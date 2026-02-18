"""
WSOP Archive Full Upload Script.

Uploads all 578 videos to Vimeo Enterprise with real-time progress tracking.
Shows detailed status after each upload.

Usage:
    python upload_all.py              # Start/resume full upload
    python upload_all.py --status     # Check current status only
    python upload_all.py --skip 10    # Skip first 10 pending files
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add paths for imports (resolve() ensures absolute paths on Windows)
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR / "vimeo"))
sys.path.insert(0, str(_SCRIPT_DIR.parent))

from auth import get_client
from vhx.collection_manager import CollectionManager
from config.season_ids import SEASON_IDS

# Retry configuration
MAX_UPLOAD_RETRIES = 3
RETRY_DELAY_SECONDS = 30

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# File paths
METADATA_FILE = DATA_DIR / "upload_metadata.json"
UPLOAD_STATE_FILE = LOGS_DIR / "upload_state.json"
UPLOAD_LOG_FILE = LOGS_DIR / "upload_log.jsonl"

# Ensure dirs exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if sys.platform == 'win32' else 'clear')


def load_metadata() -> dict:
    """Load upload metadata file."""
    if not METADATA_FILE.exists():
        print(f"Metadata file not found: {METADATA_FILE}")
        sys.exit(1)
    with open(METADATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_state() -> dict:
    """Load upload state."""
    if not UPLOAD_STATE_FILE.exists():
        return {
            "started_at": None,
            "last_updated": None,
            "completed": {},
            "failed": {},
            "vhx_linked": {},
            "upload_times": [],  # Track upload durations for ETA
        }
    with open(UPLOAD_STATE_FILE, encoding="utf-8") as f:
        state = json.load(f)
        if "upload_times" not in state:
            state["upload_times"] = []
        return state


def save_state(state: dict):
    """Save upload state."""
    state["last_updated"] = datetime.now().isoformat()
    with open(UPLOAD_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def log_upload(entry: dict):
    """Append entry to upload log."""
    entry["timestamp"] = datetime.now().isoformat()
    with open(UPLOAD_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def format_duration(seconds: float) -> str:
    """Format seconds to human readable string."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        mins = seconds / 60
        return f"{mins:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_size(gb: float) -> str:
    """Format GB to readable string."""
    if gb < 1:
        return f"{gb * 1024:.0f} MB"
    return f"{gb:.2f} GB"


def print_status_header(total: int, completed: int, failed: int, linked: int,
                        total_size_gb: float, uploaded_size_gb: float):
    """Print status header."""
    pending = total - completed - failed
    pct = (completed / total * 100) if total > 0 else 0

    print("\n" + "=" * 70)
    print("  WSOP Archive Upload - Real-time Status")
    print("=" * 70)
    print(f"""
  Total Files:     {total}
  Completed:       {completed} ({pct:.1f}%)
  Failed:          {failed}
  Pending:         {pending}
  VHX Linked:      {linked}

  Total Size:      {format_size(total_size_gb)}
  Uploaded:        {format_size(uploaded_size_gb)}
  Remaining:       {format_size(total_size_gb - uploaded_size_gb)}
""")

    # Progress bar
    bar_len = 50
    filled = int(bar_len * completed / total) if total > 0 else 0
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"  Progress: [{bar}] {pct:.1f}%")
    print("=" * 70)


def print_upload_complete(idx: int, total: int, file_info: dict, vimeo_id: str,
                          duration: float, state: dict, total_size_gb: float):
    """Print completion message for each upload."""
    completed = len(state["completed"])
    failed = len(state["failed"])
    linked = len(state["vhx_linked"])
    pending = total - completed - failed

    # Calculate uploaded size
    metadata = load_metadata()
    uploaded_size = sum(
        f["size_gb"] for f in metadata["files"]
        if f["source_path"] in state["completed"]
    )

    # Calculate ETA
    if state["upload_times"]:
        avg_time = sum(state["upload_times"][-20:]) / len(state["upload_times"][-20:])
        eta_seconds = avg_time * pending
        eta_str = format_duration(eta_seconds)
    else:
        eta_str = "calculating..."

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║  ✅ UPLOAD COMPLETE #{completed}
╠══════════════════════════════════════════════════════════════════════╣
║  File:     {file_info['filename'][:55]}
║  Title:    {file_info['vimeo_metadata']['title'][:55]}
║  Size:     {format_size(file_info['size_gb'])}
║  Duration: {format_duration(duration)}
║  Vimeo ID: {vimeo_id}
║  Season:   {file_info['vhx_metadata']['collection_path']}
╠══════════════════════════════════════════════════════════════════════╣
║  Progress: {completed}/{total} ({completed/total*100:.1f}%) | Failed: {failed} | Pending: {pending}
║  Uploaded: {format_size(uploaded_size)} / {format_size(total_size_gb)}
║  ETA:      {eta_str}
╚══════════════════════════════════════════════════════════════════════╝
""")


def print_upload_failed(idx: int, total: int, file_info: dict, error: str, state: dict):
    """Print failure message."""
    completed = len(state["completed"])
    failed = len(state["failed"])

    print(f"""
