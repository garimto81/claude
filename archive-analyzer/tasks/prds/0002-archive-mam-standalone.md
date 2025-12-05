# PRD-0002: Archive MAM (Standalone)

## Product Requirements Document

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Archive MAM - 프로덕션 스탭/에디터용 미디어 자산 관리 시스템 |
| **버전** | v1.0.0 |
| **작성일** | 2025-12-05 |
| **작성자** | Claude (AI Assistant) |
| **상태** | Draft |
| **분류** | OTT 솔루션과 분리된 독립 시스템 |

---

## 1. Executive Summary

### 1.1 시스템 분리 원칙

```
┌─────────────────────────────────────────────────────────────────────┐
│                         사용자 중심 분리                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────┐    ┌──────────────────────────┐      │
│  │  OTT Solution            │    │  Archive MAM             │      │
│  │  👁️ VIEWER 중심           │    │  ✂️ STAFF/EDITOR 중심     │      │
│  │                          │    │                          │      │
│  │  "콘텐츠를 본다"          │    │  "콘텐츠를 만든다"        │      │
│  │                          │    │                          │      │
│  │  ├── 스트리밍 시청       │    │  ├── 원본 파일 관리      │      │
│  │  ├── 추천 콘텐츠 탐색    │    │  ├── 클리핑/편집         │      │
│  │  ├── 시청 기록/이어보기  │    │  ├── 태깅/메타데이터     │      │
│  │  ├── 검색 (완성 콘텐츠)  │    │  ├── 검색 (원본 아카이브)│      │
│  │  └── 개인화 경험         │    │  └── 프로덕션 워크플로우 │      │
│  └──────────────────────────┘    └──────────────────────────┘      │
│           │                               │                         │
│           │      배포 (Publish)           │                         │
│           │◀──────────────────────────────│                         │
│           │      완성된 콘텐츠 전달        │                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 사용자 및 목적 비교

| 구분 | OTT Solution (Viewer) | Archive MAM (Staff/Editor) |
|------|----------------------|---------------------------|
| **핵심 사용자** | 일반 시청자, 구독자 | 프로덕션 스탭, 영상 에디터, PD |
| **주요 행위** | Watch, Browse, Discover | Edit, Clip, Tag, Organize |
| **콘텐츠 상태** | 완성본 (Ready to Watch) | 원본/작업본 (Raw Material) |
| **UX 목표** | 즐거운 시청 경험 | 빠른 작업 효율 |
| **검색 목적** | "뭘 볼까?" | "어디 있지? 이 장면 찾아야해" |
| **데이터 규모** | 정제된 콘텐츠 (수백 개) | 전체 아카이브 (18TB+, 2000+ 파일) |

### 1.3 워크플로우

```
┌─────────────────────────────────────────────────────────────────────┐
│                    콘텐츠 라이프사이클                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [원본 촬영] → [NAS 저장] → [MAM 등록] → [태깅/정리] → [클리핑]     │
│                               │                           │         │
│                               │     Archive MAM           │         │
│                               │     (Staff/Editor)        │         │
│                               └───────────────────────────┘         │
│                                                           │         │
│                                                      [배포]         │
│                                                           │         │
│                               ┌───────────────────────────┘         │
│                               │                                      │
│                               ▼                                      │
│                          [OTT 등록] → [스트리밍] → [시청자 소비]    │
│                               │                           │         │
│                               │     OTT Solution          │         │
│                               │     (Viewer)              │         │
│                               └───────────────────────────┘         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.4 목표

1. **스탭/에디터 생산성**: 원본 검색 → 클리핑 → 태깅을 빠르게
2. **독립 운영**: OTT 없이도 프로덕션 팀 단독 사용 가능
3. **선택적 배포**: 완성된 콘텐츠만 OTT에 Publish

---

## 2. Feature Categories

### 사용자 페르소나: Staff/Editor

