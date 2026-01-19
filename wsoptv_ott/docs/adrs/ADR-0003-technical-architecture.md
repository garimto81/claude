# ADR-0003: WSOPTV OTT Technical Architecture

| 항목 | 값 |
|------|---|
| **Status** | Proposed |
| **Impact** | High |
| **Created** | 2026-01-19 |
| **Author** | Claude Code |
| **References** | PRD-0002, PRD-0005, PRD-0006, STRAT-0008 |

---

## Context

WSOPTV OTT 플랫폼 구축을 위한 **기술 스택 권장안 및 아키텍처 설계**가 필요합니다. 5개 플랫폼(Web, iOS, Android, Samsung TV, LG TV)을 지원하며, 50만 동시접속을 처리할 수 있는 확장 가능한 아키텍처를 설계합니다.

### 주요 고려사항

1. **PRD-0002**: 50만 동시접속, 1080p, Timeshift, DRM
2. **PRD-0006**: 3계층 Multi-view, StatsView, Key Hands
3. **PRD-0005**: 협업사 RFP 대응
4. **STRAT-0008**: Phase별 점진적 구축

---

## Decision

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              WSOPTV OTT Platform                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                           CLIENT LAYER                                   │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │   Web    │  │   iOS    │  │ Android  │  │Samsung TV│  │  LG TV   │   │    │
│  │  │ Next.js  │  │ SwiftUI  │  │ Kotlin   │  │  Tizen   │  │  webOS   │   │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │    │
│  └───────┼─────────────┼─────────────┼─────────────┼─────────────┼──────────┘    │
│          │             │             │             │             │               │
│          └─────────────┴─────────────┼─────────────┴─────────────┘               │
│                                      │                                           │
│  ┌───────────────────────────────────┼───────────────────────────────────────┐   │
│  │                         API GATEWAY (Kong/AWS API Gateway)                │   │
│  └───────────────────────────────────┼───────────────────────────────────────┘   │
│                                      │                                           │
│  ┌───────────────────────────────────┼───────────────────────────────────────┐   │
│  │                           SERVICE LAYER                                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │   Auth   │  │ Content  │  │Streaming │  │  Stats   │  │  Search  │    │   │
│  │  │ Service  │  │ Service  │  │ Service  │  │ Service  │  │ Service  │    │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │   │
│  └───────┼─────────────┼─────────────┼─────────────┼─────────────┼───────────┘   │
│          │             │             │             │             │               │
│  ┌───────┼─────────────┼─────────────┼─────────────┼─────────────┼───────────┐   │
│  │       │          DATA LAYER       │             │             │           │   │
│  │  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐    │   │
│  │  │ GGPass   │  │PostgreSQL│  │  Redis   │  │   S3     │  │Elastic   │    │   │
│  │  │  SSO     │  │(Supabase)│  │  Cache   │  │ Storage  │  │ search   │    │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐   │
│  │                        INFRASTRUCTURE LAYER                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │   CDN    │  │   DRM    │  │   VPN    │  │ Monitor  │  │   CI/CD  │    │   │
│  │  │(Akamai)  │  │(Multi)   │  │ Detect   │  │(Datadog) │  │(GitHub)  │    │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │   │
│  └───────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Frontend Stack

### 1.1 Web: Next.js 14 + React 18

| 항목 | 선택 | 근거 |
|------|------|------|
| **Framework** | Next.js 14 | SSR, ISR, App Router |
| **UI Library** | React 18 | Concurrent Features |
| **State** | Zustand | 경량, 간단한 API |
| **Styling** | Tailwind CSS | 빠른 개발, 일관성 |
| **Video Player** | Video.js + hls.js | HLS 지원, 커스터마이징 |
| **Forms** | React Hook Form | 성능, 타입 안전성 |

**프로젝트 구조**:
```
src/
├── app/                    # Next.js App Router
│   ├── (auth)/             # 인증 그룹
│   ├── (main)/             # 메인 레이아웃
│   │   ├── watch/          # 시청 페이지
│   │   ├── collections/    # 컬렉션 페이지
│   │   └── profile/        # 프로필
│   └── api/                # API Routes
├── components/             # UI 컴포넌트
│   ├── player/             # 비디오 플레이어
│   ├── multiview/          # Multi-view
│   └── statsview/          # StatsView
├── hooks/                  # Custom Hooks
├── lib/                    # 유틸리티
├── store/                  # Zustand Store
└── types/                  # TypeScript 타입
```

