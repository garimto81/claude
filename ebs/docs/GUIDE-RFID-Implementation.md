# EBS - RFID 포커 카드 리더 구현 가이드

**Version**: 1.0.0
**작성일**: 2026-01-22
**관련 문서**:
- PRD-0001-EBS-RFID-Poker-Card-Reader-MVP.md
- DESIGN-RFID-Hardware.md (EBS 하드웨어 설계)
- ARCHITECTURE-RFID-Software.md (EBS 소프트웨어 아키텍처)

---

## 1. 빠른 시작 가이드

### 1.1 최소 MVP 구성

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Minimal MVP Setup                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   필요 부품 (총 ₩120,000~150,000):                                     │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  □ ESP32 DevKit V1          ₩20,000   (Coupang)                │  │
│   │  □ MFRC522 RFID 모듈        ₩10,000   (Coupang)                │  │
│   │  □ 점퍼 와이어 (M-F) 10개   ₩3,000    (전자부품몰)             │  │
│   │  □ 브레드보드 400핀         ₩3,000    (전자부품몰)             │  │
│   │  □ USB Micro 케이블         ₩3,000    (다이소)                 │  │
│   │  □ RFID 포커 카드 1덱       ₩80,000   (RFIDup/스마트포커)      │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   소프트웨어:                                                           │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  □ Arduino IDE 2.0+ (무료)                                      │  │
│   │  □ Python 3.11+ (무료)                                          │  │
│   │  □ Node.js 18+ (무료)                                           │  │
│   │  □ VS Code (무료)                                               │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 구매 링크 요약

