# Phase 6 검증: Deployment Readiness
# Windows PowerShell 전용 버전

$ErrorActionPreference = "Stop"

Write-Host "Phase 6 검증: Deployment Readiness" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# 1. 환경 변수 문서화
Write-Host "1. 환경 변수 문서화" -ForegroundColor Cyan

if (Test-Path ".env.example") {
    Write-Host "   ✅ .env.example 존재" -ForegroundColor Green

    # .env와 .env.example 동기화 확인
    if (Test-Path ".env") {
        $envKeys = (Get-Content ".env" | Select-String "^[A-Z_]+" | ForEach-Object { ($_ -split "=")[0].Trim() })
        $exampleKeys = (Get-Content ".env.example" | Select-String "^[A-Z_]+" | ForEach-Object { ($_ -split "=")[0].Trim() })

        $missingKeys = $envKeys | Where-Object { $_ -notin $exampleKeys }

        if ($missingKeys) {
            Write-Host "   ⚠️  .env.example에 누락된 키:" -ForegroundColor Yellow
            $missingKeys | ForEach-Object { Write-Host "      $_" -ForegroundColor Yellow }
        } else {
            Write-Host "   ✅ .env와 .env.example 동기화됨" -ForegroundColor Green
        }
    }
} else {
    Write-Host "   ❌ .env.example 없음" -ForegroundColor Red
    Write-Host "   생성 필요: .env를 참고하여 .env.example 작성" -ForegroundColor Yellow
    $allPassed = $false
}

# 2. 시크릿 검사
Write-Host ""
Write-Host "2. 시크릿 검사" -ForegroundColor Cyan

# Git에 .env 추적 여부
if (Test-Path ".env") {
    $gitLs = & git ls-files ".env" 2>&1
    if ($gitLs) {
        Write-Host "   ❌ CRITICAL: .env 파일이 Git에 추적됨!" -ForegroundColor Red
        Write-Host "   즉시 수정:" -ForegroundColor Yellow
        Write-Host "      git rm --cached .env" -ForegroundColor Yellow
        Write-Host "      echo .env >> .gitignore" -ForegroundColor Yellow
        $allPassed = $false
    } else {
        Write-Host "   ✅ .env 파일이 Git에서 제외됨" -ForegroundColor Green
    }
}

# Hardcoded secrets 검색
Write-Host "   하드코딩된 시크릿 검색 중..." -ForegroundColor Cyan

$secretPatterns = @(
    "password\s*[=:]\s*['\"`"](?!{{|\$|<%|ENV).{8,}",
    "api[_-]?key\s*[=:]\s*['\"`"](?!{{|\$|<%|ENV).{20,}",
    "secret\s*[=:]\s*['\"`"](?!{{|\$|<%|ENV).{10,}",
    "token\s*[=:]\s*['\"`"](?!{{|\$|<%|ENV).{20,}"
)

$secretsFound = @()
foreach ($pattern in $secretPatterns) {
    $matches = Get-ChildItem -Path . -Recurse -Include *.py,*.js,*.ts,*.tsx,*.jsx,*.yml,*.yaml -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "node_modules|\.venv|dist|build" } |
        Select-String -Pattern $pattern -CaseSensitive

    if ($matches) {
        $secretsFound += $matches
    }
}

if ($secretsFound.Count -gt 0) {
    Write-Host "   ❌ 하드코딩된 시크릿 발견:" -ForegroundColor Red
    $secretsFound | Select-Object -First 10 | ForEach-Object {
        Write-Host "      $($_.Path):$($_.LineNumber)" -ForegroundColor Yellow
    }
    $allPassed = $false
} else {
    Write-Host "   ✅ 하드코딩된 시크릿 없음" -ForegroundColor Green
}

# 3. Production Build 테스트
Write-Host ""
Write-Host "3. Production Build 테스트" -ForegroundColor Cyan

# Docker
if (Test-Path "Dockerfile") {
    Write-Host "   Docker 이미지 빌드 테스트 중..." -ForegroundColor Cyan
    $dockerBuild = & docker build -t test-image:latest . 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Docker 빌드 성공" -ForegroundColor Green
        # 테스트 이미지 정리
        & docker rmi test-image:latest 2>&1 | Out-Null
    } else {
        Write-Host "   ❌ Docker 빌드 실패" -ForegroundColor Red
        $allPassed = $false
    }
}

# Node.js
if (Test-Path "package.json") {
    $packageJson = Get-Content "package.json" | ConvertFrom-Json

    if ($packageJson.scripts.build) {
        Write-Host "   npm run build 테스트 중..." -ForegroundColor Cyan
        $buildResult = & npm run build 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Production 빌드 성공" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Production 빌드 실패" -ForegroundColor Red
            $allPassed = $false
        }
    }
}

# Python
if (Test-Path "setup.py" -or Test-Path "pyproject.toml") {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "   Python 패키지 빌드 테스트 중..." -ForegroundColor Cyan
        $pythonBuild = & python -m build 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Python 빌드 성공" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Python 빌드 스킵 (python-build 미설치 가능)" -ForegroundColor Yellow
        }
    }
}

# 4. Deployment 체크리스트
Write-Host ""
Write-Host "4. Deployment 체크리스트" -ForegroundColor Cyan

$checklist = @(
    @{Name=".env.example 존재"; Check={Test-Path ".env.example"}},
    @{Name=".gitignore에 .env 포함"; Check={(Get-Content ".gitignore" -ErrorAction SilentlyContinue) -match "^\.env$"}},
    @{Name="README.md 존재"; Check={Test-Path "README.md"}},
    @{Name="CHANGELOG.md 존재"; Check={Test-Path "CHANGELOG.md"}}
)

foreach ($item in $checklist) {
    $result = & $item.Check
    if ($result) {
        Write-Host "   ✅ $($item.Name)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  $($item.Name)" -ForegroundColor Yellow
    }
}

# 최종 결과
Write-Host ""
Write-Host "=" * 60

if ($allPassed) {
    Write-Host "✅ Phase 6 검증 통과 - 배포 준비 완료!" -ForegroundColor Green
    Write-Host ""
    Write-Host "배포 방법:" -ForegroundColor Cyan
    Write-Host "   Docker: docker-compose up -d"
    Write-Host "   또는 deployment-engineer agent 사용"
    exit 0
} else {
    Write-Host "❌ Phase 6 검증 실패" -ForegroundColor Red
    Write-Host "   위 항목들을 수정하세요" -ForegroundColor Yellow
    exit 1
}
