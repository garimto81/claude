# Phase 3 검증: Semantic Versioning 및 CHANGELOG 확인
# Windows PowerShell 전용 버전

param(
    [Parameter(Mandatory=$true)]
    [string]$VERSION_TAG
)

$ErrorActionPreference = "Stop"

Write-Host "Phase 3 검증: Semantic Versioning" -ForegroundColor Cyan
Write-Host ""

# 버전 태그 형식 확인
if ($VERSION_TAG -notmatch '^v\d+\.\d+\.\d+$') {
    Write-Host "❌ Phase 3 검증 실패: 잘못된 버전 형식" -ForegroundColor Red
    Write-Host "   입력: $VERSION_TAG"
    Write-Host "   요구: vMAJOR.MINOR.PATCH (예: v1.2.0)"
    exit 1
}

Write-Host "버전 태그: $VERSION_TAG ✓" -ForegroundColor Green

# 테스트 실행 (Phase 2 재검증)
Write-Host "테스트 재실행 중..." -ForegroundColor Cyan

if (Test-Path "pytest.ini" -or Test-Path "pyproject.toml") {
    $pytestResult = & pytest tests/ -v 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Phase 3 검증 실패: 테스트 실패" -ForegroundColor Red
        exit 1
    }
    Write-Host "   pytest: 통과 ✓" -ForegroundColor Green
}

if (Test-Path "package.json") {
    $npmResult = & npm test 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Phase 3 검증 실패: 테스트 실패" -ForegroundColor Red
        exit 1
    }
    Write-Host "   npm test: 통과 ✓" -ForegroundColor Green
}

# CHANGELOG.md 확인
if (-not (Test-Path "CHANGELOG.md")) {
    Write-Host "❌ Phase 3 검증 실패: CHANGELOG.md 없음" -ForegroundColor Red
    Write-Host ""
    Write-Host "CHANGELOG.md 생성 필요:" -ForegroundColor Yellow
    Write-Host "   .\scripts\create-changelog-entry.ps1 $VERSION_TAG"
    exit 1
}

# CHANGELOG에 버전 엔트리 확인
$changelog = Get-Content "CHANGELOG.md" -Raw -Encoding UTF8
$versionPattern = "\[$($VERSION_TAG -replace '^v', '')\]"

if ($changelog -notmatch $versionPattern) {
    Write-Host "❌ Phase 3 검증 실패: CHANGELOG에 $VERSION_TAG 엔트리 없음" -ForegroundColor Red
    Write-Host ""
    Write-Host "CHANGELOG.md 업데이트 필요:" -ForegroundColor Yellow
    Write-Host "   ## [$($VERSION_TAG -replace '^v', '')] - $(Get-Date -Format 'yyyy-MM-dd')"
    Write-Host "   ### Added"
    Write-Host "   - 기능 설명"
    exit 1
}

Write-Host "   CHANGELOG.md: 업데이트 확인 ✓" -ForegroundColor Green

# Uncommitted changes 확인
$gitStatus = & git status --porcelain 2>&1
if ($gitStatus) {
    Write-Host "⚠️  경고: Uncommitted changes 있음" -ForegroundColor Yellow
    Write-Host "$gitStatus"
    Write-Host ""
    Write-Host "커밋 후 태그 생성하세요:" -ForegroundColor Cyan
    Write-Host "   git add ."
    Write-Host "   git commit -m ""chore: Prepare release $VERSION_TAG"""
}

# 성공
Write-Host ""
Write-Host "✅ Phase 3 검증 통과" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계: Git Tag 생성" -ForegroundColor Cyan
Write-Host "   git tag -a $VERSION_TAG -m ""Release $VERSION_TAG"""
Write-Host "   git push origin $VERSION_TAG"
Write-Host ""
Write-Host "그 다음: Phase 4 (Git Commit & PR)" -ForegroundColor Cyan
Write-Host "   git commit -m ""feat: Add feature ($VERSION_TAG) [PRD-NNNN]"""
Write-Host "   git push"
