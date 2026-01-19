# PRD-0006: WSOPTV Advanced Mode

| 항목 | 값 |
|------|---|
| **Version** | 3.0 |
| **Status** | Draft |
| **Priority** | P0 |
| **Created** | 2026-01-15 |
| **Updated** | 2026-01-19 |
| **Author** | Claude Code |
| **Source** | michael_note.md, michael_vision_analysis.md, NBA TV 분석 리포트 |

---

## Executive Summary

WSOP TV의 프리미엄 시청 경험을 제공하는 **Advanced Mode** 기능 정의. Plus+ ($50) 구독자 전용으로 **NBA TV/League Pass의 검증된 UX를 1:1 매핑**하여 세계적 수준의 스포츠 스트리밍 경험을 제공합니다.

### 핵심 전략

> **"NBA TV/League Pass의 레이아웃, 위치, 양식을 WSOPTV에 1:1 매핑하여 동일하게 설계"**

### 핵심 목표

- **NBA 스타일 레이아웃**: Tournament Strip, 4분할 Multiview, Key Hands 등 검증된 UX 완전 채택
- **3계층 동적 Multi-view**: PGM → 피처 테이블 → PlayerCAM 레이어 구조로 몰입감 극대화
- **StatsView 2가지 구조**: GGPoker HUD 연동 (MVP) + 대회 실시간 연동 (Phase 2)
- Plus+ 구독의 가치 제안 확립

---

## NBA TV → WSOPTV 1:1 매핑 테이블

> **참조**: [REPORT-2026-01-19 NBA TV 분석](../reports/REPORT-2026-01-19-nbatv-reference-analysis.md)

### 전체 레이아웃 구조

| NBA TV 요소 | 위치 | WSOPTV 대응 | 변환 |
|------------|------|-------------|------|
| **Score Strip** | 최상단 가로 | **Tournament Strip** | 경기 점수 → 테이블 POT/Blinds |
| **League Pass Banner** | Score Strip 하단 | **Plus+ CTA Banner** | 구독 유도 |
| **Hero Section** | 메인 중앙 | **Featured Event** | 주요 경기 → 메인 이벤트 |
| **Headlines** | 우측 사이드바 | **Poker Headlines** | 뉴스 피드 |
| **Stories** | 콘텐츠 상단 | **Live Tables** | LIVE 배지 + 썸네일 |
| **Trending Now** | 콘텐츠 중단 | **Trending Hands** | 인기 동영상 |
| **Game Recaps** | 콘텐츠 하단 | **Tournament Recaps** | 요약본 |

### 플레이어 UI (동영상 재생 화면)

| NBA TV 요소 | 위치 | WSOPTV 대응 |
|------------|------|-------------|
| **Video Player** | 중앙 16:9 | **Table View** |
| **Streams Button** | 좌측 하단 | **Tables Button** |
| **MultiView Button** | 하단 중앙 좌 | **MultiView Button** |
| **Key Plays Button** | 하단 중앙 우 | **Key Hands Button** |
| **Layout Buttons** | 하단 우측 | **1/2/4 Layout** |
| **LIVE Badge** | 우측 상단 | **LIVE Badge** |

### Multiview 레이아웃

| NBA TV | WSOPTV |
|--------|--------|
| 2분할 (좌/우) | 2분할 (메인 테이블/서브 테이블) |
| 4분할 그리드 | 4분할 (4개 테이블) |
| "Add a Game from Score Strip" | "Add Table from Tournament Strip" |
| 오디오 활성 표시 (🔊) | 동일 |
| Score Overlay (팀 점수/시간) | POT/Blinds Overlay |

### Streaming Options 모달

| NBA TV 탭 | WSOPTV 탭 |
|-----------|-----------|
| **Broadcasts** | **Views** |
| - Lakers (In-Arena) | - Table View (딜러 시점) |
| - Raptors (In-Arena) | - PlayerCAM (선수 시점) |
| - Lakers (Studio Show) | - Analysis Stream |
| - Mobile View (In-Arena) | - Mobile Portrait View |
| **Languages** | **Languages** |
| - Spanish (Prime Video) | - Korean |
| - Portuguese (Prime Video) | - English, Japanese, etc. (20개국) |
| **Audio** | **Commentary** |
| - Home/Away 해설 | - 일반/분석/입문자 해설 |

### Key Plays → Key Hands 모달

| NBA TV | WSOPTV |
|--------|--------|
| 썸네일 (플레이 장면) | 썸네일 (핸드 장면) |
| "Smart pullup jump shot" | "Phil Ivey 4-bet bluff" |
| "Q1 • 11:16" | "Hand #47 • Blinds 50K/100K" |
| 클릭 시 해당 시점 이동 | 클릭 시 해당 핸드 이동 |
| "1 of 4 Key Plays" 오버레이 | "1 of N Key Hands" 오버레이 |

### Game Info → Hand Info 패널

| NBA TV 필드 | WSOPTV 필드 |
|------------|-------------|
| Date/Time | Date/Time |
| Arena (Crypto.com Arena) | Tournament (WSOP Main Event) |
| Officials | Dealer |
| Broadcast (Coupang Play) | Broadcast (WSOPTV) |
| Game Book (PDF) | Hand History (PDF) |
| **LINESCORES** | **HAND SUMMARY** |
| Q1, Q2, Q3, Q4 | Preflop, Flop, Turn, River |
| Team Stats | Player Stats (VPIP, PFR, AF) |

