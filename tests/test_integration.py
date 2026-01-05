#!/usr/bin/env python3
"""
Integration tests for Agent/Skill optimizer system
"""

import pytest
from pathlib import Path
import sys
from unittest.mock import patch, Mock, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "scripts"))

from analyze_agent_usage import AgentUsageAnalyzer


def create_mock_anthropic():
    """Create a mock anthropic module"""
    mock_anthropic = MagicMock()
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Improved prompt")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.Anthropic.return_value = mock_client
    return mock_anthropic, mock_client


class TestIntegration:
    """Integration test suite for end-to-end workflows"""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer instance with temporary repo root"""
        return AgentUsageAnalyzer(tmp_path)

    @pytest.fixture
    def complete_log_file(self, tmp_path):
        """Create a complete log file with multiple scenarios"""
        log_content = """[2025-01-13T10:00:00.000Z] Task execution started
Agent type: context7-engineer
Prompt: "Verify latest React 18 documentation and hooks API"
[2025-01-13T10:00:03.200Z] Task completed successfully (3.2s)

[2025-01-13T10:01:00.000Z] Invoking agent
subagent_type: playwright-engineer
description: "Run E2E tests for authentication flow"
[2025-01-13T10:01:30.500Z] ERROR: Task failed: Timeout after 30 seconds waiting for login button

[2025-01-13T10:02:00.000Z] Starting task
agent_type: test-automator
prompt: "Create unit tests for UserService class"
[2025-01-13T10:02:05.100Z] Agent completed (5.1 seconds)

[2025-01-13T10:03:00.000Z] Agent execution
Agent type: typescript-expert
Prompt: "Fix type errors in api/routes.ts"
[2025-01-13T10:03:02.800Z] SUCCESS (2.8s)

[2025-01-13T10:04:00.000Z] Task execution started
agent_type: seq-engineer
prompt: "Do task"
[2025-01-13T10:04:01.500Z] FAILED: Ambiguous prompt provided

