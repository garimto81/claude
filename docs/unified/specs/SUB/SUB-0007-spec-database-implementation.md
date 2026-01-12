# PRD-0007 Part 2: Schema Architecture

## 1. 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PostgreSQL Database                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │   ae (7개)      │  │  json (6개)     │  │     wsop_plus (5개)         │  │
│  │                 │  │                 │  │                             │  │
│  │ ├─ templates    │  │ ├─ gfx_sessions │  │ ├─ tournaments              │  │
│  │ ├─ compositions │  │ ├─ hands        │  │ ├─ blind_levels             │  │
│  │ ├─ comp_layers  │  │ ├─ hand_players │  │ ├─ payouts                  │  │
│  │ ├─ layer_map    │  │ ├─ hand_actions │  │ ├─ player_instances         │  │
│  │ ├─ data_types   │  │ ├─ hand_cards   │  │ └─ schedules                │  │
│  │ ├─ render_jobs  │  │ └─ hand_results │  │                             │  │
│  │ └─ render_out   │  │                 │  │                             │  │
│  └────────┬────────┘  └────────┬────────┘  └──────────────┬──────────────┘  │
│           │                    │                          │                 │
│           │         ┌──────────┴──────────┐               │                 │
│           │         │   Soft FK / Views   │               │                 │
│           │         └──────────┬──────────┘               │                 │
│           │                    │                          │                 │
│  ┌────────┴────────────────────┴──────────────────────────┴──────────────┐  │
│  │                        manual (7개)                                   │  │
│  │                                                                       │  │
│  │ ├─ players_master    ├─ commentators     ├─ events                    │  │
│  │ ├─ player_profiles   ├─ venues           ├─ feature_tables            │  │
│  │ └─ seating_assignments                                                │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        public (Views)                                 │  │
│  │ ├─ v_feature_table_leaderboard                                        │  │
│  │ ├─ v_unified_players                                                  │  │
│  │ └─ v_unified_hands                                                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. ae 스키마 (After Effects)

### 2.1 목적

AEP 프로젝트 파일의 메타데이터, 컴포지션, 레이어 정보 및 렌더링 작업 관리

### 2.2 테이블 목록

| 테이블 | 설명 | 주요 컬럼 |
|--------|------|----------|
| **templates** | AEP 프로젝트 파일 | name, file_path, checksum |
| **compositions** | 렌더링 가능한 컴포지션 | template_id, name, width, height, frame_rate |
| **composition_layers** | 동적 레이어 | composition_id, layer_name, layer_type, is_dynamic |
| **layer_data_mappings** | 데이터 바인딩 설정 | layer_id, source_schema, source_table, source_column |
| **data_types** | 데이터 유형 정의 | type_name, category, schema_definition (JSONB) |
| **render_jobs** | Nexrender 작업 큐 | composition_id, data_payload (JSONB), status |
| **render_outputs** | 렌더링 결과물 | render_job_id, file_path, storage_url |

### 2.3 ERD

```
┌─────────────────┐
│   templates     │
├─────────────────┤
│ id (PK)         │
│ name            │
│ file_path       │
│ checksum        │
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐
│  compositions   │
├─────────────────┤
│ id (PK)         │
│ template_id(FK) │
│ name            │
│ comp_type       │
│ width, height   │
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐
│composition_layer│       │   data_types    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ composition_id  │       │ type_name       │
│ layer_name      │       │ category        │
│ layer_type      │       │ schema_def      │
│ is_dynamic      │       └────────┬────────┘
└────────┬────────┘                │
         │ 1:1                     │
         ▼                         │
┌─────────────────┐                │
│layer_data_map   │                │
├─────────────────┤                │
│ id (PK)         │                │
│ layer_id (FK)   │                │
│ source_schema   │                │
│ source_table    │                │
│ data_type_id    │◀───────────────┘
└─────────────────┘
```

### 2.4 주요 특성

- **정적 데이터**: AEP 분석 결과, 자주 변경되지 않음
- **캐시 가능**: 템플릿/컴포지션 정보는 캐시 적합
- **매핑 핵심**: layer_data_mappings가 다른 스키마와 연결 고리

---

## 3. json 스키마 (pokerGFX RFID)

### 3.1 목적

pokerGFX에서 실시간으로 수집되는 핸드 데이터 저장

### 3.2 테이블 목록

| 테이블 | 설명 | 주요 컬럼 |
|--------|------|----------|
| **gfx_sessions** | GFX 세션 (JSON 파일 단위) | gfx_id (BIGINT UNIQUE), event_title, table_type |
| **hands** | 핸드 메타데이터 | gfx_session_id, hand_number, game_variant, pot_size |
| **hand_players** | 핸드별 플레이어 상태 | hand_id, seat_number, start_stack, end_stack, hole_cards |
| **hand_actions** | 액션 로그 | hand_id, action_order, street, action, bet_amount |
| **hand_cards** | 커뮤니티/홀 카드 | hand_id, card_rank, card_suit, card_type |
| **hand_results** | 핸드 결과 | hand_id, seat_number, is_winner, won_amount, rank_value |

### 3.3 ERD

