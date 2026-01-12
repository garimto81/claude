#### 4.2.10 graphics_queue

```sql
CREATE TABLE graphics_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID REFERENCES tournaments(id) ON DELETE SET NULL,
    graphic_type VARCHAR(50) NOT NULL,  -- 'tournament_leaderboard', 'chip_flow', 'at_risk', ...
    trigger_event VARCHAR(50) NOT NULL,  -- 'level_change', 'elimination', 'hand_completed', ...
    payload JSONB NOT NULL DEFAULT '{}',  -- 자막 렌더링에 필요한 데이터
    priority INTEGER DEFAULT 5,  -- 1 (highest) - 10 (lowest)
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'rendering', 'rendered', 'displayed', 'dismissed', 'failed'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rendered_at TIMESTAMP,
    displayed_at TIMESTAMP,
    dismissed_at TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_queue_tournament ON graphics_queue(tournament_id);
CREATE INDEX idx_queue_status ON graphics_queue(status);
CREATE INDEX idx_queue_priority ON graphics_queue(priority);
CREATE INDEX idx_queue_created ON graphics_queue(created_at DESC);
CREATE INDEX idx_queue_pending ON graphics_queue(status, priority, created_at)
    WHERE status = 'pending';
```

### 4.3 SQL Migration Script

