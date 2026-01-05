#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Evolution System - Integration Example
기존 agent 시스템과 통합 예제

Usage:
    python .claude/evolution/scripts/example_integration.py
"""

import time
import random
from track_agent_usage import get_tracker


def simulate_agent_execution(agent_name: str, phase: str, task: str, success_rate: float = 0.9):
    """
    Agent 실행 시뮬레이션

    Args:
        agent_name: Agent 이름
        phase: Phase
        task: Task 설명
        success_rate: 성공 확률 (0-1)

    Returns:
        실행 결과
    """
    print(f"\n🤖 Running {agent_name}...")
    print(f"   Phase: {phase}")
    print(f"   Task: {task}")

    # 랜덤 실행 시간 (0.5-2초)
    duration = random.uniform(0.5, 2.0)
    time.sleep(duration)

    # 랜덤 성공/실패
    success = random.random() < success_rate

    if success:
        result = {
            "status": "success",
            "output": f"{task} completed successfully",
            "duration": duration
        }
        print(f"   ✅ Success in {duration:.2f}s")
    else:
        result = {
            "status": "error",
            "error": f"Failed to complete {task}",
            "duration": duration
        }
        print(f"   ❌ Failed in {duration:.2f}s")

    return result


def demo_basic_tracking():
    """데모 1: 기본 추적"""
    print("\n" + "="*60)
    print("Demo 1: Basic Agent Tracking")
    print("="*60)

    tracker = get_tracker()

    # context7-engineer 추적
    with tracker.track("context7-engineer", phase="Phase 0", task="Verify React 18 docs"):
        _ = simulate_agent_execution(
            "context7-engineer",
            "Phase 0",
            "Verify React 18 docs",
            success_rate=0.95
        )

    # 피드백 수집
    tracker.collect_feedback(
        agent="context7-engineer",
        rating=5,
        comment="React 18 hooks verified successfully",
        effectiveness=0.95,
        suggestions="None"
    )

    tracker.flush()


def demo_multiple_agents():
    """데모 2: 여러 Agent 추적"""
    print("\n" + "="*60)
    print("Demo 2: Multiple Agents in Phase 0")
    print("="*60)

    tracker = get_tracker()

    agents = [
        ("context7-engineer", "Phase 0", "Verify library docs"),
        ("seq-engineer", "Phase 0", "Analyze requirements"),
        ("backend-architect", "Phase 0", "Design API structure")
    ]

    for agent_name, phase, task in agents:
        with tracker.track(agent_name, phase=phase, task=task):
            _ = simulate_agent_execution(agent_name, phase, task)

        # 랜덤 피드백
        tracker.collect_feedback(
            agent=agent_name,
            rating=random.randint(3, 5),
            comment=f"{agent_name} performed well",
            effectiveness=random.uniform(0.7, 1.0)
        )

    tracker.flush()


def demo_error_handling():
    """데모 3: 에러 핸들링"""
    print("\n" + "="*60)
    print("Demo 3: Error Handling")
    print("="*60)

    tracker = get_tracker()

    try:
        with tracker.track("playwright-engineer", phase="Phase 2", task="Run E2E tests"):
            # 의도적 에러
            result = simulate_agent_execution(
                "playwright-engineer",
                "Phase 2",
                "Run E2E tests",
                success_rate=0.3  # 낮은 성공률
            )

            if result["status"] == "error":
                raise RuntimeError(result["error"])

    except RuntimeError as e:
        print(f"   Caught error: {e}")
        # 에러는 자동으로 Langfuse에 기록됨

    tracker.flush()


def demo_decorator():
    """데모 4: Decorator 사용"""
    print("\n" + "="*60)
    print("Demo 4: Using @track_agent Decorator")
    print("="*60)

    from track_agent_usage import track_agent

    @track_agent("debugger", phase="Phase 1")
    def debug_error():
        """디버깅 함수 예제"""
        print("\n🐛 Debugging TypeError...")
        time.sleep(1.0)
        print("   ✅ Error fixed!")
        return {"status": "success", "fix": "Added type check"}

    @track_agent("security-auditor", phase="Phase 2")
    def security_audit():
        """보안 감사 함수 예제"""
        print("\n🔒 Running security audit...")
        time.sleep(1.5)
        print("   ✅ No vulnerabilities found")
        return {"status": "success", "vulnerabilities": 0}

    # 실행
    debug_error()
    security_audit()

    # Flush
    get_tracker().flush()


def demo_phase_workflow():
    """데모 5: 전체 Phase 워크플로우"""
    print("\n" + "="*60)
    print("Demo 5: Complete Phase 0 → Phase 1 Workflow")
    print("="*60)

    tracker = get_tracker()

    # Phase 0: PRD 작성
    print("\n📝 Phase 0: PRD Writing")
    phase0_agents = [
        ("context7-engineer", "Verify external library docs"),
        ("seq-engineer", "Analyze complex requirements"),
        ("backend-architect", "Design architecture")
    ]

    for agent, task in phase0_agents:
        with tracker.track(agent, phase="Phase 0", task=task):
            simulate_agent_execution(agent, "Phase 0", task)
        tracker.collect_feedback(
            agent=agent,
            rating=random.randint(4, 5),
            effectiveness=random.uniform(0.8, 1.0)
        )

    # Phase 1: 코드 구현
    print("\n💻 Phase 1: Implementation")
    phase1_agents = [
        ("context7-engineer", "Verify API changes"),
        ("test-automator", "Generate unit tests"),
        ("typescript-expert", "Define types"),
        ("debugger", "Fix TypeErrors")
    ]

    for agent, task in phase1_agents:
        with tracker.track(agent, phase="Phase 1", task=task):
            simulate_agent_execution(agent, "Phase 1", task)
        tracker.collect_feedback(
            agent=agent,
            rating=random.randint(3, 5),
            effectiveness=random.uniform(0.7, 0.95)
        )

    tracker.flush()

    print("\n✅ Workflow completed!")
    print(f"📊 Check dashboard: {tracker.host}")


def main():
    """메인 실행"""
    print("\n" + "="*60)
    print("Agent Evolution System - Integration Examples")
    print("="*60)

    try:
        # 데모 선택
        print("\n사용 가능한 데모:")
        print("  1. 기본 추적")
        print("  2. 여러 Agent 추적")
        print("  3. 에러 핸들링")
        print("  4. Decorator 사용")
        print("  5. 전체 Phase 워크플로우")
        print("  6. 모든 데모 실행")

        choice = input("\n데모 선택 (1-6, Enter=6): ").strip() or "6"

        demos = {
            "1": demo_basic_tracking,
            "2": demo_multiple_agents,
            "3": demo_error_handling,
            "4": demo_decorator,
            "5": demo_phase_workflow
        }

        if choice == "6":
            # 모든 데모 실행
            for demo_func in demos.values():
                demo_func()
                time.sleep(1)
        else:
            # 선택한 데모 실행
            demo_func = demos.get(choice)
            if demo_func:
                demo_func()
            else:
                print("❌ 잘못된 선택")

        print("\n" + "="*60)
        print("✅ All demos completed!")
        print("📊 Check Langfuse dashboard: http://localhost:3000")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
