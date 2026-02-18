# /auto v21.0 통합 재설계 — 설계 문서

**Version**: 1.0.0 | **Date**: 2026-02-17 | **Status**: DRAFT
**PRD**: `docs/01-plan/auto-v21-unified-redesign.plan.md`

---

## 1. 구현 대상 파일 목록

| # | 파일 | 변경 유형 | 예상 줄 수 | 설명 |
|:-:|------|:--------:|:----------:|------|
| 1 | `.claude/skills/auto/SKILL.md` | 수정 | ~240줄 | Phase 1/3/4 코드 블록 전면 교체 (Skill() → Agent Teams) |
| 2 | `.claude/skills/auto/REFERENCE.md` | 수정 | ~650줄 | 상세 워크플로우, impl-manager prompt 전문, Vercel BP 규칙 |
| 3 | `.claude/rules/08-skill-routing.md` | 수정 | ~50줄 | 스킬 매핑 테이블 업데이트 (ralph/ultrawork/ralplan/ultraqa 제거) |
| 4 | `.claude/hooks/session_cleanup.py` | 수정 | ~175줄 | ralph/ultrawork state 정리 코드 제거 (해당 코드 없으나 향후 방지 주석) |
| 5 | `docs/.pdca-status.json` | 수정 | 기존 | v21.0 feature 항목 추가 |
| 6 | `docs/AGENTS_REFERENCE.md` | 수정 | 해당 섹션 | /auto 내부 동작 설명 업데이트 |

### 제거 대상

| 대상 | 사유 |
|------|------|
| SKILL.md 내 `Skill(skill="ralplan")` 호출 | Planner-Critic Loop로 대체 |
| SKILL.md 내 `Skill(skill="ralph")` 호출 | impl-manager 5조건 루프로 대체 |
| SKILL.md 내 `Skill(skill="ultraqa")` 호출 | Lead 직접 QA + Executor 위임으로 대체 |
| REFERENCE.md 내 모든 `Skill()` 호출 코드 블록 | Agent Teams 패턴으로 전면 교체 |

### 비변경 파일 (명시적 확인)

| 파일/구성요소 | 사유 |
|--------------|------|
| Phase 0 (옵션 파싱 + TeamCreate) | Agent Teams 패턴 100% 사용 중 |
| Phase 2 (설계 문서 생성) | executor/executor-high teammate 패턴 유지 |
| Phase 5 (결과 기반 자동 실행 + TeamDelete) | BKIT teammate 패턴 유지 |
| 자율 발견 모드 (`/auto` 단독) | 5-Tier 발견 체계 변경 없음 |
| 세션 관리 (status/stop/resume) | pdca-status.json 기반 유지 |
| 옵션 시스템 (--worktree, --interactive 등) | 현행 동작 유지 |

---

## 2. SKILL.md v21.0 설계 (250줄 제한)

### 2.1 구조 개요

```
---
(frontmatter: 기존 유지, version만 21.0.0으로 변경)
---
# /auto - PDCA Orchestrator (v21.0)
> 핵심 요약 (기존 유지 + "모든 Phase에서 Agent Teams 단일 패턴 사용" 추가)

## 필수 실행 규칙 (CRITICAL)
  Phase 0: 변경 없음 (~15줄)
  Phase 1: PLAN — HEAVY 변경 (~30줄)
  Phase 2: DESIGN — 변경 없음 (~15줄)
  Phase 3: DO — STANDARD/HEAVY 변경 (~35줄)
  Phase 4: CHECK — 전면 변경 (~40줄)
  Phase 5: ACT — 변경 없음 (~15줄)

## 복잡도 기반 모드 분기 (~20줄)
## 자율 발견 모드 (~15줄)
## 세션 관리 (~10줄)
## 금지 사항 (~5줄)
```

**예상 총 줄 수**: ~240줄 (250줄 제한 이내)

### 2.2 Phase 1 HEAVY 변경 — Planner-Critic Loop

현재 SKILL.md 72행의 `Skill(ralplan)` 호출을 다음으로 교체:

```
**HEAVY (4-5점): Planner-Critic Loop (max 5 iterations)**

critic_feedback = ""
Loop (i=1..5):
  Task(subagent_type="planner", name="planner-{i}", team_name="pdca-{feature}",
       model="sonnet", prompt="계획 수립. Critic 피드백: {critic_feedback}. 출력: docs/01-plan/{feature}.plan.md")
  SendMessage → 결과 수신 → shutdown_request

  Task(subagent_type="architect", name="arch-{i}", team_name="pdca-{feature}",
       model="sonnet", prompt="계획 기술적 타당성 검증. Plan: docs/01-plan/{feature}.plan.md")
  SendMessage → 결과 수신 → shutdown_request

  Task(subagent_type="critic", name="critic-{i}", team_name="pdca-{feature}",
       model="sonnet", prompt="계획 완전성 검토. 첫 줄에 VERDICT: APPROVE 또는 VERDICT: REVISE 출력 필수.")
  SendMessage → 결과 수신 → shutdown_request

  APPROVE → Loop 종료 / REVISE → critic_feedback 업데이트 → 다음 iteration
  5회 초과 → 경고 포함 강제 승인
```

**SKILL.md는 위 흐름을 간결하게 표현 (약 15줄). 상세 prompt 전문은 REFERENCE.md.**

### 2.3 Phase 3 STANDARD/HEAVY 변경 — impl-manager

현재 SKILL.md 124행의 `Skill(ralph)` 호출을 다음으로 교체:

```
**STANDARD/HEAVY: impl-manager teammate (5조건 자체 루프)**

Task(subagent_type="executor[-high]", name="impl-manager",
     team_name="pdca-{feature}", model="sonnet|opus",
     prompt="설계 문서 기반 구현. 5조건 자체 루프 (max 10회). 상세 prompt: REFERENCE.md")
SendMessage(type="message", recipient="impl-manager", content="5조건 구현 루프 시작.")
# Lead는 IMPLEMENTATION_COMPLETED 또는 IMPLEMENTATION_FAILED 메시지만 수신

# HEAVY 병렬 실행: Lead가 독립 작업 2개+ 판단 시 병렬 impl-manager spawn
```

**SKILL.md는 핵심 흐름만 (약 10줄). impl-manager prompt 전문은 REFERENCE.md.**

### 2.4 Phase 4 변경 — Lead 직접 QA + Executor 위임

현재 SKILL.md 139행의 `Skill(ultraqa)` 호출을 다음으로 교체:

```
**Step 4.1: QA 사이클 — Lead 직접 실행 + Executor 수정 위임**

failure_history = []
Loop (max LIGHT:1 / STANDARD:3 / HEAVY:5):
  Lead 직접 실행: ruff check src/ --fix && pytest tests/ -v && npm run build (해당 시)
  실패 시:
    failure_history에 실패 내용 추가
    동일 실패 3회 연속 → QA 조기 종료 + 사용자 알림
    Task(subagent_type="executor", name="fixer-{i}",
         team_name="pdca-{feature}", model="sonnet",
         prompt="QA 실패 수정: {failure_details}")
    SendMessage → 완료 대기 → shutdown_request
  모든 검사 통과 → Step 4.2

**Step 4.2: 이중 검증 — 순차 Teammates**
(현행 v20.1과 동일, Vercel BP를 code-analyzer prompt에 통합)
```

### 2.5 frontmatter 변경

```yaml
---
name: auto
description: PDCA Orchestrator - 통합 자율 워크플로우 (Agent Teams 단일 패턴)
version: 21.0.0
# ... (나머지 동일)
omc_agents:
  - executor
  - executor-high
  - architect
  - planner
  - critic
# 제거: omc_delegate 항목 없음 (ralph, ultrawork, ralplan, ultraqa 호출 제거)
---
```

### 2.6 복잡도 분기 테이블 변경

