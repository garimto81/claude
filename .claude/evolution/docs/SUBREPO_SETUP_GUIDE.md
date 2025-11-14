# Sub-Repo Setup Guide (Python Import 방식)

## 🎯 개요

서브 레포에서 Agent Quality Tracking v2.0을 사용하는 방법입니다.

**핵심 아이디어**: 파일 복사 대신 Python import로 전역 레포의 모듈 직접 사용
→ 템플릿 업데이트 자동 반영, 관리 간소화

---

## ⚡ 빠른 시작 (5초 설정)

### 1. 자동 설정 실행

```bash
# 전역 레포 (claude01)에서
cd /path/to/claude01

# 서브 레포에 자동 설정
python scripts/setup_subrepo_tracking.py /path/to/my-sub-repo

# 여러 서브 레포에 한 번에
python scripts/setup_subrepo_tracking.py ../repo1 ../repo2 ../repo3
```

### 2. 즉시 사용 가능

```bash
# 서브 레포에서
cd /path/to/my-sub-repo

# Agent 사용 기록
python .claude/track.py debugger "Fix bug" pass --duration 1.5
```

끝! 🎉

---

## 📦 설정 스크립트가 하는 일

```
python scripts/setup_subrepo_tracking.py /path/to/sub-repo
```

실행 시 자동으로:

1. ✅ `.claude/` 디렉토리 생성
2. ✅ `track.py` 복사 (wrapper 스크립트)
3. ✅ `.env` 파일 생성 (CLAUDE_GLOBAL_REPO 경로 설정)
4. ✅ `.gitignore` 업데이트 (로그 파일 제외)
5. ✅ `.claude/README.md` 생성 (사용 가이드)
6. ✅ 테스트 실행 (정상 작동 확인)

출력 예시:
```
============================================================
🔧 Setting up: /path/to/my-sub-repo
============================================================
✅ Created: /path/to/my-sub-repo/.claude
✅ Copied: track.py (wrapper)
✅ Created: .env
✅ Updated: .gitignore
✅ Created: .claude/README.md (usage guide)

🧪 Testing...
✅ Test passed: track.py is working

============================================================
✅ Setup complete for: my-sub-repo
============================================================

📝 Quick Start:
cd /path/to/my-sub-repo
python .claude/track.py debugger 'Fix bug' pass --duration 1.5
```

---

## 📖 상세 사용법

### 1. Agent 사용 기록

```bash
# 기본 사용
python .claude/track.py <agent> <task> <status>

# 성공 예시
python .claude/track.py debugger "Fix TypeError in auth.ts" pass --duration 1.5

# 실패 예시
python .claude/track.py test-automator "Write unit tests" fail \
  --error "Timeout after 30s" \
  --duration 31.0

# Phase 정보 포함
python .claude/track.py context7-engineer "Verify React docs" pass \
  --phase "Phase 0" \
  --duration 2.3

# 자동 감지 플래그
python .claude/track.py playwright-engineer "E2E tests" pass \
  --auto-detected \
  --duration 45.2
```

출력:
```
✅ Logged: debugger - Fix TypeError in auth.ts (PASS)
   Duration: 1.50s
   Task Score: 75% (confidence: 80%)
```

### 2. Python 코드에서 직접 사용

```python
import sys
import os
from pathlib import Path

# .env에서 전역 레포 경로 읽기
from dotenv import load_dotenv
load_dotenv()

global_repo = Path(os.getenv('CLAUDE_GLOBAL_REPO'))
sys.path.insert(0, str(global_repo / '.claude' / 'evolution'))

# Import
from scripts.agent_quality_v2 import AgentQuality

# 사용
quality = AgentQuality("debugger", version="1.0.0")

# 기록
quality.record(
    task="Fix TypeError",
    status="pass",
    duration=1.5,
    phase="Phase 1"
)

# 점수 확인
score = quality.get_score()
print(f"Score: {score['weighted_avg']:.0%} (Grade: {score['grade']})")
```

### 3. Context Manager 패턴

