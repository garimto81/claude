#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Quality System v2.0 - Core Logic
합리적인 점수 시스템: Task별 독립 평가 + 시간 가중치 + 신뢰구간

Usage:
    from agent_quality_v2 import AgentQuality

    quality = AgentQuality("debugger", version="1.0.0")
    quality.record("Fix bug", "pass", duration=1.5)
    score = quality.get_score()
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import math


class AgentQuality:
    """Agent 품질 추적 (v2.0)"""

    def __init__(self, agent_name: str, version: str = "1.0.0", log_file: Optional[Path] = None):
        self.agent = agent_name
        self.version = version
        self.log_file = log_file or Path(".agent-quality-v2.jsonl")
        self.tasks = defaultdict(lambda: {"attempts": []})

        # 기존 로그 로드
        self._load_logs()

    def _load_logs(self):
        """기존 로그 로드"""
        if not self.log_file.exists():
            return

        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    log = json.loads(line.strip())
                    if log['agent'] == self.agent:
                        task = log['task']
                        self.tasks[task]["attempts"].append(log)
                except:
                    pass

    def record(
        self,
        task: str,
        status: str,
        duration: float = 0,
        error: Optional[str] = None,
        auto_detected: bool = False,
        test_output: Optional[str] = None,
        phase: Optional[str] = None
    ):
        """
        Agent 사용 기록

        Args:
            task: Task 이름
            status: "pass" or "fail"
            duration: 실행 시간 (초)
            error: 에러 메시지
            auto_detected: 자동 감지 여부 (테스트/빌드)
            test_output: 테스트 출력
            phase: Phase (예: "Phase 1")
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent": self.agent,
            "version": self.version,
            "phase": phase,
            "task": task,
            "status": status,
            "duration": duration,
            "auto_detected": auto_detected
        }

        if error:
            log_entry["error"] = error
        if test_output:
            log_entry["test_output"] = test_output

        # 메모리에 추가
        self.tasks[task]["attempts"].append(log_entry)

        # 파일에 기록
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def calculate_task_statistics(self, attempts: List[Dict]) -> Dict:
        """Task 통계 계산"""
        if not attempts:
            return {
                "total_attempts": 0,
                "successes": 0,
                "failures": 0,
                "success_rate": None,
                "weighted_rate": None,
                "avg_duration": None,
                "last_status": None,
                "confidence": 0.0
            }

        # 기본 통계
        total = len(attempts)
        successes = sum(1 for a in attempts if a['status'] == 'pass')
        failures = total - successes

        # 단순 성공률
        success_rate = successes / total if total > 0 else 0

        # 시간 가중 성공률 (최근 10개)
        recent = attempts[-10:]
        n = len(recent)
        if n > 0:
            # 지수 가중치 (최근일수록 높음)
            weights = [0.5 ** (n - i - 1) for i in range(n)]
            total_weight = sum(weights)

            weighted_sum = sum(
                w * (1 if a['status'] == 'pass' else 0)
                for w, a in zip(weights, recent)
            )
            weighted_rate = weighted_sum / total_weight
        else:
            weighted_rate = success_rate

        # 평균 duration
        durations = [a['duration'] for a in attempts if a.get('duration', 0) > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # 신뢰도 (Wilson score interval 기반 단순화)
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
            "total_attempts": total,
            "successes": successes,
            "failures": failures,
            "success_rate": success_rate,
            "weighted_rate": weighted_rate,
            "avg_duration": round(avg_duration, 2),
            "last_status": attempts[-1]['status'],
            "confidence": confidence
        }

    def calculate_trend(self, attempts: List[Dict]) -> str:
        """성능 추세 계산"""
        if len(attempts) < 4:
            return "insufficient_data"

        # 전반부 vs 후반부
        mid = len(attempts) // 2
        first_half = attempts[:mid]
        second_half = attempts[mid:]

        first_rate = sum(1 for a in first_half if a['status'] == 'pass') / len(first_half)
        second_rate = sum(1 for a in second_half if a['status'] == 'pass') / len(second_half)

        diff = second_rate - first_rate

        if diff > 0.15:
            return "improving"
        elif diff < -0.15:
            return "declining"
        else:
            return "stable"

    def get_grade(self, rate: float) -> str:
        """성공률 → 등급"""
        if rate >= 0.9: return "S"
        if rate >= 0.8: return "A"
        if rate >= 0.7: return "B"
        if rate >= 0.6: return "C"
        if rate >= 0.5: return "D"
        return "F"

    def get_status(self, rate: float) -> str:
        """성공률 → 상태"""
        if rate >= 0.8: return "✅ Excellent"
        if rate >= 0.7: return "✔️ Good"
        if rate >= 0.6: return "⚠️ Acceptable"
        if rate >= 0.5: return "⚠️ Poor"
        return "❌ Critical"

    def get_score(self) -> Dict:
        """Agent 전체 점수 계산"""
        if not self.tasks:
            return {
                "avg_success_rate": None,
                "weighted_avg": None,
                "confidence": 0.0,
                "grade": "N/A",
                "status": "No data",
                "trend": "insufficient_data",
                "total_tasks": 0,
                "tasks": {}
            }

        # Task별 통계 계산
        task_stats = {}
        task_rates = []
        task_confidences = []

        for task, data in self.tasks.items():
            stats = self.calculate_task_statistics(data["attempts"])
            trend = self.calculate_trend(data["attempts"])

            task_stats[task] = {
                **stats,
                "trend": trend
            }

            if stats['weighted_rate'] is not None:
                task_rates.append(stats['weighted_rate'])
                task_confidences.append(stats['confidence'])

        # 전체 평균
        if task_rates:
            avg_rate = sum(task_rates) / len(task_rates)
            avg_confidence = sum(task_confidences) / len(task_confidences)

            # 전체 추세
            all_attempts = []
            for data in self.tasks.values():
                all_attempts.extend(data["attempts"])
            all_attempts.sort(key=lambda x: x['timestamp'])
            overall_trend = self.calculate_trend(all_attempts)
        else:
            avg_rate = 0.0
            avg_confidence = 0.0
            overall_trend = "insufficient_data"

        return {
            "avg_success_rate": round(avg_rate, 3),
            "weighted_avg": round(avg_rate, 3),
            "confidence": round(avg_confidence, 2),
            "grade": self.get_grade(avg_rate),
            "status": self.get_status(avg_rate),
            "trend": overall_trend,
            "total_tasks": len(task_stats),
            "tasks": task_stats
        }

    def print_report(self):
        """리포트 출력"""
        score = self.get_score()

        if score['avg_success_rate'] is None:
            print(f"\n❌ {self.agent}: No data")
            return

        print(f"\n{'='*60}")
        print(f"📊 {self.agent} v{self.version} - Quality Report (v2.0)")
        print(f"{'='*60}\n")

        # Overall
        uncertainty = 1 - score['confidence']
        print(f"Overall Score: {score['weighted_avg']:.0%} ± {uncertainty:.0%} (Grade: {score['grade']})")
        print(f"Status: {score['status']}")
        print(f"Trend: {score['trend']}")
        print(f"Confidence: {score['confidence']:.0%} ({sum(len(d['attempts']) for d in self.tasks.values())} total attempts)")
        print()

        # Task breakdown
        print("Task Breakdown:")
        print(f"{'Task':<40} {'Rate':<8} {'Weight':<8} {'Conf':<6} {'Trend':<10}")
        print("-" * 80)

        for task, stats in score['tasks'].items():
            task_display = task[:37] + "..." if len(task) > 40 else task
            trend_icon = {"improving": "↗️", "stable": "→", "declining": "↘️", "insufficient_data": "?"}.get(stats['trend'], "?")

            print(
                f"{task_display:<40} "
                f"{stats['success_rate']:.0%}      "
                f"{stats['weighted_rate']:.0%}      "
                f"{stats['confidence']:.1f}    "
                f"{trend_icon} {stats['trend']:<10}"
            )

        print()


def main():
    """테스트"""
    print("🧪 Testing AgentQuality v2.0...\n")

    quality = AgentQuality("debugger", version="1.0.0")

    # Scenario: 초기 실패 후 개선
    print("Scenario: Initial failures, then improvement")

    # 초기 실패
    for i in range(3):
        quality.record("Fix TypeError", "fail", duration=2.5, error=f"Error {i}")

    # 개선
    for i in range(7):
        quality.record("Fix TypeError", "pass", duration=1.8)

    # 다른 Task
    quality.record("Fix ReferenceError", "pass", duration=2.1)
    quality.record("Fix ReferenceError", "pass", duration=1.9)

    # 리포트
    quality.print_report()

    # 점수 확인
    score = quality.get_score()
    print("\nJSON Output:")
    print(json.dumps(score, indent=2))


if __name__ == "__main__":
    main()
