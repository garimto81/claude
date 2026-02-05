"""
Vimeo Collections API Wrapper.

Manages Folders (Enterprise) and Albums for organizing videos.

Usage:
    python collections.py list                         # List all folders/albums
    python collections.py create-folder "WSOP Classic" # Create folder (Enterprise)
    python collections.py create-album "1973"          # Create album
    python collections.py create-album "1973" --folder "WSOP Classic"
    python collections.py add /videos/123456 --album "1973"
"""

import argparse
import sys
from pathlib import Path

# Add parent for auth import
sys.path.insert(0, str(Path(__file__).parent))

from auth import get_client


class VimeoCollections:
    """Vimeo Collections (Folders/Albums) API wrapper."""

    def __init__(self, client=None):
        """
        Initialize with Vimeo client.

        Args:
            client: Authenticated Vimeo client (auto-created if None)
        """
        self.client = client or get_client()
        self._user_uri = None

    @property
    def user_uri(self) -> str:
        """Get current user URI."""
        if not self._user_uri:
            response = self.client.get("/me")
            if response.status_code == 200:
                self._user_uri = response.json().get("uri", "/me")
            else:
                self._user_uri = "/me"
        return self._user_uri

    # =========================================================================
    # Folders (Enterprise only)
    # =========================================================================

    def create_folder(self, name: str) -> dict | None:
        """
        Create a new folder.

        Note: Folders are Enterprise-only feature.
        Falls back to album creation if folders not supported.

        Args:
            name: Folder name

        Returns:
            Folder data dict or None on failure
        """
        print(f"Creating folder: {name}")

        response = self.client.post(
            f"{self.user_uri}/folders",
            data={"name": name},
        )

        if response.status_code == 201:
            folder = response.json()
            print(f"  Folder created: {folder.get('uri')}")
            return folder

        if response.status_code == 403:
            print("  Folders require Enterprise plan. Using albums instead.")
            return None

        print(f"  Failed to create folder: {response.status_code}")
        print(f"  {response.text}")
        return None

    def list_folders(self) -> list[dict]:
        """
        List all folders.

        Returns:
            List of folder dicts
        """
        response = self.client.get(f"{self.user_uri}/folders", params={"per_page": 100})

        if response.status_code == 200:
            return response.json().get("data", [])

        if response.status_code == 403:
            print("Folders require Enterprise plan.")
            return []

        print(f"Failed to list folders: {response.status_code}")
        return []

    def get_folder_by_name(self, name: str) -> dict | None:
        """
        Get folder by name.

        Args:
            name: Folder name to find

        Returns:
            Folder dict or None
        """
        folders = self.list_folders()
        for folder in folders:
            if folder.get("name", "").lower() == name.lower():
                return folder
        return None

    # =========================================================================
    # Albums (Standard and above)
    # =========================================================================

    def create_album(
        self,
        name: str,
        description: str = "",
        folder_uri: str | None = None,
    ) -> dict | None:
        """
        Create a new album (showcase).

        Args:
            name: Album name
            description: Album description
            folder_uri: Optional folder URI to nest album in

        Returns:
            Album data dict or None on failure
        """
        print(f"Creating album: {name}")

        data = {"name": name}
        if description:
            data["description"] = description

        # Try to create in folder first (Enterprise)
        if folder_uri:
            response = self.client.post(
                f"{folder_uri}/albums",
                data=data,
            )
            if response.status_code == 201:
                album = response.json()
                print(f"  Album created in folder: {album.get('uri')}")
                return album
            # Fall through to create at user level

        # Create at user level
        response = self.client.post(
            f"{self.user_uri}/albums",
            data=data,
        )

        if response.status_code == 201:
            album = response.json()
            print(f"  Album created: {album.get('uri')}")
            return album

        print(f"  Failed to create album: {response.status_code}")
        print(f"  {response.text}")
        return None

    def list_albums(self, folder_uri: str | None = None) -> list[dict]:
        """
        List albums.

        Args:
            folder_uri: Optional folder to list albums from

        Returns:
            List of album dicts
        """
        endpoint = f"{folder_uri}/albums" if folder_uri else f"{self.user_uri}/albums"
        response = self.client.get(endpoint, params={"per_page": 100})

        if response.status_code == 200:
            return response.json().get("data", [])

        print(f"Failed to list albums: {response.status_code}")
        return []

    def get_album_by_name(self, name: str) -> dict | None:
        """
        Get album by name.

        Args:
            name: Album name to find

        Returns:
            Album dict or None
        """
        albums = self.list_albums()
        for album in albums:
            if album.get("name", "").lower() == name.lower():
                return album
        return None

    def get_or_create_album(self, name: str, description: str = "") -> dict:
        """
        Get existing album or create new one.

        Args:
            name: Album name
            description: Description for new album

        Returns:
            Album dict
        """
        album = self.get_album_by_name(name)
        if album:
            print(f"Using existing album: {album.get('uri')}")
            return album

        return self.create_album(name, description)

    # =========================================================================
    # Video Management
    # =========================================================================

    def add_video_to_album(self, album_uri: str, video_uri: str) -> bool:
        """
        Add video to album.

        Args:
            album_uri: Album URI (e.g., /users/123/albums/456)
            video_uri: Video URI (e.g., /videos/789)

        Returns:
            True on success
        """
        # Normalize URIs
        if not album_uri.startswith("/"):
            album_uri = f"/users/{self.user_uri.split('/')[-1]}/albums/{album_uri}"
        if not video_uri.startswith("/"):
            video_uri = f"/videos/{video_uri}"

        print(f"Adding {video_uri} to album {album_uri}")

        response = self.client.put(f"{album_uri}{video_uri}")

        if response.status_code in (200, 204):
            print("  Video added to album")
            return True

        print(f"  Failed to add video: {response.status_code}")
        print(f"  {response.text}")
        return False

    def remove_video_from_album(self, album_uri: str, video_uri: str) -> bool:
        """
        Remove video from album.

        Args:
            album_uri: Album URI
            video_uri: Video URI

        Returns:
            True on success
        """
        if not video_uri.startswith("/"):
            video_uri = f"/videos/{video_uri}"

        response = self.client.delete(f"{album_uri}{video_uri}")

        if response.status_code in (200, 204):
            print("Video removed from album")
            return True

        print(f"Failed to remove video: {response.status_code}")
        return False


