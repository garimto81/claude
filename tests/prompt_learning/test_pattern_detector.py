# tests/prompt_learning/test_pattern_detector.py
"""
Pattern Detector 테스트

pytest tests/prompt_learning/test_pattern_detector.py -v
"""

import pytest
import sys
import os

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.pattern_detector import (
    PatternDetector,
    Pattern,
    PatternReport,
    detect_patterns_from_analyses,
)
from prompt_learning.failure_analyzer import FailureAnalysis, FailureCause, FailureCategory


class TestPattern:
    """Pattern 테스트"""

    def test_create_pattern(self):
        """패턴 생성"""
        pattern = Pattern(
            pattern_id="test-pattern",
            category=FailureCategory.PATH_ERROR,
            description="파일 경로 오류",
            occurrence_count=5,
            first_seen="2024-01-01T00:00:00",
            last_seen="2024-01-05T00:00:00",
            affected_sessions=["s1", "s2", "s3", "s4", "s5"],
            trend="increasing"
        )
        assert pattern.pattern_id == "test-pattern"
        assert pattern.occurrence_count == 5

    def test_is_critical_high_count(self):
        """높은 발생 횟수는 critical"""
        pattern = Pattern(
            pattern_id="test",
            category=FailureCategory.TOOL_ERROR,
            description="test",
            occurrence_count=5,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        assert pattern.is_critical is True

    def test_is_critical_phase_violation(self):
        """Phase 위반은 항상 critical"""
        pattern = Pattern(
            pattern_id="test",
            category=FailureCategory.PHASE_VIOLATION,
            description="test",
            occurrence_count=2,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        assert pattern.is_critical is True

    def test_is_critical_false(self):
        """낮은 발생 횟수는 not critical"""
        pattern = Pattern(
            pattern_id="test",
            category=FailureCategory.TOOL_ERROR,
            description="test",
            occurrence_count=2,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        assert pattern.is_critical is False

    def test_to_dict(self):
        """딕셔너리 변환"""
        pattern = Pattern(
            pattern_id="test",
            category=FailureCategory.PATH_ERROR,
            description="test desc",
            occurrence_count=3,
            first_seen="2024-01-01",
            last_seen="2024-01-03",
            affected_sessions=["s1", "s2", "s3"],
            trend="stable"
        )
        d = pattern.to_dict()
        assert d["pattern_id"] == "test"
        assert d["category"] == "path_error"


class TestPatternReport:
    """PatternReport 테스트"""

    def test_to_markdown_empty(self):
        """빈 리포트 마크다운"""
        report = PatternReport(
            total_patterns=0,
            critical_patterns=0,
            patterns=[],
            recommendations=[]
        )
        md = report.to_markdown()
        assert "# 반복 패턴 분석 리포트" in md
        assert "총 패턴: 0개" in md

    def test_to_markdown_with_patterns(self):
        """패턴이 있는 리포트"""
        pattern = Pattern(
            pattern_id="test",
            category=FailureCategory.PATH_ERROR,
            description="경로 오류",
            occurrence_count=3,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        report = PatternReport(
            total_patterns=1,
            critical_patterns=0,
            patterns=[pattern],
            recommendations=["경로를 확인하세요"]
        )
        md = report.to_markdown()
        assert "path_error" in md
        assert "경로 오류" in md
        assert "권장 사항" in md


class TestPatternDetector:
    """PatternDetector 테스트"""

    def test_create_detector(self):
        """감지기 생성"""
        detector = PatternDetector()
        assert detector.min_occurrences == 2

    def test_create_detector_custom_min(self):
        """커스텀 최소 발생 횟수"""
        detector = PatternDetector(min_occurrences=5)
        assert detector.min_occurrences == 5

    def test_add_analysis(self):
        """분석 추가"""
        detector = PatternDetector()
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="test",
            evidence="test",
            confidence=0.8
        )
        analysis = FailureAnalysis(
            session_id="test-1",
            causes=[cause],
            severity="medium"
        )
        detector.add_analysis(analysis)
        # 내부 상태 확인
        assert len(detector._pattern_counts) == 1

    def test_detect_patterns_below_threshold(self):
        """최소 발생 미만"""
        detector = PatternDetector(min_occurrences=2)
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="test",
            evidence="test",
            confidence=0.8
        )
        analysis = FailureAnalysis(
            session_id="test-1",
            causes=[cause],
            severity="medium"
        )
        detector.add_analysis(analysis)
        patterns = detector.detect_patterns()
        assert len(patterns) == 0

    def test_detect_patterns_above_threshold(self):
        """최소 발생 이상"""
        detector = PatternDetector(min_occurrences=2)
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="파일 없음",
            evidence="test",
            confidence=0.8
        )

        for i in range(3):
            analysis = FailureAnalysis(
                session_id=f"test-{i}",
                causes=[cause],
                severity="medium"
            )
            detector.add_analysis(analysis)

        patterns = detector.detect_patterns()
        assert len(patterns) == 1
        assert patterns[0].occurrence_count == 3

    def test_detect_multiple_patterns(self):
        """여러 패턴 감지"""
        detector = PatternDetector(min_occurrences=2)

        path_cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="path error",
            evidence="test",
            confidence=0.8
        )
        tool_cause = FailureCause(
            category=FailureCategory.TOOL_ERROR,
            description="tool error",
            evidence="test",
            confidence=0.8
        )

        for i in range(2):
            detector.add_analysis(FailureAnalysis(
                session_id=f"path-{i}",
                causes=[path_cause],
                severity="medium"
            ))
            detector.add_analysis(FailureAnalysis(
                session_id=f"tool-{i}",
                causes=[tool_cause],
                severity="medium"
            ))

        patterns = detector.detect_patterns()
        assert len(patterns) == 2


