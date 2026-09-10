$ErrorActionPreference = "Stop"

Set-StrictMode -Version 2.0


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

$ProjectRoot = $PSScriptRoot

$FrontendDir = Join-Path $ProjectRoot "frontend"
$BackendDir = Join-Path $ProjectRoot "backend"
$ReleaseDir = Join-Path $ProjectRoot "release"

$ProjectConfigFile = Join-Path $ProjectRoot "project.json"

$InstallerScript = Join-Path $ProjectRoot "installer\DesktopClient.iss"
$PyInstallerSpec = Join-Path $BackendDir "DesktopClient.spec"

$Win7WebView2Installer = Join-Path $ProjectRoot "prerequisites\MicrosoftEdge_X64_109.0.1518.140.exe"
$EvergreenWebView2Installer = Join-Path $ProjectRoot "prerequisites\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"

$InnoSetupCompiler = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

function Assert-FileExists {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    if (-not (Test-Path $Path -PathType Leaf)) {
        throw "$Description not found: $Path"
    }
}


function Assert-DirectoryExists {
    param (
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    if (-not (Test-Path $Path -PathType Container)) {
        throw "$Description not found: $Path"
    }
}


# ------------------------------------------------------------
# Load project configuration
# ------------------------------------------------------------

Assert-FileExists $ProjectConfigFile "Project config"

$ProjectConfig = Get-Content $ProjectConfigFile -Raw -Encoding UTF8 | ConvertFrom-Json

$AppName = [string]$ProjectConfig.app_name
$AppId = [string]$ProjectConfig.app_id
$ExecutableName = [string]$ProjectConfig.executable_name
$InstallerName = [string]$ProjectConfig.installer_name

if ([string]::IsNullOrWhiteSpace($AppName)) {
    throw "Invalid project config: app_name"
}

if ([string]::IsNullOrWhiteSpace($AppId)) {
    throw "Invalid project config: app_id"
}

if ([string]::IsNullOrWhiteSpace($ExecutableName)) {
    throw "Invalid project config: executable_name"
}

if ([string]::IsNullOrWhiteSpace($InstallerName)) {
    throw "Invalid project config: installer_name"
}


Write-Host ""
Write-Host "========================================"
Write-Host " $AppName Build"
Write-Host "========================================"


# ------------------------------------------------------------
# 0. Validate build prerequisites
# ------------------------------------------------------------

Write-Host ""
Write-Host "[0/9] Validating build prerequisites..."

Assert-DirectoryExists $FrontendDir "Frontend directory"
Assert-DirectoryExists $BackendDir "Backend directory"

Assert-FileExists $PyInstallerSpec "PyInstaller spec"
Assert-FileExists $InstallerScript "Inno Setup script"

Assert-FileExists `
    $Win7WebView2Installer `
    "Win7 WebView2 Runtime 109 prerequisite"

Assert-FileExists `
    $EvergreenWebView2Installer `
    "WebView2 Evergreen Runtime prerequisite"

Assert-FileExists `
    $InnoSetupCompiler `
    "Inno Setup compiler"

Write-Host "Win7 WebView2     : $Win7WebView2Installer"
Write-Host "Evergreen WebView2: $EvergreenWebView2Installer"
Write-Host "Inno Setup        : $InnoSetupCompiler"


# ------------------------------------------------------------
# 1. Validate Python environment
# ------------------------------------------------------------

Write-Host ""
Write-Host "[1/9] Validating Python environment..."

Push-Location $BackendDir

try {
    $PythonVersion = uv run python -c "import platform; print(platform.python_version())"

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to detect Python version"
    }

    $PythonVersion = $PythonVersion.Trim()

    $PythonArch = uv run python -c "import struct; print(struct.calcsize('P') * 8)"

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to detect Python architecture"
    }

    $PythonArch = $PythonArch.Trim()

    $PythonBase = uv run python -c "import sys; print(sys._base_executable)"

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to detect base Python executable"
    }

    $PythonBase = $PythonBase.Trim()

    Write-Host "Python version : $PythonVersion"
    Write-Host "Python arch    : ${PythonArch}-bit"
    Write-Host "Python base    : $PythonBase"

    if ($PythonVersion -ne "3.8.10") {
        throw "Unsupported Python version: $PythonVersion. Expected 3.8.10."
    }

    if ($PythonArch -ne "64") {
        throw "Unsupported Python architecture: ${PythonArch}-bit. Expected 64-bit."
    }

    if ($PythonBase -match "\\uv\\python\\") {
        throw "uv-managed Python detected: $PythonBase. Win7 builds must use official CPython 3.8.10 x64."
    }
}
finally {
    Pop-Location
}


