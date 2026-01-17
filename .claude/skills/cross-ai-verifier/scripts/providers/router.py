"""Provider Router

Provider 선택 및 병렬 검증 관리.
"""

import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .adapters.openai_adapter import OpenAIAdapter, OpenAIResponse
from .adapters.gemini_adapter import GeminiAdapter, GeminiResponse

# multi-ai-auth TokenStore import 시도
try:
    multi_ai_auth_path = Path(__file__).parent.parent.parent.parent / "multi-ai-auth" / "scripts"
    if multi_ai_auth_path.exists():
        sys.path.insert(0, str(multi_ai_auth_path))
        from storage.token_store import TokenStore
        HAS_TOKEN_STORE = True
except ImportError:
    HAS_TOKEN_STORE = False
    TokenStore = None


ProviderType = Literal["openai", "gemini"]


@dataclass
class VerifyResult:
    """검증 결과."""
    provider: str
    issues: list[dict] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    confidence: float = 0.0
    raw_response: str = ""
    error: str | None = None


class ProviderRouter:
    """Provider 라우터.

    다중 AI Provider 관리 및 병렬 검증 지원.

    Example:
        router = ProviderRouter()
        result = await router.verify(code, "openai", prompt)
        results = await router.verify_parallel(code, ["openai", "gemini"], prompt)
    """

    SUPPORTED_PROVIDERS = ["openai", "gemini"]

    def __init__(self):
        """초기화."""
        self._token_store = None
        if HAS_TOKEN_STORE:
            self._token_store = TokenStore()

    async def _get_token(self, provider: str) -> str | None:
        """토큰 조회.

        Args:
            provider: Provider 이름

        Returns:
            토큰 문자열 또는 None
        """
        if self._token_store:
            token = await self._token_store.load(provider)
            if token and not token.is_expired():
                return token.access_token
        return None

    def _get_adapter(self, provider: str, token: str | None = None):
        """어댑터 생성.

        Args:
            provider: Provider 이름
            token: API 토큰 (없으면 환경변수 사용)

        Returns:
            해당 Provider의 어댑터

        Raises:
            ValueError: 지원하지 않는 Provider
        """
        if provider == "openai":
            return OpenAIAdapter(token=token)
        elif provider == "gemini":
            return GeminiAdapter(token=token)
        else:
            raise ValueError(f"지원하지 않는 Provider: {provider}")

    async def verify(
        self,
        code: str,
        provider: ProviderType,
        prompt: str,
        language: str = "python"
    ) -> VerifyResult:
        """단일 Provider 검증.

        Args:
            code: 검증할 코드
            provider: 사용할 Provider
            prompt: 검증 프롬프트
            language: 프로그래밍 언어

        Returns:
            VerifyResult: 검증 결과
        """
        try:
            # 토큰 조회 (TokenStore 우선, 없으면 환경변수)
            token = await self._get_token(provider)
            adapter = self._get_adapter(provider, token)

            response = await adapter.verify_code(code, language, prompt)

            return VerifyResult(
                provider=provider,
                issues=response.issues,
                suggestions=response.suggestions,
                confidence=response.confidence,
                raw_response=response.raw_response
            )

        except Exception as e:
            return VerifyResult(
                provider=provider,
                error=str(e)
            )

    async def verify_parallel(
        self,
        code: str,
        prompt: str,
        providers: list[ProviderType] | None = None,
        language: str = "python"
    ) -> list[VerifyResult]:
        """다중 Provider 병렬 검증.

        Args:
            code: 검증할 코드
            prompt: 검증 프롬프트
            providers: 사용할 Provider 목록 (기본: 모두)
            language: 프로그래밍 언어

        Returns:
            list[VerifyResult]: 각 Provider의 검증 결과
        """
        providers = providers or self.SUPPORTED_PROVIDERS

        tasks = [
            self.verify(code, provider, prompt, language)
            for provider in providers
        ]

        return await asyncio.gather(*tasks)

    def aggregate_results(self, results: list[VerifyResult]) -> dict[str, Any]:
        """결과 집계.

        Args:
            results: 검증 결과 목록

        Returns:
            dict: 집계된 결과
        """
        all_issues = []
        all_suggestions = []
        confidences = []
        errors = []

        for result in results:
            if result.error:
                errors.append({"provider": result.provider, "error": result.error})
            else:
                all_issues.extend([
                    {**issue, "source": result.provider}
                    for issue in result.issues
                ])
                all_suggestions.extend(result.suggestions)
                confidences.append(result.confidence)

        # 중복 제거 (같은 라인, 비슷한 메시지)
        unique_issues = self._deduplicate_issues(all_issues)

        return {
            "issues": unique_issues,
            "suggestions": list(set(all_suggestions)),
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
            "providers_used": [r.provider for r in results if not r.error],
            "errors": errors
        }

    def _deduplicate_issues(self, issues: list[dict]) -> list[dict]:
        """이슈 중복 제거.

        같은 라인에서 발견된 비슷한 이슈는 병합.

        Args:
            issues: 이슈 목록

        Returns:
            list[dict]: 중복 제거된 이슈
        """
        seen = {}
        for issue in issues:
            key = (issue.get("line", 0), issue.get("severity", ""))
            if key not in seen:
                seen[key] = issue
            else:
                # 같은 라인/심각도면 source 병합
                existing = seen[key]
                existing_sources = existing.get("source", "")
                new_source = issue.get("source", "")
                if new_source and new_source not in existing_sources:
                    existing["source"] = f"{existing_sources}, {new_source}"

        return list(seen.values())
