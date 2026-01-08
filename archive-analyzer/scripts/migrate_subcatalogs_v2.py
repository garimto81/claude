#!/usr/bin/env python
"""subcatalogs 다단계 구조 마이그레이션 스크립트

기존 단일 계층 subcatalogs를 다단계 계층 구조로 마이그레이션합니다.

변경 사항:
- parent_id: 상위 서브카탈로그 참조 (NULL이면 1단계)
- depth: 계층 깊이 (1, 2, 3)
- path: 전체 경로 (예: wsop/wsop-br/wsop-europe)

사용법:
    python scripts/migrate_subcatalogs_v2.py [--dry-run]
"""

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

POKERVOD_DB = "d:/AI/claude01/qwen_hand_analysis/data/pokervod.db"


def check_columns_exist(cursor) -> dict:
    """컬럼 존재 여부 확인"""
    cursor.execute("PRAGMA table_info(subcatalogs)")
    columns = {row[1] for row in cursor.fetchall()}
    return {
        "parent_id": "parent_id" in columns,
        "depth": "depth" in columns,
        "path": "path" in columns,
    }


def add_new_columns(cursor, dry_run: bool) -> None:
    """새 컬럼 추가"""
    columns_exist = check_columns_exist(cursor)

    if not columns_exist["parent_id"]:
        print("  - parent_id 컬럼 추가")
        if not dry_run:
            cursor.execute("""
                ALTER TABLE subcatalogs
                ADD COLUMN parent_id VARCHAR(100) REFERENCES subcatalogs(id)
            """)

    if not columns_exist["depth"]:
        print("  - depth 컬럼 추가")
        if not dry_run:
            cursor.execute("""
                ALTER TABLE subcatalogs
                ADD COLUMN depth INTEGER DEFAULT 1
            """)

    if not columns_exist["path"]:
        print("  - path 컬럼 추가")
        if not dry_run:
            cursor.execute("""
                ALTER TABLE subcatalogs
                ADD COLUMN path TEXT
            """)


