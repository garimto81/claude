#!/usr/bin/env python3
"""
PRD to Google Docs Converter (Notion Style)

PRD 마크다운 파일을 Google Docs로 변환하여 업로드합니다.
Notion 스타일의 깔끔한 디자인과 세련된 타이포그래피를 적용합니다.

Features:
- Notion 스타일 디자인 (파스텔 색상, 넉넉한 여백)
- 섹션 아이콘 자동 추가
- 인라인 스타일 지원 (bold, italic, code, strikethrough)
- 하이퍼링크 변환
- 실제 테이블 생성
- 목차 자동 생성
- 배치 변환 지원
- CLI 옵션

Usage:
    python scripts/prd_to_google_docs.py [OPTIONS] [FILE...]

Examples:
    python scripts/prd_to_google_docs.py                           # 기본 PRD 변환
    python scripts/prd_to_google_docs.py tasks/prds/*.md           # 배치 변환
    python scripts/prd_to_google_docs.py --toc --folder ID file.md # 목차 + 폴더 지정
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Notion 스타일 시스템 import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from lib.google_docs.notion_style import (
    NOTION_COLORS,
    NOTION_FONTS,
    NOTION_TYPOGRAPHY,
    SECTION_ICONS,
    NotionStyle,
    get_default_style,
)

# OAuth 2.0 설정 (절대 경로)
CREDENTIALS_FILE = r'D:\AI\claude01\json\desktop_credentials.json'
TOKEN_FILE = r'D:\AI\claude01\json\token.json'

# Google Docs + Drive 권한
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

# 공유 폴더 ID (Google AI Studio 폴더)
DEFAULT_FOLDER_ID = '1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW'

# ============================================================================
# Notion 스타일 시스템 (lib/google_docs/notion_style.py에서 가져옴)
# ============================================================================

# 스타일 인스턴스 생성
STYLE = get_default_style()

# 기존 코드와의 호환성을 위한 별칭
COLORS = NOTION_COLORS
FONTS = NOTION_FONTS

# Heading 스타일 (강조된 스타일)
HEADING_STYLES = {
    1: {'size': 32, 'color': 'heading_primary', 'space_before': 48, 'space_after': 16, 'underline': True},
    2: {'size': 24, 'color': 'heading_secondary', 'space_before': 36, 'space_after': 12, 'border_bottom': True},
    3: {'size': 18, 'color': 'heading_secondary', 'space_before': 28, 'space_after': 8},
    4: {'size': 16, 'color': 'text_primary', 'space_before': 20, 'space_after': 6},
    5: {'size': 14, 'color': 'text_secondary', 'space_before': 16, 'space_after': 4},
    6: {'size': 13, 'color': 'text_secondary', 'space_before': 12, 'space_after': 4},
}


def get_credentials():
    """OAuth 2.0 인증 처리"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


@dataclass
class TextSegment:
    """텍스트 세그먼트 (스타일 정보 포함)"""
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    strikethrough: bool = False
    link: Optional[str] = None


@dataclass
class InlineParseResult:
    """인라인 파싱 결과"""
    segments: list = field(default_factory=list)
    plain_text: str = ""


