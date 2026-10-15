# 规则执行与证据链

v0.2.8：新增逐项源事实复核和特殊角色分流；build232只独立开放硕士普通正文字号改14pt这一修复上下文。检测验证状态不因此全局升级。执行顺序：查询精确能力 → 预览 → 输入hash/计划ID/实现和证据hash一致 → 新副本与修改日志 → 232本地重查。CLI Word渲染保护对照与原程序结果均留证。[范围](BUILD232_REPAIR.zh.md)

v0.2.7追加：候选检测 → 源位置与属性 → 原程序版本/上下文证据 → `action_eligibility`（模式、参考适用性、内容角色）→ 条款/页面复核 → 独立修复验证 → 预览哈希与计划ID → 新副本与修改日志。候选数量减少不等于准确率提高的量化证明；build232修复门仍关闭。参见[后台CLI](AGENT_CLI.zh.md)和[伪源码说明](RECONSTRUCTED_ALGORITHM.zh.md)。

当前注册表包含32个规则ID，其中18个规则ID在明确适用范围内有原程序对照，合计35个格式/论文类型上下文。数量由本脚本读取注册表计算。此统计不代表每项规则适用于所有格式、所有论文或所有内容结构。

```mermaid
flowchart TD
  A[DOCX或PDF + 论文类型] --> B[入口检查: 空文档/保护状态]
  B --> C{格式解析}
  C --> D[DOCX: 默认样式/继承链/直接格式/表格/图片]
  C --> E[PDF: 页/文字片段/字号/颜色/图片]
  D --> F[结构 → 图片 → Word格式 → 字典]
  E --> F
  F --> G[规则ID + 属性测量 + 位置]
  G --> H{精确格式:论文类型有证据?}
  H -- 否 --> I[pending + 人工复核]
  H -- 是 --> J[核对样本范围/谓词/策略/证据哈希]
  J -- 不满足 --> I
  J -- 满足 --> K[verified_against_original]
  I --> L[中文报告/JSON/缺口说明]
  K --> L
  L --> M{用户要求副本修复?}
  M -- 是 --> N[动作白名单 + 预览 + 再验上下文与哈希]
  N --> O[博士额外验修复前后原程序证据/单纵向节]
  O --> P[新DOCX副本 + changes.json + 本地复查]
  P --> Q[保留原文件/文字/表格/图像/特殊内容]
```

## 规则来源与提高验证状态的条件

1. 原程序资源、字串、常量和恢复伪代码只产生候选规则；静态发现本身不构成动态等价证据。
2. 冻结合成输入并记录SHA256，在指定原程序build与论文类型下实际运行，保存完整文本和截图。
3. 正反对照及边界样本与本地谓词比较，通过后绑定verification_by_context[format:work_type]。
4. 输出时同时检查证据哈希、运行策略、内容配置与特定谓词支持标志。不满足条件即降为pending。
5. 聚合verified_formats / verified_work_types只是展示字段，禁止做笛卡尔积推断；修复还需要动作白名单，博士模式另验修复前后证据。

权威数据：[注册表](../scripts/testvkr-service/rules/rules_verified.json)；入口：[check_document.py](../scripts/check_document.py)；修复：[repair_document.py](../scripts/repair_document.py)；MCP：[server.py](../mcp/server.py)。

## 已有原程序证据的规则上下文

下面只列存在证据绑定的上下文。每条的有限样本范围、阈值和证据哈希以注册表对应context为准；“已验证”不是整篇论文认证。