```
| | LIGHT (0-1) | STANDARD (2-3) | HEAVY (4-5) |
|------|:-----------:|:--------------:|:-----------:|
| Phase 0 | TeamCreate | TeamCreate | TeamCreate |
| Phase 1 | haiku 분석 + haiku 계획 | haiku 분석 + sonnet 계획 | haiku 분석 + Planner-Critic Loop |
| Phase 2 | 스킵 | executor (sonnet) 설계 | executor-high (opus) 설계 |
| Phase 3 | executor (sonnet) | impl-manager (sonnet) | impl-manager (opus) + 병렬 |
| Phase 4 | Lead QA + Architect검증 | Lead QA + 이중검증 | Lead QA + 이중검증 + E2E |
| Phase 5 | haiku 보고서 + TeamDelete | sonnet 보고서 + TeamDelete | 완전 보고서 + TeamDelete |
```

---

## 3. REFERENCE.md v21.0 설계

### 3.1 변경되는 섹션 목록

| # | 섹션 | 변경 유형 | 핵심 내용 |
|:-:|------|:--------:|----------|
| 1 | Agent Teams 운영 규칙 | 수정 | "Skill() 호출 0개" 명시, Agent Teams 단일 패턴 강조 |
| 2 | Phase 1: PLAN Step 1.2 HEAVY | **전면 교체** | Planner-Critic Loop 상세 코드 블록 + Critic prompt 전문 |
| 3 | 복잡도 분기 상세 HEAVY 모드 | 수정 | "Ralplan" → "Planner-Critic Loop" |
| 4 | Phase 3: DO Step 3.1 STANDARD/HEAVY | **전면 교체** | impl-manager prompt 전문, 5조건 루프 상세, 병렬 spawn 패턴 |
| 5 | Phase 3→4 Gate | 수정 | "Ralph 5조건" → "impl-manager COMPLETED/FAILED 판정" |
| 6 | Phase 4: CHECK Step 4.1 | **전면 교체** | Lead 직접 QA + Executor 위임 + failure_history 관리 |
| 7 | Phase 4: CHECK Step 4.2 | 수정 | code-analyzer prompt에 Vercel BP 규칙 동적 주입 추가 |
| 8 | Resume | 수정 | `ralphIteration` → `implManagerIteration` 필드 변경 |
| 9 | /work 통합 안내 v20.1 변경 | 수정 | v21.0 변경 내용 추가 |

### 3.2 변경 없는 섹션

| 섹션 | 사유 |
|------|------|
| Worktree 통합 | --worktree 동작 동일 |
| Phase 2: DESIGN | executor/executor-high 패턴 유지 |
| Phase 5: ACT | BKIT teammate 패턴 유지 |
| --slack 옵션 워크플로우 | 변경 없음 |
| --gmail 옵션 워크플로우 | 변경 없음 |
| --interactive 옵션 워크플로우 | 변경 없음 |

### 3.3 신규 추가 섹션

| 섹션 | 내용 |
|------|------|
| Vercel BP 검증 규칙 | code-analyzer에 주입할 Vercel BP 핵심 규칙 목록 (~500t) |
| impl-manager Prompt 전문 | Phase 3 impl-manager에 전달하는 complete prompt (~80줄) |
| Planner-Critic Loop 상세 | Critic 피드백 처리, 토큰 제한, 강제 승인 메커니즘 |
| Same Failure 3x Early Exit | Phase 4 failure_history 관리 및 조기 종료 로직 |

---

## 4. Phase 1 HEAVY: Planner-Critic Loop 설계

### 4.1 3-Agent 순차 흐름

```
TeamCreate("pdca-{feature}") ← Phase 0에서 이미 생성됨

critic_feedback = ""      # Lead 메모리에서 관리
iteration_count = 0

Loop (max 5 iterations):
  iteration_count += 1

  ┌─ Step A: Planner Teammate ─────────────────────────────────────────┐
  │ Task(subagent_type="planner",                     │
  │      name="planner-{iteration_count}",                             │
  │      team_name="pdca-{feature}",                                   │
  │      model="sonnet",                                               │
  │      prompt="[Phase 1 HEAVY] 계획 수립 (Iteration {iteration_count}/5).   │
  │                                                                    │
  │              작업: {user_request}                                   │
  │              이전 Critic 피드백: {critic_feedback}                  │
  │                                                                    │
  │              계획 문서 작성 후 사용자 확인 단계를 건너뛰세요.       │
  │              Critic teammate가 reviewer 역할을 대신합니다.         │
  │              계획 완료 시 바로 '계획 작성 완료' 메시지를 전송하세요.│
  │                                                                    │
  │              필수 포함: 배경, 구현 범위, 영향 파일, 위험 요소.      │
  │              출력: docs/01-plan/{feature}.plan.md")                 │
  │ SendMessage(type="message", recipient="planner-{i}", content="계획 수립 시작.") │
  │ 결과 수신 대기 → shutdown_request("planner-{i}")                   │
  └────────────────────────────────────────────────────────────────────┘

  ┌─ Step B: Architect Teammate ───────────────────────────────────────┐
  │ Task(subagent_type="architect",                   │
  │      name="arch-{iteration_count}",                                │
  │      team_name="pdca-{feature}",                                   │
  │      model="sonnet",                                               │
  │      prompt="[Phase 1 HEAVY] 기술적 타당성 검증.                   │
  │              Plan 파일: docs/01-plan/{feature}.plan.md             │
  │              검증 항목:                                            │
  │              1. 파일 경로가 실제 존재하는지                         │
  │              2. 의존성 충돌 가능성                                  │
  │              3. 아키텍처 일관성                                     │
  │              4. 성능/보안 우려 사항                                 │
  │              소견을 5줄 이내로 요약하세요.")                         │
  │ SendMessage(type="message", recipient="arch-{i}", content="타당성 검증 시작.") │
  │ 결과 수신 대기 → shutdown_request("arch-{i}")                      │
  └────────────────────────────────────────────────────────────────────┘

  ┌─ Step C: Critic Teammate ──────────────────────────────────────────┐
  │ Task(subagent_type="critic",                      │
  │      name="critic-{iteration_count}",                              │
  │      team_name="pdca-{feature}",                                   │
  │      model="sonnet",                                               │
  │      prompt="[Phase 1 HEAVY] 계획 완전성 검토 (Iteration {iteration_count}/5). │
  │                                                                    │
  │              Plan 파일: docs/01-plan/{feature}.plan.md             │
  │              Architect 소견: {architect_feedback}                   │
  │                                                                    │
  │              당신은 까다로운 코드 리뷰어입니다. 일반적으로 계획은   │
  │              3회 이상 수정이 필요합니다.                            │
  │                                                                    │
  │              반드시 검증:                                           │
  │              - 모든 파일 참조가 실제 존재하는 경로인지              │
  │              - acceptance criteria가 구체적이고 측정 가능한지       │
  │              - 모호한 표현 ('적절히', '필요 시', '가능하면' 등) 여부│
  │              - 누락된 edge case가 없는지                            │
  │                                                                    │
  │              반드시 첫 줄에 VERDICT: APPROVE 또는 VERDICT: REVISE를 │
  │              출력하세요. APPROVE는 위 모든 조건 충족 시에만.        │
  │              REVISE 시 구체적 개선 피드백을 포함하세요.")           │
  │ SendMessage(type="message", recipient="critic-{i}", content="계획 검토 시작.") │
  │ 결과 수신 대기 → shutdown_request("critic-{i}")                    │
  └────────────────────────────────────────────────────────────────────┘

  ┌─ Step D: Lead 판정 ────────────────────────────────────────────────┐
  │ critic_message = Mailbox에서 수신한 critic 메시지                   │
  │ first_line = critic_message의 첫 줄                                │
  │                                                                    │
  │ if "VERDICT: APPROVE" in first_line:                               │
  │     → Loop 종료, Phase 2 진입                                      │
  │ elif "VERDICT: REVISE" in first_line:                              │
  │     → critic_feedback = critic_message에서 VERDICT: 줄 이후 전체   │
  │     → 누적 피드백이 1,500t 초과 시 최신 2회분만 유지               │
  │       (이전: "Iteration {N}: {핵심 요약 1줄}" 형태로 압축)         │
  │     → 다음 iteration                                               │
  │ else:                                                              │
  │     → REVISE로 간주 (안전 기본값)                                  │
  │                                                                    │
  │ if iteration_count >= 5 and not APPROVED:                          │
  │     → Plan 파일에 "WARNING: Critic 5회 반복으로 강제 승인" 주석 추가│
  │     → 강제 APPROVE → Phase 2 진입                                  │
  └────────────────────────────────────────────────────────────────────┘
```

