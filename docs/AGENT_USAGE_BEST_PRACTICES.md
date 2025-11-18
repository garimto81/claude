# Agent Usage Best Practices

**Version**: 5.0.0 | **Updated**: 2025-01-18

Data-driven guide for selecting the right agent for the right task, based on actual performance metrics.

---

## Overview

This document provides detailed agent-task mapping rules based on **29+ agent usages** analyzed as of 2025-01-14. Success rates and performance targets are continuously updated.

**Key Principle**: Use the right agent for the right task type. Wrong agent selection leads to:
- ❌ Low success rates (25% vs 100%)
- ❌ Timeouts (31s+ vs 2-3s)
- ❌ Poor quality output

---

## Testing Agents

### test-automator
**Success Rate**: 100% (unit tests) | 25% (integration) | **Model**: Haiku

#### ✅ Use for: Unit Tests Only
- Simple, isolated function tests
- Mock-free or simple mock tests
- Fast execution (<5s typical)

#### ❌ Don't use for: Integration/E2E Tests
- Success rate drops to 25% for integration
- Timeouts common on E2E (31s+)

#### Correct Pattern
```python
# ✅ Good
Task("test-automator", "Write unit tests for calculateTotal()")

# ❌ Bad
Task("test-automator", "Write E2E tests")  # Will timeout
```

---

### playwright-engineer
**Success Rate**: 63% (E2E, improving) | **Model**: Sonnet

#### ✅ Use for: E2E Tests and Browser Automation
- Full browser interaction tests
- User flow validation
- Cross-browser testing

#### ❌ Don't use for: Unit Tests
- Overkill for simple functions
- Slower than test-automator

#### Correct Pattern
```python
# ✅ Good
Task("playwright-engineer", "Write E2E test for login flow")

# ❌ Bad
Task("playwright-engineer", "Write unit tests")  # Overkill
```

---

## Integration Tests Best Practice

### Provide Explicit Mock Data

**Before** (25% success rate):
```python
Task("test-automator", "Write integration tests")
```

**After** (75% success rate):
```python
Task("test-automator", "Write integration tests with mock data: {user: {id: 1, email: 'test@example.com', role: 'admin'}, session: {token: 'mock-token'}}")
```

**Why**: Mock data mismatch is the #1 cause of integration test failures.

---

## Implementation Agents

### debugger
**Success Rate**: 81% | **Grade**: A | **Model**: Sonnet

#### Strengths
- ✅ Fast error resolution (<15s typical)
- ✅ Works well with TypeScript/JavaScript
- ✅ Good for runtime errors

#### Use Cases
- TypeError, ReferenceError debugging
- Import/export resolution
- Quick fixes for syntax errors

---

### typescript-expert
**Success Rate**: 50% | **Grade**: D | **Model**: Sonnet

#### ⚠️ Use Sparingly
- Only for complex type inference
- ✅ Good for: Generic constraints, conditional types
- ❌ Avoid for: Simple interface definitions (use debugger instead)

---

### fullstack-developer
**Success Rate**: 100% | **Grade**: S | **Model**: Sonnet

#### Strengths
- ✅ End-to-end feature implementation
- ✅ API + UI + database integration
- ✅ Reliable for large tasks

---

## Review & Security Agents

### code-reviewer
**Success Rate**: 100% | **Grade**: S | **Model**: Sonnet

#### Strengths
- ✅ Excellent for architecture review
- ✅ Fast execution (<15s)
- ✅ High quality feedback

#### Use Cases
- Pre-release code review
- Architecture consistency validation
- Best practice adherence

---

### pragmatic-code-review (NEW v4.18.0)
**Model**: Opus | **Grade**: S+

#### Advanced Features
- 7-tier hierarchical review framework
- Pragmatic Quality methodology
- Detailed architectural analysis

#### When to Use
- ✅ Critical PR reviews
- ✅ Pre-production releases
- ✅ Architecture changes
- ❌ Quick reviews (use code-reviewer instead - faster)

---

### security-auditor
**Success Rate**: 100% | **Grade**: S | **Model**: Sonnet

#### Strengths
- ✅ OWASP compliance checks
- ✅ SQL injection, XSS detection
- ✅ Fast and reliable

---

### security-review (NEW v4.18.0)
**Slash Command** | **High-confidence** (>80%)

#### Advanced Features
- OWASP Top 10 focused
- Minimizes false positives
- Exploitability-based prioritization

#### When to Use
- ✅ Security-critical code (auth, payments)
- ✅ External API integration
- ✅ User data handling
- ❌ Internal utilities (use security-auditor)

---

## Documentation & Research Agents

### context7-engineer
**Success Rate**: 100% | **Grade**: S | **Model**: Sonnet

#### Strengths
- ✅ External library documentation verification
- ✅ Always use before implementing new libraries
- ✅ Prevents outdated API usage

#### Critical Usage
```python
# ✅ ALWAYS do this before using new library
Task("context7-engineer", "Verify React 18 hooks API documentation")
# Then implement using verified APIs
```

---

## Performance Targets

| Agent | Use For | Expected Success | Avg Duration |
|-------|---------|------------------|--------------|
| test-automator | Unit tests | 100% | 2-3s |
| test-automator | Integration (with mocks) | 75%+ | 20-25s |
| playwright-engineer | E2E tests | 60-70% | 30-45s |
| debugger | Bug fixes | 80%+ | 10-15s |
| code-reviewer | Code quality | 100% | 10-15s |
| pragmatic-code-review | Deep review | 95%+ | 45-60s |
| security-auditor | Security scan | 100% | 10-15s |
| security-review | High-confidence scan | 90%+ | 30-45s |
| context7-engineer | Doc verification | 100% | 2-5s |
| fullstack-developer | Full feature | 100% | 60-120s |

---

## Evolution Tracking

**Data Source**: `.agent-quality-v2.jsonl`

**Last Analysis**: 2025-01-14 (29 agent usages)

**Success Rates Improve Over Time**:
- playwright-engineer: 50% → 63% (3-month improvement)
- test-automator: 75% → 100% (with mock data guidance)

**View Latest Analytics**:
```bash
python .claude/evolution/scripts/analyze_quality2.py --summary
```

---

## Common Mistakes

### ❌ Wrong Agent Selection
```python
# Bad: Using playwright for unit tests
Task("playwright-engineer", "Test calculateTotal function")
# Good: Use test-automator
Task("test-automator", "Write unit tests for calculateTotal()")
```

### ❌ Missing Mock Data
```python
# Bad: Integration test without mocks
Task("test-automator", "Write integration tests for UserService")
# Good: Explicit mock data
Task("test-automator", "Write integration tests with mock: {user: {id: 1, ...}}")
```

### ❌ Skipping context7-engineer
```python
# Bad: Implement directly
"Implement React Query for data fetching"
# Good: Verify docs first
Task("context7-engineer", "Verify React Query v4 API docs")
# Then implement with verified APIs
```

---

## Related Documentation

- **[PHASE_AGENT_MAPPING.md](PHASE_AGENT_MAPPING.md)** - Phase-specific agent selection (Phase 3-6)
- **[CLAUDE.md](../CLAUDE.md)** - Main workflow guide
- **[AGENTS_REFERENCE.md](AGENTS_REFERENCE.md)** - Complete agent catalog

---

**Maintained By**: Claude Code + garimto81
**Repository**: https://github.com/garimto81/claude-code-config
