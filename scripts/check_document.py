import argparse
import json
import os
import sys
from pathlib import Path


SERVICE_ROOT = Path(__file__).resolve().parent / "testvkr-service"
sys.path.insert(0, str(SERVICE_ROOT))

from checkers.dictionary import DictionaryChecker
from checkers.entry_document import EntryDocumentChecker
from checkers.pictures import PicturesChecker
from checkers.structure import StructureChecker
from checkers.word_format import WordFormatChecker
from parsers.docx_parser import DocxParser
from parsers.pdf_parser import PdfParser


SEVERITY_ORDER = {"critical": 0, "major": 1, "warning": 2, "info": 3}
FIX_PRIORITY_ORDER = {"must_fix": 0, "should_fix": 1, "manual_review": 2, "optional": 3}
SEVERITY_LABELS_ZH = {
    "critical": "严重",
    "major": "较严重",
    "warning": "警告",
    "info": "提示",
}
FIX_PRIORITY_LABELS_ZH = {
    "must_fix": "必改",
    "should_fix": "建议改",
    "manual_review": "需要人工确认",
    "optional": "可忽略",
}
MODULE_LABELS_ZH = {
    "entry": "入口/文件",
    "structure": "结构",
    "pictures": "图片/图形",
    "word_format": "Word/PDF 格式",
    "dictionary": "拼写/词典",
}