### 4.2 Critic 판정 파싱 규칙

| 항목 | 규칙 |
|------|------|
| 판정 추출 | Critic 메시지의 첫 줄에서 `VERDICT: APPROVE` 또는 `VERDICT: REVISE` 키워드 확인 |
| 키워드 불일치 | 첫 줄에 VERDICT 없으면 REVISE로 간주 |
| 피드백 범위 | REVISE 시 `VERDICT:` 줄 이후 전체 내용을 critic_feedback에 저장 |

### 4.3 피드백 누적 관리

| 조건 | 처리 |
|------|------|
| 피드백 1,500t 이하 | 전체 누적 유지 |
| 피드백 1,500t 초과 | 최신 2회분 전문 유지 + 이전 회차는 "Iteration {N}: {핵심 1줄}" 형태로 압축 |
| 5회 초과 | 경고 메시지와 함께 강제 APPROVE. Plan 파일 상단에 경고 주석 삽입 |

### 4.4 LIGHT/STANDARD 변경 없음

- LIGHT (0-1): Planner teammate (haiku) 단일 실행 — 현행 유지
- STANDARD (2-3): Planner teammate (sonnet) 단일 실행 — 현행 유지

---

## 5. Phase 3 STANDARD/HEAVY: impl-manager 설계

### 5.1 impl-manager Prompt 전문

다음은 Phase 3에서 impl-manager teammate에 전달하는 complete prompt이다. REFERENCE.md에 그대로 포함된다.

```
[Phase 3 DO] Implementation Manager - 5조건 자체 루프

설계 문서: docs/02-design/{feature}.design.md
계획 문서: docs/01-plan/{feature}.plan.md

당신은 Implementation Manager입니다. 설계 문서를 기반으로 코드를 구현하고,
5가지 완료 조건을 모두 충족할 때까지 자동으로 수정/재검증을 반복합니다.

=== 5가지 완료 조건 (ALL 충족 필수) ===

1. TODO == 0: 설계 문서의 모든 구현 항목 완료. 부분 완료 금지.
2. 빌드 성공: 프로젝트 빌드 명령 실행 결과 에러 0개.
   - Python: ruff check src/ --fix (lint 통과)
   - Node.js: npm run build (빌드 통과)
   - 해당 빌드 명령이 없으면 이 조건은 자동 충족.
3. 테스트 통과: 모든 테스트 green.
   - Python: pytest tests/ -v (관련 테스트만 실행 가능)
   - Node.js: npm test 또는 jest
   - 테스트가 없으면 TDD 규칙에 따라 테스트 먼저 작성.
4. 에러 == 0: lint, type check 에러 0개.
   - Python: ruff check + mypy (설정 있을 때)
   - Node.js: tsc --noEmit (TypeScript일 때)
5. 자체 코드 리뷰: 작성한 코드의 아키텍처 일관성 확인.
   - 기존 코드 패턴과 일치하는가?
   - 불필요한 복잡도가 추가되지 않았는가?
   - 보안 취약점(OWASP Top 10)이 없는가?

=== 자체 Iteration 루프 ===

최대 10회까지 반복합니다:
  1. 5조건 검증 실행
  2. 미충족 조건 발견 시 → 해당 문제 수정
  3. 수정 후 → 1번으로 (재검증)
  4. ALL 충족 시 → IMPLEMENTATION_COMPLETED 메시지 전송
  5. 10회 도달 시 → IMPLEMENTATION_FAILED 메시지 전송

=== Iron Law Evidence Chain ===

IMPLEMENTATION_COMPLETED 전송 전 반드시 다음 5단계 증거를 확보하세요:
  1. 모든 테스트 통과 (pytest/jest 실행 결과 캡처)
  2. 빌드 성공 (build command 실행 결과 캡처)
  3. Lint/Type 에러 0개 (ruff/tsc 실행 결과 캡처)
  4. 자체 코드 리뷰 완료 (아키텍처 일관성 확인 내용)
  5. 위 4개 결과를 IMPLEMENTATION_COMPLETED 메시지에 포함

증거 없는 완료 주장은 절대 금지합니다.

=== Zero Tolerance 규칙 ===

다음 행위는 절대 금지합니다:
  - 범위 축소: 설계 문서의 구현 항목을 임의로 제외
  - 부분 완료: "나머지는 나중에" 식의 미완성 제출
  - 테스트 삭제: 실패하는 테스트를 삭제하여 green 만들기
  - 조기 중단: 5조건 미충족 상태에서 COMPLETED 전송
  - 불확실 언어: "should work", "probably fine", "seems to pass" 등 사용 시
    → 해당 항목에 대해 구체적 검증을 추가로 실행

=== Red Flags 자체 감지 ===

다음 패턴을 자체 감지하고 경고하세요:
  - "should", "probably", "seems to" 등 불확실 언어 사용
  - TODO/FIXME/HACK 주석 추가
  - 테스트 커버리지 80% 미만
  - 하드코딩된 값 (매직 넘버, 매직 스트링)
  - 에러 핸들링 누락 (bare except, empty catch)

=== 메시지 형식 ===

[성공 시]
IMPLEMENTATION_COMPLETED: {
  "iterations": {실행 횟수},
  "files_changed": [{변경 파일 목록}],
  "test_results": "{pytest/jest 결과 요약}",
  "build_results": "{빌드 결과 요약}",
  "lint_results": "{lint 결과 요약}",
  "self_review": "{자체 리뷰 요약}"
}

[실패 시]
IMPLEMENTATION_FAILED: {
  "iterations": 10,
  "remaining_issues": [{미해결 문제 목록}],
  "last_attempt": "{마지막 시도 요약}",
  "recommendation": "{권장 조치}"
}

=== Background Operations ===

install, build, test 등 장시간 명령은 background로 실행하세요:
  - npm install → background
  - pip install → background
  - 전체 테스트 suite → foreground (결과 확인 필요)

=== Delegation ===

직접 코드를 작성하세요. 추가 subagent를 spawn하지 마세요.
이 teammate 내부에서의 에이전트 호출은 금지됩니다.
```

### 5.2 5조건 자체 루프 흐름도

```
impl-manager Teammate 내부:

  iteration = 0
  while iteration < 10:
    iteration += 1

    ┌─ 5조건 검증 ─────────────────────────┐
    │ 1. TODO 목록 확인 (설계 vs 구현 비교) │
    │ 2. 빌드 실행                          │
    │ 3. 테스트 실행                        │
    │ 4. Lint/Type check 실행               │
    │ 5. 자체 코드 리뷰                     │
    └───────────────────────────────────────┘
           │
           ├── ALL 충족 → Iron Law Evidence 수집
           │                → IMPLEMENTATION_COMPLETED 메시지 전송
           │                → teammate 종료 대기 (Lead의 shutdown_request)
           │
           └── ANY 미충족 → 미충족 항목 수정
                           → iteration 카운트 증가
                           → 루프 재시작

  iteration == 10 → IMPLEMENTATION_FAILED 메시지 전송
                   → teammate 종료 대기
```

### 5.3 Iron Law Evidence Chain

impl-manager가 `IMPLEMENTATION_COMPLETED` 메시지를 전송하기 위한 필수 증거:

