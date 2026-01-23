# WPT TV (World Poker Tour) 솔루션 분석 보고서

**Report ID**: REPORT-2026-01-21-wpttv
**Date**: 2026-01-21
**Author**: Claude Code
**Related**: [PRD-0002 WSOPTV OTT Platform MVP](../prds/PRD-0002-wsoptv-ott-platform-mvp.md)

---

## Executive Summary

World Poker Tour (WPT)는 **무료 OTT 스트리밍 + 구독 기반 게임 플랫폼**의 이중 모델을 성공적으로 운영 중입니다. WSOPTV 개발에 참고할 핵심 인사이트를 정리합니다.

### 핵심 발견 요약

| 영역 | WPT 현황 | WSOPTV 적용 제안 |
|------|----------|------------------|
| **OTT 플랫폼** | WatchWPT (무료, 광고 기반) | 무료 Tier 필수 |
| **구독 모델** | ClubWPT $27.95~$149.95/월 | Premium Tier 참고 |
| **글로벌 확장** | WPT Global (135개국 실제 금전) | 규제 준수 전략 |
| **방송 파트너** | CBS Sports Network + 20+ OTT | 다채널 배포 |
| **기술 파트너** | Unreel Entertainment | 기술 벤더 평가 |

---

## 1. WPT 디지털 생태계 구조

### 1.1 브랜드 포트폴리오

```
World Poker Tour 생태계
├── WPT (라이브 토너먼트)
│   └── $3,500+ 바이인 프로 대상
├── WPT Prime
│   └── $1,100~$2,400 중급 대상
├── WatchWPT (OTT 스트리밍)
│   └── 무료 + Premium $4.99/월
├── ClubWPT (구독 스윕스테이크)
│   └── $27.95~$149.95/월
├── ClubWPT Gold (교육 + 스윕스테이크)
│   └── 2025년 런칭, GTO 코칭 플랫폼
└── WPT Global (실제 금전 온라인 포커)
    └── 135개국, 미국/영국/EU 제외
```

### 1.2 수익 모델 비교

| 플랫폼 | 수익 모델 | 타겟 시장 | 규제 상태 |
|--------|----------|----------|----------|
| **WatchWPT** | 광고 (AVOD) + Premium $4.99 | 전세계 | 규제 없음 |
| **ClubWPT** | 구독료 ($27.95-$149.95/월) | 미국 43개 주 + 4개국 | 스윕스테이크 |
| **WPT Global** | 레이크 (실제 금전) | 아시아, 남미, 일부 유럽 | Curaçao 라이선스 |
| **ClubWPT Gold** | 교육 크레딧 + 칩 환전 | 미국 (CA, NY 포함) | 하이브리드 |

---

## 2. WatchWPT - 핵심 OTT 플랫폼 분석

### 2.1 출시 및 기술 인프라

| 항목 | 상세 |
|------|------|
| **출시일** | 2019년 3월 14일 |
| **기술 파트너** | Unreel Entertainment |
| **초기 콘텐츠** | 250시간+ 아카이브 |
| **현재 콘텐츠** | 시즌 1~20 + 라이브 |

### 2.2 플랫폼 가용성

