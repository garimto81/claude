# tests/prompt_learning/test_dspy_optimizer.py
"""
DSPy Optimizer 테스트

pytest tests/prompt_learning/test_dspy_optimizer.py -v
"""

import pytest
import tempfile
import os
import sys

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.dspy_optimizer import (
    DSPyOptimizer,
    PhaseSignature,
    OptimizationResult,
    OptimizationStatus,
    DEFAULT_SIGNATURES,
    create_optimizer,
    optimize_phase,
)


class TestPhaseSignature:
    """PhaseSignature 테스트"""

    def test_create_signature(self):
        """Signature 생성"""
        sig = PhaseSignature(
            phase=0,
            input_fields=["content"],
            output_fields=["is_valid"],
            instructions="검증 수행"
        )
        assert sig.phase == 0
        assert "content" in sig.input_fields
        assert "is_valid" in sig.output_fields

    def test_to_dict(self):
        """딕셔너리 변환"""
        sig = PhaseSignature(
            phase=1,
            input_fields=["a", "b"],
            output_fields=["c"],
            instructions="test"
        )
        d = sig.to_dict()
        assert d["phase"] == 1
        assert d["input_fields"] == ["a", "b"]

    def test_from_dict(self):
        """딕셔너리에서 생성"""
        data = {
            "phase": 2,
            "input_fields": ["x"],
            "output_fields": ["y"],
            "instructions": "inst",
            "examples": [{"in": 1, "out": 2}]
        }
        sig = PhaseSignature.from_dict(data)
        assert sig.phase == 2
        assert len(sig.examples) == 1


class TestDSPyOptimizer:
    """DSPyOptimizer 테스트"""

    def test_create_optimizer(self):
        """옵티마이저 생성"""
        opt = DSPyOptimizer()
        assert opt.model == "claude-sonnet-4"

    def test_create_optimizer_custom_model(self):
        """커스텀 모델로 생성"""
        opt = DSPyOptimizer(model="claude-haiku-3")
        assert opt.model == "claude-haiku-3"

    def test_default_signatures_exist(self):
        """기본 Signature 존재 확인"""
        opt = DSPyOptimizer()
        assert 0 in opt.signatures
        assert 1 in opt.signatures
        assert 2 in opt.signatures

    def test_get_signature(self):
        """Signature 조회"""
        opt = DSPyOptimizer()
        sig = opt.get_signature(0)
        assert sig is not None
        assert sig.phase == 0

    def test_get_signature_not_found(self):
        """존재하지 않는 Signature"""
        opt = DSPyOptimizer()
        sig = opt.get_signature(999)
        assert sig is None

    def test_set_signature(self):
        """Signature 설정"""
        opt = DSPyOptimizer()
        new_sig = PhaseSignature(
            phase=5,
            input_fields=["test"],
            output_fields=["result"],
            instructions="new phase"
        )
        opt.set_signature(5, new_sig)
        assert opt.get_signature(5) == new_sig

    def test_add_example(self):
        """예시 추가"""
        opt = DSPyOptimizer()
        example = {"input": "test", "output": "pass"}
        result = opt.add_example(0, example)
        assert result is True
        assert example in opt.signatures[0].examples

    def test_add_example_invalid_phase(self):
        """존재하지 않는 Phase에 예시 추가"""
        opt = DSPyOptimizer()
        result = opt.add_example(999, {"test": "data"})
        assert result is False


class TestOptimization:
    """최적화 실행 테스트"""

    def test_optimize_success(self):
        """최적화 성공"""
        opt = DSPyOptimizer()
        training_data = [
            {"input": "PRD 1", "output": "valid"},
            {"input": "PRD 2", "output": "invalid"},
        ]
        result = opt.optimize(0, training_data)
        assert result.status == OptimizationStatus.COMPLETED
        assert result.optimized_score >= result.original_score

    def test_optimize_invalid_phase(self):
        """존재하지 않는 Phase 최적화"""
        opt = DSPyOptimizer()
        result = opt.optimize(999, [{"test": "data"}])
        assert result.status == OptimizationStatus.FAILED
        assert "Unknown phase" in result.error_message

    def test_optimize_no_training_data(self):
        """학습 데이터 없이 최적화"""
        opt = DSPyOptimizer()
        result = opt.optimize(0, [])
        assert result.status == OptimizationStatus.FAILED
        assert "No training data" in result.error_message

    def test_optimize_with_iterations(self):
        """반복 횟수 지정 최적화"""
        opt = DSPyOptimizer()
        training_data = [{"input": "test", "output": "pass"}]
        result = opt.optimize(0, training_data, num_iterations=20)
        assert result.iterations == 20
        assert result.improvement > 0

    def test_optimization_history(self):
        """최적화 히스토리"""
        opt = DSPyOptimizer()
        training_data = [{"input": "test", "output": "pass"}]
        opt.optimize(0, training_data)
        opt.optimize(1, training_data)
        history = opt.get_optimization_history()
        assert len(history) == 2


class TestOptimizationResult:
    """OptimizationResult 테스트"""

    def test_is_successful_true(self):
        """성공적인 최적화"""
        result = OptimizationResult(
            status=OptimizationStatus.COMPLETED,
            original_score=0.6,
            optimized_score=0.8,
            improvement=0.2
        )
        assert result.is_successful is True

    def test_is_successful_false_failed(self):
        """실패한 최적화"""
        result = OptimizationResult(
            status=OptimizationStatus.FAILED,
            original_score=0.6,
            optimized_score=0.6,
            improvement=0.0
        )
        assert result.is_successful is False

    def test_is_successful_false_no_improvement(self):
        """개선 없는 최적화"""
        result = OptimizationResult(
            status=OptimizationStatus.COMPLETED,
            original_score=0.6,
            optimized_score=0.6,
            improvement=0.0
        )
        assert result.is_successful is False


class TestPersistence:
    """저장/로드 테스트"""

    def test_save_and_load_signatures(self):
        """Signature 저장 및 로드"""
        opt = DSPyOptimizer()
        initial_examples = len(opt.signatures[0].examples)
        opt.add_example(0, {"test": "example"})

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            opt.save_signatures(temp_path)

            opt2 = DSPyOptimizer()
            opt2.signatures.clear()
            opt2.load_signatures(temp_path)

            assert 0 in opt2.signatures
            # 기본 예시 + 추가된 예시
            assert len(opt2.signatures[0].examples) == initial_examples + 1
        finally:
            os.unlink(temp_path)


class TestConvenienceFunctions:
    """편의 함수 테스트"""

    def test_create_optimizer_func(self):
        """create_optimizer 함수"""
        opt = create_optimizer("custom-model")
        assert opt.model == "custom-model"

    def test_optimize_phase_func(self):
        """optimize_phase 함수"""
        training_data = [{"input": "test", "output": "pass"}]
        result = optimize_phase(0, training_data)
        assert isinstance(result, OptimizationResult)
        assert result.status == OptimizationStatus.COMPLETED
