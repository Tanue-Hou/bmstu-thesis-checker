from typing import List, Dict, Any
from .base import BaseChecker
from models.finding import Finding
from models.enums import Severity, ModuleType
from config import settings


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

        if total_images_size_mb > settings.IMAGE_FILE_SIZE_MAX_MB:
            findings.append(Finding(
                code="Pic.FileSizeTooLarge",
                module=ModuleType.PICTURES,
                severity=Severity.CRITICAL,
                message=self.MSG_FILE_SIZE.format(value=settings.IMAGE_FILE_SIZE_MAX_MB),
                threshold={"value": settings.IMAGE_FILE_SIZE_MAX_MB, "unit": "MB", "actual": total_images_size_mb},
                skip_switch="SkipTestPic",
            ))

        floating_images_count = 0
        large_pixel_images_count = 0
        small_labels_count = 0
        floating_image_locations = []
        large_pixel_image_locations = []
        for img_idx, img in enumerate(images):
            if img.get("placement", "inline") == "floating":
                floating_images_count += 1
                floating_image_locations.append(img.get("index", img_idx) + 1)
            w = img.get("width_px")
            if w and w > settings.IMAGE_PIXEL_THRESHOLD:
                large_pixel_images_count += 1
                large_pixel_image_locations.append(img.get("index", img_idx) + 1)

        if self.file_type == "docx":
            for p in self.doc_data.get("paragraphs", []):
                for run in p.get("runs", []):
                    fs = run.get("font_size_pt")
                    if fs and fs < 9.0:
                        small_labels_count += len(run.get("text", ""))

        if floating_images_count > 0:
            findings.append(Finding(
                code="Pic.FloatingImages",
                module=ModuleType.PICTURES,
                severity=Severity.MAJOR,
                message=self.MSG_FLOATING,
                location={"images": floating_image_locations},
                threshold={"count_drawings": floating_images_count},
                skip_switch="SkipTestPic",
            ))

        if large_pixel_images_count > 0:
            findings.append(Finding(
                code="Pic.PixelSizeTooLarge",
                module=ModuleType.PICTURES,
                severity=Severity.CRITICAL,
                message=self.MSG_PIXEL.format(value=int(settings.IMAGE_PIXEL_THRESHOLD)),
                location={"images": large_pixel_image_locations},
                threshold={"value": settings.IMAGE_PIXEL_THRESHOLD, "unit": "px", "count_images": large_pixel_images_count},
                skip_switch="SkipTestPic",
            ))

        if small_labels_count > 10:
            findings.append(Finding(
                code="Pic.SmallLabels",
                module=ModuleType.PICTURES,
                severity=Severity.INFO,
                message=self.MSG_SMALL_LABELS,
                threshold={"count_chars": small_labels_count},
                skip_switch="SkipTestPic",
            ))

        return findings
