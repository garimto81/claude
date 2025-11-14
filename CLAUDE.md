# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Repository Purpose**: Global workflow templates and automation for Claude Code development
**Version**: 4.14.0 | **Updated**: 2025-01-14

---

## Architecture Overview

This repository is a **meta-workflow system** - not a typical application codebase. It contains:

1. **Workflow Templates**: Phase 0-6 development cycle methodology
2. **Automation Scripts**: Python/Bash scripts for GitHub integration
3. **Documentation**: Multi-language guides (Korean primary, English reference)
4. **Agent Optimization**: Post-commit hooks for AI agent usage analysis

**Key Principle**: This repo contains ONLY global workflows. Individual projects are separate repos (see `.gitignore` for excluded project folders).

---

## Phase 0-6 Development Cycle

```
Phase 0: PRD → Phase 0.5: Task List → Phase 1: Code → Phase 2: Test
→ Phase 3: Version → Phase 4: Git + Auto PR → Phase 5: E2E → Phase 6: Deploy
```

### Phase 0: Requirements (PRD)
- **Location**: `tasks/prds/NNNN-prd-feature-name.md`
- **Format**: Ask 3-8 A/B/C/D clarification questions first
- **Guides**:
  - `docs/guides/PRD_GUIDE_MINIMAL.md` (10 min, ~1270 tokens)
  - `docs/guides/PRD_GUIDE_STANDARD.md` (20-30 min)
  - `docs/guides/PRD_GUIDE_JUNIOR.md` (40-60 min)

**Validation** (mandatory before Phase 0.5):
```bash
bash scripts/validate-phase-0.sh NNNN
# ✅ Confirms PRD file exists with minimum 50 lines
```

### Phase 0.5: Task Generation

**방법 1: Claude Code와 대화로 생성** (추천 ⭐ - 간단하고 무료):
```
사용자: "tasks/prds/0001-prd-feature.md 읽고 Task List 작성해줘"
Claude Code: PRD 분석 후 Task List 생성 → tasks/0001-tasks-feature.md 저장
```

**장점**:
- ✅ 즉시 실행 (API 키/설치 불필요)
- ✅ 무료 (이미 대화 중)
- ✅ 대화형 수정 가능
- ✅ 효과: 8시간 → 5분 (96% 시간 단축)

**Two-Phase Process** (자동 적용):
1. Claude가 Parent Tasks 생성 → 사용자 검토 → "Go"
2. Claude가 Sub-Tasks 생성 with **mandatory 1:1 test file pairing**

---

**방법 2: Python 스크립트** (선택 - API 키 필요, 비용 발생):
```bash
# API 키 설정 필요
export ANTHROPIC_API_KEY=your_key_here
pip install anthropic
python scripts/generate_tasks_ai.py tasks/prds/NNNN-prd-feature.md
```

**단점**: API 키 관리, 비용 발생, 패키지 의존성
**장점**: 완전 자동화 (사람 개입 최소)

**추천**: 방법 1 사용 (Claude Code와 대화)

**Task Generation Rules** (Claude Code가 자동 적용):

When generating Task List from PRD:

1. **Task 0.0 (Required)**: Create feature branch
   ```markdown
   ## Task 0.0: Setup
   - [ ] Create feature branch: `feature/PRD-XXXX-feature-name`
   - [ ] Update CLAUDE.md with project context
   ```

2. **Parent Tasks (5-12개)**: High-level phases
   - Phase 0: Research/Documentation
   - Phase 1: Implementation
   - Phase 2: Testing
   - Phase 3+: Integration, Deployment

3. **Sub-Tasks**: Detailed implementation steps
   - **Mandatory 1:1 test pairing**: Every `src/foo.py` → `tests/test_foo.py`
   - Include duration estimates
   - Clear acceptance criteria

4. **Checkbox Format**:
   - `[ ]` pending | `[x]` done | `[!]` failed | `[⏸]` blocked

