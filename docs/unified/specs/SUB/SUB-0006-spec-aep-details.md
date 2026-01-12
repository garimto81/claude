# Part 3: Caption Fields (자막별 데이터 필드 명세)

이 문서는 AEP 분석 결과를 기반으로 각 자막 콤포지션별 동적 레이어와 필요 데이터 필드를 정의합니다.

---

## 3.1 Feature Table Leaderboard

### 콤포지션 정보

| 항목 | MAIN | SUB |
|------|------|-----|
| **콤포지션명** | Feature Table Leaderboard MAIN | Feature Table Leaderboard SUB |
| **해상도** | 1920x1080 | 1920x1080 |
| **레이어 수** | 80개 | 80개 |
| **텍스트 레이어** | 42개 | 41개 |
| **이미지 레이어** | 8개 (Flag) | 9개 (Flag) |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 타입 | 예시 | 데이터 소스 |
|----------|------|------|------|------------|
| Name 1 ~ 8 | player_name | VARCHAR | "DANIEL REZAEI" | DB |
| Chips 1 ~ 8 | chips | VARCHAR | "22,975,000" | CSV/GFX |
| BBs 1 ~ 8 | bb_count | VARCHAR | "114" | 계산 (chips / big_blind) |
| Date 1 ~ 8 | rank | VARCHAR | "1" ~ "8" | DB |
| leaderboard final table | title | VARCHAR | "leaderboard final table" | 고정/수기 |
| WSOP SUPER CIRCUIT CYPRUS | event_name | VARCHAR | "WSOP SUPER CIRCUIT CYPRUS" | DB (events) |

### 이미지 레이어 (동적)

| 레이어명 | 필드 | 설명 | 경로 패턴 |
|----------|------|------|----------|
| Flag 1 ~ 9 | nationality | 국기 이미지 | `Flag/{nationality}.png` |

### 필요 데이터 (8명)

```typescript
interface FeatureTableLeaderboardData {
  event_name: string;           // "WSOP SUPER CIRCUIT CYPRUS"
  table_title: string;          // "leaderboard final table" 또는 "leaderboard table 2"
  players: {
    rank: number;               // 1-8
    name: string;               // "DANIEL REZAEI"
    nationality: string;        // "AT" (ISO 2 code)
    chips: number;              // 22975000
    bb_count: number;           // 114
  }[];
}
```

---

## 3.2 Mini Chip Counts

### 콤포지션 정보

| 항목 | MAIN | SUB |
|------|------|-----|
| **콤포지션명** | _MAIN Mini Chip Count | _SUB_Mini Chip Count |
| **해상도** | 1920x1080 | 1920x1080 |
| **텍스트 레이어** | 21개 | 21개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| name 1 ~ 8 / Name 1 ~ 7 | player_name | "Lipauka" | DB |
| Chip 1 ~ 8 / Chips 1 ~ 7 | chips_with_bb | "2,225,000 (56BB)" | CSV/GFX |
| AVERAGE STACK : ... | avg_stack | "AVERAGE STACK : 6,860,000 (45BB)" | 계산 |

### 필요 데이터

```typescript
interface MiniChipCountData {
  avg_stack: number;            // 6860000
  avg_bb: number;               // 45
  players: {
    name: string;               // "Lipauka"
    chips: number;              // 2225000
    bb_count: number;           // 56
  }[];  // 최대 8명 (MAIN) 또는 7명 (SUB)
}
```

---

## 3.3 Payouts

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Payouts |
| **해상도** | 1920x1080 |
| **텍스트 레이어** | 31개 |
| **이미지 레이어** | 9개 (Flag) |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| Rank 1 ~ 9 | place | "1" ~ "9" | CSV (payouts) |
| prize 1 ~ 9 | amount | "$1,000,000" | CSV (payouts) |
| Total Prize ... | total_prize | "Total Prize $6,860,000" | CSV (tournaments) |
| WSOP SUPER CIRCUIT CYPRUS | event_name | - | DB (events) |

### 필요 데이터

```typescript
interface PayoutsData {
  event_name: string;
  total_prize: number;          // 6860000
  payouts: {
    place: number;              // 1-9
    amount: number;             // 1000000
    nationality?: string;       // 우승자 국적 (확정 시)
  }[];
}
```

