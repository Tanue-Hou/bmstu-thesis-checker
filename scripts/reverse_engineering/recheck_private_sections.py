"""Recheck the existing private17 cases without publishing text or identities."""
from argparse import Namespace
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import check_file
from reverse_engineering.capture_section_migration import signature


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    baseline = ROOT.parent / 'private_trials/2026-10-15/cross_v0220_final/cases'
    out = ROOT.parent / 'private_trials/2026-10-16/cross_v0223_final'
    out.mkdir(parents=True, exist_ok=False)
    files = sorted(baseline.glob('*.local.json'))
    assert len(files) == 17
    rows = []
    for previous in files:
        old = json.loads(previous.read_bytes())
        path = Path(old['file'])
        row = {'case': previous.stem, 'baseline_sha256': sha(previous)}
        try:
            digest = sha(path)
            assert digest == old['source_sha256']
            options = Namespace(work_type=old['work_type'], native_build=232,
                                document_kind=old['document_kind'], template_id=(old.get('template') or {}).get('id'),
                                skip_structure=False, skip_pictures=False, skip_word_format=False, skip_dictionary=False)
            report = check_file(path, options)
            (out / previous.name).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
            assert sha(path) == digest
            row.update(status='checked', source_unchanged=True,
                       non_target_equal=signature(old) == signature(report),
                       target_before=sum(f['rule_id'] == 'Word.HeaderFooterDistanceInvalid' for f in old['findings']),
                       target_after=sum(f['rule_id'] == 'Word.HeaderFooterDistanceInvalid' for f in report['findings']))
        except Exception as exc:
            row.update(status='error', error=str(exc))
        rows.append(row)
    (out / 'cases.private.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf8')
    summary = {'status': 'private_case_recheck', 'cases': len(rows),
               'errors': sum(r['status'] != 'checked' for r in rows),
               'source_unchanged_cases': sum(r.get('source_unchanged', False) for r in rows),
               'non_target_equal_cases': sum(r.get('non_target_equal', False) for r in rows),
               'target_groups_before': sum(r.get('target_before', 0) for r in rows),
               'target_groups_after': sum(r.get('target_after', 0) for r in rows),
               'private_receipt_sha256': sha(out / 'cases.private.json'),
               'limits': 'Local recheck of previously supplied cases, no fresh native runs. Originals untouched. Not school ground truth, accuracy, or broad profile verification.'}
    (ROOT / 'evidence/native-section-integration-r1/private-case-summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf8')
    print(json.dumps(summary))
    assert summary['errors'] == 0 and summary['source_unchanged_cases'] == 17


if __name__ == '__main__':
    main()
