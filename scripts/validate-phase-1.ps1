# Phase 1 검증: 1:1 test pairing 확인
# Windows PowerShell 전용 버전

$ErrorActionPreference = "Stop"

Write-Host "Phase 1 검증: 1:1 테스트 pairing 확인" -ForegroundColor Cyan
Write-Host ""

# src 디렉토리 확인
if (-not (Test-Path "src")) {
    Write-Host "⚠️  경고: src 디렉토리가 없습니다" -ForegroundColor Yellow
    Write-Host "   아직 구현 파일이 없으면 정상입니다"
    exit 0
}

# 구현 파일 찾기 (Python, TypeScript, JavaScript)
$SRC_FILES = Get-ChildItem -Path "src" -Recurse -Include *.py,*.ts,*.tsx,*.js,*.jsx -ErrorAction SilentlyContinue

if ($SRC_FILES.Count -eq 0) {
    Write-Host "⚠️  경고: src 디렉토리에 구현 파일이 없습니다" -ForegroundColor Yellow
    exit 0
}

Write-Host "구현 파일 발견: $($SRC_FILES.Count)개" -ForegroundColor Green

# 1:1 테스트 pairing 검증
$ORPHANED = @()

foreach ($SRC_FILE in $SRC_FILES) {
    $relativePath = $SRC_FILE.FullName -replace [regex]::Escape((Get-Location).Path + "\"), ""
    $testPath = $relativePath -replace "^src\\", "tests\test_" -replace "\.py$", ".py" `
                               -replace "\.ts$", ".test.ts" `
                               -replace "\.tsx$", ".test.tsx" `
                               -replace "\.js$", ".test.js" `
                               -replace "\.jsx$", ".test.jsx"

    if (-not (Test-Path $testPath)) {
        $ORPHANED += $relativePath
        Write-Host "❌ 테스트 누락: $relativePath" -ForegroundColor Red
        Write-Host "   예상 위치: $testPath"
    }
}

# 결과 출력
if ($ORPHANED.Count -eq 0) {
    Write-Host ""
    Write-Host "✅ Phase 1 검증 통과" -ForegroundColor Green
    Write-Host "   모든 구현 파일에 테스트가 있습니다"
    Write-Host ""
    Write-Host "다음 단계: Phase 2 (Testing)" -ForegroundColor Cyan
    Write-Host "   python scripts\validate_phase_universal.py 2"
} else {
    Write-Host ""
    Write-Host "❌ Phase 1 검증 실패: $($ORPHANED.Count)개 파일에 테스트 누락" -ForegroundColor Red
    Write-Host ""
    Write-Host "📝 Phase 1 필수 규칙: 1:1 Test Pairing" -ForegroundColor Yellow
    Write-Host "   모든 구현 파일은 반드시 대응하는 테스트 파일이 있어야 합니다"
    Write-Host ""
    Write-Host "수정 방법:" -ForegroundColor Cyan
    Write-Host "   python scripts\validate-test-pairing.py --fix"
    exit 1
}
