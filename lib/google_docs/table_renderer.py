"""
네이티브 Google Docs 테이블 렌더러

마크다운 테이블을 Google Docs API의 insertTable을 사용하여
실제 테이블로 변환합니다.
"""

from typing import Any

from .models import TableData


class NativeTableRenderer:
    """마크다운 테이블을 Google Docs 네이티브 테이블로 변환"""

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

    def render(
        self,
        table_data: TableData,
        start_index: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Google Docs API 요청 생성

        Args:
            table_data: 파싱된 테이블 데이터
            start_index: 테이블 삽입 시작 인덱스

        Returns:
            tuple: (API 요청 리스트, 새로운 끝 인덱스)
        """
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
        # Google Docs에서 텍스트 삽입 시 인덱스가 밀리므로
        # 뒤에서부터 삽입해야 앞의 인덱스가 변하지 않음
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
                requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': header_index,
                            'endIndex': header_index + len(header_content)
                        },
                        'textStyle': {'bold': True},
                        'fields': 'bold'
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
        테이블 셀의 삽입 인덱스 계산

        Google Docs 테이블 구조:
        - 테이블 요소: 1
        - 각 행: 1
        - 각 셀: 2 (셀 요소 + 단락)

        공식: table_start + 2 + row_idx * (1 + col_count * 2) + col_idx * 2 + 1

        Args:
            table_start: 테이블 시작 인덱스
            row_idx: 행 인덱스 (0부터)
            col_idx: 열 인덱스 (0부터)
            col_count: 총 열 수

        Returns:
            int: 셀 내 텍스트 삽입 인덱스
        """
        # 테이블 시작 + 테이블 요소(1) + 첫 행 요소(1)
        base = table_start + 2

        # 이전 행들의 크기 (각 행 = 1 + 열수 * 2)
        row_offset = row_idx * (1 + col_count * 2)

        # 현재 행 내 셀 위치 (각 셀 = 2, 단락 위치는 +1)
        col_offset = col_idx * 2 + 1

        return base + row_offset + col_offset

    def _calc_table_end_index(self, table_start: int, table_data: TableData) -> int:
        """
        테이블 끝 인덱스 계산

        테이블 전체 크기:
        - 테이블 요소: 1
        - 각 행: 1 + (열수 * 2)
        - 마지막 줄바꿈: 1

        Args:
            table_start: 테이블 시작 인덱스
            table_data: 테이블 데이터

        Returns:
            int: 테이블 끝 다음 인덱스
        """
        # 테이블 요소
        size = 1

        # 각 행
        row_size = 1 + table_data.column_count * 2
        size += table_data.row_count * row_size

        # 셀 내용 길이 (각 셀의 텍스트 + 줄바꿈)
        all_rows = [table_data.headers] + table_data.rows
        for row in all_rows:
            for cell in row:
                size += len(cell)

        return table_start + size + 1  # +1 for trailing newline
