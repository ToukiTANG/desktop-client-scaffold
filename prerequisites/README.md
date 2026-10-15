# 离线运行环境

构建前准备以下微软原版安装包，文件不提交 Git：

- `NDP48-x86-x64-AllOS-ENU.exe`：[.NET Framework 4.8 离线包](https://support.microsoft.com/en-us/servicing/dotnetframework/2019/10/microsoft-net-framework-4-8-offline-installer-for-windows)。
- `MicrosoftEdge_X64_109.0.1518.140.exe`：Win7 SP1 的 WebView2 109 x64 配套包。
- `MicrosoftEdgeWebView2RuntimeInstallerX64.exe`：现代 Windows 的 WebView2 x64 离线包。

安装程序先检测完整 .NET Framework 4.6.2 或以上版本；不满足时安装 4.8，不降级已有版本。Win7 必须为 SP1、64 位；WebView2 必须为 109、实际 x64 文件，且能通过随软件打包的官方加载器查询到版本。先尝试修复安装，复查失败时说明共享组件影响并允许卸载不兼容运行时后重装；失败不会继续安装软件或宣称环境已就绪。静默安装按相同修复策略执行，不显示确认窗口。

环境子安装程序返回 3010/1641 时记录需要重启；Win7 新安装 WebView2 后也要求重启，不直接启动软件。缺少系统补丁、运行时正在使用或安装失败时保留错误和日志，不自动重启、不强制终止其他软件。

安装器诊断与 .NET 日志在 `%ProgramData%\应用可执行名称\InstallerLogs`，WebView2 官方安装日志通常在 `%WINDIR%\Temp\msedge_installer.log`。启动阶段也验证 .NET 和官方加载器，避免仅凭注册表版本号进入白屏。

环境检测工具在构建时预编译为 .NET 4 x64 程序，Win7 无需 PowerShell 动态编译。检测工具故障会单独报错并停止自动替换；主安装日志会复制到上述日志目录的 `Setup.log`，检测报告为 `WebView2Probe.txt`。
