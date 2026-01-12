# PRD-0003: AE 모드 전환 시스템

**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-01-07
**Priority**: P0
**Author**: Claude Code

---

## 1. 개요

### 1.1 문제 정의

현재 Nexrender Worker가 실행되면 `ae_render_only_node.txt` 파일이 생성되어 After Effects가 **렌더링 전용 모드**로 동작합니다. 이로 인해:

- AE에서 프로젝트 편집 불가
- 스크립트 실행 불가
- 렌더 큐 설정 변경 불가
- 매번 수동으로 라이선스 파일을 삭제해야 함

### 1.2 해결 목표

**원클릭으로 Nexrender 모드 ↔ 편집 모드 전환**

| 모드 | 상태 | 동작 |
|------|------|------|
| **Render 모드** | Nexrender Worker 실행 중 | AE 렌더링 전용, 자동화 가능 |
| **Edit 모드** | Worker 중지, 라이선스 파일 제거 | AE 전체 기능 사용 가능 |

### 1.3 핵심 가치

```
┌─────────────────────────────────────────────────────────────┐
│                    현재 (수동)                               │
├─────────────────────────────────────────────────────────────┤
│  Worker 중지 → 라이선스 파일 삭제 → AE 재시작 → 작업        │
│  작업 완료 → AE 종료 → Worker 시작                          │
│                                                             │
│  → 매번 5-10분 소요, 실수 가능                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    목표 (자동)                               │
├─────────────────────────────────────────────────────────────┤
│  [Edit Mode] 버튼 클릭 → 자동 전환 → AE 열기                │
│  [Render Mode] 버튼 클릭 → 자동 전환 → Worker 시작          │
│                                                             │
│  → 10초 내 전환, 실수 없음                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 기능 요구사항

### 2.1 모드 전환

| ID | 기능 | 우선순위 | 설명 |
|----|------|----------|------|
| F-001 | Edit 모드 전환 | P0 | Worker 중지 + 라이선스 파일 제거 |
| F-002 | Render 모드 전환 | P0 | 라이선스 파일 생성 + Worker 시작 |
| F-003 | 현재 모드 감지 | P0 | Worker 상태 + 라이선스 파일 존재 여부 확인 |
| F-004 | AE 프로세스 감지 | P1 | AE 실행 중일 때 경고 또는 종료 요청 |

### 2.2 자동화

| ID | 기능 | 우선순위 | 설명 |
|----|------|----------|------|
| F-005 | AE 자동 열기 | P1 | Edit 모드 전환 후 프로젝트 자동 열기 |
| F-006 | Worker 자동 관리 | P0 | 모드 전환 시 Worker 프로세스 자동 시작/중지 |
| F-007 | 상태 표시 | P1 | 현재 모드를 시각적으로 표시 |

### 2.3 안전장치

| ID | 기능 | 우선순위 | 설명 |
|----|------|----------|------|
| F-008 | 렌더링 중 보호 | P0 | 렌더링 진행 중에는 Edit 모드 전환 차단 |
| F-009 | AE 실행 중 보호 | P1 | AE 실행 중 Render 모드 전환 시 경고 |

---

## 3. 시스템 설계

### 3.1 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     AE Mode Switcher                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   CLI       │    │  PowerShell │    │   Tray App  │     │
│  │   명령어    │    │   스크립트  │    │   (선택)    │     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘     │
│         │                  │                  │             │
│         └────────────┬─────┴──────────────────┘             │
│                      ▼                                      │
│         ┌─────────────────────────────┐                     │
│         │      Core Manager           │                     │
│         │  (ae_mode_manager.py)       │                     │
│         └──────────────┬──────────────┘                     │
│                        │                                    │
│         ┌──────────────┼──────────────┐                     │
│         ▼              ▼              ▼                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │  License   │ │   Worker   │ │    AE      │              │
│  │  Manager   │ │  Manager   │ │  Launcher  │              │
│  └────────────┘ └────────────┘ └────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 라이선스 파일 위치

```
C:\Users\{USER}\Documents\ae_render_only_node.txt
C:\Users\{USER}\Documents\Adobe\ae_render_only_node.txt
```

### 3.3 모드 전환 흐름

#### Edit 모드 전환

```
[Edit Mode 요청]
      │
      ▼
