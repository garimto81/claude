# EBS Console Flutter Mock App 전면 재구현 계획

## 배경 (Background)

### 요청 내용
PRD v1.0.0 기준 3-column 레이아웃(Sidebar 220px + Preview + SettingsPanel 320px)을 PRD v1.1.0의 **Full-Width Stacked** 레이아웃(Header 40px → Preview 744px → TabBar 36px → TabContent 260px)으로 전면 재구현한다.

### 해결하려는 문제
- 레이아웃 구조가 근본적으로 변경됨 (3-column → 수직 4단 스택)
- GFX 서브섹션 4/6 → 6/6 (Numbers, Rules 누락)
- Mock 데이터 모델이 PRD 대비 심각하게 빈약 (6개 필드 vs 30+ 필드)
- Glassmorphism 디자인 토큰 미적용
- 키보드 단축키 2/11개, Command Palette 7/15+ 명령
- RFID 3안테나 상세, System Diagnostics, Config Export/Import 전체 누락

## 구현 범위 (Scope)

### 포함 항목
1. Full-Width Stacked 레이아웃 셸 (Header + Preview + TabBar + TabContent)
2. Header 재설계: Table 드롭다운 + RFID/CPU/GPU 인디케이터 + Quick Actions 4개 + Cmd+K + LIVE 뱃지
3. Preview 전폭 16:9 (744px, Chroma Key Blue + POT + 9 플레이어 슬롯)
4. TabBar 신규 (Sources/Outputs/GFX/System, 36px, accentGold 언더라인)
5. Sources 탭 확장: 7칼럼 테이블 + Board Sync + Crossfade + Audio Input
6. Outputs 탭 확장: Color Space + Bit Depth + NDI
7. GFX 탭 6 서브섹션: Layout, Card & Player, Animation, Numbers(신규), Rules(신규), Branding
8. System 탭 확장: RFID 3안테나 상세 + Diagnostics + Config Export/Import + Startup
9. Command Palette 확장: 3카테고리 15+ 명령 + 퍼지 매칭
10. Mock 데이터 6모델 전체 재작성 (MockGameState, MockPlayer, MockSystemState, MockGfxSettings, MockSourcesSettings, MockOutputsSettings)
11. Riverpod Provider 전면 재작성 (StateNotifier 기반)
12. 키보드 단축키 11개
13. Glassmorphism 디자인 토큰 (blur 12px + glassShadow + neonGlow)
14. 접기/펼치기(Collapse/Expand) 공통 위젯
15. SpinnerInput, PrecisionDropdown, RfidAntennaCard, DiagnosticPanel 신규 위젯

### 제외 항목
- Rive 애니메이션 (별도 Phase로 분리 — .riv 파일 제작 필요)
- 반응형 Breakpoint (1920px 고정 기준으로 구현, 반응형은 후속)
- 실제 백엔드 연동 (RFID, WebSocket, NDI, Game Engine)
- Action Tracker (AT) 앱

## 아키텍처 결정 (Architecture Decisions)

### AD-1: 레이아웃 구조
```
  Column (전체 화면)
  +---------------------------------------------+
  |  AppHeader (40px, 고정)                       |
  +---------------------------------------------+
  |  LivePreview (Expanded, 16:9 비율 유지)       |
  +---------------------------------------------+
  |  EbsTabBar (36px, 고정)                       |
  +---------------------------------------------+
  |  TabContent (260px, 고정, 내부 스크롤)         |
  +---------------------------------------------+
```

### AD-2: 상태 관리 구조
- 기존: 개별 `StateProvider` 30+ 개 (flat)
- 변경: 도메인별 `StateNotifierProvider` 6개 (MockGameState, MockSystemState, MockGfxSettings, MockSourcesSettings, MockOutputsSettings, AppUIState)
- 이유: 관련 상태를 그룹핑하여 일관성 보장, provider 수 축소

### AD-3: GFX 서브섹션 접기/펼치기
- `CollapsibleSection` 공통 위젯 생성
- 각 섹션 독립 `StateProvider<bool>` (expanded/collapsed)
- 기본값: Layout만 펼침, 나머지 접힘

