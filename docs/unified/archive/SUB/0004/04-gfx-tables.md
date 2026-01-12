# PRD-0004 Part 4: GFX Tables (New Tables)

**Part 4 of 7** | [← Database Schema](./03-database-schema.md) | [Caption Mapping →](./05-caption-mapping.md)

> Index: [PRD-0004](../0004-prd-caption-database-schema.md)

---

## 4.2 New Tables (PRD-0004)

### 4.2.1 gfx_sessions (신규) - pokerGFX 세션

```sql
CREATE TABLE gfx_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID REFERENCES tournaments(id) ON DELETE SET NULL,
    feature_table_id UUID REFERENCES feature_tables(id) ON DELETE SET NULL,

    -- GFX 원본 데이터
    gfx_id BIGINT UNIQUE NOT NULL,  -- pokerGFX ID (638961999170907267)
    event_title VARCHAR(255),
    table_type VARCHAR(50) DEFAULT 'FEATURE_TABLE',  -- 'FEATURE_TABLE', 'OUTER_TABLE'
    software_version VARCHAR(50),  -- 'PokerGFX 3.2'

    -- 페이아웃 (JSONB)
    payouts JSONB DEFAULT '[]',  -- [0,0,0,0,0,0,0,0,0,0]

    -- 타임스탬프
    created_at_gfx TIMESTAMP NOT NULL,  -- GFX CreatedDateTimeUTC
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 상태
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'closed', 'archived'
    total_hands INTEGER DEFAULT 0
);

CREATE INDEX idx_gfx_sessions_gfx_id ON gfx_sessions(gfx_id);
CREATE INDEX idx_gfx_sessions_tournament ON gfx_sessions(tournament_id);
CREATE INDEX idx_gfx_sessions_feature_table ON gfx_sessions(feature_table_id);
CREATE INDEX idx_gfx_sessions_status ON gfx_sessions(status);
```

**자막 매핑**: 세션 메타데이터, Feature Table 식별

### 4.2.2 hands (신규) - GFX Hand 확장

```sql
CREATE TABLE hands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gfx_session_id UUID REFERENCES gfx_sessions(id) ON DELETE CASCADE,
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,

    -- 핸드 정보 (GFX)
    hand_number INTEGER NOT NULL,
    table_number INTEGER NOT NULL,

    -- 게임 정보 (GFX GameVariant, GameClass, BetStructure)
    game_variant VARCHAR(20) DEFAULT 'HOLDEM',  -- 'HOLDEM', 'OMAHA', 'STUD'
    game_class VARCHAR(20) DEFAULT 'FLOP',  -- 'FLOP', 'DRAW', 'STUD'
    bet_structure VARCHAR(20) DEFAULT 'NOLIMIT',  -- 'NOLIMIT', 'POTLIMIT', 'LIMIT'

    -- 블라인드 정보 (GFX FlopDrawBlinds)
    level_number INTEGER NOT NULL,
    button_seat INTEGER,  -- ButtonPlayerNum
    small_blind_seat INTEGER,  -- SmallBlindPlayerNum
    small_blind_amount DECIMAL(12,2),  -- SmallBlindAmt
    big_blind_seat INTEGER,  -- BigBlindPlayerNum
    big_blind_amount DECIMAL(12,2),  -- BigBlindAmt
    ante_type VARCHAR(30),  -- 'BB_ANTE_BB1ST', 'ANTE_ALL', etc.

    -- Run It 정보 (GFX)
    num_boards INTEGER DEFAULT 1,  -- NumBoards
    run_it_num_times INTEGER DEFAULT 1,  -- RunItNumTimes

    -- 팟 정보
    pot_size DECIMAL(12,2) DEFAULT 0,
    rake DECIMAL(10,2) DEFAULT 0,

    -- 결과
    winner_id UUID REFERENCES players(id),
    winning_hand VARCHAR(50),  -- "Full House, Aces full of Kings"

    -- 시간 정보 (GFX)
    duration INTERVAL,  -- GFX Duration (PT2M56.2628165S → interval)
    started_at TIMESTAMP NOT NULL,  -- GFX StartDateTimeUTC
    completed_at TIMESTAMP,

    -- 상태
    status VARCHAR(20) DEFAULT 'in_progress',  -- 'in_progress', 'completed', 'void'

    UNIQUE(tournament_id, hand_number, table_number)
);

CREATE INDEX idx_hands_gfx_session ON hands(gfx_session_id);
CREATE INDEX idx_hands_tournament ON hands(tournament_id);
CREATE INDEX idx_hands_table ON hands(table_number);
CREATE INDEX idx_hands_number ON hands(hand_number DESC);
CREATE INDEX idx_hands_winner ON hands(winner_id);
CREATE INDEX idx_hands_game_variant ON hands(game_variant);
```

