"""RFC 8628 Device Authorization Grant 구현

Headless/CLI 환경에 최적화된 OAuth 플로우.
ChatGPT Plus/Pro 구독자의 Codex CLI 인증에 사용.
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import httpx
from rich.console import Console
from rich.panel import Panel

console = Console()


@dataclass
class DeviceCodeResponse:
    """Device code 응답"""
    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: Optional[str]
    expires_in: int
    interval: int


@dataclass
class TokenResponse:
    """Token 응답"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_in: int
    scope: Optional[str]


class DeviceFlowError(Exception):
    """Device Flow 에러"""
    pass


class DeviceFlow:
    """RFC 8628 Device Authorization Grant 구현

    Example:
        flow = DeviceFlow(
            client_id="your-client-id",
            device_auth_endpoint="https://auth.example.com/device",
            token_endpoint="https://auth.example.com/token"
        )
        token = await flow.authenticate()
    """

    def __init__(
        self,
        client_id: str,
        device_auth_endpoint: str,
        token_endpoint: str,
        client_secret: Optional[str] = None,
        scope: str = "chat"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.device_auth_endpoint = device_auth_endpoint
        self.token_endpoint = token_endpoint
        self.scope = scope

    async def request_device_code(self) -> DeviceCodeResponse:
        """Device code 요청

        Returns:
            DeviceCodeResponse: device_code, user_code, verification_uri 포함
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.device_auth_endpoint,
                data={
                    "client_id": self.client_id,
                    "scope": self.scope
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                raise DeviceFlowError(f"Device code request failed: {response.text}")

            data = response.json()
            return DeviceCodeResponse(
                device_code=data["device_code"],
                user_code=data["user_code"],
                verification_uri=data["verification_uri"],
                verification_uri_complete=data.get("verification_uri_complete"),
                expires_in=data.get("expires_in", 1800),
                interval=data.get("interval", 5)
            )

    async def poll_for_token(
        self,
        device_code: str,
        interval: int = 5,
        expires_in: int = 1800
    ) -> TokenResponse:
        """Token polling

        Args:
            device_code: Device code
            interval: Polling interval (seconds)
            expires_in: Token expiration (seconds)

        Returns:
            TokenResponse: access_token 포함
        """
        start_time = time.time()

        async with httpx.AsyncClient() as client:
            while True:
                elapsed = time.time() - start_time
                if elapsed > expires_in:
                    raise DeviceFlowError("Authorization expired")

                # Polling
                data = {
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                    "client_id": self.client_id
                }
                if self.client_secret:
                    data["client_secret"] = self.client_secret

                response = await client.post(
                    self.token_endpoint,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )

                result = response.json()

                if response.status_code == 200 and "access_token" in result:
                    return TokenResponse(
                        access_token=result["access_token"],
                        refresh_token=result.get("refresh_token"),
                        token_type=result.get("token_type", "Bearer"),
                        expires_in=result.get("expires_in", 3600),
                        scope=result.get("scope")
                    )

                error = result.get("error")
                if error == "authorization_pending":
                    # 사용자가 아직 인증하지 않음 - 계속 polling
                    console.print(".", end="", style="dim")
                    await asyncio.sleep(interval)
                elif error == "slow_down":
                    # 너무 빠른 polling - 간격 증가
                    interval += 5
                    await asyncio.sleep(interval)
                elif error == "expired_token":
                    raise DeviceFlowError("Device code expired")
                elif error == "access_denied":
                    raise DeviceFlowError("User denied authorization")
                else:
                    raise DeviceFlowError(f"Token error: {error}")

    async def authenticate(self) -> TokenResponse:
        """전체 인증 플로우 실행

        Returns:
            TokenResponse: 인증 완료 후 토큰
        """
        # 1. Device code 요청
        device_code_response = await self.request_device_code()

        # 2. 사용자에게 인증 안내
        uri = device_code_response.verification_uri_complete or device_code_response.verification_uri

        console.print()
        console.print(Panel.fit(
            f"[bold cyan]브라우저에서 방문:[/bold cyan] {uri}\n"
            f"[bold yellow]코드 입력:[/bold yellow] {device_code_response.user_code}",
            title="🔐 인증 필요",
            border_style="cyan"
        ))
        console.print()
        console.print("[dim]인증 대기 중[/dim] ", end="")

        # 3. Token polling
        token = await self.poll_for_token(
            device_code=device_code_response.device_code,
            interval=device_code_response.interval,
            expires_in=device_code_response.expires_in
        )

        console.print()
        console.print("[bold green]✅ 인증 성공![/bold green]")

        return token


# OpenAI Codex 전용 설정
class OpenAIDeviceFlow(DeviceFlow):
    """OpenAI Codex CLI용 Device Flow

    ChatGPT Plus/Pro 구독자 전용.
    """

    # OpenAI OAuth 엔드포인트 (예시 - 실제 엔드포인트로 교체 필요)
    DEFAULT_DEVICE_AUTH_ENDPOINT = "https://auth.openai.com/oauth/device/code"
    DEFAULT_TOKEN_ENDPOINT = "https://auth.openai.com/oauth/token"
    DEFAULT_CLIENT_ID = "codex-cli"

    def __init__(
        self,
        client_id: str = DEFAULT_CLIENT_ID,
        device_auth_endpoint: str = DEFAULT_DEVICE_AUTH_ENDPOINT,
        token_endpoint: str = DEFAULT_TOKEN_ENDPOINT,
        scope: str = "chat models"
    ):
        super().__init__(
            client_id=client_id,
            device_auth_endpoint=device_auth_endpoint,
            token_endpoint=token_endpoint,
            scope=scope
        )
