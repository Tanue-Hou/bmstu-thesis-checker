# BMSTU Thesis Checker Changelog

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
