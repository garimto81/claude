# PRD-0000: GGM-CSVd Core System

**Version**: 1.2.0
**Date**: 2026-01-22
**Status**: Active
**Author**: Claude Code

---

## 1. Executive Summary

### 1.1 Product Name
**GGM-CSVd** (GGM CSV Daemon)

### 1.2 One-Liner
Google Sheets 데이터를 실시간으로 로컬 CSV 파일에 동기화하는 경량 HTTP 서버

### 1.3 Problem Statement

포커 방송 그래픽 시스템에서:
- Google Sheets에 입력된 플레이어 데이터를 After Effects/OBS가 읽을 수 있는 CSV로 변환 필요
- 실시간 업데이트 (핸드 변경 시 즉시 반영)
- Hero(좌측)/Villain(우측) 분리 저장 필요
- 10개 테이블 × 2좌석 = 20개 슬롯 관리

### 1.4 Solution

```
Google Sheets → Apps Script WebApp → GGM-CSVd → Local CSV Files → AE/OBS
```

경량 Python HTTP 서버가:
1. Google Apps Script WebApp에서 JSON 데이터 fetch
2. Hero/Villain 10×6 CSV로 분리
3. 로컬 파일시스템에 atomic write
4. 비활성 슬롯은 빈 CSV로 초기화

---

## 2. Target Users

| 사용자 | 역할 | 니즈 |
|--------|------|------|
| 방송 PD | 데이터 입력 | Google Sheets에서 쉽게 편집 |
| 그래픽 오퍼레이터 | CSV 소비 | 안정적인 파일 갱신 |
| 기술 담당자 | 서버 관리 | 간단한 설정, 모니터링 |

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Google Cloud                                  │
│  ┌─────────────────┐     ┌─────────────────────────────────────┐    │
│  │  Google Sheets  │────▶│  Apps Script WebApp                 │    │
│  │  (Data Source)  │     │  ?op=nextfetch                      │    │
│  └─────────────────┘     └──────────────────┬──────────────────┘    │
└─────────────────────────────────────────────┼───────────────────────┘
                                              │ HTTPS (JSON)
                                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Local Machine                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     GGM-CSVd (localhost:8787)                 │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐  │   │
│  │  │ HTTP       │  │ Worker     │  │ File Writer            │  │   │
│  │  │ Handler    │──│ Thread     │──│ (atomic_write_text)    │  │   │
│  │  └────────────┘  └────────────┘  └────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                              │                       │
│                                              ▼                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     CSV Directory                             │   │
│  │  Hero1-1.csv  Hero1-2.csv  ...  Hero10-1.csv  Hero10-2.csv   │   │
│  │  Villain1-1.csv  Villain1-2.csv  ...  Villain10-1.csv        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                              │                       │
│                                              ▼                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  After Effects / OBS (CSV Reader)                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
1. External Trigger
   └─ GET/POST http://localhost:8787/next

2. Queue Registration
   └─ TASK_Q.put({"t":"next", "ts": timestamp})

3. Worker Thread Execution
   ├─ fetch_next(gs_url)
   │   └─ HTTP GET → Apps Script WebApp
   │   └─ Response: { ok, heroSlot, villSlot, csv: {...} }
   │
   ├─ Parse Response
   │   ├─ Dict payload: hero_text = csv[heroSlot]
   │   └─ String payload: split_12_to_6_6()
   │
   └─ write_all()
       ├─ Active slots → hero_text, villain_text
       └─ Inactive slots → blank_csv(10, 6)

4. File Output
   └─ atomic_write_text(path, text)
       ├─ Create temp file
       ├─ Write UTF-8 BOM + content
       └─ os.replace() (atomic)
