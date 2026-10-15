# BMSTU 论文检查器 · v0.2.17

当前版本：插件 **0.2.17+codex.20261015** / MCP **0.2.17**。

v0.2.17：29次原程序字号分支验证覆盖硕士/NKR、字符数边界、空格/UTF16、文本框顺序状态及两类样式继承。修正普通小字号与tiny分槽、空白/表情漏计和文本框归属；新增准确run/XML定位。仅提升受测DOCX配置，副本修复范围不扩大。[说明](releases/v0.2.17.md)。

v0.2.16：20个有效原程序输入恢复独立图形越界诊断，确认横纵向包含等值的边界、旋转轴选择和原始几何字段。图形与文本框越界分开，新增XML/旋转/所选宽高定位；保留并排除一批生成失败样本，修复权限不扩大。[说明](releases/v0.2.16.md)。

v0.2.15：13个原生A4横纵向文本框输入恢复尺寸越界诊断，确认严格边界及越界优先于小框计数；修正长窄框误报，区分位置越界和尺寸越界。新增XML定位及受限检测证据，其他图形边界仍待恢复。[说明](releases/v0.2.15.md)。

v0.2.14：增加32个原程序文本框单因素/单位边界输入，确认形状层自适应与文本框层设置差异，按原生float32换算支持cm/pt/in/无单位。补齐实际宽/高分支证据，扩大受测简单VML覆盖，px/pc仍不提升验证；修复权限不变。[说明](releases/v0.2.14.md)。

v0.2.13：恢复[浮动图片和文本框四条诊断](docs/NATIVE_DRAWINGS_232.zh.md)，15个原程序合成输入确认面积、尺寸和数量边界。修正浮动图片及普通正文小字误报，新增XML/文本框定位；仅提升已验证232 DOCX/NKR配置，自动修复权限不扩大。[发布说明](releases/v0.2.13.md)。

v0.2.12：动态确认[图片字节大小判据](docs/NATIVE_IMAGE_BYTES_232.zh.md)，修正232 DOCX累计大小模型导致的误报和漏报，保留“代码30000000字节、文案40Mb”的差异。新增逐图ZIP条目与XML定位、版本限定证据；不扩大自动修复。[发布说明](releases/v0.2.12.md)。

v0.2.11：恢复[图片检查业务链](docs/NATIVE_IMAGE_RULE_232.zh.md)，用6个DOCX/PDF边界和实际分支确认232像素判据；修正原生图片单位乱码，修复PDF资源别名重复计数。独立引擎仅在已验证的博士PNG配置中提升该规则，修复权限不扩大。[发布说明](releases/v0.2.11.md)。

v0.2.10：[原程序后台对照](docs/NATIVE_REFERENCE_CLI.zh.md)扩展到硕士/博士 NKR 的 DOCX 和 PDF，新增12个合成输入的真实原生验证、模式码与格式加载器防错。保留图片单位乱码这一已知差异；独立复刻与自动修复权限没有扩大。[发布说明](releases/v0.2.10.md)。

v0.2.9：新增 [原程序后台对照 CLI / MCP](docs/NATIVE_REFERENCE_CLI.zh.md)，在中文 Windows 上对硕士 DOCX 返回原生诊断 JSON，不需要操作文件对话框。已完成实际篇幅分支边界和复杂 DOCX 的13条原程序诊断对照。工具仍依赖用户提供的 TestVkr232，并明确记录定向干预；不是独立复刻，不扩大自动修复。见 [发布说明](releases/v0.2.9.md)。

v0.2.8：完成剩余164条逐项源事实复核；对特殊内容、校名模板和表格行高降低误导性修改建议；以原程序、XML逐字节及CLI Word渲染证据，开放[硕士普通正文字号一项新版修复](docs/BUILD232_REPAIR.zh.md)。学校合规仍需正式条款，不能把这些案例当标准答案。

[版本迭代](docs/VERSION_HISTORY.zh.md) · [规则执行与证据链](docs/RULE_CHAIN.zh.md) · [v0.2.7发布说明](releases/v0.2.7.md) · [Skill入口](skills/bmstu-thesis-checker/SKILL.md)

规则是否可靠以精确格式/论文类型、样本范围和证据哈希为准；本地检查零诊断不代表原程序通过。仓库保留原程序对照、合成样本、截图和副本修改记录。

## 0.2.6 新版 TestVkr 与逐条交叉对照

已接入build232身份与版本隔离，完成17份案例原输出采集和逐条类别对照；修正表格封面/内容控件目录遗漏，新增MCP版本查询和对照工具。案例、原程序均不是唯一标准答案；NKR对学位论文仅作试探，232自动修复尚未验证。

[新版对照与边界](docs/BUILD232_CROSS_CHECK.zh.md) · [本轮证据](evidence/build-232/) · [v0.2.6说明](releases/v0.2.6.md)

