# Agent 완전 참조 가이드

**목적**: 33개 Subagent 활용법 및 병렬 실행 전략

**버전**: 1.0.0 | **업데이트**: 2025-11-11

---

## 📊 전체 Agent 목록 (33개)

### 1. 핵심 개발 (8개)

| Agent | 용도 | 병렬 실행 | Phase |
|-------|------|----------|-------|
| `python-pro` | Python 고급 구현 (decorators, async) | ✅ | 1 |
| `frontend-developer` | React/Next.js 컴포넌트 | ✅ | 1 |
| `backend-architect` | API 설계, DB 스키마 | ✅ | 1 |
| `fullstack-developer` | 풀스택 구현 | ⚠️ | 1 |
| `typescript-expert` | TypeScript 타입 시스템 | ✅ | 1 |
| `mobile-developer` | React Native/Flutter | ✅ | 1 |
| `graphql-architect` | GraphQL 스키마/리졸버 | ✅ | 1 |
| `supabase-engineer` | Supabase 서버 아키텍처 | ✅ | 1 |

### 2. 품질 보증 (5개)

| Agent | 용도 | 병렬 실행 | Phase |
|-------|------|----------|-------|
| `test-automator` | 단위/통합 테스트 작성 | ✅ | 2 |
| `playwright-engineer` | E2E 테스트 자동화 | ✅ | 2, 5 |
| `security-auditor` | 보안 취약점 스캔 | ✅ | 5 |
| `code-reviewer` | 코드 리뷰 (품질, 보안) | ✅ | 1 후 |
| `performance-engineer` | 성능 최적화, 병목 분석 | ✅ | 5 |

### 3. 인프라/DevOps (4개)

| Agent | 용도 | 병렬 실행 | Phase |
|-------|------|----------|-------|
| `deployment-engineer` | CI/CD, Docker, K8s | ❌ | 6 |
| `devops-troubleshooter` | 프로덕션 이슈 디버깅 | ❌ | 5 |
| `cloud-architect` | AWS/GCP/Azure 설계 | ✅ | 0, 1 |
| `github-engineer` | Git 워크플로우, PR | ✅ | 4 |

### 4. 데이터 (4개)

| Agent | 용도 | 병렬 실행 | Phase |
|-------|------|----------|-------|
| `database-architect` | DB 스키마 설계 | ✅ | 1 |
| `database-optimizer` | 쿼리 최적화, 인덱스 | ✅ | 1, 5 |
| `data-engineer` | ETL 파이프라인, 데이터 레이크 | ✅ | 1 |
| `data-scientist` | SQL/BigQuery 분석 | ✅ | 분석 |

### 5. 전문 분야 (5개)

| Agent | 용도 | 병렬 실행 | Phase |
|-------|------|----------|-------|
| `ai-engineer` | LLM/RAG 시스템 설계 | ✅ | 1 |
| `ml-engineer` | ML 파이프라인, 모델 배포 | ✅ | 1 |
| `UI_UX-Designer` | UI/UX 디자인 | ✅ | 0, 1 |
| `prompt-engineer` | 프롬프트 최적화 | ✅ | 분석 |

### 6. 지원/계획 (7개)

| Agent | 용도 | 병렬 실행 | Phase |
|-------|------|----------|-------|
| `seq-engineer` | 순차적 사고, 복잡한 분석 | ✅ | 0 |
| `context7-engineer` | 최신 문서 검증 (필수) | ✅ | 0, 1 |
| `debugger` | 디버깅, 원인 분석 | ❌ | 문제 발생 시 |
| `taskmanager-planner` | 작업 계획, 마일스톤 | ✅ | 0.5 |
| `task-decomposition-expert` | 작업 분해 | ✅ | 0.5 |
| `architect-reviewer` | 아키텍처 리뷰 | ✅ | 0, 1 |
| `exa-search-specialist` | 웹 검색 (기술 조사) | ✅ | 0 |
| `context-manager` | 컨텍스트 관리 | ✅ | 전체 |

