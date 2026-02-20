"""
Slack Client with Rate Limiting

Usage:
    client = SlackClient()  # Uses stored token
    client = SlackClient(token="xoxb-...")  # Explicit token

    # Send message
    result = client.send_message("#general", "Hello!")

    # Read history
    messages = client.get_history("C123", limit=20)

    # List channels
    channels = client.list_channels(include_private=True)
"""

import json
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .models import SlackToken, SlackTeam, SlackMessage, SlackChannel, SlackUser, SendResult
from .errors import (
    SlackError,
    SlackAuthError,
    SlackRateLimitError,
    SlackAPIError,
    SlackChannelNotFoundError,
    SlackTokenRevokedError,
    SlackNetworkError,
)


# Token file path
TOKEN_PATH = Path("C:/claude/json/slack_token.json")


class RateLimiter:
    """
    Per-method rate limiting for Slack API.

    Slack 2026 Rate Limits:
    - Tier 2 (~20 req/min): chat.postMessage, conversations.list
    - Tier 3 (~50 req/min): conversations.history
    - Tier 4 (~100 req/min): users.info
    """

    def __init__(self):
        self.method_intervals = {
            "chat.postMessage": 3.0,      # Tier 2
            "chat.update": 3.0,           # Tier 2
            "conversations.history": 1.2,  # Tier 3
            "conversations.list": 3.0,     # Tier 2
            "users.info": 0.6,             # Tier 4
            "auth.test": 1.0,              # Default
            "default": 1.0,
        }
        self.last_call: dict[str, float] = {}

    def wait_if_needed(self, method: str) -> None:
        """Wait if necessary to respect rate limits."""
        interval = self.method_intervals.get(method, self.method_intervals["default"])
        last = self.last_call.get(method, 0)
        elapsed = time.time() - last

        if elapsed < interval:
            time.sleep(interval - elapsed)

        self.last_call[method] = time.time()


def load_token() -> SlackToken:
    """Load token from file."""
    if not TOKEN_PATH.exists():
        raise SlackAuthError(
            f"Token file not found: {TOKEN_PATH}\n"
            "Run 'python -m lib.slack login' to authenticate."
        )

    try:
        data = json.loads(TOKEN_PATH.read_text(encoding="utf-8"))

        # Parse team as SlackTeam
        team_data = data.get("team", {})
        team = SlackTeam(id=team_data.get("id", ""), name=team_data.get("name", ""))

        # Parse created_at if present
        created_at = None
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
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
    except (json.JSONDecodeError, KeyError) as e:
        raise SlackAuthError(f"Invalid token file format: {e}")


