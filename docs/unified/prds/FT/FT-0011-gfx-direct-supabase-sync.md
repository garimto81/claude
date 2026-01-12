# PRD-0011: GFX PC → Supabase 직접 동기화

## 문서 정보

| 항목 | 내용 |
|------|------|
| **PRD ID** | PRD-0011 |
| **제목** | GFX PC → Supabase 직접 동기화 스크립트 |
| **버전** | 1.0 |
| **작성일** | 2026-01-12 |
| **상태** | Draft |
| **상위 문서** | [PRD-0002](./FT-0002-primary-gfx-rfid.md) |
| **관련 문서** | [PRD-0010](./FT-0010-nas-smb-integration.md) (Blocked) |

---

## 1. 개요

### 1.1 목적

PokerGFX가 실행되는 Windows PC에서 JSON 파일이 생성될 때 직접 Supabase로 업로드하는 경량 동기화 스크립트 제작.

### 1.2 배경

| 문제 | 설명 |
|------|------|
| **PRD-0010 Blocked** | NAS SMB 연결 반복 실패 (System error 67) |
| **대안 필요** | SMB 의존성 없이 데이터 수집 가능한 경로 |
| **즉시 가치** | NAS 인프라 문제 해결 전에도 데이터 수집 시작 가능 |

### 1.3 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      GFX PC (Windows)                        │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   PokerGFX   │───▶│  JSON 파일   │◀──▶│  Sync Agent  │   │
│  │   (기존)     │    │  C:\GFX\out\ │    │  (Python)    │   │
│  └──────────────┘    └──────────────┘    └──────┬───────┘   │
│                                                  │           │
└──────────────────────────────────────────────────┼───────────┘
                                                   │ HTTPS
                                                   ▼
                                          ┌──────────────┐
                                          │   Supabase   │
                                          │  (gfx_sessions)
                                          └──────────────┘
```

### 1.4 핵심 가치

| 항목 | 설명 |
|------|------|
| **NAS 무의존** | SMB 연결 없이 직접 클라우드 업로드 |
| **경량화** | 단일 Python 스크립트, 최소 의존성 |
| **오프라인 대응** | 네트워크 끊김 시 로컬 큐잉 |
| **즉시 배포** | 기존 인프라 변경 없이 GFX PC에 설치 |

---

## 2. 요구사항

### 2.1 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|----------|:--------:|
| FR-01 | JSON 파일 생성/변경 감지 (watchdog) | HIGH |
| FR-02 | Supabase `gfx_sessions` 테이블 업로드 | HIGH |
| FR-03 | 중복 파일 감지 (SHA256 해시) | HIGH |
| FR-04 | 오프라인 큐잉 (SQLite 로컬 버퍼) | MEDIUM |
| FR-05 | 시스템 트레이 아이콘 (상태 표시) | LOW |
| FR-06 | 자동 시작 (Windows 서비스) | MEDIUM |

### 2.2 비기능 요구사항

| ID | 요구사항 | 목표 값 |
|----|----------|---------|
| NFR-01 | 파일 감지 → 업로드 지연 | < 5초 |
| NFR-02 | 메모리 사용량 | < 50MB |
| NFR-03 | CPU 사용량 (대기 시) | < 1% |
| NFR-04 | 오프라인 큐 용량 | 최대 1000 파일 |
| NFR-05 | 재시도 간격 | 5초 → 10초 → 30초 (지수 백오프) |

---

## 3. 시스템 구성

### 3.1 GFX PC 환경

| 구성 요소 | 값 | 비고 |
|----------|-----|------|
| OS | Windows 10/11 | 64-bit |
| Python | 3.11+ | 또는 PyInstaller 빌드 |
| PokerGFX 출력 경로 | `C:\GFX\output\` | 설정 가능 |
| 로컬 큐 경로 | `C:\GFX\sync_queue\` | SQLite |

### 3.2 Supabase 연결

| 항목 | 설명 |
|------|------|
| **테이블** | `gfx_sessions` (기존) |
| **인증** | Service Role Key (환경 변수) |
| **프로토콜** | HTTPS (TLS 1.3) |
| **Rate Limit** | 1000 req/min (충분) |

### 3.3 디렉토리 구조

```
C:\GFX\
├── output\                    # PokerGFX JSON 출력 (감시 대상)
│   └── PGFX_live_data_export GameID=*.json
├── sync_queue\               # 오프라인 큐 (SQLite)
│   └── pending.db
├── logs\                     # 로그 파일
│   └── sync_agent.log
└── sync_agent\              # 동기화 에이전트
    ├── sync_agent.py        # 메인 스크립트
    ├── config.env           # 설정 파일
    └── requirements.txt     # 의존성