---

## 3.4 Mini Payout

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | _Mini Payout |
| **텍스트 레이어** | 29개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 |
|----------|------|------|
| Rank 1 ~ 9 | place | "1" ~ "9" |
| prize 1 ~ 9 | amount | "$1,000,000" |
| Name 9 | last_eliminated | "Georgios Tsouloftas" |
| Total Prize ... | total_prize | "Total Prize $6,860,000" |

---

## 3.5 Event Info

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Event info |
| **텍스트 레이어** | 10개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| WSOP SUPER CIRCUIT CYPRUS | event_name | - | DB (events) |
| Buy-in Fee | buy_in | "$5,300" | CSV (tournaments) |
| Total Fee | prize_pool | "$6,860,000" | CSV (tournaments) |
| Num | entries | "1,372" | CSV (tournaments) |
| % | places_paid | "206TH" | CSV (tournaments) |

### 필요 데이터

```typescript
interface EventInfoData {
  event_name: string;           // "WSOP SUPER CIRCUIT CYPRUS"
  buy_in: number;               // 5300
  prize_pool: number;           // 6860000
  entries: number;              // 1372
  places_paid: number;          // 206
}
```

---

## 3.6 Broadcast Schedule

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Broadcast Schedule |
| **텍스트 레이어** | 23개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| Date 1 ~ 6 | date | "Oct 16" | 수기 (schedules) |
| Event Name 1 ~ 6 | event_title | "MAIN EVENT DAY 1A" | 수기 (schedules) |
| Time 1 ~ 6 | time | "05:10 PM UTC+3" | 수기 (schedules) |
| WSOP SUPER CIRCUIT CYPRUS | series_name | - | DB (events) |

### 필요 데이터 (6개 일정)

```typescript
interface BroadcastScheduleData {
  series_name: string;
  schedules: {
    date: string;               // "Oct 16"
    event_title: string;        // "MAIN EVENT DAY 1A"
    time: string;               // "05:10 PM UTC+3"
  }[];  // 최대 6개
}
```

---

## 3.7 Commentator

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Commentator |
| **텍스트 레이어** | 8개 |
| **이미지 레이어** | 2개 (프로필 사진) |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| Name 1 | commentator_name_1 | "Aaron Paul Kramer" | 수기 (commentators) |
| Name 2 | commentator_name_2 | "Bobby James" | 수기 (commentators) |
| Sub 3 | social_handle_1 | "@aaronpaulkramer" | 수기 (commentators) |
| Sub 4 | social_handle_2 | "@bobbyjamespoker" | 수기 (commentators) |

### 이미지 레이어 (동적)

| 레이어명 | 필드 | 설명 |
|----------|------|------|
| (PSD 파일) | photo_1 | 해설자 1 프로필 사진 |
| (PSD 파일) | photo_2 | 해설자 2 프로필 사진 |

### 필요 데이터

```typescript
interface CommentatorData {
  commentators: {
    name: string;               // "Aaron Paul Kramer"
    social_handle: string;      // "@aaronpaulkramer"
    photo_url: string;          // 프로필 사진 URL
  }[];  // 2명
}
```

---

## 3.8 Location (Venue)

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Location |
| **텍스트 레이어** | 2개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| 2025 wsop super circuit cyprus | series_year_name | "2025 wsop super circuit cyprus" | 수기 (events) |
| merit royal diamond hotel | venue_name | "merit royal diamond hotel" | 수기 (venues) |

---

## 3.9 Chip Flow

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Chip Flow |
| **텍스트 레이어** | 15개 |
| **이미지 레이어** | 1개 (Flag) |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| Player Name | player_name | "REZAEI" | DB |
| max_label | chip_max | "225,000" | GFX (chip_flow) |
| min_label | chip_min | "-1,000" | GFX (chip_flow) |
| input 5_display | current_chips | "224,800" | GFX |
| 하단 라스트 몇 핸드 | hands_label | "LAST 10 HANDS" | 고정/수기 |

> **참고**: Chip Flow 데이터는 주로 GFX에서 실시간 수신 (본 문서 범위 외)

---

