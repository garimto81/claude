---
name: auto-workflow
description: >
  자율 판단 + 자율 발견 워크플로우 (Ralph Wiggum 철학 통합).
  "할 일 없음 → 종료"가 아닌 "할 일 없음 → 스스로 발견".
  2계층 우선순위, Context 모니터링, 로그 기록을 통해 무한 반복 실행.
version: 3.0.0

triggers:
  keywords:
    - "자동 완성"
    - "auto"
    - "자율 작업"
    - "무중단"
    - "ralph"
    - "loop"
  file_patterns: []
  context:
    - "대규모 작업 자동화"
    - "Context 관리 자동화"
    - "자율 발견"

capabilities:
  - log_all_actions        # 모든 작업 로깅
  - chunk_logs             # 로그 자동 청킹
  - monitor_context        # Context 사용량 모니터링
  - auto_checkpoint        # 자동 체크포인트
  - prd_management         # PRD 작성/검토
  - auto_commit            # 90% 도달 시 자동 커밋
  - autonomous_discovery   # 자율 발견 (Tier 2)
  - completion_promise     # Ralph 스타일 종료 조건

model_preference: opus

phase: [1, 2, 3, 4, 5]
auto_trigger: false
dependencies:
  - journey-sharing
  - session
  - create  # PRD 생성용
token_budget: 3000
---

# auto-workflow 스킬 (v2.0 - Ralph Wiggum 통합)

## 개요

`/auto` 및 `/work --loop` 커맨드의 핵심 기능을 제공하는 스킬입니다.
**Ralph Wiggum 철학**을 통합하여 "할 일 없음 → 종료" 대신 **"할 일 없음 → 자율 발견"**을 구현합니다.

### 핵심 원칙

> **"Iteration > Perfection"** - 완벽보다 반복
> **"Failures Are Data"** - 실패는 정보
> **"Persistence Wins"** - 끈기가 승리

### 핵심 기능

1. **2계층 우선순위**: Tier 1(명시적) → Tier 2(자율 발견)
2. **자율 발견**: 명시적 작업 없을 때 스스로 개선점 탐색
3. **종료 조건**: `--max`, `--promise`, Context 90%만 종료
4. **로그 기록**: JSON Lines 형식으로 모든 작업 실시간 기록
5. **체크포인트**: 작업 상태 자동 저장 및 복원

## 파일 구조

```
.claude/skills/auto-workflow/
├── SKILL.md                    # 이 파일
├── scripts/
│   ├── auto_cli.py             # CLI 진입점 (python auto_cli.py)
│   ├── auto_orchestrator.py    # 메인 루프 엔진
│   ├── auto_discovery.py       # 2계층 자율 발견 로직
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

## 오케스트레이터 실행 (권장)

외부 Python 스크립트로 Claude Code를 호출하여 자율 루프를 실행합니다.

```bash
# 기본 경로
cd D:\AI\claude01\.claude\skills\auto-workflow\scripts

# 자율 루프 시작
python auto_cli.py                    # 무한 루프
python auto_cli.py --max 10           # 최대 10회
python auto_cli.py --promise "DONE"   # "DONE" 출력 시 종료
python auto_cli.py --dry-run          # 판단만, 실행 안함

# 다음 작업 확인 (1회)
python auto_cli.py discover
python auto_cli.py discover --report  # 상세 리포트

# 세션 관리
python auto_cli.py status             # 현재 상태
python auto_cli.py resume             # 마지막 세션 재개
python auto_cli.py resume <session>   # 특정 세션 재개
python auto_cli.py pause              # 일시 정지
python auto_cli.py abort              # 세션 취소
```

### 오케스트레이터 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                   Auto Orchestrator                          │
├─────────────────────────────────────────────────────────────┤
│  1. auto_cli.py (CLI 진입점)                                │
│     - 명령줄 인터페이스                                     │
│     - run/resume/status/discover/pause/abort                │
│                                                              │
│  2. auto_orchestrator.py (루프 엔진)                        │
│     - Claude Code 호출 (subprocess)                         │
│     - 종료 조건 체크 (--max, --promise, Context)            │
│     - 체크포인트 자동 저장                                  │
│                                                              │
│  3. auto_discovery.py (자율 발견)                           │
│     - Tier 1: 명시적 작업 탐지                              │
│     - Tier 2: 자율 발견 (린트, 커버리지, 문서화 등)         │
│                                                              │
│  4. auto_state.py / auto_logger.py                          │
│     - 상태 관리 및 로깅                                     │
└─────────────────────────────────────────────────────────────┘
```

## 2계층 우선순위 체계

### Tier 1: 명시적 작업

| 우선순위 | 카테고리 | 트리거 |
|:--------:|----------|--------|
| 1 | 긴급 | 빌드 깨짐, 테스트 실패 |
| 2 | 진행중 | 방금 하던 작업 완료 |
| 3 | 대기중 | PR 리뷰, 이슈 해결 |
| 4 | PRD 필요 | 새 기능 → PRD 작성/검토 |
| 5 | 계획됨 | Todo, PRD 체크박스 |

### Tier 2: 자율 발견 (Tier 1 없을 때)

**⚠️ "할 일 없음"은 종료 조건이 아님** → 자율 발견 모드로 전환

| 우선순위 | 카테고리 | 발견 방법 | 작업 예시 |
|:--------:|----------|-----------|-----------|
| 6 | 코드 품질 | `ruff check`, `tsc --noEmit` | 린트 경고 수정 |
| 7 | 테스트 커버리지 | `pytest --cov` | 커버리지 80% 미달 파일 테스트 추가 |
| 8 | 문서화 | 문서 없는 public API 탐지 | JSDoc/docstring 추가 |
| 9 | 리팩토링 | 중복 코드, 긴 함수 탐지 | 함수 분리, 추상화 |
| 10 | 의존성 | `npm audit`, `pip-audit` | 취약점 패치 |
| 11 | 성능 | TODO 주석, 느린 패턴 탐지 | 최적화 |
| 12 | 접근성 | Playwright a11y 스캔 | ARIA 라벨 추가 |

### 자율 발견 실행 로직

```python
def discover_next_task():
    """Tier 2: 자율 발견 - 스스로 개선점 탐색"""

    # 6. 코드 품질
    lint_issues = run_linter()
    if lint_issues:
        return create_issue("lint", lint_issues)

    # 7. 테스트 커버리지
    coverage = get_coverage()
    uncovered = [f for f in coverage if f.percent < 80]
    if uncovered:
        return create_issue("coverage", uncovered[0])

    # 8. 문서화
    undocumented = find_undocumented_apis()
    if undocumented:
        return create_issue("docs", undocumented[0])

    # 9-12. 기타 발견...

    # 모든 검사 통과 → 대기 (종료 아님)
    return wait_and_recheck()
```

## 종료 조건 (명시적으로만)

| 조건 | 설명 |
|------|------|
| `--max N` | N회 반복 후 종료 |
| `--promise TEXT` | `<promise>TEXT</promise>` 출력 시 종료 |
| `pause` / `abort` | 사용자 명시적 중단 |
| Context 90% | 체크포인트 저장 후 종료 (resume 가능) |

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
