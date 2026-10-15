# 本地输出体积审计

本审计只从规则注册表和当前私有真实案例 JSON 读取数据。统计脚本只在内存聚合；产物不含论文文字、案例路径/名称/ID、案例哈希或逐例结果。所有数字由脚本计算。

## 结论

规则注册表原始大小为 **2,497,779 bytes**，共 39 条规则、23 个 build/type/work-type 验证上下文；其中 `verification_by_build` 是规则紧凑序列化负载中最大的字段，占 **97.19%**。显式状态分布、按规则顶层状态回退后的解析状态，以及通过生产 `context_evidence_valid` 的证据数分别记录在 `metrics.json`。上下文缺省 `verification_status` 不直接视作验证缺失。

验证证据引用共 9,213 次，其中 2,277 个不同引用；1,978 个引用在多个上下文复用。

17 份本地 JSON 合计 **5,000,887 bytes**，单份中位数 290,819 bytes，最大 536,127 bytes；共 146 个 finding。finding 紧凑序列化最大 82,414 bytes。输出体积主要来自 `findings`；finding 字段中 `evidence_refs` 与 `precise_locations` 占比最大。每条规则在多少份案例中触发、触发实例数，以及各字段体积均为纯聚合统计，见 `metrics.json`。

## 建议

以可选 compact 投影或单独响应模式减小传输量，保留报告结论、计数、分组和每条 finding 的规则、严重度、消息、建议、验证状态、阈值与位置摘要。`evidence_refs`、完整 `precise_locations`、静态来源、样例触发输入和完整验证范围可放在按需 detail 响应中；compact 响应应带证据引用数及位置 occurrence 总数。现有完整 JSON、Markdown 和 DOCX 默认输出保持原样，避免破坏既有消费者，也不要在完整模式静默截断数组。

## 边界

这是当前本地集合的体积和触发频率描述，不用于估计总体误报率、论文规范符合率或准确率。案例内容没有复制到本产物。