## 3.10 Chip Comparison

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Chip Comparison |
| **텍스트 레이어** | 4개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 |
|----------|------|------|
| 플레이어 네임, BB 입력 | player_name_bb | "● alex foxen(67BB)" |
| Others | others_label | "● others" |
| Player % | percentage_label | "payments" |

---

## 3.11 VPIP Stats (Chip VPIP)

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Chip VPIP |
| **텍스트 레이어** | 3개 |
| **이미지 레이어** | 1개 (Flag) |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| Player Name | player_name | "DANIEL REZAEI" | DB |
| % auto | vpip_percentage | 그래프 | GFX (player_stats) |

> **참고**: VPIP 데이터는 GFX에서 실시간 계산 (본 문서 범위 외)

---

## 3.12 Chips In Play

### 콤포지션 정보

| 항목 | x3 | x4 |
|------|-----|-----|
| **콤포지션명** | Chips In Play x3 | Chips In Play x4 |
| **텍스트 레이어** | 4개 | 5개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| Fee 1 ~ 4 | chip_values | "5,000", "25,000", "100,000" | DB/계산 |

---

## 3.13 Elimination Banner

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Elimination |
| **텍스트 레이어** | 2개 |
| **이미지 레이어** | 1개 (Flag) |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| Text 제목 2 | player_name | "Mehmet Dalkilic" | DB/GFX |
| Text 내용 2 | elimination_info | "ELIMINATED IN 10TH PLACE ($64,600)" | GFX (eliminations) |

### 필요 데이터

```typescript
interface EliminationData {
  player_name: string;          // "Mehmet Dalkilic"
  nationality: string;          // "TR"
  final_rank: number;           // 10
  payout: number;               // 64600
}
```

---

## 3.14 At Risk of Elimination

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | At Risk of Elimination |
| **텍스트 레이어** | 1개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| Text 내용 | at_risk_info | "AT RISK OF ELIMINATION - 39TH ($27,700)" | CSV/계산 |

### 필요 데이터

```typescript
interface AtRiskData {
  bubble_rank: number;          // 39
  bubble_payout: number;        // 27700
}
```

---

## 3.15 Player Profile (NAME)

### 콤포지션 정보

| 변형 | 설명 | 텍스트 레이어 |
|------|------|-------------|
| NAME | 2줄 (이름 + 스택) | 2개 |
| NAME 1줄 | 이름만 | 2개 |
| NAME 2줄 (국기 빼고) | 국기 없음 | 2개 |
| NAME 3줄+ | 이름 + 현재/이전 스택 | 2개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 |
|----------|------|------|
| NAME | player_name | "Andrei Spataru" |
| Text 내용 | stack_info | "CURRENT STACK - 3,025,000 (20BB)" |
| Text 내용 2줄 | stack_multi | "CURRENT STACK - 60,500 (24BB)\rPREVIOUS STACK - 21,..." |

### 이미지 레이어

| 레이어명 | 필드 | 설명 |
|----------|------|------|
| (Flag) | nationality | 국기 이미지 |

---

## 3.16 Block Transition Level-Blinds

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Block Transition Level-Blinds |
| **텍스트 레이어** | 12개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| level-1, level-2, level-3 | level_number | "31", "32", "33" | CSV (blind_levels) |
| 75K / 150k ... | blinds_1 | "75K / 150k - 150k (bb)" | CSV (blind_levels) |
| 100K / 200K ... | blinds_2 | "100K / 200K - 200K (bb)" | CSV (blind_levels) |
| 125k / 250k ... | blinds_3 | "125k / 250k - 250k (bb)" | CSV (blind_levels) |
| 60, 61, 62 | duration | "60" (분) | CSV (blind_levels) |

### 필요 데이터 (3개 레벨)

```typescript
interface BlindLevelData {
  levels: {
    level_number: number;       // 31, 32, 33
    small_blind: number;        // 75000, 100000, 125000
    big_blind: number;          // 150000, 200000, 250000
    ante: number;               // 150000, 200000, 250000
    duration: number;           // 60 (분)
  }[];
}
```

---

## 3.17 Event Name

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Event name |
| **텍스트 레이어** | 2개 |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 | 데이터 소스 |
|----------|------|------|------------|
| main event final day | event_title | "main event final day" | 수기 (events) |
| wsop super circuit cyprus | series_name | "wsop super circuit cyprus" | 수기 (events) |

