# bkit v1.5.0 심층 분석 및 OMC 통합 제안

> 분석일: 2026-02-18 | 대상: bkit v1.5.0 (Vibecoding Kit)
> 방법: 3개 병렬 분석 에이전트 (아키텍처, 통합 비교, Context Engineering)

---

## 1. Executive Summary (핵심 요약)

bkit v1.5.0은 Context Engineering을 체계적으로 구현한 워크플로우 키트로, 22개 Skills · 11개 Agents · 39개 Scripts · 5계층 Hook System을 갖추고 있다. 3개 병렬 분석 결과, **순 중복 제거 가능 14개** (에이전트 6 + 스킬 8), **bkit 차용 권장 22개** (에이전트 4 + 스킬 9 + Hook 기능 9), **시너지 통합 포인트 6개**가 도출되었다. 즉시 적용 가치가 가장 높은 항목은 Ambiguity Score 기반 Broad Request 고도화, PreCompact Hook 상태 보존, gap-detector 정량 비교 패턴이며, 이를 통해 Agent Teams 워크플로우의 안정성과 품질 게이트 정확도를 유의미하게 향상시킬 수 있다.

---

## 2. bkit 아키텍처 개요

### 규모와 구조

bkit v1.5.0은 Vibecoding Kit으로 총 22개 Skills, 11개 Agents, 39개 Scripts, 5계층 Hook System (UserPromptSubmit → PreToolUse → PostToolUse → PreCompact → Stop)으로 구성된다. Context Engineering FR-01~FR-08을 체계적으로 구현하며, 에이전트 모델 전략은 분석(opus) / 실행(sonnet) / 빠른 처리(haiku)로 3-tier를 유지한다. PDCA Check-Act 자동 반복 루프는 Match Rate를 기반으로 작동하며, 모호성 점수(Ambiguity Score)는 7개 팩터와 Magic Word Bypass를 포함한다.

### 핵심 강점 3가지

| # | 강점 | 설명 |
|---|------|------|
| 1 | **Context Engineering 체계성** | FR-01~FR-08 전 요건 구현, 4계층 계층 구조, @import Directive 지원 |
| 2 | **Ambiguity Score 시스템** | 7개 팩터 기반 정량 모호성 측정 + Magic Word Bypass로 False Positive 억제 |
| 3 | **PreCompact + SessionStart Hook 조합** | Context Compaction 이전 상태 저장 → 복원으로 장기 세션 연속성 보장 |

### 핵심 약점 3가지

| # | 약점 | 설명 |
|---|------|------|
| 1 | **미연결 Stop Hooks** | Stop Hook이 실제 워크플로우에 연결되지 않아 종료 조건 감지 불완전 |
| 2 | **bkend.ai 플랫폼 종속성** | 일부 기능이 bkend.ai 전용 API에 의존, 범용 이식 시 대체 필요 |
| 3 | **Context Fork 활용도 낮음** | 병렬 Agent 실행 시 Fork/Selective Merge 기능이 실제로 거의 사용되지 않음 |

---

## 3. 기능 중복 매핑

분류 기준:
- **A (순 중복)**: OMC와 동일 기능, 제거 가능
- **B (차용 권장)**: bkit 구현이 우수, OMC로 이식 권장
- **C (OMC 우수)**: OMC 구현이 더 성숙, 유지
- **D (시너지)**: 양측 결합 시 새로운 가치 창출

### 3.1 에이전트 매핑 (11개 분석)

| bkit 에이전트 | OMC 대응 | 분류 | 비고 |
|--------------|----------|:----:|------|
| code-analyst | architect / analyst | A | OMC architect가 상위 집합 |
| doc-writer | writer | A | 기능 동일 |
| test-runner | qa-tester | A | OMC qa-tester가 더 풍부 |
| review-agent | code-reviewer | A | 기능 동일 |
| deploy-agent | executor (ops) | A | OMC executor로 대체 가능 |
| search-agent | researcher | A | OMC researcher가 범용성 높음 |
| gap-detector | (없음) | B | 설계 vs 구현 정량 비교, 즉시 이식 권장 |
| design-validator | (없음) | B | UI/UX 설계 검증 전문 에이전트 |
| enterprise-expert | (없음) | B | 엔터프라이즈 도메인 지식 전문화 |
| starter-guide | (없음) | B | 초보자 온보딩 가이드 전문 에이전트 |
| pdca-iterator | quality_team (PDCA) | D | bkit 반복 루프 + OMC QA 사이클 결합 |

