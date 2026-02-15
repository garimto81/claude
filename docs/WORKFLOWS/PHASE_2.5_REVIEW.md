# Phase 2.5: Professional Review Workflow

테스트 통과 후, 버전 태깅 전 수행하는 전문 리뷰 프로세스.

---

## 워크플로우 위치

```
Phase 2 (Tests Pass) → Phase 2.5 (Reviews) → Phase 3 (Version Tag)
```

**목적**: 코드 품질, 디자인 일관성, 보안 취약점을 프로덕션 전에 검증

---

## 3가지 리뷰 유형

### 1. Pragmatic Code Review (권장)

**명령어**: `/pragmatic-code-review`

**Agent**: pragmatic-code-review (Opus 모델)

**특징**:
- 7-tier 계층적 분석
- Anthropic 자체 개발 프로세스 기반
- 높은 정확도 (Opus 모델 사용)

**7-Tier 분석 구조**:

| Tier | 분석 대상 | 확인 사항 |
|------|----------|----------|
| 1 | Architecture | 시스템 설계, 모듈 경계 |
| 2 | API Design | 인터페이스 일관성, 계약 |
| 3 | Logic | 알고리즘 정확성, 엣지 케이스 |
| 4 | Error Handling | 예외 처리, 복구 전략 |
| 5 | Performance | 병목, 메모리, 복잡도 |
| 6 | Security | OWASP Top 10, 인젝션 |
| 7 | Dependencies | 버전, 취약점, 라이선스 |

**사용 시점**:
- ✅ main 브랜치 머지 전
- ✅ 중요 기능 PR
- ✅ 프로덕션 릴리스 전

**출력 예시**:
```markdown
## Code Review Summary

### Tier 1: Architecture ✅
- 모듈 분리 적절
- 의존성 방향 올바름

### Tier 3: Logic ⚠️
- `auth/login.py:45` - 비밀번호 비교 시 timing attack 가능
  - 권장: `secrets.compare_digest()` 사용

### Tier 6: Security ❌
- `api/user.py:23` - SQL injection 취약점
  - 현재: `f"SELECT * FROM users WHERE id = {user_id}"`
  - 수정: parameterized query 사용
```

---

### 2. Design Review (UI 변경시)

**명령어**: `/design-review`

**Agent**: design-review (Sonnet 모델)

**특징**:
- Playwright CLI 통합 (실제 환경 테스트)
- WCAG 2.1 AA 접근성 준수 검증
- 반응형 디자인 검증 (Desktop/Tablet/Mobile)

**7-Phase 프로세스**:

| Phase | 검증 항목 |
|-------|----------|
| 1 | Interaction | 버튼, 폼, 네비게이션 동작 |
| 2 | Visual | 색상, 타이포그래피, 간격 |
| 3 | Responsive | 브레이크포인트별 레이아웃 |
| 4 | Accessibility | 스크린 리더, 키보드 내비게이션 |
| 5 | Performance | 렌더링 속도, 애니메이션 |
| 6 | Consistency | 디자인 시스템 준수 |
| 7 | Console | JavaScript 에러, 경고 |

**사용 시점**:
- ✅ UI/UX 컴포넌트 변경
- ✅ 반응형 디자인 업데이트
- ✅ 접근성 개선 작업

**스크린샷 캡처**:
```
Desktop (1920x1080) → Tablet (768x1024) → Mobile (375x667)
```

---

### 3. Security Review (보안 민감 코드)

**명령어**: `/security-review`

**Agent**: security-auditor

**특징**:
- OWASP Top 10 집중 분석
- 높은 신뢰도 탐지 (>80%)
- 오탐(False Positive) 최소화

**검증 항목**:

| OWASP | 취약점 | 검증 방법 |
|-------|-------|----------|
| A01 | Broken Access Control | 권한 체크 누락 |
| A02 | Cryptographic Failures | 약한 암호화, 평문 저장 |
| A03 | Injection | SQL, Command, XSS |
| A04 | Insecure Design | 비즈니스 로직 결함 |
| A05 | Security Misconfiguration | 기본값, 디버그 모드 |
| A06 | Vulnerable Components | 알려진 CVE |
| A07 | Auth Failures | 세션, 토큰 관리 |
| A08 | Data Integrity | 서명, 검증 누락 |
| A09 | Logging Failures | 감사 로그 부재 |
| A10 | SSRF | 서버 사이드 요청 위조 |

**사용 시점**:
- ✅ 인증/인가 코드
- ✅ 결제 처리
- ✅ 사용자 데이터 처리
- ✅ 외부 API 통합

---

## 리뷰 선택 가이드

```
                    코드 변경
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      UI 변경?      보안 관련?     일반 코드?
          │             │             │
          ▼             ▼             ▼
   /design-review  /security-review  /pragmatic-code-review
```

**복합 변경 시**: 여러 리뷰 순차 실행

```bash
# 예: 로그인 UI 변경
/security-review      # 1. 보안 먼저
/design-review        # 2. UI 검증
/pragmatic-code-review # 3. 전체 코드 품질
```

---

## 리뷰 결과 처리

### 심각도 분류

| 심각도 | 기호 | 조치 |
|-------|------|------|
| Critical | ❌ | 즉시 수정 필수, 머지 차단 |
| Warning | ⚠️ | 수정 권장, 머지 가능 |
| Info | ℹ️ | 참고 사항 |
| Pass | ✅ | 문제 없음 |

### 수정 워크플로우

```
리뷰 결과 ❌ 발견
    │
    ▼
Phase 1로 복귀 (해당 파일 수정)
    │
    ▼
Phase 2 재실행 (테스트)
    │
    ▼
Phase 2.5 재실행 (리뷰)
    │
    ▼
모든 ✅ → Phase 3 진행
```

---

## Validation

```bash
# 리뷰 완료 확인 (커밋 메시지 기반)
git log -1 --grep="review"

# 또는 PR에 리뷰 코멘트 존재 확인
gh pr view --comments
```

---

## 자동화 통합

`.github/workflows/validate-phase.yml`에서 자동 실행:

```yaml
- name: Run Code Review
  if: contains(github.event.pull_request.labels.*.name, 'phase-2.5')
  run: |
    # 자동 리뷰 트리거
    echo "Phase 2.5 review required"
```
