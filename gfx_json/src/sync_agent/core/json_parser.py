"""JSON 파싱 모듈.

PokerGFX JSON 파일 파싱 및 file_hash 생성.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """파싱 오류."""

    def __init__(self, message: str, file_path: str | None = None):
        super().__init__(message)
        self.file_path = file_path


@dataclass
class ParseResult:
    """파싱 결과."""

    success: bool
    record: dict[str, Any] | None = None
    error: str | None = None
    file_path: str | None = None


@dataclass
class JsonParser:
    """PokerGFX JSON 파서.

    기능:
    - JSON 파일 파싱
    - file_hash 생성 (SHA-256)
    - 메타데이터 추출 (session_id, table_type 등)
    - gfx_pc_id 추가

    Examples:
        ```python
        parser = JsonParser()

        result = parser.parse("/path/to/file.json", gfx_pc_id="PC01")
        if result.success:
            record = result.record
            # {'gfx_pc_id': 'PC01', 'file_hash': 'abc...', 'session_id': 1, ...}
        ```
    """

    encoding: str = "utf-8"
    hash_algorithm: str = "sha256"

    def parse(self, file_path: str, gfx_pc_id: str) -> ParseResult:
        """JSON 파일 파싱.

        Args:
            file_path: JSON 파일 경로
            gfx_pc_id: GFX PC 식별자

        Returns:
            ParseResult
        """
        path = Path(file_path)

        # 파일 존재 확인
        if not path.exists():
            return ParseResult(
                success=False,
                error="file_not_found",
                file_path=file_path,
            )

        try:
            # 파일 읽기
            content = path.read_text(encoding=self.encoding)

            # JSON 파싱
            data = json.loads(content)

            # file_hash 생성
            file_hash = self._generate_hash(content)

            # 레코드 생성
            record = self._build_record(data, path, gfx_pc_id, file_hash)

            return ParseResult(
                success=True,
                record=record,
                file_path=file_path,
            )

        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 오류 ({file_path}): {e}")
            return ParseResult(
                success=False,
                error="json_decode_error",
                file_path=file_path,
            )

        except UnicodeDecodeError as e:
            logger.warning(f"인코딩 오류 ({file_path}): {e}")
            return ParseResult(
                success=False,
                error="encoding_error",
                file_path=file_path,
            )

        except Exception as e:
            logger.error(f"파싱 오류 ({file_path}): {e}")
            return ParseResult(
                success=False,
                error=str(e),
                file_path=file_path,
            )

    def parse_content(self, content: str, file_name: str, gfx_pc_id: str) -> ParseResult:
        """문자열 내용 파싱.

        Args:
            content: JSON 문자열
            file_name: 파일명 (메타데이터용)
            gfx_pc_id: GFX PC 식별자

        Returns:
            ParseResult
        """
        try:
            data = json.loads(content)
            file_hash = self._generate_hash(content)

            record = {
                "gfx_pc_id": gfx_pc_id,
                "file_hash": file_hash,
                "file_name": file_name,
                "session_id": self._extract_session_id(data),
                "table_type": data.get("table_type"),
                "event_title": data.get("event_title"),
                "software_version": data.get("software_version"),
                "hand_count": self._count_hands(data),
                "session_created_at": self._extract_created_at(data),
                "raw_json": data,
                "sync_source": "nas_central",
            }

            return ParseResult(success=True, record=record)

        except json.JSONDecodeError:
            return ParseResult(success=False, error="json_decode_error")

    def _generate_hash(self, content: str) -> str:
        """파일 내용 기반 해시 생성.

        Args:
            content: 파일 내용

        Returns:
            SHA-256 해시 (hex)
        """
        if self.hash_algorithm == "sha256":
            return hashlib.sha256(content.encode()).hexdigest()
        elif self.hash_algorithm == "md5":
            return hashlib.md5(content.encode()).hexdigest()
        else:
            return hashlib.sha256(content.encode()).hexdigest()

    def _build_record(
        self,
        data: dict[str, Any],
        path: Path,
        gfx_pc_id: str,
        file_hash: str,
    ) -> dict[str, Any]:
        """Supabase 레코드 생성.

        Args:
            data: 파싱된 JSON 데이터
            path: 파일 경로
            gfx_pc_id: GFX PC 식별자
            file_hash: 파일 해시

        Returns:
            Supabase 레코드
        """
        return {
            "gfx_pc_id": gfx_pc_id,
            "file_hash": file_hash,
            "file_name": path.name,
            "session_id": self._extract_session_id(data),
            "table_type": data.get("table_type"),
            "event_title": data.get("event_title"),
            "software_version": data.get("software_version"),
            "hand_count": self._count_hands(data),
            "session_created_at": self._extract_created_at(data),
            "raw_json": data,
            "sync_source": "nas_central",
        }

    def _extract_session_id(self, data: dict[str, Any]) -> int | None:
        """session_id 추출.

        다양한 형식 지원:
        - {"session_id": 123}
        - {"session": {"id": 123}}
        - {"id": 123}
        """
        if "session_id" in data:
            return int(data["session_id"])

        if "session" in data and isinstance(data["session"], dict):
            if "id" in data["session"]:
                return int(data["session"]["id"])

        if "id" in data:
            return int(data["id"])

        return None

    def _extract_created_at(self, data: dict[str, Any]) -> str | None:
        """생성 시간 추출.

        다양한 형식 지원:
        - {"created_at": "2024-01-01T00:00:00Z"}
        - {"session_created_at": "..."}
        - {"timestamp": "..."}
        """
        for key in ["created_at", "session_created_at", "timestamp", "createdAt"]:
            if key in data and data[key]:
                return str(data[key])

        return None

    def _count_hands(self, data: dict[str, Any]) -> int:
        """핸드 수 계산.

        다양한 형식 지원:
        - {"hands": [...]}
        - {"hand_count": 10}
        - {"handCount": 10}
        """
        if "hands" in data and isinstance(data["hands"], list):
            return len(data["hands"])

        if "hand_count" in data:
            return int(data["hand_count"])

        if "handCount" in data:
            return int(data["handCount"])

        return 0

    @staticmethod
    def validate_json_structure(data: dict[str, Any]) -> list[str]:
        """JSON 구조 검증.

        Args:
            data: JSON 데이터

        Returns:
            오류 메시지 리스트 (빈 리스트면 유효)
        """
        errors = []

        # 필수 필드 확인 (유연한 검증)
        if not any(k in data for k in ["session_id", "session", "id"]):
            errors.append("session_id가 없습니다")

        return errors
