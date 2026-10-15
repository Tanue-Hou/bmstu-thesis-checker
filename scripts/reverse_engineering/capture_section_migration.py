"""Lock non-target finding behavior on every referenced build232 DOCX input/mode."""
import argparse
from argparse import Namespace
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT.parent / 'private_trials/section-migration-r1'
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import check_file

TARGET = 'Word.HeaderFooterDistanceInvalid'
FIELDS = ['rule_id', 'severity', 'message', 'confidence', 'verification_status',
          'verification_evidence_intact', 'verification_scope', 'threshold_origin',
          'threshold', 'location', 'precise_locations', 'action_eligibility']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signature(report):
    return [{k: f.get(k) for k in FIELDS} for f in report['findings'] if f['rule_id'] != TARGET]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('phase', choices=['before', 'after'])
    a = p.parse_args()
    PRIVATE.mkdir(parents=True, exist_ok=True)
    baseline = PRIVATE / 'before.jsonl'
    if a.phase == 'before':
        data = json.loads((ROOT / 'scripts/testvkr-service/rules/rules_verified.json').read_bytes())
        pairs = set()
        for rule in data['rules']:
            for context in rule.get('verification_by_build', {}).get('232', {}).values():
                for ref in context['evidence_refs']:
                    if ref.endswith('.docx'):
                        pairs.add((ref, context['scope']['work_type']))
        # Preserve one representative per byte-identical input/mode.
        selected = {}
        for ref, mode in sorted(pairs):
            selected.setdefault((sha(ROOT / ref), mode), ref)
        rows = [{'input_sha256': digest, 'work_type': mode, 'input': ref}
                for (digest, mode), ref in selected.items()]
    else:
        rows = [json.loads(line) for line in baseline.read_text(encoding='utf8').splitlines()]
    destination = PRIVATE / (a.phase + '.jsonl')
    if destination.exists():
        raise ValueError('Do not overwrite an existing migration run')
    changes = []
    with destination.open('x', encoding='utf8') as stream:
        for index, row in enumerate(rows):
            path = ROOT / row['input']
            assert sha(path) == row['input_sha256']
            options = Namespace(work_type=row['work_type'], native_build=232, template_id=None,
                                document_kind='auto', skip_structure=False, skip_pictures=False,
                                skip_word_format=False, skip_dictionary=False)
            report = check_file(path, options)
            current = signature(report)
            if a.phase == 'after' and current != row['signature']:
                changes.append({'input': row['input'], 'work_type': row['work_type']})
            record = {**row, 'signature': current,
                      'target': [f for f in report['findings'] if f['rule_id'] == TARGET]}
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
            stream.flush()
            if (index + 1) % 25 == 0:
                print(a.phase, index + 1, '/', len(rows), flush=True)
    receipt = {'phase': a.phase, 'cases': len(rows), 'non_target_changed_cases': len(changes),
               'changed_cases': changes, 'result_sha256': sha(destination),
               'limits': 'Byte-identical input/mode deduplication; non-target finding semantics, evidence integrity and locations compared. Not a fresh native execution or school accuracy estimate.'}
    (PRIVATE / (a.phase + '-receipt.json')).write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt), flush=True)
    if changes:
        raise AssertionError('Unexpected non-target finding changes')


if __name__ == '__main__':
    main()
