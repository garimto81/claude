# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 10.3.1 | **Context**: Windows, PowerShell, Root: `D:\AI\claude01`

**GitHub**: `garimto81/claude`

---

## 기본 규칙

| 규칙 | 내용 |
|------|------|
| **언어** | 한글 출력. 기술 용어(code, GitHub)는 영어 |
| **경로** | 절대 경로만. `D:\AI\claude01\...` |
| **충돌** | 지침 충돌 시 → **사용자에게 질문** (임의 판단 금지) |

---

## 응답 스타일

작업 완료 시 아래 형식으로 마무리:

```
---
## 요약
> 사용자 질문/요청 내용 1줄 요약

## 답변 정리
| 항목 | 내용 |
|------|------|
| 수행 작업 | ... |
| 변경 파일 | ... |
| 결과 | ... |

## 검증 방법
- 파일: `경로/파일명` (Read로 확인)
- 명령어: `실행 명령어`
- URL: http://localhost:포트 (해당 시)
```

---

## 프로젝트 구조

```
D:\AI\claude01\
├── .claude/
│   ├── commands/     # 슬래시 커맨드 (14개)
│   ├── skills/       # 스킬 (13개)
│   ├── agents/       # 에이전트 (19개)
│   └── hooks/        # Git/Claude hooks
├── docs/             # 워크플로우 문서
├── tasks/prds/       # PRD 문서
└── VTC_Logger/       # 하위 프로젝트 (React + Vite)
```

---

## 빌드/테스트 명령어

### Python 프로젝트

```powershell
# 린트
ruff check src/ --fix

# 테스트 (개별 파일 권장 - 120초 타임아웃 방지)
pytest tests/test_specific.py -v

# 전체 테스트 (background 필수)
# run_in_background: true
pytest tests/ -v --cov=src
```

### VTC_Logger (React + Vite)

```powershell
cd D:\AI\claude01\VTC_Logger\vtc-app
npm install
npm run dev      # 개발 서버
npm run build    # 빌드
npm run lint     # ESLint
```

---

## 에이전트 (19개)

`.claude/agents/`에 정의. 상세: `docs/AGENTS_REFERENCE.md`

### 호출

```
"Use the [agent-name] agent to [task]"
```

### 주요 에이전트

| Tier | Agent | 용도 |
|------|-------|------|
| CORE | `code-reviewer` | 코드 품질, 보안 리뷰 |
| CORE | `architect` | 시스템 설계 |
| CORE | `debugger` | 버그 분석 |
| CORE | `test-engineer` | TDD/E2E 테스트 |
| DOMAIN | `frontend-dev` | React/Next.js |
| DOMAIN | `backend-dev` | FastAPI/Django |
| DOMAIN | `database-specialist` | DB, Supabase |
| TOOLING | `claude-expert` | Claude Code, MCP |

전체 19개: `docs/AGENTS_REFERENCE.md`

---

## 핵심 규칙 (Hook 강제)

| 규칙 | 위반 시 | 해결 |
|------|---------|------|
| main 브랜치 수정 금지 | **차단** | `git checkout -b feat/issue-N-desc` |
| 테스트 먼저 (TDD) | 경고 | Red → Green → Refactor |
| 상대 경로 금지 | 경고 | 절대 경로 사용 |

### main 브랜치 허용 파일

Hook(`branch_guard.py`)이 main에서도 수정 허용하는 파일:
- `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `.gitignore`
- `.claude/` 전체
- `docs/` 전체

---

## 작업 방법

```
사용자 요청 → /work "요청 내용" → 자동 완료
```

| 요청 유형 | 처리 |
|-----------|------|
| 기능/리팩토링 | `/work` → 이슈 → 브랜치 → TDD → PR |
| 버그 수정 | `/issue fix #N` |
| 문서 수정 | 직접 수정 (브랜치 불필요) |
| 질문 | 직접 응답 |

---

## 커맨드 (14개)

### 핵심 (자주 사용)

