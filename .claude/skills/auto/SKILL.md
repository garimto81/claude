---
name: auto
description: PDCA Orchestrator - 통합 자율 워크플로우 (Agent Teams 단일 패턴)
version: 22.4.0
triggers:
  keywords:
    - "/auto"
    - "auto"
    - "autopilot"
    - "/work"
model_preference: sonnet
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

# /auto - PDCA Orchestrator (v22.4)

> **핵심**: `/auto "작업"` = Phase 0-5 PDCA 자동 진행. `/auto` 단독 = 자율 발견 모드. `/work`는 `/auto`로 통합됨.
> **PRD-First**: 요구사항 요청 시 반드시 PRD 문서를 먼저 생성/수정 → 사용자 승인 후 구현 진행 (v22.3).
> **Agent Teams**: 모든 Phase에서 Agent Teams 단일 패턴 사용. Skill() 호출 0개. State 파일 의존 0개 (pdca-status.json은 진행 추적용, stop hook 비연동). 상세: `REFERENCE.md`

---

## 필수 실행 규칙 (CRITICAL)

**이 스킬이 활성화되면 반드시 Phase 0→5 순서로 실행하세요!**

### Phase 0: 옵션 파싱 + 모드 결정 + 팀 생성

| 옵션 | 효과 |
|------|------|
| `--skip-prd` | Phase 0.5 PRD 생성/수정 스킵 |
| `--skip-analysis` | Step 1.0 사전 분석 스킵 |
| `--no-issue` | Step 1.3 이슈 연동 스킵 |
| `--strict` | E2E 테스트 1회 실패 즉시 중단 (QA cycle과 무관) |
| `--dry-run` | 판단만 출력, 실행 안함 |
| `--eco` | LIGHT 모드 강제 (모든 단계 sonnet, opus 비활성화 포함) |
| `--worktree` | feature 전용 worktree 생성 후 해당 경로에서 작업, 완료 시 자동 정리 |
| `--mockup [파일]` | Phase 3.0에서 실행. **[파일] 지정 시**: 파일 내 ASCII 탐지 → `11-ascii-diagram.md` 기준 변환 (흐름/시퀀스/아키텍처 → Mermaid 코드 블록, UI 화면/컴포넌트 → HTML 목업 + PNG → Markdown 교체). **[파일] 미지정 시**: 화면명 인수 기반 신규 목업 생성. 하위 옵션: `--bnw` (HTML 목업에 B&W 스타일 제약만, 색상·폰트), `--force-html`, `--prd=` |

**팀 생성 (MANDATORY):**
```
TeamCreate(team_name="pdca-{feature}")
```
**TeamCreate 실패 방어 (Orphaned State 복구):**
- `Already leading team` 에러 발생 시 → `TeamDelete()` 즉시 호출 → `TeamCreate()` 재시도
- `Team already exists` 에러 발생 시 → `TeamDelete()` 즉시 호출 → `TeamCreate()` 재시도
- 재시도 1회 실패 시 → 사용자에게 에러 보고 후 중단 (무한 재시도 금지)

### 유의미 변경 커밋 원칙 (Commit Policy)

**유의미 변경 기준**: Phase 완료 후 `git status --short` 결과가 비어있지 않은 경우
- 코드 파일: `.py`, `.ts`, `.js`, `.tsx`, `.jsx`, `.go`, `.rs` 등
- **문서 파일**: `.md` (PRD, Plan, Design, Report 등 모두 포함)
- 설정 파일: `.json`, `.yaml`, `.toml`, `pyproject.toml` 등

**커밋 트리거 포인트** (각 Phase 완료 직후):
| 트리거 | 조건 | 커밋 메시지 패턴 |
|--------|------|----------------|
| Phase 2 설계 완료 | 설계 문서 생성 | `docs(design): {feature} 설계 문서 작성` |
| Phase 3.2 Architect APPROVE | 구현 완료 + 검증 통과 | `feat({feature}): 구현 완료` |
| Phase 4.2 Verification APPROVE | QA + 최종 검증 통과 | `fix({feature}): QA 수정사항 반영` |
| Phase 5 보고서 생성 후 | 보고서 생성 완료 | `docs(report): {feature} PDCA 완료 보고서` |
| 조기 종료 시 | max cycles 초과, 루프 가드 등 | `wip({feature}): 진행 중 변경사항 보존` |

> **공통 규칙**: 커밋 전 `git status --short`로 변경사항 확인 필수. 변경사항이 없으면 커밋 스킵.

