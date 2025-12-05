# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 3.5.0 | **Updated**: 2025-12-05 | **Context**: Windows 10/11, PowerShell, Root: `D:\AI\claude01`

## 1. Critical Rules

1. **Language**: 한글 출력. 기술 용어(code, GitHub)는 영어.
2. **Path**: 절대 경로만 사용. `D:\AI\claude01\...`
3. **Validation**: Phase 검증 필수. 실패 시 STOP.
4. **TDD**: Red → Green → Refactor. 테스트 없이 구현 완료 불가.
5. **Git**: 코드 수정은 브랜치 → PR 필수. main 직접 커밋 금지.

---

## 2. Workflow

### 요청 분류

| 요청 유형 | 자동 실행 |
|-----------|-----------|
| 신규 기능 / 리팩토링 | PRE_WORK → IMPL → FINAL_CHECK |
| 버그 수정 | PRE_WORK(light) → IMPL → FINAL_CHECK |
| 문서 수정 | 이슈 → 직접 커밋 |
| 단순 질문 | 직접 응답 |

### PRE_WORK
1. 오픈소스 검색 (MIT/Apache/BSD, Stars>500)
2. 중복 확인 (`gh issue/pr list`)
3. Make vs Buy 분석 → 사용자 승인

### IMPL
1. GitHub 이슈/브랜치 생성: `<type>/issue-<num>-<desc>`
2. TDD 구현
3. 커밋: `fix(scope): Resolve #123 🐛` / `feat(scope): Add feature ✨`

### FINAL_CHECK

E2E 테스트 → Phase 3~5 자동 진행 → Phase 6(배포)은 사용자 확인

> E2E 실행 방법 및 실패 처리: **섹션 7. Browser Testing & E2E** 참조

---

## 3. Phase Pipeline

| Phase | 핵심 | Validator |
|-------|------|-----------|
| 0 | PRD 생성 | `validate-phase-0.ps1` |
| 0.5 | Task 분해 | `validate-phase-0.5.ps1` |
| 1 | 구현 + 테스트 | `validate-phase-1.ps1` |
| 2 | 테스트 통과 | `validate-phase-2.ps1` |
| 2.5 | 코드 리뷰 | `/parallel-review` |
| 3 | 버전 결정 | Conventional Commits |
| 4 | PR 생성 | `validate-phase-4.ps1` |
| 5 | E2E + Security | `validate-phase-5.ps1` |
| 6 | 배포 | 사용자 확인 필수 |

**자동 진행 중지**: MAJOR 버전, Critical 보안 취약점, 배포, 3회 실패

### 실패 시 디버깅 전략

해결 실패 시 **반드시** `docs/DEBUGGING_STRATEGY.md` 참조:

```
실패 → Phase 0: 디버그 로그 추가 → 로그 분석 → 예측 검증
         ↓
       Phase 1: 신규 기능 vs 기존 로직 판단
         ↓
       ┌─────────────┬─────────────┐
       │ 신규 기능   │ 기존 로직   │
       │ → PRD 검토  │ → 예측 검증 │
       │ → 리팩토링? │ → 가설 실험 │
       └─────────────┴─────────────┘
         ↓
       3회 실패 → /issue-failed → 수동 개입
```

**핵심 원칙**:
1. **로그 없이 수정 금지**: 추측 기반 수정은 새 버그 유발
2. **문제 파악 > 해결**: 문제를 정확히 알면 해결은 쉬움
3. **예측 검증 필수**: "내 예측이 로그로 확인되었는가?"

---

## 4. Agents

### 4.1 내장 Subagent (4개)

Claude Code **공식 내장** subagent. `Task(subagent_type="...")` 으로 직접 호출.

| 에이전트 | 용도 | 도구 |
|----------|------|------|
| `general-purpose` | 복잡한 다단계 작업 | 모든 도구 |
| `Explore` | 코드베이스 빠른 탐색 | Glob, Grep, Read |
| `Plan` | 구현 계획 설계 | 읽기 도구만 |
| `debugger` | 버그 분석/수정 | Read, Edit, Bash, Grep |

### 4.2 로컬 에이전트 - 활성 (7개)

`.claude/plugins/*/agents/*.md`에 정의. Commands에서 직접 참조됨.

