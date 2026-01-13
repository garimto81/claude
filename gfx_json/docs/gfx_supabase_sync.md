# FT-0011: NAS JSON → Supabase 최적화 동기화

## 문서 정보

| 항목 | 내용 |
|------|------|
| **PRD ID** | FT-0011 |
| **제목** | NAS JSON → Supabase 최적화 동기화 시스템 |
| **버전** | 1.1 |
| **작성일** | 2026-01-13 |
| **상태** | Draft |
| **상위 문서** | [FT-0010](./FT-0010-nas-smb-integration.md) |
| **관련 이슈** | TBD |

---

## 1. 개요

### 1.1 목적

NAS에 저장되는 PokerGFX JSON 파일을 Supabase로 동기화하는 **하이브리드 전송 시스템** 구현.
- **실시간 경로**: 새 파일 즉시 동기화 (지연 최소화)
- **배치 경로**: 수정/큐 처리 효율화 (6배 성능 향상)
- **네이티브 감지**: watchfiles (Rust 기반) 사용으로 폴링 제거

### 1.2 배경

| 문제 | 설명 |
|------|------|
| **현재 상황** | PollingObserver로 2초마다 폴링 |
| **성능 병목** | 폴링 방식으로 감지 지연 ~2초 + CPU 낭비 |
| **장애 복구** | 오프라인 큐 순차 처리로 비효율 |

### 1.3 목표

| 지표 | 현재 | 목표 |
|------|------|------|
| 파일 감지 지연 | ~2초 (폴링) | **~1ms** (네이티브) |
| 새 파일 동기화 | ~2.5초 | **~500ms** |
| 파일 수정 100건 | ~50초 | ~8초 (배치) |
| CPU 사용률 (감시) | 높음 | **최소** |

---

## 2. 아키텍처

### 2.1 배포 방식: GFX PC 직접 실행

**선택 이유**: NAS SMB 연결 문제 회피, 네트워크 지연 없음, 단순한 배포

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GFX PC (Windows)                            │
│                                                                     │
│  ┌─────────────┐          ┌─────────────────────────────────────┐  │
│  │  PokerGFX   │ ──JSON──>│         Sync Agent                  │  │
│  │ (GFX 소프트웨어)│          │  (PyInstaller EXE)                 │  │
│  └─────────────┘          └──────────────┬──────────────────────┘  │
│         │                                │                          │
│         ▼                                ▼                          │
│  C:\pokergfx\hands\      ┌────────────────────────────────────┐    │
│  (로컬 JSON 저장)         │  watchfiles (Rust/Notify 기반)     │    │
│                          │  - ReadDirectoryChangesW (Win32)   │    │
│                          │  - 즉시 감지 (~1ms)                 │    │
│                          │  - CPU 사용 최소                    │    │
│                          └──────────────┬─────────────────────┘    │
│                                         │                           │
│                          ┌──────────────┴──────────────┐           │
│                          │                             │           │
│                          ▼                             ▼           │
│               ┌──────────────────┐       ┌─────────────────┐       │
│               │  [실시간 경로]    │       │  [배치 경로]     │       │
│               │  Change.added    │       │  Change.modified│       │
│               │                  │       │  오프라인 큐     │       │
│               │  단건 Upsert     │       │  BatchQueue     │       │
│               │  (즉시 처리)     │       │  (500건/5초)    │       │
│               └────────┬─────────┘       └────────┬────────┘       │
│                        │                          │                │
│                        └────────────┬─────────────┘                │
│                                     │                               │
└─────────────────────────────────────┼───────────────────────────────┘
                                      │ HTTPS
                                      ▼
                         ┌─────────────────────────────┐
                         │         Supabase            │
                         │     gfx_sessions 테이블      │
                         │   (file_hash UNIQUE 제약)    │
                         └─────────────────────────────┘