╔══════════════════════════════════════════════════════════════════════╗
║  ❌ UPLOAD FAILED
╠══════════════════════════════════════════════════════════════════════╣
║  File:     {file_info['filename'][:55]}
║  Error:    {error[:55]}
╠══════════════════════════════════════════════════════════════════════╣
║  Progress: {completed}/{total} | Failed: {failed}
╚══════════════════════════════════════════════════════════════════════╝
""")


def print_upload_start(idx: int, total: int, file_info: dict):
    """Print upload start message."""
    print(f"""
┌──────────────────────────────────────────────────────────────────────┐
│  📤 Uploading [{idx}/{total}]
├──────────────────────────────────────────────────────────────────────┤
│  File:   {file_info['filename'][:58]}
│  Title:  {file_info['vimeo_metadata']['title'][:58]}
│  Size:   {format_size(file_info['size_gb'])}
│  Season: {file_info['vhx_metadata']['collection_path']}
└──────────────────────────────────────────────────────────────────────┘
""")


def upload_with_retry(client, file_path: str, data: dict, max_retries: int = MAX_UPLOAD_RETRIES) -> str:
    """
    Upload to Vimeo with retry on transient failures.

    Args:
        client: Vimeo client instance
        file_path: Path to video file
        data: Video metadata dict
        max_retries: Maximum number of retry attempts

    Returns:
        Video URI string

    Raises:
        Exception: If all retry attempts fail
    """
    import requests.exceptions

    for attempt in range(1, max_retries + 1):
        try:
            uri = client.upload(file_path, data=data)
            return uri
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout) as e:
            if attempt == max_retries:
                raise
            wait = RETRY_DELAY_SECONDS * attempt
            print(f"  ⚠️  Upload attempt {attempt}/{max_retries} failed: {str(e)[:60]}")
            print(f"  ⏳  Retrying in {wait}s...")
            time.sleep(wait)

    raise RuntimeError("Upload failed after all retries")


def upload_single(client, vhx_manager, file_info: dict, state: dict) -> tuple[bool, str | None, float]:
    """
    Upload a single file.

    Returns:
        (success, vimeo_id or error, duration_seconds)
    """
    source_path = file_info["source_path"]
    vimeo_meta = file_info["vimeo_metadata"]

    # Skip if already completed
    if source_path in state["completed"]:
        return True, state["completed"][source_path], 0

    # Check file exists
    if not Path(source_path).exists():
        error = "File not found"
        state["failed"][source_path] = error
        save_state(state)
        log_upload({"status": "error", "path": source_path, "error": error})
        return False, error, 0

    start_time = time.time()

    try:
        data = {
            "name": vimeo_meta["title"],
            "description": vimeo_meta["description"],
            "privacy": {"view": vimeo_meta.get("privacy", "unlisted")},
        }

        video_uri = upload_with_retry(client, source_path, data=data)
        duration = time.time() - start_time

        if video_uri:
            vimeo_id = video_uri.split("/")[-1]
            state["completed"][source_path] = vimeo_id
            state["upload_times"].append(duration)
            save_state(state)
            log_upload({
                "status": "success",
                "path": source_path,
                "vimeo_id": vimeo_id,
                "title": vimeo_meta["title"],
                "duration": duration
            })

            # Link to VHX
            collection_path = file_info["vhx_metadata"]["collection_path"]
            season_id = SEASON_IDS.get(collection_path)
            if season_id:
                try:
                    vhx_manager.add_item_to_collection(season_id, vimeo_id)
                    state["vhx_linked"][vimeo_id] = season_id
                    save_state(state)
                except Exception as e:
                    print(f"  [WARN] VHX link failed: {e}")

            return True, vimeo_id, duration
        else:
            error = "No URI returned"
            state["failed"][source_path] = error
            save_state(state)
            log_upload({"status": "error", "path": source_path, "error": error})
            return False, error, time.time() - start_time

    except Exception as e:
        duration = time.time() - start_time
        error = str(e)[:100]
        state["failed"][source_path] = error
        save_state(state)
        log_upload({"status": "error", "path": source_path, "error": error})
        return False, error, duration


def run_full_upload(skip: int = 0):
    """Run full upload with real-time status."""
    metadata = load_metadata()
    files = metadata["files"]
    total = len(files)
    total_size_gb = sum(f["size_gb"] for f in files)

    state = load_state()
    if not state["started_at"]:
        state["started_at"] = datetime.now().isoformat()
        save_state(state)

    # Filter pending files
    to_upload = [f for f in files if f["source_path"] not in state["completed"]]

    if skip > 0:
        to_upload = to_upload[skip:]
        print(f"\nSkipping first {skip} pending files...")

    if not to_upload:
        print("\n✅ All files have been uploaded!")
        show_status_only()
        return

    # Calculate uploaded size
    uploaded_size = sum(
        f["size_gb"] for f in files
        if f["source_path"] in state["completed"]
    )

    # Show initial status
    print_status_header(
        total, len(state["completed"]), len(state["failed"]),
        len(state["vhx_linked"]), total_size_gb, uploaded_size
    )

    print(f"\n📦 {len(to_upload)} files remaining to upload...")
    print("🔑 Initializing clients...")

    # Initialize clients
    vimeo_client = get_client()
    vhx_manager = CollectionManager()

    print("✅ Clients ready. Starting uploads...\n")
    time.sleep(1)

    # Upload loop
    for i, file_info in enumerate(to_upload, 1):
        idx = len(state["completed"]) + 1

        print_upload_start(idx, total, file_info)

        success, result, duration = upload_single(vimeo_client, vhx_manager, file_info, state)

        if success and result:
            print_upload_complete(idx, total, file_info, result, duration, state, total_size_gb)
        else:
            print_upload_failed(idx, total, file_info, result or "Unknown error", state)

        # Brief pause between uploads
        if i < len(to_upload):
            time.sleep(2)

    # Final summary
    print("\n" + "=" * 70)
    print("  UPLOAD SESSION COMPLETE")
    print("=" * 70)
    print(f"""
  Total Uploaded: {len(state['completed'])}
  Total Failed:   {len(state['failed'])}
  VHX Linked:     {len(state['vhx_linked'])}
