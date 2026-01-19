"""
tests/test_phase_detection.py

Phase 감지 스크립트 테스트

Usage:
    pytest tests/test_phase_detection.py -v
"""

import pytest
import sys
import os

# scripts 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

# Import the module (파일명에서 .py 제거하고 import)
from check_phase_completion import parse_commit_message, check_todo_completion


class TestParseCommitMessage:
    """커밋 메시지 파싱 테스트"""

    def test_valid_phase_completion_message(self):
        """유효한 Phase 완료 커밋 메시지 테스트"""
        message = "feat: Add auto PR system (v1.1.0) [PRD-0002]\n\nPhase 1 completed"
        result = parse_commit_message(message)

        assert result["phase_completed"] is True
        assert result["version"] == "1.1.0"
        assert result["prd_number"] == "0002"
        assert result["phase_number"] == "1"

    def test_message_without_version(self):
        """버전이 없는 커밋 메시지 테스트"""
        message = "feat: Add feature [PRD-0001]"
        result = parse_commit_message(message)

        assert result["phase_completed"] is False
        assert result["version"] is None
        assert result["prd_number"] == "0001"

    def test_message_without_prd(self):
        """PRD가 없는 커밋 메시지 테스트"""
        message = "feat: Add feature (v1.0.0)"
        result = parse_commit_message(message)

        assert result["phase_completed"] is False
        assert result["version"] == "1.0.0"
        assert result["prd_number"] is None

    def test_message_with_phase_2(self):
        """Phase 2 커밋 메시지 테스트"""
        message = "test: Add tests (v1.2.0) [PRD-0003]\n\nPhase 2: Testing"
        result = parse_commit_message(message)

        assert result["phase_completed"] is True
        assert result["phase_number"] == "2"
        assert result["prd_number"] == "0003"

    def test_message_case_insensitive_phase(self):
        """Phase 대소문자 구분 없이 테스트"""
        message = "feat: Complete phase 3 (v1.0.0) [PRD-0001]"
        result = parse_commit_message(message)

        assert result["phase_completed"] is True
        assert result["phase_number"] == "3"

    def test_message_without_phase_keyword(self):
        """Phase 키워드가 없는 커밋 메시지 테스트"""
        message = "feat: Add feature (v1.0.0) [PRD-0001]"
        result = parse_commit_message(message)

        assert result["phase_completed"] is True
        assert result["phase_number"] is None

    def test_invalid_version_format(self):
        """잘못된 버전 형식 테스트"""
        message = "feat: Add feature (v1.0) [PRD-0001]"
        result = parse_commit_message(message)

        assert result["phase_completed"] is False
        assert result["version"] is None

    def test_invalid_prd_format(self):
        """잘못된 PRD 형식 테스트"""
        message = "feat: Add feature (v1.0.0) [PRD-001]"
        result = parse_commit_message(message)

        assert result["phase_completed"] is False
        assert result["prd_number"] is None

    def test_multiple_phase_keywords(self):
        """여러 Phase 키워드가 있을 때 첫 번째만 추출"""
        message = "feat: Phase 1 and Phase 2 (v1.0.0) [PRD-0001]"
        result = parse_commit_message(message)

        assert result["phase_completed"] is True
        assert result["phase_number"] == "1"

    def test_phase_number_out_of_range(self):
        """Phase 번호가 1-6 범위 밖인 경우"""
        message = "feat: Phase 7 completed (v1.0.0) [PRD-0001]"
        result = parse_commit_message(message)

        assert result["phase_completed"] is True
        assert result["phase_number"] is None  # 7은 매칭 안됨

    def test_multiline_commit_message(self):
        """여러 줄 커밋 메시지 테스트"""
        message = """feat: Add authentication system (v2.0.0) [PRD-0005]

Phase 1 completed:
- User login
- JWT tokens
- Password hashing

Co-Authored-By: Claude <noreply@anthropic.com>"""
        result = parse_commit_message(message)

        assert result["phase_completed"] is True
        assert result["version"] == "2.0.0"
        assert result["prd_number"] == "0005"
        assert result["phase_number"] == "1"
        assert "Co-Authored-By" in result["commit_message"]


