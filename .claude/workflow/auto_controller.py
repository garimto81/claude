#!/usr/bin/env python3
"""
Auto-Completion Workflow Controller
자동 완성 워크플로우 상태 관리 및 제어
"""

import json
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = Path(__file__).parent / "auto_state.json"


def load_state() -> dict:
    """상태 파일 로드"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return get_default_state()


def save_state(state: dict) -> None:
    """상태 파일 저장"""
    state["lastUpdated"] = datetime.now().isoformat()
    STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def get_default_state() -> dict:
    """기본 상태"""
    return {
        "enabled": False,
        "status": "idle",
        "currentTask": None,
        "taskQueue": [],
        "completedTasks": [],
        "failedTasks": [],
        "startedAt": None,
        "lastUpdated": None,
        "options": {
            "maxTasks": 10,
            "autoCommit": True,
            "autoPR": True,
            "skipOnError": True,
            "retryCount": 3,
        },
        "stats": {
            "totalTasks": 0,
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "totalTime": 0,
        },
    }


def start(tasks: list = None, options: dict = None) -> dict:
    """자동 완성 루프 시작"""
    state = load_state()
    state["enabled"] = True
    state["status"] = "running"
    state["startedAt"] = datetime.now().isoformat()
    state["taskQueue"] = tasks or []
    state["completedTasks"] = []
    state["failedTasks"] = []
    if options:
        state["options"].update(options)
    state["stats"] = {
        "totalTasks": len(state["taskQueue"]),
        "completed": 0,
        "failed": 0,
        "skipped": 0,
        "totalTime": 0,
    }
    save_state(state)
    return state


def stop() -> dict:
    """자동 완성 루프 중단"""
    state = load_state()
    state["enabled"] = False
    state["status"] = "stopped"
    save_state(state)
    return state


def pause() -> dict:
    """자동 완성 루프 일시정지"""
    state = load_state()
    state["status"] = "paused"
    save_state(state)
    return state


def resume() -> dict:
    """자동 완성 루프 재개"""
    state = load_state()
    if state["status"] == "paused":
        state["status"] = "running"
        save_state(state)
    return state


def next_task() -> dict | None:
    """다음 작업 가져오기"""
    state = load_state()
    if not state["enabled"] or state["status"] != "running":
        return None
    if not state["taskQueue"]:
        state["status"] = "completed"
        save_state(state)
        return None
    task = state["taskQueue"].pop(0)
    state["currentTask"] = task
    save_state(state)
    return task


def complete_task(task: dict, success: bool = True, error: str = None) -> dict:
    """작업 완료 처리"""
    state = load_state()
    task["completedAt"] = datetime.now().isoformat()
    task["success"] = success
    if error:
        task["error"] = error

    if success:
        state["completedTasks"].append(task)
        state["stats"]["completed"] += 1
    else:
        state["failedTasks"].append(task)
        state["stats"]["failed"] += 1

    state["currentTask"] = None

    # 다음 작업 확인
    if not state["taskQueue"]:
        state["status"] = "completed"
        state["enabled"] = False

    save_state(state)
    return state


def add_task(task: dict) -> dict:
    """작업 추가"""
    state = load_state()
    state["taskQueue"].append(task)
    state["stats"]["totalTasks"] += 1
    save_state(state)
    return state


def get_status() -> dict:
    """현재 상태 조회"""
    return load_state()


def generate_report() -> str:
    """완료 리포트 생성"""
    state = load_state()

    report = []
    report.append("━" * 50)
    report.append("📊 Auto-Completion 최종 리포트")
    report.append("━" * 50)
    report.append("")

    stats = state["stats"]
    report.append(f"총 작업: {stats['totalTasks']}개")
    report.append(f"  ✅ 완료: {stats['completed']}개")
    report.append(f"  ❌ 실패: {stats['failed']}개")
    report.append(f"  ⏭️ 스킵: {stats['skipped']}개")
    report.append("")

    if state["completedTasks"]:
        report.append("완료된 작업:")
        for task in state["completedTasks"]:
            report.append(
                f"  - {task.get('title', task.get('description', 'Unknown'))}"
            )

    if state["failedTasks"]:
        report.append("")
        report.append("실패한 작업:")
        for task in state["failedTasks"]:
            error = task.get("error", "Unknown error")
            report.append(f"  - {task.get('title', 'Unknown')}: {error}")

    report.append("")
    report.append("━" * 50)

    return "\n".join(report)


def main():
    """CLI 진입점"""
    if len(sys.argv) < 2:
        print(json.dumps(get_status(), indent=2, ensure_ascii=False))
        return

    command = sys.argv[1]

    if command == "start":
        tasks = json.loads(sys.argv[2]) if len(sys.argv) > 2 else []
        result = start(tasks)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "stop":
        result = stop()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "pause":
        result = pause()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "resume":
        result = resume()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "next":
        task = next_task()
        print(json.dumps(task, indent=2, ensure_ascii=False) if task else "null")

    elif command == "complete":
        task = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        success = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True
        result = complete_task(task, success)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "add":
        task = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        result = add_task(task)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == "status":
        print(json.dumps(get_status(), indent=2, ensure_ascii=False))

    elif command == "report":
        print(generate_report())

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
