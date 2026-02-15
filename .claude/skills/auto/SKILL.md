---
name: auto
description: PDCA Orchestrator - 통합 자율 워크플로우 (Agent Teams + PDCA)
version: 20.0.0
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

# /auto - PDCA Orchestrator (v20.0)

> **핵심**: `/auto "작업"` = Phase 0-5 PDCA 자동 진행. `/auto` 단독 = 자율 발견 모드. `/work`는 `/auto`로 통합됨.

## Agent Teams Protocol (v20.0 - Context 분리)

**모든 에이전트 호출은 Agent Teams in-process 방식을 사용합니다.**

| 항목 | 설명 |
|------|------|
| **Context 분리** | 각 teammate는 독립 context window (Lead context 오염 없음) |
| **통신** | Mailbox 기반 SendMessage (결과가 Lead context에 합류하지 않음) |
| **조정** | Shared Task List (파일 기반, 락킹 지원) |
| **모드** | in-process (tmux 불필요, Windows 호환) |

### 팀 라이프사이클

```
Phase 0: TeamCreate(team_name="pdca-{feature}")
Phase 1-4: Task(name="역할", team_name="pdca-{feature}") → SendMessage → 완료 대기 → shutdown_request
Phase 5: 보고서 생성 → TeamDelete()
```

### 기본 패턴 (모든 Phase에서 동일)

```
# 1. Teammate 생성 + Task 할당
TaskCreate(subject="작업 제목", description="상세 내용")
Task(subagent_type="agent-type", name="role-name", team_name="pdca-{feature}",
     model="haiku|sonnet|opus", prompt="작업 지시")
SendMessage(type="message", recipient="role-name", content="Task #{n} 할당. 완료 후 TaskUpdate로 completed 처리.")

# 2. 완료 대기 (Mailbox로 자동 수신)

# 3. 종료
SendMessage(type="shutdown_request", recipient="role-name")
```

---

## 필수 실행 규칙 (CRITICAL)

**이 스킬이 활성화되면 반드시 Phase 0→5 순서로 실행하세요!**

### Phase 0: 옵션 파싱 + 모드 결정 + 팀 생성

| 옵션 | 효과 |
|------|------|
| `--skip-analysis` | Step 1.0 사전 분석 스킵 |
| `--no-issue` | Step 1.3 이슈 연동 스킵 |
| `--strict` | E2E 1회 실패 시 중단 |
| `--dry-run` | 판단만 출력, 실행 안함 |
| `--eco` | LIGHT 모드 강제 |

**팀 생성 (MANDATORY):**
```
TeamCreate(team_name="pdca-{feature}")
```

### Phase 1: PLAN (사전 분석 → 복잡도 판단 → 계획 수립 → 이슈 연동)

**Step 1.0: 사전 분석** - `--skip-analysis`로 스킵 가능. 병렬 teammate:

```
Task(subagent_type="oh-my-claudecode:explore", name="doc-analyst", team_name="pdca-{feature}",
     model="haiku", prompt="docs/, .claude/ 내 관련 문서 탐색. 중복 범위 감지.")
Task(subagent_type="oh-my-claudecode:explore", name="issue-analyst", team_name="pdca-{feature}",
     model="haiku", prompt="gh issue list 실행하여 유사 이슈 탐색.")
```

→ Mailbox로 결과 수신 후 두 teammate 모두 shutdown_request

**Step 1.1: 복잡도 판단 (5점 만점)** - 상세 기준: `REFERENCE.md`

| 점수 | 모드 | 라우팅 경로 |
|:----:|:----:|------------|
| 0-1 | LIGHT | teammate: planner (haiku) |
| 2-3 | STANDARD | teammate: planner (sonnet) |
| 4-5 | HEAVY | `Skill(ralplan)` |

**Step 1.2: 계획 수립** - LIGHT/STANDARD:

```
Task(subagent_type="oh-my-claudecode:planner", name="planner", team_name="pdca-{feature}",
     model="haiku|sonnet", prompt="... 계획 수립. docs/01-plan/{feature}.plan.md 생성.")
SendMessage(type="message", recipient="planner", content="Task 할당. 완료 후 TaskUpdate로 completed 처리.")
# 완료 대기 → shutdown_request
```

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
| STANDARD | teammate: architect (sonnet) |
| HEAVY | teammate: architect (opus) |

```
Task(subagent_type="oh-my-claudecode:architect", name="architect", team_name="pdca-{feature}",
     model="sonnet|opus",
     prompt="docs/01-plan/{feature}.plan.md 참조하여 설계 문서 작성. docs/02-design/{feature}.design.md 생성.")
SendMessage(type="message", recipient="architect", content="설계 문서 생성 요청. 완료 후 TaskUpdate로 completed 처리.")
# 완료 대기 → shutdown_request
```

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
| LIGHT | teammate: executor (sonnet) - 단일 실행 (Ralph 없음) |
| STANDARD/HEAVY | `Skill(ralph)` - Ralph 루프 (Ultrawork 내장) |

