# PRD: OMC Feature Integration into /auto v22.0

> **Version**: 1.0.0 | **Date**: 2026-02-18 | **Status**: DRAFT
> **Feature**: `omc-feature-integration` | **Complexity**: HEAVY (4/5)

---

## 1. Background / Problem Statement

### 1.1 Current State

`/auto` v21.0 Agent Teams 전환으로 다음을 달성:
- Skill() 호출 4→0 (완전 제거)
- State 파일 의존 0 (Stop Hook 충돌 해소)
- Agent Teams 단일 패턴 (Context overflow 근본 해결)

그러나 전환 과정에서 OMC의 핵심 장점 다수가 누락됨:

### 1.2 Identified Gaps (이전 검토 결과)

| # | 심각도 | 누락 기능 | 영향 |
|:-:|:------:|----------|------|
| 1 | **HIGH** | 키워드 하이재킹 | `autopilot`/`ultrawork`/`ralph` 고유 동작 상실 |
| 2 | **HIGH** | 도메인 인식 에이전트 선택 | 32개 전문 에이전트 중 7종만 활용 |
| 3 | **HIGH** | 인과관계 그래프 outdated | v20.1 패턴 참조 (Skill() 호출 표기) |
| 4 | **MEDIUM** | Continuation Enforcement | Phase 5 TeamDelete 전 5점 체크리스트 없음 |
| 5 | **MEDIUM** | Broad Request Detection | 단순 작업도 전체 PDCA 진입 |
| 6 | **MEDIUM** | Notepad Wisdom | Phase 3 중 발견한 교훈 휘발 |
| 7 | **MEDIUM** | Agent Teams 강제 미준수 | Lead 자체가 구 subagent 패턴 사용 (실증됨) |
| 8 | **LOW** | Delegation Categories | temperature/thinking 세분화 미적용 |
| 9 | **LOW** | Frontend-UI-UX silent | UI 작업 시 designer 라우팅 없음 |
| 10 | **LOW** | Git-Master silent | 커밋 시 atomic commit 전문성 미적용 |
| 11 | **LOW** | Context Persistence | `<remember>` 세션 간 학습 없음 |

### 1.3 Root Cause

v21.0 설계 시 "Skill() 호출 제거"에 집중하면서, OMC가 **Skill 외부에서** 제공하던 기능들을 간과:
- Hook 기반 자동 감지 (keyword-detector, persistent-mode)
- Silent 스킬 활성화 (frontend-ui-ux, git-master)
- 의미론적 라우팅 (Delegation Categories)
- 교차 세션 학습 (Notepad Wisdom, Context Persistence)

---

## 2. Goals & Non-Goals

### 2.1 Goals

| # | Goal | 측정 기준 |
|:-:|------|----------|
| G1 | OMC 28개 스킬의 핵심 패턴을 /auto에 이식 | 이식 체크리스트 100% |
| G2 | 키워드 하이재킹 해제 + 독립 모드 복원 | `ultrawork`/`autopilot`/`ralph`가 고유 동작 실행 |
| G3 | 도메인 인식 에이전트 선택 추가 | Phase 3에서 UI→designer, 보안→security-reviewer 라우팅 |
| G4 | Agent Teams 강제 준수 | Lead 포함 구 subagent 호출 0건 |
| G5 | Continuation Enforcement 복원 | TeamDelete 전 5점 체크리스트 통과 필수 |
| G6 | 인과관계 그래프 v21.0→v22.0 갱신 | 모든 참조가 현행 패턴과 일치 |

### 2.2 Non-Goals

| # | Non-Goal | 이유 |
|:-:|----------|------|
| NG1 | OMC 독립 스킬 /auto에 흡수 | ultrawork/ecomode/swarm/pipeline은 독립 유지 |
| NG2 | Skill() 호출 재도입 | Agent Teams 단일 패턴 유지 |
| NG3 | State 파일 의존 재도입 | Stop Hook 문제 재발 방지 |
| NG4 | Hook 시스템 변경 | OMC plugin cache hook은 변경 불가 (업데이트 시 덮어씀) |
| NG5 | 전체 OMC 28개 스킬 1:1 복제 | 핵심 패턴만 이식, 독립 스킬은 그대로 |

---

## 2.5 OMC 핵심 워크플로우 심층 분석

> **목적**: Category B "이식 완료(✅)" 10개 항목의 실제 이식 수준을 OMC 원본 소스 대비 메커니즘 단위로 검증.
> **원본 소스**: `.claude/plugins/cache/omc/oh-my-claudecode/3.6.2/commands/`

---

### 2.5.1 RALPLAN — Adversarial Consensus Architecture (원본 278줄)

**원본의 독창적 메커니즘:**

| # | 메커니즘 | 설명 |
|:-:|----------|------|
| M1 | **적대적 합의** | Critic은 "Ruthless Reviewer" — 계획이 반대를 통과해야만 승인됨 |
| M2 | **Quality Gates 4개** | Critic 호출 전 사전 검증: 파일 존재, 참조 유효, 구체적 기준, 모호어 없음 |
| M3 | **Architect = 온디맨드 Oracle** | 항상 참여하지 않고 Planner/Critic이 질문할 때만 호출 |
| M4 | **구조적 통신 프로토콜** | `ARCHITECT_QUESTION` / `ARCHITECT_ANSWER` / `CRITIC_FEEDBACK` 형식 |
| M5 | **HARD RULE** | "Steps 5-7 are NON-NEGOTIABLE" — Plan mode에서도 Critic 우회 불가 |
| M6 | **수렴 메커니즘** | max 5 iter + 강제 승인 (경고 포함) safety valve |
| M7 | **상태 복구** | `ralplan-state.json`으로 세션 중단 시 재개 가능 |

**v21.0 이식 현황 (Phase 1 HEAVY):**

| 메커니즘 | 이식 상태 | 증거 |
|----------|:---------:|------|
| M1 적대적 합의 | ✅ | Planner→Architect→Critic 순차 루프, "APPROVE → 종료 / REVISE → 반복" |
| M2 Quality Gates 4개 | ❌ | REFERENCE.md에 미기술 — Critic 호출 전 사전 검증 없음 |
| M3 Architect 온디맨드 | ❌ | 매 iteration마다 Architect 순차 호출 (질문 없어도 실행) |
| M4 구조적 통신 프로토콜 | ❌ | 자유 텍스트 메시지 — QUESTION/ANSWER/FEEDBACK 형식 없음 |
| M5 HARD RULE | ✅ | "APPROVE → Loop 종료" 로직은 동일 |
| M6 수렴 메커니즘 | ✅ | max 5 iter 명시 |
| M7 상태 복구 | ❌ | State 파일 의존 제거 (v21.0 설계 결정) — 세션 중단 시 재개 불가 |

