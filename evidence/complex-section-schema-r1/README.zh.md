# 复杂 DOCX 输入有效性：官方 SDK 校验闭环

校验工具为官方 NuGet `DocumentFormat.OpenXml 2.20.0` 的 net46 版本，以 Office2013 为目标，整包只读检查且不限制错误数量。SDK、NuGet 包、校验器源码/二进制、编译器和依赖均有 SHA256 回执。此工具不负责渲染或判断学校格式规范。

结果由 JSON 和测试计算：

| 批次 | 输入 | SDK 无错误 | 处理 |
|---|---:|---:|---|
| r1 | 28 | 16 | 原始字节和原程序结果保留；含图/图表输入不能作有效文档推广依据 |
| r2-final | 8 | 0 | 图表顺序与轴 ID 已修，但锁定属性命名空间仍错 |
| r3-schema | 28 | 28 | 修正图表结构和 `noChangeAspect` 属性命名空间，重新执行原程序对照 |

错误不只是文本解析问题：r1 图表包含不完整/不符顺序的子元素；r1/r2 的 `a:graphicFrameLocks` 把无命名空间的 `noChangeAspect` 属性写成带 a 命名空间。r3 另建输入，不覆盖任何旧输入或证据。

`r3-validated-build.json` 绑定实际编译回执，是当前完整 SDK 校验依据。`r3-validation.json` 保留首次本地编译运行的结果；`r1-validation.json`、`r2-validation.json` 是旧输入的负控。两次 r3 检查均无错误。原程序最终计数/诊断证据另见 `../complex-section-r3-schema/native-receipt.json`，只有其状态为 `passed_native_complex_section_observations` 才表示对照完成。

复查入口在 `scripts/reverse_engineering/`：

1. 将固定版本官方 NuGet 包放到项目 `runtime/openxml-sdk-2.20.0/package.nupkg`，`prepare_openxml_validator.py` 会检查固定包哈希、提取 DLL 并本地编译校验器。
2. `validate_synthetic_docx.py --manifest evidence/complex-section-r3-schema/manifest.json --out evidence/新目录/validation.json` 只读复查合成输入；拒绝覆盖旧结果。
3. `verify_complex_sections.py --evidence complex-section-r3-schema` 验证或恢复本批原程序对照，需要 Windows 和原始 TestVkr232；完整原程序不随仓库发布。

下一步扩大生产支持域前，还需用已冻结的非目标黄金输出检查回归，并明确匹配的结构范围。SDK 零错误不等于 Word 渲染正确，也不等于自动修复或任意复杂 DOCX 已验证。
