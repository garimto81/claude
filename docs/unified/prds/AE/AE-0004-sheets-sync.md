# PRD-0004: Google Sheets 양방향 동기화 및 기획 대시보드

**Version**: 1.1.0
**Status**: In Progress
**Created**: 2026-01-08
**Updated**: 2026-01-08
**Author**: Claude Code
**Parent PRD**: PRD-0001 (Phase 9)

> **⚠️ 아키텍처 이슈**: 기존 시스템(DataType/DataRecord)과 신규 시스템(Sheets 동기화)이 분리되어 있음. Phase 10에서 통합 필요.

---

## 1. 개요

### 1.1 목적

Google Sheets의 기획 데이터를 실제 PostgreSQL DB로 동기화하고, 통합 대시보드에서 직접 Nexrender 렌더링을 실행할 수 있는 시스템 구축

### 1.2 핵심 가치

| 현재 방식 | 개선 방식 |
|----------|----------|
| Sheets에서 데이터 확인 → 별도 UI에서 렌더링 | 통합 대시보드에서 확인 + 렌더링 원클릭 |
| 수동 데이터 복사 | 양방향 자동 동기화 |
| 진행률 파악 어려움 | 기획 진행률 실시간 표시 |

### 1.3 대상 Google Sheets

**Spreadsheet ID**: `1P8m2uTjOfwyLk1aaSevYJNHSGm9OWH5YoPtc5WxOkdE`

| 시트 | 용도 | DB 모델 |
|------|------|---------|
| Origin | 기획 항목 (Name, Type, Priority) | PlanningItem |
| 2_Compositions | AE 콤포지션 목록 | Composition |
| 4_TextLayers | 텍스트 레이어 상세 | TextLayer |
| Mapping | Origin↔Composition 매칭 결과 | CompositionMapping |

---

## 2. 시스템 아키텍처

### 2.1 데이터 흐름

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│ Google Sheets  │◀───▶│  PostgreSQL    │────▶│   Nexrender    │
│ (기획 데이터)   │     │  (DB 스키마)    │     │   (렌더링)     │
└────────────────┘     └───────┬────────┘     └────────────────┘
                               │
                        ┌──────▼──────┐
                        │   Frontend  │
                        │ (대시보드)   │
                        └─────────────┘
```

### 2.2 동기화 방향

```
[Pull] Google Sheets → PostgreSQL DB
- gviz/tq CSV API로 데이터 fetch
- SHA256 checksum으로 변경 감지
- Upsert (신규 생성 또는 업데이트)

[Push] PostgreSQL DB → Google Sheets
- LOCAL_MODIFIED 상태 항목 필터
- Sheets API로 batch update
- 행 추가 또는 업데이트
```

### 2.3 충돌 해결

| 전략 | 설명 |
|------|------|
| `last_write_wins` | 마지막 수정 시간 기준 (기본값) |
| `local_wins` | 로컬 DB 우선 |
| `remote_wins` | Sheets 원격 우선 |
| `manual` | 수동 해결 필요 |

---

## 3. DB 스키마

### 3.1 ERD

```
┌─────────────────┐       ┌─────────────────┐
│ PlanningItem    │       │ Composition     │
│ (Origin)        │       │ (2_Compositions)│
├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │
│ name (unique)   │       │ name (unique)   │
│ item_type       │       │ duration        │
│ priority        │       │ text_layer_count│
│ source_anticip. │       │ av_layer_count  │
│ sync_status     │       │ template_id FK  │
│ sheets_row_id   │       │ sync_status     │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │  ┌─────────────────┐    │
         └─▶│CompositionMapping│◀──┘
            │ (Mapping)       │
            ├─────────────────┤
            │ id              │
            │ planning_item_id│
            │ composition_id  │
            │ match_type      │
            │ status          │
            │ score           │
            │ sync_status     │
            └─────────────────┘
                    │
            ┌───────▼───────┐
            │ TextLayer     │
            │ (4_TextLayers)│
            ├───────────────┤
            │ id            │
            │ layer_name    │
            │ composition_id│
            │ pattern       │
            │ data_type_id  │
            │ field_name    │
            │ is_mapped     │
            │ sync_status   │
            └───────────────┘
```

### 3.2 동기화 메타데이터 (공통)

```python
sheets_row_id: int | None     # 시트 행 번호
sync_status: SyncStatus       # synced/local_modified/remote_modified/conflict
local_checksum: str | None    # 로컬 데이터 SHA256
remote_checksum: str | None   # 원격 데이터 SHA256
last_synced_at: datetime      # 마지막 동기화 시간
```

---

## 4. API 설계

### 4.1 동기화 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/sync/sheets/pull` | Sheets → DB |
| POST | `/api/v1/sync/sheets/push` | DB → Sheets |
| POST | `/api/v1/sync/sheets/full` | 양방향 전체 |
| GET | `/api/v1/sync/sheets/status` | 동기화 상태 |
| GET | `/api/v1/sync/sheets/conflicts` | 충돌 목록 |
| POST | `/api/v1/sync/sheets/conflicts/{type}/{id}/resolve` | 충돌 해결 |