### AD-4: 파일 구조 (PRD Section 6 준수)
```
  ebs_console/lib/
  ├── main.dart                          (재작성)
  ├── app.dart                           (신규)
  ├── theme/
  │   ├── ebs_theme.dart                 (수정: Glassmorphism)
  │   └── ebs_colors.dart                (수정: 토큰 확장)
  ├── models/
  │   ├── mock_game_state.dart           (신규)
  │   ├── mock_player.dart               (신규)
  │   ├── mock_system_state.dart         (신규)
  │   ├── mock_gfx_settings.dart         (신규)
  │   ├── mock_sources_settings.dart     (신규)
  │   └── mock_outputs_settings.dart     (신규)
  ├── providers/
  │   ├── game_state_provider.dart       (신규)
  │   ├── system_state_provider.dart     (신규)
  │   ├── tab_provider.dart              (신규)
  │   ├── gfx_settings_provider.dart     (신규)
  │   ├── sources_provider.dart          (신규)
  │   └── outputs_provider.dart          (신규)
  ├── screens/
  │   ├── console_screen.dart            (재작성)
  │   └── command_palette.dart           (확장)
  ├── widgets/
  │   ├── header/
  │   │   └── app_header.dart            (재작성)
  │   ├── preview/
  │   │   ├── live_preview.dart          (수정: 전폭)
  │   │   └── player_slot.dart           (수정: 확장 필드)
  │   ├── panel/
  │   │   ├── tab_bar.dart               (신규)
  │   │   ├── sources_tab.dart           (확장)
  │   │   ├── outputs_tab.dart           (확장)
  │   │   ├── gfx_tab.dart               (재작성)
  │   │   ├── system_tab.dart            (재작성)
  │   │   └── gfx_sections/
  │   │       ├── layout_section.dart         (신규)
  │   │       ├── card_player_section.dart    (신규)
  │   │       ├── animation_section.dart      (신규)
  │   │       ├── numbers_section.dart        (신규)
  │   │       ├── rules_section.dart          (신규)
  │   │       └── branding_section.dart       (신규)
  │   └── common/
  │       ├── ebs_badge.dart             (재활용)
  │       ├── ebs_toggle.dart            (재활용)
  │       ├── ebs_button.dart            (재활용)
  │       ├── segment_toggle.dart        (재활용)
  │       ├── setting_row.dart           (재활용)
  │       ├── color_swatch_widget.dart   (재활용)
  │       ├── status_indicator.dart      (재활용)
  │       ├── ebs_dropdown.dart          (재활용)
  │       ├── collapsible_section.dart   (신규)
  │       ├── spinner_input.dart         (신규)
  │       ├── precision_dropdown.dart    (신규)
  │       ├── rfid_antenna_card.dart     (신규)
  │       └── diagnostic_panel.dart      (신규)
  └── (삭제)
      ├── widgets/sidebar/sidebar.dart
      ├── widgets/status_bar/status_bar.dart
      ├── widgets/panel/settings_panel.dart
      ├── models/mock_data.dart
      └── providers/app_providers.dart
```

## 영향 파일 (Affected Files)

### 삭제 파일 (5개)
| 파일 | 이유 |
|------|------|
| `C:\claude\figma\ebs_console\lib\widgets\sidebar\sidebar.dart` | Sidebar 제거 (Header 드롭다운 대체) |
| `C:\claude\figma\ebs_console\lib\widgets\status_bar\status_bar.dart` | StatusBar 제거 (Header 통합) |
| `C:\claude\figma\ebs_console\lib\widgets\panel\settings_panel.dart` | 3-column Panel 제거 (TabContent 대체) |
| `C:\claude\figma\ebs_console\lib\models\mock_data.dart` | 단일 파일 → 6개 모델 파일로 분리 |
| `C:\claude\figma\ebs_console\lib\providers\app_providers.dart` | flat providers → 6개 도메인별 provider로 분리 |

> **PRD 참고**: PRD 섹션 6 삭제 목록에 `table_list.dart`, `quick_actions.dart`, `connection_status.dart`가 명시되었으나 실제 코드베이스에 미존재하여 제외.

