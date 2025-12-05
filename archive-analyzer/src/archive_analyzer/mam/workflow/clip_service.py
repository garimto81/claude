"""
Worker D: Clip Service

클리핑 구현 (FFmpeg)

🔒 규칙:
- clips, jobs 테이블만 수정 가능
- assets 테이블은 SELECT만 (IAssetService 통해 접근)
- core/interfaces.py의 IClipService 구현
"""

from archive_analyzer.core.interfaces import (
    Clip,
    IAssetService,
    IClipService,
)


class ClipService(IClipService):
    """클리핑 서비스"""

    def __init__(self, db_path: str, asset_service: IAssetService):
        self.db_path = db_path
        self._asset_service = asset_service  # 인터페이스 통해 접근

    async def create_clip(
        self,
        asset_id: str,
        start_time: float,
        end_time: float,
        output_format: str = "mp4",
    ) -> Clip:
        """클립 생성"""
        # IAssetService 통해 자산 조회 (직접 import 금지)
        asset = await self._asset_service.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")

        # TODO: FFmpeg 클리핑 구현
        raise NotImplementedError

    async def get_clip(self, clip_id: str) -> Clip | None:
        """클립 조회"""
        # TODO: 구현
        raise NotImplementedError

    async def list_clips(
        self, asset_id: str | None = None, limit: int = 50
    ) -> list[Clip]:
        """클립 목록"""
        # TODO: 구현
        raise NotImplementedError

    async def delete_clip(self, clip_id: str) -> bool:
        """클립 삭제"""
        # TODO: 구현
        raise NotImplementedError