**이식 수준**: 7개 중 3개 이식 → **Structure-Only (43%)**

---

### 2.5.2 RALPH — Self-Referential Completion Loop (원본 122줄)

**원본의 독창적 메커니즘:**

| # | 메커니즘 | 설명 |
|:-:|----------|------|
| M1 | **자기 참조 설계** | "Your previous attempt did not output the completion promise. Continue working" — 미완성 자체가 재실행 신호 |
| M2 | **Promise 기반 완료** | `<promise>{{PROMISE}}</promise>` — 암호학적 완료 신호 (Architect 검증 후에만 출력 가능) |
| M3 | **Zero Tolerance 선언** | NO Scope Reduction / NO Partial Completion / NO Premature Stopping / NO TEST DELETION |
| M4 | **Ralph+Ultrawork 자동 통합** | Ralph 활성화 시 Ultrawork 자동 병합 |
| M5 | **Delegation Enforcement** | Path-based Write Control (`.omc/`, `.claude/`만 직접 수정) |
| M6 | **3-tier Smart Model Routing** | 도메인별 12종 에이전트 × 3티어 매트릭스 |
| M7 | **Architect 검증 필수 완료** | Architect APPROVE 없이는 Promise 출력 금지 |

**v21.0 이식 현황 (Phase 3 impl-manager):**

| 메커니즘 | 이식 상태 | 증거 |
|----------|:---------:|------|
| M1 자기 참조 설계 | ❌ | impl-manager는 단일 실행 후 결과 보고 (반복 판단은 Lead가 수행) |
| M2 Promise 기반 완료 | ❌ | `IMPLEMENTATION_COMPLETED` 텍스트 메시지로 대체 (위조 가능) |
| M3 Zero Tolerance 선언 | ❌ | impl-manager prompt에 명시되지 않음 |
| M4 Ralph+Ultrawork 통합 | ⚠️ | /auto 내부에서 통합되나, 명시적 모드 병합 아닌 Agent Teams 흡수 |
| M5 Delegation Enforcement | ❌ | impl-manager에 경로 제한 규칙 없음 |
| M6 도메인별 에이전트 라우팅 | ❌ | executor 단일 유형만 사용 (도메인 분류 없음) |
| M7 Architect 검증 필수 완료 | ✅ | Phase 4.2에서 Architect APPROVE 후 완료 |

**이식 수준**: 7개 중 1개 이식 + 1개 부분 → **Structure-Only (21%)**

---

### 2.5.3 ULTRAWORK — Maximum Throughput Orchestration (원본 106줄)

**원본의 독창적 메커니즘:**

| # | 메커니즘 | 설명 |
|:-:|----------|------|
| M1 | **Orchestrator-Only 철학** | "YOU ARE AN ORCHESTRATOR, NOT AN IMPLEMENTER" — Lead가 코드 수정 절대 금지 |
| M2 | **Path-Based Write Control** | `.omc/`, `.claude/`, `CLAUDE.md`, `AGENTS.md`만 직접 수정 허용 |
| M3 | **도메인별 3-tier 에이전트 매트릭스** | 13개 도메인(Analysis/Execution/Search/Research/Frontend/Docs/Visual/Planning/Testing/Security/Build/TDD/CodeReview) × 3 티어 |
| M4 | **Background Execution 분류** | install/build → background, test/lint → foreground (명확한 기준) |
| M5 | **Persistence Enforcement** | 4점 체크리스트 미충족 시 CONTINUE WORKING |

**v21.0 이식 현황:**

| 메커니즘 | 이식 상태 | 증거 |
|----------|:---------:|------|
| M1 Orchestrator-Only 선언 | ⚠️ | Phase 3에서 Lead가 직접 코드 수정 안 하나, SKILL.md에 명시되지 않음 (OMC CLAUDE.md에만 존재) |
| M2 Path-Based Write Control | ❌ | SKILL.md/REFERENCE.md에 경로 제한 규칙 없음 |
| M3 도메인별 에이전트 매트릭스 | ❌ | 7종만 사용 (explore, planner, critic, architect, executor, executor-high, analyst) |
| M4 Background Execution 분류 | ❌ | REFERENCE.md에 없음 |
| M5 Persistence Enforcement | ⚠️ | Phase 4 QA 루프로 부분 이식 (자동 승격만) |

**이식 수준**: 5개 중 0개 이식 + 2개 부분 → **Structure-Only (20%)**

---

### 2.5.4 AUTOPILOT — Full Autonomous Pipeline (원본 180줄)

**원본의 독창적 메커니즘:**

| # | 메커니즘 | 설명 |
|:-:|----------|------|
| M1 | **Phase 0 Expansion** | Analyst(opus) + Architect(opus) 사전 분석 → 암묵적 요구사항 추출 |
| M2 | **Triple Validation** | Phase 4에서 3개 Architect 병렬 (기능 완전성 + 보안 + 코드 품질) |
| M3 | **No User Interruption** | "Do NOT ask for user input unless truly ambiguous" |
| M4 | **Spec 통합** | Analyst + Architect 출력을 `.omc/autopilot/spec.md`로 병합 |

**v21.0 이식 현황:**

| 메커니즘 | 이식 상태 | 증거 |
|----------|:---------:|------|
| M1 Phase 0 Expansion | ⚠️ | explore(haiku) x2만 — Analyst/Architect(opus) 아닌 단순 파일 탐색 |
| M2 Triple Validation | ❌ | Phase 4.2는 architect 1개만 (보안/품질은 HEAVY 전용이나 병렬이 아닌 순차) |
| M3 No User Interruption | ❌ | /auto에 해당 선언 없음 (OMC CLAUDE.md 암묵 의존) |
| M4 Spec 통합 | ❌ | 별도 spec 파일 생성 없음 |

**이식 수준**: 4개 중 0개 이식 + 1개 부분 → **Not Transplanted (12%)**

---

### 2.5.5 ULTRAQA — Adaptive QA Cycling (원본 122줄)

**원본의 독창적 메커니즘:**

| # | 메커니즘 | 설명 |
|:-:|----------|------|
| M1 | **Architect 진단** | 매 실패마다 architect(opus)가 root cause 분석 후 수정 지시 |
| M2 | **Same Failure 3x 조기 종료** | 동일 실패 3회 → 무한 루프 방지 + root cause 표면화 |
| M3 | **Multi-Goal 지원** | tests, build, lint, typecheck, custom, interactive 6가지 |
| M4 | **Interactive Testing** | qa-tester 에이전트로 tmux 기반 CLI 테스트 |
| M5 | **4가지 종료 조건** | Goal met, Max cycles, Same failure 3x, Environment error |

