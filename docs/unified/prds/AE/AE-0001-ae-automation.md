# PRD-0001: After Effects 자동화 시스템

**Version**: 2.2.0
**Status**: In Progress
**Created**: 2025-12-23
**Updated**: 2026-01-07
**Author**: Claude Code

---

## 1. 개요

### 1.1 프로젝트 목적

웹 디자이너가 작업한 After Effects(.aep) 파일에 DB 데이터를 자동으로 주입하고, 지정된 로컬 네트워크 디렉토리(NAS)로 렌더링 결과물을 출력하는 자동화 시스템 구축

### 1.2 핵심 가치

**자동화 원칙**: 최소 인력 + 최대 자동화

| 역할 | 인간 | 시스템 |
|------|------|--------|
| 템플릿 제작 | ✅ 디자이너 | ❌ |
| 템플릿 등록 | ❌ | ✅ 폴더 감시로 자동 등록 |
| 데이터 입력 | ✅ 운영자 | ❌ |
| 데이터 저장 | ❌ | ✅ DB 자동 저장 |
| 데이터 선택 | ✅ 운영자 | ❌ |
| 렌더링 실행 | ❌ | ✅ 자동 렌더링 |
| 출력 선택 | ✅ 운영자 | ❌ |
| 파일 저장 | ❌ | ✅ NAS 자동 저장 |

**개선 목표**:

| 항목 | 현재 | 목표 |
|------|------|------|
| 렌더링 프로세스 | 수동 (AE 실행 필요) | 자동 (웹 UI로 요청) |
| 데이터 입력 | 큐시트에서 CSV 추출 → AE 연동 (반자동화) | 전용 웹 UI + PostgreSQL DB 구축 |
| 템플릿 등록 | 수동 업로드 | 폴더 저장 시 자동 등록 |
| 출력 관리 | 수동 파일 복사 | 자동 NAS 저장 |

### 1.3 채택 기술

**AE + Nexrender 모델**

![채택 기술 플로우](/docs/unified/images/ae-0001-techflow.png)
> 📐 [HTML 원본](../../docs/mockups/prd-techflow.html)

---

## 2. 사용자 및 역할

### 2.1 사용자 유형

| 역할 | 설명 | 주요 작업 |
|------|------|----------|
| **디자이너** | AE 템플릿 제작자 | 템플릿 제작/수정, 레이어 네이밍 규칙 준수 |
| **운영자** | 렌더링 요청자 | 데이터 입력, 렌더링 요청, 결과물 확인 |
| **관리자** | 시스템 관리자 | 템플릿 관리, 시스템 설정, 모니터링 |

### 2.2 워크플로우

**워크플로우 v2.0** - 최소 인력 + 최대 자동화

#### Swimlane View (역할별 흐름)

![워크플로우 Swimlane](/docs/unified/images/ae-0001-workflow-swimlane.png)
> 📐 [HTML 원본](../../docs/mockups/prd-workflow-swimlane.html)

#### Sequence View (상호작용 순서)

![워크플로우 Sequence](/docs/unified/images/ae-0001-workflow-sequence.png)
> 📐 [HTML 원본](../../docs/mockups/prd-workflow-sequence.html)

#### Cards View (단계별 상세)

![워크플로우 Cards](/docs/unified/images/ae-0001-workflow-cards.png)
> 📐 [HTML 원본](../../docs/mockups/prd-workflow-cards.html)

---

## 3. 기능 요구사항

### 3.1 템플릿 관리

| ID | 기능 | 우선순위 | 설명 |
|----|------|----------|------|
| F-101 | 템플릿 업로드 | P0 | .aep 파일 업로드 및 메타데이터 추출 |
| F-102 | 레이어 매핑 | P0 | 동적 레이어 식별 및 데이터 필드 매핑 |
| F-103 | 템플릿 미리보기 | P1 | 썸네일 및 컴포지션 정보 표시 |
| F-104 | 템플릿 버전 관리 | P2 | 버전 히스토리 및 롤백 |

### 3.2 렌더링 작업

| ID | 기능 | 우선순위 | 설명 |
|----|------|----------|------|
| F-201 | 작업 생성 | P0 | 템플릿 선택 + 데이터 입력 → 작업 생성 |
| F-202 | 배치 작업 | P1 | CSV/Excel 업로드로 다수 작업 일괄 생성 |
| F-203 | 작업 큐 관리 | P0 | 대기/진행/완료/실패 상태 관리 |
| F-204 | 실시간 진행률 | P1 | WebSocket으로 렌더링 진행률 표시 |
| F-205 | 작업 재시도 | P1 | 실패 작업 자동/수동 재시도 |

### 3.3 출력 관리

| ID | 기능 | 우선순위 | 설명 |
|----|------|----------|------|
| F-301 | NAS 출력 | P0 | 지정된 네트워크 경로로 자동 저장 |
| F-302 | 출력 형식 선택 | P0 | PNG 시퀀스 / Alpha MOV 선택 |
| F-303 | 파일 네이밍 규칙 | P1 | 커스텀 파일명 패턴 설정 |
| F-304 | 출력 히스토리 | P1 | 렌더링 결과물 목록 및 다운로드 |

### 3.4 시스템 관리

| ID | 기능 | 우선순위 | 설명 |
|----|------|----------|------|
| F-401 | 사용자 관리 | P1 | 역할 기반 접근 제어 |
| F-402 | 시스템 모니터링 | P1 | 렌더링 서버 상태, 큐 현황 |
| F-403 | 로그 조회 | P2 | 작업별 상세 로그 |
| F-404 | 설정 관리 | P1 | 출력 경로, 기본값 설정 |

