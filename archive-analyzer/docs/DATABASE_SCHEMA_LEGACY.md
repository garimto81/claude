# Database Schema - Legacy Archive

> **Archived**: 2025-12-03
> **Status**: V3.0 스키마로 대체됨
> **참조**: 현재 스키마는 `DATABASE_SCHEMA.md` 참조

이 문서는 V3.0 이전의 레거시 스키마를 보관합니다.
새 개발은 V3.0 스키마 (series, contents, content_players, content_tags)를 사용하세요.

---

## Legacy ERD

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  catalogs   │────<│  subcatalogs │     │   players   │
│─────────────│     │──────────────│     │─────────────│
│ id (PK)     │     │ id (PK)      │     │ name (PK)   │
│ name        │     │ catalog_id   │     │ display_name│
│ description │     │ name         │     │ country     │
└─────────────┘     │ display_order│     │ total_hands │
       │            └──────────────┘     └─────────────┘
       │                   │                    │
       ▼                   ▼                    │
┌─────────────────┐  ┌─────────────┐           │
│   tournaments   │  │   events    │           │
│─────────────────│  │─────────────│           │
│ id (PK)         │  │ id (PK)     │           │
│ catalog_id (FK) │──│ tournament_ │           │
│ subcatalog_id   │  │ id (FK)     │           │
│ name            │  │ name        │           │
│ year            │  │ day         │           │
│ location        │  │ session     │           │
└─────────────────┘  └──────┬──────┘           │
                            │                  │
                            ▼                  │
                     ┌─────────────┐           │
                     │    files    │           │
                     │─────────────│           │
                     │ id (PK)     │           │
                     │ event_id(FK)│           │
                     │ nas_path    │           │
                     │ filename    │           │
                     └──────┬──────┘           │
                            │                  │
                            ▼                  │
                     ┌─────────────┐           │
                     │    hands    │───────────┘
                     │─────────────│    (players JSON)
                     │ id (PK)     │
                     │ file_id(FK) │
                     │ start_sec   │
                     │ pot_size_bb │
                     └─────────────┘
```

---

## Legacy 테이블 상세

### subcatalogs
서브 카탈로그 (다단계 계층 구조): 자기 참조를 통한 무제한 깊이 지원

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | VARCHAR(100) PK | 고유 식별자 |
| catalog_id | VARCHAR(50) FK | 최상위 카탈로그 |
| parent_id | VARCHAR(100) FK NULL | 상위 서브카탈로그 |
| name | VARCHAR(200) | 서브카탈로그명 |
| depth | INTEGER | 계층 깊이 |
| path | TEXT | 전체 경로 |
| sub1, sub2, sub3 | VARCHAR(200) | 단계별 서브카탈로그명 |
| display_order | INTEGER | 표시 순서 |

#### 계층 구조 예시

```
WSOP (catalog)
├── WSOP ARCHIVE (subcatalog, depth=1)
├── WSOP-BR (subcatalog, depth=1)
│   ├── WSOP-EUROPE (depth=2)
│   └── WSOP-PARADISE (depth=2)
└── WSOP-SC (subcatalog, depth=1)
```

### tournaments
토너먼트: 연도별 대회

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | VARCHAR(100) PK | 고유 식별자 |
| catalog_id | VARCHAR(50) FK | 카탈로그 |
| subcatalog_id | VARCHAR(100) | 서브카탈로그 |
| name | VARCHAR(200) | 토너먼트명 |
| year | INTEGER | 개최 연도 |
| location | VARCHAR(100) | 개최 장소 |

### events
이벤트: 토너먼트 내 개별 이벤트

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | VARCHAR(150) PK | 고유 식별자 |
| tournament_id | VARCHAR(100) FK | 토너먼트 |
| name | VARCHAR(200) | 이벤트명 |
| day | INTEGER | 일차 |
| session | VARCHAR(50) | 세션 |

### hands
핸드: 포커 핸드 정보

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 고유 식별자 |
| file_id | VARCHAR(200) FK | 파일 |
| start_sec | FLOAT | 시작 시간 (초) |
| end_sec | FLOAT | 종료 시간 (초) |
| winner | VARCHAR(100) | 승자 |
| pot_size_bb | FLOAT | 팟 크기 (BB) |
| is_all_in | BOOLEAN | 올인 여부 |
| players | JSON | 참가 플레이어 |
| tags | JSON | 태그 |

### hand_players
핸드-플레이어 관계 테이블 (hands.players JSON 정규화)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 고유 식별자 |
| hand_id | INTEGER FK | 핸드 ID |
| player_name | VARCHAR(100) | 플레이어 이름 |
| position | INTEGER | 순서 |

### hand_tags
핸드-태그 관계 테이블 (hands.tags JSON 정규화)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER PK | 고유 식별자 |
| hand_id | INTEGER FK | 핸드 ID |
| tag | VARCHAR(50) | 태그명 |

### id_mapping
ID 매핑 테이블 (VARCHAR → INTEGER PK 마이그레이션 추적)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| table_name | VARCHAR(50) PK | 테이블명 |
| old_id | VARCHAR(200) PK | 원본 VARCHAR ID |
| new_id | INTEGER | 신규 정수 ID |

---

## Legacy 쿼리 예시

```sql
-- 특정 카탈로그의 모든 하위 항목 (재귀 CTE)
WITH RECURSIVE subcatalog_tree AS (
    SELECT id, parent_id, name, depth, path
    FROM subcatalogs
    WHERE catalog_id = 'WSOP' AND parent_id IS NULL

    UNION ALL

    SELECT s.id, s.parent_id, s.name, s.depth, s.path
    FROM subcatalogs s
    JOIN subcatalog_tree t ON s.parent_id = t.id
)
SELECT * FROM subcatalog_tree ORDER BY path;
```

---

## 마이그레이션 가이드

V3.0 스키마로 마이그레이션하려면 `scripts/migrate_v3_schema.py` 사용:

```bash
python scripts/migrate_v3_schema.py
```

### 데이터 매핑

| Legacy | V3.0 |
|--------|------|
| subcatalogs | series (catalog별 시리즈) |
| tournaments + events | contents (에피소드) |
| hands (file별) | content_players, content_tags |
