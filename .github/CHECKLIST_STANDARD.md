# Checklist 표준 가이드

이 문서는 garimto81 Organization의 모든 레포에 적용되는 **Checklist 작성 표준**입니다.

## 목적

- PR 머지 시 Slack List와 자동 연동
- 모든 레포에서 일관된 진행률 추적
- 영구 문서 기반 프로젝트 관리

---

## 1. 파일 위치 (필수 - Slack List 연동 조건)

⚠️ **Slack List 연동을 위해서는 반드시 아래 경로 중 하나에 Checklist 문서가 있어야 합니다.**

| 순위 | 경로 | 설명 |
|:----:|------|------|
| 1 | `docs/checklists/PRD-NNNN.md` | **필수** - 전용 Checklist 폴더 |
| 2 | `tasks/prds/NNNN-prd-*.md` | PRD 문서 내 Checklist 섹션 |
| 3 | `docs/PRD-NNNN-*.md` | docs 폴더 내 PRD |
| 4 | `docs/CHECKLIST.md` | 프로젝트 전체 Checklist |

❌ **문서 미작성 시**: PR 본문 Checklist로 Fallback (임시 데이터, **누적 진행률 추적 불가**)

---

## 2. 문서 구조

### 2.1 메타데이터 (필수)

```markdown
# [PRD-0001] Checklist

**PRD**: PRD-0001
**Version**: 1.0.0
**Last Updated**: 2025-12-22
**Status**: In Progress | Completed | On Hold
```

### 2.2 요약 테이블 (선택)

```markdown
## Summary

| Metric | Value |
|--------|-------|
| Total Items | 25 |
| Completed | 15 |
| Progress | 60% |
| Current Phase | Phase 2 |
```

---

## 3. Checklist 형식

### 3.1 리스트 형식 (기본)

```markdown
## Phase 1: 기능 구현

- [x] API 구현 (#101)
- [x] 테스트 작성 (#102)
- [ ] 문서화 (#103)
- [ ] 코드 리뷰
```

**규칙**:
- `- [x]`: 완료된 항목
- `- [ ]`: 미완료 항목
- `(#NNN)`: 연결된 PR 번호 (자동 체크용)

### 3.2 테이블 형식 (상세 추적용)

```markdown
## Phase 1: 기능 구현

| Status | Item | PR | Notes |
|:------:|------|:--:|-------|
| [x] | API 구현 | #101 | 완료 |
| [x] | 테스트 작성 | #102 | 완료 |
| [ ] | 문서화 | #103 | 진행중 |
| [ ] | 코드 리뷰 | - | 대기 |
```

---

## 4. PR-Checklist 연결

### 4.1 PR 제목에 PRD ID 포함 (권장)

```
feat: add login API [PRD-0001] #123
```

### 4.2 브랜치명에 PRD ID 포함

```
feat/PRD-0001-123-add-login
```

### 4.3 PR 본문에 Checklist 문서 참조

```markdown
## Related Documents

- Checklist: `docs/checklists/PRD-0001.md`
- PRD: `tasks/prds/0001-prd-sso.md`
```

---

## 5. 자동 체크 기능

### 5.1 동작 방식

```
PR #101 머지 → Checklist 문서에서 "(#101)" 포함 항목 검색
→ `- [ ] API 구현 (#101)` → `- [x] API 구현 (#101)`
→ 변경된 파일 커밋 (GitHub Actions bot)
→ 진행률 재계산 → Slack List 업데이트
```

### 5.2 항목 작성 규칙

```markdown
- [ ] 기능 구현 (#101)     ← PR #101 머지 시 자동 체크
- [ ] 테스트 작성 (#102)   ← PR #102 머지 시 자동 체크
- [ ] 문서화              ← 수동 체크 필요 (PR 번호 없음)
```

---

## 6. Slack List 연동

### 6.1 진행률 필드

```
████░░░░░░ 60% (3/5)
```

### 6.2 비고 필드

```
🔄 진행중:
• 문서화 (#103)
• 코드 리뷰
```

---

## 7. 예제 템플릿

### 7.1 신규 Checklist 생성

```markdown
# [PRD-NNNN] Checklist

**PRD**: PRD-NNNN
**Version**: 1.0.0
**Last Updated**: YYYY-MM-DD
**Status**: In Progress

---

## Phase 1: 설계

- [ ] 요구사항 분석
- [ ] 아키텍처 설계
- [ ] API 설계

## Phase 2: 구현

- [ ] 핵심 기능 구현
- [ ] 테스트 작성
- [ ] 통합 테스트

## Phase 3: 검증

- [ ] 코드 리뷰
- [ ] 문서화
- [ ] 배포 준비

---

## Changelog

| Date | PR | Changes |
|------|-----|---------|
| YYYY-MM-DD | - | 초기 작성 |
```

---

## 8. 레포별 적용

### 8.1 Reusable Workflow 사용

각 레포의 `.github/workflows/slack-list-sync.yml`:

```yaml
name: Slack List Sync

on:
  pull_request:
    types: [closed]

jobs:
  sync:
    if: github.event.pull_request.merged == true
    uses: garimto81/.github/.github/workflows/slack-list-sync-reusable.yml@main
    with:
      checklist_paths: 'docs/checklists,tasks/prds'
    secrets:
      SLACK_USER_TOKEN: ${{ secrets.SLACK_USER_TOKEN }}
      SLACK_LIST_ID: ${{ secrets.SLACK_LIST_ID }}
```

---

## 9. 참고

- [slakc_list 프로젝트](../slakc_list/README.md)
- [PRD 가이드](./docs/guides/PRD_GUIDE_STANDARD.md)