class MarkdownToDocsConverter:
    """마크다운을 Google Docs 형식으로 변환 (최적화 버전)"""

    def __init__(self, content: str, include_toc: bool = False):
        self.content = content
        self.include_toc = include_toc
        self.requests = []
        self.current_index = 1  # Google Docs는 1부터 시작
        self.headings = []  # 목차용 헤딩 수집
        self.pending_tables = []  # 테이블 정보 (나중에 처리)

    def parse(self) -> list:
        """마크다운 파싱 및 Google Docs 요청 생성"""
        lines = self.content.split('\n')
        i = 0

        # 목차 자리 예약 (나중에 채움)
        toc_placeholder_start = None
        if self.include_toc:
            toc_placeholder_start = self.current_index
            self._add_text("[목차 생성 중...]\n")

        while i < len(lines):
            line = lines[i]

            # 코드 블록 처리
            if line.startswith('```'):
                code_lines = []
                lang = line[3:].strip()
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                self._add_code_block('\n'.join(code_lines), lang)
                i += 1
                continue

            # 제목 처리
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                self._add_heading(text, level)
                i += 1
                continue

            # 테이블 처리
            if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
                table_lines = []
                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i])
                    i += 1
                self._add_table(table_lines)
                continue

            # 체크리스트 처리
            if line.strip().startswith('- [ ]') or line.strip().startswith('- [x]'):
                checked = line.strip().startswith('- [x]')
                text = line.strip()[5:].strip()
                self._add_checklist_item(text, checked)
                i += 1
                continue

            # 일반 리스트 처리
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                text = line.strip()[2:]
                self._add_bullet_item(text)
                i += 1
                continue

            # 번호 리스트 처리
            numbered_match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
            if numbered_match:
                text = numbered_match.group(2)
                self._add_numbered_item(text)
                i += 1
                continue

            # 인용문 처리
            if line.strip().startswith('>'):
                text = line.strip()[1:].strip()
                self._add_quote(text)
                i += 1
                continue

            # 수평선 처리
            if line.strip() in ['---', '***', '___']:
                self._add_horizontal_rule()
                i += 1
                continue

            # 일반 텍스트 (인라인 스타일 적용)
            if line.strip():
                self._add_paragraph_with_inline_styles(line)
            else:
                self._add_text('\n')

            i += 1

        return self.requests

    def _parse_inline_formatting(self, text: str) -> InlineParseResult:
        """인라인 포맷팅 파싱 (볼드, 이탤릭, 코드, 링크)"""
        segments = []
        plain_text = ""

        # 정규식 패턴들
        patterns = [
            (r'\[([^\]]+)\]\(([^)]+)\)', 'link'),      # [text](url)
            (r'\*\*([^*]+)\*\*', 'bold'),              # **bold**
            (r'__([^_]+)__', 'bold'),                  # __bold__
            (r'\*([^*]+)\*', 'italic'),                # *italic*
            (r'_([^_]+)_', 'italic'),                  # _italic_
            (r'`([^`]+)`', 'code'),                    # `code`
            (r'~~([^~]+)~~', 'strikethrough'),         # ~~strike~~
        ]

        # 모든 매치 찾기
        all_matches = []
        for pattern, style in patterns:
            for match in re.finditer(pattern, text):
                if style == 'link':
                    all_matches.append((match.start(), match.end(), match.group(1), style, match.group(2)))
                else:
                    all_matches.append((match.start(), match.end(), match.group(1), style, None))

        # 위치순 정렬
        all_matches.sort(key=lambda x: x[0])

        # 겹치는 매치 제거
        filtered_matches = []
        last_end = 0
        for match in all_matches:
            if match[0] >= last_end:
                filtered_matches.append(match)
                last_end = match[1]

        # 세그먼트 생성
        current_pos = 0
        for start, end, content, style, link_url in filtered_matches:
            # 이전 일반 텍스트
            if start > current_pos:
                plain_segment = text[current_pos:start]
                segments.append(TextSegment(text=plain_segment))
                plain_text += plain_segment

            # 스타일 적용 텍스트
            segment = TextSegment(text=content)
            if style == 'bold':
                segment.bold = True
            elif style == 'italic':
                segment.italic = True
            elif style == 'code':
                segment.code = True
            elif style == 'strikethrough':
                segment.strikethrough = True
            elif style == 'link':
                segment.link = link_url

            segments.append(segment)
            plain_text += content
            current_pos = end

        # 남은 텍스트
        if current_pos < len(text):
            remaining = text[current_pos:]
            segments.append(TextSegment(text=remaining))
            plain_text += remaining

        if not segments:
            segments.append(TextSegment(text=text))
            plain_text = text

        return InlineParseResult(segments=segments, plain_text=plain_text)

    def _add_text(self, text: str) -> int:
        """텍스트 삽입 요청 추가"""
        if not text:
            text = '\n'
        elif not text.endswith('\n'):
            text = text + '\n'

        self.requests.append({
            'insertText': {
                'location': {'index': self.current_index},
                'text': text
            }
        })

        start_index = self.current_index
        self.current_index += len(text)
        return start_index

    def _add_paragraph_with_inline_styles(self, text: str):
        """인라인 스타일이 적용된 단락 추가"""
        result = self._parse_inline_formatting(text)

        # 전체 텍스트 먼저 삽입
        full_text = ''.join(seg.text for seg in result.segments)
        start = self._add_text(full_text)

        # 각 세그먼트에 스타일 적용
        current_pos = start
        for segment in result.segments:
            end_pos = current_pos + len(segment.text)

            style_fields = []
            text_style = {}

            if segment.bold:
                text_style['bold'] = True
                style_fields.append('bold')

            if segment.italic:
                text_style['italic'] = True
                style_fields.append('italic')

            if segment.strikethrough:
                text_style['strikethrough'] = True
                style_fields.append('strikethrough')

            if segment.code:
                # Notion 스타일 인라인 코드 (빨간색 텍스트 + 연한 배경)
                text_style['weightedFontFamily'] = {'fontFamily': FONTS['code'], 'weight': 400}
                text_style['fontSize'] = {'magnitude': 13, 'unit': 'PT'}
                text_style['backgroundColor'] = {'color': {'rgbColor': COLORS['code_bg']}}
                text_style['foregroundColor'] = {'color': {'rgbColor': COLORS['code_text']}}
                style_fields.extend(['weightedFontFamily', 'fontSize', 'backgroundColor', 'foregroundColor'])

            if segment.link:
                # Notion 스타일 링크 (부드러운 파란색, 밑줄)
                text_style['link'] = {'url': segment.link}
                text_style['foregroundColor'] = {'color': {'rgbColor': COLORS['blue']}}
                text_style['underline'] = True
                style_fields.extend(['link', 'foregroundColor', 'underline'])

            if style_fields:
                self.requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': current_pos,
                            'endIndex': end_pos
                        },
                        'textStyle': text_style,
                        'fields': ','.join(style_fields)
                    }
                })

            current_pos = end_pos

    def _add_heading(self, text: str, level: int):
        """제목 추가 (강조된 스타일 - 아이콘 + 테두리)"""
        # 목차용 헤딩 수집
        self.headings.append({'text': text, 'level': level, 'index': self.current_index})

        # 섹션 아이콘 찾기 (H2, H3에만 적용)
        icon = None
        if level in [2, 3]:
            icon = STYLE.get_section_icon(text)

        # 아이콘이 있으면 제목 앞에 추가
        display_text = f"{icon}  {text}" if icon else text

        start = self._add_text(display_text)
        end = self.current_index - 1

        # 스타일 설정 가져오기
        style_config = HEADING_STYLES.get(level, HEADING_STYLES[3])
        color = COLORS.get(style_config['color'], COLORS['text_primary'])

        # 제목 스타일 적용 (기본 heading + 커스텀 스타일)
        heading_style = f'HEADING_{min(level, 6)}'

        # Paragraph 스타일 구성
        para_style = {
            'namedStyleType': heading_style,
            'spaceAbove': {'magnitude': style_config['space_before'], 'unit': 'PT'},
            'spaceBelow': {'magnitude': style_config['space_after'], 'unit': 'PT'},
            'lineSpacing': 130,
        }
        para_fields = ['namedStyleType', 'spaceAbove', 'spaceBelow', 'lineSpacing']

        # H1, H2에 하단 테두리 추가
        if level in [1, 2]:
            para_style['borderBottom'] = {
                'color': {'color': {'rgbColor': COLORS['border']}},
                'width': {'magnitude': 1, 'unit': 'PT'},
                'padding': {'magnitude': 8, 'unit': 'PT'},
                'dashStyle': 'SOLID',
            }
            para_fields.append('borderBottom')

        self.requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'paragraphStyle': para_style,
                'fields': ','.join(para_fields)
            }
        })

        # 텍스트 스타일 (강조된 색상)
        self.requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'textStyle': {
                    'bold': True,
                    'fontSize': {'magnitude': style_config['size'], 'unit': 'PT'},
                    'foregroundColor': {'color': {'rgbColor': color}},
                    'weightedFontFamily': {'fontFamily': FONTS['heading'], 'weight': 700},
                },
                'fields': 'bold,fontSize,foregroundColor,weightedFontFamily'
            }
        })

    def _add_code_block(self, code: str, lang: str = ''):
        """코드 블록 추가 (강조된 스타일 - 테두리 + 배경)"""
        # 코드 블록 앞에 언어 표시 (눈에 띄는 라벨)
        if lang:
            lang_start = self._add_text(f' {lang.upper()} ')
            self.requests.append({
                'updateTextStyle': {
                    'range': {'startIndex': lang_start, 'endIndex': self.current_index - 1},
                    'textStyle': {
                        'weightedFontFamily': {'fontFamily': FONTS['code'], 'weight': 500},
                        'fontSize': {'magnitude': 10, 'unit': 'PT'},
                        'foregroundColor': {'color': {'rgbColor': COLORS['blue']}},
                        'backgroundColor': {'color': {'rgbColor': COLORS['highlight_blue']}},
                    },
                    'fields': 'weightedFontFamily,fontSize,foregroundColor,backgroundColor'
                }
            })

        start = self._add_text(code)
        end = self.current_index - 1

        # 코드 스타일 (강조된 배경)
        self.requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'textStyle': {
                    'weightedFontFamily': {'fontFamily': FONTS['code'], 'weight': 400},
                    'fontSize': {'magnitude': 12, 'unit': 'PT'},
                    'foregroundColor': {'color': {'rgbColor': COLORS['text_primary']}},
                    'backgroundColor': {'color': {'rgbColor': COLORS['code_bg']}},
                },
                'fields': 'weightedFontFamily,fontSize,foregroundColor,backgroundColor'
            }
        })

        # 코드 블록 스타일 (테두리 + 패딩)
        self.requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'paragraphStyle': {
                    'indentStart': {'magnitude': 16, 'unit': 'PT'},
                    'indentEnd': {'magnitude': 16, 'unit': 'PT'},
                    'spaceAbove': {'magnitude': 12, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 12, 'unit': 'PT'},
                    'lineSpacing': 140,
                    'borderLeft': {
                        'color': {'color': {'rgbColor': COLORS['blue']}},
                        'width': {'magnitude': 3, 'unit': 'PT'},
                        'padding': {'magnitude': 12, 'unit': 'PT'},
                        'dashStyle': 'SOLID',
                    },
                },
                'fields': 'indentStart,indentEnd,spaceAbove,spaceBelow,lineSpacing,borderLeft'
            }
        })

    def _add_table(self, table_lines: list):
        """테이블 정보 저장 (나중에 별도 처리)."""
        # 테이블 데이터 파싱
        rows = []
        for line in table_lines:
            if '---' in line:
                continue
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if cells:
                rows.append(cells)

        if not rows:
            return

        num_rows = len(rows)
        num_cols = max(len(row) for row in rows)

        # 테이블 삽입 요청
        self.requests.append({
            'insertTable': {
                'rows': num_rows,
                'columns': num_cols,
                'location': {'index': self.current_index}
            }
        })

        # 테이블 정보 저장 (나중에 셀 내용 삽입용)
        self.pending_tables.append({
            'insert_index': self.current_index,
            'rows': rows,
            'num_rows': num_rows,
            'num_cols': num_cols
        })

        # 테이블 후 인덱스 업데이트
        # 실제 테이블 구조 (테스트로 확인):
        # - 테이블 앞 빈 paragraph(1)
        # - 테이블 본체: 테이블 시작(1) + 행 수 * (행 시작(1) + 셀 수 * 2) + 테이블 끝(1)
        # - 테이블 뒤 빈 paragraph(1) - 마지막 \n은 다음 삽입 시 덮어씀
        # 2x2 테이블: 1 + (2 + 2*(1+2*2)) + 0 = 1 + 12 = 13 (다음 삽입은 paragraph 시작에)
        table_body = 2 + num_rows * (1 + num_cols * 2)
        table_size = 1 + table_body  # 테이블 후 paragraph 시작 위치
        self.current_index += table_size

    def _add_bullet_item(self, text: str):
        """불릿 리스트 아이템 추가"""
        result = self._parse_inline_formatting(text)
        full_text = ''.join(seg.text for seg in result.segments)

        start = self._add_text(f"• {full_text}")

        # 인라인 스타일 적용 (bullet 문자 다음부터)
        current_pos = start + 2  # "• " 건너뛰기
        for segment in result.segments:
            end_pos = current_pos + len(segment.text)
            self._apply_segment_style(segment, current_pos, end_pos)
            current_pos = end_pos

    def _add_numbered_item(self, text: str):
        """번호 리스트 아이템 추가"""
        self._add_paragraph_with_inline_styles(text)

    def _add_checklist_item(self, text: str, checked: bool):
        """체크리스트 아이템 추가"""
        checkbox = '☑' if checked else '☐'
        result = self._parse_inline_formatting(text)
        full_text = ''.join(seg.text for seg in result.segments)
        self._add_text(f"{checkbox} {full_text}")

    def _add_quote(self, text: str):
        """인용문 추가 (Notion 스타일 - 연한 배경 + 왼쪽 테두리)"""
        start = self._add_text(f"  {text}")
        end = self.current_index - 1

        # 텍스트 스타일 (Notion 스타일 - 이탤릭 없이 깔끔하게)
        self.requests.append({
            'updateTextStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'textStyle': {
                    'foregroundColor': {'color': {'rgbColor': COLORS['text_secondary']}},
                    'fontSize': {'magnitude': 14, 'unit': 'PT'},
                },
                'fields': 'foregroundColor,fontSize'
            }
        })

        # Paragraph 스타일 (Notion 스타일 - 회색 왼쪽 테두리 + 연한 배경)
        self.requests.append({
            'updateParagraphStyle': {
                'range': {'startIndex': start, 'endIndex': end},
                'paragraphStyle': {
                    'indentStart': {'magnitude': 16, 'unit': 'PT'},
                    'indentEnd': {'magnitude': 16, 'unit': 'PT'},
                    'borderLeft': {
                        'color': {'color': {'rgbColor': COLORS['text_muted']}},
                        'width': {'magnitude': 3, 'unit': 'PT'},
                        'padding': {'magnitude': 12, 'unit': 'PT'},
                        'dashStyle': 'SOLID',
                    },
                    'shading': {
                        'backgroundColor': {'color': {'rgbColor': COLORS['background_gray']}}
                    },
                    'spaceAbove': {'magnitude': 12, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 12, 'unit': 'PT'},
                    'lineSpacing': 160,  # 1.6 line-height
                },
                'fields': 'indentStart,indentEnd,borderLeft,shading,spaceAbove,spaceBelow,lineSpacing'
            }
        })

    def _add_horizontal_rule(self):
        """수평선 추가"""
        self._add_text('─' * 50)

    def _apply_segment_style(self, segment: TextSegment, start: int, end: int):
        """세그먼트에 스타일 적용"""
        style_fields = []
        text_style = {}

        if segment.bold:
            text_style['bold'] = True
            style_fields.append('bold')

        if segment.italic:
            text_style['italic'] = True
            style_fields.append('italic')

        if segment.code:
            # Notion 스타일 인라인 코드
            text_style['weightedFontFamily'] = {'fontFamily': FONTS['code'], 'weight': 400}
            text_style['fontSize'] = {'magnitude': 13, 'unit': 'PT'}
            text_style['backgroundColor'] = {'color': {'rgbColor': COLORS['code_bg']}}
            text_style['foregroundColor'] = {'color': {'rgbColor': COLORS['code_text']}}
            style_fields.extend(['weightedFontFamily', 'fontSize', 'backgroundColor', 'foregroundColor'])

        if segment.link:
            # Notion 스타일 링크
            text_style['link'] = {'url': segment.link}
            text_style['foregroundColor'] = {'color': {'rgbColor': COLORS['blue']}}
            text_style['underline'] = True
            style_fields.extend(['link', 'foregroundColor', 'underline'])

        if style_fields:
            self.requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': end
                    },
                    'textStyle': text_style,
                    'fields': ','.join(style_fields)
                }
            })


