"""Production integration checks for the bounded Native232 section-distance profile."""
import copy
import json
import sys
import tempfile
import unittest
import zipfile
from argparse import Namespace
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts' / 'testvkr-service'))
from check_document import check_file, context_evidence_valid, load_rule_registry, verification_context
from compare_native_trial import parse_diagnostics
from checkers.native_section_counts import count_section_distance_candidates
from config import settings

EVIDENCE = ROOT / 'evidence' / 'differential-platform-r1'
BOUNDARY = EVIDENCE / 'section-boundaries-r2'
COUNTEREXAMPLE = EVIDENCE / 'one-paragraph-counterexample'
RULE = 'Word.HeaderFooterDistanceInvalid'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}


def check(path, mode='master', build=232):
    args = Namespace(work_type=mode, native_build=build, skip_structure=False,
                     skip_pictures=False, skip_word_format=False, skip_dictionary=False,
                     template_id=None, template_path=None, document_kind='vkr')
    return check_file(Path(path), args)


def edit_docx(source, destination, edit):
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(destination, 'w') as dst:
        for info in src.infolist():
            payload = src.read(info.filename)
            if info.filename == 'word/document.xml':
                root = etree.fromstring(payload)
                edit(root)
                payload = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
            dst.writestr(info, payload)


class NativeSectionModelTests(unittest.TestCase):
    def test_all_16_frozen_branches_match_native_family_and_field(self):
        receipt = json.loads((BOUNDARY / 'receipt.json').read_text(encoding='utf-8'))
        self.assertEqual(receipt['status'], 'passed_section_distance_boundary_branches')
        self.assertEqual(len(receipt['cases']), 16)
        for row in receipt['cases']:
            with self.subTest(case=row['case']):
                path = BOUNDARY / (row['case'] + '.docx')
                result = check(path, row['work_type'])
                obs = result['native_section_observations']
                expected = row['twips'] in (697, 721)
                self.assertTrue(obs['supported'])
                self.assertEqual(obs['count'], int(expected))
                field = obs['sections'][0]['fields'][row['field']]
                self.assertEqual(field['twips'], row['twips'])
                self.assertEqual(field['mismatch'], expected)
                finding = next((f for f in result['findings'] if f['rule_id'] == RULE), None)
                self.assertEqual(finding is not None, expected)
                native_text = (BOUNDARY / row['case'] / 'native-result.txt').read_text(encoding='utf-8')
                native_hits = [d for d in parse_diagnostics(native_text, 'docx') if d['rule_id'] == RULE]
                self.assertEqual(len(native_hits), int(expected))
                if finding:
                    self.assertEqual(finding['verification_status'], 'verified_against_original')
                    self.assertTrue(finding['threshold']['native_section_predicate_supported'])
                    self.assertEqual(finding['threshold']['native_mismatch_count'], 1)
                    self.assertEqual(finding['location']['section'], 1)
                    self.assertEqual(finding['location']['native_section_fields'], [row['field']])
                    occurrences = finding['precise_locations']['occurrences']
                    self.assertEqual(len(occurrences), 1)
                    self.assertEqual(occurrences[0]['section'], 1)
                    self.assertEqual(occurrences[0]['attribute'], 'w:' + row['field'])
                    self.assertEqual(occurrences[0]['raw_twips'], row['twips'])
                    self.assertEqual(occurrences[0]['xml_path'],
                                     f"/w:document/w:body/w:sectPr/w:pgMar/@w:{row['field']}")

    def test_one_paragraph_counterexample_is_supported_and_keeps_native_result(self):
        path = COUNTEREXAMPLE / 'input.docx'
        with zipfile.ZipFile(path) as archive:
            root = etree.fromstring(archive.read('word/document.xml'))
        self.assertEqual(len(root.xpath('/w:document/w:body/w:p', namespaces=NS)), 1)
        result = check(path, 'master')
        obs = result['native_section_observations']
        self.assertTrue(obs['supported'])
        self.assertEqual(obs['count'], 1)
        self.assertEqual(obs['sections'][0]['fields']['header']['twips'], 681)
        self.assertFalse(obs['sections'][0]['fields']['footer']['mismatch'])
        finding = next(f for f in result['findings'] if f['rule_id'] == RULE)
        self.assertEqual(finding['verification_status'], 'verified_against_original')
        self.assertEqual(finding['location']['native_section_fields'], ['header'])
        occurrence = finding['precise_locations']['occurrences'][0]
        self.assertEqual(occurrence['attribute'], 'w:header')
        self.assertEqual(occurrence['raw_twips'], 681)
        native_text = (COUNTEREXAMPLE / 'native-result.txt').read_text(encoding='utf-8')
        self.assertEqual(len([d for d in parse_diagnostics(native_text, 'docx') if d['rule_id'] == RULE]), 1)

    def test_build_230_keeps_legacy_setting_separate_from_native_fixed_predicate(self):
        registry = load_rule_registry()
        rule = registry[RULE]
        for mode in ('master', 'phd'):
            context = verification_context(rule, 'docx', mode, 232)
            self.assertIsNotNone(context)
            self.assertTrue(context_evidence_valid(context))
        self.assertIsNone(verification_context(rule, 'pdf', 'master', 232))
        cases = {'outside': BOUNDARY / 'master-header-697.docx',
                 'inside': BOUNDARY / 'master-header-698.docx'}
        old_setting = settings.HEADER_FOOTER_DISTANCE_CM
        try:
            settings.HEADER_FOOTER_DISTANCE_CM = 10.0
            native = {name: check(path, 'master', 232) for name, path in cases.items()}
            legacy = {name: check(path, 'master', 230) for name, path in cases.items()}
        finally:
            settings.HEADER_FOOTER_DISTANCE_CM = old_setting
        self.assertEqual(native['outside']['native_section_observations']['count'], 1)
        self.assertEqual(native['inside']['native_section_observations']['count'], 0)
        self.assertEqual(legacy['outside'].get('native_section_observations', {}), {})
        self.assertEqual(legacy['inside'].get('native_section_observations', {}), {})
        for result in legacy.values():
            finding = next(f for f in result['findings'] if f['rule_id'] == RULE)
            self.assertEqual(finding['verification_status'], 'pending_original_program_comparison')
            self.assertEqual(finding['threshold']['value'], 10.0)
            self.assertNotIn('native_section_predicate_supported', finding['threshold'])

    def test_settings_override_changes_only_legacy_policy(self):
        path = BOUNDARY / 'master-header-697.docx'
        original = settings.HEADER_FOOTER_DISTANCE_CM
        try:
            default_native = check(path, 'master', 232)['native_section_observations']
            settings.HEADER_FOOTER_DISTANCE_CM = 10.0
            overridden_native = check(path, 'master', 232)['native_section_observations']
            legacy = check(path, 'master', 230)
        finally:
            settings.HEADER_FOOTER_DISTANCE_CM = original
        self.assertEqual(overridden_native, default_native)
        legacy_finding = next(f for f in legacy['findings'] if f['rule_id'] == RULE)
        self.assertEqual(legacy_finding['threshold']['value'], 10.0)

    def test_missing_distances_multi_section_and_complex_story_are_unassessed(self):
        source = BOUNDARY / 'master-header-697.docx'
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as directory:
            missing_cases = {}
            for field in ('header', 'footer'):
                target = Path(directory) / f'missing-{field}.docx'
                def remove_field(root, field=field):
                    pg = root.find('.//w:sectPr/w:pgMar', NS)
                    pg.attrib.pop(f'{{{NS["w"]}}}{field}', None)
                edit_docx(source, target, remove_field)
                missing_cases[field] = target

            multi = Path(directory) / 'multi-section.docx'
            def add_section(root):
                body = root.xpath('/w:document/w:body', namespaces=NS)[0]
                p = etree.Element(f'{{{NS["w"]}}}p')
                ppr = etree.SubElement(p, f'{{{NS["w"]}}}pPr')
                sect = etree.SubElement(ppr, f'{{{NS["w"]}}}sectPr')
                mar = etree.SubElement(sect, f'{{{NS["w"]}}}pgMar')
                mar.set(f'{{{NS["w"]}}}header', '720')
                mar.set(f'{{{NS["w"]}}}footer', '720')
                body.insert(0, p)
            edit_docx(source, multi, add_section)

            complex_path = Path(directory) / 'table.docx'
            def add_table(root):
                body = root.xpath('/w:document/w:body', namespaces=NS)[0]
                table = etree.Element(f'{{{NS["w"]}}}tbl')
                etree.SubElement(table, f'{{{NS["w"]}}}tblPr')
                grid = etree.SubElement(table, f'{{{NS["w"]}}}tblGrid')
                etree.SubElement(grid, f'{{{NS["w"]}}}gridCol')
                row = etree.SubElement(table, f'{{{NS["w"]}}}tr')
                cell = etree.SubElement(row, f'{{{NS["w"]}}}tc')
                etree.SubElement(cell, f'{{{NS["w"]}}}p')
                body.insert(0, table)
            edit_docx(source, complex_path, add_table)

            for path in [*missing_cases.values(), multi, complex_path]:
                result = check(path, 'master', 232)
                obs = result['native_section_observations']
                self.assertFalse(obs['supported'], path.name)
                self.assertIsNone(obs['count'], path.name)
                finding = next((f for f in result['findings'] if f['rule_id'] == RULE), None)
                if finding:
                    self.assertEqual(finding['verification_status'], 'pending_original_program_comparison')
                    self.assertNotTrue(finding.get('threshold', {}).get('native_section_predicate_supported'))


if __name__ == '__main__':
    unittest.main()
