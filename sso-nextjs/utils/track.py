#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Tracking Helper
자동으로 Agent 사용을 추적하는 헬퍼 함수들
"""

import sys
import os
import io
import time
from pathlib import Path
from contextlib import contextmanager

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 전역 레포 경로 설정
from dotenv import load_dotenv
load_dotenv()

global_repo = Path(os.getenv('CLAUDE_GLOBAL_REPO'))
sys.path.insert(0, str(global_repo / '.claude' / 'evolution'))

from scripts.agent_quality_v2 import AgentQuality


@contextmanager
def track_agent(agent_name: str, task: str, version: str = "1.0.0", phase: str = None):
    """
    Agent 사용을 자동으로 추적하는 Context Manager

    사용법:
        with track_agent("debugger", "Fix TypeError"):
            # 여기에 코드 작성
            fix_bug()
        # 자동으로 성공/실패 기록됨

    Args:
        agent_name: Agent 이름 (예: "debugger", "test-automator")
        task: Task 설명 (예: "Fix TypeError in auth.ts")
        version: Agent 버전 (기본: "1.0.0")
        phase: Phase 정보 (선택, 예: "Phase 1")
    """
    quality = AgentQuality(agent_name, version)
    start_time = time.time()

    print(f"🤖 {agent_name}: {task} 시작...")

    try:
        yield quality
        # 성공
        duration = time.time() - start_time
        quality.record(
            task=task,
            status="pass",
            duration=duration,
            auto_detected=True,
            phase=phase
        )
        print(f"✅ {agent_name}: {task} 완료 ({duration:.2f}s)")

    except Exception as e:
        # 실패
        duration = time.time() - start_time
        quality.record(
            task=task,
            status="fail",
            duration=duration,
            error=str(e),
            auto_detected=True,
            phase=phase
        )
        print(f"❌ {agent_name}: {task} 실패 ({duration:.2f}s)")
        print(f"   Error: {e}")
        raise


def quick_track(agent_name: str, task: str, status: str, duration: float = 0, error: str = None):
    """
    간단한 수동 기록 (이미 완료된 작업)

    사용법:
        quick_track("debugger", "Fix bug", "pass", duration=1.5)
        quick_track("test-automator", "Tests", "fail", error="Timeout")
    """
    quality = AgentQuality(agent_name)
    quality.record(
        task=task,
        status=status,
        duration=duration,
        error=error,
        auto_detected=False
    )

    status_icon = "✅" if status == "pass" else "❌"
    print(f"{status_icon} Logged: {agent_name} - {task} ({status.upper()})")
