# PRD-0004 Part 1: Overview

**Part 1 of 7** | [Data Sources →](./02-data-sources.md)

> Index: [PRD-0004](../0004-prd-caption-database-schema.md)

---

**PRD Number**: PRD-0004
**Version**: 1.2
**Date**: 2026-01-06
**Status**: Draft
**Parent PRD**: PRD-0003 (Caption Workflow), PRD-0001 (Broadcast Graphics)

### Changelog
| Version | Date | Changes |
|---------|------|---------|
| 1.2 | 2026-01-06 | SQL migration 파일 분리 (001/002/003), View 11개 + 함수 6개 추가, 자동 트리거 추가 |
| 1.1 | 2026-01-06 | pokerGFX JSON 스키마 반영 - gfx_sessions 테이블 추가, hands/hand_actions 확장, 카드 형식 변환 규칙 추가 |
| 1.0 | 2026-01-06 | Initial PRD - 26개 자막 유형 통합 DB 스키마, 3가지 데이터 소스 통합, 15개 테이블 정의 |

### Source Documents
| Document | Location |
|----------|----------|
| PRD-0001 | [WSOP Broadcast Graphics](../0001-prd-wsop-broadcast-graphics.md) |
| PRD-0003 | [Caption Workflow](../0003-prd-caption-workflow.md) |
| PRD-0002 (Feature Table) | [GFX RFID 기술 상세](../../../../automation_feature_table/tasks/prds/PRD-0002-primary-gfx-rfid.md) |

---

## 1. Purpose & Context

### 1.1 Background

PRD-0003에서 정의된 10개 테이블을 확장하여, PRD-0001의 **26개 자막 유형 전체**를 지원하는 완전한 DB 스키마를 정의합니다.

**기존 PRD-0003 범위**:
- 10개 핵심 테이블 정의
- 데이터 수집 워크플로우 정의
- 이벤트 트리거 시스템

**PRD-0004 확장 범위**:
- 15개 테이블로 확장 (5개 신규)
- 26개 자막 유형별 데이터 매핑 완성
- 3가지 데이터 소스 통합 스키마
- TypeScript 타입 정의 포함

### 1.2 Goals

1. **완전한 스키마 정의**: 26개 자막 유형 전체 커버
2. **데이터 소스 통합**: pokerGFX JSON, WSOP+ CSV, 수기 입력 통합
3. **ERD 시각화**: Mermaid 다이어그램 포함
4. **타입 안전성**: TypeScript/Python 타입 정의

### 1.3 Non-Goals

- 데이터 수집 워크플로우 (PRD-0003 담당)
- 자막 디자인/컴포넌트 (PRD-0001 담당)
- 마이그레이션 스크립트 실행 (별도 작업)

---

## Document Structure

| Part | Document | Description |
|:----:|----------|-------------|
| **1** | **Overview (현재)** | Purpose, Goals, Changelog |
| 2 | [Data Sources](./02-data-sources.md) | pokerGFX JSON, WSOP+ CSV, 수기 입력 |
| 3 | [Database Schema](./03-database-schema.md) | ERD, 20개 테이블 목록, Core Tables |
| 4 | [GFX Tables](./04-gfx-tables.md) | gfx_sessions, hands, hand_players 등 |
| 5 | [Caption Mapping](./05-caption-mapping.md) | 26개 자막-테이블 매핑 매트릭스 |
| 6 | [TypeScript Types](./06-typescript-types.md) | Core/Entity/Payload 타입 정의 |
| 7 | [Migration Guide](./07-migration-guide.md) | Migration 파일 구조, 실행 방법 |

---

**Next**: [Part 2: Data Sources →](./02-data-sources.md)
