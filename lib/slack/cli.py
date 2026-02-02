"""
Slack CLI

Usage:
    python -m lib.slack login
    python -m lib.slack send "#general" "Hello!"
    python -m lib.slack history "#general" --limit 10
    python -m lib.slack channels --include-private
    python -m lib.slack user U123456789
"""

import sys
import io

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

app = typer.Typer(
    name="slack",
    help="Slack CLI - Message sending and channel management",
    add_completion=False,
)
console = Console()


@app.command()
def login(
    port: int = typer.Option(None, "--port", "-p", help="OAuth callback port (default: auto-detect)")
):
    """
    Authenticate with Slack via OAuth.

    Opens browser for Slack authorization and saves token locally.
    """
    from .auth import login as do_login
    from .errors import SlackError

    try:
        token = do_login(port=port)
        console.print("[green]✓ Logged in successfully![/green]")
        console.print(f"  Bot User: {token.bot_user_id}")
        console.print(f"  Workspace: {token.team.name}")
        console.print(f"  Scopes: {token.scope}")
    except SlackError as e:
        console.print(f"[red]✗ Login failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def status(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """
    Check current authentication status.
    """
    from .auth import get_token
    from .client import SlackClient
    from .errors import SlackError

    token = get_token()

    if token is None:
        if json_output:
            print(json.dumps({"authenticated": False, "error": "Not logged in"}, ensure_ascii=False))
        else:
            console.print("[yellow]Not logged in. Run 'python -m lib.slack login' first.[/yellow]")
        raise typer.Exit(1)

    # Validate token
    valid = False
    try:
        client = SlackClient(token=token.access_token)
        valid = client.validate_token()
    except SlackError:
        pass

    if json_output:
        print(json.dumps({
            "authenticated": True,
            "valid": valid,
            "bot_user_id": token.bot_user_id,
            "workspace": token.team.name,
            "team_id": token.team.id,
            "scopes": token.scope.split(",") if token.scope else [],
        }, ensure_ascii=False, indent=2))
    else:
        console.print("[bold]Token Info:[/bold]")
        console.print(f"  Bot User: {token.bot_user_id}")
        console.print(f"  Workspace: {token.team.name}")
        console.print(f"  Scopes: {token.scope}")
        if valid:
            console.print("  Status: [green]Valid[/green]")
        else:
            console.print("  Status: [red]Invalid (re-login required)[/red]")


@app.command()
def send(
    channel: str = typer.Argument(..., help="Channel ID (C...) or name (#general)"),
    message: str = typer.Argument(..., help="Message text"),
    thread_ts: Optional[str] = typer.Option(None, "--thread", "-t", help="Thread timestamp for reply"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """
    Send a message to a Slack channel.
    """
    from .client import SlackClient
    from .errors import SlackError

    try:
        client = SlackClient()
        result = client.send_message(channel, message, thread_ts=thread_ts)

        if json_output:
            print(json.dumps({
                "ok": True,
                "channel": result.channel,
                "ts": result.ts,
                "permalink": result.permalink,
            }, ensure_ascii=False, indent=2))
        else:
            console.print("[green]✓ Message sent![/green]")
            console.print(f"  Channel: {result.channel}")
            console.print(f"  Timestamp: {result.ts}")
            console.print(f"  Permalink: {result.permalink}")
    except SlackError as e:
        if json_output:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        else:
            console.print(f"[red]✗ Failed to send message: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def history(
    channel: str = typer.Argument(..., help="Channel ID (C...) or name"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of messages to retrieve"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """
    Read message history from a channel.
    """
    from .client import SlackClient
    from .errors import SlackError

    try:
        client = SlackClient()
        messages = client.get_history(channel, limit=limit)

        if json_output:
            output = [{
                "ts": msg.ts,
                "user": msg.user,
                "text": msg.text,
                "thread_ts": msg.thread_ts,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
            } for msg in messages]
            print(json.dumps({"channel": channel, "count": len(messages), "messages": output}, ensure_ascii=False, indent=2))
        else:
            if not messages:
                console.print("[yellow]No messages found.[/yellow]")
                return

            console.print(f"[bold]Messages in {channel} (latest {len(messages)}):[/bold]\n")

            for msg in reversed(messages):  # Show oldest first
                user_display = msg.user or "bot"
                text_preview = msg.text[:100] + "..." if len(msg.text) > 100 else msg.text
                timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M") if msg.timestamp else msg.ts

                if msg.thread_ts and msg.thread_ts != msg.ts:
                    console.print(f"  [dim]↳ {timestamp}[/dim] [cyan]{user_display}[/cyan]: {text_preview}")
                else:
                    console.print(f"  [dim]{timestamp}[/dim] [cyan]{user_display}[/cyan]: {text_preview}")
    except SlackError as e:
        if json_output:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            console.print(f"[red]✗ Failed to read history: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def channels(
    include_private: bool = typer.Option(False, "--private", "-p", help="Include private channels"),
    show_archived: bool = typer.Option(False, "--archived", "-a", help="Include archived channels"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """
    List all accessible channels.
    """
    from .client import SlackClient
    from .errors import SlackError

    try:
        client = SlackClient()
        channel_list = client.list_channels(
            include_private=include_private,
            exclude_archived=not show_archived,
        )

        if json_output:
            output = [{
                "id": ch.id,
                "name": ch.name,
                "is_private": ch.is_private,
                "is_archived": ch.is_archived,
                "num_members": ch.num_members,
            } for ch in channel_list]
            print(json.dumps({"count": len(channel_list), "channels": output}, ensure_ascii=False, indent=2))
        else:
            if not channel_list:
                console.print("[yellow]No channels found.[/yellow]")
                return

            table = Table(title=f"Channels ({len(channel_list)})")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Private", justify="center")
            table.add_column("Members", justify="right")

            for ch in channel_list:
                private_icon = "🔒" if ch.is_private else ""
                members = str(ch.num_members) if ch.num_members else "-"
                table.add_row(ch.id, f"#{ch.name}", private_icon, members)

            console.print(table)
    except SlackError as e:
        if json_output:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            console.print(f"[red]✗ Failed to list channels: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def user(
    user_id: str = typer.Argument(..., help="User ID (U...)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
):
    """
    Get user information.
    """
    from .client import SlackClient
    from .errors import SlackError

    try:
        client = SlackClient()
        user_info = client.get_user(user_id)

        if json_output:
            print(json.dumps({
                "id": user_info.id,
                "name": user_info.name,
                "real_name": user_info.real_name,
                "display_name": user_info.display_name,
                "email": user_info.email,
                "is_bot": user_info.is_bot,
            }, ensure_ascii=False, indent=2))
        else:
            console.print("[bold]User Info:[/bold]")
            console.print(f"  ID: {user_info.id}")
            console.print(f"  Username: @{user_info.name}")
            if user_info.real_name:
                console.print(f"  Real Name: {user_info.real_name}")
            if user_info.display_name:
                console.print(f"  Display Name: {user_info.display_name}")
            if user_info.email:
                console.print(f"  Email: {user_info.email}")
            console.print(f"  Is Bot: {'Yes' if user_info.is_bot else 'No'}")
    except SlackError as e:
        if json_output:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            console.print(f"[red]✗ Failed to get user info: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
