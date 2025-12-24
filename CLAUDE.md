# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 11.6.0 | **Context**: Windows, PowerShell, Root: `D:\AI\claude01`

**GitHub**: `garimto81/claude`

---

## 기본 규칙

| 규칙 | 내용 |
|------|------|
| **언어** | 한글 출력. 기술 용어(code, GitHub)는 영어 |
| **경로** | 절대 경로만. `D:\AI\claude01\...` |
| **충돌** | 사용자에게 질문 (임의 판단 금지) |
| **응답** | 상세: `docs/RESPONSE_STYLE.md` |

---

## 핵심 규칙 (Hook 강제)

| 규칙 | 위반 시 | 해결 |
|------|---------|------|
| 테스트 먼저 (TDD) | 경고 | Red → Green → Refactor |
| 상대 경로 금지 | 경고 | 절대 경로 사용 |
| **전체 프로세스 종료 금지** | **차단** | 해당 프로젝트 node만 종료 |
| **100줄 이상 수정 시 자동 커밋** | 자동 | `/commit` 실행 |

⚠️ `taskkill /F /IM node.exe` 등 전체 종료 명령 **절대 금지**. 다른 프로젝트 영향.

main 허용: `CLAUDE.md`, `README.md`, `.claude/`, `docs/`

---

## 프로젝트 구조

```
D:\AI\claude01\
├── CLAUDE.md                    # 핵심 워크플로우 (이 파일)
├── README.md                    # 프로젝트 소개
├── docs/                        # 문서
│   ├── COMMAND_REFERENCE.md     # 커맨드 상세 (14개)
│   ├── AGENTS_REFERENCE.md      # 에이전트/스킬 참조
│   └── WORKFLOWS/               # 워크플로우 레시피
├── .claude/                     # Claude Code 설정
│   ├── commands/                # 커스텀 슬래시 커맨드
│   ├── skills/                  # 커스텀 스킬
│   └── agents/                  # 커스텀 에이전트
├── scripts/                     # 자동화 스크립트
└── automation_sub/              # 서브 프로젝트 (WSOP Broadcast)
    └── tasks/prds/              # PRD 문서
```

### 서브 프로젝트

| 경로 | 설명 |
|------|------|
| `automation_sub/` | WSOP Broadcast Graphics System 개발 |
| `automation_sub/tasks/prds/` | PRD 문서 저장소 |

---

## 빌드/테스트 명령

### Python

```powershell
ruff check src/ --fix                    # 린트
pytest tests/test_specific.py -v         # 개별 테스트 (권장)
# pytest tests/ -v --cov=src             # 전체 (background 필수)
```

### E2E (Playwright 필수)

```powershell
npx playwright test                       # 전체 E2E
npx playwright test tests/e2e/auth.spec.ts  # 개별 테스트
```

**안전 규칙**: `pytest tests/ -v --cov` → 120초 초과 → 크래시. 개별 파일 실행 권장.

---

## 스크립트 (scripts/)

| 스크립트 | 용도 |
|----------|------|
| `validate_phase_universal.py` | Phase 검증 (범용) |
| `plugin_manager.py` | 플러그인 관리 |
| `auto-version.ps1` | 버전 자동 업데이트 |
| `setup-github-labels.ps1` | GitHub 라벨 설정 |
| `migrate_prds_to_gdocs.py` | PRD → Google Docs 마이그레이션 |

---

## MCP 설정

### 설치된 MCP

| MCP | 패키지 | 용도 |
|-----|--------|------|
| `code-reviewer` | `@vibesnipe/code-review-mcp` | AI 코드 리뷰 |

### MCP 관리 명령

```bash
claude mcp add <name> -- npx -y <package>   # 설치
claude mcp list                              # 목록
claude mcp remove <name>                     # 제거
```

### 내장 기능으로 대체됨

| 기존 MCP | 대체 내장 기능 |
|----------|---------------|
| `context7` | `WebSearch` + `WebFetch` |
| `sequential-thinking` | `Extended Thinking` |
| `taskmanager` | `TodoWrite` / `TodoRead` |
| `exa` | `WebSearch` |

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

| 커맨드 | 용도 |
|--------|------|
| `/work` | 전체 워크플로우 (이슈→TDD→PR) |
| `/orchestrate` | 메인-서브 에이전트 오케스트레이션 |
| `/check` | 린트/테스트/보안 검사 |
| `/commit` | Conventional Commit 생성 |
| `/debug` | 가설-검증 기반 디버깅 (D0-D4) |
| `/issue` | GitHub 이슈 관리 (list/create/fix) |

**전체 14개**: `docs/COMMAND_REFERENCE.md`

### 에이전트 & 스킬

**에이전트 23개** (커스텀 19 + 내장 4): `docs/AGENTS_REFERENCE.md`

**스킬 16개**: `docs/AGENTS_REFERENCE.md`

---

## 문제 해결

```
문제 → WHY(원인) → WHERE(영향) → HOW(해결) → 수정
```

**즉시 수정 금지.** 원인 파악 → 유사 패턴 검색 → 구조적 해결.

---

## 문서 작업 규칙

### 시각화 (PRD, 아키텍처 필수)

```
HTML 목업 (540px, 16px+) → 요소 캡처 → 문서 첨부
```

| 규칙 | 값 |
|------|-----|
| 가로 너비 | 540px |
| 최소 폰트 | 16px |
| 캡처 대상 | `#capture-target` (전체 화면 X) |

```powershell
# 요소만 캡처 (--selector 필수)
npx playwright screenshot docs/mockups/feature.html docs/images/feature.png --selector="#capture-target"
```

**상세**: `docs/HTML_MOCKUP_GUIDE.md`

### Checklist (Slack List 연동)

| 우선순위 | 경로 |
|:--------:|------|
| 1 | `docs/checklists/PRD-NNNN.md` |
| 2 | `tasks/prds/NNNN-prd-*.md` |

**상세**: `.github/CHECKLIST_STANDARD.md`

---

## 참조

| 문서 | 용도 |
|------|------|
| `docs/RESPONSE_STYLE.md` | 응답 스타일 상세 |
| `docs/BUILD_TEST.md` | 빌드/테스트 명령어 |
| `docs/COMMAND_REFERENCE.md` | 커맨드 상세 |
| `docs/AGENTS_REFERENCE.md` | 에이전트 상세 |
| `docs/HTML_MOCKUP_GUIDE.md` | HTML 목업 설계 가이드 |
| `docs/CHANGELOG-CLAUDE.md` | 변경 이력 |
| `.github/CHECKLIST_STANDARD.md` | Checklist 작성 표준 |
