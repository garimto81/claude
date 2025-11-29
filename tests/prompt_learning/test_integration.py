# tests/prompt_learning/test_integration.py
"""
Prompt Learning 시스템 통합 테스트 (E2E)

pytest tests/prompt_learning/test_integration.py -v
"""

import pytest
import sys
import os
from pathlib import Path

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.session_parser import SessionParser
from prompt_learning.failure_analyzer import FailureAnalyzer, FailureCategory
from prompt_learning.pattern_detector import PatternDetector
from prompt_learning.claude_md_updater import ClaudeMDUpdater
from prompt_learning.metrics import MetricsCollector, get_collector, reset_collector
from prompt_learning.dspy_optimizer import DSPyOptimizer
from prompt_learning.textgrad_optimizer import TextGradOptimizer
from prompt_learning.ab_test import ABTestFramework, ABTestConfig, Variant


class TestFullPipeline:
    """전체 Prompt Learning 파이프라인 통합 테스트"""

    def test_session_to_pattern_detection(self, sample_error_session_log):
        """세션 파싱 → 실패 분석 → 패턴 감지"""
        # 1. 세션 파싱
        parser = SessionParser()
        events = parser.parse_string(sample_error_session_log)
        assert len(events) == 4

        # 2. 실패 분석
        analyzer = FailureAnalyzer()
        analysis1 = analyzer.analyze_session("session-1", events)
        assert len(analysis1.causes) > 0
        assert any(c.category == FailureCategory.PATH_ERROR for c in analysis1.causes)

        # 3. 패턴 감지 (2회 필요)
        detector = PatternDetector(min_occurrences=2)
        detector.add_analysis(analysis1)

        # 두 번째 세션 (동일 오류)
        analysis2 = analyzer.analyze_session("session-2", events)
        detector.add_analysis(analysis2)

        patterns = detector.detect_patterns()
        assert len(patterns) >= 1
        assert any(p.category == FailureCategory.PATH_ERROR for p in patterns)

    def test_pattern_to_claude_md_update(self, temp_dir, sample_pattern, sample_claude_md_content):
        """패턴 감지 → CLAUDE.md 업데이트 제안"""
        # CLAUDE.md 생성
        claude_md_path = temp_dir / "CLAUDE.md"
        claude_md_path.write_text(sample_claude_md_content, encoding="utf-8")

        # 업데이트 제안 생성
        updater = ClaudeMDUpdater(str(claude_md_path))
        proposal = updater.generate_proposal(sample_pattern)

        assert proposal is not None
        assert proposal.section == "1. Critical Instructions"
        assert "경로" in proposal.proposed_content

    def test_full_learning_cycle(self, temp_dir, sample_error_session_log, sample_claude_md_content):
        """전체 학습 사이클: 세션 → 분석 → 패턴 → 업데이트"""
        # 1. 세션 로그 파일 생성
        session_file = temp_dir / "session.jsonl"
        session_file.write_text(sample_error_session_log, encoding="utf-8")

        # 2. 세션 파싱
        parser = SessionParser()
        events = parser.parse_file(session_file)
        summary = parser.summarize(events)
        assert summary.total_events == 4
        assert not summary.success  # 에러가 있으므로 실패

        # 3. 실패 분석
        analyzer = FailureAnalyzer()
        analysis1 = analyzer.analyze_session("test-1", events)
        analysis2 = analyzer.analyze_session("test-2", events)

        # 4. 패턴 감지
        detector = PatternDetector(min_occurrences=2)
        detector.add_analysis(analysis1)
        detector.add_analysis(analysis2)

        report = detector.generate_report()
        assert report.total_patterns >= 1

        # 5. CLAUDE.md 업데이트 제안
        claude_md = temp_dir / "CLAUDE.md"
        claude_md.write_text(sample_claude_md_content, encoding="utf-8")

        updater = ClaudeMDUpdater(str(claude_md))
        proposals = updater.generate_proposals_from_report(report)
        assert len(proposals) >= 1

        # 6. 미리보기 생성
        preview = updater.preview_changes()
        assert "변경 제안 미리보기" in preview

    def test_streaming_parser_integration(self, temp_dir, sample_session_log):
        """스트리밍 파서 통합 테스트"""
        # 로그 파일 생성
        log_file = temp_dir / "stream_test.jsonl"
        log_file.write_text(sample_session_log, encoding="utf-8")

        # 스트리밍 파싱
        parser = SessionParser()
        events_list = list(parser.parse_file_streaming(log_file))

        assert len(events_list) == 4
        # 일반 파싱과 결과 비교
        normal_events = parser.parse_file(log_file)
        assert len(events_list) == len(normal_events)