```
┌─────────────────┐
│  gfx_sessions   │
├─────────────────┤
│ id (PK)         │
│ gfx_id (UNIQUE) │──── Windows FileTime
│ event_title     │
│ table_type      │
│ tournament_id   │──── Soft FK → wsop_plus.tournaments
│ feature_table_id│──── Soft FK → manual.feature_tables
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐
│     hands       │
├─────────────────┤
│ id (PK)         │
│ gfx_session_id  │
│ hand_number     │
│ game_variant    │
│ pot_size        │
│ grade           │──── A, B, C, D
│ is_premium      │
└────────┬────────┘
         │ 1:N (3개 자식)
         ├─────────────────────────┐
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│  hand_players   │       │  hand_actions   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ hand_id (FK)    │       │ hand_id (FK)    │
│ seat_number     │       │ action_order    │
│ player_name     │       │ street          │
│ start_stack     │       │ action          │
│ end_stack       │       │ bet_amount      │
│ hole_cards      │       └─────────────────┘
│ is_winner       │
│ player_master_id│──── Soft FK → manual.players_master
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐
│   hand_cards    │       │  hand_results   │
├─────────────────┤       ├─────────────────┤
│ hand_id (FK)    │       │ hand_id (FK)    │
│ card_rank       │       │ seat_number     │
│ card_suit       │       │ is_winner       │
│ card_type       │       │ won_amount      │
│ seat_number     │       │ rank_value      │
└─────────────────┘       └─────────────────┘
```

### 3.4 주요 특성

- **실시간 데이터**: ~1초 간격 업데이트
- **이벤트 소싱**: hand_actions로 전체 핸드 재현 가능
- **Feature Table 전용**: Other Tables 데이터는 wsop_plus에서 관리

---

## 4. wsop_plus 스키마 (Tournament Operations)

### 4.1 목적

WSOP+ CSV에서 가져오는 토너먼트 운영 데이터 저장

### 4.2 테이블 목록

| 테이블 | 설명 | 주요 컬럼 |
|--------|------|----------|
| **tournaments** | 토너먼트 정보 | name, buy_in, prize_pool, remaining_players |
| **blind_levels** | 블라인드 구조 | tournament_id, level_number, sb, bb, ante |
| **payouts** | 페이아웃 구조 | tournament_id, place_start, place_end, amount |
| **player_instances** | 토너먼트 참가자 | tournament_id, player_name, chips, current_rank |
| **schedules** | 방송 일정 | date, time_start, event_title, channel |

### 4.3 ERD

```
┌─────────────────┐
│   tournaments   │
├─────────────────┤
│ id (PK)         │
│ name            │
│ buy_in          │
│ prize_pool      │
│ remaining_players│
│ status          │
│ event_id        │──── Soft FK → manual.events
└────────┬────────┘
         │ 1:N (3개 자식)
         ├──────────────────────────────────┐
         │                                  │
         ▼                                  ▼
┌─────────────────┐                ┌─────────────────┐
│  blind_levels   │                │    payouts      │
├─────────────────┤                ├─────────────────┤
│ id (PK)         │                │ id (PK)         │
│ tournament_id   │                │ tournament_id   │
│ level_number    │                │ place_start     │
│ small_blind     │                │ place_end       │
│ big_blind       │                │ amount          │
│ ante            │                │ percentage      │
│ is_current      │                │ is_current_bubble│
└─────────────────┘                └─────────────────┘
         │
         ▼
┌─────────────────┐                ┌─────────────────┐
│player_instances │                │   schedules     │
├─────────────────┤                ├─────────────────┤
│ id (PK)         │                │ id (PK)         │
│ tournament_id   │                │ date            │
│ player_name     │                │ time_start      │
│ chips           │                │ event_title     │
│ current_rank    │                │ tournament_id   │──FK
│ is_eliminated   │                │ event_id        │──Soft FK
│ player_master_id│──Soft FK       └─────────────────┘
│ feature_table_id│──Soft FK
└─────────────────┘
```

### 4.4 주요 특성

- **배치 데이터**: CSV 임포트, 레벨 종료 시 업데이트
- **Other Tables 포함**: Feature Table 외 모든 테이블 칩 카운트
- **플레이어 매칭**: player_master_id로 마스터 데이터 연결

---

## 5. manual 스키마 (수작업 입력)

### 5.1 목적

운영팀이 직접 입력하는 마스터 데이터 저장

### 5.2 테이블 목록

| 테이블 | 설명 | 주요 컬럼 |
|--------|------|----------|
| **players_master** | 플레이어 마스터 | name, nationality, wsop_bracelets, total_earnings |
| **player_profiles** | 플레이어 프로필 상세 | player_id, long_name, birth_date, playing_style |
| **commentators** | 코멘테이터 | name, credentials, social_handle |
| **venues** | 장소 | name, city, country, drone_shot_url |
| **events** | 이벤트/시리즈 | event_code, series_name, start_date, end_date |
| **feature_tables** | Feature Table 관리 | table_number, rfid_device_id, is_active |
| **seating_assignments** | 좌석 배정 | player_id, feature_table_id, seat_number |

### 5.3 ERD

