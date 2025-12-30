# tests/test_utils.py
"""
Tests for src/agents/utils.py - 병렬 워크플로우 유틸리티 함수
"""

import asyncio
import time
import pytest

from src.agents.utils import (
    ExecutionResult,
    timer,
    run_with_timeout,
    run_parallel_with_semaphore,
    format_result_report,
    parse_subtasks_from_text,
)


class TestExecutionResult:
    """ExecutionResult dataclass 테스트"""

    def test_create_success_result(self):
        """성공 결과 생성"""
        result = ExecutionResult(
            success=True,
            output="test output",
            duration_seconds=1.5,
        )
        assert result.success is True
        assert result.output == "test output"
        assert result.duration_seconds == 1.5
        assert result.error is None

    def test_create_failure_result(self):
        """실패 결과 생성"""
        result = ExecutionResult(
            success=False,
            output=None,
            duration_seconds=2.0,
            error="Something went wrong",
        )
        assert result.success is False
        assert result.output is None
        assert result.duration_seconds == 2.0
        assert result.error == "Something went wrong"


class TestTimer:
    """timer 데코레이터 테스트"""

    def test_timer_measures_time(self, capsys):
        """타이머가 실행 시간을 측정"""
        @timer
        def slow_function():
            time.sleep(0.01)
            return "done"

        result = slow_function()
        captured = capsys.readouterr()

        assert result == "done"
        assert "[Timer]" in captured.out
        assert "slow_function" in captured.out

    def test_timer_preserves_return_value(self):
        """타이머가 반환값을 보존"""
        @timer
        def add(a, b):
            return a + b

        result = add(1, 2)
        assert result == 3

    def test_timer_preserves_function_name(self):
        """타이머가 함수 이름을 보존"""
        @timer
        def my_function():
            pass

        assert my_function.__name__ == "my_function"


class TestRunWithTimeout:
    """run_with_timeout 함수 테스트"""

    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """성공적인 실행"""
        async def fast_task():
            await asyncio.sleep(0.01)
            return "completed"

        result = await run_with_timeout(fast_task(), timeout_seconds=5)

        assert result.success is True
        assert result.output == "completed"
        assert result.error is None
        assert result.duration_seconds < 5

    @pytest.mark.asyncio
    async def test_timeout_execution(self):
        """타임아웃 발생"""
        async def slow_task():
            await asyncio.sleep(10)
            return "completed"

        result = await run_with_timeout(
            slow_task(), timeout_seconds=0.1, fallback_value="timeout"
        )

        assert result.success is False
        assert result.output == "timeout"
        assert "Timeout" in result.error

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """예외 처리"""
        async def failing_task():
            raise ValueError("Test error")

        result = await run_with_timeout(
            failing_task(), timeout_seconds=5, fallback_value="fallback"
        )

        assert result.success is False
        assert result.output == "fallback"
        assert "Test error" in result.error

    @pytest.mark.asyncio
    async def test_default_fallback_value(self):
        """기본 fallback 값"""
        async def failing_task():
            raise ValueError("Test error")

        result = await run_with_timeout(failing_task(), timeout_seconds=5)

        assert result.success is False
        assert result.output is None


class TestRunParallelWithSemaphore:
    """run_parallel_with_semaphore 함수 테스트"""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """병렬 실행"""
        results = []

        async def task(n):
            await asyncio.sleep(0.01)
            results.append(n)
            return n * 2

        tasks = [task(i) for i in range(5)]
        outputs = await run_parallel_with_semaphore(tasks, max_concurrent=5)

        assert len(outputs) == 5
        assert sorted(outputs) == [0, 2, 4, 6, 8]

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """세마포어가 동시 실행 수를 제한"""
        concurrent_count = 0
        max_concurrent_seen = 0

        async def task():
            nonlocal concurrent_count, max_concurrent_seen
            concurrent_count += 1
            max_concurrent_seen = max(max_concurrent_seen, concurrent_count)
            await asyncio.sleep(0.05)
            concurrent_count -= 1
            return True

        tasks = [task() for _ in range(10)]
        await run_parallel_with_semaphore(tasks, max_concurrent=3)

        assert max_concurrent_seen <= 3

    @pytest.mark.asyncio
    async def test_empty_tasks(self):
        """빈 태스크 리스트"""
        results = await run_parallel_with_semaphore([], max_concurrent=5)
        assert results == []


