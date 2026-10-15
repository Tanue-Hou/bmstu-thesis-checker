"""Frozen synthetic branch evidence, not a school compliance claim."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from native_reference_cli import validate_native_run


class NativeSectionDistanceTests(unittest.TestCase):
    def test_actual_comparisons_and_increment_branches_for_both_modes_and_fields(self):
        directory = ROOT / 'evidence/differential-platform-r1/section-boundaries-r2'
        receipt = json.loads((directory / 'receipt.json').read_bytes())
        cases = receipt['cases']
        self.assertEqual(len(cases), 16)
        self.assertEqual({(r['work_type'], r['field'], r['twips']) for r in cases},
                         {(mode, field, value) for mode in ('master', 'phd')
                          for field in ('header', 'footer') for value in (697, 698, 720, 721)})
        for row in cases:
            with self.subTest(case=row['case']):
                for name, wanted in row['artifact_sha256'].items():
                    self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), wanted)
                trace = json.loads((directory / row['case'] / 'trace.json').read_bytes())
                text = (directory / row['case'] / 'native-result.txt').read_bytes().decode('utf8')
                diagnostics = validate_native_run(trace, text, row['work_type'], 'docx', row['input_sha256'], True)
                expected = row['twips'] in (697, 721)
                hits = [h for h in trace['breakpoint_hits'] if h['label'].startswith('section_')]
                compare = next(h for h in hits if h['label'] == f"section_{row['field']}_compare")
                outcome = next(h for h in hits if h['label'] == f"section_{row['field']}_result")
                increment = [h for h in hits if h['label'] == f"section_{row['field']}_increment"]
                self.assertEqual(bool(increment), expected)
                self.assertEqual(bool(outcome['section_state']['comparison_return_al']), not expected)
                self.assertEqual(compare['section_state']['target_and_actual_mm'][0], 12.5)
                self.assertEqual(any('Размеры колонтитулов должны быть' in d['message'] for d in diagnostics), expected)
                for hit in increment:
                    self.assertEqual(hit['registers']['Eax'], hit['section_state']['parser_address'])


if __name__ == '__main__':
    unittest.main()