```sql
-- Migration: 001_create_caption_tables.sql
-- Description: PRD-0003 자막 시스템 테이블 생성
-- Author: Claude Code
-- Date: 2025-12-25

BEGIN;

-- 1. venues (참조용, 간단)
CREATE TABLE IF NOT EXISTS venues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    country CHAR(2),
    address TEXT,
    drone_shot_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. events
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    event_code VARCHAR(50) UNIQUE NOT NULL,
    venue_id UUID REFERENCES venues(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. tournaments
CREATE TABLE IF NOT EXISTS tournaments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    buy_in DECIMAL(10,2) NOT NULL,
    starting_chips INTEGER NOT NULL,
    current_level INTEGER DEFAULT 1,
    current_day INTEGER DEFAULT 1,
    registered_players INTEGER DEFAULT 0,
    remaining_players INTEGER DEFAULT 0,
    prize_pool DECIMAL(15,2) DEFAULT 0,
    bubble_line INTEGER,
    is_itm BOOLEAN DEFAULT FALSE,
    is_registration_open BOOLEAN DEFAULT TRUE,
    registration_closes_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. players
CREATE TABLE IF NOT EXISTS players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    nationality CHAR(2) NOT NULL,
    photo_url TEXT,
    chips INTEGER NOT NULL DEFAULT 0,
    seat_number INTEGER,
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

-- 5. player_profiles
CREATE TABLE IF NOT EXISTS player_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID UNIQUE NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    hendon_mob_id VARCHAR(50),
    wsop_bracelets INTEGER DEFAULT 0,
    total_earnings DECIMAL(15,2) DEFAULT 0,
    final_tables INTEGER DEFAULT 0,
    biography TEXT,
    notable_wins JSONB DEFAULT '[]',
    hometown VARCHAR(255),
    age INTEGER,
    profession VARCHAR(255),
    social_links JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. player_stats
CREATE TABLE IF NOT EXISTS player_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    hands_played INTEGER DEFAULT 0,
    vpip DECIMAL(5,2) DEFAULT 0,
    pfr DECIMAL(5,2) DEFAULT 0,
    aggression_factor DECIMAL(5,2),
    showdown_win_rate DECIMAL(5,2),
    three_bet_percentage DECIMAL(5,2),
    fold_to_three_bet DECIMAL(5,2),
    last_calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(player_id, tournament_id)
);

-- 7. chip_history
CREATE TABLE IF NOT EXISTS chip_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    hand_number INTEGER NOT NULL,
    level_number INTEGER NOT NULL,
    chips INTEGER NOT NULL,
    chips_change INTEGER DEFAULT 0,
    bb_count DECIMAL(10,2),
    avg_stack_percentage DECIMAL(6,2),
    source VARCHAR(20) DEFAULT 'rfid',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. hand_actions
CREATE TABLE IF NOT EXISTS hand_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    table_number INTEGER NOT NULL,
    hand_number INTEGER NOT NULL,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    hole_cards CHAR(4),
    street VARCHAR(10) NOT NULL,
    action VARCHAR(20) NOT NULL,
    bet_amount DECIMAL(12,2),
    pot_size_after DECIMAL(12,2),
    is_winner BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. payouts
CREATE TABLE IF NOT EXISTS payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    place_start INTEGER NOT NULL,
    place_end INTEGER NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    percentage DECIMAL(5,2),
    is_current_bubble BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tournament_id, place_start, place_end)
);

-- 10. blind_levels
CREATE TABLE IF NOT EXISTS blind_levels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id) ON DELETE CASCADE,
    level_number INTEGER NOT NULL,
    small_blind INTEGER NOT NULL,
    big_blind INTEGER NOT NULL,
    ante INTEGER DEFAULT 0,
    big_blind_ante INTEGER DEFAULT 0,
    duration_minutes INTEGER NOT NULL,
    is_break BOOLEAN DEFAULT FALSE,
    break_duration_minutes INTEGER,
    is_current BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMP,
    ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tournament_id, level_number)
);

-- 11. graphics_queue
CREATE TABLE IF NOT EXISTS graphics_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID REFERENCES tournaments(id) ON DELETE SET NULL,
    graphic_type VARCHAR(50) NOT NULL,
    trigger_event VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rendered_at TIMESTAMP,
    displayed_at TIMESTAMP,
    dismissed_at TIMESTAMP
);

-- 12. commentators (추가)
CREATE TABLE IF NOT EXISTS commentators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    photo_url TEXT,
    credentials TEXT,
    biography TEXT,
    social_links JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. schedules (추가)
CREATE TABLE IF NOT EXISTS schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time_start TIME NOT NULL,
    time_end TIME,
    event_name VARCHAR(255) NOT NULL,
    channel VARCHAR(100),
    is_live BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_events_code ON events(event_code);
CREATE INDEX IF NOT EXISTS idx_tournaments_event ON tournaments(event_id);
CREATE INDEX IF NOT EXISTS idx_tournaments_status ON tournaments(status);
CREATE INDEX IF NOT EXISTS idx_players_tournament ON players(tournament_id);
CREATE INDEX IF NOT EXISTS idx_players_chips ON players(chips DESC);
CREATE INDEX IF NOT EXISTS idx_players_table ON players(table_number, seat_number);
CREATE INDEX IF NOT EXISTS idx_chip_history_player ON chip_history(player_id);
CREATE INDEX IF NOT EXISTS idx_chip_history_hand ON chip_history(hand_number DESC);
CREATE INDEX IF NOT EXISTS idx_actions_player ON hand_actions(player_id);
CREATE INDEX IF NOT EXISTS idx_actions_hand ON hand_actions(hand_number);
CREATE INDEX IF NOT EXISTS idx_payouts_tournament ON payouts(tournament_id);
CREATE INDEX IF NOT EXISTS idx_blinds_tournament ON blind_levels(tournament_id);
CREATE INDEX IF NOT EXISTS idx_queue_status ON graphics_queue(status);
CREATE INDEX IF NOT EXISTS idx_queue_priority ON graphics_queue(priority);

COMMIT;
```

### 4.4 Index & Performance Considerations

| 테이블 | 쿼리 패턴 | 인덱스 전략 |
|--------|----------|------------|
| **chip_history** | 최근 N핸드 조회 | `(player_id, hand_number DESC)` 복합 인덱스 |
| **hand_actions** | 특정 핸드의 모든 액션 | `(hand_number, timestamp)` 복합 인덱스 |
| **players** | 칩 순위 조회 | `(chips DESC)` 내림차순 인덱스 |
| **graphics_queue** | 대기 중 그래픽 조회 | `(status, priority, created_at)` 부분 인덱스 |