**범례**:
- ✅ 병렬 가능 - 독립적 작업, 다른 Agent와 동시 실행 가능
- ❌ 순차 필수 - 다른 작업 결과에 의존
- ⚠️ 조건부 - 상황에 따라 다름

---

## 🚀 병렬 실행 패턴

### 패턴 1: Phase 0 병렬 분석
```
seq-engineer (PRD 구조화)
  ∥
context7-engineer (기술 스택 검증)
  ∥
architect-reviewer (아키텍처 초안 리뷰)
  ∥
exa-search-specialist (기술 조사)
```

**효과**: Phase 0 시간 75% 단축 (60분 → 15분)

### 패턴 2: Phase 1 병렬 구현
```
frontend-developer (UI 컴포넌트)
  ∥
backend-architect (API 엔드포인트)
  ∥
database-architect (DB 스키마)
```

**주의**: database-architect 완료 후 backend-architect가 스키마 참조

### 패턴 3: Phase 2 병렬 테스트
```
test-automator (단위 테스트)
  ∥
playwright-engineer (E2E 테스트)
  ∥
security-auditor (보안 스캔)
```

**효과**: Phase 2 시간 60% 단축 (90분 → 36분)

### 패턴 4: Phase 5 병렬 검증
```
playwright-engineer (E2E 최종 검증)
  ∥
security-auditor (보안 점검)
  ∥
performance-engineer (성능 테스트)
  ∥
database-optimizer (쿼리 최적화)
```

**효과**: Phase 5 시간 70% 단축 (120분 → 36분)

---

## 📋 시나리오별 Agent 조합

### 시나리오 1: 새 기능 개발 (풀스택)

**Phase 0: 계획** (병렬)
```
seq-engineer + context7-engineer + architect-reviewer
```

**Phase 1: 구현** (병렬)
```
frontend-developer (UI)
  ∥
backend-architect (API)
  ∥
database-architect (DB)

→ 순차: code-reviewer (전체 리뷰)
```

**Phase 2: 테스트** (병렬)
```
test-automator (단위)
  ∥
playwright-engineer (E2E)
  ∥
security-auditor (보안)
```

**Phase 5: 검증** (병렬)
```
playwright-engineer (필수)
  ∥
security-auditor
  ∥
performance-engineer
```

**총 시간**: ~180분 → **60분** (병렬 실행 시)

---

### 시나리오 2: 버그 수정

**Phase 0: 분석** (순차)
```
debugger (원인 분석)
→ context7-engineer (관련 기술 검증)
```

**Phase 1: 수정** (단일)
```
python-pro / frontend-developer (수정)
→ code-reviewer (리뷰)
```

**Phase 2 & 5: 검증** (병렬)
```
test-automator (회귀 테스트)
  ∥
playwright-engineer (E2E)
```

**총 시간**: ~45분 → **20분** (병렬 실행 시)

---

### 시나리오 3: 성능 최적화

**Phase 0: 분석** (병렬)
```
seq-engineer (병목 분석)
  ∥
performance-engineer (프로파일링)
  ∥
database-optimizer (쿼리 분석)
```

**Phase 1: 최적화** (병렬)
```
performance-engineer (코드 최적화)
  ∥
database-optimizer (인덱스 추가)
```

**Phase 2: 검증** (병렬)
```
test-automator (성능 테스트)
  ∥
playwright-engineer (실제 환경 E2E)
```

**총 시간**: ~120분 → **40분** (병렬 실행 시)

---

### 시나리오 4: 데이터 파이프라인 구축

**Phase 0: 설계** (병렬)
```
seq-engineer (파이프라인 설계)
  ∥
data-engineer (ETL 아키텍처)
  ∥
database-architect (데이터 웨어하우스 스키마)
```

**Phase 1: 구현** (병렬)
```
data-engineer (ETL 구현)
  ∥
database-architect (스키마 생성)
  ∥
backend-architect (API)
```

**Phase 2: 검증** (병렬)
```
test-automator (데이터 품질 테스트)
  ∥
data-scientist (데이터 검증)
```

---

### 시나리오 5: AI/ML 기능 개발

