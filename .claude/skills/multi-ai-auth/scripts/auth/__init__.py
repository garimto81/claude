"""Authentication Flows

OAuth 2.0 인증 플로우 구현:
- Browser OAuth 2.0 + PKCE (Claude /login 방식)
- Authorization Code + PKCE
- Device Authorization Grant (RFC 8628) - deprecated
- API Key - deprecated
"""

from .browser_oauth import BrowserOAuth, OAuthConfig, OAuthCallbackError
from .pkce_flow import PKCEFlow, GooglePKCEFlow
from .token_storage import TokenStorage

# Deprecated - Device Flow는 OpenAI에서 차단됨
from .device_flow import DeviceFlow
from .api_key_flow import APIKeyFlow

__all__ = [
    # Browser OAuth (권장)
    "BrowserOAuth",
    "OAuthConfig",
    "OAuthCallbackError",
    # PKCE Flow
    "PKCEFlow",
    "GooglePKCEFlow",
    # Token Storage
    "TokenStorage",
    # Deprecated
    "DeviceFlow",
    "APIKeyFlow",
]
