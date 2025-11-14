#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Usage Tracking System
Langfuse 기반 agent 사용 추적 및 피드백 수집

Usage:
    from track_agent_usage import AgentTracker

    tracker = AgentTracker()

    # Agent 실행 추적
    with tracker.track("context7-engineer", phase="Phase 0", task="Verify React docs"):
        result = run_agent()

    # 피드백 수집
    tracker.collect_feedback(
        agent="context7-engineer",
        rating=5,
        comment="Successfully verified React 18 docs"
    )
"""

import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

try:
    from langfuse import Langfuse
except ImportError:
    print("❌ langfuse 패키지가 설치되지 않았습니다.")
    print("   설치: pip install -r .claude/evolution/requirements.txt")
    sys.exit(1)


class AgentTracker:
    """Agent 사용 추적 및 피드백 관리"""

    def __init__(self):
        """Initialize Langfuse client"""
        self.public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
        self.secret_key = os.getenv('LANGFUSE_SECRET_KEY')
        self.host = os.getenv('LANGFUSE_HOST', 'http://localhost:3000')

        if not self.public_key or not self.secret_key:
            raise ValueError(
                "Langfuse API keys not found!\n"
                "Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in .claude/evolution/.env"
            )

        self.client = Langfuse(
            public_key=self.public_key,
            secret_key=self.secret_key,
            host=self.host
        )

        # Session info
        self.session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.current_trace = None

    @contextmanager
    def track(
        self,
        agent_name: str,
        phase: Optional[str] = None,
        task: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Agent 실행 추적 컨텍스트 매니저

        Args:
            agent_name: Agent 이름 (예: "context7-engineer")
            phase: Phase 정보 (예: "Phase 0")
            task: Task 설명 (예: "Verify React docs")
            metadata: 추가 메타데이터

        Example:
            with tracker.track("context7-engineer", phase="Phase 0"):
                result = agent.run()
        """
        start_time = time.time()

        # Create trace
        trace = self.client.trace(
            name=f"agent-{agent_name}",
            user_id=os.getenv('USER', 'unknown'),
            session_id=self.session_id,
            metadata={
                "agent": agent_name,
                "phase": phase,
                "task": task,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
        )

        self.current_trace = trace

        try:
            print(f"📊 Tracking: {agent_name} (Phase: {phase})")
            yield trace

            # Success
            duration = time.time() - start_time
            trace.update(
                output={"status": "success", "duration_seconds": duration}
            )
            print(f"✅ Completed in {duration:.2f}s")

        except Exception as e:
            # Error
            duration = time.time() - start_time
            trace.update(
                output={
                    "status": "error",
                    "error": str(e),
                    "duration_seconds": duration
                }
            )
            print(f"❌ Error: {e}")
            raise

        finally:
            self.current_trace = None

    def collect_feedback(
        self,
        agent: str,
        rating: int,
        comment: Optional[str] = None,
        effectiveness: Optional[float] = None,
        suggestions: Optional[str] = None
    ):
        """
        사용자 피드백 수집

        Args:
            agent: Agent 이름
            rating: 평점 (1-5)
            comment: 코멘트
            effectiveness: 효과성 점수 (0-1)
            suggestions: 개선 제안

        Example:
            tracker.collect_feedback(
                agent="context7-engineer",
                rating=5,
                comment="Docs verified correctly",
                effectiveness=0.95
            )
        """
        if not self.current_trace:
            print("⚠️  Warning: No active trace. Call track() first.")
            return

        # Rating (1-5 → 0-1 scale)
        self.current_trace.score(
            name="user_rating",
            value=rating / 5.0,
            comment=comment
        )

        # Effectiveness
        if effectiveness is not None:
            self.current_trace.score(
                name="effectiveness",
                value=effectiveness,
                comment="Agent effectiveness (0=poor, 1=excellent)"
            )

        # Suggestions
        if suggestions:
            self.current_trace.score(
                name="improvement_suggestion",
                value=1.0,  # Binary: has suggestion
                comment=suggestions
            )

        print(f"💬 Feedback recorded: {rating}/5 stars")

    def prompt_feedback(self, agent: str):
        """
        터미널에서 피드백 입력받기

        Args:
            agent: Agent 이름
        """
        try:
            print(f"\n{'='*60}")
            print(f"📝 Agent '{agent}' 사용 완료!")
            print(f"{'='*60}")

            # Rating
            while True:
                try:
                    rating = int(input("평점 (1-5): "))
                    if 1 <= rating <= 5:
                        break
                    print("1-5 사이 숫자를 입력하세요.")
                except ValueError:
                    print("숫자를 입력하세요.")

            # Comment
            comment = input("코멘트 (선택, Enter=skip): ").strip()

            # Effectiveness
            effectiveness_str = input("효과성 (0-10, Enter=skip): ").strip()
            effectiveness = None
            if effectiveness_str:
                try:
                    effectiveness = int(effectiveness_str) / 10.0
                except ValueError:
                    pass

            # Suggestions
            suggestions = input("개선 제안 (선택, Enter=skip): ").strip()

            self.collect_feedback(
                agent=agent,
                rating=rating,
                comment=comment or None,
                effectiveness=effectiveness,
                suggestions=suggestions or None
            )

            print("✅ 피드백이 저장되었습니다!\n")

        except KeyboardInterrupt:
            print("\n⚠️  피드백 수집 취소됨")

    def flush(self):
        """Flush pending events to Langfuse"""
        self.client.flush()


# Global singleton
_tracker = None

def get_tracker() -> AgentTracker:
    """Get global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = AgentTracker()
    return _tracker


# Convenience functions
def track_agent(agent_name: str, phase: Optional[str] = None, task: Optional[str] = None):
    """Decorator for tracking agent functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = get_tracker()
            with tracker.track(agent_name, phase=phase, task=task):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test script
    print("🧪 Testing AgentTracker...")

    tracker = AgentTracker()

    # Test 1: Basic tracking
    print("\n1. Testing basic tracking:")
    with tracker.track("test-agent", phase="Phase 0", task="Test task"):
        time.sleep(0.5)

    # Test 2: Feedback collection
    print("\n2. Testing feedback collection:")
    with tracker.track("context7-engineer", phase="Phase 0", task="Verify React docs"):
        time.sleep(0.3)

    tracker.collect_feedback(
        agent="context7-engineer",
        rating=5,
        comment="Test feedback",
        effectiveness=0.9
    )

    # Test 3: Error handling
    print("\n3. Testing error handling:")
    try:
        with tracker.track("error-agent", phase="Phase 1", task="Test error"):
            raise ValueError("Test error")
    except ValueError:
        print("Error caught successfully")

    tracker.flush()
    print("\n✅ All tests completed!")
    print(f"📊 Check dashboard: {tracker.host}")
