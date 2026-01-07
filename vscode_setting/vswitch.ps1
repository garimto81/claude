<#
.SYNOPSIS
    Vibe IDE Switcher (Multi-Instance Edition)
    8개 이상의 VS Code 인스턴스 설정을 한꺼번에 관리하고 전환합니다.

.EXAMPLE
    .\vswitch.ps1 save work
    .\vswitch.ps1 switch broadcast
    .\vswitch.ps1 list
#>

param (
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("save", "switch", "list")]
    $Action,

    [Parameter(Mandatory = $false, Position = 1)]
    $ProfileName
)

# PowerShell 출력 인코딩을 UTF-8로 설정 (한글 깨짐 방지)
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$configFile = Join-Path $PSScriptRoot "config.json"
if (-not (Test-Path $configFile)) {
    Write-Error "config.json 파일을 찾을 수 없습니다."
    exit
}

$config = Get-Content $configFile -Raw -Encoding UTF8 | ConvertFrom-Json
$profileBaseDir = $config.profileRoot

# 환경 변수($HOME, %APPDATA% 등) 처리 함수
function Resolve-PathWithEnv($path) {
    # $HOME 문자열을 실제 경로로 치환
    if ($path.Contains('$HOME')) {
        $path = $path.Replace('$HOME', $HOME)
    }
    # %APPDATA% 등 윈도우 스타일 환경변수 처리
    return [System.Environment]::ExpandEnvironmentVariables($path)
}

function List-Profiles {
    if (-not (Test-Path $profileBaseDir)) {
        Write-Host "No profiles found." -ForegroundColor Yellow
        return
    }
    $profiles = Get-ChildItem $profileBaseDir -Directory
    Write-Host "--- Saved Profiles ---" -ForegroundColor Cyan
    foreach ($p in $profiles) {
        Write-Host "- $($p.Name)"
    }
}

function Save-Profile($name) {
    $targetDir = Join-Path $profileBaseDir $name
    if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force }

    Write-Host "Saving settings to profile: '$name'..." -ForegroundColor Green

    foreach ($inst in $config.instances) {
        $sourcePath = Resolve-PathWithEnv $inst.path
        $instTargetDir = Join-Path $targetDir $inst.name
        
        if (Test-Path $sourcePath) {
            if (-not (Test-Path $instTargetDir)) { New-Item -ItemType Directory -Path $instTargetDir -Force }
            
            # Copy settings.json, keybindings.json
            @("settings.json", "keybindings.json") | ForEach-Object {
                $file = Join-Path $sourcePath $_
                if (Test-Path $file) {
                    Copy-Item $file -Destination $instTargetDir -Force
                    Write-Host "  [OK] $($inst.name) -> $_"
                }
            }
        }
        else {
            Write-Host "  [SKIP] Path not found: $($inst.name) ($sourcePath)" -ForegroundColor Gray
        }
    }
    Write-Host "Save completed successfully." -ForegroundColor Green
}

function Switch-Profile($name) {
    $sourceDir = Join-Path $profileBaseDir $name
    if (-not (Test-Path $sourceDir)) {
        Write-Error "Profile '$name' does not exist."
        return
    }

    Write-Host "Switching to profile: '$name' (Updating 8 instances)..." -ForegroundColor Cyan

    foreach ($inst in $config.instances) {
        $targetPath = Resolve-PathWithEnv $inst.path
        $instSourceDir = Join-Path $sourceDir $inst.name
        
        if (Test-Path $instSourceDir) {
            if (-not (Test-Path $targetPath)) { New-Item -ItemType Directory -Path $targetPath -Force }

            @("settings.json", "keybindings.json") | ForEach-Object {
                $file = Join-Path $instSourceDir $_
                if (Test-Path $file) {
                    Copy-Item $file -Destination $targetPath -Force
                    Write-Host "  [SWITCHED] $($inst.name) <- $_"
                }
            }
        }
        else {
            Write-Host "  [SKIP] No data for $($inst.name) in this profile." -ForegroundColor Gray
        }
    }
    Write-Host "Switch completed! Changes applied to all VS Code instances." -ForegroundColor Cyan
}

# Main Execution Line
switch ($Action) {
    "save" { 
        if (-not $ProfileName) { Write-Error "Please provide a profile name."; exit }
        Save-Profile $ProfileName 
    }
    "switch" { 
        if (-not $ProfileName) { Write-Error "Please provide a profile name."; exit }
        Switch-Profile $ProfileName 
    }
    "list" { List-Profiles }
}
