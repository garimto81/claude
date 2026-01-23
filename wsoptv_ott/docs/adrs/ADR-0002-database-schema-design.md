# ADR-0002: WSOPTV OTT Database Schema Design

| 항목 | 값 |
|------|---|
| **Status** | Approved |
| **Impact** | High |
| **Created** | 2026-01-19 |
| **Updated** | 2026-01-19 |
| **Author** | Claude Code |
| **References** | wsop.com, PRD-0002, PRD-0006 |

---

## Context

WSOPTV OTT 플랫폼 구축을 위해 데이터베이스 스키마 설계가 필요합니다. 다음 소스를 참조하여 설계:

1. **wsop.com** 공식 사이트 구조 분석
2. **PRD-0002** MVP 요구사항
3. **PRD-0006** Advanced Mode 요구사항
4. **Hendon Mob Poker DB** 업계 표준 참조

---

## Decision

### wsop.com 실제 계층 구조

wsop.com 분석 결과, **WSOP가 최상위 브랜드**이고 하위에 여러 시리즈가 존재합니다:

```
WSOP (브랜드)
├── WSOP (본대회 - Las Vegas)
├── WSOP Paradise
├── WSOP Europe
├── WSOP Asia
├── WSOP Online
└── WSOP Circuit (지역 순회 대회)
```

### 엔티티 관계 다이어그램 (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     WSOPTV OTT Database Schema (v2.0)                            │
│                     WSOP 브랜드 기반 계층 구조                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                            WSOP (브랜드 - 암묵적 최상위)                      │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                       │                                          │
│                                       ▼                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                     │
│  │   series     │────<│   events     │────<│  sessions    │                     │
│  │ (시리즈)     │     │ (이벤트)     │     │ (세션/데이)  │                     │
│  │              │     │              │     │              │                     │
│  │ WSOP 2026    │     │ Main Event   │     │ Day 1A       │                     │
│  │ WSOP Paradise│     │ High Roller  │     │ Day 2        │                     │
│  │ WSOP Europe  │     │ $1K Daily    │     │ Final Table  │                     │
│  │ WSOP Circuit │     │              │     │              │                     │
│  └──────────────┘     └──────────────┘     └──────────────┘                     │
│         │                    │                    │                              │
│         │                    │                    │                              │
│         ▼                    ▼                    ▼                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                     │
│  │ series_points│     │event_schedule│     │   tables     │                     │
│  │ (POY 포인트) │     │ (스케줄)     │     │ (테이블)     │                     │
│  └──────────────┘     └──────────────┘     └──────────────┘                     │
│                                                   │                              │
│                                                   ▼                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                     │
│  │   players    │────<│ placements   │────<│   hands      │                     │
│  │ (플레이어)   │     │ (순위/결과)  │     │ (핸드)       │                     │
│  └──────────────┘     └──────────────┘     └──────────────┘                     │
│         │                    │                    │                              │
│         ▼                    ▼                    ▼                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                     │
│  │ player_stats │     │   earnings   │     │ hand_actions │                     │
│  │ (통계)       │     │ (수입)       │     │ (액션 로그)  │                     │
│  └──────────────┘     └──────────────┘     └──────────────┘                     │
│                                                   │                              │
│                                                   ▼                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                     │
│  │   content    │────<│  key_hands   │────<│ hand_players │                     │
│  │ (콘텐츠)     │     │ (주요 핸드)  │     │ (핸드 참여자)│                     │
│  └──────────────┘     └──────────────┘     └──────────────┘                     │
│         │                                                                        │
│         ▼                                                                        │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                     │
│  │content_streams│    │subscriptions │────<│   users      │                     │
│  │ (스트림 URL) │     │ (구독)       │     │ (사용자)     │                     │
│  └──────────────┘     └──────────────┘     └──────────────┘                     │
│                                                   │                              │
│                                                   ▼                              │
│                        ┌──────────────┐     ┌──────────────┐                     │
│                        │ leaderboards │     │watch_history │                     │
│                        │ (리더보드)   │     │ (시청 기록)  │                     │
│                        └──────────────┘     └──────────────┘                     │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 핵심 변경 사항 (v1.0 → v2.0)

| 항목 | v1.0 (기존) | v2.0 (수정) | 변경 이유 |
|------|------------|------------|-----------|
| **최상위 테이블** | `circuits` | `series` | wsop.com 구조 반영 - WSOP가 브랜드, 하위에 시리즈 |
| **시리즈 유형** | `circuit_type` | `series_type` | 명확한 명명 |
| **세션 테이블** | `tournaments` | `sessions` | Day/Flight 단위 세션 명확화 |
| **포인트 테이블** | `circuit_points` | `series_points` | 시리즈 기반 POY 포인트 |

---

## Schema Definition

### 1. Core Tournament Entities

#### 1.1 series (시리즈)

WSOP 브랜드 하위의 시리즈 (WSOP 본대회, Paradise, Europe, Asia, Online, Circuit 등)

