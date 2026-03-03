#!/usr/bin/env python3
"""md2confluence - Markdown to Confluence Storage Format converter.

Handles: image attachments, Mermaid->PNG rendering, table auto-width styling.

Usage:
    python md2confluence.py <markdown_file> <page_id> [--dry-run] [--base-url URL]

Environment:
    ATLASSIAN_EMAIL     - Confluence user email
    ATLASSIAN_API_TOKEN - Confluence API token
    CONFLUENCE_BASE_URL - Base URL (default: https://ggnetwork.atlassian.net/wiki)
"""

import os
import sys
import re
import json
import tempfile
import subprocess
import shutil
import argparse
from pathlib import Path

import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def get_config():
    return {
        "base_url": os.environ.get(
            "CONFLUENCE_BASE_URL",
            "https://ggnetwork.atlassian.net/wiki",
        ),
        "email": os.environ.get("ATLASSIAN_EMAIL", ""),
        "token": os.environ.get("ATLASSIAN_API_TOKEN", ""),
    }


def get_auth(cfg):
    return (cfg["email"], cfg["token"])


# ---------------------------------------------------------------------------
# Confluence REST API helpers
# ---------------------------------------------------------------------------

def api_get(cfg, path, params=None):
    url = f"{cfg['base_url']}/rest/api{path}"
    resp = requests.get(url, auth=get_auth(cfg), params=params)
    resp.raise_for_status()
    return resp.json()


def api_put_json(cfg, path, payload):
    url = f"{cfg['base_url']}/rest/api{path}"
    resp = requests.put(
        url, auth=get_auth(cfg), json=payload,
        headers={"Content-Type": "application/json"},
    )
    resp.raise_for_status()
    return resp.json()


def get_page_info(cfg, page_id):
    return api_get(cfg, f"/content/{page_id}", {"expand": "version,space"})


def upload_attachment(cfg, page_id, filepath, filename=None):
    if filename is None:
        filename = os.path.basename(filepath)

    url = f"{cfg['base_url']}/rest/api/content/{page_id}/child/attachment"
    headers = {"X-Atlassian-Token": "nocheck"}

    with open(filepath, "rb") as f:
        files = {"file": (filename, f, "application/octet-stream")}
        resp = requests.put(url, auth=get_auth(cfg), headers=headers, files=files)

    if resp.status_code in (200, 201):
        print(f"  [OK] {filename}")
        return resp.json()

    print(f"  [FAIL] {filename}: {resp.status_code} {resp.text[:200]}")
    return None


def update_page_content(cfg, page_id, title, html, version, space_key):
    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "version": {"number": version},
        "body": {"storage": {"value": html, "representation": "storage"}},
    }
    return api_put_json(cfg, f"/content/{page_id}", payload)


# ---------------------------------------------------------------------------
# Mermaid rendering
# ---------------------------------------------------------------------------

def render_mermaid_blocks(md_content, output_dir):
    """Replace ```mermaid blocks with rendered PNG references."""
    pattern = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)
    images = []

    def _replace(match):
        idx = len(images)
        code = match.group(1)
        mmd = os.path.join(output_dir, f"mermaid-{idx}.mmd")
        png = os.path.join(output_dir, f"mermaid-{idx}.png")

        with open(mmd, "w", encoding="utf-8") as f:
            f.write(code)

        is_win = sys.platform == "win32"
        result = subprocess.run(
            ["mmdc", "-i", mmd, "-o", png, "-b", "white", "-w", "1200", "-s", "2"],
            capture_output=True, text=True, timeout=60, shell=is_win,
        )

        if result.returncode == 0 and os.path.exists(png):
            images.append(png)
            print(f"  [OK] mermaid-{idx}.png rendered")
            return f"![mermaid-diagram-{idx}](mermaid-{idx}.png)"
        else:
            err = result.stderr[:300] if result.stderr else "unknown"
            print(f"  [WARN] mermaid-{idx} failed: {err}")
            images.append(None)
            return match.group(0)

    modified = pattern.sub(_replace, md_content)
    return modified, images


# ---------------------------------------------------------------------------
# Pandoc MD -> HTML
# ---------------------------------------------------------------------------

