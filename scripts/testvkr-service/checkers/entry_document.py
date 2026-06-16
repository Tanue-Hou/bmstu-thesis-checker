from typing import List, Dict, Any
from .base import BaseChecker
from models.finding import Finding
from models.enums import Severity, ModuleType

class EntryDocumentChecker(BaseChecker):
    def check(self) -> List[Finding]:
        findings = []
        
        # 1. Check if empty
        has_content = False
        if self.file_type == 'docx':
            paragraphs = self.doc_data.get('paragraphs', [])
            has_content = any(p.get('text', '').strip() for p in paragraphs)
        elif self.file_type == 'pdf':
            spans = self.doc_data.get('spans', [])
            has_content = any(s.get('text', '').strip() for s in spans)
            
        if not has_content:
            findings.append(Finding(
                code="Entry.DocumentEmpty",
                module=ModuleType.ENTRY_DOCUMENT,
                severity=Severity.CRITICAL,
                message="Документ пустой.",
                skip_switch=None
            ))
            
        # 2. Check for protection (if passed from parser error)
        if self.doc_data.get('is_protected', False):
            findings.append(Finding(
                code="Entry.DocumentProtected",
                module=ModuleType.ENTRY_DOCUMENT,
                severity=Severity.CRITICAL,
                message="Снимите защиту с документа.",
                skip_switch=None
            ))
            
        return findings
