---
name: auto
description: >
  PDCA Orchestrator — automated multi-phase build-verify-close cycles with Agent Teams. Triggers on "auto", "/auto", "autopilot", "PDCA", "자동 실행". Use when the user requests automated workflows, multi-phase execution (Plan→Build→Verify→Close), or structured PDCA orchestration.
version: 25.2.0
triggers:
  keywords:
    - "/auto"
    - "auto"
    - "autopilot"
    - "/work"
    - "자동화"
    - "자동 실행"
auto_trigger: true
---

# /auto - PDCA Orchestrator (v25.2 — Progressive Disclosure)

> **핵심**: `/auto "작업"` = Phase 0-4 자동 진행. `/auto` 단독 = 자율 발견 모드.
> **Agent Teams 단일 패턴**: TeamCreate → Agent(subagent_type+name+description+team_name) → SendMessage → TeamDelete.
> **Progressive Disclosure (v25.2)**: Phase 진입 시 해당 reference만 로딩. 불필요한 컨텍스트 제거.
> **코드 블록/상세 prompt**: Phase별 `references/` 파일 참조.

---

## Phase 0→4 실행 흐름

```
  Phase 0             Phase 1           Phase 2              Phase 3          Phase 4
  INIT         ──→    PLAN       ──→    BUILD         ──→    VERIFY    ──→    CLOSE
  옵션 파싱            PRD 생성         Task Clustering      QA 사이클        보고서+메트릭
  Socratic Q(0.2)     사전 분석         구현 실행             E2E 검증         팀 정리
  Adaptive Rt(0.3)    계획+설계 수립    코드 리뷰             최종 판정         커밋
  팀 생성              |               Architect Gate
  복잡도 판단          |
  플러그인 감지        |
```

---

## Phase별 컨텍스트 로딩 (Progressive Disclosure)

각 Phase 진입 시 해당 reference만 Read 도구로 로딩한다. 불필요한 Phase 문서는 읽지 않는다.

| Phase | 진입 조건 | 로딩 대상 | 설명 |
|:-----:|----------|----------|------|
| 0 | `/auto` 트리거 | 이 파일 (SKILL.md) | 옵션 파싱, 팀 생성, 복잡도 판단 |
| 1 | Phase 0 완료 | `references/phase-1-plan.md` | PRD, 사전 분석, 계획+설계 |
| 2 | PlanContract 준비 | `references/phase-2-build.md` | 구현, 코드 리뷰, Architect Gate |
| 3 | BuildContract 준비 | `references/phase-3-verify.md` | QA 사이클, E2E, 최종 검증 |
| 4 | VerifyContract 준비 | `references/phase-4-close.md` | 보고서, 메트릭, 팀 정리 |

**공통 참조** (필요 시만):

| 참조 | 로딩 조건 | 내용 |
|------|----------|------|
| `references/common.md` | Agent 미인식, 팀 운영 이슈 시 | Contracts 스키마, Fallback 매핑, Agent Teams 규칙 |
| `references/options-handlers.md` | `--mockup`, `--anno`, `--critic` 등 옵션 사용 시 | 옵션별 상세 워크플로우 |
| `guidelines/image-analysis.md` | 이미지 분석 시 | Vision AI 가이드라인 |

---

## Contract-Based Phase Interface

Phase 간 자료 결합도(1단계)를 보장하는 표준화된 Contract. 상세 스키마: `references/common.md`

| Contract | 핵심 필드 | 역할 |
|----------|----------|------|
| **InitContract** | feature, mode, complexity_score, plugins[], options, team_name | Phase 0 결정 사항 |
| **PlanContract** | prd_path, plan_path, requirements[], affected_files[], acceptance_criteria[] | Plan 데이터 전달 |
| **BuildContract** | changed_files[], test_results, build_status, lint_status, review_verdict | 구현 결과 요약 |
| **VerifyContract** | qa_cycles, qa_final_status, e2e_status, architect_final_verdict, unresolved_issues[] | 검증 결과 요약 |

---

## 옵션 통합 테이블

### 흐름 제어

| 옵션 | 효과 |
|------|------|
| `--skip-prd` | Phase 1 PRD 스킵 |
| `--skip-analysis` | Phase 1 사전 분석 스킵 |
| `--no-issue` | 이슈 연동 스킵 |
| `--strict` | E2E 1회 실패 즉시 중단 |
| `--skip-e2e` | E2E 검증 전체 스킵 |
| `--dry-run` | Phase 0-1까지만 실행 |
| `--eco` / `--eco-2` / `--eco-3` | 비용 절감 ~30% / ~50% / ~70%(프로토타이핑 전용) |
| `--worktree` | feature worktree에서 작업 |
| `--interactive` | Phase 전환 시 사용자 확인 |

