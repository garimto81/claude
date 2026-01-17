#!/usr/bin/env python3
"""Multi-AI Authentication CLI

외부 AI 서비스(GPT, Gemini, Poe)에 대한 OAuth 인증 통합 관리.

Usage:
    python main.py login --provider openai
    python main.py login --provider google
    python main.py login --provider poe --api-key "sk-..."
    python main.py status
    python main.py logout --provider openai
    python main.py logout --all
"""

import argparse
import asyncio
import sys
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from providers import OpenAIProvider, GoogleProvider, PoeProvider, BaseProvider, AuthToken
from storage import TokenStore

console = Console()


# Provider 레지스트리
PROVIDERS: dict[str, type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "google": GoogleProvider,
    "poe": PoeProvider,
}


def get_provider(name: str) -> BaseProvider:
    """Provider 인스턴스 생성"""
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDERS.keys())}")
    return PROVIDERS[name]()


async def cmd_login(provider_name: str, api_key: Optional[str] = None) -> None:
    """로그인 커맨드"""
    console.print(f"\n[bold cyan]🔐 {provider_name.upper()} 인증 시작...[/bold cyan]\n")

    try:
        provider = get_provider(provider_name)
        store = TokenStore()

        # 기존 토큰 확인
        existing_token = await store.load(provider_name)
        if existing_token and not existing_token.is_expired():
            console.print(f"[yellow]⚠️ 이미 {provider_name}에 로그인되어 있습니다.[/yellow]")
            console.print("[dim]새로 로그인하려면 먼저 logout 하세요.[/dim]\n")
            return

        # 로그인 수행
        if api_key:
            token = await provider.login(api_key=api_key)
        else:
            token = await provider.login()

        # 계정 정보 조회
        account_info = await provider.get_account_info(token)
        if account_info:
            token.account_info = account_info

        # 토큰 저장
        await store.save(token)

        # 결과 출력
        console.print()
        console.print(Panel.fit(
            f"[bold green]✅ {provider.display_name} 인증 성공![/bold green]\n\n"
            f"Provider: {provider.display_name}\n"
            f"만료: {token.expires_at.strftime('%Y-%m-%d') if token.expires_at else '무제한'}",
            title="인증 완료",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[bold red]❌ 인증 실패: {e}[/bold red]\n")
        sys.exit(1)


async def cmd_status() -> None:
    """상태 확인 커맨드"""
    console.print("\n[bold cyan]## AI 인증 상태[/bold cyan]\n")

    store = TokenStore()

    # 테이블 생성
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Provider", style="cyan")
    table.add_column("상태", justify="center")
    table.add_column("계정", style="dim")
    table.add_column("만료", justify="right")

    for provider_name, provider_class in PROVIDERS.items():
        token = await store.load(provider_name)

        if token:
            provider = provider_class()
            is_valid = provider.is_token_valid(token)

            status = "[green]✅ 활성[/green]" if is_valid else "[red]❌ 만료[/red]"

            # 계정 정보
            account = "-"
            if token.account_info:
                account = token.account_info.get("email", token.account_info.get("status", "-"))

            # 만료 정보
            if token.expires_at:
                days = token.expires_in_days()
                expiry = f"{days}일" if days is not None else "-"
            else:
                expiry = "무제한"

            table.add_row(provider.display_name, status, account, expiry)
        else:
            table.add_row(
                provider_class().display_name,
                "[dim]❌ 미인증[/dim]",
                "-",
                "-"
            )

    console.print(table)
    console.print()


async def cmd_logout(provider_name: Optional[str] = None, logout_all: bool = False) -> None:
    """로그아웃 커맨드"""
    store = TokenStore()

    if logout_all:
        console.print("\n[bold yellow]모든 인증을 해제합니다...[/bold yellow]\n")
        providers = await store.list_providers()
        for name in providers:
            token = await store.load(name)
            if token:
                provider = get_provider(name)
                await provider.logout(token)
                await store.delete(name)
                console.print(f"  [dim]✓[/dim] {name} 로그아웃")
        console.print("\n[green]✅ 모든 인증이 해제되었습니다.[/green]\n")
    elif provider_name:
        console.print(f"\n[bold yellow]{provider_name} 로그아웃 중...[/bold yellow]\n")
        token = await store.load(provider_name)
        if token:
            provider = get_provider(provider_name)
            await provider.logout(token)
            await store.delete(provider_name)
            console.print(f"[green]✅ {provider_name} 로그아웃 완료[/green]\n")
        else:
            console.print(f"[dim]{provider_name}에 로그인되어 있지 않습니다.[/dim]\n")
    else:
        console.print("[red]--provider 또는 --all 옵션을 지정하세요.[/red]")


async def cmd_refresh(provider_name: str) -> None:
    """토큰 갱신 커맨드"""
    console.print(f"\n[bold cyan]{provider_name} 토큰 갱신 중...[/bold cyan]\n")

    store = TokenStore()
    token = await store.load(provider_name)

    if not token:
        console.print(f"[red]{provider_name}에 로그인되어 있지 않습니다.[/red]")
        return

    try:
        provider = get_provider(provider_name)
        new_token = await provider.refresh(token)
        await store.save(new_token)
        console.print(f"[green]✅ {provider_name} 토큰 갱신 완료[/green]\n")
    except Exception as e:
        console.print(f"[red]❌ 토큰 갱신 실패: {e}[/red]")
        console.print("[dim]다시 로그인이 필요할 수 있습니다.[/dim]\n")


def main():
    """메인 엔트리포인트"""
    parser = argparse.ArgumentParser(
        description="Multi-AI Authentication CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # login
    login_parser = subparsers.add_parser("login", help="AI 서비스에 로그인")
    login_parser.add_argument(
        "--provider", "-p",
        required=True,
        choices=list(PROVIDERS.keys()),
        help="Provider 이름"
    )
    login_parser.add_argument(
        "--api-key", "-k",
        help="API Key (Poe 등)"
    )

    # status
    subparsers.add_parser("status", help="인증 상태 확인")

    # logout
    logout_parser = subparsers.add_parser("logout", help="로그아웃")
    logout_parser.add_argument(
        "--provider", "-p",
        choices=list(PROVIDERS.keys()),
        help="Provider 이름"
    )
    logout_parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="모든 인증 해제"
    )

    # refresh
    refresh_parser = subparsers.add_parser("refresh", help="토큰 갱신")
    refresh_parser.add_argument(
        "--provider", "-p",
        required=True,
        choices=list(PROVIDERS.keys()),
        help="Provider 이름"
    )

    args = parser.parse_args()

    if args.command == "login":
        asyncio.run(cmd_login(args.provider, args.api_key))
    elif args.command == "status":
        asyncio.run(cmd_status())
    elif args.command == "logout":
        asyncio.run(cmd_logout(args.provider, args.all))
    elif args.command == "refresh":
        asyncio.run(cmd_refresh(args.provider))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