---

## 3.18 Reporter

### 콤포지션 정보

| 항목 | 값 |
|------|-----|
| **콤포지션명** | Reporter |
| **텍스트 레이어** | 3개 |
| **이미지 레이어** | 1개 (프로필 사진) |

### 텍스트 레이어 (동적)

| 레이어명 | 필드 | 예시 |
|----------|------|------|
| Name 1 | reporter_name | "Sample Image" |
| Sub 1 | social_handle | "@sampleimage" |
| Text 제목 4 | title | "Reporter" |

---

## 3.19 데이터 필드 요약

### WSOP+ CSV 필요 필드

| 테이블 | 필드 | 사용 자막 |
|--------|------|----------|
| tournaments | buy_in, prize_pool, entries, places_paid | Event Info |
| blind_levels | level_number, small_blind, big_blind, ante, duration | Block Transition |
| payouts | place, amount | Payouts, Mini Payout, At Risk |

### 수기 입력 필요 필드

| 테이블 | 필드 | 사용 자막 |
|--------|------|----------|
| events | name, series_name | Event Info, Event Name, 모든 자막 헤더 |
| venues | name | Location |
| schedules | date, time, event_title | Broadcast Schedule |
| commentators | name, social_handle, photo_url | Commentator |
| players_master | name, nationality, photo_url | Player Profile, Leaderboard |


---

# Part 4: DB Mapping (wsop 스키마 매핑)

이 문서는 AEP 동적 레이어와 wsop 스키마 테이블 간의 매핑을 정의합니다.

---

## 4.1 매핑 원칙

1. **1:1 매핑**: 각 AEP 레이어는 하나의 DB 필드에 매핑
2. **계산 필드**: BB 수 등 계산이 필요한 필드는 뷰 또는 API에서 처리
3. **포맷 변환**: 숫자 → 문자열 변환 (쉼표, 통화 기호)은 렌더링 시 처리

---

## 4.2 테이블별 매핑

### tournaments

| DB 필드 | AEP 레이어 | 자막 유형 | 변환 |
|---------|-----------|----------|------|
| name | event_title | Event Name | 그대로 |
| buy_in | Buy-in Fee | Event Info | `$` + 쉼표 |
| prize_pool | Total Fee, Total Prize | Event Info, Payouts | `$` + 쉼표 |
| registered_players | Num | Event Info | 쉼표 |
| remaining_players | - | (직접 사용 안 함) | - |
| places_paid | % | Event Info | `TH` 접미사 |
| avg_stack | AVERAGE STACK | Mini Chip Count | 쉼표 + `(BB)` |

### blind_levels

| DB 필드 | AEP 레이어 | 자막 유형 | 변환 |
|---------|-----------|----------|------|
| level_number | level-1, level-2, level-3 | Block Transition | 그대로 |
| small_blind | blinds 첫 번째 값 | Block Transition | `K` 단위 |
| big_blind | blinds 두 번째 값 | Block Transition | `K` 단위 |
| ante | blinds 세 번째 값 | Block Transition | `K` 단위 |
| duration | 60, 61, 62 | Block Transition | 그대로 |

**변환 예시**: `small_blind: 100000` → `"100K / 200K - 200K (bb)"`

### payouts

| DB 필드 | AEP 레이어 | 자막 유형 | 변환 |
|---------|-----------|----------|------|
| place_start | Rank 1~9 | Payouts | 그대로 |
| amount | prize 1~9 | Payouts | `$` + 쉼표 |

### players_master

| DB 필드 | AEP 레이어 | 자막 유형 | 변환 |
|---------|-----------|----------|------|
| name | Name 1~8, NAME | Feature Table LB, Player Profile | 대문자화 |
| nationality | Flag 1~9 | Feature Table LB, Payouts | ISO2 → Flag 파일명 |
| photo_url | (PSD 파일) | Commentator | URL → 파일 다운로드 |

### player_instances

| DB 필드 | AEP 레이어 | 자막 유형 | 변환 |
|---------|-----------|----------|------|
| chips | Chips 1~8 | Feature Table LB | 쉼표 |
| current_rank | Date 1~8 | Feature Table LB | 그대로 |
| seat_number | - | (내부 사용) | - |

