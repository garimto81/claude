"""Edit Error Recovery Hook 테스트 (4 TC)"""
import pytest

from hook_utils import run_hook

HOOK_PATH = "C:/claude/.claude/hooks/recovery/edit_error_recovery.py"


def test_edit_not_unique_blocks():
    """TC1: Edit + "not unique" → block 출력"""
    result = run_hook(HOOK_PATH, {
        "tool_name": "Edit",
        "error": "String not unique in file",
    })
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"


def test_edit_not_found_blocks():
    """TC2: Edit + "not found" → block 출력"""
    result = run_hook(HOOK_PATH, {
        "tool_name": "Edit",
        "error": "String not found in file",
    })
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"


def test_edit_success_no_block():
    """TC3: Edit + 성공 (error 없음) → block 없음"""
    result = run_hook(HOOK_PATH, {
        "tool_name": "Edit",
    })
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"


def test_write_not_unique_no_block():
    """TC4: Write + "not unique" → tool_name이 Edit이 아님 → block 없음"""
    result = run_hook(HOOK_PATH, {
        "tool_name": "Write",
        "error": "String not unique in file",
    })
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"
