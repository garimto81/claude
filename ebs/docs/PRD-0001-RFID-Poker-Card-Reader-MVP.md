# PRD-0001: EBS - RFID 포커 카드 리더 MVP

**Version**: 1.0.0
**작성일**: 2026-01-22
**작성자**: EBS Team
**상태**: Draft

---

## 1. 개요

### 1.1 배경

PokerGFX Server 분석 결과, 포커 방송용 RFID 카드 인식 시스템의 핵심 기능을 파악했습니다. 이를 기반으로 **자체 RFID 포커 카드 인식 MVP**를 구축하여 기본적인 카드 인식 및 앱 표시 기능을 구현합니다.

### 1.2 목표

| 목표 | 설명 |
|------|------|
| **Primary** | RFID 모듈로 포커 카드 인식 |
| **Secondary** | 인식된 카드를 실시간으로 앱에 표시 |
| **Stretch** | 2장 이상 동시 인식 (홀카드) |

### 1.3 성공 지표

| 지표 | 목표값 |
|------|--------|
| 카드 인식 정확도 | 99%+ |
| 인식 → 표시 지연시간 | < 100ms |
| 동시 인식 카드 수 | 2장 (홀카드) |
| 인식 거리 | 3~5cm |

---

## 2. 기능 요구사항

### 2.1 핵심 기능 (MVP)

```
┌─────────────────────────────────────────────────────────────┐
│                     MVP 핵심 기능                           │
├─────────────────────────────────────────────────────────────┤
│  F1. 단일 카드 인식                                         │
│      └── RFID 태그 → 카드 정보 (Suit + Rank)               │
│                                                             │
│  F2. 카드 정보 표시                                         │
│      └── 인식된 카드를 UI에 실시간 렌더링                   │
│                                                             │
│  F3. 연결 상태 모니터링                                     │
│      └── RFID 리더 연결 상태 표시                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 기능 상세

#### F1. 카드 인식

| 항목 | 요구사항 |
|------|----------|
| 입력 | RFID 태그 UID |
| 출력 | 카드 정보 (suit, rank) |
| 매핑 | UID → Card DB 조회 |
| 응답 시간 | < 50ms |

**카드 데이터 구조**:
```json
{
  "uid": "04:A2:B3:C4:D5:E6:F7",
  "card": {
    "suit": "spades",
    "rank": "A",
    "display": "A♠"
  },
  "timestamp": "2026-01-22T10:30:00Z"
}
```

#### F2. 카드 표시

| 항목 | 요구사항 |
|------|----------|
| 렌더링 | 카드 이미지 또는 텍스트 |
| 위치 | 플레이어 슬롯별 표시 |
| 애니메이션 | 카드 등장 효과 (선택) |
| 히스토리 | 최근 인식된 카드 목록 |

#### F3. 연결 상태

| 상태 | 표시 |
|------|------|
| 연결됨 | 녹색 아이콘 |
| 연결 끊김 | 빨간색 아이콘 + 경고 |
| 인식 중 | 파란색 깜빡임 |

### 2.3 확장 기능 (Post-MVP)

| 기능 | 우선순위 | 설명 |
|------|----------|------|
| 다중 카드 인식 | P1 | 2장 홀카드 동시 인식 |
| 보안 딜레이 | P2 | 방송용 시간 지연 |
| 핸드 히스토리 | P2 | 게임별 핸드 기록 |
| OBS 연동 | P3 | 방송 오버레이 |

---

## 3. 하드웨어 설계

### 3.1 시스템 아키텍처

```
┌───────────────────────────────────────────────────────────────────┐
│                        System Architecture                        │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│   │  RFID Card   │ ───▶ │  RFID Reader │ ───▶ │    MCU       │  │
│   │  (NFC Tag)   │      │  (MFRC522)   │      │  (ESP32)     │  │
│   └──────────────┘      └──────────────┘      └──────────────┘  │
│                                                      │           │
│                                                      │ USB/WiFi  │
│                                                      ▼           │
│                                               ┌──────────────┐  │
│                                               │   Host PC    │  │
│                                               │  (App/Web)   │  │
│                                               └──────────────┘  │
│                                                      │           │
│                                                      ▼           │
│                                               ┌──────────────┐  │
│                                               │   Display    │  │
│                                               │  (Browser)   │  │
│                                               └──────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### 3.2 하드웨어 구성품

#### 필수 부품 (MVP)

