"""
Worker E: EDL Export Service

EDL 내보내기 (Premiere, DaVinci)

🔒 규칙:
- 파일 생성만 (DB 수정 없음)
- core/interfaces.py의 IExportService 구현
"""

from archive_analyzer.core.interfaces import (
    Asset,
    Clip,
    IExportService,
)


class EdlExportService(IExportService):
    """EDL 내보내기 서비스"""

    async def export_edl(
        self, clips: list[Clip], title: str, format: str = "premiere"
    ) -> str:
        """EDL 내보내기"""
        # TODO: 구현
        raise NotImplementedError

    async def export_metadata(
        self, assets: list[Asset], format: str = "json"
    ) -> str:
        """메타데이터 내보내기"""
        # TODO: 구현
        raise NotImplementedError
