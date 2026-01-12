# PRD: Caption Generation Workflow System

**PRD Number**: PRD-0003
**Version**: 1.3
**Date**: 2025-12-25
**Status**: Draft
**Parent PRD**: PRD-0001 (WSOP Broadcast Graphics System), PRD-0002 (Workflow Automation System)

### Changelog
| Version | Date | Changes |
|---------|------|---------|
| 1.3 | 2026-01-05 | OBS/vMix → Korea Production 방송 시스템 변경 (Non-Goals, 데이터 흐름도) |
| 1.2 | 2025-12-26 | 섹션 3.1.1 개선 - 상호 배타적 데이터 소스 분류 체계 (중복/충돌 없음), 테이블별 소스 매핑 추가 |
| 1.1 | 2025-12-25 | 섹션 3.1.1 추가 - 데이터 수집 형태 3가지 (pokerGFX JSON, WSOP+ CSV, 수기 입력) 정의 |
| 1.0 | 2025-12-25 | Initial PRD - 26개 자막 유형별 정보 수집 체계화, DB 스키마 10개 테이블, 워크플로우 파이프라인 정의 |

### Source Documents
| Document | Location |
|----------|----------|
| PRD-0001 | [WSOP Broadcast Graphics](./0001-prd-wsop-broadcast-graphics.md) |
| PRD-0002 | [Workflow Automation](./0002-prd-workflow-automation.md) |

---

## 1. Purpose & Context

### 1.1 Background

PRD-0001에서 정의된 **26개 자막 유형**의 정보 수집 방식을 체계화하고, PRD-0002의 자동화 인프라와 통합하여 **데이터 수집 → DB 저장 → 자막 생성**의 End-to-End 파이프라인을 정의합니다.

**기존 PRD의 한계**:
- PRD-0001: 자막 디자인/기능 정의 (What) ✅
- PRD-0002: 자동화 인프라 정의 (How) ✅
- **누락**: 각 자막별 데이터 수집 방식 체계화 (Where/When) ❌

### 1.2 Goals

1. **정보 수집 체계화**: 26개 자막 유형별 Pre/Live/Auto 분류
2. **DB 스키마 통합**: 10개 핵심 테이블, 관계형 모델링
3. **워크플로우 파이프라인**: 이벤트 트리거 기반 자막 생성 자동화
4. **에이전트 역할 정의**: DataCollectionAgent, GraphicsTriggerAgent 신규 정의

### 1.3 Non-Goals

- 자막 디자인/애니메이션 (PRD-0001 담당)
- 자동화 인프라 구축 (PRD-0002 담당)
- 방송 송출 시스템 (Korea Production에서 담당)

---

## 2. Caption Classification System

### 2.1 26개 자막 유형 (5개 카테고리)

| 카테고리 | 자막 수 | 주요 자막 |
|---------|--------|----------|
| **Leaderboard** | 5 | Tournament LB, Feature LB, Mini LB, Payouts, Mini Payouts |
| **Player Info** | 6 | Profile, Intro Card, At Risk, Elimination, Commentator, Heads-Up |
| **Statistics** | 5 | Chip Flow, Chip Comparison, Chips In Play, VPIP, Chip Stack Bar |
| **Event Graphics** | 5 | Schedule, Event Info, Venue, Tournament Info, Event Name |
| **Transition & L-Bar** | 5 | Blind Level, L-Bar (3종), Transition, Stinger |

### 2.2 정보 수집 방식 분류

| 수집 방식 | 코드 | 설명 | 타이밍 | 담당자 |
|----------|:----:|------|--------|--------|
| **Pre-Production** | Pre | 토너먼트 시작 전 수집 | D-7 ~ D-1 | Data Manager |
| **Live (Real-time)** | Live | RFID, 타이머, 수동 입력 | 방송 중 | RFID System, PA |
| **Auto-Generated** | Auto | 계산/집계/파생 데이터 | 실시간 | Calculation Agent |

### 2.3 자막별 데이터 매트릭스 (상세)

#### A. Leaderboard System (5개 자막)

