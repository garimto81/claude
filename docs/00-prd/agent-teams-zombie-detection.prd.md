# PRD: Agent Teams 좀비 프로세스 감지 및 자동 정리

**문서 버전**: 1.0.0
**작성일**: 2026-02-23
**상태**: Draft
**담당**: executor

---

## 1. 배경 및 목적

### 문제 상황

Agent Teams 시스템에서 teammate 프로세스(서브에이전트)가 비정상 종료되거나 완료 후 정리되지 않을 때, Lead(메인 세션)가 해당 사실을 인지하지 못한다. 사용자는 프로세스가 살아있는지 종료됐는지 구분할 수 없어 수십 분을 불필요하게 대기하는 문제가 발생한다.

### 근본 원인 분석

| 심각도 | 위치 | 원인 |
|--------|------|------|
| CRITICAL | runtime 전체 | 실시간 감지 메커니즘 없음 (heartbeat/polling 전무) |
| HIGH | `session_cleanup.py:L88-91` | `createdAt` 타입 불일치 버그 — config.json은 Unix ms 정수(`1771836168876`)이나 코드는 `datetime.fromisoformat()` 호출 → `AttributeError` → 예외 catch → 팀 삭제 안 됨 → 좀비 영구 잔류 |
| HIGH | `SubagentStop` 훅 | 훅이 등록되어 있으나 Teams cleanup/Lead 알림 기능 없음 (`checklist_updater.py`, `tmpclaude_cleanup.py` 모두 teammate 종료 무시) |
| MEDIUM | Ctrl+C / crash | SessionEnd 훅이 미실행되어 팀 레지스트리 정리 불가 |
| MEDIUM | cleanup 오류 처리 | silent exception handling으로 실패 무음 처리 |

### 목적

1. `session_cleanup.py` createdAt 파싱 버그를 수정하여 기존 TTL cleanup이 올바르게 작동하도록 한다.
2. `SubagentStop` 훅에서 좀비 teammate를 감지하고 Lead에게 즉시 알림을 전달하는 메커니즘을 구현한다.
3. 팀원 전체 종료 시 팀 레지스트리를 자동으로 정리하여 좀비 팀 상태를 제거한다.

---

## 2. 요구사항

### 기능 요구사항

| # | 요구사항 | 우선순위 |
|---|----------|----------|
| F-01 | `session_cleanup.py`의 `createdAt` 파싱 로직이 Unix ms 정수(int)와 ISO 8601 문자열(str) 양쪽을 모두 처리해야 한다 | P0 |
| F-02 | `SubagentStop` 이벤트 발생 시 신규 훅(`subagent_zombie_detector.py`)이 실행되어 종료된 teammate 정보를 수집해야 한다 | P0 |
| F-03 | 감지된 좀비 이벤트는 `~/.claude/zombie-alerts.jsonl` 파일에 JSONL 형식으로 기록되어야 한다 | P0 |
| F-04 | 좀비 감지 시 stderr에 경고 메시지를 출력하여 Lead(메인 세션)가 즉시 인지할 수 있어야 한다 | P1 |
| F-05 | 팀의 모든 teammate가 종료된 경우 해당 팀 레지스트리(`~/.claude/teams/{team-name}/`)를 자동으로 정리해야 한다 | P1 |
| F-06 | `settings.json`에 `subagent_zombie_detector.py`를 `SubagentStop` 훅으로 등록해야 한다 | P0 |

### 비기능 요구사항 (별도 섹션 참고)

- 성능, 안정성, 호환성 요구사항은 섹션 4 참조

---

## 3. 기능 범위

### In Scope

#### 3.1 버그 수정: `session_cleanup.py` createdAt 파싱

- `L88-91` 부근의 `createdAt` 처리 로직을 수정한다
- `isinstance(created, int)` 분기: Unix ms를 초로 변환 후 `datetime.fromtimestamp()` 사용
- `isinstance(created, str)` 분기: 기존 `datetime.fromisoformat()` 유지
- 예외 발생 시 silent catch 대신 로그를 남기고 해당 팀 skip(삭제 불가) 처리

#### 3.2 신규 훅: `subagent_zombie_detector.py`

훅 입력 (환경변수 또는 stdin JSON):
- `TEAMMATE_NAME` / `TEAM_NAME`: 종료된 teammate 식별자
- `EXIT_CODE`: 정상 종료(0) vs 비정상 종료

훅 동작:
1. `~/.claude/teams/{team-name}/config.json` 로드
2. 종료된 teammate를 `completed` 또는 `crashed` 상태로 마킹
3. `~/.claude/zombie-alerts.jsonl`에 이벤트 append
   ```json
   {"ts": 1771836168876, "team": "team-name", "teammate": "executor", "exit_code": 1, "type": "crash"}
   ```
4. stderr 경고 출력:
   ```
   [ZOMBIE-ALERT] teammate 'executor' in team 'team-name' has exited (code=1)
   ```
5. 팀 전원 종료 여부 확인 → 전원 종료 시 팀 레지스트리 디렉토리 삭제

#### 3.3 `settings.json` 훅 등록

```json
{
  "hooks": {
    "SubagentStop": [
      {"matcher": "", "hooks": [{"type": "command", "command": "python C:\\claude\\.claude\\hooks\\subagent_zombie_detector.py"}]}
    ]
  }
}
```

