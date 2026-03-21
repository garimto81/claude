#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Create Hyper-V VM for PokerGFX testing (BitDefender bypass)
.EXAMPLE
    .\create-pokergfx-vm.ps1
    .\create-pokergfx-vm.ps1 -ISOPath "D:\Win11.iso"
#>

param(
    [string]$VMName = "PokerGFX-Test",
    [string]$VMPath = "C:\HyperV\VMs",
    [int]$MemoryGB = 16,
    [int]$ProcessorCount = 8,
    [int]$DiskSizeGB = 80,
    [string]$ISOPath = ""
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PokerGFX Hyper-V VM Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Validate
Write-Host "[1/6] Validating..." -ForegroundColor Yellow

$vmms = Get-Service vmms -ErrorAction SilentlyContinue
if (-not $vmms -or $vmms.Status -ne 'Running') {
    Write-Host "  ERROR: Hyper-V service not running." -ForegroundColor Red
    exit 1
}
Write-Host "  Hyper-V service: OK" -ForegroundColor Green

$existingVM = Get-VM -Name $VMName -ErrorAction SilentlyContinue
if ($existingVM) {
    Write-Host "  WARNING: VM '$VMName' already exists." -ForegroundColor Yellow
    $choice = Read-Host "  Delete and recreate? (y/n)"
    if ($choice -eq 'y') {
        if ($existingVM.State -eq 'Running') { Stop-VM -Name $VMName -Force }
        Remove-VM -Name $VMName -Force
        $oldVhd = Join-Path $VMPath "$VMName"
        if (Test-Path $oldVhd) { Remove-Item $oldVhd -Recurse -Force }
        Write-Host "  Existing VM deleted." -ForegroundColor Green
    } else {
        Write-Host "  Cancelled." -ForegroundColor Yellow
        exit 0
    }
}

if (-not (Test-Path $VMPath)) {
    New-Item -Path $VMPath -ItemType Directory -Force | Out-Null
}
Write-Host "  VM path: $VMPath" -ForegroundColor Green
Write-Host ""

# Step 2: Network switch
Write-Host "[2/6] Network setup..." -ForegroundColor Yellow

$switch = Get-VMSwitch -ErrorAction SilentlyContinue |
    Where-Object { $_.SwitchType -eq 'External' } |
    Select-Object -First 1

if (-not $switch) {
    $switch = Get-VMSwitch -Name "Default Switch" -ErrorAction SilentlyContinue
}

if (-not $switch) {
    $netAdapter = Get-NetAdapter -Physical | Where-Object { $_.Status -eq 'Up' } | Select-Object -First 1
    if ($netAdapter) {
        New-VMSwitch -Name "PokerGFX-Switch" -NetAdapterName $netAdapter.Name -AllowManagementOS $true | Out-Null
        $switch = Get-VMSwitch -Name "PokerGFX-Switch"
        Write-Host "  Created external switch: PokerGFX-Switch" -ForegroundColor Green
    } else {
        New-VMSwitch -Name "PokerGFX-Switch" -SwitchType Internal | Out-Null
        $switch = Get-VMSwitch -Name "PokerGFX-Switch"
        Write-Host "  Created internal switch (no physical adapter)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  Using existing switch: $($switch.Name)" -ForegroundColor Green
}
Write-Host ""

# Step 3: Windows ISO
Write-Host "[3/6] Checking Windows ISO..." -ForegroundColor Yellow

if ($ISOPath -and (Test-Path $ISOPath)) {
    Write-Host "  ISO found: $ISOPath" -ForegroundColor Green
} else {
    $foundISO = Get-ChildItem -Path "C:\","D:\" -Filter "*.iso" -Recurse -Depth 2 -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "Win|win|W11|W10" -and $_.Length -gt 3GB } |
        Select-Object -First 1

    if ($foundISO) {
        $ISOPath = $foundISO.FullName
        Write-Host "  ISO found: $ISOPath" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "  Windows 11 ISO required." -ForegroundColor Yellow
        Write-Host "  Download: https://www.microsoft.com/software-download/windows11" -ForegroundColor Cyan
        Write-Host ""
        $ISOPath = Read-Host "  Enter ISO path (or press Enter to skip)"
    }
}
Write-Host ""

# Step 4: Create VM
Write-Host "[4/6] Creating VM..." -ForegroundColor Yellow

$vhdxPath = Join-Path $VMPath "$VMName\$VMName.vhdx"

$vm = New-VM -Name $VMName `
    -Path $VMPath `
    -MemoryStartupBytes ([int64]$MemoryGB * 1GB) `
    -Generation 2 `
    -NewVHDPath $vhdxPath `
    -NewVHDSizeBytes ([int64]$DiskSizeGB * 1GB) `
    -SwitchName $switch.Name

Write-Host "  VM created: $VMName" -ForegroundColor Green

# Step 5: Configure VM
Write-Host "[5/6] Configuring VM..." -ForegroundColor Yellow

Set-VMProcessor -VMName $VMName -Count $ProcessorCount
Write-Host "  CPU: ${ProcessorCount} vCPU" -ForegroundColor Green

Set-VMMemory -VMName $VMName -DynamicMemoryEnabled $false
Write-Host "  RAM: ${MemoryGB} GB (static)" -ForegroundColor Green

Set-VM -VMName $VMName -EnhancedSessionTransportType HvSocket -ErrorAction SilentlyContinue
Write-Host "  Enhanced Session: enabled" -ForegroundColor Green

Set-VMFirmware -VMName $VMName -SecureBootTemplate MicrosoftWindows -ErrorAction SilentlyContinue
Write-Host "  Secure Boot: Windows template" -ForegroundColor Green

try {
    $guardian = Get-HgsGuardian -Name "PokerGFX-Guardian" -ErrorAction SilentlyContinue
    if (-not $guardian) {
        $guardian = New-HgsGuardian -Name "PokerGFX-Guardian" -GenerateCertificates
    }
    $kp = New-HgsKeyProtector -Owner $guardian -AllowUntrustedRoot
    Set-VMKeyProtector -VMName $VMName -KeyProtector $kp.RawData
    Enable-VMTPM -VMName $VMName
    Write-Host "  TPM 2.0: enabled" -ForegroundColor Green
} catch {
    Write-Host "  TPM: skipped ($($_.Exception.Message))" -ForegroundColor Yellow
}

Set-VM -VMName $VMName -CheckpointType Standard
Write-Host "  Checkpoint: Standard" -ForegroundColor Green

if ($ISOPath -and (Test-Path $ISOPath)) {
    Add-VMDvdDrive -VMName $VMName -Path $ISOPath
    $dvd = Get-VMDvdDrive -VMName $VMName
    Set-VMFirmware -VMName $VMName -FirstBootDevice $dvd
    Write-Host "  ISO attached: $(Split-Path $ISOPath -Leaf)" -ForegroundColor Green
} else {
    Write-Host "  ISO: not attached (can add later)" -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Stage PokerGFX files
Write-Host "[6/6] Staging PokerGFX files..." -ForegroundColor Yellow

$pokergfxSource = "C:\Program Files\PokerGFX"
$pokergfxStaging = "C:\HyperV\PokerGFX-Staging"

if (Test-Path $pokergfxSource) {
    if (-not (Test-Path $pokergfxStaging)) {
        New-Item -Path $pokergfxStaging -ItemType Directory -Force | Out-Null
    }
    Copy-Item -Path "$pokergfxSource\*" -Destination $pokergfxStaging -Recurse -Force
    Write-Host "  PokerGFX staged: $pokergfxStaging" -ForegroundColor Green
} else {
    Write-Host "  PokerGFX source not found: $pokergfxSource" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VM Created Successfully!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Name:       $VMName"
Write-Host "  CPU:        $ProcessorCount vCPU"
Write-Host "  RAM:        $MemoryGB GB"
Write-Host "  Disk:       $DiskSizeGB GB"
Write-Host "  Network:    $($switch.Name)"
Write-Host "  VHDX:       $vhdxPath"
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
$startCmd = "Start-VM -Name " + $VMName
$connectCmd = "vmconnect.exe localhost " + $VMName
$checkpointCmd = "Checkpoint-VM -Name " + $VMName
Write-Host "  1. Start VM:     $startCmd" -ForegroundColor White
Write-Host "  2. Connect VM:   $connectCmd" -ForegroundColor White
Write-Host "  3. Install Windows 11 from ISO" -ForegroundColor White
Write-Host "  4. Connect via Enhanced Session" -ForegroundColor White
Write-Host "  5. Copy PokerGFX from $pokergfxStaging" -ForegroundColor White
Write-Host "  6. Run PokerGFX-Server.exe" -ForegroundColor White
Write-Host "  7. On success:   $checkpointCmd" -ForegroundColor White
Write-Host ""
