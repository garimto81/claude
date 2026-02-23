# Agent Teams 좀비 프로세스 감지 및 자동 정리 Work Plan

**문서 버전**: 1.0.0
**작성일**: 2026-02-23
**PRD**: `C:\claude\docs\00-prd\agent-teams-zombie-detection.prd.md`
**복잡도**: STANDARD (3/5)

---

## 배경 (Background)

### 요청 내용
Agent Teams 시스템에서 teammate 프로세스가 비정상 종료 시 Lead가 인지하지 못하는 좀비 프로세스 문제를 해결한다.

### 근본 원인 3가지

| # | 심각도 | 위치 | 원인 |
|---|--------|------|------|
| 1 | HIGH | `session_cleanup.py:L88-91` | `createdAt`이 Unix ms 정수(int)인데 `datetime.fromisoformat()` 호출 → `AttributeError` → except catch → 팀 삭제 불가 → 좀비 영구 잔류 |
| 2 | HIGH | `SubagentStop` 훅 | 기존 훅 2개(`checklist_updater.py`, `tmpclaude_cleanup.py`)가 teammate 종료를 Teams cleanup/Lead 알림에 활용하지 않음 |
| 3 | MEDIUM | 신규 훅 미등록 | `subagent_zombie_detector.py` 미존재 — 좀비 감지/기록/알림 메커니즘 전무 |

### 실제 데이터 확인

`~/.claude/teams/pdca-web-gui/config.json`에서 확인한 실제 구조:

```json
{
  "name": "pdca-web-gui",
  "createdAt": 1771836810399,
  "leadAgentId": "team-lead@pdca-web-gui",
  "leadSessionId": "78fe0576-...",
  "members": [
    {"agentId": "team-lead@pdca-web-gui", "name": "team-lead", "agentType": "team-lead", ...},
    {"agentId": "planner@pdca-web-gui", "name": "planner", "agentType": "planner", ...}
  ]
}
```

### 현재 코드 상태 (버그 재현 경로)

```
config.json: {"createdAt": 1771836810399}  (Unix ms int, 실측 데이터)
                     |
                     v
session_cleanup.py:L88:  created = config.get("createdAt", "")
session_cleanup.py:L89:  if created:  # truthy (int != 0)
session_cleanup.py:L90:      created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                              int.replace() → AttributeError!
                     |
                     v
session_cleanup.py:L96:  except Exception as e:
                              → errors 리스트에 추가, 삭제 skip → 좀비 팀 영구 잔류
```

---

## 구현 범위 (Scope)

### 포함

1. `session_cleanup.py` createdAt 파싱 버그 수정 (int/str 분기)
2. `subagent_zombie_detector.py` 신규 생성 (SubagentStop 훅)
3. `settings.json` SubagentStop 훅 배열에 신규 스크립트 등록
4. 테스트 파일 2개 신규 생성 (TDD)

### 제외

- heartbeat/polling 기반 실시간 생존 감지 (장기 로드맵)
- Ctrl+C 시 SessionEnd 훅 강제 실행 (OS 제약)
- Lead 세션 팝업/UI 알림 (CLI 환경 제약)
- 과거 좀비 기록 자동 정리

---

## 영향 파일 (Affected Files)

### 수정 예정

| 파일 | 변경 내용 | 변경 범위 |
|------|----------|----------|
| `C:\claude\.claude\hooks\session_cleanup.py` | L12: `timezone` import 추가, L88-93: createdAt int/str 분기 처리, `import sys` 추가 (stderr 출력용) | ~15줄 수정 |
| `C:\claude\.claude\settings.json` | SubagentStop hooks 배열에 `subagent_zombie_detector.py` 추가 | 4줄 추가 |

### 신규 생성