class TestCheckTodoCompletion:
    """Todo 완료 상태 확인 테스트"""

    def test_nonexistent_todo_file(self):
        """존재하지 않는 Todo 파일 테스트"""
        result = check_todo_completion("9999")

        assert result["todo_exists"] is False
        assert result["total_tasks"] == 0
        assert result["completed_tasks"] == 0
        assert result["completion_rate"] == 0.0

    def test_todo_completion_rate_calculation(self):
        """Todo 완료율 계산 테스트 (모의 파일)"""
        # 이 테스트는 실제 Todo 파일이 있어야 작동합니다
        # PRD-0002의 Todo 파일이 있는 경우
        result = check_todo_completion("0002")

        # 파일이 있으면 검증
        if result["todo_exists"]:
            assert result["total_tasks"] > 0
            assert result["completed_tasks"] >= 0
            assert 0 <= result["completion_rate"] <= 100
        else:
            # 파일이 없으면 기본값 검증
            assert result["total_tasks"] == 0


# Parametrized tests
@pytest.mark.parametrize(
    "message,expected_phase,expected_prd,expected_completed",
    [
        ("feat: Phase 1 (v1.0.0) [PRD-0001]", "1", "0001", True),
        ("fix: Phase 2 bug (v1.0.1) [PRD-0001]", "2", "0001", True),
        ("docs: Phase 3 (v1.1.0) [PRD-0002]", "3", "0002", True),
        ("refactor: Phase 4 (v2.0.0) [PRD-0003]", "4", "0003", True),
        ("perf: Phase 5 (v1.2.0) [PRD-0001]", "5", "0001", True),
        ("test: Phase 6 (v1.0.0) [PRD-0004]", "6", "0004", True),
        ("feat: No phase (v1.0.0) [PRD-0001]", None, "0001", True),
        ("feat: Missing version [PRD-0001]", None, "0001", False),
        ("feat: Missing PRD (v1.0.0)", None, None, False),
    ],
)
def test_various_commit_patterns(
    message, expected_phase, expected_prd, expected_completed
):
    """다양한 커밋 패턴 테스트"""
    result = parse_commit_message(message)

    assert result["phase_number"] == expected_phase
    assert result["prd_number"] == expected_prd
    assert result["phase_completed"] == expected_completed


# Edge cases
class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_empty_message(self):
        """빈 커밋 메시지 테스트"""
        result = parse_commit_message("")

        assert result["phase_completed"] is False
        assert result["version"] is None
        assert result["prd_number"] is None
        assert result["phase_number"] is None

    def test_unicode_characters(self):
        """유니코드 문자 포함 테스트"""
        message = "feat: 사용자 인증 추가 (v1.0.0) [PRD-0001]\n\nPhase 1 완료 ✅"
        result = parse_commit_message(message)

        assert result["phase_completed"] is True
        assert result["version"] == "1.0.0"
        assert result["prd_number"] == "0001"
        assert "✅" in result["commit_message"]

    def test_special_characters_in_version(self):
        """버전에 특수문자가 포함된 경우"""
        message = "feat: Add feature (v1.0.0-beta) [PRD-0001]"
        result = parse_commit_message(message)

        # v1.0.0-beta는 패턴에 맞지 않음 (X.Y.Z만 허용)
        assert result["version"] is None

    def test_prd_with_leading_zeros(self):
        """PRD 번호 앞에 0이 있는 경우"""
        message = "feat: Add feature (v1.0.0) [PRD-0001]"
        result = parse_commit_message(message)

        assert result["prd_number"] == "0001"

    def test_very_long_commit_message(self):
        """매우 긴 커밋 메시지 테스트"""
        long_desc = "A" * 10000
        message = f"feat: {long_desc} (v1.0.0) [PRD-0001]"
        result = parse_commit_message(message)

        assert result["phase_completed"] is True
        assert len(result["commit_message"]) > 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