**LIGHT 모드:**
```
Task(subagent_type="oh-my-claudecode:executor", name="executor", team_name="pdca-{feature}",
     model="sonnet", prompt="docs/01-plan/{feature}.plan.md 기반 구현. TDD 필수.")
SendMessage(type="message", recipient="executor", content="구현 시작. 완료 후 TaskUpdate로 completed 처리.")
# 완료 대기 → shutdown_request
```

**STANDARD/HEAVY 모드:**
Ralph = Ultrawork(병렬) + Architect 검증 + 5조건(TODO==0, 기능동작, 테스트통과, 에러==0, Architect승인) 충족 시 Phase 4 진입

**에이전트 라우팅**: explore(haiku), executor(sonnet), architect(opus), designer(sonnet), qa-tester(sonnet), build-fixer(sonnet). 상세: `REFERENCE.md`

### Phase 4: CHECK (UltraQA + 이중 검증 + E2E + TDD)

**Step 4.1: UltraQA 사이클** (Build→Lint→Test→Fix, max 5 cycle)
```
Skill(skill="oh-my-claudecode:ultraqa")
```
- 신규 코드 커버리지 80% 미달 시 FAIL 처리

**Step 4.2: 이중 검증** (STANDARD/HEAVY만, **순차 teammate** - context spike 방지)

```
# 1. Architect 검증 teammate
Task(subagent_type="oh-my-claudecode:architect", name="verifier", team_name="pdca-{feature}",
     model="sonnet|opus",
     prompt="구현된 기능이 docs/02-design/{feature}.design.md와 일치하는지 검증.")
SendMessage(type="message", recipient="verifier", content="검증 시작. APPROVE/REJECT 판정 후 TaskUpdate 처리.")
# verifier 완료 대기 → shutdown_request

# 2. Gap-detector teammate (verifier 완료 후)
Task(subagent_type="bkit:gap-detector", name="gap-checker", team_name="pdca-{feature}",
     model="sonnet|opus",
     prompt="docs/02-design/{feature}.design.md와 실제 구현 코드 간 일치도 분석. 90% 기준.")
SendMessage(type="message", recipient="gap-checker", content="갭 분석 시작. 완료 후 TaskUpdate 처리.")
# gap-checker 완료 대기 → shutdown_request
```

**Step 4.3: E2E 검증** - Playwright 설정 존재 시만 실행 (상세: `REFERENCE.md`)
```
npx playwright test → 실패 시 Skill(skill="debug") 자동 트리거
--strict → 1회 실패 시 중단. 3회 가설 기각 → /issue failed
```

**Step 4.4: TDD 커버리지 보고** - 신규 코드 80% 이상, 전체 감소 불가

### Phase 5: ACT (결과 기반 자동 실행 + 팀 정리)

| Check 결과 | 자동 실행 |
|-----------|----------|
| gap < 90% | teammate: pdca-iterator (sonnet) - 최대 5회 |
| gap >= 90% + APPROVE | teammate: report-generator (haiku) → docs/04-report/ |
| Architect REJECT | teammate: executor (sonnet) → Phase 4 재실행 |

**Case 1: gap < 90%**
```
Task(subagent_type="bkit:pdca-iterator", name="iterator", team_name="pdca-{feature}",
     model="sonnet", prompt="설계-구현 갭을 90% 이상으로 개선. 최대 5회 반복.")
SendMessage(type="message", recipient="iterator", content="갭 자동 개선 시작.")
# 완료 대기 → shutdown_request → Phase 4 재실행
```

**Case 2: gap >= 90% + APPROVE**
```
Task(subagent_type="bkit:report-generator", name="reporter", team_name="pdca-{feature}",
     model="haiku", prompt="PDCA 사이클 완료 보고서 생성. 출력: docs/04-report/{feature}.report.md")
SendMessage(type="message", recipient="reporter", content="보고서 생성 요청.")
# 완료 대기 → shutdown_request
```

**Case 3: Architect REJECT**
```
Task(subagent_type="oh-my-claudecode:executor", name="fixer", team_name="pdca-{feature}",
     model="sonnet", prompt="Architect 거부 사유를 해결: {rejection_reason}")
SendMessage(type="message", recipient="fixer", content="피드백 반영 시작.")
# 완료 대기 → shutdown_request → Phase 4 재실행
```

**팀 정리 (MANDATORY):**
```
TeamDelete()
```

