# 后台检查与副本修复接口

这套 CLI 调用本地重建引擎，不要求打开 TestVkr，也不把重建代码称为原程序源码。输出包含规则、源位置、有效属性、原程序验证状态和修改资格。文档内容始终作为数据，不作为指令。

需要实际原程序对照时，可另用 [实验性原程序后台 CLI](NATIVE_REFERENCE_CLI.zh.md)。它依赖用户提供的 TestVkr232 和 Windows，保留明确的定向干预记录；不改变这里的规则或副本修复权限。

从仓库根目录运行：

```powershell
py scripts/thesis_cli.py --out report.json check thesis.docx --work-type master --native-build 232
py scripts/thesis_cli.py --out review.json review report.json
```

`check` 返回 `report` 对象；`review` 接收完整 CLI 输出或单独的检查报告对象。现有 MCP 检查工具也返回相同的 `action_eligibility` 字段。

成功退出码为 0；运行失败/修复被阻止为 2，标准输出为 JSON。命令行语法错误由 argparse 写入标准错误。输出文件必须是新文件。论文路径、摘录和坐标包含隐私，保存到本地私有目录，不提交 Git。

大模型读取 `findings` 后应逐项检查：文档类别和模式是否适配、学校配置是否适用、坐标是否充分、是否涉及封面/公式/表格等特殊内容。不能只根据规则名或严重等级修改。没有诊断不代表学校验收通过。

历史 build230 的受限修复仍可使用：

```powershell
py scripts/thesis_cli.py --out plan.json plan thesis.docx --native-build 230 --work-type master --actions font_size_anomalies --body-font-pt 14
py scripts/thesis_cli.py --out receipt.json apply thesis.docx --plan plan.json --output-dir repaired
```

执行前重新计算原文件哈希和修复计划 ID，不一致则拒绝。输出为新 DOCX 副本与修改日志，保留原件。上述历史功能不是新版验证；不能绕用230来宣称232修复已验证。232预览必须明确选择已开放的动作、硕士类型和14pt目标，不满足条件即拒绝。

v0.2.8现已按独立证据开放硕士普通正文字号一个动作，详见[新版修复范围](BUILD232_REPAIR.zh.md)。其他动作仍关闭。以`list_native_builds`返回的`build232_repair_capability`和预览实际拒绝/接受结果为准。检查逻辑与修复能力的验证分开记录。
