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
| [REPORT-2026-01-19-nbatv](reports/REPORT-2026-01-19-nbatv-reference-analysis.md) | **NBA TV 레퍼런스 분석** | 2026-01-19 |
| [REPORT-2026-01-19](reports/REPORT-2026-01-19-document-consistency.md) | Document Consistency Report | 2026-01-19 |

---

## 문서 의존성 관계

```
PRD-0002 (MVP - 중심 문서)
│
├── PRD-0006 (Advanced Mode)
│   ├── ADR-0001 (3계층 Multi-View 근거)
│   └── REPORT-2026-01-19-nbatv (NBA TV 1:1 매핑 소스) ★ NEW
│
├── PRD-0005 (RFP)
│
├── STRAT-0003 (Cross-Promotion)
│
└── STRAT-0007 (Content Strategy)
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

*Last Updated: 2026-01-19 (NBA TV 레퍼런스 추가)*
