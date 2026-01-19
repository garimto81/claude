# tests/test_parallel_workflow.py
"""
병렬 워크플로우 테스트
"""

import pytest
import sys
import os

# 프로젝트 루트 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.config import (
    AgentConfig,
    AGENT_MODEL_TIERS,
    PHASE_AGENTS,
    DEFAULT_AGENTS,
)
from src.agents.utils import (
    parse_subtasks_from_text,
    format_result_report,
    ExecutionResult,
)


class TestAgentConfig:
    """AgentConfig 테스트"""

    def test_default_config(self):
        """기본 설정 생성 테스트"""
        config = AgentConfig(name="test", role="테스터")
        assert config.name == "test"
        assert config.role == "테스터"
        assert config.model == AGENT_MODEL_TIERS["default"]
        assert config.max_retries == 3
        assert config.context_isolation is True

    def test_custom_config(self):
        """커스텀 설정 테스트"""
        config = AgentConfig(
            name="custom",
            role="커스텀 역할",
            model="claude-opus-4",
            tools=["bash", "read_file"],
            max_retries=5,
        )
        assert config.name == "custom"
        assert config.tools == ["bash", "read_file"]
        assert config.max_retries == 5

    def test_system_prompt_auto_generation(self):
        """시스템 프롬프트 자동 생성 테스트"""
        config = AgentConfig(name="auto", role="자동 역할")
        assert "자동 역할" in config.system_prompt


class TestModelTiers:
    """모델 티어링 테스트"""

    def test_all_tiers_defined(self):
        """모든 티어가 정의되었는지 확인"""
        required_tiers = [
            "supervisor",
            "lead",
            "researcher",
            "coder",
            "reviewer",
            "validator",
            "default",
        ]
        for tier in required_tiers:
            assert tier in AGENT_MODEL_TIERS

    def test_default_tier_exists(self):
        """기본 티어 존재 확인"""
        assert "default" in AGENT_MODEL_TIERS
        assert AGENT_MODEL_TIERS["default"] is not None


class TestPhaseAgents:
    """Phase별 에이전트 매핑 테스트"""

    def test_all_phases_defined(self):
        """모든 Phase가 정의되었는지 확인"""
        required_phases = ["phase_0", "phase_0.5", "phase_1", "phase_2", "phase_2.5"]
        for phase in required_phases:
            assert phase in PHASE_AGENTS

    def test_phase_agents_not_empty(self):
        """각 Phase에 에이전트가 있는지 확인"""
        for phase, agents in PHASE_AGENTS.items():
            assert len(agents) > 0, f"{phase}에 에이전트가 없습니다"


class TestDefaultAgents:
    """기본 에이전트 설정 테스트"""

    def test_supervisor_exists(self):
        """Supervisor 에이전트 존재 확인"""
        assert "supervisor" in DEFAULT_AGENTS
        assert DEFAULT_AGENTS["supervisor"].role == "작업 분배 및 조율"

    def test_all_default_agents_have_roles(self):
        """모든 기본 에이전트가 역할을 가지고 있는지 확인"""
        for name, config in DEFAULT_AGENTS.items():
            assert config.role, f"{name} 에이전트에 역할이 없습니다"


class TestParseSubtasks:
    """서브태스크 파싱 테스트"""

    def test_numbered_list(self):
        """번호 매긴 리스트 파싱"""
        text = """
1. 첫 번째 태스크
2. 두 번째 태스크
3. 세 번째 태스크
"""
        result = parse_subtasks_from_text(text)
        assert len(result) == 3
        assert result[0] == "첫 번째 태스크"

    def test_bullet_list(self):
        """불릿 리스트 파싱"""
        text = """
- 태스크 A
- 태스크 B
- 태스크 C
"""
        result = parse_subtasks_from_text(text)
        assert len(result) == 3
        assert result[0] == "태스크 A"

    def test_mixed_format(self):
        """혼합 형식 파싱"""
        text = """
1. 첫 번째
- 두 번째
* 세 번째
"""
        result = parse_subtasks_from_text(text)
        assert len(result) >= 2


class TestFormatResultReport:
    """결과 보고서 포맷팅 테스트"""

    def test_successful_results(self):
        """성공 결과 포맷팅"""
        results = [
            {"agent_id": "0", "subtask": "태스크1", "output": "결과1", "success": True},
            {"agent_id": "1", "subtask": "태스크2", "output": "결과2", "success": True},
        ]
        report = format_result_report(results)
        assert "성공: 2" in report
        assert "실패: 0" in report

    def test_mixed_results(self):
        """성공/실패 혼합 결과 포맷팅"""
        results = [
            {"agent_id": "0", "subtask": "태스크1", "output": "결과1", "success": True},
            {
                "agent_id": "1",
                "subtask": "태스크2",
                "output": "",
                "success": False,
                "error": "타임아웃",
            },
        ]
        report = format_result_report(results)
        assert "성공: 1" in report
        assert "실패: 1" in report
        assert "실패한 태스크" in report

    def test_empty_results(self):
        """빈 결과 포맷팅"""
        results = []
        report = format_result_report(results)
        assert "성공: 0" in report


class TestExecutionResult:
    """ExecutionResult 테스트"""

    def test_successful_result(self):
        """성공 결과 생성"""
        result = ExecutionResult(
            success=True, output="테스트 출력", duration_seconds=1.5
        )
        assert result.success is True
        assert result.output == "테스트 출력"
        assert result.error is None

    def test_failed_result(self):
        """실패 결과 생성"""
        result = ExecutionResult(
            success=False, output=None, duration_seconds=5.0, error="Connection timeout"
        )
        assert result.success is False
        assert result.error == "Connection timeout"


# ============================================================================
# Integration Tests (실제 API 호출 필요)
# ============================================================================


@pytest.mark.integration
@pytest.mark.skip(reason="실제 API 키 필요")
class TestParallelWorkflowIntegration:
    """병렬 워크플로우 통합 테스트"""

    def test_simple_task(self):
        """간단한 태스크 실행"""
        from src.agents.parallel_workflow import run_parallel_task

        result = run_parallel_task("Python에서 리스트 정렬하는 3가지 방법")
        assert "final_output" in result
        assert len(result["final_output"]) > 0

    def test_parallel_execution(self):
        """병렬 실행 확인"""
        from src.agents.parallel_workflow import run_parallel_task

        result = run_parallel_task("웹 개발 프레임워크 비교 분석", num_agents=3)
        assert len(result["results"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
