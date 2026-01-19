# Submodule Policy

**Version**: 1.0.0
**Last Updated**: 2026-01-19

서브모듈에서 Claude Code 커맨드/스킬을 인식하기 위한 정책입니다.

---

## 개요

Claude Code는 **현재 작업 디렉토리(CWD)**를 기준으로 `.claude` 디렉토리를 찾습니다.

```
우선순위:
1. CWD에 .claude가 있으면 → CWD가 프로젝트 루트
2. CWD 상위 탐색 (최대 5단계) → 첫 .claude 발견 위치가 루트
3. Fallback → 메인 프로젝트 루트 (C:\claude)
```

---

## 서브모듈 유형

### 유형 1: 독립 프로젝트

서브모듈이 완전히 독립적인 프로젝트인 경우

```
submodule/
├── .claude/
│   ├── commands/       # 자체 커맨드
│   ├── skills/         # 자체 스킬
│   └── settings.json   # 자체 설정
├── CLAUDE.md           # 자체 설정 파일
├── src/
└── tests/
```

**설정 방법:**
1. 서브모듈 루트에 `.claude/` 디렉토리 생성
2. 필요한 커맨드/스킬 복사 또는 생성
3. `CLAUDE.md` 작성 (프로젝트별 규칙)

**사용 시:**
```bash
cd submodule/
claude  # 서브모듈의 .claude 인식
```

### 유형 2: 메인 프로젝트 참조

서브모듈이 메인 프로젝트의 설정을 공유하는 경우

```
submodule/
├── src/
├── tests/
└── (no .claude/)       # 메인 .claude 사용
```

**사용 시:**
```bash
cd C:\claude            # 메인 루트에서 작업
claude submodule/...    # 메인 .claude 사용
```

### 유형 3: 하이브리드

서브모듈이 일부 커맨드만 오버라이드하는 경우

```
submodule/
├── .claude/
│   └── commands/
│       └── work-custom.md   # 커스텀 워크플로우만
├── src/
└── tests/
```

**동작:**
- 서브모듈 CWD에서 실행 시 `work-custom` 사용
- 없는 커맨드는 메인에서 로드 (향후 구현)

---

## 현재 서브모듈 상태

| 서브모듈 | 유형 | .claude | 권장 조치 |
|----------|------|---------|----------|
| `ae_nexrender_module` | 독립 | ❌ 없음 | `.claude/` 생성 필요 |
| `automation_orchestration` | 하이브리드 | ⚠️ workflow만 | commands 추가 권장 |
| `automation_schema` | 메인 참조 | ❌ 없음 | 현재 상태 유지 가능 |
| `automation_dashboard` | 메인 참조 | ❌ 없음 | 현재 상태 유지 가능 |

---

## 서브모듈에 .claude 추가하기

### 최소 구성 (권장)

```bash
cd submodule/
mkdir -p .claude/commands
```

**CLAUDE.md 템플릿:**

```markdown
# CLAUDE.md

## 프로젝트 정보

| 항목 | 값 |
|------|-----|
| 이름 | [서브모듈 이름] |
| 루트 | [절대 경로] |
| 언어 | Python/TypeScript/etc |

## 빌드/테스트

\`\`\`bash
# 테스트
pytest tests/ -v

# 린트
ruff check src/
\`\`\`

## 규칙

- 메인 프로젝트 규칙 참조: `../CLAUDE.md`
```

### 커맨드 복사 (선택)

자주 사용하는 커맨드만 복사:

```bash
# 메인에서 서브모듈로 복사
cp C:\claude\.claude\commands\work.md submodule/.claude/commands/
cp C:\claude\.claude\commands\commit.md submodule/.claude/commands/
```

---

## 문제 해결

### "커맨드를 찾을 수 없음"

**원인:** CWD에 `.claude`가 없거나 상위에도 없음

**해결:**
1. 서브모듈에 `.claude/` 생성
2. 또는 메인 루트(`C:\claude`)로 이동 후 작업

### "스킬이 인식되지 않음"

**원인:** 스킬은 메인 프로젝트에만 있고 서브모듈에 없음

**해결:**
1. 필요한 스킬을 서브모듈에 복사
2. 또는 메인 루트에서 작업

### 디버깅

```bash
# 현재 감지되는 루트 확인
python -c "
from pathlib import Path
cwd = Path.cwd()
print(f'CWD: {cwd}')
print(f'.claude exists: {(cwd / \".claude\").exists()}')
"
```

---

## 관련 파일

| 파일 | 역할 |
|------|------|
| `auto_executor.py` | `detect_project_root()` 함수 |
| `CLAUDE.md` | 메인 프로젝트 설정 |
| `.claude/rules/02-paths.md` | 경로 규칙 |

---

## 서브 레포 수동 설정 방법

신규 서브 레포에서 메인 커맨드/스킬을 사용하려면:

### 1단계: Junction 생성

```powershell
# 서브 레포로 이동
cd C:\claude\<서브레포명>

# .claude 폴더 생성 (없으면)
mkdir .claude

# Junction 생성 (관리자 권한 불필요)
cmd /c "mklink /J .claude\commands C:\claude\.claude\commands"
cmd /c "mklink /J .claude\skills C:\claude\.claude\skills"
cmd /c "mklink /J .claude\agents C:\claude\.claude\agents"
```

### 2단계: settings.json 생성

`.claude/settings.json` 파일 생성:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {"type": "command", "command": "python C:/claude/.claude/hooks/branch_guard.py"}
        ]
      },
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          {"type": "command", "command": "python C:/claude/.claude/hooks/tool_validator.py"}
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {"type": "command", "command": "python C:/claude/.claude/hooks/session_init.py"}
        ]
      }
    ]
  },
  "statusLine": {
    "type": "command",
    "command": "python C:/claude/.claude/scripts/context-monitor.py",
    "padding": 0
  }
}
```

### 3단계: 검증

```powershell
# 서브 레포에서 Claude Code 실행
cd C:\claude\<서브레포명>
claude

# /work, /check 등 커맨드 사용 가능 확인
```

---

## 변경 이력

| 날짜 | 버전 | 내용 |
|------|------|------|
| 2026-01-19 | 1.1.0 | Junction 기반 수동 설정 방법 추가 |
| 2026-01-19 | 1.0.0 | 초기 작성, CWD 기반 루트 감지 도입 |