**v21.0 이식 현황 (Phase 4 Lead QA):**

| 메커니즘 | 이식 상태 | 증거 |
|----------|:---------:|------|
| M1 Architect 진단 | ❌ | Lead가 직접 실행 → 실패 시 executor에게 바로 수정 위임 (root cause 분석 없음) |
| M2 Same Failure 3x | ✅ | failure_history + 3회 조기 종료 구현 |
| M3 Multi-Goal | ⚠️ | ruff + pytest + build 고정 (lint/typecheck/custom/interactive 미지원) |
| M4 Interactive Testing | ❌ | qa-tester 에이전트 미활용 |
| M5 4가지 종료 조건 | ⚠️ | Goal met + Same failure 3x만 (Max cycles/Environment error 미명시) |

**이식 수준**: 5개 중 1개 이식 + 2개 부분 → **Partial (40%)**

---

### 2.5.6 보조 워크플로우 (독립 유지 — Non-Goal)

#### SWARM — SQLite Atomic Task Distribution (원본 483줄)

| 핵심 메커니즘 | 설명 |
|-------------|------|
| SQLite ACID 트랜잭션 | IMMEDIATE 락으로 race-condition-free task claiming |
| Heartbeat 프로토콜 | 60초 주기, 5분 미응답 시 auto-release |
| Lease-Based Ownership | 시간 기반 만료로 indefinite hang 방지 |
| Crash Recovery | 에이전트 죽어도 task auto-release → 다른 에이전트 pick up |
| Full Schema | tasks + heartbeats + swarm_session 3개 테이블 |

**v21.0 관계**: Agent Teams Mailbox가 coordination 역할 → SWARM과 다른 패턴. 독립 유지 적절.

#### ULTRAPILOT — File Ownership Partitioning (원본 159줄)

| 핵심 메커니즘 | 설명 |
|-------------|------|
| 파일 소유권 배타적 분할 | Worker별 exclusive file set → merge conflict 원천 차단 |
| Shared Files 순차 처리 | package.json, tsconfig.json 등은 병렬 후 순차 |
| 병렬화 적합성 판단 | Phase 0에서 task가 병렬 가능한지 명시적 평가 |
| Fallback | 병렬 불가 → 일반 autopilot으로 전환 |

**v21.0 관계**: HEAVY 모드의 `--worktree` 옵션으로 부분적 격리 가능하나, 파일 소유권 분할과는 다른 개념.

#### PIPELINE — Unix-Pipe Agent Chaining (원본 230줄)

| 핵심 메커니즘 | 설명 |
|-------------|------|
| Unix Pipe 메타포 | `explore -> architect -> executor` 선언적 문법 |
| 6개 Built-in Preset | review, implement, debug, research, refactor, security |
| 팬인/팬아웃 | `[explore, researcher] -> architect` 병렬 스테이지 |
| Per-Stage Model Routing | `explore:haiku -> architect:opus` 스테이지별 모델 |
| 구조적 Data Passing | `pipeline_context.previous_stages[].findings` 체이닝 |

**v21.0 관계**: PDCA Phase 순서가 사실상 고정 파이프라인이나, Pipeline의 유연한 선언적 문법과는 본질적으로 다름.

#### ECOMODE — Token-Efficient Execution

| 핵심 메커니즘 | 설명 |
|-------------|------|
| Haiku-First 라우팅 | 모든 에이전트를 haiku로 먼저 실행, 실패 시만 sonnet 승격 |
| Token Budget 추적 | 세션별 토큰 사용량 모니터링 + 경고 |
| Prompt 압축 | 불필요한 context 제거 |

**v21.0 관계**: /auto의 LIGHT 모드가 haiku 사용이나, Ecomode의 "실패 시 승격" 패턴과는 다름. 독립 유지 적절.

---

### 2.5.7 Gap 종합 매트릭스

#### Category B "이식 완료" 항목 — 메커니즘 단위 정밀 평가

| 워크플로우 | 원본 핵심 메커니즘 수 | 이식 | 부분 | 누락 | 이식률 | 판정 |
|-----------|:------------------:|:----:|:----:|:----:|:-----:|------|
| ralplan (B2) | 7 | 3 | 0 | 4 | 43% | Structure-Only |
| ralph (B1) | 7 | 1 | 1 | 5 | 21% | Structure-Only |
| ultraqa (B3) | 5 | 1 | 2 | 2 | 40% | Partial |
| autopilot (해당 없음) | 4 | 0 | 1 | 3 | 12% | Not Transplanted |
| ultrawork (해당 없음) | 5 | 0 | 2 | 3 | 20% | Structure-Only |
| **합계** | **28** | **5** | **6** | **17** | **29%** | **Structure-Only 평균** |

> **참고**: orchestrate(B4), plan(B5), review(B6), tdd(B7), code-review(B8), build-fix(B9), research(B10)는
> 원본이 단순 라우팅/위임 패턴이므로 "구조 이식 = 충분"으로 판정. 위 5개만 복합 워크플로우.

#### 이식 수준 분류 기준

| 판정 | 기준 | 의미 |
|------|------|------|
| **Full** | 이식률 80%+ | 핵심 메커니즘 대부분 이식 완료 |
| **Partial** | 이식률 40-79% | 일부 핵심 메커니즘 이식, 주요 누락 존재 |
| **Structure-Only** | 이식률 20-39% | 구조적 유사성만 존재, 핵심 메커니즘 대부분 누락 |
| **Not Transplanted** | 이식률 0-19% | 이식이라 부르기 어려운 수준 |

#### 우선순위별 보완 필요 항목

| 우선순위 | 워크플로우 | 누락 메커니즘 | 보완 방안 | 예상 효과 |
|:--------:|-----------|-------------|----------|----------|
| **P1** | ralph | Zero Tolerance 선언 | impl-manager prompt에 4개 금지 조항 추가 | 범위 축소/부분 완료 방지 |
| **P1** | ralph | Promise 기반 완료 | 구조적 완료 신호 도입 (JSON 필드 기반) | 위조 불가능한 완료 판정 |
| **P2** | ralplan | Quality Gates 4개 | Critic 호출 전 Plan 문서 사전 검증 추가 | 불완전한 Plan의 Critic 낭비 방지 |
| **P2** | ultraqa | Architect 진단 | QA 실패 시 architect에게 root cause 분석 위임 | 맹목적 수정 반복 방지 |
| **P3** | ultrawork | 도메인별 에이전트 매트릭스 | Phase 3 도메인 감지 (v22.0 Plan 3.3) | 전문 에이전트 활용률 향상 |
| **P3** | ultrawork | Background Execution 규칙 | teammate prompt에 foreground/background 기준 명시 | 불필요한 대기 감소 |
| **P4** | ralplan | Architect 온디맨드 | Planner/Critic 질문 시에만 Architect 호출 | Architect 토큰 절감 |
| **P4** | autopilot | Phase 0 Expansion | analyst(opus) 사전 분석 추가 | 암묵적 요구사항 조기 발견 |

