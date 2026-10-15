# -*- coding: utf-8 -*-
import re
from typing import List

from .base import BaseChecker
from models.finding import Finding
from models.enums import Severity, ModuleType
from config import settings


def U(text: str) -> str:
    try:
        return text.encode("ascii").decode("unicode_escape")
    except UnicodeEncodeError:
        return text


class StructureChecker(BaseChecker):
    ABSTRACT_KEYWORDS = [U("\u0440\u0435\u0444\u0435\u0440\u0430\u0442"), U("\u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u044f"), "abstract", "synopsis"]
    TOC_KEYWORDS = [U("\u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435"), U("\u043e\u0433\u043b\u0430\u0432\u043b\u0435\u043d\u0438\u0435")]
    INTRO_KEYWORDS = [U("\u0432\u0432\u0435\u0434\u0435\u043d\u0438\u0435")]
    OUTRO_KEYWORDS = [U("\u0437\u0430\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435")]
    BIB_KEYWORDS = [
        U("\u0441\u043f\u0438\u0441\u043e\u043a \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a\u043e\u0432"),
        U("\u0441\u043f\u0438\u0441\u043e\u043a \u043b\u0438\u0442\u0435\u0440\u0430\u0442\u0443\u0440\u044b"),
    ]

    MSG_LATEX = U("** \u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442 \u0442\u0435\u0433\u0438 \u0438\u0437 LaTeX.")
    MSG_EMPTY_SECTIONS = U("** \u041e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d\u044b \u043f\u0443\u0441\u0442\u044b\u0435 \u0440\u0430\u0437\u0434\u0435\u043b\u044b, \u043f\u043e\u0434\u0440\u0430\u0437\u0434\u0435\u043b\u044b, \u043f\u0443\u043d\u043a\u0442\u044b, \u043f\u043e\u0434\u043f\u0443\u043d\u043a\u0442\u044b:")
    MSG_REQUIRED = U("\u041e\u0442\u0441\u0443\u0442\u0441\u0442\u0432\u0443\u044e\u0442 \u0438\u043b\u0438 \u043d\u0435\u043f\u0440\u0430\u0432\u0438\u043b\u044c\u043d\u043e \u043e\u0444\u043e\u0440\u043c\u043b\u0435\u043d\u044b \u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043a\u0438 \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u043d\u044b\u0445 \u044d\u043b\u0435\u043c\u0435\u043d\u0442\u043e\u0432:")
    MSG_ORDER = U("* \u041d\u0430\u0440\u0443\u0448\u0435\u043d \u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0441\u043b\u0435\u0434\u043e\u0432\u0430\u043d\u0438\u044f \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u043d\u044b\u0445 \u044d\u043b\u0435\u043c\u0435\u043d\u0442\u043e\u0432 (\u0440\u0435\u0444\u0435\u0440\u0430\u0442 (\u0430\u043d\u043d\u043e\u0442\u0430\u0446\u0438\u044f), \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435, \u0432\u0432\u0435\u0434\u0435\u043d\u0438\u0435, \u0437\u0430\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435, \u0441\u043f\u0438\u0441\u043e\u043a \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u043d\u044b\u0445 \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a\u043e\u0432).")
    MSG_EMPTY_STRUCT = U("** \u041e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d\u044b \u043f\u0443\u0441\u0442\u044b\u0435 \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u043d\u044b\u0435 \u044d\u043b\u0435\u043c\u0435\u043d\u0442\u044b:")
    MSG_SMALL_STRUCT = U("* \u041e\u0431\u043d\u0430\u0440\u0443\u0436\u0435\u043d\u044b \u043d\u0435\u0431\u043e\u043b\u044c\u0448\u0438\u0435 \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u043d\u044b\u0435 \u044d\u043b\u0435\u043c\u0435\u043d\u0442\u044b:")
    MSG_CITATIONS = U("* \u0423\u043a\u0430\u0436\u0438\u0442\u0435 \u0441\u0441\u044b\u043b\u043a\u0438 \u043d\u0430 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u043d\u044b\u0435 \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a\u0438:")
    MSG_SMALL_THESIS = U("* \u041c\u0430\u043b\u0435\u043d\u044c\u043a\u0438\u0439 \u043e\u0431\u044a\u0435\u043c \u0412\u041a\u0420:")

    def _get_min_chars(self) -> int:
        thresholds = {
            "bachelor": settings.THESIS_SIZE_MIN_BACHELOR,
            "specialist": settings.THESIS_SIZE_MIN_SPECIALIST,
            "master": settings.THESIS_SIZE_MIN_MASTER,
            "phd": 0,  # Build 230 work code 5 selects no numeric character floor.
        }
        return thresholds.get(self.work_type.lower(), settings.THESIS_SIZE_MIN_DEFAULT)

    def check(self) -> List[Finding]:
        findings: List[Finding] = []
        if self.file_type == "docx":
            self._check_docx_structure(findings)
            if self.work_type in ('master','phd'):
                from .graduate_structure import check_graduate
                replaced={'Struct.RequiredHeadingsMissing','Struct.EmptyStructuralElement','Struct.SmallStructuralElement','Struct.ThesisSizeTooSmall'}
                findings=[f for f in findings if f.code not in replaced]
                findings.extend(check_graduate(self.doc_data,self.work_type))
        elif self.file_type == "pdf":
            self._check_pdf_structure(findings)
        return findings

    def _check_docx_structure(self, findings: List[Finding]):
        paragraphs = self.doc_data.get("paragraphs", [])
        latex_count = 0
        latex_patterns = [r"\\begin\{", r"\\end\{", r"\\section", r"\$.*\$"]
        citation_pattern = re.compile(r"\[\d+\]|\[\d+-\d+\]")
        citations_found = []
        structure_map = []
        current_section = None
        section_char_count = 0
        empty_headings = 0
        total_chars = 0

        for idx, p in enumerate(paragraphs):
            text = p.get("text", "")
            text_lower = text.lower().strip()
            total_chars += len(text)
            for pat in latex_patterns:
                if re.search(pat, text):
                    latex_count += 1
            if citation_pattern.search(text):
                citations_found.extend(citation_pattern.findall(text))

            is_structural = False
            heading_type = None
            if text_lower in self.ABSTRACT_KEYWORDS:
                is_structural = True
                heading_type = "abstract"
            elif text_lower in self.TOC_KEYWORDS:
                is_structural = True
                heading_type = "toc"
            elif text_lower in self.INTRO_KEYWORDS:
                is_structural = True
                heading_type = "introduction"
            elif text_lower in self.OUTRO_KEYWORDS:
                is_structural = True
                heading_type = "conclusion"
            elif text_lower in self.BIB_KEYWORDS:
                is_structural = True
                heading_type = "bibliography"

            if is_structural:
                if current_section:
                    current_section["char_count"] = section_char_count
                current_section = {"type": heading_type, "idx": idx, "text": text, "char_count": 0}
                structure_map.append(current_section)
                section_char_count = 0
            else:
                section_char_count += len(text)
            if re.match(r"^\d+(\.\d+)+\.?\s*$", text_lower):
                empty_headings += 1

        if current_section:
            current_section["char_count"] = section_char_count

        if latex_count > 0:
            findings.append(Finding(code="Struct.ContainsLatex", module=ModuleType.STRUCTURE, severity=Severity.MAJOR, message=self.MSG_LATEX, threshold={"count_tags": latex_count}, skip_switch="SkipTestStruct"))
        if empty_headings > 0:
            findings.append(Finding(code="Struct.EmptySections", module=ModuleType.STRUCTURE, severity=Severity.MAJOR, message=self.MSG_EMPTY_SECTIONS, threshold={"count": empty_headings}, skip_switch="SkipTestStruct"))

        present_types = [s["type"] for s in structure_map]
        missing = [r for r in ["introduction", "conclusion", "bibliography"] if r not in present_types]
        if missing:
            findings.append(Finding(code="Struct.RequiredHeadingsMissing", module=ModuleType.STRUCTURE, severity=Severity.INFO, message=self.MSG_REQUIRED, threshold={"missing": missing}, skip_switch="SkipTestStruct"))

        type_order = ["abstract", "toc", "introduction", "conclusion", "bibliography"]
        order_indices = [type_order.index(t) for t in present_types if t in type_order]
        if order_indices != sorted(order_indices):
            findings.append(Finding(code="Struct.IncorrectHeadingOrder", module=ModuleType.STRUCTURE, severity=Severity.INFO, message=self.MSG_ORDER, skip_switch="SkipTestStruct"))

        for sec in structure_map:
            if sec["char_count"] == 0:
                findings.append(Finding(code="Struct.EmptyStructuralElement", module=ModuleType.STRUCTURE, severity=Severity.MAJOR, message=f"{self.MSG_EMPTY_STRUCT} {sec['text']}", location={"paragraph_idx": sec["idx"]}, skip_switch="SkipTestStruct"))
            elif sec["char_count"] < 300:
                findings.append(Finding(code="Struct.SmallStructuralElement", module=ModuleType.STRUCTURE, severity=Severity.WARNING, message=f"{self.MSG_SMALL_STRUCT} {sec['text']}", location={"paragraph_idx": sec["idx"]}, threshold={"min_chars": 300, "actual": sec["char_count"]}, skip_switch="SkipTestStruct"))

        if "bibliography" in present_types and not citations_found:
            findings.append(Finding(code="Struct.MissingCitations", module=ModuleType.STRUCTURE, severity=Severity.WARNING, message=self.MSG_CITATIONS, skip_switch="SkipTestStruct"))

        min_chars = self._get_min_chars()
        if total_chars < min_chars:
            findings.append(Finding(code="Struct.ThesisSizeTooSmall", module=ModuleType.STRUCTURE, severity=Severity.WARNING, message=self.MSG_SMALL_THESIS, threshold={"min_chars": min_chars, "actual": total_chars}, skip_switch="SkipTestStruct"))

    def _check_pdf_structure(self, findings: List[Finding]):
        spans = self.doc_data.get("spans", [])
        text_full = re.sub(r"\s+", " ", " ".join([s.get("text", "") for s in spans])).lower()
        # PDF extraction may contain NBSP; require an actual heading, not a TOC/body mention.
        lines=[re.sub(r"\s+", " ", span.get('line_text',span.get('text',''))).strip().lower() for span in spans]
        missing=[]
        names={'introduction':self.INTRO_KEYWORDS,'conclusion':self.OUTRO_KEYWORDS,'bibliography':self.BIB_KEYWORDS}
        if self.doc_data.get('document_kind')=='dissertation':
            names['conclusion']=self.OUTRO_KEYWORDS+['общие выводы и заключение','общие выводы','основные результаты и выводы']
            names['bibliography']=self.BIB_KEYWORDS+['список использованной литературы','литература']
        if self.work_type=='phd' and self.doc_data.get('document_kind')!='dissertation':
            names.update({'abstract':['реферат','аннотация','реферат (аннотация)'],'toc':['оглавление']})
        for key,aliases in names.items():
            if not any(line in aliases for line in lines):missing.append(key)
        if missing:
            labels={'introduction':'ВВЕДЕНИЕ','conclusion':'ЗАКЛЮЧЕНИЕ','bibliography':'СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ','abstract':'РЕФЕРАТ (АННОТАЦИЯ)','toc':'ОГЛАВЛЕНИЕ'}
            findings.append(Finding(code="Struct.RequiredHeadingsMissing", module=ModuleType.STRUCTURE, severity=Severity.INFO,
                message=self.MSG_REQUIRED+' '+', '.join('"'+labels[k]+'"' for k in missing),
                threshold={"missing":missing,"native_predicate_supported":self.work_type=='phd' and set(missing)<= {'abstract','toc'}}, skip_switch="SkipTestStruct"))

        latex_count = 0
        for span in spans:
            t = span.get("text", "")
            if "\\begin{" in t or "\\end{" in t or "\\section" in t:
                latex_count += 1
        if latex_count > 0:
            findings.append(Finding(code="Struct.ContainsLatex", module=ModuleType.STRUCTURE, severity=Severity.MAJOR, message=self.MSG_LATEX, threshold={"count_tags": latex_count}, skip_switch="SkipTestStruct"))

        min_chars = self._get_min_chars()
        if len(text_full) < min_chars:
            findings.append(Finding(code="Struct.ThesisSizeTooSmall", module=ModuleType.STRUCTURE, severity=Severity.WARNING, message=self.MSG_SMALL_THESIS, threshold={"min_chars": min_chars, "actual": len(text_full)}, skip_switch="SkipTestStruct"))

        citation_pattern = re.compile(r"\[\d+\]")
        if U("\u0441\u043f\u0438\u0441\u043e\u043a") in text_full and not citation_pattern.search(text_full):
            findings.append(Finding(code="Struct.MissingCitations", module=ModuleType.STRUCTURE, severity=Severity.WARNING, message=self.MSG_CITATIONS, skip_switch="SkipTestStruct"))