| 자막 유형 | Pre | Live | Auto | 필요 데이터 | 핵심 테이블 | 트리거 이벤트 |
|----------|:---:|:----:|:----:|------------|------------|--------------|
| **Tournament Leaderboard** | - | O | O | chips, rank, player_id, bb_count, rank_change | players, chip_history | `hand_completed`, `level_change` |
| **Feature Table Leaderboard** | - | O | - | chips, seat, table_id, profile_photo, nationality | players, player_profiles | `feature_table_change` |
| **Mini Chip Counts** | - | O | O | chips, rank_change, highlight_flag | chip_history | `chip_update`, `pot_won` |
| **Payouts** | O | - | - | payout_structure, places_paid, total_prize | payouts | `tournament_start`, `itm_reached` |
| **Mini Payouts** | O | O | - | current_payout, next_payout, bubble_line | payouts, players | `elimination`, `pay_jump` |

#### B. Player Info System (6개 자막)

| 자막 유형 | Pre | Live | Auto | 필요 데이터 | 핵심 테이블 | 트리거 이벤트 |
|----------|:---:|:----:|:----:|------------|------------|--------------|
| **Player Profile** | O | O | - | name, nationality, photo, bracelets, earnings, current_stack | players, player_profiles | `player_featured` |
| **Player Intro Card** | O | - | - | biography, notable_wins, wsop_stats, hendon_mob_id | player_profiles | `player_intro_trigger` |
| **At Risk of Elimination** | - | O | O | current_stack, bb_count, payout_at_risk, rank | players, payouts | `all_in_detected`, `short_stack` |
| **Elimination Banner** | - | O | - | final_rank, payout_received, name, nationality | players | `player_eliminated` |
| **Commentator Profile** | O | - | - | name, photo, credentials, bio | commentators | `broadcast_start` |
| **Heads-Up Comparison** | O | O | O | stats_comparison, head2head_record, chip_ratio | player_stats, chip_history | `heads_up_trigger` |

#### C. Statistics (5개 자막)

| 자막 유형 | Pre | Live | Auto | 필요 데이터 | 핵심 테이블 | 트리거 이벤트 |
|----------|:---:|:----:|:----:|------------|------------|--------------|
| **Chip Flow** | - | O | O | chip_history[last_15], avg_stack, trend_direction | chip_history | `hand_completed` (N hands) |
| **Chip Comparison** | - | O | O | player1_chips, player2_chips, pot_equity, ratio | chip_history | `showdown_start` |
| **Chips In Play** | O | O | - | chip_denominations, total_chips_in_play | blind_levels, tournaments | `level_start`, `break_end` |
| **VPIP Stats** | - | O | O | vpip_percentage, pfr_percentage, hands_played | player_stats, hand_actions | `stat_threshold_reached` |
| **Chip Stack Bar** | - | O | O | stack_ranking, bb_equivalent, percentage_of_total | chip_history, players | `feature_table_update` |

#### D. Event Graphics (5개 자막)

| 자막 유형 | Pre | Live | Auto | 필요 데이터 | 핵심 테이블 | 트리거 이벤트 |
|----------|:---:|:----:|:----:|------------|------------|--------------|
| **Broadcast Schedule** | O | - | - | dates, times, event_names, channels | schedules | `show_schedule_trigger` |
| **Event Info** | O | O | - | buy_in, prize_pool, entries, remaining, places_paid | tournaments | `tournament_start`, `level_change` |
| **Venue/Location** | O | - | - | venue_name, city, drone_shot_url | venues | `venue_shot_trigger` |
| **Tournament Info** | O | O | - | event_name, day_number, current_level, avg_stack | tournaments, blind_levels | `day_start` |
| **Event Name Overlay** | O | - | - | event_full_name, sponsor_logos | events | `event_name_trigger` |

#### E. Transition & L-Bar (5개 자막)

| 자막 유형 | Pre | Live | Auto | 필요 데이터 | 핵심 테이블 | 트리거 이벤트 |
|----------|:---:|:----:|:----:|------------|------------|--------------|
| **Blind Level** | - | O | - | current_level, blinds, ante, duration, next_level | blind_levels | `level_change` |
| **L-Bar (Standard)** | - | O | O | blinds, seats_remaining, schedule_info, score | tournaments, blind_levels | `always_on` |
| **L-Bar (Regi Open)** | - | O | - | registration_countdown, current_entries | tournaments | `registration_open` |
| **L-Bar (Regi Close)** | - | O | - | final_entries, time_to_close | tournaments | `pre_registration_close` |
| **Transition/Stinger** | - | - | - | transition_type, player_id (optional) | - | `scene_change`, `player_highlight` |

