---
name: orchestrate
description: YAML 기반 메인-서브 에이전트 오케스트레이션 (백그라운드 격리 실행)
version: 1.0.0
triggers:
  keywords:
    - "orchestrate"
    - "오케스트레이션"
    - "메인-서브"
    - "격리 실행"
model_preference: opus
auto_trigger: false
---

# /orchestrate - 메인-서브 에이전트 오케스트레이션

사용자 지시를 받아 **YAML 업무 정의 → 서브 에이전트 백그라운드 실행 → 결과 수집 → 보고**까지 자동 수행합니다.

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **YAML 기반** | 모든 업무와 결과를 YAML 파일로 관리 |
| **진행 상황 비공유** | 서브 에이전트는 진행 상황을 공유하지 않음 |
| **결과만 저장** | 서브 에이전트는 결과만 YAML에 저장 후 완료 신호 |
| **메인 판단** | 메인 에이전트가 결과 확인 후 다음 단계 판단 |

## 사용법

```
/orchestrate <작업 지시 내용>
/orchestrate "로그인 기능 만들어줘"
/orchestrate "데이터 분석하고 보고서 작성해줘"
/orchestrate "API 3개 만들고 테스트까지"
```

## 폴더 구조

```
.claude/workflow/
├── jobs/                    # 업무 정의
│   └── job_YYYYMMDD_NNN.yaml
├── results/                 # 서브 에이전트 결과
│   ├── task_001.yaml
│   ├── task_002.yaml
│   └── ...
└── history/                 # 완료된 워크플로우 아카이브
```

## 실행 흐름

```
/orchestrate 실행
    │
    ├─ STEP 1: 지시 분석 ────────────────────────────────────┐
    │      │                                                 │
    │      ├─ 사용자 지시 파싱                               │
    │      ├─ 필요 에이전트 결정                             │
    │      └─ 작업 순서 및 의존성 분석                       │
    │                                                ────────┘
    │
    ├─ STEP 2: YAML 업무 파일 생성
    │      │
    │      └─ .claude/workflow/jobs/job_YYYYMMDD_NNN.yaml
    │           ├─ job_id
    │           ├─ request (원본 지시)
    │           ├─ tasks[] (작업 목록)
    │           │    ├─ id
    │           │    ├─ agent (담당 에이전트)
    │           │    ├─ action (수행 내용)
    │           │    ├─ depends_on (의존성)
    │           │    └─ output_file (결과 저장 위치)
    │           └─ status: pending
    │
    ├─ STEP 3: 서브 에이전트 백그라운드 실행 ────────────────┐
    │      │                                                 │ 격리
    │      ├─ Task tool (run_in_background: true)            │ 실행
    │      ├─ 진행 상황 공유 없음                            │
    │      └─ 결과만 YAML에 저장                             │
    │                                                ────────┘
    │
    ├─ STEP 4: 결과 수집 (TaskOutput으로 완료 대기)
    │      │
    │      ├─ 각 서브 에이전트 완료 신호 대기
    │      └─ results/*.yaml 파일 확인
    │
    └─ STEP 5: 결과 보고 및 판단
           │
           ├─ 결과 통합
           ├─ 성공/실패 판단
           ├─ 후속 작업 결정
           └─ 사용자에게 최종 보고
```

## STEP 1: 지시 분석

사용자 지시를 분석하여 필요한 에이전트와 작업을 결정합니다.

### 에이전트 매핑

| 작업 유형 | 담당 에이전트 |
|-----------|---------------|
| 설계/아키텍처 | `architect` |
| 백엔드 개발 | `backend-dev` |
| 프론트엔드 개발 | `frontend-dev` |
| 테스트 작성 | `test-engineer` |
| 코드 리뷰 | `code-reviewer` |
| 데이터 분석 | `data-specialist` |
| 문서 작성 | `docs-writer` |
| 리서치 | `Explore` |
| 보안 검토 | `security-auditor` |
| 디버깅 | `debugger` |

## STEP 2: YAML 업무 파일 생성

### 업무 파일 구조 (jobs/job_YYYYMMDD_NNN.yaml)

```yaml
job_id: job_20251220_001
created_at: 2025-12-20T10:00:00
request: "로그인 기능 만들어줘"
status: pending

tasks:
  - id: task_001
    agent: architect
    action: "로그인 기능 설계"
    input:
      requirements: "JWT 기반 인증"
    depends_on: null
    output_file: results/task_001.yaml
    status: pending

  - id: task_002
    agent: backend-dev
    action: "API 엔드포인트 구현"
    input:
      use_result: task_001
    depends_on: task_001
    output_file: results/task_002.yaml
    status: waiting

  - id: task_003
    agent: test-engineer
    action: "테스트 코드 작성"
    input:
      use_result: task_002
    depends_on: task_002
    output_file: results/task_003.yaml
    status: waiting
```

## STEP 3: 서브 에이전트 백그라운드 실행

### 실행 방식

```python
# 메인 에이전트가 서브 에이전트 실행
Task(
    subagent_type="{agent_type}",
    prompt="""
    ## 작업 지시
    {action}

    ## 입력 데이터
    {input}

    ## 중요 규칙
    1. 진행 상황을 메인 에이전트에 보고하지 마세요
    2. 작업 완료 후 결과만 아래 파일에 저장하세요
    3. 저장 후 "완료" 메시지만 반환하세요

    ## 결과 저장 위치
    {output_file}

    ## 결과 YAML 형식
    task_id: {task_id}
    agent: {agent}
    status: completed | failed
    started_at: ISO8601
    completed_at: ISO8601
    output:
      summary: "작업 결과 요약"
      details: "상세 내용"
      files_created: []
      files_modified: []
    errors: null | "에러 메시지"
    """,
    run_in_background=True,
    description="{action}"
)
```