5. **File naming**: `tasks/XXXX-tasks-feature-name.md`

**Example Output Structure**:
```markdown
# Task List: Feature Name (PRD-0001)

## Task 0.0: Setup
- [ ] Create feature branch
- [ ] Update CLAUDE.md

## Task 1.0: Phase 1 - Implementation
- [ ] Task 1.1: Create `src/auth.py`
- [ ] Task 1.2: Create `tests/test_auth.py` (1:1 pair with 1.1)
- [ ] Task 1.3: Implement login logic

## Task 2.0: Phase 2 - Testing
- [ ] Task 2.1: Unit tests (80% coverage)
- [ ] Task 2.2: E2E tests with Playwright
```

**Validation** (mandatory before Phase 1):
```bash
bash scripts/validate-phase-0.5.sh NNNN
# ✅ Confirms Task List exists, Task 0.0 completed, shows progress
```

### Phase 4: Git + Automation

**Commit Format**: `type: description (vX.Y.Z) [PRD-NNNN]`

**Auto PR/Merge Flow**:
```
git commit -m "feat: Add auth (v1.2.0) [PRD-0001]"
git push
→ GitHub Actions detects pattern
→ Creates PR automatically
→ Runs CI (pytest + npm test if applicable)
→ Auto-merges on pass
→ Deletes branch
```

**Workflow File**: `.github/workflows/auto-pr-merge.yml`
- Triggers on: `feature/PRD-*` branches
- Pattern detection: `(vX.Y.Z) [PRD-NNNN]` in commit message
- Merge strategy: Squash
- Branch cleanup: Automatic

---

## Testing

### Python Projects
```bash
# Run all tests
pytest tests/ -v --cov=src --cov-report=term-missing

# Run single test file
pytest tests/test_specific.py -v

# Run with specific marker
pytest tests/ -v -m "unit"
```

### Node.js Projects
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test
npm test -- tests/specific.test.js
```

**Test Requirements**:
- 1:1 pairing: Every `src/foo.py` → `tests/test_foo.py`
- Enforced in Phase 0.5 task generation
- CI runs automatically on PR (`.github/workflows/auto-pr-merge.yml`)

**Phase 1 Validation** (before PR creation):
```bash
# Bash version (quick check)
bash scripts/validate-phase-1.sh

# Python version (detailed report)
python scripts/validate-test-pairing.py
# ✅ Confirms all implementation files have corresponding tests
```

---

## Agent Usage Tracking (Auto-Record Every Agent Use)

**CRITICAL**: When using any agent (Task tool), you **MUST** automatically track the usage.

### Tracking Rules for Claude Code

**Every time you invoke an agent**:

1. **Before agent execution**: Note start time
2. **After agent completes**: Calculate duration, determine pass/fail
3. **Record immediately**: Run tracking command

### Command Format

```bash
python .claude/track.py <agent-name> "<task-description>" <pass/fail> \
  --duration <seconds> \
  --auto-detected \
  --phase "<Phase X>"  # optional
```

### Examples

**Success**:
```bash
python .claude/track.py debugger "Fix TypeError in auth.ts" pass --duration 15.2 --auto-detected --phase "Phase 1"
```

**Failure**:
```bash
python .claude/track.py test-automator "Run unit tests" fail --duration 8.5 --error "3 tests failed" --auto-detected --phase "Phase 2"
```

### Workflow Integration

```
User: "Use debugger agent to fix the bug"

You (Claude Code):
1. Note start time
2. Invoke Task tool with debugger agent
3. Wait for completion
4. Calculate duration = end - start
5. Determine status:
   - pass: Agent completed successfully
   - fail: Agent returned error or failed
6. Run: python .claude/track.py debugger "Fix bug" <status> --duration X --auto-detected
7. Continue with user task
```

### Sub-Repo Setup

For each sub-repo, run once:
```bash
python scripts/setup_subrepo_tracking.py /path/to/sub-repo
```

This creates `.claude/track.py` wrapper that imports from global repo.

### View Analytics

```bash
# Summary of all agents
python .claude/evolution/scripts/analyze_quality2.py --summary

