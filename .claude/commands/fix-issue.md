---
name: fix-issue
description: Analyze and fix GitHub issues using structured approach
---

# /fix-issue - GitHub Issue Resolver (해결 전용)

GitHub 이슈를 **해결**하는 구조화된 워크플로우.

> **역할 구분**:
> - `/fix-issue` - 이슈 **해결** (브랜치 생성 → 구현 → PR)
> - `/issues` - 이슈 **조회** (목록 + 상태)
> - `/issue` - 솔루션 **리서치** (검색 + 비교)

## Usage

```
/fix-issue <issue-number>
```

## Workflow

1. **Fetch Issue**
   ```bash
   gh issue view <issue-number>
   ```
   - Read issue description
   - Extract requirements
   - Check labels and milestone

2. **Analyze Context**
   - Review related code
   - Check similar issues
   - Identify root cause

3. **Create Branch**
   ```bash
   git checkout -b fix/issue-<number>-<description>
   ```

4. **Implement Fix**
   - Follow Phase 0-6 workflow
   - Write tests (Phase 2)
   - Update docs if needed

5. **Create PR**
   - Reference issue: `Fixes #<number>`
   - Auto-link with GitHub

## Phase Integration

### Phase 0: Requirements
- Issue description = PRD
- Labels → Priority
- Milestone → Version

### Phase 1: Implementation
- Fix the issue
- Add tests

### Phase 2: Testing
- Verify fix works
- Check edge cases

### Phase 4: PR
- Auto-reference issue
- Close on merge

## Example

```bash
/fix-issue 123

# Claude Code:
# 1. Fetching issue #123...
#    Title: "Login timeout on slow connections"
#    Labels: bug, high-priority
#
# 2. Analysis:
#    - Root cause: No timeout configuration
#    - Affected file: src/auth.ts
#
# 3. Creating branch: fix/issue-123-login-timeout
#
# 4. Implementing fix...
#    - Added timeout config
#    - Updated tests
#
# 5. Ready to commit:
#    git commit -m "fix: Add login timeout configuration
#
#    Fixes #123"
```

## Integration with Scripts

Works with existing `github-issue-dev.sh`:
```bash
# Old way
bash scripts/github-issue-dev.sh 123

# New way
/fix-issue 123
```

Both create feature branch and draft PR.

## 연동 에이전트

| 단계 | 에이전트 | 역할 |
|------|----------|------|
| 원인 분석 | `debugger` | 근본 원인 파악 |
| 코드 수정 | `code-reviewer` | 코드 품질 확인 |
| 테스트 | `test-automator` | 테스트 작성 |

## Related

- `/create-pr` - Create PR after fix
- `/pre-work` - 사전 조사 (솔루션 검색)
- `scripts/github-issue-dev.ps1`
