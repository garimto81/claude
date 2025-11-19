# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Repository Purpose**: Global workflow templates and automation for Claude Code development
**Version**: 5.2.0 | **Updated**: 2025-01-19

---

## 🚀 Quick Start: Workflow Recipes

**NEW**: Immediately usable workflow patterns for common tasks (5-60 min each)

| Task | Recipe | Time | Quick Link |
|------|--------|------|------------|
| 🐛 **Fix Bug** | TDD approach | 15 min | [recipe-debugging-tdd.md](docs/WORKFLOWS/recipe-debugging-tdd.md) |
| 📊 **Understand Code** | Mermaid diagrams | 10 min | [recipe-legacy-analysis.md](docs/WORKFLOWS/recipe-legacy-analysis.md) |
| 📅 **Daily Routine** | Progress tracking | 5 min/day | [recipe-daily-routine.md](docs/WORKFLOWS/recipe-daily-routine.md) |
| ✨ **New Feature** | Complete Phase 0-6 | 30-60 min | [recipe-new-feature.md](docs/WORKFLOWS/recipe-new-feature.md) |

**Why use recipes?**
- ✅ Copy-paste commands, run immediately
- ✅ Real-world tested patterns
- ✅ 63-95% time savings vs ad-hoc approaches
- ✅ Complement Phase 0-6 theoretical framework

**Full Recipe Index**: [docs/WORKFLOWS/README.md](docs/WORKFLOWS/README.md)

---

## Architecture Overview

This repository is a **meta-workflow system** - not a typical application codebase. It contains:

1. **Workflow Templates**: Phase 0-6 development cycle methodology
2. **Workflow Recipes** ⭐: Immediately usable patterns for common tasks
3. **Automation Scripts**: Python/Bash scripts for GitHub integration
4. **Plugin System**: Centralized plugin registry for Claude Code extensions
5. **Multi-language Documentation**: Korean primary, English reference
6. **Awesome Resources**: Curated community resources in `awesome-claude-code/`

**Key Principle**: This repo contains ONLY global workflows and meta-tools. Individual projects live in separate repositories (excluded in `.gitignore`).

---

## Common Development Commands

### Plugin Management
```bash
# List installed plugins
python scripts/plugin_manager.py list

# Install a plugin with specific version
python scripts/plugin_manager.py install python-development@1.3.0

# Check for plugin updates
python scripts/plugin_manager.py check-updates

# Compare local changes with upstream
python scripts/plugin_manager.py diff-upstream python-development
```

### Phase Validation (Universal Cross-Platform)
```bash
# Validate Phase 0 (PRD exists, 50+ lines)
python scripts/validate_phase_universal.py 0 <PRD_NUMBER>

# Validate Phase 0.5 (Task List exists, Task 0.0 complete)
python scripts/validate_phase_universal.py 0.5 <PRD_NUMBER>

# Validate Phase 1 (1:1 test pairing)
python scripts/validate_phase_universal.py 1

# Validate Phase 2 (tests pass, coverage threshold)
python scripts/validate_phase_universal.py 2 --coverage 80

# Validate Phase 3 (version tag, CHANGELOG, tests pass)
python scripts/validate_phase_universal.py 3 <VERSION_TAG>

# Validate Phase 5 (E2E, security, performance)
python scripts/validate_phase_universal.py 5

# Validate Phase 6 (deployment readiness)
python scripts/validate_phase_universal.py 6
```

### GitHub Workflow Scripts
```bash
# Setup GitHub labels for Phase workflow (one-time)
bash scripts/setup-github-labels.sh

# Start development from GitHub issue
bash scripts/github-issue-dev.sh <ISSUE_NUMBER>

# Check phase completion status
python scripts/check-phase-completion.py

# View phase status summary
bash scripts/phase-status.sh
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test with coverage
pytest tests/test_analyzer.py -v --cov=scripts --cov-report=term-missing

# Run awesome-claude-code tests
pytest awesome-claude-code/tests/ -v
```

---

## Repository Structure

### Core Workflow System
- **`.claude-plugin/registry.json`**: Central plugin registry with upstream tracking
  - Tracks 8+ plugins from multiple sources (wshobson/agents, davila7/claude-code-templates, OneRedOak/claude-code-workflows)
  - Manages versions, auto-update settings, local changes tracking
  - Status: `active`, `inactive`, `deprecated`

