# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Repository Purpose**: Global workflow templates and automation for Claude Code development
**Version**: 5.0.0 | **Updated**: 2025-01-18 | **Major Update**: Comprehensive workflow optimization

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
→ Phase 2.5: Review ⭐ → Phase 3: Version → Phase 4: Git + Auto PR
→ Phase 5: E2E + Security → Phase 6: Deploy
```

**NEW in v5.0.0**: Phase 2.5 (Professional Reviews) - Pragmatic code review, design review, security review

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

### Phase 1: Implementation

**Purpose**: Write production-ready code with 1:1 test pairing

**Core Rules**:
- **1:1 Test Pairing (Mandatory)**: Every implementation file must have a corresponding test file
  - `src/auth.py` → `tests/test_auth.py`
  - `src/components/Button.tsx` → `tests/components/Button.test.tsx`
- **Test First or Concurrent**: Write tests alongside implementation, not after
- **No orphaned implementation**: All code must have tests before PR

**Workflow**:
```bash
# 1. Implement feature
vim src/feature.py

# 2. Write tests (same session)
vim tests/test_feature.py

# 3. Run tests locally
pytest tests/test_feature.py -v

# 4. Validate 1:1 pairing
bash scripts/validate-phase-1.sh
```

**Validation** (mandatory before Phase 2):
```bash
bash scripts/validate-phase-1.sh
# ✅ Confirms all src files have test pairs
```

---

### Phase 2: Testing

**Purpose**: Ensure code quality through comprehensive testing

**Test Types**:
1. **Unit Tests** (test-automator agent)
   - Isolated function/method tests
   - 80%+ code coverage target
   - Fast execution (<5s per file)

2. **Integration Tests** (test-automator agent with mock data)
   - API endpoint tests
   - Database interaction tests
   - External service mocks

3. **E2E Tests** (playwright-engineer agent)
   - User flow validation
   - Cross-browser testing
   - Critical path coverage

**Python Projects**:
```bash
# Run all tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_specific.py -v

# Run by marker
pytest tests/ -v -m "unit"
```

**Node.js Projects**:
```bash
# Run all tests
npm test

# With coverage
npm run test:coverage

# Specific test
npm test -- tests/specific.test.js
```

**Validation** (mandatory before Phase 3):
```bash
bash scripts/validate-phase-2.sh
# ✅ Confirms all tests pass, coverage threshold met
```

---

### Phase 2.5: Code & Design Review (NEW v5.0.0)

**Purpose**: Professional review before versioning

**Review Types**:

**1. Pragmatic Code Review** (Recommended ⭐ - Opus):
```bash
/pragmatic-code-review
```
**Features**:
- 7-tier hierarchical analysis (Architecture → Dependencies)
- Pragmatic Quality framework
- Opus model for deep analysis

**When to use**:
- ✅ Before merging to main
- ✅ Critical feature PRs
- ✅ Pre-production releases

**2. Design Review** (UI changes):
```bash
/design-review
```
**Features**:
- Playwright MCP integration (live environment testing)
- 7-phase process (Interaction → Console)
- WCAG 2.1 AA accessibility compliance
- Desktop/Tablet/Mobile screenshots

**When to use**:
- ✅ UI/UX component changes
- ✅ Responsive design updates
- ✅ Accessibility improvements

**3. Security Review** (Security-critical code):
```bash
/security-review
```
**Features**:
- OWASP Top 10 focused
- High-confidence detection (>80%)
- Minimizes false positives

**When to use**:
- ✅ Authentication/authorization code
- ✅ Payment processing
- ✅ User data handling

**Validation** (recommended before Phase 3):
```bash
# Check review completion
git log -1 --grep="review"
# OR manually verify PR has review comments
```

**Workflow Integration**:
```
Phase 2 (Tests pass) → Phase 2.5 (Reviews complete) → Phase 3 (Version tag)
```

---

### Phase 3: Semantic Versioning

**Purpose**: Tag stable releases with semantic versioning

**Version Format**: `vMAJOR.MINOR.PATCH`
- **MAJOR**: Breaking changes (v2.0.0)
- **MINOR**: New features, backward compatible (v1.2.0)
- **PATCH**: Bug fixes (v1.0.1)

**Workflow**:
```bash
# 1. Ensure all tests pass
npm test  # or pytest

