# 0.2.4 - Multipage PDF and doctoral copy repair (2026-10-14)

- Native later-page table/font, color, page-size and image probes; exact page locations and bounded proof profiles.
- PDF upper-font probes through 72pt and recovered PDF span path; do not apply DOCX maximum to PDF.
- Normalize PDF NBSP, recognize exact doctoral abstract/TOC headings, report unimplemented native layout/structure checks.
- Doctoral one-portrait-section copy repair with hashed native before/after evidence and reversible XML modification log; preserve tables, drawings and special content.

# 0.2.3 - Doctoral margins and complex format evidence (2026-10-14)

- Native ±0.2 mm doctoral DOCX margins, adjacent-twip boundary probes, table font counting and merged-cell deduplication.
- Separate PhD PDF small-font, A4, color and image-area pairs, including ordinary tables/charts; unsupported PDF upper-font behavior remains pending.
- Exact format:mode proof binding, copy-repair preservation receipt, source hashes and native screenshots.

# BMSTU Thesis Checker Changelog

## 0.2.0 - Original-output verification and copy repair (2026-10-14)

- Retained 12 original-program controlled outputs; five DOCX/bachelor predicates agree with local checks. Line-spacing and first-line-indent differences remain unresolved.
- Added verification context/policy guards and evidence hash checks.
- Added MCP preview/copy-repair tools and CLI, unique output copies, JSON change logs, source integrity checks and local rechecks.
- Repair preserves other ZIP parts, special text, tables, headers/footers and images; supported fixes were rechecked in the original program on a combined fixture.

## 0.1.3 - Evidence and style inheritance repair (2026-10-14)

- Rejected old DWT-table threshold guesses using a byte-exact upstream OpenJPEG comparison.
- Recovered shipped font anomaly defaults of 8pt/18pt and a 16,000,000-pixel native image area limit. Original formatting comparison remains pending.
- Kept legacy claims separate from current evidence; unverified findings now require manual review.
- Resolved document defaults, paragraph/character basedOn styles and direct formatting; preserved table spacing units, explicit hidden=false and zero margins.
- Added reproducible regression fixtures, source hashes, original startup/result captures and recovered pseudocode exports.

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