```

### 2.2 파일 감시 방식 비교

| 항목 | PollingObserver (기존) | watchfiles (신규) |
|------|----------------------|-------------------|
| 감지 원리 | 주기적 디렉토리 스캔 | OS 네이티브 이벤트 |
| Windows API | - | ReadDirectoryChangesW |
| 감지 지연 | ~2초 | **~1ms** |
| CPU 사용 | 높음 | **최소** |
| 배터리 소모 | 높음 | **최소** |
| NAS/SMB 지원 | O | X (로컬만) |
| 구현 | Python | Rust (Notify) |

### 2.3 이벤트 라우팅

| watchfiles 이벤트 | 경로 | 처리 방식 | 지연 |
|------------------|------|----------|------|
| `Change.added` | 실시간 | 단건 Upsert | **즉시 (~1ms)** |
| `Change.modified` | 배치 | BatchQueue | 최대 5초 |
| 오프라인 큐 | 배치 | Batch Upsert | 50건 단위 |

### 2.4 Upsert vs Insert

| 방식 | 중복 처리 | 성능 |
|------|----------|------|
| `.insert()` | 에러 발생 → 예외 처리 필요 | 기본 |
| `.upsert(on_conflict)` | 자동 업데이트 | 동일 + 안전 |

**결론**: `.upsert(on_conflict="file_hash")` 사용

---

## 3. 요구사항

### 3.1 기능 요구사항

| ID | 요구사항 | 우선순위 |
|----|----------|----------|
| FR-01 | 새 파일(Change.added) 즉시 동기화 | **HIGH** |
| FR-02 | 수정 파일(Change.modified) 배치 처리 | HIGH |
| FR-03 | 오프라인 큐 배치 처리 | HIGH |
| FR-04 | 중복 파일 자동 처리 (upsert) | HIGH |
| FR-05 | 배치 크기 설정 가능 (기본 500) | MEDIUM |
| FR-06 | 배치 플러시 간격 설정 (기본 5초) | MEDIUM |
| FR-07 | **watchfiles 기반 네이티브 감지** | **HIGH** |

### 3.2 비기능 요구사항

| ID | 요구사항 | 목표 값 |
|----|----------|---------|
| NFR-01 | 파일 감지 지연 | **< 10ms** |
| NFR-02 | 새 파일 동기화 지연 | < 1초 |
| NFR-03 | 배치 처리 성능 향상 | 6배 이상 |
| NFR-04 | 메모리 사용량 (배치 큐) | < 50MB |
| NFR-05 | 장애 시 데이터 손실 | 0건 |
| NFR-06 | CPU 사용률 (파일 감시) | **< 1%** |

---

## 4. 상세 설계

### 4.1 watchfiles 기반 FileWatcher

```python
# src/sync_agent/file_watcher.py

import asyncio
import logging
from pathlib import Path
from typing import Callable, Coroutine, Any

from watchfiles import awatch, Change

logger = logging.getLogger(__name__)


class WatchfilesWatcher:
    """watchfiles 기반 파일 감시자.

    Rust(Notify) 기반으로 OS 네이티브 API 사용:
    - Windows: ReadDirectoryChangesW
    - Linux: inotify
    - macOS: FSEvents

    폴링 방식 대비:
    - 감지 지연: ~2초 → ~1ms
    - CPU 사용: 높음 → 최소
    """

    def __init__(
        self,
        watch_path: str,
        on_created: Callable[[str], Coroutine[Any, Any, None]],
        on_modified: Callable[[str], Coroutine[Any, Any, None]],
        file_pattern: str = "*.json",
    ) -> None:
        """초기화.

        Args:
            watch_path: 감시할 디렉토리 경로
            on_created: 파일 생성 시 콜백 (async)
            on_modified: 파일 수정 시 콜백 (async)
            file_pattern: 감시할 파일 패턴
        """
        self.watch_path = Path(watch_path)
        self.on_created = on_created
        self.on_modified = on_modified
        self.file_pattern = file_pattern
        self._running = False

    def _match_pattern(self, path: str) -> bool:
        """파일 패턴 매칭."""
        return Path(path).match(self.file_pattern)

    async def start(self) -> None:
        """파일 감시 시작."""
        self._running = True
        logger.info(f"watchfiles 감시 시작: {self.watch_path}")

        async for changes in awatch(self.watch_path, stop_event=self._stop_event):
            for change_type, path in changes:
                if not self._match_pattern(path):
                    continue

                try:
                    if change_type == Change.added:
                        logger.debug(f"파일 생성 감지: {path}")
                        await self.on_created(path)
                    elif change_type == Change.modified:
                        logger.debug(f"파일 수정 감지: {path}")
                        await self.on_modified(path)
                except Exception as e:
                    logger.error(f"이벤트 처리 실패 ({path}): {e}")

    async def stop(self) -> None:
        """파일 감시 중지."""
        self._running = False
        logger.info("watchfiles 감시 중지")

    @property
    def _stop_event(self) -> asyncio.Event:
        """중지 이벤트."""
        event = asyncio.Event()
        if not self._running:
            event.set()
        return event