### Box Score → Player Stats

| NBA TV 컬럼 | WSOPTV 컬럼 |
|------------|-------------|
| MIN (출전 시간) | Hands (참여 핸드 수) |
| FGM/FGA/FG% | VPIP/PFR/3-Bet% |
| 3PM/3PA/3P% | C-Bet/Fold to C-Bet |
| REB | Pots Won |
| AST | Bluffs |
| PTS | Chips Won/Lost |
| +/- | ROI |

### Play-by-Play → Hand-by-Hand Log

| NBA TV | WSOPTV |
|--------|--------|
| Q1 / ALL 탭 | Hand # / ALL 탭 |
| Auto Switch Quarter | Auto Next Hand |
| Latest First 토글 | Latest First 토글 |
| 타임스탬프 + 점수 | 타임스탬프 + POT |
| 선수 아바타 + 팀 로고 | 선수 아바타 + 카드 |
| "L. Dončić Running Layup (12 PTS)" | "[Ivey] RAISE $50,000 (UTG)" |

### Shot Charts → Position Analysis

| NBA TV | WSOPTV |
|--------|--------|
| 코트 시각화 | 테이블 포지션 시각화 |
| Made ○ / Miss ✕ | Win ● / Fold ○ |
| 선수별 필터 | 선수별 필터 |
| FG%: 57.1% (12/21) | Win Rate: 45% (9/20) |
| Range Filter | Position Filter |
| Download 버튼 | Download 버튼 |

---

## Problem Statement

### 현재 상황
- PokerGo 등 경쟁 서비스는 단일 화면 스트리밍만 제공
- 포커 팬들은 특정 플레이어에 집중하고 싶어함
- 통계 정보 없이는 전문적인 분석 시청이 어려움

### 해결 방안
- **NBA TV 스타일 검증된 UX 채택**: 글로벌 스포츠 스트리밍의 표준 패턴 적용
- **3계층 동적 Multi-view**: PGM → 피처 테이블 → PlayerCAM의 계층적 구조로 유연한 시청
- **StatsView 2구조**: MVP는 GGPoker HUD DB 활용, Phase 2는 대회 실시간 연동
- 실시간 View Mode 전환으로 유연한 시청 경험

---

## Target Users

| 사용자 유형 | 설명 | Advanced Mode 니즈 |
|------------|------|-------------------|
| **하드코어 포커 팬** | 특정 선수 팔로워 | PlayerCAM, 표정 분석 |
| **포커 학습자** | 전략 분석 시청자 | 통계 데이터, 베팅 패턴 |
| **스트리머/해설자** | 콘텐츠 크리에이터 | 멀티앵글, 분석 자료 |

---

## Feature Specification

### 1. Tournament Strip (NBA Score Strip 스타일)

> **NBA TV 참조**: Score Strip - 상단 가로 스크롤 실시간 점수

#### 1.1 개념 정의

![Tournament Strip](../images/nbatv-reference/slide_02.png)

Tournament Strip은 상단에 고정된 가로 스크롤 바로, 현재 진행 중인 모든 대회/테이블의 실시간 상태를 표시합니다.

#### 1.2 UI 설계

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🔴 Main Event  │ 🔴 High Roller │ ▶ $1K Daily │ ▶ Super Circuit #12    │
│ POT: $2.4M     │ POT: $890K     │ POT: $420K  │ Final Table            │
│ Blinds: 50K/100K│ Blinds: 25K/50K│ Blinds: 5K/10K │ POT: $1.1M         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 1.3 기능 요구사항

| ID | 요구사항 | 설명 | 우선순위 |
|----|---------|------|:--------:|
| TS-1.1 | 상단 Tournament Strip | 진행 중 대회/테이블 가로 스크롤 | P0 |
| TS-1.2 | 실시간 팟 크기 표시 | 각 테이블 현재 POT | P0 |
| TS-1.3 | LIVE 인디케이터 | 라이브/VOD 구분 배지 | P1 |
| TS-1.4 | Quick Add to Multiview | 클릭으로 Multiview 슬롯 추가 | P1 |

#### 1.4 UI 목업

![Homepage NBA Style](../images/PRD-0006/homepage-nba-style.png)

[HTML 원본](../mockups/PRD-0006/homepage-nba-style.html)

---

### 2. Multi-view (NBA Multiview 스타일)

> **NBA TV 참조**: Multiview 4분할, "Add a Game from Score Strip"

#### 2.1 개념 정의

> "메인화면이 중앙에 있고, 각 유저들의 얼굴을 잡고 있는 화면이 옆에 또 있는 방식 (아이돌 PlayerCAM 스타일)"
> — Michael Note

![NBA Multiview](../images/nbatv-reference/slide_10.png)

NBA TV의 4분할 레이아웃 + WSOPTV 3계층 구조를 결합한 하이브리드 멀티뷰 제공.

#### 2.2 레이아웃 옵션

**옵션 A: 4분할 그리드 (NBA TV 스타일)**

