"""두 CSV 파일 통합

clip_metadata_full.csv와 iconik_matched.csv를 합쳐서
모든 정보를 포함하는 통합 CSV를 생성합니다.
"""

import csv
import sqlite3
from pathlib import Path


def merge_and_export(db_path: str, output_csv: str):
    """DB에서 전체 데이터를 통합 CSV로 내보내기"""

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 전체 데이터 조회
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

    # CSV 헤더 (통합 버전)
    headers = [
        # 기본 정보
        'iconik_id',
        'title',
        'description',

        # 매칭 정보 (iconik_matched.csv에서)
        'file_id',
        'matched_file_path',
        'match_confidence',
        'is_matched',

        # 타임코드
        'time_start_ms',
        'time_end_ms',

        # 프로젝트/이벤트 정보
        'project_name',
        'year',
        'location',
        'venue',
        'episode_event',
        'source',
        'game_type',
        'tournament',

        # 포커 메타데이터
        'players_tags',
        'hand_grade',
        'hand_tag',
        'epic_hand',
        'poker_play_tags',

        # 태그/분류
        'adjective',
        'emotion',
        'is_badbeat',
        'is_bluff',
        'is_suckout',
        'is_cooler',
        'runout_tag',
        'postflop',
        'allin_tag',

        # 메타
        'created_at',
    ]

    # CSV 쓰기
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        matched_count = 0
        unmatched_count = 0

        for row in rows:
            row_dict = dict(row)
            is_matched = 'Y' if row_dict['file_id'] else 'N'

            if row_dict['file_id']:
                matched_count += 1
            else:
                unmatched_count += 1

            writer.writerow([
                row_dict['iconik_id'],
                row_dict['title'],
                row_dict['description'],

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

    print(f"\n통합 CSV 저장 완료: {output_csv}")
    print(f"  - 총 클립: {len(rows)}개")
    print(f"  - 매칭됨 (Y): {matched_count}개")
    print(f"  - 미매칭 (N): {unmatched_count}개")

    return len(rows)


if __name__ == "__main__":
    db_path = r"d:\AI\claude01\archive-analyzer\data\output\archive.db"
    output_csv = r"d:\AI\claude01\archive-analyzer\data\output\iconik_metadata_merged.csv"

    merge_and_export(db_path, output_csv)