def load_rule_registry():
    rules_path = SERVICE_ROOT / "rules" / "rules_verified.json"
    if not rules_path.exists():
        return {}
    with rules_path.open("r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return {rule["rule_id"]: rule for rule in data.get("rules", [])}


def load_rule_guidance():
    guidance_path = SERVICE_ROOT / "rules" / "rule_guidance_zh.json"
    if not guidance_path.exists():
        return {"default": {}}
    with guidance_path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def parse_document(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return "docx", DocxParser(str(path)).parse_all()
    if suffix == ".pdf":
        return "pdf", PdfParser(str(path)).parse_all()
    raise ValueError("Only .docx and .pdf files are supported.")


def describe_location(location):
    if not location:
        return "未提供精确位置；请结合模块和阈值信息人工定位。"

    parts = []
    if "section" in location:
        parts.append(f"section {location['section']}")
    if "page" in location:
        parts.append(f"PDF/页面 {location['page']}")
    if "paragraph" in location:
        parts.append(f"段落 {location['paragraph']}")
    if "paragraphs" in location:
        values = location["paragraphs"]
        if isinstance(values, list):
            shown = ", ".join(str(v) for v in values[:20])
            suffix = "..." if len(values) > 20 else ""
            parts.append(f"段落 {shown}{suffix}")
    if "table" in location:
        parts.append(f"表格 {location['table']}")
    if "tables" in location:
        values = location["tables"]
        if isinstance(values, list):
            shown = ", ".join(str(v) for v in values[:20])
            suffix = "..." if len(values) > 20 else ""
            parts.append(f"表格 {shown}{suffix}")
    if "row" in location:
        parts.append(f"行 {location['row']}")
    if "table_rows" in location:
        rows = location["table_rows"]
        if isinstance(rows, list):
            shown = ", ".join(f"表{r.get('table')}行{r.get('row')}" for r in rows[:20])
            suffix = "..." if len(rows) > 20 else ""
            parts.append(f"表格行 {shown}{suffix}")
    if "image" in location:
        parts.append(f"图片 {location['image']}")
    if "images" in location:
        values = location["images"]
        if isinstance(values, list):
            shown = ", ".join(str(v) for v in values[:20])
            suffix = "..." if len(values) > 20 else ""
            parts.append(f"图片 {shown}{suffix}")
    if "bbox" in location:
        parts.append(f"bbox {location['bbox']}")
    if "text" in location:
        parts.append(f"文本片段：{location['text']}")

    return "；".join(parts) if parts else json.dumps(location, ensure_ascii=False)


def location_group_key(location):
    if not location:
        return "未定位"
    if "page" in location:
        return f"页面 {location['page']}"
    if "section" in location:
        return f"section {location['section']}"
    if "paragraph" in location or "paragraphs" in location:
        return "段落"
    if "table" in location or "tables" in location or "table_rows" in location:
        return "表格"
    if "image" in location or "images" in location:
        return "图片"
    return "其他位置"


def finding_to_dict(finding, rule_registry, rule_guidance):
    rule = rule_registry.get(finding.code, {})
    guidance = {**rule_guidance.get("default", {}), **rule_guidance.get(finding.code, {})}
    location = finding.location
    return {
        "rule_id": finding.code,
        "module": finding.module.value,
        "severity": finding.severity.value,
        "message": rule.get("observed_message") or finding.message,
        "russian_message": rule.get("observed_message") or finding.message,
        "title_zh": guidance.get("title_zh"),
        "explanation_zh": guidance.get("explanation_zh"),
        "trigger_reason_zh": guidance.get("trigger_reason_zh"),
        "fix_suggestion_zh": guidance.get("fix_suggestion_zh"),
        "word_path_zh": guidance.get("word_path_zh"),
        "fix_priority": guidance.get("fix_priority", "manual_review"),
        "affects_antiplagiarism": bool(guidance.get("affects_antiplagiarism")),
        "confidence": rule.get("confidence") or finding.confidence or "medium",
        "threshold": finding.threshold,
        "location": location,
        "location_summary_zh": describe_location(location),
        "skip_switch": finding.skip_switch,
        "source_va": rule.get("source_va"),
        "comparator": rule.get("comparator"),
        "sample_trigger": rule.get("sample_trigger", []),
    }


def build_groups(findings):
    groups = {
        "by_severity": {},
        "by_module": {},
        "by_fix_priority": {},
        "by_location": {},
        "antiplagiarism_related": [],
    }
    for item in findings:
        groups["by_severity"].setdefault(item["severity"], []).append(item["rule_id"])
        groups["by_module"].setdefault(item["module"], []).append(item["rule_id"])
        groups["by_fix_priority"].setdefault(item["fix_priority"], []).append(item["rule_id"])
        groups["by_location"].setdefault(location_group_key(item.get("location")), []).append(item["rule_id"])
        if item["affects_antiplagiarism"]:
            groups["antiplagiarism_related"].append(item["rule_id"])
    return groups


def build_fix_checklist(findings):
    checklist = {key: [] for key in FIX_PRIORITY_LABELS_ZH}
    for item in findings:
        key = item.get("fix_priority") or "manual_review"
        checklist.setdefault(key, []).append({
            "rule_id": item["rule_id"],
            "label_zh": FIX_PRIORITY_LABELS_ZH.get(key, key),
            "title_zh": item.get("title_zh"),
            "severity": item.get("severity"),
            "module": item.get("module"),
            "location_summary_zh": item.get("location_summary_zh"),
            "fix_suggestion_zh": item.get("fix_suggestion_zh"),
            "word_path_zh": item.get("word_path_zh"),
            "affects_antiplagiarism": item.get("affects_antiplagiarism"),
        })
    return checklist


def build_review_summary(findings):
    must_fix = [f for f in findings if f.get("fix_priority") == "must_fix"]
    antiplagiarism = [f for f in findings if f.get("affects_antiplagiarism")]
    critical_or_major = [f for f in findings if f.get("severity") in {"critical", "major"}]
    if must_fix or critical_or_major:
        status = "不建议直接提交，需要先处理必改项和较高严重度问题。"
    elif findings:
        status = "可以进入人工复核，但建议先处理报告中的建议项。"
    else:
        status = "未发现当前规则可识别的问题。"
    return {
        "status_zh": status,
        "must_fix_count": len(must_fix),
        "should_fix_count": sum(1 for f in findings if f.get("fix_priority") == "should_fix"),
        "manual_review_count": sum(1 for f in findings if f.get("fix_priority") == "manual_review"),
        "optional_count": sum(1 for f in findings if f.get("fix_priority") == "optional"),
        "antiplagiarism_related_count": len(antiplagiarism),
        "critical_or_major_count": len(critical_or_major),
    }


def sorted_findings(findings):
    return sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER.get(item.get("severity"), 99),
            FIX_PRIORITY_ORDER.get(item.get("fix_priority"), 99),
            item.get("module", ""),
            item.get("rule_id", ""),
        ),
    )


def check_file(path: Path, args):
    rule_registry = load_rule_registry()
    rule_guidance = load_rule_guidance()
    file_type, doc_data = parse_document(path)

    findings = []
    checkers = [EntryDocumentChecker(doc_data, file_type, args.work_type)]

    entry_findings = checkers[0].check()
    findings.extend(entry_findings)
    stop = any(f.code in {"Entry.DocumentEmpty", "Entry.DocumentProtected"} for f in entry_findings)

    if not stop:
        if not args.skip_structure:
            findings.extend(StructureChecker(doc_data, file_type, args.work_type).check())
        if not args.skip_pictures:
            findings.extend(PicturesChecker(doc_data, file_type, args.work_type).check())
        if not args.skip_word_format:
            findings.extend(WordFormatChecker(doc_data, file_type, args.work_type).check())
        if not args.skip_dictionary:
            findings.extend(DictionaryChecker(doc_data, file_type, args.work_type).check())

    finding_dicts = [finding_to_dict(f, rule_registry, rule_guidance) for f in findings]
    result = {
        "file": str(path),
        "file_type": file_type,
        "work_type": args.work_type,
        "summary": {
            "total": len(findings),
            "critical": sum(1 for f in findings if f.severity.value == "critical"),
            "major": sum(1 for f in findings if f.severity.value == "major"),
            "warning": sum(1 for f in findings if f.severity.value == "warning"),
            "info": sum(1 for f in findings if f.severity.value == "info"),
        },
        "review_summary": build_review_summary(finding_dicts),
        "groups": build_groups(finding_dicts),
        "fix_checklist": build_fix_checklist(finding_dicts),
        "findings": sorted_findings(finding_dicts),
    }
    return result


