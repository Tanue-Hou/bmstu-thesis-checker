import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TestVkr Service"

    # Local policy defaults; original TestVkr comparisons are not dynamically verified.
    LINE_SPACING_BODY: float = 1.5       # lines
    LINE_SPACING_TABLE: float = 1.0      # lines
    FONT_SIZE_MIN_PT: float = 8.0        # native232 integer at 0x006e519c; ordinary small bucket is4<pt<8
    FONT_SIZE_MAX_PT: float = 18.0       # native232 integer at 0x006e51a0; role-gated strict upper anomaly
    FONT_SCALE_MIN_PCT: float = 70.0     # %
    FONT_SCALE_MAX_PCT: float = 130.0    # %
    TABLE_ROW_HEIGHT_MIN_MM: float = 8.0 # mm
    IMAGE_FILE_SIZE_MAX_MB: float = 40.0 # MB
    HEADER_FOOTER_DISTANCE_CM: float = 1.25 # cm
    FIRST_LINE_INDENT_CM: float = 1.25   # cm
    # Static image decoding paths compare width * height, not width alone.
    IMAGE_PIXEL_AREA_MAX: int = 16000000
    PAGE_SIZE_TOLERANCE_MM: float = 2.0
    MARGIN_TOLERANCE_MM: float = 1.0
    HEADER_FOOTER_TOLERANCE_CM: float = 0.05
    LINE_SPACING_TOLERANCE: float = 0.1
    FIRST_LINE_INDENT_TOLERANCE_CM: float = 0.05
    PARAGRAPH_INDENT_TOLERANCE_CM: float = 0.1
    FONT_VIOLATION_MIN_CHARS: int = 10

    # Margins (Standard Russian GOST 7.32 & BMSTU)
    MARGIN_LEFT_MM: float = 30.0         # mm
    MARGIN_LEFT_PHD_MM: float = 25.0     # build-230 native comparator and adjacent-twip probes; tolerance 0.2 mm
    MARGIN_TOLERANCE_PHD_MM: float = 0.2 # native float32 constant at VA 0x004db64c, dynamically bracketed
    MARGIN_RIGHT_MM: float = 10.0        # mm (sometimes 15.0 or 20.0, default 10.0)
    MARGIN_TOP_MM: float = 20.0          # mm
    MARGIN_BOTTOM_MM: float = 20.0       # mm

    # Page Size (A4)
    PAGE_WIDTH_MM: float = 210.0
    PAGE_HEIGHT_MM: float = 297.0

    # Dict settings
    DICT_UNKNOWN_WORD_THRESHOLD: float = 0.05 # 5% unknown words triggers warning

    # Thesis Size Thresholds (Characters)
    THESIS_SIZE_MIN_BACHELOR: int = 40000
    THESIS_SIZE_MIN_SPECIALIST: int = 50000
    THESIS_SIZE_MIN_MASTER: int = 60000
    THESIS_SIZE_MIN_PHD: int = 100000
    THESIS_SIZE_MIN_DEFAULT: int = 15000

    class Config:
        case_sensitive = True

settings = Settings()
