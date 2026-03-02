---
name: auto
description: PDCA Orchestrator - 통합 자율 워크플로우 (Agent Teams 단일 패턴)
version: 23.0.0
triggers:
  keywords:
    - "/auto"
    - "auto"
    - "autopilot"
    - "/work"
model_preference: opus
auto_trigger: true
agents:
  - executor
  - executor-high
  - architect
  - planner
  - critic
  - qa-tester
  - build-fixer
  - security-reviewer
  - designer
  - code-reviewer
  - writer
---

# /auto - PDCA Orchestrator (v23.0)

> **핵심**: `/auto "작업"` = Phase 0-4 자동 진행. `/auto` 단독 = 자율 발견 모드. `/work`는 `/auto`로 통합됨.
> **Agent Teams 단일 패턴**: TeamCreate → Task(team_name+name) → SendMessage → TeamDelete. Skill() 호출 0개.
> **코드 블록/상세 prompt**: `REFERENCE.md` 참조. 이 파일은 판단 로직과 흐름만 기술.

---

## Phase 0→4 실행 흐름

```
  Phase 0        Phase 1           Phase 2            Phase 3          Phase 4
  INIT    ──→    PLAN       ──→    BUILD       ──→    VERIFY    ──→    CLOSE
  옵션 파싱       PRD 생성         구현 실행           QA 사이클        보고서
  팀 생성         사전 분석         코드 리뷰           E2E 검증         팀 정리
  복잡도 판단     계획+설계 수립    Architect Gate      최종 판정         커밋
```

---

## Phase 0: INIT (옵션 + 팀 + 복잡도)

### 옵션

| 옵션 | 효과 |
|------|------|
| `--skip-prd` | Phase 1 PRD 스킵 |
| `--skip-analysis` | Phase 1 사전 분석 스킵 |
| `--no-issue` | 이슈 연동 스킵 |
| `--strict` | E2E 1회 실패 즉시 중단 |
| `--skip-e2e` | E2E 검증 전체 스킵 |
| `--dry-run` | 판단만 출력 |
| `--eco` | LIGHT 강제 (전체 sonnet) |
| `--worktree` | feature worktree에서 작업 |
| `--mockup [파일]` | Phase 2 진입 전 실행. 상세: mockup-hybrid SKILL.md |

### 팀 생성 (MANDATORY)

`TeamCreate(team_name="pdca-{feature}")`. 실패 시 `TeamDelete()` → 재시도 1회. 재실패 시 중단.

### 복잡도 판단 (5점 만점)

상세 채점 기준: `REFERENCE.md`

| 점수 | 모드 | 특성 |
|:----:|:----:|------|
| 0-1 | LIGHT | 단일 실행, QA 1회, 최소 검증 |
| 2-3 | STANDARD | 자체 루프, QA 3회, 이중 검증 |
| 4-5 | HEAVY | Planner-Critic, QA 5회, 전체 검증 |

**자동 승격**: LIGHT→STANDARD (빌드 실패 2회 or 영향 파일 5+). STANDARD→HEAVY (QA 3사이클 초과 or 영향 파일 5+).

### 커밋 정책

Phase 완료 후 `git status --short` 확인 → 변경사항 있으면 커밋.

| 트리거 | 커밋 메시지 패턴 |
|--------|----------------|
| Phase 2 Architect APPROVE | `feat({feature}): 구현 완료` |
| Phase 3 최종 검증 통과 | `fix({feature}): QA 수정사항 반영` |
| Phase 4 보고서 생성 | `docs(report): {feature} PDCA 완료 보고서` |
| 조기 종료 | `wip({feature}): 진행 중 변경사항 보존` |

---

## Phase 1: PLAN (PRD → 분석 → 계획+설계)

### Step 1.1: PRD (요구사항 문서화)

`--skip-prd`로 스킵 가능. 상세 prompt/템플릿: `REFERENCE.md`

1. `docs/00-prd/` 기존 PRD 탐색
2. prd-writer teammate (executor, opus) → PRD 생성/수정
3. **사용자 승인** (AskUserQuestion, max 수정 3회)
4. 산출물: `docs/00-prd/{feature}.prd.md`

### Step 1.2: 사전 분석

`--skip-analysis`로 스킵 가능.

병렬 explore(haiku) x2: 문서 탐색 + 이슈 탐색. 결과 5줄 요약.

### Step 1.3: 계획 수립 (Graduated Plan Review)

| 모드 | 실행 |
|------|------|
| LIGHT | planner (sonnet) + Lead Quality Gate |
| STANDARD | planner (opus) + Critic-Lite (opus) 단일 검토 |
| HEAVY | Planner-Critic Loop (opus, max 5회) |

