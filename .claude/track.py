#!/usr/bin/env python3
"""
Agent Quality Logger (서브 레포용 Python 버전)
이 파일을 서브 레포 .claude/track.py로 복사하여 사용

Usage:
    python .claude/track.py <agent> <phase> <task> <status> [error] [duration]

Example:
    python .claude/track.py "context7-engineer" "Phase 0" "Verify docs" "pass"
    python .claude/track.py "debugger" "Phase 1" "Fix bug" "fail" "TypeError" 2.5
"""

import json
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(".agent-quality.jsonl")

def get_previous_score(agent, task):
    """이전 점수 가져오기"""
    if not LOG_FILE.exists():
        return 5.0

    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()

        for line in reversed(lines):
            log = json.loads(line.strip())
            if log['agent'] == agent and log['task'] == task:
                return log['score']
    except:
        pass

    return 5.0

def get_attempt_count(agent, task):
    """시도 횟수 계산"""
    if not LOG_FILE.exists():
        return 1

    count = 0
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                log = json.loads(line.strip())
                if log['agent'] == agent and log['task'] == task:
                    count += 1
    except:
        pass

    return count + 1

def calculate_score(previous_score, attempt, status):
    """점수 계산

    규칙:
    - 1회차 통과: 5.0 (만점)
    - 실패: -1.0
    - 수정 후 통과: +0.5
    """
    if status == "pass":
        if attempt == 1:
            return 5.0
        else:
            # 수정 후 통과: +0.5
            return min(5.0, previous_score + 0.5)
    else:
        # 실패: -1.0
        return max(0.0, previous_score - 1.0)

def log_quality(agent, phase, task, status, error=None, duration=0):
    """품질 로그 기록"""
    previous_score = get_previous_score(agent, task)
    attempt = get_attempt_count(agent, task)
    score = calculate_score(previous_score, attempt, status)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent,
        "phase": phase,
        "task": task,
        "attempt": attempt,
        "status": status,
        "score": round(score, 1),
        "duration": duration,
        "previous_score": previous_score,
        "fixed": attempt > 1 and status == "pass"
    }

    if error:
        log_entry["error"] = error

    # 파일에 추가
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    # 결과 출력
    if status == "pass":
        print(f"✅ Logged: {agent} - {task} (PASS) - Score: {score:.1f}/5.0")
    else:
        print(f"❌ Logged: {agent} - {task} (FAIL) - Score: {score:.1f}/5.0")

    # 경고
    if score < 3.0:
        print(f"⚠️  WARNING: Quality score below 3.0! Immediate improvement needed.")

    if score == 0.0:
        print(f"💀 CRITICAL: Quality score is 0! Agent is completely broken.")

    return score

def main():
    if len(sys.argv) < 5:
        print("Usage: python .claude/track.py <agent> <phase> <task> <status> [error] [duration]")
        print()
        print("Example:")
        print("  python .claude/track.py 'context7-engineer' 'Phase 0' 'Verify docs' 'pass'")
        print("  python .claude/track.py 'debugger' 'Phase 1' 'Fix bug' 'fail' 'TypeError' 2.5")
        sys.exit(1)

    agent = sys.argv[1]
    phase = sys.argv[2]
    task = sys.argv[3]
    status = sys.argv[4]
    error = sys.argv[5] if len(sys.argv) > 5 else None
    duration = float(sys.argv[6]) if len(sys.argv) > 6 else 0

    if status not in ["pass", "fail"]:
        print(f"❌ Error: status must be 'pass' or 'fail', got '{status}'")
        sys.exit(1)

    log_quality(agent, phase, task, status, error, duration)

if __name__ == "__main__":
    main()
