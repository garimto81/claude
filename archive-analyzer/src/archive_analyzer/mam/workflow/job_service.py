"""
Worker D: Job Service

작업 큐 관리

🔒 규칙:
- jobs 테이블만 수정 가능
- core/interfaces.py의 IJobService 구현
"""

from archive_analyzer.core.interfaces import (
    IJobService,
    Job,
    JobStatus,
    JobType,
)


class JobService(IJobService):
    """작업 큐 서비스"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_job(self, job_type: JobType, input_data: dict) -> Job:
        """작업 생성"""
        # TODO: 구현
        raise NotImplementedError

    async def get_job(self, job_id: str) -> Job | None:
        """작업 조회"""
        # TODO: 구현
        raise NotImplementedError

    async def list_jobs(
        self, status: JobStatus | None = None, limit: int = 50
    ) -> list[Job]:
        """작업 목록"""
        # TODO: 구현
        raise NotImplementedError

    async def update_job_status(
        self, job_id: str, status: JobStatus, **kwargs
    ) -> bool:
        """작업 상태 업데이트"""
        # TODO: 구현
        raise NotImplementedError

    async def cancel_job(self, job_id: str) -> bool:
        """작업 취소"""
        # TODO: 구현
        raise NotImplementedError
