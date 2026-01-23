# WSOPTV OTT 문서 인덱스

**Version**: 4.1.0
**Last Updated**: 2026-01-20
**Major Update**: PRD-0010 NBA TV UX 솔루션 추가

---

## 문서 계층 구조

```
                    ┌─────────────────────────────┐
                    │         Vible (원천)         │
                    │  michael_note + tony_note   │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │    STRAT-0001 ★ (Vision)    │
                    │   시청자 경험 비전            │
                    └──────────────┬──────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  PRD-0002 ★     │     │  PRD-0006 ★     │     │  STRAT-0007     │
│  Platform MVP   │◀────│  Advanced Mode  │     │  Content        │
└─────────────────┘     └─────────────────┘     └─────────────────┘

★ = Tier 1 핵심 문서 (반드시 최신 유지)
```

---

## Tier 1: 핵심 문서 (4개)

반드시 최신 상태로 유지해야 하는 문서

| 문서 | 역할 | 상태 |
|------|------|:----:|
| [STRAT-0001](strategies/STRAT-0001-viewer-experience-vision.md) | **Vision** - 시청자 경험 비전 | Active |
| [PRD-0002](prds/PRD-0002-wsoptv-ott-platform-mvp.md) | **Platform** - MVP 플랫폼 스펙 | Active |
| [PRD-0006](prds/PRD-0006-advanced-mode.md) | **Feature** - Advanced Mode | Active |
| [STRAT-0007](strategies/STRAT-0007-content-sourcing.md) | **Content** - 콘텐츠 소싱 | Active |

### YouTube 대비 핵심 차별점 (STRAT-0001)

| # | 차별점 | YouTube | WSOPTV |
|:-:|--------|---------|--------|
| 1 | **Timeshift** | 불가 | 라이브 중 되감기 |
| 2 | **아카이브** | 비공개 | 영구 보존 |
| 3 | **Advanced Mode** | 없음 | Multi-view + StatsView |
| 4 | **검색** (Phase 2) | 없음 | 핸드/선수 검색 |

---

## Tier 2: 보조 문서 (5개)

필요 시 참조하는 문서

| 문서 | 역할 | 상태 |
|------|------|:----:|
| [PRD-0009](prds/PRD-0009-hand-tagging-search.md) | Hand Tagging (Phase 2) | Draft |
| [PRD-0010](prds/PRD-0010-nbatv-ux-solutions.md) | NBA TV UX 솔루션 적용 | Draft |
| [ADR-0001](adrs/ADR-0001-multiview-3layer-rationale.md) | Multi-view 설계 근거 | Draft |
| [ADR-0002](adrs/ADR-0002-database-schema-design.md) | DB 스키마 설계 | Proposed |
| [STRAT-0003](strategies/STRAT-0003-cross-promotion.md) | 프로모션 전략 | Proposal |

---

## Tier 3: 참조 문서 (3개)

읽기 전용 원천 자료

| 문서 | 역할 |
|------|------|
| [michael_note.md](vible/michael_note.md) | Michael 아이디어 원본 (Vible) |
| [tony_note.md](vible/tony_note.md) | Tony 아이디어 원본 (Moses Commentary) |
| [NBA TV 분석](reports/REPORT-2026-01-19-nbatv-reference-analysis.md) | UX 참조 |

---

## 문서 관리 원칙

1. **단일 진실 소스**: STRAT-0001이 시청자 관점의 유일한 진실
2. **계층 준수**: Tier 1 → Tier 2 → Tier 3 순서로 참조
3. **통합 우선**: 신규 문서보다 기존 문서 통합 선호
4. **아카이브 활용**: 불필요한 문서는 즉시 archive/로 이동

---

## 아카이브 (7개)

초기 기획 단계에서 과도하게 상세화된 문서들

| 문서 | 사유 |
|------|------|
| STRAT-0008~0011 | 타임라인/KPI/법규/API 미확정 |
| ADR-0003 | 기술 스택 미확정 |
| PRD-0008 | UX 방향 미확정 |
| REPORT-strategy | 전략 재검토 필요 |

**위치**: [archive/](archive/)

---

## 폴더 구조

```
docs/
├── README.md                    # 이 문서
├── vible/                       # 원천 자료
│   ├── michael_note.md
│   └── tony_note.md
├── strategies/                  # 전략 문서
│   ├── STRAT-0001-viewer-experience-vision.md  ★
│   ├── STRAT-0003-cross-promotion.md
│   └── STRAT-0007-content-sourcing.md
├── prds/                        # PRD
│   ├── PRD-0002-wsoptv-ott-platform-mvp.md     ★
│   ├── PRD-0005-wsoptv-ott-rfp.md
│   ├── PRD-0006-advanced-mode.md               ★
│   ├── PRD-0009-hand-tagging-search.md
│   └── PRD-0010-nbatv-ux-solutions.md
├── adrs/                        # ADR
│   ├── ADR-0001-multiview-3layer-rationale.md
│   └── ADR-0002-database-schema-design.md
├── reports/                     # 리포트
├── archive/                     # 아카이브
├── images/                      # 이미지
└── mockups/                     # HTML 목업
```

---

## 명명 규칙

| 유형 | 접두사 | 예시 |
|------|--------|------|
| PRD | `PRD-NNNN` | PRD-0002-wsoptv-ott-platform-mvp.md |
| ADR | `ADR-NNNN` | ADR-0001-multiview-3layer-rationale.md |
| Strategy | `STRAT-NNNN` | STRAT-0001-viewer-experience-vision.md |
| Report | `REPORT-YYYY-MM-DD` | REPORT-2026-01-19-nbatv-reference-analysis.md |

---

*Last Updated: 2026-01-20 (PRD-0010 추가)*