class TestFormatResultReport:
    """format_result_report 함수 테스트"""

    def test_all_success(self):
        """모든 태스크 성공"""
        results = [
            {"success": True, "agent_id": 1, "subtask": "Task 1", "output": "Output 1"},
            {"success": True, "agent_id": 2, "subtask": "Task 2", "output": "Output 2"},
        ]

        report = format_result_report(results)

        assert "성공: 2" in report
        assert "실패: 0" in report
        assert "Task 1" in report
        assert "Output 1" in report

    def test_with_failures(self):
        """일부 태스크 실패"""
        results = [
            {"success": True, "agent_id": 1, "subtask": "Task 1", "output": "Output 1"},
            {"success": False, "agent_id": 2, "error": "Error message"},
        ]

        report = format_result_report(results)

        assert "성공: 1" in report
        assert "실패: 1" in report
        assert "실패한 태스크" in report
        assert "Error message" in report

    def test_empty_results(self):
        """빈 결과 리스트"""
        report = format_result_report([])

        assert "성공: 0" in report
        assert "실패: 0" in report
        assert "총: 0" in report

    def test_missing_fields(self):
        """필드가 누락된 경우"""
        results = [
            {"success": True},  # agent_id, subtask, output 없음
            {"success": False},  # error 없음
        ]

        report = format_result_report(results)

        assert "N/A" in report or "No output" in report
        assert "Unknown error" in report


class TestParseSubtasksFromText:
    """parse_subtasks_from_text 함수 테스트"""

    def test_numbered_list(self):
        """번호 매긴 리스트 파싱"""
        text = """1. First task
2. Second task
3. Third task"""

        subtasks = parse_subtasks_from_text(text)

        assert len(subtasks) == 3
        assert "First task" in subtasks
        assert "Second task" in subtasks
        assert "Third task" in subtasks

    def test_dash_list(self):
        """대시 리스트 파싱"""
        text = """- Task A
- Task B
- Task C"""

        subtasks = parse_subtasks_from_text(text)

        assert len(subtasks) == 3
        assert "Task A" in subtasks

    def test_asterisk_list(self):
        """별표 리스트 파싱"""
        text = """* Task X
* Task Y"""

        subtasks = parse_subtasks_from_text(text)

        assert len(subtasks) == 2
        assert "Task X" in subtasks

    def test_bullet_list(self):
        """불릿 리스트 파싱"""
        text = """• Task 1
• Task 2"""

        subtasks = parse_subtasks_from_text(text)

        assert len(subtasks) == 2
        assert "Task 1" in subtasks

    def test_mixed_empty_lines(self):
        """빈 줄이 섞인 경우"""
        text = """1. First

2. Second

3. Third"""

        subtasks = parse_subtasks_from_text(text)

        assert len(subtasks) == 3

    def test_fallback_to_first_three_lines(self):
        """패턴이 없으면 처음 3줄 반환"""
        text = """Line one
Line two
Line three
Line four"""

        subtasks = parse_subtasks_from_text(text)

        assert len(subtasks) == 3
        assert "Line one" in subtasks
        assert "Line four" not in subtasks

    def test_empty_text(self):
        """빈 텍스트"""
        subtasks = parse_subtasks_from_text("")

        assert len(subtasks) <= 3

    def test_whitespace_handling(self):
        """공백 처리"""
        text = """  1.   Spaced task
  2.   Another task  """

        subtasks = parse_subtasks_from_text(text)

        assert "Spaced task" in subtasks
        assert "Another task" in subtasks
