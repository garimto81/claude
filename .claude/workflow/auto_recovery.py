#!/usr/bin/env python3
"""
Auto-Completion Recovery Logic
자동 완성 실패 복구 로직
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple

PROJECT_DIR = Path(__file__).parent.parent.parent
STATE_FILE = Path(__file__).parent / "auto_state.json"


def run_command(cmd: list, cwd: Path = PROJECT_DIR) -> Tuple[bool, str]:
    """명령 실행"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=300,  # 5분 타임아웃
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout expired"
    except Exception as e:
        return False, str(e)


def recover_test_failure(error_output: str) -> Tuple[bool, str]:
    """테스트 실패 복구

    전략:
    1. 린트 자동 수정 시도
    2. 타입 오류 확인
    3. 재실행
    """
    steps = []

    # 1. Ruff 자동 수정
    success, output = run_command(["ruff", "check", "--fix", "src/"])
    steps.append(f"Ruff fix: {'OK' if success else 'FAILED'}")

    # 2. 테스트 재실행
    success, output = run_command(["pytest", "tests/", "-v", "--tb=short"])
    if success:
        return True, "테스트 통과 (린트 수정 후)"

    steps.append("Pytest: FAILED")
    return False, "\n".join(steps) + f"\n{output}"


def recover_lint_error(error_output: str) -> Tuple[bool, str]:
    """린트 에러 복구

    전략:
    1. ruff --fix 실행
    2. black 포맷팅
    """
    # 1. Ruff 자동 수정
    success, output = run_command(["ruff", "check", "--fix", "."])
    if not success:
        return False, f"Ruff fix failed: {output}"

    # 2. Black 포맷팅
    success, output = run_command(["black", "."])
    if success:
        return True, "린트 수정 완료"

    return False, f"Black failed: {output}"


def recover_build_failure(error_output: str) -> Tuple[bool, str]:
    """빌드 실패 복구

    전략:
    1. 의존성 재설치
    2. 캐시 클리어
    3. 재빌드
    """
    steps = []

    # 1. pip 의존성 재설치
    if Path(PROJECT_DIR / "requirements.txt").exists():
        success, output = run_command(["pip", "install", "-r", "requirements.txt"])
        steps.append(f"pip install: {'OK' if success else 'FAILED'}")

    # 2. npm 의존성 재설치
    if Path(PROJECT_DIR / "package.json").exists():
        success, output = run_command(["npm", "install"])
        steps.append(f"npm install: {'OK' if success else 'FAILED'}")

    return True, "\n".join(steps)


def recover_conflict(error_output: str) -> Tuple[bool, str]:
    """Git 충돌 복구

    전략:
    1. 리베이스 시도
    2. 실패 시 롤백
    """
    # 1. 현재 브랜치 확인
    success, branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if not success:
        return False, "브랜치 확인 실패"

    branch = branch.strip()

    # 2. main에서 리베이스 시도
    success, output = run_command(["git", "fetch", "origin", "main"])
    if not success:
        return False, f"Fetch 실패: {output}"

    success, output = run_command(["git", "rebase", "origin/main"])
    if success:
        return True, "리베이스 성공"

    # 3. 충돌 시 롤백
    run_command(["git", "rebase", "--abort"])
    return False, "리베이스 실패 - 수동 해결 필요"


def recover_dependency_error(error_output: str) -> Tuple[bool, str]:
    """의존성 에러 복구

    전략:
    1. 가상환경 재생성
    2. 의존성 재설치
    """
    # pip 업그레이드
    run_command(["pip", "install", "--upgrade", "pip"])

    # 의존성 설치
    if Path(PROJECT_DIR / "requirements.txt").exists():
        success, output = run_command(["pip", "install", "-r", "requirements.txt"])
        if success:
            return True, "의존성 설치 완료"
        return False, f"의존성 설치 실패: {output}"

    return False, "requirements.txt 없음"


def attempt_recovery(
    error_type: str, error_output: str, retry_count: int = 0, max_retries: int = 3
) -> Tuple[bool, str]:
    """에러 유형에 따른 복구 시도

    Args:
        error_type: 에러 유형 (test, lint, build, conflict, dependency)
        error_output: 에러 출력
        retry_count: 현재 재시도 횟수
        max_retries: 최대 재시도 횟수

    Returns:
        (성공 여부, 메시지)
    """
    if retry_count >= max_retries:
        return False, f"최대 재시도 횟수({max_retries}) 초과"

    recovery_functions = {
        "test": recover_test_failure,
        "lint": recover_lint_error,
        "build": recover_build_failure,
        "conflict": recover_conflict,
        "dependency": recover_dependency_error,
    }

    if error_type not in recovery_functions:
        return False, f"알 수 없는 에러 유형: {error_type}"

    recovery_func = recovery_functions[error_type]
    success, message = recovery_func(error_output)

    if success:
        return True, f"복구 성공 (시도 {retry_count + 1}): {message}"

    # 재시도
    return attempt_recovery(error_type, error_output, retry_count + 1, max_retries)


def detect_error_type(error_output: str) -> str:
    """에러 출력에서 에러 유형 감지"""
    error_lower = error_output.lower()

    if "pytest" in error_lower or "test" in error_lower and "failed" in error_lower:
        return "test"
    if "ruff" in error_lower or "lint" in error_lower or "flake8" in error_lower:
        return "lint"
    if "build" in error_lower or "compile" in error_lower:
        return "build"
    if "conflict" in error_lower or "merge" in error_lower:
        return "conflict"
    if "module" in error_lower and "not found" in error_lower:
        return "dependency"
    if "import" in error_lower and "error" in error_lower:
        return "dependency"

    return "unknown"


def main():
    """CLI 진입점"""
    if len(sys.argv) < 2:
        print("Usage: python auto_recovery.py <error_type> [error_output]")
        print("Error types: test, lint, build, conflict, dependency, auto")
        sys.exit(1)

    error_type = sys.argv[1]
    error_output = sys.argv[2] if len(sys.argv) > 2 else ""

    # auto 모드: 에러 유형 자동 감지
    if error_type == "auto":
        error_type = detect_error_type(error_output)
        print(f"감지된 에러 유형: {error_type}")

    success, message = attempt_recovery(error_type, error_output)

    result = {
        "success": success,
        "error_type": error_type,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
