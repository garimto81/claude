# Rules Index

**Version**: 1.0.0
**Last Updated**: 2026-01-19

모듈화된 규칙 시스템의 마스터 색인입니다.

## 규칙 목록

| 파일 | 영역 | 영향도 | Hook 강제 |
|------|------|--------|-----------|
| [01-language.md](./01-language.md) | 언어/응답 | MEDIUM | ❌ |
| [02-paths.md](./02-paths.md) | 경로 | HIGH | ✅ 경고 |
| [03-git.md](./03-git.md) | Git/커밋 | HIGH | ✅ 자동 커밋 |
| [04-tdd.md](./04-tdd.md) | TDD | CRITICAL | ✅ 경고 |
| [05-supabase.md](./05-supabase.md) | Supabase | HIGH | ❌ |
| [06-documentation.md](./06-documentation.md) | 문서화 | MEDIUM | ❌ |
| [07-build-test.md](./07-build-test.md) | 빌드/테스트 | HIGH | ❌ |

## 영향도 정의

| 등급 | 설명 | 위반 시 조치 |
|------|------|--------------|
| **CRITICAL** | 시스템 안정성에 직접 영향 | Hook 차단 |
| **HIGH** | 코드 품질에 중대한 영향 | 경고 + 자동 조치 |
| **MEDIUM** | 일관성/가독성에 영향 | 경고만 |
| **LOW** | 권장사항 | 알림 없음 |

## Hook 연동

| Hook | 규칙 | 동작 |
|------|------|------|
| `tool_validator.py` | 03-git (프로세스 종료 금지) | **차단** |
| `session_init.py` | 04-tdd | 경고 |
| `branch_guard.py` | 03-git (100줄+ 수정) | 자동 커밋 |

## 사용법

CLAUDE.md에서 규칙을 참조:

```markdown
## 규칙 참조

자세한 내용은 `.claude/rules/04-tdd.md` 참조
```