```
┌─────────────────┐       ┌─────────────────┐
│ players_master  │       │    venues       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ name            │       │ name            │
│ nationality     │       │ city            │
│ photo_url       │       │ country         │
│ wsop_bracelets  │       │ drone_shot_url  │
│ total_earnings  │       └────────┬────────┘
│ is_key_player   │                │ 1:N
└────────┬────────┘                ▼
         │ 1:1            ┌─────────────────┐
         ▼                │     events      │
┌─────────────────┐       ├─────────────────┤
│ player_profiles │       │ id (PK)         │
├─────────────────┤       │ event_code      │
│ id (PK)         │       │ venue_id (FK)   │
│ player_id (FK)  │       │ start_date      │
│ long_name       │       │ end_date        │
│ birth_date      │       │ sponsor_logos   │
│ playing_style   │       └─────────────────┘
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│  commentators   │       │ feature_tables  │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ name            │       │ table_number    │
│ credentials     │       │ rfid_device_id  │
│ social_handle   │       │ is_active       │
│ photo_url       │       │ tournament_id   │──Soft FK
└─────────────────┘       └────────┬────────┘
                                   │ 1:N
         ┌─────────────────────────┘
         ▼
┌─────────────────┐
│seating_assign   │
├─────────────────┤
│ id (PK)         │
│ player_id (FK)  │──► players_master
│ feature_table_id│
│ seat_number     │
│ is_current      │
└─────────────────┘
```

### 5.4 주요 특성

- **마스터 데이터**: 토너먼트 무관 영구 데이터
- **중복 제거**: players_master로 플레이어 통합 관리
- **수동 입력**: 자동화 불가능한 데이터 (프로필, 코멘테이터)

---

## 6. 스키마별 설계 원칙

| 원칙 | 적용 |
|------|------|
| **UUID PK** | 모든 테이블 `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` |
| **JSONB 유연성** | 복잡한 구조는 JSONB 컬럼 사용 (payouts, social_links) |
| **TIMESTAMPTZ** | 모든 시간 컬럼은 타임존 포함 |
| **Soft Delete** | is_active, is_eliminated 등 Boolean 플래그 |
| **Auto Timestamp** | created_at, updated_at 자동 갱신 트리거 |
| **Unique Constraint** | 비즈니스 키에 UNIQUE 제약 (gfx_id, event_code) |

---

## 다음 파트

→ [Part 3: Cross-Schema Mapping](03-cross-schema-mapping.md)


---

# PRD-0007 Part 3: Cross-Schema Mapping

## 1. 스키마 간 관계 개요

4개 스키마는 **Soft FK**와 **Cross-Schema View**로 연결됩니다.

```
┌─────────┐                           ┌───────────┐
│   ae    │                           │   json    │
│         │                           │           │
│ layer_  │                           │ gfx_      │
│ data_   │──source_schema────────────│ sessions  │
│ mappings│  source_table             │           │
│         │  source_column            │ hands     │
│         │                           │           │
│         │                           │ hand_     │
│         │                           │ players   │
└────┬────┘                           └─────┬─────┘
     │                                      │
     │  ┌────────────────────────────────┐  │
     │  │      Soft FK 참조 관계         │  │
     │  └────────────────────────────────┘  │
     │                                      │
     │  tournament_id ─────────────────┐    │ tournament_id
     │  player_master_id ──────────┐   │    │ feature_table_id
     │  feature_table_id ─────┐    │   │    │ player_master_id
     │                        │    │   │    │
     ▼                        ▼    ▼   ▼    ▼
┌─────────────────────────────────────────────────┐
│                    manual                        │
│                                                 │
│  players_master ◀─────── player_master_id       │
│  feature_tables ◀─────── feature_table_id       │
│  events         ◀─────── event_id               │
│  venues         ◀─────── venue_id               │
│                                                 │
└─────────────────────────────────────────────────┘
                         ▲
                         │
┌─────────────────────────────────────────────────┐
│                  wsop_plus                       │
│                                                 │
│  tournaments ────────────── tournament_id ◀──   │
│  player_instances ───────── player_master_id    │
│  schedules ──────────────── event_id            │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 2. Soft FK 전략

### 2.1 정의

**Soft FK**: 외래 키 제약 조건 없이 UUID 컬럼으로 참조하는 방식

```sql
-- Hard FK (제약 조건 있음)
tournament_id UUID REFERENCES wsop_plus.tournaments(id) ON DELETE CASCADE