```

---

## 4. 상세 설계

### 4.1 파일 감시 로직

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio
from pathlib import Path

class GFXFileHandler(FileSystemEventHandler):
    """PokerGFX JSON 파일 감시 핸들러"""

    FILE_PATTERN = "PGFX_live_data_export GameID=*.json"

    def __init__(self, sync_service: "SyncService"):
        self.sync_service = sync_service
        self._pending: dict[str, asyncio.Task] = {}

    def on_created(self, event):
        if event.is_directory:
            return
        if self._matches_pattern(event.src_path):
            self._schedule_sync(event.src_path, "created")

    def on_modified(self, event):
        if event.is_directory:
            return
        if self._matches_pattern(event.src_path):
            self._schedule_sync(event.src_path, "modified")

    def _matches_pattern(self, path: str) -> bool:
        return Path(path).match(self.FILE_PATTERN)

    def _schedule_sync(self, path: str, operation: str):
        """파일 안정화 대기 후 동기화 예약"""
        # 기존 작업 취소 (파일 수정 중일 수 있음)
        if path in self._pending:
            self._pending[path].cancel()

        async def delayed_sync():
            await asyncio.sleep(2.0)  # 파일 쓰기 완료 대기
            await self.sync_service.sync_file(path, operation)

        self._pending[path] = asyncio.create_task(delayed_sync())
```

### 4.2 동기화 서비스

```python
import hashlib
import json
import logging
from datetime import datetime, UTC
from pathlib import Path
from supabase import create_client

logger = logging.getLogger(__name__)

class SyncService:
    """Supabase 동기화 서비스"""

    def __init__(self, supabase_url: str, supabase_key: str):
        self.client = create_client(supabase_url, supabase_key)
        self.local_queue = LocalQueue()

    async def sync_file(self, file_path: str, operation: str) -> bool:
        """파일을 Supabase로 동기화"""
        path = Path(file_path)

        try:
            # 파일 읽기
            content = path.read_bytes()
            file_hash = hashlib.sha256(content).hexdigest()

            # 중복 확인
            if await self._is_duplicate(file_hash):
                logger.info(f"Skipping duplicate: {path.name}")
                return True

            # JSON 파싱
            data = json.loads(content.decode("utf-8"))
            session_id = data.get("ID")

            # Supabase 업로드
            record = {
                "session_id": session_id,
                "file_name": path.name,
                "file_hash": file_hash,
                "raw_json": data,
                "table_type": data.get("Type", "UNKNOWN"),
                "event_title": data.get("EventTitle", ""),
                "software_version": data.get("SoftwareVersion", ""),
                "hand_count": len(data.get("Hands", [])),
                "session_created_at": data.get("CreatedDateTimeUTC"),
                "sync_source": "gfx_pc_direct",
                "sync_status": "synced",
            }

            self.client.table("gfx_sessions").upsert(
                record,
                on_conflict="session_id"
            ).execute()

            logger.info(
                f"Synced: {path.name} "
                f"({record['hand_count']} hands, {operation})"
            )
            return True

        except ConnectionError as e:
            # 오프라인 → 로컬 큐에 저장
            logger.warning(f"Offline, queuing: {path.name}")
            self.local_queue.enqueue(file_path, operation)
            return False

        except Exception as e:
            logger.error(f"Sync failed: {path.name} - {e}")
            return False

    async def _is_duplicate(self, file_hash: str) -> bool:
        """해시로 중복 확인"""
        result = (
            self.client.table("gfx_sessions")
            .select("id")
            .eq("file_hash", file_hash)
            .limit(1)
            .execute()
        )
        return len(result.data) > 0

    async def process_offline_queue(self):
        """오프라인 큐 처리 (재연결 시)"""
        pending = self.local_queue.get_pending()
        for item in pending:
            success = await self.sync_file(item["path"], item["operation"])
            if success:
                self.local_queue.mark_completed(item["id"])
```

### 4.3 로컬 큐 (오프라인 대응)

