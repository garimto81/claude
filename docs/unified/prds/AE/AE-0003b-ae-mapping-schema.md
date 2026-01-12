# PRD-0003: AE 템플릿 매핑 요소 DB 스키마 설계

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Priority** | P1 |
| **Created** | 2026-01-07 |
| **Author** | Claude Code |

---

## 1. 개요

### 1.1 배경
CyprusDesign.aep와 같은 복잡한 After Effects 템플릿의 콤포지션을 분석하여, 각 동적 레이어를 마스터/이벤트 데이터와 연결하는 매핑 시스템 확장이 필요합니다.

### 1.2 목적
- 모든 콤포지션 레이어의 구조화된 분석 및 저장
- 데이터 소스(선수/팀/경기결과 등)와 레이어 자동 매핑
- 렌더링 시 데이터 주입 자동화

### 1.3 현재 상태
```
DataType (players, teams, results)
    │
    ├──→ DataRecord (실제 데이터 인스턴스)
    │
    └──→ TemplateDataMapping
              │
              └──→ Template.layers (var_player_name → players.name)
                        │
                        └──→ Job (렌더링 작업)
```

---

## 2. 기존 모델 분석

### 2.1 Template 모델 (현재)
```python
class Template(Base):
    id: int
    name: str
    file_path: str
    composition: str  # 단일 콤포지션
    layers: dict      # JSON: {"var_name": {"type": "text"}}
    thumbnail: str
    duration: float
    fps: int
    width: int
    height: int
```

**문제점:**
- 단일 composition만 지원
- layers 필드가 평면 구조 (콤포지션 구분 없음)

### 2.2 TemplateDataMapping 모델 (현재)
```python
class TemplateDataMapping(Base):
    id: int
    template_id: int          # FK → templates
    layer_name: str           # "var_player_name"
    data_source: DataSource   # master | event | manual
    data_type_id: int         # FK → data_types
    data_field: str           # "name" or "team.name"
```

**문제점:**
- 콤포지션 정보 없음 (같은 레이어 이름이 여러 콤포지션에 존재할 경우 충돌)
- 레이어 메타데이터 없음 (index, inPoint, outPoint 등)

---

## 3. 확장 스키마 설계

### 3.1 새로운 모델: Composition

콤포지션 정보를 별도 테이블로 분리:

```python
class Composition(Base):
    """AE 프로젝트 내 개별 콤포지션"""

    __tablename__ = "compositions"

    id: int                   # PK
    template_id: int          # FK → templates
    name: str                 # "Cyprus-Player-Card"

    # 콤포지션 메타데이터
    width: int                # 1920
    height: int               # 1080
    duration: float           # 10.0 (초)
    frame_rate: float         # 30.0
    num_layers: int           # 15

    # 렌더링 대상 여부
    is_renderable: bool       # True (메인 출력 콤포지션)
    render_order: int         # 렌더링 순서 (1, 2, 3...)

    # 타임스탬프
    created_at: datetime
    updated_at: datetime

    # 관계
    template: Template
    layers: list["CompositionLayer"]
```

### 3.2 새로운 모델: CompositionLayer

레이어 정보를 별도 테이블로 분리:

```python
class LayerType(str, Enum):
    """레이어 클래스"""
    TEXT = "TextLayer"
    SHAPE = "ShapeLayer"
    AV = "AVLayer"
    NULL = "NullLayer"
    CAMERA = "CameraLayer"
    LIGHT = "LightLayer"
    ADJUSTMENT = "AdjustmentLayer"

class DynamicLayerType(str, Enum):
    """동적 레이어 타입"""
    TEXT = "text"       # var_, txt_, text_
    IMAGE = "image"     # img_, image_
    VIDEO = "video"     # vid_, video_

class CompositionLayer(Base):
    """콤포지션 내 개별 레이어"""

    __tablename__ = "composition_layers"

    id: int                          # PK
    composition_id: int              # FK → compositions

    # 레이어 기본 정보
    name: str                        # "var_player_name"
    index: int                       # AE 레이어 인덱스 (1-based)
    layer_type: LayerType            # TextLayer, AVLayer 등
    enabled: bool                    # True

    # 타임라인 정보
    in_point: float                  # 시작 시간 (초)
    out_point: float                 # 종료 시간 (초)

    # 동적 레이어 정보
    is_dynamic: bool                 # True (var_, img_, vid_ 접두사)
    dynamic_type: DynamicLayerType   # text | image | video | null

    # 기본값/소스
    default_value: str               # 텍스트 레이어의 기본 텍스트
    source_path: str                 # 이미지/비디오 소스 경로

    # 타임스탬프
    created_at: datetime
    updated_at: datetime

    # 관계
    composition: Composition
    data_mapping: "LayerDataMapping"  # 1:1 관계
```

