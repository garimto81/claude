"""API Key 인증 플로우

Poe, Anthropic 등 API Key 기반 인증 서비스용.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx
from rich.console import Console
from rich.prompt import Prompt

console = Console()


@dataclass
class APIKeyToken:
    """API Key 토큰"""
    api_key: str
    provider: str
    validated_at: datetime
    account_info: Optional[dict] = None


class APIKeyFlowError(Exception):
    """API Key Flow 에러"""
    pass


class APIKeyFlow:
    """API Key 인증 플로우

    Example:
        flow = APIKeyFlow(
            provider="poe",
            validation_endpoint="https://api.poe.com/v1/me"
        )
        token = await flow.authenticate()
    """

    def __init__(
        self,
        provider: str,
        validation_endpoint: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.provider = provider
        self.validation_endpoint = validation_endpoint
        self.api_key = api_key

    async def validate_api_key(self, api_key: str) -> dict:
        """API Key 유효성 검증

        Args:
            api_key: 검증할 API Key

        Returns:
            dict: 계정 정보 (있는 경우)
        """
        if not self.validation_endpoint:
            # 검증 엔드포인트 없으면 형식만 확인
            if not api_key or len(api_key) < 10:
                raise APIKeyFlowError("Invalid API key format")
            return {}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.validation_endpoint,
                headers={"Authorization": f"Bearer {api_key}"}
            )

            if response.status_code == 401:
                raise APIKeyFlowError("Invalid API key")
            elif response.status_code != 200:
                raise APIKeyFlowError(f"Validation failed: {response.status_code}")

            return response.json()

    async def authenticate(self, api_key: Optional[str] = None) -> APIKeyToken:
        """인증 수행

        Args:
            api_key: API Key (없으면 프롬프트로 입력)

        Returns:
            APIKeyToken: 검증된 토큰
        """
        # API Key 획득
        key = api_key or self.api_key
        if not key:
            console.print(f"\n[bold cyan]{self.provider} API Key를 입력하세요:[/bold cyan]")
            key = Prompt.ask("API Key", password=True)

        if not key:
            raise APIKeyFlowError("API key is required")

        # 검증
        console.print(f"[dim]{self.provider} API Key 검증 중...[/dim]")
        account_info = await self.validate_api_key(key)

        console.print(f"[bold green]✅ {self.provider} 인증 성공![/bold green]")

        return APIKeyToken(
            api_key=key,
            provider=self.provider,
            validated_at=datetime.now(),
            account_info=account_info
        )


# Poe API 전용 설정
class PoeAPIKeyFlow(APIKeyFlow):
    """Poe API Key 인증"""

    DEFAULT_VALIDATION_ENDPOINT = "https://api.poe.com/bot/me"

    def __init__(
        self,
        api_key: Optional[str] = None,
        validation_endpoint: str = DEFAULT_VALIDATION_ENDPOINT
    ):
        super().__init__(
            provider="poe",
            validation_endpoint=validation_endpoint,
            api_key=api_key
        )

    async def validate_api_key(self, api_key: str) -> dict:
        """Poe API Key 검증"""
        async with httpx.AsyncClient() as client:
            # Poe는 OpenAI 호환 API 사용
            response = await client.get(
                "https://api.poe.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )

            if response.status_code == 401:
                raise APIKeyFlowError("Invalid Poe API key")
            elif response.status_code != 200:
                # 키 형식 검증만 수행
                if not api_key.startswith("sk-") or len(api_key) < 20:
                    raise APIKeyFlowError("Invalid Poe API key format")
                return {"status": "format_valid"}

            return response.json()


# Anthropic API 전용 설정
class AnthropicAPIKeyFlow(APIKeyFlow):
    """Anthropic API Key 인증"""

    def __init__(
        self,
        api_key: Optional[str] = None
    ):
        super().__init__(
            provider="anthropic",
            validation_endpoint=None,  # Anthropic은 별도 검증 엔드포인트 없음
            api_key=api_key
        )

    async def validate_api_key(self, api_key: str) -> dict:
        """Anthropic API Key 형식 검증"""
        if not api_key.startswith("sk-ant-"):
            raise APIKeyFlowError("Invalid Anthropic API key format (should start with 'sk-ant-')")
        if len(api_key) < 50:
            raise APIKeyFlowError("Invalid Anthropic API key length")
        return {"status": "format_valid"}
