# tests/prompt_learning/test_claude_md_updater.py
"""
CLAUDE.md Updater 테스트

pytest tests/prompt_learning/test_claude_md_updater.py -v
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# 패키지로 임포트 가능하도록 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))

from prompt_learning.claude_md_updater import (
    ClaudeMDUpdater,
    UpdateProposal,
    UpdateResult,
    create_updater,
    propose_update,
)
from prompt_learning.pattern_detector import Pattern, PatternReport
from prompt_learning.failure_analyzer import FailureCategory


class TestUpdateProposal:
    """UpdateProposal 테스트"""

    def test_create_proposal(self):
        """제안 생성"""
        proposal = UpdateProposal(
            proposal_id="test-1",
            section="1. Critical Instructions",
            original_content="old",
            proposed_content="new",
            reason="테스트 이유",
            confidence=0.85
        )
        assert proposal.proposal_id == "test-1"
        assert proposal.confidence == 0.85

    def test_is_high_confidence_true(self):
        """높은 신뢰도"""
        proposal = UpdateProposal(
            proposal_id="test",
            section="test",
            original_content="",
            proposed_content="",
            reason="",
            confidence=0.9
        )
        assert proposal.is_high_confidence is True

    def test_is_high_confidence_false(self):
        """낮은 신뢰도"""
        proposal = UpdateProposal(
            proposal_id="test",
            section="test",
            original_content="",
            proposed_content="",
            reason="",
            confidence=0.5
        )
        assert proposal.is_high_confidence is False

    def test_to_dict(self):
        """딕셔너리 변환"""
        proposal = UpdateProposal(
            proposal_id="test-1",
            section="test section",
            original_content="old",
            proposed_content="new",
            reason="reason",
            confidence=0.8
        )
        d = proposal.to_dict()
        assert d["proposal_id"] == "test-1"
        assert d["is_high_confidence"] is True


class TestClaudeMDUpdater:
    """ClaudeMDUpdater 테스트"""

    def test_create_updater(self):
        """업데이터 생성"""
        updater = ClaudeMDUpdater()
        assert updater.claude_md_path is None

    def test_create_updater_with_path(self):
        """경로와 함께 업데이터 생성"""
        updater = ClaudeMDUpdater("/path/to/CLAUDE.md")
        # Windows/Unix 경로 모두 지원
        assert "CLAUDE.md" in str(updater.claude_md_path)

    def test_set_path(self):
        """경로 설정"""
        updater = ClaudeMDUpdater()
        updater.set_path("/new/path")
        # Windows/Unix 경로 모두 지원
        assert "new" in str(updater.claude_md_path)


class TestGenerateProposal:
    """제안 생성 테스트"""

    def test_generate_proposal_path_error(self):
        """경로 오류 패턴 제안"""
        updater = ClaudeMDUpdater()
        pattern = Pattern(
            pattern_id="path-1",
            category=FailureCategory.PATH_ERROR,
            description="파일 경로 오류",
            occurrence_count=5,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        proposal = updater.generate_proposal(pattern)
        assert proposal is not None
        assert proposal.section == "1. Critical Instructions"
        assert "경로" in proposal.proposed_content

    def test_generate_proposal_phase_violation(self):
        """Phase 위반 패턴 제안"""
        updater = ClaudeMDUpdater()
        pattern = Pattern(
            pattern_id="phase-1",
            category=FailureCategory.PHASE_VIOLATION,
            description="Phase 순서 위반",
            occurrence_count=3,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="increasing"
        )
        proposal = updater.generate_proposal(pattern)
        assert proposal is not None
        assert "Phase" in proposal.proposed_content

    def test_generate_proposal_tdd_violation(self):
        """TDD 위반 패턴 제안"""
        updater = ClaudeMDUpdater()
        pattern = Pattern(
            pattern_id="tdd-1",
            category=FailureCategory.TDD_VIOLATION,
            description="TDD 순서 위반",
            occurrence_count=4,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        proposal = updater.generate_proposal(pattern)
        assert proposal is not None
        assert "TDD" in proposal.proposed_content

    def test_generate_proposal_unknown_category(self):
        """알 수 없는 카테고리"""
        updater = ClaudeMDUpdater()
        pattern = Pattern(
            pattern_id="unknown-1",
            category=FailureCategory.UNKNOWN,
            description="알 수 없음",
            occurrence_count=2,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        proposal = updater.generate_proposal(pattern)
        assert proposal is None

    def test_generate_proposals_from_report(self):
        """리포트에서 제안 생성"""
        updater = ClaudeMDUpdater()
        pattern1 = Pattern(
            pattern_id="path-1",
            category=FailureCategory.PATH_ERROR,
            description="path error",
            occurrence_count=3,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        pattern2 = Pattern(
            pattern_id="tdd-1",
            category=FailureCategory.TDD_VIOLATION,
            description="tdd error",
            occurrence_count=2,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        report = PatternReport(
            total_patterns=2,
            critical_patterns=0,
            patterns=[pattern1, pattern2],
            recommendations=[]
        )
        proposals = updater.generate_proposals_from_report(report)
        assert len(proposals) == 2


class TestPreviewChanges:
    """미리보기 테스트"""

    def test_preview_no_proposals(self):
        """제안 없음"""
        updater = ClaudeMDUpdater()
        preview = updater.preview_changes()
        assert "적용할 제안이 없습니다" in preview

    def test_preview_with_proposals(self):
        """제안 있음"""
        updater = ClaudeMDUpdater()
        pattern = Pattern(
            pattern_id="test",
            category=FailureCategory.PATH_ERROR,
            description="test",
            occurrence_count=3,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        updater.generate_proposal(pattern)
        preview = updater.preview_changes()
        assert "변경 제안 미리보기" in preview
        assert "이유" in preview


class TestApplyProposals:
    """제안 적용 테스트"""

    def test_apply_no_path(self):
        """경로 없음"""
        updater = ClaudeMDUpdater()
        result = updater.apply_proposals()
        assert result.success is False
        assert "경로가 설정되지 않았습니다" in result.error_message

    def test_apply_file_not_found(self):
        """파일 없음"""
        updater = ClaudeMDUpdater("/nonexistent/CLAUDE.md")
        result = updater.apply_proposals()
        assert result.success is False
        assert "파일을 찾을 수 없습니다" in result.error_message

    def test_apply_no_proposals(self):
        """적용할 제안 없음"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("# CLAUDE.md\n")
            temp_path = f.name

        try:
            updater = ClaudeMDUpdater(temp_path)
            result = updater.apply_proposals()
            assert result.success is True
            assert result.proposals_applied == 0
        finally:
            os.unlink(temp_path)

    def test_apply_with_backup(self):
        """백업과 함께 적용"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("# CLAUDE.md\n\n## 1. Critical Instructions\n\nSome content.\n")
            temp_path = f.name

        try:
            updater = ClaudeMDUpdater(temp_path)
            pattern = Pattern(
                pattern_id="test",
                category=FailureCategory.PATH_ERROR,
                description="test",
                occurrence_count=10,  # 높은 신뢰도를 위해
                first_seen="",
                last_seen="",
                affected_sessions=[],
                trend="stable"
            )
            updater.generate_proposal(pattern)
            result = updater.apply_proposals(backup=True)

            assert result.success is True
            assert result.backup_path is not None
            assert os.path.exists(result.backup_path)

            # 백업 파일 정리
            if result.backup_path:
                os.unlink(result.backup_path)
        finally:
            os.unlink(temp_path)


class TestRollback:
    """롤백 테스트"""

    def test_rollback_no_path(self):
        """경로 없음"""
        updater = ClaudeMDUpdater()
        result = updater.rollback("/some/backup")
        assert result is False

    def test_rollback_backup_not_found(self):
        """백업 파일 없음"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name

        try:
            updater = ClaudeMDUpdater(temp_path)
            result = updater.rollback("/nonexistent/backup")
            assert result is False
        finally:
            os.unlink(temp_path)

    def test_rollback_success(self):
        """롤백 성공"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("modified content")
            temp_path = f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md.backup', delete=False, encoding='utf-8') as f:
            f.write("original content")
            backup_path = f.name

        try:
            updater = ClaudeMDUpdater(temp_path)
            result = updater.rollback(backup_path)
            assert result is True

            # 원본 내용 복원 확인
            content = Path(temp_path).read_text()
            assert content == "original content"
        finally:
            os.unlink(temp_path)
            os.unlink(backup_path)


class TestProposalManagement:
    """제안 관리 테스트"""

    def test_get_proposals(self):
        """제안 목록 조회"""
        updater = ClaudeMDUpdater()
        pattern = Pattern(
            pattern_id="test",
            category=FailureCategory.PATH_ERROR,
            description="test",
            occurrence_count=3,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        updater.generate_proposal(pattern)
        proposals = updater.get_proposals()
        assert len(proposals) == 1

    def test_clear_proposals(self):
        """제안 초기화"""
        updater = ClaudeMDUpdater()
        pattern = Pattern(
            pattern_id="test",
            category=FailureCategory.PATH_ERROR,
            description="test",
            occurrence_count=3,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        updater.generate_proposal(pattern)
        assert len(updater.get_proposals()) == 1

        updater.clear_proposals()
        assert len(updater.get_proposals()) == 0


class TestConvenienceFunctions:
    """편의 함수 테스트"""

    def test_create_updater(self):
        """create_updater 함수"""
        updater = create_updater("/path/to/CLAUDE.md")
        # Windows/Unix 경로 모두 지원
        assert "CLAUDE.md" in str(updater.claude_md_path)

    def test_propose_update(self):
        """propose_update 함수"""
        pattern = Pattern(
            pattern_id="test",
            category=FailureCategory.PATH_ERROR,
            description="test",
            occurrence_count=3,
            first_seen="",
            last_seen="",
            affected_sessions=[],
            trend="stable"
        )
        proposal = propose_update(pattern, "/path/to/CLAUDE.md")
        assert proposal is not None
