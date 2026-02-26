#!/usr/bin/env python3
"""
Mermaid 다이어그램 노드 레이블 \n 리터럴 → <br/> 일괄 변환 스크립트

사용법:
  # 단일 파일 수정
  python scripts/sanitize_mermaid.py docs/02-design/some-file.design.md

  # 디렉토리 전체 수정 (재귀)
  python scripts/sanitize_mermaid.py docs/

  # 변경사항 확인만 (dry-run)
  python scripts/sanitize_mermaid.py docs/ --dry-run

  # 백업 없이 수정
  python scripts/sanitize_mermaid.py docs/ --no-backup

배경:
  Mermaid 노드 레이블에서 \\n (백슬래시+n 두 글자)은 GitHub/VS Code에서
  줄바꿈으로 처리되지 않는다. <br/> 태그를 사용해야 모든 렌더러에서 동작한다.
  참조: .claude/rules/11-ascii-diagram.md
"""
import re
import sys
import shutil
from pathlib import Path
from typing import Optional


def fix_mermaid_label_newlines(content: str) -> tuple[str, int]:
    """
    Mermaid 블록 내 노드 레이블의 \\n 리터럴을 <br/>로 교체.

    Returns:
        (수정된 콘텐츠, 교체 횟수)
    """
    total_replacements = 0

    def fix_block(match: re.Match) -> str:
        nonlocal total_replacements
        prefix = match.group(1)   # ```mermaid\n
        block = match.group(2)    # 블록 내용
        suffix = match.group(3)   # ```

        def fix_quoted_label(q_match: re.Match) -> str:
            nonlocal total_replacements
            original = q_match.group(0)
            # 실제 \n (두 글자: 백슬래시 + n)을 <br/>로 교체
            fixed = original.replace('\\n', '<br/>')
            if fixed != original:
                count = original.count('\\n')
                total_replacements += count
            return fixed

        # 따옴표 안에서만 \n 교체 (라벨 내부)
        fixed_block = re.sub(r'"[^"]*\\n[^"]*"', fix_quoted_label, block)
        return prefix + fixed_block + suffix

    # ```mermaid ... ``` 블록 탐지 및 수정
    result = re.sub(
        r'(```mermaid\n)([\s\S]*?)(```)',
        fix_block,
        content
    )
    return result, total_replacements


def process_file(
    file_path: Path,
    dry_run: bool = False,
    backup: bool = True
) -> Optional[int]:
    """
    단일 파일 처리.

    Returns:
        교체 횟수 (변경 없으면 0, 오류 시 None)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  [ERROR] 읽기 실패: {e}")
        return None

    fixed_content, count = fix_mermaid_label_newlines(content)

    if count == 0:
        return 0

    if dry_run:
        print(f"  [DRY-RUN] {count}개 교체 예정")
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '\\n' in line and '"' in line:
                print(f"    L{i+1}: {line[:100].strip()}")
        return count

    # 백업 생성
    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        shutil.copy2(file_path, backup_path)

    # 수정된 내용 저장
    try:
        file_path.write_text(fixed_content, encoding='utf-8')
        print(f"  [OK] {count}개 \\n → <br/> 교체됨" + (f" (백업: {file_path.name}.bak)" if backup else ""))
    except Exception as e:
        print(f"  [ERROR] 쓰기 실패: {e}")
        return None

    return count


def process_directory(
    dir_path: Path,
    dry_run: bool = False,
    backup: bool = True
) -> tuple[int, int, int]:
    """
    디렉토리 재귀 처리.

    Returns:
        (처리 파일 수, 수정 파일 수, 총 교체 횟수)
    """
    processed = 0
    modified = 0
    total_replacements = 0

    for md_file in sorted(dir_path.rglob('*.md')):
        if any(part.startswith('.') for part in md_file.parts if part != '.'):
            continue
        if 'node_modules' in str(md_file):
            continue

        processed += 1
        print(f"\n{md_file.relative_to(dir_path)}")

        count = process_file(md_file, dry_run=dry_run, backup=backup)
        if count is None:
            continue
        if count > 0:
            modified += 1
            total_replacements += count
        else:
            print("  (변경 없음)")

    return processed, modified, total_replacements


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Mermaid 노드 레이블 \\n → <br/> 일괄 변환',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('target', help='파일 또는 디렉토리 경로')
    parser.add_argument('--dry-run', action='store_true', help='변경사항 미리 보기만 (실제 수정 없음)')
    parser.add_argument('--no-backup', action='store_true', help='백업 파일(.bak) 생성 안 함')

    args = parser.parse_args()

    target = Path(args.target)
    dry_run = args.dry_run
    backup = not args.no_backup

    if not target.exists():
        print(f"[ERROR] 경로가 존재하지 않습니다: {target}")
        sys.exit(1)

    print(f"=== Mermaid \\n 리터럴 제거 {'[DRY-RUN]' if dry_run else ''} ===")
    print(f"대상: {target.resolve()}")
    print(f"백업: {'비활성화' if not backup else '활성화 (.bak)'}")
    print()

    if target.is_file():
        if target.suffix.lower() != '.md':
            print(f"[WARN] .md 파일이 아닙니다: {target}")
        print(f"{target.name}")
        count = process_file(target, dry_run=dry_run, backup=backup)
        if count is not None:
            print(f"\n완료: {count}개 교체")
    else:
        processed, modified, total = process_directory(target, dry_run=dry_run, backup=backup)
        print(f"\n=== 완료 ===")
        print(f"처리: {processed}개 파일")
        print(f"수정: {modified}개 파일")
        print(f"교체: {total}개 \\n → <br/>")
        if dry_run and total > 0:
            print(f"\n실제 적용: python scripts/sanitize_mermaid.py {target}")


if __name__ == '__main__':
    main()
