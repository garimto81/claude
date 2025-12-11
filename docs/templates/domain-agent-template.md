# Domain Agent Template

**Version**: 1.0.0 | **Source**: archive-statistics, wsoptv, ggp_ojt_v2

---

## Overview

특정 도메인의 비즈니스 로직을 담당하는 에이전트 템플릿입니다.

```
┌─────────────────────────────────────┐
│        Domain Agent                  │
│  - 도메인 규칙                       │
│  - Block 관리                        │
│  - 매칭 전략                         │
└────────────────┬────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│Block 1 │  │Block 2 │  │Block 3 │
└────────┘  └────────┘  └────────┘
```

---

## Template

```markdown
# {DOMAIN_NAME} Domain Agent

**Version**: 1.0.0 | **Last Updated**: {DATE}

---

## Domain Scope

### Responsibility

{DOMAIN_DESCRIPTION}

### File Scope

| Directory | Purpose |
|-----------|---------|
| `src/{domain}/` | 핵심 로직 |
| `src/{domain}/services/` | 비즈니스 서비스 |
| `src/{domain}/models/` | 데이터 모델 |
| `tests/test_{domain}/` | 테스트 |

### Out of Scope

- {OUT_OF_SCOPE_1}
- {OUT_OF_SCOPE_2}

---

## Blocks

| Block | Files | Responsibility |
|-------|-------|----------------|
| {BLOCK_1} | `{files_1}` | {BLOCK_DESC_1} |
| {BLOCK_2} | `{files_2}` | {BLOCK_DESC_2} |
| {BLOCK_3} | `{files_3}` | {BLOCK_DESC_3} |

---

## Key Concepts

### {CONCEPT_1}

{CONCEPT_1_DESCRIPTION}

```
{CONCEPT_1_DIAGRAM_OR_CODE}
```

### {CONCEPT_2}

{CONCEPT_2_DESCRIPTION}

---

## Strategies / Algorithms

### {STRATEGY_NAME}

**목적**: {STRATEGY_PURPOSE}

| 전략 | 우선순위 | 조건 | 예시 |
|------|----------|------|------|
| {STRATEGY_1} | 1.0 | {CONDITION_1} | {EXAMPLE_1} |
| {STRATEGY_2} | 0.9 | {CONDITION_2} | {EXAMPLE_2} |
| {STRATEGY_3} | 0.8 | {CONDITION_3} | {EXAMPLE_3} |

### Implementation Location

- **File**: `src/{domain}/services/{service}.py`
- **Function**: `{function_name}()`
- **Line**: ~{LINE_NUMBER}

---

## Known Issues

### Issue #{N}: {ISSUE_TITLE}

**증상**: {SYMPTOM}

**원인**: {ROOT_CAUSE}

**해결**: {SOLUTION}

**파일**: `{FILE_PATH}:{LINE}`

---

## Debugging

### Debug Flag

```python
# 환경변수로 디버그 모드 활성화
DEBUG_{DOMAIN}_ENABLED=true

# 코드에서 확인
import os
DEBUG = os.getenv("DEBUG_{DOMAIN}_ENABLED", "false").lower() == "true"
```

### Key Log Points

| 위치 | 로그 | 확인 내용 |
|------|------|-----------|
| {LOCATION_1} | `[{DOMAIN}] {LOG_1}` | {CHECK_1} |
| {LOCATION_2} | `[{DOMAIN}] {LOG_2}` | {CHECK_2} |

---

## DO / DON'T

### DO

- [ ] Block 범위 내에서만 수정
- [ ] 전략 추가 시 우선순위 명시
- [ ] Known Issues 섹션 업데이트

### DON'T

- [ ] 다른 도메인 파일 직접 수정
- [ ] 전략 우선순위 무단 변경
- [ ] 디버그 로그 프로덕션 배포

---

## Test Policy

| 유형 | 필수 여부 | 커버리지 목표 |
|------|-----------|---------------|
| Unit | 필수 | 80% |
| Integration | 권장 | 60% |
| E2E | 선택 | - |

### Test Location

```
tests/test_{domain}/
├── test_{block_1}.py
├── test_{block_2}.py
└── fixtures/
```

---

## Related

- **Orchestrator**: `.claude/agents/orchestrator.md`
- **Block Rules**: `src/{domain}/AGENT_RULES.md`
- **API Spec**: `docs/api/{domain}.md`
```

---

## Customization Guide

1. **{DOMAIN_NAME}**: 도메인 이름 (예: Progress, Auth, Content)
2. **{BLOCK_N}**: 블럭 이름 (예: video, hand, dashboard)
3. **{STRATEGY_N}**: 매칭/처리 전략
4. **{CONCEPT_N}**: 도메인 핵심 개념

---

## Examples

### archive-statistics: Progress Domain

```markdown
# Progress Domain Agent

## Strategies (폴더-카테고리 매칭)

| 전략 | 점수 | 예시 |
|------|------|------|
| exact | 1.0 | "GOG" == "GOG" |
| prefix | 0.9 | "PAD S12" starts with "PAD " |
| word | 0.8 | "wsop" in category_words |

## Known Issues

### Issue #3: 폴더-카테고리 매칭 문제
**증상**: GGMillions 폴더가 매칭되지 않음
**원인**: DB 카테고리 누락
**해결**: reverse_word 전략 추가
```

### wsoptv: Auth Domain

```markdown
# Auth Domain Agent

## Blocks

| Block | Files | Responsibility |
|-------|-------|----------------|
| login | `src/auth/login.ts` | JWT 발급 |
| session | `src/auth/session.ts` | 세션 관리 |
| guard | `src/auth/guard.ts` | 라우트 보호 |
```

---

## Related

- [orchestrator-template.md](./orchestrator-template.md)
- [SUBREPO_ANALYSIS_REPORT.md](../SUBREPO_ANALYSIS_REPORT.md)
