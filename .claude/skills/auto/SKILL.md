---
name: auto
description: PDCA Orchestrator - 통합 자율 워크플로우 (Ralph + Ultrawork + PDCA)
version: 19.0.0
triggers:
  keywords:
    - "/auto"
    - "auto"
    - "autopilot"
    - "ulw"
    - "ultrawork"
    - "ralph"
    - "/work"
    - "work"
model_preference: opus
auto_trigger: true
omc_agents:
  - executor
  - executor-high
  - oh-my-claudecode:architect
  - planner
  - critic
  - code-reviewer
bkit_agents:
  - gap-detector
  - pdca-iterator
  - code-analyzer
  - report-generator
---

# /auto - PDCA Orchestrator (v19.0)

> **핵심**: `/auto "작업"` = Phase 0-5 PDCA 자동 진행. `/auto` 단독 = 자율 발견 모드. `/work`는 `/auto`로 통합됨.

## OMC + BKIT Integration (43 에이전트)

**OMC** (실행력): executor, executor-high, architect, planner, critic, code-reviewer
**BKIT** (체계성): gap-detector (90% 검증), pdca-iterator, code-analyzer, report-generator
**역할**: 이 스킬이 직접 orchestration. OMC 개별 스킬을 Phase별로 호출.

## 필수 실행 규칙 (CRITICAL)

**이 스킬이 활성화되면 반드시 Phase 0→5 순서로 실행하세요!**

### Phase 0: 옵션 파싱 + 모드 결정

| 옵션 | 효과 |
|------|------|
| `--skip-analysis` | Step 1.0 사전 분석 스킵 |
| `--no-issue` | Step 1.3 이슈 연동 스킵 |
| `--strict` | E2E 1회 실패 시 중단 |
| `--dry-run` | 판단만 출력, 실행 안함 |
| `--eco` | LIGHT 모드 강제 |

### Phase 1: PLAN (사전 분석 → 복잡도 판단 → 계획 수립 → 이슈 연동)

**Step 1.0: 사전 분석** - `--skip-analysis`로 스킵 가능. 병렬 실행:

```
Task(subagent_type="oh-my-claudecode:explore", model="haiku", prompt="문서 분석: CLAUDE.md, docs/ 탐색")
Task(subagent_type="oh-my-claudecode:explore", model="haiku", prompt="이슈 분석: gh issue/pr list 탐색")
```

**Step 1.1: 복잡도 판단 (5점 만점)** - 상세 기준: `REFERENCE.md`

| 점수 | 모드 | 라우팅 경로 |
|:----:|:----:|------------|
| 0-1 | LIGHT | `Task(planner, haiku)` |
| 2-3 | STANDARD | `Task(planner, sonnet)` |
| 4-5 | HEAVY | `Skill(ralplan)` |

**Step 1.3: 이슈 연동** - `--no-issue`로 스킵 가능

| 조건 | 동작 |
|------|------|
| 관련 이슈 없음 | `gh issue create` |
| Open 이슈 있음 | `gh issue comment` |
| Closed 이슈 있음 | `gh issue create` + 참조 |

**산출물**: `docs/01-plan/{feature}.plan.md`, GitHub Issue (선택)

### Phase 2: DESIGN (설계 문서 생성)

**Plan→Design Gate**: 4개 필수 섹션 확인 (배경, 구현 범위, 영향 파일, 위험 요소)

| 모드 | 실행 |
|------|------|
| LIGHT | **스킵** (Phase 3 직행) |
| STANDARD | `Task(architect, sonnet)` |
| HEAVY | `Task(architect, opus)` |

**산출물**: `docs/02-design/{feature}.design.md` (STANDARD/HEAVY만)

### Phase 3: DO (옵션 라우팅 + 구현)

**Step 3.0: 옵션 처리** (있을 경우, 구현 진입 전 실행)

| 옵션 | 실행할 스킬 | 설명 |
|------|-------------|------|
| `--gdocs` | `Skill(skill="prd-sync")` | Google Docs PRD 동기화 |
| `--mockup [파일]` | `Skill(skill="mockup-hybrid", args="...")` | 문서 기반 자동 목업 또는 단건 3-Tier |
| `--debate` | `Skill(skill="ultimate-debate", args="...")` | 3AI 토론 |
| `--research` | `Skill(skill="research", args="...")` | 리서치 모드 |
| `--slack <채널>` | Slack 채널 분석 후 컨텍스트 주입 | 채널 히스토리 기반 작업 |
| `--gmail` | Gmail 메일 분석 후 컨텍스트 주입 | 메일 기반 작업 |
| `--daily` | `Skill(skill="daily")` | daily v3.0 9-Phase Pipeline |
| `--interactive` | 각 Phase 전환 시 사용자 승인 요청 | 단계적 승인 모드 |