| 파일 | 내용 |
|------|------|
| `C:\claude\.claude\hooks\subagent_zombie_detector.py` | SubagentStop 훅 — 좀비 감지, JSONL 기록, stderr 경고, 팀 레지스트리 정리 |
| `C:\claude\tests\test_session_cleanup_createdat.py` | session_cleanup.py createdAt 파싱 단위 테스트 |
| `C:\claude\tests\test_subagent_zombie_detector.py` | subagent_zombie_detector.py 단위 테스트 |

### 참조 (수정 없음)

| 파일 | 참조 이유 |
|------|----------|
| `C:\claude\.claude\hooks\checklist_updater.py` | SubagentStop 기존 훅 — stdin JSON 파싱 패턴 참조 |
| `C:\claude\.claude\hooks\tmpclaude_cleanup.py` | SubagentStop 기존 훅 — hook 응답 패턴 참조 |
| `~/.claude/teams/{team-name}/config.json` | teammate 상태 읽기/쓰기 대상 |
| `~/.claude/zombie-alerts.jsonl` | 신규 훅이 append하는 알림 로그 |

---

## 위험 요소 (Risks)

### Risk 1: 훅 실패 시 Lead 세션 차단

**상황**: `subagent_zombie_detector.py`에서 예외 발생 시 SubagentStop 이벤트 체인이 중단되면 후속 훅(`checklist_updater.py`, `tmpclaude_cleanup.py`)도 실행 불가.

**완화**: 전체 main() 함수를 try-except 감싸기 + 항상 `{"continue": True}` 반환 + exit code 0 강제. 기존 훅 패턴(`checklist_updater.py:L137`, `tmpclaude_cleanup.py:L90`)과 동일 방어 코드 적용.

### Risk 2: config.json 파일 동시 접근 (race condition)

**상황**: 여러 teammate가 동시에 종료되면 `config.json` 읽기-수정-쓰기 사이에 충돌 발생 가능.

**완화**: 파일 잠금(fcntl/msvcrt) 대신 read-only 접근 우선. teammate 상태 마킹은 별도 파일(`zombie-alerts.jsonl`)에 append-only로 기록하여 충돌 최소화. config.json 쓰기 실패 시 skip하고 stderr 경고만 출력.

### Risk 3: Windows/Unix 경로 호환성