# ------------------------------------------------------------
# 2. Check backend code
# ------------------------------------------------------------

Write-Host ""
Write-Host "[2/9] Checking backend..."

Push-Location $BackendDir

try {
    uv run ruff check .

    if ($LASTEXITCODE -ne 0) {
        throw "Backend Ruff check failed"
    }
}
finally {
    Pop-Location
}


# ------------------------------------------------------------
# 3. Apply pywebview Win7 compatibility patch
# ------------------------------------------------------------

Write-Host ""
Write-Host "[3/9] Applying pywebview Win7 compatibility patch..."

Push-Location $BackendDir

try {
    uv run python tools\patch_pywebview_win7.py

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to apply pywebview Win7 compatibility patch"
    }
}
finally {
    Pop-Location
}


# ------------------------------------------------------------
# 4. Check and build frontend
# ------------------------------------------------------------

Write-Host ""
Write-Host "[4/9] Checking and building frontend..."

Push-Location $FrontendDir

try {
    npm run type-check

    if ($LASTEXITCODE -ne 0) {
        throw "Frontend type check failed"
    }

    npm run build

    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed"
    }
}
finally {
    Pop-Location
}


# ------------------------------------------------------------
# 5. Read application version
# ------------------------------------------------------------

Write-Host ""
Write-Host "[5/9] Reading application version..."

Push-Location $BackendDir

try {
    $Version = uv run python -c "import tomli; print(tomli.load(open('pyproject.toml','rb'))['project']['version'])"

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to read application version"
    }

    $Version = $Version.Trim()

    if ([string]::IsNullOrWhiteSpace($Version)) {
        throw "Application version is empty"
    }
}
finally {
    Pop-Location
}

Write-Host "Application version: $Version"


# ------------------------------------------------------------
# 6. Build application with PyInstaller
# ------------------------------------------------------------

Write-Host ""
Write-Host "[6/9] Building $ExecutableName..."

Push-Location $BackendDir

try {
    uv run pyinstaller DesktopClient.spec --clean --noconfirm

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed"
    }
}
finally {
    Pop-Location
}


# ------------------------------------------------------------
# 7. Prepare release directory and ZIP package
# ------------------------------------------------------------

Write-Host ""
Write-Host "[7/9] Preparing release package..."

$SourceDir = Join-Path $BackendDir "dist\$ExecutableName"
$TargetDir = Join-Path $ReleaseDir "$ExecutableName-$Version"
$ZipFile = Join-Path $ReleaseDir "$ExecutableName-$Version.zip"

if (-not (Test-Path $SourceDir -PathType Container)) {
    throw "PyInstaller output directory not found: $SourceDir"
}

New-Item -ItemType Directory -Force $ReleaseDir | Out-Null

if (Test-Path $TargetDir) {
    Remove-Item $TargetDir -Recurse -Force
}

if (Test-Path $ZipFile) {
    Remove-Item $ZipFile -Force
}

Copy-Item `
    -Path $SourceDir `
    -Destination $TargetDir `
    -Recurse

Compress-Archive `
    -Path $TargetDir `
    -DestinationPath $ZipFile `
    -CompressionLevel Optimal

if (-not (Test-Path $ZipFile -PathType Leaf)) {
    throw "ZIP package was not created: $ZipFile"
}


# ------------------------------------------------------------
# 8. Build Inno Setup installer
# ------------------------------------------------------------

Write-Host ""
Write-Host "[8/9] Building installer..."

& $InnoSetupCompiler `
    "/DAppVersion=$Version" `
    "/DAppName=$AppName" `
    "/DAppId=$AppId" `
    "/DExecutableName=$ExecutableName" `
    "/DInstallerName=$InstallerName" `
    $InstallerScript

if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup build failed"
}

$SetupFile = Join-Path $ReleaseDir "$InstallerName-$Version.exe"

if (-not (Test-Path $SetupFile -PathType Leaf)) {
    throw "Installer output not found: $SetupFile"
}


# ------------------------------------------------------------
# 9. Done
# ------------------------------------------------------------

Write-Host ""
Write-Host "[9/9] Build completed"

Write-Host ""
Write-Host "========================================"
Write-Host " Build completed successfully"
Write-Host "========================================"
Write-Host ""
Write-Host "Application : $AppName"
Write-Host "Version     : $Version"
Write-Host "Directory   : $TargetDir"
Write-Host "ZIP         : $ZipFile"
Write-Host "Installer   : $SetupFile"
Write-Host ""