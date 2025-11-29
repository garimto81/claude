# tests/prompt_learning/test_claude_md_validator.py
"""
Claude MD Validator Hook 테스트

pytest tests/prompt_learning/test_claude_md_validator.py -v
"""

import pytest
import sys
import os

# Hook 모듈 임포트를 위한 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '.claude', 'hooks'))

from claude_md_validator import (
    validate_prompt,
    format_feedback,
    get_action,
    Violation,
    Severity,
    RULES
)


class TestValidatePrompt:
    """validate_prompt 함수 테스트"""

    def test_clean_prompt_passes(self):
        """정상 프롬프트는 위반 없음"""
        prompt = "D:\\AI\\claude01\\src 폴더의 파일을 분석해주세요"
        violations = validate_prompt(prompt)
        assert len(violations) == 0

    def test_clean_prompt_korean(self):
        """한글 프롬프트는 통과"""
        prompt = "Phase 0부터 PRD를 작성해주세요"
        violations = validate_prompt(prompt)
        assert len(violations) == 0

    def test_relative_path_violation(self):
        """상대 경로 사용 감지"""
        prompts = [
            "cd ./src && run tests",
            "./scripts/run.sh 실행해줘",
            "cd src/agents 폴더로 이동"
        ]
        for prompt in prompts:
            violations = validate_prompt(prompt)
            assert any(v.rule_id == "relative_path" for v in violations), f"Failed for: {prompt}"

    def test_skip_validation_blocked(self):
        """Phase 검증 건너뛰기 차단"""
        prompts = [
            "skip phase validation",
            "validation을 건너뛰고 진행해줘",
            "skip validation and proceed"
        ]
        for prompt in prompts:
            violations = validate_prompt(prompt)
            assert any(v.rule_id == "skip_validation" for v in violations), f"Failed for: {prompt}"
            assert any(v.severity == Severity.CRITICAL for v in violations), f"Should be CRITICAL: {prompt}"

    def test_phase_jump_violation(self):
        """Phase 건너뛰기 감지"""
        prompts = [
            "Phase 3부터 시작해줘",
            "skip to phase 2",
            "phase 4로 바로 가자",
            "phase 5으로 직접 이동"
        ]
        for prompt in prompts:
            violations = validate_prompt(prompt)
            assert any(v.rule_id == "phase_jump" for v in violations), f"Failed for: {prompt}"

    def test_implement_before_test_violation(self):
        """TDD 순서 위반 감지"""
        prompts = [
            "구현 먼저 하고 테스트는 나중에",
            "implement first without test",
            "테스트 없이 코드 작성해줘"
        ]
        for prompt in prompts:
            violations = validate_prompt(prompt)
            assert any(v.rule_id == "implement_before_test" for v in violations), f"Failed for: {prompt}"

    def test_english_output_warning(self):
        """영어 출력 요청 감지"""
        prompts = [
            "respond in english please",
            "영어로 대답해줘"
        ]
        for prompt in prompts:
            violations = validate_prompt(prompt)
            assert any(v.rule_id == "english_output" for v in violations), f"Failed for: {prompt}"


class TestGetAction:
    """get_action 함수 테스트"""

    def test_no_violations_proceed(self):
        """위반 없으면 proceed"""
        assert get_action([]) == "proceed"

    def test_critical_blocks(self):
        """CRITICAL 위반은 block"""
        violations = [
            Violation(
                rule_id="skip_validation",
                message="test",
                severity=Severity.CRITICAL
            )
        ]
        assert get_action(violations) == "block"

    def test_high_warns(self):
        """HIGH 위반은 warn"""
        violations = [
            Violation(
                rule_id="relative_path",
                message="test",
                severity=Severity.HIGH
            )
        ]
        assert get_action(violations) == "warn"

    def test_medium_proceeds(self):
        """MEDIUM 위반은 proceed (로그만)"""
        violations = [
            Violation(
                rule_id="english_output",
                message="test",
                severity=Severity.MEDIUM
            )
        ]
        assert get_action(violations) == "proceed"

    def test_multiple_violations_highest_wins(self):
        """여러 위반 시 가장 높은 심각도 적용"""
        violations = [
            Violation(rule_id="test1", message="test", severity=Severity.LOW),
            Violation(rule_id="test2", message="test", severity=Severity.CRITICAL),
            Violation(rule_id="test3", message="test", severity=Severity.MEDIUM),
        ]
        assert get_action(violations) == "block"


