# -*- coding: utf-8 -*-
"""로컬 데이터 확인 스크립트"""
import os
import sqlite3

def check_local_db():
    """로컬 데이터베이스 확인"""
    print("=" * 60)
    print("=== LOCAL DATABASE CHECK ===")
    print("=" * 60)

    dbs = [
        ('archive.db', 'C:/claude/archive-analyzer/data/output/archive.db'),
        ('pokervod.db', 'D:/AI/claude01/shared-data/pokervod.db'),
    ]

    for name, path in dbs:
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"\n[OK] {name}: {size_mb:.2f} MB")

            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                tables = cursor.fetchall()
                print(f"   Tables ({len(tables)}):")
                for t in tables[:10]:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM [{t[0]}]")
                        count = cursor.fetchone()[0]
                        print(f"     - {t[0]}: {count} rows")
                    except:
                        print(f"     - {t[0]}: (error)")
                if len(tables) > 10:
                    print(f"     ... and {len(tables) - 10} more")
                conn.close()
            except Exception as e:
                print(f"   DB read error: {e}")
        else:
            print(f"\n[MISSING] {name}: {path}")


def check_iconik_data():
    """iconik 관련 데이터 확인"""
    print("\n" + "=" * 60)
    print("=== ICONIK DATA IN archive.db ===")
    print("=" * 60)

    db_path = 'C:/claude/archive-analyzer/data/output/archive.db'
    if not os.path.exists(db_path):
        print("[MISSING] archive.db not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # clip_metadata 테이블 확인
    try:
        cursor.execute("SELECT COUNT(*) FROM clip_metadata")
        total = cursor.fetchone()[0]
        print(f"\nclip_metadata: {total} clips")

        cursor.execute("SELECT COUNT(*) FROM clip_metadata WHERE file_id IS NOT NULL")
        matched = cursor.fetchone()[0]
        print(f"  - Matched: {matched} ({matched*100/total:.1f}%)" if total > 0 else "  - Matched: 0")

        cursor.execute("SELECT COUNT(*) FROM clip_metadata WHERE file_id IS NULL")
        unmatched = cursor.fetchone()[0]
        print(f"  - Unmatched: {unmatched}")

        # 프로젝트별 통계
        cursor.execute("""
            SELECT project_name, COUNT(*) as cnt
            FROM clip_metadata
            WHERE project_name IS NOT NULL
            GROUP BY project_name
            ORDER BY cnt DESC
            LIMIT 5
        """)
        projects = cursor.fetchall()
        if projects:
            print("\n  By Project:")
            for p in projects:
                print(f"    - {p[0]}: {p[1]}")
    except Exception as e:
        print(f"[ERROR] clip_metadata: {e}")

    # files 테이블 확인
    try:
        cursor.execute("SELECT COUNT(*) FROM files")
        total = cursor.fetchone()[0]
        print(f"\nfiles: {total} files")

        cursor.execute("SELECT file_type, COUNT(*) FROM files GROUP BY file_type ORDER BY COUNT(*) DESC")
        types = cursor.fetchall()
        for t in types[:5]:
            print(f"  - {t[0]}: {t[1]}")
    except Exception as e:
        print(f"[ERROR] files: {e}")

    conn.close()


if __name__ == '__main__':
    check_local_db()
    check_iconik_data()