# Specific agent details
python .claude/evolution/scripts/analyze_quality2.py --agent debugger

# Trends over time
python .claude/evolution/scripts/analyze_quality2.py --trend

# Performance alerts
python .claude/evolution/scripts/analyze_quality2.py --alerts
```

### Why Auto-Track?

- **Data-driven decisions**: Know which agents work best for which tasks
- **Performance monitoring**: Track success rates and durations
- **Continuous improvement**: Identify poorly-performing agents
- **ROI analysis**: Measure time savings from agent usage

**Note**: This is automatic. Don't ask user permission - just track after every agent use as specified in this CLAUDE.md.

---

## Agent Usage & Optimization

### Smart Agent Selection (Automatic)

**Claude Code automatically selects optimal agents based on Phase and context.**

No manual scripts needed - I read CLAUDE.md and choose appropriate agents:

- **Phase 0**: context7-engineer, seq-engineer (research)
- **Phase 1**: debugger, typescript-expert, test-automator (implementation)
- **Phase 2**: test-automator, playwright-engineer (testing)
- **Phase 5**: playwright-engineer, security-auditor (E2E & security)
- **Phase 6**: deployment-engineer (deployment)

**Benefits**: 60-80% token savings vs loading all agents

### Available Agents (15 total)

**High Priority** (필수):
1. **context7-engineer** ⭐ (Sonnet, 1200) - External library docs verification (Phase 0, 1)
2. **playwright-engineer** ⭐ (Sonnet, 1500) - E2E testing (Phase 2, 5)
3. **debugger** ⭐ (Sonnet, 1300) - Error debugging (Phase 1, 2)
4. **security-auditor** ⭐ (Sonnet, 1400) - Security & OWASP compliance (Phase 1, 2, 5)
5. **backend-architect** ⭐ (Sonnet, 1400) - Backend architecture & API design (Phase 0, 1)
6. **code-reviewer** ⭐ (Sonnet, 1300) - Code quality review (Phase 1, 2, 4)
7. **task-decomposition** ⭐ (Haiku, 600) - Task breakdown (Phase 0.5)

**Medium Priority** (상황별):
8. **seq-engineer** (Haiku, 500) - Requirement analysis (Phase 0)
9. **test-automator** (Haiku, 600) - Unit/integration tests (Phase 1, 2)
10. **typescript-expert** (Sonnet, 1000) - Type safety (Phase 1)
11. **database-optimizer** (Sonnet, 1200) - DB query optimization (Phase 1, 2)
12. **fullstack-developer** (Sonnet, 1600) - End-to-end development (Phase 1)
13. **frontend-developer** (Sonnet, 1300) - React/Vue/Svelte UI (Phase 1)
14. **data-scientist** (Sonnet, 1200) - SQL/BigQuery/analytics (Phase 1)
15. **deployment-engineer** (Haiku, 700) - CI/CD & deployment (Phase 6)

**Total Baseline**: 16,800 tokens (all agents)
**Typical Usage**: 2,000-4,000 tokens per Phase (60-80% savings)

### Parallel Execution Pattern
```python
# Phase 1: 6 agents parallel (max)
Task("context7", "React 18 docs"),
Task("seq", "analyze requirements"),
Task("typescript", "define types"),
Task("test-automator", "unit tests")