```
┌─────────────────────────────────────────────────────────────────────┐
│  Staff/Editor 페르소나                                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  👤 영상 에디터 (Editor)                                             │
│     "이 장면 어디 있더라? 빨리 찾아서 클립 뽑아야 해"                │
│     - 빠른 검색으로 원하는 장면 찾기                                 │
│     - 즉시 클리핑 후 편집 프로젝트로 가져가기                        │
│     - EDL 내보내기로 Premiere에서 이어 작업                          │
│                                                                      │
│  👤 프로덕션 스탭 (Staff)                                            │
│     "오늘 촬영분 정리하고 태그 달아야지"                             │
│     - 새 영상 등록 및 메타데이터 입력                                │
│     - 플레이어, 이벤트별 태그 부여                                   │
│     - 컬렉션으로 프로젝트별 그룹화                                   │
│                                                                      │
│  👤 PD (Producer/Director)                                          │
│     "지난 WSOP에서 Phil Hellmuth 블러핑 장면 모아줘"                 │
│     - 조건 검색으로 하이라이트 후보 선별                             │
│     - 검토 후 OTT에 배포 승인                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Category A: 자산 관리 (Asset Management)

> 스탭이 원본 파일을 등록하고 관리하는 기능

| ID | 기능 | 우선순위 | Staff/Editor 사용 시나리오 |
|----|------|----------|---------------------------|
| A-1 | 자산 스캔 | P0 | "오늘 촬영분 NAS에 올렸으니 자동으로 등록되게" |
| A-2 | 메타데이터 추출 | P0 | "해상도, 길이, 코덱 정보 자동으로 채워줘" |
| A-3 | 자산 CRUD | P0 | "이 파일 정보 수정하고, 저건 삭제해야 해" |
| A-4 | 버전 관리 | P1 | "원본이랑 편집본, 프록시 다 연결해서 보여줘" |
| A-5 | 자산 상태 | P1 | "작업 중인 건 표시해두고, 완료된 건 아카이브" |
| A-6 | 일괄 작업 | P2 | "이 폴더 전체 한번에 태그 달게" |

**데이터 모델:**

```python
class Asset:
    id: str                    # UUID
    nas_path: str              # NAS 원본 경로
    filename: str              # 파일명
    file_type: str             # video, audio, image
    size_bytes: int            # 파일 크기

    # 기술 메타데이터
    media_info: MediaInfo

    # 상태 관리
    status: str                # pending, active, archived, deleted
    versions: list[Version]

    # 타임스탬프
    created_at: datetime
    updated_at: datetime
    scanned_at: datetime
```

```python
class MediaInfo:
    video_codec: str           # h264, hevc, prores
    audio_codec: str           # aac, pcm
    width: int                 # 1920
    height: int                # 1080
    duration_seconds: float    # 3600.5
    bitrate: int               # 8000000
    framerate: float           # 29.97
    container: str             # mp4, mxf, mov
