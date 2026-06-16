from enum import Enum

class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    WARNING = "warning"
    INFO = "info"

class ModuleType(str, Enum):
    ENTRY_DOCUMENT = "entry_document"
    STRUCTURE = "structure"
    PICTURES = "pictures"
    WORD_FORMAT = "word_format"
    DICTIONARY = "dictionary"