### 1.2 iOS: SwiftUI

| 항목 | 선택 | 근거 |
|------|------|------|
| **UI Framework** | SwiftUI | 선언적 UI, Apple 표준 |
| **Architecture** | MVVM + Coordinator | 테스트 용이성 |
| **Networking** | URLSession + Combine | 네이티브, 비동기 |
| **Video Player** | AVKit + HLS | 네이티브 성능 |
| **DRM** | FairPlay | Apple 표준 |

**최소 지원**: iOS 15.0+

### 1.3 Android: Kotlin + Jetpack Compose

| 항목 | 선택 | 근거 |
|------|------|------|
| **Language** | Kotlin | 현대적, 간결 |
| **UI Framework** | Jetpack Compose | 선언적 UI |
| **Architecture** | MVVM + Clean | 테스트 용이성 |
| **Networking** | Ktor / Retrofit | 코루틴 지원 |
| **Video Player** | ExoPlayer | Google 표준, DRM 지원 |
| **DRM** | Widevine | Android 표준 |

**최소 지원**: Android 8.0+ (API 26)

### 1.4 Samsung TV: Tizen

| 항목 | 선택 | 근거 |
|------|------|------|
| **Platform** | Tizen 5.0+ | Samsung TV 표준 |
| **Framework** | React (Web App) | 재사용성 |
| **Video Player** | AVPlay API | Tizen 네이티브 |
| **DRM** | PlayReady | Samsung 지원 |

### 1.5 LG TV: webOS

| 항목 | 선택 | 근거 |
|------|------|------|
| **Platform** | webOS 5.0+ | LG TV 표준 |
| **Framework** | React (Web App) | 재사용성 |
| **Video Player** | LG Media API | webOS 네이티브 |
| **DRM** | PlayReady / Widevine | LG 지원 |

---

## 2. Video Player Architecture

### 2.1 Player Stack

```
┌─────────────────────────────────────────────────────────────┐
│                      WSOPTV Player                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   UI Layer (React)                      │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │ │
│  │  │ Controls │ │Multi-view│ │StatsView │ │Key Hands │   │ │
│  │  │   Bar    │ │ Selector │ │  HUD     │ │  Modal   │   │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                 Player Core Layer                       │ │
│  │  ┌──────────────────┐  ┌──────────────────┐            │ │
│  │  │    Video.js      │  │    hls.js        │            │ │
│  │  │  (Web/TV)        │  │ (HLS Streaming)  │            │ │
│  │  └──────────────────┘  └──────────────────┘            │ │
│  │  ┌──────────────────┐  ┌──────────────────┐            │ │
│  │  │   Bitmovin SDK   │  │   Native Player  │            │ │
│  │  │ (Mobile/TV Alt)  │  │ (AVKit/ExoPlayer)│            │ │
│  │  └──────────────────┘  └──────────────────┘            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    DRM Layer                            │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐               │ │
│  │  │ Widevine │ │ FairPlay │ │PlayReady │               │ │
│  │  │ (Chrome, │ │ (Safari, │ │(Edge, TV)│               │ │
│  │  │ Android) │ │   iOS)   │ │          │               │ │
│  │  └──────────┘ └──────────┘ └──────────┘               │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Player Features by Platform

| Feature | Web | iOS | Android | Samsung TV | LG TV |
|---------|:---:|:---:|:-------:|:----------:|:-----:|
| HLS Streaming | ✓ | ✓ | ✓ | ✓ | ✓ |
| DRM | Widevine | FairPlay | Widevine | PlayReady | PlayReady |
| Timeshift | ✓ | ✓ | ✓ | ✓ | ✓ |
| Multi-view | ✓ | ✓ | ✓ | ✗ | ✗ |
| StatsView | ✓ | ✓ | ✓ | ✗ | ✗ |
| 4분할 | ✓ | ✓ | ✓ | ✗ | ✗ |
| Key Hands | ✓ | ✓ | ✓ | ✗ | ✗ |
| Picture-in-Picture | ✓ | ✓ | ✓ | ✗ | ✗ |
| Chromecast | ✓ | ✓ | ✓ | - | - |
| AirPlay | ✓ | ✓ | - | - | - |

### 2.3 Multi-view Implementation

**옵션 비교**:

| 옵션 | 설명 | 장점 | 단점 | 권장 |
|------|------|------|------|:----:|
| **A. 클라이언트 믹싱** | 여러 스트림 동시 수신 | 유연한 레이아웃 | 트래픽 ↑, CPU ↑ | - |
| **B. 서버 믹싱** | 서버에서 합성 후 송출 | 트래픽 ↓ | 레이아웃 고정 | ✓ |
| **C. 하이브리드** | 메인 + 선택 스트림 | 균형 | 복잡도 ↑ | - |

**권장안**: **B. 서버 믹싱**

- 30분+ 의도적 지연 방송이므로 **사전 렌더링 가능**
- 트래픽 비용 최적화 (1 스트림 vs 4+ 스트림)
- 클라이언트 부하 감소

**서버 믹싱 레이아웃 옵션**:
```
Layout ID: "4split_equal"
┌───────────────┬───────────────┐
│    Stream 1   │    Stream 2   │
├───────────────┼───────────────┤
│    Stream 3   │    Stream 4   │
└───────────────┴───────────────┘

