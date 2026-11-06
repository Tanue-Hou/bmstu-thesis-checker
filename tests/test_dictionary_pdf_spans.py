import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts' / 'testvkr-service'))
from checkers.dictionary import DictionaryChecker


def span(text, line_text, page=0, block=0, line=0, index=0):
    return {'text': text, 'line_text': line_text, 'page_index': page,
            'block_index': block, 'line_index': line, 'span_index': index}


def mixed_findings(data, file_type):
    return [f for f in DictionaryChecker(data, file_type).check()
            if f.code == 'Dict.MixedScriptHomoglyphs']


class DictionaryPdfSpanTests(unittest.TestCase):
    def test_word_split_across_font_spans_counted_once(self):
        text = 'Слово маpка в тексте'
        spans = [span(t, text, index=i) for i, t in enumerate(['Слово ма', 'p', 'ка в тексте'])]
        findings = mixed_findings({'spans': spans}, 'pdf')
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].threshold['count_mixed_words'], 1)
        self.assertEqual(findings[0].location['examples'], ['маpка'])

    def test_same_text_on_distinct_lines_and_pages_is_not_deduplicated(self):
        spans = [span('маpка', 'маpка'), span('маpка', 'маpка', line=1),
                 span('маpка', 'маpка', page=1)]
        self.assertEqual(mixed_findings({'spans': spans}, 'pdf')[0].threshold['count_mixed_words'], 3)

    def test_legacy_spans_without_line_metadata_remain_independent(self):
        spans = [{'text': 'маpка'}, {'text': 'маpка'}]
        self.assertEqual(mixed_findings({'spans': spans}, 'pdf')[0].threshold['count_mixed_words'], 2)

    def test_docx_and_clean_pdf_remain_unchanged(self):
        docx = {'paragraphs': [{'text': 'маpка'}, {'text': 'обычное слово'}]}
        self.assertEqual(mixed_findings(docx, 'docx')[0].location['examples'], ['маpка'])
        spans = [span('обычное ', 'обычное слово'), span('слово', 'обычное слово', index=1)]
        self.assertEqual(mixed_findings({'spans': spans}, 'pdf'), [])

if __name__ == '__main__':
    unittest.main()