def create_wsop_hierarchy(cursor, dry_run: bool) -> int:
    """WSOP 다단계 구조 생성"""
    count = 0
    now = datetime.now().isoformat()

    # WSOP 계층 구조 정의
    wsop_structure = [
        # depth=1: 최상위 서브카탈로그
        {
            "id": "wsop-archive",
            "catalog_id": "WSOP",
            "parent_id": None,
            "name": "WSOP Archive (PRE-2016)",
            "depth": 1,
            "path": "wsop/wsop-archive",
        },
        {
            "id": "wsop-br",
            "catalog_id": "WSOP",
            "parent_id": None,
            "name": "WSOP-BR",
            "depth": 1,
            "path": "wsop/wsop-br",
        },
        {
            "id": "wsop-circuit",
            "catalog_id": "WSOP",
            "parent_id": None,
            "name": "WSOP Circuit",
            "depth": 1,
            "path": "wsop/wsop-circuit",
        },
        {
            "id": "wsop-super-circuit",
            "catalog_id": "WSOP",
            "parent_id": None,
            "name": "WSOP Super Circuit",
            "depth": 1,
            "path": "wsop/wsop-super-circuit",
        },
        # depth=2: WSOP Archive 하위
        {
            "id": "wsop-archive-2003-2010",
            "catalog_id": "WSOP",
            "parent_id": "wsop-archive",
            "name": "WSOP Archive (2003-2010)",
            "depth": 2,
            "path": "wsop/wsop-archive/2003-2010",
        },
        {
            "id": "wsop-archive-2011-2016",
            "catalog_id": "WSOP",
            "parent_id": "wsop-archive",
            "name": "WSOP Archive (2011-2016)",
            "depth": 2,
            "path": "wsop/wsop-archive/2011-2016",
        },
        {
            "id": "wsop-archive-1973-2002",
            "catalog_id": "WSOP",
            "parent_id": "wsop-archive",
            "name": "WSOP Archive (1973-2002)",
            "depth": 2,
            "path": "wsop/wsop-archive/1973-2002",
        },
        # depth=2: WSOP-BR 하위
        {
            "id": "wsop-europe",
            "catalog_id": "WSOP",
            "parent_id": "wsop-br",
            "name": "WSOP Europe",
            "depth": 2,
            "path": "wsop/wsop-br/wsop-europe",
        },
        {
            "id": "wsop-paradise",
            "catalog_id": "WSOP",
            "parent_id": "wsop-br",
            "name": "WSOP Paradise",
            "depth": 2,
            "path": "wsop/wsop-br/wsop-paradise",
        },
        {
            "id": "wsop-las-vegas",
            "catalog_id": "WSOP",
            "parent_id": "wsop-br",
            "name": "WSOP Las Vegas",
            "depth": 2,
            "path": "wsop/wsop-br/wsop-las-vegas",
        },
        # depth=3: 연도별 (예시)
        {
            "id": "wsop-europe-2024",
            "catalog_id": "WSOP",
            "parent_id": "wsop-europe",
            "name": "2024 WSOP Europe",
            "depth": 3,
            "path": "wsop/wsop-br/wsop-europe/2024",
        },
        {
            "id": "wsop-europe-2025",
            "catalog_id": "WSOP",
            "parent_id": "wsop-europe",
            "name": "2025 WSOP Europe",
            "depth": 3,
            "path": "wsop/wsop-br/wsop-europe/2025",
        },
        {
            "id": "wsop-paradise-2023",
            "catalog_id": "WSOP",
            "parent_id": "wsop-paradise",
            "name": "2023 WSOP Paradise",
            "depth": 3,
            "path": "wsop/wsop-br/wsop-paradise/2023",
        },
        {
            "id": "wsop-paradise-2024",
            "catalog_id": "WSOP",
            "parent_id": "wsop-paradise",
            "name": "2024 WSOP Paradise",
            "depth": 3,
            "path": "wsop/wsop-br/wsop-paradise/2024",
        },
        {
            "id": "wsop-las-vegas-2024",
            "catalog_id": "WSOP",
            "parent_id": "wsop-las-vegas",
            "name": "2024 WSOP Las Vegas",
            "depth": 3,
            "path": "wsop/wsop-br/wsop-las-vegas/2024",
        },
        {
            "id": "wsop-las-vegas-2025",
            "catalog_id": "WSOP",
            "parent_id": "wsop-las-vegas",
            "name": "2025 WSOP Las Vegas",
            "depth": 3,
            "path": "wsop/wsop-br/wsop-las-vegas/2025",
        },
    ]

    for item in wsop_structure:
        # 이미 존재하는지 확인
        cursor.execute("SELECT id FROM subcatalogs WHERE id = ?", (item["id"],))
        exists = cursor.fetchone()

        if exists:
            # 업데이트
            print(f"  - 업데이트: {item['id']} (depth={item['depth']})")
            if not dry_run:
                cursor.execute("""
                    UPDATE subcatalogs SET
                        parent_id = ?,
                        depth = ?,
                        path = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (item["parent_id"], item["depth"], item["path"], now, item["id"]))
        else:
            # 삽입
            print(f"  - 생성: {item['id']} (depth={item['depth']})")
            if not dry_run:
                cursor.execute("""
                    INSERT INTO subcatalogs (
                        id, catalog_id, parent_id, name, depth, path,
                        display_order, tournament_count, file_count,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, ?, ?)
                """, (
                    item["id"], item["catalog_id"], item["parent_id"],
                    item["name"], item["depth"], item["path"], now, now
                ))
        count += 1

    return count


def create_other_catalogs(cursor, dry_run: bool) -> int:
    """HCL, PAD, MPP, GGMillions 구조 생성"""
    count = 0
    now = datetime.now().isoformat()

    other_structure = [
        # HCL
        {"id": "hcl-2025", "catalog_id": "HCL", "parent_id": None, "name": "HCL 2025", "depth": 1, "path": "hcl/2025"},
        {"id": "hcl-clips", "catalog_id": "HCL", "parent_id": None, "name": "HCL Poker Clips", "depth": 1, "path": "hcl/clips"},
        # PAD
        {"id": "pad-s12", "catalog_id": "PAD", "parent_id": None, "name": "PAD Season 12", "depth": 1, "path": "pad/s12"},
        {"id": "pad-s13", "catalog_id": "PAD", "parent_id": None, "name": "PAD Season 13", "depth": 1, "path": "pad/s13"},
        # MPP
        {"id": "mpp-1m", "catalog_id": "MPP", "parent_id": None, "name": "$1M GTD Mystery Bounty", "depth": 1, "path": "mpp/1m"},
        {"id": "mpp-2m", "catalog_id": "MPP", "parent_id": None, "name": "$2M GTD Grand Final", "depth": 1, "path": "mpp/2m"},
        {"id": "mpp-5m", "catalog_id": "MPP", "parent_id": None, "name": "$5M GTD Main Event", "depth": 1, "path": "mpp/5m"},
        # GGMillions
        {"id": "ggmillions-main", "catalog_id": "GGMillions", "parent_id": None, "name": "GGMillions Main", "depth": 1, "path": "ggmillions/main"},
    ]

    for item in other_structure:
        cursor.execute("SELECT id FROM subcatalogs WHERE id = ?", (item["id"],))
        exists = cursor.fetchone()

        if exists:
            print(f"  - 업데이트: {item['id']}")
            if not dry_run:
                cursor.execute("""
                    UPDATE subcatalogs SET
                        parent_id = ?,
                        depth = ?,
                        path = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (item["parent_id"], item["depth"], item["path"], now, item["id"]))
        else:
            print(f"  - 생성: {item['id']}")
            if not dry_run:
                cursor.execute("""
                    INSERT INTO subcatalogs (
                        id, catalog_id, parent_id, name, depth, path,
                        display_order, tournament_count, file_count,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, ?, ?)
                """, (
                    item["id"], item["catalog_id"], item["parent_id"],
                    item["name"], item["depth"], item["path"], now, now
                ))
        count += 1

    return count


