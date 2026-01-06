# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Constraints

| 제약 | 설명 |
|------|------|
| **통합 DB 경로** | `D:/AI/claude01/shared-data/pokervod.db` (WAL 모드) |
| **스키마 변경 시 문서 필수** | ⚠️ 변경 시 `docs/DATABASE_SCHEMA.md` + `DATABASE_UNIFICATION.md` 반드시 동기화 |
| **FFprobe 필수** | 미디어 추출 기능에 시스템 PATH의 ffprobe 필요 |
| **Python 3.10+** | 최소 요구 버전 |

## Project Overview

Archive Analyzer는 OTT 솔루션을 위한 미디어 아카이브 분석 도구입니다. SMB 네트워크를 통해 원격 NAS에 저장된 미디어 파일(18TB+)의 메타데이터를 추출하고 카탈로그를 생성합니다.

**주요 대상**: WSOP, HCL, PAD, GGMillions, MPP, GOG 등 포커 방송 콘텐츠 아카이브 (2,100+ 파일)

## Build & Test Commands

```powershell
# 의존성 설치 (용도별)
pip install -e ".[dev,media]"        # 개발 + 미디어 분석
pip install -e ".[dev,media,search]" # 전체 (MeiliSearch 포함)
pip install -e ".[all]"              # 전체 (auth, admin 포함)

# 테스트 실행
pytest tests/ -v
pytest tests/ -v --cov=src/archive_analyzer --cov-report=term  # 커버리지

# 단일 테스트
pytest tests/test_scanner.py -v
pytest tests/test_media_extractor.py::test_ffprobe_extract -v

# 마커별 테스트
pytest tests/ -v -m unit           # 단위 테스트만
pytest tests/ -v -m "not slow"     # 느린 테스트 제외

# 린터/포매터/타입
ruff check src/
black --check src/
mypy src/archive_analyzer/
```

## CLI

```powershell
archive-analyzer --help              # 설치 후 CLI
python -m archive_analyzer.cli       # 모듈로 직접 실행
```

## Architecture

```
src/archive_analyzer/
├── config.py             # SMBConfig, AnalyzerConfig (환경변수/JSON 로드)
├── smb_connector.py      # SMB 2/3 네트워크 연결 (smbprotocol 기반)
├── file_classifier.py    # 파일 유형 분류 (video, audio, subtitle, metadata)
├── scanner.py            # 재귀 디렉토리 스캔, 체크포인트 기반 재개
├── database.py           # SQLite 저장 (6개 테이블)
├── media_extractor.py    # FFprobe 기반 메타데이터 추출
├── report_generator.py   # Markdown/JSON/Console 리포트 생성
├── search.py             # MeiliSearch 인덱싱/검색 서비스
├── sync.py               # pokervod.db 동기화 모듈
├── sheets_sync.py        # Google Sheets ↔ SQLite 양방향 동기화
├── archive_hands_sync.py # 아카이브 팀 시트 → hands 테이블 동기화
├── title_generator.py    # 시청자용 제목 자동 생성 (규칙 기반)
└── api.py                # FastAPI REST API (검색/동기화)
```

### 데이터 흐름

```
SMBConnector → ArchiveScanner → Database
                    ↓
            SMBMediaExtractor (512KB 부분 다운로드 → FFprobe)
                    ↓
            ReportGenerator (통계/스트리밍 적합성)
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
SearchService   SyncService   SheetsSyncService
(MeiliSearch)   (pokervod.db)  (Google Sheets)
```

### 주요 클래스

| 클래스 | 역할 |
|--------|------|
| `SMBConnector` | SMB 연결/재시도/디렉토리 스캔 |
| `ArchiveScanner` | 체크포인트 기반 재귀 스캔 |
| `FFprobeExtractor` / `SMBMediaExtractor` | 메타데이터 추출 |
| `SearchService` | MeiliSearch 검색 API |
| `SyncService` | archive.db → pokervod.db 동기화 |
| `SheetsSyncService` / `ArchiveHandsSync` | Google Sheets 동기화 |

## Key Scripts