class TestMetricsIntegration:
    """메트릭스 통합 테스트"""

    def test_session_metrics_collection(self):
        """세션 메트릭스 수집 통합"""
        collector = MetricsCollector()

        # 세션 1: 성공
        collector.start_session("session-1")
        collector.record_phase_attempt("session-1", 0, True, 10.0, 100)
        collector.record_phase_attempt("session-1", 1, True, 20.0, 200)
        collector.end_session("session-1", success=True, token_usage=300)

        # 세션 2: 실패
        collector.start_session("session-2")
        collector.record_phase_attempt("session-2", 0, True, 15.0, 150)
        collector.record_phase_attempt("session-2", 1, False, 5.0, 50)
        collector.end_session("session-2", success=False, token_usage=200)

        # 메트릭스 조회
        metrics = collector.get_metrics()
        assert metrics.total_sessions == 2
        assert metrics.successful_sessions == 1
        assert metrics.failed_sessions == 1
        assert metrics.total_tokens == 500
        assert metrics.overall_success_rate == 0.5

        # Phase 메트릭스
        phase0 = metrics.phase_metrics.get(0)
        assert phase0 is not None
        assert phase0.attempts == 2
        assert phase0.successes == 2

        phase1 = metrics.phase_metrics.get(1)
        assert phase1 is not None
        assert phase1.attempts == 2
        assert phase1.successes == 1

    def test_incremental_aggregation(self):
        """증분 집계 테스트"""
        collector = MetricsCollector()

        # 세션 추가
        for i in range(5):
            collector.start_session(f"session-{i}")
            collector.end_session(f"session-{i}", success=(i % 2 == 0), token_usage=100)

        # 증분 집계 확인
        assert collector._total_tokens == 500
        assert collector._successful_sessions == 3  # 0, 2, 4
        assert collector._failed_sessions == 2  # 1, 3


class TestOptimizerIntegration:
    """옵티마이저 통합 테스트"""

    def test_dspy_with_training_data(self):
        """DSPy 옵티마이저 학습 데이터 통합"""
        optimizer = DSPyOptimizer()

        # 학습 데이터
        training_data = [
            {"input": "PRD with all sections", "output": "valid"},
            {"input": "PRD missing goals", "output": "invalid"},
            {"input": "Well-structured PRD", "output": "valid"},
        ]

        # 최적화
        result = optimizer.optimize(0, training_data, num_iterations=5)
        assert result.is_successful
        assert result.improvement > 0

        # 히스토리 확인
        history = optimizer.get_optimization_history()
        assert len(history) == 1

    def test_textgrad_prompt_optimization(self):
        """TextGrad 프롬프트 최적화 통합"""
        optimizer = TextGradOptimizer()

        # 분석할 프롬프트
        prompt = "이것은 테스트 프롬프트입니다. 작업을 수행합니다."

        # 그래디언트 분석
        gradients = optimizer.analyze_prompt(prompt)
        assert len(gradients) > 0

        # 최적화
        optimized, steps = optimizer.optimize_prompt(prompt, max_iterations=3)
        assert isinstance(optimized, str)

    def test_optimizer_comparison(self):
        """DSPy vs TextGrad 비교"""
        dspy_opt = DSPyOptimizer()
        textgrad_opt = TextGradOptimizer()

        # DSPy 최적화
        dspy_result = dspy_opt.optimize(0, [{"input": "test", "output": "pass"}])

        # TextGrad 최적화
        textgrad_result = textgrad_opt.optimize_agent(
            "test-agent",
            "Test agent prompt",
            max_iterations=3
        )

        # 둘 다 결과 생성
        assert dspy_result.status.value == "completed"
        assert textgrad_result.agent_name == "test-agent"


class TestABTestIntegration:
    """A/B 테스트 통합"""

    def test_full_ab_test_lifecycle(self):
        """A/B 테스트 전체 생명주기"""
        framework = ABTestFramework()

        # 테스트 생성
        config = ABTestConfig(
            test_id="prompt-test-1",
            control_prompt="Original prompt",
            treatment_prompt="Optimized prompt",
            traffic_split=0.5,
            min_samples=50
        )
        framework.create_test(config)

        # 샘플 수집
        for i in range(100):
            user_id = f"user-{i}"
            variant = framework.get_variant("prompt-test-1", user_id)

            # 시뮬레이션: Treatment가 더 좋은 성능
            if variant == Variant.TREATMENT:
                success = i % 3 != 0  # 66% 성공
            else:
                success = i % 2 == 0  # 50% 성공

            framework.record_sample(
                test_id="prompt-test-1",
                user_id=user_id,
                input_data={"query": f"test-{i}"},
                success=success,
                latency_ms=100.0
            )

        # 결과 조회
        result = framework.get_results("prompt-test-1")
        assert result.total_samples == 100
        assert result.treatment_success_rate > 0
        assert result.control_success_rate > 0

        # 내보내기
        exported = framework.export_results("prompt-test-1")
        assert "test_id" in exported
        assert "lift" in exported


