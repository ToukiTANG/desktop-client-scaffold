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

PrivilegesRequired=admin

; Windows 7 SP1 or later
MinVersion=6.1sp1

; 64-bit only
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

Compression=lzma2
SolidCompression=yes

WizardStyle=modern

DisableProgramGroupPage=yes
UsePreviousAppDir=yes

CloseApplications=yes
RestartApplications=no


[Files]

; Application files
Source: "..\backend\dist\{#ExecutableName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Win7 WebView2 Runtime prerequisite
; dontcopy = only extract manually when needed
Source: "..\prerequisites\MicrosoftEdge_X64_109.0.1518.140.exe"; Flags: dontcopy


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

  WebView2InstallerFile =
    'MicrosoftEdge_X64_109.0.1518.140.exe';


var
  WebView2InstalledThisRun: Boolean;


function IsWindows7: Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);

  Result :=
    (Version.Major = 6) and
    (Version.Minor = 1);
end;


function GetWebView2Version(var Version: String): Boolean;
begin
  Version := '';

  { Machine-wide WebView2 Runtime }
  Result :=
    RegQueryStringValue(
      HKLM32,
      WebView2RegistryKey,
      'pv',
      Version
    );

  { Per-user WebView2 Runtime }
  if not Result then
  begin
    Result :=
      RegQueryStringValue(
        HKCU32,
        WebView2RegistryKey,
        'pv',
        Version
      );
  end;

  if Result then
  begin
    Result :=
      (Version <> '') and
      (Version <> '0.0.0.0');
  end;
end;


function IsCompatibleWebView2OnWindows7: Boolean;
var
  Version: String;
begin
  Result := False;

  if not GetWebView2Version(Version) then
  begin
    Log('WebView2 Runtime not detected');
    Exit;
  end;

  Log('Detected WebView2 Runtime version: ' + Version);

  Result := Pos('109.', Version) = 1;
end;


function InstallWebView2Runtime109: Boolean;
var
  InstallerPath: String;
  ResultCode: Integer;
  Version: String;
begin
  Result := False;

  Log('Extracting WebView2 Runtime 109 installer');

  ExtractTemporaryFile(WebView2InstallerFile);

  InstallerPath :=
    ExpandConstant('{tmp}\' + WebView2InstallerFile);

  Log('Starting WebView2 Runtime 109 installation');

  if not Exec(
    InstallerPath,
    '--msedgewebview --system-level --verbose-logging --do-not-launch-msedge',
    '',
    SW_HIDE,
    ewWaitUntilTerminated,
    ResultCode
  ) then
  begin
    Log('Unable to start WebView2 installer');
    Exit;
  end;

  Log(
    'WebView2 installer exit code: ' +
    IntToStr(ResultCode)
  );

  {
    Do not rely only on ResultCode.

    The important result is whether WebView2 109
    is actually registered after installer exits.
  }

  if not GetWebView2Version(Version) then
  begin
    Log(
      'WebView2 installer finished, but Runtime was not detected'
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
      'Installed WebView2 Runtime is not version 109'
    );
    Exit;
  end;

  Result := True;
end;


function PrepareToInstall(
  var NeedsRestart: Boolean
): String;
var
  Version: String;
begin
  Result := '';

  WebView2InstalledThisRun := False;

  {
    Windows 10 / Windows 11:
    Do not install pinned WebView2 109.
  }
  if not IsWindows7 then
  begin
    Log(
      'Current OS is not Windows 7. '
      + 'Skipping WebView2 109 prerequisite.'
    );

    Exit;
  end;

  Log('Windows 7 detected');

  {
    Win7 already has WebView2 109.
  }
  if IsCompatibleWebView2OnWindows7 then
  begin
    GetWebView2Version(Version);

    Log(
      'Compatible WebView2 Runtime already installed: '
      + Version
    );

    Exit;
  end;

  {
    Win7 without compatible Runtime.
  }
  Log(
    'Compatible WebView2 Runtime 109 not found. '
    + 'Installing bundled Runtime.'
  );

  if not InstallWebView2Runtime109 then
  begin
    Result :=
      'Microsoft Edge WebView2 Runtime 109 安装失败。'
      + #13#10
      + #13#10
      + '{#AppName} 无法在当前 Windows 7 环境中运行。'
      + #13#10
      + '请检查系统环境或安装日志后重试。';

    Exit;
  end;

  WebView2InstalledThisRun := True;

  Log(
    'WebView2 Runtime 109 installed successfully'
  );
end;


function ShouldLaunchApplication: Boolean;
begin
  {
    If Runtime was installed during this setup,
    do not immediately launch the application.
  }
  Result := not WebView2InstalledThisRun;
end;


function NeedRestart: Boolean;
begin
  {
    Conservative Win7 policy:
    if WebView2 Runtime was newly installed,
    request a reboot after application installation.
  }
  Result :=
    IsWindows7 and
    WebView2InstalledThisRun;

  if Result then
  begin
    Log(
      'Restart requested because WebView2 Runtime '
      + 'was installed during this setup'
    );
  end;
end;