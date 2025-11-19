# Phase 0.5: Task List Generation

**Duration**: 5-30 minutes
**Input**: PRD from Phase 0
**Output**: `tasks/NNNN-tasks-feature-name.md`

---

## Overview

Phase 0.5 bridges requirements (PRD) and implementation. A well-structured task list ensures nothing is forgotten and enables accurate time estimation.

**Key Innovation**: **1:1 Test Pairing** - Every implementation file gets a corresponding test file in the same task.

---

## Methods

### Method 1: Conversation with Claude Code (Recommended ⭐)

**Why this is best**:
- ✅ No API keys or setup needed
- ✅ Free (already in conversation)
- ✅ Interactive refinement
- ✅ 96% time savings (8 hours → 5 minutes)

**Process**:
```
User: "tasks/prds/0001-prd-auth.md 읽고 Task List 작성해줘"

Claude Code:
1. Reads PRD
2. Generates Parent Tasks (5-12 high-level phases)
3. Shows for approval → User: "Go"
4. Generates Sub-Tasks with 1:1 test pairing
5. Saves to tasks/0001-tasks-auth.md
```

**Two-Phase Generation** (automatic):
1. **Parent Tasks**: High-level phases (Research, Implementation, Testing, Deployment)
2. **Sub-Tasks**: Detailed steps with mandatory test pairs

---

### Method 2: Python Script (Optional - API Required)

**When to use**: Fully automated workflow, batch processing

```bash
# Setup (one-time)
export ANTHROPIC_API_KEY=your_key
pip install anthropic

# Generate
python scripts/generate_tasks_ai.py tasks/prds/0001-prd-auth.md
```

**Drawbacks**:
- Costs API credits
- Requires setup
- Less interactive

---

## Task List Structure

### Required Task 0.0: Setup
```markdown
## Task 0.0: Setup
- [ ] Create feature branch: `feature/PRD-0001-auth`
- [ ] Update CLAUDE.md with project context (if needed)
```

### Parent Tasks (5-12)
```markdown
## Task 1.0: Phase 1 - Authentication Core
[High-level description]

## Task 2.0: Phase 2 - Testing & Validation
[High-level description]

## Task 3.0: Phase 3 - Integration
[High-level description]
```

### Sub-Tasks with 1:1 Test Pairing

**Critical Rule**: Every implementation file → corresponding test file

```markdown
## Task 1.0: Phase 1 - Authentication Core

### Task 1.1: Create authentication module
- [ ] Create `src/auth/oauth.py` (implementation)
- [ ] Create `tests/auth/test_oauth.py` (1:1 paired test)
- **Duration**: 2 hours
- **Acceptance**: OAuth2 flow working, 80%+ coverage

### Task 1.2: Implement session management
- [ ] Create `src/auth/session.py`
- [ ] Create `tests/auth/test_session.py` (1:1 paired test)
- **Duration**: 1.5 hours
- **Acceptance**: Sessions persist, expire correctly
```

### Checkbox Format
```markdown
- [ ] Pending
- [x] Done
- [!] Failed (needs retry)
- [⏸] Blocked (waiting on dependency)
```

---

## Task Generation Rules

When Claude Code generates tasks (automatic):

### 1. Mandatory 1:1 Test Pairing
```
src/auth.py → tests/test_auth.py
src/components/Button.tsx → tests/components/Button.test.tsx
```

**No orphaned implementation files allowed.**

### 2. Include Duration Estimates
```markdown
- **Duration**: 2 hours
- **Duration**: 30 minutes
- **Duration**: 1 day
```

### 3. Clear Acceptance Criteria
```markdown
- **Acceptance**:
  - OAuth flow completes successfully
  - 80%+ test coverage
  - No security vulnerabilities
  - Response time < 500ms
```

### 4. Dependency Tracking
```markdown
### Task 2.3: Deploy to staging
- **Depends on**: Task 2.1 (tests pass), Task 2.2 (security audit)
```

### 5. File Naming
```
tasks/NNNN-tasks-feature-name.md
```
Same NNNN as PRD.

---

## Example Task List