```sql
CREATE TABLE series (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic Info
    name VARCHAR(255) NOT NULL,                    -- "WSOP 2026", "WSOP Paradise 2026"
    slug VARCHAR(100) UNIQUE NOT NULL,             -- "wsop-2026", "wsop-paradise-2026"
    series_type VARCHAR(50) NOT NULL,              -- 'wsop', 'wsop_paradise', 'wsop_europe', 'wsop_asia', 'wsop_online', 'wsop_circuit'

    -- Dates
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    year INTEGER NOT NULL,

    -- Location
    venue_name VARCHAR(255),                       -- "Paris Las Vegas & Horseshoe Las Vegas"
    city VARCHAR(100),                             -- "Las Vegas"
    country_code CHAR(2),                          -- "US"

    -- Stats (wsop.com 참조)
    total_events INTEGER DEFAULT 0,                -- 100 (for WSOP 2025)
    total_bracelets INTEGER DEFAULT 0,             -- 100
    total_prize_pool BIGINT DEFAULT 0,             -- Total prize money in cents
    total_entries INTEGER DEFAULT 0,

    -- Media
    logo_url VARCHAR(500),
    banner_url VARCHAR(500),

    -- Status
    status VARCHAR(20) DEFAULT 'upcoming',         -- 'upcoming', 'live', 'completed'
    is_featured BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_series_year ON series(year);
CREATE INDEX idx_series_type ON series(series_type);
CREATE INDEX idx_series_status ON series(status);
CREATE INDEX idx_series_dates ON series(start_date, end_date);
```

#### 1.2 events (이벤트/브래킷)

각 시리즈 내의 개별 이벤트 (Main Event, High Roller 등)

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    series_id UUID NOT NULL REFERENCES series(id) ON DELETE CASCADE,

    -- Event Info (wsop.com 참조)
    event_number INTEGER NOT NULL,                 -- Event #81 (Main Event)
    name VARCHAR(500) NOT NULL,                    -- "No Limit Hold'em - Main Event World Championship"
    short_name VARCHAR(100),                       -- "Main Event"
    slug VARCHAR(150) UNIQUE NOT NULL,

    -- Game Details
    game_type VARCHAR(50) NOT NULL,                -- 'no_limit_holdem', 'pot_limit_omaha', 'mixed', 'razz', etc.
    game_variant VARCHAR(100),                     -- "No Limit Hold'em", "Pot Limit Omaha Hi-Lo"
    tournament_type VARCHAR(50) DEFAULT 'freezeout', -- 'freezeout', 'rebuy', 'bounty', 'shootout', 'heads_up'

    -- Buy-in Structure
    buy_in BIGINT NOT NULL,                        -- Buy-in in cents ($10,000 = 1000000)
    rake BIGINT DEFAULT 0,                         -- Rake/fee in cents
    starting_stack INTEGER,                        -- Starting chips

    -- Blind Structure
    blind_levels JSONB,                            -- Array of blind levels
    level_duration_minutes INTEGER,                -- Duration per level

    -- Dates & Schedule
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ,
    days_count INTEGER DEFAULT 1,

    -- Results (wsop.com 참조)
    total_entries INTEGER DEFAULT 0,               -- 9,735 (Main Event 2025)
    unique_entries INTEGER DEFAULT 0,              -- Unique players (no re-entries)
    reentries INTEGER DEFAULT 0,
    prize_pool BIGINT DEFAULT 0,                   -- $90,535,500 = 9053550000 cents
    places_paid INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'scheduled',        -- 'scheduled', 'registration', 'running', 'final_table', 'completed', 'cancelled'
    current_day INTEGER DEFAULT 0,
    remaining_players INTEGER DEFAULT 0,

    -- Bracelet
    is_bracelet_event BOOLEAN DEFAULT TRUE,
    bracelet_number INTEGER,                       -- Historical bracelet number

    -- Media & Content
    featured_image_url VARCHAR(500),
    description TEXT,

    -- Flags
    is_main_event BOOLEAN DEFAULT FALSE,
    is_high_roller BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(series_id, event_number)
);

