#!/usr/bin/env python3
"""Build a source-hashed, static function index from a Ghidra export."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = DEFAULT_ROOT / "evidence" / "agent-v027" / "decompilation"
DEFAULT_OUTPUT = DEFAULT_ROOT / "evidence" / "business-map-232" / "function-index-r2"
FUNCTION_RE = re.compile(r"/\* ENTRY ([0-9a-fA-F]+) NAME (.*?) \*/")
ADDRESS_RE = re.compile(r"(?<![0-9a-fA-F])(?:DAT|PTR|FUN)_([0-9a-fA-F]{8})\b|\b([0-9a-fA-F]{8})\b")
ERROR_TERMS = ("ошибка", "некоррект", "неверн", "не допуска", "не заполн", "не указан")
WORK_TERMS = ("работ", "вкр", "квалификацион", "наименован")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def pseudocode_functions(path: Path) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    current_address = None
    current_name = None
    start_line = 0
    with path.open("r", encoding="utf-8", errors="replace") as stream:
        for line_number, line in enumerate(stream, 1):
            match = FUNCTION_RE.search(line)
            if match:
                if current_address:
                    result[current_address] = {
                        "name": current_name,
                        "start_line": start_line,
                        "end_line": line_number - 1,
                    }
                current_address, current_name = match.group(1).lower(), match.group(2)
                start_line = line_number
        if current_address:
            result[current_address] = {
                "name": current_name,
                "start_line": start_line,
                "end_line": line_number,
            }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()

    function_path = source / "functions.tsv"
    calls_path = source / "calls.tsv"
    strings_path = source / "defined_strings.tsv"
    pseudocode_path = source / "recovered_pseudocode.c"
    provenance_path = source / "provenance.json"
    inputs = [function_path, calls_path, strings_path, pseudocode_path, provenance_path]
    for path in inputs:
        if not path.is_file():
            raise SystemExit(f"Required source file missing: {path}")

    functions_rows = read_tsv(function_path)
    calls_rows = read_tsv(calls_path)
    strings_rows = read_tsv(strings_path)
    pseudo = pseudocode_functions(pseudocode_path)
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))

    functions: dict[str, dict[str, object]] = {}
    for row in functions_rows:
        address = row["address"].strip().lower()
        try:
            size = int(row["body_bytes"].strip())
        except ValueError:
            size = None
        pseudo_entry = pseudo.get(address)
        functions[address] = {
            "address": address,
            "name": row.get("name", ""),
            "size_bytes": size,
            "status": row.get("status", ""),
            "error": row.get("error", ""),
            "callers": [],
            "callees": [],
            "pseudocode_lines": (
                {"start": pseudo_entry["start_line"], "end": pseudo_entry["end_line"]}
                if pseudo_entry
                else None
            ),
        }

    for row in calls_rows:
        caller = row["caller"].strip().lower()
        callee = row["callee"].strip().lower()
        if caller in functions:
            functions[caller]["callees"].append(callee)
        if callee in functions:
            functions[callee]["callers"].append(caller)
    for entry in functions.values():
        entry["callers"] = sorted(set(entry["callers"]))
        entry["callees"] = sorted(set(entry["callees"]))

    by_address = {row["address"].strip().lower(): row for row in strings_rows}
    referenced_strings: dict[str, list[dict[str, str]]] = defaultdict(list)
    current_address = None
    with pseudocode_path.open("r", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            match = FUNCTION_RE.search(line)
            if match:
                current_address = match.group(1).lower()
                continue
            if not current_address:
                continue
            for groups in set(ADDRESS_RE.findall(line)):
                literal_address = next(group for group in groups if group).lower()
                string_row = by_address.get(literal_address)
                if string_row and string_row.get("value"):
                    referenced_strings[current_address].append(
                        {"address": literal_address, "value": string_row["value"]}
                    )

    work_name_literals = {
        item["va"].lower(): item
        for item in provenance.get("work_name_literals", [])
        if item.get("va")
    }
    string_candidates = []
    for row in strings_rows:
        value = row.get("value") or ""
        if not any(term in value.casefold() for term in ERROR_TERMS):
            continue
        address = row.get("address", "").lower()
        direct_refs = [
            address_ for address_, items in referenced_strings.items()
            if any(item["address"] == address for item in items)
        ]
        if address in work_name_literals:
            known = work_name_literals[address]
            direct_refs = sorted(set(direct_refs + [known.get("referencing_function", "").lower()]))
        direct_refs = [ref for ref in direct_refs if ref in functions]
        string_candidates.append({
            "string_address": address,
            "value": value,
            "reference_from_column": row.get("reference_from", ""),
            "direct_function_references_in_pseudocode_or_provenance": direct_refs,
            "association_basis": "direct_static_reference" if direct_refs else "text_only_candidate",
            "interpretation": (
                "俄文诊断字符串的直接静态关联；仅表示代码/导出中存在引用，不表示运行时出现或触发。"
                if direct_refs else
                "按俄文错误措辞筛出的候选；当前材料未建立到函数的直接地址引用。"
            ),
        })

    # The defined-strings export contains symbol/type annotations, while the
    # provenance manifest preserves selected decoded UTF-16 literals. Index
    # diagnostic-looking literals from that manifest explicitly and retain
    # their provenance as the evidence source.
    seen_literal_addresses = {item["string_address"] for item in string_candidates}
    for address, literal in sorted(work_name_literals.items()):
        value = literal.get("utf16_text", "")
        if address in seen_literal_addresses or not any(term in value.casefold() for term in ERROR_TERMS):
            continue
        ref = literal.get("referencing_function", "").lower()
        direct_refs = [ref] if ref in functions else []
        string_candidates.append({
            "string_address": address,
            "value": value,
            "reference_from_column": "",
            "evidence_source": "provenance.json work_name_literals",
            "direct_function_references_in_pseudocode_or_provenance": direct_refs,
            "association_basis": "direct_static_reference" if direct_refs else "text_only_candidate",
            "interpretation": (
                "俄文诊断字符串由 provenance 清单关联到函数地址；仅表示静态关联，不表示运行时出现或触发。"
                if direct_refs else
                "按俄文错误措辞筛出的候选；当前材料未建立到函数的直接地址引用。"
            ),
        })

    known_function = functions.get("0044a748")
    if known_function:
        known_function["business_candidates"] = [
            {
                "label": "work-name validation candidate",
                "basis": "provenance explicitly identifies known work-name literals; pseudocode directly references their addresses",
                "direct_literal_references": [
                    {"address": va, "value": item.get("utf16_text", "")}
                    for va, item in sorted(work_name_literals.items())
                    if item.get("referencing_function", "").lower() == "0044a748"
                ],
                "inference": "基于输入字段与工作名称词表比较以及错误文字地址引用，推测该函数参与工作名称校验；静态关联不证明具体执行路径。",
            }
        ]

    output.mkdir(parents=True, exist_ok=False)
    index = {
        "schema_version": 1,
        "analysis_type": "static_function_index",
        "source_directory": source.as_posix(),
        "target_sha256": provenance.get("target_sha256"),
        "source_files": {path.name: sha256(path) for path in inputs},
        "counts": {
            "functions": len(functions),
            "calls_rows": len(calls_rows),
            "defined_strings": len(strings_rows),
            "pseudocode_functions": len(pseudo),
            "diagnostic_string_candidates": len(string_candidates),
        },
        "limits": [
            "静态导出与伪代码行范围，不是原始源代码或完整控制流恢复。",
            "字符串定义、地址交叉引用及候选关联均不表示程序实际执行或诊断实际触发。",
            "缺失的伪代码函数范围保留为 null；间接调用和字符串引用可能不完整。",
        ],
        "functions": sorted(functions.values(), key=lambda item: item["address"]),
        "diagnostic_string_candidates": string_candidates,
    }
    index_path = output / "function-index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    direct_count = sum(item["association_basis"] == "direct_static_reference" for item in string_candidates)
    speculative_count = len(string_candidates) - direct_count
    readme = f"""# Static business-function index (r2)