---

## 3. Data Collection Workflow

### 3.1 전체 데이터 흐름

![Caption Data Flow](../../docs/images/caption-data-flow.png)

#### 3.1.1 상호 배타적 데이터 소스 분류

3가지 데이터 소스는 **서로 중복되거나 충돌하지 않습니다**.

| 소스 | 수집 범위 | 사용 단계 | 지연 시간 |
|------|----------|----------|----------|
| **pokerGFX JSON** | **오직 Feature Table 정보만** | Live | < 2초 |
| **WSOP+ CSV** | **오직 대회 정보 + Feature 이외 테이블만** | Live | - |
| **수기 입력** | **오직 1, 2에 해당하지 않는 정보만** | All Phases | - |

##### 소스 1: pokerGFX JSON (Feature Table 전용)

| 데이터 | 테이블 | 설명 |
|--------|--------|------|
| **칩 카운트** | `chip_history`, `players.chips` | Feature Table 플레이어만 |
| **핸드 액션** | `hand_actions` | 폴드, 콜, 레이즈, 베팅 등 |
| **홀 카드** | `hand_actions.hole_cards` | RFID로 추출된 카드 정보 |
| **팟 사이즈** | `hand_actions.pot_size_after` | 각 액션 후 팟 크기 |

##### 소스 2: WSOP+ CSV (대회 정보 + Other Tables)

| 데이터 | 테이블 | 설명 |
|--------|--------|------|
| **대회 정보** | `tournaments` | buy_in, prize_pool, registered/remaining players |
| **블라인드 레벨** | `blind_levels` | 현재 레벨, 다음 레벨, 남은 시간 |
| **페이아웃 구조** | `payouts` | 순위별 상금, 버블 라인 |
| **Other Tables 칩** | `players.chips` | Feature Table 이외 플레이어 |
| **남은 참가자 수** | `tournaments.remaining_players` | 실시간 탈락 반영 |

##### 소스 3: 수기 입력 (자동화 불가 정보)

| 데이터 | 테이블 | 담당자 |
|--------|--------|--------|
| **플레이어 프로필** | `player_profiles` | Data Manager |
| **프로필 사진** | `player_profiles.photo_url` | Data Manager |
| **바이오그래피** | `player_profiles.biography` | Data Manager |
| **좌석 배치** | `players.seat_number` | PA |
| **피처 테이블 지정** | `players.is_feature_table` | PD |
| **코멘테이터** | `commentators` | Production Team |
| **이벤트/장소** | `events`, `venues` | PD |

##### 테이블별 소스 매핑 (상호 배타적)

| 테이블 | pokerGFX JSON | WSOP+ CSV | 수기 입력 |
|--------|:-------------:|:---------:|:---------:|
| `chip_history` | **Feature만** | **Other만** | - |
| `hand_actions` | **전체** | - | - |
| `players.chips` | **Feature만** | **Other만** | - |
| `players.seat` | - | - | **전체** |
| `tournaments` | - | **전체** | - |
| `blind_levels` | - | **전체** | - |
| `payouts` | - | **전체** | - |
| `player_profiles` | - | - | **전체** |
| `commentators` | - | - | **전체** |
| `events`, `venues` | - | - | **전체** |

**핵심 원칙**: 각 데이터는 하나의 소스에서만 수집 → **충돌 불가능**

### 3.2 사전 준비 (Pre-Production)

**담당**: Data Manager
**타이밍**: D-7 ~ D-1

| 데이터 | 소스 | 수집 방법 | 저장 테이블 |
|--------|------|----------|------------|
| **Player Profiles** | Hendon Mob, WSOP.com | 크롤링 + 수동 입력 | player_profiles |
| **Payout Structure** | Tournament Director | CSV 임포트 | payouts |
| **Event/Venue Info** | Production Team | 수동 입력 | events, venues |
| **Broadcast Schedule** | PD | Google Sheets 동기화 | schedules |
| **Blind Structure** | Tournament Director | CSV 임포트 | blind_levels |
| **Commentator Profiles** | Production Team | 수동 입력 | commentators |

#### 3.2.1 Player Profile Import

