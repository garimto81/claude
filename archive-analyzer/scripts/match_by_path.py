"""Path 기반 iconik ↔ media_metadata 매칭 스크립트

media_metadata.csv의 Path 구조를 분석하여
iconik 클립과 아카이브 파일을 매칭합니다.
"""

import csv
import re
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass

try:
    from rapidfuzz import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    print("Warning: rapidfuzz not installed. Fuzzy matching disabled.")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================
# ProjectName → Path 매핑 테이블
# ============================================================

PROJECT_TO_PATH = {
    # WSOP Paradise
    'WSOP PARADISE': 'WSOP-PARADISE',
    'WSOP Paradise': 'WSOP-PARADISE',
    '2024 WSOP PARADISE': 'WSOP-PARADISE',
    '2023 WSOP PARADISE': 'WSOP-PARADISE',

    # Hustler Casino Live
    'Hustler Casino Live': 'HCL',

    # Poker After Dark
    'PAD (POKER AFTER DARK) SEASON 13': 'PAD',
    'Poker After Dark S12': 'PAD',
    'Poker After Dark Seanson 13': 'PAD',

    # WSOP Circuit
    '2024 WSOP Circuit Los Angeles': 'WSOP-C',

    # WSOP Las Vegas (현재)
    'WSOP': 'WSOP-LAS VEGAS',
    '2024 WSOP': 'WSOP-LAS VEGAS',
    'WSOP 2025': 'WSOP-LAS VEGAS',
    '2025 World Series Of Poker': 'WSOP-LAS VEGAS',

    # WSOP Europe
    'WSOPE': 'WSOP-EUROPE',
    '2024 WSOPE': 'WSOP-EUROPE',

    # GGMillions
    'GGMillion$': 'GGMillions',

    # MPP
    'Mediterranean Poker Party MPP': 'MPP',
}

# 연도 → Archive Path 매핑
YEAR_TO_ARCHIVE = {
    (1973, 2002): 'WSOP Archive (1973-2002)',
    (2003, 2010): 'WSOP Archive (2003-2010)',
    (2011, 2016): 'WSOP Archive (2011-2016)',
}


@dataclass
class MediaFile:
    """미디어 파일 정보"""
    id: int
    filename: str
    path: str
    folder: str
    category: str
    sub_category: str
    location: str
    year_folder: str
    normalized_name: str


@dataclass
class MatchResult:
    """매칭 결과"""
    iconik_id: str
    media_file_id: int
    media_filename: str
    match_method: str
    confidence: float


def normalize_filename(filename: str) -> str:
    """파일명 정규화"""
    # 확장자 제거
    name = re.sub(r'\.(mp4|mov|avi|mkv|mxf|m4v)$', '', filename, flags=re.IGNORECASE)
    # 특수문자를 공백으로
    name = re.sub(r'[_\-\.\[\]\(\)]', ' ', name)
    # 다중 공백 제거
    name = re.sub(r'\s+', ' ', name)
    return name.lower().strip()


def extract_year(text: str) -> Optional[int]:
    """텍스트에서 연도 추출"""
    match = re.search(r'(19[7-9]\d|20[0-2]\d)', text)
    if match:
        return int(match.group(1))
    return None


def get_archive_path_for_year(year: int) -> Optional[str]:
    """연도에 해당하는 Archive 경로 반환"""
    for (start, end), path in YEAR_TO_ARCHIVE.items():
        if start <= year <= end:
            return path
    return None


def parse_media_path(path: str) -> Dict[str, str]:
    """Path에서 카테고리 정보 추출

    예: \\\\...\\ARCHIVE\\WSOP\\WSOP-BR\\WSOP-PARADISE\\2024...
    """
    result = {
        'category': '',
        'sub_category': '',
        'location': '',
        'year_folder': '',
        'archive_path': '',
    }

    # 경로 정규화
    parts = path.replace('/', '\\').split('\\')

    # ARCHIVE 위치 찾기
    archive_idx = -1
    for i, p in enumerate(parts):
        if p.upper() == 'ARCHIVE':
            archive_idx = i
            break

    if archive_idx < 0 or archive_idx + 1 >= len(parts):
        return result

    # 카테고리 (WSOP, HCL, PAD, etc.)
    result['category'] = parts[archive_idx + 1]

    # ARCHIVE 이후 경로
    remaining = parts[archive_idx + 1:]
    result['archive_path'] = '\\'.join(remaining)

    # WSOP 세부 분류
    if result['category'] == 'WSOP' and len(remaining) > 1:
        sub = remaining[1]
        result['sub_category'] = sub

        # WSOP-BR 내부 (PARADISE, LAS VEGAS, EUROPE)
        if sub == 'WSOP-BR' and len(remaining) > 2:
            result['location'] = remaining[2]
            if len(remaining) > 3:
                result['year_folder'] = remaining[3]

        # WSOP ARCHIVE (PRE-2016)
        elif 'ARCHIVE' in sub.upper() or 'PRE-2016' in sub.upper():
            result['sub_category'] = 'WSOP ARCHIVE (PRE-2016)'
            if len(remaining) > 2:
                result['year_folder'] = remaining[2]

    # HCL
    elif result['category'] == 'HCL' and len(remaining) > 1:
        result['year_folder'] = remaining[1]

    # PAD
    elif result['category'] == 'PAD' and len(remaining) > 1:
        result['sub_category'] = remaining[1]

    return result


