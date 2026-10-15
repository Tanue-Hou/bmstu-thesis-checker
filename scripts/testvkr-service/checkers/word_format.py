from typing import List, Dict, Any
from .base import BaseChecker
from models.finding import Finding
from models.enums import Severity, ModuleType
from config import settings
from .native_font_counts import count_font_candidates

class WordFormatChecker(BaseChecker):
    def check(self) -> List[Finding]:
        findings = []

        if self.file_type == 'docx':
            self._check_docx_margins_and_page(findings)
            self._check_docx_paragraphs(findings)
            self._check_docx_tables(findings)
        elif self.file_type == 'pdf':
            self._check_pdf_format(findings)

        return findings

    def _check_docx_margins_and_page(self, findings: List[Finding]):
        sections = self.doc_data.get('sections', [])
        for idx, sec in enumerate(sections):
            page = idx + 1
            margin_tolerance = settings.MARGIN_TOLERANCE_PHD_MM if self.work_type=='phd' else settings.MARGIN_TOLERANCE_MM
            def margin_profile(axis):
                targets={'left':settings.MARGIN_LEFT_PHD_MM,'right':settings.MARGIN_RIGHT_MM,'top':settings.MARGIN_TOP_MM,'bottom':settings.MARGIN_BOTTOM_MM}
                return (self.work_type=='phd' and self.doc_data.get('native_graduate_scope_supported',False)
                    and len(sections)==1 and not sec.get('gutter_mm',0)
                    and all(sec.get('margin_'+key+'_mm') is not None and abs(sec['margin_'+key+'_mm']-value)<=margin_tolerance for key,value in targets.items() if key!=axis))

            # 1. Page Size A4 (Index 68, threshold > 0)
            w = sec.get('page_width_mm')
            h = sec.get('page_height_mm')
            if w is not None and h is not None:
                if abs(w - settings.PAGE_WIDTH_MM) > settings.PAGE_SIZE_TOLERANCE_MM or abs(h - settings.PAGE_HEIGHT_MM) > settings.PAGE_SIZE_TOLERANCE_MM:
                    findings.append(Finding(
                        code="Word.PageSizeNotA4",
                        module=ModuleType.WORD_FORMAT,
                        severity=Severity.INFO,
                        message="Документ содержит страницы, размеры которых не соответствуют формату А4.",
                        location={"section": page},
                        threshold={"expected": "210x297mm", "actual": f"{w:.1f}x{h:.1f}mm"},
                        skip_switch="SkipTestWord"
                    ))

            # 2. Left Margin & Indent (Index 69, threshold > 0)
            left_margin = sec.get('margin_left_mm')
            expected_left = settings.MARGIN_LEFT_PHD_MM if self.work_type=='phd' else settings.MARGIN_LEFT_MM
            margin_probe_supported = margin_profile('left')
            if left_margin is not None and abs(left_margin - expected_left) > margin_tolerance:
                findings.append(Finding(
                    code="Word.LeftMarginInvalid",
                    module=ModuleType.WORD_FORMAT,
                    severity=Severity.INFO,
                    message="Документ содержит страницы, размеры левого поля на которых не соответствуют требованиям или отступ первой строки абзаца не равен 1.25…1.27 см:",
                    location={"section": page},
                    threshold={"value": expected_left, "unit": "mm", "actual": left_margin,"native_margin_probe_supported":margin_probe_supported},
                    skip_switch="SkipTestWord"
                ))

            # 3. Right Margin (Index 70, threshold > 0)
            right_margin = sec.get('margin_right_mm')
            if right_margin is not None and abs(right_margin - settings.MARGIN_RIGHT_MM) > margin_tolerance:
                findings.append(Finding(
                    code="Word.RightMarginInvalid",
                    module=ModuleType.WORD_FORMAT,
                    severity=Severity.INFO,
                    message="Документ содержит страницы, размеры правого поля на которых не соответствуют требованиям, или нет знаков препинаний в конце коротких строк, или не используется выравнивание текста по ширине:",
                    location={"section": page},
                    threshold={"value": settings.MARGIN_RIGHT_MM, "unit": "mm", "actual": right_margin,'native_margin_probe_supported':margin_profile('right')},
                    skip_switch="SkipTestWord"
                ))

            # 4. Top Margin (Index 71, threshold > 0)
            top_margin = sec.get('margin_top_mm')
            if top_margin is not None and abs(top_margin - settings.MARGIN_TOP_MM) > margin_tolerance:
                findings.append(Finding(
                    code="Word.TopMarginInvalid",
                    module=ModuleType.WORD_FORMAT,
                    severity=Severity.INFO,
                    message="Документ содержит страницы, размеры верхнего поля на которых не соответствуют требованиям:",
                    location={"section": page},
                    threshold={"value": settings.MARGIN_TOP_MM, "unit": "mm", "actual": top_margin,'native_margin_probe_supported':margin_profile('top')},
                    skip_switch="SkipTestWord"
                ))

            # 5. Bottom Margin (Index 72, threshold > 0)
            bottom_margin = sec.get('margin_bottom_mm')
            if bottom_margin is not None and abs(bottom_margin - settings.MARGIN_BOTTOM_MM) > margin_tolerance:
                findings.append(Finding(
                    code="Word.BottomMarginInvalid",
                    module=ModuleType.WORD_FORMAT,
                    severity=Severity.INFO,
                    message="Документ содержит страницы, размеры нижнего поля на которых не соответствуют требованиям:",
                    location={"section": page},
                    threshold={"value": settings.MARGIN_BOTTOM_MM, "unit": "mm", "actual": bottom_margin,'native_margin_probe_supported':margin_profile('bottom')},
                    skip_switch="SkipTestWord"
                ))

            # 6. Gutter Size (Index 76, threshold > 0)
            gutter = sec.get('gutter_mm', 0.0)
            if gutter and gutter > 0.01:
                findings.append(Finding(
                    code="Word.GutterNotZero",
                    module=ModuleType.WORD_FORMAT,
                    severity=Severity.INFO,
                    message="Размер переплета в параметрах страницы должен равняться нулю.",
                    location={"section": page},
                    threshold={"value": 0.0, "unit": "mm", "actual": gutter},
                    skip_switch="SkipTestWord"
                ))

            # 7. Header/Footer distances (Index 77, threshold > 0)
            hdr = sec.get('header_distance_cm')
            ftr = sec.get('footer_distance_cm')
            if (hdr is not None and abs(hdr - settings.HEADER_FOOTER_DISTANCE_CM) > settings.HEADER_FOOTER_TOLERANCE_CM) or \
               (ftr is not None and abs(ftr - settings.HEADER_FOOTER_DISTANCE_CM) > settings.HEADER_FOOTER_TOLERANCE_CM):
                findings.append(Finding(
                    code="Word.HeaderFooterDistanceInvalid",
                    module=ModuleType.WORD_FORMAT,
                    severity=Severity.INFO,
                    message="Размеры колонтитулов должны быть 1,25 см.",
                    location={"section": page},
                    threshold={"value": settings.HEADER_FOOTER_DISTANCE_CM, "unit": "cm", "actual_hdr": hdr, "actual_ftr": ftr},
                    skip_switch="SkipTestWord"
                ))

    def _check_docx_paragraphs(self, findings: List[Finding]):
        paragraphs = self.doc_data.get('paragraphs', [])

        # Run-level violation counters (characters count)
        sz_small_count = 0
        sz_large_count = 0
        scale_small_count = 0
        scale_large_count = 0
        color_not_black_count = 0
        bg_not_white_count = 0
        compressed_spacing_count = 0
        transparent_count = 0
        low_contrast_count = 0

        # Paragraph-level violations (threshold > 0)
        line_spacing_violations = []
        first_line_indent_violations = []
        left_indent_violations = []
        right_indent_violations = []
        leading_whitespace_violations = []
        alignment_violations = []

        for idx, p in enumerate(paragraphs):
            text = p.get('text', '')
            text_strip = text.strip()
            if not text_strip:
                continue

            # Leading whitespace check (Index 83, threshold > 0)
            if text.startswith(' ') or text.startswith('\t'):
                leading_whitespace_violations.append(idx)

            # Line Spacing (Index 80, threshold > 0)
            if p['line_spacing_type'] == 'multiplier':
                if abs(p['line_spacing'] - settings.LINE_SPACING_BODY) > settings.LINE_SPACING_TOLERANCE:
                    # Ignore short paragraphs like headings
                    if len(text_strip) > 40:
                        line_spacing_violations.append(idx)

            # First Line Indent (Index 81, threshold > 0)
            if p['alignment'] != 'center' and len(text_strip) > 40:
                indent = p.get('first_line_indent_cm', 0.0)
                if abs(indent - settings.FIRST_LINE_INDENT_CM) > settings.FIRST_LINE_INDENT_TOLERANCE_CM:
                    first_line_indent_violations.append(idx)

            # Left/Right Indents (Index 78/79, threshold > 0)
            if abs(p['left_indent_cm']) > settings.PARAGRAPH_INDENT_TOLERANCE_CM:
                left_indent_violations.append(idx)
            if abs(p['right_indent_cm']) > settings.PARAGRAPH_INDENT_TOLERANCE_CM:
                right_indent_violations.append(idx)

            # Alignment (Index 82, threshold > 0)
            if p['alignment'] not in ['justify', 'center']:
                if len(text_strip) > 60: # Only check long body paragraphs
                    alignment_violations.append(idx)

            # Run level formatting checks
            for run in p.get('runs', []):
                run_text = run['text'].strip()
                if not run_text:
                    continue

                # Hidden text / vanish (Index 19, threshold > 10)
                if run.get('is_hidden'):
                    transparent_count += len(run_text)

                # Font size (Index 11, threshold > 10)
                fs = run.get('font_size_pt')
                if fs is not None:
                    if fs < settings.FONT_SIZE_MIN_PT:
                        sz_small_count += len(run_text)
                    elif fs > settings.FONT_SIZE_MAX_PT: # (Index 13, threshold > 10)
                        sz_large_count += len(run_text)

                # Font scale (Index 16/18, threshold > 10)
                scale = run.get('scale_pct', 100.0)
                if scale < settings.FONT_SCALE_MIN_PCT:
                    scale_small_count += len(run_text)
                elif scale > settings.FONT_SCALE_MAX_PCT:
                    scale_large_count += len(run_text)

                # Character Spacing (Index 14, threshold > 10)
                spacing = run.get('spacing_pt', 0.0)
                if spacing < 0.0:
                    compressed_spacing_count += len(run_text)

                # Color (not black) (Index 23, threshold > 10)
                color = run.get('color_hex')
                if color and color.upper() not in ['000000', 'AUTO']:
                    color_not_black_count += len(run_text)
                    # Low contrast detection (Index 1, threshold > 10)
                    if color.upper() in ['CCCCCC', 'D3D3D3', 'E0E0E0', 'F0F0F0', 'FFFFFF']:
                        low_contrast_count += len(run_text)

                # Background / shading (not white/none) (Index 24, threshold > 10)
                bg = run.get('bg_color_hex')
                if bg and bg.upper() not in ['FFFFFF', 'AUTO', '00000000']:
                    bg_not_white_count += len(run_text)

        # Native size counters include table cells. Deduplicate repeated proxies for merged cells.
        table_small_count=table_large_count=0
        seen_table_paragraphs=set()
        for ti,table in enumerate(self.doc_data.get('tables',[])):
            for ri,row in enumerate(table.get('rows',[])):
                for ci,cell in enumerate(row.get('cells',[])):
                    for pi,paragraph in enumerate(cell.get('paragraphs',[])):
                        identity=paragraph.get('xml_path',(ti,ri,ci,pi))
                        if identity in seen_table_paragraphs:continue
                        seen_table_paragraphs.add(identity)
                        for run in paragraph.get('runs',[]):
                            size=run.get('font_size_pt');count=len(run.get('text','').strip())
                            if size is not None and size<settings.FONT_SIZE_MIN_PT:table_small_count+=count
                            if size is not None and size>settings.FONT_SIZE_MAX_PT:table_large_count+=count
        sz_small_count+=table_small_count;sz_large_count+=table_large_count
        native_font_mode=self.doc_data.get('native_build')==232
        if native_font_mode:
            counts,records=count_font_candidates(self.doc_data,settings.FONT_SIZE_MIN_PT,settings.FONT_SIZE_MAX_PT)
            self.doc_data['native_font_candidates']=records;self.doc_data['native_font_counters']=counts
            self.doc_data['native232_font_profile_supported']=bool(self.doc_data.get('native232_font_profile_supported')) and all(r['font_size_pt'] is not None and r['font_size_pt']>0 for r in records if r['text'])
            sz_small_count=counts['small'];sz_large_count=counts['large'];table_small_count=counts['table_small'];table_large_count=counts['table_large']
        # Append findings if counters exceed 10 characters (threshold > 10)
        if sz_small_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.FontSizeTooSmall",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.MAJOR,
                message=f"В документе много символов, размер которых меньше {settings.FONT_SIZE_MIN_PT} пт",
                threshold={"value": settings.FONT_SIZE_MIN_PT, "unit": "pt", "count_chars": sz_small_count,'table_count_chars':table_small_count,**({'measurement':'UTF16 units including whitespace','minimum_exclusive_pt':settings.FONT_SIZE_MIN_PT/2,'maximum_exclusive_pt':settings.FONT_SIZE_MIN_PT,'minimum_count_exclusive':settings.FONT_VIOLATION_MIN_CHARS} if native_font_mode else {})},
                location={'native_font_runs':[r['index'] for r in records if r['bucket']=='small']} if native_font_mode else None,
                skip_switch="SkipTestWord"
            ))

        if sz_large_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.FontSizeTooLarge",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="В документе много символов, размер которых превышает требования",
                threshold={"value": settings.FONT_SIZE_MAX_PT, "unit": "pt", "count_chars": sz_large_count,'table_count_chars':table_large_count,**({'measurement':'UTF16 units including whitespace; textbox requires prior count >100','minimum_count_exclusive':settings.FONT_VIOLATION_MIN_CHARS} if native_font_mode else {})},
                location={'native_font_runs':[r['index'] for r in records if r['bucket']=='large']} if native_font_mode else None,
                skip_switch="SkipTestWord"
            ))

        if scale_small_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.FontScaleTooSmall",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.MAJOR,
                message=f"В документе много символов, у которых масштаб шрифта меньше {settings.FONT_SCALE_MIN_PCT}%:",
                threshold={"value": settings.FONT_SCALE_MIN_PCT, "unit": "%", "count_chars": scale_small_count},
                skip_switch="SkipTestWord"
            ))

        if scale_large_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.FontScaleTooLarge",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message=f"В документе много символов, у которых масштаб шрифта больше {settings.FONT_SCALE_MAX_PCT}%:",
                threshold={"value": settings.FONT_SCALE_MAX_PCT, "unit": "%", "count_chars": scale_large_count},
                skip_switch="SkipTestWord"
            ))

        if compressed_spacing_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.CompressedSpacing",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.MAJOR,
                message="** В документе много уплотненных символов:",
                threshold={"count_chars": compressed_spacing_count},
                skip_switch="SkipTestWord"
            ))

        if transparent_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.TransparentText",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.MAJOR,
                message="** В документе много прозрачных и полупрозрачных символов:",
                threshold={"count_chars": transparent_count},
                skip_switch="SkipTestWord"
            ))

        if low_contrast_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.LowContrastText",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.MAJOR,
                message="** В документе много символов, цвет которых плохо различим от цвета фона:",
                threshold={"count_chars": low_contrast_count},
                skip_switch="SkipTestWord"
            ))

        if color_not_black_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.TextColorNotBlack",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="В документе много символов, цвет которых отличается от черного:",
                threshold={"count_chars": color_not_black_count},
                skip_switch="SkipTestWord"
            ))

        if bg_not_white_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.TextBackgroundNotWhite",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="В документе много символов, цвет фона которых отличается от белого:",
                threshold={"count_chars": bg_not_white_count},
                skip_switch="SkipTestWord"
            ))

        # Paragraph style violations (threshold > 0)
        if len(line_spacing_violations) > 0:
            findings.append(Finding(
                code="Word.LineSpacingInvalid",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message=f"Междустрочный интервал в абзацах должен быть равен {settings.LINE_SPACING_BODY} строки (в таблицах одинарный):",
                location={"paragraphs": [i + 1 for i in line_spacing_violations]},
                threshold={"value": settings.LINE_SPACING_BODY, "unit": "multiplier", "count_paragraphs": len(line_spacing_violations)},
                skip_switch="SkipTestWord"
            ))

        if len(first_line_indent_violations) > 0:
            findings.append(Finding(
                code="Word.FirstLineIndentInvalid",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="Отступ первой строки в абзаце должен быть 1,25 см. (при выравнивании строк а абзаце по центру - 0 см.):",
                location={"paragraphs": [i + 1 for i in first_line_indent_violations]},
                threshold={"value": settings.FIRST_LINE_INDENT_CM, "unit": "cm", "count_paragraphs": len(first_line_indent_violations)},
                skip_switch="SkipTestWord"
            ))

        if len(left_indent_violations) > 0:
            findings.append(Finding(
                code="Word.LeftIndentInvalid",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="Левый отступ в абзацах должен быть равен 0 см.:",
                location={"paragraphs": [i + 1 for i in left_indent_violations]},
                threshold={"count_paragraphs": len(left_indent_violations)},
                skip_switch="SkipTestWord"
            ))

        if len(right_indent_violations) > 0:
            findings.append(Finding(
                code="Word.RightIndentInvalid",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="Правый отступ в абзацах должен быть равен 0 см.:",
                location={"paragraphs": [i + 1 for i in right_indent_violations]},
                threshold={"count_paragraphs": len(right_indent_violations)},
                skip_switch="SkipTestWord"
            ))

        if len(leading_whitespace_violations) > 0:
            findings.append(Finding(
                code="Word.LeadingWhitespace",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="В начале абзаца пробельные символы не ставятся:",
                location={"paragraphs": [i + 1 for i in leading_whitespace_violations]},
                threshold={"count_paragraphs": len(leading_whitespace_violations)},
                skip_switch="SkipTestWord"
            ))

        if len(alignment_violations) > 0:
            findings.append(Finding(
                code="Word.AlignmentNotJustified",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="Строки в абзацах должны выравниваться по ширине (нумерованные заголовки и текст) или по центру (заголовки структурных элементов, рисунки, названия рисунков):",
                location={"paragraphs": [i + 1 for i in alignment_violations]},
                threshold={"count_paragraphs": len(alignment_violations)},
                skip_switch="SkipTestWord"
            ))

    def _check_docx_tables(self, findings: List[Finding]):
        tables = self.doc_data.get('tables', [])

        row_height_violations = 0
        exact_height_violations = 0
        table_wrapping_violations = 0
        table_line_spacing_violations = 0
        row_height_locations = []
        exact_height_locations = []
        table_wrapping_locations = []
        table_line_spacing_locations = []
        color_not_black_count = 0
        bg_not_white_count = 0

        for t_idx, t in enumerate(tables):
            # 1. Text wrapping (Index 62, threshold > 0)
            if t.get('has_wrapping'):
                table_wrapping_violations += 1
                table_wrapping_locations.append(t_idx + 1)

            for r_idx, r in enumerate(t.get('rows', [])):
                h = r.get('height_mm')
                rule = r.get('height_rule')

                # 2. Row height >= 8 mm (Index 60, threshold > 0)
                if h is not None:
                    if h < settings.TABLE_ROW_HEIGHT_MIN_MM:
                        row_height_violations += 1
                        row_height_locations.append({"table": t_idx + 1, "row": r_idx + 1})

                    # 3. Exact height rule (Index 61, threshold > 0)
                    if rule == 'exact':
                        exact_height_violations += 1
                        exact_height_locations.append({"table": t_idx + 1, "row": r_idx + 1})

                for c_idx, c in enumerate(r.get('cells', [])):
                    cell_bg = c.get('bg_color_hex')

                    for cp in c.get('paragraphs', []):
                        # Table cell line spacing must be 1.0 (single)
                        line_spacing = cp.get('line_spacing')
                        if line_spacing is not None and cp.get('line_spacing_type', 'multiplier') == 'multiplier':
                            if abs(line_spacing - settings.LINE_SPACING_TABLE) > settings.LINE_SPACING_TOLERANCE:
                                if len(cp.get('text', '').strip()) > 5:
                                    table_line_spacing_violations += 1
                                    table_line_spacing_locations.append({"table": t_idx + 1, "row": r_idx + 1})

                        for run in cp.get('runs', []):
                            run_text = run['text'].strip()
                            if not run_text:
                                continue

                            color = run.get('color_hex')
                            if color and color.upper() not in ['000000', 'AUTO']:
                                color_not_black_count += len(run_text)

                            bg = run.get('bg_color_hex') or cell_bg
                            if bg and bg.upper() not in ['FFFFFF', 'AUTO', '00000000']:
                                bg_not_white_count += len(run_text)

        # Add findings
        if table_wrapping_violations > 0:
            findings.append(Finding(
                code="Word.TableWrappingEnabled",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.MAJOR,
                message="** Документ содержит таблицы с включенным обтеканием текстом:",
                location={"tables": table_wrapping_locations},
                threshold={"count_tables": table_wrapping_violations},
                skip_switch="SkipTestWord"
            ))

        if row_height_violations > 0:
            findings.append(Finding(
                code="Word.TableRowHeightTooSmall",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.MAJOR,
                message=f"** Высота строк в таблицах должна быть не менее {settings.TABLE_ROW_HEIGHT_MIN_MM} мм.:",
                location={"table_rows": row_height_locations},
                threshold={"value": settings.TABLE_ROW_HEIGHT_MIN_MM, "unit": "mm", "count_rows": row_height_violations},
                skip_switch="SkipTestWord"
            ))

        if exact_height_violations > 0:
            findings.append(Finding(
                code="Word.TableSuspiciousHeightRule",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.MAJOR,
                message="** Замечена подозрительная высота строк в таблицах документа. Переключите указание высоты строк из режима \"Точно\" на \"Минимум\":",
                location={"table_rows": exact_height_locations},
                threshold={"count_rows": exact_height_violations},
                skip_switch="SkipTestWord"
            ))

        if color_not_black_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.TableTextColorNotBlack",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="В таблицах, имеющихся в документе, много символов, цвет которых отличается от черного:",
                threshold={"count_chars": color_not_black_count},
                skip_switch="SkipTestWord"
            ))

        if bg_not_white_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.TableTextBackgroundNotWhite",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="В таблицах, имеющихся в документе, много символов, цвет фона которых отличается от белого:",
                threshold={"count_chars": bg_not_white_count},
                skip_switch="SkipTestWord"
            ))

        if table_line_spacing_violations > 0:
            findings.append(Finding(
                code="Word.LineSpacingInvalid",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message=f"Междустрочный интервал в абзацах должен быть равен {settings.LINE_SPACING_BODY} строки (в таблицах одинарный):",
                location={"table_rows": table_line_spacing_locations},
                threshold={"value": settings.LINE_SPACING_TABLE, "unit": "multiplier", "count_paragraphs": table_line_spacing_violations},
                skip_switch="SkipTestWord"
            ))

    def _check_pdf_format(self, findings: List[Finding]):
        pages = self.doc_data.get('pages', [])
        for p in pages:
            w = p['width_mm']
            h = p['height_mm']
            if abs(w - settings.PAGE_WIDTH_MM) > settings.PAGE_SIZE_TOLERANCE_MM or abs(h - settings.PAGE_HEIGHT_MM) > settings.PAGE_SIZE_TOLERANCE_MM:
                findings.append(Finding(
                    code="Word.PageSizeNotA4",
                    module=ModuleType.WORD_FORMAT,
                    severity=Severity.INFO,
                    message="Документ содержит страницы, размеры которых не соответствуют формату А4.",
                    location={"page": p['index'] + 1},
                    threshold={"expected": "210x297mm", "actual": f"{w:.1f}x{h:.1f}mm"},
                    skip_switch="SkipTestWord"
                ))

        spans = self.doc_data.get('spans', [])
        sz_small_count = 0
        color_not_black_count = 0
        small_pages=set();color_pages=set()

        for span in spans:
            text = span['text'].strip()
            if not text:
                continue

            fs = span['font_size_pt']
            if fs < settings.FONT_SIZE_MIN_PT:
                sz_small_count += len(text);small_pages.add(span['page_index']+1)
            # Native PDF path has no established upper-font predicate.

            color = span['color_hex']
            if color != "000000":
                color_not_black_count += len(text);color_pages.add(span['page_index']+1)

        if sz_small_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.FontSizeTooSmall",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.MAJOR,
                message=f"В документе много символов, размер которых меньше {settings.FONT_SIZE_MIN_PT} пт",
                threshold={"value": settings.FONT_SIZE_MIN_PT, "unit": "pt", "count_chars": sz_small_count},
                location={"pages":sorted(small_pages)},
                skip_switch="SkipTestWord"
            ))

        if color_not_black_count > settings.FONT_VIOLATION_MIN_CHARS:
            findings.append(Finding(
                code="Word.TextColorNotBlack",
                module=ModuleType.WORD_FORMAT,
                severity=Severity.INFO,
                message="В документе много символов, цвет которых отличается от черного:",
                threshold={"count_chars": color_not_black_count},
                location={"pages":sorted(color_pages)},
                skip_switch="SkipTestWord"
            ))