| 부품 | 모델 | 수량 | 가격 (KRW) | 구매처 |
|------|------|------|------------|--------|
| **RFID 리더** | MFRC522 | 1 | ₩8,000~15,000 | Coupang, 디바이스마트 |
| **마이크로컨트롤러** | ESP32 DevKit | 1 | ₩15,000~25,000 | Coupang, 아이씨뱅크 |
| **RFID 포커 카드** | 13.56MHz NFC | 1덱 (54장) | ₩50,000~100,000 | RFIDup, 스마트포커 |
| **점퍼 와이어** | M-F, F-F | 10+ | ₩3,000 | 전자부품몰 |
| **브레드보드** | 400핀 | 1 | ₩3,000 | 전자부품몰 |
| **USB 케이블** | Micro USB | 1 | ₩3,000 | - |

**예상 총 비용**: ₩82,000 ~ ₩149,000

#### 권장 부품 (확장)

| 부품 | 모델 | 용도 | 가격 (KRW) |
|------|------|------|------------|
| 추가 RFID 리더 | MFRC522 x2 | 다중 위치 인식 | ₩16,000 |
| 3D 프린트 케이스 | 커스텀 | 테이블 내장 | ₩20,000 |
| 안테나 확장 | 외장 안테나 | 인식 거리 확장 | ₩10,000 |

### 3.3 배선도

```
┌─────────────────────────────────────────────────────────────┐
│                    ESP32 ←→ MFRC522 연결                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ESP32 Pin          MFRC522 Pin        기능               │
│   ─────────          ──────────         ────               │
│   3.3V        ────▶  VCC               전원 (3.3V)         │
│   GND         ────▶  GND               접지                │
│   GPIO 5      ────▶  SDA (SS)          Slave Select       │
│   GPIO 18     ────▶  SCK               SPI Clock          │
│   GPIO 23     ────▶  MOSI              Master Out         │
│   GPIO 19     ────▶  MISO              Master In          │
│   GPIO 4      ────▶  RST               Reset              │
│   (N/C)              IRQ               (사용 안 함)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 RFID 카드 매핑 테이블

52장 표준 덱 + 2장 조커를 UID에 매핑:

```
┌────────────────────────────────────────────────────────────────┐
│                      Card UID Mapping                          │
├────────┬────────┬────────┬────────┬────────┬────────┬────────┤
│  Rank  │ Spades │ Hearts │ Diamonds│ Clubs  │  표기  │ 값     │
├────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│   A    │ UID_01 │ UID_14 │ UID_27 │ UID_40 │  A♠    │  14    │
│   K    │ UID_02 │ UID_15 │ UID_28 │ UID_41 │  K♠    │  13    │
│   Q    │ UID_03 │ UID_16 │ UID_29 │ UID_42 │  Q♠    │  12    │
│   J    │ UID_04 │ UID_17 │ UID_30 │ UID_43 │  J♠    │  11    │
│  10    │ UID_05 │ UID_18 │ UID_31 │ UID_44 │ 10♠    │  10    │
│   9    │ UID_06 │ UID_19 │ UID_32 │ UID_45 │  9♠    │   9    │
│   8    │ UID_07 │ UID_20 │ UID_33 │ UID_46 │  8♠    │   8    │
│   7    │ UID_08 │ UID_21 │ UID_34 │ UID_47 │  7♠    │   7    │
│   6    │ UID_09 │ UID_22 │ UID_35 │ UID_48 │  6♠    │   6    │
│   5    │ UID_10 │ UID_23 │ UID_36 │ UID_49 │  5♠    │   5    │
│   4    │ UID_11 │ UID_24 │ UID_37 │ UID_50 │  4♠    │   4    │
│   3    │ UID_12 │ UID_25 │ UID_38 │ UID_51 │  3♠    │   3    │
│   2    │ UID_13 │ UID_26 │ UID_39 │ UID_52 │  2♠    │   2    │
├────────┼────────┴────────┴────────┴────────┼────────┼────────┤
│ Joker  │ UID_53 (Red), UID_54 (Black)      │ JK     │   0    │
└────────┴───────────────────────────────────┴────────┴────────┘
```

---

## 4. 소프트웨어 설계

### 4.1 시스템 구성

```
┌─────────────────────────────────────────────────────────────────┐
│                     Software Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    Presentation Layer                    │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │  Web App    │  │  OBS Plugin │  │  Mobile App │     │  │
│   │  │  (React)    │  │  (Future)   │  │  (Future)   │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              │ WebSocket                        │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                     Server Layer                         │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │  WebSocket  │  │  Card DB    │  │  API Server │     │  │
│   │  │  Server     │  │  (SQLite)   │  │  (FastAPI)  │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              │ Serial (USB)                     │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    Hardware Layer                        │  │
│   │  ┌─────────────┐  ┌─────────────┐                       │  │
│   │  │   ESP32     │──│  MFRC522    │                       │  │
│   │  │  Firmware   │  │  RFID       │                       │  │
│   │  └─────────────┘  └─────────────┘                       │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 기술 스택