**Lead Quality Gate** (LIGHT): plan 파일 존재+내용 있음, 파일 경로 1개+ 언급. 미충족 시 1회 재요청.
**Critic-Lite** (STANDARD): QG1-QG4 검증 → APPROVE/REVISE. REVISE 시 1회 수정.
**Planner-Critic Loop** (HEAVY): Planner → Architect 타당성 → Critic QG1-QG4 → 반복. 상세: `REFERENCE.md`

산출물: `docs/01-plan/{feature}.plan.md`

### Step 1.4: 설계 통합 (STANDARD/HEAVY만)

LIGHT는 스킵. STANDARD/HEAVY: 계획 문서에 **아키텍처 결정 섹션** 포함 (별도 design.md 불필요).
필수 포함: 컴포넌트 구조, 데이터 흐름, 인터페이스 설계, 위험 요소.

> **Plan→Build Gate** (STANDARD/HEAVY): 4개 필수 섹션 확인 (배경, 구현 범위, 영향 파일, 위험 요소). 미충족 시 planner 1회 보완.

### Step 1.5: 이슈 연동

`--no-issue`로 스킵. 없으면 생성, 있으면 코멘트.

---

## Phase 2: BUILD (구현 → 코드 리뷰 → Architect Gate)

> **핵심 변경 (v23.0)**: Code Review가 BUILD 내부에 통합. 구현 완료 즉시 리뷰 → 수정 → Architect 판정.

### Step 2.0: 옵션 처리 (구현 진입 전)

| 옵션 | 처리 | 옵션 | 처리 |
|------|------|------|------|
| `--gdocs` | prd-sync | `--slack <채널>` | Slack 분석 |
| `--mockup [파일]` | ASCII→형식 변환 | `--gmail` | Gmail 분석 |
| `--debate` | ultimate-debate | `--daily` | daily |
| `--research` | research | `--interactive` | Phase별 승인 |

옵션 실패 시: 에러 출력, **절대 조용히 스킵 금지**. 상세: `REFERENCE.md`

### Step 2.1: 구현

| 모드 | 실행 방식 |
|------|----------|
| LIGHT | executor (opus) — 단일 실행, TDD 필수 |
| STANDARD | impl-manager (opus) — 5조건 자체 루프 (max 10회) |
| HEAVY | impl-manager (opus) — 5조건 자체 루프 + 병렬 가능 |

**impl-manager 5조건** (STANDARD/HEAVY — 모든 조건 충족 시 IMPLEMENTATION_COMPLETED):

| # | 조건 | 검증 방법 |
|:-:|------|----------|
| 1 | TODO == 0 | plan.md 체크리스트 전체 완료 |
| 2 | 빌드 성공 | 빌드 명령 exit code 0 |
| 3 | 테스트 통과 | pytest/jest exit code 0 |
| 4 | 에러 == 0 | lint + type check 클린 |
| 5 | 자체 코드 리뷰 | 명백한 결함 없음 확인 |

상세 impl-manager prompt: `REFERENCE.md`

### Step 2.2: Code Review (STANDARD/HEAVY 필수)

구현 완료 후 **즉시** code-reviewer (sonnet) 실행. Vercel BP 규칙 동적 주입 (React/Next.js 시).

| 판정 | 처리 |
|------|------|
| APPROVE | Step 2.3 Architect Gate 진입 |
| REVISE + 수정 목록 | executor로 수정 → code-reviewer 재검토 (max 2회) |

> LIGHT 모드: code-reviewer 스킵. Step 2.1 완료 후 바로 Phase 3 진입.

### Step 2.3: Architect Verification Gate (STANDARD/HEAVY 필수)

architect (opus, READ-ONLY) → 구현이 Plan 요구사항과 일치하는지 외부 검증.

| VERDICT | 처리 |
|---------|------|
| APPROVE | 유의미 변경 커밋 → Phase 3 진입 |
| REJECT + DOMAIN | Step 2.4 Domain-Smart Fix |

2회 REJECT → 사용자 알림 후 Phase 3 진입 허용.

### Step 2.4: Domain-Smart Fix (Architect REJECT 시)

| DOMAIN | 에이전트 |
|--------|---------|
| UI, component, style | designer |
| build, compile, type | build-fixer |
| test, coverage | executor |
| security | security-reviewer |
| 기타 | executor |

수정 완료 → Step 2.3 Architect 재검증 (max 2회).

---

## Phase 3: VERIFY (QA → E2E → 최종 판정)

### Step 3.1: QA 사이클

