# Agent 참조 가이드

**목적**: 에이전트 분류 및 활용법

**버전**: 8.0.0 | **업데이트**: 2026-02-15 | **PRD**: PRD-0031

---

## 에이전트 구조

| 계층 | 위치 | 개수 | 역할 |
|------|------|------|------|
| **내장** | Claude Code | 4개 | 기본 subagent |
| **커스텀** | `.claude/agents/` | 8개 | 전문 에이전트 |
| **스킬** | `.claude/skills/` | 48개 | 자동/수동 트리거 |
| **MCP** | `.claude.json` | 1개 | 외부 도구 연동 |

---

## 1. 내장 Subagent (4개)

| Agent | 용도 | 호출 |
|-------|------|------|
| `general-purpose` | 복잡한 다단계 작업 | `Task(subagent_type="general-purpose")` |
| `Explore` | 코드베이스 빠른 탐색 | `Task(subagent_type="Explore")` |
| `Plan` | 구현 계획 설계 | 자동 (Plan Mode) |
| `debugger` | 버그 분석/수정 | `Task(subagent_type="debugger")` |

---

## 2. 커스텀 에이전트 (8개)

### Tier 2: DOMAIN (5개) - 도메인별 전문

| Agent | 용도 | 모델 |
|-------|------|------|
| `devops-engineer` | CI/CD, 인프라, K8s | sonnet |
| `cloud-architect` | 클라우드, 네트워크 | sonnet |
| `database-specialist` | DB 설계, 최적화 | sonnet |
| `data-specialist` | 데이터, ML 파이프라인 | sonnet |
| `ai-engineer` | LLM, RAG 시스템 | sonnet |

### Tier 4: TOOLING (3개) - 도구 전문

| Agent | 용도 | 모델 |
|-------|------|------|
| `github-engineer` | GitHub 워크플로우 | haiku |
| `claude-expert` | Claude Code, MCP, 에이전트 | opus |
| `catalog-engineer` | WSOPTV 카탈로그/제목 생성 (Block F/G) | sonnet |

**OMC 대체 에이전트**: 삭제된 11개 로컬 에이전트의 기능은 OMC 에이전트로 대체됩니다: architect, code-reviewer, qa-tester, security-reviewer, designer, writer, executor (TypeScript/Python/Frontend/Backend/Fullstack 포함)

---

## 3. MCP 서버 (1개)

### 설치된 MCP

| MCP | 패키지 | 용도 |
|-----|--------|------|
| `code-reviewer` | `@vibesnipe/code-review-mcp` | AI 코드 리뷰 |

### 내장 기능으로 대체됨

| 기존 MCP | 대체 내장 기능 |
|----------|---------------|
| `context7` (기술 문서) | `WebSearch` + `WebFetch` |
| `sequential-thinking` (추론) | `Extended Thinking` (Claude 4 내장) |
| `taskmanager` (작업 관리) | `TodoWrite` / `TodoRead` |
| `exa` (웹 검색) | `WebSearch` |

### 추가 권장

| MCP | 패키지 | 용도 |
|-----|--------|------|
| `github` | `@anthropic/mcp-server-github` | GitHub API 통합 |

### 설치 방법

```bash
# 설치
claude mcp add <name> -- npx -y <package>

# 목록 확인
claude mcp list

# 제거
claude mcp remove <name>
```

---

## 4. 에이전트 사용 가이드

### 호출 방법

```
"Use the [agent-name] agent to [task]"

예:
- "Use the code-reviewer agent to review this PR"
- "Use the architect agent to design the API"
- "Use the test-engineer agent to write E2E tests"
```

### 선택 기준

