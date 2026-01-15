---
name: auto
description: 통합 자동화 커맨드 - 무한 작업, 서브에이전트 위임, 세션 관리
version: 5.0.0
triggers:
  keywords:
    - "auto"
    - "자동"
    - "자율"
    - "무한"
model_preference: opus
auto_trigger: false
---

# /auto - 통합 자동화 커맨드 (v5.0)

> **하나의 커맨드로 모든 자동화를 통합**
> `/auto`, `/delegate`, `/orchestrate` 기능을 하나로 통합한 완벽한 자동화 솔루션

## 사용법

```bash
/auto                          # 자동 작업 시작/계속 (무한 반복)
/auto "지시 내용"               # 특정 방향으로 작업
/auto status                   # 현재 진행 상황 정리
/auto redirect "새 방향"        # 방향 수정
/auto stop                     # 작업 중지 + 최종 보고서
```

---

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **무한 반복** | "할 일 없음"은 종료 조건이 아님 → 자율 발견 |
| **서브에이전트 강제** | Python 스크립트가 Task tool 사용을 강제 |
| **세션 관리** | 진행 상황을 session.yaml에 저장, 언제든 확인 가능 |
| **사용자 친화적** | 돌아와서 status 확인, redirect로 방향 수정 |

---

## ⚠️ 중요: Task tool 강제 실행

**이 커맨드는 Python 스크립트를 통해 Task tool 사용을 강제합니다.**

```bash
# 실제 실행되는 스크립트
python C:\claude\.claude\skills\auto-executor\scripts\auto_executor.py
```

### 스크립트 옵션

| 옵션 | 설명 |
|------|------|
| (없음) | 자동 작업 시작/계속 |
| `--task "지시"` | 특정 작업 실행 |
| `--status` | 진행 상황 출력 |
| `--redirect "방향"` | 방향 수정 |
| `--stop` | 세션 종료 |
| `--max N` | 최대 N회 반복 |
| `--dry-run` | 실행 없이 계획만 |

---

## 실행 지시

### 스크립트 실행 (필수)

**$ARGUMENTS를 분석하여 적절한 스크립트 옵션으로 변환 후 실행하세요:**

```bash
# /auto → 기본 실행
python C:\claude\.claude\skills\auto-executor\scripts\auto_executor.py --max 1

# /auto "지시" → 특정 작업
python C:\claude\.claude\skills\auto-executor\scripts\auto_executor.py --task "$ARGUMENTS" --max 1

# /auto status → 상태 확인
python C:\claude\.claude\skills\auto-executor\scripts\auto_executor.py --status

# /auto redirect "새 방향" → 방향 수정
python C:\claude\.claude\skills\auto-executor\scripts\auto_executor.py --redirect "$NEW_DIRECTION"

# /auto stop → 종료
python C:\claude\.claude\skills\auto-executor\scripts\auto_executor.py --stop
```

**스크립트 실행 후 결과를 사용자에게 보고하세요.**

---

## 실행 지시 (스크립트 실행 불가 시 Fallback)

### 파라미터 파싱

$ARGUMENTS를 분석하여 모드를 결정하세요:

| 입력 | 모드 |
|------|------|
| (없음) | 작업 모드 - 자동 작업 시작/계속 |
| `"지시 내용"` | 작업 모드 - 특정 방향으로 작업 |
| `status` | 상황 보고 모드 |
| `redirect "새 방향"` | 방향 수정 모드 |
| `stop` | 종료 모드 |

---

## [작업 모드] /auto 또는 /auto "지시"

### STEP 1: 세션 상태 확인

`.claude/auto/session.yaml` 파일을 확인하세요.

- **파일 존재**: 기존 세션 계속
- **파일 없음**: 새 세션 시작

새 세션 시작 시 session.yaml 생성:

```yaml
session_id: auto_YYYYMMDD_NNN
started_at: ISO8601
direction: "$ARGUMENTS 또는 자동 판단"
status: running

tasks:
  completed: []
  in_progress: []
  pending: []

statistics:
  total_tasks: 0
  completed: 0
  in_progress: 0
  pending: 0
  total_duration: 0min
```

### STEP 2: 작업 발견 (5계층 우선순위)

다음 순서로 작업을 발견하세요:

#### Tier 0: 세션 관리
- Context 90% 이상 → 정리 후 종료 안내

#### Tier 1: 명시적 지시
- 사용자가 `"지시"` 입력 → 해당 작업 우선

#### Tier 2: 긴급 (자동 탐지)
```bash
# 테스트 실패 확인
git diff --name-only | grep -E "test.*\.(py|ts|js)$"
pytest tests/ --co -q 2>/dev/null | head -5

# 린트 오류 확인
ruff check src/ --statistics 2>/dev/null | head -5

# 빌드 오류 확인
tsc --noEmit 2>&1 | head -5
```

- 테스트 실패 → 디버깅 작업
- 린트 오류 10개+ → 린트 수정 작업
- 빌드 실패 → 빌드 수정 작업

#### Tier 3: 작업 처리
```bash
# 변경 사항 확인
git diff --stat | tail -1

# 열린 이슈 확인
gh issue list --state open --limit 3 2>/dev/null

# PR 리뷰 확인
gh pr list --state open --limit 3 2>/dev/null
```

- 변경 100줄+ → 커밋 작업
- 열린 이슈 → 이슈 해결 작업
- PR 대기 → PR 리뷰 작업

#### Tier 4: 자율 개선
- 테스트 커버리지 < 80% → 테스트 추가
- 문서 업데이트 필요 → 문서 작성
- 코드 품질 개선 가능 → 리팩토링

### STEP 3: 에이전트 자동 선택

발견된 작업에서 키워드를 분석하여 에이전트를 선택하세요:

| 키워드 패턴 | 에이전트 |
|-------------|----------|
| 분석, 탐색, 구조, 리서치 | `Explore` |
| 버그, 에러, 실패, 디버그, 테스트 실패 | `debugger` |
| 테스트, TDD, 커버리지, 테스트 추가 | `test-engineer` |
| 리뷰, 검토, 품질, 린트 | `code-reviewer` |
| API, 백엔드, 서버, 엔드포인트 | `backend-dev` |
| UI, 프론트, 컴포넌트, 화면 | `frontend-dev` |
| 보안, 취약점, 인증, 권한 | `security-auditor` |
| 문서, README, 가이드, 설명 | `docs-writer` |
| DB, 쿼리, 마이그레이션, 스키마 | `database-specialist` |
| 설계, 아키텍처, 구조 설계 | `architect` |
| 배포, CI/CD, 인프라, 도커 | `devops-engineer` |
| Python, FastAPI, Django | `python-dev` |
| TypeScript, React, Next.js | `typescript-dev` |
| 커밋, git | `Bash` (직접 실행) |

**기본값**: 매칭 없으면 `Explore` 사용

### STEP 4: TodoWrite 업데이트

발견된 작업을 TodoWrite로 등록하세요:

```python
TodoWrite(todos=[
    {
        "content": "{작업 설명}",
        "status": "in_progress",
        "activeForm": "{작업 설명} 진행 중"
    },
    # 추가 발견된 작업들은 pending으로
])
```

### STEP 5: Task tool로 서브에이전트 실행 (핵심)

**반드시 Task tool을 사용하여 서브에이전트에 작업을 위임하세요.**

```python
Task(
    subagent_type="{STEP 3에서 선택한 에이전트}",
    prompt="""
## 작업 지시
{발견된 작업 설명}

## 프로젝트 정보
- 경로: C:\claude
- 현재 브랜치: {git branch 결과}

## 중요 규칙
1. 작업을 완료하고 결과만 반환하세요
2. 중간 질문 없이 최선의 판단으로 진행하세요
3. 코드 변경 시 테스트도 함께 확인하세요

## 결과 형식
### 요약
- 한 줄 요약

### 수행 작업
- 작업 1
- 작업 2

### 변경 파일 (있는 경우)
| 파일 | 변경 |
|------|------|

### 검증 방법
- 확인 명령어
    """,
    description="{작업 요약 3-5단어}"
)
```