- **`.claude/`**: Claude Code extensions
  - **`commands/`**: Slash commands (`/commit`, `/todo`, `/tdd`, `/check`, `/optimize`, `/fix-issue`, `/create-prd`, `/create-pr`, `/create-docs`, `/changelog`)
  - **`plugins/`**: Plugin implementations (python-development, javascript-typescript, debugging-toolkit, meta-development, workflow-reviews, phase-0-planning, phase-1-development, phase-2-testing, etc.)
  - **`evolution/`**: Agent quality tracking system

### Automation Scripts (`scripts/`)
- **Plugin Management**: `plugin_manager.py` - install, update, list, diff plugins
- **Universal Validator**: `validate_phase_universal.py` - cross-platform Phase 0-6 validation
- **GitHub Integration**:
  - `setup-github-labels.sh` - one-time label setup
  - `github-issue-dev.sh` - start work from issue
  - `migrate_prds_to_issues.py` - PRD to GitHub issue migration
- **Legacy Phase Validators** (Bash): `validate-phase-{0,0.5,1,2,3,5,6}.sh`
- **Utilities**:
  - `check-phase-completion.py` - progress tracking
  - `setup_subrepo_tracking.py` - agent tracking in sub-repos
  - `validate-test-pairing.py` - detailed test pairing check

### Awesome Claude Code (`awesome-claude-code/`)
Community-curated resources:
- **`scripts/`**: Resource management automation
  - `add_resource.py`, `validate_links.py`, `generate_readme.py`
  - Badge notification system for resource updates
- **`resources/`**: Categorized community resources
  - `claude.md-files/` - Example CLAUDE.md files
  - `slash-commands/` - Community slash commands
  - `workflows-knowledge-guides/` - Workflow guides
  - `official-documentation/` - Anthropic official docs

### Documentation (`docs/`)
- **`WORKFLOWS/`** ⭐: **Immediately usable workflow recipes** (NEW v5.2.0)
  - `recipe-debugging-tdd.md` - Bug fixing with TDD (15 min)
  - `recipe-legacy-analysis.md` - Code understanding with Mermaid (10 min)
  - `recipe-daily-routine.md` - Daily progress tracking (5 min/day)
  - `recipe-new-feature.md` - Complete Phase 0-6 workflow (30-60 min)
  - `README.md` - Recipe index and selection guide
- **`guides/`**: PRD guides (MINIMAL, STANDARD, JUNIOR)
- **Agent References**: `AGENTS_REFERENCE.md`, `AGENT_USAGE_BEST_PRACTICES.md`
- **Phase Guides**: `PHASE_AGENT_MAPPING.md`, `PHASE_VALIDATION_GUIDE.md`
- **Optimization**: `AGENT_OPTIMIZER_GUIDE.md`, `AI_TASK_GENERATION_GUIDE.md`
- **GitHub**: `BRANCH_PROTECTION_GUIDE.md`

### GitHub Actions (`.github/workflows/`)
- **`validate-all-phases.yml`**: Comprehensive CI/CD validation
  - Documentation validation (markdown links, linting)
  - Script validation (Python/Bash linting)
  - Plugin structure validation
  - End-to-end Phase 0-2 workflow test
  - Version consistency check
  - Security scan (secrets, hardcoded credentials)
- **`auto-pr-merge.yml`**: Auto PR creation and merge on pattern detection
- **`validate-phase.yml`**: Per-PR phase validation

### Sub-Projects (Excluded from Git)
The following directories are `.gitignore`d and contain separate projects:
- `VTC_Logger/` - Example project using workflow
- `contents-factory/` - Photo factory project
- `sso-nextjs/` - SSO implementation
- `repo-analyzer/` - Repository analysis tool

---

## Phase 0-6 Workflow System

This is a structured development methodology, not just documentation. The workflow is enforced by validation scripts and GitHub Actions.

### Phase Flow
```
Phase 0: PRD → 0.5: Task List → 1: Code → 2: Test
→ 2.5: Review → 3: Version → 4: Git + Auto PR
→ 5: E2E + Security → 6: Deploy
```

### Key Concepts

**Phase 0 - Requirements**:
- PRD stored in `tasks/prds/NNNN-prd-feature-name.md`
- Must be 50+ lines with 8 core sections
- Validated: `python scripts/validate_phase_universal.py 0 NNNN`

**Phase 0.5 - Task Generation**:
- Task List in `tasks/NNNN-tasks-feature-name.md`
- **Task 0.0 mandatory**: Create branch, update CLAUDE.md
- Two-phase generation: Parent tasks → Sub-tasks
- Validated: `python scripts/validate_phase_universal.py 0.5 NNNN`