-- Indexes
CREATE INDEX idx_events_series ON events(series_id);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_game_type ON events(game_type);
CREATE INDEX idx_events_dates ON events(start_date, end_date);
CREATE INDEX idx_events_buy_in ON events(buy_in);
CREATE INDEX idx_events_featured ON events(is_featured) WHERE is_featured = TRUE;
```

#### 1.3 sessions (세션/데이)

이벤트의 각 Day 또는 Flight 세션

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,

    -- Session Info
    day_number INTEGER NOT NULL,                   -- Day 1A, Day 1B, Day 2, Final Table
    flight_name VARCHAR(50),                       -- "1A", "1B", "1C", "2", "Final"
    session_type VARCHAR(50) DEFAULT 'day',        -- 'day', 'flight', 'final_table'

    -- Schedule
    scheduled_start TIMESTAMPTZ NOT NULL,
    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,

    -- Status
    status VARCHAR(20) DEFAULT 'scheduled',        -- 'scheduled', 'running', 'on_break', 'completed'
    current_level INTEGER DEFAULT 0,
    current_blind_small BIGINT,
    current_blind_big BIGINT,
    current_ante BIGINT,

    -- Stats
    starting_players INTEGER DEFAULT 0,
    remaining_players INTEGER DEFAULT 0,
    total_chips_in_play BIGINT DEFAULT 0,
    average_stack BIGINT DEFAULT 0,

    -- Live Streaming (PRD-0002 참조)
    is_streaming BOOLEAN DEFAULT FALSE,
    stream_url VARCHAR(500),
    stream_delay_minutes INTEGER DEFAULT 30,       -- 30분 지연 방송

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(event_id, day_number, flight_name)
);

-- Indexes
CREATE INDEX idx_sessions_event ON sessions(event_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_streaming ON sessions(is_streaming) WHERE is_streaming = TRUE;
CREATE INDEX idx_sessions_schedule ON sessions(scheduled_start);
```

---

### 2. Player Entities

#### 2.1 players (플레이어)

wsop.com Player Database 기반

```sql
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    ggpoker_id VARCHAR(100) UNIQUE,                -- GGPoker 연동 ID
    wsop_id VARCHAR(100) UNIQUE,                   -- WSOP 공식 ID
    hendon_mob_id INTEGER UNIQUE,                  -- Hendon Mob ID (업계 표준)

    -- Basic Info
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),                     -- "Phil Ivey", "Daniel Negreanu"
    nickname VARCHAR(100),                         -- "The Tiger Woods of Poker"

    -- Demographics
    country_code CHAR(2),                          -- ISO 3166-1 alpha-2
    country_name VARCHAR(100),
    city VARCHAR(100),
    birth_date DATE,

    -- Profile
    avatar_url VARCHAR(500),
    banner_url VARCHAR(500),
    bio TEXT,

    -- Career Stats (wsop.com Player Standings 참조)
    total_earnings BIGINT DEFAULT 0,               -- All-time earnings in cents
    wsop_earnings BIGINT DEFAULT 0,                -- WSOP-only earnings
    wsop_bracelets INTEGER DEFAULT 0,              -- Gold bracelets
    wsop_rings INTEGER DEFAULT 0,                  -- Circuit rings
    wsop_final_tables INTEGER DEFAULT 0,
    wsop_cashes INTEGER DEFAULT 0,
    wsop_best_finish INTEGER,                      -- Best finish (1 = win)

    -- Rankings (wsop.com Leaderboards 참조)
    all_time_rank INTEGER,                         -- All-time money list rank
    current_year_rank INTEGER,
    poy_points INTEGER DEFAULT 0,                  -- Player of the Year points

    -- GGPoker HUD Stats (PRD-0006 StatsView 참조)
    hud_vpip DECIMAL(5,2),                         -- Voluntarily Put $ In Pot %
    hud_pfr DECIMAL(5,2),                          -- Pre-Flop Raise %
    hud_3bet DECIMAL(5,2),                         -- 3-Bet %
    hud_af DECIMAL(5,2),                           -- Aggression Factor
    hud_flop_cbet DECIMAL(5,2),                    -- Flop C-Bet %
    hud_fold_to_cbet DECIMAL(5,2),                 -- Fold to C-Bet %
    hud_wtsd DECIMAL(5,2),                         -- Went to Showdown %
    hud_won_at_sd DECIMAL(5,2),                    -- Won at Showdown %
    hud_hands_played INTEGER DEFAULT 0,            -- Total hands for stats
    hud_last_updated TIMESTAMPTZ,

    -- Social Links
    twitter_handle VARCHAR(100),
    instagram_handle VARCHAR(100),
    youtube_channel VARCHAR(200),

    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    is_pro BOOLEAN DEFAULT FALSE,                  -- GGPoker Pro, etc.
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_players_name ON players(last_name, first_name);
CREATE INDEX idx_players_country ON players(country_code);
CREATE INDEX idx_players_earnings ON players(total_earnings DESC);
CREATE INDEX idx_players_bracelets ON players(wsop_bracelets DESC);
CREATE INDEX idx_players_ggpoker ON players(ggpoker_id) WHERE ggpoker_id IS NOT NULL;

-- Full-text search
CREATE INDEX idx_players_search ON players USING gin(
    to_tsvector('english', coalesce(first_name, '') || ' ' || coalesce(last_name, '') || ' ' || coalesce(nickname, ''))
);
```

#### 2.2 placements (순위/결과)

wsop.com Past Tournaments 결과 기반

