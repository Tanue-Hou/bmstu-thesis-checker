# 原程序后台对照 CLI（实验功能，v0.2.11）

本地重建检查仍使用 `scripts/thesis_cli.py`。新增 `scripts/native_reference_cli.py` 调用用户提供的原 TestVkr232，返回其实际诊断 JSON，供定位重建引擎与原程序的差异。

v0.2.20新增开发对照选项`--trace-scale`，在自有隐藏进程记录字符缩放run属性、累计分支及报告门；仍依赖原EXE，不是发现原程序自带CLI。普通检查无需此选项。

目前支持64位 Windows、64位 Python、硕士 VKR / 博士研究资格论文 NKR、DOCX / PDF。`--work-type master` 为默认值，博士须显式传入 `--work-type phd`。这里的博士模式指原程序“НКР аспиранта”，不代表所有博士学位论文标准。需要 Python 3、Windows 自带 .NET Framework 编译器和对应原 EXE；仓库不附带原程序。

```powershell
python scripts/native_reference_cli.py --input "D:\论文\硕士论文.docx" --native-exe "C:\Users\你的用户名\Downloads\TestVkr (2).exe"
```

EXE 必须匹配 build232 的已分析 SHA-256。程序会建立私有输入及 EXE 副本，在新建且隐藏的进程中运行检查，输出 `status`、`diagnostics`、`source_sha256` 和 `evidence_directory`。这些副本、原文诊断、调试记录和辅助程序只保存在项目旁的 `private_trials/native-reference/`，不提交 Git。退出码 0 才表示已观察到解析、结构检查和检查返回，且完整报告采集通过；其余情况返回失败 JSON，不能当作“无问题”。报告按 UTF-16 长度核对读取前后与实际字符数，缺失或截断即失败。

MCP 对应工具为 `check_native_reference_experimental`，参数：

```json
{
  "file_path": "D:\\论文\\硕士论文.docx",
  "native_executable_path": "C:\\Users\\你的用户名\\Downloads\\TestVkr (2).exe",
  "work_type": "master"
}
```

## 实际调用方式与边界

原程序以系统默认代码页解码三份俄语词库和封面模板，在中文系统上产生乱码。工具只对输入完整哈希与这些资源一致的八次转换，把代码页实参从 0 改为 1251；原 EXE 和系统设置不变。随后在已初始化窗体的主线程中，把一次受控拖放接收转到原有共享文件检查入口 `0047a528`，传入有效的 UTF-16 路径对象，保留正常返回位置。

这是带明确干预记录的原程序包装器，仍借用隐藏窗体和原始检查引擎。它不是发现了原程序自带命令行接口，也不是完全独立的开源复刻。无须用户操作桌面；运行期间不能把该进程当作日常交互窗口使用。用户已有 TestVkr、Word 或其他进程不会被附加或关闭。

已验证硕士字符阈值 43199／43200、附录目录页码 47／48 的实际分支；复杂 DOCX 的 13 条诊断与保留的俄语环境结果逐条匹配。v0.2.10 增加12个原生232合成样例，含博士复杂 DOCX、多页图表 PDF、72pt PDF、14页结构与删除摘要的反例。实际模式码必须匹配 master=1、phd=5；对应选择分支必须出现48/0下限及900分母，且必须命中所选格式的加载器。模式或格式错配即失败。

证据入口为 `evidence/business-map-232/native-modes-audit-r1/audit.json`。相同PDF在博士/硕士模式返回10/11条，硕士额外出现缺48页诊断；不能把博士的无篇幅提示套用硕士。数字不是排版实际页数。

v0.2.11 修正了图片过大诊断中“像素”单位的独立ANSI转换：默认在精确输入哈希和调用点匹配时将0/936改为1251，并记录转换前后；不事后替换诊断文本。`--preserve-pixel-codepage --trace-images` 可取得未修正控制组。详情及版本隔离见 [图片判据](NATIVE_IMAGE_RULE_232.zh.md)。其他ANSI字面量尚无完整覆盖证明；有限样例不证明任意论文全规则等价，原程序诊断也不等于学校标准答案。

输出必须标记 `experimental` 与 `completed_instrumented_native_reference`。不要将其伪装为未干预的原程序运行，不用它自动提升本地规则或允许修改论文。已有副本修复继续服从原来的独立验收门槛。
