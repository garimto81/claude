# PRD-0007 Part 1: Overview

## 1. 목적

WSOP 방송 그래픽 자막 시스템의 데이터베이스를 **4개 분리 스키마**로 재설계하여:

1. **데이터 소스별 독립적 관리** - 각 소스의 특성에 맞는 테이블 구조
2. **업데이트 주기 분리** - 실시간, 배치, 수동 데이터의 독립적 처리
3. **권한 세분화** - 스키마별 RLS 정책 적용
4. **확장성 확보** - 새 데이터 소스 추가 시 스키마 추가로 대응

---

## 2. 범위

### 포함

| 항목 | 설명 |
|------|------|
| 4개 스키마 설계 | ae, json, wsop_plus, manual |
| 25개 테이블 정의 | 각 스키마별 테이블 구조 |
| 크로스 스키마 관계 | Soft FK, 공유 뷰 |
| RLS 정책 | 스키마별 권한 설정 |
| Migration 파일 | Supabase 적용 가능한 SQL |

### 제외

| 항목 | 사유 |
|------|------|
| 렌더링 파이프라인 | PRD-0001에서 정의 |
| API 엔드포인트 상세 | 별도 API 설계 문서 |
| 프론트엔드 UI | 별도 UI 설계 문서 |

---

## 3. 스키마 분리 전략

### 3.1 분리 기준

```
데이터 소스 × 업데이트 주기 = 스키마
```

| 스키마 | 데이터 소스 | 업데이트 주기 | 특성 |
|--------|------------|--------------|------|
| **ae** | AEP 파일 분석 | On-demand | 템플릿 메타데이터, 정적 |
| **json** | pokerGFX RFID | ~1초 | 실시간 핸드 데이터 |
| **wsop_plus** | WSOP+ CSV | 배치/이벤트 | 토너먼트 운영 데이터 |
| **manual** | 운영팀 입력 | 수동 | 마스터 데이터 |

### 3.2 분리 이점

```
기존 (단일 wsop 스키마)
┌─────────────────────────────────┐
│           wsop                  │
│  21개 테이블 (혼재)              │
│  - 실시간 + 배치 + 수동 혼합     │
│  - 단일 RLS 정책                │
│  - 복잡한 의존성                 │
└─────────────────────────────────┘

신규 (4개 분리 스키마)
┌─────────┐ ┌─────────┐ ┌───────────┐ ┌─────────┐
│   ae    │ │  json   │ │ wsop_plus │ │ manual  │
│ 7 tables│ │ 6 tables│ │ 5 tables  │ │ 7 tables│
│ 정적    │ │ 실시간  │ │ 배치      │ │ 수동    │
│ 독립RLS │ │ 독립RLS │ │ 독립RLS   │ │ 독립RLS │
└────┬────┘ └────┬────┘ └─────┬─────┘ └────┬────┘
     │           │            │            │
     └───────────┴─────┬──────┴────────────┘
                       │
              Soft FK / 공유 뷰
```

---

## 4. 기존 PRD와의 관계

### 4.1 PRD-0004 (Caption DB Schema) 대체

| PRD-0004 | PRD-0007 | 변경 |
|----------|----------|------|
| wsop 단일 스키마 | 4개 분리 스키마 | 분리 |
| 21개 테이블 | 25개 테이블 | +4개 |
| Hard FK | Soft FK + 뷰 | 유연성 |

### 4.2 PRD-0006 (AEP Data Elements) 연계

PRD-0006의 AEP 레이어 → DB 필드 매핑을 **ae.layer_data_mappings** 테이블로 구현

```
PRD-0006 정의          →  PRD-0007 구현
─────────────────────────────────────────
AEP 동적 레이어        →  ae.composition_layers
레이어-필드 매핑       →  ae.layer_data_mappings
데이터 소스 (json)     →  json.* 테이블
데이터 소스 (wsop+)    →  wsop_plus.* 테이블
데이터 소스 (manual)   →  manual.* 테이블
```

---

## 5. 용어 정의

| 용어 | 정의 |
|------|------|
| **Soft FK** | 외래 키 제약 조건 없이 UUID로 참조하는 방식 |
| **Hard FK** | REFERENCES 제약 조건이 있는 외래 키 |
| **Cross-Schema View** | 여러 스키마의 테이블을 조인하는 뷰 |
| **GFX Session** | pokerGFX JSON 파일 하나에 해당하는 세션 |
| **Hand** | 포커 한 핸드 (딜링~승자 결정) |
| **Player Instance** | 특정 토너먼트에 참가한 플레이어 인스턴스 |
| **Player Master** | 플레이어 마스터 레코드 (토너먼트 무관) |

