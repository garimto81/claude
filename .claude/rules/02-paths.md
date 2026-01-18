---
title: 경로 규칙
impact: HIGH
section: paths
---

# 경로 규칙

## 기본 원칙

| 규칙 | 내용 |
|------|------|
| **절대 경로만 사용** | `C:\claude\...` 형식 |
| **상대 경로 금지** | `./`, `../` 사용 금지 |
| **루트 디렉토리** | `C:\claude` |

## 잘못된 예

```powershell
# ❌ 상대 경로 사용
cd ./src
cat ../config.json
python ./scripts/main.py
```

## 올바른 예

```powershell
# ✅ 절대 경로 사용
cd C:\claude\src
cat C:\claude\config.json
python C:\claude\scripts\main.py
```

## 주요 경로

| 용도 | 경로 |
|------|------|
| 프로젝트 루트 | `C:\claude` |
| 소스 코드 | `C:\claude\src` |
| 스크립트 | `C:\claude\scripts` |
| 문서 | `C:\claude\docs` |
| Claude 설정 | `C:\claude\.claude` |
| 커맨드 | `C:\claude\.claude\commands` |
| 스킬 | `C:\claude\.claude\skills` |
| 에이전트 | `C:\claude\.claude\agents` |

## 강제 수단

- Hook: `session_init.py` (경고)
- 위반 시: 경고 메시지 출력
