# PokerGFX Server 분석 보고서

**분석 일자**: 2026-01-22
**대상 경로**: `C:\Program Files\PokerGFX\Server`
**총 용량**: ~383 MB (11개 파일)

---

## 1. 요약

PokerGFX Server는 **포커 방송/스트리밍을 위한 그래픽 서버 애플리케이션**입니다. .NET Framework 기반으로 제작되었으며, RFID 카드 데이터 처리, 실시간 그래픽 오버레이, 보안 딜레이 기능을 제공합니다.

---

## 2. 파일 구조

### 2.1 실행 파일 (Executables)

| 파일명 | 크기 | 아키텍처 | 용도 |
|--------|------|----------|------|
| **PokerGFX-Server.exe** | 356 MB | x86-64 .NET | 메인 서버 (그래픽 렌더링, RFID 처리) |
| **ActionTracker.exe** | 8.9 MB | x86-64 .NET | 액션 추적 (bet/raise/fold 등) |
| **GFXUpdater.exe** | 56 KB | i386 .NET | 업데이트 유틸리티 |

### 2.2 라이브러리 (Libraries)

| 파일명 | 크기 | 유형 | 용도 |
|--------|------|------|------|
| **PokerGFX.Common.dll** | 553 KB | .NET Assembly | 공통 라이브러리 |
| **Newtonsoft.Json.dll** | 696 KB | .NET Assembly | JSON 직렬화 (v7.0+) |
| **libSkiaSharp.dylib** | 15 MB | Mach-O Universal | 그래픽 렌더링 (SkiaSharp) |

### 2.3 디버그 심볼 (Debug Symbols)

| 파일명 | 크기 |
|--------|------|
| PokerGFX-Server.pdb | 2.1 MB |
| ActionTracker.pdb | 230 KB |
| GFXUpdater.pdb | 90 KB |

### 2.4 설정 파일 (Configuration)

| 파일명 | 내용 |
|--------|------|
| **GFXUpdater.exe.config** | Assembly binding redirect (System.Runtime.CompilerServices.Unsafe v6.0) |
| **net_conn.dll.config** | Entity Framework 6.0 DB provider 설정 (SQL Server + SQLite) |

---

## 3. 기술 스택

```
┌─────────────────────────────────────────────────┐
│                 PokerGFX Server                 │
├─────────────────────────────────────────────────┤
│  Application Layer                              │
│  ├── PokerGFX-Server.exe (Main)                │
│  ├── ActionTracker.exe (Tracking)              │
│  └── GFXUpdater.exe (Maintenance)              │
├─────────────────────────────────────────────────┤
│  Common Library                                 │
│  └── PokerGFX.Common.dll                       │
├─────────────────────────────────────────────────┤
│  Third-party Dependencies                       │
│  ├── Newtonsoft.Json (JSON)                    │
│  ├── SkiaSharp (Graphics)                      │
│  └── Entity Framework 6.0 (ORM)                │
├─────────────────────────────────────────────────┤
│  Database Providers                             │
│  ├── System.Data.SqlClient (SQL Server)        │
│  └── System.Data.SQLite.EF6 (SQLite)           │
└─────────────────────────────────────────────────┘
```

| 영역 | 기술 |
|------|------|
| **플랫폼** | .NET Framework (Windows) |
| **언어** | C# |
| **ORM** | Entity Framework 6.0 |
| **그래픽** | SkiaSharp (Skia 기반 2D 렌더링) |
| **직렬화** | Newtonsoft.Json |
| **데이터베이스** | SQL Server / SQLite (dual support) |

---

## 4. 주요 컴포넌트 분석

### 4.1 PokerGFX-Server.exe (메인 서버)

**크기**: 356 MB (리소스 내장으로 추정)

**주요 기능**:
- RFID 카드 리더 데이터 수신 및 처리
- 실시간 포커 그래픽 오버레이 생성
- 보안 딜레이 (Secure Delay) 기능
- 플레이어 핸드 추적 및 표시
- 방송 그래픽 렌더링

### 4.2 ActionTracker.exe (액션 추적)

**크기**: 8.9 MB

**주요 기능**:
- 플레이어 액션 추적 (call, bet, raise, fold)
- 오퍼레이터 입력 관리
- 핸드 상태 실시간 추적

### 4.3 GFXUpdater.exe (업데이터)

**크기**: 56 KB

**주요 기능**:
- 소프트웨어 버전 관리
- 자동 업데이트 처리

---

## 5. 보안 특성

PokerGFX 보안 문서에 따르면:

| 보안 기능 | 설명 |
|-----------|------|
| **AES-256 암호화** | RFID 카드 데이터베이스 암호화 |
| **TLS 1.2** | USB 리더 모듈 통신 보안 |
| **Secure Delay** | 신뢰 없는 보안을 위한 딜레이 기능 |
| **Cards-down 그래픽** | 홀카드 보호를 위한 실시간 그래픽 |

---

## 6. 빌드 정보

| 파일 | 최종 수정일 |
|------|------------|
| PokerGFX-Server.exe | 2025-12-31 01:29 |
| ActionTracker.exe | 2025-12-31 01:29 |
| libSkiaSharp.dylib | 2025-04-25 |
| Newtonsoft.Json.dll | 2023-03-08 |

---

## 7. 특이 사항

### 7.1 대용량 메인 바이너리
- 356 MB 크기는 내장 리소스 (그래픽 템플릿, 폰트, 이미지 등) 포함으로 추정

### 7.2 macOS 라이브러리 포함
- `libSkiaSharp.dylib` (Mach-O Universal Binary) 존재
- 크로스 플랫폼 지원 계획 또는 빌드 아티팩트 잔재

### 7.3 소스 코드 미포함
- 컴파일된 바이너리만 배포
- PDB 심볼 파일 포함 (디버깅 지원)

### 7.4 듀얼 데이터베이스 지원
- 엔터프라이즈: SQL Server
- 경량: SQLite

---

## 8. 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────────┐
│                      Live Production                         │
│  ┌──────────┐    ┌─────────────────┐    ┌──────────────┐   │
│  │  RFID    │───▶│ PokerGFX-Server │───▶│  Broadcast   │   │
│  │ Readers  │    │                 │    │   Output     │   │
│  └──────────┘    │  - Card Data    │    └──────────────┘   │
│                  │  - Graphics     │                        │
│  ┌──────────┐    │  - Secure Delay │    ┌──────────────┐   │
│  │ Operator │───▶│                 │───▶│   Database   │   │
│  │  Input   │    └─────────────────┘    │ (SQL/SQLite) │   │
│  └──────────┘            │              └──────────────┘   │
│                          │                                  │
│                 ┌────────▼────────┐                        │
│                 │  ActionTracker  │                        │
│                 │ (bet/raise/fold)│                        │
│                 └─────────────────┘                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. 결론

PokerGFX Server는 **프로덕션 등급의 포커 방송 그래픽 서버**입니다:

- **모듈화된 아키텍처**: 메인 서버, 액션 추적, 업데이터 분리
- **데이터베이스 유연성**: SQL Server / SQLite 선택 가능
- **보안 중시**: AES-256, TLS 1.2, Secure Delay 구현
- **그래픽 성능**: SkiaSharp 기반 고품질 2D 렌더링

라이브 포커 스트리밍/방송 환경에서 RFID 카드 인식과 실시간 그래픽 오버레이를 제공하는 완성된 방송 솔루션입니다.
