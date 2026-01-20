#!/usr/bin/env python3
"""
세션 시작 Hook - 이전 컨텍스트 로드, 브랜치 확인, TODO 표시

SessionStart 이벤트에서 실행됩니다.
"""

import json
import subprocess
import os
import glob
from datetime import datetime
from pathlib import Path

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
SESSION_FILE = Path(PROJECT_DIR) / ".claude" / "session_state.json"
AUTO_STATE_FILE = Path(PROJECT_DIR) / ".claude" / "workflow" / "auto_state.json"

# 루트 프로젝트 경로 (커맨드 Junction 소스)
ROOT_PROJECT_DIR = Path("C:/claude")
ROOT_COMMANDS_DIR = ROOT_PROJECT_DIR / ".claude" / "commands"

# Claude Code Task 도구가 생성하는 임시 파일 패턴
TMPCLAUDE_PATTERN = "tmpclaude-*-cwd"


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


def cleanup_tmpclaude_files() -> int:
    """tmpclaude-*-cwd 임시 파일 재귀적 삭제 (Claude Code Task 도구 버그 대응)"""
    cleaned = 0
    try:
        # 모든 하위 디렉토리에서 재귀 검색
        pattern = os.path.join(PROJECT_DIR, "**", TMPCLAUDE_PATTERN)
        for filepath in glob.glob(pattern, recursive=True):
            try:
                os.remove(filepath)
                cleaned += 1
            except Exception:
                pass
        # 루트 디렉토리도 검색
        pattern = os.path.join(PROJECT_DIR, TMPCLAUDE_PATTERN)
        for filepath in glob.glob(pattern):
            try:
                os.remove(filepath)
                cleaned += 1
            except Exception:
                pass
    except Exception:
        pass
    return cleaned


def cleanup_malformed_folders() -> int:
    """경로 버그로 생성된 비정상 폴더 삭제 (재귀적 검사)

    검사 패턴:
    - C:로 시작하는 폴더명 (예: C:claude.claudeworkflowresults)
    - Cclaud로 시작하는 폴더명 (예: Cclaudegfx_json)
    - .claude 뒤에 알파벳이 붙은 폴더 (예: .claudeX)

    검사 범위:
    - 루트 레벨 + 1단계 하위 프로젝트 (node_modules, .git 등 제외)
    """
    import re
    import shutil

    # 비정상 폴더 패턴 (malformed path patterns)
    MALFORMED_PATTERNS = [
        r'^[A-Z]:',           # C:로 시작 (하드코딩 경로 버그)
        r'^Cclaud',           # Cclaud로 시작 (경로 버그 변형)
        r'\.claude[a-zA-Z]',  # .claudeX 형태 (정상 .claude는 제외)
    ]

    # 검사 제외 폴더
    SKIP_DIRS = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build', '.next'}

    cleaned = 0

    def is_malformed(name: str) -> bool:
        """폴더명이 malformed 패턴에 해당하는지 확인"""
        return any(re.match(pattern, name) for pattern in MALFORMED_PATTERNS)

    def clean_directory(path: Path, depth: int = 0, max_depth: int = 2) -> int:
        """재귀적으로 디렉토리 검사 및 정리"""
        count = 0
        if depth > max_depth:
            return count
        try:
            for item in path.iterdir():
                if not item.is_dir():
                    continue
                # malformed 패턴 감지
                if is_malformed(item.name):
                    try:
                        shutil.rmtree(item)
                        count += 1
                    except Exception:
                        pass
                # 재귀 탐색 (스킵 폴더 제외)
                elif item.name not in SKIP_DIRS:
                    count += clean_directory(item, depth + 1, max_depth)
        except PermissionError:
            pass
        except Exception:
            pass
        return count

    try:
        project_path = Path(PROJECT_DIR)
        cleaned = clean_directory(project_path)
    except Exception:
        pass

    return cleaned


def setup_commands_junction() -> tuple[bool, str]:
    """서브 프로젝트에 커맨드 Junction 자동 설정

    Returns:
        tuple[bool, str]: (설정 여부, 메시지)
    """
    project_path = Path(PROJECT_DIR)

    # 루트 프로젝트면 스킵
    if project_path == ROOT_PROJECT_DIR:
        return False, ""

    # C:\claude 하위 프로젝트가 아니면 스킵
    try:
        project_path.relative_to(ROOT_PROJECT_DIR)
    except ValueError:
        return False, ""

    # 루트 커맨드가 없으면 스킵
    if not ROOT_COMMANDS_DIR.exists():
        return False, ""

    # .claude 폴더 생성 (없으면)
    claude_dir = project_path / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)

    commands_dir = claude_dir / "commands"

    # 이미 커맨드 폴더가 있으면 스킵 (Junction 또는 실제 폴더)
    if commands_dir.exists():
        return False, ""

    # Junction 생성 (Windows)
    try:
        # subprocess로 mklink /J 실행 (관리자 권한 불필요)
        result = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(commands_dir), str(ROOT_COMMANDS_DIR)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 or commands_dir.exists():
            # .gitignore에 추가
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
            return False, f"⚠️ Junction 생성 실패: {result.stderr}"
    except Exception as e:
        return False, f"⚠️ Junction 설정 오류: {e}"


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
        # 이전 세션 임시 파일 정리 (Claude Code Task 도구 버그 대응)
        cleaned_files = cleanup_tmpclaude_files()

        # 비정상 폴더 정리 (경로 버그로 생성된 폴더)
        cleaned_folders = cleanup_malformed_folders()

        # 서브 프로젝트 커맨드 Junction 자동 설정
        junction_created, junction_message = setup_commands_junction()

        # 이전 세션 로드
        prev_session = load_previous_session()

        # 현재 상태 수집
        branch = get_current_branch()
        changes = get_uncommitted_changes()

        # 세션 정보 생성
        session_info = []

        # Junction 자동 설정 결과
        if junction_created:
            session_info.append(junction_message)

        # 임시 파일/폴더 정리 결과
        if cleaned_files > 0 or cleaned_folders > 0:
            msg = "🗑️ 정리 완료:"
            if cleaned_files > 0:
                msg += f" 임시 파일 {cleaned_files}개"
            if cleaned_folders > 0:
                msg += f" 비정상 폴더 {cleaned_folders}개"
            session_info.append(msg)

        # 브랜치 경고 (main에서 작업 중인 경우)
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
            for task in tasks[:3]:  # 최대 3개만 표시
                session_info.append(f"   - {task}")
            if len(tasks) > 3:
                session_info.append(f"   ... 외 {len(tasks) - 3}개")

        # 이전 세션 종료 시간
        if prev_session.get("last_end"):
            session_info.append(f"🕐 이전 세션: {prev_session['last_end'][:16]}")

        # 자동 완성 상태 확인
        auto_state = load_auto_state()
        if auto_state.get("enabled") and auto_state.get("status") in [
            "running",
            "paused",
        ]:
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

        # 결과 출력
        if session_info:
            message = "\n".join(session_info)
            print(
                json.dumps({"continue": True, "message": f"📍 세션 시작\n\n{message}"})
            )
        else:
            print(json.dumps({"continue": True}))

    except Exception as e:
        print(json.dumps({"continue": True, "error": str(e)}))


if __name__ == "__main__":
    main()
