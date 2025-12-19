# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MAD Framework (Multi-Agent Debate) is a Python/TypeScript hybrid project for conducting structured debates between multiple LLM agents. It has two main components:

1. **Python Core** (`src/mad/`): LangGraph-based debate orchestration library
2. **Electron Desktop App** (`desktop/`): React + Electron UI for browser-based LLM automation

## Build & Development Commands

### Python Core

```bash
# Setup (uses uv)
uv sync --all-extras

# Run single test (recommended)
pytest tests/unit/test_config.py -v

# Run all tests
pytest tests/ -v

# Lint
ruff check src/

# Type check
mypy src/
```

### Desktop App (Electron + React)

```powershell
cd D:\AI\claude01\mad_framework\desktop

# Install dependencies
npm install

# Development (Vite dev server only)
npm run dev

# Development with Electron
npm run dev:electron

# Run tests
npm run test:run

# Run tests with coverage
npm run test:coverage

# Lint
npm run lint

# Build for Windows
npm run build:win
```

## Architecture

### Python Core (`src/mad/`)

```
LangGraph StateGraph Flow:
  initialize → debate → moderate → (loop) → judge → END
```

Key components:
- **`core/orchestrator.py`**: `MAD` class - main entry point. Creates agents and builds StateGraph
- **`core/graph.py`**: LangGraph StateGraph definition with nodes (initialize, debate, moderate, judge)
- **`core/state.py`**: Pydantic state models for debate flow
- **`agents/`**: Debater, Judge, Moderator agents
- **`providers/`**: Anthropic, OpenAI provider adapters with registry pattern
- **`presets/`**: Pre-configured debate types (code_review, qa_accuracy, decision)

### Desktop App (`desktop/`)

**Process Architecture:**
- **Main process** (`electron/main.ts`): Window management, IPC handlers
- **Renderer** (`src/`): React UI with Zustand stores
- **Browser adapters** (`electron/browser/adapters/`): Automate ChatGPT, Claude, Gemini web interfaces

**Key Files:**
- `electron/debate/debate-controller.ts`: Infinite loop debate execution with cycle detection and circuit breaker (MAX_ITERATIONS=100)
- `electron/browser/browser-view-manager.ts`: Manages BrowserViews for each LLM provider
- `src/stores/debate-store.ts`: Zustand store for UI state
- `shared/types.ts`: Shared TypeScript types between main/renderer

**IPC Communication:**
- Renderer calls main via `window.api.*` (exposed in preload.ts)
- Main emits events: `debate:progress`, `debate:response`, `debate:element-score`, `debate:complete`

## Key Patterns

### Python
- Async-first (`async def debate()`)
- Provider registry pattern (`get_provider("anthropic")`)
- Pydantic for config/state validation
- pytest-asyncio for async tests

### TypeScript/Electron
- Path aliases: `@/*` (src), `@electron/*` (electron), `@shared/*` (shared)
- Context isolation with preload bridge
- Vitest for testing with jsdom

## Environment Variables

```bash
# Required for Python core
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# Optional
MAD_DEFAULT_PROVIDER=anthropic
MAD_MAX_ROUNDS=3
```

## Testing

Python tests use fixtures in `tests/conftest.py`:
- `sample_topic`: Debate topic string
- `sample_context`: Context string
- `sample_code`: Code for review tests

Desktop tests use `@testing-library/react` and Vitest globals.

## Checklist 기반 작업 관리

### 워크플로우

모든 작업은 `mad_framework_checklist.yaml`을 통해 관리됩니다.

```
사용자 요청 → checklist.yaml 확인 → 서브 에이전트 할당 → 작업 수행 → yaml 결과 기록 → Orchestrator 확인
```

### 서브 에이전트 역할

| Agent | 역할 | 트리거 키워드 |
|-------|------|--------------|
| Explore | 코드베이스 분석 | 분석, 조사, 파악 |
| Plan | 구현 전략 설계 | 설계, 계획, 전략 |
| python-dev | Python 개발 | python, provider, agent |
| typescript-dev | TypeScript/Electron 개발 | typescript, electron, react |
| test-engineer | 테스트 작성 | test, 테스트, TDD |
| code-reviewer | 코드 리뷰 | review, 리뷰, 검토 |
| debugger | 버그 수정 | bug, error, 오류 |

### 작업 완료 후 필수 사항

1. `checklist.yaml`의 `completed` 섹션에 결과 기록
2. `agent_logs`에 작업 로그 추가
3. `metrics` 업데이트
4. 관련 파일 목록 기록

### 파일 위치

- 체크리스트: `mad_framework_checklist.yaml`
- 진행상황: `mad_framework.yaml`