def render_markdown(result):
    lines = []
    def add(text=""):
        lines.append(text)

    add(f"# BMSTU 论文预审报告: {Path(result['file']).name}")
    add()
    summary = result["summary"]
    review = result.get("review_summary", {})
    add(
        f"问题总数：{summary['total']} "
        f"（critical {summary['critical']}，major {summary['major']}，"
        f"warning {summary['warning']}，info {summary['info']}）"
    )
    add()
    add("## 审阅结论")
    add(f"- 结论：{review.get('status_zh', '')}")
    add(f"- 必改项：{review.get('must_fix_count', 0)}")
    add(f"- 建议改：{review.get('should_fix_count', 0)}")
    add(f"- 需要人工确认：{review.get('manual_review_count', 0)}")
    add(f"- 影响查重/反抄袭适配：{review.get('antiplagiarism_related_count', 0)}")
    add()

    add("## 分组汇总")
    for title, group_name, label_map in [
        ("按严重程度", "by_severity", SEVERITY_LABELS_ZH),
        ("按模块", "by_module", MODULE_LABELS_ZH),
        ("按位置", "by_location", {}),
    ]:
        add(f"### {title}")
        group = result.get("groups", {}).get(group_name, {})
        if not group:
            add("- 无")
        for key, rule_ids in group.items():
            add(f"- {label_map.get(key, key)}：{len(rule_ids)} 项")
        add()

    add("## 修复清单")
    for key, title in FIX_PRIORITY_LABELS_ZH.items():
        items = result.get("fix_checklist", {}).get(key, [])
        add(f"### {title}（{len(items)}）")
        if not items:
            add("- 无")
        for item in items:
            antiplagiarism = "；影响查重" if item.get("affects_antiplagiarism") else ""
            add(
                f"- `{item['rule_id']}` {item.get('title_zh') or ''}："
                f"{item.get('fix_suggestion_zh') or ''} "
                f"位置：{item.get('location_summary_zh') or '未提供'}{antiplagiarism}"
            )
        add()

    add("## 问题详情")
    for item in result["findings"]:
        add(f"### {item['severity'].upper()} - {item['rule_id']}")
        add(f"- 模块：{MODULE_LABELS_ZH.get(item['module'], item['module'])}")
        add(f"- 中文问题：{item.get('title_zh') or ''}")
        add(f"- 中文解释：{item.get('explanation_zh') or ''}")
        add(f"- 触发原因：{item.get('trigger_reason_zh') or ''}")
        add(f"- 修改建议：{item.get('fix_suggestion_zh') or ''}")
        add(f"- Word 操作路径：{item.get('word_path_zh') or ''}")
        add(f"- 位置：{item.get('location_summary_zh') or ''}")
        add(f"- 是否影响查重/反抄袭：{'是' if item.get('affects_antiplagiarism') else '否'}")
        add(f"- 置信度：{item['confidence']}")
        add(f"- 俄文原提示：{item['russian_message']}")
        if item.get("threshold") is not None:
            add(f"- 阈值：`{json.dumps(item['threshold'], ensure_ascii=False)}`")
        if item.get("location") is not None:
            add(f"- 原始位置：`{json.dumps(item['location'], ensure_ascii=False)}`")
        if item.get("source_va"):
            add(f"- 来源：`{item['source_va']}`")
        add()
    return "\n".join(lines)


def print_markdown(result):
    print(render_markdown(result))


