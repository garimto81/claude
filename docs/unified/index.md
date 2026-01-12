# Unified Document Index

> Last updated: 2026-01-12

통합 문서 관리 시스템. 5개 프로젝트의 모든 문서를 한 곳에서 관리합니다.

## 폴더 구조

```
C:\claude\docs\unified\
├── prds/           # PRD 문서 (37개)
├── specs/          # 기술 명세서 (4개)
├── tasks/          # 작업 문서 (6개)
├── archive/        # 아카이브 (12개)
├── checklists/     # 체크리스트
├── images/         # 이미지
├── mockups/        # HTML 목업
├── index.md        # 이 파일
└── registry.json   # 메타데이터
```

## Quick Stats

| Namespace | 설명 | PRD | Spec | Task | Archive |
|-----------|------|:---:|:----:|:----:|:-------:|
| **MAIN** | Claude Root 프로젝트 | 10 | - | 3 | - |
| **HUB** | Automation Hub (공유 인프라) | 6 | - | - | 2 |
| **FT** | Feature Table (RFID 처리) | 10 | - | - | - |
| **SUB** | Subtitle System (방송 그래픽) | 6 | 4 | - | 10 |
| **AE** | After Effects 자동화 | 6 | - | 1 | - |
| **Total** | | **38** | **4** | **4** | **12** |

---

## By Priority

### P0 (Critical)

| ID | Title | Namespace |
|----|-------|-----------|
| [HUB-0001](./prds/HUB/HUB-0001-automation-hub-v2.md) | WSOP Automation Hub v2.0 | HUB |
| [HUB-0003](./prds/HUB/HUB-0003-model-unification.md) | 프로젝트 간 모델 통합 | HUB |
| [HUB-0005](./prds/HUB/HUB-0005-production-workflow.md) | GG Production 자막 워크플로우 | HUB |
| [HUB-0006](./prds/HUB/HUB-0006-mvp-schedule-management.md) | MVP 일정 관리 시스템 | HUB |
| [FT-0001](./prds/FT/FT-0001-poker-hand-auto-capture.md) | 포커 핸드 자동 캡처 | FT |
| [FT-0002](./prds/FT/FT-0002-primary-gfx-rfid.md) | Primary Layer - GFX RFID | FT |
| [FT-0005](./prds/FT/FT-0005-integrated-db-subtitle-system.md) | 통합 DB 및 자막 시스템 | FT |
| [FT-0011](./prds/FT/FT-0011-gfx-direct-supabase-sync.md) | GFX → Supabase 직접 동기화 | FT |
| [SUB-0001](./prds/SUB/SUB-0001-wsop-broadcast-graphics.md) | WSOP Broadcast Graphics | SUB |
| [SUB-0003](./prds/SUB/SUB-0003-caption-workflow.md) | Caption Generation Workflow | SUB |
| [SUB-0007](./prds/SUB/SUB-0007-4schema-database-design.md) | 4-Schema Database Design | SUB |
| [AE-0001](./prds/AE/AE-0001-ae-automation.md) | After Effects 자동화 시스템 | AE |
| [MAIN-0025](./prds/MAIN/MAIN-0025-master-workflow-optimization.md) | 전역 워크플로우 최적화 | MAIN |

### P1 (High)

