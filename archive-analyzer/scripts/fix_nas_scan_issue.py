"""
Issue #57: NAS 스캔 문제 해결 스크립트

문제: NAS 폴더 구조 변경으로 DB 경로와 실제 경로 불일치
- DB의 WSOP 경로: WSOP Archive (1973-2002)/연도/...
- NAS 실제 경로: WSOP 2003/, WSOP 2004/, ...

해결:
1. 유효하지 않은 레코드 정리
2. NAS 재스캔
3. 새 데이터로 업데이트
"""
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

ARCHIVE_DB = 'D:/AI/claude01/archive-analyzer/archive.db'
POKERVOD_DB = 'D:/AI/claude01/shared-data/pokervod.db'
NAS_ARCHIVE = Path(r'\\10.10.100.122\docker\GGPNAs\ARCHIVE')


def count_nas_files():
    """NAS 실제 파일 수 확인"""
    print("\n=== Step 1: NAS 파일 수 확인 ===")

    if not NAS_ARCHIVE.exists():
        print(f"ERROR: NAS 경로 접근 불가: {NAS_ARCHIVE}")
        return 0

    exts = {'.mp4', '.mkv', '.mxf', '.mov', '.avi', '.wmv', '.ts', '.m2ts'}
    files = []

    for catalog in NAS_ARCHIVE.iterdir():
        if catalog.is_dir():
            catalog_files = [f for f in catalog.rglob('*') if f.suffix.lower() in exts]
            files.extend(catalog_files)
            print(f"  {catalog.name}: {len(catalog_files)} files")

    print(f"\n  총 NAS 파일 수: {len(files)}")
    return files


def cleanup_invalid_records(db_path, path_column='path', dry_run=True):
    """유효하지 않은 레코드 정리"""
    print(f"\n=== Step 2: {Path(db_path).name} 정리 ===")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f'SELECT id, {path_column} FROM files')
    all_files = cursor.fetchall()
    print(f"  총 레코드: {len(all_files)}")

    invalid_ids = []
    for file_id, path in all_files:
        if not Path(path).exists():
            invalid_ids.append(file_id)

    print(f"  유효하지 않은 레코드: {len(invalid_ids)}")

    if not dry_run and invalid_ids:
        # 배치로 삭제
        chunk_size = 100
        for i in range(0, len(invalid_ids), chunk_size):
            chunk = invalid_ids[i:i + chunk_size]
            placeholders = ','.join('?' * len(chunk))
            cursor.execute(f'DELETE FROM files WHERE id IN ({placeholders})', chunk)
        conn.commit()
        print(f"  삭제 완료: {len(invalid_ids)} 레코드")

    cursor.execute(f'SELECT COUNT(*) FROM files')
    remaining = cursor.fetchone()[0]
    print(f"  남은 레코드: {remaining}")

    conn.close()
    return len(invalid_ids)


def scan_nas_to_archive_db(nas_files, dry_run=True):
    """NAS 파일을 archive.db에 추가"""
    print("\n=== Step 3: archive.db에 신규 파일 추가 ===")

    conn = sqlite3.connect(ARCHIVE_DB)
    cursor = conn.cursor()

    # 기존 경로 목록
    cursor.execute('SELECT path FROM files')
    existing_paths = {row[0] for row in cursor.fetchall()}
    print(f"  기존 레코드: {len(existing_paths)}")

    # 신규 파일
    new_files = []
    for f in nas_files:
        path_str = str(f)
        if path_str not in existing_paths:
            new_files.append({
                'path': path_str,
                'filename': f.name,
                'extension': f.suffix.lower(),
                'size_bytes': f.stat().st_size if not dry_run else 0,
                'file_type': 'video',
                'parent_folder': str(f.parent),
            })

    print(f"  신규 파일: {len(new_files)}")

    if not dry_run and new_files:
        cursor.executemany('''
            INSERT INTO files (path, filename, extension, size_bytes, file_type, parent_folder, created_at)
            VALUES (:path, :filename, :extension, :size_bytes, :file_type, :parent_folder, datetime('now'))
        ''', new_files)
        conn.commit()
        print(f"  추가 완료: {len(new_files)} 레코드")

    conn.close()
    return len(new_files)