```
┌─────────────────────────────────────────────────────────────────┐
│                    WatchWPT 배포 채널                            │
├─────────────────────────────────────────────────────────────────┤
│  모바일                                                         │
│  ├── iOS (App Store)                                           │
│  └── Android (Google Play)                                      │
├─────────────────────────────────────────────────────────────────┤
│  스마트 TV                                                       │
│  ├── Samsung TV Plus (US, UK, Brazil, Mexico)                  │
│  ├── LG TV / LG WatchWPT App                                   │
│  ├── Vizio WatchFree+                                          │
│  └── Google TV                                                  │
├─────────────────────────────────────────────────────────────────┤
│  스트리밍 디바이스                                               │
│  ├── Roku                                                       │
│  ├── Fire TV                                                    │
│  └── Apple TV                                                   │
├─────────────────────────────────────────────────────────────────┤
│  FAST/AVOD 파트너 (20+)                                         │
│  ├── Fubo, Sling, PlutoTV, Tubi, Xumo                         │
│  ├── Philo, Freevee (Amazon), Fawesome                         │
│  ├── Local Now, Whale TV+, KlowdTV                             │
│  ├── Distro TV, Freecast, FTF                                  │
│  ├── Xiaomi TV+, Sportworld, Canela TV                         │
│  └── Mansa                                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 콘텐츠 전략

| 콘텐츠 유형 | 설명 | 접근성 |
|------------|------|-------|
| **아카이브** | 시즌 1~20 전체 파이널 테이블 | 무료 |
| **WPT Greatest** | Greatest Final Tables, Tales From The Felt | 무료 |
| **라이브 스트림** | 주요 대회 파이널 테이블 | 무료 |
| **24/7 스트림** | Twitch, Rumble, YouTube 상시 방송 | 무료 |
| **Premium** | 추가 기능 | $4.99/월 |

### 2.4 라이브 스트리밍 채널

| 플랫폼 | 용도 | URL |
|--------|------|-----|
| **Twitch** | 24/7 스트림 + 라이브 | twitch.tv/wpt |
| **YouTube** | 라이브 파이널 테이블 | youtube.com/wpt |
| **Facebook** | 라이브 + 클립 | facebook.com/wpt |
| **Rumble** | 24/7 + 라이브 | rumble.com/wpt |

---

## 3. 기술 파트너: Unreel Entertainment

### 3.1 회사 개요

| 항목 | 상세 |
|------|------|
| **설립** | 2015년 |
| **투자** | $2.4M (Digital Ignition, Vineyard Point, Poise Ventures) |
| **핵심 기술** | Bumblebee AI (콘텐츠 분석 및 개인화) |
| **파트너** | Verizon Digital Media Services |

### 3.2 Unreel 제공 기능

```
Unreel OTT 플랫폼 기능
├── 앱 빌더
│   ├── iOS / Android 네이티브 앱
│   ├── Roku, Fire TV, Apple TV
│   └── 웹사이트 (WorldPokerTour.tv)
├── 콘텐츠 관리
│   ├── 7M+ 비디오 신디케이션
│   ├── 다중 앱/사이트 관리
│   └── OTT 네트워크 배포
├── Bumblebee AI
│   ├── 콘텐츠 자동 분석
│   ├── 개인화 추천
│   └── 사용자 참여 최적화
└── 수익화
    ├── 광고 기반 (AVOD)
    └── 구독 기반 (SVOD)
