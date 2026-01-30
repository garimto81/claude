"""
목업 내보내기 유틸리티

HTML 파일 저장, Playwright 스크린샷, PRD 연결 등을 처리합니다.
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# Playwright Python SDK 사용 가능 여부
_PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    _PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass


def save_html(
    content: str,
    output_path: Path,
    title: str = "Mockup",
    description: str = "",
) -> Path:
    """
    HTML 콘텐츠를 파일로 저장

    Args:
        content: HTML 콘텐츠
        output_path: 저장 경로
        title: 문서 제목
        description: 문서 설명

    Returns:
        저장된 파일 경로
    """
    # 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 플레이스홀더 치환
    content = content.replace("{{title}}", title)
    content = content.replace("{{description}}", description)
    content = content.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))

    # 파일 저장
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"HTML 저장: {output_path}")

    return output_path


def capture_screenshot(
    html_path: Path,
    image_path: Path,
    selector: Optional[str] = None,
    full_page: bool = False,
    width: int = 800,
    height: int = 600,
    auto_size: bool = True,
) -> Optional[Path]:
    """
    Playwright로 HTML 스크린샷 캡처

    Args:
        html_path: HTML 파일 경로
        image_path: 출력 이미지 경로
        selector: 캡처할 요소 선택자 (없으면 전체)
        full_page: 전체 페이지 캡처 여부
        width: 뷰포트 너비 (auto_size=False일 때 사용)
        height: 뷰포트 높이 (auto_size=False일 때 사용)
        auto_size: 콘텐츠 크기에 맞춰 자동 캡처 (기본값: True)

    Returns:
        캡처된 이미지 경로 (실패 시 None)
    """
    # 디렉토리 생성
    image_path.parent.mkdir(parents=True, exist_ok=True)

    # auto_size=True이고 Playwright SDK가 사용 가능하면 SDK 사용
    if auto_size and _PLAYWRIGHT_AVAILABLE:
        return _capture_with_auto_size(html_path, image_path, selector)

    # 폴백: CLI 사용
    return _capture_with_cli(
        html_path, image_path, selector, full_page, width, height
    )


def _capture_with_auto_size(
    html_path: Path,
    image_path: Path,
    selector: Optional[str] = None,
) -> Optional[Path]:
    """
    Playwright Python SDK로 콘텐츠 크기에 맞춰 자동 캡처

    동작 방식:
    1. 넓은 viewport로 페이지 로드 (콘텐츠가 잘리지 않도록)
    2. body의 실제 렌더링된 크기 감지 (getBoundingClientRect)
    3. viewport를 콘텐츠 크기에 맞게 조정
    4. 캡처 실행
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            # 적절한 초기 viewport (목업에 적합한 너비, 높이는 충분히)
            page = browser.new_page(viewport={"width": 900, "height": 2000})

            # file:// URL로 변환
            file_url = html_path.resolve().as_uri()
            page.goto(file_url)
            page.wait_for_load_state("networkidle")

            # 실제 콘텐츠 크기 감지 (getBoundingClientRect 사용)
            # body의 실제 렌더링된 높이와 너비를 정확하게 측정
            dimensions = page.evaluate("""
                () => {
                    const allElements = document.body.querySelectorAll('*');

                    let minLeft = Infinity;
                    let maxRight = 0;
                    let maxBottom = 0;

                    allElements.forEach(el => {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);

                        // 보이는 요소만 측정 (display:none, visibility:hidden 제외)
                        if (rect.width > 0 && rect.height > 0 &&
                            style.display !== 'none' && style.visibility !== 'hidden') {
                            if (rect.left < minLeft) minLeft = rect.left;
                            if (rect.right > maxRight) maxRight = rect.right;
                            if (rect.bottom > maxBottom) maxBottom = rect.bottom;
                        }
                    });

                    // scrollHeight와 offsetHeight 비교
                    const scrollH = Math.max(
                        document.documentElement.scrollHeight,
                        document.body.scrollHeight
                    );
                    const offsetH = Math.max(
                        document.documentElement.offsetHeight,
                        document.body.offsetHeight
                    );

                    // 콘텐츠 실제 너비 (최소 800px, 최대 1400px)
                    let contentWidth = maxRight - Math.max(0, minLeft);
                    contentWidth = Math.min(Math.max(contentWidth, 800), 1400);

                    // 높이: 가장 아래 요소의 bottom 사용 (더 정확)
                    const height = Math.max(maxBottom, offsetH);

                    return {
                        width: contentWidth,
                        height,
                        scrollH,
                        offsetH,
                        maxBottom,
                        minLeft,
                        maxRight
                    };
                }
            """)

            content_width = dimensions['width']
            content_height = dimensions['height']

            logger.info(
                f"콘텐츠 크기 감지: {content_width}x{content_height} "
                f"(scrollH={dimensions['scrollH']}, offsetH={dimensions['offsetH']}, "
                f"maxBottom={dimensions['maxBottom']})"
            )

            # 최소 크기 보장 (너무 작으면 잘못 감지된 것)
            final_width = max(int(content_width), 400)
            final_height = max(int(content_height), 300)

            # viewport 조정 후 다시 로드
            page.set_viewport_size({"width": final_width, "height": final_height})
            page.goto(file_url)
            page.wait_for_load_state("networkidle")

            # 스크린샷 캡처
            if selector:
                element = page.query_selector(selector)
                if element:
                    element.screenshot(path=str(image_path))
                else:
                    logger.warning(f"선택자 '{selector}'를 찾을 수 없음, 전체 페이지 캡처")
                    page.screenshot(path=str(image_path), full_page=False)
            else:
                page.screenshot(path=str(image_path), full_page=False)

            browser.close()

            logger.info(f"스크린샷 캡처 (auto_size): {image_path} [{final_width}x{final_height}]")
            return image_path

    except ImportError:
        logger.warning("Playwright SDK 없음, CLI로 폴백")
        return None
    except Exception as e:
        logger.error(f"auto_size 캡처 실패: {e}")
        return None


