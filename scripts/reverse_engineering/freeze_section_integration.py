"""Freeze v0.2.23 against full regression, native evidence and migration receipts."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'evidence/native-section-integration-r1'
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import context_evidence_valid
from repair_build232 import capability


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def main():
    log = (OUT / 'full-regression-r2.log').read_text(encoding='utf8')
    match = re.search(r'Ran (\d+) tests', log)
    assert match and log.rstrip().endswith('OK') and not re.search(r'^(ERROR|FAIL):', log, re.M)
    executed_test = (OUT / 'test_native_section_model.r2.py.txt').read_bytes().replace(b'\r\n', b'\n')
    assert executed_test == (ROOT / 'tests/test_native_section_model.py').read_bytes().replace(b'\r\n', b'\n')
    migration = read(OUT / 'migration-receipt.json')
    assert migration['unique_input_mode_pairs'] == 317 and migration['non_target_changed_cases'] == 0
    assert migration['before_output_sha256'] == migration['after_output_sha256']
    for name, digest in migration['implementations'].items():
        assert sha(ROOT / name) == digest, name
    original = read(OUT / 'audit.json')
    assert len(original['cases']) == 16 and all(c['matched'] for c in original['cases'])
    for name, digest in {**original['sources'], **original['implementations']}.items():
        assert sha(ROOT / name) == digest, name
    extra = read(OUT / 'aggregation-domain-controls/receipt.json')
    assert len(extra['cases']) == 4 and extra['seed_unchanged']
    for case in extra['cases']:
        assert case['increments_observed'] == 2 and case['native_diagnostic_groups'] == 1
        assert case['local_diagnostic_groups'] == 1 and case['local_attribute_locations'] == 2
        for name, digest in case['artifact_sha256'].items():
            assert sha(ROOT / name) == digest, name
    numeric = read(OUT / 'numeric-recompute.json')
    assert numeric['integer_values'] == 1441 and numeric['native_executions_in_this_audit'] == 0
    private = read(OUT / 'private-case-summary.json')
    assert private['cases'] == private['source_unchanged_cases'] == private['non_target_equal_cases'] == 17 and private['errors'] == 0
    smoke = read(OUT / 'mcp-cli-receipt.json')
    assert smoke['mcp_version'] == '0.2.23' and smoke['mcp_cases'] == 21 and smoke['cli_cases'] == 1
    closure = read(OUT / 'closure-receipt.json')
    assert closure['retained_native_input_cases'] == 12 and closure['previous_differences'] == 7 and closure['current_differences'] == 0
    registry = read(ROOT / 'scripts/testvkr-service/rules/rules_verified.json')
    contexts = [c for rule in registry['rules'] for c in rule.get('verification_by_build', {}).get('232', {}).values()]
    assert len(contexts) == 25 and all(context_evidence_valid(c) for c in contexts)
    repair = ROOT / 'scripts/repair_build232.py'
    assert repair.read_bytes() == subprocess.check_output(['git', 'show', 'v0.2.22:scripts/repair_build232.py'], cwd=ROOT)
    assert capability()['enabled'] and capability()['actions'] == ['font_size_anomalies']
    assert 'Skill is valid!' in (OUT / 'skill-validation.log').read_text(encoding='utf8')
    names = set()
    for args in [['diff', 'HEAD', '--name-only', '-z'], ['ls-files', '--others', '--exclude-standard', '-z']]:
        names.update(p for p in subprocess.check_output(['git', *args], cwd=ROOT).decode('utf8').split('\0') if p)
    target = 'evidence/native-section-integration-r1/release-freeze.json'
    names.discard(target)
    assert not any(p.startswith('private_trials/') or p.lower().endswith(('.exe', '.asm')) for p in names)
    receipt = {'version': '0.2.23', 'status': 'passed_native_section_integration_release',
               'full_regression_tests': int(match[1]), 'existing_contexts_preserved': len(contexts) - 2,
               'new_section_contexts': 2, 'valid_contexts': len(contexts),
               'retained_native_branch_executions': len(original['cases']),
               'fresh_native_executions': len(extra['cases']),
               'non_target_golden_replays': migration['unique_input_mode_pairs'], 'non_target_changed_cases': 0,
               'private_cases': private['cases'], 'mcp_cases': smoke['mcp_cases'], 'cli_cases': smoke['cli_cases'],
               'boundary_differences_before': closure['previous_differences'], 'boundary_differences_after': closure['current_differences'],
               'repair_sha256': sha(repair), 'repair_permission_expanded': False,
               'changed_file_sha256': {name: sha(ROOT / name) for name in sorted(names)},
               'limits': 'Single explicit ordinary A4 DOCX section master/NKR only. Four fresh native runs,16 retained branches, local317goldens and17real rechecks have distinct scopes. No full clone, school accuracy or complex-document/repair certification.'}
    (ROOT / target).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({'status': receipt['status'], 'tests': int(match[1]), 'contexts': len(contexts), 'files': len(names)}))


if __name__ == '__main__':
    main()
