#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Quality Analyzer v2.0
.agent-quality-v2.jsonl 로그 분석 및 리포팅

Usage:
    # 전체 요약
    python analyze_quality2.py --summary

    # 특정 Agent 상세 분석
    python analyze_quality2.py --agent debugger

    # 특정 Agent + Version
    python analyze_quality2.py --agent debugger --version 1.2.0

    # 추세 분석
    python analyze_quality2.py --trend

    # 경고 확인 (낮은 성능)
    python analyze_quality2.py --alerts

    # 특정 Task 분석
    python analyze_quality2.py --task "Fix TypeError"

    # 날짜 범위 필터
    python analyze_quality2.py --summary --start 2025-01-01 --end 2025-01-14
"""

import json
import argparse
import sys
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Import core logic
from agent_quality_v2 import AgentQuality


LOG_FILE = Path(".agent-quality-v2.jsonl")


def load_logs(
    log_file: Path = LOG_FILE,
    agent: Optional[str] = None,
    version: Optional[str] = None,
    task: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict]:
    """로그 파일 로드 (필터링 지원)"""
    if not log_file.exists():
        print(f"❌ 로그 파일이 없습니다: {log_file}")
        return []

    logs = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                log = json.loads(line.strip())

                # 필터링
                if agent and log.get('agent') != agent:
                    continue
                if version and log.get('version') != version:
                    continue
                if task and log.get('task') != task:
                    continue

                # 날짜 필터
                if start_date or end_date:
                    log_date = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                    if start_date:
                        start = datetime.fromisoformat(start_date + 'T00:00:00+00:00')
                        if log_date < start:
                            continue
                    if end_date:
                        end = datetime.fromisoformat(end_date + 'T23:59:59+00:00')
                        if log_date > end:
                            continue

                logs.append(log)
            except:
                pass

    return logs


def print_summary(logs: List[Dict]):
    """전체 요약 출력"""
    if not logs:
        print("❌ 데이터 없음")
        return

    print(f"\n{'='*70}")
    print("📊 Agent Quality Summary (v2.0)")
    print(f"{'='*70}\n")

    # Agent별 분류
    agents = defaultdict(lambda: {"versions": defaultdict(list)})

    for log in logs:
        agent_name = log['agent']
        version = log.get('version', '1.0.0')
        agents[agent_name]["versions"][version].append(log)

    # Agent별 점수 계산
    print(f"{'Agent':<25} {'Version':<10} {'Score':<8} {'Conf':<6} {'Grade':<6} {'Status':<15}")
    print("-" * 70)

    for agent_name, data in sorted(agents.items()):
        for version, version_logs in sorted(data["versions"].items()):
            # AgentQuality 객체 생성 및 로그 로드
            quality = AgentQuality(agent_name, version)

            # 로그를 tasks 구조로 변환
            for log in version_logs:
                task = log['task']
                quality.tasks[task]["attempts"].append(log)

            # 점수 계산
            score = quality.get_score()

            if score['avg_success_rate'] is not None:
                uncertainty = 1 - score['confidence']
                score_display = f"{score['weighted_avg']:.0%}±{uncertainty:.0%}"

                print(
                    f"{agent_name:<25} "
                    f"{version:<10} "
                    f"{score_display:<8} "
                    f"{score['confidence']:.1f}    "
                    f"{score['grade']:<6} "
                    f"{score['status']:<15}"
                )

    print()

    # 전체 통계
    total_attempts = len(logs)
    total_success = sum(1 for log in logs if log['status'] == 'pass')
    overall_rate = total_success / total_attempts if total_attempts > 0 else 0

    print(f"\n전체 통계:")
    print(f"  총 시도: {total_attempts}")
    print(f"  성공: {total_success}")
    print(f"  실패: {total_attempts - total_success}")
    print(f"  전체 성공률: {overall_rate:.1%}")

    # 날짜 범위
    if logs:
        dates = [datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')) for log in logs]
        print(f"  기간: {min(dates).date()} ~ {max(dates).date()}")

    print()


def print_agent_detail(agent_name: str, version: Optional[str] = None):
    """특정 Agent 상세 분석"""
    logs = load_logs(agent=agent_name, version=version)

    if not logs:
        print(f"❌ Agent '{agent_name}' 데이터 없음")
        return

    # Version별 분류
    versions = defaultdict(list)
    for log in logs:
        v = log.get('version', '1.0.0')
        versions[v].append(log)

    # 각 버전 분석
    for v, v_logs in sorted(versions.items()):
        quality = AgentQuality(agent_name, v)

        # 로그 로드
        for log in v_logs:
            task = log['task']
            quality.tasks[task]["attempts"].append(log)

        # 리포트 출력
        quality.print_report()

    # 버전간 비교 (2개 이상인 경우)
    if len(versions) >= 2:
        print(f"\n{'='*60}")
        print("📈 Version Comparison")
        print(f"{'='*60}\n")

        print(f"{'Version':<10} {'Score':<10} {'Grade':<6} {'Trend':<12}")
        print("-" * 40)

        for v in sorted(versions.keys()):
            quality = AgentQuality(agent_name, v)
            for log in versions[v]:
                quality.tasks[log['task']]["attempts"].append(log)

            score = quality.get_score()
            if score['avg_success_rate'] is not None:
                print(
                    f"{v:<10} "
                    f"{score['weighted_avg']:.1%}    "
                    f"{score['grade']:<6} "
                    f"{score['trend']:<12}"
                )

        print()


def print_trend_analysis():
    """추세 분석"""
    logs = load_logs()

    if not logs:
        print("❌ 데이터 없음")
        return

    print(f"\n{'='*70}")
    print("📈 Trend Analysis")
    print(f"{'='*70}\n")

    # 날짜별 성공률
    daily_stats = defaultdict(lambda: {"success": 0, "total": 0})

    for log in logs:
        date = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00')).date()
        daily_stats[date]["total"] += 1
        if log['status'] == 'pass':
            daily_stats[date]["success"] += 1

    print("날짜별 성공률:")
    print(f"{'Date':<12} {'Success Rate':<15} {'Attempts':<10}")
    print("-" * 40)

    for date in sorted(daily_stats.keys()):
        stats = daily_stats[date]
        rate = stats['success'] / stats['total']
        bar = "█" * int(rate * 20)

        print(f"{date} {rate:.1%} {bar:<20} ({stats['total']})")

    print()

    # Agent별 추세
    agents = defaultdict(list)
    for log in logs:
        agents[log['agent']].append(log)

    print("\nAgent별 추세:")
    print(f"{'Agent':<25} {'Trend':<15} {'Recent Rate':<12}")
    print("-" * 55)

    for agent_name, agent_logs in sorted(agents.items()):
        # 최근 10개
        recent = sorted(agent_logs, key=lambda x: x['timestamp'])[-10:]
        recent_rate = sum(1 for log in recent if log['status'] == 'pass') / len(recent)

        # 전체
        total_rate = sum(1 for log in agent_logs if log['status'] == 'pass') / len(agent_logs)

        # 추세
        if recent_rate > total_rate + 0.15:
            trend = "↗️ Improving"
        elif recent_rate < total_rate - 0.15:
            trend = "↘️ Declining"
        else:
            trend = "→ Stable"

        print(f"{agent_name:<25} {trend:<15} {recent_rate:.1%}")

    print()


def print_alerts():
    """경고 출력 (낮은 성능)"""
    logs = load_logs()

    if not logs:
        print("❌ 데이터 없음")
        return

    print(f"\n{'='*70}")
    print("⚠️ Quality Alerts")
    print(f"{'='*70}\n")

    # Agent별 분류
    agents = defaultdict(list)
    for log in logs:
        agents[log['agent']].append(log)

    alerts = []

    for agent_name, agent_logs in agents.items():
        quality = AgentQuality(agent_name)

        for log in agent_logs:
            quality.tasks[log['task']]["attempts"].append(log)

        score = quality.get_score()

        if score['avg_success_rate'] is not None:
            # 경고 조건
            if score['weighted_avg'] < 0.6:
                alerts.append({
                    "agent": agent_name,
                    "score": score['weighted_avg'],
                    "grade": score['grade'],
                    "status": score['status'],
                    "confidence": score['confidence'],
                    "trend": score['trend']
                })

    if not alerts:
        print("✅ 경고 없음 - 모든 Agent 정상")
        return

    # 심각도 순 정렬
    alerts.sort(key=lambda x: x['score'])

    print(f"{'Agent':<25} {'Score':<10} {'Grade':<6} {'Status':<15} {'Trend':<12}")
    print("-" * 70)

    for alert in alerts:
        print(
            f"{alert['agent']:<25} "
            f"{alert['score']:.1%}    "
            f"{alert['grade']:<6} "
            f"{alert['status']:<15} "
            f"{alert['trend']:<12}"
        )

    print()


def print_task_analysis(task_name: str):
    """특정 Task 분석 (모든 Agent에서)"""
    logs = load_logs(task=task_name)

    if not logs:
        print(f"❌ Task '{task_name}' 데이터 없음")
        return

    print(f"\n{'='*70}")
    print(f"📋 Task Analysis: {task_name}")
    print(f"{'='*70}\n")

    # Agent별 분류
    agents = defaultdict(list)
    for log in logs:
        agents[log['agent']].append(log)

    print(f"{'Agent':<25} {'Attempts':<10} {'Success':<8} {'Rate':<10} {'Avg Duration':<12}")
    print("-" * 70)

    for agent_name, task_logs in sorted(agents.items()):
        attempts = len(task_logs)
        successes = sum(1 for log in task_logs if log['status'] == 'pass')
        rate = successes / attempts

        durations = [log['duration'] for log in task_logs if log.get('duration', 0) > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0

        print(
            f"{agent_name:<25} "
            f"{attempts:<10} "
            f"{successes:<8} "
            f"{rate:.1%}      "
            f"{avg_duration:.2f}s"
        )

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Agent Quality Analyzer v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python analyze_quality2.py --summary
  python analyze_quality2.py --agent debugger
  python analyze_quality2.py --agent debugger --version 1.2.0
  python analyze_quality2.py --trend
  python analyze_quality2.py --alerts
  python analyze_quality2.py --task "Fix TypeError"
"""
    )

    parser.add_argument('--summary', action='store_true', help='전체 요약')
    parser.add_argument('--agent', help='특정 Agent 분석')
    parser.add_argument('--version', help='특정 Agent Version')
    parser.add_argument('--task', help='특정 Task 분석')
    parser.add_argument('--trend', action='store_true', help='추세 분석')
    parser.add_argument('--alerts', action='store_true', help='경고 확인')

    parser.add_argument('--start', help='시작 날짜 (YYYY-MM-DD)')
    parser.add_argument('--end', help='종료 날짜 (YYYY-MM-DD)')

    parser.add_argument('--log-file', type=Path, default=LOG_FILE, help='로그 파일 경로')

    args = parser.parse_args()

    # 로그 파일 체크
    if not args.log_file.exists():
        print(f"❌ 로그 파일이 없습니다: {args.log_file}")
        print("\n아직 Agent를 사용한 기록이 없습니다.")
        print("사용법: python track.py --agent debugger --task 'Fix bug' --status pass")
        sys.exit(1)

    # 명령 실행
    if args.summary:
        logs = load_logs(args.log_file, start_date=args.start, end_date=args.end)
        print_summary(logs)
    elif args.agent:
        print_agent_detail(args.agent, args.version)
    elif args.task:
        print_task_analysis(args.task)
    elif args.trend:
        print_trend_analysis()
    elif args.alerts:
        print_alerts()
    else:
        # 기본: 요약
        logs = load_logs(args.log_file)
        print_summary(logs)


if __name__ == "__main__":
    main()
