"""
Google Docs PRD Converter CLI

마크다운 PRD를 Google Docs로 변환하는 CLI 인터페이스
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

from .auth import DEFAULT_FOLDER_ID
from .converter import create_google_doc


def process_file(
    file_path: Path,
    folder_id: Optional[str] = None,
    include_toc: bool = False,
    use_native_tables: bool = True,
    custom_title: Optional[str] = None,
) -> Optional[str]:
    """
    단일 파일 처리

    Args:
        file_path: 마크다운 파일 경로
        folder_id: Google Drive 폴더 ID
        include_toc: 목차 포함 여부
        use_native_tables: 네이티브 테이블 사용 여부
        custom_title: 커스텀 문서 제목

    Returns:
        str | None: 생성된 문서 URL 또는 실패 시 None
    """
    if not file_path.exists():
        print(f"[FAIL] 파일을 찾을 수 없습니다: {file_path}")
        return None

    content = file_path.read_text(encoding='utf-8')

    # 제목 추출 (첫 번째 H1 또는 파일명)
    if custom_title:
        title = custom_title
    else:
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem

    print(f"\n[FILE] {file_path.name}")
    print(f"       제목: {title}")

    try:
        doc_url = create_google_doc(
            title=title,
            content=content,
            folder_id=folder_id,
            include_toc=include_toc,
            use_native_tables=use_native_tables,
        )
        print(f"[OK] {doc_url}")
        return doc_url
    except Exception as e:
        print(f"[FAIL] {e}")
        return None


def main():
    """CLI 메인 함수"""
    parser = argparse.ArgumentParser(
        prog='python -m lib.google_docs',
        description='PRD 마크다운을 Google Docs 네이티브 형식으로 변환',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 단일 파일 변환
  python -m lib.google_docs convert file.md

  # 커스텀 제목으로 변환
  python -m lib.google_docs convert file.md --title "My PRD"

  # 목차 포함
  python -m lib.google_docs convert file.md --toc

  # 네이티브 테이블 사용 (실험적)
  python -m lib.google_docs convert file.md --native-tables

  # 배치 변환
  python -m lib.google_docs batch tasks/prds/*.md

  # 폴더에 문서 목록 조회
  python -m lib.google_docs list
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='명령')

    # convert 명령
    convert_parser = subparsers.add_parser('convert', help='마크다운을 Google Docs로 변환')
    convert_parser.add_argument('file', help='마크다운 파일 경로')
    convert_parser.add_argument('--title', '-t', help='문서 제목 (기본: 파일에서 추출)')
    convert_parser.add_argument('--folder', '-f', default=DEFAULT_FOLDER_ID,
                                help=f'Google Drive 폴더 ID (기본: {DEFAULT_FOLDER_ID[:15]}...)')
    convert_parser.add_argument('--toc', action='store_true', help='목차 포함')
    convert_parser.add_argument('--native-tables', action='store_true',
                                help='네이티브 Google Docs 테이블 사용 (실험적)')
    convert_parser.add_argument('--no-folder', action='store_true',
                                help='폴더 이동 없이 내 드라이브에 생성')

    # batch 명령
    batch_parser = subparsers.add_parser('batch', help='여러 파일 배치 변환')
    batch_parser.add_argument('files', nargs='+', help='마크다운 파일들 (glob 패턴 지원)')
    batch_parser.add_argument('--folder', '-f', default=DEFAULT_FOLDER_ID,
                              help='Google Drive 폴더 ID')
    batch_parser.add_argument('--toc', action='store_true', help='목차 포함')
    batch_parser.add_argument('--native-tables', action='store_true',
                              help='네이티브 Google Docs 테이블 사용 (실험적)')

    # list 명령
    list_parser = subparsers.add_parser('list', help='폴더의 문서 목록 조회')
    list_parser.add_argument('--folder', '-f', default=DEFAULT_FOLDER_ID,
                             help='Google Drive 폴더 ID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    print("=" * 60)
    print("Google Docs PRD Converter")
    print("=" * 60)

    if args.command == 'convert':
        folder_id = None if args.no_folder else args.folder
        use_native = args.native_tables

        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path

        result = process_file(
            file_path=file_path,
            folder_id=folder_id,
            include_toc=args.toc,
            use_native_tables=use_native,
            custom_title=args.title,
        )

        print("\n" + "=" * 60)
        if result:
            print(f"[SUCCESS] 문서 생성 완료: {result}")
        else:
            print("[FAILED] 문서 생성 실패")
            sys.exit(1)

    elif args.command == 'batch':
        use_native = args.native_tables

        # 파일 목록 수집
        files = []
        for pattern in args.files:
            path = Path(pattern)
            if '*' in pattern:
                # glob 패턴
                if path.is_absolute():
                    files.extend(path.parent.glob(path.name))
                else:
                    files.extend(Path.cwd().glob(pattern))
            else:
                if not path.is_absolute():
                    path = Path.cwd() / path
                files.append(path)

        print(f"파일 수: {len(files)}")
        print(f"폴더 ID: {args.folder}")
        print(f"테이블: {'네이티브' if use_native else '텍스트'}")
        print("=" * 60)

        results = []
        for file_path in files:
            result = process_file(
                file_path=file_path,
                folder_id=args.folder,
                include_toc=args.toc,
                use_native_tables=use_native,
            )
            results.append((file_path, result))

        # 결과 요약
        print("\n" + "=" * 60)
        print("결과 요약")
        print("=" * 60)

        success_count = sum(1 for _, url in results if url)
        print(f"성공: {success_count}/{len(results)}")

        for file_path, url in results:
            status = "[OK]" if url else "[FAIL]"
            print(f"  {status} {file_path.name}")
            if url:
                print(f"       {url}")

    elif args.command == 'list':
        from googleapiclient.discovery import build
        from .auth import get_credentials

        creds = get_credentials()
        drive_service = build('drive', 'v3', credentials=creds)

        query = f"'{args.folder}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"

        results = drive_service.files().list(
            q=query,
            pageSize=50,
            fields="files(id, name, modifiedTime, webViewLink)"
        ).execute()

        files = results.get('files', [])

        print(f"\n문서 목록 ({len(files)}개):")
        print("-" * 60)
        for f in files:
            print(f"  • {f['name']}")
            print(f"    {f['webViewLink']}")
            print()

    print("=" * 60)


if __name__ == '__main__':
    main()
