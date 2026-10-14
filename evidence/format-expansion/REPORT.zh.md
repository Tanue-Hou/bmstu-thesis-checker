# 博士边距与复杂DOCX/PDF：本轮验收

本轮29个输入（DOCX 19、PDF 10）均保留原程序文本与截图，10组规则/格式/论文类型正反对照通过。44项本地测试通过，54个源文件哈希复核一致。版本0.2.3，未推送GitHub。

## 已确认并整合

- 博士DOCX边距左/右/上/下25/10/20/20毫米，容差±0.2毫米。左边距相邻twip：1405失败、1406通过、1428通过、1429失败；其他三边目标+0.1通过、+0.3失败。16个边距输入均核对仅改变一个XML属性。静态比较函数004db60c与目标值汇编另存static目录。
- 普通表格和单张PNG图表DOCX：修复表格小字号漏检；合并单元格去重，防止重复计数。复杂干净DOCX原程序显示无意见；表格7磅和图像超过16000000像素的反例分别触发预期提示。
- 博士PDF：小于8磅、非A4、非黑文字和超大像素面积有配对证据；普通表格文字和PNG图片的组合也测试了。当前验证内容配置限制为单页、无旋转、嵌入Times New Roman且有ToUnicode、最多一张PNG。
- 验证状态按精确format:work_type选择证据，避免本科DOCX证据被误用于博士PDF。博士模式旧100000字符猜测已停用；这不代表学校没有篇幅要求。

## 修改与保留记录

修改生成器、fixture-modifications.json与margin-modification-records.json记录样本来源、属性变化和哈希。comparison.json记录每个原程序输出与本地结果；*.original.json和*.original-*.png保存实际界面证据。acceptance.json记录复核结果。

副本保留性检查使用master模式执行受支持的字号动作；源文件未改动，副本所有ZIP成员内容一致，实际属性修改0项，表格异常明确跳过并保留人工处理记录。该测试验证保护行为，未在原程序重新检查副本，也不构成博士自动修复认证。日志：evidence\format-expansion\repair_outputs\complex_table7.repaired-d8fcba8260.changes.json。

## 尚未验证

PDF 18.5磅未出现原程序的大字号提示，因此没有移植DOCX的18磅上限。PDF格式探针仍有封面、结构等原程序诊断；这里只接受列明的格式谓词，不声称整篇论文通过。超大PDF图像还触发原程序40Mb提示，此字节量/解码量语义未通过独立边界对照，不提升该规则验证状态。

未覆盖多页/扫描PDF、其他字体编码、复杂嵌套表格、浮动图形、文本框、条件表格样式以及图表对篇幅计算的补偿。博士边距适用于所测单节无装订线普通正文；没有验证多节/横向页。自动修复仍只对受支持本科/硕士DOCX创建副本和修改日志，保留特殊内容；博士默认格式修复和PDF修复不开放。

## 复查入口

运行scripts/verify_format_expansion.py重算配对；scripts/run_revision_validation.py重跑回归和源哈希；scripts/finalize_format_expansion.py审计证据与副本；scripts/finalize_dynamic_evidence.py更新全证据manifest。原程序SHA256见static/margin-provenance.json。