### 3.3 확장된 LayerDataMapping (TemplateDataMapping 대체)

```python
class LayerDataMapping(Base):
    """레이어-데이터 소스 매핑"""

    __tablename__ = "layer_data_mappings"

    id: int                          # PK
    layer_id: int                    # FK → composition_layers (유니크)

    # 데이터 소스 설정
    data_source: DataSource          # master | event | manual
    data_type_id: int                # FK → data_types (nullable)
    data_field: str                  # "name", "photo_url", "team.name"

    # 변환 옵션
    transform: dict                  # JSON: {"uppercase": true, "prefix": "No. "}

    # 유효성 검사
    is_required: bool                # 필수 입력 여부
    validation_regex: str            # 정규식 패턴 (선택)

    # 타임스탬프
    created_at: datetime
    updated_at: datetime

    # 관계
    layer: CompositionLayer  # 1:1
    data_type: DataType
```

### 3.4 ER 다이어그램

```
┌─────────────────┐
│    Template     │
├─────────────────┤
│ id (PK)         │
│ name            │
│ file_path       │
│ ...             │
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐
│   Composition   │
├─────────────────┤
│ id (PK)         │
│ template_id(FK) │──────┐
│ name            │      │
│ width, height   │      │
│ duration        │      │
│ frame_rate      │      │
│ is_renderable   │      │
└────────┬────────┘      │
         │ 1:N           │
         ▼               │
┌─────────────────┐      │
│CompositionLayer │      │
├─────────────────┤      │
│ id (PK)         │      │
│ composition_id  │◀─────┘
│ name            │
│ index           │
│ layer_type      │
│ is_dynamic      │
│ dynamic_type    │
│ default_value   │
│ source_path     │
└────────┬────────┘
         │ 1:1
         ▼
┌─────────────────┐      ┌─────────────────┐
│LayerDataMapping │      │    DataType     │
├─────────────────┤      ├─────────────────┤
│ id (PK)         │      │ id (PK)         │
│ layer_id (FK)   │─────▶│ name            │
│ data_source     │      │ schema          │
│ data_type_id(FK)│──────│ ...             │
│ data_field      │      └────────┬────────┘
│ transform       │               │ 1:N
│ is_required     │               ▼
└─────────────────┘      ┌─────────────────┐
                         │   DataRecord    │
                         ├─────────────────┤
                         │ id (PK)         │
                         │ type_id (FK)    │
                         │ data (JSON)     │
                         │ ...             │
                         └─────────────────┘
```

---

## 4. 마이그레이션 전략

### 4.1 기존 데이터 보존

```sql
-- 1. 새 테이블 생성
CREATE TABLE compositions (...);
CREATE TABLE composition_layers (...);
CREATE TABLE layer_data_mappings (...);

-- 2. 기존 Template.layers → CompositionLayer 마이그레이션
-- 3. 기존 TemplateDataMapping → LayerDataMapping 마이그레이션
-- 4. 검증 후 구 테이블 삭제 (선택)
```

### 4.2 하위 호환성

- Template.layers 필드는 당분간 유지 (읽기 전용)
- 새로운 API 엔드포인트 추가: `/api/v1/compositions`
- 기존 엔드포인트 래핑으로 호환성 유지

---

## 5. API 엔드포인트

### 5.1 콤포지션 API

```
GET    /api/v1/templates/{id}/compositions
       → 템플릿의 모든 콤포지션 목록

GET    /api/v1/compositions/{id}
       → 콤포지션 상세 (레이어 포함)

GET    /api/v1/compositions/{id}/layers
       → 콤포지션의 레이어 목록

POST   /api/v1/templates/{id}/scan
       → AEP 파일 재스캔 (콤포지션/레이어 업데이트)
```

### 5.2 레이어 매핑 API

```
GET    /api/v1/compositions/{id}/mappings
       → 콤포지션의 레이어 매핑 목록

PUT    /api/v1/layers/{id}/mapping
       → 레이어 매핑 설정/수정

DELETE /api/v1/layers/{id}/mapping
       → 레이어 매핑 삭제

POST   /api/v1/compositions/{id}/auto-map
       → 레이어명 기반 자동 매핑 제안
```

---

## 6. 렌더링 데이터 흐름

### 6.1 Job 생성 시

