#!/usr/bin/env python3
"""
Auto-Completion Report Generator
자동 완성 완료 리포트 생성기
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(__file__).parent.parent.parent
STATE_FILE = Path(__file__).parent / "auto_state.json"
REPORTS_DIR = Path(__file__).parent / "reports"


def load_state() -> dict:
    """상태 파일 로드"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def get_git_info() -> dict:
    """Git 정보 수집"""
    info = {}

    try:
        # 현재 브랜치
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=str(PROJECT_DIR)
        )
        info["branch"] = result.stdout.strip()

        # 최근 커밋
        result = subprocess.run(
            ["git", "log", "-5", "--oneline"],
            capture_output=True, text=True, cwd=str(PROJECT_DIR)
        )
        info["recent_commits"] = result.stdout.strip().split("\n")

        # 열린 PR
        result = subprocess.run(
            ["gh", "pr", "list", "--json", "number,title,url", "-L", "5"],
            capture_output=True, text=True, cwd=str(PROJECT_DIR)
        )
        if result.returncode == 0:
            info["open_prs"] = json.loads(result.stdout)

    except Exception as e:
        info["error"] = str(e)

    return info


def calculate_duration(start_time: str, end_time: Optional[str] = None) -> str:
    """소요 시간 계산"""
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time) if end_time else datetime.now()
        delta = end - start
        minutes = int(delta.total_seconds() // 60)
        seconds = int(delta.total_seconds() % 60)
        return f"{minutes}m {seconds}s"
    except Exception:
        return "Unknown"


def generate_markdown_report(state: dict) -> str:
    """마크다운 형식 리포트 생성"""
    lines = []

    # 헤더
    lines.append("# Auto-Completion Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # 요약
    stats = state.get("stats", {})
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Tasks | {stats.get('totalTasks', 0)} |")
    lines.append(f"| Completed | {stats.get('completed', 0)} |")
    lines.append(f"| Failed | {stats.get('failed', 0)} |")
    lines.append(f"| Skipped | {stats.get('skipped', 0)} |")

    if state.get("startedAt"):
        duration = calculate_duration(state["startedAt"], state.get("lastUpdated"))
        lines.append(f"| Duration | {duration} |")
    lines.append("")

    # 완료된 작업
    if state.get("completedTasks"):
        lines.append("## Completed Tasks")
        lines.append("")
        for i, task in enumerate(state["completedTasks"], 1):
            title = task.get("title", task.get("description", "Unknown"))
            lines.append(f"{i}. **{title}**")
            if task.get("pr"):
                lines.append(f"   - PR: {task['pr']}")
            if task.get("commit"):
                lines.append(f"   - Commit: `{task['commit']}`")
            if task.get("completedAt"):
                lines.append(f"   - Completed: {task['completedAt'][:16]}")
        lines.append("")

    # 실패한 작업
    if state.get("failedTasks"):
        lines.append("## Failed Tasks")
        lines.append("")
        for task in state["failedTasks"]:
            title = task.get("title", task.get("description", "Unknown"))
            error = task.get("error", "Unknown error")
            lines.append(f"- **{title}**")
            lines.append(f"  - Error: {error}")
        lines.append("")

    # 대기 중인 작업
    if state.get("taskQueue"):
        lines.append("## Pending Tasks")
        lines.append("")
        for task in state["taskQueue"]:
            title = task.get("title", task.get("description", "Unknown"))
            lines.append(f"- {title}")
        lines.append("")

    # Git 정보
    git_info = get_git_info()
    if git_info.get("open_prs"):
        lines.append("## Open PRs")
        lines.append("")
        for pr in git_info["open_prs"]:
            lines.append(f"- [#{pr['number']}]({pr['url']}): {pr['title']}")
        lines.append("")

    # 다음 단계
    lines.append("## Next Steps")
    lines.append("")
    if state.get("failedTasks"):
        lines.append("1. Review failed tasks and resolve issues")
    if git_info.get("open_prs"):
        lines.append("2. Review and merge open PRs")
    if state.get("taskQueue"):
        lines.append("3. Run `/auto --resume` to continue pending tasks")
    if not any([state.get("failedTasks"), git_info.get("open_prs"), state.get("taskQueue")]):
        lines.append("All tasks completed successfully!")

    return "\n".join(lines)


def generate_console_report(state: dict) -> str:
    """콘솔 출력용 리포트 생성"""
    lines = []

    lines.append("━" * 50)
    lines.append("📊 Auto-Completion 최종 리포트")
    lines.append("━" * 50)
    lines.append("")

    stats = state.get("stats", {})
    lines.append(f"총 작업: {stats.get('totalTasks', 0)}개")
    lines.append(f"  ✅ 완료: {stats.get('completed', 0)}개")
    lines.append(f"  ❌ 실패: {stats.get('failed', 0)}개")
    lines.append(f"  ⏭️ 스킵: {stats.get('skipped', 0)}개")
    lines.append("")

    if state.get("startedAt"):
        duration = calculate_duration(state["startedAt"], state.get("lastUpdated"))
        lines.append(f"⏱️ 소요 시간: {duration}")
        lines.append("")

    if state.get("completedTasks"):
        lines.append("완료된 작업:")
        for task in state["completedTasks"]:
            title = task.get("title", task.get("description", "Unknown"))
            lines.append(f"  ✓ {title}")

    if state.get("failedTasks"):
        lines.append("")
        lines.append("실패한 작업:")
        for task in state["failedTasks"]:
            title = task.get("title", task.get("description", "Unknown"))
            error = task.get("error", "Unknown")[:50]
            lines.append(f"  ✗ {title}: {error}")

    git_info = get_git_info()
    if git_info.get("open_prs"):
        lines.append("")
        lines.append("생성된 PR:")
        for pr in git_info["open_prs"]:
            lines.append(f"  - #{pr['number']}: {pr['title']}")

    lines.append("")
    lines.append("━" * 50)

    return "\n".join(lines)


def save_report(content: str, format: str = "md") -> Path:
    """리포트 파일 저장"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"auto_report_{timestamp}.{format}"
    filepath = REPORTS_DIR / filename

    filepath.write_text(content, encoding="utf-8")
    return filepath


def main():
    """CLI 진입점"""
    state = load_state()

    if not state:
        print("No auto-completion state found.")
        sys.exit(1)

    format_type = sys.argv[1] if len(sys.argv) > 1 else "console"
    save_to_file = "--save" in sys.argv

    if format_type == "md" or format_type == "markdown":
        report = generate_markdown_report(state)
    else:
        report = generate_console_report(state)

    print(report)

    if save_to_file:
        ext = "md" if format_type in ["md", "markdown"] else "txt"
        filepath = save_report(report, ext)
        print(f"\n📄 리포트 저장됨: {filepath}")


if __name__ == "__main__":
    main()
