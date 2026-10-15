# LEProc.LoaderWrapper.Start IL inspection

只读检查 `LEProc.exe` 中 `LEProc.LoaderWrapper.Start` 的 IL。探针仅加载程序集元数据并读取 IL；没有调用 `Start`、`LeCreateProcess`，也没有启动目标、改写配置或联网。

## 结论

- `LeCreateProcess` 的 `flags` 参数由 `DebugMode` 决定：`DebugMode == true` 时传 `4`，否则传 `0`（`Start` IL `IL_0079`–`IL_0085`）。
- `PROCESS_INFORMATION` 局部结构在调用前初始化为零，并以 `ByRef` 传给 `LeCreateProcess`（`IL_0060`、`IL_0087`、`IL_009d`）；其后读取 `hProcess` 和 `hThread`。
- `LeCreateProcess` 返回 `UInt32`。返回值为零时，代码对 `hProcess` 调用 `WaitForSingleObject(hProcess, 0xffffffff)`，再关闭进程与线程句柄；返回值非零时跳过等待和两次 `CloseHandle`（`IL_00a2`–`IL_00d0`）。因此此处确有无限等待分支，但只在返回值为零时执行。静态 IL 不足以断言该返回值的语义或哪个分支是正常成功路径。

## 可复查文件

- `il.txt`：`Start` 与同一类型其他方法的完整 IL 转储。
- `InspectLEProcStartIL.exe`：用于生成转储的 x86 只读反射探针。
- 探针源：`implementation/scripts/reverse_engineering/InspectLEProcStartIL.cs`，SHA-256 `92CA0F5328DAC64ED005A30468430B8E861517FB3E4E62455A4779A9D20C2D6A`。
- 目标 `runtime/locale-emulator-2.5.0.1/LEProc.exe` SHA-256 `2A81CB20B5B705D84416FD8B1CD9A819B1CAFAECCC0C1E23C289884310EC0461`。

复现命令（项目根目录，使用 .NET Framework 4 编译器）：

```powershell
& 'C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe' /nologo /platform:x86 /out:'D:\Codex项目\analysis_TestVkr\implementation\evidence\locale-loader-il-20261015\InspectLEProcStartIL.exe' 'D:\Codex项目\analysis_TestVkr\implementation\scripts\reverse_engineering\InspectLEProcStartIL.cs'
& 'D:\Codex项目\analysis_TestVkr\implementation\evidence\locale-loader-il-20261015\InspectLEProcStartIL.exe' 'D:\Codex项目\analysis_TestVkr\runtime\locale-emulator-2.5.0.1\LEProc.exe' *> 'D:\Codex项目\analysis_TestVkr\implementation\evidence\locale-loader-il-20261015\il.txt'
```

结论只描述托管层静态 IL；不代表 native `LeCreateProcess` 的内部行为或目标进程的实际运行结果。
