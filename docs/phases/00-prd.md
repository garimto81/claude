# Phase 0: Requirements (PRD)

**Duration**: 10-60 minutes (depending on complexity)
**Output**: `tasks/prds/NNNN-prd-feature-name.md`

---

## Overview

Phase 0 is the foundation of every feature. A well-written PRD prevents scope creep, reduces rework, and ensures all stakeholders understand the goal.

**Core Principle**: "Measure twice, cut once" - Invest time upfront to save time later.

---

## Process

### 1. Ask Clarification Questions (A/B/C/D Method)

Before writing the PRD, ask 3-8 targeted questions to understand:

**A. Problem & Users**:
- What specific problem are we solving?
- Who are the target users?
- What pain points do they currently face?

**B. Features & Scope**:
- What are the core features (MVP)?
- What is explicitly out of scope?
- What are nice-to-have features?

**C. Success Criteria**:
- How do we measure success?
- What are the acceptance criteria?
- What performance targets must we meet?

**D. Data & Design**:
- What data models are needed?
- What are the key UI/UX considerations?
- What external APIs or services are required?

### 2. Choose PRD Template

Select based on your experience level and project complexity:

| Template | Lines | Time | When to Use |
|----------|-------|------|-------------|
| **MINIMAL** | ~50 | 10 min | Experienced team, simple feature |
| **STANDARD** | ~100 | 20-30 min | Medium complexity, new team members |
| **JUNIOR** | ~200 | 40-60 min | Complex feature, junior developers |

**Guides**:
- [MINIMAL Guide](../guides/PRD_GUIDE_MINIMAL.md) - ~1,270 tokens
- [STANDARD Guide](../guides/PRD_GUIDE_STANDARD.md) - ~2,500 tokens
- [JUNIOR Guide](../guides/PRD_GUIDE_JUNIOR.md) - ~4,500 tokens

### 3. Write the PRD

**File naming**: `tasks/prds/NNNN-prd-feature-name.md`
- NNNN = 4-digit sequential number (0001, 0002, ...)
- feature-name = kebab-case description

**Minimum sections**:
```markdown
# PRD-NNNN: Feature Name

## 1. Purpose & Problem
[What problem are we solving?]

## 2. Target Users
[Who needs this?]

## 3. Core Features
- Feature 1
- Feature 2

## 4. Out of Scope
[What we're NOT doing]

## 5. Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## 6. Data Models
[Database schema, API contracts]

## 7. UI/UX Considerations
[Design requirements, mockups]

## 8. Technical Constraints
[Performance, security, compatibility]
```

---

## Validation

**Before moving to Phase 0.5, run:**
```bash
bash scripts/validate-phase-0.sh NNNN
```

**Checks**:
- ✅ PRD file exists
- ✅ Minimum 50 lines
- ✅ Required sections present
- ✅ Clear acceptance criteria

---

## Common Mistakes

### ❌ Too Vague
```markdown
## Purpose
Make the app better
```

### ✅ Specific
```markdown
## Purpose
Reduce login time from 5s to <2s by implementing OAuth2 and session caching
```

---

### ❌ No Success Criteria
```markdown
## Success
Users can log in
```

### ✅ Measurable
```markdown
## Success Criteria
- [ ] Login completes in <2 seconds (p95)
- [ ] 99.9% authentication success rate
- [ ] Zero SQL injection vulnerabilities
- [ ] 80%+ test coverage
```

---

## Tips for Success

1. **Start Small**: Better to scope down than expand mid-development
2. **Be Specific**: Vague requirements lead to vague implementations
3. **Think End-to-End**: Consider UI, backend, database, deployment
4. **Review with Stakeholders**: Get feedback before coding
5. **Keep It Updated**: PRD is a living document

---

## Examples

### Simple Feature (MINIMAL)
```markdown
# PRD-0001: Dark Mode Toggle

## Purpose
Add dark mode option to reduce eye strain for users working at night

## Users
All application users

## Core Features
- Settings page toggle
- System preference detection
- Persistent user choice

## Out of Scope
- Custom theme colors
- Per-page theme override

## Success
- [ ] Toggle works on all pages
- [ ] Choice persists across sessions
- [ ] Matches system preference by default
```

### Complex Feature (STANDARD+)
See [PRD_GUIDE_STANDARD.md](../guides/PRD_GUIDE_STANDARD.md) for e-commerce example.

---

## Next Steps

After validation passes:
1. **Phase 0.5**: Generate Task List from PRD
2. **Review**: Team reviews and approves PRD
3. **Estimate**: Add time estimates to tasks
4. **Plan**: Schedule work in sprint/iteration

---

**References**:
- [PRD Templates](../guides/)
- [Phase 0.5: Task Generation](01-task-generation.md)
- [Quick Start Guide](../QUICK_START_GUIDE.md)