### Phase 0.5: PRD (요구사항 문서화 — 구현 전 필수)

> **CRITICAL**: 요구사항 요청 시 반드시 PRD 문서를 먼저 생성/수정한 후 구현을 진행합니다. `--skip-prd`로 스킵 가능.

**Step 0.5.1**: 기존 PRD 탐색

```
# docs/00-prd/ 디렉토리에서 기존 PRD 탐색
existing_prd = Glob("docs/00-prd/{feature}*.prd.md")
# 관련 PRD가 없으면 docs/00-prd/ 전체 탐색하여 연관 문서 확인
if not existing_prd:
    all_prds = Glob("docs/00-prd/*.prd.md")
```

**Step 0.5.2**: PRD 생성 또는 수정 — executor teammate

```
# 기존 PRD 없음 → 신규 생성
Task(subagent_type="executor", name="prd-writer", team_name="pdca-{feature}",
     model="sonnet", max_turns=25, prompt="[Phase 0.5 PRD] 사용자 요구사항을 PRD 문서로 작성.
     사용자 요청: {user_request}
     기존 관련 PRD: {existing_prds_summary}
     출력: docs/00-prd/{feature}.prd.md
     필수 섹션: 배경/목적, 요구사항 목록(번호 부여), 기능 범위, 비기능 요구사항, 제약사항, 우선순위.
     상세 템플릿: REFERENCE.md")
SendMessage(type="message", recipient="prd-writer", content="PRD 문서 작성 시작.")
# 완료 대기 → shutdown_request

# 기존 PRD 있음 → 수정
Task(subagent_type="executor", name="prd-writer", team_name="pdca-{feature}",
     model="sonnet", max_turns=25, prompt="[Phase 0.5 PRD Update] 기존 PRD를 요구사항에 맞게 수정.
     기존 PRD: docs/00-prd/{existing_prd_file}
     추가/변경 요구사항: {user_request}
     변경 이력을 ## Changelog 섹션에 기록.")
SendMessage(type="message", recipient="prd-writer", content="PRD 수정 시작.")
# 완료 대기 → shutdown_request
```

**Step 0.5.3**: 사용자 승인 (MANDATORY)

```
# PRD 내용을 사용자에게 제시
prd_content = Read("docs/00-prd/{feature}.prd.md")
# AskUserQuestion으로 승인 요청
# 승인 → Phase 1 진입
# 수정 요청 → Step 0.5.2 재실행 (수정 반영, max 3회)
# 3회 초과 → 현재 PRD로 Phase 1 진입 (경고 포함)
```

**산출물**: `docs/00-prd/{feature}.prd.md`

### Phase 1: PLAN (사전 분석 → 복잡도 판단 → 계획 수립 → 이슈 연동)

**Step 1.0**: 병렬 explore(haiku) x2 — 문서 탐색 + 이슈 탐색. `--skip-analysis`로 스킵 가능.

```
Task(subagent_type="explore", name="doc-analyst", team_name="pdca-{feature}",
     model="haiku", max_turns=10, prompt="docs/, .claude/ 내 관련 문서 탐색. 결과 5줄 이내 요약.")
Task(subagent_type="explore", name="issue-analyst", team_name="pdca-{feature}",
     model="haiku", max_turns=10, prompt="gh issue list로 유사 이슈 탐색. 결과 5줄 이내 요약.")
# 완료 대기 → 각각 SendMessage(type="shutdown_request", recipient="...")
```

**Step 1.1: 복잡도 판단 (5점 만점)** — 상세 기준: `REFERENCE.md`

| 점수 | 모드 | 라우팅 |
|:----:|:----:|--------|
| 0-1 | LIGHT | planner teammate (haiku) |
| 2-3 | STANDARD | planner teammate (sonnet) |
| 4-5 | HEAVY | Planner-Critic Loop (max 5 iter) |

> **모델 오버라이드**: 에이전트 정의(architect=sonnet 등)와 무관하게, 호출 시 `model` 파라미터가 복잡도 모드에 따라 결정됨.

**Step 1.2**: 계획 수립 → `docs/01-plan/{feature}.plan.md` 생성 (Graduated Plan Review)

