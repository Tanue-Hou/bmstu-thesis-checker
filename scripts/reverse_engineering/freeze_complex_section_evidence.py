"""Compute an auditable inventory for the bounded complex-section observation batch."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    batches = ['complex-section-r1', 'complex-section-r2-final']
    rows = []
    files = []
    destination = ROOT / 'evidence/complex-section-r1/freeze.json'
    for name in batches:
        base = ROOT / 'evidence' / name
        manifest = json.loads((base / 'manifest.json').read_bytes())
        receipt = json.loads((base / 'native-receipt.json').read_bytes())
        assert receipt['status'] == 'passed_native_complex_section_observations'
        assert len(receipt['cases']) == receipt['native_runs'] == 2 * len(manifest['cases'])
        assert sha(ROOT / manifest['generator']['path_from_implementation']) == manifest['generator']['sha256']
        rows.append({'batch': name, 'inputs': len(manifest['cases']),
                     'native_runs': receipt['native_runs'], 'status': receipt['status']})
        files.extend(p for p in base.rglob('*') if p.is_file() and p != destination)
    for path in ['scripts/native_reference_cli.py', 'scripts/reverse_engineering/trace_startup_windows.py',
                 'scripts/reverse_engineering/verify_complex_sections.py',
                 'scripts/reverse_engineering/freeze_complex_section_evidence.py',
                 'scripts/reverse_engineering/generate_complex_section_probes.py',
                 'scripts/reverse_engineering/generate_complex_section_probes_r2.py',
                 'tests/test_complex_section_evidence.py', '.gitattributes']:
        files.append(ROOT / path)
    reviews = [json.loads((ROOT / 'evidence/complex-section-r1' / name / 'receipt.json').read_bytes())
               for name in ['antigravity-input-review', 'antigravity-predicate-review']]
    result = {'status': 'frozen_bounded_observations', 'campaigns': rows,
              'native_runs': sum(row['native_runs'] for row in rows),
              'antigravity_attempts': len(reviews),
              'antigravity_successful_reviews': sum(row.get('exit_code') == 0 for row in reviews),
              'production_rule_or_repair_expansion': False,
              'limits': 'Retained synthetic bytes and native counter/report observations only. Full chart schema/rendering remains unvalidated. External reviewers returned no valid opinion.',
              'files': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(files))}}
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