Layout ID: "3layer_pgm_main"
┌───────────────────────┬───────┐
│                       │  Sub1 │
│      Main PGM         ├───────┤
│                       │  Sub2 │
└───────────────────────┴───────┘
```

### 2.4 Timeshift (DVR) Implementation

**기술 스펙**:

| 항목 | 스펙 |
|------|------|
| DVR Window | 4시간 (라이브 중) |
| Quick VOD 전환 | < 60초 |
| Seek 정확도 | ±2초 |
| Catchup 시작 | 라이브 시작점 |

**구현 방식**:
```
┌─────────────────────────────────────────────────────────────┐
│                    Timeshift Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Live Encoder ──→ Origin Server ──→ CDN Edge Cache          │
│       │               │                   │                  │
│       │               ▼                   │                  │
│       │        HLS Manifest               │                  │
│       │        (4hr sliding window)       │                  │
│       │               │                   │                  │
│       ▼               ▼                   ▼                  │
│  VOD Archive    DVR Playback        Live Playback            │
│  (S3/GCS)       (Seek enabled)      (Low latency)            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Backend Stack

### 3.1 API Layer

| 항목 | 선택 | 근거 |
|------|------|------|
| **Runtime** | Node.js 20 LTS | 성숙한 생태계, 비동기 |
| **Framework** | Fastify | 성능, 타입 지원 |
| **API Style** | REST + GraphQL | REST(기본) + GraphQL(복잡 쿼리) |
| **Validation** | Zod | 타입 안전성 |
| **Documentation** | OpenAPI 3.0 | 표준 스펙 |

**서비스 분리**:

| Service | 역할 | 기술 |
|---------|------|------|
| **Auth Service** | SSO 연동, 세션 관리 | Fastify + Passport |
| **Content Service** | 콘텐츠 CRUD, 메타데이터 | Fastify + Prisma |
| **Streaming Service** | 스트림 URL 생성, DRM | Fastify |
| **Stats Service** | HUD 데이터, StatsView | Fastify + Redis |
| **Search Service** | 검색, 필터링 | Fastify + Elasticsearch |

### 3.2 Database

| 용도 | 선택 | 근거 |
|------|------|------|
| **Primary DB** | PostgreSQL (Supabase) | ACID, JSON 지원, RLS |
| **Cache** | Redis | 세션, 실시간 데이터 |
| **Search** | Elasticsearch | 전문 검색, 필터링 |
| **Object Storage** | S3 / GCS | 비디오, 썸네일 |

**Supabase 활용**:
- PostgreSQL 관리형 서비스
- Row Level Security (RLS) 적용
- Realtime 구독 (향후)
- Edge Functions (서버리스)

### 3.3 API Gateway

| 항목 | 선택 | 근거 |
|------|------|------|
| **Gateway** | Kong / AWS API Gateway | Rate limiting, Auth |
| **Load Balancer** | ALB | AWS 통합 |

---

## 4. Infrastructure

### 4.1 Cloud Provider

**권장**: **AWS** (Primary) + Multi-Region

| 리전 | 용도 | 서비스 |
|------|------|--------|
| us-east-1 | Primary (미국) | 전체 |
| eu-west-1 | Secondary (유럽) | CDN, Cache |
| ap-northeast-1 | Secondary (아시아) | CDN, Cache |