> **P1-P2는 v22.0 구현 필수**, P3는 Section 3에서 이미 계획됨, P4는 선택적 최적화.

---

### 2.5.8 결론

Category B "이식 완료(✅)" 판정은 **구조적 유사성** 기준으로만 이루어졌으며,
OMC 원본의 **핵심 메커니즘 75%가 실제로는 누락**됨.

"Planner→Critic 루프가 있으니 ralplan 이식 완료"라는 판정은
"엔진 없이 차체만 옮겨놓고 자동차 이식 완료"와 동일한 수준의 오류.

**수정 방향**:
- Category B의 복합 워크플로우 5개: ✅ → ⚠️ 구조 이식 (메커니즘 누락)
- Category B의 단순 라우팅 5개: ✅ 유지 (구조 이식 = 충분)
- v22.0 계획에 P1-P2 보완 항목 반영 필수

---

## 3. OMC Feature Complete Catalog

### 3.1 OMC Skills (28개) — 이식 전략

#### Category A: /auto에 이식할 핵심 패턴 (8개)

| # | OMC 스킬 | 핵심 패턴 | 이식 위치 | 이식 방법 |
|:-:|----------|----------|----------|----------|
| A1 | `autopilot` | Phase 0 Expansion (Analyst+Architect 사전 분석) | Phase 1.0 확장 | STANDARD/HEAVY에서 analyst teammate 추가 |
| A2 | `autopilot` | Phase 4 병렬 검증 (Architect+Security+Code-reviewer) | Phase 4.2 확장 | HEAVY에서 security-reviewer 병렬 추가 |
| A3 | `frontend-ui-ux` | 도메인 감지 → designer 라우팅 | Phase 3 DO | 도메인 분류기 추가 (아래 3.3) |
| A4 | `git-master` | Atomic commit 규칙 | Phase 5 ACT | 커밋 시 git-master 패턴 주입 |
| A5 | `note` | Notepad Wisdom (학습/결정/이슈 캡처) | Phase 3-4 | impl-manager prompt에 캡처 지시 |
| A6 | `plan` | Broad Request Detection | Phase 0 | PDCA 진입 전 필터 (아래 3.4) |
| A7 | `ultrawork` | Background Execution 규칙 | Phase 3-4 | teammate prompt에 background 규칙 명시 |
| A8 | `cancel` | Unified stop 패턴 | `/auto stop` | 모든 teammate + TeamDelete 정리 |

#### Category B: 이식 항목 (10개) — 메커니즘 수준별 재분류

> **참고**: Section 2.5의 심층 분석 결과를 반영. 복합 워크플로우 5개는 구조만 이식되고 핵심 메커니즘이 누락됨.

| # | OMC 스킬 | 이식된 위치 | 이식 수준 | 누락 메커니즘 (핵심) |
|:-:|----------|-----------|:---------:|---------------------|
| B1 | `ralph` (5조건 루프) | Phase 3 impl-manager | ⚠️ Structure-Only (21%) | Zero Tolerance, Promise 완료, 자기 참조, 도메인 라우팅, 경로 제한 |
| B2 | `ralplan` (Planner-Critic) | Phase 1 HEAVY | ⚠️ Structure-Only (43%) | Quality Gates 4개, Architect 온디맨드, 구조적 통신, 상태 복구 |
| B3 | `ultraqa` (QA cycling) | Phase 4 Lead QA | ⚠️ Partial (40%) | Architect 진단, Interactive Testing, Multi-Goal 확장 |
| B4 | `orchestrate` | Agent Teams 전체 | ✅ Full | — (Agent Teams로 완전 대체) |
| B5 | `plan` (계획 수립) | Phase 1 | ✅ Full | — (구조 이식 = 충분) |
| B6 | `review` (Critic 검증) | Phase 1 HEAVY | ✅ Full | — (구조 이식 = 충분) |
| B7 | `tdd` (TDD 강제) | impl-manager prompt | ✅ Full | — (라우팅 패턴) |
| B8 | `code-review` | Phase 4 code-analyzer | ✅ Full | — (라우팅 패턴) |
| B9 | `build-fix` | Phase 4 fixer | ✅ Full | — (라우팅 패턴) |
| B10 | `research` | Phase 1.0 explore | ✅ Full | — (라우팅 패턴) |

> **v22.0 필수 보완**: B1(ralph) P1 항목 2건 + B2(ralplan) P2 항목 1건 + B3(ultraqa) P2 항목 1건 — Section 2.5.7 참조

#### Category C: 독립 스킬 유지 (10개) — 이식 대상 아님

| # | OMC 스킬 | 유지 이유 |
|:-:|----------|----------|
| C1 | `ultrawork` | 즉시 병렬 실행은 PDCA와 다른 워크플로우 |
| C2 | `ecomode` | 토큰 절약 전용 모드 |
| C3 | `ultrapilot` | 파일 소유권 분할 병렬은 별도 패턴 |
| C4 | `swarm` | SQLite atomic claiming은 별도 인프라 |
| C5 | `pipeline` | 순차 체이닝은 PDCA Phase와 다른 구조 |
| C6 | `analyze` | 독립 디버깅/분석 스킬 |
| C7 | `deepsearch` | 독립 탐색 스킬 |
| C8 | `learner` | 스킬 추출은 세션 단위 기능 |
| C9 | `mcp-setup` | 인프라 설정 전용 |
| C10 | `ralph-init` | PRD 초기화는 ralph 전용 |

### 3.2 OMC Agents (32개) — /auto 활용 확대 계획

**현재 v21.0**: 32개 중 **7종** 사용

```
planner, critic, architect, executor, executor-high, explore, analyst
```

**v22.0 목표**: **15종** 이상 활용 (도메인 인식 라우팅 추가)