def create_google_doc(
    title: str,
    content: str,
    folder_id: Optional[str] = None,
    include_toc: bool = False
) -> str:
    """Google Docs 문서 생성"""
    creds = get_credentials()

    # API 서비스 생성
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # 1. 빈 문서 생성
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc.get('documentId')
    print(f"  문서 생성됨: {title}")
    print(f"  ID: {doc_id}")

    # 2. 폴더로 이동 (선택적)
    if folder_id:
        try:
            file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
            previous_parents = ','.join(file.get('parents', []))

            drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            print(f"  폴더로 이동됨")
        except Exception as e:
            print(f"  폴더 이동 실패: {e}")

    # 3. 내용 추가
    converter = MarkdownToDocsConverter(content, include_toc=include_toc)
    requests = converter.parse()

    if requests:
        try:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            print(f"  Content added: {len(requests)} requests")
        except Exception as e:
            print(f"  Content add failed: {e}")

    # 4. 테이블 셀 내용 삽입 (별도 처리)
    if converter.pending_tables:
        try:
            _fill_table_cells(docs_service, doc_id, converter.pending_tables)
            print(f"  Tables filled: {len(converter.pending_tables)} tables")
        except Exception as e:
            print(f"  Table fill failed: {e}")

    # 5. 문서 URL 반환
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_url


