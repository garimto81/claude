---
name: audit
description: Daily configuration audit, improvement suggestions, and trend-based workflow optimization
triggers:
  keywords:
    - "audit"
    - "trend"
    - "워크플로우 개선"
    - "브리핑 분석"
---

# /audit

이 스킬은 `.claude/commands/audit.md` 커맨드 파일의 내용을 실행합니다.

## 서브커맨드 라우팅

| 서브커맨드 | 동작 |
|-----------|------|
| (없음) | 전체 설정 점검 |
| `quick` | 빠른 점검 (버전/개수만) |
| `deep` | 심층 점검 (내용 분석 포함) |
| `fix` | 발견된 문제 자동 수정 |
| `baseline` | 현재 상태를 기준으로 저장 |
| `suggest [영역]` | 솔루션 추천 |
| `trend` | **Gmail 브리핑 기반 트렌드 분석 + 워크플로우 갭 분석 + 메일 삭제** |
| `trend --apply` | **트렌드 분석 + 자동 적용 + 커밋 + 메일 삭제 (완전 자동화)** |

## `trend` 서브커맨드 워크플로우

```
/audit trend 실행
    │
    ├─ [1/5] Gmail 인증 확인
    ├─ [2/5] 임시보관함 브리핑 메일 수집 (in:draft subject:Claude Code)
    ├─ [3/5] Analyst 에이전트로 트렌드 추출 + 현재 워크플로우 갭 분석
    ├─ [4/5] 개선 아이디어 제안 출력
    └─ [5/5] 사용자 확인 후 브리핑 메일 삭제
```

**핵심 규칙:**
- Gmail 인증 실패 시 즉시 중단
- 브리핑 메일 없으면 "메일 없음" 출력 후 종료
- 메일 삭제는 반드시 사용자 확인 후 (`--dry-run` 시 삭제 스킵)
- `--save` 시 `.claude/research/audit-trend-<date>.md` 저장
- `--apply` 시 Step 4.5(자동 적용 + 커밋) 추가 실행

## 커맨드 파일 참조

상세 워크플로우: `.claude/commands/audit.md`
