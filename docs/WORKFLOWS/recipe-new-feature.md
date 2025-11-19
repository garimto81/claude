# Workflow Recipe: New Feature Development (Complete Phase 0-6)

**Time**: 30-60 minutes (simple feature)
**Difficulty**: Intermediate
**Phase**: Complete Phase 0-6 cycle
**Tools**: Claude Code, Git, pytest/npm test

---

## When to Use

- ✅ Starting new feature from scratch
- ✅ Feature requires planning and testing
- ✅ Need systematic development approach
- ✅ Want regression prevention and documentation
- ✅ Team collaboration required

**Real-world scenario**: "Add email notification feature when user password changes"

---

## Complete Workflow (30 min for simple feature)

### Phase 0: Requirements (5 min)

**What**: Create PRD with clear requirements

```bash
# 1. Create PRD file
vim tasks/prds/0001-prd-password-notification.md

# 2. Ask Claude to help structure PRD
Claude> "Help me write a MINIMAL PRD for email notification when user changes password.
Ask me clarifying questions using A/B/C/D format."

# Claude will ask 3-8 questions, then create PRD
```

**PRD Template** (MINIMAL):
```markdown
# PRD-0001: Password Change Email Notification

## What
Send email notification when user changes password

## Why
Security: User should know if their password was changed (detect unauthorized access)

## Must Have
- [ ] Detect password change event
- [ ] Send email with timestamp and IP address
- [ ] Email template with security message
- [ ] Handle email delivery failures

## Success Criteria
- Email sent within 10 seconds of password change
- 99% delivery rate
- Email contains: timestamp, IP, "not you?" link

## Out of Scope
- SMS notifications
- In-app notifications
- Password history tracking
```

**✅ Checkpoint**: PRD exists in `tasks/prds/0001-prd-*.md`

**Validation**:
```bash
python scripts/validate_phase_universal.py 0 0001
# ✅ PRD file exists
# ✅ Minimum 50 lines (or appropriate for MINIMAL)
```

---

### Phase 0.5: Task Generation (3 min)

**What**: Break PRD into executable tasks

```bash
Claude> "Read tasks/prds/0001-prd-password-notification.md
Generate Task List with:
1. Task 0.0 (Setup)
2. Parent tasks for each phase
3. Sub-tasks with 1:1 test pairing
Save to tasks/0001-tasks-password-notification.md"
```

**Generated Task List Example**:
```markdown
# Task List: Password Notification (PRD-0001)

## Task 0.0: Setup
- [x] Create feature branch: feature/PRD-0001-password-notification
- [ ] Update CLAUDE.md with project context

## Task 1.0: Phase 1 - Implementation
- [ ] Task 1.1: Create password change event listener
- [ ] Task 1.2: Create tests/test_password_listener.py (1:1 pair)
- [ ] Task 1.3: Create email notification service
- [ ] Task 1.4: Create tests/test_email_service.py (1:1 pair)
- [ ] Task 1.5: Create email template
- [ ] Task 1.6: Create tests/test_email_template.py (1:1 pair)

## Task 2.0: Phase 2 - Testing
- [ ] Task 2.1: Integration tests (80% coverage)
- [ ] Task 2.2: Test email delivery failure handling
- [ ] Task 2.3: Test performance (10s requirement)

... (more tasks)
```

**✅ Checkpoint**: Task List exists in `tasks/0001-tasks-*.md`

**Validation**:
```bash
python scripts/validate_phase_universal.py 0.5 0001
# ✅ Task List exists
# ✅ Task 0.0 has items
```

---

### Task 0.0: Branch Setup (1 min)

**What**: Create feature branch and prepare environment

```bash
# Create and switch to feature branch
git checkout -b feature/PRD-0001-password-notification

# Mark Task 0.0 as in progress
Claude> "Mark Task 0.0 as in progress in tasks/0001-tasks-*.md"

# Commit setup
git add tasks/
git commit -m "docs: Add PRD and tasks for password notification [PRD-0001]"
git push -u origin feature/PRD-0001-password-notification

# Mark Task 0.0 as complete
Claude> "Mark Task 0.0 as complete"
```

**✅ Checkpoint**: Feature branch created and pushed

---

### Phase 1: Implementation (12 min)

**What**: Write code WITH tests (1:1 pairing)