| 계층 | 기술 | 선택 이유 |
|------|------|----------|
| **Firmware** | Arduino (C++) | ESP32 표준, MFRC522 라이브러리 지원 |
| **Server** | Python + FastAPI | 빠른 개발, WebSocket 지원 |
| **Database** | SQLite | 경량, 설정 불필요 |
| **Frontend** | React + TypeScript | 컴포넌트 기반, 실시간 UI |
| **Communication** | WebSocket | 양방향 실시간 통신 |
| **Serial** | pyserial | Python-ESP32 통신 |

### 4.3 데이터 흐름

```
┌────────────────────────────────────────────────────────────────┐
│                        Data Flow                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. 카드 감지                                                  │
│     RFID Tag ──▶ MFRC522 ──▶ ESP32                            │
│                                                                │
│  2. UID 전송                                                   │
│     ESP32 ──[Serial JSON]──▶ Python Server                    │
│     {"type": "card_read", "uid": "04:A2:B3:C4"}               │
│                                                                │
│  3. 카드 조회                                                  │
│     Server ──▶ SQLite DB ──▶ Card Info                        │
│     SELECT * FROM cards WHERE uid = ?                          │
│                                                                │
│  4. 클라이언트 전송                                            │
│     Server ──[WebSocket]──▶ Web App                           │
│     {"type": "card_detected", "card": {"suit": "spades", ...}}│
│                                                                │
│  5. UI 렌더링                                                  │
│     Web App ──▶ React State ──▶ Card Component                │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 4.4 API 설계

#### REST API

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/status` | 시스템 상태 조회 |
| GET | `/api/cards` | 전체 카드 목록 |
| GET | `/api/cards/{uid}` | 특정 카드 조회 |
| POST | `/api/cards/register` | 새 카드 등록 |
| GET | `/api/history` | 인식 히스토리 |

#### WebSocket Events

| Event | Direction | Payload |
|-------|-----------|---------|
| `connect` | C→S | `{client_id}` |
| `card_detected` | S→C | `{uid, card, timestamp}` |
| `card_removed` | S→C | `{uid, timestamp}` |
| `reader_status` | S→C | `{connected, port}` |
| `error` | S→C | `{code, message}` |

### 4.5 데이터베이스 스키마

```sql
-- cards: 카드 마스터 테이블
CREATE TABLE cards (
    id INTEGER PRIMARY KEY,
    uid TEXT UNIQUE NOT NULL,
    suit TEXT NOT NULL CHECK (suit IN ('spades', 'hearts', 'diamonds', 'clubs', 'joker')),
    rank TEXT NOT NULL,
    display TEXT NOT NULL,
    value INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- card_reads: 인식 로그
CREATE TABLE card_reads (
    id INTEGER PRIMARY KEY,
    card_id INTEGER REFERENCES cards(id),
    reader_id TEXT,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- readers: RFID 리더 관리
CREATE TABLE readers (
    id TEXT PRIMARY KEY,
    name TEXT,
    port TEXT,
    position TEXT,
    is_active BOOLEAN DEFAULT TRUE
);
```

---

## 5. 구현 로드맵

### 5.1 Phase 구성

