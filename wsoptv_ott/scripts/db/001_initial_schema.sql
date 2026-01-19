-- WSOPTV OTT Database Schema
-- Version: 1.0.0
-- Created: 2026-01-19
-- Reference: ADR-0002-database-schema-design.md

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. CORE TOURNAMENT ENTITIES
-- ============================================================================

-- 1.1 circuits (대회 시리즈)
-- WSOP 시리즈 정보 (WSOP Main, Paradise, Europe, Asia, Online, Circuit 등)
CREATE TABLE circuits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    circuit_type VARCHAR(50) NOT NULL,

    -- Dates
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    year INTEGER NOT NULL,

    -- Location
    venue_name VARCHAR(255),
    city VARCHAR(100),
    country_code CHAR(2),

    -- Stats
    total_events INTEGER DEFAULT 0,
    total_bracelets INTEGER DEFAULT 0,
    total_prize_pool BIGINT DEFAULT 0,
    total_entries INTEGER DEFAULT 0,

    -- Media
    logo_url VARCHAR(500),
    banner_url VARCHAR(500),

    -- Status
    status VARCHAR(20) DEFAULT 'upcoming',
    is_featured BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_circuits_year ON circuits(year);
CREATE INDEX idx_circuits_type ON circuits(circuit_type);
CREATE INDEX idx_circuits_status ON circuits(status);
CREATE INDEX idx_circuits_dates ON circuits(start_date, end_date);

-- 1.2 events (이벤트/브래킷)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circuit_id UUID NOT NULL REFERENCES circuits(id) ON DELETE CASCADE,

    -- Event Info
    event_number INTEGER NOT NULL,
    name VARCHAR(500) NOT NULL,
    short_name VARCHAR(100),
    slug VARCHAR(150) UNIQUE NOT NULL,

    -- Game Details
    game_type VARCHAR(50) NOT NULL,
    game_variant VARCHAR(100),
    tournament_type VARCHAR(50) DEFAULT 'freezeout',

    -- Buy-in Structure
    buy_in BIGINT NOT NULL,
    rake BIGINT DEFAULT 0,
    starting_stack INTEGER,

    -- Blind Structure
    blind_levels JSONB,
    level_duration_minutes INTEGER,

    -- Dates & Schedule
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ,
    days_count INTEGER DEFAULT 1,

    -- Results
    total_entries INTEGER DEFAULT 0,
    unique_entries INTEGER DEFAULT 0,
    reentries INTEGER DEFAULT 0,
    prize_pool BIGINT DEFAULT 0,
    places_paid INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'scheduled',
    current_day INTEGER DEFAULT 0,
    remaining_players INTEGER DEFAULT 0,

    -- Bracelet
    is_bracelet_event BOOLEAN DEFAULT TRUE,
    bracelet_number INTEGER,

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

    UNIQUE(circuit_id, event_number)
);

CREATE INDEX idx_events_circuit ON events(circuit_id);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_game_type ON events(game_type);
CREATE INDEX idx_events_dates ON events(start_date, end_date);
CREATE INDEX idx_events_buy_in ON events(buy_in);
CREATE INDEX idx_events_featured ON events(is_featured) WHERE is_featured = TRUE;

-- 1.3 tournaments (토너먼트 세션/데이)
CREATE TABLE tournaments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,

    -- Session Info
    day_number INTEGER NOT NULL,
    flight_name VARCHAR(50),
    session_type VARCHAR(50) DEFAULT 'day',

    -- Schedule
    scheduled_start TIMESTAMPTZ NOT NULL,
    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,

    -- Status
    status VARCHAR(20) DEFAULT 'scheduled',
    current_level INTEGER DEFAULT 0,
    current_blind_small BIGINT,
    current_blind_big BIGINT,
    current_ante BIGINT,

    -- Stats
    starting_players INTEGER DEFAULT 0,
    remaining_players INTEGER DEFAULT 0,
    total_chips_in_play BIGINT DEFAULT 0,
    average_stack BIGINT DEFAULT 0,

    -- Live Streaming
    is_streaming BOOLEAN DEFAULT FALSE,
    stream_url VARCHAR(500),
    stream_delay_minutes INTEGER DEFAULT 30,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(event_id, day_number, flight_name)
);

