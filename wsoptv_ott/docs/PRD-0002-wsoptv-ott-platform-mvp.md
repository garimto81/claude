# PRD-0002: WSOPTV OTT Platform MVP

| 항목 | 값 |
|------|---|
| **Version** | 2.0 |
| **Status** | Draft |
| **Priority** | P2 |
| **Created** | 2026-01-07 |
| **Updated** | 2026-01-16 |
| **Author** | Claude Code |
| **Source** | michael_note.md, michael_vision_analysis.md |

---

## Executive Summary

WSOP(World Series of Poker) 공식 OTT 스트리밍 플랫폼 구축. 5개 플랫폼(Web, iOS, Android, Samsung TV, LG TV)에서 라이브 스트리밍, VOD, Timeshift, 20개국 자막을 지원하는 프리미엄 포커 방송 서비스. **$10 WSOP Plus** / **$50 WSOP Plus+** 2티어 구독 모델.

### 핵심 목표
- 글로벌 50만 동시접속 대응
- 1080p Full HD 품질의 라이브/VOD 제공
- **Timeshift**: 라이브 중 되감기 + 종료 후 VOD 보존
- **Advanced Mode** (Plus+ 전용): 3계층 Multi-view, StatsView → [PRD-0006](PRD-0006-advanced-mode.md)
- 20개국 다국어 자막

---

## Problem Statement

### 현재 상황
- WSOP 인수로 기존 PokerGo에서 운영하던 WSOP OTT 서비스 이관
- Michael의 비전(Insight)을 반영한 신규 WSOPTV OTT 서비스 런칭 필요
- GG POKER 생태계와 통합된 프리미엄 포커 방송 플랫폼 구축

### 해결 방안
- 통합 OTT 플랫폼 구축
- GGPass SSO 연동으로 기존 사용자 활용 (인증 + 빌링 통합)
- YouTube 대비 차별화된 프리미엄 기능 제공

### 프로모션 전략 (양방향 상호 보완)

**Flow 1: GG POKER → WSOPTV**
- GG POKER $10 칩 구매 → WSOPTV Plus 구독권 자동 발급

**Flow 2: WSOPTV → GG POKER**
- WSOPTV Plus $10 구독 → GG POKER $10 칩 제공
- WSOPTV Plus+ $50 구독 → GG POKER $50 칩 제공
- GGPass SSO 통합으로 GG POKER 접속 시 칩이 이미 생성되어 있음

> **참고 모델**: 쿠팡플레이 (로켓와우 ↔ 쿠팡플레이)


---

## Target Users

| 사용자 유형 | 설명 | 주요 니즈 |
|------------|------|----------|
| **포커 팬** | WSOP 시청자 | 라이브 경기, 하이라이트 |
| **GGPoker 회원** | 기존 플랫폼 사용자 | 심리스한 로그인, 연계 서비스 |
| **글로벌 시청자** | 비영어권 사용자 | 다국어 자막, 현지화 |

---

## Requirements

### Functional Requirements

#### FR-1: 라이브 스트리밍
| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-1.1 | 1080p Full HD 라이브 방송 | P0 |
| FR-1.2 | HLS 프로토콜 기반 스트리밍 | P0 |

> **참고**: 지연 처리는 프로덕션 방송에서 담당. TV 솔루션은 받는대로 즉시 송출.

#### FR-2: VOD & Quick VOD
| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-2.1 | 라이브→VOD 즉시 전환 (Quick VOD) | P0 |
| FR-2.2 | 시청 이력 및 이어보기 | P1 |
| FR-2.3 | 챕터/구간 탐색 | P1 |
| FR-2.4 | 다운로드 오프라인 시청 | P2 |

#### FR-3: Timeshift (YouTube 대비 차별화)

| 플랫폼 | DVR (Timeshift) | 라이브 종료 후 | 차별화 |
|--------|:---------------:|:-------------:|--------|
| **YouTube** | 비활성화 | 비공개 전환 | 맛보기 역할 |
| **WSOP TV** | **활성화** | **VOD로 보존** | 본 서비스 |

| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-3.1 | 라이브 중 되감기 (Timeshift) | P0 |
| FR-3.2 | 라이브 종료 즉시 VOD 자동 전환 (Quick VOD) | P0 |
| FR-3.3 | Catchup TV (처음부터 재시청) | P1 |

#### FR-4: Advanced Mode (Plus+ 전용)

> **상세 스펙**: [PRD-0006 Advanced Mode](PRD-0006-advanced-mode.md)

##### FR-4.1: 3계층 동적 Multi-view

**프로덕션 특징**:
GG POKER 방송은 여러 개의 테이블을 전환하여 방송하는 방식.
따라서 단순한 "PGM + PlayerCAM" 구조가 아닌 3계층 동적 구조 제공.

**계층 구조**:
| Layer | 설명 | 수량 |
|-------|------|------|
| **Layer 1: PGM** | PD 연출 메인 화면 | 1개 |
| **Layer 2: 피처 테이블** | PGM에서 제공하는 테이블 | n개 |
| **Layer 3: 플레이어 PlayerCAM** | 각 피처 테이블의 PlayerCAM | n개 (테이블별) |

**동적 레이아웃** (가로 3단):
- PGM 메인 → 우측 2개 사이드바 (피처 테이블 + PlayerCAM 비활성)
- 피처 테이블 메인 → 좌측 PGM + 우측 PlayerCAM 사이드바
- PlayerCAM 메인 → 좌측 2개 사이드바 (PGM + 피처 테이블)

**핵심 포인트**:
- 모든 피처 테이블이 PlayerCAM을 제공하는 것이 아님
- PlayerCAM 지원 테이블 선택 시에만 PlayerCAM 레이어 활성화
- 클릭/탭으로 메인 화면 전환, 레이아웃 동적 재배치

| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-4.1.1 | 3계층 동적 Multi-view 레이아웃 | P0 |
| FR-4.1.2 | 레이어 간 동적 전환 | P0 |
| FR-4.1.3 | 피처 테이블별 PlayerCAM 활성화/비활성화 | P0 |

##### FR-4.2: StatsView (2가지 구조)

**구조 1: GGPoker HUD 연동** (MVP)
- 데이터 소스: GGPoker HUD DB
- UI: GGPoker HUD와 동일한 정보 및 UI 설계
- 구현 난이도: 중간
- 우선순위: P0 (MVP)

**구조 2: 대회 실시간 연동** (Phase 2)
- 데이터 소스: 대회 실시간 데이터
- 특징: 베팅 액션 정보 실시간 표시
- 구현 난이도: 높음 (고급 작업)
- 우선순위: P1 (Phase 2)

| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-4.2.1 | GGPoker HUD 연동 StatsView | P0 |
| FR-4.2.2 | 대회 실시간 연동 StatsView | P1 |
| FR-4.3 | View Mode Switcher | P0 |

> **제약사항**: TV 앱에서는 Advanced Mode 미지원 (리모컨 UX 제약)

#### FR-5: 자막
| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-5.1 | 20개국 언어 자막 지원 | P0 |
| FR-5.2 | 영어 기반 번역 | P0 |
| FR-5.3 | VOD 자막 우선 지원 | P0 |
| FR-5.4 | 라이브 자막 (인력 투입) | P2 |

#### FR-6: 인증 & 결제
| ID | 요구사항 | 우선순위 |
|----|---------|:--------:|
| FR-6.1 | GGPass SSO 연동 (인증 + 빌링 통합) | P0 |
| FR-6.2 | 구독 플랜 관리 (Plus/Plus+) | P0 |
| FR-6.3 | 결제 필요 시 GGPass로 리다이렉트 | P0 |

#### FR-7: 구독 모델