```
┌─────────────────────────────────────────────────────────────────┐
│                     Implementation Phases                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: 하드웨어 검증 (Week 1)                               │
│  ├── ESP32 + MFRC522 연결 테스트                               │
│  ├── 단일 카드 UID 읽기                                        │
│  └── Serial 통신 확인                                          │
│                                                                 │
│  Phase 2: 기본 소프트웨어 (Week 2)                             │
│  ├── Python 시리얼 리더 구현                                   │
│  ├── SQLite DB 및 카드 매핑                                    │
│  └── 기본 CLI 테스트                                           │
│                                                                 │
│  Phase 3: 웹 인터페이스 (Week 3)                               │
│  ├── FastAPI 서버 구축                                         │
│  ├── WebSocket 실시간 통신                                     │
│  └── React 기본 UI                                             │
│                                                                 │
│  Phase 4: 통합 및 테스트 (Week 4)                              │
│  ├── E2E 테스트                                                │
│  ├── 성능 최적화                                               │
│  └── 문서화                                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 상세 일정

| Phase | 작업 | 산출물 | 예상 소요 |
|-------|------|--------|----------|
| **P1** | 하드웨어 셋업 | 동작하는 RFID 리더 | 3-5일 |
| **P1** | 펌웨어 개발 | ESP32 코드 | 2-3일 |
| **P2** | Serial 통신 | Python 리더 | 2-3일 |
| **P2** | DB 설계 | 스키마 + 초기 데이터 | 1-2일 |
| **P3** | API 서버 | FastAPI 서버 | 3-4일 |
| **P3** | WebSocket | 실시간 통신 | 2-3일 |
| **P3** | 프론트엔드 | React 앱 | 3-5일 |
| **P4** | 테스트 | 테스트 스위트 | 2-3일 |
| **P4** | 문서화 | 사용자 가이드 | 1-2일 |

**총 예상 기간**: 4-5주

### 5.3 마일스톤

| 마일스톤 | 완료 조건 | 목표일 |
|----------|----------|--------|
| **M1** | RFID 카드 UID 읽기 성공 | Week 1 |
| **M2** | 카드 → DB 조회 → CLI 출력 | Week 2 |
| **M3** | 웹 브라우저에 카드 표시 | Week 3 |
| **M4** | MVP 완료 (안정적 동작) | Week 4 |

---

## 6. 비용 산정

### 6.1 하드웨어 비용

| 항목 | 단가 | 수량 | 소계 |
|------|------|------|------|
| ESP32 DevKit | ₩20,000 | 1 | ₩20,000 |
| MFRC522 모듈 | ₩10,000 | 1 | ₩10,000 |
| RFID 포커 카드 (1덱) | ₩80,000 | 1 | ₩80,000 |
| 점퍼 와이어 세트 | ₩3,000 | 1 | ₩3,000 |
| 브레드보드 | ₩3,000 | 1 | ₩3,000 |
| USB 케이블 | ₩3,000 | 1 | ₩3,000 |
| **소계** | | | **₩119,000** |

### 6.2 옵션 비용

| 항목 | 비용 | 비고 |
|------|------|------|
| 추가 RFID 리더 (x2) | ₩20,000 | 다중 위치 인식 |
| 3D 프린트 케이스 | ₩20,000 | 외주 또는 자체 |
| 추가 카드 덱 | ₩80,000 | 백업용 |
| 외장 안테나 | ₩10,000 | 인식 거리 확장 |

### 6.3 총 예상 비용

| 구분 | 비용 |
|------|------|
| **MVP 최소** | ₩119,000 |
| **MVP 권장** | ₩150,000 |
| **확장 옵션 포함** | ₩250,000 |

---

## 7. 구매 가이드

### 7.1 국내 구매처

#### ESP32 DevKit

| 판매처 | 가격 | 배송 |
|--------|------|------|
| [Coupang](https://www.coupang.com) | ₩15,000~25,000 | 로켓배송 |
| [디바이스마트](https://www.devicemart.co.kr) | ₩18,000~22,000 | 2-3일 |
| [아이씨뱅크](https://www.icbanq.com) | ₩17,000~20,000 | 2-3일 |
| [엘레파츠](https://www.eleparts.co.kr) | ₩16,000~21,000 | 2-3일 |

#### MFRC522 RFID 모듈

| 판매처 | 가격 | 배송 |
|--------|------|------|
| [Coupang](https://www.coupang.com) | ₩8,000~15,000 | 로켓배송 |
| [디바이스마트](https://www.devicemart.co.kr) | ₩9,000~12,000 | 2-3일 |
| [AliExpress](https://www.aliexpress.com) | ₩3,000~5,000 | 2-4주 |

#### RFID 포커 카드

| 판매처 | 가격 | 특징 |
|--------|------|------|
| [스마트포커](https://sprfid.kr) | 견적 문의 | 국내 전문업체 |
| [RFIDup.com](https://www.rfidup.com) | $30~50/덱 | 해외 도매 |
| [RFID Card](https://www.rfidcard.com) | $25~40/덱 | 커스텀 가능 |
| [TP-RFID](https://www.tp-rfid.com) | $20~35/덱 | 대량 할인 |

### 7.2 권장 구매 순서

```
1. 먼저 구매 (국내, 빠른 배송)
   ├── ESP32 DevKit (Coupang)
   ├── MFRC522 모듈 (Coupang/디바이스마트)
   └── 기본 부품 (점퍼, 브레드보드)

