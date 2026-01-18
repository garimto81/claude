"""Multi-AI Authentication Skill

외부 AI 서비스(GPT, Gemini, Poe)에 대한 OAuth 인증 통합 관리.
"""

import sys
from pathlib import Path

# 스크립트 디렉토리를 sys.path에 추가 (상대 import 해결)
_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

__version__ = "1.0.0"
__author__ = "Claude Code"
