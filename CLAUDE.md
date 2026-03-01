# CLAUDE.md

**Version**: 15.0.0 | Root: `C:\claude` | GitHub: `garimto81/claude`

---

## Safety Rules (HARD BLOCK)

| Rule | Detail |
|------|--------|
| **API key prohibited** | Browser OAuth only. API key 절대 금지 |
| **Process kill prohibited** | `taskkill /F /IM node.exe` 등 전체 종료 절대 금지 |
| **Absolute paths only** | `C:\claude\...` 형식만 허용, 상대 경로 금지 |
| **Conflict resolution** | 사용자에게 질문. 임의 판단 금지 |

## Hook Enforcement (HARD BLOCK)

| Rule | Hook | On Violation |
|------|------|-------------|
| 전체 프로세스 종료 금지 | `tool_validator.py` | **차단** |
| main/master 비허용 파일 수정 | `branch_guard.py` | **차단** |
| TDD 미준수 | `session_init.py` | 경고 |

## Language

한글 출력, 기술 용어는 영어 유지. `한글(영문)` 형식 금지.

## Git

Conventional Commit. main 직접 수정 허용 파일: `CLAUDE.md`, `README.md`, `.claude/`, `docs/`

## Build

- 린트: `ruff check src/ --fix`
- 테스트: `pytest tests/test_specific.py -v` (개별 파일 권장)
- E2E: `npx playwright test tests/e2e/auth.spec.ts`

> **주의**: 전체 테스트 (`pytest tests/ -v --cov`)는 120초 초과 시 크래시. 개별 파일 실행 권장.

## Architecture Summary

5개 서브프로젝트 (`automation_hub`, `archive-analyzer`, `vimeo_ott`, `src/agents`, `lib/`), 22개 커맨드 (`.claude/commands/`), 42개 에이전트 (`.claude/agents/`), 38개 스킬 (`.claude/skills/`), 4개 Hook (`.claude/hooks/`).

상세 파일 트리 + 모델 티어링 + 팀 배치: `.claude/references/codebase-architecture.md`

## Workflow

```
사용자 요청 → /auto "요청 내용" → 자동 완료
```

| 요청 유형 | 처리 |
|-----------|------|
| 기능/리팩토링 | `/auto` → PDCA Phase 0-5 → 자동 완료 |
| 버그 수정 | `/issue fix #N` |
| 문서 수정 | 직접 수정 |
| 질문 | 직접 응답 |

## Reference Documents

| Document | Purpose |
|----------|---------|
| `docs/COMMAND_REFERENCE.md` | 22개 커맨드 상세 |
| `docs/AGENTS_REFERENCE.md` | 42개 에이전트 + 40개 스킬 상세 |
| `docs/BUILD_TEST.md` | 빌드/테스트 명령어 상세 |
| `docs/RESPONSE_STYLE.md` | 응답 스타일 |
| `.claude/references/` | 아키텍처, 프로젝트 인벤토리, Supabase, 문서화, 작업 분해 |
