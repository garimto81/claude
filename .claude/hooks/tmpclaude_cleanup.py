#!/usr/bin/env python3
"""
Task 도구 완료 후 tmpclaude-*-cwd 임시 파일 즉시 정리

PostToolUse (Task) 이벤트에서 실행됩니다.
Claude Code Windows 버그 대응 - 서브에이전트 종료 시 정리되지 않는 파일 삭제
"""

import glob
import json
import os
import sys
from pathlib import Path

TMPCLAUDE_PATTERN = "tmpclaude-*-cwd"


def cleanup_tmpclaude_files(cwd: str) -> int:
    """현재 디렉토리와 상위 프로젝트 루트에서 tmpclaude 파일 삭제"""
    cleaned = 0
    search_paths = set()

    # 현재 작업 디렉토리
    search_paths.add(cwd)

    # 상위 디렉토리들도 검색 (프로젝트 루트까지)
    current = Path(cwd)
    for _ in range(5):  # 최대 5단계 상위까지
        search_paths.add(str(current))
        if current == current.parent:
            break
        current = current.parent

    # 각 경로에서 tmpclaude 파일 삭제
    for search_path in search_paths:
        pattern = os.path.join(search_path, TMPCLAUDE_PATTERN)
        for filepath in glob.glob(pattern):
            try:
                os.remove(filepath)
                cleaned += 1
            except Exception:
                pass

    return cleaned


def main():
    """메인 함수 - PostToolUse Hook에서 호출"""
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({"continue": True}))
            return

        hook_data = json.loads(input_data)
    except json.JSONDecodeError:
        print(json.dumps({"continue": True}))
        return

    # Task tool 완료 확인
    tool_name = hook_data.get("tool_name", "")
    if tool_name != "Task":
        print(json.dumps({"continue": True}))
        return

    # 작업 디렉토리에서 임시 파일 정리
    cwd = hook_data.get("cwd", os.getcwd())
    cleaned = cleanup_tmpclaude_files(cwd)

    if cleaned > 0:
        print(f"🗑️ tmpclaude 임시 파일 {cleaned}개 삭제", file=sys.stderr)

    # Hook은 항상 성공 반환
    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
