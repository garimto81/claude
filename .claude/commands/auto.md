---
name: auto
description: 자율 판단 자동 완성 - 9개 커맨드 통합, Context 예측 관리, 5계층 우선순위
alias_of: /work --loop
version: 4.0.0
---

# /auto - 자율 판단 자동 완성 (v4.0 - 9개 커맨드 통합)

> **Note**: `/auto`는 `/work --loop`의 alias입니다. 동일한 기능을 수행합니다.

Claude가 **다음에 해야 할 작업을 스스로 판단**하고 **자동으로 실행**합니다.
**"할 일 없음"은 종료 조건이 아닙니다** → 스스로 개선점을 발견합니다.

## 통합 커맨드 (자동 트리거)

| 커맨드 | 조건 | 트리거 |
|--------|------|--------|
| `/debug` | 테스트 실패 + 원인 불명확 | Tier 1 |
| `/check --fix` | 린트/타입 경고 10개+ | Tier 1 |
| `/check --security` | 보안 취약점 (Critical/High) | Tier 1 |
| `/commit` | 변경 100줄+ | Tier 2 |
| `/issue fix` | 열린 이슈 존재 | Tier 2 |
| `/pr auto` | PR 리뷰 대기 | Tier 2 |
| `/tdd` | 새 기능 구현 요청 | Tier 3 |
| `/research` | 코드 분석/정보 수집 필요 | Tier 3 |
| `/audit quick` | 세션 시작 시 | Tier 0 |

## 사용법

```bash
# /auto 사용 (기존 방식 - 하위 호환)
/auto                         # 자율 판단 루프 시작 (무한)
/auto --max 10                # 최대 10회 반복 후 종료
/auto --promise "ALL_DONE"    # 조건 충족 시 종료
/auto resume [id]             # 세션 재개
/auto status                  # 현재 상태 확인
/auto pause                   # 일시 정지 (체크포인트 저장)
/auto abort                   # 세션 취소
/auto --dry-run               # 판단만 보여주고 실행 안함

# /work --loop 사용 (권장 - 통합 인터페이스)
/work --loop                  # 자율 판단 루프 시작
/work --loop --max 5          # 최대 5회 반복
/work --loop resume           # 세션 재개
```

## 상세 문서

전체 기능 설명은 `/work` 커맨드의 `--loop` 모드 섹션을 참조하세요:

→ `.claude/commands/work.md` > `## --loop 모드 (자율 판단 + 자율 발견)`

---

## 핵심 원칙 (Ralph Wiggum 철학)

> **"Iteration > Perfection"** - 완벽보다 반복이 중요
> **"Failures Are Data"** - 실패는 정보
> **"Persistence Wins"** - 끈기가 승리

## 종료 조건 (명시적으로만 종료)

| 조건 | 설명 |
|------|------|
| `--max N` | N회 반복 후 종료 |
| `--promise TEXT` | `<promise>TEXT</promise>` 출력 시 종료 |
| `pause` / `abort` | 사용자 명시적 중단 |
| Context 90% | 체크포인트 저장 후 종료 (resume 가능) |

**⚠️ "할 일 없음"은 종료 조건이 아님**

## 핵심 기능 요약

| 기능 | 설명 |
|------|------|
| **5계층 우선순위** | Tier 0(세션) → Tier 1(긴급) → Tier 2(작업) → Tier 3(개발) → Tier 4(자율) |
| **9개 커맨드 통합** | /check, /commit, /issue, /debug, /parallel, /tdd, /research, /pr, /audit |
| **Context 예측** | 80%에서 다음 작업 예측, 초과 시 정리 |
| **병렬 처리** | 모든 Tier에서 2-4 에이전트 병렬 실행 |
| **E2E 검증** | Functional/Visual/A11y/Perf 4방향 병렬 |

## Context 관리

### 80% 도달 시

```
현재 작업 완료
    │
    ├─ 다음 작업 탐색 (병렬)
    │
    ├─ 예상 Context 분석
    │      │
    │      ├─ 예상 +20% 미만 → 계속 진행
    │      │
    │      └─ 예상 +20% 이상 → 정리 필요
    │              │
    │              ├─ 세션 문서 업데이트
    │              ├─ /commit 실행
    │              ├─ /clear 실행
    │              └─ /auto 재시작
```

### 90% 도달 시 (즉시 정리)

```
Context 90% 도달
    │
    ├─ 추가 작업 없이 현재 작업만 완료
    ├─ 세션 문서 업데이트
    ├─ /commit 실행
    ├─ /clear 실행
    └─ /auto 재시작 (체크포인트에서 재개)
```

## 5계층 우선순위 체계

### Tier 0: 세션 관리
- 세션 시작 → `/audit quick`
- Context 80%/90% → 정리 후 재시작

### Tier 1: 긴급
- 테스트 실패 → `/debug`
- 빌드 실패 → `/debug`
- 린트/타입 경고 10+개 → `/check --fix`
- 보안 취약점 → `/check --security`

### Tier 2: 작업 처리
- 변경 100줄+ → `/commit`
- 열린 이슈 → `/issue fix #N`
- PR 리뷰 대기 → `/pr auto`

### Tier 3: 개발 지원
- 새 기능 구현 → `/tdd`
- 코드 분석 → `/research code`
- 솔루션 탐색 → `/research web`

### Tier 4: 자율 개선
- 코드 품질 → 린트 경고 수정
- 테스트 커버리지 → 미달 영역 보강
- 문서화 → README, API 문서 개선
- 리팩토링 → 중복 코드, 복잡도 개선

### Tier 4+: 자율 발견
- PRD 분석 → 개선점 탐색
- 솔루션 비교 → 더 나은 라이브러리 탐색
- 마이그레이션 → 자동 교체 제안

## 관련 파일

| 경로 | 용도 |
|------|------|
| `.claude/commands/work.md` | 통합 커맨드 (상세 문서) |
| `.claude/auto-logs/` | 세션 로그 저장소 |
| `.claude/skills/auto-workflow/` | 스킬 정의 및 스크립트 |
