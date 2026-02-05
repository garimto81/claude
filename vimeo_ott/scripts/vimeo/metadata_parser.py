"""
WSOP Video Metadata Parser.

Extracts metadata (year, series, event) from file paths.

Usage:
    python metadata_parser.py "path/to/file.mp4"
    python metadata_parser.py --test  # Test with 10 sample files
"""

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WSPOMetadata:
    """WSOP video metadata extracted from file path."""

    title: str
    year: int
    series: str
    event_name: str
    description: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "year": self.year,
            "series": self.series,
            "event_name": self.event_name,
            "description": self.description,
            "tags": self.tags,
        }


def extract_year(text: str) -> int | None:
    """Extract 4-digit year from text (1970-2030 range)."""
    match = re.search(r"\b(19[7-9]\d|20[0-2]\d)\b", text)
    return int(match.group(1)) if match else None


def extract_event_name(text: str) -> str:
    """Extract event name from filename."""
    text_lower = text.lower()

    # Main Event detection
    if any(x in text_lower for x in ["me", "main", "main event", "main-event"]):
        return "Main Event"

    # Bracelet events
    if "bracelet" in text_lower or "br" in text_lower.split("-"):
        return "Bracelet Event"

    # Player of the Year
    if "poy" in text_lower:
        return "Player of the Year"

    # Coverage
    if "coverage" in text_lower:
        return "Coverage"

    return "Main Event"  # Default assumption for classic era


def extract_series(file_path: str) -> str:
    """Extract series name from file path."""
    path_lower = file_path.lower()

    # Classic era detection
    if "classic" in path_lower or any(
        str(y) in path_lower for y in range(1973, 2003)
    ):
        return "WSOP Classic"

    # Europe
    if "wsope" in path_lower or "europe" in path_lower:
        return "WSOP Europe"

    # APAC
    if "apac" in path_lower or "asia" in path_lower:
        return "WSOP APAC"

    # Online
    if "online" in path_lower:
        return "WSOP Online"

    return "WSOP"


def parse_metadata(file_path: str) -> WSPOMetadata:
    """
    Parse WSOP metadata from file path.

    Args:
        file_path: Full path to video file

    Returns:
        WSPOMetadata with extracted information
    """
    path = Path(file_path)
    filename = path.stem
    full_path = str(path)

    # Extract year from filename first, then from path
    year = extract_year(filename) or extract_year(full_path)
    if not year:
        year = 2000  # Default fallback

    # Extract series and event
    series = extract_series(full_path)
    event_name = extract_event_name(filename)

    # Generate title
    title = f"WSOP {year} {event_name}"

    # Generate description
    description = f"World Series of Poker {year} {event_name}. Part of the {series} collection."

    # Generate tags
    tags = [
        "wsop",
        str(year),
        "poker",
        "world series of poker",
    ]

    if "classic" in series.lower():
        tags.append("classic")
        tags.append("vintage")

    if event_name == "Main Event":
        tags.append("main event")

    return WSPOMetadata(
        title=title,
        year=year,
        series=series,
        event_name=event_name,
        description=description,
        tags=tags,
    )


def test_samples() -> None:
    """Test metadata parsing with POC sample files."""
    # Sample files from the plan
    samples = [
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\1973\WSOP - 1973.avi",
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\1978\wsop-1978-me-nobug.mp4",
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\1983\wsop-1983-me-nobug.mp4",
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\1988\1988 World Series of Poker.mov",
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\1989\wsop-1989-me_nobug.mp4",
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\1992\wsop-1992-me-nobug.mp4",
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\1994\wsop-1994-me-nobug.mp4",
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\1995\wsop-1995-me-nobug.mp4",
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\1998\1998 World Series of Poker.mov",
        r"Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\2000\wsop-2000-me-nobug.mp4",
    ]

    print("=" * 60)
    print("WSOP Metadata Parser Test Results")
    print("=" * 60)

    for i, sample in enumerate(samples, 1):
        path = Path(sample)
        exists = path.exists()
        meta = parse_metadata(sample)

        print(f"\n{i}. {path.name}")
        print(f"   Exists: {'Yes' if exists else 'No'}")
        print(f"   Title: {meta.title}")
        print(f"   Year: {meta.year}")
        print(f"   Series: {meta.series}")
        print(f"   Event: {meta.event_name}")
        print(f"   Tags: {', '.join(meta.tags)}")

    print("\n" + "=" * 60)
    print(f"Tested {len(samples)} files")
    print("=" * 60)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="WSOP Video Metadata Parser")
    parser.add_argument("file", nargs="?", help="Video file path to parse")
    parser.add_argument(
        "--test", "-t", action="store_true", help="Test with 10 sample files"
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()

    if args.test:
        test_samples()
        return

    if args.file:
        meta = parse_metadata(args.file)
        if args.json:
            import json
            print(json.dumps(meta.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(f"Title: {meta.title}")
            print(f"Year: {meta.year}")
            print(f"Series: {meta.series}")
            print(f"Event: {meta.event_name}")
            print(f"Description: {meta.description}")
            print(f"Tags: {', '.join(meta.tags)}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