```sql
CREATE TABLE placements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id),        -- Final table session

    -- Finish
    finish_position INTEGER NOT NULL,              -- 1 = winner
    prize_amount BIGINT NOT NULL,                  -- Prize in cents

    -- Points (wsop.com 포인트 시스템)
    poy_points INTEGER DEFAULT 0,                  -- Player of the Year points
    series_points INTEGER DEFAULT 0,               -- Series points (POY)

    -- Bracelet/Ring
    won_bracelet BOOLEAN DEFAULT FALSE,
    won_ring BOOLEAN DEFAULT FALSE,

    -- Final Table Stats
    final_table_chips BIGINT,                      -- Chips at final table start
    heads_up_chips BIGINT,                         -- Chips at heads-up start

    -- Timestamps
    eliminated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(event_id, player_id)
);

-- Indexes
CREATE INDEX idx_placements_event ON placements(event_id);
CREATE INDEX idx_placements_player ON placements(player_id);
CREATE INDEX idx_placements_finish ON placements(finish_position);
CREATE INDEX idx_placements_prize ON placements(prize_amount DESC);
CREATE INDEX idx_placements_bracelet ON placements(won_bracelet) WHERE won_bracelet = TRUE;
```

#### 2.3 player_stats (플레이어 통계 스냅샷)

이벤트별 플레이어 통계 (PRD-0006 Player Stats 테이블 참조)

```sql
CREATE TABLE player_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,

    -- Scope
    stat_type VARCHAR(20) NOT NULL,                -- 'event', 'tournament', 'session', 'all_time'

    -- Basic Stats
    hands_played INTEGER DEFAULT 0,
    hands_won INTEGER DEFAULT 0,
    pots_won INTEGER DEFAULT 0,

    -- Preflop Stats (NBA Box Score 스타일 매핑)
    vpip DECIMAL(5,2),                             -- VPIP % → FG%
    pfr DECIMAL(5,2),                              -- PFR % → 3P%
    three_bet DECIMAL(5,2),                        -- 3-Bet %
    four_bet DECIMAL(5,2),                         -- 4-Bet %
    fold_to_3bet DECIMAL(5,2),

    -- Postflop Stats
    cbet DECIMAL(5,2),                             -- C-Bet %
    fold_to_cbet DECIMAL(5,2),
    check_raise DECIMAL(5,2),

    -- Aggression
    aggression_factor DECIMAL(5,2),                -- AF
    aggression_frequency DECIMAL(5,2),

    -- Win Rates
    win_rate_bb_100 DECIMAL(8,4),                  -- BB/100 hands
    roi DECIMAL(8,4),                              -- ROI %
    itm_percent DECIMAL(5,2),                      -- In The Money %

    -- Chips
    chips_won BIGINT DEFAULT 0,
    chips_lost BIGINT DEFAULT 0,
    net_chips BIGINT DEFAULT 0,                    -- Chips +/- (NBA +/- 대응)
    biggest_pot_won BIGINT DEFAULT 0,

    -- Bluffs (PRD-0006)
    bluff_attempts INTEGER DEFAULT 0,
    bluff_success INTEGER DEFAULT 0,
    bluff_success_rate DECIMAL(5,2),

    -- Position Stats (PRD-0006 Position Analysis 참조)
    position_stats JSONB,                          -- {"UTG": {"hands": 10, "won": 2}, ...}

    -- Timestamps
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_player_stats_player ON player_stats(player_id);
CREATE INDEX idx_player_stats_event ON player_stats(event_id);
CREATE INDEX idx_player_stats_type ON player_stats(stat_type);
```

---

### 3. Hand History Entities (PRD-0006 기반)

#### 3.1 tables (테이블)

피처 테이블 정보 (3계층 Multi-view)

```sql
CREATE TABLE tables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    -- Table Info
    table_number INTEGER NOT NULL,
    table_name VARCHAR(100),                       -- "Main Feature Table", "Secondary"

    -- Type (PRD-0006 3계층 구조)
    table_type VARCHAR(50) DEFAULT 'standard',     -- 'feature', 'secondary', 'standard'
    is_feature_table BOOLEAN DEFAULT FALSE,
    has_player_cams BOOLEAN DEFAULT FALSE,         -- PlayerCAM 지원 여부

    -- Current State
    status VARCHAR(20) DEFAULT 'active',           -- 'active', 'on_break', 'closed'
    current_hand_number INTEGER DEFAULT 0,
    seats_occupied INTEGER DEFAULT 0,

    -- Streaming (PRD-0006)
    stream_url VARCHAR(500),                       -- Table-specific stream
    player_cam_urls JSONB,                         -- {"seat_1": "url", "seat_2": "url", ...}

    -- Tournament Strip Info (PRD-0006)
    current_pot BIGINT DEFAULT 0,
    current_small_blind BIGINT,
    current_big_blind BIGINT,

    -- Timestamps
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(session_id, table_number)
);

-- Indexes
CREATE INDEX idx_tables_session ON tables(session_id);
CREATE INDEX idx_tables_feature ON tables(is_feature_table) WHERE is_feature_table = TRUE;
CREATE INDEX idx_tables_status ON tables(status);
```

#### 3.2 hands (핸드)

개별 핸드 기록