**Phase 0: 설계** (병렬)
```
seq-engineer (기능 분석)
  ∥
ai-engineer (RAG 시스템 설계)
  ∥
context7-engineer (LLM 라이브러리 검증)
```

**Phase 1: 구현** (병렬)
```
ai-engineer (RAG 파이프라인)
  ∥
backend-architect (API)
  ∥
database-architect (벡터 DB)
```

**Phase 2: 테스트** (병렬)
```
test-automator (단위)
  ∥
ai-engineer (프롬프트 테스트)
  ∥
playwright-engineer (E2E)
```

---

## 🎯 병렬 실행 원칙

### ✅ 병렬 가능한 경우
1. **독립적 작업**: 서로 다른 파일/모듈 작업
2. **같은 Phase**: 동일 Phase 내 여러 작업
3. **Read-only 분석**: 여러 분석 작업 동시 수행

### ❌ 순차 필수 경우
1. **의존성 존재**: A의 출력이 B의 입력
2. **Phase 간**: Phase 1 완료 후 Phase 2 시작
3. **공유 리소스**: 같은 파일 동시 수정

### 실행 명령 예시
```bash
# ✅ 병렬 (올바름)
Task(agent: frontend-developer) + Task(agent: backend-architect)

# ❌ 순차 (불필요)
Task(agent: frontend-developer) → 완료 대기 → Task(agent: backend-architect)

# ✅ 조건부 병렬 (스마트)
Task(agent: database-architect) → Task(agent: backend-architect + frontend-developer)
```

---

## 📊 성능 개선 효과

| 시나리오 | 순차 실행 | 병렬 실행 | 절감 |
|---------|----------|----------|------|
| 새 기능 개발 | 180분 | 60분 | 67% |
| 버그 수정 | 45분 | 20분 | 56% |
| 성능 최적화 | 120분 | 40분 | 67% |
| 데이터 파이프라인 | 150분 | 50분 | 67% |
| AI/ML 기능 | 200분 | 70분 | 65% |

**평균 절감**: **64%**

---

## 🛠️ Agent 선택 가이드

### 언어/프레임워크별

| 기술 | 추천 Agent |
|------|-----------|
| Python | `python-pro` |
| TypeScript | `typescript-expert` |
| React/Next.js | `frontend-developer` |
| Node.js API | `backend-architect` |
| React Native | `mobile-developer` |
| GraphQL | `graphql-architect` |
| Supabase | `supabase-engineer` |

### 작업 유형별

| 작업 | 추천 Agent |
|------|-----------|
| 요구사항 분석 | `seq-engineer` |
| 기술 검증 | `context7-engineer` (필수) |
| API 설계 | `backend-architect` |
| DB 설계 | `database-architect` |
| 테스트 | `test-automator` + `playwright-engineer` |
| 보안 | `security-auditor` |
| 성능 | `performance-engineer` |
| 배포 | `deployment-engineer` |
| API 테스트 | `backend-architect` + `graphql-architect` + `security-auditor` |
| 로그 분석 | `devops-troubleshooter` + `debugger` + `performance-engineer` |

---

## 💡 베스트 프랙티스

### 1. Phase 0부터 병렬 시작
```
✅ seq-engineer + context7-engineer + architect-reviewer
❌ seq-engineer → context7-engineer → architect-reviewer
```

### 2. 의존성 최소화
```
✅ frontend와 backend 독립 개발 → 통합
❌ backend 완료 대기 → frontend 시작
```

### 3. Phase 2에서 최대 병렬화
```
✅ test-automator + playwright-engineer + security-auditor
```

### 4. Phase 5 필수 검증
```
✅ playwright-engineer (필수) + security-auditor + performance-engineer
```

---

## 📚 참조

- [CLAUDE.md](../CLAUDE.md) - 핵심 워크플로우
- [Phase 0-6 가이드](../CLAUDE.md#phase-0-6)
- Agent 파일: [.claude/agents/](../.claude/agents/)

---

**관리**: 바이브 코더
**업데이트**: 2025-11-11
**버전**: 1.0.0
