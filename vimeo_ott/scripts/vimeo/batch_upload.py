"""
Vimeo Batch Upload CLI.

Uploads multiple video files with retry logic, history tracking, and collection management.

Usage:
    # Dry-run (show what would be uploaded)
    python batch_upload.py "Z:\\GGPNAs\\ARCHIVE\\WSOP\\WSOP Classic (1973 - 2002)" --dry-run

    # Upload with limit
    python batch_upload.py "Z:\\...\\WSOP Classic" --limit 10 --collection "WSOP Classic"

    # Check status
    python batch_upload.py --status

    # Resume failed uploads
    python batch_upload.py --resume
"""

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent))

from auth import get_client
from metadata_parser import parse_metadata, WSPOMetadata
from vimeo_collections import VimeoCollections

# Absolute path for history file
HISTORY_FILE = Path("C:/claude/vimeo_ott/logs/upload_history.json")

# Supported video extensions
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v"}

# Upload settings
UPLOAD_DELAY_SECONDS = 60  # Delay between uploads to avoid rate limits


@dataclass
class UploadJob:
    """Represents a single upload job."""

    file_path: str
    file_hash: str
    file_size: int
    status: Literal["pending", "uploading", "transcoding", "complete", "failed"]
    vimeo_uri: str | None = None
    vimeo_link: str | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)
    started_at: str | None = None
    completed_at: str | None = None
    retry_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UploadJob":
        """Create from dictionary."""
        return cls(**data)