## 0.2.5 学校参考与真实案例试用（历史阶段）

当时原程序采集待完成；现已由0.2.6完成新版采集，上面的当前范围为准。

新增两个有出处且适用性待确认的学校参考配置、PDF页/坐标与DOCX XML/段落定位、案例交叉检测台账、预览哈希保护和封面保护。真实论文是案例，不能当标准答案；本轮真实案例的TestVkr对照采集因窗口控制故障仍待完成，不宣称准确率或原程序全通过。

[学校参考](docs/SCHOOL_TEMPLATES.zh.md) · [真实论文试用流程](docs/REAL_TRIAL_WORKFLOW.zh.md) · [v0.2.5说明](releases/v0.2.5.md)

## 0.2.4 多页PDF与博士副本修复

新增3页图表PDF后续页反例、13/14页结构对照与博士DOCX修复前后原程序复查。PDF的18.5/19/24/36/72磅均未产生大字号警告，不能套用DOCX的18磅上限。修复NBSP参考文献标题误报、博士摘要与目录标题漏检；PDF几何/页码/目录对应等未覆盖检查显式列出。

博士单节纵向DOCX现在支持A4、异常正文大小和非黑文字的副本修复，实测原程序4条诊断降至0条，5项修改全部有可逆日志，正文/表格/图表/其他ZIP成员保持不变。博士边距及PDF仍不自动修改。详见 [本轮验收报告](evidence/multipage-phd-repair/REPORT.zh.md) 和 [使用范围](skills/bmstu-thesis-checker/references/multipage-phd-repair.md)。以下版本记录以各自轮次为限。

## 0.2.3 本轮验证

博士DOCX边距25/10/20/20毫米、容差±0.2毫米已通过原程序与相邻twip边界对照。修复表格字号漏检和跨格式验证状态串用；博士PDF小字号、A4、颜色、图像面积有独立证据。原程序29个输入与10个规则上下文配对，详见 [证据报告](evidence/format-expansion/REPORT.zh.md)。PDF结构、大字号上限和自动修复仍未验证；DOCX修复保留表格图像并记录跳过原因。

# 0.2.2 硕士／博士封面、结构和篇幅验证

硕士原样例6条诊断经封面、结构、篇幅逐步对照后降至0条。硕士48折算页、900字符每页、43200字符边界及附录A目录页码47／48已实测。博士对应 НКР аспиранта，要求 ОГЛАВЛЕНИЕ 和科研资格论文名称；DOCX不再使用10万字符猜测。博士剩余边距警告也已定位：左边距30毫米报警，单独改为25毫米后样例无意见（其他边距10／20／20毫米）；容差未测定。

新增9项有适用模式和独立证据的诊断判据，现有MCP检查入口直接提供结果；结构及篇幅只给人工修订建议。副本修复仍限本科／硕士已验证的格式操作。证据入口：`evidence/graduate-structure/summary.json`；详细边界：`skills/bmstu-thesis-checker/references/graduate-modes.md`。

以下为历史版本记录，其未验证声明以对应版本为限。

# 0.2.1 硕士模式补充验证

硕士（master）模式新增7个格式对照样本和2个修复前后复查样本。字号下限/上限、A4纸张、文字颜色四条规则与原程序一致；修复后相关三类警告消失，诊断从9条降为6条。正文文字及其他DOCX部件保持不变。证据：`evidence/dynamic-master/summary.json`。

MCP修复工具支持 `work_type: "master"`；命令行修复支持 `--work-type master`。只修改新副本并保留修改记录。硕士封面、结构、篇幅阈值、图片规则及PDF尚未得到本轮验证。样例保留原本科封面文字以隔离模式变化，因此不能据此证明硕士封面合规。

# BMSTU 论文格式检查器 🎓

0.2.0：已完成 12 个原程序对照样本，五项规则通过这批正例/负例及边界检查（DOCX、本科模式）；另有修复前后两个样本复查。
新增 `preview_thesis_fixes` 和 `fix_thesis_copy`，支持在新副本上修正 A4 页面、异常正文字号、非黑文字，并生成逐项 JSON 修改记录。
原文件、公式、域、超链接、表格文字、页眉页脚及图片保留。图片不自动压缩；行距和首行缩进因对照差异继续人工复核。
最新证据入口：`evidence/dynamic-pairs/summary.json`。

```powershell
py scripts/repair_document.py thesis.docx --dry-run
py scripts/repair_document.py thesis.docx --output-dir repaired --body-font-pt 14
```

2026-10-14 复核：旧分析中的八行“阈值表”已被逐字节证实为 OpenJPEG 小波归一化系数。
12.01pt、139.3% 和 540px 不能由这些表推导为论文格式阈值。
目前使用的原程序静态默认字号界限为 8pt/18pt；图片检查改为原始宽度乘高度超过 16,000,000 像素。
这些是异常检查界限，不是正文排版建议；正文应遵循学校模板。
下面保留 0.1.3 的静态复核背景；当前动态验证范围以 0.2.0 说明和规则表中的 scope 为准。
DOCX 已支持文档默认值、段落/字符样式及 basedOn 继承；条件表格样式、编号和主题属性仍有限制。

