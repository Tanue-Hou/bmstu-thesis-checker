"""Compute privacy-preserving aggregate size and trigger metrics for local reports.

Only aggregate statistics and rule identifiers are written. No case path, filename,
content, case identifier, or case hash is emitted. Example:
  python scripts/audit_project_metrics.py --case-dir <private-cases> --out <output-dir>
"""
from __future__ import annotations

import argparse
import collections
import json
import statistics
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
IMPLEMENTATION = REPO / "implementation"
REGISTRY = IMPLEMENTATION / "scripts/testvkr-service/rules/rules_verified.json"
CHECKER_SCRIPTS = IMPLEMENTATION / "scripts"
sys.path.insert(0, str(CHECKER_SCRIPTS))
import check_document  # noqa: E402 - use the production evidence-integrity verifier


def compact_bytes(value: object) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def build_metrics(case_dir: Path) -> dict:
    files = sorted(case_dir.glob("*.local.json"))
    if not files:
        raise ValueError("case-dir contains no *.local.json reports")
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in files]
    raw_sizes = [path.stat().st_size for path in files]

    cases_by_rule: collections.Counter[str] = collections.Counter()
    findings_by_rule: collections.Counter[str] = collections.Counter()
    finding_field_bytes: collections.Counter[str] = collections.Counter()
    report_field_bytes: collections.Counter[str] = collections.Counter()
    finding_sizes: list[int] = []
    largest_finding_fields: dict[str, int] = {}
    largest_finding_bytes = 0
    for report in reports:
        for key, value in report.items():
            report_field_bytes[key] += compact_bytes(value)
        rules_in_case: set[str] = set()
        for finding in report.get("findings", []):
            rule_id = str(finding.get("rule_id", "(missing)"))
            rules_in_case.add(rule_id)
            findings_by_rule[rule_id] += 1
            size = compact_bytes(finding)
            finding_sizes.append(size)
            if size > largest_finding_bytes:
                largest_finding_bytes = size
                largest_finding_fields = {key: compact_bytes(value) for key, value in finding.items()}
            for key, value in finding.items():
                finding_field_bytes[key] += compact_bytes(value)
        for rule_id in rules_in_case:
            cases_by_rule[rule_id] += 1

    registry = json.loads(REGISTRY.read_text(encoding="utf-8-sig"))
    registry_rules = registry.get("rules", [])
    registry_field_bytes: collections.Counter[str] = collections.Counter()
    contexts_by_type: collections.Counter[str] = collections.Counter()
    explicit_statuses: collections.Counter[str] = collections.Counter()
    resolved_statuses: collections.Counter[str] = collections.Counter()
    evidence_integrity: collections.Counter[str] = collections.Counter()
    evidence_refs: collections.Counter[str] = collections.Counter()
    for rule in registry_rules:
        for key, value in rule.items():
            registry_field_bytes[key] += compact_bytes(value)
        by_build = rule.get("verification_by_build", {})
        for build, contexts in by_build.items():
            for context_key, context in contexts.items():
                contexts_by_type[f"{build}:{context_key}"] += 1
                explicit = context.get("verification_status")
                explicit_statuses[explicit if explicit is not None else "absent"] += 1
                resolved = explicit if explicit is not None else rule.get("verification_status", "missing")
                resolved_statuses[str(resolved)] += 1
                valid = check_document.context_evidence_valid(context)
                evidence_integrity["valid" if valid else "invalid"] += 1
                for ref in context.get("evidence_refs", []):
                    evidence_refs[str(ref)] += 1

    registry_compact_bytes = sum(compact_bytes(rule) for rule in registry_rules)
    evidence_ref_occurrences = sum(evidence_refs.values())
    all_rule_ids = sorted({str(rule["rule_id"]) for rule in registry_rules}
                          | set(cases_by_rule) | set(findings_by_rule))
    frequencies = {
        rule_id: {
            "cases": cases_by_rule[rule_id],
            "case_rate_pct": round(cases_by_rule[rule_id] * 100 / len(reports), 2),
            "finding_instances": findings_by_rule[rule_id],
        }
        for rule_id in all_rule_ids
    }
    report_payload_bytes = sum(report_field_bytes.values())
    finding_payload_bytes = sum(finding_field_bytes.values())
    registry_field_total = sum(registry_field_bytes.values())

    return {
        "measurement": "Script-calculated aggregates only; no private case names, paths, contents, IDs, or case hashes.",
        "registry": {
            "raw_json_bytes": REGISTRY.stat().st_size,
            "rule_count": len(registry_rules),
            "verification_by_build_context_count": sum(contexts_by_type.values()),
            "contexts_by_build_and_format_work_type": dict(contexts_by_type),
            "explicit_status_counts": dict(explicit_statuses),
            "resolved_status_counts": dict(resolved_statuses),
            "context_evidence_valid_counts": dict(evidence_integrity),
            "rule_field_compact_json_bytes": dict(registry_field_bytes.most_common()),
            "verification_by_build_share_of_compact_rule_payload_pct": round(
                registry_field_bytes["verification_by_build"] * 100 / registry_compact_bytes, 2
            ) if registry_compact_bytes else 0,
            "verification_by_build_share_of_rule_field_value_bytes_pct": round(
                registry_field_bytes["verification_by_build"] * 100 / registry_field_total, 2
            ) if registry_field_total else 0,
            "evidence_reference_occurrences": evidence_ref_occurrences,
            "distinct_evidence_references": len(evidence_refs),
            "references_reused_at_least_once": sum(1 for count in evidence_refs.values() if count > 1),
            "duplicate_reference_occurrences": sum(count - 1 for count in evidence_refs.values()),
            "max_reuse_count_for_one_reference": max(evidence_refs.values(), default=0),
        },
        "private_case_outputs": {
            "case_count": len(reports),
            "raw_json_bytes": {
                "total": sum(raw_sizes), "min": min(raw_sizes),
                "median": int(statistics.median(raw_sizes)), "max": max(raw_sizes),
            },
            "findings_total": len(finding_sizes),
            "finding_compact_json_bytes": {
                "median": int(statistics.median(finding_sizes)) if finding_sizes else 0,
                "max": max(finding_sizes, default=0),
            },
            "max_finding_field_compact_json_bytes": dict(sorted(
                largest_finding_fields.items(), key=lambda item: item[1], reverse=True
            )[:8]),
            "rule_trigger_frequency": frequencies,
            "top_level_report_field_compact_json_bytes": dict(report_field_bytes.most_common()),
            "top_level_findings_share_of_report_fields_pct": round(
                report_field_bytes.get("findings", 0) * 100 / report_payload_bytes, 2
            ) if report_payload_bytes else 0,
            "finding_field_compact_json_bytes": dict(finding_field_bytes.most_common()),
            "largest_finding_fields_share_of_finding_payload_pct": {
                key: round(finding_field_bytes[key] * 100 / finding_payload_bytes, 2)
                for key in ("evidence_refs", "precise_locations") if finding_payload_bytes
            },
        },
        "compact_output_recommendation": {
            "compatibility": "Add an opt-in compact projection or separate response mode; retain current default JSON, Markdown, and DOCX outputs.",
            "report_fields_to_keep": ["document_kind", "file_type", "work_type", "verification_status", "summary", "review_summary", "groups", "findings"],
            "finding_fields_to_keep": ["rule_id", "module", "severity", "message", "title_zh", "explanation_zh", "trigger_reason_zh", "fix_suggestion_zh", "word_path_zh", "fix_priority", "suggested_fix_priority", "affects_antiplagiarism", "confidence", "verification_status", "threshold", "location", "location_summary_zh", "threshold_origin"],
            "large_fields_to_defer_or_bound": ["evidence_refs", "static_evidence_refs", "precise_locations", "sample_trigger", "verification_scope", "comparison_policy"],
            "deferred_field_contract": "Compact responses should retain evidence-reference count and precise-location occurrence count, with full evidence and coordinates available through a detail response. Never silently truncate arrays in the existing full response.",
        },
    }