---

## 6. 목표

### 필수 목표 (Must Have)

- [ ] 4개 스키마 생성 및 권한 설정
- [ ] 25개 테이블 생성 (인덱스 포함)
- [ ] 자동 업데이트 트리거 설정
- [ ] RLS 정책 활성화
- [ ] 크로스 스키마 뷰 생성

### 권장 목표 (Should Have)

- [ ] 데이터 검증 함수
- [ ] 실시간 구독 (Realtime) 설정
- [ ] 성능 최적화 인덱스

### 선택 목표 (Nice to Have)

- [ ] 데이터 품질 대시보드
- [ ] 자동 데이터 동기화 함수

---

## 7. 비목표 (Non-Goals)

| 항목 | 사유 |
|------|------|
| 기존 wsop 스키마 마이그레이션 | 새 프로젝트로 시작 |
| 프론트엔드 구현 | 별도 프로젝트 |
| API 구현 | 별도 백엔드 프로젝트 |
| 렌더링 파이프라인 | PRD-0001 범위 |

---

## 8. 성공 기준

| 기준 | 측정 방법 |
|------|----------|
| 스키마 생성 완료 | `SELECT schema_name FROM information_schema.schemata` |
| 테이블 25개 생성 | 스키마별 테이블 카운트 |
| RLS 활성화 | `pg_tables.rowsecurity = TRUE` |
| 인덱스 생성 | `pg_indexes` 조회 |
| 트리거 동작 | `updated_at` 자동 갱신 확인 |

---

## 다음 파트

→ [Part 2: Schema Architecture](02-schema-architecture.md)


---

# PRD-0007 Part 4: Data Flow

## 1. 전체 데이터 흐름

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            External Data Sources                             │
└─────────────────────────────────────────────────────────────────────────────┘
        │                    │                    │                    │
        ▼                    ▼                    ▼                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  AEP Files  │    │ pokerGFX    │    │  WSOP+      │    │  Admin UI   │
│  (.aep)     │    │ JSON        │    │  CSV        │    │  (Web)      │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ JSX Parser       │ JSON Parser      │ CSV Parser       │ API
       ▼                  ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ ae schema   │    │ json schema │    │ wsop_plus   │    │ manual      │
│             │    │             │    │ schema      │    │ schema      │
│ templates   │    │ gfx_sessions│    │ tournaments │    │ players_    │
│ compositions│    │ hands       │    │ blind_levels│    │   master    │
│ layers      │    │ hand_players│    │ payouts     │    │ venues      │
│ mappings    │    │ hand_actions│    │ player_inst │    │ events      │
│ render_jobs │    │ hand_cards  │    │ schedules   │    │ commentators│
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │                  └──────────────────┼──────────────────┘
       │                           │         │
       │                           ▼         │
       │                 ┌─────────────────┐ │
       │                 │ Cross-Schema    │ │
       │                 │ Views           │ │
       │                 └────────┬────────┘ │
       │                          │          │
       └──────────────────────────┼──────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │   Render API    │
                        │                 │
                        │ layer_data_     │
                        │ mappings        │
                        │      ↓          │
                        │ Data Injection  │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Nexrender     │
                        │                 │
                        │ AEP + Data      │
                        │      ↓          │
                        │ Render Output   │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ Broadcast       │
                        │ Graphics        │
                        │ (PNG/MOV)       │
                        └─────────────────┘
