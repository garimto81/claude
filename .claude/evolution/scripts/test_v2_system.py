#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Agent Quality System v2.0

Usage:
    python test_v2_system.py
"""

import json
import sys
import io
from pathlib import Path
from agent_quality_v2 import AgentQuality

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def test_scenario_1():
    """시나리오 1: 초기 실패 후 개선"""
    print("\n" + "="*60)
    print("🧪 Test Scenario 1: Initial Failures → Improvement")
    print("="*60)

    quality = AgentQuality("debugger", version="1.0.0")

    # 초기 실패 3회
    print("\n1️⃣ 초기 실패 3회...")
    for i in range(3):
        quality.record("Fix TypeError", "fail", duration=2.5, error=f"Error {i+1}")

    score1 = quality.get_score()
    print(f"   Score: {score1['weighted_avg']:.0%} (Grade: {score1['grade']}, Confidence: {score1['confidence']:.0%})")

    # 개선 7회
    print("\n2️⃣ 개선 7회...")
    for i in range(7):
        quality.record("Fix TypeError", "pass", duration=1.8)

    score2 = quality.get_score()
    print(f"   Score: {score2['weighted_avg']:.0%} (Grade: {score2['grade']}, Confidence: {score2['confidence']:.0%})")

    # 검증
    assert score2['weighted_avg'] > score1['weighted_avg'], "개선 후 점수가 높아야 함"
    assert score2['trend'] == "improving", "추세가 improving이어야 함"
    assert score2['confidence'] >= 0.6, "10회 시도 후 신뢰도 0.6 이상이어야 함"

    print("\n✅ Scenario 1 PASS")
    return quality


def test_scenario_2():
    """시나리오 2: Task별 독립 평가"""
    print("\n" + "="*60)
    print("🧪 Test Scenario 2: Task Independence")
    print("="*60)

    quality = AgentQuality("test-automator", version="1.0.0")

    # Task A: 100% 성공
    print("\n1️⃣ Task A (Unit Tests): 100% 성공 (5회)")
    for i in range(5):
        quality.record("Write unit tests", "pass", duration=2.0)

    # Task B: 0% 성공
    print("2️⃣ Task B (E2E Tests): 0% 성공 (5회)")
    for i in range(5):
        quality.record("Write E2E tests", "fail", duration=3.0, error="Timeout")

    score = quality.get_score()
    print(f"\n   Overall Score: {score['weighted_avg']:.0%} (Grade: {score['grade']})")

    # Task별 통계
    task_a = score['tasks']['Write unit tests']
    task_b = score['tasks']['Write E2E tests']

    print(f"   Task A: {task_a['weighted_rate']:.0%}")
    print(f"   Task B: {task_b['weighted_rate']:.0%}")

    # 검증
    assert task_a['weighted_rate'] == 1.0, "Task A는 100%여야 함"
    assert task_b['weighted_rate'] == 0.0, "Task B는 0%여야 함"
    assert 0.4 < score['weighted_avg'] < 0.6, "전체는 평균(50%) 근처여야 함"

    print("\n✅ Scenario 2 PASS")
    return quality


def test_scenario_3():
    """시나리오 3: 시간 가중치"""
    print("\n" + "="*60)
    print("🧪 Test Scenario 3: Time Weighting")
    print("="*60)

    quality = AgentQuality("frontend-developer", version="1.0.0")

    # 과거: 실패 5회
    print("\n1️⃣ 과거: 실패 5회")
    for i in range(5):
        quality.record("Build React component", "fail", duration=2.0)

    score1 = quality.get_score()
    print(f"   Score: {score1['weighted_avg']:.0%}")

    # 최근: 성공 5회
    print("2️⃣ 최근: 성공 5회")
    for i in range(5):
        quality.record("Build React component", "pass", duration=1.5)

    score2 = quality.get_score()
    print(f"   Score: {score2['weighted_avg']:.0%}")

    # 검증
    task_stats = score2['tasks']['Build React component']
    simple_rate = task_stats['success_rate']  # 50%
    weighted_rate = task_stats['weighted_rate']  # >50% (최근이 더 좋음)

    print(f"\n   Simple Rate: {simple_rate:.0%}")
    print(f"   Weighted Rate: {weighted_rate:.0%}")

    assert weighted_rate > simple_rate, "시간 가중치로 인해 weighted > simple이어야 함"
    assert weighted_rate > 0.6, "최근 성공으로 인해 60% 이상이어야 함"

    print("\n✅ Scenario 3 PASS")
    return quality


def test_scenario_4():
    """시나리오 4: 신뢰구간"""
    print("\n" + "="*60)
    print("🧪 Test Scenario 4: Confidence Intervals")
    print("="*60)

    quality = AgentQuality("database-optimizer", version="1.0.0")

    # 2회 시도
    print("\n1️⃣ 2회 시도 (신뢰도 낮음)")
    quality.record("Optimize SQL query", "pass", duration=1.0)
    quality.record("Optimize SQL query", "pass", duration=1.2)

    score1 = quality.get_score()
    print(f"   Score: {score1['weighted_avg']:.0%}, Confidence: {score1['confidence']:.0%}")
    assert score1['confidence'] == 0.4, "2회 시도 → 신뢰도 0.4"

    # 3회 추가 (총 5회)
    print("\n2️⃣ 3회 추가 (총 5회)")
    for i in range(3):
        quality.record("Optimize SQL query", "pass", duration=1.1)

    score2 = quality.get_score()
    print(f"   Score: {score2['weighted_avg']:.0%}, Confidence: {score2['confidence']:.0%}")
    assert score2['confidence'] == 0.6, "5회 시도 → 신뢰도 0.6"

    # 5회 추가 (총 10회)
    print("\n3️⃣ 5회 추가 (총 10회)")
    for i in range(5):
        quality.record("Optimize SQL query", "pass", duration=1.0)

    score3 = quality.get_score()
    print(f"   Score: {score3['weighted_avg']:.0%}, Confidence: {score3['confidence']:.0%}")
    assert score3['confidence'] == 0.8, "10회 시도 → 신뢰도 0.8"

    # 10회 추가 (총 20회)
    print("\n4️⃣ 10회 추가 (총 20회)")
    for i in range(10):
        quality.record("Optimize SQL query", "pass", duration=1.0)

    score4 = quality.get_score()
    print(f"   Score: {score4['weighted_avg']:.0%}, Confidence: {score4['confidence']:.0%}")
    assert score4['confidence'] == 1.0, "20회 시도 → 신뢰도 1.0"

    print("\n✅ Scenario 4 PASS")
    return quality


def test_scenario_5():
    """시나리오 5: 영구 복구 불가 방지"""
    print("\n" + "="*60)
    print("🧪 Test Scenario 5: Always Recoverable (No Death)")
    print("="*60)

    quality = AgentQuality("mobile-developer", version="1.0.0")

    # 10회 연속 실패
    print("\n1️⃣ 10회 연속 실패...")
    for i in range(10):
        quality.record("Build mobile app", "fail", duration=2.0)

    score1 = quality.get_score()
    print(f"   Score: {score1['weighted_avg']:.0%} (Grade: {score1['grade']})")
    assert score1['weighted_avg'] == 0.0, "10회 실패 → 0%"

    # 10회 연속 성공 (복구)
    print("\n2️⃣ 10회 연속 성공 (복구)...")
    for i in range(10):
        quality.record("Build mobile app", "pass", duration=1.5)

    score2 = quality.get_score()
    print(f"   Score: {score2['weighted_avg']:.0%} (Grade: {score2['grade']})")

    # 검증: 시간 가중치로 인해 최근 성공이 더 중요 → 높은 점수
    assert score2['weighted_avg'] > 0.8, "최근 성공으로 복구되어야 함"
    assert score2['trend'] == "improving", "추세가 improving이어야 함"

    print("\n✅ Scenario 5 PASS - Always Recoverable!")
    return quality


def test_all():
    """모든 테스트 실행"""
    print("\n" + "="*70)
    print("🚀 Agent Quality System v2.0 - Test Suite")
    print("="*70)

    tests = [
        test_scenario_1,
        test_scenario_2,
        test_scenario_3,
        test_scenario_4,
        test_scenario_5
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            failed += 1

    # 결과
    print("\n" + "="*70)
    print("📊 Test Results")
    print("="*70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 All tests passed! v2.0 system is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(test_all())
