"""
Vimeo OAuth Browser-based authentication.

Uses Browser OAuth flow (not API key) per CLAUDE.md rules.
Token is stored locally for reuse.
"""

import json
import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

# Token storage path
TOKEN_PATH = Path("C:/claude/json/vimeo_token.json")
CREDENTIALS_PATH = Path("C:/claude/json/vimeo_credentials.json")

# Vimeo OAuth endpoints
AUTHORIZE_URL = "https://api.vimeo.com/oauth/authorize"
TOKEN_URL = "https://api.vimeo.com/oauth/access_token"


def load_credentials() -> dict:
    """Load Vimeo app credentials from file."""
    if not CREDENTIALS_PATH.exists():
        print(f"❌ Credentials file not found: {CREDENTIALS_PATH}")
        print("\n📋 Create the file with your Vimeo app credentials:")
        print(json.dumps({
            "client_id": "YOUR_CLIENT_ID",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uri": "http://localhost:8585/callback"
        }, indent=2))
        sys.exit(1)

    with open(CREDENTIALS_PATH) as f:
        return json.load(f)


def load_token() -> dict | None:
    """Load saved token if exists."""
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH) as f:
            return json.load(f)
    return None


def save_token(token_data: dict) -> None:
    """Save token to file."""
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        json.dump(token_data, f, indent=2)
    print(f"✅ Token saved to {TOKEN_PATH}")


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to receive OAuth callback."""

    authorization_code = None

    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        parsed = urlparse(self.path)
        if parsed.path == "/callback":
            query = parse_qs(parsed.query)
            if "code" in query:
                OAuthCallbackHandler.authorization_code = query["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write("""
                    <html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
                    <h1>✅ Vimeo 인증 완료!</h1>
                    <p>이 창을 닫아도 됩니다.</p>
                    </body></html>
                """.encode("utf-8"))
            else:
                self.send_response(400)
                self.end_headers()
                error = query.get("error", ["Unknown error"])[0]
                self.wfile.write(f"Error: {error}".encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def authenticate(force: bool = False) -> str:
    """
    Authenticate with Vimeo using Browser OAuth flow.

    Args:
        force: Force re-authentication even if token exists

    Returns:
        Access token string
    """
    # Check for existing valid token
    if not force:
        token_data = load_token()
        if token_data and "access_token" in token_data:
            print("✅ Using saved Vimeo token")
            return token_data["access_token"]

    credentials = load_credentials()
    client_id = credentials["client_id"]
    client_secret = credentials["client_secret"]
    redirect_uri = credentials.get("redirect_uri", "http://localhost:8585/callback")

    # Scopes for video management
    scopes = [
        "public",
        "private",
        "create",
        "edit",
        "delete",
        "upload",
        "video_files",
    ]

    # Build authorization URL
    auth_url = (
        f"{AUTHORIZE_URL}"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={' '.join(scopes)}"
        f"&state=wsoptv_auth"
    )

    print("🌐 Opening browser for Vimeo authentication...")
    print(f"   If browser doesn't open, visit:\n   {auth_url}\n")
    webbrowser.open(auth_url)

    # Start local server to receive callback
    port = int(redirect_uri.split(":")[-1].split("/")[0])
    server = HTTPServer(("localhost", port), OAuthCallbackHandler)
    print(f"⏳ Waiting for authorization callback on port {port}...")

    # Wait for callback
    while OAuthCallbackHandler.authorization_code is None:
        server.handle_request()

    code = OAuthCallbackHandler.authorization_code
    print("✅ Authorization code received")

    # Exchange code for token
    print("🔄 Exchanging code for access token...")
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        },
        auth=(client_id, client_secret),
        headers={"Accept": "application/vnd.vimeo.*+json;version=3.4"},
    )

    if response.status_code != 200:
        print(f"❌ Token exchange failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

    token_data = response.json()
    save_token(token_data)

    # Show account info
    if "user" in token_data:
        user = token_data["user"]
        print(f"\n👤 Logged in as: {user.get('name', 'Unknown')}")
        print(f"   Account: {user.get('account', 'Unknown')}")

    return token_data["access_token"]


def get_client():
    """Get authenticated Vimeo client with extended timeout."""
    import vimeo

    token = authenticate()
    credentials = load_credentials()

    client = vimeo.VimeoClient(
        token=token,
        key=credentials["client_id"],
        secret=credentials["client_secret"],
    )

    # Set extended timeout for large file uploads (10 minutes)
    # PyVimeo uses requests internally, so we configure the timeout on the session
    if hasattr(client, '_store') and hasattr(client._store, 'session'):
        # Configure timeout via requests.Session adapter
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry

        # Create adapter with timeout settings
        adapter = HTTPAdapter(
            max_retries=Retry(total=0, connect=3, read=3, status=0)
        )
        client._store.session.mount('https://', adapter)

        # Set default timeout to 600 seconds (10 minutes) for upload operations
        original_request = client._store.session.request

        def request_with_timeout(*args, **kwargs):
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 600
            return original_request(*args, **kwargs)

        client._store.session.request = request_with_timeout

    return client


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Vimeo authentication")
    parser.add_argument("--force", "-f", action="store_true", help="Force re-authentication")
    args = parser.parse_args()

    token = authenticate(force=args.force)
    print(f"\n🔑 Access token: {token[:20]}...")