**대용량 데이터 고려**:
- `chip_history`: 파티셔닝 고려 (날짜별/토너먼트별)
- `hand_actions`: 30일 이상 데이터 아카이브
- 읽기 복제본: 그래픽 렌더링 쿼리 분산

---

## 5. Workflow Pipeline

### 5.1 Agent Hierarchy

![Caption Agent Hierarchy](../../docs/images/caption-agent-hierarchy.png)

### 5.2 Agent Definitions

#### 5.2.1 DataCollectionAgent (신규)

```python
class DataCollectionAgent(BaseAgent):
    """PRD-0003: 데이터 수집 통합 에이전트"""

    def __init__(self, config: AgentConfig, event_bus, db_session):
        super().__init__(config, event_bus, db_session)
        self.pre_production_agent = PreProductionAgent(...)
        self.live_data_agent = LiveDataAgent(...)
        self.auto_generator_agent = AutoGeneratorAgent(...)

    async def initialize(self):
        """하위 에이전트 초기화"""
        await self.pre_production_agent.initialize()
        await self.live_data_agent.initialize()
        await self.auto_generator_agent.initialize()

    async def process(self, event):
        """이벤트 라우팅"""
        if event.type.startswith('pre_production.'):
            return await self.pre_production_agent.process(event)
        elif event.type.startswith('live.'):
            return await self.live_data_agent.process(event)
        elif event.type.startswith('auto.'):
            return await self.auto_generator_agent.process(event)
```

#### 5.2.2 GraphicsTriggerAgent (신규)

```python
class GraphicsTriggerAgent(BaseAgent):
    """PRD-0003: 그래픽 트리거 에이전트"""

    def __init__(self, config: AgentConfig, event_bus, db_session):
        super().__init__(config, event_bus, db_session)
        self.event_listener = EventListenerAgent(...)
        self.priority_decision = PriorityDecisionAgent(...)
        self.queue_manager = QueueManagerAgent(...)

    async def on_event(self, event: WorkflowEvent):
        """이벤트 수신 시 그래픽 트리거 결정"""
        # 1. 이벤트-그래픽 매핑 조회
        graphics = self.get_triggered_graphics(event)

        # 2. 우선순위 결정 (AI 기반)
        prioritized = await self.priority_decision.decide(graphics, event)

        # 3. 큐에 추가
        for graphic in prioritized:
            await self.queue_manager.enqueue(graphic)

    def get_triggered_graphics(self, event: WorkflowEvent) -> list[str]:
        """이벤트에 따른 트리거 그래픽 반환"""
        mapping = {
            'hand_completed': ['chip_flow', 'mini_chip_counts', 'tournament_leaderboard'],
            'level_change': ['blind_level', 'l_bar', 'tournament_leaderboard'],
            'player_eliminated': ['elimination_banner', 'mini_payouts', 'tournament_leaderboard'],
            'all_in_detected': ['at_risk', 'chip_comparison'],
            'feature_table_change': ['feature_leaderboard', 'player_profile'],
            'itm_reached': ['payouts', 'tournament_info'],
            'day_start': ['event_info', 'tournament_info', 'broadcast_schedule'],
            'break_end': ['chips_in_play', 'blind_level'],
        }
        return mapping.get(event.type, [])
```

### 5.3 Event Trigger Mapping (8개 핵심 이벤트)

| # | 이벤트 | 발생 시점 | 트리거 자막 | 우선순위 |
|---|--------|----------|------------|----------|
| 1 | `hand_completed` | 핸드 종료 | Chip Flow, Mini Chip Counts, Tournament LB | Medium |
| 2 | `level_change` | 레벨 변경 | Blind Level, L-Bar, Tournament LB | High |
| 3 | `player_eliminated` | 플레이어 탈락 | Elimination Banner, Mini Payouts, Tournament LB | High |
| 4 | `all_in_detected` | 올인 감지 | At Risk, Chip Comparison | High |
| 5 | `feature_table_change` | 피처 테이블 변경 | Feature LB, Player Profile | Medium |
| 6 | `itm_reached` | ITM 진입 | Payouts, Tournament Info | High |
| 7 | `day_start` | Day 시작 | Event Info, Tournament Info, Schedule | Low |
| 8 | `break_end` | 브레이크 종료 | Chips In Play, Blind Level | Medium |