**BB 계산**: `chips / big_blind` → `BBs 1~8`

### events

| DB 필드 | AEP 레이어 | 자막 유형 | 변환 |
|---------|-----------|----------|------|
| name | WSOP SUPER CIRCUIT CYPRUS | 모든 자막 헤더 | 대문자화 |

### venues

| DB 필드 | AEP 레이어 | 자막 유형 | 변환 |
|---------|-----------|----------|------|
| name | merit royal diamond hotel | Location | 소문자화 |

### schedules

| DB 필드 | AEP 레이어 | 자막 유형 | 변환 |
|---------|-----------|----------|------|
| date | Date 1~6 | Broadcast Schedule | "Oct 16" 형식 |
| time_start | Time 1~6 | Broadcast Schedule | "05:10 PM UTC+3" 형식 |
| title | Event Name 1~6 | Broadcast Schedule | 대문자화 |

### commentators

| DB 필드 | AEP 레이어 | 자막 유형 | 변환 |
|---------|-----------|----------|------|
| name | Name 1, Name 2 | Commentator | 그대로 |
| social_handle | Sub 3, Sub 4 | Commentator | `@` 접두사 |
| photo_url | (PSD 파일) | Commentator | URL → 파일 |

---

## 4.3 뷰 활용

### v_tournament_leaderboard

Feature Table Leaderboard 자막에서 직접 사용 가능:

```sql
SELECT
    current_rank,           -- Date 1~8
    player_name,            -- Name 1~8
    nationality,            -- Flag 1~8
    chips,                  -- Chips 1~8
    bb_count                -- BBs 1~8 (계산됨)
FROM wsop.v_tournament_leaderboard
WHERE tournament_id = ?
ORDER BY current_rank
LIMIT 8;
```

### v_feature_table_players

Feature Table Leaderboard MAIN/SUB 구분:

```sql
SELECT
    table_number,           -- MAIN=1, SUB=2
    seat_number,
    player_name,
    chips,
    bb_count
FROM wsop.v_feature_table_players
WHERE tournament_id = ?
ORDER BY table_number, chips DESC;
```

---

## 4.4 포맷 변환 규칙

### 숫자 포맷

| 타입 | DB 값 | AEP 레이어 값 |
|------|-------|--------------|
| 칩 수 | 22975000 | "22,975,000" |
| 상금 | 1000000 | "$1,000,000" |
| BB | 114.5 | "114" (반올림) |
| 순위 | 1 | "1" |

### 단위 변환

| 범위 | 변환 | 예시 |
|------|------|------|
| < 1,000 | 그대로 | "500" |
| 1,000 ~ 999,999 | K | "100K" |
| >= 1,000,000 | M | "1M" |

### 블라인드 포맷

```
{small_blind} / {big_blind} - {ante} (bb)

예: 100000 / 200000 - 200000
→ "100K / 200K - 200K (bb)"
```

---

## 4.5 국기 이미지 매핑

### ISO 2 코드 → 파일명

| nationality | 파일명 |
|-------------|--------|
| AT | `Austria.png` 또는 `AT.png` |
| US | `USA.png` |
| GB | `Great Britain.png` 또는 `UK.png` |
| KR | `South Korea.png` |
| CN | `China.png` |
| JP | `Japan.png` |
| RU | `Russia.png` |
| DE | `Germany.png` |
| FR | `France.png` |
| ... | ... |

**경로**: `(Footage)/Flag/{nationality}.png`

### 예외 처리

| nationality | 처리 |
|-------------|------|
| NULL | `Unknown.png` 사용 |
| 알 수 없는 코드 | `Unknown.png` 사용 |

---

## 4.6 API 응답 구조

### Feature Table Leaderboard API

```json
{
  "event_name": "WSOP SUPER CIRCUIT CYPRUS",
  "table_title": "leaderboard final table",
  "big_blind": 200000,
  "players": [
    {
      "rank": 1,
      "name": "DANIEL REZAEI",
      "nationality": "AT",
      "chips": 22975000,
      "chips_formatted": "22,975,000",
      "bb_count": 114
    }
  ]
}
```

### Payouts API

