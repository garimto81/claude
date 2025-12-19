---
name: work
description: Execute work instructions with parallel analysis, issue creation, and strict validation
---

# /work - 작업 지시 실행

작업 지시를 받아 **병렬 분석 → 이슈/문서 → Todo → E2E → TDD 보고**까지 자동 수행합니다.

## 사용법

```
/work <작업 지시 내용>
/work "API 성능 개선"
/work "인증 시스템 리팩토링"

# 에이전트 모드 (서브 에이전트 기반)
/work agent "대규모 기능 구현"
/work agent --template dev "인증 시스템"
```

## 실행 흐름

```
/work 실행
    │
    ├─ Phase 1: 병렬 분석 ─────────────────────────────────┐
    │      │                                               │
    │      ├─ [Agent 1] 문서 분석 (PRD, CLAUDE.md, docs/)  │
    │      │      └─ 관련 문서 식별 및 요약                │
    │      │                                               │ 병렬
    │      └─ [Agent 2] 이슈 분석 (gh issue list)          │
    │             └─ 관련 이슈 식별 및 상태 확인           │
    │                                               ───────┘
    │
    ├─ Phase 2: 이슈 생성 + 문서 업데이트
    │      │
    │      ├─ 분석 결과 통합
    │      ├─ 새 이슈 생성 (필요 시)
    │      └─ 관련 문서 업데이트
    │
    ├─ Phase 3: Todo 작성
    │      │
    │      └─ TodoWrite로 작업 목록 생성
    │           ├─ 구현 태스크
    │           ├─ 테스트 태스크
    │           └─ 검증 태스크
    │
    ├─ Phase 4: E2E 엄격 검증
    │      │
    │      ├─ Playwright 테스트 실행
    │      ├─ 실패 시 자동 수정 (최대 2회)
    │      └─ 3회 실패 → /issue-failed
    │
    └─ Phase 5: TDD 검증 + 보고
           │
           ├─ 단위 테스트 실행
           ├─ 커버리지 확인
           └─ 최종 보고서 출력
```

## Phase 1: 병렬 분석

### 문서 분석 에이전트

```python
Task(
    subagent_type="Explore",
    prompt="""
    작업 지시: {instruction}

    다음을 분석하세요:
    1. CLAUDE.md - 관련 규칙/워크플로우
    2. tasks/prds/ - 관련 PRD
    3. docs/ - 관련 문서
    4. 영향받는 파일 목록

    JSON 형식으로 반환:
    {
        "related_docs": [...],
        "affected_files": [...],
        "recommendations": [...]
    }
    """,
    description="문서 분석"
)
```

### 이슈 분석 에이전트

```python
Task(
    subagent_type="Explore",
    prompt="""
    작업 지시: {instruction}

    다음을 분석하세요:
    1. gh issue list - 관련 이슈 검색
    2. gh pr list - 관련 PR 검색
    3. 중복 이슈 확인
    4. 의존성 이슈 파악

    JSON 형식으로 반환:
    {
        "related_issues": [...],
        "related_prs": [...],
        "duplicates": [...],
        "dependencies": [...]
    }
    """,
    description="이슈 분석"
)
```

## Phase 2: 이슈 생성 + 문서 업데이트

### 이슈 생성 기준

| 조건 | 동작 |
|------|------|
| 관련 이슈 없음 | 새 이슈 생성 |
| 관련 이슈 있음 (Open) | 기존 이슈에 코멘트 추가 |
| 관련 이슈 있음 (Closed) | 새 이슈 생성 + 참조 링크 |

### 문서 업데이트

```bash
# 자동 업데이트 대상
- tasks/prds/NNNN-prd-*.md  # PRD 생성/업데이트
- docs/*.md                  # 관련 문서 수정
- CHANGELOG.md               # 변경 로그 추가
```

## Phase 3: Todo 작성

### Todo 구조

```python
TodoWrite(todos=[
    {"content": "Phase 1: 문서/이슈 분석 완료", "status": "completed", "activeForm": "분석 중"},
    {"content": "Phase 2: 이슈 생성 및 문서 업데이트", "status": "completed", "activeForm": "업데이트 중"},
    {"content": "구현: <핵심 구현 항목>", "status": "in_progress", "activeForm": "구현 중"},
    {"content": "테스트: 단위 테스트 작성", "status": "pending", "activeForm": "테스트 작성 중"},
    {"content": "테스트: E2E 테스트 작성", "status": "pending", "activeForm": "E2E 작성 중"},
    {"content": "검증: TDD 검증", "status": "pending", "activeForm": "TDD 검증 중"},
    {"content": "보고: 최종 결과 보고", "status": "pending", "activeForm": "보고서 작성 중"}
])
```

