# 复杂 DOCX：section 距离独立计数验证

本目录为合成技术输入，不是真实论文，也不是学校格式标准。`manifest.json` 固定输入、生成器及基线哈希。`native-receipt.json` 只有状态为 `passed_native_complex_section_observations` 才表示本批完成。

原程序观测除了比较返回值和两处递增分支，还在最终报告门 `0x0047e293` 核验栈槽指针、ECX 与 section parser 计数地址别名，读取最终计数，并对照完整报告中的目标诊断分组。原程序每次检查由专属隐藏进程执行，输入副本和原始执行日志留在项目私有目录。公开证据只含合成输入和其结果。

覆盖实际页眉页脚/PAGE 域、普通表格、简单 OMML 公式、内嵌 PNG、合成图表及组合输入，分别运行 master 和 NKR phd。不能据此宣称任意复杂文档、博士学位论文规范或自动修复通过。

**r1 图表存在结构疑点**：series marker 排在 cat/val 之后，lineChart 缺少自身 axId。原程序完成检查不等于图表符合 Office schema 或可正确呈现。因此 r1 图表和组合案例只证明原程序对这些确切字节的行为。`../complex-section-r2-final/` 修正这两处问题，但完整 XSD/Word 渲染仍未验证；被取代的中间生成批次归档在项目私有目录 `private_trials/complex-section-r1/superseded-generator-run`，不用于推广规则。

`static-section-map.*` 保留独立静态调用链分析，其“尚未捕获动态别名”描述针对该静态记录。后续实际动态证据在 `native/*/trace.json` 和批次回执中，不改写先前的证据边界。

两个 Antigravity 任务分工审查输入与判据，均因认证/网络失败而没有评审结论。公开保留提示词与失败回执，认证日志留私有目录；失败不计作独立复核通过。

当前仅增加观测和回归证据，生产检测支持域、MCP 判据与副本修复范围保持原先验证边界。推广需另行完成样本有效性、非目标回归和发布验收。
