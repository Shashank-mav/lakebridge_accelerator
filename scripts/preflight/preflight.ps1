<#
    Preflight Check - Windows Only
    Project: Lakebridge Accelerator
    Step 1 - Verify all pre-requisites before installation of Lakebridge
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Profile
)

$ReportPath = "$PSScriptRoot\preflight_report.txt"
"" | Out-File $ReportPath

Write-Host "============================================================"
Write-Host " Lakebridge Accelerator - Preflight Check (Windows)"
Write-Host " Profile: $Profile"
Write-Host "============================================================"
Add-Content $ReportPath "Profile: $Profile"

function Check-Command {
    param([string]$cmd)
    $exists = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($exists) {
        Write-Host "PASS: $cmd found"
        Add-Content $ReportPath "PASS: $cmd found"
        return $true
    }
    else {
        Write-Host "FAIL: $cmd not found"
        Add-Content $ReportPath "FAIL: $cmd not found"
        return $false
    }
}

Write-Host "`nChecking Databricks CLI..."
if (-not (Check-Command "databricks")) {
    Write-Host "Install Databricks CLI before proceeding."
    exit 1
}

$DbVersion = databricks --version 2>$null
Add-Content $ReportPath "Databricks CLI version: $DbVersion"

$ConfigFile = "$HOME\.databrickscfg"
Write-Host "`nChecking configuration file: $ConfigFile"

if (Test-Path $ConfigFile) {
    Add-Content $ReportPath "Found .databrickscfg file"
}
else {
    Write-Host "FAIL: .databrickscfg file not found."
    Add-Content $ReportPath "FAIL: .databrickscfg file not found."
    exit 1
}

Write-Host "`nValidating Databricks profile connectivity..."
$ClusterList = databricks clusters list --profile $Profile 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "PASS: Profile connectivity verified."
    Add-Content $ReportPath "PASS: clusters list succeeded"
} else {
    Write-Host "FAIL: Databricks CLI cannot connect with profile $Profile"
    Add-Content $ReportPath $ClusterList
    exit 1
}

Write-Host "`nChecking Python installation..."
if (Check-Command "python") {
    $PyVersion = python -c "import sys; print('.'.join(map(str,sys.version_info[:3])))" 2>$null
    Add-Content $ReportPath "Python version: $PyVersion"

    $parts = $PyVersion.Split(".")
    $major = [int]$parts[0]
    $minor = [int]$parts[1]

    if ($major -eq 3 -and $minor -ge 10 -and $minor -le 13) {
        Write-Host "PASS: Python version supported (3.10 - 3.13)"
        Add-Content $ReportPath "PASS: Python supported"
    }
    else {
        Write-Host "FAIL: Python version must be 3.10 to 3.13"
        Add-Content $ReportPath "FAIL: Unsupported Python version"
        exit 1
    }
}
else {
    exit 1
}

Write-Host "`nChecking Java installation..."
if (Check-Command "java") {
    $JavaSpec = java -XshowSettings:properties -version 2>&1 |
        Select-String "java.specification.version" |
        ForEach-Object { $_.ToString().Split("=")[-1].Trim() }

    if ($JavaSpec) {
        $JavaMajor = [int]$JavaSpec.Split(".")[0]
        if ($JavaMajor -ge 11) {
            Write-Host "PASS: Java version $JavaSpec supported"
            Add-Content $ReportPath "PASS: Java >= 11"
        } else {
            Write-Host "FAIL: Java must be >= 11"
            Add-Content $ReportPath "FAIL: Java version too low"
            exit 1
        }
    }
}
else {
    exit 1
}

Write-Host "`nChecking Git..."
if (-not (Check-Command "git")) { exit 1 }

Write-Host "Checking curl/wget..."
if (-not (Check-Command "curl")) {
    if (-not (Check-Command "wget")) {
        Write-Host "FAIL: Neither curl nor wget found"
        exit 1
    }
}

Write-Host "`n============================================================"
Write-Host " Preflight completed successfully."
Write-Host " Report saved at: $ReportPath"
Write-Host " Proceed to Step 2: Installation of Lakebridge"
Write-Host "============================================================"
