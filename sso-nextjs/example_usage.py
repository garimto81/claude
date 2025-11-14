#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Tracking 사용 예시
"""

from utils.track import track_agent, quick_track


# ============================================================
# 예시 1: 기본 사용 (가장 간단)
# ============================================================

def example_1_basic():
    """가장 기본적인 사용법"""

    with track_agent("debugger", "Fix TypeError in auth.ts"):
        # 여기에 실제 작업 코드 작성
        print("버그 수정 중...")
        # fix_bug()
        # 성공하면 자동으로 "pass" 기록
        # 실패하면 자동으로 "fail" 기록


# ============================================================
# 예시 2: 테스트 실행
# ============================================================

def example_2_tests():
    """테스트 실행 자동 추적"""

    # Unit tests
    with track_agent("test-automator", "Run unit tests", phase="Phase 2"):
        import subprocess
        result = subprocess.run(['npm', 'test'], capture_output=True)
        if result.returncode != 0:
            raise Exception("Tests failed")

    # E2E tests
    with track_agent("playwright-engineer", "Run E2E tests", phase="Phase 5"):
        import subprocess
        result = subprocess.run(['npx', 'playwright', 'test'], capture_output=True)
        if result.returncode != 0:
            raise Exception("E2E tests failed")


# ============================================================
# 예시 3: 여러 Agent 순차 실행
# ============================================================

def example_3_multiple_agents():
    """Phase 0-6 워크플로우"""

    # Phase 0: 문서 검증
    with track_agent("context7-engineer", "Verify Next.js docs", phase="Phase 0"):
        print("문서 확인 중...")
        # verify_docs()

    # Phase 1: 구현
    with track_agent("fullstack-developer", "Implement auth", phase="Phase 1"):
        print("인증 구현 중...")
        # implement_auth()

    # Phase 2: 테스트
    with track_agent("test-automator", "Write tests", phase="Phase 2"):
        print("테스트 작성 중...")
        # write_tests()


# ============================================================
# 예시 4: 에러 처리
# ============================================================

def example_4_error_handling():
    """에러가 발생해도 자동으로 기록됨"""

    try:
        with track_agent("debugger", "Fix complex bug"):
            # 일부러 에러 발생
            raise ValueError("Something went wrong")

    except ValueError as e:
        print(f"에러 발생했지만 자동으로 기록됨: {e}")
        # 실패 기록은 자동으로 됨!


# ============================================================
# 예시 5: 조건부 실행
# ============================================================

def example_5_conditional():
    """조건에 따라 다른 Agent 사용"""

    task_type = "frontend"  # 또는 "backend"

    if task_type == "frontend":
        with track_agent("frontend-developer", "Build UI"):
            print("UI 개발 중...")
    else:
        with track_agent("backend-developer", "Build API"):
            print("API 개발 중...")


# ============================================================
# 예시 6: 수동 기록 (이미 완료된 작업)
# ============================================================

def example_6_manual():
    """이미 끝난 작업을 나중에 기록"""

    # 작업은 이미 끝났고, 기록만 하고 싶을 때
    quick_track("debugger", "Fixed bug manually", "pass", duration=120.5)
    quick_track("test-automator", "Manual test", "fail", error="Found edge case")


# ============================================================
# 실제 사용 예시 (실행)
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Agent Tracking 사용 예시")
    print("=" * 60)

    # 예시 1: 기본 사용
    print("\n[예시 1] 기본 사용")
    example_1_basic()

    # 예시 4: 에러 처리
    print("\n[예시 4] 에러 처리")
    example_4_error_handling()

    # 예시 6: 수동 기록
    print("\n[예시 6] 수동 기록")
    example_6_manual()

    print("\n✅ 모든 예시 완료!")
    print(f"로그 파일: .agent-quality-v2.jsonl")
