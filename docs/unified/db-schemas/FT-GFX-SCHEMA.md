# GFX JSON Database Schema

PokerGFX JSON 데이터 저장을 위한 PostgreSQL/Supabase 데이터베이스 스키마 설계 문서

**Version**: 1.0.0
**Date**: 2025-01-13
**Project**: Feature Table Automation (FT-0001)

---

## 1. 개요

### 1.1 목적

PokerGFX에서 생성되는 JSON 파일을 정규화된 관계형 데이터베이스에 저장하여:
- 핸드별 검색 및 분석
- 플레이어 통계 집계
- 핸드 등급(A/B/C) 분류 및 방송 적격성 판단
- 녹화 오프셋 기반 비디오 편집 지점 추출

### 1.2 JSON 분석 요약

```
gfx_json/
├── table-GG/           # 테이블 GG
│   └── 1015~1021/      # 날짜별 폴더 (MMDD)
└── table-pokercaster/  # 테이블 pokercaster
    └── 1015~1021/
```

**파일 네이밍**: `PGFX_live_data_export GameID={int64}.json`

### 1.3 JSON 스키마 (중첩 구조)

```
Root (Session)
├── ID (int64)                  # PokerGFX GameID
├── CreatedDateTimeUTC          # ISO 8601
├── EventTitle                  # 이벤트 제목 (선택)
├── SoftwareVersion             # "PokerGFX 3.2"
├── Type                        # "FEATURE_TABLE"
├── Payouts[10]                 # 페이아웃 배열
└── Hands[]                     # 핸드 배열
    ├── HandNum                 # 핸드 번호
    ├── Duration                # ISO 8601 Duration
    ├── StartDateTimeUTC        # 핸드 시작 시간
    ├── RecordingOffsetStart    # 녹화 오프셋
    ├── GameVariant             # "HOLDEM"
    ├── GameClass               # "FLOP"
    ├── BetStructure            # "NOLIMIT"
    ├── AnteAmt, BombPotAmt     # 앤티/폭탄팟 금액
    ├── NumBoards, RunItNumTimes
    ├── FlopDrawBlinds          # 블라인드 정보 객체
    ├── StudLimits              # Stud 리밋 객체
    ├── Events[]                # 액션 배열
    │   ├── EventType           # FOLD/BET/CALL/CHECK/RAISE/ALL_IN/BOARD_CARD
    │   ├── PlayerNum           # 플레이어 번호 (1-10, 0=보드)
    │   ├── BetAmt              # 베팅 금액
    │   ├── Pot                 # 팟 크기
    │   └── BoardCards          # 보드 카드 (null 또는 "5d")
    └── Players[]               # 플레이어 배열
        ├── PlayerNum           # 시트 번호 (1-10)
        ├── Name, LongName      # 플레이어 이름
        ├── HoleCards[]         # 홀 카드 ([""] 또는 ["10d 9d"])
        ├── StartStackAmt       # 시작 스택
        ├── EndStackAmt         # 종료 스택
        ├── CumulativeWinningsAmt
        └── 통계 (VPIP%, PFR%, Aggression%, ShowdownPct)
```

---

## 2. ERD (Entity Relationship Diagram)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PokerGFX Database Schema                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐       ┌──────────────────────┐
│   gfx_players        │       │    gfx_sessions      │
│   (플레이어 마스터)    │       │    (세션/게임 단위)    │
├──────────────────────┤       ├──────────────────────┤
│ PK id: uuid          │       │ PK id: uuid          │
│    player_hash: text │◄──┐   │ UK session_id: int8  │───┐
│    name: text        │   │   │ UK file_hash: text   │   │
│    long_name: text   │   │   │    file_name: text   │   │
│    total_hands: int  │   │   │    table_type: enum  │   │
│    first_seen_at: ts │   │   │    event_title: text │   │
│    last_seen_at: ts  │   │   │    software_version  │   │
│    created_at: ts    │   │   │    payouts: int[]    │   │
│    updated_at: ts    │   │   │    hand_count: int   │   │
└──────────────────────┘   │   │    session_start: ts │   │
                           │   │    nas_path: text    │   │
                           │   │    sync_status: enum │   │
                           │   │    raw_json: jsonb   │   │
                           │   │    created_at: ts    │   │
                           │   └──────────────────────┘   │
                           │              │               │
                           │              │ 1:N           │
                           │              ▼               │
                           │   ┌──────────────────────┐   │
                           │   │     gfx_hands        │   │
                           │   │    (핸드 단위)        │   │
                           │   ├──────────────────────┤   │
                           │   │ PK id: uuid          │   │
                           │   │ FK session_id: int8  │◄──┘
                           │   │    hand_num: int     │
                           │   │    game_variant: enum│
                           │   │    game_class: enum  │
                           │   │    bet_structure:enum│
                           │   │    duration_seconds  │
                           │   │    start_time: ts    │
                           │   │    recording_offset  │
                           │   │    ante_amt: int     │
                           │   │    bomb_pot_amt: int │
                           │   │    blinds: jsonb     │
                           │   │    pot_size: int     │
                           │   │    board_cards: text[]│
                           │   │    winner_name: text │
                           │   │    created_at: ts    │
                           │   └──────────────────────┘
                           │              │
                           │              │ 1:N
        ┌──────────────────┴──────────────┼──────────────────┐
        │                                 │                  │
        ▼                                 ▼                  ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  gfx_hand_players    │  │    gfx_events        │  │    hand_grades       │
