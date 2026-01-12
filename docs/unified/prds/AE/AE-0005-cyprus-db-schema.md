# PRD-0005: CyprusDesign DB Schema

**Version**: 1.0.1
**Status**: In Progress (Phase 0 진행 중 - JSX 실행 필요)
**Created**: 2026-01-09
**Updated**: 2026-01-12
**Author**: Claude Code

---

## 목적

CyprusDesign.aep 템플릿의 comp 폴더 내 콤포지션들을 효율적으로 관리하고 렌더링하기 위한 전용 DB 스키마 설계

## 요구사항

| 항목 | 선택 |
|------|------|
| DB 저장소 | **PostgreSQL + Supabase 동기화** |
| 마스터 데이터 연동 | **예** (DataRecord FK 연결, 선수 자동완성) |
| 콤포지션 범위 | **comp 폴더만** (렌더링 대상) |

---

## Phase 0: AEP 분석 계획 (최우선)

### 0.1 현재 분석 현황

| 항목 | 상태 | 파일 |
|------|------|------|
| 전체 스캔 | ✅ 완료 | `CyprusDesign_analysis.json` |
| 청킹 분석 | ✅ 완료 | `analysis/*.json` |
| comp 폴더 분류 | ❌ **미완료** | `comp_folder_list.json` 없음 |

### 0.1.1 문제점

현재 `comp_folder_detailed.json`과 `07_comp_folder_templates.json`은 **전체 프로젝트 스캔** 데이터 기반입니다.

```
sourceType: "full_scan"  ← comp 폴더가 아닌 전체 프로젝트
```

**원인**: `list_comp_folder.jsx`가 AE에서 실행되지 않아 `comp_folder_list.json`이 없음 → fallback으로 전체 스캔 데이터 사용

### 0.2 추가 분석 필요 사항 ⚠️

#### 1) comp 폴더 식별 및 콤포지션 추출 (미완료)

**필요 작업**:
1. After Effects에서 `CyprusDesign.aep` 열기
2. `File > Scripts > Run Script File...`
3. `scripts/list_comp_folder.jsx` 실행
4. `comp_folder_list.json` 생성 확인
5. `python scripts/analyze_comp_folder.py` 재실행

**예상 결과물**:
- `comp_folder_list.json` - comp 폴더 콤포지션만 추출
- `comp_folder_detailed.json` - 레이어 패턴 분석 (comp 폴더만)
- `07_comp_folder_templates.json` - DB 시드용 (comp 폴더만)

#### 2) 분석 데이터 구조

```json
{
  "projectName": "CyprusDesign.aep",
  "compFolderCompositions": [
    {
      "name": "Feature Table Leaderboard MAIN",
      "width": 1920,
      "height": 1080,
      "duration": 60.03,
      "numLayers": 80,
      "layers": [
        {
          "index": 1,
          "name": "Name 1",
          "type": "text",
          "textContent": "DANIEL REZAEI",
          "pattern": "slot",
          "slotIndex": 1,
          "fieldKey": "name"
        }
      ]
    }
  ]
}
```

### 0.3 레이어 패턴 분석 로직

```python
import re

def analyze_layer_pattern(layer_name: str) -> dict:
    """레이어명에서 패턴과 슬롯 번호 추출"""

    # 패턴 1: "Name 1", "Chips 2", "BBs 3" 등
    match = re.match(r'^(.+?)\s*(\d+)$', layer_name)
    if match:
        return {
            "pattern": "slot",
            "field_key": match.group(1).strip().lower().replace(" ", "_"),
            "slot_index": int(match.group(2))
        }

    # 패턴 2: "Rank 1", "Date 1" 등
    match = re.match(r'^(.+?)(\d+)$', layer_name)
    if match:
        return {
            "pattern": "slot",
            "field_key": match.group(1).strip().lower(),
            "slot_index": int(match.group(2))
        }

    # 패턴 3: 고정 라벨 ("players", "chips", "payouts")
    if layer_name.lower() in ["players", "chips", "payouts", "bbs", "level", "blinds"]:
        return {
            "pattern": "label",
            "field_key": layer_name.lower(),
            "slot_index": None
        }

    # 패턴 4: 단일 동적 ("Player Name", "Total Prize")
    return {
        "pattern": "single",
        "field_key": layer_name.lower().replace(" ", "_"),
        "slot_index": None
    }
```

