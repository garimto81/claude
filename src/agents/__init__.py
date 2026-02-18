# Multi-Agent Parallel Workflow System
# Claude Agent SDK + LangGraph Integration

from .parallel_workflow import (
    WorkflowState,
    build_parallel_workflow,
    run_parallel_task,
)
from .config import (
    AgentConfig,
    AGENT_MODEL_TIERS,
    TEAM_MODEL_TIERS,
    TEAM_CONFIGS,
    get_teams_for_complexity,
)
from .teams import (
    DevTeam,
    QualityTeam,
    OpsTeam,
    ResearchTeam,
    Coordinator,
)

__all__ = [
    # 기존 API
    "WorkflowState",
    "build_parallel_workflow",
    "run_parallel_task",
    "AgentConfig",
    "AGENT_MODEL_TIERS",
    # Team Workflow
    "TEAM_MODEL_TIERS",
    "TEAM_CONFIGS",
    "get_teams_for_complexity",
    "DevTeam",
    "QualityTeam",
    "OpsTeam",
    "ResearchTeam",
    "Coordinator",
]

__version__ = "2.0.0"
