"""Hook 테스트 공통 유틸리티"""
import json
import subprocess
import sys


def run_hook(hook_path: str, stdin_data: dict, timeout: int = 10) -> dict:
    """subprocess로 Hook 실행, stdout JSON 파싱

    Returns:
        dict with keys: stdout (parsed JSON or None), stderr (str), returncode (int)
    """
    proc = subprocess.run(
        [sys.executable, hook_path],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True,
        timeout=timeout,
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
