"""Context Limit Recovery Hook 테스트 (4 TC)"""
import pytest

from hook_utils import run_hook

HOOK_PATH = "C:/claude/.claude/hooks/recovery/context_limit_recovery.py"


def test_context_limit_exceeded_blocks():
    """TC1: "context limit exceeded" → block 출력"""
    result = run_hook(HOOK_PATH, {"error": "context limit exceeded"})
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"


def test_context_window_exceeded_blocks():
    """TC2: "context window exceeded" → block 출력"""
    result = run_hook(HOOK_PATH, {"error": "context window exceeded, please reduce input"})
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"


def test_token_limit_reached_blocks():
    """TC3: "token limit reached" → block 출력"""
    result = run_hook(HOOK_PATH, {"error": "token limit reached for this session"})
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"


def test_context_alone_no_block():
    """TC4: "context" 단독 (false positive 제거) → block 안 됨"""
    result = run_hook(HOOK_PATH, {"error": "some context here"})
    # "context" 단독은 "context limit" / "context window"를 포함하지 않으므로 block 없음
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"
