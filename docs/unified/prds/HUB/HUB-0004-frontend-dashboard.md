# PRD-0004: WSOP Automation Hub 통합 프론트엔드 대시보드

## 문서 정보

| 항목 | 내용 |
|------|------|
| **PRD ID** | PRD-0004 |
| **제목** | WSOP Automation Hub 통합 프론트엔드 대시보드 |
| **버전** | 1.0.0 |
| **작성일** | 2026-01-06 |
| **수정일** | 2026-01-06 |
| **상태** | Draft |
| **우선순위** | P1 |
| **관련 PRD** | PRD-0001, PRD-0002, PRD-0003 |

---

## Executive Summary

### 배경

automation_hub는 WSOP 방송 자동화의 공유 백엔드로서 3개 프로젝트(feature_table, sub, ae)를 통합합니다. 현재 FastAPI 기반 모니터링 API만 존재하고 **프론트엔드 UI가 전무**하여 운영팀의 실시간 모니터링과 수작업 입력이 불가능합니다.

### 핵심 목표

| # | 목표 | 상세 |
|---|------|------|
| 1 | **페르소나별 대시보드** | 4개 역할별 최적화된 UI |
| 2 | **WebSocket 실시간** | 모든 페르소나에 실시간 업데이트 |
| 3 | **역할 기반 접근 제어** | 페르소나별 권한 분리 |

### 페르소나 정의

| # | 페르소나 | 주요 업무 | 핵심 기능 |
|---|---------|----------|----------|
| 1 | **DB 운영자** | 데이터 입력 및 렌더링 관리 | Hand 수동 입력, 렌더링 작업 선택/관리 |
| 2 | **방송 관리자** | 방송 상황 총괄 | 실시간 방송 모니터링, 방송 핸드 선택 |
| 3 | **연출팀** | 방송 연출 및 플레이어 관리 | 키 플레이어/테이블 관리, 대회 상황 모니터링 |
| 4 | **외부 협력팀** | 방송 소스 전송 | 방송 소스 모니터링, 외부 전송 관리 |

### 기술 스택 결정

- **Framework**: React 18 + TypeScript
- **실시간성**: WebSocket
- **상태 관리**: TanStack Query + Zustand

---

## 1. 문제 정의 & 배경

### 1.1 현재 상황

![현재 아키텍처](/docs/unified/images/hub-0004-current-architecture.png)

> 📎 **HTML 원본**: [prd-0004-current-architecture.html](../../docs/mockups/prd-0004-current-architecture.html)

<details>
<summary>📝 텍스트 다이어그램 (접기/펼치기)</summary>

```
┌─────────────────────────────────────────────────────────────┐
│  automation_feature_table (RFID) ──► Hand                  │
│  automation_sub (CSV) ──────────► Tournament + Render      │
│                                        │                    │
│                                        ▼                    │
│                              PostgreSQL (공유)              │
│                                        │                    │
│  automation_ae (렌더링) ◄──────────────┘                   │
│                                                             │
│  [모니터링 API: GET /stats, /pending, /health]             │
│  [프론트엔드 UI: ❌ 없음]                                   │
└─────────────────────────────────────────────────────────────┘
```

</details>

### 1.2 문제점

| # | 문제 | 영향 | 심각도 |
|---|------|------|--------|
| 1 | 프론트엔드 UI 부재 | JSON API만 제공, 운영팀 모니터링 불가 | 높음 |
| 2 | 수작업 입력 불가 | CSV 누락 시 Manual Hand 입력 경로 없음 | 높음 |
| 3 | 실시간 업데이트 없음 | 새로고침 의존, 긴급 상황 대응 지연 | 중간 |
| 4 | 렌더링 관리 불가 | 실패 작업 재시도, 우선순위 변경 불가 | 중간 |

### 1.3 제약 조건

| 제약 | 내용 |
|------|------|
| 기존 백엔드 유지 | FastAPI + PostgreSQL 구조 변경 최소화 |
| Repository 패턴 활용 | 기존 Repository 메서드 확장 |
| 디자인 표준 준수 | docs/mockups/ 스타일 (진한 파란색 테마) |

