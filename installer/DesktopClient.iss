#ifndef AppName
  #define AppName "Desktop Client"
#endif

#ifndef AppId
  #define AppId "F8A49F6C-8A19-4A0E-9D29-4C8F45A9583E"
#endif

#ifndef ExecutableName
  #define ExecutableName "DesktopClient"
#endif

#ifndef InstallerName
  #define InstallerName "DesktopClientSetup"
#endif

#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif


[Setup]

AppId={{{#AppId}}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}

DefaultDirName={autopf}\{#ExecutableName}
DefaultGroupName={#AppName}

OutputDir=..\release
OutputBaseFilename={#InstallerName}-{#AppVersion}

SetupIconFile=..\backend\build_resources\app.ico
UninstallDisplayIcon={app}\{#ExecutableName}.exe

Compression=lzma2
SolidCompression=yes

WizardStyle=modern

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

PrivilegesRequired=admin
SetupLogging=yes
MinVersion=6.1sp1

DisableProgramGroupPage=yes

CloseApplications=yes
RestartApplications=no


[Files]

; ============================================================
; Application
; ============================================================

Source: "..\backend\dist\{#ExecutableName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs


; ============================================================
; WebView2 prerequisites
; ============================================================

; Windows 7:
; pinned WebView2 Runtime 109
Source: "..\prerequisites\MicrosoftEdge_X64_109.0.1518.140.exe"; Flags: dontcopy

 ; .NET 4.8 离线包：缺少 4.6.2 及以上完整版本时安装，不依赖外网。
Source: "..\prerequisites\NDP48-x86-x64-AllOS-ENU.exe"; Flags: dontcopy
; 从本次应用打包产物提取同一套 x64 加载器，避免版本与程序不一致。
Source: "WebView2Probe.exe"; Flags: dontcopy
Source: "WebView2Probe.exe.config"; Flags: dontcopy
Source: "..\backend\dist\{#ExecutableName}\_internal\webview\lib\runtimes\win-x64\native\WebView2Loader.dll"; DestName: "RuntimeProbeLoader.dll"; Flags: dontcopy

; Windows 10 / Windows 11 / Server 2016+:
; Evergreen Standalone Installer x64
Source: "..\prerequisites\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"; Flags: dontcopy


[Tasks]

Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"


[Icons]

Name: "{group}\{#AppName}"; Filename: "{app}\{#ExecutableName}.exe"

Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#ExecutableName}.exe"; Tasks: desktopicon


[Run]

Filename: "{app}\{#ExecutableName}.exe"; Description: "启动 {#AppName}"; Flags: nowait postinstall skipifsilent; Check: ShouldLaunchApplication


[Code]

const
  WebView2RegistryKey =
    'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';

  Win7WebView2InstallerFile =
    'MicrosoftEdge_X64_109.0.1518.140.exe';

  EvergreenWebView2InstallerFile =
    'MicrosoftEdgeWebView2RuntimeInstallerX64.exe';


var
  Win7WebView2InstalledThisRun: Boolean;
  RuntimeRestartRequired: Boolean;
  RuntimeProbeFailed: Boolean;

  WebView2ProgressPage: TOutputMarqueeProgressWizardPage;
  WebView2ProgressVisible: Boolean;


{ ============================================================ }
{ Windows version                                             }
{ ============================================================ }

function IsWindows7: Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);

  Result :=
    (Version.Major = 6) and
    (Version.Minor = 1);
end;


{ ============================================================ }
{ WebView2 progress UI                                        }
{ ============================================================ }

procedure InitializeWizard;
begin
  Win7WebView2InstalledThisRun := False;
  RuntimeRestartRequired := False;
  RuntimeProbeFailed := False;
  WebView2ProgressVisible := False;

  WebView2ProgressPage :=
    CreateOutputMarqueeProgressPage(
      '正在安装运行环境',
      '正在准备 Microsoft Edge WebView2 Runtime...'
    );
end;


procedure ShowWebView2Progress(
  const MainText: String;
  const DetailText: String
);
begin
  WebView2ProgressPage.SetText(
    MainText,
    DetailText
  );

  if not WebView2ProgressVisible then
  begin
    WebView2ProgressPage.Show;
    WebView2ProgressPage.Animate;

    WebView2ProgressVisible := True;
  end;
end;


procedure HideWebView2Progress;
begin
  if WebView2ProgressVisible then
  begin
    WebView2ProgressPage.Hide;

    WebView2ProgressVisible := False;
  end;
end;


{ .NET 检测与安装；重启由主安装程序统一处理，不让子安装程序直接重启。 }
function HasRequiredNetFramework: Boolean;
var Release: Cardinal;
begin
  Result := False;
  Release := 0;
  if RegQueryDWordValue(HKLM64, 'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full', 'Release', Release) then
    Result := Release >= 394802;
  if not Result then
    if RegQueryDWordValue(HKLM32, 'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full', 'Release', Release) then
      Result := Release >= 394802;
  Log(Format('.NET Framework minimum release check: %d; ready=%d', [Release, Ord(Result)]));
end;

function RuntimeLogDirectory: String;
begin
  Result := ExpandConstant('{commonappdata}\{#ExecutableName}\InstallerLogs');
  ForceDirectories(Result);
end;

function EnsureNetFramework: Boolean;
var Code: Integer; LogPath: String;
begin
  Result := HasRequiredNetFramework;
  if Result then Exit;
  LogPath := RuntimeLogDirectory + '\DotNet48.txt';
  ShowWebView2Progress('正在安装 .NET Framework 4.8...', '缺少界面运行环境，正在安装随软件提供的离线包，请稍候。');
  try
    ExtractTemporaryFile('NDP48-x86-x64-AllOS-ENU.exe');
    if not Exec(ExpandConstant('{tmp}\NDP48-x86-x64-AllOS-ENU.exe'),
      '/q /norestart /log "' + LogPath + '"', '', SW_HIDE, ewWaitUntilTerminated, Code) then Exit;
    Log(Format('.NET installer exit code=%d; log=%s', [Code, LogPath]));
    if (Code <> 0) and (Code <> 3010) and (Code <> 1641) then Exit;
    if (Code = 3010) or (Code = 1641) then RuntimeRestartRequired := True;
    Result := HasRequiredNetFramework;
    if not Result then Log('.NET install returned success but registry verification failed');
  finally
    HideWebView2Progress;
  end;
end;

function GetBinaryType(const ApplicationName: String; var BinaryType: Cardinal): Boolean;
  external 'GetBinaryTypeW@kernel32.dll stdcall';

procedure SaveSetupLog;
var SourcePath, TargetPath: String;
begin
  SourcePath := ExpandConstant('{log}');
  TargetPath := RuntimeLogDirectory + '\Setup.log';
  if (SourcePath <> '') and (CompareText(SourcePath, TargetPath) <> 0) then
    if not FileCopy(SourcePath, TargetPath, False) then Log('Cannot copy setup log to ' + TargetPath);
end;

procedure DeinitializeSetup;
begin
  SaveSetupLog;
end;

function IsRuntimeX64AndLoadable(const RuntimeFolder: String; const Version: String): Boolean;
var BinaryType: Cardinal; Code: Integer; ReportPath: String; Report: AnsiString;
begin
  Result := False;
  if not GetBinaryType(RuntimeFolder + '\msedgewebview2.exe', BinaryType) then begin
    Log('Cannot read WebView2 executable architecture: ' + RuntimeFolder); Exit;
  end;
  if BinaryType <> 6 then begin
    Log('WebView2 runtime is not x64: ' + RuntimeFolder); Exit;
  end;
  { 预编译的 .NET 4 x64 检测工具，不依赖客户电脑上的 PowerShell 或编译器。 }
  ExtractTemporaryFile('WebView2Probe.exe');
  ExtractTemporaryFile('WebView2Probe.exe.config');
  ExtractTemporaryFile('RuntimeProbeLoader.dll');
  ReportPath := RuntimeLogDirectory + '\WebView2Probe.txt';
  DeleteFile(ReportPath);
  if not Exec(ExpandConstant('{tmp}\WebView2Probe.exe'),
    '"' + ExpandConstant('{tmp}\RuntimeProbeLoader.dll') + '" "' + RuntimeFolder +
    '" "' + ReportPath + '" "' + Version + '"', '', SW_HIDE, ewWaitUntilTerminated, Code) then begin
    RuntimeProbeFailed := True;
    Log('Cannot start precompiled x64 WebView2 probe'); Exit;
  end;
  if LoadStringFromFile(ReportPath, Report) then Log('WebView2 native probe: ' + UTF8Decode(Report))
  else RuntimeProbeFailed := True;
  if (Code <> 0) and (Code <> 1) then RuntimeProbeFailed := True;
  Log(Format('WebView2 probe exit=%d; probe failure=%d', [Code, Ord(RuntimeProbeFailed)]));
  Result := (Code = 0) and not RuntimeProbeFailed;
end;

{ ============================================================ }
{ WebView2 version                                            }
{ ============================================================ }

function IsValidWebView2Version(
  const Version: String
): Boolean;
begin
  Result :=
    (Version <> '') and
    (Version <> '0.0.0.0');
end;


function IsLegacyWebView2OnModernWindows(
  const Version: String
): Boolean;
begin
  {
    Runtime 109 is retained only for Windows 7.

    Although some 109 builds can theoretically work on
    Windows 10, real deployment has shown installations where
    registry + executable both exist but WebView2 still fails
    during CoreWebView2Environment creation.

    Therefore modern Windows should upgrade 109.x to Evergreen.
  }

  Result := Pos('109.', Version) = 1;
end;


{ ============================================================ }
{ WebView2 registry                                           }
{ ============================================================ }

function GetWebView2Version(
  var Version: String
): Boolean;
begin
  Version := '';

  { ---------------------------------------------------------- }
  { Machine-wide Runtime                                     }
  { ---------------------------------------------------------- }

  Result :=
    RegQueryStringValue(
      HKLM32,
      WebView2RegistryKey,
      'pv',
      Version
    );

  if Result then
    Result := IsValidWebView2Version(Version);


  { ---------------------------------------------------------- }
  { Per-user Runtime                                         }
  { ---------------------------------------------------------- }

  if not Result then
  begin
    Version := '';

    Result :=
      RegQueryStringValue(
        HKCU32,
        WebView2RegistryKey,
        'pv',
        Version
      );

    if Result then
      Result := IsValidWebView2Version(Version);
  end;
end;


{ ============================================================ }
{ Machine-wide Runtime health                                 }
{ ============================================================ }

function IsMachineWebView2RuntimeHealthy(
  var Version: String
): Boolean;
var
  RuntimePath: String;
begin
  Result := False;
  Version := '';

  if not RegQueryStringValue(
    HKLM32,
    WebView2RegistryKey,
    'pv',
    Version
  ) then
  begin
    Log(
      'Machine-wide WebView2 Runtime registry entry not found'
    );

    Exit;
  end;

  if not IsValidWebView2Version(Version) then
  begin
    Log(
      'Machine-wide WebView2 Runtime version is invalid: ' +
      Version
    );

    Exit;
  end;

  RuntimePath :=
    ExpandConstant(
      '{pf32}\Microsoft\EdgeWebView\Application\' +
      Version +
      '\msedgewebview2.exe'
    );

  if FileExists(RuntimePath) then
  begin
    Log(
      'Healthy machine-wide WebView2 Runtime detected: ' +
      Version
    );

    Log(
      'WebView2 executable: ' +
      RuntimePath
    );

    Result := True;
    if IsWindows7 then Result := IsRuntimeX64AndLoadable(ExtractFileDir(RuntimePath), Version);
  end
  else
  begin
    Log(
      'Machine-wide WebView2 registry entry exists, '
      + 'but runtime executable was not found: '
      + RuntimePath
    );
  end;
end;


{ ============================================================ }
{ Per-user Runtime health                                     }
{ ============================================================ }

function IsUserWebView2RuntimeHealthy(
  var Version: String
): Boolean;
var
  RuntimePath: String;
begin
  Result := False;
  Version := '';

  if not RegQueryStringValue(
    HKCU32,
    WebView2RegistryKey,
    'pv',
    Version
  ) then
  begin
    Log(
      'Per-user WebView2 Runtime registry entry not found'
    );

    Exit;
  end;

  if not IsValidWebView2Version(Version) then
  begin
    Log(
      'Per-user WebView2 Runtime version is invalid: ' +
      Version
    );

    Exit;
  end;

  RuntimePath :=
    ExpandConstant(
      '{localappdata}\Microsoft\EdgeWebView\Application\' +
      Version +
      '\msedgewebview2.exe'
    );

  if FileExists(RuntimePath) then
  begin
    Log(
      'Healthy per-user WebView2 Runtime detected: ' +
      Version
    );

    Log(
      'WebView2 executable: ' +
      RuntimePath
    );

    Result := True;
    if IsWindows7 then Result := IsRuntimeX64AndLoadable(ExtractFileDir(RuntimePath), Version);
  end
  else
  begin
    Log(
      'Per-user WebView2 registry entry exists, '
      + 'but runtime executable was not found: '
      + RuntimePath
    );
  end;
end;


{ ============================================================ }
{ Combined Runtime health                                     }
{ ============================================================ }

function GetHealthyWebView2Version(
  var Version: String
): Boolean;
begin
  if IsMachineWebView2RuntimeHealthy(Version) then
  begin
    Result := True;
    Exit;
  end;

  if IsUserWebView2RuntimeHealthy(Version) then
  begin
    Result := True;
    Exit;
  end;

  Version := '';

  Result := False;
end;


{ ============================================================ }
{ Windows 7 Runtime validation                                }
{ ============================================================ }

function IsCompatibleWebView2OnWindows7: Boolean;
var
  Version: String;
begin
  Result := False;

  if not GetHealthyWebView2Version(Version) then
  begin
    Log(
      'Healthy WebView2 Runtime not detected on Windows 7'
    );

    Exit;
  end;

  Log(
    'Detected healthy WebView2 Runtime on Windows 7: ' +
    Version
  );

  Result := Pos('109.', Version) = 1;

  if not Result then
  begin
    Log(
      'Detected WebView2 Runtime is not compatible '
      + 'with Windows 7 requirement: '
      + Version
    );
  end;
end;


{ ============================================================ }
{ Install WebView2 Runtime 109 for Windows 7                  }
{ ============================================================ }

function InstallWebView2Runtime109: Boolean;
var
  InstallerPath: String;
  ResultCode: Integer;
  Version: String;
begin
  Result := False;

  ShowWebView2Progress(
    '正在准备 WebView2 Runtime 109...',
    '正在解压 Windows 7 运行环境，请稍候。'
  );

  try
    Log(
      'Extracting WebView2 Runtime 109 installer'
    );

    ExtractTemporaryFile(
      Win7WebView2InstallerFile
    );

    InstallerPath :=
      ExpandConstant(
        '{tmp}\' +
        Win7WebView2InstallerFile
      );

    ShowWebView2Progress(
      '正在安装 WebView2 Runtime 109...',
      'Windows 7 首次安装可能需要一些时间，请勿关闭安装程序。'
    );

    Log(
      'Starting WebView2 Runtime 109 installation'
    );

    if not Exec(
      InstallerPath,
      '--msedgewebview --system-level --verbose-logging --do-not-launch-msedge',
      '',
      SW_HIDE,
      ewWaitUntilTerminated,
      ResultCode
    ) then
    begin
      Log(
        'Unable to start WebView2 Runtime 109 installer'
      );

      Exit;
    end;

    Log(
      'WebView2 Runtime 109 installer exit code: ' +
      IntToStr(ResultCode)
    );

    ShowWebView2Progress(
      '正在验证 WebView2 Runtime 109...',
      '运行环境安装即将完成。'
    );

    if not GetHealthyWebView2Version(Version) then
    begin
      Log(
        'WebView2 Runtime 109 installer finished, '
        + 'but healthy Runtime was not detected'
      );

      Exit;
    end;

    Log(
      'WebView2 Runtime after installation: ' +
      Version
    );

    if Pos('109.', Version) <> 1 then
    begin
      Log(
        'Installed WebView2 Runtime is not version 109: ' +
        Version
      );

      Exit;
    end;

    Result := True;

  finally
    HideWebView2Progress;
  end;
end;


{ 不操作任意注册表给出的路径，只使用微软的标准运行时安装目录。 }
function UninstallIncompatibleRuntime(const RootKey: Integer; const BaseFolder: String; const MachineInstall: Boolean): Boolean;
var Version, SetupPath, Arguments: String; Code, I: Integer;
begin
  Result := True;
  Code := -1;
  if not RegQueryStringValue(RootKey, WebView2RegistryKey, 'pv', Version) then Exit;
  if not IsValidWebView2Version(Version) then Exit;
  for I := 1 to Length(Version) do
    if Pos(Version[I], '0123456789.') = 0 then begin Result := False; Exit; end;
  SetupPath := BaseFolder + '\' + Version + '\Installer\setup.exe';
  if not FileExists(SetupPath) then begin
    Log('Cannot automatically uninstall incomplete runtime: ' + SetupPath);
    Result := False; Exit;
  end;
  Arguments := '--uninstall --msedgewebview --force-uninstall --verbose-logging';
  if MachineInstall then begin
    Arguments := Arguments + ' --system-level';
    Result := Exec(SetupPath, Arguments, '', SW_HIDE, ewWaitUntilTerminated, Code);
  end else begin
    Arguments := Arguments + ' --user-level';
    { 用户目录中的卸载器按原用户权限执行，不以管理员权限执行用户可写文件。 }
    Result := ExecAsOriginalUser(SetupPath, Arguments, '', SW_HIDE, ewWaitUntilTerminated, Code);
  end;
  Log(Format('WebView2 uninstall launched=%d; exit=%d; file=%s', [Ord(Result), Code, SetupPath]));
  Result := Result and (Code = 0);
end;

function RepairWin7WebView2: Boolean;
begin
  { 先尝试安装/升级，不能只根据安装器退出码判定修复完成。 }
  if RuntimeProbeFailed then begin Result := False; Exit; end;
  Result := InstallWebView2Runtime109;
  if Result or RuntimeProbeFailed then Exit;
  if not WizardSilent then
    if MsgBox('现有 WebView2 运行环境不兼容或损坏，安装程序需要卸载该共享组件后重新安装 109 x64。' + #13#10 +
      '请关闭其他使用 WebView2 的软件。替换可能影响其他软件，是否继续？', mbConfirmation, MB_YESNO) <> IDYES then Exit;
  ShowWebView2Progress('正在替换不兼容的 WebView2...', '正在卸载原有运行环境并准备重新安装，请稍候。');
  try
    Result := UninstallIncompatibleRuntime(HKLM32, ExpandConstant('{pf32}\Microsoft\EdgeWebView\Application'), True);
    if not Result then Exit;
    Result := UninstallIncompatibleRuntime(HKCU32, ExpandConstant('{localappdata}\Microsoft\EdgeWebView\Application'), False);
    if not Result then Exit;
  finally
    HideWebView2Progress;
  end;
  Result := InstallWebView2Runtime109;
end;

{ ============================================================ }
{ Install Evergreen Runtime for modern Windows                }
{ ============================================================ }

function InstallEvergreenWebView2Runtime: Boolean;
var
  InstallerPath: String;
  ResultCode: Integer;
  Version: String;
begin
  Result := False;

  ShowWebView2Progress(
    '正在准备 WebView2 Runtime...',
    '正在解压运行环境，请稍候。'
  );

  try
    Log(
      'Extracting WebView2 Evergreen Runtime installer'
    );

    ExtractTemporaryFile(
      EvergreenWebView2InstallerFile
    );

    InstallerPath :=
      ExpandConstant(
        '{tmp}\' +
        EvergreenWebView2InstallerFile
      );

    ShowWebView2Progress(
      '正在安装 WebView2 Runtime...',
      '首次安装或升级运行环境可能需要一些时间，请勿关闭安装程序。'
    );

    Log(
      'Starting WebView2 Evergreen Runtime installation'
    );

    if not Exec(
      InstallerPath,
      '/silent /install',
      '',
      SW_HIDE,
      ewWaitUntilTerminated,
      ResultCode
    ) then
    begin
      Log(
        'Unable to start WebView2 Evergreen installer'
      );

      Exit;
    end;

    Log(
      'WebView2 Evergreen installer exit code: ' +
      IntToStr(ResultCode)
    );

    ShowWebView2Progress(
      '正在验证 WebView2 Runtime...',
      '运行环境安装即将完成。'
    );

    if not GetHealthyWebView2Version(Version) then
    begin
      Log(
        'WebView2 Evergreen installer finished, '
        + 'but healthy Runtime is still unavailable'
      );

      Exit;
    end;

    Log(
      'WebView2 Runtime after Evergreen installation: ' +
      Version
    );

    if IsLegacyWebView2OnModernWindows(Version) then
    begin
      Log(
        'Evergreen installation finished, '
        + 'but Runtime is still legacy version: '
        + Version
      );

      Exit;
    end;

    Result := True;

  finally
    HideWebView2Progress;
  end;
end;


{ ============================================================ }
{ Prepare installation                                        }
{ ============================================================ }

function PrepareToInstall(
  var NeedsRestart: Boolean
): String;
var
  Version: String;
begin
  Result := '';
  RuntimeProbeFailed := False;

  { PrepareToInstall 可能重试，已需要重启的状态不能被重置。 }
  if not EnsureNetFramework then begin
    Result := '.NET Framework 4.8 安装或验证失败。请检查系统补丁和安装日志：' + RuntimeLogDirectory + '\DotNet48.txt';
    if Result <> '' then SaveSetupLog;
    Exit;
  end;

  { ========================================================== }
  { Windows 10 / Windows 11 / Server 2016+                    }
  { ========================================================== }

  if not IsWindows7 then
  begin
    Log(
      'Modern Windows detected'
    );

    if GetHealthyWebView2Version(Version) then
    begin

      { ------------------------------------------------------- }
      { Existing Runtime 109                                  }
      {                                                       }
      { Do not trust 109.x on modern Windows.                 }
      { Upgrade it to Evergreen.                              }
      { ------------------------------------------------------- }

      if IsLegacyWebView2OnModernWindows(Version) then
      begin
        Log(
          'Legacy WebView2 Runtime detected on modern Windows: '
          + Version
        );

        Log(
          'Upgrading legacy WebView2 Runtime to Evergreen'
        );
      end
      else
      begin

        { ----------------------------------------------------- }
        { Modern healthy Runtime already exists               }
        { ----------------------------------------------------- }

        Log(
          'Compatible modern WebView2 Runtime already installed: '
          + Version
        );

        Log(
          'Skipping Evergreen Runtime installation'
        );

        if Result <> '' then SaveSetupLog;
    Exit;
      end;

    end
    else
    begin

      { ------------------------------------------------------- }
      { Runtime does not exist or installation is incomplete  }
      { ------------------------------------------------------- }

      Log(
        'WebView2 Runtime is missing or incomplete'
      );

      Log(
        'Installing bundled Evergreen Runtime'
      );
    end;


    { --------------------------------------------------------- }
    { Install / repair / upgrade Evergreen                    }
    { --------------------------------------------------------- }

    if not InstallEvergreenWebView2Runtime then
    begin
      Result :=
        'Microsoft Edge WebView2 Runtime 安装失败。'
        + #13#10
        + #13#10
        + '{#AppName} 无法正常启动。'
        + #13#10
        + #13#10
        + '请检查安装日志：' + RuntimeLogDirectory + #13#10 + '以及 C:\Windows\Temp\msedge_installer.log。';

      if Result <> '' then SaveSetupLog;
    Exit;
    end;

    Log(
      'WebView2 Evergreen Runtime installed successfully'
    );

    if Result <> '' then SaveSetupLog;
    Exit;
  end;


  { ========================================================== }
  { Windows 7                                                 }
  { ========================================================== }

  Log(
    'Windows 7 detected'
  );


  { ---------------------------------------------------------- }
  { Compatible WebView2 109 already installed                }
  { ---------------------------------------------------------- }

  if IsCompatibleWebView2OnWindows7 then
  begin
    GetHealthyWebView2Version(Version);

    Log(
      'Compatible WebView2 Runtime 109 '
      + 'already installed: '
      + Version
    );

    if Result <> '' then SaveSetupLog;
    Exit;
  end;


  { ---------------------------------------------------------- }
  { Install pinned WebView2 Runtime 109                       }
  { ---------------------------------------------------------- }

  Log(
    'Compatible WebView2 Runtime 109 not found'
  );

  Log(
    'Installing bundled WebView2 Runtime 109'
  );

  if not RepairWin7WebView2 then
  begin
    if RuntimeProbeFailed then begin
      Result := 'WebView2 环境检测工具执行失败，尚不能判断运行时是否正常。' + #13#10 +
        '请勿反复重装运行环境。请提供此目录中的 Setup.log 和 WebView2Probe.txt：' + RuntimeLogDirectory;
      SaveSetupLog;
      Exit;
    end;
    Result :=
      'Microsoft Edge WebView2 Runtime 109 安装失败。'
      + #13#10
      + #13#10
      + '{#AppName} 无法在当前 Windows 7 环境中运行。'
      + #13#10
      + #13#10
      + '请检查安装日志：' + RuntimeLogDirectory + #13#10 + '以及 C:\Windows\Temp\msedge_installer.log。';

    if Result <> '' then SaveSetupLog;
    Exit;
  end;

  Win7WebView2InstalledThisRun := True;

  Log(
    'WebView2 Runtime 109 installed successfully'
  );
end;


{ ============================================================ }
{ Application launch                                          }
{ ============================================================ }

function ShouldLaunchApplication: Boolean;
begin
  { 新装 Win7 WebView2 或 .NET 安装要求重启时，完成安装后先重启再运行。 }

  Result :=
    not Win7WebView2InstalledThisRun and not RuntimeRestartRequired;
end;


{ ============================================================ }
{ Restart policy                                               }
{ ============================================================ }

function NeedRestart: Boolean;
begin
  { 保留子安装器的重启要求；Win7 新装 WebView2 时也提示重启。 }

  Result :=
    RuntimeRestartRequired or (IsWindows7 and Win7WebView2InstalledThisRun);

  if Result then
  begin
    Log(
      'Restart requested because a prerequisite '
      + 'was installed during this setup'
    );
  end;
end;