```

### 3.3 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      ggm_csvd.py                             │
├─────────────────────────────────────────────────────────────┤
│  Configuration                                               │
│  ├─ DEFAULTS (dict)                                         │
│  ├─ CONFIG (global, thread-safe with CONF_LOCK)             │
│  └─ load_config() → reads config.json                       │
├─────────────────────────────────────────────────────────────┤
│  HTTP Server                                                 │
│  ├─ Handler (http.server.BaseHTTPRequestHandler)            │
│  │   ├─ do_GET(): /health, /reload, /next                   │
│  │   └─ do_POST(): /next, /force                            │
│  └─ ThreadingTCPServer (127.0.0.1:8787)                     │
├─────────────────────────────────────────────────────────────┤
│  Worker System                                               │
│  ├─ TASK_Q (queue.Queue)                                    │
│  ├─ worker_loop() → daemon thread                           │
│  └─ perform_next() → main business logic                    │
├─────────────────────────────────────────────────────────────┤
│  File Operations                                             │
│  ├─ atomic_write_text() → tempfile + os.replace             │
│  ├─ blank_csv() → generates empty 10x6 CSV                  │
│  ├─ scan_slot_files() → discovers Hero*/Villain* files      │
│  └─ pick_target_path() → resolves .csv extension            │
├─────────────────────────────────────────────────────────────┤
│  Data Processing                                             │
│  ├─ fetch_next() → HTTP GET to WebApp                       │
│  ├─ split_12_to_6_6() → splits 12-col to 6+6                │
│  └─ write_all() → updates all slot files                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. API Specification

### 4.1 Endpoints

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/health` | 서버 상태 조회 | `{ ok, queue, last, config }` |
| GET | `/next` | CSV 갱신 트리거 | `{ ok, queued }` |
| POST | `/next` | CSV 갱신 트리거 | `{ ok, queued }` |
| GET | `/reload` | config.json 리로드 | `{ ok, reloaded }` |
| POST | `/force` | CSV 강제 쓰기 | `{ ok, wrote, blanked, hero, villain }` |

### 4.2 /health Response

```json
{
  "ok": true,
  "queue": 0,
  "last": {
    "ok": true,
    "wrote": 2,
    "blanked": 18,
    "hero": "Hero1-1",
    "villain": "Villain1-1"
  },
  "config": {
    "csv_dir": "C:/GGM$/CSV",
    "gs_url": "https://script.google.com/...",
    "port": 8787,
    "rows": 10,
    "cols": 12
  }
}
```

### 4.3 /force Request

```json
{
  "hero": "Hero1-1",
  "villain": "Villain1-1",
  "csvHero": "a,b,c,d,e,f\n...",
  "csvVillain": "x,y,z,w,v,u\n..."
}
```

---

## 5. Configuration

### 5.1 config.json Schema

```json
{
  "csv_dir": "C:/GGM$/CSV",
  "gs_url": "https://script.google.com/macros/s/.../exec?op=nextfetch",
  "rows": 10,
  "cols": 12,
  "port": 8787,
  "write_mode": "atomic",
  "process_duplicates": true,
  "dedup_window_ms": 0,
  "whitelist": []
}
```

### 5.2 Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `csv_dir` | string | `D:/CSV_Practice/CSV` | CSV 파일 저장 경로 |
| `gs_url` | string | `""` | Google Apps Script WebApp URL |
| `rows` | int | `10` | CSV 행 수 |
| `cols` | int | `12` | 전체 열 수 (12 → 6+6 분할) |
| `port` | int | `8787` | HTTP 서버 포트 |
| `write_mode` | string | `atomic` | 파일 쓰기 모드 |
| `process_duplicates` | bool | `true` | 중복 요청 처리 여부 |
| `dedup_window_ms` | int | `0` | 중복 제거 시간 창 (ms) |
| `whitelist` | array | `[]` | 대상 슬롯 목록 (비어있으면 자동 스캔) |

---

## 6. CSV File Format

### 6.1 File Naming

```
{Type}{Table}-{Seat}.csv

예시:
- Hero1-1.csv    (테이블 1, 좌석 1, Hero)
- Villain3-2.csv (테이블 3, 좌석 2, Villain)
- Hero_Position.csv (특수: 위치 정보)
```

### 6.2 CSV Structure

