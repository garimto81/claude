-- WSOPTV OTT Database Schema - Additional Tables & Constraints
-- Version: 1.0.1
-- Created: 2026-01-19
-- Reference: ADR-0002-database-schema-design.md (검증 결과 반영)

-- ============================================================================
-- ADDITIONAL TABLES (ERD 정합성)
-- ============================================================================

-- event_schedule (이벤트 스케줄)
-- FR-2 (VOD 챕터/구간 탐색), Tournament Strip 지원
CREATE TABLE IF NOT EXISTS event_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,

    -- Schedule Info
    session_name VARCHAR(100) NOT NULL,            -- "Day 1A", "Day 1B", "Day 2", "Final Table"
    session_type VARCHAR(50),                      -- 'start', 'break', 'dinner', 'resume', 'end'

    -- Timing
    scheduled_time TIMESTAMPTZ NOT NULL,
    actual_time TIMESTAMPTZ,
    duration_minutes INTEGER,

    -- Description
    description TEXT,
    notes TEXT,

    -- Status
    status VARCHAR(20) DEFAULT 'scheduled',        -- 'scheduled', 'in_progress', 'completed', 'cancelled'

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_event_schedule_event ON event_schedule(event_id);
CREATE INDEX idx_event_schedule_time ON event_schedule(scheduled_time);
CREATE INDEX idx_event_schedule_status ON event_schedule(status);

CREATE TRIGGER update_event_schedule_updated_at
    BEFORE UPDATE ON event_schedule
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE event_schedule IS '이벤트 세션 스케줄 (Day 1A, Break 등)';

-- earnings (수입 기록)
-- wsop.com 데이터 동기화용
CREATE TABLE IF NOT EXISTS earnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,

    -- Event Context
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    placement_id UUID REFERENCES placements(id) ON DELETE SET NULL,

    -- Amount
    amount BIGINT NOT NULL,                        -- Amount in cents
    currency VARCHAR(3) DEFAULT 'USD',

    -- Type
    earning_type VARCHAR(50) NOT NULL,             -- 'tournament', 'bounty', 'bonus', 'last_longer'

    -- Source
    source VARCHAR(50),                            -- 'wsop', 'circuit', 'online'

    -- Context
    description VARCHAR(500),

    -- Timestamps
    earned_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_earnings_player ON earnings(player_id);
CREATE INDEX idx_earnings_event ON earnings(event_id);
CREATE INDEX idx_earnings_type ON earnings(earning_type);
CREATE INDEX idx_earnings_date ON earnings(earned_at DESC);
CREATE INDEX idx_earnings_amount ON earnings(amount DESC);

COMMENT ON TABLE earnings IS '플레이어 수입 기록 (wsop.com 연동)';

-- ============================================================================
-- CHECK CONSTRAINTS (데이터 무결성)
-- ============================================================================

-- circuits
ALTER TABLE circuits ADD CONSTRAINT chk_circuits_year CHECK (year >= 1970 AND year <= 2100);
ALTER TABLE circuits ADD CONSTRAINT chk_circuits_status CHECK (status IN ('upcoming', 'live', 'completed'));
ALTER TABLE circuits ADD CONSTRAINT chk_circuits_dates CHECK (end_date >= start_date);
ALTER TABLE circuits ADD CONSTRAINT chk_circuits_type CHECK (circuit_type IN (
    'wsop', 'wsop_paradise', 'wsop_europe', 'wsop_asia', 'wsop_online', 'wsop_circuit', 'super_circuit', 'bracelets'
));

