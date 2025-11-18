# Phase-Specific Agent Mapping Guide

**Version**: 5.0.0 | **Updated**: 2025-01-18

Complete guide for selecting optimal agents for each phase of the development cycle.

---

## Overview

This document provides detailed agent selection guidance for **Phase 3-6** of the development workflow. For Phase 0-2, see [CLAUDE.md](../CLAUDE.md).

**Quick Reference**:
- **Phase 3**: Versioning & Release Tagging
- **Phase 4**: Git + Automated PR/Merge
- **Phase 5**: E2E Testing & Security Validation
- **Phase 6**: Production Deployment

---

## Phase 3: Versioning

### code-reviewer (Required)
**Success Rate**: 100% | **Grade**: S | **Model**: Sonnet

**Use for**:
- Final code quality check before release
- Pre-release code review
- Architecture consistency validation
- Best practice adherence

**Timing**: After all tests pass, before creating git tag

**Output**: Review report for CHANGELOG.md

### github-engineer (Recommended)
**Model**: Haiku

**Use for**:
- Semantic version validation
- Git tag creation with proper annotations
- CHANGELOG.md formatting

**Timing**: After code-reviewer approval

---

## Phase 4: Git + PR Automation

### github-engineer (Required)
**Model**: Haiku

**Use for**:
- Automated PR creation from feature branch
- PR description generation
- Branch management

**Timing**: After Phase 3 tag creation

**Note**: Mostly automated via `.github/workflows/auto-pr-merge.yml`

### code-reviewer (Optional)
**Model**: Sonnet

**Use for**:
- Final PR review before merge
- Cross-file impact analysis
- Merge conflict resolution suggestions

---

## Phase 5: E2E & Security Testing

### playwright-engineer (Required)
**Success Rate**: 63% (improving) | **Model**: Sonnet

**Use for**:
- User flow testing (login, checkout, critical paths)
- Cross-browser validation (Chrome, Firefox, Safari)
- Visual regression testing

**Known Issues**:
- ⚠️ Timeout on complex flows (>45s)

**Best Practice**: Break long flows into smaller tests

**Timing**: Run in parallel with security-auditor

### security-auditor (Required)
**Success Rate**: 100% | **Grade**: S | **Model**: Sonnet

**Use for**:
- OWASP Top 10 compliance check
- Dependency vulnerability scan
- SQL injection/XSS prevention validation

**Timing**: Run in parallel with playwright-engineer

**Blocker**: Critical vulnerabilities must be fixed before Phase 6

### performance-engineer (Recommended)
**Grade**: A | **Model**: Sonnet

**Use for**:
- Load testing (1000+ concurrent users)
- Database query optimization
- Memory leak detection
- API response time benchmarking (<500ms target)

**Timing**: Run after E2E tests pass

### database-optimizer (Conditional)
**Model**: Sonnet

**Use for**:
- Slow query optimization (>100ms)
- Index recommendations
- Connection pool tuning

**Trigger**: Use ONLY if performance-engineer identifies DB bottlenecks

---

## Phase 6: Production Deployment

### deployment-engineer (Required)
**Grade**: A | **Model**: Haiku

**Use for**:
- Docker image build and optimization
- Kubernetes manifest creation
- CI/CD pipeline configuration
- Deployment script generation

**Timing**: After all Phase 5 checks pass

**Output**: Deployment commands, rollback plan

### cloud-architect (Recommended for first deployment)
**Model**: Sonnet

**Use for**:
- AWS/GCP/Azure resource provisioning
- Load balancer configuration
- Auto-scaling setup
- Cost optimization

**Timing**: Before deployment-engineer (infrastructure must exist first)

### devops-troubleshooter (Emergency use only)
**Model**: Sonnet

**Use for**:
- Deployment failure diagnosis
- Log analysis for errors
- Rollback execution
- Root cause analysis

**Trigger**: Use ONLY when deployment fails or production incidents occur

---

## Phase-Agent Summary Table

| Phase | Required Agents | Optional Agents | Parallel Execution |
|-------|----------------|-----------------|-------------------|
| 0 | context7-engineer, seq-engineer | architect-reviewer, exa-search | ✅ All |
| 0.5 | task-decomposition | taskmanager-planner | ✅ Both |
| 1 | debugger | backend-architect, frontend-developer, fullstack-developer | ✅ Most (exclude debugger) |
| 2 | test-automator, playwright-engineer | code-reviewer, security-auditor | ✅ All |
| 3 | code-reviewer, github-engineer | None | ✅ Both |
| 4 | github-engineer | code-reviewer | ❌ Sequential (github-engineer first) |
| 5 | playwright-engineer, security-auditor | performance-engineer, database-optimizer | ✅ All |
| 6 | deployment-engineer | cloud-architect, devops-troubleshooter | ⚠️ cloud-architect first, then deployment-engineer |

---

## Key Insights

### Parallel Execution Strategy
- **Always parallel**: Phase 0, 0.5, 2, 3, 5 (max time savings)
- **Sequential required**: Phase 4 (github-engineer creates PR, then code-reviewer reviews)
- **Conditional parallel**: Phase 6 (cloud-architect sets up infrastructure, then deployment-engineer deploys)
- **Emergency only**: devops-troubleshooter (production incidents)

### Performance Metrics
- **Token Savings**: 89.9% average vs loading all 33 agents
- **Measurement**: Run `python scripts/measure-token-usage.py --all`

---

## Related Documentation

- **[CLAUDE.md](../CLAUDE.md)** - Main workflow guide (Phase 0-2)
- **[AGENT_USAGE_BEST_PRACTICES.md](AGENT_USAGE_BEST_PRACTICES.md)** - Detailed agent-task mapping rules
- **[AGENTS_REFERENCE.md](AGENTS_REFERENCE.md)** - Complete agent catalog (122+ agents)

---

**Maintained By**: Claude Code + garimto81
**Repository**: https://github.com/garimto81/claude-code-config
