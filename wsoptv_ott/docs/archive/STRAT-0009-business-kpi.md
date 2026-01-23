# STRAT-0009: WSOPTV OTT 비즈니스 KPI

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Priority** | Critical |
| **Created** | 2026-01-19 |
| **Author** | Claude Code |
| **References** | PRD-0002, STRAT-0003 |

---

## Executive Summary

WSOPTV OTT 플랫폼의 **측정 가능한 비즈니스 목표**를 정의합니다. North Star Metric으로 **MAU(Monthly Active Users)**를 설정하고, 구독자 성장, 전환율, GG POKER 연계 KPI를 체계화합니다.

### KPI 프레임워크

```
                    ┌─────────────────┐
                    │  North Star     │
                    │     MAU         │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐        ┌────▼────┐        ┌────▼────┐
    │ 구독자   │        │ 참여도   │        │ 수익    │
    │ 성장     │        │ 지표     │        │ 지표    │
    └─────────┘        └─────────┘        └─────────┘
```

---

## 1. North Star Metric: MAU

### 정의

**MAU (Monthly Active Users)**: 월간 1회 이상 WSOPTV에 로그인하여 콘텐츠를 시청한 고유 사용자 수

### 목표

| 기간 | 목표 | 근거 |
|------|:----:|------|
| 런칭 후 3개월 (Y1 Q1) | 20,000 | 초기 GGPass 연동 유입 |
| Y1 (2026-08 ~ 2027-07) | 50,000 | 첫 번째 WSOP 시즌 효과 |
| Y2 (2027-08 ~ 2028-07) | 150,000 | 콘텐츠 축적 + 마케팅 |
| Y3 (2028-08 ~ 2029-07) | 300,000 | 글로벌 확장 |

### 벤치마크

| 서비스 | MAU | 비고 |
|--------|----:|------|
| PokerGo | ~100K | WSOP 독점 (과거) |
| ESPN+ | ~25M | 종합 스포츠 |
| DAZN | ~15M | 스포츠 특화 |
| **WSOPTV 목표 (Y3)** | **300K** | 포커 특화 프리미엄 |

---

## 2. Primary KPIs

### 2.1 구독자 성장

#### 총 구독자 수

| 기간 | Plus ($10) | Plus+ ($50) | Total |
|------|:----------:|:-----------:|:-----:|
| Y1 Q1 (3개월) | 8,000 | 2,000 | 10,000 |
| **Y1 (12개월)** | **40,000** | **10,000** | **50,000** |
| **Y2 (24개월)** | **110,000** | **40,000** | **150,000** |
| **Y3 (36개월)** | **210,000** | **90,000** | **300,000** |

#### 신규 가입자 (Monthly)

| 기간 | 월간 신규 목표 | 채널별 비중 |
|------|:-------------:|------------|
| Y1 | 4,000/월 | Organic 30%, GGPass 50%, 광고 20% |
| Y2 | 8,000/월 | Organic 40%, GGPass 40%, 광고 20% |
| Y3 | 12,000/월 | Organic 50%, GGPass 30%, 광고 20% |

### 2.2 Plus → Plus+ 전환율

**목표**: Plus 구독자의 **25%**가 Plus+로 업그레이드

| 기간 | 전환율 목표 | 전략 |
|------|:----------:|------|
| Y1 | 20% | Advanced Mode 가치 증명 |
| Y2 | 25% | StatsView 구조2 런칭 |
| Y3 | 30% | AI 기능 추가 |

#### 전환 유도 터치포인트

| 터치포인트 | 전환율 기여 |
|-----------|:----------:|
| Multi-view 미리보기 | 35% |
| "Upgrade for StatsView" CTA | 25% |
| Key Hands 제한 해제 | 20% |
| 시즌 프로모션 | 20% |

### 2.3 MRR/ARR

**MRR (Monthly Recurring Revenue)**

| 기간 | Plus MRR | Plus+ MRR | Total MRR |
|------|:--------:|:---------:|:---------:|
| Y1 | $400,000 | $500,000 | **$900,000** |
| Y2 | $1,100,000 | $2,000,000 | **$3,100,000** |
| Y3 | $2,100,000 | $4,500,000 | **$6,600,000** |