### STEP 6: 결과 수집 및 세션 저장

서브에이전트 결과를 받으면:

1. **session.yaml 업데이트**
   - in_progress → completed로 이동
   - 결과 요약 추가
   - statistics 업데이트

2. **TodoWrite 업데이트**
   - 완료된 작업 completed로 변경

### STEP 7: 결과 보고 및 다음 안내

다음 형식으로 보고하세요:

```markdown
## /auto 작업 완료

### 실행된 작업
> {작업 설명}

### 에이전트
{사용된 에이전트}

### 결과 요약
{서브에이전트 결과 요약}

### 진행 현황
| 상태 | 개수 |
|------|------|
| 완료 | {N} |
| 대기 | {M} |

---

**다음 단계**
- 계속 진행: `/auto`
- 상황 확인: `/auto status`
- 방향 수정: `/auto redirect "새 방향"`
- 종료: `/auto stop`
```

---

## [상황 보고 모드] /auto status

`.claude/auto/session.yaml` 파일을 읽어서 다음 형식으로 보고하세요:

```markdown
## /auto 진행 현황

### 세션 정보
| 항목 | 값 |
|------|-----|
| 세션 ID | {session_id} |
| 시작 | {started_at} |
| 방향 | {direction} |
| 상태 | {status} |

### 완료된 작업 ({N}개)
1. ✅ {작업1} ({에이전트}, {소요시간})
2. ✅ {작업2} ({에이전트}, {소요시간})
...

### 진행중 ({N}개)
🔄 {작업} ({에이전트})

### 대기중 ({N}개)
⏳ {작업1}
⏳ {작업2}
...

### 통계
| 항목 | 값 |
|------|-----|
| 총 작업 | {total_tasks} |
| 완료 | {completed} |
| 총 시간 | {total_duration} |

---

**명령어**
- 계속 진행: `/auto`
- 방향 수정: `/auto redirect "새 방향"`
- 종료: `/auto stop`
```

---

## [방향 수정 모드] /auto redirect "새 방향"

1. **현재 작업 정리**
   - 진행중인 작업 완료 대기 또는 취소
   - 대기중인 작업 목록 초기화

2. **새 방향 설정**
   - session.yaml의 direction 업데이트
   - 새 방향 기반으로 작업 재발견

3. **보고**
```markdown
## /auto 방향 수정 완료

### 이전 방향
> {이전 direction}

### 새 방향
> {새 direction}

### 정리된 작업
- {취소된 작업 목록}

---

새 방향으로 작업을 시작하려면 `/auto` 입력
```

---

## [종료 모드] /auto stop

1. **전체 작업 요약 수집**
   - session.yaml에서 모든 완료된 작업 수집

2. **변경 파일 집계**
   ```bash
   git diff --stat HEAD~{완료된 커밋 수}
   ```

3. **최종 보고서 출력**

```markdown
## /auto 최종 보고서

### 세션 요약
| 항목 | 값 |
|------|-----|
| 세션 ID | {session_id} |
| 기간 | {started_at} ~ {now} |
| 총 시간 | {total_duration} |
| 방향 | {direction} |

### 작업 통계
| 상태 | 개수 |
|------|------|
| 완료 | {completed} |
| 미완료 | {pending + in_progress} |
| 총계 | {total_tasks} |

### 주요 성과
1. {성과 1}
2. {성과 2}
3. {성과 3}

### 사용된 에이전트
| 에이전트 | 작업 수 |
|----------|---------|
| {agent1} | {N} |
| {agent2} | {M} |

### 변경 파일
| 파일 | 변경 |
|------|------|
| {file1} | +{N}, -{M} |
| {file2} | +{N} |

### 미완료 작업
- {미완료 작업 1}
- {미완료 작업 2}

---

세션이 종료되었습니다.
새 세션을 시작하려면 `/auto` 입력
```