-- events
ALTER TABLE events ADD CONSTRAINT chk_events_buy_in CHECK (buy_in >= 0);
ALTER TABLE events ADD CONSTRAINT chk_events_rake CHECK (rake >= 0);
ALTER TABLE events ADD CONSTRAINT chk_events_entries CHECK (total_entries >= 0);
ALTER TABLE events ADD CONSTRAINT chk_events_prize_pool CHECK (prize_pool >= 0);
ALTER TABLE events ADD CONSTRAINT chk_events_status CHECK (status IN (
    'scheduled', 'registration', 'running', 'final_table', 'completed', 'cancelled'
));
ALTER TABLE events ADD CONSTRAINT chk_events_game_type CHECK (game_type IN (
    'no_limit_holdem', 'pot_limit_omaha', 'pot_limit_omaha_hilo', 'limit_holdem',
    'limit_omaha_hilo', 'razz', 'stud', 'stud_hilo', 'mixed', 'horse', 'dealer_choice', 'other'
));

-- tournaments
ALTER TABLE tournaments ADD CONSTRAINT chk_tournaments_day CHECK (day_number >= 0);
ALTER TABLE tournaments ADD CONSTRAINT chk_tournaments_status CHECK (status IN (
    'scheduled', 'running', 'on_break', 'completed'
));
ALTER TABLE tournaments ADD CONSTRAINT chk_tournaments_delay CHECK (stream_delay_minutes >= 0 AND stream_delay_minutes <= 120);

-- players
ALTER TABLE players ADD CONSTRAINT chk_players_bracelets CHECK (wsop_bracelets >= 0);
ALTER TABLE players ADD CONSTRAINT chk_players_rings CHECK (wsop_rings >= 0);
ALTER TABLE players ADD CONSTRAINT chk_players_earnings CHECK (total_earnings >= 0);
ALTER TABLE players ADD CONSTRAINT chk_players_wsop_earnings CHECK (wsop_earnings >= 0);

-- player_stats
ALTER TABLE player_stats ADD CONSTRAINT chk_player_stats_vpip CHECK (vpip IS NULL OR (vpip >= 0 AND vpip <= 100));
ALTER TABLE player_stats ADD CONSTRAINT chk_player_stats_pfr CHECK (pfr IS NULL OR (pfr >= 0 AND pfr <= 100));
ALTER TABLE player_stats ADD CONSTRAINT chk_player_stats_3bet CHECK (three_bet IS NULL OR (three_bet >= 0 AND three_bet <= 100));
ALTER TABLE player_stats ADD CONSTRAINT chk_player_stats_cbet CHECK (cbet IS NULL OR (cbet >= 0 AND cbet <= 100));
ALTER TABLE player_stats ADD CONSTRAINT chk_player_stats_type CHECK (stat_type IN ('event', 'tournament', 'session', 'all_time'));

-- placements
ALTER TABLE placements ADD CONSTRAINT chk_placements_finish CHECK (finish_position >= 1);
ALTER TABLE placements ADD CONSTRAINT chk_placements_prize CHECK (prize_amount >= 0);

-- hands
ALTER TABLE hands ADD CONSTRAINT chk_hands_blinds CHECK (big_blind >= small_blind);
ALTER TABLE hands ADD CONSTRAINT chk_hands_pot CHECK (pot_total >= 0);

-- hand_players
ALTER TABLE hand_players ADD CONSTRAINT chk_hand_players_seat CHECK (seat_number >= 1 AND seat_number <= 10);
ALTER TABLE hand_players ADD CONSTRAINT chk_hand_players_position CHECK (position IN (
    'BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'MP', 'MP+1', 'MP+2', 'HJ', 'CO'
));

-- hand_actions
ALTER TABLE hand_actions ADD CONSTRAINT chk_hand_actions_street CHECK (street IN (
    'preflop', 'flop', 'turn', 'river'
));
ALTER TABLE hand_actions ADD CONSTRAINT chk_hand_actions_type CHECK (action_type IN (
    'fold', 'check', 'call', 'bet', 'raise', 'all_in', 'post_sb', 'post_bb', 'post_ante'
));

-- content
ALTER TABLE content ADD CONSTRAINT chk_content_type CHECK (content_type IN (
    'live', 'vod', 'quick_vod', 'highlight', 'archive', 'clip'
));
ALTER TABLE content ADD CONSTRAINT chk_content_tier CHECK (subscription_tier IN ('free', 'plus', 'plus_plus'));
ALTER TABLE content ADD CONSTRAINT chk_content_status CHECK (status IN ('draft', 'published', 'archived', 'deleted'));