### 4.2 기획 통계 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/planning/stats/overview` | 대시보드 개요 (진행률, 매핑률, 렌더링 통계) |
| GET | `/api/v1/planning/stats/progress` | 기획 항목별 상세 |
| GET | `/api/v1/planning/stats/compositions` | 콤포지션 목록 |
| GET | `/api/v1/planning/stats/compositions/{id}/layers` | 레이어 목록 |

### 4.3 렌더링 실행 API

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/planning/items/{id}/render` | 기획 항목 → 렌더링 |
| POST | `/api/v1/planning/compositions/{id}/render` | 콤포지션 → 렌더링 |
| POST | `/api/v1/planning/batch-render` | 선택 항목 일괄 렌더링 |
| GET | `/api/v1/planning/mappings` | 매핑 목록 |
| POST | `/api/v1/planning/mappings/{id}/approve` | 매핑 승인 |

---

## 5. 프론트엔드

### 5.1 기획 대시보드 (`/planning`)

```
┌─────────────────────────────────────────────────────────────────┐
│ 기획 대시보드                              [Sheets→DB] [DB→Sheets]│
├─────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│ │ 기획 항목 │ │  승인됨   │ │검토 필요  │ │  미매칭   │            │
│ │    50    │ │    30    │ │    15    │ │    5     │            │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘            │
│                                                                  │
│ 기획 매핑률 ████████████████░░░░ 70%                            │
│ 레이어 매핑률 ██████████████░░░░░░ 60%                          │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ ☑ 항목명              │ 타입   │ 상태     │ 콤포지션     │ 🚀 │ │
│ │ ☑ Tournament Leader  │ UI     │ approved │ Feature Tab │ 🚀 │ │
│ │ ☐ Mini Leaderboard   │ UI     │ review   │ Mini Chip   │ ⏸ │ │
│ │ ☐ Payouts            │ Data   │ missing  │ -           │ - │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                           [선택 항목 일괄 렌더링] │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 컴포넌트 구조

- `PlanningDashboard.tsx` - 메인 페이지
- `StatCard` - 통계 카드
- `ProgressBar` - 진행률 바
- `StatusBadge` - 상태 배지

---

## 6. 구현 현황

### 6.1 완료

- [x] DB 모델 (PlanningItem, Composition, TextLayer, CompositionMapping)
- [x] Alembic 마이그레이션
- [x] 동기화 서비스 (`sheets_sync/`)
- [x] 동기화 API (`sync.py`)
- [x] 대시보드 통계 API (`planning_stats.py`)
- [x] 렌더링 실행 API (`planning_render.py`)
- [x] 프론트엔드 API 클라이언트
- [x] PlanningDashboard 페이지

### 6.2 미완료

- [ ] 테스트 코드
- [ ] 자동 동기화 스케줄러 (옵션)
- [ ] Google Apps Script Webhook 연동 (옵션)

### 6.3 버그 수정 (2026-01-08)