| ID | Title | Namespace |
|----|-------|-----------|
| [HUB-0002](./prds/HUB/HUB-0002-conflict-monitoring.md) | 충돌/중복 모니터링 | HUB |
| [HUB-0004](./prds/HUB/HUB-0004-frontend-dashboard.md) | 프론트엔드 대시보드 | HUB |
| [FT-0003](./prds/FT/FT-0003-secondary-gemini-live.md) | Gemini Live API | FT |
| [FT-0004](./prds/FT/FT-0004-fusion-engine.md) | Fusion Engine | FT |
| [FT-0007](./prds/FT/FT-0007-custom-rfid-client.md) | 자체 RFID 클라이언트 | FT |
| [FT-0008](./prds/FT/FT-0008-monitoring-dashboard.md) | 모니터링 대시보드 | FT |
| [FT-0010](./prds/FT/FT-0010-nas-smb-integration.md) | NAS SMB 연동 | FT |
| [SUB-0002](./prds/SUB/SUB-0002-workflow-automation.md) | Workflow Automation | SUB |
| [SUB-0005](./prds/SUB/SUB-0005-trigger-db-visualization.md) | Trigger-DB Visualization | SUB |
| [SUB-0006](./prds/SUB/SUB-0006-aep-data-elements.md) | AEP Data Elements | SUB |
| [AE-0002](./prds/AE/AE-0002-pokergfx-db-schema.md) | PokerGFX DB Schema | AE |
| [AE-0003a](./prds/AE/AE-0003a-ae-mode-switcher.md) | AE 모드 전환 시스템 | AE |
| [AE-0003b](./prds/AE/AE-0003b-ae-mapping-schema.md) | AE 템플릿 매핑 스키마 | AE |
| [AE-0004](./prds/AE/AE-0004-sheets-sync.md) | Google Sheets 동기화 | AE |
| [AE-0005](./prds/AE/AE-0005-cyprus-db-schema.md) | CyprusDesign DB Schema | AE |
| [MAIN-0024](./prds/MAIN/MAIN-0024-agent-causality-analysis.md) | 에이전트 인과관계 분석 | MAIN |
| [MAIN-0026](./prds/MAIN/MAIN-0026-token-management.md) | 토큰 관리 계획 | MAIN |
| [MAIN-0027](./prds/MAIN/MAIN-0027-skills-migration.md) | Skills 마이그레이션 | MAIN |
| [MAIN-0028](./prds/MAIN/MAIN-0028-tdd-enhancement.md) | TDD 워크플로우 강화 | MAIN |
| [MAIN-0030](./prds/MAIN/MAIN-0030-documentation-sync.md) | 문서 동기화 | MAIN |

### P2 (Medium)

| ID | Title | Namespace |
|----|-------|-----------|
| [FT-0009](./prds/FT/FT-0009-gfx-json-simulator.md) | GFX JSON Simulator | FT |
| [MAIN-0029](./prds/MAIN/MAIN-0029-github-actions.md) | GitHub Actions 통합 | MAIN |

---

## By Namespace

### MAIN - Claude Root

| ID | Title | Status | Priority |
|----|-------|--------|----------|
| [MAIN-0002](./prds/MAIN/MAIN-0002-org-pr-collection.md) | Org PR Collection | Draft | P1 |
| [MAIN-0009](./prds/MAIN/MAIN-0009-prompt-learning.md) | Prompt Learning | Draft | P1 |
| [MAIN-0024](./prds/MAIN/MAIN-0024-agent-causality-analysis.md) | 에이전트 인과관계 분석 및 정리 | Draft | P1 |
| [MAIN-0025](./prds/MAIN/MAIN-0025-master-workflow-optimization.md) | 전역 워크플로우 최적화 (Master) | Draft | P0 |
| [MAIN-0026](./prds/MAIN/MAIN-0026-token-management.md) | 토큰 관리 계획 | Draft | P1 |
| [MAIN-0027](./prds/MAIN/MAIN-0027-skills-migration.md) | Skills 마이그레이션 | Draft | P1 |
| [MAIN-0028](./prds/MAIN/MAIN-0028-tdd-enhancement.md) | TDD 워크플로우 강화 | Draft | P1 |
| [MAIN-0029](./prds/MAIN/MAIN-0029-github-actions.md) | GitHub Actions 통합 | Draft | P2 |
| [MAIN-0030](./prds/MAIN/MAIN-0030-documentation-sync.md) | 전역 지침 및 워크플로우 문서 동기화 | Draft | P1 |
| [MAIN-0031](./prds/MAIN/MAIN-0031-document-unification.md) | 문서 통합 관리 시스템 | Completed | P0 |