### 5.4 Event Type Definitions

```python
from enum import Enum

class CaptionEventType(Enum):
    # Data Collection Events
    PRE_PRODUCTION_PLAYER_IMPORTED = "pre_production.player.imported"
    PRE_PRODUCTION_PAYOUT_IMPORTED = "pre_production.payout.imported"
    PRE_PRODUCTION_SCHEDULE_UPDATED = "pre_production.schedule.updated"

    # Live Events (RFID/Timer)
    LIVE_HAND_COMPLETED = "live.hand.completed"
    LIVE_LEVEL_CHANGE = "live.level.changed"
    LIVE_PLAYER_ELIMINATED = "live.player.eliminated"
    LIVE_ALL_IN_DETECTED = "live.all_in.detected"
    LIVE_FEATURE_TABLE_CHANGE = "live.feature_table.changed"
    LIVE_ITM_REACHED = "live.itm.reached"
    LIVE_DAY_START = "live.day.started"
    LIVE_BREAK_END = "live.break.ended"
    LIVE_REGISTRATION_CLOSED = "live.registration.closed"

    # Auto-Generated Events
    AUTO_STATS_CALCULATED = "auto.stats.calculated"
    AUTO_CHIP_FLOW_GENERATED = "auto.chip_flow.generated"
    AUTO_RANK_UPDATED = "auto.rank.updated"

    # Graphics Events
    GRAPHICS_TRIGGERED = "graphics.triggered"
    GRAPHICS_RENDERED = "graphics.rendered"
    GRAPHICS_DISPLAYED = "graphics.displayed"
    GRAPHICS_DISMISSED = "graphics.dismissed"
```

---

## 6. PRD-0001/0002 Integration

### 6.1 공유 인프라

| 인프라 | PRD-0001 | PRD-0002 | PRD-0003 |
|--------|----------|----------|----------|
| **PostgreSQL** | 스키마 정의 | 이벤트 로그 | 10개 자막 테이블 |
| **Google Sheets** | 읽기 (렌더링) | 양방향 동기화 | 사전 데이터 임포트 |
| **WebSocket** | 그래픽 UI | 모니터링 | 실시간 데이터 푸시 |
| **Redis** | 세션/캐시 | Event Bus | Chip Flow 캐시 |
| **Event Bus** | - | 정의 | 8개 이벤트 추가 |

### 6.2 의존성 그래프

```
PRD-0003 (Caption Workflow)
    │
    ├──── PRD-0002 (Automation)
    │     ├── Event Bus System
    │     ├── DataSyncAgent (RFID Parser)
    │     ├── MonitoringAgent
    │     └── AI Agent Framework
    │
    └──── PRD-0001 (Graphics)
          ├── 26개 자막 컴포넌트
          ├── Control Panel
          ├── Korea Production Integration
          └── Animation System
```

### 6.3 데이터 흐름 통합

```
RFID System (현장)
    │
    ▼
PRD-0002: RFIDParserAgent
    │
    ▼
PRD-0003: DataCollectionAgent ───────────────┐
    │                                         │
    ├── LiveDataAgent ─────────────┐          │
    ├── AutoGeneratorAgent ────────┤          │
    └── PreProductionAgent ────────┤          │
                                   │          │
                                   ▼          ▼
                           PostgreSQL (10 Tables)
                                   │
                                   ▼
PRD-0003: GraphicsTriggerAgent
    │
    ├── EventListenerAgent
    ├── PriorityDecisionAgent (AI)
    └── QueueManagerAgent
                   │
                   ▼
           graphics_queue
                   │
                   ▼
PRD-0001: Graphics Frontend (React)
                   │
                   ▼
           Korea Production 방송 시스템
```

---

## 7. Implementation Phases

### Phase 0: Infrastructure Extension (1주)

