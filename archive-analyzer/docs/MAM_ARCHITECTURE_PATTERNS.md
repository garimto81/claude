# MAM 시스템 아키텍처 패턴 조사

**작성일**: 2025-12-01
**대상**: Archive Analyzer 확장을 위한 Self-hosted MAM 시스템 아키텍처

---

## 1. 일반적인 MAM 시스템 아키텍처

### 1.1 컴포넌트 구성

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                            │
│  (Web UI, Mobile App, Desktop Client)                       │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API / GraphQL
┌──────────────────▼──────────────────────────────────────────┐
│                   API Gateway Layer                          │
│  (Auth, Rate Limiting, Request Routing)                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴───────────┬─────────────┐
        │                      │             │
┌───────▼──────┐   ┌──────────▼────┐   ┌───▼──────────┐
│ Metadata     │   │ Transcoding   │   │ Search       │
│ Service      │   │ Service       │   │ Service      │
│              │   │               │   │              │
│ - 파일 스캔   │   │ - FFmpeg 워커 │   │ - Indexing   │
│ - 메타 추출   │   │ - HLS/DASH    │   │ - Full-text  │
│ - DB 저장     │   │ - 썸네일 생성 │   │ - Faceted    │
└───────┬──────┘   └───────┬───────┘   └───┬──────────┘
        │                  │               │
        │         ┌────────▼───────────────▼─────┐
        │         │   Message Queue (RabbitMQ)   │
        │         │   - 비동기 작업 큐            │
        │         │   - 작업 우선순위 관리        │
        │         └──────────────────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────┐
│                   Data Layer                                  │
├───────────────────┬─────────────────┬────────────────────────┤
│ PostgreSQL        │ Elasticsearch   │ Object Storage         │
│ - 구조화 메타데이터│ - 전문 검색      │ - MinIO/S3            │
│ - 관계형 데이터    │ - 로그 분석      │ - 원본 미디어 파일    │
│ - 트랜잭션         │ - 집계 쿼리      │ - 트랜스코딩 결과     │
└───────────────────┴─────────────────┴────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────────┐
│                 File Storage Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ NAS/SMB  │  │ Local FS │  │ Cloud    │                 │
│  │ (원본)    │  │ (캐시)    │  │ (백업)   │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└────────────────────────────────────────────────────────────┘
```

### 1.2 데이터 흐름

#### A. 파일 인제스트 (Ingest)
```
1. 파일 감지
   NAS/SMB → Watcher Service (inotify/polling)

2. 메타데이터 추출
   → 파일 큐 등록 (RabbitMQ)
   → FFprobe Worker 실행
   → 메타데이터 DB 저장 (PostgreSQL)
   → 검색 인덱스 업데이트 (Elasticsearch)

3. 썸네일/프록시 생성
   → 트랜스코딩 큐 등록
   → FFmpeg Worker 실행
   → MinIO/S3에 결과 저장

4. 검색 가능 상태
   → 클라이언트에서 검색/스트리밍 가능
```

#### B. 검색 및 재생
```
1. 사용자 검색
   Client → API Gateway → Search Service
   → Elasticsearch 쿼리 (전문 검색, 필터)
   → PostgreSQL 조인 (관계형 데이터)
   → 검색 결과 반환

2. 미디어 스트리밍
   Client → API Gateway → Streaming Service
   → MinIO/S3에서 HLS 세그먼트 조회
   → CDN 캐싱 (선택)
   → 클라이언트 재생
```

### 1.3 스토리지 계층 구조

| 계층 | 용도 | 기술 스택 | 특징 |
|------|------|-----------|------|
| **Hot Storage** | 자주 접근하는 파일 | Local SSD, Redis | 빠른 접근, 고비용 |
| **Warm Storage** | 중간 사용률 파일 | NAS, MinIO | 적정 속도, 중간 비용 |
| **Cold Storage** | 아카이브 (원본) | Tape, Glacier | 느린 접근, 저비용 |
| **Cache** | 프록시/썸네일 | Local FS, CDN | 임시 저장, 빠른 조회 |

---

## 2. 주요 기술 스택 조합

### 2.1 메타데이터 저장

#### A. PostgreSQL (추천: 구조화 데이터)

**장점**:
- ACID 트랜잭션 보장
- 복잡한 조인/관계 쿼리 지원
- JSON/JSONB 컬럼으로 유연성 확보
- 성숙한 에코시스템

**스키마 예시**:
```sql
-- 파일 메타데이터
CREATE TABLE media_files (
    id BIGSERIAL PRIMARY KEY,
    file_path TEXT UNIQUE NOT NULL,
    file_hash VARCHAR(64),
    file_size BIGINT,
    mime_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_path_hash (file_hash),
    INDEX idx_created (created_at DESC)
);