┌─────────────────────┐
│ 1. 렌더링 중 확인   │──────▶ 렌더링 중 → 차단
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ 2. Worker 중지      │
│    (nexrender 프로세스)
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ 3. 라이선스 파일    │
│    삭제/이름변경    │
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ 4. AE 종료 대기     │
│    (실행 중이면)    │
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ 5. 완료 알림        │
│    (선택: AE 열기)  │
└─────────────────────┘
```

#### Render 모드 전환

```
[Render Mode 요청]
      │
      ▼
┌─────────────────────┐
│ 1. AE 실행 중 확인  │──────▶ 실행 중 → 경고
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ 2. 라이선스 파일    │
│    생성             │
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ 3. Worker 시작      │
│    (nexrender-worker)
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ 4. Server 확인      │
│    (nexrender-server)
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│ 5. 완료 알림        │
└─────────────────────┘
```

---

## 4. 구현 계획

### Phase 1: 핵심 기능 (MVP)

- [ ] Core Manager (Python) 구현
- [ ] License Manager: 파일 생성/삭제
- [ ] Worker Manager: 프로세스 시작/중지
- [ ] CLI 명령어: `ae-mode edit`, `ae-mode render`

### Phase 2: 편의 기능

- [ ] 현재 상태 확인 명령어: `ae-mode status`
- [ ] AE 프로젝트 자동 열기
- [ ] 렌더링 중 보호 로직

### Phase 3: UI (선택)

- [ ] 시스템 트레이 앱
- [ ] 상태 아이콘 표시
- [ ] 알림 팝업

---

## 5. 사용법 (예상)

### CLI 명령어

```powershell
# 현재 상태 확인
ae-mode status
# Output:
#   Mode: Render
#   Worker: Running (PID: 12345)
#   License: Active

# Edit 모드로 전환
ae-mode edit
# Output:
#   ✓ Worker stopped
#   ✓ License files removed
#   → Mode changed to: Edit
#   → You can now open AE for editing

# Edit 모드 + AE 열기
ae-mode edit --open "C:\templates\MyProject.aep"
# Output:
#   ✓ Mode changed to: Edit
#   ✓ Opening AE project...

# Render 모드로 전환
ae-mode render
# Output:
#   ✓ License files created
#   ✓ Worker started (PID: 12346)
#   → Mode changed to: Render
#   → Ready for automation
```

### PowerShell Alias 설정

```powershell
# $PROFILE에 추가
function ae-edit { python C:\claude\automation_ae\scripts\ae_mode_manager.py edit $args }
function ae-render { python C:\claude\automation_ae\scripts\ae_mode_manager.py render $args }
function ae-status { python C:\claude\automation_ae\scripts\ae_mode_manager.py status }
```

---

## 6. 파일 구조

```
C:\claude\automation_ae\scripts\
├── ae_mode_manager.py      # Core Manager (메인)
├── ae_mode_config.json     # 설정 파일
└── ae_mode.ps1             # PowerShell 래퍼 (선택)
```

---

## 7. 설정 파일

```json
{
  "license_paths": [
    "C:\\Users\\{USER}\\Documents\\ae_render_only_node.txt",
    "C:\\Users\\{USER}\\Documents\\Adobe\\ae_render_only_node.txt"
  ],
  "ae_executable": "C:\\Program Files\\Adobe\\Adobe After Effects 2025\\Support Files\\AfterFX.exe",
  "nexrender": {
    "server_host": "localhost",
    "server_port": 3000,
    "worker_binary": "C:\\Program Files\\Adobe\\Adobe After Effects 2025\\Support Files\\aerender.exe"
  },
  "default_project": null
}
```

---

## 8. 성공 지표

| 지표 | 목표 |
|------|------|
| 모드 전환 시간 | 10초 이내 |
| 수동 작업 | 0회 (완전 자동화) |
| 오류 발생률 | 0% |
| 사용자 만족도 | 수동 대비 90% 시간 절약 |

---

## 부록

### A. 관련 프로세스

| 프로세스 | 설명 |
|----------|------|
| `AfterFX.exe` | AE GUI 모드 |
| `aerender.exe` | AE 렌더링 엔진 |
| `node.exe` (nexrender-worker) | Nexrender Worker |
| `node.exe` (nexrender-server) | Nexrender Server |

### B. 참고 자료

- [Nexrender License Documentation](https://github.com/inlife/nexrender#render-only-license)
- [AE Render Only Mode](https://helpx.adobe.com/after-effects/using/automated-rendering-network-rendering.html)

