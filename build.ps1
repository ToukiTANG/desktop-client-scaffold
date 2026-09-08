$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$FrontendDir = Join-Path $ProjectRoot "frontend"
$BackendDir = Join-Path $ProjectRoot "backend"
$ReleaseDir = Join-Path $ProjectRoot "release"

$InstallerScript = Join-Path $ProjectRoot "installer\DesktopClient.iss"
$WebView2Installer = Join-Path $ProjectRoot "prerequisites\MicrosoftEdge_X64_109.0.1518.140.exe"

$InnoSetupCompiler = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"


Write-Host "========================================"
Write-Host " Desktop Client Build"
Write-Host "========================================"


# ------------------------------------------------------------
# 0. Validate Python environment
# ------------------------------------------------------------

Write-Host ""
Write-Host "[0/8] Validating Python environment..."

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
# 1. Apply pywebview Win7 compatibility patch
# ------------------------------------------------------------

Write-Host ""
Write-Host "[1/8] Applying pywebview Win7 compatibility patch..."

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
# 2. Build frontend
# ------------------------------------------------------------

Write-Host ""
Write-Host "[2/8] Building frontend..."

Push-Location $FrontendDir

try {
    npm run build

    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed"
    }
}
finally {
    Pop-Location
}


# ------------------------------------------------------------
# 3. Read application version
# ------------------------------------------------------------

Write-Host ""
Write-Host "[3/8] Reading application version..."

Push-Location $BackendDir

try {
    $Version = uv run python -c "import tomli; print(tomli.load(open('pyproject.toml','rb'))['project']['version'])"

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to read application version"
    }

    $Version = $Version.Trim()
}
finally {
    Pop-Location
}

Write-Host "Application version: $Version"


# ------------------------------------------------------------
# 4. Build application with PyInstaller
# ------------------------------------------------------------

Write-Host ""
Write-Host "[4/8] Building DesktopClient..."

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
# 5. Prepare release directory
# ------------------------------------------------------------

Write-Host ""
Write-Host "[5/8] Preparing release directory..."

$SourceDir = Join-Path $BackendDir "dist\DesktopClient"
$TargetDir = Join-Path $ReleaseDir "DesktopClient-$Version"

if (-not (Test-Path $SourceDir)) {
    throw "PyInstaller output directory not found: $SourceDir"
}

New-Item -ItemType Directory -Force $ReleaseDir | Out-Null

if (Test-Path $TargetDir) {
    Remove-Item -Recurse -Force $TargetDir
}

Copy-Item -Path $SourceDir -Destination $TargetDir -Recurse


# ------------------------------------------------------------
# 6. Create ZIP package
# ------------------------------------------------------------

Write-Host ""
Write-Host "[6/8] Creating ZIP package..."

$ZipFile = Join-Path $ReleaseDir "DesktopClient-$Version.zip"

if (Test-Path $ZipFile) {
    Remove-Item -Force $ZipFile
}

Compress-Archive `
    -Path $TargetDir `
    -DestinationPath $ZipFile `
    -CompressionLevel Optimal


# ------------------------------------------------------------
# 7. Build Inno Setup installer
# ------------------------------------------------------------

Write-Host ""
Write-Host "[7/8] Building installer..."

if (-not (Test-Path $InstallerScript)) {
    throw "Inno Setup script not found: $InstallerScript"
}

if (-not (Test-Path $WebView2Installer)) {
    throw "WebView2 Runtime prerequisite not found: $WebView2Installer"
}

if (-not (Test-Path $InnoSetupCompiler)) {
    throw "Inno Setup compiler not found: $InnoSetupCompiler"
}

& $InnoSetupCompiler "/DAppVersion=$Version" $InstallerScript

if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup build failed"
}

$SetupFile = Join-Path $ReleaseDir "DesktopClientSetup-$Version.exe"

if (-not (Test-Path $SetupFile)) {
    throw "Installer output not found: $SetupFile"
}


# ------------------------------------------------------------
# 8. Done
# ------------------------------------------------------------

Write-Host ""
Write-Host "[8/8] Build completed"

Write-Host ""
Write-Host "========================================"
Write-Host " Build completed successfully"
Write-Host "========================================"
Write-Host ""
Write-Host "Version   : $Version"
Write-Host "Directory : $TargetDir"
Write-Host "ZIP       : $ZipFile"
Write-Host "Installer : $SetupFile"
Write-Host ""