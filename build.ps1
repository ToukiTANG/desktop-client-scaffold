$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$FrontendDir = Join-Path $ProjectRoot "frontend"
$BackendDir = Join-Path $ProjectRoot "backend"
$ReleaseDir = Join-Path $ProjectRoot "release"

Write-Host "========================================"
Write-Host " Desktop Client Build"
Write-Host "========================================"

# 1. Build frontend
Write-Host ""
Write-Host "[1/5] Building frontend..."

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


# 2. Read application version
Write-Host ""
Write-Host "[2/5] Reading application version..."

Push-Location $BackendDir

try {
    $Version = uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to read application version"
    }

    $Version = $Version.Trim()
}
finally {
    Pop-Location
}

Write-Host "Version: $Version"


# 3. Build Windows application
Write-Host ""
Write-Host "[3/5] Building DesktopClient.exe..."

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


# 4. Prepare release directory
Write-Host ""
Write-Host "[4/5] Preparing release..."

$SourceDir = Join-Path $BackendDir "dist\DesktopClient"
$TargetDir = Join-Path $ReleaseDir "DesktopClient-$Version"

if (Test-Path $TargetDir) {
    Remove-Item -Recurse -Force $TargetDir
}

New-Item -ItemType Directory -Force $ReleaseDir | Out-Null
Copy-Item -Path $SourceDir -Destination $TargetDir -Recurse

# 5. Create release ZIP
Write-Host ""
Write-Host "[5/5] Creating release ZIP..."

$ZipFile = Join-Path $ReleaseDir "DesktopClient-$Version.zip"

if (Test-Path $ZipFile) {
    Remove-Item -Force $ZipFile
}

Compress-Archive -Path $TargetDir -DestinationPath $ZipFile -CompressionLevel Optimal


Write-Host ""
Write-Host "========================================"
Write-Host " Build completed successfully"
Write-Host " Version : $Version"
Write-Host " Output  : $TargetDir"
Write-Host "========================================"