### 신규 파일 (24개)
| 파일 | 설명 |
|------|------|
| `lib/app.dart` | MaterialApp + Theme 설정 |
| `lib/models/mock_game_state.dart` | GameState + Player 확장 모델 |
| `lib/models/mock_player.dart` | 17필드 Player 모델 |
| `lib/models/mock_system_state.dart` | SystemState + RfidAntenna + Diagnostics |
| `lib/models/mock_gfx_settings.dart` | GFX 6섹션 전체 설정 모델 |
| `lib/models/mock_sources_settings.dart` | Sources 설정 모델 |
| `lib/models/mock_outputs_settings.dart` | Outputs 설정 모델 |
| `lib/providers/game_state_provider.dart` | GameState StateNotifier |
| `lib/providers/system_state_provider.dart` | SystemState StateNotifier |
| `lib/providers/tab_provider.dart` | 탭 + UI 상태 |
| `lib/providers/gfx_settings_provider.dart` | GFX 설정 StateNotifier |
| `lib/providers/sources_provider.dart` | Sources 설정 StateNotifier |
| `lib/providers/outputs_provider.dart` | Outputs 설정 StateNotifier |
| `lib/widgets/panel/tab_bar.dart` | 4탭 바 (36px) |
| `lib/widgets/panel/gfx_sections/layout_section.dart` | GFX Layout 서브섹션 |
| `lib/widgets/panel/gfx_sections/card_player_section.dart` | GFX Card & Player |
| `lib/widgets/panel/gfx_sections/animation_section.dart` | GFX Animation |
| `lib/widgets/panel/gfx_sections/numbers_section.dart` | GFX Numbers (신규) |
| `lib/widgets/panel/gfx_sections/rules_section.dart` | GFX Rules (신규) |
| `lib/widgets/panel/gfx_sections/branding_section.dart` | GFX Branding |
| `lib/widgets/common/collapsible_section.dart` | 접기/펼치기 공통 위젯 |
| `lib/widgets/common/spinner_input.dart` | +/- 버튼 숫자 입력 |
| `lib/widgets/common/precision_dropdown.dart` | Chipcount Precision 드롭다운 |
| `lib/widgets/common/rfid_antenna_card.dart` | RFID 안테나 상태 카드 |
| `lib/widgets/common/diagnostic_panel.dart` | 진단 지표 패널 |
| `lib/widgets/preview/player_slot.dart` | live_preview.dart에서 추출 — holeCards, equity, action, position 확장 |

### 수정 파일 (8개)
| 파일 | 변경 내용 |
|------|----------|
| `lib/main.dart` | ProviderScope + App() 호출로 단순화 |
| `lib/theme/ebs_colors.dart` | Glassmorphism 토큰 추가 (glassShadow, neonGlow, equityBar), sidebarWidth/panelWidth 제거 |
| `lib/theme/ebs_theme.dart` | Glassmorphism 기반 ThemeData 재구성 |
| `lib/screens/console_screen.dart` | 3-column → Full-Width Stacked + 키보드 단축키 11개 |
| `lib/screens/command_palette.dart` | 15+ 명령 + 퍼지 매칭 + blur dimming |
| `lib/widgets/header/app_header.dart` | Table 드롭다운 + RFID/CPU/GPU 인디케이터 + Quick Actions |
| `lib/widgets/preview/live_preview.dart` | 전폭 16:9, boardCards, sidePots 표시 |

> **참고**: `player_slot.dart`는 기존에 독립 파일로 존재하지 않음 (`live_preview.dart` 내부 private 클래스). 신규 파일로 추출 (아래 신규 파일 목록 참조).

## 위험 요소 (Risks)

### R-1: 대규모 파일 동시 수정 충돌 (HIGH)
- **영향**: 같은 파일을 수정하는 에이전트가 동시 실행 시 충돌
- **완화**: Wave 기반 순차 실행, 파일 의존성 그래프에 따라 분리

### R-2: Provider 마이그레이션 중 런타임 에러 (MEDIUM)
- **영향**: 기존 `StateProvider` → `StateNotifierProvider` 전환 시 기존 위젯의 ref.watch 호출이 깨짐
- **완화**: Wave 1에서 모든 model/provider를 먼저 완성한 후 Wave 2에서 위젯 수정