```

### 3.3 Verizon 파트너십 (2018)

- 100+ 신규 스트리밍 서비스 런칭 지원
- WPT, Level One, Enthusiast Network 포함
- CDN 및 인프라 제공

---

## 4. ClubWPT - 구독 모델 상세

### 4.1 가격 구조

| 플랜 | 월 비용 | 연간 비용 | 할인율 |
|------|--------|----------|-------|
| **월간** | $33.95 | - | - |
| **분기** | $24.98 | $89.95 (3개월) | 12% |
| **연간** | $24.99 | $299.95 | 26% |

### 4.2 VIP 멤버십 혜택

| 혜택 | 상세 |
|------|------|
| **토너먼트** | 월 $100,000+ 상금풀 접근 |
| **콘텐츠** | WPT TV 에피소드 전체 시청 |
| **쇼핑** | ShopWPT 10% 할인 |
| **이벤트** | ScoreBig 이벤트 티켓 $10 할인 |
| **플레이** | 24/7 무제한 포커 |

### 4.3 Diamond 멤버십 추가 혜택

| 혜택 | 상세 |
|------|------|
| **가격** | $149.95/월 |
| **교육** | Upswing Poker Lab 1.0 전체 접근 |
| **전략** | Elite Cash Game Exploits 코스 |
| **토너먼트** | Diamond 전용 대회 |

### 4.4 Super SATurdays

| 항목 | 상세 |
|------|------|
| **가격** | $100/월 (애드온) |
| **특전** | 주간 WPT/WPT Prime 패스포트 대회 |
| **대상** | 라이브 이벤트 진출 희망자 |

---

## 5. 방송 파트너십

### 5.1 TV 방송

| 파트너 | 역할 | 시작 |
|--------|------|------|
| **CBS Sports Network** | 독점 TV 파트너 | 시즌 XXI (2022) |
| **Fox Sports Net** | 이전 TV 파트너 | - |

### 5.2 OTT 배포

| 카테고리 | 파트너 |
|----------|--------|
| **유료 스트리밍** | YouTube TV, Fubo, DIRECTV Stream, Hulu + Live TV |
| **FAST 채널** | PlutoTV, Tubi, Xumo, Freevee |
| **포커 전문** | PokerGO (구독 기반) |
| **글로벌** | Xiaomi TV+, Sportworld, Canela TV |

---

## 6. WPT Global - 실제 금전 플랫폼

### 6.1 플랫폼 개요

| 항목 | 상세 |
|------|------|
| **출시** | 2022년 |
| **운영사** | Seventip N.V |
| **라이선스** | Curaçao Gaming Authority |
| **가용 국가** | 135개국 |
| **제외 지역** | 미국, 영국, 프랑스, 스페인, 이탈리아, 포르투갈 |

### 6.2 보안 기술

| 기술 | 설명 |
|------|------|
| **FairGame AI** | 담합/봇 실시간 탐지 |
| **RNG 인증** | GLI 독립 감사 완료 |
| **좌석 관리** | 초보자/레크리에이션 좌석 예약 시스템 |
| **Game Integrity** | 50명+ 전담 팀 운영 |

### 6.3 게임 종류

| 게임 | 포맷 |
|------|------|
| **Texas Hold'em** | 캐시게임, MTT, SNG |
| **PLO** | 4카드 오마하 |
| **Short Deck** | 6+ 홀덤 |
| **토너먼트** | Bounty Hunter, Mystery Bounty, PKO |
| **위성** | WPT 라이브 이벤트 예선 |

---

## 7. 방송 기술: RFID & 오버레이

### 7.1 홀카드 카메라 시스템

| 세대 | 기술 | 시기 |
|------|------|------|
| **1세대** | 언더테이블 카메라 | 1999 (Late Night Poker) |
| **2세대** | 레일 내장 카메라 | 2000년대 초 (WSOP, HSP) |
| **3세대** | RFID 테이블 시스템 | 2012+ (EPT) |

### 7.2 현대 RFID 시스템

```
RFID 방송 시스템 아키텍처
├── 하드웨어
│   ├── RFID 칩 내장 카드
│   ├── 펠트 하단 RFID 리더
│   └── 각 좌석별 안테나
├── 소프트웨어 (PokerGFX 등)
│   ├── 실시간 카드 인식
│   ├── 오버레이 그래픽 생성
│   ├── 승률 계산 (실시간)
│   └── 멀티캠 자동 전환
└── 출력
    ├── 4K UHD 지원
    ├── 딜레이 스트림
    └── 라이브 스트림
```

### 7.3 주요 벤더

| 벤더 | 제품 | 고객 |
|------|------|------|
| **PokerGFX** | 통합 RFID + 오버레이 솔루션 | WSOP, PokerGO |
| **wTVision** | RFID 테이블 시스템 | PokerStars IT |
| **Cardroom Direct** | 이벤트용 RFID 테이블 | 다수 토너먼트 |

---

## 8. WSOPTV 적용 제안

### 8.1 OTT 전략 비교

| 항목 | WPT 전략 | WSOPTV 제안 |
|------|---------|------------|
| **무료 Tier** | WatchWPT (AVOD) | WSOPTV Free (AVOD) |
| **유료 Tier** | Premium $4.99/월 | Plus+ $9.99/월 |
| **프리미엄** | ClubWPT $27.95+/월 | Advanced Mode $19.99/월 |
| **라이브** | Twitch/YouTube 무료 | 무료 라이브 유지 |

### 8.2 플랫폼 우선순위

```
Phase 1 (MVP)
├── Web (Desktop/Mobile)
├── iOS App
├── Android App
└── YouTube/Twitch 라이브

Phase 2
├── Samsung TV Plus
├── LG TV
├── Roku
└── Fire TV

