import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TestVkr Service"
    
    # Document Format Thresholds (Extracted from TestVkr.exe)
    LINE_SPACING_BODY: float = 1.5       # lines
    LINE_SPACING_TABLE: float = 1.0      # lines
    FONT_SIZE_MIN_PT: float = 12.0       # pt
    FONT_SCALE_MIN_PCT: float = 70.0     # %
    FONT_SCALE_MAX_PCT: float = 130.0    # %
    TABLE_ROW_HEIGHT_MIN_MM: float = 8.0 # mm
    IMAGE_FILE_SIZE_MAX_MB: float = 40.0 # MB
    HEADER_FOOTER_DISTANCE_CM: float = 1.25 # cm
    FIRST_LINE_INDENT_CM: float = 1.25   # cm
    IMAGE_PIXEL_THRESHOLD: float = 540.0 # px
    
    # Margins (Standard Russian GOST 7.32 & BMSTU)
    MARGIN_LEFT_MM: float = 30.0         # mm
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
