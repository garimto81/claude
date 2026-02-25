# 컨텍스트 전문화 전략 검증 플랜

> **대상 문서**: `C:\claude\docs\04-report\context-specialization-strategy.md`
> **검증 방향**: 적대적 (Adversarial) — 치명적 결함 우선 발굴
> **생성일**: 2026-02-25 | **갱신**: 2026-02-25 (5축 검증 + 평가 매트릭스 + 권장 대안 추가)

---

## 분석 범위

4개 전략(A: CLAUDE.md 슬림화, B: 마이크로 스킬, C: 동적 프로파일링, D: 규칙 태그)을 5개 축(기술 실현성, 안전성, 유지보수, 논문 적용성, 운영 시나리오)으로 검증한다.

- **포함**: 전략 A/B/C/D 각각의 치명적/심각/중간 결함 분석, 전략별 평가 매트릭스, 실현 가능 대안
- **포함**: 실제 코드/파일 경로 기반 근거 제시, Claude Code 공식 동작 확인
- **제외**: 구현 코드 작성

---

## 발견된 문제점

### CRITICAL (전략 무효화 수준)

### F-1. CLAUDE.md 런타임 교체 메커니즘 부재 (전략 A, C)

**결함**: Claude Code는 세션 시작 시 CLAUDE.md를 정적으로 로드한다. `~/.claude/CLAUDE.md`와 프로젝트 루트 `CLAUDE.md` 두 파일이 항상 로드되며, 이 로딩 경로를 Hook이나 사용자 코드로 런타임에 변경할 수 있는 API가 존재하지 않는다.

**근거**:
- `C:\claude\.claude\hooks\session_init.py` (565줄): `SessionStart` hook은 `{"continue": true, "message": "..."}` JSON만 반환 가능. CLAUDE.md 로딩 경로를 제어하는 필드가 없다. Claude Code 공식 문서 확인: "For UserPromptSubmit and SessionStart, stdout is added as context that Claude can see and act on" — 즉 메시지 주입만 가능, 파일 로딩 제어 불가.
- `C:\claude\.claude\settings.json` (81줄): hooks 설정에 `contextFiles`, `claudeMdOverride`, `profileSwitch` 같은 필드가 존재하지 않는다.
- Claude Code 공식 동작: CLAUDE.md 파일은 디렉토리 계층 상 상위 경로에서 전부 로드, 하위 디렉토리는 on-demand 로드. 파일명이 `CLAUDE.md`가 아니면 자동 로드되지 않는다.
- GitHub Issue #8997 "[FEATURE] Dynamic/Lazy Agent Loading to Reduce Context Token Usage"가 OPEN 상태 — 공식 팀이 아직 구현하지 않은 기능.

**전략 A 영향**: "프로젝트 타입별 CLAUDE.md 프로필"은 실제로 `~/.claude/profiles/media.md`를 로드할 수 없다. `CLAUDE.md`라는 파일명이 아니면 자동 로드되지 않는다.
**전략 C 영향**: `session_init.py`가 "프로젝트 타입 감지 후 최적 컨텍스트 로드"하는 것이 불가능. hook은 메시지만 출력할 수 있고, context loading을 제어할 수 없다.

**심각도**: CRITICAL — 전략 A와 C의 핵심 전제가 무효화됨.

### F-2. 규칙 파일 태그 기반 선택 로드 메커니즘 부재 (전략 D)

**결함**: `.claude/rules/` 디렉토리 내 모든 `.md` 파일은 Claude Code에 의해 무조건 로드된다. 파일 내용에 `[ALL]`, `[DEV]`, `[MEDIA]` 같은 태그를 추가해도 Claude Code는 태그를 해석하여 선택적으로 로드하는 기능이 없다.

**근거**:
- `.claude/rules/` 디렉토리: 현재 6개 규칙 파일이 모두 항상 로드됨 (시스템 프롬프트의 `Contents of C:\claude\.claude\rules\...` 블록으로 확인 가능)
- Claude Code는 `.claude/rules/*.md`를 파일시스템에서 glob하여 전부 주입한다. 파일 단위 on/off만 가능하고, 파일 내부 태그 기반 부분 로드는 불가능하다.

**유일한 우회**: 파일을 물리적으로 이동/삭제하는 것인데, 이는 세션 중 동적 전환이 아니라 사전 설정이며, 34개 프로젝트 각각에 다른 rules 디렉토리를 유지해야 한다.

**심각도**: CRITICAL — 전략 D의 태그 시스템이 기술적으로 구현 불가.

### F-3. profile.yaml의 `skip_rules` / `active_rules` / `context_budget` Enforce 불가 (전략 A, C, D)

**결함**: 전략 문서가 제안하는 `profile.yaml`의 `skip_rules`, `active_rules`, `context_budget` 필드를 실제로 enforce하는 런타임이 존재하지 않는다. 이들은 가상 API이다.