Generated by `implementation/scripts/reverse_engineering/index_business_functions.py`.

This is a static navigation aid for target SHA-256 `{index['target_sha256']}`. It indexes {len(functions):,} discovered function records, {len(calls_rows):,} call rows, and {len(strings_rows):,} defined strings. Pseudocode line locations refer to `agent-v027/decompilation/recovered_pseudocode.c`.

## Candidate associations

The `defined_strings.tsv` input contains symbol/type annotations rather than decoded Russian messages. Diagnostic-looking UTF-16 literals are therefore also indexed from `provenance.json` when present. The index contains {len(string_candidates)} Russian diagnostic-string candidates: {direct_count} have a direct static address reference in recovered pseudocode or the supplied provenance record; {speculative_count} are text-only candidates. `0044a748` is annotated as a work-name validation candidate because the provenance explicitly ties it to known work-name literals and the pseudocode references those literal addresses. This semantic label is an inference.

Direct static references establish only a relationship in the exported artifacts. They do not establish runtime execution, a reached branch, or a displayed/triggered diagnostic. The address scan recognizes `DAT_`, `PTR_`, and `FUN_` symbols plus standalone eight-hex-digit tokens. It applies only to decoded strings in the supplied TSV and provenance list; `defined_strings.tsv` has no decoded values for most literal addresses, so this is not a complete scan of all data cross-references. The pseudocode is decompiler output, indirect calls may be incomplete, and absent line spans are recorded as `null`.

## Reproducibility

`function-index.json` records SHA-256 for each of the five source inputs, plus the target binary hash from provenance. This revision is written under `function-index-r2/` to preserve the previous evidence. Re-run from the `implementation` directory with the project's Python interpreter:

```powershell
& 'C:\\Users\\Tanue Hou\\AppData\\Local\\Programs\\Python\\Python313\\python.exe' scripts/reverse_engineering/index_business_functions.py
```
"""
    (output / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({"functions": len(functions), "calls": len(calls_rows), "diagnostic_candidates": len(string_candidates), "direct": direct_count, "text_only": speculative_count, "output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
