# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Critical Instructions

### Core Rules
1. **Language**: User-facing output in Korean (한글). Technical terms (code, variables, GitHub) in English.
2. **Path Handling**: ALWAYS use absolute paths. Verify file existence before read/write.
3. **Validation**: NEVER skip phase validation. If validation fails, STOP and fix before proceeding.

### Project Context
- **Root**: `D:\AI\claude01`
- **Platform**: Windows 10/11 (PowerShell native)
- **Identity**: Meta-workflow system for Claude Code (methodology + automation tools, not product code)
- **Plugin Registry**: `.claude-plugin/registry.json`

---

## 2. Build & Test Commands

```powershell
# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=.claude/scripts --cov-report=term

# Run single test file
pytest tests/test_specific.py -v

# Phase validation (PowerShell - preferred on Windows)
.\scripts\validate-phase-0.ps1 NNNN    # PRD validation
.\scripts\validate-phase-0.5.ps1 NNNN  # Task list validation
.\scripts\validate-phase-1.ps1         # 1:1 test pairing check
.\scripts\validate-phase-2.ps1         # Test execution
.\scripts\validate-phase-3.ps1 v1.2.0  # Version & changelog
.\scripts\validate-phase-4.ps1         # Git ops validation
.\scripts\validate-phase-5.ps1         # E2E & security
.\scripts\validate-phase-6.ps1         # Deployment readiness

# Universal validator (Python - cross-platform)
python scripts/validate_phase_universal.py <phase> [args]
python scripts/validate_phase_universal.py 0 0001
python scripts/validate_phase_universal.py 2 --coverage 80

# Phase status check
.\scripts\phase-status.ps1

# Plugin management
python scripts/plugin_manager.py
```

---

## 3. Workflow Pipeline

Strict phase-gate workflow. Each phase must pass validation before proceeding.

| Phase | Action | Output | Validator |
| :--- | :--- | :--- | :--- |
| **0** | PRD Creation (8 sections) | `tasks/prds/NNNN-*.md` | `validate-phase-0.ps1 NNNN` |
| **0.5** | Task Breakdown | `tasks/NNNN-tasks-*.md` | `validate-phase-0.5.ps1 NNNN` |
| **1** | Implementation + 1:1 tests | `src/*`, `tests/*` | `validate-phase-1.ps1` |
| **2** | Test & Coverage | All tests pass | `validate-phase-2.ps1` |
| **2.5** | Code Review | Approval | `/parallel-review` (slash cmd) |
| **3** | Version Bump | `CHANGELOG.md` | `validate-phase-3.ps1 vX.Y.Z` |
| **4** | Git Commit/PR | PR Created | `validate-phase-4.ps1` |
| **5** | E2E & Security | Security Report | `validate-phase-5.ps1` |
| **6** | Deployment | Released | `validate-phase-6.ps1` |

> If validation fails, fix in current phase. Do not regress to previous phases.

---

## 4. Slash Commands

Available in `.claude/commands/`:

| Command | Purpose |
| :--- | :--- |
| `/create-prd` | Interactive PRD creation (Phase 0) |
| `/tdd` | TDD workflow - test first (Phase 1) |
| `/fix-issue` | Structured bug fix workflow |
| `/check` | Code quality checks |
| `/commit` | Conventional commit with emoji |
| `/changelog` | Update CHANGELOG.md |
| `/create-pr` | Create GitHub PR |
| `/create-docs` | Generate documentation |
| `/analyze-code` | Generate Mermaid class diagram |
| `/optimize` | Performance analysis |
| `/todo` | Manage project todos |
| `/issues` | GitHub 이슈 목록 및 상태 조회 |
| `/issue` | **[Multi-Agent]** 병렬 솔루션 검색 |
| `/issue-update` | 실패 분석 및 새 해결책 제안 |
| `/search` | 웹/GitHub 검색 및 추천 |
| `/parallel-research` | **[Multi-Agent]** 병렬 리서치 |
| `/parallel-review` | **[Multi-Agent]** 4-에이전트 코드 리뷰 |
| `/parallel-dev` | **[Multi-Agent]** 4-에이전트 병렬 개발 (Architect/Coder/Tester/Docs) |
| `/parallel-test` | **[Multi-Agent]** 4-에이전트 병렬 테스트 (Unit/Integration/E2E/Security) |

