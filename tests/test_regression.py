import importlib.util
import json
import sys
import tempfile
import subprocess
import unittest
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts' / 'testvkr-service'))
from parsers.docx_parser import DocxParser
from checkers.word_format import WordFormatChecker
from checkers.pictures import PicturesChecker
from check_document import check_file, load_rule_registry
from config import settings
from argparse import Namespace

TEXT = 'Контрольный текст для проверки формата документа. ' * 5

def node(parent, tag, **attributes):
    element = OxmlElement('w:' + tag)
    for key, value in attributes.items():
        element.set(qn('w:' + key), str(value))
    parent.append(element)
    return element

def sample(mode, path):
    doc = Document()
    normal = doc.styles['Normal']
    normal.font.size = Pt(14)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.first_line_indent = Cm(1.25)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    base = doc.styles.add_style('BaseBody', WD_STYLE_TYPE.PARAGRAPH)
    base.base_style = normal
    derived = doc.styles.add_style('DerivedBody', WD_STYLE_TYPE.PARAGRAPH)
    derived.base_style = base
    p = doc.add_paragraph(TEXT, 'DerivedBody')
    run = p.runs[0]
    if mode == 'direct':
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run.font.size = Pt(14)
    elif mode == 'override':
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.first_line_indent = Cm(0)
        run.font.size = Pt(7)
    elif mode == 'character':
        char_base = doc.styles.add_style('CharBase', WD_STYLE_TYPE.CHARACTER)
        char_base.font.size = Pt(7)
        char_child = doc.styles.add_style('CharChild', WD_STYLE_TYPE.CHARACTER)
        char_child.base_style = char_base
        run.style = char_child
    elif mode == 'hidden_off':
        base.font.hidden = True
        run.font.hidden = False
    elif mode == 'exact':
        p.paragraph_format.line_spacing = Pt(18)
    elif mode == 'default':
        normal.font.size = None
        defaults = doc.styles.element.find(qn('w:docDefaults'))
        rdefaults = defaults.find(qn('w:rPrDefault')).find(qn('w:rPr'))
        sz = rdefaults.find(qn('w:sz'))
        if sz is not None:
            rdefaults.remove(sz)
        node(rdefaults, 'sz', val=28)
    elif mode == 'partial':
        base.paragraph_format.space_after = Pt(9)
        p.paragraph_format.space_before = Pt(3)
    elif mode == 'table':
        cell = doc.add_table(rows=1, cols=1).cell(0, 0)
        cp = cell.paragraphs[0]
        cp.text = TEXT
        cp.style = derived
        derived.paragraph_format.line_spacing = 1.0
    doc.save(path)
    return path


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def parse(self, mode):
        path = sample(mode, Path(self.temp.name) / (mode + '.docx'))
        return DocxParser(str(path)).parse_all()

    def test_inherited_matches_direct(self):
        inherited, direct = self.parse('inherited'), self.parse('direct')
        for key in ('line_spacing', 'first_line_indent_cm', 'alignment'):
            self.assertEqual(inherited['paragraphs'][0][key], direct['paragraphs'][0][key])
        self.assertEqual(inherited['paragraphs'][0]['runs'][0]['font_size_pt'], 14)
        for data in (inherited, direct):
            codes = {f.code for f in WordFormatChecker(data, 'docx', 'bachelor').check()}
            self.assertTrue(codes.isdisjoint({'Word.FontSizeTooSmall', 'Word.LineSpacingInvalid', 'Word.FirstLineIndentInvalid'}))

    def test_direct_override_triggers(self):
        data = self.parse('override')
        codes = {f.code for f in WordFormatChecker(data, 'docx', 'bachelor').check()}
        self.assertTrue({'Word.FontSizeTooSmall', 'Word.LineSpacingInvalid', 'Word.FirstLineIndentInvalid'} <= codes)

    def test_character_based_on(self):
        self.assertEqual(self.parse('character')['paragraphs'][0]['runs'][0]['font_size_pt'], 7)

    def test_doc_defaults(self):
        self.assertEqual(self.parse('default')['paragraphs'][0]['runs'][0]['font_size_pt'], 14)

    def test_explicit_hidden_false(self):
        self.assertFalse(self.parse('hidden_off')['paragraphs'][0]['runs'][0]['is_hidden'])

    def test_partial_spacing_attributes_inherit(self):
        p = self.parse('partial')['paragraphs'][0]
        self.assertEqual(p['line_spacing'], 1.5)
        self.assertEqual(p['space_before_pt'], 3)
        self.assertEqual(p['space_after_pt'], 9)

    def test_exact_spacing_keeps_units(self):
        p = self.parse('exact')['paragraphs'][0]
        self.assertEqual(p['line_spacing_type'], 'pt')
        self.assertEqual(p['line_spacing'], 18)

    def test_table_inherits(self):
        p = self.parse('table')['tables'][0]['rows'][0]['cells'][0]['paragraphs'][0]
        self.assertEqual(p['line_spacing'], 1.0)
        self.assertEqual(p['runs'][0]['font_size_pt'], 14)

    def test_image_guess_disabled(self):
        data = {'images': [{'width_px': 4000, 'height_px': 4000}]}
        self.assertNotIn('Pic.PixelSizeTooLarge', {f.code for f in PicturesChecker(data, 'docx', 'bachelor').check()})

    def test_image_area_not_width(self):
        for w, h, expected in ((4000, 4000, False), (4001, 4000, True), (16001, 1, False), (1, 16000001, True)):
            data = {'images': [{'width_px': w, 'height_px': h}]}
            codes = {f.code for f in PicturesChecker(data, 'docx', 'bachelor').check()}
            self.assertEqual('Pic.PixelSizeTooLarge' in codes, expected)

    def test_registry_does_not_claim_original_verification(self):
        for rule in load_rule_registry().values():
            if rule['verification_status']=='verified_against_original':
                import hashlib
                evidence=ROOT/rule['evidence_refs'][0]
                self.assertEqual(hashlib.sha256(evidence.read_bytes()).hexdigest(),rule['verification_evidence_sha256'])
                self.assertTrue(json.loads(evidence.read_text(encoding='utf-8'))['checks'][rule['rule_id']]['pass'])
            else:
                self.assertIsNone(rule['observed_message'])
        self.assertEqual(load_rule_registry()['Word.FontSizeTooSmall']['threshold'], settings.FONT_SIZE_MIN_PT)

    def test_report_preserves_runtime_message_and_evidence_status(self):
        path = sample('override', Path(self.temp.name) / 'override.docx')
        args = Namespace(work_type='bachelor', skip_structure=True, skip_pictures=True, skip_word_format=False, skip_dictionary=True)
        result = check_file(path, args)
        self.assertIn('formatting_coverage', result)
        finding = next(f for f in result['findings'] if f['rule_id'] == 'Word.FontSizeTooSmall')
        self.assertIn(str(settings.FONT_SIZE_MIN_PT), finding['message'])
        self.assertEqual(finding['verification_status'], 'verified_against_original')
        self.assertEqual(finding['fix_priority'], 'must_fix')
        self.assertIn('未完成原程序对照', __import__('check_document').render_markdown(result))

    def test_font_size_boundaries(self):
        for size, expected in ((7.5, True), (8.0, False), (8.5, False), (12.0, False)):
            doc = Document()
            p = doc.add_paragraph(TEXT)
            p.runs[0].font.size = Pt(size)
            path = Path(self.temp.name) / (str(size) + '.docx')
            doc.save(path)
            data = DocxParser(str(path)).parse_all()
            codes = {f.code for f in WordFormatChecker(data, 'docx', 'bachelor').check()}
            self.assertEqual('Word.FontSizeTooSmall' in codes, expected)

    def test_font_upper_boundary(self):
        for size, expected in ((18.0, False), (18.5, True)):
            doc = Document()
            doc.add_paragraph(TEXT).runs[0].font.size = Pt(size)
            path = Path(self.temp.name) / (str(size) + '.docx')
            doc.save(path)
            data = DocxParser(str(path)).parse_all()
            codes = {f.code for f in WordFormatChecker(data, 'docx', 'bachelor').check()}
            self.assertEqual('Word.FontSizeTooLarge' in codes, expected)

    def test_zero_margin_is_not_missing(self):
        doc = Document()
        doc.sections[0].left_margin = Cm(0)
        doc.sections[0].header_distance = Cm(0)
        doc.add_paragraph(TEXT)
        path = Path(self.temp.name) / 'zero.docx'
        doc.save(path)
        data = DocxParser(str(path)).parse_all()
        self.assertEqual(data['sections'][0]['margin_left_mm'], 0)
        codes = {f.code for f in WordFormatChecker(data, 'docx', 'bachelor').check()}
        self.assertTrue({'Word.LeftMarginInvalid', 'Word.HeaderFooterDistanceInvalid'} <= codes)

    def test_mcp_rule_metadata_matches_runtime(self):
        spec = importlib.util.spec_from_file_location('checker_mcp', ROOT / 'mcp' / 'server.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        rule = next(r for r in module.merged_rules() if r['rule_id'] == 'Word.FontSizeTooSmall')
        self.assertEqual(rule['threshold'], settings.FONT_SIZE_MIN_PT)
        self.assertEqual(rule['verification_status'], 'verified_against_original')

    def test_mcp_stdio_protocol(self):
        messages = [
            {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-11-25'}},
            {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
            {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'list_rules', 'arguments': {}}},
        ]
        run = subprocess.run([sys.executable, str(ROOT / 'mcp' / 'server.py')],
                             input='\n'.join(json.dumps(m) for m in messages) + '\n',
                             capture_output=True, text=True, encoding='utf-8', timeout=15)
        self.assertEqual(run.returncode, 0, run.stderr)
        replies = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual([r['id'] for r in replies], [1, 2, 3])
        self.assertEqual(len(replies[1]['result']['tools']), 7)
        self.assertEqual(sum(r['verification_status']=='verified_against_original' for r in replies[2]['result']['structuredContent']['rules']),18)

    def test_verification_does_not_transfer_to_pdf_or_other_work_type(self):
        from check_document import finding_to_dict,load_rule_guidance
        from models.finding import Finding
        from models.enums import Severity,ModuleType
        f=Finding(code='Word.FontSizeTooSmall',module=ModuleType.WORD_FORMAT,severity=Severity.MAJOR,message='test')
        for file_type,work_type in [('pdf','bachelor'),('docx','specialist')]:
            result=finding_to_dict(f,load_rule_registry(),load_rule_guidance(),file_type,work_type)
            self.assertEqual(result['verification_status'],'pending_original_program_comparison')
            self.assertEqual(result['fix_priority'],'manual_review')


if __name__ == '__main__':
    unittest.main()