### 3.5 데이터 관리 (v2.0 신규)

**기존 방식**: 큐시트에서 CSV 추출 → AE 연동 (반자동화)

**개선 방식**: 전용 웹 UI + PostgreSQL DB로 마스터/이벤트 데이터 관리

> **레거시 지원**: 기존 큐시트 CSV 워크플로우에 익숙한 사용자를 위해 CSV 가져오기/내보내기 지원

| ID | 기능 | 우선순위 | 설명 |
|----|------|----------|------|
| F-501 | 데이터 타입 정의 | P0 | 운영자가 직접 데이터 구조 정의 (필드명, 타입, 필수 여부) |
| F-502 | 마스터 데이터 관리 | P0 | 선수, 팀 등 반복 사용 데이터 CRUD |
| F-503 | 이벤트 데이터 관리 | P0 | 경기 결과, 순위 등 동적 데이터 CRUD |
| F-504 | 인라인 편집 | P0 | 셀 클릭 시 바로 수정 (DB 직접 편집) |
| F-505 | 자동완성/검색 | P0 | 기존 데이터에서 검색하여 선택 |
| F-506 | 데이터 참조 | P1 | 선수 → 팀 관계 등 참조 필드 지원 |
| F-507 | 가져오기/내보내기 | P2 | CSV/Excel 호환 |

**데이터 타입 예시**:

| 타입 | 필드 | 설명 |
|------|------|------|
| 선수 (players) | name, name_en, team_id, photo_url, country, chips | 마스터 데이터 |
| 팀 (teams) | name, logo_url, country | 마스터 데이터 |
| 경기결과 (results) | player_id, rank, score, prize, event_date | 이벤트 데이터 |

### 3.6 템플릿 자동 등록 (v2.0 신규)

디자이너의 작업 효율을 위한 폴더 감시 기반 자동 등록

| ID | 기능 | 우선순위 | 설명 |
|----|------|----------|------|
| F-601 | 폴더 감시 | P0 | 지정 폴더 실시간 감시 (watchdog) |
| F-602 | 자동 등록 | P0 | .aep/.aepx 파일 생성 시 자동 파싱 및 DB 등록 |
| F-603 | 자동 업데이트 | P1 | 파일 수정 시 메타데이터 자동 갱신 |
| F-604 | 삭제 처리 | P2 | 파일 삭제 시 DB 반영 여부 설정 가능 |
| F-605 | WebSocket 알림 | P1 | 새 템플릿 등록 시 프론트엔드 실시간 알림 |

**감시 폴더 구조**:

```
D:/AE_Templates/           # 감시 루트
├── lower_third/           # 카테고리별 하위 폴더 지원
│   ├── lower_third_v1.aep
│   └── lower_third_v2.aep
├── scoreboard/
│   └── scoreboard.aep
└── transition/
    └── wipe.aep
```

---

## 4. 시스템 아키텍처

### 4.1 전체 구성도

![시스템 아키텍처](/docs/unified/images/ae-0001-architecture.png)
> 📐 [HTML 원본](../../docs/mockups/prd-architecture.html)

### 4.2 기술 스택

| 계층 | 기술 | 버전 | 용도 |
|------|------|------|------|
| **Frontend** | React | 18.x | 관리 UI |
| | TypeScript | 5.x | 타입 안전성 |
| | TanStack Query | 5.x | 서버 상태 관리 |
| | Tailwind CSS | 3.x | 스타일링 |
| **Backend** | FastAPI | 0.109+ | REST API |
| | Python | 3.11+ | 백엔드 언어 |
| | SQLAlchemy | 2.x | ORM |
| | Celery | 5.x | 비동기 작업 |
| **Database** | PostgreSQL | 15+ | 메인 DB |
| | Redis | 7.x | 작업 큐, 캐시 |
| **Rendering** | Nexrender | 1.62.x | AE 자동화 |
| | After Effects | 2025 | 렌더링 엔진 |

### 4.3 디렉토리 구조

```
D:\AI\claude01\automation_ae\
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── api/               # API 라우트
│   │   │   ├── v1/
│   │   │   │   ├── templates.py
│   │   │   │   ├── jobs.py
│   │   │   │   └── outputs.py
│   │   │   └── deps.py
│   │   ├── core/              # 설정, 보안
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── models/            # SQLAlchemy 모델
│   │   │   ├── template.py
│   │   │   ├── job.py
│   │   │   └── output.py
│   │   ├── schemas/           # Pydantic 스키마
│   │   ├── services/          # 비즈니스 로직
│   │   │   └── nexrender/     # Nexrender 연동
│   │   │       ├── client.py
│   │   │       └── job_builder.py
│   │   └── workers/           # Celery 워커
│   │       └── render_worker.py
│   ├── requirements.txt
│   └── main.py
│
├── frontend/                   # React 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   │   ├── JobForm/
│   │   │   ├── JobList/
│   │   │   └── TemplateManager/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Jobs.tsx
│   │   │   └── Templates.tsx
│   │   ├── api/
│   │   └── hooks/
│   ├── package.json
│   └── vite.config.ts
│
├── templates/                  # AE 템플릿 저장소
│   └── .gitkeep
│
├── output/                     # 로컬 출력 (테스트용)
│   └── .gitkeep
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 5. 데이터 모델

### 5.1 ERD

![ERD 다이어그램](/docs/unified/images/ae-0001-erd.png)
> 📐 [HTML 원본](../../docs/mockups/prd-erd.html)

### 5.2 Template 모델

```python
class Template(Base):
    __tablename__ = "templates"

    id: int                    # PK
    name: str                  # 템플릿 이름
    file_path: str             # .aep 파일 경로
    composition: str           # 렌더링 컴포지션 이름
    layers: dict               # 동적 레이어 정보 (JSON)
    # {
    #   "PlayerName": {"type": "text", "default": ""},
    #   "PlayerPhoto": {"type": "image", "default": "placeholder.png"},
    #   "Score": {"type": "text", "default": "0"}
    # }
    thumbnail: str             # 썸네일 경로
    duration: float            # 영상 길이 (초)
    fps: int                   # 프레임레이트
    width: int                 # 해상도 (가로)
    height: int                # 해상도 (세로)
    created_at: datetime
    updated_at: datetime
