# WSOPTV OTT 문서 인덱스

**Version**: 2.0.0
**Last Updated**: 2026-01-19
**Major Update**: 전략 재점검 7개 문서 추가

---

## 문서 분류

### PRD (Product Requirements Document)

플랫폼 기능 및 요구사항 정의 문서

| 문서 ID | 제목 | 상태 | 우선순위 |
|---------|------|------|:--------:|
| [PRD-0002](prds/PRD-0002-wsoptv-ott-platform-mvp.md) | WSOPTV OTT Platform MVP | Draft | P2 |
| [PRD-0005](prds/PRD-0005-wsoptv-ott-rfp.md) | WSOPTV OTT RFP | Draft | - |
| [PRD-0006](prds/PRD-0006-advanced-mode.md) | Advanced Mode | Draft | P0 |
| [PRD-0008](prds/PRD-0008-tv-app-ux-alternative.md) | **TV 앱 UX 대안** ★ | Draft | P1 |

### ADR (Architecture Decision Record)

아키텍처 결정 근거 문서

| 문서 ID | 제목 | 상태 | 영향도 |
|---------|------|------|:------:|
| [ADR-0001](adrs/ADR-0001-multiview-3layer-rationale.md) | 3계층 Multi-View 설계 논리 | Draft | High |
| [ADR-0002](adrs/ADR-0002-database-schema-design.md) | DB 스키마 설계 | Proposed | High |
| [ADR-0003](adrs/ADR-0003-technical-architecture.md) | **기술 아키텍처** ★ | Proposed | Critical |

### Strategy

전략 및 비즈니스 문서

| 문서 ID | 제목 | 상태 | 우선순위 |
|---------|------|------|:--------:|
| [STRAT-0003](strategies/STRAT-0003-cross-promotion.md) | 상호 보완 프로모션 전략 | Proposal | P1 |
| [STRAT-0007](strategies/STRAT-0007-content-sourcing.md) | Content Sourcing & Distribution | Draft | P0 |
| [STRAT-0008](strategies/STRAT-0008-timeline-roadmap.md) | **타임라인 로드맵** ★ | Approved | Critical |
| [STRAT-0009](strategies/STRAT-0009-business-kpi.md) | **비즈니스 KPI** ★ | Approved | Critical |
| [STRAT-0010](strategies/STRAT-0010-legal-compliance.md) | **법규 준수** ★ | Approved | Critical |
| [STRAT-0011](strategies/STRAT-0011-ggpass-integration-spec.md) | **GGPass 통합 스펙** ★ | Approved | Critical |

### Report

분석 및 리포트 문서

| 문서 ID | 제목 | 날짜 |
|---------|------|------|
| [REPORT-2026-01-19-nbatv](reports/REPORT-2026-01-19-nbatv-reference-analysis.md) | NBA TV 레퍼런스 분석 | 2026-01-19 |
| [REPORT-2026-01-19](reports/REPORT-2026-01-19-document-consistency.md) | Document Consistency Report | 2026-01-19 |
| [REPORT-2026-01-19-strategy](reports/REPORT-2026-01-19-strategy-review.md) | **전략 재점검 결과** ★ | 2026-01-19 |

---

## 문서 의존성 관계

```
                        ┌─────────────────┐
                        │   PRD-0002      │ ◀── 중심 문서
                        │   MVP Platform  │
                        └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PRD-0006      │     │   PRD-0005      │     │   PRD-0008 ★    │
│ Advanced Mode   │     │     RFP         │     │  TV UX Alt      │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│   ADR-0001      │
│ 3계층 Multi-view│
└─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   ADR-0002      │     │   ADR-0003 ★    │     │  STRAT-0003     │
│  DB Schema      │     │ Tech Arch       │     │ Cross-Promotion │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ STRAT-0007      │     │ STRAT-0008 ★    │     │ STRAT-0010 ★    │
│Content Sourcing │     │ Timeline        │     │ Legal           │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│ STRAT-0009 ★    │     │ STRAT-0011 ★    │
│ Business KPI    │     │ GGPass API      │
└─────────────────┘     └─────────────────┘

★ = 신규 작성 (전략 재점검)
```

### NBA TV 레퍼런스 (UX 설계 기준)

PRD-0006 Advanced Mode는 **NBA TV/League Pass의 검증된 UX를 1:1 매핑**하여 설계되었습니다.

| NBA TV 요소 | WSOPTV 대응 |
|------------|-------------|
| Score Strip | Tournament Strip |
| Multiview (4분할) | 4분할 Multiview |
| Key Plays | Key Hands |
| Play-by-Play | Hand-by-Hand Log |
| Box Score | Player Stats |
| Shot Charts | Position Analysis |

**상세 매핑**: [NBA TV 분석 리포트](reports/REPORT-2026-01-19-nbatv-reference-analysis.md)

---

## 폴더 구조

