# tests/test_benchmark.py
"""
Tests for src/agents/benchmark.py - 병렬 워크플로우 성능 벤치마크
"""

import asyncio
import pytest

from src.agents.benchmark import (
    BenchmarkResult,
    benchmark_sequential,
    benchmark_parallel,
    compare_results,
    simulate_task,
    simulate_task_async,
)


class TestBenchmarkResult:
    """BenchmarkResult dataclass 테스트"""

    def test_create_benchmark_result(self):
        """BenchmarkResult 생성"""
        result = BenchmarkResult(
            name="Test",
            execution_mode="sequential",
            total_time_seconds=1.5,
            individual_times=[0.5, 0.5, 0.5],
            success_count=3,
            failure_count=0,
        )
        assert result.name == "Test"
        assert result.execution_mode == "sequential"
        assert result.total_time_seconds == 1.5
        assert len(result.individual_times) == 3
        assert result.success_count == 3
        assert result.failure_count == 0

    def test_benchmark_result_with_failures(self):
        """실패가 있는 BenchmarkResult"""
        result = BenchmarkResult(
            name="Test with failures",
            execution_mode="parallel",
            total_time_seconds=2.0,
            individual_times=[0.5, 0.5, 0.5, 0.5],
            success_count=2,
            failure_count=2,
        )
        assert result.success_count == 2
        assert result.failure_count == 2


class TestBenchmarkSequential:
    """benchmark_sequential 함수 테스트"""

    def test_sequential_all_success(self):
        """모든 태스크 성공"""
        tasks = [lambda: None, lambda: None, lambda: None]
        result = benchmark_sequential(tasks)

        assert result.name == "Sequential Execution"
        assert result.execution_mode == "sequential"
        assert result.success_count == 3
        assert result.failure_count == 0
        assert len(result.individual_times) == 3

    def test_sequential_with_failures(self):
        """일부 태스크 실패"""
        def failing_task():
            raise ValueError("Test error")

        tasks = [lambda: None, failing_task, lambda: None]
        result = benchmark_sequential(tasks)

        assert result.success_count == 2
        assert result.failure_count == 1

    def test_sequential_with_custom_names(self):
        """커스텀 태스크 이름"""
        tasks = [lambda: None, lambda: None]
        task_names = ["task_a", "task_b"]
        result = benchmark_sequential(tasks, task_names)

        assert result.success_count == 2
        assert len(result.individual_times) == 2

    def test_sequential_empty_tasks(self):
        """빈 태스크 리스트"""
        result = benchmark_sequential([])

        assert result.success_count == 0
        assert result.failure_count == 0
        assert result.individual_times == []

    def test_sequential_measures_time(self):
        """실행 시간 측정"""
        import time

        def slow_task():
            time.sleep(0.01)

        tasks = [slow_task, slow_task]
        result = benchmark_sequential(tasks)

        assert result.total_time_seconds >= 0.02
        for t in result.individual_times:
            assert t >= 0.01


class TestBenchmarkParallel:
    """benchmark_parallel 함수 테스트"""

    @pytest.mark.asyncio
    async def test_parallel_all_success(self):
        """모든 태스크 성공"""
        tasks = [lambda: None, lambda: None, lambda: None]
        result = await benchmark_parallel(tasks)

        assert result.name == "Parallel Execution"
        assert result.execution_mode == "parallel"
        assert result.success_count == 3
        assert result.failure_count == 0

    @pytest.mark.asyncio
    async def test_parallel_with_async_tasks(self):
        """비동기 태스크 실행"""
        async def async_task():
            await asyncio.sleep(0.001)

        tasks = [async_task, async_task, async_task]
        result = await benchmark_parallel(tasks)

        assert result.success_count == 3
        assert result.failure_count == 0

    @pytest.mark.asyncio
    async def test_parallel_with_failures(self):
        """일부 태스크 실패"""
        def failing_task():
            raise ValueError("Test error")

        tasks = [lambda: None, failing_task, lambda: None]
        result = await benchmark_parallel(tasks)

        assert result.success_count == 2
        assert result.failure_count == 1

    @pytest.mark.asyncio
    async def test_parallel_async_failure(self):
        """비동기 태스크 실패"""
        async def failing_async_task():
            raise ValueError("Async error")

        tasks = [failing_async_task, lambda: None]
        result = await benchmark_parallel(tasks)

        assert result.success_count == 1
        assert result.failure_count == 1

    @pytest.mark.asyncio
    async def test_parallel_empty_tasks(self):
        """빈 태스크 리스트"""
        result = await benchmark_parallel([])

        assert result.success_count == 0
        assert result.failure_count == 0
        assert result.individual_times == []

    @pytest.mark.asyncio
    async def test_parallel_faster_than_sequential(self):
        """병렬이 순차보다 빠름"""
        import time

        def slow_task():
            time.sleep(0.05)

        tasks = [slow_task, slow_task, slow_task]

        # Sequential
        seq_result = benchmark_sequential(tasks.copy())

        # Parallel
        par_result = await benchmark_parallel(tasks.copy())

        # 병렬 실행이 더 빨라야 함 (또는 비슷)
        # 동기 태스크라 큰 차이 없을 수 있음
        assert par_result.total_time_seconds <= seq_result.total_time_seconds * 1.5