| 도메인 | 추가 에이전트 | 활용 Phase | 조건 |
|--------|-------------|-----------|------|
| Frontend | `designer` / `designer-high` | Phase 3 DO | UI/컴포넌트 작업 감지 시 |
| Security | `security-reviewer` | Phase 4.2 CHECK | HEAVY 모드에서 항상 |
| Testing | `qa-tester` | Phase 4.1 CHECK | E2E 실패 시 진단 위임 |
| Data | `scientist` | Phase 3 DO | 데이터 분석 작업 감지 시 |
| Docs | `writer` | Phase 5 ACT | 보고서 생성 시 |
| Build | `build-fixer` | Phase 4.1 CHECK | 빌드 실패 시 전문 수정 |
| TDD | `tdd-guide` | Phase 3 DO | 테스트 작성 전문 위임 |
| Code Review | `code-reviewer` | Phase 4.2 CHECK | HEAVY 모드에서 추가 |

### 3.3 도메인 인식 라우팅 (NEW — Phase 3 DO)

```
Lead가 작업 내용 분석 → 도메인 분류:

도메인 감지 규칙:
┌─────────────────────────────────────────────────────┐
│ IF 영향 파일에 다음 패턴 포함:                         │
│   *.tsx, *.jsx, *.css, *.scss, *.svelte, *.vue      │
│   components/, pages/, layouts/, styles/             │
│ THEN domain = "frontend"                             │
│   → executor 대신 designer/designer-high 사용         │
│                                                      │
│ IF 영향 파일에 다음 패턴 포함:                         │
│   auth*, security*, crypto*, password*, token*       │
│   middleware/auth*, policies/*                        │
│ THEN domain = "security"                             │
│   → Phase 4.2에 security-reviewer 추가               │
│                                                      │
│ IF 영향 파일에 다음 패턴 포함:                         │
│   *.ipynb, data/, analytics/, ml/, stats/            │
│ THEN domain = "data"                                 │
│   → executor 대신 scientist 사용                      │
│                                                      │
│ ELSE domain = "general"                              │
│   → executor/executor-high (기존 동작)                │
└─────────────────────────────────────────────────────┘
```

### 3.4 Broad Request Detection (NEW — Phase 0)

```
/auto 진입 시 작업 인수 분석:

┌──────────────────────────────────────────────────────┐
│ Broad 판정 조건 (ANY):                                │
│   1. 모호한 동사: "improve", "enhance", "fix",        │
│      "refactor" + 구체적 대상 없음                     │
│   2. 파일/함수 미지정                                  │
│   3. 3개+ 비관련 영역 언급                             │
│   4. 단일 문장, 명확한 산출물 없음                      │
│                                                       │
│ Broad → Phase 1 PLAN 정상 진입 (STANDARD+ 강제)       │
│                                                       │
│ Trivial 판정 조건 (ALL):                              │
│   1. 단일 파일 지정                                    │
│   2. 구체적 동작 ("이 함수에 에러 핸들링 추가")          │
│   3. 예상 변경 10줄 이하                               │
│                                                       │
│ Trivial → PDCA 스킵, Lead 직접 실행 + Architect 검증   │
└──────────────────────────────────────────────────────┘
```

### 3.5 OMC Internal Protocols — 이식 상세

#### 3.5.1 Continuation Enforcement (Phase 5 TeamDelete 전)

```
Phase 5 ACT → TeamDelete() 직전 5점 검증:

□ [1] TODO: TaskList 조회 → pending/in_progress == 0
□ [2] FUNCTIONALITY: impl-manager COMPLETED 메시지 확인
□ [3] TESTS: Phase 4 Lead QA 통과 증거 존재
□ [4] ERRORS: ruff + pytest + build 최종 결과 에러 0
□ [5] ARCHITECT: Phase 4.2 APPROVE 판정 존재

ALL 5 체크 → TeamDelete() 허용
ANY 미충족 → 해당 Phase 재실행 (TeamDelete 불가)
```

#### 3.5.2 Iron Law Evidence Chain (강화)

현재 impl-manager prompt에 포함되어 있으나, **Lead 수준**에서도 강제:

```
Lead가 "완료" 선언 전 필수 증거:

| 주장 | 필수 증거 | 증거 위치 |
|------|----------|----------|
| "구현 완료" | impl-manager COMPLETED 메시지 | Mailbox 수신 내용 |
| "테스트 통과" | pytest/jest 실행 결과 | Phase 4 Lead QA 출력 |
| "빌드 성공" | ruff/build 실행 결과 | Phase 4 Lead QA 출력 |
| "검증 통과" | Architect APPROVE 메시지 | Phase 4.2 Mailbox |
| "갭 90%+" | gap-detector 결과 | Phase 4.2 Mailbox |

증거 없는 주장 → 사용자에게 "증거 미확보" 알림 + 해당 검증 재실행
```

#### 3.5.3 Agent Teams 강제 준수 (Lead 자기 규제)

```
Lead의 Task() 호출 시 필수 체크:

✅ 허용:
  Task(subagent_type="...", name="역할명", team_name="pdca-{feature}",
       model="tier", prompt="...")

❌ 금지 (즉시 자기 수정):
  Task(subagent_type="...", model="tier", prompt="...")  # name 없음
  Task(subagent_type="...", prompt="...")                 # team_name 없음
  Task(..., run_in_background=True)                      # 구 패턴

예외: 순수 리서치 (읽기 전용) 에이전트도 Agent Teams 사용 필수
      → "빠른 조회라 괜찮다"는 변명 금지 (2026-02-18 실증)
```

#### 3.5.4 Notepad Wisdom 연동 (Phase 3-4)

```
impl-manager prompt에 추가할 지시:

"구현 중 다음 항목을 발견하면 IMPLEMENTATION_COMPLETED 메시지에 포함:
  - LEARNING: 기술적 발견 (예: "이 API는 rate limit 100/min")
  - DECISION: 아키텍처 결정 (예: "JWT 대신 session 사용")
  - ISSUE: 알려진 이슈 (예: "IE11 미지원")
  - PROBLEM: 차단 요소 (예: "외부 API 다운")
"

Lead가 수신 후 .omc/notepads/{feature}/ 에 저장:
  learnings.md, decisions.md, issues.md, problems.md
```

#### 3.5.5 Background Execution 규칙 (teammate prompt 주입)

```
impl-manager 및 fixer teammate prompt에 추가:

"장시간 명령 실행 시:
  Background (run_in_background: true):
    - npm install, pip install, cargo build
    - docker build, docker pull
  Foreground (결과 필요):
    - pytest, npm test (결과 캡처 필수)
    - ruff check, tsc --noEmit (에러 확인)
    - git status, git diff (상태 확인)
  최대 동시 background: 5개"
```

---

## 4. Implementation Scope

