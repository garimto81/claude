"""
PokerGO YouTube 채널에서 WSOP 2025 관련 영상 데이터 수집
한글/영어 메타데이터 지원
"""

import asyncio
import re
from playwright.async_api import async_playwright


def parse_views(view_text: str) -> int:
    """조회수 텍스트를 숫자로 변환 (한글/영어 지원)"""
    if not view_text:
        return 0

    # 원본 텍스트에서 숫자와 단위 추출
    text = view_text.lower()

    # 한글 "회" 또는 영어 "views" 제거
    text = re.sub(r"(조회수|회|views?|view|\s)", "", text)

    # K/M/만/억 처리
    multiplier = 1
    if "k" in text:
        multiplier = 1000
        text = text.replace("k", "")
    elif "m" in text:
        multiplier = 1000000
        text = text.replace("m", "")
    elif "만" in text:
        multiplier = 10000
        text = text.replace("만", "")
    elif "억" in text:
        multiplier = 100000000
        text = text.replace("억", "")

    # 쉼표 제거
    text = text.replace(",", "").replace(".", ".").strip()

    try:
        return int(float(text) * multiplier)
    except ValueError:
        return 0


def parse_duration_to_minutes(duration_text: str) -> float:
    """재생시간을 분 단위로 변환"""
    if not duration_text:
        return 0

    parts = duration_text.strip().split(":")
    try:
        if len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
        elif len(parts) == 2:  # MM:SS
            return int(parts[0]) + int(parts[1]) / 60
        else:
            return 0
    except ValueError:
        return 0


def is_2025_video(date_text: str, title: str = "") -> bool:
    """2025년 영상인지 확인 (현재 2026년 1월 기준)"""
    # 제목에 2025가 있으면 2025년 영상
    if "2025" in title:
        return True

    if not date_text:
        return False

    date_lower = date_text.lower()

    # 명시적으로 2025가 포함된 경우
    if "2025" in date_text:
        return True

    # 영어: "X months ago", "X days ago" 등
    if "ago" in date_lower:
        if any(unit in date_lower for unit in ["day", "week", "hour", "minute"]):
            return True
        if "month" in date_lower:
            match = re.search(r"(\d+)\s*month", date_lower)
            if match:
                months = int(match.group(1))
                return months <= 8
        if "year" in date_lower:
            return False

    # 한글: "X개월 전", "X일 전" 등
    if "전" in date_text:
        if any(unit in date_text for unit in ["일", "주", "시간", "분"]):
            return True
        if "개월" in date_text:
            match = re.search(r"(\d+)\s*개월", date_text)
            if match:
                months = int(match.group(1))
                return months <= 8
        if "년" in date_text:
            match = re.search(r"(\d+)\s*년", date_text)
            if match:
                years = int(match.group(1))
                return years == 0

    return False