### R-3: GFX Numbers/Rules 섹션 복잡도 과소평가 (MEDIUM)
- **영향**: Numbers 섹션만 8영역 독립 드롭다운 + 3 표시 모드 = 24+ 위젯 조합
- **완화**: precision_dropdown.dart 공통 위젯으로 반복 패턴 추출

### R-4: Glassmorphism blur 성능 (LOW)
- **영향**: BackdropFilter(blur: 12px)이 Desktop에서 프레임 드롭 유발 가능
- **완화**: blur를 Preview 영역에는 적용하지 않고, TabContent와 Header에만 선택 적용

### Edge Case 1: 빈 플레이어 슬롯 (seat 2,4,6,7,8)
- 기존: `isEmpty` getter로 단순 체크
- 확장: `isEliminated`, `isFolded` 상태 추가 → 3가지 "비활성" 표현 필요 (빈/접힘/탈락)

### Edge Case 2: Command Palette 퍼지 매칭 오탐
- `del 30` → `delay 30` (정상)
- `del` → `delay` vs `delete` (모호)
- 완화: Levenshtein distance 기반, 거리 동일 시 카테고리 우선순위 적용

## 태스크 목록 (Tasks)

### Wave 0: 정리 (삭제 + 스캐폴딩)
> **의존**: 없음. 후속 Wave의 전제 조건.

- [ ] **T0.1**: `sidebar.dart`, `status_bar.dart`, `settings_panel.dart` 삭제
  - 파일: `C:\claude\figma\ebs_console\lib\widgets\sidebar\sidebar.dart`, `status_bar\status_bar.dart`, `panel\settings_panel.dart`
  - AC: 3파일 삭제, import 참조 제거 (console_screen.dart에서)

- [ ] **T0.2**: `ebs_colors.dart` Glassmorphism 토큰 확장
  - 파일: `C:\claude\figma\ebs_console\lib\theme\ebs_colors.dart`
  - 변경: `glassShadow`, `neonGlow`, `equityBar` 추가, `sidebarWidth`/`panelWidth`/`statusBarHeight` 제거, `tabBarHeight: 36`, `tabContentHeight: 260`, `previewHeight: 744` 추가
  - AC: 빌드 에러 없음

- [ ] **T0.3**: 디렉토리 구조 생성
  - `lib/models/`, `lib/providers/`, `lib/widgets/panel/gfx_sections/` 디렉토리
  - AC: 모든 디렉토리 존재

### Wave 1: 데이터 레이어 (Model + Provider)
> **의존**: Wave 0 완료. 위젯 레이어의 전제 조건.
> **병렬 가능**: T1.1~T1.6 (모델 6개) 동시 실행 가능. T1.7~T1.12 (프로바이더)는 모델 완료 후.

- [ ] **T1.1**: `mock_game_state.dart` 작성
  - PRD 3.1 기준 16필드 (tableName, gameType, gamePhase, handNumber, potAmount, sidePots, smallBlind, bigBlind, ante, boardCards, players, activePlayers, winningHandName, isLive, delay)
  - AC: 모든 필드 PRD 3.1과 1:1 매칭

- [ ] **T1.2**: `mock_player.dart` 작성
  - PRD 3.2 기준 17필드
  - AC: 모든 필드 PRD 3.2와 1:1 매칭

- [ ] **T1.3**: `mock_system_state.dart` + `MockRfidAntenna` + `MockDiagnostics` 작성
  - PRD 3.3 기준
  - AC: antennas 3개 (Upcard, Muck, Community), diagnostics 4지표

- [ ] **T1.4**: `mock_gfx_settings.dart` 작성
  - PRD 3.4 기준 — Layout, Numbers, Rules, Animation, Branding 전체
  - AC: chipPrecision 8영역, displayMode 3영역, leaderboard 6옵션 모두 포함

- [ ] **T1.5**: `mock_sources_settings.dart` 작성
  - PRD 3.5 기준 9필드
  - AC: boardSyncOffsetX/Y, crossfadeDuration, audioInput 포함

- [ ] **T1.6**: `mock_outputs_settings.dart` 작성
  - PRD 3.6 기준 10필드
  - AC: colorSpace, bitDepth, ndiOutput 포함