def generate_file_id(nas_path, existing_ids=None):
    """nas_path에서 고유 ID 생성"""
    import hashlib
    # 경로를 정규화하고 해시 생성 (전체 32자 사용)
    normalized = nas_path.replace('\\', '/').lower()
    hash_digest = hashlib.md5(normalized.encode()).hexdigest()
    base_id = f"file_{hash_digest}"

    # 충돌 방지
    if existing_ids is not None:
        counter = 0
        final_id = base_id
        while final_id in existing_ids:
            counter += 1
            final_id = f"{base_id}_{counter}"
        existing_ids.add(final_id)
        return final_id

    return base_id


def sync_to_pokervod(dry_run=True):
    """archive.db → pokervod.db 동기화"""
    print("\n=== Step 4: pokervod.db 동기화 ===")

    archive_conn = sqlite3.connect(ARCHIVE_DB)
    pokervod_conn = sqlite3.connect(POKERVOD_DB)

    archive_cursor = archive_conn.cursor()
    pokervod_cursor = pokervod_conn.cursor()

    # archive.db에서 유효한 파일 조회
    archive_cursor.execute('SELECT path, filename, size_bytes, extension FROM files')
    archive_files = archive_cursor.fetchall()

    # pokervod.db 기존 경로 및 ID
    pokervod_cursor.execute('SELECT nas_path FROM files')
    existing_paths = {row[0] for row in pokervod_cursor.fetchall()}

    pokervod_cursor.execute('SELECT id FROM files')
    existing_ids = {row[0] for row in pokervod_cursor.fetchall()}

    new_records = []
    for path, filename, size, ext in archive_files:
        if path not in existing_paths:
            new_records.append({
                'id': generate_file_id(path, existing_ids),
                'nas_path': path,
                'filename': filename,
                'size_bytes': size,
                'analysis_status': 'pending',
            })

    print(f"  archive.db 파일: {len(archive_files)}")
    print(f"  pokervod.db 기존: {len(existing_paths)}")
    print(f"  신규 추가 대상: {len(new_records)}")

    if not dry_run and new_records:
        pokervod_cursor.executemany('''
            INSERT INTO files (id, nas_path, filename, size_bytes, analysis_status, created_at)
            VALUES (:id, :nas_path, :filename, :size_bytes, :analysis_status, datetime('now'))
        ''', new_records)
        pokervod_conn.commit()
        print(f"  추가 완료: {len(new_records)} 레코드")

    archive_conn.close()
    pokervod_conn.close()
    return len(new_records)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Issue #57: NAS 스캔 문제 해결')
    parser.add_argument('--execute', action='store_true', help='실제 실행 (기본: dry-run)')
    args = parser.parse_args()

    dry_run = not args.execute

    print("=" * 60)
    print("Issue #57: NAS 스캔 문제 해결")
    print("=" * 60)
    print(f"모드: {'DRY-RUN (시뮬레이션)' if dry_run else 'EXECUTE (실제 실행)'}")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: NAS 파일 수 확인
    nas_files = count_nas_files()
    if not nas_files:
        print("\nERROR: NAS 접근 실패")
        return

    # Step 2: 유효하지 않은 레코드 정리
    cleanup_invalid_records(ARCHIVE_DB, path_column='path', dry_run=dry_run)
    cleanup_invalid_records(POKERVOD_DB, path_column='nas_path', dry_run=dry_run)

    # Step 3: NAS 파일을 archive.db에 추가
    added = scan_nas_to_archive_db(nas_files, dry_run=dry_run)

    # Step 4: pokervod.db 동기화
    synced = sync_to_pokervod(dry_run=dry_run)

    print("\n" + "=" * 60)
    print("완료")
    print("=" * 60)
    if dry_run:
        print("\n⚠️  DRY-RUN 모드입니다. 실제 실행하려면:")
        print("    python scripts/fix_nas_scan_issue.py --execute")


if __name__ == '__main__':
    main()
