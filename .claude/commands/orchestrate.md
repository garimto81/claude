---
name: orchestrate
description: "[DEPRECATED] /auto로 통합됨 - 메인-서브 에이전트 오케스트레이션"
alias_of: /auto
version: 2.0.0
deprecated: true
---

# /orchestrate - 메인-서브 오케스트레이션 (Deprecated)

> **이 커맨드는 `/auto`로 통합되었습니다.**

## 마이그레이션 안내

| 기존 | 새로운 |
|------|--------|
| `/orchestrate "로그인 기능 만들어줘"` | `/auto "로그인 기능 만들어줘"` |
| `/orchestrate --parallel "작업"` | `/auto "작업"` |
| `/orchestrate --sequential "작업"` | `/auto "작업"` |

## 새로운 /auto 사용법

```bash
/auto                    # 자동 작업 시작
/auto "지시 내용"         # 특정 방향으로 작업
/auto status             # 진행 상황 확인
/auto redirect "새 방향"  # 방향 수정
/auto stop               # 종료 + 최종 보고서
```

## /auto가 orchestrate보다 좋은 점

| 항목 | /orchestrate | /auto |
|------|-------------|-------|
| YAML 관리 | 수동 | 자동 (session.yaml) |
| 작업 발견 | 사용자 지시만 | 5계층 자동 발견 |
| 반복 실행 | 1회 | 무한 (자율 발견) |
| 상태 확인 | 파일 직접 확인 | `/auto status` |
| 방향 수정 | 새로 시작 | `/auto redirect` |

## /auto 세션 관리

```
.claude/auto/
├── session.yaml          # 현재 세션 상태
└── history/              # 완료된 세션 아카이브
```

---

## 자동 리다이렉트

**이 커맨드 실행 시 `/auto`로 자동 리다이렉트됩니다.**

$ARGUMENTS가 있으면: `/auto "$ARGUMENTS"` 실행
$ARGUMENTS가 없으면: `/auto` 실행

---

**`/auto`를 사용하세요.**