```
┌─────────────────────────────────────────────────────────────┐
│  ┌───────────────────────┐  ┌───────────────────────────┐   │
│  │  WSOP Main Event      │  │  $100K High Roller        │   │
│  │  Final Table          │  │  Day 2                    │   │
│  │  POT: $2.4M           │  │  POT: $890K               │   │
│  │  🔊 AUDIO             │  │                           │   │
│  └───────────────────────┘  └───────────────────────────┘   │
│  ┌───────────────────────┐  ┌───────────────────────────┐   │
│  │  Add Table from       │  │  Super Circuit #12        │   │
│  │  Tournament Strip     │  │  Heads Up                 │   │
│  │                       │  │  POT: $420K               │   │
│  └───────────────────────┘  └───────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  [Tables] [MultiView] [Key Hands]     [1] [2] [4] Layout    │
└─────────────────────────────────────────────────────────────┘
```

**옵션 B: 3계층 동적 레이아웃 (WSOPTV 오리지널)**

**케이스 1: PGM이 메인 (기본 상태)**
```
┌──────────────────────────────────────────────────────────┐
│                                           │ 피처 테이블   │
│                                           │ ┌──────────┐ │
│           메인 PGM (확대)                   │ │ Table 1  │ │
│                                           │ │PlayerCAM지원│ │
│                                           │ └──────────┘ │
│                                           │ ┌──────────┐ │
│                                           │ │ Table 2  │ │
│                                           │ └──────────┘ │
│                                           ├──────────────┤
│                                           │PlayerCAM(비활성)│
│                                           │ "테이블 선택 │
│                                           │  시 활성화"  │
└──────────────────────────────────────────────────────────┘
```

**케이스 2: 피처 테이블이 메인 (테이블 클릭 시)**
```
┌──────────────────────────────────────────────────────────┐
│ PGM       │                               │ PlayerCAM    │
│ ┌───────┐ │                               │ ┌──────────┐ │
│ │ 축소  │ │    피처 테이블 #1 (확대)        │ │ Player 1 │ │
│ │ PGM   │ │    (PlayerCAM 지원 테이블)     │ └──────────┘ │
│ └───────┘ │                               │ ┌──────────┐ │
│ ┌───────┐ │                               │ │ Player 2 │ │
│ │ 다른  │ │                               │ └──────────┘ │
│ │테이블 │ │                               │ ┌──────────┐ │
│ └───────┘ │                               │ │ Player 3 │ │
│           │                               │ └──────────┘ │
└──────────────────────────────────────────────────────────┘
```

#### 2.3 기능 요구사항

| ID | 요구사항 | 설명 | 우선순위 |
|----|---------|------|:--------:|
| MV-1.1 | 4분할 그리드 레이아웃 | NBA TV 스타일 4개 동시 시청 | P0 |
| MV-1.2 | 빈 슬롯 가이드 | "Add Table from Tournament Strip" | P0 |
| MV-1.3 | 1/2/4 분할 전환 | 하단 버튼으로 레이아웃 전환 | P0 |
| MV-1.4 | 오디오 선택 | 4개 중 1개만 오디오 활성화 | P1 |
| MV-1.5 | 3계층 동적 레이아웃 | PGM → 피처 테이블 → PlayerCAM | P1 |
| MV-1.6 | POT/Blinds Overlay | 각 화면에 현재 상태 오버레이 | P1 |
| MV-1.7 | 동기화 상태 표시 | 모든 스트림 동기화 인디케이터 | P1 |

#### 2.4 UI 목업

![Multiview 4분할](../images/PRD-0006/multiview-4split.png)

[HTML 원본](../mockups/PRD-0006/multiview-4split.html)

![Multiview 3계층](../images/PRD-0006/multiview-3layer.png)

[HTML 원본](../mockups/PRD-0006/multiview-3layer.html)

---

### 3. 플레이어 컨트롤 UI (NBA Player Controls 스타일)

> **NBA TV 참조**: Streams/MultiView/Key Plays 버튼 배치

![NBA Player Controls](../images/nbatv-reference/slide_08.png)

#### 3.1 컨트롤바 구성

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        [비디오 플레이어 영역]                             │
│                                                              🔴 LIVE    │
├─────────────────────────────────────────────────────────────────────────┤
│  ▶/⏸  [────────●───────────────────────────────]  🔊  ⬜  ⛶            │
├─────────────────────────────────────────────────────────────────────────┤
│  [🎥 Tables (5)] [📺 MultiView] [⭐ Key Hands]        [1] [2] [4]       │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 3.2 기능 요구사항

| ID | 요구사항 | 설명 | 우선순위 |
|----|---------|------|:--------:|
| PC-1.1 | Tables 버튼 | 사용 가능한 테이블/뷰 선택 | P0 |
| PC-1.2 | MultiView 버튼 | 멀티뷰 모드 진입 | P0 |
| PC-1.3 | Key Hands 버튼 | 주요 핸드 목록 모달 | P0 |
| PC-1.4 | Layout 전환 버튼 | 1/2/4 분할 전환 | P1 |
| PC-1.5 | LIVE 인디케이터 | 우측 상단 라이브 배지 | P1 |

#### 3.3 UI 목업

![Player Controls NBA Style](../images/PRD-0006/player-controls-nba-style.png)

