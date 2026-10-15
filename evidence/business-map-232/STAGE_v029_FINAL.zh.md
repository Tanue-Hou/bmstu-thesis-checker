# v0.2.9 最终验收

回归 95 项通过；Skill quick validation 通过。MCP 现有 10 个工具，实际原生调用返回复杂匿名 DOCX 的 13 条诊断。源 DOCX 与 EXE 哈希保持不变。

四组硕士篇幅边界的最新记录在 `native-volume-*-r3/`，有实际选择阈值、计数、分母、最终候选和不足分支。复杂案例最新记录在 `native-direct-complex-reference-r3/`；原生 13 条诊断与旧俄语环境证据完整匹配，原截图哈希也已核对。独立核查见 `native-business-verification-r2/verification.json`。

最终复核增加报告完整性防护：`WM_GETTEXT` 返回字符数、字符串长度、读取前后长度必须一致，CLI 还核对原文 UTF-16 长度和长度回执。空白、不完整、编号断裂、缺少完成返回或发生访问异常都拒绝报成功。保留原始 CRLF，避免 Unicode 计数失真。

受控主线程入口现在只用零载荷消息触发，转入共享检查函数前不会消费拖放句柄；不传递跨进程全局内存。只追踪本次创建的进程。CLI 的 DOCX、EXE 和辅助程序副本均在私有目录，不上传 Git。

`stage-v029-final/manifest.json` 是最终源码及证据哈希入口；`stage-v029/` 是上述报告防护复核前的历史快照，不应作为当前源码验收。历史原始记录与失败尝试均保留。

本轮没有扩大自动修复动作。原生包装器仍依赖 TestVkr232，仅开放64位 Windows、64位 Python、硕士 DOCX。博士/PDF、更多真实案例和独立复刻的完整等价尚未完成，总目标继续保留。