-- 비디오 메타데이터
CREATE TABLE video_metadata (
    id BIGSERIAL PRIMARY KEY,
    file_id BIGINT REFERENCES media_files(id) ON DELETE CASCADE,
    codec VARCHAR(50),
    width INT,
    height INT,
    duration_sec DECIMAL(10,3),
    bitrate_kbps INT,
    framerate DECIMAL(6,3),
    container VARCHAR(50),
    -- JSONB로 추가 메타데이터 저장
    extra_metadata JSONB,
    INDEX idx_resolution (width, height),
    INDEX idx_codec (codec)
);

-- 태그 (다대다)
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE file_tags (
    file_id BIGINT REFERENCES media_files(id),
    tag_id INT REFERENCES tags(id),
    PRIMARY KEY (file_id, tag_id)
);

-- 컬렉션 (프로젝트/시리즈)
CREATE TABLE collections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_id INT REFERENCES collections(id)
);

CREATE TABLE collection_files (
    collection_id INT REFERENCES collections(id),
    file_id BIGINT REFERENCES media_files(id),
    sort_order INT,
    PRIMARY KEY (collection_id, file_id)
);
```

**확장성**:
- Read Replica (읽기 부하 분산)
- Partitioning (시간/카테고리별 파티션)
- Connection Pooling (PgBouncer)

#### B. Elasticsearch (추천: 검색)

**장점**:
- 강력한 전문 검색 (Full-text search)
- Faceted search (필터링, 집계)
- Near real-time 인덱싱
- 수평 확장 용이

**인덱스 설계**:
```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "media_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "file_id": { "type": "keyword" },
      "file_path": { "type": "text", "fields": { "keyword": { "type": "keyword" } } },
      "filename": { "type": "text", "analyzer": "media_analyzer" },
      "description": { "type": "text", "analyzer": "media_analyzer" },
      "tags": { "type": "keyword" },
      "codec": { "type": "keyword" },
      "resolution": { "type": "keyword" },
      "duration_sec": { "type": "integer" },
      "created_at": { "type": "date" },
      "metadata": { "type": "object", "enabled": false }
    }
  }
}
```

**쿼리 예시**:
```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "filename": "WSOP 2023" } }
      ],
      "filter": [
        { "term": { "codec": "h264" } },
        { "range": { "duration_sec": { "gte": 3600 } } }
      ]
    }
  },
  "aggs": {
    "by_resolution": { "terms": { "field": "resolution" } },
    "by_codec": { "terms": { "field": "codec" } }
  }
}
```

#### C. MongoDB (대안: 스키마 유연성)

**적합 케이스**:
- 스키마가 자주 변하는 경우
- 중첩된 문서 구조 선호
- 샤딩이 필요한 대용량 데이터

**단점**:
- 복잡한 조인 성능 낮음
- 트랜잭션 지원 제한적 (4.0 이상 개선)

### 2.2 파일 스토리지

#### A. MinIO (추천: Self-hosted S3)

**장점**:
- S3 호환 API
- On-premise 배포 가능
- Erasure Coding (데이터 보호)
- 수평 확장 용이

**구성**:
```yaml
# docker-compose.yml
services:
  minio1:
    image: minio/minio
    command: server http://minio{1...4}/data{1...2} --console-address ":9001"
    volumes:
      - /mnt/storage1:/data1
      - /mnt/storage2:/data2
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}

  # minio2, minio3, minio4 동일 설정