class BatchUploader:
    """Batch video uploader with history tracking."""

    def __init__(
        self,
        history_file: Path = HISTORY_FILE,
        client=None,
    ):
        """
        Initialize batch uploader.

        Args:
            history_file: Path to upload history JSON file
            client: Vimeo client (auto-created if None)
        """
        self.history_file = history_file
        self.client = client or get_client()
        self.collections = VimeoCollections(self.client)
        self.jobs: dict[str, UploadJob] = {}
        self._load_history()

    def _load_history(self) -> None:
        """Load upload history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    data = json.load(f)
                    for file_hash, job_data in data.get("jobs", {}).items():
                        self.jobs[file_hash] = UploadJob.from_dict(job_data)
                print(f"Loaded {len(self.jobs)} jobs from history")
            except Exception as e:
                print(f"Warning: Could not load history: {e}")

    def _save_history(self) -> None:
        """Save upload history to file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "last_updated": datetime.now().isoformat(),
            "jobs": {h: j.to_dict() for h, j in self.jobs.items()},
        }
        with open(self.history_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _compute_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
        """Compute MD5 hash of first 10MB for dedup (fast)."""
        hasher = hashlib.md5()
        bytes_read = 0
        max_bytes = 10 * 1024 * 1024  # 10MB

        with open(file_path, "rb") as f:
            while bytes_read < max_bytes:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
                bytes_read += len(chunk)

        # Include file size in hash for better uniqueness
        hasher.update(str(file_path.stat().st_size).encode())
        return hasher.hexdigest()

    def scan_directory(
        self,
        directory: str,
        pattern: str = "*",
        limit: int | None = None,
    ) -> list[Path]:
        """
        Scan directory for video files.

        Args:
            directory: Directory to scan
            pattern: Glob pattern (default: all files)
            limit: Maximum files to return

        Returns:
            List of video file paths
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"Directory not found: {directory}")
            return []

        files = []
        patterns = pattern.split(",") if "," in pattern else [pattern]

        for pat in patterns:
            pat = pat.strip()
            for file_path in dir_path.rglob(pat):
                if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
                    files.append(file_path)

        # Sort by year (extracted from path)
        files.sort(key=lambda p: (str(p).lower(), p.name))

        if limit:
            files = files[:limit]

        return files

    def add_files(self, paths: list[Path]) -> int:
        """
        Add files to upload queue.

        Args:
            paths: List of file paths

        Returns:
            Number of new files added
        """
        added = 0
        for path in paths:
            file_hash = self._compute_file_hash(path)

            # Skip if already processed
            if file_hash in self.jobs:
                job = self.jobs[file_hash]
                if job.status in ("complete", "transcoding"):
                    print(f"  Skipping (already uploaded): {path.name}")
                    continue
                if job.status == "pending":
                    print(f"  Already queued: {path.name}")
                    continue

            # Parse metadata
            meta = parse_metadata(str(path))

            # Create job
            job = UploadJob(
                file_path=str(path),
                file_hash=file_hash,
                file_size=path.stat().st_size,
                status="pending",
                metadata=meta.to_dict(),
            )
            self.jobs[file_hash] = job
            added += 1
            print(f"  Added: {path.name} ({job.file_size / 1024 / 1024:.1f} MB)")

        self._save_history()
        return added

    def _upload_single(
        self,
        job: UploadJob,
        collection_name: str | None = None,
        privacy: str = "unlisted",
    ) -> bool:
        """
        Upload a single file.

        Args:
            job: Upload job
            collection_name: Optional album name to add video to
            privacy: Privacy setting

        Returns:
            True on success
        """
        path = Path(job.file_path)
        if not path.exists():
            job.status = "failed"
            job.error = "File not found"
            self._save_history()
            return False

        meta = WSPOMetadata(**job.metadata) if job.metadata else parse_metadata(str(path))

        print(f"\nUploading: {path.name}")
        print(f"  Size: {job.file_size / 1024 / 1024 / 1024:.2f} GB")
        print(f"  Title: {meta.title}")

        job.status = "uploading"
        job.started_at = datetime.now().isoformat()
        self._save_history()

        try:
            # Prepare upload data
            data = {
                "name": meta.title,
                "description": meta.description,
                "privacy": {"view": privacy},
            }

            # Upload using TUS protocol (handled by PyVimeo)
            uri = self.client.upload(str(path), data=data)

            job.vimeo_uri = uri
            job.status = "transcoding"
            self._save_history()

            print(f"  Upload complete: {uri}")

            # Get video link
            response = self.client.get(uri)
            if response.status_code == 200:
                video = response.json()
                job.vimeo_link = video.get("link")
                print(f"  Video URL: {job.vimeo_link}")

                # Check transcode status
                status = video.get("status")
                transcode = video.get("transcode", {}).get("status")
                print(f"  Status: {status} | Transcode: {transcode}")

                if status == "available":
                    job.status = "complete"

            # Add to collection if specified
            if collection_name and job.vimeo_uri:
                album = self.collections.get_or_create_album(
                    collection_name,
                    f"WSOP videos from the {collection_name} collection",
                )
                if album:
                    self.collections.add_video_to_album(album.get("uri"), job.vimeo_uri)

            job.completed_at = datetime.now().isoformat()
            self._save_history()
            return True

        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.retry_count += 1
            self._save_history()
            print(f"  Upload failed: {e}")
            return False

    def run(
        self,
        max_concurrent: int = 1,  # Sequential for safety
        max_retries: int = 3,
        collection: str | None = None,
        privacy: str = "unlisted",
        dry_run: bool = False,
    ) -> dict:
        """
        Run upload jobs.

        Args:
            max_concurrent: Max concurrent uploads (1 = sequential)
            max_retries: Max retries per file
            collection: Album name to add videos to
            privacy: Privacy setting
            dry_run: If True, only show what would be uploaded

        Returns:
            Summary dict with counts
        """
        pending = [j for j in self.jobs.values() if j.status == "pending"]

        if not pending:
            print("No pending uploads.")
            return {"pending": 0, "uploaded": 0, "failed": 0}

        print(f"\n{'=' * 60}")
        print(f"Batch Upload: {len(pending)} files")
        print(f"Collection: {collection or 'None'}")
        print(f"Privacy: {privacy}")
        print(f"{'=' * 60}")

        if dry_run:
            print("\n[DRY RUN] Would upload:")
            total_size = 0
            for job in pending:
                path = Path(job.file_path)
                meta = job.metadata
                size_gb = job.file_size / 1024 / 1024 / 1024
                total_size += job.file_size
                print(f"  - {meta.get('title', path.name)} ({size_gb:.2f} GB)")
            print(f"\nTotal: {len(pending)} files, {total_size / 1024 / 1024 / 1024:.2f} GB")
            return {"pending": len(pending), "uploaded": 0, "failed": 0}

        uploaded = 0
        failed = 0

        for i, job in enumerate(pending, 1):
            print(f"\n[{i}/{len(pending)}] Processing...")

            success = self._upload_single(job, collection, privacy)
            if success:
                uploaded += 1
            else:
                failed += 1

            # Delay between uploads
            if i < len(pending):
                print(f"Waiting {UPLOAD_DELAY_SECONDS}s before next upload...")
                time.sleep(UPLOAD_DELAY_SECONDS)

        print(f"\n{'=' * 60}")
        print(f"Upload Complete: {uploaded} succeeded, {failed} failed")
        print(f"{'=' * 60}")

        return {"pending": 0, "uploaded": uploaded, "failed": failed}

    def resume(self, max_retries: int = 3, collection: str | None = None) -> dict:
        """
        Resume failed uploads.

        Args:
            max_retries: Max total retries
            collection: Album name

        Returns:
            Summary dict
        """
        failed = [
            j for j in self.jobs.values()
            if j.status == "failed" and j.retry_count < max_retries
        ]

        if not failed:
            print("No failed uploads to resume.")
            return {"resumed": 0, "succeeded": 0}

        print(f"Resuming {len(failed)} failed uploads...")

        for job in failed:
            job.status = "pending"

        self._save_history()
        return self.run(collection=collection)

    def get_status(self) -> dict:
        """Get upload status summary."""
        status_counts = {
            "pending": 0,
            "uploading": 0,
            "transcoding": 0,
            "complete": 0,
            "failed": 0,
        }

        total_size = 0
        uploaded_size = 0

        for job in self.jobs.values():
            status_counts[job.status] = status_counts.get(job.status, 0) + 1
            total_size += job.file_size
            if job.status in ("complete", "transcoding"):
                uploaded_size += job.file_size

        return {
            "total_jobs": len(self.jobs),
            "status_counts": status_counts,
            "total_size_gb": total_size / 1024 / 1024 / 1024,
            "uploaded_size_gb": uploaded_size / 1024 / 1024 / 1024,
        }

    def print_status(self) -> None:
        """Print detailed status."""
        status = self.get_status()

        print(f"\n{'=' * 60}")
        print("Upload Status")
        print(f"{'=' * 60}")
        print(f"Total jobs: {status['total_jobs']}")
        print(f"Total size: {status['total_size_gb']:.2f} GB")
        print(f"Uploaded: {status['uploaded_size_gb']:.2f} GB")
        print()
        print("By status:")
        for s, count in status["status_counts"].items():
            if count > 0:
                print(f"  {s}: {count}")

        # Show failed jobs
        failed = [j for j in self.jobs.values() if j.status == "failed"]
        if failed:
            print(f"\nFailed uploads ({len(failed)}):")
            for job in failed:
                print(f"  - {Path(job.file_path).name}: {job.error}")

        print(f"{'=' * 60}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Vimeo Batch Upload")
    parser.add_argument("directory", nargs="?", help="Directory to scan for videos")
    parser.add_argument(
        "--pattern",
        "-p",
        default="*.mp4,*.mov,*.avi",
        help="File patterns (comma-separated)",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        help="Maximum files to upload",
    )
    parser.add_argument(
        "--collection",
        "-c",
        help="Album name to add videos to",
    )
    parser.add_argument(
        "--privacy",
        default="unlisted",
        choices=["anybody", "unlisted", "password", "disable"],
        help="Privacy setting (default: unlisted)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without uploading",
    )
    parser.add_argument(
        "--status",
        "-s",
        action="store_true",
        help="Show upload status",
    )
    parser.add_argument(
        "--resume",
        "-r",
        action="store_true",
        help="Resume failed uploads",
    )
    parser.add_argument(
        "--poc",
        action="store_true",
        help="Use POC sample files (10 files from WSOP Classic)",
    )

    args = parser.parse_args()

    # Status check (no auth needed if just reading history)
    if args.status:
        uploader = BatchUploader(client=None)
        uploader._load_history()
        uploader.print_status()
        return

    # Need client for other operations
    uploader = BatchUploader()

    # Resume
    if args.resume:
        uploader.resume(collection=args.collection)
        return

    # POC mode - use predefined sample files
    if args.poc:
        from poc_samples import get_sample_files
        files = get_sample_files()
        if not files:
            print("No POC sample files found.")
            return

        print(f"POC mode: {len(files)} sample files")
        uploader.add_files(files)

        if args.dry_run:
            uploader.run(dry_run=True, collection=args.collection or "WSOP Classic", privacy=args.privacy)
        else:
            uploader.run(collection=args.collection or "WSOP Classic", privacy=args.privacy)
        return

    # Scan and upload
    if args.directory:
        print(f"Scanning: {args.directory}")
        files = uploader.scan_directory(
            args.directory,
            pattern=args.pattern,
            limit=args.limit,
        )

        if not files:
            print("No video files found.")
            return

        print(f"Found {len(files)} video files")
        uploader.add_files(files)

        if args.dry_run:
            uploader.run(dry_run=True, collection=args.collection, privacy=args.privacy)
        else:
            uploader.run(collection=args.collection, privacy=args.privacy)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
