from typing import List, Dict, Any
from models.finding import Finding
from config import settings

class BaseChecker:
    def __init__(self, document_data: Dict[str, Any], file_type: str, work_type: str = "bachelor"):
        """
        document_data is the parsed data from DocxParser or PdfParser.
        file_type is 'docx' or 'pdf'.
        """
        self.doc_data = document_data
        self.file_type = file_type
        self.work_type = work_type

    def check(self) -> List[Finding]:
        raise NotImplementedError("Subclasses must implement check()")
