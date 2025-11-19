# Workflow Recipe: Bug Fixing with TDD

**Time**: 15 minutes
**Difficulty**: Beginner
**Phase**: Ad-hoc (outside Phase 0-6)
**Tools**: Claude Code, pytest

---

## When to Use

- ✅ Production bug reported with error logs
- ✅ Unexpected behavior in existing feature
- ✅ Need to ensure bug doesn't regress
- ✅ Want to understand root cause before fixing

**Real-world scenario**: User reports "Login fails with 500 error when email has uppercase letters"

---

## Step-by-Step Workflow

### Step 1: Explore & Understand (3 min)

⚠️ **절대 바로 수정하지 말 것** - 파일 구조를 먼저 이해하세요

**What**: Gather context about the bug

```bash
# Add error logs to context
# (Paste error logs in conversation)

# Add relevant source files - DO NOT FIX YET!
Claude> "현재 발생하는 에러(로그 첨부)와 관련된 파일들을 찾아서 구조를 설명해줘.
Read src/auth/login.py and explain what might cause 500 error with uppercase emails"
```

**Expected outcome**: Understanding of code flow and potential root cause

❌ **Common Mistake**: Fixing code before understanding the bug
✅ **Correct**: Analyze first, fix later

---

### Step 2: Reproduce with Test (5 min) ⭐⭐⭐ **핵심 단계**

⚠️ **수정하지 말고, 테스트만 작성하세요!**

**What**: Write a failing test that reproduces the bug

```bash
# Create reproduction test - DO NOT FIX CODE YET!
Claude> "수정하지 말고, 이 버그가 발생함을 증명하는 실패하는 테스트 코드를 먼저 작성해.
Write a test in tests/reproduce_login_bug.py that:
1. Tests login with email 'User@Example.com' (uppercase)
2. Should succeed but currently fails with 500 error
3. Use pytest format
4. DO NOT modify src/auth/login.py yet!"

# Run the test (should FAIL)
pytest tests/reproduce_login_bug.py -v
```

**Expected output**:
```
FAILED tests/reproduce_login_bug.py::test_login_uppercase_email
AssertionError: Expected 200, got 500
```

**✅ Checkpoint**: Test fails as expected - bug is reproduced

---

### Step 3: Fix the Bug (5 min)

**What**: Modify code to make the test pass

```bash
# Ask Claude to fix
Claude> "Fix src/auth/login.py to handle uppercase emails. The test should pass."

# Run test again (should PASS)
pytest tests/reproduce_login_bug.py -v
```

**Expected output**:
```
PASSED tests/reproduce_login_bug.py::test_login_uppercase_email
```

**✅ Checkpoint**: Test passes - bug is fixed

---

### Step 4: Integrate & Prevent Regression (2 min)

❌ **절대 테스트 삭제 금지!** - 회귀 방지를 위해 영구 suite에 추가하세요

**What**: Move test to permanent test suite and commit

```bash
# ❌ WRONG - DO NOT DELETE TEST:
# rm tests/reproduce_login_bug.py  # 이렇게 하지 마세요!

# ✅ CORRECT - Move to permanent suite:
Claude> "테스트 코드는 삭제하지 말고, tests/test_auth.py로 이동해.
Move test_login_uppercase_email to tests/test_auth.py (merge or rename)"

# Run full test suite
pytest tests/test_auth.py -v

# Commit the fix WITH the test
git add src/auth/login.py tests/test_auth.py
git commit -m "fix: Handle uppercase emails in login (v1.0.1)

- Add test for uppercase email handling (regression prevention)
- Fix email normalization in login flow"
```

**✅ Checkpoint**: Bug fixed, regression prevented, change committed

---

## Why This Works

**TDD Approach Benefits**:
1. **Reproduce First**: Test proves bug exists before fixing
2. **Fix Verification**: Test passing proves fix works
3. **Regression Prevention**: Test stays in suite forever
4. **Clear Documentation**: Test shows expected behavior

**Time Comparison**:
- ❌ **Traditional**: Explore (10m) + Debug (20m) + Manual test (10m) + Hope it doesn't break again = 40min
- ✅ **TDD Recipe**: Explore (3m) + Reproduce (5m) + Fix (5m) + Integrate (2m) = 15min (63% faster)

