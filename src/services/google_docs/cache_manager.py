"""
Cache Manager

Google Docs → 로컬 Markdown 캐시 동기화.
"""

import logging
import re
from datetime import datetime
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .client import GoogleDocsClient
from .metadata_manager import MetadataManager

logger = logging.getLogger(__name__)


class CacheManager:
    """로컬 캐시 관리자"""

    # 기본 캐시 디렉토리
    DEFAULT_CACHE_DIR = _get_project_root() / "tasks" / "prds"

    # 캐시 파일 헤더 템플릿
    CACHE_HEADER_TEMPLATE = """<!--
  {prd_id} Local Cache (Read-Only)
  Master: {google_doc_url}
  Last Synced: {last_sync}
  DO NOT EDIT - Changes will be overwritten
-->

"""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        client: Optional[GoogleDocsClient] = None,
        metadata_manager: Optional[MetadataManager] = None,
    ):
        """
        초기화

        Args:
            cache_dir: 캐시 디렉토리 경로
            client: Google Docs 클라이언트
            metadata_manager: 메타데이터 관리자
        """
        self.cache_dir = cache_dir or self.DEFAULT_CACHE_DIR
        self.client = client or GoogleDocsClient()
        self.metadata = metadata_manager or MetadataManager()

    def _ensure_cache_dir(self) -> None:
        """캐시 디렉토리 존재 확인"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, prd_id: str) -> Path:
        """캐시 파일 경로 생성"""
        return self.cache_dir / f"{prd_id}.cache.md"

    # ==================== Sync Operations ====================

    def sync_prd(self, prd_id: str) -> bool:
        """
        단일 PRD 동기화 (Google Docs → 로컬 캐시)

        Args:
            prd_id: PRD ID

        Returns:
            동기화 성공 여부
        """
        prd = self.metadata.get_prd(prd_id)
        if not prd:
            logger.warning(f"PRD를 찾을 수 없음: {prd_id}")
            return False

        try:
            # Google Docs에서 내용 가져오기
            doc = self.client.get_document(prd.google_doc_id)
            content = self._convert_doc_to_markdown(doc)

            # 캐시 파일 헤더 생성
            header = self.CACHE_HEADER_TEMPLATE.format(
                prd_id=prd_id,
                google_doc_url=prd.google_doc_url,
                last_sync=datetime.utcnow().isoformat() + "Z",
            )

            # 캐시 파일 저장
            self._ensure_cache_dir()
            cache_path = self._get_cache_path(prd_id)

            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(header)
                f.write(content)

            # 메타데이터 업데이트
            self.metadata.update_prd(prd_id, local_cache=cache_path.name)

            logger.info(f"캐시 동기화 완료: {prd_id} → {cache_path}")
            return True

        except Exception as e:
            logger.error(f"캐시 동기화 실패: {prd_id} - {e}")
            return False

    def sync_all(self) -> Dict[str, bool]:
        """
        모든 PRD 동기화

        Returns:
            PRD ID별 동기화 결과 딕셔너리
        """
        results = {}
        for prd in self.metadata.list_prds():
            results[prd.prd_id] = self.sync_prd(prd.prd_id)

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        logger.info(f"전체 동기화 완료: {success_count}/{total_count}")

        return results

    # ==================== Google Docs → Markdown Conversion ====================

    def _convert_doc_to_markdown(self, doc: Dict[str, Any]) -> str:
        """
        Google Docs 문서를 Markdown으로 변환

        Args:
            doc: Google Docs 문서 객체

        Returns:
            Markdown 문자열
        """
        body = doc.get("body", {})
        content = body.get("content", [])

        markdown_parts = []

        for element in content:
            if "paragraph" in element:
                md = self._convert_paragraph(element["paragraph"])
                if md:
                    markdown_parts.append(md)
            elif "table" in element:
                md = self._convert_table(element["table"])
                if md:
                    markdown_parts.append(md)
            elif "sectionBreak" in element:
                markdown_parts.append("\n---\n")

        return "\n".join(markdown_parts)

    def _convert_paragraph(self, paragraph: Dict[str, Any]) -> str:
        """
        단락을 Markdown으로 변환

        Args:
            paragraph: 단락 객체

        Returns:
            Markdown 문자열
        """
        elements = paragraph.get("elements", [])
        style = paragraph.get("paragraphStyle", {})
        named_style = style.get("namedStyleType", "NORMAL_TEXT")

        # 텍스트 추출
        text_parts = []
        for element in elements:
            if "textRun" in element:
                text = element["textRun"].get("content", "")
                text_style = element["textRun"].get("textStyle", {})

                # 스타일 적용
                if text_style.get("bold"):
                    text = f"**{text.strip()}**"
                if text_style.get("italic"):
                    text = f"*{text.strip()}*"
                if text_style.get("strikethrough"):
                    text = f"~~{text.strip()}~~"

                text_parts.append(text)

        text = "".join(text_parts).rstrip()

        if not text:
            return ""

        # 헤딩 처리
        heading_map = {
            "HEADING_1": "#",
            "HEADING_2": "##",
            "HEADING_3": "###",
            "HEADING_4": "####",
            "HEADING_5": "#####",
            "HEADING_6": "######",
        }

        if named_style in heading_map:
            prefix = heading_map[named_style]
            # 줄바꿈 제거
            text = text.replace("\n", " ").strip()
            return f"{prefix} {text}\n"

        # 리스트 처리
        bullet = paragraph.get("bullet")
        if bullet:
            nesting = bullet.get("nestingLevel", 0)
            indent = "  " * nesting
            _list_id = bullet.get(
                "listId", ""
            )  # TODO: 번호 매기기 리스트에서 사용 예정

            # 번호 매기기 또는 글머리 기호
            # TODO: 번호 매기기 리스트 지원
            return f"{indent}- {text.strip()}\n"

        # 일반 텍스트
        return f"{text}\n"

    def _convert_table(self, table: Dict[str, Any]) -> str:
        """
        테이블을 Markdown으로 변환

        Args:
            table: 테이블 객체

        Returns:
            Markdown 문자열
        """
        rows = table.get("tableRows", [])
        if not rows:
            return ""

        markdown_rows = []

        for row_idx, row in enumerate(rows):
            cells = row.get("tableCells", [])
            cell_texts = []

            for cell in cells:
                # 셀 내용 추출
                cell_content = cell.get("content", [])
                text = self._extract_cell_text(cell_content)
                cell_texts.append(text.strip().replace("\n", " "))

            markdown_rows.append("| " + " | ".join(cell_texts) + " |")

            # 헤더 구분선 추가
            if row_idx == 0:
                separator = "| " + " | ".join(["---"] * len(cell_texts)) + " |"
                markdown_rows.append(separator)

        return "\n".join(markdown_rows) + "\n"

    def _extract_cell_text(self, content: List[Dict]) -> str:
        """셀 내용에서 텍스트 추출"""
        text_parts = []

        for element in content:
            if "paragraph" in element:
                for para_element in element["paragraph"].get("elements", []):
                    if "textRun" in para_element:
                        text_parts.append(para_element["textRun"].get("content", ""))

        return "".join(text_parts)

    # ==================== Cache Read Operations ====================

    def read_cache(self, prd_id: str) -> Optional[str]:
        """
        캐시 파일 읽기

        Args:
            prd_id: PRD ID

        Returns:
            캐시 내용 또는 None
        """
        cache_path = self._get_cache_path(prd_id)

        if not cache_path.exists():
            logger.warning(f"캐시 파일 없음: {cache_path}")
            return None

        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_cache_info(self, prd_id: str) -> Optional[Dict[str, Any]]:
        """
        캐시 파일 정보 조회

        Args:
            prd_id: PRD ID

        Returns:
            캐시 정보 딕셔너리 또는 None
        """
        cache_path = self._get_cache_path(prd_id)

        if not cache_path.exists():
            return None

        stat = cache_path.stat()

        # 헤더에서 last_sync 추출
        content = self.read_cache(prd_id)
        last_sync = None
        if content:
            match = re.search(r"Last Synced: ([^\n]+)", content)
            if match:
                last_sync = match.group(1).strip()

        return {
            "path": str(cache_path),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "last_sync": last_sync,
        }

    def is_cache_stale(
        self,
        prd_id: str,
        max_age_hours: int = 1,
    ) -> bool:
        """
        캐시가 오래되었는지 확인

        Args:
            prd_id: PRD ID
            max_age_hours: 최대 허용 시간 (시간)

        Returns:
            캐시가 오래되었으면 True
        """
        cache_info = self.get_cache_info(prd_id)
        if not cache_info:
            return True  # 캐시 없음 = 오래됨

        last_sync = cache_info.get("last_sync")
        if not last_sync:
            return True

        try:
            # ISO 형식 파싱
            sync_time = datetime.fromisoformat(last_sync.replace("Z", "+00:00"))
            now = datetime.now(sync_time.tzinfo)
            age = now - sync_time
            return age.total_seconds() > max_age_hours * 3600
        except Exception:
            return True

    # ==================== Cache Delete Operations ====================

    def delete_cache(self, prd_id: str) -> bool:
        """
        캐시 파일 삭제

        Args:
            prd_id: PRD ID

        Returns:
            삭제 성공 여부
        """
        cache_path = self._get_cache_path(prd_id)

        if cache_path.exists():
            cache_path.unlink()
            logger.info(f"캐시 삭제됨: {cache_path}")
            return True

        return False

    def clear_all_caches(self) -> int:
        """
        모든 캐시 파일 삭제

        Returns:
            삭제된 파일 수
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.cache.md"):
            cache_file.unlink()
            count += 1

        logger.info(f"캐시 전체 삭제: {count}개 파일")
        return count

    # ==================== Utility ====================

    def list_cached_prds(self) -> List[str]:
        """
        캐시된 PRD ID 목록

        Returns:
            PRD ID 리스트
        """
        prd_ids = []
        for cache_file in self.cache_dir.glob("*.cache.md"):
            # PRD-0001.cache.md → PRD-0001
            prd_id = cache_file.stem.replace(".cache", "")
            prd_ids.append(prd_id)

        return sorted(prd_ids)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        캐시 통계

        Returns:
            통계 딕셔너리
        """
        cached_ids = self.list_cached_prds()
        total_size = sum(
            self._get_cache_path(prd_id).stat().st_size
            for prd_id in cached_ids
            if self._get_cache_path(prd_id).exists()
        )

        stale_count = sum(1 for prd_id in cached_ids if self.is_cache_stale(prd_id))

        return {
            "cached_count": len(cached_ids),
            "total_size_bytes": total_size,
            "stale_count": stale_count,
            "fresh_count": len(cached_ids) - stale_count,
        }