```

### 4.2 BatchQueue 클래스

```python
# src/sync_agent/batch_queue.py

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BatchQueue:
    """배치 처리용 인메모리 큐.

    속성:
        max_size: 배치 최대 크기 (기본 500)
        flush_interval: 자동 플러시 간격 초 (기본 5.0)
    """

    max_size: int = 500
    flush_interval: float = 5.0
    _items: list[dict[str, Any]] = field(default_factory=list)
    _last_flush: float = field(default_factory=time.time)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def add(self, record: dict[str, Any]) -> list[dict[str, Any]] | None:
        """레코드 추가. 플러시 조건 충족 시 배치 반환."""
        async with self._lock:
            self._items.append(record)

            if len(self._items) >= self.max_size:
                return await self._flush_internal()

            if self._should_flush():
                return await self._flush_internal()

            return None

    def _should_flush(self) -> bool:
        """시간 기반 플러시 조건 확인."""
        return (
            len(self._items) > 0
            and (time.time() - self._last_flush) >= self.flush_interval
        )

    async def _flush_internal(self) -> list[dict[str, Any]]:
        """내부 플러시 (락 보유 상태)."""
        batch = self._items
        self._items = []
        self._last_flush = time.time()
        return batch

    async def flush(self) -> list[dict[str, Any]]:
        """강제 플러시."""
        async with self._lock:
            return await self._flush_internal()

    @property
    def pending_count(self) -> int:
        """대기 중인 레코드 수."""
        return len(self._items)
```

### 4.3 SyncAgent 메인 루프

```python
# src/sync_agent/main.py

import asyncio
import logging

from src.sync_agent.config import SyncAgentSettings
from src.sync_agent.file_watcher import WatchfilesWatcher
from src.sync_agent.sync_service import SyncService
from src.sync_agent.local_queue import LocalQueue

logger = logging.getLogger(__name__)


class SyncAgent:
    """GFX JSON → Supabase 동기화 에이전트."""

    def __init__(self, settings: SyncAgentSettings) -> None:
        self.settings = settings
        self.local_queue = LocalQueue(settings.queue_db_path)
        self.sync_service = SyncService(settings, self.local_queue)
        self.watcher: WatchfilesWatcher | None = None

    async def start(self) -> None:
        """에이전트 시작."""
        logger.info("SyncAgent 시작")

        # watchfiles 기반 파일 감시자 초기화
        self.watcher = WatchfilesWatcher(
            watch_path=self.settings.gfx_watch_path,
            on_created=self._handle_created,
            on_modified=self._handle_modified,
            file_pattern="*.json",
        )

        # 병렬 실행: 파일 감시 + 오프라인 큐 처리
        await asyncio.gather(
            self.watcher.start(),
            self._process_offline_queue_loop(),
        )

    async def _handle_created(self, path: str) -> None:
        """파일 생성 이벤트 처리 (실시간 경로)."""
        await self.sync_service.sync_file(path, "created")

    async def _handle_modified(self, path: str) -> None:
        """파일 수정 이벤트 처리 (배치 경로)."""
        await self.sync_service.sync_file(path, "modified")

    async def _process_offline_queue_loop(self) -> None:
        """오프라인 큐 주기적 처리."""
        while True:
            await asyncio.sleep(self.settings.queue_process_interval)
            await self.sync_service.process_offline_queue()

    async def stop(self) -> None:
        """에이전트 중지."""
        if self.watcher:
            await self.watcher.stop()

        # 배치 큐 플러시
        await self.sync_service.flush_batch_queue()
        logger.info("SyncAgent 중지")
```

### 4.4 설정 추가

```python
# src/sync_agent/config.py

class SyncAgentSettings(BaseSettings):
    # Supabase 연결
    supabase_url: str
    supabase_key: str

    # 감시 경로
    gfx_watch_path: str = "C:/GFX/output"

    # 배치 처리 설정
    batch_size: int = 500
    flush_interval: float = 5.0

    # 오프라인 큐
    queue_db_path: str = "C:/GFX/sync_queue/pending.db"
    queue_process_interval: int = 60
    max_retries: int = 5
```

---

## 5. 데이터베이스

### 5.1 Supabase 테이블

```sql
-- gfx_sessions 테이블 (기존)
CREATE TABLE gfx_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,  -- Upsert 충돌 키
    raw_json JSONB NOT NULL,
    table_type TEXT,
    event_title TEXT,
    software_version TEXT,
    hand_count INTEGER DEFAULT 0,
    session_created_at TIMESTAMPTZ,
    sync_source TEXT DEFAULT 'gfx_pc_direct',
    sync_status TEXT DEFAULT 'synced',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- file_hash 인덱스 (upsert 성능)