4. **세션 파일 아카이브**
   - `.claude/auto/session.yaml` → `.claude/auto/history/session_{id}.yaml`로 이동
   - 새 세션을 위해 session.yaml 삭제

---

## 세션 파일 구조

### .claude/auto/session.yaml

```yaml
session_id: auto_20260115_001
started_at: 2026-01-15T10:00:00
direction: "API 리팩토링"
status: running  # running | completed

tasks:
  completed:
    - id: task_001
      description: "API 엔드포인트 분석"
      agent: Explore
      started_at: 2026-01-15T10:00:00
      completed_at: 2026-01-15T10:05:00
      duration: 5min
      result: "15개 엔드포인트 발견"

  in_progress:
    - id: task_002
      description: "린트 오류 수정"
      agent: code-reviewer
      started_at: 2026-01-15T10:05:00

  pending:
    - id: task_003
      description: "테스트 커버리지 개선"
      agent: test-engineer

statistics:
  total_tasks: 10
  completed: 5
  in_progress: 1
  pending: 4
  total_duration: 25min
```

---

## 폴더 구조

```
.claude/auto/
├── session.yaml          # 현재 세션 상태
└── history/              # 완료된 세션 아카이브
    ├── session_20260114_001.yaml
    └── session_20260115_001.yaml
```

---

## 예시

### 예시 1: 기본 사용

```bash
$ /auto

# [STEP 1] 세션 확인 → 새 세션 시작
# [STEP 2] 작업 발견 → 린트 오류 15개 발견
# [STEP 3] 에이전트 선택 → code-reviewer
# [STEP 4] TodoWrite 등록
# [STEP 5] Task tool 실행
# [STEP 6] 결과 수집
# [STEP 7] 보고

## /auto 작업 완료

### 실행된 작업
> 린트 오류 15개 수정

### 에이전트
code-reviewer

### 결과 요약
- ruff 경고 15개 수정
- 주요 수정: unused imports, line length

### 진행 현황
| 상태 | 개수 |
|------|------|
| 완료 | 1 |
| 대기 | 3 |

---

**다음 단계**
- 계속 진행: `/auto`
- 상황 확인: `/auto status`
```

### 예시 2: 방향 지정

```bash
$ /auto "테스트 커버리지 80% 달성해줘"

# direction: "테스트 커버리지 80% 달성"으로 설정
# test-engineer 에이전트로 작업 위임
```

### 예시 3: 상황 확인

```bash
$ /auto status

## /auto 진행 현황

### 세션 정보
| 항목 | 값 |
|------|-----|
| 시작 | 2026-01-15 10:00 |
| 방향 | 테스트 커버리지 80% 달성 |
| 경과 | 25분 |

### 완료된 작업 (3개)
1. ✅ 현재 커버리지 분석 (Explore, 3분)
2. ✅ 미커버 함수 식별 (test-engineer, 5분)
3. ✅ auth 모듈 테스트 추가 (test-engineer, 10분)

### 대기중 (2개)
⏳ api 모듈 테스트 추가
⏳ utils 모듈 테스트 추가
```

---

## 관련 파일

| 경로 | 용도 |
|------|------|
| `.claude/auto/session.yaml` | 현재 세션 상태 |
| `.claude/auto/history/` | 완료된 세션 아카이브 |
| `.claude/agents/` | 사용 가능한 에이전트 정의 |

---

## 마이그레이션 안내

기존 `/delegate`, `/orchestrate` 사용자:

| 기존 | 새로운 |
|------|--------|
| `/delegate "작업"` | `/auto "작업"` |
| `/orchestrate "작업"` | `/auto "작업"` |
| `/work --loop` | `/auto` |

---

**작업을 시작하려면 `/auto`를 입력하세요.**
