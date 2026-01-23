# NBA TV & Triton Poker Plus OTT 분석 보고서

**작성일**: 2026-01-20
**소스**: [Google Slides - NBA TV 분석 자료](https://docs.google.com/presentation/d/12czNJ9OmJjzu-Nii1ZefIjNgov94I8gNIyXNVdBv9I4/edit?usp=sharing)
**작성**: GG PRODUCTION
**목적**: WSOPTV OTT 플랫폼 개발을 위한 레퍼런스 분석

---

## 목차

1. [개요](#개요)
2. [NBA TV 분석 (슬라이드 1-16)](#nba-tv-분석-슬라이드-1-16)
3. [Triton Poker Plus 분석 (슬라이드 17-19)](#triton-poker-plus-분석-슬라이드-17-19)
4. [핵심 기능 비교](#핵심-기능-비교)
5. [WSOPTV 적용 방안](#wsoptv-적용-방안)

---

## 개요

이 보고서는 **NBA TV OTT**와 **Triton Poker Plus** 두 플랫폼을 분석합니다.

| 플랫폼 | 특징 | WSOPTV 관련성 |
|--------|------|---------------|
| **NBA TV** | 스포츠 OTT의 표준 UX 패턴 | MultiView, Stats, Key Plays |
| **Triton Poker Plus** | 포커 전용 OTT | Hand History, Chip Counts, 포커 특화 UI |

총 **19개 슬라이드**로 구성:
- 슬라이드 1-16: NBA TV
- 슬라이드 17-19: Triton Poker Plus

---

## NBA TV 분석 (슬라이드 1-16)

### 슬라이드 1: 표지
![Slide 1](../images/nbatv-reference/slide_01.png)

**내용**: NBA TV 분석 자료 - GG PRODUCTION

---

### 슬라이드 2: NBA.com 메인 화면
![Slide 2](../images/nbatv-reference/slide_02.png)

**화면 구성**:

| 영역 | 내용 | WSOPTV 적용 |
|------|------|-------------|
| **상단 배너** | "STREAM LIKE YOU'RE COURTSIDE" + League Pass CTA | "WATCH LIKE YOU'RE AT THE TABLE" |
| **스코어 티커** | 실시간 경기 스코어 (Hornets 89-57 Nuggets, Trail Blazers 44-39 Kings 등) | 테이블별 칩 리더/참가자 수 |
| **Hero 영역** | Morant Leads Grizzlies to London Victory (109-126 FINAL) | 메인 이벤트 하이라이트 |
| **CTA 버튼** | WATCH / BOX SCORE | WATCH / STATS |
| **Related Content** | Game Recap, Ja drops 24 points... | 관련 핸드/플레이어 |
| **Headlines** | 뉴스 피드 사이드바 | 토너먼트 뉴스 |
| **Rivals Week 배너** | AWS 스폰서 프로모션 | 이벤트 프로모션 |

**핵심 인사이트**:
- 실시간 스코어가 항상 상단에 노출
- Hero 영역에 최신 주요 경기 하이라이트
- 빠른 시청 액세스를 위한 CTA 버튼

---

### 슬라이드 3: 콘텐츠 허브 (Stories, Trending, Recaps)
![Slide 3](../images/nbatv-reference/slide_03.png)

**주요 섹션**:

1. **STORIES**
   - 라이브 경기 썸네일 (LIVE 배지)
   - Hornets vs Nuggets, Raptors vs Lakers, Trail Blazers vs Kings
   - "ALL-ACCESS" 배지로 프리미엄 콘텐츠 표시

2. **TRENDING NOW**
   - Durant Passes Dirk for 6th in Career Points
   - Ja Drops 24 Points, 13 Assists in London
   - Garland Out 7-10 Days with Right Toe Sprain
   - Cooper Flagg Can't Down

3. **50-POINT GAMES IN 2025-26**
   - Anthony Edwards drops career-high 55 points
   - Jaylen Brown ties career high with 50 points
   - Kawhi pours in career-high 55 points
   - Jokić erupts for triple-dub on Chi...

4. **2025-26 GAME RECAPS**
   - "FULL GAME RECAP" 배지
   - Grizzlies 126 - Magic 109
   - Trail Blazers 132 - Lakers 116

**WSOPTV 적용**:
- STORIES → 라이브 테이블별 스토리
- TRENDING NOW → 핫 핸드/빅 팟 하이라이트
- 50-POINT GAMES → "올해의 백만 달러 팟"
- GAME RECAPS → 토너먼트 Day Recap

---

### 슬라이드 4: Around the NBA (기사형 콘텐츠)
![Slide 4](../images/nbatv-reference/slide_04.png)

**콘텐츠 구성**:

| 섹션 | 기사 | 날짜 |
|------|------|------|
| 2025-26 GAME RECAPS | (상단 연속) | - |
| **AROUND THE NBA** | | |
| KIA MVP LADDER | SGA Reclaims No. 1 Spot | January 17, 2026 |
| Award Candidates | Who Are Top Award Candidates at Midpoint? | January 17, 2026 |
| KIA ROOKIE LADDER | Raynaud Nearing Top 5 | January 15, 2026 |
| On-Off Leaders | Who Are Top On-Off Leaders at Midseason? | January 15, 2026 |
| NBA London Game '26 | Everything to Know | January 17, 2026 |

**핵심 인사이트**:
- 썸네일 + 제목 + 설명 + 날짜 구조
- 날짜 기반 정렬 (최신순)
- 기사/분석 콘텐츠와 영상 콘텐츠 혼합

**WSOPTV 적용**:
- POY Ladder, 시즌 어워드, 신인 주목 선수
- 수익 리더보드, WSOP Europe 등

---

### 슬라이드 5: MultiView 설정 화면
![Slide 5](../images/nbatv-reference/slide_05.png)

**화면 구성**:

```
┌─────────────────────────────────────────────────┐
│  상단 스코어 티커 + "Add to Multiview" 링크      │
├─────────────────────────────────────────────────┤
│  Rivals Week 배너                                │
├────────────────────┬────────────────────────────┤
│                    │                            │
│   Add a Game       │    Add a Game              │
│   from Score Strip │    from Score Strip        │
│                    │                            │
└────────────────────┴────────────────────────────┘
```

**핵심 기능**:
- 스코어 티커에서 경기 선택 후 "Add to Multiview" 클릭
- 빈 슬롯에 "Add a Game from Score Strip" 안내
- 2분할 레이아웃 기본 제공

**WSOPTV 적용**:
- 테이블 Strip에서 MultiView로 테이블 추가
- 빈 슬롯 클릭 시 테이블 선택 모달

---

### 슬라이드 6: Streaming Options - Broadcasts 탭
![Slide 6](../images/nbatv-reference/slide_06.png)

**STREAMING OPTIONS 모달**:

| 탭 | 내용 |
|-----|------|
| **Broadcasts** (선택됨) | 방송 소스 선택 |
| Languages | 언어 선택 |
| Audio | 오디오 설정 |

**Broadcasts 옵션**:

| 옵션 | 설명 |
|------|------|
| ✓ **Lakers (In-Arena)** | Local broadcast with home arena game breaks |
| Raptors (In-Arena) | Local broadcast with home arena game breaks |
| Lakers (Studio Show) | Local broadcast with pre, post, and halftime analysis |
| Raptors (Studio Show) | Local broadcast with pre, post, and halftime analysis |
| Mobile View (In-Arena) | Optimized viewing experience, focused on close up action |

**핵심 인사이트**:
- 홈팀/원정팀 선택 가능
- In-Arena (생중계) vs Studio Show (분석 포함) 구분
- Mobile View로 모바일 최적화 옵션

**WSOPTV 적용**:
- Main Table View / Secondary Table View
- Player Focused / Rail View
- Stats Overlay 버전

---

### 슬라이드 7: Streaming Options - Languages 탭
![Slide 7](../images/nbatv-reference/slide_07.png)

**Languages 옵션**:

| 언어 | 제공사 | 설명 |
|------|--------|------|
| Spanish (Prime Video) | Prime Video | Pre-game, halftime, and post game analysis |
| Portuguese (Prime Video) | Prime Video | Pre-game, halftime, and post game analysis |

**WSOPTV 적용**:
- 20개국 언어 지원 (PRD-0002 요구사항)
- 언어별 해설 트랙 선택
- 자막 vs 더빙 옵션

---

### 슬라이드 8: 단일 경기 시청 화면 (플레이어 UI)
![Slide 8](../images/nbatv-reference/slide_08.png)

**화면 구성**:

```
┌─────────────────────────────────────────────────┐
│  RAPTORS @ LAKERS                               │
│  Lakers (In-Arena) ⚙                            │
├─────────────────────────────────────────────────┤
│                                                 │
│                [영상 영역]                       │
│                                                 │
├─────────────────────────────────────────────────┤
│ ⬜ ⬛⬛ ⬛⬛⬛⬛                                    │ ← 레이아웃 아이콘
│                                                 │
│ 🔘 Streams 10  📊 MultiView  🎯 Key Plays      │ ← 핵심 버튼
│                                                 │
│ ▶ 00:31:43 ━━━━━━━━━━━━━━━━━━━━━━━━━━ LIVE     │
└─────────────────────────────────────────────────┘
```

**핵심 버튼**:

| 버튼 | 기능 | WSOPTV 적용 |
|------|------|-------------|
| **Streams 10** | 동시 진행 경기 10개 목록 | 동시 진행 테이블 목록 |
| **MultiView** | 멀티뷰 모드 전환 | 3-Layer Multi-view |
| **Key Plays** | 주요 장면 네비게이션 | Key Hands |

---

### 슬라이드 9: 2분할 MultiView
![Slide 9](../images/nbatv-reference/slide_09.png)

**레이아웃**:

| 좌측 | 우측 |
|------|------|
| 국가 제창 "AND THE HOME OF THE BRAVE" | 경기 진행 (CHA 102 - DEN 78) |

**하단 탭**:
- Summary | Box Score | Game Charts | Play By Play

**핵심 인사이트**:
- 서로 다른 유형의 콘텐츠 동시 시청 가능
- 팀 워터마크 오버레이 (Toronto, Lakers)
- 각 뷰에 독립적인 컨트롤

---

### 슬라이드 10: 4분할 MultiView
![Slide 10](../images/nbatv-reference/slide_10.png)

**4분할 구성**:

```
┌─────────────────┬─────────────────┐
│  Lakers 로고/   │  경기 진행      │
│  팀 브랜딩      │  (코트 뷰)      │
├─────────────────┼─────────────────┤
│  하이라이트     │  경기장 전경    │
│  (슬램덩크)     │  (관중석 분위기)│
└─────────────────┴─────────────────┘
    ticketmaster | POR 84 - SAC 53 | Half 12:26
```

**핵심 인사이트**:
- 동일 경기의 다양한 앵글 또는 여러 경기
- 하단에 스폰서 + 다른 경기 스코어
- 각 뷰가 독립적인 목적

**WSOPTV 적용 (3-Layer Multi-view)**:
- Main: Feature Table
- Secondary: Table 2, 3
- Stats: 실시간 핸드 히스토리 오버레이

---

### 슬라이드 11: Key Plays 목록 모달
![Slide 11](../images/nbatv-reference/slide_11.png)

**KEY PLAYS 모달**:

```
┌─────────────────────────────────────┐
│           KEY PLAYS           [X]   │
├─────────────────────────────────────┤
│ 🖼 Smart pullup jump shot           │
│   Q1 • 11:16                        │
├─────────────────────────────────────┤
│ 🖼 Ingram running dunk              │
│   Q1 • 09:21                        │
├─────────────────────────────────────┤
│ 🖼 Murray-Boyles running layup      │
│   Q1 • 08:30                        │
├─────────────────────────────────────┤
│ 🖼 Barnes driving finger roll layup │
│   Q1 • 06:44                        │
└─────────────────────────────────────┘
```

**핵심 인사이트**:
- 썸네일 + 플레이 설명 + 타임스탬프
- 시간순 정렬 (최신 → 과거)
- 클릭 시 해당 시점으로 즉시 점프

**WSOPTV 적용 (Key Hands)**:
- All-in 상황, 블러프 캐치, Bad Beat
- Royal Flush 등 레어 핸드

---

### 슬라이드 12: Key Plays 재생 화면
![Slide 12](../images/nbatv-reference/slide_12.png)

**오버레이 UI**:
- 우측 상단: "Smart pullup jump shot" - 1 of 4 Key Plays
- 스코어: 23 vs LAL 0 | 11:18 | Q1
- 전체 화면 경기 영상 위에 Key Play 정보 오버레이

**핵심 인사이트**:
- "1 of 4 Key Plays" 네비게이션
- 재생 중에도 Key Play 정보 표시
- 다음/이전 Key Play로 빠른 이동

---

### 슬라이드 13: 경기 프리뷰/리캡 페이지
![Slide 13](../images/nbatv-reference/slide_13.png)

**페이지 구성**:

**좌측 - 기사**:
- 제목: "UP-AND-DOWN RAPTORS, BANGED-UP LAKERS CLASH IN LA"
- 날짜: Sunday, January 18th, 2026 7:28 AM
- 유형: Game Preview
- 상세 분석 기사 본문

**우측 - GAME INFO**:

| 항목 | 값 |
|------|---|
| 날짜 | Monday, January 19, 2026, 11:30 AM |
| 장소 | Crypto.com Arena, Los Angeles, CA |
| Officials | James Williams, Matt Myers, Ray Acosta |
| Broadcast | Coupang Play, League Pass |
| Radio | (라디오 링크) |
| Game Book | Download PDF |

**LINESCORES**:

| TEAM | Q1 | Q2 | Q3 | Q4 |
|------|----|----|----|----|
| TOR | 28 | 0 | 0 | 0 → 28 |
| LAL | 21 | 0 | 0 | 0 → 21 |

**상세 통계**: PTP, FB PTS, BIG LD, 3PTS, TNOV, TOV, TTOV, PST

---

### 슬라이드 14: Box Score (선수별 상세 통계)
![Slide 14](../images/nbatv-reference/slide_14.png)

**Toronto Raptors 통계**:

| PLAYER | MIN | FGM | FGA | FG% | 3PM | 3PA | 3P% | ... | PTS |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| Brandon Ingram | 10:23 | 1 | 6 | 16.7 | 0 | 3 | 0.0 | ... | 7 |
| Scottie Barnes | 06:58 | 3 | 3 | 100 | 0 | 0 | 0.0 | ... | 8 |
| Ochai Agbaji | 06:32 | 0 | 3 | 0.0 | 0 | 2 | 0.0 | ... | 8 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Los Angeles Lakers 통계**:

| PLAYER | MIN | FGM | FGA | FG% | 3PM | 3PA | 3P% | ... | PTS |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| LeBron James | 06:15 | 1 | 2 | 50.0 | 0 | 0 | 0.0 | ... | 2 |
| Luka Dončić | 10:23 | 3 | 8 | 37.5 | 2 | 4 | 50.0 | ... | 12 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**DNP (Did Not Play)**: A.J. Lawson, Alijah Martin, Jonathan Mogbo, Garrett Temple

**WSOPTV 적용 (Player Stats)**:

| PLAYER | HANDS | VPIP | PFR | 3-BET | BB WON | SHOWDOWN |
|--------|-------|------|-----|-------|--------|----------|
| Phil Hellmuth | 42 | 18% | 12% | 8% | +125 | 3 |

---

### 슬라이드 15: Shot Charts (슈팅 차트)
![Slide 15](../images/nbatv-reference/slide_15.png)

**SHOT CHARTS 구조**:

```
[Shot Plot ▼] [All Periods ▼]        Range Filter ▼

TORONTO RAPTORS              LOS ANGELES LAKERS
All Players                  All Players
□ A. Lawson - #0            □ B. James - #9
□ A. Martin - #55           □ D. Knecht - #4
□ B. Ingram - #3            □ D. Ayton - #5
...                         ...

[코트 다이어그램]            [코트 다이어그램]
 ○ Made  × Miss              ○ Made  × Miss

FG%: 57.1% (12/21)          FG%: 46.7% (7/15)
    [DOWNLOAD]                   [DOWNLOAD]
```

**핵심 인사이트**:
- 선수별 필터링 (체크박스)
- 코트 위치 기반 슛 시각화
- Made(○) vs Miss(×) 구분
- DOWNLOAD 버튼으로 데이터 내보내기

**WSOPTV 적용**:
- 포지션별 플레이 패턴
- 베팅 사이즈 분포
- 핸드 레인지 시각화

---

### 슬라이드 16: Play-by-Play
![Slide 16](../images/nbatv-reference/slide_16.png)

**Play-by-Play 구조**:

```
        [Q1]                    [ALL]
[LIVE] Auto Switch Quarter ○  Latest First ○

🦖 Toronto Raptors           🏀 Los Angeles Lakers
────────────────────────────────────────────────
                    01:37    LAL Timeout
                    01:37    L. Dončić Bad Pass
                             Out-Of-Bounds TURNOVER (2 TO)
S. Mamukelashvili   02:00
25' 3PT (12 PTS)    28-21
(B. Ingram 2 AST)
                    02:20    L. Dončić Running Layup (12 PTS)
                    25-21
                    02:27    G. Vincent STEAL (1 STL)
J. Shead Bad Pass   02:27
TURNOVER (1 TO)
```

**핵심 기능**:
- Q1 / ALL 탭 전환
- Auto Switch Quarter: 현재 쿼터 자동 전환
- Latest First: 최신순 정렬
- 양팀 플레이 타임라인 (시간, 스코어, 액션)

**WSOPTV 적용 (Hand-by-Hand)**:

| 시간 | Player 1 | Action | Player 2 |
|------|----------|--------|----------|
| 02:15 | Phil Hellmuth | 3-bet to $15,000 | |
| 02:18 | | Call | Daniel Negreanu |

---

## Triton Poker Plus 분석 (슬라이드 17-19)

### 슬라이드 17: Triton Poker Plus 표지
![Slide 17](../images/nbatv-reference/slide_17.png)

**내용**: "TRITON POKER PLUS" 타이틀

**의의**: 포커 전용 OTT 플랫폼으로, WSOPTV 개발의 직접적인 레퍼런스

---

### 슬라이드 18: Hand History 상세 화면
![Slide 18](../images/nbatv-reference/slide_18.png)

**화면 구성**:

**좌측 - 비디오 플레이어**:
- 이벤트: 2025 Triton Paradise
- 제목: **$75K POT LIMIT OMAHA 6-HANDED**
- 부제: Final Table
- 설명: Full coverage of the final table of the $75K Pot Limit Omaha 6-Handed event from Atlantis Paradise Island - The Bahamas.
- 재생 시간: 37:30 / 3:17:03
- **Players**: 참가자 아바타 목록 (7명)

**우측 - Hand History 패널**:

| 항목 | 값 |
|------|---|
| **Pot** | 1.2M (12 BBs) |
| **Level** | 50K/100K/100K |

**Hand result**:
| 플레이어 | 핸드 | 결과 | 칩 |
|----------|------|------|-----|
| Matthias Eibinger | A♠ Q♦ 8♣ 3♥ / Two Pair | -460K | 5.9M |
| Ding Biao | A♣ Q♠ 10♣ 7♥ / Two Pair | +710K | 1.2M |

**플레이어별 액션**:

| 플레이어 | 칩 | 액션 | 금액 |
|----------|-----|------|------|
| Matthias Eibinger | 5.9M | ● Call | 460K |
| Ben Lamb (BB) | 1.2M | Fold | - |
| Stephen Chidwick (SB) | 1.2M | Fold | - |
| Michael Watson (D) | 3.8M | Fold | - |
| Richard Gryko | 2.5M | Fold | - |
| **Ding Biao** | - | **● All In** | 460K |
| Dylan Weisman | 2.8M | Fold | - |
| Matthias Eibinger | 6.2M | ● Raise | 240K |
| Ben Lamb (BB) | 1.2M | ● BB | 100K |
| Stephen Chidwick (SB) | 1.2M | ● SB | 50K |
| Ben Lamb (BB) | 1.2M | ● Ante | 100K |

**네비게이션**: ◀ Hand 14 of 81 ▶

---

### 슬라이드 19: Hand Navigation 화면
![Slide 19](../images/nbatv-reference/slide_19.png)

**변경점**:
- 재생 시간: 46:38 / 3:17:03
- **Hand History** 탭 (선택됨) / Chip counts 탭
- Pot: 200K (2 BBs)
- Level: 50K/100K/100K

**플레이어 상태**:

| 플레이어 | 칩 | 액션 | 금액 |
|----------|-----|------|------|
| Michael Watson | 3.8M | ● | (Next) |
| Richard Gryko (BB) | 2.3M | ● BB | 100K |

**네비게이션**:
- ◀ **Show hand result** ▶
- Hand 19 of 81

**핵심 인사이트**:
- Hand-by-Hand 네비게이션 (81개 핸드)
- "Show hand result" 버튼으로 결과 확인
- Chip counts 탭으로 전환 가능
- 각 플레이어의 포지션 표시 (D, BB, SB)

---

## 핵심 기능 비교

### NBA TV vs Triton Poker Plus

| 기능 | NBA TV | Triton Poker Plus | WSOPTV 적용 |
|------|--------|-------------------|-------------|
| **콘텐츠 단위** | 경기 (Game) | 핸드 (Hand) | 핸드 (Hand) |
| **실시간 지표** | 스코어 | Pot, Level, Chip Count | Pot, Level, Chip Count |
| **네비게이션** | Q1/Q2/Q3/Q4 | Hand 1 of N | Hand 1 of N |
| **Key Moments** | Key Plays | Hand History | Key Hands |
| **통계** | Box Score, Shot Charts | Chip Counts, Hand Result | Player Stats, Hand History |
| **MultiView** | 2/4분할 | 비디오 + Hand History 패널 | 3-Layer Multi-view |

### Triton Poker Plus 특화 기능

| 기능 | 설명 | WSOPTV 적용 |
|------|------|-------------|
| **Hand History 패널** | 우측 고정, 실시간 업데이트 | StatsView 레이어로 구현 |
| **Chip Counts 탭** | 전체 플레이어 칩 현황 | 칩 리더보드 |
| **Hand Result** | 핸드 결과 + 핸드 카드 표시 | 핸드 결과 오버레이 |
| **Action History** | Call, Fold, Raise, All In 등 | 베팅 액션 로그 |
| **Hand Navigation** | 이전/다음 핸드 이동 | 핸드 네비게이션 |
| **Players 섹션** | 참가자 아바타 목록 | 플레이어 썸네일 |

---

## WSOPTV 적용 방안

### Phase 1: Core Features (MVP)

| 기능 | NBA TV 참조 | Triton 참조 | 구현 |
|------|------------|-------------|------|
| 메인 스트리밍 | Hero 영역 | 비디오 플레이어 | 메인 테이블 라이브 |
| Score Strip | 상단 스코어 티커 | - | 테이블별 칩 리더 |
| VOD | Game Recaps | Hand 네비게이션 | 핸드별 VOD |

### Phase 2: Advanced Mode

| 기능 | NBA TV 참조 | Triton 참조 | 구현 |
|------|------------|-------------|------|
| MultiView | 2/4분할 | 비디오 + 패널 | 3-Layer Multi-view |
| Key Moments | Key Plays | Hand History | Key Hands |
| Stats | Box Score | Chip Counts | Player Stats |

### Phase 3: Premium Features

| 기능 | NBA TV 참조 | Triton 참조 | 구현 |
|------|------------|-------------|------|
| Shot Charts | Shot Plot, Shot Zone | - | Position Charts |
| Play-by-Play | 양팀 타임라인 | Action History | Hand-by-Hand |
| Analytics | Lead Tracker | Hand Result | Chip Lead Graph |

---

## 결론

### NBA TV에서 배울 점
1. **개인화된 시청 경험**: 팀별/언어별 스트림 선택
2. **MultiView**: 여러 경기 동시 시청
3. **Key Plays**: AI 기반 하이라이트 자동 추출
4. **통계 시각화**: Box Score, Shot Charts, Play-by-Play

### Triton Poker Plus에서 배울 점
1. **Hand 중심 네비게이션**: 핸드 단위로 콘텐츠 탐색
2. **Hand History 패널**: 비디오 옆 실시간 정보 패널
3. **Chip Counts**: 전체 플레이어 칩 현황 한눈에
4. **Action History**: 베팅 액션 상세 로그

### WSOPTV 핵심 차별점
- NBA TV의 **UX 패턴** + Triton Poker Plus의 **포커 특화 기능** 결합
- **3-Layer Multi-view**: Main + Secondary + Stats
- **Key Hands**: AI 기반 중요 핸드 자동 감지
- **StatsView**: 실시간 Hand History + Chip Counts 오버레이

---

*이 문서는 WSOPTV OTT 개발을 위한 내부 분석 자료입니다.*
