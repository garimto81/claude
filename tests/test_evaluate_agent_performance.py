#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for evaluate_agent_performance.py

Langfuse API 통합 테스트
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Optional, List

import pytest

# Mock langfuse before importing the module
sys.modules['langfuse'] = MagicMock()

# Add evolution scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "evolution" / "scripts"))


@dataclass
class MockTrace:
    """Mock Langfuse trace object"""
    id: str
    name: str
    output: Optional[dict] = None
    metadata: Optional[dict] = None


@dataclass
class MockScore:
    """Mock Langfuse score object"""
    name: str
    value: float


@dataclass
class MockResponse:
    """Mock Langfuse API response"""
    data: List


class TestPerformanceMetrics:
    """PerformanceMetrics 클래스 테스트"""

    def test_performance_score_calculation(self):
        """성능 점수 계산 테스트"""
        from evaluate_agent_performance import PerformanceMetrics

        metrics = PerformanceMetrics(
            agent_name="test-agent",
            total_runs=100,
            success_rate=0.95,
            avg_duration=1.5,
            error_rate=0.05,
            avg_user_rating=0.9,
            avg_effectiveness=0.85,
            improvement_suggestions_count=2
        )

        # 점수가 0-100 범위인지 확인
        assert 0 <= metrics.performance_score <= 100

        # 높은 성능 메트릭은 높은 점수를 반환해야 함
        assert metrics.performance_score >= 70

    def test_grade_assignment(self):
        """등급 할당 테스트"""
        from evaluate_agent_performance import PerformanceMetrics

        # 높은 성능
        high_metrics = PerformanceMetrics(
            agent_name="high-performer",
            total_runs=100,
            success_rate=0.98,
            avg_duration=1.0,
            error_rate=0.02,
            avg_user_rating=0.95,
            avg_effectiveness=0.95,
            improvement_suggestions_count=0
        )
        assert high_metrics.grade in ["S", "A"]

        # 낮은 성능
        low_metrics = PerformanceMetrics(
            agent_name="low-performer",
            total_runs=10,
            success_rate=0.3,
            avg_duration=10.0,
            error_rate=0.7,
            avg_user_rating=0.3,
            avg_effectiveness=0.3,
            improvement_suggestions_count=10
        )
        assert low_metrics.grade in ["D", "F"]

    def test_status_determination(self):
        """상태 판정 테스트"""
        from evaluate_agent_performance import PerformanceMetrics

        excellent = PerformanceMetrics(
            agent_name="excellent",
            total_runs=100,
            success_rate=0.95,
            avg_duration=1.0,
            error_rate=0.05,
            avg_user_rating=0.9,
            avg_effectiveness=0.9,
            improvement_suggestions_count=0
        )
        assert "Excellent" in excellent.status or "Good" in excellent.status


