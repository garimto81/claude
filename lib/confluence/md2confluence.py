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
import tempfile
import subprocess
import shutil
import argparse
from html import unescape as html_unescape
from pathlib import Path
from urllib.parse import unquote as url_unquote

import requests

# Ensure UTF-8 output on Windows (prevents cp949 UnicodeEncodeError)
if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _get_win_env(name):
    """Get Windows User environment variable (fallback when shell env is empty)."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            return winreg.QueryValueEx(key, name)[0]
    except Exception:
        return ""


def get_config():
    return {
        "base_url": (os.environ.get("CONFLUENCE_BASE_URL", "")
                     or _get_win_env("CONFLUENCE_BASE_URL")
                     or "https://ggnetwork.atlassian.net/wiki"),
        "email": os.environ.get("ATLASSIAN_EMAIL", "") or _get_win_env("ATLASSIAN_EMAIL"),
        "token": os.environ.get("ATLASSIAN_API_TOKEN", "") or _get_win_env("ATLASSIAN_API_TOKEN"),
    }


def get_auth(cfg):
    return (cfg["email"], cfg["token"])


# ---------------------------------------------------------------------------
# Confluence REST API helpers
# ---------------------------------------------------------------------------

def api_get(cfg, path, params=None):
    url = f"{cfg['base_url']}/rest/api{path}"
    resp = requests.get(url, auth=get_auth(cfg), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_put_json(cfg, path, payload):
    url = f"{cfg['base_url']}/rest/api{path}"
    resp = requests.put(
        url, auth=get_auth(cfg), json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if not resp.ok:
        print(f"  API Error {resp.status_code}: {resp.text[:500]}", file=sys.stderr)
    resp.raise_for_status()
    return resp.json()


def get_page_info(cfg, page_id):
    try:
        return api_get(cfg, f"/content/{page_id}", {"expand": "version,space"})
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            # Try draft status
            return api_get(cfg, f"/content/{page_id}", {"expand": "version,space", "status": "draft"})
        raise


def upload_attachment(cfg, page_id, filepath, filename=None):
    if filename is None:
        filename = os.path.basename(filepath)

    url = f"{cfg['base_url']}/rest/api/content/{page_id}/child/attachment"
    headers = {"X-Atlassian-Token": "nocheck"}

    with open(filepath, "rb") as f:
        files = {"file": (filename, f, "application/octet-stream")}
        resp = requests.put(url, auth=get_auth(cfg), headers=headers, files=files, timeout=60)

    if resp.status_code in (200, 201):
        print(f"  [OK] {filename}")
        return resp.json()

    print(f"  [FAIL] {filename}: {resp.status_code} {resp.text[:200]}")
    return None


def update_page_content(cfg, page_id, title, html, version, space_key, publish_draft=False):
    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "version": {"number": version},
        "body": {"storage": {"value": html, "representation": "storage"}},
    }
    if publish_draft:
        payload["status"] = "current"
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
        cmd = (["cmd", "/c", "mmdc", "-i", mmd, "-o", png, "-b", "white", "-w", "1200", "-s", "2"]
               if is_win else ["mmdc", "-i", mmd, "-o", png, "-b", "white", "-w", "1200", "-s", "2"])
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=60,
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
    base_cmd = [
        "pandoc",
        "-f", "markdown+pipe_tables+grid_tables",
        "-t", "html",
        f"--resource-path={resource_path}",
        "--wrap=none",
        "--no-highlight",
    ]
    cmd = ["cmd", "/c"] + base_cmd if is_win else base_cmd
    result = subprocess.run(
        cmd,
        input=md_content, capture_output=True,
        text=True, encoding="utf-8", timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc failed: {result.stderr}")
    return result.stdout


# ---------------------------------------------------------------------------
# HTML post-processing for Confluence Storage Format
# ---------------------------------------------------------------------------

MAX_IMAGE_WIDTH = 720


def postprocess_html(html, image_widths=None):
    """Transform pandoc HTML into Confluence storage format."""
    if image_widths is None:
        image_widths = {}

    # 0a) <pre><code> -> Confluence code macro
    def _code_block_to_macro(match):
        lang_match = re.search(r'class="(?:sourceCode\s+)?(\w+)"', match.group(0))
        lang = lang_match.group(1) if lang_match else "none"
        code_match = re.search(r'<code[^>]*>(.*?)</code>', match.group(0), re.DOTALL)
        code = re.sub(r'<[^>]+>', '', code_match.group(1))  # strip inner tags
        code = html_unescape(code)
        code = code.replace(']]>', ']]]]><![CDATA[>')  # CDATA escape
        lang_param = (
            f'<ac:parameter ac:name="language">{lang}</ac:parameter>'
            if lang != "none" else ''
        )
        return (
            f'<ac:structured-macro ac:name="code">{lang_param}'
            f'<ac:plain-text-body><![CDATA[{code}]]>'
            f'</ac:plain-text-body></ac:structured-macro>'
        )

    html = re.sub(r'<pre[^>]*>\s*<code[^>]*>.*?</code>\s*</pre>', _code_block_to_macro, html, flags=re.DOTALL)

    # 0b) Strip foreign class/id/style attributes (preserve ac:/ri: elements)
    def _strip_foreign_attrs(match):
        tag = match.group(0)
        if '<ac:' in tag or '<ri:' in tag:
            return tag
        tag = re.sub(r'\s+class="[^"]*"', '', tag)
        tag = re.sub(r'\s+id="[^"]*"', '', tag)
        tag = re.sub(r'\s+style="[^"]*"', '', tag)
        return tag

    html = re.sub(r'<[a-zA-Z][^>]*>', _strip_foreign_attrs, html)

    # 1) <img> -> <ac:image> with attachment reference (width-limited)
    def _img_to_ac(match):
        attrs = match.group(1)
        src_m = re.search(r'src="([^"]*)"', attrs)
        alt_m = re.search(r'alt="([^"]*)"', attrs)
        if not src_m:
            return match.group(0)
        filename = url_unquote(os.path.basename(src_m.group(1)))
        alt = alt_m.group(1) if alt_m else filename
        width_attr = ""
        if filename in image_widths and image_widths[filename] > MAX_IMAGE_WIDTH:
            width_attr = f' ac:width="{MAX_IMAGE_WIDTH}"'
        return (
            f'<ac:image ac:alt="{alt}" ac:title="{alt}"{width_attr}>'
            f'<ri:attachment ri:filename="{filename}" />'
            f"</ac:image>"
        )

    html = re.sub(r"<img\s+([^>]*)\/?>", _img_to_ac, html)

    # 1.5) Image captions → split into image + styled caption <p>
    # Case A: image and caption text in same <p> (no blank line in MD)
    html = re.sub(
        r'(<ac:image\b[^>]*>.*?</ac:image>)\s+([^<]+)</p>',
        r'\1</p>\n<p style="text-align: center; color: #626F86; font-size: 12px;"><em>\2</em></p>',
        html, flags=re.DOTALL,
    )
    # Case B: image and caption in separate <p> (blank line in MD)
    html = re.sub(
        r'(</ac:image>\s*</p>)\s*\n?\s*<p>([^<\n]+)</p>',
        r'\1\n<p style="text-align: center; color: #626F86; font-size: 12px;"><em>\2</em></p>',
        html,
    )

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

def _resolve_image(src, base_dir, tmp_dir, images, seen):
    """Resolve image path and add to collection if it exists on disk."""
    filename = os.path.basename(src)
    if filename in seen:
        return
    seen.add(filename)

    if src.startswith("mermaid-"):
        full = os.path.join(tmp_dir, src)
    else:
        full = os.path.join(base_dir, src)

    if os.path.exists(full):
        images.append((filename, full))
    else:
        # Try URL-decoded path (handles %EC%8A%A4... Korean filenames)
        decoded_src = url_unquote(src)
        decoded_full = os.path.join(base_dir, decoded_src)
        decoded_filename = os.path.basename(decoded_src)
        if os.path.exists(decoded_full):
            images.append((decoded_filename, decoded_full))
        else:
            print(f"  [MISSING] {src} (resolved: {full})")


def _build_width_map(images):
    """Build {filename: pixel_width} map using PIL for width-limiting."""
    widths = {}
    try:
        from PIL import Image
    except ImportError:
        return widths
    for fname, fpath in images:
        try:
            with Image.open(fpath) as img:
                widths[fname] = img.width
        except Exception:
            pass
    return widths


def collect_images(md_content, base_dir, tmp_dir):
    """Return list of (filename, absolute_path) for all images."""
    images = []
    seen = set()

    # Pattern 1: Markdown image syntax ![alt](src)
    md_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    for _alt, src in md_pattern.findall(md_content):
        _resolve_image(src, base_dir, tmp_dir, images, seen)

    # Pattern 2: HTML <img src="..."> tags
    img_pattern = re.compile(r'<img\s+[^>]*src="([^"]*)"[^>]*/?>',)
    for src in img_pattern.findall(md_content):
        _resolve_image(src, base_dir, tmp_dir, images, seen)

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
    is_draft = False
    if not dry_run:
        info = get_page_info(cfg, page_id)
        ver = info["version"]["number"]
        title = info["title"]
        space = info["space"]["key"]
        is_draft = info.get("status") == "draft"
        if is_draft:
            print(f"  DRAFT page | Version: {ver} | Space: {space}")
            # Extract title from MD H1 if draft has no title
            if not title:
                h1_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
                title = h1_match.group(1).strip() if h1_match else "Untitled"
                print(f"  Title from MD: {title}")
        else:
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

        images = collect_images(modified_md, base_dir, tmp_dir)
        image_widths = _build_width_map(images)
        html = postprocess_html(html, image_widths)
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

        if is_draft:
            # Draft workflow: publish first (minimal body), then attach, then update body
            print(f"[5a/7] Publishing draft as page '{title}'...")
            result = update_page_content(
                cfg, page_id, title, "<p>Publishing...</p>", ver + 1, space, publish_draft=True,
            )
            cur_ver = result["version"]["number"]
            print(f"  Published as v{cur_ver}")

            print(f"[5b/7] Uploading {len(images)} attachments...")
            for fname, fpath in images:
                upload_attachment(cfg, page_id, fpath, fname)

            new_ver = cur_ver + 1
            print(f"[6/7] Updating page body (v{cur_ver} -> v{new_ver})...")
            result = update_page_content(cfg, page_id, title, html, new_ver, space)
            final_ver = result["version"]["number"]
            print(f"  SUCCESS: Page updated to v{final_ver}")
        else:
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

    cfg = get_config()
    if not cfg["email"] or not cfg["token"]:
        print(
            "ERROR: ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN required.\n"
            "Set as environment variables or Windows User environment variables.",
            file=sys.stderr,
        )
        sys.exit(1)

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
