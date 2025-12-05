# Archive MAM Worker Guide

병렬 개발을 위한 Worker별 가이드입니다. 각 Claude Code 인스턴스는 할당된 Worker 역할만 수행합니다.

## Worker 할당

| Worker | Category | 담당 영역 | 브랜치 prefix |
|--------|----------|-----------|---------------|
| **A** | Asset | `mam/asset/`, `api/routes/assets.py` | `feature/mam-asset-*` |
| **B** | Tag | `mam/tag/`, `api/routes/tags.py` | `feature/mam-tag-*` |
| **C** | Search | `mam/search/`, `api/routes/search.py` | `feature/mam-search-*` |
| **D** | Workflow | `mam/workflow/`, `api/routes/clips.py` | `feature/mam-workflow-*` |
| **E** | Production | `mam/production/`, `api/routes/production.py` | `feature/mam-production-*` |
| **F** | Admin | `mam/admin/`, `api/routes/admin.py` | `feature/mam-admin-*` |

---

## Worker 시작 명령

Claude Code 시작 시 다음과 같이 역할을 명시하세요:

```
나는 Worker [A/B/C/D/E/F]로 Archive MAM의 [Category] 기능을 개발합니다.

내 담당 영역:
- 디렉토리: src/archive_analyzer/mam/{category}/
- API 라우트: src/archive_analyzer/api/routes/{category}.py
- 테스트: tests/mam/test_{category}*.py

규칙:
1. 내 담당 디렉토리만 수정
2. core/interfaces.py의 인터페이스 구현
3. 다른 Worker 영역 직접 import 금지
4. 담당 테이블만 CRUD, 나머지는 SELECT만
```

---

## Worker A: Asset Management

```markdown
## 나는 Worker A입니다

### 담당 기능
- 자산 CRUD (등록, 조회, 수정, 삭제)
- 버전 관리 (원본, 프록시, 편집본)
- 메타데이터 관리

### 담당 파일
- src/archive_analyzer/mam/asset/asset_service.py
- src/archive_analyzer/mam/asset/version_service.py
- src/archive_analyzer/api/routes/assets.py
- tests/mam/test_asset*.py

### 담당 테이블
- assets (CRUD)
- asset_versions (CRUD)

### 구현할 인터페이스
- IAssetService

### API 엔드포인트
- GET /mam/assets
- POST /mam/assets
- GET /mam/assets/{id}
- PUT /mam/assets/{id}
- DELETE /mam/assets/{id}
- GET /mam/assets/{id}/versions
```

---

## Worker B: Tag System

```markdown
## 나는 Worker B입니다

### 담당 기능
- 태그 CRUD
- 자동 태깅 (파일명/경로 기반)
- 태그 별명/오타 보정
- 자산 태깅

### 담당 파일
- src/archive_analyzer/mam/tag/tag_service.py
- src/archive_analyzer/mam/tag/auto_tagger.py
- src/archive_analyzer/api/routes/tags.py
- tests/mam/test_tag*.py

### 담당 테이블
- tags (CRUD)
- tag_aliases (CRUD)
- asset_tags (CRUD)

### 구현할 인터페이스
- ITagService

### API 엔드포인트
- GET /mam/tags
- POST /mam/tags
- GET /mam/tags/autocomplete
- POST /mam/assets/{id}/tags
- DELETE /mam/assets/{id}/tags/{tag_id}
```

---

## Worker C: Search System

```markdown
## 나는 Worker C입니다

### 담당 기능
- 통합 검색
- 자동완성
- 퍼지 검색 (오타 허용)
- 초성 검색
- 패싯 (필터 집계)

### 담당 파일
- src/archive_analyzer/mam/search/search_service.py
- src/archive_analyzer/mam/search/fuzzy.py
- src/archive_analyzer/mam/search/choseong.py
- src/archive_analyzer/api/routes/search.py
- tests/mam/test_search*.py

### 담당 테이블
- search_index (CRUD)

### 구현할 인터페이스
- ISearchService

### API 엔드포인트
- GET /mam/search
- GET /mam/search/autocomplete
- GET /mam/search/facets
```

---

## Worker D: Workflow

```markdown
## 나는 Worker D입니다

### 담당 기능
- 클리핑 (FFmpeg)
- 트랜스코딩
- 작업 큐 관리
- 썸네일 생성

### 담당 파일
- src/archive_analyzer/mam/workflow/clip_service.py
- src/archive_analyzer/mam/workflow/job_service.py
- src/archive_analyzer/mam/workflow/transcode_service.py
- src/archive_analyzer/api/routes/clips.py
- tests/mam/test_workflow*.py

### 담당 테이블
- clips (CRUD)
- jobs (CRUD)

### 구현할 인터페이스
- IClipService
- IJobService

### API 엔드포인트
- POST /mam/clips
- GET /mam/clips/{id}
- DELETE /mam/clips/{id}
- GET /mam/jobs
- POST /mam/jobs/{id}/cancel

### 다른 Worker 의존
- IAssetService (Worker A) - 자산 조회용
```