│  (핸드별 플레이어)     │  │   (액션/이벤트)       │  │   (핸드 등급)         │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│ PK id: uuid          │  │ PK id: uuid          │  │ PK id: uuid          │
│ FK hand_id: uuid     │  │ FK hand_id: uuid     │  │ FK hand_id: uuid     │
│ FK player_id: uuid   │  │    event_order: int  │  │    grade: char(1)    │
│    seat_num: int     │  │    event_type: enum  │  │    has_premium_hand  │
│    player_name: text │  │    player_num: int   │  │    has_long_playtime │
│    hole_cards: text[]│  │    bet_amt: int      │  │    has_premium_board │
│    start_stack: int  │  │    pot: int          │  │    conditions_met    │
│    end_stack: int    │  │    board_cards: text │  │    broadcast_eligible│
│    cumulative_win    │  │    board_num: int    │  │    graded_by: text   │
│    sitting_out: bool │  │    created_at: ts    │  │    graded_at: ts     │
│    is_winner: bool   │  └──────────────────────┘  └──────────────────────┘
│    vpip_percent      │
│    created_at: ts    │
└──────────────────────┘
```

### 테이블 관계 요약

| 관계 | 설명 |
|------|------|
| `gfx_sessions` 1:N `gfx_hands` | 세션당 여러 핸드 |
| `gfx_hands` 1:N `gfx_events` | 핸드당 여러 액션 |
| `gfx_hands` 1:N `gfx_hand_players` | 핸드당 최대 10명 |
| `gfx_hands` 1:1 `hand_grades` | 핸드당 1개 등급 |
| `gfx_players` 1:N `gfx_hand_players` | 플레이어당 여러 핸드 참여 |

---

## 3. Enum 타입 정의

```sql
-- ============================================================================
-- ENUM Types
-- ============================================================================

-- 테이블 타입 (게임 종류)
CREATE TYPE table_type AS ENUM (
    'FEATURE_TABLE',    -- 피처 테이블 (방송용)
    'MAIN_TABLE',       -- 메인 테이블
    'FINAL_TABLE',      -- 파이널 테이블
    'SIDE_TABLE',       -- 사이드 테이블
    'UNKNOWN'           -- 미분류
);

-- 게임 변형
CREATE TYPE game_variant AS ENUM (
    'HOLDEM',           -- Texas Hold'em
    'OMAHA',            -- Omaha
    'OMAHA_HILO',       -- Omaha Hi-Lo
    'STUD',             -- 7-Card Stud
    'STUD_HILO',        -- Stud Hi-Lo
    'RAZZ',             -- Razz
    'DRAW',             -- 5-Card Draw
    'MIXED'             -- Mixed games
);

-- 게임 클래스
CREATE TYPE game_class AS ENUM (
    'FLOP',             -- Hold'em, Omaha (커뮤니티 카드)
    'STUD',             -- 7-Card Stud
    'DRAW',             -- 5-Card Draw
    'MIXED'             -- Mixed games
);

-- 베팅 구조
CREATE TYPE bet_structure AS ENUM (
    'NOLIMIT',          -- No Limit
    'POTLIMIT',         -- Pot Limit
    'LIMIT',            -- Fixed Limit
    'SPREAD_LIMIT'      -- Spread Limit
);

-- 이벤트 타입 (액션)
CREATE TYPE event_type AS ENUM (
    'FOLD',             -- 폴드
    'CHECK',            -- 체크
    'CALL',             -- 콜
    'BET',              -- 베팅
    'RAISE',            -- 레이즈
    'ALL_IN',           -- 올인
    'BOARD_CARD',       -- 보드 카드 공개
    'ANTE',             -- 앤티
    'BLIND',            -- 블라인드
    'STRADDLE',         -- 스트래들
    'BRING_IN',         -- 브링인 (Stud)
    'MUCK',             -- 카드 버림
    'SHOW',             -- 카드 공개
    'WIN'               -- 팟 획득
);

