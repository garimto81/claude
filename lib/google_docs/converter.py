"""
Markdown to Google Docs 변환기

마크다운을 Google Docs 네이티브 형식으로 변환합니다.
Premium Dark Text 스타일 시스템 연동.
"""

import re
from typing import Any, Optional

from googleapiclient.discovery import build

from .auth import get_credentials, DEFAULT_FOLDER_ID
from .models import TextSegment, InlineParseResult
from .table_renderer import NativeTableRenderer
from .notion_style import NotionStyle


class MarkdownToDocsConverter:
    """마크다운을 Google Docs API 요청으로 변환"""

    def __init__(
        self,
        content: str,
        include_toc: bool = False,
        use_native_tables: bool = True,
        code_font: str = "Consolas",
        code_bg_color: tuple[float, float, float] | None = None,
        use_premium_style: bool = True,
        docs_service: Any = None,
        doc_id: str | None = None,
    ):
        """
        Args:
            content: 마크다운 콘텐츠
            include_toc: 목차 포함 여부
            use_native_tables: 네이티브 테이블 사용 여부
            code_font: 코드 블록 폰트
            code_bg_color: 코드 블록 배경색 (RGB 0-1), None이면 스타일에서 가져옴
            use_premium_style: 파랑 계열 전문 문서 스타일 사용 여부
            docs_service: Google Docs API 서비스 (2단계 테이블 처리용)
            doc_id: 문서 ID (2단계 테이블 처리용)
        """
        self.content = content
        self.include_toc = include_toc
        self.use_native_tables = use_native_tables
        self.code_font = code_font
        self.use_premium_style = use_premium_style
        self.docs_service = docs_service
        self.doc_id = doc_id

        # 파랑 계열 전문 문서 스타일 시스템
        self.style = NotionStyle.default() if use_premium_style else None

        # 코드 배경색: 명시적 지정 > 스타일 시스템 > 기본값
        if code_bg_color is not None:
            self.code_bg_color = code_bg_color
        elif self.style:
            bg = self.style.get_color('code_bg')
            self.code_bg_color = (bg['red'], bg['green'], bg['blue'])
        else:
            self.code_bg_color = (0.949, 0.949, 0.949)  # #F2F2F2

        self.requests: list[dict[str, Any]] = []
        self.current_index = 1  # Google Docs는 1부터 시작
        self.headings: list[dict[str, Any]] = []

        self._table_renderer = NativeTableRenderer()

        # 참조 링크 저장소
        self._reference_links: dict[str, str] = {}

        # YAML frontmatter 제거 및 참조 링크 파싱
        self._preprocess_content()

    def _preprocess_content(self):
        """
        콘텐츠 전처리
        - YAML frontmatter 제거
        - 참조 링크 추출
        - 각주 추출
        """
        lines = self.content.split('\n')
        processed_lines = []
        i = 0

        # 1. YAML frontmatter 제거 (--- ... --- 로 감싸진 부분)
        if lines and lines[0].strip() == '---':
            i = 1
            while i < len(lines) and lines[i].strip() != '---':
                i += 1
            i += 1  # 닫는 --- 건너뛰기

        # 2. 참조 링크 및 각주 추출
        while i < len(lines):
            line = lines[i]

            # 참조 링크: [ref]: url
            ref_match = re.match(r'^\[([^\]]+)\]:\s*(.+)$', line.strip())
            if ref_match:
                ref_id = ref_match.group(1).lower()
                ref_url = ref_match.group(2).strip()
                self._reference_links[ref_id] = ref_url
                i += 1
                continue

            # 각주 정의: [^1]: note
            footnote_match = re.match(r'^\[\^([^\]]+)\]:\s*(.+)$', line.strip())
            if footnote_match:
                # 각주는 문서 끝에 추가하도록 별도 저장
                # (현재는 간단히 제거, 추후 구현 시 확장 가능)
                i += 1
                continue

            processed_lines.append(line)
            i += 1

        self.content = '\n'.join(processed_lines)

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

    def parse_batched(self) -> list[list[dict[str, Any]]]:
        """
        마크다운 파싱 및 단계별 요청 배치 생성

        insertTable 요청을 기준으로 요청을 분리합니다.
        테이블 삽입 후 인덱스가 변경되므로, 각 배치는 순차적으로 실행해야 합니다.

        Returns:
            list[list]: 순차적으로 실행할 요청 배치 리스트
        """
        # 먼저 전체 요청 생성
        self.parse()

        # insertTable 요청을 기준으로 분리
        batches = []
        current_batch = []

        for req in self.requests:
            if 'insertTable' in req:
                # 현재 배치 저장 (비어있지 않으면)
                if current_batch:
                    batches.append(current_batch)
                    current_batch = []

                # insertTable은 단독 배치로
                batches.append([req])
            else:
                current_batch.append(req)

        # 마지막 배치 저장
        if current_batch:
            batches.append(current_batch)

        return batches

    def _parse_inline_formatting(self, text: str) -> InlineParseResult:
        """인라인 포맷팅 파싱 (볼드, 이탤릭, 코드, 링크)"""
        segments: list[TextSegment] = []
        plain_text = ""

        # 참조 링크 치환 [text][ref] → [text](url)
        def replace_ref_link(match):
            text_part = match.group(1)
            ref_part = match.group(2) if match.group(2) else text_part
            ref_url = self._reference_links.get(ref_part.lower(), '')
            if ref_url:
                return f'[{text_part}]({ref_url})'
            return match.group(0)  # 참조 못 찾으면 원본 유지

        # 참조 링크 패턴: [text][ref] 또는 [text][]
        text = re.sub(r'\[([^\]]+)\]\[([^\]]*)\]', replace_ref_link, text)

        # 정규식 패턴들 (순서 중요 - 긴 패턴 먼저)
        patterns = [
            (r'\[([^\]]+)\]\(([^)]+)\)', 'link'),      # [text](url)
            # 중첩 포맷 (bold + italic)
            (r'\*\*\*(.+?)\*\*\*', 'bold_italic'),     # ***bold italic***
            (r'___(.+?)___', 'bold_italic'),          # ___bold italic___
            (r'\*\*_(.+?)_\*\*', 'bold_italic'),      # **_bold italic_**
            (r'__\*(.+?)\*__', 'bold_italic'),        # __*bold italic*__
            (r'\*__(.+?)__\*', 'bold_italic'),        # *__bold italic__*
            (r'_\*\*(.+?)\*\*_', 'bold_italic'),      # _**bold italic**_
            # 단일 포맷
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
            elif style == 'bold_italic':
                segment.bold = True
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
        """인라인 스타일이 적용된 단락 추가 (Premium Dark Text 스타일)"""
        result = self._parse_inline_formatting(text)

        # 전체 텍스트 먼저 삽입
        full_text = ''.join(seg.text for seg in result.segments)
        start = self._add_text(full_text)

        # Premium Dark Text 스타일 사용
        if self.style and self.use_premium_style:
            body_config = self.style.typography.get('body', {})
            color_name = body_config.get('color', 'text_primary')
            color = self.style.get_color(color_name)
            line_height = body_config.get('line_height', 1.65) * 100
            space_after = body_config.get('space_after', 10)
            font_size = body_config.get('size', 11)

            # NORMAL_TEXT Named Style + 커스텀 스타일
            self.requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': self.current_index - 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'NORMAL_TEXT',
                        'lineSpacing': line_height,
                        'spaceBelow': {'magnitude': space_after, 'unit': 'PT'}
                    },
                    'fields': 'namedStyleType,lineSpacing,spaceBelow'
                }
            })

            # 본문 색상 적용
            self.requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': self.current_index - 1
                    },
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': color}},
                        'fontSize': {'magnitude': font_size, 'unit': 'PT'},
                    },
                    'fields': 'foregroundColor,fontSize'
                }
            })
        else:
            # 기본 스타일 (레거시)
            self.requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': self.current_index - 1
                    },
                    'paragraphStyle': {
                        'lineSpacing': 115,  # 115% 줄간격 (SKILL.md 표준)
                        'spaceBelow': {'magnitude': 0, 'unit': 'PT'}  # 0pt (줄바꿈 최소화)
                    },
                    'fields': 'lineSpacing,spaceBelow'
                }
            })

        # 각 세그먼트에 스타일 적용
        current_pos = start
        for segment in result.segments:
            end_pos = current_pos + len(segment.text)
            self._apply_segment_style(segment, current_pos, end_pos)
            current_pos = end_pos

    def _add_heading(self, text: str, level: int):
        """제목 추가 (Premium Dark Text 스타일 적용)"""
        # 목차용 헤딩 수집
        self.headings.append({'text': text, 'level': level, 'index': self.current_index})

        start = self._add_text(text)

        # Premium Dark Text 스타일 사용
        if self.style and self.use_premium_style:
            heading_config = self.style.get_heading_style(level)
            color_name = heading_config.get('color', 'heading_primary')
            color = self.style.get_color(color_name)

            space_before = heading_config.get('space_before', 24)
            space_after = heading_config.get('space_after', 8)
            font_size = heading_config.get('size', 16)
            font_weight = heading_config.get('weight', 600)
            line_height = heading_config.get('line_height', 1.3) * 100

            # 제목 스타일 적용 (Named Style + Custom)
            heading_style = f'HEADING_{min(level, 6)}'
            self.requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': self.current_index - 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': heading_style,
                        'spaceAbove': {'magnitude': space_before, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': space_after, 'unit': 'PT'},
                        'lineSpacing': line_height,
                    },
                    'fields': 'namedStyleType,spaceAbove,spaceBelow,lineSpacing'
                }
            })

            # 색상 및 폰트 스타일 적용
            self.requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': self.current_index - 1
                    },
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': color}},
                        'fontSize': {'magnitude': font_size, 'unit': 'PT'},
                        'bold': font_weight >= 600,
                    },
                    'fields': 'foregroundColor,fontSize,bold'
                }
            })

            # H1 하단 구분선 적용 (SKILL.md 2.3 표준)
            if level == 1 and heading_config.get('border_bottom'):
                border_style = self.style.get_h1_border_style()
                self.requests.append({
                    'updateParagraphStyle': {
                        'range': {
                            'startIndex': start,
                            'endIndex': self.current_index
                        },
                        'paragraphStyle': {
                            'borderBottom': border_style
                        },
                        'fields': 'borderBottom'
                    }
                })
        else:
            # 기본 스타일 (레거시)
            space_settings = {
                1: {'before': 48, 'after': 16},
                2: {'before': 36, 'after': 12},
                3: {'before': 28, 'after': 8},
                4: {'before': 20, 'after': 6},
                5: {'before': 16, 'after': 4},
                6: {'before': 12, 'after': 4},
            }
            spacing = space_settings.get(level, {'before': 16, 'after': 8})

            heading_style = f'HEADING_{min(level, 6)}'
            self.requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': self.current_index - 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': heading_style,
                        'spaceAbove': {'magnitude': spacing['before'], 'unit': 'PT'},
                        'spaceBelow': {'magnitude': spacing['after'], 'unit': 'PT'},
                        'lineSpacing': 120,
                    },
                    'fields': 'namedStyleType,spaceAbove,spaceBelow,lineSpacing'
                }
            })

    def _add_table(self, table_lines: list[str]):
        """테이블 추가"""
        if self.use_native_tables:
            self._add_native_table(table_lines)
        else:
            self._add_text_table(table_lines)

    def _add_native_table(self, table_lines: list[str]):
        """네이티브 Google Docs 테이블 추가 (2단계 방식)"""
        table_data = self._table_renderer.parse_markdown_table(table_lines)

        if table_data.column_count == 0:
            return

        # 2단계 처리 (docs_service가 있는 경우)
        if self.docs_service and self.doc_id:
            self._add_native_table_two_phase(table_data)
        else:
            # 레거시 단일 batchUpdate 방식 (실패 가능)
            requests, new_index = self._table_renderer.render(table_data, self.current_index)
            self.requests.extend(requests)
            self.current_index = new_index

    def _add_native_table_two_phase(self, table_data):
        """
        최적화된 2단계 네이티브 테이블 처리 (v2.3.2+)

        API 호출 횟수: 3회 (기존 8회 → 62% 감소)
        1. batchUpdate: 기존 요청 + insertTable
        2. documents.get: 테이블 구조 조회
        3. batchUpdate: 텍스트 + 셀 스타일 + 텍스트 스타일 통합
        """
        # 1단계: 기존 요청 + insertTable 통합 실행
        # 문서 조회하여 현재 끝 인덱스 확인
        doc = self.docs_service.documents().get(documentId=self.doc_id).execute()
        body = doc.get('body', {})
        content = body.get('content', [])
        doc_end_index = content[-1].get('endIndex', 1) if content else 1

        # 테이블 삽입 위치 (문서 끝 - 1)
        table_start_index = doc_end_index - 1

        # 테이블 구조 요청 생성
        structure_request = self._table_renderer.render_table_structure(
            table_data, table_start_index
        )

        # 기존 요청 + insertTable 통합 실행 [API 호출 #1]
        if structure_request:
            combined_requests = self.requests + [structure_request]
            self.docs_service.documents().batchUpdate(
                documentId=self.doc_id,
                body={'requests': combined_requests}
            ).execute()
            self.requests = []

        # 2단계: 문서 재조회하여 실제 테이블 구조 확인 [API 호출 #2]
        doc = self.docs_service.documents().get(documentId=self.doc_id).execute()

        # 마지막 테이블 요소 찾기
        table_element = self._find_last_table(doc)

        if table_element:
            # 3단계: 통합 렌더링 (텍스트 + 셀 스타일 + 텍스트 스타일) [API 호출 #3]
            unified_requests = self._table_renderer.render_table_content_and_styles(
                table_data, table_element
            )
            if unified_requests:
                self.docs_service.documents().batchUpdate(
                    documentId=self.doc_id,
                    body={'requests': unified_requests}
                ).execute()

            # 문서 끝 인덱스 업데이트 (테이블 끝 인덱스 + 여유)
            table_end = self._table_renderer.get_table_end_index(table_element)
            # 텍스트 삽입량 추정
            text_length = sum(
                len(cell) for row in [table_data.headers] + table_data.rows for cell in row
            )
            self.current_index = table_end + text_length
        else:
            # 테이블을 찾지 못한 경우 추정값 사용
            self.current_index = table_start_index + self._estimate_table_size(table_data) - 1

    def _find_last_table(self, doc: dict) -> dict | None:
        """문서에서 마지막 테이블 요소 찾기"""
        body = doc.get('body', {})
        content = body.get('content', [])

        # 뒤에서부터 검색하여 첫 번째 테이블 반환
        for element in reversed(content):
            if 'table' in element:
                return element

        return None

    def _estimate_table_size(self, table_data) -> int:
        """테이블 크기 추정 (폴백용)"""
        size = 1  # 테이블 요소
        row_size = 1 + table_data.column_count * 2
        size += table_data.row_count * row_size

        all_rows = [table_data.headers] + table_data.rows
        for row in all_rows:
            for cell in row:
                size += len(cell)

        return size + 1

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
        """코드 블록 추가 (GitHub 스타일)"""
        block_start = self.current_index

        # 언어 레이블 (있을 경우)
        if lang:
            lang_start = self._add_text(f'📄 {lang.upper()}')
            self.requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': lang_start,
                        'endIndex': self.current_index - 1
                    },
                    'textStyle': {
                        'fontSize': {'magnitude': 9, 'unit': 'PT'},
                        'foregroundColor': {
                            'color': {'rgbColor': {'red': 0.4, 'green': 0.4, 'blue': 0.4}}
                        },
                        'bold': True,
                    },
                    'fields': 'fontSize,foregroundColor,bold'
                }
            })
            self.requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': lang_start,
                        'endIndex': self.current_index - 1
                    },
                    'paragraphStyle': {
                        'spaceBelow': {'magnitude': 0, 'unit': 'PT'},  # 0pt (언어 레이블과 코드 밀착)
                    },
                    'fields': 'spaceBelow'
                }
            })

        # 코드 내용
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
                    'fontSize': {'magnitude': 11, 'unit': 'PT'},
                    'foregroundColor': {
                        'color': {'rgbColor': {'red': 0.15, 'green': 0.15, 'blue': 0.15}}
                    },
                    'backgroundColor': {
                        'color': {'rgbColor': {
                            'red': self.code_bg_color[0],
                            'green': self.code_bg_color[1],
                            'blue': self.code_bg_color[2]
                        }}
                    }
                },
                'fields': 'weightedFontFamily,fontSize,foregroundColor,backgroundColor'
            }
        })

        # 코드 블록 단락 스타일 (들여쓰기, 줄간격)
        self.requests.append({
            'updateParagraphStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': self.current_index - 1
                },
                'paragraphStyle': {
                    'indentStart': {'magnitude': 16, 'unit': 'PT'},
                    'indentEnd': {'magnitude': 16, 'unit': 'PT'},
                    'lineSpacing': 140,
                    'spaceAbove': {'magnitude': 8, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 12, 'unit': 'PT'},
                },
                'fields': 'indentStart,indentEnd,lineSpacing,spaceAbove,spaceBelow'
            }
        })

    def _add_bullet_item(self, text: str):
        """불릿 리스트 아이템 추가 (Premium Dark Text 스타일)"""
        result = self._parse_inline_formatting(text)
        full_text = ''.join(seg.text for seg in result.segments)

        start = self._add_text(f"• {full_text}")

        # Premium Dark Text 스타일 적용
        if self.style and self.use_premium_style:
            list_config = self.style.typography.get('list', {})
            color_name = list_config.get('color', 'text_primary')
            color = self.style.get_color(color_name)
            line_height = list_config.get('line_height', 1.55) * 100
            font_size = list_config.get('size', 11)
            indent = list_config.get('indent', 20)

            # 단락 스타일
            self.requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': self.current_index - 1
                    },
                    'paragraphStyle': {
                        'namedStyleType': 'NORMAL_TEXT',
                        'lineSpacing': line_height,
                        'indentStart': {'magnitude': indent, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 0, 'unit': 'PT'},  # 0pt (줄바꿈 최소화)
                    },
                    'fields': 'namedStyleType,lineSpacing,indentStart,spaceBelow'
                }
            })

            # 텍스트 스타일
            self.requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': self.current_index - 1
                    },
                    'textStyle': {
                        'foregroundColor': {'color': {'rgbColor': color}},
                        'fontSize': {'magnitude': font_size, 'unit': 'PT'},
                    },
                    'fields': 'foregroundColor,fontSize'
                }
            })

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
        """수평선 추가 (SKILL.md 2.3 표준: ─ 반복 금지, 하단 구분선 사용)"""
        # 빈 단락 삽입 후 하단에 얇은 구분선 추가
        start = self._add_text(' ')

        if self.style and self.use_premium_style:
            divider_color = self.style.get_color('divider')

            # 여백 + 하단 구분선 (SKILL.md 2.3 표준)
            self.requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': start,
                        'endIndex': self.current_index
                    },
                    'paragraphStyle': {
                        'spaceAbove': {'magnitude': 12, 'unit': 'PT'},
                        'spaceBelow': {'magnitude': 12, 'unit': 'PT'},
                        'borderBottom': {
                            'color': {'color': {'rgbColor': divider_color}},
                            'width': {'magnitude': 0.5, 'unit': 'PT'},
                            'padding': {'magnitude': 8, 'unit': 'PT'},
                            'dashStyle': 'SOLID'
                        }
                    },
                    'fields': 'spaceAbove,spaceBelow,borderBottom'
                }
            })

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
    use_native_tables: bool = True,
    apply_page_style: bool = True,
) -> str:
    """
    Google Docs 문서 생성

    Args:
        title: 문서 제목
        content: 마크다운 콘텐츠
        folder_id: Google Drive 폴더 ID (None이면 기본 폴더)
        include_toc: 목차 포함 여부
        use_native_tables: 네이티브 테이블 사용 여부 (2단계 처리로 안정적)
        apply_page_style: 페이지 스타일 적용 여부 (A4, 72pt 여백, 115% 줄간격)

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
        print("     폴더로 이동됨")
    except Exception as e:
        print(f"     폴더 이동 실패: {e}")

    # 3. 페이지 스타일 적용 (A4, 72pt 여백) - SKILL.md 전역 표준
    if apply_page_style:
        try:
            style = NotionStyle.default()
            page_style_request = style.get_page_style_request()
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': [page_style_request]}
            ).execute()
            print("     페이지 스타일 적용됨 (A4, 72pt 여백)")
        except Exception as e:
            print(f"     페이지 스타일 적용 실패: {e}")

    # 4. 콘텐츠 변환 및 추가 (2단계 테이블 처리 지원)
    converter = MarkdownToDocsConverter(
        content,
        include_toc=include_toc,
        use_native_tables=use_native_tables,
        docs_service=docs_service if use_native_tables else None,
        doc_id=doc_id if use_native_tables else None,
    )
    requests = converter.parse()

    # 남은 요청들 실행 (테이블 처리 중 일부 요청이 이미 실행되었을 수 있음)
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
    else:
        print("     콘텐츠 추가됨 (테이블 포함)")

    # 5. 전체 문서 줄간격 적용 (115%)
    if apply_page_style:
        try:
            doc = docs_service.documents().get(documentId=doc_id).execute()
            end_index = max(el.get("endIndex", 1) for el in doc["body"]["content"])

            if end_index > 2:
                docs_service.documents().batchUpdate(
                    documentId=doc_id,
                    body={'requests': [{
                        "updateParagraphStyle": {
                            "range": {"startIndex": 1, "endIndex": end_index - 1},
                            "paragraphStyle": {
                                "lineSpacing": 115,
                            },
                            "fields": "lineSpacing"
                        }
                    }]}
                ).execute()
                print("     줄간격 적용됨 (115%)")
        except Exception as e:
            print(f"     줄간격 적용 실패: {e}")

    # 6. 문서 URL 반환
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_url
