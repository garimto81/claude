# PRD-0004 Part 2: Data Source Integration

**Part 2 of 7** | [← Overview](./01-overview.md) | [Database Schema →](./03-database-schema.md)

> Index: [PRD-0004](../0004-prd-caption-database-schema.md)

---

## 2. Data Source Integration

### 2.1 3가지 데이터 소스 (상호 배타적)

| 소스 | 범위 | 데이터 유형 | 지연 시간 |
|------|------|------------|----------|
| **pokerGFX JSON** | Feature Table 전용 | RFID 핸드/카드/칩 데이터 | < 2초 |
| **WSOP+ CSV** | 대회 정보 + Other Tables | 순위, 상금, 블라인드 | 수동 |
| **수기 입력** | 자동화 불가 정보 | 프로필, 좌석, 코멘테이터 | 수동 |

### 2.2 pokerGFX JSON 스키마 상세

> **Source**: PokerGFX 3.2+ (Enterprise/Pro License)

#### 2.2.1 최상위 구조 (Session)

```json
{
  "CreatedDateTimeUTC": "2025-10-16T08:25:17.0907267Z",
  "EventTitle": "WSOP Main Event Day 3",
  "Hands": [...],
  "ID": 638961999170907267,
  "Payouts": [0,0,0,0,0,0,0,0,0,0],
  "SoftwareVersion": "PokerGFX 3.2",
  "Type": "FEATURE_TABLE"
}
```

| 필드 | 타입 | DB 컬럼 | 설명 |
|------|------|---------|------|
| `ID` | number | `gfx_sessions.gfx_id` | 세션 고유 ID |
| `CreatedDateTimeUTC` | string | `gfx_sessions.created_at_gfx` | 세션 생성 시간 (ISO 8601) |
| `EventTitle` | string | `gfx_sessions.event_title` | 이벤트 제목 |
| `Type` | string | `gfx_sessions.table_type` | 테이블 타입 (FEATURE_TABLE) |
| `SoftwareVersion` | string | `gfx_sessions.software_version` | PokerGFX 버전 |
| `Hands` | array | → `hands` 테이블 | 핸드 객체 배열 |
| `Payouts` | array | `gfx_sessions.payouts` | 페이아웃 배열 (JSONB) |

#### 2.2.2 Hand 객체

```json
{
  "HandNum": 2,
  "GameVariant": "HOLDEM",
  "GameClass": "FLOP",
  "BetStructure": "NOLIMIT",
  "Duration": "PT2M56.2628165S",
  "StartDateTimeUTC": "2025-10-16T08:28:43.2539856Z",
  "NumBoards": 1,
  "RunItNumTimes": 1,
  "Players": [...],
  "Events": [...],
  "FlopDrawBlinds": {...}
}
```

| 필드 | 타입 | DB 컬럼 | 설명 |
|------|------|---------|------|
| `HandNum` | number | `hands.hand_number` | 핸드 번호 |
| `GameVariant` | string | `hands.game_variant` | 게임 종류 (HOLDEM, OMAHA) |
| `GameClass` | string | `hands.game_class` | 게임 클래스 (FLOP, DRAW) |
| `BetStructure` | string | `hands.bet_structure` | 베팅 구조 (NOLIMIT, POTLIMIT, LIMIT) |
| `Duration` | string | `hands.duration` | 핸드 진행 시간 (ISO 8601 Duration) |
| `StartDateTimeUTC` | string | `hands.started_at` | 핸드 시작 시간 |
| `NumBoards` | number | `hands.num_boards` | 보드 수 (Run It Twice 등) |
| `RunItNumTimes` | number | `hands.run_it_num_times` | Run It 횟수 |

#### 2.2.3 Player 객체 (핸드 내)

```json
{
  "PlayerNum": 7,
  "Name": "Phil Ivey",
  "LongName": "Phillip Dennis Ivey Jr.",
  "StartStackAmt": 9000000,
  "EndStackAmt": 12500000,
  "CumulativeWinningsAmt": 3500000,
  "HoleCards": ["as", "kh"],
  "SittingOut": false,
  "EliminationRank": -1,
  "VPIPPercent": 28.5,
  "PreFlopRaisePercent": 22.3,
  "AggressionFrequencyPercent": 45.2,
  "WentToShowDownPercent": 31.0
}
```

| 필드 | 타입 | DB 컬럼 | 설명 |
|------|------|---------|------|
| `PlayerNum` | number | `hand_players.seat_number` | 시트 번호 (1-10) |
| `Name` | string | `players.name` | 플레이어 이름 |
| `LongName` | string | `player_profiles.long_name` | 플레이어 전체 이름 |
| `StartStackAmt` | number | `hand_players.start_stack` | 핸드 시작 스택 |
| `EndStackAmt` | number | `hand_players.end_stack` | 핸드 종료 스택 |
| `CumulativeWinningsAmt` | number | `hand_players.cumulative_winnings` | 누적 수익 |
| `HoleCards` | array | `hand_players.hole_cards` | 홀 카드 (2장) |
| `SittingOut` | boolean | `hand_players.sitting_out` | 자리 비움 여부 |
| `EliminationRank` | number | `eliminations.final_rank` | 탈락 순위 (-1: 미탈락) |
| `VPIPPercent` | number | `player_stats.vpip` | VPIP 통계 |
| `PreFlopRaisePercent` | number | `player_stats.pfr` | PFR 통계 |
| `AggressionFrequencyPercent` | number | `player_stats.aggression_factor` | AF 통계 |
| `WentToShowDownPercent` | number | `player_stats.showdown_win_rate` | WTSD 통계 |

