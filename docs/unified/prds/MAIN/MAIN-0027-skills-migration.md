# PRD-0027: Skills 마이그레이션

**Version**: 1.0.0 | **Date**: 2025-12-06 | **Status**: Draft
**Parent**: [PRD-0025](./MAIN-0025-master-workflow-optimization.md)
**Priority**: P0

---

## 1. 목적

28개 Commands를 8개 Skills로 통합하여 **Progressive Disclosure** 패턴을 적용하고 토큰 효율성을 극대화합니다.

---

## 2. Skills 목록

### 2.1 우선순위별 분류

| 우선순위 | Skill | 원본 Command | 예상 절감 |
|----------|-------|-------------|----------|
| 🔴 P0 | `debugging-workflow` | `/analyze-logs` + DEBUGGING_STRATEGY.md | ~2500 토큰 |
| 🔴 P0 | `pre-work-research` | `/pre-work` | ~1800 토큰 |
| 🔴 P0 | `final-check-automation` | `/final-check` | ~2000 토큰 |
| 🟠 P1 | `tdd-workflow` | `/tdd` | ~1200 토큰 |
| 🟠 P1 | `code-quality-checker` | `/check` | ~1400 토큰 |
| 🟠 P1 | `phase-validation` | Phase validators | ~1000 토큰 |
| 🟢 P2 | `parallel-agent-orchestration` | `/parallel-*` | ~1500 토큰 |
| 🟢 P2 | `issue-resolution` | `/fix-issue` | ~1100 토큰 |

**총 예상 절감**: ~12500 토큰

---

## 3. Skills 구조

### 3.1 디렉토리 레이아웃

```
.claude/skills/
├── webapp-testing/              # ✅ 기존
├── skill-creator/               # ✅ 기존
│
├── debugging-workflow/          # 🆕 P0
│   ├── SKILL.md                # ~300줄
│   ├── references/
│   │   └── log-patterns.md
│   └── scripts/
│       ├── analyze_logs.py
│       └── add_debug_logs.py
│
├── pre-work-research/           # 🆕 P0
│   ├── SKILL.md
│   ├── references/
│   │   └── oss-evaluation.md
│   └── scripts/
│       └── github_search.py
│
├── final-check-automation/      # 🆕 P0
│   ├── SKILL.md
│   └── scripts/
│       └── run_final_check.py
│
├── tdd-workflow/                # 🆕 P1
│   ├── SKILL.md
│   ├── assets/test-templates/
│   └── scripts/
│       ├── validate_red_phase.py
│       └── tdd_auto_cycle.py
│
├── code-quality-checker/        # 🆕 P1
│   ├── SKILL.md
│   └── scripts/
│       └── run_quality_check.py
│
├── phase-validation/            # 🆕 P1
│   ├── SKILL.md
│   └── scripts/
│       └── validate_phase.py
│
├── parallel-agent-orchestration/ # 🆕 P2
│   ├── SKILL.md
│   └── references/
│       └── agent-combinations.md
│
└── issue-resolution/            # 🆕 P2
    ├── SKILL.md
    └── scripts/
        └── fix_issue_flow.py
```

### 3.2 메타데이터 표준

```yaml
---
name: debugging-workflow
description: >
  디버깅 실패 시 자동 트리거. 로그 분석, DEBUGGING_STRATEGY.md 적용.
  키워드: "로그 분석", "debug", "실패", "오류"
version: 1.0.0
phase: [1, 2, 5]
auto_trigger: true
dependencies:
  - debugger (subagent)
token_budget: 2500
---
```

---

## 4. 자동 트리거 규칙

| Skill | 트리거 키워드 | Phase |
|-------|-------------|-------|
| `debugging-workflow` | 오류, 실패, debug, 로그 | 1, 2, 5 |
| `pre-work-research` | 신규 기능, 오픈소스, 라이브러리 | 0 |
| `final-check-automation` | E2E, 최종 검증, Phase 5 | 5 |
| `tdd-workflow` | TDD, 테스트 먼저, Red-Green | 1, 2 |
| `code-quality-checker` | 린트, 보안, 품질 검사 | 2.5 |

---

## 5. 마이그레이션 절차

### 5.1 Phase 1: P0 Skills (Week 1)

```bash
# 1. debugging-workflow 생성
python .claude/skills/skill-creator/scripts/init_skill.py debugging-workflow

# 2. SKILL.md 작성 (DEBUGGING_STRATEGY.md 통합)
# 3. scripts/ 구현 (analyze-logs 로직 이동)
# 4. 테스트

# 반복: pre-work-research, final-check-automation
```

### 5.2 Phase 2: P1 Skills (Week 2)

```bash
# tdd-workflow, code-quality-checker, phase-validation
```

### 5.3 Phase 3: P2 Skills (Week 3)

```bash
# parallel-agent-orchestration, issue-resolution
```

### 5.4 Phase 4: Commands Deprecation

```markdown
# 기존 Command에 경고 추가
⚠️ DEPRECATED: Use `debugging-workflow` skill instead.
This command will be removed in v5.0.0.
```

---

## 6. 구현 Task

### P0 (Week 1)
- [ ] Task 1: `debugging-workflow` SKILL.md 작성
- [ ] Task 2: `debugging-workflow` scripts 구현
- [ ] Task 3: `pre-work-research` 생성
- [ ] Task 4: `final-check-automation` 생성
- [ ] Task 5: 자동 트리거 테스트

### P1 (Week 2)
- [ ] Task 6: `tdd-workflow` 생성
- [ ] Task 7: `code-quality-checker` 생성
- [ ] Task 8: `phase-validation` 생성

### P2 (Week 3)
- [ ] Task 9: `parallel-agent-orchestration` 생성
- [ ] Task 10: `issue-resolution` 생성
- [ ] Task 11: 기존 Commands deprecated 표시

---

## 7. 성공 지표

| 지표 | 현재 | 목표 |
|------|------|------|
| Skills 수 | 2개 | 10개 |
| 자동 트리거율 | 0% | 80% |
| Commands 토큰 | ~4000 | ~400 (메타데이터) |

---

**Dependencies**: PRD-0026 (토큰 전략)
**Next**: PRD-0028 (TDD), PRD-0029 (GitHub Actions)

