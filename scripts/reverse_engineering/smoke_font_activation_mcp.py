"""Smoke the run-time native font activation cases through the real MCP stdio server."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT = ROOT / 'evidence/business-map-232/font-activation-audit-r3/audit.json'
RULE = 'Word.FontSizeTooSmall'
WANTED = {
    (mode, case)
    for mode in ('master', 'phd')
    for case in ('beforeSmall', 'fallback60Small', 'fallback61Small',
                 'exactSmallMarker', 'prefixSmallMarker', 'fallback59Table',
                 'fallback59Textbox')
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root, path):
    path = path.resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f'Output path must stay inside the project: {path}') from exc
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--audit', type=Path, default=DEFAULT_AUDIT)
    parser.add_argument('--expected-server-version', default='0.2.19')
    parser.add_argument('--timeout', type=int, default=240)
    args = parser.parse_args()

    out = inside(ROOT, args.out)
    out.mkdir(parents=True, exist_ok=False)
    private = inside(ROOT.parent, ROOT.parent / 'private_trials' / out.name)
    private.mkdir(parents=True, exist_ok=False)
    audit_path = args.audit.resolve()
    audit_path.relative_to(ROOT.resolve())
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    assert isinstance(audit.get('cases'), list), 'audit must contain a cases array'

    by_key = {}
    for row in audit['cases']:
        key = (row.get('work_type'), row.get('case'))
        if key not in WANTED:
            continue
        if key in by_key:
            previous = by_key[key]
            assert row['sha256'] == previous['sha256'], f'conflicting source hash for {key}'
            assert row['font_state'] == previous['font_state'], f'conflicting native counter for {key}'
            continue
        by_key[key] = row
    missing = sorted(WANTED - set(by_key))
    assert not missing, f'missing required native font cases: {missing}'
    cases = [by_key[key] for key in sorted(WANTED)]

    requests = [{
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05', 'capabilities': {},
            'clientInfo': {'name': 'font-activation-smoke', 'version': '1'},
        },
    }]
    for request_id, row in enumerate(cases, 2):
        requests.append({
            'jsonrpc': '2.0', 'id': request_id, 'method': 'tools/call',
            'params': {
                'name': 'check_thesis_document',
                'arguments': {
                    'file_path': str((ROOT / row['input']).resolve()),
                    'native_build': 232,
                    'work_type': row['work_type'],
                },
            },
        })

    run = subprocess.run(
        [sys.executable, str(ROOT / 'mcp/server.py')],
        input=''.join(json.dumps(request, ensure_ascii=False) + '\n' for request in requests),
        text=True, encoding='utf-8', capture_output=True, timeout=args.timeout,
    )
    raw = private / 'responses.jsonl'
    raw.write_text(run.stdout, encoding='utf-8', newline='\n')
    assert run.returncode == 0, run.stderr
    responses = [json.loads(line) for line in run.stdout.splitlines() if line.strip()]
    assert len(responses) == len(requests), (len(responses), len(requests), run.stderr)
    version = responses[0]['result']['serverInfo']['version']
    assert version == args.expected_server_version, version

    receipts = []
    for response, row in zip(responses[1:], cases):
        source = inside(ROOT, ROOT / row['input'])
        assert source.is_file(), source
        source_sha = sha(source)
        assert source_sha == row['sha256'], (row['case'], row['work_type'], source_sha, row['sha256'])

        result = response['result']['structuredContent']
        assert result['source_sha256'] == source_sha, (row['case'], result.get('source_sha256'))
        observations = result['native_word_observations']
        assert observations.get('profile_supported') is True, (row['case'], row['work_type'], observations)
        counters = observations.get('font_counters') or {}
        expected = row['font_state']
        assert counters.get('small') == expected['small_count'], (row['case'], row['work_type'], counters, expected)
        assert counters.get('tiny') == expected['tiny_count'], (row['case'], row['work_type'], counters, expected)
        assert counters.get('large') == expected['large_count'], (row['case'], row['work_type'], counters, expected)

        findings = {finding['rule_id']: finding for finding in result.get('findings', [])}
        positive = expected['small_count'] > 10
        finding = findings.get(RULE)
        assert (finding is not None) == positive, (row['case'], row['work_type'], expected, finding)
        occurrences = []
        if positive:
            assert finding['verification_status'] == 'verified_against_original', (row['case'], finding)
            scope = finding.get('verification_scope') or {}
            assert scope.get('build') == 232 and scope.get('work_type') == row['work_type'], (row['case'], scope)
            precise = finding.get('precise_locations') or {}
            occurrences = precise.get('occurrences') or []
            assert precise.get('precision') == 'source_coordinate', (row['case'], precise)
            assert occurrences and not precise.get('truncated', False), (row['case'], precise)
            assert sum(item.get('utf16_units', 0) for item in occurrences) == expected['small_count'], (row['case'], occurrences)
            for item in occurrences:
                assert item.get('kind') in {'docx_run', 'docx_table_run', 'docx_textbox_run'}, (row['case'], item)
                xml_path = item.get('xml_path')
                run_xml_path = item.get('run_xml_path')
                assert isinstance(xml_path, str) and xml_path.startswith('/w:document/w:body/'), (row['case'], item)
                assert isinstance(run_xml_path, str) and run_xml_path.startswith(xml_path + '/w:r'), (row['case'], item)
                assert item.get('native_font_enabled') is True, (row['case'], item)
                assert isinstance(item.get('native_activation_ordinal'), int), (row['case'], item)

        capture = inside(ROOT, ROOT / row['evidence_directory'])
        assert capture.is_dir() and (capture / 'trace.json').is_file(), (row['case'], capture)
        receipts.append({
            'case': row['case'], 'work_type': row['work_type'], 'input': row['input'],
            'source_sha256': source_sha, 'native_capture': row['evidence_directory'],
            'native_small_count': expected['small_count'], 'mcp_small_count': counters['small'],
            'small_finding_present': finding is not None,
            'verified_precise_xml_occurrences': len(occurrences),
            'positive_occurrences_have_activation_fields': bool(positive),
        })

    receipt = {
        'status': 'passed_actual_mcp_font_activation_smoke',
        'server_version': version,
        'audit_path': audit_path.relative_to(ROOT).as_posix(),
        'cases': receipts,
        'native_captures': [row['evidence_directory'] for row in cases],
        'raw_response_sha256': sha(raw),
        'private_raw_response': raw.relative_to(ROOT.parent).as_posix(),
        'limits': 'Actual MCP stdio transport for the small-font family and its activation boundary only; positives require native-build-232 verification scope, exact XML run locations, UTF-16 count agreement, and enabled/activation fields. Native captures were retained by source hash and were not rerun by this smoke script.',
    }
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n',
                                      encoding='utf-8', newline='\n')
    print(json.dumps({'status': receipt['status'], 'server_version': version,
                      'cases': len(receipts), 'raw_response_sha256': receipt['raw_response_sha256']}))


if __name__ == '__main__':
    main()