### 3.2 스킬 매핑 (22개 분석)

| bkit 스킬 | OMC 대응 | 분류 | 비고 |
|-----------|----------|:----:|------|
| /search | /research | A | /research가 상위 집합 |
| /document | /auto (--gdocs) | A | 기능 포함됨 |
| /test | /check (--e2e) | A | /check --e2e로 대체 |
| /review | /check (code) | A | /check로 통합 |
| /format | /check (--fix) | A | ruff/prettier 동일 |
| /deploy | /auto Phase 5 | A | /auto 배포 Phase로 대체 |
| /status | /check | A | 기능 중복 |
| /refactor | /auto (리팩토링) | A | /auto 요청으로 처리 |
| /ambiguity-check | (없음) | B | Ambiguity Score 계산 스킬 |
| /context-fork | (없음) | B | Agent 병렬 컨텍스트 분기 |
| /session-restore | (없음) | B | Session Hook 상태 복원 |
| /gap-report | (없음) | B | 설계-구현 Gap 리포트 생성 |
| /import-context | (없음) | B | @import Directive 처리 |
| /level-detect | (없음) | B | 프로젝트 레벨 자동 감지 |
| /pdca-archive | (없음) | B | PDCA 결과 아카이브 |
| /evaluator | (없음) | B | Evaluator-Optimizer 패턴 |
| /conflict-detect | (없음) | B | Context 계층 간 충돌 감지 |
| /auto (bkit) | /auto | C | OMC /auto가 PDCA Phase 더 정교 |
| /commit (bkit) | /commit | C | OMC /commit이 Conventional Commit 완전 지원 |
| /debug (bkit) | /debug | C | OMC /debug가 D0-D4 Phase 더 체계적 |
| /parallel (bkit) | /parallel | C | OMC Agent Teams 병렬화가 더 성숙 |
| /tdd (bkit) | /tdd | D | bkit Red-Green 엄격성 + OMC hook 결합 |

### 3.3 Hook 시스템 비교

| Hook 종류 | bkit 구현 | OMC 구현 | 분류 |
|-----------|-----------|----------|:----:|
| UserPromptSubmit | Ambiguity Score 계산 + 레벨 감지 | Broad Request Detection (단순) | D (결합 권장) |
| PreToolUse | 도구 사용 전 검증 (파일 경로 등) | tool_validator.py (프로세스 종료 방지) | C (OMC 우수) |
| PostToolUse | 결과 품질 검사 | post_edit_check.js (TDD 준수 확인) | D (결합 권장) |
| PreCompact | 상태 직렬화 저장 | (없음) | B (즉시 이식) |
| Stop | 종료 조건 감지 (미연결) | (없음) | B (개선 후 이식) |
| SessionStart | 이전 상태 복원 | session_init.py (경고만) | B (복원 기능 추가) |

---

## 4. 즉시 적용 가능한 개선점 (High Priority)

### 4.1 Ambiguity Score 도입

**현재 문제**: OMC의 Broad Request Detection은 동사 패턴 매칭(improve, enhance 등) 기반 단순 규칙으로, False Positive와 False Negative가 빈번히 발생한다.

**bkit 접근법**: 7개 팩터(동사 모호성, 대상 미특정, 파일 언급 여부, 범위 추정, 의존성 수, 질문 vs 명령 여부, Magic Word 포함)를 0-1 스코어로 합산. 점수 0.6 이상 시 계획 단계 진입. Magic Word("just", "quickly", "simply")가 있으면 점수를 0.3 차감하여 False Positive 억제.

**적용 방안**:
```markdown
# CLAUDE.md 수정 대상: Broad Request Detection 섹션

기존 단순 패턴 매칭 → 7개 팩터 점수 계산으로 교체
Magic Word Bypass 추가 (just/quickly/simply → 점수 0.3 차감)
임계값: 0.6 이상 시 → /auto Phase 1 진입
```

