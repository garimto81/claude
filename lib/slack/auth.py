"""
Slack OAuth 2.0 Authentication

Usage:
    from lib.slack.auth import login, get_token

    # First time: OAuth flow
    token = login()

    # Subsequent: Load from file
    token = get_token()
"""

import json
import socket
import webbrowser
import http.server
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Optional

import requests

from .models import SlackCredentials, SlackToken, SlackTeam
from .errors import SlackAuthError, SlackCredentialsNotFoundError


# File paths
CREDENTIALS_PATH = Path("C:/claude/json/slack_credentials.json")
TOKEN_PATH = Path("C:/claude/json/slack_token.json")

# Default OAuth scopes
DEFAULT_SCOPES = [
    "chat:write",
    "channels:read",
    "channels:history",
    "groups:read",
    "groups:history",
    "im:write",
    "users:read",
]

# Port range for OAuth callback
PORTS = [8765, 8766, 8767, 8768, 8769, 8770]


def load_credentials() -> SlackCredentials:
    """
    Load OAuth credentials from file.

    Returns:
        SlackCredentials object

    Raises:
        SlackCredentialsNotFoundError: If credentials file not found
    """
    if not CREDENTIALS_PATH.exists():
        raise SlackCredentialsNotFoundError(str(CREDENTIALS_PATH))

    try:
        data = json.loads(CREDENTIALS_PATH.read_text(encoding="utf-8"))
        return SlackCredentials(**data)
    except (json.JSONDecodeError, KeyError) as e:
        raise SlackAuthError(f"Invalid credentials file: {e}")


def build_auth_url(credentials: SlackCredentials, port: int, scopes: list[str] = None) -> str:
    """
    Build Slack OAuth authorization URL.

    Args:
        credentials: OAuth app credentials
        port: Local callback server port
        scopes: OAuth scopes (default: DEFAULT_SCOPES)

    Returns:
        Authorization URL string
    """
    scopes = scopes or DEFAULT_SCOPES
    redirect_uri = f"http://localhost:{port}/slack/oauth/callback"

    params = {
        "client_id": credentials.client_id,
        "scope": ",".join(scopes),
        "redirect_uri": redirect_uri,
    }

    query = urllib.parse.urlencode(params)
    return f"https://slack.com/oauth/v2/authorize?{query}"


def exchange_code(credentials: SlackCredentials, code: str, port: int) -> SlackToken:
    """
    Exchange authorization code for access token.

    Args:
        credentials: OAuth app credentials
        code: Authorization code from callback
        port: Local callback server port

    Returns:
        SlackToken object

    Raises:
        SlackAuthError: If token exchange fails
    """
    redirect_uri = f"http://localhost:{port}/slack/oauth/callback"

    response = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
    )

    data = response.json()

    if not data.get("ok"):
        error = data.get("error", "unknown")
        raise SlackAuthError(f"Token exchange failed: {error}")

    team_data = data.get("team", {})
    team = SlackTeam(
        id=team_data.get("id", ""),
        name=team_data.get("name", ""),
    )

    return SlackToken(
        access_token=data["access_token"],
        token_type=data.get("token_type", "bot"),
        scope=data.get("scope", ""),
        bot_user_id=data.get("bot_user_id", ""),
        app_id=data.get("app_id", ""),
        team=team,
        authed_user=data.get("authed_user"),
        created_at=datetime.now(),
    )


def save_token(token: SlackToken) -> None:
    """
    Save token to file.

    Args:
        token: SlackToken to save
    """
    # Ensure directory exists
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict
    data = {
        "access_token": token.access_token,
        "token_type": token.token_type,
        "scope": token.scope,
        "bot_user_id": token.bot_user_id,
        "app_id": token.app_id,
        "team": {
            "id": token.team.id,
            "name": token.team.name,
        },
        "authed_user": token.authed_user,
        "created_at": token.created_at.isoformat() if token.created_at else None,
    }

    TOKEN_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def find_available_port() -> int:
    """
    Find an available port for OAuth callback server.

    Returns:
        Available port number

    Raises:
        SlackAuthError: If no ports available
    """
    for port in PORTS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue

    raise SlackAuthError(f"No available ports for OAuth callback (tried {PORTS})")


def get_token() -> Optional[SlackToken]:
    """
    Load token from file.

    Returns:
        SlackToken if file exists, None otherwise
    """
    if not TOKEN_PATH.exists():
        return None

    try:
        data = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))

        team_data = data.get("team", {})
        team = SlackTeam(
            id=team_data.get("id", ""),
            name=team_data.get("name", ""),
        )

        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass

        return SlackToken(
            access_token=data["access_token"],
            token_type=data.get("token_type", "bot"),
            scope=data.get("scope", ""),
            bot_user_id=data.get("bot_user_id", ""),
            app_id=data.get("app_id", ""),
            team=team,
            authed_user=data.get("authed_user"),
            created_at=created_at,
        )
    except (json.JSONDecodeError, KeyError):
        return None


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""

    def log_message(self, format, *args):
        """Suppress logging."""
        pass

    def do_GET(self):
        """Handle OAuth callback."""
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/slack/oauth/callback":
            query = urllib.parse.parse_qs(parsed.query)

            if "code" in query:
                self.server.auth_code = query["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h1>Login Successful!</h1>"
                    b"<p>You can close this window.</p></body></html>"
                )
            elif "error" in query:
                error = query.get("error", ["unknown"])[0]
                self.server.auth_error = error
                self.send_response(400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    f"<html><body><h1>Login Failed</h1><p>Error: {error}</p></body></html>".encode()
                )
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing code parameter")
        else:
            self.send_response(404)
            self.end_headers()


def login(port: int = None) -> SlackToken:
    """
    Perform OAuth flow to get access token.

    Args:
        port: Callback server port (auto-detected if None)

    Returns:
        SlackToken object

    Raises:
        SlackAuthError: If login fails
    """
    # Load credentials
    credentials = load_credentials()

    # Find available port
    if port is None:
        port = find_available_port()

    # Build authorization URL
    auth_url = build_auth_url(credentials, port)

    print(f"Opening browser for Slack authorization...")
    print(f"If browser doesn't open, visit: {auth_url}")

    # Start local server
    server_address = ("localhost", port)
    httpd = http.server.HTTPServer(server_address, OAuthCallbackHandler)
    httpd.auth_code = None
    httpd.auth_error = None

    # Open browser
    webbrowser.open(auth_url)

    # Wait for callback
    print(f"Waiting for authorization on port {port}...")
    httpd.handle_request()

    # Check result
    if httpd.auth_error:
        raise SlackAuthError(f"Authorization failed: {httpd.auth_error}")

    if not httpd.auth_code:
        raise SlackAuthError("No authorization code received")

    # Exchange code for token
    print("Exchanging code for token...")
    token = exchange_code(credentials, httpd.auth_code, port)

    # Save token
    save_token(token)
    print(f"Token saved to {TOKEN_PATH}")
    print(f"Logged in as bot: {token.bot_user_id} in workspace: {token.team.name}")

    return token
