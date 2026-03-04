---
name: prd-sync
description: >
  This skill should be used when the user needs to synchronize PRD documents between Google Docs and local repository.
triggers:
  keywords:
    - "prd-sync"
---

# /prd-sync

이 스킬은 `.claude/commands/prd-sync.md` 커맨드 파일의 내용을 실행합니다.

## 커맨드 파일 참조

상세 워크플로우: `.claude/commands/prd-sync.md`

## /auto 통합 동작

`/auto --gdocs` 실행 시 아래 워크플로우가 적용된다.

### Step 2.0: /auto에서 호출 시

```
Lead가 /auto Step 2.0에서 --gdocs 옵션 감지 시:
1. prd-syncer teammate (executor, opus) 생성
2. .claude/commands/prd-sync.md 워크플로우 실행
3. Google Docs PRD → docs/00-prd/ 로컬 동기화
4. 동기화된 PRD를 Phase 1 계획에 반영
```

### 필수 조건

- google-workspace 스킬의 OAuth 2.0 인증 완료 상태
- 인증 실패 시: 에러 출력 후 중단 (조용한 스킵 금지)