CREATE INDEX idx_tournaments_event ON tournaments(event_id);
CREATE INDEX idx_tournaments_status ON tournaments(status);
CREATE INDEX idx_tournaments_streaming ON tournaments(is_streaming) WHERE is_streaming = TRUE;
CREATE INDEX idx_tournaments_schedule ON tournaments(scheduled_start);

-- ============================================================================
-- 2. PLAYER ENTITIES
-- ============================================================================

-- 2.1 players (플레이어)
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    ggpoker_id VARCHAR(100) UNIQUE,
    wsop_id VARCHAR(100) UNIQUE,
    hendon_mob_id INTEGER UNIQUE,

    -- Basic Info
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    nickname VARCHAR(100),

    -- Demographics
    country_code CHAR(2),
    country_name VARCHAR(100),
    city VARCHAR(100),
    birth_date DATE,

    -- Profile
    avatar_url VARCHAR(500),
    banner_url VARCHAR(500),
    bio TEXT,

    -- Career Stats
    total_earnings BIGINT DEFAULT 0,
    wsop_earnings BIGINT DEFAULT 0,
    wsop_bracelets INTEGER DEFAULT 0,
    wsop_rings INTEGER DEFAULT 0,
    wsop_final_tables INTEGER DEFAULT 0,
    wsop_cashes INTEGER DEFAULT 0,
    wsop_best_finish INTEGER,

    -- Rankings
    all_time_rank INTEGER,
    current_year_rank INTEGER,
    poy_points INTEGER DEFAULT 0,

    -- GGPoker HUD Stats
    hud_vpip DECIMAL(5,2),
    hud_pfr DECIMAL(5,2),
    hud_3bet DECIMAL(5,2),
    hud_af DECIMAL(5,2),
    hud_flop_cbet DECIMAL(5,2),
    hud_fold_to_cbet DECIMAL(5,2),
    hud_wtsd DECIMAL(5,2),
    hud_won_at_sd DECIMAL(5,2),
    hud_hands_played INTEGER DEFAULT 0,
    hud_last_updated TIMESTAMPTZ,

    -- Social Links
    twitter_handle VARCHAR(100),
    instagram_handle VARCHAR(100),
    youtube_channel VARCHAR(200),

    -- Status
    is_verified BOOLEAN DEFAULT FALSE,
    is_pro BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_players_name ON players(last_name, first_name);
CREATE INDEX idx_players_country ON players(country_code);
CREATE INDEX idx_players_earnings ON players(total_earnings DESC);
CREATE INDEX idx_players_bracelets ON players(wsop_bracelets DESC);
CREATE INDEX idx_players_ggpoker ON players(ggpoker_id) WHERE ggpoker_id IS NOT NULL;
CREATE INDEX idx_players_search ON players USING gin(
    to_tsvector('english', coalesce(first_name, '') || ' ' || coalesce(last_name, '') || ' ' || coalesce(nickname, ''))
);

-- 2.2 placements (순위/결과)
CREATE TABLE placements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    tournament_id UUID REFERENCES tournaments(id),

    -- Finish
    finish_position INTEGER NOT NULL,
    prize_amount BIGINT NOT NULL,

    -- Points
    poy_points INTEGER DEFAULT 0,
    circuit_points INTEGER DEFAULT 0,

    -- Bracelet/Ring
    won_bracelet BOOLEAN DEFAULT FALSE,
    won_ring BOOLEAN DEFAULT FALSE,

    -- Final Table Stats
    final_table_chips BIGINT,
    heads_up_chips BIGINT,

    -- Timestamps
    eliminated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(event_id, player_id)
);

CREATE INDEX idx_placements_event ON placements(event_id);
CREATE INDEX idx_placements_player ON placements(player_id);
CREATE INDEX idx_placements_finish ON placements(finish_position);
CREATE INDEX idx_placements_prize ON placements(prize_amount DESC);
CREATE INDEX idx_placements_bracelet ON placements(won_bracelet) WHERE won_bracelet = TRUE;

