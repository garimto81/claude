# tests/prompt_learning/test_textgrad_optimizer.py
"""
TextGrad Optimizer 테스트

pytest tests/prompt_learning/test_textgrad_optimizer.py -v
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.textgrad_optimizer import (
    TextGradOptimizer,
    TextGradient,
    GradientType,
    OptimizationStep,
    AgentOptimizationResult,
    create_textgrad_optimizer,
    optimize_single_prompt,
)


class TestTextGradient:
    """TextGradient 테스트"""

    def test_create_gradient(self):
        """그래디언트 생성"""
        gradient = TextGradient(
            gradient_type=GradientType.IMPROVE_CLARITY,
            original_text="original",
            feedback="needs improvement",
            suggested_change="improved",
            confidence=0.8
        )
        assert gradient.gradient_type == GradientType.IMPROVE_CLARITY
        assert gradient.confidence == 0.8

    def test_apply_gradient(self):
        """그래디언트 적용"""
        gradient = TextGradient(
            gradient_type=GradientType.IMPROVE_CLARITY,
            original_text="old",
            feedback="change it",
            suggested_change="new text",
            confidence=0.9
        )
        result = gradient.apply()
        assert result == "new text"


class TestOptimizationStep:
    """OptimizationStep 테스트"""

    def test_improvement_calculation(self):
        """개선율 계산"""
        step = OptimizationStep(
            step_number=1,
            original_prompt="old",
            optimized_prompt="new",
            gradients_applied=[],
            score_before=0.5,
            score_after=0.7
        )
        assert abs(step.improvement - 0.2) < 0.0001  # 부동소수점 비교


class TestAgentOptimizationResult:
    """AgentOptimizationResult 테스트"""

    def test_final_score_with_steps(self):
        """단계가 있을 때 최종 점수"""
        step = OptimizationStep(
            step_number=1,
            original_prompt="old",
            optimized_prompt="new",
            gradients_applied=[],
            score_before=0.5,
            score_after=0.8
        )
        result = AgentOptimizationResult(
            agent_name="test-agent",
            original_prompt="old",
            optimized_prompt="new",
            steps=[step],
            total_improvement=0.3,
            iterations=1
        )
        assert result.final_score == 0.8

    def test_final_score_no_steps(self):
        """단계가 없을 때 최종 점수"""
        result = AgentOptimizationResult(
            agent_name="test-agent",
            original_prompt="old",
            optimized_prompt="old",
            steps=[],
            total_improvement=0.0,
            iterations=0
        )
        assert result.final_score == 0.0


class TestTextGradOptimizer:
    """TextGradOptimizer 테스트"""

    def test_create_optimizer(self):
        """옵티마이저 생성"""
        optimizer = TextGradOptimizer()
        assert optimizer.model == "claude-sonnet-4"

    def test_create_optimizer_custom_model(self):
        """커스텀 모델로 생성"""
        optimizer = TextGradOptimizer(model="claude-haiku-3")
        assert optimizer.model == "claude-haiku-3"

    def test_analyze_short_prompt(self):
        """짧은 프롬프트 분석"""
        optimizer = TextGradOptimizer()
        prompt = "간단한 프롬프트입니다."
        gradients = optimizer.analyze_prompt(prompt)
        # 짧은 프롬프트는 ADD_EXAMPLES 그래디언트 생성
        assert any(g.gradient_type == GradientType.ADD_EXAMPLES for g in gradients)

    def test_analyze_long_prompt(self):
        """긴 프롬프트 분석"""
        optimizer = TextGradOptimizer()
        prompt = "이것은 매우 긴 프롬프트입니다 " * 100
        gradients = optimizer.analyze_prompt(prompt)
        # 긴 프롬프트는 IMPROVE_CONCISENESS 그래디언트 생성
        assert any(g.gradient_type == GradientType.IMPROVE_CONCISENESS for g in gradients)

    def test_analyze_vague_prompt(self):
        """모호한 프롬프트 분석"""
        optimizer = TextGradOptimizer()
        prompt = "이것 저것 등 여러 가지 것들을 처리합니다. 기타 등등."
        gradients = optimizer.analyze_prompt(prompt)
        # 모호한 표현이 있으면 IMPROVE_SPECIFICITY 그래디언트 생성
        assert any(g.gradient_type == GradientType.IMPROVE_SPECIFICITY for g in gradients)


class TestPromptOptimization:
    """프롬프트 최적화 테스트"""

    def test_optimize_prompt_basic(self):
        """기본 프롬프트 최적화"""
        optimizer = TextGradOptimizer()
        prompt = "이것은 테스트 프롬프트입니다"
        optimized, steps = optimizer.optimize_prompt(prompt, max_iterations=3)
        assert isinstance(optimized, str)
        assert isinstance(steps, list)

    def test_optimize_prompt_with_examples_added(self):
        """예시 추가 최적화"""
        optimizer = TextGradOptimizer()
        prompt = "작업을 수행합니다."
        optimized, steps = optimizer.optimize_prompt(prompt, max_iterations=3)
        # 예시가 추가되어야 함
        if steps:
            assert any(
                GradientType.ADD_EXAMPLES in [g.gradient_type for g in s.gradients_applied]
                for s in steps
            )

    def test_optimize_prompt_max_iterations(self):
        """최대 반복 횟수 제한"""
        optimizer = TextGradOptimizer()
        prompt = "테스트"
        optimized, steps = optimizer.optimize_prompt(prompt, max_iterations=2)
        assert len(steps) <= 2


class TestAgentOptimization:
    """에이전트 최적화 테스트"""

    def test_optimize_agent(self):
        """에이전트 최적화"""
        optimizer = TextGradOptimizer()
        result = optimizer.optimize_agent(
            agent_name="test-agent",
            agent_prompt="에이전트 프롬프트입니다",
            max_iterations=3
        )
        assert result.agent_name == "test-agent"
        assert isinstance(result.optimized_prompt, str)

    def test_optimize_all_agents_empty_dir(self):
        """빈 디렉토리"""
        optimizer = TextGradOptimizer()
        with tempfile.TemporaryDirectory() as tmpdir:
            results = optimizer.optimize_all_agents(tmpdir)
            assert results == []

    def test_optimize_all_agents_with_files(self):
        """파일이 있는 디렉토리"""
        optimizer = TextGradOptimizer()
        with tempfile.TemporaryDirectory() as tmpdir:
            # 테스트 에이전트 파일 생성
            agent_path = Path(tmpdir) / "test-agent.md"
            agent_path.write_text("테스트 에이전트 프롬프트", encoding="utf-8")

            results = optimizer.optimize_all_agents(tmpdir, max_iterations=2)
            assert len(results) == 1
            assert results[0].agent_name == "test-agent"

    def test_optimization_history(self):
        """최적화 히스토리"""
        optimizer = TextGradOptimizer()
        optimizer.optimize_agent("agent1", "prompt1")
        optimizer.optimize_agent("agent2", "prompt2")
        history = optimizer.get_optimization_history()
        assert len(history) == 2


class TestReport:
    """리포트 생성 테스트"""

    def test_generate_report_empty(self):
        """빈 결과 리포트"""
        optimizer = TextGradOptimizer()
        report = optimizer.generate_report([])
        assert "# TextGrad 최적화 리포트" in report
        assert "분석된 에이전트: 0개" in report

    def test_generate_report_with_results(self):
        """결과가 있는 리포트"""
        optimizer = TextGradOptimizer()
        result = AgentOptimizationResult(
            agent_name="test-agent",
            original_prompt="old",
            optimized_prompt="new",
            steps=[],
            total_improvement=0.15,
            iterations=2
        )
        report = optimizer.generate_report([result])
        assert "test-agent" in report
        assert "분석된 에이전트: 1개" in report


class TestConvenienceFunctions:
    """편의 함수 테스트"""

    def test_create_textgrad_optimizer(self):
        """create_textgrad_optimizer 함수"""
        optimizer = create_textgrad_optimizer("custom-model")
        assert optimizer.model == "custom-model"

    def test_optimize_single_prompt(self):
        """optimize_single_prompt 함수"""
        result = optimize_single_prompt("테스트 프롬프트", max_iterations=2)
        assert isinstance(result, str)


class TestEvaluatePrompt:
    """프롬프트 평가 테스트"""

    def test_evaluate_short_prompt(self):
        """짧은 프롬프트 평가"""
        optimizer = TextGradOptimizer()
        score = optimizer._evaluate_prompt("짧음")
        assert 0 <= score <= 1

    def test_evaluate_good_prompt(self):
        """좋은 프롬프트 평가"""
        optimizer = TextGradOptimizer()
        prompt = """
이것은 잘 구성된 프롬프트입니다.
여러 줄로 나뉘어 있습니다.
명확한 구조를 가지고 있습니다.

예시:
- 입력: 테스트
- 출력: 결과
"""
        score = optimizer._evaluate_prompt(prompt)
        # 좋은 프롬프트는 높은 점수
        assert score >= 0.6

    def test_evaluate_poor_prompt(self):
        """나쁜 프롬프트 평가"""
        optimizer = TextGradOptimizer()
        score = optimizer._evaluate_prompt("x")
        # 나쁜 프롬프트는 낮은 점수
        assert score <= 0.6