def render_readme(metrics: dict) -> str:
    registry = metrics["registry"]
    cases = metrics["private_case_outputs"]
    size = cases["raw_json_bytes"]
    return f"""# 本地输出体积审计

本审计只从规则注册表和当前私有真实案例 JSON 读取数据。统计脚本只在内存聚合；产物不含论文文字、案例路径/名称/ID、案例哈希或逐例结果。所有数字由脚本计算。

## 结论

规则注册表原始大小为 **{registry['raw_json_bytes']:,} bytes**，共 {registry['rule_count']} 条规则、{registry['verification_by_build_context_count']} 个 build/type/work-type 验证上下文；其中 `verification_by_build` 是规则紧凑序列化负载中最大的字段，占 **{registry['verification_by_build_share_of_compact_rule_payload_pct']:.2f}%**。显式状态分布、按规则顶层状态回退后的解析状态，以及通过生产 `context_evidence_valid` 的证据数分别记录在 `metrics.json`。上下文缺省 `verification_status` 不直接视作验证缺失。

验证证据引用共 {registry['evidence_reference_occurrences']:,} 次，其中 {registry['distinct_evidence_references']:,} 个不同引用；{registry['references_reused_at_least_once']:,} 个引用在多个上下文复用。

{cases['case_count']} 份本地 JSON 合计 **{size['total']:,} bytes**，单份中位数 {size['median']:,} bytes，最大 {size['max']:,} bytes；共 {cases['findings_total']} 个 finding。finding 紧凑序列化最大 {cases['finding_compact_json_bytes']['max']:,} bytes。输出体积主要来自 `findings`；finding 字段中 `evidence_refs` 与 `precise_locations` 占比最大。每条规则在多少份案例中触发、触发实例数，以及各字段体积均为纯聚合统计，见 `metrics.json`。

## 建议

以可选 compact 投影或单独响应模式减小传输量，保留报告结论、计数、分组和每条 finding 的规则、严重度、消息、建议、验证状态、阈值与位置摘要。`evidence_refs`、完整 `precise_locations`、静态来源、样例触发输入和完整验证范围可放在按需 detail 响应中；compact 响应应带证据引用数及位置 occurrence 总数。现有完整 JSON、Markdown 和 DOCX 默认输出保持原样，避免破坏既有消费者，也不要在完整模式静默截断数组。

## 边界

这是当前本地集合的体积和触发频率描述，不用于估计总体误报率、论文规范符合率或准确率。案例内容没有复制到本产物。
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-dir", type=Path, required=True,
                        help="Directory containing local *.local.json reports")
    parser.add_argument("--out", type=Path, required=True,
                        help="Output directory or metrics.json path")
    args = parser.parse_args()
    destination = args.out
    if destination.suffix.lower() == ".json":
        destination.parent.mkdir(parents=True, exist_ok=True)
        metrics_path = destination
        readme_path = destination.with_name("README.md")
    else:
        destination.mkdir(parents=True, exist_ok=True)
        metrics_path = destination / "metrics.json"
        readme_path = destination / "README.md"
    metrics = build_metrics(args.case_dir)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    readme_path.write_text(render_readme(metrics), encoding="utf-8", newline="\n")
    print(json.dumps({"case_count": metrics["private_case_outputs"]["case_count"],
                      "context_count": metrics["registry"]["verification_by_build_context_count"],
                      "evidence_valid": metrics["registry"]["context_evidence_valid_counts"],
                      "aggregate_only": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