-- 2.3 player_stats (플레이어 통계 스냅샷)
CREATE TABLE player_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    tournament_id UUID REFERENCES tournaments(id) ON DELETE CASCADE,

    -- Scope
    stat_type VARCHAR(20) NOT NULL,

    -- Basic Stats
    hands_played INTEGER DEFAULT 0,
    hands_won INTEGER DEFAULT 0,
    pots_won INTEGER DEFAULT 0,

    -- Preflop Stats
    vpip DECIMAL(5,2),
    pfr DECIMAL(5,2),
    three_bet DECIMAL(5,2),
    four_bet DECIMAL(5,2),
    fold_to_3bet DECIMAL(5,2),

    -- Postflop Stats
    cbet DECIMAL(5,2),
    fold_to_cbet DECIMAL(5,2),
    check_raise DECIMAL(5,2),

    -- Aggression
    aggression_factor DECIMAL(5,2),
    aggression_frequency DECIMAL(5,2),

    -- Win Rates
    win_rate_bb_100 DECIMAL(8,4),
    roi DECIMAL(8,4),
    itm_percent DECIMAL(5,2),

    -- Chips
    chips_won BIGINT DEFAULT 0,
    chips_lost BIGINT DEFAULT 0,
    net_chips BIGINT DEFAULT 0,
    biggest_pot_won BIGINT DEFAULT 0,

    -- Bluffs
    bluff_attempts INTEGER DEFAULT 0,
    bluff_success INTEGER DEFAULT 0,
    bluff_success_rate DECIMAL(5,2),

    -- Position Stats
    position_stats JSONB,

    -- Timestamps
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_player_stats_player ON player_stats(player_id);
CREATE INDEX idx_player_stats_event ON player_stats(event_id);
CREATE INDEX idx_player_stats_type ON player_stats(stat_type);

-- ============================================================================
-- 3. HAND HISTORY ENTITIES
-- ============================================================================

-- 3.1 tables (테이블)
CREATE TABLE tables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,

    -- Table Info
    table_number INTEGER NOT NULL,
    table_name VARCHAR(100),

    -- Type
    table_type VARCHAR(50) DEFAULT 'standard',
    is_feature_table BOOLEAN DEFAULT FALSE,
    has_player_cams BOOLEAN DEFAULT FALSE,

    -- Current State
    status VARCHAR(20) DEFAULT 'active',
    current_hand_number INTEGER DEFAULT 0,
    seats_occupied INTEGER DEFAULT 0,

    -- Streaming
    stream_url VARCHAR(500),
    player_cam_urls JSONB,

    -- Tournament Strip Info
    current_pot BIGINT DEFAULT 0,
    current_small_blind BIGINT,
    current_big_blind BIGINT,

    -- Timestamps
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(tournament_id, table_number)
);

CREATE INDEX idx_tables_tournament ON tables(tournament_id);
CREATE INDEX idx_tables_feature ON tables(is_feature_table) WHERE is_feature_table = TRUE;
CREATE INDEX idx_tables_status ON tables(status);

-- 3.2 hands (핸드)
CREATE TABLE hands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_id UUID NOT NULL REFERENCES tables(id) ON DELETE CASCADE,
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,

    -- Hand Info
    hand_number INTEGER NOT NULL,
    hand_id VARCHAR(100) UNIQUE,

    -- Timing
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    video_timestamp_start INTEGER,
    video_timestamp_end INTEGER,

    -- Blinds/Stakes
    small_blind BIGINT NOT NULL,
    big_blind BIGINT NOT NULL,
    ante BIGINT DEFAULT 0,

    -- Board
    flop_card_1 CHAR(2),
    flop_card_2 CHAR(2),
    flop_card_3 CHAR(2),
    turn_card CHAR(2),
    river_card CHAR(2),
    board VARCHAR(20),

    -- Pot
    pot_preflop BIGINT DEFAULT 0,
    pot_flop BIGINT DEFAULT 0,
    pot_turn BIGINT DEFAULT 0,
    pot_river BIGINT DEFAULT 0,
    pot_total BIGINT NOT NULL,
    rake BIGINT DEFAULT 0,

    -- Result
    winner_player_id UUID REFERENCES players(id),
    winning_hand VARCHAR(50),
    winning_cards VARCHAR(10),
    went_to_showdown BOOLEAN DEFAULT FALSE,

    -- Hand Summary
    hand_summary JSONB,

    -- Key Hand Flag
    is_key_hand BOOLEAN DEFAULT FALSE,
    key_hand_reason VARCHAR(200),
    key_hand_tags TEXT[],

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(table_id, hand_number)
);

