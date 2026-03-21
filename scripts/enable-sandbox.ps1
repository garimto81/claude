#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Enable Windows Sandbox feature (requires reboot)
#>

$feature = "Containers-DisposableClientVM"

Write-Host ""
Write-Host "  Enabling Windows Sandbox..." -ForegroundColor Yellow

$state = (Get-WindowsOptionalFeature -Online -FeatureName $feature).State

if ($state -eq "Enabled") {
    Write-Host "  Windows Sandbox is already enabled." -ForegroundColor Green
    exit 0
}

Enable-WindowsOptionalFeature -Online -FeatureName $feature -NoRestart

Write-Host ""
Write-Host "  Windows Sandbox enabled." -ForegroundColor Green
Write-Host "  REBOOT REQUIRED to complete installation." -ForegroundColor Red
Write-Host ""
$choice = Read-Host "  Reboot now? (y/n)"
if ($choice -eq 'y') {
    Restart-Computer -Force
}