### 0.4 분석 결과 파일 구조

```
templates/CyprusDesign/
├── CyprusDesign.aep
├── CyprusDesign_analysis.json        # 기존: 전체 스캔
├── comp_folder_list.json             # 신규: comp 폴더 콤포지션
├── comp_folder_detailed.json         # 신규: 레이어 패턴 분석 포함
└── analysis/
    ├── 01_metadata.json
    ├── 02_compositions_summary.json
    ├── 03_text_layers.json
    └── 07_comp_folder_templates.json  # 신규: DB 시드용
```

### 0.5 분석 실행 순서

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: JSX 스크립트 실행 (AE 필요)                              │
│   list_comp_folder.jsx → comp_folder_list.json                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Python 분석 스크립트                                     │
│   scripts/analyze_comp_folder.py                                │
│   → comp_folder_detailed.json                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: DB 시드 데이터 생성                                      │
│   scripts/generate_cyprus_seed.py                               │
│   → 07_comp_folder_templates.json                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 분석 스크립트 구현

### 1.1 신규 스크립트

| 스크립트 | 역할 |
|----------|------|
| `scripts/analyze_comp_folder.py` | 레이어 패턴 분석, 슬롯 카운트 계산 |
| `scripts/generate_cyprus_seed.py` | DB 시드 데이터 생성 |

### 1.2 기존 스크립트 수정

| 스크립트 | 수정 내용 |
|----------|----------|
| `list_comp_folder.jsx` | 레이어 상세 정보 추가 (textContent, sourcePath) |

---

## Phase 2: DB 스키마 설계

