"""
Google Docs PRD 동기화 스크립트 (전역)

모든 프로젝트에서 CLAUDE.md에 등록된 Google Docs와 로컬 Markdown 파일 동기화

사용법:
    # 현재 디렉토리의 프로젝트 동기화
    python C:\\claude\\scripts\\prd_sync.py check
    python C:\\claude\\scripts\\prd_sync.py pull
    python C:\\claude\\scripts\\prd_sync.py push

    # 특정 프로젝트 지정
    python C:\\claude\\scripts\\prd_sync.py check --project wsoptv_nbatv_clone
    python C:\\claude\\scripts\\prd_sync.py pull --project wsoptv_ott

    # 루트에서 실행
    cd C:\\claude && python -m scripts.prd_sync check --project wsoptv_nbatv_clone
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 루트 디렉토리
CLAUDE_ROOT = Path(r"C:\claude")

# 인증 파일 경로 (항상 루트의 json 폴더 사용)
CREDENTIALS_FILE = CLAUDE_ROOT / "json" / "desktop_credentials.json"
TOKEN_FILE = CLAUDE_ROOT / "json" / "token.json"

# Google Docs API 범위
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


@dataclass
class DocMapping:
    """문서 매핑 정보"""
    doc_id: str
    doc_title: str
    local_path: Path
    version: str
    sync_date: str
    project_root: Path


def get_credentials() -> Credentials:
    """OAuth 2.0 인증 정보 획득"""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def detect_project_root(project_name: Optional[str] = None) -> Optional[Path]:
    """
    프로젝트 루트 디렉토리 결정

    우선순위:
    1. --project 인자로 지정된 프로젝트
    2. 현재 작업 디렉토리
    3. 현재 디렉토리의 부모 디렉토리 (scripts/ 에서 실행 시)
    """
    if project_name:
        # 프로젝트 이름으로 경로 결정
        project_path = CLAUDE_ROOT / project_name
        if project_path.exists() and (project_path / "CLAUDE.md").exists():
            return project_path
        print(f"[ERROR] Project not found: {project_path}")
        return None

    # 현재 디렉토리 확인
    cwd = Path.cwd()

    # 현재 디렉토리에 CLAUDE.md가 있으면 사용
    if (cwd / "CLAUDE.md").exists():
        return cwd

    # 부모 디렉토리 확인 (scripts/ 에서 실행 시)
    if cwd.name == "scripts" and (cwd.parent / "CLAUDE.md").exists():
        return cwd.parent

    # C:\claude 하위 디렉토리인지 확인
    try:
        rel_path = cwd.relative_to(CLAUDE_ROOT)
        # 첫 번째 디렉토리가 프로젝트
        parts = rel_path.parts
        if parts:
            project_path = CLAUDE_ROOT / parts[0]
            if (project_path / "CLAUDE.md").exists():
                return project_path
    except ValueError:
        pass

    print("[ERROR] Cannot detect project root. Use --project option.")
    return None


def list_available_projects() -> List[str]:
    """동기화 가능한 프로젝트 목록"""
    projects = []
    for path in CLAUDE_ROOT.iterdir():
        if path.is_dir() and (path / "CLAUDE.md").exists():
            claude_md = (path / "CLAUDE.md").read_text(encoding="utf-8")
            # Google Docs 매핑이 있는 프로젝트만
            if re.search(r'\|\s*\*\*.+?\*\*\s*\|\s*`[a-zA-Z0-9_-]+`', claude_md):
                projects.append(path.name)
    return sorted(projects)


def parse_claude_md(project_root: Path) -> Optional[DocMapping]:
    """CLAUDE.md에서 Google Docs 매핑 정보 파싱"""
    claude_md_path = project_root / "CLAUDE.md"

    if not claude_md_path.exists():
        print(f"[ERROR] CLAUDE.md not found: {claude_md_path}")
        return None

    content = claude_md_path.read_text(encoding="utf-8")

    # Google Docs ID 추출 (테이블에서)
    # | **WSOP TV PRD** | `1VE0StXfXN5-cUGXSLFTNp280VgTHxEHgRHaDrNUtBBo` | v5.1.0 | 2026-01-26 |
    doc_pattern = r'\|\s*\*\*(.+?)\*\*\s*\|\s*`([a-zA-Z0-9_-]+)`\s*\|\s*v?([\d.]+)\s*\|\s*([\d-]+)\s*\|'

    match = re.search(doc_pattern, content)
    if not match:
        print(f"[ERROR] Google Docs mapping not found in {claude_md_path}")
        print("       Required format:")
        print("       | **문서명** | `DOC_ID` | v1.0.0 | 2026-01-26 |")
        return None

    doc_title = match.group(1)
    doc_id = match.group(2)
    version = match.group(3)
    sync_date = match.group(4)

    # 로컬 파일 경로 추출
    # 로컬 PRD (`docs/guides/WSOP-TV-PRD.md` v5.1.0)
    local_pattern = r'`(docs/[^`]+\.md)`'
    local_match = re.search(local_pattern, content)

    if local_match:
        local_path = project_root / local_match.group(1)
    else:
        # 기본 경로 탐색
        default_paths = [
            project_root / "docs" / "guides",
            project_root / "docs" / "prds",
            project_root / "docs",
        ]
        local_path = None
        for default_dir in default_paths:
            if default_dir.exists():
                md_files = list(default_dir.glob("*.md"))
                if md_files:
                    local_path = md_files[0]
                    break

        if not local_path:
            local_path = project_root / "docs" / "PRD.md"

    return DocMapping(
        doc_id=doc_id,
        doc_title=doc_title,
        local_path=local_path,
        version=version,
        sync_date=sync_date,
        project_root=project_root
    )


def extract_text_from_doc(doc: dict) -> str:
    """Google Docs 문서에서 텍스트 추출"""
    body = doc.get("body", {})
    content = body.get("content", [])

    text_parts = []

    def process_element(element):
        if "paragraph" in element:
            para = element["paragraph"]
            para_style = para.get("paragraphStyle", {})
            named_style = para_style.get("namedStyleType", "")

            line_parts = []
            for elem in para.get("elements", []):
                if "textRun" in elem:
                    line_parts.append(elem["textRun"].get("content", ""))

            line = "".join(line_parts)

            # 헤딩 처리
            if "HEADING" in named_style:
                level = int(named_style.replace("HEADING_", ""))
                prefix = "#" * level + " "
                line = prefix + line.strip() + "\n"

            text_parts.append(line)

        elif "table" in element:
            table = element["table"]
            rows = table.get("tableRows", [])

            for row_idx, row in enumerate(rows):
                cells = row.get("tableCells", [])
                row_parts = []

                for cell in cells:
                    cell_text = []
                    for cell_content in cell.get("content", []):
                        if "paragraph" in cell_content:
                            for elem in cell_content["paragraph"].get("elements", []):
                                if "textRun" in elem:
                                    cell_text.append(elem["textRun"].get("content", "").strip())
                    row_parts.append(" ".join(cell_text))

                text_parts.append("| " + " | ".join(row_parts) + " |\n")

                # 헤더 구분선
                if row_idx == 0:
                    text_parts.append("|" + "|".join(["---"] * len(cells)) + "|\n")

            text_parts.append("\n")

    for element in content:
        process_element(element)

    return "".join(text_parts)


def get_doc_content(doc_id: str) -> Tuple[str, dict]:
    """Google Docs 문서 내용 조회"""
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)

    doc = docs_service.documents().get(documentId=doc_id).execute()
    text = extract_text_from_doc(doc)

    return text, doc


def get_local_content(local_path: Path) -> str:
    """로컬 Markdown 파일 내용 조회"""
    if not local_path.exists():
        return ""
    return local_path.read_text(encoding="utf-8")


def compare_documents(gdocs_text: str, local_text: str) -> dict:
    """문서 비교"""
    gdocs_lines = gdocs_text.strip().split("\n")
    local_lines = local_text.strip().split("\n")

    # 간단한 비교 (줄 수, 문자 수)
    return {
        "gdocs_lines": len(gdocs_lines),
        "local_lines": len(local_lines),
        "gdocs_chars": len(gdocs_text),
        "local_chars": len(local_text),
        "line_diff": len(gdocs_lines) - len(local_lines),
        "char_diff": len(gdocs_text) - len(local_text),
        "identical": gdocs_text.strip() == local_text.strip()
    }


def update_claude_md_sync_date(project_root: Path, doc_title: str, sync_date: str):
    """CLAUDE.md의 동기화 날짜 업데이트"""
    claude_md_path = project_root / "CLAUDE.md"
    content = claude_md_path.read_text(encoding="utf-8")

    # 문서 제목을 기준으로 날짜 패턴 교체 (더 범용적)
    escaped_title = re.escape(doc_title)
    pattern = rf'(\|\s*\*\*{escaped_title}\*\*\s*\|\s*`[^`]+`\s*\|\s*v?[\d.]+\s*\|\s*)[\d-]+(\s*\|)'

    updated = re.sub(pattern, rf'\g<1>{sync_date}\2', content)

    claude_md_path.write_text(updated, encoding="utf-8")


def cmd_check(mapping: DocMapping) -> dict:
    """차이점 확인"""
    print("=" * 60)
    print("Google Docs PRD Sync Status")
    print("=" * 60)
    print(f"Project: {mapping.project_root.name}")
    print(f"Document: {mapping.doc_title}")
    print(f"Doc ID: {mapping.doc_id}")
    print(f"Local: {mapping.local_path}")
    print(f"Version: v{mapping.version}")
    print(f"Last Sync: {mapping.sync_date}")
    print()

    print("[1/2] Fetching Google Docs...")
    gdocs_text, doc = get_doc_content(mapping.doc_id)

    print("[2/2] Reading local file...")
    local_text = get_local_content(mapping.local_path)

    print()
    comparison = compare_documents(gdocs_text, local_text)

    print("=" * 60)
    print("Comparison Result")
    print("=" * 60)
    print(f"Google Docs: {comparison['gdocs_lines']:,} lines, {comparison['gdocs_chars']:,} chars")
    print(f"Local file:  {comparison['local_lines']:,} lines, {comparison['local_chars']:,} chars")
    print()

    if comparison['identical']:
        print("Status: [SYNC] Synchronized")
    else:
        print("Status: [DIFF] Differences found")
        print(f"  Line diff: {comparison['line_diff']:+d}")
        print(f"  Char diff: {comparison['char_diff']:+d}")

        if comparison['gdocs_chars'] > comparison['local_chars']:
            print("  -> Google Docs is newer (pull recommended)")
        else:
            print("  -> Local is newer (push recommended)")

    return comparison


def cmd_pull(mapping: DocMapping, force: bool = False):
    """Google Docs -> Local sync"""
    print("=" * 60)
    print("Google Docs -> Local Sync (pull)")
    print("=" * 60)

    # Check first
    comparison = cmd_check(mapping)

    if comparison['identical'] and not force:
        print("\nAlready synchronized.")
        return

    print()
    if not force:
        confirm = input("Overwrite local file? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return

    print("\nSyncing...")
    gdocs_text, _ = get_doc_content(mapping.doc_id)

    # Create backup
    backup_path = mapping.local_path.with_suffix(".md.bak")
    if mapping.local_path.exists():
        import shutil
        shutil.copy(mapping.local_path, backup_path)
        print(f"Backup created: {backup_path}")

    # Save file
    mapping.local_path.parent.mkdir(parents=True, exist_ok=True)
    mapping.local_path.write_text(gdocs_text, encoding="utf-8")
    print(f"Saved: {mapping.local_path}")

    # Update sync date
    today = datetime.now().strftime("%Y-%m-%d")
    update_claude_md_sync_date(mapping.project_root, mapping.doc_title, today)
    print(f"CLAUDE.md sync date updated: {today}")

    print("\n[DONE] Sync complete!")


def cmd_push(mapping: DocMapping, force: bool = False):
    """Local -> Google Docs sync (update existing document, preserve ID)"""
    print("=" * 60)
    print("Local -> Google Docs Sync (push)")
    print("=" * 60)

    # Check first
    comparison = cmd_check(mapping)

    if comparison['identical'] and not force:
        print("\nAlready synchronized.")
        return

    print()
    if not force:
        confirm = input("Update Google Docs? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled")
            return

    print("\nSyncing...")
    print(f"[INFO] Doc ID 고정: {mapping.doc_id}")
    print(f"       Running: python -m lib.google_docs update {mapping.doc_id} \"{mapping.local_path}\"")

    import subprocess
    result = subprocess.run(
        [
            "python", "-m", "lib.google_docs", "update",
            mapping.doc_id,
            str(mapping.local_path)
        ],
        cwd=str(CLAUDE_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    if result.returncode == 0:
        print(stdout)

        # Update sync date (Doc ID는 변경되지 않음)
        today = datetime.now().strftime("%Y-%m-%d")
        update_claude_md_sync_date(mapping.project_root, mapping.doc_title, today)
        print(f"       Sync date: {today}")

        print("\n[DONE] Sync complete!")
    else:
        print(f"[ERROR] Update failed:")
        print(stderr)


def cmd_list():
    """List projects with Google Docs sync configured"""
    print("=" * 60)
    print("Projects with Google Docs Sync")
    print("=" * 60)

    projects = list_available_projects()

    if not projects:
        print("No projects found with Google Docs mapping.")
        return

    for project in projects:
        project_root = CLAUDE_ROOT / project
        mapping = parse_claude_md(project_root)
        if mapping:
            print(f"\n{project}/")
            print(f"  Document: {mapping.doc_title}")
            print(f"  Version:  v{mapping.version}")
            print(f"  Sync:     {mapping.sync_date}")


def main():
    parser = argparse.ArgumentParser(
        description="Google Docs PRD Sync (Global)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check sync status (auto-detect project)
  python C:\\claude\\scripts\\prd_sync.py check

  # Specify project
  python C:\\claude\\scripts\\prd_sync.py check --project wsoptv_nbatv_clone

  # Pull from Google Docs
  python C:\\claude\\scripts\\prd_sync.py pull --project wsoptv_ott

  # Push to Google Docs
  python C:\\claude\\scripts\\prd_sync.py push --force

  # List all projects
  python C:\\claude\\scripts\\prd_sync.py list
"""
    )

    parser.add_argument(
        "action",
        choices=["check", "pull", "push", "list"],
        help="Action: check, pull (GDocs->Local), push (Local->GDocs), list"
    )
    parser.add_argument(
        "--project", "-p",
        help="Project name (e.g., wsoptv_nbatv_clone)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force execution without confirmation"
    )

    args = parser.parse_args()

    # List command doesn't need project
    if args.action == "list":
        cmd_list()
        return

    # Detect project root
    project_root = detect_project_root(args.project)
    if not project_root:
        print("\nAvailable projects:")
        for p in list_available_projects():
            print(f"  - {p}")
        sys.exit(1)

    # Parse CLAUDE.md
    mapping = parse_claude_md(project_root)
    if not mapping:
        sys.exit(1)

    # Execute action
    if args.action == "check":
        cmd_check(mapping)
    elif args.action == "pull":
        cmd_pull(mapping, force=args.force)
    elif args.action == "push":
        cmd_push(mapping, force=args.force)


if __name__ == "__main__":
    main()