-- 동기화 상태
CREATE TYPE sync_status AS ENUM (
    'pending',          -- 처리 대기
    'synced',           -- 동기화 완료
    'updated',          -- 업데이트됨
    'failed',           -- 실패
    'archived'          -- 아카이브됨
);

-- 앤티 타입
CREATE TYPE ante_type AS ENUM (
    'NO_ANTE',          -- 앤티 없음
    'BB_ANTE_BB1ST',    -- BB 앤티 (BB 먼저)
    'BB_ANTE_BTN1ST',   -- BB 앤티 (버튼 먼저)
    'ALL_ANTE',         -- 전원 앤티
    'DEAD_ANTE'         -- 데드 앤티
);
```

---

## 4. 테이블 DDL

### 4.1 gfx_players (플레이어 마스터)

```sql
-- ============================================================================
-- gfx_players: 플레이어 마스터 테이블 (중복 제거)
-- 동일 플레이어를 여러 세션/핸드에서 참조
-- ============================================================================

CREATE TABLE gfx_players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 플레이어 식별 (name + long_name 해시로 중복 방지)
    player_hash TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    long_name TEXT DEFAULT '',

    -- 누적 통계 (추후 집계용)
    total_hands_played INTEGER DEFAULT 0,
    total_sessions INTEGER DEFAULT 0,

    -- 타임스탬프
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_gfx_players_name ON gfx_players(name);
CREATE INDEX idx_gfx_players_hash ON gfx_players(player_hash);
```

### 4.2 gfx_sessions (세션/게임 단위)

```sql
-- ============================================================================
-- gfx_sessions: PokerGFX 게임 세션 저장
-- 원본 JSON 전체를 raw_json에 보관 (감사 추적)
-- ============================================================================

CREATE TABLE gfx_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- PokerGFX 세션 식별자 (Windows FileTime 기반 int64)
    session_id BIGINT NOT NULL UNIQUE,

    -- 파일 정보
    file_name TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,  -- SHA256 (중복 방지)
    nas_path TEXT,                    -- 원본 NAS 경로

    -- 세션 메타데이터
    table_type table_type NOT NULL DEFAULT 'UNKNOWN',
    event_title TEXT DEFAULT '',
    software_version TEXT DEFAULT '',
    payouts INTEGER[] DEFAULT ARRAY[]::INTEGER[],

    -- 집계 필드
    hand_count INTEGER DEFAULT 0,
    player_count INTEGER DEFAULT 0,
    total_duration_seconds INTEGER DEFAULT 0,

    -- 시간 정보
    session_created_at TIMESTAMPTZ,   -- CreatedDateTimeUTC from JSON
    session_start_time TIMESTAMPTZ,   -- 첫 핸드 시작 시간
    session_end_time TIMESTAMPTZ,     -- 마지막 핸드 종료 시간

    -- 원본 JSON 저장
    raw_json JSONB NOT NULL,

    -- 동기화 상태
    sync_status sync_status DEFAULT 'pending',
    sync_error TEXT,

    -- 타임스탬프
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_gfx_sessions_session_id ON gfx_sessions(session_id);
CREATE INDEX idx_gfx_sessions_file_hash ON gfx_sessions(file_hash);
CREATE INDEX idx_gfx_sessions_table_type ON gfx_sessions(table_type);
CREATE INDEX idx_gfx_sessions_created_at ON gfx_sessions(session_created_at DESC);
CREATE INDEX idx_gfx_sessions_sync_status ON gfx_sessions(sync_status);
CREATE INDEX idx_gfx_sessions_processed_at ON gfx_sessions(processed_at DESC);

-- JSONB 인덱스 (선택적)
CREATE INDEX idx_gfx_sessions_raw_json_type
    ON gfx_sessions USING GIN ((raw_json -> 'Type'));
```

### 4.3 gfx_hands (핸드 단위)

```sql
-- ============================================================================
-- gfx_hands: 개별 핸드 데이터
-- 세션의 Hands[] 배열을 정규화하여 저장
-- ============================================================================

