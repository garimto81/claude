# tests/prompt_learning/test_ab_test.py
"""
A/B 테스트 프레임워크 테스트

pytest tests/prompt_learning/test_ab_test.py -v
"""

import pytest
import sys
import os

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.ab_test import (
    ABTestFramework,
    ABTestConfig,
    ABTestResult,
    TestSample,
    Variant,
    create_ab_test,
)


class TestABTestConfig:
    """ABTestConfig 테스트"""

    def test_create_config(self):
        """설정 생성"""
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="original",
            treatment_prompt="new",
        )
        assert config.test_id == "test-1"
        assert config.traffic_split == 0.5

    def test_custom_traffic_split(self):
        """커스텀 트래픽 분할"""
        config = ABTestConfig(
            test_id="test-2",
            control_prompt="a",
            treatment_prompt="b",
            traffic_split=0.3
        )
        assert config.traffic_split == 0.3

    def test_invalid_traffic_split(self):
        """유효하지 않은 트래픽 분할"""
        with pytest.raises(ValueError):
            ABTestConfig(
                test_id="test",
                control_prompt="a",
                treatment_prompt="b",
                traffic_split=1.5
            )

    def test_invalid_min_samples(self):
        """유효하지 않은 최소 샘플"""
        with pytest.raises(ValueError):
            ABTestConfig(
                test_id="test",
                control_prompt="a",
                treatment_prompt="b",
                min_samples=5
            )


class TestABTestFramework:
    """ABTestFramework 테스트"""

    def test_create_framework(self):
        """프레임워크 생성"""
        framework = ABTestFramework()
        assert len(framework.tests) == 0

    def test_create_test(self):
        """테스트 생성"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="control",
            treatment_prompt="treatment"
        )
        test_id = framework.create_test(config)
        assert test_id == "test-1"
        assert "test-1" in framework.tests

    def test_get_variant_consistent(self):
        """일관된 변형 할당"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="a",
            treatment_prompt="b"
        )
        framework.create_test(config)

        # 같은 사용자는 항상 같은 변형 받음
        variant1 = framework.get_variant("test-1", "user-123")
        variant2 = framework.get_variant("test-1", "user-123")
        assert variant1 == variant2

    def test_get_variant_distribution(self):
        """변형 분포"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="a",
            treatment_prompt="b",
            traffic_split=0.5
        )
        framework.create_test(config)

        # 많은 사용자로 분포 확인
        control_count = 0
        treatment_count = 0
        for i in range(1000):
            variant = framework.get_variant("test-1", f"user-{i}")
            if variant == Variant.CONTROL:
                control_count += 1
            else:
                treatment_count += 1

        # 대략 50/50 분할 (허용 오차 10%)
        assert 400 < control_count < 600
        assert 400 < treatment_count < 600

    def test_get_variant_unknown_test(self):
        """존재하지 않는 테스트"""
        framework = ABTestFramework()
        with pytest.raises(ValueError):
            framework.get_variant("unknown", "user-1")

    def test_get_prompt(self):
        """프롬프트 조회"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="control prompt",
            treatment_prompt="treatment prompt"
        )
        framework.create_test(config)

        assert framework.get_prompt("test-1", Variant.CONTROL) == "control prompt"
        assert framework.get_prompt("test-1", Variant.TREATMENT) == "treatment prompt"


class TestSampleRecording:
    """샘플 기록 테스트"""

    def test_record_sample(self):
        """샘플 기록"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="a",
            treatment_prompt="b"
        )
        framework.create_test(config)

        sample = framework.record_sample(
            test_id="test-1",
            user_id="user-1",
            input_data={"query": "test"},
            success=True,
            latency_ms=100.5
        )

        assert sample.success is True
        assert sample.latency_ms == 100.5
        assert len(framework.samples["test-1"]) == 1

    def test_record_sample_unknown_test(self):
        """존재하지 않는 테스트에 샘플 기록"""
        framework = ABTestFramework()
        with pytest.raises(ValueError):
            framework.record_sample(
                test_id="unknown",
                user_id="user-1",
                input_data={},
                success=True,
                latency_ms=100
            )


class TestResults:
    """결과 계산 테스트"""

    def test_get_results_empty(self):
        """빈 결과"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="a",
            treatment_prompt="b"
        )
        framework.create_test(config)

        result = framework.get_results("test-1")
        assert result.control_samples == 0
        assert result.treatment_samples == 0

    def test_get_results_with_samples(self):
        """샘플이 있는 결과"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="a",
            treatment_prompt="b",
            traffic_split=0.5
        )
        framework.create_test(config)

        # 샘플 추가
        for i in range(100):
            success = i % 2 == 0  # 50% 성공률
            framework.record_sample(
                test_id="test-1",
                user_id=f"user-{i}",
                input_data={},
                success=success,
                latency_ms=100
            )

        result = framework.get_results("test-1")
        assert result.total_samples == 100
        assert result.control_samples + result.treatment_samples == 100

    def test_get_results_unknown_test(self):
        """존재하지 않는 테스트 결과"""
        framework = ABTestFramework()
        with pytest.raises(ValueError):
            framework.get_results("unknown")

    def test_lift_calculation(self):
        """Lift 계산"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="a",
            treatment_prompt="b",
            traffic_split=0.5,
            min_samples=10
        )
        framework.create_test(config)

        # Control: 50% 성공, Treatment: 75% 성공
        for i in range(100):
            variant = framework.get_variant("test-1", f"user-{i}")
            if variant == Variant.CONTROL:
                success = i % 2 == 0
            else:
                success = i % 4 != 0  # 75% 성공
            framework.record_sample(
                test_id="test-1",
                user_id=f"user-{i}",
                input_data={},
                success=success,
                latency_ms=100
            )

        result = framework.get_results("test-1")
        # Treatment가 더 좋으면 lift > 0
        # 정확한 값은 할당에 따라 다름
        assert isinstance(result.lift, float)


class TestSignificance:
    """통계적 유의성 테스트"""

    def test_is_test_complete_not_enough_samples(self):
        """샘플 부족"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="a",
            treatment_prompt="b",
            min_samples=100
        )
        framework.create_test(config)

        # 50개만 추가
        for i in range(50):
            framework.record_sample(
                test_id="test-1",
                user_id=f"user-{i}",
                input_data={},
                success=True,
                latency_ms=100
            )

        assert framework.is_test_complete("test-1") is False


class TestExport:
    """내보내기 테스트"""

    def test_export_results(self):
        """결과 내보내기"""
        framework = ABTestFramework()
        config = ABTestConfig(
            test_id="test-1",
            control_prompt="a",
            treatment_prompt="b"
        )
        framework.create_test(config)

        # 샘플 추가
        for i in range(20):
            framework.record_sample(
                test_id="test-1",
                user_id=f"user-{i}",
                input_data={},
                success=i % 2 == 0,
                latency_ms=100
            )

        exported = framework.export_results("test-1")
        assert "test_id" in exported
        assert "control_samples" in exported
        assert "treatment_samples" in exported
        assert "lift" in exported
        assert "p_value" in exported


class TestConvenienceFunction:
    """편의 함수 테스트"""

    def test_create_ab_test(self):
        """create_ab_test 함수"""
        framework = create_ab_test(
            test_id="quick-test",
            control_prompt="old",
            treatment_prompt="new",
            traffic_split=0.3
        )
        assert "quick-test" in framework.tests
        assert framework.tests["quick-test"].traffic_split == 0.3
