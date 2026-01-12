# PRD-0004 Part 7: Migration Guide

**Part 7 of 7** | [← TypeScript Types](./06-typescript-types.md)

> Index: [PRD-0004](../0004-prd-caption-database-schema.md)

---

## 7. SQL Migration Files

### 7.1 Migration 파일 구조

```
scripts/migrations/
├── README.md                           # 사용 가이드
├── 001_create_caption_tables.sql       # PRD-0003 기본 테이블 (13개)
├── 002_extend_gfx_schema.sql           # PRD-0004 GFX 확장 (7개)
└── 003_create_views_functions.sql      # View 11개 + 함수 6개
```

### 7.2 Migration 요약

| 파일 | 테이블 | 인덱스 | View | 함수 | PRD |
|------|:------:|:------:|:----:|:----:|:---:|
| `001_create_caption_tables.sql` | 13개 | 30+ | - | - | PRD-0003 |
| `002_extend_gfx_schema.sql` | 7개 | 25+ | - | - | PRD-0004 |
| `003_create_views_functions.sql` | - | - | 11개 | 6개 | PRD-0004 |
| **합계** | **20개** | **55+** | **11개** | **6개** | - |

### 7.3 실행 방법

```bash
# PostgreSQL 접속
psql -U postgres -d wsop_graphics

# 순차 실행 (필수)
\i scripts/migrations/001_create_caption_tables.sql
\i scripts/migrations/002_extend_gfx_schema.sql
\i scripts/migrations/003_create_views_functions.sql
```

### 7.4 View 목록 (11개)

| View | 설명 | 자막 매핑 |
|------|------|----------|
| `v_tournament_leaderboard` | 전체 순위표 | Tournament Leaderboard |
| `v_feature_table_players` | 피처 테이블 플레이어 | Feature Table LB |
| `v_mini_chip_counts` | 미니 칩 카운트 | Mini Chip Counts |
| `v_player_profile` | 플레이어 프로필 | Player Profile |
| `v_at_risk_players` | 탈락 위기 플레이어 | At Risk |
| `v_recent_eliminations` | 최근 탈락자 | Elimination Banner |
| `v_chip_flow` | 칩 흐름 | Chip Flow |
| `v_vpip_stats` | VPIP/PFR 통계 | VPIP Stats |
| `v_hand_summary` | 핸드 요약 | Hand Highlight |
| `v_current_blind_level` | 현재 블라인드 | Blind Level |
| `v_l_bar_standard` | L-Bar 표준 | L-Bar |

### 7.5 함수 목록 (6개)

| 함수 | 입력 | 출력 | 용도 |
|------|------|------|------|
| `convert_gfx_card(TEXT)` | `'as'` | `'As'` | GFX 카드 형식 변환 |
| `convert_gfx_hole_cards(JSONB)` | `'["as","kh"]'` | `'AsKh'` | 홀카드 변환 |
| `calculate_bb_count(INT, INT)` | chips, bb | `DECIMAL` | BB 수 계산 |
| `calculate_avg_stack_percentage(INT, INT)` | chips, avg | `DECIMAL` | 평균 대비 % |
| `update_player_ranks(UUID)` | tournament_id | - | 순위 자동 업데이트 |
| `import_gfx_session(JSONB, UUID, UUID)` | gfx_data, ... | session_id | GFX 세션 임포트 |

### 7.6 자동 트리거

| 트리거 | 테이블 | 이벤트 | 동작 |
|--------|--------|--------|------|
| `trg_log_chip_change` | `players` | `UPDATE OF chips` | `chip_history` 자동 기록 |

### 7.7 사용 예시

```sql
-- GFX 카드 변환
SELECT convert_gfx_card('as');  -- 'As'
SELECT convert_gfx_card('10d'); -- 'Td'
SELECT convert_gfx_hole_cards('["as", "kh"]'::JSONB); -- 'AsKh'

-- BB 계산
SELECT calculate_bb_count(500000, 10000);  -- 50.00

-- 순위 업데이트
SELECT update_player_ranks('tournament-uuid-here');

-- GFX 세션 임포트
SELECT import_gfx_session(
    '{"ID": 638961999170907267, "EventTitle": "WSOP Main Event"}'::JSONB,
    'tournament-uuid',
    'feature-table-uuid'
);
```

**상세 스키마**: [scripts/migrations/README.md](../../../scripts/migrations/README.md)

---

## 8. Implementation Phases

### Phase 1: Migration 실행
- [ ] `001_create_caption_tables.sql` 실행 (PRD-0003 기본 테이블)
- [ ] `002_extend_gfx_schema.sql` 실행 (PRD-0004 GFX 테이블)
- [ ] `003_create_views_functions.sql` 실행 (View + 함수)
- [ ] 인덱스 생성 확인

### Phase 2: Type Definitions
- [ ] TypeScript 타입 정의
- [ ] Python Pydantic 모델 정의
- [ ] API Schema 정의

### Phase 3: Data Migration
- [ ] 기존 데이터 마이그레이션
- [ ] 데이터 무결성 검증

### Phase 4: Integration
- [ ] PRD-0003 워크플로우 연동
- [ ] PRD-0001 프론트엔드 연동

---

## 9. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| 26개 자막 데이터 커버리지 | 100% | 테이블 매핑 완료 |
| 쿼리 응답 시간 | < 50ms | 평균 SELECT 쿼리 |
| 데이터 무결성 | 100% | FK 제약 조건 통과 |
| 타입 안전성 | 100% | TypeScript 컴파일 오류 0 |

---

## Appendix

### A. Card Notation

```
Rank: A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2
Suit: h (hearts), d (diamonds), c (clubs), s (spades)

Examples:
- Ah = Ace of Hearts
- Ks = King of Spades
- Tc = Ten of Clubs
- 2d = Two of Diamonds

Hole Cards: AhKs (Ace of Hearts, King of Spades)
```

### B. Position Names

```
BTN = Button (Dealer)
SB = Small Blind
BB = Big Blind
UTG = Under the Gun
UTG+1, UTG+2 = Early Position
MP = Middle Position
HJ = Hijack
CO = Cutoff
```

### C. Related Documents

- [PRD-0001: WSOP Broadcast Graphics](../0001-prd-wsop-broadcast-graphics.md)
- [PRD-0003: Caption Workflow](../0003-prd-caption-workflow.md)

---

**Next Steps**:
1. Migration 스크립트 실행
2. TypeScript/Python 타입 파일 생성
3. PRD-0003 워크플로우 연동
4. Checklist 업데이트: `docs/checklists/PRD-0004.md`

---

**Previous**: [← Part 6: TypeScript Types](./06-typescript-types.md) | **Index**: [PRD-0004](../0004-prd-caption-database-schema.md)
