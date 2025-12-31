# tests/test_phase_validator.py
"""
Tests for src/agents/phase_validator.py - Phase 검증 병렬 실행기
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.agents.phase_validator import (
    ValidationResult,
    PROJECT_ROOT,
    run_validator,
    run_validators_parallel,
    run_command_async,
    format_validation_report,
)


class TestValidationResult:
    """ValidationResult dataclass 테스트"""

    def test_create_success_result(self):
        """성공 결과 생성"""
        result = ValidationResult(
            phase="1",
            success=True,
            output="All tests passed",
            duration_seconds=5.0,
        )
        assert result.phase == "1"
        assert result.success is True
        assert result.output == "All tests passed"
        assert result.duration_seconds == 5.0
        assert result.error is None

    def test_create_failure_result(self):
        """실패 결과 생성"""
        result = ValidationResult(
            phase="2",
            success=False,
            output="",
            duration_seconds=3.0,
            error="Test failed",
        )
        assert result.success is False
        assert result.error == "Test failed"


class TestRunValidator:
    """run_validator 함수 테스트"""

    @pytest.mark.asyncio
    async def test_script_not_found(self):
        """스크립트가 없는 경우"""
        from pathlib import Path

        with patch.object(Path, "exists", return_value=False):
            result = await run_validator("99")

            assert result.success is False
            assert "not found" in result.error.lower() or "script" in result.error.lower()

    @pytest.mark.asyncio
    async def test_successful_validation(self):
        """성공적인 검증"""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"Success output", b""))

        with patch("src.agents.phase_validator.PROJECT_ROOT") as mock_root:
            mock_script_path = MagicMock()
            mock_script_path.exists.return_value = True
            mock_script_path.__str__ = MagicMock(return_value="test_script.ps1")
            mock_root.__truediv__ = MagicMock(return_value=mock_script_path)

            with patch("asyncio.create_subprocess_exec", return_value=mock_process):
                result = await run_validator("1")

                assert result.success is True
                assert result.output == "Success output"
                assert result.error is None

    @pytest.mark.asyncio
    async def test_failed_validation(self):
        """실패한 검증"""
        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"Error message"))

        with patch("src.agents.phase_validator.PROJECT_ROOT") as mock_root:
            mock_script_path = MagicMock()
            mock_script_path.exists.return_value = True
            mock_script_path.__str__ = MagicMock(return_value="test_script.ps1")
            mock_root.__truediv__ = MagicMock(return_value=mock_script_path)

            with patch("asyncio.create_subprocess_exec", return_value=mock_process):
                result = await run_validator("1")

                assert result.success is False
                assert result.error == "Error message"

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """타임아웃 처리"""
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())

        with patch("src.agents.phase_validator.PROJECT_ROOT") as mock_root:
            mock_script_path = MagicMock()
            mock_script_path.exists.return_value = True
            mock_script_path.__str__ = MagicMock(return_value="test_script.ps1")
            mock_root.__truediv__ = MagicMock(return_value=mock_script_path)

            with patch("asyncio.create_subprocess_exec", return_value=mock_process):
                result = await run_validator("1")

                assert result.success is False
                assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """예외 처리"""
        with patch("src.agents.phase_validator.PROJECT_ROOT") as mock_root:
            mock_script_path = MagicMock()
            mock_script_path.exists.return_value = True
            mock_script_path.__str__ = MagicMock(return_value="test_script.ps1")
            mock_root.__truediv__ = MagicMock(return_value=mock_script_path)

            with patch("asyncio.create_subprocess_exec", side_effect=OSError("Command not found")):
                result = await run_validator("1")

                assert result.success is False
                assert "Command not found" in result.error

    @pytest.mark.asyncio
    async def test_with_args(self):
        """추가 인자 전달"""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"Output", b""))

        with patch("src.agents.phase_validator.PROJECT_ROOT") as mock_root:
            mock_script_path = MagicMock()
            mock_script_path.exists.return_value = True
            mock_script_path.__str__ = MagicMock(return_value="test_script.ps1")
            mock_root.__truediv__ = MagicMock(return_value=mock_script_path)

            with patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_exec:
                result = await run_validator("1", ["--verbose", "--dry-run"])

                assert result.success is True
                # 인자가 전달되었는지 확인
                call_args = mock_exec.call_args
                assert "--verbose" in call_args[0]
                assert "--dry-run" in call_args[0]


class TestRunValidatorsParallel:
    """run_validators_parallel 함수 테스트"""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """병렬 실행"""
        mock_results = [
            ValidationResult(phase="1", success=True, output="OK", duration_seconds=1.0),
            ValidationResult(phase="2", success=True, output="OK", duration_seconds=1.0),
        ]

        with patch("src.agents.phase_validator.run_validator") as mock_run:
            mock_run.side_effect = mock_results

            results = await run_validators_parallel(["1", "2"])

            assert len(results) == 2
            assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_with_args_map(self):
        """Phase별 인자 맵"""
        mock_result = ValidationResult(phase="1", success=True, output="OK", duration_seconds=1.0)

        with patch("src.agents.phase_validator.run_validator", return_value=mock_result) as mock_run:
            args_map = {"1": ["--verbose"], "2": ["--quick"]}
            await run_validators_parallel(["1", "2"], args_map)

            # 각 phase에 맞는 인자가 전달되었는지 확인
            calls = mock_run.call_args_list
            assert calls[0][0] == ("1", ["--verbose"])
            assert calls[1][0] == ("2", ["--quick"])

    @pytest.mark.asyncio
    async def test_empty_phases(self):
        """빈 phase 리스트"""
        results = await run_validators_parallel([])
        assert results == []


class TestRunCommandAsync:
    """run_command_async 함수 테스트"""

    @pytest.mark.asyncio
    async def test_successful_command(self):
        """성공적인 명령어 실행"""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"Command output", b""))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await run_command_async("test", ["echo", "hello"])

            assert result.success is True
            assert result.phase == "test"
            assert result.output == "Command output"

    @pytest.mark.asyncio
    async def test_failed_command(self):
        """실패한 명령어"""
        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b"", b"Error output"))

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await run_command_async("lint", ["ruff", "check"])

            assert result.success is False
            assert result.error == "Error output"

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """예외 처리"""
        with patch("asyncio.create_subprocess_exec", side_effect=FileNotFoundError("Command not found")):
            result = await run_command_async("test", ["nonexistent"])

            assert result.success is False
            assert "not found" in result.error.lower()


class TestFormatValidationReport:
    """format_validation_report 함수 테스트"""

    def test_all_passed(self):
        """모든 검증 통과"""
        results = [
            ValidationResult(phase="1", success=True, output="OK", duration_seconds=2.0),
            ValidationResult(phase="2", success=True, output="OK", duration_seconds=3.0),
        ]

        report = format_validation_report(results)

        assert "2 passed" in report
        assert "0 failed" in report
        assert "PASS" in report
        assert "Phase 1" in report
        assert "Phase 2" in report

    def test_with_failures(self):
        """일부 검증 실패"""
        results = [
            ValidationResult(phase="1", success=True, output="OK", duration_seconds=2.0),
            ValidationResult(phase="2", success=False, output="", duration_seconds=3.0, error="Test failed"),
        ]

        report = format_validation_report(results)

        assert "1 passed" in report
        assert "1 failed" in report
        assert "PASS" in report
        assert "FAIL" in report
        assert "Test failed" in report

    def test_empty_results(self):
        """빈 결과 리스트"""
        report = format_validation_report([])

        assert "0 passed" in report
        assert "0 failed" in report

    def test_total_time_calculation(self):
        """총 소요 시간 계산"""
        results = [
            ValidationResult(phase="1", success=True, output="OK", duration_seconds=2.5),
            ValidationResult(phase="2", success=True, output="OK", duration_seconds=3.5),
        ]

        report = format_validation_report(results)

        # 2.5 + 3.5 = 6.0
        assert "6.00" in report

    def test_long_error_truncated(self):
        """긴 에러 메시지 잘림"""
        long_error = "A" * 200  # 200자 에러
        results = [
            ValidationResult(phase="1", success=False, output="", duration_seconds=1.0, error=long_error),
        ]

        report = format_validation_report(results)

        # 에러가 100자 + "..."로 잘려야 함
        assert "..." in report
        assert long_error not in report  # 전체 에러가 없어야 함


class TestProjectRoot:
    """PROJECT_ROOT 상수 테스트"""

    def test_project_root_is_path(self):
        """PROJECT_ROOT가 Path 객체"""
        from pathlib import Path
        assert isinstance(PROJECT_ROOT, Path)

    def test_project_root_value(self):
        """PROJECT_ROOT 값 확인"""
        assert "claude01" in str(PROJECT_ROOT)
