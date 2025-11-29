# tests/prompt_learning/test_session_parser.py
"""
Session Parser 테스트

pytest tests/prompt_learning/test_session_parser.py -v
"""

import pytest
import tempfile
import os
import sys
import json
from pathlib import Path

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.session_parser import (
    SessionParser,
    SessionEvent,
    SessionSummary,
    EventType,
    find_session_logs,
    parse_multiple_sessions,
)


class TestSessionEvent:
    """SessionEvent 테스트"""

    def test_from_dict_user_message(self):
        """사용자 메시지 이벤트"""
        data = {"type": "user", "content": {"text": "hello"}, "timestamp": "2024-01-01T00:00:00Z"}
        event = SessionEvent.from_dict(data)
        assert event.event_type == EventType.USER_MESSAGE

    def test_from_dict_assistant_message(self):
        """어시스턴트 메시지 이벤트"""
        data = {"type": "assistant", "content": {"text": "hi"}, "timestamp": "2024-01-01T00:00:00Z"}
        event = SessionEvent.from_dict(data)
        assert event.event_type == EventType.ASSISTANT_MESSAGE

    def test_from_dict_tool_call(self):
        """도구 호출 이벤트"""
        data = {"tool": {"name": "Read"}, "timestamp": "2024-01-01T00:00:00Z"}
        event = SessionEvent.from_dict(data)
        assert event.event_type == EventType.TOOL_CALL
        assert event.tool_name == "Read"

    def test_from_dict_tool_result(self):
        """도구 결과 이벤트"""
        data = {"tool": "Read", "tool_result": True, "success": True, "timestamp": "2024-01-01T00:00:00Z"}
        event = SessionEvent.from_dict(data)
        assert event.event_type == EventType.TOOL_RESULT

    def test_from_dict_error(self):
        """에러 이벤트"""
        data = {"error": "Something went wrong", "timestamp": "2024-01-01T00:00:00Z"}
        event = SessionEvent.from_dict(data)
        assert event.event_type == EventType.ERROR
        assert event.error == "Something went wrong"

    def test_from_dict_unknown(self):
        """알 수 없는 이벤트"""
        data = {"random": "data"}
        event = SessionEvent.from_dict(data)
        assert event.event_type == EventType.UNKNOWN


class TestSessionParser:
    """SessionParser 테스트"""

    def test_create_parser(self):
        """파서 생성"""
        parser = SessionParser()
        assert parser._events == []

    def test_parse_string_empty(self):
        """빈 문자열 파싱"""
        parser = SessionParser()
        events = parser.parse_string("")
        assert events == []

    def test_parse_string_single_event(self):
        """단일 이벤트 파싱"""
        parser = SessionParser()
        log = '{"type": "user", "content": {"text": "hello"}, "timestamp": "2024-01-01T00:00:00Z"}'
        events = parser.parse_string(log)
        assert len(events) == 1
        assert events[0].event_type == EventType.USER_MESSAGE

    def test_parse_string_multiple_events(self):
        """여러 이벤트 파싱"""
        parser = SessionParser()
        log = """{"type": "user", "content": {}, "timestamp": "2024-01-01T00:00:00Z"}
{"type": "assistant", "content": {}, "timestamp": "2024-01-01T00:00:01Z"}
{"tool": {"name": "Read"}, "timestamp": "2024-01-01T00:00:02Z"}"""
        events = parser.parse_string(log)
        assert len(events) == 3

    def test_parse_string_invalid_json(self):
        """잘못된 JSON 무시"""
        parser = SessionParser()
        log = """{"type": "user", "content": {}}
not valid json
{"type": "assistant", "content": {}}"""
        events = parser.parse_string(log)
        assert len(events) == 2

    def test_parse_file_not_found(self):
        """파일 없음 에러"""
        parser = SessionParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/path.jsonl")

    def test_parse_file_success(self):
        """파일 파싱 성공"""
        parser = SessionParser()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False, encoding='utf-8') as f:
            f.write('{"type": "user", "content": {"text": "test"}}\n')
            f.write('{"type": "assistant", "content": {"text": "response"}}\n')
            temp_path = f.name

        try:
            events = parser.parse_file(temp_path)
            assert len(events) == 2
        finally:
            os.unlink(temp_path)


