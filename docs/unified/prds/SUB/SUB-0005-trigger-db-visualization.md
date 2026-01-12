# PRD: Trigger Event & DB Table Visualization

**PRD Number**: PRD-0005
**Version**: 1.0
**Date**: 2026-01-06
**Status**: Draft
**Parent PRD**: PRD-0003 (Caption Workflow), PRD-0004 (Caption Database Schema)

### Changelog
| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-06 | 섹션 2.3 추가 - 트리거 → DB → 자막 인과관계 다이어그램 |
| 1.0 | 2026-01-06 | 초기 PRD - 트리거 이벤트/DB 테이블 트리 구조 시각화 |

---

## 1. Purpose & Context

### 1.1 Background

PRD-0003 (Caption Workflow)과 PRD-0004 (Caption Database Schema)에서 정의된 **8개 트리거 이벤트**와 **20개 DB 테이블**의 관계를 직관적으로 이해할 수 있는 시각화 자료가 필요합니다.

**현재 문제**:
- 텍스트 기반 매트릭스는 전체 관계 파악이 어려움
- 트리거 → 자막 → DB 테이블의 3단계 연결 관계가 복잡함
- 개발자/PM이 빠르게 참조할 수 있는 시각 자료 부재

### 1.2 Goals

1. **트리거 이벤트 트리**: 8개 이벤트 → 26개 자막 → DB 테이블 연결 시각화
2. **DB 스키마 트리**: 20개 테이블 헤더 구조 및 자막 매핑 시각화
3. **인터랙티브 HTML**: 개발자가 로컬에서 참조 가능한 목업

---

## 2. Visualization Structure

### 2.1 Trigger Events Tree

8개 트리거 이벤트를 우선순위별로 분류하고, 연결된 자막과 DB 테이블을 표시합니다.

![Trigger Events Tree](/docs/unified/images/sub-0005/trigger-event-tree.png)

**[HTML 원본 보기](../../docs/mockups/PRD-0005/trigger-event-tree.html)**

#### 2.1.1 HIGH Priority Events (4개)

| Event | Description | Triggered Captions | DB Tables |
|-------|-------------|-------------------|-----------|
| `hand_completed` | 핸드 종료 시 | Tournament LB, Mini Chip, Chip Flow | players, chip_history, hand_actions |
| `level_change` | 레벨 변경 시 | Blind Level, L-Bar, Tournament LB, Event Info | blind_levels, tournaments |
| `player_eliminated` | 플레이어 탈락 시 | Elimination Banner, Mini Payouts, Tournament LB | players, payouts, eliminations |
| `all_in_detected` | 올인 감지 시 | At Risk, Chip Comparison | players, payouts, chip_history |

#### 2.1.2 MEDIUM Priority Events (2개)

| Event | Description | Triggered Captions | DB Tables |
|-------|-------------|-------------------|-----------|
| `feature_table_change` | 피처 테이블 변경 | Feature Table LB, Player Profile, Chip Stack Bar | feature_tables, players, player_profiles |
| `itm_reached` | ITM 진입 시 | Payouts, Tournament Info | payouts, tournaments |

#### 2.1.3 LOW Priority Events (2개)

| Event | Description | Triggered Captions | DB Tables |
|-------|-------------|-------------------|-----------|
| `day_start` | Day 시작 시 | Tournament Info, Event Info, Schedule | tournaments, events, schedules |
| `break_end` | 브레이크 종료 시 | Chips In Play, Blind Level | blind_levels, tournaments |

---

### 2.2 DB Schema Tree

20개 테이블의 헤더 구조와 자막 매핑을 카드 형태로 시각화합니다.

![DB Table Schema](/docs/unified/images/sub-0005/db-table-schema.png)

**[HTML 원본 보기](../../docs/mockups/PRD-0005/db-table-schema.html)**

#### 2.2.1 테이블 그룹별 분류

| Group | Tables | 주요 자막 |
|-------|--------|----------|
| **Core Reference** (4) | venues, events, commentators, schedules | Venue, Event Name, Commentator, Schedule |
| **Tournament** (3) | tournaments, blind_levels, payouts | Tournament Info, Blind Level, Payouts |
| **Player** (6) | players, player_profiles, player_stats, chip_history, hand_actions, eliminations | All Player/Stats captions |
| **Graphics Queue** (1) | graphics_queue | All 26 captions |

#### 2.2.2 핵심 테이블 헤더 요약

**players**
```
player_id (PK) | name | nationality | chips | current_rank | seat_number
```

**chip_history**
```
history_id (PK) | player_id (FK) | hand_number | chips | chips_change | bb_count
```

