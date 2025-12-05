"""
Worker F: Dashboard Service

대시보드 통계

🔒 규칙:
- 모든 테이블 SELECT 가능 (통계용)
- audit_logs 테이블만 INSERT 가능
- core/interfaces.py의 IDashboardService 구현
"""

from archive_analyzer.core.interfaces import IDashboardService


class DashboardService(IDashboardService):
    """대시보드 서비스"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def get_stats(self) -> dict:
        """전체 통계"""
        # TODO: 구현
        raise NotImplementedError

    async def get_storage_analysis(self) -> dict:
        """스토리지 분석"""
        # TODO: 구현
        raise NotImplementedError

    async def get_recent_activity(self, limit: int = 20) -> list[dict]:
        """최근 활동"""
        # TODO: 구현
        raise NotImplementedError
