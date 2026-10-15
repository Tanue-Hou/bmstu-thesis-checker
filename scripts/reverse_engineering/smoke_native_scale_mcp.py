"""Smoke native232 scale counters and exact run locations through MCP stdio."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT = ROOT / 'evidence/business-map-232/scale-audit-r1/audit.json'
RULES = {
    'small': 'Word.FontScaleTooSmall',
    'large': 'Word.FontScaleTooLarge',
}
WANTED = {
    (mode, case)
    for mode in ('master', 'phd')
    for case in (
        'small69_10', 'small69_11', 'tiny30_11', 'small70_11',
        'large130_11', 'large131_11', 'textboxLarge', 'linkedDirect100',
        'emojiSmall', 'linkedLarge',
    )
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(root, path):
    path = path.resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f'Path must stay inside {root}: {path}') from exc
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True,
                        help='Fresh output directory, relative to the implementation root or absolute within it.')
    parser.add_argument('--audit', type=Path, default=DEFAULT_AUDIT)
    parser.add_argument('--expected-server-version', default='0.2.20')
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()

    out = inside(ROOT, ROOT / args.out if not args.out.is_absolute() else args.out)
    out.mkdir(parents=True, exist_ok=False)
    private = inside(ROOT.parent, ROOT.parent / 'private_trials' / out.name)
    private.mkdir(parents=True, exist_ok=False)

    audit_path = inside(ROOT, args.audit if args.audit.is_absolute() else ROOT / args.audit)
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    assert audit.get('status') == 'passed_native232_scale_branch_counter_report_and_run_audit'
    assert audit.get('native_executions') == 52
    assert isinstance(audit.get('cases'), list), 'audit must contain a cases array'

    by_key = {}
    for row in audit['cases']:
        key = (row.get('work_type'), row.get('case'))
        if key not in WANTED:
            continue
        if key in by_key:
            prior = by_key[key]
            assert row['sha256'] == prior['sha256'], f'conflicting source hash for {key}'
            assert row['scale_state'] == prior['scale_state'], f'conflicting native scale counters for {key}'
            assert row['scale_pct'] == prior['scale_pct'], f'conflicting scale property for {key}'
            continue
        by_key[key] = row
    missing = sorted(WANTED - set(by_key))
    assert not missing, f'missing required native scale cases: {missing}'
    cases = [by_key[key] for key in sorted(WANTED)]

    requests = [{
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05', 'capabilities': {},
            'clientInfo': {'name': 'native-scale-smoke', 'version': '1'},
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
        observations = result.get('native_scale_observations') or {}
        assert observations.get('profile_supported') is True, (row['case'], row['work_type'], observations)
        counters = observations.get('counters') or {}
        expected = row['scale_state']
        for bucket in ('small', 'tiny', 'large'):
            assert counters.get(bucket) == expected[f'{bucket}_count'], (
                row['case'], row['work_type'], bucket, counters, expected)

        findings = {finding['rule_id']: finding for finding in result.get('findings', [])}
        positive_rules = []
        occurrence_counts = {}
        for bucket, rule_id in RULES.items():
            positive = expected[f'{bucket}_count'] > 10
            finding = findings.get(rule_id)
            assert (finding is not None) == positive, (row['case'], row['work_type'], bucket, expected, finding)
            occurrence_counts[rule_id] = 0
            if not positive:
                continue

            positive_rules.append(rule_id)
            assert finding['verification_status'] == 'verified_against_original', (row['case'], finding)
            assert finding.get('verification_evidence_intact') is True, (row['case'], finding)
            scope = finding.get('verification_scope') or {}
            assert scope.get('build') == 232 and scope.get('format') == 'docx' \
                and scope.get('work_type') == row['work_type'], (row['case'], scope)
            precise = finding.get('precise_locations') or {}
            occurrences = precise.get('occurrences') or []
            assert precise.get('precision') == 'source_coordinate', (row['case'], precise)
            assert occurrences and not precise.get('truncated', False), (row['case'], precise)
            assert sum(item.get('utf16_units', 0) for item in occurrences) == expected[f'{bucket}_count'], (
                row['case'], bucket, occurrences, expected)
            for item in occurrences:
                assert item.get('part') == 'word/document.xml', (row['case'], item)
                run_xml_path = item.get('run_xml_path')
                assert isinstance(run_xml_path, str) and '/w:r' in run_xml_path, (row['case'], item)
                assert item.get('actual') == row['scale_pct'], (row['case'], item, row['scale_pct'])
                assert item.get('native_font_enabled') is True, (row['case'], item)
                assert isinstance(item.get('native_activation_ordinal'), int), (row['case'], item)
            occurrence_counts[rule_id] = len(occurrences)

        capture = inside(ROOT, ROOT / row['evidence_directory'])
        assert capture.is_dir() and (capture / 'trace.json').is_file(), (row['case'], capture)
        receipts.append({
            'case': row['case'], 'work_type': row['work_type'],
            'source_sha256': source_sha, 'native_capture': row['evidence_directory'],
            'scale_pct': row['scale_pct'], 'text_utf16_units': row['text_utf16_units'],
            'native_counters': expected, 'mcp_counters': counters,
            'scale_findings_present': positive_rules,
            'verified_precise_run_occurrences': occurrence_counts,
        })

    receipt = {
        'status': 'passed_actual_mcp_native_scale_smoke',
        'server_version': version,
        'audit_path': audit_path.relative_to(ROOT).as_posix(),
        'cases': receipts,
        'native_captures': [row['evidence_directory'] for row in cases],
        'raw_response_sha256': sha(raw),
        'private_raw_response': raw.relative_to(ROOT.parent).as_posix(),
        'limits': 'Actual MCP stdio transport for the selected native232 scale cases only. Counter and positive-finding checks are bound to same-input native captures; positives require build/mode verification, exact run locations, scale actual value, UTF-16 total, and enabled/activation fields. This does not broaden the native scale profile or establish real-document accuracy.',
    }
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n',
                                      encoding='utf-8', newline='\n')
    print(json.dumps({
        'status': receipt['status'], 'server_version': version,
        'cases': len(receipts), 'raw_response_sha256': receipt['raw_response_sha256'],
    }))


if __name__ == '__main__':
    main()
