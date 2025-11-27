#!/usr/bin/env python
"""아카이브 전체 스캔 실행 스크립트"""

import sys
import os
from pathlib import Path

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from archive_analyzer.config import SMBConfig
from archive_analyzer.smb_connector import SMBConnector
from archive_analyzer.database import Database
from archive_analyzer.scanner import ArchiveScanner, ScanProgress


# 설정
SERVER = "10.10.100.122"
SHARE = "docker"
USERNAME = "GGP"
PASSWORD = os.getenv("SMB_PASSWORD", "!@QW12qw")
ARCHIVE_PATH = "GGPNAs/ARCHIVE"
DB_PATH = "archive.db"


def progress_callback(progress: ScanProgress):
    """진행률 출력"""
    bar_width = 30
    filled = int(bar_width * progress.percentage / 100)
    bar = "█" * filled + "░" * (bar_width - filled)

    print(
        f"\r[{bar}] {progress.percentage:5.1f}% | "
        f"{progress.processed_files:,}/{progress.total_files:,} | "
        f"{progress.files_per_second:.1f} f/s | "
        f"ETA: {progress.estimated_remaining:.0f}s",
        end="",
        flush=True
    )


def main():
    print("=" * 60)
    print("Archive Analyzer - Full Scan")
    print("=" * 60)
    print(f"Server: {SERVER}")
    print(f"Share: {SHARE}")
    print(f"Archive: {ARCHIVE_PATH}")
    print(f"Database: {DB_PATH}")
    print()

    # SMB 연결
    config = SMBConfig(
        server=SERVER,
        share=SHARE,
        username=USERNAME,
        password=PASSWORD,
    )

    connector = SMBConnector(config)
    database = Database(DB_PATH)

    try:
        print("Connecting to SMB server...")
        connector.connect()
        print("Connected!")
        print()

        # 스캐너 생성
        scanner = ArchiveScanner(
            connector=connector,
            database=database,
            archive_path=ARCHIVE_PATH,
            batch_size=50,
        )
        scanner.set_progress_callback(progress_callback)

        # 스캔 실행
        print("Starting scan...")
        print()
        result = scanner.scan(count_first=True)

        print()
        print()
        print("=" * 60)
        print("SCAN COMPLETE")
        print("=" * 60)
        print(f"Scan ID: {result.scan_id}")
        print(f"Total Files: {result.total_files:,}")
        print(f"Total Size: {result.total_size / (1024**4):.2f} TB")
        print(f"Duration: {result.duration_seconds:.1f} seconds")
        print(f"Speed: {result.total_files / result.duration_seconds:.1f} files/second")
        print()
        print("By Type:")
        for file_type, data in sorted(result.by_type.items()):
            size_gb = data['size'] / (1024**3)
            print(f"  {file_type:12}: {data['count']:6,} files ({size_gb:8.2f} GB)")

        if result.errors:
            print()
            print(f"Errors: {len(result.errors)}")
            for err in result.errors[:5]:
                print(f"  - {err}")
            if len(result.errors) > 5:
                print(f"  ... and {len(result.errors) - 5} more")

        # DB 통계 확인
        print()
        print("Database Statistics:")
        db_stats = database.get_statistics()
        print(f"  Records in DB: {db_stats['total_files']:,}")
        print(f"  Total size: {db_stats['total_size'] / (1024**4):.2f} TB")

    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        raise
    finally:
        connector.disconnect()
        database.close()
        print()
        print("Done.")


if __name__ == "__main__":
    main()