class SlackClient:
    """
    Slack Web API client with rate limiting.

    Usage:
        client = SlackClient()  # Uses stored token
        client = SlackClient(token="xoxb-...")  # Explicit token
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize client.

        Args:
            token: Bot token (xoxb-...). If None, loads from file.
        """
        if token is None:
            token_obj = load_token()
            token = token_obj.access_token

        self._token = token
        self._client = WebClient(token=token)
        self._rate_limiter = RateLimiter()

    def _handle_error(self, error: SlackApiError) -> None:
        """Convert Slack API errors to custom exceptions."""
        response = error.response
        error_code = response.data.get("error", "unknown") if hasattr(response, 'data') else "unknown"

        if error_code == "ratelimited":
            retry_after = int(response.headers.get("Retry-After", 30))
            raise SlackRateLimitError(retry_after)
        elif error_code == "channel_not_found":
            raise SlackChannelNotFoundError(error_code)
        elif error_code == "token_revoked":
            raise SlackTokenRevokedError()
        elif error_code in ("invalid_auth", "account_inactive", "token_expired"):
            raise SlackAuthError(f"Authentication failed: {error_code}")
        else:
            raise SlackAPIError(error_code, response.data if hasattr(response, 'data') else {})

    def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None,
    ) -> SendResult:
        """
        Send a message to a channel.

        Args:
            channel: Channel ID (C...) or name (#general)
            text: Message text
            thread_ts: Reply in thread (optional)

        Returns:
            SendResult with ts, channel, permalink
        """
        self._rate_limiter.wait_if_needed("chat.postMessage")

        try:
            response = self._client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts,
            )

            return SendResult(
                ok=response.data.get("ok", True),
                ts=response.data["ts"],
                channel=response.data["channel"],
                message=response.data.get("message"),
            )
        except SlackApiError as e:
            self._handle_error(e)

    def update_message(
        self,
        channel: str,
        ts: str,
        text: str,
    ) -> SendResult:
        """
        Update an existing message.

        Args:
            channel: Channel ID where the message exists
            ts: Timestamp of the message to update
            text: New message text

        Returns:
            SendResult with updated ts, channel
        """
        self._rate_limiter.wait_if_needed("chat.update")

        try:
            response = self._client.chat_update(
                channel=channel,
                ts=ts,
                text=text,
            )

            return SendResult(
                ok=response.data.get("ok", True),
                ts=response.data["ts"],
                channel=response.data["channel"],
                message=response.data.get("message"),
            )
        except SlackApiError as e:
            self._handle_error(e)

    def get_history(
        self,
        channel: str,
        limit: int = 100,
        oldest: Optional[str] = None,
        latest: Optional[str] = None,
    ) -> list[SlackMessage]:
        """
        Get channel message history.

        Args:
            channel: Channel ID
            limit: Max messages to return (default 100)
            oldest: Only messages after this Unix timestamp (inclusive)
            latest: Only messages before this Unix timestamp (exclusive)

        Returns:
            List of SlackMessage objects
        """
        self._rate_limiter.wait_if_needed("conversations.history")

        try:
            params = {
                "channel": channel,
                "limit": limit,
            }
            if oldest is not None:
                params["oldest"] = oldest
            if latest is not None:
                params["latest"] = latest

            response = self._client.conversations_history(**params)

            messages = []
            for msg in response.data.get("messages", []):
                messages.append(SlackMessage(
                    ts=msg["ts"],
                    text=msg.get("text", ""),
                    channel=channel,
                    user=msg.get("user"),
                    thread_ts=msg.get("thread_ts"),
                    timestamp=datetime.fromtimestamp(float(msg["ts"])) if msg.get("ts") else None,
                ))

            return messages
        except SlackApiError as e:
            self._handle_error(e)

    def get_history_with_cursor(
        self,
        channel: str,
        limit: int = 100,
        oldest: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> tuple[list, Optional[str]]:
        """cursor 기반 채널 히스토리 페이지네이션.

        Args:
            channel: Channel ID
            limit: Max messages per page (default 100)
            oldest: Only messages after this Unix timestamp
            cursor: Pagination cursor from previous response

        Returns:
            (messages, next_cursor) — next_cursor is None if no more pages
        """
        self._rate_limiter.wait_if_needed("conversations.history")

        try:
            params: dict = {"channel": channel, "limit": limit}
            if oldest is not None:
                params["oldest"] = oldest
            if cursor is not None:
                params["cursor"] = cursor

            response = self._client.conversations_history(**params)

            messages = []
            for msg in response.data.get("messages", []):
                messages.append(SlackMessage(
                    ts=msg["ts"],
                    text=msg.get("text", ""),
                    channel=channel,
                    user=msg.get("user"),
                    thread_ts=msg.get("thread_ts"),
                    timestamp=datetime.fromtimestamp(float(msg["ts"])) if msg.get("ts") else None,
                    files=msg.get("files", []),
                ))

            next_cursor = response.data.get("response_metadata", {}).get("next_cursor") or None
            return messages, next_cursor
        except SlackApiError as e:
            self._handle_error(e)
            return [], None

    def list_channels(
        self,
        include_private: bool = False,
        exclude_archived: bool = True,
    ) -> list[SlackChannel]:
        """
        List channels the bot can access.

        Args:
            include_private: Include private channels
            exclude_archived: Exclude archived channels

        Returns:
            List of SlackChannel objects
        """
        self._rate_limiter.wait_if_needed("conversations.list")

        types = "public_channel,private_channel" if include_private else "public_channel"

        try:
            response = self._client.conversations_list(
                types=types,
                exclude_archived=exclude_archived,
            )

            channels = []
            for ch in response.data.get("channels", []):
                channels.append(SlackChannel(
                    id=ch["id"],
                    name=ch["name"],
                    is_private=ch.get("is_private", False),
                    is_archived=ch.get("is_archived", False),
                    is_member=ch.get("is_member", True),
                    num_members=ch.get("num_members"),
                    topic=ch.get("topic", {}).get("value") if isinstance(ch.get("topic"), dict) else None,
                    purpose=ch.get("purpose", {}).get("value") if isinstance(ch.get("purpose"), dict) else None,
                ))

            return channels
        except SlackApiError as e:
            self._handle_error(e)

    def get_user(self, user_id: str) -> SlackUser:
        """
        Get user information.

        Args:
            user_id: User ID (U...)

        Returns:
            SlackUser object
        """
        self._rate_limiter.wait_if_needed("users.info")

        try:
            response = self._client.users_info(user=user_id)

            user_data = response.data.get("user", {})
            profile = user_data.get("profile", {})

            return SlackUser(
                id=user_data.get("id", user_id),
                name=user_data.get("name", ""),
                real_name=user_data.get("real_name") or profile.get("real_name"),
                display_name=profile.get("display_name"),
                email=profile.get("email"),
                is_bot=user_data.get("is_bot", False),
            )
        except SlackApiError as e:
            self._handle_error(e)

    def validate_token(self) -> bool:
        """
        Check if token is valid.

        Returns:
            True if valid, False otherwise
        """
        try:
            self._rate_limiter.wait_if_needed("auth.test")
            response = self._client.auth_test()
            return response.data.get("ok", False)
        except SlackApiError:
            return False

    def auth_test(self) -> dict:
        """
        Test authentication and get user/team info.

        Returns:
            Auth info dict with user_id, team_id, team, user, etc.
        """
        self._rate_limiter.wait_if_needed("auth.test")

        try:
            response = self._client.auth_test()
            return response.data
        except SlackApiError as e:
            self._handle_error(e)

    # ==========================================
    # Slack Lists API (2025.09 Public Release)
    # Requires paid Slack plan
    # ==========================================

    def create_list(
        self,
        name: str,
        description: str = "",
        todo_mode: bool = True,
        schema: list[dict] = None,
    ) -> dict:
        """
        Create a new Slack List.

        Args:
            name: List name (title)
            description: Optional description
            todo_mode: If True, creates with Completed, Assignee, Due date columns
            schema: Custom column schema (optional)

        Returns:
            Created list info with list_id
        """
        self._rate_limiter.wait_if_needed("slackLists.create")

        try:
            params = {
                "name": name,
                "todo_mode": todo_mode,
            }

            if description:
                # description needs to be in Block Kit format
                params["description_blocks"] = [
                    {
                        "type": "rich_text",
                        "elements": [{
                            "type": "rich_text_section",
                            "elements": [{
                                "type": "text",
                                "text": description,
                            }]
                        }]
                    }
                ]

            if schema:
                params["schema"] = schema

            response = self._client.api_call(
                "slackLists.create",
                json=params,
            )

            if not response.data.get("ok"):
                raise SlackAPIError(
                    response.data.get("error", "unknown"),
                    response.data,
                )

            return response.data
        except SlackApiError as e:
            self._handle_error(e)

    def add_list_item(
        self,
        list_id: str,
        fields: dict[str, any],
    ) -> dict:
        """
        Add an item to a Slack List.

        Args:
            list_id: ID of the list
            fields: Field values keyed by column_id

        Returns:
            Created item info
        """
        self._rate_limiter.wait_if_needed("slackLists.items.create")

        try:
            # Convert fields to initial_fields format
            initial_fields = []
            for column_id, value in fields.items():
                if isinstance(value, str):
                    # Text fields require rich_text as array (not wrapped in value)
                    initial_fields.append({
                        "column_id": column_id,
                        "rich_text": [{
                            "type": "rich_text",
                            "elements": [{
                                "type": "rich_text_section",
                                "elements": [{
                                    "type": "text",
                                    "text": value,
                                }]
                            }]
                        }]
                    })
                elif isinstance(value, bool):
                    # Boolean fields (like todo_completed)
                    initial_fields.append({
                        "column_id": column_id,
                        "checkbox": value,
                    })
                else:
                    initial_fields.append({
                        "column_id": column_id,
                        "value": value,
                    })

            response = self._client.api_call(
                "slackLists.items.create",
                json={
                    "list_id": list_id,
                    "initial_fields": initial_fields,
                },
            )

            if not response.data.get("ok"):
                raise SlackAPIError(
                    response.data.get("error", "unknown"),
                    response.data,
                )

            return response.data
        except SlackApiError as e:
            self._handle_error(e)

    def delete_message(self, channel: str, ts: str) -> bool:
        """
        Delete a message from a channel.

        Args:
            channel: Channel ID
            ts: Message timestamp

        Returns:
            True if deleted successfully
        """
        self._rate_limiter.wait_if_needed("chat.delete")

        try:
            response = self._client.chat_delete(channel=channel, ts=ts)
            return response.data.get("ok", False)
        except SlackApiError as e:
            self._handle_error(e)

    def get_list_items(self, list_id: str, limit: int = 100) -> dict:
        """
        Get items from a Slack List.

        Args:
            list_id: ID of the list
            limit: Max items to return

        Returns:
            List items data
        """
        self._rate_limiter.wait_if_needed("slackLists.items.list")

        try:
            response = self._client.api_call(
                "slackLists.items.list",
                params={
                    "list_id": list_id,
                    "limit": limit,
                },
            )

            if not response.data.get("ok"):
                raise SlackAPIError(
                    response.data.get("error", "unknown"),
                    response.data,
                )

            return response.data
        except SlackApiError as e:
            self._handle_error(e)


    def get_channel_info(self, channel_id: str) -> dict:
        """
        Get channel information.

        Args:
            channel_id: Channel ID (C...)

        Returns:
            Channel info dict
        """
        self._rate_limiter.wait_if_needed("conversations.info")

        try:
            response = self._client.conversations_info(channel=channel_id)
            return response.data["channel"]
        except SlackApiError as e:
            self._handle_error(e)

    def get_channel_members(self, channel_id: str) -> list[str]:
        """
        Get channel members.

        Args:
            channel_id: Channel ID (C...)

        Returns:
            List of member user IDs
        """
        self._rate_limiter.wait_if_needed("conversations.members")

        try:
            response = self._client.conversations_members(channel=channel_id)
            return response.data["members"]
        except SlackApiError as e:
            self._handle_error(e)

    def get_pins(self, channel_id: str) -> list[dict]:
        """
        Get pinned messages in a channel.

        Args:
            channel_id: Channel ID (C...)

        Returns:
            List of pinned item dicts
        """
        self._rate_limiter.wait_if_needed("pins.list")

        try:
            response = self._client.pins_list(channel=channel_id)
            return response.data["items"]
        except SlackApiError as e:
            self._handle_error(e)


class SlackUserClient(SlackClient):
    """
    Slack client using User Token for features not available to bots.

    Required for:
    - Slack Lists API (lists:read, lists:write)

    Usage:
        from lib.slack import SlackUserClient

        client = SlackUserClient()  # Uses stored user token
        result = client.create_list("My List", "Description")
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize client with user token.

        Args:
            token: User token (xoxp-...). If None, loads from file.
        """
        if token is None:
            from .auth import get_user_token
            user_token = get_user_token()
            if user_token is None:
                raise SlackAuthError(
                    "User token not found. Run 'python -m lib.slack login --user' to authenticate."
                )
            token = user_token.access_token

        # Initialize parent with user token
        super().__init__(token=token)