```

---

### Category B: 태그 시스템 (Tag System)

> 스탭이 콘텐츠를 분류하고, 에디터가 빠르게 찾을 수 있게

| ID | 기능 | 우선순위 | Staff/Editor 사용 시나리오 |
|----|------|----------|---------------------------|
| B-1 | 태그 분류 체계 | P0 | "플레이어, 대회, 핸드별로 분류해서 관리" |
| B-2 | 수동 태깅 | P0 | "이 영상에 Phil Hellmuth, Bluff 태그 추가" |
| B-3 | 자동 태깅 | P1 | "파일명에 WSOP 2024 있으니 자동으로 태그 달아줘" |
| B-4 | 태그 별명 | P1 | "pil 치면 Phil Hellmuth 자동 매칭" |
| B-5 | 태그 계층 | P2 | "WSOP > Main Event > Day 3 계층으로" |
| B-6 | AI 태깅 | P3 | "영상 분석해서 등장인물, 상황 자동 태깅" |

**태그 카테고리:**

```python
TAG_CATEGORIES = {
    # 대회 정보
    "tournament": {
        "description": "대회/시리즈",
        "examples": ["WSOP", "WPT", "EPT", "HCL", "PAD", "GGMillions"],
        "auto_extract": True,  # 파일 경로에서 추출
    },

    # 이벤트 정보
    "event": {
        "description": "이벤트 유형",
        "examples": ["Main Event", "High Roller", "Super High Roller", "Cash Game"],
        "auto_extract": True,
    },

    # 시간 정보
    "temporal": {
        "description": "시간 관련",
        "examples": ["2024", "Day 1", "Day 2", "Final Table"],
        "auto_extract": True,
    },

    # 플레이어
    "player": {
        "description": "등장 선수",
        "examples": ["Phil Hellmuth", "Daniel Negreanu", "Phil Ivey"],
        "auto_extract": False,  # 수동 또는 AI 필요
        "has_aliases": True,
    },

    # 핸드 정보
    "hand": {
        "description": "포커 핸드",
        "examples": ["AA", "KK", "AKs", "72o"],
        "auto_extract": False,
    },

    # 액션/상황
    "action": {
        "description": "게임 액션",
        "examples": ["Bluff", "All-in", "Bad Beat", "Hero Call", "Slow Play"],
        "auto_extract": False,
    },

    # 감정/분위기
    "emotion": {
        "description": "감정/분위기",
        "examples": ["Tilt", "Celebration", "Tension", "Dramatic"],
        "auto_extract": False,
    },

    # 기술 정보
    "technical": {
        "description": "기술 분류",
        "examples": ["4K", "1080p", "MXF", "Broadcast", "Web"],
        "auto_extract": True,
    },
}
```

**태그 별명 시스템:**

```python
PLAYER_ALIASES = {
    "player_phil_hellmuth": {
        "canonical": "Phil Hellmuth",
        "aliases": [
            "phil hellmuth",
            "pil",              # 오타
            "philhelmuth",      # 붙여쓰기
            "poker brat",       # 별명
            "hellmuth",
            "ㅍㅎ",             # 초성
        ],
    },
    "player_daniel_negreanu": {
        "canonical": "Daniel Negreanu",
        "aliases": [
            "daniel negreanu",
            "negreanu",
            "kid poker",        # 별명
            "dnegs",
            "ㄷㄴ",
        ],
    },
}
```

---

### Category C: 검색 시스템 (Search System)

> 에디터가 원하는 장면을 빠르게 찾는 핵심 기능

| ID | 기능 | 우선순위 | Staff/Editor 사용 시나리오 |
|----|------|----------|---------------------------|
| C-1 | 키워드 검색 | P0 | "Phil Hellmuth 블러핑 찾아줘" |
| C-2 | 필터 검색 | P0 | "WSOP 2024에서 AA 핸드만 보여줘" |
| C-3 | 자동완성 | P0 | "phi... 치면 Phil Hellmuth 바로 추천" |
| C-4 | 퍼지 검색 | P1 | "helmuth 오타쳐도 hellmuth 찾아줘" |
| C-5 | 초성 검색 | P1 | "ㅍㅎ 치면 Phil Hellmuth" |
| C-6 | 시맨틱 검색 | P3 | "드라마틱한 올인 장면 찾아줘" |

**검색 쿼리 예시:**

```python
# 단순 검색
query = "WSOP 2024"

# 필터 검색
{
    "query": "Phil Hellmuth",
    "filters": {
        "tournament": ["WSOP", "WPT"],
        "year": [2023, 2024],
        "action": ["Bluff", "All-in"],
    },
    "sort": "-created_at",
    "limit": 50,
}

# 초성 검색
query = "ㅍㅎ"  # → Phil Hellmuth

# 퍼지 검색
query = "pil helmuth"  # → Phil Hellmuth (오타 보정)
```

**검색 결과:**

```python
class SearchResult:
    total: int
    assets: list[AssetSummary]
    facets: dict[str, list[FacetItem]]  # 필터 집계
    suggestions: list[str]               # 검색어 제안
```

---

### Category D: 워크플로우 (Workflow)

> 에디터의 실제 작업을 지원하는 핵심 도구

| ID | 기능 | 우선순위 | Staff/Editor 사용 시나리오 |
|----|------|----------|---------------------------|
| D-1 | 즉시 클리핑 | P0 | "이 장면 23:45-24:15 바로 클립으로 뽑아줘" |
| D-2 | 미리보기 | P0 | "전체 다운 안 받고 이 구간만 먼저 볼게" |
| D-3 | 프록시 생성 | P1 | "편집용으로 저해상도 프록시 만들어줘" |
| D-4 | 배치 트랜스코딩 | P2 | "이 폴더 전체 MP4로 변환해줘" |
| D-5 | 썸네일 생성 | P1 | "이 영상 대표 이미지 뽑아줘" |
| D-6 | 작업 큐 | P1 | "지금 돌리는 작업 상태 보여줘" |

**클리핑 워크플로우:**

```
1. 검색 결과에서 자산 선택
       ↓