CREATE INDEX idx_hands_table ON hands(table_id);
CREATE INDEX idx_hands_tournament ON hands(tournament_id);
CREATE INDEX idx_hands_winner ON hands(winner_player_id);
CREATE INDEX idx_hands_key ON hands(is_key_hand) WHERE is_key_hand = TRUE;
CREATE INDEX idx_hands_timestamp ON hands(started_at);
CREATE INDEX idx_hands_pot ON hands(pot_total DESC);

-- 3.3 hand_players (핸드 참여자)
CREATE TABLE hand_players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hand_id UUID NOT NULL REFERENCES hands(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,

    -- Position
    seat_number INTEGER NOT NULL,
    position VARCHAR(10) NOT NULL,
    is_button BOOLEAN DEFAULT FALSE,
    is_small_blind BOOLEAN DEFAULT FALSE,
    is_big_blind BOOLEAN DEFAULT FALSE,

    -- Stack
    stack_start BIGINT NOT NULL,
    stack_end BIGINT NOT NULL,

    -- Hole Cards
    hole_card_1 CHAR(2),
    hole_card_2 CHAR(2),
    cards_shown BOOLEAN DEFAULT FALSE,

    -- Result
    is_winner BOOLEAN DEFAULT FALSE,
    amount_won BIGINT DEFAULT 0,
    amount_invested BIGINT DEFAULT 0,

    -- Action Summary
    folded_street VARCHAR(20),
    went_to_showdown BOOLEAN DEFAULT FALSE,
    was_all_in BOOLEAN DEFAULT FALSE,

    -- PlayerCAM
    player_cam_clip_url VARCHAR(500),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(hand_id, player_id)
);

CREATE INDEX idx_hand_players_hand ON hand_players(hand_id);
CREATE INDEX idx_hand_players_player ON hand_players(player_id);
CREATE INDEX idx_hand_players_position ON hand_players(position);
CREATE INDEX idx_hand_players_winner ON hand_players(is_winner) WHERE is_winner = TRUE;

-- 3.4 hand_actions (핸드 액션)
CREATE TABLE hand_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hand_id UUID NOT NULL REFERENCES hands(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,

    -- Action Order
    action_order INTEGER NOT NULL,
    street VARCHAR(20) NOT NULL,

    -- Action Details
    action_type VARCHAR(20) NOT NULL,
    amount BIGINT DEFAULT 0,
    raise_to BIGINT,
    is_all_in BOOLEAN DEFAULT FALSE,

    -- Pot State
    pot_after_action BIGINT NOT NULL,

    -- Video Sync
    video_timestamp INTEGER,

    -- Context
    facing_bet BIGINT DEFAULT 0,

    -- Timestamps
    action_time TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_hand_actions_hand ON hand_actions(hand_id);
CREATE INDEX idx_hand_actions_player ON hand_actions(player_id);
CREATE INDEX idx_hand_actions_street ON hand_actions(street);
CREATE INDEX idx_hand_actions_order ON hand_actions(hand_id, action_order);
CREATE INDEX idx_hand_actions_type ON hand_actions(action_type);

-- ============================================================================
-- 4. CONTENT & STREAMING ENTITIES
-- ============================================================================

-- 4.1 content (콘텐츠)
CREATE TABLE content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    tournament_id UUID REFERENCES tournaments(id) ON DELETE SET NULL,

    -- Content Info
    title VARCHAR(500) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,

    -- Type
    content_type VARCHAR(50) NOT NULL,
    category VARCHAR(100),

    -- Duration
    duration_seconds INTEGER,

    -- Thumbnail & Media
    thumbnail_url VARCHAR(500),
    poster_url VARCHAR(500),
    preview_url VARCHAR(500),

    -- Streaming
    is_live BOOLEAN DEFAULT FALSE,
    live_started_at TIMESTAMPTZ,
    live_ended_at TIMESTAMPTZ,

    -- Timeshift
    timeshift_enabled BOOLEAN DEFAULT TRUE,
    timeshift_window_hours INTEGER DEFAULT 24,

    -- Access
    subscription_tier VARCHAR(20) DEFAULT 'plus',
    is_advanced_mode BOOLEAN DEFAULT FALSE,

    -- Metadata for Search
    year INTEGER,
    player_names TEXT[],
    game_types TEXT[],
    tags TEXT[],

    -- Quick VOD Chapters
    chapters JSONB,

    -- Stats
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'draft',
    published_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_content_event ON content(event_id);
CREATE INDEX idx_content_type ON content(content_type);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_live ON content(is_live) WHERE is_live = TRUE;
CREATE INDEX idx_content_tier ON content(subscription_tier);
CREATE INDEX idx_content_year ON content(year);
CREATE INDEX idx_content_published ON content(published_at DESC);
CREATE INDEX idx_content_search ON content USING gin(
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || array_to_string(player_names, ' ') || ' ' || array_to_string(tags, ' '))
);

