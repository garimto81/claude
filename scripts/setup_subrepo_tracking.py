#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Agent Quality Tracking for Sub-Repos
서브 레포에 Agent Quality Tracking 설정

Usage:
    # 현재 디렉토리에 설정
    python scripts/setup_subrepo_tracking.py

    # 특정 디렉토리에 설정
    python scripts/setup_subrepo_tracking.py /path/to/sub-repo

    # 여러 서브 레포에 한 번에 설정
    python scripts/setup_subrepo_tracking.py ../repo1 ../repo2 ../repo3
"""

import sys
import os
import io
import shutil
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def setup_tracking(subrepo_path: Path, global_repo_path: Path):
    """서브 레포에 tracking 설정"""
    print(f"\n{'='*60}")
    print(f"🔧 Setting up: {subrepo_path}")
    print(f"{'='*60}")

    # 1. .claude 디렉토리 생성
    claude_dir = subrepo_path / '.claude'
    claude_dir.mkdir(exist_ok=True)
    print(f"✅ Created: {claude_dir}")

    # 2. track_wrapper.py 복사
    template_file = global_repo_path / '.claude' / 'evolution' / 'templates' / 'track_wrapper.py'
    target_file = claude_dir / 'track.py'

    if not template_file.exists():
        print(f"❌ Template not found: {template_file}")
        return False

    shutil.copy2(template_file, target_file)
    print(f"✅ Copied: track.py (wrapper)")

    # 3. .env 파일 생성/업데이트
    env_file = subrepo_path / '.env'
    env_line = f"CLAUDE_GLOBAL_REPO={global_repo_path.absolute()}\n"

    if env_file.exists():
        # 기존 파일 읽기
        with open(env_file, 'r') as f:
            content = f.read()

        # CLAUDE_GLOBAL_REPO가 없으면 추가
        if 'CLAUDE_GLOBAL_REPO' not in content:
            with open(env_file, 'a') as f:
                f.write(f"\n# Agent Quality Tracking\n")
                f.write(env_line)
            print(f"✅ Updated: .env (added CLAUDE_GLOBAL_REPO)")
        else:
            print(f"ℹ️  .env already has CLAUDE_GLOBAL_REPO")
    else:
        # 새 파일 생성
        with open(env_file, 'w') as f:
            f.write("# Agent Quality Tracking\n")
            f.write(env_line)
        print(f"✅ Created: .env")

    # 4. .gitignore 업데이트
    gitignore_file = subrepo_path / '.gitignore'
    gitignore_lines = [
        "# Agent Quality Tracking",
        ".agent-quality-v2.jsonl",
        ".agent-quality.jsonl.bak",
        ""
    ]

    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            content = f.read()

        # 이미 있는지 확인
        if '.agent-quality-v2.jsonl' not in content:
            with open(gitignore_file, 'a') as f:
                f.write("\n" + "\n".join(gitignore_lines))
            print(f"✅ Updated: .gitignore")
        else:
            print(f"ℹ️  .gitignore already configured")
    else:
        with open(gitignore_file, 'w') as f:
            f.write("\n".join(gitignore_lines))
        print(f"✅ Created: .gitignore")

    # 5. README.md 생성 (사용 가이드)
    readme_file = claude_dir / 'README.md'
    readme_content = f"""# Agent Quality Tracking

이 디렉토리는 Agent Quality Tracking v2.0 시스템을 사용합니다.

## 설정 완료 ✅

- `track.py`: Agent 사용 기록 스크립트
- `.env`: 전역 레포 경로 설정
- `.gitignore`: 로그 파일 제외

## 사용법

### 1. Agent 사용 기록

```bash
# 성공
python .claude/track.py debugger "Fix TypeError" pass --duration 1.5

# 실패
python .claude/track.py test-automator "Write tests" fail --error "Timeout"

# Phase 정보 포함
python .claude/track.py context7-engineer "Verify docs" pass --phase "Phase 0"
```

### 2. 분석 (전역 레포에서)

```bash
cd {global_repo_path}

# 전체 요약
python .claude/evolution/scripts/analyze_quality2.py --summary

# 특정 Agent
python .claude/evolution/scripts/analyze_quality2.py --agent debugger

# 추세 분석
python .claude/evolution/scripts/analyze_quality2.py --trend
```

### 3. 자동 기록 (Python 코드에서)

```python
import sys
sys.path.insert(0, '{global_repo_path.absolute()}/.claude/evolution')

from scripts.agent_quality_v2 import AgentQuality

quality = AgentQuality("debugger", version="1.0.0")
quality.record("Fix bug", "pass", duration=1.5)
```

## 로그 파일

- `.agent-quality-v2.jsonl`: Agent 사용 로그 (자동 생성)
- Git에서 제외됨 (`.gitignore`)

## 문서

전체 문서: `{global_repo_path}/.claude/evolution/MIGRATION_GUIDE.md`
"""

    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✅ Created: .claude/README.md (usage guide)")

    # 6. 테스트
    print(f"\n🧪 Testing...")
    test_cmd = f"cd {subrepo_path} && python .claude/track.py --help"
    result = os.system(test_cmd + " > /dev/null 2>&1")

    if result == 0:
        print(f"✅ Test passed: track.py is working")
    else:
        print(f"⚠️  Test failed: Please check manually")

    # 완료 메시지
    print(f"\n{'='*60}")
    print(f"✅ Setup complete for: {subrepo_path.name}")
    print(f"{'='*60}")

    print(f"\n📝 Quick Start:")
    print(f"cd {subrepo_path}")
    print(f"python .claude/track.py debugger 'Fix bug' pass --duration 1.5")

    return True


def main():
    # 전역 레포 경로 (이 스크립트가 있는 곳)
    script_path = Path(__file__).resolve()
    global_repo_path = script_path.parent.parent

    print(f"🌍 Global repo: {global_repo_path}")

    # 서브 레포 경로들
    if len(sys.argv) > 1:
        subrepo_paths = [Path(arg).resolve() for arg in sys.argv[1:]]
    else:
        # 인자 없으면 현재 디렉토리
        subrepo_paths = [Path.cwd()]

    # 각 서브 레포에 설정
    success_count = 0
    fail_count = 0

    for subrepo_path in subrepo_paths:
        if not subrepo_path.exists():
            print(f"\n❌ Directory not found: {subrepo_path}")
            fail_count += 1
            continue

        # 전역 레포 자신은 제외
        if subrepo_path.resolve() == global_repo_path.resolve():
            print(f"\n⚠️  Skipping global repo: {subrepo_path}")
            continue

        try:
            if setup_tracking(subrepo_path, global_repo_path):
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"\n❌ Error: {e}")
            fail_count += 1

    # 최종 결과
    print(f"\n{'='*60}")
    print(f"📊 Summary")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")

    if success_count > 0:
        print(f"\n💡 Next steps:")
        print(f"1. 서브 레포에서 Agent 사용할 때마다 기록")
        print(f"2. python .claude/track.py <agent> <task> <status>")
        print(f"3. 전역 레포에서 분석: analyze_quality2.py --summary")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
