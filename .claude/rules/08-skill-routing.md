# 스킬 라우팅 규칙

모든 스킬은 Agent Teams 패턴으로 직접 실행합니다. 로컬 에이전트 (`C:\claude\.claude\agents\`)를 사용합니다.

## 스킬 매핑 테이블

| 스킬 | 실행 방식 | 서브커맨드 |
|------|----------|-----------|
| `/auto` | 직접 실행 (PDCA orchestrator, Agent Teams 단일 패턴) | Phase 1-5, --gdocs, --mockup, --daily 등 |
| `/check` | Agent Teams (QA 사이클) | --fix, --e2e, --perf, --security, --all |
| `/debug` | Agent Teams (architect 분석) | D0-D4 Phase |
| `/tdd` | Agent Teams (tdd-guide) | - |
| `/parallel` | Agent Teams (병렬 executor) | dev, test, review, research, check |
| `/research` | Agent Teams (researcher) | code, web, plan, review |
| `/commit`, `/issue`, `/pr`, `/verify`, `/mockup-hybrid` | 직접 실행 | 각 고유 서브커맨드 |

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
- 서브프로젝트에 리소스 로컬 생성 금지 (Junction 사용, 상세: `09-global-only.md`)
- 인과관계 파괴 금지 (커맨드 삭제/변경 시 연쇄 확인 필수)
