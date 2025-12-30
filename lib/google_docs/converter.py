"""
Markdown to Google Docs 변환기

마크다운을 Google Docs 네이티브 형식으로 변환합니다.
"""

import re
from typing import Any, Optional

from googleapiclient.discovery import build

from .auth import get_credentials, DEFAULT_FOLDER_ID
from .models import TextSegment, InlineParseResult
from .table_renderer import NativeTableRenderer


class MarkdownToDocsConverter:
    """마크다운을 Google Docs API 요청으로 변환"""

    def __init__(
        self,
        content: str,
        include_toc: bool = False,
        use_native_tables: bool = True,
        code_font: str = "Consolas",
        code_bg_color: tuple[float, float, float] = (0.95, 0.95, 0.95),
    ):
        """
        Args:
            content: 마크다운 콘텐츠
            include_toc: 목차 포함 여부
            use_native_tables: 네이티브 테이블 사용 여부
            code_font: 코드 블록 폰트
            code_bg_color: 코드 블록 배경색 (RGB 0-1)
        """
        self.content = content
        self.include_toc = include_toc
        self.use_native_tables = use_native_tables
        self.code_font = code_font
        self.code_bg_color = code_bg_color

        self.requests: list[dict[str, Any]] = []
        self.current_index = 1  # Google Docs는 1부터 시작
        self.headings: list[dict[str, Any]] = []

        self._table_renderer = NativeTableRenderer()

    def parse(self) -> list[dict[str, Any]]:
        """
        마크다운 파싱 및 Google Docs API 요청 생성

        Returns:
            list: batchUpdate에 전달할 요청 리스트
        """
        lines = self.content.split('\n')
        i = 0

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
                if text:
                    self._add_heading(text, level)
                i += 1
                continue

            # 테이블 처리
            if '|' in line and i + 1 < len(lines) and ('---' in lines[i + 1] or ':-' in lines[i + 1]):
                table_lines = []
                while i < len(lines) and '|' in lines[i]:
                    table_lines.append(lines[i])
                    i += 1
                self._add_table(table_lines)
                continue

            # 체크리스트 처리
            if line.strip().startswith('- [ ]') or line.strip().startswith('- [x]') or line.strip().startswith('- [X]'):
                checked = 'x' in line.strip()[3:5].lower()
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
                self._add_paragraph_with_inline_styles(f"{numbered_match.group(1)}. {text}")
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
        segments: list[TextSegment] = []
        plain_text = ""

        # 정규식 패턴들 (순서 중요)
        patterns = [
            (r'\[([^\]]+)\]\(([^)]+)\)', 'link'),      # [text](url)
            (r'\*\*(.+?)\*\*', 'bold'),                # **bold** (non-greedy, 내부 * 허용)
            (r'__(.+?)__', 'bold'),                    # __bold__ (non-greedy, 내부 _ 허용)
            (r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', 'italic'),  # *italic* (** 제외)
            (r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', 'italic'),        # _italic_ (__ 제외)
            (r'`([^`]+)`', 'code'),                    # `code`
            (r'~~(.+?)~~', 'strikethrough'),           # ~~strike~~ (non-greedy)
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
            self._apply_segment_style(segment, current_pos, end_pos)
            current_pos = end_pos

    def _add_heading(self, text: str, level: int):
        """제목 추가"""
        # 목차용 헤딩 수집
        self.headings.append({'text': text, 'level': level, 'index': self.current_index})

        start = self._add_text(text)

        # 제목 스타일 적용
        heading_style = f'HEADING_{min(level, 6)}'
        self.requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': self.current_index - 1
                },
                'paragraphStyle': {
                    'namedStyleType': heading_style
                },
                'fields': 'namedStyleType'
            }
        })

    def _add_table(self, table_lines: list[str]):
        """테이블 추가"""
        if self.use_native_tables:
            self._add_native_table(table_lines)
        else:
            self._add_text_table(table_lines)

    def _add_native_table(self, table_lines: list[str]):
        """네이티브 Google Docs 테이블 추가"""
        table_data = self._table_renderer.parse_markdown_table(table_lines)

        if table_data.column_count == 0:
            return

        # 테이블 앞 줄바꿈
        self._add_text('')

        # 테이블 렌더링
        requests, new_index = self._table_renderer.render(table_data, self.current_index)
        self.requests.extend(requests)
        self.current_index = new_index

        # 테이블 뒤 줄바꿈
        self._add_text('')

    def _add_text_table(self, table_lines: list[str]):
        """텍스트 기반 테이블 추가 (폴백)"""
        table_data = self._table_renderer.parse_markdown_table(table_lines)

        if table_data.column_count == 0:
            return

        # 각 열의 최대 너비 계산
        all_rows = [table_data.headers] + table_data.rows
        col_widths = [0] * table_data.column_count
        for row in all_rows:
            for i, cell in enumerate(row):
                if i < table_data.column_count:
                    col_widths[i] = max(col_widths[i], len(cell))

        # 정렬된 텍스트 테이블 생성
        for row_idx, row in enumerate(all_rows):
            padded_cells = []
            for i in range(table_data.column_count):
                cell = row[i] if i < len(row) else ""
                padded_cells.append(cell.ljust(col_widths[i]))

            line_text = " | ".join(padded_cells)

            if row_idx == 0:
                # 헤더 행 (볼드)
                start = self._add_text(line_text)
                self.requests.append({
                    'updateTextStyle': {
                        'range': {'startIndex': start, 'endIndex': self.current_index - 1},
                        'textStyle': {'bold': True},
                        'fields': 'bold'
                    }
                })
                # 구분선
                separator = "-+-".join("-" * w for w in col_widths)
                self._add_text(separator)
            else:
                self._add_text(line_text)

    def _add_code_block(self, code: str, lang: str = ''):
        """코드 블록 추가"""
        # 언어 표시
        if lang:
            self._add_text(f'[{lang}]')

        start = self._add_text(code)

        # 코드 스타일 (고정폭 폰트 + 배경색)
        self.requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': self.current_index - 1
                },
                'textStyle': {
                    'weightedFontFamily': {
                        'fontFamily': self.code_font,
                        'weight': 400
                    },
                    'fontSize': {'magnitude': 10, 'unit': 'PT'},
                    'backgroundColor': {
                        'color': {'rgbColor': {
                            'red': self.code_bg_color[0],
                            'green': self.code_bg_color[1],
                            'blue': self.code_bg_color[2]
                        }}
                    }
                },
                'fields': 'weightedFontFamily,fontSize,backgroundColor'
            }
        })

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

    def _add_checklist_item(self, text: str, checked: bool):
        """체크리스트 아이템 추가"""
        checkbox = '☑' if checked else '☐'
        result = self._parse_inline_formatting(text)
        full_text = ''.join(seg.text for seg in result.segments)
        self._add_text(f"{checkbox} {full_text}")

    def _add_quote(self, text: str):
        """인용문 추가"""
        start = self._add_text(f"│ {text}")

        # 이탤릭 + 회색 스타일
        self.requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': self.current_index - 1
                },
                'textStyle': {
                    'italic': True,
                    'foregroundColor': {
                        'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}
                    }
                },
                'fields': 'italic,foregroundColor'
            }
        })

    def _add_horizontal_rule(self):
        """수평선 추가"""
        self._add_text('─' * 50)

    def _apply_segment_style(self, segment: TextSegment, start: int, end: int):
        """세그먼트에 스타일 적용"""
        style_fields = []
        text_style: dict[str, Any] = {}

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
            text_style['weightedFontFamily'] = {
                'fontFamily': self.code_font,
                'weight': 400
            }
            text_style['backgroundColor'] = {
                'color': {'rgbColor': {
                    'red': self.code_bg_color[0],
                    'green': self.code_bg_color[1],
                    'blue': self.code_bg_color[2]
                }}
            }
            style_fields.extend(['weightedFontFamily', 'backgroundColor'])

        if segment.link:
            text_style['link'] = {'url': segment.link}
            text_style['foregroundColor'] = {
                'color': {'rgbColor': {'red': 0.06, 'green': 0.46, 'blue': 0.88}}
            }
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
    include_toc: bool = False,
    use_native_tables: bool = False,  # 기본값: 텍스트 테이블 (더 안정적)
) -> str:
    """
    Google Docs 문서 생성

    Args:
        title: 문서 제목
        content: 마크다운 콘텐츠
        folder_id: Google Drive 폴더 ID (None이면 기본 폴더)
        include_toc: 목차 포함 여부
        use_native_tables: 네이티브 테이블 사용 여부

    Returns:
        str: 생성된 문서의 URL
    """
    creds = get_credentials()

    # API 서비스 생성
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # 1. 빈 문서 생성
    doc = docs_service.documents().create(body={'title': title}).execute()
    doc_id = doc.get('documentId')
    print(f"[OK] 문서 생성됨: {title}")
    print(f"     ID: {doc_id}")

    # 2. 폴더로 이동
    target_folder = folder_id or DEFAULT_FOLDER_ID
    try:
        file = drive_service.files().get(fileId=doc_id, fields='parents').execute()
        previous_parents = ','.join(file.get('parents', []))

        drive_service.files().update(
            fileId=doc_id,
            addParents=target_folder,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        print(f"     폴더로 이동됨")
    except Exception as e:
        print(f"     폴더 이동 실패: {e}")

    # 3. 콘텐츠 변환 및 추가
    converter = MarkdownToDocsConverter(
        content,
        include_toc=include_toc,
        use_native_tables=use_native_tables
    )
    requests = converter.parse()

    if requests:
        try:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            print(f"     콘텐츠 추가됨: {len(requests)} 요청")
        except Exception as e:
            print(f"     콘텐츠 추가 실패: {e}")
            raise

    # 4. 문서 URL 반환
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_url
