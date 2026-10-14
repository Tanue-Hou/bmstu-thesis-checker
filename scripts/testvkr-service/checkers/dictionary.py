import re
from typing import List, Dict, Any
from .base import BaseChecker
from models.finding import Finding
from models.enums import Severity, ModuleType

class DictionaryChecker(BaseChecker):
    # Regex to detect Russian words
    RU_WORD_PAT = re.compile(r"\b[а-яёА-ЯЁ]+\b")

    # Regex to detect homoglyph swap fraud: mixed Latin and Cyrillic in a single word
    # e.g., 'p' (Latin) and 'а' (Cyrillic) in "раrаgraph"
    MIXED_SCRIPT_PAT = re.compile(r"\b(?=[а-яёА-ЯЁ]*[a-zA-Z])(?=[a-zA-Z]*[а-яёА-ЯЁ])[а-яёА-ЯЁa-zA-Z]+\b")

    def check(self) -> List[Finding]:
        findings = []

        paragraphs = []
        if self.file_type == 'docx':
            paragraphs = [p.get('text', '') for p in self.doc_data.get('paragraphs', [])]
        elif self.file_type == 'pdf':
            paragraphs = [s.get('text', '') for s in self.doc_data.get('spans', [])]

        full_text = " ".join(paragraphs)
        if not full_text.strip():
            return findings

        # 1. Mixed Script (Homoglyph Swaps) - Plagiarism bypass checking
        mixed_words = self.MIXED_SCRIPT_PAT.findall(full_text)
        if mixed_words:
            findings.append(Finding(
                code="Dict.MixedScriptHomoglyphs",
                module=ModuleType.DICTIONARY,
                severity=Severity.MAJOR,
                message="** В документе много незнакомых слов. Возможно они написаны с ошибками (обнаружена смесь латиницы и кириллицы):",
                threshold={"count_mixed_words": len(mixed_words)},
                location={"examples": mixed_words[:10]},
                skip_switch="SkipTestDict"
            ))

        # 2. Extract Russian words and check spelling errors or unknown words ratio
        # Since we do not have Hunspell binaries locally, we can check basic spelling pattern errors:
        # e.g. words with double vowels or consonants that are invalid in Russian, or extremely long words.
        words = self.RU_WORD_PAT.findall(full_text)
        unknown_words = []

        for w in words:
            # Check for suspicious character patterns (e.g. triple consonants, triple vowels, invalid combinations)
            # Russian phonotactics violations: e.g. 'щч', 'ьъ', etc.
            w_lower = w.lower()
            if any(comb in w_lower for comb in ['ьь', 'ъъ', 'ьъ', 'ъь', 'щч', 'шч', 'жш', 'чщ']):
                unknown_words.append(w)

        if len(unknown_words) > 5:
            findings.append(Finding(
                code="Dict.SuspiciousRussianWords",
                module=ModuleType.DICTIONARY,
                severity=Severity.WARNING,
                message="* В документе замечены слова с подозрительными сочетаниями букв (возможны орфографические ошибки):",
                threshold={"count": len(unknown_words)},
                location={"examples": unknown_words[:10]},
                skip_switch="SkipTestDict"
            ))

        return findings
