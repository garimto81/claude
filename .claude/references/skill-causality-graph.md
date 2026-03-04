# 스킬 인과관계 그래프 (CRITICAL - 절대 보존)

> **v23.0 기준** — Agent Teams 단일 패턴. Skill() 호출 0개. BKIT 에이전트 0개.

## 1. /auto 5-Tier Discovery + PDCA Orchestrator

```
                    ┌─────────────────────────────────────────────┐
                    │              /auto (v23.0)                  │
                    │      PDCA Orchestrator (직접 실행)           │
                    └─────────────────────────────────────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              ▼                         ▼                         ▼
     작업 인수 있음               작업 인수 없음                Options
     (Phase 0-4 실행)            (자율 발견 모드)              (전처리)
              │                         │                         │
              ▼                   ┌────┴────┐             ┌──────┴──────┐
     Phase 0-4 PDCA          Tier 2 URGENT              │ --gdocs     │
     (아래 상세)             Tier 3 WORK               │ --mockup    │
                             Tier 4 SUPPORT             │ --debate    │
                             Tier 5 AUTO                │ --research  │
                                  │                     │ --daily     │
                             ┌────┴────┐                │ --slack     │
                             │ /debug  │                │ --gmail     │
                             │ /issue  │                │ --jira      │
                             │ /commit │                │ --figma     │
                             │ /check  │                └─────────────┘
                             └─────────┘
```

## 2. Phase 0-4 PDCA 체인 (Agent Teams 패턴: TeamCreate → Task(team_name+name) → SendMessage → TeamDelete)

```
/auto "작업"
  │
  ├── Phase 0 INIT: 옵션 파싱 + TeamCreate + 복잡도 판단
  │   ├── 옵션: --skip-prd, --skip-analysis, --no-issue, --strict, --eco, --worktree
  │   ├── TeamCreate(team_name="pdca-{feature}")
  │   └── 복잡도 판단: 0-1 LIGHT / 2-3 STANDARD / 4-5 HEAVY
  │
  ├── Phase 1 PLAN: PRD → 사전 분석 → 계획+설계 수립 → 이슈 연동
  │   ├── Step 1.1: PRD → docs/00-prd/{feature}.prd.md
  │   ├── Step 1.2: explore(haiku) x2 병렬 — 문서+이슈 탐색
  │   ├── Step 1.3: 모드별 분기 (Graduated Plan Review)
  │   │   ├── LIGHT: planner(sonnet) + Lead Quality Gate
  │   │   ├── STANDARD: planner(opus) + Critic-Lite(opus, QG1-QG5, max 2회 수정)
  │   │   └── HEAVY: Planner-Critic Loop(opus, max 5회)
  │   ├── Step 1.4: 설계 통합 (STANDARD/HEAVY — Plan에 아키텍처 결정 포함)
  │   └── 산출물: docs/01-plan/{feature}.plan.md
  │
  ├── Phase 2 BUILD: 구현 → 코드 리뷰 → Architect Gate
  │   ├── Step 2.1: 구현
  │   │   ├── LIGHT: executor(opus) — 단일 실행, TDD 필수
  │   │   └── STANDARD/HEAVY: impl-manager(opus) — 5조건 자체 루프 (max 10회)
  │   ├── Step 2.2: code-reviewer(sonnet) — STANDARD/HEAVY 필수 (max 2회)
  │   └── Step 2.3: Architect Gate (READ-ONLY, MATCH_RATE + MISSING_ITEMS)
  │       ├── APPROVE (MATCH_RATE >= 90%) → 커밋 → Phase 3
  │       └── REJECT + DOMAIN → Domain-Smart Fix → 재검증 (max 2회)
  │
  ├── Phase 3 VERIFY: QA → E2E → 최종 Architect 판정
  │   ├── Step 3.1: QA Runner(sonnet) — 6종 검증 (lint, type, unit, integration, build, security)
  │   │   ├── LIGHT: 1회
  │   │   ├── STANDARD: max 3회 + Architect 진단 + Domain-Smart Fix
  │   │   └── HEAVY: max 5회 + Architect 진단 + Domain-Smart Fix
  │   ├── Step 3.2: E2E 검증 (STANDARD/HEAVY, Playwright/Cypress 존재 시)
  │   └── Step 3.3: Architect 최종 검증 (MATCH_RATE% + MISSING_ITEMS)
  │       ├── APPROVE (MATCH_RATE >= 90%) → 커밋 → Phase 4
  │       └── REJECT (MATCH_RATE < 90%) + MISSING_ITEMS
  │           → executor가 MISSING_ITEMS 기반 수정 → Architect 재검증
  │           → MATCH_RATE 정체 2회 연속 → 조기 종료
  │           → STANDARD max 3회, HEAVY max 5회
  │
  └── Phase 4 CLOSE: 보고서 + 커밋 + 팀 정리
      ├── writer teammate → docs/04-report/{feature}.report.md
      ├── 유의미 변경 커밋
      ├── 모든 teammate shutdown_request
      └── TeamDelete()
```

## 3. 인과관계 체인 (데이터 흐름)

```
planner → (plan.md)
  → impl-manager → (구현 코드)
    → code-reviewer → (리뷰 통과)
      → Architect Gate (MATCH_RATE% + MISSING_ITEMS)
        → [REJECT: Domain-Smart Fix → 재검증]
        → QA Runner (6종 검증)
          → Architect 최종 (MATCH_RATE% + MISSING_ITEMS)
            → [REJECT: MISSING_ITEMS → executor 수정 → 재검증 루프]
            → writer → 보고서 → TeamDelete
```

## 4. 에이전트 역할 매핑 (v23.0)

| 에이전트 | PDCA Phase | 역할 | 모델 |
|---------|:----------:|------|:----:|
| `planner` | Phase 1 PLAN | 계획 수립 (QG1-QG5 검증) | sonnet/opus |
| `critic` | Phase 1 PLAN | Planner-Critic Loop (HEAVY) | opus |
| `executor` / `impl-manager` | Phase 2 BUILD | 구현 (5조건 자체 루프) | opus |
| `code-reviewer` | Phase 2 BUILD | 코드 리뷰 (Vercel BP 동적 주입) | sonnet |
| `architect` | Phase 2-3 | READ-ONLY 검증 (MATCH_RATE + MISSING_ITEMS) | opus |
| `designer` | Phase 2 BUILD | UI/Component DOMAIN Fix | sonnet |
| `build-fixer` | Phase 2-3 | Build/Type DOMAIN Fix | sonnet |
| `security-reviewer` | Phase 2-3 | Security DOMAIN Fix | sonnet |
| `qa-tester` | Phase 3 VERIFY | QA Runner 6종 검증 | sonnet |
| `writer` | Phase 4 CLOSE | 완료 보고서 생성 | sonnet/opus |

**`/work`는 `/auto`로 통합 완료 (v19.0).** 별도 그래프 불필요.

**이 인과관계가 무너지면 `/auto`의 PDCA + Discovery 시스템 전체가 작동하지 않음**