```
10행 × 6열, UTF-8 with BOM

Example (blank):
,,,,,
,,,,,
,,,,,
... (10 rows)

Example (with data):
Name,Stack,Position,Action,Amount,Cards
John,50000,BTN,Raise,1500,Ah Kd
...
```

---

## 7. Security Requirements

### 7.1 Current State (v1.2)

| 영역 | 상태 | 위험도 |
|------|------|--------|
| 네트워크 바인딩 | 127.0.0.1 only | LOW |
| 인증/인가 | 없음 | HIGH |
| 입력 검증 | 부분적 | HIGH |
| 파일 경로 검증 | 없음 | HIGH |

### 7.2 Required Security Patches

**Priority 1: 경로 Traversal 방지**
```python
import re
SLOT_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')

def validate_slot_name(name: str) -> bool:
    return bool(SLOT_PATTERN.match(name))
```

**Priority 2: Content-Length 제한**
```python
MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB

def do_POST(self):
    length = int(self.headers.get("Content-Length", "0") or "0")
    if length > MAX_BODY_SIZE:
        return self._send(413, {"ok": False, "error": "Payload too large"})
```

**Priority 3: API 토큰 인증 (선택)**
```json
// config.json
{
  "api_token": "your-secret-token"
}
```

---

## 8. Deployment

### 8.1 Prerequisites

- Python 3.x (표준 라이브러리만 사용)
- Windows (경로 형식: `C:/...`)
- Google Apps Script WebApp 배포

### 8.2 Installation

```bash
# 1. 파일 배치
copy ggm_csvd.py C:\GGM$\CSVD\
copy config.json C:\GGM$\CSVD\

# 2. 설정 편집
notepad C:\GGM$\CSVD\config.json

# 3. 실행
python C:\GGM$\CSVD\ggm_csvd.py
# 또는
run_ggm_csvd.bat
```

### 8.3 Startup Script

```batch
:: run_ggm_csvd.bat
@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found.
  pause
  exit /b 1
)

cmd /k python -u ggm_csvd.py
```

---

## 9. Monitoring & Troubleshooting

### 9.1 Health Check

```bash
curl http://localhost:8787/health
```

### 9.2 Manual Trigger

```bash
curl http://localhost:8787/next
```

### 9.3 Common Issues

| 증상 | 원인 | 해결 |
|------|------|------|
| `gs_url 비어있음` | config.json 미설정 | WebApp URL 설정 |
| `CSV 폴더 없음` | csv_dir 경로 오류 | 폴더 생성 또는 경로 수정 |
| `웹앱 JSON 파싱 실패` | WebApp 응답 오류 | Apps Script 배포 확인 |
| `hero/villain 슬롯이 응답에 없음` | WebApp 응답 형식 | JSON 구조 확인 |

---

## 10. Related Documents

| 문서 | 설명 |
|------|------|
| [PRD-0001-ggm-csvd-gui.md](PRD-0001-ggm-csvd-gui.md) | GUI 대시보드 PRD |
| [CLAUDE.md](../CLAUDE.md) | Claude Code 가이드 |

---

## 11. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2.0 | 2026-01-22 | Hero/Villain 분리 기록, dict payload 지원 |
| 1.1.0 | - | 12열 자동 분할 |
| 1.0.0 | - | 초기 릴리스 |

---

## Appendix A: Google Apps Script WebApp Response Format

### Expected Response (Dict Payload)

```json
{
  "ok": true,
  "heroSlot": "Hero1-1",
  "villSlot": "Villain1-1",
  "csv": {
    "Hero1-1": "a,b,c,d,e,f\na,b,c,d,e,f\n...",
    "Villain1-1": "x,y,z,w,v,u\nx,y,z,w,v,u\n..."
  }
}
```

### Legacy Response (String Payload)

```json
{
  "ok": true,
  "heroSlot": "Hero1-1",
  "villSlot": "Villain1-1",
  "csv": "a,b,c,d,e,f,x,y,z,w,v,u\na,b,c,d,e,f,x,y,z,w,v,u\n..."
}
```

12열 문자열은 자동으로 6+6으로 분할됩니다.
