---
title: 빌드 및 테스트 규칙
impact: HIGH
section: build
---

# 빌드 및 테스트 규칙

## Python 명령

```powershell
# 린트
ruff check src/ --fix

# 개별 테스트 (권장)
pytest tests/test_specific.py -v

# 전체 테스트 (주의: background 필수)
# pytest tests/ -v --cov=src
```

## E2E 테스트 (Playwright)

```powershell
# 전체 E2E
npx playwright test

# 개별 테스트
npx playwright test tests/e2e/auth.spec.ts
```

## 안전 규칙

| 명령 | 제한 | 권장 |
|------|------|------|
| `pytest tests/ -v --cov` | 120초 초과 시 크래시 | 개별 파일 실행 |
| 전체 테스트 실행 | 메인 Context 소모 | background 모드 |

## 잘못된 예

```powershell
# ❌ 전체 테스트를 메인에서 실행 (크래시 위험)
pytest tests/ -v --cov=src

# ❌ 타임아웃 없이 장시간 테스트
npx playwright test --timeout=0
```

## 올바른 예

```powershell
# ✅ 개별 테스트 실행
pytest tests/test_auth.py -v

# ✅ 특정 테스트 함수만 실행
pytest tests/test_auth.py::test_login -v

# ✅ E2E는 특정 파일만
npx playwright test tests/e2e/login.spec.ts
```

## 테스트 우선순위

| 순위 | 테스트 유형 | 실행 방법 |
|:----:|------------|----------|
| 1 | 단위 테스트 | `pytest tests/unit/` |
| 2 | 통합 테스트 | `pytest tests/integration/` |
| 3 | E2E 테스트 | `npx playwright test` |

## 커버리지 확인

```powershell
# HTML 리포트 생성
pytest tests/ -v --cov=src --cov-report=html

# 결과 확인
start htmlcov/index.html
```

## 상세 문서

`docs/BUILD_TEST.md`