def _fill_table_cells(docs_service, doc_id: str, pending_tables: list):
    """테이블 셀에 내용 삽입 (문서 구조 분석 후)."""
    # 문서 가져오기
    doc = docs_service.documents().get(documentId=doc_id).execute()
    body_content = doc.get('body', {}).get('content', [])

    # 문서에서 테이블 찾기
    tables_in_doc = []
    for element in body_content:
        if 'table' in element:
            tables_in_doc.append({
                'startIndex': element.get('startIndex'),
                'table': element.get('table')
            })

    # 모든 셀 삽입 요청 수집
    all_insert_requests = []
    all_style_requests = []

    for table_idx, pending in enumerate(pending_tables):
        if table_idx >= len(tables_in_doc):
            continue

        table_info = tables_in_doc[table_idx]
        table_struct = table_info['table']
        rows_data = pending['rows']

        for row_idx, table_row in enumerate(table_struct.get('tableRows', [])):
            row_data = rows_data[row_idx] if row_idx < len(rows_data) else []

            for col_idx, table_cell in enumerate(table_row.get('tableCells', [])):
                cell_text = row_data[col_idx] if col_idx < len(row_data) else ""
                if not cell_text:
                    continue

                # 셀 내 첫 번째 paragraph의 시작 인덱스
                cell_content = table_cell.get('content', [])
                if cell_content:
                    para = cell_content[0]
                    para_start = para.get('startIndex', 0)

                    all_insert_requests.append({
                        'insertText': {
                            'location': {'index': para_start},
                            'text': cell_text
                        },
                        '_sort_index': para_start
                    })

                    # 헤더 행 (첫 번째 행) 볼드 스타일
                    if row_idx == 0:
                        all_style_requests.append({
                            'updateTextStyle': {
                                'range': {
                                    'startIndex': para_start,
                                    'endIndex': para_start + len(cell_text)
                                },
                                'textStyle': {'bold': True},
                                'fields': 'bold'
                            },
                            '_sort_index': para_start
                        })

    # 역순으로 정렬 (인덱스가 큰 것부터 삽입해야 앞쪽 인덱스에 영향 없음)
    all_insert_requests.sort(key=lambda r: r['_sort_index'], reverse=True)

    # _sort_index 제거
    for r in all_insert_requests:
        del r['_sort_index']
    for r in all_style_requests:
        del r['_sort_index']

    # insertText 먼저 실행, 그 다음 스타일 적용
    if all_insert_requests:
        docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': all_insert_requests}
        ).execute()

    # 스타일 적용 (텍스트 삽입 후 인덱스가 변경되므로 다시 문서 가져오기)
    if all_style_requests:
        # 문서 다시 가져오기
        doc = docs_service.documents().get(documentId=doc_id).execute()
        body_content = doc.get('body', {}).get('content', [])

        # 테이블에서 헤더 행 셀 찾기 및 스타일 적용
        style_requests = []
        cell_style_requests = []

        for element in body_content:
            if 'table' in element:
                table = element['table']
                table_start = element.get('startIndex', 0)
                first_row = table.get('tableRows', [{}])[0]

                for col_idx, cell in enumerate(first_row.get('tableCells', [])):
                    cell_content = cell.get('content', [])
                    if cell_content:
                        para = cell_content[0]
                        elements = para.get('paragraph', {}).get('elements', [])
                        if elements:
                            text_run = elements[0].get('textRun', {})
                            content = text_run.get('content', '').rstrip('\n')
                            if content:
                                start = elements[0].get('startIndex', 0)
                                end = start + len(content)
                                # 텍스트 볼드 + 색상
                                style_requests.append({
                                    'updateTextStyle': {
                                        'range': {'startIndex': start, 'endIndex': end},
                                        'textStyle': {
                                            'bold': True,
                                            'foregroundColor': {'color': {'rgbColor': COLORS['heading_secondary']}},
                                        },
                                        'fields': 'bold,foregroundColor'
                                    }
                                })

                    # 헤더 셀 배경색 (tableRange 사용)
                    cell_style_requests.append({
                        'updateTableCellStyle': {
                            'tableRange': {
                                'tableCellLocation': {
                                    'tableStartLocation': {'index': table_start},
                                    'rowIndex': 0,
                                    'columnIndex': col_idx,
                                },
                                'rowSpan': 1,
                                'columnSpan': 1,
                            },
                            'tableCellStyle': {
                                'backgroundColor': {'color': {'rgbColor': COLORS['table_header_bg']}},
                            },
                            'fields': 'backgroundColor'
                        }
                    })

        if style_requests:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': style_requests}
            ).execute()

        if cell_style_requests:
            try:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': cell_style_requests}
                ).execute()
            except Exception as e:
                # 셀 스타일 실패해도 계속 진행
                print(f"  Table cell style warning: {e}")


