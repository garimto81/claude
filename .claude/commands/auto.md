---
name: auto
description: 자율 판단 자동 완성 - Claude가 다음 작업을 스스로 판단하고 실행
---

# /auto - 자율 판단 자동 완성

Claude가 **다음에 해야 할 작업을 스스로 판단**하고 **자동으로 실행**합니다.

## 사용법

```bash
/auto                    # 자율 판단 루프 시작
/auto resume [id]        # 세션 재개
/auto status             # 현재 상태 확인
/auto pause              # 일시 정지 (체크포인트 저장)
/auto abort              # 세션 취소
/auto --max 5            # 최대 5개 작업 후 중단
/auto --dry-run          # 판단만 보여주고 실행 안함
```

## 핵심 기능

### 1. 로그 기록

모든 작업을 `.claude/auto-logs/` 폴더에 JSON Lines 형식으로 기록합니다.

```
.claude/auto-logs/active/session_YYYYMMDD_HHMMSS/
├── state.json           # 세션 상태
├── log_001.json         # 로그 청크 1 (50KB)
├── log_002.json         # 로그 청크 2
└── checkpoint.json      # 재개용 체크포인트
```

### 2. 로그 청킹

- 로그 파일이 **50KB**를 초과하면 자동으로 새 청크 생성
- 청크 파일: `log_001.json`, `log_002.json`, ...

### 3. Context 모니터링 (90% 임계값)

| 사용량 | 상태 | 액션 |
|--------|------|------|
| 0-40% | safe | 정상 작업 |
| 40-60% | monitor | 주의 |
| 60-80% | prepare | 체크포인트 준비 |
| 80-90% | warning | 체크포인트 저장 |
| **90%+** | **critical** | **진행 중 작업 완료 → /commit → 세션 종료** |

### 4. Context 90% 도달 시 동작

Context 90% 도달 시 **추가 작업 없이**:
1. 현재 진행 중인 작업만 완료
2. `/commit`으로 변경사항 커밋
3. 체크포인트 저장 (Todo, 결정사항, 힌트)
4. **세션 종료** (사용자가 `/auto resume`으로 재개)

```
⚠️ Context 90% 도달
   ▶ 진행 중인 작업 완료 중...
   ✅ /commit 실행
   ✅ 체크포인트 저장
   ⏹️ 세션 종료

💡 재개하려면: /auto resume
```

### 5. PRD 작성 및 검토

새 기능 구현 시 PRD 단계를 자동으로 수행합니다:

| 단계 | 설명 |
|------|------|
| **PRD 탐색** | 기존 PRD 문서 확인 (`tasks/prds/`) |
| **PRD 작성** | 없으면 `/create prd` 자동 실행 |
| **PRD 검토** | 요구사항 완전성, 기술 실현 가능성 검토 |
| **PRD 승인** | 사용자 확인 후 구현 진행 |

```
📋 PRD 단계
   ▶ 기존 PRD 탐색... tasks/prds/0045-prd-auth.md 발견
   ▶ PRD 검토 중...
      - 요구사항: 5개 ✓
      - 기술 스펙: 명확 ✓
      - 테스트 시나리오: 3개 ✓
   ✅ PRD 검토 완료 → 구현 진행
```

## 실행 흐름

```
/auto 실행
    │
    ├─ [1] 세션 초기화
    │      - session_id 생성
    │      - 로그 폴더 생성
    │
    ├─ [2] 상태 분석
    │      - Git 상태 (브랜치, 변경사항)
    │      - 열린 이슈/PR
    │      - 테스트 상태
    │      - Todo 미완료 항목
    │      - PRD 문서 상태
    │
    ├─ [3] 작업 판단 (우선순위)
    │      1. 긴급: 빌드 깨짐, 테스트 실패
    │      2. 진행중: 방금 하던 작업 완료
    │      3. 대기중: PR 리뷰, 이슈 해결
    │      4. PRD 필요: 새 기능 → PRD 작성/검토
    │      5. 계획됨: Todo, PRD 체크박스
    │
    ├─ [4] PRD 단계 (새 기능인 경우)
    │      - PRD 탐색 (tasks/prds/)
    │      - PRD 없으면 → /create prd 실행
    │      - PRD 검토 (요구사항, 기술스펙, 테스트)
    │      - 사용자 승인 대기
    │
    ├─ [5] 작업 실행
    │      - 로그 기록
    │      - Context 모니터링
    │      - 80% 도달 시 체크포인트 저장
    │
    └─ [6] 반복 / 종료
           - 할 일 있음 → [2]로 복귀
           - 할 일 없음 → 종료
           - Context 90% → /commit → 세션 종료
```

## 출력 예시

### 기본 실행

```
🤖 /auto - 자율 판단 모드 시작
   Session: session_20251230_103000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 상태 분석 중...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Git: feat/login 브랜치, 3개 파일 수정됨
   테스트: 2개 실패
   이슈: #45 (open), #46 (open)
   PRD: tasks/prds/0045-prd-auth.md ✓
   📊 Context: 12% | 🟢█▁▁▁▁▁▁▁▁

💭 판단: 테스트 실패 → 우선 수정 필요

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ 실행: 테스트 수정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   [LOG] action: analyze_test_failure
   [LOG] action: fix_code
   ▶ 테스트 재실행... ✓ 12/12 통과
   [LOG] action: commit

   📊 Context: 45% | 🟢████▁▁▁▁▁
```