**LIGHT (0-1점): Planner + Lead Quality Gate**
```
Task(subagent_type="planner", name="planner", team_name="pdca-{feature}",
     model="haiku", max_turns=30, prompt="(복잡도: LIGHT {score}/5). docs/01-plan/{feature}.plan.md 생성.
     PRD 참조: docs/00-prd/{feature}.prd.md (있으면 반드시 기반으로 계획 수립).
     사용자 확인/인터뷰 단계 건너뛰고 바로 계획 문서를 작성하세요.")
SendMessage(type="message", recipient="planner", content="계획 수립 시작.")
# 완료 대기 → shutdown_request
# Lead Quality Gate: (1) plan 파일 존재+내용 있음, (2) 파일 경로 1개+ 언급
# 미충족 시 Planner 1회 재요청
```

**STANDARD (2-3점): Planner + Critic-Lite 단일 검토**
```
Task(subagent_type="planner", name="planner", team_name="pdca-{feature}",
     model="opus", max_turns=30, prompt="(복잡도: STANDARD {score}/5). docs/01-plan/{feature}.plan.md 생성.
     PRD 참조: docs/00-prd/{feature}.prd.md (있으면 반드시 기반으로 계획 수립).
     사용자 확인/인터뷰 단계 건너뛰세요. Critic-Lite가 검토합니다.")
SendMessage(type="message", recipient="planner", content="계획 수립 시작.")
# 완료 대기 → shutdown_request
# Critic-Lite: Quality Gates 4 검증 (QG1-QG4) — 상세 prompt: REFERENCE.md
Task(subagent_type="critic", name="critic-lite", team_name="pdca-{feature}",
     model="opus", max_turns=15, prompt="[Critic-Lite] QG1-QG4 검증. VERDICT: APPROVE/REVISE.")
SendMessage(type="message", recipient="critic-lite", content="Plan 검토 시작.")
# REVISE → Planner 1회 수정 → 수정본 수용 (추가 Critic 없음)
```

**HEAVY (4-5점): Planner-Critic Loop (max 5 iterations)** — 상세 prompt: `REFERENCE.md`
```
critic_feedback = ""
Loop (i=1..5):
  1. Planner teammate (opus) → 계획 수립 (critic_feedback 반영)
  2. Architect teammate (opus) → 기술적 타당성 검증
  3. Critic teammate (opus) → Quality Gates 4 (QG1-QG4) + VERDICT: APPROVE/REVISE
  APPROVE → Loop 종료 / REVISE → critic_feedback 업데이트 → 다음 iteration
  5회 초과 → 경고 포함 강제 승인
```

**Step 1.3**: 이슈 연동 (없으면 생성, 있으면 코멘트). `--no-issue`로 스킵 가능.

### Phase 2: DESIGN (설계 문서 생성)

**Plan→Design Gate (STANDARD/HEAVY만)**: 4개 필수 섹션 확인 (배경, 구현 범위, 영향 파일, 위험 요소)

| 모드 | 실행 | 에이전트 |
|------|------|---------|
| LIGHT | **스킵** (Phase 3 직행) | — |
| STANDARD | design-writer teammate | `executor` (sonnet) |
| HEAVY | design-writer teammate | `executor-high` (sonnet) |

> **주의**: `architect`는 READ-ONLY (Write 도구 없음). 설계 **문서 생성**에는 executor 계열 사용 필수.

```
# STANDARD 예시 (HEAVY: executor-high + sonnet)
Task(subagent_type="executor", name="design-writer", team_name="pdca-{feature}",
     model="sonnet", max_turns=40, prompt="docs/01-plan/{feature}.plan.md 참조. 설계 문서 작성. 출력: docs/02-design/{feature}.design.md")
SendMessage(type="message", recipient="design-writer", content="설계 문서 생성 요청.")
```

**산출물**: `docs/02-design/{feature}.design.md` (STANDARD/HEAVY만)
> **커밋 (유의미 변경 시)**: 설계 문서 생성 후 `git status --short` 확인 → 변경사항 있으면 `git add docs/ && git commit -m "docs(design): {feature} 설계 문서 작성"`

### Phase 3: DO (옵션 라우팅 + 구현)

**Step 3.0**: 옵션 처리 (구현 진입 전 실행)

| 옵션 | 스킬 | 옵션 | 스킬 |
|------|------|------|------|
| `--gdocs` | `prd-sync` | `--slack <채널>` | Slack 분석 |
| `--mockup [파일] [--bnw]` | ASCII→형식 변환 (`11-ascii-diagram.md` 기준) | `--gmail` | Gmail 분석 |
| `--debate` | `ultimate-debate` | `--daily` | `daily` |
| `--research` | `research` | `--interactive` | Phase별 승인 |