class TestTrend:
    """추세 계산 테스트"""

    def test_trend_stable_few_sessions(self):
        """세션 수가 적으면 stable"""
        detector = PatternDetector(min_occurrences=2)
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="test",
            evidence="test",
            confidence=0.8
        )

        for i in range(2):
            detector.add_analysis(FailureAnalysis(
                session_id=f"test-{i}",
                causes=[cause],
                severity="medium"
            ))

        patterns = detector.detect_patterns()
        assert patterns[0].trend == "stable"


class TestGenerateReport:
    """리포트 생성 테스트"""

    def test_generate_report_empty(self):
        """빈 리포트"""
        detector = PatternDetector()
        report = detector.generate_report()
        assert report.total_patterns == 0
        assert report.critical_patterns == 0

    def test_generate_report_with_patterns(self):
        """패턴이 있는 리포트"""
        detector = PatternDetector(min_occurrences=2)
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="test",
            evidence="test",
            confidence=0.8
        )

        for i in range(3):
            detector.add_analysis(FailureAnalysis(
                session_id=f"test-{i}",
                causes=[cause],
                severity="medium"
            ))

        report = detector.generate_report()
        assert report.total_patterns == 1
        assert len(report.recommendations) > 0


class TestCriticalPatterns:
    """Critical 패턴 테스트"""

    def test_get_critical_patterns(self):
        """Critical 패턴 조회"""
        detector = PatternDetector(min_occurrences=2)
        critical_cause = FailureCause(
            category=FailureCategory.PHASE_VIOLATION,
            description="phase error",
            evidence="test",
            confidence=0.8
        )
        normal_cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="path error",
            evidence="test",
            confidence=0.8
        )

        for i in range(2):
            detector.add_analysis(FailureAnalysis(
                session_id=f"critical-{i}",
                causes=[critical_cause],
                severity="critical"
            ))
            detector.add_analysis(FailureAnalysis(
                session_id=f"normal-{i}",
                causes=[normal_cause],
                severity="medium"
            ))

        critical = detector.get_critical_patterns()
        assert len(critical) == 1
        assert critical[0].category == FailureCategory.PHASE_VIOLATION


class TestPatternByCategory:
    """카테고리별 패턴 테스트"""

    def test_get_pattern_by_category(self):
        """카테고리별 조회"""
        detector = PatternDetector(min_occurrences=2)
        path_cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="path",
            evidence="test",
            confidence=0.8
        )

        for i in range(2):
            detector.add_analysis(FailureAnalysis(
                session_id=f"test-{i}",
                causes=[path_cause],
                severity="medium"
            ))

        patterns = detector.get_pattern_by_category(FailureCategory.PATH_ERROR)
        assert len(patterns) == 1

        patterns = detector.get_pattern_by_category(FailureCategory.TOOL_ERROR)
        assert len(patterns) == 0


class TestReset:
    """초기화 테스트"""

    def test_reset(self):
        """데이터 초기화"""
        detector = PatternDetector(min_occurrences=1)
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="test",
            evidence="test",
            confidence=0.8
        )
        detector.add_analysis(FailureAnalysis(
            session_id="test",
            causes=[cause],
            severity="medium"
        ))

        assert len(detector.detect_patterns()) == 1
        detector.reset()
        assert len(detector.detect_patterns()) == 0


class TestConvenienceFunction:
    """편의 함수 테스트"""

    def test_detect_patterns_from_analyses(self):
        """detect_patterns_from_analyses 함수"""
        cause = FailureCause(
            category=FailureCategory.PATH_ERROR,
            description="test",
            evidence="test",
            confidence=0.8
        )
        analyses = [
            FailureAnalysis(session_id="s1", causes=[cause], severity="medium"),
            FailureAnalysis(session_id="s2", causes=[cause], severity="medium"),
            FailureAnalysis(session_id="s3", causes=[cause], severity="medium"),
        ]
        report = detect_patterns_from_analyses(analyses, min_occurrences=2)
        assert report.total_patterns == 1
