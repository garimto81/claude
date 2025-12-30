#!/usr/bin/env python3
"""
Checklist Task Start Hook
서브 에이전트(Task tool) 시작 시 체크리스트에 current_task 설정
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml


def find_checklist_yaml(start_path: Path) -> Path | None:
    """현재 디렉토리부터 상위로 checklist.yaml 검색"""
    current = start_path
    while current != current.parent:
        checklist = current / "checklist.yaml"
        if checklist.exists():
            return checklist
        current = current.parent
    return None


def get_next_task_id(data: dict) -> str:
    """다음 TASK ID 생성"""
    max_id = 0

    # pending에서 찾기
    for task in data.get("pending", []):
        task_id = task.get("id", "TASK-000")
        try:
            num = int(task_id.split("-")[1])
            max_id = max(max_id, num)
        except (IndexError, ValueError):
            pass

    # completed에서 찾기
    for task in data.get("completed", []):
        task_id = task.get("id", "TASK-000")
        try:
            num = int(task_id.split("-")[1])
            max_id = max(max_id, num)
        except (IndexError, ValueError):
            pass

    return f"TASK-{max_id + 1:03d}"


def update_checklist_start(checklist_path: Path, task_info: dict) -> bool:
    """체크리스트에 current_task 설정"""
    try:
        with open(checklist_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        now = datetime.now().isoformat()
        data["updated_at"] = now

        # 이미 current_task가 있으면 스킵 (중복 방지)
        if data.get("current_task") and data["current_task"].get("id"):
            return True

        # 새 current_task 설정
        task_id = get_next_task_id(data)
        data["current_task"] = {
            "id": task_id,
            "title": task_info.get("description", "서브 에이전트 작업"),
            "status": "in_progress",
            "agent": task_info.get("subagent_type", "general-purpose"),
            "started_at": now,
        }

        # agent_logs에 시작 로그 추가
        if "agent_logs" not in data:
            data["agent_logs"] = []
        data["agent_logs"].append(
            {
                "timestamp": now,
                "agent": task_info.get("subagent_type", "general-purpose"),
                "task_id": task_id,
                "action": "작업 시작",
                "status": "in_progress",
            }
        )

        # stats 업데이트
        if "stats" not in data:
            data["stats"] = {"total": 0, "completed": 0, "in_progress": 0, "pending": 0}
        data["stats"]["total"] = data["stats"].get("total", 0) + 1
        data["stats"]["in_progress"] = data["stats"].get("in_progress", 0) + 1

        with open(checklist_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        return True
    except Exception as e:
        print(f"체크리스트 시작 업데이트 실패: {e}", file=sys.stderr)
        return False


def main():
    """메인 함수 - Hook에서 호출됨"""
    # stdin에서 hook 데이터 읽기
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({"continue": True}))
            sys.exit(0)

        hook_data = json.loads(input_data)
    except json.JSONDecodeError:
        print(json.dumps({"continue": True}))
        sys.exit(0)

    # Task tool 확인
    tool_name = hook_data.get("tool_name", "")
    if tool_name != "Task":
        print(json.dumps({"continue": True}))
        sys.exit(0)

    # tool_input에서 정보 추출
    tool_input = hook_data.get("tool_input", {})
    task_info = {
        "description": tool_input.get("description", ""),
        "subagent_type": tool_input.get("subagent_type", "general-purpose"),
        "prompt": tool_input.get("prompt", "")[:100],  # 처음 100자만
    }

    # 체크리스트 찾기 및 업데이트
    cwd = Path(hook_data.get("cwd", os.getcwd()))
    checklist_path = find_checklist_yaml(cwd)

    if checklist_path:
        if update_checklist_start(checklist_path, task_info):
            print(f"📋 체크리스트 작업 시작: {task_info['description']}", file=sys.stderr)

    # Hook은 항상 성공 반환 (차단하지 않음)
    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
