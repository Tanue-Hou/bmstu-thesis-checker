# 新版逐动作修复范围

build232只开放一个动作：**硕士 DOCX 普通正文字号异常改为14pt**。要求明确传入 `font_size_anomalies`、`work_type=master`、`body_font_pt=14`，Normal样式必须明确为14pt，正文须有准确的ВВЕДЕНИЕ锚点，文档限一个纵向节。

```powershell
py scripts/thesis_cli.py --out plan.json plan thesis.docx --native-build 232 --work-type master --actions font_size_anomalies --body-font-pt 14
py scripts/thesis_cli.py --out receipt.json apply thesis.docx --plan plan.json --output-dir repaired
```

只修改锚点之后、Normal样式、较长普通段落中的小于8pt或大于18pt文字。整段含公式、域、图片、超链接、内容控件、修订、编号属性或脚注引用时跳过。封面、图题/标题、表格、上下标、隐藏文字、页眉页脚均保留；未改变的公式仍可能被原程序提示。

A4、颜色、PDF、博士/NKR、学位论文和其他字号目标仍未开放232修复。历史230动作保留原有独立证据范围；不要借230入口宣称新版验证通过。

三种不同字节输入在新版原程序执行：过小正文、过大正文、标准正文配受保护异常。相同字节的副本显式复用同一采集，不伪造六次执行。两种正文异常修复后正文摘录消失，公式提示保留；纯保护对照零改动。逐项逆转日志所列字号后，整个document.xml必须与原始字节一致；其他ZIP部件逐字节一致。

通过命令行调用独立Word实例以只读方式导出三份PDF，共9页。5张不同页面经视觉检查；封面和公式图表页在三个输入之间像素哈希完全相同。有限样本布局验证不保证任意真实论文自动排版正确。

执行时核验修复实现及证据哈希、输入哈希、预览计划ID。输出新副本、逐项修改日志及本地232重查结果，不覆盖原件。

[验收门](../evidence/v028/complex-repair/acceptance.json) · [原程序与XML验证](../evidence/v028/complex-repair/structural-native-validation.json) · [CLI渲染记录](../evidence/v028/complex-repair/rendered/render-receipt.json)