| 커맨드 | 용도 |
|--------|------|
| `/work "내용"` | 전체 워크플로우 (`--auto` 완전 자동화) |
| `/issue [action]` | 이슈 관리 (`list`, `create`, `fix`, `failed`) |
| `/commit` | Conventional Commits |
| `/check [options]` | 린트/테스트 (`--e2e`, `--perf`, `--security`) |
| `/tdd` | TDD 워크플로우 |

### 병렬 실행

| 커맨드 | 용도 |
|--------|------|
| `/parallel dev` | 병렬 개발 (`--branch` 브랜치 격리) |
| `/parallel test` | 병렬 테스트 |
| `/parallel review` | 병렬 코드 리뷰 |

### 생성/분석

| 커맨드 | 용도 |
|--------|------|
| `/research [sub]` | 리서치 (`code`, `web`, `plan`) |
| `/create [type]` | PRD/PR/문서 생성 (`prd`, `pr`, `docs`) |
| `/pr [action]` | PR 리뷰/머지 (`review`, `merge`, `create`) |

### 관리

| 커맨드 | 용도 |
|--------|------|
| `/todo` | 작업 관리 |
| `/session [sub]` | 세션 관리 (`compact`, `journey`, `changelog`) |
| `/deploy` | 버전/Docker 배포 |
| `/audit` | 설정 점검 (`suggest` 솔루션 추천) |

전체: `.claude/commands/`

---

## MCP 서버 (4개)

| MCP | 용도 |
|-----|------|
| `context7` | 기술 문서 조회 |
| `sequential-thinking` | 복잡한 추론 |
| `taskmanager` | 작업 관리 |
| `exa` | 고급 웹 검색 |

### MCP 관리

```powershell
claude mcp list                    # 목록
claude mcp add <name> -- npx -y <package>  # 추가
claude mcp remove <name>           # 제거
```

---

## 스킬 (13개)

자동 트리거 스킬:

| 스킬 | 트리거 조건 |
|------|-----------|
| `tdd-workflow` | "TDD", "테스트 먼저" |
| `debugging-workflow` | "debug", "3회 실패" |
| `code-quality-checker` | "린트", "품질 검사" |
| `final-check-automation` | "E2E", "최종 검증" |

수동 호출: `webapp-testing`, `pr-review-agent`, `skill-creator`

---

## 안전 규칙

```powershell
# 금지 (120초 초과 → 크래시)
pytest tests/ -v --cov

# 권장
pytest tests/test_a.py -v
# 또는 run_in_background: true
```

---

## 문제 해결

```
문제 → WHY(원인) → WHERE(영향 범위) → HOW(해결) → 수정
```

**즉시 수정 금지.** 원인 파악 → 유사 패턴 검색 → 구조적 해결.

---

## 참조

| 문서 | 용도 |
|------|------|
| `docs/COMMAND_REFERENCE.md` | **커맨드 사용법 총정리** |
| `docs/AGENTS_REFERENCE.md` | 에이전트 전체 목록 |
| `docs/PRD-0031-AGENT-CONSOLIDATION.md` | 에이전트 통합 PRD |
| `docs/PRD-0032-COMMAND-CONSOLIDATION.md` | 커맨드 통합 PRD |
| `.claude/commands/` | 커맨드 원본 파일 |
| `.claude/skills/` | 스킬 상세 |
| `.claude/agents/` | 에이전트 상세 |

---

## 변경 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| 10.3.1 | 2025-12-12 | 응답 스타일 가이드 추가 (요약/정리/검증) |
| 10.3.0 | 2025-12-12 | `/audit suggest` 서브커맨드 추가 (웹/GitHub 솔루션 추천) |
| 10.2.1 | 2025-12-12 | `catalog-engineer` 에이전트 추가 (18 → 19개) |
| 10.2.0 | 2025-12-12 | `/audit` 커맨드 추가, Daily Improvement System 문서 |
| 10.1.0 | 2025-12-11 | 빌드/테스트 명령어, Hook 허용 파일, MCP 관리 추가 |
| 10.0.0 | 2025-12-11 | PRD-0032: 커맨드 통합 (20개 → 12개) |
| 9.0.0 | 2025-12-11 | PRD-0031: 에이전트 통합 (50개 → 18개) |