```json
{
  "event_name": "WSOP SUPER CIRCUIT CYPRUS",
  "total_prize": 6860000,
  "total_prize_formatted": "$6,860,000",
  "payouts": [
    {
      "place": 1,
      "amount": 1000000,
      "amount_formatted": "$1,000,000"
    }
  ]
}
```

---

## 4.7 PRD-0004 연계

### 참조 테이블

| 테이블 | PRD-0004 위치 | 본 문서 사용 |
|--------|--------------|-------------|
| wsop.tournaments | Part 3 | Event Info, Payouts |
| wsop.blind_levels | Part 3 | Block Transition |
| wsop.payouts | Part 3 | Payouts, Mini Payout |
| wsop.players_master | Part 3 | Feature Table LB, Player Profile |
| wsop.player_instances | Part 3 | Feature Table LB, Mini Chip Count |
| wsop.events | Part 3 | 모든 자막 헤더 |
| wsop.venues | Part 3 | Location |
| wsop.schedules | Part 3 | Broadcast Schedule |
| wsop.commentators | Part 3 | Commentator |

### 뷰 활용

| 뷰 | PRD-0004 위치 | 본 문서 사용 |
|----|--------------|-------------|
| wsop.v_tournament_leaderboard | Part 7 | Feature Table LB |
| wsop.v_feature_table_players | Part 7 | Feature Table LB MAIN/SUB |
| wsop.v_eliminations | Part 7 | Elimination Banner |


---

# Part 5: Input Guide (데이터 입력 가이드)

이 문서는 WSOP+ CSV 템플릿과 수기 입력 필드 가이드를 제공합니다.

---

## 5.1 WSOP+ CSV 템플릿

### tournaments.csv

```csv
name,buy_in,prize_pool,registered_players,remaining_players,places_paid,avg_stack
"MAIN EVENT",5300,6860000,1372,8,206,857500
```

| 컬럼 | 타입 | 필수 | 설명 | 예시 |
|------|------|:----:|------|------|
| name | TEXT | ✅ | 대회명 | "MAIN EVENT" |
| buy_in | INTEGER | ✅ | 바이인 (달러) | 5300 |
| prize_pool | INTEGER | ✅ | 총 상금 (달러) | 6860000 |
| registered_players | INTEGER | ✅ | 총 참가자 | 1372 |
| remaining_players | INTEGER | ✅ | 남은 참가자 | 8 |
| places_paid | INTEGER | ✅ | 상금 지급 순위 | 206 |
| avg_stack | INTEGER | ❌ | 평균 스택 (계산 가능) | 857500 |

---

### blind_levels.csv

```csv
level_number,small_blind,big_blind,ante,duration
31,75000,150000,150000,60
32,100000,200000,200000,60
33,125000,250000,250000,60
```

| 컬럼 | 타입 | 필수 | 설명 | 예시 |
|------|------|:----:|------|------|
| level_number | INTEGER | ✅ | 레벨 번호 | 32 |
| small_blind | INTEGER | ✅ | 스몰 블라인드 | 100000 |
| big_blind | INTEGER | ✅ | 빅 블라인드 | 200000 |
| ante | INTEGER | ✅ | 앤티 | 200000 |
| duration | INTEGER | ✅ | 레벨 시간 (분) | 60 |

---

### payouts.csv

```csv
place_start,place_end,amount
1,1,1000000
2,2,670000
3,3,475000
4,4,345000
5,5,250000
6,6,185000
7,7,140000
8,8,107500
9,9,82000
```

| 컬럼 | 타입 | 필수 | 설명 | 예시 |
|------|------|:----:|------|------|
| place_start | INTEGER | ✅ | 순위 시작 | 1 |
| place_end | INTEGER | ✅ | 순위 끝 | 1 |
| amount | INTEGER | ✅ | 상금 (달러) | 1000000 |

---

### players.csv (Other Tables)

```csv
name,nationality,chips,current_rank
"DANIEL REZAEI","AT",22975000,1
"BERNARDO NEVES","PT",15375000,2
"ALI KUBASI","LB",12450000,3
```