[HTML 원본](../mockups/PRD-0006/player-controls-nba-style.html)

---

### 4. Streaming Options 모달 (NBA Broadcasts 스타일)

> **NBA TV 참조**: Broadcasts/Languages/Audio 탭 구조

![NBA Streaming Options](../images/nbatv-reference/slide_06.png)

#### 4.1 탭 구조

**Views 탭 (Broadcasts 대응)**

| 뷰 옵션 | 설명 | NBA 대응 |
|---------|------|----------|
| **Table View** | 딜러 시점 전체 테이블 | In-Arena Home |
| **PlayerCAM** | 선수 개별 카메라 | In-Arena Away |
| **Analysis Stream** | 해설자 분석 방송 | Studio Show |
| **Mobile Portrait** | 세로 영상 최적화 | Mobile View |

**Languages 탭**

| 언어 | 지원 형태 |
|------|----------|
| English | 기본 |
| Korean | 자막 + 해설 |
| Japanese | 자막 + 해설 |
| Chinese | 자막 |
| ... (20개국) | 자막 |

**Commentary 탭 (Audio 대응)**

| 해설 유형 | 설명 |
|----------|------|
| **일반 해설** | 전통적인 스포츠 중계 스타일 |
| **분석 해설** | 전문 통계/확률 분석 |
| **입문자 해설** | 포커 룰 설명 포함 |

#### 4.2 UI 목업

![Streaming Options Modal](../images/PRD-0006/streaming-options-modal.png)

[HTML 원본](../mockups/PRD-0006/streaming-options-modal.html)

---

### 5. Key Hands 모달 (NBA Key Plays 스타일)

> **NBA TV 참조**: Key Plays 목록 + 점프 기능

![NBA Key Plays](../images/nbatv-reference/slide_11.png)

#### 5.1 목록 구성

```
┌─────────────────────────────────────────┐
│              KEY HANDS                   │
├─────────────────────────────────────────┤
│  [썸네일] Phil Ivey 4-bet bluff         │
│           Hand #47 • Blinds 50K/100K    │
│           ▶ Jump to this hand           │
├─────────────────────────────────────────┤
│  [썸네일] AA cracked by runner-runner   │
│           Hand #52 • POT $1.2M          │
│           ▶ Jump to this hand           │
├─────────────────────────────────────────┤
│  [썸네일] All-in call with K-high       │
│           Hand #58 • Winner: Smith      │
│           ▶ Jump to this hand           │
└─────────────────────────────────────────┘
```

#### 5.2 오버레이 네비게이션

점프 후 화면 우측 상단에 표시:

```
┌────────────────────────────────────────┐
│  Phil Ivey 4-bet bluff                 │
│  1 of 12 Key Hands           [< ▶ >]   │
└────────────────────────────────────────┘
```

#### 5.3 기능 요구사항

| ID | 요구사항 | 설명 | 우선순위 |
|----|---------|------|:--------:|
| KH-1.1 | Key Hands 버튼 | 플레이어 하단 컨트롤바 | P0 |
| KH-1.2 | 모달 목록 | 썸네일 + 핸드 설명 + 타임스탬프 | P0 |
| KH-1.3 | 클릭 점프 | 해당 핸드 시점으로 이동 | P0 |
| KH-1.4 | 오버레이 네비게이션 | "1 of N Key Hands" + 화살표 | P1 |
| KH-1.5 | AI 자동 추출 | 주요 핸드 자동 태깅 | P2 |

#### 5.4 UI 목업

![Key Hands Modal](../images/PRD-0006/key-hands-modal.png)

[HTML 원본](../mockups/PRD-0006/key-hands-modal.html)

---

### 6. Hand Info 패널 (NBA Game Info 스타일)

> **NBA TV 참조**: Game Info 패널 + LINESCORES

![NBA Game Info](../images/nbatv-reference/slide_13.png)

#### 6.1 패널 구성

**기본 정보**

| 필드 | 예시 값 |
|------|--------|
| **Date/Time** | January 19, 2026 • 8:00 PM PT |
| **Tournament** | WSOP Main Event - Final Table |
| **Dealer** | John Smith |
| **Broadcast** | WSOPTV Plus+ |
| **Hand History** | [Download PDF] |

**HAND SUMMARY (LINESCORES 대응)**

```
┌────────────────────────────────────────────────────────┐
│           │ Preflop │  Flop  │  Turn  │ River │ Total  │
├───────────┼─────────┼────────┼────────┼───────┼────────┤
│ Phil Ivey │  $50K   │ $200K  │ $600K  │  -    │ $850K  │
│ Negreanu  │  $150K  │ $200K  │ FOLD   │  -    │ -$350K │
└────────────────────────────────────────────────────────┘
```

#### 6.2 UI 목업

![Hand Info Panel](../images/PRD-0006/hand-info-panel.png)

[HTML 원본](../mockups/PRD-0006/hand-info-panel.html)

---

### 7. Player Stats 테이블 (NBA Box Score 스타일)

> **NBA TV 참조**: Box Score 선수별 통계

![NBA Box Score](../images/nbatv-reference/slide_14.png)

#### 7.1 통계 컬럼 매핑

