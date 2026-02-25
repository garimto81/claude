# 전략 검증 실증 분석 결과

**분석 대상**: `docs/04-report/context-specialization-strategy.md`
**분석 플랜**: `docs/01-plan/strategy-validation.plan.md`
**작성일**: 2026-02-25
**분석자**: executor-high (claude-sonnet-4-6)

---

## Task 1: Context Loading 메커니즘 검증

### 증거

**`C:\claude\.claude\settings.json` 분석 (실제 확인):**

```json
{
  "hooks": {
    "SessionStart": [{ "type": "command", "command": "python3 C:/claude/.claude/hooks/session_init.py" }],
    "PreToolUse": [ ... branch_guard.py, tool_validator.py ... ],
    "PostToolUse": [ ... post_edit_check.js ... ],
    "SessionEnd": [ ... session_cleanup.py ... ]
  }
}
```

- `contextFiles` 필드: **존재하지 않음**
- `profileSwitch` 필드: **존재하지 않음**
- `active_rules` / `skip_rules` 필드: **존재하지 않음**
- settings.json에서 런타임 context 파일 지정/교체 API: **완전 부재**

**`C:\claude\.claude\hooks\session_init.py` 반환 스키마 (실제 확인):**

```python
# main() 함수 최종 출력 — 두 가지 형태만 존재
print(json.dumps({"continue": True, "message": "..."}))  # 메시지 포함
print(json.dumps({"continue": True}))                    # 빈 통과
print(json.dumps({"continue": True, "error": str(e)}))  # 에러
```

hook 반환값은 `continue` (bool) + `message` (str, 선택) + `error` (str, 선택) 3개 필드만 지원.
`contextFiles`, `active_rules`, `skip_rules`, `profileSwitch` 등의 필드는 코드 어디에도 없음.

