#!/usr/bin/env python3
"""
세션 시작 Hook - 브랜치 확인, TODO 표시, Stale 상태 정리

SessionStart 이벤트에서 실행됩니다.
"""

import json
import subprocess
import os
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def _get_project_root() -> Path:
    """플랫폼에 따라 루트 프로젝트 경로 반환"""
    if os.name == "nt":
        return Path("C:/claude")
    wsl_path = Path("/mnt/c/claude")
    if wsl_path.exists():
        return wsl_path
    return Path(PROJECT_DIR)


ROOT_PROJECT_DIR = _get_project_root()
ROOT_COMMANDS_DIR = ROOT_PROJECT_DIR / ".claude" / "commands"


def get_current_branch() -> str:
    """현재 브랜치 이름 반환"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def get_uncommitted_changes() -> int:
    """커밋되지 않은 변경 수"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR,
        )
        return len([line for line in result.stdout.strip().split("\n") if line])
    except Exception:
        return 0


def setup_commands_junction() -> tuple[bool, str]:
    """서브 프로젝트에 커맨드 Junction 자동 설정"""
    project_path = Path(PROJECT_DIR)

    if project_path == ROOT_PROJECT_DIR:
        return False, ""

    try:
        project_path.relative_to(ROOT_PROJECT_DIR)
    except ValueError:
        return False, ""

    if not ROOT_COMMANDS_DIR.exists():
        return False, ""

    claude_dir = project_path / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)

    commands_dir = claude_dir / "commands"
    if commands_dir.exists():
        return False, ""

    try:
        result = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(commands_dir), str(ROOT_COMMANDS_DIR)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 or commands_dir.exists():
            gitignore_path = project_path / ".gitignore"
            gitignore_entry = ".claude/commands/"

            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding="utf-8")
                if gitignore_entry not in content:
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write(f"\n# Claude commands (Junction to root)\n{gitignore_entry}\n")
            else:
                gitignore_path.write_text(
                    f"# Claude commands (Junction to root)\n{gitignore_entry}\n",
                    encoding="utf-8"
                )

            return True, f"✨ 커맨드 Junction 자동 설정됨 → {ROOT_COMMANDS_DIR}"
        else:
            return False, ""
    except Exception:
        return False, ""


def _deactivate_state_file(path: Path, now: datetime) -> str | None:
    """상태 JSON 파일의 active 플래그를 비활성화 (새 세션이므로 무조건 stale)"""
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)

        if not state.get("active"):
            return None

        state["active"] = False
        state["deactivated_reason"] = "SessionStart cleanup (new session)"
        state["deactivated_at"] = now.isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        name = path.stem
        return f"🔄 {name} 비활성화 (새 세션 시작)"
    except Exception:
        return None


