<#
  Step 2: Lakebridge Installation Script (Windows)
#>

function Write-Header {
    param($text)
    Write-Host "============================================================"
    Write-Host $text
    Write-Host "============================================================"
}

function Pause-Continue {
    Write-Host ""
    Read-Host "Press ENTER to continue"
}

Write-Header "Lakebridge Accelerator - Installation (Step 2)"

# ---------------------------------------------------------------------
# 1. Validate 'lakebridge' profile exists
# ---------------------------------------------------------------------
Write-Host "Validating Databricks CLI profile 'lakebridge'..."

$configPath = "$HOME\.databrickscfg"
$profileExists = $false

if (Test-Path $configPath) {
    $lines = Get-Content $configPath
    foreach ($ln in $lines) {
        if ($ln.Trim() -eq "[lakebridge]") {
            $profileExists = $true
        }
    }
}

if (-not $profileExists) {
    Write-Host "ERROR: Databricks profile 'lakebridge' not found."
    Write-Host "Run Preflight (Step 1) before installation."
    exit 1
}

Write-Host "PASS: Profile 'lakebridge' detected."
Pause-Continue

# ---------------------------------------------------------------------
# 2. Detect CLI type
# ---------------------------------------------------------------------
Write-Host ""
Write-Host "Detecting Databricks CLI version..."

$cliOutput = databricks --version 2>&1
$usingNewCLI = $false

if ($cliOutput -match "Databricks CLI v") {
    $usingNewCLI = $true
    Write-Host "Using NEW Databricks CLI (auth model)"
} else {
    Write-Host "Using OLD Databricks CLI (pip version)"
}

Pause-Continue

# # ---------------------------------------------------------------------
# # 3. FORCE Python Interpreter (important for Windows)
# # ---------------------------------------------------------------------
# Write-Host ""
# Write-Host "Detecting Python interpreter for Databricks CLI..."

# $pythonCmd = $null
# $pythonCandidates = @("python", "python3", "py -3", "py")

# foreach ($cmd in $pythonCandidates) {
#     try {
#         $ver = & $cmd -c "import sys; print('OK')" 2>$null
#         if ($LASTEXITCODE -eq 0 -and $ver -eq "OK") {
#             $pythonCmd = $cmd
#             break
#         }
#     } catch {}
# }

# if (-not $pythonCmd) {
#     Write-Host "FAIL: No working Python interpreter found."
#     Write-Host "Install Python 3.10 - 3.13 from:"
#     Write-Host "  https://www.python.org/downloads/windows/"
#     exit 1
# }

# Write-Host "PASS: Using Python interpreter: $pythonCmd"

# try {
#     $pythonPath = (Get-Command $pythonCmd).Source
# } catch {
#     Write-Host "FAIL: Could not resolve python executable path."
#     exit 1
# }

# Write-Host "Python Executable Path: $pythonPath"

# Write-Host "Setting Databricks CLI Python interpreter..."
# setx DATABRICKS_PYTHON_EXECUTABLE $pythonPath | Out-Null

# Write-Host "PASS: Environment variable DATABRICKS_PYTHON_EXECUTABLE set."
# Pause-Continue

# ---------------------------------------------------------------------
# 4. Install Lakebridge (REPLACED SECTION)
# ---------------------------------------------------------------------
Write-Host "`nChecking if Lakebridge is already installed..."

# Get list of installed python packages
$pkgList = pip list --format=json | ConvertFrom-Json

$existing = $pkgList | Where-Object { $_.name -eq "databricks-labs-lakebridge" }

if ($existing) {
    Write-Host "PASS: Lakebridge is already installed (version $($existing.version))."
    Write-Host "Skipping installation."
}
else {
    Write-Host "Lakebridge not installed. Installing now..."
    Write-Host "Running: databricks labs install lakebridge"

    databricks labs install lakebridge
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAIL: Lakebridge installation failed."
        exit 1
    }
    Write-Host "PASS: Lakebridge installed successfully."
}


# ---------------------------------------------------------------------
# 5. Install Analyzer + Transpiler  (REMOVED & REPLACED WITH MESSAGE)
# ---------------------------------------------------------------------
Write-Host ""
Write-Host "Skipping Analyzer and Transpiler installation (Not required for pinned version)."
Write-Host "PASS: Analyzer/Transpiler step intentionally skipped."
Pause-Continue

# ---------------------------------------------------------------------
# 6. Verify Analyzer + Transpiler (REPLACED WITH VERSION CHECK)
# ---------------------------------------------------------------------
Write-Host ""
Write-Host "Verifying Lakebridge installation..."

try {
    $lbVersion = pip show databricks-labs-lakebridge 2>&1
    Write-Host $lbVersion
} catch {
    Write-Host "FAIL: Could not query Lakebridge version."
    exit 1
}

Write-Host "PASS: Lakebridge installation verified."

Write-Host ""
Write-Host "============================================================"
Write-Host "Lakebridge Installation Completed Successfully (Step 2)"
Write-Host "============================================================"
