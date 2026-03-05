---
doc_type: "prd"
doc_id: "EBS-Flutter-Console-Mock"
version: "1.1.0"
status: "active"
owner: "BRACELET STUDIO"
created: "2026-03-05"
updated: "2026-03-05"
depends_on:
  - "EBS-UI-Design-v3.prd.md (UI 설계 원본)"
  - "figma/mockups/index.html (HTML Hi-Fi 프로토타입)"
  - "pokergfx-prd-v2.md (22개 게임 변형, GFX 3서브탭)"
  - "pokergfx-reverse-engineering-complete.md (GameTypeData 79필드, ConfigurationPreset 99+필드)"
  - "pokergfx-v3.2-complete-whitepaper.md (GFX1/2/3 요소, Sources/Outputs/System)"
---

# EBS Console Flutter Mock App PRD

## 1. 개요

### 1.1 목적

HTML Hi-Fi 목업(`figma/mockups/console/`)과 PRD v3.0의 Console 설계를 **Flutter Desktop (Windows)** 앱으로 구현한다. 모든 백엔드 기능(RFID, WebSocket, NDI, Game Engine)은 mock 데이터로 대체하여 **UI만 검증** 가능한 인터랙티브 프로토타입을 만든다.

### 1.2 범위

| 포함 | 제외 |
|------|------|
| Console 6화면 (C01-C06) | Action Tracker (AT) |
| Mock 데이터 레이어 (6 모델) | 실제 RFID/WebSocket 연동 |
| 탭 전환/네비게이션 | Overlay 렌더링 엔진 |
| Rive 상태 애니메이션 (11개) | NDI/DeckLink 출력 |
| Dark Glassmorphism 테마 | 실제 비디오 입력 |
| GFX 6 서브섹션 전체 | 실제 게임 엔진 로직 |
| 키보드 단축키 (8개) | 멀티 테이블 동시 제어 |
| Command Palette (15+ 명령) | 실제 ATEM 통신 |

### 1.3 기술 스택

| 항목 | 선택 |
|------|------|
| Framework | Flutter 3.41+ (Desktop Windows) |
| 언어 | Dart |
| 상태 관리 | Riverpod |
| 애니메이션 | Rive + Flutter 내장 |
| 폰트 | Inter (UI) + JetBrains Mono (데이터) |
| 디자인 | PRD v3.0 색상 토큰 + Glassmorphism |

## 2. 화면 설계

### 2.1 공통 레이아웃 — Full-Width Stacked

```
+--[EBS]--[Table v]--[RFID][CPU][GPU]--[Reset][Deck][AT][Hide]--+
|                                                                |  40px  Header
+----------------------------------------------------------------+
|                                                                |
|                  PREVIEW (전폭, 16:9)                          |
|                  Chroma Key Blue (#0000FF)                     |  744px  Preview
|                  오버레이 실시간 렌더링                         |
|                                                                |
+---[Sources]---[Outputs]---[GFX]---[System]---------------------+
|                                                                |  36px  Tab Bar
+----------------------------------------------------------------+
|                                                                |
|            탭 콘텐츠 영역 (스크롤 가능)                        |  260px  Tab Content
|                                                                |
+----------------------------------------------------------------+
```

**구조 상세 (1920x1080 기준)**:

| 영역 | 높이 | 너비 | 설명 |
|------|------|------|------|
| Header | 40px | 전폭 | 로고+테이블 선택+상태 인디케이터+Quick Actions |
| Preview | 744px | 전폭 (16:9 비율 유지) | Chroma Key Blue 캔버스, 오버레이 렌더링 |
| Tab Bar | 36px | 전폭 | Sources/Outputs/GFX/System 4탭 |
| Tab Content | 260px | 전폭 | 선택된 탭의 설정 패널 (스크롤 가능) |

**Header Bar (40px) 구성**:

- 좌측: EBS 로고 + Table 드롭다운 (테이블 선택)
- 중앙: 상태 인디케이터 — RFID(연결상태), CPU(%), GPU(%)
- 우측: Quick Actions — [Reset Hand] [Register Deck] [Launch AT] [Hide GFX] + [Cmd+K] LIVE 뱃지

