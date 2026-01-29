# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 12.0.0 | **Context**: Windows, PowerShell, Root: `C:\claude`

**GitHub**: `garimto81/claude`

---

## 프로젝트 개요

Claude Code 워크플로우 및 자동화 도구 메타 레포지토리. 커스텀 커맨드, 에이전트, 스킬을 포함한 개발 방법론 정의.

**주요 하위 프로젝트:**

| 프로젝트 | 경로 | 설명 |
|----------|------|------|
| **automation_hub** | `C:\claude\automation_hub` | WSOP 방송 자동화 공유 인프라 (PostgreSQL, Supabase) |
| **archive-analyzer** | `C:\claude\archive-analyzer` | 미디어 파일 분류 및 MAM 시스템 |
| **src/agents** | `C:\claude\src\agents` | Multi-Agent 병렬 워크플로우 시스템 (LangGraph) |

---

## 핵심 원칙

| 원칙 | 내용 |
|------|------|
| **언어** | 한글 출력, 기술 용어는 영어 유지 |
| **AI 티 제거** | `한글(영문)` 형식 금지 → 한글 또는 영어 중 하나만 |
| **경로** | 절대 경로만 (`C:\claude\...`) |
| **충돌** | 사용자에게 질문 (임의 판단 금지) |
| **API 키 금지** | API 키 방식 절대 사용 금지, Browser OAuth만 허용 |

---

## 빌드 및 테스트

### Python (루트)

```powershell
# 린트
ruff check src/ --fix

# 개별 테스트 (권장 - 120초 타임아웃 방지)
pytest tests/test_specific.py -v

# 전체 테스트 (background 필수)
pytest tests/ -v --cov=src
```

### E2E 테스트 (Playwright)

```powershell
npx playwright install              # 최초 설치
npx playwright test                 # 전체 실행
npx playwright test tests/e2e/auth.spec.ts  # 개별 실행
```

### 하위 프로젝트

| 프로젝트 | 테스트 명령 |
|----------|-------------|
| automation_hub | `pytest tests/ -v` (asyncio_mode=auto) |
| archive-analyzer | `pytest tests/ -v` |

> **주의**: 전체 테스트 (`pytest tests/ -v --cov`)는 120초 초과 시 크래시. 개별 파일 실행 권장.

---

## 코드 아키텍처

### 1. Multi-Agent 시스템 (`src/agents/`)

```
src/agents/
├── __init__.py          # WorkflowState, build_parallel_workflow 공개
├── config.py            # AGENT_MODEL_TIERS, AgentConfig, PHASE_AGENTS
├── parallel_workflow.py # LangGraph 기반 병렬 실행
└── prompt_learning/     # 프롬프트 최적화 (DSPy, TextGrad)
```

**모델 티어링:** supervisor/lead/coder → sonnet, validator → haiku

### 2. 커맨드 시스템 (`.claude/commands/`)

20개 커맨드 (`/work`, `/auto`, `/commit`, `/check` 등). 각 `.md` 파일이 슬래시 커맨드 정의.

### 3. 에이전트 시스템 (`.claude/agents/`)

19개 커스텀 에이전트. Tier 1(Core) 6개, Tier 2(Domain) 8개, Tier 3(Language) 2개, Tier 4(Tooling) 3개.

### 4. 스킬 시스템 (`.claude/skills/`)

24개 스킬. 각 디렉토리에 `SKILL.md` + 관련 파일. 자동/수동 트리거 지원.

---

## 규칙 참조

상세 규칙은 모듈화된 파일 참조: `.claude/rules/`

| 영역 | 파일 | 영향도 |
|------|------|--------|
| TDD | `.claude/rules/04-tdd.md` | CRITICAL |
| Git | `.claude/rules/03-git.md` | HIGH |
| Supabase | `.claude/rules/05-supabase.md` | HIGH |
| 경로 | `.claude/rules/02-paths.md` | HIGH |
| 빌드/테스트 | `.claude/rules/07-build-test.md` | HIGH |
| 문서화 | `.claude/rules/06-documentation.md` | MEDIUM |
| 언어 | `.claude/rules/01-language.md` | MEDIUM |

---

## Hook 강제 규칙

| 규칙 | Hook | 위반 시 |
|------|------|---------|
| **전체 프로세스 종료 금지** | `tool_validator.py` | **차단** |
| **API 키 사용 금지** | - | **절대 금지** |
| TDD 미준수 | `session_init.py` | 경고 |
| 100줄+ 수정 | `branch_guard.py` | 자동 커밋 |
| 상대 경로 사용 | `session_init.py` | 경고 |

⚠️ `taskkill /F /IM node.exe` 등 전체 종료 명령 **절대 금지**
⚠️ `OPENAI_API_KEY`, `GOOGLE_API_KEY` 등 API 키 환경변수 설정 **절대 금지**

---

## 작업 방법

```
사용자 요청 → /work "요청 내용" → 자동 완료
```

| 요청 유형 | 처리 |
|-----------|------|
| 기능/리팩토링 | `/work` → 이슈 → 브랜치 → TDD → PR |
| 버그 수정 | `/issue fix #N` |
| 문서 수정 | 직접 수정 |
| 질문 | 직접 응답 |

---

## 빠른 참조

### 주요 커맨드

| 커맨드 | 용도 | 빈도 |
|--------|------|------|
| `/auto` | 통합 자율 완성 (Ralph+Ultrawork+Ralplan 자동) | **90%** |
| `/commit` | Conventional Commit 생성 | 필요 시 |
| `/check` | 린트/테스트/보안 검사 | 필요 시 |
| `/debug` | 가설-검증 기반 디버깅 | 필요 시 |
| `/issue` | GitHub 이슈 관리 | 필요 시 |

**전체 20개**: `docs/COMMAND_REFERENCE.md`

### main 브랜치 허용 파일

`CLAUDE.md`, `README.md`, `.claude/`, `docs/`

---

## 참조 문서

| 문서 | 용도 |
|------|------|
| `.claude/rules/_index.md` | **규칙 마스터 색인** |
| `docs/COMMAND_REFERENCE.md` | 커맨드 상세 |
| `docs/AGENTS_REFERENCE.md` | 에이전트/스킬 상세 |
| `docs/BUILD_TEST.md` | 빌드/테스트 명령어 |
| `docs/RESPONSE_STYLE.md` | 응답 스타일 |
