# WSOPTV OTT 문서 인덱스

**Version**: 1.0.0
**Last Updated**: 2026-01-19

---

## 문서 분류

### PRD (Product Requirements Document)

플랫폼 기능 및 요구사항 정의 문서

| 문서 ID | 제목 | 상태 | 우선순위 |
|---------|------|------|:--------:|
| [PRD-0002](prds/PRD-0002-wsoptv-ott-platform-mvp.md) | WSOPTV OTT Platform MVP | Draft | P2 |
| [PRD-0005](prds/PRD-0005-wsoptv-ott-rfp.md) | WSOPTV OTT RFP | Draft | - |
| [PRD-0006](prds/PRD-0006-advanced-mode.md) | Advanced Mode | Draft | P0 |

### ADR (Architecture Decision Record)

아키텍처 결정 근거 문서

| 문서 ID | 제목 | 상태 | 영향도 |
|---------|------|------|:------:|
| [ADR-0001](adrs/ADR-0001-multiview-3layer-rationale.md) | 3계층 Multi-View 설계 논리 | Draft | High |

### Strategy

전략 및 비즈니스 문서

| 문서 ID | 제목 | 상태 | 우선순위 |
|---------|------|------|:--------:|
| [STRAT-0003](strategies/STRAT-0003-cross-promotion.md) | 상호 보완 프로모션 전략 | Proposal | P1 |
| [STRAT-0007](strategies/STRAT-0007-content-sourcing.md) | Content Sourcing & Distribution | Draft | P0 |

### Report

분석 및 리포트 문서

| 문서 ID | 제목 | 날짜 |
|---------|------|------|
| [REPORT-2026-01-19](reports/REPORT-2026-01-19-document-consistency.md) | Document Consistency Report | 2026-01-19 |

---

## 문서 의존성 관계

```
PRD-0002 (MVP - 중심 문서)
│
├── PRD-0006 (Advanced Mode)
│   └── ADR-0001 (3계층 Multi-View 근거)
│
├── PRD-0005 (RFP)
│
├── STRAT-0003 (Cross-Promotion)
│
└── STRAT-0007 (Content Strategy)
```

---

## 폴더 구조

```
docs/
├── README.md                    # 이 문서 (인덱스)
├── prds/                        # PRD 문서
│   ├── PRD-0002-wsoptv-ott-platform-mvp.md
│   ├── PRD-0005-wsoptv-ott-rfp.md
│   └── PRD-0006-advanced-mode.md
├── adrs/                        # ADR 문서
│   └── ADR-0001-multiview-3layer-rationale.md
├── strategies/                  # 전략 문서
│   ├── STRAT-0003-cross-promotion.md
│   └── STRAT-0007-content-sourcing.md
├── reports/                     # 리포트
│   └── REPORT-2026-01-19-document-consistency.md
├── images/                      # 스크린샷/다이어그램
│   ├── PRD-0002/
│   ├── PRD-0006/
│   ├── ADR-0001/
│   └── STRAT-0003/
└── mockups/                     # HTML 목업
    ├── PRD-0002/
    ├── PRD-0006/
    ├── ADR-0001/
    └── STRAT-0003/
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

*Last Updated: 2026-01-19*