**Preview 영역 (744px)**:

- 전폭 16:9 Chroma Key Blue 캔버스
- 오버레이 요소 실시간 표시: POT, 플레이어 슬롯 9개, 보드 카드
- 클릭 인터랙션: 오버레이 요소 클릭 → GFX 탭으로 전환 + 해당 요소 설정 포커스

**Tab Bar (36px)**:

- Sources / Outputs / GFX / System 4탭
- 활성 탭: accentGold 언더라인
- Cmd+1~4 단축키로 탭 전환

**Tab Content (260px)**:

- 각 탭별 설정 패널이 수직 스크롤 가능하게 표시
- 서브섹션은 접기/펼치기(Collapse/Expand) 지원

**삭제되는 요소 (v1.0.0 대비)**:

| 삭제 요소 | 이동 대상 |
|-----------|----------|
| Sidebar (220px) | Header의 Table 드롭다운 |
| Quick Actions (사이드바) | Header 우측 |
| Connection 상태 (사이드바) | Header 중앙 인디케이터 |
| 우측 Panel (320px) | Tab Content로 통합 |
| Status Bar (36px) | Header에 통합 (RFID/CPU/GPU → Header 중앙, Hand# → Preview 오버레이, Delay → LIVE 뱃지 옆) |

### 2.2 C01 Main (Dashboard)

- **Header**: EBS 로고, Table 드롭다운(3개 mock 테이블), RFID/CPU/GPU 인디케이터, Quick Actions 4개, Cmd+K, LIVE 뱃지
- **Preview**: 전폭 16:9, Chroma Key Blue, POT 표시, 플레이어 슬롯 9개
- **Tab Bar**: Sources 탭 기본 활성
- **Tab Content**: Sources 탭 설정 표시

### 2.3 C02 Sources 탭 확장

- **Video Sources 테이블** 7칼럼: L / R / Source / Format / Cycle / Status / Action
- **Board Sync 보정**: Offset X/Y 슬라이더
- **Chroma Key**: Enable 토글 + Color 스와치 + 강도 슬라이더
- **ATEM Control**: IP 입력 + 소스 선택 (비활성 표시)
- **Crossfade**: 스피너 (초 단위)
- **Audio Input**: 드롭다운 (Default, HDMI 1, USB Audio)

### 2.4 C03 Outputs 탭 확장

- **Resolution**: Video Size 드롭다운 + 9x16 세로 토글 + Frame Rate
- **Live Pipeline**: NDI / DeckLink / Audio Preview 드롭다운
- **Fill & Key**: Enable 토글 + Key Color + 듀얼 미니 프리뷰
- **Color Space**: BT.709 / BT.2020 드롭다운
- **Bit Depth**: 8-bit / 10-bit 드롭다운

### 2.5 C04 GFX 탭 — 6 서브섹션

GFX 탭은 단일 스크롤 패널로 6개 서브섹션을 포함한다. 각 섹션은 접기/펼치기 가능.

```
GFX 탭 (단일 스크롤 패널)
+-- LAYOUT (GFX1 유래)
|   Board Position (Left/Centre/Right)
|   Player Layout (Horizontal, Vert/Bot/Spill, Vert/Bot/Fit,
|                  Vert/Top/Spill, Vert/Top/Fit)
|   X/Top/Bot Margin (% 스피너)
|   Heads Up Custom Y pos
|
+-- CARD & PLAYER (GFX1 유래)
|   Reveal Players (Immediate/Delayed)
|   Show Fold (Immediate/Action On/After Bet/Action On+Next)
|     + Fold Delay Time
|   Reveal Cards (6가지: Immediate ~ Showdown-Tourney)
|   Show Heads Up History, Action Clock threshold
|
+-- ANIMATION (GFX1 유래)
|   Transition In (Fade/Slide/Pop/Expand) + Time (0.1~5.0초)
|   Transition Out (동일) + Time
|   Indent Action Player, Bounce Action Player
|
+-- NUMBERS (GFX3 유래)
|   Chipcount Precision 8영역 독립 설정
|     (Exact/Smart/Smart+Extra):
|     Player Stack, Player Action, Pot, Blinds,
|     Leaderboard, Chipcounts, Ticker, Twitch Bot
|   Display Mode 3영역 (Amount/BB Multiple/Both):
|     Chipcounts, Pot, Bets
|   Currency: Symbol ($, EUR, GBP, JPY, KRW),
|     Trailing toggle, Divide by 100
|
+-- RULES (GFX2 유래)
|   Game Rules: Move button after Bomb Pot,
|     Limit Raises, Straddle/Sleeper
|   Display: Equity show timing, Player ordering,
|     Winning hand highlight, Add seat#,
|     Show eliminated, Allow Rabbit Hunting,
|     Display side pot
|   Leaderboard 6옵션: knockout rank, chipcount%,
|     eliminated, cumulative, hide on hand, max BB
|   Outs/Equity: Show Outs position,
|     True Outs, Score Strip mode
|
+-- BRANDING (GFX1 유래)
    Sponsor Logo x2
    Vanity text + Replace with Game Variant
    Blinds display (Never/Every Hand/New Level/With Strip)
    Show hand# with blinds
```

### 2.6 C05 System 탭 확장

- **RFID 3안테나 상세**: Upcard / Muck / Community 각각
  - Power (dBm), Sensitivity (0.0~1.0), Heartbeat, Status (OK/WEAK/OFFLINE)
- **Table**: Name + Password + Reset + Calibrate + Update 버튼
- **Action Tracker**: Allow Access 토글
- **Diagnostics**:
  - Table Diagnostics: dBm / 정확도 / 레이턴시 / 드롭율
  - System Log: 레벨 필터 (DEBUG/INFO/WARN/ERROR)
  - Export Folder 경로
- **Config**: Export / Import 버튼 쌍
- **Startup**: Auto Start + Auto Connect + Default Theme

### 2.7 C06 Command Palette 확장

- 배경 dimming + blur, 560px 모달, ESC 닫기

**3카테고리 명령 테이블**:

| 카테고리 | 명령 예시 |
|---------|----------|
| OVERLAY | show gfx, hide gfx, toggle overlay, show leaderboard, show equity |
| SYSTEM | reset hand, theme dark/light, output 1080p/720p, delay 30, export config |
| RFID | calibrate, antenna 1/2/3, reset rfid |

- 15+ 명령 지원
- 퍼지 매칭: `del 30` → `delay 30`으로 자동 매칭
- Footer: 키보드 힌트 가이드

### 2.8 키보드 단축키

| 단축키 | 동작 |
|--------|------|
| Cmd+K | Command Palette 열기 |
| Cmd+1 | Sources 탭 |
| Cmd+2 | Outputs 탭 |
| Cmd+3 | GFX 탭 |
| Cmd+4 | System 탭 |
| Cmd+R | Reset Hand |
| Cmd+C | Calibrate RFID |
| Cmd+L | Leaderboard 토글 |
| Cmd+H | Hide GFX 토글 |
| Ctrl+? | 단축키 가이드 |
| Esc | 모달/팔레트 닫기 |

### 2.9 반응형 Breakpoint

| Breakpoint | Preview 높이 | Tab Content 높이 | 비고 |
|-----------|-------------|-----------------|------|
| >= 1920px | 744px | 260px | 전폭 스택, 기본 사이즈 |
| 1280~1919px | 비율 축소 | 220px | 전폭 스택 유지 |
| 1024~1279px | 최소 비율 | 200px | 전폭 스택, 최소 지원 |
| < 1024px | — | — | 미지원 (최소 해상도) |

## 3. Mock 데이터 설계

### 3.1 MockGameState 확장

```dart
class MockGameState {
  String tableName;          // "Main Event #3"
  String gameType;           // "NLHE", "PLO", "PLO5", "SHORT_DECK"
  String gamePhase;          // PRE_FLOP, FLOP, TURN, RIVER, SHOWDOWN
  int handNumber;            // 247
  int potAmount;             // 2450
  List<int> sidePots;        // [1200, 800]
  int smallBlind;            // 50
  int bigBlind;              // 100
  int ante;                  // 0
  List<String> boardCards;   // ["As", "Kh", "7d", "", ""]
  List<MockPlayer> players;  // 9 slots
  int activePlayers;         // 6
  String? winningHandName;   // "Full House, Aces full of Kings"
  bool isLive;               // true
  Duration delay;            // Duration(seconds: 28)
}
```

### 3.2 MockPlayer 확장

```dart
class MockPlayer {
  int seat;              // 1-9
  String name;           // "KIM"
  int stack;             // 48200
  List<String> holeCards; // ["Ah", "Ks"]
  String position;       // "BTN", "SB", "BB", "UTG", etc.
  double? equity;        // 0.65
  bool isActive;         // true
  bool isDealer;         // false
  bool isFolded;         // false
  bool isAllIn;          // false
  bool isEliminated;     // false
  String? action;        // "BET", "CALL", "FOLD"
  int? actionAmount;     // 200
  String? country;       // "KR"
}
```

### 3.3 MockSystemState 확장

```dart
class MockSystemState {
  bool rfidConnected;     // true
  bool atConnected;       // true
  bool engineOk;          // true
  double cpuUsage;        // 0.12
  double gpuUsage;        // 0.35
  double memUsage;        // 0.45
  String cameraMode;      // "STATIC"
  bool chromaKeyEnabled;  // true
  Color chromaKeyColor;   // Color(0xFF0000FF)
  List<MockRfidAntenna> antennas; // 3개
  MockDiagnostics diagnostics;
}

class MockRfidAntenna {
  String name;          // "Upcard", "Muck", "Community"
  bool isConnected;
  int power;            // dBm
  double sensitivity;   // 0.0~1.0
  Duration heartbeat;
  String status;        // "OK", "WEAK", "OFFLINE"
}

class MockDiagnostics {
  double signalStrength;  // dBm
  double accuracy;        // %
  double latency;         // ms
  double dropRate;        // %
}
```

### 3.4 MockGfxSettings (신규)

```dart
class MockGfxSettings {
  // Layout
  String boardPosition;    // "Left", "Centre", "Right"
  String playerLayout;     // "Horizontal", "Vert/Bot/Spill", etc.
  double xMargin;          // %
  double topMargin;        // %
  double botMargin;        // %
  double headsUpCustomY;

  // Numbers
  Map<String, String> chipPrecision; // 8영역: "Exact"/"Smart"/"Smart+Extra"
  Map<String, String> displayMode;   // 3영역: "Amount"/"BB Multiple"/"Both"
  String currencySymbol;   // "$", "EUR", "GBP", "JPY", "KRW"
  bool trailingZeros;
  bool divideBy100;

  // Rules
  bool moveButtonAfterBombPot;
  int limitRaises;
  bool straddleEnabled;
  bool sleeperEnabled;
  String equityShowTiming;
  String playerOrdering;
  bool winningHandHighlight;
  bool addSeatNumber;
  bool showEliminated;
  bool allowRabbitHunting;
  bool displaySidePot;

  // Leaderboard
  bool knockoutRank;
  bool chipcountPercent;
  bool showEliminatedLeaderboard;
  bool cumulativeScore;
  bool hideOnHand;
  int maxBBDisplay;

  // Animation
  String transitionIn;     // "Fade", "Slide", "Pop", "Expand"
  double transitionInTime; // 0.1~5.0
  String transitionOut;
  double transitionOutTime;
  bool indentActionPlayer;
  bool bounceActionPlayer;

  // Branding
  String? sponsorLogo1;
  String? sponsorLogo2;
  String vanityText;
  bool replaceWithGameVariant;
  String blindsDisplay;     // "Never", "Every Hand", "New Level", "With Strip"
  bool showHandWithBlinds;
}
```

### 3.5 MockSourcesSettings (신규)

```dart
class MockSourcesSettings {
  String cameraMode;      // "STATIC", "DYNAMIC"
  bool chromaKeyEnabled;
  Color chromaKeyColor;
  double chromaKeyIntensity;
  double crossfadeDuration;
  String? atemIp;         // null = 비활성
  String audioInput;      // "Default", "HDMI 1", "USB Audio"
  double boardSyncOffsetX;
  double boardSyncOffsetY;
}
```

### 3.6 MockOutputsSettings (신규)

```dart
class MockOutputsSettings {
  String videoSize;       // "1920x1080", "1280x720"
  bool verticalMode;      // 9x16
  int frameRate;          // 30, 60
  String ndiOutput;       // "Disabled", "NDI 1", "NDI 2"
  String deckLinkOutput;  // "Disabled", "DeckLink 1"
  String audioPreview;    // "Default", "Monitor"
  bool fillAndKeyEnabled;
  Color keyColor;
  String colorSpace;      // "BT.709", "BT.2020"
  String bitDepth;        // "8-bit", "10-bit"
}
```

## 4. 색상 토큰

### 4.1 PRD v3.0 기본 토큰

| 토큰 | Hex | 용도 |
|------|-----|------|
| bgPrimary | #0D0D1A | 메인 배경 |
| bgSecondary | #1A1A2E | 헤더 |
| bgTertiary | #16213E | 설정 패널 |
| accentGold | #D4AF37 | 주요 강조 |
| accentBlue | #00D4FF | 보조 강조 |
| accentNeon | #FF6B35 | 알림/경고 |
| textPrimary | #FFFFFF | 주요 텍스트 |
| textSecondary | #A0A0B0 | 보조 텍스트 |
| textMuted | #606070 | 비활성 텍스트 |
| success | #4CAF50 | 연결 성공 |
| danger | #FF4444 | 에러/LIVE |
| warning | #FFC107 | 경고/딜레이 |

### 4.2 Glassmorphism 토큰 (신규)

| 토큰 | 값 | 용도 |
|------|-----|------|
| glassBg | rgba(13,13,26,0.65) | 반투명 배경 |
| glassBlur | 12px | 배경 블러 |
| glassBorder | rgba(255,255,255,0.08) | 유리 테두리 |
| glassShadow | rgba(0,0,0,0.3) | 유리 그림자 |
| neonGlow | rgba(0,212,255,0.15) | 네온 글로우 |
| equityBar | #00D4FF | 에쿼티 바 |

## 5. Rive 애니메이션

### 5.1 기존 (v1.0.0)

| 요소 | 애니메이션 | 상태 머신 |
|------|----------|----------|
| Status Indicator | pulse (live), steady (active), dim (idle) | 3-state |
| LIVE Badge | pulse-red 1.5s infinite | 1-state loop |
| Toggle Switch | slide + color transition | on/off |
| Tab Underline | slide-x to active tab | position-based |
| Sidebar Item | hover highlight + active gold border | 3-state |

### 5.2 추가 (v1.1.0)

| 요소 | 애니메이션 | 상태 머신 |
|------|----------|----------|
| Fold Fadeout | opacity 1→0.3 + desaturate | trigger |
| All-in Glow | neon pulse ring | 1-state loop |
| Equity Bar Fill | width 0→equity% | value-based |
| Card Reveal Flip | 3D Y-axis rotation 180° | trigger |
| Action Clock Countdown | circular progress 100→0% | timer-based |
| Section Collapse | height animate + chevron rotate | toggle |

## 6. 파일 구조

```
ebs_console/
  lib/
    main.dart
    app.dart
    theme/
      ebs_theme.dart
      ebs_colors.dart
    models/
      mock_game_state.dart
      mock_player.dart
      mock_system_state.dart
      mock_gfx_settings.dart        # 신규
      mock_sources_settings.dart     # 신규
      mock_outputs_settings.dart     # 신규
    providers/
      game_state_provider.dart
      system_state_provider.dart
      tab_provider.dart
      gfx_settings_provider.dart     # 신규
      sources_provider.dart          # 신규
      outputs_provider.dart          # 신규
    screens/
      console_screen.dart            # Full-Width Stacked 레이아웃으로 재작성
      command_palette.dart
    widgets/
      header/
        app_header.dart              # Table 드롭다운 + 상태 인디케이터 + Quick Actions 통합
      preview/
        live_preview.dart            # 전폭 16:9로 변경
        player_slot.dart
      panel/
        tab_bar.dart                 # 신규: Sources/Outputs/GFX/System 탭 바 (36px)
        sources_tab.dart
        outputs_tab.dart
        gfx_tab.dart
        system_tab.dart
        gfx_sections/                # 신규
          layout_section.dart
          card_player_section.dart
          animation_section.dart
          numbers_section.dart
          rules_section.dart
          branding_section.dart
      common/
        ebs_badge.dart
        ebs_toggle.dart
        ebs_button.dart
        segment_toggle.dart
        setting_row.dart
        status_indicator.dart
        color_swatch.dart
        spinner_input.dart           # 신규
        precision_dropdown.dart      # 신규
        rfid_antenna_card.dart       # 신규
        diagnostic_panel.dart        # 신규
  pubspec.yaml
```

**삭제 (v1.0.0 대비)**:

- `widgets/sidebar/` 전체 (sidebar.dart, table_list.dart, quick_actions.dart, connection_status.dart)
- `widgets/status_bar/` 전체 (status_bar.dart)

## 7. 구현 우선순위

| 순서 | 항목 | 설명 |
|:----:|------|------|
| 1 | Theme + Colors + 공통 위젯 | Glassmorphism 토큰 + Spinner/Dropdown 위젯 |
| 2 | Full-Width Stacked 레이아웃 셸 | Header(40px) + Preview(744px) + TabBar(36px) + TabContent(260px) |
| 3 | Header Bar | 로고+Table 드롭다운+상태 인디케이터+Quick Actions+LIVE 뱃지 |
| 4 | Live Preview (전폭 16:9) | Chroma Key Blue + POT + 플레이어 슬롯 9개 |
| 5 | Tab Bar + 탭 전환 | 4탭 + 활성 언더라인 + Cmd+1~4 단축키 |
| 6 | Sources 탭 | 7칼럼 테이블 + Chroma Key + ATEM(비활성) |
| 7 | Outputs 탭 | Fill & Key 듀얼 프리뷰 + 9x16 토글 |
| 8 | GFX 탭 (6 서브섹션) | Layout, Card&Player, Animation, Numbers, Rules, Branding |
| 9 | System 탭 | RFID 3안테나 + 진단 + Config Export/Import |
| 10 | Command Palette (Cmd+K) | 3카테고리 + 15+ 명령 + 퍼지 매칭 |
| 11 | 키보드 단축키 | 8개 바인딩 |
| 12 | Mock 데이터 전체 연동 | 확장 모델 6개 + 상태 변경 시연 |

## 8. 검증 기준

| 항목 | 기준 |
|------|------|
| 레이아웃 | Full-Width Stacked 4영역 정확히 분할 |
| 색상 | PRD v3.0 토큰 + Glassmorphism 6개 적용 |
| 폰트 | Inter + JetBrains Mono |
| 인터랙션 | 탭 전환, 토글, 접기/펼치기 동작 |
| 반응성 | 1920x1080 기준, 1024px 최소 |
| Mock 데이터 | 모든 화면에 의미 있는 샘플 데이터 표시 |
| GFX 서브섹션 | 6개 모두 스크롤+접기 가능 |
| Numbers | 8영역 독립 드롭다운 + 3 표시 모드 |
| RFID | 3안테나 상태 카드 + 진단 지표 |
| Command Palette | 3카테고리 + 퍼지 매칭 |
| 단축키 | 8개 이상 동작 |
| 비활성 요소 | ATEM, NDI 등 비활성 상태 표시 |

## Changelog

| 날짜 | 버전 | 변경 내용 | 결정 근거 |
|------|------|-----------|----------|
| 2026-03-05 | v1.1.0 | 레이아웃 Full-Width Stacked 전면 재설계, GFX 탭 6서브섹션, Mock 데이터 6모델, 색상/애니메이션/파일구조 확장 | pokergfx-prd-v2 + reverse-engineering + whitepaper 분석 반영 |
| 2026-03-05 | v1.0.0 | 최초 작성 | HTML 목업 + PRD v3.0 분석 기반 |
