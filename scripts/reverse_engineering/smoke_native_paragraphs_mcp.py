"""Smoke native-verified paragraph diagnostics through the actual MCP server."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT = ROOT / 'evidence/business-map-232/paragraph-acceptance-r1/audit.json'
RULES = {
    'left': 'Word.LeftIndentInvalid',
    'right': 'Word.RightIndentInvalid',
    'line': 'Word.LineSpacingInvalid',
}
WANTED = {
    ('master', 'line179'),
    ('master', 'control'),
    ('master', 'leftNegative6'),
    ('master', 'fallback60'),
    ('master', 'inheritedBoth'),
    ('master', 'tableBoth'),
    ('phd', 'line180'),
    ('phd', 'rightNegative6'),
    ('phd', 'fallback60'),
    ('phd', 'tableBoth'),
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


def iter_xml_paths(value):
    """Collect explicit XML path fields from native paragraph records."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {'xml_path', 'source_xml_path'} and isinstance(item, str) and item:
                yield item
            else:
                yield from iter_xml_paths(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_xml_paths(item)


def verify_finding(finding, rule_id, row, record_paths):
    assert finding['rule_id'] == rule_id
    assert finding['verification_status'] == 'verified_against_original', (row['case'], rule_id)
    scope = finding.get('verification_scope') or {}
    assert scope.get('build') == 232, (row['case'], rule_id, scope)
    assert scope.get('work_type') == row['work_type'], (row['case'], rule_id, scope)

    precise = finding.get('precise_locations') or {}
    occurrences = precise.get('occurrences') or []
    assert precise.get('precision') == 'source_coordinate', (row['case'], rule_id, precise)
    assert occurrences and not precise.get('truncated', False), (row['case'], rule_id, precise)
    for occurrence in occurrences:
        assert occurrence.get('kind') == 'docx_paragraph', (row['case'], rule_id, occurrence)
        assert occurrence.get('part') == 'word/document.xml', (row['case'], rule_id, occurrence)
        xml_path = occurrence.get('xml_path')
        assert isinstance(xml_path, str) and xml_path, (row['case'], rule_id, occurrence)
        assert xml_path in record_paths, (row['case'], rule_id, xml_path)
    return occurrences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--audit', type=Path, default=DEFAULT_AUDIT)
    parser.add_argument('--expected-server-version', default='0.2.18')
    parser.add_argument('--timeout', type=int, default=180)
    args = parser.parse_args()

    out = inside(ROOT, args.out)
    out.mkdir(parents=True, exist_ok=False)
    private = inside(ROOT.parent, ROOT.parent / 'private_trials' / out.name)
    private.mkdir(parents=True, exist_ok=False)
    audit_path = args.audit.resolve()
    audit_path.relative_to(ROOT.resolve())
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    all_cases = audit.get('cases')
    assert isinstance(all_cases, list), 'audit.json must contain a cases array'

    by_key = {}
    for row in all_cases:
        key = (row.get('work_type'), row.get('case'))
        if key in WANTED:
            if key in by_key:
                assert row['sha256'] == by_key[key]['sha256'] and row['native_counters'] == by_key[key]['native_counters'], f'conflicting repeated case: {key}'
                continue
            by_key[key] = row
    missing = sorted(WANTED - set(by_key))
    assert not missing, f'missing required native paragraph cases: {missing}'
    cases = [by_key[key] for key in sorted(WANTED)]

    requests = [{
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05', 'capabilities': {},
            'clientInfo': {'name': 'paragraph-acceptance-smoke', 'version': '1'},
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
        source = (ROOT / row['input']).resolve()
        assert source.is_file(), source
        source_sha = sha(source)
        assert source_sha == row['sha256'], (row['case'], source_sha, row['sha256'])

        native_counters = row['native_counters']
        assert all(bucket in native_counters for bucket in RULES), (row['case'], native_counters)
        result = response['result']['structuredContent']
        assert result['source_sha256'] == source_sha, (row['case'], result.get('source_sha256'))
        observations = result['native_paragraph_observations']
        assert observations['profile_supported'] is True, (row['case'], observations)
        counters = observations['counters']
        assert {bucket: counters[bucket] for bucket in RULES} == {
            bucket: native_counters[bucket] for bucket in RULES
        }, (row['case'], counters, native_counters)

        records = observations.get('native_paragraph_records')
        assert isinstance(records, (list, dict)), (row['case'], 'missing native_paragraph_records')
        record_paths = set(iter_xml_paths(records))
        if any(counters.values()):assert record_paths, (row['case'], 'native_paragraph_records have no XML paths')
        findings = {finding['rule_id']: finding for finding in result.get('findings', [])
                    if finding.get('rule_id') in RULES.values()}

        family_receipts = {}
        for bucket, rule_id in RULES.items():
            count = counters[bucket]
            finding = findings.get(rule_id)
            assert (finding is not None) == (count > 0), (row['case'], bucket, count, finding)
            occurrences = []
            if count > 0:
                occurrences = verify_finding(finding, rule_id, row, record_paths)
            family_receipts[bucket] = {
                'native_counter': count,
                'finding_present': finding is not None,
                'verified_positive': count > 0,
                'xml_occurrences': len(occurrences),
            }

        capture = (ROOT / row['evidence_directory']).resolve()
        assert capture.is_dir(), (row['case'], capture)
        assert (capture / 'trace.json').is_file(), (row['case'], 'missing native trace')
        receipts.append({
            'case': row['case'], 'work_type': row['work_type'],
            'input': row['input'], 'source_sha256': source_sha,
            'native_capture': row['evidence_directory'],
            'paragraph_counters_and_verified_xml_findings': family_receipts,
            'three_families_match_native_capture': True,
        })

    receipt = {
        'status': 'passed_actual_mcp_native_paragraph_smoke',
        'server_version': version,
        'audit_path': audit_path.relative_to(ROOT).as_posix(),
        'cases': receipts,
        'native_captures': [row['evidence_directory'] for row in cases],
        'raw_response_sha256': sha(raw),
        'private_raw_response': str(raw.relative_to(ROOT.parent).as_posix()),
        'limits': 'Actual MCP transport for left/right/line only; positive findings required native-build-232 verification scope and exact word/document.xml paragraph locations. Native executions were retained by source hash and were not rerun by this smoke script.',
    }
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n',
                                      encoding='utf-8', newline='\n')
    print(json.dumps({'status': receipt['status'], 'server_version': version,
                      'cases': len(receipts), 'raw_response_sha256': receipt['raw_response_sha256']}))


if __name__ == '__main__':
    main()