**자막 매핑**: Chip Flow (hand_number 기준), Hand Highlight (Soft Contents)

### 4.2.3 hand_players (신규) - 핸드별 플레이어 상태

```sql
CREATE TABLE hand_players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hand_id UUID NOT NULL REFERENCES hands(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,

    -- 시트 정보 (GFX PlayerNum)
    seat_number INTEGER NOT NULL,  -- 1-10

    -- 스택 정보 (GFX StartStackAmt, EndStackAmt)
    start_stack DECIMAL(12,2) NOT NULL,
    end_stack DECIMAL(12,2) NOT NULL,
    cumulative_winnings DECIMAL(12,2) DEFAULT 0,  -- CumulativeWinningsAmt

    -- 카드 정보 (GFX HoleCards)
    hole_cards VARCHAR(10),  -- 'AsKh' (변환된 형식)

    -- 상태 (GFX)
    sitting_out BOOLEAN DEFAULT FALSE,  -- SittingOut
    is_winner BOOLEAN DEFAULT FALSE,

    -- 실시간 통계 (GFX 제공)
    vpip_percent DECIMAL(5,2),  -- VPIPPercent
    pfr_percent DECIMAL(5,2),  -- PreFlopRaisePercent
    aggression_percent DECIMAL(5,2),  -- AggressionFrequencyPercent
    wtsd_percent DECIMAL(5,2),  -- WentToShowDownPercent

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(hand_id, seat_number)
);

CREATE INDEX idx_hand_players_hand ON hand_players(hand_id);
CREATE INDEX idx_hand_players_player ON hand_players(player_id);
CREATE INDEX idx_hand_players_seat ON hand_players(seat_number);
CREATE INDEX idx_hand_players_winner ON hand_players(is_winner) WHERE is_winner = TRUE;
```

**자막 매핑**: Player Stats, Chip Flow, Heads-Up Comparison

### 4.2.4 hand_actions (확장) - GFX Event 매핑

```sql
CREATE TABLE hand_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hand_id UUID NOT NULL REFERENCES hands(id) ON DELETE CASCADE,
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    player_id UUID REFERENCES players(id) ON DELETE CASCADE,  -- NULL for BOARD_CARD events

    -- 포지션 정보 (GFX PlayerNum)
    seat_number INTEGER,  -- 1-10 (GFX PlayerNum)
    position_name VARCHAR(20),  -- 'BTN', 'SB', 'BB', 'UTG', 'MP', 'CO', etc.

    -- 액션 정보 (GFX Event)
    street VARCHAR(10) NOT NULL,  -- 'preflop', 'flop', 'turn', 'river'
    action_order INTEGER NOT NULL,  -- 해당 스트리트 내 순서
    action VARCHAR(20) NOT NULL,  -- 'fold', 'call', 'raise', 'check', 'bet', 'all-in', 'showdown'

    -- 베팅 정보 (GFX BetAmt, Pot)
    bet_amount DECIMAL(12,2),  -- GFX BetAmt
    pot_size_after DECIMAL(12,2),  -- GFX Pot

    -- 보드/드로우 정보 (GFX)
    board_num INTEGER DEFAULT 0,  -- GFX BoardNum (Run It Twice)
    num_cards_drawn INTEGER DEFAULT 0,  -- GFX NumCardsDrawn (Draw games)

    -- 타임스탬프 (GFX DateTimeUTC)
    timestamp TIMESTAMP,  -- GFX DateTimeUTC (nullable)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actions_hand ON hand_actions(hand_id);
CREATE INDEX idx_actions_player ON hand_actions(player_id);
CREATE INDEX idx_actions_street ON hand_actions(street);
CREATE INDEX idx_actions_action ON hand_actions(action);
CREATE INDEX idx_actions_order ON hand_actions(hand_id, action_order);
```

**자막 매핑**: VPIP/PFR 계산 소스, Chip Comparison

**GFX EventType → action 변환**:

| GFX EventType | DB action | 비고 |
|---------------|-----------|------|
| `FOLD` | `fold` | - |
| `CALL` | `call` | - |
| `CHECK` | `check` | - |
| `RAISE` | `raise` | - |
| `BET` | `bet` | - |
| `ALL_IN` | `all-in` | - |
| `SHOWDOWN` | `showdown` | - |
| `BOARD CARD` | - | → community_cards 테이블로 분리 |

### 4.2.5 community_cards (신규) - GFX BOARD CARD

