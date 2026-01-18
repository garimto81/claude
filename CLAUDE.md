# CLAUDE.md

**Version**: 12.0.0 | **Context**: Windows, PowerShell, Root: `C:\claude`

**GitHub**: `garimto81/claude`

---

## 핵심 원칙

| 원칙 | 내용 |
|------|------|
| **언어** | 한글 출력, 기술 용어는 영어 유지 |
| **경로** | 절대 경로만 (`C:\claude\...`) |
| **충돌** | 사용자에게 질문 (임의 판단 금지) |

---

## 규칙 참조

상세 규칙은 모듈화된 파일 참조: `.claude/rules/`

| 영역 | 파일 | 영향도 |
|------|------|--------|
| TDD | `.claude/rules/04-tdd.md` | CRITICAL |
| Git | `.claude/rules/03-git.md` | HIGH |
| Supabase | `.claude/rules/05-supabase.md` | HIGH |
| 경로 | `.claude/rules/02-paths.md` | HIGH |
| 빌드/테스트 | `.claude/rules/07-build-test.md` | HIGH |
| 문서화 | `.claude/rules/06-documentation.md` | MEDIUM |
| 언어 | `.claude/rules/01-language.md` | MEDIUM |

---

## Hook 강제 규칙

| 규칙 | Hook | 위반 시 |
|------|------|---------|
| **전체 프로세스 종료 금지** | `tool_validator.py` | **차단** |
| TDD 미준수 | `session_init.py` | 경고 |
| 100줄+ 수정 | `branch_guard.py` | 자동 커밋 |
| 상대 경로 사용 | `session_init.py` | 경고 |

⚠️ `taskkill /F /IM node.exe` 등 전체 종료 명령 **절대 금지**

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
| `/work --loop` | 자율 반복 모드 (= `/auto`) |
| `/check` | 린트/테스트/보안 검사 |
| `/commit` | Conventional Commit 생성 |
| `/debug` | 가설-검증 기반 디버깅 |
| `/issue` | GitHub 이슈 관리 |

**전체 17개**: `docs/COMMAND_REFERENCE.md`

### main 브랜치 허용 파일

`CLAUDE.md`, `README.md`, `.claude/`, `docs/`

---

## 참조 문서

| 문서 | 용도 |
|------|------|
| `.claude/rules/_index.md` | **규칙 마스터 색인** |
| `docs/COMMAND_REFERENCE.md` | 커맨드 상세 |
| `docs/AGENTS_REFERENCE.md` | 에이전트/스킬 상세 |
| `docs/BUILD_TEST.md` | 빌드/테스트 명령어 |
| `docs/RESPONSE_STYLE.md` | 응답 스타일 |
