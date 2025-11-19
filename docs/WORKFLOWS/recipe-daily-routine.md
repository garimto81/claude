# Workflow Recipe: Daily Development Routine

**Time**: 5 minutes per day
**Difficulty**: Beginner
**Phase**: Parallel (runs alongside Phase 0-6)
**Tools**: Claude Code, Terminal

---

## When to Use

- ✅ Daily standup/check-in ritual
- ✅ Track progress across multiple tasks
- ✅ Maintain context between coding sessions
- ✅ Prevent context-switching overhead
- ✅ Generate daily retrospectives

**Real-world scenario**: "Working on 3 PRDs simultaneously, need to stay organized and track progress"

---

## Daily Workflow Cycle

### Morning: Start Session (2 min)

**What**: Load context and prioritize today's work

```bash
# 1. Check yesterday's progress
cat .claude/daily-log.md

# 2. Ask Claude for daily briefing
Claude> "Review tasks/0001-tasks-*.md and tasks/0002-tasks-*.md
Show me:
1. What I completed yesterday
2. What's in progress
3. What I should prioritize today"
```

**Expected output**:
```markdown
## Daily Briefing - 2025-01-19

### ✅ Completed Yesterday (2025-01-18)
- [x] Task 1.2: Create auth API endpoints (PRD-0001)
- [x] Task 2.1: Unit tests for auth (PRD-0001)

### 🔄 In Progress
- [ ] Task 1.3: Implement OAuth2 flow (PRD-0001)
- [ ] Task 0.5: Research payment APIs (PRD-0002)

### 🎯 Recommended Priority
1. **High**: Task 1.3 (blocking Phase 2 for PRD-0001)
2. **Medium**: Task 0.5 (research for PRD-0002)
3. **Low**: Documentation updates
```

**✅ Checkpoint**: Clear priorities for the day

---

### During Work: Track Progress (30 sec per task)

**What**: Update task status in real-time

```bash
# After completing a task
Claude> "Mark Task 1.3 as complete in tasks/0001-tasks-auth.md"

# When starting new task
Claude> "Mark Task 2.2 as in progress in tasks/0001-tasks-auth.md"

# When blocked
Claude> "Mark Task 3.1 as blocked in tasks/0001-tasks-auth.md
Add note: 'Waiting for API key from DevOps team'"
```

**Task Status Symbols**:
- `[ ]` = Pending
- `[x]` = Complete
- `[!]` = Failed/Blocked
- `[⏸]` = Paused

---

### Evening: Retrospective (3 min)

**What**: Generate daily summary and plan next day

```bash
Claude> "Create daily retrospective in .claude/daily-log.md:
1. What I accomplished today
2. What I learned
3. Blockers encountered
4. Plan for tomorrow

Based on changes to tasks/*.md files."
```

**Expected output**:
```markdown
# Daily Log - 2025-01-19

## Accomplishments
- ✅ Completed OAuth2 integration (Task 1.3, PRD-0001)
- ✅ Fixed token refresh bug (Task 1.4, PRD-0001)
- ✅ Wrote 8 unit tests for auth flow

## Learnings
- OAuth2 state parameter prevents CSRF attacks
- Redis TTL handles token expiration automatically
- Jest mock functions need `.mockClear()` between tests

## Blockers
- ⚠️ Task 3.1 blocked: Waiting for Stripe API key
- 💡 Workaround: Using Stripe test mode for now

## Tomorrow's Plan
1. Phase 2: Complete all auth tests (PRD-0001)
2. Phase 3: Version tag v1.2.0
3. Start Phase 0 for payment system (PRD-0002)

## Metrics
- Tasks completed: 3
- Time spent: 4.5 hours
- PRDs in progress: 2 (PRD-0001, PRD-0002)
```

**✅ Checkpoint**: Context preserved for tomorrow

---

## Weekly Review (Fridays, 10 min)

**What**: Analyze trends and optimize workflow

```bash
Claude> "Analyze .claude/daily-log.md for this week (Jan 15-19):
1. Total tasks completed
2. Average time per Phase
3. Common blockers
4. Productivity trends
5. Suggestions for next week"
```

**Expected output**:
```markdown
# Weekly Review - Week of Jan 15-19, 2025

## Metrics
- Total tasks: 17 completed / 23 planned (74%)
- PRDs completed: 1 (PRD-0001: Auth System)
- PRDs in progress: 2 (PRD-0002, PRD-0003)
- Avg time per task: 1.2 hours

## Phase Breakdown
- Phase 0 (Planning): 3 hours (15%)
- Phase 1 (Implementation): 10 hours (50%)
- Phase 2 (Testing): 5 hours (25%)
- Phase 3-6: 2 hours (10%)

## Bottlenecks
1. Phase 2 tests taking longer than expected (5h vs 3h planned)
2. Blocked 2x waiting for external API keys
3. Context-switching between PRD-0002 and PRD-0003

## Wins
- ✅ Shipped PRD-0001 on schedule
- ✅ Zero bugs in production
- ✅ 85% test coverage

## Next Week Optimizations
- Batch similar tasks (all Phase 2 tests together)
- Request API keys earlier in Phase 0
- Focus on one PRD at a time (finish PRD-0002 before starting PRD-0003)
```

---

## Integration with Phase System

