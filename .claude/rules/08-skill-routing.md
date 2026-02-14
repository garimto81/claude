# OMC 스킬 라우팅 규칙

로컬 스킬(`.claude/skills/`)은 OMC 플러그인으로 **자동 위임**됩니다.
SKILL.md의 `omc_delegate` frontmatter가 있으면 해당 OMC 스킬로 자동 라우팅.

## 스킬 매핑 테이블

| 로컬 스킬 | OMC 위임 | 서브커맨드 |
|-----------|----------|-----------|
| `/auto` | `autopilot` | --gdocs, --mockup, --debate, --research |
| `/check` | `ultraqa` | --fix, --e2e, --perf, --security, --all |
| `/debug` | `analyze` | D0-D4 Phase |
| `/tdd` | `tdd` | - |
| `/parallel` | `ultrawork` | dev, test, review, research, check |
| `/research` | `research` | code, web, plan, review |
| `/commit`, `/issue`, `/pr`, `/verify`, `/mockup-hybrid` | - (직접 실행) | 각 고유 서브커맨드 |

## 인과관계 그래프

**CRITICAL**: `.claude/references/skill-causality-graph.md` 참조. 이 관계가 무너지면 5계층 Discovery 전체 작동 불가.

## Deprecated 스킬

| Deprecated | 리다이렉트 |
|------------|-----------|
| `/auto-workflow`, `/auto-executor` | `/auto` |
| `/tdd-workflow` | `/tdd` |
| `/cross-ai-verifier` | `/verify` |
| `/issue-resolution` | `/issue fix` |

## 에이전트 티어 라우팅

| 복잡도 | 티어 | 에이전트 예시 |
|--------|------|--------------|
| 간단 | LOW (haiku) | `explore`, `executor-low`, `writer` |
| 보통 | MEDIUM (sonnet) | `executor`, `designer`, `qa-tester` |
| 복잡 | HIGH (opus) | `architect`, `planner`, `executor-high` |

## 금지 사항

- SKILL.md에 "참조하세요"만 작성 금지 (실행 지시 필수)
- omc_delegate 없이 OMC 기능 기대 금지
- 서브프로젝트에 리소스 로컬 생성 금지 (Junction 사용, 상세: `09-global-only.md`)
- 인과관계 파괴 금지 (커맨드 삭제/변경 시 연쇄 확인 필수)
