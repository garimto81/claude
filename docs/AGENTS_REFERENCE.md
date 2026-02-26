# Agent 참조 가이드

**버전**: 9.1.0 | **업데이트**: 2026-02-25

> **v9.0.0**: OMC 플러그인 완전 제거 (2026-02-18). 42개 로컬 에이전트로 전환 완료.
> 모든 에이전트는 `.claude/agents/`에서 직접 로드됩니다.

---

## 에이전트 구조 (42개)

```
  .claude/agents/ (42개 로컬 에이전트)
  ├── 실행 계층 (3개)     executor, executor-high, executor-low
  ├── 설계 계층 (6개)     architect, architect-medium, architect-low, planner, analyst, critic
  ├── 탐색 계층 (5개)     explore, explore-medium, explore-high, researcher, researcher-low
  ├── 품질 계층 (11개)    code-reviewer, qa-tester, security-reviewer, build-fixer, tdd-guide, gap-detector (+low/-high 변형)
  ├── UI 계층 (4개)       designer, designer-high, designer-low, frontend-dev
  ├── 도메인 계층 (11개)  ai-engineer, cloud-architect, database-specialist, data-specialist,
  │                       devops-engineer, github-engineer, claude-expert, catalog-engineer,
  │                       scientist, scientist-high, scientist-low
  └── 특수 목적 (2개)     vision, writer
```

**모델 티어**: sonnet = 표준/복잡, haiku = 빠른/단순

---

## 1. 실행 계층 (Executor Tier)

| 에이전트 | 모델 | 설명 | 사용 시점 |
|---------|------|------|----------|
| `executor` | sonnet | 구현 작업 실행 전문가 | 표준 코드 변경, /auto PDCA |
| `executor-high` | sonnet | 복잡한 다중 파일 작업 | 4+ 파일 변경, 아키텍처 수준 구현 |
| `executor-low` | haiku | 단순 단일 파일 작업 | 1-2줄 수정, 사소한 변경 |

**호출 예시:**
```python
Task(subagent_type="executor", model="sonnet", ...)
Task(subagent_type="executor-high", model="sonnet", ...)
Task(subagent_type="executor-low", model="haiku", ...)
```

---

## 2. 설계 계층 (Architecture Tier)

| 에이전트 | 모델 | 설명 | 사용 시점 |
|---------|------|------|----------|
| `architect` | sonnet | 전략적 아키텍처 (READ-ONLY) | 완료 검증, 설계 리뷰 |
| `architect-medium` | sonnet | 중간 복잡도 아키텍처 | 디버깅, 중간 설계 |
| `architect-low` | haiku | 빠른 코드 조회 | 단순 함수 설명, 빠른 참조 |
| `planner` | sonnet | 전략적 작업 계획 수립 | 복잡한 기능 계획 수립 |
| `analyst` | sonnet | 요구사항 분석 컨설턴트 | 구현 전 요구사항 분석 |
| `critic` | sonnet | 계획 검토 전문가 | 작업 계획 비판적 검토 |

---

## 3. 탐색 계층 (Explore Tier)

| 에이전트 | 모델 | 설명 | 사용 시점 |
|---------|------|------|----------|
| `explore` | haiku | 빠른 코드베이스 탐색 | 파일/패턴 검색, 3회 이하 쿼리 |
| `explore-medium` | sonnet | 중간 탐색 (추론 포함) | 보통 탐색, 다중 위치 검색 |
| `explore-high` | sonnet | 심층 아키텍처 탐색 | 시스템 전체 이해, 복잡한 분석 |
| `researcher` | sonnet | 외부 문서/참조 조사 | 웹 검색, API 문서 조사 |
| `researcher-low` | haiku | 빠른 문서 조회 | 단순 문서 참조 |

---

## 4. 품질 계층 (Quality Tier)

### 코드 리뷰

| 에이전트 | 모델 | 설명 |
|---------|------|------|
| `code-reviewer` | sonnet | 품질/보안/유지보수성 코드 리뷰. 심각도 등급 제공 |
| `code-reviewer-low` | haiku | 소규모 변경 빠른 리뷰 |

### QA 테스트

| 에이전트 | 모델 | 설명 |
|---------|------|------|
| `qa-tester` | sonnet | 6종 QA 실행 및 결과 보고 |
| `qa-tester-high` | sonnet | 종합 프로덕션 수준 QA |

### 보안 리뷰

| 에이전트 | 모델 | 설명 |
|---------|------|------|
| `security-reviewer` | sonnet | OWASP Top 10, 시크릿 스캐닝. 사용자 입력/인증/API 코드에 PROACTIVE 사용 |
| `security-reviewer-low` | haiku | 소규모 변경 빠른 보안 스캔 |

### 빌드 수정

| 에이전트 | 모델 | 설명 |
|---------|------|------|
| `build-fixer` | sonnet | 빌드/TypeScript 오류 수정. 최소 diff, 아키텍처 변경 없음 |
| `build-fixer-low` | haiku | 단순 타입 오류, 단일 라인 수정 |

### TDD & 분석

| 에이전트 | 모델 | 설명 |
|---------|------|------|
| `tdd-guide` | sonnet | TDD 전문가. 테스트 먼저 작성 강제. 80%+ 커버리지 |
| `tdd-guide-low` | haiku | 단순 테스트 케이스 제안 |
| `gap-detector` | sonnet | 설계 문서와 구현 간 Gap 정량 분석. Match Rate(%) 계산 |

