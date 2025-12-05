# PRD-0003: Archive MAM 병렬 개발 가이드

## Parallel Development Guide for Multiple Claude Code Instances

| 항목 | 내용 |
|------|------|
| **목적** | 복수의 Claude Code가 동시에 Archive MAM을 개발할 때 충돌 방지 |
| **버전** | v1.0.0 |
| **작성일** | 2025-12-05 |

---

## 1. 개발 단위 분리 원칙

### 1.1 물리적 분리 (파일/디렉토리)

```
archive-analyzer/src/archive_analyzer/
│
├── core/                    # 🔒 공유 모듈 (변경 금지 구역)
│   ├── config.py            # 설정 로드
│   ├── smb_connector.py     # SMB 연결
│   ├── database.py          # DB 연결 (추상화)
│   └── models.py            # 공유 데이터 모델
│
├── mam/                     # ✂️ MAM 기능 (분리 개발)
│   ├── asset/               # [Worker A 담당]
│   ├── tag/                 # [Worker B 담당]
│   ├── search/              # [Worker C 담당]
│   ├── workflow/            # [Worker D 담당]
│   ├── production/          # [Worker E 담당]
│   └── admin/               # [Worker F 담당]
│
└── api/                     # 🌐 API 라우트 (기능별 분리)
    └── routes/
        ├── assets.py        # [Worker A 담당]
        ├── tags.py          # [Worker B 담당]
        ├── search.py        # [Worker C 담당]
        ├── clips.py         # [Worker D 담당]
        ├── production.py    # [Worker E 담당]
        └── admin.py         # [Worker F 담당]
```

### 1.2 Worker 할당표

| Worker | Category | 디렉토리 | 담당 파일 | 테스트 파일 |
|--------|----------|----------|-----------|-------------|
| **A** | Asset Management | `mam/asset/` | `asset_service.py`, `version_service.py` | `tests/mam/test_asset*.py` |
| **B** | Tag System | `mam/tag/` | `tag_service.py`, `auto_tagger.py` | `tests/mam/test_tag*.py` |
| **C** | Search | `mam/search/` | `search_service.py`, `fuzzy.py`, `choseong.py` | `tests/mam/test_search*.py` |
| **D** | Workflow | `mam/workflow/` | `clip_service.py`, `transcode_service.py` | `tests/mam/test_workflow*.py` |
| **E** | Production | `mam/production/` | `edl_export.py`, `collection_service.py` | `tests/mam/test_production*.py` |
| **F** | Admin | `mam/admin/` | `dashboard_service.py`, `user_service.py` | `tests/mam/test_admin*.py` |

---

## 2. 논리적 분리 (인터페이스 계약)

### 2.1 공유 인터페이스 정의

모든 Worker가 참조하는 **공통 인터페이스**는 `core/interfaces.py`에 정의:

```python
# core/interfaces.py - 🔒 변경 시 전체 합의 필요

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# ============================================
# 공유 데이터 모델 (모든 Worker가 사용)
# ============================================

@dataclass
class Asset:
    """자산 기본 정보 - 모든 모듈에서 참조"""
    id: str
    nas_path: str
    filename: str
    file_type: str  # video, audio, image
    size_bytes: int
    status: str  # pending, active, archived
    created_at: datetime
    updated_at: Optional[datetime] = None

@dataclass
class Tag:
    """태그 정보"""
    id: str
    name: str
    category: str  # tournament, player, hand, action, emotion
    canonical_name: Optional[str] = None

@dataclass
class Clip:
    """클립 정보"""
    id: str
    source_asset_id: str
    start_time: float
    end_time: float
    output_path: Optional[str] = None
    status: str  # pending, processing, completed, failed

# ============================================
# 서비스 인터페이스 (계약)
# ============================================

class IAssetService(ABC):
    """Worker A가 구현"""
    @abstractmethod
    async def get_asset(self, asset_id: str) -> Asset | None: ...

    @abstractmethod
    async def list_assets(self, limit: int, offset: int) -> list[Asset]: ...

    @abstractmethod
    async def create_asset(self, nas_path: str, **kwargs) -> Asset: ...

class ITagService(ABC):
    """Worker B가 구현"""
    @abstractmethod
    async def get_tags_for_asset(self, asset_id: str) -> list[Tag]: ...

    @abstractmethod
    async def add_tag_to_asset(self, asset_id: str, tag_id: str) -> bool: ...

    @abstractmethod
    async def search_tags(self, query: str) -> list[Tag]: ...

class ISearchService(ABC):
    """Worker C가 구현"""
    @abstractmethod
    async def search(self, query: str, filters: dict) -> list[Asset]: ...

    @abstractmethod
    async def autocomplete(self, prefix: str) -> list[str]: ...

class IClipService(ABC):
    """Worker D가 구현"""
    @abstractmethod
    async def create_clip(self, asset_id: str, start: float, end: float) -> Clip: ...

    @abstractmethod
    async def get_clip_status(self, clip_id: str) -> Clip | None: ...
```