| 작업 | 설명 | 산출물 | 의존성 |
|------|------|--------|--------|
| DB 마이그레이션 | 10개 테이블 생성 | `001_create_caption_tables.sql` | PRD-0001 Phase 1 |
| 이벤트 타입 정의 | 8개 핵심 이벤트 | `caption_events.py` | PRD-0002 Phase 0 |
| Agent 인터페이스 | DataCollectionAgent, GraphicsTriggerAgent | `agents/caption/` | PRD-0002 |

### Phase 1: Pre-Production Pipeline (2주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| PreProductionAgent 구현 | Hendon Mob 크롤링, 수동 입력 UI | P0 |
| Player Profile Import | 배치 임포트, 이미지 다운로드 | P0 |
| Payout Structure Import | CSV 임포트, 수동 편집 | P0 |
| Event/Venue Setup | 토너먼트 기본 정보 입력 | P0 |
| Blind Structure Import | CSV 임포트 | P1 |

### Phase 2: Live Data Pipeline (3주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| LiveDataAgent 구현 | RFID 데이터 수신/파싱 | P0 |
| ChipHistoryTracker | 칩 변동 자동 기록 | P0 |
| BlindLevelTimer | 레벨 자동 전환, 이벤트 발생 | P0 |
| FeatureTableManager | 피처 테이블 플레이어 관리 | P1 |
| Manual Input UI | PA용 수동 입력 인터페이스 | P1 |

### Phase 3: Auto-Generation Pipeline (2주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| AutoGeneratorAgent 구현 | 통계/계산 자동화 | P0 |
| StatsCalculator | VPIP, PFR, 어그레션 계산 | P0 |
| ChipFlowGenerator | 최근 15핸드 차트 데이터 | P0 |
| RankCalculator | 순위 변동, 평균 스택 대비 | P0 |
| PayoutTracker | 현재 버블, 다음 페이점프 | P1 |

### Phase 4: Graphics Trigger Integration (2주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| GraphicsTriggerAgent 구현 | 이벤트-그래픽 매핑 | P0 |
| EventListenerAgent | DB 변경 감지, 이벤트 발생 | P0 |
| QueueManagerAgent | 우선순위 기반 큐 관리 | P0 |
| PRD-0001 Frontend 연동 | WebSocket 그래픽 호출 | P0 |
| 자막별 데이터 포맷터 | 26개 자막 JSON 포맷 | P1 |

### Phase 5: AI Integration & Optimization (2주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| PriorityDecisionAgent | Day별 비율 자동 조절 (GPT) | P1 |
| StoryDetectionAgent 연동 | PRD-0002 AI Agent 통합 | P2 |
| 대시보드 통합 | 실시간 워크플로우 모니터링 | P1 |
| 성능 최적화 | 쿼리 튜닝, 캐싱 전략 | P1 |

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| 데이터 수집 완료율 (Pre) | 100% | 토너먼트 시작 전 필수 데이터 |
| 실시간 데이터 지연 | < 2초 | RFID → DB 반영 시간 |
| 자동 계산 정확도 | > 99% | VPIP/PFR 검증 |
| 그래픽 트리거 성공률 | > 95% | 이벤트 → 그래픽 표시 |
| 자막 데이터 누락률 | < 1% | 필수 필드 누락 비율 |
| PA 수동 입력 시간 | 50%↓ | 자동화 전후 비교 |

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| RFID 데이터 누락 | High | 수동 입력 폴백, 알림 시스템 |
| DB 쿼리 성능 저하 | High | 인덱스 최적화, 읽기 복제본 |
| 잘못된 통계 계산 | Medium | 검증 로직, 수동 오버라이드 |
| 이벤트 중복 발생 | Low | 디바운싱, 중복 체크 |
| 그래픽 큐 과부하 | Medium | 우선순위 관리, 자동 정리 |

---

## 10. Open Questions

1. **RFID 데이터 포맷**: 구체적인 프로토콜 및 필드 정의?
2. **Hendon Mob API**: 크롤링 vs 공식 API 사용 가능 여부?
3. **실시간 통계 임계값**: VPIP 극단 기준 (<10%, >45%) 검증 필요
4. **그래픽 우선순위 규칙**: Day별 비율 외 추가 규칙?
5. **데이터 보관 기간**: chip_history, hand_actions 아카이브 정책?