**payouts**
```
payout_id (PK) | place_start | place_end | amount | is_current_bubble
```

**blind_levels**
```
level_id (PK) | level_number | small_blind | big_blind | ante | duration_minutes
```

---

### 2.3 Causality Flow (인과관계)

트리거 이벤트와 DB 테이블은 **독립적이지 않고 직접적인 인과관계**가 있습니다.

![Causality Flow](/docs/unified/images/sub-0005/causality-flow.png)

**[HTML 원본 보기](../../docs/mockups/PRD-0005/causality-flow.html)**

#### 2.3.1 인과관계 흐름

```
Event 발생 → DB Write (상태 변경) → DB Read (데이터 조회) → Caption 렌더링
```

#### 2.3.2 구체적 예시 (8개 전체)

**HIGH Priority (4개)**

| 트리거 이벤트 | DB Write (변경) | DB Read (조회) | 생성 자막 |
|--------------|-----------------|----------------|-----------|
| `hand_completed` | INSERT `chip_history` | SELECT `chip_history`, `players` | Chip Flow, Tournament LB |
| `level_change` | UPDATE `tournaments.current_level` | SELECT `blind_levels` | Blind Level, L-Bar |
| `player_eliminated` | INSERT `eliminations` | SELECT `eliminations`, `payouts` | Elimination Banner, Mini Payouts |
| `all_in_detected` | INSERT `hand_actions` (all-in) | SELECT `players`, `payouts` | At Risk, Chip Comparison |

**MEDIUM / LOW Priority (4개)**

| 트리거 이벤트 | DB Write (변경) | DB Read (조회) | 생성 자막 |
|--------------|-----------------|----------------|-----------|
| `feature_table_change` | UPDATE `feature_tables.is_active` | SELECT `players`, `player_profiles` | Feature Table LB, Player Profile |
| `itm_reached` | UPDATE `tournaments.is_itm` | SELECT `payouts`, `tournaments` | Payouts, Tournament Info |
| `day_start` | UPDATE `tournaments.current_day` | SELECT `events`, `schedules` | Tournament Info, Broadcast Schedule |
| `break_end` | UPDATE `tournaments.is_on_break` | SELECT `blind_levels`, `tournaments` | Chips In Play, Blind Level |

#### 2.3.3 핵심 인사이트

> **트리거 이벤트는 단순히 자막을 "트리거"하는 것이 아니라, 먼저 DB 상태를 변경(Write)합니다.
> 그 후 변경된 데이터를 조회(Read)하여 자막을 생성합니다.
> 따라서 트리거 이벤트와 DB 테이블은 직접적인 인과관계가 있습니다.**

---

## 3. File Structure

```
docs/
├── mockups/
│   └── PRD-0005/
│       ├── trigger-event-tree.html    # 트리거 이벤트 트리 (인터랙티브)
│       ├── db-table-schema.html       # DB 스키마 트리 (인터랙티브)
│       └── causality-flow.html        # 인과관계 흐름 (인터랙티브)
├── images/
│   └── PRD-0005/
│       ├── trigger-event-tree.png     # 트리거 이벤트 스크린샷
│       ├── db-table-schema.png        # DB 스키마 스크린샷
│       └── causality-flow.png         # 인과관계 흐름 스크린샷
└── checklists/
    └── PRD-0005.md                    # Checklist
```

---

## 4. Use Cases

### 4.1 개발자 참조

- **상황**: `hand_completed` 이벤트 처리 로직 작성
- **참조**: 트리거 트리에서 연결된 자막(Tournament LB, Chip Flow) 확인
- **결과**: 필요한 DB 테이블(players, chip_history) 즉시 파악

### 4.2 PM/기획자 리뷰

- **상황**: 새로운 자막 유형 추가 검토
- **참조**: DB 스키마 트리에서 기존 테이블 구조 확인
- **결과**: 추가 컬럼 필요 여부 판단

---

## 5. Related PRDs

| PRD | 관계 |
|-----|------|
| PRD-0003 | 트리거 이벤트 & 자막 매핑 정의 (데이터 소스) |
| PRD-0004 | DB 스키마 상세 정의 (테이블 구조 소스) |
| PRD-0001 | 26개 자막 유형 정의 (자막 목록 소스) |

---

## Appendix: Google Sheets 연동

이 시각화 데이터는 Google Sheets로도 관리됩니다:
- **스프레드시트**: [WSOP Caption Types - 26개 자막 유형](https://docs.google.com/spreadsheets/d/1P8m2uTjOfwyLk1aaSevYJNHSGm9OWH5YoPtc5WxOkdE/edit)
- **생성 스크립트**: `scripts/create_caption_sheet.py`

