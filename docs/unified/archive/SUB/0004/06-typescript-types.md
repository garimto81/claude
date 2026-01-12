# PRD-0004 Part 6: TypeScript Type Definitions

**Part 6 of 7** | [← Caption Mapping](./05-caption-mapping.md) | [Migration Guide →](./07-migration-guide.md)

> Index: [PRD-0004](../0004-prd-caption-database-schema.md)

---

## 6. TypeScript Type Definitions

### 6.1 Core Types

```typescript
// types/database.ts

// ID Types
type UUID = string;
type ISO3166Alpha2 = string;  // 'US', 'KR', 'CY', etc.

// Card Types
type Card = string;  // 'Ah', 'Ks', '2d', 'Tc'
type HoleCards = string;  // 'AhKs', 'QdQc'

// Status Types
type TournamentStatus = 'scheduled' | 'running' | 'paused' | 'completed';
type PlayerStatus = 'active' | 'eliminated' | 'away';
type GraphicStatus = 'pending' | 'rendering' | 'displayed' | 'dismissed' | 'failed';
type ContentStatus = 'pending' | 'ready' | 'played' | 'skipped';

// Action Types
type PokerAction = 'fold' | 'call' | 'raise' | 'check' | 'bet' | 'all-in' | 'showdown';
type Street = 'preflop' | 'flop' | 'turn' | 'river';

// GFX Types (pokerGFX 3.2+)
type GFXGameVariant = 'HOLDEM' | 'OMAHA' | 'STUD';
type GFXGameClass = 'FLOP' | 'DRAW' | 'STUD';
type GFXBetStructure = 'NOLIMIT' | 'POTLIMIT' | 'LIMIT';
type GFXEventType = 'FOLD' | 'CALL' | 'CHECK' | 'RAISE' | 'BET' | 'ALL_IN' | 'BOARD CARD' | 'SHOWDOWN';
type GFXAnteType = 'BB_ANTE_BB1ST' | 'ANTE_ALL' | 'NO_ANTE';
type GFXSessionStatus = 'active' | 'closed' | 'archived';

// Graphic Types (26개 자막)
type GraphicType =
  // Leaderboard
  | 'tournament_leaderboard'
  | 'feature_table_leaderboard'
  | 'mini_chip_counts'
  | 'payouts'
  | 'mini_payouts'
  // Player Info
  | 'player_profile'
  | 'player_intro_card'
  | 'at_risk'
  | 'elimination_banner'
  | 'commentator_profile'
  | 'heads_up_comparison'
  // Statistics
  | 'chip_flow'
  | 'chip_comparison'
  | 'chips_in_play'
  | 'vpip_stats'
  | 'chip_stack_bar'
  // Event Graphics
  | 'broadcast_schedule'
  | 'event_info'
  | 'venue_location'
  | 'tournament_info'
  | 'event_name'
  // Transition & L-Bar
  | 'blind_level'
  | 'l_bar_standard'
  | 'l_bar_regi_open'
  | 'l_bar_regi_close'
  | 'transition';

// Trigger Events
type TriggerEvent =
  | 'hand_completed'
  | 'level_change'
  | 'player_eliminated'
  | 'all_in_detected'
  | 'feature_table_change'
  | 'itm_reached'
  | 'day_start'
  | 'break_end'
  | 'registration_closed'
  | 'manual';
```

### 6.2 Entity Interfaces

