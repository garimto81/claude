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
    from playwright.sync_api import sync_playwright  # noqa: F401
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
    width: int = 720,
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
        result = _capture_with_auto_size(html_path, image_path, selector)
        if result and not _validate_capture(result):
            logger.warning("공백 과다 감지, selector='#q-app'으로 재캡처")
            result = _capture_with_auto_size(html_path, image_path, selector="#q-app")
        if result and not _validate_capture(result):
            logger.warning("재캡처도 공백 과다, crop 시도")
            result = _crop_whitespace(result)
        return result

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

    전략 우선순위:
    1. selector 파라미터 → 해당 요소만 캡처
    2. body 첫 번째 자식 요소 → element.screenshot() (정확한 콘텐츠 영역)
    3. 폴백 → body.getBoundingClientRect()로 크기 측정 후 캡처

    NOTE: scrollHeight는 viewport 크기 이상을 반환하므로 사용하지 않는다.
    element.screenshot()이 요소의 렌더링된 bounding box만 정확히 캡처한다.
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
            )
            # 초기 viewport: 콘텐츠 로드용 (CSS max-width/max-height가 렌더링 크기 제어)
            context = browser.new_context(
                viewport={"width": 720, "height": 800},
                device_scale_factor=1,
            )
            page = context.new_page()

            # file:// URL로 변환
            file_url = html_path.resolve().as_uri()
            page.goto(file_url)
            page.wait_for_load_state("networkidle")

            # === 전략 1: selector 파라미터 사용 ===
            if selector:
                element = page.query_selector(selector)
                if element:
                    element.screenshot(path=str(image_path))
                    browser.close()
                    logger.info(f"스크린샷 캡처 (selector: {selector}): {image_path}")
                    return image_path
                logger.warning(f"선택자 '{selector}'를 찾을 수 없음, .container 탐색")

            # === 전략 2: body 첫 번째 자식 요소 캡처 ===
            # .app, .wrapper 등 최상위 래퍼를 클래스명 무관하게 찾음
            root_element = page.query_selector("body > *:first-child")
            if root_element:
                root_element.screenshot(path=str(image_path))
                browser.close()
                logger.info(f"스크린샷 캡처 (root element): {image_path}")
                return image_path

            # === 전략 3: CSS 제약 해제 후 실제 콘텐츠 크기 측정 ===
            dimensions = page.evaluate("""
                () => {
                    const body = document.body;
                    const html = document.documentElement;

                    // 원래 스타일 저장
                    const origBodyMaxH = body.style.maxHeight;
                    const origBodyOverflow = body.style.overflow;
                    const origHtmlMaxH = html.style.maxHeight;
                    const origHtmlOverflow = html.style.overflow;

                    // CSS max-height/overflow 제약 임시 해제
                    body.style.maxHeight = 'none';
                    body.style.overflow = 'visible';
                    html.style.maxHeight = 'none';
                    html.style.overflow = 'visible';

                    // 실제 콘텐츠 크기 측정
                    const rect = body.getBoundingClientRect();
                    const scrollW = Math.max(rect.width, body.scrollWidth);
                    const scrollH = Math.max(rect.height, body.scrollHeight);

                    // 스타일 복원
                    body.style.maxHeight = origBodyMaxH;
                    body.style.overflow = origBodyOverflow;
                    html.style.maxHeight = origHtmlMaxH;
                    html.style.overflow = origHtmlOverflow;

                    return {
                        width: Math.ceil(scrollW),
                        height: Math.ceil(scrollH)
                    };
                }
            """)

            content_width = max(min(int(dimensions['width']), 720), 50)
            content_height = max(min(int(dimensions['height']), 1280), 50)

            logger.info(f"콘텐츠 크기 감지 (폴백): {content_width}x{content_height}")

            # viewport를 콘텐츠 크기에 맞게 조정
            page.set_viewport_size({"width": content_width, "height": content_height})
            page.wait_for_timeout(100)

            page.screenshot(path=str(image_path), full_page=False)
            browser.close()

            logger.info(f"스크린샷 캡처 (폴백 auto_size): {image_path} [{content_width}x{content_height}]")
            return image_path

    except ImportError:
        logger.warning("Playwright SDK 없음, CLI로 폴백")
        return None
    except Exception as e:
        logger.error(f"auto_size 캡처 실패: {e}")
        return None