2. 타임라인에서 구간 지정 (start_time, end_time)
       ↓
3. 클리핑 요청
       ↓
4. FFmpeg Stream Copy 실행 (무손실, 5초 이내)
       ↓
5. 클립 파일 저장 + 메타데이터 기록
       ↓
6. (선택) OTT에 배포
```

```python
class ClipRequest:
    source_asset_id: str
    start_time: float          # 시작 (초)
    end_time: float            # 종료 (초)
    output_format: str         # mp4, mov
    quality: str               # original, proxy

class ClipResult:
    id: str
    source_asset_id: str
    output_path: str
    duration: float
    size_bytes: int
    status: str                # completed, failed
```

**FFmpeg 명령:**

```bash
# Stream Copy (무손실, 빠름)
ffmpeg -ss {start} -to {end} -i {input} -c copy {output}

# 프록시 생성 (저해상도)
ffmpeg -i {input} -vf scale=640:-1 -c:v libx264 -crf 28 {output}

# 썸네일 추출
ffmpeg -ss {time} -i {input} -vframes 1 -q:v 2 {output.jpg}
```

---

### Category E: 프로덕션 도구 (Production Tools)

> 에디터가 편집 소프트웨어와 연동하는 도구

| ID | 기능 | 우선순위 | Staff/Editor 사용 시나리오 |
|----|------|----------|---------------------------|
| E-1 | EDL 내보내기 | P2 | "선택한 클립들 Premiere용 EDL로 내보내줘" |
| E-2 | 마커 관리 | P2 | "핸드 시작점마다 마커 찍어서 타임라인에 보여줘" |
| E-3 | 컬렉션 | P1 | "WSOP 2024 하이라이트 프로젝트로 묶어둘게" |
| E-4 | 공유 링크 | P2 | "PD한테 이 클립 리뷰용으로 링크 보내줘" |
| E-5 | 다운로드 관리 | P1 | "이 영상들 로컬로 다운받아야 하는데 큐에 넣어줘" |
| E-6 | 히스토리 | P1 | "내가 어제 뽑은 클립들 다시 보여줘" |

**EDL (Edit Decision List) 내보내기:**

```
TITLE: WSOP 2024 Highlights
FCM: NON-DROP FRAME

001  WSOP_D1  V     C        00:23:45:12 00:24:15:00 00:00:00:00 00:00:29:18
* FROM CLIP NAME: WSOP_2024_Day1_Table1.mp4
* COMMENT: Phil Hellmuth All-in

002  WSOP_D1  V     C        00:45:12:00 00:46:02:15 00:00:29:18 00:01:20:03
* FROM CLIP NAME: WSOP_2024_Day1_Table1.mp4
* COMMENT: Bad Beat AA vs 72
```

---

### Category F: 관리 도구 (Admin Tools)

> 시스템 관리자/리드가 전체 운영을 관리

| ID | 기능 | 우선순위 | Staff/Editor 사용 시나리오 |
|----|------|----------|---------------------------|
| F-1 | 대시보드 | P0 | "전체 아카이브 상태 한눈에 보여줘" |
| F-2 | 사용자 관리 | P1 | "새 에디터 계정 추가하고 권한 설정" |
| F-3 | 스캔 스케줄 | P1 | "매일 밤 12시에 NAS 자동 스캔" |
| F-4 | 스토리지 분석 | P1 | "중복 파일 있나? 용량 얼마나 쓰고 있나?" |
| F-5 | 감사 로그 | P2 | "누가 언제 어떤 클립 뽑았는지 확인" |
| F-6 | 백업/복구 | P2 | "메타데이터 백업해두고 복구할 수 있게" |

---

### 카테고리 요약: OTT vs MAM

```
┌─────────────────────────────────────────────────────────────────────┐
│                    기능 분리 원칙                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  OTT Solution (Viewer 중심)          Archive MAM (Staff/Editor 중심)│
│  ─────────────────────────           ─────────────────────────────  │
│                                                                      │
│  ✓ 스트리밍 시청                     ✓ A. 자산 관리                 │
│  ✓ 추천 시스템 (For You)             ✓ B. 태그 시스템               │
│  ✓ 시청 기록 / 이어보기              ✓ C. 검색 시스템 (원본)        │
│  ✓ 검색 (완성 콘텐츠)                ✓ D. 워크플로우 (클리핑)       │
│  ✓ 사용자 프로필                     ✓ E. 프로덕션 도구 (EDL)       │
│  ✓ 개인화 경험                       ✓ F. 관리 도구                 │
│                                                                      │
│  "뭘 볼까?"                          "어디 있지? 이거 뽑아야 해"    │
│                                                                      │
│  ──────────────────────────────────────────────────────────────────  │
│                                                                      │
│  [MAM에서 완성] ──── Publish ────→ [OTT에 등록] → [시청자 소비]    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. System Architecture