This recipe runs **parallel** to Phase 0-6:

```
┌─────────────────────────────────────────┐
│  Phase 0-6 (Project Structure)          │
│  PRD → Tasks → Code → Test → Deploy    │
└─────────────────────────────────────────┘
         ↕ (tracked by)
┌─────────────────────────────────────────┐
│  Daily Routine (Progress Tracking)      │
│  Morning → Work → Evening               │
└─────────────────────────────────────────┘
```

**How they work together**:
- **Phase system**: What to build (structure)
- **Daily routine**: Progress tracking (momentum)

---

## Related Commands

**Slash commands**:
- `/todo` - Manage project todos with priorities
- `/commit` - Format commit with PRD reference

**Proposed new commands**:
- `/daily-standup` - Generate morning briefing
- `/daily-retro` - Create evening retrospective
- `/weekly-review` - Analyze week's progress

---

## Success Checklist

Daily routine complete when:
- [ ] Morning briefing reviewed
- [ ] Priorities clear for the day
- [ ] Task statuses updated in real-time
- [ ] Evening retrospective written
- [ ] Tomorrow's plan documented
- [ ] `.claude/daily-log.md` updated

---

## Real Example: Multi-Project Developer

**Scenario**: Working on 3 projects (Auth System, Payment API, Admin Dashboard)

### Monday Morning (9:00 AM)

```bash
Claude> "Daily briefing for PRD-0001, PRD-0002, PRD-0003"

Output:
┌─────────────────────────────────────────┐
│ PRD-0001 (Auth System)                   │
│ Status: Phase 2 (Testing)                │
│ Progress: 12/15 tasks (80%)              │
│ Priority: HIGH (ship this week)          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ PRD-0002 (Payment API)                   │
│ Status: Phase 0 (Planning)               │
│ Progress: 2/8 tasks (25%)                │
│ Priority: MEDIUM (research phase)        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ PRD-0003 (Admin Dashboard)               │
│ Status: Backlog                          │
│ Progress: 0/20 tasks (0%)                │
│ Priority: LOW (start next week)          │
└─────────────────────────────────────────┘

**Recommendation**: Focus on PRD-0001 today (finish Phase 2)
```

### During Day

```bash
11:30 AM - Completed Task 2.3
Claude> "Mark Task 2.3 complete in tasks/0001-tasks-auth.md"

2:00 PM - Started Task 2.4
Claude> "Mark Task 2.4 in progress"

4:00 PM - Blocked on API key
Claude> "Mark Task 3.1 blocked: 'Waiting for AWS SES API key from DevOps'"
```

### Evening (6:00 PM)

```bash
Claude> "Daily retrospective"

Output:
## Daily Log - Monday, Jan 15, 2025

### Today's Accomplishments
- ✅ Completed Phase 2 testing for auth (PRD-0001)
- ✅ All 15 unit tests passing
- ✅ 87% code coverage

### Blockers
- ⚠️ Task 3.1 blocked (AWS SES API key)
- 💡 Emailed DevOps, should have key tomorrow

### Tomorrow
1. Receive API key, unblock Task 3.1
2. Complete Phase 3 (version tagging)
3. Ship PRD-0001 🚀

### Time
- Focused work: 6 hours
- Meetings: 1 hour
- Context switching: 0 (stayed on PRD-0001 all day ✅)
```

---

## Tips & Best Practices

### Tip 1: Use System Prompts for Context

Keep a `.claude/context.md` file:
```markdown
# Current Focus
- **Main**: PRD-0001 (Auth System) - Phase 2 testing
- **Secondary**: PRD-0002 (Payment API) - Research

# Preferences
- Test framework: pytest
- Commit format: Conventional commits
- Branch naming: feature/PRD-NNNN-description

# Blockers
- Waiting for AWS SES API key (requested 2025-01-15)
```

Then reference it:
```bash
Claude> "Read .claude/context.md and update daily briefing"
```

### Tip 2: Automate Retrospectives

Create Git hook to prompt for retrospective:
```bash
# .git/hooks/post-commit
#!/bin/bash
echo "💡 Remember to update daily log: .claude/daily-log.md"
```

### Tip 3: Track Metrics

Add metrics to retrospective:
```markdown
## Metrics
- Commits: 8
- Tests added: 12
- Lines changed: +450 / -120
- Build time: 2.3s
```

---

## Why This Works

**Daily Routine Benefits**:
1. **Context Preservation**: No "what was I doing?" each morning
2. **Progress Visibility**: Clear tracking across multiple PRDs
3. **Blocker Management**: Document blockers, find workarounds
4. **Continuous Improvement**: Weekly reviews identify patterns
5. **Accountability**: Written record of accomplishments

**Time Comparison**:
- ❌ **No routine**: 30min context loading each day × 5 days = 2.5h/week wasted
- ✅ **With routine**: 5min × 5 days = 25min/week
- **Savings**: 2h 5min per week (83% reduction in context-switching overhead)

---

**Next Steps**:
- For starting new features → Use [recipe-new-feature.md](recipe-new-feature.md)
- For understanding codebase → Use [recipe-legacy-analysis.md](recipe-legacy-analysis.md)
- For fixing bugs → Use [recipe-debugging-tdd.md](recipe-debugging-tdd.md)