### 2.2 의존성 방향

```
┌─────────────────────────────────────────────────────────────────────┐
│                    의존성 흐름 (단방향)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  core/interfaces.py  ◀──────────────────────────────────────────┐   │
│  core/models.py      ◀──────────────────────────────────────────┤   │
│  core/database.py    ◀──────────────────────────────────────────┤   │
│        │                                                         │   │
│        │ (import만 가능, 수정 금지)                              │   │
│        ▼                                                         │   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │ Worker A │  │ Worker B │  │ Worker C │  │ Worker D │ ...     │   │
│  │ (Asset)  │  │ (Tag)    │  │ (Search) │  │ (Clip)   │         │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │   │
│        │             │             │             │               │   │
│        └─────────────┴─────────────┴─────────────┘               │   │
│                              │                                    │   │
│                              ▼                                    │   │
│                    api/routes/*.py                                │   │
│                              │                                    │   │
│                              ▼                                    │   │
│                        api/app.py  ◀──────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

⚠️ 금지된 의존성:
- Worker A → Worker B (직접 import 금지)
- mam/* → api/* (역방향 금지)
- api/routes/assets.py → mam/tag/ (담당 영역 외 접근 금지)
```

### 2.3 Worker 간 통신

Worker 간 데이터가 필요한 경우 **인터페이스를 통해서만** 접근:

```python
# ❌ 잘못된 예 - Worker D가 Worker A 직접 import
from mam.asset.asset_service import AssetService  # 금지!

# ✅ 올바른 예 - 인터페이스 통해 접근
from core.interfaces import IAssetService

class ClipService:
    def __init__(self, asset_service: IAssetService):
        self._asset_service = asset_service

    async def create_clip(self, asset_id: str, start: float, end: float):
        asset = await self._asset_service.get_asset(asset_id)
        if not asset:
            raise ValueError(f"Asset not found: {asset_id}")
        # 클립 생성 로직...
```

---

## 3. 데이터베이스 분리

### 3.1 테이블 소유권

| 테이블 | 소유 Worker | 읽기 권한 | 쓰기 권한 |
|--------|-------------|-----------|-----------|
| `assets` | Worker A | 전체 | A만 |
| `asset_versions` | Worker A | 전체 | A만 |
| `tags` | Worker B | 전체 | B만 |
| `tag_aliases` | Worker B | 전체 | B만 |
| `asset_tags` | Worker B | 전체 | B만 |
| `search_index` | Worker C | 전체 | C만 |
| `clips` | Worker D | 전체 | D만 |
| `jobs` | Worker D | 전체 | D만 |
| `collections` | Worker E | 전체 | E만 |
| `collection_assets` | Worker E | 전체 | E만 |
| `users` | Worker F | 전체 | F만 |
| `audit_logs` | Worker F | 전체 | F만 |

### 3.2 마이그레이션 규칙

```
migrations/
├── 001_core_schema.sql          # 🔒 공통 (합의 필요)
├── 100_asset_tables.sql         # Worker A
├── 200_tag_tables.sql           # Worker B
├── 300_search_tables.sql        # Worker C
├── 400_workflow_tables.sql      # Worker D
├── 500_production_tables.sql    # Worker E
├── 600_admin_tables.sql         # Worker F
```

**번호 규칙:**
- 001-099: 공통 스키마 (변경 시 전체 합의)
- 100-199: Worker A (Asset)
- 200-299: Worker B (Tag)
- 300-399: Worker C (Search)
- 400-499: Worker D (Workflow)
- 500-599: Worker E (Production)
- 600-699: Worker F (Admin)