| 이슈 | 제목 | 상태 |
|------|------|:----:|
| [#3](https://github.com/garimto81/automation_ae/issues/3) | sync_engine: Pull 동기화 시 중복 키 에러 | ✅ 수정됨 |
| [#4](https://github.com/garimto81/automation_ae/issues/4) | planning_stats: progress API 중복 항목 반환 | ✅ 수정됨 |
| - | planning/sync API: 프론트엔드 응답 처리 `.data` 중복 | ✅ 수정됨 |

---

## 7. 아키텍처 이슈 및 Phase 10 계획

### 7.1 현재 문제점

**두 시스템이 분리되어 있음**:

```
┌─────────────────────────────────────┐
│   기존 시스템 (Phase 1-8)           │
│   DataType → DataRecord             │  ← 비어있음 (0개)
│        ↓                            │
│   TemplateDataMapping               │  ← 비어있음 (0개)
│        ↓                            │
│   Template (4개) ←──────────────┐   │
└─────────────────────────────────│───┘
                                  │ 연결 안됨
┌─────────────────────────────────│───┐
│   Sheets 동기화 시스템 (Phase 9)│   │
│   PlanningItem (21개)           │   │
│        ↓                        │   │
│   CompositionMapping (28개)     │   │
│        ↓                        │   │
│   Composition (58개) ───────────┘   │  ← template_id 연결 없음
│        ↓                            │
│   TextLayer (279개)                 │  ← data_type_id 연결 없음
└─────────────────────────────────────┘
```

### 7.2 영향

| 페이지 | 문제 |
|--------|------|
| **데이터 타입 관리** | DataType 테이블 비어있음 → 데이터 없음 |
| **기획 대시보드** | TextLayer.data_type_id가 DataType과 연결 안됨 |
| **렌더링** | Composition.template_id가 Template과 연결 안됨 → 렌더링 불가 |

### 7.3 Phase 10 통합 계획

#### Step 1: TextLayer → DataType 자동 생성

```python
# TextLayer의 data_type_name을 기반으로 DataType 자동 생성
for text_layer in text_layers:
    if text_layer.data_type_name:
        data_type = get_or_create_data_type(text_layer.data_type_name)
        text_layer.data_type_id = data_type.id
```

#### Step 2: Composition → Template 자동 매칭

```python
# Composition.name과 Template.composition을 매칭
for composition in compositions:
    template = find_template_by_composition_name(composition.name)
    if template:
        composition.template_id = template.id
```

#### Step 3: 통합 렌더링 파이프라인

```
PlanningItem (기획 항목)
    ↓ CompositionMapping
Composition (AE 콤포지션)
    ↓ template_id
Template (AE 템플릿)
    ↓ TextLayer.data_type_id
DataType → DataRecord (렌더링 데이터)
    ↓
Job → Nexrender (렌더링 실행)
```

### 7.4 Phase 10 체크리스트

- [ ] TextLayer.data_type_name → DataType 자동 생성 서비스
- [ ] Composition.name → Template.composition 자동 매칭 서비스
- [ ] 통합 렌더링 파이프라인 구현
- [ ] "데이터 타입 관리" 페이지에 Sheets 데이터 연동
- [ ] 기획 대시보드에서 직접 렌더링 실행 가능

---

## 8. 파일 목록

### 8.1 Backend

```
backend/app/
├── models/
│   ├── sync_enums.py           # SyncStatus, MatchType, MappingStatus
│   ├── planning_item.py        # PlanningItem
│   ├── composition.py          # Composition
│   ├── text_layer.py           # TextLayer
│   └── composition_mapping.py  # CompositionMapping
├── services/sheets_sync/
│   ├── __init__.py
│   ├── client.py               # SheetsClient
│   ├── checksum.py             # calculate_checksum
│   ├── conflict_resolver.py    # ConflictResolver
│   ├── sync_engine.py          # SheetsSyncEngine
│   └── mappers/
│       ├── base.py             # BaseMapper
│       ├── origin_mapper.py
│       ├── composition_mapper.py
│       ├── text_layer_mapper.py
│       └── mapping_mapper.py
├── api/v1/
│   ├── sync.py                 # 동기화 API
│   ├── planning_stats.py       # 대시보드 통계
│   └── planning_render.py      # 렌더링 실행
└── core/
    └── config.py               # SHEETS_* 설정 추가
```

### 8.2 Frontend

```
frontend/src/
├── api/
│   ├── planning.ts             # Planning API 클라이언트
│   └── sync.ts                 # Sync API 클라이언트
├── pages/
│   └── PlanningDashboard.tsx   # 통합 대시보드
└── App.tsx                     # 라우트 추가
```

---

## 9. 환경 변수

```env
# Google Sheets (config.py에 추가됨)
GOOGLE_SHEETS_CREDENTIALS_FILE=C:/claude/json/desktop_credentials.json
GOOGLE_SHEETS_TOKEN_FILE=C:/claude/json/token_sheets.json
SHEETS_SPREADSHEET_ID=1P8m2uTjOfwyLk1aaSevYJNHSGm9OWH5YoPtc5WxOkdE
SYNC_AUTO_ENABLED=false
SYNC_INTERVAL_MINUTES=30
SYNC_CONFLICT_STRATEGY=last_write_wins
```

---

## 10. 사용 방법

### 10.1 초기 동기화

```bash
# API 호출
curl -X POST http://localhost:8000/api/v1/sync/sheets/pull

# 또는 프론트엔드에서 "Sheets → DB" 버튼 클릭
```

### 10.2 렌더링 실행

1. `/planning` 대시보드 접속
2. 기획 항목 목록에서 승인된(approved) 항목 선택
3. "렌더링" 버튼 클릭 또는 체크박스로 다중 선택 후 "일괄 렌더링"

### 10.3 매핑 승인

1. `review` 상태 항목 확인
2. 콤포지션 매칭 검토
3. "승인" 버튼 클릭 → `approved` 상태로 변경
4. 이후 렌더링 가능

