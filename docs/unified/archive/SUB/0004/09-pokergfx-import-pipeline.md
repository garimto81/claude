# PRD-0004 Part 9: pokerGFX Import Pipeline

**Part 9 of 9** | [← Supabase Integration](./08-supabase-integration.md)

> Index: [PRD-0004](../0004-prd-caption-database-schema.md)

---

**PRD Number**: PRD-0004
**Version**: 1.3
**Date**: 2026-01-08
**Status**: Draft
**Parent PRD**: PRD-0003, PRD-0001

---

## 9. pokerGFX Import Pipeline

### 9.1 JSON 구조 → DB 매핑 Overview

```
pokerGFX JSON
    │
    ├── Session Level
    │   └── gfx_sessions
    │
    ├── Hand Level
    │   └── hands
    │
    ├── Player Level (per Hand)
    │   ├── players_master (UPSERT)
    │   ├── player_instances (UPSERT)
    │   ├── hand_players
    │   └── player_stats (UPDATE)
    │
    ├── Event Level (Actions)
    │   ├── hand_actions
    │   └── hand_cards (BOARD_CARD events)
    │
    └── Derived
        ├── chip_flow (chips_after - chips_before)
        └── eliminations (if EliminationRank present)
```

### 9.2 필드 매핑 상세

#### Session → gfx_sessions

| GFX 필드 | DB 컬럼 | 변환 | 예시 |
|----------|---------|------|------|
| `ID` | `gfx_id` | BIGINT | 638961999170907267 |
| `CreatedDateTimeUTC` | `created_at_gfx` | ISO8601 → TIMESTAMPTZ | 2025-10-16T08:25:17Z |
| `EventTitle` | `event_title` | VARCHAR(255) | "WSOP Main Event Day 3" |
| `Type` | `table_type` | VARCHAR(50) | "FEATURE_TABLE" |
| `SoftwareVersion` | `software_version` | VARCHAR(50) | "PokerGFX 3.2" |
| `Payouts` | `payouts` | JSONB | [0,0,0,0,0,0,0,0,0,0] |

#### Hand → hands

| GFX 필드 | DB 컬럼 | 변환 | 예시 |
|----------|---------|------|------|
| `HandNum` | `hand_number` | INTEGER | 2 |
| `GameVariant` | `game_variant` | VARCHAR(20) | "HOLDEM" |
| `GameClass` | `game_class` | VARCHAR(20) | "FLOP" |
| `BetStructure` | `bet_structure` | VARCHAR(20) | "NOLIMIT" |
| `Duration` | `duration` | ISO8601 → INTERVAL | "PT2M56S" → 00:02:56 |
| `StartDateTimeUTC` | `started_at` | TIMESTAMPTZ | 2025-10-16T08:28:43Z |
| `FlopDrawBlinds.BlindLevel` | `level_number` | INTEGER | 15 |
| `FlopDrawBlinds.ButtonPlayerNum` | `button_seat` | INTEGER | 2 |
| `FlopDrawBlinds.SmallBlindPlayerNum` | `small_blind_seat` | INTEGER | 3 |
| `FlopDrawBlinds.SmallBlindAmt` | `small_blind_amount` | DECIMAL | 50000 |
| `FlopDrawBlinds.BigBlindPlayerNum` | `big_blind_seat` | INTEGER | 4 |
| `FlopDrawBlinds.BigBlindAmt` | `big_blind_amount` | DECIMAL | 100000 |
| `FlopDrawBlinds.AnteType` | `ante_type` | VARCHAR(30) | "BB_ANTE_BB1ST" |
| `NumBoards` | `num_boards` | INTEGER | 1 |
| `RunItNumTimes` | `run_it_num_times` | INTEGER | 1 |

#### Player → hand_players

