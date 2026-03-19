"""Hook 테스트 공통 픽스처"""
import sys
from pathlib import Path

import pytest

# tests/hooks 디렉토리를 sys.path에 추가해 hook_utils 임포트 허용
sys.path.insert(0, str(Path(__file__).parent))

from hook_utils import run_hook

HOOKS_DIR = Path("C:/claude/.claude/hooks")
RECOVERY_DIR = HOOKS_DIR / "recovery"


@pytest.fixture
def hook_runner():
    """Hook 실행 헬퍼 픽스처"""
    return run_hook