CREATE TABLE gfx_hands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 세션 참조 (session_id는 BIGINT)
    session_id BIGINT NOT NULL,

    -- 핸드 식별
    hand_num INTEGER NOT NULL,

    -- 게임 정보
    game_variant game_variant DEFAULT 'HOLDEM',
    game_class game_class DEFAULT 'FLOP',
    bet_structure bet_structure DEFAULT 'NOLIMIT',

    -- 시간 정보
    duration_seconds INTEGER DEFAULT 0,
    start_time TIMESTAMPTZ NOT NULL,
    recording_offset_iso TEXT,        -- ISO 8601 Duration (원본 보존)
    recording_offset_seconds BIGINT,  -- 변환된 초 단위

    -- 게임 설정
    num_boards INTEGER DEFAULT 1,
    run_it_num_times INTEGER DEFAULT 1,
    ante_amt INTEGER DEFAULT 0,
    bomb_pot_amt INTEGER DEFAULT 0,
    description TEXT DEFAULT '',

    -- 블라인드 정보 (JSONB로 유연하게 저장)
    blinds JSONB DEFAULT '{}'::JSONB,
    /*
    {
        "ante_type": "BB_ANTE_BB1ST",
        "big_blind_amt": 180000,
        "big_blind_player_num": 3,
        "small_blind_amt": 5000,
        "small_blind_player_num": 2,
        "button_player_num": 1,
        "third_blind_amt": 0,
        "blind_level": 0
    }
    */

    -- Stud 전용 리밋 (JSONB)
    stud_limits JSONB DEFAULT '{}'::JSONB,

    -- 집계 필드
    pot_size INTEGER DEFAULT 0,
    player_count INTEGER DEFAULT 0,
    showdown_count INTEGER DEFAULT 0,

    -- 보드 카드 (배열)
    board_cards TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- 승자 정보
    winner_name TEXT,
    winner_seat INTEGER,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 복합 유니크 제약
    CONSTRAINT uq_session_hand UNIQUE (session_id, hand_num)
);

-- 인덱스
CREATE INDEX idx_gfx_hands_session_id ON gfx_hands(session_id);
CREATE INDEX idx_gfx_hands_hand_num ON gfx_hands(hand_num);
CREATE INDEX idx_gfx_hands_start_time ON gfx_hands(start_time DESC);
CREATE INDEX idx_gfx_hands_pot_size ON gfx_hands(pot_size DESC);
CREATE INDEX idx_gfx_hands_game_variant ON gfx_hands(game_variant);
CREATE INDEX idx_gfx_hands_duration ON gfx_hands(duration_seconds DESC);

-- 보드 카드 검색용 GIN 인덱스
CREATE INDEX idx_gfx_hands_board_cards ON gfx_hands USING GIN (board_cards);
```

### 4.4 gfx_hand_players (핸드별 플레이어 상태)

```sql
-- ============================================================================
-- gfx_hand_players: 핸드별 플레이어 상태
-- 각 핸드에서의 플레이어 스택, 카드, 통계 저장
-- ============================================================================

CREATE TABLE gfx_hand_players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 참조
    hand_id UUID NOT NULL REFERENCES gfx_hands(id) ON DELETE CASCADE,
    player_id UUID REFERENCES gfx_players(id) ON DELETE SET NULL,

    -- 시트 정보
    seat_num INTEGER NOT NULL CHECK (seat_num BETWEEN 1 AND 10),
    player_name TEXT NOT NULL,  -- 비정규화 (조회 성능)

    -- 홀 카드 (쇼다운 시만 존재)
    hole_cards TEXT[] DEFAULT ARRAY[]::TEXT[],
    has_shown BOOLEAN DEFAULT FALSE,

    -- 스택 정보
    start_stack_amt INTEGER DEFAULT 0,
    end_stack_amt INTEGER DEFAULT 0,
    cumulative_winnings_amt INTEGER DEFAULT 0,
    blind_bet_straddle_amt INTEGER DEFAULT 0,

    -- 상태
    sitting_out BOOLEAN DEFAULT FALSE,
    elimination_rank INTEGER DEFAULT -1,  -- -1 = not eliminated
    is_winner BOOLEAN DEFAULT FALSE,

    -- 통계 (핸드 종료 시점 기준)
    vpip_percent NUMERIC(5,2) DEFAULT 0,
    preflop_raise_percent NUMERIC(5,2) DEFAULT 0,
    aggression_frequency_percent NUMERIC(5,2) DEFAULT 0,
    went_to_showdown_percent NUMERIC(5,2) DEFAULT 0,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 복합 유니크 제약
    CONSTRAINT uq_hand_seat UNIQUE (hand_id, seat_num)
);

-- 인덱스
CREATE INDEX idx_gfx_hand_players_hand_id ON gfx_hand_players(hand_id);
CREATE INDEX idx_gfx_hand_players_player_id ON gfx_hand_players(player_id);
CREATE INDEX idx_gfx_hand_players_seat ON gfx_hand_players(seat_num);
CREATE INDEX idx_gfx_hand_players_winner ON gfx_hand_players(is_winner) WHERE is_winner = TRUE;
CREATE INDEX idx_gfx_hand_players_shown ON gfx_hand_players(has_shown) WHERE has_shown = TRUE;

-- 홀 카드 검색용 GIN 인덱스
CREATE INDEX idx_gfx_hand_players_cards ON gfx_hand_players USING GIN (hole_cards);
```

### 4.5 gfx_events (액션/이벤트)

```sql
-- ============================================================================
-- gfx_events: 핸드 내 액션/이벤트 시퀀스
-- FOLD, BET, CALL, RAISE, ALL_IN, BOARD_CARD 등
-- ============================================================================