| 에이전트 | 참조 위치 | Phase |
|----------|----------|-------|
| `debugger` | analyze-logs, fix-issue, tdd | 문제 시 |
| `backend-architect` | api-test | 1 |
| `code-reviewer` | check, optimize, fix-issue, tdd | 2.5 |
| `test-automator` | fix-issue, tdd | 2 |
| `security-auditor` | check, api-test | 5 |
| `playwright-engineer` | final-check | 2, 5 |
| `context7-engineer` | pre-work | 0, 1 |

### 4.3 로컬 에이전트 - 대기 (21개)

CLAUDE.md에 언급되었으나 Commands에서 직접 호출되지 않음. 필요 시 활성화.

| 분야 | 에이전트 |
|------|----------|
| **Phase 0** | `seq-engineer`, `exa-search-specialist`, `taskmanager-planner`, `task-decomposition-expert` |
| **Phase 1** | `frontend-developer`, `fullstack-developer`, `typescript-expert`, `mobile-developer` |
| **Phase 6** | `architect-reviewer`, `deployment-engineer`, `devops-troubleshooter`, `cloud-architect` |
| **전문** | `python-pro`, `graphql-architect`, `supabase-engineer`, `performance-engineer`, `github-engineer`, `database-architect`, `database-optimizer`, `context-manager` |

### 4.4 MCP 연동 에이전트 (3개)

| 에이전트 | MCP 도구 | 상태 |
|----------|---------|------|
| `exa-search-specialist` | `mcp__exa__search` | 활성 |
| `context7-engineer` | `mcp__ref__search` | 활성 |
| `context-manager` | `mcp__mem0__*` | 대기 |

### Phase별 권장 에이전트

| Phase | 내장 | 로컬 (활성) |
|-------|------|-------------|
| 0 (PRD) | `Plan`, `Explore` | `context7-engineer` |
| 1 (구현) | `debugger` | `backend-architect` |
| 2 (테스트) | - | `test-automator`, `playwright-engineer` |
| 2.5 (리뷰) | - | `code-reviewer`, `security-auditor` |
| 5 (E2E) | - | `playwright-engineer`, `security-auditor` |

★ **Browser Testing**: `playwright-engineer` 및 `webapp-testing` 스킬은 **모든 Phase에서 사용 가능**

### Agent-Workflow 연결

```
사용자 요청
    ↓
┌─────────────────────────────────────────────────────┐
│ Workflow (PRE_WORK → IMPL → FINAL_CHECK)            │
│     │           │            │                      │
│     ↓           ↓            ↓                      │
│ ┌───────┐  ┌────────┐  ┌───────────┐               │
│ │Explore│  │개발    │  │playwright │               │
│ │context│  │에이전트│  │security   │               │
│ └───────┘  └────────┘  └───────────┘               │
└─────────────────────────────────────────────────────┘
```

| Workflow 단계 | 호출 Agent | 역할 |
|---------------|------------|------|
| PRE_WORK | `Explore`, `context7-engineer`, `exa-search-specialist` | 코드 탐색, 기술 검증, 오픈소스 검색 |
| IMPL | `debugger`, `backend-architect`, `frontend-developer`, `test-automator` | 원인 분석, 구현, 테스트 |
| FINAL_CHECK | `playwright-engineer`, `security-auditor`, `code-reviewer` | E2E, 보안, 리뷰 |

### 슬래시 커맨드 → Agent 매핑

| 커맨드 | 호출 Agent (병렬) |
|--------|-------------------|
| `/parallel-dev` | `architect` + `coder` + `tester` + `docs` |
| `/parallel-test` | `unit` + `integration` + `e2e` + `security` |
| `/parallel-review` | `code-reviewer` + `security-auditor` + `architect-reviewer` |
| `/fix-issue` | `debugger` → 개발 에이전트 (순차) |

### 병렬 호출 예시

```python
# 단일 메시지에 여러 Task 호출 = 병렬 실행
Task(subagent_type="frontend-developer", prompt="UI 구현", description="프론트")
Task(subagent_type="backend-architect", prompt="API 구현", description="백엔드")
Task(subagent_type="test-automator", prompt="테스트 작성", description="테스트")
```

> 상세: `docs/AGENTS_REFERENCE.md`

---

## 5. Architecture

### 디렉토리 구조

