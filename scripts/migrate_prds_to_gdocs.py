#!/usr/bin/env python3
"""
PRD Migration Script

기존 Markdown PRD를 Google Docs로 마이그레이션하는 CLI 스크립트.

Usage:
    python scripts/migrate_prds_to_gdocs.py all                    # 전체 마이그레이션
    python scripts/migrate_prds_to_gdocs.py PRD-0001               # 특정 PRD
    python scripts/migrate_prds_to_gdocs.py list                   # 마이그레이션 대상 목록
    python scripts/migrate_prds_to_gdocs.py status                 # 현재 상태
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.google_docs import (
    GoogleDocsClient,
    MetadataManager,
    CacheManager,
)
from src.services.google_docs.migration import PRDMigrator, MigrationReport

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def cmd_list(args):
    """마이그레이션 대상 PRD 목록"""
    migrator = PRDMigrator()
    prds = migrator.discover_prds(args.source_dir)

    print(f"\n마이그레이션 대상 PRD ({len(prds)}개)")
    print("=" * 60)

    if not prds:
        print("  (대상 없음)")
        return

    for prd_id, path in prds:
        print(f"  {prd_id}: {path.name}")

    print()


def cmd_status(args):
    """현재 마이그레이션 상태"""
    metadata = MetadataManager()
    stats = metadata.get_stats()

    print("\nPRD 마이그레이션 상태")
    print("=" * 60)
    print(f"  총 PRD: {stats['total']}개")
    print(f"  다음 번호: PRD-{stats['next_number']:04d}")
    print(f"  마지막 동기화: {stats['last_sync'] or '없음'}")
    print()

    if stats["by_status"]:
        print("  상태별:")
        for status, count in stats["by_status"].items():
            print(f"    - {status}: {count}")

    if stats["by_priority"]:
        print("  우선순위별:")
        for priority, count in stats["by_priority"].items():
            print(f"    - {priority}: {count}")

    print()


def cmd_migrate_all(args):
    """전체 PRD 마이그레이션"""
    print("\n전체 PRD 마이그레이션 시작...")
    print("=" * 60)

    # 연결 테스트
    client = GoogleDocsClient()
    if not client.test_connection():
        print("오류: Google API 연결 실패")
        print("  - token_docs.json 파일 확인")
        print("  - 인터넷 연결 확인")
        return 1

    migrator = PRDMigrator(client=client)
    report = migrator.migrate_all(args.source_dir)

    # 결과 출력
    print(f"\n마이그레이션 완료!")
    print(f"  성공: {report.success_count}개")
    print(f"  실패: {report.failed_count}개")
    print(f"  총: {report.total_count}개")
    print()

    for result in report.results:
        status = "✓" if result.success else "✗"
        print(f"  {status} {result.prd_id}")
        if result.success:
            print(f"      → {result.google_doc_url}")
        else:
            print(f"      오류: {result.error}")

    # 보고서 저장
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"\n보고서 저장됨: {output_path}")

    return 0 if report.failed_count == 0 else 1


def cmd_migrate_single(args):
    """단일 PRD 마이그레이션"""
    prd_id = args.prd_id.upper()
    if not prd_id.startswith("PRD-"):
        prd_id = f"PRD-{prd_id}"

    print(f"\n{prd_id} 마이그레이션 시작...")
    print("=" * 60)

    # 연결 테스트
    client = GoogleDocsClient()
    if not client.test_connection():
        print("오류: Google API 연결 실패")
        return 1

    migrator = PRDMigrator(client=client)
    result = migrator.migrate_prd(prd_id, args.source_path)

    if result.success:
        print(f"\n✓ 마이그레이션 성공!")
        print(f"  PRD ID: {result.prd_id}")
        print(f"  Google Docs: {result.google_doc_url}")
    else:
        print(f"\n✗ 마이그레이션 실패")
        print(f"  오류: {result.error}")
        return 1

    return 0


def cmd_sync(args):
    """PRD 동기화 (Google Docs → 로컬 캐시)"""
    cache = CacheManager()

    if args.prd_id:
        prd_id = args.prd_id.upper()
        if not prd_id.startswith("PRD-"):
            prd_id = f"PRD-{prd_id}"

        print(f"\n{prd_id} 동기화 중...")
        success = cache.sync_prd(prd_id)

        if success:
            print(f"✓ 동기화 완료")
            info = cache.get_cache_info(prd_id)
            if info:
                print(f"  캐시: {info['path']}")
                print(f"  크기: {info['size']} bytes")
        else:
            print("✗ 동기화 실패")
            return 1
    else:
        print("\n전체 PRD 동기화 중...")
        results = cache.sync_all()
        success_count = sum(1 for v in results.values() if v)
        print(f"\n✓ 동기화 완료: {success_count}/{len(results)}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="PRD를 Google Docs로 마이그레이션",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  python scripts/migrate_prds_to_gdocs.py list
  python scripts/migrate_prds_to_gdocs.py all
  python scripts/migrate_prds_to_gdocs.py PRD-0001
  python scripts/migrate_prds_to_gdocs.py sync PRD-0001
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="명령")

    # list 명령
    list_parser = subparsers.add_parser("list", help="마이그레이션 대상 목록")
    list_parser.add_argument(
        "--source-dir",
        default="tasks/prds/",
        help="PRD 디렉토리 (기본: tasks/prds/)",
    )

    # status 명령
    subparsers.add_parser("status", help="현재 상태")

    # all 명령
    all_parser = subparsers.add_parser("all", help="전체 마이그레이션")
    all_parser.add_argument(
        "--source-dir",
        default="tasks/prds/",
        help="PRD 디렉토리 (기본: tasks/prds/)",
    )
    all_parser.add_argument(
        "--output",
        "-o",
        help="보고서 출력 파일 (JSON)",
    )

    # 단일 PRD 마이그레이션
    single_parser = subparsers.add_parser("migrate", help="단일 PRD 마이그레이션")
    single_parser.add_argument("prd_id", help="PRD ID (예: PRD-0001)")
    single_parser.add_argument(
        "--source-path",
        help="원본 파일 경로 (없으면 자동 검색)",
    )

    # sync 명령
    sync_parser = subparsers.add_parser("sync", help="PRD 동기화")
    sync_parser.add_argument(
        "prd_id",
        nargs="?",
        help="PRD ID (없으면 전체 동기화)",
    )

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "all":
        return cmd_migrate_all(args)
    elif args.command == "migrate":
        return cmd_migrate_single(args)
    elif args.command == "sync":
        return cmd_sync(args)
    else:
        # PRD-NNNN 형식이면 단일 마이그레이션으로 처리
        if args.command and (
            args.command.upper().startswith("PRD-")
            or args.command.isdigit()
        ):
            args.prd_id = args.command
            args.source_path = None
            return cmd_migrate_single(args)

        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
