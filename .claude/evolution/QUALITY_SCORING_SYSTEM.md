# Agent Quality Scoring System (게임화된 점수 시스템)

**버전**: 2.0.0
**업데이트**: 2025-01-14

---

## 🎮 점수 시스템 규칙

### 기본 규칙

```
시작 점수: 5.0/5.0 (만점)

✅ 설계 통과 → 만점 유지 (5.0)
❌ 버그 발생 → -1.0점 손실 (4.0)
🔧 버그 수정 → +0.5점 복구 (4.5)
❌ 수정 후 또 실패 → -1.0점 손실 (3.5)
...
💀 5번 실패 → 품질 0.0 (최악)
```

### 점수 계산

```python
초기_점수 = 5.0
실패_페널티 = -1.0
수정_보너스 = +0.5

현재_점수 = max(0, 초기_점수 + (실패_횟수 * 실패_페널티) + (수정_횟수 * 수정_보너스))

# 예시:
# 실패 2회, 수정 1회: 5.0 - 2.0 + 0.5 = 3.5
# 실패 5회, 수정 0회: 5.0 - 5.0 = 0.0
```

---

## 📊 로그 구조 설계

### 1. Agent Quality Log (`.agent-quality.jsonl`)

**위치**: 각 서브 레포 루트 `.agent-quality.jsonl`

**형식**: JSON Lines (한 줄에 하나의 JSON)

```jsonl
{"timestamp":"2025-01-14T10:30:00Z","agent":"context7-engineer","phase":"Phase 0","task":"Verify React docs","attempt":1,"status":"pass","score":5.0,"duration":1.23}
{"timestamp":"2025-01-14T11:00:00Z","agent":"playwright-engineer","phase":"Phase 2","task":"E2E login test","attempt":1,"status":"fail","error":"Selector timeout","score":4.0,"duration":5.67}
{"timestamp":"2025-01-14T11:30:00Z","agent":"playwright-engineer","phase":"Phase 2","task":"E2E login test","attempt":2,"status":"pass","score":4.5,"duration":3.21,"fixed":true}
```

**필수 필드**:
```typescript
interface AgentQualityLog {
  timestamp: string;        // ISO 8601
  agent: string;            // Agent 이름
  phase: string;            // Phase 0-6
  task: string;             // Task 설명
  attempt: number;          // 시도 횟수 (1, 2, 3...)
  status: "pass" | "fail";  // 통과/실패
  score: number;            // 현재 점수 (0-5)
  duration: number;         // 실행 시간 (초)
  error?: string;           // 에러 메시지 (fail 시)
  fixed?: boolean;          // 수정 후 재시도 여부
  previous_score?: number;  // 이전 점수
}
```

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│  서브 레포 (sso-nextjs, ojt-platform 등)                  │
│                                                           │
│  .agent-quality.jsonl  ← 로그 기록                        │
│  .claude/track.sh      ← 경량 스크립트                     │
└─────────────────────────────────────────────────────────┘
                    ↓ (주기적 동기화)
┌─────────────────────────────────────────────────────────┐
│  전역 레포 (claude01)                                     │
│                                                           │
│  .claude/evolution/data/                                 │
│    ├── sso-nextjs.jsonl       ← 수집된 로그               │
│    ├── ojt-platform.jsonl                                │
│    └── quality-summary.json   ← 종합 점수                 │
│                                                           │
│  .claude/evolution/scripts/                              │
│    ├── analyze_quality.py     ← 분석 스크립트             │
│    └── sync_quality_logs.py   ← 동기화 스크립트           │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│  Langfuse Dashboard                                      │
│                                                           │
│  Agent 별 품질 점수 차트                                   │
│  실패 패턴 분석                                            │
│  개선 추이 모니터링                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 서브 레포에서 로그 남기기

### 방법 1: 경량 Bash 스크립트 (추천)

**파일**: `.claude/track.sh`

