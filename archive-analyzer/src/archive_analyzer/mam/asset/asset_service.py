"""
Worker A: Asset Service

자산 CRUD 및 버전 관리 구현

🔒 규칙:
- assets, asset_versions 테이블만 수정 가능
- 다른 테이블은 SELECT만
- core/interfaces.py의 IAssetService 구현
"""

from archive_analyzer.core.interfaces import (
    Asset,
    AssetStatus,
    AssetVersion,
    FileType,
    IAssetService,
)


class AssetService(IAssetService):
    """자산 관리 서비스"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def get_asset(self, asset_id: str) -> Asset | None:
        """자산 조회"""
        # TODO: 구현
        raise NotImplementedError

    async def list_assets(
        self,
        limit: int = 50,
        offset: int = 0,
        status: AssetStatus | None = None,
        file_type: FileType | None = None,
    ) -> tuple[list[Asset], int]:
        """자산 목록"""
        # TODO: 구현
        raise NotImplementedError

    async def create_asset(self, nas_path: str, **kwargs) -> Asset:
        """자산 생성"""
        # TODO: 구현
        raise NotImplementedError

    async def update_asset(self, asset_id: str, **kwargs) -> Asset | None:
        """자산 수정"""
        # TODO: 구현
        raise NotImplementedError

    async def delete_asset(self, asset_id: str) -> bool:
        """자산 삭제 (soft delete)"""
        # TODO: 구현
        raise NotImplementedError

    async def get_versions(self, asset_id: str) -> list[AssetVersion]:
        """자산 버전 목록"""
        # TODO: 구현
        raise NotImplementedError

    async def create_version(
        self, asset_id: str, version_type: str, path: str, **kwargs
    ) -> AssetVersion:
        """버전 생성"""
        # TODO: 구현
        raise NotImplementedError
