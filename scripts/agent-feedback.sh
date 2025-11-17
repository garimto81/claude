#!/bin/bash
# Agent Performance Feedback Loop
# Wrapper for analyze_quality2.py with actionable recommendations

echo "======================================================================"
echo "Agent Performance Feedback Loop"
echo "======================================================================"

# Check if analyze_quality2.py exists
if [ ! -f ".claude/evolution/scripts/analyze_quality2.py" ]; then
  echo "Error: analyze_quality2.py not found"
  exit 1
fi

# Run summary analysis
echo ""
echo "Summary of All Agents:"
python .claude/evolution/scripts/analyze_quality2.py --summary

# Check for underperforming agents (<60% success rate)
echo ""
echo "======================================================================"
echo "Actionable Recommendations:"
echo "======================================================================"

# Parse agent quality data
if [ -f ".agent-quality-v2.jsonl" ]; then
  # Count agents with low success rates
  python - <<'EOF'
import json
from collections import defaultdict

agents = defaultdict(lambda: {"pass": 0, "fail": 0})

with open(".agent-quality-v2.jsonl") as f:
    for line in f:
        log = json.loads(line)
        agent = log["agent"]
        status = log["status"]
        agents[agent][status] += 1

print("\nAgent Success Rates:")
print(f"{'Agent':<30} {'Success Rate':<15} {'Recommendation'}")
print("-" * 70)

for agent, stats in sorted(agents.items(), key=lambda x: x[1]["pass"] / max(1, x[1]["pass"] + x[1]["fail"])):
    total = stats["pass"] + stats["fail"]
    success_rate = (stats["pass"] / total * 100) if total > 0 else 0

    recommendation = ""
    if success_rate < 40:
        recommendation = "CRITICAL: Review usage patterns"
    elif success_rate < 60:
        recommendation = "WARNING: Needs improvement"
    elif success_rate < 80:
        recommendation = "OK: Minor optimization needed"
    else:
        recommendation = "GOOD: Performing well"

    print(f"{agent:<30} {success_rate:>6.1f}%        {recommendation}")

print("\nKey Insights:")
print("- Agents <40%: Stop using until pattern fixed")
print("- Agents 40-60%: Review task descriptions (add context)")
print("- Agents 60-80%: Minor tweaks (e.g., timeout, mock data)")
print("- Agents >80%: Keep current usage patterns")
EOF
else
  echo "No agent quality data found (.agent-quality-v2.jsonl)"
  echo "Start tracking with: python .claude/track.py <agent> <task> <status>"
fi

echo ""
echo "======================================================================"
echo "To track new agent usage:"
echo "  python .claude/track.py <agent> '<task description>' <pass|fail> --duration <secs>"
echo "======================================================================"
