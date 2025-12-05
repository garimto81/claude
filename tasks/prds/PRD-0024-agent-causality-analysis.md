# PRD-0024: 에이전트 인과관계 분석 및 정리

**Version**: 1.2.0 | **Created**: 2025-12-05 | **Updated**: 2025-12-05 | **Status**: In Progress
**Issue**: [#24](https://github.com/garimto81/archive-analyzer/issues/24)

---

## 1. 개요

### 1.1 목적
CLAUDE.md 및 워크플로우에 기록된 에이전트와 실제 존재하는 에이전트 간의 **인과관계 분석** 및 **미사용 에이전트 처리 방안** 수립

### 1.2 배경 (초기 상태)
| 구분 | 초기 | 현재 | 위치 |
|------|------|------|------|
| 내장 subagent | 4개 | 4개 | Claude Code 시스템 |
| 로컬 에이전트 | 56개 | **49개** ✅ | `.claude/plugins/*/agents/*.md` |
| 아카이브 | 0개 | **6개** ✅ | `.claude/plugins.archive/` |
| 워크플로우 참조 | 12개 | **7개** | `.claude/commands/*.md` |

### 1.3 문제점 및 진행 상황
| 문제 | 상태 | 비고 |
|------|------|------|
| "내장 37개" 오류 명시 | ⚠️ 대기 | CLAUDE.md 수정 필요 |
| 중복 에이전트 | ✅ 해결 | 30개 중복 → 제거 완료 |
| 미사용 에이전트 | ✅ 진행중 | 6개 아카이브 이동 |

---

## 2. 분석 결과

### 2.1 Claude Code 공식 내장 Subagent (4개)

| 에이전트 | 기능 | 도구 | 특성 |
|---------|------|------|------|
| `general-purpose` | 복잡한 다단계 작업 | 모든 도구 | 범용 |
| `Explore` | 코드베이스 탐색 | Glob, Grep, Read | 읽기 전용, Haiku |
| `Plan` | 계획 수립 | 읽기 도구만 | Plan Mode 전용 |
| `debugger` | 버그 분석/수정 | Read, Edit, Bash, Grep | 순차 필수 |

> **참고**: `claude-code-guide`, `statusline-setup`은 **슬래시 커맨드**이며 subagent가 아님

### 2.2 로컬 에이전트 분류 (v1.2 업데이트)

#### A. 워크플로우에서 직접 참조 (7개) - **활성**

| 에이전트 | 참조 위치 | Phase | 위치 |
|---------|----------|-------|------|
| `debugger` | analyze-logs, fix-issue, final-check, tdd | 문제 시 | phase-1-development |
| `backend-architect` | api-test.md | 1 | phase-1-development |
| `code-reviewer` | check, optimize, fix-issue, tdd | 1, 2.5 | phase-2-testing |
| `test-automator` | fix-issue, tdd | 2 | phase-2-testing |
| `security-auditor` | check, api-test | 5 | phase-2-testing |
| `playwright-engineer` | final-check | 2, 5 | phase-2-testing |
| `context7-engineer` | pre-work | 0, 1 | phase-0-planning |

#### B. CLAUDE.md에만 언급 (21개) - **대기**

문서에 언급되었으나 슬래시 커맨드에서 직접 호출되지 않음:
```
# Phase 0
seq-engineer, exa-search-specialist, taskmanager-planner, task-decomposition-expert

# Phase 1
frontend-developer, fullstack-developer, typescript-expert, mobile-developer

# Phase 2.5-6
architect-reviewer, deployment-engineer, devops-troubleshooter, cloud-architect

# 전문 분야
python-pro, graphql-architect, supabase-engineer, performance-engineer,
github-engineer, database-architect, database-optimizer, context-manager
```

#### C. 정의만 존재 (21개) - **미사용 후보**

`.claude/plugins/`에 정의되어 있으나 어디서도 참조되지 않음:
```
# AI/ML
ai-engineer, ml-engineer, data-engineer, data-scientist, prompt-engineer

# 개발 도구
javascript-pro, typescript-pro, fastapi-pro

# 인프라
kubernetes-architect, terraform-specialist, network-engineer

# 메타/문서화
agent-expert, command-expert, mcp-expert, docs-architect, api-documenter

# 기타
dx-optimizer, legacy-modernizer, observability-engineer, tdd-orchestrator,
design-review, pragmatic-code-review, UI_UX-Designer
```

#### D. 아카이브 완료 (6개)

`.claude/plugins.archive/`로 이동됨:
```
cli-ui-designer, django-pro, docusaurus-expert,
hybrid-cloud-architect, temporal-python-pro, tutorial-engineer
```

### 2.3 중복 에이전트 (✅ 해결됨)

| 에이전트 | 이전 중복 | 현재 위치 |
|---------|----------|----------|
| `code-reviewer` | 4곳 | ✅ phase-2-testing |
| `cloud-architect` | 3곳 | ✅ phase-6-deployment |
| `deployment-engineer` | 3곳 | ✅ phase-6-deployment |
| `frontend-developer` | 3곳 | ✅ phase-1-development |
| `security-auditor` | 3곳 | ✅ phase-2-testing |

> **참고**: Git status에서 D (deleted) 상태인 30개 파일이 중복 제거 결과

### 2.4 MCP 연동 에이전트

| 로컬 에이전트 | MCP 도구 | 상태 |
|--------------|---------|------|
| `exa-search-specialist` | `mcp__exa__search` | 활성 |
| `context-manager` | `mcp__mem0__*` | 대기 |
| `context7-engineer` | `mcp__ref__search` | 활성 |

---

## 3. 솔루션 비교 분석

### 3.1 검색 결과 요약

병렬 검색으로 분석한 에이전트 관리 솔루션:

| 솔루션 | 장점 | 단점 | 작업량 |
|--------|------|------|--------|
| **A. YAML Registry + LangGraph** ⭐ | 기존 코드 재활용, 점진적 마이그레이션 | 레지스트리 구현 필요 | 중 |
| **B. CrewAI 마이그레이션** | Role-based 직관성, 빠른 프로토타이핑 | 전면 재작성 필요 | 대 |
| **C. 단순화 (내장만)** | 유지보수 쉬움, 복잡도 감소 | 전문성 손실 | 소 |

### 3.2 권장 솔루션: YAML Agent Registry

**핵심 발견**: Claude Code의 `subagent_type` 파라미터는 **공식 미정의**. 로컬 에이전트는 자동 위임 또는 명시적 요청으로만 호출 가능.

```yaml
# .claude/agents.yaml (신규 레지스트리)
agents:
  # Tier 1: 내장 subagent (직접 호출 가능)
  debugger:
    type: builtin
    subagent_type: debugger

  # Tier 2: 로컬 에이전트 (LangGraph 실행)
  backend-architect:
    type: local
    prompt_file: .claude/plugins/backend-development/agents/backend-architect.md
    model: sonnet
    tools: [Read, Write, Edit, Bash]

  # Tier 3: MCP 연동
  exa-search:
    type: mcp
    server: exa
    tool: search
```

**계층 구조**:
```
Master Supervisor (general-purpose)
├── Phase 0 Team (Plan + Explore)
│   └── context7-engineer, exa-search (MCP)
├── Phase 1 Team (general-purpose)
│   └── backend-architect, frontend-developer (Local)
├── Phase 2 Team (debugger)
│   └── test-automator, playwright-engineer (Local)
└── Phase 5 Team (general-purpose)
    └── security-auditor, deployment-engineer (Local)
```

**참고 자료**:
- [langgraph-bigtool](https://github.com/langchain-ai/langgraph-bigtool) - 대규모 도구 관리
- [LangGraph Multi-Agent Workflows](https://blog.langchain.com/langgraph-multi-agent-workflows/)

---

## 4. 세부 구현 방안

### 4.1 CLAUDE.md 섹션 4 수정

**기존**:
```markdown
## 4. Agents (내장 Subagent 중심)
Claude Code **내장 subagent 37개**를 활용.
```

**변경**:
```markdown
## 4. Agents

### 4.1 내장 Subagent (4개)
| 에이전트 | 용도 | 호출 |
|---------|------|------|
| `general-purpose` | 복잡한 다단계 작업 | Task(subagent_type="general-purpose") |
| `Explore` | 코드베이스 탐색 | Task(subagent_type="Explore") |
| `Plan` | 계획 수립 | 자동 (Plan Mode) |
| `debugger` | 버그 분석/수정 | Task(subagent_type="debugger") |

### 4.2 로컬 에이전트 (12개 활성)
`.claude/plugins/*/agents/*.md`에 정의된 프로젝트 맞춤형 에이전트.

| 에이전트 | Phase | 용도 |
|---------|-------|------|
| `frontend-developer` | 1 | React/Next.js 컴포넌트 |
| `backend-architect` | 1 | API 설계 |
| ... |

> 전체 목록: `docs/AGENTS_REFERENCE.md`

### 4.3 MCP 연동 에이전트 (3개)
| 에이전트 | MCP 도구 |
|---------|---------|
| `exa-search-specialist` | `mcp__exa__search` |
| `context7-engineer` | `mcp__ref__search` |
| `context-manager` | `mcp__mem0__*` |
```

### 3.2 로컬 에이전트 정리

#### Phase 1: 중복 제거
- 중복 정의된 5개 에이전트 → 대표 위치 1곳만 유지
- 나머지 → 심볼릭 링크 또는 삭제

#### Phase 2: 미사용 아카이브
```powershell
# 미사용 23개 → .claude/plugins.archive/로 이동
mkdir .claude/plugins.archive
mv .claude/plugins/meta-development/agents/agent-expert.md .claude/plugins.archive/
...
```

#### Phase 3: 활성 에이전트 문서화
- `docs/AGENTS_REFERENCE.md` 재구성
- 활성 12개 + 대기 21개 = 33개 문서화
- Phase별 권장 에이전트 테이블

### 3.3 워크플로우 인과관계 다이어그램

```
                    ┌─────────────────┐
                    │   사용자 요청    │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            ↓                ↓                ↓
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │   PRE_WORK    │ │     IMPL      │ │  FINAL_CHECK  │
    │   (Phase 0)   │ │  (Phase 1-2)  │ │  (Phase 3-6)  │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │                 │                 │
    ┌───────┴───────┐ ┌───────┴───────┐ ┌───────┴───────┐
    │ 내장          │ │ 로컬          │ │ 로컬          │
    │ - Explore     │ │ - frontend-   │ │ - playwright- │
    │ - Plan        │ │   developer   │ │   engineer    │
    │               │ │ - backend-    │ │ - security-   │
    │ 로컬          │ │   architect   │ │   auditor     │
    │ - context7-   │ │ - test-       │ │               │
    │   engineer    │ │   automator   │ │ 내장          │
    │ - exa-search- │ │               │ │ - debugger    │
    │   specialist  │ │ 내장          │ │               │
    │               │ │ - debugger    │ │               │
    │               │ │ - general-    │ │               │
    │               │ │   purpose     │ │               │
    └───────────────┘ └───────────────┘ └───────────────┘
```

---

## 5. 작업 항목

### 5.1 Phase 1: 중복 제거 및 아카이브 (✅ 완료)

- [x] 중복 에이전트 5개 대표 위치 결정 → 30개 파일 삭제
- [x] `.claude/plugins.archive/` 디렉토리 생성
- [x] 미사용 에이전트 6개 이동 완료

### 5.2 Phase 2: 문서 수정 (✅ 완료)

- [x] CLAUDE.md 섹션 4 재구성 (내장/로컬/MCP 분리)
- [x] "내장 subagent 37개" → "내장 4개 + 로컬 7개(활성) + MCP 3개" 수정
- [x] `docs/AGENTS_REFERENCE.md` 활성/대기/미사용 분류 추가 (v2.0.0)

### 5.3 Phase 3: YAML Registry 구축 (선택적)

> **결정 필요**: YAML Registry 구현 여부. 현재 로컬 에이전트는 자동 위임으로만 호출 가능.

- [ ] `.claude/agents.yaml` 레지스트리 파일 생성
- [ ] 내장 4개 + 로컬 활성 7개 + MCP 3개 정의
- [ ] `src/agents/registry.py` 로더 구현

### 5.4 Phase 4: 검증

- [ ] CLAUDE.md 정확성 검증
- [ ] 슬래시 커맨드 동작 테스트
- [ ] PR 생성 및 리뷰
- [ ] Git 변경사항 커밋 (삭제된 30개 파일)

---

## 6. 성공 기준

| 기준 | 초기 | 현재 | 목표 | 상태 |
|------|------|------|------|------|
| 내장 에이전트 명시 | "37개" | **"4개"** | "4개" | ✅ |
| 로컬 에이전트 | 56개 | **49개** | 49개 | ✅ |
| 중복 에이전트 | 30개 | **0개** | 0개 | ✅ |
| 미사용 아카이브 | 혼재 | **6개** | 21개 | ⏳ |
| 문서 정확성 | ~70% | **~95%** | 100% | ✅ |

---

## 7. 위험 및 완화

| 위험 | 영향 | 완화 방안 |
|------|------|----------|
| 아카이브 후 필요한 에이전트 발견 | 중 | 아카이브에서 복원 가능 |
| 심볼릭 링크 Windows 호환성 | 낮 | 직접 복사로 대체 |
| 기존 워크플로우 중단 | 높 | 활성 에이전트는 위치 유지 |

---

## 8. 참고 자료

- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents.md)
- [LangGraph Multi-Agent Workflows](https://blog.langchain.com/langgraph-multi-agent-workflows/)
- [langgraph-bigtool](https://github.com/langchain-ai/langgraph-bigtool) - 대규모 도구 관리
- [CrewAI Documentation](https://docs.crewai.com/)
- [CLAUDE.md v3.5.0](D:\AI\claude01\CLAUDE.md)
- [docs/AGENTS_REFERENCE.md](D:\AI\claude01\docs\AGENTS_REFERENCE.md)
