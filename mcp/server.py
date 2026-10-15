import json
import sys
from argparse import Namespace
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = PLUGIN_ROOT / "scripts"
SERVICE_ROOT = SCRIPTS_ROOT / "testvkr-service"
sys.path.insert(0, str(SCRIPTS_ROOT))
sys.path.insert(0, str(SERVICE_ROOT))

if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from check_document import check_file, load_rule_guidance, load_rule_registry, write_report_bundle
from repair_document import repair_copy
from compare_native_trial import compare,load_capture
from native_builds import BUILDS,require_build
from school_templates import BUILTINS, load_template


SERVER_NAME = "BMSTU Thesis Checker"
SERVER_VERSION = "0.2.8"
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


def send(message):
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def send_result(message_id, result):
    send({"jsonrpc": "2.0", "id": message_id, "result": result})


def send_error(message_id, code, message):
    send({"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}})


def require_string(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value.strip()


def make_args(args):
    work_type = args.get("work_type") or "bachelor"
    if work_type not in {"bachelor", "specialist", "master", "phd"}:
        raise ValueError("work_type must be one of bachelor, specialist, master, phd.")
    return Namespace(
        work_type=work_type,
        native_build=args.get("native_build",232),
        template_id=args.get("template_id"),template_path=args.get("template_path"),document_kind=args.get("document_kind","auto"),
        skip_structure=bool(args.get("skip_structure")),
        skip_pictures=bool(args.get("skip_pictures")),
        skip_word_format=bool(args.get("skip_word_format")),
        skip_dictionary=bool(args.get("skip_dictionary")),
    )


def check_document_tool(args):
    path = Path(require_string(args.get("file_path"), "file_path")).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"File does not exist: {path}")
    result = check_file(path, make_args(args))
    if args.get("report_dir"):
        result["report_paths"] = write_report_bundle(result, args["report_dir"])
    return {
        "content": [{"type": "text", "text": f"Checked {path.name}: {result['summary']['total']} findings."}],
        "structuredContent": result,
    }


def list_document_files(folder, recursive=True):
    root = Path(require_string(folder, "folder_path")).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Folder does not exist: {root}")
    iterator = root.rglob("*") if recursive else root.glob("*")
    return sorted(p for p in iterator if p.is_file() and p.suffix.lower() in {".docx", ".pdf"})


def check_folder_tool(args):
    files = list_document_files(args.get("folder_path"), args.get("recursive", True) is not False)
    checker_args = make_args(args)
    results = [check_file(path, checker_args) for path in files]
    if args.get("report_dir"):
        for result in results:
            result["report_paths"] = write_report_bundle(result, args["report_dir"])
    summary = {
        "files": len(results),
        "findings": sum(item["summary"]["total"] for item in results),
        "critical": sum(item["summary"]["critical"] for item in results),
        "major": sum(item["summary"]["major"] for item in results),
        "warning": sum(item["summary"]["warning"] for item in results),
        "info": sum(item["summary"]["info"] for item in results),
    }
    return {
        "content": [{"type": "text", "text": f"Checked {summary['files']} files: {summary['findings']} findings."}],
        "structuredContent": {"folder": str(Path(args.get("folder_path")).resolve()), "summary": summary, "results": results},
    }


def merged_rules():
    registry = load_rule_registry()
    guidance = load_rule_guidance()
    rules = []
    for rule_id, rule in registry.items():
        rules.append({
            **rule,
            "guidance_zh": {
                **guidance.get("default", {}),
                **guidance.get(rule_id, {}),
            },
        })
    return sorted(rules, key=lambda item: item["rule_id"])


def repair_tool(args, dry_run=False):
    result = repair_copy(require_string(args.get('file_path'),'file_path'),
                         output_dir=args.get('output_dir'), actions=args.get('actions'),
                         body_font_pt=args.get('body_font_pt'),
                         work_type=args.get('work_type','bachelor'), dry_run=dry_run,expected_input_sha256=args.get('expected_input_sha256'),native_build=args.get("native_build",230))
    return {'content':[{'type':'text','text':f"{'Planned' if dry_run else 'Applied'} {len(result['changes'])} formatting changes; source unchanged: {result['source_unchanged']}."}],
            'structuredContent':result}


def tool_list_result():
    return {
        "tools": [
            {"name":"list_native_builds","description":"Known TestVkr identities and validation boundaries; no cross-build evidence transfer.","inputSchema":{"type":"object","properties":{}},"annotations":{"readOnlyHint":True,"destructiveHint":False}},
            {"name":"compare_thesis_results","description":"Compare retained native diagnostics with a local report, verify hashes, retain every diagnostic/finding; no ground-truth or accuracy claim.","inputSchema":{"type":"object","properties":{"local_report_path":{"type":"string"},"native_capture_path":{"type":"string"}},"required":["local_report_path","native_capture_path"]},"annotations":{"readOnlyHint":True,"destructiveHint":False}},
            {"name":"list_school_templates","description":"List sourced school reference profiles and unconfirmed applicability; no native-proof promotion.","inputSchema":{"type":"object","properties":{}},"annotations":{"readOnlyHint":True,"destructiveHint":False}},
            {
                'name':'preview_thesis_fixes',
                'description':'Preview conservative DOCX fixes using dynamically validated rules. Writes no document.',
                'inputSchema':{'type':'object','properties':{
                    'file_path':{'type':'string'},
                    'actions':{'type':'array','items':{'type':'string','enum':['page_size_a4','font_size_anomalies','text_color_black']}},
                    'body_font_pt':{'type':'number'},
                    'native_build':{'type':'integer','enum':[230,232],'default':230,'description':'230 historical;232 independently gated master ordinary-body font action to14pt only'},
                    'expected_input_sha256':{'type':'string','description':'Preview source hash; reject changed inputs'},
                    'work_type':{'type':'string','enum':['bachelor','master','phd'],'default':'bachelor'}},'required':['file_path']},
                'annotations':{'readOnlyHint':True,'destructiveHint':False,'openWorldHint':False}
            },
            {
                'name':'fix_thesis_copy',
                'description':'Create a new repaired DOCX copy and JSON change log. Never overwrite the original. PDF, images, equations, tables and headers are not edited.',
                'inputSchema':{'type':'object','properties':{
                    'file_path':{'type':'string'},'output_dir':{'type':'string'},
                    'actions':{'type':'array','items':{'type':'string','enum':['page_size_a4','font_size_anomalies','text_color_black']}},
                    'body_font_pt':{'type':'number'},
                    'native_build':{'type':'integer','enum':[230,232],'default':230,'description':'230 historical;232 independently gated master ordinary-body font action to14pt only'},
                    'expected_input_sha256':{'type':'string','description':'Preview source hash; reject changed inputs'},
                    'work_type':{'type':'string','enum':['bachelor','master','phd'],'default':'bachelor'}},'required':['file_path']},
                'annotations':{'readOnlyHint':False,'destructiveHint':False,'idempotentHint':False,'openWorldHint':False}
            },
            {
                "name": "check_thesis_document",
                "title": "Check Thesis Document",
                "description": "Check one DOCX/PDF thesis file and return structured bilingual findings.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Absolute path to a .docx or .pdf file."},
                        "work_type": {"type": "string", "enum": ["bachelor", "specialist", "master", "phd"], "default": "bachelor"},
                        "native_build":{"type":"integer","enum":[230,232],"default":232,"description":"Fixed original-program reference; build230 proof never transfers to232"},
                        "template_id":{"type":"string","description":"Optional school reference profile, separate from native proof"},
                        "template_path":{"type":"string"},
                        "document_kind":{"type":"string","enum":["auto","vkr","nkr","dissertation"],"default":"auto"},
                        "skip_structure": {"type": "boolean", "default": False},
                        "skip_pictures": {"type": "boolean", "default": False},
                        "skip_word_format": {"type": "boolean", "default": False},
                        "skip_dictionary": {"type": "boolean", "default": False},
                        "report_dir": {"type": "string", "description": "Optional output folder for JSON, Markdown, and DOCX report files."},
                    },
                    "required": ["file_path"],
                },
                "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
            },
            {
                "name": "check_thesis_folder",
                "title": "Check Thesis Folder",
                "description": "Check all DOCX/PDF files in a folder and return a summary plus per-file findings.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "folder_path": {"type": "string", "description": "Absolute path to a folder."},
                        "recursive": {"type": "boolean", "default": True},
                        "work_type": {"type": "string", "enum": ["bachelor", "specialist", "master", "phd"], "default": "bachelor"},
                        "native_build":{"type":"integer","enum":[230,232],"default":232,"description":"Fixed original-program reference; build230 proof never transfers to232"},
                        "template_id":{"type":"string","description":"Optional school reference profile, separate from native proof"},
                        "template_path":{"type":"string"},
                        "document_kind":{"type":"string","enum":["auto","vkr","nkr","dissertation"],"default":"auto"},
                        "skip_structure": {"type": "boolean", "default": False},
                        "skip_pictures": {"type": "boolean", "default": False},
                        "skip_word_format": {"type": "boolean", "default": False},
                        "skip_dictionary": {"type": "boolean", "default": False},
                        "report_dir": {"type": "string", "description": "Optional output folder for per-file JSON, Markdown, and DOCX report files."},
                    },
                    "required": ["folder_path"],
                },
                "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
            },
            {
                "name": "list_rules",
                "title": "List Thesis Rules",
                "description": "List known rules with thresholds, source addresses, confidence, samples, and Chinese guidance.",
                "inputSchema": {"type": "object", "properties": {}},
                "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
            },
            {
                "name": "explain_rule",
                "title": "Explain Thesis Rule",
                "description": "Explain one rule by rule_id with threshold, source, confidence, samples, and Chinese guidance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"rule_id": {"type": "string"}},
                    "required": ["rule_id"],
                },
                "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
            },
        ]
    }