**ARR (Annual Recurring Revenue)**

| 기간 | ARR |
|------|----:|
| Y1 | $10.8M |
| Y2 | $37.2M |
| Y3 | $79.2M |

### 2.4 이탈률 (Churn Rate)

| 구독 티어 | 월간 이탈률 목표 | 벤치마크 |
|----------|:--------------:|----------|
| Plus | < 8% | OTT 평균 ~10% |
| Plus+ | < 5% | 프리미엄 평균 ~6% |

**이탈 방지 전략**:
1. 시즌 콘텐츠 알림
2. 아카이브 큐레이션
3. GG POKER 칩 연계
4. Plus+ 전용 Early Access

---

## 3. GG POKER 연계 KPI

### 3.1 Flow 1: GG POKER → WSOPTV

**GG POKER 유저의 WSOPTV 전환**

| 지표 | 목표 | 측정 |
|------|:----:|------|
| GG POKER 활성 유저 중 WSOPTV 가입률 | 10% | GGPass SSO 추적 |
| 칩 구매 → Plus 자동 발급 활성화율 | 80% | 프로모션 코드 추적 |
| GG POKER 유입 사용자 리텐션 (Day 30) | 50% | 코호트 분석 |

### 3.2 Flow 2: WSOPTV → GG POKER

**WSOPTV 유저의 GG POKER 전환**

| 지표 | 목표 | 측정 |
|------|:----:|------|
| WSOPTV 구독자 중 GG POKER 신규 가입률 | 30% | GGPass SSO 추적 |
| "Play Now" 버튼 클릭률 | 5% | 이벤트 추적 |
| 칩 자동 생성 후 실제 게임 시작률 | 60% | GG POKER 데이터 |

### 3.3 Cross-Platform LTV

| 세그먼트 | 예상 LTV | 비고 |
|---------|:-------:|------|
| WSOPTV Only | $120 | 12개월 × $10 |
| GG POKER Only | $250 | 업계 평균 |
| **WSOPTV + GG POKER** | **$500+** | 시너지 효과 |

---

## 4. Secondary KPIs

### 4.1 시청 참여도

| 지표 | 목표 | 벤치마크 |
|------|:----:|----------|
| 평균 세션 시청 시간 | 45분 | Netflix 60분 |
| 주간 시청 세션 수 | 3회 | ESPN+ 2.5회 |
| 콘텐츠 완료율 (VOD) | 60% | OTT 평균 50% |

### 4.2 리텐션

| 리텐션 지표 | 목표 |
|-----------|:----:|
| Day 1 | 70% |
| Day 7 | 60% |
| Day 30 | 40% |
| Day 90 | 30% |

### 4.3 Advanced Mode 사용률 (Plus+)

| 기능 | 사용률 목표 | 측정 |
|------|:----------:|------|
| Multi-view 활성화 | 70% | 기능 토글 추적 |
| StatsView 활성화 | 60% | HUD 토글 추적 |
| Key Hands 사용 | 50% | 모달 오픈 추적 |
| Position Analysis | 30% | 페이지 방문 추적 |

### 4.4 콘텐츠 지표

| 지표 | 목표 |
|------|:----:|
| 라이브 동시접속 피크 | 50,000 (Main Event) |
| VOD 일일 재생 수 | 100,000 |
| 아카이브 검색 사용률 | 20% |

---

## 5. 국가별 목표 분배

### 5.1 Tier 1 시장 (60%)

| 국가 | 구독자 비중 | Y1 목표 | 특성 |
|------|:----------:|:-------:|------|
| 미국 | 30% | 15,000 | 핵심 시장 |
| 영국 | 10% | 5,000 | 유럽 거점 |
| 캐나다 | 8% | 4,000 | 북미 연계 |
| 호주 | 7% | 3,500 | 영어권 |
| 독일 | 5% | 2,500 | 유럽 최대 |

### 5.2 Tier 2 시장 (30%)

| 국가 | 구독자 비중 | Y1 목표 |
|------|:----------:|:-------:|
| 브라질 | 8% | 4,000 |
| 일본 | 6% | 3,000 |
| 한국 | 5% | 2,500 |
| 프랑스 | 5% | 2,500 |
| 스페인 | 3% | 1,500 |
| 이탈리아 | 3% | 1,500 |