```python
import sqlite3
from datetime import datetime, UTC
from pathlib import Path

class LocalQueue:
    """SQLite 기반 오프라인 큐"""

    def __init__(self, db_path: str = "C:/GFX/sync_queue/pending.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pending_syncs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending'
                )
            """)

    def enqueue(self, file_path: str, operation: str):
        """큐에 추가"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO pending_syncs
                   (file_path, operation, created_at)
                   VALUES (?, ?, ?)""",
                (file_path, operation, datetime.now(UTC).isoformat())
            )

    def get_pending(self, limit: int = 50) -> list[dict]:
        """대기 중인 항목 조회"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM pending_syncs
                   WHERE status = 'pending'
                   ORDER BY created_at ASC
                   LIMIT ?""",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def mark_completed(self, item_id: int):
        """완료 표시"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE pending_syncs SET status = 'completed' WHERE id = ?",
                (item_id,)
            )
```

### 4.4 설정 파일

```env
# config.env

# Supabase 연결
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJxxxxxx  # Service Role Key

# 감시 경로
GFX_WATCH_PATH=C:\GFX\output

# 로깅
LOG_LEVEL=INFO
LOG_PATH=C:\GFX\logs\sync_agent.log

# 동기화 설정
FILE_SETTLE_DELAY=2.0       # 파일 안정화 대기 (초)
RETRY_DELAY=5.0             # 재시도 간격 (초)
MAX_RETRIES=5               # 최대 재시도 횟수
QUEUE_PROCESS_INTERVAL=60   # 오프라인 큐 처리 간격 (초)
```

---

## 5. 메인 스크립트

### 5.1 sync_agent.py

```python
#!/usr/bin/env python3
"""GFX PC → Supabase 직접 동기화 에이전트"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from watchdog.observers import Observer

# 설정 로드
load_dotenv(Path(__file__).parent / "config.env")

# 로깅 설정
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.getenv("LOG_PATH", "sync_agent.log")),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """메인 엔트리포인트"""
    logger.info("GFX Sync Agent starting...")

    # 서비스 초기화
    sync_service = SyncService(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY"),
    )

    # 파일 감시 설정
    watch_path = os.getenv("GFX_WATCH_PATH", "C:/GFX/output")
    handler = GFXFileHandler(sync_service)
    observer = Observer()
    observer.schedule(handler, watch_path, recursive=False)
    observer.start()

    logger.info(f"Watching: {watch_path}")

    # 오프라인 큐 주기적 처리
    queue_interval = float(os.getenv("QUEUE_PROCESS_INTERVAL", 60))

    try:
        while True:
            await asyncio.sleep(queue_interval)
            await sync_service.process_offline_queue()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. 배포

### 6.1 의존성

```txt
# requirements.txt
supabase>=2.0.0
watchdog>=3.0.0
python-dotenv>=1.0.0
```

### 6.2 설치 스크립트

```powershell
# install.ps1

# Python 확인
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python 3.11+ required. Install from python.org"
    exit 1
}

# 디렉토리 생성
$dirs = @(
    "C:\GFX\output",
    "C:\GFX\sync_queue",
    "C:\GFX\logs",
    "C:\GFX\sync_agent"
)
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

# 의존성 설치
pip install -r requirements.txt

# 설정 파일 복사 (수동 편집 필요)
Copy-Item config.env.example C:\GFX\sync_agent\config.env

Write-Host "Installation complete!"
Write-Host "Edit C:\GFX\sync_agent\config.env with your Supabase credentials"
```

### 6.3 Windows 서비스 등록

```powershell
# register_service.ps1

# NSSM으로 서비스 등록 (https://nssm.cc/)
$nssm = "C:\tools\nssm.exe"
$serviceName = "GFXSyncAgent"
$pythonPath = (Get-Command python).Source
$scriptPath = "C:\GFX\sync_agent\sync_agent.py"

& $nssm install $serviceName $pythonPath $scriptPath
& $nssm set $serviceName AppDirectory "C:\GFX\sync_agent"
& $nssm set $serviceName DisplayName "GFX Supabase Sync Agent"
& $nssm set $serviceName Description "PokerGFX JSON to Supabase sync service"
& $nssm set $serviceName Start SERVICE_AUTO_START

# 서비스 시작
& $nssm start $serviceName
```

### 6.4 PyInstaller 빌드 (Python 미설치 환경)

```powershell
# build.ps1
pip install pyinstaller
pyinstaller --onefile --name GFXSyncAgent sync_agent.py

