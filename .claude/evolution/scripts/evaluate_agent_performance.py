#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Performance Evaluation System
Agent/스킬 사용 성능을 자동으로 판단하는 시스템

평가 방식:
1. 정량적 메트릭 (자동 측정)
   - Task completion rate (성공/실패율)
   - Avg duration (평균 실행 시간)
   - Error rate (에러율)
   - User satisfaction (평균 평점)

2. 정성적 메트릭 (LLM-as-Judge)
   - Output quality (출력 품질)
   - Task relevance (작업 관련성)
   - Code quality (코드 품질)

3. 비교 평가
   - Baseline과 비교
   - Phase별 비교
   - Agent 간 비교

Usage:
    python evaluate_agent_performance.py --agent context7-engineer
    python evaluate_agent_performance.py --agent all --phase "Phase 0"
    python evaluate_agent_performance.py --report
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

try:
    from langfuse import Langfuse
except ImportError:
    print("❌ langfuse 패키지가 설치되지 않았습니다.")
    sys.exit(1)


@dataclass
class PerformanceMetrics:
    """Agent 성능 메트릭"""
    agent_name: str
    total_runs: int
    success_rate: float  # 0-1
    avg_duration: float  # seconds
    error_rate: float  # 0-1
    avg_user_rating: Optional[float]  # 0-1 (5점 만점의 정규화)
    avg_effectiveness: Optional[float]  # 0-1
    improvement_suggestions_count: int

    # 추가 메트릭
    p95_duration: Optional[float] = None  # 95 percentile
    retry_rate: Optional[float] = None

    @property
    def performance_score(self) -> float:
        """
        종합 성능 점수 (0-100)

        가중치:
        - Success rate: 30%
        - User rating: 25%
        - Effectiveness: 20%
        - Speed (inverse duration): 15%
        - Error rate (inverse): 10%
        """
        # Success rate (30%)
        success_score = self.success_rate * 30

        # User rating (25%)
        rating_score = (self.avg_user_rating or 0.7) * 25

        # Effectiveness (20%)
        effectiveness_score = (self.avg_effectiveness or 0.7) * 20

        # Speed (15%) - inverse of duration
        # 0-2초: 100점, 2-5초: 75점, 5초+: 50점
        if self.avg_duration <= 2:
            speed_score = 15
        elif self.avg_duration <= 5:
            speed_score = 15 * (1 - (self.avg_duration - 2) / 3 * 0.25)
        else:
            speed_score = 15 * 0.5

        # Error rate (10%) - inverse
        error_score = (1 - self.error_rate) * 10

        total = success_score + rating_score + effectiveness_score + speed_score + error_score
        return round(total, 2)

    @property
    def grade(self) -> str:
        """성적 등급 (S/A/B/C/D/F)"""
        score = self.performance_score
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"

    @property
    def status(self) -> str:
        """상태 판정"""
        score = self.performance_score
        if score >= 80:
            return "✅ Excellent"
        elif score >= 70:
            return "✔️ Good"
        elif score >= 60:
            return "⚠️ Acceptable"
        else:
            return "❌ Needs Improvement"