-- Soft FK (제약 조건 없음, 주석으로 문서화)
tournament_id UUID,  -- Soft FK → wsop_plus.tournaments
```

### 2.2 Soft FK를 사용하는 이유

| 이유 | 설명 |
|------|------|
| **스키마 독립성** | 스키마별 독립 배포/마이그레이션 가능 |
| **삭제 유연성** | 참조 대상 삭제 시 오류 없이 NULL 유지 |
| **성능** | FK 검증 오버헤드 제거 |
| **순환 참조 방지** | 크로스 스키마 순환 참조 문제 해결 |

### 2.3 Soft FK 목록

| 소스 테이블 | 컬럼 | 대상 테이블 |
|------------|------|------------|
| **json.gfx_sessions** | tournament_id | wsop_plus.tournaments |
| **json.gfx_sessions** | feature_table_id | manual.feature_tables |
| **json.gfx_sessions** | event_id | manual.events |
| **json.hand_players** | player_master_id | manual.players_master |
| **wsop_plus.tournaments** | event_id | manual.events |
| **wsop_plus.tournaments** | venue_id | manual.venues |
| **wsop_plus.player_instances** | player_master_id | manual.players_master |
| **wsop_plus.player_instances** | feature_table_id | manual.feature_tables |
| **wsop_plus.schedules** | event_id | manual.events |
| **wsop_plus.schedules** | venue_id | manual.venues |
| **manual.feature_tables** | tournament_id | wsop_plus.tournaments |
| **ae.layer_data_mappings** | source_schema + source_table | 동적 참조 |

---

## 3. ae.layer_data_mappings 매핑

### 3.1 매핑 구조

`ae.layer_data_mappings` 테이블은 AE 레이어와 데이터 소스를 연결:

```sql
CREATE TABLE ae.layer_data_mappings (
    layer_id UUID UNIQUE NOT NULL,      -- 대상 레이어
    source_schema VARCHAR(50) NOT NULL, -- 'json', 'wsop_plus', 'manual'
    source_table VARCHAR(100) NOT NULL, -- 'players_master', 'hands'
    source_column VARCHAR(100) NOT NULL,-- 'name', 'chips'
    source_path TEXT,                   -- JSONB 경로: 'payouts[0].amount'
    transform_type VARCHAR(50),         -- 'format_number', 'uppercase'
    transform_config JSONB DEFAULT '{}'
);
```

### 3.2 매핑 예시

| 레이어 | source_schema | source_table | source_column | transform |
|--------|---------------|--------------|---------------|-----------|
| Name 1 | manual | players_master | display_name | uppercase |
| Chips 1 | wsop_plus | player_instances | chips | format_number |
| BBs 1 | wsop_plus | player_instances | bb_count | - |
| Flag 1 | manual | players_master | nationality | flag_path |
| Blinds | wsop_plus | blind_levels | blinds_display | - |
| Hole Card 1 | json | hand_players | hole_card_1 | - |
| Pot Size | json | hands | pot_size | format_chips |
| Winner | json | hand_results | player_name | uppercase |

### 3.3 매핑 SQL 예시

```sql
-- Feature Table Leaderboard 매핑
INSERT INTO ae.layer_data_mappings (layer_id, source_schema, source_table, source_column, transform_type)
VALUES
  -- Name 레이어들
  ('uuid-name-1', 'manual', 'players_master', 'display_name', 'uppercase'),
  ('uuid-name-2', 'manual', 'players_master', 'display_name', 'uppercase'),

  -- Chips 레이어들
  ('uuid-chips-1', 'wsop_plus', 'player_instances', 'chips', 'format_number'),
  ('uuid-chips-2', 'wsop_plus', 'player_instances', 'chips', 'format_number'),

  -- Flag 레이어들 (국적 → 플래그 이미지 경로)
  ('uuid-flag-1', 'manual', 'players_master', 'nationality', 'flag_path');
```

---

## 4. Cross-Schema Views

### 4.1 v_feature_table_leaderboard

Feature Table의 현재 리더보드:

```sql
CREATE VIEW public.v_feature_table_leaderboard AS
SELECT
    -- Feature Table 정보
    ft.id AS feature_table_id,
    ft.table_name,
    ft.table_number,

    -- 플레이어 마스터 정보
    pm.id AS player_master_id,
    pm.name,
    pm.display_name,
    pm.nationality,
    pm.photo_url,
    pm.wsop_bracelets,

    -- 토너먼트 인스턴스 정보
    pi.chips,
    pi.current_rank,
    pi.bb_count,
    pi.rank_change,

    -- 좌석 정보
    sa.seat_number

FROM manual.feature_tables ft
JOIN manual.seating_assignments sa
    ON ft.id = sa.feature_table_id AND sa.is_current = TRUE
JOIN manual.players_master pm
    ON sa.player_id = pm.id
LEFT JOIN wsop_plus.player_instances pi
    ON pi.player_master_id = pm.id
    AND pi.tournament_id::text = ft.tournament_id::text
WHERE ft.is_active = TRUE
ORDER BY ft.table_number, pi.chips DESC;
```

### 4.2 v_unified_players

플레이어 통합 뷰 (마스터 + 인스턴스):

```sql
CREATE VIEW public.v_unified_players AS
SELECT
    pm.id AS player_master_id,
    pm.name,
    pm.display_name,
    pm.nationality,
    pm.photo_url,
    pm.wsop_bracelets,
    pm.total_earnings,

    pi.id AS player_instance_id,
    pi.tournament_id,
    pi.chips,
    pi.current_rank,
    pi.bb_count,
    pi.is_eliminated,

    t.name AS tournament_name,
    t.current_level,
    t.buy_in,
    t.prize_pool

FROM manual.players_master pm
LEFT JOIN wsop_plus.player_instances pi
    ON pi.player_master_id = pm.id
LEFT JOIN wsop_plus.tournaments t
    ON pi.tournament_id = t.id;
```

### 4.3 v_unified_hands

핸드 통합 뷰 (GFX + 마스터 플레이어):

```sql
CREATE VIEW public.v_unified_hands AS
SELECT
    h.id AS hand_id,
    h.hand_number,
    h.game_variant,
    h.pot_size,
    h.grade,
    h.is_premium,
    h.started_at,
    h.completed_at,

    hp.seat_number,
    hp.player_name AS gfx_player_name,
    hp.start_stack,
    hp.end_stack,
    hp.stack_delta,
    hp.hole_cards_normalized,
    hp.is_winner,

    -- 마스터 플레이어 매칭
    pm.id AS player_master_id,
    pm.display_name,
    pm.nationality,
    pm.photo_url

