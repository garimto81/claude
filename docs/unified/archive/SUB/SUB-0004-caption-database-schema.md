# PRD-0004: Caption Database Schema (Index)

**PRD Number**: PRD-0004
**Version**: 1.3
**Date**: 2026-01-08
**Status**: Draft
**Parent PRD**: PRD-0003 (Caption Workflow), PRD-0001 (Broadcast Graphics)

---

## Document Structure

| Part | Document | Description |
|:----:|----------|-------------|
| 1 | [Overview](./0004/01-overview.md) | Purpose, Goals, Non-Goals, Changelog |
| 2 | [Data Sources](./0004/02-data-sources.md) | pokerGFX JSON, WSOP+ CSV, 수기 입력 통합 |
| 3 | [Database Schema](./0004/03-database-schema.md) | ERD, 21개 테이블 목록, Core Tables |
| 4 | [GFX Tables](./0004/04-gfx-tables.md) | gfx_sessions, hands, hand_players 등 |
| 5 | [Caption Mapping](./0004/05-caption-mapping.md) | 26개 자막-테이블 매핑 매트릭스 |
| 6 | [TypeScript Types](./0004/06-typescript-types.md) | Core/Entity/Payload 타입 정의 |
| 7 | [Migration Guide](./0004/07-migration-guide.md) | Migration 파일 구조, 실행 방법 |
| 8 | [Supabase Integration](./0004/08-supabase-integration.md) | 스키마 분리, RLS, Realtime, API 접근 |
| 9 | [Import Pipeline](./0004/09-pokergfx-import-pipeline.md) | pokerGFX JSON 파싱, UPSERT 전략 |

---

## Quick Summary

### 스키마 구조
- **스키마**: `wsop` (Caption 시스템), `public` (AEP 분석 - 기존)
- **총 테이블**: 21개 (wsop 스키마)
- **View**: 7개, **함수**: 5개, **트리거**: 8개

### 테이블 구성
| Phase | 테이블 | 설명 |
|-------|--------|------|
| Phase 1 | venues, events, tournaments, blind_levels, payouts, commentators, schedules | Core Reference (7개) |
| Phase 2 | players_master, player_instances, feature_tables, player_stats | Player System (4개) |
| Phase 3 | gfx_sessions, hands, hand_players, hand_actions, hand_cards, chip_flow | Hand System (6개) |
| Phase 4 | graphics_queue, eliminations, soft_contents, clip_markers | Broadcast System (4개) |

### 데이터 소스
| 소스 | 범위 | 테이블 |
|------|------|--------|
| pokerGFX JSON | Feature Table RFID | gfx_sessions, hands, hand_players, hand_actions, hand_cards |
| WSOP+ CSV | 대회 정보 + Other Tables | tournaments, players_master, payouts, blind_levels |
| 수기 입력 | 자동화 불가 정보 | player profiles, commentators, events |

### 자막 커버리지
- **26개 자막 유형** 전체 지원
- [상세 매핑 →](./0004/05-caption-mapping.md)

---

## Related Documents

| Document | Description |
|----------|-------------|
| [PRD-0001](./0001-prd-wsop-broadcast-graphics.md) | WSOP Broadcast Graphics System |
| [PRD-0003](./0003-prd-caption-workflow.md) | Caption Generation Workflow |
| [Migration README](../scripts/migrations/README.md) | SQL Migration 가이드 |

## Quick Links

- [Checklist](../docs/checklists/PRD-0004.md)
- [Migration Scripts](../scripts/migrations/)

---

### Changelog
| Version | Date | Changes |
|---------|------|---------|
| 1.3 | 2026-01-08 | Supabase `wsop` 스키마 분리 적용, Part 8-9 추가 (Supabase Integration, Import Pipeline) |
| 1.2 | 2026-01-06 | SQL migration 파일 분리, View 11개 + 함수 6개, 문서 청킹 (7개 파트) |
| 1.1 | 2026-01-06 | pokerGFX JSON 스키마 반영, gfx_sessions 테이블 추가 |
| 1.0 | 2026-01-06 | Initial PRD - 26개 자막 유형 통합 DB 스키마 |
