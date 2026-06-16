# BMSTU 论文格式检查器 🎓

---

[![License](https://img.shields.io/badge/License-MIT-gold.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

---

**BMSTU 论文格式检查器** 是一个本地运行的 Codex/MCP 插件，专门针对鲍曼国立技术大学（BMSTU）毕业论文（ВКР）格式要求进行自动化预审检查。它基于干净重写的规则引擎，支持 `.docx` 和 `.pdf` 格式，能够快速识别结构、格式、图片和词典层面的问题，并给出中文修复建议和 Word 操作路径。

## 功能特性

- **文档入口检查**：空文档、受保护文档、不支持格式识别
- **结构检查**：缺少 Введение/Заключение、缺少参考文献、体量不足等问题
- **格式检查**：
  - 页面尺寸（A4）、页边距、页眉页脚距离
  - 首行缩进 1.25cm、行距 1.5、表格行距单倍
  - 字号 12pt 以上、字体缩放正常范围
  - 文字颜色/背景符合要求
- **图片检查**：图片总大小超限、像素尺寸过大、浮动图片、标注过小
- **词典检查**：拉丁/西里尔混用眼形符替换、可疑俄文拼写组合（规避查重识别）
- **BMSTU/GOST 标准兼容**：所有规则经过验证匹配官方要求
- **结构化输出**：JSON 原始数据 + Markdown 中文报告
- **MCP 工具集成**：Codex 原生支持 4 个工具接口

## 每条检查结果包含

| 信息 | 说明 |
|------|------|
| 严重程度 | 错误 / 警告 / 仅需人工确认 |
| 定位信息 | 页码、段落号、表格编号/行号、图片编号 |
| 中文解释 | 问题是什么 |
| 触发原因 | 为什么这是个问题 |
| 修复建议 | 怎么改 |
| Word 操作路径 | 在 Word 界面哪里点击修改 |
| 查重影响 | 是否影响反抄袭检测 |

## 安装（Codex 本地插件）

1. 克隆到本地：
```bash
git clone https://github.com/Tanue-Hou/bmstu-thesis-checker.git
```

2. 在你的个人 `marketplace.json` 中添加：
```json
{
  "plugins": [
    {
      "name": "bmstu-thesis-checker",
      "source": {
        "source": "local",
        "path": "/path/to/bmstu-thesis-checker"
      }
    }
  ]
}
```

3. 在 Codex 设置 → 插件中安装启用

## 使用方法

### 命令行

```bash
# 检查单个文档输出 Markdown 报告
python scripts/check_document.py path/to/thesis.docx --output report.md

# 检查单个文档输出 JSON
python scripts/check_document.py path/to/thesis.pdf --output result.json

# 跳过指定模块
python scripts/check_document.py path/to/thesis.docx --skip-pictures --skip-dictionary
```

### MCP 工具（Codex 中使用）

- `check_thesis_document(path)` — 检查单个文档
- `check_thesis_folder(folder)` — 检查文件夹中所有支持的文档
- `list_rules()` — 列出所有可用规则
- `explain_rule(rule_id)` — 获取规则的详细中文说明

## 项目结构

```
bmstu-thesis-checker/
├── .codex-plugin/
│   └── plugin.json          # Codex 插件元数据
├── .mcp.json                # MCP 服务配置
├── mcp/
│   └── server.py            # MCP 工具入口
├── skills/
│   └── bmstu-thesis-checker/
│       └── SKILL.md         # Codex Skill 触发说明
├── scripts/
│   ├── check_document.py    # CLI 入口
│   └── testvkr-service/     # 检查核心引擎
│       ├── checkers/        # 五大检查模块
│       ├── parsers/         # docx/pdf 解析器
│       ├── models/          # 数据模型
│       └── rules/
│           ├── rules_verified.json    # 规则定义与阈值
│           └── rule_guidance_zh.json  # 中文修复指导
└── README.md
```

## 依赖

Python 依赖请见 `scripts/testvkr-service/requirements.txt`

## 许可证

MIT - 仅供个人学术使用。

## 版本日志

参见 [CHANGELOG.md](./CHANGELOG.md)
