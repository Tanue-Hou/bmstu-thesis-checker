"""Resolve the sole registry-schema error with an auditable targeted retry."""
import hashlib
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def statuses(path):
    text = path.read_text(encoding='utf-8')
    rows = dict(re.findall(r'^(test_\S+ \([^)]+\)) \.\.\. (ok|ERROR|FAIL)$', text, re.M))
    count = int(re.search(r'Ran (\d+) tests', text)[1])
    assert len(rows) == count, (path.name, len(rows), count)
    return rows


def main():
    base = ROOT / 'evidence/business-map-232'
    initial = base / 'regression-v0218-initial.log'
    retry = base / 'regression-v0218-schema-retry.log'
    before = statuses(initial)
    after = statuses(retry)
    failed = [name for name, status in before.items() if status != 'ok']
    assert len(failed) == 1 and failed[0].startswith('test_registry_does_not_claim_original_verification ')
    assert all(s == 'ok' for s in after.values()) and set(after) <= set(before)
    baseline = ROOT.parent / 'private_trials/2026-10-15/cross_v0218/summary.private.json'
    old = json.loads(baseline.read_text(encoding='utf-8'))
    registry = 'scripts/testvkr-service/rules/rules_verified.json'
    for name, digest in old['implementation_sha256'].items():
        if name != registry:
            assert sha(ROOT / name) == digest, name
    data = json.loads((ROOT / registry).read_text(encoding='utf-8'))
    for rule_id in ['Word.LeftIndentInvalid', 'Word.RightIndentInvalid']:
        rule = next(r for r in data['rules'] if r['rule_id'] == rule_id)
        assert rule.pop('observed_message') is None
    reconstructed = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    assert hashlib.sha256(reconstructed).hexdigest() == old['implementation_sha256'][registry]
    resolved = {**before, **after}
    assert all(value == 'ok' for value in resolved.values())
    receipt = {'unique_tests_passed': len(resolved), 'initial_tests': len(before),
               'initial_failures': failed, 'targeted_retry_tests': len(after), 'unresolved_failures': 0,
               'initial_log_sha256': sha(initial), 'targeted_retry_log_sha256': sha(retry),
               'registry_schema_only_change_proven': 'Removing exactly two observed_message:null fields reproduces the initial-run registry SHA; all captured runtime implementation hashes unchanged.',
               'current_registry_sha256': sha(ROOT / registry), 'initial_private_summary_sha256': sha(baseline),
               'tests': resolved,
               'limits': 'This is148 unique accepted tests across the full initial run and18-test targeted schema retry, not a claimed single all-green full invocation.'}
    (base / 'regression-v0218-acceptance.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: receipt[k] for k in ['unique_tests_passed', 'initial_tests', 'targeted_retry_tests', 'unresolved_failures']}))


if __name__ == '__main__':
    main()
