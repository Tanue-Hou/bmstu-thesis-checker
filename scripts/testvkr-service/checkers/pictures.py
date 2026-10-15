from typing import List, Dict, Any
from .base import BaseChecker
from models.finding import Finding
from models.enums import Severity, ModuleType
from config import settings
from parsers.drawing_geometry import f32


def U(text: str) -> str:
    try:
        return text.encode("ascii").decode("unicode_escape")
    except UnicodeEncodeError:
        return text


class PicturesChecker(BaseChecker):
    MSG_FILE_SIZE = U(r"*** \u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442 \u0440\u0438\u0441\u0443\u043d\u043a\u0438 \u0431\u043e\u043b\u044c\u0448\u043e\u0433\u043e \u0440\u0430\u0437\u043c\u0435\u0440\u0430 (\u0431\u043e\u043b\u044c\u0448\u0435 {value} Mb):")
    MSG_FLOATING = U(r"** \u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442 \u043f\u043b\u0430\u0432\u0430\u044e\u0449\u0438\u0435 \u0440\u0438\u0441\u0443\u043d\u043a\u0438. \u0412\u0441\u0442\u0440\u043e\u0439\u0442\u0435 \u0440\u0438\u0441\u0443\u043d\u043a\u0438 \u0432 \u0442\u0435\u043a\u0441\u0442:")
    MSG_PIXEL = U(r"*** \u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442 \u0440\u0438\u0441\u0443\u043d\u043a\u0438 \u0431\u043e\u043b\u044c\u0448\u043e\u0433\u043e \u0440\u0430\u0437\u043c\u0435\u0440\u0430 (\u0431\u043e\u043b\u044c\u0448\u0435 {value} \u043f\u0438\u043a\u0441\u0435\u043b\u0435\u0439):")
    MSG_SMALL_LABELS = U(r"\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u0441\u043e\u0434\u0435\u0440\u0436\u0438\u0442 \u043c\u0435\u043b\u043a\u0438\u0435 \u043d\u0430\u0434\u043f\u0438\u0441\u0438. \u0423\u0432\u0435\u043b\u0438\u0447\u044c\u0442\u0435 \u0438\u0445 \u0440\u0430\u0437\u043c\u0435\u0440 \u0438\u043b\u0438 \u0443\u0434\u0430\u043b\u0438\u0442\u0435:")

    def check(self) -> List[Finding]:
        findings = []
        images = self.doc_data.get("images", [])
        total_images_size_mb = sum(img.get("byte_size_mb", 0.0) for img in images)

        native232_docx=self.file_type=='docx' and self.doc_data.get('native_build')==232
        byte_violations=[im for im in images if isinstance(im.get('zip_local_uncompressed_size'),int) and im['zip_local_uncompressed_size']>30000000] if native232_docx else []
        if (bool(byte_violations) if native232_docx else total_images_size_mb > settings.IMAGE_FILE_SIZE_MAX_MB):
            findings.append(Finding(
                code="Pic.FileSizeTooLarge",
                module=ModuleType.PICTURES,
                severity=Severity.CRITICAL,
                message=self.MSG_FILE_SIZE.format(value=40 if native232_docx else settings.IMAGE_FILE_SIZE_MAX_MB),
                location={'images':[im['index']+1 for im in byte_violations]} if native232_docx else None,
                threshold=({'value':30000000,'unit':'bytes','measurement':'per referenced ZIP local-header declared uncompressed size','native_message_value':40,'native_message_unit':'Mb','actual_max_bytes':max(im['zip_local_uncompressed_size'] for im in byte_violations),'count_images':len(byte_violations)} if native232_docx else {"value": settings.IMAGE_FILE_SIZE_MAX_MB, "unit": "MB", "actual": total_images_size_mb}),
                skip_switch="SkipTestPic",
            ))

        floating_images_count = 0
        large_pixel_images_count = 0
        small_labels_count = 0
        floating_image_locations = []
        large_pixel_image_locations = []
        large_pixel_pages=set()
        floating_area=0.0;floating_area_supported=True
        for img_idx, img in enumerate(images):
            if img.get("placement", "inline") == "floating":
                floating_images_count += 1
                floating_image_locations.append(img.get("index", img_idx) + 1)
                area=img.get('native_display_area_mm2')
                if area is None:floating_area_supported=False
                elif img.get('wrap_mode')=='wrapNone':floating_area=f32(floating_area+area)
                elif img.get('wrap_mode')!='wrapSquare':floating_area_supported=False
            w = img.get("width_px")
            h = img.get("height_px")
            if w is not None and h is not None and w * h > settings.IMAGE_PIXEL_AREA_MAX:
                large_pixel_images_count += 1
                large_pixel_image_locations.append(img.get("index", img_idx) + 1)
                if "page_index" in img:large_pixel_pages.add(img["page_index"]+1)

        if native232_docx:
            small_labels_count=sum(l.get('small_geometry_candidate',False) for l in self.doc_data.get('labels',[]))
        elif self.file_type == "docx":
            for p in self.doc_data.get("paragraphs", []):
                for run in p.get("runs", []):
                    fs = run.get("font_size_pt")
                    if fs and fs < 9.0:
                        small_labels_count += len(run.get("text", ""))

        if floating_images_count > 0 and (not native232_docx or (floating_area_supported and floating_area>500)):
            findings.append(Finding(
                code="Pic.FloatingImages",
                module=ModuleType.PICTURES,
                severity=Severity.MAJOR,
                message=self.MSG_FLOATING,
                location={"images": floating_image_locations},
                threshold={"count_drawings": floating_images_count,**({'area_mm2':floating_area,'area_threshold_mm2':500,'area_measurement_supported':floating_area_supported,'measurement':'float32 aggregate wrapNone anchor area; wrapSquare contributes zero'} if native232_docx else {})},
                skip_switch="SkipTestPic",
            ))

        if large_pixel_images_count > 0:
            findings.append(Finding(
                code="Pic.PixelSizeTooLarge",
                module=ModuleType.PICTURES,
                severity=Severity.CRITICAL,
                message=self.MSG_PIXEL.format(value=settings.IMAGE_PIXEL_AREA_MAX),
                location={"images": large_pixel_image_locations, **({"pages":sorted(large_pixel_pages)} if large_pixel_pages else {})},
                threshold={"value": settings.IMAGE_PIXEL_AREA_MAX, "unit": "pixels_total", "measurement": "width_px * height_px", "count_images": large_pixel_images_count},
                skip_switch="SkipTestPic",
            ))

        if small_labels_count > 10:
            findings.append(Finding(
                code="Pic.SmallLabels",
                module=ModuleType.PICTURES,
                severity=Severity.INFO,
                message=self.MSG_SMALL_LABELS,
                location={'labels':[l['index']+1 for l in self.doc_data.get('labels',[]) if l.get('small_geometry_candidate')]} if native232_docx else None,
                threshold=({'count_labels':small_labels_count,'minimum_count_exclusive':10,'dimension_threshold_mm':2,'measurement':'textbox width or height strictly below2mm'} if native232_docx else {"count_chars": small_labels_count}),
                skip_switch="SkipTestPic",
            ))

        if native232_docx:
            floating_labels=[l for l in self.doc_data.get('labels',[]) if l.get('position')=='absolute']
            for code,message in [('Pic.FloatingShapes','** Документ содержит плавающие графические фигуры. Встройте фигуры в текст:'),('Pic.FloatingLabels','** Документ содержит плавающие надписи. Встройте надписи в текст:')]:
                if floating_labels:findings.append(Finding(code=code,module=ModuleType.PICTURES,severity=Severity.MAJOR,message=message,location={'labels':[l['index']+1 for l in floating_labels]},threshold={'count_labels':len(floating_labels),'measurement':'simple absolute VML textboxes; general shapes unimplemented'},skip_switch='SkipTestPic'))
        return findings