```
D:\AI\claude01\
├── .claude/
│   ├── commands/      # 슬래시 커맨드 (28개)
│   ├── plugins/       # 로컬 에이전트 정의 (49개)
│   ├── skills/        # webapp-testing (E2E), skill-creator
│   └── hooks/         # 프롬프트 검증
├── src/agents/        # LangGraph 멀티에이전트
├── scripts/           # Phase Validators (PowerShell)
├── tasks/prds/        # PRD 문서
├── tests/             # pytest 테스트
└── archive-analyzer/  # 서브프로젝트 (별도 CLAUDE.md)
```

### LangGraph Multi-Agent Pattern

`src/agents/parallel_workflow.py` - Fan-Out/Fan-In 패턴:

```
                    ┌─────────────┐
                    │  Supervisor │ (sonnet) - 태스크 분해
                    │ supervisor_ │
                    │    node     │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐  ← Fan-Out
            ↓              ↓              ↓
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │  Agent 0  │  │  Agent 1  │  │  Agent 2  │  (병렬 실행)
    │(researcher)│ │(researcher)│ │(researcher)│
    └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
          │              │              │
          └──────────────┼──────────────┘  ← Fan-In
                         ↓
                  ┌─────────────┐
                  │ Aggregator  │ (sonnet) - 결과 종합
                  │   _node     │
                  └─────────────┘
```

**State Flow**:
```python
WorkflowState = {
    task: str,                          # 원본 태스크
    subtasks: list[str],                # supervisor가 분해
    results: Annotated[list, add],      # Reducer로 병합
    final_output: str                   # aggregator 출력
}
```

**Model Tiering** (`src/agents/config.py`):

| Role | Model | 용도 |
|------|-------|------|
| supervisor | sonnet | 복잡한 의사결정, 태스크 분해 |
| researcher | sonnet | 일반 태스크 실행 |
| validator | haiku | 간단한 검증 (비용 최적화) |

**Specialized Workflows**:
- `dev_workflow.py`: Architect/Coder/Tester/Docs 병렬
- `test_workflow.py`: Unit/Integration/E2E/Security 병렬

---

## 6. Commands (핵심)

| 커맨드 | 용도 |
|--------|------|
| `/autopilot` | 자율 운영 - 이슈 자동 처리 (토큰 한도까지) |
| `/fix-issue` | GitHub 이슈 분석 및 수정 |
| `/commit` | Conventional Commit 생성 |
| `/create-pr` | PR 생성 |
| `/parallel-dev` | 병렬 개발 에이전트 |
| `/tdd` | TDD 가이드 |
| `/check` | 코드 품질 검사 |
| `/issue-failed` | 실패 분석 + 새 솔루션 제안 |

> 전체 목록: `.claude/commands/`

---

## 7. Browser Testing & E2E

**모든 Phase에서** 브라우저 기반 테스트 가능. UI 검증이 필요할 때 즉시 사용.

### 사용 시점

| Phase | 브라우저 테스트 용도 |
|-------|---------------------|
| 1 (구현) | UI 컴포넌트 동작 확인, 레이아웃 검증 |
| 2 (테스트) | 통합 테스트, 사용자 플로우 검증 |
| 2.5 (리뷰) | UI/UX 리뷰, 접근성 확인 |
| 5 (E2E) | 전체 시나리오 테스트, 회귀 테스트 ← **FINAL_CHECK 자동 실행** |

### 실행 방법

```powershell
# 방법 1: Playwright 직접 실행
npx playwright test                         # 전체 테스트
npx playwright test --ui                    # UI 모드 (디버깅)
npx playwright test tests/e2e/flow.spec.ts  # 단일 파일

# 방법 2: webapp-testing 스킬 (서버 자동 관리)
python .claude/skills/webapp-testing/scripts/with_server.py \
  --server "npm run dev" --port 3000 \
  -- python your_test.py

# 방법 3: playwright-engineer 에이전트 호출
Task(subagent_type="playwright-engineer",
     prompt="로그인 → 대시보드 플로우 테스트",
     description="E2E 테스트")
```

### 빠른 검증 패턴

```python
# 현재 UI 상태 스크린샷 캡처
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:3000')
    page.wait_for_load_state('networkidle')
    page.screenshot(path='D:/AI/claude01/logs/ui_check.png', full_page=True)
    browser.close()
```

### E2E 실패 처리 (FINAL_CHECK)

| 시도 | 동작 |
|------|------|
| 1회 실패 | 스크린샷/로그 분석 → 자동 수정 |
| 2회 실패 | selector 재검증 → 수정 |
| 3회 실패 | ⏸️ `/issue-failed` → 수동 개입 |