### 4.2 CDN

| 항목 | 선택 | 근거 |
|------|------|------|
| **Primary CDN** | Akamai | 비디오 스트리밍 전문 |
| **Backup CDN** | CloudFront | AWS 통합, 비용 효율 |

**CDN 설정**:
- HLS 세그먼트 캐싱
- 지역별 Edge 서버
- Multi-CDN 페일오버

### 4.3 DRM

| 플랫폼 | DRM | 라이선스 서버 |
|--------|-----|-------------|
| Chrome, Firefox | Widevine | Google / BuyDRM |
| Safari, iOS | FairPlay | Apple / BuyDRM |
| Edge, TV | PlayReady | Microsoft / BuyDRM |

**DRM 통합 서비스**: BuyDRM (KeyOS) 또는 PallyCon

### 4.4 Monitoring

| 용도 | 선택 |
|------|------|
| **APM** | Datadog / New Relic |
| **Log** | Datadog Logs / CloudWatch |
| **Error** | Sentry |
| **Uptime** | Pingdom / UptimeRobot |

---

## 5. Security

### 5.1 Authentication

```
┌─────────────────────────────────────────────────────────────┐
│                    Authentication Flow                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User ──→ WSOPTV App ──→ GGPass SSO ──→ OAuth 2.0 Token     │
│                │                             │               │
│                │                             ▼               │
│                │                        JWT Validation       │
│                │                             │               │
│                ▼                             ▼               │
│         API Request ──────────────────→ API Gateway         │
│         (Bearer Token)                  (Token Verify)       │
│                                              │               │
│                                              ▼               │
│                                        Backend Service       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 VPN Detection (PRD-0002 NFR-2)

**목표 정확도**: 80-90%

**구현 스택**:
1. **MaxMind GeoIP2** - IP 위치 + VPN DB
2. **WebRTC Leak Detection** - 클라이언트
3. **DNS Leak Detection** - 클라이언트
4. **Timezone Mismatch** - 클라이언트 vs IP

### 5.3 Rate Limiting

| Endpoint | Limit | Window |
|----------|:-----:|:------:|
| Auth | 10 req | 1 min |
| Content API | 1000 req | 1 min |
| Search | 100 req | 1 min |
| Stream URL | 50 req | 1 min |

---

## 6. Performance Requirements

### 6.1 NFR-1 매핑 (PRD-0002)

| 요구사항 | 목표 | 구현 방안 |
|---------|------|---------|
| 동시접속 50만 | 500K CCU | CDN + Auto-scaling |
| 초기 버퍼링 < 3초 | < 3s | Edge 캐싱, ABR |
| 재버퍼링 < 1% | < 1% | Multi-CDN, QoS |

### 6.2 API 성능 목표

| API | P50 | P95 | P99 |
|-----|:---:|:---:|:---:|
| Auth | 50ms | 100ms | 200ms |
| Content List | 100ms | 200ms | 500ms |
| Stream URL | 50ms | 100ms | 200ms |
| HUD Stats | 100ms | 200ms | 300ms |
| Search | 200ms | 500ms | 1000ms |

### 6.3 Scaling Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    Scaling Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Traffic ──→ CDN (Akamai) ──→ ALB ──→ ECS Fargate          │
│                                         │                    │
│                                         ▼                    │
│                              Auto Scaling Group              │
│                              (CPU/Memory based)              │
│                                         │                    │
│                                         ▼                    │
│                              ┌─────────────────┐             │
│                              │ Service Replicas│             │
│                              │  (2 ~ 50 tasks) │             │
│                              └─────────────────┘             │
│                                         │                    │
│                                         ▼                    │
│                              ┌─────────────────┐             │
│                              │   RDS / Redis   │             │
│                              │  (Read Replicas)│             │
│                              └─────────────────┘             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. DevOps & CI/CD

### 7.1 CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     CI/CD Pipeline                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Developer ──→ GitHub PR ──→ GitHub Actions                 │
│                                   │                          │
│                    ┌──────────────┼──────────────┐           │
│                    │              │              │           │
│                    ▼              ▼              ▼           │
│                 Lint          Test           Build           │
│                    │              │              │           │
│                    └──────────────┼──────────────┘           │
│                                   │                          │
│                                   ▼                          │
│                            PR Approved                       │
│                                   │                          │
│                                   ▼                          │
│                     Merge to main branch                     │
│                                   │                          │
│                    ┌──────────────┼──────────────┐           │
│                    │              │              │           │
│                    ▼              ▼              ▼           │
│                Staging        QA Test      Production        │
│               (Auto)         (Manual)      (Approval)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Infrastructure as Code

| 용도 | 도구 |
|------|------|
| **Infrastructure** | Terraform |
| **Kubernetes** | Helm (if K8s) |
| **Secrets** | AWS Secrets Manager |
| **Configuration** | AWS Parameter Store |

### 7.3 Environments

| 환경 | 용도 | 배포 |
|------|------|------|
| `development` | 개발 | 자동 |
| `staging` | QA 테스트 | PR 머지 시 |
| `production` | 운영 | 수동 승인 |

---

## 8. Cost Estimation

### 8.1 월간 예상 비용 (Y1 기준, 50K MAU)

| 항목 | 예상 비용 | 비고 |
|------|:--------:|------|
| **AWS Infrastructure** | $15,000 | EC2, RDS, S3 |
| **CDN (Akamai)** | $20,000 | 비디오 트래픽 |
| **Supabase** | $2,000 | Pro Plan |
| **DRM (BuyDRM)** | $3,000 | 라이선스 |
| **Monitoring (Datadog)** | $2,000 | APM, Logs |
| **3rd Party** | $3,000 | MaxMind, Sentry |
| **Total** | **$45,000/월** | |

### 8.2 확장 시 비용 (Y3, 300K MAU)

| 항목 | 예상 비용 |
|------|:--------:|
| AWS Infrastructure | $50,000 |
| CDN | $80,000 |
| Supabase | $5,000 |
| DRM | $10,000 |
| Monitoring | $5,000 |
| 3rd Party | $5,000 |
| **Total** | **$155,000/월** |

---

## Consequences

### Positive

1. **검증된 기술 스택**: Next.js, Fastify, PostgreSQL은 대규모 서비스에서 검증됨
2. **확장성**: 서버리스 + CDN으로 50만 동시접속 대응
3. **개발 효율**: TypeScript 전체 적용으로 타입 안전성
4. **비용 최적화**: 서버 믹싱으로 트래픽 비용 절감

### Negative

1. **복잡도**: 5개 플랫폼 지원으로 유지보수 부담
2. **협업사 의존**: CDN, DRM 등 외부 서비스 의존
3. **초기 비용**: 인프라 초기 구축 비용

### Risks

1. **CDN 장애**: Multi-CDN 페일오버 필수
2. **DRM 호환성**: 플랫폼별 테스트 필수
3. **성능 미달**: 부하 테스트 조기 실시

---

## Alternatives Considered

### GraphQL vs REST

| 옵션 | 선택 | 근거 |
|------|:----:|------|
| REST Only | - | 복잡한 쿼리 비효율 |
| GraphQL Only | - | 캐싱 어려움 |
| **REST + GraphQL** | ✓ | 용도에 맞게 혼용 |

### Self-hosted vs Managed DB

| 옵션 | 선택 | 근거 |
|------|:----:|------|
| Self-hosted PostgreSQL | - | 운영 부담 |
| **Supabase** | ✓ | 관리형, RLS, Edge Functions |
| AWS RDS | - | 비용 대비 기능 부족 |

---

## References

- [PRD-0002 WSOPTV OTT Platform MVP](../prds/PRD-0002-wsoptv-ott-platform-mvp.md)
- [PRD-0005 RFP](../prds/PRD-0005-wsoptv-ott-rfp.md)
- [PRD-0006 Advanced Mode](../prds/PRD-0006-advanced-mode.md)
- [ADR-0002 Database Schema](ADR-0002-database-schema-design.md)
- [STRAT-0008 Timeline Roadmap](../strategies/STRAT-0008-timeline-roadmap.md)
- [STRAT-0011 GGPass Integration](../strategies/STRAT-0011-ggpass-integration-spec.md)

---

*Created: 2026-01-19*
*Last Updated: 2026-01-19*

> **Note**: 이 문서는 권장 아키텍처입니다. 협업사 RFP 응답에 따라 일부 기술 스택이 변경될 수 있습니다.
