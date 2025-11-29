# tests/prompt_learning/test_failure_analyzer.py
"""
Failure Analyzer 테스트

pytest tests/prompt_learning/test_failure_analyzer.py -v
"""

import pytest
import sys
import os

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.failure_analyzer import (
    FailureAnalyzer,
    FailureAnalysis,
    FailureCause,
    FailureCategory,
)
from prompt_learning.session_parser import SessionEvent, EventType


class TestFailureCause:
    """FailureCause 테스트"""

    def test_create_cause(self):
        """원인 생성"""
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="파일을 찾을 수 없음",
            evidence="FileNotFoundError: /path/to/file",
            confidence=0.8,
            suggestion="경로를 확인하세요"
        )
        assert cause.category == FailureCategory.PATH_ERROR
        assert cause.confidence == 0.8


class TestFailureAnalysis:
    """FailureAnalysis 테스트"""

    def test_primary_cause_empty(self):
        """원인이 없을 때"""
        analysis = FailureAnalysis(
            session_id="test-1",
            causes=[],
            severity="low"
        )
        assert analysis.primary_cause is None

    def test_primary_cause_single(self):
        """단일 원인"""
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="test",
            evidence="test",
            confidence=0.9
        )
        analysis = FailureAnalysis(
            session_id="test-1",
            causes=[cause],
            severity="medium"
        )
        assert analysis.primary_cause == cause

    def test_primary_cause_multiple(self):
        """여러 원인 중 가장 높은 신뢰도"""
        cause1 = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="test1",
            evidence="test1",
            confidence=0.5
        )
        cause2 = FailureCause(
            category=FailureCategory.TOOL_ERROR,
            description="test2",
            evidence="test2",
            confidence=0.9
        )
        analysis = FailureAnalysis(
            session_id="test-1",
            causes=[cause1, cause2],
            severity="high"
        )
        assert analysis.primary_cause == cause2

    def test_to_dict(self):
        """딕셔너리 변환"""
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="test",
            evidence="test",
            confidence=0.8
        )
        analysis = FailureAnalysis(
            session_id="test-1",
            causes=[cause],
            severity="medium",
            affected_phase=1,
            recommendations=["Fix the path"]
        )
        d = analysis.to_dict()
        assert d["session_id"] == "test-1"
        assert len(d["causes"]) == 1
        assert d["severity"] == "medium"


class TestFailureAnalyzer:
    """FailureAnalyzer 테스트"""

    def test_create_analyzer(self):
        """분석기 생성"""
        analyzer = FailureAnalyzer()
        assert analyzer._analysis_history == []

    def test_analyze_empty_events(self):
        """빈 이벤트 분석"""
        analyzer = FailureAnalyzer()
        analysis = analyzer.analyze_session("test-1", [])
        assert analysis.session_id == "test-1"
        assert len(analysis.causes) == 0
        assert analysis.severity == "low"

    def test_analyze_path_error(self):
        """경로 오류 분석"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={"message": "FileNotFoundError: /path/to/file"},
            error="FileNotFoundError: /path/to/file"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert any(c.category == FailureCategory.PATH_ERROR for c in analysis.causes)

    def test_analyze_phase_violation(self):
        """Phase 위반 분석"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={},
            error="phase 3 validation fail"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert any(c.category == FailureCategory.PHASE_VIOLATION for c in analysis.causes)
        assert analysis.severity == "critical"

    def test_analyze_validation_skip(self):
        """검증 스킵 분석"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={},
            error="skip validation requested"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert any(c.category == FailureCategory.VALIDATION_SKIP for c in analysis.causes)

    def test_analyze_tdd_violation(self):
        """TDD 위반 분석"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={},
            error="구현 먼저 하고 테스트 나중에"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert any(c.category == FailureCategory.TDD_VIOLATION for c in analysis.causes)

    def test_analyze_tool_failure(self):
        """도구 실패 분석"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.TOOL_RESULT,
            content={"error": "command failed"},
            tool_name="Bash",
            success=False
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert any(c.category == FailureCategory.TOOL_ERROR for c in analysis.causes)

    def test_analyze_timeout(self):
        """타임아웃 분석"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={},
            error="Operation timed out"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert any(c.category == FailureCategory.TIMEOUT for c in analysis.causes)

    def test_analyze_permission_denied(self):
        """권한 오류 분석"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={},
            error="Permission denied: /etc/passwd"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert any(c.category == FailureCategory.PERMISSION_DENIED for c in analysis.causes)


class TestSeverity:
    """심각도 테스트"""

    def test_severity_low(self):
        """낮은 심각도"""
        analyzer = FailureAnalyzer()
        analysis = analyzer.analyze_session("test-1", [])
        assert analysis.severity == "low"

    def test_severity_critical_phase(self):
        """Phase 위반은 critical"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={},
            error="phase validation fail"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert analysis.severity == "critical"

    def test_severity_high_tdd(self):
        """TDD 위반은 high"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={},
            error="implement first without test"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert analysis.severity in ["high", "critical"]


class TestRecommendations:
    """권장 사항 테스트"""

    def test_recommendations_path_error(self):
        """경로 오류 권장 사항"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={},
            error="FileNotFoundError"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert len(analysis.recommendations) > 0

    def test_recommendations_tdd(self):
        """TDD 위반 권장 사항"""
        analyzer = FailureAnalyzer()
        event = SessionEvent(
            timestamp="2024-01-01T00:00:00Z",
            event_type=EventType.ERROR,
            content={},
            error="implement first test later"
        )
        analysis = analyzer.analyze_session("test-1", [event])
        assert any("/tdd" in r for r in analysis.recommendations)


class TestHistory:
    """히스토리 테스트"""

    def test_get_analysis_history(self):
        """분석 히스토리"""
        analyzer = FailureAnalyzer()
        analyzer.analyze_session("test-1", [])
        analyzer.analyze_session("test-2", [])
        history = analyzer.get_analysis_history()
        assert len(history) == 2

    def test_get_common_failures(self):
        """공통 실패 집계"""
        analyzer = FailureAnalyzer()
        event1 = SessionEvent(
            timestamp="",
            event_type=EventType.ERROR,
            content={},
            error="FileNotFoundError"
        )
        event2 = SessionEvent(
            timestamp="",
            event_type=EventType.ERROR,
            content={},
            error="FileNotFoundError again"
        )
        analyzer.analyze_session("test-1", [event1])
        analyzer.analyze_session("test-2", [event2])
        common = analyzer.get_common_failures()
        assert FailureCategory.PATH_ERROR in common
        assert common[FailureCategory.PATH_ERROR] >= 2