**옵션 실패 시**: 에러 메시지 출력, **절대 조용히 스킵하지 않음**. 상세: `REFERENCE.md`

**Step 3.1: 구현 실행** (모드별 분기)

| 모드 | 실행 |
|------|------|
| LIGHT | `Task(executor, sonnet)` - 단일 실행 (Ralph 없음) |
| STANDARD/HEAVY | `Skill(ralph)` - Ralph 루프 (Ultrawork 내장) |

Ralph = Ultrawork(병렬) + Architect 검증 + 5조건(TODO==0, 기능동작, 테스트통과, 에러==0, Architect승인) 충족 시 Phase 4 진입

**에이전트 라우팅**: explore(haiku), executor(sonnet), architect(opus), designer(sonnet), qa-tester(sonnet), build-fixer(sonnet). 상세: `REFERENCE.md`

### Phase 4: CHECK (UltraQA + 이중 검증 + E2E + TDD)

**Step 4.1: UltraQA 사이클** (Build→Lint→Test→Fix, max 5 cycle)
```
Skill(skill="oh-my-claudecode:ultraqa")
```
- 신규 코드 커버리지 80% 미달 시 FAIL 처리

**Step 4.2: 이중 검증** (STANDARD/HEAVY만, 병렬 실행)
```
Task(subagent_type="oh-my-claudecode:architect", model="{모드별}", ...)  # 기능 완성도
Task(subagent_type="bkit:gap-detector", model="{모드별}", ...)           # 설계-구현 90% 일치
```

**Step 4.3: E2E 검증** - Playwright 설정 존재 시만 실행 (상세: `REFERENCE.md`)
```
npx playwright test → 실패 시 Skill(skill="debug") 자동 트리거
--strict → 1회 실패 시 중단. 3회 가설 기각 → /issue failed
```

**Step 4.4: TDD 커버리지 보고** - 신규 코드 80% 이상, 전체 감소 불가

### Phase 5: ACT (결과 기반 자동 실행)

| Check 결과 | 자동 실행 |
|-----------|----------|
| gap < 90% | `Task(bkit:pdca-iterator, sonnet)` - 최대 5회 |
| gap >= 90% + APPROVE | `Task(bkit:report-generator, haiku)` → docs/04-report/ |
| Architect REJECT | `Task(executor, sonnet)` → Phase 4 재실행 |

**보고서 포맷** (확장): 분석 결과 / 설계 요약 / 구현 내역 / E2E 결과 / TDD 커버리지 / 이슈-PR 링크

---

## 복잡도 기반 모드 분기

| | LIGHT (0-1) | STANDARD (2-3) | HEAVY (4-5) |
|------|:-----------:|:--------------:|:-----------:|
| **Phase 1** | haiku 분석 + haiku 계획 | haiku 분석 + sonnet 계획 | haiku 분석 + Ralplan |
| **Phase 2** | 스킵 | sonnet 설계 | opus 설계 |
| **Phase 3** | sonnet executor | Ralph (sonnet) | Ralph (opus 검증) |
| **Phase 4** | UltraQA only | UltraQA + 이중검증 | UltraQA + 이중검증 + E2E |
| **Phase 5** | haiku 보고서 | sonnet 보고서 | 완전 보고서 |
| **예상 토큰** | ~5,000t | ~12,000t | ~20,000t |

**자동 승격**: LIGHT에서 빌드 실패 2회 / UltraQA 3사이클 / 영향 파일 5개+ 시 STANDARD로 승격

---

## 자율 발견 모드 (`/auto` 단독 실행 - 작업 인수 없음)

| Tier | 이름 | 발견 대상 | 실행 |
|:----:|------|----------|------|
| 0 | CONTEXT | context >= 90% | 체크포인트 생성 |
| 1 | EXPLICIT | 사용자 지시 | 해당 작업 실행 |
| 2 | URGENT | 빌드/테스트 실패 | `/debug` 실행 |
| 3 | WORK | pending TODO, 이슈 | 작업 처리 |
| 4 | SUPPORT | staged 파일, 린트 에러 | `/commit`, `/check` |
| 5 | AUTONOMOUS | 코드 품질 개선 | 리팩토링 제안 |

## 세션 관리

```bash
/auto status    # 현재 상태 확인
/auto stop      # 중지 (상태 저장)
/auto resume    # 재개
```

## 금지 사항

옵션 실패 시 조용히 스킵 / Architect 검증 없이 완료 선언 / 증거 없이 "완료됨" 주장 / 테스트 삭제로 문제 해결

**상세**: --slack, --gmail, --interactive, Step 상세 워크플로우 → `REFERENCE.md`
