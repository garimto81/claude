"""
HTML 와이어프레임 어댑터

기존 HTML 템플릿을 사용하여 와이어프레임 목업을 생성합니다.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class HTMLGenerationResult:
    """HTML 생성 결과"""
    success: bool
    html_content: str
    error_message: Optional[str] = None


class HTMLAdapter:
    """HTML 와이어프레임 어댑터"""

    DEFAULT_TEMPLATE_PATH = Path(__file__).parent.parent.parent.parent / "templates" / "mockup-wireframe.html"

    def __init__(self, template_path: Optional[Path] = None):
        """
        HTMLAdapter 초기화

        Args:
            template_path: HTML 템플릿 경로
        """
        self.template_path = template_path or self.DEFAULT_TEMPLATE_PATH

    def generate(
        self,
        screen_name: str,
        description: str = "",
        elements: Optional[list[str]] = None,
        layout: str = "1-column",
    ) -> HTMLGenerationResult:
        """
        HTML 와이어프레임 생성

        Args:
            screen_name: 화면 이름
            description: 화면 설명
            elements: 포함할 요소 목록 (header, sidebar, form, table, cards, modal)
            layout: 레이아웃 타입 (1-column, sidebar, 2-column)

        Returns:
            HTMLGenerationResult 객체
        """
        try:
            # 템플릿 로드
            if self.template_path.exists():
                template = self.template_path.read_text(encoding="utf-8")
            else:
                template = self._get_default_template()

            # 플레이스홀더 치환
            html = template.replace("{{title}}", screen_name)
            html = html.replace("{{description}}", description or screen_name)
            html = html.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))

            # 요소 기반 커스터마이징
            if elements:
                html = self._customize_elements(html, elements)

            # 레이아웃 적용
            html = self._apply_layout(html, layout)

            return HTMLGenerationResult(
                success=True,
                html_content=html,
            )

        except Exception as e:
            return HTMLGenerationResult(
                success=False,
                html_content="",
                error_message=str(e),
            )

    def _get_default_template(self) -> str:
        """기본 템플릿 반환"""
        return '''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=720">
  <title>{{title}} - Wireframe</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Space Mono', monospace;
      background: #fff;
      padding: 0;
      margin: 0;
    }
    .container {
      width: auto;
      max-width: 720px;
      height: auto;
      max-height: 1280px;
      margin: 0;
      background: #fff;
      border: 1px solid #e5e5e5;
      box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
      overflow: hidden;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 24px 32px;
      border-bottom: 2px solid #1a1a1a;
      background: #fff;
    }
    .logo-text {
      font-family: 'Space Mono', monospace;
      font-weight: 700;
      font-size: 0.875rem;
      letter-spacing: 0.15em;
      color: #000;
      text-transform: uppercase;
    }
    .header-meta {
      font-family: 'Space Mono', monospace;
      font-size: 0.75rem;
      letter-spacing: 0.05em;
      color: #999;
    }
    .content {
      padding: 48px 32px 64px;
    }
    .subtitle {
      font-family: 'Space Mono', monospace;
      font-size: 0.75rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #999;
      margin-bottom: 16px;
    }
    .title {
      font-family: 'DM Serif Display', serif;
      font-size: 2.5rem;
      font-weight: 400;
      color: #000;
      letter-spacing: -0.02em;
      line-height: 1.1;
      margin-bottom: 24px;
    }
    .description {
      font-family: 'Space Mono', monospace;
      font-size: 0.875rem;
      line-height: 1.6;
      color: #2d2d2d;
      margin-bottom: 48px;
      max-width: 560px;
    }
    .placeholder {
      border: 1px dashed #999;
      padding: 48px 32px;
      background: #f8f8f8;
      display: flex;
      align-items: center;
      justify-content: flex-start;
    }
    .placeholder-label {
      font-family: 'Space Mono', monospace;
      font-size: 0.75rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #666;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <span class="logo-text">WIREFRAME</span>
      <span class="header-meta">{{date}}</span>
    </div>
    <div class="content">
      <p class="subtitle">MOCKUP</p>
      <h1 class="title">{{title}}</h1>
      <p class="description">{{description}}</p>
      <div class="placeholder">
        <span class="placeholder-label">Content Area</span>
      </div>
    </div>
  </div>
</body>
</html>'''

    def _customize_elements(self, html: str, elements: list[str]) -> str:
        """요소 기반 커스터마이징"""
        # 현재는 기본 템플릿 유지
        # 향후 요소별 HTML 블록 주입 가능
        return html

    def _apply_layout(self, html: str, layout: str) -> str:
        """레이아웃 적용"""
        # 현재는 기본 레이아웃 유지
        # 향후 레이아웃별 CSS/HTML 변경 가능
        return html

    def generate_from_prompt(
        self,
        prompt: str,
    ) -> HTMLGenerationResult:
        """
        프롬프트에서 화면 정보 추출하여 생성

        Args:
            prompt: 사용자 프롬프트

        Returns:
            HTMLGenerationResult 객체
        """
        # 간단한 프롬프트 파싱
        # "화면명 - 설명" 또는 "화면명: 설명" 형식 지원
        parts = re.split(r'\s*[-:]\s*', prompt, maxsplit=1)
        screen_name = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else ""

        # 요소 감지 (간단한 키워드 기반)
        elements = []
        prompt_lower = prompt.lower()

        if any(k in prompt_lower for k in ["폼", "form", "입력", "로그인", "login"]):
            elements.append("form")
        if any(k in prompt_lower for k in ["테이블", "table", "목록", "list"]):
            elements.append("table")
        if any(k in prompt_lower for k in ["카드", "card", "그리드", "grid"]):
            elements.append("cards")
        if any(k in prompt_lower for k in ["사이드바", "sidebar", "메뉴"]):
            elements.append("sidebar")

        return self.generate(
            screen_name=screen_name,
            description=description,
            elements=elements if elements else None,
        )
