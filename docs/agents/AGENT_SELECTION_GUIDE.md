# Agent Selection Guide

올바른 Agent 선택을 위한 성공률 데이터 및 최적화 가이드.

---

## Agent 성공률 데이터

실제 사용 데이터 기반 (`.agent-quality-v2.jsonl` 분석):

| Agent | 성공률 | 평균 시간 | 권장 용도 |
|-------|-------|----------|----------|
| test-automator | 100% | 12s | 단위 테스트, 통합 테스트 |
| code-reviewer | 100% | 18s | 코드 리뷰 |
| security-auditor | 100% | 25s | 보안 스캔 |
| context7-engineer | 100% | 8s | 외부 라이브러리 문서 검증 |
| debugger | 81% | 15s | 버그 수정 |
| playwright-engineer | 63% | 45s | E2E 테스트 |
| typescript-expert | 75% | 20s | TypeScript 타입 정의 |

---

## Task-Agent 매핑

### Quick Reference

| Task 유형 | ✅ 사용 | ❌ 피하기 | 이유 |
|----------|--------|----------|------|
| 단위 테스트 | test-automator | playwright-engineer | 과도한 리소스 |
| E2E 테스트 | playwright-engineer | test-automator | 타임아웃 |
| 버그 수정 | debugger | typescript-expert | 더 빠름 |
| 코드 리뷰 | code-reviewer | 수동 리뷰 | 일관성 |
| 보안 스캔 | security-auditor | 수동 감사 | 누락 방지 |
| 문서 검증 | context7-engineer | 생략 | 위험 |
| 타입 정의 | typescript-expert | debugger | 전문성 |

---

## Phase별 Agent 선택

### Phase 0: Planning & Research

```python
# 병렬 실행 가능
Task("context7-engineer", "Research React 18 new features")
Task("seq-engineer", "Analyze requirements and dependencies")
```

| Agent | 용도 |
|-------|------|
| context7-engineer | 외부 라이브러리 문서 검증 |
| seq-engineer | 순차적 요구사항 분석 |
| exa-search-specialist | 웹 검색 기반 리서치 |

### Phase 1: Implementation

```python
# 순차 실행 권장 (의존성)
Task("debugger", "Fix authentication bug in login.py")
Task("test-automator", "Write unit tests for login.py")
```

| Agent | 용도 |
|-------|------|
| debugger | 버그 수정, 에러 해결 |
| typescript-expert | TypeScript 타입 정의 |
| backend-architect | API 설계 |
| frontend-developer | UI 컴포넌트 |

### Phase 2: Testing

```python
# 병렬 실행 가능
Task("test-automator", "Run unit tests with 80% coverage")
Task("playwright-engineer", "Run E2E tests for login flow")
```

| Agent | 용도 |
|-------|------|
| test-automator | 단위/통합 테스트 |
| playwright-engineer | E2E 테스트, 브라우저 자동화 |

### Phase 2.5: Review

```python
# 순차 실행 (리뷰 결과 반영)
Task("security-auditor", "OWASP Top 10 security scan")
Task("code-reviewer", "Full code review")
```

| Agent | 용도 |
|-------|------|
| code-reviewer | 코드 품질 리뷰 |
| security-auditor | 보안 취약점 스캔 |
| design-review | UI/UX 리뷰 (Playwright CLI) |

### Phase 5: E2E & Security

```python
# 병렬 실행 가능
Task("playwright-engineer", "Full E2E test suite")
Task("security-auditor", "Final security audit")
Task("performance-engineer", "Load testing 1000 users")
```

### Phase 6: Deployment

```python
Task("deployment-engineer", "Deploy to production with Docker")
```

| Agent | 용도 |
|-------|------|
| deployment-engineer | CI/CD, 배포 |
| cloud-architect | 클라우드 인프라 |
| devops-troubleshooter | 배포 문제 해결 |

---

## 성공률 향상 팁

### Integration Tests: Mock Data 제공

**문제**: Integration test에서 mock data 없이 요청 시 25% 성공률

**해결**: 명시적 mock data 제공 시 75% 성공률

```python
# ❌ Bad (25% 성공률)
Task("test-automator", "Write integration tests for user API")

# ✅ Good (75% 성공률)
Task("test-automator", """
Write integration tests for user API with mock data:
{
  "user": {"id": 1, "name": "Test User", "email": "test@example.com"},
  "token": "mock-jwt-token-12345",
  "expected_response": {"status": 200, "message": "Success"}
}
""")
```

### E2E Tests: 명확한 흐름 정의

```python
# ❌ Bad
Task("playwright-engineer", "Test the login page")

# ✅ Good
Task("playwright-engineer", """
Test login flow:
1. Navigate to /login
2. Enter email: test@example.com
3. Enter password: password123
4. Click submit button
5. Verify redirect to /dashboard
6. Verify welcome message contains username
""")
```

### Debugging: 에러 컨텍스트 제공

```python
# ❌ Bad
Task("debugger", "Fix the bug")

# ✅ Good
Task("debugger", """
Fix TypeError in auth/login.py:45
Error: 'NoneType' object has no attribute 'get'
Context: Occurs when user.profile is None
Stack trace attached: ...
""")
```

---

## 병렬 실행 패턴

### 최대 병렬 실행 (독립 작업)

```python
# Phase 0: 4개 병렬
Task("context7-engineer", "React 18 docs"),
Task("seq-engineer", "Analyze requirements"),
Task("typescript-expert", "Define types"),
Task("exa-search-specialist", "Research competitors")

# Phase 2: 3개 병렬
Task("test-automator", "Unit tests"),
Task("playwright-engineer", "E2E tests"),
Task("security-auditor", "Security scan")
```

### 순차 실행 (의존성)

```python
# 구현 → 테스트 → 리뷰
Task("debugger", "Implement feature")  # 먼저 완료
# ... 완료 대기 ...
Task("test-automator", "Write tests")   # 구현 후 실행
# ... 완료 대기 ...
Task("code-reviewer", "Review code")    # 테스트 후 실행
```

**시간 절약**: 병렬 실행 시 평균 64% 시간 단축

---

## Agent 사용량 추적

### 수동 기록 (Agent 사용 후)

```bash
python .claude/track.py <agent> "<description>" <pass/fail> \
  --duration <seconds> \
  --phase "Phase X"
```

### 예시

```bash
# 성공
python .claude/track.py debugger "Fix TypeError in auth.py" pass \
  --duration 15.2 --phase "Phase 1"

# 실패
python .claude/track.py test-automator "Integration tests" fail \
  --duration 45.0 --error "3 tests failed" --phase "Phase 2"
```

### 분석

```bash
# 전체 요약
python .claude/evolution/scripts/analyze_quality2.py --summary

# 특정 Agent 분석
python .claude/evolution/scripts/analyze_quality2.py --agent debugger

# 트렌드 확인
python .claude/evolution/scripts/analyze_quality2.py --trend
```

---

## 토큰 최적화

| 전략 | 토큰 사용 | 절감률 |
|------|----------|--------|
| 전체 Agent 로드 | ~40,000 | - |
| Plugin 시스템 | ~15,000 | 62% |
| Phase별 로드 | ~3,000 | 92% |
| 필요시 로드 | ~1,500 | 96% |

**권장**: Claude가 Phase 컨텍스트에 따라 자동 선택 (수동 개입 불필요)
