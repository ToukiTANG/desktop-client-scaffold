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

  Win7WebView2InstalledThisRun := False;


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
        + '请检查系统环境或安装日志后重试。';

      Exit;
    end;

    Log(
      'WebView2 Evergreen Runtime installed successfully'
    );

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

  if not InstallWebView2Runtime109 then
  begin
    Result :=
      'Microsoft Edge WebView2 Runtime 109 安装失败。'
      + #13#10
      + #13#10
      + '{#AppName} 无法在当前 Windows 7 环境中运行。'
      + #13#10
      + #13#10
      + '请检查系统环境或安装日志后重试。';

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
  {
    Windows 7:

    If WebView2 Runtime 109 was newly installed,
    do not immediately launch the application.

    Windows 10+ Evergreen Runtime installations may
    launch the application immediately.
  }

  Result :=
    not Win7WebView2InstalledThisRun;
end;


{ ============================================================ }
{ Restart policy                                               }
{ ============================================================ }

function NeedRestart: Boolean;
begin
  {
    Conservative Windows 7 policy:

    Only request restart when WebView2 Runtime 109
    was installed during this setup.
  }

  Result :=
    IsWindows7 and
    Win7WebView2InstalledThisRun;

  if Result then
  begin
    Log(
      'Restart requested because WebView2 Runtime 109 '
      + 'was installed during this setup'
    );
  end;
end;