#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Feedback Collection CLI
사용자 피드백을 쉽게 수집하는 CLI 도구

Usage:
    # Agent 사용 후 실행
    python .claude/evolution/scripts/collect_feedback.py context7-engineer

    # 빠른 평점만
    python .claude/evolution/scripts/collect_feedback.py context7-engineer --rating 5

    # 완전한 피드백
    python .claude/evolution/scripts/collect_feedback.py context7-engineer \
        --rating 5 \
        --comment "Docs verified correctly" \
        --effectiveness 9 \
        --suggestion "Add retry logic"
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from track_agent_usage import get_tracker


def main():
    parser = argparse.ArgumentParser(
        description="Agent 피드백 수집 CLI",
        epilog="Example: python collect_feedback.py context7-engineer --rating 5"
    )

    parser.add_argument(
        'agent',
        help='Agent 이름 (예: context7-engineer)'
    )

    parser.add_argument(
        '--rating', '-r',
        type=int,
        choices=range(1, 6),
        help='평점 (1-5)'
    )

    parser.add_argument(
        '--comment', '-c',
        help='코멘트'
    )

    parser.add_argument(
        '--effectiveness', '-e',
        type=int,
        choices=range(0, 11),
        help='효과성 (0-10)'
    )

    parser.add_argument(
        '--suggestion', '-s',
        help='개선 제안'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='인터랙티브 모드 (질문 형식)'
    )

    args = parser.parse_args()

    try:
        tracker = get_tracker()

        # Create temporary trace for feedback
        with tracker.track(args.agent, phase="Feedback", task="User feedback"):
            if args.interactive or not args.rating:
                # Interactive mode
                tracker.prompt_feedback(args.agent)
            else:
                # CLI mode
                effectiveness = None
                if args.effectiveness is not None:
                    effectiveness = args.effectiveness / 10.0

                tracker.collect_feedback(
                    agent=args.agent,
                    rating=args.rating,
                    comment=args.comment,
                    effectiveness=effectiveness,
                    suggestions=args.suggestion
                )

        tracker.flush()

        print("✅ 피드백이 Langfuse에 저장되었습니다!")
        print(f"📊 대시보드: {tracker.host}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