```bash
#!/bin/bash
# Agent Quality Logger (서브 레포용)
# Usage: .claude/track.sh <agent> <phase> <task> <status> [error]

AGENT="$1"
PHASE="$2"
TASK="$3"
STATUS="$4"  # "pass" or "fail"
ERROR="${5:-}"

LOG_FILE=".agent-quality.jsonl"

# 이전 점수 가져오기
PREVIOUS_SCORE=$(tail -1 "$LOG_FILE" 2>/dev/null | jq -r '.score // 5.0')

# 시도 횟수 계산
ATTEMPT=$(grep "\"agent\":\"$AGENT\"" "$LOG_FILE" 2>/dev/null | grep "\"task\":\"$TASK\"" | wc -l)
ATTEMPT=$((ATTEMPT + 1))

# 점수 계산
if [ "$STATUS" = "pass" ]; then
    if [ $ATTEMPT -eq 1 ]; then
        SCORE=5.0
    else
        # 수정 후 통과: +0.5
        SCORE=$(echo "$PREVIOUS_SCORE + 0.5" | bc)
        FIXED="true"
    fi
elif [ "$STATUS" = "fail" ]; then
    # 실패: -1.0
    SCORE=$(echo "$PREVIOUS_SCORE - 1.0" | bc)
    FIXED="false"
fi

# 최소 0, 최대 5
SCORE=$(echo "$SCORE" | awk '{if ($1 < 0) print 0; else if ($1 > 5) print 5; else print $1}')

# JSON 생성
cat >> "$LOG_FILE" <<EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","agent":"$AGENT","phase":"$PHASE","task":"$TASK","attempt":$ATTEMPT,"status":"$STATUS","score":$SCORE,"duration":0,"error":"$ERROR","fixed":$FIXED,"previous_score":$PREVIOUS_SCORE}
EOF

echo "✅ Logged: $AGENT - $TASK ($STATUS) - Score: $SCORE/5.0"
```

**사용법**:
```bash
# 서브 레포에서 실행
.claude/track.sh "context7-engineer" "Phase 0" "Verify React docs" "pass"

# 실패 시
.claude/track.sh "playwright-engineer" "Phase 2" "E2E test" "fail" "Selector timeout"

# 수정 후 통과
.claude/track.sh "playwright-engineer" "Phase 2" "E2E test" "pass"
```

---

### 방법 2: Python 스크립트 (더 정교)

**파일**: `.claude/track.py`

```python
#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(".agent-quality.jsonl")

def get_previous_score(agent, task):
    """이전 점수 가져오기"""
    if not LOG_FILE.exists():
        return 5.0

    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()

    for line in reversed(lines):
        log = json.loads(line)
        if log['agent'] == agent and log['task'] == task:
            return log['score']

    return 5.0

def get_attempt_count(agent, task):
    """시도 횟수 계산"""
    if not LOG_FILE.exists():
        return 1

    count = 0
    with open(LOG_FILE, 'r') as f:
        for line in f:
            log = json.loads(line)
            if log['agent'] == agent and log['task'] == task:
                count += 1

    return count + 1

def calculate_score(previous_score, attempt, status):
    """점수 계산"""
    if status == "pass":
        if attempt == 1:
            return 5.0
        else:
            # 수정 후 통과: +0.5
            return min(5.0, previous_score + 0.5)
    else:
        # 실패: -1.0
        return max(0.0, previous_score - 1.0)

def log_quality(agent, phase, task, status, error=None, duration=0):
    """품질 로그 기록"""
    previous_score = get_previous_score(agent, task)
    attempt = get_attempt_count(agent, task)
    score = calculate_score(previous_score, attempt, status)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent,
        "phase": phase,
        "task": task,
        "attempt": attempt,
        "status": status,
        "score": round(score, 1),
        "duration": duration,
        "previous_score": previous_score,
        "fixed": attempt > 1 and status == "pass"
    }

    if error:
        log_entry["error"] = error

    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    print(f"✅ Logged: {agent} - {task} ({status}) - Score: {score:.1f}/5.0")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: .claude/track.py <agent> <phase> <task> <status> [error] [duration]")
        sys.exit(1)

    agent = sys.argv[1]
    phase = sys.argv[2]
    task = sys.argv[3]
    status = sys.argv[4]
    error = sys.argv[5] if len(sys.argv) > 5 else None
    duration = float(sys.argv[6]) if len(sys.argv) > 6 else 0

    log_quality(agent, phase, task, status, error, duration)
```

**사용법**:
```bash
python .claude/track.py "context7-engineer" "Phase 0" "Verify docs" "pass"
python .claude/track.py "debugger" "Phase 1" "Fix TypeError" "fail" "Type mismatch" 2.5
python .claude/track.py "debugger" "Phase 1" "Fix TypeError" "pass" "" 1.8
```

---

### 방법 3: Claude Code 통합 (자동)

**CLAUDE.md에 추가**:

```markdown
## Agent Quality Tracking

모든 agent/skill 사용 시 자동으로 품질 로그 기록:

```bash
# Phase 1: Code 작업 후
.claude/track.sh "typescript-expert" "Phase 1" "Type definitions" "pass"

# 테스트 실패 시
.claude/track.sh "test-automator" "Phase 2" "Unit tests" "fail" "Assertion failed"

# 수정 후
.claude/track.sh "test-automator" "Phase 2" "Unit tests" "pass"
```

**자동화** (Git hook):
```bash
# .git/hooks/post-commit
#!/bin/bash
# 마지막 agent 사용 추적
# TODO: 자동 감지 로직
```
```

