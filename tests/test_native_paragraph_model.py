"""Differential checks against retained original-program paragraph counters."""
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/reverse_engineering/predict_native_paragraphs.py'
spec = importlib.util.spec_from_file_location('paragraph_model', SCRIPT)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class NativeParagraphModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads((ROOT / 'evidence/business-map-232/paragraph-audit-r1/audit.json').read_text())

    def test_retained_native_counters_on_all_same_inputs(self):
        rows = self.audit['cases']
        self.assertEqual(len(rows), 45)
        self.assertEqual(len({r['sha256'] for r in rows}), 29)
        for row in rows:
            with self.subTest(case=row['case'], mode=row['work_type']):
                source = ROOT / row['input']
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), row['sha256'])
                actual = model.predict(source)
                self.assertTrue(actual['profile_supported'])
                self.assertEqual(actual['counters'], {k: row['native_counters'][k] for k in ['left', 'right', 'line']})

    def test_activation_and_short_text_are_observed_separately(self):
        rows = {r['case']: r for r in self.audit['cases'] if r['work_type'] == 'master'}
        self.assertEqual(rows['preambleNegative']['native_counters']['left'], 0)
        self.assertEqual(rows['unactivatedNegative']['native_counters']['left'], 0)
        self.assertEqual(rows['shortNegative']['native_counters']['left'], 1)
        self.assertEqual(rows['blankNegative']['native_counters']['left'], 0)
        self.assertEqual(rows['shortLine179']['native_counters']['line'], 1)

    def test_line_and_signed_indent_boundaries_from_native(self):
        rows = {r['case']: r for r in self.audit['cases'] if r['work_type'] == 'master'}
        for name in ['line178', 'line179']:
            self.assertEqual(rows[name]['native_counters']['line'], 1)
        for name in ['line180', 'line181', 'single', 'double', 'exact24', 'atLeast24']:
            self.assertEqual(rows[name]['native_counters']['line'], 0)
        for axis in ['left', 'right']:
            self.assertEqual(rows[axis + 'Negative5']['native_counters'][axis], 0)
            self.assertEqual(rows[axis + 'Negative6']['native_counters'][axis], 1)
            self.assertEqual(rows[axis + 'OneInch']['native_counters'][axis], 0)

    def test_independent_read_only_cli(self):
        row = next(r for r in self.audit['cases'] if r['case'] == 'line179')
        source = ROOT / row['input']
        process = subprocess.run([sys.executable, str(SCRIPT), '--input', str(source)], capture_output=True, timeout=30)
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads(process.stdout)
        self.assertTrue(result['experimental'])
        self.assertEqual(result['source_sha256'], row['sha256'])
        self.assertEqual(result['counters']['line'], 1)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), row['sha256'])


if __name__ == '__main__':
    unittest.main()
