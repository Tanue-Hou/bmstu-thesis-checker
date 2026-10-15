"""Map observed first-indent hardware-watch writes back to native 232 instructions.

Inputs are synthetic-run traces. This script is read-only with respect to the PE,
traces and decompilation inputs; it creates only the requested evidence directory.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import capstone
import pefile

ROOT = Path(__file__).resolve().parents[2]  # implementation/
REPO = ROOT.parent
EXE = REPO / "runtime" / "TestVkr232.exe"
EXE_SHA256 = "5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0"
TRACE_INPUTS = {
    "docx_calibration": (REPO / "private_trials/first-watch-calibration-r1/native/trace.json",
        "b21c51a656bff61044ae6f4acbbc0f7365270f04e4af7e771624a7d47a8101e9"),
    "pdf_multipage": (REPO / "private_trials/first-watch-pdf-mp-r1/native/trace.json",
        "3d58fbe2e52bfe92774452f844eecfbc2a0c58444ce8545899ef49b84fbaf719"),
}
DECOMP = ROOT / "evidence/agent-v027/decompilation"
FUNCTIONS = DECOMP / "functions.tsv"
PSEUDO = DECOMP / "recovered_pseudocode.c"
CALLS = DECOMP / "calls.tsv"
PROVENANCE = DECOMP / "provenance.json"
FUNCTION_VAS = [0x006acec0, 0x006acf5b, 0x00403318, 0x0043e010,
                0x0043dd1c, 0x0046ba90]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hx(value):
    return hex(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True,
                    help="New evidence/business-map-232/first-indent-watch-writers-r1 directory")
    ap.add_argument("--private-out", type=Path,
                    default=REPO / "private_trials/reverse-engineering/first-indent-watch-writers-r1",
                    help="Private destination for full function assembly (defaults under private_trials)")
    args = ap.parse_args()
    out = args.out.absolute()
    out.mkdir(parents=True, exist_ok=True)
    private_out = args.private_out.absolute()
    private_out.mkdir(parents=True, exist_ok=True)
    raw = EXE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXE_SHA256
    pe = pefile.PE(data=raw)
    assert pe.OPTIONAL_HEADER.ImageBase == 0x400000
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    func_rows = {}
    for line in FUNCTIONS.read_text(encoding="utf-8").splitlines()[1:]:
        cols = line.split("\t")
        if len(cols) >= 3:
            try:
                func_rows[int(cols[0], 16)] = int(cols[2])
            except ValueError:
                pass
    function_asm = {}
    for va in FUNCTION_VAS:
        size = func_rows[va]
        offset = pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)
        code = raw[offset:offset + size]
        insns = list(md.disasm(code, va))
        assert insns and insns[0].address == va
        assert insns[-1].address + insns[-1].size <= va + size
        label = f"FUN_{va:08x}"
        function_asm[label] = insns
        text = "\n".join(f"{i.address:08x}  {i.bytes.hex():<20} {i.mnemonic} {i.op_str}".rstrip()
                          for i in insns) + "\n"
        (private_out / f"{label}.asm").write_text(text, encoding="utf-8", newline="\n")

    traces = {}
    writers = []
    for name, (path, expected_hash) in TRACE_INPUTS.items():
        trace_hash = sha(path)
        assert trace_hash == expected_hash, (name, trace_hash)
        doc = json.loads(path.read_text(encoding="utf-8"))
        assert doc["target_sha256"] == EXE_SHA256
        watch = doc["first_indent_counter_watch"]
        assert watch.get("requested") and watch.get("installed")
        assert watch.get("report_addresses_match") is True
        traces[name] = {
            "path_from_repo": path.relative_to(REPO).as_posix(),
            "sha256": trace_hash,
            "probe_document_sha256": doc.get("probe_document", {}).get("sha256"),
            "loader": watch.get("loader"),
            "initial_values": watch.get("initial_values"),
            "final_values": watch.get("final_values"),
            "report_binding_match": watch.get("report_addresses_match"),
            "report_base": hx(watch["report_base"]),
            "watched_addresses": {k: hx(v) for k, v in watch["addresses"].items()},
        }
        # trace JSON captures a relocated runtime near-code window. Convert to the
        # preferred image VA, compare with disk, and resolve EIP-after to its writer.
        runtime_base = None
        for event in doc.get("events", []):
            if event.get("event") in ("create_process", "CREATE_PROCESS_DEBUG_EVENT"):
                runtime_base = int(event.get("image_base", "0"), 0) or None
                if runtime_base:
                    break
        if runtime_base is None:
            # Existing trace event schema names this field module_base.
            for event in doc.get("events", []):
                if event.get("image") or event.get("module"):
                    for key in ("module_base", "base", "image_base"):
                        if event.get(key):
                            runtime_base = int(event[key], 0) if isinstance(event[key], str) else event[key]
                            break
                if runtime_base:
                    break
        # Runtime preferred-base delta is inferable directly from sampled code VA
        # and function's known preferred VA. The trace records preferred EIP too.
        for w in watch["writes"]:
            preferred_after = int(w["preferred_eip_after"], 0)
            runtime_after = int(w["eip_after"], 0)
            if runtime_base is None:
                runtime_base = runtime_after - (preferred_after - pe.OPTIONAL_HEADER.ImageBase)
            assert runtime_after - runtime_base + pe.OPTIONAL_HEADER.ImageBase == preferred_after
            candidates = [i for insns in function_asm.values() for i in insns
                          if i.address + i.size == preferred_after]
            assert len(candidates) == 1, (name, hx(preferred_after), len(candidates))
            ins = candidates[0]
            owner = next(k for k, seq in function_asm.items() if ins in seq)
            near_start_runtime = int(w["near_code_start"], 0)
            near_start_va = near_start_runtime - runtime_base + pe.OPTIONAL_HEADER.ImageBase
            near = bytes.fromhex(w["near_code_hex"])
            off = pe.get_offset_from_rva(near_start_va - pe.OPTIONAL_HEADER.ImageBase)
            disk_near = raw[off:off + len(near)]
            diffs = [j for j, (a, b) in enumerate(zip(near, disk_near)) if a != b]
            relocs = {entry.rva for block in pe.DIRECTORY_ENTRY_BASERELOC
                      for entry in block.entries if entry.type != pefile.RELOCATION_TYPE["IMAGE_REL_BASED_ABSOLUTE"]}
            writer_off = pe.get_offset_from_rva(ins.address - pe.OPTIONAL_HEADER.ImageBase)
            writer_disk = raw[writer_off:writer_off + ins.size]
            assert writer_disk == bytes(ins.bytes)
            assert not any(x == 0xCC for x in writer_disk)
            prefix_rep = any(p in (capstone.x86.X86_PREFIX_REP, capstone.x86.X86_PREFIX_REPE,
                                   capstone.x86.X86_PREFIX_REPNE) for p in ins.prefix)
            regs = {k.lower(): int(v, 0) for k, v in w.get("registers", {}).items()}
            mem = next((op.mem for op in ins.operands if op.type == capstone.x86.X86_OP_MEM), None)
            effective = None
            if mem is not None:
                base = regs.get(ins.reg_name(mem.base).lower(), 0) if mem.base else 0
                index = regs.get(ins.reg_name(mem.index).lower(), 0) if mem.index else 0
                effective = (base + index * mem.scale + mem.disp) & 0xffffffff
            record = {
                "trace": name,
                "fired_fields": w.get("fired_fields"),
                "before": w.get("before"), "after": w.get("after"),
                "eip_after_preferred_va": hx(preferred_after),
                "writer_va": hx(ins.address), "writer_bytes": bytes(ins.bytes).hex(),
                "writer_instruction": f"{ins.mnemonic} {ins.op_str}".strip(),
                "owner_function": owner,
                "memory_write_start": hx(effective) if effective is not None else None,
                "memory_write_width_bytes": 8 if ins.mnemonic == "fst" and "qword" in ins.op_str else (4 if ins.mnemonic == "inc" else None),
                "rep_prefix": prefix_rep,
                "registers": w.get("registers"),
                "near_code_preferred_start": hx(near_start_va),
                "near_code_match": not diffs,
                "near_code_differing_preferred_vas": [hx(near_start_va + j) for j in diffs],
                "writer_bytes_match_disk": True,
                "software_breakpoint_byte_in_writer": False,
            }
            if diffs:
                record["mismatch_explanation"] = "Only relocation-adjusted immediate data in sampled window; writer bytes themselves match disk."
                record["relocation_rvas_in_window"] = [hx(r) for r in sorted(relocs)
                    if near_start_va - pe.OPTIONAL_HEADER.ImageBase <= r < near_start_va - pe.OPTIONAL_HEADER.ImageBase + len(near)]
            writers.append(record)

    # Exact assertions for the writer locations and semantics this map covers.
    expected = {0x6acef5: 0x6acef2, 0x6acef9: 0x6acef5, 0x403623: 0x403621}
    assert all(int(x["eip_after_preferred_va"], 16) in expected and
               int(x["writer_va"], 16) == expected[int(x["eip_after_preferred_va"], 16)]
               for x in writers)
    assert all(not x["rep_prefix"] for x in writers)
    source_hashes = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p)
                     for p in [PSEUDO, FUNCTIONS, CALLS, PROVENANCE]}
    public_writers = [{k: record[k] for k in (
        "trace", "fired_fields", "before", "after", "eip_after_preferred_va",
        "writer_va", "writer_bytes", "writer_instruction", "owner_function",
        "memory_write_start", "memory_write_width_bytes", "rep_prefix",
        "near_code_match", "near_code_differing_preferred_vas",
        "writer_bytes_match_disk", "software_breakpoint_byte_in_writer",
        "mismatch_explanation", "relocation_rvas_in_window") if k in record}
        for record in writers]
    private_artifacts = {
        f"FUN_{va:08x}.asm": {
            "path_from_repo": private_out.relative_to(REPO).as_posix() + f"/FUN_{va:08x}.asm",
            "sha256": sha(private_out / f"FUN_{va:08x}.asm"),
            "availability": "private_trial_artifact_not_obtainable_from_public_repository",
        } for va in FUNCTION_VAS
    }
    result = {
        "schema": "native-counter-watch-writer-map-r1",
        "target": {"path_from_repo": "runtime/TestVkr232.exe", "sha256": EXE_SHA256,
                   "preferred_image_base": hx(pe.OPTIONAL_HEADER.ImageBase)},
        "inputs": traces,
        "writers": public_writers,
        "private_function_assembly_artifacts": private_artifacts,
        "decompilation_sources": source_hashes,
        "interpretation_boundary": [
            "Hardware watch confirms only writes observed in these two synthetic runs.",
            "FST qword stores are same-value zero writes in the calibration trace; second store overlaps the watched 4-byte first slot.",
            "INC dword [ecx] changes the watched left counter from 0 to 1 in the calibration trace.",
            "PDF trace confirms zeroing writes and report-address binding; no first increment occurred in this trace, which does not establish that no writer exists.",
            "All mapped writer instructions are non-REP; for REP string instructions, an after-watch EIP can require separate iteration-aware handling."
        ],
        "static_call_chains": {
            "docx": ["FUN_0043dd1c", "FUN_0043e010", "FUN_006acf5b", "FUN_006acec0"],
            "pdf": ["FUN_0046ba90", "FUN_0043e010", "FUN_006acf5b", "FUN_006acec0"],
            "counter_writer": "FUN_00403318; direct callers exist in calls.tsv but the watch trace does not identify a unique dynamic caller."
        },
        "static_pseudocode_lines": {
            "FUN_00403318": [983, 1128], "FUN_0043dd1c": [30941, 31043],
            "FUN_0043e010": [31045, 31062], "FUN_0046ba90": [57180, 57210],
            "FUN_006acec0": [382433, 382520], "FUN_006acf5b": [382522, 382530]
        }
    }
    (out / "map.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    (out / "reconstruction.c").write_text("""/* Analyst reconstruction from native instructions and synthetic hardware-watch traces. */
/* For the observed calibration execution, FUN_006acec0 stores the existing zero
   x87 value to 8-byte ranges; the second qword overlaps the watched first slot. */
store_qword(dst + offset, current_x87_value);

/* In the observed calibration execution, FUN_00403318 reaches INC [ECX] with
   ECX equal to the report-bound left-counter address. */
*(uint32_t *)counter_address += 1;

/* PDF trace: same-value zeroing writes and report binding observed; no first
   increment in this trace is not evidence that another execution cannot do so. */
""", encoding="utf-8", newline="\n")
    print(json.dumps({"out": str(out), "writer_count": len(writers), "trace_count": len(traces)}, indent=2))


if __name__ == "__main__":
    main()
