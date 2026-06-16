import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List
from models.finding import CheckResponse, Finding, DocumentSummary
from models.enums import Severity, ModuleType
from parsers.docx_parser import DocxParser
from parsers.pdf_parser import PdfParser
from checkers.entry_document import EntryDocumentChecker
from checkers.word_format import WordFormatChecker
from checkers.pictures import PicturesChecker
from checkers.structure import StructureChecker
from checkers.dictionary import DictionaryChecker

router = APIRouter()

@router.post("/check", response_model=CheckResponse)
async def check_document(
    file: UploadFile = File(...),
    work_type: str = Form("bachelor"),
    skip_structure: bool = Form(False),
    skip_pictures: bool = Form(False),
    skip_word_format: bool = Form(False),
    skip_dictionary: bool = Form(False)
):
    # Determine file extension
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.docx', '.pdf']:
        raise HTTPException(status_code=400, detail="Укажите (перетащите) файл формата docx или pdf")

    # Create temporary file in workspace temp folder
    temp_dir = os.path.join(os.getcwd(), "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    import uuid
    temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}{ext}")
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при работе с файлом: {str(e)}")

    findings: List[Finding] = []
    doc_data = {}
    is_protected = False
    
    # 1. Parse content
    try:
        if ext == '.docx':
            parser = DocxParser(temp_file_path)
            doc_data = parser.parse_all()
        else:
            parser = PdfParser(temp_file_path)
            doc_data = parser.parse_all()
    except Exception as e:
        # Check if it was password protected
        # For PDF, fitz raises an exception if password protected.
        # For Word, zipfile raises BadZipFile or similar.
        err_msg = str(e).lower()
        if "encrypted" in err_msg or "password" in err_msg or "decrypt" in err_msg:
            is_protected = True
            doc_data = {"is_protected": True}
        else:
            # Document parsing failed
            # Delete temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return CheckResponse(
                status="failed",
                summary=DocumentSummary(total_findings=1, critical=1, major=0, warning=0, info=0),
                findings=[Finding(
                    code="Entry.DocumentParsingError",
                    module=ModuleType.ENTRY_DOCUMENT,
                    severity=Severity.CRITICAL,
                    message="Ошибка при разборе содержимого документа.",
                    skip_switch=None
                )]
            )

    # Delete temp file
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

    # 2. Run checkers
    file_type = 'docx' if ext == '.docx' else 'pdf'
    
    # Always run entry document check
    entry_checker = EntryDocumentChecker(doc_data, file_type, work_type)
    findings.extend(entry_checker.check())
    
    # If document is empty or protected, skip other checkers
    is_empty_or_protected = any(f.code in ["Entry.DocumentEmpty", "Entry.DocumentProtected"] for f in findings)
    
    if not is_empty_or_protected:
        # Structure Checker
        if not skip_structure:
            structure_checker = StructureChecker(doc_data, file_type, work_type)
            findings.extend(structure_checker.check())
            
        # Pictures Checker
        if not skip_pictures:
            pictures_checker = PicturesChecker(doc_data, file_type, work_type)
            findings.extend(pictures_checker.check())
            
        # Word Format Checker
        if not skip_word_format:
            word_checker = WordFormatChecker(doc_data, file_type, work_type)
            findings.extend(word_checker.check())
            
        # Dictionary Checker
        if not skip_dictionary:
            dict_checker = DictionaryChecker(doc_data, file_type, work_type)
            findings.extend(dict_checker.check())

    # Load rules confidence mapping
    confidence_map = {}
    try:
        import json
        rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rules", "rules_verified.json")
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8-sig") as f:
                rules_data = json.load(f)
                for r in rules_data.get("rules", []):
                    confidence_map[r["rule_id"]] = r["confidence"]
    except Exception:
        pass

    # Enrich findings with confidence levels
    for f in findings:
        f.confidence = confidence_map.get(f.code, "medium")

    # 3. Calculate summary statistics
    critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
    major = sum(1 for f in findings if f.severity == Severity.MAJOR)
    warning = sum(1 for f in findings if f.severity == Severity.WARNING)
    info = sum(1 for f in findings if f.severity == Severity.INFO)
    
    summary = DocumentSummary(
        total_findings=len(findings),
        critical=critical,
        major=major,
        warning=warning,
        info=info
    )
    
    return CheckResponse(
        status="completed",
        summary=summary,
        findings=findings
    )

@router.get("/rules")
async def list_rules():
    # Load rules registry
    rules_data = {}
    try:
        import json
        rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rules", "rules_verified.json")
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8-sig") as f:
                rules_data = json.load(f)
    except Exception:
        pass
    return {
        "description": "Перечень правил форматирования и верификации ВКР (МГТУ им. Н.Э. Баумана)",
        "modules": {
            "entry_document": "Проверка файла, защита, пустое содержимое",
            "structure": "Порядок структурных разделов, пустые и короткие разделы, LaTeX-теги",
            "pictures": "Размер картинок, плавающие рисунки/фигуры, размер надписей",
            "word_format": "Междустрочные интервалы, поля, шрифты, таблицы, переплет",
            "dictionary": "Орфография, смесь латиницы и кириллицы (хомоглифы)"
        },
        "verified_rules": rules_data.get("rules", [])
    }