def _capture_with_cli(
    html_path: Path,
    image_path: Path,
    selector: Optional[str] = None,
    full_page: bool = False,
    width: int = 800,
    height: int = 600,
) -> Optional[Path]:
    """Playwright CLI로 스크린샷 캡처 (폴백용)"""
    # file:// URL로 변환
    file_url = html_path.resolve().as_uri()

    # Playwright 명령어 구성
    cmd = ["npx", "playwright", "screenshot"]

    if selector:
        cmd.extend(["--selector", selector])

    if full_page:
        cmd.append("--full-page")

    cmd.extend([
        "--viewport-size", f"{width},{height}",
        str(file_url),
        str(image_path),
    ])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            logger.info(f"스크린샷 캡처 (CLI): {image_path}")
            return image_path
        else:
            logger.error(f"Playwright CLI 오류: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        logger.error("Playwright 타임아웃")
        return None
    except FileNotFoundError:
        logger.error("Playwright가 설치되지 않음. 'npx playwright install' 실행 필요")
        return None
    except Exception as e:
        logger.error(f"스크린샷 캡처 실패: {e}")
        return None


def generate_markdown_embed(
    image_path: Path,
    html_path: Path,
    alt_text: str,
    relative_to: Optional[Path] = None,
) -> str:
    """
    Markdown 문서에 삽입할 코드 생성

    Args:
        image_path: 이미지 경로
        html_path: HTML 파일 경로
        alt_text: 이미지 대체 텍스트
        relative_to: 상대 경로 기준 디렉토리

    Returns:
        Markdown 삽입 코드
    """
    if relative_to:
        try:
            img_rel = image_path.relative_to(relative_to)
            html_rel = html_path.relative_to(relative_to)
        except ValueError:
            img_rel = image_path
            html_rel = html_path
    else:
        img_rel = image_path
        html_rel = html_path

    # POSIX 경로 형식으로 변환
    img_rel_str = str(img_rel).replace("\\", "/")
    html_rel_str = str(html_rel).replace("\\", "/")

    return f"""![{alt_text}]({img_rel_str})
[HTML 원본]({html_rel_str})"""


def get_output_paths(
    name: str,
    prd: Optional[str] = None,
    suffix: str = "",
    mockup_dir: Path = Path("docs/mockups"),
    image_dir: Path = Path("docs/images/mockups"),
) -> tuple[Path, Path]:
    """
    출력 파일 경로 생성

    Args:
        name: 목업 이름
        prd: PRD 번호 (있으면 하위 폴더 사용)
        suffix: 파일명 접미사 (예: "-hifi")
        mockup_dir: 목업 기본 디렉토리
        image_dir: 이미지 기본 디렉토리

    Returns:
        (html_path, image_path) 튜플
    """
    # 파일명 생성 (공백을 하이픈으로)
    safe_name = name.lower().replace(" ", "-").replace("_", "-")

    # 한글 처리 (간단히 유지)
    import re
    safe_name = re.sub(r'[^\w\-]', '', safe_name, flags=re.UNICODE)

    filename = f"{safe_name}{suffix}"

    if prd:
        html_path = mockup_dir / prd / f"{filename}.html"
        image_path = image_dir / prd / f"{filename}.png"
    else:
        html_path = mockup_dir / f"{filename}.html"
        image_path = image_dir / f"{filename}.png"

    return html_path, image_path