### 3.1 독립 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Archive MAM (Standalone)                          │
├─────────────────────────────────────────────────────────────────────┤
│  Frontend Layer                                                      │
│  ├── Admin Dashboard (FastAPI + Jinja2/HTMX)                        │
│  ├── Search UI (Cmd+K 팔레트)                                        │
│  └── Clip Editor (타임라인 UI)                                       │
├─────────────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                                 │
│  ├── /mam/assets/*       - 자산 관리 API                            │
│  ├── /mam/tags/*         - 태그 관리 API                            │
│  ├── /mam/search/*       - 검색 API                                 │
│  ├── /mam/clips/*        - 클리핑 API                               │
│  ├── /mam/jobs/*         - 작업 큐 API                              │
│  └── /mam/admin/*        - 관리 API                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Service Layer                                                       │
│  ├── AssetService        - 자산 CRUD, 버전 관리                     │
│  ├── TagService          - 태그 관리, 자동 태깅                     │
│  ├── SearchService       - MeiliSearch 검색                         │
│  ├── ClipService         - FFmpeg 클리핑                            │
│  ├── WorkflowService     - 작업 큐 관리                             │
│  └── SyncService         - 외부 시스템 동기화 (선택)                │
├─────────────────────────────────────────────────────────────────────┤
│  Data Layer                                                          │
│  ├── SQLite (mam.db)     - 자산, 태그, 작업 메타데이터              │
│  ├── MeiliSearch         - 전문 검색 인덱스                         │
│  └── File Cache          - 썸네일, 프록시 캐시                      │
├─────────────────────────────────────────────────────────────────────┤
│  Storage Layer                                                       │
│  ├── NAS (SMB)           - 원본 파일 (18TB+)                        │
│  └── Local Storage       - 클립, 프록시, 썸네일                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 디렉토리 구조

```
archive-analyzer/
├── src/archive_analyzer/
│   ├── core/                    # 기존 핵심 모듈
│   │   ├── config.py
│   │   ├── smb_connector.py
│   │   ├── scanner.py
│   │   ├── media_extractor.py
│   │   └── database.py
│   │
│   ├── mam/                     # MAM 전용 모듈 (신규)
│   │   ├── __init__.py
│   │   ├── models.py            # Asset, Tag, Clip 모델
│   │   ├── asset_service.py     # 자산 관리
│   │   ├── tag_service.py       # 태그 시스템
│   │   ├── clip_service.py      # 클리핑
│   │   ├── workflow_service.py  # 작업 큐
│   │   └── export_service.py    # EDL, 내보내기
│   │
│   ├── search/                  # 검색 모듈
│   │   ├── meilisearch.py
│   │   ├── fuzzy.py
│   │   └── choseong.py
│   │
│   ├── api/                     # REST API
│   │   ├── app.py
│   │   └── routes/
│   │       ├── assets.py
│   │       ├── tags.py
│   │       ├── search.py
│   │       ├── clips.py
│   │       └── admin.py
│   │
│   └── web/                     # 웹 UI
│       ├── templates/
│       └── static/
│
├── data/
│   ├── mam.db                   # MAM 전용 DB
│   ├── cache/                   # 썸네일, 프록시
│   └── clips/                   # 생성된 클립
│
└── scripts/
    ├── run_scan.py
    ├── start_mam.py             # MAM 서버 시작
    └── sync_to_ott.py           # (선택) OTT 동기화
```

### 3.3 데이터베이스 스키마 (mam.db)

```sql
-- 자산 테이블
CREATE TABLE assets (
    id TEXT PRIMARY KEY,
    nas_path TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT,              -- video, audio, image
    size_bytes INTEGER,

    -- 기술 메타데이터
    video_codec TEXT,
    audio_codec TEXT,
    width INTEGER,
    height INTEGER,
    duration_seconds REAL,
    bitrate INTEGER,
    framerate REAL,
    container TEXT,

    -- 상태
    status TEXT DEFAULT 'active', -- pending, active, archived
    scan_status TEXT DEFAULT 'pending',

    -- 타임스탬프
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    scanned_at DATETIME
);

-- 태그 테이블
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,       -- tournament, player, hand, action, etc.
    canonical_name TEXT,
    parent_id TEXT,               -- 계층 구조
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES tags(id)
);

-- 태그 별명
CREATE TABLE tag_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id TEXT NOT NULL,
    alias TEXT NOT NULL,
    UNIQUE(tag_id, alias),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- 자산-태그 연결
CREATE TABLE asset_tags (
    asset_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,  -- 자동 태깅 신뢰도
    source TEXT,                  -- manual, auto, ai
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (asset_id, tag_id),
    FOREIGN KEY (asset_id) REFERENCES assets(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- 클립 테이블
CREATE TABLE clips (
    id TEXT PRIMARY KEY,
    source_asset_id TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    output_path TEXT,
    output_format TEXT,
    size_bytes INTEGER,
    status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (source_asset_id) REFERENCES assets(id)
);

-- 작업 큐
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,       -- scan, clip, transcode, export
    status TEXT DEFAULT 'queued', -- queued, running, completed, failed
    input_data TEXT,              -- JSON
    output_data TEXT,             -- JSON
    progress REAL DEFAULT 0,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME
);

-- 버전 관리
CREATE TABLE asset_versions (
    id TEXT PRIMARY KEY,
    asset_id TEXT NOT NULL,
    version_type TEXT NOT NULL,   -- original, proxy, clip, edited
    path TEXT NOT NULL,
    size_bytes INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

-- 컬렉션
CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE collection_assets (
    collection_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    position INTEGER DEFAULT 0,
    PRIMARY KEY (collection_id, asset_id),
    FOREIGN KEY (collection_id) REFERENCES collections(id),
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

-- 인덱스
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_file_type ON assets(file_type);
CREATE INDEX idx_tags_category ON tags(category);
CREATE INDEX idx_clips_status ON clips(status);
CREATE INDEX idx_jobs_status ON jobs(status);
```

---

## 4. API Endpoints

### 4.1 자산 API

```
GET    /mam/assets                  # 목록 (필터, 페이징)
GET    /mam/assets/{id}             # 상세
POST   /mam/assets                  # 등록
PUT    /mam/assets/{id}             # 수정
DELETE /mam/assets/{id}             # 삭제
GET    /mam/assets/{id}/versions    # 버전 목록
POST   /mam/assets/{id}/tags        # 태그 추가
DELETE /mam/assets/{id}/tags/{tid}  # 태그 제거
```

### 4.2 태그 API

```
GET    /mam/tags                    # 목록 (카테고리별)
GET    /mam/tags/{id}               # 상세
POST   /mam/tags                    # 생성
PUT    /mam/tags/{id}               # 수정
DELETE /mam/tags/{id}               # 삭제
GET    /mam/tags/autocomplete       # 자동완성
POST   /mam/tags/{id}/aliases       # 별명 추가
```

### 4.3 검색 API

```
GET    /mam/search                  # 통합 검색
GET    /mam/search/autocomplete     # 자동완성
GET    /mam/search/facets           # 패싯 (필터 집계)
POST   /mam/search/advanced         # 고급 검색
```

### 4.4 클리핑 API

```
POST   /mam/clips                   # 클립 생성 요청
GET    /mam/clips/{id}              # 상태 조회
GET    /mam/clips/{id}/download     # 다운로드
DELETE /mam/clips/{id}              # 삭제
```

### 4.5 작업 API

```
GET    /mam/jobs                    # 작업 목록
GET    /mam/jobs/{id}               # 상태 조회
POST   /mam/jobs/{id}/cancel        # 취소
POST   /mam/jobs/{id}/retry         # 재시도
```

### 4.6 관리 API

```
GET    /mam/admin/dashboard         # 대시보드 통계
POST   /mam/admin/scan              # 스캔 시작
GET    /mam/admin/storage           # 스토리지 분석
GET    /mam/admin/logs              # 감사 로그
```

---

## 5. OTT 연동 (선택적)

> OTT 솔루션과 분리되어 있지만, 필요 시 연동 가능

### 5.1 연동 방식

```
┌───────────────┐         ┌───────────────┐
│  Archive MAM  │         │  OTT Solution │
│  (mam.db)     │ ──API──→│  (pokervod.db)│
└───────────────┘         └───────────────┘
       │                         │
       │    POST /ott/publish    │
       │    ─────────────────→   │
       │                         │
       │    자산 메타데이터      │
       │    클립 파일 경로       │
       │    태그 정보            │
       └─────────────────────────┘
```

### 5.2 배포 API

```python
# MAM → OTT 배포
POST /mam/publish
{
    "asset_id": "abc123",
    "target": "ott",              # ott, youtube, etc.
    "options": {
        "catalog_id": "wsop",
        "generate_thumbnail": True,
        "add_to_recommendations": True,
    }
}
```

### 5.3 동기화 스크립트

```powershell
# 선택적 OTT 동기화
python scripts/sync_to_ott.py --dry-run    # 시뮬레이션
python scripts/sync_to_ott.py              # 실행
```

---

## 6. Milestones

| Phase | 설명 | 주요 기능 | 카테고리 |
|-------|------|-----------|----------|
| **1** | 자산 기반 | 스캔, 메타데이터, CRUD | A |
| **2** | 태그 시스템 | 분류 체계, 수동 태깅, 별명 | B |
| **3** | 검색 | 키워드, 필터, 자동완성 | C |
| **4** | 워크플로우 | 클리핑, 미리보기 | D |
| **5** | 프로덕션 | EDL, 컬렉션, 다운로드 | E |
| **6** | 관리 | 대시보드, 사용자, 스케줄 | F |
| **7** | AI (선택) | 자동 태깅, 하이라이트 | B, D |
| **8** | OTT 연동 (선택) | 배포, 동기화 | - |

---

## 7. Non-Functional Requirements

| 항목 | 목표 |
|------|------|
| 검색 응답 | < 200ms |
| 클리핑 (5분) | < 10초 |
| 스캔 속도 | > 100 files/min |
| 동시 사용자 | 20명 |
| 가용성 | 99% (업무 시간) |

---

## 8. Success Metrics

| 지표 | 목표 | 측정 |
|------|------|------|
| 자산 등록률 | 100% | 스캔/등록 |
| 태그 커버리지 | > 80% | 태그 자산/전체 |
| 검색 만족도 | > 90% | 관련 결과 비율 |
| 클리핑 성공률 | > 99% | 성공/전체 |
| 평균 클리핑 시간 | < 10초 | 실측 |

---

## Appendix

### A. 기술 스택

| 구성요소 | 기술 |
|----------|------|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | SQLite (WAL) |
| Search | MeiliSearch |
| Media | FFmpeg/FFprobe |
| Network | smbprotocol |
| Auth | Google OAuth 2.0 |
| Frontend | Jinja2 + HTMX |

### B. 환경 변수

```bash
# SMB
SMB_SERVER=10.10.100.122
SMB_SHARE=docker
SMB_USERNAME=user
SMB_PASSWORD=pass
ARCHIVE_PATH=GGPNAs/ARCHIVE

# MAM
MAM_DB_PATH=data/mam.db
MAM_CACHE_PATH=data/cache
MAM_CLIPS_PATH=data/clips

# Search
MEILISEARCH_URL=http://localhost:7700

# Auth
GOOGLE_CLIENT_ID=xxx
GOOGLE_CLIENT_SECRET=xxx
ADMIN_EMAILS=admin@example.com

# OTT 연동 (선택)
OTT_API_URL=http://localhost:5001
OTT_DB_PATH=D:/AI/claude01/shared-data/pokervod.db
```

---

**작성일**: 2025-12-05
**버전**: 1.0.0
**작성자**: Claude (AI Assistant)

### Changelog

- **v1.0.0**: OTT와 분리된 독립형 MAM PRD 작성 - 카테고리별 기능 정리
