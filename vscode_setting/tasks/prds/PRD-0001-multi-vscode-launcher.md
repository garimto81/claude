# PRD-0001: Multi-VSCode IDE Launcher with Claude Auto-Execute

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Priority** | P1 |
| **Created** | 2026-01-06 |
| **Author** | Claude Code |

---

## 1. 개요

### 1.1 배경
개인 개발자가 여러 프로젝트를 동시에 작업할 때, 각 프로젝트마다 VSCode를 열고 Claude Code를 실행하는 반복 작업이 필요합니다. 대규모 모노레포나 마이크로서비스 환경에서는 7개 이상의 IDE를 관리해야 하며, 이 과정이 비효율적입니다.

### 1.2 목표
- 여러 VSCode IDE를 한 번에 실행
- 각 IDE의 작업 폴더를 JSON 설정 파일로 관리
- 모든 IDE에서 `claude --dangerously-skip-permissions` 명령어를 자동 실행
- 터미널 창 자동 배치 및 상태 모니터링

### 1.3 대상 사용자
- **개인 개발자**: 혼자 여러 프로젝트를 동시에 작업하는 개발자

---

## 2. 핵심 기능

### 2.1 JSON 설정 파일 기반 프로젝트 관리

```json
// vscode-projects.json
{
  "version": "1.0",
  "projects": [
    {
      "name": "frontend",
      "path": "D:/projects/frontend",
      "enabled": true
    },
    {
      "name": "backend",
      "path": "D:/projects/backend",
      "enabled": true
    },
    {
      "name": "shared-lib",
      "path": "D:/projects/shared-lib",
      "enabled": false
    }
  ],
  "settings": {
    "terminalLayout": "grid",
    "autoExecuteClaude": true,
    "claudeArgs": "--dangerously-skip-permissions"
  }
}
```

### 2.2 VSCode 다중 인스턴스 실행

| 기능 | 설명 |
|------|------|
| 동시 실행 | 7개 이상 IDE 병렬 실행 지원 |
| 폴더 지정 | 각 IDE마다 다른 로컬 폴더 할당 |
| 새 창 모드 | `code --new-window` 옵션으로 독립 창 생성 |

### 2.3 Claude 명령어 자동 실행

```powershell
# 각 VSCode 터미널에서 실행
claude --dangerously-skip-permissions
```

- 터미널 자동 열기 (통합 터미널)
- 명령어 자동 입력 및 실행
- 노드 형태 프롬프트 모드 활성화

### 2.4 터미널 배치 자동화

```
┌──────────────┬──────────────┬──────────────┐
│  Project 1   │  Project 2   │  Project 3   │
│  (Frontend)  │  (Backend)   │  (API)       │
├──────────────┼──────────────┼──────────────┤
│  Project 4   │  Project 5   │  Project 6   │
│  (Worker)    │  (Admin)     │  (Shared)    │
├──────────────┴──────────────┴──────────────┤
│              Project 7+ (Overflow)          │
└─────────────────────────────────────────────┘
```

- 그리드 레이아웃 자동 계산
- 화면 해상도 기반 창 크기 최적화
- 다중 모니터 지원

### 2.5 상태 모니터링

| 상태 | 표시 | 설명 |
|------|------|------|
| Starting | 🟡 | VSCode 시작 중 |
| Running | 🟢 | Claude 실행 중 |
| Error | 🔴 | 실행 오류 발생 |
| Idle | ⚪ | 대기 중 |

---

## 3. 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| 스크립트 언어 | PowerShell 7+ |
| 설정 포맷 | JSON |
| IDE | VSCode (code CLI) |
| 창 관리 | Windows API (Add-Type) |

---

## 4. 시각화

### 4.1 전체 흐름

![전체 흐름](../images/PRD-0001/flow.png)

[HTML 원본 보기](../mockups/PRD-0001/flow.html)

### 4.2 설정 화면

![설정 화면](../images/PRD-0001/config-screen.png)

[HTML 원본 보기](../mockups/PRD-0001/config-screen.html)

### 4.3 실행 화면

![실행 화면](../images/PRD-0001/execution-screen.png)

[HTML 원본 보기](../mockups/PRD-0001/execution-screen.html)

---

## 5. 사용 시나리오

### 5.1 기본 실행

```powershell
# 설정 파일 기반 실행
./vscode-launcher.ps1

# 특정 설정 파일 지정
./vscode-launcher.ps1 -ConfigFile "my-projects.json"
```

### 5.2 프로필 사용

```powershell
# 프로필 저장
./vscode-launcher.ps1 -SaveProfile "work"

# 프로필 로드
./vscode-launcher.ps1 -LoadProfile "work"
```

---

## 6. 성공 지표

| 지표 | 목표 |
|------|------|
| 실행 시간 | 7개 IDE 10초 이내 전체 시작 |
| 성공률 | Claude 자동 실행 99% 성공 |
| 메모리 | IDE당 500MB 이하 추가 사용 |

---

## 7. 제약 사항

- Windows 전용 (PowerShell 기반)
- VSCode 및 Claude Code CLI 사전 설치 필요
- `--dangerously-skip-permissions` 옵션 사용으로 인한 보안 주의

---

## 8. 향후 확장

- [ ] macOS/Linux 지원 (Bash 버전)
- [ ] VSCode 확장 프로그램 연동
- [ ] 원격 SSH 프로젝트 지원
- [ ] 프로젝트별 Claude 설정 분리