### Aiden Commands (작업 문서화)
| Command | Purpose |
| :--- | :--- |
| `/aiden-first` | 작업 시작 시 MD 파일에 상세 기록 |
| `/aiden-plan` | 계획 수립 및 문서화 |
| `/aiden-update` | 작업 진행 상황 업데이트 |
| `/aiden-summary` | 작업 요약 생성 |
| `/aiden-endtoend` | 전체 프로세스 문서화 |

---

## 5. Architecture

This is a **monorepo** containing multiple sub-projects with a shared workflow system:

```
D:\AI\claude01\
├── .claude/              # Claude Code extensions
│   ├── commands/         # Slash commands (*.md)
│   ├── agents/           # Agent definitions (33 agents)
│   ├── skills/           # Skills (skill-creator, webapp-testing)
│   └── settings.json     # Claude Code settings (bypass mode, statusline)
├── .claude-plugin/       # Plugin registry (wshobson, davila7, OneRedOak)
├── scripts/              # Phase validators (PowerShell + Python)
├── src/agents/           # Multi-agent system (LangGraph)
├── tasks/                # PRDs and task lists
│   └── prds/             # Product Requirement Documents
├── tests/                # Pytest test suite
├── docs/                 # Documentation
│   ├── WORKFLOWS/        # Workflow recipes
│   ├── GITHUB_WORKFLOW/  # GitHub integration guides
│   └── guides/           # Detailed guides (MULTI_AGENT_GUIDE.md)
└── [sub-projects]/       # Independent projects
```

### Key Sub-Projects
- `archive-analyzer/` - Media archive analysis tools
- `actiontracker/` - Action tracking system
- `handlogger/` - Hand logging application
- `keyplayer_manager/` - Key player management with Google Apps Script
- `table_tracker/` - Table tracking with Firebase
- `softsender/` - Soft message sender
- `commercial/` - Commercial project (Supabase + Vercel)
- `sso-system/`, `sso-nextjs/` - SSO authentication systems

---

## 6. GitHub Integration

```powershell
# Setup labels for repository
.\scripts\setup-github-labels.ps1

# Start work on issue (creates branch + draft PR)
.\scripts\github-issue-dev.ps1 <issue-number>
```

---

## 7. Multi-Agent System

병렬 멀티에이전트 워크플로우 (LangGraph + Claude Agent SDK):

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

| 모듈 | 설명 |
| :--- | :--- |
| `src/agents/parallel_workflow.py` | LangGraph Fan-Out/Fan-In 워크플로우 |
| `src/agents/dev_workflow.py` | 병렬 개발 워크플로우 (Architect/Coder/Tester/Docs) |
| `src/agents/test_workflow.py` | 병렬 테스트 워크플로우 (Unit/Integration/E2E/Security) |
| `src/agents/phase_validator.py` | Phase 병렬 검증기 |
| `src/agents/config.py` | 모델 티어링 (supervisor/lead/researcher/coder/reviewer/validator) |

### Model Tiering
- `supervisor`, `lead`, `researcher`, `coder`, `reviewer`: claude-sonnet-4
- `validator`: claude-haiku-3 (간단한 검증용)

상세 가이드: `docs/guides/MULTI_AGENT_GUIDE.md`, `docs/AGENTS_REFERENCE.md`

---

## 8. Quick Reference

- **Bypass Mode**: `.\start-claude-bypass.bat` (skips permission prompts)
- **Python**: 3.11+ required
- **Dependencies**: `anthropic>=0.40.0`, `langgraph`, `langchain-anthropic`
- **Test markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- **Agent count**: 33 agents in `.claude/agents/`
- **Plugins**: 7 active (python-development, javascript-typescript, debugging-toolkit, meta-development, workflow-reviews, phase-0/1/2)

---

## 9. Complex Feature Protocol

### Planning First
복잡한 기능은 코드 작성 전 계획 승인 필수. 계획 미승인 시 구현 금지.

### TDD Strict Order
| 순서 | 행동 | 금지 |
| :--- | :--- | :--- |
| 1. Red | 실패 테스트 작성 | ❌ 구현 금지 |
| 2. Commit | 테스트만 커밋 | ❌ 구현 포함 금지 |
| 3. Green | 최소 구현 | ❌ 테스트 수정 금지 |
| 4. Refactor | 정리 | ❌ 테스트 실패 금지 |

### Context Preservation
- `/fork`: 대화 분기 (계획 유지)
- `gh issue create --body-file plan.md`: 장기 보존