### 4.1 변경 대상 파일

| # | 파일 | 변경 내용 | 예상 줄 수 |
|:-:|------|----------|:---------:|
| 1 | `.claude/skills/auto/SKILL.md` | 키워드 제거, Phase 0 Trivial 필터, Phase 5 Enforcement | +30 |
| 2 | `.claude/skills/auto/REFERENCE.md` | 도메인 라우팅, Wisdom, Background 규칙, 증거 체인 | +150 |
| 3 | `.claude/references/skill-causality-graph.md` | v22.0 Agent Teams 패턴으로 전면 갱신 | 전면 재작성 |
| 4 | `.claude/skills/auto/scripts/omc_bridge.py` | dead code 삭제 또는 Agent Teams 유틸리티로 전환 | -700 또는 재작성 |
| 5 | `.claude/rules/08-skill-routing.md` | 키워드 하이재킹 해제 반영 | +10 |

### 4.2 변경하지 않는 파일

| 파일 | 이유 |
|------|------|
| `~/.claude/CLAUDE.md` (OMC) | OMC plugin 영역, 직접 수정 불가 |
| OMC plugin cache hooks | 업데이트 시 덮어씀 |
| 독립 스킬 (ultrawork, ecomode 등) | Non-Goal NG1 |

---

## 5. Detailed Design

### 5.1 SKILL.md 변경

#### 5.1.1 키워드 하이재킹 해제

```yaml
# BEFORE (v21.0)
triggers:
  keywords:
    - "/auto"
    - "auto"
    - "autopilot"    # ← 제거
    - "ulw"          # ← 제거
    - "ultrawork"    # ← 제거
    - "ralph"        # ← 제거
    - "/work"
    - "work"

# AFTER (v22.0)
triggers:
  keywords:
    - "/auto"
    - "auto"
    - "/work"
    - "work"
```

이렇게 하면 `autopilot`, `ulw`, `ultrawork`, `ralph` 키워드는 OMC CLAUDE.md의 Mandatory Skill Invocation 테이블에서 독립 처리됨.

#### 5.1.2 Phase 0 Trivial 필터 추가

SKILL.md Phase 0 섹션에 추가:

```markdown
**Step 0.1: Trivial 판정 (PDCA 스킵 여부)**

| 조건 (ALL 충족 시 Trivial) | 예시 |
|---------------------------|------|
| 단일 파일 지정 | "src/auth.py의 login 함수" |
| 구체적 동작 명시 | "에러 핸들링 추가", "오타 수정" |
| 예상 변경 10줄 이하 | 함수 1개 수정 |

Trivial → PDCA 스킵:
  Lead 직접 실행 (10줄 이하) 또는 executor teammate 단일 실행
  → Architect teammate 검증 (APPROVE/REJECT)
  → 완료 (TeamCreate/TeamDelete 불필요)
```

#### 5.1.3 Phase 5 Continuation Enforcement 추가

SKILL.md Phase 5 섹션에 추가:

```markdown
**Phase 5 Pre-TeamDelete 체크리스트 (MANDATORY)**

TeamDelete() 호출 전 5점 검증:
1. TaskList → pending/in_progress == 0
2. impl-manager COMPLETED 메시지 수신 확인
3. Phase 4 Lead QA 통과 증거 (최신 5분 이내)
4. ruff + pytest + build 에러 0
5. Architect APPROVE 판정 확인

미충족 시: 해당 Phase 재실행. TeamDelete 불가.
```

### 5.2 REFERENCE.md 변경

#### 5.2.1 도메인 인식 라우팅 섹션 추가

Phase 3 DO 섹션에 새 하위 섹션:

```markdown
### Step 3.0.5: 도메인 감지 (Phase 3 진입 시)

Lead가 Plan/Design 문서의 영향 파일 분석 → 도메인 분류:

| 도메인 | 감지 패턴 | Phase 3 에이전트 | Phase 4 추가 에이전트 |
|--------|----------|----------------|---------------------|
| frontend | *.tsx, *.jsx, *.css, components/ | designer/designer-high | — |
| security | auth*, security*, token*, middleware/auth* | executor (보안 주의 prompt) | security-reviewer |
| data | *.ipynb, data/, analytics/, ml/ | scientist/scientist-high | — |
| general | (위 해당 없음) | executor/executor-high | — |

도메인 감지는 Plan 문서의 "영향 파일" 섹션 파싱으로 수행.
감지 결과를 impl-manager prompt에 "domain: {domain}" 으로 주입.
```

#### 5.2.2 Notepad Wisdom 섹션 추가

```markdown
### Notepad Wisdom 연동 (Phase 3-4)

impl-manager COMPLETED 메시지에 다음 필드 추가 (선택):
  "wisdom": {
    "learnings": ["..."],
    "decisions": ["..."],
    "issues": ["..."],
    "problems": ["..."]
  }

Lead 수신 후 처리:
  - wisdom 필드 존재 시 → .omc/notepads/{feature}/ 에 append
  - wisdom 필드 없음 → 스킵 (선택적 기능)
```

#### 5.2.3 Background Execution 규칙 섹션 추가

```markdown
### Background Execution 규칙

impl-manager 및 fixer teammate prompt에 포함할 규칙:

| 명령 유형 | 실행 방식 | 이유 |
|----------|---------|------|
| npm install, pip install | background | 네트워크 대기 |
| docker build/pull | background | 장시간 |
| npm run build, cargo build | foreground | 결과 캡처 필수 |
| pytest, npm test | foreground | 결과 파싱 필수 |
| ruff, tsc --noEmit | foreground | 에러 확인 |
| git status/diff | foreground | 즉시 확인 |

동시 background 최대: 5개
```

### 5.3 skill-causality-graph.md 전면 갱신

