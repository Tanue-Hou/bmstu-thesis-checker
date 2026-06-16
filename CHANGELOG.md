# BMSTU Thesis Checker Changelog

## 0.1.2 - High-quality review reports

- Added review-level conclusion data in `review_summary`.
- Added grouping by location in addition to severity, module, fix priority, and anti-plagiarism impact.
- Improved Markdown report layout with review conclusion, grouped summary, fix checklist, and detailed bilingual findings.
- Added DOCX report generation through `--format docx --out <path>`.
- Added report bundle generation through `--report-dir <path>`, producing:
  - `*_report.json`
  - `*_report.md`
  - `*_report.docx`
- Added MCP `report_dir` support for `check_thesis_document` and `check_thesis_folder`.
- Updated skill documentation for JSON/Markdown/DOCX report workflows.

## 0.1.1 - Chinese report layer and MCP tools

- Added Chinese rule guidance metadata in `scripts/testvkr-service/rules/rule_guidance_zh.json`.
- Added JSON report fields for Chinese explanation, trigger reason, fix suggestion, Word operation path, fix priority, anti-plagiarism impact, comparator, sample triggers, and source address.
- Added Markdown report sections for summary, fix checklist, and bilingual finding details.
- Added grouped report data by severity, module, fix priority, and anti-plagiarism impact.
- Enhanced DOCX location output for paragraph numbers, table row numbers, section numbers, and image numbers where the parser/checker exposes them.
- Added MCP server `mcp/server.py` and `.mcp.json`.
- Added MCP tools:
  - `check_thesis_document`
  - `check_thesis_folder`
  - `list_rules`
  - `explain_rule`
- Updated skill instructions to document the report fields and MCP tools.

Note: Git was not available in the current Windows PATH, so this changelog records the version change until a real git commit can be created.