```

### 5.3 Job 모델

```python
class JobStatus(Enum):
    PENDING = "pending"        # 대기
    PROCESSING = "processing"  # 렌더링 중
    COMPLETED = "completed"    # 완료
    FAILED = "failed"          # 실패

class Job(Base):
    __tablename__ = "jobs"

    id: int                    # PK
    template_id: int           # FK → Template
    status: JobStatus          # 상태
    data: dict                 # 주입 데이터 (JSON)
    # {
    #   "PlayerName": "김철수",
    #   "PlayerPhoto": "/assets/players/kim.png",
    #   "Score": "100"
    # }
    data_selections: list      # v2.0: 데이터 선택 정보 (JSON)
    # [
    #   {"layer_name": "PlayerName", "source": "master", "record_id": 123},
    #   {"layer_name": "Score", "source": "event", "record_id": 456}
    # ]
    output_format: str         # "png_sequence" | "mov_alpha"
    output_path: str           # NAS 출력 경로
    output_filename: str       # 출력 파일명 패턴
    error_message: str         # 에러 메시지 (실패 시)
    progress: int              # 진행률 (0-100)
    created_at: datetime
    started_at: datetime
    completed_at: datetime
```

### 5.4 데이터 타입 모델 (v2.0 신규)

```python
class DataType(Base):
    """마스터/이벤트 데이터 타입 정의"""
    __tablename__ = "data_types"

    id: int                    # PK
    category: str              # "master" | "event"
    name: str                  # 타입 코드명 (예: "players", "teams")
    display_name: str          # 표시명 (예: "선수", "팀")
    schema: dict               # 필드 정의 (JSON)
    # {
    #   "fields": [
    #     {"name": "name", "type": "text", "required": true, "display": "선수명"},
    #     {"name": "team_id", "type": "reference", "ref_type": "teams", "display": "소속팀"},
    #     {"name": "photo_url", "type": "image", "required": false, "display": "사진"}
    #   ],
    #   "display_field": "name",
    #   "search_fields": ["name", "name_en"]
    # }
    created_at: datetime
    updated_at: datetime
```

### 5.5 데이터 레코드 모델 (v2.0 신규)

```python
class DataRecord(Base):
    """실제 데이터 레코드"""
    __tablename__ = "data_records"

    id: int                    # PK
    type_id: int               # FK → DataType
    data: dict                 # 실제 데이터 (JSON)
    # {
    #   "name": "김철수",
    #   "team_id": 5,
    #   "photo_url": "/assets/players/kim.png",
    #   "country": "KR",
    #   "chips": 1500000
    # }
    search_text: str           # 검색용 정규화 텍스트
    event_date: datetime       # 이벤트 날짜 (이벤트 데이터용)
    created_at: datetime
    updated_at: datetime
```

### 5.6 템플릿-데이터 매핑 모델 (v2.0 신규)

```python
class TemplateDataMapping(Base):
    """템플릿 레이어와 데이터 필드 매핑"""
    __tablename__ = "template_data_mappings"

    id: int                    # PK
    template_id: int           # FK → Template
    layer_name: str            # 템플릿 레이어 이름
    data_source: str           # "master" | "event" | "manual"
    data_type_id: int          # FK → DataType (master/event 선택 시)
    data_field: str            # 데이터 필드 경로 (예: "name", "photo_url")
    created_at: datetime
```

---

## 6. API 설계

### 6.1 템플릿 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/templates` | 템플릿 목록 조회 |
| GET | `/api/v1/templates/{id}` | 템플릿 상세 조회 |
| POST | `/api/v1/templates` | 템플릿 업로드 |
| PUT | `/api/v1/templates/{id}` | 템플릿 수정 |
| DELETE | `/api/v1/templates/{id}` | 템플릿 삭제 |
| GET | `/api/v1/templates/{id}/layers` | 레이어 정보 조회 |

### 6.2 작업 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/jobs` | 작업 목록 조회 |
| GET | `/api/v1/jobs/{id}` | 작업 상세 조회 |
| POST | `/api/v1/jobs` | 작업 생성 |
| POST | `/api/v1/jobs/batch` | 배치 작업 생성 |
| DELETE | `/api/v1/jobs/{id}` | 작업 취소/삭제 |
| POST | `/api/v1/jobs/{id}/retry` | 작업 재시도 |
| GET | `/api/v1/jobs/{id}/progress` | 진행률 조회 (WebSocket) |

### 6.3 출력 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/outputs` | 출력 목록 조회 |
| GET | `/api/v1/outputs/{id}` | 출력 상세 조회 |
| GET | `/api/v1/outputs/{id}/download` | 파일 다운로드 |

### 6.4 데이터 타입 API (v2.0 신규)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/data-types` | 데이터 타입 목록 조회 |
| GET | `/api/v1/data-types/{id}` | 데이터 타입 상세 조회 |
| POST | `/api/v1/data-types` | 데이터 타입 생성 |
| PUT | `/api/v1/data-types/{id}` | 데이터 타입 수정 |
| DELETE | `/api/v1/data-types/{id}` | 데이터 타입 삭제 |