| # | 증거 | 수집 방법 | 메시지 포함 |
|:-:|------|----------|:----------:|
| 1 | 테스트 통과 | `pytest -v` 또는 `jest` 실행 결과 | 결과 요약 |
| 2 | 빌드 성공 | `ruff check` / `npm run build` 실행 결과 | 결과 요약 |
| 3 | Lint/Type 에러 0개 | `ruff` / `tsc --noEmit` 실행 결과 | 결과 요약 |
| 4 | 자체 코드 리뷰 | 변경 파일 diff 검토, 패턴 일관성 확인 | 리뷰 요약 |
| 5 | 증거 통합 | 위 4개를 IMPLEMENTATION_COMPLETED 메시지에 JSON 포함 | 전체 |

### 5.4 Zero Tolerance 규칙

| 금지 행위 | 감지 방법 | 대응 |
|----------|----------|------|
| 범위 축소 | 설계 문서 TODO vs 구현 TODO 비교 | 누락 항목 구현 재개 |
| 부분 완료 | IMPLEMENTATION_COMPLETED 전 5조건 재검증 | 미충족 시 COMPLETED 전송 차단 |
| 테스트 삭제 | `git diff --stat`에서 test 파일 삭제 감지 | 삭제된 테스트 복원 |
| 조기 중단 | 5조건 미충족 상태 확인 | 루프 계속 |
| 불확실 언어 | prompt 내 self-check 규칙 | 구체적 검증 추가 실행 |

### 5.5 IMPLEMENTATION_COMPLETED / FAILED 메시지 형식

**COMPLETED 예시**:
```json
IMPLEMENTATION_COMPLETED: {
  "iterations": 3,
  "files_changed": ["src/agents/config.py", "src/agents/teams/coordinator.py", "tests/test_coordinator.py"],
  "test_results": "12 passed, 0 failed (pytest -v)",
  "build_results": "ruff check: All checks passed",
  "lint_results": "0 errors, 0 warnings",
  "self_review": "기존 BaseTeam 패턴 유지, 신규 coordinator에 의존성 주입 적용"
}
```

**FAILED 예시**:
```json
IMPLEMENTATION_FAILED: {
  "iterations": 10,
  "remaining_issues": ["test_coordinator::test_heavy_mode FAILED - timeout", "ruff E501 in coordinator.py:142"],
  "last_attempt": "timeout 값 300s로 증가했으나 여전히 실패",
  "recommendation": "coordinator.py의 heavy_mode 병렬 처리 로직 재설계 필요"
}
```

### 5.6 병렬 impl-manager (HEAVY ultrawork 대체)

HEAVY 모드에서 독립 작업이 2개 이상일 때 Lead가 판단:

```
# Lead가 설계 문서 분석 → 독립 작업 분할

# 독립 작업 예: "API 구현"과 "UI 구현"이 서로 의존 없음
Task(subagent_type="executor-high", name="impl-api",
     team_name="pdca-{feature}", model="opus",
     prompt="[Phase 3 HEAVY 병렬] API 구현 담당. {impl-manager 전체 prompt}.
             담당 범위: src/api/ 하위 파일만. 다른 경로 수정 금지.")
Task(subagent_type="executor-high", name="impl-ui",
     team_name="pdca-{feature}", model="opus",
     prompt="[Phase 3 HEAVY 병렬] UI 구현 담당. {impl-manager 전체 prompt}.
             담당 범위: src/components/ 하위 파일만. 다른 경로 수정 금지.")

SendMessage(type="message", recipient="impl-api", content="API 구현 시작.")
SendMessage(type="message", recipient="impl-ui", content="UI 구현 시작.")

# 두 impl-manager 모두에서 IMPLEMENTATION_COMPLETED 수신 대기
# 하나라도 FAILED → Lead가 사용자에게 알림
```

**--worktree 병렬 격리** (기존 REFERENCE.md 패턴 유지):
```bash
git worktree add "C:/claude/wt/{feature}-api" "feat/{feature}"
git worktree add "C:/claude/wt/{feature}-ui" "feat/{feature}"
```

### 5.7 자동 재시도/승격/실패 로직

| 조건 | 처리 |
|------|------|
| impl-manager 5조건 루프 내 빌드 실패 | impl-manager 자체 재시도 (10회 한도 내) |
| impl-manager 10회 초과 (FAILED 반환) | Lead가 사용자에게 알림 + 수동 개입 요청 |
| LIGHT에서 빌드 실패 2회 | STANDARD 자동 승격 (impl-manager 재spawn) |
| UltraQA 3사이클 초과 | STANDARD → HEAVY 자동 승격 |
| 영향 파일 5개 이상 감지 | LIGHT/STANDARD → HEAVY 자동 승격 |
| 진행 상태 추적 | `pdca-status.json`의 `implManagerIteration` 필드 |
| 세션 중단 후 resume | `pdca-status.json` 기반 Phase/iteration 복원 |

### 5.8 Resume 동작 (세션 중단 후 재개)

`pdca-status.json`에 추가되는 필드:

```json
{
  "implManagerIteration": 5,
  "implManagerStatus": "in_progress",
  "implManagerRemainingIssues": ["test failure in X", "lint error in Y"]
}
```

Resume 시:
- iteration 5회 미만 → 해당 지점부터 재개
- iteration 5회 이상 소진 → 처음부터 재시작
- impl-manager teammate를 새로 spawn하면서 prompt에 포함:
  ```
  "이전 시도에서 {N}회까지 진행됨. 남은 이슈: {remaining_issues}.
   이전 시도의 변경 사항은 이미 파일에 반영되어 있음. 이어서 진행."
  ```

---

## 6. Phase 4: QA 사이클 설계

### 6.1 Step 4.1: Lead 직접 QA + Executor 수정 위임

```
failure_history = []  # 실패 기록 배열
max_cycles = LIGHT:1 / STANDARD:3 / HEAVY:5
cycle = 0

while cycle < max_cycles:
  cycle += 1

  ┌─ Step A: Lead 직접 QA 실행 ─────────────────────────────────────┐
  │ # Python 프로젝트                                                │
  │ Bash("ruff check src/ --fix")        → lint_result               │
  │ Bash("pytest tests/ -v")             → test_result               │
  │                                                                  │
  │ # Node.js 프로젝트 (해당 시)                                     │
  │ Bash("npm run build")                → build_result              │
  │ Bash("npm test")                     → test_result               │
  │                                                                  │
  │ # TypeScript (해당 시)                                           │
  │ Bash("npx tsc --noEmit")             → type_result               │
  └──────────────────────────────────────────────────────────────────┘
          │
          ├── 모든 검사 통과 → Step 4.2 (이중 검증) 진입
          │
          └── 실패 발견 →
              │
              ┌─ Step B: 실패 기록 + Same Failure 3x 검사 ─────────┐
              │ failure_entry = {                                    │
              │   "cycle": cycle,                                    │
              │   "type": "lint|test|build|type",                    │
              │   "detail": "{실패 상세}",                           │
              │   "signature": "{실패 식별 시그니처}"                │
              │ }                                                    │
              │ failure_history.append(failure_entry)                │
              │                                                      │
              │ # Same Failure 3x 감지                               │
              │ same_failures = [f for f in failure_history           │
              │                  if f.signature == failure_entry.signature] │
              │ if len(same_failures) >= 3:                          │
              │   → QA 사이클 조기 종료                              │
              │   → "동일 실패 3회 감지: {root_cause}" 출력          │
              │   → 사용자에게 수동 개입 요청                        │
              │   → Phase 4 종료 (Phase 5로 미진입)                  │
              └─────────────────────────────────────────────────────┘
              │
              ┌─ Step C: Executor Teammate 수정 위임 ───────────────┐
              │ Task(subagent_type="executor",      │
              │      name="fixer-{cycle}",                           │
              │      team_name="pdca-{feature}",                     │
              │      model="sonnet",                                 │
              │      prompt="QA 실패 수정.                           │
              │              실패 유형: {failure_type}                │
              │              실패 상세: {failure_detail}              │
              │              이전 실패 이력: {failure_history 요약}   │
              │              수정 후 해당 검사를 재실행하여           │
              │              통과를 확인하세요.")                     │
              │ SendMessage(type="message", recipient="fixer-{cycle}",│
              │             content="QA 실패 수정 시작.")            │
              │ 완료 대기 → shutdown_request("fixer-{cycle}")        │
              └─────────────────────────────────────────────────────┘
              │
              └── 다음 cycle로 (Step A 재실행)
```

