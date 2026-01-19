"""
Core Interfaces for Archive MAM

이 파일은 모든 Worker가 공유하는 인터페이스 계약을 정의합니다.

🔒 주의사항:
- 이 파일 변경 시 모든 Worker와 합의 필요
- GitHub Issue 생성 후 논의
- 변경 후 모든 Worker에게 알림

Worker 할당:
- Worker A: Asset Management (IAssetService)
- Worker B: Tag System (ITagService)
- Worker C: Search (ISearchService)
- Worker D: Workflow (IClipService, IJobService)
- Worker E: Production (ICollectionService, IExportService)
- Worker F: Admin (IUserService, IDashboardService)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

# ============================================
# Enums
# ============================================


class AssetStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class FileType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    OTHER = "other"


class ClipStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    SCAN = "scan"
    CLIP = "clip"
    TRANSCODE = "transcode"
    EXPORT = "export"


class TagCategory(str, Enum):
    TOURNAMENT = "tournament"
    EVENT = "event"
    TEMPORAL = "temporal"
    PLAYER = "player"
    HAND = "hand"
    ACTION = "action"
    EMOTION = "emotion"
    TECHNICAL = "technical"


# ============================================
# Data Models (공유)
# ============================================


@dataclass
class Asset:
    """자산 기본 정보 - 모든 모듈에서 참조"""

    id: str
    nas_path: str
    filename: str
    file_type: FileType
    size_bytes: int
    status: AssetStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    # 기술 메타데이터 (선택)
    video_codec: Optional[str] = None
    audio_codec: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[float] = None
    bitrate: Optional[int] = None
    framerate: Optional[float] = None
    container: Optional[str] = None


@dataclass
class AssetVersion:
    """자산 버전"""

    id: str
    asset_id: str
    version_type: str  # original, proxy, clip, edited
    path: str
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None


@dataclass
class Tag:
    """태그 정보"""

    id: str
    name: str
    category: TagCategory
    canonical_name: Optional[str] = None
    parent_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class TagAlias:
    """태그 별명"""

    id: int
    tag_id: str
    alias: str


@dataclass
class AssetTag:
    """자산-태그 연결"""

    asset_id: str
    tag_id: str
    confidence: float = 1.0  # 자동 태깅 신뢰도
    source: str = "manual"  # manual, auto, ai


@dataclass
class Clip:
    """클립 정보"""

    id: str
    source_asset_id: str
    start_time: float
    end_time: float
    output_path: Optional[str] = None
    output_format: Optional[str] = None
    size_bytes: Optional[int] = None
    status: ClipStatus = ClipStatus.PENDING
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Job:
    """작업 정보"""

    id: str
    job_type: JobType
    status: JobStatus = JobStatus.QUEUED
    input_data: Optional[str] = None  # JSON
    output_data: Optional[str] = None  # JSON
    progress: float = 0.0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Collection:
    """컬렉션"""

    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class SearchResult:
    """검색 결과"""

    total: int
    assets: list[Asset]
    facets: dict[str, list[tuple[str, int]]] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class User:
    """사용자"""

    id: str
    email: str
    name: Optional[str] = None
    role: str = "editor"  # admin, editor, viewer
    created_at: Optional[datetime] = None


# ============================================
# Service Interfaces (계약)
# ============================================


class IAssetService(ABC):
    """
    Worker A 담당: Asset Management

    자산의 CRUD 및 버전 관리
    """

    @abstractmethod
    async def get_asset(self, asset_id: str) -> Asset | None:
        """자산 조회"""
        ...

    @abstractmethod
    async def list_assets(
        self,
        limit: int = 50,
        offset: int = 0,
        status: AssetStatus | None = None,
        file_type: FileType | None = None,
    ) -> tuple[list[Asset], int]:
        """자산 목록 (assets, total)"""
        ...

    @abstractmethod
    async def create_asset(self, nas_path: str, **kwargs) -> Asset:
        """자산 생성"""
        ...

    @abstractmethod
    async def update_asset(self, asset_id: str, **kwargs) -> Asset | None:
        """자산 수정"""
        ...

    @abstractmethod
    async def delete_asset(self, asset_id: str) -> bool:
        """자산 삭제 (soft delete)"""
        ...

    @abstractmethod
    async def get_versions(self, asset_id: str) -> list[AssetVersion]:
        """자산 버전 목록"""
        ...

    @abstractmethod
    async def create_version(
        self, asset_id: str, version_type: str, path: str, **kwargs
    ) -> AssetVersion:
        """버전 생성"""
        ...


class ITagService(ABC):
    """
    Worker B 담당: Tag System

    태그 관리 및 자산 태깅
    """

    @abstractmethod
    async def get_tag(self, tag_id: str) -> Tag | None:
        """태그 조회"""
        ...

    @abstractmethod
    async def list_tags(self, category: TagCategory | None = None) -> list[Tag]:
        """태그 목록"""
        ...

    @abstractmethod
    async def create_tag(self, name: str, category: TagCategory, **kwargs) -> Tag:
        """태그 생성"""
        ...

    @abstractmethod
    async def search_tags(self, query: str, limit: int = 10) -> list[Tag]:
        """태그 검색 (자동완성용)"""
        ...

    @abstractmethod
    async def get_tags_for_asset(self, asset_id: str) -> list[Tag]:
        """자산의 태그 목록"""
        ...

    @abstractmethod
    async def add_tag_to_asset(
        self, asset_id: str, tag_id: str, source: str = "manual"
    ) -> bool:
        """자산에 태그 추가"""
        ...

    @abstractmethod
    async def remove_tag_from_asset(self, asset_id: str, tag_id: str) -> bool:
        """자산에서 태그 제거"""
        ...

    @abstractmethod
    async def auto_tag_asset(self, asset_id: str, nas_path: str) -> list[Tag]:
        """자동 태깅 (파일명/경로 기반)"""
        ...


class ISearchService(ABC):
    """
    Worker C 담당: Search System

    검색 및 자동완성
    """

    @abstractmethod
    async def search(
        self,
        query: str,
        filters: dict | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> SearchResult:
        """통합 검색"""
        ...

    @abstractmethod
    async def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        """자동완성"""
        ...

    @abstractmethod
    async def index_asset(self, asset: Asset, tags: list[Tag]) -> bool:
        """자산 인덱싱"""
        ...

    @abstractmethod
    async def remove_from_index(self, asset_id: str) -> bool:
        """인덱스에서 제거"""
        ...

    @abstractmethod
    async def get_facets(self, query: str = "") -> dict[str, list[tuple[str, int]]]:
        """패싯 정보"""
        ...


class IClipService(ABC):
    """
    Worker D 담당: Workflow - Clipping

    클리핑 및 트랜스코딩
    """

    @abstractmethod
    async def create_clip(
        self,
        asset_id: str,
        start_time: float,
        end_time: float,
        output_format: str = "mp4",
    ) -> Clip:
        """클립 생성 요청"""
        ...

    @abstractmethod
    async def get_clip(self, clip_id: str) -> Clip | None:
        """클립 상태 조회"""
        ...

    @abstractmethod
    async def list_clips(
        self, asset_id: str | None = None, limit: int = 50
    ) -> list[Clip]:
        """클립 목록"""
        ...

    @abstractmethod
    async def delete_clip(self, clip_id: str) -> bool:
        """클립 삭제"""
        ...


class IJobService(ABC):
    """
    Worker D 담당: Workflow - Job Queue

    비동기 작업 관리
    """

    @abstractmethod
    async def create_job(self, job_type: JobType, input_data: dict) -> Job:
        """작업 생성"""
        ...

    @abstractmethod
    async def get_job(self, job_id: str) -> Job | None:
        """작업 조회"""
        ...

    @abstractmethod
    async def list_jobs(
        self, status: JobStatus | None = None, limit: int = 50
    ) -> list[Job]:
        """작업 목록"""
        ...

    @abstractmethod
    async def update_job_status(self, job_id: str, status: JobStatus, **kwargs) -> bool:
        """작업 상태 업데이트"""
        ...

    @abstractmethod
    async def cancel_job(self, job_id: str) -> bool:
        """작업 취소"""
        ...


class ICollectionService(ABC):
    """
    Worker E 담당: Production - Collections

    컬렉션 관리
    """

    @abstractmethod
    async def create_collection(self, name: str, **kwargs) -> Collection:
        """컬렉션 생성"""
        ...

    @abstractmethod
    async def get_collection(self, collection_id: str) -> Collection | None:
        """컬렉션 조회"""
        ...

    @abstractmethod
    async def list_collections(self) -> list[Collection]:
        """컬렉션 목록"""
        ...

    @abstractmethod
    async def add_asset_to_collection(self, collection_id: str, asset_id: str) -> bool:
        """컬렉션에 자산 추가"""
        ...

    @abstractmethod
    async def get_collection_assets(self, collection_id: str) -> list[Asset]:
        """컬렉션의 자산 목록"""
        ...


class IExportService(ABC):
    """
    Worker E 담당: Production - Export

    EDL 등 내보내기
    """

    @abstractmethod
    async def export_edl(
        self, clips: list[Clip], title: str, format: str = "premiere"
    ) -> str:
        """EDL 내보내기"""
        ...

    @abstractmethod
    async def export_metadata(self, assets: list[Asset], format: str = "json") -> str:
        """메타데이터 내보내기"""
        ...


class IUserService(ABC):
    """
    Worker F 담당: Admin - User Management

    사용자 관리
    """

    @abstractmethod
    async def get_user(self, user_id: str) -> User | None:
        """사용자 조회"""
        ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """이메일로 사용자 조회"""
        ...

    @abstractmethod
    async def create_user(self, email: str, **kwargs) -> User:
        """사용자 생성"""
        ...

    @abstractmethod
    async def update_user_role(self, user_id: str, role: str) -> bool:
        """역할 변경"""
        ...

    @abstractmethod
    async def list_users(self) -> list[User]:
        """사용자 목록"""
        ...


class IDashboardService(ABC):
    """
    Worker F 담당: Admin - Dashboard

    대시보드 통계
    """

    @abstractmethod
    async def get_stats(self) -> dict:
        """전체 통계"""
        ...

    @abstractmethod
    async def get_storage_analysis(self) -> dict:
        """스토리지 분석"""
        ...

    @abstractmethod
    async def get_recent_activity(self, limit: int = 20) -> list[dict]:
        """최근 활동"""
        ...
