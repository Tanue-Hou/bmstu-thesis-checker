#!/usr/bin/env python3
"""Map decoded Russian UTF-16LE literals to static Ghidra function references."""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXE = ROOT.parent / "runtime" / "TestVkr232.exe"
DEFAULT_PSEUDO = ROOT / "evidence" / "agent-v027" / "decompilation" / "recovered_pseudocode.c"
DEFAULT_PROVENANCE = ROOT / "evidence" / "agent-v027" / "decompilation" / "provenance.json"
DEFAULT_OUT = ROOT / "evidence" / "business-map-232" / "diagnostic-map-r2"
SYMBOL_RE = re.compile(r"\b(DAT|PTR|FUN)_([0-9a-fA-F]{8})\b")
PLAIN_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-fA-F]{8})(?![0-9a-fA-F])")
ENTRY_RE = re.compile(r"/\* ENTRY ([0-9a-fA-F]+) NAME (.*?) \*/")
DIAGNOSTIC_TERMS = ("ошибка", "не допуска", "некоррект", "должен", "должна", "должны", "нельзя", "неверн", "необходимо", "требуется")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pe_image_base_and_sections(data: bytes):
    if data[:2] != b"MZ":
        raise ValueError("Target does not have an MZ header")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe:pe + 4] != b"PE\0\0":
        raise ValueError("PE signature missing")
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24
    magic = struct.unpack_from("<H", data, opt)[0]
    if magic == 0x10B:
        image_base = struct.unpack_from("<I", data, opt + 28)[0]
    elif magic == 0x20B:
        image_base = struct.unpack_from("<Q", data, opt + 24)[0]
    else:
        raise ValueError("Unknown PE optional-header format")
    sections = []
    off = opt + optional_size
    for i in range(section_count):
        p = off + i * 40
        name = data[p:p + 8].split(b"\0", 1)[0].decode("ascii", "replace")
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", data, p + 8)
        sections.append((name, virtual_address, max(virtual_size, raw_size), raw_offset, raw_size))
    return image_base, sections


def va_to_file_offset(va: int, image_base: int, sections) -> int | None:
    rva = va - image_base
    for _name, section_rva, span, raw_offset, raw_size in sections:
        if section_rva <= rva < section_rva + span:
            delta = rva - section_rva
            if delta < raw_size:
                return raw_offset + delta
            return None
    return None


def scan_utf16_russian(data: bytes, image_base: int, sections):
    found = []
    # PE string data is normally code-unit aligned. Scan both alignments to
    # tolerate packed resources while still requiring a NUL terminator.
    for parity in (0, 1):
        i = parity
        while i + 1 < len(data):
            start = i
            chars = []
            while i + 1 < len(data):
                unit = data[i] | (data[i + 1] << 8)
                if unit == 0:
                    break
                ch = chr(unit)
                if not (ch.isprintable() or ch in "\t\r\n"):
                    break
                chars.append(ch)
                i += 2
            end = i
            if i + 1 < len(data) and data[i:i + 2] == b"\0\0" and len(chars) >= 3:
                text = "".join(chars)
                if any("\u0400" <= c <= "\u04ff" for c in text):
                    va = image_base + next((rva + (start - raw) for _n, rva, _s, raw, rs in sections if raw <= start < raw + rs), -1)
                    if va >= image_base:
                        found.append({"file_offset": start, "end_file_offset": end, "va": f"{va:08x}", "end_va": f"{va + end - start:08x}", "text": text})
            # Skip the terminator; on a failed run, advance one code unit.
            i = i + 2 if i + 1 < len(data) and data[i:i + 2] == b"\0\0" else max(i + 2, start + 2)
    dedup = {(x["file_offset"], x["text"]): x for x in found}
    return sorted(dedup.values(), key=lambda x: (int(x["va"],16), x["text"]))