# 2. Update CHANGELOG.md
vim CHANGELOG.md
# Add:
# ## [1.2.0] - 2025-01-14
# ### Added
# - New authentication feature [PRD-0001]

# 3. Create git tag
git tag -a v1.2.0 -m "Release 1.2.0: Add authentication"

# 4. Push tag
git push origin v1.2.0
```

**CHANGELOG.md Format**:
```markdown
# Changelog

## [1.2.0] - 2025-01-14
### Added
- OAuth2 authentication [PRD-0001]
- User profile API [PRD-0002]

### Fixed
- Login timeout bug [#123]

## [1.1.0] - 2025-01-10
...
```

**Validation** (mandatory before Phase 4):
```bash
bash scripts/validate-phase-3.sh v1.2.0
# ✅ Confirms tests pass, CHANGELOG updated, no uncommitted changes
```

---

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

### Phase 5: E2E & Security Testing

**Purpose**: Final validation before production deployment

**Mandatory Checks**:

**1. E2E Testing** (playwright-engineer agent):
```bash
# Run E2E tests
npm run test:e2e

# Or use agent
# Task("playwright-engineer", "Run E2E tests for login, checkout, and profile flows")
```
- User flow validation (login, signup, core features)
- Cross-browser testing (Chrome, Firefox, Safari)
- Mobile responsive testing
- Performance benchmarks (page load <3s)

**2. Security Audit** (security-auditor agent):
```bash
# Automated scans
npm audit
python -m pip_audit  # Python projects

# Or use agent
# Task("security-auditor", "Audit authentication system for OWASP Top 10")
```
- OWASP Top 10 compliance
- SQL injection prevention
- XSS/CSRF protection
- Dependency vulnerability scan
- No hardcoded secrets

**3. Performance Testing** (performance-engineer agent):
```bash
# Load testing
artillery run load-test.yml

# Or use agent
# Task("performance-engineer", "Run load test for 1000 concurrent users")
```
- API response time <500ms
- Database query optimization
- Memory leak detection
- CPU profiling

**Validation** (mandatory before Phase 6):
```bash
bash scripts/validate-phase-5.sh
# ✅ Confirms E2E tests pass, no critical vulnerabilities, performance benchmarks met
```

---

### Phase 6: Deployment

**Purpose**: Deploy to production with confidence

**Pre-Deployment Checklist**:
- [ ] All Phase 5 checks passed
- [ ] Environment variables documented in `.env.example`
- [ ] Secrets stored in environment, not code
- [ ] Production build tested locally
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Monitoring/alerting configured

**Deployment Workflow**:
```bash
# Use deployment-engineer agent
# Task("deployment-engineer", "Deploy to production using Docker + GitHub Actions")

# Or manual:
# 1. Build production image
docker build -t myapp:v1.2.0 .

# 2. Test locally
docker run -p 3000:3000 myapp:v1.2.0

# 3. Push to registry
docker push myregistry/myapp:v1.2.0

# 4. Deploy (example: K8s)
kubectl apply -f k8s/deployment.yml
kubectl rollout status deployment/myapp
```

**Environment Variables**:
```bash
# .env.example (committed to git)
DATABASE_URL=postgresql://user:pass@host:5432/db
API_KEY=your_api_key_here
REDIS_URL=redis://localhost:6379

# .env (NOT committed, in .gitignore)
DATABASE_URL=postgresql://prod_user:prod_pass@prod_host:5432/prod_db
API_KEY=actual_production_key
REDIS_URL=redis://prod-redis:6379
```

**Rollback Plan**:
```bash
# If deployment fails, rollback to previous version
kubectl rollout undo deployment/myapp

# Or with Docker
docker pull myregistry/myapp:v1.1.0
docker run -p 3000:3000 myregistry/myapp:v1.1.0
```

**Validation** (pre-deployment):
```bash
bash scripts/validate-phase-6.sh
# ✅ Confirms .env.example exists, no secrets in code, build succeeds
```

**Post-Deployment**:
- [ ] Smoke tests pass
- [ ] Monitoring dashboards show healthy metrics
- [ ] Error rates within normal range
- [ ] Performance metrics meet SLA

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

### 🚀 Plugin Marketplace System (Updated v5.0.0)

**통합 완료**: 3개 주요 소스 통합 완료 (2025-01-18)
- wshobson/agents (v4.16.0)
- davila7/claude-code-templates (v4.17.0)
- OneRedOak/claude-code-workflows (v4.18.0)

**현재 아키텍처**:
- **25개 플러그인** (17개 wshobson + 8개 Phase별 legacy)
- **122+ 에이전트** (89개 wshobson + 33개 기존 + 통합)
- **27개 스킬** (Progressive Disclosure 방식)
- **마켓플레이스 시스템** (.claude-plugin/marketplace.json)

### Plugin Architecture

Each plugin is an isolated unit containing:
- **Agents**: Domain-specific experts (1-3 per plugin)
- **Commands**: Slash commands for workflows
- **Skills**: Progressive disclosure knowledge packages

**토큰 효율성**: Skills는 필요할 때만 활성화되어 200k 토큰 한계 극복

### Smart Agent Selection (Automatic)

**Claude Code automatically selects optimal agents based on Phase and context.**

No manual scripts needed - I read CLAUDE.md and choose appropriate agents:

- **Phase 0**: context7-engineer, seq-engineer (research)
- **Phase 1**: debugger, typescript-expert, test-automator (implementation)
- **Phase 2**: test-automator, playwright-engineer (testing)
- **Phase 5**: playwright-engineer, security-auditor (E2E & security)
- **Phase 6**: deployment-engineer (deployment)

**Benefits**: 60-80% token savings vs loading all agents

### Available Plugins (25 total)

**wshobson Plugins (17개)** - Production-ready workflows + Meta-development:

1. **full-stack-orchestration** ⭐ - Multi-agent coordination for complete features
   - Agents: 7+ agents (backend, frontend, database, test, security, deploy, observability)
   - Commands: `/full-stack-feature`
   - Use: End-to-end feature development

2. **python-development** - Python 3.12+ modern development
   - Agents: python-pro, django-pro, fastapi-pro
   - Skills: async-patterns, testing, packaging, performance, uv-manager
   - Use: Python projects

3. **javascript-typescript** - JS/TS applications
   - Agents: typescript-expert, node-specialist
   - Skills: types, node-patterns, testing, es6+
   - Use: JavaScript/TypeScript projects

4. **backend-development** - API architecture
   - Agents: backend-architect, api-designer, microservices-expert
   - Skills: api-design, architecture-patterns, microservices, temporal-testing
   - Use: Backend API development

5. **security-scanning** - Code security
   - Agents: security-auditor, penetration-tester
   - Skills: owasp-top10, dependency-scanning
   - Use: Security audits

6. **kubernetes-operations** - K8s deployment
   - Agents: k8s-architect
   - Skills: deployment-strategies, helm-charts, gitops, monitoring
   - Use: Kubernetes deployments

7. **cloud-infrastructure** - Multi-cloud platforms
   - Agents: cloud-architect, terraform-specialist
   - Skills: cost-optimization, multi-cloud, networking, serverless
   - Use: Cloud infrastructure

8. **api-testing-observability** - API testing
   - Agents: api-tester, observability-engineer
   - Use: API testing and monitoring

9. **code-refactoring** - Code improvement
   - Agents: refactoring-expert
   - Use: Code refactoring

10. **application-performance** - Performance optimization
    - Agents: performance-engineer
    - Use: Performance tuning

11. **cicd-automation** - CI/CD pipelines
    - Agents: cicd-specialist
    - Skills: pipeline-design, github-actions, gitlab-ci, secrets-management
    - Use: CI/CD automation

12. **debugging-toolkit** - Interactive debugging
    - Agents: debugger, dx-optimizer
    - Commands: `/smart-debug`
    - Use: Bug fixing

13. **code-documentation** - Documentation generation
    - Agents: docs-architect, tutorial-engineer, code-reviewer
    - Commands: `/doc-generate`, `/code-explain`
    - Use: Documentation

14. **git-pr-workflows** - Git/PR automation
    - Agents: code-reviewer
    - Commands: `/pr-enhance`, `/onboard`, `/git-workflow`
    - Use: Git workflows

15. **agent-orchestration** - Multi-agent coordination
    - Use: Complex multi-agent tasks

16. **meta-development** ⭐ - Claude Code component development (NEW v4.17.0)
    - Source: davila7/claude-code-templates
    - Agents: agent-expert, command-expert, mcp-expert, cli-ui-designer, docusaurus-expert, frontend-developer
    - Use: Creating agents, commands, MCPs, and documentation for Claude Code itself
    - **When to use**: Building Claude Code extensions, custom agents, slash commands, or MCP integrations

17. **workflow-reviews** ⭐ - Specialized review workflows (NEW v4.18.0)
    - Source: OneRedOak/claude-code-workflows
    - Agents: pragmatic-code-review (Opus), design-review (Sonnet)
    - Commands: `/pragmatic-code-review`, `/design-review`, `/security-review`
    - Use: Professional code/design/security reviews inspired by Anthropic's own process
    - **When to use**: PR reviews, UI/UX validation, security audits, accessibility compliance
    - **Features**: 7-tier hierarchical review, Playwright MCP integration, OWASP Top 10, WCAG 2.1 AA

---

**Phase-Specific Plugins (8개)** - Legacy agents organized by Phase:

1. **phase-0-planning** - Planning & Research
   - Agents: seq-engineer ⭐, context7-engineer ⭐, task-decomposition-expert, taskmanager-planner, exa-search-specialist
   - Use: Phase 0-0.5

2. **phase-1-development** - Implementation
   - Agents: debugger ⭐, typescript-expert, frontend-developer, backend-architect ⭐, fullstack-developer, python-pro, mobile-developer
   - Use: Phase 1

3. **phase-2-testing** - Testing
   - Agents: test-automator ⭐, playwright-engineer ⭐, code-reviewer ⭐, security-auditor ⭐
   - Use: Phase 2

4. **phase-3-architecture** - Architecture review
   - Agents: architect-reviewer, graphql-architect
   - Use: Phase 3

5. **phase-6-deployment** - Deployment
   - Agents: deployment-engineer ⭐, devops-troubleshooter, cloud-architect
   - Use: Phase 6

6. **database-tools** - Database specialists
   - Agents: database-architect, database-optimizer
   - Use: Database design/optimization

7. **ai-ml-tools** - AI/ML specialists
   - Agents: ai-engineer, ml-engineer, data-engineer, data-scientist, prompt-engineer
   - Use: AI/ML projects

8. **specialized-tools** - Specialized agents
   - Agents: github-engineer, supabase-engineer, performance-engineer, context-manager, UI_UX-Designer
   - Use: Specialized tasks

---

**Token Usage** (with Plugin System):
- **All plugins loaded**: ~15,000 tokens (vs 40,000 before)
- **Phase-specific plugins only**: 1,500-3,000 tokens
- **Skills loaded on-demand**: 0 tokens until activated
- **Savings**: 85-95% per conversation (improved from 80-90%)

**⭐ = Highest priority plugins for most projects**

### Skills System (27개)

Skills are **progressive disclosure** knowledge packages that activate only when needed:

**Backend Skills** (5):
- api-design-principles, architecture-patterns, microservices-patterns, temporal-python-testing, workflow-orchestration-patterns

**CI/CD Skills** (4):
- deployment-pipeline-design, github-actions-templates, gitlab-ci-patterns, secrets-management

**Cloud Skills** (4):
- cost-optimization, multi-cloud-patterns, networking-fundamentals, serverless-architectures

**JavaScript/TypeScript Skills** (4):
- advanced-typescript-patterns, es6-modern-features, node-best-practices, testing-frameworks

**Kubernetes Skills** (4):
- deployment-strategies, helm-chart-patterns, gitops-workflows, monitoring-observability

**Python Skills** (5):
- async-python-patterns, python-packaging, python-performance-optimization, python-testing-patterns, uv-package-manager

**Security Skills** (1):
- owasp-top10-checklist

**Activation**: Skills자동으로 활성화 (컨텍스트 기반)

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

### Agent-Task Mapping Rules (Summary)

**IMPORTANT**: Use the right agent for the right task type.

#### Quick Reference

| Task Type | ✅ Use This Agent | ❌ Don't Use |
|-----------|------------------|-------------|
| Unit Tests | test-automator (100% success) | playwright-engineer (overkill) |
| E2E Tests | playwright-engineer (63% success) | test-automator (will timeout) |
| Bug Fixes | debugger (81% success) | typescript-expert (slower) |
| Code Review | code-reviewer (100% success) | Manual review |
| Security Scan | security-auditor (100% success) | Manual audit |
| Doc Verification | context7-engineer (100% success) | Skip (risky) |

#### Integration Tests Pro Tip

**Always provide explicit mock data** (25% → 75% success rate):
```python
# ✅ Good
Task("test-automator", "Write integration tests with mock: {user: {id: 1, ...}}")

# ❌ Bad (will fail)
Task("test-automator", "Write integration tests")
```

**Detailed Guide**: See [docs/AGENT_USAGE_BEST_PRACTICES.md](docs/AGENT_USAGE_BEST_PRACTICES.md)

---

### Phase-Specific Agent Selection (Summary)

**Quick Phase Reference**:

| Phase | Primary Agents | Notes |
|-------|---------------|-------|
| **Phase 0-2** | See main workflow above | Planning → Implementation → Testing |
| **Phase 3** | code-reviewer, github-engineer | Version tagging, CHANGELOG |
| **Phase 4** | github-engineer | Auto PR/merge (mostly automated) |
| **Phase 5** | playwright-engineer, security-auditor | E2E + Security (parallel) |
| **Phase 6** | deployment-engineer | Production deployment |

**Detailed Mapping**: See [docs/PHASE_AGENT_MAPPING.md](docs/PHASE_AGENT_MAPPING.md)

**Key Execution Strategies**:
- **Parallel**: Phase 0, 0.5, 2, 3, 5 (max time savings)
- **Sequential**: Phase 4 (github-engineer → code-reviewer)
- **Conditional**: Phase 6 (cloud-architect first if needed)

**Token Savings**: 89.9% average vs loading all agents

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

### Phase Validation

**Validation Scripts & GitHub CI**

Use these validation scripts to ensure phase requirements are met before transitioning:

**Phase 0 → 0.5 Validation**:
```bash
bash scripts/validate-phase-0.sh NNNN
```
Checks:
- ✅ PRD exists in `tasks/prds/NNNN-prd-*.md`
- ✅ PRD has minimum 50 lines
- ✅ PRD includes purpose and core features sections

**Phase 0.5 → 1 Validation**:
```bash
bash scripts/validate-phase-0.5.sh NNNN
```
Checks:
- ✅ Task List exists in `tasks/NNNN-tasks-*.md`
- ✅ Task 0.0 completed (feature branch created)
- ✅ Task checkboxes properly formatted

**Phase 1 → 2 Validation**:
```bash
bash scripts/validate-phase-1.sh
```
Checks:
- ✅ All implementation files have 1:1 test pairs
- ✅ No orphaned implementation files

**Phase 2 → 3 Validation**:
```bash
bash scripts/validate-phase-2.sh
```
Checks:
- ✅ All tests pass (pytest or npm test)
- ✅ Test coverage meets minimum threshold
- ✅ No failing test files

**Phase 3 → 4 Validation**:
```bash
bash scripts/validate-phase-3.sh vX.Y.Z
```
Checks:
- ✅ All tests still pass
- ✅ CHANGELOG.md updated
- ✅ No uncommitted changes
- ✅ Version tag format correct

**Phase 5 → 6 Validation**:
```bash
bash scripts/validate-phase-5.sh
```
Checks:
- ✅ E2E tests exist and pass
- ✅ No critical security vulnerabilities
- ✅ Performance benchmarks met

**Phase 6 (Pre-Deployment) Validation**:
```bash
bash scripts/validate-phase-6.sh
```
Checks:
- ✅ .env.example exists and documented
- ✅ No hardcoded secrets in code
- ✅ Production build succeeds
- ✅ Deployment checklist completed

**GitHub CI Auto-Validation**: `.github/workflows/validate-phase.yml`
- Auto-runs on PRs from `feature/PRD-*` branches
- Enforces all validation gates
- Posts results as PR comment
- Blocks merge if validation fails

**Benefits**:
- 🚫 Prevents phase skipping
- ✅ Enforces 1:1 test pairing
- 📊 50% rework reduction
- 🤖 Automated in CI/CD pipeline

---

## File Structure

```
claude01/
├── CLAUDE.md                 # This file (v4.16.0)
├── README.md                 # Navigation & quick start
├── 깃허브_워크플로우_개요.md   # GitHub workflow (Korean, 5min)
├── 깃허브_빠른시작.md         # GitHub setup (Korean, 30min)
│
├── docs/                     # Detailed guides
│   ├── AGENTS_REFERENCE.md           # 120+ agents documented
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
├── .claude-plugin/           # 🆕 Plugin Marketplace System
│   └── marketplace.json              # 23 plugins metadata
│
├── .claude/                  # Claude Code extensions
│   ├── hooks/post-commit             # Git hook
│   ├── scripts/
│   │   ├── analyze_agent_usage.py    # Agent optimizer
│   │   └── load-plugins.py           # Plugin loader
│   ├── agents/                       # 🔄 Legacy agent files (reference)
│   │   └── *.md                      # 33 original agents
│   ├── plugins/                      # 🆕 New plugin system
│   │   ├── full-stack-orchestration/
│   │   │   ├── agents/               # 7+ orchestrated agents
│   │   │   ├── commands/             # Slash commands
│   │   │   └── skills/               # Progressive skills
│   │   ├── python-development/
│   │   │   ├── agents/               # python-pro, django-pro, fastapi-pro
│   │   │   └── skills/               # async, testing, packaging, perf, uv
│   │   ├── phase-0-planning/         # Legacy organized by phase
│   │   ├── phase-1-development/
│   │   ├── phase-2-testing/
│   │   ├── database-tools/
│   │   ├── ai-ml-tools/
│   │   └── ... (23 plugins total)
│   ├── plugins.old/                  # Backup of old plugin structure
│   ├── skills/                       # Global skills
│   │   ├── skill-creator/
│   │   └── webapp-testing/
│   ├── commands/                     # Slash commands
│   │   ├── aiden-endtoend.md
│   │   ├── aiden-plan.md
│   │   └── ...
│   ├── evolution/                    # Agent quality tracking
│   │   ├── scripts/
│   │   │   └── analyze_quality2.py
│   │   └── README.md
│   ├── track.py                      # Agent usage tracker
│   └── optimizer-config.json
│
├── .claude.backup-YYYYMMDD/  # Backup before v4.16.0 upgrade
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
- **v4.16.0 (2025-01-18)** - **wshobson/agents Plugin System Integration** 🚀
  - ✅ **23 Plugins**: 15 wshobson + 8 Phase-specific legacy
  - ✅ **120+ Agents**: 87 wshobson + 33 original + integration
  - ✅ **27 Skills**: Progressive disclosure knowledge packages
  - ✅ **Marketplace System**: `.claude-plugin/marketplace.json`
  - ✅ **Token Optimization**: 85-95% savings (improved from 80-90%)
  - ✅ **Architecture**: Plugin-based isolated units (agents + commands + skills)
  - **Result**: Production-ready plugin ecosystem, massive scalability, token efficiency
- v4.15.0 (2025-01-14) - Agent usage tracking v2.0, documentation updates
- v4.14.0 (2025-01-14) - **Conversation-First Simplification**: Removed unnecessary complexity
  - ✅ Task generation: API script → Conversation (saves API costs, setup complexity)
  - ✅ Agent selection: Manual script → Automatic (no user action needed)
  - ✅ Phase validation: Manual scripts → Automatic conversation (no user action needed)
  - ✅ Agent analysis: Post-commit hook + API → On-demand conversation
  - **Result**: Simpler workflow, no API keys, no setup, just conversation
- v4.13.0 (2025-01-14) - Integrated PhaseFlow AI task generation (later simplified to conversation)
- v4.12.0 (2025-01-14) - Expanded plugin system to 15 agents (later simplified to automatic)
- v4.11.0 (2025-01-14) - Explored wshobson/agents plugin system (now fully integrated in v4.16.0)
- v4.10.0 (2025-01-14) - Integrated cc-sdd validation gates (simplified to automatic)
- v4.9.0 (2025-01-13) - Architecture overview, testing commands
