# 首行与左缩进 watchpoint 输入

本清单只复用已存在的合成输入、build-232 原生 trace 和 report；没有重造或执行文件。逐案路径、SHA、计数及 trace/report 哈希见 `manifest.json`。

建议最小 DOCX 组为：`noFirst`（`w:firstLine=0`）、`firstOneInch`（`1440` twips）以及 `negativeLeft` 正控（左缩进 `-1440` twips）。前两份的原生 first/left counter 都是 0；`negativeLeft` 的 left counter 为 1，并命中 `paragraph_left_report_emit`，适合作为 DOCX `+0x290` 写入观察的正控。DOCX `+0x29c` first 计数目前没有已知正控。

PDF 组选一页 pixel-boundary baseline（`pdf_4000x4000.pdf`，1页、pixel branch 未触发）和两个多页对照：`mp_clean.pdf`（3页）与 `structure_clean.pdf`（14页）。后两份来自 build-232 `phd` 原生 capture。当前这些 PDF 报告没有分别记录 first/left counter；不能据此假定 PDF 候选槽已写或未写。

主入口的 PDF parser base 是 `local_78+0x149`。共享主计数索引 `0x51` 的候选 first offset 为 `4*(0x149+0x51)=0x668`；索引 `0x4e` 的候选 left offset 算术为 `4*(0x149+0x4e)=0x65c`。`+0x65c` 仅是从 parser base 与共享槽索引推出的地址，现有材料没有证明 PDF left-indent producer。DOCX 对应偏移则由 `local_74+0x158` 得到 first `+0x29c`、left `+0x290`。所有offset依据及静态索引 SHA 已记录在 manifest；其中 PDF writer 语义仍待动态观察确认。