```powershell
# 핵심 워크플로우
python scripts/run_scan.py                    # 아카이브 스캔
python scripts/extract_metadata_netdrive.py   # 네트워크 드라이브 메타데이터 추출
python scripts/generate_report.py             # 리포트 생성
python scripts/retry_failed.py                # 실패 항목 재처리

# 검색/동기화
python scripts/index_to_meilisearch.py        # MeiliSearch 인덱싱
python scripts/sync_to_pokervod.py            # pokervod.db 동기화

# iconik 메타데이터 통합
python scripts/import_iconik_metadata.py      # iconik CSV 임포트
python scripts/clip_matcher.py                # 클립-파일 매칭
python scripts/match_by_path.py               # 경로 기반 매칭

# DB 마이그레이션
python scripts/migrate_subcatalogs_v2.py      # 서브카탈로그 V2
python scripts/migrate_integer_pk.py          # 정수 PK 마이그레이션
python scripts/migrate_json_normalization.py  # JSON 정규화

# 유틸리티
python scripts/test_smb.py                    # SMB 연결 테스트

# NAS 유지보수 (Issue #57)
python scripts/fix_nas_scan_issue.py          # NAS 경로 불일치 해결 (dry-run)
python scripts/fix_nas_scan_issue.py --execute  # 실제 실행
python scripts/verify_db_files.py             # DB 파일 존재 여부 검증
```

## Configuration

환경변수 또는 JSON 파일로 설정:

| 카테고리 | 변수 | 용도 |
|----------|------|------|
| **SMB** | `SMB_SERVER`, `SMB_SHARE`, `SMB_USERNAME`, `SMB_PASSWORD` | NAS 연결 |
| **SMB** | `ARCHIVE_PATH` | 아카이브 경로 (기본: `GGPNAs/ARCHIVE`) |
| **Search** | `MEILISEARCH_URL` | MeiliSearch 서버 (기본: `http://localhost:7700`) |
| **Sheets** | `CREDENTIALS_PATH`, `SPREADSHEET_ID` | Google Sheets 동기화 |
| **OAuth** | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Google OAuth 인증 |
| **Admin** | `ADMIN_EMAILS` | 관리자 이메일 목록 |

```python
config = AnalyzerConfig.from_env()
config = AnalyzerConfig.from_file("config.json")
```

## Database

### 내부 DB: archive.db

| 테이블 | 용도 |
|--------|------|
| `files` | 파일 경로, 크기, 유형, 스캔 상태 |
| `media_info` | 비디오/오디오 코덱, 해상도, 재생시간 |
| `scan_checkpoints` | 스캔 재개를 위한 체크포인트 |
| `scan_stats` | 스캔별 통계 |
| `clip_metadata` | iconik CSV 임포트 (클립 태그, 플레이어) |
| `media_files` | media_metadata.csv 경로 기반 매칭용 |

### 외부 DB 연동: pokervod.db

**경로**: `D:/AI/claude01/shared-data/pokervod.db` (통합 DB)
**소유자**: `qwen_hand_analysis` 레포 (OTT 플랫폼 마스터 DB)

```
archive.db                              pokervod.db
──────────                              ───────────
files.path ─────────────────────────→ files.nas_path
media_info.video_codec ─────────────→ files.codec
media_info.width/height ────────────→ files.resolution
media_info.duration_seconds ────────→ files.duration_sec
clip_metadata.players_tags ─────────→ hands.players (JSON)
```

## Services

### Search (MeiliSearch)

```powershell
docker-compose up -d                                              # 서버 시작
python scripts/index_to_meilisearch.py --db-path data/output/archive.db  # 인덱싱
uvicorn archive_analyzer.api:app --reload --port 8000            # API 서버
```

API 문서: `http://localhost:8000/docs`

### Sync (pokervod.db)

```powershell
python scripts/sync_to_pokervod.py --stats     # 통계 확인
python scripts/sync_to_pokervod.py --dry-run   # 시뮬레이션
python scripts/sync_to_pokervod.py             # 전체 동기화
```

### Google Sheets 동기화

```powershell
python -m archive_analyzer.sheets_sync --init      # 초기 동기화
python -m archive_analyzer.sheets_sync --daemon    # 백그라운드 데몬
python -m archive_analyzer.archive_hands_sync --sync  # Hands 동기화

# Docker 서비스
docker-compose -f docker-compose.sync.yml up -d
```

### Admin (Web UI)

```powershell
python scripts/start_admin.py  # 관리 서버 시작 (IP 자동 감지)
```

| 엔드포인트 | 설명 |
|-----------|------|
| `/admin/` | Admin Dashboard |
| `/auth/login` | Google OAuth Login |
| `/docs` | API Documentation |

## Streaming Compatibility

OTT 호환 판정 기준 (`ReportGenerator`):
- **코덱**: h264, hevc, vp9, av1
- **컨테이너**: mp4, webm, mov
- MXF 등 방송용 포맷 → 트랜스코딩 필요

## Documentation

| 문서 | 설명 |
|------|------|
| `docs/DATABASE_SCHEMA.md` | DB 스키마 및 연동 관계 (**스키마 변경 시 필수 업데이트**) |
| `docs/archive_structure.md` | 아카이브 폴더 구조 및 태그 스키마 |
| `docs/MAM_SOLUTIONS_RESEARCH.md` | 오픈소스 MAM 솔루션 비교 |