---

## Worker E: Production Tools

```markdown
## 나는 Worker E입니다

### 담당 기능
- 컬렉션 관리
- EDL 내보내기 (Premiere, DaVinci)
- 메타데이터 내보내기
- 공유 링크 생성

### 담당 파일
- src/archive_analyzer/mam/production/collection_service.py
- src/archive_analyzer/mam/production/edl_export.py
- src/archive_analyzer/mam/production/share_service.py
- src/archive_analyzer/api/routes/production.py
- tests/mam/test_production*.py

### 담당 테이블
- collections (CRUD)
- collection_assets (CRUD)

### 구현할 인터페이스
- ICollectionService
- IExportService

### API 엔드포인트
- GET /mam/collections
- POST /mam/collections
- POST /mam/collections/{id}/assets
- POST /mam/export/edl
- POST /mam/share
```

---

## Worker F: Admin Tools

```markdown
## 나는 Worker F입니다

### 담당 기능
- 대시보드 통계
- 사용자 관리
- 스토리지 분석
- 감사 로그
- 스캔 스케줄

### 담당 파일
- src/archive_analyzer/mam/admin/dashboard_service.py
- src/archive_analyzer/mam/admin/user_service.py
- src/archive_analyzer/mam/admin/audit_service.py
- src/archive_analyzer/api/routes/admin.py
- tests/mam/test_admin*.py

### 담당 테이블
- users (CRUD)
- audit_logs (CRUD)
- 기타 테이블 (SELECT만)

### 구현할 인터페이스
- IUserService
- IDashboardService

### API 엔드포인트
- GET /mam/admin/dashboard
- GET /mam/admin/users
- POST /mam/admin/users
- GET /mam/admin/storage
- GET /mam/admin/logs
```

---

## 충돌 방지 규칙

### 절대 금지
1. ❌ 다른 Worker의 `mam/{category}/` 디렉토리 수정
2. ❌ 다른 Worker의 테이블에 INSERT/UPDATE/DELETE
3. ❌ `core/interfaces.py` 무단 수정
4. ❌ 다른 Worker 서비스 직접 import

### 허용
1. ✅ `core/interfaces.py` 읽기
2. ✅ 다른 테이블 SELECT
3. ✅ 인터페이스를 통한 다른 서비스 사용

### 인터페이스 변경 필요 시
1. GitHub Issue 생성: "[Core Change] 인터페이스 변경 요청"
2. 모든 Worker에게 알림
3. 합의 후 한 명이 대표로 수정
4. 다른 Worker들 코드 업데이트

---

## 테스트 실행

```powershell
# 내 Worker 테스트만 실행
pytest tests/mam/test_{category}*.py -v

# 예: Worker A
pytest tests/mam/test_asset*.py -v

# 예: Worker B
pytest tests/mam/test_tag*.py -v
```

---

## 브랜치 전략

```bash
# 브랜치 생성
git checkout develop
git pull origin develop
git checkout -b feature/mam-{category}-{task}

# 예: Worker A가 CRUD 구현
git checkout -b feature/mam-asset-crud

# 예: Worker B가 자동 태깅 구현
git checkout -b feature/mam-tag-auto-tagging
```

---

## 디렉토리 구조

```
src/archive_analyzer/
├── core/
│   ├── interfaces.py        # 🔒 공유 인터페이스 (변경 금지)
│   ├── database.py          # 🔒 DB 연결
│   └── config.py            # 🔒 설정
│
├── mam/
│   ├── asset/               # Worker A 전용
│   │   ├── __init__.py
│   │   └── asset_service.py
│   │
│   ├── tag/                 # Worker B 전용
│   │   ├── __init__.py
│   │   └── tag_service.py
│   │
│   ├── search/              # Worker C 전용
│   │   ├── __init__.py
│   │   └── search_service.py
│   │
│   ├── workflow/            # Worker D 전용
│   │   ├── __init__.py
│   │   ├── clip_service.py
│   │   └── job_service.py
│   │
│   ├── production/          # Worker E 전용
│   │   ├── __init__.py
│   │   └── collection_service.py
│   │
│   └── admin/               # Worker F 전용
│       ├── __init__.py
│       └── dashboard_service.py
│
└── api/
    └── routes/
        ├── assets.py        # Worker A
        ├── tags.py          # Worker B
        ├── search.py        # Worker C
        ├── clips.py         # Worker D
        ├── production.py    # Worker E
        └── admin.py         # Worker F
```
