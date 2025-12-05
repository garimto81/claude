"""
Worker C: Search System

담당 파일:
- search_service.py
- fuzzy.py
- choseong.py

담당 테이블:
- search_index (CRUD)

API 엔드포인트:
- GET /mam/search
- GET /mam/search/autocomplete
- GET /mam/search/facets
"""

from .search_service import SearchService

__all__ = ["SearchService"]