```python
import sys
import os
from pathlib import Path
from contextlib import contextmanager
import time

# Setup
from dotenv import load_dotenv
load_dotenv()

global_repo = Path(os.getenv('CLAUDE_GLOBAL_REPO'))
sys.path.insert(0, str(global_repo / '.claude' / 'evolution'))

from scripts.agent_quality_v2 import AgentQuality

@contextmanager
def track_agent(agent_name: str, task: str, version: str = "1.0.0"):
    """Context manager for automatic tracking"""
    quality = AgentQuality(agent_name, version)
    start_time = time.time()

    try:
        yield quality
        # Success
        duration = time.time() - start_time
        quality.record(task, "pass", duration=duration)
        print(f"✅ {agent_name}: {task} - SUCCESS ({duration:.2f}s)")
    except Exception as e:
        # Failure
        duration = time.time() - start_time
        quality.record(task, "fail", duration=duration, error=str(e))
        print(f"❌ {agent_name}: {task} - FAILED ({duration:.2f}s): {e}")
        raise

# 사용
with track_agent("debugger", "Fix bug"):
    # Your code here
    fix_bug()
```

---

## 🔍 분석 및 리포트

분석은 **전역 레포에서** 실행:

```bash
cd /path/to/claude01

# 전체 요약
python .claude/evolution/scripts/analyze_quality2.py --summary

# 특정 Agent 상세
python .claude/evolution/scripts/analyze_quality2.py --agent debugger

# 특정 Agent + Version
python .claude/evolution/scripts/analyze_quality2.py --agent debugger --version 1.2.0

# 추세 분석
python .claude/evolution/scripts/analyze_quality2.py --trend

# 경고 확인 (낮은 성능)
python .claude/evolution/scripts/analyze_quality2.py --alerts

# 특정 Task 분석 (모든 Agent)
python .claude/evolution/scripts/analyze_quality2.py --task "Fix TypeError"

# 날짜 범위 필터
python .claude/evolution/scripts/analyze_quality2.py --summary \
  --start 2025-01-01 \
  --end 2025-01-14
```

---

## 🗂️ 디렉토리 구조

### 권장 구조

```
workspace/
├── claude01/                    # 전역 레포
│   ├── .claude/
│   │   └── evolution/
│   │       ├── scripts/
│   │       │   ├── agent_quality_v2.py    # 핵심 로직
│   │       │   └── analyze_quality2.py    # 분석 도구
│   │       └── templates/
│   │           └── track_wrapper.py       # Wrapper 템플릿
│   └── scripts/
│       └── setup_subrepo_tracking.py      # 설정 스크립트
│
├── my-project-1/                # 서브 레포 1
│   ├── .claude/
│   │   ├── track.py             # Wrapper (복사됨)
│   │   └── README.md            # 사용 가이드
│   ├── .env                     # CLAUDE_GLOBAL_REPO=/path/to/claude01
│   ├── .gitignore               # .agent-quality-v2.jsonl
│   └── .agent-quality-v2.jsonl  # 로그 (자동 생성)
│
└── my-project-2/                # 서브 레포 2
    └── (동일한 구조)
```

---

## 🛠️ 수동 설정 (자동 스크립트 대신)

자동 스크립트를 사용할 수 없는 경우:

### 1. .env 파일 생성

```bash
# 서브 레포에서
cat > .env <<EOF
# Agent Quality Tracking
CLAUDE_GLOBAL_REPO=/path/to/claude01
EOF
```

### 2. track.py 복사

```bash
cp /path/to/claude01/.claude/evolution/templates/track_wrapper.py .claude/track.py
```

### 3. .gitignore 업데이트

```bash
cat >> .gitignore <<EOF

# Agent Quality Tracking
.agent-quality-v2.jsonl
.agent-quality.jsonl.bak
EOF
```

### 4. 테스트

```bash
python .claude/track.py --help
```

---

## 🔄 템플릿 업데이트 시

전역 레포의 `agent_quality_v2.py`가 업데이트되면:

### 자동 반영 ✅

```bash
# 서브 레포에서는 아무것도 안 해도 됨!
# Python import로 직접 참조하므로 자동으로 최신 버전 사용
```

### Wrapper만 업데이트 필요 (드물게)

