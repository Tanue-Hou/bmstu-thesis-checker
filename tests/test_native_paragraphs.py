"""Production parity and scope checks against actual native paragraph evidence."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from argparse import Namespace
from lxml import etree
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_document import check_file, load_rule_registry, verification_context, context_evidence_valid
BASE = ROOT / 'evidence/business-map-232'
RULES = {'left': 'Word.LeftIndentInvalid', 'right': 'Word.RightIndentInvalid', 'line': 'Word.LineSpacingInvalid'}


def check(path, mode='master', build=232):
    return check_file(path, Namespace(work_type=mode, native_build=build, skip_structure=False,
                                     skip_pictures=False, skip_word_format=False, skip_dictionary=False))


class NativeParagraphTests(unittest.TestCase):
    def test_all_68_actual_executions_match_production_and_exact_locations(self):
        audit = json.loads((BASE / 'paragraph-acceptance-r1/audit.json').read_text())
        self.assertEqual(len(audit['cases']), 68)
        for row in audit['cases']:
            with self.subTest(case=row['case'], mode=row['work_type']):
                result = check(ROOT / row['input'], row['work_type'])
                obs = result['native_paragraph_observations']
                self.assertTrue(obs['profile_supported'])
                self.assertEqual(obs['counters'], {k: row['native_counters'][k] for k in RULES})
                found = {f['rule_id']: f for f in result['findings']}
                for bucket, rule in RULES.items():
                    self.assertEqual(rule in found, obs['counters'][bucket] > 0)
                    if rule in found:
                        f = found[rule]
                        self.assertEqual(f['verification_status'], 'verified_against_original')
                        expected = {p['xml_path'] for p in obs['native_paragraph_records'] if p['matches'][bucket]}
                        self.assertEqual({p['xml_path'] for p in f['precise_locations']['occurrences']}, expected)

    def test_fallback_counts_empty_paragraphs_and_starts_at_61(self):
        for case, count in [('fallback59', 0), ('fallback60', 1), ('blankFallback60', 1), ('fallback1000', 1)]:
            result = check(BASE / 'paragraph-state-inputs-r2' / (case + '.docx'))
            self.assertEqual(result['native_paragraph_observations']['counters']['left'], count)
        result = check(BASE / 'paragraph-state-inputs-r2/fallback60.docx')
        f = next(f for f in result['findings'] if f['rule_id'] == RULES['left'])
        self.assertEqual(f['precise_locations']['occurrences'][0]['native_activation_ordinal'], 61)

    def test_inheritance_direct_override_and_table_ownership(self):
        inherited = check(BASE / 'paragraph-state-inputs-r2/inheritedBoth.docx')
        override = check(BASE / 'paragraph-state-inputs-r2/directOverridesStyle.docx')
        self.assertEqual(inherited['native_paragraph_observations']['counters']['line'], 1)
        self.assertEqual(override['native_paragraph_observations']['counters']['line'], 0)
        table = check(BASE / 'paragraph-state-inputs-r2/tableBoth.docx')
        findings = [f for f in table['findings'] if f['rule_id'] == RULES['line']]
        self.assertEqual(len(findings), 1)
        location = findings[0]['precise_locations']['occurrences'][0]
        self.assertIn('w:tbl', location['xml_path'])
        self.assertEqual(location['content_role'], 'table_text_manual_review')

    def test_complex_formula_cannot_inherit_verified_paragraph_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'formula.docx'
            with zipfile.ZipFile(BASE / 'paragraph-inputs-r4/control.docx') as source, zipfile.ZipFile(path, 'w') as target:
                for info in source.infolist():
                    payload = source.read(info.filename)
                    if info.filename == 'word/document.xml':
                        root = etree.fromstring(payload)
                        body = root.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}body')
                        body[0].append(etree.Element('{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath'))
                        payload = etree.tostring(root)
                    target.writestr(info, payload)
            result = check(path)
            self.assertFalse(result['native_paragraph_observations']['profile_supported'])
            f = next(f for f in result['findings'] if f['rule_id'] == RULES['line'])
            self.assertEqual(f['verification_status'], 'pending_original_program_comparison')

    def test_context_hashes_and_version_format_mode_isolation(self):
        registry = load_rule_registry()
        for rule in RULES.values():
            for mode in ['master', 'phd']:
                context = verification_context(registry[rule], 'docx', mode, 232)
                self.assertTrue(context_evidence_valid(context))
                changed = copy.deepcopy(context)
                changed['implementation_hashes']['scripts/testvkr-service/checkers/native_paragraph_counts.py'] = '0' * 64
                self.assertFalse(context_evidence_valid(changed))
            for fmt, mode in [('pdf', 'phd'), ('pdf', 'master'), ('docx', 'bachelor')]:
                self.assertIsNone(verification_context(registry[rule], fmt, mode, 232))
        old = check(BASE / 'paragraph-inputs-r4/control.docx', build=230)
        self.assertEqual(old['native_paragraph_observations'], {})
        finding = next(f for f in old['findings'] if f['rule_id'] == RULES['line'])
        self.assertNotIn('native_line_integer_minimum', finding['threshold'])

    def test_conditional_table_style_does_not_inherit_plain_table_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'styled-table.docx'
            with zipfile.ZipFile(BASE / 'paragraph-state-inputs-r2/tableBoth.docx') as source, zipfile.ZipFile(path, 'w') as target:
                for info in source.infolist():
                    payload = source.read(info.filename)
                    if info.filename == 'word/document.xml':
                        root = etree.fromstring(payload)
                        ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
                        properties = root.find('.//{%s}tblPr' % ns)
                        etree.SubElement(properties, '{%s}tblStyle' % ns).set('{%s}val' % ns, 'TableGrid')
                        payload = etree.tostring(root)
                    target.writestr(info, payload)
            self.assertFalse(check(path)['native_paragraph_observations']['profile_supported'])

    def test_output_omits_full_thesis_text_and_repair_remains_unchanged(self):
        obs = check(BASE / 'paragraph-state-inputs-r2/fallback1000.docx')['native_paragraph_observations']
        self.assertEqual(len(obs['native_paragraph_records']), 1)
        self.assertFalse(obs['records_truncated'])
        self.assertTrue(all('text' not in r for r in obs['native_paragraph_records']))
        self.assertEqual(hashlib.sha256((ROOT / 'scripts/repair_build232.py').read_bytes()).hexdigest(),
                         '1c43e621f00a260264ec27f260e49e6b24ff67e2bd5f986a9935c047686a5dad')


if __name__ == '__main__':
    unittest.main()