**근거**:
- `C:\claude\.claude\profiles\` 디렉토리에 4개 YAML 파일(minimal, development, research, full)이 있으나, 이들은 도구 목록만 정의한다. 이 YAML을 읽고 적용하는 코드가 `session_init.py`나 다른 hook에 없다.
- `skip_rules`, `active_rules`는 Claude Code 공식 설정 스키마(https://json.schemastore.org/claude-code-settings.json)에 존재하지 않는 필드이다.
- `context_budget`은 Claude Code가 인식하는 설정이 아니다. 토큰 예산 제어는 사용자 수준에서 불가능하다.
- 검증: Grep으로 전체 코드베이스에서 `skip_rules|active_rules|context_budget` 검색 결과 0건 — 이 필드를 참조하는 코드가 존재하지 않는다.

**심각도**: CRITICAL — profile.yaml이 "선언만 가능, 실행 불가"인 죽은 설정 파일.

---

### SIGNIFICANT (심각한 설계 결함)

### S-1. /quick 스킬의 PRD-First 및 Architect 검증 우회 안전성 (전략 B)

**결함**: `/quick` 스킬은 "PRD-First 스킵 + Architect 검증 스킵"을 설계 목표로 한다. 이는 `C:\claude\.claude\rules\13-requirements-prd.md`와 `~/.claude/CLAUDE.md`의 "RULE 4: NEVER complete without Architect verification"을 명시적으로 우회한다.

**위험 시나리오**:
1. 사용자가 "변수명 변경"이라고 요청하지만, 실제로는 public API 시그니처를 변경 → PRD 없이 진행되어 breaking change 미문서화
2. "오타 수정"으로 위장된 로직 변경 (if → else 등) → Architect 검증 없이 통과
3. 10줄 기준의 판단이 수동적: "10줄 이하 변경"이지만 import 추가/삭제로 인한 연쇄 영향이 클 수 있음

**근거**:
- `~/.claude/CLAUDE.md` RULE 4: "NEVER complete without Architect verification" — 예외 없는 절대 규칙
- `13-requirements-prd.md`: "구현 완료 후 PRD 업데이트 없이 세션 종료 금지"
- 현재 `--skip-prd` 예외는 "hotfix, 오타, 설정, 리팩토링"으로 제한되어 있지만, /quick은 이 범위를 더 넓힌다

**심각도**: SIGNIFICANT — 안전 규칙 우회로 인한 regression 위험.

### S-2. 마이크로 스킬 간 보안 패치 동기화 부재 (전략 B)

**결함**: `/auto-media`, `/auto-data`, `/auto-ops` 등 마이크로 스킬은 `/auto`의 복사본이다. `/auto`에 보안 패치가 적용되어도 마이크로 스킬에 자동 전파되지 않는다.

**위험 시나리오**:
- `/auto` SKILL.md에 새로운 안전 규칙 추가 (예: "SQL injection 방지") → `/auto-data`에는 반영 안 됨
- `/auto` v22.4 → v22.5 업그레이드 시 5개 스킬 파일을 각각 수동 패치해야 함
- 현재도 `/auto` SKILL.md가 426줄이며, 이를 6개로 분기하면 유지보수 대상이 2500줄+로 폭증

**근거**:
- `C:\claude\.claude\skills\auto\SKILL.md`: 현재 단일 진입점이 모든 워크플로우를 통합 관리 (v22.4)
- 스킬 시스템에 "상속" 메커니즘이 없음 — 각 SKILL.md는 독립 파일
- 기존 경험 (`MEMORY.md`): 에이전트 마이그레이션 시 "내용 재작성 필수" — 파일명만 바꾸면 프로토콜 충돌 발생했음

**심각도**: SIGNIFICANT — 장기적으로 보안 drift 발생 확실.

### S-3. 안전 규칙 누락 위험 — 핵심 5개 (전략 A)

**결함**: CLAUDE.md 슬림화 시 다음 안전 규칙이 도메인 프로필에서 누락될 수 있다:

| 안전 규칙 | 현재 위치 | 누락 시 영향 |
|-----------|-----------|-------------|
| API 키 금지 | `C:\claude\CLAUDE.md` 핵심 원칙 | OAuth 대신 API 키 하드코딩 발생 |
| 프로세스 전체 종료 금지 | `C:\claude\CLAUDE.md` + `tool_validator.py` | node.exe 전체 종료 → VS Code 크래시 |
| branch_guard (main 보호) | `branch_guard.py` + `.claude/settings.json` | main 브랜치 직접 코드 수정 |
| PRD-First | `13-requirements-prd.md` | 요구사항 미문서화 |
| TDD | `04-tdd.md` | 테스트 없는 코드 배포 |

**위험**: "minimal.md"나 "docs.md" 프로필이 이들 중 일부를 포함하지 않을 경우, 해당 프로젝트에서 안전 규칙이 비활성화된다.

**근거**:
- `tool_validator.py`는 hook으로 실행되므로 CLAUDE.md와 독립적이지만, CLAUDE.md에 "프로세스 종료 금지"가 명시되지 않으면 에이전트가 hook을 우회하는 방법을 시도할 수 있다 (예: PowerShell 우회 명령)
- hook은 패턴 매칭 기반이므로 100% 차단을 보장하지 않는다

**심각도**: SIGNIFICANT — safety regression은 워크플로우 전체 신뢰도를 훼손.

### S-4. 에이전트 Lazy Loading의 기술적 불가능성 + 전제 오류 (전략 A, B)

**결함 1**: 전략 문서는 "42개 에이전트 중 5개만 기본 활성화, 나머지 Lazy Loading"을 제안하지만, Claude Code에 에이전트 활성/비활성 토글 메커니즘이 없다. GitHub Issue #8997이 정확히 이 기능을 요청하고 있으며 OPEN 상태이다.

**결함 2**: 전략 문서의 전제(P-3, 95-106줄) "42개 에이전트가 항상 시스템 프롬프트에 존재"가 부정확할 가능성이 있다. Claude Code 공식 문서에 따르면 에이전트는 "세션 시작 시 로드"되나, `Task()` 호출 시에만 해당 에이전트 정의가 subagent에 전달된다. 모든 에이전트 정의가 메인 context에 항상 포함되는 것은 아닐 수 있다 — 이 경우 에이전트 수 절감의 효과 자체가 미미하다.

**근거**:
- `C:\claude\.claude\agents/` 디렉토리에 42개 `.md` 파일 (총 7,117줄). Claude Code는 이 디렉토리를 스캔하여 사용 가능한 에이전트 목록을 구성한다.
- 에이전트를 "비활성화"하려면 파일을 물리적으로 이동/삭제해야 하는데, 이는 다른 프로젝트에서 해당 에이전트가 필요한 경우 문제가 된다.
- GitHub Issue #8997 "[FEATURE] Dynamic/Lazy Agent Loading to Reduce Context Token Usage" — 커뮤니티에서 동일한 문제 제기, 공식 미구현.
- GitHub Issue #7336 "Feature Request: Lazy Loading for MCP Servers and Tools (95% context reduction possible)" — MCP 수준에서도 lazy loading 미구현.

**심각도**: SIGNIFICANT — 전제 오류 + 기술적 불가능의 이중 문제.

---

### MODERATE (개선 가능하나 위험 존재)

### M-1. 프로젝트 클러스터 경계 모호성

**결함**: 전략 문서의 클러스터 매핑(286-307줄)에서 여러 프로젝트가 경계를 넘는다.

| 프로젝트 | 전략 문서 클러스터 | 실제 특성 | 충돌 |
|----------|-------------------|-----------|------|
| archive-analyzer | MEDIA | 파일 분류(DATA) + OCR(MEDIA) | MEDIA/DATA 중복 |
| wsoptv_flutter | WEB (292줄) | Flutter + 스트리밍 | WEB/MEDIA 중복 |
| automation_hub | DATA | PostgreSQL + Supabase + 자동화(OPS) | DATA/OPS 중복 |
| gg_ecosystem | DATA | 생태계 관리(OPS?) | DATA/OPS 모호 |

**근거**:
- `C:\claude\CLAUDE.md` 주요 하위 프로젝트 테이블: archive-analyzer = "미디어 파일 분류 및 MAM 시스템", automation_hub = "WSOP 방송 자동화 공유 인프라 (PostgreSQL, Supabase)"

**심각도**: MODERATE — 단일 프로필로 분류 불가능한 프로젝트가 다수 존재.

### M-2. 유지보수 파일 수 폭증

**결함**: 전략 전체 구현 시 추가되는 파일/설정:

```
신규 파일 목록:
  ~/.claude/profiles/ × 6개 (minimal, web, data, media, ops, docs)
  profile.yaml × 34개 (서브 프로젝트별)
  마이크로 스킬 SKILL.md × 4-5개 (/quick, /auto-media, /auto-data, /auto-ops)

  합계: ~45개 파일 추가