```markdown
# 스킬 인과관계 그래프 (v22.0 — Agent Teams 단일 패턴)

## 1. /auto PDCA Orchestrator

                    ┌─────────────────────────────────────┐
                    │         /auto (v22.0)                │
                    │   PDCA Orchestrator (Agent Teams)    │
                    └─────────────────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
     작업 인수 있음           작업 인수 없음            Options
     (Phase 0-5)            (자율 발견)              (전처리)
              │                     │                     │
         ┌────┴────┐          Tier 0-5            --gdocs, --mockup
         │         │          Discovery           --slack, --gmail
    Trivial?   Normal?                            --debate, --daily
         │         │
    직접실행   Phase 0-5
    +검증     (아래 상세)

## 2. Phase 0-5 PDCA (Agent Teams)

TeamCreate("pdca-{feature}")
  │
  ├── Phase 0: 옵션 파싱 + Trivial 판정
  │   └── Trivial → PDCA 스킵 (직접 실행 + Architect 검증)
  │
  ├── Phase 1 PLAN
  │   ├── Step 1.0: Task(explore, haiku) x2 병렬
  │   ├── Step 1.1: 복잡도 판단 (0-5)
  │   ├── Step 1.2: LIGHT: Task(planner, haiku)
  │   │             STANDARD: Task(planner, sonnet)
  │   │             HEAVY: Planner-Critic Loop (max 5 iter)
  │   └── Step 1.3: 이슈 연동
  │
  ├── Phase 2 DESIGN
  │   ├── LIGHT: 스킵
  │   ├── STANDARD: Task(executor, sonnet)
  │   └── HEAVY: Task(executor-high, opus)
  │
  ├── Phase 3 DO
  │   ├── Step 3.0: 옵션 처리
  │   ├── Step 3.0.5: 도메인 감지 (NEW v22.0)
  │   │   → frontend: designer / security: executor+주의 / data: scientist
  │   ├── LIGHT: Task(executor|designer|scientist, sonnet)
  │   └── STD/HEAVY: Task(impl-manager, sonnet|opus) — 5조건 루프
  │
  ├── Phase 4 CHECK
  │   ├── Step 4.1: Lead QA (ruff + pytest + build)
  │   ├── Step 4.2: Architect → gap-detector → code-analyzer 순차
  │   │   HEAVY 추가: security-reviewer (보안 도메인 시)
  │   ├── Step 4.3: E2E (Playwright 있을 때)
  │   └── Step 4.4: TDD 커버리지
  │
  └── Phase 5 ACT
      ├── Continuation Enforcement (5점 체크, NEW v22.0)
      ├── gap < 90% → pdca-iterator → Phase 4 재실행
      ├── gap >= 90% + APPROVE → report-generator → TeamDelete
      └── REJECT → executor fixer → Phase 4 재실행

## 3. BKIT 에이전트 역할 (변경 없음)

| Agent | Phase | 역할 |
|-------|:-----:|------|
| gap-detector | 4 CHECK | 설계-구현 90% 검증 |
| pdca-iterator | 5 ACT | gap < 90% 자동 개선 |
| code-analyzer | 4 CHECK | 코드 품질 분석 |
| report-generator | 5 ACT | 완료 보고서 |

## 4. 독립 스킬 (v22.0에서 이식 대상 아님)

ultrawork, ecomode, ultrapilot, swarm, pipeline, cancel,
analyze, deepsearch, tdd, frontend-ui-ux, git-master, learner

이들은 /auto와 독립적으로 호출 가능.
키워드 트리거는 OMC CLAUDE.md에서 처리.
```

### 5.4 omc_bridge.py 처리

**Option A (권장): 삭제**
- v21.0에서 이미 dead code
- Agent Teams 패턴은 SKILL.md/REFERENCE.md로 충분
- 700줄 제거로 코드베이스 간소화

**Option B: Agent Teams 유틸리티로 전환**
- `UNIFIED_AGENT_REGISTRY`만 보존
- 도메인 감지 함수 추가 (`detect_domain(files: List[str]) -> str`)
- Skill/State 관련 코드 전부 삭제

---

## 6. Risk Assessment

| # | 위험 | 확률 | 영향 | 완화 |
|:-:|------|:---:|:---:|------|
| R1 | 키워드 제거 후 OMC 트리거 실패 | LOW | HIGH | OMC CLAUDE.md의 Mandatory Skill Invocation이 독립 처리 |
| R2 | 도메인 감지 오탐 (frontend 아닌데 designer 사용) | MED | MED | 감지 규칙을 보수적으로 설정 (확실한 패턴만) |
| R3 | Notepad Wisdom 토큰 오버헤드 | LOW | LOW | 선택적 기능 (wisdom 필드 없으면 스킵) |
| R4 | Trivial 판정 오류 (복잡한 작업을 Trivial로 분류) | MED | MED | 빌드 실패 시 자동 STANDARD 승격 (기존 규칙) |
| R5 | omc_bridge.py 삭제 시 기존 참조 파괴 | LOW | LOW | grep으로 참조 검증 후 삭제 |

---

## 7. Testing Strategy

| # | 테스트 | 검증 방법 |
|:-:|--------|----------|
| T1 | 키워드 분리 | `ultrawork fix all errors` 입력 → OMC ultrawork 실행 (not /auto) |
| T2 | Trivial 필터 | `/auto "src/auth.py 오타 수정"` → PDCA 스킵, 직접 실행 |
| T3 | 도메인 라우팅 | `/auto "React 컴포넌트 추가"` → Phase 3에서 designer 사용 |
| T4 | Continuation | Phase 5에서 테스트 실패 상태 → TeamDelete 차단 확인 |
| T5 | Agent Teams 강제 | Lead의 Task() 호출에 name/team_name 필수 확인 |
| T6 | 인과관계 일치 | causality-graph.md의 모든 참조가 SKILL.md/REFERENCE.md와 일치 |

---

## 8. Implementation Plan (Phase별)

### Phase 1: 문서 정비 (LIGHT — 예상 변경 40줄)

1. `skill-causality-graph.md` 전면 갱신 (v22.0)
2. `08-skill-routing.md` 키워드 하이재킹 해제 반영
3. `omc_bridge.py` 삭제 또는 정리

### Phase 2: SKILL.md 업데이트 (STANDARD — 예상 변경 30줄)

1. triggers.keywords에서 `autopilot`, `ulw`, `ultrawork`, `ralph` 제거
2. Phase 0에 Trivial 필터 추가
3. Phase 5에 Continuation Enforcement 추가

### Phase 3: REFERENCE.md 확장 (STANDARD — 예상 변경 150줄)

1. 도메인 인식 라우팅 섹션 추가 (Step 3.0.5)
2. Notepad Wisdom 연동 섹션 추가
3. Background Execution 규칙 섹션 추가
4. Lead Iron Law Evidence Chain 강화 섹션 추가
5. Agent Teams 강제 준수 자기 규제 섹션 추가

### Phase 4: 검증

1. T1-T6 테스트 수행
2. Architect 검증
3. gap-detector (90% 이상 목표)

---

## 9. Success Criteria