| WSOPTV 컬럼 | 설명 | NBA 대응 |
|------------|------|----------|
| **Hands** | 참여 핸드 수 | MIN |
| **VPIP** | Voluntarily Put $ In Pot | FG% |
| **PFR** | Pre-Flop Raise % | 3P% |
| **3-Bet%** | 3-Bet 빈도 | FT% |
| **C-Bet** | Continuation Bet % | - |
| **Pots Won** | 획득 팟 수 | REB |
| **Chips +/-** | 칩 변동 | +/- |

#### 7.2 테이블 예시

```
┌──────────────────────────────────────────────────────────────────────────┐
│ PLAYER STATS - Final Table                                               │
├───────────────┬───────┬──────┬──────┬───────┬───────┬─────────┬─────────┤
│ Player        │ Hands │ VPIP │  PFR │ 3-Bet │ C-Bet │ Pots Won│ Chips +/-│
├───────────────┼───────┼──────┼──────┼───────┼───────┼─────────┼─────────┤
│ Phil Ivey     │   47  │  28% │  22% │  12%  │  75%  │    12   │ +$2.4M  │
│ D. Negreanu   │   52  │  35% │  18% │   8%  │  62%  │     8   │ -$890K  │
│ Phil Hellmuth │   38  │  22% │  15% │   6%  │  80%  │     6   │ +$420K  │
│ ...           │  ...  │ ...  │ ...  │  ...  │  ...  │   ...   │  ...    │
└───────────────┴───────┴──────┴──────┴───────┴───────┴─────────┴─────────┘
```

#### 7.3 UI 목업

![Player Stats Table](../images/PRD-0006/player-stats-table.png)

[HTML 원본](../mockups/PRD-0006/player-stats-table.html)

---

### 8. Hand-by-Hand Log (NBA Play-by-Play 스타일)

> **NBA TV 참조**: Play-by-Play 실시간 로그

![NBA Play-by-Play](../images/nbatv-reference/slide_16.png)

#### 8.1 로그 구성

```
┌─────────────────────────────────────────────────────────────┐
│  [Hand #47] [All]  |  Filter: [All Players ▼]               │
│  ☑ Auto Next Hand   ☐ Latest First                          │
├─────────────────────────────────────────────────────────────┤
│  [👤 Ivey]   UTG    RAISE $50,000        │ POT: $75,000     │
│  [👤 Negreanu]  BTN    3-BET $150,000    │ POT: $225,000    │
│  [👤 Ivey]   UTG    CALL $100,000        │ POT: $325,000    │
│  ─────────── FLOP: A♥ K♠ 7♦ ───────────                     │
│  [👤 Ivey]         CHECK                 │                   │
│  [👤 Negreanu]     BET $200,000          │ POT: $525,000    │
│  [👤 Ivey]         RAISE $600,000        │ POT: $1,125,000  │
│  [👤 Negreanu]     FOLD                  │                   │
│  ─────────── RESULT: Ivey wins $950,000 ───────────         │
└─────────────────────────────────────────────────────────────┘
```

#### 8.2 기능 요구사항

| ID | 요구사항 | 설명 | 우선순위 |
|----|---------|------|:--------:|
| HL-1.1 | 실시간 액션 로그 | 프리플롭/플롭/턴/리버 액션 | P0 |
| HL-1.2 | 선수 필터 | 특정 선수 액션만 표시 | P1 |
| HL-1.3 | Auto Next Hand | 다음 핸드 자동 전환 | P1 |
| HL-1.4 | Latest First 토글 | 최신순/시간순 정렬 | P2 |
| HL-1.5 | 타임스탬프 링크 | 클릭 시 해당 시점으로 이동 | P2 |

#### 8.3 UI 목업

![Hand-by-Hand Log](../images/PRD-0006/hand-by-hand-log.png)

[HTML 원본](../mockups/PRD-0006/hand-by-hand-log.html)

---

### 9. Position Analysis (NBA Shot Charts 스타일)

> **NBA TV 참조**: Shot Charts 시각화

![NBA Shot Charts](../images/nbatv-reference/slide_15.png)

#### 9.1 시각화 구성

```
┌─────────────────────────────────────────────────────────────┐
│                    POSITION ANALYSIS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│              [BB]  [SB]  [BTN]  [CO]  [MP]  [UTG]            │
│               ●     ○     ●      ●    ◐     ●               │
│                                                              │
│     ● Win (Showdown)   ○ Fold   ◐ Win (No Showdown)         │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Win Rate by Position:                                       │
│  BTN: 45% (9/20)  │  CO: 38% (6/16)  │  MP: 25% (4/16)      │
│  UTG: 20% (2/10)  │  BB: 35% (7/20)  │  SB: 30% (6/20)      │
├─────────────────────────────────────────────────────────────┤
│  Filter: [All Players ▼]   Range: [All Hands ▼]             │
│                                          [📥 Download]       │
└─────────────────────────────────────────────────────────────┘
```

#### 9.2 기능 요구사항

| ID | 요구사항 | 설명 | 우선순위 |
|----|---------|------|:--------:|
| PA-1.1 | 테이블 포지션 시각화 | 포지션별 성적 표시 | P1 |
| PA-1.2 | Win/Fold 마커 | 결과별 아이콘 표시 | P1 |
| PA-1.3 | 선수별 필터 | 특정 선수 데이터만 표시 | P2 |
| PA-1.4 | Range 필터 | 핸드 범위 필터 | P2 |
| PA-1.5 | Download 버튼 | 데이터 다운로드 | P2 |

