"""Stop Completion Check Hook 테스트 (4 TC)"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from hook_utils import run_hook

HOOK_PATH = "C:/claude/.claude/hooks/stop_completion_check.py"


def make_task_file(tasks_dir: Path, name: str, status: str, subject: str = "Test task"):
    task_data = {"status": status, "subject": subject}
    (tasks_dir / f"{name}.json").write_text(
        json.dumps(task_data), encoding="utf-8"
    )


def run_hook_with_tasks_dir(tasks_dir: Path) -> dict:
    """HOME을 tasks_dir 부모로 설정해 Hook 실행"""
    home_dir = tasks_dir.parent.parent  # tasks_dir = home/.claude/tasks
    env = os.environ.copy()
    env["USERPROFILE"] = str(home_dir)
    env["HOME"] = str(home_dir)

    proc = subprocess.run(
        [sys.executable, HOOK_PATH],
        input=json.dumps({}),
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )

    stdout_data = None
    if proc.stdout.strip():
        try:
            stdout_data = json.loads(proc.stdout.strip())
        except json.JSONDecodeError:
            stdout_data = {"raw": proc.stdout.strip()}

    return {
        "stdout": stdout_data,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
    }


def test_no_tasks_no_block(tmp_path):
    """TC1: tasks 디렉토리 비어있음 → block 없음"""
    tasks_dir = tmp_path / ".claude" / "tasks"
    tasks_dir.mkdir(parents=True)

    result = run_hook_with_tasks_dir(tasks_dir)
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"


def test_all_completed_no_block(tmp_path):
    """TC2: status=completed 파일만 → block 없음"""
    tasks_dir = tmp_path / ".claude" / "tasks"
    tasks_dir.mkdir(parents=True)
    make_task_file(tasks_dir, "task1", "completed")
    make_task_file(tasks_dir, "task2", "completed")

    result = run_hook_with_tasks_dir(tasks_dir)
    assert result["stdout"] is None or result["stdout"].get("decision") != "block"


def test_in_progress_task_blocks(tmp_path):
    """TC3: status=in_progress → {"decision": "block"} 출력"""
    tasks_dir = tmp_path / ".claude" / "tasks"
    tasks_dir.mkdir(parents=True)
    make_task_file(tasks_dir, "task1", "in_progress", "진행 중인 작업")

    result = run_hook_with_tasks_dir(tasks_dir)
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"


def test_pending_task_blocks(tmp_path):
    """TC4: status=pending → block 출력"""
    tasks_dir = tmp_path / ".claude" / "tasks"
    tasks_dir.mkdir(parents=True)
    make_task_file(tasks_dir, "task1", "pending", "대기 중인 작업")

    result = run_hook_with_tasks_dir(tasks_dir)
    assert result["stdout"] is not None
    assert result["stdout"].get("decision") == "block"