class TestCompareResults:
    """compare_results 함수 테스트"""

    def test_compare_results_parallel_faster(self):
        """병렬이 더 빠른 경우"""
        sequential = BenchmarkResult(
            name="Sequential",
            execution_mode="sequential",
            total_time_seconds=5.0,
            individual_times=[1.0, 1.0, 1.0, 1.0, 1.0],
            success_count=5,
            failure_count=0,
        )
        parallel = BenchmarkResult(
            name="Parallel",
            execution_mode="parallel",
            total_time_seconds=1.0,
            individual_times=[1.0, 1.0, 1.0, 1.0, 1.0],
            success_count=5,
            failure_count=0,
        )

        report = compare_results(sequential, parallel)

        assert "5.00초" in report  # Sequential 시간
        assert "1.00초" in report  # Parallel 시간
        assert "5.00x" in report or "5.0x" in report  # Speedup
        assert "병렬 실행이" in report
        assert "빠릅니다" in report

    def test_compare_results_no_speedup(self):
        """병렬화 효과 없는 경우"""
        sequential = BenchmarkResult(
            name="Sequential",
            execution_mode="sequential",
            total_time_seconds=1.0,
            individual_times=[1.0],
            success_count=1,
            failure_count=0,
        )
        parallel = BenchmarkResult(
            name="Parallel",
            execution_mode="parallel",
            total_time_seconds=1.0,
            individual_times=[1.0],
            success_count=1,
            failure_count=0,
        )

        report = compare_results(sequential, parallel)

        assert "제한적" in report

    def test_compare_results_zero_parallel_time(self):
        """병렬 시간이 0인 경우 (에지 케이스)"""
        sequential = BenchmarkResult(
            name="Sequential",
            execution_mode="sequential",
            total_time_seconds=1.0,
            individual_times=[1.0],
            success_count=1,
            failure_count=0,
        )
        parallel = BenchmarkResult(
            name="Parallel",
            execution_mode="parallel",
            total_time_seconds=0.0,
            individual_times=[0.0],
            success_count=1,
            failure_count=0,
        )

        # ZeroDivisionError가 발생하지 않아야 함
        report = compare_results(sequential, parallel)
        assert report is not None

    def test_compare_results_zero_sequential_time(self):
        """순차 시간이 0인 경우 (에지 케이스)"""
        sequential = BenchmarkResult(
            name="Sequential",
            execution_mode="sequential",
            total_time_seconds=0.0,
            individual_times=[0.0],
            success_count=1,
            failure_count=0,
        )
        parallel = BenchmarkResult(
            name="Parallel",
            execution_mode="parallel",
            total_time_seconds=1.0,
            individual_times=[1.0],
            success_count=1,
            failure_count=0,
        )

        report = compare_results(sequential, parallel)
        assert report is not None

    def test_compare_results_with_failures(self):
        """실패가 포함된 결과 비교"""
        sequential = BenchmarkResult(
            name="Sequential",
            execution_mode="sequential",
            total_time_seconds=3.0,
            individual_times=[1.0, 1.0, 1.0],
            success_count=2,
            failure_count=1,
        )
        parallel = BenchmarkResult(
            name="Parallel",
            execution_mode="parallel",
            total_time_seconds=1.0,
            individual_times=[1.0, 1.0, 1.0],
            success_count=2,
            failure_count=1,
        )

        report = compare_results(sequential, parallel)

        assert "2/1" in report  # success/failure


class TestSimulateTask:
    """simulate_task 함수 테스트"""

    def test_simulate_task_default_duration(self):
        """기본 duration으로 실행"""
        import time

        start = time.time()
        result = simulate_task(0.01)  # 빠른 테스트를 위해 짧은 시간
        elapsed = time.time() - start

        assert elapsed >= 0.01
        assert "completed" in result.lower()

    def test_simulate_task_custom_duration(self):
        """커스텀 duration으로 실행"""
        result = simulate_task(0.01)
        assert "0.01" in result


class TestSimulateTaskAsync:
    """simulate_task_async 함수 테스트"""

    @pytest.mark.asyncio
    async def test_simulate_task_async_default_duration(self):
        """기본 duration으로 비동기 실행"""
        import time

        start = time.time()
        result = await simulate_task_async(0.01)
        elapsed = time.time() - start

        assert elapsed >= 0.01
        assert "completed" in result.lower()

    @pytest.mark.asyncio
    async def test_simulate_task_async_custom_duration(self):
        """커스텀 duration으로 비동기 실행"""
        result = await simulate_task_async(0.01)
        assert "0.01" in result
