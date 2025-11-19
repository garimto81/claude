# GitHub Labels 설정 스크립트
# Windows PowerShell 전용 버전
# Phase 0-6 워크플로우에 필요한 라벨 자동 생성

$ErrorActionPreference = "Stop"

Write-Host "GitHub Labels 설정 시작..." -ForegroundColor Cyan
Write-Host ""

# gh CLI 확인
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 오류: GitHub CLI (gh) 설치 필요" -ForegroundColor Red
    Write-Host ""
    Write-Host "설치 방법:" -ForegroundColor Yellow
    Write-Host "   winget install GitHub.cli"
    Write-Host "   또는"
    Write-Host "   scoop install gh"
    exit 1
}

# GitHub 인증 확인
$authStatus = & gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 오류: GitHub 인증 필요" -ForegroundColor Red
    Write-Host ""
    Write-Host "인증 방법:" -ForegroundColor Yellow
    Write-Host "   gh auth login"
    exit 1
}

# Phase 라벨 정의
$LABELS = @(
    @{name="phase-0-prd"; color="d73a4a"; description="Phase 0: PRD (Product Requirements Document)"},
    @{name="phase-0.5-tasks"; color="d876e3"; description="Phase 0.5: Task List Generation"},
    @{name="phase-1-implementation"; color="0075ca"; description="Phase 1: Code Implementation"},
    @{name="phase-2-testing"; color="cfd3d7"; description="Phase 2: Testing & Validation"},
    @{name="phase-2.5-review"; color="fbca04"; description="Phase 2.5: Code/Design/Security Review"},
    @{name="phase-3-versioning"; color="a2eeef"; description="Phase 3: Semantic Versioning"},
    @{name="phase-4-git"; color="7057ff"; description="Phase 4: Git Commit & PR"},
    @{name="phase-5-e2e"; color="008672"; description="Phase 5: E2E & Security Testing"},
    @{name="phase-6-deploy"; color="0e8a16"; description="Phase 6: Deployment"},
    @{name="blocked"; color="b60205"; description="Blocked by dependency or issue"},
    @{name="ready-to-merge"; color="0e8a16"; description="All checks passed, ready for merge"}
)

# 라벨 생성
$created = 0
$skipped = 0

foreach ($label in $LABELS) {
    Write-Host "라벨 생성: $($label.name)..." -NoNewline

    $result = & gh label create $label.name --color $label.color --description $label.description --force 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
        $created++
    } else {
        if ($result -match "already exists") {
            Write-Host " ⏭️ (이미 존재)" -ForegroundColor Yellow
            $skipped++
        } else {
            Write-Host " ❌" -ForegroundColor Red
            Write-Host "   오류: $result" -ForegroundColor Red
        }
    }
}

# 결과 요약
Write-Host ""
Write-Host "✅ GitHub Labels 설정 완료" -ForegroundColor Green
Write-Host "   생성: $created개"
Write-Host "   기존: $skipped개"
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "   1. GitHub Issue 생성 (gh issue create)"
Write-Host "   2. Phase 라벨 적용"
Write-Host "   3. 작업 시작 (.\scripts\github-issue-dev.ps1 <ISSUE_NUMBER>)"
