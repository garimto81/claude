#!/usr/bin/env python3
"""
Tests for prompt improvement functionality
"""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

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
    return mock_anthropic, mock_client, mock_response


class TestPromptOptimizer:
    """Test suite for prompt improvement"""

    @pytest.fixture
    def analyzer(self, tmp_path):
        """Create analyzer instance with temporary repo root"""
        return AgentUsageAnalyzer(tmp_path)

    @pytest.fixture
    def sample_failures(self):
        """Create sample failure data"""
        return [
            {
                "agent_type": "context7-engineer",
                "prompt": "Check docs",
                "error": "Cannot find documentation",
                "failure_cause": "ambiguous_prompt",
            },
            {
                "agent_type": "playwright-engineer",
                "prompt": "Run tests",
                "error": "Timeout after 30 seconds",
                "failure_cause": "timeout",
            },
            {
                "agent_type": "test-automator",
                "prompt": "Create test for user authentication module",
                "error": "Missing test file",
                "failure_cause": "missing_context",
            },
        ]

    def test_generate_improvements_disabled(self, analyzer, sample_failures):
        """Test that improvements are not generated when disabled"""
        analyzer.config["improvement"]["auto_generate"] = False

        improvements = analyzer.generate_improvements(sample_failures)
        assert len(improvements) == 0

    def test_generate_improvements_success(self, analyzer, sample_failures):
        """Test successful prompt improvement generation"""
        # Mock the Anthropic module
        mock_anthropic, mock_client, mock_response = create_mock_anthropic()
        mock_response.content = [
            Mock(
                text="Improved prompt: Verify the latest React 18 documentation from official sources"
            )
        ]

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            improvements = analyzer.generate_improvements(sample_failures)

        assert len(improvements) > 0
        assert len(improvements) <= analyzer.config["improvement"]["max_suggestions"]

        # Check improvement structure
        for improvement in improvements:
            assert "agent" in improvement
            assert "original_prompt" in improvement
            assert "error" in improvement
            assert "failure_cause" in improvement
            assert "improved_prompt" in improvement
            assert len(improvement["improved_prompt"]) > 0

    def test_generate_improvements_respects_max_suggestions(self, analyzer):
        """Test that max_suggestions limit is respected"""
        # Create more failures than max_suggestions
        many_failures = [
            {
                "agent_type": f"test-agent-{i}",
                "prompt": f"test prompt {i}",
                "error": f"error {i}",
                "failure_cause": "unknown",
            }
            for i in range(10)
        ]

        mock_anthropic, mock_client, _ = create_mock_anthropic()

        analyzer.config["improvement"]["max_suggestions"] = 3
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            improvements = analyzer.generate_improvements(many_failures)

        assert len(improvements) <= 3

    def test_generate_improvements_uses_correct_model(self, analyzer, sample_failures):
        """Test that the configured model is used"""
        mock_anthropic, mock_client, _ = create_mock_anthropic()

        analyzer.config["improvement"]["model"] = "claude-sonnet-4-20250514"
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            analyzer.generate_improvements(sample_failures[:1])

        # Verify the model parameter
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-20250514"

    def test_generate_improvements_anthropic_not_installed(
        self, analyzer, sample_failures
    ):
        """Test graceful handling when anthropic package is not installed"""
        with patch(
            "builtins.__import__",
            side_effect=ImportError("No module named 'anthropic'"),
        ):
            improvements = analyzer.generate_improvements(sample_failures)
            assert len(improvements) == 0

    def test_generate_improvements_api_error(self, analyzer, sample_failures, tmp_path):
        """Test handling of API errors"""
        mock_anthropic, mock_client, _ = create_mock_anthropic()
        mock_client.messages.create.side_effect = Exception("API Error")

        # Ensure .claude directory exists
        (tmp_path / ".claude").mkdir(parents=True, exist_ok=True)

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            improvements = analyzer.generate_improvements(sample_failures)

        # Should return empty list and log error
        assert len(improvements) == 0

        # Check error log was created
        error_log = tmp_path / ".claude" / "optimizer-error.log"
        assert error_log.exists()

    def test_generate_improvements_prompt_format(self, analyzer, sample_failures):
        """Test that the prompt sent to Claude API is correctly formatted"""
        mock_anthropic, mock_client, _ = create_mock_anthropic()

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            analyzer.generate_improvements(sample_failures[:1])

        # Check the prompt includes all necessary information
        call_args = mock_client.messages.create.call_args[1]
        prompt_text = call_args["messages"][0]["content"]

        assert "context7-engineer" in prompt_text
        assert "Check docs" in prompt_text
        assert "ambiguous_prompt" in prompt_text
        assert "Cannot find documentation" in prompt_text

    def test_save_improvements_creates_file(self, analyzer, tmp_path):
        """Test that save_improvements creates the suggestions file"""
        improvements = [
            {
                "agent": "test-agent",
                "original_prompt": "Test",
                "error": "Test error",
                "improved_prompt": "Improved test prompt",
            }
        ]

        analyzer.save_improvements(improvements)

        suggestions_file = tmp_path / ".claude" / "improvement-suggestions.md"
        assert suggestions_file.exists()

        content = suggestions_file.read_text(encoding="utf-8")
        assert "test-agent" in content
        assert "Test" in content
        assert "Improved test prompt" in content

    def test_save_improvements_appends(self, analyzer, tmp_path):
        """Test that save_improvements appends to existing file"""
        suggestions_file = tmp_path / ".claude" / "improvement-suggestions.md"
        suggestions_file.parent.mkdir(parents=True, exist_ok=True)
        suggestions_file.write_text("Existing content\n", encoding="utf-8")

        improvements = [
            {
                "agent": "test-agent",
                "original_prompt": "Test",
                "error": "Test error",
                "improved_prompt": "Improved",
            }
        ]

        analyzer.save_improvements(improvements)

        content = suggestions_file.read_text(encoding="utf-8")
        assert "Existing content" in content
        assert "test-agent" in content

    def test_save_improvements_empty_list(self, analyzer, tmp_path):
        """Test that save_improvements handles empty improvement list"""
        analyzer.save_improvements([])

        suggestions_file = tmp_path / ".claude" / "improvement-suggestions.md"
        assert not suggestions_file.exists()

    def test_save_improvements_markdown_format(self, analyzer, tmp_path):
        """Test that saved improvements use correct markdown format"""
        improvements = [
            {
                "agent": "test-agent",
                "original_prompt": "Original",
                "error": "Error message",
                "improved_prompt": "Improved",
            }
        ]

        analyzer.save_improvements(improvements)

        suggestions_file = tmp_path / ".claude" / "improvement-suggestions.md"
        content = suggestions_file.read_text(encoding="utf-8")

        # Check markdown formatting
        assert "##" in content  # Timestamp header
        assert "###" in content  # Agent header
        assert "**Original Prompt**" in content
        assert "**Error**" in content
        assert "**Improved Prompt**" in content
        assert "---" in content  # Separator

    def test_generate_improvements_preserves_metadata(self, analyzer, sample_failures):
        """Test that all failure metadata is preserved in improvements"""
        mock_anthropic, _, _ = create_mock_anthropic()

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            improvements = analyzer.generate_improvements(sample_failures[:1])

        assert len(improvements) == 1
        improvement = improvements[0]

        # Check all metadata fields are present
        assert improvement["agent"] == sample_failures[0]["agent_type"]
        assert improvement["original_prompt"] == sample_failures[0]["prompt"]
        assert improvement["error"] == sample_failures[0]["error"]
        assert improvement["failure_cause"] == sample_failures[0]["failure_cause"]
        assert "improved_prompt" in improvement


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