def ensure_catalogs_exist(cursor, dry_run: bool) -> None:
    """카탈로그 존재 확인 및 생성"""
    catalogs = ["WSOP", "HCL", "PAD", "MPP", "GGMillions"]
    now = datetime.now().isoformat()

    for catalog_id in catalogs:
        cursor.execute("SELECT id FROM catalogs WHERE id = ?", (catalog_id,))
        if not cursor.fetchone():
            print(f"  - 카탈로그 생성: {catalog_id}")
            if not dry_run:
                cursor.execute("""
                    INSERT INTO catalogs (id, name, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (catalog_id, catalog_id, now, now))


def main():
    parser = argparse.ArgumentParser(description="subcatalogs 다단계 마이그레이션")
    parser.add_argument("--dry-run", action="store_true", help="실제 변경 없이 시뮬레이션")
    parser.add_argument("--db", type=str, default=POKERVOD_DB, help="pokervod.db 경로")
    args = parser.parse_args()

    if not Path(args.db).exists():
        print(f"오류: DB 파일을 찾을 수 없습니다: {args.db}")
        return

    if args.dry_run:
        print("[DRY-RUN 모드]\n")

    conn = sqlite3.connect(args.db)
    cursor = conn.cursor()

    try:
        # 1. 새 컬럼 추가
        print("1. 스키마 업데이트...")
        add_new_columns(cursor, args.dry_run)

        # 2. 카탈로그 확인
        print("\n2. 카탈로그 확인...")
        ensure_catalogs_exist(cursor, args.dry_run)

        # 3. WSOP 계층 구조
        print("\n3. WSOP 계층 구조 생성...")
        wsop_count = create_wsop_hierarchy(cursor, args.dry_run)

        # 4. 기타 카탈로그
        print("\n4. 기타 카탈로그 구조 생성...")
        other_count = create_other_catalogs(cursor, args.dry_run)

        if not args.dry_run:
            conn.commit()

        print(f"\n=== 완료 ===")
        print(f"WSOP: {wsop_count}개")
        print(f"기타: {other_count}개")
        print(f"총계: {wsop_count + other_count}개")

        if args.dry_run:
            print("\n[DRY-RUN] 실제 변경 없음")

    except Exception as e:
        print(f"\n오류 발생: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