**--mockup 실행 경로** (`11-ascii-diagram.md` 기준 타입 판별):
```
--mockup <파일>
      │
      ▼
파일 내 ASCII 다이어그램 탐지
      │
      ├─ 흐름/시퀀스/아키텍처/트리 → Mermaid 코드 블록으로 교체
      │
      └─ UI 화면/컴포넌트 목업 → HTML 목업 + PNG 캡처 → Markdown 교체
              └─ --bnw 적용 시: HTML 목업에 B&W 스타일 제약 (색상·폰트)

--mockup "화면명" (파일 미지정)
      └─ 신규 화면 목업 생성 → designer teammate → docs/mockups/{name}.html
              └─ --bnw 적용 시: B&W 스타일 제약
```
executor 또는 executor-high가 `docs/mockups/*.html`을 직접 Write하는 것은 금지. UI 목업 생성 시 반드시 designer 에이전트 경유.
**--bnw**: HTML 목업의 스타일 제약만 (색상 없음). 자동 트리거 없음 — 명시적 플래그 필수.

**옵션 실패 시**: 에러 출력, **절대 조용히 스킵 금지**. 상세: `REFERENCE.md`

**Step 3.1**: 구현 실행

| 모드 | 실행 |
|------|------|
| LIGHT | executor teammate (sonnet) — 단일 실행 |
| STANDARD | impl-manager teammate (sonnet) — 5조건 자체 루프 |
| HEAVY | impl-manager teammate (sonnet) — 5조건 자체 루프 + 병렬 가능 |

```
# LIGHT: executor teammate 단일 실행
Task(subagent_type="executor", name="executor", team_name="pdca-{feature}",
     model="sonnet", max_turns=50, prompt="docs/01-plan/{feature}.plan.md 기반 구현. TDD 필수.")
SendMessage(type="message", recipient="executor", content="구현 시작.")

# STANDARD/HEAVY: impl-manager teammate (5조건 자체 루프) — 상세 prompt: REFERENCE.md
Task(subagent_type="executor[-high]", name="impl-manager",
     team_name="pdca-{feature}", model="sonnet", max_turns=60,
     prompt="설계 문서 기반 구현. 5조건 자체 루프 (max 10회). 상세 prompt: REFERENCE.md")
SendMessage(type="message", recipient="impl-manager", content="5조건 구현 루프 시작.")
# Lead는 IMPLEMENTATION_COMPLETED 또는 IMPLEMENTATION_FAILED 메시지만 수신
```

impl-manager 5조건: TODO==0, 빌드 성공, 테스트 통과, 에러==0, 자체 코드 리뷰. 상세: `REFERENCE.md`
**Step 3.2**: Architect Verification Gate (STANDARD/HEAVY 필수, LIGHT 스킵)

```
# impl-manager IMPLEMENTATION_COMPLETED 수신 후 (STANDARD/HEAVY만)
Task(subagent_type="architect", name="impl-verifier", team_name="pdca-{feature}",
     model="opus", max_turns=20, prompt="[Phase 3 Architect Gate] 구현 외부 검증. 상세: REFERENCE.md")
SendMessage(type="message", recipient="impl-verifier", content="구현 검증 시작.")
# VERDICT: APPROVE → 유의미 변경 커밋 → Phase 4 진입
#   git status --short 확인 → 변경사항 있으면:
#   git add -A && git commit -m "feat({feature}): 구현 완료 (Architect APPROVE)"
# VERDICT: REJECT + DOMAIN → Step 3.3 Domain-Smart Fix
# 2회 REJECT → 사용자 알림 후 Phase 4 진입 허용
```

**Step 3.3**: Domain-Smart Fix Routing (Architect REJECT 시)

| Architect DOMAIN | 에이전트 | 용도 |
|------------------|---------|------|
| UI, component, style | designer | 프론트엔드 수정 |
| build, compile, type | build-fixer | 빌드/타입 에러 |
| test, coverage | executor | 테스트 수정 |
| security | security-reviewer | 보안 이슈 |
| 기타 | executor | 일반 수정 |

```
# Domain-Smart Fix → Architect 재검증 (max 2회)
Task(subagent_type="{domain-agent}", name="domain-fixer", team_name="pdca-{feature}",
     model="sonnet", max_turns=30, prompt="Architect 거부 사유: {rejection}. DOMAIN: {domain}. 수정 실행.")
# 수정 완료 → Step 3.2 Architect 재검증
```

### Phase 4: CHECK (QA Runner + Architect 진단 + 검증 + E2E + TDD)

