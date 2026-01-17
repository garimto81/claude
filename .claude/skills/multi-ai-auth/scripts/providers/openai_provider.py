"""OpenAI Provider

ChatGPT Plus/Pro 구독자용 Device Authorization Grant 인증.
"""

from datetime import datetime, timedelta
from typing import Optional

import httpx

from .base import AuthToken, BaseProvider
from ..auth.device_flow import OpenAIDeviceFlow


class OpenAIProvider(BaseProvider):
    """OpenAI Codex CLI용 Provider

    ChatGPT Plus/Pro 구독자 전용.
    Device Authorization Grant (RFC 8628) 사용.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ):
        self.client_id = client_id or "codex-cli"
        self.client_secret = client_secret

    @property
    def name(self) -> str:
        return "openai"

    @property
    def display_name(self) -> str:
        return "OpenAI"

    async def login(self, **kwargs) -> AuthToken:
        """Device Flow로 로그인"""
        flow = OpenAIDeviceFlow(
            client_id=self.client_id
        )
        token_response = await flow.authenticate()

        # 만료 시간 계산
        expires_at = datetime.now() + timedelta(seconds=token_response.expires_in)

        return AuthToken(
            provider=self.name,
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token,
            expires_at=expires_at,
            token_type=token_response.token_type,
            scopes=token_response.scope.split() if token_response.scope else []
        )

    async def refresh(self, token: AuthToken) -> AuthToken:
        """Refresh token으로 갱신"""
        if not token.refresh_token:
            raise ValueError("No refresh token available")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                OpenAIDeviceFlow.DEFAULT_TOKEN_ENDPOINT,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": token.refresh_token,
                    "client_id": self.client_id
                }
            )

            if response.status_code != 200:
                raise ValueError(f"Token refresh failed: {response.text}")

            data = response.json()
            expires_at = datetime.now() + timedelta(seconds=data.get("expires_in", 3600))

            return AuthToken(
                provider=self.name,
                access_token=data["access_token"],
                refresh_token=data.get("refresh_token", token.refresh_token),
                expires_at=expires_at,
                token_type=data.get("token_type", "Bearer"),
                scopes=data.get("scope", "").split() if data.get("scope") else token.scopes
            )

    async def logout(self, token: AuthToken) -> bool:
        """토큰 폐기"""
        # OpenAI는 토큰 폐기 엔드포인트가 없을 수 있음
        # 로컬에서만 삭제
        return True

    async def validate(self, token: AuthToken) -> bool:
        """토큰 유효성 검증"""
        if token.is_expired():
            return False

        # API 호출로 검증
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {token.access_token}"}
            )
            return response.status_code == 200

    async def get_account_info(self, token: AuthToken) -> Optional[dict]:
        """계정 정보 조회"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openai.com/v1/me",
                headers={"Authorization": f"Bearer {token.access_token}"}
            )
            if response.status_code == 200:
                return response.json()
        return None
