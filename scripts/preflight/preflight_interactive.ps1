<#
  Preflight (Windows)
  Step order:
    1. Python
    2. Java
    3. Databricks CLI installed
    4. Databricks CLI profile and connectivity
#>

function Write-Header {
    param($text)
    Write-Host "============================================================"
    Write-Host $text
    Write-Host "============================================================"
}

function Check-Command {
    param([string]$cmd)
    $exists = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($exists) {
        Write-Host "PASS: $cmd found"
        return $true
    } else {
        Write-Host "FAIL: $cmd not found"
        return $false
    }
}

function Pause-Continue {
    Write-Host ""
    Read-Host "Press ENTER to continue"
}

Write-Header "Lakebridge Accelerator - Preflight (Interactive, Windows)"

#######################################################################
# STEP 1: Python
#######################################################################
Write-Host ""
Write-Host "STEP 1 of 4: Checking Python (required: 3.10 - 3.13)"

if (-not (Check-Command "python")) {
    Write-Host "Python not found."
    Write-Host "Install Python from: https://www.python.org/downloads/windows/"
    Write-Host "Select Add Python To PATH during installation."
    exit 1
}

# Execute Python version check safely
$pyver = python -c "import sys; print(sys.version_info[0], sys.version_info[1])" 2>$null
if (-not $pyver) {
    Write-Host "Unable to check python version."
    exit 1
}

$parts = $pyver.Split(" ")
$major = [int]$parts[0]
$minor = [int]$parts[1]

Write-Host "Detected Python major.minor = $major.$minor"

if ($major -eq 3 -and $minor -ge 10 -and $minor -le 13) {
    Write-Host "PASS: Python version is within required range"
} else {
    Write-Host "FAIL: Install Python version 3.10 - 3.13"
    exit 1
}

Pause-Continue

#######################################################################
# STEP 2: Java
#######################################################################
Write-Host ""
Write-Host "STEP 2 of 4: Checking Java (required: 11 or above)"

if (-not (Check-Command "java")) {
    Write-Host "Java not found."
    Write-Host "Install Java 11+ from: https://adoptium.net"
    exit 1
}

# Get Java spec version
$javaSpecLine = (java -XshowSettings:properties -version 2>&1 | Select-String "java.specification.version")
if ($javaSpecLine) {
    $spec = ($javaSpecLine -split "=")[-1].Trim()
    Write-Host "Detected java.specification.version = $spec"
    $specMajor = [int]($spec.Split(".")[0])
    if ($specMajor -ge 11) {
        Write-Host "PASS: Java version supported"
    } else {
        Write-Host "FAIL: Java version must be >= 11"
        exit 1
    }
} else {
    Write-Host "Unable to parse java version. Verify Java installation."
    exit 1
}

Pause-Continue

#######################################################################
# STEP 3: Databricks CLI installed
#######################################################################
Write-Host ""
Write-Host "STEP 3 of 4: Checking Databricks CLI installation"

if (-not (Check-Command "databricks")) {
    Write-Host "Databricks CLI not found."
    Write-Host "Install with:"
    Write-Host "    pip install databricks-cli"
    exit 1
}

$cliVer = databricks --version 2>$null
Write-Host "Databricks CLI version = $cliVer"

Pause-Continue

#######################################################################
# STEP 4: Databricks CLI profile & connectivity
#######################################################################
Write-Host ""
Write-Host "STEP 4 of 4: Configuring and testing Databricks CLI profile"
Write-Host ""

$answer = Read-Host "Do you already have a Databricks profile configured? (y/n)"

if ($answer -match "^[Yy]") {
    $profile = Read-Host "Enter the profile name (example: default)"
} else {
    Write-Host ""
    Write-Host "We will create a Databricks profile."
    Write-Host "You need:"
    Write-Host "  1. Databricks workspace URL"
    Write-Host "  2. Personal Access Token (PAT)"
    Write-Host ""

    $profile = Read-Host "Choose a profile name (example: default, prod)"
    $dbHost = Read-Host "Enter workspace host URL (example: https://adb-xxx.azuredatabricks.net)"
    $token = Read-Host "Paste your personal access token"

    Write-Host "Configuring Databricks CLI profile..."

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "databricks"
    $psi.Arguments = "configure --token --profile $profile"
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    $process.Start() | Out-Null

    $process.StandardInput.WriteLine($dbHost)
    $process.StandardInput.WriteLine($token)
    $process.StandardInput.Close()

    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()

    $process.WaitForExit()

    if ($process.ExitCode -ne 0) {
        Write-Host "Failed to configure profile. Output:"
        Write-Host $stdout
        Write-Host $stderr
        Write-Host "Try running manually:"
        Write-Host "  databricks configure --token --profile $profile"
        exit 1
    } else {
        Write-Host "Databricks CLI profile '$profile' configured successfully."
    }
}

Write-Host ""
Write-Host "Testing Databricks connectivity..."
$clusters = databricks clusters list --profile $profile 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "FAIL: Databricks CLI could not connect using profile '$profile'."
    Write-Host "Check:"
    Write-Host "  1. Workspace URL is correct"
    Write-Host "  2. Token is valid"
    Write-Host "  3. Consider selecting a cluster:"
    Write-Host "       databricks configure --configure-cluster --profile $profile"
    Write-Host "Full error:"
    Write-Host $clusters
    exit 1
}

Write-Host ""
Write-Host "PASS: Connected to Databricks successfully."
Write-Host "Preflight checks finished successfully."
