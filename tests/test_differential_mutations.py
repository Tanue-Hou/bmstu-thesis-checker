"""Tests for deterministic DOCX mutations and bounded ddmin certification."""
from __future__ import annotations

from io import BytesIO
import sys
import unittest
import zipfile

from lxml import etree

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from differential_mutations import (  # noqa: E402
    OutcomeStatus,
    PredicateOutcome,
    ddmin,
    delete_paragraph,
    describe_mutation,
    mutate_docx,
    paragraph_atoms,
    retain_paragraphs,
    remove_paragraph_property,
    structural_candidates,
    validate_docx,
)

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {'w': W}


def fixture_docx() -> bytes:
    document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document xmlns:w="{W}"><w:body>
      <w:p><w:pPr><w:ind w:left="120"/><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>
        <w:r><w:rPr><w:sz w:val="24"/></w:rPr><w:t>alpha</w:t></w:r>
        <w:r><w:t>beta</w:t></w:r></w:p>
      <w:p><w:r><w:t>gamma</w:t></w:r></w:p>
      <w:sectPr><w:pgMar w:top="1440" w:bottom="1440" w:gutter="0" w:header="720" w:footer="720"/></w:sectPr>
    </w:body></w:document>'''.encode()
    out = BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
        z.writestr('word/document.xml', document)
        z.writestr('word/styles.xml', b'<styles/>')
        z.writestr('custom/data.bin', b'preserve-me')
    return out.getvalue()


def xml_part(data: bytes, name='word/document.xml'):
    with zipfile.ZipFile(BytesIO(data)) as z:
        return etree.fromstring(z.read(name))


class DifferentialMutationTests(unittest.TestCase):
    def setUp(self):
        self.seed = fixture_docx()

    def test_single_property_mutations_are_deterministic_and_seed_is_immutable(self):
        original = self.seed
        cases = [
            ('paragraph_indent', {'index': 0, 'attribute': 'left', 'value': 240}, '{'+W+'}left', '240'),
            ('paragraph_indent', {'index': 0, 'attribute': 'right', 'value': 120}, '{'+W+'}right', '120'),
            ('paragraph_indent', {'index': 0, 'attribute': 'firstLine', 'value': 360}, '{'+W+'}firstLine', '360'),
            ('paragraph_spacing', {'index': 0, 'attribute': 'line', 'value': 480}, '{'+W+'}line', '480'),
            ('paragraph_spacing', {'index': 0, 'attribute': 'lineRule', 'value': 'exact'}, '{'+W+'}lineRule', 'exact'),
            ('run_font_sz', {'paragraph_index': 0, 'run_index': 0, 'value': 30}, '{'+W+'}val', '30'),
            ('section_page_margin', {'section_index': 0, 'attribute': 'gutter', 'value': 240}, '{'+W+'}gutter', '240'),
            ('section_page_margin', {'section_index': 0, 'attribute': 'header', 'value': 900}, '{'+W+'}header', '900'),
            ('section_page_margin', {'section_index': 0, 'attribute': 'footer', 'value': 900}, '{'+W+'}footer', '900'),
        ]
        for kind, args, attr, expected in cases:
            with self.subTest(property=kind, args=args):
                mutation = {'kind': kind, **args}
                first = mutate_docx(self.seed, mutation)
                second = mutate_docx(self.seed, mutation)
                self.assertEqual(first, second)
                self.assertIn('set to', describe_mutation(mutation))
                validate_docx(first)
                before = xml_part(self.seed)
                after = xml_part(first)
                if kind == 'paragraph_indent':
                    target = after.xpath('./w:body/w:p[1]/w:pPr/w:ind', namespaces=NS)[0]
                    self.assertEqual(target.get(attr), expected)
                    old_ind = before.xpath('./w:body/w:p[1]/w:pPr/w:ind', namespaces=NS)[0]
                    if attr != '{'+W+'}left': self.assertNotIn(attr, old_ind.attrib)
                    else: self.assertEqual(old_ind.get(attr), '120')
                elif kind == 'paragraph_spacing':
                    target = after.xpath('./w:body/w:p[1]/w:pPr/w:spacing', namespaces=NS)[0]
                    self.assertEqual(target.get(attr), expected)
                elif kind == 'run_font_sz':
                    target = after.xpath('./w:body/w:p[1]/w:r[1]/w:rPr/w:sz', namespaces=NS)[0]
                    self.assertEqual(target.get('{'+W+'}val'), '30')
                else:
                    target = after.xpath('./w:body/w:sectPr/w:pgMar', namespaces=NS)[0]
                    self.assertEqual(target.get(attr), expected)
        self.assertEqual(self.seed, original)

    def test_property_removal_and_structural_helpers_preserve_package_and_final_sectpr(self):
        removed = mutate_docx(self.seed, 'left', None, paragraph_index=0)
        validate_docx(removed.data)
        self.assertIsNone(xml_part(removed.data).xpath('./w:body/w:p[1]/w:pPr/w:ind/@w:left', namespaces=NS)[0] if xml_part(removed.data).xpath('./w:body/w:p[1]/w:pPr/w:ind/@w:left', namespaces=NS) else None)
        deleted = delete_paragraph(self.seed, 0)
        validate_docx(deleted.data)
        self.assertEqual(len(xml_part(deleted.data).xpath('./w:body/w:p', namespaces=NS)), 1)
        prop_removed = remove_paragraph_property(self.seed, 0, 'spacing')
        validate_docx(prop_removed.data)
        self.assertFalse(xml_part(prop_removed.data).xpath('./w:body/w:p[1]/w:pPr/w:spacing', namespaces=NS))
        self.assertEqual(len(structural_candidates(self.seed)), 4)
        self.assertEqual(paragraph_atoms(self.seed), [0, 1])
        retained = retain_paragraphs(self.seed, [1])
        validate_docx(retained)
        self.assertEqual(len(xml_part(retained).xpath('./w:body/w:p', namespaces=NS)), 1)
        for candidate in structural_candidates(self.seed):
            with zipfile.ZipFile(BytesIO(self.seed)) as a, zipfile.ZipFile(BytesIO(candidate.data)) as b:
                self.assertEqual(a.namelist(), b.namelist())
                for name in a.namelist():
                    if name != 'word/document.xml':
                        self.assertEqual(a.read(name), b.read(name))
        with self.assertRaises(ValueError):
            remove_paragraph_property(self.seed, 0, 'sectPr')

    def test_ddmin_returns_certified_one_minimal_only_after_complete_delete_one_pass(self):
        calls = []
        result = ddmin(('noise-a', 'cause', 'noise-b'), lambda xs: calls.append(xs) or ('cause' in xs), max_evaluations=50)
        self.assertEqual(result['status'], 'certified_1minimal')
        self.assertEqual(result['items'], ['cause'])
        self.assertGreaterEqual(result['evaluations'], 2)

    def test_budget_exhaustion_and_unresolved_invalid_candidates_never_claim_mismatch(self):
        exhausted = ddmin((1, 2), lambda xs: True, max_evaluations=1)
        self.assertEqual(exhausted['status'], 'budget_exhausted')
        unresolved = ddmin((1, 2), lambda xs: True if xs else None, max_evaluations=20)
        self.assertEqual(unresolved['status'], 'unresolved')
        self.assertEqual(unresolved['unresolved_evaluations'], 1)
        invalid = ddmin((1, 2), lambda xs: PredicateOutcome(OutcomeStatus.MATCH) if xs else PredicateOutcome(OutcomeStatus.INVALID, 'invalid DOCX'), max_evaluations=20)
        self.assertEqual(invalid['status'], 'unresolved')
        self.assertEqual(invalid['unresolved_evaluations'], 1)


if __name__ == '__main__':
    unittest.main()