## Phase 4: E2E 엄격 검증

### 검증 프로세스

```
npx playwright test
    │
    ├─ 성공 → Phase 5 진행
    │
    └─ 실패 → 자동 수정 시도 (최대 2회)
               │
               ├─ 수정 성공 → 재실행
               │
               └─ 3회 실패 → /issue-failed 호출
                              └─ 수동 개입 요청
```

### 검증 기준

| 항목 | 기준 | 실패 시 |
|------|------|---------|
| E2E 테스트 | 100% 통과 | 자동 수정 |
| 성능 | 응답 시간 <3s | 경고 |
| 접근성 | a11y 오류 0 | 경고 |

## Phase 5: TDD 검증 + 보고

### TDD 검증

```bash
# 단위 테스트
pytest tests/ -v --cov=src --cov-report=term

# 커버리지 기준
- 신규 코드: 80% 이상
- 전체: 기존 대비 감소 불가
```

### 최종 보고서

```markdown
# 작업 완료 보고서

## 요약
- **작업 지시**: {instruction}
- **소요 시간**: XX분
- **생성 이슈**: #NNN
- **생성 PR**: #NNN

## Phase 1: 분석 결과
- 관련 문서: N개
- 관련 이슈: N개
- 영향 파일: N개

## Phase 2: 변경 사항
- 생성된 이슈: #NNN - {title}
- 업데이트된 문서: docs/XXX.md

## Phase 3: 구현 내역
| 파일 | 변경 | 설명 |
|------|------|------|
| src/xxx.py | +50/-10 | 기능 구현 |

## Phase 4: E2E 검증
- 테스트: NN개 통과
- 실패: 0개
- 성능: OK

## Phase 5: TDD 검증
- 단위 테스트: NN개 통과
- 커버리지: XX% (기준 80%)

## 다음 단계
1. PR 리뷰 요청
2. 배포 준비
```

## 예시

```bash
$ /work API 응답 캐싱 추가

🔍 Phase 1: 병렬 분석 중...
   [Agent 1] 문서 분석...
      - CLAUDE.md: 캐싱 관련 규칙 없음
      - docs/API.md: 캐싱 미언급
      - 영향 파일: src/api/*.py (5개)

   [Agent 2] 이슈 분석...
      - 관련 이슈: #45 (Closed), #67 (Open)
      - 중복: 없음

📝 Phase 2: 이슈 생성 + 문서 업데이트
   - 이슈 #67에 코멘트 추가
   - docs/API.md 캐싱 섹션 추가

✅ Phase 3: Todo 작성 완료 (7개 항목)

🧪 Phase 4: E2E 검증
   - playwright test: 15/15 통과

📊 Phase 5: TDD 검증
   - pytest: 42/42 통과
   - 커버리지: 85% (기준 80% 충족)

📋 최종 보고서 출력...
```

## 연동 커맨드

| 커맨드 | 연동 시점 |
|--------|----------|
| `/research plan` | Phase 1 전 (선택) |
| `/tdd` | Phase 5 |
| `/issue failed` | E2E 3회 실패 시 |
| `/commit` | 완료 후 |
| `/create pr` | 완료 후 |

