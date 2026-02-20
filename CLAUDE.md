# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 14.1.0 | **Context**: Windows, Root: `C:\claude`

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
| **lib/** | `C:\claude\lib` | 통합 라이브러리 (Gmail, Slack, Google Docs, PDF, Mockup, AI Auth) |

---

## 핵심 원칙

| 원칙 | 내용 |
|------|------|
| **언어** | 한글 출력, 기술 용어는 영어 유지 |
| **AI 티 제거** | `한글(영문)` 형식 금지 → 한글 또는 영어 중 하나만 |
| **경로** | 절대 경로만 (`C:\claude\...`), 상대 경로 금지 |
| **충돌** | 사용자에게 질문 (임의 판단 금지) |
| **API 키 금지** | API 키 방식 절대 사용 금지, Browser OAuth만 허용 |
| **프로세스 종료 금지** | `taskkill /F /IM node.exe` 등 전체 종료 절대 금지 |
| **Git** | Conventional Commit, main 직접 수정은 허용 파일만 (`CLAUDE.md`, `README.md`, `.claude/`, `docs/`) |
| **TDD** | 테스트 먼저 작성 (상세: `.claude/rules/04-tdd.md`) |
| **이미지 분석** | "이미지 분석" 요청 시 Tesseract OCR 정밀 분석 자동 실행 (상세: `.claude/rules/10-image-analysis.md`) |
| **다이어그램** | 터미널 응답의 모든 다이어그램은 ASCII art 출력 필수. Mermaid/PNG 금지 (상세: `.claude/rules/11-ascii-diagram.md`) |
| **대형 문서** | 300줄+ 문서는 스켈레톤-퍼스트 + Map-Reduce 청킹 패턴 적용. 단일 Write 금지 (상세: `.claude/rules/12-large-document-protocol.md`) |

---

## 빌드 및 테스트

상세: `docs/BUILD_TEST.md`

**필수 명령:**
- 린트: `ruff check src/ --fix`
- 개별 테스트: `pytest tests/test_specific.py -v` (권장)
- E2E: `npx playwright test tests/e2e/auth.spec.ts`

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
├── pdf_utils/      # PDF/MD 텍스트 추출 + 4가지 청킹 전략 (Fixed-size, Hierarchical, Semantic, Late) + `/chunk --prd`
├── ocr/            # Tesseract OCR 정밀 텍스트 추출 (pytesseract + OpenCV)
├── mockup_hybrid/  # HTML 와이어프레임 + Google Stitch 하이브리드 목업
└── ai_auth/        # AI 서비스 인증 통합 (GPT, Gemini)
```

**인증 방식:** 모든 lib은 Browser OAuth 사용 (API 키 금지). 토큰 저장: `C:\claude\json\`

### 3. 커맨드 시스템 (`.claude/commands/`)

21개 커맨드 (`/auto`, `/commit`, `/check`, `/chunk` 등). 각 `.md` 파일이 슬래시 커맨드 정의.

### 4. 에이전트 시스템 (`.claude/agents/`)

42개 로컬 에이전트. OMC 플러그인 완전 제거됨 (2026-02-18) — 모든 에이전트가 `.claude/agents/`에서 직접 로드됨.

**주요 에이전트**: `architect`, `executor`, `executor-high`, `planner`, `critic`, `designer`, `code-reviewer`, `qa-tester`, `gap-detector`, `writer`, `researcher`

### 5. 스킬 시스템 (`.claude/skills/`)

36개 스킬 디렉토리. 각 디렉토리에 `SKILL.md` + 관련 파일. 자동/수동 트리거 지원.

### 6. Hook 시스템 (`.claude/hooks/`)

| Hook | 역할 |
|------|------|
| `tool_validator.py` | 프로세스 전체 종료 명령 차단 (PreToolUse) |
| `session_init.py` | 세션 시작 시 TDD 준수 경고 (SessionStart) |
| `branch_guard.py` | main/master 브랜치에서 비허용 파일 수정 차단 (PreToolUse) |
| `post_edit_check.js` | 편집 후 품질 검증 (PostToolUse) |

---

## Hook 강제 규칙

| 규칙 | Hook | 위반 시 |
|------|------|---------|
| **전체 프로세스 종료 금지** | `tool_validator.py` | **차단** |
| TDD 미준수 | `session_init.py` | 경고 |
| main/master 비허용 파일 수정 | `branch_guard.py` | **차단** |

---

## 작업 방법

```
사용자 요청 → /auto "요청 내용" → 자동 완료
```

| 요청 유형 | 처리 |
|-----------|------|
| 기능/리팩토링 | `/auto` → PDCA Phase 0-5 → 자동 완료 |
| 버그 수정 | `/issue fix #N` |
| 문서 수정 | 직접 수정 |
| 질문 | 직접 응답 |

---

## 빠른 참조

### 주요 커맨드

| 커맨드 | 용도 | 빈도 |
|--------|------|------|
| `/auto` | 통합 자율 완성 (PDCA 5-Phase, Agent Teams) | **90%** |
| `/commit` | Conventional Commit 생성 | 필요 시 |
| `/check` | 린트/테스트/보안 검사 | 필요 시 |
| `/debug` | 가설-검증 기반 디버깅 | 필요 시 |
| `/issue` | GitHub 이슈 관리 | 필요 시 |

**전체 21개**: `docs/COMMAND_REFERENCE.md`

---

## 참조 문서

| 문서 | 용도 |
|------|------|
| `docs/COMMAND_REFERENCE.md` | 커맨드 상세 |
| `docs/AGENTS_REFERENCE.md` | 에이전트/스킬 상세 |
| `docs/BUILD_TEST.md` | 빌드/테스트 명령어 |
| `docs/RESPONSE_STYLE.md` | 응답 스타일 |
| `.claude/references/` | Supabase, 문서화, 글로벌 전용, 작업 분해 참조 |
