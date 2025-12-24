"""
Google Docs PRD Converter - 공통 모듈

PRD 마크다운 파일을 Google Docs 네이티브 형식으로 변환합니다.

Usage:
    from lib.google_docs import MarkdownToDocsConverter, create_google_doc

    # 변환
    converter = MarkdownToDocsConverter(markdown_content)
    requests = converter.parse()

    # 문서 생성
    doc_url = create_google_doc(title, markdown_content)
"""

from .models import TextSegment, TableData, TableCell, ConversionResult
from .auth import get_credentials
from .converter import MarkdownToDocsConverter, create_google_doc
from .table_renderer import NativeTableRenderer

__version__ = "1.0.0"
__all__ = [
    "TextSegment",
    "TableData",
    "TableCell",
    "ConversionResult",
    "get_credentials",
    "MarkdownToDocsConverter",
    "create_google_doc",
    "NativeTableRenderer",
]