-- content_streams
ALTER TABLE content_streams ADD CONSTRAINT chk_streams_type CHECK (stream_type IN ('hls', 'dash', 'smooth'));
ALTER TABLE content_streams ADD CONSTRAINT chk_streams_quality CHECK (quality IN (
    '1080p', '720p', '480p', '360p', '240p', 'auto'
));

-- users
ALTER TABLE users ADD CONSTRAINT chk_users_tier CHECK (subscription_tier IN ('free', 'plus', 'plus_plus'));
ALTER TABLE users ADD CONSTRAINT chk_users_status CHECK (subscription_status IN ('active', 'cancelled', 'expired', 'pending'));

-- subscriptions
ALTER TABLE subscriptions ADD CONSTRAINT chk_subscriptions_plan CHECK (plan_type IN ('plus', 'plus_plus'));
ALTER TABLE subscriptions ADD CONSTRAINT chk_subscriptions_period CHECK (billing_period IN ('monthly', 'yearly'));
ALTER TABLE subscriptions ADD CONSTRAINT chk_subscriptions_status CHECK (status IN (
    'active', 'cancelled', 'expired', 'refunded', 'pending'
));
ALTER TABLE subscriptions ADD CONSTRAINT chk_subscriptions_dates CHECK (expires_at >= started_at);

-- watch_history
ALTER TABLE watch_history ADD CONSTRAINT chk_watch_progress CHECK (watch_progress_percent >= 0 AND watch_progress_percent <= 100);
ALTER TABLE watch_history ADD CONSTRAINT chk_watch_device CHECK (device_type IN (
    'web', 'ios', 'android', 'samsung_tv', 'lg_tv', 'roku', 'fire_tv', 'other'
));

-- ============================================================================
-- COMMENTS (문서화)
-- ============================================================================

-- Core Tables
COMMENT ON TABLE circuits IS 'WSOP 대회 시리즈 (WSOP Main, Paradise, Europe, Asia 등)';
COMMENT ON COLUMN circuits.circuit_type IS 'wsop, wsop_paradise, wsop_europe, wsop_asia, wsop_online, wsop_circuit, super_circuit';
COMMENT ON COLUMN circuits.total_prize_pool IS '총 상금 (센트 단위, $1M = 100000000)';

COMMENT ON TABLE events IS '개별 이벤트/브래킷 (Main Event, High Roller 등)';
COMMENT ON COLUMN events.buy_in IS '바이인 금액 (센트 단위, $10,000 = 1000000)';
COMMENT ON COLUMN events.game_type IS 'no_limit_holdem, pot_limit_omaha, mixed 등';

COMMENT ON TABLE tournaments IS '토너먼트 세션/데이 (Day 1A, Final Table 등)';
COMMENT ON COLUMN tournaments.stream_delay_minutes IS '라이브 스트리밍 지연 시간 (기본 30분)';

-- Player Tables
COMMENT ON TABLE players IS '플레이어 정보 (wsop.com + GGPoker 연동)';
COMMENT ON COLUMN players.hud_vpip IS 'Voluntarily Put $ In Pot % (0-100)';
COMMENT ON COLUMN players.hud_pfr IS 'Pre-Flop Raise % (0-100)';
COMMENT ON COLUMN players.hud_af IS 'Aggression Factor';

COMMENT ON TABLE placements IS '토너먼트 순위/결과';
COMMENT ON COLUMN placements.prize_amount IS '상금 (센트 단위)';

COMMENT ON TABLE player_stats IS '플레이어 통계 스냅샷 (이벤트/토너먼트/세션별)';
COMMENT ON COLUMN player_stats.position_stats IS 'JSONB: {"UTG": {"hands": 10, "won": 2}, ...}';