**영향 범위**: `CLAUDE.md` Broad Request Detection 섹션, `~/.claude/CLAUDE.md` DELEGATION-FIRST 섹션.

---

### 4.2 PreCompact 상태 보존 Hook

**현재 문제**: Context Compaction 발생 시 진행 중이던 작업 상태(TODO 목록, 현재 Phase, 미완료 파일 목록)가 소실되어 Compaction 이후 맥락 재구성에 큰 비용이 든다.

**bkit 접근법**: PreCompact Hook에서 현재 상태를 `.omc/context/compact_summary.md`에 직렬화 저장. SessionStart Hook에서 해당 파일 존재 시 자동 복원하여 세션 연속성 유지.

**적용 방안**:
```bash
# .claude/hooks/pre-compact.sh (신규 생성)
python .omc/scripts/save_compact_state.py \
  --output .omc/context/compact_summary.md \
  --include todos,phase,in-progress-files
```

**영향 범위**: `.claude/hooks/` (신규 파일 2개), `.omc/context/` 디렉토리, `session_init.py` 수정.

---

### 4.3 gap-detector 패턴 강화

**현재 문제**: OMC의 Architect Gate는 "승인/거부" 이진 판단만 제공하며, 설계 문서 대비 구현 커버리지를 정량적으로 측정하는 수단이 없다.

**bkit 접근법**: gap-detector 에이전트가 설계 문서(`.design.md`)의 요구사항을 파싱하여 구현 파일과 1:1 매핑. Match Rate(%) 계산 후 임계값(기본 90%) 미달 시 자동 ITERATE. 구체적 Gap 목록을 리포트로 출력.

**적용 방안**:
- `.claude/agents/gap-detector.md` 신규 작성 (bkit 패턴 이식)
- `/auto` Phase 3(Check) 완료 후 gap-detector 자동 호출
- Match Rate < 90% → Phase 2(Do) 재진입 규칙 추가

**영향 범위**: `.claude/agents/gap-detector.md` (신규), `.claude/skills/auto/SKILL.md` Phase 3 섹션.

---

### 4.4 Session Start 상태 복원

**현재 문제**: `session_init.py`는 TDD 미준수 경고만 출력하며, 이전 세션에서 중단된 작업의 복원 기능이 없다.

**bkit 접근법**: SessionStart Hook에서 `.omc/context/compact_summary.md` 존재 여부 확인 → 존재 시 요약 내용을 첫 번째 메시지로 자동 주입하여 "이전 작업에서 X 단계까지 진행했습니다" 형태로 연속성 제공.

**적용 방안**:
```python
# session_init.py 수정
if Path('.omc/context/compact_summary.md').exists():
    summary = Path('.omc/context/compact_summary.md').read_text()
    print(f"[Session Restore] 이전 상태 감지:\n{summary}")
```

**영향 범위**: `.claude/hooks/session_init.py` (수정), `.omc/context/` 디렉토리.

---

## 5. 중기 적용 개선점 (Medium Priority)

### 5.1 Context Hierarchy 계층화

bkit의 4-Level Context Hierarchy (Global → Project → Session → Task)를 OMC에 명시적으로 적용한다. 현재 OMC는 Global(`~/.claude/CLAUDE.md`) + Project(`CLAUDE.md`) 2계층만 명시적으로 관리하며, Session/Task 레벨은 암묵적으로만 존재한다.

**적용 방안**: `.omc/context/hierarchy.md`에 4계층 계층 구조 문서화, 계층 간 충돌 발생 시 하위 계층 우선 원칙 명문화. `/check` 실행 시 계층 충돌 탐지 단계 추가.

**영향 범위**: `.omc/context/` 디렉토리 구조, `docs/BUILD_TEST.md` 업데이트.

---

### 5.2 @import Directive 시스템

bkit의 `@import` Directive는 Skill 실행 시 필요한 참조 컨텍스트를 동적으로 주입하는 메커니즘이다. 현재 OMC Skill은 SKILL.md에 정적으로 컨텍스트를 기술하며, 동적 주입 수단이 없다.

