"""
Google Docs Service Package

PRD 관리를 위한 Google Docs API 통합 서비스.
"""

from .client import GoogleDocsClient
from .metadata_manager import MetadataManager, PRDMetadata
from .prd_service import PRDService
from .cache_manager import CacheManager

__all__ = [
    "GoogleDocsClient",
    "MetadataManager",
    "PRDMetadata",
    "PRDService",
    "CacheManager",
]

__version__ = "1.0.0"
