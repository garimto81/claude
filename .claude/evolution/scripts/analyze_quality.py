#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Quality 분석 도구
전역 레포에서 수집된 품질 로그를 분석

Usage:
    python analyze_quality.py --summary
    python analyze_quality.py --agent context7-engineer
    python analyze_quality.py --repo sso-nextjs
    python analyze_quality.py --trend --days 30
    python analyze_quality.py --alerts
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict

class QualityAnalyzer:
    """품질 분석기"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def load_summary(self) -> Dict:
        """요약 로드"""
        summary_file = self.data_dir / "quality-summary.json"

        if not summary_file.exists():
            print("⚠️  No summary found. Run sync_quality_logs.py first.")
            return {}

        with open(summary_file, 'r') as f:
            return json.load(f)

    def load_logs(self, repo_name: str = None) -> List[Dict]:
        """로그 로드"""
        logs = []

        if repo_name:
            log_files = [self.data_dir / f"{repo_name}.jsonl"]
        else:
            log_files = self.data_dir.glob("*.jsonl")

        for log_file in log_files:
            if log_file.name.startswith("quality-summary"):
                continue

            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        log['repo'] = log_file.stem
                        logs.append(log)
                    except:
                        pass

        return logs

    def print_summary(self):
        """요약 출력"""
        summary = self.load_summary()

        if not summary:
            return

        print("\n" + "="*80)
        print("📊 Agent Quality Summary (All Repos)")
        print("="*80 + "\n")

        for repo, agents in summary.items():
            print(f"🔹 {repo}")

            if not agents:
                print("  (No data)\n")
                continue

            # 점수별 정렬
            sorted_agents = sorted(
                agents.items(),
                key=lambda x: x[1]['current_score'],
                reverse=True
            )

            for agent, scores in sorted_agents:
                status = self._get_status_icon(scores['current_score'])
                grade = self._get_grade(scores['current_score'])

                print(
                    f"  {status} {agent:<25} "
                    f"{scores['current_score']:.1f}/5.0 ({grade}) "
                    f"| avg: {scores['avg_score']:.1f} "
                    f"| {scores['passes']}✓ {scores['fails']}✗ "
                    f"| tasks: {len(scores['tasks'])}"
                )

            print()

        print("="*80 + "\n")

    def analyze_agent(self, agent_name: str):
        """특정 Agent 상세 분석"""
        logs = self.load_logs()
        agent_logs = [log for log in logs if log['agent'] == agent_name]

        if not agent_logs:
            print(f"❌ No logs found for agent: {agent_name}")
            return

        # 통계
        total_attempts = len(agent_logs)
        passes = sum(1 for log in agent_logs if log['status'] == 'pass')
        fails = total_attempts - passes
        current_score = agent_logs[-1]['score']

        # 에러 분석
        errors = defaultdict(int)
        for log in agent_logs:
            if log['status'] == 'fail' and log.get('error'):
                errors[log['error']] += 1

        # 출력
        print(f"\n{'='*60}")
        print(f"📊 {agent_name} - Detailed Analysis")
        print(f"{'='*60}\n")

        # 현재 상태
        status = self._get_status_icon(current_score)
        grade = self._get_grade(current_score)
        print(f"Current Score: {status} {current_score:.1f}/5.0 (Grade: {grade})")
        print(f"Status: {self._get_status_text(current_score)}\n")

        # 통계
        print(f"Total Attempts: {total_attempts}")
        print(f"Passes: {passes} ({passes/total_attempts*100:.1f}%)")
        print(f"Failures: {fails} ({fails/total_attempts*100:.1f}%)")
        print()

        # Task 목록
        tasks = set(log['task'] for log in agent_logs)
        print(f"Tasks ({len(tasks)}):")
        for task in tasks:
            task_logs = [log for log in agent_logs if log['task'] == task]
            task_passes = sum(1 for log in task_logs if log['status'] == 'pass')
            task_fails = len(task_logs) - task_passes
            print(f"  - {task}: {task_passes}✓ {task_fails}✗")
        print()

        # 에러 분석
        if errors:
            print(f"Common Errors:")
            for error, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {error}: {count}회")
            print()

        # 추세
        print("Score Trend:")
        for i, log in enumerate(agent_logs[-10:], 1):  # 최근 10개
            status_icon = "✅" if log['status'] == 'pass' else "❌"
            print(f"  {i}. {status_icon} {log['task'][:40]:<40} {log['score']:.1f}")
        print()

        # 권장 사항
        print("💡 Recommendations:")
        if current_score < 3.0:
            print("  🚨 URGENT: Quality critically low!")
            print("  1. Review all failure logs")
            print("  2. Fix common errors immediately")
            print("  3. Consider rewriting agent instructions")
        elif current_score < 4.0:
            print("  ⚠️  Quality needs improvement")
            print("  1. Address common error patterns")
            print("  2. Add error handling/retry logic")
        else:
            print("  ✅ Quality is good, maintain current practices")

        if errors:
            print(f"\n  Focus on fixing:")
            for error, count in list(sorted(errors.items(), key=lambda x: x[1], reverse=True))[:3]:
                print(f"    - {error}")

        print(f"\n{'='*60}\n")

    def analyze_repo(self, repo_name: str):
        """특정 레포 분석"""
        logs = self.load_logs(repo_name)

        if not logs:
            print(f"❌ No logs found for repo: {repo_name}")
            return

        # Agent별 그룹화
        agent_stats = defaultdict(lambda: {'passes': 0, 'fails': 0, 'score': 0})

        for log in logs:
            agent = log['agent']
            if log['status'] == 'pass':
                agent_stats[agent]['passes'] += 1
            else:
                agent_stats[agent]['fails'] += 1
            agent_stats[agent]['score'] = log['score']

        # 출력
        print(f"\n{'='*60}")
        print(f"📊 {repo_name} - Repository Analysis")
        print(f"{'='*60}\n")

        print(f"Total Logs: {len(logs)}")
        print(f"Agents: {len(agent_stats)}\n")

        print(f"{'Agent':<25} {'Score':<10} {'Pass':<8} {'Fail':<8} {'Total':<8}")
        print("-"*60)

        for agent, stats in sorted(agent_stats.items(), key=lambda x: x[1]['score'], reverse=True):
            total = stats['passes'] + stats['fails']
            status = self._get_status_icon(stats['score'])

            print(
                f"{agent:<25} "
                f"{status} {stats['score']:.1f}/5.0  "
                f"{stats['passes']:<8} "
                f"{stats['fails']:<8} "
                f"{total:<8}"
            )

        print(f"\n{'='*60}\n")

    def analyze_trend(self, days: int = 30):
        """시간별 추세 분석"""
        logs = self.load_logs()

        if not logs:
            print("❌ No logs found")
            return

        # 날짜별 그룹화
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_logs = []

        for log in logs:
            try:
                log_time = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                if log_time >= cutoff:
                    recent_logs.append(log)
            except:
                pass

        if not recent_logs:
            print(f"❌ No logs in last {days} days")
            return

        # Agent별 추세
        agent_trends = defaultdict(list)
        for log in sorted(recent_logs, key=lambda x: x['timestamp']):
            agent_trends[log['agent']].append({
                'timestamp': log['timestamp'],
                'score': log['score']
            })

        # 출력
        print(f"\n{'='*60}")
        print(f"📈 Quality Trend (Last {days} days)")
        print(f"{'='*60}\n")

        for agent, trend in agent_trends.items():
            if len(trend) < 2:
                continue

            start_score = trend[0]['score']
            end_score = trend[-1]['score']
            change = end_score - start_score

            if change > 0:
                trend_icon = "📈"
                trend_text = f"+{change:.1f}"
            elif change < 0:
                trend_icon = "📉"
                trend_text = f"{change:.1f}"
            else:
                trend_icon = "➡️"
                trend_text = "0.0"

            print(f"{trend_icon} {agent:<25} {start_score:.1f} → {end_score:.1f} ({trend_text})")

        print(f"\n{'='*60}\n")

    def check_alerts(self):
        """품질 알림 확인"""
        summary = self.load_summary()

        if not summary:
            return

        alerts = []

        for repo, agents in summary.items():
            for agent, scores in agents.items():
                score = scores['current_score']

                if score == 0:
                    alerts.append({
                        'level': 'CRITICAL',
                        'repo': repo,
                        'agent': agent,
                        'score': score,
                        'message': 'Agent completely broken (score 0)'
                    })
                elif score < 2.0:
                    alerts.append({
                        'level': 'URGENT',
                        'repo': repo,
                        'agent': agent,
                        'score': score,
                        'message': 'Quality critically low'
                    })
                elif score < 3.0:
                    alerts.append({
                        'level': 'WARNING',
                        'repo': repo,
                        'agent': agent,
                        'score': score,
                        'message': 'Quality below acceptable level'
                    })

        if not alerts:
            print("\n✅ No quality alerts. All agents performing well!\n")
            return

        # 출력
        print(f"\n{'='*60}")
        print(f"🚨 Quality Alerts ({len(alerts)})")
        print(f"{'='*60}\n")

        for alert in sorted(alerts, key=lambda x: x['score']):
            level_icons = {
                'CRITICAL': '💀',
                'URGENT': '🚨',
                'WARNING': '⚠️'
            }

            icon = level_icons.get(alert['level'], '⚠️')
            print(f"{icon} [{alert['level']}] {alert['repo']}/{alert['agent']}")
            print(f"   Score: {alert['score']:.1f}/5.0 - {alert['message']}\n")

        print(f"{'='*60}\n")

    def _get_status_icon(self, score: float) -> str:
        """점수에 따른 상태 아이콘"""
        if score >= 4.0:
            return "✅"
        elif score >= 3.0:
            return "⚠️"
        else:
            return "❌"

    def _get_grade(self, score: float) -> str:
        """점수에 따른 등급"""
        if score >= 4.5:
            return "S"
        elif score >= 4.0:
            return "A"
        elif score >= 3.0:
            return "B"
        elif score >= 2.0:
            return "C"
        elif score >= 1.0:
            return "D"
        else:
            return "F"

    def _get_status_text(self, score: float) -> str:
        """점수에 따른 상태 텍스트"""
        if score >= 4.5:
            return "✅ Excellent"
        elif score >= 4.0:
            return "✔️ Good"
        elif score >= 3.0:
            return "⚠️ Acceptable"
        elif score >= 2.0:
            return "❌ Poor"
        else:
            return "💀 Critical"


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent 품질 분석 도구",
        epilog="Example: python analyze_quality.py --summary"
    )

    parser.add_argument('--summary', action='store_true', help='전체 요약')
    parser.add_argument('--agent', help='특정 Agent 분석')
    parser.add_argument('--repo', help='특정 레포 분석')
    parser.add_argument('--trend', action='store_true', help='추세 분석')
    parser.add_argument('--days', type=int, default=30, help='추세 기간 (일)')
    parser.add_argument('--alerts', action='store_true', help='품질 알림 확인')

    args = parser.parse_args()

    # 데이터 디렉토리
    global_repo = Path(__file__).parent.parent.parent.parent.resolve()
    data_dir = global_repo / ".claude/evolution/data"

    if not data_dir.exists():
        print("❌ Data directory not found. Run sync_quality_logs.py first.")
        return

    analyzer = QualityAnalyzer(data_dir)

    if args.summary:
        analyzer.print_summary()
    elif args.agent:
        analyzer.analyze_agent(args.agent)
    elif args.repo:
        analyzer.analyze_repo(args.repo)
    elif args.trend:
        analyzer.analyze_trend(args.days)
    elif args.alerts:
        analyzer.check_alerts()
    else:
        # 기본: 요약 + 알림
        analyzer.print_summary()
        analyzer.check_alerts()


if __name__ == "__main__":
    main()
