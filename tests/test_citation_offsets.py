"""Source-bound citation locations use original paragraph offsets."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'scripts/testvkr-service')]
from adjudicate_remaining import structural_facts


class CitationOffsetsTests(unittest.TestCase):
    def test_offsets_and_quotes_align_with_original_source(self):
        source = '  Методы   [1, 2–4] и [5, С. 21] на дороге.'
        data = {'structure_paragraphs': [
            {'index': 0, 'text': source, 'xml_path': '/p[1]'},
            {'index': 1, 'text': 'СПИСОК ЛИТЕРАТУРЫ', 'xml_path': '/p[2]'},
            {'index': 2, 'text': '1. Источник', 'xml_path': '/p[3]'},
        ]}
        result = structural_facts('Struct.MissingCitations', data)
        candidates = result['citation_candidates']
        self.assertEqual([c['citation'] for c in candidates], ['[1, 2–4]', '[5, С. 21]'])
        for candidate in candidates:
            start = candidate['character_start']
            quote = candidate['citation']
            self.assertEqual(source[start:start + len(quote)], quote)

    def test_whitespace_unicode_and_no_candidate(self):
        source = '\t🚘 Работа\u00a0\u00a0[12 ; 14—16]'
        data = {'structure_paragraphs': [{'index': 4, 'text': source, 'xml_path': '/p[5]'}]}
        candidate = structural_facts('Native.CitationsToAbsentSources', data)['citation_candidates'][0]
        self.assertEqual(source[candidate['character_start']:][:len(candidate['citation'])], candidate['citation'])
        self.assertEqual(structural_facts('Struct.MissingCitations', {'structure_paragraphs': [{'text':'Без ссылок'}]})['citation_candidates'], [])


if __name__ == '__main__':
    unittest.main()