---

## Appendix

### A. Caption-Data Matrix (Summary)

| 자막 유형 | Pre | Live | Auto | 핵심 테이블 | 주요 트리거 |
|----------|:---:|:----:|:----:|------------|------------|
| Tournament Leaderboard | - | O | O | players, chip_history | hand_completed |
| Feature Table LB | - | O | - | players | feature_table_change |
| Mini Chip Counts | - | O | O | chip_history | chip_update |
| Payouts | O | - | - | payouts | tournament_start |
| Mini Payouts | O | O | - | payouts | elimination |
| Player Profile | O | O | - | player_profiles | player_featured |
| Player Intro Card | O | - | - | player_profiles | player_intro_trigger |
| At Risk | - | O | O | players, payouts | all_in_detected |
| Elimination Banner | - | O | - | players | player_eliminated |
| Commentator Profile | O | - | - | commentators | broadcast_start |
| Heads-Up Comparison | O | O | O | player_stats | heads_up_trigger |
| Chip Flow | - | O | O | chip_history | hand_completed |
| Chip Comparison | - | O | O | chip_history | showdown_start |
| Chips In Play | O | O | - | blind_levels | break_end |
| VPIP Stats | - | O | O | player_stats | stat_threshold |
| Chip Stack Bar | - | O | O | chip_history | feature_table_update |
| Broadcast Schedule | O | - | - | schedules | show_schedule_trigger |
| Event Info | O | O | - | tournaments | tournament_start |
| Venue/Location | O | - | - | venues | venue_shot_trigger |
| Tournament Info | O | O | - | tournaments | day_start |
| Event Name | O | - | - | events | event_name_trigger |
| Blind Level | - | O | - | blind_levels | level_change |
| L-Bar (Standard) | - | O | O | tournaments | always_on |
| L-Bar (Regi Open) | - | O | - | tournaments | registration_open |
| L-Bar (Regi Close) | - | O | - | tournaments | pre_registration_close |
| Transition/Stinger | - | - | - | - | scene_change |

### B. Event Catalog

| Event | Payload | Source | 구독 Agent |
|-------|---------|--------|-----------|
| `hand_completed` | `{hand_number, table_id, winner_id, pot_size}` | RFID Parser | AutoGenerator, GraphicsTrigger |
| `level_change` | `{new_level, blinds, ante, duration}` | Tournament Timer | GraphicsTrigger |
| `player_eliminated` | `{player_id, final_rank, payout}` | RFID + Manual | GraphicsTrigger, DataSync |
| `all_in_detected` | `{player_id, chips, bb_count, payout_at_risk}` | RFID Parser | GraphicsTrigger |
| `feature_table_change` | `{table_number, player_ids}` | Manual (PD) | GraphicsTrigger |
| `itm_reached` | `{remaining_players, bubble_line}` | Tournament Timer | GraphicsTrigger |
| `day_start` | `{day_number, registered, remaining}` | Manual (PD) | GraphicsTrigger |
| `break_end` | `{level_number, chips_in_play}` | Tournament Timer | GraphicsTrigger |

### C. Image References

| Diagram | Path |
|---------|------|
| Caption Data Flow | `docs/images/caption-data-flow.png` |
| Agent Hierarchy | `docs/images/caption-agent-hierarchy.png` |
| DB ERD | `docs/images/caption-db-erd.png` |

### D. Related Documents

- [PRD-0001: WSOP Broadcast Graphics](./0001-prd-wsop-broadcast-graphics.md)
- [PRD-0002: Workflow Automation](./0002-prd-workflow-automation.md)
- [HTML Mockup Guide](../../docs/HTML_MOCKUP_GUIDE.md)

---

**Next Steps**:
1. Open Questions 해결
2. Phase 0: DB 마이그레이션 실행
3. `/issue create` 로 GitHub 이슈 생성
4. Checklist 업데이트: `docs/checklists/PRD-0003.md`