```sql
CREATE TABLE hands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_id UUID NOT NULL REFERENCES tables(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    -- Hand Info
    hand_number INTEGER NOT NULL,                  -- Sequential hand number
    hand_id VARCHAR(100) UNIQUE,                   -- External hand ID

    -- Timing
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    video_timestamp_start INTEGER,                 -- Seconds from stream start
    video_timestamp_end INTEGER,

    -- Blinds/Stakes
    small_blind BIGINT NOT NULL,
    big_blind BIGINT NOT NULL,
    ante BIGINT DEFAULT 0,

    -- Board (Community Cards)
    flop_card_1 CHAR(2),                           -- "Ah", "Ks", "7d"
    flop_card_2 CHAR(2),
    flop_card_3 CHAR(2),
    turn_card CHAR(2),
    river_card CHAR(2),
    board VARCHAR(20),                             -- "Ah Ks 7d 2c Tc"

    -- Pot
    pot_preflop BIGINT DEFAULT 0,
    pot_flop BIGINT DEFAULT 0,
    pot_turn BIGINT DEFAULT 0,
    pot_river BIGINT DEFAULT 0,
    pot_total BIGINT NOT NULL,
    rake BIGINT DEFAULT 0,

    -- Result
    winner_player_id UUID REFERENCES players(id),
    winning_hand VARCHAR(50),                      -- "Full House, Aces over Kings"
    winning_cards VARCHAR(10),                     -- "AA" (hole cards)
    went_to_showdown BOOLEAN DEFAULT FALSE,

    -- Hand Summary (PRD-0006 Hand Info 패널)
    hand_summary JSONB,                            -- Detailed action breakdown

    -- Key Hand Flag (PRD-0006)
    is_key_hand BOOLEAN DEFAULT FALSE,
    key_hand_reason VARCHAR(200),                  -- "Phil Ivey 4-bet bluff"
    key_hand_tags TEXT[],                          -- ["bluff", "big_pot", "elimination"]

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(table_id, hand_number)
);

-- Indexes
CREATE INDEX idx_hands_table ON hands(table_id);
CREATE INDEX idx_hands_session ON hands(session_id);
CREATE INDEX idx_hands_winner ON hands(winner_player_id);
CREATE INDEX idx_hands_key ON hands(is_key_hand) WHERE is_key_hand = TRUE;
CREATE INDEX idx_hands_timestamp ON hands(started_at);
CREATE INDEX idx_hands_pot ON hands(pot_total DESC);
```

#### 3.3 hand_players (핸드 참여자)

핸드별 플레이어 정보

```sql
CREATE TABLE hand_players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hand_id UUID NOT NULL REFERENCES hands(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,

    -- Position (PRD-0006 Position Analysis)
    seat_number INTEGER NOT NULL,                  -- 1-10
    position VARCHAR(10) NOT NULL,                 -- 'BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'MP', 'MP+1', 'HJ', 'CO'
    is_button BOOLEAN DEFAULT FALSE,
    is_small_blind BOOLEAN DEFAULT FALSE,
    is_big_blind BOOLEAN DEFAULT FALSE,

    -- Stack
    stack_start BIGINT NOT NULL,                   -- Chips at hand start
    stack_end BIGINT NOT NULL,                     -- Chips at hand end

    -- Hole Cards (if known)
    hole_card_1 CHAR(2),                           -- "Ah"
    hole_card_2 CHAR(2),                           -- "Kh"
    cards_shown BOOLEAN DEFAULT FALSE,

    -- Result
    is_winner BOOLEAN DEFAULT FALSE,
    amount_won BIGINT DEFAULT 0,
    amount_invested BIGINT DEFAULT 0,              -- Total put in pot

    -- Action Summary
    folded_street VARCHAR(20),                     -- 'preflop', 'flop', 'turn', 'river', NULL
    went_to_showdown BOOLEAN DEFAULT FALSE,
    was_all_in BOOLEAN DEFAULT FALSE,

    -- PlayerCAM (PRD-0006)
    player_cam_clip_url VARCHAR(500),              -- Individual hand clip

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(hand_id, player_id)
);

-- Indexes
CREATE INDEX idx_hand_players_hand ON hand_players(hand_id);
CREATE INDEX idx_hand_players_player ON hand_players(player_id);
CREATE INDEX idx_hand_players_position ON hand_players(position);
CREATE INDEX idx_hand_players_winner ON hand_players(is_winner) WHERE is_winner = TRUE;
```

#### 3.4 hand_actions (핸드 액션)

Hand-by-Hand Log (PRD-0006 Play-by-Play 스타일)

