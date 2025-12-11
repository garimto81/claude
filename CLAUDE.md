# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 9.0.0 | **Context**: Windows, PowerShell, Root: `D:\AI\claude01`

**GitHub**: `garimto81/claude`

---

## 기본 규칙

| 규칙 | 내용 |
|------|------|
| **언어** | 한글 출력. 기술 용어(code, GitHub)는 영어 |
| **경로** | 절대 경로만. `D:\AI\claude01\...` |
| **충돌** | 지침 충돌 시 → **사용자에게 질문** (임의 판단 금지) |

---

## 프로젝트 구조

```
D:\AI\claude01\
├── .claude/
│   ├── commands/     # 슬래시 커맨드 (20개) - 자동 로드
│   ├── skills/       # 스킬 (13개) - 자동 로드
│   └── agents/       # 에이전트 (50개) - 자동 로드
├── docs/             # 워크플로우 문서
└── tasks/prds/       # PRD 문서
```

---

## 에이전트 (50개)

`.claude/agents/`에 정의된 전문 에이전트 (자동 로드):

### 호출 방법

```
"Use the [agent-name] agent to [task]"
예: "Use the debugger agent to analyze this error"
```

### 주요 에이전트

| Agent | 용도 |
|-------|------|
| `debugger` | 버그 분석, 근본 원인 분석 |
| `code-reviewer` | 코드 품질, 보안 리뷰 |
| `test-automator` | 테스트 자동화 |
| `frontend-developer` | React/Next.js 개발 |
| `backend-architect` | API 설계, 마이크로서비스 |
| `playwright-engineer` | E2E 테스트 |
| `security-auditor` | OWASP 보안 스캔 |
| `python-pro` | Python 3.12+ 전문 |

전체 목록: `docs/AGENTS_REFERENCE.md`

---

## 핵심 규칙 (Hook 강제)

| 규칙 | 위반 시 | 해결 |
|------|---------|------|
| main 브랜치 수정 금지 | **차단** | `git checkout -b feat/issue-N-desc` |
| 테스트 먼저 (TDD) | 경고 | Red → Green → Refactor |
| 상대 경로 금지 | 경고 | 절대 경로 사용 |

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

## 커맨드 (20개)

### 핵심 (5개)

| 커맨드 | 용도 |
|--------|------|
| `/work "내용"` | 전체 워크플로우 (`--auto` 완전 자동화) |
| `/issue <action>` | 이슈 관리 (`list`, `create`, `fix`, `failed`) |
| `/commit` | Conventional Commits |
| `/check` | 린트 + 테스트 |
| `/tdd` | TDD 워크플로우 |

### 병렬 실행

| 커맨드 | 용도 |
|--------|------|
| `/parallel dev` | 병렬 개발 |
| `/parallel test` | 병렬 테스트 |
| `/parallel review` | 병렬 코드 리뷰 |

### 기타

| 커맨드 | 용도 |
|--------|------|
| `/pre-work` | 사전 조사 |
| `/research` | 코드베이스 분석 |
| `/plan` | 구현 계획 |
| `/create <type>` | PRD/PR/문서 생성 |
| `/optimize` | 성능 분석 |
| `/final-check` | E2E 검증 |
| `/pr <action>` | PR 리뷰/머지 |
| `/changelog` | 변경로그 |

전체: `.claude/commands/`

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
| `docs/AGENTS_REFERENCE.md` | 에이전트 전체 목록 |
| `docs/COMMAND_SELECTOR.md` | 커맨드 선택 가이드 |
| `.claude/commands/` | 커맨드 상세 |
| `.claude/skills/` | 스킬 상세 |
| `.claude/agents/` | 에이전트 상세 |
