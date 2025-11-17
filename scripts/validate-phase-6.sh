#!/bin/bash
# Phase 6 검증: Pre-Deployment Checklist
# Based on cc-sdd validation system (MIT License)
# Adapted for claude01 Phase 0-6 workflow

set -e

echo "🔍 Phase 6 검증 시작: Deployment Readiness"

# .env.example 확인
echo ""
echo "📋 환경 변수 문서화 확인..."

if [ -f ".env.example" ]; then
  echo "   ✅ .env.example 존재"

  # .env.example의 변수 개수
  ENV_COUNT=$(grep -c "^[A-Z_]*=" ".env.example" || echo "0")
  echo "   환경 변수: ${ENV_COUNT}개 문서화됨"

  if [ "$ENV_COUNT" -eq 0 ]; then
    echo "   ⚠️  .env.example이 비어있음"
  fi
else
  echo "   ❌ .env.example 없음"
  echo "   생성 필요: 모든 환경 변수를 예시 값과 함께 문서화"
  exit 1
fi

# 하드코딩된 시크릿 최종 확인
echo ""
echo "🔒 시크릿 하드코딩 최종 검사..."

SECRETS_FOUND=false

if grep -r -E "(password|secret|api_key|token|key).*=.*['\"][a-zA-Z0-9]{20,}['\"]" src/ 2>/dev/null | grep -v ".test." | grep -v ".spec." | grep -v ".example"; then
  echo "   ❌ 하드코딩된 시크릿 발견"
  SECRETS_FOUND=true
fi

if grep -r -E "postgres://.*:.*@" src/ 2>/dev/null | grep -v ".test." | grep -v ".example"; then
  echo "   ❌ 하드코딩된 데이터베이스 URL 발견"
  SECRETS_FOUND=true
fi

if [ "$SECRETS_FOUND" = true ]; then
  echo "   모든 시크릿을 환경 변수로 이동하세요"
  exit 1
else
  echo "   ✅ 하드코딩된 시크릿 없음"
fi

# Production Build 테스트
echo ""
echo "🏗️  Production Build 검증 중..."

BUILD_SUCCESS=false

# Node.js 프로젝트
if [ -f "package.json" ] && grep -q '"build"' package.json; then
  echo "   Node.js 빌드 실행 중..."
  if npm run build; then
    echo "   ✅ Production build 성공"
    BUILD_SUCCESS=true
  else
    echo "   ❌ Production build 실패"
    exit 1
  fi
fi

# Python 프로젝트 (optional)
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
  echo "   Python 프로젝트 감지 (빌드 검증 스킵)"
  BUILD_SUCCESS=true
fi

# Go 프로젝트
if [ -f "go.mod" ]; then
  echo "   Go 빌드 실행 중..."
  if go build -o build/app ./...; then
    echo "   ✅ Go build 성공"
    BUILD_SUCCESS=true
  else
    echo "   ❌ Go build 실패"
    exit 1
  fi
fi

if [ "$BUILD_SUCCESS" = false ]; then
  echo "   ⚠️  빌드 스크립트 없음 (package.json의 \"build\" 또는 Makefile)"
fi

# Docker 이미지 빌드 테스트 (선택)
echo ""
echo "🐳 Docker 검증 중..."

if [ -f "Dockerfile" ]; then
  echo "   ✅ Dockerfile 존재"

  if [ "$BUILD_DOCKER" = "true" ]; then
    echo "   Docker 이미지 빌드 중..."
    if docker build -t app-test:latest .; then
      echo "   ✅ Docker build 성공"
    else
      echo "   ❌ Docker build 실패"
      exit 1
    fi
  else
    echo "   ⏭️  Docker build 스킵 (BUILD_DOCKER=true로 실행 가능)"
  fi
else
  echo "   ⏭️  Dockerfile 없음 (Docker 배포 시 필요)"
fi

# Deployment Checklist
echo ""
echo "✅ Deployment Checklist:"
echo "   [ ] All Phase 5 checks passed"
echo "   [ ] .env.example documented"
echo "   [ ] No hardcoded secrets"
echo "   [ ] Production build succeeds"
echo "   [ ] Database migrations tested"
echo "   [ ] Rollback plan documented"
echo "   [ ] Monitoring/alerting configured"

echo ""
echo "✅ Phase 6 검증 완료: Deployment 준비됨"
echo "   🚀 배포를 진행하세요"
exit 0