```sql
CREATE TABLE hand_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hand_id UUID NOT NULL REFERENCES hands(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,

    -- Action Order
    action_order INTEGER NOT NULL,                 -- Sequential action number
    street VARCHAR(20) NOT NULL,                   -- 'preflop', 'flop', 'turn', 'river'

    -- Action Details
    action_type VARCHAR(20) NOT NULL,              -- 'fold', 'check', 'call', 'bet', 'raise', 'all_in'
    amount BIGINT DEFAULT 0,                       -- Bet/Raise amount
    raise_to BIGINT,                               -- Total raise amount (raise "to" X)
    is_all_in BOOLEAN DEFAULT FALSE,

    -- Pot State
    pot_after_action BIGINT NOT NULL,

    -- Video Sync (PRD-0006)
    video_timestamp INTEGER,                       -- Seconds from stream start

    -- Context
    facing_bet BIGINT DEFAULT 0,                   -- Bet/Raise player is facing

    -- Timestamps
    action_time TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_hand_actions_hand ON hand_actions(hand_id);
CREATE INDEX idx_hand_actions_player ON hand_actions(player_id);
CREATE INDEX idx_hand_actions_street ON hand_actions(street);
CREATE INDEX idx_hand_actions_order ON hand_actions(hand_id, action_order);
CREATE INDEX idx_hand_actions_type ON hand_actions(action_type);
```

---

### 4. Content & Streaming Entities (PRD-0002)

#### 4.1 content (콘텐츠)

VOD, Live, Quick VOD

```sql
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,

    -- Content Info
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,

    -- Type
    content_type VARCHAR(50) NOT NULL,             -- 'live', 'vod', 'quick_vod', 'highlight', 'archive'
    category VARCHAR(100),                         -- 'main_event', 'bracelet', 'high_roller', 'classics'

    -- Duration
    duration_seconds INTEGER,

    -- Thumbnail & Media
    thumbnail_url VARCHAR(500),
    poster_url VARCHAR(500),
    preview_url VARCHAR(500),                      -- Preview video URL

    -- Streaming (PRD-0002)
    is_live BOOLEAN DEFAULT FALSE,
    live_started_at TIMESTAMPTZ,
    live_ended_at TIMESTAMPTZ,

    -- Timeshift (PRD-0002 DVR)
    timeshift_enabled BOOLEAN DEFAULT TRUE,
    timeshift_window_hours INTEGER DEFAULT 24,

    -- Access
    subscription_tier VARCHAR(20) DEFAULT 'plus',  -- 'free', 'plus', 'plus_plus'
    is_advanced_mode BOOLEAN DEFAULT FALSE,        -- Plus+ only

    -- Metadata for Search (Collections Screen)
    year INTEGER,
    player_names TEXT[],                           -- For search: ["Phil Ivey", "Negreanu"]
    game_types TEXT[],                             -- ["No Limit Hold'em", "PLO"]
    tags TEXT[],

    -- Quick VOD Chapters
    chapters JSONB,                                -- [{"title": "Final Table Start", "timestamp": 0}, ...]

    -- Stats
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'draft',            -- 'draft', 'published', 'archived'
    published_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_content_event ON content(event_id);
CREATE INDEX idx_content_type ON content(content_type);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_live ON content(is_live) WHERE is_live = TRUE;
CREATE INDEX idx_content_tier ON content(subscription_tier);
CREATE INDEX idx_content_year ON content(year);
CREATE INDEX idx_content_published ON content(published_at DESC);

-- Full-text search for Collections
CREATE INDEX idx_content_search ON content USING gin(
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || array_to_string(player_names, ' ') || ' ' || array_to_string(tags, ' '))
);
```

#### 4.2 content_streams (스트림 URL)

HLS/DRM 스트림 정보

```sql
CREATE TABLE content_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,

    -- Stream Info
    stream_type VARCHAR(50) NOT NULL,              -- 'hls', 'dash', 'smooth'
    quality VARCHAR(20) NOT NULL,                  -- '1080p', '720p', '480p', '360p', 'auto'

    -- URLs
    stream_url VARCHAR(1000) NOT NULL,
    backup_url VARCHAR(1000),

    -- DRM (PRD-0002 NFR-2)
    drm_type VARCHAR(50),                          -- 'widevine', 'fairplay', 'playready'
    drm_license_url VARCHAR(500),

    -- Bitrate
    video_bitrate INTEGER,                         -- kbps
    audio_bitrate INTEGER,                         -- kbps

    -- Multi-view Streams (PRD-0006)
    is_pgm BOOLEAN DEFAULT FALSE,                  -- Main PGM stream
    is_feature_table BOOLEAN DEFAULT FALSE,
    is_player_cam BOOLEAN DEFAULT FALSE,
    table_id UUID REFERENCES tables(id),
    player_id UUID REFERENCES players(id),         -- For PlayerCAM

    -- Audio Options (PRD-0006 Streaming Options)
    audio_language VARCHAR(10) DEFAULT 'en',
    commentary_type VARCHAR(50),                   -- 'standard', 'analysis', 'beginner'

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_content_streams_content ON content_streams(content_id);
CREATE INDEX idx_content_streams_type ON content_streams(stream_type);
CREATE INDEX idx_content_streams_quality ON content_streams(quality);
CREATE INDEX idx_content_streams_pgm ON content_streams(is_pgm) WHERE is_pgm = TRUE;
```

#### 4.3 key_hands (주요 핸드 - PRD-0006)

Key Hands 모달용

