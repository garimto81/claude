"""
Auto Discovery - 자율 발견 엔진

2계층 우선순위 체계에 따라 다음 작업을 발견합니다.
- Tier 1: 명시적 작업 (긴급, 진행중, 대기중, PRD, 계획됨)
- Tier 2: 자율 발견 (코드 품질, 테스트, 문서화, 리팩토링 등)
"""

import json
import subprocess
import re
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Optional


def run_command(cmd: list, cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess:
    """UTF-8 인코딩으로 subprocess 실행"""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
        encoding="utf-8",
        errors="replace"
    )


class Priority(IntEnum):
    """2계층 우선순위"""
    # Tier 1: 명시적 작업
    URGENT = 1          # 빌드 깨짐, 테스트 실패
    IN_PROGRESS = 2     # 방금 하던 작업 완료
    WAITING = 3         # PR 리뷰, 이슈 해결
    PRD_NEEDED = 4      # 새 기능 → PRD 작성/검토
    PLANNED = 5         # Todo, PRD 체크박스

    # Tier 2: 자율 발견
    CODE_QUALITY = 6    # 린트 경고, 타입 오류
    TEST_COVERAGE = 7   # 커버리지 미달
    DOCUMENTATION = 8   # 문서화 누락
    REFACTORING = 9     # 중복 코드, 복잡도
    DEPENDENCIES = 10   # 보안 취약점, 버전
    PERFORMANCE = 11    # 느린 패턴, TODO 주석
    ACCESSIBILITY = 12  # a11y 개선


@dataclass
class DiscoveredTask:
    """발견된 작업"""
    priority: Priority
    category: str
    title: str
    description: str
    command: str  # 실행할 명령 (예: "/issue fix #123")
    details: dict = None

    def to_dict(self) -> dict:
        return {
            "priority": self.priority.value,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "command": self.command,
            "details": self.details or {}
        }