```

**버킷 정책**:
- `raw-media`: 원본 파일 (Write Once, Read Many)
- `proxies`: 프록시/트랜스코딩 결과 (TTL 설정)
- `thumbnails`: 썸네일 (캐시, CDN 연동)

#### B. NAS/SMB (현재 사용 중)

**현재 구성**:
- Synology NAS (10.10.100.122)
- SMB 2/3 프로토콜
- 18TB+ 스토리지

**개선 방안**:
- NFS 마운트 (SMB보다 성능 우수)
- iSCSI 블록 스토리지 (DB용)
- NAS를 Cold Storage로 전환, Hot Storage는 별도 구성

### 2.3 트랜스코딩

#### A. FFmpeg (현재 사용 중)

**최적화**:
```python
# HLS 트랜스코딩 (멀티 비트레이트)
ffmpeg -i input.mp4 \
  -c:v libx264 -preset fast -crf 22 \
  -c:a aac -b:a 128k \
  -f hls -hls_time 6 -hls_playlist_type vod \
  -master_pl_name master.m3u8 \
  -var_stream_map "v:0,a:0 v:1,a:1 v:2,a:2" \
  -hls_segment_filename "stream_%v/seg_%03d.ts" \
  stream_%v.m3u8

# 1080p
-s 1920x1080 -b:v 5000k
# 720p
-s 1280x720 -b:v 2800k
# 480p
-s 854x480 -b:v 1400k
```

**병렬 처리**:
```python
# Celery 워커 구성
@celery.task
def transcode_video(file_id, preset):
    file = db.get_file(file_id)
    output_path = f"/tmp/transcode_{file_id}_{preset}.mp4"

    # FFmpeg 실행
    subprocess.run([
        'ffmpeg', '-i', file.path,
        '-preset', preset,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_path
    ])

    # MinIO 업로드
    minio.upload_file('proxies', output_path, f"{file_id}/{preset}.mp4")

    # 메타데이터 업데이트
    db.update_file_proxy(file_id, preset, output_path)
```

#### B. AWS MediaConvert (클라우드 대안)

**장점**:
- 관리형 서비스, 인프라 불필요
- 자동 스케일링
- 다양한 프리셋

**단점**:
- 비용 (분당 과금)
- 클라우드 종속

### 2.4 검색 엔진 비교

| 항목 | Elasticsearch | MeiliSearch | Typesense |
|------|---------------|-------------|-----------|
| **성능** | 우수 | 매우 빠름 | 매우 빠름 |
| **설정 복잡도** | 높음 | 낮음 | 낮음 |
| **메모리 사용** | 높음 | 중간 | 낮음 |
| **확장성** | 클러스터 지원 | 단일 노드 중심 | 클러스터 지원 |
| **쿼리 기능** | 매우 강력 | 기본적 | 강력 |
| **타이포 허용** | 플러그인 | 내장 | 내장 |
| **추천 용도** | 대규모, 복잡한 쿼리 | 중소규모, 빠른 검색 | 중소규모, 타이포 허용 |

**Archive Analyzer 추천**: **MeiliSearch**
- 설정 간단 (단일 바이너리)
- 타이포 허용 검색 (파일명 오타 대응)
- 한글 검색 지원
- 메모리 효율적

---

## 3. 확장성 고려사항

### 3.1 10TB+ 규모 처리

#### A. 파일 인덱싱 전략

**1. 점진적 스캔 (Incremental Scan)**
```python
# 체크포인트 기반 재개 (현재 구현)
checkpoint = db.get_checkpoint(scan_id)
if checkpoint:
    resume_from = checkpoint.last_path
```

**2. 병렬 스캔 (Parallel Scanning)**
```python
# 폴더별 병렬 워커
from concurrent.futures import ThreadPoolExecutor

def scan_folder(folder_path):
    scanner = ArchiveScanner(connector, db, folder_path)
    return scanner.scan()

with ThreadPoolExecutor(max_workers=4) as executor:
    folders = ['/WSOP', '/HCL', '/PAD', '/Other']
    futures = [executor.submit(scan_folder, f) for f in folders]
    results = [f.result() for f in futures]
```

**3. 메타데이터 추출 우선순위**
```python
# 우선순위 큐
priority_queue = {
    'high': [],    # 최근 파일, 자주 조회
    'medium': [],  # 일반 파일
    'low': []      # 아카이브 파일
}

# Celery 우선순위 설정
@celery.task(priority=9)  # high
def extract_metadata_high(file_id):
    pass

@celery.task(priority=5)  # medium
def extract_metadata_medium(file_id):
    pass
```

#### B. 데이터베이스 샤딩

**수평 파티셔닝 (Sharding)**:
```sql
-- 연도별 파티션 (PostgreSQL)
CREATE TABLE media_files (
    id BIGSERIAL,
    file_path TEXT,
    created_year INT,
    ...
) PARTITION BY RANGE (created_year);

CREATE TABLE media_files_2020 PARTITION OF media_files
    FOR VALUES FROM (2020) TO (2021);

