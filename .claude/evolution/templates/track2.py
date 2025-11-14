#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Quality Tracker v2.0 (서브 레포용)
합리적인 점수 시스템 구현

Usage:
    python .claude/track.py \
        --agent "debugger" \
        --task "Fix TypeError in auth.ts" \
        --status "pass" \
        --duration 1.5

    python .claude/track.py \
        --agent "test-automator" \
        --task "Unit tests" \
        --status "fail" \
        --error "Assertion failed" \
        --auto-detected  # 테스트 자동 감지
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path


LOG_FILE = Path(".agent-quality-v2.jsonl")


def record_quality(
    agent: str,
    task: str,
    status: str,
    version: str = "1.0.0",
    phase: str = None,
    duration: float = 0,
    error: str = None,
    auto_detected: bool = False,
    test_output: str = None
):
    """품질 기록"""

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent,
        "version": version,
        "task": task,
        "status": status,
        "duration": duration,
        "auto_detected": auto_detected
    }

    if phase:
        log_entry["phase"] = phase
    if error:
        log_entry["error"] = error
    if test_output:
        log_entry["test_output"] = test_output

    # 파일에 추가
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    # 결과 출력
    status_icon = "✅" if status == "pass" else "❌"
    print(f"{status_icon} Logged: {agent} - {task} ({status.upper()})")

    if duration > 0:
        print(f"   Duration: {duration:.2f}s")

    if error:
        print(f"   Error: {error}")

    # 간단한 통계 (현재 agent + task)
    stats = get_task_stats(agent, task)
    if stats:
        rate = stats['weighted_rate']
        conf = stats['confidence']
        print(f"   Task Score: {rate:.0%} (confidence: {conf:.0%})")


def get_task_stats(agent: str, task: str) -> dict:
    """특정 Task의 현재 통계"""
    if not LOG_FILE.exists():
        return None

    attempts = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                log = json.loads(line.strip())
                if log['agent'] == agent and log['task'] == task:
                    attempts.append(log)
            except:
                pass

    if not attempts:
        return None

    # 간단한 통계
    total = len(attempts)
    successes = sum(1 for a in attempts if a['status'] == 'pass')

    # 시간 가중 성공률 (최근 10개)
    recent = attempts[-10:]
    n = len(recent)
    if n > 0:
        weights = [0.5 ** (n - i - 1) for i in range(n)]
        total_weight = sum(weights)
        weighted_sum = sum(
            w * (1 if a['status'] == 'pass' else 0)
            for w, a in zip(weights, recent)
        )
        weighted_rate = weighted_sum / total_weight
    else:
        weighted_rate = successes / total if total > 0 else 0

    # 신뢰도
    if total >= 20:
        confidence = 1.0
    elif total >= 10:
        confidence = 0.8
    elif total >= 5:
        confidence = 0.6
    elif total >= 2:
        confidence = 0.4
    else:
        confidence = 0.2

    return {
        "total": total,
        "successes": successes,
        "success_rate": successes / total,
        "weighted_rate": weighted_rate,
        "confidence": confidence
    }


def main():
    parser = argparse.ArgumentParser(
        description="Agent Quality Tracker v2.0",
        epilog="Example: python track.py --agent debugger --task 'Fix bug' --status pass"
    )

    parser.add_argument('--agent', required=True, help='Agent 이름')
    parser.add_argument('--task', required=True, help='Task 이름')
    parser.add_argument('--status', required=True, choices=['pass', 'fail'], help='상태')
    parser.add_argument('--version', default='1.0.0', help='Agent 버전 (기본: 1.0.0)')
    parser.add_argument('--phase', help='Phase (예: Phase 1)')
    parser.add_argument('--duration', type=float, default=0, help='실행 시간 (초)')
    parser.add_argument('--error', help='에러 메시지')
    parser.add_argument('--auto-detected', action='store_true', help='자동 감지 여부')
    parser.add_argument('--test-output', help='테스트 출력')

    args = parser.parse_args()

    record_quality(
        agent=args.agent,
        task=args.task,
        status=args.status,
        version=args.version,
        phase=args.phase,
        duration=args.duration,
        error=args.error,
        auto_detected=args.auto_detected,
        test_output=args.test_output
    )


if __name__ == "__main__":
    main()