```markdown
# Task List: OAuth Authentication (PRD-0001)

**Total Estimated Time**: 16 hours
**Target Completion**: 2025-01-25

---

## Task 0.0: Setup
- [ ] Create branch: `feature/PRD-0001-oauth`
- [ ] Update CLAUDE.md with OAuth context

---

## Task 1.0: Phase 1 - Implementation (8 hours)

### Task 1.1: OAuth Provider Setup
- [ ] Create `src/auth/providers/google.py`
- [ ] Create `tests/auth/providers/test_google.py`
- **Duration**: 2 hours
- **Acceptance**: Google OAuth working locally

### Task 1.2: Session Management
- [ ] Create `src/auth/session.py`
- [ ] Create `tests/auth/test_session.py`
- **Duration**: 1.5 hours
- **Acceptance**: Sessions persist in Redis

### Task 1.3: User Profile API
- [ ] Create `src/api/user_profile.py`
- [ ] Create `tests/api/test_user_profile.py`
- **Duration**: 2 hours
- **Acceptance**: GET/PUT /api/user endpoint works

---

## Task 2.0: Phase 2 - Testing (4 hours)

### Task 2.1: Unit Tests
- [ ] Ensure 80%+ coverage on auth module
- [ ] Add edge case tests (expired tokens, etc.)
- **Duration**: 2 hours
- **Acceptance**: `pytest tests/ --cov=src` shows 80%+

### Task 2.2: E2E Tests
- [ ] Create `tests/e2e/test_login_flow.py` (Playwright)
- **Duration**: 2 hours
- **Acceptance**: Full login flow works in browser

---

## Task 3.0: Phase 3 - Documentation (2 hours)

### Task 3.1: API Documentation
- [ ] Update OpenAPI spec with new endpoints
- **Duration**: 1 hour

### Task 3.2: User Guide
- [ ] Write "How to Set Up OAuth" guide
- **Duration**: 1 hour

---

## Task 4.0: Phase 4 - Deployment (2 hours)

### Task 4.1: Environment Variables
- [ ] Add `.env.example` with OAuth keys
- [ ] Update deployment docs
- **Duration**: 30 minutes

### Task 4.2: Deploy to Staging
- [ ] Deploy and smoke test
- **Depends on**: Task 2.1, 2.2
- **Duration**: 1.5 hours
```

---

## Validation

**Before Phase 1, run:**
```bash
bash scripts/validate-phase-0.5.sh NNNN
```

**Checks**:
- ✅ Task list file exists
- ✅ Task 0.0 completed (branch created)
- ✅ Checkboxes properly formatted
- ✅ Duration estimates present
- ✅ 1:1 test pairing for implementation tasks

---

## Progress Tracking

### During Development
```bash
# Quick status check
bash scripts/phase-status.sh 0001

# Or manually
grep -oP '\[.\]' tasks/0001-tasks-auth.md | sort | uniq -c
```

**Output**:
```
15 [ ]  # Pending
8  [x]  # Done
2  [!]  # Failed
1  [⏸]  # Blocked
```

### GitHub Integration (Optional)
```bash
# Migrate to GitHub Issue
python scripts/migrate_prds_to_issues.py tasks/prds/0001-prd-auth.md

# Track via issue tasklist
gh issue view 123
```

---

## Tips

1. **Break Down Large Tasks**: If >4 hours, split into smaller sub-tasks
2. **Front-Load Risks**: Tackle uncertain/hard tasks first
3. **Add Buffer**: Estimates often underestimate; add 20-30% buffer
4. **Update as You Go**: Check boxes, add notes, adjust estimates
5. **Review Dependencies**: Ensure tasks are ordered correctly

---

## Common Patterns

### Backend API
```markdown
- [ ] Create model: `src/models/User.py`
- [ ] Create API: `src/api/users.py`
- [ ] Create tests: `tests/api/test_users.py` (1:1)
- [ ] Update OpenAPI spec
```

### Frontend Component
```markdown
- [ ] Create component: `src/components/LoginForm.tsx`
- [ ] Create tests: `tests/components/LoginForm.test.tsx` (1:1)
- [ ] Add Storybook story
- [ ] Update design system docs
```

### Database Migration
```markdown
- [ ] Write migration: `migrations/001_add_oauth_table.sql`
- [ ] Test migration locally
- [ ] Update schema docs
- [ ] Plan rollback procedure
```

---

## Next Steps

After validation passes:
1. **Phase 1**: Start implementation (Task 1.0)
2. **Daily Updates**: Mark completed tasks
3. **Blockers**: Flag and resolve ASAP
4. **Reviews**: Mini-reviews after each major task

---

**References**:
- [Phase 0: PRD](00-prd.md)
- [Phase 1: Implementation](02-implementation.md)
- [Quick Commands](../QUICK_COMMANDS.md)
