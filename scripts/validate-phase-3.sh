#!/bin/bash
# Phase 3 검증: Semantic Versioning 및 CHANGELOG
# Based on cc-sdd validation system (MIT License)
# Adapted for claude01 Phase 0-6 workflow

set -e

VERSION=$1

# 사용법 체크
if [ -z "$VERSION" ]; then
  echo "❌ 사용법: $0 <VERSION>"
  echo "   예시: $0 v1.2.0"
  exit 1
fi

echo "🔍 Phase 3 검증 시작: Semantic Versioning ($VERSION)"

# 버전 형식 검증 (vX.Y.Z)
if ! [[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "❌ 버전 형식 오류: $VERSION"
  echo "   올바른 형식: vMAJOR.MINOR.PATCH (예: v1.2.0)"
  exit 1
fi

echo "✅ 버전 형식 올바름: $VERSION"

# 모든 테스트 통과 확인
echo ""
echo "🧪 테스트 재실행 중..."

# Python 프로젝트
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
  if ! pytest tests/ -v > /dev/null 2>&1; then
    echo "❌ 테스트 실패: Phase 2를 먼저 통과하세요"
    exit 1
  fi
  echo "✅ Python 테스트 통과"
fi

# Node.js 프로젝트
if [ -f "package.json" ] && grep -q '"test"' package.json; then
  if ! npm test > /dev/null 2>&1; then
    echo "❌ 테스트 실패: Phase 2를 먼저 통과하세요"
    exit 1
  fi
  echo "✅ Node.js 테스트 통과"
fi

# Go 프로젝트
if [ -f "go.mod" ]; then
  if ! go test ./... > /dev/null 2>&1; then
    echo "❌ 테스트 실패: Phase 2를 먼저 통과하세요"
    exit 1
  fi
  echo "✅ Go 테스트 통과"
fi

# CHANGELOG.md 확인
echo ""
if [ ! -f "CHANGELOG.md" ]; then
  echo "⚠️  CHANGELOG.md 없음"
  echo "   생성 권장:"
  echo "   echo '# Changelog\n\n## [${VERSION#v}] - $(date +%Y-%m-%d)\n### Added\n- Initial release' > CHANGELOG.md"
else
  # CHANGELOG에 현재 버전 존재 확인
  VERSION_NUM="${VERSION#v}"  # v1.2.0 → 1.2.0
  if grep -q "\[${VERSION_NUM}\]" CHANGELOG.md; then
    echo "✅ CHANGELOG.md 업데이트됨 (버전 ${VERSION_NUM} 포함)"
  else
    echo "⚠️  CHANGELOG.md에 버전 ${VERSION_NUM} 없음"
    echo "   업데이트 권장:"
    echo "   ## [${VERSION_NUM}] - $(date +%Y-%m-%d)"
    echo "   ### Added/Changed/Fixed"
  fi
fi

# Uncommitted changes 확인
echo ""
if [ -n "$(git status --porcelain)" ]; then
  echo "⚠️  커밋되지 않은 변경사항 존재"
  echo "   모든 변경사항을 커밋하세요"
  git status --short
else
  echo "✅ 모든 변경사항 커밋됨"
fi

# Git tag 생성 권장
echo ""
if git rev-parse "$VERSION" >/dev/null 2>&1; then
  echo "✅ Git tag $VERSION 이미 존재"
else
  echo "📌 Git tag 생성 권장:"
  echo "   git tag -a $VERSION -m \"Release $VERSION\""
  echo "   git push origin $VERSION"
fi

echo ""
echo "✅ Phase 3 검증 완료"
echo "   다음 단계: Phase 4 (Git + Auto PR)"
exit 0
