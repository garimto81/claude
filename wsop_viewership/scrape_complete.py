"""
PokerGO YouTube 채널 WSOP 2025 완전한 데이터 수집
- 제목에 "2025" 포함된 영상
- 제목에 "WSOP Main Event" + 최근 업로드 영상
"""

import asyncio
import json
import re
from playwright.async_api import async_playwright


def parse_exact_views(view_text: str) -> int:
    """정확한 조회수 추출"""
    if not view_text:
        return 0
    numbers = re.findall(r'[\d,]+', view_text)
    if numbers:
        num_str = max(numbers, key=len)
        try:
            return int(num_str.replace(',', ''))
        except ValueError:
            pass
    return 0


def parse_duration_to_minutes(duration_text: str) -> float:
    """재생시간을 분 단위로 변환"""
    if not duration_text:
        return 0
    parts = duration_text.strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
        elif len(parts) == 2:
            return int(parts[0]) + int(parts[1]) / 60
    except ValueError:
        pass
    return 0


def is_recent_upload(metadata: str) -> bool:
    """최근 업로드인지 확인 (8개월 이내)"""
    metadata_lower = metadata.lower()
    if 'ago' in metadata_lower:
        if any(unit in metadata_lower for unit in ['day', 'week', 'hour', 'minute']):
            return True
        if 'month' in metadata_lower:
            match = re.search(r'(\d+)\s*month', metadata_lower)
            if match:
                months = int(match.group(1))
                return months <= 8
    return False