**상황**: `pathlib.Path.home()` 반환값이 Windows(`C:\Users\AidenKim`)와 Unix(`/home/user`)에서 다름. 하드코딩된 경로 구분자(`\` vs `/`) 사용 시 크로스 플랫폼 실패.

**완화**: 모든 경로를 `pathlib.Path`로 처리. 문자열 경로 구분자 하드코딩 금지. PRD C-03 준수 확인.

### Risk 4: zombie-alerts.jsonl 파일 크기 무한 증가

**상황**: 대량의 좀비 이벤트가 발생하면 JSONL 파일이 무한히 커질 수 있음.

**완화**: 현재 범위에서는 자동 정리 미구현 (Out of Scope). 파일 쓰기 실패 시에도 stderr 출력은 독립 try 블록으로 보장 (PRD NFR 준수).

### Edge Case 1: createdAt 필드가 없거나 0인 경우

`config.get("createdAt", "")`가 `0` (int falsy) 또는 빈 문자열을 반환하면 if 분기를 건너뛰어 TTL 검사 없이 즉시 삭제됨. 수정 코드에서 `0`과 `""`를 명시적으로 구분해야 함.

### Edge Case 2: createdAt이 초 단위 Unix timestamp인 경우

`1771836168`(초)과 `1771836168876`(밀리초)를 구분해야 함. 10자리 이하면 초 단위, 13자리면 밀리초 단위로 분기.

### Edge Case 3: SubagentStop stdin이 빈 경우

Claude Code 버전에 따라 stdin에 데이터가 전달되지 않을 수 있음. `sys.stdin.read()`가 빈 문자열이면 환경변수 fallback 확인 후 graceful exit.

---

## 태스크 목록 (Tasks)

### T1. [TDD-Red] session_cleanup.py createdAt 파싱 테스트 작성

**설명**: `cleanup_stale_agent_teams()` 함수의 createdAt 파싱 로직에 대한 실패 테스트 작성.

**수행 방법**:
- 파일: `C:\claude\tests\test_session_cleanup_createdat.py`
- 테스트 케이스:
  1. `createdAt`이 Unix ms 정수(`1771836168876`) → TTL 비교 정상 동작
  2. `createdAt`이 ISO 8601 문자열(`"2026-02-23T10:00:00Z"`) → 기존 로직 유지
  3. `createdAt`이 Unix 초 정수(`1771836168`) → 초 단위 감지 정상
  4. `createdAt`이 `0` → 즉시 삭제 대상 (TTL 만료 취급)
  5. `createdAt`이 없음 → 즉시 삭제 대상
- `cleanup_stale_agent_teams()` 함수를 직접 import하여 테스트
- `tmp_path` fixture로 임시 teams 디렉토리 생성, `monkeypatch`로 `Path.home()` mock

**Acceptance Criteria**: `pytest tests/test_session_cleanup_createdat.py -v` 실행 시 5개 테스트 중 케이스 1, 3이 FAIL (현재 버그 재현).

---

### T2. [TDD-Green] session_cleanup.py createdAt int/str 분기 수정

**설명**: `session_cleanup.py:L88-91`의 createdAt 파싱 로직을 int/str 양쪽 처리하도록 수정.

**수행 방법**:
- 파일: `C:\claude\.claude\hooks\session_cleanup.py`
- 변경 1) L8 부근: `import sys` 추가 (현재 미 import, stderr 출력용)
- 변경 2) L12: `from datetime import datetime` → `from datetime import datetime, timezone`
- 변경 3) L88-93 교체 (6줄 → 약 12줄):

현재 코드 (`session_cleanup.py:L88-93`):
```python
created = config.get("createdAt", "")
if created:
    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
    age_hours = (datetime.now(created_dt.tzinfo) - created_dt).total_seconds() / 3600
    if age_hours < ttl_hours:
        continue
```

수정 코드:
```python
created = config.get("createdAt")
if created is not None and created != "":
    created_dt = None
    if isinstance(created, (int, float)) and created > 0:
        # Unix ms (13자리) vs Unix sec (10자리) 분기
        ts = created / 1000 if created > 1e12 else float(created)
        created_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    elif isinstance(created, str) and created:
        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
    else:
        print(f"[session_cleanup] createdAt 타입 미지원: {type(created).__name__}={created}", file=sys.stderr)

    if created_dt is not None:
        age_hours = (datetime.now(timezone.utc) - created_dt).total_seconds() / 3600
        if age_hours < ttl_hours:
            continue
```

핵심 변경점:
- `isinstance(created, (int, float))` 분기로 Unix timestamp 처리
- `created > 1e12` 기준으로 ms/sec 자동 감지
- `timezone.utc` 통일 (기존 `created_dt.tzinfo` 의존 제거)
- 미지원 타입은 stderr 경고 후 skip (삭제 진행하지 않음)

**Acceptance Criteria**: `pytest tests/test_session_cleanup_createdat.py -v` 실행 시 5개 테스트 전체 PASS.

---

### T3. [TDD-Red] subagent_zombie_detector.py 테스트 작성

**설명**: 신규 좀비 감지 훅의 전체 동작에 대한 실패 테스트 작성.

**수행 방법**:
- 파일: `C:\claude\tests\test_subagent_zombie_detector.py`
- 테스트 케이스:
  1. stdin에 teammate 종료 JSON → `zombie-alerts.jsonl`에 이벤트 append 확인
  2. exit_code=0 (정상 종료) → type이 `"normal"` 기록
  3. exit_code=1 (비정상 종료) → type이 `"crash"` 기록, stderr에 `[ZOMBIE-ALERT]` 출력
  4. 팀 전원 종료 시 팀 레지스트리 디렉토리 삭제 확인
  5. 팀 일부만 종료 시 디렉토리 보존 확인
  6. stdin 빈 입력 → graceful exit (`{"continue": True}`)
  7. config.json 없음/읽기 실패 → stderr 경고 + graceful exit
- `tmp_path`, `monkeypatch`, `capsys` fixture 사용

**Acceptance Criteria**: `pytest tests/test_subagent_zombie_detector.py -v` 실행 시 7개 테스트 전체 FAIL (모듈 미존재 ImportError).

---

### T4. [TDD-Green] subagent_zombie_detector.py 구현

**설명**: `SubagentStop` 이벤트에서 좀비 teammate를 감지하고 알림/정리하는 훅 스크립트 신규 작성.

**수행 방법**:
- 파일: `C:\claude\.claude\hooks\subagent_zombie_detector.py` (신규 생성, 약 120줄)
- 표준 라이브러리만 사용: `json`, `sys`, `os`, `pathlib`, `datetime`, `shutil`, `time`
- 구현 흐름:

```
  stdin JSON 읽기
       |
       v
  teammate/team 식별
  (hook_data에서 추출 → 환경변수 fallback → teams dir 스캔)
       |
       v
  ~/.claude/teams/{team}/config.json 로드
       |
       v
  zombie-alerts.jsonl에 이벤트 append
       |
       v
  stderr에 [ZOMBIE-ALERT] 경고 출력
       |
       v
  팀 전원 종료 확인
       |
       +--[전원 종료]--> shutil.rmtree(teams_dir / team_name)
       |
       +--[일부 생존]--> skip
       |
       v
  stdout에 {"continue": true} 출력
```

- 핵심 함수:

| 함수 | 역할 | 입력 | 출력 |
|------|------|------|------|
| `main()` | 전체 흐름 조율, try-except wrap | - | stdout JSON |
| `parse_input()` | stdin JSON + 환경변수 파싱 | stdin str | `(team_name, teammate_name, exit_code)` |
| `write_alert(data)` | JSONL append | dict | bool (성공 여부) |
| `warn_stderr(team, mate, code)` | `[ZOMBIE-ALERT]` 경고 | str, str, int | None |
| `check_all_stopped(team_name)` | 전원 종료 판정 | str | bool |

- 팀 전원 종료 판정 로직:
  - config.json의 `members` 배열 순회
  - `agentType == "team-lead"` 제외
  - 나머지 member 중 활성 프로세스 존재 여부를 `~/.claude/teams/{team}/inboxes/` 하위 디렉토리로 확인
  - 실제 config.json 구조 참고: `members[].agentId`, `members[].name`, `members[].agentType`

- 핵심 규칙:
  - 전체 main()을 try-except 감싸기 (Lead 세션 차단 방지)
  - 파일 쓰기와 stderr 출력을 독립 try 블록으로 분리 (NFR: 쓰기 실패해도 stderr 출력 보장)
  - exit code 항상 0
  - `pathlib.Path` 사용 (하드코딩 경로 구분자 금지)
  - `zombie-alerts.jsonl` 경로: `Path.home() / ".claude" / "zombie-alerts.jsonl"`
  - JSONL 레코드 형식: `{"ts": <unix_ms>, "team": "<name>", "teammate": "<name>", "exit_code": <int>, "type": "crash"|"normal"}`

**Acceptance Criteria**: `pytest tests/test_subagent_zombie_detector.py -v` 실행 시 7개 테스트 전체 PASS. `ruff check` 린트 통과.

---

### T5. settings.json SubagentStop 훅 등록

**설명**: `settings.json`의 `SubagentStop` 훅 배열에 `subagent_zombie_detector.py`를 추가.

**수행 방법**:
- 파일: `C:\claude\.claude\settings.json`
- 대상: L8-22 SubagentStop 섹션
- 현재 상태 (hooks 2개):
  ```json
  "SubagentStop": [
    {"matcher": "", "hooks": [
      {"type": "command", "command": "python3 C:/claude/.claude/hooks/checklist_updater.py"},
      {"type": "command", "command": "python3 C:/claude/.claude/hooks/tmpclaude_cleanup.py"}
    ]}
  ]
  ```
- 수정 후 (hooks 3개 — 신규 훅을 기존 2개 **뒤**에 추가):
  ```json
  "SubagentStop": [
    {"matcher": "", "hooks": [
      {"type": "command", "command": "python3 C:/claude/.claude/hooks/checklist_updater.py"},
      {"type": "command", "command": "python3 C:/claude/.claude/hooks/tmpclaude_cleanup.py"},
      {"type": "command", "command": "python3 C:/claude/.claude/hooks/subagent_zombie_detector.py"}
    ]}
  ]
  ```
- 순서 근거: 기존 훅의 동작(체크리스트 업데이트, 임시파일 정리)을 먼저 완료한 뒤 좀비 감지 실행. zombie_detector가 팀 레지스트리를 삭제할 수 있으므로 기존 훅이 config.json을 읽을 수 있도록 후순위 배치.

**Acceptance Criteria**: `settings.json` JSON 파싱 오류 없음. `SubagentStop` hooks 배열에 `subagent_zombie_detector.py` 항목 존재. 기존 2개 훅 유지.

---

### T6. 통합 검증

**설명**: 전체 변경사항의 린트, 테스트, JSON 유효성 통합 검증.

**수행 방법**:
1. `ruff check C:\claude\.claude\hooks\session_cleanup.py C:\claude\.claude\hooks\subagent_zombie_detector.py --fix`
2. `pytest tests/test_session_cleanup_createdat.py tests/test_subagent_zombie_detector.py -v`
3. `python -c "import json; json.load(open('C:/claude/.claude/settings.json'))"` (JSON 유효성)
4. 수동 확인: `subagent_zombie_detector.py`가 외부 패키지 import 없음 (표준 라이브러리만)

**Acceptance Criteria**:
- ruff 린트 오류 0건
- 테스트 12개 전체 PASS (T1: 5개 + T3: 7개)
- settings.json JSON 파싱 성공
- 외부 패키지 import 0건

---

## 검증 계획 (요구사항별)

| 요구사항 | 검증 방법 | 테스트 태스크 |
|----------|----------|-------------|
| F-01 | `test_session_cleanup_createdat.py` 케이스 1-5 | T1, T2 |
| F-02 | `test_subagent_zombie_detector.py` 케이스 1-3 | T3, T4 |
| F-03 | `test_subagent_zombie_detector.py` 케이스 1 (JSONL append 확인) | T3, T4 |
| F-04 | `test_subagent_zombie_detector.py` 케이스 3 (stderr 출력 확인) | T3, T4 |
| F-05 | `test_subagent_zombie_detector.py` 케이스 4-5 (팀 디렉토리 삭제/보존) | T3, T4 |
| F-06 | T5 JSON 파싱 + 항목 존재 확인 | T5, T6 |

---

## 의존성 흐름

```
  T1 (테스트 작성)
       |
       v
  T2 (버그 수정) ----+
                      |
  T3 (테스트 작성)    |
       |              |
       v              |
  T4 (훅 구현) ------+---> T5 (settings.json) ---> T6 (통합 검증)
```

- T1 → T2: TDD Red → Green
- T3 → T4: TDD Red → Green
- T2, T4 → T5: 구현 완료 후 등록
- T5 → T6: 등록 후 통합 검증

---

## 커밋 전략 (Commit Strategy)

```
feat(hooks): Agent Teams 좀비 프로세스 감지 및 자동 정리

- fix: session_cleanup.py createdAt int/str 분기 처리 (L88-91 버그 수정)
- feat: subagent_zombie_detector.py 신규 — SubagentStop 좀비 감지/알림/정리
- chore: settings.json SubagentStop 훅 등록
- test: createdAt 파싱 5개 + 좀비 감지 7개 단위 테스트
```

Conventional Commit 형식: `feat(hooks): Agent Teams 좀비 프로세스 감지 및 자동 정리`