---

## 🔄 전역 레포에서 로그 수집

### 동기화 스크립트

**파일**: `.claude/evolution/scripts/sync_quality_logs.py`

```python
#!/usr/bin/env python3
"""
서브 레포들의 품질 로그를 전역 레포로 동기화

Usage:
    python sync_quality_logs.py --repos sso-nextjs ojt-platform
    python sync_quality_logs.py --all
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List

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
            return

        # 전역 레포로 복사
        dest_file = self.data_dir / f"{repo_name}.jsonl"

        # 기존 로그가 있으면 append
        if dest_file.exists():
            # 중복 제거 (timestamp 기준)
            existing_timestamps = set()
            with open(dest_file, 'r') as f:
                for line in f:
                    log = json.loads(line)
                    existing_timestamps.add(log['timestamp'])

            # 새 로그만 추가
            new_count = 0
            with open(log_file, 'r') as src:
                with open(dest_file, 'a') as dst:
                    for line in src:
                        log = json.loads(line)
                        if log['timestamp'] not in existing_timestamps:
                            dst.write(line)
                            new_count += 1

            print(f"✅ {repo_name}: Synced {new_count} new logs")
        else:
            # 전체 복사
            shutil.copy(log_file, dest_file)

            with open(log_file, 'r') as f:
                total = sum(1 for _ in f)

            print(f"✅ {repo_name}: Synced {total} logs (initial)")

    def sync_all(self, repo_configs: List[dict]):
        """모든 레포 동기화"""
        print(f"🔄 Syncing quality logs from {len(repo_configs)} repos...\n")

        for config in repo_configs:
            repo_name = config['name']
            repo_path = Path(config['path'])

            if not repo_path.exists():
                print(f"⚠️  {repo_name}: Path not found - {repo_path}")
                continue

            self.sync_repo(repo_name, repo_path)

        print(f"\n✅ Sync completed!")

    def generate_summary(self):
        """종합 점수 생성"""
        summary = {}

        for log_file in self.data_dir.glob("*.jsonl"):
            if log_file.name == "quality-summary.json":
                continue

            repo_name = log_file.stem
            agent_scores = {}

            with open(log_file, 'r') as f:
                for line in f:
                    log = json.loads(line)
                    agent = log['agent']

                    if agent not in agent_scores:
                        agent_scores[agent] = {
                            'current_score': log['score'],
                            'total_attempts': 0,
                            'passes': 0,
                            'fails': 0,
                            'avg_score': 0,
                            'last_updated': log['timestamp']
                        }

                    agent_scores[agent]['current_score'] = log['score']
                    agent_scores[agent]['total_attempts'] += 1
                    agent_scores[agent]['last_updated'] = log['timestamp']

                    if log['status'] == 'pass':
                        agent_scores[agent]['passes'] += 1
                    else:
                        agent_scores[agent]['fails'] += 1

            # 평균 점수 계산
            for agent in agent_scores:
                total = agent_scores[agent]['total_attempts']
                passes = agent_scores[agent]['passes']
                agent_scores[agent]['avg_score'] = round(
                    (passes / total) * 5.0, 1
                ) if total > 0 else 0

            summary[repo_name] = agent_scores

        # 저장
        summary_file = self.data_dir / "quality-summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n📊 Summary saved: {summary_file}")
        return summary

def main():
    import argparse

    parser = argparse.ArgumentParser(description="서브 레포 품질 로그 동기화")
    parser.add_argument('--repos', nargs='+', help='레포 이름들')
    parser.add_argument('--all', action='store_true', help='모든 레포 동기화')
    parser.add_argument('--config', default='repo-config.json', help='레포 설정 파일')

    args = parser.parse_args()

    # 전역 레포 경로 (현재 스크립트 위치 기준)
    global_repo = Path(__file__).parent.parent.parent.parent

    syncer = QualityLogSyncer(global_repo)

    # 레포 설정 로드
    config_file = global_repo / ".claude/evolution/config" / args.config
    if config_file.exists():
        with open(config_file, 'r') as f:
            repo_configs = json.load(f)['repos']
    else:
        # 기본 설정
        repo_configs = [
            {"name": "sso-nextjs", "path": "../sso-nextjs"},
            {"name": "ojt-platform", "path": "../ojt-platform"}
        ]

    # 동기화
    if args.all:
        syncer.sync_all(repo_configs)
    elif args.repos:
        filtered = [c for c in repo_configs if c['name'] in args.repos]
        syncer.sync_all(filtered)
    else:
        print("Usage: --repos <names> or --all")
        return

    # 종합 점수 생성
    summary = syncer.generate_summary()

    # 출력
    print("\n" + "="*60)
    print("📊 Quality Summary")
    print("="*60)

    for repo, agents in summary.items():
        print(f"\n🔹 {repo}")
        for agent, scores in agents.items():
            status = "✅" if scores['current_score'] >= 4.0 else "⚠️" if scores['current_score'] >= 3.0 else "❌"
            print(f"  {status} {agent}: {scores['current_score']:.1f}/5.0 (avg: {scores['avg_score']:.1f}, {scores['passes']}✓ {scores['fails']}✗)")

if __name__ == "__main__":
    main()
```

