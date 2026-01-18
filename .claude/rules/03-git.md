---
title: Git 및 커밋 규칙
impact: HIGH
section: git
---

# Git 및 커밋 규칙

## 핵심 규칙

| 규칙 | 위반 시 | 조치 |
|------|---------|------|
| **전체 프로세스 종료 금지** | **차단** | 해당 프로젝트 node만 종료 |
| **100줄 이상 수정 시** | 자동 | `/commit` 실행 |
| **main 브랜치 직접 수정** | 경고 | 허용 파일만 가능 |

## 절대 금지 명령어

```powershell
# ❌ 전체 프로세스 종료 (다른 프로젝트에 영향)
taskkill /F /IM node.exe
Stop-Process -Name node

# ❌ Force push to main
git push --force origin main
```

## 올바른 종료 방법

```powershell
# ✅ 특정 포트의 프로세스만 종료
npx kill-port 3000

# ✅ 특정 PID만 종료
Stop-Process -Id <PID>
```

## main 브랜치 허용 파일

- `CLAUDE.md`
- `README.md`
- `.claude/` (전체)
- `docs/` (전체)

## Conventional Commit

```
<type>(<scope>): <description>

[body]

[footer]
```

### 타입

| 타입 | 설명 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서 변경 |
| `refactor` | 코드 개선 |
| `test` | 테스트 추가/수정 |
| `chore` | 빌드, 설정 변경 |

## 강제 수단

- Hook: `tool_validator.py` (프로세스 종료 차단)
- Hook: `branch_guard.py` (100줄+ 자동 커밋)