### 6.2 Same Failure 3x 조기 종료

| 항목 | 설명 |
|------|------|
| 실패 시그니처 | `{failure_type}:{핵심 에러 메시지}` (예: `test:test_coordinator::test_heavy_mode FAILED`) |
| 동일 판정 | 시그니처가 정확히 일치하는 실패가 3회 누적 |
| 조기 종료 출력 | `"[Phase 4] 동일 실패 3회 감지: {signature}. Root cause: {analysis}. 수동 개입 필요."` |
| 후속 처리 | Phase 5로 진입하지 않음. 사용자에게 실패 보고서 제공 |

### 6.3 failure_history[] 관리

```python
# failure_history 구조 (Lead 메모리에서 관리)
failure_history = [
    {
        "cycle": 1,
        "type": "test",
        "detail": "test_coordinator.py::test_heavy_mode - AssertionError: expected 3 got 2",
        "signature": "test:test_coordinator::test_heavy_mode FAILED"
    },
    {
        "cycle": 2,
        "type": "lint",
        "detail": "coordinator.py:142 E501 line too long (145 > 120)",
        "signature": "lint:coordinator.py:142 E501"
    }
]
```

### 6.4 Step 4.2: 이중 검증 (현행 유지 + Vercel BP 통합)

Step 4.2는 현행 v20.1과 동일한 순차 teammate 패턴을 유지한다. 유일한 변경은 code-analyzer prompt에 Vercel BP 규칙을 동적 주입하는 것이다.

```
# 1. Architect teammate (현행 유지)
Task(subagent_type="architect", name="verifier",
     team_name="pdca-{feature}", model="sonnet",
     prompt="구현이 설계 문서와 일치하는지 검증. APPROVE/REJECT 판정.")
# ... shutdown_request

# 2. gap-detector teammate (현행 유지, STANDARD/HEAVY만)
Task(subagent_type="bkit:gap-detector", name="gap-checker",
     team_name="pdca-{feature}", model="sonnet",
     prompt="설계-구현 일치도 분석. 90% 기준.")
# ... shutdown_request

# 3. code-analyzer teammate (Vercel BP 추가, STANDARD/HEAVY만)
Task(subagent_type="bkit:code-analyzer", name="quality-checker",
     team_name="pdca-{feature}", model="sonnet",
     prompt="코드 품질/보안/성능 분석.
             추가 검증 — Vercel BP 규칙 준수 여부 확인:
             {vercel_bp_rules}")     # ← 동적 주입
# ... shutdown_request
```

---

## 7. Vercel BP 통합 설계

### 7.1 통합 방식

**code-analyzer teammate prompt에 동적 주입**

- BKIT plugin 코드 직접 수정 금지 (업데이트 시 덮어쓰임)
- REFERENCE.md에 Vercel BP 규칙 목록 관리 (~500t)
- Phase 4 Step 4.2에서 code-analyzer spawn 시 prompt에 규칙을 문자열로 주입

### 7.2 Vercel BP 핵심 규칙 목록 (REFERENCE.md에 포함)

```
=== Vercel Best Practices 검증 규칙 ===

[React 성능]
- useMemo/useCallback: 실제 re-render 비용이 높은 경우에만 사용. 과도한 메모이제이션 지양.
- key prop: 배열 렌더링 시 안정적 key 사용 (index 금지).
- lazy loading: 큰 컴포넌트는 React.lazy + Suspense.
- state 최소화: 파생 가능한 값은 state 대신 계산.

[Next.js 패턴]
- App Router 우선: pages/ 대신 app/ 디렉토리 사용.
- Server Component 기본: 'use client' 최소화. 인터랙티브 부분만 Client.
- Metadata API: generateMetadata 사용, <Head> 지양.
- Image 최적화: next/image 필수, width/height 명시.
- Font 최적화: next/font 사용, FOUT/FOIT 방지.

[접근성]
- 모든 인터랙티브 요소에 aria-label 또는 accessible name.
- Semantic HTML: div 남용 대신 nav, main, section, article, aside.
- 키보드 네비게이션: 모든 기능이 Tab/Enter로 접근 가능.
- 색상 대비: WCAG 2.1 AA 기준 (4.5:1 이상).

[보안]
- dangerouslySetInnerHTML 사용 시 sanitize 필수.
- 환경 변수: NEXT_PUBLIC_ prefix 없이 서버 전용 비밀 유지.
- CSP 헤더: next.config.js에 Content-Security-Policy 설정.

[성능]
- Bundle size: dynamic import로 코드 분할.
- API Route: Edge Runtime 우선 (해당 시).
- Caching: ISR/SSG 우선, SSR은 필요한 경우만.
```

### 7.3 동적 주입 메커니즘

```
# Phase 4 Step 4.2에서 code-analyzer spawn 시:

vercel_bp_rules = """
[위 7.2 규칙 전체를 문자열로 포함]
"""

# 프로젝트 유형 감지 (Lead가 직접 확인)
has_nextjs = Glob("next.config.*") 결과 존재 여부
has_react = Glob("**/package.json") 내 "react" dependency 존재 여부

# 조건부 주입: Next.js 또는 React 프로젝트일 때만
if has_nextjs or has_react:
    code_analyzer_prompt += f"\n추가 검증 - Vercel BP 규칙:\n{vercel_bp_rules}"
else:
    # 웹 프로젝트가 아닌 경우 Vercel BP 규칙 생략
    pass
```

---

## 8. OMC 기능 이관 검증 체크리스트

PRD Section 13의 26개 기능 각각에 대한 v21.0 구현 위치:

| # | OMC 기능 | 출처 | v21.0 구현 위치 | 구현 방법 |
|:-:|---------|:----:|:---------------:|----------|
| 1 | Self-referential loop | ralph | REFERENCE.md Phase 3 impl-manager prompt | prompt 내 "5조건 미충족 시 자동 재시도" 지시 |
| 2 | PRD Mode (`--prd`) | ralph | SKILL.md Phase 1 옵션 처리 | `--prd` 옵션 시 Planner prompt에 user story 분해 추가 |
| 3 | Iron Law Evidence Chain | ralph | REFERENCE.md impl-manager prompt | "COMPLETED 전 5단계 증거 필수 확보" 섹션 |
| 4 | Red Flags 감지 | ralph | REFERENCE.md impl-manager prompt | "Red Flags 자체 감지" 섹션 |
| 5 | Architect Mandatory Verification | ralph | SKILL.md Phase 4 Step 4.2 | Architect teammate (현행 유지) |
| 6 | Zero Tolerance | ralph | REFERENCE.md impl-manager prompt | "Zero Tolerance 규칙" 섹션 |
| 7 | State Cleanup | ralph, ulw | SKILL.md Phase 5 TeamDelete() | Agent Teams lifecycle로 자동 정리. State 파일 불필요 |
| 8 | Parallel Execution 강제 | ulw | SKILL.md Phase 3 HEAVY | Lead가 독립 작업 판단 시 병렬 impl-manager spawn |
| 9 | Delegation Enforcement | ulw | OMC CLAUDE.md Rule 3 (현행 유지) | impl-manager prompt에 "직접 코드 수정, subagent 금지" |
| 10 | Background Operations | ulw | REFERENCE.md impl-manager prompt | "Background Operations" 섹션 |
| 11 | Persistence Enforcement | ulw, ralph | **제거** | Agent Teams teammate는 Lead의 shutdown_request 없이 종료 불가. impl-manager 자체 iteration으로 대체 |
| 12 | Smart Model Routing | ralph, ulw | SKILL.md 복잡도 분기 테이블 | Agent Teams `model` 파라미터로 직접 제어 (현행 유지) |
| 13 | 3-Agent Consensus Loop | ralplan | SKILL.md Phase 1 HEAVY + REFERENCE.md | Planner-Critic Loop 설계 (섹션 4) |
| 14 | Plan Mode Phase 3.5 bypass | ralplan | REFERENCE.md Planner prompt | "사용자 확인 단계 skip, Critic이 reviewer" 지시 |
| 15 | Critic Mandatory Rule | ralplan | SKILL.md Phase 1 HEAVY | "Critic APPROVE 필수" 완료 조건 |
| 16 | Critic 높은 기준치 | ralplan | REFERENCE.md Critic prompt | "까다로운 리뷰어, 3회 이상 REVISE 예상" 지시 |
| 17 | Quality Gates 4개 | ralplan | REFERENCE.md Planner prompt | 4개 gate 조건 명시 (파일 참조 유효, criteria 구체, 범위 명확, 모호성 배제) |
| 18 | Force approval with warning | ralplan | SKILL.md Phase 1 HEAVY | "5회 초과 시 경고 포함 강제 승인" |
| 19 | Autonomous QA Cycling | ultraqa | SKILL.md Phase 4 Step 4.1 | Lead 직접 QA + Executor 수정 위임 |
| 20 | Goal Type Parsing (6종) | ultraqa | REFERENCE.md Phase 4 | Lead가 프로젝트 유형에 맞는 QA 명령 자동 선택 |
| 21 | Same Failure 3x Early Exit | ultraqa | SKILL.md + REFERENCE.md Phase 4 | failure_history[] 관리 + 3회 조기 종료 |
| 22 | Custom Pattern Matching | ultraqa | REFERENCE.md Phase 4 | `--custom` 옵션으로 임의 성공 패턴 정의 |
| 23 | Interactive Testing | ultraqa | REFERENCE.md Phase 4 | `--interactive` 옵션 시 qa-tester teammate |
| 24 | Observability 포맷 | ultraqa | REFERENCE.md 전역 규칙 | 모든 teammate prompt에 "[Phase N Step M]" 형식 규약 |
| 25 | failures[] 추적 | ultraqa | SKILL.md + REFERENCE.md Phase 4 | Lead가 failure_history[] 관리 |
| 26 | Notepad Memory | hook | REFERENCE.md Agent Teams 운영 규칙 | `.omc/notepad.md` 직접 관리 가능 (현행 hook 유지) |

### HIGH 누락 위험 항목 검증

| # | 기능 | 누락 위험 | 검증 방법 |
|:-:|------|:--------:|----------|
| 1 | Self-referential loop | HIGH | impl-manager가 10회 iteration을 실제로 반복하는지 테스트 |
| 3 | Iron Law Evidence Chain | HIGH | IMPLEMENTATION_COMPLETED 메시지에 5단계 증거 포함 여부 확인 |
| 11 | Persistence Enforcement | HIGH | impl-manager teammate가 중간에 멈추지 않는지 확인 |
| 13 | 3-Agent Consensus Loop | HIGH | Planner-Critic 5회 iteration 동작 확인 |
| 14 | Plan Mode bypass | HIGH | Critic이 reviewer 역할 수행하는지 확인 |
| 16 | Critic 높은 기준치 | HIGH | Critic이 첫 iteration에서 APPROVE하지 않는 경향 확인 |
| 21 | Same Failure 3x | HIGH | 동일 실패 3회 시 조기 종료 동작 확인 |

---

## 9. State 파일 제거 설계

### 9.1 제거 대상 State 파일

| State 파일 | 현재 용도 | v21.0 대체 |
|-----------|----------|-----------|
| `.omc/ralph-state.json` | Ralph 루프 active/iteration 추적 | 불필요. impl-manager 자체 iteration. `pdca-status.json`의 `implManagerIteration`으로 대체 |
| `.omc/ralph-verification.json` | Ralph 검증 pending 상태 | 불필요. Agent Teams lifecycle으로 대체 |
| `.omc/ultrawork-state.json` | Ultrawork active/delegation 추적 | 불필요. Agent Teams lifecycle으로 대체 |
| `~/.claude/ultrawork-state.json` | Ultrawork global active 상태 | 불필요. Agent Teams lifecycle으로 대체 |

### 9.2 session_cleanup.py 변경사항

현재 `session_cleanup.py`에는 ralph/ultrawork state 파일을 직접 정리하는 코드가 없다 (OMC의 `persistent-mode.mjs` hook과 `session_init.py`에서 처리). 따라서 session_cleanup.py의 코드 변경은 최소한이다.

**변경 내용**:
1. `TEMP_PATTERNS` 목록에서 `ralph-counter.txt`, `ralph-test-*.md` 패턴 제거 (더 이상 생성되지 않음)
2. `cleanup_stale_agent_teams()` 함수는 유지 (Agent Teams 정리 로직은 v21.0에서도 필요)
3. 향후 방지 주석 추가: `# v21.0: ralph/ultrawork state 파일은 더 이상 사용하지 않음. Agent Teams lifecycle으로 대체.`

**session_cleanup.py 변경 diff**:
```python
# 변경 전
TEMP_PATTERNS = [
    "temp_*.py",
    "temp_*.txt",
    "temp_*.md",
    "*.tmp",
    "*.bak",
    "tmpclaude-*",
    "ralph-counter.txt",     # ← 제거
    "ralph-test-*.md",       # ← 제거
]

# 변경 후
TEMP_PATTERNS = [
    "temp_*.py",
    "temp_*.txt",
    "temp_*.md",
    "*.tmp",
    "*.bak",
    "tmpclaude-*",
    # v21.0: ralph/ultrawork state 파일은 Agent Teams lifecycle으로 대체됨
]
```

### 9.3 Stop Hook 관련 변경

v21.0에서 ralph/ultrawork state 파일이 생성되지 않으므로, OMC의 `persistent-mode.mjs` stop hook에서 해당 경로를 읽는 코드가 자연스럽게 무효화된다:

| persistent-mode.mjs 경로 | v20.1 | v21.0 |
|--------------------------|-------|-------|
| Priority 1: `ralph-state.json` active 검사 | 파일이 생성되어 차단 가능 | 파일이 생성되지 않음 → 검사 skip |
| Priority 2: `ultrawork-state.json` active 검사 | 파일이 생성되어 차단 가능 | 파일이 생성되지 않음 → 검사 skip |
| Priority 3: `~/.claude/todos/*.json` 검사 | Agent Teams와 무관 (별도 경로) | 동일 (변경 없음) |

**결론**: OMC plugin 코드를 수정하지 않아도 state 파일 미생성으로 Stop Hook 충돌이 자연 해소된다.

### 9.4 pdca-status.json 필드 변경

```json
// v20.1 필드
{
  "ralphIteration": 5,
  "ralphStatus": "in_progress"
}

// v21.0 필드 (대체)
{
  "implManagerIteration": 5,
  "implManagerStatus": "in_progress",
  "implManagerRemainingIssues": ["issue1", "issue2"]
}
```

---

## 10. 08-skill-routing.md 변경 설계

### 10.1 스킬 매핑 테이블 업데이트

**변경 전**:
```
| 로컬 스킬 | OMC 위임 | 서브커맨드 |
|-----------|----------|-----------|
| `/auto` | - (직접 실행, PDCA orchestrator) | Phase 1-5, --gdocs, --mockup, --daily 등 |
| `/check` | `ultraqa` | --fix, --e2e, --perf, --security, --all |
| `/parallel` | `ultrawork` | dev, test, review, research, check |
```

**변경 후**:
```
| 로컬 스킬 | OMC 위임 | 서브커맨드 |
|-----------|----------|-----------|
| `/auto` | - (직접 실행, PDCA orchestrator, Agent Teams 단일 패턴) | Phase 1-5, --gdocs, --mockup, --daily 등 |
| `/check` | `ultraqa` | --fix, --e2e, --perf, --security, --all |
| `/parallel` | `ultrawork` | dev, test, review, research, check |
```