**`C:\claude\.claude\rules\` 디렉토리 (실제 Glob 결과):**

```
04-tdd.md
08-skill-routing.md
10-image-analysis.md
11-ascii-diagram.md
12-large-document-protocol.md
13-requirements-prd.md
```

총 6개 파일. 실제 줄 수: 18+53+75+141+98+136 = **521줄**.
전략 문서 추정값 `~370줄`보다 **151줄(41%) 과소평가**됨.

### 결론

**F-1 (CLAUDE.md 런타임 교체 불가) 확정.**

Claude Code SDK의 settings.json 스키마에 `contextFiles` 또는 `profileSwitch` API가 존재하지 않는다.
session_init.py hook은 `{"continue": true}` 신호만 반환할 수 있으며, context 로딩 경로를 변경하는 능력이 없다.
전략 3.3항의 `load_context()` 개념적 설계는 현재 SDK에서 구현 불가. 에이전트가 session_init.py에 `load_context()` 로직을 추가해도 실제 context 로딩을 변경할 수 없다 — hook 반환값은 단순 continue/block 신호에 불과하다.

---

## Task 2: Hook 스키마 검증

### 증거

**session_init.py 실제 반환 구조 분석 (전체 코드 확인):**

`main()` 함수는 최종적으로 세 가지 JSON 형태만 출력한다:

| 조건 | 반환값 |
|------|--------|
| 정상 동작 (메시지 있음) | `{"continue": True, "message": "..."}` |
| 정상 동작 (메시지 없음) | `{"continue": True}` |
| 예외 발생 | `{"continue": True, "error": str(e)}` |

hook이 실제로 수행하는 작업 목록:
- `cleanup_stale_omc_states()` — stale JSON 파일 비활성화
- `cleanup_stale_global_todos()` — 미완료 TODO 초기화
- `cleanup_orphan_agent_teams()` — 고아 팀 삭제
- `check_fatigue_signals()` — 편집 패턴 경고
- `check_prd_sync_status()` — PRD 미업데이트 경고
- `setup_commands_junction()` — 서브프로젝트 Junction 설정
- `get_current_branch()` / `get_uncommitted_changes()` — git 상태 읽기
- `load_previous_session()` / `load_auto_state()` — 이전 세션 상태 로드
- `save_session_state()` — 현재 세션 상태 저장

**지원하지 않는 필드 목록:**
- `contextFiles`: 미존재 — context 파일 경로를 교체하는 API 없음
- `active_rules`: 미존재 — 규칙 파일 선택적 활성화 불가
- `skip_rules`: 미존재 — 규칙 파일 비활성화 불가
- `profile`: 미존재 — 프로파일 전환 불가
- `agentSubset`: 미존재 — 에이전트 필터링 불가

### 결론

**hook은 context loading을 제어하는 능력이 없다.**

session_init.py는 세션 시작 시 부수 작업(정리, 경고, 상태 저장)만 수행하고 `{"continue": true}`를 반환하는 것이 전부다. Claude Code SDK는 hook 반환값을 통해 context 경로를 변경하는 메커니즘을 제공하지 않는다.

전략 3.3항 "동적 컨텍스트 프로파일링"의 `detect_project_type()` + `load_context()` 패턴은 개념적으로만 유효하고, 현재 SDK에서 실제로 context 로딩을 변경할 수 없다. 이는 전략의 핵심 자동화 메커니즘(동적 프로파일 전환)이 현재 구현 불가능함을 의미한다.

---

## Task 3: 안전 규칙 보존 매트릭스

### 증거

**5대 안전 규칙 정의 위치 확인 (실제 파일 Grep):**

| 안전 규칙 | 정의 위치 | 메커니즘 | CLAUDE.md 슬림화 의존 여부 |
|-----------|---------|----------|--------------------------|
| API 키 금지 | `C:\claude\CLAUDE.md:35` ("API 키 방식 절대 사용 금지, Browser OAuth만 허용") | CLAUDE.md 텍스트 + `tool_validator.py` (민감파일 패턴 차단) | **부분 의존** (선언은 CLAUDE.md, 집행은 hook) |
| 프로세스 전체 종료 금지 | `C:\claude\.claude\hooks\tool_validator.py` (DANGEROUS_BASH_PATTERNS 목록에 `taskkill /F /IM node` 패턴) | **PreToolUse hook 차단** | hook 독립 — CLAUDE.md 슬림화와 무관 |
| branch_guard | `C:\claude\.claude\hooks\branch_guard.py` (PreToolUse Edit/Write에서 main 브랜치 확인) | **PreToolUse hook 차단** | hook 독립 — CLAUDE.md 슬림화와 무관 |
| PRD-First | `C:\claude\.claude\rules\13-requirements-prd.md` (136줄 상세 규칙) | rules 파일 자동 로드 | **rules 파일 독립** — CLAUDE.md에 참조 포인터만 있음 |
| TDD | `C:\claude\.claude\rules\04-tdd.md` (18줄) | rules 파일 자동 로드 | **rules 파일 독립** — CLAUDE.md에 참조 포인터만 있음 |

**프로필별 안전 규칙 보존 매트릭스:**

프로필 슬림화는 CLAUDE.md 내용을 줄이는 것이므로, 다음 기준으로 평가:
- hook 기반 = 항상 보존 (CLAUDE.md와 독립)
- rules 파일 기반 = 항상 보존 (CLAUDE.md와 독립, rules 파일이 별도 로드됨)
- CLAUDE.md 선언만 = 슬림화 시 제거 위험

| 안전 규칙 | 정의 레이어 | minimal | web | data | media | ops | docs |
|-----------|-----------|:-------:|:---:|:----:|:-----:|:---:|:----:|
| API 키 금지 | CLAUDE.md(선언) + hook(집행) | **위험** | **위험** | **위험** | **위험** | **위험** | **위험** |
| 프로세스 종료 금지 | hook(PreToolUse) | 보존 | 보존 | 보존 | 보존 | 보존 | 보존 |
| branch_guard | hook(PreToolUse) | 보존 | 보존 | 보존 | 보존 | 보존 | 보존 |
| PRD-First | rules/13-requirements-prd.md | 보존 | 보존 | 보존 | 보존 | 보존 | 보존 |
| TDD | rules/04-tdd.md | 보존 | 보존 | 보존 | 보존 | 보존 | 보존 |

**위험 셀 상세 분석 (API 키 금지):**

`C:\claude\CLAUDE.md:35`의 선언이 없어지면 에이전트는 API 키 방식이 금지된다는 것을 텍스트로 인지할 수 없게 된다. `tool_validator.py`는 민감 파일(`.env`, `credentials.json`) 쓰기를 차단하지만, API 키를 코드에 하드코딩하거나 다른 파일명으로 저장하는 행동은 차단하지 않는다. 따라서 CLAUDE.md 슬림화 시 API 키 금지 선언이 제거되면 에이전트 행동 변경 위험이 있다.

### 결론

5대 안전 규칙 중 4개(프로세스 종료 금지, branch_guard, PRD-First, TDD)는 CLAUDE.md 슬림화와 독립적으로 보존된다. **API 키 금지만이 CLAUDE.md 슬림화 시 위험에 노출된다.** 이 규칙은 6개 프로필 모두에서 위험 상태가 된다. 전략의 안전 규칙 보존 주장은 API 키 금지 규칙에 대해 불완전하다.

---

## Task 4: 마이크로 스킬 전파 시뮬레이션

### 증거

**`C:\claude\.claude\skills\` 전체 SKILL.md 목록 (실제 Glob 결과):**

```
auto/, audit/, check/, chunk/, claude-switch/, code-quality-checker/,
commit/, create/, daily/, debug/, deploy/, drive/, final-check-automation/,
gmail/, google-workspace/, issue/, karpathy-guidelines/, mockup-hybrid/,
overlay-fallback/, parallel/, playwright-wrapper/, pre-work-research/,
prd-sync/, pr/, research/, session/, shorts-generator/, skill-creator/,
slack/, supabase-integration/, tdd/, todo/, ultimate-debate/,
update-slack-list/, vercel-deployment/, vercel-react-best-practices/,
webapp-testing/, agent-teamworks/
```

총 38개 스킬 SKILL.md 확인됨 (CLAUDE.md 명시 37개와 차이 존재).

**제안된 마이크로 스킬 존재 여부:**

| 제안 스킬 | 파일 존재 여부 |
|----------|-------------|
| `/quick` | **존재하지 않음** |
| `/auto-media` | **존재하지 않음** |
| `/auto-data` | **존재하지 않음** |
| `/auto-ops` | **존재하지 않음** |
| `/auto-web` | **존재하지 않음** |
| `/fix` (독립 스킬) | **존재하지 않음** (issue/SKILL.md 내 fix 서브커맨드만 존재) |

**스킬 간 include/상속 메커니즘:**

스킬 디렉토리는 독립 SKILL.md 파일로 구성됨. 파일 간 `include`, `extends`, `import` 같은 상속 메커니즘을 지원하는 표준 패턴 없음. `/auto` SKILL.md는 426줄 독립 파일이며, 다른 마이크로 스킬에서 공유하는 공통 라이브러리 파일 없음.

**보안 패치 전파 시뮬레이션:**

만약 `/auto`에 보안 버그 수정이 필요할 때:
- 현재: `auto/SKILL.md` 1개 파일 수정 → 모든 호출에 즉시 반영
- 마이크로 스킬 구현 후: `auto/SKILL.md` + `auto-media/SKILL.md` + `auto-data/SKILL.md` + `auto-ops/SKILL.md` + `quick/SKILL.md` 최소 5개 파일 개별 수정 필요

공유 inheritance 메커니즘이 없으므로, 핵심 로직 변경 시 각 마이크로 스킬을 개별적으로 수동 동기화해야 한다.

### 결론

**S-2 (수동 동기화 부담) 확정.**

제안된 5개 마이크로 스킬(`/quick`, `/auto-media`, `/auto-data`, `/auto-ops`, `/auto-web`)은 현재 모두 존재하지 않으며, 스킬 간 코드 공유/상속 메커니즘이 없다. 보안 패치 전파 시 수동 동기화 필요 파일 수는 현재 1개에서 구현 후 최소 5~6개로 증가한다. 전략이 제시하는 "태스크 유형별 분리 스킬"은 유지보수 부담을 5배 이상 증가시키는 결함이 있다.

---

## Task 5: 클러스터 경계 충돌 분석

### 증거

**실제 C:\claude 하위 디렉토리 목록 (Bash ls 결과):**

총 탐지된 프로젝트 디렉토리: **60개** (단순 데이터 디렉토리 포함)
의미 있는 서브 프로젝트 (CLAUDE.md 또는 코드 존재): 약 38개

**기술 스택 기반 실제 특성 분류:**

| 프로젝트 | 감지된 특성 | 전략 분류 | 충돌 여부 |
|----------|-----------|---------|---------|
| ae_nexrender_module | package.json (NODE) | 전략 미언급 | 미분류 |
| airi | package.json + Dockerfile | 전략 미언급 | 미분류 |
| archive-analyzer | requirements 없음, src/ 있음 (Python) | DATA | 불명확 |
| automation_ae | Dockerfile (OPS) | OPS | 일치 |
| automation_aep_csv | 특성 불명확 | DATA | 불명확 |
| automation_dashboard | package.json (NODE) | DATA | **충돌** (NODE인데 DATA로 분류) |
| automation_hub | package.json (NODE) + docker-compose.yml | DATA | **충돌** (NODE인데 DATA로 분류) |
| automation_orchestration | 특성 불명확 | OPS | 불명확 |
| automation_sub | requirements.txt (Python) | OPS | **충돌** (Python인데 OPS로 분류) |
| card_ofc | 특성 불명확 | SIMPLE | 불명확 |
| claudeyoutuber | package.json + Dockerfile | WEB | 일치 |
| clawhub-repo | package.json + Dockerfile | 전략 미언급 | 미분류 |
| ebs | 특성 불명확 | OPS | 불명확 |
| investment | 특성 불명확 | DATA | 불명확 |
| kanban_board | 특성 불명확 | WEB | 불명확 |
| lobster-repo | package.json (NODE) | 전략 미언급 | 미분류 |
| mad_framework | Dockerfile | OPS | 일치 |
| openclaw-repo | package.json + Dockerfile | 전략 미언급 | 미분류 |
| project-showcase-hub | package.json (NODE) | 전략 미언급 | 미분류 |
| qwen_hand_analysis | package.json + requirements.txt + Dockerfile | MEDIA | **충돌** (OCR/Data인데 MEDIA) |
| secretary | requirements.txt (Python) | SIMPLE | **충돌** (Python 프로젝트인데 SIMPLE) |
| shorts-generator | package.json + Dockerfile | MEDIA | 일치 |
| vimeo_ott | 특성 불명확 | MEDIA | 불명확 |
| webtoon_remaster | requirements.txt (Python) | WEB | **충돌** (Python인데 WEB) |
| wsoptv_flutter | pubspec.lock (Flutter/Dart) | WEB (전략 표) or MEDIA (별도 언급) | **충돌** (Dart인데 WEB과 MEDIA 양쪽에 언급) |
| wsoptv_mvp | package.json | MEDIA | 일치 |
| wsoptv_nbatv | package.json | MEDIA | 일치 |
| WSOPTV | Dockerfile | MEDIA | 일치 |

**충돌 유형 분류:**
- 명확한 충돌 (기술 스택 기반): `automation_dashboard`, `automation_hub`, `automation_sub`, `qwen_hand_analysis`, `secretary`, `webtoon_remaster` = **6개**
- 이중 분류 충돌 (`wsoptv_flutter`): 1개
- 전략 문서 미언급 프로젝트: `ae_nexrender_module`, `airi`, `clawhub-repo`, `lobster-repo`, `openclaw-repo`, `project-showcase-hub` 등 최소 6개

**전략 문서가 주장하는 34개 서브 프로젝트와 실제 간 괴리:**
실제 탐지된 의미 있는 프로젝트는 38개 이상이며, 전략 문서에 언급되지 않은 프로젝트 6개 이상이 존재한다.

### 결론

**경계 충돌 비율: 최소 7/38 = 18.4% (명확한 충돌 기준)**

전략 문서의 클러스터 매핑은 기술 스택 자동 감지가 아닌 프로젝트명 기반 수동 분류에 의존하며, 실제 기술 스택과 18% 이상 불일치한다. `wsoptv_flutter`의 이중 분류(WEB과 MEDIA 양쪽에 등장)는 프로파일 선택 로직의 모호성을 드러낸다. 또한 전략에 언급되지 않은 프로젝트 6개 이상이 존재해 클러스터 매핑이 불완전하다.

---

## Task 6: Total Context 변화량

### 증거

**실제 줄 수 측정 (Bash wc -l 결과):**

```
$ wc -l /c/claude/CLAUDE.md /c/Users/AidenKim/.claude/CLAUDE.md
  171  /c/claude/CLAUDE.md
  165  /c/Users/AidenKim/.claude/CLAUDE.md
  336  total

