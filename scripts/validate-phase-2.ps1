# Phase 2 검증: 테스트 실행 및 커버리지 확인
# Windows PowerShell 전용 버전

param(
    [int]$CoverageThreshold = 80
)

$ErrorActionPreference = "Stop"

Write-Host "Phase 2 검증: 테스트 실행 및 커버리지" -ForegroundColor Cyan
Write-Host ""

# Python 프로젝트 확인
if (Test-Path "pytest.ini" -or Test-Path "pyproject.toml" -or Test-Path "setup.py") {
    Write-Host "Python 프로젝트 감지됨" -ForegroundColor Green

    # pytest 실행
    Write-Host "pytest 실행 중..." -ForegroundColor Cyan
    $pytestResult = & pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=xml 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Phase 2 검증 실패: 테스트 실패" -ForegroundColor Red
        Write-Host $pytestResult
        exit 1
    }

    # 커버리지 확인
    if (Test-Path "coverage.xml") {
        [xml]$coverage = Get-Content "coverage.xml"
        $line_rate = [math]::Round([double]$coverage.coverage.'line-rate' * 100, 2)

        Write-Host "   테스트 커버리지: $line_rate%" -ForegroundColor Green

        if ($line_rate -lt $CoverageThreshold) {
            Write-Host "❌ Phase 2 검증 실패: 커버리지 부족" -ForegroundColor Red
            Write-Host "   요구: $CoverageThreshold%, 현재: $line_rate%"
            exit 1
        }
    }
}

# Node.js 프로젝트 확인
if (Test-Path "package.json") {
    Write-Host "Node.js 프로젝트 감지됨" -ForegroundColor Green

    # npm test 실행
    Write-Host "npm test 실행 중..." -ForegroundColor Cyan
    $npmResult = & npm test 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Phase 2 검증 실패: 테스트 실패" -ForegroundColor Red
        Write-Host $npmResult
        exit 1
    }
}

# 성공
Write-Host ""
Write-Host "✅ Phase 2 검증 통과" -ForegroundColor Green
Write-Host "   모든 테스트 통과"
Write-Host ""
Write-Host "다음 단계: Phase 3 (Versioning)" -ForegroundColor Cyan
Write-Host "   python scripts\validate_phase_universal.py 3 v1.x.x"
