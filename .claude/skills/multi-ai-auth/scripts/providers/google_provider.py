"""Google Provider

Gemini API용 OAuth 2.0 + PKCE 인증.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import httpx

from .base import AuthToken, BaseProvider
from ..auth.pkce_flow import GooglePKCEFlow


class GoogleProvider(BaseProvider):
    """Google Gemini API용 Provider

    OAuth 2.0 Authorization Code + PKCE 사용.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None
    ):
        self.client_id = client_id or os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("GOOGLE_CLIENT_SECRET")

    @property
    def name(self) -> str:
        return "google"

    @property
    def display_name(self) -> str:
        return "Google Gemini"

    async def login(self, **kwargs) -> AuthToken:
        """PKCE Flow로 로그인"""
        if not self.client_id:
            raise ValueError(
                "Google Client ID가 필요합니다.\n"
                "1. Google Cloud Console에서 OAuth 클라이언트 생성\n"
                "2. GOOGLE_CLIENT_ID 환경변수 설정"
            )

        flow = GooglePKCEFlow(
            client_id=self.client_id,
            client_secret=self.client_secret
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
                GooglePKCEFlow.DEFAULT_TOKEN_ENDPOINT,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": token.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
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
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/revoke",
                data={"token": token.access_token}
            )
            return response.status_code == 200

    async def validate(self, token: AuthToken) -> bool:
        """토큰 유효성 검증"""
        if token.is_expired():
            return False

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/tokeninfo",
                params={"access_token": token.access_token}
            )
            return response.status_code == 200

    async def get_account_info(self, token: AuthToken) -> Optional[dict]:
        """계정 정보 조회"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token.access_token}"}
            )
            if response.status_code == 200:
                return response.json()
        return None