def load_media_metadata(csv_path: str, db_path: str) -> int:
    """media_metadata.csv를 DB에 로드

    Args:
        csv_path: media_metadata.csv 경로
        db_path: 데이터베이스 경로

    Returns:
        로드된 레코드 수
    """
    logger.info(f"Loading media_metadata from {csv_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 기존 데이터 삭제
    cursor.execute("DELETE FROM media_files")

    loaded = 0
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            file_id = row.get('ID', '')
            if not file_id:
                continue

            path = row.get('Path', '')
            filename = row.get('Filename', '')
            folder = row.get('Folder', '')

            # Path 파싱
            parsed = parse_media_path(path)

            # 파일명 정규화
            normalized = normalize_filename(filename)

            # Duration 파싱
            duration = None
            dur_str = row.get('Duration (sec)', '')
            if dur_str:
                try:
                    duration = float(dur_str)
                except ValueError:
                    pass

            # Size 파싱
            size = None
            size_str = row.get('Size (bytes)', '')
            if size_str:
                try:
                    size = int(size_str)
                except ValueError:
                    pass

            cursor.execute("""
                INSERT OR REPLACE INTO media_files
                (id, filename, path, folder, container, size_bytes, duration_sec,
                 category, sub_category, location, year_folder, archive_path, normalized_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(file_id),
                filename,
                path,
                folder,
                row.get('Container', ''),
                size,
                duration,
                parsed['category'],
                parsed['sub_category'],
                parsed['location'],
                parsed['year_folder'],
                parsed['archive_path'],
                normalized,
            ))

            loaded += 1

    conn.commit()
    conn.close()

    logger.info(f"Loaded {loaded} media files")
    return loaded


def load_media_files(db_path: str) -> List[MediaFile]:
    """DB에서 미디어 파일 목록 로드"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, path, folder, category, sub_category,
               location, year_folder, normalized_name
        FROM media_files
    """)

    files = []
    for row in cursor.fetchall():
        files.append(MediaFile(
            id=row['id'],
            filename=row['filename'],
            path=row['path'],
            folder=row['folder'] or '',
            category=row['category'] or '',
            sub_category=row['sub_category'] or '',
            location=row['location'] or '',
            year_folder=row['year_folder'] or '',
            normalized_name=row['normalized_name'] or '',
        ))

    conn.close()
    return files


def load_unmatched_clips(db_path: str) -> List[Dict]:
    """매칭되지 않은 iconik 클립 로드"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT iconik_id, title, description, project_name, episode_event,
               players_tags, year
        FROM clip_metadata
        WHERE file_id IS NULL
    """)

    clips = []
    for row in cursor.fetchall():
        clips.append({
            'iconik_id': row['iconik_id'],
            'title': row['title'] or '',
            'description': row['description'] or '',
            'project_name': row['project_name'] or '',
            'episode_event': row['episode_event'] or '',
            'players_tags': row['players_tags'] or '',
            'year': row['year'],
        })

    conn.close()
    return clips


def build_media_index(media_files: List[MediaFile]) -> Dict[str, List[MediaFile]]:
    """미디어 파일 인덱스 생성"""
    index = defaultdict(list)

    for mf in media_files:
        # 카테고리별 인덱스
        if mf.category:
            index[f'cat:{mf.category}'].append(mf)

        # 서브카테고리별 인덱스
        if mf.sub_category:
            index[f'sub:{mf.sub_category}'].append(mf)

        # Location별 인덱스
        if mf.location:
            index[f'loc:{mf.location}'].append(mf)

        # Archive Path별 인덱스
        if mf.year_folder:
            index[f'year:{mf.year_folder}'].append(mf)

    return index


# ============================================================
# 매칭 전략들
# ============================================================

def match_by_project_path(
    clip: Dict,
    media_index: Dict[str, List[MediaFile]],
    all_media: List[MediaFile]
) -> Optional[MatchResult]:
    """Strategy 1: ProjectName → Path 직접 매칭"""
    project = clip['project_name']

    if not project:
        return None

    # 매핑 테이블에서 Path 찾기
    target_path = PROJECT_TO_PATH.get(project)
    if not target_path:
        return None

    # 해당 경로의 파일들 찾기
    candidates = []
    for mf in all_media:
        if target_path in mf.path or target_path in mf.location or target_path in mf.sub_category:
            candidates.append(mf)

    if not candidates:
        return None

    # 파일명 유사도로 최적 매칭
    return find_best_match(clip, candidates, 'project_path')


def match_by_year_archive(
    clip: Dict,
    media_index: Dict[str, List[MediaFile]],
    all_media: List[MediaFile]
) -> Optional[MatchResult]:
    """Strategy 2: 연도 기반 Archive Path 매칭"""
    # 연도 추출 (project_name 또는 title에서)
    year = clip.get('year')
    if not year:
        year = extract_year(clip['project_name'] + ' ' + clip['title'])

    if not year:
        return None

    # Archive 경로 결정
    archive_path = get_archive_path_for_year(year)
    if not archive_path:
        return None

    # 해당 Archive의 파일들
    candidates = [mf for mf in all_media if archive_path in mf.path or archive_path in mf.sub_category]

    if not candidates:
        return None

    return find_best_match(clip, candidates, 'year_archive')


def match_subclip_parent(
    clip: Dict,
    media_index: Dict[str, List[MediaFile]],
    all_media: List[MediaFile]
) -> Optional[MatchResult]:
    """Strategy 3: Subclip → 부모 파일 매칭"""
    title = clip['title']

    # Subclip 패턴 확인
    if '_subclip' not in title.lower() and 'subclip' not in title.lower():
        return None

    # 부모 파일명 추출
    parent_name = re.split(r'_subclip|_Subclip|subclip', title, flags=re.IGNORECASE)[0]
    parent_normalized = normalize_filename(parent_name)

    if len(parent_normalized) < 5:
        return None

    # 프로젝트 기반 후보 필터링
    candidates = all_media
    project = clip['project_name']
    if project and project in PROJECT_TO_PATH:
        target = PROJECT_TO_PATH[project]
        candidates = [mf for mf in all_media if target in mf.path]

    if not candidates:
        candidates = all_media

    # 부모 파일명과 유사한 파일 찾기
    best_match = None
    best_score = 0

    for mf in candidates:
        if not FUZZY_AVAILABLE:
            # 단순 포함 검사
            if parent_normalized in mf.normalized_name:
                return MatchResult(
                    iconik_id=clip['iconik_id'],
                    media_file_id=mf.id,
                    media_filename=mf.filename,
                    match_method='subclip_parent',
                    confidence=0.80,
                )
        else:
            score = fuzz.token_set_ratio(parent_normalized, mf.normalized_name)
            if score > best_score:
                best_score = score
                best_match = mf

    if best_match and best_score >= 70:
        return MatchResult(
            iconik_id=clip['iconik_id'],
            media_file_id=best_match.id,
            media_filename=best_match.filename,
            match_method='subclip_parent',
            confidence=min(0.95, best_score / 100),
        )

    return None


def match_by_filename_similarity(
    clip: Dict,
    media_index: Dict[str, List[MediaFile]],
    all_media: List[MediaFile]
) -> Optional[MatchResult]:
    """Strategy 4: 파일명 유사도 매칭"""
    if not FUZZY_AVAILABLE:
        return None

    title_normalized = normalize_filename(clip['title'])

    if len(title_normalized) < 5:
        return None

    # 프로젝트 기반 후보 필터링
    candidates = all_media
    project = clip['project_name']
    if project:
        # PRE-2016 연도 프로젝트
        year = extract_year(project)
        if year and year <= 2016:
            archive_path = get_archive_path_for_year(year)
            if archive_path:
                candidates = [mf for mf in all_media if archive_path in mf.path]

        # 직접 매핑
        elif project in PROJECT_TO_PATH:
            target = PROJECT_TO_PATH[project]
            candidates = [mf for mf in all_media if target in mf.path]

    if not candidates:
        candidates = all_media

    best_match = None
    best_score = 0

    for mf in candidates:
        score = fuzz.token_set_ratio(title_normalized, mf.normalized_name)
        if score > best_score:
            best_score = score
            best_match = mf

    if best_match and best_score >= 75:
        return MatchResult(
            iconik_id=clip['iconik_id'],
            media_file_id=best_match.id,
            media_filename=best_match.filename,
            match_method='filename_similarity',
            confidence=min(0.95, best_score / 100),
        )

    return None


def match_by_players(
    clip: Dict,
    media_index: Dict[str, List[MediaFile]],
    all_media: List[MediaFile]
) -> Optional[MatchResult]:
    """Strategy 5: 선수 이름 + 연도 매칭"""
    players_str = clip['players_tags']
    if not players_str:
        return None

    # 선수 이름 추출
    players = [p.strip().lower() for p in players_str.split(',') if p.strip()]
    if not players:
        return None

    # 연도 추출
    year = clip.get('year') or extract_year(clip['project_name'] + ' ' + clip['title'])

    # 후보 필터링
    candidates = all_media
    if year and year <= 2016:
        archive_path = get_archive_path_for_year(year)
        if archive_path:
            candidates = [mf for mf in all_media if archive_path in mf.path]

    # 선수 이름이 파일명에 포함된 파일 찾기
    for mf in candidates:
        filename_lower = mf.filename.lower()
        for player in players:
            # 성(surname)만 매칭 (공백 이후)
            surname = player.split()[-1] if ' ' in player else player
            if len(surname) >= 3 and surname in filename_lower:
                return MatchResult(
                    iconik_id=clip['iconik_id'],
                    media_file_id=mf.id,
                    media_filename=mf.filename,
                    match_method='player_name',
                    confidence=0.75,
                )

    return None


def find_best_match(
    clip: Dict,
    candidates: List[MediaFile],
    method: str
) -> Optional[MatchResult]:
    """후보 중 최적 매칭 찾기"""
    if not candidates:
        return None

    title_normalized = normalize_filename(clip['title'])

    if not FUZZY_AVAILABLE:
        # Fuzzy 없으면 첫 번째 후보 반환
        return MatchResult(
            iconik_id=clip['iconik_id'],
            media_file_id=candidates[0].id,
            media_filename=candidates[0].filename,
            match_method=method,
            confidence=0.70,
        )

    best_match = None
    best_score = 0

    for mf in candidates:
        score = fuzz.token_set_ratio(title_normalized, mf.normalized_name)
        if score > best_score:
            best_score = score
            best_match = mf

    if best_match and best_score >= 60:
        return MatchResult(
            iconik_id=clip['iconik_id'],
            media_file_id=best_match.id,
            media_filename=best_match.filename,
            match_method=method,
            confidence=min(0.95, best_score / 100),
        )

    return None


def run_matching(db_path: str) -> Dict[str, int]:
    """전체 매칭 실행

    Args:
        db_path: 데이터베이스 경로

    Returns:
        매칭 통계
    """
    logger.info("Loading data...")

    # 데이터 로드
    media_files = load_media_files(db_path)
    unmatched_clips = load_unmatched_clips(db_path)

    logger.info(f"  Media files: {len(media_files)}")
    logger.info(f"  Unmatched clips: {len(unmatched_clips)}")

    # 인덱스 생성
    media_index = build_media_index(media_files)

    # 매칭 실행
    results = []
    matched_ids = set()

    strategies = [
        ('project_path', match_by_project_path),
        ('subclip_parent', match_subclip_parent),
        ('year_archive', match_by_year_archive),
        ('filename_similarity', match_by_filename_similarity),
        ('player_name', match_by_players),
    ]

    for strategy_name, strategy_func in strategies:
        logger.info(f"Running strategy: {strategy_name}")
        strategy_matches = 0

        for clip in unmatched_clips:
            if clip['iconik_id'] in matched_ids:
                continue

            result = strategy_func(clip, media_index, media_files)
            if result:
                results.append(result)
                matched_ids.add(clip['iconik_id'])
                strategy_matches += 1

        logger.info(f"  {strategy_name}: {strategy_matches} matches")

    # 결과 저장
    logger.info("Saving results...")
    save_match_results(db_path, results)

    # 통계
    stats = {
        'total_unmatched': len(unmatched_clips),
        'new_matches': len(results),
        'remaining_unmatched': len(unmatched_clips) - len(results),
    }

    # 방법별 통계
    method_counts = defaultdict(int)
    for r in results:
        method_counts[r.match_method] += 1

    stats['by_method'] = dict(method_counts)

    return stats


def save_match_results(db_path: str, results: List[MatchResult]):
    """매칭 결과를 DB에 저장"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for result in results:
        cursor.execute("""
            UPDATE clip_metadata
            SET file_id = ?,
                matched_file_path = ?,
                match_confidence = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE iconik_id = ?
        """, (
            result.media_file_id,
            result.media_filename,
            result.confidence,
            result.iconik_id,
        ))

    conn.commit()
    conn.close()

    logger.info(f"Saved {len(results)} match results")


def sanitize_text(text: str) -> str:
    """텍스트 필드에서 줄바꿈 및 특수문자 정리"""
    if not text:
        return ''
    # 줄바꿈을 공백으로 치환
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    # 탭을 공백으로 치환
    text = text.replace('\t', ' ')
    # 다중 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def export_merged_csv(db_path: str, output_path: str):
    """매칭 결과를 포함한 CSV 내보내기"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM clip_metadata
        ORDER BY
            CASE WHEN file_id IS NOT NULL THEN 0 ELSE 1 END,
            project_name,
            episode_event,
            title
    """)

    rows = cursor.fetchall()
    conn.close()

    headers = [
        'iconik_id', 'title', 'description',
        'file_id', 'matched_file_path', 'match_confidence', 'is_matched',
        'time_start_ms', 'time_end_ms',
        'project_name', 'year', 'location', 'venue', 'episode_event',
        'source', 'game_type', 'tournament',
        'players_tags', 'hand_grade', 'hand_tag', 'epic_hand', 'poker_play_tags',
        'adjective', 'emotion',
        'is_badbeat', 'is_bluff', 'is_suckout', 'is_cooler',
        'runout_tag', 'postflop', 'allin_tag',
        'created_at',
    ]

    matched_count = 0
    unmatched_count = 0

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for row in rows:
            row_dict = dict(row)
            is_matched = 'Y' if row_dict['file_id'] else 'N'

            if row_dict['file_id']:
                matched_count += 1
            else:
                unmatched_count += 1

            # 텍스트 필드 정리 (줄바꿈 제거)
            writer.writerow([
                row_dict['iconik_id'],
                sanitize_text(row_dict['title']),
                sanitize_text(row_dict['description']),
                row_dict['file_id'],
                row_dict['matched_file_path'],
                row_dict['match_confidence'],
                is_matched,
                row_dict['time_start_ms'],
                row_dict['time_end_ms'],
                row_dict['project_name'],
                row_dict['year'],
                row_dict['location'],
                row_dict['venue'],
                row_dict['episode_event'],
                row_dict['source'],
                row_dict['game_type'],
                row_dict['tournament'],
                row_dict['players_tags'],
                row_dict['hand_grade'],
                row_dict['hand_tag'],
                row_dict['epic_hand'],
                row_dict['poker_play_tags'],
                row_dict['adjective'],
                row_dict['emotion'],
                row_dict['is_badbeat'],
                row_dict['is_bluff'],
                row_dict['is_suckout'],
                row_dict['is_cooler'],
                row_dict['runout_tag'],
                row_dict['postflop'],
                row_dict['allin_tag'],
                row_dict['created_at'],
            ])

    logger.info(f"Exported CSV: {output_path}")
    logger.info(f"  Matched: {matched_count}, Unmatched: {unmatched_count}")

    return matched_count, unmatched_count


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Path 기반 iconik ↔ media_metadata 매칭')
    parser.add_argument('--media-csv', '-m', required=True, help='media_metadata.csv 경로')
    parser.add_argument('--db', '-d', required=True, help='데이터베이스 경로')
    parser.add_argument('--output', '-o', help='출력 CSV 경로')
    parser.add_argument('--load-only', action='store_true', help='media_metadata만 로드')

    args = parser.parse_args()

    print("=" * 70)
    print("           Path 기반 iconik ↔ media_metadata 매칭")
    print("=" * 70)

    # 1. media_metadata 로드
    print("\n[1] media_metadata.csv 로드 중...")
    loaded = load_media_metadata(args.media_csv, args.db)
    print(f"    {loaded}개 파일 로드 완료")

    if args.load_only:
        print("\n로드 완료. 종료합니다.")
        return

    # 2. 매칭 실행
    print("\n[2] 매칭 실행 중...")
    stats = run_matching(args.db)

    print("\n[3] 매칭 결과")
    print("-" * 70)
    print(f"  미매칭 클립: {stats['total_unmatched']}개")
    print(f"  신규 매칭: {stats['new_matches']}개")
    print(f"  남은 미매칭: {stats['remaining_unmatched']}개")

    print("\n  [방법별 매칭]")
    for method, count in stats.get('by_method', {}).items():
        print(f"    {method}: {count}개")

    # 3. CSV 내보내기
    if args.output:
        print(f"\n[4] CSV 내보내기: {args.output}")
        matched, unmatched = export_merged_csv(args.db, args.output)
        print(f"    총 매칭: {matched}개 ({matched/(matched+unmatched)*100:.1f}%)")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