CREATE TABLE gfx_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 핸드 참조
    hand_id UUID NOT NULL REFERENCES gfx_hands(id) ON DELETE CASCADE,

    -- 이벤트 순서 (핸드 내)
    event_order INTEGER NOT NULL,

    -- 이벤트 정보
    event_type event_type NOT NULL,
    player_num INTEGER DEFAULT 0,  -- 0 = 보드 카드

    -- 베팅 정보
    bet_amt INTEGER DEFAULT 0,
    pot INTEGER DEFAULT 0,

    -- 보드 카드 (BOARD_CARD 이벤트 시)
    board_cards TEXT,  -- 단일 카드 문자열 (예: "6d")
    board_num INTEGER DEFAULT 0,

    -- Draw 게임용
    num_cards_drawn INTEGER DEFAULT 0,

    -- 시간 (있을 경우)
    event_time TIMESTAMPTZ,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 복합 유니크 제약
    CONSTRAINT uq_hand_event_order UNIQUE (hand_id, event_order)
);

-- 인덱스
CREATE INDEX idx_gfx_events_hand_id ON gfx_events(hand_id);
CREATE INDEX idx_gfx_events_type ON gfx_events(event_type);
CREATE INDEX idx_gfx_events_player ON gfx_events(player_num) WHERE player_num > 0;
CREATE INDEX idx_gfx_events_board ON gfx_events(event_type) WHERE event_type = 'BOARD_CARD';
CREATE INDEX idx_gfx_events_order ON gfx_events(hand_id, event_order);
```

### 4.6 hand_grades (핸드 등급)

```sql
-- ============================================================================
-- hand_grades: 핸드 등급 분류 결과
-- grading/grader.py와 연동
-- ============================================================================

CREATE TABLE hand_grades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 핸드 참조
    hand_id UUID NOT NULL REFERENCES gfx_hands(id) ON DELETE CASCADE,

    -- 등급 (A/B/C)
    grade CHAR(1) NOT NULL CHECK (grade IN ('A', 'B', 'C')),

    -- 등급 조건
    has_premium_hand BOOLEAN DEFAULT FALSE,     -- HandRank <= 4
    has_long_playtime BOOLEAN DEFAULT FALSE,    -- duration >= threshold
    has_premium_board_combo BOOLEAN DEFAULT FALSE,  -- board rank <= 7
    conditions_met INTEGER NOT NULL CHECK (conditions_met BETWEEN 0 AND 3),

    -- 방송 적격성
    broadcast_eligible BOOLEAN DEFAULT FALSE,

    -- 편집 포인트 제안
    suggested_edit_start_offset INTEGER,  -- 초 단위
    edit_start_confidence NUMERIC(3,2),

    -- 등급 부여 정보
    graded_by TEXT,  -- 'auto', 'manual', 'ai'
    graded_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 유니크 제약
    CONSTRAINT uq_hand_grade UNIQUE (hand_id)
);

-- 인덱스
CREATE INDEX idx_hand_grades_grade ON hand_grades(grade);
CREATE INDEX idx_hand_grades_eligible ON hand_grades(broadcast_eligible)
    WHERE broadcast_eligible = TRUE;
CREATE INDEX idx_hand_grades_hand_id ON hand_grades(hand_id);
```

### 4.7 sync_log (동기화 로그)

```sql
-- ============================================================================
-- sync_log: NAS 파일 동기화 추적
-- ============================================================================

CREATE TABLE sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 파일 정보
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    file_size_bytes BIGINT,

    -- 작업 정보
    operation TEXT NOT NULL,  -- created, modified, deleted
    status TEXT DEFAULT 'processing',  -- processing, success, failed, skipped

    -- 결과
    session_id UUID REFERENCES gfx_sessions(id),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 인덱스
CREATE INDEX idx_sync_log_hash ON sync_log(file_hash);
CREATE INDEX idx_sync_log_status ON sync_log(status);
CREATE INDEX idx_sync_log_created ON sync_log(created_at DESC);
```

---

## 5. 뷰 정의

### 5.1 v_recent_hands (최근 핸드 뷰)

```sql
-- ============================================================================
-- v_recent_hands: 최근 핸드 + 등급 정보 뷰
-- ============================================================================

CREATE OR REPLACE VIEW v_recent_hands AS
SELECT
    h.id,
    h.session_id,
    h.hand_num,
    h.game_variant,
    h.bet_structure,
    h.duration_seconds,
    h.start_time,
    h.pot_size,
    h.board_cards,
    h.winner_name,
    h.player_count,
    h.showdown_count,
    s.table_type,
    s.event_title,
    g.grade,
    g.broadcast_eligible,
    g.conditions_met