2. 테스트 후 구매 (해외, 1-2주)
   └── RFID 포커 카드 (RFIDup 또는 스마트포커)

3. 선택적 구매
   ├── 추가 리더 모듈
   └── 케이스/안테나
```

### 7.3 카드 구매 시 주의사항

| 항목 | 확인 사항 |
|------|----------|
| **주파수** | 13.56MHz (HF) 확인 필수 |
| **칩 타입** | MIFARE Classic 또는 NTAG213/215 |
| **카드 크기** | 표준 포커 사이즈 (63 x 88mm) |
| **내구성** | PVC 코팅, 방수 여부 |
| **최소 주문** | 1덱(54장) 또는 대량 |

---

## 8. 위험 요소 및 대응

### 8.1 기술적 위험

| 위험 | 영향 | 대응 |
|------|------|------|
| 카드 인식 불량 | 높음 | 안테나 조정, 거리 최적화 |
| 다중 카드 간섭 | 중간 | Anti-collision 알고리즘 |
| Serial 통신 지연 | 낮음 | 버퍼링, 비동기 처리 |
| WiFi 불안정 | 중간 | USB 유선 모드 대안 |

### 8.2 비기술적 위험

| 위험 | 영향 | 대응 |
|------|------|------|
| 카드 배송 지연 | 중간 | 테스트용 일반 NFC 태그 사용 |
| 부품 불량 | 낮음 | 여분 구매 |
| 호환성 문제 | 중간 | 사전 스펙 확인 |

---

## 9. 참고 자료

### 9.1 학습 리소스

| 리소스 | URL | 용도 |
|--------|-----|------|
| ESP32 MFRC522 튜토리얼 | [Random Nerd Tutorials](https://randomnerdtutorials.com/esp32-mfrc522-rfid-reader-arduino/) | 하드웨어 셋업 |
| Arduino RFID 라이브러리 | [GitHub - miguelbalboa/rfid](https://github.com/miguelbalboa/rfid) | 펌웨어 |
| FastAPI WebSocket | [FastAPI Docs](https://fastapi.tiangolo.com/advanced/websockets/) | 서버 개발 |
| React WebSocket | [react-use-websocket](https://github.com/robtaussig/react-use-websocket) | 프론트엔드 |

### 9.2 관련 문서

| 문서 | 경로 |
|------|------|
| PokerGFX 분석 | `docs/REPORT-PokerGFX-Server-Analysis.md` |
| 하드웨어 설계 | `docs/DESIGN-RFID-Hardware.md` (작성 예정) |
| API 명세 | `docs/API-RFID-Reader.md` (작성 예정) |

---

## 10. 승인

| 역할 | 이름 | 날짜 | 서명 |
|------|------|------|------|
| 작성자 | - | 2026-01-22 | |
| 검토자 | - | | |
| 승인자 | - | | |

---

## 부록 A: ESP32 펌웨어 샘플 코드

```cpp
#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>

#define SS_PIN  5
#define RST_PIN 4

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("{\"type\":\"ready\",\"message\":\"RFID Reader initialized\"}");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }

  // UID를 문자열로 변환
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (i > 0) uid += ":";
    if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  // JSON 출력
  StaticJsonDocument<200> doc;
  doc["type"] = "card_read";
  doc["uid"] = uid;
  doc["timestamp"] = millis();

  serializeJson(doc, Serial);
  Serial.println();

  mfrc522.PICC_HaltA();
  delay(500);  // 중복 방지
}
```

---

## 부록 B: Python Serial Reader 샘플

```python
import serial
import json
import asyncio
from typing import Callable

class RFIDReader:
    def __init__(self, port: str = "COM3", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.callbacks = []

    def connect(self):
        self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
        print(f"Connected to {self.port}")

    def on_card_read(self, callback: Callable):
        self.callbacks.append(callback)

    async def read_loop(self):
        while True:
            if self.serial and self.serial.in_waiting:
                line = self.serial.readline().decode('utf-8').strip()
                try:
                    data = json.loads(line)
                    if data.get("type") == "card_read":
                        for callback in self.callbacks:
                            await callback(data)
                except json.JSONDecodeError:
                    pass
            await asyncio.sleep(0.01)

# 사용 예
async def handle_card(data):
    print(f"Card detected: {data['uid']}")

reader = RFIDReader(port="COM3")
reader.connect()
reader.on_card_read(handle_card)
asyncio.run(reader.read_loop())
```

---

**문서 끝**
