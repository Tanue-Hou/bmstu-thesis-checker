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


SERVER_NAME = "BMSTU Thesis Checker"
SERVER_VERSION = "0.1.2"
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


def tool_list_result():
    return {
        "tools": [
            {
                "name": "check_thesis_document",
                "title": "Check Thesis Document",
                "description": "Check one DOCX/PDF thesis file and return structured bilingual findings.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Absolute path to a .docx or .pdf file."},
                        "work_type": {"type": "string", "enum": ["bachelor", "specialist", "master", "phd"], "default": "bachelor"},
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