```python
# 1. 콤포지션 선택
composition = get_composition(template_id, comp_name)

# 2. 동적 레이어 조회 + 매핑 정보
layers = get_dynamic_layers_with_mappings(composition.id)

# 3. 데이터 자동 주입
data = {}
for layer in layers:
    if layer.data_mapping:
        mapping = layer.data_mapping
        if mapping.data_source == "master":
            record = get_data_record(mapping.data_type_id, record_id)
            value = get_nested_field(record.data, mapping.data_field)
            value = apply_transform(value, mapping.transform)
        elif mapping.data_source == "manual":
            value = user_input[layer.name]
        data[layer.name] = value

# 4. Job 생성
job = create_job(template_id, composition.name, data)
```

### 6.2 자동 매핑 제안 로직

```python
def suggest_auto_mapping(layer_name: str) -> dict | None:
    """레이어명 패턴 분석 → DataType.field 제안"""

    # 접두사 제거: var_player_name → player_name
    clean_name = remove_prefix(layer_name)  # "player_name"

    # 패턴 매칭
    patterns = [
        (r"player_(.+)", "players", "$1"),        # player_name → players.name
        (r"team_(.+)", "teams", "$1"),            # team_logo → teams.logo
        (r"(.+)_rank", "results", "rank"),        # player_rank → results.rank
        (r"(.+)_chips", "results", "chips_count"),
    ]

    for pattern, data_type, field_template in patterns:
        match = re.match(pattern, clean_name)
        if match:
            field = field_template.replace("$1", match.group(1))
            return {
                "data_type": data_type,
                "data_field": field,
                "confidence": 0.9
            }

    return None
```

---

## 7. 프론트엔드 UI 설계

### 7.1 콤포지션 트리 뷰

```
📁 CyprusDesign.aep
├── 🎬 Cyprus-Player-Card (1920x1080, 10s)
│   ├── 📝 var_player_name    → players.name ✅
│   ├── 🖼️ img_player_photo   → players.photo_url ✅
│   ├── 📝 var_team_name      → teams.name ✅
│   └── 📝 var_chips_count    → ⚠️ 미매핑
│
├── 🎬 Cyprus-Leaderboard (1920x1080, 30s)
│   ├── 📝 var_rank_1_name    → results.rank_1.name ✅
│   ├── 📝 var_rank_1_chips   → results.rank_1.chips ✅
│   └── ...
│
└── 🎬 Cyprus-Banner (1920x200, 5s)
    └── 📝 var_event_title    → events.title ✅
```

### 7.2 매핑 설정 UI

```
┌─────────────────────────────────────────────────────────┐
│ 레이어: var_player_name                                │
├─────────────────────────────────────────────────────────┤
│                                                        │
│ 데이터 소스: ○ 마스터 데이터  ○ 이벤트 데이터  ● 수동  │
│                                                        │
│ 데이터 타입: [players        ▼]                        │
│                                                        │
│ 필드 경로:  [name           ▼]                        │
│             └── name, name_en, nickname, team.name     │
│                                                        │
│ 변환 옵션:                                             │
│   ☑️ 대문자 변환   ☐ 말줄임 (15자)   ☐ 접두사 추가   │
│                                                        │
│ 미리보기: "KIM CHUL SU"                               │
│                                                        │
│                          [취소]  [저장]                │
└─────────────────────────────────────────────────────────┘
```

---

## 8. 체크리스트

### Phase 1: 모델 생성
- [ ] Composition 모델 생성
- [ ] CompositionLayer 모델 생성
- [ ] LayerDataMapping 모델 생성
- [ ] Alembic 마이그레이션 스크립트 작성

### Phase 2: API 개발
- [ ] 콤포지션 CRUD API
- [ ] 레이어 조회 API
- [ ] 매핑 설정 API
- [ ] 자동 매핑 제안 API

### Phase 3: 스캐너 연동
- [ ] JSX 스캔 결과 → DB 저장 서비스
- [ ] 증분 스캔 (변경된 레이어만 업데이트)
- [ ] 스캔 히스토리 관리

### Phase 4: 프론트엔드
- [ ] 콤포지션 트리 뷰 컴포넌트
- [ ] 매핑 설정 모달
- [ ] 자동 매핑 제안 UI

### Phase 5: 렌더링 통합
- [ ] Job 생성 시 매핑 데이터 자동 주입
- [ ] 렌더링 프리뷰 기능

---

## 9. 참고 자료

- 기존 모델: `backend/app/models/`
- JSX 스크립트: `backend/app/services/jsx_scripts/`
- API 라우터: `backend/app/api/v1/`

