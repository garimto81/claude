---
name: auto
description: 자율 판단 자동 완성 - Claude가 다음 작업을 스스로 판단하고 실행 (→ /work --loop alias)
alias_of: /work --loop
---

# /auto - 자율 판단 자동 완성 (Ralph Wiggum 통합)

> **Note**: `/auto`는 `/work --loop`의 alias입니다. 동일한 기능을 수행합니다.

Claude가 **다음에 해야 할 작업을 스스로 판단**하고 **자동으로 실행**합니다.
**"할 일 없음"은 종료 조건이 아닙니다** → 스스로 개선점을 발견합니다.

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
| **자율 발견** | 명시적 작업 없으면 스스로 개선점 탐색 |
| **2계층 우선순위** | Tier 1(명시적) → Tier 2(자율 발견) |
| **로그 기록** | `.claude/auto-logs/`에 JSON Lines 형식 기록 |
| **Context 관리** | 90% 도달 시 체크포인트 → 세션 종료 |
| **체크포인트** | 80%에서 자동 저장, resume 지원 |

## 2계층 우선순위 체계

### Tier 1: 명시적 작업
1. 테스트 실패 → 즉시 수정
2. PR CI 실패 → 해당 브랜치로 이동
3. 커밋 안 된 변경 → `/commit`
4. PRD 필요 → 탐색/작성/검토
5. 열린 이슈 → `/issue fix #N`

### Tier 2: 자율 발견 (Tier 1 없을 때)
6. 코드 품질 → 린트 경고, 타입 오류 수정
7. 테스트 커버리지 → 미달 영역 보강
8. 문서화 → README, API 문서 개선
9. 리팩토링 → 중복 코드, 복잡도 개선
10. 의존성 → 보안 취약점, 버전 업데이트
11. 성능 → 느린 쿼리, 메모리 누수
12. 접근성 → a11y 개선

## 관련 파일

| 경로 | 용도 |
|------|------|
| `.claude/commands/work.md` | 통합 커맨드 (상세 문서) |
| `.claude/auto-logs/` | 세션 로그 저장소 |
| `.claude/skills/auto-workflow/` | 스킬 정의 및 스크립트 |
