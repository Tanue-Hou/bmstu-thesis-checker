# BMSTU Thesis Checker (Codex Plugin)

A local Codex plugin for checking BMSTU (Bauman Moscow State Technical University) graduate theses (VKR) against formatting and structure requirements.

## Features

- Supports `.docx` and `.pdf` documents
- Multiple check modules:
  - Entry validation (empty/protected documents, format check)
  - Structure check (Введение, Заключение, references, size)
  - Word/PDF format check (A4, margins, indent, line spacing, font size, etc.)
  - Image check (size, resolution, captions)
  - Dictionary/homoglyph check (Latin/Cyrillic mixing, suspicious spellings)
- BMSTU/GOST compliant rules
- Structured JSON output + Markdown report
- Chinese guidance with Word fix instructions
- MCP tools for Codex integration

## Installation (Codex)

1. Add to your personal marketplace:
```json
{
  "plugins": [
    {
      "name": "bmstu-thesis-checker",
      "source": {
        "source": "local",
        "path": "/path/to/bmstu-thesis-checker"
      }
    }
  ]
}
```

2. Install in Codex settings → Plugins

## Usage

### CLI
```bash
python scripts/check_document.py path/to/thesis.docx --output report.md
python scripts/check_document.py path/to/thesis.pdf --output result.json
```

### MCP Tools (Codex)
- `check_thesis_document(path)` - Check a single document
- `check_thesis_folder(folder)` - Check all supported documents in a folder
- `list_rules()` - List all available rules
- `explain_rule(rule_id)` - Get detailed explanation for a rule

## Rules

All rules are verified against BMSTU VKR requirements. Each finding includes:
- Severity (error/warning/info)
- Location (page, paragraph, table/row, image)
- Chinese explanation
- Fix suggestion with Word navigation path
- Whether it affects anti-plagiarism check

## License

UNLICENSED - for personal use.
