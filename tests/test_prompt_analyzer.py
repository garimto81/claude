"""Tests for prompt_analyzer.py — Tier 1 통계 엔진."""

import json
import sys
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import pytest

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))

from prompt_analyzer import (
    analyze_prompts,
    categorize,
    extract_keywords,
    extract_skill,
    get_time_slot,
    load_prompts,
    merge_stats,
    normalize_prompt,
)


class TestCategorize:
    """카테고리 분류 규칙 테스트."""

    def test_categorize_command(self):
        assert categorize("/auto --eco") == "command"
        assert categorize("/commit") == "command"
        assert categorize("/audit config") == "command"

    def test_categorize_feature(self):
        assert categorize("새로운 스킬 추가해줘") == "feature"
        assert categorize("로그인 기능 구현") == "feature"
        assert categorize("add a new component") == "feature"
        assert categorize("버튼 생성해줘") == "feature"

    def test_categorize_fix(self):
        assert categorize("이 버그 수정해줘") == "fix"
        assert categorize("에러가 발생함") == "fix"
        assert categorize("fix the login issue") == "fix"

    def test_categorize_question(self):
        assert categorize("이게 어떻게 동작해?") == "question"
        assert categorize("왜 실패하지?") == "question"
        assert categorize("이 함수가 뭐야?") == "question"

    def test_categorize_config(self):
        assert categorize("hook 설정 변경") == "config"
        assert categorize("config 파일 열어줘") == "config"

    def test_categorize_research(self):
        assert categorize("코드 분석해줘") == "research"
        assert categorize("research best practices") == "research"

    def test_categorize_general(self):
        assert categorize("안녕하세요") == "general"
        assert categorize("ㅋㅋㅋ") == "general"

    def test_categorize_priority_command_over_feature(self):
        assert categorize("/auto 기능 추가") == "command"


class TestExtractSkill:
    def test_extract_skill_basic(self):
        assert extract_skill("/auto --eco") == "/auto"
        assert extract_skill("/commit") == "/commit"
        assert extract_skill("/audit config") == "/audit"

    def test_extract_skill_none(self):
        assert extract_skill("일반 프롬프트") is None
        assert extract_skill("fix something") is None


class TestExtractKeywords:
    def test_korean_keywords(self):
        kws = extract_keywords("새로운 스킬 추가 요청")
        assert "스킬" in kws
        assert "추가" in kws

    def test_english_keywords(self):
        kws = extract_keywords("fix the login component")
        assert "fix" in kws
        assert "login" in kws
        assert "component" in kws

    def test_mixed(self):
        kws = extract_keywords("audit 설정 점검")
        assert "audit" in kws
        assert "설정" in kws
        assert "점검" in kws


class TestGetTimeSlot:
    def test_slots_coverage(self):
        from datetime import datetime as dt
        slots = set()
        for hour in range(24):
            d = dt(2026, 3, 23, hour, 0, 0)
            ts = int(d.timestamp() * 1000)
            slots.add(get_time_slot(ts))
        assert slots == {"morning", "afternoon", "evening", "night"}


class TestLoadPrompts:
    def test_load_prompts_filters_by_project(self, tmp_path):
        history = tmp_path / "history.jsonl"
        entries = [
            {"display": "test1", "timestamp": 100, "project": "C:\\claude", "sessionId": "s1"},
            {"display": "test2", "timestamp": 200, "project": "C:\\other", "sessionId": "s2"},
            {"display": "test3", "timestamp": 300, "project": "C:\\claude", "sessionId": "s1"},
        ]
        history.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")

        with patch("prompt_analyzer.HISTORY_PATH", history):
            result = load_prompts(project_filter="C:\\claude")
            assert len(result) == 2
            assert all(r["project"] == "C:\\claude" for r in result)

    def test_load_new_prompts_after_watermark(self, tmp_path):
        history = tmp_path / "history.jsonl"
        entries = [
            {"display": "old", "timestamp": 100, "project": "C:\\claude", "sessionId": "s1"},
            {"display": "new1", "timestamp": 200, "project": "C:\\claude", "sessionId": "s2"},
            {"display": "new2", "timestamp": 300, "project": "C:\\claude", "sessionId": "s2"},
        ]
        history.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")

        with patch("prompt_analyzer.HISTORY_PATH", history):
            result = load_prompts(after_timestamp=150)
            assert len(result) == 2
            assert result[0]["display"] == "new1"
            assert result[1]["display"] == "new2"


class TestAnalyzePrompts:
    def test_category_frequency(self):
        prompts = [
            {"display": "/auto", "timestamp": 100, "sessionId": "s1", "project": ""},
            {"display": "/commit", "timestamp": 200, "sessionId": "s1", "project": ""},
            {"display": "버그 수정", "timestamp": 300, "sessionId": "s1", "project": ""},
            {"display": "기능 추가", "timestamp": 400, "sessionId": "s1", "project": ""},
        ]
        result = analyze_prompts(prompts)
        assert result["categories"]["command"] == 2
        assert result["categories"]["fix"] == 1
        assert result["categories"]["feature"] == 1

    def test_skill_usage_frequency(self):
        prompts = [
            {"display": "/auto --eco", "timestamp": 100, "sessionId": "s1", "project": ""},
            {"display": "/auto config", "timestamp": 200, "sessionId": "s1", "project": ""},
            {"display": "/commit", "timestamp": 300, "sessionId": "s1", "project": ""},
            {"display": "일반 텍스트", "timestamp": 400, "sessionId": "s1", "project": ""},
        ]
        result = analyze_prompts(prompts)
        assert result["skills"]["/auto"] == 2
        assert result["skills"]["/commit"] == 1

    def test_keyword_extraction(self):
        prompts = [
            {"display": "audit 설정 점검", "timestamp": 100, "sessionId": "s1", "project": ""},
            {"display": "audit 결과 확인", "timestamp": 200, "sessionId": "s1", "project": ""},
        ]
        result = analyze_prompts(prompts)
        assert result["keywords"]["audit"] == 2

    def test_repeat_detection(self):
        prompts = [
            {"display": "mockup 생성해줘", "timestamp": i * 100, "sessionId": "s1", "project": ""}
            for i in range(4)
        ]
        result = analyze_prompts(prompts)
        assert any(v >= 3 for v in result["repeats"].values())


class TestMergeStats:
    def test_merge_categories(self):
        existing = {"categories": {"command": 10, "fix": 5}, "skills": {},
                    "top_keywords": [], "time_slots": {}, "repeats": {},
                    "total_analyzed": 15, "sessions": {}}
        delta = {"categories": {"command": 3, "feature": 2}, "skills": {},
                 "keywords": Counter(), "time_slots": {}, "repeats": {},
                 "count": 5, "sessions": {}}
        result = merge_stats(existing, delta)
        assert result["categories"]["command"] == 13
        assert result["categories"]["fix"] == 5
        assert result["categories"]["feature"] == 2
        assert result["total_analyzed"] == 20


class TestNormalizePrompt:
    def test_normalize_whitespace(self):
        assert normalize_prompt("  hello   world  ") == "hello world"

    def test_normalize_case(self):
        assert normalize_prompt("Hello World") == "hello world"

    def test_normalize_paths(self):
        result = normalize_prompt("fix C:\\claude\\src\\main.py issue")
        assert "C:\\claude" not in result