CREATE UNIQUE INDEX idx_gfx_sessions_file_hash ON gfx_sessions(file_hash);
```

---

## 6. 오프라인 큐 설명

### 6.1 필요 시나리오

| 장애 유형 | 처리 방식 |
|----------|----------|
| 네트워크 일시 단절 | LocalQueue 저장 → 자동 재시도 |
| Supabase 503 에러 | LocalQueue 저장 → 복구 후 배치 처리 |
| GFX PC 재부팅 | 미처리 파일 스캔 → 배치 처리 |
| 장시간 오프라인 | LocalQueue 누적 → 복구 후 일괄 처리 |

---

## 7. 구현 계획

### 7.1 파일 변경 목록

| 파일 | 작업 | 우선순위 |
|------|------|----------|
| `src/sync_agent/file_watcher.py` | **신규 생성** (watchfiles) | **HIGH** |
| `src/sync_agent/batch_queue.py` | 신규 생성 | HIGH |
| `src/sync_agent/sync_service.py` | 수정 (하이브리드 로직) | HIGH |
| `src/sync_agent/main.py` | 수정 (watchfiles 통합) | HIGH |
| `src/sync_agent/config.py` | 설정 추가 | HIGH |
| `requirements.txt` | **watchfiles 추가** | HIGH |
| `tests/test_file_watcher.py` | **신규 생성** | HIGH |
| `tests/test_batch_queue.py` | 신규 생성 | HIGH |

### 7.2 의존성 추가

```txt
# requirements.txt
watchfiles>=0.21.0  # Rust 기반 파일 감시
supabase>=2.0.0
pydantic-settings>=2.0.0
```

---

## 8. 검증 계획

### 8.1 성능 벤치마크

| 시나리오 | 측정 방법 | 목표 |
|----------|----------|------|
| 파일 감지 지연 | 파일 생성 → 이벤트 수신 시간 | **< 10ms** |
| 실시간 1건 | 감지 → Supabase 완료 | < 1초 |
| 배치 500건 | 배치 upsert 지연 | < 10초 |
| 큐 1000건 | 복구 처리 시간 | < 60초 |
| CPU 사용률 | idle 상태 감시 중 | **< 1%** |

### 8.2 watchfiles vs PollingObserver 비교 테스트

```python
# tests/test_file_watcher_performance.py

import time
import asyncio
from pathlib import Path

async def test_watchfiles_detection_latency():
    """watchfiles 감지 지연 측정."""
    detected = asyncio.Event()
    detection_time = None

    async def on_created(path: str):
        nonlocal detection_time
        detection_time = time.perf_counter()
        detected.set()

    watcher = WatchfilesWatcher(
        watch_path="./test_dir",
        on_created=on_created,
        on_modified=lambda p: None,
    )

    # 백그라운드에서 감시 시작
    watch_task = asyncio.create_task(watcher.start())

    await asyncio.sleep(0.1)  # 감시 시작 대기

    # 파일 생성 및 시간 측정
    start_time = time.perf_counter()
    Path("./test_dir/test.json").write_text("{}")

    await asyncio.wait_for(detected.wait(), timeout=5.0)

    latency_ms = (detection_time - start_time) * 1000
    assert latency_ms < 100  # 100ms 이내 감지
