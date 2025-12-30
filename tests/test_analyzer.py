#!/usr/bin/env python3
"""
Tests for failure analysis functionality
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "scripts"))

from analyze_agent_usage import AgentUsageAnalyzer


class TestFailureAnalyzer:
    """Test suite for failure analysis"""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer instance with temporary repo root"""
        return AgentUsageAnalyzer(tmp_path)

    @pytest.fixture
    def sample_agent_calls(self):
        """Create sample agent call data"""
        return [
            {
                "timestamp": "2025-01-13T10:00:00Z",
                "agent_type": "context7-engineer",
                "prompt": "Verify React documentation",
                "status": "success",
                "duration": 3.2
            },
            {
                "timestamp": "2025-01-13T10:01:00Z",
                "agent_type": "playwright-engineer",
                "prompt": "Run E2E tests for the login flow",
                "status": "failed",
                "error": "Timeout after 30 seconds"
            },
            {
                "timestamp": "2025-01-13T10:02:00Z",
                "agent_type": "test-automator",
                "prompt": "Create tests for user module",
                "status": "failed",
                "error": "Cannot find test file test_example.py"
            },
            {
                "timestamp": "2025-01-13T10:03:00Z",
                "agent_type": "typescript-expert",
                "prompt": "Fix type errors in module",
                "status": "failed",
                "error": "Invalid parameter value provided"
            },
            {
                "timestamp": "2025-01-13T10:04:00Z",
                "agent_type": "seq-engineer",
                "prompt": "Do",
                "status": "failed",
                "error": "Task execution incomplete"
            },
            {
                "timestamp": "2025-01-13T10:05:00Z",
                "agent_type": "code-reviewer",
                "prompt": "Review security vulnerabilities in auth module",
                "status": "failed",
                "error": "API rate limit exceeded"
            }
        ]

    def test_analyze_no_failures(self, analyzer):
        """Test analyzing calls with no failures"""
        calls = [
            {"agent_type": "test1", "status": "success", "duration": 1.0},
            {"agent_type": "test2", "status": "success", "duration": 2.0}
        ]

        failures = analyzer.analyze_failures(calls)
        assert len(failures) == 0

    def test_analyze_timeout_failure(self, analyzer, sample_agent_calls):
        """Test classifying timeout failures"""
        failures = analyzer.analyze_failures(sample_agent_calls)

        timeout_failures = [f for f in failures if f["failure_cause"] == "timeout"]
        assert len(timeout_failures) == 1
        assert timeout_failures[0]["agent_type"] == "playwright-engineer"

    def test_analyze_missing_context_failure(self, analyzer, sample_agent_calls):
        """Test classifying missing context failures"""
        failures = analyzer.analyze_failures(sample_agent_calls)

        missing_failures = [f for f in failures if f["failure_cause"] == "missing_context"]
        assert len(missing_failures) == 1
        assert missing_failures[0]["agent_type"] == "test-automator"

    def test_analyze_parameter_error_failure(self, analyzer, sample_agent_calls):
        """Test classifying parameter error failures"""
        failures = analyzer.analyze_failures(sample_agent_calls)

        param_failures = [f for f in failures if f["failure_cause"] == "parameter_error"]
        assert len(param_failures) == 1
        assert param_failures[0]["agent_type"] == "typescript-expert"

    def test_analyze_ambiguous_prompt_failure(self, analyzer, sample_agent_calls):
        """Test classifying ambiguous prompt failures"""
        failures = analyzer.analyze_failures(sample_agent_calls)

        ambiguous_failures = [f for f in failures if f["failure_cause"] == "ambiguous_prompt"]
        assert len(ambiguous_failures) == 1
        assert ambiguous_failures[0]["agent_type"] == "seq-engineer"
        assert len(ambiguous_failures[0]["prompt"]) < 20

    def test_analyze_api_error_failure(self, analyzer, sample_agent_calls):
        """Test classifying API error failures"""
        failures = analyzer.analyze_failures(sample_agent_calls)

        api_failures = [f for f in failures if f["failure_cause"] == "api_error"]
        assert len(api_failures) == 1
        assert api_failures[0]["agent_type"] == "code-reviewer"

    def test_analyze_all_failure_types(self, analyzer, sample_agent_calls):
        """Test that all failure types are detected"""
        failures = analyzer.analyze_failures(sample_agent_calls)

        assert len(failures) == 5  # 5 failed calls in sample data

        causes = {f["failure_cause"] for f in failures}
        expected_causes = {"timeout", "missing_context", "parameter_error", "ambiguous_prompt", "api_error"}
        assert causes == expected_causes

    def test_analyze_preserves_original_data(self, analyzer, sample_agent_calls):
        """Test that analysis preserves original call data"""
        failures = analyzer.analyze_failures(sample_agent_calls)

        for failure in failures:
            assert "timestamp" in failure
            assert "agent_type" in failure
            assert "prompt" in failure
            assert "status" in failure
            assert failure["status"] == "failed"
            assert "error" in failure
            assert "failure_cause" in failure

    def test_analyze_edge_case_empty_error(self, analyzer):
        """Test analyzing failure with empty error message"""
        calls = [
            {
                "agent_type": "test-agent",
                "status": "failed",
                "error": "",
                "prompt": "Test prompt with sufficient length for classification"
            }
        ]

        failures = analyzer.analyze_failures(calls)

        assert len(failures) == 1
        # Empty error with long prompt (>= 20 chars) falls through to api_error
        assert failures[0]["failure_cause"] == "api_error"

    def test_analyze_edge_case_missing_prompt(self, analyzer):
        """Test analyzing failure with missing prompt"""
        calls = [
            {
                "agent_type": "test-agent",
                "status": "failed",
                "error": "Some error",
                "prompt": ""
            }
        ]

        failures = analyzer.analyze_failures(calls)

        assert len(failures) == 1
        # "error" keyword in error message triggers parameter_error before prompt length check
        assert failures[0]["failure_cause"] == "parameter_error"

    def test_analyze_mixed_statuses(self, analyzer):
        """Test analyzing calls with mixed statuses"""
        calls = [
            {"agent_type": "test1", "status": "success", "duration": 1.0},
            {"agent_type": "test2", "status": "failed", "error": "timeout", "prompt": "test"},
            {"agent_type": "test3", "status": "unknown"},
            {"agent_type": "test4", "status": "failed", "error": "error", "prompt": "test"}
        ]

        failures = analyzer.analyze_failures(calls)

        # Only "failed" status should be included
        assert len(failures) == 2
        assert all(f["status"] == "failed" for f in failures)

    def test_analyze_case_insensitive_keywords(self, analyzer):
        """Test that error classification is case-insensitive"""
        calls = [
            {"agent_type": "test1", "status": "failed", "error": "TIMEOUT OCCURRED", "prompt": "test"},
            {"agent_type": "test2", "status": "failed", "error": "Cannot Find File", "prompt": "test"},
            {"agent_type": "test3", "status": "failed", "error": "Invalid Input", "prompt": "test"}
        ]

        failures = analyzer.analyze_failures(calls)

        assert failures[0]["failure_cause"] == "timeout"
        assert failures[1]["failure_cause"] == "missing_context"
        assert failures[2]["failure_cause"] == "parameter_error"

    def test_analyze_multiple_keyword_matches(self, analyzer):
        """Test prioritization when multiple keywords match"""
        calls = [
            {
                "agent_type": "test-agent",
                "status": "failed",
                "error": "Timeout occurred: cannot find resource",
                "prompt": "test"
            }
        ]

        failures = analyzer.analyze_failures(calls)

        # Timeout should be detected first due to order in code
        assert failures[0]["failure_cause"] == "timeout"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
