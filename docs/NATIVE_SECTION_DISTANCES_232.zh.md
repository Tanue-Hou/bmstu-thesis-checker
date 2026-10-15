# Native232 页眉、页脚距离检查

此规则只在一个受限 DOCX 档案内复现 TestVkr 232 的页眉和页脚距离判断。原程序把 `w:pgMar/@w:header` 与 `w:pgMar/@w:footer` 的整数 twips 转成单精度毫米，再分别与 12.5 mm 比较；允许差值为单精度 0.2 mm。当前模型对每个显式距离独立计数，并在同一诊断中指出触发的 section 与 XML 属性。

当前证据覆盖单个普通 section、两个显式整数距离（0–1440 twips），且不含表格、绘图、公式、字段、修订、内容控件或其他故事范围。profile 不支持的文档会保留为未验证候选，不会将缺失属性、多 section 或复杂结构解释为通过。

16 条冻结分支来自 master 与 phd 模式，分别改变页眉或页脚字段，并覆盖 697、698、720、721 twips。两种模式和两个字段均观察到相同结果：697 与 721 触发；698 与 720 不触发。边界与静态模型预测的通过区间 698–720 一致。这组结果只支持所测输入、模式和字段，不代表全部 Word 文档或学校格式符合性。

该规则在 Native232 profile 下使用固定的原程序谓词。可配置的 `HEADER_FOOTER_DISTANCE_CM` 与本地容差仍用于旧版 build 230 的既有本地策略；修改设置不会改变 Native232 观察值，也不会把 build 230 的结果升级成原程序验证。该规则不授权自动修复。

另一个独立反例只有一个正文段落，原程序仍输出页眉距离诊断。输入 SHA-256 为 `059fb630a4afd33b18e5b8ed97353dabe17b6063ef190e9a43df557f5a9dedac`，原生结果 SHA-256 为 `0fccc8b5fc9cc7a28732f1e3a6afde0061dd9c89d0a5cf7d9535c1a36ebe3316`。它说明单段落本身可处于受支持 profile；后续删除最终段落使原生执行失败，因此不把它称为已证明的最小反例。

可复查证据：

- [section-function-map.json](../evidence/differential-platform-r1/section-function-map.json)，SHA-256 `78216c74c0080eb8f58403bf9a1375bff47937207a0664111fac2a8e9f3261ed`；映射绑定目标 `runtime/TestVkr232.exe` SHA-256 `5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0`。
- [16 条原生边界回执](../evidence/differential-platform-r1/section-boundaries-r2/receipt.json)，SHA-256 `b28c29f6c6a62d50fd73231141813eecaf8b53a5d93a88b1ded2855d0a618823`。回执记录了每条输入及捕获产物的哈希。
- [单段落反例目录](../evidence/differential-platform-r1/one-paragraph-counterexample/)保存输入、原生文本结果、报告与追踪。

静态映射和有限原生分支测试为实现提供来源证据；它们不证明复杂 section、缺失距离、页眉页脚继承、其他格式或所有文档的行为。对这些输入，当前验证状态仍保持未验证。
