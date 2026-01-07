"""
PRD Service

Google Docs 기반 PRD 생성 및 관리 서비스.

Features:
- 기본 PRD 생성 (텍스트 기반)
- 시각화 PRD 생성 (HTML 목업 → 스크린샷 → Google Docs 삽입)
- Notion 스타일 적용
- 이미지 자동 삽입
"""

import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .client import GoogleDocsClient
from .metadata_manager import MetadataManager, PRDMetadata

# lib/google_docs 모듈 import (시각화용)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lib"))
try:
    from google_docs import (
        MarkdownToDocsConverter,
        ImageInserter,
        NotionStyle,
        get_default_style,
    )
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PRDSection:
    """PRD 섹션 정의"""

    title: str
    content: str = ""
    heading_level: int = 2


@dataclass
class VisualizationConfig:
    """시각화 설정"""

    enabled: bool = False
    mockup_dir: Path = None  # HTML 목업 디렉토리
    image_dir: Path = None   # 스크린샷 저장 디렉토리
    drive_folder_id: str = ""  # Google Drive 이미지 폴더 ID
    image_width: int = 450   # 이미지 너비 (PT)
    apply_notion_style: bool = True  # Notion 스타일 적용 여부

    def __post_init__(self):
        if self.mockup_dir is None:
            self.mockup_dir = Path("docs/mockups")
        if self.image_dir is None:
            self.image_dir = Path("docs/images")


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

    # 시각화 설정
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

    # 시각화 이미지 매핑 (섹션명 → 이미지 경로)
    section_images: Dict[str, Path] = field(default_factory=dict)

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
                title = title[len(f"{prd_id}:") :].strip()

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

    # ==================== Visualization (--gdocs) ====================

    def create_prd_with_visualization(
        self,
        title: str,
        template: Optional[PRDTemplate] = None,
        images: Optional[Dict[str, Path]] = None,
        priority: str = "P1",
        tags: Optional[List[str]] = None,
        apply_notion_style: bool = True,
        image_width: int = 450,
    ) -> PRDMetadata:
        """
        시각화 포함 PRD 생성 (--gdocs 옵션)

        HTML 목업 → 스크린샷 → Google Drive 업로드 → Google Docs 삽입

        Args:
            title: PRD 제목
            template: PRD 템플릿
            images: 섹션별 이미지 매핑 {"Technical Design": Path("flow.png")}
            priority: 우선순위
            tags: 태그 목록
            apply_notion_style: Notion 스타일 적용 여부
            image_width: 이미지 너비 (PT)

        Returns:
            생성된 PRDMetadata

        Raises:
            ImportError: lib/google_docs 모듈이 없을 경우
        """
        if not VISUALIZATION_AVAILABLE:
            raise ImportError(
                "시각화 기능을 사용하려면 lib/google_docs 모듈이 필요합니다.\n"
                "lib/google_docs/ 디렉토리가 존재하는지 확인하세요."
            )

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
        doc_id = doc_info["documentId"]

        logger.info(f"[1/4] 문서 생성됨: {doc_title}")

        # Markdown → Google Docs 네이티브 변환
        markdown_content = template.to_document_content()
        converter = MarkdownToDocsConverter(
            markdown_content,
            use_native_tables=True,
        )
        requests = converter.parse()

        if requests:
            self.client.update_document(doc_id, requests)
            logger.info(f"[2/4] 콘텐츠 변환 완료: {len(requests)} 요청")

        # 이미지 삽입
        if images:
            self._insert_images_to_doc(doc_id, images, image_width)
            logger.info(f"[3/4] 이미지 삽입 완료: {len(images)}개")
        else:
            logger.info("[3/4] 이미지 없음 (스킵)")

        # Notion 스타일 적용
        if apply_notion_style:
            self._apply_notion_style(doc_id)
            logger.info("[4/4] Notion 스타일 적용 완료")
        else:
            logger.info("[4/4] 스타일 적용 스킵")

        # 메타데이터 저장
        metadata = self.metadata.add_prd(
            google_doc_id=doc_id,
            title=title,
            status="Draft",
            priority=priority,
            tags=tags,
        )

        logger.info(f"✅ PRD 생성 완료: {prd_id}")
        logger.info(f"   URL: {doc_info['url']}")

        return metadata

    def _insert_images_to_doc(
        self,
        doc_id: str,
        images: Dict[str, Path],
        width: int = 450,
    ) -> int:
        """
        Google Docs에 이미지 삽입

        Args:
            doc_id: 문서 ID
            images: 섹션명 → 이미지 경로 매핑
            width: 이미지 너비 (PT)

        Returns:
            삽입된 이미지 수
        """
        if not VISUALIZATION_AVAILABLE:
            logger.warning("시각화 모듈 없음 - 이미지 삽입 스킵")
            return 0

        # credentials 가져오기
        credentials = self.client._load_credentials()
        inserter = ImageInserter(credentials)

        inserted_count = 0

        for section_name, image_path in images.items():
            image_path = Path(image_path)

            if not image_path.exists():
                logger.warning(f"이미지 파일 없음: {image_path}")
                continue

            try:
                # 1. Google Drive에 업로드
                file_id, image_url = inserter.upload_to_drive(
                    image_path,
                    folder_id=self.client.folder_id,
                    make_public=True,
                )
                logger.info(f"   Drive 업로드: {image_path.name}")

                # 2. 섹션 제목 뒤에 이미지 삽입
                success = inserter.insert_image_after_heading(
                    doc_id,
                    image_url,
                    section_name,
                    width=width,
                )

                if success:
                    inserted_count += 1
                    logger.info(f"   '{section_name}' 섹션에 이미지 삽입")
                else:
                    logger.warning(f"   이미지 삽입 실패: {section_name}")

            except Exception as e:
                logger.error(f"이미지 처리 실패 ({image_path}): {e}")

        return inserted_count

    def _apply_notion_style(self, doc_id: str) -> bool:
        """
        Notion 스타일 적용

        Args:
            doc_id: 문서 ID

        Returns:
            성공 여부
        """
        if not VISUALIZATION_AVAILABLE:
            return False

        try:
            style = get_default_style()

            # 문서 조회
            doc = self.client.get_document(doc_id)
            body_content = doc.get("body", {}).get("content", [])

            requests = []

            for element in body_content:
                if "paragraph" not in element:
                    continue

                para = element["paragraph"]
                para_style = para.get("paragraphStyle", {})
                named_style = para_style.get("namedStyleType", "")

                # 제목 스타일 처리
                if "HEADING" in named_style:
                    level = int(named_style.replace("HEADING_", ""))
                    heading_style = style.typography.get(level, {})

                    start_idx = element.get("startIndex", 0)
                    end_idx = element.get("endIndex", 0)

                    if heading_style:
                        color = style.get_color(heading_style.get("color", "text_primary"))

                        requests.append({
                            "updateTextStyle": {
                                "range": {
                                    "startIndex": start_idx,
                                    "endIndex": end_idx - 1,
                                },
                                "textStyle": {
                                    "foregroundColor": {
                                        "color": {"rgbColor": color}
                                    },
                                    "fontSize": {
                                        "magnitude": heading_style.get("size", 14),
                                        "unit": "PT"
                                    },
                                },
                                "fields": "foregroundColor,fontSize"
                            }
                        })

            if requests:
                self.client.update_document(doc_id, requests)
                logger.info(f"Notion 스타일 적용: {len(requests)} 요청")

            return True

        except Exception as e:
            logger.error(f"스타일 적용 실패: {e}")
            return False

    def insert_visualization(
        self,
        prd_id: str,
        section_name: str,
        image_path: Path,
        width: int = 450,
    ) -> bool:
        """
        기존 PRD에 시각화 이미지 추가

        Args:
            prd_id: PRD ID
            section_name: 삽입할 섹션 제목
            image_path: 이미지 파일 경로
            width: 이미지 너비 (PT)

        Returns:
            성공 여부
        """
        prd = self.get_prd(prd_id)
        if not prd:
            logger.warning(f"PRD를 찾을 수 없음: {prd_id}")
            return False

        result = self._insert_images_to_doc(
            prd.google_doc_id,
            {section_name: image_path},
            width=width,
        )

        return result > 0