-- 4.2 content_streams (스트림 URL)
CREATE TABLE content_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,

    -- Stream Info
    stream_type VARCHAR(50) NOT NULL,
    quality VARCHAR(20) NOT NULL,

    -- URLs
    stream_url VARCHAR(1000) NOT NULL,
    backup_url VARCHAR(1000),

    -- DRM
    drm_type VARCHAR(50),
    drm_license_url VARCHAR(500),

    -- Bitrate
    video_bitrate INTEGER,
    audio_bitrate INTEGER,

    -- Multi-view Streams
    is_pgm BOOLEAN DEFAULT FALSE,
    is_feature_table BOOLEAN DEFAULT FALSE,
    is_player_cam BOOLEAN DEFAULT FALSE,
    table_id UUID REFERENCES tables(id),
    player_id UUID REFERENCES players(id),

    -- Audio Options
    audio_language VARCHAR(10) DEFAULT 'en',
    commentary_type VARCHAR(50),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_content_streams_content ON content_streams(content_id);
CREATE INDEX idx_content_streams_type ON content_streams(stream_type);
CREATE INDEX idx_content_streams_quality ON content_streams(quality);
CREATE INDEX idx_content_streams_pgm ON content_streams(is_pgm) WHERE is_pgm = TRUE;

-- 4.3 key_hands (주요 핸드)
CREATE TABLE key_hands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    hand_id UUID REFERENCES hands(id) ON DELETE SET NULL,

    -- Key Hand Info
    title VARCHAR(200) NOT NULL,
    description TEXT,

    -- Video Position
    video_timestamp_start INTEGER NOT NULL,
    video_timestamp_end INTEGER,

    -- Hand Context
    hand_number INTEGER,
    blinds_level VARCHAR(50),
    pot_size BIGINT,

    -- Thumbnail
    thumbnail_url VARCHAR(500),

    -- Players Involved
    player_ids UUID[],
    primary_player_id UUID REFERENCES players(id),

    -- Tags for filtering
    tags TEXT[],

    -- Order
    display_order INTEGER DEFAULT 0,

    -- Status
    is_ai_generated BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_key_hands_content ON key_hands(content_id);
CREATE INDEX idx_key_hands_hand ON key_hands(hand_id);
CREATE INDEX idx_key_hands_player ON key_hands(primary_player_id);
CREATE INDEX idx_key_hands_timestamp ON key_hands(video_timestamp_start);
CREATE INDEX idx_key_hands_order ON key_hands(content_id, display_order);

-- 4.4 subtitles (자막)
CREATE TABLE subtitles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,

    -- Language
    language_code VARCHAR(10) NOT NULL,
    language_name VARCHAR(50) NOT NULL,

    -- Subtitle Info
    subtitle_type VARCHAR(20) DEFAULT 'srt',
    subtitle_url VARCHAR(500) NOT NULL,

    -- Status
    is_default BOOLEAN DEFAULT FALSE,
    is_auto_generated BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(content_id, language_code)
);

CREATE INDEX idx_subtitles_content ON subtitles(content_id);
CREATE INDEX idx_subtitles_language ON subtitles(language_code);

-- ============================================================================
-- 5. USER & SUBSCRIPTION ENTITIES
-- ============================================================================

