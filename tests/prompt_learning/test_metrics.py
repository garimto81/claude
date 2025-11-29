# tests/prompt_learning/test_metrics.py
"""
Metrics 테스트

pytest tests/prompt_learning/test_metrics.py -v
"""

import pytest
import tempfile
import os
import sys
import json

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.metrics import (
    MetricsCollector,
    PhaseMetrics,
    SessionMetrics,
    PromptLearningMetrics,
    get_collector,
    reset_collector,
)


class TestPhaseMetrics:
    """PhaseMetrics 테스트"""

    def test_create_phase_metrics(self):
        """Phase 메트릭스 생성"""
        pm = PhaseMetrics(
            phase=0,
            attempts=10,
            successes=8,
            failures=2
        )
        assert pm.phase == 0
        assert pm.attempts == 10

    def test_success_rate(self):
        """성공률 계산"""
        pm = PhaseMetrics(phase=0, attempts=10, successes=8, failures=2)
        assert pm.success_rate == 0.8

    def test_success_rate_zero_attempts(self):
        """시도 없을 때 성공률"""
        pm = PhaseMetrics(phase=0)
        assert pm.success_rate == 0.0

    def test_failure_rate(self):
        """실패율 계산"""
        pm = PhaseMetrics(phase=0, attempts=10, successes=8, failures=2)
        assert pm.failure_rate == 0.2

    def test_to_dict(self):
        """딕셔너리 변환"""
        pm = PhaseMetrics(phase=1, attempts=5, successes=4, failures=1)
        d = pm.to_dict()
        assert d["phase"] == 1
        assert d["success_rate"] == 0.8


class TestSessionMetrics:
    """SessionMetrics 테스트"""

    def test_create_session_metrics(self):
        """세션 메트릭스 생성"""
        sm = SessionMetrics(
            session_id="test-1",
            start_time="2024-01-01T00:00:00"
        )
        assert sm.session_id == "test-1"
        assert sm.success is False

    def test_to_dict(self):
        """딕셔너리 변환"""
        sm = SessionMetrics(
            session_id="test-1",
            start_time="2024-01-01T00:00:00",
            end_time="2024-01-01T00:05:00",
            duration_seconds=300,
            token_usage=1000,
            success=True
        )
        d = sm.to_dict()
        assert d["session_id"] == "test-1"
        assert d["success"] is True


class TestPromptLearningMetrics:
    """PromptLearningMetrics 테스트"""

    def test_create_metrics(self):
        """메트릭스 생성"""
        metrics = PromptLearningMetrics()
        assert metrics.total_sessions == 0

    def test_overall_success_rate(self):
        """전체 성공률"""
        metrics = PromptLearningMetrics(
            total_sessions=10,
            successful_sessions=7,
            failed_sessions=3
        )
        assert metrics.overall_success_rate == 0.7

    def test_overall_success_rate_zero(self):
        """세션 없을 때 성공률"""
        metrics = PromptLearningMetrics()
        assert metrics.overall_success_rate == 0.0

    def test_to_dict(self):
        """딕셔너리 변환"""
        metrics = PromptLearningMetrics(
            total_sessions=5,
            successful_sessions=4,
            failed_sessions=1,
            total_tokens=5000
        )
        d = metrics.to_dict()
        assert d["total_sessions"] == 5
        assert d["overall_success_rate"] == 0.8

    def test_to_markdown(self):
        """마크다운 변환"""
        metrics = PromptLearningMetrics(
            total_sessions=10,
            successful_sessions=8,
            failed_sessions=2,
            total_tokens=10000,
            avg_session_duration=120.0
        )
        md = metrics.to_markdown()
        assert "# Prompt Learning 메트릭스 리포트" in md
        assert "총 세션: 10개" in md
        assert "80.0%" in md