def process_file(
    file_path: Path,
    folder_id: Optional[str] = None,
    include_toc: bool = False
) -> Optional[str]:
    """단일 파일 처리"""
    if not file_path.exists():
        print(f"[FAIL] File not found: {file_path}")
        return None

    content = file_path.read_text(encoding='utf-8')

    # 제목 추출
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.stem

    print(f"\n[FILE] {file_path.name}")

    try:
        doc_url = create_google_doc(title, content, folder_id, include_toc)
        print(f"  [OK] {doc_url}")
        return doc_url
    except Exception as e:
        print(f"  [FAIL] {e}")
        return None


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='PRD 마크다운을 Google Docs로 변환',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # 기본 PRD 변환
  %(prog)s tasks/prds/PRD-0001.md       # 특정 파일 변환
  %(prog)s tasks/prds/*.md              # 배치 변환
  %(prog)s --toc file.md                # 목차 포함
  %(prog)s --folder FOLDER_ID file.md   # 폴더 지정
        """
    )

    parser.add_argument(
        'files',
        nargs='*',
        help='변환할 마크다운 파일 (없으면 기본 PRD)'
    )

    parser.add_argument(
        '--folder', '-f',
        default=DEFAULT_FOLDER_ID,
        help=f'대상 Google Drive 폴더 ID (기본: {DEFAULT_FOLDER_ID[:20]}...)'
    )

    parser.add_argument(
        '--toc',
        action='store_true',
        help='목차 자동 생성'
    )

    parser.add_argument(
        '--no-folder',
        action='store_true',
        help='폴더 이동 없이 내 드라이브에 생성'
    )

    args = parser.parse_args()

    # 폴더 ID 결정
    folder_id = None if args.no_folder else args.folder

    # 파일 목록 결정
    if not args.files:
        # 기본 PRD 파일
        default_prd = Path(r'D:\AI\claude01\automation_feature_table\tasks\prds\PRD-0001-poker-hand-auto-capture.md')
        files = [default_prd]
    else:
        files = []
        for pattern in args.files:
            if '*' in pattern:
                # 와일드카드 확장
                base_path = Path(r'D:\AI\claude01\automation_feature_table')
                files.extend(base_path.glob(pattern))
            else:
                file_path = Path(pattern)
                if not file_path.is_absolute():
                    file_path = Path(r'D:\AI\claude01\automation_feature_table') / file_path
                files.append(file_path)

    print("=" * 60)
    print("PRD to Google Docs Converter (Optimized)")
    print("=" * 60)
    print(f"파일 수: {len(files)}")
    print(f"폴더 ID: {folder_id or '(내 드라이브)'}")
    print(f"목차: {'예' if args.toc else '아니오'}")
    print("=" * 60)

    # 파일 처리
    results = []
    for file_path in files:
        result = process_file(file_path, folder_id, args.toc)
        results.append((file_path, result))

    # 결과 요약
    print("\n" + "=" * 60)
    print("결과 요약")
    print("=" * 60)

    success_count = sum(1 for _, url in results if url)
    print(f"성공: {success_count}/{len(results)}")

    for file_path, url in results:
        status = "[OK]" if url else "[FAIL]"
        print(f"  {status} {file_path.name}")
        if url:
            print(f"      {url}")

    print("=" * 60)


if __name__ == '__main__':
    main()