| GFX 필드 | DB 컬럼 | 변환 | 예시 |
|----------|---------|------|------|
| `PlayerNum` | `seat_number` | INTEGER | 7 |
| `Name` | → `players_master.name` | VARCHAR | "Phil Ivey" |
| `StartStackAmt` | `start_stack` | BIGINT | 9000000 |
| `EndStackAmt` | `end_stack` | BIGINT | 12500000 |
| `HoleCards` | `hole_cards` | 변환 필요 | ["as","kh"] → "AsKh" |
| `CumulativeWinningsAmt` | `cumulative_winnings` | BIGINT | 3500000 |
| `SittingOut` | `sitting_out` | BOOLEAN | false |
| `VPIPPercent` | `vpip_percent` | DECIMAL(5,2) | 28.5 |
| `PreFlopRaisePercent` | `pfr_percent` | DECIMAL(5,2) | 22.0 |
| `AggressionFrequencyPercent` | `aggression_percent` | DECIMAL(5,2) | 45.0 |
| `WentToShowDownPercent` | `wtsd_percent` | DECIMAL(5,2) | 35.0 |

#### Event → hand_actions

| GFX 필드 | DB 컬럼 | 변환 | 예시 |
|----------|---------|------|------|
| `EventType` | `action` | lowercase 변환 | "RAISE" → "raise" |
| `PlayerNum` | `seat_number` | INTEGER | 5 |
| `BetAmt` | `bet_amount` | DECIMAL | 180000 |
| `Pot` | `pot_size_after` | DECIMAL | 370000 |
| `DateTimeUTC` | `action_time` | TIMESTAMPTZ | 2025-10-16T08:29:15Z |
| `BoardNum` | `board_num` | INTEGER | 1 |
| `NumCardsDrawn` | `num_cards_drawn` | INTEGER | null |

### 9.3 카드 형식 변환

#### 변환 규칙

```python
def convert_gfx_card(gfx_card: str) -> str:
    """
    pokerGFX: 'as', 'kh', '10d', 'jc'
    DB/phevaluator: 'As', 'Kh', 'Td', 'Jc'
    """
    if not gfx_card or len(gfx_card) < 2:
        return None

    rank = gfx_card[:-1].upper()
    suit = gfx_card[-1].lower()

    if rank == '10':
        rank = 'T'

    return f"{rank}{suit}"

def convert_hole_cards(gfx_cards: list) -> str:
    """
    ['as', 'kh'] → 'AsKh'
    """
    if not gfx_cards or len(gfx_cards) < 2:
        return None

    return ''.join(convert_gfx_card(c) for c in gfx_cards[:2])
```

#### SQL 함수 (이미 배포됨)

```sql
-- wsop.convert_gfx_card('as') → 'As'
-- wsop.convert_gfx_card('10d') → 'Td'
-- wsop.convert_gfx_hole_cards('["as", "kh"]'::JSONB) → 'AsKh'
```

### 9.4 UPSERT 전략

#### gfx_sessions (gfx_id 기준)

```sql
INSERT INTO wsop.gfx_sessions (gfx_id, event_title, table_type, ...)
VALUES ($1, $2, $3, ...)
ON CONFLICT (gfx_id) DO UPDATE SET
    event_title = EXCLUDED.event_title,
    total_hands = EXCLUDED.total_hands,
    updated_at = NOW();
```

#### players_master (name + nationality 기준)

```sql
-- 함수 사용 권장
SELECT wsop.get_or_create_player_master('Phil Ivey', 'US');
```

#### hands (gfx_session_id + hand_number 기준)

```sql
INSERT INTO wsop.hands (gfx_session_id, hand_number, ...)
VALUES ($1, $2, ...)
ON CONFLICT (gfx_session_id, hand_number) DO UPDATE SET
    status = 'completed',
    final_pot = EXCLUDED.final_pot,
    ...;
```

### 9.5 Python 구현 예시