Phase 3
├── FAST 채널 파트너십
│   ├── PlutoTV
│   ├── Tubi
│   └── Freevee
└── 글로벌 확장
```

### 8.3 기술 파트너 평가

| 옵션 | 장점 | 단점 |
|------|------|------|
| **Unreel** | WPT 검증, AI 개인화 | 소규모 |
| **JW Player** | 대규모 인프라 | 비용 |
| **자체 개발** | 완전 제어 | 시간/비용 |
| **Verizon MDM** | CDN 강점 | 복잡성 |

### 8.4 차별화 전략

| WPT에 없는 기능 | WSOPTV 우위 |
|----------------|-------------|
| **Advanced Mode** | 3계층 Multi-view, StatsView |
| **WSOP 브랜드** | 세계 최고 포커 브랜드 |
| **GGPass SSO** | 통합 계정 시스템 |
| **20개국 자막** | 글로벌 접근성 |
| **Timeshift** | 실시간 되감기 |

---

## 9. 시장 데이터

### 9.1 미국 포커 시장

| 지표 | 수치 | 출처 |
|------|------|------|
| **정기 플레이어** | 4,000만 명 | WPT Press |
| **TV 시청자** | 690만 명 | WPT Press |
| **OTT 시프트** | 증가 추세 | WPT Press |

### 9.2 WPT 구독 가용 지역

| 지역 | ClubWPT | WPT Global |
|------|---------|------------|
| **미국** | 43개 주 | ❌ |
| **캐나다** | ✅ | ❌ |
| **영국** | ✅ | ❌ |
| **호주** | ✅ | ❌ |
| **프랑스** | ✅ | ❌ |
| **아시아** | ❌ | ✅ |
| **남미** | ❌ | ✅ |

---

## 10. 결론 및 권장사항

### 10.1 WPT 모델의 강점

1. **다층 수익 모델**: 무료(광고) → 저가 구독 → 고가 구독 → 실제 금전
2. **광범위한 배포**: 20+ OTT 파트너, 주요 스마트 TV 내장
3. **라이브 접근성**: Twitch/YouTube 무료 라이브로 팬 확보
4. **규제 회피**: 스윕스테이크 모델로 미국 시장 공략

### 10.2 WSOPTV 권장 전략

| 우선순위 | 전략 | 근거 |
|:--------:|------|------|
| **1** | 무료 Tier 필수 도입 | WPT 성공 모델 |
| **2** | FAST 채널 파트너십 | 신규 사용자 유입 |
| **3** | Advanced Mode 차별화 | WPT에 없는 기능 |
| **4** | 스마트 TV 앱 우선 | 시청 패턴 변화 |
| **5** | Unreel/JW Player 평가 | 기술 파트너 선정 |

### 10.3 다음 단계

- [ ] Unreel Entertainment 기술 미팅
- [ ] FAST 채널 파트너 (PlutoTV, Tubi) 협의
- [ ] Samsung/LG TV 앱 요구사항 정의
- [ ] RFID 방송 시스템 벤더 선정

---

## Sources

### 공식 사이트
- [World Poker Tour](https://www.worldpokertour.com/)
- [WatchWPT Smart TV App](https://www.worldpokertour.com/watchwpt-smart-tv-app/)
- [Where to Watch WPT](https://www.worldpokertour.com/watch-wpt)
- [ClubWPT Pricing](https://www.clubwpt.com/pricing/)
- [WPT Global](https://wptglobal.com/)

### 분석 자료
- [Pokerfuse: WPT OTT Streaming Service Launch](https://pokerfuse.com/news/media-and-software/210467-world-poker-tour-launches-new-free-poker-ott-streaming/)
- [Pokerfuse: WPT Brands Compared](https://pokerfuse.com/latest-news/2026/1/key-worldpokertour-brands-compared-understanding/)
- [Pokerfuse: WPT 2026 Guide](https://pokerfuse.com/live-poker/world-poker-tour/)
- [PokerNews: WPT Global Review](https://www.pokernews.com/wpt-global/)

### 기술 파트너
- [Unreel Entertainment](https://www.unreel.me/)
- [TechCrunch: Unreel.me Launch](https://techcrunch.com/2016/04/14/unreel-me-launch/)
- [PokerGFX (RFID Solutions)](https://www.videopokertable.net/)

### 방송
- [WPT CBS Sports Network Partnership](https://www.worldpokertour.com/press-release/world-poker-tour-secures-new-broadcast-partnership-with-cbs-sports-network)
- [Pluto TV WPT Channel](https://pluto.tv/us/live-tv/5616f9c0ada51f8004c4b091)

---

*Last Updated: 2026-01-21*