| 티어 | 가격 | 명칭 | 주요 기능 |
|------|------|------|----------|
| Basic | $10/월 | **WSOP Plus** | 라이브, VOD, Timeshift, 자막 |
| Premium | $50/월 | **WSOP Plus+** | Plus 기능 + Advanced Mode (Multi-view, StatsView) |

> **참고**: Exclusive Content (behind-the-scenes)는 별도 제작하지 않음 → Advanced Mode가 Plus+의 유일한 차별화 포인트

### Non-Functional Requirements

#### NFR-1: 성능
| ID | 요구사항 | 목표치 |
|----|---------|-------|
| NFR-1.1 | 동시접속 | 50만 사용자 |
| NFR-1.2 | 초기 버퍼링 | < 3초 |
| NFR-1.3 | 재버퍼링 비율 | < 1% |

#### NFR-2: 보안
| ID | 요구사항 | 목표치 |
|----|---------|-------|
| NFR-2.1 | DRM | Widevine, FairPlay, PlayReady |
| NFR-2.2 | VPN 감지 | 80-90% 정확도 |
| NFR-2.3 | 국가별 블랙아웃 | 지원 |

#### NFR-3: 가용성
| ID | 요구사항 | 목표치 |
|----|---------|-------|
| NFR-3.1 | 서비스 가용성 | 99.9% |

---

## Technical Architecture

### 플랫폼 구성

![Platform Architecture](../../docs/images/PRD-0002/architecture.png)

[HTML 원본](../../docs/mockups/PRD-0002/architecture.html)

### 시스템 연동

> **시스템 아키텍처**는 위 다이어그램 참조

**GGPass SSO 통합**:
- 로그인: GGPass SSO 처리
- Billing: GGPass 내부에서 처리
- 결제 필요 시: GGPass 페이지로 이동하여 처리

> **참고**: 기술 스택 (CDN, DRM, Database 등)은 향후 협업사 제안에 따라 결정

---

## UI/UX Design

### Watch Screen

![Watch Screen](../../docs/images/PRD-0002/watch-screen.png)

[HTML 원본](../../docs/mockups/PRD-0002/watch-screen.html)

**주요 기능**:
- 대형 플레이어 (히어로 영역)
- 라이브 뱃지 표시
- 3계층 멀티뷰 전환 버튼
- 20개국 자막 선택
- Quick VOD 하이라이트 섹션

### Multi-View (3계층 동적 레이아웃)

#### Layer 1: Main PGM

![Layer 1: Main PGM](../../docs/images/PRD-0002/multiview-layer1-pgm.png)

[HTML 원본](../../docs/mockups/PRD-0002/multiview-layer1-pgm.html)

**레이아웃**: 메인에 PGM, 우측에 피처 테이블 목록만

#### Layer 2: Feature Table

![Layer 2: Feature Table](../../docs/images/PRD-0002/multiview-layer2-table.png)

[HTML 원본](../../docs/mockups/PRD-0002/multiview-layer2-table.html)

**레이아웃**: 좌측에 PGM+다른 테이블, 메인에 선택한 테이블, 우측에 PlayerCAM 목록

#### Layer 3: PlayerCAM

![Layer 3: PlayerCAM](../../docs/images/PRD-0002/multiview-layer3-playercam.png)

[HTML 원본](../../docs/mockups/PRD-0002/multiview-layer3-playercam.html)

**레이아웃**: 좌측에 PGM+피처 테이블, 메인에 선택한 PlayerCAM, 우측에 다른 PlayerCAM

**주요 기능**:
- 3계층 동적 레이아웃 (PGM → 피처 테이블 → PlayerCAM)
- 클릭으로 메인 화면 전환
- 피처 테이블별 PlayerCAM 지원 여부 표시 (PlayerCAM 뱃지)
- 동기화 상태 표시
- Layer 전환 버튼

### Multi-View UX Flow

![Multi-View UX Flow](../../docs/images/PRD-0002/multiview-ux-flow.png)

[HTML 원본](../../docs/mockups/PRD-0002/multiview-ux-flow.html)

### StatsView Video Player Layout

