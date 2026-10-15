# 页眉页脚距离集成证据

本轮把已经恢复的TestVkr232距离谓词接入正式本地CLI、MCP与Skill，仅新增硕士/NKR博士的单普通显式section检测上下文，不扩大副本修复。

- `audit.json`：改变后的本地模型与v0.2.22保留的16个原程序比较/递增分支对照；不是16次新的原程序执行。
- `aggregation-domain-controls/`：4次全新原程序执行，覆盖两个字段同时为0/1440、两种模式；每次两处递增、一组诊断、本地两处属性定位。第二次INC后的内存未单独采样，限制保留。
- `numeric-recompute.*`：独立有理数重算1441个整数输入的float32存储与比较，新增原程序执行为0。
- `migration-receipt.json`：317组唯一已验证输入/模式的本地修改前后重放，全部非目标finding语义、定位、验证状态和修复资格一致。完整JSONL留本地private_trials，公开只放聚合哈希与实现变化。
- `private-case-summary.json`：17份真实案例本地复查，0错误、原件不变、非目标结果全一致；不包含案例内容、名称或路径，也不是学校合规裁定。
- `full-regression.log`：初次完整运行的新增测试旧断言失败记录；`full-regression-r2.log`为固定测试契约后186项完整通过记录。`test_native_section_model.r2.py.txt`保存该次实际测试源码。
- `mcp-cli-receipt.json`：21项实际stdio MCP与1项CLI调用，原程序新增执行为0。
- `closure-receipt.json`：原始12个合成边界输入的7项诊断族计数差异全部闭环为0项，原生缓存哈希和完成收据重验；不是总体准确率。
- 三个`antigravity-*review`目录为独立模型意见；`antigravity-resolution.zh.md`记录采纳与纠正。认证日志保留私有，模型意见不替代原程序证据。

全部公开DOCX均来自合成baseline。原程序EXE、真实论文和详细私有结果不在本目录。多section、缺失/继承属性、页眉页脚故事体、公式、表格、绘图等仍是待验证范围；没有诊断不等于学校通过。