def cleanup_stale_omc_states(ttl_hours: int = 2) -> list[str]:
    """OMC persistent mode의 stale 상태를 정리 (Stop hook 차단 방지)

    정리 대상:
    - .omc/ultrawork-state.json (local)
    - ~/.claude/ultrawork-state.json (global)
    - .omc/ralph-state.json
    - .omc/ralph-verification.json
    - .omc/continuation-count.json
    - ~/.claude/.session-stats.json
    """
    messages = []
    now = datetime.now(timezone.utc)
    omc_dir = Path(PROJECT_DIR) / ".omc"
    global_claude_dir = Path.home() / ".claude"

    # ultrawork-state (LOCAL + GLOBAL)
    for ultrawork_path in [
        omc_dir / "ultrawork-state.json",
        global_claude_dir / "ultrawork-state.json",
    ]:
        msg = _deactivate_state_file(ultrawork_path, now)
        if msg:
            loc = "global" if ultrawork_path.parent == global_claude_dir else "local"
            messages.append(f"{msg} [{loc}]")

    # ralph-state
    msg = _deactivate_state_file(omc_dir / "ralph-state.json", now)
    if msg:
        messages.append(msg)

    # ralph-verification
    ralph_verify_path = omc_dir / "ralph-verification.json"
    if ralph_verify_path.exists():
        try:
            with open(ralph_verify_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            modified = False
            if state.get("pending"):
                state["pending"] = False
                modified = True
            if state.get("status") == "pending":
                state["status"] = "expired"
                modified = True
            if modified:
                state["expired_reason"] = "SessionStart cleanup (new session)"
                with open(ralph_verify_path, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2)
                messages.append("🔄 ralph-verification pending 상태 만료 처리")
        except Exception:
            pass

    # continuation-count 항상 리셋
    cont_path = omc_dir / "continuation-count.json"
    if cont_path.exists():
        try:
            with open(cont_path, "r", encoding="utf-8") as f:
                cont_state = json.load(f)
            prev_count = cont_state.get("count", 0)
            if prev_count > 0:
                with open(cont_path, "w", encoding="utf-8") as f:
                    json.dump({"count": 0, "reset_at": now.isoformat()}, f, indent=2)
                messages.append(f"🔄 Todo continuation 카운터 리셋 (이전: {prev_count}회)")
        except Exception:
            pass

    # 로컬 TODO 파일 정리
    for local_todo_path in [
        omc_dir / "todos.json",
        Path(PROJECT_DIR) / ".claude" / "todos.json",
    ]:
        if local_todo_path.exists():
            try:
                mtime = datetime.fromtimestamp(
                    local_todo_path.stat().st_mtime, tz=timezone.utc
                )
                elapsed = now - mtime
                if elapsed > timedelta(hours=ttl_hours):
                    with open(local_todo_path, "r", encoding="utf-8") as f:
                        todos = json.load(f)
                    if isinstance(todos, list) and any(
                        isinstance(t, dict)
                        and t.get("status") not in ("completed", "cancelled")
                        for t in todos
                    ):
                        with open(local_todo_path, "w", encoding="utf-8") as f:
                            json.dump([], f)
                        messages.append(f"🔄 로컬 TODO 정리: {local_todo_path.name}")
            except Exception:
                pass

    # 세션 통계 리셋
    stats_path = global_claude_dir / ".session-stats.json"
    if stats_path.exists():
        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                stats = json.load(f)
            if isinstance(stats.get("sessions"), dict):
                stats["sessions"] = {}
                stats["sessionStart"] = now.isoformat()
                with open(stats_path, "w", encoding="utf-8") as f:
                    json.dump(stats, f, indent=2)
            elif stats.get("toolCalls", 0) > 0:
                stats["toolCalls"] = 0
                stats["sessionStart"] = now.isoformat()
                with open(stats_path, "w", encoding="utf-8") as f:
                    json.dump(stats, f, indent=2)
        except Exception:
            pass

    return messages


def cleanup_orphan_agent_teams() -> list[str]:
    """세션 시작 시 고아 Agent Teams 즉시 정리 (TTL 없이 모두 제거)"""
    messages = []
    home = Path.home()
    teams_dir = home / ".claude" / "teams"
    tasks_dir = home / ".claude" / "tasks"

    # Teams 정리
    deleted_teams = []
    if teams_dir.exists():
        for entry in teams_dir.iterdir():
            if entry.is_dir():
                try:
                    shutil.rmtree(entry)
                    deleted_teams.append(entry.name)
                except Exception as e:
                    messages.append(f"⚠️ 팀 정리 실패: {entry.name} ({e})")

    # Tasks 정리 (teams와 같은 이름만)
    if tasks_dir.exists():
        for entry in tasks_dir.iterdir():
            if entry.is_dir() and entry.name in deleted_teams:
                try:
                    shutil.rmtree(entry)
                except Exception:
                    pass

    if deleted_teams:
        messages.append(f"🧹 고아 팀 {len(deleted_teams)}개 정리: {', '.join(deleted_teams[:3])}{'...' if len(deleted_teams) > 3 else ''}")

    return messages


def cleanup_stale_global_todos(ttl_hours: int = 2) -> list[str]:
    """~/.claude/todos/ 내 이전 세션의 stale TODO 파일 정리

    persistent-mode.mjs의 countIncompleteTodos()가 이전 agent 세션의
    미완료 TODO를 감지하여 새 세션의 Stop hook을 차단하는 문제를 방지합니다.
    """
    messages = []
    now = datetime.now(timezone.utc)
    todos_dir = Path.home() / ".claude" / "todos"

    if not todos_dir.exists():
        return messages

    cleaned_count = 0
    incomplete_total = 0

    try:
        for todo_file in todos_dir.glob("*.json"):
            try:
                mtime = datetime.fromtimestamp(
                    todo_file.stat().st_mtime, tz=timezone.utc
                )
                elapsed = now - mtime

                if elapsed <= timedelta(hours=ttl_hours):
                    continue

                with open(todo_file, "r", encoding="utf-8") as f:
                    todos = json.load(f)

                if not isinstance(todos, list) or len(todos) == 0:
                    continue

                incomplete = [
                    t for t in todos
                    if isinstance(t, dict)
                    and t.get("status") not in ("completed", "cancelled")
                ]

                if not incomplete:
                    continue

                incomplete_total += len(incomplete)

                with open(todo_file, "w", encoding="utf-8") as f:
                    json.dump([], f)
                cleaned_count += 1

            except Exception:
                continue

    except Exception:
        pass

    if cleaned_count > 0:
        messages.append(
            f"🔄 Stale TODO 파일 정리: {cleaned_count}개 파일, "
            f"{incomplete_total}개 미완료 항목 초기화 (TTL {ttl_hours}h 초과)"
        )

    return messages


def check_fatigue_signals(ttl_hours: int = 24) -> list[str]:
    """피로도 신호 파일 분석 및 경고 생성"""
    warnings = []
    fatigue_log = ROOT_PROJECT_DIR / ".claude" / "logs" / "fatigue_signals.jsonl"

    if not fatigue_log.exists():
        return warnings

    try:
        import json
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=ttl_hours)
        cutoff_ts = cutoff.timestamp() * 1000  # ms

        content = fatigue_log.read_text(encoding="utf-8")
        lines = [l.strip() for l in content.strip().split("\n") if l.strip()]

        burst_files = set()
        burst_count = 0

        for line in lines:
            try:
                entry = json.loads(line)
                if entry.get("type") == "edit_burst" and entry.get("ts", 0) > cutoff_ts:
                    burst_files.add(entry.get("file", ""))
                    burst_count += 1
            except Exception:
                continue

        if burst_count >= 3:
            warnings.append(
                f"⚠️ 피로도 경고: 최근 {ttl_hours}시간 내 집중 편집 패턴 {burst_count}회 감지 "
                f"({len(burst_files)}개 파일). 잠시 휴식을 권장합니다."
            )
        elif burst_count >= 1:
            warnings.append(
                f"📊 편집 집중 패턴: {burst_count}회 (파일: {len(burst_files)}개)"
            )
    except Exception:
        pass

    return warnings


