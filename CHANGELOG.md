# v0.2.23

- 新增Native232页眉/页脚距离判据：12.5 mm±float32(0.2 mm)，分别检查`w:header`和`w:footer`并提供精确XML属性位置。build230可配置本地策略及±0.5 mm容差保持独立。
- 只注册master和NKR博士DOCX受限上下文：单一纵向A4 section、显式整数距离0..1440 twips，无表格、绘图、公式、字段、修订、内容控件或额外故事部分。不增加修复权限。
- 保留16条边界分支和四次0/1440 twips新原生运行；17份私有案例零执行错误、输入未改且非目标17族全部一致。另对1441个整数twips作不运行原程序的独立有理数复算。这些结果不代表准确率或学校合规。
- 首次186项全量测试记录9错1失败；调整新测试断言后，全量186项重跑通过。三项独立复核促成了float32舍入及哈希依赖声明的更正，均已由反汇编、算术复核和可验证的非自指哈希链支持。
- 详见[发布说明](releases/v0.2.23.md)与[距离证据](docs/NATIVE_SECTION_DISTANCES_232.zh.md)。

# v0.2.22

- 新增实验性MCP工具`run_differential_campaign_experimental`，用固定SHA种子与显式TestVkr232执行有界DOCX单属性变异、所选诊断族计数比较及段落缩减；MCP上限为4个变体、8次原生运行、4次缩减评估。默认检查引擎仍为重建的本地实现。
- 首轮8个变体使用6次新原生运行和2次校验缓存命中；section页眉/页脚距离边界12个变体使用27次新运行、1次缓存命中，观察到7项规则族计数差异和5项相等。这些是受限差分结果，不代表准确率或语义等价。
- 16个硕士/NKR博士section边界分支在697、698、720、721 twips上完成观察；原程序比较目标为12.5±0.2 mm。当前本地规则仍为±0.5 mm，差异暂不并入规则或验证范围，等待单独规则更新。
- 首次有界ddmin从40段缩至15段后达到16次评估上限，其中13次未解决；未认证1-minimal。平台不是完整模糊测试框架，尚不支持PDF、OMML、样式链生成或随机组合。修复权限不扩大。
- 详见[差分测试说明](docs/DIFFERENTIAL_TESTING.zh.md)与[发布说明](releases/v0.2.22.md)。

# v0.2.21

- 为`thesis_cli.py check`及MCP文档/文件夹检查新增可选compact输出；默认`full`保持兼容，review要求完整报告。
- 17份保留的私有案例报告中，compact JSON保持判定字段和位置总数不变；使用相同UTF-8 JSON序列化后，由4,907,702字节降至923,849字节（81.18%）。聚合收据：`evidence/optimization-audit-r1/compact-benchmark.json`。
- 复核6个合成原生计数观察（4次新运行、2个复用捕获）；规范化完整原生报告均与各自基线匹配。负左缩进正向writer控制观察到left槽增量；first槽在这些案例中只观察到初始化复位值，不能据此认定producer或规则不存在。未提升检测验证或扩大修复范围。

# v0.2.20

- 52次硕士/博士原生执行核对字符缩放：普通小缩放31..69%、极小观察槽2..30%、大缩放>130%，UTF16计数>10报告。
- 原程序启用前的文字不累计；大缩放不继承大字号的文本框此前100字符门。补齐表格、文本框、空格/表情、样式继承和直接覆盖对照。
- 增加四个限定检测上下文和准确XML位置；修复算法不变，未开放缩放修复。首行缩进仍待恢复。

# v0.2.19

- 修正原生字号计数启用顺序：本段字号先检查，段落结束后才启用后续检查；精确标题、第61段、表格/文本框空边界按原程序证据处理。
- 原生兼容字号单独解析关联字符样式，并保留普通OOXML字号及既有副本修复路径。
- 76次原生执行、48个不同输入用于受限检测核对；未扩大复杂文档、PDF或副本修复权限。

# v0.2.18

- Integrate native232 activation, negative left/right indent and normalized/truncated line-spacing predicates, with exact paragraph XML locations.
- Validate68 native runs/42 unique inputs, inheritance/override, a single-cell table and1001-paragraph fallback; keep school suggestions separate and unknown profiles pending.
- Bound observation output to matched metadata; no new automatic repair.

# v0.2.17

- Recover font producer branches, half-point comparisons, UTF16 counters and final >10 report gates using29 native master/NKR DOCX executions.
- Correct ordinary-small versus tiny buckets, whitespace/surrogate counting, nested textbox run attribution and stateful textbox large-font gates.
- Verify paragraph/character style inheritance and a single-cell table; add source-bound font-run locations and observation counters.
- Add four exact version/mode/profile contexts. Keep PDF/complex content pending and existing repair permissions unchanged.

# v0.2.16

- Recover independent shape-bounds diagnostics using20 valid native cases with inclusive portrait/landscape boundaries and rotation-bin observations.
- Add Pic.ShapesOutOfBounds and exact XML/selected-dimension locations; keep textbox strict bounds separate.
- Retain raw comparison operands, actual shape branch/counter and static function map; field semantic names remain provisional.
- Exclude six wrongly generated landscape inputs, retain failed experiment provenance and guard against generator variable collisions. Drawing repair remains closed.

# v0.2.15