### HUB - Automation Hub

| ID | Title | Status | Priority |
|----|-------|--------|----------|
| [HUB-0001](./prds/HUB/HUB-0001-automation-hub-v2.md) | WSOP Automation Hub v2.0 | Draft | P0 |
| [HUB-0002](./prds/HUB/HUB-0002-conflict-monitoring.md) | 충돌/중복 모니터링 시스템 | Draft | P1 |
| [HUB-0003](./prds/HUB/HUB-0003-model-unification.md) | 프로젝트 간 모델 통합 | Draft | P0 |
| [HUB-0004](./prds/HUB/HUB-0004-frontend-dashboard.md) | 프론트엔드 대시보드 | Draft | P1 |
| [HUB-0005](./prds/HUB/HUB-0005-production-workflow.md) | GG Production 자막 워크플로우 | Draft | P0 |
| [HUB-0006](./prds/HUB/HUB-0006-mvp-schedule-management.md) | MVP 일정 관리 시스템 | Draft | P0 |

### FT - Feature Table

| ID | Title | Status | Priority |
|----|-------|--------|----------|
| [FT-0001](./prds/FT/FT-0001-poker-hand-auto-capture.md) | 포커 핸드 자동 캡처 및 분류 시스템 | Draft | P0 |
| [FT-0002](./prds/FT/FT-0002-primary-gfx-rfid.md) | Primary Layer - GFX RFID | Draft | P0 |
| [FT-0003](./prds/FT/FT-0003-secondary-gemini-live.md) | Secondary Layer - Gemini Live API | Draft | P1 |
| [FT-0004](./prds/FT/FT-0004-fusion-engine.md) | Fusion Engine | Draft | P1 |
| [FT-0005](./prds/FT/FT-0005-integrated-db-subtitle-system.md) | 통합 데이터베이스 및 자막 데이터 시스템 | Draft | P0 |
| [FT-0007](./prds/FT/FT-0007-custom-rfid-client.md) | 자체 RFID 클라이언트 개발 | Draft | P1 |
| [FT-0008](./prds/FT/FT-0008-monitoring-dashboard.md) | 모니터링 대시보드 구현 | Draft | P1 |
| [FT-0009](./prds/FT/FT-0009-gfx-json-simulator.md) | GFX JSON Simulator (NAS Test) | Draft | P2 |
| [FT-0010](./prds/FT/FT-0010-nas-smb-integration.md) | NAS SMB 연동 | Draft | P1 |
| [FT-0011](./prds/FT/FT-0011-gfx-direct-supabase-sync.md) | GFX PC → Supabase 직접 동기화 | Draft | P0 |

### SUB - Subtitle System

| ID | Title | Status | Priority |
|----|-------|--------|----------|
| [SUB-0001](./prds/SUB/SUB-0001-wsop-broadcast-graphics.md) | WSOP Broadcast Graphics System | Draft | P0 |
| [SUB-0002](./prds/SUB/SUB-0002-workflow-automation.md) | Workflow Automation System | Draft | P1 |
| [SUB-0003](./prds/SUB/SUB-0003-caption-workflow.md) | Caption Generation Workflow System | Draft | P0 |
| [SUB-0005](./prds/SUB/SUB-0005-trigger-db-visualization.md) | Trigger Event & DB Table Visualization | Draft | P1 |
| [SUB-0006](./prds/SUB/SUB-0006-aep-data-elements.md) | AEP Data Elements | Draft | P1 |
| [SUB-0007](./prds/SUB/SUB-0007-4schema-database-design.md) | 4-Schema Database Design | Draft | P0 |

### AE - After Effects

