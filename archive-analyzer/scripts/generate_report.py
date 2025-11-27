#!/usr/bin/env python
"""아카이브 분석 리포트 생성 스크립트

Issue #11: 상세 스캔 리포트 생성기 구현 (FR-005)

Usage:
    # 콘솔 출력
    python scripts/generate_report.py

    # Markdown 출력
    python scripts/generate_report.py --format markdown -o report.md

    # JSON 출력
    python scripts/generate_report.py --format json -o report.json

    # 모든 포맷 출력
    python scripts/generate_report.py --all -o data/output/
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from archive_analyzer.database import Database
from archive_analyzer.report_generator import ReportGenerator, ReportFormatter, ArchiveReport


def main():
    parser = argparse.ArgumentParser(
        description="아카이브 분석 리포트 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_report.py                           # 콘솔 출력
  python scripts/generate_report.py --format markdown         # Markdown 출력
  python scripts/generate_report.py --format json -o data.json # JSON 파일 저장
  python scripts/generate_report.py --all -o data/output/      # 모든 포맷 저장
        """
    )

    parser.add_argument(
        "--db", "-d",
        default="archive.db",
        help="데이터베이스 파일 경로 (기본: archive.db)"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["console", "markdown", "json"],
        default="console",
        help="출력 포맷 (기본: console)"
    )

    parser.add_argument(
        "--output", "-o",
        help="출력 파일 경로 (지정하지 않으면 stdout)"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="모든 포맷으로 출력 (--output은 디렉토리로 지정)"
    )

    parser.add_argument(
        "--archive-path",
        default="\\\\10.10.100.122\\docker\\GGPNAs\\ARCHIVE",
        help="아카이브 경로 (리포트에 표시용)"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="진행 메시지 숨기기"
    )

    args = parser.parse_args()

    # 데이터베이스 확인
    if not os.path.exists(args.db):
        print(f"Error: 데이터베이스 파일을 찾을 수 없습니다: {args.db}", file=sys.stderr)
        print("먼저 스캔을 실행하세요: python scripts/scan_archive.py", file=sys.stderr)
        sys.exit(1)

    # 리포트 생성
    if not args.quiet:
        print("=" * 60)
        print("  Archive Analyzer Report Generator")
        print("=" * 60)
        print(f"  Database: {args.db}")
        print(f"  Format: {args.format}")
        print()

    try:
        db = Database(args.db)
        generator = ReportGenerator(db)

        if not args.quiet:
            print("리포트 생성 중...")

        report = generator.generate(archive_path=args.archive_path)

        if not args.quiet:
            print(f"리포트 생성 완료!")
            print()

        # 출력
        if args.all:
            # 모든 포맷 출력
            output_dir = Path(args.output) if args.output else Path(".")
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Console
            console_output = ReportFormatter.to_console(report)
            print(console_output)

            # Markdown
            md_path = output_dir / f"report_{timestamp}.md"
            md_content = ReportFormatter.to_markdown(report)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"\nMarkdown 저장: {md_path}")

            # JSON
            json_path = output_dir / f"report_{timestamp}.json"
            json_content = ReportFormatter.to_json(report)
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            print(f"JSON 저장: {json_path}")

        else:
            # 단일 포맷 출력
            if args.format == "console":
                output = ReportFormatter.to_console(report)
            elif args.format == "markdown":
                output = ReportFormatter.to_markdown(report)
            elif args.format == "json":
                output = ReportFormatter.to_json(report)

            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(output)
                if not args.quiet:
                    print(f"리포트 저장: {args.output}")
            else:
                print(output)

        db.close()

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
