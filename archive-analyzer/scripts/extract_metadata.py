#!/usr/bin/env python
"""미디어 메타데이터 추출 스크립트 (최적화 버전)

NAS 아카이브의 비디오 파일에서 메타데이터를 추출하여 데이터베이스에 저장합니다.
Issue #10: 미디어 메타데이터 추출기 구현 (FR-002)

최적화:
- 병렬 처리 (ThreadPoolExecutor)
- HEADER_SIZE 축소 (512KB)
- SMB 연결 풀링

Usage:
    python extract_metadata.py              # 전체 파일 추출
    python extract_metadata.py --test       # 테스트 모드 (5개만)
    python extract_metadata.py --limit 100  # 제한된 수만 추출
    python extract_metadata.py --workers 4  # 병렬 워커 수 지정
"""

import sys
import os
import argparse
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

# Windows 콘솔 UTF-8 설정 (먼저 환경변수 설정)
os.environ['PYTHONIOENCODING'] = 'utf-8'

if sys.platform == 'win32':
    # 콘솔 출력 인코딩 강제 설정
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Python 3.6 이하
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from archive_analyzer.config import SMBConfig
from archive_analyzer.smb_connector import SMBConnector
from archive_analyzer.database import Database
from archive_analyzer.media_extractor import SMBMediaExtractor, ExtractionProgress


# 설정
SERVER = "10.10.100.122"
SHARE = "docker"
USERNAME = "GGP"
PASSWORD = os.getenv("SMB_PASSWORD", "!@QW12qw")
ARCHIVE_PATH = "GGPNAs/ARCHIVE"
DB_PATH = "archive.db"


# 스레드 로컬 저장소 (각 워커별 SMB 연결)
thread_local = threading.local()


def get_worker_connector(config: SMBConfig) -> SMBConnector:
    """워커별 SMB 연결 반환 (연결 풀링)"""
    if not hasattr(thread_local, 'connector'):
        thread_local.connector = SMBConnector(config)
        thread_local.connector.connect()
    return thread_local.connector


def get_worker_extractor(config: SMBConfig) -> SMBMediaExtractor:
    """워커별 추출기 반환"""
    if not hasattr(thread_local, 'extractor'):
        connector = get_worker_connector(config)
        thread_local.extractor = SMBMediaExtractor(connector)
    return thread_local.extractor


def extract_single_file(args):
    """단일 파일 메타데이터 추출 (병렬 처리용)"""
    file_record, config = args

    try:
        extractor = get_worker_extractor(config)
        info = extractor.extract(file_record.path, file_id=file_record.id)
        return (file_record, info, None)
    except Exception as e:
        return (file_record, None, str(e))