**적용 방안**: SKILL.md 상단에 `<!-- @import: path/to/reference.md -->` 주석 규약 도입. Skill 실행 에이전트가 이를 파싱하여 해당 파일 내용을 컨텍스트에 prepend.

**영향 범위**: `.claude/skills/` 전체 SKILL.md 파일 (점진적 적용), `.claude/agents/executor.md`.

---

### 5.3 프로젝트 레벨 자동 감지

bkit의 level-detect 스킬은 프로젝트 복잡도(파일 수, 의존성 수, 팀 규모 추정)를 분석하여 적합한 워크플로우 레벨(starter/standard/enterprise)을 자동 판단한다.

**적용 방안**: `/auto` Phase 0에서 level-detect 로직 통합. 복잡도 5점제(현재)에 "프로젝트 레벨 배수"를 적용하여 팀 배치 결정을 정교화. `CLAUDE.md`의 팀 배치 규칙 테이블에 프로젝트 레벨 열 추가.

**영향 범위**: `.claude/skills/auto/SKILL.md` Phase 0 섹션, `src/agents/config.py` COMPLEXITY_TEAM_MAP.

---

### 5.4 /pdca archive 기능

bkit의 `/pdca archive` 스킬은 완료된 PDCA 사이클의 결과(계획, 실행 로그, Check 결과, Act 내용)를 타임스탬프 기반으로 아카이브한다.

**적용 방안**: `/auto` Phase 5 완료 시 `.omc/plans/archive/` 디렉토리에 결과 자동 저장. 파일명 규약: `{feature}-{date}.md`. 기존 `.omc/plans/archive/` 디렉토리 구조 그대로 활용 가능.

**영향 범위**: `.claude/skills/auto/SKILL.md` Phase 5 섹션, `.omc/plans/archive/` 디렉토리.

---

## 6. 시너지 통합 제안 (Strategic)

### 6.1 이중 라우팅 (레벨감지 + 복잡도점수)

**현재**: OMC 복잡도 5점제(0-10) → 팀 배치.
**bkit**: 프로젝트 레벨(starter/standard/enterprise) → 워크플로우 분기.
**시너지**: 두 시스템을 결합하면 `복잡도 점수 × 프로젝트 레벨 배수`로 더 정확한 팀 배치 결정 가능. 예: 복잡도 6점 × enterprise 배수(1.5) = 9점 → 전체 4팀 투입.

---

### 6.2 Evaluator-Optimizer 패턴 통합

**현재**: OMC Architect Gate는 "승인/거부" 이진 판단.
**bkit**: Evaluator가 점수화 → Optimizer가 개선 제안 → 재평가 루프.
**시너지**: `/auto` Phase 3(Check)에 Evaluator-Optimizer 루프 통합. Architect가 점수(0-100)와 구체적 개선 제안을 동시에 제공하면, executor가 개선 후 재검증하는 자동 루프 구성.

---

### 6.3 9-Phase 도메인 지식 주입

**현재**: OMC `/auto` Phase 0-5가 일반 목적 워크플로우.
**bkit**: 9-Phase 시스템이 각 Phase에 도메인 특화 지식(WSOP 방송, OTT 업로드 등)을 주입.
**시너지**: `/auto` Phase별 도메인 컨텍스트 @import 지원. 프로젝트별 `docs/.domain-context.md` 파일을 Phase 시작 시 자동 주입하여 도메인 전문성 향상.

---

### 6.4 pdca-iterator + QA 사이클 결합

**현재**: OMC quality_team이 PDCA 사이클 검증.
**bkit**: pdca-iterator가 Match Rate 기반 자동 반복.
**시너지**: quality_team에 Match Rate 임계값 기반 자동 ITERATE 로직 통합. 현재 수동으로 "재실행해야 하는" 상황을 자동화.

---

### 6.5 zero-script-qa + qa-tester 결합

**현재**: OMC qa-tester가 테스트 실행 및 결과 분석.
**bkit**: zero-script-qa가 스크립트 없이 LLM 기반 품질 검사.
**시너지**: qa-tester 실행 실패(환경 미비) 시 zero-script-qa로 자동 폴백. 환경 독립적 품질 검사 보장.

---