def print_collections_tree(collections: VimeoCollections) -> None:
    """Print collections as a tree structure."""
    print("\nVimeo Collections")
    print("=" * 50)

    # Try folders first (Enterprise)
    folders = collections.list_folders()
    if folders:
        print("\nFolders (Projects):")
        for folder in folders:
            print(f"  [{folder.get('name')}] ({folder.get('uri')})")
            # Note: Projects have items, not albums
            items = folder.get("metadata", {}).get("connections", {}).get("items", {})
            total = items.get("total", 0)
            print(f"    Items: {total}")

    # List user-level albums
    albums = collections.list_albums()
    if albums:
        print("\nAlbums:")
        for album in albums:
            video_count = album.get("metadata", {}).get("connections", {}).get("videos", {}).get("total", 0)
            print(f"  - {album.get('name')} ({video_count} videos) [{album.get('uri')}]")

    if not folders and not albums:
        print("\nNo collections found.")

    print("=" * 50)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Vimeo Collections Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # list
    subparsers.add_parser("list", help="List collections")

    # create-folder
    folder_parser = subparsers.add_parser("create-folder", help="Create folder")
    folder_parser.add_argument("name", help="Folder name")

    # create-album
    album_parser = subparsers.add_parser("create-album", help="Create album")
    album_parser.add_argument("name", help="Album name")
    album_parser.add_argument("--folder", "-f", help="Parent folder name")
    album_parser.add_argument("--description", "-d", default="", help="Description")

    # add (video to album)
    add_parser = subparsers.add_parser("add", help="Add video to album")
    add_parser.add_argument("video", help="Video URI (e.g., /videos/123456)")
    add_parser.add_argument("--album", "-a", required=True, help="Album name or URI")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    collections = VimeoCollections()

    if args.command == "list":
        print_collections_tree(collections)

    elif args.command == "create-folder":
        result = collections.create_folder(args.name)
        if not result:
            print("Consider using 'create-album' for Standard plans.")

    elif args.command == "create-album":
        folder_uri = None
        if args.folder:
            folder = collections.get_folder_by_name(args.folder)
            if folder:
                folder_uri = folder.get("uri")
            else:
                print(f"Folder '{args.folder}' not found. Creating album at user level.")

        collections.create_album(args.name, args.description, folder_uri)

    elif args.command == "add":
        # Get album by name or URI
        if args.album.startswith("/"):
            album_uri = args.album
        else:
            album = collections.get_album_by_name(args.album)
            if not album:
                print(f"Album '{args.album}' not found.")
                sys.exit(1)
            album_uri = album.get("uri")

        collections.add_video_to_album(album_uri, args.video)


if __name__ == "__main__":
    main()
