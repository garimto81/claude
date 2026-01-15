---
name: delegate
description: "[DEPRECATED] /auto로 통합됨 - 서브에이전트 위임"
alias_of: /auto
version: 2.0.0
deprecated: true
---

# /delegate - 서브에이전트 위임 (Deprecated)

> **이 커맨드는 `/auto`로 통합되었습니다.**

## 마이그레이션 안내

| 기존 | 새로운 |
|------|--------|
| `/delegate "작업"` | `/auto "작업"` |
| `/delegate --agent debugger "에러"` | `/auto "에러 디버깅"` |
| `/delegate --parallel "작업"` | `/auto "작업"` |

## 새로운 /auto 사용법

```bash
/auto                    # 자동 작업 시작
/auto "지시 내용"         # 특정 방향으로 작업
/auto status             # 진행 상황 확인
/auto redirect "새 방향"  # 방향 수정
/auto stop               # 종료 + 최종 보고서
```

## /auto 장점

- **무한 반복**: 작업이 끝나면 자동으로 다음 작업 발견
- **세션 관리**: 진행 상황 저장, 언제든 확인 가능
- **서브에이전트 위임**: Task tool로 자동 위임
- **에이전트 자동 선택**: 키워드 기반 최적 에이전트 선택

---

## 자동 리다이렉트

**이 커맨드 실행 시 `/auto`로 자동 리다이렉트됩니다.**

$ARGUMENTS가 있으면: `/auto "$ARGUMENTS"` 실행
$ARGUMENTS가 없으면: `/auto` 실행

---

**`/auto`를 사용하세요.**