### 6.5 데이터 레코드 API (v2.0 신규)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/data-types/{type_id}/records` | 레코드 목록 조회 (페이지네이션) |
| GET | `/api/v1/data-types/{type_id}/records/{id}` | 레코드 상세 조회 |
| POST | `/api/v1/data-types/{type_id}/records` | 레코드 생성 |
| PUT | `/api/v1/data-types/{type_id}/records/{id}` | 레코드 수정 |
| DELETE | `/api/v1/data-types/{type_id}/records/{id}` | 레코드 삭제 |
| POST | `/api/v1/data-types/{type_id}/records/bulk` | 레코드 일괄 생성/수정 |
| GET | `/api/v1/data-types/{type_id}/records/search?q=` | 레코드 검색 (자동완성) |

### 6.6 템플릿 매핑 API (v2.0 신규)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/templates/{id}/mappings` | 템플릿 레이어-데이터 매핑 조회 |
| PUT | `/api/v1/templates/{id}/mappings` | 매핑 설정 저장 |

### 6.7 폴더 감시 API (v2.0 신규)

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/watcher/status` | 감시 상태 조회 |
| POST | `/api/v1/watcher/rescan` | 폴더 수동 재스캔 |
| WS | `/api/v1/ws/watcher` | 템플릿 등록 실시간 알림 |

---

## 7. UI/UX 설계

### 7.1 화면 구성

| 화면 | 경로 | 설명 |
|------|------|------|
| 대시보드 | `/` | 전체 현황, 최근 작업, 통계 |
| 작업 목록 | `/jobs` | 작업 목록, 필터, 상태 관리 |
| 작업 생성 | `/jobs/new` | 템플릿 선택, 데이터 입력, 옵션 설정 |
| 템플릿 관리 | `/templates` | 템플릿 목록, 업로드, 레이어 매핑 |
| 출력 히스토리 | `/outputs` | 렌더링 결과물 목록 |
| 설정 | `/settings` | 시스템 설정 |
| **데이터 타입** | `/data-types` | 데이터 타입 목록 및 생성 (v2.0) |
| **데이터 편집** | `/data-types/{id}/records` | PostgreSQL 기반 데이터 편집 (v2.0) |
| **렌더링 선택** | `/render` | 데이터 선택 → 렌더링 (v2.0) |
| **템플릿 매핑** | `/templates/{id}/mapping` | 레이어-데이터 매핑 설정 (v2.0) |

### 7.2 목업

#### 대시보드
![대시보드](../../docs/images/mockup-dashboard.png)
> 📐 [HTML 원본](../../docs/mockups/dashboard.html)

#### 작업 생성 화면
![작업 생성](../../docs/images/mockup-job-create.png)
> 📐 [HTML 원본](../../docs/mockups/job-create.html)

#### 작업 목록 화면
![작업 목록](../../docs/images/mockup-job-list.png)
> 📐 [HTML 원본](../../docs/mockups/job-list.html)

---

## 8. Nexrender 연동

### 8.1 기본값 처리 정책

**핵심 원칙**: DB에 매칭 데이터가 없는 레이어는 AEP 템플릿에 저장된 기본값을 그대로 사용

| 시나리오 | 동작 | 예시 |
|----------|------|------|
| DB 데이터 있음 | 데이터 주입 | `var_player_name` → "김철수" |
| DB 데이터 없음 | AEP 기본값 유지 | `var_score` → AEP 저장값 "0" |
| 빈 문자열 전달 | 빈 값으로 교체 | `var_note` → "" |

**구현 방식** (`job_builder.py`):

```python
def _build_assets_section(self) -> list[dict]:
    assets = []
    for layer_name, layer_info in layers.items():
        if layer_name not in data:
            continue  # AEP 기본값 유지 (assets에 미포함)
        # 데이터가 있는 경우만 assets에 추가
        assets.append(...)
    return assets
```

**디자이너 가이드**:
- AEP 템플릿 저장 시 모든 동적 레이어에 기본값(placeholder) 설정 권장
- 예: `var_player_name` → "PLAYER NAME", `var_score` → "0"

### 8.2 출력 형식 설정

**지원 형식**: `OutputFormat` enum으로 선택

| 출력 형식 | Output Module | 설명 |
|----------|---------------|------|
| **PNG_SEQUENCE** | 기본값 | 투명 배경 PNG 시퀀스, 서브폴더 출력 |
| **MOV_ALPHA** ✨ | `Nexrender` (커스텀) | 알파 채널 포함 MOV, 오버레이용 |

**MOV Alpha 출력 설정** (v2.2.0 신규):

```python
# job_builder.py - OutputFormat에 따른 분기
if self.job.output_format == OutputFormat.MOV_ALPHA:
    template_data["outputModule"] = "Nexrender"  # 커스텀 Output Module
    template_data["outputExt"] = "mov"
else:
    template_data["outputExt"] = "png"

# Actions 섹션
if self.job.output_format == OutputFormat.MOV_ALPHA:
    return {
        "postrender": [{
            "module": "@nexrender/action-copy",
            "input": "result.mov",
            "output": f"{local_output_dir}/result.mov",
        }]
    }
