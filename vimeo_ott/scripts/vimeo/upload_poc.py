"""
Vimeo Video Upload POC for WSOPTV.

Tests basic upload functionality with Vimeo Enterprise API.

Usage:
    python upload_poc.py test.mp4
    python upload_poc.py test.mp4 --title "Test Video" --description "Test upload"
    python upload_poc.py --list  # List recent videos
    python upload_poc.py --info /videos/123456  # Get video info
"""

import argparse
import sys
from pathlib import Path

# Add parent for auth import
sys.path.insert(0, str(Path(__file__).parent))

from auth import get_client, authenticate


def list_videos(client, limit: int = 10) -> list:
    """List recent videos from account."""
    print(f"\n📹 Fetching {limit} recent videos...")

    response = client.get("/me/videos", params={"per_page": limit, "sort": "date"})

    if response.status_code != 200:
        print(f"❌ Failed to list videos: {response.status_code}")
        print(response.text)
        return []

    data = response.json()
    videos = data.get("data", [])

    print(f"\n📋 Found {data.get('total', 0)} videos (showing {len(videos)}):\n")

    for i, video in enumerate(videos, 1):
        uri = video.get("uri", "")
        name = video.get("name", "Untitled")
        duration = video.get("duration", 0)
        status = video.get("status", "unknown")
        created = video.get("created_time", "")[:10]

        print(f"  {i}. {name}")
        print(f"     URI: {uri}")
        print(f"     Duration: {duration}s | Status: {status} | Created: {created}")
        print()

    return videos


def get_video_info(client, uri: str) -> dict:
    """Get detailed video information."""
    print(f"\n🔍 Fetching video info for {uri}...")

    # Normalize URI
    if not uri.startswith("/videos/"):
        uri = f"/videos/{uri}"

    response = client.get(uri)

    if response.status_code != 200:
        print(f"❌ Failed to get video: {response.status_code}")
        print(response.text)
        return {}

    video = response.json()

    print("\n📹 Video Details:")
    print(f"   Name: {video.get('name')}")
    print(f"   URI: {video.get('uri')}")
    print(f"   Link: {video.get('link')}")
    print(f"   Duration: {video.get('duration')}s")
    print(f"   Status: {video.get('status')}")
    print(f"   Privacy: {video.get('privacy', {}).get('view')}")
    print(f"   Created: {video.get('created_time')}")
    print(f"   Modified: {video.get('modified_time')}")

    # File info
    files = video.get("files", [])
    if files:
        print(f"\n   📁 Files ({len(files)}):")
        for f in files[:5]:  # Show first 5
            print(f"      - {f.get('quality')}: {f.get('width')}x{f.get('height')} ({f.get('type')})")

    # Download links (Enterprise feature)
    download = video.get("download", [])
    if download:
        print(f"\n   ⬇️ Download links available: {len(download)}")

    return video


def upload_video(
    client,
    file_path: str,
    title: str | None = None,
    description: str | None = None,
    privacy: str = "unlisted",
) -> str:
    """
    Upload video to Vimeo.

    Args:
        client: Authenticated Vimeo client
        file_path: Path to video file
        title: Video title (defaults to filename)
        description: Video description
        privacy: Privacy setting (anybody, unlisted, password, disable)

    Returns:
        Video URI on success
    """
    path = Path(file_path)

    if not path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    file_size = path.stat().st_size
    file_name = path.stem

    print("\n📤 Uploading video:")
    print(f"   File: {path.name}")
    print(f"   Size: {file_size / 1024 / 1024:.2f} MB")
    print(f"   Title: {title or file_name}")
    print(f"   Privacy: {privacy}")
    print()

    # Prepare metadata
    data = {
        "name": title or file_name,
        "privacy": {"view": privacy},
    }

    if description:
        data["description"] = description

    try:
        print("⏳ Starting upload (this may take a while)...")
        uri = client.upload(str(path), data=data)
        print("\n✅ Upload complete!")
        print(f"   Video URI: {uri}")

        # Get video link
        response = client.get(uri)
        if response.status_code == 200:
            video = response.json()
            print(f"   Video URL: {video.get('link')}")
            print(f"   Status: {video.get('status')}")

            # Transcode status
            transcode = video.get("transcode", {})
            if transcode:
                print(f"   Transcode: {transcode.get('status')}")

        return uri

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        sys.exit(1)


def check_quota(client) -> dict:
    """Check upload quota."""
    print("\n📊 Checking upload quota...")

    response = client.get("/me")

    if response.status_code != 200:
        print(f"❌ Failed to get quota: {response.status_code}")
        return {}

    user = response.json()
    quota = user.get("upload_quota", {})

    print("\n📊 Upload Quota:")
    print(f"   Space used: {quota.get('space', {}).get('used', 0) / 1024 / 1024 / 1024:.2f} GB")
    print(f"   Space free: {quota.get('space', {}).get('free', 0) / 1024 / 1024 / 1024:.2f} GB")
    print(f"   Space max: {quota.get('space', {}).get('max', 0) / 1024 / 1024 / 1024:.2f} GB")

    periodic = quota.get("periodic", {})
    if periodic:
        used = periodic.get("used") or 0
        free = periodic.get("free") or 0
        if used or free:
            print("\n   Periodic quota:")
            print(f"   Used: {used / 1024 / 1024 / 1024:.2f} GB")
            print(f"   Free: {free / 1024 / 1024 / 1024:.2f} GB")

    return quota


def main():
    parser = argparse.ArgumentParser(description="Vimeo Upload POC")
    parser.add_argument("file", nargs="?", help="Video file to upload")
    parser.add_argument("--title", "-t", help="Video title")
    parser.add_argument("--description", "-d", help="Video description")
    parser.add_argument("--privacy", "-p", default="unlisted",
                        choices=["anybody", "unlisted", "password", "disable"],
                        help="Privacy setting (default: unlisted)")
    parser.add_argument("--list", "-l", action="store_true", help="List recent videos")
    parser.add_argument("--info", "-i", help="Get video info by URI")
    parser.add_argument("--quota", "-q", action="store_true", help="Check upload quota")
    parser.add_argument("--auth", action="store_true", help="Force re-authentication")

    args = parser.parse_args()

    # Force auth if requested
    if args.auth:
        authenticate(force=True)
        return

    # Get client
    client = get_client()

    # Check quota
    if args.quota:
        check_quota(client)
        return

    # List videos
    if args.list:
        list_videos(client)
        return

    # Get video info
    if args.info:
        get_video_info(client, args.info)
        return

    # Upload video
    if args.file:
        upload_video(
            client,
            args.file,
            title=args.title,
            description=args.description,
            privacy=args.privacy,
        )
        return

    # No action specified
    parser.print_help()


if __name__ == "__main__":
    main()