```sql
CREATE TABLE key_hands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    hand_id UUID REFERENCES hands(id) ON DELETE SET NULL,

    -- Key Hand Info (PRD-0006 Key Plays 스타일)
    title VARCHAR(200) NOT NULL,                   -- "Phil Ivey 4-bet bluff"
    description TEXT,

    -- Video Position
    video_timestamp_start INTEGER NOT NULL,        -- Seconds from start
    video_timestamp_end INTEGER,

    -- Hand Context
    hand_number INTEGER,
    blinds_level VARCHAR(50),                      -- "Blinds 50K/100K"
    pot_size BIGINT,

    -- Thumbnail
    thumbnail_url VARCHAR(500),

    -- Players Involved
    player_ids UUID[],
    primary_player_id UUID REFERENCES players(id),

    -- Tags for filtering
    tags TEXT[],                                   -- ['bluff', 'big_pot', 'elimination', 'hero_call']

    -- Order
    display_order INTEGER DEFAULT 0,

    -- Status
    is_ai_generated BOOLEAN DEFAULT FALSE,         -- AI 자동 추출 여부 (P2)
    is_verified BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_key_hands_content ON key_hands(content_id);
CREATE INDEX idx_key_hands_hand ON key_hands(hand_id);
CREATE INDEX idx_key_hands_player ON key_hands(primary_player_id);
CREATE INDEX idx_key_hands_timestamp ON key_hands(video_timestamp_start);
CREATE INDEX idx_key_hands_order ON key_hands(content_id, display_order);
```

#### 4.4 subtitles (자막 - PRD-0002)

20개국 자막 지원

```sql
CREATE TABLE subtitles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,

    -- Language (20개국)
    language_code VARCHAR(10) NOT NULL,            -- 'en', 'ko', 'ja', 'zh', 'es', 'pt', 'de', 'fr', etc.
    language_name VARCHAR(50) NOT NULL,            -- "English", "한국어", "日本語"

    -- Subtitle Info
    subtitle_type VARCHAR(20) DEFAULT 'srt',       -- 'srt', 'vtt', 'ttml'
    subtitle_url VARCHAR(500) NOT NULL,

    -- Status
    is_default BOOLEAN DEFAULT FALSE,
    is_auto_generated BOOLEAN DEFAULT FALSE,       -- AI 번역 여부

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(content_id, language_code)
);

-- Indexes
CREATE INDEX idx_subtitles_content ON subtitles(content_id);
CREATE INDEX idx_subtitles_language ON subtitles(language_code);
```

---

### 5. User & Subscription Entities (PRD-0002)

#### 5.1 users (사용자)