현재 유지보수 대상: CLAUDE.md ×2 + rules ×6 + SKILL.md ×1 = 9개
전략 후 유지보수 대상: 9 + 45 = 54개 (6배 증가)
```

**근거**:
- `MEMORY.md` "AGENTS_REFERENCE.md drift": 이미 42개 에이전트 정의와 문서가 쉽게 어긋남 → 54개 설정 파일은 drift 위험을 기하급수적으로 증가시킨다.

**심각도**: MODERATE — 유지보수 부담이 context 절감 효과를 상쇄할 가능성.

### M-3. 논문 결론의 적용 범위 오류

**결함**: 전략 문서가 인용하는 논문은 SWE-bench (GitHub Issue → PR 해결) 환경에서의 성능을 측정했다. 현재 워크플로우는 로컬 개발 환경 (34개 서브 프로젝트, Agent Teams, PDCA 5-Phase)으로, 논문의 실험 조건과 근본적으로 다르다.

| 논문 환경 | 현재 환경 | 차이 |
|-----------|-----------|------|
| 단일 레포 | 34개 서브 프로젝트 루트 레포 | 멀티 프로젝트 |
| 단일 에이전트 | 42개 에이전트 오케스트레이션 | Agent Teams |
| 1회성 작업 | 지속적 세션 (hook, state) | 상태 유지 |
| AGENTS.md 유무 | CLAUDE.md + rules + skills + agents | 다층 context |
| 벤치마크 점수 | 실제 개발 생산성 | 측정 지표 다름 |

**근거**:
- 논문 발견 "context files cause agents to follow instructions faithfully"는 CLAUDE.md의 안전 규칙(프로세스 종료 금지, branch_guard 등)이 **의도적으로** 충실히 따르게 하기 위한 것이다. 이 "비용"을 제거하면 안전성도 함께 제거된다.
- 논문의 "+2.7% 성능 향상"은 중복 제거 효과이며, 안전 규칙 제거 효과가 아니다.

**심각도**: MODERATE — 논문 결론을 이 환경에 직접 대입하면 오해석 위험.

### M-4. 자동 감지 실패 시 Fallback 미정의 (전략 C)

**결함**: `session_init.py`의 `detect_project_type()` 함수가 프로젝트 타입을 잘못 판단하거나 판단하지 못할 경우의 fallback이 "default" CLAUDE.md로만 정의되어 있다.

**위험 시나리오**:
- 신규 프로젝트 (marker 파일 없음) → default로 전락 → 과도한 context
- 혼합 프로젝트 (package.json + pandas) → 첫 번째 매칭으로 결정 → 잘못된 프로필
- `session_init.py`의 marker 목록이 현실을 반영하지 못하면 지속적 오분류

**심각도**: MODERATE — fallback이 기존보다 나빠지지는 않지만, 자동 감지에 대한 과도한 신뢰 위험.

### M-5. 기존 profiles/*.yaml과 전략 profiles/*.md의 충돌

**결함**: `C:\claude\.claude\profiles\` 디렉토리에 이미 4개의 `.yaml` 프로필(minimal, development, research, full)이 존재한다. 전략 A는 같은 디렉토리에 6개의 `.md` 프로필을 추가하려 한다. 두 시스템의 관계, 우선순위, 공존 방법이 정의되지 않았다.

**근거**:
- `C:\claude\.claude\profiles\minimal.yaml`: 도구 세트 중심 프로필 (Read, Write, Edit, Bash)
- 전략 A의 `minimal.md`: CLAUDE.md 슬림 버전 — 완전히 다른 목적

**심각도**: MODERATE — 네이밍 충돌 + 개념 혼동.

---

## 4. 근거 요약 (Evidence Matrix)

| 결함 ID | 근거 파일/소스 | 핵심 사실 |
|---------|---------------|-----------|
| F-1 | `C:\claude\.claude\hooks\session_init.py` | hook은 `{"continue", "message"}` JSON만 반환. context 제어 불가 |
| F-1 | `C:\claude\.claude\settings.json` | hooks 설정에 context/profile 관련 필드 없음 |
| F-1 | Claude Code 공식 문서 | "stdout is added as context" — 메시지 주입만, 파일 로딩 제어 불가 |
| F-2 | `.claude/rules/` 디렉토리 | 시스템이 모든 `.md` 파일을 무조건 로드 (시스템 프롬프트에서 확인) |
| F-2 | Claude Code 공식 문서 | "All markdown files automatically loaded, no configuration needed" |
| F-3 | `C:\claude\.claude\profiles\*.yaml` | 프로필이 존재하나 이를 읽는 코드가 hook에 없음 |
| F-3 | Grep 검색 (전체 코드베이스) | `skip_rules`, `active_rules`, `context_budget` 참조 코드 0건 |
| S-1 | `C:\claude\.claude\rules\13-requirements-prd.md` | PRD-First 예외 조건 명시 |
| S-1 | `~/.claude/CLAUDE.md` | RULE 4: Architect 검증 예외 없음 |
| S-2 | `C:\claude\.claude\skills\auto\SKILL.md` | 단일 SKILL.md v22.4, 상속 메커니즘 없음 |
| S-3 | `C:\claude\.claude\hooks\tool_validator.py` | 패턴 매칭 기반, 100% 차단 미보장 |
| S-4 | `C:\claude\.claude\agents\*.md` (42개, 7117줄) | 에이전트 활성/비활성 토글 메커니즘 없음 |
| S-4 | GitHub Issue #8997 | "[FEATURE] Dynamic/Lazy Agent Loading" — OPEN, 공식 미구현 |
| M-1 | `C:\claude\CLAUDE.md` 프로젝트 테이블 | archive-analyzer, wsoptv_flutter 등 경계 중복 |
| M-3 | 전략 문서 7-17줄 | 논문 환경: SWE-bench, 단일 레포, 단일 에이전트 |
| M-5 | `C:\claude\.claude\profiles\` | 기존 4개 .yaml + 제안 6개 .md 충돌 |

---

## 5. 검증 방법론 (Critic이 사용할 기준)

### 5.1 기술적 실현 가능성 검증 기준

| 검증 항목 | 통과 조건 | 검증 방법 |
|-----------|-----------|-----------|
| CLAUDE.md 런타임 교체 | 공식 API/설정이 존재한다 | Claude Code 문서 + settings.json 스키마 확인 |
| rules 태그 기반 선택 로드 | .claude/rules/ 파일 부분 로드 메커니즘이 있다 | 시스템 프롬프트에서 rules 로딩 방식 확인 |
| profile.yaml enforce | YAML을 읽고 적용하는 런타임 코드가 있다 | session_init.py + settings.json 검토 |
| 에이전트 Lazy Loading | 에이전트 활성/비활성 토글이 있다 | .claude/agents/ 로딩 메커니즘 확인 |
| session_init.py context 제어 | hook 반환값으로 context 변경 가능하다 | hook JSON schema 확인 |

### 5.2 안전성 검증 기준

| 검증 항목 | 통과 조건 | 검증 방법 |
|-----------|-----------|-----------|
| /quick 안전 우회 | 우회 가능한 시나리오가 0건이다 | 악용 시나리오 5건 시뮬레이션 |
| 핵심 안전 규칙 보존 | 모든 프로필에 5대 안전 규칙이 포함된다 | 각 프로필 파일 교차 검증 |
| 마이크로 스킬 보안 동기화 | 패치 전파 메커니즘이 정의되어 있다 | 스킬 파일 상속/포함 구조 확인 |

### 5.3 유지보수 복잡도 검증 기준

| 검증 항목 | 통과 조건 | 검증 방법 |
|-----------|-----------|-----------|
| 파일 수 증가 | 추가 파일 < 15개 | 전체 신규 파일 목록 카운트 |
| 단일 변경 시 수정 파일 수 | 워크플로우 규칙 변경 시 수정 대상 < 5개 파일 | 변경 전파 시뮬레이션 |
| drift 위험 | 자동 정합성 검사 도구가 있다 | /audit 커맨드 범위 확인 |

### 5.4 논문 적용 검증 기준

| 검증 항목 | 통과 조건 | 검증 방법 |
|-----------|-----------|-----------|
| 환경 동등성 | 논문 실험 환경과 현재 환경의 차이가 3건 이하이다 | 환경 비교 매트릭스 |
| 성능 지표 해석 | -2~3% 저하가 안전 규칙 제거가 아닌 중복 제거에서 비롯됨을 확인 | 논문 원문 재분석 |
| Total context 실제 감소 | 전략 적용 후 실제 토큰 수가 감소한다 | 전후 토큰 카운트 측정 |

---

## 6. 태스크 목록 (Tasks)

### Task 1: Claude Code Context Loading 메커니즘 실증 검증

**설명**: Claude Code가 CLAUDE.md, .claude/rules/, .claude/agents/ 파일을 실제로 어떤 시점에 어떤 방식으로 로드하는지 실증 실험으로 확인한다.

**수행 방법**:
1. 임시 `.claude/rules/test-tag-rule.md` 파일 생성 (내용: `[TEST] 이 규칙은 무시하세요`)
2. 세션 시작 후 시스템 프롬프트에 해당 내용이 포함되는지 확인
3. `session_init.py`에서 파일을 삭제/이동한 후 같은 세션에서 규칙 참조 여부 확인

**Acceptance Criteria**: rules 디렉토리의 모든 .md 파일이 세션 시작 시 정적으로 로드됨을 확인하거나 반증한다.

### Task 2: session_init.py Hook 반환값 스키마 검증

**설명**: SessionStart hook의 JSON 반환값에 context loading을 제어할 수 있는 필드가 있는지 확인한다.

**수행 방법**:
1. `session_init.py`에서 `{"continue": true, "contextFiles": ["path"]}` 같은 비표준 필드 반환 실험
2. Claude Code 소스 코드 또는 공식 문서에서 hook JSON schema 확인
3. 실제 테스트로 비표준 필드가 무시되는지 확인

**Acceptance Criteria**: hook이 context loading을 제어할 수 있으면 F-1이 해소되고, 아니면 F-1이 확정된다.

### Task 3: 안전 규칙 5대 항목 프로필별 보존 매트릭스 작성

**설명**: 전략 A가 제안하는 6개 프로필 각각에서 5대 안전 규칙이 어떻게 보존되는지 매트릭스를 작성한다.

**수행 방법**:
1. 5대 안전 규칙 목록 확정 (API 키 금지, 프로세스 종료 금지, branch_guard, PRD-First, TDD)
2. 각 규칙이 어디에 정의되어 있는지 확인 (CLAUDE.md vs rules vs hook)
3. hook 기반 규칙은 CLAUDE.md와 독립적으로 동작하는지 검증
4. CLAUDE.md 슬림화 시 hook 우회 시나리오 분석

**Acceptance Criteria**: 6개 프로필 x 5개 안전 규칙 = 30개 셀 매트릭스에서 모든 셀이 "보존됨" 또는 "위험+대안"으로 채워진다.

### Task 4: 마이크로 스킬 보안 패치 전파 시뮬레이션

**설명**: `/auto`에 보안 패치가 적용될 때 4개 마이크로 스킬에 자동 전파되는 메커니즘이 있는지 검증한다.

**수행 방법**:
1. 현재 스킬 시스템에 "상속" 또는 "include" 메커니즘이 있는지 확인 (`.claude/skills/` 구조 분석)
2. `/auto` SKILL.md에 새 규칙 1줄 추가 → 마이크로 스킬에 자동 반영되는지 확인
3. 수동 동기화가 필요한 경우 변경 전파 비용 산출

**Acceptance Criteria**: 자동 전파 메커니즘이 있으면 S-2가 해소되고, 없으면 S-2 확정 + 수동 동기화 비용 수치 제시.

### Task 5: 프로젝트 클러스터 경계 충돌 분석

**설명**: 34개 서브 프로젝트 중 단일 클러스터에 분류할 수 없는 프로젝트를 식별하고, 복수 프로필 적용 시 동작을 정의한다.

**수행 방법**:
1. 34개 서브 프로젝트 디렉토리 탐색 (`C:\claude\` 하위)
2. 각 프로젝트의 실제 파일 구성 확인 (package.json, requirements.txt, Dockerfile 등)
3. 전략 문서의 클러스터 매핑과 실제 특성 비교
4. 2개 이상 클러스터에 걸치는 프로젝트 목록 + 비율 산출

**Acceptance Criteria**: 경계 충돌 프로젝트가 전체의 30% 미만이면 전략이 유효하고, 30% 이상이면 클러스터 재설계 필요.

### Task 6: Total Context 실제 변화량 측정

**설명**: 전략 적용 후 실제 context 토큰이 감소하는지, 아니면 프로필/태그/스킬 추가로 오히려 증가하는지 측정한다.

**수행 방법**:
1. 현재 상태: CLAUDE.md x2 + rules x6 = 약 706줄 정확 카운트
2. 전략 A 적용 후: 프로필 .md 파일 줄 수 + 남은 공통 CLAUDE.md 줄 수
3. 전략 D 적용 후: 태그 주석이 추가된 rules 파일 줄 수
4. 전략 B 적용 후: 마이크로 스킬 SKILL.md 총 줄 수 vs 현재 단일 SKILL.md

**Acceptance Criteria**: 전략 적용 후 총 줄 수가 현재 706줄보다 줄어들면 "감소 효과 있음", 같거나 늘어나면 "감소 효과 없음".

### Task 7: 논문 환경 vs 현재 환경 동등성 분석

**설명**: 논문 (arxiv:2602.11988)의 실험 환경과 현재 환경의 차이를 체계적으로 분석하여 논문 결론의 적용 가능성을 판단한다.

**수행 방법**:
1. 논문 실험 설정 재확인 (SWE-bench, 단일 에이전트, 단일 레포)
2. 현재 환경 특성 정리 (34 서브 프로젝트, Agent Teams, PDCA, hook 시스템)
3. 차이점별 논문 결론 적용 가능성 판단
4. "중복 제거 효과"와 "안전 규칙 제거 효과" 분리

**Acceptance Criteria**: 논문 결론 중 직접 적용 가능한 항목과 불가능한 항목이 명확히 분류된다.

---

## 7. 위험 요소 (Risks)

### Edge Case 1: Hook 기반 안전과 CLAUDE.md 기반 안전의 분리
- `tool_validator.py`와 `branch_guard.py`는 hook으로 실행되므로 CLAUDE.md 내용과 독립적이다.
- 그러나 에이전트가 hook을 우회하는 창의적 방법을 찾을 수 있다 (예: `cmd.exe /c` 래핑).
- CLAUDE.md에 "절대 금지" 규칙이 없으면 에이전트가 우회를 시도할 동기가 생긴다.

### Edge Case 2: 프로필 오분류 시 연쇄 실패
- `detect_project_type()`이 wsoptv_flutter를 "web"으로 분류하면, 스트리밍 관련 에이전트(catalog-engineer)가 비활성화되어 핵심 기능 구현 불가.
- 사용자가 오분류를 인지하기까지 여러 실패 사이클이 발생할 수 있다.

### Edge Case 3: Context Compaction과 프로필의 상호작용
- Claude Code는 컨텍스트가 길어지면 자동 압축(compaction)한다 (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50`).
- 프로필로 context를 줄였더라도, 대형 작업에서 compaction이 프로필 내용을 삭제할 수 있다.
- 이 경우 줄인 프로필마저 소실되어, 규칙 없는 상태로 에이전트가 작동한다.