```

---

## 2. 데이터 소스별 흐름

### 2.1 AEP 파일 → ae 스키마

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. AEP 파일 스캔                                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   CyprusDesign.aep                                               │
│        │                                                         │
│        ▼                                                         │
│   JSX Script (ExtendScript)                                      │
│        │                                                         │
│        │ 콤포지션 목록 추출                                       │
│        │ 레이어 정보 추출                                         │
│        │ 동적 레이어 식별 (var_, img_, vid_)                      │
│        ▼                                                         │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ ae.templates                                               │ │
│   │   - name: "CyprusDesign"                                   │ │
│   │   - file_path: "C:\...\CyprusDesign.aep"                   │ │
│   │   - checksum: SHA-256                                      │ │
│   └────────────────────────────────────────────────────────────┘ │
│        │                                                         │
│        ▼ 1:N                                                     │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ ae.compositions                                            │ │
│   │   - name: "Feature Table Leaderboard MAIN"                 │ │
│   │   - width: 1920, height: 1080                              │ │
│   │   - comp_type: "leaderboard"                               │ │
│   └────────────────────────────────────────────────────────────┘ │
│        │                                                         │
│        ▼ 1:N                                                     │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ ae.composition_layers                                      │ │
│   │   - layer_name: "Name 1"                                   │ │
│   │   - layer_type: "text"                                     │ │
│   │   - is_dynamic: true                                       │ │
│   └────────────────────────────────────────────────────────────┘ │
│        │                                                         │
│        ▼ 1:1                                                     │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ ae.layer_data_mappings                                     │ │
│   │   - source_schema: "manual"                                │ │
│   │   - source_table: "players_master"                         │ │
│   │   - source_column: "display_name"                          │ │
│   │   - transform_type: "uppercase"                            │ │
│   └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

업데이트 주기: On-demand (템플릿 변경 시)
```

### 2.2 pokerGFX JSON → json 스키마

```
┌──────────────────────────────────────────────────────────────────┐
│ 2. pokerGFX RFID 데이터                                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Feature Table RFID Scanner                                     │
│        │                                                         │
│        │ 실시간 (~1초)                                            │
│        ▼                                                         │
│   JSON File (638961999170907267.json)                            │
│        │                                                         │
│        │ JSON Parser                                             │
│        ▼                                                         │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ json.gfx_sessions                                          │ │
│   │   - gfx_id: 638961999170907267 (Windows FileTime)          │ │
│   │   - event_title: "WSOP Main Event Day 3"                   │ │
│   │   - table_type: "FEATURE_TABLE"                            │ │
│   │   - tournament_id: UUID (Soft FK)                          │ │
│   └────────────────────────────────────────────────────────────┘ │
│        │                                                         │
│        ▼ 1:N                                                     │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ json.hands                                                 │ │
│   │   - hand_number: 1, 2, 3...                                │ │
│   │   - game_variant: "HOLDEM"                                 │ │
│   │   - pot_size: 1500000                                      │ │
│   │   - grade: "A" (A-D 등급)                                   │ │
│   │   - is_premium: true (Royal Flush 등)                       │ │
│   └────────────────────────────────────────────────────────────┘ │
│        │                                                         │
│        ├──────────────────┬──────────────────┐                   │
│        ▼                  ▼                  ▼                   │
│   hand_players       hand_actions       hand_cards               │
│   - seat: 1-10       - action_order    - flop/turn/river        │
│   - player_name      - street          - card_rank/suit          │
│   - start_stack      - action (fold..) - seat_number (hole)      │
│   - end_stack        - bet_amount                                │
│   - hole_cards       - pot_size_after                            │
│                                                                  │
│        │                                                         │
│        ▼                                                         │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ json.hand_results                                          │ │
│   │   - is_winner: true                                        │ │
│   │   - won_amount: 500000                                     │ │
│   │   - hand_rank: "Full House"                                │ │
│   │   - rank_value: 322 (phevaluator)                          │ │
│   └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

업데이트 주기: ~1초 (실시간)
범위: Feature Table만 (RFID 카드 리더기 테이블)
```

### 2.3 WSOP+ CSV → wsop_plus 스키마

```
┌──────────────────────────────────────────────────────────────────┐
│ 3. WSOP+ 토너먼트 데이터                                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   WSOP+ Tournament Management System                             │
│        │                                                         │
│        │ CSV Export (레벨 종료 시)                                │
│        ▼                                                         │
│   tournament_data.csv                                            │
│   player_chips.csv                                               │
│   blind_structure.csv                                            │
│        │                                                         │
│        │ CSV Parser                                              │
│        ▼                                                         │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ wsop_plus.tournaments                                      │ │
│   │   - name: "WSOP Main Event"                                │ │
│   │   - buy_in: 10000                                          │ │
│   │   - prize_pool: 80000000                                   │ │
│   │   - remaining_players: 27                                  │ │
│   │   - current_level: 32                                      │ │
│   │   - status: "running"                                      │ │
│   └────────────────────────────────────────────────────────────┘ │
│        │                                                         │
│        ├────────────┬────────────┬────────────┐                  │
│        ▼            ▼            ▼            ▼                  │
│   blind_levels   payouts   player_inst   schedules               │
│   - level: 32    - 1st     - chips       - date                  │
│   - sb: 100000   - 2nd     - rank        - time_start            │
│   - bb: 200000   - 3-4th   - is_elim     - event_title           │
│   - ante: 200000 - 5-6th   - seat_num    - channel               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

업데이트 주기: 배치 (레벨 종료, 이벤트 변경 시)
범위: 모든 테이블 (Feature + Other Tables)
```