```

---

## 9. 참조

### 9.1 웹 리서치 출처

- [watchfiles - GitHub](https://github.com/samuelcolvin/watchfiles)
- [watchfiles Documentation](https://watchfiles.helpmanual.io/)
- [Best Practices for Inserting Large Number of Rows](https://github.com/orgs/supabase/discussions/11349)
- [Speeding Up Bulk Loading in PostgreSQL](https://dev.to/supabase/speeding-up-bulk-loading-in-postgresql-41g5)
- [Python: Upsert data - Supabase Docs](https://supabase.com/docs/reference/python/upsert)

### 9.2 관련 문서

| 문서 | 설명 |
|------|------|
| [FT-0010](./FT-0010-nas-smb-integration.md) | NAS SMB 통합 |
| [FT-0002](./FT-0002-primary-gfx-rfid.md) | Primary Layer - GFX RFID |

---

## 10. NAS 중앙 통제 아키텍처 (v2.0)

### 10.1 개요

기존 GFX PC별 개별 Agent 방식에서 **NAS 중앙 통제 방식**으로 전면 재설계.

| 항목 | 기존 (v1.x) | 변경 (v2.0) |
|------|-------------|-------------|
| Agent 위치 | 각 GFX PC | NAS (단일) |
| 파일 감시 | watchfiles (로컬) | PollingObserver (SMB) |
| 관리 포인트 | N개 PC | 1개 NAS |
| 모니터링 | 없음 | Next.js 대시보드 |
| 배포 | PyInstaller EXE | Docker Container |

### 10.2 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           GFX PC Layer                                   │
│                                                                          │
│   GFX PC 1        GFX PC 2        GFX PC N                              │
│   (PokerGFX)      (PokerGFX)      (PokerGFX)                            │
│       │               │               │                                  │
│       └───────────────┼───────────────┘                                  │
│                       │ SMB Write                                        │
└───────────────────────┼──────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       NAS Storage Layer                                  │
│   \\NAS\gfx_data\                                                        │
│   ├── config/pc_registry.json    ← PC 등록 정보                         │
│   ├── PC01/hands/                ← GFX PC 1 전용                        │
│   ├── PC02/hands/                ← GFX PC 2 전용                        │
│   └── _error/                    ← 파싱 실패 파일 격리                   │
└───────────────────────┼──────────────────────────────────────────────────┘
                        │ Docker Volume Mount
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   NAS Docker Container Layer                             │
│                                                                          │
│   ┌─────────────────────────────────┐  ┌────────────────────────────┐   │
│   │   Central Sync Agent (Python)   │  │  Next.js Dashboard         │   │
│   │                                 │  │  (Port 3000)               │   │
│   │   - MultiPathWatcher            │  │                            │   │
│   │   - CentralSyncService          │  │  - 실시간 현황             │   │
│   │   - BatchQueue (500건/5초)      │  │  - PC별 상태               │   │
│   │   - LocalQueue (SQLite)         │  │  - 오류 목록               │   │
│   └───────────────┬─────────────────┘  └─────────────┬──────────────┘   │
│                   │                                  │                   │
└───────────────────┼──────────────────────────────────┼───────────────────┘
                    │ HTTPS                            │ Realtime
                    ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Supabase Cloud                                  │
│                                                                          │
│   ┌─────────────────────────┐  ┌─────────────────────────────────────┐  │
│   │   gfx_sessions 테이블   │  │      sync_events 테이블            │  │
│   │                         │  │      (Realtime 활성화)             │  │
│   │   + gfx_pc_id 컬럼      │  │                                     │  │
│   │   UNIQUE(gfx_pc_id,     │  │   → Next.js 대시보드 실시간 업데이트│  │
│   │          file_hash)     │  │                                     │  │
│   └─────────────────────────┘  └─────────────────────────────────────┘  │
│                                                                          │
│   ┌─────────────────────────┐  ┌─────────────────────────────────────┐  │
│   │   pc_status 뷰         │  │      sync_stats 뷰                  │  │
│   │   (PC별 상태 집계)      │  │      (전체 통계)                    │  │
│   └─────────────────────────┘  └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 10.3 주요 파일

| 파일 | 설명 |
|------|------|
| `src/sync_agent/multi_path_watcher.py` | 다중 SMB 경로 감시 (watchdog) |
| `src/sync_agent/config.py` | CentralSyncSettings 클래스 |
| `src/sync_agent/sync_service.py` | CentralSyncService (gfx_pc_id 지원) |
| `src/sync_agent/main.py` | CentralSyncAgent 클래스, `--central` 모드 |
| `migrations/001_nas_central.sql` | Supabase 테이블 마이그레이션 |
| `docker-compose.yml` | Docker 배포 설정 |
| `dashboard/` | Next.js 웹 대시보드 |

### 10.4 실행 방법

```bash
# 1. Supabase 마이그레이션 실행
# Supabase SQL Editor에서 migrations/001_nas_central.sql 실행

# 2. .env 파일 설정
cp .env.example .env
# SUPABASE_URL, SUPABASE_SERVICE_KEY 등 설정

# 3. Docker Compose 실행
docker-compose up -d

# 4. 대시보드 접속
# http://localhost:3000
```

---

## 11. 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-01-13 | 초안 작성 | Claude |
| 1.1 | 2026-01-13 | watchfiles 기반으로 변경 (PollingObserver → Rust/Notify) | Claude |
| 2.0 | 2026-01-13 | NAS 중앙 통제 방식 재설계, GUI 대시보드 추가 | Claude |