""")

    if state["failed"]:
        print("  Failed files:")
        for path, error in list(state["failed"].items())[:5]:
            print(f"    - {Path(path).name}: {error[:40]}...")

    print("=" * 70)


def show_status_only():
    """Show status without uploading."""
    metadata = load_metadata()
    files = metadata["files"]
    total = len(files)
    total_size_gb = sum(f["size_gb"] for f in files)

    state = load_state()

    uploaded_size = sum(
        f["size_gb"] for f in files
        if f["source_path"] in state["completed"]
    )

    print_status_header(
        total, len(state["completed"]), len(state["failed"]),
        len(state["vhx_linked"]), total_size_gb, uploaded_size
    )

    if state["started_at"]:
        print(f"\n  Started:      {state['started_at']}")
    if state["last_updated"]:
        print(f"  Last Update:  {state['last_updated']}")

    # Show recent uploads
    if state["completed"]:
        print("\n  Recent Uploads:")
        recent = list(state["completed"].items())[-5:]
        for path, vid in recent:
            filename = Path(path).name[:40]
            print(f"    ✅ {filename}... -> {vid}")

    if state["failed"]:
        print(f"\n  Failed ({len(state['failed'])}):")
        for path, error in list(state["failed"].items())[:3]:
            filename = Path(path).name[:30]
            print(f"    ❌ {filename}...: {error[:30]}...")

    print("\n" + "=" * 70)
    print("\n  To continue uploading: python upload_all.py")
    print("  To retry failed:       python scripts/vimeo/batch_upload.py --retry-failed")
    print("")


def main():
    parser = argparse.ArgumentParser(description="WSOP Archive Full Upload")
    parser.add_argument("--status", "-s", action="store_true", help="Show status only")
    parser.add_argument("--skip", type=int, default=0, help="Skip first N pending files")

    args = parser.parse_args()

    if args.status:
        show_status_only()
    else:
        run_full_upload(skip=args.skip)


if __name__ == "__main__":
    main()
