# REPORT-2026-01-19: WSOPTV OTT 전략 재점검 결과

| 항목 | 값 |
|------|---|
| **Type** | Strategy Review Report |
| **Date** | 2026-01-19 |
| **Author** | Claude Code |
| **Status** | Final |

---

## Executive Summary

WSOPTV OTT 플랫폼의 **전체 전략 문서 7개를 전면 재점검**하고, 발견된 **7가지 주요 갭(Gap)**을 해소하기 위한 **신규 문서 7개**를 작성했습니다. 본 리포트는 재점검 결과와 개선 사항을 종합합니다.

### 재점검 범위

| 영역 | 기존 문서 | 신규 문서 |
|------|:--------:|:--------:|
| PRD | 3개 | 1개 |
| ADR | 2개 | 1개 |
| Strategy | 2개 | 4개 |
| Report | 2개 | 1개 (본 문서) |
| **Total** | **9개** | **7개** |

### 런칭 전략 결정

| 항목 | 결정 |
|------|------|
| **런칭 목표** | Post-Season (2026-08-01) |
| **근거** | WSOP 시즌 콘텐츠 확보 후 안정적 런칭 |

---

## 1. Gap Analysis Summary

### 1.1 발견된 문제점 (7가지)

| # | 영역 | 문제 | 심각도 | 해결 문서 |
|:-:|------|------|:------:|----------|
| 1 | **타임라인** | Phase별 절대 일정 부재 | Critical | STRAT-0008 |
| 2 | **KPI** | 비즈니스 지표 없음 | Critical | STRAT-0009 |
| 3 | **법규** | 칩 자동 생성 규제 미검토 | Critical | STRAT-0010 |
| 4 | **협업** | GGPass/GGPoker API 스펙 미정 | Critical | STRAT-0011 |
| 5 | **기술** | 기술 스택 미확정 | High | ADR-0003 |
| 6 | **UX** | TV Advanced Mode 미지원 보완 없음 | Medium | PRD-0008 |
| 7 | **통합** | 전체 전략 정합성 리뷰 없음 | Medium | 본 리포트 |

### 1.2 기존 강점 (유지 사항)

| # | 강점 | 문서 | 평가 |
|:-:|------|------|------|
| 1 | 명확한 차별화 (Timeshift + Multi-view) | PRD-0002 | ✓ 유지 |
| 2 | NBA TV 1:1 매핑 UX | PRD-0006 | ✓ 유지 |
| 3 | 완성도 높은 DB 스키마 | ADR-0002 | ✓ 유지 |
| 4 | 양방향 프로모션 전략 | STRAT-0003 | ✓ 유지 (법규 연계 추가) |
| 5 | 콘텐츠 소싱 체계화 | STRAT-0007 | ✓ 유지 |

---

## 2. Key Decisions Made

### 2.1 런칭 전략

| 옵션 | 선택 | 근거 |
|------|:----:|------|
| In-Season 런칭 (2026-05) | ✗ | 준비 기간 부족, 리스크 |
| **Post-Season 런칭 (2026-08-01)** | **✓** | 콘텐츠 확보, QA 충분 |
| Delayed 런칭 (2027) | ✗ | 시장 기회 손실 |

### 2.2 칩 자동 생성 정책

| 국가 유형 | 정책 |
|---------|------|
| 완전 합법 (영국, 미국 일부 주) | 칩 자동 생성 유지 |
| 조건부 합법 (독일) | 선택적 활성화 |
| 금지 (호주, 한국, 일본) | 비활성화 또는 크레딧 대안 |

### 2.3 TV Advanced Mode 대안

| Phase | 구현 |
|-------|------|
| Phase 1 | 2분할 간소화 + Pre-rendered HUD |
| Phase 2 | Second Screen Companion |
| Phase 3 | Voice Control |

### 2.4 기술 스택 권장안

| 레이어 | 선택 |
|--------|------|
| Frontend (Web) | Next.js 14 + React 18 |
| Frontend (Mobile) | SwiftUI / Kotlin + Compose |
| Backend | Node.js + Fastify |
| Database | PostgreSQL (Supabase) |
| CDN | Akamai (Primary) |
| DRM | Widevine + FairPlay + PlayReady |

---

## 3. Document Updates Summary

### 3.1 신규 작성 문서 (7개)

| 문서 ID | 제목 | 용량 | 핵심 내용 |
|---------|------|:----:|----------|
| **STRAT-0008** | 타임라인 로드맵 | ~250줄 | Phase별 절대 일정, 마일스톤 |
| **STRAT-0009** | 비즈니스 KPI | ~250줄 | MAU, ARR, 전환율 목표 |
| **STRAT-0010** | 법규 준수 | ~350줄 | 20개국 규제, 칩 자동 생성 대안 |
| **STRAT-0011** | GGPass 통합 스펙 | ~400줄 | OAuth 2.0, Billing, HUD API |
| **ADR-0003** | 기술 아키텍처 | ~450줄 | 기술 스택, 인프라, 비용 |
| **PRD-0008** | TV UX 대안 | ~300줄 | 4가지 대안, Phase별 권장 |
| **REPORT** | 전략 리뷰 결과 | ~300줄 | 본 문서 |

### 3.2 업데이트 필요 문서 (4개)

| 문서 | 업데이트 내용 | 상태 |
|------|-------------|:----:|
| PRD-0002 | References에 신규 문서 추가 | Pending |
| PRD-0006 | TV 대안 섹션에 PRD-0008 링크 | Pending |
| STRAT-0003 | 법규 준수 참조 (STRAT-0010) | Pending |
| docs/README.md | 신규 7개 문서 인덱스 | Pending |

---

## 4. Action Items

### 4.1 즉시 조치 필요 (Before 2026-02-28)