### 6.6 Context Fork + Agent Teams 결합

**현재**: OMC Agent Teams가 병렬 에이전트 실행 시 공유 상태 관리.
**bkit**: Context Fork가 병렬 에이전트별 독립 컨텍스트 제공.
**시너지**: Agent Teams 병렬 실행 시 팀별로 Context Fork 적용하여 상태 충돌 방지. Selective Merge로 각 팀 결과만 선택적으로 통합.

---

## 7. 차용 불필요 항목 및 사유

| bkit 기능 | 차용 불필요 사유 |
|-----------|----------------|
| 8언어 하드코딩 트리거 테이블 | LLM 기반 라우팅이 더 유연, 하드코딩 유지보수 부담 높음 |
| confidence 0.8 하드코딩 | 임계값 고정은 오히려 유연성 저하, OMC의 점수 기반 동적 임계값이 우수 |
| bkend.ai 전용 API 호출부 | 플랫폼 종속성 문제, 이식 시 대체 필요하여 ROI 낮음 |
| Docker 기반 실행 환경 | Windows 환경(C:\claude)과 충돌, PowerShell 기반 현재 환경과 불일치 |
| UserPromptSubmit 버그 대응 코드 | GitHub #20659 버그는 Claude Code 업데이트로 해결 예정, 임시 코드 이식 불필요 |
| Stop Hook (미연결 상태) | 현재 bkit에서도 미연결이며, 연결 완성 후 재검토 권장 |
| 미성숙한 Ambiguity Score 서브팩터 | confidence 0.8 하드코딩 등 미성숙 요소 제거 후 핵심 로직만 이식 |

---

## 8. 구현 로드맵

### Phase 1: 즉시 (이번 주)

| 작업 | 파일 | 복잡도 |
|------|------|:------:|
| Ambiguity Score → CLAUDE.md Broad Request Detection 교체 | `CLAUDE.md`, `~/.claude/CLAUDE.md` | Low |
| PreCompact Hook 스크립트 작성 | `.claude/hooks/pre-compact.sh`, `.omc/scripts/save_compact_state.py` | Medium |
| session_init.py 상태 복원 기능 추가 | `.claude/hooks/session_init.py` | Low |
| gap-detector 에이전트 이식 | `.claude/agents/gap-detector.md` | Low |

### Phase 2: 1주 내

| 작업 | 파일 | 복잡도 |
|------|------|:------:|
| /auto Phase 3에 gap-detector 자동 호출 통합 | `.claude/skills/auto/SKILL.md` | Medium |
| Context Hierarchy 4계층 문서화 | `.omc/context/hierarchy.md` | Low |
| /pdca archive 기능 추가 | `.claude/skills/auto/SKILL.md` Phase 5 | Low |
| /auto Phase 0에 level-detect 로직 통합 | `.claude/skills/auto/SKILL.md` Phase 0 | Medium |

### Phase 3: 1개월 내

| 작업 | 파일 | 복잡도 |
|------|------|:------:|
| @import Directive 시스템 구현 | `.claude/agents/executor.md`, SKILL.md 전체 | High |
| Evaluator-Optimizer 루프 → /auto Phase 3 통합 | `.claude/skills/auto/SKILL.md`, `src/agents/quality_team.py` | High |
| Context Fork + Agent Teams 결합 | `src/agents/teams/base_team.py`, `src/agents/teams/coordinator.py` | High |
| pdca-iterator Match Rate 자동 ITERATE → quality_team 통합 | `src/agents/teams/quality_team.py` | Medium |

### 영향 파일 전체 목록

```
신규 생성:
  .claude/agents/gap-detector.md
  .claude/hooks/pre-compact.sh
  .omc/scripts/save_compact_state.py
  .omc/context/hierarchy.md

수정:
  CLAUDE.md                              (Broad Request Detection 교체)
  ~/.claude/CLAUDE.md                    (Ambiguity Score 섹션 추가)
  .claude/hooks/session_init.py          (상태 복원 기능)
  .claude/skills/auto/SKILL.md          (Phase 0, 3, 5 섹션)
  src/agents/config.py                   (COMPLEXITY_TEAM_MAP 프로젝트 레벨 배수)
  src/agents/teams/quality_team.py       (Match Rate 자동 ITERATE)
  src/agents/teams/base_team.py          (Context Fork 지원)
  src/agents/teams/coordinator.py        (이중 라우팅 로직)
```