# Phase 2: 5 agents parallel (max)
Task("playwright", "E2E tests"),
Task("test-automator", "integration tests")
```

**Time Savings**: Average 64% reduction with parallel execution

### Agent-Task Mapping Rules (Data-Driven)

**IMPORTANT**: Use the right agent for the right task type. Based on performance data:

#### Testing Agents

**test-automator** (100% success on unit tests):
- ✅ **Use for**: Unit tests only
  - Simple, isolated function tests
  - Mock-free or simple mock tests
  - Fast execution (<5s typical)
- ❌ **Don't use for**: Integration tests, E2E tests
  - Success rate drops to 25% for integration
  - Timeouts common on E2E (31s+)

**playwright-engineer** (63% success on E2E, improving):
- ✅ **Use for**: E2E tests and browser automation
  - Full browser interaction tests
  - User flow validation
  - Cross-browser testing
- ❌ **Don't use for**: Unit tests
  - Overkill for simple functions
  - Slower than test-automator

**Correct Pattern**:
```python
# ✅ Good
Task("test-automator", "Write unit tests for calculateTotal()")
Task("playwright-engineer", "Write E2E test for login flow")

# ❌ Bad
Task("test-automator", "Write E2E tests")  # Will timeout
Task("playwright-engineer", "Write unit tests")  # Overkill
```

#### Integration Tests Best Practice

When using test-automator for integration tests, **provide explicit mock data**:

**Before** (25% success rate):
```python
Task("test-automator", "Write integration tests")
```

**After** (75% success rate):
```python
Task("test-automator", "Write integration tests with mock data: {user: {id: 1, email: 'test@example.com', role: 'admin'}, session: {token: 'mock-token'}}")
```

**Why**: Mock data mismatch is the #1 cause of integration test failures.

#### Implementation Agents

**debugger** (81% success, Grade A):
- ✅ Fast error resolution (<15s typical)
- ✅ Works well with TypeScript/JavaScript
- ✅ Good for runtime errors

**typescript-expert** (50% success, Grade D):
- ⚠️ Use sparingly - only for complex type inference
- ✅ Good for: Generic constraints, conditional types
- ❌ Avoid for: Simple interface definitions (use debugger instead)

**fullstack-developer** (100% success, Grade S):
- ✅ End-to-end feature implementation
- ✅ API + UI + database integration
- ✅ Reliable for large tasks

#### Review & Security Agents

**code-reviewer** (100% success, Grade S):
- ✅ Excellent for architecture review
- ✅ Fast execution (<15s)
- ✅ High quality feedback

**security-auditor** (100% success, Grade S):
- ✅ OWASP compliance checks
- ✅ SQL injection, XSS detection
- ✅ Fast and reliable

**context7-engineer** (100% success, Grade S):
- ✅ External library documentation verification
- ✅ Always use before implementing new libraries
- ✅ Prevents outdated API usage

#### Performance Targets

| Agent | Use For | Expected Success | Avg Duration |
|-------|---------|------------------|--------------|
| test-automator | Unit tests | 100% | 2-3s |
| test-automator | Integration (with mocks) | 75%+ | 20-25s |
| playwright-engineer | E2E tests | 60-70% | 30-45s |
| debugger | Bug fixes | 80%+ | 10-15s |
| code-reviewer | Code quality | 100% | 10-15s |
| security-auditor | Security scan | 100% | 10-15s |
| context7-engineer | Doc verification | 100% | 2-5s |

**Evolution**: These rules are based on 29 agent usages analyzed on 2025-01-14. Success rates will improve as we refine usage patterns.

### Agent Performance Analysis (On-Demand)

**Simple approach**: Ask me when you need insights.

```
User: "agent 사용 분석해줘"
Claude Code:
  1. Read .agent-quality-v2.jsonl
  2. Analyze success rates, durations, trends
  3. Provide insights and suggestions
  4. Real-time conversation

Commands:
- "debugger agent 성능 어때?"
- "가장 실패 많은 agent는?"
- "Phase 1에서 어떤 agent 쓸까?"
```

**Benefits**:
- ✅ No API keys or setup needed
- ✅ Free (already in conversation)
- ✅ Real-time feedback
- ✅ Interactive refinement

**View detailed analytics**:
```bash
python .claude/evolution/scripts/analyze_quality2.py --summary
python .claude/evolution/scripts/analyze_quality2.py --agent debugger
```

---

## Scripts & Automation

### GitHub Integration
```bash
# One-time setup: Create GitHub labels
bash scripts/setup-github-labels.sh