```typescript
// types/entities.ts

interface Tournament {
  id: UUID;
  eventId: UUID;
  name: string;
  buyIn: number;
  startingChips: number;
  currentLevel: number;
  currentDay: number;
  registeredPlayers: number;
  remainingPlayers: number;
  prizePool: number;
  bubbleLine: number | null;
  isItm: boolean;
  isRegistrationOpen: boolean;
  registrationClosesAt: Date | null;
  avgStack: number | null;
  status: TournamentStatus;
}

interface Player {
  id: UUID;
  tournamentId: UUID;
  name: string;
  nationality: ISO3166Alpha2;
  photoUrl: string | null;
  chips: number;
  seatNumber: number | null;
  tableNumber: number | null;
  isFeatureTable: boolean;
  featureTableId: UUID | null;
  isEliminated: boolean;
  eliminatedAt: Date | null;
  finalRank: number | null;
  payoutReceived: number | null;
  currentRank: number | null;
  rankChange: number;
  bbCount: number | null;
  avgStackPercentage: number | null;
}

interface PlayerProfile {
  id: UUID;
  playerId: UUID;
  hendonMobId: string | null;
  gpiId: string | null;
  wsopBracelets: number;
  wsopRings: number;
  wsopFinalTables: number;
  totalEarnings: number;
  finalTables: number;
  biography: string | null;
  notableWins: NotableWin[];
  hometown: string | null;
  age: number | null;
  profession: string | null;
  socialLinks: SocialLinks;
  isKeyPlayer: boolean;
  keyPlayerReason: string | null;
}

interface PlayerStats {
  id: UUID;
  playerId: UUID;
  tournamentId: UUID;
  handsPlayed: number;
  handsWon: number;
  vpip: number;
  pfr: number;
  aggressionFactor: number | null;
  showdownWinRate: number | null;
  threeBetPercentage: number | null;
  foldToThreeBet: number | null;
  cBetPercentage: number | null;
  allInCount: number;
  allInWon: number;
}

interface ChipHistory {
  id: UUID;
  playerId: UUID;
  tournamentId: UUID;
  handId: UUID | null;
  handNumber: number;
  levelNumber: number;
  chips: number;
  chipsChange: number;
  bbCount: number | null;
  avgStackPercentage: number | null;
  source: 'rfid' | 'manual' | 'csv';
  timestamp: Date;
}

// GFX Session (pokerGFX 세션)
interface GfxSession {
  id: UUID;
  tournamentId: UUID | null;
  featureTableId: UUID | null;
  gfxId: number;  // pokerGFX ID (bigint)
  eventTitle: string | null;
  tableType: 'FEATURE_TABLE' | 'OUTER_TABLE';
  softwareVersion: string | null;
  payouts: number[];
  createdAtGfx: Date;
  importedAt: Date;
  status: GFXSessionStatus;
  totalHands: number;
}

// Hand (GFX 확장)
interface Hand {
  id: UUID;
  gfxSessionId: UUID | null;
  tournamentId: UUID;
  handNumber: number;
  tableNumber: number;
  // GFX Game Info
  gameVariant: GFXGameVariant;
  gameClass: GFXGameClass;
  betStructure: GFXBetStructure;
  // GFX FlopDrawBlinds
  levelNumber: number;
  buttonSeat: number | null;
  smallBlindSeat: number | null;
  smallBlindAmount: number | null;
  bigBlindSeat: number | null;
  bigBlindAmount: number | null;
  anteType: GFXAnteType | null;
  // GFX Run It
  numBoards: number;
  runItNumTimes: number;
  // Pot
  potSize: number;
  rake: number;
  // Result
  winnerId: UUID | null;
  winningHand: string | null;
  // Time (GFX)
  duration: string | null;  // ISO 8601 Duration
  startedAt: Date;
  completedAt: Date | null;
  status: 'in_progress' | 'completed' | 'void';
}

// Hand Player (핸드별 플레이어 상태 - GFX Player 객체)
interface HandPlayer {
  id: UUID;
  handId: UUID;
  playerId: UUID;
  seatNumber: number;
  // GFX Stack
  startStack: number;
  endStack: number;
  cumulativeWinnings: number;
  // GFX HoleCards (변환된 형식)
  holeCards: string | null;
  // GFX Status
  sittingOut: boolean;
  isWinner: boolean;
  // GFX Stats (실시간)
  vpipPercent: number | null;
  pfrPercent: number | null;
  aggressionPercent: number | null;
  wtsdPercent: number | null;
}

// Hand Action (GFX Event 매핑)
interface HandAction {
  id: UUID;
  handId: UUID;
  tournamentId: UUID;
  playerId: UUID | null;  // NULL for BOARD_CARD
  seatNumber: number | null;
  positionName: string | null;
  // GFX Event
  street: Street;
  actionOrder: number;
  action: PokerAction;
  betAmount: number | null;
  potSizeAfter: number | null;
  // GFX Board/Draw
  boardNum: number;
  numCardsDrawn: number;
  timestamp: Date | null;
}

interface Payout {
  id: UUID;
  tournamentId: UUID;
  placeStart: number;
  placeEnd: number;
  amount: number;
  percentage: number | null;
  isCurrentBubble: boolean;
  isReached: boolean;
}

interface BlindLevel {
  id: UUID;
  tournamentId: UUID;
  levelNumber: number;
  smallBlind: number;
  bigBlind: number;
  ante: number;
  bigBlindAnte: number;
  durationMinutes: number;
  isBreak: boolean;
  breakDurationMinutes: number | null;
  isCurrent: boolean;
  startedAt: Date | null;
  endsAt: Date | null;
}

interface Elimination {
  id: UUID;
  tournamentId: UUID;
  playerId: UUID;
  finalRank: number;
  payoutReceived: number | null;
  eliminatedById: UUID | null;
  eliminationHandId: UUID | null;
  playerHoleCards: HoleCards | null;
  eliminatorHoleCards: HoleCards | null;
  wasBroadcast: boolean;
  broadcastAt: Date | null;
  eliminatedAt: Date;
}

interface GraphicsQueueItem {
  id: UUID;
  tournamentId: UUID | null;
  graphicType: GraphicType;
  triggerEvent: TriggerEvent;
  payload: Record<string, unknown>;
  priority: number;
  status: GraphicStatus;
  errorMessage: string | null;
  createdAt: Date;
  renderedAt: Date | null;
  displayedAt: Date | null;
  dismissedAt: Date | null;
}

// Helper Types
interface NotableWin {
  event: string;
  year: number;
  prize: number;
}

interface SocialLinks {
  twitter?: string;
  instagram?: string;
  youtube?: string;
}
```