CREATE TABLE media_files_2021 PARTITION OF media_files
    FOR VALUES FROM (2021) TO (2022);
```

**샤드 키 선택**:
- 시간 기반: `created_at` (아카이브 특성상 적합)
- 카테고리 기반: `project_name` (WSOP, HCL, PAD 등)
- 해시 기반: `file_hash` (균등 분산)

#### C. 캐싱 전략

**1. 애플리케이션 레벨 캐시 (Redis)**
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def get_file_metadata(file_id):
    # 캐시 조회
    cached = r.get(f"file:{file_id}")
    if cached:
        return json.loads(cached)

    # DB 조회
    metadata = db.get_media_info(file_id)

    # 캐시 저장 (1시간 TTL)
    r.setex(f"file:{file_id}", 3600, json.dumps(metadata))
    return metadata
```

**2. 쿼리 결과 캐싱**
```python
# 검색 결과 캐싱 (자주 조회되는 쿼리)
def search_files(query, filters):
    cache_key = f"search:{hash(query)}:{hash(filters)}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    results = elasticsearch.search(query, filters)
    r.setex(cache_key, 600, json.dumps(results))  # 10분 TTL
    return results
```

**3. CDN 캐싱 (썸네일/프록시)**
- CloudFlare, Fastly 등 CDN 사용
- MinIO에서 직접 서빙 시 Nginx 캐싱

### 3.2 동시 사용자 지원

#### A. API 성능 최적화

**1. 비동기 처리 (FastAPI 예시)**
```python
from fastapi import FastAPI
from databases import Database

app = FastAPI()
database = Database("postgresql://...")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.get("/files/{file_id}")
async def get_file(file_id: int):
    query = "SELECT * FROM media_files WHERE id = :file_id"
    result = await database.fetch_one(query=query, values={"file_id": file_id})
    return result

@app.get("/search")
async def search(q: str, limit: int = 20):
    # Elasticsearch 비동기 쿼리
    results = await es_client.search(index="media", body={
        "query": {"match": {"filename": q}},
        "size": limit
    })
    return results['hits']['hits']
```

**2. Rate Limiting**
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.get("/api/files", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def list_files():
    # 분당 10회 제한
    pass
```

**3. Connection Pooling**
```python
# PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://...",
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True  # 연결 상태 확인
)
```

#### B. 로드 밸런싱

**Nginx 설정**:
```nginx
upstream api_backend {
    least_conn;  # 최소 연결 방식
    server api1.local:8000 weight=1;
    server api2.local:8000 weight=1;
    server api3.local:8000 weight=2;  # 더 높은 스펙
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # 캐싱
        proxy_cache api_cache;
        proxy_cache_valid 200 10m;
    }
}
```

---

## 4. NAS/SMB 연동 패턴

### 4.1 파일 인덱싱 전략

#### A. Polling 방식 (현재 구현)

**장점**:
- 간단한 구현
- SMB 프로토콜만 필요
- 안정적

**단점**:
- 실시간성 부족
- 네트워크 부하

**최적화**:
```python
# 변경 감지 최적화 (modified_at 기반)
def incremental_scan(last_scan_time):
    for file_info in connector.scan_directory(recursive=True):
        if file_info.modified_time > last_scan_time:
            # 신규/변경 파일만 처리
            process_file(file_info)
```

#### B. Webhook 방식 (NAS 지원 시)

**Synology NAS 예시**:
```bash
# DSM 파일 이벤트 스크립트
# /usr/local/etc/rc.d/file-watcher.sh

inotifywait -m -r /volume1/ARCHIVE -e create,modify,delete |
while read path action file; do
    curl -X POST http://api.local/webhook/file-event \
         -H "Content-Type: application/json" \
         -d "{\"action\": \"$action\", \"path\": \"$path/$file\"}"
done
```

**API 수신**:
```python
@app.post("/webhook/file-event")
async def handle_file_event(event: FileEvent):
    if event.action == "create":
        # 비동기 메타데이터 추출 작업 등록
        celery.send_task('extract_metadata', args=[event.path])
    elif event.action == "delete":
        db.mark_file_deleted(event.path)
    return {"status": "ok"}
```

#### C. 하이브리드 방식 (추천)

```python
# 1. 주기적 전체 스캔 (매일 새벽 2시)
@scheduler.scheduled_job('cron', hour=2)
def full_scan():
    scanner.scan(count_first=True)