---

## 5. UI 계층 (Design Tier)

| 에이전트 | 모델 | 설명 | 사용 시점 |
|---------|------|------|----------|
| `designer` | sonnet | UI/UX 개발 전문가 | 표준 컴포넌트, 인터페이스 |
| `designer-high` | sonnet | 복잡한 UI 아키텍처 및 디자인 시스템 | 복잡한 UI 아키텍처 |
| `designer-low` | haiku | 단순 스타일링, 마이너 UI 수정 | CSS 조정, 소규모 변경 |
| `frontend-dev` | sonnet | 프론트엔드 개발. React/Next.js 성능 최적화 | 전체 프론트엔드 작업 |

> **plugin 연동**: `frontend-design` 플러그인이 designer 에이전트의 Aesthetic Guidelines 제공

---

## 6. 도메인 계층 (Domain Tier)

### 인프라 & 플랫폼

| 에이전트 | 모델 | 전문 분야 |
|---------|------|----------|
| `devops-engineer` | sonnet | CI/CD, K8s, Terraform, 트러블슈팅 |
| `cloud-architect` | sonnet | AWS/Azure/GCP, 네트워킹, 비용 최적화 |
| `database-specialist` | sonnet | DB 설계, 쿼리 최적화, Supabase, RLS |
| `github-engineer` | haiku | GitHub Actions, 브랜치 전략, PR 워크플로우 |

### AI & 데이터

| 에이전트 | 모델 | 전문 분야 |
|---------|------|----------|
| `ai-engineer` | sonnet | LLM 앱, RAG, 벡터 DB, 프롬프트 엔지니어링 |
| `data-specialist` | sonnet | 데이터 분석, ETL, ML 파이프라인 |
| `scientist` | sonnet | 데이터 분석 및 리서치 실행 (python_repl) |
| `scientist-high` | sonnet | 복잡한 리서치, 가설 검증, ML (python_repl) |
| `scientist-low` | haiku | 빠른 데이터 검사, 단순 통계 (python_repl) |

### 특화 도구

| 에이전트 | 모델 | 전문 분야 |
|---------|------|----------|
| `claude-expert` | sonnet | Claude Code, MCP, 에이전트, 프롬프트 최적화 |
| `catalog-engineer` | sonnet | WSOPTV 카탈로그 생성, Block F/G 전담 |

---

## 7. 특수 목적 (Special Tier)

| 에이전트 | 모델 | 설명 |
|---------|------|------|
| `vision` | sonnet | 이미지, PDF, 다이어그램 시각 분석 |
| `writer` | haiku | 기술 문서 작성 (README, API docs, 주석) |

---

## 빠른 선택 가이드

```
  질문: 어떤 에이전트를 써야 하나?
  │
  ├─ 코드 작성/수정이 필요한가?
  │   ├─ 단순 (1-2줄, 1파일) → executor-low (haiku)
  │   ├─ 표준 (여러 줄, 1-3파일) → executor (sonnet)
  │   └─ 복잡 (4+ 파일, 아키텍처) → executor-high (sonnet)
  │
  ├─ 코드를 탐색/검색해야 하나?
  │   ├─ 빠른 패턴 검색 → explore (haiku)
  │   ├─ 다중 위치 탐색 → explore-medium (sonnet)
  │   └─ 시스템 전체 이해 → explore-high (sonnet)
  │
  ├─ 검토/검증이 필요한가?
  │   ├─ 아키텍처 검증 → architect (sonnet)
  │   ├─ 코드 품질 → code-reviewer (sonnet)
  │   ├─ 보안 취약점 → security-reviewer (sonnet)
  │   └─ QA 실행 → qa-tester (sonnet)
  │
  ├─ UI/프론트엔드 작업?
  │   ├─ 단순 스타일 → designer-low (haiku)
  │   ├─ 컴포넌트 → designer (sonnet)
  │   └─ 전체 프론트엔드 → frontend-dev (sonnet)
  │
  └─ 특화 도메인?
      ├─ 클라우드/DevOps → cloud-architect / devops-engineer
      ├─ 데이터/AI → data-specialist / ai-engineer / scientist
      ├─ DB → database-specialist
      └─ 문서화 → writer (haiku)
```

---

## 에이전트 티어 요약

| 티어 | 에이전트 수 | 모델 분포 |
|------|------------|----------|
| 실행 | 3개 | 2 sonnet + 1 haiku |
| 설계 | 6개 | 5 sonnet + 1 haiku |
| 탐색 | 5개 | 3 sonnet + 2 haiku |
| 품질 | 10개 | 7 sonnet + 3 haiku |
| UI | 4개 | 3 sonnet + 1 haiku |
| 도메인 | 11개 | 10 sonnet + 1 haiku |
| 특수 | 3개 | 2 sonnet + 1 haiku |
| **합계** | **42개** | **32 sonnet + 10 haiku** |

---

## MCP 서버

| MCP | 용도 |
|-----|------|
| `sequential-thinking` | 복잡한 문제 단계별 추론 |

설정 위치: `C:\Users\AidenKim\.claude.json`

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 9.0.0 | 2026-02-19 | OMC 플러그인 제거 반영, 42개 로컬 에이전트 전면 재작성 |
| 8.0.0 | 2026-02-15 | 모델 정보 동기화 |
| 7.0.0 | 2026-02-05 | 스킬 개수 47개 반영 |
