#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Download Windows 11 ISO using Media Creation Tool
.DESCRIPTION
    Downloads MCT and creates a Windows 11 ISO automatically.
    Output: C:\HyperV\Win11.iso
#>

param(
    [string]$OutputPath = "C:\HyperV",
    [string]$ISOName = "Win11.iso"
)

$ErrorActionPreference = "Stop"
$mctUrl = "https://go.microsoft.com/fwlink/?linkid=2156295"
$mctPath = Join-Path $OutputPath "MediaCreationTool.exe"
$isoPath = Join-Path $OutputPath $ISOName

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Windows 11 ISO Download" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputPath)) {
    New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null
}

# Check if ISO already exists
if (Test-Path $isoPath) {
    $size = [math]::Round((Get-Item $isoPath).Length / 1GB, 1)
    Write-Host "  ISO already exists: $isoPath ($size GB)" -ForegroundColor Green
    Write-Host "  Delete it first if you want to re-download." -ForegroundColor Yellow
    exit 0
}

# Step 1: Download Media Creation Tool
Write-Host "[1/2] Downloading Media Creation Tool..." -ForegroundColor Yellow

try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $mctUrl -OutFile $mctPath -UseBasicParsing
    Write-Host "  MCT downloaded: $mctPath" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Download failed." -ForegroundColor Red
    Write-Host "  Manual download: https://www.microsoft.com/software-download/windows11" -ForegroundColor Cyan
    exit 1
}

# Step 2: Run MCT to create ISO
Write-Host "[2/2] Creating ISO (this takes 15-30 min)..." -ForegroundColor Yellow
Write-Host "  Output: $isoPath" -ForegroundColor Gray
Write-Host ""

# MCT command-line options for unattended ISO creation
# /Eula Accept  /Retail  /MediaArch x64  /MediaLangCode ko-kr  /MediaEdition Enterprise
$mctArgs = "/Eula Accept /Retail /MediaArch x64 /MediaLangCode ko-kr /Action CreateMedia /MediaPath $isoPath"

Write-Host "  Starting Media Creation Tool..." -ForegroundColor Yellow
Write-Host "  (MCT UI will appear - select ISO file option)" -ForegroundColor Gray
Write-Host ""

# MCT does not fully support silent ISO creation in all versions
# Launch it and let user follow the wizard
Start-Process -FilePath $mctPath -Wait

# Verify
if (Test-Path $isoPath) {
    $size = [math]::Round((Get-Item $isoPath).Length / 1GB, 1)
    Write-Host ""
    Write-Host "  ISO created: $isoPath ($size GB)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Next: Run VM creation script:" -ForegroundColor Yellow
    Write-Host "  .\create-pokergfx-vm.ps1 -ISOPath $isoPath" -ForegroundColor Cyan
} else {
    # MCT might save to a different location - search for it
    Write-Host ""
    Write-Host "  ISO not found at expected path." -ForegroundColor Yellow
    Write-Host "  Check where MCT saved the ISO and run:" -ForegroundColor Yellow
    Write-Host "  .\create-pokergfx-vm.ps1 -ISOPath <path-to-iso>" -ForegroundColor Cyan
}

# Cleanup MCT
Remove-Item $mctPath -Force -ErrorAction SilentlyContinue

Write-Host ""
