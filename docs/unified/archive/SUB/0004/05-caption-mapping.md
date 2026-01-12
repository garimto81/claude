# PRD-0004 Part 5: Caption Mapping

**Part 5 of 7** | [← GFX Tables](./04-gfx-tables.md) | [TypeScript Types →](./06-typescript-types.md)

> Index: [PRD-0004](../0004-prd-caption-database-schema.md)

---

## 5. 26개 자막 유형 - 테이블 매핑

### 5.1 Complete Mapping Matrix

| # | 자막 유형 | 핵심 테이블 | 보조 테이블 | 데이터 소스 |
|---|----------|------------|------------|------------|
| **Leaderboard System** |
| 1 | Tournament Leaderboard | `players` | `chip_history`, `tournaments` | Live + Auto |
| 2 | Feature Table LB | `players` | `feature_tables`, `player_profiles` | Live |
| 3 | Mini Chip Counts | `chip_history` | `players` | Live + Auto |
| 4 | Payouts | `payouts` | `tournaments` | Pre |
| 5 | Mini Payouts | `payouts` | `eliminations` | Pre + Live |
| **Player Info System** |
| 6 | Player Profile | `player_profiles` | `players`, `player_stats` | Pre + Live |
| 7 | Player Intro Card | `player_profiles` | `soft_contents` | Pre |
| 8 | At Risk of Elimination | `players` | `payouts` | Live + Auto |
| 9 | Elimination Banner | `eliminations` | `players`, `hands` | Live |
| 10 | Commentator Profile | `commentators` | - | Pre |
| 11 | Heads-Up Comparison | `players` | `player_profiles`, `player_stats`, `chip_history` | Pre + Live + Auto |
| **Statistics** |
| 12 | Chip Flow | `chip_history` | `hands`, `tournaments` | Live + Auto |
| 13 | Chip Comparison | `chip_history` | `players`, `hand_actions` | Live + Auto |
| 14 | Chips In Play | `blind_levels` | `tournaments` | Pre + Live |
| 15 | VPIP Stats | `player_stats` | `hand_actions` | Live + Auto |
| 16 | Chip Stack Bar | `players` | `chip_history` | Live + Auto |
| **Event Graphics** |
| 17 | Broadcast Schedule | `schedules` | `events` | Pre |
| 18 | Event Info | `tournaments` | `events` | Pre + Live |
| 19 | Venue/Location | `venues` | `events` | Pre |
| 20 | Tournament Info | `tournaments` | `blind_levels` | Pre + Live |
| 21 | Event Name | `events` | - | Pre |
| **Transition & L-Bar** |
| 22 | Blind Level | `blind_levels` | `tournaments` | Live |
| 23 | L-Bar (Standard) | `tournaments` | `blind_levels`, `schedules` | Live + Auto |
| 24 | L-Bar (Regi Open) | `tournaments` | - | Live |
| 25 | L-Bar (Regi Close) | `tournaments` | - | Live |
| 26 | Transition/Stinger | `graphics_queue` | `players` | - |

### 5.2 데이터 소스별 테이블

#### pokerGFX JSON (RFID)
- `hands` (Feature Table 핸드)
- `hand_actions` (액션 로그)
- `community_cards` (커뮤니티 카드)
- `chip_history` (Feature Table 플레이어만)

#### WSOP+ CSV
- `tournaments` (대회 정보)
- `players` (Other Tables 칩/순위)
- `payouts` (상금 구조)
- `blind_levels` (블라인드 레벨)

#### 수기 입력
- `player_profiles` (프로필 상세)
- `commentators` (코멘테이터)
- `events`, `venues` (이벤트/장소)
- `schedules` (방송 스케줄)
- `feature_tables` (피처 테이블 지정)
- `soft_contents` (소프트 콘텐츠)

---

**Previous**: [← Part 4: GFX Tables](./04-gfx-tables.md) | **Next**: [Part 6: TypeScript Types →](./06-typescript-types.md)