| 컬럼 | 타입 | 필수 | 설명 | 예시 |
|------|------|:----:|------|------|
| name | TEXT | ✅ | 플레이어 이름 | "DANIEL REZAEI" |
| nationality | TEXT | ✅ | 국적 (ISO 2) | "AT" |
| chips | INTEGER | ✅ | 현재 칩 | 22975000 |
| current_rank | INTEGER | ❌ | 현재 순위 | 1 |

---

## 5.2 수기 입력 필드

### events (이벤트 정보)

| 필드 | 타입 | 필수 | 설명 | 입력 예시 |
|------|------|:----:|------|----------|
| name | TEXT | ✅ | 이벤트명 | "MAIN EVENT FINAL DAY" |
| series_name | TEXT | ✅ | 시리즈명 | "WSOP SUPER CIRCUIT CYPRUS" |
| year | INTEGER | ✅ | 연도 | 2025 |

**담당**: PD

---

### venues (장소 정보)

| 필드 | 타입 | 필수 | 설명 | 입력 예시 |
|------|------|:----:|------|----------|
| name | TEXT | ✅ | 장소명 | "Merit Royal Diamond Hotel" |
| city | TEXT | ❌ | 도시 | "Kyrenia" |
| country | TEXT | ❌ | 국가 | "Cyprus" |

**담당**: PD

---

### schedules (방송 일정)

| 필드 | 타입 | 필수 | 설명 | 입력 예시 |
|------|------|:----:|------|----------|
| date | DATE | ✅ | 방송 날짜 | "2025-10-16" |
| time_start | TIME | ✅ | 시작 시간 | "17:10" |
| timezone | TEXT | ✅ | 타임존 | "UTC+3" |
| title | TEXT | ✅ | 방송 제목 | "MAIN EVENT DAY 1A" |

**담당**: Production Team

**표시 포맷**:
- date: `Oct 16` 형식
- time: `05:10 PM UTC+3` 형식

---

### commentators (해설자)

| 필드 | 타입 | 필수 | 설명 | 입력 예시 |
|------|------|:----:|------|----------|
| name | TEXT | ✅ | 이름 | "Aaron Paul Kramer" |
| social_handle | TEXT | ✅ | SNS 핸들 | "aaronpaulkramer" |
| photo_url | URL | ✅ | 프로필 사진 | "https://..." |
| credentials | TEXT | ❌ | 직함 | "Poker Commentator" |

**담당**: Production Team

**주의**: social_handle에 `@`를 포함하지 않음 (표시 시 자동 추가)

---

### players_master (플레이어 마스터)

| 필드 | 타입 | 필수 | 설명 | 입력 예시 |
|------|------|:----:|------|----------|
| name | TEXT | ✅ | 이름 | "Daniel Rezaei" |
| nationality | TEXT | ✅ | 국적 (ISO 2) | "AT" |
| photo_url | URL | ❌ | 프로필 사진 | "https://..." |
| bracelets | INTEGER | ❌ | WSOP 브레이슬릿 수 | 2 |

**담당**: Data Manager

---

### feature_tables (Feature Table 구성)

| 필드 | 타입 | 필수 | 설명 | 입력 예시 |
|------|------|:----:|------|----------|
| table_number | INTEGER | ✅ | 테이블 번호 (1=MAIN, 2=SUB) | 1 |
| table_name | TEXT | ❌ | 테이블 이름 | "Final Table" |

**담당**: PD

---

### seat_assignment (좌석 배치)

| 필드 | 타입 | 필수 | 설명 | 입력 예시 |
|------|------|:----:|------|----------|
| player_name | TEXT | ✅ | 플레이어 이름 | "Daniel Rezaei" |
| table_number | INTEGER | ✅ | 테이블 번호 | 1 |
| seat_number | INTEGER | ✅ | 좌석 번호 (1-9) | 5 |

**담당**: PA (현장)

---

## 5.3 국적 코드 참조

### 주요 국적 코드 (ISO 3166-1 alpha-2)

