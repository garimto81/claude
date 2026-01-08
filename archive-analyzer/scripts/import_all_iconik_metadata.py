"""전체 iconik 메타데이터 임포트 스크립트

매칭 여부와 관계없이 모든 iconik 클립을 DB에 저장합니다.
"""

import csv
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

# 프로젝트 src 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from archive_analyzer.database import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_int(value: str) -> int:
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


def load_iconik_csv(csv_path: str) -> List[Dict]:
    """iconik CSV 전체 로드"""
    clips = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            iconik_id = row.get('id', '').strip()
            title = row.get('title', '').strip()

            if not iconik_id:
                continue

            # 빈 제목이나 테스트 데이터 건너뛰기
            if not title or 'test' in title.lower():
                continue

            clips.append({
                'iconik_id': iconik_id,
                'title': title,
                'description': row.get('Description', '').strip(),
                'time_start_ms': parse_int(row.get('time_start_ms', '')),
                'time_end_ms': parse_int(row.get('time_end_ms', '')),
                'project_name': row.get('ProjectName', '').strip(),
                'year': parse_int(row.get('Year_', '')),
                'location': row.get('Location', '').strip(),
                'venue': row.get('Venue', '').strip(),
                'episode_event': row.get('EpisodeEvent', '').strip(),
                'source': row.get('Source', '').strip(),
                'game_type': row.get('GameType', '').strip(),
                'players_tags': row.get('PlayersTags', '').strip(),
                'hand_grade': row.get('HandGrade', '').strip(),
                'hand_tag': row.get('HANDTag', '').strip(),
                'epic_hand': row.get('EPICHAND', '').strip(),
                'tournament': row.get('Tournament', '').strip(),
                'poker_play_tags': row.get('PokerPlayTags', '').strip(),
                'adjective': row.get('Adjective', '').strip(),
                'emotion': row.get('Emotion', '').strip(),
                'is_badbeat': parse_bool_tag(row.get('Badbeat', '')),
                'is_bluff': parse_bool_tag(row.get('Bluff', '')),
                'is_suckout': parse_bool_tag(row.get('Suckout', '')),
                'is_cooler': parse_bool_tag(row.get('Cooler', '')),
                'runout_tag': row.get('RUNOUTTag', '').strip(),
                'postflop': row.get('PostFlop', '').strip(),
                'allin_tag': row.get('All-in', '').strip(),
            })

    return clips


def load_matched_csv(csv_path: str) -> Dict[str, Dict]:
    """매칭 결과 CSV 로드"""
    matches = {}

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Support both column naming conventions
            iconik_id = row.get('iconik_id', '') or row.get('Clip ID', '')
            iconik_id = iconik_id.strip()
            if not iconik_id:
                continue

            matches[iconik_id] = {
                'matched_filename': (row.get('matched_filename', '') or row.get('Matched Filename', '')).strip(),
                'matched_file_id': parse_int(row.get('matched_file_id', '') or row.get('Matched File ID', '')),
                'match_method': (row.get('match_method', '') or row.get('Match Method', '')).strip(),
                'match_confidence': float(row.get('confidence', '') or row.get('Confidence', '') or '0'),
            }

    return matches


def import_all(
    iconik_csv: str,
    matched_csv: str,
    db_path: str = "archive.db",
) -> Dict[str, int]:
    """전체 iconik 메타데이터를 DB에 임포트

    Args:
        iconik_csv: iconik 메타데이터 CSV 경로
        matched_csv: 매칭 결과 CSV 경로
        db_path: 데이터베이스 경로

    Returns:
        임포트 통계
    """
    logger.info("Loading iconik CSV...")
    all_clips = load_iconik_csv(iconik_csv)
    logger.info(f"Loaded {len(all_clips)} clips from iconik CSV")

    logger.info("Loading matched CSV...")
    matches = load_matched_csv(matched_csv)
    logger.info(f"Loaded {len(matches)} matches")

    # DB에 임포트
    db = Database(db_path)

    imported_matched = 0
    imported_unmatched = 0

    for clip in all_clips:
        iconik_id = clip['iconik_id']

        # 매칭 정보가 있으면 추가
        if iconik_id in matches:
            match_info = matches[iconik_id]
            clip['file_id'] = match_info['matched_file_id']
            clip['matched_file_path'] = match_info['matched_filename']
            clip['match_confidence'] = match_info['match_confidence']
        else:
            clip['file_id'] = None
            clip['matched_file_path'] = None
            clip['match_confidence'] = None

        try:
            db.insert_clip_metadata(clip)
            if clip['file_id']:
                imported_matched += 1
            else:
                imported_unmatched += 1
        except Exception as e:
            logger.warning(f"Failed to insert clip {iconik_id}: {e}")

    db.close()

    stats = {
        'total': len(all_clips),
        'matched': imported_matched,
        'unmatched': imported_unmatched,
    }

    logger.info(f"Import complete: {imported_matched} matched, {imported_unmatched} unmatched")
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

    match_rate = (stats['matched'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"  매칭률: {match_rate:.1f}%")

    if stats['by_project']:
        print("\n  [프로젝트별]")
        for proj, count in sorted(stats['by_project'].items(), key=lambda x: -x[1]):
            print(f"    {proj}: {count:,}개")

    if stats['by_hand_grade']:
        print("\n  [핸드 등급별]")
        for grade, count in sorted(stats['by_hand_grade'].items(), key=lambda x: -x[1]):
            print(f"    {grade}: {count:,}개")

    if stats['by_event']:
        print("\n  [이벤트별 (상위 20개)]")
        for i, (event, count) in enumerate(stats['by_event'].items()):
            if i >= 20:
                break
            print(f"    {event}: {count:,}개")

    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='전체 iconik 메타데이터 DB 임포트 (매칭/미매칭 모두)'
    )
    parser.add_argument(
        '--iconik', '-i',
        required=True,
        help='iconik CSV 파일 경로'
    )
    parser.add_argument(
        '--matched', '-m',
        required=True,
        help='매칭 결과 CSV 파일 경로'
    )
    parser.add_argument(
        '--db', '-d',
        default='archive.db',
        help='데이터베이스 경로 (기본: archive.db)'
    )

    args = parser.parse_args()

    import_all(
        iconik_csv=args.iconik,
        matched_csv=args.matched,
        db_path=args.db,
    )

    # 임포트 후 통계 출력
    show_statistics(args.db)


if __name__ == "__main__":
    main()