# 2. 실시간 변경 감지 (Webhook)
@app.post("/webhook/file-event")
async def handle_event(event):
    celery.send_task('process_file_change', args=[event])

# 3. 캐시된 파일 목록 사용 (API 조회)
def get_file_list(folder):
    cached = redis.get(f"folder:{folder}:files")
    if cached:
        return json.loads(cached)

    files = connector.list_directory(folder)
    redis.setex(f"folder:{folder}:files", 300, json.dumps(files))
    return files
```

### 4.2 실시간 동기화 방법

#### A. 변경 감지 프로토콜

**SMB Change Notify** (Windows 전용):
```python
# pysmb 라이브러리 사용
from smb.SMBConnection import SMBConnection

conn = SMBConnection(username, password, "client", "server")
conn.connect(server_ip, 445)

# 변경 감지 시작
conn.notifyChange(service_name, path, FILE_NOTIFY_CHANGE_FILE_NAME)
```

**한계**:
- Linux/Samba 서버에서 지원 제한적
- 장기 연결 유지 필요

#### B. Database Trigger 방식

**NAS DB 직접 연동** (가능한 경우):
```sql
-- PostgreSQL Trigger 예시
CREATE OR REPLACE FUNCTION notify_file_change()
RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('file_changes', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER file_change_trigger
AFTER INSERT OR UPDATE ON nas_files
FOR EACH ROW EXECUTE FUNCTION notify_file_change();
```

**Python 리스너**:
```python
import psycopg2
import select

conn = psycopg2.connect("dbname=nas user=postgres")
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
curs = conn.cursor()
curs.execute("LISTEN file_changes;")

while True:
    if select.select([conn], [], [], 5) == ([], [], []):
        continue
    conn.poll()
    while conn.notifies:
        notify = conn.notifies.pop(0)
        print(f"Notification: {notify.payload}")
        # 파일 변경 처리
        handle_file_change(json.loads(notify.payload))
```

### 4.3 성능 최적화

#### A. SMB 연결 풀링

```python
from queue import Queue
import threading

class SMBConnectionPool:
    def __init__(self, config, pool_size=5):
        self.config = config
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            conn = SMBConnector(config)
            conn.connect()
            self.pool.put(conn)

    def get_connection(self):
        return self.pool.get()

    def return_connection(self, conn):
        self.pool.put(conn)

    @contextmanager
    def connection(self):
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.return_connection(conn)

# 사용
pool = SMBConnectionPool(smb_config, pool_size=10)

with pool.connection() as conn:
    files = conn.list_directory("/ARCHIVE")
```

#### B. 청크 다운로드 (대용량 파일)

```python
def download_file_chunked(smb_path, local_path, chunk_size=1024*1024):
    """1MB 단위로 분할 다운로드"""
    with connector.open_file(smb_path, 'rb') as smb_file, \
         open(local_path, 'wb') as local_file:
        while True:
            chunk = smb_file.read(chunk_size)
            if not chunk:
                break
            local_file.write(chunk)
            # 진행률 표시
            print(f"Downloaded {local_file.tell():,} bytes")
```

#### C. 병렬 다운로드 (여러 파일)

```python
from concurrent.futures import ThreadPoolExecutor

def download_files_parallel(file_list, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_file, file_path)
            for file_path in file_list
        ]
        results = [f.result() for f in futures]
    return results
```

---

## 5. 현재 Archive Analyzer 확장 권장사항

### 5.1 단계별 마이그레이션 계획

#### Phase 1: 데이터베이스 업그레이드 (3개월)

**현재**: SQLite (archive.db)
**목표**: PostgreSQL + Redis

**마이그레이션**:
```python
# 1. PostgreSQL 스키마 생성
# 2. SQLite → PostgreSQL 데이터 이관
import sqlite3
import psycopg2

sqlite_conn = sqlite3.connect('archive.db')
pg_conn = psycopg2.connect("postgresql://...")

# 데이터 복사
cursor = sqlite_conn.cursor()
cursor.execute("SELECT * FROM files")
for row in cursor.fetchall():
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute(
        "INSERT INTO media_files (path, filename, ...) VALUES (%s, %s, ...)",
        row
    )
