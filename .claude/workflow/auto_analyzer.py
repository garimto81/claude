#!/usr/bin/env python3
"""
Auto-Completion State Analyzer
프로젝트 상태 분석 및 다음 작업 판단
"""

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

PROJECT_DIR = Path(__file__).parent.parent.parent


@dataclass
class GitStatus:
    """Git 상태"""
    branch: str = ""
    is_main: bool = False
    uncommitted_files: int = 0
    unpushed_commits: int = 0
    has_conflicts: bool = False
    ahead: int = 0
    behind: int = 0


@dataclass
class CodeStatus:
    """코드 상태"""
    tests_passing: Optional[bool] = None
    test_failures: int = 0
    lint_errors: int = 0
    build_ok: Optional[bool] = None


@dataclass
class ProjectStatus:
    """프로젝트 상태"""
    open_issues: list = None
    open_prs: list = None
    pending_todos: list = None
    prd_unchecked: int = 0

    def __post_init__(self):
        self.open_issues = self.open_issues or []
        self.open_prs = self.open_prs or []
        self.pending_todos = self.pending_todos or []


@dataclass
class SessionStatus:
    """세션 상태"""
    last_action: str = ""
    in_progress_task: str = ""
    last_user_request: str = ""


@dataclass
class AnalysisResult:
    """분석 결과"""
    git: GitStatus
    code: CodeStatus
    project: ProjectStatus
    session: SessionStatus
    timestamp: str = ""

    def __post_init__(self):
        self.timestamp = datetime.now().isoformat()


