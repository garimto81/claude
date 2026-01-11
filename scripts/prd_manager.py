#!/usr/bin/env python3
"""
PRD Manager - Google Docs PRD 동기화 CLI

Usage:
    python scripts/prd_manager.py sync PRD-0001    # 특정 PRD 동기화
    python scripts/prd_manager.py sync --all       # 모든 PRD 동기화
    python scripts/prd_manager.py list             # PRD 목록 조회
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 프로젝트 루트 설정
PROJECT_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = PROJECT_ROOT / ".prd-registry.json"
CACHE_DIR = PROJECT_ROOT / "tasks" / "prds"

# lib/google_docs 임포트
sys.path.insert(0, str(PROJECT_ROOT / "lib"))
try:
    from google_docs.auth import get_credentials, build_docs_service
    GOOGLE_DOCS_AVAILABLE = True
except ImportError:
    GOOGLE_DOCS_AVAILABLE = False


def load_registry() -> Dict[str, Any]:
    """PRD 레지스트리 로드"""
    if not REGISTRY_PATH.exists():
        return {"prds": {}}

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(registry: Dict[str, Any]) -> None:
    """PRD 레지스트리 저장"""
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def get_doc_content(doc_id: str) -> Optional[str]:
    """Google Docs에서 문서 내용 가져오기"""
    if not GOOGLE_DOCS_AVAILABLE:
        print("[ERROR] Google Docs 라이브러리를 사용할 수 없습니다")
        return None

    try:
        creds = get_credentials()
        service = build_docs_service(creds)

        # 문서 가져오기
        doc = service.documents().get(documentId=doc_id).execute()

        # 텍스트 추출
        content_parts = []
        for element in doc.get("body", {}).get("content", []):
            if "paragraph" in element:
                for text_run in element["paragraph"].get("elements", []):
                    if "textRun" in text_run:
                        content_parts.append(text_run["textRun"].get("content", ""))

        return "".join(content_parts)
    except Exception as e:
        print(f"[ERROR] 문서 가져오기 실패: {e}")
        return None


def extract_doc_id(url: str) -> Optional[str]:
    """Google Docs URL에서 문서 ID 추출"""
    import re
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None


def sync_prd(prd_id: str, registry: Dict[str, Any]) -> bool:
    """특정 PRD 동기화"""
    prds = registry.get("prds", {})

    if prd_id not in prds:
        print(f"[ERROR] {prd_id}가 레지스트리에 없습니다")
        return False

    prd_info = prds[prd_id]
    doc_url = prd_info.get("url", "")
    doc_id = extract_doc_id(doc_url)

    if not doc_id:
        print(f"[ERROR] {prd_id}의 문서 ID를 추출할 수 없습니다")
        return False

    print(f"[SYNC] {prd_id} 동기화 중...")

    content = get_doc_content(doc_id)
    if content is None:
        return False

    # 캐시 파일 생성
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{prd_id}.cache.md"

    now = datetime.utcnow().isoformat() + "Z"
    cache_content = f"""<!--
  {prd_id} Local Cache (Read-Only)
  Master: {doc_url}
  Last Synced: {now}
  DO NOT EDIT - Changes will be overwritten by /prd-sync
-->

{content}

---

> **Note**: This is a read-only cache.
"""

    cache_file.write_text(cache_content, encoding="utf-8")

    # 레지스트리 업데이트
    prds[prd_id]["updated_at"] = now
    save_registry(registry)

    print(f"[OK] Synced {prd_id} from Google Docs")
    print(f"     Cache: {cache_file.relative_to(PROJECT_ROOT)}")
    print(f"     Last Updated: {now}")

    return True


def sync_all(registry: Dict[str, Any]) -> int:
    """모든 PRD 동기화"""
    prds = registry.get("prds", {})

    if not prds:
        print("[INFO] 등록된 PRD가 없습니다")
        return 0

    success_count = 0
    for prd_id in prds:
        if sync_prd(prd_id, registry):
            success_count += 1
        print()

    print(f"[DONE] {success_count}/{len(prds)} PRD 동기화 완료")
    return success_count


def list_prds(registry: Dict[str, Any]) -> None:
    """등록된 PRD 목록 출력"""
    prds = registry.get("prds", {})

    if not prds:
        print("[INFO] 등록된 PRD가 없습니다")
        return

    print(f"PRD Registry ({len(prds)} documents)")
    print("=" * 60)

    for prd_id, info in sorted(prds.items()):
        status = info.get("status", "Unknown")
        status_icon = {"Draft": "D", "Approved": "A", "In Progress": "P", "Completed": "C"}.get(status, "?")
        title = info.get("title", "Untitled")
        url = info.get("url", "")
        priority = info.get("priority", "P2")
        updated = info.get("updated_at", "Unknown")[:10] if info.get("updated_at") else "Unknown"

        print(f"\n[{status_icon}] {prd_id}: {title}")
        print(f"    URL: {url}")
        print(f"    Priority: {priority} | Updated: {updated}")


def main():
    parser = argparse.ArgumentParser(
        description="PRD Manager - Google Docs PRD 동기화",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="명령")

    # sync 명령
    sync_parser = subparsers.add_parser("sync", help="PRD 동기화")
    sync_parser.add_argument("prd_id", nargs="?", help="PRD ID (예: PRD-0001)")
    sync_parser.add_argument("--all", action="store_true", help="모든 PRD 동기화")

    # list 명령
    subparsers.add_parser("list", help="PRD 목록 조회")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    registry = load_registry()

    if args.command == "list":
        list_prds(registry)
        return 0

    if args.command == "sync":
        if args.all:
            sync_all(registry)
            return 0
        elif args.prd_id:
            success = sync_prd(args.prd_id, registry)
            return 0 if success else 1
        else:
            print("[ERROR] PRD ID를 지정하거나 --all 옵션을 사용하세요")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