pg_conn.commit()
```

**추가 기능**:
- Full-text search (PostgreSQL `tsvector`)
- 사용자 관리 (users, permissions 테이블)
- 컬렉션/프로젝트 관리

#### Phase 2: 검색 엔진 도입 (2개월)

**선택**: MeiliSearch

**구성**:
```bash
# Docker로 실행
docker run -d \
  --name meilisearch \
  -p 7700:7700 \
  -v /var/meilisearch:/meili_data \
  getmeili/meilisearch:latest
```

**인덱스 생성**:
```python
import meilisearch

client = meilisearch.Client('http://localhost:7700', 'masterKey')

# 인덱스 생성
index = client.index('media_files')

# 문서 추가
documents = [
    {
        'id': 1,
        'filename': 'WSOP_2023_Main_Event_Day1.mp4',
        'path': '/ARCHIVE/WSOP/2023/Main_Event_Day1.mp4',
        'codec': 'h264',
        'resolution': '1080p',
        'tags': ['WSOP', '2023', 'Main Event']
    }
]
index.add_documents(documents)

# 검색
results = index.search('WSOP 2023', {
    'filter': 'codec = h264',
    'limit': 20
})
```

#### Phase 3: API 서버 구축 (3개월)

**FastAPI 기반 REST API**:

```python
# api/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

app = FastAPI(title="Archive Analyzer API")

