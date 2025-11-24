# ============================================================
#  Lakebridge Accelerator - 1 Line CURL Installer (Windows)
# ============================================================

$repo = "https://raw.githubusercontent.com/Shashank-mav/lakebridge_accelerator/main"

Write-Host ""
Write-Host "==============================================="
Write-Host " Lakebridge Accelerator – Installer"
Write-Host "==============================================="
Write-Host ""

# Create project folder
$root = "$PWD\lakebridge_accelerator"
if (!(Test-Path $root)) {
    New-Item -ItemType Directory -Path $root | Out-Null
    Write-Host "Created folder: $root"
} else {
    Write-Host "Using existing folder: $root"
}

# ---- Directory Setup ----
$dirs = @(
    "scripts/preflight",
    "scripts/install",
    "config"
)

foreach ($d in $dirs) {
    $path = "$root\$d"
    if (!(Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }
}

Write-Host "Folders prepared."

# ---- Download files ----
$files = @{
    "main.py" = "$repo/main.py"
    "scripts/preflight/preflight_interactive.ps1" = "$repo/scripts/preflight/preflight_interactive.ps1"
    "scripts/install/install_lakebridge.ps1" = "$repo/scripts/install/install_lakebridge.ps1"
    "config/config.yaml" = "$repo/config/config.yaml"
}

foreach ($item in $files.GetEnumerator()) {
    $dst = "$root\$($item.Key)"
    Write-Host "Downloading $($item.Key) ..."
    Invoke-WebRequest -Uri $item.Value -OutFile $dst
}

Write-Host ""
Write-Host "All files downloaded successfully."

# ---- Run Installer ----
Write-Host ""
Write-Host "Launching Stage-1 Installer..."
powershell -ExecutionPolicy Bypass -File "$root\main.py"

Write-Host ""
Write-Host "Installation Finished."
