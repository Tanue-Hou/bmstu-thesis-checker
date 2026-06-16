import os
from typing import Dict, Any, List

class PdfParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        try:
            import fitz
        except ImportError:
            raise ImportError("PyMuPDF (fitz) is not installed. PDF parsing is unavailable.")
        self.doc = fitz.open(file_path)
        self.metadata = {}
        self.parse_basic_metadata()

    def parse_basic_metadata(self):
        self.metadata['file_size_mb'] = os.path.getsize(self.file_path) / (1024 * 1024)
        self.metadata['page_count'] = len(self.doc)
        
        # Check page sizes of all pages
        self.metadata['pages'] = []
        for i, page in enumerate(self.doc):
            rect = page.rect
            # PDF points are 1/72 inch. 1 inch = 25.4 mm.
            # mm = points * 25.4 / 72 = points * 0.352778
            width_mm = rect.width * 0.352778
            height_mm = rect.height * 0.352778
            self.metadata['pages'].append({
                'index': i,
                'width_mm': width_mm,
                'height_mm': height_mm
            })

    def parse_text_and_fonts(self) -> List[Dict[str, Any]]:
        elements = []
        for page_idx, page in enumerate(self.doc):
            text_dict = page.get_text("dict")
            for block in text_dict.get("blocks", []):
                # Only look at text blocks
                if block.get("type") == 0:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            # Convert PDF integer color (sRGB) to hex
                            # fitz color is integer representation of sRGB
                            color_int = span.get("color", 0)
                            r = (color_int >> 16) & 255
                            g = (color_int >> 8) & 255
                            b = color_int & 255
                            color_hex = f"{r:02X}{g:02X}{b:02X}"
                            
                            elements.append({
                                'page_index': page_idx,
                                'text': span.get("text", ""),
                                'font_name': span.get("font", ""),
                                'font_size_pt': span.get("size", 0.0),
                                'color_hex': color_hex,
                                'bbox': span.get("bbox", (0, 0, 0, 0))
                            })
        return elements

    def parse_images(self) -> List[Dict[str, Any]]:
        images_info = []
        for page_idx, page in enumerate(self.doc):
            image_list = page.get_images(full=True)
            for img_idx, img in enumerate(image_list):
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                width = base_image["width"]
                height = base_image["height"]
                byte_size = len(image_bytes)
                
                images_info.append({
                    'page_index': page_idx,
                    'xref': xref,
                    'width_px': float(width),
                    'height_px': float(height),
                    'byte_size_mb': byte_size / (1024 * 1024),
                    'extension': image_ext
                })
        return images_info

    def parse_all(self) -> Dict[str, Any]:
        return {
            'file_size_mb': self.metadata['file_size_mb'],
            'page_count': self.metadata['page_count'],
            'pages': self.metadata['pages'],
            'spans': self.parse_text_and_fonts(),
            'images': self.parse_images()
        }
