"""Frozen official-SDK positive/negative controls, without requiring Office in CI."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ComplexSectionSchemaTests(unittest.TestCase):
    def test_valid_r3_inputs_match_sdk_and_native_manifests(self):
        manifest_path = ROOT / 'evidence/complex-section-r3-schema/manifest.json'
        manifest = json.loads(manifest_path.read_bytes())
        receipt = json.loads((ROOT / 'evidence/complex-section-schema-r1/r3-validated-build.json').read_bytes())
        self.assertEqual(hashlib.sha256(manifest_path.read_bytes()).hexdigest(), receipt['manifest_sha256'])
        self.assertTrue(receipt['read_only'] and receipt['source_unchanged'])
        self.assertEqual(receipt['input_count'], len(manifest['cases']))
        self.assertEqual(receipt['valid_input_count'], receipt['input_count'])
        build = receipt['validator_build']
        self.assertEqual(build['source_sha256'], receipt['validator_source_sha256'])
        self.assertEqual(build['validator_binary_sha256'], receipt['validator_binary_sha256'])
        self.assertEqual(build['sdk_binary_sha256'], receipt['sdk_binary_sha256'])
        self.assertEqual(build['package_sha256'], receipt['nuget_package_sha256'])
        for row, case in zip(receipt['cases'], manifest['cases']):
            self.assertEqual(row['case_id'], case['case_id'])
            self.assertEqual(row['errors'], [])
            self.assertEqual(hashlib.sha256((ROOT / row['file']).read_bytes()).hexdigest(), case['sha256'])

    def test_old_invalid_inputs_are_preserved_as_negative_controls(self):
        base = ROOT / 'evidence/complex-section-schema-r1'
        for name in ('r1-validation.json', 'r2-validation.json'):
            receipt = json.loads((base / name).read_bytes())
            self.assertLess(receipt['valid_input_count'], receipt['input_count'])
            errors = [error for case in receipt['cases'] for error in case['errors']]
            self.assertTrue(any(error['id'] == 'Sch_UndeclaredAttribute' and 'noChangeAspect' in error['description'] for error in errors))
            for row in receipt['cases']:
                self.assertEqual(hashlib.sha256((ROOT / row['file']).read_bytes()).hexdigest(), row['source_sha256'])


if __name__ == '__main__':
    unittest.main()