| 품목 | 국내 구매 | 해외 구매 |
|------|----------|----------|
| **ESP32 DevKit** | [Coupang 검색](https://www.coupang.com/np/search?q=ESP32) | [Amazon](https://www.amazon.com/s?k=esp32+devkit) |
| **MFRC522** | [Coupang 검색](https://www.coupang.com/np/search?q=MFRC522) | [AliExpress](https://www.aliexpress.com/w/wholesale-mfrc522.html) |
| **RFID 포커 카드** | [스마트포커](https://sprfid.kr/) | [RFIDup](https://www.rfidup.com/) |
| **부품 세트** | [디바이스마트](https://www.devicemart.co.kr/) | [SparkFun](https://www.sparkfun.com/) |

---

## 2. 구현 로드맵

### 2.1 Phase 개요

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Implementation Roadmap                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Week 1: 하드웨어 검증                                                 │
│   ═══════════════════                                                   │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  Day 1-2: 부품 도착 및 환경 설정                                │  │
│   │           └── Arduino IDE 설치, ESP32 드라이버 설치             │  │
│   │                                                                  │  │
│   │  Day 3-4: ESP32 + MFRC522 연결                                  │  │
│   │           └── SPI 배선, 테스트 코드 업로드                       │  │
│   │                                                                  │  │
│   │  Day 5-7: 카드 인식 테스트                                      │  │
│   │           └── UID 읽기, Serial Monitor 확인                      │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│   ▼ Milestone: RFID 카드 UID 읽기 성공                                 │
│                                                                         │
│   Week 2: 기본 소프트웨어                                               │
│   ═══════════════════════                                               │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  Day 1-2: Python Serial 리더 구현                               │  │
│   │           └── pyserial, JSON 파싱                                │  │
│   │                                                                  │  │
│   │  Day 3-4: SQLite DB 설정                                        │  │
│   │           └── 스키마 생성, 카드 매핑 데이터                      │  │
│   │                                                                  │  │
│   │  Day 5-7: CLI 테스트 도구                                       │  │
│   │           └── 카드 등록, 조회, 로그                              │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│   ▼ Milestone: 카드 → DB 조회 → CLI 출력 성공                         │
│                                                                         │
│   Week 3: 웹 인터페이스                                                 │
│   ════════════════════                                                  │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  Day 1-2: FastAPI 서버 구축                                     │  │
│   │           └── REST API, WebSocket 엔드포인트                     │  │
│   │                                                                  │  │
│   │  Day 3-4: React 프론트엔드                                      │  │
│   │           └── 카드 컴포넌트, WebSocket 연결                      │  │
│   │                                                                  │  │
│   │  Day 5-7: UI 완성                                               │  │
│   │           └── 스타일링, 히스토리, 연결 상태                      │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│   ▼ Milestone: 웹 브라우저에 카드 실시간 표시                          │
│                                                                         │
│   Week 4: 통합 및 안정화                                                │
│   ══════════════════════                                                │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  Day 1-3: E2E 테스트                                            │  │
│   │           └── 전체 흐름 테스트, 엣지 케이스                      │  │
│   │                                                                  │  │
│   │  Day 4-5: 성능 최적화                                           │  │
│   │           └── 지연 시간 개선, 안정성 향상                        │  │
│   │                                                                  │  │
│   │  Day 6-7: 문서화                                                │  │
│   │           └── 사용자 가이드, 트러블슈팅                          │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│   ▼ Milestone: MVP 완료                                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 상세 체크리스트

#### Phase 1: 하드웨어 검증

```markdown
## Week 1 체크리스트

### Day 1-2: 환경 설정
- [ ] Arduino IDE 2.0+ 설치
- [ ] ESP32 보드 매니저 추가
      URL: https://dl.espressif.com/dl/package_esp32_index.json
- [ ] MFRC522 라이브러리 설치 (Library Manager)
- [ ] ArduinoJson 라이브러리 설치
- [ ] USB 드라이버 설치 (CP2102 또는 CH340)
- [ ] ESP32 보드 인식 확인 (COM 포트)

### Day 3-4: 하드웨어 조립
- [ ] ESP32를 브레드보드에 장착
- [ ] MFRC522 핀헤더 납땜 (필요시)
- [ ] 배선 연결:
      - [ ] VCC → 3.3V
      - [ ] GND → GND
      - [ ] SDA → GPIO5
      - [ ] SCK → GPIO18
      - [ ] MOSI → GPIO23
      - [ ] MISO → GPIO19
      - [ ] RST → GPIO4
- [ ] 배선 검증 (멀티미터)

### Day 5-7: 카드 인식 테스트
- [ ] DumpInfo 예제 업로드
- [ ] Serial Monitor 115200 baud 설정
- [ ] RFID 카드/태그 인식 테스트
- [ ] UID 출력 확인
- [ ] 인식 거리 테스트 (0-5cm)
- [ ] 안정성 테스트 (100회 연속)
```

#### Phase 2: 기본 소프트웨어

```markdown
## Week 2 체크리스트

### Day 1-2: Python Serial
- [ ] Python 3.11+ 설치
- [ ] 가상환경 생성: python -m venv venv
- [ ] pyserial 설치: pip install pyserial
- [ ] Serial 연결 테스트 코드 작성
- [ ] JSON 파싱 구현
- [ ] 카드 이벤트 핸들링

### Day 3-4: SQLite 데이터베이스
- [ ] 스키마 설계 확정
- [ ] cards 테이블 생성
- [ ] card_reads 테이블 생성
- [ ] 52장 카드 초기 데이터 생성
- [ ] UID 매핑 스크립트

### Day 5-7: CLI 도구
- [ ] 카드 등록 기능
- [ ] UID 조회 기능
- [ ] 인식 로그 출력
- [ ] 미등록 카드 알림
- [ ] 기본 통계 (읽기 횟수 등)
```

#### Phase 3: 웹 인터페이스

```markdown
## Week 3 체크리스트

### Day 1-2: FastAPI 서버
- [ ] FastAPI 프로젝트 구조 생성
- [ ] REST API 엔드포인트 구현
      - [ ] GET /api/status
      - [ ] GET /api/cards
      - [ ] GET /api/cards/{uid}
      - [ ] POST /api/cards/register
- [ ] WebSocket 핸들러 구현
- [ ] Serial 서비스 통합
- [ ] CORS 설정

### Day 3-4: React 프론트엔드
- [ ] Vite + React 프로젝트 생성
- [ ] TypeScript 설정
- [ ] WebSocket 훅 구현
- [ ] Card 컴포넌트 제작
- [ ] 기본 레이아웃

### Day 5-7: UI 완성
- [ ] 카드 애니메이션
- [ ] 연결 상태 표시
- [ ] 히스토리 목록
- [ ] 반응형 디자인
- [ ] 에러 핸들링
```

#### Phase 4: 통합 및 안정화

```markdown
## Week 4 체크리스트

### Day 1-3: E2E 테스트
- [ ] 전체 흐름 테스트 시나리오
- [ ] 연결 끊김 복구 테스트
- [ ] 다중 카드 연속 인식
- [ ] 장시간 안정성 테스트
- [ ] 엣지 케이스 처리

### Day 4-5: 최적화
- [ ] 인식 지연 시간 측정 (< 100ms 목표)
- [ ] WebSocket 재연결 로직
- [ ] 메모리 누수 확인
- [ ] 에러 로깅 개선

### Day 6-7: 문서화
- [ ] 설치 가이드
- [ ] 사용자 매뉴얼
- [ ] 트러블슈팅 가이드
- [ ] API 문서
```

---

## 3. 단계별 상세 가이드

### 3.1 Step 1: Arduino IDE 설정

```
1. Arduino IDE 다운로드 및 설치
   https://www.arduino.cc/en/software

2. ESP32 보드 매니저 추가
   File → Preferences → Additional Board Manager URLs:
   https://dl.espressif.com/dl/package_esp32_index.json

3. ESP32 보드 설치
   Tools → Board → Boards Manager → "ESP32" 검색 → 설치

4. 라이브러리 설치
   Sketch → Include Library → Manage Libraries:
   - "MFRC522" by GithubCommunity 설치
   - "ArduinoJson" by Benoit Blanchon 설치

5. 보드 선택
   Tools → Board → ESP32 Arduino → "ESP32 Dev Module"

6. 포트 선택
   Tools → Port → COM3 (또는 해당 포트)
```

### 3.2 Step 2: 펌웨어 업로드

```cpp
// 테스트 코드: rfid_test.ino

#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN  5
#define RST_PIN 4

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("RFID Reader Ready");
  Serial.println("Place card on reader...");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent()) {
    delay(50);
    return;
  }

  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  Serial.print("Card UID: ");
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (i > 0) Serial.print(":");
    if (mfrc522.uid.uidByte[i] < 0x10) Serial.print("0");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.println();

  mfrc522.PICC_HaltA();
  delay(500);
}
```

**업로드 방법**:
1. 코드 복사하여 Arduino IDE에 붙여넣기
2. Ctrl+U 또는 Upload 버튼 클릭
3. "Done uploading" 메시지 확인
4. Tools → Serial Monitor 열기 (115200 baud)
5. 카드를 리더에 올려 UID 출력 확인

### 3.3 Step 3: Python 서버 설정

```bash
# 프로젝트 디렉토리 생성
mkdir rfid-poker-reader
cd rfid-poker-reader

# Python 가상환경
python -m venv venv
.\venv\Scripts\activate  # Windows

# 패키지 설치
pip install fastapi uvicorn pyserial websockets pydantic

# 디렉토리 구조 생성
mkdir -p server/app/{models,services,api,db}
mkdir -p frontend/src/{components,hooks,types}
mkdir data
```

### 3.4 Step 4: 카드 매핑 데이터

```python
# server/app/db/init_cards.py

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "cards.db"

# 52장 카드 + 2장 조커 초기 데이터
CARDS = [
    # Spades (♠)
    ("UID_01", "spades", "A"),
    ("UID_02", "spades", "K"),
    ("UID_03", "spades", "Q"),
    # ... 나머지 카드
]

def init_cards():
    conn = sqlite3.connect(str(DB_PATH))

    # 기존 데이터 삭제
    conn.execute("DELETE FROM cards")

    # 카드 삽입
    for uid, suit, rank in CARDS:
        display = f"{rank}{'♠♥♦♣'['shdc'.index(suit[0])]}"
        value = {"A":14,"K":13,"Q":12,"J":11}.get(rank, int(rank) if rank.isdigit() else 0)

        conn.execute(
            "INSERT INTO cards (uid, suit, rank, display, value) VALUES (?, ?, ?, ?, ?)",
            (uid, suit, rank, display, value)
        )

    conn.commit()
    conn.close()
    print(f"Initialized {len(CARDS)} cards")

if __name__ == "__main__":
    init_cards()
```

**참고**: 실제 UID는 RFID 카드 구매 후 개별적으로 매핑해야 합니다.

### 3.5 Step 5: 카드 UID 매핑 도구

```python
# tools/map_cards.py
# 실제 RFID 카드의 UID를 매핑하는 도구

import serial
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "cards.db"

SUITS = ["spades", "hearts", "diamonds", "clubs"]
RANKS = ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def map_card(uid: str, suit: str, rank: str):
    """카드 UID 매핑"""
    conn = get_db()

    # 기존 매핑 확인
    existing = conn.execute("SELECT * FROM cards WHERE uid = ?", (uid,)).fetchone()
    if existing:
        print(f"UID {uid} already mapped to {existing['display']}")
        return False

    # 새 매핑 추가
    symbols = {"spades": "♠", "hearts": "♥", "diamonds": "♦", "clubs": "♣"}
    display = f"{rank}{symbols[suit]}"
    values = {"A":14,"K":13,"Q":12,"J":11,"10":10,"9":9,"8":8,"7":7,"6":6,"5":5,"4":4,"3":3,"2":2}
    value = values.get(rank, 0)

    conn.execute(
        "INSERT INTO cards (uid, suit, rank, display, value) VALUES (?, ?, ?, ?, ?)",
        (uid, suit, rank, display, value)
    )
    conn.commit()
    print(f"Mapped: {uid} → {display}")
    return True

def interactive_mapping(port: str = "COM3"):
    """대화형 카드 매핑"""
    ser = serial.Serial(port, 115200, timeout=1)
    print("=== RFID Card Mapping Tool ===")
    print("Place cards on reader to map them.")
    print("Press Ctrl+C to exit.\n")

    card_index = 0
    total_cards = len(SUITS) * len(RANKS)

    try:
        while card_index < total_cards:
            suit = SUITS[card_index // len(RANKS)]
            rank = RANKS[card_index % len(RANKS)]

            print(f"\nWaiting for card: {rank} of {suit}")

            while True:
                if ser.in_waiting:
                    line = ser.readline().decode('utf-8').strip()
                    try:
                        data = json.loads(line)
                        if data.get("type") == "card_read":
                            uid = data.get("uid")
                            if map_card(uid, suit, rank):
                                card_index += 1
                            break
                    except json.JSONDecodeError:
                        pass

    except KeyboardInterrupt:
        print(f"\n\nMapping stopped. {card_index}/{total_cards} cards mapped.")

    ser.close()

if __name__ == "__main__":
    import sys
    port = sys.argv[1] if len(sys.argv) > 1 else "COM3"
    interactive_mapping(port)
```

---

## 4. 비용 상세 분석

### 4.1 MVP 비용

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MVP Cost Breakdown                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   필수 부품                                                             │
│   ═════════                                                             │
│   ESP32 DevKit V1                    ₩20,000                           │
│   MFRC522 RFID 모듈                  ₩10,000                           │
│   점퍼 와이어 (M-F) 10개             ₩3,000                            │
│   브레드보드 400핀                   ₩3,000                            │
│   USB Micro 케이블                   ₩3,000                            │
│   ─────────────────────────────────────────                            │
│   부품 소계                          ₩39,000                           │
│                                                                         │
│   RFID 포커 카드                                                        │
│   ═════════════                                                         │
│   옵션 A: 스마트포커 (국내)          ₩100,000~150,000 (견적 필요)      │
│   옵션 B: RFIDup (해외)              $30~50 ≈ ₩45,000~75,000           │
│   옵션 C: TP-RFID (해외 대량)        $20~35 ≈ ₩30,000~50,000           │
│   ─────────────────────────────────────────                            │
│   카드 예상 비용                     ₩50,000~150,000                   │
│                                                                         │
│   ═════════════════════════════════════════════════════════════════    │
│   MVP 총 예상 비용                   ₩89,000 ~ ₩189,000               │
│   ═════════════════════════════════════════════════════════════════    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 확장 비용

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Extended Setup Cost                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   다중 리더 구성 (6인 테이블)                                           │
│   ═══════════════════════════                                           │
│   추가 MFRC522 모듈 x6               ₩60,000                           │
│   추가 점퍼 와이어                   ₩10,000                           │
│   ESP32 (더 많은 GPIO)               ₩25,000                           │
│   외부 3.3V 전원                     ₩10,000                           │
│   ─────────────────────────────────────────                            │
│   다중 리더 소계                     ₩105,000                          │
│                                                                         │
│   테이블 내장 옵션                                                      │
│   ════════════════                                                      │
│   3D 프린트 케이스 x7                ₩70,000                           │
│   페라이트 차폐 시트                 ₩20,000                           │
│   케이블 정리 부품                   ₩10,000                           │
│   ─────────────────────────────────────────                            │
│   내장 옵션 소계                     ₩100,000                          │
│                                                                         │
│   추가 카드 덱                                                          │
│   ═══════════════                                                       │
│   백업 덱 x2                         ₩100,000~200,000                  │
│                                                                         │
│   ═════════════════════════════════════════════════════════════════    │
│   확장 총 예상 비용                  ₩305,000 ~ ₩405,000              │
│   ═════════════════════════════════════════════════════════════════    │
│                                                                         │
│   전체 (MVP + 확장)                  ₩394,000 ~ ₩594,000              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.3 비용 비교 (vs 상용 솔루션)

| 구분 | 자체 구축 MVP | 자체 구축 확장 | 상용 솔루션 |
|------|--------------|---------------|-------------|
| **초기 비용** | ₩100,000~200,000 | ₩400,000~600,000 | ₩5,000,000+ |
| **리더 1개** | ₩30,000 | ₩10,000 (대량) | ₩500,000+ |
| **카드 1덱** | ₩50,000~100,000 | ₩30,000 (대량) | ₩100,000+ |
| **소프트웨어** | 무료 (오픈소스) | 무료 | 라이센스 |
| **유지보수** | 자체 | 자체 | 연간 계약 |
| **커스터마이징** | 자유 | 자유 | 제한적 |

---

## 5. 트러블슈팅 가이드

### 5.1 하드웨어 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| ESP32 인식 안됨 | 드라이버 미설치 | CP2102/CH340 드라이버 설치 |
| 업로드 실패 | 잘못된 포트 | Tools → Port에서 올바른 COM 선택 |
| RFID 초기화 실패 | SPI 배선 오류 | 핀 연결 재확인, 특히 SS/RST |
| 카드 인식 안됨 | 전원 부족 | 3.3V 확인, USB 포트 변경 |
| 간헐적 인식 | 접촉 불량 | 점퍼 와이어 교체, 납땜 확인 |
| 짧은 인식 거리 | 금속 간섭 | 리더 위치 조정, 금속 제거 |

### 5.2 소프트웨어 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| Serial 연결 실패 | 포트 사용 중 | Arduino Serial Monitor 닫기 |
| JSON 파싱 오류 | 불완전한 데이터 | 버퍼 비우기, 줄바꿈 확인 |
| WebSocket 연결 끊김 | 서버 오류 | 로그 확인, 재시작 |
| 카드 미조회 | UID 미등록 | 카드 매핑 실행 |
| DB 오류 | 스키마 불일치 | DB 초기화 재실행 |

### 5.3 디버깅 명령어

```bash
# ESP32 시리얼 모니터 (터미널)
screen /dev/ttyUSB0 115200  # Linux/Mac
# Windows: Arduino IDE Serial Monitor 사용

# Python 시리얼 테스트
python -c "import serial; s=serial.Serial('COM3',115200); print(s.readline())"

# 서버 로그 확인
uvicorn app.main:app --reload --log-level debug

# WebSocket 테스트
websocat ws://localhost:8000/ws
```

---

## 6. 다음 단계 (Post-MVP)

### 6.1 확장 기능 로드맵

```
Phase 2: 다중 리더 (Week 5-6)
├── 7개 리더 동시 연결
├── 포지션별 카드 표시
└── 테이블 레이아웃 UI

Phase 3: 방송 연동 (Week 7-8)
├── OBS 오버레이 개발
├── 보안 딜레이 구현
└── 방송 모드 UI

Phase 4: 고급 기능 (Week 9-10)
├── 핸드 분석
├── 팟 계산
└── 통계 대시보드
```

### 6.2 참고 자료

| 리소스 | 링크 |
|--------|------|
| ESP32 공식 문서 | https://docs.espressif.com/projects/esp-idf/ |
| MFRC522 라이브러리 | https://github.com/miguelbalboa/rfid |
| FastAPI 문서 | https://fastapi.tiangolo.com/ |
| React 문서 | https://react.dev/ |
| 포커 핸드 계산 | https://github.com/alexfmpe/poker |

---

## 7. 문서 색인

| 문서 | 용도 |
|------|------|
| **PRD-0001-EBS-RFID-Poker-Card-Reader-MVP.md** | EBS 제품 요구사항 |
| **DESIGN-RFID-Hardware.md** | EBS 하드웨어 설계 상세 |
| **ARCHITECTURE-RFID-Software.md** | EBS 소프트웨어 아키텍처 |
| **GUIDE-RFID-Implementation.md** | EBS 구현 가이드 (본 문서) |
| **REPORT-PokerGFX-Server-Analysis.md** | PokerGFX 분석 참고 |

---

**문서 끝**
