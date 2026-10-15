"""Compare activation timing against retained original-program counters."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import parse_document
from checkers.native_font_counts import count_font_candidates

BASE = ROOT / 'evidence/business-map-232'


class NativeFontActivationTests(unittest.TestCase):
    def test_retained_native_activation_cases(self):
        executions = 0
        for folder in ('font-activation-native-r1', 'font-activation-native-r2',
                       'font-activation-native-r3', 'font-activation-native-r4',
                       'font-activation-boundary-native-r1', 'font-activation-phd-native-r1'):
            for case in json.loads((BASE / folder / 'matrix.json').read_text())['cases']:
                with self.subTest(case=case['case'], mode=case['work_type']):
                    _, data = parse_document(ROOT / case['input'])
                    counts, records = count_font_candidates(data)
                    self.assertTrue(data['native232_font_profile_supported'])
                    for bucket in ('small', 'tiny', 'large'):
                        self.assertEqual(counts[bucket], case['font_state'][bucket + '_count'])
                    self.assertTrue(all(r['native_font_enabled'] for r in records if r['bucket']))
                executions += 1
        self.assertEqual(executions, 44)

    def test_font_precedes_current_paragraph_activation(self):
        for case, enabled in [('fallback60Small', False), ('fallback61Small', True)]:
            _, data = parse_document(BASE / 'font-activation-inputs-r4' / (case + '.docx'))
            _, records = count_font_candidates(data)
            self.assertEqual(records[-1]['native_font_enabled'], enabled)

    def test_structural_empty_boundary_has_no_invented_paragraph_location(self):
        _, data = parse_document(BASE / 'font-activation-inputs-r4/fallback59Table.docx')
        boundary = next(e for e in data['native_font_activation_events'] if e['kind'] == 'table_end_boundary')
        self.assertIsNone(boundary['xml_path'])
        self.assertTrue(boundary['source_table_xml_path'])
        self.assertEqual(boundary['text'], '')

    def test_native_linked_character_precedence_preserves_standard_resolution(self):
        for case, native, standard in [('titleChar50', 25, 14), ('unlinkTitle', 14, 14),
                                       ('titleChar50Direct30', 15, 15)]:
            _, data = parse_document(BASE / 'linked-font-inputs-r1' / (case + '.docx'))
            trace = json.loads((BASE / 'linked-font-native-r1' / case / 'trace.json').read_text())
            runs = [h['font_state'] for h in trace['breakpoint_hits'] if h['label'] == 'font_run_state']
            for i in (0, 1):
                run = data['paragraphs'][i]['runs'][0]
                self.assertEqual(run['font_size_pt'], standard)
                self.assertEqual(run['native_font_size_pt'], native)
                self.assertEqual(runs[i]['size_half_points'], native * 2)


if __name__ == '__main__':
    unittest.main()
