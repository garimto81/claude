# VSCode Multi-Launcher with Claude Auto-Execute

여러 VSCode IDE를 한 번에 실행하고, 각 터미널에서 Claude Code를 자동으로 실행하는 PowerShell 스크립트입니다.

## 기능

- JSON 설정 파일로 프로젝트 관리
- 7개 이상 IDE 동시 실행
- 그리드 레이아웃 자동 배치
- Claude 명령어 자동 실행
- 프로필 저장/로드
- 실시간 상태 모니터링

## 빠른 시작

### 1. 설정 파일 생성

```powershell
# 예제 파일을 복사하여 설정 파일 생성
Copy-Item vscode-projects.example.json vscode-projects.json
```

### 2. 프로젝트 경로 수정

`vscode-projects.json`을 편집하여 프로젝트 경로를 설정:

```json
{
  "version": "1.0",
  "projects": [
    {
      "name": "frontend",
      "path": "D:/your/project/path",
      "enabled": true
    }
  ],
  "settings": {
    "terminalLayout": "grid",
    "autoExecuteClaude": true,
    "claudeArgs": "--dangerously-skip-permissions"
  }
}
```

### 3. 실행

```powershell
# 기본 실행
./vscode-launcher-v2.ps1

# 특정 설정 파일 사용
./vscode-launcher-v2.ps1 -ConfigFile "my-projects.json"

# 미리보기 (실제 실행 없이)
./vscode-launcher-v2.ps1 -DryRun
```

## 사용법

### 기본 옵션

| 옵션 | 설명 |
|------|------|
| `-ConfigFile` | 설정 파일 경로 (기본: vscode-projects.json) |
| `-DryRun` | 실제 실행 없이 동작 확인 |
| `-NoAutoExecute` | Claude 자동 실행 비활성화 |
| `-SkipPositioning` | 창 위치 조정 비활성화 |

### 프로필

```powershell
# 현재 설정을 프로필로 저장
./vscode-launcher-v2.ps1 -SaveProfile "work"

# 저장된 프로필 로드
./vscode-launcher-v2.ps1 -LoadProfile "work"
```

## 설정 옵션

### projects

| 필드 | 타입 | 설명 |
|------|------|------|
| `name` | string | 프로젝트 표시 이름 |
| `path` | string | 프로젝트 폴더 절대 경로 |
| `enabled` | boolean | 활성화 여부 |

### settings

| 필드 | 기본값 | 설명 |
|------|--------|------|
| `terminalLayout` | "grid" | 창 배치 방식 (grid/horizontal/vertical/cascade) |
| `autoExecuteClaude` | true | Claude 자동 실행 여부 |
| `claudeArgs` | "--dangerously-skip-permissions" | Claude 명령어 인자 |
| `startupDelayMs` | 500 | IDE 실행 간격 (ms) |
| `maxRetries` | 3 | 실패 시 재시도 횟수 |

## 창 배치

### Grid (기본)

```
┌──────────┬──────────┬──────────┐
│ Project1 │ Project2 │ Project3 │
├──────────┼──────────┼──────────┤
│ Project4 │ Project5 │ Project6 │
├──────────┴──────────┴──────────┤
│         Project7+              │
└────────────────────────────────┘
```

프로젝트 수에 따라 자동으로 그리드 크기를 계산합니다.

## 상태 표시

| 상태 | 아이콘 | 설명 |
|------|--------|------|
| Starting | [Y] | VSCode 시작 중 |
| Running | [G] | Claude 실행 중 |
| Error | [R] | 오류 발생 |

## 요구 사항

- Windows 10/11
- PowerShell 5.1+
- VSCode (code CLI 사용 가능)
- Claude Code CLI

## 문제 해결

### VSCode가 열리지 않는 경우

```powershell
# code 명령어 확인
code --version
```

### 창 위치가 조정되지 않는 경우

- VSCode가 완전히 로드될 때까지 약간의 지연이 필요합니다
- `startupDelayMs` 값을 늘려보세요

### Claude가 실행되지 않는 경우

- Claude Code CLI가 설치되어 있는지 확인
- 수동으로 터미널을 열어 `claude --version` 실행

## 파일 구조

```
vscode_setting/
├── vscode-launcher-v2.ps1          # 메인 스크립트 (v2)
├── vscode-launcher.ps1             # 기본 스크립트 (v1)
├── vscode-projects.json            # 설정 파일
├── vscode-projects.example.json    # 예제 설정
├── vscode-projects.schema.json     # JSON 스키마
├── .vscode-launcher-profiles/      # 저장된 프로필
├── vscode-launcher.log             # 실행 로그
├── docs/
│   ├── checklists/PRD-0001.md     # 체크리스트
│   ├── mockups/PRD-0001/          # HTML 목업
│   └── images/PRD-0001/           # 스크린샷
└── tasks/prds/PRD-0001-*.md       # PRD 문서
```

## 라이선스

MIT License