### 실행 옵션 (Step 2.0 처리)

| 옵션 | 효과 |
|------|------|
| `--mockup [파일]` / `--mockup-q` | 3-Tier 목업 / Quasar Minimal 목업 |
| `--gdocs` | Google Docs PRD 동기화 |
| `--critic` | 약점 분석 → 웹 리서치 → 솔루션 제안 |
| `--debate` | 3-AI 병렬 분석 합의 |
| `--research` | 코드베이스/외부 리서치 |
| `--daily` | 일일 대시보드 |
| `--slack <채널>` / `--gmail` | Slack/Gmail 분석 |
| `--con <page_id>` | Confluence 발행 |
| `--jira <cmd> <target>` | Jira 조회/분석 |
| `--figma <url> [connect\|rules\|capture\|auth]` | Figma 디자인 연동 |
| `--anno [파일]` | Screenshot→HTML→Annotation 워크플로우 |

> **CRITICAL**: 실행 옵션 사용 시 `references/options-handlers.md`를 반드시 Read한 후 처리. 미로딩 상태에서 실행 옵션 처리 금지.

---

## Phase 0: INIT (옵션 + 팀 + 복잡도)

### Step 0.1: Option Parsing (MANDATORY)

사용자 입력에서 옵션을 파싱한다. **실행 옵션** 감지 시:

1. **즉시** Read(`references/options-handlers.md`) 실행 — Phase 1 진입 전 필수
2. 해당 옵션의 상세 워크플로우를 확인한 후에만 처리
3. options-handlers.md에 정의되지 않은 방식으로 옵션을 처리하는 것은 **금지** (hallucination 방지)

실행 옵션 목록: `--mockup`, `--mockup-q`, `--anno`, `--critic`, `--debate`, `--research`, `--daily`, `--jira`, `--figma`, `--gdocs`, `--slack`, `--gmail`, `--con`

> 흐름 제어 옵션 (`--skip-prd`, `--eco` 등)은 인라인 처리. options-handlers.md 로딩 불필요.

### Step 0.2: Socratic Questioning (Ambiguity >= 0.5 시)

5차원(목적/범위/제약/우선순위/수용기준) 중 핵심 3개만 AskUserQuestion. Magic Word (`!quick`, `!just`, `!hotfix`) 시 스킵.

### Step 0.3: Adaptive Model Routing

| 분류 | 신호 | 기본 모델 |
|------|------|----------|
| Trivial | 파일 1개, 포맷/요약/오타 | Haiku 항상 |
| Standard | 파일 2-5개, 구현/리뷰 | Sonnet |
| Complex | 파일 5+개, refactor/debug/design | Opus |
| Critical | architect/system/migration | Opus 항상 |

`--eco` 결합 시: `references/model-routing-guide.md` 참조.

### eco 자동 선택 (opt-in)

`--auto-eco` 플래그 사용 시 Adaptive 분류 결과를 eco 레벨에 자동 매핑:

| adaptive_tier | 자동 eco 레벨 | 근거 |
|:------------:|:------------:|------|
| Trivial | --eco-3 | Haiku 충분 |
| Standard | --eco | 비용 최적화 |
| Complex | (없음) | 품질 우선 |
| Critical | (없음) | 품질 최우선 |

사용자 명시적 `--eco[-N]` 지정 시 자동 선택 오버라이드. `--no-eco` 시 자동 선택 비활성화.

### 팀 생성 (MANDATORY)

`TeamCreate(team_name="pdca-{feature}")`. 실패 시 `TeamDelete()` → 재시도 1회. 재실패 시 중단.

> 커스텀 에이전트 미인식 시 Fallback 매핑: `references/common.md`

### 복잡도 판단 (6점 만점)

| 점수 | 모드 | 특성 |
|:----:|:----:|------|
| 0-1 | LIGHT | 단일 실행, QA 1회, 최소 검증 |
| 2-3 | STANDARD | 자체 루프, QA 3회, 이중 검증 |
| 4-6 | HEAVY | Planner-Critic, QA 5회, 전체 검증 |

### EscalationContract (Phase 경계에서만 승격)

`build_failures >= 2` → LIGHT→STANDARD, `affected_files >= 5` → STANDARD/HEAVY, `qa_cycles > 3` → STANDARD→HEAVY, `architect_rejects >= 2` → 승격 없음+사용자 알림.