FROM json.hands h
JOIN json.hand_players hp ON h.id = hp.hand_id
LEFT JOIN manual.players_master pm
    ON LOWER(pm.name) = LOWER(hp.player_name);
```

### 4.4 v_current_blind_level

현재 블라인드 레벨:

```sql
CREATE VIEW public.v_current_blind_level AS
SELECT
    t.id AS tournament_id,
    t.name AS tournament_name,
    bl.level_number,
    bl.small_blind,
    bl.big_blind,
    bl.ante,
    bl.blinds_display,
    bl.duration_minutes,
    bl.started_at,
    bl.ends_at,
    bl.time_remaining_seconds
FROM wsop_plus.tournaments t
JOIN wsop_plus.blind_levels bl
    ON t.id = bl.tournament_id AND bl.is_current = TRUE
WHERE t.status IN ('running', 'final_table');
```

---

## 5. 26개 자막 유형 매핑

### 5.1 자막 → 스키마 매핑 매트릭스

| # | 자막 유형 | ae | json | wsop_plus | manual |
|---|----------|:--:|:----:|:---------:|:------:|
| 1 | Tournament Leaderboard | ✓ | | ✓ | ✓ |
| 2 | Feature Table LB | ✓ | ✓ | ✓ | ✓ |
| 3 | Mini Chip Counts | ✓ | ✓ | ✓ | ✓ |
| 4 | Payouts | ✓ | | ✓ | |
| 5 | Mini Payouts | ✓ | | ✓ | |
| 6 | Player Profile | ✓ | | ✓ | ✓ |
| 7 | Player Intro Card | ✓ | | | ✓ |
| 8 | At Risk | ✓ | | ✓ | ✓ |
| 9 | Elimination Banner | ✓ | | ✓ | ✓ |
| 10 | Commentator Profile | ✓ | | | ✓ |
| 11 | Heads-Up Comparison | ✓ | ✓ | ✓ | ✓ |
| 12 | Chip Flow | ✓ | ✓ | | |
| 13 | Chip Comparison | ✓ | ✓ | | |
| 14 | Chips In Play | ✓ | | ✓ | |
| 15 | VPIP Stats | ✓ | ✓ | | |
| 16 | Chip Stack Bar | ✓ | | ✓ | ✓ |
| 17 | Broadcast Schedule | ✓ | | ✓ | ✓ |
| 18 | Event Info | ✓ | | ✓ | ✓ |
| 19 | Venue/Location | ✓ | | | ✓ |
| 20 | Tournament Info | ✓ | | ✓ | ✓ |
| 21 | Event Name | ✓ | | | ✓ |
| 22 | Blind Level | ✓ | | ✓ | |
| 23 | L-Bar (Standard) | ✓ | ✓ | ✓ | |
| 24 | L-Bar (Regi Open) | ✓ | | ✓ | |
| 25 | L-Bar (Regi Close) | ✓ | | ✓ | |
| 26 | Transition/Stinger | ✓ | | | |

### 5.2 데이터 소스 우선순위

동일 필드에 여러 소스가 있을 때:

```
1. json (실시간) - Feature Table 전용
2. wsop_plus (배치) - Other Tables + 토너먼트 정보
3. manual (수동) - 프로필, 보정
```

예: 플레이어 칩 카운트
```
Feature Table → json.hand_players.end_stack (실시간)
Other Tables → wsop_plus.player_instances.chips (배치)
```

---

## 6. 데이터 조인 패턴

### 6.1 Feature Table Leaderboard 조회

```sql
-- Feature Table의 현재 리더보드 (순위순)
SELECT
    sa.seat_number,
    pm.display_name,
    pm.nationality,
    COALESCE(hp.end_stack, pi.chips) AS chips,
    pi.current_rank,
    pi.bb_count
FROM manual.feature_tables ft
JOIN manual.seating_assignments sa ON ft.id = sa.feature_table_id
JOIN manual.players_master pm ON sa.player_id = pm.id
LEFT JOIN wsop_plus.player_instances pi ON pi.player_master_id = pm.id
LEFT JOIN json.gfx_sessions gs ON gs.feature_table_id = ft.id
LEFT JOIN json.hands h ON h.gfx_session_id = gs.id
    AND h.hand_number = (SELECT MAX(hand_number) FROM json.hands WHERE gfx_session_id = gs.id)
LEFT JOIN json.hand_players hp ON hp.hand_id = h.id
    AND LOWER(hp.player_name) = LOWER(pm.name)
WHERE ft.is_active = TRUE
ORDER BY COALESCE(hp.end_stack, pi.chips) DESC;
```

### 6.2 핸드 결과 + 플레이어 정보

```sql
-- 특정 핸드의 결과와 플레이어 마스터 정보
SELECT
    h.hand_number,
    h.pot_size,
    h.grade,
    hr.seat_number,
    hr.player_name AS gfx_name,
    hr.is_winner,
    hr.won_amount,
    hr.hand_rank,
    pm.display_name,
    pm.nationality,
    pm.photo_url,
    pm.wsop_bracelets
