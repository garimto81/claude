---
name: issues
description: List and check status of GitHub issues
---

# /issues - GitHub Issue List & Status (조회 전용)

GitHub 이슈 목록 **조회** 및 상태 확인.

> **역할 구분**:
> - `/issues` - 이슈 **조회/상태 확인** (Read)
> - `/fix-issue` - 이슈 **해결** (브랜치 생성 → 구현 → PR)
> - `/issue` - 이슈 **솔루션 리서치** (Multi-Agent 병렬 검색)

## Usage

```
/issues [filter]
```

## Filters

| Filter | 설명 | 예시 |
| :--- | :--- | :--- |
| (없음) | 열린 이슈 전체 | `/issues` |
| `mine` | 내게 할당된 이슈 | `/issues mine` |
| `open` | 열린 이슈 | `/issues open` |
| `closed` | 닫힌 이슈 | `/issues closed` |
| `all` | 전체 이슈 | `/issues all` |
| `<number>` | 특정 이슈 상세 | `/issues 123` |
| `label:<name>` | 라벨별 필터 | `/issues label:bug` |

## Commands

### 1. 이슈 목록 조회

```bash
# 열린 이슈 (기본)
gh issue list

# 내게 할당된 이슈
gh issue list --assignee @me

# 라벨별 조회
gh issue list --label bug
gh issue list --label "high-priority"

# 상태별 조회
gh issue list --state closed --limit 10
gh issue list --state all
```

### 2. 이슈 상세 조회

```bash
# 이슈 상세 보기
gh issue view <number>

# 코멘트 포함
gh issue view <number> --comments
```

### 3. 이슈 상태 변경

```bash
# 이슈 닫기
gh issue close <number>

# 이슈 재오픈
gh issue reopen <number>

# 라벨 추가
gh issue edit <number> --add-label "in-progress"

# 담당자 할당
gh issue edit <number> --add-assignee @me
```

## Output Format

```
📋 Open Issues (5)

#123 [bug] Login timeout on slow connections
     Labels: bug, high-priority
     Assignee: @user
     Created: 2025-01-15

#124 [feature] Add OAuth2 support
     Labels: enhancement, auth
     Assignee: -
     Created: 2025-01-16

#125 [docs] Update API documentation
     Labels: documentation
     Assignee: @user
     Created: 2025-01-17
```

## Phase Integration

| Phase | 이슈 활용 |
| :--- | :--- |
| **0** | 이슈 → PRD 생성 |
| **1** | 이슈 브랜치 생성 (`fix/issue-123-*`) |
| **4** | PR에 이슈 연결 (`Fixes #123`) |

## Workflow Example

```bash
# 1. 이슈 목록 확인
/issues

# 2. 특정 이슈 상세 확인
/issues 123

# 3. 이슈 작업 시작
/fix-issue 123

# 4. PR 생성 (이슈 자동 연결)
/create-pr
```

## Quick Reference

```bash
gh issue list                      # 열린 이슈
gh issue list -a @me               # 내 이슈
gh issue list -l bug               # 버그 이슈
gh issue list -s closed -L 5       # 최근 닫힌 5개
gh issue view 123                  # 상세 보기
gh issue view 123 -c               # 코멘트 포함
```

## Related

- `/fix-issue` - 이슈 해결 워크플로우
- `/create-pr` - PR 생성 (이슈 연결)
- `scripts/github-issue-dev.ps1` - 이슈 개발 자동화
