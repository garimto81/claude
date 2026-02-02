"""
Slack Integration Library

Browser OAuth authentication, message sending/receiving, channel management.

Usage:
    from lib.slack import SlackClient, login, get_token

    # First time: OAuth flow
    login()

    # Create client
    client = SlackClient()

    # Send message
    result = client.send_message("#general", "Hello!")

    # Read history
    messages = client.get_history("#general", limit=10)

    # List channels
    channels = client.list_channels(include_private=True)

CLI Usage:
    python -m lib.slack login
    python -m lib.slack send "#general" "Hello!"
    python -m lib.slack history "#general"
    python -m lib.slack channels
"""

__version__ = "1.0.0"

from .client import SlackClient, RateLimiter, load_token
from .auth import login, get_token, load_credentials, save_token
from .models import (
    SlackCredentials,
    SlackTeam,
    SlackToken,
    SlackMessage,
    SlackChannel,
    SlackUser,
    SendResult,
)
from .errors import (
    SlackError,
    SlackAuthError,
    SlackRateLimitError,
    SlackAPIError,
    SlackChannelNotFoundError,
    SlackTokenRevokedError,
    SlackCredentialsNotFoundError,
    SlackNetworkError,
)

__all__ = [
    # Version
    "__version__",
    # Client
    "SlackClient",
    "RateLimiter",
    "load_token",
    # Auth
    "login",
    "get_token",
    "load_credentials",
    "save_token",
    # Models
    "SlackCredentials",
    "SlackTeam",
    "SlackToken",
    "SlackMessage",
    "SlackChannel",
    "SlackUser",
    "SendResult",
    # Errors
    "SlackError",
    "SlackAuthError",
    "SlackRateLimitError",
    "SlackAPIError",
    "SlackChannelNotFoundError",
    "SlackTokenRevokedError",
    "SlackCredentialsNotFoundError",
    "SlackNetworkError",
]