def md_to_html(md_content, resource_path):
    is_win = sys.platform == "win32"
    result = subprocess.run(
        [
            "pandoc",
            "-f", "markdown+pipe_tables+grid_tables",
            "-t", "html",
            f"--resource-path={resource_path}",
            "--wrap=none",
        ],
        input=md_content, capture_output=True,
        text=True, encoding="utf-8", timeout=60, shell=is_win,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc failed: {result.stderr}")
    return result.stdout


# ---------------------------------------------------------------------------
# HTML post-processing for Confluence Storage Format
# ---------------------------------------------------------------------------

def postprocess_html(html):
    """Transform pandoc HTML into Confluence storage format."""

    # 1) <img> -> <ac:image> with attachment reference
    def _img_to_ac(match):
        attrs = match.group(1)
        src_m = re.search(r'src="([^"]*)"', attrs)
        alt_m = re.search(r'alt="([^"]*)"', attrs)
        if not src_m:
            return match.group(0)
        filename = os.path.basename(src_m.group(1))
        alt = alt_m.group(1) if alt_m else filename
        return (
            f'<ac:image ac:alt="{alt}" ac:title="{alt}">'
            f'<ri:attachment ri:filename="{filename}" />'
            f"</ac:image>"
        )

    html = re.sub(r"<img\s+([^>]*)\/?>", _img_to_ac, html)

    # 2) Table styling - auto-width via data-layout
    html = html.replace("<table>", '<table data-layout="default">')

    # 3) Wrap bare <th>/<td> content in <p> tags (Confluence requires this)
    def _wrap_cell(match):
        tag = match.group(1)
        attrs = match.group(2) or ""
        content = match.group(3).strip()
        if not content:
            content = "<br/>"
        if not content.startswith(("<p>", "<p ", "<ac:", "<ul", "<ol", "<h")):
            content = f"<p>{content}</p>"
        return f"<{tag}{attrs}>{content}</{tag}>"

    html = re.sub(
        r"<(t[hd])(\s[^>]*)?>(.+?)</\1>",
        _wrap_cell, html, flags=re.DOTALL,
    )

    # 4) Clean up empty paragraphs
    html = re.sub(r"<p>\s*</p>", "", html)

    return html


# ---------------------------------------------------------------------------
# Collect image references
# ---------------------------------------------------------------------------

def collect_images(md_content, base_dir, tmp_dir):
    """Return list of (filename, absolute_path) for all images."""
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    images = []
    seen = set()

    for _alt, src in pattern.findall(md_content):
        filename = os.path.basename(src)
        if filename in seen:
            continue
        seen.add(filename)

        if src.startswith("mermaid-"):
            full = os.path.join(tmp_dir, src)
        else:
            full = os.path.join(base_dir, src)

        if os.path.exists(full):
            images.append((filename, full))
        else:
            print(f"  [MISSING] {src} (resolved: {full})")

    return images


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def convert(md_path, page_id, dry_run=False, base_url=None):
    cfg = get_config()
    if base_url:
        cfg["base_url"] = base_url

    md_path = Path(md_path).resolve()
    base_dir = str(md_path.parent)

    print(f"[1/6] Reading: {md_path}")
    md_content = md_path.read_text(encoding="utf-8")

    print(f"[2/6] Fetching page info ({page_id})...")
    if not dry_run:
        info = get_page_info(cfg, page_id)
        ver = info["version"]["number"]
        title = info["title"]
        space = info["space"]["key"]
        print(f"  Title: {title} | Version: {ver} | Space: {space}")
    else:
        ver, title, space = 0, "DRY-RUN", "DRY"

    tmp_dir = tempfile.mkdtemp(prefix="md2con_")

    try:
        mermaid_count = len(re.findall(r"```mermaid", md_content))
        print(f"[3/6] Rendering {mermaid_count} Mermaid diagrams...")
        modified_md, mermaid_pngs = render_mermaid_blocks(md_content, tmp_dir)

        print("[4/6] Converting MD -> Confluence HTML...")
        html = md_to_html(modified_md, base_dir)
        html = postprocess_html(html)

        images = collect_images(modified_md, base_dir, tmp_dir)
        print(f"[5/6] Uploading {len(images)} attachments...")

        if dry_run:
            for fname, _fpath in images:
                print(f"  [DRY] Would upload: {fname}")
            print("[6/6] [DRY] Would update page content")
            preview = os.path.join(tmp_dir, "preview.html")
            Path(preview).write_text(html, encoding="utf-8")
            print(f"  Preview saved: {preview}")
            # Don't clean tmp_dir on dry-run so user can inspect
            return {"status": "dry_run", "preview": preview, "tmp_dir": tmp_dir}

        for fname, fpath in images:
            upload_attachment(cfg, page_id, fpath, fname)

        new_ver = ver + 1
        print(f"[6/6] Updating page (v{ver} -> v{new_ver})...")
        result = update_page_content(cfg, page_id, title, html, new_ver, space)
        final_ver = result["version"]["number"]
        print(f"  SUCCESS: Page updated to v{final_ver}")
        return {"status": "success", "version": final_ver}

    finally:
        if not dry_run:
            shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Markdown to Confluence converter"
    )
    parser.add_argument("markdown_file", help="Path to .md file")
    parser.add_argument("page_id", help="Confluence page ID")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview conversion without uploading",
    )
    parser.add_argument(
        "--base-url",
        help="Confluence base URL (include /wiki for Cloud)",
    )
    args = parser.parse_args()

    try:
        result = convert(
            args.markdown_file, args.page_id,
            args.dry_run, args.base_url,
        )
        sys.exit(0 if result["status"] in ("success", "dry_run") else 1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