### 통신 규칙

| 허용 | 금지 |
|------|------|
| 결과 YAML 저장 | 진행 상황 보고 |
| 완료 신호 | 중간 질문 |
| 에러 기록 | 실시간 대화 |

## STEP 4: 결과 수집

### 완료 대기

```python
# 각 서브 에이전트 완료 대기
TaskOutput(task_id="{agent_task_id}", block=True)
```

### 결과 파일 구조 (results/task_NNN.yaml)

```yaml
task_id: task_001
agent: architect
status: completed
started_at: 2025-12-20T10:05:00
completed_at: 2025-12-20T10:15:00

output:
  summary: "JWT 기반 로그인 설계 완료"
  details: |
    - 엔드포인트: POST /api/auth/login
    - 토큰 유효기간: 24시간
    - 리프레시 토큰: 7일
  files_created:
    - docs/auth-design.md
  files_modified: []
  recommendations:
    - "bcrypt 해싱 권장"
    - "Rate limiting 추가 권장"

errors: null
```

## STEP 5: 결과 보고 및 판단

### 결과 통합

메인 에이전트가 모든 results/*.yaml 파일을 읽어 통합합니다.

### 최종 보고 형식

```markdown
# /orchestrate 완료 보고

## 요약
> {원본 지시} 작업이 완료되었습니다.

## 작업 흐름
┌──────────┐    ┌──────────┐    ┌──────────┐
│ 설계     │───▶│ 구현     │───▶│ 테스트   │
│ 완료     │    │ 완료     │    │ 완료     │
└──────────┘    └──────────┘    └──────────┘

## 서브 에이전트 결과

| 에이전트 | 작업 | 상태 | 소요 시간 |
|----------|------|------|-----------|
| architect | 설계 | 완료 | 10분 |
| backend-dev | API 구현 | 완료 | 25분 |
| test-engineer | 테스트 | 완료 | 15분 |

## 변경 파일
| 파일 | 변경 |
|------|------|
| src/auth/login.py | +120 |
| tests/test_auth.py | +80 |

## 검증 방법
- `pytest tests/test_auth.py -v`
- `curl -X POST http://localhost:8000/api/auth/login`

## 주의점
- Rate limiting 미적용 상태
- 프로덕션 배포 전 보안 검토 필요
```

### 판단 및 후속 조치

| 결과 | 후속 조치 |
|------|-----------|
| 모든 작업 성공 | 최종 보고 출력 |
| 일부 실패 | 실패 작업 재시도 또는 사용자에게 질문 |
| 전체 실패 | 원인 분석 후 사용자에게 보고 |

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--parallel` | 독립 작업 병렬 실행 | `/orchestrate --parallel "3개 API 만들어줘"` |
| `--sequential` | 모든 작업 순차 실행 | `/orchestrate --sequential "단계별 진행"` |
| `--timeout=N` | 작업별 타임아웃 (분) | `/orchestrate --timeout=30 "대규모 작업"` |
| `--retry=N` | 실패 시 재시도 횟수 | `/orchestrate --retry=2 "중요한 작업"` |

## 예시

### 예시 1: 로그인 기능

```bash
$ /orchestrate 로그인 기능 만들어줘

STEP 1: 지시 분석
   - 작업 유형: 기능 개발
   - 필요 에이전트: architect, backend-dev, test-engineer
   - 작업 수: 3개

STEP 2: 업무 파일 생성
   - .claude/workflow/jobs/job_20251220_001.yaml

STEP 3: 서브 에이전트 실행 (백그라운드)
   - [architect] 설계 시작... (격리 실행)
   - [backend-dev] 대기 중 (task_001 의존)
   - [test-engineer] 대기 중 (task_002 의존)

STEP 4: 결과 수집 중...
   task_001 완료 (architect)
   task_002 완료 (backend-dev)
   task_003 완료 (test-engineer)

STEP 5: 최종 보고
   [보고서 출력]
```

### 예시 2: 데이터 분석

```bash
$ /orchestrate 매출 데이터 분석하고 보고서 만들어줘

STEP 1: 지시 분석
   - 작업 유형: 데이터 분석 + 문서 작성
   - 필요 에이전트: data-specialist, docs-writer
   - 작업 수: 2개

STEP 2: 업무 파일 생성
   - .claude/workflow/jobs/job_20251220_002.yaml

STEP 3: 서브 에이전트 실행 (백그라운드)
   - [data-specialist] 분석 시작... (격리 실행)
   - [docs-writer] 대기 중 (task_001 의존)

STEP 4: 결과 수집 중...
   task_001 완료 (data-specialist)
   task_002 완료 (docs-writer)

STEP 5: 최종 보고
   [보고서 출력]
```

## 연동 커맨드

| 커맨드 | 연동 시점 |
|--------|----------|
| `/research` | STEP 1 전 (선택) |
| `/commit` | 완료 후 |
| `/check` | 완료 후 검증 |

## 아카이브

완료된 워크플로우는 자동으로 아카이브됩니다:

```bash
.claude/workflow/history/
└── job_20251220_001/
    ├── job.yaml          # 원본 업무 정의
    ├── results/          # 결과 파일들
    │   ├── task_001.yaml
    │   ├── task_002.yaml
    │   └── task_003.yaml
    └── summary.yaml      # 최종 요약
```

---

**작업 지시를 입력해 주세요.**
