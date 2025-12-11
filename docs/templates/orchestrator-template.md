# Orchestrator Agent Template

**Version**: 1.0.0 | **Source**: wsoptv, ggp_ojt_v2, archive-statistics

---

## Overview

프로젝트 전체 작업을 조율하는 최상위 에이전트 템플릿입니다.

```
┌─────────────────────────────────────┐
│          Orchestrator               │
│  - 작업 라우팅                       │
│  - 에러 핸들링                       │
│  - 글로벌 설정                       │
└────────────────┬────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│Domain A│  │Domain B│  │Domain C│
└────────┘  └────────┘  └────────┘
```

---

## Template

```markdown
# Orchestrator Agent

**Version**: 1.0.0 | **Project**: {PROJECT_NAME}

---

## Role

{PROJECT_NAME} 프로젝트의 모든 AI 작업을 조율하는 메인 에이전트입니다.

### Responsibilities

1. **라우팅**: 작업을 적절한 Domain Agent로 전달
2. **컨텍스트 관리**: 도메인 간 정보 공유
3. **에러 핸들링**: 실패 시 복구 전략 실행
4. **품질 검증**: 최종 결과물 검증

---

## Domain Agents

| Domain | Agent File | Responsibility |
|--------|------------|----------------|
| {DOMAIN_1} | `.claude/agents/{domain_1}-domain.md` | {DESCRIPTION_1} |
| {DOMAIN_2} | `.claude/agents/{domain_2}-domain.md` | {DESCRIPTION_2} |
| {DOMAIN_3} | `.claude/agents/{domain_3}-domain.md` | {DESCRIPTION_3} |

---

## Routing Rules

### Keyword-Based Routing

| Keywords | Target Domain | Priority |
|----------|---------------|----------|
| {KEYWORDS_1} | {DOMAIN_1} | 1 |
| {KEYWORDS_2} | {DOMAIN_2} | 2 |
| {KEYWORDS_3} | {DOMAIN_3} | 3 |

### File-Based Routing

| Path Pattern | Target Domain |
|--------------|---------------|
| `src/{domain_1}/` | {DOMAIN_1} |
| `src/{domain_2}/` | {DOMAIN_2} |
| `tests/` | All (테스트 관련) |

---

## Workflow

### Standard Flow

```
1. 작업 수신
     ↓
2. 컨텍스트 분석
     ↓
3. Domain 라우팅
     ↓
4. Domain Agent 실행
     ↓
5. 결과 검증
     ↓
6. 완료 보고
```

### Error Handling

```
실패 감지
    ↓
┌───────────────────────────────────┐
│ 실패 유형 판단                     │
├───────────────────────────────────┤
│ A) 일시적 오류 → 재시도 (최대 3회) │
│ B) 도메인 오류 → 다른 도메인 전환   │
│ C) 치명적 오류 → 사용자 알림       │
└───────────────────────────────────┘
```

---

## Context Loading

### 작업 전 필수 로딩

1. **Global**: `CLAUDE.md`
2. **Orchestrator**: `.claude/agents/orchestrator.md` (이 파일)
3. **Target Domain**: `.claude/agents/{domain}-domain.md`
4. **Block Rules**: `src/{domain}/AGENT_RULES.md` (해당 시)

### Context Budget

| Phase | Token Budget |
|-------|--------------|
| 분석 | 1,000 |
| 실행 | 3,000 |
| 검증 | 500 |

---

## Global Settings

### Branch Naming

```
feat/{domain}/issue-{N}-{description}
fix/{domain}/issue-{N}-{description}
```

### Commit Convention

```
{type}({domain}): {description}

Types: feat, fix, refactor, docs, test, chore
```

---

## DO / DON'T

### DO

- [ ] 작업 전 Domain Agent 문서 로딩
- [ ] 에러 발생 시 로그 수집
- [ ] 도메인 경계 존중

### DON'T

- [ ] 도메인 규칙 무시하고 직접 수정
- [ ] 에러 숨김 (반드시 보고)
- [ ] 컨텍스트 없이 작업 시작
```

---

## Customization Guide

1. **{PROJECT_NAME}**: 프로젝트 이름으로 교체
2. **{DOMAIN_N}**: 도메인 이름으로 교체 (예: auth, content, api)
3. **{KEYWORDS_N}**: 라우팅 키워드로 교체
4. **{DESCRIPTION_N}**: 도메인 설명으로 교체

---

## Examples

### wsoptv Orchestrator

- Domains: auth, content, stream, search, migration
- Routing: JWT/로그인 → auth, HLS/스트리밍 → stream

### archive-statistics Orchestrator

- Domains: scanner, progress, sync
- Routing: NAS/스캔 → scanner, 매칭/진행률 → progress

---

## Related

- [domain-agent-template.md](./domain-agent-template.md)
- [SUBREPO_ANALYSIS_REPORT.md](../SUBREPO_ANALYSIS_REPORT.md)