```bash
# Task 1.1 & 1.2: Listener + Test (together)
Claude> "Create src/auth/password_listener.py that:
1. Listens for password change events
2. Captures user_id, timestamp, IP address

AND create tests/test_password_listener.py with:
1. Test successful event capture
2. Test missing data handling"

# Task 1.3 & 1.4: Email service + Test (together)
Claude> "Create src/email/notification_service.py that:
1. Sends email using SMTP
2. Handles delivery failures with retry (3 attempts)
3. Logs all attempts

AND create tests/test_email_service.py with:
1. Test successful email send
2. Test retry logic on failure
3. Test logging"

# Task 1.5 & 1.6: Template + Test (together)
Claude> "Create templates/password_changed.html with:
- Security message
- Timestamp and IP display
- 'Not you?' support link

AND create tests/test_email_template.py to validate template rendering"
```

**✅ Checkpoint**: All implementation files have 1:1 test pairs

**Validation**:
```bash
python scripts/validate_phase_universal.py 1 0001
# ✅ All src files have test pairs
# ✅ No orphaned implementation files
```

---

### Phase 2: Testing (5 min)

**What**: Comprehensive test coverage

```bash
# Run all tests
pytest tests/ -v --cov=src --cov-report=term-missing

# Expected output:
# ✅ test_password_listener.py::test_capture_event PASSED
# ✅ test_email_service.py::test_send_email PASSED
# ✅ test_email_service.py::test_retry_logic PASSED
# ✅ test_email_template.py::test_render PASSED
#
# Coverage: 87% (target: 80%+)

# Fix any failures
Claude> "Fix failing tests in test_email_service.py"

# Re-run until all pass
pytest tests/ -v
```

**✅ Checkpoint**: All tests passing, 80%+ coverage

**Validation**:
```bash
python scripts/validate_phase_universal.py 2 0001
# ✅ All tests pass
# ✅ Coverage threshold met
```

---

### Phase 2.5: Code Review (3 min) - OPTIONAL

**What**: Professional review before versioning

```bash
# Option 1: Pragmatic Code Review (comprehensive)
/pragmatic-code-review

# Option 2: Security Review (if handling sensitive data)
/security-review

# Review checklist:
# - [ ] No hardcoded secrets
# - [ ] SQL injection prevented
# - [ ] XSS protection in email template
# - [ ] Rate limiting on email sends
# - [ ] Proper error handling
```

**✅ Checkpoint**: Code review passed, issues addressed

---

### Phase 3: Versioning (2 min)

**What**: Tag release with semantic version

```bash
# Determine version bump
# - MAJOR: Breaking changes (v2.0.0)
# - MINOR: New feature (v1.1.0) ← This case
# - PATCH: Bug fix (v1.0.1)

# Update CHANGELOG.md
vim CHANGELOG.md
```

**CHANGELOG Entry**:
```markdown
## [1.1.0] - 2025-01-19

### Added
- Email notification on password change [PRD-0001]
- Password change event listener
- SMTP email service with retry logic
- Security email template
```

**Create git tag**:
```bash
git tag -a v1.1.0 -m "Release 1.1.0: Password change notification"
```

**✅ Checkpoint**: CHANGELOG updated, tag created

**Validation**:
```bash
python scripts/validate_phase_universal.py 3 v1.1.0
# ✅ Tests pass
# ✅ CHANGELOG updated
# ✅ Tag format correct
```

---

### Phase 4: Git + Auto PR (2 min)

**What**: Commit, push, auto-create PR

```bash
# Commit all changes
git add .
git commit -m "feat: Add password change email notification (v1.1.0) [PRD-0001]

- Implement password change event listener
- Create email notification service with retry logic
- Add security email template
- 87% test coverage

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
git push origin feature/PRD-0001-password-notification

# Push tag
git push origin v1.1.0

# GitHub Actions will:
# 1. Detect pattern: (v1.1.0) [PRD-0001]
# 2. Create PR automatically
# 3. Run CI (pytest)
# 4. Auto-merge on pass (if configured)
```

**✅ Checkpoint**: PR created automatically, CI running

---

### Phase 5: E2E & Security (5 min)

**What**: Final validation before production

```bash
# 1. E2E Test (manual or automated)
Claude> "Create E2E test:
1. User logs in
2. Changes password
3. Check email inbox (use test email service)
4. Verify email received within 10 seconds
5. Verify email contains timestamp, IP, support link"

# 2. Security Audit
/security-review

# OR manual:
npm audit  # Node.js
pip-audit  # Python

# 3. Performance Test
Claude> "Test email send performance:
- Send 100 password change notifications
- All should complete within 10s each
- No memory leaks"
```