#### 9.3 UI 목업

![Position Analysis](../images/PRD-0006/position-analysis.png)

[HTML 원본](../mockups/PRD-0006/position-analysis.html)

---

### 10. StatsView (통계 뷰) - 2가지 구조

#### 10.1 개념 정의

> "허드같이 그 유저의 수치라든가, 플랍에서 베팅할 확률같은거, 이런게 띄어져있는 영상"
> — Michael Note

#### 10.2 구조 1: GGPoker HUD 연동 (MVP)

| 항목 | 내용 |
|------|------|
| **데이터 소스** | GGPoker HUD DB |
| **UI 설계** | GGPoker HUD와 동일한 정보 및 UI |
| **구현 난이도** | 중간 |
| **우선순위** | P0 (MVP) |

**제공 통계**:

| 통계 | 설명 |
|------|------|
| **VPIP** | Voluntarily Put $ In Pot |
| **PFR** | Pre-Flop Raise % |
| **3Bet** | 3-Bet 빈도 |
| **AF** | Aggression Factor |
| **Flop CB%** | 플랍 컨티뉴에이션 베팅 빈도 |
| **칩 카운트** | 현재 스택 크기 |

#### 10.3 구조 2: 대회 실시간 연동 (Phase 2)

| 항목 | 내용 |
|------|------|
| **데이터 소스** | 대회 실시간 데이터 |
| **특징** | 베팅 액션 정보 실시간 표시 |
| **구현 난이도** | 높음 (고급 작업) |
| **우선순위** | P1 (Phase 2) |

**제공 정보**:

| 정보 | 설명 |
|------|------|
| **현재 액션** | Bet / Raise / Call / Fold / Check |
| **베팅 금액** | 실시간 베팅 사이즈 |
| **팟 오즈** | 콜 시 팟 오즈 계산 |
| **예상 액션** | AI 기반 다음 액션 예측 |

#### 10.4 기능 요구사항

| ID | 요구사항 | 설명 | 우선순위 |
|----|---------|------|:--------:|
| SV-1.1 | 구조 1: GGPoker HUD 연동 | GGPoker HUD DB 기반 통계 표시 | P0 |
| SV-1.2 | HUD ON/OFF 토글 | 사용자 선택으로 표시/숨김 | P0 |
| SV-1.3 | 기본 통계 6종 | VPIP, PFR, 3Bet, AF, Flop CB, 칩 | P0 |
| SV-1.4 | 통계 상세 팝업 | 클릭 시 전체 통계 표시 | P1 |
| SV-2.1 | 구조 2: 대회 실시간 연동 | 베팅 액션 실시간 표시 | P1 |
| SV-2.2 | 예상 액션 표시 | AI 기반 베팅 확률 표시 | P2 |

#### 10.5 UI 목업

![StatsView HUD](../images/PRD-0006/statsview-hud.png)

[HTML 원본](../mockups/PRD-0006/statsview-hud.html)

---

### 11. View Mode Switcher

#### 11.1 UI 설계