#### 2.2.4 Event 객체 (액션)

```json
{
  "EventType": "RAISE",
  "PlayerNum": 5,
  "BetAmt": 180000,
  "Pot": 370000,
  "BoardCards": null,
  "BoardNum": 0,
  "DateTimeUTC": "2025-10-16T08:29:15.123Z",
  "NumCardsDrawn": 0
}
```

| 필드 | 타입 | DB 컬럼 | 설명 |
|------|------|---------|------|
| `EventType` | string | `hand_actions.action` | 이벤트 타입 (아래 참조) |
| `PlayerNum` | number | `hand_actions.seat_number` | 플레이어 시트 번호 |
| `BetAmt` | number | `hand_actions.bet_amount` | 베팅 금액 |
| `Pot` | number | `hand_actions.pot_size_after` | 현재 팟 |
| `BoardCards` | array | → `community_cards` | 보드 카드 (BOARD_CARD 이벤트 시) |
| `BoardNum` | number | `community_cards.board_num` | 보드 번호 (Run It Twice) |
| `DateTimeUTC` | string | `hand_actions.timestamp` | 이벤트 시간 |
| `NumCardsDrawn` | number | `hand_actions.num_cards_drawn` | 드로우한 카드 수 |

**EventType 매핑**:

| GFX EventType | DB action | 설명 |
|---------------|-----------|------|
| `FOLD` | `fold` | 폴드 |
| `CALL` | `call` | 콜 |
| `CHECK` | `check` | 체크 |
| `RAISE` | `raise` | 레이즈 |
| `BET` | `bet` | 베팅 |
| `ALL_IN` | `all-in` | 올인 |
| `BOARD CARD` | - | 보드 카드 공개 (→ community_cards) |
| `SHOWDOWN` | `showdown` | 쇼다운 |

#### 2.2.5 FlopDrawBlinds 객체

```json
{
  "ButtonPlayerNum": 2,
  "SmallBlindPlayerNum": 3,
  "SmallBlindAmt": 50000,
  "BigBlindPlayerNum": 4,
  "BigBlindAmt": 100000,
  "AnteType": "BB_ANTE_BB1ST",
  "BlindLevel": 15
}
```

| 필드 | 타입 | DB 컬럼 | 설명 |
|------|------|---------|------|
| `ButtonPlayerNum` | number | `hands.button_seat` | 버튼 위치 |
| `SmallBlindPlayerNum` | number | `hands.small_blind_seat` | SB 위치 |
| `SmallBlindAmt` | number | `hands.small_blind_amount` | SB 금액 |
| `BigBlindPlayerNum` | number | `hands.big_blind_seat` | BB 위치 |
| `BigBlindAmt` | number | `hands.big_blind_amount` | BB 금액 |
| `AnteType` | string | `hands.ante_type` | 앤티 타입 |
| `BlindLevel` | number | `hands.level_number` | 블라인드 레벨 |

### 2.3 카드 형식 변환

pokerGFX와 내부 DB/phevaluator 간 카드 형식 변환:

| 구분 | pokerGFX | DB 저장 | phevaluator |
|------|----------|---------|-------------|
| **Rank** | 소문자 (a, k, q, j, 10) | 대문자 (A, K, Q, J, T) | 대문자 |
| **Suit** | 소문자 (h, d, c, s) | 소문자 | 소문자 |
| **예시** | `as`, `kh`, `10d`, `jc` | `As`, `Kh`, `Td`, `Jc` | `As`, `Kh`, `Td`, `Jc` |

**변환 규칙**:
1. Rank 첫 글자 대문자로 변환
2. `10` → `T` 변환
3. Suit는 소문자 유지

```python
def convert_gfx_card(gfx_card: str) -> str:
    """pokerGFX 카드 형식을 DB/phevaluator 형식으로 변환"""
    rank = gfx_card[:-1].upper()
    suit = gfx_card[-1].lower()
    if rank == '10':
        rank = 'T'
    return f"{rank}{suit}"
```

### 2.4 테이블별 소스 매핑

```
┌─────────────────────────────────────────────────────────────────┐
│                    데이터 소스 → 테이블 매핑                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  pokerGFX JSON (RFID)          WSOP+ CSV            수기 입력     │
│  ─────────────────────        ─────────────        ────────────  │
│  ┌─────────────────┐          ┌───────────┐       ┌───────────┐  │
│  │ hand_actions    │          │tournaments│       │player_    │  │
│  │ (Feature Table) │          │           │       │profiles   │  │
│  └────────┬────────┘          └─────┬─────┘       └─────┬─────┘  │
│           │                         │                   │        │
│  ┌────────▼────────┐          ┌─────▼─────┐       ┌─────▼─────┐  │
│  │ chip_history    │          │ payouts   │       │commentators│ │
│  │ (Feature Only)  │          │           │       │           │  │
│  └────────┬────────┘          └─────┬─────┘       └─────┬─────┘  │
│           │                         │                   │        │
│  ┌────────▼────────┐          ┌─────▼─────┐       ┌─────▼─────┐  │
│  │ community_cards │          │blind_     │       │ events    │  │
│  │                 │          │levels     │       │ venues    │  │
│  └─────────────────┘          └───────────┘       └───────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

**Previous**: [← Part 1: Overview](./01-overview.md) | **Next**: [Part 3: Database Schema →](./03-database-schema.md)