async def scrape_pokergo_streams():
    """PokerGO YouTube 채널 스트림 스크래핑"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",  # 영어로 설정하여 일관된 형식 유지
        )
        page = await context.new_page()

        print("PokerGO YouTube 채널 접속 중...")
        await page.goto(
            "https://www.youtube.com/@PokerGO/streams", wait_until="networkidle"
        )
        await asyncio.sleep(5)

        # 스크롤해서 더 많은 영상 로드
        print("영상 목록 로드 중 (스크롤)...")
        for i in range(30):
            await page.evaluate("window.scrollBy(0, 2000)")
            await asyncio.sleep(0.7)
            if (i + 1) % 10 == 0:
                print(f"  스크롤 {i+1}/30...")

        await asyncio.sleep(2)

        # JavaScript로 영상 데이터 추출
        print("\n영상 정보 추출 중...")

        videos_data = await page.evaluate("""
            () => {
                const videos = [];
                const videoElements = document.querySelectorAll('ytd-rich-item-renderer, ytd-grid-video-renderer, ytd-video-renderer');

                videoElements.forEach(el => {
                    try {
                        const titleEl = el.querySelector('#video-title, #video-title-link, a#video-title');
                        const title = titleEl ? (titleEl.getAttribute('title') || titleEl.textContent || '').trim() : '';

                        const metaEl = el.querySelector('#metadata-line, #metadata');
                        const metadata = metaEl ? metaEl.innerText : '';

                        // 모든 span에서 데이터 추출
                        const allText = el.innerText || '';

                        const timeEl = el.querySelector('ytd-thumbnail-overlay-time-status-renderer #text, span.ytd-thumbnail-overlay-time-status-renderer, [id="text"].ytd-thumbnail-overlay-time-status-renderer');
                        const duration = timeEl ? timeEl.innerText.trim() : '';

                        if (title) {
                            videos.push({
                                title: title,
                                metadata: metadata,
                                allText: allText,
                                duration: duration
                            });
                        }
                    } catch (e) {}
                });

                return videos;
            }
        """)

        print(f"총 {len(videos_data)}개 영상 추출됨\n")

        # WSOP 필터링 및 조건 적용
        all_wsop = []
        matching = []
        total_views = 0

        for v in videos_data:
            title = v.get("title", "")
            if "wsop" not in title.lower():
                continue

            duration_text = v.get("duration", "")
            duration_minutes = parse_duration_to_minutes(duration_text)

            # 메타데이터에서 조회수 추출
            metadata = v.get("metadata", "") or v.get("allText", "")

            # 조회수 추출 (여러 패턴 지원)
            views = 0
            # 영어: "123K views", "1.2M views"
            views_match = re.search(r"([\d,.]+)\s*([KkMm])?\s*views?", metadata)
            if views_match:
                num = views_match.group(1)
                unit = views_match.group(2) or ""
                views = parse_views(f"{num}{unit}")

            # 한글: "조회수 123만회", "조회수 1.2K회"
            if views == 0:
                views_match = re.search(
                    r"조회수\s*([\d,.]+)\s*([KkMm만억])?\s*회?", metadata
                )
                if views_match:
                    num = views_match.group(1)
                    unit = views_match.group(2) or ""
                    views = parse_views(f"{num}{unit}")

            # 2025년 체크 (제목 + 메타데이터)
            is_2025 = is_2025_video(metadata, title)

            video_info = {
                "title": title,
                "duration": duration_text,
                "duration_minutes": duration_minutes,
                "views": views,
                "metadata": metadata[:100],
                "is_2025": is_2025,
                "is_long": duration_minutes >= 60,
            }
            all_wsop.append(video_info)

            if is_2025 and duration_minutes >= 60:
                matching.append(video_info)
                total_views += views

        await browser.close()

        return all_wsop, matching, total_views


async def main():
    all_wsop, filtered, total = await scrape_pokergo_streams()

    print("\n" + "=" * 130)
    print("WSOP 영상 전체 목록 (키워드 매칭)")
    print("=" * 130)

    if all_wsop:
        print(
            f"\n{'#':<4} {'제목':<55} {'시간':<12} {'조회수':>15} {'2025':>6} {'1h+':>5}"
        )
        print("-" * 130)

        for i, v in enumerate(all_wsop, 1):
            title_short = (
                v["title"][:52] + "..." if len(v["title"]) > 55 else v["title"]
            )
            print(
                f"{i:<4} {title_short:<55} {v['duration']:<12} {v['views']:>15,} {'Y' if v['is_2025'] else 'N':>6} {'Y' if v['is_long'] else 'N':>5}"
            )

        print(f"\n총 {len(all_wsop)}개 WSOP 영상 발견")

    print("\n" + "=" * 130)
    print("WSOP 2025 영상 분석 결과 (1시간 이상)")
    print("=" * 130)

    if not filtered:
        print("\n조건에 맞는 영상을 찾지 못했습니다.")
        if all_wsop:
            print("\n[디버그] 상위 10개 영상:")
            for v in all_wsop[:10]:
                print(f"  제목: {v['title'][:50]}")
                print(
                    f"    시간: {v['duration']} ({v['duration_minutes']:.0f}분) | 조회수: {v['views']:,} | 2025: {v['is_2025']}"
                )
                print(f"    메타: {v['metadata'][:60]}")
                print()
        return

    print(f"\n{'#':<4} {'제목':<65} {'시간':<12} {'조회수':>15}")
    print("-" * 100)

    for i, v in enumerate(filtered, 1):
        title_short = v["title"][:62] + "..." if len(v["title"]) > 65 else v["title"]
        print(f"{i:<4} {title_short:<65} {v['duration']:<12} {v['views']:>15,}")

    print("-" * 100)
    print(f"\n총 영상 수: {len(filtered)}개")
    print(f"총 조회수 합계: {total:,} views")
    print("=" * 130)


if __name__ == "__main__":
    asyncio.run(main())