FROM gfx_hands h
LEFT JOIN gfx_sessions s ON h.session_id = s.session_id
LEFT JOIN hand_grades g ON h.id = g.hand_id
ORDER BY h.start_time DESC;
```

### 5.2 v_showdown_players (쇼다운 플레이어 뷰)

```sql
-- ============================================================================
-- v_showdown_players: 쇼다운 플레이어 (홀카드 공개)
-- ============================================================================

CREATE OR REPLACE VIEW v_showdown_players AS
SELECT
    hp.id,
    hp.hand_id,
    hp.player_name,
    hp.seat_num,
    hp.hole_cards,
    hp.start_stack_amt,
    hp.end_stack_amt,
    hp.cumulative_winnings_amt,
    hp.is_winner,
    h.hand_num,
    h.board_cards,
    h.pot_size,
    h.session_id
FROM gfx_hand_players hp
JOIN gfx_hands h ON hp.hand_id = h.id
WHERE hp.has_shown = TRUE
ORDER BY h.start_time DESC, hp.seat_num;
```

### 5.3 v_session_summary (세션 요약 뷰)

```sql
-- ============================================================================
-- v_session_summary: 세션 요약 통계
-- ============================================================================

CREATE OR REPLACE VIEW v_session_summary AS
SELECT
    s.id,
    s.session_id,
    s.file_name,
    s.table_type,
    s.event_title,
    s.hand_count,
    s.total_duration_seconds,
    s.session_created_at,
    s.sync_status,
    COUNT(CASE WHEN g.grade = 'A' THEN 1 END) AS grade_a_count,
    COUNT(CASE WHEN g.grade = 'B' THEN 1 END) AS grade_b_count,
    COUNT(CASE WHEN g.grade = 'C' THEN 1 END) AS grade_c_count,
    COUNT(CASE WHEN g.broadcast_eligible THEN 1 END) AS eligible_count
FROM gfx_sessions s
LEFT JOIN gfx_hands h ON s.session_id = h.session_id
LEFT JOIN hand_grades g ON h.id = g.hand_id
GROUP BY s.id, s.session_id, s.file_name, s.table_type,
         s.event_title, s.hand_count, s.total_duration_seconds,
         s.session_created_at, s.sync_status
ORDER BY s.session_created_at DESC;
```

---

## 6. 함수 및 트리거

### 6.1 updated_at 자동 갱신

```sql
-- ============================================================================
-- 트리거 함수: updated_at 자동 갱신
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 각 테이블에 트리거 적용
CREATE TRIGGER update_gfx_sessions_updated_at
    BEFORE UPDATE ON gfx_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gfx_hands_updated_at
    BEFORE UPDATE ON gfx_hands
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gfx_players_updated_at
    BEFORE UPDATE ON gfx_players
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 6.2 플레이어 해시 생성

```sql
-- ============================================================================
-- 함수: 플레이어 고유 해시 생성
-- ============================================================================

CREATE OR REPLACE FUNCTION generate_player_hash(p_name TEXT, p_long_name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN md5(LOWER(TRIM(COALESCE(p_name, ''))) || ':' || LOWER(TRIM(COALESCE(p_long_name, ''))));
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

### 6.3 세션 통계 업데이트

```sql
-- ============================================================================
-- 함수: 세션 통계 업데이트
-- ============================================================================

