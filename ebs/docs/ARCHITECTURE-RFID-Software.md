# EBS - RFID 포커 카드 리더 소프트웨어 아키텍처

**Version**: 1.0.0
**작성일**: 2026-01-22
**관련 PRD**: PRD-0001-EBS-RFID-Poker-Card-Reader-MVP

---

## 1. 아키텍처 개요

### 1.1 시스템 레이어

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Software Architecture Overview                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Layer 4: Presentation (UI)                                            │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │  │
│   │  │  Web App    │  │  OBS Plugin │  │  Mobile App (Future)    │ │  │
│   │  │  (React)    │  │  (Future)   │  │                         │ │  │
│   │  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘ │  │
│   └─────────┼────────────────┼──────────────────────┼───────────────┘  │
│             │                │                      │                   │
│             └────────────────┼──────────────────────┘                   │
│                              │ WebSocket                                │
│                              ▼                                          │
│   Layer 3: Application Server                                           │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  ┌─────────────────────────────────────────────────────────────┐│  │
│   │  │                    FastAPI Server                           ││  │
│   │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││  │
│   │  │  │  REST API   │  │  WebSocket  │  │  Serial Manager     │ ││  │
│   │  │  │  /api/*     │  │  Handler    │  │  (pyserial)         │ ││  │
│   │  │  └─────────────┘  └─────────────┘  └─────────────────────┘ ││  │
│   │  └─────────────────────────────────────────────────────────────┘│  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              │ Serial (USB)                             │
│                              ▼                                          │
│   Layer 2: Data Layer                                                   │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │  │
│   │  │  SQLite DB  │  │  Card Cache │  │  Event Queue            │ │  │
│   │  │  (Storage)  │  │  (Memory)   │  │  (asyncio)              │ │  │
│   │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              │ Serial JSON                              │
│                              ▼                                          │
│   Layer 1: Firmware (ESP32)                                             │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │  │
│   │  │  SPI Driver │  │  JSON       │  │  RFID Reader            │ │  │
│   │  │             │  │  Serializer │  │  (MFRC522 Lib)          │ │  │
│   │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 기술 스택

| 레이어 | 기술 | 버전 | 역할 |
|--------|------|------|------|
| **Firmware** | Arduino (C++) | ESP32 Core 2.0+ | RFID 읽기, Serial 전송 |
| **Server** | Python + FastAPI | 3.11+, 0.100+ | API, WebSocket, Serial |
| **Database** | SQLite | 3.x | 카드 매핑, 로그 |
| **Frontend** | React + TypeScript | 18+, 5.0+ | 실시간 UI |
| **Communication** | WebSocket + JSON | - | 양방향 통신 |

---

## 2. Firmware 설계 (ESP32)

### 2.1 디렉토리 구조

```
firmware/
├── rfid_reader/
│   ├── rfid_reader.ino        # 메인 스케치
│   ├── config.h               # 핀 설정, 상수
│   ├── rfid_handler.cpp       # RFID 처리 로직
│   ├── rfid_handler.h
│   ├── serial_protocol.cpp    # JSON 직렬화
│   └── serial_protocol.h
├── libraries/
│   └── MFRC522/               # RFID 라이브러리
└── platformio.ini             # PlatformIO 설정 (선택)
```

### 2.2 핵심 코드

#### config.h
```cpp
#ifndef CONFIG_H
#define CONFIG_H

// Pin Definitions
#define SS_PIN      5
#define RST_PIN     4
#define SCK_PIN     18
#define MOSI_PIN    23
#define MISO_PIN    19

// Serial Configuration
#define SERIAL_BAUD 115200

// Timing
#define READ_DELAY_MS   500     // 중복 읽기 방지
#define DEBOUNCE_MS     100     // 디바운스 시간

// Multi-reader support (확장용)
#define MAX_READERS     7
#define READER_PINS     {5, 15, 16, 17, 21, 22, 25}

#endif
```

#### rfid_reader.ino (메인)
```cpp
#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>
#include "config.h"

MFRC522 mfrc522(SS_PIN, RST_PIN);
String lastUID = "";
unsigned long lastReadTime = 0;

void setup() {
    Serial.begin(SERIAL_BAUD);
    SPI.begin();
    mfrc522.PCD_Init();

    // 시작 메시지 전송
    sendEvent("ready", "RFID Reader initialized");
}

void loop() {
    // 새 카드 감지
    if (!mfrc522.PICC_IsNewCardPresent()) {
        delay(50);
        return;
    }

    if (!mfrc522.PICC_ReadCardSerial()) {
        return;
    }

    // UID 추출
    String uid = getUID();

    // 중복 읽기 필터링
    if (uid == lastUID && (millis() - lastReadTime) < READ_DELAY_MS) {
        mfrc522.PICC_HaltA();
        return;
    }

    // 카드 읽기 이벤트 전송
    sendCardRead(uid);

    lastUID = uid;
    lastReadTime = millis();

    mfrc522.PICC_HaltA();
}

String getUID() {
    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        if (i > 0) uid += ":";
        if (mfrc522.uid.uidByte[i] < 0x10) uid += "0";
        uid += String(mfrc522.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    return uid;
}

void sendCardRead(String uid) {
    StaticJsonDocument<256> doc;
    doc["type"] = "card_read";
    doc["uid"] = uid;
    doc["reader_id"] = 0;
    doc["timestamp"] = millis();

    serializeJson(doc, Serial);
    Serial.println();
}

void sendEvent(const char* type, const char* message) {
    StaticJsonDocument<256> doc;
    doc["type"] = type;
    doc["message"] = message;
    doc["timestamp"] = millis();

    serializeJson(doc, Serial);
    Serial.println();
}
```

### 2.3 시리얼 프로토콜

| 방향 | 메시지 타입 | 페이로드 |
|------|-------------|----------|
| ESP32 → PC | `ready` | `{type, message, timestamp}` |
| ESP32 → PC | `card_read` | `{type, uid, reader_id, timestamp}` |
| ESP32 → PC | `card_removed` | `{type, uid, reader_id, timestamp}` |
| ESP32 → PC | `error` | `{type, code, message, timestamp}` |
| PC → ESP32 | `ping` | `{type}` |
| PC → ESP32 | `config` | `{type, read_delay, ...}` |

---

## 3. Server 설계 (Python + FastAPI)

### 3.1 디렉토리 구조

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 설정
│   ├── models/
│   │   ├── __init__.py
│   │   ├── card.py             # Card 모델
│   │   ├── reader.py           # Reader 모델
│   │   └── event.py            # Event 모델
│   ├── services/
│   │   ├── __init__.py
│   │   ├── serial_service.py   # Serial 통신
│   │   ├── card_service.py     # 카드 조회/등록
│   │   └── websocket_service.py# WS 브로드캐스트
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # REST 라우트
│   │   └── websocket.py        # WS 핸들러
│   └── db/
│       ├── __init__.py
│       ├── database.py         # SQLite 연결
│       └── init_data.py        # 초기 카드 데이터
├── tests/
│   ├── test_serial.py
│   ├── test_api.py
│   └── test_websocket.py
├── requirements.txt
└── run.py                      # 실행 스크립트
```

### 3.2 핵심 코드

#### app/main.py
```python
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.config import settings
from app.api.routes import router
from app.api.websocket import websocket_manager
from app.services.serial_service import serial_service
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    asyncio.create_task(serial_service.start())
    yield
    # Shutdown
    await serial_service.stop()

app = FastAPI(
    title="RFID Poker Card Reader",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 클라이언트 메시지 처리
    except Exception:
        websocket_manager.disconnect(websocket)
```

#### app/services/serial_service.py
```python
import asyncio
import json
from typing import Optional, Callable
import serial
import serial.tools.list_ports

from app.config import settings
from app.services.card_service import card_service
from app.services.websocket_service import websocket_manager

class SerialService:
    def __init__(self):
        self.serial: Optional[serial.Serial] = None
        self.running = False
        self.port = settings.SERIAL_PORT
        self.baudrate = settings.SERIAL_BAUDRATE

    async def start(self):
        """시리얼 연결 시작 및 읽기 루프"""
        self.running = True
        await self._connect()
        await self._read_loop()

    async def stop(self):
        """시리얼 연결 종료"""
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()

    async def _connect(self):
        """시리얼 포트 연결"""
        try:
            # 자동 포트 감지
            if self.port == "auto":
                self.port = self._find_esp32_port()

            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            print(f"Connected to {self.port}")

            # 연결 상태 브로드캐스트
            await websocket_manager.broadcast({
                "type": "reader_status",
                "connected": True,
                "port": self.port
            })
        except Exception as e:
            print(f"Serial connection failed: {e}")
            await websocket_manager.broadcast({
                "type": "reader_status",
                "connected": False,
                "error": str(e)
            })

    def _find_esp32_port(self) -> str:
        """ESP32 포트 자동 감지"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "CP210" in port.description or "CH340" in port.description:
                return port.device
        raise Exception("ESP32 not found")

    async def _read_loop(self):
        """비동기 시리얼 읽기 루프"""
        while self.running:
            if self.serial and self.serial.is_open and self.serial.in_waiting:
                try:
                    line = self.serial.readline().decode('utf-8').strip()
                    if line:
                        data = json.loads(line)
                        await self._handle_message(data)
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"Serial read error: {e}")
            await asyncio.sleep(0.01)

    async def _handle_message(self, data: dict):
        """시리얼 메시지 처리"""
        msg_type = data.get("type")

        if msg_type == "card_read":
            uid = data.get("uid")
            # 카드 정보 조회
            card = await card_service.get_card_by_uid(uid)

            if card:
                # 카드 감지 이벤트 브로드캐스트
                await websocket_manager.broadcast({
                    "type": "card_detected",
                    "uid": uid,
                    "card": card.dict(),
                    "timestamp": data.get("timestamp")
                })
            else:
                # 미등록 카드
                await websocket_manager.broadcast({
                    "type": "unknown_card",
                    "uid": uid,
                    "timestamp": data.get("timestamp")
                })

        elif msg_type == "ready":
            await websocket_manager.broadcast({
                "type": "reader_ready",
                "message": data.get("message")
            })

serial_service = SerialService()
```

#### app/services/card_service.py
```python
from typing import Optional, List
from app.models.card import Card
from app.db.database import get_db

class CardService:
    async def get_card_by_uid(self, uid: str) -> Optional[Card]:
        """UID로 카드 조회"""
        db = get_db()
        cursor = db.execute(
            "SELECT * FROM cards WHERE uid = ?",
            (uid,)
        )
        row = cursor.fetchone()
        if row:
            return Card(**dict(row))
        return None

    async def get_all_cards(self) -> List[Card]:
        """전체 카드 목록"""
        db = get_db()
        cursor = db.execute("SELECT * FROM cards ORDER BY id")
        return [Card(**dict(row)) for row in cursor.fetchall()]

    async def register_card(self, uid: str, suit: str, rank: str) -> Card:
        """새 카드 등록"""
        display = f"{rank}{self._get_suit_symbol(suit)}"
        value = self._get_card_value(rank)

        db = get_db()
        cursor = db.execute(
            """INSERT INTO cards (uid, suit, rank, display, value)
               VALUES (?, ?, ?, ?, ?)""",
            (uid, suit, rank, display, value)
        )
        db.commit()

        return Card(
            id=cursor.lastrowid,
            uid=uid,
            suit=suit,
            rank=rank,
            display=display,
            value=value
        )

    def _get_suit_symbol(self, suit: str) -> str:
        symbols = {
            "spades": "♠",
            "hearts": "♥",
            "diamonds": "♦",
            "clubs": "♣",
            "joker": "★"
        }
        return symbols.get(suit, "?")

    def _get_card_value(self, rank: str) -> int:
        values = {
            "A": 14, "K": 13, "Q": 12, "J": 11,
            "10": 10, "9": 9, "8": 8, "7": 7,
            "6": 6, "5": 5, "4": 4, "3": 3, "2": 2,
            "JK": 0
        }
        return values.get(rank, 0)

card_service = CardService()
```

#### app/api/routes.py
```python
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.card import Card, CardCreate
from app.services.card_service import card_service
from app.services.serial_service import serial_service

router = APIRouter()

@router.get("/status")
async def get_status():
    """시스템 상태"""
    return {
        "status": "running",
        "serial_connected": serial_service.serial is not None
                           and serial_service.serial.is_open,
        "serial_port": serial_service.port
    }

@router.get("/cards", response_model=List[Card])
async def get_cards():
    """전체 카드 목록"""
    return await card_service.get_all_cards()

@router.get("/cards/{uid}", response_model=Card)
async def get_card(uid: str):
    """UID로 카드 조회"""
    card = await card_service.get_card_by_uid(uid)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.post("/cards/register", response_model=Card)
async def register_card(card_data: CardCreate):
    """새 카드 등록"""
    return await card_service.register_card(
        uid=card_data.uid,
        suit=card_data.suit,
        rank=card_data.rank
    )

@router.get("/history")
async def get_history(limit: int = 100):
    """카드 인식 히스토리"""
    db = get_db()
    cursor = db.execute(
        """SELECT cr.*, c.display
           FROM card_reads cr
           JOIN cards c ON cr.card_id = c.id
           ORDER BY cr.read_at DESC
           LIMIT ?""",
        (limit,)
    )
    return [dict(row) for row in cursor.fetchall()]
```

### 3.3 데이터베이스 스키마

#### app/db/database.py
```python
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "cards.db"

def get_db():
    """SQLite 연결 반환"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """데이터베이스 초기화"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = get_db()

    # 테이블 생성
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT UNIQUE NOT NULL,
            suit TEXT NOT NULL CHECK (suit IN ('spades', 'hearts', 'diamonds', 'clubs', 'joker')),
            rank TEXT NOT NULL,
            display TEXT NOT NULL,
            value INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS card_reads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER REFERENCES cards(id),
            reader_id TEXT DEFAULT '0',
            read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS readers (
            id TEXT PRIMARY KEY,
            name TEXT,
            port TEXT,
            position TEXT,
            is_active BOOLEAN DEFAULT TRUE
        );

        CREATE INDEX IF NOT EXISTS idx_cards_uid ON cards(uid);
        CREATE INDEX IF NOT EXISTS idx_card_reads_time ON card_reads(read_at);
    """)

    conn.commit()
    conn.close()
```

---

## 4. Frontend 설계 (React)

### 4.1 디렉토리 구조

```
frontend/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/
│   │   ├── Card/
│   │   │   ├── Card.tsx
│   │   │   ├── Card.css
│   │   │   └── index.ts
│   │   ├── CardSlot/
│   │   │   ├── CardSlot.tsx
│   │   │   └── index.ts
│   │   ├── ConnectionStatus/
│   │   │   └── ConnectionStatus.tsx
│   │   └── History/
│   │       └── History.tsx
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   └── useCards.ts
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.ts
│   └── styles/
│       └── global.css
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### 4.2 핵심 코드

#### src/types/index.ts
```typescript
export interface Card {
  id: number;
  uid: string;
  suit: 'spades' | 'hearts' | 'diamonds' | 'clubs' | 'joker';
  rank: string;
  display: string;
  value: number;
}

export interface CardEvent {
  type: 'card_detected' | 'card_removed' | 'unknown_card';
  uid: string;
  card?: Card;
  timestamp: number;
}

export interface ReaderStatus {
  type: 'reader_status' | 'reader_ready';
  connected: boolean;
  port?: string;
  message?: string;
}

export type WSMessage = CardEvent | ReaderStatus;
```

#### src/hooks/useWebSocket.ts
```typescript
import { useEffect, useRef, useState, useCallback } from 'react';
import { WSMessage, Card } from '../types';

const WS_URL = 'ws://localhost:8000/ws';

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastCard, setLastCard] = useState<Card | null>(null);
  const [history, setHistory] = useState<Card[]>([]);
  const [readerConnected, setReaderConnected] = useState(false);

  const connect = useCallback(() => {
    ws.current = new WebSocket(WS_URL);

    ws.current.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const data: WSMessage = JSON.parse(event.data);

      switch (data.type) {
        case 'card_detected':
          if (data.card) {
            setLastCard(data.card);
            setHistory(prev => [data.card!, ...prev.slice(0, 19)]);
          }
          break;

        case 'reader_status':
          setReaderConnected(data.connected);
          break;

        case 'reader_ready':
          setReaderConnected(true);
          break;
      }
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      setReaderConnected(false);
      // 재연결 시도
      setTimeout(connect, 3000);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      ws.current?.close();
    };
  }, [connect]);

  return {
    isConnected,
    readerConnected,
    lastCard,
    history,
    clearLastCard: () => setLastCard(null),
  };
}
```

#### src/components/Card/Card.tsx
```typescript
import React from 'react';
import { Card as CardType } from '../../types';
import './Card.css';

interface CardProps {
  card: CardType;
  size?: 'small' | 'medium' | 'large';
  animate?: boolean;
}

const suitColors: Record<string, string> = {
  spades: '#000000',
  clubs: '#000000',
  hearts: '#FF0000',
  diamonds: '#FF0000',
  joker: '#FFD700',
};

const suitSymbols: Record<string, string> = {
  spades: '♠',
  clubs: '♣',
  hearts: '♥',
  diamonds: '♦',
  joker: '★',
};

export const Card: React.FC<CardProps> = ({
  card,
  size = 'medium',
  animate = false
}) => {
  const color = suitColors[card.suit];
  const symbol = suitSymbols[card.suit];

  return (
    <div
      className={`card card--${size} ${animate ? 'card--animate' : ''}`}
      style={{ color }}
    >
      <div className="card__corner card__corner--top">
        <span className="card__rank">{card.rank}</span>
        <span className="card__suit">{symbol}</span>
      </div>

      <div className="card__center">
        <span className="card__symbol">{symbol}</span>
      </div>

      <div className="card__corner card__corner--bottom">
        <span className="card__rank">{card.rank}</span>
        <span className="card__suit">{symbol}</span>
      </div>
    </div>
  );
};
```

#### src/components/Card/Card.css
```css
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card--small {
  width: 60px;
  height: 84px;
  font-size: 12px;
}

.card--medium {
  width: 100px;
  height: 140px;
  font-size: 18px;
}

.card--large {
  width: 150px;
  height: 210px;
  font-size: 24px;
}

.card__corner {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1;
}

.card__corner--top {
  top: 8px;
  left: 8px;
}

.card__corner--bottom {
  bottom: 8px;
  right: 8px;
  transform: rotate(180deg);
}

.card__rank {
  font-weight: bold;
}

.card__suit {
  font-size: 0.8em;
}

.card__center {
  font-size: 3em;
}

.card--animate {
  animation: cardAppear 0.3s ease-out;
}

@keyframes cardAppear {
  from {
    transform: scale(0.5) rotateY(90deg);
    opacity: 0;
  }
  to {
    transform: scale(1) rotateY(0);
    opacity: 1;
  }
}
```

#### src/App.tsx
```typescript
import React from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { Card } from './components/Card/Card';
import { ConnectionStatus } from './components/ConnectionStatus/ConnectionStatus';
import './styles/global.css';

function App() {
  const {
    isConnected,
    readerConnected,
    lastCard,
    history
  } = useWebSocket();

  return (
    <div className="app">
      <header className="header">
        <h1>RFID Poker Card Reader</h1>
        <ConnectionStatus
          wsConnected={isConnected}
          readerConnected={readerConnected}
        />
      </header>

      <main className="main">
        <section className="current-card">
          <h2>Current Card</h2>
          <div className="card-display">
            {lastCard ? (
              <Card card={lastCard} size="large" animate />
            ) : (
              <div className="card-placeholder">
                Place card on reader
              </div>
            )}
          </div>
        </section>

        <section className="history">
          <h2>History</h2>
          <div className="history-grid">
            {history.map((card, index) => (
              <Card key={`${card.uid}-${index}`} card={card} size="small" />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
```

---

## 5. 데이터 흐름

### 5.1 카드 인식 시퀀스

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Card Detection Sequence                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  User          Card           MFRC522        ESP32          Server      │
│   │             │               │              │               │        │
│   │  Place card │               │              │               │        │
│   │─────────────▶               │              │               │        │
│   │             │  RF Signal    │              │               │        │
│   │             │◀──────────────│              │               │        │
│   │             │  Modulated    │              │               │        │
│   │             │──────────────▶│              │               │        │
│   │             │               │  UID Data    │               │        │
│   │             │               │─────────────▶│               │        │
│   │             │               │              │  JSON Serial  │        │
│   │             │               │              │──────────────▶│        │
│   │             │               │              │               │        │
│   │             │               │              │  DB Query     │        │
│   │             │               │              │               │────┐   │
│   │             │               │              │               │    │   │
│   │             │               │              │               │◀───┘   │
│   │             │               │              │               │        │
│   │             │               │              │   WebSocket   │        │
│   │◀────────────────────────────────────────────────────────────        │
│   │             │               │              │  Broadcast    │        │
│   │   Display   │               │              │               │        │
│   │             │               │              │               │        │
│                                                                         │
│  Timeline: ~50-100ms total                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 메시지 형식

#### ESP32 → Server
```json
{
  "type": "card_read",
  "uid": "04:A2:B3:C4:D5:E6:F7",
  "reader_id": 0,
  "timestamp": 123456789
}
```

#### Server → Client (WebSocket)
```json
{
  "type": "card_detected",
  "uid": "04:A2:B3:C4:D5:E6:F7",
  "card": {
    "id": 1,
    "uid": "04:A2:B3:C4:D5:E6:F7",
    "suit": "spades",
    "rank": "A",
    "display": "A♠",
    "value": 14
  },
  "timestamp": 123456789
}
```

---

## 6. 설치 및 실행

### 6.1 개발 환경 설정

```bash
# 1. Python 환경
cd server
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Node.js 환경
cd frontend
npm install

# 3. Arduino IDE
# - ESP32 보드 매니저 추가
# - MFRC522 라이브러리 설치
# - ArduinoJson 라이브러리 설치
```

### 6.2 실행 순서

```bash
# 1. ESP32 펌웨어 업로드
# Arduino IDE에서 rfid_reader.ino 업로드

# 2. Server 실행
cd server
python run.py
# http://localhost:8000

# 3. Frontend 실행
cd frontend
npm run dev
# http://localhost:5173
```

### 6.3 requirements.txt (Server)
```
fastapi>=0.100.0
uvicorn>=0.23.0
pyserial>=3.5
websockets>=11.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### 6.4 package.json (Frontend)
```json
{
  "name": "rfid-poker-reader",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^4.4.0"
  }
}
```

---

## 7. 확장 가이드

### 7.1 다중 리더 지원

```python
# server/app/services/serial_service.py (확장)

class MultiReaderService:
    def __init__(self):
        self.readers: Dict[str, serial.Serial] = {}

    async def add_reader(self, reader_id: str, port: str):
        """리더 추가"""
        self.readers[reader_id] = serial.Serial(port, 115200)

    async def remove_reader(self, reader_id: str):
        """리더 제거"""
        if reader_id in self.readers:
            self.readers[reader_id].close()
            del self.readers[reader_id]
```

### 7.2 OBS 오버레이 연동

```typescript
// OBS Browser Source URL 제공
// http://localhost:5173/overlay

// frontend/src/pages/Overlay.tsx
export const Overlay: React.FC = () => {
  const { lastCard } = useWebSocket();

  return (
    <div className="overlay" style={{ background: 'transparent' }}>
      {lastCard && <Card card={lastCard} size="large" animate />}
    </div>
  );
};
```

### 7.3 보안 딜레이 구현

```python
# server/app/services/delay_service.py

import asyncio
from collections import deque
from datetime import datetime, timedelta

class DelayService:
    def __init__(self, delay_seconds: int = 30):
        self.delay = timedelta(seconds=delay_seconds)
        self.queue: deque = deque()

    async def add_event(self, event: dict):
        """이벤트를 딜레이 큐에 추가"""
        event['scheduled_at'] = datetime.now() + self.delay
        self.queue.append(event)

    async def process_queue(self):
        """딜레이된 이벤트 처리"""
        now = datetime.now()
        while self.queue and self.queue[0]['scheduled_at'] <= now:
            event = self.queue.popleft()
            await websocket_manager.broadcast(event)
        await asyncio.sleep(0.1)
```

---

## 8. 테스트 전략

### 8.1 단위 테스트

```python
# tests/test_card_service.py
import pytest
from app.services.card_service import card_service

@pytest.mark.asyncio
async def test_get_card_by_uid():
    # Given
    uid = "04:A2:B3:C4:D5:E6:F7"

    # When
    card = await card_service.get_card_by_uid(uid)

    # Then
    assert card is not None
    assert card.uid == uid
    assert card.suit in ['spades', 'hearts', 'diamonds', 'clubs']

@pytest.mark.asyncio
async def test_unknown_uid_returns_none():
    # Given
    uid = "FF:FF:FF:FF"

    # When
    card = await card_service.get_card_by_uid(uid)

    # Then
    assert card is None
```

### 8.2 통합 테스트

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    assert "status" in response.json()

def test_get_cards():
    response = client.get("/api/cards")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

---

**문서 끝**