def progress_callback(progress: ExtractionProgress):
    """진행률 출력"""
    bar_width = 30
    filled = int(bar_width * progress.percentage / 100)
    bar = "█" * filled + "░" * (bar_width - filled)

    # 남은 시간 계산
    eta_str = ""
    if progress.estimated_remaining > 0:
        eta_min = int(progress.estimated_remaining // 60)
        eta_sec = int(progress.estimated_remaining % 60)
        eta_str = f" | ETA: {eta_min}m {eta_sec}s"

    print(
        f"\r[{bar}] {progress.percentage:5.1f}% | "
        f"{progress.processed_files}/{progress.total_files} | "
        f"OK: {progress.successful}, Fail: {progress.failed} | "
        f"{progress.files_per_second:.2f} f/s{eta_str}    ",
        end="",
        flush=True
    )


def extract_batch_parallel(
    config: SMBConfig,
    database: Database,
    video_files: list,
    skip_existing: bool = True,
    verbose: bool = False,
    max_workers: int = 4
) -> dict:
    """병렬 배치 메타데이터 추출

    Args:
        config: SMB 설정
        database: 데이터베이스
        video_files: 비디오 파일 목록
        skip_existing: 이미 추출된 파일 건너뛰기
        verbose: 상세 출력
        max_workers: 병렬 워커 수

    Returns:
        추출 결과 통계
    """
    total = len(video_files)
    processed = 0
    successful = 0
    failed = 0
    skipped = 0

    start_time = datetime.now()

    # 이미 추출된 파일 필터링
    files_to_extract = []
    for file_record in video_files:
        if skip_existing and database.has_media_info(file_record.id):
            skipped += 1
            processed += 1
        else:
            files_to_extract.append(file_record)

    actual_to_process = len(files_to_extract)

    print(f"\nStarting parallel extraction for {actual_to_process} files (skipped: {skipped})...")
    print(f"Using {max_workers} parallel workers")
    print("-" * 70)

    if actual_to_process == 0:
        return {
            'total': total,
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'skipped': skipped,
            'elapsed_seconds': 0,
            'files_per_second': 0,
        }

    # 병렬 처리
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 작업 제출
        futures = {
            executor.submit(extract_single_file, (f, config)): f
            for f in files_to_extract
        }

        # 결과 수집
        for future in as_completed(futures):
            file_record, info, error = future.result()
            processed += 1

            if error:
                failed += 1
                if verbose:
                    print(f"\n[{processed}/{total}] ERROR: {file_record.filename}")
                    print(f"    Exception: {error}")
            elif info and info.extraction_status == "success":
                successful += 1
                database.insert_media_info(info)

                if verbose:
                    print(f"\n[{processed}/{total}] SUCCESS: {file_record.filename}")
                    print(f"    {info.video_codec} {info.resolution} | {info.duration_formatted}")
            else:
                failed += 1
                if info:
                    database.insert_media_info(info)

                if verbose:
                    error_msg = info.extraction_error if info else "Unknown error"
                    print(f"\n[{processed}/{total}] FAILED: {file_record.filename}")
                    print(f"    Error: {error_msg}")

            # 진행률 표시 (verbose가 아닐 때)
            if not verbose:
                elapsed = (datetime.now() - start_time).total_seconds()
                fps = processed / elapsed if elapsed > 0 else 0
                remaining = (total - processed) / fps if fps > 0 else 0

                progress = ExtractionProgress(
                    total_files=total,
                    processed_files=processed,
                    successful=successful + skipped,
                    failed=failed,
                    current_file=file_record.filename,
                    files_per_second=fps,
                    estimated_remaining=remaining,
                )
                progress_callback(progress)

            # 주기적으로 DB 커밋 (50개마다)
            if processed % 50 == 0:
                database._get_connection().commit()

    # 최종 커밋
    database._get_connection().commit()

    elapsed = (datetime.now() - start_time).total_seconds()

    return {
        'total': total,
        'processed': processed,
        'successful': successful,
        'failed': failed,
        'skipped': skipped,
        'elapsed_seconds': elapsed,
        'files_per_second': processed / elapsed if elapsed > 0 else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Media Metadata Extractor (Optimized)")
    parser.add_argument('--test', action='store_true', help="Test mode (5 files only)")
    parser.add_argument('--limit', type=int, default=0, help="Limit number of files to process")
    parser.add_argument('--skip-existing', action='store_true', default=True, help="Skip already extracted files")
    parser.add_argument('--no-skip', action='store_true', help="Re-extract all files")
    parser.add_argument('--verbose', '-v', action='store_true', help="Verbose output")
    parser.add_argument('--workers', '-w', type=int, default=4, help="Number of parallel workers (default: 4)")
    args = parser.parse_args()

    skip_existing = not args.no_skip

    print("=" * 70, flush=True)
    print("Media Metadata Extractor - Issue #10 (FR-002) [OPTIMIZED]", flush=True)
    print("=" * 70, flush=True)
    print(f"Server: {SERVER}")
    print(f"Share: {SHARE}")
    print(f"Archive: {ARCHIVE_PATH}")
    print(f"Database: {DB_PATH}")
    print(f"Mode: {'TEST' if args.test else 'FULL'}")
    print(f"Skip existing: {skip_existing}")
    print(f"Parallel workers: {args.workers}")
    print()

    # SMB 설정 (연결은 각 워커에서)
    config = SMBConfig(
        server=SERVER,
        share=SHARE,
        username=USERNAME,
        password=PASSWORD,
    )

    database = Database(DB_PATH)

    try:
        # 비디오 파일 목록 조회
        video_files = database.get_files_by_type("video", limit=100000)
        total_files = len(video_files)
        print(f"Found {total_files} video files in database")

        # 이미 추출된 파일 수 확인
        existing_count = database.get_media_info_count()
        print(f"Already extracted: {existing_count} files")
        print(f"Remaining: {total_files - existing_count} files")
        print()

        if not video_files:
            print("No video files found. Please run scan first.")
            return

        # 처리할 파일 수 결정
        if args.test:
            limit = 5
        elif args.limit > 0:
            limit = args.limit
        else:
            limit = len(video_files)

        files_to_process = video_files[:limit]

        # 병렬 배치 추출 실행
        result = extract_batch_parallel(
            config=config,
            database=database,
            video_files=files_to_process,
            skip_existing=skip_existing,
            verbose=args.verbose,
            max_workers=args.workers
        )

        print()
        print()
        print("=" * 70)
        print("EXTRACTION COMPLETE")
        print("=" * 70)
        print(f"Total files: {result['total']}")
        print(f"Processed: {result['processed']}")
        print(f"Successful: {result['successful']}")
        print(f"Failed: {result['failed']}")
        print(f"Skipped (existing): {result['skipped']}")
        print(f"Elapsed time: {result['elapsed_seconds']:.1f} seconds")
        print(f"Speed: {result['files_per_second']:.2f} files/second")
        print()

        # DB 통계 확인
        media_stats = database.get_media_statistics()
        print("Database Media Statistics:")
        print(f"  Total extracted: {media_stats['total']}")
        print(f"  Successful: {media_stats['successful']}")
        print(f"  Failed: {media_stats['failed']}")

        if media_stats['by_resolution']:
            print("  By Resolution:")
            for res, count in sorted(media_stats['by_resolution'].items(), key=lambda x: -x[1]):
                print(f"    {res}: {count}")

        if media_stats['by_codec']:
            print("  By Video Codec:")
            for codec, count in sorted(media_stats['by_codec'].items(), key=lambda x: -x[1]):
                print(f"    {codec}: {count}")

        if media_stats['total_duration_seconds'] > 0:
            hours = media_stats['total_duration_seconds'] / 3600
            print(f"  Total Duration: {hours:.1f} hours ({hours/24:.1f} days)")

    except KeyboardInterrupt:
        print("\n\nExtraction interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        database.close()
        print()
        print("Done.")


if __name__ == "__main__":
    main()
