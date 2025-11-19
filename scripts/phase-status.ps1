# Phase 진행 상태 확인
# Windows PowerShell 전용 버전

$ErrorActionPreference = "Continue"

Write-Host "Phase 진행 상태 확인" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# PRD 파일 찾기
$prds = Get-ChildItem -Path "tasks\prds\*-prd-*.md" -ErrorAction SilentlyContinue

if ($prds.Count -eq 0) {
    Write-Host "PRD 없음 (Phase 0 시작 전)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "시작하기:" -ForegroundColor Cyan
    Write-Host "   1. PRD 작성: vim tasks\prds\0001-prd-feature.md"
    Write-Host "   2. Task List: python scripts\generate_tasks_ai.py"
    exit 0
}

# 각 PRD별 상태 확인
foreach ($prd in $prds) {
    $prdNum = $prd.Name -replace '-prd-.*', ''
    $prdName = $prd.Name -replace '^[0-9]+-prd-(.*)\.md$', '$1'

    Write-Host "PRD-$prdNum: $prdName" -ForegroundColor Green
    Write-Host "-" * 60

    # Phase 0
    if (Test-Path $prd.FullName) {
        $lines = (Get-Content $prd.FullName | Measure-Object -Line).Lines
        Write-Host "   Phase 0 (PRD): ✅ 완료 ($lines lines)" -ForegroundColor Green
    }

    # Phase 0.5
    $taskFile = Get-ChildItem -Path "tasks\$prdNum-tasks-*.md" -ErrorAction SilentlyContinue
    if ($taskFile) {
        $content = Get-Content $taskFile.FullName -Raw
        $total = ([regex]::Matches($content, "\[.\]")).Count
        $completed = ([regex]::Matches($content, "\[x\]")).Count

        if ($total -gt 0) {
            $percentage = [math]::Round(($completed / $total) * 100)
            Write-Host "   Phase 0.5 (Tasks): ✅ 완료 ($completed/$total, $percentage%)" -ForegroundColor Green
        }
    } else {
        Write-Host "   Phase 0.5 (Tasks): ❌ 미완료" -ForegroundColor Red
    }

    # Phase 1 (src 파일 확인)
    if (Test-Path "src") {
        $srcFiles = Get-ChildItem -Path "src" -Recurse -Include *.py,*.ts,*.tsx,*.js,*.jsx -ErrorAction SilentlyContinue
        if ($srcFiles) {
            Write-Host "   Phase 1 (Code): ✅ 진행 중 ($($srcFiles.Count) files)" -ForegroundColor Yellow
        }
    }

    # Phase 2 (테스트 확인)
    if (Test-Path "tests") {
        $testFiles = Get-ChildItem -Path "tests" -Recurse -Include *.py,*.test.ts,*.test.tsx,*.test.js,*.test.jsx -ErrorAction SilentlyContinue
        if ($testFiles) {
            Write-Host "   Phase 2 (Tests): ✅ 진행 중 ($($testFiles.Count) files)" -ForegroundColor Yellow
        }
    }

    # Phase 3 (Git tag 확인)
    $tags = & git tag -l "v*" 2>&1
    if ($tags) {
        $latestTag = $tags | Select-Object -Last 1
        Write-Host "   Phase 3 (Version): ✅ $latestTag" -ForegroundColor Green
    }

    Write-Host ""
}

Write-Host "=" * 60
Write-Host ""
Write-Host "상세 검증:" -ForegroundColor Cyan
Write-Host "   python scripts\validate_phase_universal.py <PHASE> [ARGS]"
