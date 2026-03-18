"""Circuit Breaker Hook 테스트 (6 TC)"""
import json
import os
import shutil
import time
from pathlib import Path

import pytest

from hook_utils import run_hook

HOOK_PATH = "C:/claude/.claude/hooks/circuit_breaker.py"
STATE_FILE = Path("C:/claude/.claude/hooks/.circuit_breaker_state.json")
BACKUP_FILE = Path("C:/claude/.claude/hooks/.circuit_breaker_state.json.bak")


@pytest.fixture(autouse=True)
def backup_state():
    """테스트 전후 상태 파일 백업/복원"""
    original_exists = STATE_FILE.exists()
    original_content = None
    if original_exists:
        original_content = STATE_FILE.read_bytes()
        shutil.copy2(STATE_FILE, BACKUP_FILE)

    yield

    # 복원
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if original_exists and original_content is not None:
        STATE_FILE.write_bytes(original_content)
        if BACKUP_FILE.exists():
            BACKUP_FILE.unlink()


def write_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state), encoding="utf-8")


def read_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def test_closed_initial_no_error():
    """TC1: CLOSED 초기 상태 — 에러 없는 입력 → 상태 유지, block 없음"""
    if STATE_FILE.exists():
        STATE_FILE.unlink()

    result = run_hook(HOOK_PATH, {})
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"

    state = read_state()
    assert state.get("state") == "CLOSED"


def test_closed_single_error_stays_closed():
    """TC2: CLOSED + 에러 1회 → failures=1, 아직 CLOSED"""
    write_state({"state": "CLOSED", "failures": 0, "last_failure": 0, "backoff": 1})

    result = run_hook(HOOK_PATH, {"error": "some error occurred"})
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"

    state = read_state()
    assert state.get("failures") == 1
    assert state.get("state") == "CLOSED"


def test_closed_three_errors_opens():
    """TC3: CLOSED + 에러 3회 연속 → state=OPEN, {"decision": "block"} 출력"""
    write_state({"state": "CLOSED", "failures": 2, "last_failure": time.time(), "backoff": 1})

    result = run_hook(HOOK_PATH, {"error": "third error"})
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"

    state = read_state()
    assert state.get("state") == "OPEN"


def test_open_state_blocks():
    """TC4: OPEN 상태에서 호출 → block 출력"""
    write_state({
        "state": "OPEN",
        "failures": 3,
        "last_failure": time.time(),
        "backoff": 2,
    })

    result = run_hook(HOOK_PATH, {})
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"


def test_open_after_30s_becomes_half_open():
    """TC5: OPEN + 30초 경과 → HALF_OPEN 전환"""
    write_state({
        "state": "OPEN",
        "failures": 3,
        "last_failure": time.time() - 60,  # 60초 전
        "backoff": 2,
    })

    result = run_hook(HOOK_PATH, {})
    # HALF_OPEN으로 전환 후 에러 없으므로 block 없이 CLOSED가 될 수 있음
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"

    state = read_state()
    # HALF_OPEN으로 전환되거나 CLOSED로 전환됨
    assert state.get("state") in ("HALF_OPEN", "CLOSED")


def test_half_open_success_closes():
    """TC6: HALF_OPEN + 성공 → CLOSED 복귀, failures=0"""
    write_state({
        "state": "HALF_OPEN",
        "failures": 3,
        "last_failure": time.time() - 60,
        "backoff": 2,
    })

    result = run_hook(HOOK_PATH, {})  # 에러 없는 입력
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"

    state = read_state()
    assert state.get("state") == "CLOSED"
    assert state.get("failures") == 0
