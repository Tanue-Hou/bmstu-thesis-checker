"""Retained native comparisons, final counter alias and report-group proof."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from native_reference_cli import validate_native_run


class ComplexSectionEvidenceTests(unittest.TestCase):
    def test_retained_complex_section_counters_and_reports(self):
        for name in ('complex-section-r1', 'complex-section-r2-final'):
            with self.subTest(campaign=name):
                self.check_campaign(name)

    def check_campaign(self, name):
        base = ROOT / 'evidence' / name
        manifest_path = base / 'manifest.json'
        receipt = json.loads((base / 'native-receipt.json').read_bytes())
        manifest = json.loads(manifest_path.read_bytes())
        self.assertEqual(receipt['status'], 'passed_native_complex_section_observations')
        self.assertEqual(receipt['manifest_sha256'], hashlib.sha256(manifest_path.read_bytes()).hexdigest())
        self.assertEqual(len(receipt['cases']), 2 * len(manifest['cases']))
        cases = {case['case_id']: case for case in manifest['cases']}
        for row in receipt['cases']:
            with self.subTest(case=row['case']):
                source = cases[row['case'].removeprefix(row['mode'] + '-')]
                expected = sum(not 698 <= v <= 720 for v in source['section'].values())
                for relative, digest in row['artifact_sha256'].items():
                    self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), digest)
                folder = base / 'native' / row['case']
                trace = json.loads((folder / 'trace.json').read_bytes())
                text = (folder / 'native-result.txt').read_bytes().decode('utf8')
                diagnostics = validate_native_run(trace, text, row['mode'], 'docx', source['sha256'], True)
                gates = [h for h in trace['breakpoint_hits'] if h['label'] == 'section_distance_report_gate']
                self.assertEqual(len(gates), 1)
                state = gates[0]['section_state']
                self.assertTrue(state['addresses_match'])
                self.assertEqual(int(state['counter_address'], 16), int(state['parser_address'], 16) + 0x28c)
                self.assertEqual(int(state['counter_address'], 16), int(state['report_base'], 16) + 0x134)
                self.assertEqual(state['final_count'], expected)
                self.assertEqual(sum('Размеры колонтитулов должны быть' in d['message'] for d in diagnostics), int(expected > 0))


if __name__ == '__main__':
    unittest.main()
