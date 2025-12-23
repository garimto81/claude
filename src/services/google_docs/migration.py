"""
PRD Migration Module

기존 Markdown PRD를 Google Docs로 마이그레이션.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .client import GoogleDocsClient
from .metadata_manager import MetadataManager, PRDMetadata
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class MigrationResult:
    """마이그레이션 결과"""

    prd_id: str
    source_path: str
    google_doc_id: str = ""
    google_doc_url: str = ""
    success: bool = False
    error: str = ""
    migrated_at: str = ""

    def __post_init__(self):
        if not self.migrated_at and self.success:
            self.migrated_at = datetime.utcnow().isoformat() + "Z"


@dataclass
class MigrationReport:
    """마이그레이션 보고서"""

    started_at: str = ""
    completed_at: str = ""
    total_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    results: List[MigrationResult] = field(default_factory=list)

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.utcnow().isoformat() + "Z"

    def finalize(self):
        self.completed_at = datetime.utcnow().isoformat() + "Z"
        self.total_count = len(self.results)
        self.success_count = sum(1 for r in self.results if r.success)
        self.failed_count = self.total_count - self.success_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "results": [
                {
                    "prd_id": r.prd_id,
                    "source_path": r.source_path,
                    "google_doc_id": r.google_doc_id,
                    "google_doc_url": r.google_doc_url,
                    "success": r.success,
                    "error": r.error,
                }
                for r in self.results
            ],
        }


class MarkdownToDocsConverter:
    """Markdown → Google Docs 변환기"""

    def convert(self, markdown_content: str) -> List[Dict[str, Any]]:
        """
        Markdown을 Google Docs API 요청으로 변환

        Args:
            markdown_content: Markdown 문자열

        Returns:
            Google Docs batchUpdate 요청 리스트
        """
        requests = []
        current_index = 1

        lines = markdown_content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # 헤딩 처리
            if line.startswith("#"):
                heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
                if heading_match:
                    level = len(heading_match.group(1))
                    text = heading_match.group(2).strip()
                    req, current_index = self._create_heading(
                        text, level, current_index
                    )
                    requests.extend(req)
                    i += 1
                    continue

            # 테이블 처리
            if line.startswith("|"):
                table_lines = []
                while i < len(lines) and lines[i].startswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                req, current_index = self._create_table(table_lines, current_index)
                requests.extend(req)
                continue

            # 리스트 처리
            if re.match(r"^[\s]*[-*]\s+", line):
                req, current_index = self._create_bullet(line, current_index)
                requests.extend(req)
                i += 1
                continue

            # 번호 리스트 처리
            if re.match(r"^[\s]*\d+\.\s+", line):
                req, current_index = self._create_numbered(line, current_index)
                requests.extend(req)
                i += 1
                continue

            # 코드 블록 처리
            if line.startswith("```"):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # 닫는 ``` 건너뛰기
                req, current_index = self._create_code_block(code_lines, current_index)
                requests.extend(req)
                continue

            # 수평선 처리
            if re.match(r"^[-*_]{3,}$", line.strip()):
                req, current_index = self._create_horizontal_rule(current_index)
                requests.extend(req)
                i += 1
                continue

            # 일반 텍스트
            if line.strip():
                req, current_index = self._create_paragraph(line, current_index)
                requests.extend(req)

            i += 1

        return requests

    def _create_heading(
        self, text: str, level: int, index: int
    ) -> Tuple[List[Dict], int]:
        """헤딩 생성"""
        text_with_newline = text + "\n"
        end_index = index + len(text_with_newline)

        heading_map = {
            1: "HEADING_1",
            2: "HEADING_2",
            3: "HEADING_3",
            4: "HEADING_4",
            5: "HEADING_5",
            6: "HEADING_6",
        }

        requests = [
            {"insertText": {"location": {"index": index}, "text": text_with_newline}},
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": end_index - 1},
                    "paragraphStyle": {
                        "namedStyleType": heading_map.get(level, "HEADING_1")
                    },
                    "fields": "namedStyleType",
                }
            },
        ]

        return requests, end_index

    def _create_paragraph(self, text: str, index: int) -> Tuple[List[Dict], int]:
        """일반 단락 생성"""
        # Bold 처리: **text** → text with bold style
        text_with_newline = text + "\n"
        end_index = index + len(text_with_newline)

        requests = [
            {"insertText": {"location": {"index": index}, "text": text_with_newline}}
        ]

        return requests, end_index

    def _create_bullet(self, line: str, index: int) -> Tuple[List[Dict], int]:
        """글머리 기호 리스트 생성"""
        # 들여쓰기 레벨 계산
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        nesting_level = indent // 2

        text = re.sub(r"^[-*]\s+", "", stripped)
        text_with_newline = text + "\n"
        end_index = index + len(text_with_newline)

        requests = [
            {"insertText": {"location": {"index": index}, "text": text_with_newline}},
            {
                "createParagraphBullets": {
                    "range": {"startIndex": index, "endIndex": end_index - 1},
                    "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                }
            },
        ]

        return requests, end_index

    def _create_numbered(self, line: str, index: int) -> Tuple[List[Dict], int]:
        """번호 리스트 생성"""
        stripped = line.lstrip()
        text = re.sub(r"^\d+\.\s+", "", stripped)
        text_with_newline = text + "\n"
        end_index = index + len(text_with_newline)

        requests = [
            {"insertText": {"location": {"index": index}, "text": text_with_newline}},
            {
                "createParagraphBullets": {
                    "range": {"startIndex": index, "endIndex": end_index - 1},
                    "bulletPreset": "NUMBERED_DECIMAL_NESTED",
                }
            },
        ]

        return requests, end_index

    def _create_table(
        self, table_lines: List[str], index: int
    ) -> Tuple[List[Dict], int]:
        """테이블 생성 (간단히 텍스트로 변환)"""
        # Google Docs API의 테이블 생성은 복잡하므로
        # 간단히 텍스트로 변환
        text = "\n".join(table_lines) + "\n\n"
        end_index = index + len(text)

        requests = [{"insertText": {"location": {"index": index}, "text": text}}]

        return requests, end_index

    def _create_code_block(
        self, lines: List[str], index: int
    ) -> Tuple[List[Dict], int]:
        """코드 블록 생성"""
        text = "\n".join(lines) + "\n\n"
        end_index = index + len(text)

        requests = [
            {"insertText": {"location": {"index": index}, "text": text}},
            # Courier New 폰트 적용
            {
                "updateTextStyle": {
                    "range": {"startIndex": index, "endIndex": end_index - 1},
                    "textStyle": {
                        "weightedFontFamily": {"fontFamily": "Courier New"}
                    },
                    "fields": "weightedFontFamily",
                }
            },
        ]

        return requests, end_index

    def _create_horizontal_rule(self, index: int) -> Tuple[List[Dict], int]:
        """수평선 생성"""
        text = "\n---\n\n"
        end_index = index + len(text)

        requests = [{"insertText": {"location": {"index": index}, "text": text}}]

        return requests, end_index


class PRDMigrator:
    """PRD 마이그레이션 관리자"""

    def __init__(
        self,
        client: Optional[GoogleDocsClient] = None,
        metadata_manager: Optional[MetadataManager] = None,
        cache_manager: Optional[CacheManager] = None,
    ):
        """
        초기화

        Args:
            client: Google Docs 클라이언트
            metadata_manager: 메타데이터 관리자
            cache_manager: 캐시 관리자
        """
        self.client = client or GoogleDocsClient()
        self.metadata = metadata_manager or MetadataManager()
        self.cache = cache_manager or CacheManager()
        self.converter = MarkdownToDocsConverter()

    def discover_prds(
        self,
        source_dir: str = "tasks/prds/",
    ) -> List[Tuple[str, Path]]:
        """
        마이그레이션 대상 PRD 검색

        Args:
            source_dir: PRD 디렉토리 경로

        Returns:
            (PRD ID, 파일 경로) 튜플 리스트
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.warning(f"디렉토리 없음: {source_dir}")
            return []

        prds = []

        # PRD-NNNN-*.md 또는 NNNN-prd-*.md 패턴
        for md_file in source_path.glob("*.md"):
            # 캐시 파일 제외
            if ".cache" in md_file.name:
                continue

            # PRD ID 추출
            prd_id = self._extract_prd_id(md_file)
            if prd_id:
                prds.append((prd_id, md_file))

        return sorted(prds, key=lambda x: x[0])

    def _extract_prd_id(self, file_path: Path) -> Optional[str]:
        """파일 경로에서 PRD ID 추출"""
        name = file_path.stem

        # PRD-0001-feature-name.md 패턴
        match = re.match(r"^(PRD-\d{4})", name, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # 0001-prd-feature-name.md 패턴
        match = re.match(r"^(\d{4})-prd-", name, re.IGNORECASE)
        if match:
            return f"PRD-{match.group(1)}"

        return None

    def migrate_single(
        self,
        source_path: Path,
        prd_id: Optional[str] = None,
    ) -> MigrationResult:
        """
        단일 PRD 마이그레이션

        Args:
            source_path: 원본 Markdown 파일 경로
            prd_id: PRD ID (없으면 파일에서 추출)

        Returns:
            마이그레이션 결과
        """
        # PRD ID 결정
        if prd_id is None:
            prd_id = self._extract_prd_id(source_path)
            if prd_id is None:
                prd_id = self.metadata.generate_prd_id()

        result = MigrationResult(prd_id=prd_id, source_path=str(source_path))

        try:
            # 1. Markdown 파일 읽기
            with open(source_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            # 2. 제목 추출
            title = self._extract_title(markdown_content, prd_id)

            # 3. Google Docs 문서 생성
            doc_title = f"{prd_id}: {title}"
            doc_info = self.client.create_document(doc_title)

            # 4. 내용 삽입 (간단히 텍스트로)
            self.client.insert_text(doc_info["documentId"], markdown_content)

            # 5. 메타데이터 저장
            self.metadata.add_prd_with_id(
                prd_id=prd_id,
                google_doc_id=doc_info["documentId"],
                title=title,
                status="In Progress",
            )

            # 6. 로컬 캐시 생성
            self.cache.sync_prd(prd_id)

            result.google_doc_id = doc_info["documentId"]
            result.google_doc_url = doc_info["url"]
            result.success = True

            logger.info(f"마이그레이션 성공: {prd_id} → {doc_info['url']}")

        except Exception as e:
            result.error = str(e)
            logger.error(f"마이그레이션 실패: {prd_id} - {e}")

        return result

    def _extract_title(self, markdown_content: str, prd_id: str) -> str:
        """Markdown에서 제목 추출"""
        # # PRD: Title 또는 # PRD-0001: Title 패턴
        match = re.search(r"^#\s+(?:PRD[-:\s]*\d*[-:\s]*)?\s*(.+)$", markdown_content, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            # PRD ID 제거
            title = re.sub(r"^PRD-\d{4}[-:\s]*", "", title).strip()
            return title

        # 첫 줄 사용
        first_line = markdown_content.strip().split("\n")[0]
        return first_line[:50] if first_line else prd_id

    def migrate_all(
        self,
        source_dir: str = "tasks/prds/",
    ) -> MigrationReport:
        """
        모든 PRD 마이그레이션

        Args:
            source_dir: PRD 디렉토리 경로

        Returns:
            마이그레이션 보고서
        """
        report = MigrationReport()
        prds = self.discover_prds(source_dir)

        logger.info(f"마이그레이션 대상: {len(prds)}개 PRD")

        for prd_id, source_path in prds:
            # 이미 마이그레이션된 PRD 스킵
            existing = self.metadata.get_prd(prd_id)
            if existing:
                logger.info(f"이미 마이그레이션됨, 스킵: {prd_id}")
                continue

            result = self.migrate_single(source_path, prd_id)
            report.results.append(result)

        report.finalize()
        return report

    def migrate_prd(
        self,
        prd_id: str,
        source_path: Optional[str] = None,
    ) -> MigrationResult:
        """
        특정 PRD ID로 마이그레이션

        Args:
            prd_id: PRD ID
            source_path: 원본 파일 경로 (없으면 자동 검색)

        Returns:
            마이그레이션 결과
        """
        if source_path:
            return self.migrate_single(Path(source_path), prd_id)

        # PRD ID로 파일 검색
        prds = self.discover_prds()
        for pid, path in prds:
            if pid.upper() == prd_id.upper():
                return self.migrate_single(path, prd_id)

        return MigrationResult(
            prd_id=prd_id,
            source_path="",
            success=False,
            error=f"PRD 파일을 찾을 수 없음: {prd_id}",
        )
