"""pytest 설정 파일"""

import sys
from pathlib import Path

# 프로젝트 src 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