class AgentEvaluator:
    """Agent 성능 평가기"""

    def __init__(self):
        """Initialize Langfuse client"""
        self.client = Langfuse(
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:3000')
        )

    def get_agent_metrics(
        self,
        agent_name: str,
        days: int = 7,
        phase: Optional[str] = None
    ) -> PerformanceMetrics:
        """
        Agent의 성능 메트릭 계산

        Args:
            agent_name: Agent 이름
            days: 최근 N일
            phase: Phase 필터 (optional)

        Returns:
            PerformanceMetrics
        """
        # TODO: Langfuse API로 데이터 가져오기
        # 현재는 시뮬레이션

        # 실제 구현에서는:
        # traces = self.client.get_traces(
        #     filter={
        #         "metadata.agent": agent_name,
        #         "timestamp": f">{days}d"
        #     }
        # )

        # 시뮬레이션 데이터
        import random

        total_runs = random.randint(10, 50)
        success_count = int(total_runs * random.uniform(0.7, 0.98))
        error_count = total_runs - success_count

        durations = [random.uniform(0.5, 5.0) for _ in range(total_runs)]
        ratings = [random.uniform(0.6, 1.0) for _ in range(int(total_runs * 0.8))]
        effectiveness = [random.uniform(0.6, 0.95) for _ in range(int(total_runs * 0.7))]

        metrics = PerformanceMetrics(
            agent_name=agent_name,
            total_runs=total_runs,
            success_rate=success_count / total_runs,
            avg_duration=sum(durations) / len(durations),
            error_rate=error_count / total_runs,
            avg_user_rating=sum(ratings) / len(ratings) if ratings else None,
            avg_effectiveness=sum(effectiveness) / len(effectiveness) if effectiveness else None,
            improvement_suggestions_count=random.randint(0, 5),
            p95_duration=sorted(durations)[int(len(durations) * 0.95)],
            retry_rate=random.uniform(0, 0.1)
        )

        return metrics

    def compare_agents(self, agents: List[str], phase: Optional[str] = None) -> Dict:
        """
        여러 Agent 성능 비교

        Args:
            agents: Agent 이름 리스트
            phase: Phase 필터

        Returns:
            비교 결과
        """
        results = {}
        for agent in agents:
            metrics = self.get_agent_metrics(agent, phase=phase)
            results[agent] = metrics

        # 순위 매기기
        sorted_agents = sorted(
            results.items(),
            key=lambda x: x[1].performance_score,
            reverse=True
        )

        return {
            "agents": results,
            "ranking": [(agent, metrics.performance_score) for agent, metrics in sorted_agents],
            "best": sorted_agents[0][0],
            "worst": sorted_agents[-1][0]
        }

    def generate_report(self, agent_name: str, metrics: PerformanceMetrics) -> str:
        """
        상세 리포트 생성

        Args:
            agent_name: Agent 이름
            metrics: 성능 메트릭

        Returns:
            마크다운 리포트
        """
        report = f"""
# Performance Report: {agent_name}

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Period**: Last 7 days

---

## 📊 Overall Score

**Performance Score**: {metrics.performance_score}/100 (Grade: {metrics.grade})
**Status**: {metrics.status}

---

## 📈 Metrics Breakdown

### 1. Task Completion
- **Total Runs**: {metrics.total_runs}
- **Success Rate**: {metrics.success_rate * 100:.1f}%
- **Error Rate**: {metrics.error_rate * 100:.1f}%

### 2. Speed
- **Avg Duration**: {metrics.avg_duration:.2f}s
- **P95 Duration**: {metrics.p95_duration:.2f}s

### 3. User Satisfaction
- **Avg Rating**: {(metrics.avg_user_rating or 0) * 5:.1f}/5
- **Avg Effectiveness**: {(metrics.avg_effectiveness or 0) * 100:.1f}%

### 4. Improvement
- **Suggestions Count**: {metrics.improvement_suggestions_count}

---

## 🎯 Performance Analysis

"""

        # 분석
        if metrics.performance_score >= 80:
            report += """
### ✅ Strengths
- High success rate and user satisfaction
- Consistently fast execution
- Minimal errors
"""
        elif metrics.performance_score >= 60:
            report += """
### ⚠️ Areas for Improvement
- Success rate could be improved
- Consider optimizing duration
- Review user feedback for common issues
"""
        else:
            report += """
### ❌ Critical Issues
- **Low success rate**: Needs immediate attention
- **High error rate**: Review error logs
- **User dissatisfaction**: Analyze feedback
"""

        # 추천 액션
        report += """
---

## 💡 Recommended Actions

"""

        if metrics.success_rate < 0.8:
            report += "1. ⚠️ **Improve success rate**: Review failed traces and fix common errors\n"

        if metrics.avg_duration > 3.0:
            report += "2. ⏱️ **Optimize speed**: Consider caching or parallel execution\n"

        if metrics.avg_user_rating and metrics.avg_user_rating < 0.7:
            report += "3. 📝 **Address user feedback**: Review improvement suggestions\n"

        if metrics.error_rate > 0.1:
            report += "4. 🐛 **Reduce errors**: Implement better error handling and retries\n"

        if metrics.improvement_suggestions_count > 3:
            report += f"5. 🔧 **Process suggestions**: {metrics.improvement_suggestions_count} improvement ideas pending\n"

        report += """
---

## 🔗 Next Steps

1. Review detailed traces in Langfuse dashboard
2. Implement recommended improvements
3. Re-evaluate in 1 week
"""

        return report

    def evaluate_baseline(self, agent_name: str) -> Dict:
        """
        Baseline 성능 설정

        Args:
            agent_name: Agent 이름

        Returns:
            Baseline 메트릭
        """
        metrics = self.get_agent_metrics(agent_name, days=30)

        baseline = {
            "agent": agent_name,
            "date": datetime.now().isoformat(),
            "performance_score": metrics.performance_score,
            "success_rate": metrics.success_rate,
            "avg_duration": metrics.avg_duration,
            "avg_user_rating": metrics.avg_user_rating
        }

        # 저장
        baseline_file = Path(__file__).parent.parent / "config" / f"{agent_name}-baseline.json"
        baseline_file.parent.mkdir(exist_ok=True)

        import json
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)

        print(f"✅ Baseline saved: {baseline_file}")
        return baseline