CREATE OR REPLACE FUNCTION update_session_stats(p_session_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE gfx_sessions
    SET
        hand_count = (
            SELECT COUNT(*) FROM gfx_hands WHERE session_id = p_session_id
        ),
        total_duration_seconds = (
            SELECT COALESCE(SUM(duration_seconds), 0)
            FROM gfx_hands WHERE session_id = p_session_id
        ),
        session_start_time = (
            SELECT MIN(start_time) FROM gfx_hands WHERE session_id = p_session_id
        ),
        session_end_time = (
            SELECT MAX(start_time + (duration_seconds || ' seconds')::INTERVAL)
            FROM gfx_hands WHERE session_id = p_session_id
        ),
        updated_at = NOW()
    WHERE session_id = p_session_id;
END;
$$ LANGUAGE plpgsql;
```

### 6.4 ISO 8601 Duration 파싱

```sql
-- ============================================================================
-- 함수: ISO 8601 Duration을 초 단위로 변환
-- 입력 예: "PT39.2342715S", "PT35M37.2477537S"
-- ============================================================================

CREATE OR REPLACE FUNCTION parse_iso8601_duration(duration TEXT)
RETURNS NUMERIC AS $$
DECLARE
    days_match TEXT[];
    hours_match TEXT[];
    minutes_match TEXT[];
    seconds_match TEXT[];
    total_seconds NUMERIC := 0;
BEGIN
    IF duration IS NULL OR duration = '' THEN
        RETURN 0;
    END IF;

    -- 일 (D)
    days_match := regexp_match(duration, '(\d+(?:\.\d+)?)D', 'i');
    IF days_match IS NOT NULL THEN
        total_seconds := total_seconds + (days_match[1]::NUMERIC * 86400);
    END IF;

    -- 시간 (H)
    hours_match := regexp_match(duration, '(\d+(?:\.\d+)?)H', 'i');
    IF hours_match IS NOT NULL THEN
        total_seconds := total_seconds + (hours_match[1]::NUMERIC * 3600);
    END IF;

    -- 분 (M) - T 이후에만
    minutes_match := regexp_match(duration, 'T.*?(\d+(?:\.\d+)?)M', 'i');
    IF minutes_match IS NOT NULL THEN
        total_seconds := total_seconds + (minutes_match[1]::NUMERIC * 60);
    END IF;

    -- 초 (S)
    seconds_match := regexp_match(duration, '(\d+(?:\.\d+)?)S', 'i');
    IF seconds_match IS NOT NULL THEN
        total_seconds := total_seconds + seconds_match[1]::NUMERIC;
    END IF;

    RETURN total_seconds;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

---

## 7. 인덱스 전략 및 쿼리 패턴

### 7.1 주요 쿼리 패턴

| 쿼리 패턴 | 설명 | 최적화 인덱스 |
|-----------|------|---------------|
| 최근 세션 조회 | `ORDER BY session_created_at DESC` | `idx_gfx_sessions_created_at` |
| 파일 중복 체크 | `WHERE file_hash = ?` | `idx_gfx_sessions_file_hash` (UNIQUE) |
| 세션별 핸드 조회 | `WHERE session_id = ?` | `idx_gfx_hands_session_id` |
| 핸드별 이벤트 조회 | `WHERE hand_id = ? ORDER BY event_order` | `idx_gfx_events_order` |
| 방송 적격 핸드 | `WHERE broadcast_eligible = TRUE` | `idx_hand_grades_eligible` (partial) |
| 프리미엄 보드 검색 | `WHERE 'Ah' = ANY(board_cards)` | `idx_gfx_hands_board_cards` (GIN) |
| 쇼다운 플레이어 | `WHERE has_shown = TRUE` | `idx_gfx_hand_players_shown` (partial) |
| 플레이어별 핸드 | `WHERE player_id = ?` | `idx_gfx_hand_players_player_id` |

### 7.2 인덱스 요약

```sql
-- Primary Keys (자동 생성)
-- gfx_sessions.id, gfx_hands.id, gfx_events.id, gfx_players.id, gfx_hand_players.id

-- Unique Constraints
-- gfx_sessions.session_id, gfx_sessions.file_hash
-- gfx_players.player_hash
-- (session_id, hand_num), (hand_id, seat_num), (hand_id, event_order)

-- B-tree Indexes (범위/정렬 쿼리)
-- gfx_sessions: session_created_at DESC, processed_at DESC
-- gfx_hands: start_time DESC, pot_size DESC, duration_seconds DESC
-- gfx_events: (hand_id, event_order)

-- GIN Indexes (배열/JSONB 검색)
-- gfx_hands.board_cards
-- gfx_hand_players.hole_cards
-- gfx_sessions.raw_json (선택적)

-- Partial Indexes (조건부 최적화)
-- hand_grades.broadcast_eligible WHERE TRUE
-- gfx_hand_players.is_winner WHERE TRUE
-- gfx_hand_players.has_shown WHERE TRUE
-- gfx_events.event_type WHERE 'BOARD_CARD'
```

---

## 8. RLS 정책 (Row Level Security)

```sql
-- ============================================================================
-- RLS 정책 설정 (Supabase 환경)
-- ============================================================================

-- 모든 테이블 RLS 활성화
ALTER TABLE gfx_players ENABLE ROW LEVEL SECURITY;
ALTER TABLE gfx_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE gfx_hands ENABLE ROW LEVEL SECURITY;
ALTER TABLE gfx_hand_players ENABLE ROW LEVEL SECURITY;
ALTER TABLE gfx_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE hand_grades ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_log ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- gfx_players 정책
-- ============================================================================
CREATE POLICY "gfx_players_select_authenticated"
    ON gfx_players FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "gfx_players_insert_service"
    ON gfx_players FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "gfx_players_update_service"
    ON gfx_players FOR UPDATE
    USING (auth.role() = 'service_role');

-- ============================================================================
-- gfx_sessions 정책
-- ============================================================================
CREATE POLICY "gfx_sessions_select_authenticated"
    ON gfx_sessions FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "gfx_sessions_insert_service"
    ON gfx_sessions FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "gfx_sessions_update_service"
    ON gfx_sessions FOR UPDATE
    USING (auth.role() = 'service_role');

-- ============================================================================
-- gfx_hands 정책
-- ============================================================================
CREATE POLICY "gfx_hands_select_authenticated"
    ON gfx_hands FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "gfx_hands_insert_service"
    ON gfx_hands FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

-- ============================================================================
-- gfx_hand_players 정책
-- ============================================================================
CREATE POLICY "gfx_hand_players_select_authenticated"
    ON gfx_hand_players FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "gfx_hand_players_insert_service"
    ON gfx_hand_players FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

-- ============================================================================
-- gfx_events 정책
-- ============================================================================
CREATE POLICY "gfx_events_select_authenticated"
    ON gfx_events FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "gfx_events_insert_service"
    ON gfx_events FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

-- ============================================================================
-- hand_grades 정책
-- ============================================================================
CREATE POLICY "hand_grades_select_authenticated"
    ON hand_grades FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "hand_grades_insert_service"
    ON hand_grades FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "hand_grades_update_service"
    ON hand_grades FOR UPDATE
    USING (auth.role() = 'service_role');

-- ============================================================================
-- sync_log 정책
-- ============================================================================
CREATE POLICY "sync_log_select_authenticated"
    ON sync_log FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "sync_log_all_service"
    ON sync_log FOR ALL
    USING (auth.role() = 'service_role');
```

---

## 9. 마이그레이션 순서

### 실행 순서

```
1. ENUM 타입 생성 (CREATE TYPE)
2. gfx_players 테이블 생성
3. gfx_sessions 테이블 생성
4. gfx_hands 테이블 생성
5. gfx_hand_players 테이블 생성
6. gfx_events 테이블 생성
7. hand_grades 테이블 생성
8. sync_log 테이블 생성
9. 뷰 생성 (CREATE VIEW)
10. 함수 생성 (CREATE FUNCTION)
11. 트리거 생성 (CREATE TRIGGER)
12. 인덱스 생성 (CREATE INDEX)
13. RLS 정책 적용 (ALTER TABLE, CREATE POLICY)
```

### Rollback 순서 (역순)

```
1. RLS 정책 삭제 (DROP POLICY)
2. 인덱스 삭제 (DROP INDEX)
3. 트리거 삭제 (DROP TRIGGER)
4. 함수 삭제 (DROP FUNCTION)
5. 뷰 삭제 (DROP VIEW)
6. 테이블 삭제 (역순: sync_log → hand_grades → gfx_events → ...)
7. ENUM 타입 삭제 (DROP TYPE)
```

---

## 10. 제약조건 요약

| 테이블 | 제약조건 | 설명 |
|--------|----------|------|
| `gfx_sessions` | `session_id UNIQUE` | PokerGFX ID 중복 방지 |
| `gfx_sessions` | `file_hash UNIQUE` | 파일 중복 동기화 방지 |
| `gfx_hands` | `(session_id, hand_num) UNIQUE` | 세션 내 핸드 번호 중복 방지 |
| `gfx_hand_players` | `(hand_id, seat_num) UNIQUE` | 핸드 내 시트 중복 방지 |
| `gfx_hand_players` | `seat_num BETWEEN 1 AND 10` | 유효 시트 번호 |
| `gfx_events` | `(hand_id, event_order) UNIQUE` | 이벤트 순서 중복 방지 |
| `hand_grades` | `grade IN ('A','B','C')` | 유효 등급 값 |
| `hand_grades` | `conditions_met BETWEEN 0 AND 3` | 유효 조건 수 |

---

## 11. 구현 연동 파일

| 파일 | 역할 | 연동 테이블 |
|------|------|-------------|
| `src/database/supabase_repository.py` | Repository 패턴 | 모든 테이블 |
| `src/primary/pokergfx_file_parser.py` | JSON 파싱 | gfx_sessions, gfx_hands |
| `src/models/hand.py` | 도메인 모델 | gfx_hands, gfx_hand_players |
| `src/grading/grader.py` | 등급 분류 | hand_grades |
| `src/sync_agent/sync_service.py` | NAS 동기화 | sync_log |

---

## Appendix: 카드 표기법

### 카드 랭크

| 표기 | 랭크 |
|------|------|
| 2-9 | 숫자 |
| 10 | Ten |
| j | Jack |
| q | Queen |
| k | King |
| a | Ace |

### 수트 (Suit)

| 표기 | 수트 |
|------|------|
| s | Spade |
| h | Heart |
| d | Diamond |
| c | Club |

### 예시

- `as` = Ace of Spades
- `10d` = Ten of Diamonds
- `kh` = King of Hearts
