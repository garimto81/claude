"""
HTML 시안 스크린샷 캡처 스크립트
Playwright를 사용하여 HTML 파일들을 PNG로 캡처합니다.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# 경로 설정
MOCKUPS_DIR = Path(r"D:\AI\claude01\ggp_heritage_mall\design\mockups")
SCREENSHOTS_DIR = Path(r"D:\AI\claude01\ggp_heritage_mall\design\screenshots")


async def capture_screenshots():
    """HTML 시안들을 스크린샷으로 캡처"""
    # 스크린샷 디렉토리 생성
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    # 캡처할 HTML 파일 목록
    html_files = [
        ("01-landing-page.html", "01-landing-page.png", 1920, 1080),
        ("02-product-list.html", "02-product-list.png", 1920, 1400),
        ("03-checkout.html", "03-checkout.png", 1920, 1080),
        ("04-admin-dashboard.html", "04-admin-dashboard.png", 1920, 1080),
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        for html_file, screenshot_name, width, height in html_files:
            html_path = MOCKUPS_DIR / html_file
            screenshot_path = SCREENSHOTS_DIR / screenshot_name

            if not html_path.exists():
                print(f"파일 없음: {html_path}")
                continue

            print(f"캡처 중: {html_file}...")

            # 새 페이지 생성
            page = await browser.new_page(viewport={"width": width, "height": height})

            # HTML 파일 로드
            await page.goto(f"file:///{html_path.as_posix()}")

            # 페이지 로딩 대기
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)  # 폰트 로딩 대기

            # 스크린샷 캡처 (전체 페이지)
            await page.screenshot(path=str(screenshot_path), full_page=True)

            print(f"저장됨: {screenshot_path}")

            await page.close()

        await browser.close()

    print("\n모든 스크린샷 캡처 완료!")
    print(f"저장 위치: {SCREENSHOTS_DIR}")


if __name__ == "__main__":
    asyncio.run(capture_screenshots())
