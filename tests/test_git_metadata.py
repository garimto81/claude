#!/usr/bin/env python3
"""
Tests for Git metadata functionality
"""

import pytest
from pathlib import Path
import sys
import subprocess
from unittest.mock import Mock, patch, call

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "scripts"))

from analyze_agent_usage import AgentUsageAnalyzer


class TestGitMetadata:
    """Test suite for Git metadata storage"""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer instance with temporary repo root"""
        # Ensure .claude directory exists for error logging
        (tmp_path / ".claude").mkdir(parents=True, exist_ok=True)
        return AgentUsageAnalyzer(tmp_path)

    @pytest.fixture
    def sample_agent_calls(self):
        """Create sample agent call data"""
        return [
            {
                "agent_type": "context7-engineer",
                "status": "success",
                "duration": 3.2
            },
            {
                "agent_type": "playwright-engineer",
                "status": "failed",
                "error": "Timeout",
                "failure_cause": "timeout"
            },
            {
                "agent_type": "test-automator",
                "status": "success",
                "duration": 5.1
            }
        ]

    def test_add_metadata_disabled(self, analyzer, sample_agent_calls):
        """Test that metadata is not added when disabled"""
        analyzer.config["git_metadata"]["enabled"] = False

        with patch('subprocess.run') as mock_run:
            analyzer.add_git_metadata(sample_agent_calls)
            mock_run.assert_not_called()

    def test_add_metadata_empty_calls(self, analyzer):
        """Test that nothing happens with empty agent calls"""
        with patch('subprocess.run') as mock_run:
            analyzer.add_git_metadata([])
            mock_run.assert_not_called()

    def test_add_metadata_amend_disabled(self, analyzer, sample_agent_calls):
        """Test that metadata is not added when amend is disabled"""
        analyzer.config["git_metadata"]["amend_commit"] = False

        with patch('subprocess.run') as mock_run:
            analyzer.add_git_metadata(sample_agent_calls)
            mock_run.assert_not_called()

    @patch('subprocess.run')
    def test_add_metadata_success(self, mock_run, analyzer, sample_agent_calls, tmp_path):
        """Test successful metadata addition"""
        # Mock git log output (current commit message)
        mock_log_result = Mock()
        mock_log_result.stdout = "feat: Add feature (v1.0.0) [PRD-0001]\n\nSome description"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(sample_agent_calls)

        # Should call git log first, then git commit --amend
        assert mock_run.call_count == 2

        # Check git log call
        log_call = mock_run.call_args_list[0]
        assert log_call[0][0] == ["git", "log", "-1", "--pretty=%B"]

        # Check git commit --amend call
        amend_call = mock_run.call_args_list[1]
        assert amend_call[0][0][0] == "git"
        assert amend_call[0][0][1] == "commit"
        assert amend_call[0][0][2] == "--amend"
        assert "--no-verify" in amend_call[0][0]

    @patch('subprocess.run')
    def test_add_metadata_filters_sensitive_info(self, mock_run, analyzer, tmp_path):
        """Test that sensitive information is filtered from metadata"""
        agent_calls = [
            {
                "agent_type": "test-agent",
                "status": "success",
                "duration": 1.0,
                "prompt": "Secret API key: sk-1234567890",
                "parameters": {"secret": "password123"},
                "error": None
            }
        ]

        mock_log_result = Mock()
        mock_log_result.stdout = "Test commit"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(agent_calls)

        # Get the commit message from the amend call
        amend_call = mock_run.call_args_list[1]
        commit_message = amend_call[0][0][4]  # -m argument

        # Verify sensitive info is NOT in the message
        assert "Secret API key" not in commit_message
        assert "sk-1234567890" not in commit_message
        assert "password123" not in commit_message

        # Verify safe info IS in the message
        assert "test-agent" in commit_message
        assert "success" in commit_message

    @patch('subprocess.run')
    def test_add_metadata_json_format(self, mock_run, analyzer, sample_agent_calls, tmp_path):
        """Test that metadata is in compact JSON format"""
        mock_log_result = Mock()
        mock_log_result.stdout = "Test commit"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(sample_agent_calls)

        # Get the commit message
        amend_call = mock_run.call_args_list[1]
        commit_message = amend_call[0][0][4]

        # Check JSON format
        assert "Agent-Usage:" in commit_message
        assert "[{" in commit_message  # JSON array start
        assert '"agent":' in commit_message  # JSON field
        assert '"status":' in commit_message

        # Check compact format (no extra spaces)
        assert ", " not in commit_message.split("Agent-Usage:")[1]
        assert ": " not in commit_message.split("Agent-Usage:")[1].replace('"status":', '').replace('"agent":', '').replace('"duration":', '').replace('"error":', '')

    @patch('subprocess.run')
    def test_add_metadata_includes_duration(self, mock_run, analyzer, tmp_path):
        """Test that duration is included and formatted correctly"""
        agent_calls = [
            {
                "agent_type": "test-agent",
                "status": "success",
                "duration": 123.456789
            }
        ]

        mock_log_result = Mock()
        mock_log_result.stdout = "Test commit"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(agent_calls)

        # Get the commit message
        amend_call = mock_run.call_args_list[1]
        commit_message = amend_call[0][0][4]

        # Check duration format (1 decimal place + 's')
        assert '"duration":"123.5s"' in commit_message

    @patch('subprocess.run')
    def test_add_metadata_includes_failure_cause(self, mock_run, analyzer, tmp_path):
        """Test that failure cause is included for failed tasks"""
        agent_calls = [
            {
                "agent_type": "test-agent",
                "status": "failed",
                "failure_cause": "timeout"
            }
        ]

        mock_log_result = Mock()
        mock_log_result.stdout = "Test commit"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(agent_calls)

        # Get the commit message
        amend_call = mock_run.call_args_list[1]
        commit_message = amend_call[0][0][4]

        # Check failure cause is included as error field
        assert '"error":"timeout"' in commit_message

    @patch('subprocess.run')
    def test_add_metadata_skip_if_already_exists(self, mock_run, analyzer, sample_agent_calls):
        """Test that metadata is not added if already present"""
        # Mock git log output with existing Agent-Usage
        mock_log_result = Mock()
        mock_log_result.stdout = "Test commit\n\nAgent-Usage: [{\"agent\":\"test\"}]"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(sample_agent_calls)

        # Should only call git log, not git commit --amend
        assert mock_run.call_count == 1
        assert mock_run.call_args[0][0] == ["git", "log", "-1", "--pretty=%B"]

    @patch('subprocess.run')
    def test_add_metadata_handles_git_error(self, mock_run, analyzer, sample_agent_calls, tmp_path):
        """Test graceful handling of git command errors"""
        # Mock git log failure
        mock_run.side_effect = subprocess.CalledProcessError(1, "git log")

        # Should not raise exception
        analyzer.add_git_metadata(sample_agent_calls)

        # Error should be logged
        error_log = tmp_path / ".claude" / "optimizer-error.log"
        assert error_log.exists()

    @patch('subprocess.run')
    def test_add_metadata_preserves_original_message(self, mock_run, analyzer, sample_agent_calls):
        """Test that original commit message is preserved"""
        original_message = "feat: Add feature (v1.0.0) [PRD-0001]\n\nDetailed description\n\nCo-Authored-By: Someone"

        mock_log_result = Mock()
        mock_log_result.stdout = original_message
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(sample_agent_calls)

        # Get the new commit message
        amend_call = mock_run.call_args_list[1]
        new_message = amend_call[0][0][4]

        # Original message should be at the start
        assert new_message.startswith(original_message)

        # Agent-Usage should be appended
        assert "\nAgent-Usage:" in new_message

    @patch('subprocess.run')
    def test_add_metadata_uses_no_verify_flag(self, mock_run, analyzer, sample_agent_calls):
        """Test that --no-verify flag is used to prevent hook loops"""
        mock_log_result = Mock()
        mock_log_result.stdout = "Test commit"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(sample_agent_calls)

        # Check that --no-verify is in the amend command
        amend_call = mock_run.call_args_list[1]
        assert "--no-verify" in amend_call[0][0]

    @patch('subprocess.run')
    def test_add_metadata_multiple_agents(self, mock_run, analyzer, sample_agent_calls):
        """Test metadata with multiple agent calls"""
        mock_log_result = Mock()
        mock_log_result.stdout = "Test commit"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(sample_agent_calls)

        # Get the commit message
        amend_call = mock_run.call_args_list[1]
        commit_message = amend_call[0][0][4]

        # Check all agents are included
        assert "context7-engineer" in commit_message
        assert "playwright-engineer" in commit_message
        assert "test-automator" in commit_message

    @patch('subprocess.run')
    def test_add_metadata_cwd_parameter(self, mock_run, analyzer, sample_agent_calls, tmp_path):
        """Test that git commands use correct working directory"""
        mock_log_result = Mock()
        mock_log_result.stdout = "Test commit"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        analyzer.add_git_metadata(sample_agent_calls)

        # Check both git calls use the repo root as cwd
        for call_item in mock_run.call_args_list:
            assert call_item[1]["cwd"] == tmp_path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
