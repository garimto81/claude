"""
Worker D: Workflow

담당 파일:
- clip_service.py
- job_service.py
- transcode_service.py

담당 테이블:
- clips (CRUD)
- jobs (CRUD)

API 엔드포인트:
- POST/GET /mam/clips
- GET/DELETE /mam/clips/{id}
- GET /mam/jobs
- POST /mam/jobs/{id}/cancel
"""

from .clip_service import ClipService
from .job_service import JobService

__all__ = ["ClipService", "JobService"]
