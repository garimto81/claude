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
from .notion_style import (
    NOTION_COLORS,
    NOTION_FONTS,
    NOTION_TYPOGRAPHY,
    SECTION_ICONS,
    CALLOUT_STYLES,
    NotionStyle,
    NotionStyleMixin,
    get_default_style,
    hex_to_rgb,
)
from .diagram_generator import DiagramGenerator, create_generator
from .image_inserter import ImageInserter, create_inserter

__version__ = "1.2.0"
__all__ = [
    # Models
    "TextSegment",
    "TableData",
    "TableCell",
    "ConversionResult",
    # Auth
    "get_credentials",
    # Converter
    "MarkdownToDocsConverter",
    "create_google_doc",
    "NativeTableRenderer",
    # Notion Style
    "NOTION_COLORS",
    "NOTION_FONTS",
    "NOTION_TYPOGRAPHY",
    "SECTION_ICONS",
    "CALLOUT_STYLES",
    "NotionStyle",
    "NotionStyleMixin",
    "get_default_style",
    "hex_to_rgb",
    # Diagram Generator
    "DiagramGenerator",
    "create_generator",
    # Image Inserter
    "ImageInserter",
    "create_inserter",
]