| 规则ID | 独立验证上下文 | 主要证据 |
|---|---|---|
| `Word.FontSizeTooSmall` | `docx:bachelor`、`docx:master`、`docx:phd`、`pdf:phd` | [dynamic-master](../evidence/dynamic-master/comparison.json)、[dynamic-pairs](../evidence/dynamic-pairs/comparison.json)、[format-expansion](../evidence/format-expansion/comparison.json)、[multipage-phd-repair](../evidence/multipage-phd-repair/comparison.json) |
| `Word.PageSizeNotA4` | `docx:bachelor`、`docx:master`、`docx:phd`、`pdf:phd` | [dynamic-master](../evidence/dynamic-master/comparison.json)、[dynamic-pairs](../evidence/dynamic-pairs/comparison.json)、[format-expansion](../evidence/format-expansion/comparison.json)、[multipage-phd-repair](../evidence/multipage-phd-repair/comparison.json) |
| `Word.LeftMarginInvalid` | `docx:phd` | [format-expansion](../evidence/format-expansion/comparison.json) |
| `Word.RightMarginInvalid` | `docx:phd` | [format-expansion](../evidence/format-expansion/comparison.json) |
| `Word.TopMarginInvalid` | `docx:phd` | [format-expansion](../evidence/format-expansion/comparison.json) |
| `Word.BottomMarginInvalid` | `docx:phd` | [format-expansion](../evidence/format-expansion/comparison.json) |
| `Pic.PixelSizeTooLarge` | `docx:bachelor`、`docx:phd`、`pdf:phd` | [dynamic-pairs](../evidence/dynamic-pairs/comparison.json)、[format-expansion](../evidence/format-expansion/comparison.json)、[multipage-phd-repair](../evidence/multipage-phd-repair/comparison.json) |
| `Word.FontSizeTooLarge` | `docx:bachelor`、`docx:master`、`docx:phd` | [dynamic-master](../evidence/dynamic-master/comparison.json)、[dynamic-pairs](../evidence/dynamic-pairs/comparison.json)、[multipage-phd-repair](../evidence/multipage-phd-repair/comparison.json) |
| `Word.TextColorNotBlack` | `docx:bachelor`、`docx:master`、`docx:phd`、`pdf:phd` | [dynamic-master](../evidence/dynamic-master/comparison.json)、[dynamic-pairs](../evidence/dynamic-pairs/comparison.json)、[format-expansion](../evidence/format-expansion/comparison.json)、[multipage-phd-repair](../evidence/multipage-phd-repair/comparison.json) |
| `Graduate.UniversityNameInvalid` | `docx:master`、`docx:phd` | [graduate-structure](../evidence/graduate-structure/comparison.json) |
| `Graduate.TitlePageMismatch` | `docx:master`、`docx:phd` | [graduate-structure](../evidence/graduate-structure/comparison.json) |
| `Graduate.WorkNameInvalid` | `docx:phd` | [graduate-structure](../evidence/graduate-structure/comparison.json) |
| `Graduate.RequiredHeadingsMissing` | `docx:master`、`docx:phd` | [graduate-structure](../evidence/graduate-structure/comparison.json) |
| `Graduate.TocEmpty` | `docx:master`、`docx:phd` | [graduate-structure](../evidence/graduate-structure/comparison.json) |
| `Graduate.TocSmall` | `docx:master` | [graduate-structure](../evidence/graduate-structure/comparison.json) |
| `Graduate.AbstractTooShort` | `docx:master` | [graduate-structure](../evidence/graduate-structure/comparison.json) |
| `Graduate.ThesisSizeTooSmall` | `docx:master` | [graduate-structure](../evidence/graduate-structure/comparison.json) |
| `Struct.RequiredHeadingsMissing` | `pdf:phd` | [multipage-phd-repair](../evidence/multipage-phd-repair/comparison.json) |

## 主要阈值与不等价边界

- DOCX字号异常界限：小于8磅、超过18磅，累计违规字符超过10；不是正文推荐字号。博士PDF已测18.5/19/24/36/72磅均无大字号提示，不能套用DOCX上限。
- 原生图片像素面积上限：16000000；不是旧540像素宽度猜测。40Mb图片诊断的存储/解码量语义未独立验证，保持人工复核。
- 博士DOCX边距：左/右/上/下25/10/20/20毫米，容差±0.2毫米；左允许1406–1428 twips，相邻1405、1429失败。仅所测单节普通文本配置有边距证明，不自动修改边距。
- 硕士篇幅：48折算页、每页900个去首尾空白UTF-16单位；43199/43200和附录A目录页码47/48有动态边界对照。不是Word实际分页，带图表补偿未验证。
- 博士build-230分支不选择数值篇幅下限，旧100000字符猜测已停用；不代表学校没有篇幅要求。
- 硕士目录识别条目：小于5为空，5–10少，11的对照通过。摘要单段与三实质段对照已测；350俄语字符精确边界仅静态，不当作动态边界验证。

## 自动修复链

支持本科/硕士DOCX与单节纵向博士DOCX：A4、异常正文大小、非黑文字。字号目标来自用户或已知Normal样式。每次创建唯一新副本和changes.json，记录源/输出哈希、位置、原属性、修改后属性、跳过原因与本地复查。博士模式额外要求repair_evidence_ref哈希完整。
表格文字、图片、域、公式、超链接、修订内容、文本框、内容控件、页眉页脚保持原样。PDF、博士边距、行距、缩进和结构不自动修复；不承诺修改任意论文后均通过原程序。

## 当前PDF缺口

图表格式对照覆盖博士模式1–3页、无旋转、嵌入Times New Roman+ToUnicode、每页最多一张PNG。摘要与博士目录标题缺失另有13/14页文字结构对照，不据此扩大图表格式证明到任意页数。
PDF几何边距、页边文字、页码/页眉页脚位置、目录页码与正文对应、封面及参考文献完整性尚未复制。报告保留native_comparison_limits；本地零诊断不代表原程序通过。

完整结果：[本轮验收](../evidence/multipage-phd-repair/REPORT.zh.md)、[0.2.3验收](../evidence/format-expansion/REPORT.zh.md)、[Skill](../skills/bmstu-thesis-checker/SKILL.md)。

## 0.2.5 学校与案例证据分支

源文件字节哈希 → 模式/文档类型 → 解析与源坐标 → 原程序异常规则（原冻结上下文）＋独立学校参考规则 → 候选问题与人工判定 → 预览计划/哈希 → 受限副本修复 → 本地及排版QA/原程序复测。

Template.* 始终独立于 native verification；学位论文不继承NKR证据。真实论文不预设合格。原程序采集只有经过输入/模式/build/输出哈希校验才进入对照，未采集保留pending。案例内容和哈希不进入公共证据；公开的本地回归不证明真实论文原程序通过。

## 0.2.6 版本隔离与交叉对照

程序build+SHA256 → 同字节案例+固定模式 → 原诊断/UIA/截图哈希 → 本地报告选定版本 → 每条诊断/候选的类别关系 → 源属性/学校条款/页面人工判定。232四字号控制样本独立保存；不把230证据跨版本转移。真实案例不作标准答案，也不自动升级规则状态。