def run_command(cmd: list, cwd: Path = PROJECT_DIR) -> tuple[bool, str]:
    """명령 실행"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def analyze_git() -> GitStatus:
    """Git 상태 분석"""
    status = GitStatus()

    # 현재 브랜치
    success, output = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if success:
        status.branch = output
        status.is_main = output in ["main", "master"]

    # 커밋되지 않은 파일
    success, output = run_command(["git", "status", "--porcelain"])
    if success:
        status.uncommitted_files = len([line for line in output.split("\n") if line.strip()])

    # 푸시되지 않은 커밋
    success, output = run_command(["git", "rev-list", "--count", "@{u}..HEAD"])
    if success and output.isdigit():
        status.unpushed_commits = int(output)

    # ahead/behind
    success, output = run_command(["git", "rev-list", "--left-right", "--count", "@{u}...HEAD"])
    if success:
        parts = output.split()
        if len(parts) == 2:
            status.behind = int(parts[0])
            status.ahead = int(parts[1])

    # 충돌 확인
    success, output = run_command(["git", "diff", "--name-only", "--diff-filter=U"])
    if success:
        status.has_conflicts = bool(output.strip())

    return status


def analyze_code() -> CodeStatus:
    """코드 상태 분석 (빠른 검사)"""
    status = CodeStatus()

    # 린트 검사 (ruff)
    success, output = run_command(["ruff", "check", ".", "--statistics"])
    if success:
        status.lint_errors = 0
    else:
        # 에러 개수 추출 시도
        lines = output.split("\n")
        status.lint_errors = len([line for line in lines if line.strip() and not line.startswith("Found")])

    return status


def analyze_project() -> ProjectStatus:
    """프로젝트 상태 분석"""
    status = ProjectStatus()

    # GitHub 이슈
    success, output = run_command(["gh", "issue", "list", "--json", "number,title,labels", "-L", "10"])
    if success:
        try:
            status.open_issues = json.loads(output)
        except json.JSONDecodeError:
            pass

    # GitHub PR
    success, output = run_command(["gh", "pr", "list", "--json", "number,title,state", "-L", "5"])
    if success:
        try:
            status.open_prs = json.loads(output)
        except json.JSONDecodeError:
            pass

    # TodoWrite 상태 (파일에서 읽기)
    todo_file = PROJECT_DIR / ".claude" / "todos.json"
    if todo_file.exists():
        try:
            todos = json.loads(todo_file.read_text(encoding="utf-8"))
            status.pending_todos = [t for t in todos if t.get("status") == "pending"]
        except Exception:
            pass

    return status


def analyze_session() -> SessionStatus:
    """세션 상태 분석"""
    status = SessionStatus()

    # 세션 상태 파일에서 읽기
    session_file = PROJECT_DIR / ".claude" / "session_state.json"
    if session_file.exists():
        try:
            data = json.loads(session_file.read_text(encoding="utf-8"))
            status.last_action = data.get("last_action", "")
            status.in_progress_task = data.get("in_progress_task", "")
            status.last_user_request = data.get("last_user_request", "")
        except Exception:
            pass

    return status


def analyze_all() -> AnalysisResult:
    """전체 상태 분석"""
    return AnalysisResult(
        git=analyze_git(),
        code=analyze_code(),
        project=analyze_project(),
        session=analyze_session()
    )


# ============================================
# Tier 2: 자율 발견 함수들
# ============================================

def discover_lint_issues() -> tuple[int, str]:
    """린트 이슈 탐색 (우선순위 6)"""
    # ruff로 린트 이슈 확인
    success, output = run_command(["ruff", "check", ".", "--output-format=json"])
    if not success and output:
        try:
            issues = json.loads(output)
            if issues:
                return len(issues), issues[0].get("filename", "")
        except (json.JSONDecodeError, TypeError):
            pass
    return 0, ""


def discover_todo_comments() -> list[dict]:
    """TODO/FIXME 코멘트 탐색 (우선순위 8)"""
    todos = []
    # git grep으로 TODO/FIXME 찾기
    success, output = run_command(
        ["git", "grep", "-n", "-E", "(TODO|FIXME|XXX|HACK):"]
    )
    if success and output:
        for line in output.split("\n")[:10]:  # 상위 10개만
            parts = line.split(":", 2)
            if len(parts) >= 3:
                todos.append({
                    "file": parts[0],
                    "line": parts[1],
                    "content": parts[2].strip()[:50]
                })
    return todos


def discover_dependency_updates() -> list[dict]:
    """의존성 업데이트 확인 (우선순위 10)"""
    updates = []

    # Python: pip list --outdated
    success, output = run_command(["pip", "list", "--outdated", "--format=json"])
    if success and output:
        try:
            outdated = json.loads(output)
            for pkg in outdated[:5]:  # 상위 5개만
                updates.append({
                    "name": pkg.get("name", ""),
                    "current": pkg.get("version", ""),
                    "latest": pkg.get("latest_version", "")
                })
        except (json.JSONDecodeError, TypeError):
            pass

    return updates


def discover_security_vulns() -> list[dict]:
    """보안 취약점 확인 (우선순위 11)"""
    vulns = []

    # npm audit (Node 프로젝트)
    package_json = PROJECT_DIR / "package.json"
    if package_json.exists():
        success, output = run_command(["npm", "audit", "--json"])
        if not success and output:
            try:
                audit = json.loads(output)
                vuln_count = audit.get("metadata", {}).get("vulnerabilities", {})
                total = sum(vuln_count.values()) if isinstance(vuln_count, dict) else 0
                if total > 0:
                    vulns.append({"type": "npm", "count": total})
            except (json.JSONDecodeError, TypeError):
                pass

    return vulns


def discover_next_task() -> Optional["NextAction"]:
    """
    Tier 2: 자율 발견 - 스스로 개선점 탐색
    Ralph Wiggum 철학: "할 일 없음 → 스스로 발견"
    """

    # 6. 코드 품질 (린트 이슈)
    lint_count, lint_file = discover_lint_issues()
    if lint_count > 0:
        return NextAction(
            priority=6,
            action_type="discover",
            description=f"린트 이슈 수정 ({lint_count}개)",
            command="/check --fix",
            reason=f"자율 발견: {lint_file}에서 린트 이슈 발견"
        )

    # 8. TODO/FIXME 코멘트
    todos = discover_todo_comments()
    if todos:
        first = todos[0]
        return NextAction(
            priority=8,
            action_type="discover",
            description=f"TODO 해결 ({len(todos)}개)",
            command=f"/issue create \"TODO: {first['content']}\"",
            reason=f"자율 발견: {first['file']}:{first['line']}에 TODO"
        )

    # 10. 의존성 업데이트
    outdated = discover_dependency_updates()
    if outdated:
        pkg = outdated[0]
        return NextAction(
            priority=10,
            action_type="discover",
            description=f"의존성 업데이트 ({len(outdated)}개)",
            command=f"/work \"의존성 업데이트: {pkg['name']}\"",
            reason=f"자율 발견: {pkg['name']} {pkg['current']} → {pkg['latest']}"
        )

    # 11. 보안 취약점
    vulns = discover_security_vulns()
    if vulns:
        return NextAction(
            priority=11,
            action_type="discover",
            description=f"보안 취약점 수정 ({vulns[0]['count']}개)",
            command="/check --security",
            reason="자율 발견: 보안 취약점 발견"
        )

    # Tier 2에서도 발견 못함
    return None


@dataclass
class NextAction:
    """다음 작업"""
    priority: int  # 1=긴급, 2=진행중, 3=대기, 4=계획, 5=개선, 6-11=자율발견, 99=대기
    action_type: str  # fix, commit, push, pr, issue, todo, refactor, discover, wait, none
    description: str
    command: str  # 실행할 명령
    reason: str  # 왜 이 작업인지


def decide_next_action(analysis: AnalysisResult) -> NextAction:
    """다음 작업 판단"""

    git = analysis.git
    code = analysis.code
    project = analysis.project
    _ = analysis.session  # Reserved for future use

    # 1. 긴급: 충돌 해결
    if git.has_conflicts:
        return NextAction(
            priority=1,
            action_type="fix",
            description="Git 충돌 해결",
            command="/debug conflict",
            reason="충돌이 발생해서 먼저 해결해야 합니다"
        )

    # 2. 긴급: 테스트 실패
    if code.tests_passing is False or code.test_failures > 0:
        return NextAction(
            priority=1,
            action_type="fix",
            description="테스트 수정",
            command="/debug test",
            reason=f"테스트 {code.test_failures}개 실패 중"
        )

    # 3. 긴급: 린트 에러
    if code.lint_errors > 5:  # 5개 이상이면 긴급
        return NextAction(
            priority=1,
            action_type="fix",
            description="린트 에러 수정",
            command="/check --fix",
            reason=f"린트 에러 {code.lint_errors}개 발견"
        )

    # 4. 진행중: 커밋 필요
    if git.uncommitted_files > 0:
        return NextAction(
            priority=2,
            action_type="commit",
            description="변경사항 커밋",
            command="/commit",
            reason=f"{git.uncommitted_files}개 파일이 커밋되지 않음"
        )

    # 5. 진행중: 푸시 필요
    if git.unpushed_commits > 0:
        return NextAction(
            priority=2,
            action_type="push",
            description="커밋 푸시",
            command="git push",
            reason=f"{git.unpushed_commits}개 커밋이 푸시되지 않음"
        )

    # 6. 진행중: PR 생성 (기능 브랜치에서)
    if not git.is_main and git.ahead > 0:
        return NextAction(
            priority=2,
            action_type="pr",
            description="PR 생성",
            command="/create pr",
            reason=f"브랜치 {git.branch}에 {git.ahead}개 커밋 있음"
        )

    # 7. 대기중: PR 리뷰/머지
    if project.open_prs:
        pr = project.open_prs[0]
        return NextAction(
            priority=3,
            action_type="pr",
            description=f"PR #{pr['number']} 처리",
            command=f"/pr review #{pr['number']}",
            reason=f"대기 중인 PR: {pr['title']}"
        )

    # 8. 대기중: 이슈 해결
    if project.open_issues:
        # 우선순위 높은 이슈 찾기
        issue = project.open_issues[0]
        for i in project.open_issues:
            labels = [label.get("name", "") for label in i.get("labels", [])]
            if "priority-high" in labels or "urgent" in labels:
                issue = i
                break

        return NextAction(
            priority=3,
            action_type="issue",
            description=f"이슈 #{issue['number']} 해결",
            command=f"/issue fix {issue['number']}",
            reason=f"열린 이슈: {issue['title']}"
        )

    # 9. 계획됨: Todo 진행
    if project.pending_todos:
        todo = project.pending_todos[0]
        return NextAction(
            priority=4,
            action_type="todo",
            description=f"Todo 진행: {todo.get('content', '')}",
            command=f"/work \"{todo.get('content', '')}\"",
            reason="미완료 Todo 항목 있음"
        )

    # 10. 개선: 린트 경고 수정
    if code.lint_errors > 0:
        return NextAction(
            priority=5,
            action_type="fix",
            description="린트 경고 수정",
            command="/check --fix",
            reason=f"린트 경고 {code.lint_errors}개"
        )

    # ============================================
    # Tier 2: 자율 발견 (Tier 1 작업 없을 때)
    # Ralph Wiggum: "할 일 없음 → 스스로 발견"
    # ============================================
    discovered = discover_next_task()
    if discovered:
        return discovered

    # 모든 Tier에서 할 일 없음 -> 대기 상태 (재탐색 예정)
    return NextAction(
        priority=99,
        action_type="wait",
        description="대기 중 (재탐색 예정)",
        command="",
        reason="Tier 1, 2 모두 완료. 잠시 후 재탐색합니다."
    )


def format_analysis(analysis: AnalysisResult) -> str:
    """분석 결과 포맷팅"""
    lines = []
    lines.append("━" * 45)
    lines.append("🔍 상태 분석 결과")
    lines.append("━" * 45)

    # Git
    git = analysis.git
    lines.append(f"Git: {git.branch} 브랜치")
    if git.uncommitted_files:
        lines.append(f"   - {git.uncommitted_files}개 파일 수정됨")
    if git.unpushed_commits:
        lines.append(f"   - {git.unpushed_commits}개 커밋 미푸시")
    if git.has_conflicts:
        lines.append("   - ⚠️ 충돌 발생")

    # Code
    code = analysis.code
    if code.lint_errors:
        lines.append(f"린트: {code.lint_errors}개 에러")
    if code.test_failures:
        lines.append(f"테스트: {code.test_failures}개 실패")

    # Project
    project = analysis.project
    if project.open_issues:
        lines.append(f"이슈: {len(project.open_issues)}개 open")
    if project.open_prs:
        lines.append(f"PR: {len(project.open_prs)}개 대기")
    if project.pending_todos:
        lines.append(f"Todo: {len(project.pending_todos)}개 미완료")

    return "\n".join(lines)


def format_decision(action: NextAction) -> str:
    """판단 결과 포맷팅"""
    priority_map = {
        1: "🚨 긴급", 2: "⚡ 진행중", 3: "📋 대기", 4: "📝 계획", 5: "✨ 개선",
        # Tier 2: 자율 발견
        6: "🔍 자율발견:품질", 7: "🔍 자율발견:커버리지", 8: "🔍 자율발견:TODO",
        9: "🔍 자율발견:문서화", 10: "🔍 자율발견:의존성", 11: "🔍 자율발견:보안",
        99: "⏸️ 대기중"
    }
    lines = []
    lines.append("")
    lines.append(f"💭 판단: {action.description}")
    lines.append(f"   우선순위: {priority_map.get(action.priority, '?')}")
    lines.append(f"   이유: {action.reason}")
    if action.command:
        lines.append(f"   실행: {action.command}")
    return "\n".join(lines)


def main():
    """CLI 진입점"""
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode == "analyze":
        # 분석만
        analysis = analyze_all()
        print(format_analysis(analysis))

    elif mode == "decide":
        # 판단만
        analysis = analyze_all()
        action = decide_next_action(analysis)
        print(format_decision(action))

    elif mode == "json":
        # JSON 출력
        analysis = analyze_all()
        action = decide_next_action(analysis)
        result = {
            "analysis": {
                "git": asdict(analysis.git),
                "code": asdict(analysis.code),
                "project": asdict(analysis.project),
                "session": asdict(analysis.session),
            },
            "next_action": asdict(action)
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:  # full
        analysis = analyze_all()
        action = decide_next_action(analysis)
        print(format_analysis(analysis))
        print(format_decision(action))


if __name__ == "__main__":
    main()
