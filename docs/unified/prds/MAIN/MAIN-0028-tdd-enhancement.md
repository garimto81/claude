# PRD-0028: TDD 워크플로우 강화

**Version**: 1.0.0 | **Date**: 2025-12-06 | **Status**: Draft
**Parent**: [PRD-0025](./MAIN-0025-master-workflow-optimization.md)
**Priority**: P1

---

## 1. 목적

Anthropic Best Practices를 적용하여 TDD 워크플로우를 강화하고, **Red Phase 강제 검증**, **Mock 사용 제한**, **Extended Thinking 통합**을 구현합니다.

---

## 2. 현재 vs 목표

| 항목 | Before | After |
|------|--------|-------|
| 테스트 우선 강제 | 가이드만 | `validate-red-phase.ps1` 자동 검증 |
| 실패 확인 | 언급만 | MUST FAIL 검증 필수 |
| Mock 방지 | 없음 | Hook으로 30% 초과 시 경고 |
| Extended Thinking | 미사용 | complexity별 ultrathink 권장 |

---

## 3. Red Phase 강제 검증

### 3.1 validate-red-phase.ps1

```powershell
# 검증 로직
1. 테스트 파일만 존재하는지 확인 (구현 파일 없음)
2. pytest 실행 → MUST FAIL
3. 실패 원인 확인 (ImportError, NameError 등)
4. 통과 시 → GREEN phase 진행
   실패 시 → 테스트 수정 필요
```

### 3.2 TDD Phase Gate

```
RED Phase:
1. 테스트 파일 작성 (tests/test_*.py)
2. pytest 실행 → 반드시 FAIL
3. 커밋: "test: Add XXX test (RED) 🔴"

GREEN Phase:
1. 최소 구현 (src/*.py)
2. pytest 실행 → PASS
3. 커밋: "feat: Implement XXX (GREEN) 🟢"

REFACTOR Phase:
1. 코드 개선 (테스트 변경 없음)
2. pytest 실행 → 여전히 PASS
3. 커밋: "refactor: Improve XXX ♻️"
```

---

## 4. Mock 사용 제한

### 4.1 prevent-excessive-mocks.py (Hook)

```python
# Pre-commit hook
허용: 외부 API (requests., boto3., psycopg2.)
금지: 내부 함수 Mock (src.* 패턴)
경고: Mock 비율 > 30%
```

### 4.2 허용/금지 예시

```python
# ✅ 허용: 외부 API
@patch('requests.get')
def test_fetch_user(mock_get): ...

# ❌ 금지: 내부 구현
@patch('src.auth.verify_password')  # 직접 구현해야 함
def test_login(mock_verify): ...
```

---

## 5. Extended Thinking 통합

| 복잡도 | Mode | 예시 |
|--------|------|------|
| 단순 CRUD | (none) | `login(email, password)` |
| 비즈니스 로직 | `think` | Multi-step checkout |
| 상태 머신 | `think hard` | Order state transitions |
| 분산 시스템 | `ultrathink` | Cache consistency |

### 프롬프트 예시

```
/tdd distributed-cache --ultrathink

"Ultrathink this TDD scenario:
- 3-node cluster with eventual consistency
- Network partition handling
- Race condition edge cases"
```

---

## 6. TDD 자동화 스크립트

### 6.1 tdd-auto-cycle.ps1

```powershell
# Write → Test → Adjust 자동 반복 (최대 5회)
for iteration in 1..5:
    1. pytest 실행
    2. 실패 분석
    3. Claude 자동 수정
    4. 재테스트

    if all_pass: break

if iteration == 5 && failed:
    → /issue-failed → 수동 개입
```

---

## 7. 구현 Task

- [ ] Task 1: `validate-red-phase.ps1` 생성
- [ ] Task 2: `prevent-excessive-mocks.py` Hook 생성
- [ ] Task 3: `tdd-auto-cycle.ps1` 생성
- [ ] Task 4: `/tdd` 커맨드 업데이트 (Anthropic Best Practices)
- [ ] Task 5: `tdd-workflow` Skill 통합 (PRD-0027)

---

## 8. 성공 지표

| 지표 | 현재 | 목표 |
|------|------|------|
| Red Phase 준수율 | - | 95% |
| Mock 비율 | ~40% | < 30% |
| ultrathink 활용 | 0% | 복잡 시나리오 100% |

---

**Dependencies**: PRD-0027 (`tdd-workflow` Skill)
**Next**: PRD-0029 (GitHub Actions)