**Anti-Pattern Warning** ⚠️:
```bash
# ❌ NEVER DO THIS - Deleting Test After Fix:
pytest reproduce_bug.py -v  # PASSED
rm reproduce_bug.py         # DELETE TEST ← 큰 실수!
git commit

# 결과:
# - 3개월 후 같은 버그 재발생 (리팩토링 중)
# - 테스트 없어서 감지 못함
# - Production 배포 → 고객 클레임
# - 2시간 디버깅 + 긴급 패치

# ✅ ALWAYS DO THIS - Keep Test in Suite:
mv reproduce_bug.py tests/test_bugfix_login.py  # 영구 보관
pytest tests/ -v  # 전체 suite 통과
git commit  # 테스트 포함 커밋

# 결과:
# - 3개월 후 같은 버그 시도 시 테스트 즉시 FAILED
# - 커밋 전 감지 → Production 배포 차단
# - 0분 디버깅 (회귀 방지)
```

---

## Common Variations

### Variation 1: Complex Bug (Multi-file)

If bug spans multiple files:
```bash
Step 1: Claude> "Read src/auth/login.py, src/db/users.py, and explain the flow"
Step 2: Write integration test instead of unit test
Step 3: Fix may require changes in multiple files
```

### Variation 2: Performance Bug

If bug is about performance:
```bash
Step 2: Add performance assertion
pytest.mark.timeout(2)  # Should complete in <2 seconds
```

### Variation 3: UI Bug (Playwright)

For frontend bugs:
```bash
Step 2: Write Playwright E2E test instead of pytest
npx playwright test reproduce_ui_bug.spec.ts
```

---

## Integration with Phase System

This recipe **doesn't fit** Phase 0-6 workflow because:
- Bugs are ad-hoc, not planned in PRD
- Need immediate fix, not full development cycle

**When to use Phase system instead**:
- If bug requires major refactoring → Create PRD-NNNN
- If bug reveals missing feature → Phase 0

**When to use this recipe**:
- Hotfix needed immediately
- Bug is localized (1-3 files)
- Clear reproduction steps exist

---

## Related Commands

**Slash commands that enhance this workflow**:
- `/tdd` - Extended TDD guidance
- `/check` - Code quality check after fix
- `/commit` - Format commit message

**Agents to use**:
- **debugger** - For complex root cause analysis
- **test-automator** - For writing comprehensive test cases
- **code-reviewer** - For reviewing fix before commit

---

## Success Checklist

Before completing this recipe:
- [ ] **Step 1**: File structure understood (no premature fixes)
- [ ] **Step 2**: Test reproduces bug (FAILED initially)
- [ ] **Step 2**: Confirmed no code changes made yet
- [ ] **Step 3**: Test passes after fix (PASSED)
- [ ] **Step 4**: All existing tests still pass
- [ ] **Step 4**: ❌ Test NOT deleted (moved to permanent suite)
- [ ] **Step 4**: ✅ Test committed WITH the fix
- [ ] **Step 4**: Commit message describes bug and fix

---

## Real Example

**Bug Report**: "API returns 500 when user's `created_at` field is null"

```bash
# Step 1: Explore (2min)
Claude> "Read src/api/users.py and explain how created_at is used"

# Step 2: Reproduce (4min)
Claude> "Write test in tests/reproduce_created_at_bug.py:
- Create user with created_at=null
- Call GET /api/users/{id}
- Should return 200 but currently 500"

pytest tests/reproduce_created_at_bug.py -v  # FAILED ✅

# Step 3: Fix (5min)
Claude> "Fix src/api/users.py to handle null created_at gracefully"

pytest tests/reproduce_created_at_bug.py -v  # PASSED ✅

# Step 4: Integrate (2min)
mv tests/reproduce_created_at_bug.py tests/test_users.py
pytest tests/ -v  # All pass
git commit -m "fix: Handle null created_at in user API (v1.0.2)"
```

**Total time**: 13 minutes
**Bug fixed**: ✅
**Regression prevented**: ✅
**Tests added**: 1

---

**Next Steps**:
- For new features → Use [recipe-new-feature.md](recipe-new-feature.md)
- For legacy code analysis → Use [recipe-legacy-analysis.md](recipe-legacy-analysis.md)
- For daily routines → Use [recipe-daily-routine.md](recipe-daily-routine.md)