class TestMetricsCollector:
    """MetricsCollector 테스트"""

    def test_create_collector(self):
        """수집기 생성"""
        collector = MetricsCollector()
        assert len(collector._sessions) == 0

    def test_start_session(self):
        """세션 시작"""
        collector = MetricsCollector()
        session = collector.start_session("test-1")
        assert session.session_id == "test-1"
        assert session.start_time is not None

    def test_end_session(self):
        """세션 종료"""
        collector = MetricsCollector()
        collector.start_session("test-1")
        session = collector.end_session("test-1", success=True, token_usage=1000)
        assert session is not None
        assert session.success is True
        assert session.token_usage == 1000
        assert session.end_time is not None

    def test_end_session_not_found(self):
        """존재하지 않는 세션 종료"""
        collector = MetricsCollector()
        result = collector.end_session("nonexistent", success=True)
        assert result is None

    def test_record_phase_attempt(self):
        """Phase 시도 기록"""
        collector = MetricsCollector()
        collector.start_session("test-1")
        collector.record_phase_attempt("test-1", phase=0, success=True)
        collector.record_phase_attempt("test-1", phase=1, success=False)

        session = collector.get_session("test-1")
        assert 0 in session.phases_completed
        assert 1 not in session.phases_completed
        assert session.errors_count == 1

    def test_record_error(self):
        """에러 기록"""
        collector = MetricsCollector()
        collector.start_session("test-1")
        collector.record_error("test-1")
        collector.record_error("test-1")

        session = collector.get_session("test-1")
        assert session.errors_count == 2


class TestGetMetrics:
    """메트릭스 조회 테스트"""

    def test_get_metrics_empty(self):
        """빈 메트릭스"""
        collector = MetricsCollector()
        metrics = collector.get_metrics()
        assert metrics.total_sessions == 0

    def test_get_metrics_with_sessions(self):
        """세션이 있는 메트릭스"""
        collector = MetricsCollector()

        collector.start_session("test-1")
        collector.record_phase_attempt("test-1", 0, True)
        collector.end_session("test-1", success=True, token_usage=1000)

        collector.start_session("test-2")
        collector.record_phase_attempt("test-2", 0, False)
        collector.end_session("test-2", success=False, token_usage=500)

        metrics = collector.get_metrics()
        assert metrics.total_sessions == 2
        assert metrics.successful_sessions == 1
        assert metrics.failed_sessions == 1
        assert metrics.total_tokens == 1500

    def test_get_session(self):
        """세션 조회"""
        collector = MetricsCollector()
        collector.start_session("test-1")
        session = collector.get_session("test-1")
        assert session is not None
        assert session.session_id == "test-1"

    def test_get_session_not_found(self):
        """존재하지 않는 세션 조회"""
        collector = MetricsCollector()
        session = collector.get_session("nonexistent")
        assert session is None

    def test_get_phase_metrics(self):
        """Phase 메트릭스 조회"""
        collector = MetricsCollector()
        collector.start_session("test-1")
        collector.record_phase_attempt("test-1", 0, True)
        collector.record_phase_attempt("test-1", 0, True)
        collector.record_phase_attempt("test-1", 0, False)

        pm = collector.get_phase_metrics(0)
        assert pm is not None
        assert pm.attempts == 3
        assert pm.successes == 2

    def test_get_phase_metrics_not_found(self):
        """존재하지 않는 Phase 메트릭스"""
        collector = MetricsCollector()
        pm = collector.get_phase_metrics(999)
        assert pm is None


class TestExport:
    """내보내기 테스트"""

    def test_export_json(self):
        """JSON 내보내기"""
        collector = MetricsCollector()
        collector.start_session("test-1")
        collector.record_phase_attempt("test-1", 0, True)
        collector.end_session("test-1", success=True)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            collector.export_json(temp_path)

            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            assert "sessions" in data
            assert "metrics" in data
            assert "test-1" in data["sessions"]
        finally:
            os.unlink(temp_path)


class TestReset:
    """초기화 테스트"""

    def test_reset(self):
        """데이터 초기화"""
        collector = MetricsCollector()
        collector.start_session("test-1")
        collector.record_phase_attempt("test-1", 0, True)

        collector.reset()

        assert len(collector._sessions) == 0
        assert len(collector._phase_data) == 0


class TestGlobalCollector:
    """전역 수집기 테스트"""

    def test_get_collector(self):
        """전역 수집기 조회"""
        reset_collector()
        collector1 = get_collector()
        collector2 = get_collector()
        assert collector1 is collector2

    def test_reset_collector(self):
        """전역 수집기 초기화"""
        collector1 = get_collector()
        reset_collector()
        collector2 = get_collector()
        assert collector1 is not collector2