[2025-01-13T10:05:00.000Z] Invoking agent
subagent_type: code-reviewer
description: "Review security vulnerabilities in auth module"
[2025-01-13T10:05:10.300Z] Task completed (10.3 seconds)
"""
        log_file = tmp_path / "claude.log"
        log_file.write_text(log_content, encoding='utf-8')
        return log_file

    def test_full_pipeline_parse_analyze_notify(self, analyzer, complete_log_file):
        """Test complete pipeline: parse → analyze → notify"""
        # Parse log file
        agent_calls = analyzer.parse_log_file(complete_log_file)

        assert len(agent_calls) == 6

        # Analyze failures
        failures = analyzer.analyze_failures(agent_calls)

        assert len(failures) == 2  # playwright-engineer and seq-engineer

        # Verify failure classifications
        failure_dict = {f["agent_type"]: f for f in failures}

        assert "playwright-engineer" in failure_dict
        assert failure_dict["playwright-engineer"]["failure_cause"] == "timeout"

        assert "seq-engineer" in failure_dict
        assert failure_dict["seq-engineer"]["failure_cause"] == "ambiguous_prompt"

        # Test notification (should not raise)
        analyzer.notify(failures)

    def test_full_pipeline_with_improvements(self, analyzer, complete_log_file, tmp_path):
        """Test complete pipeline including improvement generation"""
        # Mock Claude API
        mock_anthropic, mock_client = create_mock_anthropic()
        mock_response1 = Mock()
        mock_response1.content = [Mock(text="Improved: Run end-to-end authentication tests with explicit 60-second timeout and detailed element selectors")]
        mock_response2 = Mock()
        mock_response2.content = [Mock(text="Improved: Analyze the requirements for the user authentication feature and break down into sequential implementation steps")]

        mock_client.messages.create.side_effect = [mock_response1, mock_response2]

        # Run full pipeline
        agent_calls = analyzer.parse_log_file(complete_log_file)
        failures = analyzer.analyze_failures(agent_calls)

        with patch.dict('sys.modules', {'anthropic': mock_anthropic}):
            improvements = analyzer.generate_improvements(failures)
        analyzer.save_improvements(improvements)

        # Verify improvements were generated
        assert len(improvements) == 2

        # Verify suggestions file was created
        suggestions_file = tmp_path / ".claude" / "improvement-suggestions.md"
        assert suggestions_file.exists()

        content = suggestions_file.read_text(encoding='utf-8')
        assert "playwright-engineer" in content
        assert "seq-engineer" in content
        assert "Improved:" in content

    @patch('subprocess.run')
    def test_full_pipeline_with_git_metadata(self, mock_run, analyzer, complete_log_file):
        """Test complete pipeline including Git metadata storage"""
        # Mock git commands
        mock_log_result = Mock()
        mock_log_result.stdout = "feat: Implement auth (v1.0.0) [PRD-0001]"
        mock_log_result.returncode = 0

        mock_run.return_value = mock_log_result

        # Run full pipeline
        agent_calls = analyzer.parse_log_file(complete_log_file)
        _ = analyzer.analyze_failures(agent_calls)
        analyzer.add_git_metadata(agent_calls)

        # Verify git commands were called
        assert mock_run.call_count == 2

        # Verify commit message includes all agents
        amend_call = mock_run.call_args_list[1]
        commit_message = amend_call[0][0][4]

        assert "Agent-Usage:" in commit_message
        assert "context7-engineer" in commit_message
        assert "playwright-engineer" in commit_message
        assert "test-automator" in commit_message

    def test_run_method_full_workflow(self, analyzer, complete_log_file, tmp_path):
        """Test the main run() method with complete workflow"""
        # Setup log directory
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "claude.log").write_text(complete_log_file.read_text(), encoding='utf-8')

        # Override log directory detection
        analyzer.log_dir = log_dir

        # Disable improvements to avoid API calls
        analyzer.config["improvement"]["auto_generate"] = False

        # Disable git metadata to avoid git calls
        analyzer.config["git_metadata"]["enabled"] = False

        # Run main workflow
        analyzer.run()

        # Verify it completes without errors (implicit test)

    def test_config_integration(self, tmp_path):
        """Test configuration loading and integration"""
        # Create custom config
        config_path = tmp_path / ".claude" / "optimizer-config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_content = """{
  "enabled": true,
  "log_analysis": {
    "max_log_size_mb": 5,
    "parse_timeout_seconds": 10
  },
  "improvement": {
    "auto_generate": false,
    "model": "claude-sonnet-4-20250514",
    "max_suggestions": 3
  },
  "git_metadata": {
    "enabled": false,
    "use_trailer": true,
    "amend_commit": true
  },
  "notification": {
    "console_output": false,
    "save_to_file": true
  }
}"""
        config_path.write_text(config_content, encoding='utf-8')

        # Create analyzer and verify config loaded
        analyzer = AgentUsageAnalyzer(tmp_path)

        assert analyzer.config["enabled"] is True
        assert analyzer.config["log_analysis"]["max_log_size_mb"] == 5
        assert analyzer.config["improvement"]["auto_generate"] is False
        assert analyzer.config["improvement"]["max_suggestions"] == 3
        assert analyzer.config["git_metadata"]["enabled"] is False
        assert analyzer.config["notification"]["console_output"] is False

    def test_error_resilience(self, analyzer, tmp_path):
        """Test that errors don't crash the system"""
        # Test with non-existent log file
        analyzer.log_dir = tmp_path / "nonexistent"
        analyzer.run()  # Should complete without error

        # Test with empty log file
        log_dir = tmp_path / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        empty_log = log_dir / "empty.log"
        empty_log.write_text("", encoding='utf-8')

        analyzer.log_dir = log_dir
        analyzer.run()  # Should complete without error

    def test_os_specific_log_detection(self, analyzer):
        """Test OS-specific log directory detection"""
        log_dir = analyzer.detect_claude_log_dir()

        # Should return a Path object
        assert isinstance(log_dir, Path) or log_dir is None

        # If on Windows, should contain APPDATA
        import os
        if os.name == 'nt' and os.getenv('APPDATA'):
            assert "Claude" in str(log_dir)

    @patch('subprocess.run')
    def test_end_to_end_with_all_features(self, mock_run, complete_log_file, tmp_path):
        """Comprehensive E2E test with all features enabled"""
        # Setup
        analyzer = AgentUsageAnalyzer(tmp_path)
        analyzer.log_dir = complete_log_file.parent

        # Mock Claude API
        mock_anthropic, mock_client = create_mock_anthropic()

        # Mock git
        mock_log_result = Mock()
        mock_log_result.stdout = "Test commit"
        mock_log_result.returncode = 0
        mock_run.return_value = mock_log_result

        # Run full workflow with patched anthropic
        with patch.dict('sys.modules', {'anthropic': mock_anthropic}):
            analyzer.run()

        # Verify all components were called
        # (Implicit: no exceptions raised means success)

        # Verify outputs exist
        suggestions_file = tmp_path / ".claude" / "improvement-suggestions.md"
        assert suggestions_file.exists()

    def test_concurrent_executions(self, analyzer, complete_log_file):
        """Test that multiple analyzer instances don't conflict"""
        analyzer2 = AgentUsageAnalyzer(analyzer.repo_root)

        # Both should be able to parse the same log
        calls1 = analyzer.parse_log_file(complete_log_file)
        calls2 = analyzer2.parse_log_file(complete_log_file)

        assert len(calls1) == len(calls2)

    def test_unicode_handling(self, analyzer, tmp_path):
        """Test handling of Unicode characters in logs"""
        log_content = """[2025-01-13T10:00:00Z] Task execution started
Agent type: context7-engineer
Prompt: "한글 프롬프트 테스트 🚀"
[2025-01-13T10:00:01Z] Success
"""
        log_file = tmp_path / "unicode.log"
        log_file.write_text(log_content, encoding='utf-8')

        agent_calls = analyzer.parse_log_file(log_file)

        assert len(agent_calls) == 1
        assert "한글" in agent_calls[0]["prompt"]
        assert "🚀" in agent_calls[0]["prompt"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
