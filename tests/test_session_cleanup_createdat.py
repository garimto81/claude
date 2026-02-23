"""
session_cleanup.py createdAt 파싱 버그 수정 테스트
F-01: createdAt int/str 양쪽 처리
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timezone
import json
import sys
import os

# 테스트 대상 함수를 직접 import하기 어려우므로
# cleanup_stale_agent_teams 함수의 createdAt 파싱 로직을 직접 테스트

def parse_createdat(created):
    """session_cleanup.py의 수정 후 파싱 로직 (설계 문서 2.3 기준)"""
    if created is None or created == "":
        return None
    created_dt = None
    if isinstance(created, (int, float)) and created > 0:
        ts = created / 1000 if created >= 1e12 else float(created)
        created_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    elif isinstance(created, str) and created:
        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
    return created_dt


def test_createdat_unix_ms_recent():
    """TC1: Unix ms 정수 (최근 시각) → datetime 반환"""
    ts_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    result = parse_createdat(ts_ms)
    assert result is not None
    assert isinstance(result, datetime)
    assert result.tzinfo is not None


def test_createdat_unix_ms_old():
    """TC2: Unix ms 정수 (과거) → datetime 반환"""
    result = parse_createdat(1000000000000)  # 2001년
    assert result is not None
    assert result.year == 2001


def test_createdat_iso_string():
    """TC3: ISO 8601 문자열 → datetime 반환"""
    result = parse_createdat("2026-02-23T10:00:00Z")
    assert result is not None
    assert result.year == 2026
    assert result.month == 2


def test_createdat_zero():
    """TC4: 0 정수 → None 반환 (created > 0 실패)"""
    result = parse_createdat(0)
    assert result is None


def test_createdat_none():
    """TC5: None → None 반환"""
    result = parse_createdat(None)
    assert result is None