class TestAgentEvaluator:
    """AgentEvaluator 클래스 테스트"""

    @patch("evaluate_agent_performance.Langfuse")
    def test_get_agent_metrics_with_traces(self, mock_langfuse_class):
        """trace가 있을 때 메트릭 계산 테스트"""
        from evaluate_agent_performance import AgentEvaluator

        # Mock 설정
        mock_client = MagicMock()
        mock_langfuse_class.return_value = mock_client

        # Mock traces
        mock_traces = [
            MockTrace(
                id="trace-1",
                name="agent-test-agent",
                output={"status": "success", "duration_seconds": 1.5},
                metadata={"phase": "Phase 0", "agent": "test-agent"}
            ),
            MockTrace(
                id="trace-2",
                name="agent-test-agent",
                output={"status": "success", "duration_seconds": 2.0},
                metadata={"phase": "Phase 0", "agent": "test-agent"}
            ),
            MockTrace(
                id="trace-3",
                name="agent-test-agent",
                output={"status": "error", "duration_seconds": 3.0},
                metadata={"phase": "Phase 0", "agent": "test-agent"}
            ),
        ]

        mock_client.fetch_traces.return_value = MockResponse(data=mock_traces)
        mock_client.fetch_scores.return_value = MockResponse(data=[
            MockScore(name="user_rating", value=0.8),
            MockScore(name="effectiveness", value=0.85)
        ])

        evaluator = AgentEvaluator()
        metrics = evaluator.get_agent_metrics("test-agent", days=7)

        # 검증
        assert metrics.total_runs == 3
        assert metrics.success_rate == pytest.approx(2/3, rel=0.01)
        assert metrics.error_rate == pytest.approx(1/3, rel=0.01)
        assert metrics.avg_duration == pytest.approx((1.5 + 2.0 + 3.0) / 3, rel=0.01)

    @patch("evaluate_agent_performance.Langfuse")
    def test_get_agent_metrics_empty_traces(self, mock_langfuse_class):
        """trace가 없을 때 빈 메트릭 반환 테스트"""
        from evaluate_agent_performance import AgentEvaluator

        mock_client = MagicMock()
        mock_langfuse_class.return_value = mock_client
        mock_client.fetch_traces.return_value = MockResponse(data=[])

        evaluator = AgentEvaluator()
        metrics = evaluator.get_agent_metrics("nonexistent-agent", days=7)

        assert metrics.total_runs == 0
        assert metrics.success_rate == 0.0
        assert metrics.avg_duration == 0.0

    @patch("evaluate_agent_performance.Langfuse")
    def test_get_agent_metrics_api_error(self, mock_langfuse_class):
        """API 오류 시 빈 메트릭 반환 테스트"""
        from evaluate_agent_performance import AgentEvaluator

        mock_client = MagicMock()
        mock_langfuse_class.return_value = mock_client
        mock_client.fetch_traces.side_effect = Exception("API Error")

        evaluator = AgentEvaluator()
        metrics = evaluator.get_agent_metrics("test-agent", days=7)

        assert metrics.total_runs == 0

    @patch("evaluate_agent_performance.Langfuse")
    def test_get_agent_metrics_with_phase_filter(self, mock_langfuse_class):
        """phase 필터 적용 테스트"""
        from evaluate_agent_performance import AgentEvaluator

        mock_client = MagicMock()
        mock_langfuse_class.return_value = mock_client

        # 다양한 phase의 traces
        mock_traces = [
            MockTrace(
                id="trace-1",
                name="agent-test",
                output={"status": "success", "duration_seconds": 1.0},
                metadata={"phase": "Phase 0"}
            ),
            MockTrace(
                id="trace-2",
                name="agent-test",
                output={"status": "success", "duration_seconds": 2.0},
                metadata={"phase": "Phase 1"}
            ),
            MockTrace(
                id="trace-3",
                name="agent-test",
                output={"status": "success", "duration_seconds": 1.5},
                metadata={"phase": "Phase 0"}
            ),
        ]

        mock_client.fetch_traces.return_value = MockResponse(data=mock_traces)
        mock_client.fetch_scores.return_value = MockResponse(data=[])

        evaluator = AgentEvaluator()
        metrics = evaluator.get_agent_metrics("test", days=7, phase="Phase 0")

        # Phase 0 trace만 포함되어야 함
        assert metrics.total_runs == 2

    @patch("evaluate_agent_performance.Langfuse")
    def test_get_trace_scores(self, mock_langfuse_class):
        """_get_trace_scores 헬퍼 메서드 테스트"""
        from evaluate_agent_performance import AgentEvaluator

        mock_client = MagicMock()
        mock_langfuse_class.return_value = mock_client

        mock_scores = [
            MockScore(name="user_rating", value=0.8),
            MockScore(name="effectiveness", value=0.9)
        ]
        mock_client.fetch_scores.return_value = MockResponse(data=mock_scores)

        evaluator = AgentEvaluator()
        scores = evaluator._get_trace_scores("trace-123")

        assert len(scores) == 2
        mock_client.fetch_scores.assert_called_once_with(trace_id="trace-123")

    @patch("evaluate_agent_performance.Langfuse")
    def test_compare_agents(self, mock_langfuse_class):
        """Agent 비교 테스트"""
        from evaluate_agent_performance import AgentEvaluator

        mock_client = MagicMock()
        mock_langfuse_class.return_value = mock_client

        # 빈 traces 반환 (단순화)
        mock_client.fetch_traces.return_value = MockResponse(data=[])

        evaluator = AgentEvaluator()
        result = evaluator.compare_agents(["agent-a", "agent-b"])

        assert "agents" in result
        assert "ranking" in result
        assert "best" in result
        assert "worst" in result


class TestP95Duration:
    """P95 duration 계산 테스트"""

    @patch("evaluate_agent_performance.Langfuse")
    def test_p95_calculation(self, mock_langfuse_class):
        """P95 duration 정확히 계산되는지 테스트"""
        from evaluate_agent_performance import AgentEvaluator

        mock_client = MagicMock()
        mock_langfuse_class.return_value = mock_client

        # 100개의 traces (1.0초 ~ 100.0초)
        mock_traces = [
            MockTrace(
                id=f"trace-{i}",
                name="agent-test",
                output={"status": "success", "duration_seconds": float(i)},
                metadata={}
            )
            for i in range(1, 101)
        ]

        mock_client.fetch_traces.return_value = MockResponse(data=mock_traces)
        mock_client.fetch_scores.return_value = MockResponse(data=[])

        evaluator = AgentEvaluator()
        metrics = evaluator.get_agent_metrics("test", days=7)

        # P95 = 95번째 값 (95.0)
        assert metrics.p95_duration == pytest.approx(95.0, rel=0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
