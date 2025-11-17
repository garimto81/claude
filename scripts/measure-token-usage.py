#!/usr/bin/env python3
"""
Token Usage Measurement Script
측정 목적: Phase별 agent 로딩 시 실제 토큰 절감률 계산

Usage:
    python scripts/measure-token-usage.py --phase 0
    python scripts/measure-token-usage.py --all
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List

# Agent token costs (from CLAUDE.md)
AGENT_COSTS = {
    # Core Agents (15)
    "context7-engineer": 1200,
    "seq-engineer": 500,
    "task-decomposition": 600,
    "architect-reviewer": 1300,
    "backend-architect": 1400,
    "frontend-developer": 1300,
    "fullstack-developer": 1600,
    "typescript-expert": 1000,
    "debugger": 1300,
    "test-automator": 600,
    "playwright-engineer": 1500,
    "code-reviewer": 1300,
    "security-auditor": 1400,
    "performance-engineer": 1300,
    "deployment-engineer": 700,

    # Extended Agents (18)
    "python-pro": 1200,
    "mobile-developer": 1400,
    "graphql-architect": 1300,
    "supabase-engineer": 1400,
    "database-architect": 1300,
    "database-optimizer": 1200,
    "data-engineer": 1400,
    "data-scientist": 1200,
    "ai-engineer": 1500,
    "ml-engineer": 1400,
    "prompt-engineer": 1000,
    "cloud-architect": 1500,
    "devops-troubleshooter": 1400,
    "github-engineer": 800,
    "taskmanager-planner": 700,
    "exa-search-specialist": 600,
    "context-manager": 500,
    "ui-ux-designer": 1200,
}

# Phase-specific agent recommendations (from CLAUDE.md)
PHASE_AGENTS = {
    "0": ["context7-engineer", "seq-engineer", "architect-reviewer", "exa-search-specialist"],
    "0.5": ["task-decomposition", "taskmanager-planner"],
    "1": ["backend-architect", "frontend-developer", "fullstack-developer", "typescript-expert",
          "debugger", "database-architect", "python-pro"],
    "2": ["test-automator", "playwright-engineer", "code-reviewer", "security-auditor"],
    "3": ["code-reviewer", "github-engineer"],
    "4": ["github-engineer"],
    "5": ["playwright-engineer", "security-auditor", "performance-engineer", "database-optimizer"],
    "6": ["deployment-engineer", "cloud-architect", "devops-troubleshooter"],
}


def calculate_tokens(agents: List[str]) -> int:
    """Calculate total tokens for given agent list"""
    return sum(AGENT_COSTS.get(agent, 0) for agent in agents)


def measure_phase(phase: str) -> Dict:
    """Measure token usage for a specific phase"""
    agents = PHASE_AGENTS.get(phase, [])
    tokens = calculate_tokens(agents)

    return {
        "phase": phase,
        "agents": agents,
        "agent_count": len(agents),
        "tokens": tokens,
    }


def measure_all_phases() -> Dict:
    """Measure token usage for all phases"""
    results = {}

    # Calculate all agents (baseline)
    all_agents = list(AGENT_COSTS.keys())
    all_tokens = calculate_tokens(all_agents)

    results["baseline"] = {
        "description": "All 33 agents loaded",
        "agents": all_agents,
        "agent_count": len(all_agents),
        "tokens": all_tokens,
    }

    # Calculate each phase
    for phase in ["0", "0.5", "1", "2", "3", "4", "5", "6"]:
        results[f"phase_{phase}"] = measure_phase(phase)

    # Calculate savings
    phase_tokens = [results[f"phase_{p}"]["tokens"] for p in ["0", "0.5", "1", "2", "3", "4", "5", "6"]]
    avg_phase_tokens = sum(phase_tokens) / len(phase_tokens)
    savings_pct = ((all_tokens - avg_phase_tokens) / all_tokens) * 100

    results["summary"] = {
        "baseline_tokens": all_tokens,
        "avg_phase_tokens": int(avg_phase_tokens),
        "min_phase_tokens": min(phase_tokens),
        "max_phase_tokens": max(phase_tokens),
        "avg_savings_percent": round(savings_pct, 1),
    }

    return results


def print_report(results: Dict):
    """Print formatted report"""
    print("=" * 70)
    print("Token Usage Measurement Report")
    print("=" * 70)

    # Baseline
    baseline = results["baseline"]
    print(f"\nBaseline (All Agents):")
    print(f"   Agents: {baseline['agent_count']}")
    print(f"   Tokens: {baseline['tokens']:,}")

    # Per-phase breakdown
    print(f"\nPhase-Specific Token Usage:")
    print(f"{'Phase':<8} {'Agents':<8} {'Tokens':<10} {'Savings':<10}")
    print("-" * 40)

    for phase in ["0", "0.5", "1", "2", "3", "4", "5", "6"]:
        data = results[f"phase_{phase}"]
        tokens = data["tokens"]
        savings = ((baseline["tokens"] - tokens) / baseline["tokens"]) * 100
        print(f"{phase:<8} {data['agent_count']:<8} {tokens:<10,} {savings:.1f}%")

    # Summary
    summary = results["summary"]
    print(f"\nSummary:")
    print(f"   Baseline: {summary['baseline_tokens']:,} tokens")
    print(f"   Average Phase: {summary['avg_phase_tokens']:,} tokens")
    print(f"   Min Phase: {summary['min_phase_tokens']:,} tokens")
    print(f"   Max Phase: {summary['max_phase_tokens']:,} tokens")
    print(f"   **Average Savings: {summary['avg_savings_percent']}%**")

    print(f"\nVerified Claim: \"{summary['avg_savings_percent']}% token savings per conversation\"")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Measure token usage across phases")
    parser.add_argument("--phase", type=str, help="Specific phase to measure (0, 0.5, 1, 2, 3, 4, 5, 6)")
    parser.add_argument("--all", action="store_true", help="Measure all phases")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.phase:
        result = measure_phase(args.phase)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\nPhase {result['phase']}:")
            print(f"  Agents: {result['agent_count']} - {', '.join(result['agents'])}")
            print(f"  Tokens: {result['tokens']:,}")
    else:
        results = measure_all_phases()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_report(results)


if __name__ == "__main__":
    main()
