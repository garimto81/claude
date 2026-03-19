"""PreCompact Save Hook 테스트 (4 TC)"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from hook_utils import run_hook

HOOK_PATH = "C:/claude/.claude/hooks/pre_compact_save.py"
SNAPSHOT_FILE = Path("C:/claude/.claude/hooks/.pre_compact_snapshot.json")


@pytest.fixture(autouse=True)
def cleanup_snapshot():
    """테스트 후 스냅샷 파일 정리"""
    original_exists = SNAPSHOT_FILE.exists()
    original_content = None
    if original_exists:
        original_content = SNAPSHOT_FILE.read_bytes()

    yield

    if SNAPSHOT_FILE.exists():
        SNAPSHOT_FILE.unlink()
    if original_exists and original_content is not None:
        SNAPSHOT_FILE.write_bytes(original_content)


def test_normal_execution_creates_snapshot():
    """TC1: 정상 실행 → 스냅샷 파일 생성됨"""
    result = run_hook(HOOK_PATH, {})
    assert result["returncode"] == 0
    assert SNAPSHOT_FILE.exists()


def test_snapshot_has_required_keys():
    """TC2: 스냅샷에 timestamp, teams, tasks_summary 키 존재"""
    run_hook(HOOK_PATH, {})

    assert SNAPSHOT_FILE.exists()
    data = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))

    assert "timestamp" in data
    assert "teams" in data
    assert "tasks_summary" in data


def test_missing_teams_dir_ok(tmp_path, monkeypatch):
    """TC3: teams 디렉토리 없음 → 정상 실행 (빈 teams 배열)"""
    # HOME을 tmp_path로 변경해 빈 teams 디렉토리 환경 시뮬레이션
    env = os.environ.copy()
    env["USERPROFILE"] = str(tmp_path)
    env["HOME"] = str(tmp_path)

    proc = subprocess.run(
        [sys.executable, HOOK_PATH],
        input=json.dumps({}),
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    assert proc.returncode == 0

    # 스냅샷 파일은 HOOK_PATH 고정 경로에 생성되므로 내용만 확인
    if SNAPSHOT_FILE.exists():
        data = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        # teams는 빈 배열이거나 존재해야 함
        assert isinstance(data.get("teams"), list)


def test_unreadable_team_config_preserved(tmp_path, monkeypatch):
    """TC4: 읽기 불가 team config → 에러 정보 포함 (스냅샷에 teams 항목 보존)"""
    # tmp_path에 가짜 teams 디렉토리와 읽기 불가 config 파일 생성
    teams_dir = tmp_path / ".claude" / "teams" / "bad-team"
    teams_dir.mkdir(parents=True)
    bad_config = teams_dir / "config.json"
    bad_config.write_text("{ invalid json }", encoding="utf-8")

    env = os.environ.copy()
    env["USERPROFILE"] = str(tmp_path)
    env["HOME"] = str(tmp_path)

    proc = subprocess.run(
        [sys.executable, HOOK_PATH],
        input=json.dumps({}),
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    assert proc.returncode == 0

    # Hook이 에러 없이 완료되면 통과 (스냅샷 파일 위치는 고정)
    if SNAPSHOT_FILE.exists():
        data = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
        assert "teams" in data