```

**AE Output Module 생성 필요** (최초 1회):

1. After Effects 실행
2. Edit > Templates > Output Module
3. New 클릭 후 설정:
   - Format: **QuickTime**
   - Video Codec: **Animation** (또는 GoPro CineForm)
   - Channels: **RGB + Alpha** ⚠️ 필수
   - Color: **Straight (Unmatted)**
4. 이름: **"Nexrender"**로 저장

### 8.3 AE 프로젝트 렌더 큐 설정 가이드

**PNG 시퀀스 (알파 포함) 출력을 위한 필수 설정:**

1. **렌더 큐 추가**: Composition → Add to Render Queue (Ctrl+M)
2. **Output Module 설정**:
   - Format: **PNG Sequence**
   - Channels: **RGB + Alpha** (중요!)
   - Depth: Millions of Colors+
3. **Output To**: `[compName]_[#####].png` 형식
4. **프로젝트 저장**: 렌더 큐 항목이 있는 상태로 저장

⚠️ **주의**: Nexrender는 AE 프로젝트의 렌더 큐 설정을 사용합니다. `outputExt`만으로는 출력 형식이 변경되지 않습니다.

### 8.4 Job JSON 구조

```json
{
  "template": {
    "src": "file:///C:/templates/feature_table.aep",
    "composition": "Feature Table Leaderboard MAIN",
    "outputExt": "png",
    "continueOnMissing": true,
    "frameStart": 0,
    "frameEnd": 1799
  },
  "assets": [
    {
      "type": "data",
      "layerName": "var_player_name",
      "property": "Source Text",
      "value": "김철수"
    }
  ],
  "actions": {
    "postrender": [
      {
        "module": "@nexrender/action-copy",
        "input": "*.png",
        "output": "C:/output/job_000001/"
      }
    ]
  },
  "callback": "http://localhost:8000/api/v1/callbacks/render/1"
}
```

---

## 9. 구현 계획

### Phase 1: 기반 구축 (MVP) ✅

- [x] 프로젝트 초기화 (백엔드/프론트엔드)
- [x] DB 스키마 및 모델 구현
- [x] 기본 API 구현 (CRUD)
- [x] Nexrender 연동 테스트

### Phase 2: 핵심 기능 ✅

- [x] 템플릿 업로드 및 레이어 파싱
- [x] 작업 생성 UI
- [x] 렌더링 워커 구현
- [x] NAS 출력 연동

### Phase 3: 고급 기능 ✅

- [x] 배치 작업 (CSV 업로드)
- [x] 실시간 진행률 (WebSocket)
- [x] 작업 재시도 및 에러 핸들링
- [x] 대시보드 통계

### Phase 4: 안정화 ✅

- [x] 로깅 및 모니터링
- [x] 테스트 코드 작성
- [x] 문서화
- [x] 성능 최적화

### Phase 5: 데이터 관리 시스템 (v2.0) ✅

**목표**: 기존 큐시트 CSV 기반 반자동화 → 전용 웹 UI + PostgreSQL DB로 데이터 관리 체계 개선

- [x] DB 모델 설계 및 마이그레이션 (DataType, DataRecord, TemplateDataMapping)
- [x] 마스터 데이터 API 구현 (`/api/v1/data-types`, `/api/v1/data-types/{id}/records`)
- [x] 이벤트 데이터 API 구현
- [x] 데이터 그리드 컴포넌트 구현 (DataGrid, EditableCell)
- [x] 자동완성 컴포넌트 구현 (AutocompleteCell)
- [x] 마스터/이벤트 데이터 페이지 구현

**산출물**:
- `backend/app/models/data_type.py` ✅
- `backend/app/models/data_record.py` ✅
- `backend/app/api/v1/data_types.py` ✅
- `backend/app/api/v1/data_records.py` ✅
- `frontend/src/components/DataGrid/` ✅
- `frontend/src/pages/DataTypes.tsx` ✅
- `frontend/src/pages/DataRecords.tsx` ✅

### Phase 6: 폴더 감시 시스템 (v2.0) ✅

**목표**: 템플릿 자동 등록 기능

- [x] Watchdog 서비스 구현 (folder_watcher.py)
- [x] 감시 워커 구현 (watcher_worker.py)
- [x] 감시 상태 API 구현 (`/api/v1/watcher`)
- [x] WebSocket 알림 연동
- [x] 테스트 (기존 테스트 파일 활용)

**산출물**:
- `backend/app/services/folder_watcher.py` ✅
- `backend/app/workers/watcher_worker.py` ✅
- `backend/app/api/v1/watcher.py` ✅
- `backend/app/api/v1/websocket.py` ✅ (watcher 엔드포인트 추가)
- `backend/run_watcher.py` ✅

### Phase 7: 새 렌더링 워크플로우 (v2.0) ✅ (100%)

**목표**: 데이터 선택 기반 렌더링

- [x] 템플릿-데이터 매핑 API 구현
- [x] 매핑 설정 UI 구현
- [x] Jobs API 수정 (DataSelection 지원)
- [x] 새 렌더링 선택 페이지 구현
- [x] 매핑 API 테스트
- [x] Nexrender 클라이언트 연동 테스트 (2026-01-06)
- [x] Job API 테스트 업데이트
- [x] Docker Compose Celery Worker 서비스 추가

**산출물**:
- `backend/app/api/v1/template_mapping.py` ✅
- `backend/app/schemas/job.py` ✅ (data_selections 필드)
- `backend/app/api/v1/jobs.py` ✅ (resolve_data_selections 함수)
- `backend/tests/test_template_mapping.py` ✅
- `backend/tests/test_api_jobs.py` ✅ (TestJobDataSelections 클래스)
- `frontend/src/pages/RenderSelect.tsx` ✅
- `frontend/src/pages/TemplateMapping.tsx` ✅

### Phase 8: 고급 기능 및 안정화 (v2.0) ✅

**목표**: 완성도 향상 + 렌더링 병렬 처리

**렌더링 병렬 처리**:
- [x] Celery 설정 환경변수화 (config.py)
- [x] 워커 concurrency 동적 설정 (run_worker.py)
- [x] Docker 워커 스케일링 지원 (docker-compose.yml)

**AE 프로젝트 설정 자동화** (2026-01-07):
- [x] Nexrender 호환 렌더 큐 설정 스크립트 (JSX)
- [x] 배치 설정 자동화 스크립트 (Python)
- [x] job_builder.py `outputFileName` 설정 추가

**알파 채널 출력 (MOV_ALPHA)** (2026-01-07):
- [x] OutputFormat.MOV_ALPHA 분기 처리 (job_builder.py)
- [x] AE 커스텀 Output Module "Nexrender" 연동
- [x] action-copy MOV 파일 복사 설정
- [x] 렌더링 테스트 완료 (1920x1080, 60초, 2GB)

**기타 기능**:
- [ ] 다중 선택 배치 렌더링
- [ ] F-507: 데이터 가져오기/내보내기 (CSV/Excel)
- [ ] 성능 최적화 (가상 스크롤, 캐싱)
- [ ] F-604: 삭제 처리 (파일 삭제 시 DB 반영)

### Phase 9: Google Sheets 양방향 동기화 (v3.0) 🟡

**목표**: 기획 데이터 관리 체계화 + 실시간 동기화 + 대시보드 렌더링

**DB 모델** (2026-01-08):
- [x] SyncStatus, MatchType, MappingStatus Enum 정의
- [x] PlanningItem 모델 (Origin 시트)
- [x] Composition 모델 (2_Compositions 시트)
- [x] TextLayer 모델 (4_TextLayers 시트)
- [x] CompositionMapping 모델 (Mapping 시트)
- [x] Alembic 마이그레이션

**동기화 서비스**:
- [x] SheetsClient (Google Sheets API)
- [x] 매퍼 (Origin, Composition, TextLayer, Mapping)
- [x] SheetsSyncEngine (Pull/Push/충돌 해결)
- [x] checksum.py (SHA256 기반 변경 감지)
- [x] ConflictResolver (충돌 해결 전략)

**API 엔드포인트**:
- [x] `/api/v1/sync/sheets/pull` - Sheets → DB
- [x] `/api/v1/sync/sheets/push` - DB → Sheets
- [x] `/api/v1/sync/sheets/status` - 동기화 상태
- [x] `/api/v1/sync/sheets/conflicts` - 충돌 목록
- [x] `/api/v1/planning/stats/overview` - 대시보드 통계
- [x] `/api/v1/planning/items/{id}/render` - 렌더링 실행
- [x] `/api/v1/planning/batch-render` - 일괄 렌더링

**프론트엔드**:
- [x] planning.ts, sync.ts API 클라이언트
- [x] PlanningDashboard.tsx 통합 대시보드
- [x] 기획 항목 테이블 + 렌더링 버튼
- [x] 동기화 상태 패널

**산출물**:
- `backend/app/models/sync_enums.py`
- `backend/app/models/planning_item.py`
- `backend/app/models/composition.py`
- `backend/app/models/text_layer.py`
- `backend/app/models/composition_mapping.py`
- `backend/app/services/sheets_sync/` (전체 디렉토리)
- `backend/app/api/v1/sync.py`
- `backend/app/api/v1/planning_stats.py`
- `backend/app/api/v1/planning_render.py`
- `frontend/src/api/planning.ts`
- `frontend/src/api/sync.ts`
- `frontend/src/pages/PlanningDashboard.tsx`

**남은 작업**:
- [ ] 테스트 코드 작성
- [ ] 전체 테스트 및 문서화

**산출물**:
- `backend/app/core/config.py` ✅ (Celery 설정 추가)
- `backend/run_worker.py` ✅ (환경변수 지원)
- `backend/app/workers/celery_app.py` ✅ (settings 연동)
- `docker-compose.yml` ✅ (스케일링 지원)
- `.env.example` ✅ (환경변수 문서화)
- `scripts/setup_render_queue.jsx` ✅ (AE 렌더 큐 설정)
- `scripts/setup_ae_templates.py` ✅ (배치 설정 자동화)
- `backend/app/services/nexrender/job_builder.py` ✅ (MOV_ALPHA 출력 지원)

---

## 10. 연동 테스트 결과 (2026-01-06)

### 10.1 테스트 환경

| 구성요소 | 버전/설정 | 상태 |
|----------|----------|------|
| After Effects | 2025 | ✅ 설치됨 |
| Nexrender Server | 1.62.3 | ✅ localhost:3000 |
| Nexrender Worker | 1.62.3 | ⚠️ 관리자 권한 필요 |
| FastAPI Backend | Docker | ✅ localhost:8000 |
| Celery Worker | Docker | ✅ ae-automation-celery |
| PostgreSQL | 16-alpine | ✅ localhost:5433 |
| Redis | 7-alpine | ✅ localhost:6380 |
| Frontend | Vite + React | ✅ localhost:5173 |

### 10.2 전체 흐름 테스트

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Backend   │────▶│   Celery    │────▶│  Nexrender  │
│  POST /jobs │     │   FastAPI   │     │   Worker    │     │   Server    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
     ✅                  ✅                  ✅                  ✅
   Job 생성            pending →          processing        Job queued
                      processing          Nexrender 제출
                                                                  │
                                                                  ▼
                                                          ┌─────────────┐
                                                          │  Nexrender  │
                                                          │   Worker    │
                                                          │  (aerender) │
                                                          └─────────────┘
                                                               ⏳
                                                          AE 렌더링
```

### 10.3 테스트 결과

| 테스트 항목 | 결과 | 비고 |
|------------|------|------|
| 템플릿 생성 API | ✅ Pass | ID: 1, 2, 3, 4 생성 |
| Job 생성 API | ✅ Pass | ID: 1~27+ 생성 |
| Celery 태스크 전송 | ✅ Pass | Redis 브로커 연동 |
| Nexrender 제출 | ✅ Pass | UID 발급, `file:///` 형식 확인 |
| Webhook 콜백 설정 | ✅ Pass | callback URL 설정됨 |
| Nexrender Worker | ✅ Pass | AE 2025 연동 완료 |
| AE 렌더링 | ✅ Pass | PNG/MOV 모두 성공 |
| **MOV Alpha 출력** | ✅ Pass | 알파 채널 정상 적용 (v2.2.0) |

### 10.3.1 MOV Alpha 렌더링 테스트 (2026-01-07) ✨

| 템플릿 | 해상도 | 프레임 | 결과 | 파일 크기 |
|--------|--------|--------|------|----------|
| Leaderboard100 Player Row | 1920x52 | 60 | ✅ 성공 | 4.7MB |
| Leaderboard100 Player Row | 1920x52 | 1800 (60초) | ✅ 성공 | 97MB |
| CyprusDesign Feature Table | 1920x1080 | 1800 (60초) | ✅ 성공 | 2.0GB |

**테스트 설정**:
- Output Module: `Nexrender` (커스텀 - QuickTime Animation + RGB+Alpha)
- outputExt: `mov`
- action-copy input: `result.mov`

### 10.4 수정된 버그

| 파일 | 이슈 | 해결 |
|------|------|------|
| `data_export.py` | `ImportError` 클래스명 충돌 | `DataImportError`로 변경 |
| `templates.py` | `LayerInfo` JSON 직렬화 실패 | `.model_dump()` 추가 |
| `job_builder.py` | Windows `file://` URL 파싱 오류 | `file:///C:/path` 형식으로 수정 (슬래시 3개) |
| `job_builder.py` | 출력 파일명 불일치 (2026-01-07) | `outputFileName: "result"` 명시적 설정 추가 |

### 10.5 Nexrender Worker 실행 방법

```powershell
# 관리자 권한 터미널에서 실행 (패치 설치 - 최초 1회)
npx @nexrender/worker --host=http://localhost:3000 `
  --binary="C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\aerender.exe"
```

### 10.6 남은 작업

| 항목 | 상태 | 설명 |
|------|------|------|
| Nexrender Worker 패치 | ⏳ 대기 | 관리자 권한으로 1회 실행 필요 |
| 출력 디렉토리 | ✅ 생성됨 | `D:/AI/claude01/automation_ae/output` |
| 템플릿 레이어 확인 | ⚠️ 필요 | AE에서 실제 레이어명 확인 후 재등록 |

### 10.7 Docker Compose 서비스 구성

```yaml
services:
  postgres:        # PostgreSQL 16    (5433)
  redis:           # Redis 7          (6380)
  backend:         # FastAPI          (8000)
  celery-worker:   # Celery Worker    (신규 추가)
  frontend:        # React Vite       (5173)
  dozzle:          # 로그 모니터링     (9999)
```

**Celery Worker 스케일링**:
```powershell
docker-compose up -d --scale celery-worker=3  # 워커 3개 실행
```

---

## 11. 성공 지표

| 지표 | 목표 |
|------|------|
| 렌더링 성공률 | 95% 이상 |
| 평균 렌더링 시간 | 기존 대비 50% 단축 |
| 수동 작업 감소 | 90% 이상 자동화 |
| 사용자 만족도 | 4.0/5.0 이상 |

---

## 12. 리스크 및 대응

| 리스크 | 영향 | 대응 |
|--------|------|------|
| AE 크래시 | 높음 | 자동 재시도, 워커 격리 |
| 플러그인 라이선스 | 중간 | 사전 검증, 문서화 |
| NAS 연결 불안정 | 중간 | 로컬 버퍼, 재시도 로직 |
| 대용량 파일 처리 | 중간 | 청크 업로드, 스트리밍 |

---

## 부록

### A. 레이어 네이밍 규칙

디자이너가 템플릿 제작 시 준수해야 할 규칙:

```
동적 레이어 네이밍: [PREFIX]_[NAME]

PREFIX:
  - var_  : 텍스트 데이터
  - img_  : 이미지 에셋
  - vid_  : 비디오 에셋

예시:
  - var_player_name
  - var_score
  - img_player_photo
  - img_team_logo
```

### B. AE 프로젝트 설정 가이드

**문제**: Nexrender가 렌더링 결과물을 찾지 못하는 경우

**원인**: AE 프로젝트의 렌더 큐 출력 설정이 Nexrender 기대값과 불일치

**해결 방법 1**: JSX 스크립트 사용 (권장)

```powershell
# AE에서 직접 실행
File > Scripts > Run Script File... > setup_render_queue.jsx
```

**해결 방법 2**: Python 배치 스크립트 사용

```powershell
cd C:\claude\automation_ae\scripts

# 전체 템플릿 폴더 처리
python setup_ae_templates.py

# 단일 파일 처리
python setup_ae_templates.py --single "C:\templates\MyTemplate.aep"

# 파일 목록만 확인
python setup_ae_templates.py --list
```

**렌더 큐 설정 체크리스트**:

| 항목 | 설정값 | 비고 |
|------|--------|------|
| Output Module | PNG Sequence | Format 설정 |
| Channels | RGB + Alpha | 투명 배경 필수 |
| Output To | `result_[#####].png` | Nexrender 표준 |

**수동 설정 방법**:

1. 컴포지션 선택 후 `Ctrl+M` (렌더 큐 추가)
2. Output Module 클릭 → Format: PNG Sequence
3. Channels: RGB + Alpha 선택
4. Output To 클릭 → 파일명: `result_[#####].png`
5. 프로젝트 저장 (`Ctrl+S`)

### C. MOV Alpha Output Module 생성 가이드 ✨

**목적**: 알파 채널이 포함된 MOV 파일 출력 (오버레이 자막용)

**생성 방법**:

1. After Effects 실행
2. **Edit > Templates > Output Module** 클릭
3. Settings 섹션에서 **New** 클릭
4. **Format Options** 설정:
   - Format: **QuickTime**
   - Video Codec: **Animation** (또는 GoPro CineForm YUV 10-bit)
5. **Channels**: **RGB + Alpha** 선택 ⚠️ **필수!**
6. **Color**: **Straight (Unmatted)** 선택
7. OK 클릭
8. 이름 입력: **"Nexrender"**
9. **Save All** 클릭

**확인 방법**:

```powershell
# Nexrender로 테스트 렌더링
curl -X POST http://localhost:3000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "template": {
      "src": "file:///C:/templates/test.aep",
      "composition": "Main",
      "outputModule": "Nexrender",
      "outputExt": "mov"
    },
    "assets": [],
    "actions": {
      "postrender": [{
        "module": "@nexrender/action-copy",
        "input": "result.mov",
        "output": "C:/output/test.mov"
      }]
    }
  }'
```

**코덱별 특성**:

| 코덱 | 알파 | 파일 크기 | Windows 호환 |
|------|------|----------|-------------|
| Animation (RLE) | ✅ | 매우 큼 | ✅ |
| GoPro CineForm | ✅ | 중간 | ✅ |
| Apple ProRes 4444 | ✅ | 중간 | ❌ (macOS만) |

### D. 운영 가이드

#### 시스템 시작 (권장 순서)

```powershell
# 1. Docker 서비스 시작 (PostgreSQL, Redis, Backend, Frontend)
cd C:\claude\automation_ae
docker-compose up -d

# 2. Nexrender 서버 시작 (별도 터미널)
npx nexrender-server --port 3000

# 3. Nexrender 워커 시작 (별도 터미널, 관리자 권한)
npx nexrender-worker --host http://localhost:3000

# 4. Celery 워커 시작 (선택사항 - Docker에서 실행됨)
# docker-compose logs -f celery-worker
```

#### 원클릭 시작 스크립트

```powershell
# PowerShell에서 실행
.\scripts\start-all.ps1

# 또는 Bash에서 실행
./scripts/start-all.sh
```

#### 서비스 상태 확인

| 서비스 | 확인 방법 | 정상 응답 |
|--------|----------|----------|
| Backend | `curl http://localhost:8000/health` | `{"status": "healthy"}` |
| Nexrender | `curl http://localhost:3000/api/v1/jobs` | `[]` 또는 Job 목록 |
| Frontend | 브라우저에서 `http://localhost:5173` | UI 표시 |
| PostgreSQL | `docker-compose ps postgres` | Up |
| Redis | `docker-compose ps redis` | Up |

### E. 트러블슈팅

#### E.1 Nexrender 연결 거부 (Connection refused)

**증상**: Job 생성 시 `[Errno 111] Connection refused` 에러

**원인**: Nexrender 서버가 실행되지 않음

**해결**:
```powershell
# Nexrender 서버 시작
npx nexrender-server --port 3000
```

#### E.2 렌더링 결과 파일 없음 (result.avi not found)

**증상**: `ENOENT: no such file or directory, open '...\result.avi'`

**원인**: AE의 기본 출력 형식이 MOV (ProRes 4444)이며, action-copy가 잘못된 확장자를 찾음

**해결**:
- Job builder에서 `input: "result.mov"` 사용 (이미 적용됨)
- 또는 AE Output Module에서 AVI로 변경

#### E.3 Output Module not found

**증상**: `No output module template was found with the given name`

**원인**: "Nexrender" 커스텀 Output Module이 AE에 없음

**해결**:
1. AE 실행 > Edit > Templates > Output Module
2. New > Format: QuickTime, Channels: RGB+Alpha
3. 이름: "Nexrender"로 저장

#### E.4 JSX 스크립트 JSON 에러

**증상**: `ReferenceError: JSON is not defined`

**원인**: ExtendScript에 JSON 객체 없음

**해결**: JSON 라이브러리 포함 스크립트 사용
- `scripts/extract_layers_v2.jsx` 사용 (JSON polyfill 포함)

#### E.5 PNG Sequence 출력 실패

**증상**: PNG 파일이 생성되지 않음

**원인**: AE 프로젝트의 렌더 큐 설정 불일치

**해결**:
```powershell
# JSX 스크립트로 렌더 큐 설정
File > Scripts > Run Script File... > scripts/setup_render_queue.jsx
```

### F. 참고 자료

- [Nexrender GitHub](https://github.com/inlife/nexrender)
- [Nexrender Documentation](https://www.nexrender.com)
- [Adobe aerender Documentation](https://helpx.adobe.com/after-effects/using/automated-rendering-network-rendering.html)
- [AE Output Module 문서](https://helpx.adobe.com/after-effects/using/basics-rendering-exporting.html)