- Recover textbox dimension overflow with13 actual native A4 portrait/landscape cases, branch hits and report counters.
- Add Pic.LabelsOutOfBounds; fix long/narrow textbox small-label false positives by preserving native branch precedence.
- Separate position exclusion from dimension overflow; add diagnostic family mapping for reconstructed drawing rules.
- Keep larger/unsupported drawing families pending and all drawing repair closed.

# v0.2.14

- Add32 actual native textbox inputs covering unit boundaries, layer-specific fit, insets, empty/long text and larger rectangles.
- Recover native unit multipliers from instructions; match float32 dimensions and width/height branches. Keep px/pc verification pending.
- Correct shape-autofit height false positives while preserving small-width diagnostics; extend bounded VML profiles and exact locations.
- Preserve original output, flags, branches, source hashes and static function map; no new repair permission.

# v0.2.13

- Recover four drawing families using15 actual native synthetic inputs, geometry/counter observations and report branches.
- Correct floating-image area/wrap semantics and replace the build232 body-small-font label heuristic with measured textbox geometry/counts.
- Add precise VML/image locations and four bounded evidence/hash-bound DOCX/NKR contexts; unknown wrap stays unassessed.
- Preserve raw traces and legacy slot-label correction. Keep all drawing repair closed.

# v0.2.12

- Trace per-image ZIP local-header size lookup, unsigned30000000-byte comparison, branch and report counter; preserve the native40Mb text mismatch.
- Fix build232 DOCX aggregation false positive and boundary false negative, with exact image/ZIP/XML locations.
- Retain five native cases including data-descriptor local-zero behavior and a same-input MCP comparison.
- Register only the supported NKR DOCX context; reject ZIP64/ambiguous headers for verification and keep repair permissions unchanged.

# v0.2.11

- Map image predicates through native getters, signed32 comparison, flag, counter and report; retain six real PNG boundary runs and same-input codepage control/treatment.
- Fix the exact ANSI pixel-unit conversion in the owned native process, without rewriting the report.
- Deduplicate PDF resource aliases while preserving placement coordinates.
- Add source/evidence-bound build232 image contexts for the tested postgraduate DOCX/PDF profiles; keep other contexts and all repair gates independent.

# v0.2.10

- Extend experimental original232 CLI/MCP to master / NKR postgraduate DOCX and PDF; verify selected radio, actual mode code, threshold branch, format-specific loader and complete report.
- Retain 12 public synthetic native runs, bounded historical comparisons and actual postgraduate PDF MCP smoke. Preserve a pixel-unit encoding difference rather than claiming complete text equivalence.
- Keep independent-engine validation and all copy-repair permissions unchanged.

# 0.2.8 - Source-level review and independently gated master font repair (2026-10-15)

- Review164 remaining source-fact records individually; retain school-policy/semantic uncertainties instead of declaring compliance.
- Separate name-template, special-role and table-height advice from edit eligibility; add row XML and paragraph role locations.
- Independently accept only build232 master ordinary-body anomalous font repair to14pt; all other232 actions/modes remain closed.
- Retain complex formula/table/figure/field controls, native diagnostic excerpt pairs, exact XML/ZIP preservation and9-page CLI Word rendering with protected-page pixel identity.
- Expose scoped capability in CLI/MCP and bind repair to implementation/evidence hashes, input hash and plan ID; retain changes and local232 recheck.

# 0.2.7 - Evidence dispositions, false-positive fix and agent CLI (2026-10-15)

- Retain individual dispositions for all 298 original private review rows; school compliance remains unresolved where evidence is insufficient.
- Correct oblique Russian VKR cover-name recognition; recheck all17 cases, removing13 confirmed local recognition defects (218 to205 candidate groups).
- Add independent action eligibility without hiding candidates, plus JSON CLI check/review/plan/apply with stale-plan refusal.
- Export actual build232 C-like decompiler output (10191 of10192 discovered functions) and trace both work-name token lists; not original source or complete semantic recovery.
- Retain two synthetic master font repair native before/after pairs. Build232 repair remains closed pending broader protected-content/layout validation.

# 0.2.6 - TestVkr build232 and source-bound cross-checks (2026-10-15)

- Identify build232 independently; bind report/capture/executable/screenshot identities and prevent build230 proof transfer.
- Complete native captures for the 17 private cases; retain all diagnostic/finding comparison rows without treating cases as ground truth.
- Read table covers and SDT TOCs in document order, retain source XML positions, avoid nested textbox duplication and table-only false empty checks.
- Add front-matter/table/heading role hints to font locations and protect retained trial/review directories from overwrite.
- Add MCP list_native_builds and compare_thesis_results; current check reference defaults to232, historical copy repair remains230 only.
- Recheck 7/8/18/18.5pt master DOCX controls in232; no general rule, PDF-degree or232 repair validation claim.

# 0.2.5 - Sourced school references and private real-case trials (2026-10-15)

- Separate school reference profiles from native TestVkr thresholds; distinguish degree dissertations from NKR.
- Add bounded PDF page/bbox and DOCX XML/run/table locations and searchable private trial reports.
- Normalize PDF font variants and recognize dissertation conclusion heading variants.
- Protect recognized cover/front matter in copy repair; bind execution to preview input hash and retain deterministic plan IDs.
- Add school-profile MCP discovery and private native-result comparison with input/output identity checks.
- Real cases are not ground truth. Original-program capture for this corpus remains pending due to window activation failure; no accuracy claim or new native-proof promotion.

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