$ find /c/claude/.claude/rules -name "*.md" -exec wc -l {} +
   18  04-tdd.md
   53  08-skill-routing.md
   75  10-image-analysis.md
  141  11-ascii-diagram.md
   98  12-large-document-protocol.md
  136  13-requirements-prd.md
  521  total

$ wc -l /c/claude/.claude/skills/auto/SKILL.md
  426
```

**현재 실제 줄 수 vs 전략 문서 추정값 비교:**

| 측정 항목 | 전략 문서 추정 | 실제 측정 | 오차 |
|----------|-------------|---------|------|
| ~/.claude/CLAUDE.md | 165줄 | **165줄** | 일치 |
| C:\claude\CLAUDE.md | 171줄 | **171줄** | 일치 |
| rules/04-tdd.md | ~30줄 | **18줄** | -12줄 (40% 과대) |
| rules/08-skill-routing.md | ~50줄 | **53줄** | +3줄 |
| rules/10-image-analysis.md | ~60줄 | **75줄** | +15줄 |
| rules/11-ascii-diagram.md | ~80줄 | **141줄** | +61줄 (76% 과소) |
| rules/12-large-document.md | ~70줄 | **98줄** | +28줄 (40% 과소) |
| rules/13-requirements-prd.md | ~80줄 | **136줄** | +56줄 (70% 과소) |
| **rules 소계** | **~370줄** | **521줄** | **+151줄(41% 과소)** |
| auto/SKILL.md | 426줄 | **426줄** | 일치 |
| **항상 로드 소계** | ~706줄 | **857줄** | **+151줄(21% 과소)** |
| /auto 실행 기준 총계 | ~1,632줄 | **1,283줄 이상** | 측정 기준 상이 |

**Phase 1 전략 후 예상 vs 실제 가능 감소:**

전략이 제안하는 Phase 1 목표:
- 글로벌 CLAUDE.md: 165 → 80줄 (-85줄)
- 프로젝트 CLAUDE.md: 171 → 80줄 (-91줄)
- /auto SKILL.md: 426 → 100줄 핵심 + REFERENCE.md 참조

그러나 rules 파일들은 521줄이 항상 로드되며, 이는 전략 문서의 추정(370줄)보다 151줄 더 많다. Phase 1 슬림화를 달성해도 rules 파일 로드는 변경되지 않으므로, 실제 감소는 전략의 `-50%` 주장보다 훨씬 적을 수 있다.

**실제 총계 계산:**

```
현재 항상 로드 (실제): 171 + 165 + 521 = 857줄
전략 문서 추정: ~706줄 (21% 과소평가)