class TestSessionSummary:
    """SessionSummary 테스트"""

    def test_summarize_empty(self):
        """빈 이벤트 요약"""
        parser = SessionParser()
        summary = parser.summarize([])
        assert summary.total_events == 0
        assert summary.success is True

    def test_summarize_with_events(self):
        """이벤트 있는 요약"""
        parser = SessionParser()
        log = """{"type": "user", "content": {}, "timestamp": "2024-01-01T00:00:00Z"}
{"type": "assistant", "content": {}, "timestamp": "2024-01-01T00:00:01Z"}
{"tool": {"name": "Read"}, "timestamp": "2024-01-01T00:00:02Z"}"""
        events = parser.parse_string(log)
        summary = parser.summarize(events)
        assert summary.total_events == 3
        assert summary.user_messages == 1
        assert summary.assistant_messages == 1
        assert summary.tool_calls == 1

    def test_summarize_with_errors(self):
        """에러가 있는 요약"""
        parser = SessionParser()
        log = """{"type": "user", "content": {}, "timestamp": "2024-01-01T00:00:00Z"}
{"error": "Something failed", "timestamp": "2024-01-01T00:00:01Z"}"""
        events = parser.parse_string(log)
        summary = parser.summarize(events)
        assert summary.success is False
        assert len(summary.errors) > 0

    def test_to_dict(self):
        """딕셔너리 변환"""
        summary = SessionSummary(
            session_id="test-123",
            total_events=5,
            user_messages=2,
            assistant_messages=2,
            tool_calls=1,
            errors=[],
            success=True,
            duration_seconds=10.5
        )
        d = summary.to_dict()
        assert d["session_id"] == "test-123"
        assert d["total_events"] == 5


class TestFilters:
    """필터 함수 테스트"""

    def test_get_tool_calls(self):
        """도구 호출 필터"""
        parser = SessionParser()
        log = """{"type": "user", "content": {}}
{"tool": {"name": "Read"}}
{"tool": {"name": "Write"}}"""
        events = parser.parse_string(log)
        tool_calls = parser.get_tool_calls(events)
        assert len(tool_calls) == 2

    def test_get_errors(self):
        """에러 필터"""
        parser = SessionParser()
        log = """{"type": "user", "content": {}}
{"error": "Error 1"}
{"error": "Error 2"}"""
        events = parser.parse_string(log)
        errors = parser.get_errors(events)
        assert len(errors) == 2

    def test_get_failed_tool_calls(self):
        """실패한 도구 호출 필터"""
        parser = SessionParser()
        log = """{"tool": "Read", "tool_result": true, "success": true}
{"tool": "Write", "tool_result": true, "success": false}"""
        events = parser.parse_string(log)
        failed = parser.get_failed_tool_calls(events)
        assert len(failed) == 1


class TestDuration:
    """시간 계산 테스트"""

    def test_calculate_duration(self):
        """duration 계산"""
        parser = SessionParser()
        log = """{"type": "user", "content": {}, "timestamp": "2024-01-01T00:00:00Z"}
{"type": "assistant", "content": {}, "timestamp": "2024-01-01T00:00:30Z"}"""
        events = parser.parse_string(log)
        summary = parser.summarize(events)
        assert summary.duration_seconds == 30.0

    def test_calculate_duration_invalid_format(self):
        """잘못된 시간 형식"""
        parser = SessionParser()
        duration = parser._calculate_duration("invalid", "also invalid")
        assert duration == 0.0


class TestUtilityFunctions:
    """유틸리티 함수 테스트"""

    def test_find_session_logs(self):
        """세션 로그 찾기"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 테스트 파일 생성
            (Path(tmpdir) / "session1.jsonl").write_text("{}")
            (Path(tmpdir) / "session2.jsonl").write_text("{}")
            (Path(tmpdir) / "other.txt").write_text("not a log")

            logs = list(find_session_logs(tmpdir))
            assert len(logs) == 2

    def test_find_session_logs_empty_dir(self):
        """빈 디렉토리"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logs = list(find_session_logs(tmpdir))
            assert logs == []

    def test_find_session_logs_nonexistent(self):
        """존재하지 않는 디렉토리"""
        logs = list(find_session_logs("/nonexistent/path"))
        assert logs == []

    def test_parse_multiple_sessions(self):
        """여러 세션 파싱"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path1 = Path(tmpdir) / "session1.jsonl"
            path1.write_text('{"type": "user", "content": {}}\n')

            path2 = Path(tmpdir) / "session2.jsonl"
            path2.write_text('{"type": "user", "content": {}}\n{"type": "assistant", "content": {}}\n')

            summaries = parse_multiple_sessions([path1, path2])
            assert len(summaries) == 2
            assert summaries["session1.jsonl"].total_events == 1
            assert summaries["session2.jsonl"].total_events == 2
