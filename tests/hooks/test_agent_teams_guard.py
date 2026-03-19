"""Agent Teams Guard Hook 테스트 (6 TC)"""
import pytest

from hook_utils import run_hook

HOOK_PATH = "C:/claude/.claude/hooks/agent_teams_guard.py"


def test_explore_agent_approved():
    """TC1: Explore 에이전트 (면제) → approve"""
    result = run_hook(HOOK_PATH, {
        "tool_name": "Agent",
        "tool_input": {"subagent_type": "Explore"},
    })
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "approve"


def test_plan_agent_approved():
    """TC2: Plan 에이전트 (면제) → approve"""
    result = run_hook(HOOK_PATH, {
        "tool_name": "Agent",
        "tool_input": {"subagent_type": "Plan"},
    })
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "approve"


def test_executor_with_all_params_approved():
    """TC3: executor + team_name+name+description → approve"""
    result = run_hook(HOOK_PATH, {
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "executor",
            "team_name": "dev-team",
            "name": "impl-manager",
            "description": "구현 담당 에이전트",
        },
    })
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "approve"


def test_executor_missing_team_name_blocked():
    """TC4: executor + team_name 누락 → block"""
    result = run_hook(HOOK_PATH, {
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "executor",
            "name": "impl-manager",
            "description": "구현 담당 에이전트",
        },
    })
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"
    assert "team_name" in result["stdout"].get("reason", "")


def test_architect_missing_name_blocked():
    """TC5: architect + name 누락 → block"""
    result = run_hook(HOOK_PATH, {
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "architect",
            "team_name": "dev-team",
            "description": "아키텍처 검증 에이전트",
        },
    })
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"
    assert "name" in result["stdout"].get("reason", "")


def test_empty_input_approved():
    """TC6: 비어있는 입력 → approve (빈 stdin)"""
    import json
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, HOOK_PATH],
        input="",
        capture_output=True,
        text=True,
        timeout=10,
    )

    stdout_data = None
    if proc.stdout.strip():
        try:
            stdout_data = json.loads(proc.stdout.strip())
        except json.JSONDecodeError:
            stdout_data = {"raw": proc.stdout.strip()}

    assert stdout_data is not None
    assert stdout_data.get("decision") == "approve"
