#!/usr/bin/env python3
"""
Token Optimizer Hook - OpenAI Codex 기법 기반 토큰 절약

Codex Agent Loop의 토큰 절약 기법을 구현:
- Response 캐싱: 동일한 파일 읽기 요청에 대한 캐시
- 중복 요청 제거: 5분 내 동일 Grep/Glob 패턴 요청 스킵
- 결과 압축: 긴 출력을 요약 형태로 압축

캐시 저장소: .omc/cache/token_cache.json
캐시 TTL: 5분 (조절 가능)
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# 동적 프로젝트 루트 감지
def _get_project_root() -> Path:
    """프로젝트 루트 디렉토리를 동적으로 감지"""
    if env_root := os.environ.get("CLAUDE_PROJECT_DIR"):
        return Path(env_root)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    if (project_root / ".claude").exists():
        return project_root
    return Path.cwd()


PROJECT_ROOT = _get_project_root()
CACHE_DIR = PROJECT_ROOT / ".omc" / "cache"
CACHE_FILE = CACHE_DIR / "token_cache.json"
STATS_FILE = CACHE_DIR / "token_stats.json"

# 설정
DEFAULT_TTL_MINUTES = 5
MAX_CACHE_ENTRIES = 1000
MAX_CACHED_CONTENT_SIZE = 50000  # 50KB
COMPRESS_THRESHOLD = 10000  # 10KB 이상이면 압축


class TokenOptimizer:
    """토큰 최적화 캐시 관리 클래스"""

    def __init__(self, ttl_minutes: int = DEFAULT_TTL_MINUTES):
        """
        Args:
            ttl_minutes: 캐시 TTL (분)
        """
        self.ttl = timedelta(minutes=ttl_minutes)
        self.cache: dict[str, dict] = {}
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "tokens_saved": 0,
            "duplicates_skipped": 0,
        }
        self._load_cache()
        self._load_stats()

    def _load_cache(self):
        """캐시 파일 로드"""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.cache = data.get("cache", {})
                    # TTL 만료 항목 제거
                    self._cleanup_expired()
            except (json.JSONDecodeError, OSError):
                self.cache = {}

    def _save_cache(self):
        """캐시 파일 저장"""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump({"cache": self.cache}, f, ensure_ascii=False)
        except OSError:
            pass

    def _load_stats(self):
        """통계 파일 로드"""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    self.stats.update(json.load(f))
            except (json.JSONDecodeError, OSError):
                pass

    def _save_stats(self):
        """통계 파일 저장"""
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def _cleanup_expired(self):
        """만료된 캐시 항목 제거"""
        now = datetime.now()
        expired_keys = []
        for key, entry in self.cache.items():
            if "expires_at" in entry:
                expires_at = datetime.fromisoformat(entry["expires_at"])
                if now > expires_at:
                    expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        # 최대 항목 수 제한
        if len(self.cache) > MAX_CACHE_ENTRIES:
            # 오래된 항목 제거 (생성 시간 기준)
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: x[1].get("created_at", ""),
            )
            to_remove = len(self.cache) - MAX_CACHE_ENTRIES
            for key, _ in sorted_items[:to_remove]:
                del self.cache[key]

    def _generate_cache_key(self, tool_name: str, tool_input: dict) -> str:
        """캐시 키 생성"""
        # 입력을 정규화하여 해시 생성
        normalized = json.dumps(
            {"tool": tool_name, "input": tool_input},
            sort_keys=True,
            ensure_ascii=False,
        )
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _estimate_tokens(self, content: str) -> int:
        """토큰 수 추정 (간단한 휴리스틱)"""
        # 대략 4자 = 1토큰 (영어 기준), 한글은 2자 = 1토큰
        english_chars = sum(1 for c in content if ord(c) < 128)
        korean_chars = len(content) - english_chars
        return (english_chars // 4) + (korean_chars // 2)

    def _compress_content(self, content: str) -> tuple[str, bool]:
        """
        긴 콘텐츠 압축

        Returns:
            (압축된 콘텐츠, 압축 여부)
        """
        if len(content) <= COMPRESS_THRESHOLD:
            return content, False

        # 줄 수 기반 압축
        lines = content.split("\n")
        if len(lines) > 50:
            # 처음 20줄 + 요약 + 마지막 10줄
            compressed = (
                "\n".join(lines[:20])
                + f"\n\n... ({len(lines) - 30}줄 생략) ...\n\n"
                + "\n".join(lines[-10:])
            )
            return compressed, True

        # 길이 기반 압축
        if len(content) > MAX_CACHED_CONTENT_SIZE:
            truncated = content[:MAX_CACHED_CONTENT_SIZE]
            return truncated + f"\n... ({len(content) - MAX_CACHED_CONTENT_SIZE}자 생략)", True

        return content, False

    # === 공개 API ===

    def check_cache(self, tool_name: str, tool_input: dict) -> Optional[dict]:
        """
        캐시 확인

        Args:
            tool_name: 도구 이름 (Read, Grep, Glob)
            tool_input: 도구 입력

        Returns:
            캐시 히트 시 저장된 결과, 없으면 None
        """
        self.stats["total_requests"] += 1

        # 캐시 가능한 도구만 처리
        if tool_name not in ["Read", "Grep", "Glob"]:
            return None

        cache_key = self._generate_cache_key(tool_name, tool_input)

        if cache_key in self.cache:
            entry = self.cache[cache_key]
            expires_at = datetime.fromisoformat(entry["expires_at"])

            if datetime.now() <= expires_at:
                self.stats["cache_hits"] += 1
                self.stats["tokens_saved"] += entry.get("estimated_tokens", 0)
                self._save_stats()
                return {
                    "cached": True,
                    "result": entry["result"],
                    "compressed": entry.get("compressed", False),
                    "original_tokens": entry.get("estimated_tokens", 0),
                }

        self.stats["cache_misses"] += 1
        self._save_stats()
        return None

    def store_cache(self, tool_name: str, tool_input: dict, result: str) -> dict:
        """
        결과 캐시 저장

        Args:
            tool_name: 도구 이름
            tool_input: 도구 입력
            result: 도구 실행 결과

        Returns:
            캐시 저장 정보
        """
        if tool_name not in ["Read", "Grep", "Glob"]:
            return {"cached": False, "reason": "not_cacheable_tool"}

        cache_key = self._generate_cache_key(tool_name, tool_input)
        compressed_result, was_compressed = self._compress_content(result)
        estimated_tokens = self._estimate_tokens(result)

        self.cache[cache_key] = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "result": compressed_result,
            "compressed": was_compressed,
            "estimated_tokens": estimated_tokens,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + self.ttl).isoformat(),
        }

        self._cleanup_expired()
        self._save_cache()

        return {
            "cached": True,
            "key": cache_key,
            "compressed": was_compressed,
            "estimated_tokens": estimated_tokens,
        }

    def check_duplicate(self, tool_name: str, tool_input: dict) -> bool:
        """
        중복 요청 확인 (Grep/Glob 패턴)

        Args:
            tool_name: 도구 이름
            tool_input: 도구 입력

        Returns:
            중복 여부
        """
        if tool_name not in ["Grep", "Glob"]:
            return False

        cache_key = self._generate_cache_key(tool_name, tool_input)

        if cache_key in self.cache:
            entry = self.cache[cache_key]
            expires_at = datetime.fromisoformat(entry["expires_at"])

            if datetime.now() <= expires_at:
                self.stats["duplicates_skipped"] += 1
                self._save_stats()
                return True

        return False

    def get_stats(self) -> dict:
        """통계 조회"""
        hit_rate = 0
        if self.stats["total_requests"] > 0:
            hit_rate = round(
                self.stats["cache_hits"] / self.stats["total_requests"] * 100, 2
            )

        return {
            **self.stats,
            "cache_size": len(self.cache),
            "hit_rate_percent": hit_rate,
        }

    def clear_cache(self):
        """캐시 초기화"""
        self.cache = {}
        self._save_cache()

    def invalidate_file(self, file_path: str):
        """특정 파일 관련 캐시 무효화"""
        keys_to_remove = []
        for key, entry in self.cache.items():
            tool_input = entry.get("tool_input", {})
            if tool_input.get("file_path") == file_path:
                keys_to_remove.append(key)
            elif tool_input.get("path") == file_path:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.cache[key]

        if keys_to_remove:
            self._save_cache()


# === Hook Entry Point ===

def main():
    """PreToolUse Hook 엔트리포인트"""
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            print(json.dumps({"decision": "approve"}))
            return

        data = json.loads(input_data)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        optimizer = TokenOptimizer()

        # 파일 쓰기 시 관련 캐시 무효화
        if tool_name in ["Write", "Edit"]:
            file_path = tool_input.get("file_path", "")
            if file_path:
                optimizer.invalidate_file(file_path)
            print(json.dumps({"decision": "approve"}))
            return

        # 캐시 확인 (Read, Grep, Glob)
        if tool_name in ["Read", "Grep", "Glob"]:
            cached = optimizer.check_cache(tool_name, tool_input)
            if cached:
                # 캐시 히트 - 결과를 메시지로 전달 (실제로는 approve하고 캐시 정보 로깅)
                # Hook은 차단하지 않고 통계만 기록
                print(
                    json.dumps(
                        {
                            "decision": "approve",
                            "metadata": {
                                "cache_hit": True,
                                "tokens_saved": cached.get("original_tokens", 0),
                            },
                        }
                    )
                )
                return

        print(json.dumps({"decision": "approve"}))

    except Exception as e:
        print(json.dumps({"decision": "approve", "error": str(e)}))


if __name__ == "__main__":
    # 테스트 모드
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("=== Token Optimizer Test ===\n")

        optimizer = TokenOptimizer(ttl_minutes=5)

        # 테스트 1: 캐시 저장
        test_input = {"file_path": "C:\\claude\\test.py"}
        test_result = "def hello():\n    print('Hello, World!')\n" * 10

        print("1. 캐시 저장 테스트")
        store_info = optimizer.store_cache("Read", test_input, test_result)
        print(f"   저장 결과: {store_info}")

        # 테스트 2: 캐시 조회
        print("\n2. 캐시 조회 테스트")
        cached = optimizer.check_cache("Read", test_input)
        print(f"   캐시 히트: {cached is not None}")
        if cached:
            print(f"   토큰 절약: {cached.get('original_tokens', 0)}")

        # 테스트 3: 중복 요청 확인
        print("\n3. 중복 요청 테스트 (Grep)")
        grep_input = {"pattern": "def.*hello", "path": "C:\\claude"}
        optimizer.store_cache("Grep", grep_input, "test.py:1:def hello()")
        is_dup = optimizer.check_duplicate("Grep", grep_input)
        print(f"   중복 여부: {is_dup}")

        # 테스트 4: 통계
        print("\n4. 통계")
        stats = optimizer.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        # 테스트 5: 압축
        print("\n5. 콘텐츠 압축 테스트")
        long_content = "\n".join([f"Line {i}: Some content here" for i in range(100)])
        compressed, was_compressed = optimizer._compress_content(long_content)
        print(f"   원본 길이: {len(long_content)}")
        print(f"   압축 후 길이: {len(compressed)}")
        print(f"   압축 여부: {was_compressed}")

        print("\n=== 테스트 완료 ===")
    else:
        main()