| 모드 | QA 횟수 | 실패 시 |
|------|:-------:|---------|
| LIGHT | 1회 | 보고만 (STANDARD 승격 검토) |
| STANDARD | max 3회 | Architect 진단 → Domain-Smart Fix → 재실행 |
| HEAVY | max 5회 | Architect 진단 → Domain-Smart Fix → 재실행 |

QA Runner (sonnet): 6종 검증 (lint, type, unit, integration, build, security). 상세: `REFERENCE.md`

**4종 Exit Conditions:**

| 우선순위 | 조건 | 처리 |
|:--------:|------|------|
| 1 | Environment Error | 즉시 중단 + 환경 문제 보고 |
| 2 | Same Failure 3x | 조기 종료 + root cause 보고 |
| 3 | Max Cycles | 미해결 이슈 보고 |
| 4 | Goal Met | Step 3.2 진입 |

### Step 3.2: E2E 검증 (STANDARD/HEAVY + 프레임워크 존재 시)

`--skip-e2e`로 스킵. `playwright.config.*` / `cypress.config.*` / `vitest.config.*` 존재 시 활성.

e2e-runner (sonnet) 백그라운드 실행 → 결과 수집.
E2E_FAILED 시: Architect 진단 → Domain-Smart Fix → 재실행 (max 2회). `--strict`: 1회 실패 즉시 중단.

### Step 3.3: 최종 검증

architect (opus) → Plan 대비 구현 일치 검증. APPROVE/REJECT 판정.

| 결과 | 처리 |
|------|------|
| APPROVE | 유의미 변경 커밋 → Phase 4 |
| REJECT (gap < 90%) | executor로 갭 수정 → Phase 3 재실행 |

### Step 3.4: TDD 커버리지

신규 코드 80% 이상, 전체 커버리지 감소 불가. 상세: `REFERENCE.md`

> **Phase 3↔4 루프 가드**: Phase 4→Phase 3 재진입 최대 3회. 초과 시 커밋 + 미해결 이슈 보고.

---

## Phase 4: CLOSE (보고서 + 팀 정리)

### Step 4.1: 보고서 생성

writer teammate → `docs/04-report/{feature}.report.md`. 모델: LIGHT=sonnet, STANDARD/HEAVY=opus.

### Step 4.2: 커밋 + Safe Cleanup

1. 유의미 변경 커밋: `docs(report): {feature} PDCA 완료 보고서`
2. 모든 teammate `shutdown_request` 순차 전송 (응답 대기 max 5초)
3. `TeamDelete()` 실행
4. 실패 시 Python `shutil.rmtree()` fallback

> 세션 crash recovery: `session_init.py` hook이 고아 팀 자동 정리.

---

## 복잡도 기반 모드 분기

| Phase | LIGHT (0-1) | STANDARD (2-3) | HEAVY (4-5) |
|-------|:-----------:|:--------------:|:-----------:|
| **0 INIT** | TeamCreate | TeamCreate | TeamCreate |
| **1 PLAN** | PRD + sonnet 계획 | PRD + opus 계획 + Critic-Lite + 설계 통합 | PRD + Planner-Critic Loop + 설계 통합 |
| **2 BUILD** | executor 단일 | impl-manager 5조건 + code-reviewer + Architect Gate | impl-manager 5조건 + code-reviewer + Architect Gate |
| **3 VERIFY** | QA 1회 + Architect | QA 3회 + E2E + Architect + 진단 루프 | QA 5회 + E2E + Architect + 진단 루프 |
| **4 CLOSE** | writer (sonnet) | writer (opus) | writer (opus) |

## 자율 발견 모드 (`/auto` 단독)

Tier 0 CONTEXT → 1 EXPLICIT → 2 URGENT → 3 WORK → 4 SUPPORT → 5 AUTONOMOUS 순서. 상세: `REFERENCE.md`

## 세션 관리

`/auto status` (상태 확인) / `/auto stop` (중지+TeamDelete) / `/auto resume` (재개+TeamCreate). 상세: `REFERENCE.md`

> **완전 frozen 시**: 별도 PowerShell 창에서 `python C:\claude\.claude\scripts\emergency_stop.py` 실행.

## 금지 사항

- 옵션 실패 시 조용히 스킵
- Architect 검증 없이 완료 선언
- 증거 없이 "완료됨" 주장
- 테스트 삭제로 문제 해결
- TeamDelete 없이 세션 종료
- architect로 파일 생성 시도 (READ-ONLY)
- Skill() 호출 (Agent Teams 단일 패턴)
- Team-Lead가 `shutdown_response` 호출 (세션 종료됨)
- 코드 블록 상세/prompt는 `REFERENCE.md` 참조