---

## 4. Git 브랜치 전략

### 4.1 브랜치 구조

```
main
  │
  ├── develop                    # 통합 브랜치
  │     │
  │     ├── feature/mam-asset-*      # Worker A
  │     ├── feature/mam-tag-*        # Worker B
  │     ├── feature/mam-search-*     # Worker C
  │     ├── feature/mam-workflow-*   # Worker D
  │     ├── feature/mam-production-* # Worker E
  │     └── feature/mam-admin-*      # Worker F
  │
  └── release/*
```

### 4.2 브랜치 네이밍 규칙

```
feature/mam-{category}-{description}

예시:
- feature/mam-asset-crud           # Worker A
- feature/mam-tag-auto-tagging     # Worker B
- feature/mam-search-fuzzy         # Worker C
- feature/mam-workflow-clip        # Worker D
```

### 4.3 충돌 방지 규칙

| 규칙 | 설명 |
|------|------|
| **파일 잠금** | 자신의 담당 디렉토리만 수정 |
| **인터페이스 변경** | `core/` 변경 시 Issue 생성 후 합의 |
| **PR 범위** | 자신의 Category 파일만 포함 |
| **리뷰** | 다른 Worker 영역 건드리면 해당 Worker 리뷰 필수 |

---

## 5. API 엔드포인트 분리

### 5.1 URL 프리픽스

| Worker | URL Prefix | 예시 |
|--------|------------|------|
| A | `/mam/assets/*` | `GET /mam/assets`, `POST /mam/assets` |
| B | `/mam/tags/*` | `GET /mam/tags`, `POST /mam/assets/{id}/tags` |
| C | `/mam/search/*` | `GET /mam/search`, `GET /mam/search/autocomplete` |
| D | `/mam/clips/*`, `/mam/jobs/*` | `POST /mam/clips`, `GET /mam/jobs` |
| E | `/mam/collections/*`, `/mam/export/*` | `POST /mam/export/edl` |
| F | `/mam/admin/*` | `GET /mam/admin/dashboard` |

### 5.2 라우터 등록 (app.py)

```python
# api/app.py - 라우터 등록만 담당, 각 Worker가 자신의 라우터 구현

from fastapi import FastAPI

app = FastAPI(title="Archive MAM")

# Worker별 라우터 import 및 등록
from api.routes.assets import router as assets_router      # Worker A
from api.routes.tags import router as tags_router          # Worker B
from api.routes.search import router as search_router      # Worker C
from api.routes.clips import router as clips_router        # Worker D
from api.routes.production import router as production_router  # Worker E
from api.routes.admin import router as admin_router        # Worker F

app.include_router(assets_router, prefix="/mam/assets", tags=["Assets"])
app.include_router(tags_router, prefix="/mam/tags", tags=["Tags"])
app.include_router(search_router, prefix="/mam/search", tags=["Search"])
app.include_router(clips_router, prefix="/mam/clips", tags=["Clips"])
app.include_router(production_router, prefix="/mam", tags=["Production"])
app.include_router(admin_router, prefix="/mam/admin", tags=["Admin"])
```

---

## 6. 테스트 분리

### 6.1 테스트 디렉토리 구조

```
tests/
├── conftest.py              # 공통 fixture (읽기 전용)
├── core/                    # 공통 테스트
│   └── test_interfaces.py
│
├── mam/
│   ├── test_asset_*.py      # Worker A
│   ├── test_tag_*.py        # Worker B
│   ├── test_search_*.py     # Worker C
│   ├── test_workflow_*.py   # Worker D
│   ├── test_production_*.py # Worker E
│   └── test_admin_*.py      # Worker F
│
└── integration/             # 통합 테스트 (별도 관리)
    └── test_full_workflow.py
```

### 6.2 테스트 실행 (Worker별)

```powershell
# Worker A만 테스트
pytest tests/mam/test_asset*.py -v

# Worker B만 테스트
pytest tests/mam/test_tag*.py -v

# 전체 테스트 (통합 전)
pytest tests/ -v
```

---

## 7. 개발 시작 체크리스트

