# Workflow Reference Guide

이 문서는 CLAUDE.md의 상세 워크플로우 정보를 담고 있습니다.

---

## 1. Phase Pipeline 상세

### Causal Workflow Pipeline

Strict phase-gate workflow. Each phase is the **Cause** for the next phase's **Effect**.

| Phase | Input (Cause) | Action (Process) | Output (Effect) | Validator (Gatekeeper) |
| :--- | :--- | :--- | :--- | :--- |
| **0** | User Request | PRD Creation (8 sections) | `tasks/prds/NNNN-*.md` | `validate-phase-0.ps1 NNNN` |
| **0.5** | PRD | Task Breakdown | `tasks/NNNN-tasks-*.md` | `validate-phase-0.5.ps1 NNNN` |
| **1** | Task List | Implementation + 1:1 tests | `src/*`, `tests/*` | `validate-phase-1.ps1` |
| **2** | Impl Code | Test & Coverage | All tests pass | `validate-phase-2.ps1` |
| **2.5** | Verified Code | Code Review | Approval | `/parallel-review` |
| **3** | Approval | Version Bump | `CHANGELOG.md` | `validate-phase-3.ps1 vX.Y.Z` |
| **4** | Versioned Code | Git Commit/PR | PR Created | `validate-phase-4.ps1` |
| **5** | PR | E2E & Security | Security Report | `validate-phase-5.ps1` |
| **6** | Passed PR | Deployment | Released | `validate-phase-6.ps1` |

> **Feedback Loop**: If validation fails, return to the **Action** step of the *current* phase.

---

## 2. Multi-Agent System 상세

### 병렬 워크플로우 (LangGraph + Claude Agent SDK)

```python
# 병렬 태스크 실행
from src.agents.parallel_workflow import run_parallel_task
result = run_parallel_task("프로젝트 분석", num_agents=3)

# 병렬 개발 워크플로우
from src.agents.dev_workflow import run_dev_workflow
result = run_dev_workflow("사용자 인증 기능 구현")

# 병렬 테스트 워크플로우
from src.agents.test_workflow import run_test_workflow
result = run_test_workflow("src/auth", scope="전체")

# CLI 실행
python src/agents/parallel_workflow.py "프로젝트 구조 분석"
python src/agents/dev_workflow.py "새 API 엔드포인트 추가"
python src/agents/test_workflow.py "src/api" "전체"
```

### Core Modules (`src/agents/`)

| 모듈 | 역할 | 핵심 요소 |
|------|------|-----------|
| `config.py` | 모델 티어링 & 에이전트 설정 | `AGENT_MODEL_TIERS`, `AgentConfig`, `PHASE_AGENTS` |
| `parallel_workflow.py` | Fan-Out/Fan-In 워크플로우 | `run_parallel_task()`, `run_parallel_task_async()` |
| `dev_workflow.py` | 병렬 개발 워크플로우 | Architect/Coder/Tester/Docs 에이전트 |
| `test_workflow.py` | 병렬 테스트 워크플로우 | Unit/Integration/E2E/Security 에이전트 |
| `utils.py` | 유틸리티 | `parse_subtasks_from_text()`, `ExecutionResult` |

### Model Tiering
- `supervisor`, `lead`, `researcher`, `coder`, `reviewer`: claude-sonnet-4
- `validator`: claude-haiku-3 (간단한 검증용)

---

## 3. Agent Evolution System 상세

Agent 사용 추적 및 피드백 기반 자동 개선 시스템 (Langfuse 기반).

```bash
# 시작
cd .claude/evolution
cp .env.example .env && docker-compose up -d

# 대시보드: http://localhost:3000
```

```python
# Agent 추적
from .claude.evolution.scripts.track_agent_usage import get_tracker
tracker = get_tracker()

with tracker.track("context7-engineer", phase="Phase 0", task="Verify docs"):
    result = agent.run()

tracker.collect_feedback(agent="context7-engineer", rating=5, effectiveness=0.9)
```