![StatsView Layout](../../docs/images/PRD-0002/player-with-statsview.png)

[HTML 원본](../../docs/mockups/PRD-0002/player-with-statsview.html)

**레이아웃 구조**:
- 좌측: 플레이어 통계 HUD (VPIP/PFR/3Bet/AF/Stack)
- 중앙: 비디오 플레이어
- 우측: 게임 정보 HUD (Pot/Odds/SPR/Action History)
- HUD 토글 ON/OFF 지원

### Collections Screen

![Collections Screen](../../docs/images/PRD-0002/collections-screen.png)

[HTML 원본](../../docs/mockups/PRD-0002/collections-screen.html)

**주요 기능**:
- 히어로 배너 (Featured Collection)
- 필터 탭 (Main Event, Bracelet, High Roller, Classics)
- 시청 진행률 표시
- 큐레이티드 플레이리스트
- 검색 기능

---

## Scope

### In Scope (MVP)
| 항목 | 설명 |
|------|------|
| 플랫폼 | Web, iOS, Android, Samsung TV, LG TV |
| 화질 | 1080p Full HD |
| 멀티뷰 | 3계층 동적 레이아웃 (Web/Mobile만) |
| 자막 | 20개국 |
| 메뉴 | Watch + Collections 2개만 |

### Out of Scope
| 항목 | 사유 |
|------|------|
| 4K 지원 | 장비/인프라 비용 과다 |
| VLM (비디오 AI 분석) | 고비용, 별도 업체 필요 |
| 뉴스 섹션 | 불필요 |
| 전적/플레이어 정보 | WSOP.com 링크 연결 |
| 티켓팅 | 온라인 구독만 |
| Roku/Fire TV | Phase 2 |

---

## Cost Factors

### 비용 절감 포인트
| 항목 | 내용 | 영향도 |
|------|------|:------:|
| GGPass SSO | 로그인/가입 개발 불필요 | 높음 |
| 빌링 시스템 | GGPass 내부 처리 | 높음 |
| 스케줄 API | 내부 DB 연동 | 중간 |
| 사이트 범위 | 2개 메뉴만 | 높음 |

### 비용 증가 요소
| 항목 | 내용 | 영향도 |
|------|------|:------:|
| TV 앱 | 플랫폼별 개발 | 중간 |

---

## Timeline (Phase)

### Phase 1: MVP
- Web + Mobile 앱
- 라이브 + VOD + 자막
- GGPass SSO 연동 (인증 + 빌링)
- StatsView 구조 1 (GGPoker HUD 연동)

### Phase 2: 확장
- TV 앱 (Samsung, LG)
- 3계층 멀티뷰
- Quick VOD
- StatsView 구조 2 (대회 실시간 연동)

### Phase 3: 고도화
- 4K 지원
- AI 챕터/요약
- Roku/Fire TV

---

## Open Questions

1. TV 미러링/캐스팅 지원 여부
2. 블랙아웃 정책 (사이트 단위 vs 영상 단위)

---

## References

- [Michael Vision Note](../docs/order/michael_note.md)
- [Michael Vision Analysis](../docs/order/michael_vision_analysis.md)
- [PRD-0006 Advanced Mode](PRD-0006-advanced-mode.md)

---

## Revision History

| 버전 | 날짜 | 작성자 | 내용 |
|------|------|--------|------|
| 1.0 | 2026-01-07 | Claude Code | 최초 작성 |
| 2.0 | 2026-01-16 | Claude Code | Problem Statement 수정, FR-1.3/1.4 삭제, FR-4 3계층 구조로 재설계, StatsView 2구조 추가, GGPass SSO+Billing 통합, 기술스택/Risks/Metrics 섹션 삭제, 목업 B&W 재설계 |
| 2.1 | 2026-01-16 | Claude Code | FANCAM→PlayerCAM 용어 변경, 프로모션 양방향 흐름 추가, UX Flow/StatsView Layout 목업 추가 |
