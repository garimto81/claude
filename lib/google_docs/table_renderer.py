"""
네이티브 Google Docs 테이블 렌더러

마크다운 테이블을 Google Docs API의 insertTable을 사용하여
실제 테이블로 변환합니다.

2단계 렌더링 방식:
1. 테이블 구조 생성 (insertTable)
2. 문서 재조회 후 텍스트/스타일 삽입
"""

import re
from dataclasses import dataclass, field
from typing import Any

from .models import TableData


@dataclass
class CellInlineStyle:
    """셀 내 인라인 스타일 정보"""
    start: int  # 셀 내 상대 위치
    end: int
    bold: bool = False
    italic: bool = False
    code: bool = False


@dataclass
class ParsedCellContent:
    """파싱된 셀 내용"""
    plain_text: str  # 마크다운 기호 제거된 텍스트
    styles: list[CellInlineStyle] = field(default_factory=list)


class NativeTableRenderer:
    """마크다운 테이블을 Google Docs 네이티브 테이블로 변환 (2단계 방식)"""

    # SKILL.md 2.3 표준 테이블 스타일
    BODY_COLOR = {'red': 0.25, 'green': 0.25, 'blue': 0.25}  # #404040
    HEADER_BG_COLOR = {'red': 0.90, 'green': 0.90, 'blue': 0.90}  # #E6E6E6
    BORDER_COLOR = {'red': 0.80, 'green': 0.80, 'blue': 0.80}  # #CCCCCC
    CODE_BG_COLOR = {'red': 0.949, 'green': 0.949, 'blue': 0.949}  # #F2F2F2
    CELL_PADDING_PT = 5  # 5pt 패딩

    def _parse_cell_inline_formatting(self, text: str) -> ParsedCellContent:
        """
        셀 내용에서 인라인 마크다운 파싱

        **bold**, *italic*, `code` 등을 추출하고 plain text 반환
        """
        styles: list[CellInlineStyle] = []

        # 정규식 패턴들 (순서 중요 - 긴 패턴 먼저)
        patterns = [
            # 중첩 포맷 (bold + italic)
            (r'\*\*\*(.+?)\*\*\*', 'bold_italic'),     # ***bold italic***
            (r'___(.+?)___', 'bold_italic'),          # ___bold italic___
            (r'\*\*_(.+?)_\*\*', 'bold_italic'),      # **_bold italic_**
            (r'__\*(.+?)\*__', 'bold_italic'),        # __*bold italic*__
            (r'\*__(.+?)__\*', 'bold_italic'),        # *__bold italic__*
            (r'_\*\*(.+?)\*\*_', 'bold_italic'),      # _**bold italic**_
            # 단일 포맷
            (r'\*\*(.+?)\*\*', 'bold'),      # **bold**
            (r'__(.+?)__', 'bold'),          # __bold__
            (r'\*(.+?)\*', 'italic'),        # *italic*
            (r'_(.+?)_', 'italic'),          # _italic_
            (r'`([^`]+)`', 'code'),          # `code`
        ]

        # 모든 매치 찾기
        all_matches = []
        for pattern, style in patterns:
            for match in re.finditer(pattern, text):
                all_matches.append((match.start(), match.end(), match.group(1), style))

        # 위치순 정렬
        all_matches.sort(key=lambda x: x[0])

        # 겹치는 매치 제거
        filtered_matches = []
        last_end = 0
        for match in all_matches:
            if match[0] >= last_end:
                filtered_matches.append(match)
                last_end = match[1]

        # plain text 생성 및 스타일 정보 수집
        plain_parts = []
        current_pos = 0
        plain_offset = 0

        for start, end, content, style in filtered_matches:
            # 이전 일반 텍스트
            if start > current_pos:
                plain_parts.append(text[current_pos:start])
                plain_offset += start - current_pos

            # 스타일 정보 저장 (plain text 기준 위치)
            style_info = CellInlineStyle(
                start=plain_offset,
                end=plain_offset + len(content),
                bold=(style == 'bold' or style == 'bold_italic'),
                italic=(style == 'italic' or style == 'bold_italic'),
                code=(style == 'code'),
            )
            styles.append(style_info)

            plain_parts.append(content)
            plain_offset += len(content)
            current_pos = end

        # 남은 텍스트
        if current_pos < len(text):
            plain_parts.append(text[current_pos:])

        plain_text = ''.join(plain_parts)

        return ParsedCellContent(plain_text=plain_text, styles=styles)

    def parse_markdown_table(self, table_lines: list[str]) -> TableData:
        """
        마크다운 테이블 라인을 TableData로 파싱

        Args:
            table_lines: 테이블 마크다운 라인들

        Returns:
            TableData: 파싱된 테이블 데이터
        """
        headers = []
        rows = []
        alignments = []

        for i, line in enumerate(table_lines):
            line = line.strip()
            if not line:
                continue

            # 구분선 (---) 처리 - 정렬 정보 추출
            if '---' in line or ':-' in line or '-:' in line:
                cells = [c.strip() for c in line.strip('|').split('|')]
                for cell in cells:
                    cell = cell.strip()
                    if cell.startswith(':') and cell.endswith(':'):
                        alignments.append('center')
                    elif cell.endswith(':'):
                        alignments.append('right')
                    else:
                        alignments.append('left')
                continue

            # 일반 행 처리
            cells = [c.strip() for c in line.strip('|').split('|')]
            cells = [c for c in cells if c or cells.index(c) not in [0, len(cells)-1]]

            if not headers:
                headers = cells
            else:
                rows.append(cells)

        # 열 수 정규화
        column_count = len(headers) if headers else 0
        if column_count == 0:
            return TableData(
                headers=[],
                rows=[],
                column_count=0,
                row_count=0,
                column_alignments=[]
            )

        # 행 데이터 정규화 (열 수 맞추기)
        normalized_rows = []
        for row in rows:
            if len(row) < column_count:
                row.extend([''] * (column_count - len(row)))
            elif len(row) > column_count:
                row = row[:column_count]
            normalized_rows.append(row)

        # 정렬 정보 정규화
        if len(alignments) < column_count:
            alignments.extend(['left'] * (column_count - len(alignments)))

        return TableData(
            headers=headers,
            rows=normalized_rows,
            column_count=column_count,
            row_count=len(normalized_rows) + 1,  # 헤더 포함
            column_alignments=alignments[:column_count]
        )

    def render_table_structure(
        self,
        table_data: TableData,
        start_index: int,
    ) -> dict[str, Any] | None:
        """
        1단계: 테이블 구조만 생성하는 요청 반환

        Args:
            table_data: 파싱된 테이블 데이터
            start_index: 테이블 삽입 시작 인덱스

        Returns:
            dict: insertTable 요청 또는 None
        """
        if table_data.column_count == 0 or table_data.row_count == 0:
            return None

        return {
            'insertTable': {
                'rows': table_data.row_count,
                'columns': table_data.column_count,
                'location': {'index': start_index}
            }
        }

    def render_table_content(
        self,
        table_data: TableData,
        table_element: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        2단계: 실제 테이블 구조를 기반으로 텍스트/스타일 요청 생성

        Args:
            table_data: 파싱된 테이블 데이터
            table_element: Google Docs에서 조회한 실제 테이블 구조

        Returns:
            list: insertText 및 updateTextStyle 요청 리스트
        """
        requests = []

        # 테이블 구조에서 각 셀의 실제 인덱스 추출
        cell_indices = self._extract_cell_indices(table_element)

        if not cell_indices:
            return requests

        # 모든 행 데이터 수집
        all_rows = [table_data.headers] + table_data.rows

        # 셀 내용 파싱 및 삽입 준비 (역순으로 - 인덱스 시프트 방지)
        insertions = []
        for row_idx, row in enumerate(all_rows):
            for col_idx, content in enumerate(row):
                if content and row_idx < len(cell_indices) and col_idx < len(cell_indices[row_idx]):
                    cell_start = cell_indices[row_idx][col_idx]

                    # 마크다운 파싱 (** 제거, 스타일 정보 추출)
                    parsed = self._parse_cell_inline_formatting(content)

                    insertions.append({
                        'index': cell_start,
                        'content': parsed.plain_text,  # 마크다운 기호 제거된 텍스트
                        'original': content,
                        'styles': parsed.styles,       # 인라인 스타일 정보
                        'row_idx': row_idx,
                        'col_idx': col_idx,
                    })

        # 역순 정렬 (뒤에서부터 삽입)
        insertions.sort(key=lambda x: x['index'], reverse=True)

        # 텍스트 삽입 요청
        for item in insertions:
            requests.append({
                'insertText': {
                    'location': {'index': item['index']},
                    'text': item['content']
                }
            })

        # 스타일 적용 (텍스트 삽입 후)
        # 주의: insertText 요청들이 먼저 실행된 후에 스타일이 적용됨

        # 테이블 시작 인덱스 (셀 스타일 적용용)
        table_start_index = table_element.get('startIndex', 0)

        # 1. 테이블 전체 셀 스타일 적용 (테두리, 패딩) - SKILL.md 2.3 표준
        table = table_element.get('table', {})
        table_rows = table.get('tableRows', [])
        for row_idx, row in enumerate(table_rows):
            cells = row.get('tableCells', [])
            for col_idx, cell in enumerate(cells):
                # 테두리 스타일 정의 (SKILL.md 2.3 표준: 1pt, #CCCCCC)
                border_style = {
                    'color': {'color': {'rgbColor': self.BORDER_COLOR}},
                    'width': {'magnitude': 1, 'unit': 'PT'},
                    'dashStyle': 'SOLID',
                }

                # 셀 스타일 요청 생성
                cell_style: dict[str, Any] = {
                    # 패딩 5pt (SKILL.md 표준)
                    'contentAlignment': 'TOP',
                    'paddingTop': {'magnitude': self.CELL_PADDING_PT, 'unit': 'PT'},
                    'paddingBottom': {'magnitude': self.CELL_PADDING_PT, 'unit': 'PT'},
                    'paddingLeft': {'magnitude': self.CELL_PADDING_PT, 'unit': 'PT'},
                    'paddingRight': {'magnitude': self.CELL_PADDING_PT, 'unit': 'PT'},
                    # 테두리 (SKILL.md 표준: 1pt, #CCCCCC)
                    'borderTop': border_style,
                    'borderBottom': border_style,
                    'borderLeft': border_style,
                    'borderRight': border_style,
                }

                # 헤더 행 배경색 (SKILL.md 표준: #E6E6E6)
                if row_idx == 0:
                    cell_style['backgroundColor'] = {
                        'color': {'rgbColor': self.HEADER_BG_COLOR}
                    }

                requests.append({
                    'updateTableCellStyle': {
                        'tableRange': {
                            'tableCellLocation': {
                                'tableStartLocation': {'index': table_start_index},
                                'rowIndex': row_idx,
                                'columnIndex': col_idx,
                            },
                            'rowSpan': 1,
                            'columnSpan': 1,
                        },
                        'tableCellStyle': cell_style,
                        'fields': 'contentAlignment,paddingTop,paddingBottom,paddingLeft,paddingRight,borderTop,borderBottom,borderLeft,borderRight,backgroundColor'
                    }
                })

        # NOTE: 텍스트 스타일은 render_table_text_styles()에서 별도 처리
        # (인덱스 시프트 문제 방지를 위해 별도 batchUpdate 필요)

        return requests

    def render_table_text_styles(
        self,
        table_data: TableData,
        table_element: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        3단계: 텍스트 삽입 후 텍스트 스타일 적용

        insertText 실행 후 문서를 재조회한 뒤 호출해야 합니다.
        이렇게 분리하면 인덱스 시프트 문제가 해결됩니다.

        Args:
            table_data: 파싱된 테이블 데이터
            table_element: 텍스트 삽입 후 재조회한 테이블 구조

        Returns:
            list: updateTextStyle 요청 리스트
        """
        requests = []

        # 테이블 구조에서 각 셀의 실제 인덱스 추출 (삽입 후 새 인덱스)
        cell_indices = self._extract_cell_indices(table_element)

        if not cell_indices:
            return requests

        # 모든 행 데이터 수집
        all_rows = [table_data.headers] + table_data.rows

        for row_idx, row in enumerate(all_rows):
            for col_idx, content in enumerate(row):
                if content and row_idx < len(cell_indices) and col_idx < len(cell_indices[row_idx]):
                    cell_start = cell_indices[row_idx][col_idx]

                    # 마크다운 파싱
                    parsed = self._parse_cell_inline_formatting(content)
                    plain_text = parsed.plain_text

                    if not plain_text:
                        continue

                    # 셀 스타일: 본문 색상만 (볼드는 마크다운 **...** 문법으로만 적용)
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': cell_start,
                                'endIndex': cell_start + len(plain_text)
                            },
                            'textStyle': {
                                'foregroundColor': {'color': {'rgbColor': self.BODY_COLOR}}
                            },
                            'fields': 'foregroundColor'
                        }
                    })

                    # 마크다운 인라인 스타일 적용 (**볼드**, *이탤릭*, `코드`)
                    for style in parsed.styles:
                        style_fields = []
                        inline_style: dict[str, Any] = {}

                        if style.bold:
                            inline_style['bold'] = True
                            style_fields.append('bold')

                        if style.italic:
                            inline_style['italic'] = True
                            style_fields.append('italic')

                        if style.code:
                            inline_style['weightedFontFamily'] = {
                                'fontFamily': 'Consolas',
                                'weight': 400
                            }
                            inline_style['backgroundColor'] = {
                                'color': {'rgbColor': self.CODE_BG_COLOR}
                            }
                            style_fields.extend(['weightedFontFamily', 'backgroundColor'])

                        if style_fields:
                            requests.append({
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': cell_start + style.start,
                                        'endIndex': cell_start + style.end
                                    },
                                    'textStyle': inline_style,
                                    'fields': ','.join(style_fields)
                                }
                            })

        return requests

    # =========================================================================
    # 최적화된 통합 렌더링 (v2.3.2+)
    # =========================================================================

    def render_table_content_and_styles(
        self,
        table_data: TableData,
        table_element: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        최적화된 2단계 통합 렌더링: 텍스트 삽입 + 셀 스타일 + 텍스트 스타일

        기존 render_table_content() + render_table_text_styles() 통합 버전.
        단일 batchUpdate로 모든 작업을 처리하여 API 호출을 최소화합니다.

        Args:
            table_data: 파싱된 테이블 데이터
            table_element: Google Docs에서 조회한 실제 테이블 구조

        Returns:
            list: 통합된 API 요청 리스트 (insertText + updateTableCellStyle + updateTextStyle)
        """
        requests: list[dict[str, Any]] = []

        # 테이블 구조에서 각 셀의 실제 인덱스 추출
        cell_indices = self._extract_cell_indices(table_element)

        if not cell_indices:
            return requests

        # 모든 행 데이터 수집
        all_rows = [table_data.headers] + table_data.rows

        # =====================================================================
        # Phase 1: 텍스트 삽입 정보 수집 및 역순 삽입
        # =====================================================================
        insertions: list[dict[str, Any]] = []

        for row_idx, row in enumerate(all_rows):
            for col_idx, content in enumerate(row):
                if content and row_idx < len(cell_indices) and col_idx < len(cell_indices[row_idx]):
                    cell_start = cell_indices[row_idx][col_idx]

                    # 마크다운 파싱 (** 제거, 스타일 정보 추출)
                    parsed = self._parse_cell_inline_formatting(content)

                    insertions.append({
                        'index': cell_start,
                        'content': parsed.plain_text,
                        'parsed': parsed,
                        'row_idx': row_idx,
                        'col_idx': col_idx,
                    })

        # 역순 정렬 (뒤에서부터 삽입 - 인덱스 시프트 방지)
        insertions.sort(key=lambda x: x['index'], reverse=True)

        # 텍스트 삽입 요청
        for item in insertions:
            if item['content']:
                requests.append({
                    'insertText': {
                        'location': {'index': item['index']},
                        'text': item['content']
                    }
                })

        # =====================================================================
        # Phase 2: 셀 스타일 적용 (테두리, 패딩, 헤더 배경)
        # =====================================================================
        table_start_index = table_element.get('startIndex', 0)
        table = table_element.get('table', {})
        table_rows = table.get('tableRows', [])

        for row_idx, row in enumerate(table_rows):
            cells = row.get('tableCells', [])
            for col_idx, cell in enumerate(cells):
                # 테두리 스타일 정의 (SKILL.md 2.3 표준: 1pt, #CCCCCC)
                border_style = {
                    'color': {'color': {'rgbColor': self.BORDER_COLOR}},
                    'width': {'magnitude': 1, 'unit': 'PT'},
                    'dashStyle': 'SOLID',
                }

                # 셀 스타일 요청 생성
                cell_style: dict[str, Any] = {
                    'contentAlignment': 'TOP',
                    'paddingTop': {'magnitude': self.CELL_PADDING_PT, 'unit': 'PT'},
                    'paddingBottom': {'magnitude': self.CELL_PADDING_PT, 'unit': 'PT'},
                    'paddingLeft': {'magnitude': self.CELL_PADDING_PT, 'unit': 'PT'},
                    'paddingRight': {'magnitude': self.CELL_PADDING_PT, 'unit': 'PT'},
                    'borderTop': border_style,
                    'borderBottom': border_style,
                    'borderLeft': border_style,
                    'borderRight': border_style,
                }

                # 헤더 행 배경색 (SKILL.md 표준: #E6E6E6)
                if row_idx == 0:
                    cell_style['backgroundColor'] = {
                        'color': {'rgbColor': self.HEADER_BG_COLOR}
                    }

                requests.append({
                    'updateTableCellStyle': {
                        'tableRange': {
                            'tableCellLocation': {
                                'tableStartLocation': {'index': table_start_index},
                                'rowIndex': row_idx,
                                'columnIndex': col_idx,
                            },
                            'rowSpan': 1,
                            'columnSpan': 1,
                        },
                        'tableCellStyle': cell_style,
                        'fields': 'contentAlignment,paddingTop,paddingBottom,paddingLeft,paddingRight,borderTop,borderBottom,borderLeft,borderRight,backgroundColor'
                    }
                })

        # =====================================================================
        # Phase 3: 텍스트 스타일 적용 (본문 색상 + 인라인 마크다운)
        # 주의: insertText 후 인덱스가 변경되므로 시프트 계산 필요
        # =====================================================================

        # 인덱스 시프트 계산 (역순 삽입으로 인한 누적 오프셋)
        # 역순 삽입이므로, 각 셀의 원래 인덱스 이후에 삽입된 텍스트 길이만큼 시프트
        index_shifts = self._calculate_index_shifts(insertions)

        for item in insertions:
            if not item['content']:
                continue

            original_index = item['index']
            shift = index_shifts.get(original_index, 0)
            shifted_start = original_index + shift
            parsed = item['parsed']
            plain_text = parsed.plain_text
            is_header = item['row_idx'] == 0

            # 셀 전체에 본문 색상 적용
            text_style: dict[str, Any] = {
                'foregroundColor': {
                    'color': {'rgbColor': self.BODY_COLOR}
                }
            }
            fields = ['foregroundColor']

            # 헤더 행은 볼드 추가
            if is_header:
                text_style['bold'] = True
                fields.append('bold')

            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': shifted_start,
                        'endIndex': shifted_start + len(plain_text)
                    },
                    'textStyle': text_style,
                    'fields': ','.join(fields)
                }
            })

            # 인라인 스타일 적용 (**볼드**, *이탤릭*, `코드`)
            for style in parsed.styles:
                style_fields: list[str] = []
                inline_style: dict[str, Any] = {}

                if style.bold:
                    inline_style['bold'] = True
                    style_fields.append('bold')

                if style.italic:
                    inline_style['italic'] = True
                    style_fields.append('italic')

                if style.code:
                    inline_style['weightedFontFamily'] = {
                        'fontFamily': 'Consolas',
                        'weight': 400
                    }
                    inline_style['backgroundColor'] = {
                        'color': {'rgbColor': self.CODE_BG_COLOR}
                    }
                    style_fields.extend(['weightedFontFamily', 'backgroundColor'])

                if style_fields:
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': shifted_start + style.start,
                                'endIndex': shifted_start + style.end
                            },
                            'textStyle': inline_style,
                            'fields': ','.join(style_fields)
                        }
                    })

        return requests

    def _calculate_index_shifts(
        self,
        insertions: list[dict[str, Any]]
    ) -> dict[int, int]:
        """
        역순 텍스트 삽입으로 인한 인덱스 시프트 계산

        역순 삽입 시, 뒤쪽 인덱스에 삽입된 텍스트는 앞쪽 인덱스에 영향을 주지 않음.
        따라서 각 인덱스는 자신보다 앞에 있는 삽입 텍스트 길이만큼 시프트됨.

        Args:
            insertions: 역순 정렬된 삽입 정보 리스트

        Returns:
            dict: {원래_인덱스: 시프트_량}
        """
        shifts: dict[int, int] = {}

        # 삽입 순서대로 (역순 = 인덱스 큰 것부터) 처리
        # 자신보다 인덱스가 작은 삽입들의 텍스트 길이 합이 시프트량
        for i, item in enumerate(insertions):
            current_index = item['index']
            shift = 0

            # 자신보다 뒤에 있는 항목들 (이미 처리된 = 인덱스 더 큰 것들)은 영향 없음
            # 자신보다 앞에 있는 항목들 (아직 처리 안 됨 = 인덱스 더 작은 것들)의 텍스트 길이 합
            for j in range(i + 1, len(insertions)):
                other = insertions[j]
                if other['index'] < current_index:
                    shift += len(other['content']) if other['content'] else 0

            shifts[current_index] = shift

        return shifts

    def _extract_cell_indices(self, table_element: dict[str, Any]) -> list[list[int]]:
        """
        테이블 요소에서 각 셀의 시작 인덱스 추출

        Args:
            table_element: Google Docs 테이블 구조 요소

        Returns:
            list[list[int]]: 행/열별 셀 시작 인덱스
        """
        cell_indices = []

        table = table_element.get('table')
        if not table:
            return cell_indices

        table_rows = table.get('tableRows', [])
        for row in table_rows:
            row_indices = []
            cells = row.get('tableCells', [])
            for cell in cells:
                # 셀 내 첫 번째 문단의 시작 인덱스
                content = cell.get('content', [])
                if content:
                    first_para = content[0]
                    if 'paragraph' in first_para:
                        para_start = first_para.get('startIndex', 0)
                        row_indices.append(para_start)
            cell_indices.append(row_indices)

        return cell_indices

    def get_table_end_index(self, table_element: dict[str, Any]) -> int:
        """
        테이블의 끝 인덱스 반환

        Args:
            table_element: Google Docs 테이블 구조 요소

        Returns:
            int: 테이블 끝 인덱스
        """
        return table_element.get('endIndex', 0)

    # =========================================================================
    # 레거시 메서드 (하위 호환성) - v2.4.0에서 제거 예정
    # =========================================================================

    def render(
        self,
        table_data: TableData,
        start_index: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        [DEPRECATED] 단일 batchUpdate용 테이블 렌더링

        .. deprecated:: 2.3.0
            이 메서드는 인덱스 계산 문제로 자주 실패합니다.
            대신 `render_table_structure()` + `render_table_content()`를 사용하세요.
            v2.4.0에서 제거 예정입니다.

        Warning:
            이 메서드는 더 이상 사용하지 마세요.

        Args:
            table_data: 파싱된 테이블 데이터
            start_index: 테이블 삽입 시작 인덱스

        Returns:
            tuple: (API 요청 리스트, 새로운 끝 인덱스)
        """
        import warnings
        warnings.warn(
            "render() is deprecated since v2.3.0 and will be removed in v2.4.0. "
            "Use render_table_structure() + render_table_content() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        if table_data.column_count == 0 or table_data.row_count == 0:
            return [], start_index

        requests = []

        # 1. 빈 테이블 생성
        requests.append({
            'insertTable': {
                'rows': table_data.row_count,
                'columns': table_data.column_count,
                'location': {'index': start_index}
            }
        })

        # 2. 모든 행 데이터 수집 (헤더 + 데이터 행)
        all_rows = [table_data.headers] + table_data.rows

        # 3. 셀 내용 삽입 (역순으로 - 인덱스 시프트 방지)
        cell_insertions = []

        for row_idx in range(len(all_rows)):
            for col_idx in range(table_data.column_count):
                cell_index = self._calc_cell_index(
                    start_index,
                    row_idx,
                    col_idx,
                    table_data.column_count
                )
                content = all_rows[row_idx][col_idx] if col_idx < len(all_rows[row_idx]) else ''

                if content:
                    cell_insertions.append({
                        'row_idx': row_idx,
                        'col_idx': col_idx,
                        'index': cell_index,
                        'content': content,
                        'is_header': row_idx == 0
                    })

        # 역순 정렬 (뒤에서부터 삽입)
        cell_insertions.sort(key=lambda x: x['index'], reverse=True)

        # 텍스트 삽입 요청 생성
        for cell in cell_insertions:
            requests.append({
                'insertText': {
                    'location': {'index': cell['index']},
                    'text': cell['content']
                }
            })

        # 4. 헤더 행 볼드 스타일 적용
        for col_idx in range(table_data.column_count):
            header_content = table_data.headers[col_idx] if col_idx < len(table_data.headers) else ''
            if header_content:
                header_index = self._calc_cell_index(
                    start_index, 0, col_idx, table_data.column_count
                )
                # SKILL.md 표준: 진한 회색 #404040
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': header_index,
                            'endIndex': header_index + len(header_content)
                        },
                        'textStyle': {
                            'bold': True,
                            'foregroundColor': {
                                'color': {'rgbColor': {'red': 0.25, 'green': 0.25, 'blue': 0.25}}
                            }
                        },
                        'fields': 'bold,foregroundColor'
                    }
                })

        # 5. 새로운 끝 인덱스 계산
        new_index = self._calc_table_end_index(start_index, table_data)

        return requests, new_index

    def _calc_cell_index(
        self,
        table_start: int,
        row_idx: int,
        col_idx: int,
        col_count: int,
    ) -> int:
        """
        [레거시] 테이블 셀의 삽입 인덱스 계산 (추정값)

        Google Docs 테이블 구조:
        - 테이블 요소: 1
        - 각 행: 1
        - 각 셀: 2 (셀 요소 + 단락)
        """
        base = table_start + 2
        row_offset = row_idx * (1 + col_count * 2)
        col_offset = col_idx * 2 + 1
        return base + row_offset + col_offset

    def _calc_table_end_index(self, table_start: int, table_data: TableData) -> int:
        """
        [레거시] 테이블 끝 인덱스 계산 (추정값)
        """
        size = 1
        row_size = 1 + table_data.column_count * 2
        size += table_data.row_count * row_size

        all_rows = [table_data.headers] + table_data.rows
        for row in all_rows:
            for cell in row:
                size += len(cell)

        return table_start + size + 1
