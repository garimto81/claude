#!/usr/bin/env python3
"""Tests for Figma URL parser."""
import sys
sys.path.insert(0, "C:/claude")
import pytest
from lib.figma.url_parser import parse_figma_url, validate_figma_url


class TestParseFigmaUrl:
    def test_design_url_with_node_id(self):
        url = "https://www.figma.com/design/ABC123/MyFile?node-id=1-2"
        result = parse_figma_url(url)
        assert result["file_key"] == "ABC123"
        assert result["node_id"] == "1:2"
        assert result["file_name"] == "MyFile"

    def test_file_url_with_node_id(self):
        url = "https://figma.com/file/XYZ789/Title?node-id=42-15"
        result = parse_figma_url(url)
        assert result["file_key"] == "XYZ789"
        assert result["node_id"] == "42:15"

    def test_url_without_node_id(self):
        url = "https://www.figma.com/design/ABC123/MyFile"
        result = parse_figma_url(url)
        assert result["file_key"] == "ABC123"
        assert result["node_id"] is None

    def test_url_with_extra_params(self):
        url = "https://figma.com/design/KEY/Name?node-id=10-5&t=abc123"
        result = parse_figma_url(url)
        assert result["file_key"] == "KEY"
        assert result["node_id"] == "10:5"

    def test_invalid_url(self):
        with pytest.raises(ValueError):
            parse_figma_url("https://google.com")


class TestValidateFigmaUrl:
    def test_valid_design_url(self):
        assert validate_figma_url("https://www.figma.com/design/ABC/File") is True

    def test_valid_file_url(self):
        assert validate_figma_url("https://figma.com/file/ABC/File") is True

    def test_invalid_url(self):
        assert validate_figma_url("https://google.com") is False

    def test_empty_string(self):
        assert validate_figma_url("") is False
