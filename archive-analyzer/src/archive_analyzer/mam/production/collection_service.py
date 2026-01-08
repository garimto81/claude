"""
Worker E: Collection Service

컬렉션 관리

🔒 규칙:
- collections, collection_assets 테이블만 수정 가능
- assets 테이블은 SELECT만
- core/interfaces.py의 ICollectionService 구현
"""

from archive_analyzer.core.interfaces import (
    Asset,
    Collection,
    ICollectionService,
)


class CollectionService(ICollectionService):
    """컬렉션 서비스"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_collection(self, name: str, **kwargs) -> Collection:
        """컬렉션 생성"""
        # TODO: 구현
        raise NotImplementedError

    async def get_collection(self, collection_id: str) -> Collection | None:
        """컬렉션 조회"""
        # TODO: 구현
        raise NotImplementedError

    async def list_collections(self) -> list[Collection]:
        """컬렉션 목록"""
        # TODO: 구현
        raise NotImplementedError

    async def add_asset_to_collection(
        self, collection_id: str, asset_id: str
    ) -> bool:
        """컬렉션에 자산 추가"""
        # TODO: 구현
        raise NotImplementedError

    async def get_collection_assets(self, collection_id: str) -> list[Asset]:
        """컬렉션의 자산 목록"""
        # TODO: 구현
        raise NotImplementedError