### Worker 시작 전 확인사항

```markdown
## Worker [A/B/C/D/E/F] 시작 체크리스트

### 1. 브랜치 확인
- [ ] `develop` 브랜치에서 최신 pull
- [ ] `feature/mam-{category}-{task}` 브랜치 생성

### 2. 담당 영역 확인
- [ ] 내 담당 디렉토리: `mam/{category}/`
- [ ] 내 담당 라우트: `api/routes/{category}.py`
- [ ] 내 담당 테스트: `tests/mam/test_{category}*.py`

### 3. 인터페이스 확인
- [ ] `core/interfaces.py` 읽기
- [ ] 필요한 인터페이스 구현 시작

### 4. 다른 Worker 영역 접근 금지
- [ ] 다른 Worker 디렉토리 수정 안 함
- [ ] 다른 Worker 테이블 직접 수정 안 함
- [ ] 필요시 인터페이스 통해 접근
```

---

## 8. 충돌 해결 프로토콜

### 8.1 공통 파일 변경 필요 시

```
1. GitHub Issue 생성
   - 제목: "[Core Change] {변경 내용}"
   - 라벨: "core-change", "needs-discussion"

2. 모든 Worker에게 알림
   - Issue에 @mention

3. 합의 후 한 명이 대표로 수정

4. 다른 Worker들 rebase
```

### 8.2 인터페이스 추가 필요 시

```python
# 새 인터페이스가 필요한 경우:

# 1. Issue 생성
# 2. 인터페이스 초안 작성 (Issue 코멘트)
# 3. 합의 후 core/interfaces.py에 추가
# 4. 담당 Worker가 구현
```

---

## 9. 실행 순서 권장

### Phase 1: 기반 구축 (순차)

```
1. [공통] core/interfaces.py 정의
2. [공통] core/database.py 설정
3. [공통] migrations/001_core_schema.sql
```

### Phase 2: 병렬 개발

```
┌─────────────────────────────────────────────────────────────────────┐
│  동시 진행 가능                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [Worker A]         [Worker B]         [Worker C]                   │
│  Asset CRUD         Tag CRUD           Search Index                 │
│  asset_service.py   tag_service.py     search_service.py            │
│       ↓                  ↓                  ↓                        │
│  Version Mgmt       Auto Tagging       Fuzzy/Choseong               │
│       ↓                  ↓                  ↓                        │
│  API Routes         API Routes         API Routes                   │
│                                                                      │
│  [Worker D]         [Worker E]         [Worker F]                   │
│  Clip Service       EDL Export         Dashboard                    │
│  clip_service.py    edl_export.py      dashboard_service.py         │
│       ↓                  ↓                  ↓                        │
│  Job Queue          Collections        User Mgmt                    │
│       ↓                  ↓                  ↓                        │
│  API Routes         API Routes         API Routes                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase 3: 통합

```
1. 각 Worker PR → develop 머지
2. 통합 테스트 실행
3. 충돌 해결
4. develop → main 머지
```

---

## 10. 요약: 황금률

```
┌─────────────────────────────────────────────────────────────────────┐
│                    병렬 개발 황금률                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. 🔒 자기 영역만 수정한다                                          │
│     - mam/{category}/ 만 수정                                        │
│     - 다른 Worker 디렉토리 절대 건드리지 않음                        │
│                                                                      │
│  2. 📋 인터페이스 계약을 지킨다                                      │
│     - core/interfaces.py의 계약 준수                                 │
│     - 변경 필요시 Issue 먼저                                         │
│                                                                      │
│  3. 🗄️ 자기 테이블만 쓴다                                            │
│     - 담당 테이블만 INSERT/UPDATE/DELETE                             │
│     - 다른 테이블은 SELECT만                                         │
│                                                                      │
│  4. 🌿 브랜치 규칙을 따른다                                          │
│     - feature/mam-{category}-* 형식                                  │
│     - develop에 자주 머지                                            │
│                                                                      │
│  5. ✅ 테스트 먼저 통과시킨다                                        │
│     - 자기 테스트 통과 확인 후 PR                                    │
│     - 다른 Worker 테스트 깨뜨리지 않음                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

**작성일**: 2025-12-05
**버전**: 1.0.0
