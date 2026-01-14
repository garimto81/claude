-- ============================================================================
-- GFX JSON 정규화 테이블 마이그레이션
-- Version: 1.0.0
-- Date: 2024-01-14
-- Project: PokerGFX JSON to Supabase Normalization
-- ============================================================================

-- ============================================================================
-- 1. gfx_players (플레이어 마스터)
-- ============================================================================
CREATE TABLE IF NOT EXISTS gfx_players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 플레이어 식별 (name + long_name 해시로 중복 방지)
    player_hash TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    long_name TEXT,

    -- 타임스탬프
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    total_hands INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_gfx_players_hash ON gfx_players(player_hash);
CREATE INDEX IF NOT EXISTS idx_gfx_players_name ON gfx_players(name);

-- ============================================================================
-- 2. gfx_sessions (세션/게임 단위)
-- ============================================================================
CREATE TABLE IF NOT EXISTS gfx_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- PokerGFX 세션 식별자 (Windows FileTime 기반 int64)
    session_id BIGINT NOT NULL UNIQUE,

    -- PC/파일 정보
    gfx_pc_id TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    file_name TEXT NOT NULL,

    -- 메타데이터
    event_title TEXT,
    software_version TEXT,
    table_type TEXT,
    created_datetime_utc TIMESTAMPTZ,

    -- Payouts (배열 → JSONB)
    payouts JSONB,

    -- 동기화 정보
    sync_source TEXT DEFAULT 'nas_central',
    hand_count INTEGER DEFAULT 0,

    -- 원본 JSON (선택적 보존)
    raw_json JSONB,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 복합 유니크 (PC + 파일 해시)
    CONSTRAINT uq_gfx_sessions_pc_file UNIQUE (gfx_pc_id, file_hash)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_gfx_sessions_session_id ON gfx_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_gfx_sessions_pc ON gfx_sessions(gfx_pc_id);
CREATE INDEX IF NOT EXISTS idx_gfx_sessions_created ON gfx_sessions(created_datetime_utc DESC);

-- ============================================================================
-- 3. gfx_hands (핸드 단위)
-- ============================================================================
CREATE TABLE IF NOT EXISTS gfx_hands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 세션 참조
    session_id BIGINT NOT NULL,
    hand_num INTEGER NOT NULL,

    -- 게임 정보
    game_variant TEXT DEFAULT 'HOLDEM',
    game_class TEXT DEFAULT 'FLOP',
    bet_structure TEXT DEFAULT 'NOLIMIT',

    -- 시간 정보
    duration_seconds FLOAT DEFAULT 0.0,
    start_datetime_utc TIMESTAMPTZ,
    recording_offset_start FLOAT,

    -- 블라인드 정보
    small_blind DECIMAL(18,2),
    big_blind DECIMAL(18,2),
    ante DECIMAL(18,2),

    -- 게임 설정
    num_boards INTEGER DEFAULT 1,
    run_it_num_times INTEGER DEFAULT 1,

    -- 집계
    player_count INTEGER DEFAULT 0,
    event_count INTEGER DEFAULT 0,
    pot_size DECIMAL(18,2),

    -- 보드 카드
    board_cards TEXT[],

    -- 승자
    winner_name TEXT,
    description TEXT,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 복합 유니크
    CONSTRAINT uq_gfx_hands_session_num UNIQUE (session_id, hand_num)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_gfx_hands_session ON gfx_hands(session_id);
CREATE INDEX IF NOT EXISTS idx_gfx_hands_start ON gfx_hands(start_datetime_utc DESC);
CREATE INDEX IF NOT EXISTS idx_gfx_hands_variant ON gfx_hands(game_variant);

-- ============================================================================
-- 4. gfx_hand_players (핸드별 플레이어)
-- ============================================================================
CREATE TABLE IF NOT EXISTS gfx_hand_players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 참조
    hand_id UUID NOT NULL REFERENCES gfx_hands(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES gfx_players(id) ON DELETE CASCADE,

    -- 시트 정보
    player_num INTEGER NOT NULL,

    -- 홀 카드
    hole_cards TEXT[],

    -- 스택 정보
    start_stack_amt DECIMAL(18,2),
    end_stack_amt DECIMAL(18,2),
    cumulative_winnings_amt DECIMAL(18,2),

    -- 플레이어 통계
    vpip_pct FLOAT,
    pfr_pct FLOAT,
    aggression_pct FLOAT,

    -- 상태
    sitting_out BOOLEAN DEFAULT FALSE,
    is_winner BOOLEAN DEFAULT FALSE,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 복합 유니크
    CONSTRAINT uq_gfx_hand_players_seat UNIQUE (hand_id, player_num)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_gfx_hand_players_hand ON gfx_hand_players(hand_id);
CREATE INDEX IF NOT EXISTS idx_gfx_hand_players_player ON gfx_hand_players(player_id);

-- ============================================================================
-- 5. gfx_events (액션/이벤트)
-- ============================================================================
CREATE TABLE IF NOT EXISTS gfx_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 핸드 참조
    hand_id UUID NOT NULL REFERENCES gfx_hands(id) ON DELETE CASCADE,

    -- 이벤트 정보
    event_order INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    player_num INTEGER,

    -- 베팅/팟 정보
    amount DECIMAL(18,2),
    pot DECIMAL(18,2),

    -- 보드 카드 (BOARD_CARD 이벤트)
    cards TEXT[],

    -- 추가 데이터
    extra_data JSONB,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- 복합 유니크
    CONSTRAINT uq_gfx_events_order UNIQUE (hand_id, event_order)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_gfx_events_hand ON gfx_events(hand_id);
CREATE INDEX IF NOT EXISTS idx_gfx_events_type ON gfx_events(event_type);
CREATE INDEX IF NOT EXISTS idx_gfx_events_order ON gfx_events(hand_id, event_order);

-- ============================================================================
-- 6. sync_log (동기화 로그)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sync_log (
    id BIGSERIAL PRIMARY KEY,

    -- 대상 정보
    gfx_pc_id TEXT NOT NULL,
    session_id BIGINT,
    file_path TEXT,
    file_hash TEXT,

    -- 동기화 결과
    status TEXT NOT NULL,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,

    -- 오류 정보
    error_message TEXT,
    error_details JSONB,

    -- 성능 측정
    duration_ms INTEGER,

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_sync_log_pc ON sync_log(gfx_pc_id);
CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log(status);
CREATE INDEX IF NOT EXISTS idx_sync_log_session ON sync_log(session_id);
CREATE INDEX IF NOT EXISTS idx_sync_log_created ON sync_log(created_at DESC);

-- ============================================================================
-- 7. updated_at 자동 갱신 트리거
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 적용
DROP TRIGGER IF EXISTS update_gfx_players_updated_at ON gfx_players;
CREATE TRIGGER update_gfx_players_updated_at
    BEFORE UPDATE ON gfx_players
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_gfx_sessions_updated_at ON gfx_sessions;
CREATE TRIGGER update_gfx_sessions_updated_at
    BEFORE UPDATE ON gfx_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_gfx_hands_updated_at ON gfx_hands;
CREATE TRIGGER update_gfx_hands_updated_at
    BEFORE UPDATE ON gfx_hands
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 완료 메시지
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'GFX JSON 정규화 테이블 마이그레이션 완료';
    RAISE NOTICE '생성된 테이블: gfx_players, gfx_sessions, gfx_hands, gfx_hand_players, gfx_events, sync_log';
END $$;