def load_previous_session() -> dict:
    """이전 세션 상태 로드"""
    session_file = Path(PROJECT_DIR) / ".claude" / "session_state.json"
    if session_file.exists():
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_auto_state() -> dict:
    """자동 완성 상태 로드"""
    auto_state_file = Path(PROJECT_DIR) / ".claude" / "workflow" / "auto_state.json"
    if auto_state_file.exists():
        try:
            with open(auto_state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_session_state(state: dict):
    """세션 상태 저장"""
    session_file = Path(PROJECT_DIR) / ".claude" / "session_state.json"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    state["last_start"] = datetime.now().isoformat()
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def main():
    try:
        # Stale 상태 정리 (Stop hook 차단 방지)
        stale_messages = cleanup_stale_omc_states(ttl_hours=2)
        stale_messages.extend(cleanup_stale_global_todos(ttl_hours=2))
        stale_messages.extend(cleanup_orphan_agent_teams())
        stale_messages.extend(check_fatigue_signals(ttl_hours=24))

        # Junction 설정
        junction_created, junction_message = setup_commands_junction()

        # 세션 정보
        prev_session = load_previous_session()
        branch = get_current_branch()
        changes = get_uncommitted_changes()

        session_info = []
        session_info.extend(stale_messages)

        if junction_created:
            session_info.append(junction_message)

        # 브랜치 경고
        if branch in ["main", "master"]:
            session_info.append(
                f"⚠️ 현재 {branch} 브랜치입니다. 기능 개발 시 새 브랜치 생성 권장"
            )

        # 미커밋 변경사항
        if changes > 0:
            session_info.append(f"📝 커밋되지 않은 변경: {changes}개 파일")

        # 이전 세션 미완료 작업
        if prev_session.get("pending_tasks"):
            tasks = prev_session["pending_tasks"]
            session_info.append(f"📋 이전 세션 미완료 작업: {len(tasks)}개")
            for task in tasks[:3]:
                session_info.append(f"   - {task}")
            if len(tasks) > 3:
                session_info.append(f"   ... 외 {len(tasks) - 3}개")

        # 자동 완성 상태
        auto_state = load_auto_state()
        if auto_state.get("enabled") and auto_state.get("status") in ["running", "paused"]:
            queue_len = len(auto_state.get("taskQueue", []))
            completed = auto_state.get("stats", {}).get("completed", 0)
            session_info.append("")
            session_info.append(
                f"🔄 자동 완성 루프 {'일시정지' if auto_state['status'] == 'paused' else '진행'} 중"
            )
            session_info.append(f"   - 완료: {completed}개, 대기: {queue_len}개")
            if auto_state.get("currentTask"):
                task_title = auto_state["currentTask"].get("title", "Unknown")
                session_info.append(f"   - 현재 작업: {task_title}")
            session_info.append("   → /auto --resume 로 재개 가능")

        # 세션 상태 저장
        save_session_state(
            {
                "branch": branch,
                "pending_tasks": prev_session.get("pending_tasks", []),
                "last_end": prev_session.get("last_end"),
            }
        )

        # 출력
        if session_info:
            message = "\n".join(session_info)
            print(json.dumps({"continue": True, "message": f"📍 세션 시작\n\n{message}"}))
        else:
            print(json.dumps({"continue": True}))

    except Exception as e:
        print(json.dumps({"continue": True, "error": str(e)}))


if __name__ == "__main__":
    main()