**Step 4.1**: QA 사이클 — QA Runner + Architect 진단 + Domain-Smart Fix

```
# LIGHT: QA 1회 실행. 실패 시 보고만 (STANDARD 자동 승격 검토). 진단/수정 없음.
Task(subagent_type="qa-tester", name="qa-runner", team_name="pdca-{feature}",
     model="sonnet", max_turns=40, prompt="6종 QA 실행. 상세: REFERENCE.md")
# QA_PASSED → Step 4.2 / QA_FAILED → 실패 보고 + STANDARD 승격 조건 확인

# STANDARD/HEAVY: QA 사이클 (max STANDARD:3 / HEAVY:5)
failure_history = []
Loop (max_cycles):
  # A. QA Runner teammate
  Task(subagent_type="qa-tester", name="qa-runner-{i}", team_name="pdca-{feature}",
       model="sonnet", max_turns=40, prompt="6종 QA 실행. 상세: REFERENCE.md")
  # QA_PASSED → Step 4.2 / QA_FAILED → B
  # B. Architect Root Cause 진단 (MANDATORY)
  Task(subagent_type="architect", name="diagnostician-{i}", team_name="pdca-{feature}",
       model="opus", max_turns=20, prompt="QA 실패 root cause 진단. 출력: DIAGNOSIS + FIX_GUIDE + DOMAIN.")
  # C. Domain-Smart Fix
  Task(subagent_type="{domain-agent}", name="fixer-{i}", team_name="pdca-{feature}",
       model="sonnet", max_turns=30, prompt="진단 기반 수정: {DIAGNOSIS}. 지침: {FIX_GUIDE}.")
```

**4종 Exit Conditions:**

| 우선순위 | 조건 | 처리 |
|:--------:|------|------|
| 1 | Environment Error | 즉시 중단 + 환경 문제 보고 |
| 2 | Same Failure 3x | 조기 종료 + root cause 보고 |
| 3 | Max Cycles 도달 | 미해결 이슈 보고 |
| 4 | Goal Met | Step 4.2 이중 검증 진입 |

QA Runner 6종 goal, Architect 진단 prompt, Domain routing 상세: `REFERENCE.md`

**Step 4.2**: 검증 (순차 teammate — context spike 방지)

| 모드 | 실행 |
|------|------|
| LIGHT | architect teammate (sonnet) — APPROVE/REJECT만 |
| STANDARD | architect (opus) → code-reviewer (sonnet) 순차 |
| HEAVY | architect (opus) → code-reviewer (sonnet) 순차 |

```
# LIGHT: architect만 / STANDARD/HEAVY: architect → code-reviewer 순차
Task(subagent_type="architect", name="verifier", team_name="pdca-{feature}",
     model="opus", max_turns=20, prompt="구현이 Plan/Design 요구사항과 일치하는지 검증. APPROVE/REJECT 판정.")
SendMessage(type="message", recipient="verifier", content="검증 시작.")
# 완료 대기 → shutdown_request → (STANDARD/HEAVY: code-reviewer 순차 spawn)
# code-reviewer prompt에 Vercel BP 규칙 동적 주입 (React/Next.js 프로젝트 시) — 상세: REFERENCE.md
# code-reviewer APPROVE 후 → 유의미 변경 커밋:
#   git status --short 확인 → 변경사항 있으면:
#   git add -A && git commit -m "fix({feature}): QA 검증 수정사항 반영"
```

> architect는 READ-ONLY이므로 **검증/판정에 적합**. 파일 생성에는 사용 금지.

**Step 4.3**: E2E — Playwright 존재 시만. 실패 시 `/debug`. `--strict` → 1회 실패 중단.
**Step 4.4**: TDD 커버리지 — 신규 80% 이상, 전체 감소 불가.

### Phase 5: ACT (결과 기반 자동 실행 + 팀 정리)

| Check 결과 | 자동 실행 |
|-----------|----------|
| gap < 90% | executor teammate로 갭 개선 (최대 5회) → Phase 4 재실행 |
| gap >= 90% + APPROVE | writer teammate → `docs/04-report/` |
| Architect REJECT | executor teammate (수정) → Phase 4 재실행 |

> **Phase 4↔5 루프 가드**: Phase 5→Phase 4 재진입 누적 최대 3회. 초과 시 유의미 변경 커밋 후 미해결 이슈 보고 + 종료.

