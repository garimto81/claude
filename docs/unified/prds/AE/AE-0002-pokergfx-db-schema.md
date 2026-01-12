# PRD-0002: PokerGFX DB Schema

## 문서 정보

| 항목 | 내용 |
|------|------|
| **PRD ID** | PRD-0002 |
| **제목** | PokerGFX RFID 데이터베이스 스키마 |
| **버전** | 1.0 |
| **작성일** | 2025-01-06 |
| **상태** | Draft |
| **우선순위** | P0 |
| **관련 PRD** | PRD-0001 (AE Automation System) |

---

## 1. 개요

### 1.1 배경

PokerGFX RFID 시스템에서 생성되는 포커 핸드 데이터를 효율적으로 저장하고 분석하기 위한 데이터베이스 스키마 설계.
기존 AE 렌더링 시스템(Template, Job, DataType)과 통합되어 마스터 데이터 참조 및 자동 렌더링을 지원.

### 1.2 목표

| 목표 | 설명 | 측정 지표 |
|------|------|----------|
| **데이터 정규화** | PokerGFX JSON 구조를 관계형 DB로 정규화 | 5개 전용 테이블 |
| **실시간 처리** | 핸드 데이터 < 100ms 저장 | p99 latency |
| **분석 지원** | 핸드 등급별, 플레이어별 통계 쿼리 | 복합 인덱스 적용 |
| **렌더링 연동** | 마스터 데이터(선수/팀) 참조 | FK 관계 |

### 1.3 범위

**포함:**
- PokerGFX 전용 5개 테이블 (poker_sessions, poker_hands, poker_players, poker_events, hand_results)
- Enum 타입 6개 (GameVariant, GameClass, BetStructure, AnteType, EventType, HandRank)
- 마스터 데이터 연동 (data_records FK)
- phevaluator 통합 (HandResult)

**제외:**
- PokerGFX JSON 파서 구현 (별도 서비스)
- 실시간 WebSocket 스트리밍
- 플레이어 마스터 데이터 마이그레이션

---

## 2. 요구사항

### 2.1 기능 요구사항

#### FR-001: 세션 관리
| ID | 요구사항 | 우선순위 |
|----|----------|:--------:|
| FR-001-01 | PokerGFX 세션 ID (BigInteger) 저장 | P0 |
| FR-001-02 | 세션별 메타데이터 (event_title, table_type) 저장 | P0 |
| FR-001-03 | 페이아웃 배열 JSON 저장 | P1 |
| FR-001-04 | 원본 생성 시간 (created_at_utc) 보존 | P0 |

#### FR-002: 핸드 관리
| ID | 요구사항 | 우선순위 |
|----|----------|:--------:|
| FR-002-01 | 핸드 번호 (session 내 unique) 저장 | P0 |
| FR-002-02 | 게임 설정 (GameVariant, GameClass, BetStructure) | P0 |
| FR-002-03 | 블라인드 정보 (FlopDrawBlinds) 통합 저장 | P0 |
| FR-002-04 | 커뮤니티 카드 캐싱 (JSON) | P1 |
| FR-002-05 | ISO 8601 Duration → seconds 변환 저장 | P1 |

#### FR-003: 플레이어 관리
| ID | 요구사항 | 우선순위 |
|----|----------|:--------:|
| FR-003-01 | 시트 번호, 이름 저장 | P0 |
| FR-003-02 | 스택 정보 (start/end/cumulative) | P0 |
| FR-003-03 | 홀 카드 JSON 저장 | P0 |
| FR-003-04 | 플레이어 통계 (VPIP, PFR, AF, WTSD) | P1 |
| FR-003-05 | 마스터 데이터 연결 (data_records FK) | P1 |

#### FR-004: 이벤트 로그
| ID | 요구사항 | 우선순위 |
|----|----------|:--------:|
| FR-004-01 | 이벤트 순서 (event_order) 보장 | P0 |
| FR-004-02 | 12가지 EventType Enum 지원 | P0 |
| FR-004-03 | 베팅 정보 (bet_amount, pot_amount) | P0 |
| FR-004-04 | 보드 카드 이벤트 (BOARD CARD) 처리 | P0 |

