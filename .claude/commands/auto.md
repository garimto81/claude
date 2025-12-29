---
name: auto
description: 자율 판단 자동 완성 - Claude가 다음 작업을 스스로 판단하고 실행 (→ /work --loop alias)
alias_of: /work --loop
---

# /auto - 자율 판단 자동 완성

> **Note**: `/auto`는 `/work --loop`의 alias입니다. 동일한 기능을 수행합니다.

Claude가 **다음에 해야 할 작업을 스스로 판단**하고 **자동으로 실행**합니다.

## 사용법

```bash
# /auto 사용 (기존 방식 - 하위 호환)
/auto                    # 자율 판단 루프 시작
/auto resume [id]        # 세션 재개
/auto status             # 현재 상태 확인
/auto pause              # 일시 정지 (체크포인트 저장)
/auto abort              # 세션 취소
/auto --max 5            # 최대 5개 작업 후 중단
/auto --dry-run          # 판단만 보여주고 실행 안함

# /work --loop 사용 (권장 - 통합 인터페이스)
/work --loop             # 자율 판단 루프 시작
/work --loop resume      # 세션 재개
/work --loop status      # 현재 상태 확인
```

## 상세 문서

전체 기능 설명은 `/work` 커맨드의 `--loop` 모드 섹션을 참조하세요:

→ `.claude/commands/work.md` > `## --loop 모드 (자율 판단)`

---

## 핵심 기능 요약

| 기능 | 설명 |
|------|------|
| **로그 기록** | `.claude/auto-logs/`에 JSON Lines 형식 기록 |
| **로그 청킹** | 50KB 초과 시 자동 분할 |
| **Context 관리** | 90% 도달 시 자동 커밋 → 세션 종료 |
| **PRD 관리** | 탐색 → 작성 → 검토 → 승인 |
| **체크포인트** | 80%에서 자동 저장, resume 지원 |

## 실행 지시

`/auto` 또는 `/work --loop` 실행 시, `/work` 커맨드의 `--loop` 모드 실행 지시를 따릅니다.

**우선순위 기반 작업 판단:**
1. 테스트 실패 → 즉시 수정
2. PR CI 실패 → 해당 브랜치로 이동
3. 커밋 안 된 변경 → `/commit`
4. PRD 필요 → 탐색/작성/검토
5. 열린 이슈 → `/issue fix #N`
6. Todo 미완료 → 해당 작업
7. 모두 완료 → 루프 종료

## 관련 파일

| 경로 | 용도 |
|------|------|
| `.claude/commands/work.md` | 통합 커맨드 (상세 문서) |
| `.claude/auto-logs/` | 세션 로그 저장소 |
| `.claude/skills/auto-workflow/` | 스킬 정의 및 스크립트 |
