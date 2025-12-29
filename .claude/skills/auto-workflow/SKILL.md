---
name: auto-workflow
description: >
  자율 판단 자동 완성 워크플로우. PRD 작성/검토, Context 모니터링, 로그 기록,
  자동 저장 기능을 통해 대규모 작업을 체계적으로 수행합니다.
version: 1.1.0

triggers:
  keywords:
    - "자동 완성"
    - "auto"
    - "자율 작업"
    - "무중단"
  file_patterns: []
  context:
    - "대규모 작업 자동화"
    - "Context 관리 자동화"

capabilities:
  - log_all_actions        # 모든 작업 로깅
  - chunk_logs             # 로그 자동 청킹
  - monitor_context        # Context 사용량 모니터링
  - auto_checkpoint        # 자동 체크포인트
  - prd_management         # PRD 작성/검토
  - auto_commit            # 90% 도달 시 자동 커밋

model_preference: opus

phase: [1, 2, 3, 4, 5]
auto_trigger: false
dependencies:
  - journey-sharing
  - session
  - create  # PRD 생성용
token_budget: 3000
---

# auto-workflow 스킬

## 개요

`/auto` 커맨드의 핵심 기능을 제공하는 스킬입니다.

### 핵심 기능

1. **PRD 관리**: 새 기능 시 PRD 탐색/작성/검토/승인
2. **로그 기록**: JSON Lines 형식으로 모든 작업 실시간 기록
3. **로그 청킹**: 50KB 초과 시 자동 분할
4. **Context 모니터링**: 90% 도달 시 /commit → 세션 종료
5. **체크포인트**: 작업 상태 자동 저장 및 복원

## 파일 구조

```
.claude/skills/auto-workflow/
├── SKILL.md                    # 이 파일
├── scripts/
│   ├── auto_logger.py          # 로그 관리
│   └── auto_state.py           # 상태/체크포인트 관리
└── references/
    └── log-schema.md           # 로그 스키마 문서

.claude/auto-logs/
├── active/                     # 진행 중인 세션
│   └── session_YYYYMMDD_HHMMSS/
│       ├── state.json          # 세션 상태
│       ├── log_001.json        # 로그 청크
│       └── checkpoint.json     # 체크포인트
└── archive/                    # 완료된 세션
```

## Context 임계값

| 사용량 | 상태 | 액션 |
|--------|------|------|
| 0-40% | safe | 정상 작업 |
| 40-60% | monitor | 모니터링 강화 |
| 60-80% | prepare | 체크포인트 준비 |
| 80-90% | warning | 체크포인트 저장 |
| **90%+** | **critical** | **진행 중 작업 완료 → /commit → 세션 종료** |

**90% 도달 시 동작:**
1. 추가 작업 없이 현재 작업만 완료
2. `/commit`으로 변경사항 커밋
3. 체크포인트 저장
4. 세션 종료 (사용자가 `/auto resume`으로 재개)

## 사용 패턴

### 새 세션 시작

```python
from auto_state import AutoState

state = AutoState(original_request="API 인증 기능 구현")
state.update_phase("analysis")
state.update_progress(total=5, completed=0, pending=5)
```

### 로그 기록

```python
from auto_logger import AutoLogger

logger = AutoLogger(session_id=state.session_id)
logger.log_action("file_read", "src/auth.py", "success")
logger.log_decision("JWT 선택", "보안 강화", ["Session", "Basic"])
```

### 체크포인트 생성

```python
state.create_checkpoint(
    task_id=3,
    task_content="핸들러 구현",
    context_hint="src/auth/handler.py의 generate_token",
    todo_state=[...]
)
```

### 세션 복원

```python
from auto_state import restore_session

state, summary = restore_session("session_20251230_103000")
print(summary)  # 재개용 컨텍스트 출력
```

### PRD 관리

```python
# PRD 상태 업데이트
state.update_prd_status("searching")  # 탐색 중
state.update_prd_status("writing")    # 작성 중
state.update_prd_status("reviewing", path="tasks/prds/0046-prd-auth.md")

# PRD 검토 결과 저장
state.set_prd_review_result({
    "requirements": 5,
    "tech_spec": "clear",
    "test_scenarios": 3,
    "checklist_items": 8
})

# PRD 승인
state.approve_prd()

# PRD 상태 조회
prd_status = state.get_prd_status()
```

## 로그 스키마

```json
{
  "timestamp": "2025-12-30T10:30:00.000Z",
  "sequence": 1,
  "event_type": "action|decision|error|milestone|checkpoint",
  "phase": "init|analysis|implementation|testing|complete",
  "data": {
    "action": "file_read|file_write|command|tool_use",
    "target": "path/to/file",
    "result": "success|fail",
    "details": {}
  },
  "context_usage": 45,
  "todo_state": [...]
}
```

## PRD 단계 흐름

```
새 기능 작업 감지
    │
    ├─ 1. PRD 탐색
    │      tasks/prds/ 검색
    │
    ├─ 2. PRD 없으면 → /create prd 실행
    │      PRD 자동 작성
    │
    ├─ 3. PRD 검토
    │      - 요구사항 완전성
    │      - 기술 실현 가능성
    │      - 테스트 시나리오
    │
    └─ 4. 사용자 승인 대기
           승인 후 구현 진행
```

## Context 90% 도달 흐름

```
Context 90% 도달
    │
    ├─ 1. 현재 작업 완료 (추가 작업 없음)
    │
    ├─ 2. /commit 실행
    │      변경사항 커밋
    │
    ├─ 3. 체크포인트 저장
    │      - Todo 상태
    │      - 핵심 결정
    │      - 변경 파일
    │      - PRD 상태
    │      - 재개 힌트
    │
    └─ 4. 세션 종료
           "💡 재개하려면: /auto resume"
```

## 관련 커맨드

- `/auto` - 메인 커맨드
- `/auto resume [session_id]` - 세션 재개
- `/auto status` - 현재 상태 확인
- `/auto pause` - 일시 정지
- `/auto abort` - 세션 취소
