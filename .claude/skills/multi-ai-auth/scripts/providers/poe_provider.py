"""Poe Provider

Poe API Key 기반 인증.
100+ AI 모델 통합 접근.
"""

import os
from datetime import datetime
from typing import Optional

import httpx

from .base import AuthToken, BaseProvider

# 절대 import로 변경 (상대 import 문제 해결)
import sys
from pathlib import Path
_SCRIPT_DIR = Path(__file__).parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from auth.api_key_flow import PoeAPIKeyFlow


class PoeProvider(BaseProvider):
    """Poe API Provider

    API Key 기반 인증.
    OpenAI 호환 API로 100+ 모델 접근.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("POE_API_KEY")

    @property
    def name(self) -> str:
        return "poe"

    @property
    def display_name(self) -> str:
        return "Poe"

    async def login(self, api_key: Optional[str] = None, **kwargs) -> AuthToken:
        """API Key로 로그인"""
        flow = PoeAPIKeyFlow(api_key=api_key or self.api_key)
        api_key_token = await flow.authenticate()

        return AuthToken(
            provider=self.name,
            access_token=api_key_token.api_key,
            refresh_token=None,
            expires_at=None,  # API Key는 만료 없음
            token_type="Bearer",
            scopes=["chat", "models"],
            account_info=api_key_token.account_info
        )

    async def refresh(self, token: AuthToken) -> AuthToken:
        """API Key는 갱신 불필요"""
        # 유효성만 재확인
        is_valid = await self.validate(token)
        if not is_valid:
            raise ValueError("API key is no longer valid")
        return token

    async def logout(self, token: AuthToken) -> bool:
        """API Key 로그아웃 (로컬 삭제만)"""
        return True

    async def validate(self, token: AuthToken) -> bool:
        """API Key 유효성 검증"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.poe.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {token.access_token}"},
                    timeout=10.0
                )
                return response.status_code == 200
            except httpx.RequestError:
                # 네트워크 에러 시 형식 검증만
                return token.access_token.startswith("sk-") and len(token.access_token) > 20

    async def get_account_info(self, token: AuthToken) -> Optional[dict]:
        """계정 정보 조회"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.poe.com/openai/v1/models",
                    headers={"Authorization": f"Bearer {token.access_token}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    models = response.json()
                    return {
                        "status": "active",
                        "available_models": len(models.get("data", [])),
                        "subscription": "Poe API"
                    }
            except httpx.RequestError:
                pass
        return None
