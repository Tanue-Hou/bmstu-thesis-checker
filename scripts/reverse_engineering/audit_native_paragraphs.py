"""Compare actual native paragraph branches, independent model and shipped checker."""
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
from predict_native_paragraphs import predict


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.absolute()
    out.mkdir(exist_ok=False)
    base = ROOT / 'evidence/business-map-232'
    folders = ['paragraph-native-r1', 'paragraph-native-r2', 'paragraph-producer-discovery-r1',
               'paragraph-branches-native-r2', 'paragraph-boundary-native-r1', 'paragraph-role-native-r1',
               'paragraph-phd-native-r1']
    rules = {'left': 'Word.LeftIndentInvalid', 'right': 'Word.RightIndentInvalid', 'line': 'Word.LineSpacingInvalid'}
    phrases = {'left': '\u041b\u0435\u0432\u044b\u0439 \u043e\u0442\u0441\u0442\u0443\u043f \u0432 \u0430\u0431\u0437\u0430\u0446\u0430\u0445',
               'right': '\u041f\u0440\u0430\u0432\u044b\u0439 \u043e\u0442\u0441\u0442\u0443\u043f \u0432 \u0430\u0431\u0437\u0430\u0446\u0430\u0445',
               'line': '\u041c\u0435\u0436\u0434\u0443\u0441\u0442\u0440\u043e\u0447\u043d\u044b\u0439 \u0438\u043d\u0442\u0435\u0440\u0432\u0430\u043b \u0432 \u0430\u0431\u0437\u0430\u0446\u0430\u0445'}
    sources = {}
    rows = []
    for folder in folders:
        matrix = base / folder / 'matrix.json'
        sources[matrix.relative_to(ROOT).as_posix()] = sha(matrix)
        for row in json.loads(matrix.read_text())['cases']:
            source = ROOT / row['input']
            directory = ROOT / row['evidence_directory']
            assert sha(source) == row['sha256']
            trace = json.loads((directory / 'trace.json').read_text())
            native = validate_native_run(trace, (directory / 'native-result.txt').read_bytes().decode('utf-8'),
                                         row['work_type'], 'docx', sha(source), True)
            hits = trace['breakpoint_hits']
            model = predict(source)
            assert model['profile_supported'], row['case']
            assert model['counters'] == {k: row['native_counters'][k] for k in rules}, (row['case'], model['counters'], row['native_counters'])
            differences = []
            legacy = check_file(source, Namespace(work_type=row['work_type'], native_build=232,
                                                  skip_structure=False, skip_pictures=False,
                                                  skip_word_format=False, skip_dictionary=False))
            found = {f['rule_id'] for f in legacy['findings']}
            for bucket, rule in rules.items():
                triggered = model['counters'][bucket] > 0
                assert triggered == any(h['label'] == 'paragraph_' + bucket + '_report_emit' for h in hits)
                assert triggered == any(phrases[bucket] in n['message'] for n in native)
                if (rule in found) != triggered:
                    differences.append({'rule_id': rule, 'shipped_checker': rule in found, 'native': triggered})
            if any(h['label'] == 'paragraph_properties' for h in hits):
                for bucket in rules:
                    producers = [h for h in hits if h['label'] == 'paragraph_' + bucket + '_add']
                    assert len(producers) == model['counters'][bucket], (row['case'], bucket)
                assert sum(h['label'] == 'paragraph_properties' for h in hits) < 128
                assert sum(h['label'] == 'paragraph_bucket_add' for h in hits) < 256
            rows.append({**row, 'independent_counters': model['counters'], 'three_families_agree': True,
                         'shipped_checker_differences': differences})
            for file in [source, *directory.iterdir()]:
                if file.is_file():
                    sources[file.relative_to(ROOT).as_posix()] = sha(file)
    implementations = ['scripts/reverse_engineering/predict_native_paragraphs.py',
                       'scripts/testvkr-service/parsers/docx_parser.py', 'scripts/testvkr-service/parsers/style_resolver.py',
                       'scripts/testvkr-service/checkers/word_format.py', 'scripts/check_document.py']
    result = {'status': 'passed_bounded_independent_paragraph_model_native_comparison',
              'cases': rows, 'sources': sources,
              'implementation_sha256': {p: sha(ROOT / p) for p in implementations},
              'native_executions': len(rows),
              'shipped_checker_family_disagreements': sum(len(r['shipped_checker_differences']) for r in rows),
              'local_only_family_instances': sum(d['shipped_checker'] and not d['native'] for r in rows for d in r['shipped_checker_differences']),
              'native_only_family_instances': sum(d['native'] and not d['shipped_checker'] for r in rows for d in r['shipped_checker_differences']),
              'production_rule_promotion': False, 'repair_permission_expanded': False,
              'limits': ['Synthetic baseline repeated; counts include repeated identical inputs and are not independent real-paper accuracy samples.',
                         'Common report gates are measured; producer comparisons measured only for newer trace matrices.',
                         'First-line checks, PDF, styles beyond Normal, tables and >60-paragraph activation remain outside this proof.',
                         'Failed paragraph-branches-native-r1 instrumentation is excluded; private raw failure retained.']}
    (out / 'audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['cases', 'sources', 'implementation_sha256', 'limits']}))


if __name__ == '__main__':
    main()