def write_docx_report(result, out_path):
    from docx import Document
    from docx.shared import Pt

    document = Document()
    styles = document.styles
    styles["Normal"].font.name = "Microsoft YaHei"
    styles["Normal"].font.size = Pt(10)

    document.add_heading(f"BMSTU 论文预审报告：{Path(result['file']).name}", level=1)
    summary = result["summary"]
    review = result.get("review_summary", {})
    document.add_paragraph(
        f"问题总数：{summary['total']}；严重：{summary['critical']}；"
        f"较严重：{summary['major']}；警告：{summary['warning']}；提示：{summary['info']}。"
    )
    document.add_heading("审阅结论", level=2)
    document.add_paragraph(review.get("status_zh", ""))
    document.add_paragraph(
        f"必改 {review.get('must_fix_count', 0)} 项；建议改 {review.get('should_fix_count', 0)} 项；"
        f"人工确认 {review.get('manual_review_count', 0)} 项；"
        f"影响查重/反抄袭适配 {review.get('antiplagiarism_related_count', 0)} 项。"
    )

    document.add_heading("修复清单", level=2)
    for key, title in FIX_PRIORITY_LABELS_ZH.items():
        items = result.get("fix_checklist", {}).get(key, [])
        document.add_heading(f"{title}（{len(items)}）", level=3)
        if not items:
            document.add_paragraph("无")
            continue
        table = document.add_table(rows=1, cols=5)
        table.style = "Table Grid"
        headers = ["规则", "问题", "位置", "建议", "Word 操作路径"]
        for idx, header in enumerate(headers):
            table.rows[0].cells[idx].text = header
        for item in items:
            row = table.add_row().cells
            row[0].text = item.get("rule_id", "")
            row[1].text = item.get("title_zh") or ""
            row[2].text = item.get("location_summary_zh") or ""
            row[3].text = item.get("fix_suggestion_zh") or ""
            row[4].text = item.get("word_path_zh") or ""

    document.add_heading("问题详情", level=2)
    for item in result["findings"]:
        document.add_heading(f"{item['severity'].upper()} - {item['rule_id']}", level=3)
        details = [
            ("模块", MODULE_LABELS_ZH.get(item["module"], item["module"])),
            ("中文问题", item.get("title_zh") or ""),
            ("中文解释", item.get("explanation_zh") or ""),
            ("触发原因", item.get("trigger_reason_zh") or ""),
            ("修改建议", item.get("fix_suggestion_zh") or ""),
            ("Word 操作路径", item.get("word_path_zh") or ""),
            ("位置", item.get("location_summary_zh") or ""),
            ("是否影响查重/反抄袭", "是" if item.get("affects_antiplagiarism") else "否"),
            ("置信度", item.get("confidence") or ""),
            ("俄文原提示", item.get("russian_message") or ""),
        ]
        if item.get("threshold") is not None:
            details.append(("阈值", json.dumps(item["threshold"], ensure_ascii=False)))
        if item.get("source_va"):
            details.append(("来源", item["source_va"]))
        table = document.add_table(rows=0, cols=2)
        table.style = "Table Grid"
        for key, value in details:
            row = table.add_row().cells
            row[0].text = key
            row[1].text = str(value)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(out_path))
    return out_path


def write_report_bundle(result, report_dir):
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    base = Path(result["file"]).stem
    paths = {
        "json": report_dir / f"{base}_report.json",
        "markdown": report_dir / f"{base}_report.md",
        "docx": report_dir / f"{base}_report.docx",
    }
    paths["json"].write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["markdown"].write_text(render_markdown(result), encoding="utf-8")
    write_docx_report(result, paths["docx"])
    return {key: str(value) for key, value in paths.items()}


def main():
    parser = argparse.ArgumentParser(description="Check a DOCX/PDF thesis with the BMSTU rules engine.")
    parser.add_argument("file", help="Path to a .docx or .pdf file.")
    parser.add_argument("--work-type", default="bachelor", choices=["bachelor", "specialist", "master", "phd"])
    parser.add_argument("--skip-structure", action="store_true")
    parser.add_argument("--skip-pictures", action="store_true")
    parser.add_argument("--skip-word-format", action="store_true")
    parser.add_argument("--skip-dictionary", action="store_true")
    parser.add_argument("--format", choices=["json", "markdown", "docx"], default="json")
    parser.add_argument("--out", help="Optional output file.")
    parser.add_argument("--report-dir", help="Optional directory for report.json, report.md, and report.docx.")
    args = parser.parse_args()

    path = Path(args.file).expanduser().resolve()
    result = check_file(path, args)
    if args.report_dir:
        result["report_paths"] = write_report_bundle(result, args.report_dir)

    if args.format == "json":
        text = json.dumps(result, ensure_ascii=False, indent=2)
    elif args.format == "markdown":
        text = render_markdown(result)
    else:
        if not args.out:
            raise SystemExit("--out is required when --format docx is used.")
        write_docx_report(result, args.out)
        return

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
