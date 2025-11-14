# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Repository Purpose**: Global workflow templates and automation for Claude Code development
**Version**: 4.13.0 | **Updated**: 2025-01-14

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

**AI-Powered Auto-generation** (권장):
```bash
# 1. API 키 설정 (최초 1회)
export ANTHROPIC_API_KEY=your_key_here  # Unix/macOS
set ANTHROPIC_API_KEY=your_key_here     # Windows

# 2. 의존성 설치 (최초 1회)
pip install anthropic

# 3. Task List 자동 생성 (30초)
python scripts/generate_tasks_ai.py tasks/prds/NNNN-prd-feature.md

# Preview 모드 (저장 안 함)
python scripts/generate_tasks_ai.py tasks/prds/NNNN-prd-feature.md --preview
```

- **Output**: `tasks/NNNN-tasks-feature-name.md`
- **효과**: 8시간 → 30분 (94% 시간 단축)
- **가이드**: `docs/AI_TASK_GENERATION_GUIDE.md`
- **Two-Phase Process**:
  1. Generate Parent Tasks → user reviews → user says "Go"
  2. Generate Sub-Tasks with **mandatory 1:1 test file pairing**

**Critical Rules** (자동 적용):
- Task 0.0 MUST create feature branch
- Every implementation file MUST have corresponding test file
- Update checkboxes immediately: `[ ]` → `[x]` upon completion
- Status markers: `[ ]` pending | `[x]` done | `[!]` failed | `[⏸]` blocked

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

## Agent Usage & Optimization

### Plugin System (wshobson/agents inspired)

**Smart Agent Loading**: Phase/키워드 기반 선택적 Agent 로딩으로 토큰 40-70% 절감

```bash
# Phase별 최적 Agent 확인
python .claude/scripts/load-plugins.py --phase "Phase 0"
# → context7-engineer, seq-engineer 활성화 (66% 토큰 절감)

python .claude/scripts/load-plugins.py --phase "Phase 1" --keywords "React"
# → context7-engineer, test-automator, typescript-expert (44% 절감)

python .claude/scripts/load-plugins.py --phase "Phase 5"
# → playwright-engineer (70% 절감)
```

**상세 가이드**: `docs/PLUGIN_SYSTEM_GUIDE.md`

### Top 15 Agents (15 plugins total)

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

### Agent Optimizer (Post-Commit Hook)

**Auto-Analysis**: `.claude/hooks/post-commit` → `python .claude/scripts/analyze_agent_usage.py`

**What It Does**:
1. Parses Claude Code logs for agent usage
2. Classifies failures: `timeout` | `missing_context` | `parameter_error` | `ambiguous_prompt` | `api_error`
3. Uses Claude API to generate improved prompts
4. Saves to: `.claude/improvement-suggestions.md`
5. Amends commit with metadata: `Agent-Usage: [{"agent":"...","status":"..."}]`

**Setup**:
```bash
# Unix/macOS
ln -s ../../.claude/hooks/post-commit .git/hooks/post-commit

# Windows
copy .claude\hooks\post-commit .git\hooks\post-commit

# Install dependencies
pip install -r requirements.txt

# Optional: Set API key for improvement generation
export ANTHROPIC_API_KEY=your_key
```

**Config**: `.claude/optimizer-config.json`

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

### Phase Validation (cc-sdd inspired)

**Validation Gates**: Explicit checkpoints preventing phase skipping, ensuring spec-first development.

```bash
# Phase 0: PRD existence (before Task generation)
bash scripts/validate-phase-0.sh NNNN

# Phase 0.5: Task List + Task 0.0 completion (before coding)
bash scripts/validate-phase-0.5.sh NNNN

# Phase 1: 1:1 Test pairing (before PR)
bash scripts/validate-phase-1.sh
python scripts/validate-test-pairing.py  # More detailed

# Check overall progress
python scripts/check-phase-completion.py tasks/NNNN-tasks-*.md
```

**Automatic PR Validation**: `.github/workflows/validate-phase.yml`
- Triggers on: `feature/PRD-*` branch PRs
- Runs: Phase 0 → 0.5 → 1 validation sequence
- Posts: Results as PR comment
- Blocks: Merge if validation fails

**Benefits** (from cc-sdd integration):
- 🚫 Prevents coding without PRD
- ✅ Enforces 1:1 test pairing
- 📊 50% rework reduction
- ⏱️ 90% validation time savings (10min → 1min)

**Full Guide**: `docs/PHASE_VALIDATION_GUIDE.md`

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

1. **Minimal PRDs**: Use MINIMAL guide when experienced (saves ~3000 tokens)
2. **Parallel tool calls**: `Read("a.py"), Read("b.py")` in single message
3. **Focused context**: Read only necessary files, avoid full codebase scans
4. **Diff-based**: Show only changed sections, not entire files

**Example Savings**:
- PRD: MINIMAL (1270 tokens) vs JUNIOR (4500 tokens) = 72% reduction
- Docs: Recent optimization reduced 1737 → 1255 lines = 28% token reduction

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

### Local Workflow
```bash
# 1. Create PRD
vim tasks/prds/0001-prd-my-feature.md

# 2. Validate Phase 0
bash scripts/validate-phase-0.sh 0001

# 3. Generate tasks
python scripts/generate_tasks.py tasks/prds/0001-prd-my-feature.md

# 4. Review, then "Go" → sub-tasks generated

# 5. Validate Phase 0.5 & create branch (Task 0.0)
bash scripts/validate-phase-0.5.sh 0001
git checkout -b feature/PRD-0001-my-feature

# 6. Implement with tests
vim src/my_feature.py
vim tests/test_my_feature.py

# 7. Validate Phase 1
python scripts/validate-test-pairing.py

# 8. Commit & push
git commit -m "feat: Add feature (v1.0.0) [PRD-0001]"
git push  # → Auto PR/merge + validation takes over
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
- v4.13.0 (2025-01-14) - Integrated PhaseFlow AI task generation system, Phase 0.5 automation (8h → 30min, 94% time savings)
- v4.12.0 (2025-01-14) - Expanded plugin system to 15 agents (5 → 15), 16.8K baseline, 60-80% token savings per Phase
- v4.11.0 (2025-01-14) - Integrated wshobson/agents plugin system, Phase/keyword-based agent loading, 40-70% token savings
- v4.10.0 (2025-01-14) - Integrated cc-sdd validation gate system, added Phase 0/0.5/1 validation scripts, auto PR validation
- v4.9.0 (2025-01-13) - Added architecture overview, testing commands, agent optimizer details, clarified meta-workflow nature
