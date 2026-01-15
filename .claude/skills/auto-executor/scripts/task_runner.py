#!/usr/bin/env python3
"""
task_runner.py: Task tool 강제 호출 로직

Claude CLI를 호출할 때 Task tool 사용을 강제합니다.
"""

import subprocess
import shutil
import sys
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any


class TaskRunner:
    """Task tool을 강제로 사용하여 서브에이전트 실행"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.claude_path = self._find_claude()

    def _find_claude(self) -> str:
        """Claude CLI 경로 찾기"""
        claude = shutil.which("claude")
        if claude:
            return claude
        # Windows 기본 경로
        default_paths = [
            r"C:\Users\AidenKim\AppData\Local\npm\claude.cmd",
            r"C:\Program Files\nodejs\claude.cmd",
        ]
        for path in default_paths:
            if Path(path).exists():
                return path
        return "claude"  # fallback

    def discover_next_task(self, direction: Optional[str] = None) -> Optional[str]:
        """5계층 우선순위로 다음 작업 발견"""

        # Tier 2: 긴급 (테스트/린트/빌드 실패)
        task = self._check_urgent_tasks()
        if task:
            return task

        # Tier 3: 작업 처리 (변경사항/이슈/PR)
        task = self._check_work_tasks()
        if task:
            return task

        # Tier 1: 명시적 지시 (direction이 있으면)
        if direction:
            return f"사용자 지시: {direction}"

        return None

    def discover_autonomous_task(self) -> Optional[str]:
        """Tier 4: 자율 개선 작업 발견"""

        # 테스트 커버리지 확인
        try:
            result = subprocess.run(
                ["pytest", "--co", "-q"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30
            )
            if "no tests" in result.stdout.lower():
                return "테스트가 없는 모듈에 테스트 추가"
        except Exception:
            pass

        # 문서 확인
        readme = self.project_root / "README.md"
        if not readme.exists():
            return "README.md 문서 작성"

        # TODO 주석 확인
        try:
            result = subprocess.run(
                ["git", "grep", "-n", "TODO:", "--", "*.py", "*.ts", "*.js"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30
            )
            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                return f"TODO 주석 해결 ({len(lines)}개 발견)"
        except Exception:
            pass

        return None

    def _check_urgent_tasks(self) -> Optional[str]:
        """Tier 2: 긴급 작업 확인"""

        # 린트 오류 확인
        try:
            result = subprocess.run(
                ["ruff", "check", ".", "--statistics"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=60
            )
            if result.returncode != 0:
                # 오류 수 파싱
                match = re.search(r"(\d+)\s+error", result.stdout + result.stderr)
                if match:
                    count = int(match.group(1))
                    if count >= 5:
                        return f"린트 오류 {count}개 수정"
        except Exception:
            pass

        # TypeScript 빌드 오류
        tsconfig = self.project_root / "tsconfig.json"
        if tsconfig.exists():
            try:
                result = subprocess.run(
                    ["npx", "tsc", "--noEmit"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=120
                )
                if result.returncode != 0:
                    errors = result.stdout.count("error TS")
                    if errors > 0:
                        return f"TypeScript 빌드 오류 {errors}개 수정"
            except Exception:
                pass

        return None

    def _check_work_tasks(self) -> Optional[str]:
        """Tier 3: 작업 처리 확인"""

        # 변경사항 확인
        try:
            result = subprocess.run(
                ["git", "diff", "--stat"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30
            )
            if result.stdout.strip():
                # 변경 줄 수 파싱
                match = re.search(r"(\d+)\s+insertion|(\d+)\s+deletion", result.stdout)
                if match:
                    insertions = int(match.group(1) or 0)
                    deletions = int(match.group(2) or 0)
                    total = insertions + deletions
                    if total >= 100:
                        return f"변경사항 {total}줄 커밋"
        except Exception:
            pass

        # GitHub 이슈 확인
        try:
            result = subprocess.run(
                ["gh", "issue", "list", "--state", "open", "--limit", "1", "--json", "number,title"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                issues = json.loads(result.stdout)
                if issues:
                    issue = issues[0]
                    return f"GitHub 이슈 #{issue['number']} 해결: {issue['title']}"
        except Exception:
            pass

        return None

    def execute_with_task_tool(self, task: str, agent: str) -> Dict[str, Any]:
        """
        Task tool을 강제로 사용하여 서브에이전트 실행

        핵심: Claude CLI 호출 시 Task tool 사용을 명시적으로 강제
        """

        # Task tool 강제 프롬프트
        prompt = f'''**중요: 반드시 Task tool을 사용하세요. 직접 처리는 금지입니다.**

다음 작업을 Task tool로 서브에이전트에 위임하세요.

## 작업 정보
- 작업: {task}
- 에이전트: {agent}

## 필수 실행 방식

아래 형식으로 Task tool을 호출하세요:

Task(
    subagent_type="{agent}",
    prompt="""
## 작업 지시
{task}

## 프로젝트 경로
{self.project_root}

## 중요 규칙
1. 작업을 완료하고 결과만 반환하세요
2. 중간 질문 없이 최선의 판단으로 진행하세요

## 결과 형식
### 요약
- 한 줄 요약

### 수행 작업
- 작업 목록

### 변경 파일
| 파일 | 변경 |
|------|------|
    """,
    description="{task[:50]}"
)

**경고: Task tool을 사용하지 않고 직접 처리하면 실패로 간주됩니다.**
**반드시 위의 Task() 호출을 실행하세요.**
'''

        try:
            # Claude CLI 실행
            result = subprocess.run(
                [self.claude_path, "-p", prompt, "--dangerously-skip-permissions"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600,  # 10분 타임아웃
                encoding="utf-8",
                errors="replace"
            )

            output = result.stdout + result.stderr

            # 결과 파싱
            return {
                "success": result.returncode == 0,
                "summary": self._extract_summary(output),
                "output": output[:2000],  # 최대 2000자
                "task": task,
                "agent": agent
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "summary": "타임아웃 (10분 초과)",
                "output": "",
                "task": task,
                "agent": agent
            }
        except Exception as e:
            return {
                "success": False,
                "summary": f"실행 오류: {str(e)}",
                "output": "",
                "task": task,
                "agent": agent
            }

    def _extract_summary(self, output: str) -> str:
        """출력에서 요약 추출"""
        # "### 요약" 섹션 찾기
        match = re.search(r"###\s*요약\s*\n([^\n#]+)", output)
        if match:
            return match.group(1).strip()

        # "요약:" 패턴 찾기
        match = re.search(r"요약[:\s]+([^\n]+)", output)
        if match:
            return match.group(1).strip()

        # 첫 번째 의미있는 줄 반환
        for line in output.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and len(line) > 10:
                return line[:100]

        return "결과 요약 없음"