# 결과: dist/GFXSyncAgent.exe
```

---

## 7. 모니터링

### 7.1 로그 포맷

```
2026-01-12 14:30:15 [INFO] GFX Sync Agent starting...
2026-01-12 14:30:15 [INFO] Watching: C:\GFX\output
2026-01-12 14:30:20 [INFO] Synced: PGFX_live_data_export GameID=123.json (15 hands, created)
2026-01-12 14:31:00 [INFO] Synced: PGFX_live_data_export GameID=123.json (18 hands, modified)
2026-01-12 14:31:30 [WARNING] Offline, queuing: PGFX_live_data_export GameID=124.json
2026-01-12 14:32:30 [INFO] Processing offline queue: 1 pending
```

### 7.2 Supabase 대시보드 확인

```sql
-- 최근 동기화 확인
SELECT
    file_name,
    hand_count,
    sync_source,
    sync_status,
    processed_at
FROM gfx_sessions
WHERE sync_source = 'gfx_pc_direct'
ORDER BY processed_at DESC
LIMIT 20;
```

### 7.3 헬스체크

```python
# health_check.py
import os
from supabase import create_client

def check_connection():
    client = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    result = client.table("gfx_sessions").select("id").limit(1).execute()
    return len(result.data) >= 0  # 쿼리 성공 여부

if __name__ == "__main__":
    if check_connection():
        print("OK: Supabase connected")
    else:
        print("FAIL: Cannot connect to Supabase")
```

---

## 8. 스키마 확장

### 8.1 gfx_sessions 테이블 수정

기존 테이블에 `sync_source` 컬럼 추가로 데이터 출처 구분:

```sql
-- Supabase SQL Editor
ALTER TABLE gfx_sessions
ADD COLUMN IF NOT EXISTS sync_source TEXT DEFAULT 'nas';

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_gfx_sessions_sync_source
ON gfx_sessions(sync_source);

-- 코멘트
COMMENT ON COLUMN gfx_sessions.sync_source IS
'Data source: nas (NAS/Docker), gfx_pc_direct (GFX PC direct upload)';
```

### 8.2 sync_source 값

| 값 | 설명 |
|----|------|
| `nas` | NAS → Docker 경로 (기존) |
| `gfx_pc_direct` | GFX PC 직접 업로드 (신규) |
| `simulator` | 시뮬레이터 (테스트) |

---

## 9. PRD-0010과의 관계

### 9.1 병행 운영

| 시나리오 | 우선순위 | 설명 |
|----------|:--------:|------|
| PRD-0010 Blocked 유지 | PRD-0011 사용 | GFX PC 직접 업로드 |
| PRD-0010 해결됨 | 선택 가능 | NAS 경로 또는 직접 업로드 중 선택 |
| 두 경로 동시 | 중복 방지 | `file_hash` 기반 중복 감지로 충돌 없음 |

### 9.2 마이그레이션 경로

```
현재 (Blocked):
  GFX PC → (X) NAS → Docker → Supabase

PRD-0011 적용:
  GFX PC ─────────────────────▶ Supabase

향후 (PRD-0010 해결 시):
  GFX PC ───▶ NAS ───▶ Docker ───▶ Supabase (백업)
       └────────────────────────▶ Supabase (주 경로)
```

---

## 10. 체크리스트

### 10.1 개발

- [ ] sync_agent.py 구현
- [ ] LocalQueue (SQLite) 구현
- [ ] GFXFileHandler 구현
- [ ] 설정 파일 템플릿 작성
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 (로컬)

### 10.2 배포

- [ ] GFX PC에 Python 3.11 설치 확인
- [ ] 디렉토리 구조 생성
- [ ] config.env 설정 (Supabase 키)
- [ ] 수동 실행 테스트
- [ ] Windows 서비스 등록
- [ ] 로그 확인

### 10.3 검증

- [ ] JSON 파일 생성 시 자동 업로드
- [ ] 파일 수정 시 증분 업로드
- [ ] 오프라인 시 로컬 큐잉
- [ ] 재연결 시 큐 처리
- [ ] Supabase 대시보드에서 데이터 확인

---

## 11. 관련 문서

| 문서 | 설명 |
|------|------|
| [PRD-0002](./FT-0002-primary-gfx-rfid.md) | PokerGFX JSON 스키마 |
| [PRD-0010](./FT-0010-nas-smb-integration.md) | NAS SMB 연동 (Blocked) |
| [supabase_client.py](../../src/database/supabase_client.py) | Supabase 클라이언트 |
| [supabase_repository.py](../../src/database/supabase_repository.py) | Repository 패턴 |

---

## 12. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-01-12 | 초안 작성 | Claude |