**✅ Checkpoint**: E2E passing, no security issues, performance OK

**Validation**:
```bash
python scripts/validate_phase_universal.py 5 0001
# ✅ E2E tests exist and pass
# ✅ No critical vulnerabilities
# ✅ Performance benchmarks met
```

---

### Phase 6: Deployment (3 min)

**What**: Deploy to production

```bash
# Pre-deployment checklist
- [x] .env.example has EMAIL_SMTP_HOST, EMAIL_FROM
- [x] Secrets in environment (not code)
- [x] Production build tested locally
- [x] Rollback plan documented

# Deploy (example: Docker)
docker build -t myapp:v1.1.0 .
docker push myregistry/myapp:v1.1.0

# OR use agent
Claude> "Deploy to production using our standard Kubernetes workflow"

# Post-deployment verification
curl https://api.myapp.com/health
# Expected: 200 OK

# Smoke test
Claude> "Create test user, change password, verify email sent"
```

**✅ Checkpoint**: Feature live in production, monitoring healthy

**Validation**:
```bash
python scripts/validate_phase_universal.py 6 0001
# ✅ .env.example exists
# ✅ No secrets in code
# ✅ Build succeeds
```

---

## Success Checklist

Complete feature development:
- [ ] Phase 0: PRD approved
- [ ] Phase 0.5: Task List created
- [ ] Task 0.0: Branch created
- [ ] Phase 1: Code + tests (1:1 pairing)
- [ ] Phase 2: All tests pass, 80%+ coverage
- [ ] Phase 2.5: Code review passed (optional)
- [ ] Phase 3: Version tagged, CHANGELOG updated
- [ ] Phase 4: PR created, CI passed
- [ ] Phase 5: E2E + security validated
- [ ] Phase 6: Deployed to production
- [ ] Feature working in production

---

## Time Breakdown (Simple Feature)

| Phase | Time | Tasks |
|-------|------|-------|
| Phase 0 | 5 min | Write MINIMAL PRD |
| Phase 0.5 | 3 min | Generate task list |
| Task 0.0 | 1 min | Create branch |
| Phase 1 | 12 min | Implement + tests (3 files × 4 min) |
| Phase 2 | 5 min | Run tests, fix failures |
| Phase 2.5 | 3 min | Code review (optional) |
| Phase 3 | 2 min | Version tag, CHANGELOG |
| Phase 4 | 2 min | Commit, push, auto-PR |
| Phase 5 | 5 min | E2E + security |
| Phase 6 | 3 min | Deploy |
| **Total** | **38 min** | (without Phase 2.5: 35 min) |

**Complex feature**: 60-120 min (more files, complex logic)

---

## Common Variations

### Variation 1: Frontend Feature (React)

```bash
# Phase 1: Component + Test
Claude> "Create src/components/PasswordChangeNotice.tsx
AND tests/PasswordChangeNotice.test.tsx"

# Phase 2: Run frontend tests
npm test
```

### Variation 2: API Endpoint

```bash
# Phase 1: Route + Controller + Test
Claude> "Create:
- src/routes/notifications.ts
- src/controllers/NotificationController.ts
- tests/NotificationController.test.ts"

# Phase 5: API E2E test
curl -X POST http://localhost:3000/api/notifications/test
```

### Variation 3: Database Migration

```bash
# Phase 1: Migration + Rollback
Claude> "Create database migration:
- migrations/001_add_notification_settings.sql
- migrations/001_rollback.sql"

# Phase 2: Test migration
npm run migrate:up
npm run migrate:down  # Rollback test
```

---

## Integration with Other Recipes

**Before this recipe**:
- If legacy codebase → Use [recipe-legacy-analysis.md](recipe-legacy-analysis.md) first
- If adding to existing feature → Review architecture diagrams

**During this recipe**:
- Run [recipe-daily-routine.md](recipe-daily-routine.md) in parallel
- If bug found → Use [recipe-debugging-tdd.md](recipe-debugging-tdd.md)

**After this recipe**:
- Daily: Update progress in daily-routine
- Weekly: Include in weekly review

---

## Related Commands

**Phase 0**:
- `/create-prd` - Interactive PRD generation

**Phase 1**:
- `/tdd` - Test-driven development guidance

**Phase 2**:
- (Run tests directly: `pytest` / `npm test`)

**Phase 2.5**:
- `/pragmatic-code-review` - Comprehensive code review
- `/design-review` - UI/UX review (if frontend)
- `/security-review` - Security audit

