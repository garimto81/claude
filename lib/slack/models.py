"""
Slack Library Pydantic Models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, computed_field


class SlackCredentials(BaseModel):
    """OAuth app credentials from slack_credentials.json"""

    client_id: str
    client_secret: str
    redirect_uri: str = "http://localhost:8765/slack/oauth/callback"


class SlackTeam(BaseModel):
    """Slack workspace/team info"""

    id: str
    name: str


class SlackToken(BaseModel):
    """OAuth token stored in slack_token.json"""

    access_token: str
    token_type: str = "bot"
    scope: str
    bot_user_id: str
    app_id: str
    team: SlackTeam
    authed_user: Optional[dict] = None
    created_at: Optional[datetime] = None


class SlackMessage(BaseModel):
    """Slack message"""

    ts: str  # Message timestamp (unique ID)
    text: str
    channel: str
    user: Optional[str] = None
    thread_ts: Optional[str] = None
    timestamp: Optional[datetime] = None  # Parsed timestamp

    @computed_field
    @property
    def permalink(self) -> str:
        """Generate message permalink"""
        ts_no_dot = self.ts.replace(".", "")
        return f"https://slack.com/archives/{self.channel}/p{ts_no_dot}"


class SlackChannel(BaseModel):
    """Slack channel info"""

    id: str
    name: str
    is_private: bool = False
    is_archived: bool = False
    is_member: bool = True
    num_members: Optional[int] = None
    topic: Optional[str] = None
    purpose: Optional[str] = None


class SlackUser(BaseModel):
    """Slack user info"""

    id: str
    name: str
    real_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    is_bot: bool = False


class SendResult(BaseModel):
    """Result of sending a message"""

    ok: bool
    ts: str
    channel: str
    message: Optional[dict] = None

    @computed_field
    @property
    def permalink(self) -> str:
        """Generate message permalink"""
        ts_no_dot = self.ts.replace(".", "")
        return f"https://slack.com/archives/{self.channel}/p{ts_no_dot}"
