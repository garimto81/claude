#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
서브 레포들의 품질 로그를 전역 레포로 동기화

Usage:
    python sync_quality_logs.py --repos sso-nextjs ojt-platform
    python sync_quality_logs.py --all
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict

class QualityLogSyncer:
    """품질 로그 동기화기"""

    def __init__(self, global_repo_path: Path):
        self.global_repo = global_repo_path
        self.data_dir = global_repo_path / ".claude/evolution/data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def sync_repo(self, repo_name: str, repo_path: Path):
        """단일 레포 동기화"""
        log_file = repo_path / ".agent-quality.jsonl"

        if not log_file.exists():
            print(f"⚠️  {repo_name}: No quality log found")
            return 0

        # 전역 레포로 복사
        dest_file = self.data_dir / f"{repo_name}.jsonl"

        # 기존 로그가 있으면 append
        if dest_file.exists():
            # 중복 제거 (timestamp 기준)
            existing_timestamps = set()
            with open(dest_file, 'r') as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        existing_timestamps.add(log['timestamp'])
                    except Exception:
                        pass

            # 새 로그만 추가
            new_count = 0
            with open(log_file, 'r') as src:
                with open(dest_file, 'a') as dst:
                    for line in src:
                        try:
                            log = json.loads(line.strip())
                            if log['timestamp'] not in existing_timestamps:
                                dst.write(line)
                                new_count += 1
                        except Exception:
                            pass

            print(f"✅ {repo_name}: Synced {new_count} new logs")
            return new_count
        else:
            # 전체 복사
            shutil.copy(log_file, dest_file)

            with open(log_file, 'r') as f:
                total = sum(1 for _ in f)

            print(f"✅ {repo_name}: Synced {total} logs (initial)")
            return total

    def sync_all(self, repo_configs: List[dict]) -> Dict:
        """모든 레포 동기화"""
        print(f"🔄 Syncing quality logs from {len(repo_configs)} repos...\n")

        results = {}
        for config in repo_configs:
            repo_name = config['name']
            repo_path = Path(config['path']).expanduser().resolve()

            if not repo_path.exists():
                print(f"⚠️  {repo_name}: Path not found - {repo_path}")
                continue

            count = self.sync_repo(repo_name, repo_path)
            results[repo_name] = count

        print("\n✅ Sync completed!")
        return results

    def generate_summary(self) -> Dict:
        """종합 점수 생성"""
        summary = {}

        for log_file in self.data_dir.glob("*.jsonl"):
            if log_file.name.startswith("quality-summary"):
                continue

            repo_name = log_file.stem
            agent_scores = {}

            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        agent = log['agent']

                        if agent not in agent_scores:
                            agent_scores[agent] = {
                                'current_score': log['score'],
                                'total_attempts': 0,
                                'passes': 0,
                                'fails': 0,
                                'avg_score': 0,
                                'last_updated': log['timestamp'],
                                'tasks': set()
                            }

                        agent_scores[agent]['current_score'] = log['score']
                        agent_scores[agent]['total_attempts'] += 1
                        agent_scores[agent]['last_updated'] = log['timestamp']
                        agent_scores[agent]['tasks'].add(log['task'])

                        if log['status'] == 'pass':
                            agent_scores[agent]['passes'] += 1
                        else:
                            agent_scores[agent]['fails'] += 1
                    except Exception:
                        pass

            # 평균 점수 계산 & set → list 변환
            for agent in agent_scores:
                total = agent_scores[agent]['total_attempts']
                passes = agent_scores[agent]['passes']
                agent_scores[agent]['avg_score'] = round(
                    (passes / total) * 5.0, 1
                ) if total > 0 else 0
                agent_scores[agent]['tasks'] = list(agent_scores[agent]['tasks'])

            summary[repo_name] = agent_scores

        # 저장
        summary_file = self.data_dir / "quality-summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n📊 Summary saved: {summary_file}")
        return summary

    def print_summary(self, summary: Dict):
        """요약 출력"""
        print("\n" + "="*60)
        print("📊 Quality Summary")
        print("="*60)

        for repo, agents in summary.items():
            print(f"\n🔹 {repo}")

            if not agents:
                print("  (No data)")
                continue

            # 점수별 정렬
            sorted_agents = sorted(
                agents.items(),
                key=lambda x: x[1]['current_score'],
                reverse=True
            )

            for agent, scores in sorted_agents:
                # 상태 아이콘
                if scores['current_score'] >= 4.0:
                    status = "✅"
                elif scores['current_score'] >= 3.0:
                    status = "⚠️"
                else:
                    status = "❌"

                print(
                    f"  {status} {agent}: "
                    f"{scores['current_score']:.1f}/5.0 "
                    f"(avg: {scores['avg_score']:.1f}, "
                    f"{scores['passes']}✓ {scores['fails']}✗)"
                )

        print("="*60 + "\n")


def load_repo_config(global_repo: Path) -> List[Dict]:
    """레포 설정 로드"""
    config_file = global_repo / ".claude/evolution/config/repo-config.json"

    if config_file.exists():
        with open(config_file, 'r') as f:
            data = json.load(f)
            return data.get('repos', [])

    # 기본 설정
    return [
        {
            "name": "sso-nextjs",
            "path": "~/AI/sso-nextjs",
            "description": "SSO system with NextAuth + Supabase"
        },
        {
            "name": "ojt-platform",
            "path": "~/AI/ojt-platform",
            "description": "OJT platform"
        }
    ]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="서브 레포 품질 로그 동기화",
        epilog="Example: python sync_quality_logs.py --all"
    )

    parser.add_argument(
        '--repos',
        nargs='+',
        help='특정 레포들만 동기화 (예: sso-nextjs ojt-platform)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='모든 레포 동기화'
    )

    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='동기화 없이 요약만 생성'
    )

    args = parser.parse_args()

    # 전역 레포 경로 (현재 스크립트 위치 기준)
    global_repo = Path(__file__).parent.parent.parent.parent.resolve()

    syncer = QualityLogSyncer(global_repo)

    if args.summary_only:
        # 요약만 생성
        summary = syncer.generate_summary()
        syncer.print_summary(summary)
        return

    # 레포 설정 로드
    repo_configs = load_repo_config(global_repo)

    # 필터링
    if args.repos:
        repo_configs = [c for c in repo_configs if c['name'] in args.repos]

    if not args.all and not args.repos:
        print("Usage: --repos <names> or --all")
        print("\nAvailable repos:")
        for config in load_repo_config(global_repo):
            print(f"  - {config['name']}: {config.get('description', '')}")
        return

    # 동기화
    _ = syncer.sync_all(repo_configs)

    # 종합 점수 생성 및 출력
    summary = syncer.generate_summary()
    syncer.print_summary(summary)


if __name__ == "__main__":
    main()
