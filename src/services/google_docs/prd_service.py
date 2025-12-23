"""
PRD Service

Google Docs 기반 PRD 생성 및 관리 서비스.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .client import GoogleDocsClient
from .metadata_manager import MetadataManager, PRDMetadata

logger = logging.getLogger(__name__)


@dataclass
class PRDSection:
    """PRD 섹션 정의"""

    title: str
    content: str = ""
    heading_level: int = 2


@dataclass
class PRDTemplate:
    """PRD 템플릿"""

    # 메타데이터
    prd_id: str = ""
    title: str = ""
    version: str = "1.0"
    status: str = "Draft"
    priority: str = "P1"
    created_date: str = ""
    author: str = "Claude Code"

    # 섹션 내용
    executive_summary: str = ""
    problem_statement: str = ""
    target_users: str = ""
    goals: str = ""
    requirements: str = ""
    technical_design: str = ""
    success_metrics: str = ""
    timeline: str = ""
    risks: str = ""
    open_questions: str = ""

    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().strftime("%Y-%m-%d")

    def to_document_content(self) -> str:
        """문서 전체 내용 생성"""
        lines = []

        # 제목
        lines.append(f"# {self.prd_id}: {self.title}\n\n")

        # 메타데이터 테이블
        lines.append("| 항목 | 값 |\n")
        lines.append("|------|----|\n")
        lines.append(f"| **Version** | {self.version} |\n")
        lines.append(f"| **Status** | {self.status} |\n")
        lines.append(f"| **Priority** | {self.priority} |\n")
        lines.append(f"| **Created** | {self.created_date} |\n")
        lines.append(f"| **Author** | {self.author} |\n")
        lines.append("\n---\n\n")

        # Executive Summary
        if self.executive_summary:
            lines.append("## Executive Summary\n\n")
            lines.append(f"{self.executive_summary}\n\n")

        # Problem Statement
        if self.problem_statement:
            lines.append("## Problem Statement\n\n")
            lines.append(f"{self.problem_statement}\n\n")

        # Target Users
        if self.target_users:
            lines.append("## Target Users\n\n")
            lines.append(f"{self.target_users}\n\n")

        # Goals
        if self.goals:
            lines.append("## Goals\n\n")
            lines.append(f"{self.goals}\n\n")

        # Requirements
        if self.requirements:
            lines.append("## Requirements\n\n")
            lines.append(f"{self.requirements}\n\n")

        # Technical Design
        if self.technical_design:
            lines.append("## Technical Design\n\n")
            lines.append(f"{self.technical_design}\n\n")

        # Success Metrics
        if self.success_metrics:
            lines.append("## Success Metrics\n\n")
            lines.append(f"{self.success_metrics}\n\n")

        # Timeline
        if self.timeline:
            lines.append("## Timeline\n\n")
            lines.append(f"{self.timeline}\n\n")

        # Risks
        if self.risks:
            lines.append("## Risks & Mitigations\n\n")
            lines.append(f"{self.risks}\n\n")

        # Open Questions
        if self.open_questions:
            lines.append("## Open Questions\n\n")
            lines.append(f"{self.open_questions}\n\n")

        # Footer
        lines.append("---\n\n")
        lines.append(f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

        return "".join(lines)


class PRDService:
    """PRD 관리 서비스"""

    def __init__(
        self,
        client: Optional[GoogleDocsClient] = None,
        metadata_manager: Optional[MetadataManager] = None,
    ):
        """
        초기화

        Args:
            client: Google Docs 클라이언트
            metadata_manager: 메타데이터 관리자
        """
        self.client = client or GoogleDocsClient()
        self.metadata = metadata_manager or MetadataManager()

    # ==================== PRD Creation ====================

    def create_prd(
        self,
        title: str,
        template: Optional[PRDTemplate] = None,
        status: str = "Draft",
        priority: str = "P1",
        tags: Optional[List[str]] = None,
    ) -> PRDMetadata:
        """
        새 PRD 생성

        Args:
            title: PRD 제목
            template: PRD 템플릿 (None이면 기본 템플릿)
            status: 상태
            priority: 우선순위
            tags: 태그 목록

        Returns:
            생성된 PRDMetadata
        """
        # PRD ID 생성
        prd_id = self.metadata.generate_prd_id()

        # 템플릿 준비
        if template is None:
            template = PRDTemplate(prd_id=prd_id, title=title)
        else:
            template.prd_id = prd_id
            template.title = title

        # Google Docs 문서 생성
        doc_title = f"{prd_id}: {title}"
        doc_info = self.client.create_document(doc_title)

        # 문서 내용 삽입
        content = template.to_document_content()
        self.client.insert_text(doc_info["documentId"], content)

        # 메타데이터 저장
        metadata = self.metadata.add_prd(
            google_doc_id=doc_info["documentId"],
            title=title,
            status=status,
            priority=priority,
            tags=tags,
        )

        logger.info(f"PRD 생성 완료: {prd_id} - {title}")
        logger.info(f"  URL: {doc_info['url']}")

        return metadata

    def create_prd_from_questions(
        self,
        title: str,
        answers: Dict[str, str],
        priority: str = "P1",
        tags: Optional[List[str]] = None,
    ) -> PRDMetadata:
        """
        대화형 질문 답변으로 PRD 생성

        Args:
            title: PRD 제목
            answers: 질문별 답변 딕셔너리
            priority: 우선순위
            tags: 태그 목록

        Returns:
            생성된 PRDMetadata
        """
        template = PRDTemplate(
            title=title,
            priority=priority,
            executive_summary=answers.get("summary", ""),
            problem_statement=answers.get("problem", ""),
            target_users=answers.get("users", ""),
            goals=answers.get("goals", ""),
            requirements=answers.get("requirements", ""),
            technical_design=answers.get("technical", ""),
            success_metrics=answers.get("metrics", ""),
            timeline=answers.get("timeline", ""),
            risks=answers.get("risks", ""),
            open_questions=answers.get("questions", ""),
        )

        return self.create_prd(
            title=title,
            template=template,
            priority=priority,
            tags=tags,
        )

    # ==================== PRD Retrieval ====================

    def get_prd(self, prd_id: str) -> Optional[PRDMetadata]:
        """
        PRD 조회

        Args:
            prd_id: PRD ID

        Returns:
            PRDMetadata 또는 None
        """
        return self.metadata.get_prd(prd_id)

    def get_prd_content(self, prd_id: str) -> Optional[str]:
        """
        PRD 문서 내용 조회

        Args:
            prd_id: PRD ID

        Returns:
            문서 텍스트 또는 None
        """
        prd = self.get_prd(prd_id)
        if not prd:
            return None

        return self.client.get_document_text(prd.google_doc_id)

    def list_prds(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[PRDMetadata]:
        """
        PRD 목록 조회

        Args:
            status: 상태 필터
            priority: 우선순위 필터

        Returns:
            PRDMetadata 리스트
        """
        return self.metadata.list_prds(status=status, priority=priority)

    # ==================== PRD Update ====================

    def update_prd_status(self, prd_id: str, status: str) -> Optional[PRDMetadata]:
        """
        PRD 상태 업데이트

        Args:
            prd_id: PRD ID
            status: 새 상태

        Returns:
            업데이트된 PRDMetadata 또는 None
        """
        return self.metadata.update_prd(prd_id, status=status)

    def update_prd_priority(self, prd_id: str, priority: str) -> Optional[PRDMetadata]:
        """
        PRD 우선순위 업데이트

        Args:
            prd_id: PRD ID
            priority: 새 우선순위

        Returns:
            업데이트된 PRDMetadata 또는 None
        """
        return self.metadata.update_prd(prd_id, priority=priority)

    def append_to_prd(self, prd_id: str, section: str, content: str) -> bool:
        """
        PRD 문서에 내용 추가

        Args:
            prd_id: PRD ID
            section: 섹션 제목
            content: 추가할 내용

        Returns:
            성공 여부
        """
        prd = self.get_prd(prd_id)
        if not prd:
            logger.warning(f"PRD를 찾을 수 없음: {prd_id}")
            return False

        # 문서 끝에 내용 추가
        doc = self.client.get_document(prd.google_doc_id)
        body = doc.get("body", {})
        content_elements = body.get("content", [])

        # 마지막 인덱스 찾기
        end_index = 1
        for element in content_elements:
            if "endIndex" in element:
                end_index = element["endIndex"]

        # 새 섹션 추가
        new_content = f"\n\n## {section}\n\n{content}\n"
        self.client.insert_text(prd.google_doc_id, new_content, index=end_index - 1)

        # 메타데이터 업데이트
        self.metadata.update_prd(prd_id)

        logger.info(f"PRD 섹션 추가됨: {prd_id} - {section}")
        return True

    # ==================== PRD Deletion ====================

    def delete_prd(self, prd_id: str, delete_doc: bool = False) -> bool:
        """
        PRD 삭제

        Args:
            prd_id: PRD ID
            delete_doc: Google Docs 문서도 삭제할지 여부

        Returns:
            삭제 성공 여부
        """
        prd = self.get_prd(prd_id)
        if not prd:
            logger.warning(f"PRD를 찾을 수 없음: {prd_id}")
            return False

        # Google Docs 문서 삭제
        if delete_doc:
            try:
                self.client.delete_document(prd.google_doc_id)
            except Exception as e:
                logger.error(f"문서 삭제 실패: {e}")

        # 메타데이터 삭제
        return self.metadata.delete_prd(prd_id)

    # ==================== Utility ====================

    def get_prd_url(self, prd_id: str) -> Optional[str]:
        """
        PRD 문서 URL 조회

        Args:
            prd_id: PRD ID

        Returns:
            Google Docs URL 또는 None
        """
        prd = self.get_prd(prd_id)
        if prd:
            return prd.google_doc_url
        return None

    def sync_from_google(self, prd_id: str) -> Optional[PRDMetadata]:
        """
        Google Docs에서 메타데이터 동기화

        Args:
            prd_id: PRD ID

        Returns:
            업데이트된 PRDMetadata 또는 None
        """
        prd = self.get_prd(prd_id)
        if not prd:
            return None

        # Google Docs에서 문서 정보 조회
        try:
            doc = self.client.get_document(prd.google_doc_id)
            title = doc.get("title", prd.title)

            # 제목에서 PRD ID 제거
            if title.startswith(f"{prd_id}:"):
                title = title[len(f"{prd_id}:"):].strip()

            return self.metadata.update_prd(prd_id, title=title)
        except Exception as e:
            logger.error(f"동기화 실패: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """
        PRD 통계 조회

        Returns:
            통계 딕셔너리
        """
        return self.metadata.get_stats()
