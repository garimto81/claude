"""
Mockup Hybrid - HTML 와이어프레임 + Google Stitch 하이브리드 목업 생성 시스템

이 모듈은 프롬프트 분석 기반으로 최적의 목업 생성 백엔드를 자동 선택합니다.

주요 기능:
- 프롬프트 분석 기반 자동 백엔드 선택
- HTML 와이어프레임 생성
- Google Stitch API 연동
- Playwright 스크린샷
- 폴백 처리

사용 예시:
    from lib.mockup_hybrid import MockupGenerator

    generator = MockupGenerator()
    result = generator.generate(
        name="로그인 화면",
        options={"bnw": True}
    )
    print(result.html_path)
    print(result.image_path)
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


__version__ = "2.0.0"
__all__ = [
    "MockupBackend",
    "MockupResult",
    "SelectionReason",
    "MockupOptions",
]


class MockupBackend(Enum):
    """목업 생성 백엔드"""
    HTML = "html"
    STITCH = "stitch"
    MERMAID = "mermaid"


class SelectionReason(Enum):
    """백엔드 선택 이유"""
    FORCE_HTML = "강제 HTML 옵션"
    FORCE_HIFI = "강제 Stitch 옵션"
    HIFI_KEYWORD = "고품질 키워드 감지"
    HTML_KEYWORD = "빠른/구조 키워드 감지"
    PRD_LINKED = "PRD 연결"
    MULTI_SCREEN = "다중 화면 (빠른 생성)"
    API_UNAVAILABLE = "Stitch API 불가"
    RATE_LIMITED = "Rate Limit 초과"
    FORCE_MERMAID = "강제 Mermaid 옵션"
    MERMAID_KEYWORD = "다이어그램 키워드 감지"
    DEFAULT = "기본값 (HTML)"
    FALLBACK = "Stitch 실패 → HTML 폴백"


@dataclass
class MockupOptions:
    """목업 생성 옵션"""
    bnw: bool = True
    force_html: bool = False
    force_hifi: bool = False
    force_mermaid: bool = False
    screens: int = 1
    prd: Optional[str] = None
    flow: bool = False
    style: str = "wireframe"


@dataclass
class MockupResult:
    """목업 생성 결과"""
    backend: MockupBackend
    reason: SelectionReason
    html_path: Optional[Path]
    image_path: Optional[Path]
    success: bool
    message: str
    fallback_used: bool = False
    mermaid_code: Optional[str] = None

    def __str__(self) -> str:
        status = "✅" if self.success else "❌"

        if self.backend == MockupBackend.MERMAID:
            backend_emoji = "📊"
        elif self.backend == MockupBackend.STITCH:
            backend_emoji = "🤖"
        else:
            backend_emoji = "📝"

        lines = [
            f"{backend_emoji} 선택: {self.backend.value.upper()} (이유: {self.reason.value})",
        ]

        if self.fallback_used:
            lines.insert(0, "⚠️ Stitch API 실패 → HTML로 폴백")

        lines.append(f"{status} 생성: {self.html_path}")

        if self.image_path:
            lines.append(f"📸 캡처: {self.image_path}")

        if self.mermaid_code:
            lines.append("")
            lines.append("```mermaid")
            lines.append(self.mermaid_code)
            lines.append("```")

        return "\n".join(lines)


# 기본 경로 설정
DEFAULT_MOCKUP_DIR = Path("docs/mockups")
DEFAULT_IMAGE_DIR = Path("docs/images/mockups")
