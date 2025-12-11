# 서브레포 분석 보고서

**Version**: 1.0.0 | **작성일**: 2025-12-10

---

## 1. 분석 개요

Claude Code 전역 워크플로우(`claude-code-config`)에서 활용 가능한 커맨드, 에이전트, 패턴을 추출하기 위해 12개 서브레포를 분석했습니다.

| 항목 | 수량 |
|------|------|
| 분석 서브레포 | 12개 |
| 발견 커맨드 | 18개 |
| 발견 에이전트 | 37개 |
| 전역 활용 가능 패턴 | 8개 |

---

## 2. 서브레포 현황

### 2.1 전체 목록

| 서브레포 | 도메인 | 커맨드 | 에이전트 | Block Agent |
|----------|--------|--------|----------|-------------|
| `qwen_hand_analysis` | 포커 VOD 분석 | 6개 | - | - |
| `sso-system` | SSO 인증 | 5개 | - | - |
| `wsoptv` | 스트리밍 플랫폼 | 1개 | 6개 | ✅ |
| `archive-statistics` | NAS 모니터링 | 2개 | 4개 | ✅ |
| `db_architecture` | DB 설계 | 1개 | - | ✅ (문서 기반) |
| `ggp_ojt_v2` | OJT 교육 시스템 | - | 8개 | ✅ |
| `classic-isekai` | 웹소설 제작 | 3개 | 11개 | 파이프라인 |
| `field-uploader` | - | - | - | - |
| `shorts-generator` | - | - | - | - |
| `side_monitor` | - | - | - | - |
| `archive-analyzer` | 아카이브 분석 | - | - | - |
| `archive-mam` | - | - | - | - |

### 2.2 주요 서브레포 상세

#### qwen_hand_analysis
- **특징**: 병렬 작업 관리 커맨드 다수
- **핵심 커맨드**: `parallel-check`, `parallel-branch`, `workflow-v2`
- **전역 활용**: ⭐⭐⭐ (병렬 작업 패턴)

#### wsoptv
- **특징**: Block Agent System 완성도 높음
- **구조**: Orchestrator → 5개 Domain Agent
- **핵심 커맨드**: `work-wsoptv` (E2E 자동 검증)
- **전역 활용**: ⭐⭐⭐ (Block Agent 템플릿)

#### archive-statistics
- **특징**: 도메인 에이전트 문서화 상세
- **구조**: Orchestrator → 3개 Domain Agent
- **핵심 커맨드**: `work-block`, `work-auto`
- **전역 활용**: ⭐⭐⭐ (디버깅/이슈 문서화 패턴)

#### ggp_ojt_v2
- **특징**: AI 엔진 관리 패턴
- **구조**: Orchestrator → 7개 Feature Agent
- **전역 활용**: ⭐⭐ (AI Fallback, Auth 패턴)

#### classic-isekai
- **특징**: 웹소설 제작 파이프라인 (10단계)
- **구조**: Orchestrator → 10개 Pipeline Agent
- **전역 활용**: ⭐ (PM Reflect 이중 검증)

---

## 3. 발견된 아키텍처 패턴

### 3.1 Block Agent System

**출처**: wsoptv, archive-statistics, ggp_ojt_v2

```
┌─────────────────────────────────────────────────────────────┐
│                    Block Agent Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Level 0: Orchestrator                                        │
│      │    - 라우팅, 에러 핸들링, 글로벌 설정                    │
│      │                                                        │
│      ├─────────────────────────────────────────────────────┐  │
│      │                                                     │  │
│      ▼                                                     ▼  │
│  Level 1: Domain Agent                              Domain Agent
│      │    - 도메인 규칙                                       │
│      │    - Block 관리                                        │
│      │                                                        │
│      ├────────────────────────────────────────────────────┐   │
│      │                                                    │   │
│      ▼                                                    ▼   │
│  Level 2: Block (AGENT_RULES.md)                      Block   │
│           - DO/DON'T 규칙                                     │
│           - 파일 범위                                         │
│           - 테스트 정책                                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 병렬 작업 충돌 검사

**출처**: qwen_hand_analysis

```
작업 A, B, C
    │
    ▼
┌─────────────────────────────────┐
│ 파일 범위 분석                    │
│ - 각 작업의 수정 파일 목록        │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ 충돌 매트릭스 생성                │
│ ┌──────┬────┬────┬────┬─────┐  │
│ │ 파일 │ A  │ B  │ C  │충돌 │  │
│ ├──────┼────┼────┼────┼─────┤  │
│ │ x.ts │ W  │ R  │ -  │ -   │  │
│ │ y.ts │ W  │ W  │ -  │ ⚠️  │  │
│ └──────┴────┴────┴────┴─────┘  │
└───────────────┬─────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
충돌 없음                충돌 있음
→ 병렬 실행              → 순차 실행
```

### 3.3 브랜치 기반 병렬 개발

**출처**: qwen_hand_analysis

```
main
 │
 ├──▶ feature/issue-N-frontend (Agent 1)
 │
 ├──▶ feature/issue-N-backend (Agent 2)
 │
 └──▶ feature/issue-N-infra (Agent 3)
      │
      └──▶ 각자 작업 후 PR → 머지