```python
# Hendon Mob 크롤링 예시
class PlayerProfileImporter:
    """사전 플레이어 프로필 수집"""

    async def import_from_hendon_mob(self, player_id: str) -> PlayerProfile:
        """Hendon Mob에서 플레이어 정보 수집"""
        # 1. Hendon Mob 페이지 크롤링
        # 2. WSOP 브레이슬릿, 총 상금, 주요 성적 추출
        # 3. player_profiles 테이블에 저장
        pass

    async def import_from_csv(self, csv_path: str) -> list[PlayerProfile]:
        """CSV 배치 임포트"""
        pass
```

#### 3.2.2 Payout Structure Import

```python
# Payout 구조 임포트 예시
PAYOUT_CSV_FORMAT = """
place_start,place_end,amount,percentage
1,1,1000000,15.0
2,2,600000,9.0
3,3,400000,6.0
4,5,250000,3.75
6,9,150000,2.25
"""
```

### 3.3 실시간 수집 (Live)

**담당**: RFID System, Tournament Timer, PA
**타이밍**: 방송 중 (실시간)

| 데이터 | 소스 | 수집 방법 | 저장 테이블 | 지연 시간 |
|--------|------|----------|------------|----------|
| **Chip Counts** | RFID System | 자동 수신 | players, chip_history | < 2초 |
| **Hand Actions** | RFID System | 자동 파싱 | hand_actions | < 2초 |
| **Blind Level** | Tournament Timer | 자동 감지 | blind_levels | < 1초 |
| **Player Position** | PA (수동) | Control Panel | players | 수동 |
| **Feature Table** | PD (수동) | Control Panel | players | 수동 |

#### 3.3.1 RFID Data Flow

```python
class RFIDDataReceiver:
    """RFID 데이터 수신 및 처리"""

    async def on_hand_completed(self, rfid_data: dict):
        """핸드 완료 시 호출"""
        # 1. RFID 원시 데이터 파싱
        parsed = await self.parser.parse(rfid_data)

        # 2. hand_actions 테이블 저장
        await self.db.insert_hand_action(parsed)

        # 3. chip_history 업데이트
        await self.update_chip_history(parsed)

        # 4. player_stats 재계산 트리거
        await self.event_bus.emit('hand_completed', parsed)
```

#### 3.3.2 Tournament Timer Integration

```python
class TournamentTimer:
    """블라인드 레벨 자동 관리"""

    async def on_level_change(self, new_level: int):
        """레벨 변경 시 호출"""
        # 1. blind_levels 테이블 업데이트
        await self.db.update_current_level(new_level)

        # 2. 이벤트 발생
        await self.event_bus.emit('level_change', {
            'level': new_level,
            'blinds': self.get_blinds(new_level),
            'ante': self.get_ante(new_level)
        })
```

### 3.4 자동 생성 (Auto-Generated)

**담당**: Calculation Agent
**타이밍**: 실시간 (이벤트 트리거)

| 데이터 | 계산 방법 | 트리거 이벤트 | 저장 테이블 |
|--------|----------|--------------|------------|
| **VPIP/PFR** | hand_actions 집계 | `hand_completed` | player_stats |
| **Chip Flow** | chip_history 최근 N개 | `hand_completed` | (캐시) |
| **Rank/BB** | chips / big_blind | `chip_update` | chip_history |
| **Avg Stack %** | chips / avg_stack * 100 | `chip_update` | chip_history |
| **Payout at Risk** | 현재 순위 → payout 조회 | `all_in_detected` | (실시간 계산) |

#### 3.4.1 Stats Calculator

```python
class StatsCalculator:
    """플레이어 통계 자동 계산"""

    async def calculate_vpip(self, player_id: str) -> float:
        """VPIP 계산: 자발적 팟 참여율"""
        total_hands = await self.db.count_hands(player_id)
        voluntarily_in_pot = await self.db.count_actions(
            player_id,
            actions=['call', 'raise', 'bet']
        )
        return (voluntarily_in_pot / total_hands * 100) if total_hands > 0 else 0

    async def calculate_pfr(self, player_id: str) -> float:
        """PFR 계산: 프리플랍 레이즈율"""
        preflop_hands = await self.db.count_hands(player_id, street='preflop')
        raises = await self.db.count_actions(
            player_id,
            actions=['raise'],
            street='preflop'
        )
        return (raises / preflop_hands * 100) if preflop_hands > 0 else 0
```

#### 3.4.2 Chip Flow Generator