| 상황 | 추천 에이전트 |
|------|--------------|
| 코드 작성 후 리뷰 | code-reviewer |
| 설계 결정 필요 | architect |
| 버그 분석 | debugger |
| 테스트 작성 | qa-tester |
| 보안 점검 | security-reviewer |
| 문서 작성 | writer |
| React/UI 개발 | designer |
| API 개발 | executor |
| 전체 기능 개발 | executor-high |
| CI/CD, K8s | `devops-engineer` |
| AWS/Azure/GCP | `cloud-architect` |
| DB 설계/최적화 | `database-specialist` |
| 데이터/ML | `data-specialist` |
| LLM/RAG | `ai-engineer` |
| TS 고급 타입 | executor |
| Python 고급 | executor |
| GitHub 워크플로우 | `github-engineer` |
| Claude Code 설정 | `claude-expert` |
| WSOPTV 카탈로그 | `catalog-engineer` |

---

## 5. 통합 이력 (PRD-0031)

### 삭제된 에이전트 (→ 내장 기능 대체)

| 에이전트 | 대체 기능 |
|---------|---------|
| `context7-engineer` | `WebSearch` / `WebFetch` 내장 |
| `exa-search-specialist` | `WebSearch` 내장 |
| `seq-engineer` | `Extended Thinking` 내장 |
| `taskmanager-planner` | `TodoWrite` 내장 |

### 통합된 에이전트

| 삭제 | 통합 대상 |
|------|----------|
| `typescript-pro`, `typescript-expert` | → `typescript-dev` |
| `database-architect`, `database-optimizer`, `supabase-engineer` | → `database-specialist` |
| `data-scientist`, `data-engineer`, `ml-engineer` | → `data-specialist` |
| `deployment-engineer`, `devops-troubleshooter`, `kubernetes-architect`, `terraform-specialist` | → `devops-engineer` |
| `frontend-developer`, `UI_UX-Designer`, `design-review` | → `frontend-dev` |
| `backend-architect`, `architect-reviewer`, `graphql-architect` | → `architect` |
| `test-automator`, `playwright-engineer`, `tdd-orchestrator` | → `test-engineer` |
| `pragmatic-code-review` | → `code-reviewer` |
| `api-documenter`, `docs-architect` | → `docs-writer` |
| `cloud-architect`, `network-engineer` | → `cloud-architect` |
| `agent-expert`, `command-expert`, `mcp-expert`, `prompt-engineer` | → `claude-expert` |

### 백업 위치

삭제된 에이전트: `.claude/agents.backup/`

---

## 버전 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| 8.1.0 | 2026-02-18 | /auto v21.0: 내부 Skill() 호출 제거 (ralplan/ralph/ultraqa → Agent Teams 단일 패턴) |
| 8.0.0 | 2026-02-15 | OMC 중복 제거 (19개 → 8개: 11개 에이전트를 OMC 플러그인으로 대체) |
| 7.1.0 | 2026-02-13 | 스킬 개수 동기화 (47개 → 48개: daily 스킬 추가 반영) |
| 7.0.0 | 2026-02-05 | 모델 정보 동기화 (code-reviewer/docs-writer/github-engineer: sonnet→haiku), 스킬 개수 47개 반영 |
| 6.8.0 | 2026-01-03 | 스킬 개수 정정 (16개 → 18개: 실제 파일 개수와 동기화) |
| 6.7.0 | 2025-12-20 | ACE-FCA 스킬 제거 시도 (context-compaction, research-validation) - 실제 미삭제 |
| 6.6.0 | 2025-12-20 | ACE-FCA 스킬 추가 (17개 → 19개: context-compaction, research-validation) |
| 6.5.0 | 2025-12-20 | 스킬 개수 수정 (15개 → 17개: command-analytics, google-workspace 추가) |
| 6.4.0 | 2025-12-17 | 스킬 개수 수정 (13개 → 15개: supabase-integration, vercel-deployment 추가) |
| 6.3.0 | 2025-12-16 | MCP 정리 (5개 → 1개), 내장 기능 대체 문서화 |
| 6.2.0 | 2025-12-16 | MCP 5개로 업데이트 (exa, code-reviewer 추가) |
| 6.1.0 | 2025-12-12 | `catalog-engineer` 추가 (18 → 19개) |
| 6.0.0 | 2025-12-11 | PRD-0031 적용: 50개 → 18개 통합, MCP 분리 |
| 5.0.0 | 2025-12-11 | plugins/ → agents/ 이동, 구조 개편 |