```

### 3.4 E2E 자동 검증 (Zero-Interrupt)

**출처**: wsoptv

```
┌─────────────────────────────────────────────────────────────┐
│                    E2E 자동 검증 흐름                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Step 1: 타입 체크 + 린트                                     │
│      ↓                                                        │
│  Step 2: 단위 테스트 (Vitest)                                 │
│      ↓                                                        │
│  Step 3: E2E 테스트 (Playwright)                              │
│      │   └─ Chromium, Firefox, WebKit 병렬                   │
│      ↓                                                        │
│  Step 4: 시각적 회귀 테스트                                   │
│      ↓                                                        │
│  Step 5: 성능 벤치마크 (Web Vitals)                           │
│      ↓                                                        │
│  Step 6: 실패 시 자동 수정 (최대 3회)                         │
│      ↓                                                        │
│  ✅ 사용자 최종 검증                                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.5 문서 계층 기반 개발

**출처**: db_architecture

```
PRD (요구사항)
    ↓
Architecture (아키텍처)
    ↓
LLD (상세 설계)
    ↓
Implementation (구현)
    ↓
Documentation Sync (문서 동기화)
```

### 3.6 AI 엔진 Fallback

**출처**: ggp_ojt_v2

```
Local AI (vLLM Qwen3-4B)
    ↓ 실패 시
Chrome AI (Gemini Nano)
    ↓ 미지원 시
WebLLM (브라우저 내 LLM)
    ↓ 실패 시
에러 표시 (수동 입력 유도)
```

### 3.7 PM Reflect (이중 검증)

**출처**: classic-isekai

```
Primary PM → Score A
    ↓
Secondary PM → Score B (독립 평가)
    ↓
비교 분석
    │
    ├─ diff ≤ 0.5 → accept
    ├─ diff ≤ 1.5 (both ≥ 8.0) → accept
    ├─ diff > 1.5 → human review
    └─ both < 7.0 → rewrite
```

### 3.8 Known Issues 문서화

**출처**: archive-statistics

```markdown
### Issue #N: 제목

**증상**: 사용자가 관찰한 문제

**원인**: 분석 결과

**해결**: 적용한 수정사항

**파일**: 수정된 파일 위치
```

---

## 4. 전역 활용 제안

### 4.1 전역 커맨드 승격 (우선순위 순)

| 순위 | 커맨드 | 출처 | 용도 | 구현 복잡도 |
|------|--------|------|------|-------------|
| ⭐⭐⭐ | `/parallel-check` | qwen_hand_analysis | 병렬 작업 전 충돌 검사 | 중 |
| ⭐⭐⭐ | `/parallel-branch` | qwen_hand_analysis | 브랜치 기반 병렬 개발 | 중 |
| ⭐⭐⭐ | `/work-block` | archive-statistics | Block Agent 워크플로우 | 고 |
| ⭐⭐ | `/work-docs` | db_architecture | 문서 기반 개발 | 중 |
| ⭐ | `/pm-reflect` | classic-isekai | 이중 검증 | 저 |

### 4.2 전역 에이전트 템플릿

| 템플릿 | 출처 | 용도 | 구현 복잡도 |
|--------|------|------|-------------|
| `orchestrator-template.md` | wsoptv, ggp_ojt_v2 | 모든 프로젝트 오케스트레이터 | 저 |
| `domain-agent-template.md` | archive-statistics | 도메인 에이전트 표준 | 저 |
| `auth-agent-template.md` | ggp_ojt_v2 | 인증 필요 프로젝트 | 중 |
| `ai-agent-template.md` | ggp_ojt_v2 | AI 통합 프로젝트 | 중 |

### 4.3 전역 스킬 추가

| 스킬 | 출처 | 용도 |
|------|------|------|
| `debugging-workflow` | archive-statistics | 디버깅 플래그/로그 패턴 표준화 |
| `issue-resolution` | archive-statistics | Known Issues 문서화 자동화 |
| `parallel-agent-orchestration` | qwen_hand_analysis | 병렬 에이전트 조율 |

---

## 5. 구현 로드맵

### Phase 1: 템플릿 (즉시)

1. `docs/templates/orchestrator-template.md` 작성
2. `docs/templates/domain-agent-template.md` 작성
3. 기존 `/parallel` 커맨드에 충돌 검사 통합

### Phase 2: 커맨드 (단기)

1. `/parallel-check` 독립 커맨드 생성
2. `/parallel-branch` 커맨드 생성
3. `/work-block` 범용화 (프로젝트 감지 자동화)

### Phase 3: 스킬 (중기)

1. `debugging-workflow` 스킬 추가
2. `issue-resolution` 스킬 추가
3. 기존 스킬과 통합

---

## 6. 참조

### 분석 대상 파일

| 서브레포 | 주요 파일 |
|----------|----------|
| qwen_hand_analysis | `.claude/commands/parallel-check.md`, `parallel-branch.md`, `workflow-v2.md` |
| wsoptv | `.claude/agents/orchestrator.md`, `work-wsoptv.md` |
| archive-statistics | `.claude/agents/progress-domain.md`, `scanner-domain.md` |
| ggp_ojt_v2 | `.claude/agents/orchestrator.md`, `auth-agent.md`, `ai-agent.md` |
| db_architecture | `.claude/commands/work-db.md` |
| classic-isekai | `.claude/agents/00-orchestrator.md` |

### 관련 문서

- [CLAUDE.md](../CLAUDE.md) - 전역 지침
- [.claude/commands/](../.claude/commands/) - 기존 커맨드
- [.claude/skills/](../.claude/skills/) - 기존 스킬

---

**작성**: Claude Code | **검토 필요**: 구현 우선순위 결정