FROM json.hand_results hr
JOIN json.hands h ON hr.hand_id = h.id
LEFT JOIN manual.players_master pm
    ON LOWER(pm.name) = LOWER(hr.player_name)
WHERE h.id = 'hand-uuid'
ORDER BY hr.is_winner DESC, hr.won_amount DESC;
```

### 6.3 플레이어 이름 매칭 전략

GFX player_name과 마스터 데이터 매칭:

```sql
-- 매칭 우선순위
-- 1. 정확히 일치 (대소문자 무시)
-- 2. display_name 일치
-- 3. alternative_names JSONB 포함 여부

SELECT pm.*
FROM manual.players_master pm
WHERE
    LOWER(pm.name) = LOWER('DANIEL NEGREANU')
    OR LOWER(pm.display_name) = LOWER('DANIEL NEGREANU')
    OR pm.alternate_names @> '"DANIEL NEGREANU"'::jsonb
LIMIT 1;
```

---

## 7. 데이터 무결성 보장

### 7.1 애플리케이션 레벨 검증

Soft FK이므로 애플리케이션에서 검증:

```python
async def validate_soft_fk(
    session: AsyncSession,
    source_id: UUID,
    target_schema: str,
    target_table: str
) -> bool:
    """Soft FK 유효성 검증"""
    if source_id is None:
        return True  # NULL은 허용

    query = text(f"SELECT EXISTS(SELECT 1 FROM {target_schema}.{target_table} WHERE id = :id)")
    result = await session.execute(query, {"id": source_id})
    return result.scalar()
```

### 7.2 정기 정합성 검사

```sql
-- 고아 레코드 검출 (참조 대상 없는 Soft FK)
SELECT
    'json.gfx_sessions' AS source_table,
    COUNT(*) AS orphan_count
FROM json.gfx_sessions gs
WHERE gs.tournament_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM wsop_plus.tournaments t WHERE t.id = gs.tournament_id
  )

UNION ALL

SELECT
    'wsop_plus.player_instances' AS source_table,
    COUNT(*) AS orphan_count
FROM wsop_plus.player_instances pi
WHERE pi.player_master_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM manual.players_master pm WHERE pm.id = pi.player_master_id
  );
```

---

## 다음 파트

→ [Part 4: Data Flow](04-data-flow.md)


---

# PRD-0007 Part 5: Implementation Guide

## 1. Migration 파일 구조

### 1.1 파일 목록

```
supabase/migrations/
├── 20260110000000_create_schemas.sql        # 4개 스키마 생성
├── 20260110000100_ae_schema_tables.sql      # ae 스키마 7개 테이블
├── 20260110000200_json_schema_tables.sql    # json 스키마 6개 테이블
├── 20260110000300_wsop_plus_schema_tables.sql  # wsop_plus 5개 테이블
├── 20260110000400_manual_schema_tables.sql  # manual 스키마 7개 테이블
├── 20260110000500_indexes.sql               # 전체 인덱스 (90+)
├── 20260110000600_functions_triggers.sql    # 함수 7개 + 트리거 20+
└── 20260110000700_rls_policies.sql          # RLS 정책
```

### 1.2 실행 순서

Migration 파일은 **타임스탬프 순서**로 자동 실행됩니다:

```
1. create_schemas       → 스키마 네임스페이스 생성
2. ae_schema_tables     → ae.* 테이블 생성
3. json_schema_tables   → json.* 테이블 생성
4. wsop_plus_tables     → wsop_plus.* 테이블 생성
5. manual_tables        → manual.* 테이블 생성
6. indexes              → 인덱스 생성
7. functions_triggers   → 함수/트리거 생성
8. rls_policies         → RLS 활성화 및 정책 적용
```

---

## 2. 적용 방법

### 2.1 로컬 개발 환경

```powershell
# 1. Supabase CLI 시작
cd C:\claude\automation_sub
supabase start

# 2. Migration 적용 (로컬 DB 초기화 + 적용)
supabase db reset

# 3. 상태 확인
supabase db status
```

### 2.2 원격 Supabase 프로젝트

```powershell
# 1. 프로젝트 연결
supabase link --project-ref YOUR_PROJECT_REF

# 2. Migration 푸시
supabase db push

# 3. 확인
supabase db diff
```

### 2.3 수동 적용 (SQL 직접 실행)

```powershell
# 파일 순서대로 실행
psql -h localhost -p 54322 -U postgres -d postgres \
  -f supabase/migrations/20260110000000_create_schemas.sql \
  -f supabase/migrations/20260110000100_ae_schema_tables.sql \
  -f supabase/migrations/20260110000200_json_schema_tables.sql \
  -f supabase/migrations/20260110000300_wsop_plus_schema_tables.sql \
  -f supabase/migrations/20260110000400_manual_schema_tables.sql \
  -f supabase/migrations/20260110000500_indexes.sql \
  -f supabase/migrations/20260110000600_functions_triggers.sql \
  -f supabase/migrations/20260110000700_rls_policies.sql
```

---

## 3. 검증 체크리스트

### 3.1 스키마 생성 확인

```sql
-- 4개 스키마 존재 확인
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name IN ('ae', 'json', 'wsop_plus', 'manual')
ORDER BY schema_name;

