# BMSTU 论文检查器

当前版本：插件 **0.2.22+codex.20261015**，MCP **0.2.22**。本地检查器处理 DOCX/PDF，提供结构化诊断和可用的来源位置；各规则的适用模式、样本范围和验证状态以报告与规则证据为准。默认检查仍由重建的本地引擎执行；原程序差分是独立的实验功能，不等同学校验收。

当前版本变更和历史版本记录见 [CHANGELOG.md](CHANGELOG.md) 与 [版本说明](releases/v0.2.22.md)。

## 快速开始

需要 Windows 或可运行 Python 3.10+ 的环境，并安装项目依赖：

```powershell
python -m pip install -r requirements-dev.txt
```

从仓库根目录检查一份文档并输出 Markdown 报告：

```powershell
python scripts/check_document.py "C:\path\to\thesis.docx" --work-type master --format markdown --out "C:\path\to\report.md"
```

也可将 JSON、Markdown 和 DOCX 报告一起写入新目录：

```powershell
python scripts/check_document.py "C:\path\to\thesis.pdf" --work-type phd --report-dir "C:\path\to\report"
```

`check_document.py` 支持 `--out`（输出文件）和 `--report-dir`（报告目录），没有 `--output` 选项。另一入口 `scripts/thesis_cli.py` 使用顶层 `--out` 写 JSON，例如：

```powershell
python scripts/thesis_cli.py --out report.json check "C:\path\to\thesis.docx" --work-type master --native-build 232
```

`thesis_cli.py check` 可选 `--detail compact` 控制结构化报告体积；默认 `full` 保持原输出。compact保留完整finding列表和判定字段，每项最多保留3个位置示例及1条证据引用，native段落观察最多保留3条记录，并标明截断。compact报告不能直接交给`review`重新推断，需以`--detail full`重新检查。

## Codex / MCP

`.mcp.json` 配置本地 MCP 服务入口 `py ./mcp/server.py`。插件当前暴露 11 个工具：

- 检查与规则：`check_thesis_document`、`check_thesis_folder`、`list_rules`、`explain_rule`
- 学校配置与版本：`list_school_templates`、`list_native_builds`
- 比较与原生参考：`compare_thesis_results`、`check_native_reference_experimental`、`run_differential_campaign_experimental`
- 修复：`preview_thesis_fixes`、`fix_thesis_copy`

原生参考工具需要用户提供匹配 build232 的 TestVkr 可执行文件，仅支持 Windows 上的硕士/NKR 博士研究资格论文 DOCX/PDF，并保留代码页和文件入口干预记录。详情见[原生对照 CLI 说明](docs/NATIVE_REFERENCE_CLI.zh.md)。

MCP 的 `check_thesis_document` 与 `check_thesis_folder` 也接受可选 `detail: "compact"`；省略时仍返回`full`。压缩仅限报告展示内容，不改变诊断、规则判定或修复资格。

`run_differential_campaign_experimental` 是额外的有界 DOCX 对照入口：需显式提供固定种子规格和匹配的 TestVkr232 可执行文件，结果须保存在工作区 `private_trials`。MCP每次最多处理4个变体、启动8次原生运行并进行4次缩减评估；只比较选定诊断族的消息/finding分组数。它不是完整模糊测试平台、学校规范裁判或自动规则升级入口。说明见[差分测试指南](docs/DIFFERENTIAL_TESTING.zh.md)。

## 验证与修复边界

- build232 的检测验证按规则、文档模式、格式和受测配置分别登记；不能把一个上下文的证据外推到其他文档。
- 诊断为零不代表通过 TestVkr 或学校验收；有些发现只供人工复核。
- 自动修复权限与检测验证分开。目前 build232 仅开放已验证范围内硕士正文异常字号调整；其他操作依照[修复范围说明](docs/BUILD232_REPAIR.zh.md)。
- 真实论文和报告可能包含私人内容，应保存在本地私有目录，不提交仓库。

## 深入资料

[原生232版式规则证据](docs/NATIVE_PARAGRAPH_RULES_232.zh.md) · [字号证据](docs/NATIVE_FONT_RULES_232.zh.md) · [图片与图形证据](docs/NATIVE_IMAGE_RULE_232.zh.md) · [版本历史](docs/VERSION_HISTORY.zh.md) · [规则执行链](docs/RULE_CHAIN.zh.md)

## 许可

插件元数据将许可标记为 `UNLICENSED`，仓库未附独立的 `LICENSE` 文件。此 README 不作 MIT 或其他开源许可声明；许可政策未在此变更。
