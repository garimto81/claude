"""Session Error Recovery Hook 테스트 (4 TC)"""
import pytest

from hook_utils import run_hook

HOOK_PATH = "C:/claude/.claude/hooks/recovery/session_error_recovery.py"


def test_connection_refused_blocks():
    """TC1: "connection refused" → block 출력"""
    result = run_hook(HOOK_PATH, {"error": "connection refused to server"})
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"


def test_session_expired_blocks():
    """TC2: "session expired" → block 출력"""
    result = run_hook(HOOK_PATH, {"error": "session expired, please re-authenticate"})
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"


def test_timeout_alone_no_block():
    """TC3: "timeout" 단독 (false positive 제거) → block 안 됨"""
    result = run_hook(HOOK_PATH, {"error": "operation timeout"})
    # SESSION_ERROR_KEYWORDS에 "timeout" 단독은 없으므로 block 없음
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"


def test_no_error_no_block():
    """TC4: 에러 없음 → block 없음"""
    result = run_hook(HOOK_PATH, {})
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"