def build_references(path: Path):
    refs = defaultdict(list)
    current = None
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            m = ENTRY_RE.search(line)
            if m:
                current = {"address": m.group(1).lower(), "name": m.group(2)}
                continue
            if current is None:
                continue
            matches = [(m.group(2), m.group(1), "symbol") for m in SYMBOL_RE.finditer(line)]
            covered = {m.start(2) for m in SYMBOL_RE.finditer(line)}
            matches.extend((m.group(1), "", "bare_hex") for m in PLAIN_RE.finditer(line) if m.start(1) not in covered)
            for value, prefix, form in matches:
                va = int(value, 16)
                refs[va].append({"function_address": current["address"], "function_name": current["name"], "pseudocode_line": line_no, "symbol_form": (prefix + "_" if prefix else "") + value.lower(), "address_form": form})
    return refs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe", type=Path, default=DEFAULT_EXE)
    ap.add_argument("--pseudocode", type=Path, default=DEFAULT_PSEUDO)
    ap.add_argument("--provenance", type=Path, default=DEFAULT_PROVENANCE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--supplementary-pseudocode",type=Path,action='append',default=[])
    args = ap.parse_args()

    binary = args.exe.read_bytes()
    binary_hash = hashlib.sha256(binary).hexdigest()
    provenance = json.loads(args.provenance.read_text(encoding="utf-8"))
    if binary_hash.lower() != provenance.get("target_sha256", "").lower():
        raise SystemExit("Target hash does not match decompilation provenance")
    image_base, sections = pe_image_base_and_sections(binary)
    strings = scan_utf16_russian(binary, image_base, sections)

    known = {item["va"].lower(): item for item in provenance.get("work_name_literals", [])}
    for expected_va in ("006d6b5a", "006d6bee"):
        literal = known.get(expected_va)
        match = next((x for x in strings if x["va"] == expected_va), None)
        if not literal or not match or match["file_offset"] != literal["file_offset"] or match["text"] != literal["utf16_text"]:
            raise SystemExit("Known-string verification failed at " + expected_va)

    references = build_references(args.pseudocode)
    pseudocode_label=args.pseudocode.resolve().relative_to(ROOT).as_posix()
    for address,items in references.items():
        for item in items:item['pseudocode_source']=pseudocode_label
    for supplement in args.supplementary_pseudocode:
        additional=build_references(supplement)
        supplement_label=supplement.resolve().relative_to(ROOT).as_posix()
        for address,items in additional.items():
            for item in items:item['pseudocode_source']=supplement_label
            references[address].extend(items)
    # Assign each reference to the containing literal interval in one sorted
    # sweep/index lookup instead of rescanning every reference for every text.
    starts = [int(item["va"], 16) for item in strings]
    max_ends=[];max_end=0
    for item in strings:
        max_end=max(max_end,int(item['end_va'],16));max_ends.append(max_end)
    refs_by_string = defaultdict(list)
    for address, refs in references.items():
        at = bisect.bisect_right(starts, address) - 1
        while at >= 0 and max_ends[at] > address:
            low = starts[at]
            if address<int(strings[at]['end_va'],16) and (address-low)%2==0:
                for ref in refs:
                    refs_by_string[at].append(dict(ref, referenced_va=f"{address:08x}", reference_relation="direct_addr" if address == low else "reference_inside_literal", byte_offset_into_literal=address - low))
            at -= 1

    diagnostic_map = []
    for index, item in enumerate(strings):
        found_refs = refs_by_string[index]
        text = item["text"]
        terms = [term for term in DIAGNOSTIC_TERMS if term in text.casefold()]
        diagnostic_map.append(dict(item, diagnostic_terms=terms, candidate_functions=sorted(found_refs, key=lambda r: (r["function_address"], r["pseudocode_line"], r["referenced_va"]))))

    args.output.mkdir(parents=True, exist_ok=False)
    result = {
        "schema_version": 1,
        "analysis_type": "static_utf16le_string_reference_map",
        "target_sha256": binary_hash,
        "pe_image_base": f"{image_base:08x}",
        "source_hashes": {p.name: sha256(p) for p in (args.exe, args.pseudocode, args.provenance,*args.supplementary_pseudocode)},
        "counts": {
            "russian_utf16le_nul_terminated_strings": len(strings),
            "diagnostic_text_candidates": sum(bool(x["diagnostic_terms"]) for x in diagnostic_map),
            "diagnostic_candidates_with_function_refs": sum(bool(x["candidate_functions"]) for x in diagnostic_map if x["diagnostic_terms"]),
            "all_strings_with_function_refs": sum(bool(x["candidate_functions"]) for x in diagnostic_map),
        },
        "known_address_verification": [
            {"va": va, "file_offset": known[va]["file_offset"], "text": known[va]["utf16_text"], "verified": True}
            for va in ("006d6b5a", "006d6bee")
        ],
        "limits": [
            "静态文件扫描；字符串及函数引用不证明运行时执行、分支到达或诊断触发。",
            "包含西里尔码元的可打印序列仍可能是随机二进制误解码；8713等总数不能当作自然语言诊断或规则数量。",
            "UTF-16LE扫描只收录可解码、至少3码元、含西里尔字符且有NUL终止的连续文本；不覆盖UTF-8/ANSI、跨段资源、未终止或不可打印混合数据。",
            "函数候选来自反编译文本中的DAT_/PTR_/FUN_符号和独立8位十六进制字面量；裸数字可能是常量，均需人工核验。",
            "VA到文件偏移按PE节表映射；不在已初始化节数据中的地址不会被作为字符串纳入。",
        ],
        "strings": diagnostic_map,
    }
    (args.output / "diagnostic-map.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = f"""# Native Russian diagnostic string map (r2)

Static scan of `runtime/TestVkr232.exe`, SHA-256 `{binary_hash}`; PE image base `0x{image_base:08x}`. The scanner first verified both known literals against provenance and their exact file offsets and decoded text: `006d6b5a` and `006d6bee`.

The JSON contains {len(strings):,} decodable Russian UTF-16LE NUL-terminated strings. Of these, {result['counts']['diagnostic_text_candidates']:,} contain configured diagnostic terms; {result['counts']['diagnostic_candidates_with_function_refs']:,} diagnostic candidates have at least one pseudocode address reference. Each candidate records function address/name and pseudocode line. A reference equal to the string's first VA is `direct_addr`; an address pointing later within the string's byte range is `reference_inside_literal`, with its byte offset.

All links are static candidates, not evidence that code executed or a diagnostic fired. The scan omits non-UTF-16LE or unterminated text and the reference map can include bare hexadecimal constants; see `limits` in the JSON for scope.

Printable sequences containing Cyrillic code units can include random binary false positives. The total is not a count of meaningful messages or rules. Revision2 sorts by VA, handles nested intervals with prefix maximum ends, and excludes odd-byte offsets into UTF-16 code units. Prior evidence is preserved.

Rebuild from the project root with:

```powershell
& 'C:\\Users\\Tanue Hou\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' implementation/scripts/reverse_engineering/map_native_diagnostics.py
```
"""
    (args.output / "README.md").write_text(summary, encoding="utf-8")
    print(json.dumps({"russian_strings": len(strings), "diagnostic_candidates": result["counts"]["diagnostic_text_candidates"], "diagnostic_with_refs": result["counts"]["diagnostic_candidates_with_function_refs"], "known_checks": 2, "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