#### FR-005: 핸드 결과
| ID | 요구사항 | 우선순위 |
|----|----------|:--------:|
| FR-005-01 | phevaluator rank_value (1-7462) 저장 | P0 |
| FR-005-02 | HandRank 카테고리 (10단계) | P0 |
| FR-005-03 | 프리미엄 핸드 플래그 (등급 1-4) | P0 |
| FR-005-04 | 승패 정보 (is_winner, won_amount) | P0 |

### 2.2 비기능 요구사항

| ID | 카테고리 | 요구사항 | 기준 |
|----|----------|----------|------|
| NFR-001 | 성능 | 핸드 저장 latency | < 100ms p99 |
| NFR-002 | 성능 | 세션 전체 저장 | < 1s (100 hands) |
| NFR-003 | 확장성 | 일일 처리량 | 10,000+ hands |
| NFR-004 | 가용성 | 데이터 손실률 | 0% |
| NFR-005 | 쿼리 | 핸드 등급별 조회 | < 50ms |
| NFR-006 | 쿼리 | 플레이어별 통계 | < 100ms |

---

## 3. 아키텍처

### 3.1 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           System Architecture                                │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   PokerGFX      │
                    │   RFID System   │
                    └────────┬────────┘
                             │ JSON Export
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │  JSON Parser    │  │  Hand Evaluator │  │  DB Service     │             │
│  │  (watchdog)     │──│  (phevaluator)  │──│  (SQLAlchemy)   │             │
│  └─────────────────┘  └─────────────────┘  └────────┬────────┘             │
│                                                      │                      │
│  ┌─────────────────┐  ┌─────────────────┐           │                      │
│  │  Template       │  │  Job            │◄──────────┘                      │
│  │  Service        │◄─│  Service        │                                  │
│  └─────────────────┘  └─────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL Database                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    기존 테이블 (AE Rendering)                        │   │
│  │  templates, jobs, outputs, data_types, data_records,                │   │
│  │  template_data_mappings                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                  ▲                                          │
│                                  │ FK (master_record_id)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    신규 테이블 (PokerGFX)                            │   │
│  │  poker_sessions, poker_hands, poker_players, poker_events,          │   │
│  │  hand_results                                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 ERD (Entity Relationship Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PokerGFX ERD                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────┐
│  poker_sessions   │
├───────────────────┤
│ id (PK)           │
│ gfx_session_id    │◄─────────┐
│ event_title       │          │
│ table_type        │          │
│ software_version  │          │
│ payouts (JSON)    │          │
│ created_at_utc    │          │ 1:N
│ created_at        │          │
│ updated_at        │          │
└───────────────────┘          │
                               │
┌───────────────────┐          │
│   poker_hands     │──────────┘
├───────────────────┤
│ id (PK)           │◄─────────┬──────────┐
│ session_id (FK)   │          │          │
│ hand_num          │          │          │
│ game_variant      │          │          │
│ game_class        │          │          │
│ bet_structure     │          │          │
│ duration_seconds  │          │          │
│ started_at_utc    │          │          │
│ num_boards        │          │          │
│ run_it_num_times  │          │          │
│ button_seat       │          │ 1:N      │ 1:N
│ sb_seat / sb_amt  │          │          │
│ bb_seat / bb_amt  │          │          │
│ ante_type         │          │          │
│ blind_level       │          │          │
│ community_cards   │          │          │
│ created_at        │          │          │
└───────────────────┘          │          │
                               │          │
┌───────────────────┐          │          │
│  poker_players    │──────────┘          │
├───────────────────┤                     │
│ id (PK)           │◄──────────┐         │
│ hand_id (FK)      │           │         │
│ seat_num          │           │         │
│ name              │           │         │
│ long_name         │           │         │
│ start_stack       │           │         │
│ end_stack         │           │         │
│ cumulative_win    │           │         │
│ hole_cards (JSON) │           │         │
│ sitting_out       │           │ 1:1     │
│ elimination_rank  │           │         │
│ vpip_percent      │           │         │
│ pfr_percent       │           │         │
│ af_percent        │           │         │
│ wtsd_percent      │           │         │
│ master_record_id  │──────┐    │         │
│ created_at        │      │    │         │
└───────────────────┘      │    │         │
                           │    │         │
┌───────────────────┐      │    │         │
│   hand_results    │──────┼────┘         │
├───────────────────┤      │              │
│ id (PK)           │      │              │
│ player_id (FK)    │      │              │
│ rank_value        │      │              │
│ rank_category     │      │              │
│ rank_name         │      │              │
│ is_premium        │      │              │
│ is_winner         │      │              │
│ won_amount        │      │              │
│ created_at        │      │              │
└───────────────────┘      │              │
                           │              │
┌───────────────────┐      │              │
│   data_records    │◄─────┘              │
├───────────────────┤  (기존 테이블)       │
│ id (PK)           │                     │
│ type_id (FK)      │                     │
│ data (JSON)       │                     │
│ search_text       │                     │
│ ...               │                     │
└───────────────────┘                     │
                                          │
┌───────────────────┐                     │
│  poker_events     │─────────────────────┘
├───────────────────┤
│ id (PK)           │
│ hand_id (FK)      │
│ event_order       │
│ event_type        │
│ seat_num          │
│ bet_amount        │
│ pot_amount        │
│ board_cards (JSON)│
│ board_num         │
│ cards_drawn       │
│ event_at_utc      │
│ created_at        │
└───────────────────┘
```

### 3.3 데이터 흐름

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Data Flow Diagram                                 │
└─────────────────────────────────────────────────────────────────────────────┘

PokerGFX JSON                                                    Database
━━━━━━━━━━━━━                                                    ━━━━━━━━

┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Session    │      │   Parser    │      │  Validator  │      │  poker_     │
│  {          │─────▶│   extract   │─────▶│   check     │─────▶│  sessions   │
│    ID,      │      │   session   │      │   unique    │      │             │
│    Hands[]  │      │   metadata  │      │   gfx_id    │      │             │
│  }          │      │             │      │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
      │
      ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Hand       │      │   Parser    │      │  Merger     │      │  poker_     │
│  {          │─────▶│   extract   │─────▶│   combine   │─────▶│  hands      │
│    HandNum, │      │   hand +    │      │   hand +    │      │             │
│    Players, │      │   blinds    │      │   FlopDraw  │      │             │
│    Events   │      │             │      │   Blinds    │      │             │
│  }          │      │             │      │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
      │
      ├───────────────────────────────────────────────────────────────────┐
      │                                                                   │
      ▼                                                                   ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Player     │      │  Matcher    │      │  Linker     │      │  poker_     │
│  {          │─────▶│   find      │─────▶│   attach    │─────▶│  players    │
│    Name,    │      │   master    │      │   master_   │      │             │
│    HoleCards│      │   record    │      │   record_id │      │             │
│  }          │      │             │      │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
      │                                                               │
      │                                                               ▼
      │                                          ┌─────────────┐ ┌─────────────┐
      │                                          │  phevaluator│ │  hand_      │
      └─────────────────────────────────────────▶│   evaluate  │─│  results    │
                                                 │   7 cards   │ │             │
                                                 └─────────────┘ └─────────────┘

┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Event      │      │   Parser    │      │   Orderer   │      │  poker_     │
│  {          │─────▶│   extract   │─────▶│   assign    │─────▶│  events     │
│    EventType│      │   event     │      │   event_    │      │             │
│    BetAmt   │      │   data      │      │   order     │      │             │
│  }          │      │             │      │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
```

---

## 4. 테이블 상세 설계

### 4.1 poker_sessions

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INTEGER | PK, AUTO | 내부 ID |
| gfx_session_id | BIGINT | UNIQUE, NOT NULL, INDEX | PokerGFX 세션 ID |
| event_title | VARCHAR(255) | NULLABLE | 이벤트 제목 |
| table_type | VARCHAR(50) | NOT NULL, DEFAULT 'FEATURE_TABLE' | 테이블 타입 |
| software_version | VARCHAR(50) | NULLABLE | PokerGFX 버전 |
| payouts | JSON | NULLABLE | 페이아웃 배열 |
| created_at_utc | TIMESTAMP WITH TZ | NULLABLE | 원본 생성 시간 |
| created_at | TIMESTAMP WITH TZ | NOT NULL, DEFAULT NOW() | 저장 시간 |
| updated_at | TIMESTAMP WITH TZ | NOT NULL, DEFAULT NOW() | 수정 시간 |

**인덱스:**
- `ix_poker_sessions_gfx_id` (gfx_session_id) - UNIQUE

### 4.2 poker_hands

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INTEGER | PK, AUTO | 내부 ID |
| session_id | INTEGER | FK → poker_sessions.id, CASCADE, INDEX | 세션 참조 |
| hand_num | INTEGER | NOT NULL | 핸드 번호 |
| game_variant | ENUM | NOT NULL, DEFAULT 'HOLDEM' | 게임 종류 |
| game_class | ENUM | NOT NULL, DEFAULT 'FLOP' | 게임 클래스 |
| bet_structure | ENUM | NOT NULL, DEFAULT 'NOLIMIT' | 베팅 구조 |
| duration_seconds | FLOAT | NULLABLE | 핸드 진행 시간 (초) |
| started_at_utc | TIMESTAMP WITH TZ | NULLABLE, INDEX | 핸드 시작 시간 |
| num_boards | INTEGER | NOT NULL, DEFAULT 1 | 보드 수 |
| run_it_num_times | INTEGER | NOT NULL, DEFAULT 1 | Run It 횟수 |
| button_seat | INTEGER | NULLABLE | 버튼 위치 |
| sb_seat | INTEGER | NULLABLE | SB 위치 |
| sb_amount | INTEGER | NULLABLE | SB 금액 |
| bb_seat | INTEGER | NULLABLE | BB 위치 |
| bb_amount | INTEGER | NULLABLE | BB 금액 |
| ante_type | ENUM | NULLABLE | 앤티 타입 |
| blind_level | INTEGER | NULLABLE | 블라인드 레벨 |
| community_cards | JSON | NULLABLE | 커뮤니티 카드 캐시 |
| created_at | TIMESTAMP WITH TZ | NOT NULL, DEFAULT NOW() | 저장 시간 |

**인덱스:**
- `ix_poker_hands_session_hand` (session_id, hand_num) - UNIQUE
- `ix_poker_hands_started_at` (started_at_utc)

### 4.3 poker_players

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INTEGER | PK, AUTO | 내부 ID |
| hand_id | INTEGER | FK → poker_hands.id, CASCADE, INDEX | 핸드 참조 |
| seat_num | INTEGER | NOT NULL | 시트 번호 |
| name | VARCHAR(100) | NOT NULL, INDEX | 플레이어 이름 |
| long_name | VARCHAR(255) | NULLABLE | 전체 이름 |
| start_stack | INTEGER | NOT NULL, DEFAULT 0 | 시작 스택 |
| end_stack | INTEGER | NOT NULL, DEFAULT 0 | 종료 스택 |
| cumulative_winnings | INTEGER | NOT NULL, DEFAULT 0 | 누적 수익 |
| hole_cards | JSON | NULLABLE | 홀 카드 |
| sitting_out | BOOLEAN | NOT NULL, DEFAULT FALSE | 자리 비움 |
| elimination_rank | INTEGER | NOT NULL, DEFAULT -1 | 탈락 순위 |
| vpip_percent | FLOAT | NULLABLE | VPIP 통계 |
| pfr_percent | FLOAT | NULLABLE | PFR 통계 |
| af_percent | FLOAT | NULLABLE | AF 통계 |
| wtsd_percent | FLOAT | NULLABLE | WTSD 통계 |
| master_record_id | INTEGER | FK → data_records.id, SET NULL, NULLABLE | 마스터 데이터 |
| created_at | TIMESTAMP WITH TZ | NOT NULL, DEFAULT NOW() | 저장 시간 |

**인덱스:**
- `ix_poker_players_hand_seat` (hand_id, seat_num) - UNIQUE
- `ix_poker_players_name` (name)

### 4.4 poker_events

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INTEGER | PK, AUTO | 내부 ID |
| hand_id | INTEGER | FK → poker_hands.id, CASCADE, INDEX | 핸드 참조 |
| event_order | INTEGER | NOT NULL | 이벤트 순서 |
| event_type | ENUM | NOT NULL | 이벤트 타입 |
| seat_num | INTEGER | NULLABLE | 플레이어 시트 |
| bet_amount | INTEGER | NULLABLE | 베팅 금액 |
| pot_amount | INTEGER | NULLABLE | 현재 팟 |
| board_cards | JSON | NULLABLE | 보드 카드 |
| board_num | INTEGER | NULLABLE | 보드 번호 |
| cards_drawn | INTEGER | NULLABLE | 드로우 카드 수 |
| event_at_utc | TIMESTAMP WITH TZ | NULLABLE | 이벤트 시간 |
| created_at | TIMESTAMP WITH TZ | NOT NULL, DEFAULT NOW() | 저장 시간 |

**인덱스:**
- `ix_poker_events_hand_order` (hand_id, event_order) - UNIQUE
- `ix_poker_events_type` (event_type)

### 4.5 hand_results

| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | INTEGER | PK, AUTO | 내부 ID |
| player_id | INTEGER | FK → poker_players.id, CASCADE, UNIQUE, INDEX | 플레이어 참조 |
| rank_value | INTEGER | NOT NULL | phevaluator 값 (1-7462) |
| rank_category | ENUM | NOT NULL | 핸드 등급 |
| rank_name | VARCHAR(50) | NOT NULL | 등급 이름 |
| is_premium | BOOLEAN | NOT NULL, DEFAULT FALSE | 프리미엄 핸드 |
| is_winner | BOOLEAN | NOT NULL, DEFAULT FALSE | 승자 여부 |
| won_amount | INTEGER | NULLABLE | 획득 금액 |
| created_at | TIMESTAMP WITH TZ | NOT NULL, DEFAULT NOW() | 저장 시간 |

**인덱스:**
- `ix_hand_results_rank_category` (rank_category)
- `ix_hand_results_premium` (is_premium)
- `ix_hand_results_winner` (is_winner)

---

## 5. Enum 타입 정의

### 5.1 GameVariant

```python
class GameVariant(str, Enum):
    HOLDEM = "HOLDEM"
    OMAHA = "OMAHA"
    OMAHA_HILO = "OMAHA_HILO"
    STUD = "STUD"
    RAZZ = "RAZZ"
    DRAW = "DRAW"
```

### 5.2 GameClass

```python
class GameClass(str, Enum):
    FLOP = "FLOP"      # Hold'em, Omaha
    DRAW = "DRAW"      # Draw games
    STUD = "STUD"      # Stud games
```

### 5.3 BetStructure

```python
class BetStructure(str, Enum):
    NOLIMIT = "NOLIMIT"
    POTLIMIT = "POTLIMIT"
    LIMIT = "LIMIT"
```

### 5.4 AnteType

```python
class AnteType(str, Enum):
    NONE = "NONE"
    BB_ANTE_BB1ST = "BB_ANTE_BB1ST"
    BB_ANTE = "BB_ANTE"
    TRADITIONAL = "TRADITIONAL"
```

### 5.5 EventType

```python
class EventType(str, Enum):
    # 베팅 액션
    FOLD = "FOLD"
    CHECK = "CHECK"
    CALL = "CALL"
    BET = "BET"
    RAISE = "RAISE"
    ALL_IN = "ALL_IN"

    # 보드 이벤트
    BOARD_CARD = "BOARD CARD"

    # 특수 이벤트
    SHOWDOWN = "SHOWDOWN"
    ANTE = "ANTE"
    BLIND = "BLIND"
    UNCALLED = "UNCALLED"
    WIN = "WIN"
    MUCK = "MUCK"
```

### 5.6 HandRank

```python
class HandRank(IntEnum):
    ROYAL_FLUSH = 1
    STRAIGHT_FLUSH = 2
    FOUR_OF_A_KIND = 3
    FULL_HOUSE = 4
    FLUSH = 5
    STRAIGHT = 6
    THREE_OF_A_KIND = 7
    TWO_PAIR = 8
    ONE_PAIR = 9
    HIGH_CARD = 10
```

**phevaluator 값 범위:**

| 등급 | 핸드 | 값 범위 |
|:----:|------|---------|
| 1 | Royal Flush | 1 |
| 2 | Straight Flush | 2-10 |
| 3 | Four of a Kind | 11-166 |
| 4 | Full House | 167-322 |
| 5 | Flush | 323-1599 |
| 6 | Straight | 1600-1609 |
| 7 | Three of a Kind | 1610-2467 |
| 8 | Two Pair | 2468-3325 |
| 9 | One Pair | 3326-6185 |
| 10 | High Card | 6186-7462 |

---

## 6. 쿼리 최적화

### 6.1 주요 쿼리 패턴

#### Q1: 세션별 핸드 목록

```sql
SELECT h.*,
       (SELECT COUNT(*) FROM poker_players WHERE hand_id = h.id) as player_count
FROM poker_hands h
WHERE h.session_id = :session_id
ORDER BY h.hand_num;
```

**인덱스 활용:** `ix_poker_hands_session_hand`

#### Q2: 프리미엄 핸드 조회

```sql
SELECT p.name, p.hole_cards, hr.rank_name, h.hand_num
FROM hand_results hr
JOIN poker_players p ON hr.player_id = p.id
JOIN poker_hands h ON p.hand_id = h.id
WHERE hr.is_premium = TRUE
ORDER BY hr.rank_category, h.started_at_utc DESC;
```

**인덱스 활용:** `ix_hand_results_premium`

#### Q3: 플레이어별 통계

```sql
SELECT p.name,
       COUNT(*) as hands_played,
       SUM(CASE WHEN hr.is_winner THEN 1 ELSE 0 END) as wins,
       AVG(hr.rank_category) as avg_rank
FROM poker_players p
LEFT JOIN hand_results hr ON p.id = hr.player_id
GROUP BY p.name
ORDER BY wins DESC;
```

**인덱스 활용:** `ix_poker_players_name`

#### Q4: 시간대별 핸드 조회

```sql
SELECT h.*, s.event_title
FROM poker_hands h
JOIN poker_sessions s ON h.session_id = s.id
WHERE h.started_at_utc BETWEEN :start AND :end
ORDER BY h.started_at_utc;
```

**인덱스 활용:** `ix_poker_hands_started_at`

### 6.2 인덱스 전략

| 인덱스 | 용도 | 예상 효과 |
|--------|------|----------|
| gfx_session_id UNIQUE | 중복 세션 방지 | 100% hit |
| session_id + hand_num | 세션 내 핸드 조회 | Covering index |
| hand_id + seat_num | 핸드 내 플레이어 조회 | Covering index |
| hand_id + event_order | 이벤트 시퀀스 조회 | Covering index |
| rank_category | 핸드 등급 필터 | Selective filter |
| is_premium | 프리미엄 핸드 필터 | Boolean filter |

---

## 7. API 설계

### 7.1 엔드포인트 목록

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/poker/sessions` | 세션 생성 |
| GET | `/api/v1/poker/sessions` | 세션 목록 |
| GET | `/api/v1/poker/sessions/{id}` | 세션 상세 |
| GET | `/api/v1/poker/sessions/{id}/hands` | 세션 핸드 목록 |
| POST | `/api/v1/poker/hands` | 핸드 생성 (배치) |
| GET | `/api/v1/poker/hands/{id}` | 핸드 상세 (플레이어/이벤트 포함) |
| GET | `/api/v1/poker/hands/{id}/timeline` | 핸드 타임라인 |
| GET | `/api/v1/poker/results/premium` | 프리미엄 핸드 목록 |
| GET | `/api/v1/poker/stats/players` | 플레이어 통계 |

### 7.2 요청/응답 스키마

#### POST /api/v1/poker/sessions

**Request:**
```json
{
  "gfx_session_id": 638961999170907267,
  "event_title": "WSOP Main Event",
  "table_type": "FEATURE_TABLE",
  "software_version": "PokerGFX 3.2",
  "created_at_utc": "2025-10-16T08:25:17.090Z",
  "payouts": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
}
```

**Response:**
```json
{
  "id": 1,
  "gfx_session_id": 638961999170907267,
  "event_title": "WSOP Main Event",
  "table_type": "FEATURE_TABLE",
  "hands_count": 0,
  "created_at": "2025-01-06T12:00:00Z"
}
```

#### GET /api/v1/poker/hands/{id}

**Response:**
```json
{
  "id": 42,
  "session_id": 1,
  "hand_num": 5,
  "game_variant": "HOLDEM",
  "bet_structure": "NOLIMIT",
  "blinds": {
    "button_seat": 2,
    "sb_seat": 3,
    "sb_amount": 5000,
    "bb_seat": 4,
    "bb_amount": 10000
  },
  "community_cards": ["7s", "jd", "as", "kc", "2h"],
  "players": [
    {
      "id": 101,
      "seat_num": 1,
      "name": "Player A",
      "hole_cards": ["Ah", "Kd"],
      "start_stack": 100000,
      "end_stack": 120000,
      "result": {
        "rank_name": "Two Pair",
        "is_winner": true,
        "won_amount": 20000
      }
    }
  ],
  "events": [
    {"order": 0, "type": "BLIND", "seat": 3, "amount": 5000},
    {"order": 1, "type": "BLIND", "seat": 4, "amount": 10000},
    {"order": 2, "type": "CALL", "seat": 1, "amount": 10000, "pot": 25000}
  ]
}
```

---

## 8. 마이그레이션 계획

### 8.1 Alembic 마이그레이션

```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "add pokergfx tables"

# 마이그레이션 적용
alembic upgrade head

# 롤백 (필요시)
alembic downgrade -1
```

### 8.2 마이그레이션 순서

```
1. poker_sessions 생성
        ↓
2. poker_hands 생성 (FK → poker_sessions)
        ↓
3. poker_players 생성 (FK → poker_hands, data_records)
        ↓
4. poker_events 생성 (FK → poker_hands)
        ↓
5. hand_results 생성 (FK → poker_players)
```

### 8.3 데이터 마이그레이션

기존 데이터가 없으므로 초기 마이그레이션만 필요.

---

## 9. 테스트 계획

### 9.1 단위 테스트

| 테스트 | 설명 | 우선순위 |
|--------|------|:--------:|
| 모델 생성 | 각 모델 CRUD 테스트 | P0 |
| 관계 검증 | FK 관계, CASCADE 삭제 | P0 |
| Enum 검증 | 모든 Enum 값 저장/조회 | P0 |
| 인덱스 검증 | UNIQUE 제약조건 | P0 |
| HandResult.from_evaluation | 팩토리 메서드 | P0 |

### 9.2 통합 테스트

| 테스트 | 설명 | 우선순위 |
|--------|------|:--------:|
| 전체 세션 저장 | Session → Hand → Player/Event | P0 |
| 마스터 데이터 연동 | PokerPlayer ↔ DataRecord | P1 |
| 쿼리 성능 | 주요 쿼리 latency 측정 | P1 |

### 9.3 성능 테스트

| 시나리오 | 목표 |
|----------|------|
| 100 hands 저장 | < 1s |
| 1000 hands 조회 | < 500ms |
| 프리미엄 핸드 필터 | < 50ms |

---

## 10. 보안 고려사항

### 10.1 데이터 보호

| 항목 | 조치 |
|------|------|
| 플레이어 이름 | 마스킹 옵션 제공 |
| 홀 카드 | 접근 권한 제어 |
| 스택 정보 | 읽기 전용 API |

### 10.2 접근 제어

- API 인증 필수 (JWT)
- 세션별 접근 권한 (owner/viewer)
- 핸드 결과 지연 공개 옵션

---

## 11. 구현 파일

### 11.1 생성된 모델 파일

| 파일 | 위치 |
|------|------|
| `poker_session.py` | `backend/app/models/` |
| `poker_hand.py` | `backend/app/models/` |
| `poker_player.py` | `backend/app/models/` |
| `poker_event.py` | `backend/app/models/` |
| `hand_result.py` | `backend/app/models/` |

### 11.2 모델 관계도

```
PokerSession
    └── PokerHand (1:N)
            ├── PokerPlayer (1:N)
            │       ├── HandResult (1:1)
            │       └── DataRecord (N:1, optional)
            └── PokerEvent (1:N)
```

---

## 부록

### A. PokerGFX JSON 원본 구조

PRD-0002-primary-gfx-rfid.md 참조

### B. phevaluator 라이브러리

- GitHub: https://github.com/HenryRLee/PokerHandEvaluator
- PyPI: `phevaluator>=0.5.0`
- 성능: 7장 평가 ~0.1μs

### C. 관련 문서

- PRD-0001: After Effects Automation System
- PRD-0002 (feature_table): Primary Layer - GFX RFID