| # | 항목 | 담당 | 의존성 |
|:-:|------|------|--------|
| 1 | GGPass 팀과 API 스펙 협의 | 기술팀 | STRAT-0011 |
| 2 | 미국 주별 법적 검토 의뢰 | 법무팀 | STRAT-0010 |
| 3 | 협업사 RFP 응답 평가 | PM | PRD-0005 |
| 4 | 기술 스택 최종 확정 | 기술팀 | ADR-0003 |

### 4.2 30일 내 조치 (Before 2026-02-19)

| # | 항목 | 담당 |
|:-:|------|------|
| 1 | KPI 목표 경영진 승인 | PM + 경영진 |
| 2 | 칩 자동 생성 국가별 정책 확정 | PM + 법무 |
| 3 | TV UX 대안 사용성 테스트 | UX팀 |
| 4 | CDN/DRM 벤더 선정 | 인프라팀 |

### 4.3 런칭 전 완료 (Before 2026-08-01)

| # | 항목 | 목표일 |
|:-:|------|--------|
| 1 | MVP 개발 완료 | 2026-06-30 |
| 2 | 베타 테스트 | 2026-07-01 ~ 07-31 |
| 3 | 국가별 이용약관 | 2026-06-30 |
| 4 | 마케팅 캠페인 준비 | 2026-07-15 |

---

## 5. Risk Matrix Update

### 5.1 신규 식별 리스크

| 리스크 | 확률 | 영향 | 완화 전략 | 담당 |
|--------|:----:|:----:|----------|------|
| 미국 주 규제 위반 | 중 | Critical | 보수적 접근, 법률 자문 | 법무 |
| GGPass API 변경 | 중 | 높음 | 버전 관리, Mock 유지 | 기술 |
| 칩 자동 생성 금지 확대 | 중 | 높음 | 대안 B/C 준비 | PM |
| TV 앱 Plus+ 불만 | 높음 | 중 | PRD-0008 대안 구현 | UX |
| 협업사 일정 지연 | 높음 | 중 | 2주 버퍼, 병렬 작업 | PM |

### 5.2 리스크 등급 변화

| 리스크 | 이전 | 현재 | 변화 이유 |
|--------|:----:|:----:|---------|
| 법규 리스크 | 미평가 | **High** | STRAT-0010 분석 결과 |
| 기술 리스크 | High | **Medium** | ADR-0003 스택 명확화 |
| 타임라인 리스크 | High | **Medium** | STRAT-0008 일정 수립 |

---

## 6. Document Hierarchy (Updated)

### 6.1 문서 의존성 맵

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
│   PRD-0006      │     │   PRD-0005      │     │   PRD-0008      │
│ Advanced Mode   │     │     RFP         │     │  TV UX Alt ★    │
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

★ = 신규 작성
```

### 6.2 업데이트된 폴더 구조

```
docs/
├── README.md                           # 인덱스 (업데이트 필요)
├── prds/
│   ├── PRD-0002-wsoptv-ott-platform-mvp.md
│   ├── PRD-0005-wsoptv-ott-rfp.md
│   ├── PRD-0006-advanced-mode.md
│   └── PRD-0008-tv-app-ux-alternative.md      ★ NEW
├── adrs/
│   ├── ADR-0001-multiview-3layer-rationale.md
│   ├── ADR-0002-database-schema-design.md
│   └── ADR-0003-technical-architecture.md     ★ NEW
├── strategies/
│   ├── STRAT-0003-cross-promotion.md
│   ├── STRAT-0007-content-sourcing.md
│   ├── STRAT-0008-timeline-roadmap.md         ★ NEW (Critical)
│   ├── STRAT-0009-business-kpi.md             ★ NEW (Critical)
│   ├── STRAT-0010-legal-compliance.md         ★ NEW (Critical)
│   └── STRAT-0011-ggpass-integration-spec.md  ★ NEW (Critical)
├── reports/
│   ├── REPORT-2026-01-19-nbatv-reference-analysis.md
│   ├── REPORT-2026-01-19-document-consistency.md
│   └── REPORT-2026-01-19-strategy-review.md   ★ NEW (본 문서)
├── images/
└── mockups/
```

---

## 7. Next Steps

### 7.1 즉시 (이번 세션)

- [x] 신규 문서 7개 작성 완료
- [ ] 기존 문서 4개 업데이트
  - [ ] PRD-0002 References 추가
  - [ ] PRD-0006 TV 대안 링크
  - [ ] STRAT-0003 법규 참조
  - [ ] docs/README.md 인덱스

### 7.2 팔로업 (향후)

| 기간 | 항목 |
|------|------|
| 1주 | GGPass 팀 미팅 일정 조율 |
| 2주 | 법률 자문 의뢰서 발송 |
| 4주 | KPI 목표 경영진 리뷰 |
| 6주 | 협업사 RFP 최종 선정 |

---

## 8. Conclusion

본 전략 재점검을 통해 WSOPTV OTT 플랫폼의 **7가지 주요 갭을 식별**하고, **7개 신규 문서**로 해결했습니다.

### 핵심 성과

1. **명확한 타임라인**: Post-Season 런칭 (2026-08-01) 확정
2. **측정 가능한 KPI**: MAU 50K (Y1) → 300K (Y3) 목표 설정
3. **법규 리스크 대응**: 20개국 규제 분석 및 칩 자동 생성 대안 수립
4. **기술 방향성**: 기술 스택 권장안 및 비용 추정 완료
5. **TV UX 보완**: Plus+ 가치 제공 4가지 대안 제시

### 남은 과제

- GGPass/GGPoker 팀과의 API 스펙 확정
- 미국 주별 법적 검토 완료
- 협업사 최종 선정 및 계약

---

*Report Generated: 2026-01-19*
*Author: Claude Code*
