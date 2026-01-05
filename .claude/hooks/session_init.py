#!/usr/bin/env python3
"""
세션 시작 Hook - 이전 컨텍스트 로드, 브랜치 확인, TODO 표시

SessionStart 이벤트에서 실행됩니다.
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", "D:/AI/claude01")
SESSION_FILE = Path(PROJECT_DIR) / ".claude" / "session_state.json"
AUTO_STATE_FILE = Path(PROJECT_DIR) / ".claude" / "workflow" / "auto_state.json"


def get_current_branch() -> str:
    """현재 브랜치 이름 반환"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
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
            cwd=PROJECT_DIR
        )
        return len([line for line in result.stdout.strip().split("\n") if line])
    except Exception:
        return 0


def load_previous_session() -> dict:
    """이전 세션 상태 로드"""
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_auto_state() -> dict:
    """자동 완성 상태 로드"""
    if AUTO_STATE_FILE.exists():
        try:
            with open(AUTO_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_session_state(state: dict):
    """세션 상태 저장"""
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["last_start"] = datetime.now().isoformat()
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def main():
    try:
        # 이전 세션 로드
        prev_session = load_previous_session()

        # 현재 상태 수집
        branch = get_current_branch()
        changes = get_uncommitted_changes()

        # 세션 정보 생성
        session_info = []

        # 브랜치 경고 (main에서 작업 중인 경우)
        if branch in ["main", "master"]:
            session_info.append(f"⚠️ 현재 {branch} 브랜치입니다. 기능 개발 시 새 브랜치 생성 권장")

        # 미커밋 변경사항
        if changes > 0:
            session_info.append(f"📝 커밋되지 않은 변경: {changes}개 파일")

        # 이전 세션 미완료 작업
        if prev_session.get("pending_tasks"):
            tasks = prev_session["pending_tasks"]
            session_info.append(f"📋 이전 세션 미완료 작업: {len(tasks)}개")
            for task in tasks[:3]:  # 최대 3개만 표시
                session_info.append(f"   - {task}")
            if len(tasks) > 3:
                session_info.append(f"   ... 외 {len(tasks) - 3}개")

        # 이전 세션 종료 시간
        if prev_session.get("last_end"):
            session_info.append(f"🕐 이전 세션: {prev_session['last_end'][:16]}")

        # 자동 완성 상태 확인
        auto_state = load_auto_state()
        if auto_state.get("enabled") and auto_state.get("status") in ["running", "paused"]:
            queue_len = len(auto_state.get("taskQueue", []))
            completed = auto_state.get("stats", {}).get("completed", 0)
            session_info.append("")
            session_info.append(f"🔄 자동 완성 루프 {'일시정지' if auto_state['status'] == 'paused' else '진행'} 중")
            session_info.append(f"   - 완료: {completed}개, 대기: {queue_len}개")
            if auto_state.get("currentTask"):
                task_title = auto_state["currentTask"].get("title", "Unknown")
                session_info.append(f"   - 현재 작업: {task_title}")
            session_info.append("   → /auto --resume 로 재개 가능")

        # 세션 상태 저장
        save_session_state({
            "branch": branch,
            "pending_tasks": prev_session.get("pending_tasks", []),
            "last_end": prev_session.get("last_end"),
        })

        # 결과 출력
        if session_info:
            message = "\n".join(session_info)
            print(json.dumps({
                "continue": True,
                "message": f"📍 세션 시작\n\n{message}"
            }))
        else:
            print(json.dumps({"continue": True}))

    except Exception as e:
        print(json.dumps({"continue": True, "error": str(e)}))


if __name__ == "__main__":
    main()
