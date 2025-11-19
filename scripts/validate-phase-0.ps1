# Phase 0 검증: PRD 파일 존재 확인
# Windows PowerShell 전용 버전
# Based on cc-sdd validation system (MIT License)
# Adapted for claude01 Phase 0-6 workflow

param(
    [Parameter(Mandatory=$true)]
    [string]$PRD_NUM
)

$ErrorActionPreference = "Stop"

# PRD 파일 존재 확인
$PRD_PATTERN = "tasks\prds\$PRD_NUM-prd-*.md"
$PRD_FILE = Get-ChildItem -Path $PRD_PATTERN -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $PRD_FILE) {
    Write-Host "❌ Phase 0 검증 실패: PRD 파일 없음" -ForegroundColor Red
    Write-Host "   경로: $PRD_PATTERN"
    Write-Host ""
    Write-Host "📝 Phase 0 요구사항:" -ForegroundColor Yellow
    Write-Host "   1. tasks\prds\$PRD_NUM-prd-feature-name.md 파일 생성 필요"
    Write-Host "   2. PRD 가이드: docs\guides\PRD_GUIDE_MINIMAL.md 참고"
    exit 1
}

# PRD 내용 검증 (최소 요구사항)
$content = Get-Content -Path $PRD_FILE.FullName -Raw -Encoding UTF8

if (-not ($content -match "## 목적|## Purpose")) {
    Write-Host "⚠️  경고: PRD에 '목적' 섹션이 없습니다" -ForegroundColor Yellow
}

if (-not ($content -match "## 핵심 기능|## Core Features")) {
    Write-Host "⚠️  경고: PRD에 '핵심 기능' 섹션이 없습니다" -ForegroundColor Yellow
}

# 성공
Write-Host "✅ Phase 0 검증 통과" -ForegroundColor Green
Write-Host "   PRD 파일: $($PRD_FILE.FullName)"

# 파일 통계
$LINES = (Get-Content -Path $PRD_FILE.FullName | Measure-Object -Line).Lines
Write-Host "   라인 수: $LINES"

if ($LINES -lt 50) {
    Write-Host "   ⚠️  PRD가 너무 짧습니다 (최소 50줄 권장)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "다음 단계: Phase 0.5 (Task List)" -ForegroundColor Cyan
Write-Host "   python scripts\validate_phase_universal.py 0.5 $PRD_NUM"
