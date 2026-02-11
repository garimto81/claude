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
| **vimeo_ott** | `C:\claude\vimeo_ott` | Vimeo OTT 콘텐츠 업로드/관리 (VHX API, S3) |
| **src/agents** | `C:\claude\src\agents` | Multi-Agent 병렬 워크플로우 시스템 (LangGraph) |
| **lib/** | `C:\claude\lib` | 통합 라이브러리 (Gmail, Slack, Google Docs, PDF, Mockup) |

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
| lib/google_docs | `pytest lib/google_docs/tests/ -v` |
| lib/pdf_utils | `pytest lib/pdf_utils/tests/ -v` |
| lib/slack | `pytest lib/slack/tests/ -v` |

### lib CLI 도구

```powershell
python -m lib.gmail login           # Gmail OAuth 인증
python -m lib.gmail inbox --limit 10
python -m lib.slack login           # Slack Bot OAuth
python -m lib.slack login --user    # Slack User OAuth (Lists API용)
python -m lib.google_docs           # Google Docs PRD 변환
python -m lib.pdf_utils             # PDF 청킹/추출
```

> **주의**: 전체 테스트 (`pytest tests/ -v --cov`)는 120초 초과 시 크래시. 개별 파일 실행 권장.

---

## 코드 아키텍처

### 1. Multi-Agent 시스템 (`src/agents/`)

```
src/agents/
├── __init__.py          # WorkflowState, build_parallel_workflow, Teams API 공개
├── config.py            # AGENT_MODEL_TIERS, TEAM_CONFIGS, COMPLEXITY_TEAM_MAP
├── parallel_workflow.py # LangGraph Fan-Out/Fan-In 병렬 실행
├── teams/               # 4팀 오케스트레이션 (v2.0)
│   ├── coordinator.py   # 복잡도 분석 → 팀 배치 → 의존성 실행 → 결과 통합
│   ├── base_team.py     # BaseTeam 추상 클래스 (State → Node → Graph → Run)
│   ├── dev_team.py      # 개발팀 (설계, 구현, 테스트, 문서화)
│   ├── quality_team.py  # 품질팀 (PDCA 사이클 검증)
│   ├── ops_team.py      # 운영팀 (CI/CD, 인프라, 모니터링)
│   └── research_team.py # 리서치팀 (코드 분석, 웹 조사)
└── prompt_learning/     # 프롬프트 최적화 (DSPy, TextGrad)
```

**모델 티어링:** supervisor/lead/coder → sonnet, validator/assistant → haiku

**팀 배치 규칙** (복잡도 점수 0-10): 4-5 → Dev, 6-7 → Dev+Quality, 8-9 → +Research, 10 → 4팀 전체

### 2. 통합 라이브러리 (`lib/`)

```
lib/
├── gmail/          # Gmail OAuth + 메일 CRUD (Browser OAuth)
├── slack/          # Slack OAuth + 메시징 + Lists API (Bot/User Token)
├── google_docs/    # Markdown→Google Docs 변환, Drive 정리, 프로젝트 레지스트리
├── pdf_utils/      # PDF 텍스트 추출 + 토큰/페이지 기반 청킹
└── mockup_hybrid/  # HTML 와이어프레임 + Google Stitch 하이브리드 목업
```

**인증 방식:** 모든 lib은 Browser OAuth 사용 (API 키 금지). 토큰 저장: `C:\claude\json\`

### 3. 커맨드 시스템 (`.claude/commands/`)

24개 커맨드 (`/work`, `/auto`, `/commit`, `/check` 등). 각 `.md` 파일이 슬래시 커맨드 정의.

### 4. 에이전트 시스템 (`.claude/agents/`)

19개 커스텀 에이전트. Tier 1(Core) 6개, Tier 2(Domain) 8개, Tier 3(Language) 2개, Tier 4(Tooling) 3개.

### 5. 스킬 시스템 (`.claude/skills/`)

47개 스킬 (+ 5개 deprecated). 각 디렉토리에 `SKILL.md` + 관련 파일. 자동/수동 트리거 지원.

---

## 규칙 참조

상세 규칙은 모듈화된 파일 참조: `.claude/rules/`

| 영역 | 파일 | 영향도 |
|------|------|--------|
| TDD | `.claude/rules/04-tdd.md` | CRITICAL |
| Global-Only | `.claude/rules/09-global-only.md` | CRITICAL |
| Git | `.claude/rules/03-git.md` | HIGH |
| Supabase | `.claude/rules/05-supabase.md` | HIGH |
| 경로 | `.claude/rules/02-paths.md` | HIGH |
| 빌드/테스트 | `.claude/rules/07-build-test.md` | HIGH |
| Task 분해 | `.claude/rules/10-task-decomposition.md` | HIGH |
| 스킬 라우팅 | `.claude/rules/08-skill-routing.md` | HIGH |
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

**전체 24개**: `docs/COMMAND_REFERENCE.md`

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