def print_metrics_table(agents_metrics: Dict[str, PerformanceMetrics]):
    """메트릭 테이블 출력"""
    print("\n" + "="*100)
    print(f"{'Agent':<25} {'Runs':<8} {'Success':<10} {'Duration':<12} {'Rating':<10} {'Score':<8} {'Grade':<8} {'Status':<20}")
    print("="*100)

    for agent, metrics in sorted(agents_metrics.items(), key=lambda x: x[1].performance_score, reverse=True):
        print(
            f"{agent:<25} "
            f"{metrics.total_runs:<8} "
            f"{metrics.success_rate*100:>6.1f}%   "
            f"{metrics.avg_duration:>6.2f}s      "
            f"{(metrics.avg_user_rating or 0)*5:>4.1f}/5    "
            f"{metrics.performance_score:>6.1f}  "
            f"{metrics.grade:<8} "
            f"{metrics.status:<20}"
        )

    print("="*100 + "\n")


def main():
    """메인 실행"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent 성능 평가 시스템",
        epilog="Example: python evaluate_agent_performance.py --agent context7-engineer"
    )

    parser.add_argument('--agent', help='Agent 이름 (또는 "all")')
    parser.add_argument('--phase', help='Phase 필터')
    parser.add_argument('--days', type=int, default=7, help='최근 N일')
    parser.add_argument('--report', action='store_true', help='상세 리포트 생성')
    parser.add_argument('--baseline', action='store_true', help='Baseline 설정')
    parser.add_argument('--compare', action='store_true', help='Agent 비교')

    args = parser.parse_args()

    evaluator = AgentEvaluator()

    # Agent 리스트
    all_agents = [
        "context7-engineer",
        "playwright-engineer",
        "seq-engineer",
        "test-automator",
        "typescript-expert",
        "debugger",
        "database-optimizer",
        "security-auditor",
        "deployment-engineer",
        "fullstack-developer",
        "frontend-developer",
        "backend-architect",
        "data-scientist",
        "code-reviewer",
        "task-decomposition"
    ]

    if args.baseline:
        # Baseline 설정
        agent = args.agent or "context7-engineer"
        print(f"📊 Setting baseline for {agent}...")
        baseline = evaluator.evaluate_baseline(agent)
        print(f"✅ Baseline score: {baseline['performance_score']}")
        return

    if args.compare:
        # Agent 비교
        agents = all_agents if args.agent == "all" else [args.agent]
        print(f"📊 Comparing {len(agents)} agents...")

        comparison = evaluator.compare_agents(agents, phase=args.phase)

        print_metrics_table(comparison["agents"])

        print(f"🥇 Best: {comparison['best']}")
        print(f"🥉 Worst: {comparison['worst']}")

        return

    if args.agent:
        # 단일 Agent 평가
        print(f"📊 Evaluating {args.agent}...")
        metrics = evaluator.get_agent_metrics(args.agent, days=args.days, phase=args.phase)

        print(f"\n{'='*60}")
        print(f"Agent: {metrics.agent_name}")
        print(f"Score: {metrics.performance_score}/100 (Grade: {metrics.grade})")
        print(f"Status: {metrics.status}")
        print(f"{'='*60}\n")

        print(f"Total Runs: {metrics.total_runs}")
        print(f"Success Rate: {metrics.success_rate * 100:.1f}%")
        print(f"Avg Duration: {metrics.avg_duration:.2f}s")
        print(f"Avg Rating: {(metrics.avg_user_rating or 0) * 5:.1f}/5")
        print(f"Avg Effectiveness: {(metrics.avg_effectiveness or 0) * 100:.1f}%")

        if args.report:
            # 상세 리포트
            report = evaluator.generate_report(args.agent, metrics)

            report_file = Path(__file__).parent.parent / "data" / f"{args.agent}-report-{datetime.now().strftime('%Y%m%d')}.md"
            report_file.parent.mkdir(exist_ok=True)

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"\n✅ Report saved: {report_file}")
            print(report)

    else:
        # 전체 요약
        print("📊 All Agents Performance Summary\n")

        agents_metrics = {}
        for agent in all_agents:
            metrics = evaluator.get_agent_metrics(agent, days=args.days, phase=args.phase)
            agents_metrics[agent] = metrics

        print_metrics_table(agents_metrics)


if __name__ == "__main__":
    main()