| 국가 | 코드 | Flag 파일명 |
|------|------|------------|
| Austria | AT | Austria.png |
| Australia | AU | Australia.png |
| Belgium | BE | Belgium.png |
| Brazil | BR | Brazil.png |
| Canada | CA | Canada.png |
| China | CN | China.png |
| Cyprus | CY | Cyprus.png |
| Czech Republic | CZ | Czech Republic.png |
| Germany | DE | Germany.png |
| Denmark | DK | Denmark.png |
| Spain | ES | Spain.png |
| France | FR | France.png |
| United Kingdom | GB | Great Britain.png |
| Greece | GR | Greece.png |
| Hungary | HU | Hungary.png |
| Ireland | IE | Ireland.png |
| Israel | IL | Israel.png |
| Italy | IT | Italy.png |
| Japan | JP | Japan.png |
| South Korea | KR | South Korea.png |
| Lebanon | LB | lebanon.png |
| Netherlands | NL | Netherlands.png |
| Poland | PL | Poland.png |
| Portugal | PT | Portugal.png |
| Romania | RO | Romania.png |
| Russia | RU | Russia.png |
| Sweden | SE | Sweden.png |
| Turkey | TR | Turkey.png |
| Ukraine | UA | Ukraine.png |
| United States | US | USA.png |

---

## 5.4 입력 검증 규칙

### 필수 필드 검증

| 데이터 | 검증 규칙 |
|--------|----------|
| 국적 코드 | ISO 2 코드 (2자리 대문자) |
| 칩 수 | 양의 정수 |
| 상금 | 양의 정수 |
| 날짜 | YYYY-MM-DD 형식 |
| 시간 | HH:MM 형식 (24시간) |
| URL | http:// 또는 https:// 시작 |

### 중복 검증

| 테이블 | 유니크 키 |
|--------|----------|
| players_master | name + nationality |
| schedules | date + title |
| commentators | name |

---

## 5.5 입력 워크플로우

### 대회 시작 전 (D-1)

```
1. 이벤트 정보 입력 (PD)
   └─ events: name, series_name, year
   └─ venues: name, city, country

2. 일정 입력 (Production)
   └─ schedules: date, time_start, title (6개)

3. 해설자 입력 (Production)
   └─ commentators: name, social_handle, photo_url (2명)

4. 블라인드 구조 CSV 업로드 (Data Manager)
   └─ blind_levels.csv

5. 상금 구조 CSV 업로드 (Data Manager)
   └─ payouts.csv
```

### 대회 시작 (D-Day)

```
1. 플레이어 마스터 확인 (Data Manager)
   └─ players_master: name, nationality

2. Feature Table 구성 (PD)
   └─ feature_tables: table_number, table_name

3. 좌석 배치 (PA)
   └─ seat_assignment: player_name, seat_number
```

### 대회 진행 중

```
1. 칩 카운트 업데이트 (Data Manager)
   └─ players.csv 업로드 (레벨 종료 시)

2. 좌석 변경 (PA)
   └─ seat_assignment 업데이트 (테이블 변경 시)

3. 탈락자 발생 (자동/Data Manager)
   └─ eliminations (GFX에서 자동 또는 수동)
```

---

## 5.6 샘플 데이터

### mini_main.csv (참조)

```csv
플레이어 이름,스택(bb)
"Lipauka","2,225,000 (56BB)"
"Voronin","1,625,000 (41BB)"
"Vos","1,585,000 (40BB)"
"Kalamar","1,465,000 (37BB)"
"Spataru","1,100,000 (28BB)"
"Lukovic","720,000 (18BB)"
"Tlimisov","345,000 (9BB)"
"Katchalov","120,000 (3BB)"
```

> **참고**: 실제 AEP 템플릿의 샘플 CSV 파일 형식

---

## 5.7 주의사항

### 데이터 충돌 방지

1. **Feature Table 플레이어 칩**: GFX에서 실시간 수신되므로 CSV로 덮어쓰지 않음
2. **Other Table 플레이어 칩**: CSV로만 업데이트
3. **좌석 배치**: PA만 수정 권한

### 포맷 주의

1. **이름**: 따옴표로 감싸기 (쉼표 포함 가능)
2. **숫자**: 쉼표 없이 입력 (포맷은 시스템에서 처리)
3. **국적**: 대문자 2자리 (AT, US, GB 등)

### 업로드 타이밍

1. **blind_levels.csv**: 대회 시작 전 1회
2. **payouts.csv**: 대회 시작 전 1회
3. **players.csv**: 레벨 종료 시마다 (Feature Table 제외)


---