### Edge Case 4: 복수 클러스터 프로젝트 운영 시나리오
- wsoptv_flutter: MEDIA 클러스터이면서 동시에 Flutter(WEB) 특성 → profile 하나만 적용 시 절반의 기능 누락
- archive-analyzer: DATA + MEDIA 둘 다 해당 → OCR 규칙이 DATA 프로필에 없으면 핵심 기능 불가
- 전략 C의 `detect_project_type()`이 첫 매칭으로 결정하면, 나머지 특성은 무시된다

### Edge Case 5: /quick 10줄 경계 처리
- 전략 B의 `/quick`이 10줄 이하 변경만 허용하지만, 11줄 변경 시 자동 라우팅 메커니즘이 정의되지 않았다
- 사용자가 /quick으로 시작한 후 "한 줄만 더"를 반복하면 PRD/Architect 검증 없이 대규모 변경이 진행될 수 있다
- context_budget 800토큰 초과 시 행동이 미정의 — Claude Code에 토큰 예산 enforce 기능이 없으므로 이 숫자는 의미 없다

---

## 8. 전략별 평가 매트릭스

```
+--------+-------------+--------+----------+-------------+------+
| 전략   | 기술 실현성 | 안전성 | 유지보수 | 논문 적용성 | 종합 |
+--------+-------------+--------+----------+-------------+------+
| A      |    1/5      |  2/5   |   3/5    |    3/5      | 2/5  |
| B      |    4/5      |  2/5   |   2/5    |    3/5      | 3/5  |
| C      |    1/5      |  3/5   |   1/5    |    2/5      | 2/5  |
| D      |    1/5      |  3/5   |   2/5    |    3/5      | 2/5  |
+--------+-------------+--------+----------+-------------+------+
```

