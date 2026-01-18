"""Token Storage

OAuth 토큰의 안전한 저장 및 관리.
Claude Code와 동일한 방식으로 로컬에 토큰 저장.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# AuthToken을 로컬에서 정의 (순환 import 방지)
@dataclass
class AuthToken:
    """인증 토큰 데이터 클래스 (로컬 정의)"""
    provider: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    token_type: str = "Bearer"
    scopes: list[str] = field(default_factory=list)
    account_info: Optional[dict] = None

    def is_expired(self) -> bool:
        """토큰 만료 여부 확인"""
        if self.expires_at is None:
            return False
        return datetime.now() >= self.expires_at

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (저장용)"""
        return {
            "provider": self.provider,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "token_type": self.token_type,
            "scopes": self.scopes,
            "account_info": self.account_info
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuthToken":
        """딕셔너리에서 생성"""
        expires_at = None
        if data.get("expires_at"):
            expires_at = datetime.fromisoformat(data["expires_at"])
        return cls(
            provider=data["provider"],
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at,
            token_type=data.get("token_type", "Bearer"),
            scopes=data.get("scopes", []),
            account_info=data.get("account_info")
        )


class TokenStorage:
    """토큰 저장소.

    토큰을 로컬 파일에 안전하게 저장합니다.
    저장 위치: ~/.claude/ai-tokens.json

    Example:
        storage = TokenStorage()
        storage.save(token)
        token = storage.load("openai")
    """

    DEFAULT_PATH = Path.home() / ".claude" / "ai-tokens.json"

    def __init__(self, storage_path: Optional[Path] = None):
        """초기화.

        Args:
            storage_path: 토큰 저장 경로 (기본값: ~/.claude/ai-tokens.json)
        """
        self.storage_path = storage_path or self.DEFAULT_PATH
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """저장 디렉토리 생성."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_all(self) -> dict:
        """모든 토큰 데이터 로드."""
        if not self.storage_path.exists():
            return {}

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_all(self, data: dict) -> None:
        """모든 토큰 데이터 저장."""
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # 파일 권한 제한 (Unix 계열에서만)
        if os.name != "nt":
            os.chmod(self.storage_path, 0o600)

    def save(self, token: AuthToken) -> None:
        """토큰 저장.

        Args:
            token: 저장할 토큰
        """
        data = self._load_all()
        data[token.provider] = token.to_dict()
        self._save_all(data)

    def load(self, provider: str) -> Optional[AuthToken]:
        """토큰 로드.

        Args:
            provider: Provider 이름 (openai, google 등)

        Returns:
            AuthToken: 저장된 토큰 또는 None
        """
        data = self._load_all()
        token_data = data.get(provider)

        if not token_data:
            return None

        return AuthToken.from_dict(token_data)

    def delete(self, provider: str) -> bool:
        """토큰 삭제.

        Args:
            provider: Provider 이름

        Returns:
            bool: 삭제 성공 여부
        """
        data = self._load_all()
        if provider in data:
            del data[provider]
            self._save_all(data)
            return True
        return False

    def list_all(self) -> list[str]:
        """저장된 모든 Provider 목록 반환.

        Returns:
            list[str]: Provider 이름 목록
        """
        data = self._load_all()
        return list(data.keys())

    def clear_all(self) -> None:
        """모든 토큰 삭제."""
        self._save_all({})

    def get_valid_token(self, provider: str) -> Optional[AuthToken]:
        """유효한 토큰만 반환.

        만료된 토큰은 None 반환.

        Args:
            provider: Provider 이름

        Returns:
            AuthToken: 유효한 토큰 또는 None
        """
        token = self.load(provider)
        if token and not token.is_expired():
            return token
        return None

    def has_valid_token(self, provider: str) -> bool:
        """유효한 토큰 존재 여부.

        Args:
            provider: Provider 이름

        Returns:
            bool: 유효한 토큰 존재 여부
        """
        return self.get_valid_token(provider) is not None