async def scrape_pokergo_streams():
    """PokerGO YouTube 채널 스트림 스크래핑 - 완전판"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = await context.new_page()

        print("PokerGO YouTube 채널 접속 중...")
        await page.goto("https://www.youtube.com/@PokerGO/streams", wait_until="networkidle")
        await asyncio.sleep(5)

        print("영상 목록 로드 중...")
        for i in range(40):
            await page.evaluate("window.scrollBy(0, 2000)")
            await asyncio.sleep(0.5)
            if (i + 1) % 10 == 0:
                print(f"  스크롤 {i+1}/40...")

        await asyncio.sleep(2)

        print("\n영상 정보 추출 중...")

        videos_data = await page.evaluate("""
            () => {
                const videos = [];
                const videoElements = document.querySelectorAll('ytd-rich-item-renderer, ytd-grid-video-renderer');

                videoElements.forEach(el => {
                    try {
                        const titleEl = el.querySelector('#video-title, a#video-title');
                        const title = titleEl ? (titleEl.getAttribute('title') || titleEl.textContent || '').trim() : '';
                        const href = titleEl ? (titleEl.href || titleEl.getAttribute('href') || '') : '';

                        const metaEl = el.querySelector('#metadata-line');
                        const metadata = metaEl ? metaEl.innerText : '';

                        const timeEl = el.querySelector('ytd-thumbnail-overlay-time-status-renderer #text');
                        const duration = timeEl ? timeEl.innerText.trim() : '';

                        if (title && href) {
                            let url = href;
                            if (!href.startsWith('http')) {
                                url = 'https://www.youtube.com' + href;
                            }
                            videos.push({
                                title: title,
                                url: url,
                                metadata: metadata,
                                duration: duration
                            });
                        }
                    } catch (e) {}
                });

                return videos;
            }
        """)

        print(f"총 {len(videos_data)}개 영상 발견")

        # WSOP 2025 필터링 (확장된 기준)
        wsop_2025_videos = []
        seen_titles = set()

        for v in videos_data:
            title = v.get('title', '')
            title_lower = title.lower()

            # WSOP 키워드 확인
            if 'wsop' not in title_lower:
                continue

            # 중복 체크
            if title in seen_titles:
                continue

            duration_text = v.get('duration', '')
            duration_minutes = parse_duration_to_minutes(duration_text)

            # 1시간 이상
            if duration_minutes < 60:
                continue

            metadata = v.get('metadata', '')

            # 2025 영상 판정 기준:
            # 1. 제목에 "2025" 포함
            # 2. 제목에 "WSOP Main Event" 포함 + 최근 업로드
            # 3. 제목에 특정 2025 이벤트 키워드 포함 + 최근 업로드

            is_2025 = False

            if '2025' in title:
                is_2025 = True
            elif 'main event' in title_lower and is_recent_upload(metadata):
                # Main Event는 연 1회이므로 최근 업로드면 2025
                is_2025 = True
            elif is_recent_upload(metadata) and any(kw in title_lower for kw in [
                'daniel negreanu', 'phil hellmuth', 'michael mizrachi',
                'bryn kenney', 'nick schulman', 'phil ivey'
            ]):
                # 유명 선수 + WSOP + 최근 업로드
                is_2025 = True

            if not is_2025:
                continue

            seen_titles.add(title)
            wsop_2025_videos.append({
                'title': title,
                'url': v.get('url', ''),
                'duration': duration_text,
                'duration_minutes': duration_minutes,
                'metadata': metadata
            })

        print(f"\nWSOP 2025 (1시간+) 영상: {len(wsop_2025_videos)}개")

        # 개별 영상에서 정확한 조회수 수집
        if wsop_2025_videos:
            print("\n개별 영상 조회수 수집 중...")
            detail_page = await context.new_page()

            for i, video in enumerate(wsop_2025_videos):
                title_short = video['title'][:45] + "..." if len(video['title']) > 45 else video['title']
                print(f"  [{i+1}/{len(wsop_2025_videos)}] {title_short}")

                if not video.get('url'):
                    video['views'] = 0
                    print(f"    -> URL 없음")
                    continue

                try:
                    await detail_page.goto(video['url'], wait_until="domcontentloaded", timeout=20000)
                    await asyncio.sleep(1.5)

                    view_text = await detail_page.evaluate("""
                        () => {
                            const meta = document.querySelector('meta[itemprop="interactionCount"]');
                            if (meta) return meta.content;

                            const viewEl = document.querySelector('ytd-video-view-count-renderer span.view-count');
                            if (viewEl) return viewEl.innerText;

                            const info = document.querySelector('#info span.view-count');
                            if (info) return info.innerText;

                            return '';
                        }
                    """)

                    views = parse_exact_views(view_text)
                    video['views'] = views
                    print(f"    -> {views:,} views")

                except Exception as e:
                    video['views'] = 0
                    print(f"    -> 오류: {str(e)[:30]}")

                await asyncio.sleep(0.3)

            await detail_page.close()

        await browser.close()
        return wsop_2025_videos


async def main():
    videos = await scrape_pokergo_streams()

    # 조회수 기준 정렬
    videos_sorted = sorted(videos, key=lambda x: x.get('views', 0), reverse=True)

    total_views = sum(v.get('views', 0) for v in videos)
    videos_with_views = [v for v in videos if v.get('views', 0) > 0]

    print("\n" + "=" * 100)
    print("WSOP 2025 영상 분석 결과 (1시간 이상)")
    print("=" * 100)

    print(f"\n총 영상 수: {len(videos)}개")
    print(f"조회수 확인된 영상: {len(videos_with_views)}개")
    print(f"총 조회수: {total_views:,} views")

    print("\n[조회수 TOP 10]")
    print("-" * 100)
    for i, v in enumerate(videos_sorted[:10], 1):
        print(f"{i}. {v['title'][:70]}")
        print(f"   {v['duration']} | {v['views']:,} views")

    # JSON 저장
    with open('wsop_2025_complete.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_videos': len(videos),
            'videos_with_views': len(videos_with_views),
            'total_views': total_views,
            'videos': videos_sorted
        }, f, ensure_ascii=False, indent=2)

    print(f"\n데이터가 wsop_2025_complete.json에 저장되었습니다.")


if __name__ == "__main__":
    asyncio.run(main())