class AutoDiscovery:
    """자율 발견 엔진"""

    def __init__(self, project_root: str = "D:/AI/claude01"):
        self.project_root = Path(project_root)

    def discover_next_task(self) -> Optional[DiscoveredTask]:
        """
        2계층 우선순위에 따라 다음 작업 발견

        Returns:
            DiscoveredTask or None (모든 검사 통과 시)
        """
        # Tier 1: 명시적 작업
        task = self._check_tier1()
        if task:
            return task

        # Tier 2: 자율 발견
        task = self._check_tier2()
        if task:
            return task

        return None

    # === Tier 1: 명시적 작업 ===

    def _check_tier1(self) -> Optional[DiscoveredTask]:
        """Tier 1 검사"""
        # 1. 긴급: 테스트 실패 확인
        task = self._check_test_failures()
        if task:
            return task

        # 2. 진행중: 커밋 안 된 변경사항
        task = self._check_uncommitted_changes()
        if task:
            return task

        # 3. 대기중: PR CI 실패, 열린 이슈
        task = self._check_open_issues()
        if task:
            return task

        # 4. PRD 필요: 진행 중인 PRD 확인
        task = self._check_prd_status()
        if task:
            return task

        # 5. 계획됨: Todo 미완료 항목
        task = self._check_planned_todos()
        if task:
            return task

        return None

    def _check_test_failures(self) -> Optional[DiscoveredTask]:
        """테스트 실패 확인 (빠른 검사)"""
        try:
            # .pytest_cache에서 마지막 실패 확인
            lastfailed_path = self.project_root / ".pytest_cache" / "v" / "cache" / "lastfailed"
            if lastfailed_path.exists():
                with open(lastfailed_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content and content != "{}":
                        return DiscoveredTask(
                            priority=Priority.URGENT,
                            category="테스트 실패",
                            title="실패한 테스트 수정",
                            description="마지막 실행에서 실패한 테스트가 있습니다",
                            command="pytest --lf -v",  # 실패한 테스트만 재실행
                            details={"lastfailed": content}
                        )
        except (FileNotFoundError, IOError):
            pass

        return None

    def _check_uncommitted_changes(self) -> Optional[DiscoveredTask]:
        """커밋 안 된 변경사항 확인"""
        try:
            result = run_command(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                timeout=10
            )

            if result.returncode == 0 and result.stdout and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                modified_count = len([l for l in lines if l.startswith(" M") or l.startswith("M ")])
                added_count = len([l for l in lines if l.startswith("??")])

                if modified_count > 0:
                    return DiscoveredTask(
                        priority=Priority.IN_PROGRESS,
                        category="커밋 필요",
                        title="변경사항 커밋",
                        description=f"수정된 파일 {modified_count}개, 새 파일 {added_count}개",
                        command="/commit",
                        details={"modified": modified_count, "added": added_count}
                    )
        except subprocess.TimeoutExpired:
            pass

        return None

    def _check_open_issues(self) -> Optional[DiscoveredTask]:
        """열린 이슈 확인"""
        try:
            result = run_command(
                ["gh", "issue", "list", "--state", "open", "--limit", "5", "--json", "number,title,labels"],
                cwd=self.project_root,
                timeout=30
            )

            if result.returncode == 0 and result.stdout and result.stdout.strip():
                issues = json.loads(result.stdout)
                if issues:
                    # 버그 라벨 우선
                    bug_issues = [i for i in issues if any(l.get("name") == "bug" for l in i.get("labels", []))]
                    target = bug_issues[0] if bug_issues else issues[0]

                    return DiscoveredTask(
                        priority=Priority.WAITING,
                        category="이슈 해결",
                        title=f"#{target['number']}: {target['title']}",
                        description=f"열린 이슈 {len(issues)}개 중 우선 처리",
                        command=f"/issue fix #{target['number']}",
                        details={"issue": target}
                    )
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass

        return None

    def _check_prd_status(self) -> Optional[DiscoveredTask]:
        """PRD 상태 확인"""
        prd_dir = self.project_root / "tasks" / "prds"
        if not prd_dir.exists():
            return None

        # 진행 중인 PRD 찾기 (체크박스 미완료)
        for prd_file in prd_dir.glob("*-prd-*.md"):
            try:
                content = prd_file.read_text(encoding="utf-8")
                unchecked = content.count("- [ ]")
                checked = content.count("- [x]") + content.count("- [X]")

                if unchecked > 0 and checked > 0:  # 진행 중인 PRD
                    return DiscoveredTask(
                        priority=Priority.PRD_NEEDED,
                        category="PRD 진행",
                        title=f"PRD 체크리스트 완료: {prd_file.name}",
                        description=f"완료 {checked}/{checked + unchecked} 항목",
                        command=f"/work 'PRD {prd_file.name} 체크리스트 항목 진행'",
                        details={"prd": prd_file.name, "checked": checked, "unchecked": unchecked}
                    )
            except Exception:
                pass

        return None

    def _check_planned_todos(self) -> Optional[DiscoveredTask]:
        """계획된 Todo 확인 (TODO.md, CHECKLIST.md)"""
        todo_files = [
            self.project_root / "TODO.md",
            self.project_root / "docs" / "CHECKLIST.md"
        ]

        for todo_file in todo_files:
            if todo_file.exists():
                try:
                    content = todo_file.read_text(encoding="utf-8")
                    unchecked_matches = re.findall(r"- \[ \] (.+)", content)

                    if unchecked_matches:
                        first_todo = unchecked_matches[0].strip()
                        return DiscoveredTask(
                            priority=Priority.PLANNED,
                            category="계획된 작업",
                            title=first_todo[:50] + ("..." if len(first_todo) > 50 else ""),
                            description=f"{todo_file.name}의 미완료 항목 ({len(unchecked_matches)}개)",
                            command=f"/work '{first_todo}'",
                            details={"file": todo_file.name, "todos": unchecked_matches[:5]}
                        )
                except Exception:
                    pass

        return None

    # === Tier 2: 자율 발견 ===

    def _check_tier2(self) -> Optional[DiscoveredTask]:
        """Tier 2 자율 발견"""
        # 6. 코드 품질
        task = self._check_lint_issues()
        if task:
            return task

        # 7. 테스트 커버리지
        task = self._check_test_coverage()
        if task:
            return task

        # 8. 문서화
        task = self._check_documentation()
        if task:
            return task

        # 9. 리팩토링 (TODO 주석)
        task = self._check_todo_comments()
        if task:
            return task

        # 10. 의존성
        task = self._check_dependencies()
        if task:
            return task

        return None

    def _check_lint_issues(self) -> Optional[DiscoveredTask]:
        """린트 이슈 확인 (ruff)"""
        try:
            result = run_command(
                ["ruff", "check", "src/", "--output-format", "json"],
                cwd=self.project_root,
                timeout=60
            )

            if result.stdout and result.stdout.strip():
                issues = json.loads(result.stdout)
                if issues:
                    # 파일별 그룹핑
                    files = {}
                    for issue in issues:
                        filename = issue.get("filename", "unknown")
                        files[filename] = files.get(filename, 0) + 1

                    worst_file = max(files.items(), key=lambda x: x[1])

                    return DiscoveredTask(
                        priority=Priority.CODE_QUALITY,
                        category="코드 품질",
                        title=f"린트 경고 수정 ({len(issues)}개)",
                        description=f"가장 많은 이슈: {worst_file[0]} ({worst_file[1]}개)",
                        command="ruff check src/ --fix",
                        details={"total": len(issues), "by_file": dict(list(files.items())[:5])}
                    )
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass

        return None

    def _check_test_coverage(self) -> Optional[DiscoveredTask]:
        """테스트 커버리지 확인"""
        coverage_file = self.project_root / ".coverage"
        coverage_json = self.project_root / "coverage.json"

        # 기존 커버리지 데이터가 있으면 분석
        if coverage_json.exists():
            try:
                with open(coverage_json, "r") as f:
                    data = json.load(f)

                total_coverage = data.get("totals", {}).get("percent_covered", 100)

                if total_coverage < 80:
                    # 커버리지 낮은 파일 찾기
                    files = data.get("files", {})
                    low_coverage = [
                        (f, info.get("summary", {}).get("percent_covered", 0))
                        for f, info in files.items()
                        if info.get("summary", {}).get("percent_covered", 100) < 60
                    ]
                    low_coverage.sort(key=lambda x: x[1])

                    if low_coverage:
                        worst = low_coverage[0]
                        return DiscoveredTask(
                            priority=Priority.TEST_COVERAGE,
                            category="테스트 커버리지",
                            title=f"커버리지 개선 ({total_coverage:.1f}%)",
                            description=f"가장 낮은 파일: {worst[0]} ({worst[1]:.1f}%)",
                            command=f"/work '테스트 추가: {worst[0]}'",
                            details={"total": total_coverage, "low_files": low_coverage[:5]}
                        )
            except (json.JSONDecodeError, KeyError):
                pass

        return None

    def _check_documentation(self) -> Optional[DiscoveredTask]:
        """문서화 누락 확인"""
        # src/ 폴더의 Python 파일 중 docstring 없는 것 찾기
        undocumented = []

        src_dir = self.project_root / "src"
        if not src_dir.exists():
            return None

        for py_file in src_dir.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                # 클래스나 함수 정의 후 docstring 없는 경우 탐지
                # 간단한 휴리스틱: 파일에 """가 없으면 문서화 부족
                if 'def ' in content or 'class ' in content:
                    if '"""' not in content and "'''" not in content:
                        undocumented.append(str(py_file.relative_to(self.project_root)))
            except Exception:
                pass

        if undocumented:
            return DiscoveredTask(
                priority=Priority.DOCUMENTATION,
                category="문서화",
                title=f"Docstring 추가 ({len(undocumented)}개 파일)",
                description=f"문서화 필요: {undocumented[0]}",
                command=f"/work 'Docstring 추가: {undocumented[0]}'",
                details={"files": undocumented[:10]}
            )

        return None

    def _check_todo_comments(self) -> Optional[DiscoveredTask]:
        """TODO 주석 확인"""
        try:
            result = run_command(
                ["git", "grep", "-n", "-E", "(TODO|FIXME|HACK|XXX):", "--", "*.py", "*.ts", "*.tsx"],
                cwd=self.project_root,
                timeout=30
            )

            if result.returncode == 0 and result.stdout and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                todos = []

                for line in lines[:20]:  # 최대 20개
                    match = re.match(r"([^:]+):(\d+):(.+)", line)
                    if match:
                        todos.append({
                            "file": match.group(1),
                            "line": match.group(2),
                            "content": match.group(3).strip()
                        })

                if todos:
                    first = todos[0]
                    return DiscoveredTask(
                        priority=Priority.REFACTORING,
                        category="리팩토링",
                        title=f"TODO 주석 해결 ({len(todos)}개)",
                        description=f"{first['file']}:{first['line']} - {first['content'][:40]}...",
                        command=f"/work 'TODO 해결: {first['file']}:{first['line']}'",
                        details={"todos": todos}
                    )
        except subprocess.TimeoutExpired:
            pass

        return None

    def _check_dependencies(self) -> Optional[DiscoveredTask]:
        """의존성 취약점 확인"""
        # pip-audit 확인
        try:
            result = run_command(
                ["pip-audit", "--format", "json"],
                cwd=self.project_root,
                timeout=120
            )

            if result.returncode != 0 and result.stdout and result.stdout.strip():
                vulns = json.loads(result.stdout)
                if vulns:
                    return DiscoveredTask(
                        priority=Priority.DEPENDENCIES,
                        category="의존성",
                        title=f"보안 취약점 ({len(vulns)}개)",
                        description="pip-audit에서 취약점 발견",
                        command="pip-audit --fix",
                        details={"vulnerabilities": vulns[:5]}
                    )
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass

        return None

    def get_status_report(self) -> dict:
        """현재 상태 리포트"""
        return {
            "tier1": {
                "test_failures": self._check_test_failures() is not None,
                "uncommitted": self._check_uncommitted_changes() is not None,
                "open_issues": self._check_open_issues() is not None,
                "prd_pending": self._check_prd_status() is not None,
                "planned_todos": self._check_planned_todos() is not None
            },
            "tier2": {
                "lint_issues": self._check_lint_issues() is not None,
                "low_coverage": self._check_test_coverage() is not None,
                "missing_docs": self._check_documentation() is not None,
                "todo_comments": self._check_todo_comments() is not None,
                "vulnerabilities": self._check_dependencies() is not None
            }
        }


if __name__ == "__main__":
    discovery = AutoDiscovery()

    print("=== 자율 발견 테스트 ===\n")

    task = discovery.discover_next_task()
    if task:
        print(f"[P{task.priority.value}] {task.category}")
        print(f"제목: {task.title}")
        print(f"설명: {task.description}")
        print(f"명령: {task.command}")
    else:
        print("✅ 모든 검사 통과 - 할 일 없음")

    print("\n=== 상태 리포트 ===")
    import pprint
    pprint.pprint(discovery.get_status_report())