**Phase 1 - Implementation**:
- **1:1 test pairing mandatory**: Every `src/foo.py` → `tests/test_foo.py`
- No orphaned implementation files allowed
- Validated: `python scripts/validate_phase_universal.py 1`

**Phase 2 - Testing**:
- All tests must pass
- Minimum coverage threshold (default 80%)
- Validated: `python scripts/validate_phase_universal.py 2 --coverage 80`

**Phase 2.5 - Reviews** (NEW in v5.0.0):
- `/pragmatic-code-review` - 7-tier hierarchical review (Opus)
- `/design-review` - Playwright MCP UI/UX review (Sonnet)
- `/security-review` - OWASP Top 10 security audit

**Phase 3 - Versioning**:
- Semantic versioning: `vMAJOR.MINOR.PATCH`
- CHANGELOG.md update required
- Git tag created
- Validated: `python scripts/validate_phase_universal.py 3 v1.2.0`

**Phase 4 - Git Automation**:
- Commit format: `type: description (vX.Y.Z) [PRD-NNNN]`
- Auto PR creation on `feature/PRD-*` branches
- Auto-merge on CI pass

**Phase 5 - E2E & Security**:
- E2E tests (playwright-engineer agent)
- Security audit (security-auditor agent)
- Performance benchmarks
- Validated: `python scripts/validate_phase_universal.py 5`

**Phase 6 - Deployment**:
- Environment variables documented (`.env.example`)
- No hardcoded secrets
- Production build tested
- Validated: `python scripts/validate_phase_universal.py 6`

---

## Plugin System Architecture

### Registry Structure
The `.claude-plugin/registry.json` tracks:
- Plugin metadata (id, version, source)
- Upstream repositories (wshobson/agents, davila7/claude-code-templates, OneRedOak/claude-code-workflows)
- Local changes tracking
- Auto-update settings
- Installation/check timestamps

### Plugin Types
1. **Upstream Plugins**: Synced from external repos
   - `python-development` (wshobson/agents)
   - `javascript-typescript` (wshobson/agents)
   - `debugging-toolkit` (wshobson/agents)
   - `meta-development` (davila7/claude-code-templates)
   - `workflow-reviews` (OneRedOak/claude-code-workflows)

2. **Local/Legacy Plugins**: Project-specific
   - `phase-0-planning`, `phase-1-development`, `phase-2-testing`

### Plugin Components
Each plugin may contain:
- **Agents**: Domain experts (`.md` files in `agents/`)
- **Commands**: Slash commands (`.md` files in `commands/`)
- **Skills**: Knowledge packages (`.md` files in `skills/`)

---

## Slash Commands

Available via `.claude/commands/`:

**Workflow Commands**:
- `/commit` - Create conventional commits with emojis
- `/create-prd` - Interactive PRD generation
- `/create-pr` - Streamline PR creation
- `/todo` - Manage project todos with priorities

**Quality Commands**:
- `/check` - Comprehensive code quality checks
- `/tdd` - Test-Driven Development guide
- `/optimize` - Performance analysis

**Development Commands**:
- `/fix-issue` - Structured GitHub issue resolution
- `/create-docs` - Documentation generation
- `/changelog` - Changelog entry creation

**AIDEN System** (Agent-Integrated Development Environment):
- `/aiden-plan` - Planning agent
- `/aiden-first` - First-time setup
- `/aiden-update` - Update workflow
- `/aiden-endtoend` - End-to-end execution
- `/aiden-summary` - Progress summary

---

## Testing & Validation

### Test Structure
- **`tests/`**: Root-level tests for scripts
  - `test_analyzer.py` - Phase analyzer tests
  - `test_optimizer.py` - Agent optimizer tests
  - `test_phase_detection.py` - Phase detection logic
  - `test_pr_creation.py` - PR automation tests
  - `test_git_metadata.py` - Git metadata extraction

- **`awesome-claude-code/tests/`**: Resource management tests
  - `test_add_resource.py`, `test_generate_readme.py`
  - `test_badge_notification_validation.py`

### Running Tests
```bash
# All tests with coverage
pytest tests/ -v --cov=scripts --cov-report=html

# Specific test module
pytest tests/test_phase_detection.py -v

# Awesome Claude Code tests
pytest awesome-claude-code/tests/ -v

# GitHub Actions CI test
# Runs automatically on PR to master/main
```

---

## Bypassing Permissions (Windows)

