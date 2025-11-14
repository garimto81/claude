#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Quality Tracker - Wrapper for Sub-Repos
서브 레포용 간단한 wrapper 스크립트

이 파일을 서브 레포의 .claude/ 디렉토리에 복사하세요.
전역 레포의 agent_quality_v2를 직접 import하므로 항상 최신 버전 사용.

Usage:
    python .claude/track_wrapper.py debugger "Fix bug" pass --duration 1.5
    python .claude/track_wrapper.py test-automator "Write tests" fail --error "Timeout"
"""

import sys
import os
import io
import argparse
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 전역 레포 경로 자동 감지
def find_global_repo():
    """전역 레포 (claude01) 경로 찾기"""
    # 1. 환경변수에서 찾기
    if 'CLAUDE_GLOBAL_REPO' in os.environ:
        return Path(os.environ['CLAUDE_GLOBAL_REPO'])

    # 2. 상대 경로에서 찾기 (형제 디렉토리)
    current = Path.cwd()

    # 부모 디렉토리의 claude01 찾기
    parent = current.parent
    if (parent / 'claude01').exists():
        return parent / 'claude01'

    # 조부모 디렉토리의 claude01 찾기
    grandparent = parent.parent
    if (grandparent / 'claude01').exists():
        return grandparent / 'claude01'

    # 3. .env 파일에서 찾기
    env_file = current / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('CLAUDE_GLOBAL_REPO='):
                    path = line.split('=', 1)[1].strip().strip('"').strip("'")
                    return Path(path)

    return None


# 전역 레포 경로 추가
global_repo = find_global_repo()

if global_repo is None:
    print("❌ 전역 레포 (claude01)를 찾을 수 없습니다!")
    print("\n해결 방법:")
    print("1. 환경변수 설정:")
    print("   export CLAUDE_GLOBAL_REPO=/path/to/claude01")
    print("\n2. .env 파일에 추가:")
    print("   echo 'CLAUDE_GLOBAL_REPO=/path/to/claude01' >> .env")
    print("\n3. 디렉토리 구조 확인:")
    print("   parent/")
    print("   ├── claude01/  (전역 레포)")
    print("   └── my-project/  (서브 레포)")
    sys.exit(1)

# Python path에 추가
evolution_path = global_repo / '.claude' / 'evolution'
if not evolution_path.exists():
    print(f"❌ 전역 레포에 evolution 디렉토리가 없습니다: {evolution_path}")
    sys.exit(1)

sys.path.insert(0, str(evolution_path))

# 이제 import 가능
try:
    from scripts.agent_quality_v2 import AgentQuality
except ImportError as e:
    print(f"❌ agent_quality_v2를 import할 수 없습니다: {e}")
    print(f"\n전역 레포 경로: {global_repo}")
    print(f"Evolution 경로: {evolution_path}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Agent Quality Tracker (v2.0) - Sub-Repo Wrapper",
        epilog="Example: python track_wrapper.py debugger 'Fix bug' pass --duration 1.5"
    )

    parser.add_argument('agent', help='Agent 이름 (예: debugger)')
    parser.add_argument('task', help='Task 이름 (예: Fix TypeError)')
    parser.add_argument('status', choices=['pass', 'fail'], help='상태: pass 또는 fail')

    parser.add_argument('--version', default='1.0.0', help='Agent 버전 (기본: 1.0.0)')
    parser.add_argument('--phase', help='Phase (예: Phase 1)')
    parser.add_argument('--duration', type=float, default=0, help='실행 시간 (초)')
    parser.add_argument('--error', help='에러 메시지 (실패 시)')
    parser.add_argument('--auto-detected', action='store_true', help='자동 감지 여부')

    args = parser.parse_args()

    # AgentQuality 사용
    quality = AgentQuality(args.agent, version=args.version)

    quality.record(
        task=args.task,
        status=args.status,
        duration=args.duration,
        error=args.error,
        auto_detected=args.auto_detected,
        phase=args.phase
    )

    # 결과 출력
    status_icon = "✅" if args.status == "pass" else "❌"
    print(f"{status_icon} Logged: {args.agent} - {args.task} ({args.status.upper()})")

    if args.duration > 0:
        print(f"   Duration: {args.duration:.2f}s")

    if args.error:
        print(f"   Error: {args.error}")

    # 간단한 통계
    score = quality.get_score()
    if score['avg_success_rate'] is not None:
        task_stats = score['tasks'].get(args.task)
        if task_stats:
            rate = task_stats['weighted_rate']
            conf = task_stats['confidence']
            print(f"   Task Score: {rate:.0%} (confidence: {conf:.0%})")


if __name__ == "__main__":
    main()