### 6.3 자막별 Payload Types

```typescript
// types/graphic-payloads.ts

// Leaderboard System
interface TournamentLeaderboardPayload {
  players: Array<{
    rank: number;
    rankChange: number;
    name: string;
    nationality: ISO3166Alpha2;
    chips: number;
    bbCount: number;
  }>;
  totalPlayers: number;
  avgStack: number;
}

interface FeatureTableLeaderboardPayload {
  tables: Array<{
    tableNumber: number;
    tableName: string;
    players: Array<{
      seatNumber: number;
      name: string;
      nationality: ISO3166Alpha2;
      photoUrl: string | null;
      chips: number;
      bbCount: number;
    }>;
  }>;
  currentBlind: {
    smallBlind: number;
    bigBlind: number;
  };
}

interface MiniChipCountsPayload {
  players: Array<{
    name: string;
    nationality: ISO3166Alpha2;
    chips: number;
    chipsChange: number;
    isHighlighted: boolean;
    isPotWinner: boolean;
  }>;
}

interface PayoutsPayload {
  tournament: string;
  totalPrize: number;
  structure: Array<{
    placeStart: number;
    placeEnd: number;
    amount: number;
    percentage: number;
  }>;
  currentBubbleLine: number;
}

// Player Info System
interface PlayerProfilePayload {
  name: string;
  nationality: ISO3166Alpha2;
  photoUrl: string | null;
  currentStack: number;
  wsopBracelets: number;
  totalEarnings: number;
  hometown: string | null;
}

interface AtRiskPayload {
  name: string;
  nationality: ISO3166Alpha2;
  currentStack: number;
  bbCount: number;
  currentRank: number;
  payoutAtRisk: number;
}

interface EliminationBannerPayload {
  name: string;
  nationality: ISO3166Alpha2;
  photoUrl: string | null;
  finalRank: number;
  payoutReceived: number;
  eliminatedBy: string | null;
}

interface HeadsUpComparisonPayload {
  player1: {
    name: string;
    nationality: ISO3166Alpha2;
    photoUrl: string | null;
    chips: number;
    chipPercentage: number;
    wsopBracelets: number;
    totalEarnings: number;
  };
  player2: {
    name: string;
    nationality: ISO3166Alpha2;
    photoUrl: string | null;
    chips: number;
    chipPercentage: number;
    wsopBracelets: number;
    totalEarnings: number;
  };
}

// Statistics
interface ChipFlowPayload {
  playerName: string;
  nationality: ISO3166Alpha2;
  history: Array<{
    handNumber: number;
    chips: number;
    avgPercentage: number;
  }>;
  currentChips: number;
  avgStack: number;
}

interface VPIPStatsPayload {
  playerName: string;
  nationality: ISO3166Alpha2;
  vpip: number;
  pfr: number;
  handsPlayed: number;
}

// Event Graphics
interface BlindLevelPayload {
  currentLevel: number;
  smallBlind: number;
  bigBlind: number;
  ante: number;
  duration: number;
  timeRemaining: number;
  nextLevel: {
    smallBlind: number;
    bigBlind: number;
    ante: number;
  } | null;
}

interface LBarStandardPayload {
  blinds: string;  // "25,000/50,000 (5,000)"
  seatsRemaining: number;
  avgStack: number;
  scheduleInfo: string | null;
}
```

---

**Previous**: [← Part 5: Caption Mapping](./05-caption-mapping.md) | **Next**: [Part 7: Migration Guide →](./07-migration-guide.md)
