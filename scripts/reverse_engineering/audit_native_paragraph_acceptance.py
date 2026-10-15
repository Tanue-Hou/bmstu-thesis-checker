"""Accept the integrated three-bucket engine against retained native executions."""
import argparse
import hashlib
import json
import sys
from argparse import Namespace
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import check_file
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
    old = json.loads((base / 'paragraph-audit-r1/audit.json').read_text())
    sources = dict(old['sources'])
    for path, digest in sources.items():
        assert sha(ROOT / path) == digest, path
    cases = list(old['cases'])
    for folder in ['paragraph-state-native-r1', 'paragraph-long-native-r1', 'paragraph-state-phd-native-r1']:
        matrix = base / folder / 'matrix.json'
        sources[matrix.relative_to(ROOT).as_posix()] = sha(matrix)
        cases += json.loads(matrix.read_text())['cases']
    rules = {'left': 'Word.LeftIndentInvalid', 'right': 'Word.RightIndentInvalid', 'line': 'Word.LineSpacingInvalid'}
    rows = []
    for row in cases:
        source = ROOT / row['input']
        directory = ROOT / row['evidence_directory']
        assert sha(source) == row['sha256']
        trace = json.loads((directory / 'trace.json').read_text())
        validate_native_run(trace, (directory / 'native-result.txt').read_bytes().decode('utf-8'),
                            row['work_type'], 'docx', row['sha256'], True)
        result = check_file(source, Namespace(work_type=row['work_type'], native_build=232, skip_structure=False,
                                             skip_pictures=False, skip_word_format=False, skip_dictionary=False))
        obs = result['native_paragraph_observations']
        assert obs['profile_supported'], row['case']
        assert obs['counters'] == {k: row['native_counters'][k] for k in rules}, row['case']
        found = {f['rule_id']: f for f in result['findings']}
        for bucket, rule in rules.items():
            assert (rule in found) == (row['native_counters'][bucket] > 0), (row['case'], rule)
            if rule in found:
                locations = found[rule]['precise_locations']
                expected = {p['xml_path'] for p in obs['native_paragraph_records'] if p['matches'][bucket]}
                assert {p['xml_path'] for p in locations['occurrences']} == expected
                assert not locations['truncated'] and locations['occurrence_count'] == row['native_counters'][bucket]
                assert found[rule]['threshold']['native_predicate_supported']
        hits = trace['breakpoint_hits']
        for bucket in rules:
            adds = [h for h in hits if h['label'] == 'paragraph_' + bucket + '_add']
            if any(h['label'] == 'paragraph_properties' for h in hits):
                assert len(adds) == row['native_counters'][bucket]
        phase = [h['paragraph_property_state'] for h in hits if h['label'] == 'paragraph_activation_count']
        if row['case'].startswith('fallback') or row['case'] == 'blankFallback60':
            assert phase and max(p['native_paragraph_count'] for p in phase) == min(row['filler_paragraphs'] + 1, 61)
        rows.append({**row, 'integrated_counters': obs['counters'], 'three_families_agree': True,
                     'producer_adds_checked': any(h['label'] == 'paragraph_properties' for h in hits),
                     'ordinary_property_trace_capped': sum(h['label'] == 'paragraph_properties' for h in hits) == 128,
                     'long_probe_note': 'Late anomalous add branches and final counters remain directly observed even when ordinary-property sampling stops.'})
        for file in [source, *directory.iterdir()]:
            if file.is_file():
                sources[file.relative_to(ROOT).as_posix()] = sha(file)
    assert len(rows) == 68
    result = {'status': 'passed_integrated_native232_paragraph_counters_activation_inheritance_and_table_audit',
              'native_executions': len(rows), 'unique_input_hashes': len({r['sha256'] for r in rows}),
              'native_modes': {mode: sum(r['work_type'] == mode for r in rows) for mode in ['master', 'phd']},
              'cases': rows, 'sources': sources, 'repair_permission_expanded': False,
              'limits': ['Synthetic inputs and repeated baselines, not real-paper accuracy or school-compliance evidence.',
                         'Plain-list fallback tested through1001 paragraphs; inherited/direct properties and one single-cell table tested.',
                         'General tables, fields, formulas, textboxes, numbering styles, pre-activation table state and PDF remain unverified.',
                         'First-line-indent producer remains unresolved; this audit covers only three buckets.']}
    (out / 'audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: result[k] for k in ['status', 'native_executions', 'unique_input_hashes', 'native_modes']}))


if __name__ == '__main__':
    main()