```python
from supabase import create_client
from typing import Dict, Any
import json

class PokerGFXImporter:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)

    async def import_session(self, gfx_json: Dict[str, Any]) -> str:
        """전체 GFX 세션 임포트"""

        # 1. gfx_sessions UPSERT
        session_data = {
            'gfx_id': gfx_json['ID'],
            'event_title': gfx_json.get('EventTitle'),
            'table_type': gfx_json.get('Type', 'FEATURE_TABLE'),
            'software_version': gfx_json.get('SoftwareVersion'),
            'payouts': gfx_json.get('Payouts', []),
            'total_hands': len(gfx_json.get('Hands', [])),
            'created_at_gfx': gfx_json.get('CreatedDateTimeUTC')
        }

        result = self.supabase.table('wsop.gfx_sessions').upsert(
            session_data, on_conflict='gfx_id'
        ).execute()

        session_id = result.data[0]['id']

        # 2. 각 핸드 처리
        for hand in gfx_json.get('Hands', []):
            await self._import_hand(session_id, hand)

        return session_id

    async def _import_hand(self, session_id: str, hand: Dict) -> str:
        """개별 핸드 임포트"""

        blinds = hand.get('FlopDrawBlinds', {})

        hand_data = {
            'gfx_session_id': session_id,
            'hand_number': hand['HandNum'],
            'game_variant': hand.get('GameVariant', 'HOLDEM'),
            'game_class': hand.get('GameClass', 'FLOP'),
            'bet_structure': hand.get('BetStructure', 'NOLIMIT'),
            'level_number': blinds.get('BlindLevel'),
            'button_seat': blinds.get('ButtonPlayerNum'),
            'small_blind_seat': blinds.get('SmallBlindPlayerNum'),
            'small_blind_amount': blinds.get('SmallBlindAmt'),
            'big_blind_seat': blinds.get('BigBlindPlayerNum'),
            'big_blind_amount': blinds.get('BigBlindAmt'),
            'ante_type': blinds.get('AnteType'),
            'started_at': hand.get('StartDateTimeUTC'),
            'status': 'completed'
        }

        result = self.supabase.table('wsop.hands').upsert(
            hand_data, on_conflict='gfx_session_id,hand_number'
        ).execute()

        hand_id = result.data[0]['id']

        # 3. 플레이어 처리
        for player in hand.get('Players', []):
            await self._import_hand_player(hand_id, player)

        # 4. 액션 처리
        for idx, event in enumerate(hand.get('Events', [])):
            await self._import_action(hand_id, event, idx)

        return hand_id

    def _convert_hole_cards(self, cards: list) -> str:
        """홀카드 변환"""
        if not cards or len(cards) < 2:
            return None

        def convert_card(c):
            rank = c[:-1].upper()
            suit = c[-1].lower()
            if rank == '10':
                rank = 'T'
            return f"{rank}{suit}"

        return ''.join(convert_card(c) for c in cards[:2])
```

### 9.6 데이터 흐름 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    pokerGFX JSON File                       │
│  {"ID": 638..., "Hands": [{...}], ...}                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Import Pipeline                          │
│  1. Parse JSON                                              │
│  2. Validate required fields                                │
│  3. Transform data types                                    │
│  4. UPSERT to Supabase                                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ gfx_sessions  │    │    hands      │    │ hand_players  │
│ (1 per file)  │    │ (N per file)  │    │ (M per hand)  │
└───────────────┘    └───────────────┘    └───────────────┘
                              │
                              │ Triggers
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Derived Data                             │
│  • chip_flow (from start_stack, end_stack)                 │
│  • player_stats (aggregate VPIP, PFR)                       │
│  • eliminations (if EliminationRank present)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   graphics_queue                            │
│  자막 렌더링 요청 자동 생성                                  │
└─────────────────────────────────────────────────────────────┘
```

### 9.7 에러 핸들링

| 에러 유형 | 처리 방법 |
|----------|----------|
| JSON 파싱 실패 | 로그 기록 후 스킵 |
| 필수 필드 누락 | ValidationError 발생 |
| FK 참조 실패 | 부모 레코드 먼저 생성 후 재시도 |
| UNIQUE 충돌 | UPSERT로 자동 처리 |
| 트랜잭션 실패 | 롤백 후 재시도 (3회) |

### 9.8 검증 체크리스트

```python
def validate_gfx_json(data: dict) -> bool:
    """GFX JSON 유효성 검사"""
    required = ['ID', 'CreatedDateTimeUTC']
    for field in required:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    if 'Hands' in data:
        for hand in data['Hands']:
            validate_hand(hand)

    return True

def validate_hand(hand: dict) -> bool:
    required = ['HandNum']
    for field in required:
        if field not in hand:
            raise ValidationError(f"Hand missing: {field}")
    return True
```

---

**[← Back to Index](../0004-prd-caption-database-schema.md)**
