# Plan: Playwright MCP → CLI 전환

## 배경

Playwright MCP 플러그인(`playwright@claude-plugins-official`)이 활성화되어 있으나, 대부분 워크플로우는 이미 Playwright CLI(`npx playwright test/screenshot`)를 사용 중. MCP는 불필요한 프로세스 오버헤드를 발생시키며, CLI로 완전 통합하면 의존성이 단순화됨.

## 문제 정의

- MCP 서버가 세션마다 프로세스를 생성하여 리소스 낭비
- MCP와 CLI 두 가지 경로가 혼재하여 유지보수 복잡도 증가
- MCP 도구(`mcp__playwright__*`)는 대화형 브라우저 제어에만 사용되며, 워크플로우에서는 활용하지 않음

## 구현 범위

### 포함

| 항목 | 설명 |
|------|------|
| MCP 제거 | `claude mcp remove playwright` 실행 |
| SKILL.md 업데이트 | `playwright-wrapper`, `webapp-testing`, `mockup-hybrid`, `final-check-automation`, `phase-validation` |
| export_utils.py | CLI 전용 로직 유지, MCP 참조 없음 |
| 문서 업데이트 | docs/ 하위 MCP 참조 파일 수정 |

### 제외

- Playwright 테스트 코드 자체 변경 없음
- `lib/mockup_hybrid/export_utils.py`의 Python SDK 사용 로직은 유지 (이미 CLI 독립적)
- 하위 프로젝트(`vimeo_ott/`, `automation_hub/`) 변경 없음

## 예상 영향 파일

- `.claude/skills/playwright-wrapper/SKILL.md`
- `.claude/skills/webapp-testing/SKILL.md`
- `.claude/skills/mockup-hybrid/SKILL.md`
- `.claude/skills/final-check-automation/SKILL.md`
- `.claude/skills/phase-validation/SKILL.md`
- `docs/01-plan/hooks-improvement.plan.md`
- `docs/02-design/hooks-improvement.design.md`
- `docs/04-report/hooks-improvement.report.md`

## 위험 요소

| 위험 | 영향도 | 완화 방안 |
|------|:------:|----------|
| 대화형 브라우저 제어 불가 | LOW | Playwright Python SDK의 `sync_playwright`로 대체 가능 |
| MCP 제거 후 세션 재시작 필요 | LOW | 작업 완료 후 안내 |
| npx 캐시 문제 | LOW | `npx playwright install` 재실행 |

## 복잡도 점수

- 파일 범위: 1점 (8+ 파일)
- 아키텍처: 1점 (MCP → CLI 패턴 전환)
- 의존성: 0점 (CLI 이미 설치됨)
- 모듈 영향: 1점 (skills, docs)
- 사용자 명시: 0점
- **총점: 3/5 → Planner 단독**