| 스크립트 | 용도 |
| :--- | :--- |
| `track_agent_usage.py` | Agent 실행 추적 |
| `collect_feedback.py` | CLI 피드백 수집 |
| `analyze_quality.py` | 품질 분석 |
| `llm_judge.py` | LLM 기반 평가 |

---

## 4. Slash Commands 전체 목록

### Planning (Phase 0 - 0.5)
| Command | Purpose |
| :--- | :--- |
| `/create-prd` | Interactive PRD creation |
| `/aiden-plan` | 계획 수립 및 문서화 |
| `/aiden-first` | 작업 시작 시 상세 기록 |
| `/issues` | GitHub 이슈 목록 조회 |
| `/todo` | 할 일 목록 관리 |

### Coding (Phase 1)
| Command | Purpose |
| :--- | :--- |
| `/tdd` | TDD workflow - test first |
| `/fix-issue` | Structured bug fix workflow |
| `/check` | Code quality checks |
| `/parallel-dev` | **[Multi-Agent]** 4-에이전트 병렬 개발 |

### Verifying (Phase 2 - 2.5)
| Command | Purpose |
| :--- | :--- |
| `/parallel-test` | **[Multi-Agent]** 4-에이전트 병렬 테스트 |
| `/parallel-review` | **[Multi-Agent]** 4-에이전트 코드 리뷰 |
| `/optimize` | Performance analysis |
| `/analyze-code` | Generate Mermaid class diagram |

### Ops (Phase 3 - 6)
| Command | Purpose |
| :--- | :--- |
| `/commit` | Conventional commit with emoji |
| `/changelog` | Update CHANGELOG.md |
| `/create-pr` | Create GitHub PR |
| `/create-docs` | Generate documentation |

### Issue Management
| Command | Purpose |
| :--- | :--- |
| `/issue` | GitHub 이슈 등록 |
| `/issues` | 이슈 목록 조회 |
| `/issue-update` | 실패 분석 및 새 해결책 제안 |
| `/fix-issue` | 이슈 해결 워크플로우 |

### Research & Analysis
| Command | Purpose |
| :--- | :--- |
| `/parallel-research` | **[Multi-Agent]** 병렬 리서치 (오픈소스 우선) |
| `/optimize` | 성능 분석 및 최적화 |
| `/analyze-logs` | 로그 분석 및 문제 진단 |
| `/api-test` | API 엔드포인트 테스트 |
| `/analyze-code` | Mermaid 클래스 다이어그램 생성 |

### Documentation
| Command | Purpose |
| :--- | :--- |
| `/aiden-update` | 작업 진행 상황 업데이트 |
| `/aiden-summary` | 작업 요약 생성 |
| `/create-docs` | 문서 자동 생성 |

### Auto Workflow Support
| Command | Purpose |
| :--- | :--- |
| `/pre-work` | 사전 조사 (솔루션 검색 + 중복 확인) |
| `/final-check` | 최종 검증 (E2E 100% + 보고서) |

---

## 5. TDD Strict Order

| 순서 | 행동 | 금지 |
| :--- | :--- | :--- |
| 1. Red | 실패 테스트 작성 | ❌ 구현 금지 |
| 2. Commit | 테스트만 커밋 | ❌ 구현 포함 금지 |
| 3. Green | 최소 구현 | ❌ 테스트 수정 금지 |
| 4. Refactor | 정리 | ❌ 테스트 실패 금지 |

---

## 6. Troubleshooting

| 증상 | 원인 | 해결 |
|------|------|------|
| `ANTHROPIC_API_KEY not set` | 환경변수 미설정 | `$env:ANTHROPIC_API_KEY = "key"` |
| Phase 검증 실패 | 이전 Phase 미완료 | `.\scripts\phase-status.ps1`로 확인 |
| Hook 차단 (CRITICAL) | CLAUDE.md 규칙 위반 | 메시지의 제안 따르기 |
| Multi-Agent 실행 오류 | 의존성 미설치 | `pip install langgraph langchain-anthropic` |
| 테스트 실패 | 환경 불일치 | `pytest tests/ -v --tb=short` |
