"""clip_metadata 테이블을 CSV로 내보내기

DB에 저장된 전체 클립 메타데이터를 CSV 파일로 내보냅니다.
"""

import csv
import sys
import sqlite3
from pathlib import Path

# 프로젝트 src 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def export_to_csv(db_path: str, output_csv: str):
    """clip_metadata 테이블을 CSV로 내보내기"""

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 전체 데이터 조회
    cursor.execute("""
        SELECT
            iconik_id,
            title,
            description,
            time_start_ms,
            time_end_ms,
            project_name,
            year,
            location,
            venue,
            episode_event,
            source,
            game_type,
            players_tags,
            hand_grade,
            hand_tag,
            epic_hand,
            tournament,
            poker_play_tags,
            adjective,
            emotion,
            is_badbeat,
            is_bluff,
            is_suckout,
            is_cooler,
            runout_tag,
            postflop,
            allin_tag,
            file_id,
            matched_file_path,
            match_confidence,
            created_at
        FROM clip_metadata
        ORDER BY project_name, episode_event, title
    """)

    rows = cursor.fetchall()
    conn.close()

    # CSV 헤더
    headers = [
        'iconik_id', 'title', 'description',
        'time_start_ms', 'time_end_ms',
        'project_name', 'year', 'location', 'venue',
        'episode_event', 'source', 'game_type',
        'players_tags', 'hand_grade', 'hand_tag',
        'epic_hand', 'tournament', 'poker_play_tags',
        'adjective', 'emotion',
        'is_badbeat', 'is_bluff', 'is_suckout', 'is_cooler',
        'runout_tag', 'postflop', 'allin_tag',
        'file_id', 'matched_file_path', 'match_confidence',
        'is_matched', 'created_at'
    ]

    # CSV 쓰기
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for row in rows:
            row_dict = dict(row)
            # is_matched 컬럼 추가
            is_matched = 'Y' if row_dict['file_id'] else 'N'

            writer.writerow([
                row_dict['iconik_id'],
                row_dict['title'],
                row_dict['description'],
                row_dict['time_start_ms'],
                row_dict['time_end_ms'],
                row_dict['project_name'],
                row_dict['year'],
                row_dict['location'],
                row_dict['venue'],
                row_dict['episode_event'],
                row_dict['source'],
                row_dict['game_type'],
                row_dict['players_tags'],
                row_dict['hand_grade'],
                row_dict['hand_tag'],
                row_dict['epic_hand'],
                row_dict['tournament'],
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
                row_dict['file_id'],
                row_dict['matched_file_path'],
                row_dict['match_confidence'],
                is_matched,
                row_dict['created_at'],
            ])

    print(f"Exported {len(rows)} clips to {output_csv}")
    return len(rows)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='clip_metadata를 CSV로 내보내기')
    parser.add_argument('--db', '-d', default='archive.db', help='DB 경로')
    parser.add_argument('--output', '-o', required=True, help='출력 CSV 경로')

    args = parser.parse_args()
    export_to_csv(args.db, args.output)


if __name__ == "__main__":
    main()
