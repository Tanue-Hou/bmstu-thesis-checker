"""Measure compact report projection size on retained private cross-check outputs.

The receipt is deliberately aggregate-only: it contains no case names, paths,
source hashes, findings, or document text.
"""
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = Path(
    r"D:\Codex项目\analysis_TestVkr\private_trials\2026-10-15\cross_v0220_final\cases"
)
OUTPUT = ROOT / "evidence" / "optimization-audit-r1" / "compact-benchmark.json"
sys.path.insert(0, str(ROOT / "scripts"))
from compact_report import project_report


DECISION_FIELDS = (
    "rule_id", "severity", "verification_status", "verification_scope",
    "verification_by_build", "threshold_origin", "threshold", "confidence",
    "fix_priority", "action_eligibility",
)
TOP_LEVEL_DECISION_FIELDS = (
    "document_kind", "file_type", "work_type", "native_reference",
    "verification_status", "summary", "review_summary", "action_contract",
    "action_summary", "repair_capability",
)


def decision_signature(report):
    return [
        {field: finding.get(field) for field in DECISION_FIELDS}
        for finding in report.get("findings", [])
    ]


def location_count_total(report):
    total = 0
    for finding in report.get("findings", []):
        precise = finding.get("precise_locations") or {}
        total += precise.get("occurrence_count", len(precise.get("occurrences", [])))
    return total


def top_level_signature(report):
    return {field: report.get(field) for field in TOP_LEVEL_DECISION_FIELDS}


def serialized_bytes(report):
    return len(json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8"))


def benchmark(cases_dir=DEFAULT_CASES):
    # Keep the explicitly authorized absolute input path as supplied. Resolving
    # this private-trials path is unnecessary and can be blocked by Windows ACLs.
    cases_dir = Path(cases_dir)
    inputs = sorted(cases_dir.glob("*.local.json"))
    if not inputs:
        raise ValueError("No local report JSON files found in the configured cases directory")

    full_bytes = compact_bytes = finding_total = location_total = 0
    invariant_cases = size_reduced_cases = 0
    for path in inputs:
        report = json.loads(path.read_text(encoding="utf-8-sig"))
        full = project_report(report, "full")
        compact = project_report(report, "compact")
        same = (
            top_level_signature(full) == top_level_signature(compact)
            and decision_signature(full) == decision_signature(compact)
            and location_count_total(full) == location_count_total(compact)
            and len(full.get("findings", [])) == len(compact.get("findings", []))
        )
        invariant_cases += int(same)
        full_size, compact_size = serialized_bytes(full), serialized_bytes(compact)
        full_bytes += full_size
        compact_bytes += compact_size
        finding_total += len(full.get("findings", []))
        location_total += location_count_total(full)
        size_reduced_cases += int(compact_size < full_size)

    saved = full_bytes - compact_bytes
    percent = (100.0 * saved / full_bytes) if full_bytes else 0.0
    passed = invariant_cases == len(inputs) and saved > 0
    result = {
        "status": "passed" if passed else "failed",
        "cases_processed": len(inputs),
        "findings_total": finding_total,
        "source_location_occurrences_total": location_total,
        "decision_and_location_invariants": {
            "cases_unchanged": invariant_cases,
            "all_cases_unchanged": invariant_cases == len(inputs),
        },
        "serialized_report_bytes": {
            "format": "UTF-8 JSON, ensure_ascii=false, indent=2; same serializer for both levels",
            "full_total": full_bytes,
            "compact_total": compact_bytes,
            "bytes_removed": saved,
            "reduction_percent": round(percent, 2),
            "cases_with_smaller_compact_output": size_reduced_cases,
        },
        "limits": "Aggregate output only. No case identifiers, paths, hashes, finding text, or document text are retained. Size change is serialization volume, not accuracy or correctness evidence beyond the explicit invariant checks.",
    }
    return result


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        raise SystemExit("Benchmark receipt already exists; refusing to overwrite it")
    result = benchmark()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "cases_processed": result["cases_processed"],
        "full_total_bytes": result["serialized_report_bytes"]["full_total"],
        "compact_total_bytes": result["serialized_report_bytes"]["compact_total"],
        "reduction_percent": result["serialized_report_bytes"]["reduction_percent"],
    }, ensure_ascii=False))
    if result["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