@app.get("/api/v1/files")
async def list_files(
    limit: int = 20,
    offset: int = 0,
    file_type: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(MediaFile)
    if file_type:
        query = query.filter(MediaFile.file_type == file_type)
    files = query.offset(offset).limit(limit).all()
    return {"total": query.count(), "items": files}

@app.get("/api/v1/files/{file_id}")
async def get_file(file_id: int, db: Session = Depends(get_db)):
    file = db.query(MediaFile).filter(MediaFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@app.get("/api/v1/search")
async def search_files(q: str, limit: int = 20):
    results = meilisearch.index('media_files').search(q, {'limit': limit})
    return results

@app.post("/api/v1/scan/trigger")
async def trigger_scan(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_full_scan)
    return {"status": "scan started"}
```

**인증/권한**:
```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload

@app.get("/api/v1/admin/stats", dependencies=[Depends(verify_token)])
async def get_stats():
    # 관리자 전용 엔드포인트
    pass
```

#### Phase 4: 웹 UI 구축 (4개월)

**기술 스택**:
- Frontend: Next.js (React) + TailwindCSS
- Video Player: Video.js / HLS.js
- State Management: Zustand / Tanstack Query

**주요 페이지**:
1. 검색 페이지 (전문 검색, 필터링)
2. 파일 상세 페이지 (메타데이터, 미리보기)
3. 컬렉션 관리
4. 관리자 대시보드 (스캔 상태, 통계)

**예시 컴포넌트**:
```tsx
// components/FileGrid.tsx
export function FileGrid({ files }: { files: MediaFile[] }) {
  return (
    <div className="grid grid-cols-4 gap-4">
      {files.map(file => (
        <FileCard key={file.id} file={file} />
      ))}
    </div>
  );
}

// components/FileCard.tsx
export function FileCard({ file }: { file: MediaFile }) {
  return (
    <div className="border rounded-lg p-4">
      <img src={file.thumbnail_url} alt={file.filename} />
      <h3>{file.filename}</h3>
      <p>{file.resolution} | {file.codec}</p>
      <p>{formatDuration(file.duration_seconds)}</p>
    </div>
  );
}
```

#### Phase 5: 스트리밍 최적화 (3개월)

**MinIO 도입**:
```bash
# MinIO 설치
docker run -d \
  -p 9000:9000 -p 9001:9001 \
  --name minio \
  -v /mnt/storage/minio:/data \
  minio/minio server /data --console-address ":9001"
```

**HLS 트랜스코딩**:
```python
# Celery 워커
@celery.task
def create_hls_stream(file_id):
    file = db.get_file(file_id)
    output_dir = f"/tmp/hls_{file_id}"
    os.makedirs(output_dir, exist_ok=True)

    # FFmpeg HLS 생성
    subprocess.run([
        'ffmpeg', '-i', file.path,
        '-c:v', 'libx264', '-c:a', 'aac',
        '-hls_time', '6',
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', f"{output_dir}/seg_%03d.ts",
        f"{output_dir}/playlist.m3u8"
    ])

    # MinIO 업로드
    for ts_file in glob.glob(f"{output_dir}/*.ts"):
        minio_client.fput_object(
            'streams', f"{file_id}/{os.path.basename(ts_file)}", ts_file
        )
    minio_client.fput_object(
        'streams', f"{file_id}/playlist.m3u8", f"{output_dir}/playlist.m3u8"
    )

    # DB 업데이트
    db.update_file_stream_url(file_id, f"http://minio:9000/streams/{file_id}/playlist.m3u8")
```

### 5.2 권장 아키텍처 (최종 목표)

```
┌─────────────────────────────────────────────────────────────┐
│                     Web UI (Next.js)                         │
│  - 검색/필터링                                                │
│  - 미디어 플레이어 (HLS.js)                                   │
│  - 컬렉션 관리                                                │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/WebSocket
┌──────────────────▼──────────────────────────────────────────┐
│              API Server (FastAPI)                            │
│  - REST API (/api/v1/*)                                      │
│  - WebSocket (실시간 스캔 진행률)                             │
│  - JWT 인증                                                   │
└────┬────────────┬────────────────┬─────────────────────┬────┘
     │            │                │                     │
┌────▼────┐ ┌────▼─────┐ ┌────────▼──────┐ ┌──────────▼─────┐
│PostgreSQL│ │MeiliSearch│ │ Redis (Cache) │ │ Celery Workers │
│- 메타데이터│ │- 전문검색  │ │- Session      │ │- 스캔          │
│- 관계데이터│ │- 집계     │ │- 쿼리 캐시     │ │- 트랜스코딩    │
└────┬────┘ └──────────┘ └───────────────┘ └────────┬───────┘
     │                                                │
┌────▼────────────────────────────────────────────────▼───────┐
│                  Storage Layer                               │
├─────────────────┬────────────────────┬───────────────────────┤
│ NAS/SMB         │ MinIO (S3)         │ Local Cache          │
│ (원본 파일)      │ (HLS 스트림)        │ (임시 다운로드)       │
│ 18TB+           │ 프록시/썸네일        │                      │
└─────────────────┴────────────────────┴───────────────────────┘
```

### 5.3 기술 스택 요약

| 계층 | 현재 (v0.2.0) | 권장 (v1.0) |
|------|---------------|-------------|
| **Database** | SQLite | PostgreSQL 14+ + Redis |
| **Search** | - | MeiliSearch |
| **API** | - | FastAPI |
| **Frontend** | - | Next.js + TailwindCSS |
| **Storage** | NAS/SMB | NAS (원본) + MinIO (스트림) |
| **Transcoding** | FFprobe (메타데이터만) | FFmpeg (HLS) + Celery |
| **Cache** | - | Redis + CDN (선택) |
| **Queue** | - | Celery + RabbitMQ |
| **Deployment** | Local script | Docker Compose |

### 5.4 예상 비용 및 리소스

**하드웨어 요구사항** (중간 규모):
- **API Server**: 4 CPU, 8GB RAM
- **Database**: 8 CPU, 16GB RAM, 500GB SSD
- **Search**: 4 CPU, 8GB RAM
- **Workers**: 8 CPU, 16GB RAM (트랜스코딩용)
- **Storage**: 기존 NAS + 2TB SSD (캐시)

**소프트웨어 비용**:
- 모두 오픈소스 → $0 (라이선스 비용 없음)

**운영 비용** (클라우드 대신 온프레미스):
- 전력비: ~$100/월
- 유지보수: 개발자 1명 파트타임

---

## 6. 참고 자료

### 오픈소스 MAM 솔루션
- **Pravega**: https://github.com/pravega/pravega
- **OpenMAM**: https://github.com/openmam
- **Media Server (Red5/Ant Media)**: https://antmedia.io

### 관련 기술 문서
- PostgreSQL Partitioning: https://www.postgresql.org/docs/current/ddl-partitioning.html
- MeiliSearch Docs: https://docs.meilisearch.com
- FFmpeg HLS Guide: https://trac.ffmpeg.org/wiki/EncodingForStreamingSites
- MinIO Quickstart: https://min.io/docs/minio/linux/index.html

### 유사 프로젝트
- **Plex Media Server**: 개인용 미디어 서버 (클라이언트/서버 아키텍처)
- **Jellyfin**: 오픈소스 미디어 시스템
- **Tautulli**: Plex 모니터링 (DB 설계 참고)

---

**작성자**: Claude (AI Assistant)
**검토 필요**: 기술 리더, DevOps 엔지니어
