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
        "antiplagiarism_related": [],
    }
    for item in findings:
        groups["by_severity"].setdefault(item["severity"], []).append(item["rule_id"])
        groups["by_module"].setdefault(item["module"], []).append(item["rule_id"])
        groups["by_fix_priority"].setdefault(item["fix_priority"], []).append(item["rule_id"])
        if item["affects_antiplagiarism"]:
            groups["antiplagiarism_related"].append(item["rule_id"])
    return groups


def build_fix_checklist(findings):
    labels = {
        "must_fix": "必改",
        "should_fix": "建议改",
        "manual_review": "需要人工确认",
        "optional": "可忽略",
    }
    checklist = {key: [] for key in labels}
    for item in findings:
        key = item.get("fix_priority") or "manual_review"
        checklist.setdefault(key, []).append({
            "rule_id": item["rule_id"],
            "label_zh": labels.get(key, key),
            "title_zh": item.get("title_zh"),
            "location_summary_zh": item.get("location_summary_zh"),
            "fix_suggestion_zh": item.get("fix_suggestion_zh"),
        })
    return checklist


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
        "groups": build_groups(finding_dicts),
        "fix_checklist": build_fix_checklist(finding_dicts),
        "findings": finding_dicts,
    }
    return result


def print_markdown(result):
    print(f"# BMSTU 论文预审报告: {Path(result['file']).name}")
    print()
    summary = result["summary"]
    print(
        f"问题总数：{summary['total']} "
        f"（critical {summary['critical']}，major {summary['major']}，"
        f"warning {summary['warning']}，info {summary['info']}）"
    )
    print()
    print("## 修复清单")
    priority_titles = [
        ("must_fix", "必改"),
        ("should_fix", "建议改"),
        ("manual_review", "需要人工确认"),
        ("optional", "可忽略"),
    ]
    for key, title in priority_titles:
        items = result.get("fix_checklist", {}).get(key, [])
        print(f"### {title}（{len(items)}）")
        if not items:
            print("- 无")
        for item in items:
            print(
                f"- `{item['rule_id']}` {item.get('title_zh') or ''}："
                f"{item.get('fix_suggestion_zh') or ''} "
                f"位置：{item.get('location_summary_zh') or '未提供'}"
            )
        print()

    print("## 问题详情")
    for item in result["findings"]:
        print(f"### {item['severity'].upper()} - {item['rule_id']}")
        print(f"- 模块：{item['module']}")
        print(f"- 中文问题：{item.get('title_zh') or ''}")
        print(f"- 中文解释：{item.get('explanation_zh') or ''}")
        print(f"- 触发原因：{item.get('trigger_reason_zh') or ''}")
        print(f"- 修改建议：{item.get('fix_suggestion_zh') or ''}")
        print(f"- Word 操作路径：{item.get('word_path_zh') or ''}")
        print(f"- 位置：{item.get('location_summary_zh') or ''}")
        print(f"- 置信度：{item['confidence']}")
        print(f"- 俄文原提示：{item['russian_message']}")
        if item.get("threshold") is not None:
            print(f"- 阈值：`{json.dumps(item['threshold'], ensure_ascii=False)}`")
        if item.get("location") is not None:
            print(f"- 原始位置：`{json.dumps(item['location'], ensure_ascii=False)}`")
        if item.get("source_va"):
            print(f"- 来源：`{item['source_va']}`")
        print()


def main():
    parser = argparse.ArgumentParser(description="Check a DOCX/PDF thesis with the BMSTU rules engine.")
    parser.add_argument("file", help="Path to a .docx or .pdf file.")
    parser.add_argument("--work-type", default="bachelor", choices=["bachelor", "specialist", "master", "phd"])
    parser.add_argument("--skip-structure", action="store_true")
    parser.add_argument("--skip-pictures", action="store_true")
    parser.add_argument("--skip-word-format", action="store_true")
    parser.add_argument("--skip-dictionary", action="store_true")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--out", help="Optional output file.")
    args = parser.parse_args()

    path = Path(args.file).expanduser().resolve()
    result = check_file(path, args)

    if args.format == "json":
        text = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        from io import StringIO
        old_stdout = sys.stdout
        buf = StringIO()
        try:
            sys.stdout = buf
            print_markdown(result)
        finally:
            sys.stdout = old_stdout
        text = buf.getvalue()

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