**핵심 변경**: `/auto`의 설명에 "Agent Teams 단일 패턴" 추가. `/check`과 `/parallel`은 독립 스킬이므로 OMC 위임 유지 (이들은 `/auto` 외부에서 독립 호출되며, v21.0의 변경 범위 밖).

### 10.2 에이전트 티어 라우팅 변경

변경 없음. 기존 LOW/MEDIUM/HIGH 3-tier 라우팅 유지.

### 10.3 `/auto` 내부 호출 제거 명시

08-skill-routing.md에 다음 주석 추가:

```
## /auto 내부 OMC 호출 (v21.0)

v21.0부터 `/auto`는 내부에서 OMC Skill() 호출을 사용하지 않습니다.
모든 Phase가 Agent Teams 단일 패턴으로 실행됩니다.

| 이전 호출 | v21.0 대체 | Phase |
|----------|-----------|:-----:|
| `Skill(ralplan)` | Planner-Critic Loop (Agent Teams) | 1 HEAVY |
| `Skill(ralph)` | impl-manager 5조건 루프 (Agent Teams) | 3 STD/HEAVY |
| `Skill(ultraqa)` | Lead 직접 QA + Executor 위임 | 4 |

> `/check`(`ultraqa`), `/parallel`(`ultrawork`)은 독립 스킬이므로 OMC 위임 유지.
> `/auto` 내부에서만 호출이 제거됨.
```

---

## 11. 테스트 전략

### 11.1 LIGHT 모드 테스트 시나리오

```
작업: "README.md에 설치 방법 추가"
예상 복잡도: 0-1점 (LIGHT)

검증 포인트:
- [ ] Phase 0: TeamCreate 성공
- [ ] Phase 1: Planner (haiku) 단일 실행, Critic Loop 미실행
- [ ] Phase 2: 스킵 (설계 문서 미생성)
- [ ] Phase 3: Executor (sonnet) 단일 실행, impl-manager 미사용
- [ ] Phase 4 Step 4.1: Lead 직접 QA 1회 사이클
- [ ] Phase 4 Step 4.2: Architect (sonnet) 검증만 (gap-detector 스킵)
- [ ] Phase 5: haiku 보고서 생성 + TeamDelete
- [ ] Skill() 호출 0건 확인
- [ ] State 파일 생성 0건 확인
- [ ] 전체 Phase 0→5 완주
```

### 11.2 STANDARD 모드 테스트 시나리오

```
작업: "lib/slack에 메시지 검색 기능 추가"
예상 복잡도: 2-3점 (STANDARD)

검증 포인트:
- [ ] Phase 0: TeamCreate 성공
- [ ] Phase 1: Planner (sonnet) 단일 실행, Critic Loop 미실행
- [ ] Phase 2: Executor (sonnet) 설계 문서 생성
- [ ] Phase 3: impl-manager (sonnet) 5조건 자체 루프
  - [ ] IMPLEMENTATION_COMPLETED 메시지에 5단계 증거 포함
  - [ ] Lead context에 중간 iteration 미수신 (최종 메시지만)
- [ ] Phase 4 Step 4.1: Lead 직접 QA 3회 사이클
  - [ ] 실패 시 Executor teammate 수정 위임
  - [ ] failure_history[] 정상 관리
- [ ] Phase 4 Step 4.2: Architect → gap-detector → code-analyzer 순차
  - [ ] code-analyzer prompt에 Vercel BP 미포함 (Python 프로젝트)
- [ ] Phase 5: 보고서 생성 + TeamDelete
- [ ] Skill() 호출 0건 확인
- [ ] ralph-state.json 미생성 확인
- [ ] ultrawork-state.json 미생성 확인
```

### 11.3 HEAVY 모드 테스트 시나리오

```
작업: "src/agents/teams에 research_team.py 전면 리팩토링"
예상 복잡도: 4-5점 (HEAVY)

검증 포인트:
- [ ] Phase 0: TeamCreate 성공
- [ ] Phase 1: Planner-Critic Loop 실행
  - [ ] Planner → Architect → Critic 순차 3회 이상 반복
  - [ ] Critic VERDICT: REVISE → 피드백 누적
  - [ ] Critic VERDICT: APPROVE → Loop 종료
  - [ ] (5회 초과 시) 경고 포함 강제 승인
- [ ] Phase 2: Executor-high (opus) 설계 문서 생성
- [ ] Phase 3: impl-manager (opus) 5조건 자체 루프
  - [ ] 독립 작업 2개+ 시 병렬 impl-manager spawn (TaskList에서 확인)
  - [ ] IMPLEMENTATION_COMPLETED/FAILED 메시지 형식 준수
- [ ] Phase 4 Step 4.1: Lead 직접 QA 5회 사이클
  - [ ] Same Failure 3x 조기 종료 동작 확인 (해당 시)
- [ ] Phase 4 Step 4.2: Architect → gap-detector → code-analyzer (opus) 순차
- [ ] Phase 4 Step 4.3: E2E (Playwright 존재 시)
- [ ] Phase 5: 완전 보고서 + TeamDelete
- [ ] Skill() 호출 0건 확인
- [ ] State 파일 미생성 확인
- [ ] Stop Hook 충돌 0건 확인
```

### 11.4 Edge Case 테스트

| Edge Case | 검증 방법 |
|-----------|----------|
| impl-manager 10회 초과 (FAILED) | 의도적으로 불가능한 작업 부여 → FAILED 메시지 수신 확인 |
| Same Failure 3x | 의도적으로 수정 불가능한 실패 유발 → 3회 후 조기 종료 확인 |
| Critic 5회 초과 강제 승인 | 극도로 까다로운 Critic prompt → 강제 승인 메시지 확인 |
| 세션 중단 후 resume | Phase 3 중간에 세션 종료 → `/auto resume`으로 재개 확인 |
| LIGHT → STANDARD 자동 승격 | 빌드 실패 2회 유발 → STANDARD 모드 전환 확인 |
| --worktree + HEAVY 병렬 | worktree 격리된 병렬 impl-manager 실행 확인 |
| 옵션 동작 확인 | `--dry-run`, `--eco`, `--interactive`, `--worktree` 각 1회 |

---

## 12. 마이그레이션 단계별 변경 diff 요약

PRD Section 9의 8단계 마이그레이션에서 각 파일의 구체적 변경 내용:

### 단계 1: SKILL.md Phase 1 HEAVY 수정

| 파일 | 변경 위치 | 변경 내용 |
|------|----------|----------|
| `SKILL.md` | 72행 복잡도 분기 테이블 | `Skill(ralplan)` → `Planner-Critic Loop (max 5 iter)` |
| `SKILL.md` | 77행 HEAVY 코드 블록 | `Skill(skill="ralplan", ...)` → 3-agent Loop 간결 코드 블록 (~15줄) |

**위험도**: LOW (독립 변경, Phase 3/4에 영향 없음)

### 단계 2: SKILL.md Phase 4 Step 4.1 수정

| 파일 | 변경 위치 | 변경 내용 |
|------|----------|----------|
| `SKILL.md` | 137-143행 Step 4.1 | `Skill(skill="ultraqa")` → Lead 직접 QA + Executor 위임 코드 블록 (~20줄) |
| `SKILL.md` | 복잡도 분기 테이블 Phase 4 행 | `UltraQA + ...` → `Lead QA + ...` |

**위험도**: LOW (독립 변경)

### 단계 3: SKILL.md Phase 3 STANDARD/HEAVY 수정

| 파일 | 변경 위치 | 변경 내용 |
|------|----------|----------|
| `SKILL.md` | 119-135행 Phase 3 전체 | `Skill(skill="ralph", ...)` → impl-manager 코드 블록 (~15줄) |
| `SKILL.md` | 복잡도 분기 테이블 Phase 3 행 | `Ralph (sonnet/opus)` → `impl-manager (sonnet/opus)` |