### PRD 단계 (새 기능)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PRD 단계
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ▶ 기존 PRD 탐색... tasks/prds/ 검색 중
   ❌ 관련 PRD 없음

   ▶ PRD 작성 시작 (/create prd)
   📝 "사용자 인증 기능" PRD 생성 중...
   ✅ PRD 작성 완료: tasks/prds/0046-prd-user-auth.md

   ▶ PRD 검토 중...
      - 요구사항: 5개 ✓
      - 기술 스펙: 명확 ✓
      - 테스트 시나리오: 3개 ✓
      - 체크리스트: 8개 항목 ✓

   ❓ PRD를 승인하시겠습니까? (Y/N)
```

### Context 90% 도달

```
   📊 Context: 92% | 🚨█████████

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Context 90% 도달
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ▶ 진행 중인 작업 완료 중...
   ✅ 현재 작업 완료

   ▶ /commit 실행 중...
   ✅ feat(auth): JWT 토큰 발급 구현

   ▶ 체크포인트 저장 중...
   ✅ checkpoint.json 저장 완료
   ✅ state.json 저장 완료

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏹️ 세션 종료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Session: session_20251230_103000
   진행률: 3/5 (60%)
   커밋: feat(auth): JWT 토큰 발급 구현

💡 재개하려면: /auto resume
```

## 세션 재개

```bash
# 마지막 세션 자동 재개
/auto resume

# 특정 세션 재개
/auto resume session_20251230_103000
```

재개 시 표시되는 정보:
- 원본 요청
- 진행률
- 핵심 결정 사항
- 변경된 파일
- 다음 작업 힌트

## 안전장치

| 상황 | 동작 |
|------|------|
| main 브랜치 직접 수정 | 브랜치 생성 후 진행 |
| 위험한 작업 (force push 등) | 스킵 + 알림 |
| 3회 연속 실패 | 루프 중단 + 수동 확인 요청 |
| 무한 루프 감지 | 자동 중단 |

## 중단 방법

| 입력 | 동작 |
|------|------|
| 아무 메시지 | 현재 작업 완료 후 중단 |
| `중단` | 즉시 중단 |
| `/auto pause` | 체크포인트 저장 후 중단 |
| Ctrl+C | 강제 종료 |

## 로그 스키마

```json
{
  "timestamp": "2025-12-30T10:30:00.000Z",
  "sequence": 1,
  "event_type": "action|decision|checkpoint",
  "phase": "init|analysis|implementation|testing|complete",
  "data": {
    "action": "file_read|file_write|command|tool_use",
    "target": "path/to/file",
    "result": "success|fail"
  },
  "context_usage": 45,
  "todo_state": [...]
}
```

## 관련 파일

| 경로 | 용도 |
|------|------|
| `.claude/auto-logs/active/` | 진행 중인 세션 로그 |
| `.claude/auto-logs/archive/` | 완료된 세션 아카이브 |
| `.claude/skills/auto-workflow/` | 스킬 정의 및 스크립트 |

---

## 실행 지시

이 커맨드가 실행되면 다음 순서로 진행하세요:

### 1. 세션 초기화

```python
# 새 세션 또는 resume
if args.get('resume'):
    session_id = args.get('session_id') or get_latest_active_session()
    state, summary = restore_session(session_id)
    print(summary)
else:
    state = AutoState(original_request="자율 판단 모드")
```

### 2. 상태 분석

병렬로 실행:
- `git status --short`
- `git branch --show-current`
- `gh issue list --state open`
- `gh pr list --state open`

### 3. 작업 판단 우선순위

1. **테스트 실패** → 즉시 수정
2. **PR CI 실패** → 해당 브랜치로 이동하여 수정
3. **커밋 안 된 변경** → `/commit` 실행
4. **PRD 필요** → PRD 탐색/작성/검토 (새 기능인 경우)
5. **열린 이슈** → `/issue fix #N`
6. **Todo 미완료** → 해당 작업 진행
7. **모두 완료** → 루프 종료

### 4. PRD 단계 실행

새 기능 작업 감지 시:
```python
# 1. PRD 탐색
prd_files = glob("tasks/prds/*.md")
related_prd = find_related_prd(task_description, prd_files)

if not related_prd:
    # 2. PRD 작성
    execute_skill("/create prd", task_description)

# 3. PRD 검토
review_result = review_prd(prd_path)
# - 요구사항 완전성
# - 기술 실현 가능성
# - 테스트 시나리오

# 4. 사용자 승인
if not user_approved:
    wait_for_approval()
```

### 5. Context 모니터링

매 작업 완료 후:
```python
level = state.update_context_usage(current_percent)

if level == "warning":  # 80%
    # 체크포인트 저장
    state.create_checkpoint(...)

if level == "critical":  # 90%
    # 진행 중인 작업 완료 (추가 작업 없음)
    finish_current_task()
    # /commit 실행
    execute_skill("/commit")
    # 체크포인트 저장
    state.create_checkpoint(...)
    # 세션 종료 (자동 재개 안함)
    state.set_status("paused")
    print("💡 재개하려면: /auto resume")
    exit()
```

### 6. 로그 기록

모든 주요 액션에서:
```python
logger.log_action("file_read", "path/to/file", "success")
logger.log_decision("JWT 선택", "보안 강화")
```