`track_wrapper.py`가 변경된 경우만 재설치:

```bash
cd /path/to/claude01
python scripts/setup_subrepo_tracking.py /path/to/sub-repo
# → track.py만 덮어씌움
```

---

## 🐛 문제 해결

### 문제 1: "전역 레포를 찾을 수 없습니다"

```
❌ 전역 레포 (claude01)를 찾을 수 없습니다!
```

**해결책**:
```bash
# .env 파일 확인
cat .env

# CLAUDE_GLOBAL_REPO 설정
echo "CLAUDE_GLOBAL_REPO=/path/to/claude01" >> .env
```

### 문제 2: "agent_quality_v2를 import할 수 없습니다"

```
❌ agent_quality_v2를 import할 수 없습니다
```

**해결책**:
```bash
# 전역 레포 경로 확인
ls $CLAUDE_GLOBAL_REPO/.claude/evolution/scripts/agent_quality_v2.py

# 없으면 경로 수정
vim .env
```

### 문제 3: 로그 파일이 Git에 포함됨

```
git status
# .agent-quality-v2.jsonl이 보임
```

**해결책**:
```bash
# .gitignore 업데이트
cat >> .gitignore <<EOF
.agent-quality-v2.jsonl
EOF

# 이미 추가된 경우
git rm --cached .agent-quality-v2.jsonl
git commit -m "Remove quality log from git"
```

---

## 📊 통합 워크플로우 예시

### Scenario: Phase 0-6 개발 사이클

```bash
# Phase 0: PRD
with track_agent("context7-engineer", "Verify Next.js docs", version="1.0.0"):
    verify_nextjs_docs()

# Phase 1: 구현
with track_agent("fullstack-developer", "Implement auth", version="1.0.0"):
    implement_auth()

# Phase 2: 테스트
with track_agent("test-automator", "Write unit tests", version="1.0.0"):
    write_unit_tests()

with track_agent("playwright-engineer", "E2E tests", version="1.0.0"):
    run_e2e_tests()

# Phase 3: 버전 태그
git tag v1.0.0

# Phase 4: PR 생성
# (자동)

# Phase 5: 최종 E2E
with track_agent("playwright-engineer", "Production E2E", version="1.0.0"):
    run_production_e2e()

# Phase 6: 배포
# (자동)
```

### 분석 (전역 레포)

```bash
cd /path/to/claude01

# 이번 주 성능 확인
python .claude/evolution/scripts/analyze_quality2.py --summary \
  --start 2025-01-08 \
  --end 2025-01-14

# Agent별 상세
python .claude/evolution/scripts/analyze_quality2.py --agent playwright-engineer

# 경고 확인
python .claude/evolution/scripts/analyze_quality2.py --alerts
```

---

## 💡 Best Practices

### 1. 환경변수 우선순위

```bash
# 1순위: 환경변수
export CLAUDE_GLOBAL_REPO=/path/to/claude01

# 2순위: .env 파일
echo "CLAUDE_GLOBAL_REPO=/path/to/claude01" > .env

# 3순위: 자동 감지 (형제 디렉토리)
# parent/claude01, parent/parent/claude01
```

### 2. CI/CD 통합

```yaml
# .github/workflows/test.yml
- name: Setup Agent Tracking
  run: |
    export CLAUDE_GLOBAL_REPO=${{ github.workspace }}/../claude01
    python .claude/track.py test-automator "CI Tests" pass --auto-detected
```

### 3. Git Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Agent 사용 통계 자동 기록
export CLAUDE_GLOBAL_REPO=/path/to/claude01
python .claude/track.py code-reviewer "Pre-commit review" pass --auto-detected
```

---

## 📚 관련 문서

- **MIGRATION_GUIDE.md** - v1.0 → v2.0 마이그레이션
- **REDESIGNED_SYSTEM.md** - v2.0 설계 명세
- **agent_quality_v2.py** - 핵심 로직 소스 코드
- **analyze_quality2.py** - 분석 도구 소스 코드

---

**Version**: 2.0.0
**Last Updated**: 2025-01-14
**Status**: ✅ Production Ready