**Phase 3**:
- `/changelog` - Update CHANGELOG.md

**Phase 4**:
- `/commit` - Format commit message
- `/create-pr` - Manual PR creation (if auto-PR disabled)

**Phase 6**:
- (Use deployment-engineer agent for complex deploys)

---

## Tips & Best Practices

### Tip 1: Use Phases as Checkpoints, Not Barriers

Don't overthink phase transitions:
```bash
# ✅ Good: Iterate within Phase 1
Claude> "Fix bug in password_listener.py"
# Stay in Phase 1, don't go back to Phase 0

# ❌ Bad: Rigid phase progression
"We must complete ALL Phase 1 tasks before ANY Phase 2"
# You can write tests as you code (TDD)
```

### Tip 2: Combine Similar Tasks

```bash
# ✅ Efficient: Create file + test together
Claude> "Create service.py AND test_service.py"

# ❌ Slow: Create separately
Claude> "Create service.py"
[10 minutes later]
Claude> "Create test_service.py"  # Lost context
```

### Tip 3: Use MINIMAL PRD for Simple Features

**Simple feature** (< 5 files, < 1 day):
- Use MINIMAL PRD (1270 tokens)
- 3-5 clarifying questions
- 5 min PRD creation

**Complex feature** (> 10 files, > 3 days):
- Use STANDARD PRD (3500 tokens)
- 8-12 clarifying questions
- 20 min PRD creation

### Tip 4: Automate Repetitive Tasks

Create aliases:
```bash
# .bash_aliases or .zshrc
alias phase1="python scripts/validate_phase_universal.py 1"
alias phase2="pytest tests/ -v --cov=src"
alias phase3="vim CHANGELOG.md"
```

---

## Why This Works

**Phase 0-6 Benefits**:
1. **Phase 0**: Prevents scope creep, clear requirements
2. **Phase 0.5**: No forgotten tasks, clear progress tracking
3. **Phase 1**: 1:1 test pairing prevents "write tests later" (never happens)
4. **Phase 2**: Catch bugs early (10x cheaper than production)
5. **Phase 2.5**: Professional review prevents rework
6. **Phase 3**: Semantic versioning enables rollback
7. **Phase 4**: Auto-PR saves 10 min per feature
8. **Phase 5**: E2E + security = confidence before deploy
9. **Phase 6**: Systematic deployment prevents mistakes

**Time Comparison**:
- ❌ **Ad-hoc**: Code (30m) + "Oops, forgot tests" (20m) + Manual PR (10m) + Bugs in prod (2h debug) = 3h
- ✅ **Phase 0-6**: Structured workflow (35m) + Zero prod bugs = 35min (83% faster)

---

## Real Example: OAuth2 Integration

**Feature**: Add Google OAuth2 login

**Phase 0** (5 min):
```markdown
# PRD-0005: Google OAuth2 Login

## What
Users can log in with Google account

## Why
Reduce signup friction, increase conversion

## Must Have
- [ ] Google OAuth2 client setup
- [ ] Authorization flow (redirect to Google)
- [ ] Token exchange and user creation
- [ ] Link existing email accounts

## Success Criteria
- Login completes in <5 seconds
- 95% success rate
- Works on Chrome, Safari, Firefox
```

**Phase 0.5** (3 min): 12 tasks generated

**Phase 1** (20 min):
- `src/auth/oauth2_client.ts` + `tests/test_oauth2_client.ts`
- `src/auth/oauth2_controller.ts` + `tests/test_oauth2_controller.ts`
- `src/db/oauth_accounts.ts` + `tests/test_oauth_accounts.ts`

**Phase 2** (8 min): All tests pass, 89% coverage

**Phase 2.5** (5 min): Security review - found CSRF vulnerability, added state parameter

**Phase 3** (2 min): v1.3.0, CHANGELOG updated

**Phase 4** (2 min): Auto-PR created, CI passed

**Phase 5** (10 min): E2E test (login with real Google account), security audit passed

**Phase 6** (5 min): Deployed, monitoring healthy

**Total time**: 60 minutes
**Feature shipped**: ✅
**Bugs in production**: 0
**Security issues**: 0 (caught in Phase 2.5)

---

**Next Steps**:
- For bugs in this feature → Use [recipe-debugging-tdd.md](recipe-debugging-tdd.md)
- For daily tracking → Use [recipe-daily-routine.md](recipe-daily-routine.md)
- For analyzing dependencies → Use [recipe-legacy-analysis.md](recipe-legacy-analysis.md)