```python
class ChipFlowGenerator:
    """Chip Flow 차트 데이터 생성"""

    async def generate(self, player_id: str, last_n_hands: int = 15) -> list[dict]:
        """최근 N핸드 칩 히스토리 생성"""
        history = await self.db.get_chip_history(
            player_id,
            limit=last_n_hands,
            order_by='hand_number DESC'
        )

        avg_stack = await self.db.get_avg_stack()

        return [
            {
                'hand_number': h.hand_number,
                'chips': h.chips,
                'avg_percentage': (h.chips / avg_stack * 100) if avg_stack > 0 else 0,
                'trend': 'up' if h.chips_change > 0 else 'down' if h.chips_change < 0 else 'flat'
            }
            for h in reversed(history)
        ]
```

---

## 4. Database Schema

### 4.1 ERD Diagram

![Caption DB ERD](../../docs/images/caption-db-erd.png)

### 4.2 Table Definitions (10개)

#### 4.2.1 events

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    event_code VARCHAR(50) UNIQUE NOT NULL,  -- 'WSOP_2026_LV', 'WSOP_2025_SC_CYPRUS'
    venue_id UUID REFERENCES venues(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',  -- 'scheduled', 'running', 'completed'
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_events_code ON events(event_code);
CREATE INDEX idx_events_status ON events(status);
```

#### 4.2.2 tournaments

```sql
CREATE TABLE tournaments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    buy_in DECIMAL(10,2) NOT NULL,
    starting_chips INTEGER NOT NULL,
    current_level INTEGER DEFAULT 1,
    current_day INTEGER DEFAULT 1,  -- Day 1, 2, 3, Final
    registered_players INTEGER DEFAULT 0,
    remaining_players INTEGER DEFAULT 0,
    prize_pool DECIMAL(15,2) DEFAULT 0,
    bubble_line INTEGER,  -- ITM 진입 라인
    is_itm BOOLEAN DEFAULT FALSE,
    is_registration_open BOOLEAN DEFAULT TRUE,
    registration_closes_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'scheduled',  -- 'scheduled', 'running', 'paused', 'completed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_tournaments_event ON tournaments(event_id);
CREATE INDEX idx_tournaments_status ON tournaments(status);
CREATE INDEX idx_tournaments_day ON tournaments(current_day);
```

#### 4.2.3 players

```sql
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    nationality CHAR(2) NOT NULL,  -- ISO 3166-1 alpha-2
    photo_url TEXT,
    chips INTEGER NOT NULL DEFAULT 0,
    seat_number INTEGER,  -- 1-10
    table_number INTEGER,
    is_feature_table BOOLEAN DEFAULT FALSE,
    is_eliminated BOOLEAN DEFAULT FALSE,
    eliminated_at TIMESTAMP,
    final_rank INTEGER,
    payout_received DECIMAL(12,2),
    registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_players_tournament ON players(tournament_id);
CREATE INDEX idx_players_chips ON players(chips DESC);
CREATE INDEX idx_players_table ON players(table_number, seat_number);
CREATE INDEX idx_players_feature ON players(is_feature_table) WHERE is_feature_table = TRUE;
CREATE INDEX idx_players_eliminated ON players(is_eliminated);
```

#### 4.2.4 player_profiles

```sql
CREATE TABLE player_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID UNIQUE NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    hendon_mob_id VARCHAR(50),
    wsop_bracelets INTEGER DEFAULT 0,
    total_earnings DECIMAL(15,2) DEFAULT 0,
    final_tables INTEGER DEFAULT 0,
    biography TEXT,
    notable_wins JSONB DEFAULT '[]',  -- [{"event": "...", "year": 2023, "prize": 1000000}]
    hometown VARCHAR(255),
    age INTEGER,
    profession VARCHAR(255),
    social_links JSONB DEFAULT '{}',  -- {"twitter": "...", "instagram": "..."}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_profiles_hendon ON player_profiles(hendon_mob_id);
CREATE INDEX idx_profiles_bracelets ON player_profiles(wsop_bracelets DESC);
CREATE INDEX idx_profiles_earnings ON player_profiles(total_earnings DESC);
```

#### 4.2.5 player_stats

```sql
CREATE TABLE player_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    hands_played INTEGER DEFAULT 0,
    vpip DECIMAL(5,2) DEFAULT 0,  -- Voluntarily Put $ In Pot (0-100%)
    pfr DECIMAL(5,2) DEFAULT 0,   -- Pre-Flop Raise (0-100%)
    aggression_factor DECIMAL(5,2),  -- (Bet + Raise) / Call
    showdown_win_rate DECIMAL(5,2),
    three_bet_percentage DECIMAL(5,2),
    fold_to_three_bet DECIMAL(5,2),
    last_calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(player_id, tournament_id)
);

