# VCode - Multi-VSCode Launcher with Claude Auto-Execute v1.1

param(
    [Parameter(Position=0)][string]$Action = "help",
    [Parameter(Position=1)][string]$ProfileName,
    [switch]$DryRun,
    [switch]$NoAuto
)

$root = $PSScriptRoot
$config = Join-Path $root "vscode-layout.json"
$profilesDir = Join-Path $root "profiles"

function Show-Banner {
    Write-Host @"

 ██╗   ██╗ ██████╗ ██████╗ ██████╗ ███████╗
 ██║   ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝
 ██║   ██║██║     ██║   ██║██║  ██║█████╗  
 ╚██╗ ██╔╝██║     ██║   ██║██║  ██║██╔══╝  
  ╚████╔╝ ╚██████╗╚██████╔╝██████╔╝███████╗
   ╚═══╝   ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
                                    v1.1
"@ -ForegroundColor Cyan
}

function Show-Help {
    Show-Banner
    Write-Host "  Usage: ./vcode.ps1 <action> [profile] [options]`n" -ForegroundColor White
    Write-Host "  Actions:" -ForegroundColor Yellow
    Write-Host "    detect       Save current window layout"
    Write-Host "    launch       Launch all + position + Claude"
    Write-Host "    reposition   Reposition existing windows"
    Write-Host "    status       Show current windows"
    Write-Host "    profiles     List available profiles"
    Write-Host "    use <name>   Switch to profile (work/home)"
    Write-Host ""
    Write-Host "  Options:" -ForegroundColor Yellow
    Write-Host "    -DryRun      Preview only"
    Write-Host "    -NoAuto      Skip Claude execution"
    Write-Host ""
    Write-Host "  Profiles:" -ForegroundColor Yellow
    Write-Host "    work         회사용 (자동화/분석)"
    Write-Host "    home         집용 (YouTube/콘텐츠)"
    Write-Host ""
}

function Show-Profiles {
    Show-Banner
    Write-Host "  Available Profiles:`n" -ForegroundColor Yellow
    
    Get-ChildItem "$profilesDir/*.json" -ErrorAction SilentlyContinue | ForEach-Object {
        $p = Get-Content $_.FullName -Raw | ConvertFrom-Json
        $count = ($p.projects | Where-Object { $_.enabled }).Count
        Write-Host "    $($p.name)" -ForegroundColor Green -NoNewline
        Write-Host " - $($p.description) ($count projects)" -ForegroundColor Gray
    }
    Write-Host ""
}

function Use-Profile {
    param([string]$Name)
    
    $profilePath = Join-Path $profilesDir "$Name.json"
    
    if (-not (Test-Path $profilePath)) {
        Write-Host "  [X] Profile not found: $Name" -ForegroundColor Red
        Write-Host "  Available: work, home" -ForegroundColor Gray
        return
    }
    
    Copy-Item $profilePath $config -Force
    $p = Get-Content $profilePath -Raw | ConvertFrom-Json
    $count = ($p.projects | Where-Object { $_.enabled }).Count
    
    Write-Host "  [+] Switched to: $Name ($($p.description))" -ForegroundColor Green
    Write-Host "  [*] Projects: $count enabled" -ForegroundColor Cyan
    Write-Host ""
}

switch ($Action.ToLower()) {
    "detect" {
        Show-Banner
        & "$root\detect-layout.ps1"
        if (Test-Path "$root\current-layout.json") {
            Copy-Item "$root\current-layout.json" $config -Force
            Write-Host "`n  [+] Layout saved to vscode-layout.json" -ForegroundColor Green
        }
    }
    "launch" {
        Show-Banner
        $args = @()
        if ($DryRun) { $args += "-DryRun" }
        if ($NoAuto) { $args += "-NoAutoExecute" }
        & "$root\launch-layout.ps1" @args
    }
    "reposition" {
        Show-Banner
        $args = @()
        if ($DryRun) { $args += "-DryRun" }
        & "$root\reposition-layout.ps1" @args
    }
    "status" {
        Show-Banner
        $windows = Get-Process -Name "Code" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match "Visual Studio Code" }
        Write-Host "  Running VSCode: $($windows.Count) windows`n" -ForegroundColor Cyan
        $windows | ForEach-Object { Write-Host "    [+] $($_.MainWindowTitle)" -ForegroundColor Green }
        
        if (Test-Path $config) {
            $cfg = Get-Content $config -Raw | ConvertFrom-Json
            if ($cfg.name) {
                Write-Host "`n  Current Profile: $($cfg.name)" -ForegroundColor Yellow
            }
        }
        Write-Host ""
    }
    "profiles" {
        Show-Profiles
    }
    "use" {
        Show-Banner
        if ($ProfileName) {
            Use-Profile -Name $ProfileName
        } else {
            Write-Host "  [!] Usage: ./vcode.ps1 use <profile-name>" -ForegroundColor Yellow
            Show-Profiles
        }
    }
    default { Show-Help }
}