For Windows users who need to bypass Claude Code permissions:

1. **Global Commands Available**:
   ```powershell
   claude-bypass    # PowerShell
   claude-bypass    # CMD
   ```

2. **Batch Scripts**:
   ```cmd
   .\start-claude-auto.bat
   .\start-claude-bypass.bat
   ```

3. **VSCode Task**:
   - `Ctrl+Shift+P` → "Tasks: Run Task" → "Claude CLI (Auto Bypass)"

4. **Direct Flag**:
   ```bash
   claude --dangerously-skip-permissions
   ```

---

## Language & Conventions

**Primary Language**: Korean (한글) for user-facing docs
**Technical Terms**: English (GitHub, Docker, API, pytest, etc.)
**Code/Scripts**: English with Korean comments where helpful

**Commit Convention**:
```
type: subject (vX.Y.Z) [PRD-NNNN]

Types: feat, fix, docs, refactor, perf, test, chore
Example: feat: Add OAuth (v1.2.0) [PRD-0001]
```

**File Naming**:
- PRDs: `tasks/prds/NNNN-prd-feature-name.md`
- Tasks: `tasks/NNNN-tasks-feature-name.md`
- Tests: `tests/test_<module>.py` (1:1 pairing with implementation)

---

## Key Dependencies

### Python (requirements.txt)
- `anthropic>=0.39.0` - Anthropic API client
- `pytest>=8.3.4`, `pytest-cov>=6.0.0` - Testing framework
- `pylint>=3.3.2` - Code linting
- Additional: `requests`, `pyyaml`, `jinja2`, `gitpython`

### Development (requirements-test.txt)
- `pytest-xdist` - Parallel test execution
- `pytest-mock` - Mocking support
- `coverage[toml]` - Coverage reporting

### Awesome Claude Code (awesome-claude-code/requirements.txt)
- Resource management utilities
- Badge generation
- Link validation

---

## Important Files

**Configuration**:
- `.claude-plugin/registry.json` - Plugin registry (DO NOT manually edit versions)
- `.gitignore` - Excludes sub-projects, build artifacts, secrets

**Documentation Index**:
- `README.md` - Korean primary documentation
- `CLAUDE.md` - This file (workflow reference)
- `docs/QUICK_START_GUIDE.md` - 5-minute quickstart

**Automation**:
- `.github/workflows/validate-all-phases.yml` - CI/CD pipeline
- `scripts/validate_phase_universal.py` - Cross-platform validator

---

## Best Practices

1. **Use Universal Validator**: `validate_phase_universal.py` works on Windows/macOS/Linux
2. **Always Validate Before Next Phase**: Prevents phase skipping and rework
3. **Maintain 1:1 Test Pairing**: Every implementation file needs a test file
4. **Let GitHub Actions Enforce Quality**: CI runs all validations on PRs
5. **Update Plugin Registry via CLI**: Use `plugin_manager.py`, not manual edits
6. **Follow Commit Convention**: Enables auto PR/merge workflow
7. **Document in Korean**: User-facing docs in Korean, code/technical in English

---

## Version History

- **v5.2.0 (2025-01-19)**: Workflow Recipes System ⭐
  - 4 immediately usable workflow recipes (5-60 min each)
  - `docs/WORKFLOWS/` directory with recipe index
  - Quick Start section in CLAUDE.md
  - Real-world tested patterns with copy-paste commands
  - 63-95% time savings vs ad-hoc approaches

- **v5.1.0 (2025-01-19)**: Repository cleanup
  - Removed project code (2.1MB) - clarified meta-workflow identity
  - Deleted duplicate/outdated documentation
  - Updated .gitignore with warning message
  - CLEANUP_REPORT.md comprehensive documentation

- **v5.0.0 (2025-01-19)**: Comprehensive workflow optimization
  - CLAUDE.md streamlined, documentation reorganized
  - Phase 2.5 (Professional Reviews) formalized
  - Universal cross-platform validator created

- **v4.18.0 (2025-01-18)**: Workflow-Reviews plugin integration
  - Pragmatic code review (Opus)
  - Design review (Playwright MCP)
  - Security review (OWASP Top 10)

- **v4.17.0 (2025-01-18)**: Meta-Development plugin integration
  - Agent development guides
  - Command/MCP experts
  - CLI UI designer

- **v4.16.0 (2025-01-18)**: Plugin system integration
  - 25 plugins, 120+ agents
  - 27 progressive disclosure skills
  - 85-95% token efficiency
