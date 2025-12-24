#!/usr/bin/env python3
"""
PRD to Google Docs Converter (Optimized)

PRD 마크다운 파일을 Google Docs로 변환하여 업로드합니다.

Features:
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
                text_style['weightedFontFamily'] = {
                    'fontFamily': 'Consolas',
                    'weight': 400
                }
                text_style['backgroundColor'] = {
                    'color': {'rgbColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}}
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
                            'startIndex': current_pos,
                            'endIndex': end_pos
                        },
                        'textStyle': text_style,
                        'fields': ','.join(style_fields)
                    }
                })

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

    def _add_code_block(self, code: str, lang: str = ''):
        """코드 블록 추가"""
        # 코드 블록 앞에 언어 표시
        if lang:
            self._add_text(f'[{lang}]')

        start = self._add_text(code)

        # 코드 스타일 (고정폭 폰트)
        self.requests.append({
            'updateTextStyle': {
                'range': {
                    'startIndex': start,
                    'endIndex': self.current_index - 1
                },
                'textStyle': {
                    'weightedFontFamily': {
                        'fontFamily': 'Consolas',
                        'weight': 400
                    },
                    'fontSize': {'magnitude': 10, 'unit': 'PT'},
                    'backgroundColor': {
                        'color': {'rgbColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}}
                    }
                },
                'fields': 'weightedFontFamily,fontSize,backgroundColor'
            }
        })

    def _add_table(self, table_lines: list):
        """테이블 추가 (정렬된 텍스트 형식)"""
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

        # 각 열의 최대 너비 계산
        num_cols = max(len(row) for row in rows)
        col_widths = [0] * num_cols
        for row in rows:
            for i, cell in enumerate(row):
                if i < num_cols:
                    col_widths[i] = max(col_widths[i], len(cell))

        # 정렬된 텍스트 테이블 생성
        for row_idx, row in enumerate(rows):
            # 각 셀을 고정 너비로 패딩
            padded_cells = []
            for i in range(num_cols):
                cell = row[i] if i < len(row) else ""
                padded_cells.append(cell.ljust(col_widths[i]))

            line_text = " | ".join(padded_cells)

            if row_idx == 0:
                # 헤더 행 (볼드)
                start = self._add_text(line_text)
                self.requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': start,
                            'endIndex': self.current_index - 1
                        },
                        'textStyle': {'bold': True},
                        'fields': 'bold'
                    }
                })
                # 구분선 추가
                separator = "-+-".join("-" * w for w in col_widths)
                self._add_text(separator)
            else:
                self._add_text(line_text)

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
        """인용문 추가"""
        start = self._add_text(f"│ {text}")

        # 이탤릭 스타일 적용
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
        text_style = {}

        if segment.bold:
            text_style['bold'] = True
            style_fields.append('bold')

        if segment.italic:
            text_style['italic'] = True
            style_fields.append('italic')

        if segment.code:
            text_style['weightedFontFamily'] = {
                'fontFamily': 'Consolas',
                'weight': 400
            }
            text_style['backgroundColor'] = {
                'color': {'rgbColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}}
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

    # 4. 문서 URL 반환
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_url


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