| # | 기준 | 측정 |
|:-:|------|------|
| SC1 | OMC 키워드가 독립 스킬로 정상 라우팅 | `ultrawork`, `autopilot` 테스트 |
| SC2 | /auto가 도메인별 전문 에이전트 사용 | UI 작업 시 designer 호출 확인 |
| SC3 | Phase 5 Continuation Enforcement 작동 | 미완료 시 TeamDelete 차단 |
| SC4 | 인과관계 그래프가 현행과 100% 일치 | 문서 교차 검증 |
| SC5 | omc_bridge.py dead code 제거 | 파일 삭제 또는 최소화 |
| SC6 | Agent Teams 구 패턴 호출 0건 | Lead Task() 호출 전수 검사 |

---

## Appendix A: OMC 28개 스킬 → /auto 이식 매트릭스

| # | OMC Skill | 핵심 패턴 | v21.0 상태 | v22.0 목표 | 이식 방법 |
|:-:|-----------|----------|:----------:|:----------:|----------|
| 1 | autopilot | Expansion + 병렬 검증 | ℹ️ 분리 | ⚠️ 패턴 이식 | Phase 1.0 analyst + Phase 4.2 security |
| 2 | ultrapilot | 파일 소유권 분할 | ℹ️ 분리 | ℹ️ 유지 | — |
| 3 | ultrawork | 즉시 병렬 실행 | ⚠️ 하이재킹 | ℹ️ 복원 | 키워드 제거 |
| 4 | ecomode | haiku 우선 | ⚠️ 하이재킹 | ℹ️ 복원 | 키워드 제거 |
| 5 | ralph | 5조건 지속 | ✅ | ✅ | 변경 없음 |
| 6 | plan | 계획 수립 | ✅ | ✅ | Broad Detection 추가 |
| 7 | ralplan | Planner-Critic | ✅ | ✅ | 변경 없음 |
| 8 | review | Critic 검증 | ✅ | ✅ | 변경 없음 |
| 9 | analyze | 디버깅 | ℹ️ 분리 | ℹ️ 유지 | — |
| 10 | deepsearch | 탐색 | ℹ️ 분리 | ℹ️ 유지 | — |
| 11 | deepinit | AGENTS.md | ❌ | ℹ️ 유지 | — |
| 12 | ultraqa | QA cycling | ✅ | ✅ | 변경 없음 |
| 13 | tdd | test-first | ℹ️ 분리 | ℹ️ 유지 | — |
| 14 | code-review | 코드 리뷰 | ℹ️ 분리 | ℹ️ 유지 | — |
| 15 | frontend-ui-ux | UI 도메인 | ❌ | ✅ 이식 | 도메인 라우팅 |
| 16 | build-fix | 빌드 수정 | ℹ️ 분리 | ℹ️ 유지 | Phase 4 fixer 활용 |
| 17 | git-master | atomic commit | ❌ | ⚠️ 패턴 주입 | Phase 5 커밋 시 |
| 18 | release | 릴리스 | ❌ | ℹ️ 유지 | — |
| 19 | orchestrate | 오케스트레이션 | ✅ | ✅ | Agent Teams |
| 20 | swarm | atomic claiming | ℹ️ 분리 | ℹ️ 유지 | — |
| 21 | pipeline | 체이닝 | ℹ️ 분리 | ℹ️ 유지 | — |
| 22 | cancel | 통합 취소 | ℹ️ 분리 | ℹ️ 유지 | — |
| 23 | learner | 스킬 추출 | ❌ | ℹ️ 유지 | — |
| 24 | note | Notepad | ❌ | ✅ 이식 | Wisdom 연동 |
| 25 | research | 리서치 | ℹ️ 분리 | ℹ️ 유지 | — |
| 26 | omc-setup | 설정 | ❌ | ℹ️ 유지 | — |
| 27 | doctor | 진단 | ❌ | ℹ️ 유지 | — |
| 28 | help/hud | UI 설정 | ❌ | ℹ️ 유지 | — |

**v22.0 이식 요약**:
- ✅ 유지 (10개): ralph, plan, ralplan, review, ultraqa, orchestrate + (변경 없음)
- ✅ 신규 이식 (3개): frontend-ui-ux 도메인 라우팅, note Wisdom, autopilot 패턴
- ⚠️ 패턴 주입 (2개): git-master 커밋 규칙, plan Broad Detection
- ℹ️ 독립 유지 (13개): ultrawork, ecomode, ultrapilot, swarm, pipeline, cancel, analyze, deepsearch, tdd, learner, research, deepinit, 기타
- 🔧 키워드 복원 (2개): ultrawork, ralph → 하이재킹 해제

---

## Appendix B: OMC 32개 에이전트 → /auto 활용 매트릭스

| 에이전트 | v21.0 활용 | v22.0 활용 | 추가 조건 |
|---------|:----------:|:----------:|----------|
| architect | Phase 4.2 | Phase 4.2 | 변경 없음 |
| architect-medium | — | Phase 1 STD | 선택적 |
| architect-low | — | — | — |
| executor | Phase 3,4 | Phase 3,4 | 변경 없음 |
| executor-high | Phase 2,3 HEAVY | Phase 2,3 HEAVY | 변경 없음 |
| executor-low | — | — | — |
| explore | Phase 1.0 | Phase 1.0 | 변경 없음 |
| explore-medium | — | — | — |
| explore-high | — | — | — |
| planner | Phase 1 | Phase 1 | 변경 없음 |
| critic | Phase 1 HEAVY | Phase 1 HEAVY | 변경 없음 |
| analyst | — | Phase 1.0 STD/HEAVY | autopilot 패턴 이식 |
| **designer** | — | **Phase 3 frontend** | **NEW v22.0** |
| **designer-high** | — | **Phase 3 frontend HEAVY** | **NEW v22.0** |
| designer-low | — | — | — |
| **security-reviewer** | — | **Phase 4.2 HEAVY** | **NEW v22.0** |
| security-reviewer-low | — | — | — |
| **scientist** | — | **Phase 3 data** | **NEW v22.0** |
| scientist-high | — | — | — |
| scientist-low | — | — | — |
| **qa-tester** | — | **Phase 4.1 E2E 실패** | **NEW v22.0** |
| qa-tester-high | — | — | — |
| **writer** | — | **Phase 5 보고서** | **NEW v22.0** |
| **build-fixer** | — | **Phase 4.1 빌드 실패** | **NEW v22.0** |
| build-fixer-low | — | — | — |
| **tdd-guide** | — | **Phase 3 테스트 위임** | **NEW v22.0** 선택적 |
| tdd-guide-low | — | — | — |
| code-reviewer | — | Phase 4.2 HEAVY | 선택적 |
| code-reviewer-low | — | — | — |
| researcher | — | — | — |
| researcher-low | — | — | — |
| vision | — | — | — |

**v22.0 에이전트 활용**: 7종 → **15종** (+8종 추가)
