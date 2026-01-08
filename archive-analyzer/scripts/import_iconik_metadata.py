"""iconik 메타데이터 CSV 임포트 스크립트

iconik에서 추출한 클립 메타데이터를 archive.db에 임포트합니다.
파일명 퍼지 매칭을 통해 기존 files 테이블과 연결합니다.
"""

import csv
import sys
import logging
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any

# 프로젝트 src 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from archive_analyzer.database import Database

# rapidfuzz가 있으면 퍼지 매칭 사용
try:
    from rapidfuzz import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    print("Warning: rapidfuzz not installed. Fuzzy matching disabled.")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# CSV 컬럼 → DB 필드 매핑
COLUMN_MAPPING = {
    'id': 'iconik_id',
    'title': 'title',
    'Description': 'description',
    'time_start_ms': 'time_start_ms',
    'time_end_ms': 'time_end_ms',
    'ProjectName': 'project_name',
    'Year_': 'year',
    'Location': 'location',
    'Venue': 'venue',
    'EpisodeEvent': 'episode_event',
    'Source': 'source',
    'GameType': 'game_type',
    'PlayersTags': 'players_tags',
    'HandGrade': 'hand_grade',
    'HANDTag': 'hand_tag',
    'EPICHAND': 'epic_hand',
    'Tournament': 'tournament',
    'PokerPlayTags': 'poker_play_tags',
    'Adjective': 'adjective',
    'Emotion': 'emotion',
    'Badbeat': 'is_badbeat',
    'Bluff': 'is_bluff',
    'Suckout': 'is_suckout',
    'Cooler': 'is_cooler',
    'RUNOUTTag': 'runout_tag',
    'PostFlop': 'postflop',
    'All-in': 'allin_tag',
}


def parse_int(value: str) -> Optional[int]:
    """문자열을 정수로 변환"""
    if not value or value.strip() == '':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def parse_bool_tag(value: str) -> bool:
    """태그 값이 있으면 True"""
    return bool(value and value.strip())


def parse_csv_row(row: Dict[str, str]) -> Dict[str, Any]:
    """CSV 행을 DB 레코드로 변환"""
    clip = {}

    for csv_col, db_field in COLUMN_MAPPING.items():
        value = row.get(csv_col, '').strip()

        # 불리언 필드
        if db_field.startswith('is_'):
            clip[db_field] = parse_bool_tag(value)
        # 정수 필드
        elif db_field in ('time_start_ms', 'time_end_ms', 'year'):
            clip[db_field] = parse_int(value)
        else:
            clip[db_field] = value if value else None

    return clip


def load_csv(csv_path: str) -> List[Dict[str, Any]]:
    """CSV 파일 로드"""
    clips = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            clip = parse_csv_row(row)

            # iconik_id가 없으면 건너뛰기
            if not clip.get('iconik_id'):
                continue

            # 빈 제목인 경우 건너뛰기 (테스트 데이터 등)
            if not clip.get('title') or 'test' in clip.get('title', '').lower():
                continue

            clips.append(clip)

    return clips


def extract_filename_keywords(title: str) -> List[str]:
    """클립 제목에서 파일명 매칭용 키워드 추출

    예: "7-wsop-2024-be-ev-12-1500-nlh-ft-Fan-doubles-KK-vs-Yea-QQs"
    → ['wsop', '2024', 'ev-12', '1500', 'nlh', 'ft']
    """
    keywords = []
    title_lower = title.lower()

    # 연도 추출
    import re
    years = re.findall(r'20\d{2}', title_lower)
    keywords.extend(years)

    # 이벤트 번호 추출
    events = re.findall(r'ev[-_]?\d+', title_lower)
    keywords.extend(events)

    # 프로젝트명 추출
    projects = ['wsop', 'hcl', 'pad', 'mpp', 'ggmillions']
    for proj in projects:
        if proj in title_lower:
            keywords.append(proj)

    # 이벤트 타입 추출
    event_types = ['main event', 'me', 'ft', 'final', 'day']
    for et in event_types:
        if et in title_lower:
            keywords.append(et.replace(' ', ''))

    return keywords


def fuzzy_match_file(clip_title: str, file_paths: List[str], threshold: int = 60) -> Optional[tuple]:
    """퍼지 매칭으로 가장 유사한 파일 찾기

    Returns:
        (file_path, confidence) or None
    """
    if not FUZZY_AVAILABLE or not file_paths:
        return None

    # 파일명만 추출
    filenames = [Path(p).stem for p in file_paths]

    # 클립 제목 정규화
    clip_normalized = clip_title.lower().replace('-', ' ').replace('_', ' ')

    # 매칭
    result = process.extractOne(
        clip_normalized,
        filenames,
        scorer=fuzz.token_set_ratio,
        score_cutoff=threshold
    )

    if result:
        matched_filename, score, idx = result
        return (file_paths[idx], score / 100.0)

    return None