### Phase 0.4: Plugin Activation Scan

프로젝트 루트 파일 감지 → 플러그인 자동 활성화. 상세: `references/plugin-fusion-rules.md`

**Iron Laws (전 Phase 적용)**: (1) TDD: 실패 테스트 없이 코드 금지 (2) Debugging: Root cause 없이 수정 금지 (3) Verification: 증거 없이 완료 선언 금지

### 커밋 정책

| 트리거 | 커밋 메시지 패턴 |
|--------|----------------|
| Phase 2 Architect APPROVE | `feat({feature}): 구현 완료` |
| Phase 3 최종 검증 통과 | `fix({feature}): QA 수정사항 반영` |
| Phase 4 보고서 생성 | `docs(report): {feature} PDCA 완료 보고서` |
| 조기 종료 | `wip({feature}): 진행 중 변경사항 보존` |

---

## Phase 1: PLAN (PRD → 분석 → 계획+설계)

Step 1.0-1.5: Requirement Gathering → PRD → 사전 분석 → 계획 (Graduated Plan Review) → 설계+OOP Gate → 이슈 연동.
- LIGHT: planner + Lead Quality Gate. STANDARD: + Critic-Lite. HEAVY: Planner-Critic Loop (max 5회).
- Plan→Build Gate: 4개 필수 섹션 + OOP Scorecard PASS (STANDARD/HEAVY).
> 상세: `references/phase-1-plan.md`

---

## Phase 2: BUILD (구현 → 코드 리뷰 → Architect Gate)

Step 2.0-2.4: 옵션 처리 → 구현 (impl-manager 4조건) → Code Review → Architect Gate + Gap Analysis → Domain-Smart Fix.
- LIGHT: executor-high 단일. STANDARD/HEAVY: impl-manager 루프 (max 10회) + code-reviewer + Architect.
- Architect Gate: READ-ONLY + gap-detector (Match Rate >= 90%). 2회 REJECT → 사용자 알림.
> 상세: `references/phase-2-build.md`

---

## Phase 3: VERIFY (QA → E2E → 최종 판정)

Step 3.1-3.4: QA 사이클 → E2E → 최종 검증 → TDD 커버리지.
- QA: LIGHT 1회, STANDARD 3회, HEAVY 5회. FAIL → Systematic Debugging D0-D4.
- Phase 3↔4 루프 가드: 최대 3회. 초과 시 커밋 + 미해결 이슈 보고.
> 상세: `references/phase-3-verify.md`

---

## Phase 4: CLOSE (보고서 + 팀 정리)

Step 4.0-4.2: Deployment Check → 보고서 (8개 메트릭) → 커밋 + Safe Cleanup.
- LIGHT: writer(haiku). STANDARD/HEAVY: executor-high(opus). TeamDelete 필수.
> 상세: `references/phase-4-close.md`

---

## 복잡도 기반 모드 분기

| Phase | LIGHT (0-1) | STANDARD (2-3) | HEAVY (4-6) |
|-------|:-----------:|:--------------:|:-----------:|
| 0 INIT | TeamCreate | TeamCreate | TeamCreate |
| 1 PLAN | PRD + planner | + Critic-Lite + 설계 | + Planner-Critic Loop |
| 2 BUILD | executor 단일 (TDD) | impl-manager + code-reviewer + Architect | + 병렬 가능 |
| 3 VERIFY | QA 1회 + Architect | QA 3회 + E2E + 진단 루프 | QA 5회 + E2E + 진단 루프 |
| 4 CLOSE | writer (haiku) | executor-high (opus) | executor-high (opus) |

## 자율 발견 모드 + 세션 관리

- `/auto` 단독: Tier 0 CONTEXT → 1 EXPLICIT → 2 URGENT → 3 WORK → 4 SUPPORT → 5 AUTONOMOUS. 상세: `references/common.md`
- `/auto status` (상태) / `/auto stop` (중지+TeamDelete) / `/auto resume` (재개). 완전 frozen 시: `python C:\claude\.claude\scripts\emergency_stop.py`

## 금지 사항

- 옵션 실패 시 조용히 스킵 / Architect 검증 없이 완료 선언 / 증거 없이 "완료됨" 주장
- 테스트 삭제로 문제 해결 / TeamDelete 없이 세션 종료 / architect로 파일 생성 (READ-ONLY)
- Skill() 호출 금지 (Agent Teams 단일 패턴) / Team-Lead `shutdown_response` 호출 금지