---

## 9. Appendix

### 9.1 bkit 전체 파일 구조

```
bkit v1.5.0
├── Skills (22개)
│   ├── /auto, /commit, /debug, /tdd, /parallel  ← OMC와 중복 (C)
│   ├── /search, /document, /test, /review        ← OMC로 대체 가능 (A)
│   ├── /format, /deploy, /status, /refactor      ← OMC로 대체 가능 (A)
│   ├── /ambiguity-check, /context-fork           ← 이식 권장 (B)
│   ├── /session-restore, /gap-report             ← 이식 권장 (B)
│   ├── /import-context, /level-detect            ← 이식 권장 (B)
│   ├── /pdca-archive, /evaluator                 ← 이식 권장 (B)
│   ├── /conflict-detect                          ← 이식 권장 (B)
│   └── /tdd                                      ← 시너지 결합 (D)
│
├── Agents (11개)
│   ├── code-analyst, doc-writer, test-runner     ← 제거 가능 (A)
│   ├── review-agent, deploy-agent, search-agent  ← 제거 가능 (A)
│   ├── gap-detector, design-validator            ← 이식 권장 (B)
│   ├── enterprise-expert, starter-guide          ← 이식 권장 (B)
│   └── pdca-iterator                             ← 시너지 결합 (D)
│
├── Scripts (39개)
│   ├── Context Engineering (FR-01~FR-08)
│   ├── Ambiguity Score Calculator
│   ├── Context Fork / Selective Merge
│   └── PDCA Match Rate Calculator
│
└── Hooks (5계층)
    ├── UserPromptSubmit → Ambiguity Score + Level Detect
    ├── PreToolUse → 도구 검증
    ├── PostToolUse → 결과 품질 검사
    ├── PreCompact → 상태 직렬화 저장
    └── Stop → 종료 조건 감지 (미연결)
```

### 9.2 에이전트/스킬 전체 매핑 테이블

| bkit | 분류 | OMC 대응 | 우선순위 |
|------|:----:|----------|:--------:|
| **에이전트** | | | |
| code-analyst | A | architect / analyst | - |
| doc-writer | A | writer | - |
| test-runner | A | qa-tester | - |
| review-agent | A | code-reviewer | - |
| deploy-agent | A | executor | - |
| search-agent | A | researcher | - |
| gap-detector | B | (없음) | P0 |
| design-validator | B | (없음) | P1 |
| enterprise-expert | B | (없음) | P2 |
| starter-guide | B | (없음) | P2 |
| pdca-iterator | D | quality_team | P1 |
| **스킬** | | | |
| /search | A | /research | - |
| /document | A | /auto --gdocs | - |
| /test | A | /check --e2e | - |
| /review | A | /check | - |
| /format | A | /check --fix | - |
| /deploy | A | /auto Phase 5 | - |
| /status | A | /check | - |
| /refactor | A | /auto | - |
| /ambiguity-check | B | (없음) | P0 |
| /session-restore | B | (없음) | P0 |
| /gap-report | B | (없음) | P0 |
| /context-fork | B | (없음) | P1 |
| /import-context | B | (없음) | P1 |
| /level-detect | B | (없음) | P1 |
| /pdca-archive | B | (없음) | P2 |
| /evaluator | B | (없음) | P2 |
| /conflict-detect | B | (없음) | P2 |
| /auto (bkit) | C | /auto | - |
| /commit (bkit) | C | /commit | - |
| /debug (bkit) | C | /debug | - |
| /parallel (bkit) | C | /parallel | - |
| /tdd | D | /tdd + hooks | P1 |

**범례**: A=중복 제거 | B=차용 권장 | C=OMC 우수 유지 | D=시너지 결합 | P0=즉시/P1=1주/P2=1개월

---

*분석 문서 작성: executor (Sonnet 4.6) | 2026-02-18*
*기반 분석: bkit-arch-analyst, integration-analyst, context-analyst*