### 5.3 Tier 3 시장 (10%)

| 지역 | 구독자 비중 | Y1 목표 |
|------|:----------:|:-------:|
| 기타 유럽 | 5% | 2,500 |
| 기타 아시아 | 3% | 1,500 |
| 기타 | 2% | 1,000 |

---

## 6. KPI 대시보드

### 6.1 Executive Dashboard

| 섹션 | 지표 | 갱신 주기 |
|------|------|:--------:|
| **Overview** | MAU, ARR, Churn | Daily |
| **Growth** | 신규 가입, 전환율 | Daily |
| **Engagement** | 시청 시간, 세션 수 | Daily |
| **Revenue** | MRR, ARPU | Weekly |

### 6.2 Product Dashboard

| 섹션 | 지표 | 갱신 주기 |
|------|------|:--------:|
| **Features** | Advanced Mode 사용률 | Daily |
| **Content** | 재생 수, 완료율 | Daily |
| **Platform** | 기기별 분포 | Weekly |

### 6.3 Marketing Dashboard

| 섹션 | 지표 | 갱신 주기 |
|------|------|:--------:|
| **Acquisition** | 채널별 CAC | Weekly |
| **Conversion** | Funnel 전환율 | Daily |
| **GG POKER** | Cross-platform 전환 | Weekly |

---

## 7. KPI 추적 도구

### 7.1 분석 도구 스택

| 도구 | 용도 | 담당 |
|------|------|------|
| **Mixpanel** | 이벤트 추적, Funnel | Product |
| **Amplitude** | 코호트 분석, 리텐션 | Product |
| **Stripe** | 매출, 구독 | Finance |
| **Looker** | BI 대시보드 | Data |
| **BigQuery** | 데이터 웨어하우스 | Data |

### 7.2 이벤트 추적 체계

```yaml
# 주요 이벤트
User Events:
  - user_signed_up
  - user_logged_in
  - subscription_started
  - subscription_upgraded
  - subscription_cancelled

Content Events:
  - content_played
  - content_completed
  - live_stream_joined
  - multiview_enabled
  - statsview_enabled
  - key_hands_clicked

GG POKER Events:
  - ggpoker_linked
  - play_now_clicked
  - chips_granted
```

---

## 8. Success Criteria

### 8.1 Y1 성공 기준

| 카테고리 | 지표 | 목표 | 필수 |
|---------|------|:----:|:----:|
| **Growth** | MAU | 50,000 | ✓ |
| **Growth** | 총 구독자 | 50,000 | ✓ |
| **Revenue** | ARR | $10M | ✓ |
| **Engagement** | 세션 시청 시간 | 45분 | - |
| **Retention** | Day 30 | 40% | ✓ |
| **Conversion** | Plus → Plus+ | 20% | - |

### 8.2 Y3 성공 기준

| 카테고리 | 지표 | 목표 |
|---------|------|:----:|
| **Growth** | MAU | 300,000 |
| **Growth** | 총 구독자 | 300,000 |
| **Revenue** | ARR | $79M |
| **GG POKER** | Cross-platform LTV | $500+ |

---

## 9. Risks & Mitigation

| 리스크 | 영향 KPI | 완화 전략 |
|--------|---------|----------|
| GGPass 유입 부족 | MAU, 신규 가입 | 직접 마케팅 강화 |
| Plus+ 전환 저조 | ARR | Advanced Mode 가치 강화 |
| 높은 이탈률 | ARR, MAU | 콘텐츠 다양화, 알림 최적화 |
| 국가별 규제 | 국가별 MAU | STRAT-0010 법규 준수 |
| 경쟁사 (PokerGo) | MAU | 차별화 기능 강화 |

---

## References

- [PRD-0002 WSOPTV OTT Platform MVP](../prds/PRD-0002-wsoptv-ott-platform-mvp.md)
- [STRAT-0003 Cross-Promotion Strategy](STRAT-0003-cross-promotion.md)
- [STRAT-0008 Timeline Roadmap](STRAT-0008-timeline-roadmap.md)

---

*Created: 2026-01-19*
*Last Updated: 2026-01-19*