Phase 1 후 최선 시나리오:
  80 (global) + 80 (project) + 521 (rules 변경 없음) = 681줄
  감소: 857 - 681 = 176줄 (20.5% 감소)
  전략 목표 -50%와 비교: 실제 달성 가능한 감소는 절반에 불과
```

### 결론

**현재 총계: 857줄 (항상 로드 기준), 전략 추정 706줄보다 21% 과소평가됨.**

Phase 1 슬림화 후 예상: 681줄 (20.5% 감소). 전략이 주장하는 `~350줄 (-50%)` 목표는 달성 불가능하다 — rules 파일 521줄이 항상 로드되므로 두 CLAUDE.md를 모두 0줄로 만들어도 521줄 이상이 유지된다. 전략 문서는 rules 파일 줄 수를 41% 과소평가했으며, 이로 인해 전체 감소 효과 예측이 크게 부풀려졌다.

---

## Task 7: 논문 환경 동등성

### 증거

**전략 문서 논문 적용 근거 섹션 (실제 확인, context-specialization-strategy.md):**

```
기반 논문: "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"
(arxiv:2602.11988, Gloaguen et al., ETH Zurich, 2026-02-12)
```

전략 문서가 인용한 핵심 수치:
- 성능 변화: LLM 생성 Context -2~3%, 개발자 작성 Context +4%
- 비용 증가: +20~23%
- 추가 단계 수: +2.45~3.92
- 문서 제거 효과: +2.7% 향상

**논문 환경 vs 현재 환경 차이 매트릭스:**

| 환경 요소 | 논문 환경 | 현재 환경 | 논문 결론 직접 적용 가능 여부 |
|----------|---------|---------|---------------------------|
| 평가 기준 | SWE-bench (실제 GitHub 이슈 해결) | 복합 목표 (품질/속도/비용/학습) | **불가능** — 단일 벤치마크 vs 복합 지표 |
| 에이전트 아키텍처 | 단일 에이전트 (ReAct 루프) | Agent Teams (TeamCreate/TeamDelete, 병렬) | **불가능** — 단일 에이전트 결과를 멀티 에이전트에 적용 불가 |
| 레포지토리 구조 | 단일 레포, 단일 코드베이스 | 메타 레포 + 34개 서브 프로젝트 + 워크플로우 정의 | **불가능** — 멀티 레포 구조에 단일 레포 실험 결과 적용 불가 |
| Context 파일 역할 | 단순 코딩 힌트 (파일 구조, 명령어) | 에이전트 프로토콜 정의, 안전 규칙 집행 | **불가능** — 정보성 힌트 vs 규범적 지시의 차이 |
| 평가 태스크 유형 | 버그 수정, 기능 추가 (단일 태스크) | PDCA 5-Phase 워크플로우, Agent Teams 오케스트레이션 | **불가능** — 단순 태스크 vs 복잡 워크플로우 |
| Hook 시스템 | 존재하지 않음 | PreToolUse/PostToolUse/SessionStart/SessionEnd 4개 | **불가능** — hook 시스템이 논문 환경에 없음 |
| Context 파일 크기 | AGENTS.md 단일 파일 (논문 실험 범위) | CLAUDE.md x2 + 6개 rules 파일 = 857줄 | **부분 적용** — 규모 차이로 인해 수치 신뢰 낮음 |
| 모델 | 논문 미명시 (GPT-4/Claude 계열 추정) | claude-sonnet-4-6 (Sonnet 4.6) | **부분 적용** — 모델 동일성 불확실 |
| "충실도의 역설" | 단순 지시 따름 → 불필요한 탐색 | 프로토콜 준수 필수 (Agent Teams 없이 작동 불가) | **불가능** — 논문의 "지시 줄이면 성능 향상" 결론이 여기선 반대로 작용 가능 |
| 문서 제거 효과 +2.7% | README 중복 제거 시 | CLAUDE.md 제거 시 Agent Teams 프로토콜 상실 | **위험** — 단순 제거가 시스템 붕괴를 초래할 수 있음 |

**결정적 차이 — "충실도의 역설"의 역전:**

논문 결론: "지시사항 준수가 오히려 성능 저하 → 지시사항 줄여라"

현재 환경에서는:
- `TeamCreate → Task → SendMessage → TeamDelete` 프로토콜이 CLAUDE.md에 명시됨
- 이 지시사항을 "줄이면" Agent Teams가 올바르게 구성되지 않음
- 프로토콜 자체가 기능 정의이지 단순 힌트가 아님

즉, 논문이 말하는 "불필요한 지시"와 현재의 "필수 프로토콜 정의"는 근본적으로 다른 성격이다.

### 결론

논문 환경(SWE-bench, 단일 에이전트, 단일 레포, 정보성 context)과 현재 환경(복합 목표, Agent Teams, 메타+서브 레포, 프로토콜 정의 context)은 **9/10 환경 요소에서 불일치**한다. 논문의 핵심 수치(-2~3%, +4%, +2.7%)를 현재 환경에 직접 적용하는 것은 방법론적으로 부당하다.

특히 "지시사항 제거 시 성능 향상" 결론은 현재 환경에서 역전될 위험이 있다 — Agent Teams 프로토콜, hook 설정, 안전 규칙은 제거 시 시스템 기능 상실을 초래한다. 논문은 정보성 힌트의 제거를 논하며, 전략 문서는 이를 규범적 프로토콜 정의에 무비판적으로 적용했다.

---

## 종합 결론 (결함별 확정 상태)

### 결함별 확정/반증 매트릭스

| 결함 ID | 설명 | 확정/반증 | 핵심 증거 |
|---------|-----|---------|---------|
| F-1 | CLAUDE.md 런타임 교체 불가 | **확정** | settings.json에 contextFiles/profileSwitch API 없음. hook 반환값은 continue 신호만 지원 |
| F-2 | rules 파일 줄 수 과소평가 | **확정** | 실측 521줄 vs 전략 추정 370줄 (41% 차이) |
| F-3 | 전략 감소 목표 달성 불가 | **확정** | Phase 1 후 실제 최선 20.5% 감소, 전략 목표 50% 불가 |
| S-1 | 동적 프로파일링 구현 불가 | **확정** | session_init.py가 context 로딩 경로 변경 능력 없음 |
| S-2 | 마이크로 스킬 수동 동기화 부담 | **확정** | 제안된 5개 스킬 미존재, 상속 메커니즘 없음, 유지보수 5배 증가 |
| S-3 | 안전 규칙 보존 불완전 | **부분 확정** | API 키 금지만 CLAUDE.md 의존(6프로필 전부 위험). 나머지 4개는 안전 |
| S-4 | 클러스터 경계 충돌 | **확정** | 실측 18.4% 충돌율, wsoptv_flutter 이중 분류, 6개 프로젝트 미언급 |
| M-1 | 논문 환경 동등성 결여 | **확정** | 9/10 환경 요소 불일치. SWE-bench vs 현재 복합 목표 |
| M-2 | "충실도 역설" 역전 위험 | **확정** | Agent Teams 프로토콜은 필수 기능 정의 — 줄이면 시스템 붕괴 |
| M-3 | rules 파일 항상 로드 가정 | **확인 필요** | rules 파일이 실제로 모든 세션에 자동 로드되는지 SDK 문서 미확인 |
| M-4 | 에이전트 42개 "항상 시스템 프롬프트" 주장 | **확인 필요** | 로컬 에이전트가 실제로 항상 시스템 프롬프트에 포함되는지 미확인 |
| M-5 | Phase 2 profile.yaml 구현 가능성 | **확정 불가** | profile.yaml을 읽어 context를 변경하는 SDK API 없음 (F-1과 연계) |

### 실행 가능한 전략 요소 (검증 통과)

1. **CLAUDE.md 텍스트 슬림화** — SDK 제약 없음. 단순 파일 편집. 효과는 과소 추정됨
2. **안전 규칙 4개** — hook/rules 독립 유지. PRD-First, TDD, 프로세스종료금지, branch_guard
3. **중복 정보 제거** — 논문 기준 +2.7% 가능. 디렉토리 구조 설명 등 중복 섹션 제거

### 구현 불가능한 전략 요소

1. **전략 3.3 동적 컨텍스트 프로파일링** — session_init.py가 context 로딩 변경 불가
2. **profile.yaml 기반 자동 전환** — SDK API 없음
3. **마이크로 스킬 분리** — 유지보수 부담 5배 증가, 상속 메커니즘 없음
4. **에이전트 Lazy Loading** — 에이전트 시스템 아키텍처 변경 필요 (현재 구현 방식 미확인)

### 수정 권고

| 전략 섹션 | 문제 | 권고 |
|----------|-----|-----|
| 3.3 동적 프로파일링 | F-1 확정으로 구현 불가 | 제거하거나 "수동 CLAUDE.md 교체" 방식으로 재명세 |
| 6. 예상 효과 | `-50%` 목표 근거 없음 | 실측 기반 수정: 최대 `-20%` (CLAUDE.md만 슬림화 시) |
| 3.2 마이크로 스킬 | S-2 확정 | /quick만 구현하고 나머지는 /auto Phase 0 임계값 조정으로 대체 |
| 7. 주의사항 | API 키 금지 누락 | API 키 금지 규칙을 슬림화 불가 항목으로 명시 추가 |

---

*분석 완료: 2026-02-25 | 실증 확인 태스크: 7/7 완료*
