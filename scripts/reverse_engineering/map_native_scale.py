"""Map native TestVkr 2.32 character-size scaling branches to static evidence."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import capstone
import pefile

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = "5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0"
EXPECTED_TRACE = "3753bfd3b1ad6fbfbec067641dc9b79c8eba5a29d9d88d7838429edc689bfd38"
EXPECTED_REPORT = "5de68d45a218b803c28ce43b69b63c3dca73f160cda9cbe3096d3dae8eea206f"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = args.out.absolute()
    out.mkdir(parents=True, exist_ok=False)
    exe = ROOT.parent / "runtime" / "TestVkr232.exe"
    raw = exe.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED:
        raise SystemExit(f"unexpected executable SHA-256: {digest}")
    pe = pefile.PE(data=raw)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    slices = {}
    ranges = [
        (0x409B84, 0x409D00, "scale_producer"),
        (0x47BACD, 0x47BBE0, "ordinary_report_gate_emit"),
        (0x47BBDD, 0x47BCF8, "size_report_gate_emit"),
        (0x40CC64, 0x40E738, "w_parser_candidate"),
    ]
    for start, end, name in ranges:
        off = pe.get_offset_from_rva(start - 0x400000)
        ins = list(md.disasm(raw[off:off + end - start], start))
        (out / f"{name}.asm").write_text(
            "\n".join(f"{i.address:08x} {i.mnemonic} {i.op_str}" for i in ins) + "\n",
            encoding="utf-8", newline="\n")
        slices[name] = {"start_va": hex(start), "end_va_exclusive": hex(end),
                        "instruction_count": len(ins)}

    constants = {}
    for va in (0x6E51C0,):
        off = pe.get_offset_from_rva(va - 0x400000)
        constants[hex(va)] = {"raw_hex": raw[off:off + 4].hex(),
                              "signed_int32": struct.unpack("<i", raw[off:off + 4])[0]}
    xml_tags = {}
    for va in (0x6C1DE3, 0x6C1DE7, 0x6C1DD3, 0x6C1DDD):
        off = pe.get_offset_from_rva(va - 0x400000)
        end = raw.index(b"\0", off)
        xml_tags[hex(va)] = {"file_offset": off, "raw_hex": raw[off:end + 1].hex(),
                             "utf8": raw[off:end].decode("utf-8")}

    source_pseudo = ROOT / "evidence/agent-v027/decompilation/recovered_pseudocode.c"
    source_main = ROOT / "evidence/business-map-232/file-entry-decompilation-r1/function.c"
    provenance = ROOT / "evidence/agent-v027/decompilation/provenance.json"
    case_dir = ROOT / "evidence/business-map-232/scale-native-r1/small69_11"
    trace_path = case_dir / "trace.json"
    report_path = case_dir / "report.json"
    trace_raw, report_raw = trace_path.read_bytes(), report_path.read_bytes()
    trace_sha, report_sha = hashlib.sha256(trace_raw).hexdigest(), hashlib.sha256(report_raw).hexdigest()
    if trace_sha != EXPECTED_TRACE or report_sha != EXPECTED_REPORT:
        raise SystemExit(f"native scale evidence changed: trace={trace_sha}, report={report_sha}")
    trace, report = json.loads(trace_raw), json.loads(report_raw)
    if trace.get("target_sha256") != digest or report.get("executable_sha256") != digest:
        raise SystemExit("runtime evidence is for a different executable")
    if report.get("trace_sha256") != trace_sha:
        raise SystemExit("report.json does not bind the supplied trace")
    hits = trace.get("breakpoint_hits", [])
    size_hit = next((h for h in hits if h.get("label") == "font_run_state" and
                     h.get("font_state", {}).get("scale_pct") == 69 and
                     h.get("font_state", {}).get("enabled_flag") == 1), None)
    add_hit = next((h for h in hits if h.get("label") == "scale_small_add" and
                    h.get("scale_state", {}).get("scale_pct") == 69), None)
    gate_hit = next((h for h in hits if h.get("label") == "scale_small_report_gate"), None)
    emit_hit = next((h for h in hits if h.get("label") == "scale_small_report_emit"), None)
    if not all((size_hit, add_hit, gate_hit, emit_hit)):
        raise SystemExit("expected size/add/report gate/report emit breakpoints are missing")
    image_base = next((int(e["image_base"], 16) for e in trace.get("events", [])
                       if e.get("event") == 3 and e.get("image_base")), None)
    if image_base is None:
        raise SystemExit("trace image base is missing")
    preferred = lambda hit: hex(int(hit["address"], 16) - image_base + 0x400000)
    evidence = {
        "target": {"path": "../runtime/TestVkr232.exe", "sha256": digest},
        "slices": slices,
        "constant_values": constants,
        "native_xml_strings": xml_tags,
        "breakpoint_candidates_static_only": {
            "ordinary": {"branch_cmp": "0x00409b9f", "bucket_add": "0x00409ba8",
                         "producer_call_00402f08": "0x00409bc6"},
            "tiny": {"branch_cmp": "0x00409bd0", "bucket_add": "0x00409bdc",
                     "producer_call_00402f08": "0x00409bf7"},
            "large": {"branch_cmp": "0x00409cc3", "bucket_add": "0x00409cdb",
                      "producer_call_00402f08": "0x00409cf9"},
            "report": {"ordinary_slot_0x10_gt_10_cmp": "0x0047bacd",
                       "ordinary_render_call_0047a298": "0x0047bb80",
                       "slot_0x12_vs_DAT_006e51c0_cmp": "0x0047bbe6",
                       "slot_0x12_render_call_0047a298": "0x0047bc9b"}},
        "analyst_interpretation": {
            "004098f8": "classifies a run style's size into ordinary-small, tiny, and large buckets",
            "00402f08": "adds selected run text to the parser diagnostic bucket",
            "0040cc64": "parses w:w to intermediate +0x9c and w:spacing to intermediate +0xa0",
            "004263a4": "copies a style object field-for-field, including +0xa0 to +0xa0",
            "0040f98c": "converts intermediate +0x9c to output style +0xa0 and intermediate +0xa0 to output +0xa4",
            "0047a528": "constructs main report entries from counters"},
        "decompiler_cross_references": {
            "scale_classifier": {"function_entry": "0x004098f8", "source_lines": "4105-4177"},
            "w_w_to_intermediate": {"function_entry": "0x0040cc64", "source_lines": "6350-6359",
                                    "tag_va": "0x006c1de3", "value_attribute_va": "0x006c1de7",
                                    "destination_offset": "0x9c"},
            "w_spacing_to_intermediate": {"function_entry": "0x0040cc64", "source_lines": "6334-6346",
                                           "tag_va": "0x006c1dd3", "value_attribute_va": "0x006c1ddd",
                                           "destination_offset": "0xa0"},
            "style_field_copy": {"function_entry": "0x004263a4", "source_line": 18045,
                                 "field": "source +0xa0 to destination +0xa0; helper called by 0041c118 at line 13132"},
            "style_construction": {"function_entry": "0x0040f98c", "source_lines": "7081-7082",
                                   "field_map": {"intermediate +0x9c": "output +0xa0 (index 0x28)",
                                                 "intermediate +0xa0": "output +0xa4 (index 0x29)"}},
            "run_property_parser_call": {"caller": "0x0040e9a8", "source_line": 6855,
                                         "call": "FUN_0040cc64(param_1,param_2+0x54)"},
            "main_report_counter_tests": {"function_entry": "0x0047a528", "source_lines": "896-921"}},
        "runtime_case_evidence": {
            "case": "scale-native-r1/small69_11",
            "trace_path": trace_path.relative_to(ROOT).as_posix(), "trace_sha256": trace_sha,
            "report_path": report_path.relative_to(ROOT).as_posix(), "report_sha256": report_sha,
            "report_binds_trace_sha256": report.get("trace_sha256"),
            "input": {"w:w": 69, "source_sha256": report.get("source_sha256")},
            "dynamic_observations_this_case_only": {
                "font_run_state": {"runtime_va": size_hit["address"], "preferred_va": preferred(size_hit),
                                   "scale_pct": size_hit["font_state"]["scale_pct"],
                                   "enabled_flag": size_hit["font_state"]["enabled_flag"]},
                "scale_small_add": {"runtime_va": add_hit["address"], "preferred_va": preferred(add_hit),
                                    "scale_pct": add_hit["scale_state"]["scale_pct"]},
                "scale_small_report_gate": {"runtime_va": gate_hit["address"], "preferred_va": preferred(gate_hit),
                                             "small_count": gate_hit["scale_report_state"]["small_count"]},
                "scale_small_report_emit": {"runtime_va": emit_hit["address"], "preferred_va": preferred(emit_hit),
                                             "small_count": emit_hit["scale_report_state"]["small_count"]},
                "matching_report_diagnostic": next((x["message"] for x in report.get("diagnostics", [])
                                                     if "масштаб шрифта меньше 70%" in x.get("message", "")), None)},
            "scope": "Only this small69_11 case dynamically confirms these observed states and gates; other mapped addresses remain static candidates."},
        "source_hashes": {
            "evidence/agent-v027/decompilation/recovered_pseudocode.c": hashlib.sha256(source_pseudo.read_bytes()).hexdigest(),
            "evidence/business-map-232/file-entry-decompilation-r1/function.c": hashlib.sha256(source_main.read_bytes()).hexdigest(),
            "evidence/agent-v027/decompilation/provenance.json": hashlib.sha256(provenance.read_bytes()).hexdigest()},
        "limits": ["Static disassembly and decompiler text remain candidates except the case-specific hits in runtime_case_evidence.",
                   "Function names and business labels are analyst interpretations.",
                   "Object fields are tracked with their owning structure and offsets; shared offsets across structures do not imply shared semantics.",
                   "Direct versus linked style resolution is not established by these copy helpers alone."]}
    (out / "map.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
    (out / "reconstruction.c").write_text(
        "/* Analyst reconstruction from static 2.32 evidence; not original source. */\n"
        "intermediate.size = parse_w_w_val();       /* intermediate +0x9c */\n"
        "intermediate.spacing = parse_w_spacing_val(); /* intermediate +0xa0 */\n"
        "style.size = intermediate.size;            /* style +0xa0 */\n"
        "style.spacing = intermediate.spacing;      /* style +0xa4 */\n"
        "if (style.size < 70 && run_enabled) {\n"
        "    if (style.size > 30) add_text(parser + 0x198);\n"
        "    else if (style.size > 1) add_text(parser + 0x19c);\n"
        "}\n"
        "if (style.size > 130 && run_enabled) add_text(parser + 0x1a0);\n"
        "if (main[0x10] > 10) emit_ordinary_report();\n"
        "if (main[0x12] > *(int32_t*)0x006e51c0) emit_size_report();\n"
        "/* Runtime behavior and exact XML inheritance are not asserted here. */\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(out), "sha256": digest, "constant": constants}))


if __name__ == "__main__":
    main()
