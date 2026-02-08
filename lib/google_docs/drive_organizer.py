"""
Google Drive Organizer

Drive 파일 정리, 중복 제거, 폴더 구조화를 위한 모듈
"""

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

from .auth import get_credentials, DEFAULT_FOLDER_ID
from .project_registry import get_project_folder_id


@dataclass
class FileInfo:
    """Drive 파일 정보"""
    id: str
    name: str
    mime_type: str
    size: int = 0
    modified_time: str = ""
    md5_checksum: str = ""
    parents: list = field(default_factory=list)

    @property
    def is_folder(self) -> bool:
        return self.mime_type == "application/vnd.google-apps.folder"

    @property
    def is_image(self) -> bool:
        return self.mime_type.startswith("image/")

    @property
    def is_google_doc(self) -> bool:
        return "google-apps" in self.mime_type


@dataclass
class DuplicateGroup:
    """중복 파일 그룹"""
    name: str
    files: list  # List[FileInfo]
    keep: Optional[FileInfo] = None  # 유지할 파일

    @property
    def count(self) -> int:
        return len(self.files)

    @property
    def to_delete(self) -> list:
        if not self.keep:
            return []
        return [f for f in self.files if f.id != self.keep.id]


class DriveOrganizer:
    """Google Drive 정리 도구"""

    # 기본 폴더 구조
    DEFAULT_STRUCTURE = {
        "documents": {
            "prds": {},
            "guides": {},
            "archives": {}
        },
        "images": {
            "prds": {},
            "wireframes": {},
            "diagrams": {},
            "screenshots": {}
        },
        "archives": {
            "2026-Q1": {},
            "deprecated": {}
        }
    }

    # 파일 분류 규칙 (정규식 패턴 → 대상 폴더)
    CLASSIFICATION_RULES = [
        (r"PRD-(\d{4})", "images/prds/PRD-{0}"),  # PRD-0001 → images/prds/PRD-0001
        (r"(wireframe|mockup)", "images/wireframes"),
        (r"(diagram|arch|flow)", "images/diagrams"),
        (r"(screenshot|capture)", "images/screenshots"),
        (r"beginner-", "images/prds/tutorials"),
        (r"^\d{2}-", "images/prds/general"),  # 01-xxx, 02-xxx 등
    ]

    def __init__(self, root_folder_id: Optional[str] = None):
        try:
            self.root_folder_id = root_folder_id or get_project_folder_id()
        except Exception:
            self.root_folder_id = root_folder_id or DEFAULT_FOLDER_ID
        self.creds = get_credentials()
        self.drive = build("drive", "v3", credentials=self.creds)
        self._folder_cache: dict[str, str] = {}  # path → folder_id

    def get_all_files(self, folder_id: Optional[str] = None, recursive: bool = False) -> list[FileInfo]:
        """폴더 내 모든 파일 조회"""
        folder_id = folder_id or self.root_folder_id
        all_files = []
        page_token = None

        while True:
            query = f"'{folder_id}' in parents and trashed=false"
            results = self.drive.files().list(
                q=query,
                pageSize=200,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, md5Checksum, parents)"
            ).execute()

            files = results.get("files", [])
            for f in files:
                file_info = FileInfo(
                    id=f["id"],
                    name=f["name"],
                    mime_type=f.get("mimeType", ""),
                    size=int(f.get("size", 0)),
                    modified_time=f.get("modifiedTime", ""),
                    md5_checksum=f.get("md5Checksum", ""),
                    parents=f.get("parents", [])
                )
                all_files.append(file_info)

                # 재귀적으로 하위 폴더 탐색
                if recursive and file_info.is_folder:
                    all_files.extend(self.get_all_files(file_info.id, recursive=True))

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        return all_files

    def find_duplicates(self, folder_id: Optional[str] = None) -> list[DuplicateGroup]:
        """중복 파일 탐지 (파일명 + 크기 기반)"""
        files = self.get_all_files(folder_id)

        # 이미지 파일만 필터링
        images = [f for f in files if f.is_image]

        # 파일명으로 그룹화
        by_name: dict[str, list[FileInfo]] = defaultdict(list)
        for f in images:
            by_name[f.name].append(f)

        # 중복 그룹 생성
        duplicates = []
        for name, group_files in by_name.items():
            if len(group_files) > 1:
                # 최신 파일을 유지 대상으로 선택
                sorted_files = sorted(group_files, key=lambda x: x.modified_time, reverse=True)
                dup_group = DuplicateGroup(
                    name=name,
                    files=sorted_files,
                    keep=sorted_files[0]
                )
                duplicates.append(dup_group)

        return sorted(duplicates, key=lambda x: -x.count)

    def delete_duplicates(self, dry_run: bool = True) -> dict:
        """중복 파일 삭제"""
        duplicates = self.find_duplicates()

        result = {
            "total_groups": len(duplicates),
            "files_to_delete": 0,
            "deleted": [],
            "errors": [],
            "dry_run": dry_run
        }

        for group in duplicates:
            for file_to_delete in group.to_delete:
                result["files_to_delete"] += 1

                if not dry_run:
                    try:
                        # Trash로 이동 (완전 삭제 대신)
                        self.drive.files().update(
                            fileId=file_to_delete.id,
                            body={"trashed": True}
                        ).execute()
                        result["deleted"].append({
                            "id": file_to_delete.id,
                            "name": file_to_delete.name
                        })
                    except Exception as e:
                        result["errors"].append({
                            "id": file_to_delete.id,
                            "name": file_to_delete.name,
                            "error": str(e)
                        })

        return result

    def create_folder(self, name: str, parent_id: str) -> str:
        """폴더 생성"""
        # 이미 존재하는지 확인
        query = f"name='{name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.drive.files().list(q=query, fields="files(id)").execute()

        if results.get("files"):
            return results["files"][0]["id"]

        # 새 폴더 생성
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id]
        }
        folder = self.drive.files().create(body=file_metadata, fields="id").execute()
        return folder["id"]

    def create_folder_structure(self, structure: Optional[dict] = None, parent_id: Optional[str] = None) -> dict:
        """폴더 구조 생성"""
        structure = structure or self.DEFAULT_STRUCTURE
        parent_id = parent_id or self.root_folder_id
        created = {}

        def _create_recursive(struct: dict, parent: str, path: str = ""):
            for name, children in struct.items():
                current_path = f"{path}/{name}" if path else name
                folder_id = self.create_folder(name, parent)
                created[current_path] = folder_id
                self._folder_cache[current_path] = folder_id

                if children:
                    _create_recursive(children, folder_id, current_path)

        _create_recursive(structure, parent_id)
        return created

    def classify_file(self, file: FileInfo) -> Optional[str]:
        """파일 분류 규칙 적용"""
        for pattern, target_folder in self.CLASSIFICATION_RULES:
            match = re.search(pattern, file.name, re.IGNORECASE)
            if match:
                # 그룹 치환 ({0}, {1} 등)
                folder = target_folder
                for i, group in enumerate(match.groups()):
                    if group:
                        folder = folder.replace(f"{{{i}}}", group)
                return folder
        return None

    def move_file(self, file_id: str, new_parent_id: str) -> bool:
        """파일 이동 (폴더 변경)"""
        try:
            file = self.drive.files().get(fileId=file_id, fields="parents").execute()
            previous_parents = ",".join(file.get("parents", []))

            self.drive.files().update(
                fileId=file_id,
                addParents=new_parent_id,
                removeParents=previous_parents,
                fields="id, parents"
            ).execute()
            return True
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                "파일 이동 실패: file_id=%s, target=%s, error=%s",
                file_id, new_parent_id, e
            )
            return False

    def organize_files(self, dry_run: bool = True) -> dict:
        """파일 자동 정리"""
        files = self.get_all_files()
        images = [f for f in files if f.is_image]

        result = {
            "total_files": len(images),
            "classified": 0,
            "unclassified": 0,
            "moved": [],
            "skipped": [],
            "errors": [],
            "dry_run": dry_run
        }

        for file in images:
            target_folder = self.classify_file(file)

            if not target_folder:
                result["unclassified"] += 1
                result["skipped"].append({
                    "id": file.id,
                    "name": file.name,
                    "reason": "No matching rule"
                })
                continue

            result["classified"] += 1

            if not dry_run:
                # 대상 폴더 ID 확보
                folder_id = self._folder_cache.get(target_folder)
                if not folder_id:
                    # 폴더 생성 필요
                    parts = target_folder.split("/")
                    current_parent = self.root_folder_id
                    current_path = ""
                    for part in parts:
                        current_path = f"{current_path}/{part}" if current_path else part
                        if current_path in self._folder_cache:
                            current_parent = self._folder_cache[current_path]
                        else:
                            current_parent = self.create_folder(part, current_parent)
                            self._folder_cache[current_path] = current_parent
                    folder_id = current_parent

                # 파일 이동
                if self.move_file(file.id, folder_id):
                    result["moved"].append({
                        "id": file.id,
                        "name": file.name,
                        "target": target_folder
                    })
                else:
                    result["errors"].append({
                        "id": file.id,
                        "name": file.name,
                        "error": "Move failed"
                    })
            else:
                result["moved"].append({
                    "id": file.id,
                    "name": file.name,
                    "target": target_folder
                })

        return result

    def get_status(self) -> dict:
        """현재 상태 분석"""
        files = self.get_all_files()

        # 타입별 분류
        folders = [f for f in files if f.is_folder]
        docs = [f for f in files if f.is_google_doc]
        images = [f for f in files if f.is_image]
        others = [f for f in files if not f.is_folder and not f.is_google_doc and not f.is_image]

        # 중복 분석
        duplicates = self.find_duplicates()
        total_duplicates = sum(d.count - 1 for d in duplicates)  # 원본 제외

        # 용량 계산
        total_size = sum(f.size for f in files)
        image_size = sum(f.size for f in images)

        return {
            "folder_id": self.root_folder_id,
            "summary": {
                "total_files": len(files),
                "folders": len(folders),
                "documents": len(docs),
                "images": len(images),
                "others": len(others)
            },
            "storage": {
                "total_bytes": total_size,
                "total_mb": round(total_size / 1024 / 1024, 2),
                "images_bytes": image_size,
                "images_mb": round(image_size / 1024 / 1024, 2)
            },
            "duplicates": {
                "groups": len(duplicates),
                "total_duplicate_files": total_duplicates,
                "top_duplicates": [
                    {"name": d.name, "count": d.count}
                    for d in duplicates[:10]
                ]
            },
            "issues": self._analyze_issues(files, folders, duplicates)
        }

    def _analyze_issues(self, files: list, folders: list, duplicates: list) -> list:
        """문제점 분석"""
        issues = []

        if len(duplicates) > 0:
            total_dup = sum(d.count - 1 for d in duplicates)
            issues.append({
                "type": "duplicates",
                "severity": "warning",
                "message": f"{len(duplicates)} duplicate file groups detected ({total_dup} excess files)"
            })

        if len(folders) == 0:
            issues.append({
                "type": "no_structure",
                "severity": "warning",
                "message": "No folder structure (all files in root)"
            })

        # 정리되지 않은 이미지
        unclassified = 0
        for f in files:
            if f.is_image and not self.classify_file(f):
                unclassified += 1

        if unclassified > 0:
            issues.append({
                "type": "unclassified",
                "severity": "info",
                "message": f"{unclassified} files cannot be auto-classified"
            })

        return issues