-- 인덱스
CREATE INDEX idx_stats_player ON player_stats(player_id);
CREATE INDEX idx_stats_vpip ON player_stats(vpip);
CREATE INDEX idx_stats_pfr ON player_stats(pfr);
```

#### 4.2.6 chip_history

```sql
CREATE TABLE chip_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    hand_number INTEGER NOT NULL,
    level_number INTEGER NOT NULL,
    chips INTEGER NOT NULL,
    chips_change INTEGER DEFAULT 0,  -- +/- from previous hand
    bb_count DECIMAL(10,2),  -- chips / big_blind
    avg_stack_percentage DECIMAL(6,2),  -- chips / avg_stack * 100
    source VARCHAR(20) DEFAULT 'rfid',  -- 'rfid', 'manual', 'calculated'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_chip_history_player ON chip_history(player_id);
CREATE INDEX idx_chip_history_tournament ON chip_history(tournament_id);
CREATE INDEX idx_chip_history_hand ON chip_history(hand_number DESC);
CREATE INDEX idx_chip_history_timestamp ON chip_history(timestamp DESC);

-- 파티셔닝 고려 (대용량 데이터)
-- CREATE TABLE chip_history_partitioned (
--     ...
-- ) PARTITION BY RANGE (timestamp);
```

#### 4.2.7 hand_actions

```sql
CREATE TABLE hand_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    table_number INTEGER NOT NULL,
    hand_number INTEGER NOT NULL,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,  -- 1-10 (seat position)
    hole_cards CHAR(4),  -- 'AhKs', 'QdQc' (RFID로 추출)
    street VARCHAR(10) NOT NULL,  -- 'preflop', 'flop', 'turn', 'river'
    action VARCHAR(20) NOT NULL,  -- 'fold', 'call', 'raise', 'check', 'bet', 'all-in'
    bet_amount DECIMAL(12,2),
    pot_size_after DECIMAL(12,2),
    is_winner BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_actions_tournament ON hand_actions(tournament_id);
CREATE INDEX idx_actions_player ON hand_actions(player_id);
CREATE INDEX idx_actions_hand ON hand_actions(hand_number);
CREATE INDEX idx_actions_street ON hand_actions(street);
CREATE INDEX idx_actions_action ON hand_actions(action);
```

#### 4.2.8 payouts

```sql
CREATE TABLE payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    place_start INTEGER NOT NULL,  -- 1, 2, 3, 4 (for 4-5), 6 (for 6-9), ...
    place_end INTEGER NOT NULL,    -- 1, 2, 3, 5, 9, ...
    amount DECIMAL(12,2) NOT NULL,
    percentage DECIMAL(5,2),  -- of total prize pool
    is_current_bubble BOOLEAN DEFAULT FALSE,  -- 현재 버블 라인
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_payouts_tournament ON payouts(tournament_id);
CREATE INDEX idx_payouts_place ON payouts(place_start, place_end);
CREATE UNIQUE INDEX idx_payouts_unique ON payouts(tournament_id, place_start, place_end);
```

#### 4.2.9 blind_levels

```sql
CREATE TABLE blind_levels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    level_number INTEGER NOT NULL,
    small_blind INTEGER NOT NULL,
    big_blind INTEGER NOT NULL,
    ante INTEGER DEFAULT 0,
    big_blind_ante INTEGER DEFAULT 0,  -- BBA (Big Blind Ante)
    duration_minutes INTEGER NOT NULL,
    is_break BOOLEAN DEFAULT FALSE,
    break_duration_minutes INTEGER,
    is_current BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP,
    ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(tournament_id, level_number)
);

-- 인덱스
CREATE INDEX idx_blinds_tournament ON blind_levels(tournament_id);
CREATE INDEX idx_blinds_level ON blind_levels(level_number);
CREATE INDEX idx_blinds_current ON blind_levels(is_current) WHERE is_current = TRUE;
```