本地验证：`py scripts/run_revision_validation.py`。证据保存在 `evidence/2026-10-14/`。

---

[![License](https://img.shields.io/badge/License-MIT-gold.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

---

**BMSTU 论文格式检查器** 是一个本地运行的 Codex/MCP 插件，专门针对鲍曼国立技术大学（BMSTU）毕业论文（ВКР）格式要求进行自动化预审检查。它基于干净重写的规则引擎，支持 `.docx` 和 `.pdf` 格式，能够快速识别结构、格式、图片和词典层面的问题，并给出中文修复建议和 Word 操作路径。

## 功能特性

- **文档入口检查**：空文档、受保护文档、不支持格式识别
- **结构检查**：缺少 Введение/Заключение、缺少参考文献、体量不足等问题
- **格式检查**：
  - 页面尺寸（A4）、页边距、页眉页脚距离
  - 首行缩进 1.25cm、行距 1.5、表格行距单倍
  - 异常字号界限 8pt/18pt（不作为正文字号建议）、字体缩放范围提示
  - 文字颜色/背景符合要求
- **图片检查**：图片总大小超限、像素尺寸过大、浮动图片、标注过小
- **词典检查**：拉丁/西里尔混用眼形符替换、可疑俄文拼写组合（规避查重识别）
- **BMSTU/GOST 标准兼容**：规则包含本地策略与启发式；尚未完成与原版 TestVkr 的逐条动态对照
- **结构化输出**：JSON 原始数据 + Markdown 中文报告
- **MCP 工具集成**：提供 6 个工具接口，包含修复预览和副本修复

## 每条检查结果包含

| 信息 | 说明 |
|------|------|
| 严重程度 | 错误 / 警告 / 仅需人工确认 |
| 定位信息 | 页码、段落号、表格编号/行号、图片编号 |
| 中文解释 | 问题是什么 |
| 触发原因 | 为什么这是个问题 |
| 修复建议 | 怎么改 |
| Word 操作路径 | 在 Word 界面哪里点击修改 |
| 查重影响 | 是否影响反抄袭检测 |

## 安装（Codex 本地插件）

1. 克隆到本地：
```bash
git clone https://github.com/Tanue-Hou/bmstu-thesis-checker.git
```

2. 在你的个人 `marketplace.json` 中添加：
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

3. 在 Codex 设置 → 插件中安装启用

## 使用方法

### 命令行

```bash
# 检查单个文档输出 Markdown 报告
python scripts/check_document.py path/to/thesis.docx --format markdown --out report.md

# 检查单个文档输出 JSON
python scripts/check_document.py path/to/thesis.pdf --output result.json

# 跳过指定模块
python scripts/check_document.py path/to/thesis.docx --skip-pictures --skip-dictionary
```

### MCP 工具（Codex 中使用）

- `check_thesis_document(path)` — 检查单个文档
- `check_thesis_folder(folder)` — 检查文件夹中所有支持的文档
- `list_rules()` — 列出所有可用规则
- `explain_rule(rule_id)` — 获取规则的详细中文说明

## 项目结构

```
bmstu-thesis-checker/
├── .codex-plugin/
│   └── plugin.json          # Codex 插件元数据
├── .mcp.json                # MCP 服务配置
├── mcp/
│   └── server.py            # MCP 工具入口
├── skills/
│   └── bmstu-thesis-checker/
│       └── SKILL.md         # Codex Skill 触发说明
├── scripts/
│   ├── check_document.py    # CLI 入口
│   └── testvkr-service/     # 检查核心引擎
│       ├── checkers/        # 五大检查模块
│       ├── parsers/         # docx/pdf 解析器
│       ├── models/          # 数据模型
│       └── rules/
│           ├── rules_verified.json    # 规则定义与阈值
│           └── rule_guidance_zh.json  # 中文修复指导
└── README.md
```

## 依赖

Python 依赖请见 `scripts/testvkr-service/requirements.txt`

## 许可证

当前插件元数据标记为 UNLICENSED，仓库尚未附独立许可证；本次发布不变更该元数据。

## 版本日志

参见 [CHANGELOG.md](./CHANGELOG.md)
# v0.2.7 更新

新增[后台JSON CLI](docs/AGENT_CLI.zh.md)、[行为重建伪源码](docs/RECONSTRUCTED_ALGORITHM.zh.md)和[新版机器码反编译](evidence/agent-v027/decompilation/provenance.json)。17案例修正13组名称识别误报；298条证据处置仍含待判定项目。新版副本修复尚未开放，详见[发布边界](releases/v0.2.7.md)。