```
┌─────────────────────────────────────────────────────────┐
│  View Mode:                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Standard │  │Multi-view│  │StatsView │              │
│  │    ●     │  │    ○     │  │    ○     │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

#### 11.2 모드별 특징

| Mode | 설명 | 화면 구성 |
|------|------|----------|
| **Standard** | 기본 시청 모드 | 단일 PGM 화면 |
| **Multi-view** | 멀티앵글 모드 | 4분할 또는 3계층 |
| **StatsView** | 통계 오버레이 모드 | PGM + HUD |
| **Combined** | 통합 모드 (P2) | Multi-view + HUD |

#### 11.3 기능 요구사항

| ID | 요구사항 | 설명 | 우선순위 |
|----|---------|------|:--------:|
| VS-1.1 | 모드 전환 UI | 상단 탭 또는 플로팅 버튼 | P0 |
| VS-1.2 | 실시간 전환 | 재생 중 끊김 없이 전환 | P0 |
| VS-1.3 | 모드 기억 | 마지막 선택 모드 저장 | P1 |
| VS-1.4 | Combined 모드 | Multi-view + StatsView 동시 | P2 |

#### 11.4 UI 목업

![View Mode Switcher](../images/PRD-0006/view-mode-switcher.png)

[HTML 원본](../mockups/PRD-0006/view-mode-switcher.html)

---

### 12. 멀티 재생 확장 (Tony 기획)

#### 12.1 선수별/테이블별 멀티 재생

| 기능 | 설명 | 우선순위 |
|------|------|:--------:|
| **선수별 멀티 재생** | 한 테이블의 각 선수별 화면 동시 재생 | P1 |
| **테이블별 멀티 재생** | 각각 다른 대회, 테이블 동시 재생 | P1 |

> 여러 대회/테이블을 병렬로 시청하면서 관심 있는 선수의 플레이를 놓치지 않는 시청 경험 제공.

#### 12.2 동영상 Tagging (Hand 기반)

대회 영상/Script 기반 영상 태깅 시스템으로 핸드 단위 검색 및 재생 지원.

| 태그 필드 | 설명 |
|----------|------|
| **Hand Number** | 핸드 번호, Blinds 레벨 |
| **참여 플레이어** | 해당 핸드에 참여한 플레이어 목록 |
| **각 플레이어의 Hands** | 홀카드 정보 |
| **Community Card** | 보드 카드 (Flop, Turn, River) |
| **최종 Winner** | 승자 + 승리 핸드 |

#### 12.3 고급 검색 기능

| 검색 유형 | 설명 | 예시 |
|----------|------|------|
| **선수 기반** | 특정 선수가 참여한 Pot만 재생 | "Phil Ivey 핸드 모음" |
| **핸드 결과 기반** | 특정 핸드로 이기거나 진 핸드 | "AA로 진 핸드" |
| **복합 검색** | A 선수와 B 선수가 함께 했던 대회/동영상 | "Negreanu vs Hellmuth" |
| **특수 상황** | 희귀 상황 핸드 검색 | "포카드가 로열 스트레이트 플러시에게 패한 핸드" |

#### 12.4 UI 목업

![Hand Search](../images/PRD-0006/hand-search.png)

[HTML 원본](../mockups/PRD-0006/hand-search.html)

---

## Access Control

### 구독 티어별 접근 권한

| 기능 | Plus ($10) | Plus+ ($50) |
|------|:----------:|:-----------:|
| Standard Mode | O | O |
| Tournament Strip | O | O |
| Multi-view (4분할) | **X** | **O** |
| 3계층 Multi-view | **X** | **O** |
| StatsView | **X** | **O** |
| Key Hands 점프 | **X** | **O** |
| Hand-by-Hand Log | O (Basic) | **O (Full)** |
| Position Analysis | **X** | **O** |
| Combined Mode | X | O (P2) |

### Timeshift (재방송) 접근 권한

| 기능 | Plus ($10) | Plus+ ($50) |
|------|:----------:|:-----------:|
| Standard Timeshift | O | O |
| Timeshift + Multi-view | **X** | **O** |
| Timeshift + StatsView | **X** | **O** |
| Timeshift 보관 기간 | 30일 | 무제한 |

### Plus+ 가치 제안

> "Exclusive Content (behind-the-scenes) 는 굳이 WSOPTV 용으로 따로 제작하지 말자."
> — Michael Note

**결론**: Advanced Mode가 Plus+의 **유일한 차별화 포인트**

| Plus+ 전용 기능 | 가치 |
|----------------|------|
| 4분할 Multiview | NBA 스타일 동시 시청 |
| 3계층 Multi-view | 좋아하는 플레이어 집중 시청 |
| StatsView | 전문적인 분석 시청 |
| Key Hands 점프 | 주요 순간 빠른 탐색 |
| Position Analysis | 포지션별 성적 시각화 |
| (향후) 4K 화질 | 프리미엄 화질 |

---

## Technical Requirements

### 스트리밍 아키텍처

#### Multi-view 구현 방식

| 옵션 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **A. 클라이언트 믹싱** | 10개 스트림 동시 수신 | 유연한 레이아웃 | 트래픽 10배, 기기 부하 |
| **B. 서버 믹싱** | 서버에서 합성 후 송출 | 트래픽 1배 | 레이아웃 고정 |
| **C. 하이브리드** | 메인+선택 캠만 수신 | 균형 | 복잡도 증가 |

**권장안**: **B. 서버 믹싱**
- 30분+ 의도적 지연 방송이므로 사전 렌더링 가능
- 트래픽 비용 최적화

#### StatsView 구현 방식

| 옵션 | 설명 | 실현 가능성 | 비용 |
|------|------|:----------:|:----:|
| **A. GTO Solver 실시간 연동** | 실시간 최적 플레이 계산 | 낮음 | 매우 높음 |
| **B. 사전 계산 통계** | 역대 데이터 기반 통계 | 높음 | 중간 |
| **C. 수동 입력** | 해설자/운영자 입력 | 높음 | 낮음 |

**권장안**: **B. 사전 계산 통계** (MVP)
- GGPoker 내부 통계 DB 활용
- 대회 시작 전 플레이어 프로필 캐싱

### 플랫폼별 지원

| 플랫폼 | Multi-view | StatsView | Key Hands | Position Analysis |
|--------|:----------:|:---------:|:---------:|:-----------------:|
| **Web** | O | O | O | O |
| **iOS** | O | O | O | O |
| **Android** | O | O | O | O |
| **Samsung TV** | X | X | X | X |
| **LG TV** | X | X | X | X |

> **제약사항**: TV 앱에서는 Advanced Mode 미지원. PGM 단일 화면만 제공.

---

## UI/UX Specification

### Multi-view 인터랙션

| 액션 | 동작 |
|------|------|
| 슬롯 탭 | 해당 화면 풀스크린 전환 |
| 풀스크린에서 뒤로 | 멀티뷰로 복귀 |
| 오디오 아이콘 탭 | 오디오 소스 전환 |
| 더블탭 | 메인 PGM으로 복귀 |
| Tournament Strip 클릭 | 해당 테이블을 빈 슬롯에 추가 |

### StatsView 인터랙션

| 액션 | 동작 |
|------|------|
| HUD 탭 | 상세 통계 팝업 |
| 팝업 외부 탭 | 팝업 닫기 |
| HUD 토글 버튼 | 전체 HUD 표시/숨김 |
| 롱프레스 | HUD 위치 조정 (P2) |

### Key Hands 인터랙션

| 액션 | 동작 |
|------|------|
| Key Hands 버튼 클릭 | 모달 열기 |
| 핸드 항목 클릭 | 해당 시점으로 점프 |
| 오버레이 화살표 클릭 | 이전/다음 Key Hand 이동 |
| 오버레이 외부 클릭 | 오버레이 닫기 |

---

## Dependencies

### 내부 의존성

| 의존성 | 설명 | 담당 |
|--------|------|------|
| GGPoker 통계 API | 플레이어 히스토리 데이터 | GG POKER |
| RFID 테이블 연동 | 실시간 칩 카운트 | 프로덕션팀 |
| 멀티캠 인프라 | 10개 동시 카메라 | 프로덕션팀 |
| Key Hands 태깅 | 주요 핸드 메타데이터 | 콘텐츠팀 |

### 외부 의존성

| 의존성 | 설명 | 공급사 |
|--------|------|--------|
| 비디오 믹싱 서버 | 서버 사이드 렌더링 | OVP 업체 |
| CDN 멀티스트림 | 동시 스트림 배포 | AWS/Akamai |

---

## Success Metrics

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| Plus+ 전환율 | Plus 대비 20% 전환 | 구독 데이터 |
| Advanced Mode 사용률 | Plus+ 사용자 중 70% | 기능 사용 로그 |
| Multi-view 평균 사용 시간 | 세션당 30분+ | 시청 로그 |
| StatsView 활성화율 | 60% 상시 ON | 설정 로그 |
| Key Hands 점프 사용률 | 세션당 평균 5회+ | 클릭 로그 |

---

## Timeline

| Phase | 기능 | 목표 시점 |
|-------|------|----------|
| **Phase 1 (MVP)** | Tournament Strip, 4분할 Multiview, StatsView 기본, Key Hands | Q3 2026 |
| **Phase 2** | 3계층 Multi-view, Hand-by-Hand Log, Player Stats | Q4 2026 |
| **Phase 3** | Position Analysis, Combined Mode, AI Key Hands 추출 | 2027 |

---

## Open Questions

### 프로덕션팀 (PD/연출) 제안 필요

1. **Multi-view 레이아웃 선호도**
   - NBA 스타일 4분할 vs WSOPTV 3계층?
   - 제안 배경: 두 가지 방식 모두 제공 가능

2. **TV 앱 예외 처리**
   - Plus+ 구독자가 TV에서 Advanced Mode 미지원 시 사용자 경험 어떻게 할 것인가?
   - 제안 배경: 리모컨 UX 제약으로 인한 구현 불가능성

### GG POKER (데이터 제공) 제안 필요

1. **StatsView 통계 범위 및 정확성**
   - GGPoker 내부 통계만 제공 vs 외부 데이터 연동?
   - GTO Wizard 연동 가능성 및 기술 스택?
   - 제안 배경: 통계 데이터의 신뢰성과 확장성

2. **통계 데이터 갱신 주기**
   - 대회 전 1회 캐싱 vs 핸드별 실시간 갱신?
   - 제안 배경: 레이턴시 vs 정확성 트레이드오프

### 개발팀 (기술 구현) 제안 필요

1. **서버 믹싱 vs 클라이언트 믹싱**
   - B안(서버 믹싱) 권장 근거: 30분+ 지연 방송이므로 사전 렌더링 가능
   - 제안 배경: 트래픽 비용 최적화

---

## References

- [PRD-0002 WSOPTV OTT Platform MVP](PRD-0002-wsoptv-ott-platform-mvp.md) - MVP 스펙
- [ADR-0001 3계층 Multi-View 아키텍처 근거](../adrs/ADR-0001-multiview-3layer-rationale.md)
- [REPORT-2026-01-19 NBA TV 분석](../reports/REPORT-2026-01-19-nbatv-reference-analysis.md) - **NBA TV 1:1 매핑 소스**

---

*Created: 2026-01-15*
*Last Updated: 2026-01-19*

---

## Revision History

| 버전 | 날짜 | 작성자 | 내용 |
|------|------|--------|------|
| 1.0 | 2026-01-15 | Claude Code | 최초 작성 |
| 2.0 | 2026-01-16 | Claude Code | Multi-view 3계층 동적 구조로 재설계, StatsView 2가지 구조 정의, UI 목업 링크 추가 |
| 2.1 | 2026-01-19 | Claude Code | 섹션 4 추가 (Tony 기획: 멀티 재생 확장, Hand Tagging, 고급 검색) |
| 2.2 | 2026-01-19 | Claude Code | PRD-0006 전용 UI 목업 4개 추가 |
| **3.0** | **2026-01-19** | **Claude Code** | **NBA TV 1:1 매핑 전략 적용 - 전면 재설계. Tournament Strip, 플레이어 컨트롤, Streaming Options, Key Hands, Hand Info, Player Stats, Hand-by-Hand Log, Position Analysis 섹션 추가** |