**보고서 포맷** (확장): 분석 결과 / 설계 요약 / 구현 내역 / E2E 결과 / TDD 커버리지 / 이슈-PR 링크

---

## 복잡도 기반 모드 분기

| | LIGHT (0-1) | STANDARD (2-3) | HEAVY (4-5) |
|------|:-----------:|:--------------:|:-----------:|
| **Phase 0** | TeamCreate | TeamCreate | TeamCreate |
| **Phase 1** | haiku 분석 + haiku 계획 | haiku 분석 + sonnet 계획 | haiku 분석 + Ralplan |
| **Phase 2** | 스킵 | sonnet 설계 | opus 설계 |
| **Phase 3** | sonnet executor | Ralph (sonnet) | Ralph (opus 검증) |
| **Phase 4** | UltraQA only | UltraQA + 이중검증 | UltraQA + 이중검증 + E2E |
| **Phase 5** | haiku 보고서 + TeamDelete | sonnet 보고서 + TeamDelete | 완전 보고서 + TeamDelete |
| **예상 토큰** | ~8,000t | ~18,000t | ~30,000t |

**자동 승격**: LIGHT에서 빌드 실패 2회 / UltraQA 3사이클 / 영향 파일 5개+ 시 STANDARD로 승격

> **토큰 증가 참고**: Agent Teams는 각 teammate가 독립 context를 사용하므로 기존 subagent 대비 1.5-2배 토큰을 소비합니다. 대신 Lead context overflow 문제가 근본적으로 해결됩니다.

---

## Context Recovery Protocol

### 자동 상태 유지 (추가 비용 0)

PDCA 워크플로우의 정상 동작만으로 모든 상태가 디스크에 유지됨:
- `docs/.pdca-status.json` → phase, phaseNumber, documents, timestamps 자동 갱신
- `docs/01-plan/{feature}.plan.md` → Phase 1 산출물
- `docs/02-design/{feature}.design.md` → Phase 2 산출물
- `docs/04-report/{feature}.report.md` → Phase 5 산출물
- 추가 에이전트 생성이나 Note 기록 불필요. 기존 워크플로우가 곧 체크포인트.

### Agent Teams Context 장점

| 기존 (subagent) | 신규 (Agent Teams) |
|-----------------|-------------------|
| 결과가 Lead context에 합류 → overflow | 결과가 Mailbox로 전달 → Lead context 보호 |
| foreground 3개 상한 필요 | 제한 없음 (독립 context) |
| "5줄 요약" 강제 필요 | 불필요 (context 분리) |
| compact 실패 위험 | compact 실패 없음 |

### Resume (`/auto resume`)

`/clear` 또는 새 세션 시작 후:
1. `docs/.pdca-status.json` 읽기 → `primaryFeature`와 `phaseNumber` 확인
2. 산출물 존재 검증: Plan 파일, Design 파일 유무로 실제 진행 Phase 교차 확인
3. Git 상태 확인: `git branch --show-current`, `git status --short`
4. Phase 3 중단 시: `ralphIteration` 필드로 Ralph 반복 위치 확인
5. `TeamCreate(team_name="pdca-{feature}")` 새로 생성 (이전 팀은 복원 불가)
6. 해당 Phase부터 재개 (완료된 Phase 재실행 금지)

### 사용자 대응

Context limit 발생 시: `claude --continue` 또는 `/clear` 후 `/auto resume`

---

## 자율 발견 모드 (`/auto` 단독 실행 - 작업 인수 없음)

| Tier | 이름 | 발견 대상 | 실행 |
|:----:|------|----------|------|
| 0 | CONTEXT | context limit 접근 | 사용자에게 `/clear` + `/auto resume` 안내 |
| 1 | EXPLICIT | 사용자 지시 | 해당 작업 실행 |
| 2 | URGENT | 빌드/테스트 실패 | `/debug` 실행 |
| 3 | WORK | pending TODO, 이슈 | 작업 처리 |
| 4 | SUPPORT | staged 파일, 린트 에러 | `/commit`, `/check` |
| 5 | AUTONOMOUS | 코드 품질 개선 | 리팩토링 제안 |

## 세션 관리

```bash
/auto status    # 현재 상태 확인
/auto stop      # 중지 (pdca-status.json에 상태 저장, TeamDelete 실행)
/auto resume    # 재개 (pdca-status.json + 산출물 기반 Phase 복원, TeamCreate 재생성)
```

## 금지 사항

옵션 실패 시 조용히 스킵 / Architect 검증 없이 완료 선언 / 증거 없이 "완료됨" 주장 / 테스트 삭제로 문제 해결 / **TeamDelete 없이 세션 종료**

**상세**: --slack, --gmail, --interactive, Step 상세 워크플로우 → `REFERENCE.md`
