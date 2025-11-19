# Phase 5 검증: E2E & Security Testing
# Windows PowerShell 전용 버전

$ErrorActionPreference = "Stop"

Write-Host "Phase 5 검증: E2E & Security Testing" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# 1. E2E 테스트 확인
Write-Host "1. E2E 테스트 확인" -ForegroundColor Cyan

if (Test-Path "playwright.config.ts" -or Test-Path "playwright.config.js") {
    Write-Host "   Playwright 설정 감지됨" -ForegroundColor Green

    # E2E 테스트 실행
    if (Test-Path "tests\e2e" -or Test-Path "e2e") {
        Write-Host "   E2E 테스트 실행 중..." -ForegroundColor Cyan
        $playwrightResult = & npx playwright test 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ E2E 테스트 통과" -ForegroundColor Green
        } else {
            Write-Host "   ❌ E2E 테스트 실패" -ForegroundColor Red
            $allPassed = $false
        }
    } else {
        Write-Host "   ⚠️  E2E 테스트 디렉토리 없음" -ForegroundColor Yellow
        $allPassed = $false
    }
} elseif (Test-Path "cypress.config.ts" -or Test-Path "cypress.config.js") {
    Write-Host "   Cypress 설정 감지됨" -ForegroundColor Green

    if (Test-Path "cypress\e2e") {
        Write-Host "   Cypress E2E 테스트 실행 중..." -ForegroundColor Cyan
        $cypressResult = & npx cypress run 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Cypress E2E 테스트 통과" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Cypress E2E 테스트 실패" -ForegroundColor Red
            $allPassed = $false
        }
    }
} else {
    Write-Host "   ⚠️  E2E 테스트 설정 없음 (Playwright/Cypress)" -ForegroundColor Yellow
    $allPassed = $false
}

# 2. Security Audit
Write-Host ""
Write-Host "2. Security Audit" -ForegroundColor Cyan

# Node.js 프로젝트
if (Test-Path "package.json") {
    Write-Host "   npm audit 실행 중..." -ForegroundColor Cyan
    $auditResult = & npm audit --production 2>&1

    $criticalCount = ($auditResult | Select-String "critical").Matches.Count
    $highCount = ($auditResult | Select-String "high").Matches.Count

    if ($criticalCount -eq 0 -and $highCount -eq 0) {
        Write-Host "   ✅ npm audit: Critical/High 취약점 없음" -ForegroundColor Green
    } else {
        Write-Host "   ❌ npm audit: Critical ($criticalCount), High ($highCount)" -ForegroundColor Red
        Write-Host "   수정: npm audit fix" -ForegroundColor Yellow
        $allPassed = $false
    }
}

# Python 프로젝트
if (Test-Path "requirements.txt" -or Test-Path "pyproject.toml") {
    if (Get-Command pip-audit -ErrorAction SilentlyContinue) {
        Write-Host "   pip-audit 실행 중..." -ForegroundColor Cyan
        $pipAuditResult = & pip-audit 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ pip-audit: 취약점 없음" -ForegroundColor Green
        } else {
            Write-Host "   ❌ pip-audit: 취약점 발견" -ForegroundColor Red
            $allPassed = $false
        }
    } else {
        Write-Host "   ⚠️  pip-audit 미설치 (pip install pip-audit)" -ForegroundColor Yellow
    }
}

# 3. 보안 체크리스트
Write-Host ""
Write-Host "3. 보안 체크리스트" -ForegroundColor Cyan

# .env 파일 Git 추적 확인
if (Test-Path ".env") {
    $gitLs = & git ls-files ".env" 2>&1
    if ($gitLs) {
        Write-Host "   ❌ .env 파일이 Git에 추적됨 (즉시 제거 필요!)" -ForegroundColor Red
        Write-Host "   수정: git rm --cached .env && echo .env >> .gitignore" -ForegroundColor Yellow
        $allPassed = $false
    } else {
        Write-Host "   ✅ .env 파일이 Git에서 제외됨" -ForegroundColor Green
    }
}

# .env.example 확인
if (-not (Test-Path ".env.example")) {
    Write-Host "   ⚠️  .env.example 없음 (권장)" -ForegroundColor Yellow
}

# Hardcoded secrets 검색 (간단한 패턴)
Write-Host "   하드코딩된 시크릿 검색 중..." -ForegroundColor Cyan
$secretPatterns = @(
    "password\s*=\s*['\"`"](?!{{).{8,}",
    "api[_-]?key\s*=\s*['\"`"](?!{{).{20,}",
    "secret\s*=\s*['\"`"](?!{{).{10,}"
)

$secretsFound = $false
foreach ($pattern in $secretPatterns) {
    $matches = Get-ChildItem -Path . -Recurse -Include *.py,*.js,*.ts,*.tsx,*.jsx -ErrorAction SilentlyContinue |
        Select-String -Pattern $pattern -CaseSensitive

    if ($matches) {
        $secretsFound = $true
        Write-Host "   ⚠️  의심스러운 시크릿 발견:" -ForegroundColor Yellow
        $matches | ForEach-Object { Write-Host "      $($_.Path):$($_.LineNumber)" -ForegroundColor Yellow }
    }
}

if (-not $secretsFound) {
    Write-Host "   ✅ 하드코딩된 시크릿 없음 (기본 검사)" -ForegroundColor Green
}

# 4. Performance (선택)
Write-Host ""
Write-Host "4. Performance Benchmarks (선택)" -ForegroundColor Cyan
Write-Host "   ℹ️  성능 테스트는 수동으로 실행하세요" -ForegroundColor Gray
Write-Host "   예: artillery run load-test.yml" -ForegroundColor Gray

# 최종 결과
Write-Host ""
Write-Host "=" * 60

if ($allPassed) {
    Write-Host "✅ Phase 5 검증 통과" -ForegroundColor Green
    Write-Host ""
    Write-Host "다음 단계: Phase 6 (Deployment)" -ForegroundColor Cyan
    Write-Host "   python scripts\validate_phase_universal.py 6"
    exit 0
} else {
    Write-Host "❌ Phase 5 검증 실패" -ForegroundColor Red
    Write-Host "   위 항목들을 수정하세요" -ForegroundColor Yellow
    exit 1
}