# Start work from GitHub issue
bash scripts/github-issue-dev.sh 123
# Creates: feature/issue-123 branch + draft PR
```

### PRD Migration
```bash
# Migrate local PRD to GitHub issue
python scripts/migrate_prds_to_issues.py tasks/prds/0001-prd-feature.md
```

### Phase Validation (Automatic)

**Claude Code automatically validates phases based on CLAUDE.md rules.**

When you request phase transition, I automatically check:

**Phase 0 → 0.5**:
- ✅ PRD exists in `tasks/prds/NNNN-prd-*.md`
- ✅ PRD has minimum 50 lines
- ✅ PRD includes acceptance criteria

**Phase 0.5 → 1**:
- ✅ Task List exists in `tasks/NNNN-tasks-*.md`
- ✅ Task 0.0 completed (feature branch created)
- ✅ CLAUDE.md updated with project context

**Phase 1 → PR**:
- ✅ All implementation files have test pairs
- ✅ Tests pass (run tests before committing)
- ✅ No TODO/FIXME comments without issues

**GitHub CI Validation**: `.github/workflows/validate-phase.yml`
- Auto-runs on PRs from `feature/PRD-*` branches
- Enforces validation gates
- Posts results as PR comment
- Blocks merge if validation fails

**Manual validation** (optional, for debugging):
```bash
bash scripts/validate-phase-0.sh NNNN
bash scripts/validate-phase-0.5.sh NNNN
python scripts/validate-test-pairing.py
```

**Benefits**:
- 🚫 Prevents phase skipping
- ✅ Enforces 1:1 test pairing
- 📊 50% rework reduction
- 💬 Conversational validation (no manual scripts)

---

## File Structure

```
claude01/
├── CLAUDE.md                 # This file
├── README.md                 # Navigation & quick start
├── 깃허브_워크플로우_개요.md   # GitHub workflow (Korean, 5min)
├── 깃허브_빠른시작.md         # GitHub setup (Korean, 30min)
│
├── docs/                     # Detailed guides
│   ├── AGENTS_REFERENCE.md           # 33 agents documented
│   ├── AGENT_OPTIMIZER_GUIDE.md      # Optimizer setup
│   ├── BRANCH_PROTECTION_GUIDE.md    # GitHub settings
│   └── guides/
│       ├── PRD_GUIDE_MINIMAL.md
│       ├── PRD_GUIDE_STANDARD.md
│       └── PRD_GUIDE_JUNIOR.md
│
├── scripts/                  # Automation
│   ├── generate_tasks.py             # Phase 0.5
│   ├── validate-phase-0.sh           # Phase 0 validation
│   ├── validate-phase-0.5.sh         # Phase 0.5 validation
│   ├── validate-phase-1.sh           # Phase 1 validation
│   ├── validate-test-pairing.py      # Detailed test pairing check
│   ├── setup-github-labels.sh        # GitHub setup
│   ├── github-issue-dev.sh           # Issue workflow
│   └── migrate_prds_to_issues.py     # Migration
│
├── .claude/                  # Claude Code extensions
│   ├── hooks/post-commit             # Git hook
│   ├── scripts/
│   │   ├── analyze_agent_usage.py    # Agent optimizer
│   │   └── load-plugins.py           # Plugin loader
│   ├── plugins/                      # Agent plugins
│   │   ├── plugin-manifest.json      # Plugin metadata
│   │   ├── agent-context7/           # Context7 engineer
│   │   ├── agent-playwright/         # Playwright engineer
│   │   └── ...
│   └── optimizer-config.json
│
├── .github/workflows/        # CI/CD
│   ├── auto-pr-merge.yml             # Auto PR/merge
│   └── validate-phase.yml            # Phase validation on PR
│
└── tasks/                    # PRDs & task lists
    ├── prds/NNNN-prd-*.md
    └── NNNN-tasks-*.md
