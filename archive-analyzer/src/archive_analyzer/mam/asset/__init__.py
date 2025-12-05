"""
Worker A: Asset Management

담당 파일:
- asset_service.py
- version_service.py

담당 테이블:
- assets (CRUD)
- asset_versions (CRUD)

API 엔드포인트:
- GET/POST /mam/assets
- GET/PUT/DELETE /mam/assets/{id}
- GET /mam/assets/{id}/versions
"""

from .asset_service import AssetService

__all__ = ["AssetService"]