### 2.4 Admin UI → manual 스키마

```
┌──────────────────────────────────────────────────────────────────┐
│ 4. 수작업 데이터 입력                                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Admin Web UI                                                   │
│        │                                                         │
│        │ REST API / GraphQL                                      │
│        ▼                                                         │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ manual.players_master                                      │ │
│   │   - name: "Daniel Negreanu"                                │ │
│   │   - nationality: "CA"                                      │ │
│   │   - photo_url: "https://..."                               │ │
│   │   - wsop_bracelets: 6                                      │ │
│   │   - total_earnings: 45000000                               │ │
│   │   - is_key_player: true                                    │ │
│   └────────────────────────────────────────────────────────────┘ │
│        │                                                         │
│        ▼ 1:1                                                     │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ manual.player_profiles                                     │ │
│   │   - long_name: "Daniel Negreanu"                           │ │
│   │   - birth_date: "1974-07-26"                               │ │
│   │   - playing_style: "LAG"                                   │ │
│   │   - biography: "Canadian professional..."                  │ │
│   └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│   │ commentators    │  │ venues          │  │ events          │  │
│   │ - name          │  │ - name          │  │ - event_code    │  │
│   │ - credentials   │  │ - city          │  │ - series_name   │  │
│   │ - photo_url     │  │ - country       │  │ - start_date    │  │
│   │ - social_handle │  │ - drone_shot_url│  │ - sponsor_logos │  │
│   └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────────┐│
│   │ manual.feature_tables + seating_assignments                 ││
│   │   - table_number: 1                                         ││
│   │   - rfid_device_id: "RFID001"                               ││
│   │   - seat_number: 1-9                                        ││
│   │   - player_id → players_master                              ││
│   └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

업데이트 주기: 수동 (운영팀 입력)
담당자: PA, PD, Data Manager
```

---

## 3. 렌더링 데이터 흐름

### 3.1 자막 렌더링 요청 처리

