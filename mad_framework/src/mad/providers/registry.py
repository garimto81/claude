"""Provider registry for managing LLM providers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from mad.core.config import MADConfig
from mad.providers.anthropic import AnthropicProvider
from mad.providers.openai import OpenAIProvider

if TYPE_CHECKING:
    from mad.providers.base import LLMProvider

ProviderType = Literal["anthropic", "openai", "google"]


class ProviderRegistry:
    """Registry for managing and instantiating LLM providers."""

    _providers: dict[str, type[LLMProvider]] = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
    }

    _instances: dict[str, LLMProvider] = {}

    @classmethod
    def register(cls, name: str, provider_class: type[LLMProvider]) -> None:
        """Register a new provider class."""
        cls._providers[name] = provider_class

    @classmethod
    def get(
        cls,
        name: ProviderType,
        api_key: str | None = None,
        config: MADConfig | None = None,
    ) -> LLMProvider:
        """Get or create a provider instance.

        Args:
            name: Provider name ('anthropic', 'openai', 'google').
            api_key: Optional API key (overrides config/env).
            config: Optional MADConfig for API keys.

        Returns:
            LLMProvider instance.

        Raises:
            ValueError: If provider not found.
        """
        if name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            msg = f"Unknown provider '{name}'. Available: {available}"
            raise ValueError(msg)

        # Resolve API key
        if api_key is None and config is not None:
            key_map = {
                "anthropic": config.anthropic_api_key,
                "openai": config.openai_api_key,
                "google": config.google_api_key,
            }
            api_key = key_map.get(name)

        # Create cache key
        cache_key = f"{name}:{api_key or 'default'}"

        if cache_key not in cls._instances:
            provider_class = cls._providers[name]
            cls._instances[cache_key] = provider_class(api_key=api_key)

        return cls._instances[cache_key]

    @classmethod
    def available_providers(cls) -> list[str]:
        """List all registered provider names."""
        return list(cls._providers.keys())

    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached provider instances."""
        cls._instances.clear()


def get_provider(
    name: ProviderType,
    api_key: str | None = None,
    config: MADConfig | None = None,
) -> LLMProvider:
    """Convenience function to get a provider from the registry.

    Args:
        name: Provider name ('anthropic', 'openai', 'google').
        api_key: Optional API key.
        config: Optional MADConfig.

    Returns:
        LLMProvider instance.
    """
    return ProviderRegistry.get(name, api_key, config)