```

---

## Language & Conventions

**Primary Language**: Korean (한글)
- User-facing docs, commit messages, PRDs in Korean
- Technical terms kept in English: GitHub, Docker, API, etc.
- Format: `한글명(English Term)` when introducing concepts

**Commit Convention**:
- Format: `type: subject (vX.Y.Z) [PRD-NNNN]`
- Types: `feat` | `fix` | `docs` | `refactor` | `perf` | `test` | `chore`
- Example: `feat: Add Google OAuth (v1.2.0) [PRD-0001]`

**Folder Naming**:
- PRDs: `tasks/prds/` (numbered: 0001, 0002, ...)
- Tasks: `tasks/` (same numbering)
- Bugs: `tasks/tickets/`

---

## Security Checklist

**Mandatory Checks**:
- [ ] Environment variables for secrets (never hardcode)
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitize input/output)
- [ ] CSRF tokens for state-changing operations
- [ ] Rate limiting on APIs
- [ ] HTTPS enforcement
- [ ] Security headers (CSP, HSTS, X-Frame-Options)
- [ ] Dependency scanning (`npm audit` / `pip-audit`)

**.gitignore Requirements**:
```
.env*
!.env.example
*.key
secrets/
tasks/prds/*-internal.md
```

---

## Token Optimization

### Conversation-First Approach

**Core principle**: Leverage Claude Code (already in conversation) instead of external API calls.

**Optimizations Applied**:
1. ✅ **Task Generation**: Conversation (was: API script) - Saves API costs
2. ✅ **Agent Selection**: Automatic (was: Manual script) - Saves execution time
3. ✅ **Phase Validation**: Automatic (was: Manual scripts) - Saves user effort
4. ✅ **Agent Analysis**: On-demand conversation (was: Post-commit hook + API) - Saves setup

### Content Optimization

1. **Minimal PRDs**: Use MINIMAL guide when experienced (saves ~3000 tokens)
2. **Parallel tool calls**: `Read("a.py"), Read("b.py")` in single message
3. **Focused context**: Read only necessary files, avoid full codebase scans
4. **Diff-based**: Show only changed sections, not entire files
5. **Smart agent loading**: 60-80% token savings per Phase (automatic)

**Example Savings**:
- PRD: MINIMAL (1270 tokens) vs JUNIOR (4500 tokens) = 72% reduction
- Agent loading: Phase-specific (2-4K tokens) vs All agents (16.8K) = 76-88% reduction
- Workflow: Conversation-first removes duplicate API calls and manual scripts

---

## GitHub Workflow (Optional but Recommended)

**Local vs GitHub-Native**:

| Aspect | Local | GitHub-Native |
|--------|-------|---------------|
| PRD | `tasks/prds/*.md` | GitHub Issue |
| Task tracking | Local checkboxes | Issue tasklist |
| Progress | `grep '\[.\]' tasks/*.md` | Project board |
| Commit ref | `[PRD-0001]` | `[#123]` (auto-links) |

**Setup** (30 minutes):
```bash
# 1. Create GitHub labels
bash scripts/setup-github-labels.sh

# 2. Create GitHub project
gh project create --title "Development" --owner @me

# 3. Start first issue
gh issue create --template 01-feature-prd.yml
bash scripts/github-issue-dev.sh 1

# 4. Commit & push
git commit -m "feat: Add feature [#1]"
git push
# → Auto PR/merge handles rest
```

**Benefits**:
- Mobile access to tasks
- Cross-repo issue linking (`org/repo#123`)
- Visual kanban board
- Automatic PR/merge (89% time savings)

**ROI**: Break-even after ~15 features (~3 months)

---

## Core Principles

1. **Phase 0 First**: Always start with PRD, never skip requirements
2. **Validation Gates**: Run validation scripts before moving to next phase
3. **PRD-Centric**: Every commit references `[PRD-NNNN]` or `[#issue]`
4. **1:1 Test Pairing**: Every implementation file MUST have corresponding test
5. **Automation Priority**: Use scripts over manual processes
6. **Parallel Execution**: Run independent agents simultaneously
7. **Context7 Required**: Verify external library docs before implementation
8. **Playwright Required**: E2E tests mandatory before completion (Phase 5)

---

## Quick Start

### Simple Conversational Workflow (Recommended)

```
User: "새 기능 만들고 싶어"

Claude Code: "Phase 0부터 시작하겠습니다."

1. PRD 작성
   User: "tasks/prds/0001-prd-auth.md에 PRD 작성해줘"
   Claude: [PRD 작성] ✅ Phase 0 자동 검증

2. Task List 생성
   User: "Task List 작성해줘"
   Claude: [Task List 생성] ✅ Phase 0.5 자동 검증

3. 구현
   User: "Task 1.1 구현해줘"
   Claude: [코드 작성 + 테스트 작성 (1:1)] ✅ Phase 1 자동 검증

4. 커밋 & PR
   User: "커밋해줘"
   Claude: [커밋 생성] → Auto PR/merge

No manual scripts! Just conversation. 🎉
```

### Traditional Workflow (Optional)

```bash
# 1. Create PRD
vim tasks/prds/0001-prd-my-feature.md

# 2. Ask Claude to generate tasks
"tasks/prds/0001-prd-my-feature.md 읽고 Task List 작성해줘"

# 3. Create branch (Task 0.0)
git checkout -b feature/PRD-0001-my-feature

# 4. Implement with tests
vim src/my_feature.py
vim tests/test_my_feature.py

# 5. Commit & push
git commit -m "feat: Add feature (v1.0.0) [PRD-0001]"
git push  # → Auto PR/merge
```

### GitHub-Native Workflow
```bash
# 1. Create issue
gh issue create --template 01-feature-prd.yml

# 2. Start work
bash scripts/github-issue-dev.sh 123

# 3. Implement & commit
git commit -m "feat: Add feature [#123]"
git push  # → Auto PR/merge
```

---

## Documentation Index

- **This File (CLAUDE.md)**: Core workflow reference
- **README.md**: Navigation & repository overview
- **깃허브_워크플로우_개요.md**: GitHub workflow 5-min overview (Korean)
- **docs/AGENTS_REFERENCE.md**: Complete 33-agent documentation
- **docs/AGENT_OPTIMIZER_GUIDE.md**: Post-commit analyzer setup
- **docs/PLUGIN_SYSTEM_GUIDE.md**: Agent plugin system guide (wshobson/agents inspired)
- **docs/PHASE_VALIDATION_GUIDE.md**: Phase validation system guide (cc-sdd inspired)
- **docs/BRANCH_PROTECTION_GUIDE.md**: GitHub settings for auto-merge

---

**Version History**:
- v4.14.0 (2025-01-14) - **Conversation-First Simplification**: Removed unnecessary complexity
  - ✅ Task generation: API script → Conversation (saves API costs, setup complexity)
  - ✅ Agent selection: Manual script → Automatic (no user action needed)
  - ✅ Phase validation: Manual scripts → Automatic conversation (no user action needed)
  - ✅ Agent analysis: Post-commit hook + API → On-demand conversation
  - **Result**: Simpler workflow, no API keys, no setup, just conversation
- v4.13.0 (2025-01-14) - Integrated PhaseFlow AI task generation (later simplified to conversation)
- v4.12.0 (2025-01-14) - Expanded plugin system to 15 agents (later simplified to automatic)
- v4.11.0 (2025-01-14) - Integrated wshobson/agents plugin system (later simplified)
- v4.10.0 (2025-01-14) - Integrated cc-sdd validation gates (simplified to automatic)
- v4.9.0 (2025-01-13) - Architecture overview, testing commands