**위험도**: HIGH (핵심 변경. 5조건 루프의 정확한 재구현이 필수)

### 단계 4: REFERENCE.md 전면 업데이트

| 파일 | 변경 섹션 | 변경 내용 |
|------|----------|----------|
| `REFERENCE.md` | Phase 1 Step 1.2 HEAVY | Ralplan 코드 블록 → Planner-Critic Loop 상세 (~60줄) |
| `REFERENCE.md` | Phase 3 Step 3.1 STANDARD/HEAVY | Ralph 코드 블록 → impl-manager prompt 전문 (~80줄) |
| `REFERENCE.md` | Phase 3→4 Gate | Ralph 5조건 → impl-manager COMPLETED/FAILED |
| `REFERENCE.md` | Phase 4 Step 4.1 | UltraQA 코드 블록 → Lead QA + failure_history (~40줄) |
| `REFERENCE.md` | Phase 4 Step 4.2 | code-analyzer prompt에 Vercel BP 동적 주입 추가 (~20줄) |
| `REFERENCE.md` | Resume | `ralphIteration` → `implManagerIteration` |
| `REFERENCE.md` | 신규: Vercel BP 규칙 | 핵심 규칙 목록 (~30줄) |
| `REFERENCE.md` | 신규: Same Failure 3x | failure_history 관리 + 조기 종료 로직 (~20줄) |
| `REFERENCE.md` | v20.1 변경 내용 | v21.0 변경 내용 추가 (~10줄) |

**위험도**: MEDIUM (문서 변경이지만 실행 코드 블록 포함)

### 단계 5: OMC CLAUDE.md 스킬 라우팅 정리

| 파일 | 변경 위치 | 변경 내용 |
|------|----------|----------|
| `~/.claude/CLAUDE.md` | Mandatory Skill Invocation 테이블 | "ralph", "ultrawork" 키워드 시 `/auto` 내부 Agent Teams로 처리됨을 명시 (기존 `ralph`/`ultrawork` 키워드 → `/auto` 리다이렉트 유지) |

**위험도**: LOW (기존 키워드 트리거 동작은 유지, 내부 실행만 변경)

**참고**: `~/.claude/CLAUDE.md`는 `/auto` 외부에서의 `ralph`, `ultrawork` 키워드 트리거를 여전히 처리해야 하므로, 키워드 매핑 자체는 유지한다. 변경은 설명 텍스트만.

### 단계 6: skill-routing.md 업데이트

| 파일 | 변경 위치 | 변경 내용 |
|------|----------|----------|
| `08-skill-routing.md` | 스킬 매핑 테이블 `/auto` 행 | "Agent Teams 단일 패턴" 추가 |
| `08-skill-routing.md` | 신규 섹션 | "/auto 내부 OMC 호출 (v21.0)" 섹션 추가 (~15줄) |

**위험도**: LOW

### 단계 7: session_cleanup.py 정리

| 파일 | 변경 위치 | 변경 내용 |
|------|----------|----------|
| `session_cleanup.py` | 17-26행 TEMP_PATTERNS | `ralph-counter.txt`, `ralph-test-*.md` 제거 + 주석 추가 |

**위험도**: LOW

### 단계 8: 통합 테스트

| 테스트 | 대상 | 검증 |
|--------|------|------|
| LIGHT 1건 | 간단한 파일 수정 | Phase 0→5 완주, Skill() 0건 |
| STANDARD 1건 | 중간 기능 추가 | impl-manager 5조건 루프, failure_history 동작 |
| HEAVY 1건 | 복잡 리팩토링 | Planner-Critic Loop, 병렬 impl-manager, E2E |

**위험도**: MEDIUM (실제 실행이므로 예상치 못한 문제 발생 가능)

### 마이그레이션 순서 의존성

```
단계 1 (Phase 1) ─┐
                   ├── 단계 4 (REFERENCE.md) ── 단계 5 (OMC CLAUDE.md)
단계 2 (Phase 4) ─┤                            ── 단계 6 (skill-routing.md)
                   │                            ── 단계 7 (session_cleanup.py)
단계 3 (Phase 3) ─┘
                                                ── 단계 8 (통합 테스트, 모든 단계 완료 후)
```

- 단계 1, 2, 3은 독립 실행 가능 (서로 다른 Phase 수정)
- 단계 4는 단계 1-3 완료 후 실행 (REFERENCE.md는 SKILL.md와 동기화 필요)
- 단계 5, 6, 7은 단계 4 이후 병렬 실행 가능
- 단계 8은 모든 단계 완료 후 순차 실행

---

## 부록 A: SKILL.md v21.0 전체 구조 스켈레톤

```yaml
---
name: auto
description: PDCA Orchestrator - 통합 자율 워크플로우 (Agent Teams 단일 패턴)
version: 21.0.0
triggers:
  keywords: ["/auto", "auto", "autopilot", "ulw", "ultrawork", "ralph", "/work", "work"]
model_preference: opus
auto_trigger: true
omc_agents: [executor, executor-high, architect, planner, critic]
bkit_agents: [gap-detector, pdca-iterator, code-analyzer, report-generator]
---

# /auto - PDCA Orchestrator (v21.0)
> 핵심: Agent Teams 단일 패턴. Skill() 호출 0개. State 파일 의존 0개.

## 필수 실행 규칙 (CRITICAL)

### Phase 0: 옵션 파싱 + 모드 결정 + 팀 생성
(변경 없음 — 현행 v20.1 유지)

### Phase 1: PLAN
Step 1.0: 병렬 explore (변경 없음)
Step 1.1: 복잡도 판단 (변경 없음)
Step 1.2: 계획 수립
  LIGHT/STANDARD: (변경 없음)
  HEAVY: Planner-Critic Loop (max 5 iter) ← 신규
Step 1.3: 이슈 연동 (변경 없음)

### Phase 2: DESIGN
(변경 없음 — 현행 v20.1 유지)

### Phase 3: DO
Step 3.0: 옵션 처리 (변경 없음)
Step 3.1: 구현 실행
  LIGHT: executor teammate (변경 없음)
  STANDARD/HEAVY: impl-manager teammate (5조건 자체 루프) ← 신규
  HEAVY 병렬: 병렬 impl-manager teammates ← 신규

### Phase 4: CHECK
Step 4.1: QA 사이클 — Lead 직접 실행 + Executor 수정 위임 ← 신규
Step 4.2: 이중 검증 — Architect + gap-detector + code-analyzer (Vercel BP 통합) ← 수정
Step 4.3: E2E (변경 없음)
Step 4.4: TDD 커버리지 (변경 없음)

### Phase 5: ACT
(변경 없음 — 현행 v20.1 유지)

## 복잡도 기반 모드 분기
(테이블 업데이트: Ralplan→Planner-Critic, Ralph→impl-manager, UltraQA→Lead QA)

## 자율 발견 모드
(변경 없음)

## 세션 관리
(변경 없음, ralphIteration→implManagerIteration 필드명 변경만)

## 금지 사항
(기존 + "Skill() 호출 금지" 추가)
```

---

## 부록 B: 롤백 전략

| 항목 | 롤백 방법 |
|------|----------|
| SKILL.md | `git checkout v20.1 -- .claude/skills/auto/SKILL.md` |
| REFERENCE.md | `git checkout v20.1 -- .claude/skills/auto/REFERENCE.md` |
| 08-skill-routing.md | `git checkout v20.1 -- .claude/rules/08-skill-routing.md` |
| session_cleanup.py | `git checkout v20.1 -- .claude/hooks/session_cleanup.py` |
| OMC Skill() | 코드에 남아 있으므로 롤백 시 자동 복구 |
| State 파일 정리 코드 | 제거하지 않고 주석 처리했으므로 주석 해제로 복구 |

**롤백 판단 기준**: 통합 테스트 (단계 8)에서 STANDARD 모드 Phase 0→5 완주 실패 시 전체 롤백.