-- 예상 결과:
-- ae
-- json
-- manual
-- wsop_plus
```

### 3.2 테이블 카운트 확인

```sql
-- 스키마별 테이블 수
SELECT
    table_schema,
    COUNT(*) AS table_count
FROM information_schema.tables
WHERE table_schema IN ('ae', 'json', 'wsop_plus', 'manual')
GROUP BY table_schema
ORDER BY table_schema;

-- 예상 결과:
-- ae: 7
-- json: 6
-- manual: 7
-- wsop_plus: 5
```

### 3.3 테이블 상세 확인

```sql
-- 전체 테이블 목록
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('ae', 'json', 'wsop_plus', 'manual')
ORDER BY table_schema, table_name;
```

### 3.4 인덱스 확인

```sql
-- 인덱스 목록
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname IN ('ae', 'json', 'wsop_plus', 'manual')
ORDER BY schemaname, tablename, indexname;
```

### 3.5 RLS 활성화 확인

```sql
-- RLS 상태 확인
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname IN ('ae', 'json', 'wsop_plus', 'manual')
ORDER BY schemaname, tablename;

-- 모든 rowsecurity가 TRUE여야 함
```

### 3.6 트리거 확인

```sql
-- 트리거 목록
SELECT
    event_object_schema,
    event_object_table,
    trigger_name
FROM information_schema.triggers
WHERE event_object_schema IN ('ae', 'json', 'wsop_plus', 'manual')
ORDER BY event_object_schema, event_object_table;
```

### 3.7 함수 확인

```sql
-- 함수 목록
SELECT
    n.nspname AS schema,
    p.proname AS function_name
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname IN ('ae', 'json', 'wsop_plus', 'manual', 'public')
  AND p.proname LIKE '%update%' OR p.proname LIKE '%convert%' OR p.proname LIKE '%format%'
ORDER BY n.nspname, p.proname;
```

---

## 4. API 연동 가이드

### 4.1 Supabase Client 설정

```typescript
// supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.SUPABASE_URL!
const supabaseKey = process.env.SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseKey, {
  db: {
    schema: 'public'  // 기본 스키마
  }
})

// 스키마별 클라이언트
export const aeClient = createClient(supabaseUrl, supabaseKey, {
  db: { schema: 'ae' }
})

export const jsonClient = createClient(supabaseUrl, supabaseKey, {
  db: { schema: 'json' }
})

export const wsopPlusClient = createClient(supabaseUrl, supabaseKey, {
  db: { schema: 'wsop_plus' }
})

export const manualClient = createClient(supabaseUrl, supabaseKey, {
  db: { schema: 'manual' }
})
```

### 4.2 기본 CRUD 예시

```typescript
// players_master 조회
const { data: players, error } = await manualClient
  .from('players_master')
  .select('*')
  .eq('is_active', true)
  .order('wsop_bracelets', { ascending: false })

// 토너먼트 조회 + 블라인드 레벨
const { data: tournament } = await wsopPlusClient
  .from('tournaments')
  .select(`
    *,
    blind_levels!inner(*)
  `)
  .eq('status', 'running')
  .eq('blind_levels.is_current', true)
  .single()

// GFX 세션 + 핸드 조회
const { data: session } = await jsonClient
  .from('gfx_sessions')
  .select(`
    *,
    hands(
      *,
      hand_players(*),
      hand_results(*)
    )
  `)
  .eq('gfx_id', 638961999170907267)
  .single()
```

### 4.3 Cross-Schema 조회 (Raw SQL)

```typescript
// 크로스 스키마 뷰 사용
const { data } = await supabase
  .rpc('get_feature_table_leaderboard', {
    p_feature_table_id: 'uuid-here'
  })

// 또는 직접 SQL 실행
const { data } = await supabase
  .from('v_feature_table_leaderboard')
  .select('*')
  .eq('feature_table_id', 'uuid-here')
```

### 4.4 Realtime 구독

```typescript
// 핸드 업데이트 구독
const channel = supabase
  .channel('hand-updates')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'json',
      table: 'hands'
    },
    (payload) => {
      console.log('New hand:', payload.new)
    }
  )
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'wsop_plus',
      table: 'player_instances',
      filter: 'is_eliminated=eq.false'
    },
    (payload) => {
      console.log('Chip update:', payload.new)
    }
  )
  .subscribe()
```

---

## 5. 데이터 임포트 가이드

### 5.1 pokerGFX JSON 임포트

```python
# import_pokergfx.py
import json
from supabase import create_client

def import_gfx_session(file_path: str):
    with open(file_path) as f:
        data = json.load(f)

    # 1. 세션 생성
    session = supabase.table('gfx_sessions').insert({
        'gfx_id': data['ID'],
        'event_title': data['EventTitle'],
        'table_type': data['Type'],
        'software_version': data['SoftwareVersion'],
        'created_at_gfx': data['CreatedDateTimeUTC'],
        'payouts': data.get('Payouts', [])
    }).execute()

    session_id = session.data[0]['id']

    # 2. 핸드 임포트
    for hand in data['Hands']:
        import_hand(session_id, hand)