- [ ] **T1.7**: `game_state_provider.dart` 작성
  - StateNotifierProvider + mock 초기 데이터
  - AC: ref.watch(gameStateProvider) 정상 동작

- [ ] **T1.8**: `system_state_provider.dart` 작성
  - AC: antennas, diagnostics provider 포함

- [ ] **T1.9**: `tab_provider.dart` 작성
  - activeTabProvider + commandPaletteVisibleProvider + GFX 섹션 접기 상태 6개
  - AC: 탭 전환, 팔레트 표시, 섹션 접기 상태 관리 가능

- [ ] **T1.10**: `gfx_settings_provider.dart` 작성
  - AC: chipPrecision, displayMode 등 Map 기반 상태 업데이트

- [ ] **T1.11**: `sources_provider.dart` 작성
  - AC: chromaKey, boardSync 상태 변경 가능

- [ ] **T1.12**: `outputs_provider.dart` 작성
  - AC: resolution, colorSpace, bitDepth 상태 변경 가능

- [ ] **T1.13**: `mock_data.dart` 삭제 + `app_providers.dart` 삭제
  - AC: 기존 파일 제거, 새 provider 파일로 완전 대체

### Wave 2: 레이아웃 셸 + Header + TabBar + Preview
> **의존**: Wave 1 완료.
> **병렬 가능**: T2.1 (셸) 먼저 → T2.2/T2.3/T2.4 동시 가능

- [ ] **T2.1**: `console_screen.dart` 재작성 (Full-Width Stacked)
  - Column: AppHeader + Expanded(LivePreview) + EbsTabBar + SizedBox(260, TabContent)
  - 키보드 단축키 11개 바인딩
  - AC: 4영역 분할 렌더링, 탭 전환 동작, Cmd+1~4/Cmd+K/Cmd+R/Cmd+C/Cmd+L/Cmd+H/Ctrl+?/Esc 동작

- [ ] **T2.2**: `app_header.dart` 재작성
  - 좌: EBS 로고 + Table 드롭다운 (3 mock 테이블)
  - 중: RFID(dot) + CPU(%) + GPU(%) 인디케이터
  - 우: Reset Hand / Register Deck / Launch AT / Hide GFX 버튼 + Cmd+K + LIVE 뱃지
  - AC: 3영역 배치, 드롭다운 동작, 인디케이터 mock 수치 표시

- [ ] **T2.3**: `tab_bar.dart` 신규
  - Sources / Outputs / GFX / System 4탭
  - 활성 탭: accentGold 하단 2px 언더라인
  - AC: 탭 클릭 전환, 활성 탭 시각적 구분

