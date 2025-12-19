# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MAD Framework (Multi-Agent Debate) - Python/TypeScript hybrid for LLM agent debates.
- **Python Core** (`src/mad/`): LangGraph-based debate orchestration with async support
- **Desktop App** (`desktop/`): Electron + React + Zustand UI for browser LLM automation

## Commands

### Python
```bash
uv sync --all-extras                     # Setup (dev + google extras)
pytest tests/unit/test_config.py -v      # Single test (권장)
pytest tests/unit/ -v                    # Unit tests only
ruff check src/ && mypy src/             # Lint + Type check
```

### Desktop
```powershell
cd D:\AI\claude01\mad_framework\desktop
npm run dev:electron   # Dev with Electron
npm run test:run       # All tests (Vitest)
npm run lint           # ESLint
```

## Architecture

### Python (`src/mad/`)

**StateGraph Flow:**
```
initialize → debate → moderate → (loop if not consensus) → judge → END
```

| Module | Purpose |
|--------|---------|
| `core/orchestrator.py` | `MAD` class - entry point, creates graph and agents |
| `core/graph.py` | LangGraph StateGraph definition, node functions |
| `core/state.py` | `DebateState` TypedDict for graph state |
| `core/config.py` | Pydantic configs: `DebateConfig`, `DebaterConfig`, `JudgeConfig` |
| `agents/debater.py` | `DebaterAgent` - perspective-based argumentation |
| `agents/judge.py` | `JudgeAgent` - final verdict with confidence score |
| `agents/moderator.py` | `ModeratorAgent` - consensus check, early stopping |
| `providers/registry.py` | `get_provider("anthropic")` - singleton factory |

**Usage:**
```python
from mad import MAD, DebateConfig
result = await mad.debate(topic="...", context="...")
# result.verdict, result.confidence, result.total_cost
```

### Desktop (`desktop/`)

**Main Process (Electron):**
| File | Purpose |
|------|---------|
| `electron/debate/debate-controller.ts` | Infinite debate loop (MAX_ITERATIONS=100), Circuit Breaker |
| `electron/debate/cycle-detector.ts` | Levenshtein-based cycle detection (threshold=0.85) |
| `electron/browser/browser-view-manager.ts` | Multi-provider BrowserView management |
| `electron/browser/adapters/base-adapter.ts` | Browser automation with selector fallbacks |
| `electron/browser/adapters/selector-config.ts` | Per-provider CSS selectors |
| `electron/ipc/handlers.ts` | IPC handlers for renderer communication |

**Renderer Process (React):**
| File | Purpose |
|------|---------|
| `src/App.tsx` | Main app with Zustand store |
| `src/components/DebateControlPanel.tsx` | Start/stop debate controls |
| `src/components/ResponseViewer.tsx` | Streaming response display |
| `src/components/ElementScoreBoard.tsx` | Per-element score tracking |

**Shared Types:**
- `shared/types.ts`: `LLMProvider`, `AdapterResult<T>`, `DebateConfig`, `StreamChunk`

**Key Patterns:**
- `AdapterResult<T>` for standardized success/error returns (Issue #17)
- Selector fallback system for UI changes (Issue #18)
- Event-based streaming: `debate:stream-chunk` for real-time updates

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
GOOGLE_API_KEY=xxxxx              # Optional, for google provider
MAD_DEFAULT_PROVIDER=anthropic    # Optional
```

## Testing

### Python
```bash
pytest tests/unit/test_config.py -v          # Single file
pytest tests/unit/ -v -k "test_debater"      # By pattern
pytest --cov=src/mad tests/unit/             # With coverage
```

### Desktop (Vitest)
```bash
npm run test:run                              # All tests
npm run test:run -- tests/unit/adapters      # Directory
npm run test:coverage                         # With coverage
```

## Key Constants

| Constant | Location | Value | Purpose |
|----------|----------|-------|---------|
| `MAX_ITERATIONS` | debate-controller.ts:48 | 100 | Debate loop limit |
| `MAX_CONSECUTIVE_EMPTY_RESPONSES` | debate-controller.ts:49 | 3 | Circuit breaker |
| `DEFAULT_SIMILARITY_THRESHOLD` | cycle-detector.ts:77 | 0.85 | Cycle detection |
| `completionThreshold` | DebateConfig | 90 | Element completion score |
