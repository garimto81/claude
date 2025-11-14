#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Quality Migration: v1.0 → v2.0
.agent-quality.jsonl → .agent-quality-v2.jsonl

v1.0 format:
{
  "timestamp": "...",
  "agent": "debugger",
  "task": "Fix bug",
  "status": "pass",
  "score": 4.5,  // 제거됨
  "duration": 1.5,
  "error": null,
  "auto_detected": false
}

v2.0 format:
{
  "timestamp": "...",
  "agent": "debugger",
  "version": "1.0.0",  // 추가됨
  "task": "Fix bug",
  "status": "pass",
  // score 필드 제거 (동적 계산)
  "duration": 1.5,
  "error": null,
  "auto_detected": false
}

Usage:
    python migrate_v1_to_v2.py
    python migrate_v1_to_v2.py --input custom.jsonl --output custom-v2.jsonl
    python migrate_v1_to_v2.py --dry-run  # 테스트만
"""

import json
import argparse
from pathlib import Path
from typing import Dict


def migrate_log_entry(entry: Dict) -> Dict:
    """v1.0 로그 엔트리를 v2.0 포맷으로 변환"""
    migrated = {}

    # 필수 필드 복사
    migrated["timestamp"] = entry["timestamp"]
    migrated["agent"] = entry["agent"]
    migrated["task"] = entry["task"]
    migrated["status"] = entry["status"]

    # version 추가 (v1.0에는 없음)
    migrated["version"] = entry.get("version", "1.0.0")

    # 선택 필드 복사
    if "phase" in entry and entry["phase"] is not None:
        migrated["phase"] = entry["phase"]

    if "duration" in entry:
        migrated["duration"] = entry["duration"]
    else:
        migrated["duration"] = 0

    if "error" in entry and entry["error"] is not None:
        migrated["error"] = entry["error"]

    if "auto_detected" in entry:
        migrated["auto_detected"] = entry["auto_detected"]
    else:
        migrated["auto_detected"] = False

    if "test_output" in entry and entry["test_output"] is not None:
        migrated["test_output"] = entry["test_output"]

    # "score" 필드는 의도적으로 제외 (v2.0에서는 동적 계산)

    return migrated


def migrate_file(input_path: Path, output_path: Path, dry_run: bool = False) -> Dict:
    """파일 마이그레이션"""
    if not input_path.exists():
        return {
            "success": False,
            "error": f"입력 파일이 없습니다: {input_path}"
        }

    # 기존 v2.0 파일 체크
    if output_path.exists() and not dry_run:
        return {
            "success": False,
            "error": f"출력 파일이 이미 존재합니다: {output_path}\n"
                    f"기존 파일을 백업하거나 삭제한 후 다시 시도하세요."
        }

    stats = {
        "total": 0,
        "migrated": 0,
        "skipped": 0,
        "errors": []
    }

    # 마이그레이션
    migrated_entries = []

    with open(input_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            stats["total"] += 1

            try:
                entry = json.loads(line.strip())

                # v1.0 필드 검증 ("score" 필드가 있으면 v1.0)
                if "score" in entry:
                    migrated = migrate_log_entry(entry)
                    migrated_entries.append(migrated)
                    stats["migrated"] += 1
                else:
                    # 이미 v2.0 형식일 수 있음
                    if "version" in entry:
                        # v2.0 형식
                        stats["skipped"] += 1
                        stats["errors"].append(f"Line {line_num}: 이미 v2.0 형식")
                    else:
                        # 알 수 없는 형식
                        stats["skipped"] += 1
                        stats["errors"].append(f"Line {line_num}: 알 수 없는 형식")

            except json.JSONDecodeError as e:
                stats["skipped"] += 1
                stats["errors"].append(f"Line {line_num}: JSON 파싱 실패 - {e}")
            except KeyError as e:
                stats["skipped"] += 1
                stats["errors"].append(f"Line {line_num}: 필수 필드 누락 - {e}")

    # 출력 (dry-run이 아닌 경우)
    if not dry_run and migrated_entries:
        with open(output_path, 'w') as f:
            for entry in migrated_entries:
                f.write(json.dumps(entry) + '\n')

    return {
        "success": True,
        "stats": stats,
        "dry_run": dry_run
    }


def print_report(result: Dict):
    """마이그레이션 결과 출력"""
    if not result["success"]:
        print(f"❌ 실패: {result['error']}")
        return

    stats = result["stats"]
    dry_run = result["dry_run"]

    print(f"\n{'='*60}")
    if dry_run:
        print("🔍 Dry Run - Migration Preview")
    else:
        print("✅ Migration Complete")
    print(f"{'='*60}\n")

    print(f"총 로그: {stats['total']}")
    print(f"마이그레이션: {stats['migrated']}")
    print(f"스킵: {stats['skipped']}")

    if stats['errors']:
        print(f"\n⚠️ 경고 ({len(stats['errors'])}개):")
        for error in stats['errors'][:10]:  # 최대 10개만
            print(f"  - {error}")

        if len(stats['errors']) > 10:
            print(f"  ... 외 {len(stats['errors']) - 10}개")

    print()

    if dry_run:
        print("💡 실제 마이그레이션을 수행하려면 --dry-run 옵션을 제거하세요.")
    elif stats['migrated'] > 0:
        print("✅ v2.0 로그 파일이 생성되었습니다.")
        print("💡 이제 analyze_quality2.py를 사용하여 분석할 수 있습니다.")


def main():
    parser = argparse.ArgumentParser(
        description="Agent Quality Migration: v1.0 → v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # 기본 마이그레이션
  python migrate_v1_to_v2.py

  # Dry run (테스트)
  python migrate_v1_to_v2.py --dry-run

  # 커스텀 파일
  python migrate_v1_to_v2.py --input old.jsonl --output new.jsonl

  # 백업 생성
  python migrate_v1_to_v2.py --backup
"""
    )

    parser.add_argument(
        '--input',
        type=Path,
        default=Path('.agent-quality.jsonl'),
        help='입력 파일 (v1.0 형식, 기본: .agent-quality.jsonl)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('.agent-quality-v2.jsonl'),
        help='출력 파일 (v2.0 형식, 기본: .agent-quality-v2.jsonl)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 변환하지 않고 테스트만 수행'
    )

    parser.add_argument(
        '--backup',
        action='store_true',
        help='입력 파일을 .bak으로 백업'
    )

    args = parser.parse_args()

    # 백업 생성
    if args.backup and args.input.exists() and not args.dry_run:
        backup_path = args.input.with_suffix('.jsonl.bak')
        import shutil
        shutil.copy2(args.input, backup_path)
        print(f"✅ 백업 생성: {backup_path}")

    # 마이그레이션
    result = migrate_file(args.input, args.output, args.dry_run)

    # 결과 출력
    print_report(result)

    # Exit code
    if not result["success"]:
        exit(1)


if __name__ == "__main__":
    main()
