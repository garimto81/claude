"""
Worker B: Tag Service

태그 관리 및 자산 태깅 구현

🔒 규칙:
- tags, tag_aliases, asset_tags 테이블만 수정 가능
- assets 테이블은 SELECT만
- core/interfaces.py의 ITagService 구현
"""

from archive_analyzer.core.interfaces import (
    ITagService,
    Tag,
    TagCategory,
)


class TagService(ITagService):
    """태그 관리 서비스"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def get_tag(self, tag_id: str) -> Tag | None:
        """태그 조회"""
        # TODO: 구현
        raise NotImplementedError

    async def list_tags(self, category: TagCategory | None = None) -> list[Tag]:
        """태그 목록"""
        # TODO: 구현
        raise NotImplementedError

    async def create_tag(self, name: str, category: TagCategory, **kwargs) -> Tag:
        """태그 생성"""
        # TODO: 구현
        raise NotImplementedError

    async def search_tags(self, query: str, limit: int = 10) -> list[Tag]:
        """태그 검색"""
        # TODO: 구현
        raise NotImplementedError

    async def get_tags_for_asset(self, asset_id: str) -> list[Tag]:
        """자산의 태그 목록"""
        # TODO: 구현
        raise NotImplementedError

    async def add_tag_to_asset(
        self, asset_id: str, tag_id: str, source: str = "manual"
    ) -> bool:
        """자산에 태그 추가"""
        # TODO: 구현
        raise NotImplementedError

    async def remove_tag_from_asset(self, asset_id: str, tag_id: str) -> bool:
        """자산에서 태그 제거"""
        # TODO: 구현
        raise NotImplementedError

    async def auto_tag_asset(self, asset_id: str, nas_path: str) -> list[Tag]:
        """자동 태깅"""
        # TODO: 구현
        raise NotImplementedError