```
# gap >= 90% + APPROVE → 보고서 생성 후 Safe Cleanup
# 보고서 모델 분기: LIGHT=haiku, STANDARD/HEAVY=sonnet
report_model = "haiku" if mode == "LIGHT" else "sonnet"
Task(subagent_type="writer", name="reporter", team_name="pdca-{feature}",
     model=report_model, max_turns=25, prompt="PDCA 완료 보고서 생성. 출력: docs/04-report/{feature}.report.md")
SendMessage(type="message", recipient="reporter", content="보고서 생성 요청.")
# 완료 대기 → shutdown_request
# 유의미 변경 커밋: git add docs/04-report/ && git commit -m "docs(report): {feature} PDCA 완료 보고서"
# → Safe Cleanup (아래 절차)
```

**팀 정리 (MANDATORY — Safe Cleanup):**
1. 모든 활성 teammate에 `SendMessage(type="shutdown_request")` 순차 전송
2. 각 teammate 응답 대기 (최대 5초). 무응답 시 다음 단계로 진행 (차단 금지)
3. `TeamDelete()` 실행
4. TeamDelete 실패 시 수동 fallback: `python3 -c "import shutil,pathlib; [shutil.rmtree(pathlib.Path.home()/'.claude'/d/'{팀명}', ignore_errors=True) for d in ['teams','tasks']]"`
5. 실패 원인 로그 출력 (사용자 알림)

> **세션 crash recovery**: 새 세션 시작 시 `session_init.py` hook이 고아 팀을 자동 정리합니다. 수동 정리 필요 시 Python `shutil.rmtree()` 사용 (`rm -rf ~/...`는 tool_validator.py에 의해 차단됨).

---

## 복잡도 기반 모드 분기

| | LIGHT (0-1) | STANDARD (2-3) | HEAVY (4-5) |
|------|:-----------:|:--------------:|:-----------:|
| **Phase 0** | TeamCreate | TeamCreate | TeamCreate |
| **Phase 0.5** | PRD 생성/수정 + 사용자 승인 | PRD 생성/수정 + 사용자 승인 | PRD 생성/수정 + 사용자 승인 |
| **Phase 1** | haiku 계획 + Lead QG | sonnet 계획 + Critic-Lite | Planner-Critic Loop |
| **Phase 2** | 스킵 | executor (sonnet) 설계 | executor-high (sonnet) 설계 |
| **Phase 3.1** | executor (sonnet) | impl-manager (sonnet) | impl-manager (sonnet) + 병렬 |
| **Phase 3.2** | — | Architect Gate | Architect Gate |
| **Phase 4.1** | QA 1회 (보고만) | QA 3회 + 진단 | QA 5회 + 진단 |
| **Phase 4.2** | Architect (sonnet) | Architect (opus) + code-reviewer (sonnet) | Architect (opus) + code-reviewer (sonnet) |
| **Phase 5** | writer (haiku) + 커밋 + TeamDelete | writer (sonnet) + 커밋 + TeamDelete | writer (sonnet) + 커밋 + TeamDelete |

**자동 승격**: LIGHT→STANDARD: 빌드 실패 2회 또는 영향 파일 5개+. STANDARD→HEAVY: QA 3사이클 초과 또는 영향 파일 5개+.

## 자율 발견 모드 (`/auto` 단독 실행 — 작업 인수 없음)

Tier 0 CONTEXT → 1 EXPLICIT → 2 URGENT → 3 WORK → 4 SUPPORT → 5 AUTONOMOUS 순서로 발견. 상세: `REFERENCE.md`

## 세션 관리

`/auto status` (상태 확인) / `/auto stop` (중지+TeamDelete) / `/auto resume` (재개+TeamCreate). 상세: `REFERENCE.md`

> **🚨 Ctrl+C + /auto stop 모두 무효인 경우 (완전 frozen)**:
> 별도 PowerShell 창에서 `python C:\claude\.claude\scripts\emergency_stop.py` 실행.
> 원인·절차 상세: `REFERENCE.md` → Nuclear Option 섹션

## 금지 사항

옵션 실패 시 조용히 스킵 / Architect 검증 없이 완료 선언 / 증거 없이 "완료됨" 주장 / 테스트 삭제로 문제 해결 / **TeamDelete 없이 세션 종료** / **architect 에이전트로 파일 생성 시도** / **Skill() 호출 금지 (Agent Teams 단일 패턴)** / **executor가 `docs/mockups/*.html` 직접 생성 금지** (반드시 designer 에이전트 + --mockup --bnw 라우트 경유) / **코드 블록 상세, 옵션 워크플로우, impl-manager prompt, Vercel BP**: `REFERENCE.md`