```
┌──────────────────────────────────────────────────────────────────┐
│ 렌더링 요청 → 데이터 수집 → 렌더링 실행                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. 렌더링 요청 수신                                            │
│   POST /api/render                                               │
│   {                                                              │
│     "composition_id": "uuid-leaderboard",                        │
│     "tournament_id": "uuid-tournament",                          │
│     "feature_table_id": "uuid-table-1"                           │
│   }                                                              │
│        │                                                         │
│        ▼                                                         │
│   2. 레이어 매핑 조회                                            │
│   SELECT * FROM ae.layer_data_mappings                           │
│   WHERE layer_id IN (SELECT id FROM ae.composition_layers        │
│                      WHERE composition_id = :comp_id)            │
│        │                                                         │
│        ▼                                                         │
│   3. 데이터 수집 (매핑별)                                        │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ source_schema: "manual", source_table: "players_master"    │ │
│   │ → SELECT display_name, nationality, photo_url              │ │
│   │   FROM manual.players_master                               │ │
│   │   WHERE id IN (SELECT player_id FROM seating_assignments   │ │
│   │                WHERE feature_table_id = :table_id)         │ │
│   └────────────────────────────────────────────────────────────┘ │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ source_schema: "wsop_plus", source_table: "player_inst"    │ │
│   │ → SELECT chips, current_rank, bb_count                     │ │
│   │   FROM wsop_plus.player_instances                          │ │
│   │   WHERE tournament_id = :tournament_id                     │ │
│   └────────────────────────────────────────────────────────────┘ │
│   ┌────────────────────────────────────────────────────────────┐ │
│   │ source_schema: "json", source_table: "hand_players"        │ │
│   │ → SELECT end_stack                                         │ │
│   │   FROM json.hand_players hp                                │ │
│   │   JOIN json.hands h ON ...                                 │ │
│   │   WHERE latest hand                                        │ │
│   └────────────────────────────────────────────────────────────┘ │
│        │                                                         │
│        ▼                                                         │
│   4. 데이터 변환 (transform)                                     │
│   - format_number: 1500000 → "1.5M"                             │
│   - uppercase: "Daniel Negreanu" → "DANIEL NEGREANU"            │
│   - flag_path: "CA" → "flags/CA.png"                            │
│        │                                                         │
│        ▼                                                         │
│   5. 렌더 작업 생성                                              │
│   INSERT INTO ae.render_jobs (composition_id, data_payload, ...)│
│   {                                                              │
│     "Name 1": "DANIEL NEGREANU",                                 │
│     "Chips 1": "45.2M",                                          │
│     "Flag 1": "flags/CA.png",                                    │
│     ...                                                          │
│   }                                                              │
│        │                                                         │
│        ▼                                                         │
│   6. Nexrender 실행                                              │
│   - AEP 템플릿 로드                                              │
│   - 데이터 주입                                                  │
│   - 렌더링 실행                                                  │
│   - 결과물 저장                                                  │
│        │                                                         │
│        ▼                                                         │
│   7. 결과 저장                                                   │
│   INSERT INTO ae.render_outputs (render_job_id, file_path, ...)  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 자막별 데이터 조합

| 자막 유형 | json | wsop_plus | manual |
|----------|------|-----------|--------|
| **Feature Table Leaderboard** | hand_players.end_stack (실시간 칩) | player_instances.current_rank | players_master.display_name, nationality |
| **Payouts** | - | payouts.amount, payouts.percentage | events.name |
| **Player Profile** | - | player_instances.chips | players_master.*, player_profiles.* |
| **Commentator** | - | - | commentators.* |
| **Blind Level** | - | blind_levels.* | - |
| **Hand Result** | hand_results.*, hand_players.hole_cards | - | players_master.photo_url |

---

## 4. 실시간 업데이트 흐름

### 4.1 Supabase Realtime 구독

```
┌─────────────────────────────────────────────────────────────────┐
│ Realtime 구독 (PostgreSQL LISTEN/NOTIFY)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Frontend (React)                                              │
│        │                                                        │
│        │ Supabase Realtime Subscribe                            │
│        ▼                                                        │
│   supabase                                                      │
│     .channel('feature-table-updates')                           │
│     .on('postgres_changes', {                                   │
│       event: 'UPDATE',                                          │
│       schema: 'json',                                           │
│       table: 'hand_players'                                     │
│     }, handleUpdate)                                            │
│     .subscribe()                                                │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ 이벤트 수신                                             │   │
│   │ {                                                       │   │
│   │   "type": "UPDATE",                                     │   │
│   │   "table": "hand_players",                              │   │
│   │   "new": { "end_stack": 1600000, ... },                 │   │
│   │   "old": { "end_stack": 1500000, ... }                  │   │
│   │ }                                                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                        │
│        ▼                                                        │
│   UI 업데이트 / 자동 렌더링 트리거                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 자동 렌더링 트리거

```sql
-- 특정 조건에서 자동 렌더링 트리거
CREATE OR REPLACE FUNCTION json.trigger_auto_render()
RETURNS TRIGGER AS $$
BEGIN
    -- 프리미엄 핸드 완료 시 자동 렌더링 요청
    IF NEW.is_premium = TRUE AND NEW.completed_at IS NOT NULL THEN
        INSERT INTO ae.render_jobs (
            composition_id,
            data_payload,
            priority,
            status
        )
        SELECT
            c.id,
            jsonb_build_object('hand_id', NEW.id),
            1,  -- 높은 우선순위
            'pending'
        FROM ae.compositions c
        WHERE c.comp_type = 'premium_hand_replay';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_render_premium_hand
    AFTER UPDATE OF completed_at ON json.hands
    FOR EACH ROW
    WHEN (NEW.is_premium = TRUE)
    EXECUTE FUNCTION json.trigger_auto_render();
```

---

## 5. 데이터 동기화 전략

### 5.1 동기화 주기

| 데이터 소스 | 주기 | 방법 |
|------------|------|------|
| **pokerGFX JSON** | ~1초 | WebSocket / Polling |
| **WSOP+ CSV** | 레벨 종료 | 수동 업로드 / FTP |
| **Admin UI** | 즉시 | REST API |
| **AEP 분석** | On-demand | 버튼 클릭 |

### 5.2 충돌 해결

```
동일 플레이어 칩 카운트 충돌 시:
1. json.hand_players.end_stack (Feature Table, 실시간)
2. wsop_plus.player_instances.chips (Other Tables, 배치)

우선순위: Feature Table에서는 json 우선, 그 외는 wsop_plus
```

---

## 다음 파트

→ [Part 5: Implementation Guide](05-implementation-guide.md)


---
