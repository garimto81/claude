"""Provider Router

Provider 선택 및 병렬 검증 관리.
"""

import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

# 부모 디렉토리를 sys.path에 추가
_PARENT_DIR = Path(__file__).parent.parent
if str(_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_DIR))

from providers.adapters.openai_adapter import OpenAIAdapter, OpenAIResponse
from providers.adapters.gemini_adapter import GeminiAdapter, GeminiResponse


def _get_multi_ai_auth_path() -> Path | None:
    """Multi-AI Auth 경로 탐색.

    Returns:
        경로가 존재하면 Path, 없으면 None
    """
    # 절대 경로로 안정적인 import
    skill_root = Path(__file__).parent.parent.parent  # .claude/skills/cross-ai-verifier
    auth_path = skill_root.parent / "multi-ai-auth"  # .claude/skills/multi-ai-auth

    if auth_path.exists():
        return auth_path
    return None


# multi-ai-auth TokenStore import
HAS_TOKEN_STORE = False
TokenStore = None

auth_path = _get_multi_ai_auth_path()
if auth_path:
    try:
        # sys.path에 중복 추가 방지
        auth_path_str = str(auth_path)
        if auth_path_str not in sys.path:
            sys.path.insert(0, auth_path_str)

        # 패키지 레벨에서 import
        from scripts.storage.token_store import TokenStore
        HAS_TOKEN_STORE = True
    except ImportError as e:
        # import 실패 시 디버깅 정보 (Warning 메시지 제거)
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
        # 기본 모드 (OAuth 우선, 환경변수 fallback)
        router = ProviderRouter()
        result = await router.verify(code, "openai", prompt)

        # 인증 강제 모드 (OAuth 토큰 필수)
        router = ProviderRouter(require_auth=True)
        await router.ensure_authenticated("openai")  # 토큰 없으면 에러
        result = await router.verify(code, "openai", prompt)
    """

    SUPPORTED_PROVIDERS = ["openai", "gemini"]

    def __init__(self, require_auth: bool = False):
        """초기화.

        Args:
            require_auth: True면 OAuth 토큰 필수 (API 키 허용 안함)
        """
        self._token_store = None
        self._require_auth = require_auth

        if HAS_TOKEN_STORE:
            self._token_store = TokenStore()
        elif require_auth:
            # TokenStore 없으면 인증 강제 모드 사용 불가
            raise RuntimeError(
                "require_auth=True requires multi-ai-auth skill.\n"
                "Install multi-ai-auth skill first."
            )

    async def ensure_authenticated(self, provider: str) -> None:
        """인증 확인 및 안내.

        Args:
            provider: Provider 이름

        Raises:
            RuntimeError: 토큰이 없거나 만료된 경우
        """
        if not self._require_auth:
            # 인증 강제 모드가 아니면 체크하지 않음
            return

        token = await self._get_token(provider)
        if not token:
            # 로그인 안내 메시지
            raise RuntimeError(
                f"❌ {provider.upper()} 인증이 필요합니다.\n"
                f"   다음 명령어로 로그인하세요:\n"
                f"   /ai-auth login --provider {provider}"
            )

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
            # 인증 강제 모드면 토큰 확인
            if self._require_auth:
                await self.ensure_authenticated(provider)

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