---

## 2. 목표 & 성공 지표

### 2.1 핵심 목표

| # | 목표 | 상세 |
|---|------|------|
| 1 | 통합 대시보드 | 4개 페르소나별 최적화된 UI |
| 2 | WebSocket 실시간 | 5초 이내 상태 변경 반영 |
| 3 | 수작업 CRUD | Hand, Tournament, RenderInstruction |

### 2.2 성공 지표

| 지표 | 현재 | 목표 |
|------|------|------|
| UI 화면 수 | 0개 | 12개+ (페르소나당 3개) |
| 실시간 지연 | N/A | < 5초 |
| API 엔드포인트 | 3개 | 25개+ |
| WebSocket 채널 | 0개 | 4개 (tables, events, sources, stats) |

---

## 3. 아키텍처

### 3.1 전체 시스템 구조

![시스템 아키텍처](/docs/unified/images/hub-0004-system-architecture.png)

> 📎 **HTML 원본**: [prd-0004-system-architecture.html](../../docs/mockups/prd-0004-system-architecture.html)

<details>
<summary>📝 텍스트 다이어그램 (접기/펼치기)</summary>

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │
│  │ DB Operator │  │  Broadcast  │  │ Production  │  │External│ │
│  │  Dashboard  │  │   Manager   │  │    Team     │  │Partners│ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └───┬────┘ │
│         └────────────────┼────────────────┼─────────────┘      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │        State Management (TanStack Query + Zustand)       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              API Layer (axios + WebSocket)               │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  REST API    │  │  WebSocket   │  │  Basic Auth  │          │
│  │  /api/v1/*   │  │  /ws         │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Repositories                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL                            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

</details>

### 3.2 프론트엔드 폴더 구조

```
frontend/
├── src/
│   ├── api/                      # API 클라이언트
│   │   ├── client.ts             # axios 인스턴스
│   │   ├── websocket.ts          # WebSocket 클라이언트
│   │   ├── hands.api.ts
│   │   ├── renders.api.ts
│   │   ├── broadcast.api.ts      # 방송 관리 API
│   │   ├── players.api.ts        # 플레이어/테이블 API
│   │   └── transfer.api.ts       # 외부 전송 API
│   ├── components/
│   │   ├── ui/                   # shadcn/ui 컴포넌트
│   │   ├── layout/               # Header, Sidebar, MainLayout
│   │   └── shared/               # StatusBadge, CardDisplay
│   ├── features/
│   │   ├── db-operator/          # DB 운영자 대시보드
│   │   ├── broadcast-manager/    # 방송 관리자 대시보드
│   │   ├── production/           # 연출팀 대시보드
│   │   └── external/             # 외부 협력팀 대시보드
│   ├── hooks/                    # useWebSocket, useAuth
│   ├── stores/                   # Zustand 스토어
│   ├── types/                    # TypeScript 타입
│   └── styles/                   # Tailwind + 테마
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

### 3.3 라우트 구조 (페르소나별)

```
/                           → 페르소나 선택 / 기본 대시보드
/login                      → 로그인 (역할 선택)

# DB 운영자
/db-operator                → DB 운영자 메인
/db-operator/hand-entry     → Hand 수동 입력
/db-operator/renders        → 렌더링 작업 관리
/db-operator/data           → 데이터 조회/수정

# 방송 관리자
/broadcast                  → 방송 관리자 메인
/broadcast/tables           → 테이블별 상태
/broadcast/queue            → 방송 대기열
/broadcast/preview/:id      → 핸드 미리보기

# 연출팀
/production                 → 연출팀 메인
/production/tournament      → 대회 현황
/production/key-players     → 키 플레이어 관리
/production/tables          → 테이블 배치

# 외부 협력팀
/external                   → 외부 협력팀 메인
/external/sources           → 방송 소스 모니터링
/external/outputs           → 렌더링 출력 현황
/external/transfer          → 전송 관리
```

---

## 4. 기능 요구사항 (페르소나별)

### 4.1 DB 운영자 대시보드

> **주요 업무**: 데이터 입력 및 렌더링 관리

![DB 운영자 대시보드](/docs/unified/images/hub-0004-db-operator.png)

> 📎 **HTML 원본**: [prd-0004-db-operator.html](../../docs/mockups/prd-0004-db-operator.html)

<details>
<summary>📝 텍스트 와이어프레임 (접기/펼치기)</summary>

```
┌─────────────────────────────────────────────────────────────┐
│  DB Operator Dashboard                    [실시간 ●]        │
├─────────────────────────────────────────────────────────────┤
│  [Hand 입력]  [렌더링 관리]  [데이터 조회]                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐  ┌─────────────────────────┐   │
│  │ 수작업 Hand 입력 폼      │  │ 렌더링 큐               │   │
│  │ Table: [FT-01 ▼]        │  │ [✓] premium_hand #45    │   │
│  │ Hand#: [____]           │  │ [ ] elimination #44     │   │
│  │ Players: [+ Add]        │  │ [ ] leaderboard #43     │   │
│  │ Community: [Card Grid]  │  │                         │   │
│  │ [Submit Hand]           │  │ [렌더 선택] [우선순위]   │   │
│  └─────────────────────────┘  └─────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 최근 입력 데이터                      [Export CSV]    │   │
│  │ ID | Table | Hand# | Source | Status | Created       │   │
│  │ 45 | FT-01 | 123   | Manual | ✓      | 10:30        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

</details>

| 기능 | 설명 | API |
|------|------|-----|
| **Hand 수동 입력** | 테이블, 핸드번호, 플레이어, 커뮤니티카드 | POST /api/v1/hands |
| **렌더링 작업 선택** | 대기 중인 작업 체크박스 선택 | GET /api/v1/renders/pending |
| **렌더링 실행** | 선택된 작업 일괄 처리 시작 | POST /api/v1/renders/batch-start |
| **우선순위 변경** | 작업 순서 조정 | PATCH /api/v1/renders/{id}/priority |
| **데이터 조회/수정** | 입력된 Hand 검색 및 수정 | GET/PUT /api/v1/hands |

---

### 4.2 방송 관리자 대시보드

> **주요 업무**: 방송 상황 총괄 및 핸드 선택

![방송 관리자 대시보드](/docs/unified/images/hub-0004-broadcast-manager.png)

> 📎 **HTML 원본**: [prd-0004-broadcast-manager.html](../../docs/mockups/prd-0004-broadcast-manager.html)

<details>
<summary>📝 텍스트 와이어프레임 (접기/펼치기)</summary>

```
┌─────────────────────────────────────────────────────────────┐
│  Broadcast Manager                        [LIVE 🔴]         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 현재 방송 상황                                       │    │
│  │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │    │
│  │ │ FT-01   │ │ FT-02   │ │ FT-03   │ │ FT-04   │    │    │
│  │ │ Hand#45 │ │ Hand#67 │ │ Hand#23 │ │ Waiting │    │    │
│  │ │ [LIVE]  │ │ [Ready] │ │ [Ready] │ │ [Idle]  │    │    │
│  │ └─────────┘ └─────────┘ └─────────┘ └─────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────┐  ┌────────────────────────┐   │
│  │ 방송 핸드 선택            │  │ 핸드 미리보기           │   │
│  │ ○ FT-01 Hand#45 ★        │  │ ┌────────────────────┐ │   │
│  │   John: A♠K♠ (Winner)    │  │ │  [Live Preview]    │ │   │
│  │ ○ FT-02 Hand#67          │  │ │  Board: A♠K♥Q♦J♣  │ │   │
│  │   Mike: Q♥Q♦             │  │ │  Pot: $125,000     │ │   │
│  │ [방송 전환] [대기열 추가]  │  │ └────────────────────┘ │   │
│  └──────────────────────────┘  └────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 방송 대기열                                           │   │
│  │ 1. FT-01 Hand#45 (Premium: Full House) [On Air]      │   │
│  │ 2. FT-02 Hand#67 (Standard) [Next]                   │   │
│  │ 3. FT-03 Hand#23 (Standard) [Queued]                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

</details>

| 기능 | 설명 | API |
|------|------|-----|
| **테이블 상태 모니터링** | 모든 테이블의 실시간 핸드 상태 | WebSocket: tables 채널 |
| **방송 핸드 선택** | 다음 방송할 핸드 선택 | POST /api/v1/broadcast/select |
| **방송 대기열 관리** | 대기열 순서 조정 | PUT /api/v1/broadcast/queue |
| **핸드 미리보기** | 선택된 핸드 상세 정보 | GET /api/v1/hands/{id}/preview |
| **방송 전환** | 현재 방송 핸드 변경 | POST /api/v1/broadcast/switch |

---

### 4.3 연출팀 대시보드

> **주요 업무**: 키 플레이어 관리 및 대회 상황 모니터링

![연출팀 대시보드](/docs/unified/images/hub-0004-production-team.png)

> 📎 **HTML 원본**: [prd-0004-production-team.html](../../docs/mockups/prd-0004-production-team.html)

<details>
<summary>📝 텍스트 와이어프레임 (접기/펼치기)</summary>

```
┌─────────────────────────────────────────────────────────────┐
│  Production Team                          [Tournament Live] │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 대회 현황: WSOP 2025 Main Event - Day 3              │   │
│  │ Level 15 | Blinds: 4K/8K/8K | Players: 42/1024       │   │
│  │ Avg Stack: $487,619 | Next Break: 45:00              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────┐  ┌────────────────────────┐   │
│  │ 키 플레이어 관리          │  │ 테이블 배치            │   │
│  │ ★ John Doe (Chip Leader) │  │ ┌────┐ ┌────┐ ┌────┐  │   │
│  │   Table: FT-01, Seat: 3  │  │ │FT-1│ │FT-2│ │FT-3│  │   │
│  │   Stack: $1.2M           │  │ │★★★│ │★☆☆│ │☆☆☆│  │   │
│  │   [Edit] [Track]         │  │ └────┘ └────┘ └────┘  │   │
│  │ ★ Jane Smith (2nd)       │  │                        │   │
│  │   Table: FT-02, Seat: 7  │  │ ★ = Key Player        │   │
│  │ [+ Add Key Player]       │  │ [테이블 재배치]        │   │
│  └──────────────────────────┘  └────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 실시간 이벤트 피드                                    │   │
│  │ 10:45 [ELIM] Mike Brown eliminated (42nd - $15K)     │   │
│  │ 10:42 [CHIP] John Doe wins $250K pot (New CL)        │   │
│  │ 10:38 [HAND] Premium Hand: Royal Flush at FT-01      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

</details>

| 기능 | 설명 | API |
|------|------|-----|
| **대회 현황 모니터링** | 블라인드, 남은 플레이어, 평균 스택 | GET /api/v1/tournaments/active |
| **키 플레이어 관리** | 주요 플레이어 등록/추적 | POST /api/v1/players/key |
| **테이블 배치 관리** | 플레이어 테이블 배치 현황 | GET /api/v1/tables/layout |
| **실시간 이벤트 피드** | 탈락, 칩리더 변경, 프리미엄 핸드 | WebSocket: events 채널 |
| **테이블 재배치** | 테이블 밸런싱 정보 | PUT /api/v1/tables/rebalance |

---

### 4.4 외부 협력팀 대시보드

> **주요 업무**: 방송 소스 모니터링 및 외부 전송

![외부 협력팀 대시보드](/docs/unified/images/hub-0004-external-partners.png)

> 📎 **HTML 원본**: [prd-0004-external-partners.html](../../docs/mockups/prd-0004-external-partners.html)

<details>
<summary>📝 텍스트 와이어프레임 (접기/펼치기)</summary>

```
┌─────────────────────────────────────────────────────────────┐
│  External Partners                        [Sources Active]  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 방송 소스 상태                                        │   │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │   │
│  │ │ Main Feed   │ │ Table Cam   │ │ Player Cam  │      │   │
│  │ │ [● Active]  │ │ [● Active]  │ │ [○ Standby] │      │   │
│  │ │ 1920x1080   │ │ 1920x1080   │ │ 1920x1080   │      │   │
│  │ │ 60fps       │ │ 30fps       │ │ 30fps       │      │   │
│  │ └─────────────┘ └─────────────┘ └─────────────┘      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────┐  ┌────────────────────────┐   │
│  │ 렌더링 출력 현황          │  │ 전송 대상              │   │
│  │ ✓ Leaderboard (Ready)    │  │ ☑ ESPN                 │   │
│  │ ✓ Premium Hand (Ready)   │  │ ☑ PokerGO              │   │
│  │ ○ Elimination (Pending)  │  │ ☐ Social Media         │   │
│  │ [Download All] [Preview] │  │ [전송 시작] [일시정지]  │   │
│  └──────────────────────────┘  └────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 전송 로그                                             │   │
│  │ 10:45 [ESPN] Leaderboard sent successfully           │   │
│  │ 10:42 [PokerGO] Premium Hand sent successfully       │   │
│  │ 10:38 [ERROR] Social Media timeout - retry queued    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

</details>

| 기능 | 설명 | API |
|------|------|-----|
| **방송 소스 모니터링** | 비디오 피드 상태 확인 | GET /api/v1/sources/status |
| **렌더링 출력 현황** | 완료된 렌더링 파일 목록 | GET /api/v1/outputs/ready |
| **전송 대상 관리** | ESPN, PokerGO 등 대상 선택 | GET /api/v1/destinations |
| **전송 실행** | 선택된 파일 외부 전송 | POST /api/v1/transfer/send |
| **전송 로그** | 전송 성공/실패 이력 | GET /api/v1/transfer/logs |

---

### 4.5 공통 컴포넌트

| 컴포넌트 | 기능 | 사용 페르소나 |
|---------|------|--------------|
| **Header** | 로고, 페르소나 전환, 알림 | 전체 |
| **Sidebar** | 네비게이션, 퀵 액션 | 전체 |
| **RealTimeIndicator** | WebSocket 연결 상태 | 전체 |
| **NotificationToast** | 실시간 알림 표시 | 전체 |
| **StatusBadge** | 상태 배지 (Live, Ready, Pending) | 전체 |
| **CardDisplay** | 포커 카드 시각화 | 방송관리자, 연출팀 |

---

## 5. 비기능 요구사항

| 지표 | 요구사항 |
|------|---------|
| **실시간 지연** | WebSocket 메시지 < 5초 |
| **초기 로딩** | LCP < 2초 |
| **브라우저 지원** | Chrome 90+, Firefox 90+, Edge 90+ |
| **반응형** | Desktop (1440px+) 우선, Tablet (768px+) 지원 |

---

## 6. 기술 스택

| 구분 | 기술 | 선택 이유 |
|------|------|----------|
| **Framework** | React 18 + TypeScript | 타입 안전성, 생태계 |
| **Build** | Vite | 빠른 HMR, ESM |
| **Routing** | React Router v6 | 표준 |
| **State (서버)** | TanStack Query v5 | 캐싱, 자동 재검증 |
| **State (클라이언트)** | Zustand | 경량, 간단 |
| **UI** | shadcn/ui + Tailwind CSS | 커스터마이징 |
| **Charts** | Recharts | React 네이티브, SVG |
| **Tables** | TanStack Table v8 | 가상화, 정렬/필터 |
| **Forms** | React Hook Form + Zod | 유효성 검증 |
| **WebSocket** | Native WebSocket | 단순성 |

---

## 7. 구현 로드맵 (페르소나 기반)

### Phase 1: 기반 구축

| # | 작업 | 파일 |
|---|------|------|
| 1 | 프로젝트 초기화 (Vite + React + TS) | frontend/package.json |
| 2 | Tailwind + shadcn/ui 설정 | frontend/tailwind.config.js |
| 3 | React Router 설정 (페르소나별 라우트) | frontend/src/routes.tsx |
| 4 | TanStack Query + Zustand 설정 | frontend/src/main.tsx |
| 5 | 레이아웃 + 페르소나 선택 UI | frontend/src/components/layout/ |

### Phase 2: 백엔드 API 확장

| # | 작업 | 파일 |
|---|------|------|
| 1 | Repository 메서드 확장 | shared/db/repositories.py |
| 2 | Pydantic 스키마 정의 | monitor/schemas.py |
| 3 | REST API 라우터 (hands, renders, broadcast, players, transfer) | monitor/routers/*.py |
| 4 | WebSocket ConnectionManager (채널: tables, events, sources) | monitor/websocket.py |
| 5 | 이벤트 발행기 | monitor/events.py |

### Phase 3: DB 운영자 대시보드

| # | 작업 | 파일 |
|---|------|------|
| 1 | HandForm (수작업 입력) | features/db-operator/HandForm.tsx |
| 2 | CardSelector 컴포넌트 | features/db-operator/CardSelector.tsx |
| 3 | RenderQueue 관리 (선택/우선순위) | features/db-operator/RenderQueue.tsx |
| 4 | 데이터 조회/수정 테이블 | features/db-operator/DataTable.tsx |

### Phase 4: 방송 관리자 대시보드

| # | 작업 | 파일 |
|---|------|------|
| 1 | TableStatusGrid (테이블별 상태) | features/broadcast-manager/TableStatusGrid.tsx |
| 2 | HandSelector (방송 핸드 선택) | features/broadcast-manager/HandSelector.tsx |
| 3 | BroadcastQueue (대기열 관리) | features/broadcast-manager/BroadcastQueue.tsx |
| 4 | HandPreview (실시간 미리보기) | features/broadcast-manager/HandPreview.tsx |

### Phase 5: 연출팀 대시보드

| # | 작업 | 파일 |
|---|------|------|
| 1 | TournamentStatus (대회 현황) | features/production/TournamentStatus.tsx |
| 2 | KeyPlayerManager (키 플레이어 관리) | features/production/KeyPlayerManager.tsx |
| 3 | TableLayout (테이블 배치) | features/production/TableLayout.tsx |
| 4 | EventFeed (실시간 이벤트) | features/production/EventFeed.tsx |

### Phase 6: 외부 협력팀 대시보드

| # | 작업 | 파일 |
|---|------|------|
| 1 | SourceMonitor (방송 소스 상태) | features/external/SourceMonitor.tsx |
| 2 | OutputGallery (렌더링 출력) | features/external/OutputGallery.tsx |
| 3 | DestinationManager (전송 대상) | features/external/DestinationManager.tsx |
| 4 | TransferLogs (전송 로그) | features/external/TransferLogs.tsx |

### 구현 순서 다이어그램

![구현 로드맵](/docs/unified/images/hub-0004-roadmap.png)

> 📎 **HTML 원본**: [prd-0004-roadmap.html](../../docs/mockups/prd-0004-roadmap.html)

<details>
<summary>📝 텍스트 다이어그램 (접기/펼치기)</summary>

```
┌─────────────┐
│  Phase 1    │  기반 구축 (공통)
│  기반 구축   │
└──────┬──────┘
       │
┌──────▼──────┐
│  Phase 2    │  백엔드 API (공통)
│  API 확장    │
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
┌─────────────┐┌─────────────┐┌─────────────┐┌─────────────┐
│  Phase 3    ││  Phase 4    ││  Phase 5    ││  Phase 6    │
│  DB 운영자   ││  방송 관리자 ││  연출팀      ││  외부 협력팀 │
└─────────────┘└─────────────┘└─────────────┘└─────────────┘
       │              │              │              │
       └──────────────┴──────────────┴──────────────┘
                             │
                    ┌────────▼────────┐
                    │  통합 테스트     │
                    │  배포            │
                    └─────────────────┘
```

</details>

---

## 8. 위험 관리

| # | 위험 | 영향 | 심각도 | 대응책 |
|---|------|------|--------|--------|
| 1 | WebSocket 연결 불안정 | 실시간 업데이트 누락 | 중간 | Exponential backoff 재연결 + Polling 폴백 |
| 2 | API 응답 지연 | UX 저하 | 낮음 | 스켈레톤 UI + 로딩 상태 |
| 3 | 대량 데이터 렌더링 | 성능 저하 | 중간 | TanStack Virtual (가상화) |
| 4 | 타입 불일치 | 런타임 에러 | 낮음 | Zod 스키마 검증 |

---

## 9. 성공 기준 (페르소나별)

### 9.1 필수 (MVP) - 각 페르소나별 핵심 기능

**DB 운영자**
- [ ] Hand 수동 입력 폼 동작
- [ ] 렌더링 작업 목록 조회 및 선택

**방송 관리자**
- [ ] 테이블별 실시간 상태 표시
- [ ] 방송 핸드 선택 및 전환

**연출팀**
- [ ] 대회 현황 (블라인드, 남은 플레이어) 표시
- [ ] 키 플레이어 등록/조회

**외부 협력팀**
- [ ] 렌더링 출력 목록 조회
- [ ] 전송 대상 선택 및 전송 실행

**공통**
- [ ] WebSocket 연결 및 실시간 업데이트
- [ ] 페르소나별 라우팅 및 네비게이션

### 9.2 권장 (Full)

- [ ] 모든 페르소나 대시보드 완전 구현
- [ ] 실시간 이벤트 피드 (탈락, 칩리더 변경)
- [ ] 필터링, 페이지네이션
- [ ] 반응형 디자인 (Tablet 지원)
- [ ] 전송 로그 및 히스토리

### 9.3 품질 체크리스트

- [ ] TypeScript strict mode 통과
- [ ] ESLint 에러 0개
- [ ] Lighthouse Performance > 80
- [ ] WebSocket 재연결 (5회 이상)
- [ ] API 에러 핸들링 (Toast 알림)

---

## 10. 참고 문서

### 시각화 자료

| 다이어그램 | 이미지 | HTML 원본 |
|-----------|--------|-----------|
| 현재 아키텍처 | [PNG](/docs/unified/images/hub-0004-current-architecture.png) | [HTML](../../docs/mockups/prd-0004-current-architecture.html) |
| 시스템 아키텍처 | [PNG](/docs/unified/images/hub-0004-system-architecture.png) | [HTML](../../docs/mockups/prd-0004-system-architecture.html) |
| DB 운영자 대시보드 | [PNG](/docs/unified/images/hub-0004-db-operator.png) | [HTML](../../docs/mockups/prd-0004-db-operator.html) |
| 방송 관리자 대시보드 | [PNG](/docs/unified/images/hub-0004-broadcast-manager.png) | [HTML](../../docs/mockups/prd-0004-broadcast-manager.html) |
| 연출팀 대시보드 | [PNG](/docs/unified/images/hub-0004-production-team.png) | [HTML](../../docs/mockups/prd-0004-production-team.html) |
| 외부 협력팀 대시보드 | [PNG](/docs/unified/images/hub-0004-external-partners.png) | [HTML](../../docs/mockups/prd-0004-external-partners.html) |
| 구현 로드맵 | [PNG](/docs/unified/images/hub-0004-roadmap.png) | [HTML](../../docs/mockups/prd-0004-roadmap.html) |

### 핵심 파일 (수정/생성 대상)

| 파일 | 작업 |
|------|------|
| `monitor/main.py` | REST API + WebSocket 확장 |
| `shared/db/repositories.py` | CRUD 메서드 확장 |
| `monitor/schemas.py` | Pydantic 스키마 (신규) |
| `monitor/websocket.py` | ConnectionManager (신규) |
| `frontend/` | React 프로젝트 (신규) |

### 내부 문서

- `tasks/prds/PRD-0001-automation-hub-v2.md` - 백엔드 아키텍처
- `tasks/prds/PRD-0002-conflict-monitoring.md` - 충돌 모니터링
- `tasks/prds/PRD-0003-model-unification.md` - 모델 통합
- `docs/mockups/prd-0001-*.html` - 디자인 표준

### 디자인 토큰

```css
:root {
  --bg-gradient: linear-gradient(135deg, #1a1a2e, #16213e);
  --color-primary: #4a69bd;
  --color-secondary: #6c5ce7;
  --status-pending: #fdcb6e;
  --status-processing: #a29bfe;
  --status-completed: #00b894;
  --status-failed: #ff7675;
}
```

---

**작성**: 2026-01-06
**검토**: -
**승인**: -