```sql
CREATE TABLE community_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hand_id UUID NOT NULL REFERENCES hands(id) ON DELETE CASCADE,

    -- 스트리트 (GFX BOARD CARD event)
    street VARCHAR(10) NOT NULL,  -- 'flop', 'turn', 'river'

    -- 보드 번호 (GFX BoardNum - Run It Twice 지원)
    board_num INTEGER DEFAULT 0,

    -- 카드 정보 (GFX BoardCards, 변환된 형식)
    card_1 CHAR(2),  -- 'Ah', 'Ks', '2d', 'Tc', etc.
    card_2 CHAR(2),  -- Flop only
    card_3 CHAR(2),  -- Flop only

    -- 원본 GFX 카드 (소문자)
    gfx_cards JSONB,  -- ["as", "kh", "7d"]

    -- 소스
    source VARCHAR(20) DEFAULT 'gfx',  -- 'gfx', 'manual'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(hand_id, street, board_num)
);

CREATE INDEX idx_community_hand ON community_cards(hand_id);
CREATE INDEX idx_community_street ON community_cards(street);
CREATE INDEX idx_community_board ON community_cards(board_num);
```

**자막 매핑**: Hand Display (Virtual Table 연동)

### 4.2.6 feature_tables (신규)

```sql
CREATE TABLE feature_tables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,

    -- 테이블 정보
    table_number INTEGER NOT NULL,
    table_name VARCHAR(100),  -- "Feature Table 1", "Amazon Room"

    -- RFID 연동
    rfid_enabled BOOLEAN DEFAULT TRUE,
    rfid_device_id VARCHAR(100),

    -- 방송 상태
    is_live BOOLEAN DEFAULT FALSE,
    camera_position VARCHAR(50),  -- "Main", "Bird's Eye", "Rail"

    -- 활성 상태
    is_active BOOLEAN DEFAULT TRUE,
    activated_at TIMESTAMP,
    deactivated_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(tournament_id, table_number)
);

CREATE INDEX idx_feature_tournament ON feature_tables(tournament_id);
CREATE INDEX idx_feature_active ON feature_tables(is_active) WHERE is_active = TRUE;
```

**자막 매핑**: Feature Table Leaderboard, L-Bar (Table Info)

### 4.2.7 eliminations (신규) - GFX EliminationRank

```sql
CREATE TABLE eliminations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,

    -- 탈락 정보
    final_rank INTEGER NOT NULL,
    payout_received DECIMAL(12,2),

    -- 탈락 상황
    eliminated_by_id UUID REFERENCES players(id),  -- 탈락시킨 플레이어
    elimination_hand_id UUID REFERENCES hands(id),

    -- 핸드 정보 (Heads-up)
    player_hole_cards CHAR(4),  -- 탈락 플레이어 핸드
    eliminator_hole_cards CHAR(4),  -- 탈락시킨 플레이어 핸드

    -- 방송 표시 여부
    was_broadcast BOOLEAN DEFAULT FALSE,
    broadcast_at TIMESTAMP,

    eliminated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_elim_tournament ON eliminations(tournament_id);
CREATE INDEX idx_elim_player ON eliminations(player_id);
CREATE INDEX idx_elim_rank ON eliminations(final_rank);
CREATE INDEX idx_elim_time ON eliminations(eliminated_at DESC);
```

**자막 매핑**:
- Elimination Banner (final_rank, payout_received, eliminated_at)
- Mini Payouts (최근 탈락자 상금)

### 4.2.8 soft_contents (신규)

```sql
CREATE TABLE soft_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID REFERENCES tournaments(id) ON DELETE SET NULL,

    -- 콘텐츠 유형 (PRD-0001 4.6)
    content_type VARCHAR(50) NOT NULL,  -- 'player_intro', 'player_update', 'hand_highlight', 'interview', 'special_moment'

    -- 관련 플레이어
    player_id UUID REFERENCES players(id),

    -- 콘텐츠 정보
    title VARCHAR(255),
    description TEXT,
    media_url TEXT,  -- 영상/이미지 URL

    -- 우선순위
    priority INTEGER DEFAULT 5,

    -- 상태
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'ready', 'played', 'skipped'

    -- 예약 시간
    scheduled_at TIMESTAMP,
    played_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_soft_tournament ON soft_contents(tournament_id);
CREATE INDEX idx_soft_player ON soft_contents(player_id);
CREATE INDEX idx_soft_status ON soft_contents(status);
CREATE INDEX idx_soft_scheduled ON soft_contents(scheduled_at);
```

**자막 매핑**:
- Player 소개/업데이트 (Soft Contents)
- Interview Card
- Special Moment

---

**Previous**: [← Part 3: Database Schema](./03-database-schema.md) | **Next**: [Part 5: Caption Mapping →](./05-caption-mapping.md)
