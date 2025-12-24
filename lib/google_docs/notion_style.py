"""
Notion 스타일 시스템

Google Docs PRD 변환에 사용되는 Notion 스타일 색상, 타이포그래피, 컴포넌트 스타일을 정의합니다.

Features:
- 부드러운 파스텔 색상 팔레트
- 넉넉한 여백과 줄간격
- 섹션별 아이콘
- Callout 박스 스타일
"""

from dataclasses import dataclass
from typing import Any


# ============================================================================
# Notion 색상 팔레트 (RGB 0-1 범위)
# ============================================================================

def hex_to_rgb(hex_color: str) -> dict[str, float]:
    """HEX 색상을 Google Docs RGB 형식으로 변환"""
    hex_color = hex_color.lstrip('#')
    return {
        'red': int(hex_color[0:2], 16) / 255,
        'green': int(hex_color[2:4], 16) / 255,
        'blue': int(hex_color[4:6], 16) / 255,
    }


NOTION_COLORS = {
    # 텍스트 색상
    'text_primary': hex_to_rgb('#1a1a1a'),      # 거의 검정
    'text_secondary': hex_to_rgb('#555555'),    # 중간 회색
    'text_muted': hex_to_rgb('#888888'),        # 연한 회색

    # 제목 색상 (강조)
    'heading_primary': hex_to_rgb('#0969DA'),   # GitHub Blue - H1용
    'heading_secondary': hex_to_rgb('#1F2328'), # 진한 검정 - H2용
    'heading_accent': hex_to_rgb('#0550AE'),    # 진한 파랑 - 링크/강조

    # 배경 색상
    'background': hex_to_rgb('#FFFFFF'),         # 흰색
    'background_gray': hex_to_rgb('#F6F8FA'),    # GitHub 스타일 배경
    'background_warm': hex_to_rgb('#FFFBEB'),    # 따뜻한 노랑 배경

    # 선명한 액센트 색상
    'red': hex_to_rgb('#CF222E'),               # 진한 빨강
    'orange': hex_to_rgb('#BF8700'),            # 진한 주황
    'yellow': hex_to_rgb('#9A6700'),            # 진한 노랑
    'green': hex_to_rgb('#1A7F37'),             # 진한 초록
    'blue': hex_to_rgb('#0969DA'),              # 진한 파랑
    'purple': hex_to_rgb('#8250DF'),            # 진한 보라
    'pink': hex_to_rgb('#BF3989'),              # 진한 핑크

    # 하이라이트 배경 (연한 버전)
    'highlight_red': hex_to_rgb('#FFEBE9'),
    'highlight_orange': hex_to_rgb('#FFF8C5'),
    'highlight_yellow': hex_to_rgb('#FFF8C5'),
    'highlight_green': hex_to_rgb('#DAFBE1'),
    'highlight_blue': hex_to_rgb('#DDF4FF'),
    'highlight_purple': hex_to_rgb('#FBEFFF'),
    'highlight_gray': hex_to_rgb('#F6F8FA'),

    # 코드 블록 (더 명확한 배경)
    'code_bg': hex_to_rgb('#F6F8FA'),           # GitHub 코드 배경
    'code_text': hex_to_rgb('#CF222E'),         # 빨간 코드 텍스트
    'code_border': hex_to_rgb('#D0D7DE'),       # 코드 테두리

    # 테두리 및 구분선
    'border': hex_to_rgb('#D0D7DE'),
    'divider': hex_to_rgb('#D8DEE4'),

    # 테이블 (더 눈에 띄는 헤더)
    'table_header_bg': hex_to_rgb('#F6F8FA'),   # 헤더 배경
    'table_header_text': hex_to_rgb('#1F2328'), # 헤더 텍스트
    'table_border': hex_to_rgb('#D0D7DE'),
    'table_row_alt': hex_to_rgb('#F6F8FA'),
}


# ============================================================================
# 폰트 설정
# ============================================================================

NOTION_FONTS = {
    'heading': 'Georgia',           # 세리프 (Notion 기본)
    'body': 'Arial',                # 산세리프 (가독성)
    'code': 'Consolas',             # 고정폭
    'ui': 'Segoe UI',               # UI 요소
}


# ============================================================================
# 타이포그래피 시스템
# ============================================================================