def _validate_capture(image_path: Path, max_whitespace_ratio: float = 0.4) -> bool:
    """캡처 이미지의 하단 공백 비율 검증

    Args:
        image_path: 검증할 이미지 경로
        max_whitespace_ratio: 허용 최대 공백 비율 (기본 0.4)

    Returns:
        True if valid (공백 비율이 임계값 이하)
    """
    try:
        from PIL import Image
    except ImportError:
        return True  # Pillow 없으면 항상 통과 (soft dependency)

    try:
        img = Image.open(image_path)
        width, height = img.size

        # 하단 30% 영역 검사
        check_height = int(height * 0.3)
        if check_height < 10:
            return True

        bottom_region = img.crop((0, height - check_height, width, height))
        pixels = list(bottom_region.getdata())

        if not pixels:
            return True

        # 가장 많은 색상 = 배경색으로 추정
        from collections import Counter
        color_counts = Counter(pixels)
        most_common_color, most_common_count = color_counts.most_common(1)[0]

        ratio = most_common_count / len(pixels)
        if ratio > max_whitespace_ratio:
            logger.warning(f"하단 공백 비율 {ratio:.1%} > {max_whitespace_ratio:.0%}")
            return False
        return True
    except Exception as e:
        logger.warning(f"캡처 검증 실패 (무시): {e}")
        return True


def _crop_whitespace(image_path: Path) -> Optional[Path]:
    """이미지 하단 공백을 잘라내는 최후 수단

    Args:
        image_path: crop 대상 이미지 경로

    Returns:
        crop된 이미지 경로 (실패 시 원본 경로)
    """
    try:
        from PIL import Image
    except ImportError:
        return image_path  # Pillow 없으면 원본 반환

    try:
        img = Image.open(image_path)
        # getbbox()로 비어있지 않은 영역 탐지
        bbox = img.getbbox()
        if bbox:
            cropped = img.crop(bbox)
            cropped.save(image_path)
            logger.info(f"공백 crop 완료: {img.size} → {cropped.size}")
        return image_path
    except Exception as e:
        logger.warning(f"crop 실패 (원본 유지): {e}")
        return image_path


def _capture_with_cli(
    html_path: Path,
    image_path: Path,
    selector: Optional[str] = None,
    full_page: bool = False,
    width: int = 720,
    height: int = 600,
) -> Optional[Path]:
    """Playwright CLI로 스크린샷 캡처 (폴백용)"""
    import platform

    # file:// URL로 변환
    file_url = html_path.resolve().as_uri()

    # Playwright 명령어 구성 (Windows: cmd /c npx 패턴 필수)
    if platform.system() == "Windows":
        cmd = ["cmd", "/c", "npx", "playwright", "screenshot"]
    else:
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

    # 한글 + 유니코드 보존 (가-힣 명시 추가)
    import re
    safe_name = re.sub(r'[^\w가-힣\-]', '', safe_name, flags=re.UNICODE)

    # 빈 문자열 폴백 (한국어만 포함된 이름이 모두 제거되는 경우 방지)
    if not safe_name:
        safe_name = "mockup"

    filename = f"{safe_name}{suffix}"

    if prd:
        html_path = mockup_dir / prd / f"{filename}.html"
        image_path = image_dir / prd / f"{filename}.png"
    else:
        html_path = mockup_dir / f"{filename}.html"
        image_path = image_dir / f"{filename}.png"

    return html_path, image_path


def capture_url(url: str, delay_ms: int = 5000,
                width: int = 720, height: int = 1280) -> bool:
    """URL 기반 Playwright headless 캡처 (구 figma_headless_capture 대체)

    Args:
        url: 캡처할 URL (http/https/file)
        delay_ms: 페이지 로드 후 대기 시간 (ms)
        width: 뷰포트 너비
        height: 뷰포트 높이

    Returns:
        True if 성공
    """
    if not url.startswith(("http://", "https://", "file://")):
        logger.error(f"Invalid URL scheme: {url[:80]}")
        return False

    if not _PLAYWRIGHT_AVAILABLE:
        logger.error("Playwright SDK 미설치, capture_url 불가")
        return False

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                )
                page = context.new_page()
                page.goto(url)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(delay_ms)
                logger.info(f"URL 캡처 완료: {url[:80]}...")
                return True
            finally:
                browser.close()
    except Exception as e:
        logger.error(f"URL 캡처 실패: {e}")
        return False
