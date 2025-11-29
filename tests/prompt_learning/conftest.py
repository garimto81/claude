# tests/prompt_learning/conftest.py
"""
Prompt Learning 테스트 공통 Fixture

pytest tests/prompt_learning/ -v
"""

import pytest
import tempfile
import sys
import os
from pathlib import Path

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.metrics import reset_collector
from prompt_learning.failure_analyzer import FailureCause, FailureCategory, FailureAnalysis
from prompt_learning.session_parser import SessionEvent, EventType, SessionParser
from prompt_learning.pattern_detector import Pattern


@pytest.fixture(autouse=True)
def reset_global_state():
    """각 테스트마다 전역 상태 초기화"""
    reset_collector()
    yield
    reset_collector()


@pytest.fixture
def temp_dir():
    """임시 디렉토리 제공"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_failure_cause():
    """표준 FailureCause 객체"""
    return FailureCause(
        category=FailureCategory.PATH_ERROR,
        description="Test path error",
        evidence="FileNotFoundError: /path/to/file",
        confidence=0.8,
        suggestion="Use absolute paths"
    )


@pytest.fixture
def sample_failure_analysis(sample_failure_cause):
    """표준 FailureAnalysis 객체"""
    return FailureAnalysis(
        session_id="test-session-1",
        causes=[sample_failure_cause],
        severity="medium",
        affected_phase=1,
        recommendations=["Check file paths"]
    )


@pytest.fixture
def sample_session_log():
    """표준 세션 로그 문자열"""
    return """{"type": "user", "content": {"text": "test"}, "timestamp": "2024-01-01T00:00:00Z"}
{"type": "assistant", "content": {"text": "response"}, "timestamp": "2024-01-01T00:00:01Z"}
{"tool": {"name": "Read"}, "timestamp": "2024-01-01T00:00:02Z"}
{"tool": "Read", "tool_result": true, "success": true, "timestamp": "2024-01-01T00:00:03Z"}"""


@pytest.fixture
def sample_error_session_log():
    """오류가 포함된 세션 로그"""
    return """{"type": "user", "content": {"text": "test"}, "timestamp": "2024-01-01T00:00:00Z"}
{"error": "FileNotFoundError: ./test.txt", "timestamp": "2024-01-01T00:00:01Z"}
{"type": "user", "content": {"text": "retry"}, "timestamp": "2024-01-01T00:00:02Z"}
{"error": "FileNotFoundError: ./test2.txt", "timestamp": "2024-01-01T00:00:03Z"}"""


@pytest.fixture
def sample_pattern():
    """표준 Pattern 객체"""
    return Pattern(
        pattern_id="path_error:test",
        category=FailureCategory.PATH_ERROR,
        description="Test path error",
        occurrence_count=5,
        first_seen="2024-01-01T00:00:00",
        last_seen="2024-01-05T00:00:00",
        affected_sessions=["s1", "s2", "s3", "s4", "s5"],
        trend="stable"
    )


@pytest.fixture
def session_parser():
    """SessionParser 인스턴스"""
    return SessionParser()


@pytest.fixture
def sample_claude_md_content():
    """CLAUDE.md 샘플 내용"""
    return """# CLAUDE.md

## 1. Critical Instructions

### Core Rules
1. Use absolute paths
2. Validate before proceeding

## 2. Build & Test Commands

```bash
pytest tests/ -v
```

## 3. Workflow Pipeline

Phase 0 -> Phase 1 -> Phase 2

## 9. Complex Feature Protocol

TDD is required.
"""
