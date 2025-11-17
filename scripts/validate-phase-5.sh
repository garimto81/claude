#!/bin/bash
# Phase 5 검증: E2E Testing & Security Audit
# Based on cc-sdd validation system (MIT License)
# Adapted for claude01 Phase 0-6 workflow

set -e

echo "🔍 Phase 5 검증 시작: E2E & Security Testing"

# E2E 테스트 확인
echo ""
echo "🎭 E2E 테스트 검증 중..."

E2E_EXISTS=false

# Playwright 프로젝트
if [ -f "playwright.config.ts" ] || [ -f "playwright.config.js" ]; then
  echo "   Playwright 설정 발견"
  E2E_EXISTS=true

  if [ -d "tests/e2e" ] || [ -d "e2e" ]; then
    echo "   ✅ E2E 테스트 파일 존재"

    # E2E 테스트 실행 (선택)
    if [ "$RUN_E2E" = "true" ]; then
      echo "   Running E2E tests..."
      if npx playwright test; then
        echo "   ✅ E2E 테스트 통과"
      else
        echo "   ❌ E2E 테스트 실패"
        exit 1
      fi
    else
      echo "   ⏭️  E2E 테스트 스킵 (RUN_E2E=true로 실행 가능)"
    fi
  else
    echo "   ⚠️  E2E 테스트 폴더 없음 (tests/e2e/ 또는 e2e/)"
  fi
fi

# Cypress 프로젝트
if [ -f "cypress.config.ts" ] || [ -f "cypress.config.js" ]; then
  echo "   Cypress 설정 발견"
  E2E_EXISTS=true

  if [ -d "cypress/e2e" ]; then
    echo "   ✅ E2E 테스트 파일 존재"
  else
    echo "   ⚠️  E2E 테스트 폴더 없음 (cypress/e2e/)"
  fi
fi

if [ "$E2E_EXISTS" = false ]; then
  echo "⚠️  E2E 테스트 프레임워크 미설정"
  echo "   Playwright 또는 Cypress 설정 권장"
fi

# Security Audit
echo ""
echo "🔒 보안 검증 중..."

# Node.js 프로젝트
if [ -f "package.json" ]; then
  echo "   Running npm audit..."
  if npm audit --production; then
    echo "   ✅ 보안 취약점 없음"
  else
    AUDIT_LEVEL=$(npm audit --json | grep -o '"high":[0-9]*' | cut -d':' -f2 || echo "0")
    CRITICAL=$(npm audit --json | grep -o '"critical":[0-9]*' | cut -d':' -f2 || echo "0")

    if [ "$CRITICAL" -gt 0 ]; then
      echo "   ❌ Critical 취약점 발견: $CRITICAL개"
      echo "   npm audit fix 실행 필요"
      exit 1
    elif [ "$AUDIT_LEVEL" -gt 0 ]; then
      echo "   ⚠️  High 취약점 발견: $AUDIT_LEVEL개"
      echo "   npm audit fix 권장"
    else
      echo "   ✅ Critical/High 취약점 없음"
    fi
  fi
fi

# Python 프로젝트
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
  if command -v pip-audit &> /dev/null; then
    echo "   Running pip-audit..."
    if pip-audit; then
      echo "   ✅ Python 보안 취약점 없음"
    else
      echo "   ⚠️  Python 취약점 발견 (pip-audit 출력 확인)"
    fi
  else
    echo "   ⏭️  pip-audit 미설치 (pip install pip-audit)"
  fi
fi

# 환경 변수 검증
echo ""
echo "🔑 환경 변수 검증 중..."

if [ -f ".env.example" ]; then
  echo "   ✅ .env.example 존재"
else
  echo "   ⚠️  .env.example 없음 (생성 권장)"
fi

# .env가 .gitignore에 있는지 확인
if [ -f ".gitignore" ] && grep -q "^\.env$" ".gitignore"; then
  echo "   ✅ .env가 .gitignore에 포함됨"
else
  echo "   ⚠️  .env를 .gitignore에 추가하세요"
fi

# 하드코딩된 시크릿 검사
echo ""
echo "🕵️  하드코딩된 시크릿 검사 중..."

if grep -r -E "(password|secret|api_key|token).*=.*['\"][^'\"]{10,}['\"]" src/ 2>/dev/null | grep -v ".test." | grep -v ".spec."; then
  echo "   ⚠️  하드코딩된 시크릿 가능성 발견 (확인 필요)"
else
  echo "   ✅ 하드코딩된 시크릿 없음"
fi

echo ""
echo "✅ Phase 5 검증 완료"
echo "   다음 단계: Phase 6 (Deployment)"
exit 0