GGPass SSO 연동

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- GGPass SSO (PRD-0002)
    ggpass_id VARCHAR(100) UNIQUE NOT NULL,        -- GGPass SSO ID
    ggpoker_id VARCHAR(100),                       -- GGPoker 연동

    -- Basic Info
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),

    -- Location
    country_code CHAR(2),
    timezone VARCHAR(50),
    preferred_language VARCHAR(10) DEFAULT 'en',

    -- Subscription (PRD-0002 FR-7)
    subscription_tier VARCHAR(20) DEFAULT 'free',  -- 'free', 'plus', 'plus_plus'
    subscription_status VARCHAR(20) DEFAULT 'active', -- 'active', 'cancelled', 'expired'
    subscription_started_at TIMESTAMPTZ,
    subscription_expires_at TIMESTAMPTZ,

    -- Preferences
    preferences JSONB DEFAULT '{}',                -- UI preferences, default quality, etc.

    -- Stats
    total_watch_time_seconds BIGINT DEFAULT 0,
    favorite_players UUID[],

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_ggpass ON users(ggpass_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
```

#### 5.2 subscriptions (구독 이력)

```sql
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Plan (PRD-0002 FR-7)
    plan_type VARCHAR(20) NOT NULL,                -- 'plus', 'plus_plus'
    plan_name VARCHAR(100),                        -- "WSOP Plus", "WSOP Plus+"
    price_cents INTEGER NOT NULL,                  -- $10 = 1000, $50 = 5000
    currency VARCHAR(3) DEFAULT 'USD',

    -- Billing Period
    billing_period VARCHAR(20) DEFAULT 'monthly',  -- 'monthly', 'yearly'
    started_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    cancelled_at TIMESTAMPTZ,

    -- GGPass Billing
    ggpass_transaction_id VARCHAR(100),

    -- Promo (PRD-0002 프로모션)
    promo_code VARCHAR(50),
    promo_type VARCHAR(50),                        -- 'ggpoker_chip_purchase', 'direct'
    ggpoker_chips_granted INTEGER DEFAULT 0,       -- 연동 칩 지급량

    -- Status
    status VARCHAR(20) DEFAULT 'active',           -- 'active', 'cancelled', 'expired', 'refunded'

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_plan ON subscriptions(plan_type);
CREATE INDEX idx_subscriptions_dates ON subscriptions(started_at, expires_at);
```

#### 5.3 watch_history (시청 기록)

이어보기 및 추천용

```sql
CREATE TABLE watch_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,

    -- Progress
    watch_progress_seconds INTEGER DEFAULT 0,
    watch_progress_percent DECIMAL(5,2) DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,

    -- Session Info
    device_type VARCHAR(50),                       -- 'web', 'ios', 'android', 'samsung_tv', 'lg_tv'
    quality_watched VARCHAR(20),

    -- Advanced Mode Usage (PRD-0006)
    used_multiview BOOLEAN DEFAULT FALSE,
    used_statsview BOOLEAN DEFAULT FALSE,
    used_key_hands BOOLEAN DEFAULT FALSE,
    view_mode_used VARCHAR(50),                    -- 'standard', 'multiview', 'statsview', 'combined'

    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_watched_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_watch_history_user ON watch_history(user_id);
CREATE INDEX idx_watch_history_content ON watch_history(content_id);
CREATE INDEX idx_watch_history_last ON watch_history(last_watched_at DESC);
CREATE INDEX idx_watch_history_user_content ON watch_history(user_id, content_id);
```

---

### 6. Series Points & Leaderboard (wsop.com 참조)

#### 6.1 series_points (시리즈 포인트)

```sql
CREATE TABLE series_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    series_id UUID NOT NULL REFERENCES series(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    placement_id UUID REFERENCES placements(id) ON DELETE SET NULL,

    -- Points (wsop.com 포인트 시스템)
    points INTEGER NOT NULL,
    points_type VARCHAR(50) NOT NULL,              -- 'poy', 'circuit', 'online', 'paradise', 'europe', 'asia'

    -- Rank at time of earning
    rank_at_time INTEGER,

    -- Context
    reason VARCHAR(200),                           -- "1st place - Main Event"

    -- Timestamps
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_series_points_player ON series_points(player_id);
CREATE INDEX idx_series_points_series ON series_points(series_id);
CREATE INDEX idx_series_points_type ON series_points(points_type);
CREATE INDEX idx_series_points_earned ON series_points(earned_at DESC);
```

#### 6.2 leaderboards (리더보드)

wsop.com Player Standings 스냅샷

```sql
CREATE TABLE leaderboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Leaderboard Type
    leaderboard_type VARCHAR(50) NOT NULL,         -- 'all_time_earnings', 'yearly_earnings', 'bracelets', 'poy_current', 'series_current'
    year INTEGER,
    series_id UUID REFERENCES series(id),

    -- Snapshot
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Rankings Data
    rankings JSONB NOT NULL,                       -- [{"rank": 1, "player_id": "uuid", "value": 1000000}, ...]

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_leaderboards_type ON leaderboards(leaderboard_type);
CREATE INDEX idx_leaderboards_year ON leaderboards(year);
CREATE INDEX idx_leaderboards_date ON leaderboards(snapshot_date DESC);
```

---

## Consequences

### Positive

1. **wsop.com 완벽 매핑**: 공식 사이트 데이터 구조와 1:1 호환
2. **PRD-0006 지원**: Advanced Mode의 모든 기능 (Multi-view, StatsView, Key Hands, Hand-by-Hand Log, Position Analysis) 지원
3. **확장성**: 향후 AI 기반 Key Hands 추출, 실시간 데이터 연동 등 확장 가능
4. **검색 최적화**: Full-text search 인덱스로 Collections 검색 성능 보장
5. **GGPass 통합**: SSO 및 구독 관리 완벽 지원

### Negative

1. **복잡도**: 테이블 수 증가로 인한 관리 복잡도
2. **스토리지**: 핸드 히스토리 데이터 누적 시 대용량 스토리지 필요
3. **동기화**: GGPoker HUD 데이터와의 실시간 동기화 필요

### Risks

1. **데이터 정합성**: 다중 소스(wsop.com, GGPoker, 프로덕션)에서의 데이터 충돌
2. **성능**: 대용량 핸드 히스토리 쿼리 시 성능 이슈
3. **마이그레이션**: 기존 PokerGo 데이터 마이그레이션 복잡도

---

## Migration Strategy

### Phase 1: Core Tables
- series, events, sessions
- players, placements
- content, content_streams

### Phase 2: Hand History
- tables, hands, hand_players, hand_actions
- key_hands

### Phase 3: User & Stats
- users, subscriptions, watch_history
- player_stats, series_points, leaderboards

### Phase 4: Search & Optimization
- Full-text search 인덱스
- 파티셔닝 (hands 테이블 - 연도별)
- Read replica 설정

---

## References

- [wsop.com](https://www.wsop.com) - 공식 사이트 구조
- [Hendon Mob Poker Database](https://pokerdb.thehendonmob.com) - 업계 표준 참조
- [PRD-0002](../prds/PRD-0002-wsoptv-ott-platform-mvp.md) - MVP 요구사항
- [PRD-0006](../prds/PRD-0006-advanced-mode.md) - Advanced Mode 요구사항

---

*Created: 2026-01-19*
