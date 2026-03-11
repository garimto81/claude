"""Figma capture headless 래퍼 — start "" 브라우저 호출 대체"""

from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger(__name__)


def figma_headless_capture(url: str, delay_ms: int = 5000) -> bool:
    """
    Playwright headless로 Figma capture URL 로드.
    capture.js가 DOM 캡처 + MCP endpoint로 전송.

    Args:
        url: Figma capture URL (hash 파라미터 포함)
        delay_ms: capture.js 실행 대기 시간 (ms)

    Returns:
        True if page loaded successfully
    """
    if not url.startswith(("http://", "https://", "file://")):
        logger.error(f"Invalid URL scheme: {url[:80]}")
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                context = browser.new_context(
                    viewport={"width": 720, "height": 1280},
                    device_scale_factor=1,
                )
                page = context.new_page()
                page.goto(url)
                page.wait_for_load_state("networkidle")
                # capture.js의 DOM 캡처 + MCP 전송 완료 대기
                page.wait_for_timeout(delay_ms)
                logger.info(f"Figma headless capture 완료: {url[:80]}...")
                return True
            finally:
                browser.close()
    except Exception as e:
        logger.error(f"Figma headless capture 실패: {e}")
        return False