class TestFormatFeedback:
    """format_feedback 함수 테스트"""

    def test_empty_violations(self):
        """위반 없으면 빈 문자열"""
        assert format_feedback([]) == ""

    def test_format_single_violation(self):
        """단일 위반 포맷"""
        violations = [
            Violation(
                rule_id="test_rule",
                message="테스트 메시지",
                severity=Severity.HIGH,
                suggestion="제안 사항"
            )
        ]
        result = format_feedback(violations)
        assert "CLAUDE.md 규칙 위반 감지" in result
        assert "test_rule" in result
        assert "테스트 메시지" in result
        assert "제안 사항" in result
        assert "🟠" in result  # HIGH severity icon

    def test_format_multiple_violations(self):
        """다중 위반 포맷"""
        violations = [
            Violation(rule_id="rule1", message="msg1", severity=Severity.CRITICAL),
            Violation(rule_id="rule2", message="msg2", severity=Severity.MEDIUM),
        ]
        result = format_feedback(violations)
        assert "rule1" in result
        assert "rule2" in result
        assert "🔴" in result  # CRITICAL
        assert "🟡" in result  # MEDIUM


class TestRulesCompleteness:
    """규칙 정의 완전성 테스트"""

    def test_all_rules_have_required_fields(self):
        """모든 규칙에 필수 필드 존재"""
        required_fields = ["pattern", "message", "severity"]
        for rule_id, rule in RULES.items():
            for field in required_fields:
                assert field in rule, f"Rule '{rule_id}' missing field '{field}'"

    def test_all_patterns_compile(self):
        """모든 패턴이 유효한 정규식"""
        import re
        for rule_id, rule in RULES.items():
            try:
                re.compile(rule["pattern"])
            except re.error as e:
                pytest.fail(f"Rule '{rule_id}' has invalid pattern: {e}")

    def test_minimum_rules_count(self):
        """최소 5개 규칙 정의"""
        assert len(RULES) >= 5, f"Expected at least 5 rules, got {len(RULES)}"


class TestEdgeCases:
    """경계 케이스 테스트"""

    def test_empty_prompt(self):
        """빈 프롬프트"""
        violations = validate_prompt("")
        assert len(violations) == 0

    def test_whitespace_only_prompt(self):
        """공백만 있는 프롬프트"""
        violations = validate_prompt("   \n\t  ")
        assert len(violations) == 0

    def test_unicode_prompt(self):
        """유니코드 프롬프트"""
        prompt = "한글과 日本語와 emoji 🎉 테스트"
        violations = validate_prompt(prompt)
        assert len(violations) == 0

    def test_very_long_prompt(self):
        """매우 긴 프롬프트"""
        prompt = "정상적인 내용 " * 10000
        violations = validate_prompt(prompt)
        assert len(violations) == 0

    def test_case_insensitive_matching(self):
        """대소문자 무관 매칭"""
        prompts = [
            "SKIP VALIDATION",
            "Skip Validation",
            "sKiP vAlIdAtIoN"
        ]
        for prompt in prompts:
            violations = validate_prompt(prompt)
            assert any(v.rule_id == "skip_validation" for v in violations), f"Failed for: {prompt}"


# ============================================================================
# 실제 사용 시나리오 테스트
# ============================================================================

class TestRealWorldScenarios:
    """실제 사용 시나리오 테스트"""

    def test_valid_prd_creation_request(self):
        """유효한 PRD 생성 요청"""
        prompt = "Phase 0을 시작해서 사용자 인증 기능에 대한 PRD를 작성해주세요"
        violations = validate_prompt(prompt)
        assert len(violations) == 0

    def test_valid_tdd_request(self):
        """유효한 TDD 요청"""
        prompt = "테스트를 먼저 작성하고 구현해주세요. TDD 방식으로 진행합니다."
        violations = validate_prompt(prompt)
        assert len(violations) == 0

    def test_valid_absolute_path_request(self):
        """유효한 절대 경로 요청"""
        prompt = "D:\\AI\\claude01\\src\\agents 폴더의 파일을 수정해주세요"
        violations = validate_prompt(prompt)
        assert len(violations) == 0

    def test_invalid_shortcut_request(self):
        """잘못된 단축 요청"""
        prompt = "검증을 건너뛰고 바로 Phase 3으로 가서 배포해줘"
        violations = validate_prompt(prompt)
        # skip_validation이 감지되어야 함
        rule_ids = [v.rule_id for v in violations]
        assert "skip_validation" in rule_ids, f"Expected skip_validation, got: {rule_ids}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
