from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from .enums import Severity, ModuleType

class Finding(BaseModel):
    code: str
    module: ModuleType
    severity: Severity
    message: str
    location: Optional[Dict[str, Any]] = None  # e.g., {"page": 5, "paragraph": 1, "text": "..."}
    threshold: Optional[Dict[str, Any]] = None # e.g., {"value": 12, "unit": "pt", "actual": 11.5}
    skip_switch: Optional[str] = None          # e.g., "SkipTestWord"
    confidence: Optional[str] = None           # e.g., "high", "medium", "low"
    verification_status: str = "unverified_local_heuristic"

class DocumentSummary(BaseModel):
    total_findings: int
    critical: int
    major: int
    warning: int
    info: int

class CheckResponse(BaseModel):
    status: str
    verification_status: str = "local_policy_check_not_original_program_certification"
    summary: DocumentSummary
    findings: List[Finding]