**사용법**:
```bash
# 모든 레포 동기화
python .claude/evolution/scripts/sync_quality_logs.py --all

# 특정 레포만
python .claude/evolution/scripts/sync_quality_logs.py --repos sso-nextjs ojt-platform
```

---

## 📈 전역 지침에서 분석

### CLAUDE.md에 추가

```markdown
## Agent Quality Monitoring

### 품질 점수 확인

```bash
# 전체 품질 점수 확인
python .claude/evolution/scripts/analyze_quality.py --summary

# 특정 Agent 상세 분석
python .claude/evolution/scripts/analyze_quality.py --agent context7-engineer

# 개선 추세 확인
python .claude/evolution/scripts/analyze_quality.py --trend --days 30
```

### 자동 알림

품질 점수가 3.0 이하로 떨어지면:
1. ⚠️ 경고 메시지 출력
2. 📊 상세 분석 리포트 생성
3. 💡 개선 제안 생성 (PromptAgent)
4. 🔧 Instruction 자동 최적화 (Phase 2)
```

---

## 🎯 실전 시나리오

### 시나리오 1: 신규 Agent 테스트

```bash
# sso-nextjs 프로젝트에서

# 1회차: 설계 통과
.claude/track.sh "auth-specialist" "Phase 1" "Implement OAuth" "pass"
# → Score: 5.0/5.0 ✅

# Phase 2: 테스트 실패
.claude/track.sh "test-automator" "Phase 2" "Auth unit tests" "fail" "Token validation failed"
# → Score: 4.0/5.0 ⚠️

# 버그 수정 후
.claude/track.sh "test-automator" "Phase 2" "Auth unit tests" "pass"
# → Score: 4.5/5.0 ✔️
```

### 시나리오 2: 반복 실패

```bash
# 1회: 실패
.claude/track.sh "playwright-engineer" "Phase 5" "E2E flow" "fail" "Selector timeout"
# → Score: 4.0/5.0

# 2회: 수정 후 실패
.claude/track.sh "playwright-engineer" "Phase 5" "E2E flow" "fail" "Network error"
# → Score: 3.0/5.0 ⚠️

# 3회: 수정 후 실패
.claude/track.sh "playwright-engineer" "Phase 5" "E2E flow" "fail" "Assertion failed"
# → Score: 2.0/5.0 ❌

# 4회: 드디어 통과
.claude/track.sh "playwright-engineer" "Phase 5" "E2E flow" "pass"
# → Score: 2.5/5.0

# → 전역 레포에서 알림: "playwright-engineer 품질 저하 감지"
```

### 시나리오 3: 전역 분석

```bash
# 전역 레포 (claude01)에서

# 서브 레포들 동기화
python .claude/evolution/scripts/sync_quality_logs.py --all

# 출력:
# ✅ sso-nextjs: Synced 15 logs
# ✅ ojt-platform: Synced 8 logs
#
# 📊 Quality Summary
# 🔹 sso-nextjs
#   ✅ auth-specialist: 5.0/5.0 (avg: 5.0, 3✓ 0✗)
#   ⚠️ test-automator: 4.5/5.0 (avg: 4.5, 2✓ 1✗)
# 🔹 ojt-platform
#   ❌ playwright-engineer: 2.5/5.0 (avg: 2.5, 1✓ 3✗)

# 상세 분석
python .claude/evolution/scripts/analyze_quality.py --agent playwright-engineer

# 출력:
# ❌ playwright-engineer Quality Report
# Current Score: 2.5/5.0 (Grade: D)
# Total Attempts: 4
# Failures: 3
# Common Errors:
#   - Selector timeout (2회)
#   - Network error (1회)
#
# Recommendations:
# 1. Review selector strategy
# 2. Add network retry logic
# 3. Consider increasing timeouts
```

---

## 🔗 다음 단계

이 시스템 PR #17에 추가하시겠습니까?

```bash
git add .claude/evolution/QUALITY_SCORING_SYSTEM.md
git add .claude/evolution/scripts/sync_quality_logs.py
git commit -m "feat: Add quality scoring system (5-point scale)"
```