- [ ] **T2.4**: `live_preview.dart` 수정
  - 전폭 16:9, Chroma Key Blue (#0000FF) 배경
  - POT 표시 (sidePots 포함), 9 플레이어 슬롯
  - AC: 16:9 비율 유지, POT 금액 표시, 플레이어 이름/스택/position 표시

- [ ] **T2.5**: `main.dart` + `app.dart` 재작성
  - main.dart: ProviderScope + runApp(EbsApp())
  - app.dart: MaterialApp + EbsTheme + ConsoleScreen
  - AC: 앱 정상 부팅

### Wave 3: 공통 위젯 (신규)
> **의존**: Wave 1 (모델 참조).
> **병렬 가능**: T3.1~T3.5 모두 독립, 동시 실행 가능

- [ ] **T3.1**: `collapsible_section.dart`
  - title + isExpanded + onToggle + child
  - 셰브론 아이콘 회전 애니메이션
  - AC: 접기/펼치기 토글, 셰브론 90도 회전

- [ ] **T3.2**: `spinner_input.dart`
  - value + min + max + step + suffix + onChanged
  - [-] value [+] 레이아웃
  - AC: +/- 클릭 시 값 변경, min/max 범위 제한

- [ ] **T3.3**: `precision_dropdown.dart`
  - label + value + items(Exact/Smart/Smart+Extra) + onChanged
  - 8영역 독립 사용 가능
  - AC: 드롭다운 선택 변경

- [ ] **T3.4**: `rfid_antenna_card.dart`
  - MockRfidAntenna 데이터 표시: name, power(dBm), sensitivity, heartbeat, status
  - status별 색상: OK=success, WEAK=warning, OFFLINE=danger
  - AC: 3안테나 카드 렌더링, 상태별 색상 표시

- [ ] **T3.5**: `diagnostic_panel.dart`
  - MockDiagnostics 4지표 표시: signalStrength, accuracy, latency, dropRate
  - 프로그레스 바 시각화
  - AC: 4지표 숫자+바 표시

### Wave 4: 탭 콘텐츠 (Sources + Outputs)
> **의존**: Wave 1 + Wave 3.
> **병렬 가능**: T4.1, T4.2 동시 가능 (서로 다른 파일)

- [ ] **T4.1**: `sources_tab.dart` 확장
  - 7칼럼 테이블: L / R / Source / Format / Cycle / Status / Action
  - Board Sync: Offset X/Y 슬라이더 (SpinnerInput 사용)
  - Chroma Key: Enable + Color + 강도 슬라이더
  - ATEM Control: IP + 소스 선택 (비활성 표시)
  - Crossfade: SpinnerInput (초)
  - Audio Input: 드롭다운
  - AC: 7칼럼 렌더링, Board Sync/Crossfade/Audio 동작

- [ ] **T4.2**: `outputs_tab.dart` 확장
  - Resolution: Video Size 드롭다운 + 9x16 토글 + Frame Rate
  - Live Pipeline: NDI / DeckLink / Audio Preview 드롭다운
  - Fill & Key: Enable + Key Color + 듀얼 미니 프리뷰
  - Color Space: BT.709 / BT.2020 드롭다운
  - Bit Depth: 8-bit / 10-bit 드롭다운
  - AC: 모든 드롭다운/토글 동작, Color Space/Bit Depth 표시

### Wave 5: GFX 탭 6 서브섹션
> **의존**: Wave 3 (CollapsibleSection, SpinnerInput, PrecisionDropdown).
> **병렬 가능**: T5.1~T5.6 모두 독립 파일, 동시 실행 가능 (최대 4개 Wave)

- [ ] **T5.1**: `gfx_tab.dart` 재작성 + `layout_section.dart`
  - gfx_tab.dart: 6개 CollapsibleSection을 SingleChildScrollView로 감싸기
  - layout_section.dart: Board Position, Player Layout, X/Top/Bot Margin, Heads Up Custom Y
  - AC: 6섹션 스크롤, Layout 섹션 접기/펼치기

- [ ] **T5.2**: `card_player_section.dart`
  - Reveal Players (Immediate/Delayed), Show Fold + Delay Time, Reveal Cards (6가지)
  - Show Heads Up History, Action Clock threshold
  - AC: 모든 드롭다운 + SpinnerInput 동작

- [ ] **T5.3**: `animation_section.dart`
  - Transition In/Out (Fade/Slide/Pop/Expand) + Time
  - Indent/Bounce Action Player 토글
  - AC: 4개 Transition 타입 선택, 시간 SpinnerInput

- [ ] **T5.4**: `numbers_section.dart` (신규, 가장 복잡)
  - Chipcount Precision: 8영역 독립 PrecisionDropdown
  - Display Mode: 3영역 (Amount/BB Multiple/Both)
  - Currency: Symbol 드롭다운 + Trailing + Divide by 100 토글
  - AC: 8개 PrecisionDropdown 독립 동작, 3개 DisplayMode 드롭다운, Currency 5종

- [ ] **T5.5**: `rules_section.dart` (신규)
  - Game Rules: Move button, Limit Raises, Straddle/Sleeper
  - Display: Equity timing, Player ordering, Winning hand, Add seat#, Show eliminated, Rabbit Hunting, Side pot
  - Leaderboard: 6옵션 토글
  - Outs/Equity: Show Outs position, True Outs, Score Strip mode
  - AC: 토글 15+ 개 동작, 드롭다운 4+ 개 동작

- [ ] **T5.6**: `branding_section.dart`
  - Sponsor Logo x2 (드롭존), Vanity text, Replace with Game Variant
  - Blinds display 4옵션, Show hand# with blinds
  - AC: 드롭존 2개, 드롭다운 1개, 토글 2개

### Wave 6: System 탭 확장
> **의존**: Wave 3 (RfidAntennaCard, DiagnosticPanel).

- [ ] **T6.1**: `system_tab.dart` 재작성
  - RFID 3안테나 상세: RfidAntennaCard x 3
  - Table: Name + Password + Reset + Calibrate + Update 버튼
  - Action Tracker: Allow Access 토글
  - Diagnostics: DiagnosticPanel + System Log 레벨 필터 + Export Folder
  - Config: Export / Import 버튼 쌍
  - Startup: Auto Start + Auto Connect + Default Theme
  - AC: 3안테나 카드 표시, 진단 4지표, Export/Import 버튼 렌더링

### Wave 7: Command Palette + 테마 + 최종 통합
> **의존**: Wave 2~6 완료.

- [ ] **T7.1**: `command_palette.dart` 확장
  - 배경 dimming + blur, 560px 모달
  - 3카테고리 (OVERLAY, SYSTEM, RFID) 15+ 명령
  - 퍼지 매칭: Levenshtein distance 기반
  - Footer 키보드 힌트
  - AC: 15+ 명령 목록, 퍼지 매칭 `del 30` → `delay 30` 동작, ESC 닫기

- [ ] **T7.2**: `ebs_theme.dart` Glassmorphism 적용
  - BackdropFilter(blur: 12px), glassShadow, neonGlow
  - Header/TabBar/TabContent에 선택 적용
  - AC: blur 효과 시각적 확인

- [ ] **T7.3**: `player_slot.dart` 확장
  - holeCards 표시 (카드 이미지 또는 텍스트)
  - equity 바, position 뱃지, action/amount 표시
  - isFolded/isAllIn/isEliminated 시각 상태
  - AC: 9 슬롯 중 활성 플레이어에 모든 필드 표시

- [ ] **T7.4**: 빌드 검증 + 전체 통합 테스트
  - `flutter build windows` 성공
  - 모든 탭 전환, 드롭다운, 토글, 접기/펼치기 동작 확인
  - 키보드 단축키 11개 동작 확인
  - AC: 빌드 성공, 런타임 에러 0건

### Wave 8: 비주얼 품질 (designer 전담)
> **의존**: Wave 7 완료 (기능 동작 확인 후).

- [ ] **T8.1**: Glassmorphism 전체 적용 검증
  - blur 12px + glassShadow + neonGlow 일관성
  - 색상 토큰 PRD v3.0 기준 검증

- [ ] **T8.2**: 타이포그래피 검증
  - Inter (UI) + JetBrains Mono (데이터) 일관성
  - 폰트 사이즈/웨이트 PRD 기준 검증

- [ ] **T8.3**: 레이아웃 픽셀 퍼펙트 검증
  - Header 40px, TabBar 36px, TabContent 260px 정확성
  - Preview 16:9 비율 정확성

## 커밋 전략 (Commit Strategy)

| Wave | 커밋 메시지 |
|------|------------|
| 0 | `refactor(console): v1.0 레이아웃 제거 + Glassmorphism 토큰 확장` |
| 1 | `feat(console): mock 데이터 6모델 + provider 재작성` |
| 2 | `feat(console): Full-Width Stacked 레이아웃 셸 + Header + TabBar` |
| 3 | `feat(console): 공통 위젯 5개 추가 (collapsible, spinner, precision, rfid, diagnostic)` |
| 4 | `feat(console): Sources + Outputs 탭 PRD v1.1 확장` |
| 5 | `feat(console): GFX 탭 6 서브섹션 전체 구현 (Numbers, Rules 포함)` |
| 6 | `feat(console): System 탭 RFID 3안테나 + Diagnostics 확장` |
| 7 | `feat(console): Command Palette 15+ 명령 + 키보드 단축키 11개 + 통합` |
| 8 | `style(console): Glassmorphism + 타이포그래피 + 레이아웃 비주얼 검증` |

## 요약

| 항목 | 수치 |
|------|------|
| 총 태스크 | 33개 |
| 총 Wave | 9개 (Wave 0~8) |
| 삭제 파일 | 5개 |
| 신규 파일 | 24개 |
| 수정 파일 | 8개 |
| 예상 복잡도 | **HIGH** |
| 핵심 위험 | Provider 마이그레이션 런타임 에러, GFX Numbers/Rules 복잡도 |