def handle_tool_call(params):
    name = params.get("name")
    args = params.get("arguments") or {}
    if name == "list_native_builds":
        from repair_build232 import capability
        return {"content":[{"type":"text","text":"Build-specific repair scope is independent from whole-rule detection proof."}],"structuredContent":{"builds":BUILDS,"rule_evidence_build":230,"current_build":232,"repair_evidence_build":230,"build232_repair_capability":capability()}}
    if name == "compare_thesis_results":
        local=json.loads(Path(require_string(args.get("local_report_path"),"local_report_path")).read_text(encoding="utf-8-sig"))
        result=compare(local,load_capture(require_string(args.get("native_capture_path"),"native_capture_path")))
        return {"content":[{"type":"text","text":result["status"]}],"structuredContent":result}
    if name == "list_school_templates":
        profiles=[load_template(p.stem) for p in sorted(BUILTINS.glob("*.json"))]
        return {"content":[{"type":"text","text":"School references require department/year applicability review."}],"structuredContent":{"templates":profiles}}
    if name == 'preview_thesis_fixes':
        return repair_tool(args, dry_run=True)
    if name == 'fix_thesis_copy':
        return repair_tool(args, dry_run=False)
    if name == "check_thesis_document":
        return check_document_tool(args)
    if name == "check_thesis_folder":
        return check_folder_tool(args)
    if name == "list_rules":
        rules = merged_rules()
        return {
            "content": [{"type": "text", "text": f"Loaded {len(rules)} rules."}],
            "structuredContent": {"rules": rules},
        }
    if name == "explain_rule":
        rule_id = require_string(args.get("rule_id"), "rule_id")
        for rule in merged_rules():
            if rule["rule_id"] == rule_id:
                return {
                    "content": [{"type": "text", "text": f"{rule_id}: {rule['guidance_zh'].get('title_zh', 'rule')}"}],
                    "structuredContent": rule,
                }
        raise ValueError(f"Unknown rule_id: {rule_id}")
    raise ValueError(f"Unknown tool: {name or ''}")


def handle(message):
    message_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    if method == "initialize":
        send_result(message_id, {
            "protocolVersion": params.get("protocolVersion", "2025-11-25"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": "Use these tools to check BMSTU VKR/thesis DOCX and PDF documents and return bilingual findings with Chinese fix guidance.",
        })
        return

    if method == "ping":
        send_result(message_id, {})
        return

    if method == "tools/list":
        send_result(message_id, tool_list_result())
        return

    if method == "tools/call":
        try:
            send_result(message_id, handle_tool_call(params))
        except Exception as exc:
            send_error(message_id, INTERNAL_ERROR, str(exc))
        return

    if message_id is not None:
        send_error(message_id, METHOD_NOT_FOUND, f"Method not found: {method}")


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            handle(json.loads(line))
        except Exception as exc:
            send_error(None, INVALID_PARAMS, str(exc))


if __name__ == "__main__":
    main()