-- 5.1 users (사용자)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- GGPass SSO
    ggpass_id VARCHAR(100) UNIQUE NOT NULL,
    ggpoker_id VARCHAR(100),

    -- Basic Info
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),

    -- Location
    country_code CHAR(2),
    timezone VARCHAR(50),
    preferred_language VARCHAR(10) DEFAULT 'en',

    -- Subscription
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_status VARCHAR(20) DEFAULT 'active',
    subscription_started_at TIMESTAMPTZ,
    subscription_expires_at TIMESTAMPTZ,

    -- Preferences
    preferences JSONB DEFAULT '{}',

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

CREATE INDEX idx_users_ggpass ON users(ggpass_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_tier);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;

-- 5.2 subscriptions (구독 이력)
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Plan
    plan_type VARCHAR(20) NOT NULL,
    plan_name VARCHAR(100),
    price_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Billing Period
    billing_period VARCHAR(20) DEFAULT 'monthly',
    started_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    cancelled_at TIMESTAMPTZ,

    -- GGPass Billing
    ggpass_transaction_id VARCHAR(100),

    -- Promo
    promo_code VARCHAR(50),
    promo_type VARCHAR(50),
    ggpoker_chips_granted INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'active',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_plan ON subscriptions(plan_type);
CREATE INDEX idx_subscriptions_dates ON subscriptions(started_at, expires_at);

-- 5.3 watch_history (시청 기록)
CREATE TABLE watch_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,

    -- Progress
    watch_progress_seconds INTEGER DEFAULT 0,
    watch_progress_percent DECIMAL(5,2) DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,

    -- Session Info
    device_type VARCHAR(50),
    quality_watched VARCHAR(20),

    -- Advanced Mode Usage
    used_multiview BOOLEAN DEFAULT FALSE,
    used_statsview BOOLEAN DEFAULT FALSE,
    used_key_hands BOOLEAN DEFAULT FALSE,
    view_mode_used VARCHAR(50),

    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_watched_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_watch_history_user ON watch_history(user_id);
CREATE INDEX idx_watch_history_content ON watch_history(content_id);
CREATE INDEX idx_watch_history_last ON watch_history(last_watched_at DESC);
CREATE INDEX idx_watch_history_user_content ON watch_history(user_id, content_id);

-- ============================================================================
-- 6. CIRCUIT POINTS & LEADERBOARD
-- ============================================================================

-- 6.1 circuit_points (서킷 포인트)
CREATE TABLE circuit_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    circuit_id UUID NOT NULL REFERENCES circuits(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    placement_id UUID REFERENCES placements(id) ON DELETE SET NULL,

    -- Points
    points INTEGER NOT NULL,
    points_type VARCHAR(50) NOT NULL,

    -- Rank at time of earning
    rank_at_time INTEGER,

    -- Context
    reason VARCHAR(200),

    -- Timestamps
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_circuit_points_player ON circuit_points(player_id);
CREATE INDEX idx_circuit_points_circuit ON circuit_points(circuit_id);
CREATE INDEX idx_circuit_points_type ON circuit_points(points_type);
CREATE INDEX idx_circuit_points_earned ON circuit_points(earned_at DESC);

-- 6.2 leaderboards (리더보드)
CREATE TABLE leaderboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Leaderboard Type
    leaderboard_type VARCHAR(50) NOT NULL,
    year INTEGER,
    circuit_id UUID REFERENCES circuits(id),

    -- Snapshot
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Rankings Data
    rankings JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_leaderboards_type ON leaderboards(leaderboard_type);
CREATE INDEX idx_leaderboards_year ON leaderboards(year);
CREATE INDEX idx_leaderboards_date ON leaderboards(snapshot_date DESC);

-- ============================================================================
-- 7. TRIGGERS FOR updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_circuits_updated_at BEFORE UPDATE ON circuits FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tournaments_updated_at BEFORE UPDATE ON tournaments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_players_updated_at BEFORE UPDATE ON players FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_placements_updated_at BEFORE UPDATE ON placements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tables_updated_at BEFORE UPDATE ON tables FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_hands_updated_at BEFORE UPDATE ON hands FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_updated_at BEFORE UPDATE ON content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_streams_updated_at BEFORE UPDATE ON content_streams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_key_hands_updated_at BEFORE UPDATE ON key_hands FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subtitles_updated_at BEFORE UPDATE ON subtitles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