### Out of Scope

- heartbeat/polling 기반 실시간 생존 감지 (장기 로드맵)
- Ctrl+C 시 SessionEnd 훅 강제 실행 (OS 제약, 별도 이슈)
- Lead 세션에 팝업/UI 알림 (CLI 환경 제약)
- 과거 좀비 기록 자동 정리 (수동 또는 별도 스크립트로 처리)

---

## 4. 비기능 요구사항

| 카테고리 | 요구사항 | 측정 기준 |
|----------|----------|----------|
| **성능** | 훅 실행 시간 100ms 이내 완료 | 파일 I/O 최소화, 동기 단순 처리 |
| **안정성** | 훅 실패 시 main process(Lead 세션)에 영향 없음 | try-except 전 구간 wrap, exit code 0 강제 반환 |
| **안정성** | `zombie-alerts.jsonl` 쓰기 실패 시에도 stderr 출력은 진행 | 파일 쓰기와 stderr 출력을 독립 try 블록으로 분리 |
| **호환성** | Windows(win32) + Unix 경로 모두 지원 | `pathlib.Path` 사용, 하드코딩 경로 구분자 금지 |
| **유지보수** | 기존 훅(`checklist_updater.py`, `tmpclaude_cleanup.py`)과 독립 실행 | 신규 파일로 분리, 기존 파일 수정 최소화 |
| **보안** | config.json 읽기 실패(권한/파일 없음) 시 조용히 skip | 예외 catch 후 경고만 출력 |

---

## 5. 제약사항

| # | 제약사항 | 근거 |
|---|----------|------|
| C-01 | **프로세스 전체 종료 명령 금지** — `taskkill /F /IM`, `kill -9 *` 등 사용 불가 | `tool_validator.py` Hook이 차단 |
| C-02 | **API 키 방식 인증 금지** — 외부 서비스 연동 시 Browser OAuth만 허용 | 프로젝트 보안 정책 |
| C-03 | 훅 스크립트는 `C:\claude\.claude\hooks\` 경로에 위치해야 함 | `settings.json` hooks 경로 규약 |
| C-04 | `settings.json` 수정은 `.claude/` 하위이므로 main 브랜치 직접 수정 허용 | `branch_guard.py` 허용 경로 |
| C-05 | 신규 훅은 Python 3.x 표준 라이브러리만 사용 (외부 패키지 최소화) | 의존성 부하 방지 |
| C-06 | 좀비 알림 로그 파일(`zombie-alerts.jsonl`)은 `~/.claude/` 전역 경로에 저장 | 프로젝트별 레지스트리와 분리, 전역 감시 가능 |

---

## 6. 우선순위

### P0 (즉시 — 현재 버그 수정)

1. **F-01** `session_cleanup.py` createdAt 파싱 버그 수정
   - 영향: 기존 TTL cleanup이 완전히 작동하지 않는 CRITICAL 버그
   - 변경 범위: 단일 파일 5줄 이내 수정

2. **F-06** `settings.json` 훅 등록 (SubagentStop → `subagent_zombie_detector.py`)

3. **F-02 + F-03** `subagent_zombie_detector.py` 신규 작성
   - teammate 종료 감지 + JSONL 기록

### P1 (단기 — 사용자 경험 개선)

4. **F-04** stderr 경고 출력 (Lead 인지 개선)
5. **F-05** 팀 전원 종료 시 레지스트리 자동 정리

### 장기 로드맵 (Out of Scope)

- heartbeat 기반 실시간 생존 감지 (polling 주기 설계 필요)
- zombie-alerts.jsonl 자동 정리 및 대시보드

---

## 7. 구현 파일 목록

| 파일 | 작업 유형 | 내용 |
|------|----------|------|
| `C:\claude\.claude\hooks\session_cleanup.py` | **수정** | `createdAt` int/str 분기 처리 (L88-91), silent catch → 로그 출력 |
| `C:\claude\.claude\hooks\subagent_zombie_detector.py` | **신규 생성** | SubagentStop 훅 — teammate 종료 감지, JSONL 기록, stderr 경고, 팀 레지스트리 정리 |
| `C:\claude\.claude\settings.json` | **수정** | `SubagentStop` hooks 배열에 `subagent_zombie_detector.py` 등록 |

### 영향받는 기존 파일 (수정 없음, 참고용)

| 파일 | 역할 | 참고 이유 |
|------|------|----------|
| `C:\claude\.claude\hooks\checklist_updater.py` | SubagentStop 기존 훅 | Task 완료 체크리스트 업데이트 — 독립 실행 유지 |
| `C:\claude\.claude\hooks\tmpclaude_cleanup.py` | SubagentStop 기존 훅 | 임시 파일 정리 — 독립 실행 유지 |
| `~/.claude/teams/{team-name}/config.json` | 팀 레지스트리 | teammate 상태 읽기/쓰기 대상 |
| `~/.claude/zombie-alerts.jsonl` | 알림 로그 | 신규 생성, 신규 훅이 append |

---

## 참고

- Agent Teams 패턴 상세: `C:\claude\CLAUDE.md` — Agent Teams Protocol 섹션
- Hook 시스템 상세: `C:\claude\CLAUDE.md` — Hook 시스템 섹션
- 관련 이슈: session_cleanup.py L88-91 AttributeError (createdAt 파싱 실패)
