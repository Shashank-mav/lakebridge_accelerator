# ============================================================
#  Lakebridge Accelerator - 1 Line CURL Installer (Windows)
# ============================================================

$repo = "https://raw.githubusercontent.com/Shashank-mav/lakebridge_accelerator/main"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " Lakebridge Accelerator – Installer" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Create project folder
$root = "$PWD\lakebridge_accelerator"
if (!(Test-Path $root)) {
    New-Item -ItemType Directory -Path $root | Out-Null
    Write-Host "Created folder: $root" -ForegroundColor Green
} else {
    Write-Host "Using existing folder: $root" -ForegroundColor DarkYellow
}

# ---- Directory Setup ----
$dirs = @(
    "scripts/preflight",
    "scripts/install",
    "config"
)

foreach ($d in $dirs) {
    $path = "$root\$d"
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
    }
}

Write-Host "Folders prepared." -ForegroundColor Green

# ---- Download files ----
$files = @{
    "main.py" = "$repo/main.py"
    "scripts/preflight/preflight_interactive.ps1" = "$repo/scripts/preflight/preflight_interactive.ps1"
    "scripts/install/install_lakebridge.ps1" = "$repo/scripts/install/install_lakebridge.ps1"
    "config/config.yaml" = "$repo/config/config.yaml"
}

foreach ($item in $files.GetEnumerator()) {
    $dst = "$root\$($item.Key)"
    Write-Host "Downloading $($item.Key) ..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $item.Value -OutFile $dst -UseBasicParsing
}

Write-Host ""
Write-Host "All files downloaded successfully!" -ForegroundColor Green

# ---- Run Installer ----
Write-Host ""
Write-Host "Launching Stage-1 Installer..." -ForegroundColor Yellow

# Correct Python Execution
python "$root\main.py"

Write-Host ""
Write-Host "Installation Finished." -ForegroundColor Green
