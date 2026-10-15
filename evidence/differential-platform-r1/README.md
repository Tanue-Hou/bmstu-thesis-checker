# DOCX差分平台首轮证据

本目录全部输入来自既有合成baseline或其变异，不含真实论文。完整批量运行数据保留在本地private_trials；公开保留聚合回执、单段反例、16个实际边界分支捕获和我们自己的分析脚本快照。

- `spec.json`、`boundary-spec.json`：不可变种子的属性变异规格。
- `initial-source/`：最初两批执行时的自有平台代码与身份哈希；后续脚本改进不冒充旧批次执行版本。
- `pilot-receipt.json`：各批次运行/缓存计数、40→15→1段缩减及未解决边界；`one-paragraph-counterexample/`含仍保留差异的完整双端报告和源输入。
- `final-*.py.txt`：最终缩减及缓存回放实际使用的平台代码。缓存身份随源代码集合变化，后续版本应新建campaign；不能直接把不同版本的缓存视为有效。
- `final-source-manifest.json`：独立重算并匹配最终执行身份的163个源码/规则文件哈希；明确排除执行后才加入的发布/冻结脚本。实际版本的原生CLI源码也单独保留，换行字节差异不冒充同一个源码哈希。
- `section-boundaries-r2/`：硕士和NKR博士、页眉和页脚、697/698/720/721twips共16项原程序实际比较与递增分支记录。
- `section-function-map.json`、`section-reconstruction.c`：小片段指令与分析者编写的行为伪代码；不是原作者源码。实际INC使用EAX指向parser。
- `mcp-receipt.json`：实际stdio MCP入口验证，11个工具、缓存复用及错误预算拒绝。
- `tests-r1.log`保留最初两项测试因新增focus白名单而需更新模拟映射的失败；后续日志记录修复后结果。
- `antigravity-review/`为去标识设计审查意见，不能充当原程序执行证据；认证运行日志留在私有目录。

初次section观察脚本错误假设EBX是计数基址，虽原程序运行成功，但该验收断言失败；第一次生成输入留在`section-boundaries/`，原始运行留在本地`private_trials/section-distance-branches-r1`。依据实际`INC [EAX+0x28c]`修正验收后新建r2重跑，没有覆盖失败记录。

首轮最小化预算不足，最终空文档删减导致原程序执行失败；两者都没有计入有效一致样本，也没有标记为已证明最小。本轮只定位行为差异，没有更新规则验证、扩大修复或估计准确率。用法及后续缺口见[差分说明](../../docs/DIFFERENTIAL_TESTING.zh.md)。