class TestEndToEnd:
    """E2E 시나리오 테스트"""

    def test_complete_prompt_learning_workflow(self, temp_dir):
        """완전한 Prompt Learning 워크플로우"""
        # 1. 초기 CLAUDE.md
        claude_md = temp_dir / "CLAUDE.md"
        claude_md.write_text("""# CLAUDE.md

## 1. Critical Instructions

Basic instructions here.

## 3. Workflow Pipeline

Phase workflow.
""", encoding="utf-8")

        # 2. 여러 세션 시뮬레이션
        sessions_data = [
            """{"type": "user", "content": {}, "timestamp": "2024-01-01T00:00:00Z"}
{"error": "FileNotFoundError: ./config.txt", "timestamp": "2024-01-01T00:00:01Z"}""",
            """{"type": "user", "content": {}, "timestamp": "2024-01-02T00:00:00Z"}
{"error": "FileNotFoundError: ./data.json", "timestamp": "2024-01-02T00:00:01Z"}""",
            """{"type": "user", "content": {}, "timestamp": "2024-01-03T00:00:00Z"}
{"error": "phase 2 validation fail", "timestamp": "2024-01-03T00:00:01Z"}""",
        ]

        parser = SessionParser()
        analyzer = FailureAnalyzer()
        detector = PatternDetector(min_occurrences=2)
        collector = MetricsCollector()

        # 3. 각 세션 처리
        for i, session_data in enumerate(sessions_data):
            session_id = f"session-{i}"

            # 메트릭스 시작
            collector.start_session(session_id)

            # 파싱
            events = parser.parse_string(session_data)

            # 분석
            analysis = analyzer.analyze_session(session_id, events)
            detector.add_analysis(analysis)

            # 메트릭스 종료
            has_error = len(analysis.causes) > 0
            collector.end_session(session_id, success=not has_error, token_usage=100)

        # 4. 패턴 리포트 생성
        report = detector.generate_report()
        assert report.total_patterns >= 1

        # 5. CLAUDE.md 업데이트 제안
        updater = ClaudeMDUpdater(str(claude_md))
        proposals = updater.generate_proposals_from_report(report)

        # 6. 높은 신뢰도 제안 적용
        if proposals:
            result = updater.apply_proposals(backup=True)
            if result.success and result.proposals_applied > 0:
                # 백업 확인
                assert result.backup_path is not None

                # 업데이트된 내용 확인
                updated_content = claude_md.read_text(encoding="utf-8")
                assert len(updated_content) > 0

        # 7. 메트릭스 확인
        metrics = collector.get_metrics()
        assert metrics.total_sessions == 3
        assert metrics.failed_sessions >= 2  # 오류가 있는 세션

        # 8. 마크다운 리포트 생성
        md_report = metrics.to_markdown()
        assert "Prompt Learning 메트릭스 리포트" in md_report

    def test_pattern_trend_detection(self):
        """패턴 추세 감지 E2E"""
        analyzer = FailureAnalyzer()
        detector = PatternDetector(min_occurrences=3)

        # 증가하는 오류 패턴 시뮬레이션
        from prompt_learning.session_parser import SessionEvent, EventType

        for i in range(10):
            event = SessionEvent(
                timestamp=f"2024-01-{i+1:02d}T00:00:00Z",
                event_type=EventType.ERROR,
                content={},
                error="FileNotFoundError: ./test.txt"
            )
            analysis = analyzer.analyze_session(f"session-{i}", [event])
            detector.add_analysis(analysis)

        # 패턴 및 추세 확인
        patterns = detector.detect_patterns()
        assert len(patterns) >= 1

        # Critical 패턴 확인
        critical = detector.get_critical_patterns()
        # 10회 발생이면 critical
        assert len(critical) >= 1

        # 리포트에 권장 사항 포함
        report = detector.generate_report()
        assert len(report.recommendations) > 0


class TestTimestampCaching:
    """타임스탬프 캐싱 성능 테스트"""

    def test_cache_effectiveness(self):
        """캐시 효과 확인"""
        parser = SessionParser()

        # 동일한 타임스탬프로 여러 번 호출
        ts = "2024-01-01T12:00:00Z"

        # 첫 번째 호출 (캐시 미스)
        result1 = parser._parse_timestamp(ts)

        # 두 번째 호출 (캐시 히트)
        result2 = parser._parse_timestamp(ts)

        # 결과 동일
        assert result1 == result2

        # 캐시 정보 확인
        cache_info = parser._parse_timestamp.cache_info()
        assert cache_info.hits >= 1
