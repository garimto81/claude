#!/bin/bash
# Phase 2 검증: 테스트 실행 및 커버리지 확인
# Based on cc-sdd validation system (MIT License)
# Adapted for claude01 Phase 0-6 workflow

set -e

echo "🔍 Phase 2 검증 시작: 테스트 실행 및 커버리지"

# 테스트 파일 존재 확인
if [ ! -d "tests" ]; then
  echo "❌ Phase 2 검증 실패: tests/ 폴더 없음"
  echo "   테스트를 먼저 작성하세요"
  exit 1
fi

# Python 프로젝트 검증
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
  echo "🐍 Python 프로젝트 감지"

  # pytest 설치 확인
  if ! command -v pytest &> /dev/null; then
    echo "❌ pytest가 설치되지 않음: pip install pytest pytest-cov"
    exit 1
  fi

  # 테스트 실행
  echo "🧪 Running tests..."
  if pytest tests/ -v --cov=src --cov-report=term-missing; then
    echo "✅ 모든 테스트 통과"
  else
    echo "❌ 테스트 실패"
    exit 1
  fi

  # 커버리지 확인 (최소 70%)
  COVERAGE=$(pytest tests/ --cov=src --cov-report=term-missing | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
  if [ -n "$COVERAGE" ] && [ "$COVERAGE" -ge 70 ]; then
    echo "✅ 테스트 커버리지: ${COVERAGE}% (>= 70%)"
  else
    echo "⚠️  테스트 커버리지: ${COVERAGE}% (권장: 70% 이상)"
  fi
fi

# Node.js 프로젝트 검증
if [ -f "package.json" ] && grep -q '"test"' package.json; then
  echo "📦 Node.js 프로젝트 감지"

  # npm 설치 확인
  if ! command -v npm &> /dev/null; then
    echo "❌ npm이 설치되지 않음"
    exit 1
  fi

  # 테스트 실행
  echo "🧪 Running tests..."
  if npm test; then
    echo "✅ 모든 테스트 통과"
  else
    echo "❌ 테스트 실패"
    exit 1
  fi
fi

# Go 프로젝트 검증
if [ -f "go.mod" ]; then
  echo "🔷 Go 프로젝트 감지"

  # 테스트 실행
  echo "🧪 Running tests..."
  if go test ./... -v; then
    echo "✅ 모든 테스트 통과"
  else
    echo "❌ 테스트 실패"
    exit 1
  fi
fi

echo ""
echo "✅ Phase 2 검증 통과: 모든 테스트 성공"
echo "   다음 단계: Phase 3 (Semantic Versioning)"
exit 0