**워크플로우**:
```
1. playwright-engineer 호출 또는 webapp-testing 스킬 사용
2. 테스트 실행: npx playwright test
3. 실패 시: 스크린샷 분석 → 자동 수정 (최대 3회)
4. 100% 통과 필수 → 실패 시 수동 개입
```

> 상세: `.claude/skills/webapp-testing/SKILL.md`

---

## 8. Build & Test

```powershell
# 단위 테스트
pytest tests/ -v
pytest tests/ -v -m unit                    # 단위 테스트만
pytest tests/test_parallel_workflow.py -v   # 단일 파일
pytest tests/test_file.py::test_func -v     # 단일 함수
pytest tests/ -v --cov=src --cov-report=term  # 커버리지

# Browser/E2E 테스트 → 섹션 7 참조

# 에이전트 실행
python src/agents/parallel_workflow.py "프로젝트 분석"
python src/agents/dev_workflow.py "새 기능 구현"

# Phase 상태
.\scripts\phase-status.ps1
.\scripts\validate-phase-5.ps1              # E2E + Security 검증
```

### archive-analyzer (서브프로젝트)

```powershell
cd D:\AI\claude01\archive-analyzer
pip install -e ".[dev,media,search]"
pytest tests/ -v
ruff check src/ && black --check src/ && mypy src/archive_analyzer/
uvicorn src.archive_analyzer.api:app --reload --port 8000
```

> 상세: `D:\AI\claude01\archive-analyzer\CLAUDE.md`

---

## 9. MCP Tools

`.mcp.json`에 설정된 외부 MCP 서버. `mcp__<server>__<tool>` 형태로 호출.

| MCP Server | 용도 | 호출 예시 |
|------------|------|----------|
| **exa** | 고급 웹 검색 (exa.ai) | `mcp__exa__search` |
| **mem0** | 대화 메모리 저장/조회 | `mcp__mem0__add_memory`, `mcp__mem0__search_memory` |
| **ref** | 참조 문서 검색 (ref.tools) | `mcp__ref__search` |
| **docfork** | 문서 포크/관리 | `mcp__docfork__*` |

### 사용 시점

| MCP | Phase | 용도 |
|-----|-------|------|
| **exa** | 0, PRE_WORK | 오픈소스/기술 트렌드 검색, 솔루션 조사 |
| **mem0** | 전체 | 중요 결정사항 저장, 이전 컨텍스트 조회 |
| **ref** | 0, 1 | API 문서, 라이브러리 레퍼런스 검색 |

### 에이전트 연결

| MCP | 내장 Subagent |
|-----|--------------|
| exa | `exa-search-specialist` |
| mem0 | `context-manager` (권장) |
| ref | `context7-engineer` (권장) |

### 예시

```python
# Exa 검색 (PRE_WORK에서 자동 사용)
mcp__exa__search(query="best React state management 2025")

# 메모리 저장 (중요 결정사항)
mcp__mem0__add_memory(content="DB 스키마: users 테이블에 role 컬럼 추가 결정")

# 메모리 조회 (이전 컨텍스트)
mcp__mem0__search_memory(query="DB 스키마 결정사항")
```

> 설정: `.mcp.json`

---

## 10. Environment

| 변수 | 용도 |
|------|------|
| `ANTHROPIC_API_KEY` | Claude API |
| `GITHUB_TOKEN` | GitHub CLI |
| `SMB_SERVER` / `SMB_USERNAME` / `SMB_PASSWORD` | NAS 접속 |
| `MEILISEARCH_URL` | 검색 서버 |
| `EXA_API_KEY` | Exa MCP 검색 |
| `MEM0_API_KEY` | Mem0 MCP 메모리 |
| `REF_API_KEY` | Ref MCP 문서 검색 |

> MCP 설정: `.mcp.json.example` 참조 → `.mcp.json`으로 복사 후 환경변수 설정

---

## 11. Do Not

- ❌ Phase validator 없이 다음 Phase 진행
- ❌ 상대 경로 사용 (`./`, `../`)
- ❌ PR 없이 main 직접 커밋
- ❌ 테스트 없이 구현 완료
- ❌ `pokervod.db` 스키마 무단 변경 (`qwen_hand_analysis` 소유)
