"""Build release documentation from the actual registry and retained acceptance receipts."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def main():
    reg=read('scripts/testvkr-service/rules/rules_verified.json');rules=[r for r in reg['rules'] if r.get('verification_status')=='verified_against_original'];contexts=sum(len(r.get('verification_by_context',{})) for r in rules);accept=read('evidence/multipage-phd-repair/acceptance.json');validation=read('evidence/2026-10-14/validation.json');assert validation['test_exit_code']==0
    doc=ROOT/'docs';doc.mkdir(exist_ok=True);releases=ROOT/'releases';releases.mkdir(exist_ok=True)
    lines=['# v0.2.4 规则执行与证据链','',f'当前注册表包含{len(reg["rules"])}个规则ID，其中{len(rules)}个规则ID在明确适用范围内有原程序对照，合计{contexts}个格式/论文类型上下文。数量由本脚本读取注册表计算。此统计不代表每项规则适用于所有格式、所有论文或所有内容结构。','',
'''```mermaid
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
''','## 规则来源与提高验证状态的条件','',
'1. 原程序资源、字串、常量和恢复伪代码只产生候选规则；静态发现本身不构成动态等价证据。','2. 冻结合成输入并记录SHA256，在指定原程序build与论文类型下实际运行，保存完整文本和截图。','3. 正反对照及边界样本与本地谓词比较，通过后绑定verification_by_context[format:work_type]。','4. 输出时同时检查证据哈希、运行策略、内容配置与特定谓词支持标志。不满足条件即降为pending。','5. 聚合verified_formats / verified_work_types只是展示字段，禁止做笛卡尔积推断；修复还需要动作白名单，博士模式另验修复前后证据。','',
'权威数据：[注册表](../scripts/testvkr-service/rules/rules_verified.json)；入口：[check_document.py](../scripts/check_document.py)；修复：[repair_document.py](../scripts/repair_document.py)；MCP：[server.py](../mcp/server.py)。','',
'## 已有原程序证据的规则上下文','',
'下面只列存在证据绑定的上下文。每条的有限样本范围、阈值和证据哈希以注册表对应context为准；“已验证”不是整篇论文认证。','',
'| 规则ID | 独立验证上下文 | 主要证据 |','|---|---|---|']
    for r in rules:
        contexts_r=r.get('verification_by_context',{});refs=sorted({p for c in contexts_r.values() for p in c['evidence_refs']});links='、'.join('['+p.split('/')[1]+'](../'+p+')' for p in refs)
        lines.append('| `'+r['rule_id']+'` | '+'、'.join('`'+k+'`' for k in sorted(contexts_r))+' | '+links+' |')
    lines+=['','## 主要阈值与不等价边界','',
'- DOCX字号异常界限：小于8磅、超过18磅，累计违规字符超过10；不是正文推荐字号。博士PDF已测18.5/19/24/36/72磅均无大字号提示，不能套用DOCX上限。',
'- 原生图片像素面积上限：16000000；不是旧540像素宽度猜测。40Mb图片诊断的存储/解码量语义未独立验证，保持人工复核。',
'- 博士DOCX边距：左/右/上/下25/10/20/20毫米，容差±0.2毫米；左允许1406–1428 twips，相邻1405、1429失败。仅所测单节普通文本配置有边距证明，不自动修改边距。',
'- 硕士篇幅：48折算页、每页900个去首尾空白UTF-16单位；43199/43200和附录A目录页码47/48有动态边界对照。不是Word实际分页，带图表补偿未验证。',
'- 博士build-230分支不选择数值篇幅下限，旧100000字符猜测已停用；不代表学校没有篇幅要求。',
'- 硕士目录识别条目：小于5为空，5–10少，11的对照通过。摘要单段与三实质段对照已测；350俄语字符精确边界仅静态，不当作动态边界验证。','',
'## 自动修复链','',
'支持本科/硕士DOCX与单节纵向博士DOCX：A4、异常正文大小、非黑文字。字号目标来自用户或已知Normal样式。每次创建唯一新副本和changes.json，记录源/输出哈希、位置、原属性、修改后属性、跳过原因与本地复查。博士模式额外要求repair_evidence_ref哈希完整。',
'表格文字、图片、域、公式、超链接、修订内容、文本框、内容控件、页眉页脚保持原样。PDF、博士边距、行距、缩进和结构不自动修复；不承诺修改任意论文后均通过原程序。','',
'## 当前PDF缺口','',
'图表格式对照覆盖博士模式1–3页、无旋转、嵌入Times New Roman+ToUnicode、每页最多一张PNG。摘要与博士目录标题缺失另有13/14页文字结构对照，不据此扩大图表格式证明到任意页数。',
'PDF几何边距、页边文字、页码/页眉页脚位置、目录页码与正文对应、封面及参考文献完整性尚未复制。报告保留native_comparison_limits；本地零诊断不代表原程序通过。','',
'完整结果：[本轮验收](../evidence/multipage-phd-repair/REPORT.zh.md)、[0.2.3验收](../evidence/format-expansion/REPORT.zh.md)、[Skill](../skills/bmstu-thesis-checker/SKILL.md)。','']
    (doc/'RULE_CHAIN.zh.md').write_text('\n'.join(lines),encoding='utf-8')
    history='''# 版本演进

当前发布版本：v0.2.4；插件版本0.2.4+codex.20261014；MCP协议返回版本0.2.4。

| 迭代 | 主要变化 | 验证依据与边界 |
|---|---|---|
| v0.1.2 | 原有格式/结构检查、中文报告与DOCX报告包 | 原仓库提交a740fee；当时尚不能把本地策略当作原程序等价规则 |
| 0.1.3 | 修正旧阈值猜测，解析样式继承，恢复伪代码与俄语进程环境 | [静态证据](../evidence/2026-10-14/)；恢复伪代码不是原始源代码 |
| 0.2.0 | 本科DOCX五类正反对照，新增预览与副本修复 | [原程序配对](../evidence/dynamic-pairs/comparison.json)与修复前后输出；行距/缩进差异未提高验证状态 |
| 0.2.1 | 硕士DOCX字号/A4/颜色与副本修复对照 | [硕士矩阵](../evidence/dynamic-master/comparison.json)；不转移到其他格式或模式 |
| 0.2.2 | 硕士/博士封面和结构、硕士篇幅边界，博士目录名称与左边距定位 | [研究生结构矩阵](../evidence/graduate-structure/comparison.json)；不把折算页当实际排版页数 |
| 0.2.3 | 博士四边距±0.2毫米、表格漏检/去重、PDF有限格式对照、精确上下文绑定 | [验收报告](../evidence/format-expansion/REPORT.zh.md)；PDF上限与完整结构未复制 |
| **v0.2.4** | 多页图表PDF、PDF字号/结构差异、博士DOCX副本修复、证据哈希保护 | [验收报告](../evidence/multipage-phd-repair/REPORT.zh.md)；仍保留PDF几何/目录等缺口 |

中间迭代是在同一工作区连续完成的检查点，并非每个都已有独立Git提交或Release。此次统一提交当前实现、Skill、测试、冻结样本、原程序截图与记录，并仅为实际发布的当前版本建立v0.2.4标签。

[规则链](RULE_CHAIN.zh.md) · [v0.2.4发布说明](../releases/v0.2.4.md) · [变更日志](../CHANGELOG.md)
'''
    (doc/'VERSION_HISTORY.zh.md').write_text(history,encoding='utf-8')
    release=f'''# v0.2.4 发布说明

当前本地验证版本归档：插件0.2.4+codex.20261014，MCP 0.2.4。

- 注册表{len(reg['rules'])}个规则ID，其中{len(rules)}个有有限范围原程序对照，合计{contexts}个精确格式/论文类型上下文。
- 最新一轮{accept['native_input_cases']}个原程序输入（PDF {accept['native_pdf_cases']}，DOCX含修复副本{accept['native_docx_cases_including_repair']}），{accept['rule_context_pairs']}组规则上下文配对；{accept['local_tests_passed']}项本地测试通过。
- 博士图表DOCX组合样本原程序{accept['doctoral_repair_native_before_after'][0]}→{accept['doctoral_repair_native_before_after'][1]}条诊断，{accept['doctoral_copy_property_changes']}项属性修改可从日志完全逆转；源文件、文字、表格、图表和其他ZIP成员保留。
- MCP实际预览/副本工具已验证，输出哈希与原程序检查过的副本一致。

## 主要更新

修复样式继承和表格字号漏检、合并单元格重复计数、跨格式验证状态串用、PDF NBSP参考文献标题误报，以及博士PDF摘要/目录标题漏检。DOCX与PDF字号上限独立处理，PDF未沿用DOCX18磅规则。

## 使用与边界

支持DOCX/PDF检查和本科/硕士/博士模式。自动修复仅对支持的DOCX创建副本：A4、异常正文大小、非黑文字；博士限一个纵向节。表格、图片、特殊内容保留并记录跳过原因。PDF和博士边距仍只检查，不自动修改。

PDF原程序几何/页码/目录对应等检查尚未完整重建。所有已验证规则均限具体上下文和样本配置，不能据此宣称整篇论文或整个程序完全等价。

## 安装与复查

```powershell
python -m pip install -r scripts/testvkr-service/requirements.txt
python scripts/check_document.py path/to/thesis.docx --work-type phd --format json
python scripts/repair_document.py path/to/thesis.docx --work-type phd --dry-run
```

副本修复须在用户授权范围内执行，并尊重学校模板。开发测试依赖见requirements-dev.txt：

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

原程序对照的原始文本、截图、合成输入、修改日志和SHA256均保留在evidence目录。历史收据中的Windows绝对路径是原实验环境记录，克隆后不要据此覆盖本机路径；复查请使用仓库内相对路径与哈希。再次动态验证需要自己的原程序和相应俄语进程环境；运行检查器和本地测试无需原EXE。

[版本演进](../docs/VERSION_HISTORY.zh.md) · [规则链](../docs/RULE_CHAIN.zh.md) · [本轮原程序对照验收](../evidence/multipage-phd-repair/REPORT.zh.md) · [完整变更日志](../CHANGELOG.md)
'''
    (releases/'v0.2.4.md').write_text(release,encoding='utf-8')
    print(json.dumps({'registered_rules':len(reg['rules']),'verified_rules':len(rules),'rule_contexts':contexts,'version':'0.2.4'}))
if __name__=='__main__':main()