```
docs/
├── README.md                           # 이 문서 (인덱스)
├── prds/                               # PRD 문서
│   ├── PRD-0002-wsoptv-ott-platform-mvp.md
│   ├── PRD-0005-wsoptv-ott-rfp.md
│   ├── PRD-0006-advanced-mode.md
│   └── PRD-0008-tv-app-ux-alternative.md      ★ NEW
├── adrs/                               # ADR 문서
│   ├── ADR-0001-multiview-3layer-rationale.md
│   ├── ADR-0002-database-schema-design.md
│   └── ADR-0003-technical-architecture.md     ★ NEW
├── strategies/                         # 전략 문서
│   ├── STRAT-0003-cross-promotion.md
│   ├── STRAT-0007-content-sourcing.md
│   ├── STRAT-0008-timeline-roadmap.md         ★ NEW (Critical)
│   ├── STRAT-0009-business-kpi.md             ★ NEW (Critical)
│   ├── STRAT-0010-legal-compliance.md         ★ NEW (Critical)
│   └── STRAT-0011-ggpass-integration-spec.md  ★ NEW (Critical)
├── reports/                            # 리포트
│   ├── REPORT-2026-01-19-nbatv-reference-analysis.md
│   ├── REPORT-2026-01-19-document-consistency.md
│   └── REPORT-2026-01-19-strategy-review.md   ★ NEW (본 리뷰 결과)
├── images/                             # 스크린샷/다이어그램
└── mockups/                            # HTML 목업
```

---

## 명명 규칙

| 유형 | 접두사 | 예시 |
|------|--------|------|
| PRD | `PRD-NNNN` | PRD-0002-wsoptv-ott-platform-mvp.md |
| ADR | `ADR-NNNN` | ADR-0001-multiview-3layer-rationale.md |
| Strategy | `STRAT-NNNN` | STRAT-0003-cross-promotion.md |
| Report | `REPORT-YYYY-MM-DD` | REPORT-2026-01-19-document-consistency.md |

---

## 시각 자료

### PRD-0006 NBA 스타일 목업 (NEW)

| 목업 | 설명 | NBA 참조 |
|------|------|----------|
| [homepage-nba-style.html](mockups/PRD-0006/homepage-nba-style.html) | 홈페이지 레이아웃 | Score Strip, Hero Section |
| [player-controls-nba-style.html](mockups/PRD-0006/player-controls-nba-style.html) | 플레이어 컨트롤바 | Streams/MultiView/Key Plays |
| [streaming-options-modal.html](mockups/PRD-0006/streaming-options-modal.html) | 스트리밍 옵션 모달 | Broadcasts/Languages |
| [key-hands-modal.html](mockups/PRD-0006/key-hands-modal.html) | Key Hands 모달 | Key Plays |
| [hand-info-panel.html](mockups/PRD-0006/hand-info-panel.html) | Hand Info 패널 | Game Info |
| [player-stats-table.html](mockups/PRD-0006/player-stats-table.html) | 선수 통계 테이블 | Box Score |
| [hand-by-hand-log.html](mockups/PRD-0006/hand-by-hand-log.html) | 액션 로그 | Play-by-Play |
| [position-analysis.html](mockups/PRD-0006/position-analysis.html) | 포지션 분석 | Shot Charts |

### 이미지 참조 규칙

문서에서 이미지 참조 시:
```markdown
![이미지 설명](../images/PRD-0002/image-name.png)
```

### HTML 목업 참조 규칙

```markdown
[HTML 원본](../mockups/PRD-0002/mockup-name.html)
```

---

## 상태 정의

| 상태 | 설명 |
|------|------|
| Draft | 초안 작성 중 |
| Proposal | 제안됨, 검토 대기 |
| Approved | 승인됨 |
| Deprecated | 더 이상 사용하지 않음 |

---

---

## 전략 재점검 신규 문서 요약 (★)

2026-01-19 전략 재점검 결과 7개 문서가 신규 추가되었습니다.

| 구분 | 문서 | 핵심 내용 |
|------|------|----------|
| **타임라인** | STRAT-0008 | Phase별 절대 일정, 런칭 목표: 2026-08-01 |
| **KPI** | STRAT-0009 | MAU 50K(Y1)→300K(Y3), 전환율 목표 |
| **법규** | STRAT-0010 | 20개국 규제, 칩 자동 생성 대안 |
| **API** | STRAT-0011 | GGPass OAuth, Billing, HUD API 스펙 |
| **기술** | ADR-0003 | 기술 스택, 비용 추정 |
| **TV UX** | PRD-0008 | Advanced Mode 대안 4가지 |
| **리포트** | REPORT-strategy | 전체 재점검 결과 |

**상세 리포트**: [REPORT-2026-01-19-strategy-review](reports/REPORT-2026-01-19-strategy-review.md)

---

*Last Updated: 2026-01-19 (전략 재점검 7개 문서 추가)*