def import_hand(session_id: str, hand_data: dict):
    # 핸드 생성
    hand = supabase.table('hands').insert({
        'gfx_session_id': session_id,
        'hand_number': hand_data['HandNum'],
        'game_variant': hand_data['GameVariant'],
        'bet_structure': hand_data['BetStructure'],
        # ... 기타 필드
    }).execute()

    hand_id = hand.data[0]['id']

    # 플레이어 임포트
    for player in hand_data['Players']:
        supabase.table('hand_players').insert({
            'hand_id': hand_id,
            'seat_number': player['PlayerNum'],
            'player_name': player['Name'],
            'start_stack': player['StartStackAmt'],
            'end_stack': player['EndStackAmt'],
            'hole_cards': player.get('HoleCards'),
            # ... 기타 필드
        }).execute()

    # 액션, 카드, 결과 임포트...
```

### 5.2 WSOP+ CSV 임포트

```python
# import_wsop_csv.py
import pandas as pd

def import_tournament_csv(file_path: str, tournament_id: str):
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        # 플레이어 마스터 찾기 또는 생성
        player = find_or_create_player(row['Name'], row.get('Nationality'))

        # 플레이어 인스턴스 업서트
        supabase.table('player_instances').upsert({
            'tournament_id': tournament_id,
            'player_name': row['Name'],
            'chips': row['Chips'],
            'current_rank': row['Rank'],
            'player_master_id': player['id']
        }, on_conflict='tournament_id,player_name').execute()
```

---

## 6. config.toml 설정

### 6.1 API 스키마 노출

```toml
# supabase/config.toml

[api]
# 4개 스키마를 API로 노출
schemas = ["public", "ae", "json", "wsop_plus", "manual"]
extra_search_path = ["public", "extensions"]
max_rows = 1000
```

### 6.2 Realtime 설정

```toml
[realtime]
enabled = true
# IP 허용 (개발용)
ip_range = "0.0.0.0/0"

# 변경 감지할 테이블
[[realtime.subscriptions]]
schema = "json"
tables = ["gfx_sessions", "hands", "hand_players"]

[[realtime.subscriptions]]
schema = "wsop_plus"
tables = ["tournaments", "player_instances", "blind_levels"]
```

---

## 7. 트러블슈팅

### 7.1 스키마 접근 오류

```
오류: permission denied for schema ae

해결:
GRANT USAGE ON SCHEMA ae TO anon, authenticated, service_role;
```

### 7.2 RLS 정책 차단

```
오류: new row violates row-level security policy

해결:
1. 정책 확인: SELECT * FROM pg_policies WHERE schemaname = 'ae';
2. 정책 추가: CREATE POLICY ... ON ae.table_name ...
3. 또는 service_role 키 사용
```

### 7.3 Cross-Schema 조인 오류

```
오류: relation "json.hands" does not exist

해결:
1. 스키마 검색 경로 확인: SHOW search_path;
2. 설정: SET search_path TO public, ae, json, wsop_plus, manual;
3. 또는 풀 네임 사용: json.hands
```

### 7.4 Soft FK 정합성 오류

```
문제: tournament_id가 참조하는 레코드가 없음

해결:
1. 데이터 정합성 검사 스크립트 실행
2. 고아 레코드 NULL 처리 또는 삭제
3. 임포트 시 참조 대상 먼저 생성
```

---

## 8. 성능 최적화

### 8.1 권장 인덱스

이미 migration에 포함되어 있지만, 추가로 필요한 경우:

```sql
-- 자주 사용되는 조인 컬럼
CREATE INDEX CONCURRENTLY idx_json_hp_player_name_lower
ON json.hand_players (LOWER(player_name));

-- GIN 인덱스 (JSONB 검색용)
CREATE INDEX CONCURRENTLY idx_manual_players_alternate_names
ON manual.players_master USING gin (alternate_names);
```

### 8.2 Materialized View

자주 사용되는 크로스 스키마 조회:

```sql
CREATE MATERIALIZED VIEW public.mv_feature_table_leaderboard AS
SELECT ... -- v_feature_table_leaderboard와 동일
WITH DATA;

-- 주기적 새로고침
REFRESH MATERIALIZED VIEW CONCURRENTLY public.mv_feature_table_leaderboard;
```

---

## 9. 체크리스트

### 9.1 배포 전 체크리스트

- [ ] 모든 migration 파일 생성 완료
- [ ] 로컬 환경에서 `supabase db reset` 성공
- [ ] 스키마 4개 생성 확인
- [ ] 테이블 25개 생성 확인
- [ ] 인덱스 생성 확인
- [ ] RLS 활성화 확인
- [ ] 트리거 동작 확인 (`updated_at` 자동 갱신)
- [ ] config.toml API schemas 설정

### 9.2 통합 테스트 체크리스트

- [ ] 플레이어 마스터 CRUD
- [ ] 토너먼트 + 블라인드 레벨 조회
- [ ] GFX 세션 + 핸드 임포트
- [ ] Cross-Schema 뷰 조회
- [ ] Realtime 구독 동작

---

## 관련 문서

| 문서 | 설명 |
|------|------|
| [PRD-0004](../0004-prd-caption-database-schema.md) | 기존 wsop 단일 스키마 |
| [PRD-0006](../0006-prd-aep-data-elements.md) | AEP 데이터 요소 명세 |
| [Supabase Docs](https://supabase.com/docs) | Supabase 공식 문서 |


---