def print_status(status: dict):
    """상태 출력 (CLI용)"""
    print("\nGoogle Drive Status")
    print("=" * 60)
    print(f"Folder ID: {status['folder_id'][:20]}...")
    print()

    s = status["summary"]
    print("Files:")
    print(f"  - Folders:    {s['folders']}")
    print(f"  - Documents:  {s['documents']} (Google Docs/Sheets)")
    print(f"  - Images:     {s['images']} ({status['storage']['images_mb']} MB)")
    print(f"  - Others:     {s['others']}")
    print()

    d = status["duplicates"]
    if d["groups"] > 0:
        print(f"Duplicates: {d['groups']} groups, {d['total_duplicate_files']} excess files")
        print("  Top duplicates:")
        for dup in d["top_duplicates"][:5]:
            print(f"    - {dup['name']}: {dup['count']}x")
        print()

    if status["issues"]:
        print("Issues:")
        for issue in status["issues"]:
            icon = "⚠️" if issue["severity"] == "warning" else "ℹ️"
            print(f"  {icon}  {issue['message']}")
        print()

    print("Recommendations:")
    print("  1. Run 'drive duplicates --delete' to remove duplicates")
    print("  2. Run 'drive init' to create folder structure")
    print("  3. Run 'drive organize' to sort files")


def print_duplicates(duplicates: list[DuplicateGroup]):
    """중복 파일 출력 (CLI용)"""
    print("\nDuplicate Files Analysis")
    print("=" * 60)
    print(f"Total groups: {len(duplicates)}")
    print(f"Total excess files: {sum(d.count - 1 for d in duplicates)}")
    print()

    for group in duplicates[:20]:
        print(f"📁 {group.name} ({group.count}x)")
        print(f"   Keep: {group.keep.id[:15]}... (modified: {group.keep.modified_time[:10]})")
        for f in group.to_delete[:3]:
            print(f"   Delete: {f.id[:15]}...")
        if len(group.to_delete) > 3:
            print(f"   ... and {len(group.to_delete) - 3} more")
        print()