NOTION_TYPOGRAPHY: dict[int | str, dict[str, Any]] = {
    # Heading 스타일 (넉넉한 여백)
    1: {
        'size': 32,
        'weight': 700,
        'line_height': 1.3,
        'space_before': 48,
        'space_after': 16,
        'font': 'heading',
        'color': 'text_primary',
    },
    2: {
        'size': 24,
        'weight': 600,
        'line_height': 1.4,
        'space_before': 36,
        'space_after': 12,
        'font': 'heading',
        'color': 'text_primary',
    },
    3: {
        'size': 18,
        'weight': 600,
        'line_height': 1.4,
        'space_before': 28,
        'space_after': 8,
        'font': 'heading',
        'color': 'text_primary',
    },
    4: {
        'size': 16,
        'weight': 600,
        'line_height': 1.5,
        'space_before': 20,
        'space_after': 6,
        'font': 'heading',
        'color': 'text_secondary',
    },
    5: {
        'size': 14,
        'weight': 600,
        'line_height': 1.5,
        'space_before': 16,
        'space_after': 4,
        'font': 'heading',
        'color': 'text_secondary',
    },
    6: {
        'size': 13,
        'weight': 600,
        'line_height': 1.5,
        'space_before': 12,
        'space_after': 4,
        'font': 'heading',
        'color': 'text_muted',
    },

    # Body 스타일
    'body': {
        'size': 14,
        'weight': 400,
        'line_height': 1.7,      # Notion의 넉넉한 줄간격
        'space_after': 8,
        'font': 'body',
        'color': 'text_primary',
    },

    # 코드 스타일
    'code_inline': {
        'size': 13,
        'weight': 400,
        'font': 'code',
        'color': 'code_text',
        'background': 'code_bg',
    },
    'code_block': {
        'size': 13,
        'weight': 400,
        'line_height': 1.5,
        'font': 'code',
        'color': 'text_primary',
        'background': 'code_bg',
        'padding': 16,
    },

    # 리스트 스타일
    'list': {
        'size': 14,
        'weight': 400,
        'line_height': 1.6,
        'indent': 24,
        'item_spacing': 4,
        'font': 'body',
        'color': 'text_primary',
    },

    # 인용문 스타일
    'quote': {
        'size': 14,
        'weight': 400,
        'line_height': 1.6,
        'font': 'body',
        'color': 'text_secondary',
        'border_color': 'text_muted',
        'border_width': 3,
        'padding': 16,
    },
}


# ============================================================================
# 섹션 아이콘 매핑
# ============================================================================

SECTION_ICONS: dict[str, str] = {
    # 일반 섹션
    'overview': '📋',
    'introduction': '📝',
    'background': '📚',
    'goals': '🎯',
    'objectives': '🎯',

    # 기술 섹션
    'architecture': '🏗️',
    'technical': '⚙️',
    'implementation': '💻',
    'api': '🔌',
    'data': '💾',
    'database': '🗄️',
    'erd': '📊',

    # 기능 섹션
    'features': '✨',
    'requirements': '📋',
    'specifications': '📐',
    'user': '👤',
    'ux': '🎨',
    'ui': '🖼️',

    # 프로세스 섹션
    'workflow': '🔄',
    'process': '⚡',
    'flow': '➡️',
    'timeline': '📅',
    'schedule': '🗓️',
    'milestones': '🏁',

    # 품질 섹션
    'testing': '🧪',
    'quality': '✅',
    'security': '🔒',
    'performance': '🚀',

    # 배포/운영 섹션
    'deployment': '🚢',
    'infrastructure': '☁️',
    'monitoring': '📈',
    'operations': '🔧',

    # 문서 섹션
    'appendix': '📎',
    'references': '📖',
    'glossary': '📕',
    'changelog': '📝',
}


# ============================================================================
# Callout 스타일
# ============================================================================

CALLOUT_STYLES: dict[str, dict[str, Any]] = {
    'info': {
        'icon': 'ℹ️',
        'background': 'highlight_blue',
        'border_color': 'blue',
    },
    'warning': {
        'icon': '⚠️',
        'background': 'highlight_orange',
        'border_color': 'orange',
    },
    'success': {
        'icon': '✅',
        'background': 'highlight_green',
        'border_color': 'green',
    },
    'danger': {
        'icon': '🚨',
        'background': 'highlight_red',
        'border_color': 'red',
    },
    'tip': {
        'icon': '💡',
        'background': 'highlight_yellow',
        'border_color': 'yellow',
    },
    'note': {
        'icon': '📝',
        'background': 'highlight_gray',
        'border_color': 'text_muted',
    },
}


# ============================================================================
# 스타일 유틸리티 클래스
# ============================================================================

