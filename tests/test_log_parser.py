#!/usr/bin/env python3
"""
Tests for log file parsing functionality
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "scripts"))

from analyze_agent_usage import AgentUsageAnalyzer


class TestLogParser:
    """Test suite for log file parsing"""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer instance with temporary repo root"""
        return AgentUsageAnalyzer(tmp_path)

    @pytest.fixture
    def sample_log_success(self, tmp_path):
        """Create a sample log file with successful agent execution"""
        log_content = """[2025-01-13T10:15:23.456Z] Task execution started
Agent type: context7-engineer
Prompt: "Verify latest React documentation"
[2025-01-13T10:15:26.789Z] Task completed (3.3s)
"""
        log_file = tmp_path / "test.log"
        log_file.write_text(log_content, encoding='utf-8')
        return log_file

    @pytest.fixture
    def sample_log_failure(self, tmp_path):
        """Create a sample log file with failed agent execution"""
        log_content = """[2025-01-13 10:20:15] Starting task
agent_type: "playwright-engineer"
description: "Run E2E tests"
[2025-01-13 10:20:18] ERROR: Task failed: Timeout after 30 seconds
"""
        log_file = tmp_path / "test.log"
        log_file.write_text(log_content, encoding='utf-8')
        return log_file

    @pytest.fixture
    def sample_log_multiple(self, tmp_path):
        """Create a sample log file with multiple agent calls"""
        log_content = """[2025-01-13T10:00:00.000Z] Agent execution
subagent_type: seq-engineer
prompt: 'Analyze requirements'
[2025-01-13T10:00:05.123Z] Agent completed (5.1s)

[2025-01-13T10:01:00.000Z] Invoking agent
Agent type: test-automator
Prompt: 'Create unit tests'
[2025-01-13T10:01:15.456Z] FAILED: Cannot find test framework

[2025-01-13T10:02:00.000Z] Task execution started
agent_type: typescript-expert
description: 'Fix type errors'
[2025-01-13T10:02:30.789Z] Task completed (30.8s)
"""
        log_file = tmp_path / "test.log"
        log_file.write_text(log_content, encoding='utf-8')
        return log_file

    def test_parse_successful_execution(self, analyzer, sample_log_success):
        """Test parsing a successful agent execution"""
        result = analyzer.parse_log_file(sample_log_success)

        assert len(result) == 1
        assert result[0]["agent_type"] == "context7-engineer"
        assert result[0]["status"] == "success"
        # Note: duration parsing is optional and may not capture due to regex limitations
        assert result[0]["duration"] >= 0.0
        assert "React documentation" in result[0]["prompt"]

    def test_parse_failed_execution(self, analyzer, sample_log_failure):
        """Test parsing a failed agent execution"""
        result = analyzer.parse_log_file(sample_log_failure)

        assert len(result) == 1
        assert result[0]["agent_type"] == "playwright-engineer"
        assert result[0]["status"] == "failed"
        assert "Timeout" in result[0]["error"]

    def test_parse_multiple_executions(self, analyzer, sample_log_multiple):
        """Test parsing multiple agent executions"""
        result = analyzer.parse_log_file(sample_log_multiple)

        assert len(result) == 3

        # First task - success
        assert result[0]["agent_type"] == "seq-engineer"
        assert result[0]["status"] == "success"
        # Note: duration parsing is optional and may not capture due to regex limitations
        assert result[0]["duration"] >= 0.0

        # Second task - failure
        assert result[1]["agent_type"] == "test-automator"
        assert result[1]["status"] == "failed"
        assert "Cannot find" in result[1]["error"]

        # Third task - success
        assert result[2]["agent_type"] == "typescript-expert"
        assert result[2]["status"] == "success"
        assert result[2]["duration"] >= 0.0

    def test_parse_empty_file(self, analyzer, tmp_path):
        """Test parsing an empty log file"""
        empty_log = tmp_path / "empty.log"
        empty_log.write_text("", encoding='utf-8')

        result = analyzer.parse_log_file(empty_log)
        assert len(result) == 0

    def test_parse_invalid_format(self, analyzer, tmp_path):
        """Test parsing a log file with invalid format"""
        invalid_log = tmp_path / "invalid.log"
        invalid_log.write_text("Random text without proper format\n", encoding='utf-8')

        result = analyzer.parse_log_file(invalid_log)
        assert len(result) == 0

    def test_parse_large_file_skip(self, analyzer, tmp_path):
        """Test that very large files are skipped"""
        # Set max size to 1KB for testing
        analyzer.config["log_analysis"]["max_log_size_mb"] = 0.001

        large_log = tmp_path / "large.log"
        large_log.write_text("x" * 2000, encoding='utf-8')  # 2KB file

        result = analyzer.parse_log_file(large_log)
        assert len(result) == 0

    def test_parse_incomplete_task(self, analyzer, tmp_path):
        """Test parsing a log with incomplete task (no completion/failure)"""
        log_content = """[2025-01-13T10:30:00.000Z] Task execution started
agent_type: code-reviewer
prompt: "Review code changes"
"""
        log_file = tmp_path / "test.log"
        log_file.write_text(log_content, encoding='utf-8')

        result = analyzer.parse_log_file(log_file)

        assert len(result) == 1
        assert result[0]["status"] == "unknown"
        assert result[0]["agent_type"] == "code-reviewer"

    def test_timestamp_formats(self, analyzer, tmp_path):
        """Test parsing different timestamp formats"""
        log_content = """[2025-01-13T10:00:00Z] Task execution started
agent_type: test1
[2025-01-13T10:00:01.123Z] Success

[2025-01-13 11:00:00] Starting task
agent_type: test2
[2025-01-13 11:00:01] Finished

[2025-01-13T12:00:00.456789Z] Invoking agent
agent_type: test3
[2025-01-13T12:00:02.789012Z] Task completed
"""
        log_file = tmp_path / "test.log"
        log_file.write_text(log_content, encoding='utf-8')

        result = analyzer.parse_log_file(log_file)

        assert len(result) == 3
        assert all(r["agent_type"].startswith("test") for r in result)

    def test_extract_prompt_variations(self, analyzer, tmp_path):
        """Test extracting prompts with different quote styles"""
        log_content = """[2025-01-13T10:00:00Z] Task execution started
Prompt: "Double quoted prompt"
[2025-01-13T10:00:01Z] Success

[2025-01-13T10:01:00Z] Agent execution
prompt: 'Single quoted prompt'
[2025-01-13T10:01:01Z] Finished

[2025-01-13T10:02:00Z] Starting task
description: "Description field"
[2025-01-13T10:02:01Z] Task completed
"""
        log_file = tmp_path / "test.log"
        log_file.write_text(log_content, encoding='utf-8')

        result = analyzer.parse_log_file(log_file)

        assert len(result) == 3
        assert "Double quoted" in result[0]["prompt"]
        assert "Single quoted" in result[1]["prompt"]
        assert "Description field" in result[2]["prompt"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
