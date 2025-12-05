"""
Worker B: Tag System

담당 파일:
- tag_service.py
- auto_tagger.py

담당 테이블:
- tags (CRUD)
- tag_aliases (CRUD)
- asset_tags (CRUD)

API 엔드포인트:
- GET/POST /mam/tags
- GET /mam/tags/autocomplete
- POST/DELETE /mam/assets/{id}/tags
"""

from .tag_service import TagService

__all__ = ["TagService"]