@dataclass
class NotionStyle:
    """Notion 스타일 설정 컨테이너"""
    colors: dict[str, dict[str, float]]
    typography: dict[int | str, dict[str, Any]]
    fonts: dict[str, str]
    icons: dict[str, str]
    callouts: dict[str, dict[str, Any]]

    @classmethod
    def default(cls) -> 'NotionStyle':
        """기본 Notion 스타일 반환"""
        return cls(
            colors=NOTION_COLORS,
            typography=NOTION_TYPOGRAPHY,
            fonts=NOTION_FONTS,
            icons=SECTION_ICONS,
            callouts=CALLOUT_STYLES,
        )

    def get_color(self, name: str) -> dict[str, float]:
        """색상 이름으로 RGB 값 반환"""
        return self.colors.get(name, self.colors['text_primary'])

    def get_heading_style(self, level: int) -> dict[str, Any]:
        """헤딩 레벨별 스타일 반환"""
        return self.typography.get(level, self.typography[6])

    def get_font(self, style_type: str) -> str:
        """스타일 타입에 맞는 폰트 반환"""
        font_key = self.typography.get(style_type, {}).get('font', 'body')
        return self.fonts.get(font_key, self.fonts['body'])

    def get_section_icon(self, section_name: str) -> str | None:
        """섹션 이름에 맞는 아이콘 반환"""
        section_lower = section_name.lower()
        for key, icon in self.icons.items():
            if key in section_lower:
                return icon
        return None

    def get_callout_style(self, callout_type: str) -> dict[str, Any]:
        """Callout 타입별 스타일 반환"""
        return self.callouts.get(callout_type, self.callouts['note'])


class NotionStyleMixin:
    """Notion 스타일 적용을 위한 Mixin 클래스"""

    def __init__(self, style: NotionStyle | None = None):
        self.style = style or NotionStyle.default()

    def _build_text_style(
        self,
        size: float | None = None,
        font: str | None = None,
        bold: bool = False,
        italic: bool = False,
        color: str | None = None,
        background: str | None = None,
        link: str | None = None,
    ) -> dict[str, Any]:
        """Google Docs textStyle 객체 생성"""
        text_style: dict[str, Any] = {}
        fields: list[str] = []

        if size:
            text_style['fontSize'] = {'magnitude': size, 'unit': 'PT'}
            fields.append('fontSize')

        if font:
            font_name = self.style.fonts.get(font, font)
            text_style['weightedFontFamily'] = {
                'fontFamily': font_name,
                'weight': 700 if bold else 400,
            }
            fields.append('weightedFontFamily')
        elif bold:
            text_style['bold'] = True
            fields.append('bold')

        if italic:
            text_style['italic'] = True
            fields.append('italic')

        if color:
            text_style['foregroundColor'] = {
                'color': {'rgbColor': self.style.get_color(color)}
            }
            fields.append('foregroundColor')

        if background:
            text_style['backgroundColor'] = {
                'color': {'rgbColor': self.style.get_color(background)}
            }
            fields.append('backgroundColor')

        if link:
            text_style['link'] = {'url': link}
            fields.append('link')

        return {'textStyle': text_style, 'fields': ','.join(fields)}

    def _build_paragraph_style(
        self,
        named_style: str | None = None,
        space_before: float | None = None,
        space_after: float | None = None,
        line_height: float | None = None,
        indent_start: float | None = None,
        indent_end: float | None = None,
        background: str | None = None,
        border_left: dict | None = None,
    ) -> dict[str, Any]:
        """Google Docs paragraphStyle 객체 생성"""
        para_style: dict[str, Any] = {}
        fields: list[str] = []

        if named_style:
            para_style['namedStyleType'] = named_style
            fields.append('namedStyleType')

        if space_before is not None:
            para_style['spaceAbove'] = {'magnitude': space_before, 'unit': 'PT'}
            fields.append('spaceAbove')

        if space_after is not None:
            para_style['spaceBelow'] = {'magnitude': space_after, 'unit': 'PT'}
            fields.append('spaceBelow')

        if line_height is not None:
            para_style['lineSpacing'] = line_height * 100
            fields.append('lineSpacing')

        if indent_start is not None:
            para_style['indentStart'] = {'magnitude': indent_start, 'unit': 'PT'}
            fields.append('indentStart')

        if indent_end is not None:
            para_style['indentEnd'] = {'magnitude': indent_end, 'unit': 'PT'}
            fields.append('indentEnd')

        if background:
            para_style['shading'] = {
                'backgroundColor': {'color': {'rgbColor': self.style.get_color(background)}}
            }
            fields.append('shading')

        if border_left:
            para_style['borderLeft'] = border_left
            fields.append('borderLeft')

        return {'paragraphStyle': para_style, 'fields': ','.join(fields)}


# ============================================================================
# 편의 함수
# ============================================================================

def get_default_style() -> NotionStyle:
    """기본 Notion 스타일 인스턴스 반환"""
    return NotionStyle.default()
