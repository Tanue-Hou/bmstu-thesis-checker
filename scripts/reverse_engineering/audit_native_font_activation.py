"""Audit run-time font activation, preserving prior font and role evidence."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from argparse import Namespace
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import check_file, parse_document
from native_reference_cli import validate_native_run


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.absolute()
    out.mkdir(exist_ok=False)
    base = ROOT / 'evidence/business-map-232'
    old = json.loads((base / 'font-audit-r1/audit.json').read_text())
    sources = dict(old['sources'])
    cases = list(old['cases'])
    for name, digest in sources.items():
        assert sha(ROOT / name) == digest, name
    for folder in ['font-activation-native-r1', 'font-activation-native-r2', 'font-activation-native-r3',
                   'font-activation-native-r4', 'font-activation-boundary-native-r1', 'font-activation-phd-native-r1', 'linked-font-native-r1']:
        matrix = base / folder / 'matrix.json'
        sources[matrix.relative_to(ROOT).as_posix()] = sha(matrix)
        cases += json.loads(matrix.read_text())['cases']
    rows = []
    for row in cases:
        source = ROOT / row['input']
        directory = ROOT / row['evidence_directory']
        assert sha(source) == row['sha256']
        trace = json.loads((directory / 'trace.json').read_text())
        native = validate_native_run(trace, (directory / 'native-result.txt').read_bytes().decode('utf-8'),
                                    row['work_type'], 'docx', row['sha256'], True)
        report = check_file(source, Namespace(work_type=row['work_type'], native_build=232,
                                             skip_structure=False, skip_pictures=False, skip_word_format=False, skip_dictionary=False))
        obs = report['native_word_observations']
        assert obs['profile_supported'], row['case']
        hits = trace['breakpoint_hits']
        counts = obs['font_counters']
        found = {f['rule_id']: f for f in report['findings']}
        for bucket in ['small', 'tiny', 'large']:
            assert counts[bucket] == row['font_state'][bucket + '_count'], (row['case'], bucket, counts, row['font_state'])
            assert sum(h['font_state']['text']['length'] for h in hits if h['label'] == 'font_' + bucket + '_add') == counts[bucket]
        for bucket, rule, phrase in [('small','Word.FontSizeTooSmall','размер которых меньше 8'),
                                     ('large','Word.FontSizeTooLarge','размер которых превышает 18')]:
            triggered = counts[bucket] > 10
            assert (rule in found) == triggered == any(phrase in n['message'] for n in native)
            assert triggered == any(h['label'] == 'font_' + bucket + '_report_emit' for h in hits)
            if triggered:
                occurrences = found[rule]['precise_locations']['occurrences']
                assert sum(l['utf16_units'] for l in occurrences) == counts[bucket]
                assert all(l['native_font_enabled'] is True for l in occurrences)
        _, data = parse_document(source)
        from checkers.native_font_counts import count_font_candidates
        _, records = count_font_candidates(data)
        run_hits = [h['font_state'] for h in hits if h['label'] == 'font_run_state']
        capped = len(run_hits) == 256
        if not capped:
            actual = Counter((h['size_half_points'], h['text']['length'], h['text']['prefix'], bool(h['enabled_flag']), h['textbox_gate_f0'] != 0)
                             for h in run_hits if h['text']['length'] and 0 < h['size_half_points'] and (h['size_half_points'] < 16 or h['size_half_points'] > 36))
            expected = Counter((int(r['font_size_pt'] * 2), r['utf16_units'], r['text'].encode('utf-16le')[:512].decode('utf-16le', errors='replace'), r['native_font_enabled'], r['role']=='textbox')
                               for r in records if r['text'] and r['font_size_pt'] is not None and r['font_size_pt'] > 0 and (r['font_size_pt'] < 8 or r['font_size_pt'] > 18))
            assert actual == expected, (row['case'], actual, expected)
        rows.append({**row, 'local_font_counters': counts, 'both_font_families_agree': True,
                     'font_run_sampling_capped': capped, 'anomalous_run_activation_multiset_checked': not capped})
        for path in [source, *directory.iterdir()]:
            if path.is_file():
                sources[path.relative_to(ROOT).as_posix()] = sha(path)
    result = {'status':'passed_native232_font_activation_and_prior_counter_audit', 'cases':rows,
              'native_executions':len(rows), 'unique_input_hashes':len({r['sha256'] for r in rows}),
              'native_modes':{mode:sum(r['work_type']==mode for r in rows) for mode in ['master','phd']},
              'sources':sources, 'repair_permission_expanded':False,
              'limits':['Repeated synthetic inputs are not independent real-paper accuracy evidence.',
                        'Run classifier precedes paragraph activation; table/textbox end boundaries count in the native list.',
                        'Ordinary run-state sampling stops at256; late producer adds and final counters are still directly observed.',
                        'General mixed table/textbox, visible textbox host text, fields/math/extra stories and PDF remain unverified.']}
    (out / 'audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:result[k] for k in ['status','native_executions','unique_input_hashes','native_modes']}))


if __name__ == '__main__':
    main()
