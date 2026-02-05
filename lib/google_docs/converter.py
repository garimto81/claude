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


def utf16_len(text: str) -> int:
    """
    Google Docs API용 UTF-16 코드 유닛 길이 계산

    Google Docs API는 인덱스를 UTF-16 코드 유닛으로 계산합니다.
    이모지 등 서로게이트 페어 문자는 2개의 코드 유닛을 사용합니다.
    """
    return len(text.encode("utf-16-le")) // 2


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
        base_path: str | None = None,
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
            base_path: 마크다운 파일의 기준 경로 (상대 이미지 경로 해석용)
        """
        self.content = content
        self.base_path = base_path
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
            bg = self.style.get_color("code_bg")
            self.code_bg_color = (bg["red"], bg["green"], bg["blue"])
        else:
            self.code_bg_color = (0.949, 0.949, 0.949)  # #F2F2F2

        self.requests: list[dict[str, Any]] = []
        self.current_index = 1  # Google Docs는 1부터 시작
        self.headings: list[dict[str, Any]] = []
        self._is_first_h1 = True  # First H1 uses TITLE style

        self._table_renderer = NativeTableRenderer()

        # 참조 링크 저장소
        self._reference_links: dict[str, str] = {}

        # 이미지 정보 저장소 (2단계 삽입용)
        # 각 항목: {'index': 삽입위치, 'url': 이미지URL, 'alt': alt텍스트}
        self._pending_images: list[dict[str, Any]] = []

        # YAML frontmatter 제거 및 참조 링크 파싱
        self._preprocess_content()

    def _preprocess_content(self):
        """
        콘텐츠 전처리
        - YAML frontmatter 제거
        - 참조 링크 추출
        - 각주 추출
        - HTML Callout 박스 변환
        """
        lines = self.content.split("\n")
        processed_lines = []
        i = 0

        # 1. YAML frontmatter 제거 (--- ... --- 로 감싸진 부분)
        if lines and lines[0].strip() == "---":
            i = 1
            while i < len(lines) and lines[i].strip() != "---":
                i += 1
            i += 1  # 닫는 --- 건너뛰기

        # 2. 참조 링크 및 각주 추출
        while i < len(lines):
            line = lines[i]

            # 참조 링크: [ref]: url
            ref_match = re.match(r"^\[([^\]]+)\]:\s*(.+)$", line.strip())
            if ref_match:
                ref_id = ref_match.group(1).lower()
                ref_url = ref_match.group(2).strip()
                self._reference_links[ref_id] = ref_url
                i += 1
                continue

            # 각주 정의: [^1]: note
            footnote_match = re.match(r"^\[\^([^\]]+)\]:\s*(.+)$", line.strip())
            if footnote_match:
                # 각주는 문서 끝에 추가하도록 별도 저장
                # (현재는 간단히 제거, 추후 구현 시 확장 가능)
                i += 1
                continue

            processed_lines.append(line)
            i += 1

        self.content = "\n".join(processed_lines)

        # 3. HTML Callout 박스 변환 (<div style="..."> → Markdown Callout)
        self.content = self._convert_html_callouts(self.content)

        # 3. 괄호 안 영문 표기 삭제 (한글 뒤의 영문 설명 제거)
        # 예: "3대 원천 (Three Pillars)" → "3대 원천"
        # 패턴: 한글/숫자 + 공백 + (영문만으로 구성된 괄호)
        self.content = re.sub(
            r'(?<=[가-힣0-9])\s*\([A-Za-z][A-Za-z\s\-\/&\'".,]+\)',
            '',
            self.content
        )

        # 5. HTML 원본 링크 및 텍스트 삭제
        # 예: "[HTML 원본](./mockups/xxx.html)" → 삭제
        # 예: "HTML 원본" 단독 텍스트 → 삭제
        self.content = re.sub(
            r'\[HTML\s*원본\]\([^)]+\)',  # [HTML 원본](링크) 패턴
            '',
            self.content
        )
        self.content = re.sub(
            r'HTML\s*원본',  # "HTML 원본" 단독 텍스트
            '',
            self.content
        )

    def _convert_html_callouts(self, content: str) -> str:
        """
        HTML Callout 박스를 Markdown Callout 형식으로 변환

        지원하는 HTML 패턴:
        - <div style="border:...red..."> → 🚨 경고 (danger)
        - <div style="border:...orange/yellow..."> → ⚠️ 주의 (warning)
        - <div style="border:...green..."> → ✅ 성공 (success)
        - <div style="border:...blue..."> → ℹ️ 정보 (info)
        - <div> (스타일 없음 또는 기타) → 📝 메모 (note)

        Returns:
            변환된 콘텐츠
        """
        def detect_callout_type(style: str) -> tuple[str, str]:
            """스타일에서 Callout 타입 감지"""
            style_lower = style.lower()

            # 색상 기반 타입 감지
            if 'red' in style_lower or '#dc2626' in style_lower or '#f00' in style_lower:
                return '🚨', '경고'
            elif 'orange' in style_lower or '#d97706' in style_lower:
                return '⚠️', '주의'
            elif 'yellow' in style_lower or '#ca8a04' in style_lower:
                return '💡', '팁'
            elif 'green' in style_lower or '#059669' in style_lower:
                return '✅', '성공'
            elif 'blue' in style_lower or '#1a4d8c' in style_lower:
                return 'ℹ️', '정보'
            elif 'purple' in style_lower or '#7c3aed' in style_lower:
                return '🔮', '특수'
            else:
                return '📝', '메모'

        def replace_html_block(match) -> str:
            """HTML 블록을 Markdown Callout으로 변환"""
            full_match = match.group(0)
            style = match.group(1) or ''
            inner_content = match.group(2) or ''

            # 스타일에서 Callout 타입 감지
            emoji, label = detect_callout_type(style)

            # 내부 HTML 태그 정리
            # <p>, <br>, <span> 등 제거하고 텍스트만 추출
            cleaned = re.sub(r'<br\s*/?>', '\n', inner_content)  # <br> → 줄바꿈
            cleaned = re.sub(r'</?p[^>]*>', '\n', cleaned)  # <p> → 줄바꿈
            cleaned = re.sub(r'</?span[^>]*>', '', cleaned)  # <span> 제거
            cleaned = re.sub(r'</?strong[^>]*>', '**', cleaned)  # <strong> → **
            cleaned = re.sub(r'</?b[^>]*>', '**', cleaned)  # <b> → **
            cleaned = re.sub(r'</?em[^>]*>', '*', cleaned)  # <em> → *
            cleaned = re.sub(r'</?i[^>]*>', '*', cleaned)  # <i> → *
            cleaned = re.sub(r'</?code[^>]*>', '`', cleaned)  # <code> → `
            cleaned = re.sub(r'<[^>]+>', '', cleaned)  # 나머지 태그 제거

            # 공백 정리
            cleaned = re.sub(r'\n\s*\n+', '\n', cleaned)  # 여러 빈 줄 → 한 줄
            cleaned = cleaned.strip()

            # 여러 줄인 경우 각 줄을 blockquote로
            lines = cleaned.split('\n')
            result_lines = []

            # 첫 줄에 아이콘 + 라벨 추가
            if lines:
                first_line = lines[0].strip()
                # 이미 "경고:", "주의:" 등이 있으면 아이콘만 추가
                if first_line.startswith(('경고', '주의', '정보', '팁', '성공', '메모')):
                    result_lines.append(f"> {emoji} **{first_line}**")
                else:
                    result_lines.append(f"> {emoji} **{label}**: {first_line}")

                # 나머지 줄
                for line in lines[1:]:
                    line = line.strip()
                    if line:
                        result_lines.append(f"> {line}")

            return '\n'.join(result_lines) + '\n'

        # HTML div 블록 패턴 (멀티라인, non-greedy)
        # <div style="...">...</div> 또는 <div>...</div>
        pattern = r'<div(?:\s+style="([^"]*)")?[^>]*>(.*?)</div>'
        content = re.sub(pattern, replace_html_block, content, flags=re.DOTALL | re.IGNORECASE)

        return content

    def parse(self) -> list[dict[str, Any]]:
        """
        마크다운 파싱 및 Google Docs API 요청 생성

        Returns:
            list: batchUpdate에 전달할 요청 리스트
        """
        lines = self.content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # 코드 블록 처리
            if line.startswith("```"):
                code_lines = []
                lang = line[3:].strip()
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                self._add_code_block("\n".join(code_lines), lang)
                i += 1
                continue

            # 제목 처리
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                text = line.lstrip("#").strip()
                if text:
                    self._add_heading(text, level)
                i += 1
                continue

            # 테이블 처리
            if (
                "|" in line
                and i + 1 < len(lines)
                and ("---" in lines[i + 1] or ":-" in lines[i + 1])
            ):
                table_lines = []
                while i < len(lines) and "|" in lines[i]:
                    table_lines.append(lines[i])
                    i += 1
                self._add_table(table_lines)
                continue

            # 체크리스트 처리
            if (
                line.strip().startswith("- [ ]")
                or line.strip().startswith("- [x]")
                or line.strip().startswith("- [X]")
            ):
                checked = "x" in line.strip()[3:5].lower()
                text = line.strip()[5:].strip()
                self._add_checklist_item(text, checked)
                i += 1
                continue

            # 일반 리스트 처리
            if line.strip().startswith("- ") or line.strip().startswith("* "):
                text = line.strip()[2:]
                self._add_bullet_item(text)
                i += 1
                continue

            # 번호 리스트 처리
            numbered_match = re.match(r"^(\d+)\.\s+(.+)$", line.strip())
            if numbered_match:
                text = numbered_match.group(2)
                self._add_paragraph_with_inline_styles(
                    f"{numbered_match.group(1)}. {text}"
                )
                i += 1
                continue

            # 인용문 처리
            if line.strip().startswith(">"):
                text = line.strip()[1:].strip()
                self._add_quote(text)
                i += 1
                continue

            # 수평선 처리
            if line.strip() in ["---", "***", "___"]:
                self._add_horizontal_rule()
                i += 1
                continue

            # 독립 이미지 라인 처리: 줄 전체가 이미지인 경우
            image_match = re.match(r"^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
            if image_match:
                alt_text = image_match.group(1)
                image_url = image_match.group(2)
                self._add_image_block(image_url, alt_text)
                i += 1
                continue

            # 일반 텍스트 (인라인 스타일 적용)
            if line.strip():
                self._add_paragraph_with_inline_styles(line)
            else:
                self._add_text("\n")

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
            if "insertTable" in req:
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
            ref_url = self._reference_links.get(ref_part.lower(), "")
            if ref_url:
                return f"[{text_part}]({ref_url})"
            return match.group(0)  # 참조 못 찾으면 원본 유지

        # 참조 링크 패턴: [text][ref] 또는 [text][]
        text = re.sub(r"\[([^\]]+)\]\[([^\]]*)\]", replace_ref_link, text)

        # 정규식 패턴들 (순서 중요 - 긴 패턴 먼저)
        patterns = [
            (
                r"!\[([^\]]*)\]\(([^)]+)\)",
                "image",
            ),  # ![alt](url) - 이미지 (링크보다 먼저!)
            (r"\[([^\]]+)\]\(([^)]+)\)", "link"),  # [text](url)
            # 중첩 포맷 (bold + italic)
            (r"\*\*\*(.+?)\*\*\*", "bold_italic"),  # ***bold italic***
            (r"___(.+?)___", "bold_italic"),  # ___bold italic___
            (r"\*\*_(.+?)_\*\*", "bold_italic"),  # **_bold italic_**
            (r"__\*(.+?)\*__", "bold_italic"),  # __*bold italic*__
            (r"\*__(.+?)__\*", "bold_italic"),  # *__bold italic__*
            (r"_\*\*(.+?)\*\*_", "bold_italic"),  # _**bold italic**_
            # 단일 포맷
            (r"\*\*(.+?)\*\*", "bold"),  # **bold** (non-greedy, 내부 * 허용)
            (r"__(.+?)__", "bold"),  # __bold__ (non-greedy, 내부 _ 허용)
            (r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", "italic"),  # *italic* (** 제외)
            (r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", "italic"),  # _italic_ (__ 제외)
            (r"`([^`]+)`", "code"),  # `code`
            (r"~~(.+?)~~", "strikethrough"),  # ~~strike~~ (non-greedy)
        ]

        # 모든 매치 찾기
        all_matches = []
        for pattern, style in patterns:
            for match in re.finditer(pattern, text):
                if style == "link":
                    all_matches.append(
                        (
                            match.start(),
                            match.end(),
                            match.group(1),
                            style,
                            match.group(2),
                        )
                    )
                elif style == "image":
                    # 이미지: group(1)=alt텍스트, group(2)=URL
                    all_matches.append(
                        (
                            match.start(),
                            match.end(),
                            match.group(1),
                            style,
                            match.group(2),
                        )
                    )
                else:
                    all_matches.append(
                        (match.start(), match.end(), match.group(1), style, None)
                    )

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
            if style == "bold":
                segment.bold = True
            elif style == "italic":
                segment.italic = True
            elif style == "bold_italic":
                segment.bold = True
                segment.italic = True
            elif style == "code":
                segment.code = True
            elif style == "strikethrough":
                segment.strikethrough = True
            elif style == "link":
                segment.link = link_url
            elif style == "image":
                segment.image_url = link_url  # URL (HTTP/HTTPS 또는 로컬 경로)
                segment.image_alt = content  # alt 텍스트

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
            text = "\n"
        elif not text.endswith("\n"):
            text = text + "\n"

        self.requests.append(
            {"insertText": {"location": {"index": self.current_index}, "text": text}}
        )

        start_index = self.current_index
        self.current_index += utf16_len(text)
        return start_index

    def _add_paragraph_with_inline_styles(self, text: str):
        """인라인 스타일이 적용된 단락 추가 (Premium Dark Text 스타일)"""
        result = self._parse_inline_formatting(text)

        # 전체 텍스트 먼저 삽입
        full_text = "".join(seg.text for seg in result.segments)
        start = self._add_text(full_text)

        # Premium Dark Text 스타일 사용
        if self.style and self.use_premium_style:
            body_config = self.style.typography.get("body", {})
            color_name = body_config.get("color", "text_primary")
            color = self.style.get_color(color_name)
            line_height = body_config.get("line_height", 1.65) * 100
            space_after = body_config.get("space_after", 10)
            font_size = body_config.get("size", 11)

            # NORMAL_TEXT Named Style + 커스텀 스타일
            self.requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": self.current_index - 1,
                        },
                        "paragraphStyle": {
                            "namedStyleType": "NORMAL_TEXT",
                            "lineSpacing": line_height,
                            "spaceBelow": {"magnitude": space_after, "unit": "PT"},
                        },
                        "fields": "namedStyleType,lineSpacing,spaceBelow",
                    }
                }
            )

            # 본문 색상 적용
            self.requests.append(
                {
                    "updateTextStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": self.current_index - 1,
                        },
                        "textStyle": {
                            "foregroundColor": {"color": {"rgbColor": color}},
                            "fontSize": {"magnitude": font_size, "unit": "PT"},
                        },
                        "fields": "foregroundColor,fontSize",
                    }
                }
            )
        else:
            # 기본 스타일 (레거시)
            self.requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": self.current_index - 1,
                        },
                        "paragraphStyle": {
                            "lineSpacing": 115,  # 115% 줄간격 (SKILL.md 표준)
                            "spaceBelow": {
                                "magnitude": 0,
                                "unit": "PT",
                            },  # 0pt (줄바꿈 최소화)
                        },
                        "fields": "lineSpacing,spaceBelow",
                    }
                }
            )

        # 각 세그먼트에 스타일 적용
        current_pos = start
        for segment in result.segments:
            end_pos = current_pos + utf16_len(segment.text)
            self._apply_segment_style(segment, current_pos, end_pos)
            current_pos = end_pos

    def _add_heading(self, text: str, level: int):
        """제목 추가 (Premium Dark Text 스타일 적용)"""
        # 목차용 헤딩 수집
        self.headings.append(
            {"text": text, "level": level, "index": self.current_index}
        )

        start = self._add_text(text)

        # Premium Dark Text 스타일 사용
        if self.style and self.use_premium_style:
            heading_config = self.style.get_heading_style(level)
            color_name = heading_config.get("color", "heading_primary")
            color = self.style.get_color(color_name)

            space_before = heading_config.get("space_before", 24)
            space_after = heading_config.get("space_after", 8)
            font_size = heading_config.get("size", 16)
            font_weight = heading_config.get("weight", 600)
            line_height = heading_config.get("line_height", 1.3) * 100

            # 제목 스타일 적용 (첫 H1은 TITLE, 나머지는 HEADING_N)
            if level == 1 and self._is_first_h1:
                heading_style = "TITLE"
                self._is_first_h1 = False
            else:
                heading_style = f"HEADING_{min(level, 6)}"
            self.requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": self.current_index - 1,
                        },
                        "paragraphStyle": {
                            "namedStyleType": heading_style,
                            "spaceAbove": {"magnitude": space_before, "unit": "PT"},
                            "spaceBelow": {"magnitude": space_after, "unit": "PT"},
                            "lineSpacing": line_height,
                        },
                        "fields": "namedStyleType,spaceAbove,spaceBelow,lineSpacing",
                    }
                }
            )

            # 색상 및 폰트 스타일 적용
            self.requests.append(
                {
                    "updateTextStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": self.current_index - 1,
                        },
                        "textStyle": {
                            "foregroundColor": {"color": {"rgbColor": color}},
                            "fontSize": {"magnitude": font_size, "unit": "PT"},
                            "bold": font_weight >= 600,
                        },
                        "fields": "foregroundColor,fontSize,bold",
                    }
                }
            )

            # H1 하단 구분선 적용 (SKILL.md 2.3 표준)
            if level == 1 and heading_config.get("border_bottom"):
                border_style = self.style.get_h1_border_style()
                self.requests.append(
                    {
                        "updateParagraphStyle": {
                            "range": {
                                "startIndex": start,
                                "endIndex": self.current_index,
                            },
                            "paragraphStyle": {"borderBottom": border_style},
                            "fields": "borderBottom",
                        }
                    }
                )
        else:
            # 기본 스타일 (레거시)
            space_settings = {
                1: {"before": 48, "after": 16},
                2: {"before": 36, "after": 12},
                3: {"before": 28, "after": 8},
                4: {"before": 20, "after": 6},
                5: {"before": 16, "after": 4},
                6: {"before": 12, "after": 4},
            }
            spacing = space_settings.get(level, {"before": 16, "after": 8})

            # 첫 H1은 TITLE 스타일 적용
            if level == 1 and self._is_first_h1:
                heading_style = "TITLE"
                self._is_first_h1 = False
            else:
                heading_style = f"HEADING_{min(level, 6)}"
            self.requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": self.current_index - 1,
                        },
                        "paragraphStyle": {
                            "namedStyleType": heading_style,
                            "spaceAbove": {
                                "magnitude": spacing["before"],
                                "unit": "PT",
                            },
                            "spaceBelow": {"magnitude": spacing["after"], "unit": "PT"},
                            "lineSpacing": 120,
                        },
                        "fields": "namedStyleType,spaceAbove,spaceBelow,lineSpacing",
                    }
                }
            )

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
            requests, new_index = self._table_renderer.render(
                table_data, self.current_index
            )
            self.requests.extend(requests)
            self.current_index = new_index

    def _add_native_table_two_phase(self, table_data):
        """
        최적화된 2단계 네이티브 테이블 처리 (v2.4.1 - Rate Limit 처리 추가)

        API 호출 최적화:
        - 쓰기: 3회 (기존 요청 + 테이블 구조 + 콘텐츠/스타일)
        - 읽기: 2회 (인덱스 확인 + 테이블 구조 조회)

        Rate Limit (429) 처리를 위한 지수 백오프 재시도 로직 포함.
        """
        import time
        from googleapiclient.errors import HttpError

        def _retry(request_fn, max_retries=5, initial_delay=30):
            """Rate Limit 처리를 위한 재시도 래퍼"""
            for attempt in range(max_retries):
                try:
                    return request_fn()
                except HttpError as e:
                    if e.resp.status == 429 and attempt < max_retries - 1:
                        wait_time = initial_delay * (1.5 ** attempt)
                        print(f"     [429] Rate limit, {wait_time:.0f}초 대기 후 재시도...")
                        time.sleep(wait_time)
                    else:
                        raise

        # 1단계: 문서 현재 상태 조회하여 인덱스 동기화
        doc = _retry(
            lambda: self.docs_service.documents().get(documentId=self.doc_id).execute()
        )
        body = doc.get("body", {})
        content = body.get("content", [])
        doc_end_index = content[-1].get("endIndex", 1) if content else 1

        # 2단계: 기존 요청 먼저 실행 (테이블 전까지의 콘텐츠)
        # 요청들의 인덱스를 실제 문서 상태에 맞게 재계산
        if self.requests:
            # 실제 문서 끝 위치로 인덱스 오프셋 계산
            actual_insert_index = doc_end_index - 1

            # 요청들의 인덱스 재계산
            adjusted_requests = self._adjust_request_indices(
                self.requests, actual_insert_index
            )

            _retry(
                lambda: self.docs_service.documents().batchUpdate(
                    documentId=self.doc_id, body={"requests": adjusted_requests}
                ).execute()
            )
            self.requests = []

        # 3단계: 문서 재조회 + 테이블 구조 삽입
        doc = _retry(
            lambda: self.docs_service.documents().get(documentId=self.doc_id).execute()
        )
        body = doc.get("body", {})
        content = body.get("content", [])
        doc_end_index = content[-1].get("endIndex", 1) if content else 1
        table_start_index = doc_end_index - 1

        structure_request = self._table_renderer.render_table_structure(
            table_data, table_start_index
        )

        if structure_request:
            _retry(
                lambda: self.docs_service.documents().batchUpdate(
                    documentId=self.doc_id, body={"requests": [structure_request]}
                ).execute()
            )

        # 3단계: 테이블 구조 조회 + 콘텐츠/스타일 적용 (읽기 1회 + 쓰기 1회)
        # 최적화: 마지막 documents.get을 여기서 수행하고 current_index도 동시에 업데이트
        doc = _retry(
            lambda: self.docs_service.documents().get(documentId=self.doc_id).execute()
        )
        table_element = self._find_last_table(doc)

        if table_element:
            unified_requests = self._table_renderer.render_table_content_and_styles(
                table_data, table_element
            )
            if unified_requests:
                _retry(
                    lambda: self.docs_service.documents().batchUpdate(
                        documentId=self.doc_id, body={"requests": unified_requests}
                    ).execute()
                )

        # current_index 업데이트
        # 문서 끝 인덱스 - 1로 설정 (다음 콘텐츠 삽입 위치)
        body = doc.get("body", {})
        content = body.get("content", [])
        if content:
            # 문서 끝 인덱스는 마지막 요소의 endIndex - 1
            self.current_index = content[-1].get("endIndex", 1) - 1
        else:
            self.current_index = 1

    def _adjust_request_indices(
        self, requests: list[dict], target_start_index: int
    ) -> list[dict]:
        """
        요청들의 인덱스를 실제 문서 상태에 맞게 재계산

        Args:
            requests: 원본 요청 리스트
            target_start_index: 실제 문서에서 삽입할 시작 위치

        Returns:
            인덱스가 조정된 요청 리스트
        """
        if not requests:
            return requests

        # 원본 요청의 최소 인덱스 찾기
        min_index = float("inf")
        for req in requests:
            if "insertText" in req:
                idx = req["insertText"]["location"]["index"]
                min_index = min(min_index, idx)
            elif "insertInlineImage" in req:
                idx = req["insertInlineImage"]["location"]["index"]
                min_index = min(min_index, idx)

        if min_index == float("inf"):
            return requests

        # 오프셋 계산
        offset = target_start_index - min_index

        # 새 요청 리스트 생성 (원본 수정 방지)
        adjusted = []
        for req in requests:
            new_req = {}
            for key, value in req.items():
                if key == "insertText":
                    new_value = dict(value)
                    new_value["location"] = dict(value["location"])
                    new_value["location"]["index"] += offset
                    new_req[key] = new_value
                elif key == "insertInlineImage":
                    new_value = dict(value)
                    new_value["location"] = dict(value["location"])
                    new_value["location"]["index"] += offset
                    new_req[key] = new_value
                elif key == "updateTextStyle":
                    new_value = dict(value)
                    new_value["range"] = dict(value["range"])
                    new_value["range"]["startIndex"] += offset
                    new_value["range"]["endIndex"] += offset
                    new_req[key] = new_value
                elif key == "updateParagraphStyle":
                    new_value = dict(value)
                    new_value["range"] = dict(value["range"])
                    new_value["range"]["startIndex"] += offset
                    new_value["range"]["endIndex"] += offset
                    new_req[key] = new_value
                elif key == "createParagraphBullets":
                    new_value = dict(value)
                    new_value["range"] = dict(value["range"])
                    new_value["range"]["startIndex"] += offset
                    new_value["range"]["endIndex"] += offset
                    new_req[key] = new_value
                else:
                    new_req[key] = value
            adjusted.append(new_req)

        return adjusted

    def _find_last_table(self, doc: dict) -> dict | None:
        """문서에서 마지막 테이블 요소 찾기"""
        body = doc.get("body", {})
        content = body.get("content", [])

        # 뒤에서부터 검색하여 첫 번째 테이블 반환
        for element in reversed(content):
            if "table" in element:
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
                self.requests.append(
                    {
                        "updateTextStyle": {
                            "range": {
                                "startIndex": start,
                                "endIndex": self.current_index - 1,
                            },
                            "textStyle": {"bold": True},
                            "fields": "bold",
                        }
                    }
                )
                # 구분선
                separator = "-+-".join("-" * w for w in col_widths)
                self._add_text(separator)
            else:
                self._add_text(line_text)

    def _add_code_block(self, code: str, lang: str = ""):
        """
        코드 블록 추가 (테이블 기반 박스 스타일)

        Google Docs API에는 네이티브 코드 블록이 없으므로,
        1x1 테이블 + 배경색 + 고정폭 폰트로 시각적 코드 박스를 구현합니다.

        v2.8.0: 테이블 기반 코드 박스로 업그레이드
        """
        # 2단계 테이블 처리 (docs_service가 있는 경우)
        if self.docs_service and self.doc_id:
            self._add_code_block_as_table(code, lang)
        else:
            # 레거시 방식 (단순 텍스트 + 배경색)
            self._add_code_block_legacy(code, lang)

    def _add_code_block_as_table(self, code: str, lang: str = ""):
        """
        코드 블록을 1x1 테이블로 추가 (시각적 박스 효과)

        테이블 구조:
        ┌─────────────────────────────┐
        │ 📄 PYTHON                   │  ← 언어 헤더 (옵션)
        ├─────────────────────────────┤
        │ def hello():                │
        │     print("Hello World")    │  ← 코드 내용
        └─────────────────────────────┘
        """
        import time
        from googleapiclient.errors import HttpError

        def _retry(request_fn, max_retries=5, initial_delay=30):
            for attempt in range(max_retries):
                try:
                    return request_fn()
                except HttpError as e:
                    if e.resp.status == 429 and attempt < max_retries - 1:
                        wait_time = initial_delay * (1.5 ** attempt)
                        time.sleep(wait_time)
                    else:
                        raise

        # 1단계: 기존 요청 먼저 실행
        doc = _retry(
            lambda: self.docs_service.documents().get(documentId=self.doc_id).execute()
        )
        body = doc.get("body", {})
        content = body.get("content", [])
        doc_end_index = content[-1].get("endIndex", 1) if content else 1

        if self.requests:
            actual_insert_index = doc_end_index - 1
            adjusted_requests = self._adjust_request_indices(
                self.requests, actual_insert_index
            )
            _retry(
                lambda: self.docs_service.documents().batchUpdate(
                    documentId=self.doc_id, body={"requests": adjusted_requests}
                ).execute()
            )
            self.requests = []

        # 2단계: 문서 재조회 + 테이블 삽입
        doc = _retry(
            lambda: self.docs_service.documents().get(documentId=self.doc_id).execute()
        )
        body = doc.get("body", {})
        content = body.get("content", [])
        doc_end_index = content[-1].get("endIndex", 1) if content else 1
        table_start_index = doc_end_index - 1

        # 1x1 테이블 삽입 (또는 언어 헤더 포함 시 2x1)
        row_count = 2 if lang else 1
        _retry(
            lambda: self.docs_service.documents().batchUpdate(
                documentId=self.doc_id,
                body={
                    "requests": [
                        {
                            "insertTable": {
                                "rows": row_count,
                                "columns": 1,
                                "location": {"index": table_start_index},
                            }
                        }
                    ]
                },
            ).execute()
        )

        # 3단계: 테이블 구조 조회 및 내용 채우기
        doc = _retry(
            lambda: self.docs_service.documents().get(documentId=self.doc_id).execute()
        )
        table_element = self._find_last_table(doc)

        if not table_element:
            # 테이블 생성 실패 시 레거시 방식으로 폴백
            self._add_code_block_legacy(code, lang)
            return

        table = table_element.get("table", {})
        table_rows = table.get("tableRows", [])

        # 테이블 스타일 (전체 너비 510pt = 18cm)
        table_start = table_element.get("startIndex", 1)
        table_end = table_element.get("endIndex", table_start + 1)

        style_requests = []

        if lang and len(table_rows) >= 2:
            # 언어 헤더 셀 (첫 번째 행)
            header_row = table_rows[0]
            header_cells = header_row.get("tableCells", [])
            if header_cells:
                header_cell = header_cells[0]
                header_start = header_cell.get("startIndex", 0)
                header_content = header_cell.get("content", [])
                if header_content:
                    para = header_content[0].get("paragraph", {})
                    para_elements = para.get("elements", [])
                    if para_elements:
                        text_start = para_elements[0].get("startIndex", header_start + 1)
                        # 언어 레이블 삽입
                        style_requests.append({
                            "insertText": {
                                "location": {"index": text_start},
                                "text": f"📄 {lang.upper()}"
                            }
                        })

            # 코드 셀 (두 번째 행)
            code_row = table_rows[1]
        else:
            # 코드 셀만 (첫 번째 행)
            code_row = table_rows[0] if table_rows else None

        if code_row:
            code_cells = code_row.get("tableCells", [])
            if code_cells:
                code_cell = code_cells[0]
                code_content = code_cell.get("content", [])
                if code_content:
                    para = code_content[0].get("paragraph", {})
                    para_elements = para.get("elements", [])
                    if para_elements:
                        text_start = para_elements[0].get("startIndex", 1)
                        # 코드 내용 삽입
                        style_requests.append({
                            "insertText": {
                                "location": {"index": text_start},
                                "text": code
                            }
                        })

        # 내용 삽입 실행
        if style_requests:
            # 역순 정렬 (인덱스 시프트 방지)
            style_requests.sort(
                key=lambda x: x.get("insertText", {}).get("location", {}).get("index", 0),
                reverse=True
            )
            _retry(
                lambda: self.docs_service.documents().batchUpdate(
                    documentId=self.doc_id, body={"requests": style_requests}
                ).execute()
            )

        # 4단계: 스타일 적용
        doc = _retry(
            lambda: self.docs_service.documents().get(documentId=self.doc_id).execute()
        )
        table_element = self._find_last_table(doc)

        if table_element:
            table = table_element.get("table", {})
            table_rows = table.get("tableRows", [])

            format_requests = []

            for row_idx, row in enumerate(table_rows):
                cells = row.get("tableCells", [])
                for cell in cells:
                    cell_content = cell.get("content", [])
                    for content_el in cell_content:
                        if "paragraph" in content_el:
                            para = content_el["paragraph"]
                            para_elements = para.get("elements", [])
                            for el in para_elements:
                                if "textRun" in el:
                                    start_idx = el.get("startIndex", 0)
                                    end_idx = el.get("endIndex", start_idx + 1)

                                    if lang and row_idx == 0:
                                        # 언어 헤더 스타일 (언어별 색상 배지)
                                        lang_lower = lang.lower()
                                        # 언어별 텍스트 색상 (어두운 톤)
                                        lang_text_colors = {
                                            "python": {"red": 0.2, "green": 0.35, "blue": 0.55},
                                            "javascript": {"red": 0.6, "green": 0.5, "blue": 0.1},
                                            "typescript": {"red": 0.18, "green": 0.45, "blue": 0.7},
                                            "bash": {"red": 0.25, "green": 0.25, "blue": 0.25},
                                            "shell": {"red": 0.25, "green": 0.25, "blue": 0.25},
                                            "json": {"red": 0.5, "green": 0.35, "blue": 0.15},
                                            "yaml": {"red": 0.45, "green": 0.25, "blue": 0.45},
                                            "sql": {"red": 0.7, "green": 0.35, "blue": 0.15},
                                            "html": {"red": 0.8, "green": 0.25, "blue": 0.15},
                                            "css": {"red": 0.15, "green": 0.45, "blue": 0.8},
                                            "go": {"red": 0.0, "green": 0.55, "blue": 0.65},
                                            "rust": {"red": 0.7, "green": 0.3, "blue": 0.2},
                                            "java": {"red": 0.7, "green": 0.4, "blue": 0.2},
                                        }
                                        text_color = lang_text_colors.get(
                                            lang_lower, {"red": 0.35, "green": 0.35, "blue": 0.35}
                                        )
                                        format_requests.append({
                                            "updateTextStyle": {
                                                "range": {"startIndex": start_idx, "endIndex": end_idx},
                                                "textStyle": {
                                                    "fontSize": {"magnitude": 9, "unit": "PT"},
                                                    "bold": True,
                                                    "foregroundColor": {
                                                        "color": {"rgbColor": text_color}
                                                    },
                                                    "weightedFontFamily": {
                                                        "fontFamily": "Arial",
                                                        "weight": 700,
                                                    },
                                                },
                                                "fields": "fontSize,bold,foregroundColor,weightedFontFamily",
                                            }
                                        })
                                    else:
                                        # 코드 스타일
                                        format_requests.append({
                                            "updateTextStyle": {
                                                "range": {"startIndex": start_idx, "endIndex": end_idx},
                                                "textStyle": {
                                                    "weightedFontFamily": {
                                                        "fontFamily": self.code_font,
                                                        "weight": 400,
                                                    },
                                                    "fontSize": {"magnitude": 10, "unit": "PT"},
                                                    "foregroundColor": {
                                                        "color": {"rgbColor": {"red": 0.15, "green": 0.15, "blue": 0.15}}
                                                    },
                                                },
                                                "fields": "weightedFontFamily,fontSize,foregroundColor",
                                            }
                                        })

                    # 셀 배경색 설정
                    cell_start = cell.get("startIndex", 0)
                    cell_end = cell.get("endIndex", cell_start + 1)

                    if lang and row_idx == 0:
                        # 헤더 셀: 언어별 연한 배경색
                        lang_lower = lang.lower()
                        lang_header_bg = {
                            "python": {"red": 0.9, "green": 0.92, "blue": 0.96},    # 연한 파랑
                            "javascript": {"red": 0.98, "green": 0.96, "blue": 0.88},  # 연한 노랑
                            "typescript": {"red": 0.88, "green": 0.93, "blue": 0.98},  # 연한 청색
                            "bash": {"red": 0.92, "green": 0.92, "blue": 0.92},      # 연한 회색
                            "shell": {"red": 0.92, "green": 0.92, "blue": 0.92},     # 연한 회색
                            "json": {"red": 0.96, "green": 0.94, "blue": 0.9},       # 연한 갈색
                            "yaml": {"red": 0.95, "green": 0.92, "blue": 0.95},      # 연한 보라
                            "sql": {"red": 0.98, "green": 0.93, "blue": 0.88},       # 연한 주황
                            "html": {"red": 0.98, "green": 0.9, "blue": 0.88},       # 연한 빨강
                            "css": {"red": 0.88, "green": 0.93, "blue": 0.98},       # 연한 파랑
                            "go": {"red": 0.88, "green": 0.96, "blue": 0.97},        # 연한 청록
                            "rust": {"red": 0.97, "green": 0.92, "blue": 0.9},       # 연한 적갈
                            "java": {"red": 0.97, "green": 0.93, "blue": 0.9},       # 연한 주황
                        }
                        bg_color = lang_header_bg.get(
                            lang_lower, {"red": 0.92, "green": 0.92, "blue": 0.92}
                        )
                    else:
                        # 코드 셀: 연한 회색 배경
                        bg_color = {
                            "red": self.code_bg_color[0],
                            "green": self.code_bg_color[1],
                            "blue": self.code_bg_color[2],
                        }

                    format_requests.append({
                        "updateTableCellStyle": {
                            "tableStartLocation": {"index": table_element.get("startIndex", 1)},
                            "tableCellStyle": {
                                "backgroundColor": {"color": {"rgbColor": bg_color}},
                                "paddingLeft": {"magnitude": 10, "unit": "PT"},
                                "paddingRight": {"magnitude": 10, "unit": "PT"},
                                "paddingTop": {"magnitude": 6, "unit": "PT"},
                                "paddingBottom": {"magnitude": 6, "unit": "PT"},
                            },
                            "fields": "backgroundColor,paddingLeft,paddingRight,paddingTop,paddingBottom",
                        }
                    })

            # 테이블 테두리 스타일 (Google Docs 네이티브 코드 블록 스타일)
            # 연한 회색 테두리로 코드 박스 효과
            border_color = {"red": 0.8, "green": 0.8, "blue": 0.8}
            format_requests.append({
                "updateTableCellStyle": {
                    "tableStartLocation": {"index": table_element.get("startIndex", 1)},
                    "tableCellStyle": {
                        "borderLeft": {
                            "width": {"magnitude": 1, "unit": "PT"},
                            "dashStyle": "SOLID",
                            "color": {"color": {"rgbColor": border_color}},
                        },
                        "borderRight": {
                            "width": {"magnitude": 1, "unit": "PT"},
                            "dashStyle": "SOLID",
                            "color": {"color": {"rgbColor": border_color}},
                        },
                        "borderTop": {
                            "width": {"magnitude": 1, "unit": "PT"},
                            "dashStyle": "SOLID",
                            "color": {"color": {"rgbColor": border_color}},
                        },
                        "borderBottom": {
                            "width": {"magnitude": 1, "unit": "PT"},
                            "dashStyle": "SOLID",
                            "color": {"color": {"rgbColor": border_color}},
                        },
                    },
                    "fields": "borderLeft,borderRight,borderTop,borderBottom",
                }
            })

            if format_requests:
                _retry(
                    lambda: self.docs_service.documents().batchUpdate(
                        documentId=self.doc_id, body={"requests": format_requests}
                    ).execute()
                )

        # current_index 업데이트
        doc = _retry(
            lambda: self.docs_service.documents().get(documentId=self.doc_id).execute()
        )
        body = doc.get("body", {})
        content = body.get("content", [])
        if content:
            self.current_index = content[-1].get("endIndex", 1) - 1
        else:
            self.current_index = 1

    def _add_code_block_legacy(self, code: str, lang: str = ""):
        """코드 블록 추가 (레거시 방식 - 텍스트 + paragraph border)

        docs_service 없이도 시각적 코드 박스 효과를 제공합니다.
        v2.9.0: paragraph border + shading으로 네이티브 코드 블록 유사 효과
        """
        # 언어 레이블 (있을 경우) - 배지 스타일
        if lang:
            lang_lower = lang.lower()
            # 언어별 텍스트 색상
            lang_text_colors = {
                "python": {"red": 0.2, "green": 0.35, "blue": 0.55},
                "javascript": {"red": 0.6, "green": 0.5, "blue": 0.1},
                "typescript": {"red": 0.18, "green": 0.45, "blue": 0.7},
                "bash": {"red": 0.25, "green": 0.25, "blue": 0.25},
                "shell": {"red": 0.25, "green": 0.25, "blue": 0.25},
                "json": {"red": 0.5, "green": 0.35, "blue": 0.15},
                "yaml": {"red": 0.45, "green": 0.25, "blue": 0.45},
                "sql": {"red": 0.7, "green": 0.35, "blue": 0.15},
                "html": {"red": 0.8, "green": 0.25, "blue": 0.15},
                "css": {"red": 0.15, "green": 0.45, "blue": 0.8},
                "go": {"red": 0.0, "green": 0.55, "blue": 0.65},
                "rust": {"red": 0.7, "green": 0.3, "blue": 0.2},
                "java": {"red": 0.7, "green": 0.4, "blue": 0.2},
            }
            text_color = lang_text_colors.get(
                lang_lower, {"red": 0.35, "green": 0.35, "blue": 0.35}
            )

            lang_start = self._add_text(f"📄 {lang.upper()}")
            self.requests.append(
                {
                    "updateTextStyle": {
                        "range": {
                            "startIndex": lang_start,
                            "endIndex": self.current_index - 1,
                        },
                        "textStyle": {
                            "fontSize": {"magnitude": 9, "unit": "PT"},
                            "foregroundColor": {
                                "color": {"rgbColor": text_color}
                            },
                            "bold": True,
                            "weightedFontFamily": {
                                "fontFamily": "Arial",
                                "weight": 700,
                            },
                        },
                        "fields": "fontSize,foregroundColor,bold,weightedFontFamily",
                    }
                }
            )
            self.requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {
                            "startIndex": lang_start,
                            "endIndex": self.current_index - 1,
                        },
                        "paragraphStyle": {
                            "spaceBelow": {"magnitude": 2, "unit": "PT"},
                            "spaceAbove": {"magnitude": 12, "unit": "PT"},
                        },
                        "fields": "spaceBelow,spaceAbove",
                    }
                }
            )

        # 코드 내용
        start = self._add_text(code)

        # 코드 스타일 (고정폭 폰트 + 배경색)
        self.requests.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": self.current_index - 1},
                    "textStyle": {
                        "weightedFontFamily": {
                            "fontFamily": self.code_font,
                            "weight": 400,
                        },
                        "fontSize": {"magnitude": 11, "unit": "PT"},
                        "foregroundColor": {
                            "color": {
                                "rgbColor": {"red": 0.15, "green": 0.15, "blue": 0.15}
                            }
                        },
                        "backgroundColor": {
                            "color": {
                                "rgbColor": {
                                    "red": self.code_bg_color[0],
                                    "green": self.code_bg_color[1],
                                    "blue": self.code_bg_color[2],
                                }
                            }
                        },
                    },
                    "fields": "weightedFontFamily,fontSize,foregroundColor,backgroundColor",
                }
            }
        )

        # 코드 블록 단락 스타일 (4면 테두리 + 음영으로 박스 효과)
        # Google Docs API의 paragraph border와 shading 활용
        border_color = {"red": 0.8, "green": 0.8, "blue": 0.8}
        border_style = {
            "color": {"color": {"rgbColor": border_color}},
            "width": {"magnitude": 1, "unit": "PT"},
            "padding": {"magnitude": 8, "unit": "PT"},
            "dashStyle": "SOLID",
        }
        code_bg = {
            "red": self.code_bg_color[0],
            "green": self.code_bg_color[1],
            "blue": self.code_bg_color[2],
        }

        self.requests.append(
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": start, "endIndex": self.current_index - 1},
                    "paragraphStyle": {
                        "namedStyleType": "NORMAL_TEXT",
                        "indentStart": {"magnitude": 12, "unit": "PT"},
                        "indentEnd": {"magnitude": 12, "unit": "PT"},
                        "lineSpacing": 130,  # 코드는 더 좁은 줄간격
                        "spaceAbove": {"magnitude": 4, "unit": "PT"},
                        "spaceBelow": {"magnitude": 12, "unit": "PT"},
                        # 4면 테두리로 코드 박스 효과
                        "borderTop": border_style,
                        "borderBottom": border_style,
                        "borderLeft": border_style,
                        "borderRight": border_style,
                        # 음영 배경
                        "shading": {
                            "backgroundColor": {"color": {"rgbColor": code_bg}}
                        },
                    },
                    "fields": "namedStyleType,indentStart,indentEnd,lineSpacing,spaceAbove,spaceBelow,borderTop,borderBottom,borderLeft,borderRight,shading",
                }
            }
        )

    def _add_bullet_item(self, text: str):
        """불릿 리스트 아이템 추가 (Premium Dark Text 스타일)"""
        result = self._parse_inline_formatting(text)
        full_text = "".join(seg.text for seg in result.segments)

        start = self._add_text(f"• {full_text}")

        # Premium Dark Text 스타일 적용
        if self.style and self.use_premium_style:
            list_config = self.style.typography.get("list", {})
            color_name = list_config.get("color", "text_primary")
            color = self.style.get_color(color_name)
            line_height = list_config.get("line_height", 1.55) * 100
            font_size = list_config.get("size", 11)
            indent = list_config.get("indent", 20)

            # 단락 스타일
            self.requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": self.current_index - 1,
                        },
                        "paragraphStyle": {
                            "namedStyleType": "NORMAL_TEXT",
                            "lineSpacing": line_height,
                            "indentStart": {"magnitude": indent, "unit": "PT"},
                            "spaceBelow": {
                                "magnitude": 0,
                                "unit": "PT",
                            },  # 0pt (줄바꿈 최소화)
                        },
                        "fields": "namedStyleType,lineSpacing,indentStart,spaceBelow",
                    }
                }
            )

            # 텍스트 스타일
            self.requests.append(
                {
                    "updateTextStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": self.current_index - 1,
                        },
                        "textStyle": {
                            "foregroundColor": {"color": {"rgbColor": color}},
                            "fontSize": {"magnitude": font_size, "unit": "PT"},
                        },
                        "fields": "foregroundColor,fontSize",
                    }
                }
            )

        # 인라인 스타일 적용 (bullet 문자 다음부터)
        current_pos = start + 2  # "• " 건너뛰기
        for segment in result.segments:
            end_pos = current_pos + utf16_len(segment.text)
            self._apply_segment_style(segment, current_pos, end_pos)
            current_pos = end_pos

    def _add_checklist_item(self, text: str, checked: bool):
        """체크리스트 아이템 추가"""
        checkbox = "☑" if checked else "☐"
        result = self._parse_inline_formatting(text)
        full_text = "".join(seg.text for seg in result.segments)
        self._add_text(f"{checkbox} {full_text}")

    def _add_quote(self, text: str):
        """인용문 추가 (인라인 포맷팅 지원)"""
        # 인라인 포맷팅 파싱 (bold, italic, code, link 등)
        result = self._parse_inline_formatting(text)
        full_text = "".join(seg.text for seg in result.segments)

        start = self._add_text(f"│ {full_text}")

        # 전체에 이탤릭 + 회색 기본 스타일
        self.requests.append(
            {
                "updateTextStyle": {
                    "range": {"startIndex": start, "endIndex": self.current_index - 1},
                    "textStyle": {
                        "italic": True,
                        "foregroundColor": {
                            "color": {
                                "rgbColor": {"red": 0.4, "green": 0.4, "blue": 0.4}
                            }
                        },
                    },
                    "fields": "italic,foregroundColor",
                }
            }
        )

        # 인라인 스타일 적용 ("│ " 다음부터)
        current_pos = start + 2  # "│ " 건너뛰기
        for segment in result.segments:
            end_pos = current_pos + utf16_len(segment.text)
            self._apply_segment_style(segment, current_pos, end_pos)
            current_pos = end_pos

    def _add_image_block(self, url: str, alt_text: str = ""):
        """
        이미지 블록 추가 (2단계 삽입)

        1단계: placeholder 텍스트 삽입
        2단계: create_google_doc()에서 실제 이미지로 교체

        Args:
            url: 이미지 URL (HTTP/HTTPS) 또는 로컬 경로
            alt_text: 이미지 alt 텍스트
        """
        # 로컬 경로 감지 및 URL 정규화
        normalized_url, is_local = self._normalize_image_url(url)

        if normalized_url:
            # 이미지 삽입 위치 기록 (현재 인덱스)
            self._pending_images.append(
                {
                    "index": self.current_index,
                    "url": normalized_url,
                    "alt": alt_text or "image",
                    "is_local": is_local,  # 로컬 파일 여부 표시
                    "original_url": url,  # 원본 경로 (디버깅용)
                }
            )

            # placeholder 텍스트 삽입 (나중에 삭제됨)
            placeholder = f"[🖼 {alt_text or 'image'}]"
            start = self._add_text(placeholder)

            # placeholder 스타일 (회색, 이탤릭)
            self.requests.append(
                {
                    "updateTextStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": self.current_index - 1,
                        },
                        "textStyle": {
                            "italic": True,
                            "foregroundColor": {
                                "color": {
                                    "rgbColor": {"red": 0.6, "green": 0.6, "blue": 0.6}
                                }
                            },
                        },
                        "fields": "italic,foregroundColor",
                    }
                }
            )
        else:
            # URL이 유효하지 않으면 아무것도 삽입하지 않음 (문서 독립성 보장)
            # 경고 메시지 삭제: Google Docs에 깨진 참조 표시 방지
            pass

    def _normalize_image_url(self, url: str) -> tuple[str | None, bool]:
        """
        이미지 URL 정규화

        HTTP/HTTPS URL은 그대로 반환
        로컬 경로는 절대 경로로 변환하여 반환

        Args:
            url: 원본 URL 또는 경로

        Returns:
            (정규화된 URL 또는 경로, is_local_file) 튜플
            - HTTP URL: (url, False)
            - 로컬 파일: (절대 경로, True)
            - 파일 없음: (None, False)
        """
        from pathlib import Path
        from urllib.parse import unquote

        url = url.strip()

        # URL 디코딩 (로컬 경로에서 %20 → 공백 등 변환)
        # 예: "스크린샷%202026-01-21%20113700.png" → "스크린샷 2026-01-21 113700.png"
        decoded_url = unquote(url)

        # HTTP/HTTPS URL (디코딩 없이 원본 사용)
        if url.startswith(("http://", "https://")):
            return url, False

        # Data URL (Base64 인코딩 이미지)
        if url.startswith("data:image/"):
            return url, False

        # 로컬 경로 처리 (디코딩된 URL 사용)
        local_path = None

        # 절대 경로
        if decoded_url.startswith(("/", "C:", "D:", "E:")):
            local_path = Path(decoded_url)
        # 상대 경로 (base_path 기준)
        elif decoded_url.startswith(("./", "../")) or not decoded_url.startswith("http"):
            if self.base_path:
                base = Path(self.base_path)
                if base.is_file():
                    base = base.parent
                local_path = (base / decoded_url).resolve()
            else:
                # base_path 없으면 현재 디렉토리 기준
                local_path = Path(decoded_url).resolve()

        # 파일 존재 확인
        if local_path and local_path.exists() and local_path.is_file():
            return str(local_path), True

        # 파일 없음
        return None, False

    def _is_broken_link(self, url: str) -> bool:
        """
        Google Docs에서 작동하지 않는 깨진 링크 여부 확인

        제외 대상:
        - 로컬 HTML 파일 (.html)
        - 상대 경로 링크 (./*, ../*)
        - 앵커만 있는 링크 (#*)
        - 파일 프로토콜 (file://*)
        - 로컬 마크다운 파일 (.md)

        Args:
            url: 검사할 URL

        Returns:
            bool: 깨진 링크면 True, 정상 링크면 False
        """
        url = url.strip()

        # 빈 URL
        if not url:
            return True

        # 앵커만 있는 링크 (#section)
        if url.startswith("#"):
            return True

        # 파일 프로토콜
        if url.startswith("file://"):
            return True

        # 상대 경로 (./*, ../*)
        if url.startswith("./") or url.startswith("../"):
            return True

        # 로컬 HTML 파일 (.html, .htm)
        url_lower = url.lower()
        if url_lower.endswith((".html", ".htm")) and not url.startswith(("http://", "https://")):
            return True

        # 로컬 마크다운 파일 (.md)
        if url_lower.endswith(".md") and not url.startswith(("http://", "https://")):
            return True

        # 확장자가 있는 로컬 파일 경로 패턴 (드라이브 문자 또는 슬래시로 시작)
        if re.match(r'^[a-zA-Z]:', url) or (url.startswith("/") and not url.startswith("//")):
            return True

        return False

    def _add_horizontal_rule(self):
        """수평선 추가 (SKILL.md 2.3 표준: ─ 반복 금지, 하단 구분선 사용)"""
        # 빈 단락 삽입 후 하단에 얇은 구분선 추가
        start = self._add_text(" ")

        if self.style and self.use_premium_style:
            divider_color = self.style.get_color("divider")

            # 여백 + 하단 구분선 (SKILL.md 2.3 표준)
            self.requests.append(
                {
                    "updateParagraphStyle": {
                        "range": {"startIndex": start, "endIndex": self.current_index},
                        "paragraphStyle": {
                            "spaceAbove": {"magnitude": 12, "unit": "PT"},
                            "spaceBelow": {"magnitude": 12, "unit": "PT"},
                            "borderBottom": {
                                "color": {"color": {"rgbColor": divider_color}},
                                "width": {"magnitude": 0.5, "unit": "PT"},
                                "padding": {"magnitude": 8, "unit": "PT"},
                                "dashStyle": "SOLID",
                            },
                        },
                        "fields": "spaceAbove,spaceBelow,borderBottom",
                    }
                }
            )

    def _apply_segment_style(self, segment: TextSegment, start: int, end: int):
        """세그먼트에 스타일 적용"""
        style_fields = []
        text_style: dict[str, Any] = {}

        if segment.bold:
            text_style["bold"] = True
            style_fields.append("bold")

        if segment.italic:
            text_style["italic"] = True
            style_fields.append("italic")

        if segment.strikethrough:
            text_style["strikethrough"] = True
            style_fields.append("strikethrough")

        if segment.code:
            text_style["weightedFontFamily"] = {
                "fontFamily": self.code_font,
                "weight": 400,
            }
            text_style["backgroundColor"] = {
                "color": {
                    "rgbColor": {
                        "red": self.code_bg_color[0],
                        "green": self.code_bg_color[1],
                        "blue": self.code_bg_color[2],
                    }
                }
            }
            style_fields.extend(["weightedFontFamily", "backgroundColor"])

        if segment.link:
            # 깨진 링크 필터링 (Google Docs에서 작동하지 않는 링크 제외)
            link_url = segment.link
            is_broken_link = self._is_broken_link(link_url)

            if not is_broken_link:
                text_style["link"] = {"url": link_url}
                text_style["foregroundColor"] = {
                    "color": {"rgbColor": {"red": 0.06, "green": 0.46, "blue": 0.88}}
                }
                text_style["underline"] = True
                style_fields.extend(["link", "foregroundColor", "underline"])

        if style_fields:
            self.requests.append(
                {
                    "updateTextStyle": {
                        "range": {"startIndex": start, "endIndex": end},
                        "textStyle": text_style,
                        "fields": ",".join(style_fields),
                    }
                }
            )


def _execute_with_retry(request_fn, max_retries=5, initial_delay=30):
    """
    Rate Limit (429) 처리를 위한 지수 백오프 재시도 래퍼

    Args:
        request_fn: 실행할 API 요청 함수 (람다 또는 callable)
        max_retries: 최대 재시도 횟수 (기본 5회)
        initial_delay: 초기 대기 시간 (초, 기본 30초 - 분당 60회 쿼터 고려)

    Returns:
        API 응답

    Raises:
        HttpError: 재시도 후에도 실패한 경우
    """
    import time
    from googleapiclient.errors import HttpError

    for attempt in range(max_retries):
        try:
            return request_fn()
        except HttpError as e:
            if e.resp.status == 429 and attempt < max_retries - 1:
                wait_time = initial_delay * (1.5 ** attempt)  # 30, 45, 67.5, 101...초
                print(f"     [429] Rate limit, {wait_time:.0f}초 대기 후 재시도 ({attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise


def create_google_doc(
    title: str,
    content: str,
    folder_id: Optional[str] = None,
    include_toc: bool = False,
    use_native_tables: bool = True,
    apply_page_style: bool = True,
    base_path: Optional[str] = None,
) -> str:
    """
    Google Docs 문서 생성 (v2.4.1 - Rate Limit 처리 추가)

    Args:
        title: 문서 제목
        content: 마크다운 콘텐츠
        folder_id: Google Drive 폴더 ID (None이면 기본 폴더)
        include_toc: 목차 포함 여부
        use_native_tables: 네이티브 테이블 사용 여부 (2단계 처리로 안정적)
        apply_page_style: 페이지 스타일 적용 여부 (A4, 72pt 여백, 115% 줄간격)
        base_path: 마크다운 파일의 기준 경로 (상대 이미지 경로 해석용)

    Returns:
        str: 생성된 문서의 URL
    """
    creds = get_credentials()

    # API 서비스 생성
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # 1. 빈 문서 생성
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc.get("documentId")
    print(f"[OK] 문서 생성됨: {title}")
    print(f"     ID: {doc_id}")

    # 2. 폴더로 이동
    target_folder = folder_id or DEFAULT_FOLDER_ID
    try:
        file = drive_service.files().get(fileId=doc_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents", []))

        drive_service.files().update(
            fileId=doc_id,
            addParents=target_folder,
            removeParents=previous_parents,
            fields="id, parents",
        ).execute()
        print("     폴더로 이동됨")
    except Exception as e:
        print(f"     폴더 이동 실패: {e}")

    # 3. 페이지 스타일 적용 (A4, 72pt 여백) - SKILL.md 전역 표준
    if apply_page_style:
        try:
            style = NotionStyle.default()
            page_style_request = style.get_page_style_request()
            _execute_with_retry(
                lambda: docs_service.documents().batchUpdate(
                    documentId=doc_id, body={"requests": [page_style_request]}
                ).execute()
            )
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
        base_path=base_path,
    )
    requests = converter.parse()

    # 남은 요청들 실행 (테이블 처리 중 일부 요청이 이미 실행되었을 수 있음)
    if requests:
        try:
            # 테이블 처리 후 문서 상태가 변경되었을 수 있으므로 인덱스 재계산
            doc = _execute_with_retry(
                lambda: docs_service.documents().get(documentId=doc_id).execute()
            )
            body = doc.get("body", {})
            content = body.get("content", [])
            doc_end_index = content[-1].get("endIndex", 1) if content else 1
            actual_insert_index = doc_end_index - 1

            # 요청들의 인덱스를 실제 문서 상태에 맞게 재계산
            adjusted_requests = converter._adjust_request_indices(
                requests, actual_insert_index
            )

            _execute_with_retry(
                lambda: docs_service.documents().batchUpdate(
                    documentId=doc_id, body={"requests": adjusted_requests}
                ).execute()
            )
            print(f"     콘텐츠 추가됨: {len(requests)} 요청")
        except Exception as e:
            print(f"     콘텐츠 추가 실패: {e}")
            raise
    else:
        print("     콘텐츠 추가됨 (테이블 포함)")

    # 5. 2단계 이미지 삽입 (placeholder → 실제 이미지) - API 최적화 버전
    if converter._pending_images:
        from pathlib import Path
        from .image_inserter import ImageInserter

        try:
            # ImageInserter 생성 (로컬 이미지 업로드용)
            image_inserter = ImageInserter(creds, docs_service, drive_service)

            # 로컬 이미지 업로드 및 URL 변환 (Drive API 호출)
            uploaded_count = 0
            for img_info in converter._pending_images:
                if img_info.get("is_local", False):
                    try:
                        local_path = Path(img_info["url"])
                        if local_path.exists():
                            file_id, public_url = image_inserter.upload_to_drive(
                                local_path,
                                folder_id=target_folder,
                                make_public=True,
                            )
                            img_info["url"] = public_url
                            img_info["is_local"] = False
                            uploaded_count += 1
                    except Exception as upload_err:
                        print(f"     이미지 업로드 실패 ({img_info.get('original_url', '')}): {upload_err}")

            if uploaded_count > 0:
                print(f"     로컬 이미지 {uploaded_count}개 업로드됨")

            # 최적화: 단 1회의 documents.get으로 모든 placeholder 위치 수집
            doc = _execute_with_retry(
                lambda: docs_service.documents().get(documentId=doc_id).execute()
            )
            body_content = doc.get("body", {}).get("content", [])

            # 유효한 이미지만 필터링 및 위치 정보 수집
            image_operations = []
            for img_info in converter._pending_images:
                if img_info.get("is_local", False):
                    continue

                placeholder_pattern = f"[🖼 {img_info['alt']}"
                placeholder_index = _find_text_index(body_content, placeholder_pattern)

                if placeholder_index is not None:
                    placeholder_full = f"[🖼 {img_info['alt']}]"
                    delete_length = len(placeholder_full) + 1
                    image_operations.append({
                        "index": placeholder_index,
                        "delete_length": delete_length,
                        "url": img_info["url"],
                        "alt": img_info.get("alt", ""),
                    })

            # 역순 정렬 (뒤에서부터 처리하여 인덱스 시프트 방지)
            image_operations.sort(key=lambda x: x["index"], reverse=True)

            # 최적화: 이미지별로 삭제+삽입을 단일 batchUpdate로 처리
            # (삭제와 삽입은 인덱스 의존성이 있어 완전 일괄 처리는 불가)
            # Rate Limit (429) 처리를 위한 지수 백오프 재시도 로직 추가
            import time
            from googleapiclient.errors import HttpError

            inserted_count = 0
            failed_count = 0

            for i, op in enumerate(image_operations):
                max_retries = 3
                retry_delay = 2  # 초기 딜레이 2초

                for attempt in range(max_retries):
                    try:
                        # 삭제 + 삽입을 단일 batchUpdate로 결합
                        docs_service.documents().batchUpdate(
                            documentId=doc_id,
                            body={
                                "requests": [
                                    # 먼저 삭제
                                    {
                                        "deleteContentRange": {
                                            "range": {
                                                "startIndex": op["index"],
                                                "endIndex": op["index"] + op["delete_length"],
                                            }
                                        }
                                    },
                                    # 같은 위치에 이미지 삽입
                                    {
                                        "insertInlineImage": {
                                            "location": {"index": op["index"]},
                                            "uri": op["url"],
                                            "objectSize": {
                                                "width": {"magnitude": 510, "unit": "PT"},
                                            },
                                        }
                                    },
                                ]
                            },
                        ).execute()
                        inserted_count += 1
                        break  # 성공 시 루프 탈출
                    except HttpError as e:
                        if e.resp.status == 429:
                            # Rate Limit - 재시도
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)  # 지수 백오프
                                print(f"     [429] Rate limit, {wait_time}초 대기 후 재시도... ({op.get('alt', '')})")
                                time.sleep(wait_time)
                            else:
                                print(f"     이미지 삽입 실패 (max retries) ({op.get('alt', '')})")
                                failed_count += 1
                        else:
                            print(f"     이미지 삽입 경고 ({op.get('alt', '')}): {e}")
                            failed_count += 1
                            break
                    except Exception as img_err:
                        print(f"     이미지 삽입 경고 ({op.get('alt', '')}): {img_err}")
                        failed_count += 1
                        break

                # Rate Limit 방지: 매 10개 이미지마다 1초 대기
                if (i + 1) % 10 == 0 and i + 1 < len(image_operations):
                    time.sleep(1)

            if inserted_count > 0:
                msg = f"     이미지 {inserted_count}개 삽입됨"
                if failed_count > 0:
                    msg += f" ({failed_count}개 실패)"
                print(msg)
        except Exception as e:
            print(f"     이미지 삽입 실패: {e}")

    # 6. 전체 문서 줄간격 적용 (115%) - SKILL.md 전역 표준
    # 최적화: 이미지 삽입 없는 경우에만 documents.get 호출 필요
    if apply_page_style:
        try:
            # 최종 문서 상태 조회 (이미지 삽입으로 인덱스 변경됐을 수 있음)
            doc = _execute_with_retry(
                lambda: docs_service.documents().get(documentId=doc_id).execute()
            )
            end_index = max(el.get("endIndex", 1) for el in doc["body"]["content"])

            if end_index > 2:
                _execute_with_retry(
                    lambda: docs_service.documents().batchUpdate(
                        documentId=doc_id,
                        body={
                            "requests": [
                                {
                                    "updateParagraphStyle": {
                                        "range": {
                                            "startIndex": 1,
                                            "endIndex": end_index - 1,
                                        },
                                        "paragraphStyle": {
                                            "lineSpacing": 115,
                                        },
                                        "fields": "lineSpacing",
                                    }
                                }
                            ]
                        },
                    ).execute()
                )
                print("     줄간격 적용됨 (115%)")
        except Exception as e:
            print(f"     줄간격 적용 실패: {e}")

    # 7. 문서 URL 반환
    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_url


def _find_text_index(body_content: list[dict], search_text: str) -> int | None:
    """
    Google Docs body content에서 특정 텍스트의 시작 인덱스 찾기

    Args:
        body_content: 문서 body.content 리스트
        search_text: 찾을 텍스트

    Returns:
        텍스트 시작 인덱스 또는 None
    """
    for element in body_content:
        if "paragraph" in element:
            paragraph = element["paragraph"]
            para_elements = paragraph.get("elements", [])

            for para_el in para_elements:
                if "textRun" in para_el:
                    text_content = para_el["textRun"].get("content", "")
                    if search_text in text_content:
                        # 텍스트 시작 인덱스 계산
                        start_index = para_el.get("startIndex", 0)
                        offset = text_content.find(search_text)
                        return start_index + offset

    return None


def update_google_doc(
    doc_id: str,
    content: str,
    include_toc: bool = False,
    use_native_tables: bool = True,
    apply_page_style: bool = True,
    base_path: Optional[str] = None,
) -> str:
    """
    기존 Google Docs 문서 내용을 전부 삭제하고 새 내용으로 교체 (문서 ID 유지)

    Args:
        doc_id: 기존 Google Docs 문서 ID
        content: 새 마크다운 콘텐츠
        include_toc: 목차 포함 여부
        use_native_tables: 네이티브 테이블 사용 여부
        apply_page_style: 페이지 스타일 적용 여부
        base_path: 마크다운 파일의 기준 경로 (상대 이미지 경로 해석용)

    Returns:
        str: 문서 URL
    """
    creds = get_credentials()

    # API 서비스 생성
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # 1. 기존 문서 내용 전체 삭제
    print("[1/5] 기존 내용 삭제 중...")
    try:
        doc = _execute_with_retry(
            lambda: docs_service.documents().get(documentId=doc_id).execute()
        )
        body_content = doc.get("body", {}).get("content", [])

        # 문서 끝 인덱스 찾기 (첫 번째 요소는 보통 sectionBreak, 마지막 요소의 endIndex - 1까지 삭제)
        if len(body_content) > 1:
            end_index = max(el.get("endIndex", 1) for el in body_content)
            if end_index > 2:
                _execute_with_retry(
                    lambda: docs_service.documents().batchUpdate(
                        documentId=doc_id,
                        body={
                            "requests": [
                                {
                                    "deleteContentRange": {
                                        "range": {
                                            "startIndex": 1,
                                            "endIndex": end_index - 1,
                                        }
                                    }
                                }
                            ]
                        },
                    ).execute()
                )
                print("       기존 내용 삭제됨")
        else:
            print("       문서가 비어있음")
    except Exception as e:
        print(f"       기존 내용 삭제 실패: {e}")
        raise

    # 2. 페이지 스타일 적용
    print("[2/5] 페이지 스타일 적용 중...")
    if apply_page_style:
        try:
            style = NotionStyle.default()
            page_style_request = style.get_page_style_request()
            _execute_with_retry(
                lambda: docs_service.documents().batchUpdate(
                    documentId=doc_id, body={"requests": [page_style_request]}
                ).execute()
            )
            print("       페이지 스타일 적용됨 (A4, 72pt 여백)")
        except Exception as e:
            print(f"       페이지 스타일 적용 실패: {e}")

    # 3. 콘텐츠 변환 및 추가
    print("[3/5] 콘텐츠 변환 중...")
    converter = MarkdownToDocsConverter(
        content,
        include_toc=include_toc,
        use_native_tables=use_native_tables,
        docs_service=docs_service if use_native_tables else None,
        doc_id=doc_id if use_native_tables else None,
        base_path=base_path,
    )
    requests = converter.parse()

    if requests:
        try:
            doc = _execute_with_retry(
                lambda: docs_service.documents().get(documentId=doc_id).execute()
            )
            body = doc.get("body", {})
            doc_content = body.get("content", [])
            doc_end_index = doc_content[-1].get("endIndex", 1) if doc_content else 1
            actual_insert_index = doc_end_index - 1

            adjusted_requests = converter._adjust_request_indices(
                requests, actual_insert_index
            )

            _execute_with_retry(
                lambda: docs_service.documents().batchUpdate(
                    documentId=doc_id, body={"requests": adjusted_requests}
                ).execute()
            )
            print(f"       콘텐츠 추가됨: {len(requests)} 요청")
        except Exception as e:
            print(f"       콘텐츠 추가 실패: {e}")
            raise
    else:
        print("       콘텐츠 추가됨 (테이블 포함)")

    # 4. 이미지 삽입
    print("[4/5] 이미지 삽입 중...")
    if converter._pending_images:
        from pathlib import Path
        from .image_inserter import ImageInserter

        try:
            image_inserter = ImageInserter(creds, docs_service, drive_service)

            # 로컬 이미지 업로드
            uploaded_count = 0
            for img_info in converter._pending_images:
                if img_info.get("is_local", False):
                    try:
                        local_path = Path(img_info["url"])
                        if local_path.exists():
                            file_id, public_url = image_inserter.upload_to_drive(
                                local_path,
                                folder_id=DEFAULT_FOLDER_ID,
                                make_public=True,
                            )
                            img_info["url"] = public_url
                            img_info["is_local"] = False
                            uploaded_count += 1
                    except Exception as upload_err:
                        print(f"       이미지 업로드 실패: {upload_err}")

            if uploaded_count > 0:
                print(f"       로컬 이미지 {uploaded_count}개 업로드됨")

            # placeholder 위치 찾기 및 이미지 삽입
            doc = _execute_with_retry(
                lambda: docs_service.documents().get(documentId=doc_id).execute()
            )
            body_content = doc.get("body", {}).get("content", [])

            image_operations = []
            for img_info in converter._pending_images:
                if img_info.get("is_local", False):
                    continue

                placeholder_pattern = f"[🖼 {img_info['alt']}"
                placeholder_index = _find_text_index(body_content, placeholder_pattern)

                if placeholder_index is not None:
                    placeholder_full = f"[🖼 {img_info['alt']}]"
                    delete_length = len(placeholder_full) + 1
                    image_operations.append({
                        "index": placeholder_index,
                        "delete_length": delete_length,
                        "url": img_info["url"],
                        "alt": img_info.get("alt", ""),
                    })

            image_operations.sort(key=lambda x: x["index"], reverse=True)

            import time
            from googleapiclient.errors import HttpError

            inserted_count = 0
            for i, op in enumerate(image_operations):
                max_retries = 3
                retry_delay = 2

                for attempt in range(max_retries):
                    try:
                        docs_service.documents().batchUpdate(
                            documentId=doc_id,
                            body={
                                "requests": [
                                    {
                                        "deleteContentRange": {
                                            "range": {
                                                "startIndex": op["index"],
                                                "endIndex": op["index"] + op["delete_length"],
                                            }
                                        }
                                    },
                                    {
                                        "insertInlineImage": {
                                            "location": {"index": op["index"]},
                                            "uri": op["url"],
                                            "objectSize": {
                                                "width": {"magnitude": 510, "unit": "PT"},
                                            },
                                        }
                                    },
                                ]
                            },
                        ).execute()
                        inserted_count += 1
                        break
                    except HttpError as e:
                        if e.resp.status == 429:
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)
                                print(f"       [429] Rate limit, {wait_time}초 대기...")
                                time.sleep(wait_time)
                        else:
                            break
                    except Exception:
                        break

                if (i + 1) % 10 == 0 and i + 1 < len(image_operations):
                    time.sleep(1)

            if inserted_count > 0:
                print(f"       이미지 {inserted_count}개 삽입됨")
        except Exception as e:
            print(f"       이미지 삽입 실패: {e}")
    else:
        print("       이미지 없음")

    # 5. 줄간격 적용
    print("[5/5] 줄간격 적용 중...")
    if apply_page_style:
        try:
            doc = _execute_with_retry(
                lambda: docs_service.documents().get(documentId=doc_id).execute()
            )
            end_index = max(el.get("endIndex", 1) for el in doc["body"]["content"])

            if end_index > 2:
                _execute_with_retry(
                    lambda: docs_service.documents().batchUpdate(
                        documentId=doc_id,
                        body={
                            "requests": [
                                {
                                    "updateParagraphStyle": {
                                        "range": {
                                            "startIndex": 1,
                                            "endIndex": end_index - 1,
                                        },
                                        "paragraphStyle": {
                                            "lineSpacing": 115,
                                        },
                                        "fields": "lineSpacing",
                                    }
                                }
                            ]
                        },
                    ).execute()
                )
                print("       줄간격 적용됨 (115%)")
        except Exception as e:
            print(f"       줄간격 적용 실패: {e}")

    doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_url
