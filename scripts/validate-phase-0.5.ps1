# Phase 0.5 검증: Task List 파일 존재 및 Task 0.0 완료 확인
# Windows PowerShell 전용 버전

param(
    [Parameter(Mandatory=$true)]
    [string]$PRD_NUM
)

$ErrorActionPreference = "Stop"

# Task List 파일 존재 확인
$TASK_PATTERN = "tasks\$PRD_NUM-tasks-*.md"
$TASK_FILE = Get-ChildItem -Path $TASK_PATTERN -ErrorAction SilentlyContinue | Select-Object -First 1

if (-not $TASK_FILE) {
    Write-Host "❌ Phase 0.5 검증 실패: Task List 파일 없음" -ForegroundColor Red
    Write-Host "   경로: $TASK_PATTERN"
    Write-Host ""
    Write-Host "📝 Phase 0.5 요구사항:" -ForegroundColor Yellow
    Write-Host "   1. tasks\$PRD_NUM-tasks-feature-name.md 파일 생성 필요"
    Write-Host "   2. Task generation: python scripts\generate_tasks_ai.py 또는 Claude 대화로 생성"
    exit 1
}

# Task 0.0 완료 확인
$content = Get-Content -Path $TASK_FILE.FullName -Raw -Encoding UTF8

if (-not ($content -match "## Task 0.0")) {
    Write-Host "❌ Phase 0.5 검증 실패: Task 0.0이 없습니다" -ForegroundColor Red
    Write-Host "   Task 0.0은 필수 (Setup: Create branch, Update CLAUDE.md)" -ForegroundColor Yellow
    exit 1
}

# Task 0.0 완료 여부 확인
if ($content -match "## Task 0.0.*?\[x\]") {
    Write-Host "✅ Phase 0.5 검증 통과" -ForegroundColor Green
    Write-Host "   Task List 파일: $($TASK_FILE.FullName)"
    Write-Host "   Task 0.0: 완료 ✓"
} else {
    Write-Host "⚠️  Phase 0.5 진행 중" -ForegroundColor Yellow
    Write-Host "   Task List 파일: $($TASK_FILE.FullName)"
    Write-Host "   Task 0.0: 미완료 - 브랜치 생성 필요"
    Write-Host ""
    Write-Host "다음 작업:" -ForegroundColor Cyan
    Write-Host "   git checkout -b feature/PRD-$PRD_NUM-feature-name"
    exit 1
}

# 진행률 표시
$total = ([regex]::Matches($content, "\[.\]")).Count
$completed = ([regex]::Matches($content, "\[x\]")).Count

if ($total -gt 0) {
    $percentage = [math]::Round(($completed / $total) * 100)
    Write-Host "   진행률: $completed/$total ($percentage%)"
}

Write-Host ""
Write-Host "다음 단계: Phase 1 (Implementation)" -ForegroundColor Cyan
Write-Host "   python scripts\validate_phase_universal.py 1"
