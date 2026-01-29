# setup_subproject_claude.ps1
# 서브프로젝트에 .claude/skills 심볼릭 링크 생성
# 관리자 권한 필요

param(
    [string]$RootPath = "C:\claude",
    [switch]$Force,
    [switch]$DryRun
)

# 관리자 권한 확인
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin -and -not $DryRun) {
    Write-Error "관리자 권한이 필요합니다. PowerShell을 관리자로 실행하세요."
    exit 1
}

# 서브프로젝트 목록
$subprojects = @(
    "automation_hub",
    "archive-analyzer",
    "wsoptv_ott",
    "wsoptv_nbatv_clone",
    "ebs"
)

$targetSkills = Join-Path $RootPath ".claude\skills"

if (-not (Test-Path $targetSkills)) {
    Write-Error "소스 skills 디렉토리가 없습니다: $targetSkills"
    exit 1
}

Write-Host "=== 서브프로젝트 Claude 설정 ===" -ForegroundColor Cyan
Write-Host "루트: $RootPath"
Write-Host "타겟: $targetSkills"
Write-Host ""

foreach ($proj in $subprojects) {
    $projPath = Join-Path $RootPath $proj

    if (-not (Test-Path $projPath)) {
        Write-Host "[$proj] 프로젝트 없음 - 스킵" -ForegroundColor Yellow
        continue
    }

    $claudeDir = Join-Path $projPath ".claude"
    $skillsLink = Join-Path $claudeDir "skills"

    # .claude 디렉토리 생성
    if (-not (Test-Path $claudeDir)) {
        if ($DryRun) {
            Write-Host "[$proj] DRY-RUN: .claude 디렉토리 생성됨" -ForegroundColor Magenta
        } else {
            New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
            Write-Host "[$proj] .claude 디렉토리 생성됨" -ForegroundColor Green
        }
    }

    # 기존 skills 처리
    if (Test-Path $skillsLink) {
        $item = Get-Item $skillsLink

        if ($item.LinkType -eq "SymbolicLink") {
            if ($item.LinkTarget -eq $targetSkills) {
                Write-Host "[$proj] 이미 올바른 심볼릭 링크" -ForegroundColor Gray
                continue
            } else {
                if ($Force) {
                    if ($DryRun) {
                        Write-Host "[$proj] DRY-RUN: 잘못된 링크 제거 후 재생성" -ForegroundColor Magenta
                    } else {
                        Remove-Item $skillsLink -Force
                        Write-Host "[$proj] 잘못된 링크 제거됨" -ForegroundColor Yellow
                    }
                } else {
                    Write-Host "[$proj] 다른 타겟 링크 존재 - -Force 필요" -ForegroundColor Red
                    continue
                }
            }
        } else {
            if ($Force) {
                if ($DryRun) {
                    Write-Host "[$proj] DRY-RUN: 기존 디렉토리 백업 후 링크 생성" -ForegroundColor Magenta
                } else {
                    $backup = "$skillsLink.bak.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                    Rename-Item $skillsLink $backup
                    Write-Host "[$proj] 기존 디렉토리 백업: $backup" -ForegroundColor Yellow
                }
            } else {
                Write-Host "[$proj] 기존 skills 디렉토리 존재 - -Force 필요" -ForegroundColor Red
                continue
            }
        }
    }

    # 심볼릭 링크 생성
    if ($DryRun) {
        Write-Host "[$proj] DRY-RUN: 심볼릭 링크 생성됨" -ForegroundColor Magenta
    } else {
        try {
            New-Item -ItemType SymbolicLink -Path $skillsLink -Target $targetSkills -Force | Out-Null
            Write-Host "[$proj] 심볼릭 링크 생성됨" -ForegroundColor Green
        } catch {
            Write-Host "[$proj] 링크 생성 실패: $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== 완료 ===" -ForegroundColor Cyan
