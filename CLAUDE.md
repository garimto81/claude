# CLAUDE.md

Root: `C:\claude` | GitHub: `garimto81/claude`

---

## Safety Rules (HARD BLOCK)

| Rule | Detail |
|------|--------|
| **API key prohibited** | Browser OAuth only. API key 절대 금지 |
| **Process kill prohibited** | `taskkill /F /IM node.exe` 등 전체 종료 절대 금지 |
| **Absolute paths only** | `C:\claude\...` 형식만 허용, 상대 경로 금지 |
| **Conflict resolution** | 사용자에게 질문. 임의 판단 금지 |

## Language

한글 출력, 기술 용어는 영어 유지. `한글(영문)` 형식 금지.

## Git

Conventional Commit. main 직접 수정 허용 파일: `CLAUDE.md`, `README.md`, `.claude/`, `docs/`

## Build

- 린트: `ruff check src/ --fix`
- 테스트: `pytest tests/test_specific.py -v` (개별 파일 권장)
- E2E: `npx playwright test tests/e2e/auth.spec.ts`

> **주의**: 전체 테스트 (`pytest tests/ -v --cov`)는 120초 초과 시 크래시. 개별 파일 실행 권장.

## Context Loading

프로젝트 구조/아키텍처 파악이 필요하면 `.claude/references/codebase-architecture.md`를 읽어라.
빌드/테스트 명령 상세가 필요하면 `docs/BUILD_TEST.md`를 읽어라.
응답 스타일 기준은 `docs/RESPONSE_STYLE.md`를 읽어라.