| ID | Title | Status | Priority |
|----|-------|--------|----------|
| [AE-0001](./prds/AE/AE-0001-ae-automation.md) | After Effects 자동화 시스템 | Draft | P0 |
| [AE-0002](./prds/AE/AE-0002-pokergfx-db-schema.md) | PokerGFX DB Schema | Draft | P1 |
| [AE-0003a](./prds/AE/AE-0003a-ae-mode-switcher.md) | AE 모드 전환 시스템 | Draft | P1 |
| [AE-0003b](./prds/AE/AE-0003b-ae-mapping-schema.md) | AE 템플릿 매핑 요소 DB 스키마 설계 | Draft | P1 |
| [AE-0004](./prds/AE/AE-0004-sheets-sync.md) | Google Sheets 양방향 동기화 및 기획 대시보드 | Draft | P1 |
| [AE-0005](./prds/AE/AE-0005-cyprus-db-schema.md) | CyprusDesign DB Schema | Draft | P1 |

---

## Data Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    WSOP 방송 자동화 통합 파이프라인                         │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  [RFID JSON]              [WSOP+ CSV]          [수작업 입력]              │
│      │                         │                    │                    │
│      ▼                         ▼                    ▼                    │
│  automation_feature_table  automation_sub      UI/API                   │
│  (FT-0001~0011)            (SUB-0001~0007)    (수동 입력)                │
│      │                         │                    │                    │
│      └─────────────────┬───────┴────────────────────┘                   │
│                        │                                                 │
│                        ▼                                                 │
│              automation_hub                                             │
│         (PostgreSQL/Supabase)                                           │
│         (HUB-0001~0006)                                                 │
│                        │                                                 │
│                        ▼                                                 │
│              automation_ae                                              │
│         (After Effects 렌더링)                                           │
│         (AE-0001~0005)                                                  │
│                        │                                                 │
│                        ▼                                                 │
│              [렌더링 결과물]                                              │
│              (NAS 저장)                                                  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Specs (기술 명세서)

### SUB - Subtitle System

| ID | Title |
|----|-------|
| [SUB-0001-spec](./specs/SUB/SUB-0001-spec-design-appendix.md) | Design Appendix |
| [SUB-0003-spec](./specs/SUB/SUB-0003-spec-caption-database.md) | Caption Database Spec |
| [SUB-0006-spec](./specs/SUB/SUB-0006-spec-aep-details.md) | AEP Details Spec |
| [SUB-0007-spec](./specs/SUB/SUB-0007-spec-database-implementation.md) | Database Implementation Spec |

---

## Tasks (작업 문서)

### MAIN

| ID | Title |
|----|-------|
| [MAIN-0009-tasks](./tasks/MAIN/MAIN-0009-tasks-prompt-learning.md) | Prompt Learning Tasks |
| [MAIN-0026-tasks](./tasks/MAIN/MAIN-0026-tasks.md) | Token Management Tasks |
| [MAIN-0027-tasks](./tasks/MAIN/MAIN-0027-tasks.md) | Skills Migration Tasks |

### AE

| ID | Title |
|----|-------|
| [AE-0002-tasks](./tasks/AE/AE-0002-tasks-v2.md) | AE Tasks v2 |

---

## Archive

### HUB

| ID | Title |
|----|-------|
| [HUB-0000](./archive/HUB/HUB-0000-automation-hub-integration.md) | Automation Hub Integration (Archived) |
| [HUB-gemini](./archive/HUB/HUB-gemini.md) | Gemini Notes |

### SUB

| ID | Title |
|----|-------|
| [SUB-0004](./archive/SUB/SUB-0004-caption-database-schema.md) | Caption Database Schema (Archived) |
| [SUB-0004/](./archive/SUB/0004/) | 9개 분할 문서 |

---

## Resources

- [통합 레지스트리](./registry.json) - 모든 PRD 메타데이터
- [마이그레이션 스크립트](../../scripts/migrate-docs.ps1) - 문서 마이그레이션 도구
