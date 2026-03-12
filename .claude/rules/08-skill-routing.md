# 스킬 라우팅 규칙

모든 스킬은 Agent Teams 패턴으로 직접 실행합니다. 로컬 에이전트 (`C:\claude\.claude\agents\`)를 사용합니다.

## 스킬 매핑 테이블

| 스킬 | 실행 방식 | 서브커맨드 |
|------|----------|-----------|
| `/auto` | 직접 실행 (PDCA orchestrator, Agent Teams 단일 패턴) | Phase 1-5, --gdocs, --mockup, --daily 등 |
| `/check` | Agent Teams (QA 사이클) | --fix, --e2e, --perf, --security, --all, --react, --level |
| `/debug` | Agent Teams (architect 분석) | D0-D4 Phase |
| `/tdd` | Agent Teams (tdd-guide) | - |
| `/parallel` | Agent Teams (병렬 executor) | dev, test, review, research, check |
| `/research` | Agent Teams (researcher) | code, web, plan, review |
| `/commit`, `/issue`, `/pr`, `/verify`, `/mockup-hybrid` | 직접 실행 | 각 고유 서브커맨드 |
| `--jira` | `/auto` 옵션 (lib/jira/jira_client.py 실행) | epics, project, board, search, issue |
| `--figma` | `/auto` 옵션 (Figma MCP 플러그인 래퍼, OAuth 인증) | `<url>`, `connect <url>`, `rules`, `capture`, `auth` |
| `/overlay-fallback` | 직접 실행 (자동 트리거: T-1~T-5 조건) | — |
| `calendar` | 스킬 (lib/calendar CLI wrapper, gws 하이브리드) | today, week, list, create, delete |

## 외부 플러그인 연동

| 플러그인 | 역할 | 통합 상태 |
|---------|------|----------|
| `frontend-design` | 프론트엔드 미학 가이드라인 (Typography, Color, Motion, Spatial, Anti-Patterns) | `designer.md`에 가이드라인 직접 내장 완료. 플러그인은 세션 컨텍스트 보강용. |
| `figma` | Figma MCP 서버 + MCP 도구 13개 (implement, connect, rules, capture, auth) | 로컬 래퍼 스킬 `.claude/skills/figma/SKILL.md`로 /auto 통합 완료. OAuth 인증 자동. |

## Deprecated 스킬

| Deprecated | 리다이렉트 |
|------------|-----------|
| `/auto-workflow`, `/auto-executor` | `/auto` |
| `/work` | `/auto` (v19.0 통합) |
| `/work --auto` | `/auto` |
| `/work --loop` | `/auto` |
| `/tdd-workflow` | `/tdd` |
| `/cross-ai-verifier` | `/verify` |
| `/issue-resolution` | `/issue fix` |
| `/daily-sync` | `/daily` |
| `skill-creator` | 삭제 (v23.0 감사) |
| `pre-work-research` | `/research` |
| `agent-teamworks` | `/auto` Agent Teams |
| `final-check-automation` | `/check` |
| `code-quality-checker` | `/check` (흡수 통합) |
| `webapp-testing` | `playwright-wrapper` (흡수 통합) |

## 에이전트 티어 라우팅

| 복잡도 | 티어 | 에이전트 예시 |
|--------|------|--------------|
| 간단 | LOW (haiku) | `explore`, `executor-low`, `writer` |
| 보통 | MEDIUM (sonnet) | `executor`, `designer`, `qa-tester` |
| 복잡 | HIGH (opus) | `architect`, `planner`, `executor-high` |

## 인과관계 그래프

상세: `.claude/references/skill-causality-graph.md` (이 관계가 무너지면 5계층 Discovery 전체 작동 불가)

## 금지 사항

- SKILL.md에 "참조하세요"만 작성 금지 (실행 지시 필수)
- 서브프로젝트에 리소스 로컬 생성 금지 (Junction 사용)
- 인과관계 파괴 금지 (커맨드 삭제/변경 시 연쇄 확인 필수)