## 연동 에이전트

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 1 | `Explore` x2 | 병렬 분석 |
| 2 | `general-purpose` | 이슈/문서 처리 |
| 4 | `test-engineer` | E2E 테스트 |
| 5 | `test-engineer` | TDD 검증 |

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--auto` | 완전 자동화 (최종 보고서만 확인) | `/work --auto "대규모 리팩토링"` |
| `--skip-analysis` | Phase 1 스킵 | `/work --skip-analysis "빠른 수정"` |
| `--no-issue` | 이슈 생성 안함 | `/work --no-issue "내부 리팩토링"` |
| `--strict` | 엄격 모드 (E2E 1회 실패 시 중단) | `/work --strict "프로덕션 배포"` |

### --auto 모드 상세

`/work --auto`는 `/work-auto`와 동일하게 동작합니다:

- 모든 Phase 자동 실행 (중간 확인 없음)
- 7단계 E2E Strict Validation
- 실패 시 자동 수정 (최대 3회)
- 최종 보고서만 사용자에게 제출

---

## /work agent - 에이전트 기반 실행

**메인 에이전트(Supervisor)가 YAML만 관리하고, 서브 에이전트가 실제 작업을 수행합니다.**

### 사용법

```bash
/work agent "대규모 기능 구현"
/work agent --template dev "인증 시스템"
/work agent --template research "프레임워크 비교"
```

### 기본 /work와의 차이

| 항목 | `/work` (기본) | `/work agent` |
|------|---------------|---------------|
| 실행 주체 | 메인 에이전트가 직접 | 서브 에이전트가 작업 |
| 상태 관리 | 메모리 기반 | YAML 파일 기반 |
| 진행상황 공유 | O | X (결과만 공유) |
| 확장성 | 단일 컨텍스트 | 독립 컨텍스트 (병렬) |
| 용도 | 일반 작업 | 대규모/복잡한 작업 |

### 실행 흐름

```
/work agent "사용자 인증 기능"
    │
    ├─ Step 1: 태스크 분해 (Supervisor)
    │      │
    │      └─ 작업을 독립적인 태스크로 분해
    │           ├─ task-001: DB 스키마 설계
    │           ├─ task-002: API 구현
    │           ├─ task-003: 테스트 작성
    │           └─ task-004: 문서화
    │
    ├─ Step 2: YAML 작성 (Supervisor)
    │      │
    │      └─ .agent/tasks/*.yaml 생성
    │
    ├─ Step 3: 에이전트 스폰 (병렬)
    │      │
    │      ├─ [Agent 1] database-specialist
    │      ├─ [Agent 2] backend-dev
    │      ├─ [Agent 3] test-engineer
    │      └─ [Agent 4] docs-writer
    │
    │      ※ 각 에이전트는 독립 실행 (진행상황 공유 X)
    │
    ├─ Step 4: 결과 수집 (Supervisor)
    │      │
    │      └─ .agent/results/*.yaml 읽기
    │           └─ 결과 검증 및 통합
    │
    └─ Step 5: 최종 보고
           │
           └─ E2E 검증 → TDD 검증 → 보고서
```

### YAML 파일 구조

**각 레포의 로컬 폴더에 저장** (레포별 독립 관리)

```
{project-root}/
└── .agent/                    # 레포별 에이전트 폴더
    ├── tasks/                 # 태스크 정의
    │   ├── task-001.yaml      # Supervisor → Agent
    │   └── task-002.yaml
    │
    ├── results/               # 결과 저장
    │   ├── result-001.yaml    # Agent → Supervisor
    │   └── result-002.yaml
    │
    └── state.yaml             # 전체 상태 (Supervisor 관리)
```

### 템플릿

| 템플릿 | 에이전트 구성 | 용도 |
|--------|-------------|------|
| `dev` | architect → coder, tester, docs | 기능 개발 |
| `research` | 4x research (병렬) | 리서치 |
| `review` | security, logic, style, perf | 코드 리뷰 |
| `fix` | debugger → coder → tester | 버그 수정 |

### 예시

```bash
$ /work agent --template dev "OAuth2 인증 구현"

📋 Workflow 시작: OAuth2 인증 구현

[Step 1] 태스크 분해
   ├─ task-001: 아키텍처 설계 (architect)
   ├─ task-002: OAuth2 라이브러리 연동 (coder)
   ├─ task-003: 테스트 작성 (tester)
   └─ task-004: API 문서화 (docs)

[Step 2] YAML 작성
   └─ .agent/tasks/ (4 files)

[Step 3] 에이전트 스폰
   ├─ [순차] architect (의존성: 없음)
   │      └─ 완료 → result-001.yaml
   │
   └─ [병렬] coder, tester, docs (의존성: architect)
          ├─ 완료 → result-002.yaml
          ├─ 완료 → result-003.yaml
          └─ 완료 → result-004.yaml

[Step 4] 결과 수집
   └─ 4/4 태스크 완료

[Step 5] 검증 및 보고
   ├─ E2E: 12/12 통과
   ├─ TDD: 28/28 통과 (85% 커버리지)
   └─ 문서: docs/oauth2.md 생성됨

✅ 완료 | 총 소요: 8분 32초
```

### 언제 사용?

| 상황 | 권장 |
|------|------|
| 간단한 버그 수정 | `/work` (기본) |
| 중간 규모 기능 | `/work` (기본) |
| **대규모 기능 개발** | `/work agent` ✅ |
| **병렬 리서치** | `/work agent --template research` ✅ |
| **복잡한 리팩토링** | `/work agent --template dev` ✅ |

---

**작업 지시를 입력해 주세요.**
