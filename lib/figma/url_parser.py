#!/usr/bin/env python3
"""Figma URL parser — extract file_key and node_id from Figma URLs.

Usage:
    python url_parser.py "https://www.figma.com/design/ABC123/MyFile?node-id=1-2"
    python url_parser.py parse "https://figma.com/file/XYZ/Title?node-id=42-15"
"""

import json
import re
import sys
from urllib.parse import parse_qs, urlparse

sys.stdout.reconfigure(encoding="utf-8")

# Matches /design/<key>/<name> or /file/<key>/<name>
_FIGMA_PATH_RE = re.compile(r"^/(?:design|file)/([^/]+)(?:/([^/?]*))?")


def parse_figma_url(url: str) -> dict:
    """Extract file_key, node_id, and file_name from a Figma URL.

    Args:
        url: A Figma URL (https://figma.com/design/KEY/Name?node-id=X-Y)

    Returns:
        {"file_key": str, "node_id": str|None, "file_name": str|None}

    Raises:
        ValueError: If the URL is not a valid Figma design/file URL.
    """
    parsed = urlparse(url)
    if not parsed.hostname or "figma.com" not in parsed.hostname:
        raise ValueError(f"Not a Figma URL: {url}")

    match = _FIGMA_PATH_RE.match(parsed.path)
    if not match:
        raise ValueError(f"Invalid Figma URL path: {parsed.path}")

    file_key = match.group(1)
    file_name = match.group(2) or None

    # Extract node-id from query params, convert dash to colon (MCP format)
    qs = parse_qs(parsed.query)
    node_id_raw = qs.get("node-id", [None])[0]
    node_id = node_id_raw.replace("-", ":") if node_id_raw else None

    return {
        "file_key": file_key,
        "node_id": node_id,
        "file_name": file_name,
    }


def validate_figma_url(url: str) -> bool:
    """Check if a URL is a valid Figma design/file URL."""
    if not url:
        return False
    try:
        parse_figma_url(url)
        return True
    except ValueError:
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Support both `url_parser.py <url>` and `url_parser.py parse <url>`
    target = sys.argv[-1]
    try:
        result = parse_figma_url(target)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
