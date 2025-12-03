"""DB 파일의 실제 존재 여부 확인"""
import sys
import sqlite3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')


def check_file_exists(nas_path):
    """파일 존재 여부 확인"""
    try:
        return Path(nas_path).exists()
    except Exception:
        return False


def main():
    conn = sqlite3.connect('D:/AI/claude01/shared-data/pokervod.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nas_path FROM files')
    files = cursor.fetchall()
    conn.close()

    print(f"DB 파일 수: {len(files)}")
    print("파일 존재 여부 확인 중... (병렬 처리)")

    existing = []
    missing = []

    # 병렬 처리로 빠르게 확인
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_file_exists, f[1]): f for f in files}

        for i, future in enumerate(as_completed(futures)):
            file_info = futures[future]
            if future.result():
                existing.append(file_info)
            else:
                missing.append(file_info)

            # 진행 상황
            if (i + 1) % 500 == 0:
                print(f"  확인: {i + 1}/{len(files)}")

    print(f"\n=== 결과 ===")
    print(f"존재하는 파일: {len(existing)}")
    print(f"누락된 파일: {len(missing)}")

    if missing:
        print(f"\n=== 누락된 파일 샘플 (최대 10개) ===")
        for file_id, path in missing[:10]:
            print(f"  ID {file_id}: {path[:80]}...")

    # 카탈로그별 누락 현황
    print(f"\n=== 카탈로그별 누락 현황 ===")
    catalog_missing = {}
    for file_id, path in missing:
        if 'ARCHIVE' in path:
            parts = path.split('ARCHIVE')
            if len(parts) > 1:
                sub = parts[1].lstrip('/').lstrip('\\')
                folder = sub.split('/')[0].split('\\')[0]
                catalog_missing[folder] = catalog_missing.get(folder, 0) + 1

    for catalog, count in sorted(catalog_missing.items(), key=lambda x: -x[1]):
        print(f"  {catalog}: {count}")


if __name__ == '__main__':
    main()
