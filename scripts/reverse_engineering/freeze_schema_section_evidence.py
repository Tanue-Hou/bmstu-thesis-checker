"""Freeze SDK-valid section observations and the next migration's baseline."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import context_evidence_valid


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    schema_root = ROOT / 'evidence/complex-section-schema-r1'
    native_root = ROOT / 'evidence/complex-section-r3-schema'
    destination = schema_root / 'freeze.json'
    schema = json.loads((schema_root / 'r3-validated-build.json').read_bytes())
    native = json.loads((native_root / 'native-receipt.json').read_bytes())
    assert schema['input_count'] == schema['valid_input_count']
    assert native['status'] == 'passed_native_complex_section_observations'
    assert len(native['cases']) == native['native_runs'] == 2 * schema['input_count']
    baseline_path = ROOT.parent / 'private_trials/complex-section-profile-migration-r1/before-receipt.json'
    baseline = json.loads(baseline_path.read_bytes())
    assert sha(baseline_path.parent / 'before.jsonl') == baseline['result_sha256']
    registry = ROOT / 'scripts/testvkr-service/rules/rules_verified.json'
    data = json.loads(registry.read_bytes())
    contexts = [c for r in data['rules'] for c in r.get('verification_by_build', {}).get('232', {}).values()]
    assert all(context_evidence_valid(c) for c in contexts)
    names = ['scripts/reverse_engineering/ValidateSyntheticDocx.cs',
             'scripts/reverse_engineering/prepare_openxml_validator.py',
             'scripts/reverse_engineering/validate_synthetic_docx.py',
             'scripts/reverse_engineering/generate_schema_section_probes.py',
             'scripts/reverse_engineering/verify_complex_sections.py',
             'scripts/reverse_engineering/capture_section_migration.py',
             'scripts/reverse_engineering/freeze_schema_section_evidence.py',
             'tests/test_complex_section_evidence.py', 'tests/test_complex_section_schema.py',
             'skills/bmstu-thesis-checker/SKILL.md']
    files = [ROOT / name for name in names]
    files.extend(p for base in (schema_root, native_root) for p in base.rglob('*') if p.is_file() and p != destination)
    result = {'status': 'frozen_schema_valid_native_section_observations',
              'sdk_valid_inputs': schema['valid_input_count'], 'native_runs': native['native_runs'],
              'native_positive_report_groups': sum(row['target_diagnostic_groups'] for row in native['cases']),
              'baseline_unique_input_modes': baseline['cases'], 'baseline_output_sha256': baseline['result_sha256'],
              'registry_sha256': sha(registry), 'valid_native232_contexts': len(contexts),
              'production_rule_or_repair_expansion': False,
              'repair_source_sha256': sha(ROOT / 'scripts/repair_build232.py'),
              'limits': 'SDK Office2013 structure plus exact synthetic native observations. Rendering and broader production coverage remain unproven; baseline is prepared for a future non-target replay.',
              'files': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(files))}}
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}))


if __name__ == '__main__':
    main()