### 평가 근거

**전략 A (프로젝트 타입별 CLAUDE.md 슬림화)**
- 기술 실현성 1/5: CLAUDE.md 로딩 경로를 프로젝트별로 바꿀 공식 메커니즘이 없다 (F-1). `~/.claude/profiles/media.md`는 자동 로드 대상이 아니다.
- 안전성 2/5: 슬림화 과정에서 안전 규칙 누락 위험이 높다 (S-3). hook 기반 안전은 독립적이나 CLAUDE.md 규칙 부재 시 우회 동기 발생.
- 유지보수 3/5: 6개 프로필 파일 관리는 상대적으로 적지만, 기존 profiles/*.yaml과 네이밍 충돌 (M-5).
- 논문 적용성 3/5: "최소 & 보편적" 원칙 자체는 합리적이나, 멀티에이전트 환경에서의 검증이 없다 (M-3).

**전략 B (도메인별 마이크로 스킬)**
- 기술 실현성 4/5: 스킬 파일 추가는 기존 메커니즘으로 가능하다. /quick 구현도 기술적으로 문제없다.
- 안전성 2/5: /quick의 PRD-First + Architect 검증 우회가 규칙 위반 (S-1). 마이크로 스킬 보안 동기화 부재 (S-2).
- 유지보수 2/5: 426줄 SKILL.md가 6개로 분기 시 총 2500줄+ 유지보수 대상 (M-2). fork divergence 확실.
- 논문 적용성 3/5: 태스크 유형별 분리는 "관련 context만 로드" 원칙에 부합하나, 스킬 자체의 context 비용이 추가된다.

**전략 C (동적 컨텍스트 프로파일링)**
- 기술 실현성 1/5: session_init.py hook이 context loading을 제어할 수 없다 (F-1). profile.yaml enforce 불가 (F-3). 순수 가상 설계.
- 안전성 3/5: 자동 감지 + fallback 구조 자체는 안전하지만, 감지 실패 시 706줄 전체 로드 (M-4).
- 유지보수 1/5: 34개 profile.yaml + session_init.py 확장 + marker 유지 = 유지보수 폭증. 프로젝트 변경 시 yaml 미갱신 위험.
- 논문 적용성 2/5: 동적 프로파일링은 오히려 context 판단 복잡도를 증가시킨다. 논문은 정적 제거를 권장.

**전략 D (규칙 선택적 활성화)**
- 기술 실현성 1/5: .claude/rules/ 내 태그 기반 선택 로드 메커니즘이 Claude Code에 없다 (F-2). 파일 단위 물리적 이동만 가능.
- 안전성 3/5: [ALL] 태그에 안전 규칙을 집중하면 안전성 유지 가능하지만, 태그 시스템 자체가 구현 불가이므로 평가 무의미.
- 유지보수 2/5: 태그 주석 추가는 간단하나, enforce 메커니즘 없이는 죽은 주석에 불과.
- 논문 적용성 3/5: "프로젝트와 무관한 규칙 제거" 원칙은 합리적이나, 6개 규칙 파일 중 실제 무관한 것은 1-2개 수준.

---

## 9. 구현 가능한 권장 대안

CRITICAL 결함 3건(F-1, F-2, F-3)이 전략 A/C/D의 핵심 전제를 무효화하므로, Claude Code의 **실제 동작 메커니즘** 내에서 실현 가능한 대안을 제시한다.

### 대안 1: CLAUDE.md 정적 슬림화 (전략 A 변형, 구현 가능)

프로필 분기가 아닌, 단일 CLAUDE.md를 직접 축소한다.

```
현재 구조:
  ~/.claude/CLAUDE.md (165줄) — 글로벌 지침
  C:\claude\CLAUDE.md (171줄) — 프로젝트 지침

대안:
  ~/.claude/CLAUDE.md (80줄 이하) — 핵심 5규칙 + 위임 테이블만
  C:\claude\CLAUDE.md (80줄 이하) — 빌드/테스트 + 안전 규칙만
  중복 제거: 아키텍처 설명, 에이전트 목록 등 → 별도 참조 문서로 이동
```

**기술 근거**: CLAUDE.md 파일 자체를 편집하는 것은 항상 가능하다. 파일 분기가 아닌 내용 축소.
**논문 근거**: "에이전트가 없어도 파일/코드 탐색으로 알 수 있다면 제거" (황금 규칙)

### 대안 2: .claude/rules/ 파일 물리적 분리 (전략 D 변형, 구현 가능)

태그 시스템 대신, 서브 프로젝트별로 필요한 rules 파일만 symlink/junction한다.

```
현재: C:\claude\.claude\rules\ (6개 파일, 항상 전부 로드)

대안:
  C:\claude\.claude\rules\          — 공통 규칙만 (04-tdd.md, branch 관련)
  C:\claude\.claude\rules-media\    — 미디어 전용 규칙
  C:\claude\.claude\rules-dev\      — 개발 전용 규칙

  서브 프로젝트 예시:
  C:\claude\wsoptv_ott\.claude\rules\ → junction → rules + rules-media
  C:\claude\investment\.claude\rules\ → junction → rules + rules-dev
```

**기술 근거**: .claude/rules/ 디렉토리 내 파일을 물리적으로 분리하면 해당 디렉토리의 .md 파일만 로드된다. Junction은 session_init.py에서 이미 commands에 사용 중인 검증된 패턴이다.
**위험**: 서브 프로젝트별 junction 유지보수 부담. 그러나 session_init.py가 자동 생성하면 일회성.

### 대안 3: /auto SKILL.md 참조 분리 (전략 B 변형, 구현 가능)

마이크로 스킬을 만들지 않고, /auto SKILL.md에서 상세 내용을 REFERENCE.md로 분리한다.

```
현재: /auto SKILL.md (426줄 단일 파일)

대안:
  /auto SKILL.md (100줄) — 핵심 흐름 + 에이전트 호출 규칙만
  /auto REFERENCE.md (326줄) — Phase별 상세, 복잡도별 분기 등
  에이전트가 필요 시 Read("REFERENCE.md")로 참조
```

**기술 근거**: SKILL.md는 스킬 호출 시 로드된다. 내용을 줄이면 직접적으로 context 절감. 스킬 시스템에 상속은 없지만, 단일 파일을 작게 만드는 것은 가능하다.
**주의**: REFERENCE.md를 Read하는 추가 비용 발생 가능. 그러나 필요 시에만 로드하므로 항상 로드보다 효율적.

### 대안 4: 안전 규칙의 Hook 집중 전략 (안전성 보장)

CLAUDE.md 축소와 무관하게, 안전 규칙을 hook에 집중시켜 "CLAUDE.md 내용에 의존하지 않는 안전성"을 확보한다.

```
현재 hook:
  tool_validator.py — 위험 명령 차단 (Bash, Write, Edit)
  branch_guard.py — main 브랜치 보호

강화 방안:
  tool_validator.py에 추가 패턴:
    - API 키 하드코딩 감지 (Write/Edit 시 "sk-", "AKIA" 등 패턴 차단)
    - 10줄 초과 변경 감지 + 경고 (Architect 검증 권고 메시지)
  session_init.py에 추가:
    - 현재 프로젝트에 필요한 규칙 요약을 메시지로 주입
```

**기술 근거**: Hook은 CLAUDE.md 로딩과 독립적으로 실행된다. tool_validator.py의 패턴 매칭은 확장 가능한 검증 메커니즘이다. SessionStart hook의 메시지 주입은 context 주입과 동등한 효과를 낸다.

---

## 10. 결론

### 전반적 판정: 4개 전략 중 3개 기각, 1개 조건부 수용

| 전략 | 판정 | 이유 |
|------|------|------|
| A (CLAUDE.md 슬림화) | **조건부 수용** | 프로필 분기는 기각하되, 단일 CLAUDE.md 정적 축소는 유효하고 즉시 실행 가능 |
| B (마이크로 스킬) | **기각** | 기술적으로 가능하나, 안전 규칙 우회 + fork divergence 비용이 context 절감 효과를 초과 |
| C (동적 프로파일링) | **기각** | 핵심 전제(session_init.py context 제어)가 기술적으로 불가능. 순수 가상 설계 |
| D (규칙 태그) | **기각** | 태그 기반 선택 로드가 Claude Code에 존재하지 않는 기능. 물리적 분리로 대체 가능 |

### 핵심 발견

1. **전략 문서의 근본 오류**: 4개 전략 중 3개가 Claude Code에 존재하지 않는 기능(런타임 context 교체, 태그 기반 규칙 로드, profile.yaml enforce)을 전제로 한다. 이는 "있었으면 좋겠다"를 "있다"로 착각한 설계이다.

2. **논문 결론의 과대 적용**: 논문은 SWE-bench 단일 에이전트 환경에서 AGENTS.md 파일의 효과를 측정했다. 42개 에이전트 + Agent Teams + PDCA 워크플로우 환경에 직접 대입하는 것은 논문 범위를 벗어난다. 특히 "context 제거 시 +2.7% 향상"이 "안전 규칙을 포함한 모든 context를 줄여야 한다"로 해석되면 안전성 회귀가 발생한다.

3. **실행 가능한 경로**: 대안 1(정적 슬림화)과 대안 3(SKILL.md 참조 분리)는 Claude Code의 기존 메커니즘 안에서 즉시 실행 가능하며, 대안 2(rules 물리적 분리)는 Junction 패턴 확장으로 구현 가능하다. 이 3개 대안만으로도 전략 문서가 목표한 "706줄 → ~350줄" 절감에 근접할 수 있다.

4. **안전성 우선 원칙**: 어떤 context 최적화도 5대 안전 규칙(API 키 금지, 프로세스 종료 금지, branch_guard, PRD-First, TDD)을 약화시켜서는 안 된다. Hook 기반 안전성 강화(대안 4)를 CLAUDE.md 축소와 병행해야 한다.

---

## 11. 커밋 전략 (Commit Strategy)

```
docs(plan): strategy-validation 적대적 검증 플랜 완성
```

---

*생성일: 2026-02-25 | 갱신일: 2026-02-25 | 에이전트: planner | 복잡도: HEAVY*
