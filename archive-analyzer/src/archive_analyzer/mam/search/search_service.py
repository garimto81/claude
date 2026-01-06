"""
Worker C: Search Service

검색 및 자동완성 구현

🔒 규칙:
- search_index 테이블만 수정 가능
- assets, tags 테이블은 SELECT만
- core/interfaces.py의 ISearchService 구현
"""

from archive_analyzer.core.interfaces import (
    Asset,
    ISearchService,
    SearchResult,
    Tag,
)


class SearchService(ISearchService):
    """검색 서비스"""

    def __init__(self, db_path: str, meilisearch_url: str | None = None):
        self.db_path = db_path
        self.meilisearch_url = meilisearch_url

    async def search(
        self,
        query: str,
        filters: dict | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> SearchResult:
        """통합 검색"""
        # TODO: 구현
        raise NotImplementedError

    async def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        """자동완성"""
        # TODO: 구현
        raise NotImplementedError

    async def index_asset(self, asset: Asset, tags: list[Tag]) -> bool:
        """자산 인덱싱"""
        # TODO: 구현
        raise NotImplementedError

    async def remove_from_index(self, asset_id: str) -> bool:
        """인덱스에서 제거"""
        # TODO: 구현
        raise NotImplementedError

    async def get_facets(self, query: str = "") -> dict[str, list[tuple[str, int]]]:
        """패싯 정보"""
        # TODO: 구현
        raise NotImplementedError
