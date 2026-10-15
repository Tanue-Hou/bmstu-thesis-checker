# 主窗体 Delphi 事件与文件入口（r1）

目标 `runtime/TestVkr232.exe` SHA-256：`5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0`。资源证据中的 `TTSTWNDMAIN` 是 `TPF0` DFM，负载文件偏移 `6229840`、长度 `6567`、SHA-256 `02009268d287046afa6426436683b4819db1195dc55fae17b2ec3914a2558a18`。根对象是 `TstWndMain: TTstWndMain`。解析到 6 个连续发布方法表记录，每条为“Word记录长度 + 32位代码 VA + ShortString 方法名”；每个 VA 都严格命中 `functions.tsv`。JSON 保存原始记录字节、DFM 事件属性偏移和函数的调用者/被调用者。

## 文件入口

`sbOpen: TSpeedButton.OnClick` 绑定 `sbOpenClick` → `00481b40`。伪代码检查 `TOpenDialog.od` 的执行方法；成功后从对话框取路径并调用共享处理入口 `0047a528`。

文件也能绕过该对话框：`FormCreate` (`00481874`) 调用 `DragAcceptFiles(TRUE)`；消息分发函数 `00482f10` 对 `WM_DROPFILES` (`0x233`) 调用 `00481794`。该处理器通过 `DragQueryFileW` 计数，只在恰好一个文件时取路径并直接调用 `0047a528`；多文件分支显示提示并结束拖放。因此静态证据支持一个内部拖放入口，它与打开按钮共用处理函数。`0047a528` 在函数清单中标记 `failed_or_timeout`，其函数体未成功反编译，内部处理细节未知。

`TimerTimer` (`004818a4`) 绑定 `Timer: TTimer`。伪代码显示它访问 `http://mt5.bmstu.ru/vkr/TestVkr/`、检查 HTTP 状态，并在版本条件满足时提示/打开 URL；未见其调用文件处理入口。`rbBakClick` 绑定多个学位类型单选按钮，`MemoClick` 是 `Memo: TMemo.OnClick`。

本证据只解析 PE 资源、函数表、调用表和现有静态伪代码；未运行目标或操作 UI。Delphi 通过方法表间接分发事件，因此空的直接 caller 列表不表示事件不可达。
