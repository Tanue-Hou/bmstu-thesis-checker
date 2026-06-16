---
name: bmstu-thesis-checker
description: Check Russian BMSTU VKR/thesis DOCX and PDF files using a local clean-room rules engine derived from TestVkr reverse-engineering signals plus BMSTU/GOST-style formatting rules. Use when the user asks to inspect a thesis, diploma, VKR, dissertation, scientific paper, DOCX, or PDF for formatting, structure, images, dictionary/homoglyph issues, and problem locations.
---

# BMSTU Thesis Checker

Use this skill to check `.docx` and `.pdf` thesis-style documents with the bundled local rules engine.
The plugin also exposes MCP tools for direct Codex use: `check_thesis_document`, `check_thesis_folder`, `list_rules`, and `explain_rule`.

## Scope

This is a clean-room checker, not a byte-for-byte clone of `TestVkr.exe`. It is based on:

- recovered TestVkr strings and high-confidence thresholds,
- recovered threshold table/function analysis,
- BMSTU/GOST-style formatting requirements,
- local regression samples in the original analysis workspace.

Report confidence clearly:

- `high`: supported by recovered strings/thresholds and sample coverage.
- `medium`: supported by standard/BMSTU convention or strong heuristic.
- `low`: heuristic and not dynamically verified against the original EXE.

## Command

Run from any working directory:

```powershell
py "$env:USERPROFILE\plugins\bmstu-thesis-checker\scripts\check_document.py" "C:\path\to\document.docx" --format json
```

For a Markdown report:

```powershell
py "$env:USERPROFILE\plugins\bmstu-thesis-checker\scripts\check_document.py" "C:\path\to\document.docx" --format markdown --out "C:\path\to\report.md"
```

Supported options:

- `--work-type bachelor|specialist|master|phd`
- `--skip-structure`
- `--skip-pictures`
- `--skip-word-format`
- `--skip-dictionary`
- `--format json|markdown`
- `--out <path>`

## Workflow

1. If the user provides a document path, run `scripts/check_document.py` on that file.
2. Prefer JSON output for machine inspection, Markdown output for a user-facing report.
3. Summarize by severity first: critical, major, warning, info.
4. Include the rule id, confidence, Russian observed message, Chinese explanation, trigger reason, fix suggestion, Word operation path, threshold, and location when present.
5. Use the fix checklist groups when the user wants an actionable review: must fix, should fix, manual review, optional.
6. If the user asks whether it matches TestVkr exactly, state that dynamic EXE comparison is still required for exact behavioral equivalence.

## Useful paths

- Rule registry: `scripts/testvkr-service/rules/rules_verified.json`
- Chinese rule guidance: `scripts/testvkr-service/rules/rule_guidance_zh.json`
- Engine entry point: `scripts/check_document.py`
- MCP server: `mcp/server.py`
- Service code: `scripts/testvkr-service/`
