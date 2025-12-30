# tests/test_config.py
"""
Tests for src/agents/config.py - Multi-Agent System Configuration
"""

import pytest

from src.agents.config import (
    AGENT_MODEL_TIERS,
    PHASE_AGENTS,
    AgentConfig,
    DEFAULT_AGENTS,
    get_api_key,
)


class TestAgentModelTiers:
    """AGENT_MODEL_TIERS 상수 테스트"""

    def test_contains_required_tiers(self):
        """필수 tier가 모두 정의되어 있는지 확인"""
        required_tiers = ["supervisor", "lead", "researcher", "coder", "reviewer", "validator", "default"]
        for tier in required_tiers:
            assert tier in AGENT_MODEL_TIERS, f"Missing tier: {tier}"

    def test_all_values_are_valid_model_strings(self):
        """모든 값이 유효한 모델 문자열인지 확인"""
        for tier, model in AGENT_MODEL_TIERS.items():
            assert isinstance(model, str), f"Tier '{tier}' has non-string value"
            assert "claude" in model.lower(), f"Tier '{tier}' has invalid model: {model}"

    def test_default_tier_exists(self):
        """default tier가 존재하는지 확인"""
        assert "default" in AGENT_MODEL_TIERS

    def test_validator_uses_haiku_for_cost_optimization(self):
        """validator는 비용 최적화를 위해 haiku 사용"""
        assert "haiku" in AGENT_MODEL_TIERS["validator"]


class TestPhaseAgents:
    """PHASE_AGENTS 상수 테스트"""

    def test_contains_all_phases(self):
        """모든 phase가 정의되어 있는지 확인"""
        expected_phases = ["phase_0", "phase_0.5", "phase_1", "phase_2", "phase_2.5", "phase_3", "phase_4"]
        for phase in expected_phases:
            assert phase in PHASE_AGENTS, f"Missing phase: {phase}"

    def test_all_phases_have_agents(self):
        """모든 phase에 에이전트가 할당되어 있는지 확인"""
        for phase, agents in PHASE_AGENTS.items():
            assert isinstance(agents, list), f"Phase '{phase}' agents is not a list"
            assert len(agents) > 0, f"Phase '{phase}' has no agents"

    def test_phase_1_has_parallel_agents(self):
        """phase_1은 병렬 에이전트를 가짐"""
        phase_1_agents = PHASE_AGENTS["phase_1"]
        assert "code_agent" in phase_1_agents
        assert "test_agent" in phase_1_agents
        assert "docs_agent" in phase_1_agents


class TestAgentConfig:
    """AgentConfig dataclass 테스트"""

    def test_create_with_required_fields(self):
        """필수 필드로 생성"""
        config = AgentConfig(name="test_agent", role="test role")
        assert config.name == "test_agent"
        assert config.role == "test role"

    def test_default_model_applied(self):
        """기본 모델이 적용되는지 확인"""
        config = AgentConfig(name="test", role="test")
        assert config.model == AGENT_MODEL_TIERS["default"]

    def test_custom_model_override(self):
        """커스텀 모델 오버라이드"""
        custom_model = "claude-opus-4-0-20250514"
        config = AgentConfig(name="test", role="test", model=custom_model)
        assert config.model == custom_model

    def test_default_system_prompt_generated(self):
        """시스템 프롬프트가 자동 생성되는지 확인"""
        config = AgentConfig(name="my_agent", role="코드 작성")
        assert config.system_prompt is not None
        assert "코드 작성" in config.system_prompt

    def test_custom_system_prompt_preserved(self):
        """커스텀 시스템 프롬프트가 유지되는지 확인"""
        custom_prompt = "This is a custom prompt"
        config = AgentConfig(name="test", role="test", system_prompt=custom_prompt)
        assert config.system_prompt == custom_prompt

    def test_default_tools_empty(self):
        """기본 tools는 빈 리스트"""
        config = AgentConfig(name="test", role="test")
        assert config.tools == []

    def test_custom_tools(self):
        """커스텀 tools 설정"""
        tools = ["read_file", "write_file", "bash"]
        config = AgentConfig(name="test", role="test", tools=tools)
        assert config.tools == tools

    def test_default_max_retries(self):
        """기본 max_retries 값"""
        config = AgentConfig(name="test", role="test")
        assert config.max_retries == 3

    def test_default_timeout_seconds(self):
        """기본 timeout_seconds 값"""
        config = AgentConfig(name="test", role="test")
        assert config.timeout_seconds == 120

    def test_default_context_isolation(self):
        """기본 context_isolation 값"""
        config = AgentConfig(name="test", role="test")
        assert config.context_isolation is True


class TestDefaultAgents:
    """DEFAULT_AGENTS 상수 테스트"""

    def test_contains_required_agents(self):
        """필수 에이전트가 정의되어 있는지 확인"""
        required_agents = ["supervisor", "researcher", "coder", "reviewer", "tester"]
        for agent in required_agents:
            assert agent in DEFAULT_AGENTS, f"Missing agent: {agent}"

    def test_all_values_are_agent_configs(self):
        """모든 값이 AgentConfig 인스턴스인지 확인"""
        for name, config in DEFAULT_AGENTS.items():
            assert isinstance(config, AgentConfig), f"Agent '{name}' is not AgentConfig"

    def test_supervisor_has_custom_system_prompt(self):
        """supervisor는 커스텀 시스템 프롬프트를 가짐"""
        supervisor = DEFAULT_AGENTS["supervisor"]
        assert "Supervisor" in supervisor.system_prompt

    def test_coder_has_required_tools(self):
        """coder는 필요한 tools를 가짐"""
        coder = DEFAULT_AGENTS["coder"]
        assert "write_file" in coder.tools
        assert "edit_file" in coder.tools
        assert "bash" in coder.tools

    def test_tester_uses_validator_model(self):
        """tester는 validator 모델(haiku) 사용"""
        tester = DEFAULT_AGENTS["tester"]
        assert tester.model == AGENT_MODEL_TIERS["validator"]


class TestGetApiKey:
    """get_api_key 함수 테스트"""

    def test_returns_api_key_when_set(self, monkeypatch):
        """환경 변수가 설정되어 있으면 API 키 반환"""
        test_key = "sk-ant-api03-test-key-12345"
        monkeypatch.setenv("ANTHROPIC_API_KEY", test_key)
        assert get_api_key() == test_key

    def test_raises_error_when_not_set(self, monkeypatch):
        """환경 변수가 없으면 ValueError 발생"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValueError) as exc_info:
            get_api_key()
        assert "ANTHROPIC_API_KEY" in str(exc_info.value)

    def test_error_message_includes_instructions(self, monkeypatch):
        """에러 메시지에 설정 지침 포함"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValueError) as exc_info:
            get_api_key()
        assert ".env" in str(exc_info.value) or "환경 변수" in str(exc_info.value)
