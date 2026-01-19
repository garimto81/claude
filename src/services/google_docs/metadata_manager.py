"""
PRD Metadata Manager

.prd-registry.json 파일을 통한 PRD 메타데이터 관리.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .client import _get_project_root

logger = logging.getLogger(__name__)


@dataclass
class PRDMetadata:
    """PRD 메타데이터"""

    prd_id: str  # PRD-0001 형식
    google_doc_id: str
    google_doc_url: str
    title: str
    status: str = "Draft"  # Draft, In Progress, Review, Approved, Archived
    priority: str = "P1"  # P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
    created_at: str = ""
    updated_at: str = ""
    local_cache: str = ""  # PRD-0001.cache.md
    checklist_path: str = ""  # docs/checklists/PRD-0001.md
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        if not self.updated_at:
            self.updated_at = self.created_at
        if not self.local_cache:
            self.local_cache = f"{self.prd_id}.cache.md"
        if not self.checklist_path:
            self.checklist_path = f"docs/checklists/{self.prd_id}.md"

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)

    @classmethod
    def from_dict(cls, prd_id: str, data: Dict[str, Any]) -> "PRDMetadata":
        """딕셔너리에서 생성"""
        return cls(prd_id=prd_id, **data)


@dataclass
class PRDRegistry:
    """PRD 레지스트리"""

    version: str = "1.0.0"
    last_sync: str = ""
    next_prd_number: int = 1
    prds: Dict[str, PRDMetadata] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """JSON 직렬화용 딕셔너리"""
        return {
            "version": self.version,
            "last_sync": self.last_sync,
            "next_prd_number": self.next_prd_number,
            "prds": {prd_id: prd.to_dict() for prd_id, prd in self.prds.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PRDRegistry":
        """딕셔너리에서 생성"""
        prds = {}
        for prd_id, prd_data in data.get("prds", {}).items():
            # prd_id가 이미 prd_data에 있을 수 있음
            if "prd_id" in prd_data:
                del prd_data["prd_id"]
            prds[prd_id] = PRDMetadata.from_dict(prd_id, prd_data)

        return cls(
            version=data.get("version", "1.0.0"),
            last_sync=data.get("last_sync", ""),
            next_prd_number=data.get("next_prd_number", 1),
            prds=prds,
        )


class MetadataManager:
    """PRD 메타데이터 관리자"""

    # 기본 레지스트리 경로
    DEFAULT_REGISTRY_PATH = (
        _get_project_root() / "tasks" / "prds" / ".prd-registry.json"
    )

    def __init__(self, registry_path: Optional[Path] = None):
        """
        초기화

        Args:
            registry_path: 레지스트리 파일 경로
        """
        self.registry_path = registry_path or self.DEFAULT_REGISTRY_PATH
        self._registry: Optional[PRDRegistry] = None

    def _ensure_registry_dir(self) -> None:
        """레지스트리 디렉토리 존재 확인"""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def registry(self) -> PRDRegistry:
        """레지스트리 로드 (lazy loading)"""
        if self._registry is None:
            self._registry = self.load()
        return self._registry

    def load(self) -> PRDRegistry:
        """
        레지스트리 파일 로드

        Returns:
            PRDRegistry 인스턴스
        """
        if self.registry_path.exists():
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"레지스트리 로드됨: {self.registry_path}")
            return PRDRegistry.from_dict(data)
        else:
            logger.info("레지스트리 파일 없음, 새로 생성")
            return PRDRegistry()

    def save(self) -> None:
        """레지스트리 파일 저장"""
        self._ensure_registry_dir()

        # 마지막 동기화 시간 업데이트
        self.registry.last_sync = datetime.utcnow().isoformat() + "Z"

        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.registry.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(f"레지스트리 저장됨: {self.registry_path}")

    # ==================== PRD CRUD ====================

    def get_next_prd_number(self) -> int:
        """
        다음 PRD 번호 조회 (자동 증가)

        Returns:
            다음 PRD 번호
        """
        number = self.registry.next_prd_number
        return number

    def generate_prd_id(self) -> str:
        """
        새 PRD ID 생성

        Returns:
            PRD-NNNN 형식의 ID
        """
        number = self.get_next_prd_number()
        return f"PRD-{number:04d}"

    def add_prd(
        self,
        google_doc_id: str,
        title: str,
        status: str = "Draft",
        priority: str = "P1",
        tags: Optional[List[str]] = None,
    ) -> PRDMetadata:
        """
        새 PRD 추가

        Args:
            google_doc_id: Google Docs 문서 ID
            title: PRD 제목
            status: 상태
            priority: 우선순위
            tags: 태그 목록

        Returns:
            생성된 PRDMetadata
        """
        prd_id = self.generate_prd_id()
        google_doc_url = f"https://docs.google.com/document/d/{google_doc_id}/edit"

        metadata = PRDMetadata(
            prd_id=prd_id,
            google_doc_id=google_doc_id,
            google_doc_url=google_doc_url,
            title=title,
            status=status,
            priority=priority,
            tags=tags or [],
        )

        self.registry.prds[prd_id] = metadata
        self.registry.next_prd_number += 1
        self.save()

        logger.info(f"PRD 추가됨: {prd_id} - {title}")
        return metadata

    def add_prd_with_id(
        self,
        prd_id: str,
        google_doc_id: str,
        title: str,
        status: str = "Draft",
        priority: str = "P1",
        tags: Optional[List[str]] = None,
    ) -> PRDMetadata:
        """
        지정된 ID로 PRD 추가 (마이그레이션용)

        Args:
            prd_id: PRD ID (예: PRD-0001)
            google_doc_id: Google Docs 문서 ID
            title: PRD 제목
            status: 상태
            priority: 우선순위
            tags: 태그 목록

        Returns:
            생성된 PRDMetadata
        """
        google_doc_url = f"https://docs.google.com/document/d/{google_doc_id}/edit"

        metadata = PRDMetadata(
            prd_id=prd_id,
            google_doc_id=google_doc_id,
            google_doc_url=google_doc_url,
            title=title,
            status=status,
            priority=priority,
            tags=tags or [],
        )

        self.registry.prds[prd_id] = metadata

        # next_prd_number 업데이트 (더 큰 번호가 있으면)
        try:
            prd_num = int(prd_id.split("-")[1])
            if prd_num >= self.registry.next_prd_number:
                self.registry.next_prd_number = prd_num + 1
        except (ValueError, IndexError):
            pass

        self.save()
        logger.info(f"PRD 추가됨 (지정 ID): {prd_id} - {title}")
        return metadata

    def get_prd(self, prd_id: str) -> Optional[PRDMetadata]:
        """
        PRD 조회

        Args:
            prd_id: PRD ID

        Returns:
            PRDMetadata 또는 None
        """
        return self.registry.prds.get(prd_id)

    def update_prd(
        self,
        prd_id: str,
        **kwargs,
    ) -> Optional[PRDMetadata]:
        """
        PRD 업데이트

        Args:
            prd_id: PRD ID
            **kwargs: 업데이트할 필드

        Returns:
            업데이트된 PRDMetadata 또는 None
        """
        prd = self.get_prd(prd_id)
        if not prd:
            logger.warning(f"PRD를 찾을 수 없음: {prd_id}")
            return None

        for key, value in kwargs.items():
            if hasattr(prd, key):
                setattr(prd, key, value)

        prd.updated_at = datetime.utcnow().isoformat() + "Z"
        self.save()

        logger.info(f"PRD 업데이트됨: {prd_id}")
        return prd

    def delete_prd(self, prd_id: str) -> bool:
        """
        PRD 삭제

        Args:
            prd_id: PRD ID

        Returns:
            삭제 성공 여부
        """
        if prd_id in self.registry.prds:
            del self.registry.prds[prd_id]
            self.save()
            logger.info(f"PRD 삭제됨: {prd_id}")
            return True

        logger.warning(f"PRD를 찾을 수 없음: {prd_id}")
        return False

    # ==================== Query Methods ====================

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
        prds = list(self.registry.prds.values())

        if status:
            prds = [p for p in prds if p.status == status]

        if priority:
            prds = [p for p in prds if p.priority == priority]

        # 최신순 정렬
        prds.sort(key=lambda p: p.updated_at, reverse=True)

        return prds

    def find_by_google_doc_id(self, google_doc_id: str) -> Optional[PRDMetadata]:
        """
        Google Doc ID로 PRD 조회

        Args:
            google_doc_id: Google Docs 문서 ID

        Returns:
            PRDMetadata 또는 None
        """
        for prd in self.registry.prds.values():
            if prd.google_doc_id == google_doc_id:
                return prd
        return None

    def find_by_title(self, title: str) -> List[PRDMetadata]:
        """
        제목으로 PRD 검색

        Args:
            title: 검색할 제목 (부분 일치)

        Returns:
            일치하는 PRDMetadata 리스트
        """
        title_lower = title.lower()
        return [
            prd
            for prd in self.registry.prds.values()
            if title_lower in prd.title.lower()
        ]

    # ==================== Statistics ====================

    def get_stats(self) -> Dict[str, Any]:
        """
        PRD 통계 조회

        Returns:
            통계 딕셔너리
        """
        prds = list(self.registry.prds.values())

        status_counts = {}
        priority_counts = {}

        for prd in prds:
            status_counts[prd.status] = status_counts.get(prd.status, 0) + 1
            priority_counts[prd.priority] = priority_counts.get(prd.priority, 0) + 1

        return {
            "total": len(prds),
            "by_status": status_counts,
            "by_priority": priority_counts,
            "next_number": self.registry.next_prd_number,
            "last_sync": self.registry.last_sync,
        }
