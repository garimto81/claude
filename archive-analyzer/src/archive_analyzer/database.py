"""SQLite 데이터베이스 모듈

스캔 결과 저장 및 조회를 위한 데이터베이스 관리
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Iterator, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import logging

from .file_classifier import FileType

logger = logging.getLogger(__name__)


@dataclass
class FileRecord:
    """파일 레코드 데이터 클래스"""
    id: Optional[int] = None
    path: str = ""
    filename: str = ""
    extension: str = ""
    size_bytes: int = 0
    modified_at: Optional[datetime] = None
    file_type: str = ""
    parent_folder: str = ""
    scan_status: str = "pending"
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        d = asdict(self)
        if d['modified_at']:
            d['modified_at'] = d['modified_at'].isoformat()
        if d['created_at']:
            d['created_at'] = d['created_at'].isoformat()
        return d

    @classmethod
    def from_row(cls, row: tuple, columns: list[str]) -> "FileRecord":
        """데이터베이스 행에서 생성"""
        data = dict(zip(columns, row))

        # datetime 변환
        if data.get('modified_at'):
            data['modified_at'] = datetime.fromisoformat(data['modified_at'])
        if data.get('created_at'):
            data['created_at'] = datetime.fromisoformat(data['created_at'])

        return cls(**data)


@dataclass
class ScanCheckpoint:
    """스캔 체크포인트"""
    id: Optional[int] = None
    scan_id: str = ""
    last_path: str = ""
    total_files: int = 0
    processed_files: int = 0
    status: str = "in_progress"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Database:
    """SQLite 데이터베이스 관리자"""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str = "archive.db"):
        """
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._ensure_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """데이터베이스 연결 반환"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    @contextmanager
    def transaction(self):
        """트랜잭션 컨텍스트 매니저"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def _ensure_schema(self) -> None:
        """데이터베이스 스키마 생성"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 파일 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                extension TEXT,
                size_bytes INTEGER DEFAULT 0,
                modified_at DATETIME,
                file_type TEXT,
                parent_folder TEXT,
                scan_status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 인덱스 생성
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_status ON files(scan_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_parent ON files(parent_folder)")

        # 스캔 체크포인트 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT UNIQUE NOT NULL,
                last_path TEXT,
                total_files INTEGER DEFAULT 0,
                processed_files INTEGER DEFAULT 0,
                status TEXT DEFAULT 'in_progress',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 스캔 통계 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT NOT NULL,
                file_type TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                total_size INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info(f"Database schema ensured at {self.db_path}")

    def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self._connection:
            self._connection.close()
            self._connection = None

    # === 파일 CRUD ===

    def insert_file(self, record: FileRecord) -> int:
        """파일 레코드 삽입

        Args:
            record: 파일 레코드

        Returns:
            삽입된 레코드 ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO files
            (path, filename, extension, size_bytes, modified_at, file_type, parent_folder, scan_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.path,
            record.filename,
            record.extension,
            record.size_bytes,
            record.modified_at.isoformat() if record.modified_at else None,
            record.file_type,
            record.parent_folder,
            record.scan_status,
        ))

        conn.commit()
        return cursor.lastrowid

    def insert_files_batch(self, records: List[FileRecord]) -> int:
        """파일 레코드 일괄 삽입

        Args:
            records: 파일 레코드 목록

        Returns:
            삽입된 레코드 수
        """
        if not records:
            return 0

        conn = self._get_connection()
        cursor = conn.cursor()

        data = [
            (
                r.path,
                r.filename,
                r.extension,
                r.size_bytes,
                r.modified_at.isoformat() if r.modified_at else None,
                r.file_type,
                r.parent_folder,
                r.scan_status,
            )
            for r in records
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO files
            (path, filename, extension, size_bytes, modified_at, file_type, parent_folder, scan_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data)

        conn.commit()
        return len(records)

    def get_file_by_path(self, path: str) -> Optional[FileRecord]:
        """경로로 파일 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM files WHERE path = ?", (path,))
        row = cursor.fetchone()

        if row:
            columns = [col[0] for col in cursor.description]
            return FileRecord.from_row(tuple(row), columns)
        return None

    def get_files_by_type(self, file_type: str, limit: int = 1000) -> List[FileRecord]:
        """파일 유형으로 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM files WHERE file_type = ? LIMIT ?",
            (file_type, limit)
        )

        columns = [col[0] for col in cursor.description]
        return [FileRecord.from_row(tuple(row), columns) for row in cursor.fetchall()]

    def get_all_files(self, limit: int = 10000) -> Iterator[FileRecord]:
        """모든 파일 조회 (제너레이터)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM files LIMIT ?", (limit,))
        columns = [col[0] for col in cursor.description]

        for row in cursor:
            yield FileRecord.from_row(tuple(row), columns)

    def update_file_status(self, path: str, status: str) -> bool:
        """파일 상태 업데이트"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE files SET scan_status = ? WHERE path = ?",
            (status, path)
        )
        conn.commit()
        return cursor.rowcount > 0

    def delete_file(self, path: str) -> bool:
        """파일 레코드 삭제"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM files WHERE path = ?", (path,))
        conn.commit()
        return cursor.rowcount > 0

    def file_exists(self, path: str) -> bool:
        """파일 존재 여부 확인"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM files WHERE path = ? LIMIT 1", (path,))
        return cursor.fetchone() is not None

    # === 통계 ===

    def get_file_count(self, file_type: Optional[str] = None) -> int:
        """파일 수 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if file_type:
            cursor.execute(
                "SELECT COUNT(*) FROM files WHERE file_type = ?",
                (file_type,)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM files")

        return cursor.fetchone()[0]

    def get_total_size(self, file_type: Optional[str] = None) -> int:
        """총 파일 크기 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if file_type:
            cursor.execute(
                "SELECT COALESCE(SUM(size_bytes), 0) FROM files WHERE file_type = ?",
                (file_type,)
            )
        else:
            cursor.execute("SELECT COALESCE(SUM(size_bytes), 0) FROM files")

        return cursor.fetchone()[0]

    def get_statistics(self) -> dict:
        """전체 통계 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                file_type,
                COUNT(*) as count,
                COALESCE(SUM(size_bytes), 0) as total_size
            FROM files
            GROUP BY file_type
        """)

        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_type': {}
        }

        for row in cursor.fetchall():
            file_type = row['file_type'] or 'unknown'
            count = row['count']
            size = row['total_size']

            stats['by_type'][file_type] = {
                'count': count,
                'size': size
            }
            stats['total_files'] += count
            stats['total_size'] += size

        return stats

    # === 체크포인트 ===

    def save_checkpoint(self, checkpoint: ScanCheckpoint) -> int:
        """체크포인트 저장"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO scan_checkpoints
            (scan_id, last_path, total_files, processed_files, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            checkpoint.scan_id,
            checkpoint.last_path,
            checkpoint.total_files,
            checkpoint.processed_files,
            checkpoint.status,
            datetime.now().isoformat(),
        ))

        conn.commit()
        return cursor.lastrowid

    def get_checkpoint(self, scan_id: str) -> Optional[ScanCheckpoint]:
        """체크포인트 조회"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM scan_checkpoints WHERE scan_id = ?",
            (scan_id,)
        )
        row = cursor.fetchone()

        if row:
            return ScanCheckpoint(
                id=row['id'],
                scan_id=row['scan_id'],
                last_path=row['last_path'],
                total_files=row['total_files'],
                processed_files=row['processed_files'],
                status=row['status'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            )
        return None

    def update_checkpoint_progress(
        self,
        scan_id: str,
        last_path: str,
        processed_files: int
    ) -> None:
        """체크포인트 진행 상황 업데이트"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE scan_checkpoints
            SET last_path = ?, processed_files = ?, updated_at = ?
            WHERE scan_id = ?
        """, (
            last_path,
            processed_files,
            datetime.now().isoformat(),
            scan_id,
        ))

        conn.commit()

    def complete_checkpoint(self, scan_id: str) -> None:
        """체크포인트 완료 처리"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE scan_checkpoints
            SET status = 'completed', updated_at = ?
            WHERE scan_id = ?
        """, (datetime.now().isoformat(), scan_id))

        conn.commit()

    def clear_all(self) -> None:
        """모든 데이터 삭제 (테스트용)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM files")
        cursor.execute("DELETE FROM scan_checkpoints")
        cursor.execute("DELETE FROM scan_stats")

        conn.commit()
        logger.warning("All data cleared from database")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