-- Hand History Tables
COMMENT ON TABLE tables IS '테이블 정보 (피처 테이블, PlayerCAM 지원 여부)';
COMMENT ON COLUMN tables.player_cam_urls IS 'JSONB: {"seat_1": "url", "seat_2": "url", ...}';

COMMENT ON TABLE hands IS '핸드 기록';
COMMENT ON COLUMN hands.board IS '커뮤니티 카드 (예: "Ah Ks 7d 2c Tc")';
COMMENT ON COLUMN hands.is_key_hand IS 'Key Hands 모달에 표시 여부';

COMMENT ON TABLE hand_players IS '핸드별 참여 플레이어';
COMMENT ON COLUMN hand_players.hole_card_1 IS '홀카드 1 (예: "Ah")';

COMMENT ON TABLE hand_actions IS '핸드 액션 로그 (Hand-by-Hand Log)';
COMMENT ON COLUMN hand_actions.street IS 'preflop, flop, turn, river';

-- Content Tables
COMMENT ON TABLE content IS 'VOD, 라이브, Quick VOD 콘텐츠';
COMMENT ON COLUMN content.subscription_tier IS 'free, plus ($10), plus_plus ($50)';
COMMENT ON COLUMN content.chapters IS 'JSONB: [{"title": "Final Table Start", "timestamp": 0}, ...]';

COMMENT ON TABLE content_streams IS 'HLS/DASH 스트림 URL (DRM 포함)';
COMMENT ON COLUMN content_streams.drm_type IS 'widevine, fairplay, playready';

COMMENT ON TABLE key_hands IS 'Key Hands 모달용 (PRD-0006)';
COMMENT ON COLUMN key_hands.tags IS '태그 배열 (bluff, big_pot, elimination 등)';

COMMENT ON TABLE subtitles IS '20개국 자막 (PRD-0002 FR-5)';

-- User Tables
COMMENT ON TABLE users IS 'GGPass SSO 연동 사용자';
COMMENT ON COLUMN users.ggpass_id IS 'GGPass SSO ID (필수)';
COMMENT ON COLUMN users.preferences IS 'JSONB: UI 설정, 기본 화질 등';

COMMENT ON TABLE subscriptions IS '구독 이력';
COMMENT ON COLUMN subscriptions.ggpoker_chips_granted IS '프로모션 연동 칩 지급량';

COMMENT ON TABLE watch_history IS '시청 기록 (이어보기, 추천용)';
COMMENT ON COLUMN watch_history.view_mode_used IS 'standard, multiview, statsview, combined';

-- Leaderboard Tables
COMMENT ON TABLE circuit_points IS '서킷 포인트 (POY, Circuit 등)';
COMMENT ON TABLE leaderboards IS '리더보드 스냅샷 (all_time_earnings, bracelets 등)';
COMMENT ON COLUMN leaderboards.rankings IS 'JSONB: [{"rank": 1, "player_id": "uuid", "value": 1000000}, ...]';

-- ============================================================================
-- RLS POLICIES (Supabase 환경용 - 선택적 적용)
-- ============================================================================

-- 사용자 테이블 RLS
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY users_select_own ON users FOR SELECT USING (auth.uid()::text = ggpass_id);
-- CREATE POLICY users_update_own ON users FOR UPDATE USING (auth.uid()::text = ggpass_id);

-- 시청 기록 RLS
-- ALTER TABLE watch_history ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY watch_history_select_own ON watch_history FOR SELECT USING (auth.uid()::text = (SELECT ggpass_id FROM users WHERE id = user_id));
-- CREATE POLICY watch_history_insert_own ON watch_history FOR INSERT WITH CHECK (auth.uid()::text = (SELECT ggpass_id FROM users WHERE id = user_id));

-- 구독 테이블 RLS
-- ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY subscriptions_select_own ON subscriptions FOR SELECT USING (auth.uid()::text = (SELECT ggpass_id FROM users WHERE id = user_id));

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