def import_iconik_csv(
    csv_path: str,
    db_path: str = "archive.db",
    match_files: bool = True,
    match_threshold: int = 60,
) -> Dict[str, int]:
    """iconik CSV를 데이터베이스에 임포트

    Args:
        csv_path: CSV 파일 경로
        db_path: 데이터베이스 경로
        match_files: files 테이블과 매칭 시도 여부
        match_threshold: 퍼지 매칭 임계값 (0-100)

    Returns:
        임포트 통계
    """
    logger.info(f"Loading CSV: {csv_path}")
    clips = load_csv(csv_path)
    logger.info(f"Loaded {len(clips)} clips from CSV")

    if not clips:
        logger.warning("No clips to import")
        return {'total': 0, 'imported': 0, 'matched': 0}

    db = Database(db_path)

    # 파일 매칭을 위한 파일 목록 로드
    file_paths = []
    file_map = {}  # path -> file_id

    if match_files:
        logger.info("Loading file list for matching...")
        for record in db.get_all_files(limit=100000):
            file_paths.append(record.path)
            file_map[record.path] = record.id
        logger.info(f"Loaded {len(file_paths)} files for matching")

    # 클립 임포트
    imported = 0
    matched = 0

    for i, clip in enumerate(clips):
        # 파일 매칭
        if match_files and file_paths:
            match_result = fuzzy_match_file(
                clip.get('title', ''),
                file_paths,
                threshold=match_threshold
            )

            if match_result:
                matched_path, confidence = match_result
                clip['matched_file_path'] = matched_path
                clip['file_id'] = file_map.get(matched_path)
                clip['match_confidence'] = confidence
                matched += 1

        # DB에 삽입
        try:
            db.insert_clip_metadata(clip)
            imported += 1
        except Exception as e:
            logger.warning(f"Failed to insert clip {clip.get('iconik_id')}: {e}")

        # 진행률 로깅
        if (i + 1) % 100 == 0:
            logger.info(f"Processed {i + 1}/{len(clips)} clips")

    db.close()

    stats = {
        'total': len(clips),
        'imported': imported,
        'matched': matched,
        'match_rate': f"{matched / len(clips) * 100:.1f}%" if clips else "0%"
    }

    logger.info(f"Import complete: {stats}")
    return stats


def show_statistics(db_path: str = "archive.db"):
    """임포트된 클립 통계 출력"""
    db = Database(db_path)
    stats = db.get_clip_statistics()
    db.close()

    print("\n" + "=" * 60)
    print("           클립 메타데이터 통계")
    print("=" * 60)
    print(f"  총 클립 수: {stats['total']:,}개")
    print(f"  매칭된 클립: {stats['matched']:,}개")
    print(f"  미매칭 클립: {stats['unmatched']:,}개")

    print("\n  [프로젝트별]")
    for proj, count in stats['by_project'].items():
        print(f"    {proj}: {count:,}개")

    print("\n  [핸드 등급별]")
    for grade, count in stats['by_hand_grade'].items():
        print(f"    {grade}: {count:,}개")

    print("\n  [이벤트별 (상위 10개)]")
    for i, (event, count) in enumerate(stats['by_event'].items()):
        if i >= 10:
            break
        print(f"    {event}: {count:,}개")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='iconik 메타데이터 CSV 임포트'
    )
    parser.add_argument(
        'csv_path',
        nargs='?',
        help='CSV 파일 경로'
    )
    parser.add_argument(
        '--db', '-d',
        default='archive.db',
        help='데이터베이스 경로 (기본: archive.db)'
    )
    parser.add_argument(
        '--no-match',
        action='store_true',
        help='파일 매칭 비활성화'
    )
    parser.add_argument(
        '--threshold', '-t',
        type=int,
        default=60,
        help='퍼지 매칭 임계값 (기본: 60)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='통계만 출력'
    )

    args = parser.parse_args()

    if args.stats:
        show_statistics(args.db)
        return

    if not args.csv_path:
        parser.print_help()
        return

    import_iconik_csv(
        csv_path=args.csv_path,
        db_path=args.db,
        match_files=not args.no_match,
        match_threshold=args.threshold,
    )

    # 임포트 후 통계 출력
    show_statistics(args.db)


if __name__ == "__main__":
    main()