### 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                      PostgreSQL (Primary)                    │
├─────────────────────────────────────────────────────────────┤
│  cyprus_templates ──────┬──── cyprus_template_fields        │
│         │               │              │                     │
│         │               │              └─── data_records FK  │
│         ▼               │                                    │
│  cyprus_render_jobs     └──── cyprus_presets                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 동기화 (Phase 4)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Supabase (Storage)                      │
└─────────────────────────────────────────────────────────────┘
```

### 테이블 정의

#### 1. cyprus_templates

```sql
CREATE TABLE cyprus_templates (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  category VARCHAR(50) NOT NULL,
  slot_count INT DEFAULT 0,
  duration FLOAT,
  width INT DEFAULT 1920,
  height INT DEFAULT 1080,
  description TEXT,

  supabase_id UUID,
  sync_status VARCHAR(20) DEFAULT 'pending',
  last_synced_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 2. cyprus_template_fields

```sql
CREATE TYPE cyprus_field_type AS ENUM ('text', 'image', 'number', 'currency', 'date', 'time');
CREATE TYPE cyprus_field_pattern AS ENUM ('slot', 'single', 'label');

CREATE TABLE cyprus_template_fields (
  id SERIAL PRIMARY KEY,
  template_id INT REFERENCES cyprus_templates(id) ON DELETE CASCADE,

  layer_name VARCHAR(255) NOT NULL,
  field_key VARCHAR(100) NOT NULL,
  field_type cyprus_field_type NOT NULL,
  pattern cyprus_field_pattern NOT NULL,
  slot_index INT,

  data_type_id INT REFERENCES data_types(id) ON DELETE SET NULL,
  data_field VARCHAR(100),

  is_required BOOLEAN DEFAULT FALSE,
  default_value TEXT,
  transform VARCHAR(255),

  created_at TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(template_id, layer_name)
);
```

#### 3. cyprus_render_jobs

```sql
CREATE TYPE cyprus_job_status AS ENUM ('pending', 'processing', 'completed', 'failed');

CREATE TABLE cyprus_render_jobs (
  id SERIAL PRIMARY KEY,
  template_id INT REFERENCES cyprus_templates(id),
  status cyprus_job_status DEFAULT 'pending',
  progress INT DEFAULT 0,

  data JSONB NOT NULL,
  slot_records JSONB,

  output_path VARCHAR(500),
  output_format VARCHAR(50) DEFAULT 'mov_alpha',
  error_message TEXT,
  retry_count INT DEFAULT 0,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,

  supabase_id UUID
);
```

#### 4. cyprus_presets

```sql
CREATE TABLE cyprus_presets (
  id SERIAL PRIMARY KEY,
  template_id INT REFERENCES cyprus_templates(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,

  data JSONB NOT NULL,
  slot_records JSONB,

  is_favorite BOOLEAN DEFAULT FALSE,
  use_count INT DEFAULT 0,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Phase 3: API 및 시드 데이터

### API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | /api/v1/cyprus/templates | 템플릿 목록 |
| GET | /api/v1/cyprus/templates/{id} | 템플릿 상세 |
| POST | /api/v1/cyprus/jobs | 렌더링 작업 생성 |
| GET | /api/v1/cyprus/presets | 프리셋 목록 |
| GET | /api/v1/cyprus/autocomplete | 선수 자동완성 |

---

## Phase 4: Supabase 동기화

```sql
CREATE TABLE cyprus_templates_sync (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pg_id INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(50) NOT NULL,
  slot_count INT,
  fields JSONB,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE cyprus_jobs_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pg_job_id INT NOT NULL,
  template_name VARCHAR(255),
  status VARCHAR(20),
  data JSONB,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Phase 5: Alembic 마이그레이션 (가장 마지막)

```powershell
cd C:\claude\automation_ae\backend
alembic revision --autogenerate -m "create cyprus tables"
alembic upgrade head
```

---

## 파일 변경 목록

### Phase 0-1 (분석)
```
scripts/
├── analyze_comp_folder.py       # 신규
├── generate_cyprus_seed.py      # 신규
└── list_comp_folder.jsx         # 수정

templates/CyprusDesign/
├── comp_folder_list.json        # 신규
├── comp_folder_detailed.json    # 신규
└── analysis/
    └── 07_comp_folder_templates.json  # 신규
```

### Phase 2-3 (DB/API)
```
backend/app/
├── models/
│   ├── cyprus_template.py
│   ├── cyprus_template_field.py
│   ├── cyprus_render_job.py
│   └── cyprus_preset.py
├── schemas/cyprus.py
├── api/v1/cyprus.py
└── services/cyprus_sync.py
```

### Phase 4-5 (Supabase/마이그레이션)
```
supabase/migrations/
└── 20260110_create_cyprus_sync.sql

backend/alembic/versions/
└── xxxx_create_cyprus_tables.py
```

---

## 실행 순서 요약

| 순서 | Phase | 작업 | 상태 |
|:----:|:-----:|------|:----:|
| 1 | 0 | JSX 스크립트 실행 (comp 폴더 추출) | ❌ **AE 필요** |
| 2 | 1 | Python 분석 스크립트 작성 | ✅ 완료 |
| 3 | 1 | 레이어 패턴 분석 실행 | ⏳ Step 1 대기 |
| 4 | 2 | SQLAlchemy 모델 작성 | - |
| 5 | 3 | API 엔드포인트 구현 | - |
| 6 | 3 | 시드 데이터 생성/적용 | - |
| 7 | 4 | Supabase 동기화 구현 | - |
| 8 | 5 | Alembic 마이그레이션 | - |

---

## 검증 방법

1. **분석 검증**: comp 폴더 콤포지션 수 확인, 슬롯 패턴 정확도
2. **API 테스트**: Swagger UI CRUD 테스트
3. **렌더링 E2E**: Feature Table Leaderboard MAIN 렌더링 테스트

---

## Checklist

- [ ] **JSX 스크립트로 comp 폴더 추출** ← AE 실행 필요
- [x] Python 분석 스크립트 구현 (`analyze_comp_folder.py`)
- [ ] 레이어 패턴 분석 실행 (JSX 완료 후)
- [ ] SQLAlchemy 모델 작성
- [ ] API 엔드포인트 구현
- [ ] 시드 데이터 생성/적용
- [ ] Supabase 동기화 구현
- [ ] Alembic 마이그레이션

