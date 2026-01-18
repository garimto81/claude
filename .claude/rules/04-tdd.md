---
title: TDD 규칙
impact: CRITICAL
section: tdd
---

# TDD 규칙

## 핵심 원칙

**테스트 먼저 작성 (Red → Green → Refactor)**

| 단계 | 설명 | 예상 결과 |
|------|------|----------|
| **Red** | 실패하는 테스트 먼저 작성 | 테스트 실패 |
| **Green** | 테스트 통과하는 최소 코드 작성 | 테스트 통과 |
| **Refactor** | 코드 개선 (테스트 유지) | 테스트 통과 |

## 잘못된 예

```python
# ❌ 구현 먼저 작성
def calculate_total(items):
    return sum(item.price for item in items)

# 테스트는 나중에...
```

## 올바른 예

```python
# ✅ 테스트 먼저 작성
def test_calculate_total_returns_sum():
    items = [Item(price=100), Item(price=200)]
    assert calculate_total(items) == 300

# 그 다음 구현
def calculate_total(items):
    return sum(item.price for item in items)
```

## TDD 워크플로우

```
1. 테스트 작성 (RED)
   └── pytest tests/test_feature.py -v
   └── 결과: FAILED

2. 최소 구현 (GREEN)
   └── pytest tests/test_feature.py -v
   └── 결과: PASSED

3. 리팩토링 (REFACTOR)
   └── 코드 개선
   └── pytest tests/test_feature.py -v
   └── 결과: PASSED (유지)
```

## 테스트 파일 명명

| 프레임워크 | 패턴 |
|-----------|------|
| pytest | `test_*.py` 또는 `*_test.py` |
| Jest | `*.test.ts` 또는 `*.spec.ts` |

## 강제 수단

- Hook: `session_init.py` (경고)
- 위반 시: TDD 미준수 경고 메시지
- 스킬: `/tdd` 커맨드로 강제 TDD 모드

## 관련 스킬

- `tdd-workflow`: TDD 워크플로우 자동화
- `/tdd`: TDD 강제 모드 진입
