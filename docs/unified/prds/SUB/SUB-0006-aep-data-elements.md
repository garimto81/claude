# Part 1: Overview

## 1.1 목적

**AEP 동적 레이어 분석 결과를 기반으로 26개 자막 유형별 필요 데이터 필드를 정의**

WSOP Broadcast Graphics 시스템에서 자막 렌더링에 필요한 데이터 요소를 명확히 정의하여:
1. 데이터 입력 담당자가 어떤 데이터를 준비해야 하는지 파악
2. DB 스키마와 AEP 레이어 간의 정확한 매핑 제공
3. CSV 템플릿 및 수기 입력 UI 설계 기반 제공

---

## 1.2 범위

### 포함

| 데이터 소스 | 설명 | 담당 |
|------------|------|------|
| **WSOP+ CSV** | 대회 정보, 블라인드, 상금, 플레이어 칩 (Other Tables) | Data Manager |
| **수기 입력** | 프로필, 해설자, 일정, Feature Table 구성 | PA/PD/Production |

### 제외

| 데이터 소스 | 이유 |
|------------|------|
| **pokerGFX JSON** | GFX 실시간 데이터 - PRD-0004에서 별도 처리 |
| **AEP 스키마 설계** | automation_ae 프로젝트에서 별도 처리 |

---

## 1.3 AEP 분석 결과 요약

### 원본 파일

- **경로**: `C:\claude\automation_ae\templates\CyprusDesign\CyprusDesign.aep`
- **분석 범위**: **AEP 내부 `comp` 폴더 이하의 콤포지션만 분석**
- **분석 결과**: `C:\claude\automation_ae\templates\CyprusDesign\analysis\`

### 통계 (재분석 및 수정 예정)

| 항목 | 수량 |
|------|------|
| 총 콤포지션 | 58개 |
| 총 Footage | 294개 |
| 텍스트 레이어 | 1,397개 |
| 자막 콤포지션 | 18개 |

### 식별된 자막 콤포지션 (재검토 필요)

> ⚠️ **주의**: 현재 아래 목록은 `comp` 폴더 외부의 불필요한 콤포지션이 포함되어 있을 수 있습니다. 실제 방송용 `comp` 폴더 기준으로 재작성되어야 합니다.

| # | 콤포지션명 | 자막 유형 | 텍스트 레이어 |
|---|-----------|----------|-------------|
| 1 | Feature Table Leaderboard MAIN | Feature Table LB | 42개 |
| 2 | Feature Table Leaderboard SUB | Feature Table LB (서브) | 41개 |
| 3 | _MAIN Mini Chip Count | Mini Chip Counts | 21개 |
| 4 | _SUB_Mini Chip Count | Mini Chip Counts (서브) | 21개 |
| 5 | Payouts | Payouts | 31개 |
| 6 | _Mini Payout | Mini Payouts | 29개 |
| 7 | Event info | Event Info | 10개 |
| 8 | Broadcast Schedule | Broadcast Schedule | 23개 |
| 9 | Commentator | Commentator Profile | 8개 |
| 10 | Location | Venue/Location | 2개 |
| 11 | Chip Flow | Chip Flow | 15개 |
| 12 | Chip Comparison | Chip Comparison | 4개 |
| 13 | Chip VPIP | VPIP Stats | 3개 |
| 14 | Chips In Play x3/x4 | Chips In Play | 4-5개 |
| 15 | Elimination | Elimination Banner | 2개 |
| 16 | At Risk of Elimination | At Risk | 1개 |
| 17 | NAME / NAME 1줄 / NAME 2줄 / NAME 3줄+ | Player Profile | 2개 |
| 18 | Block Transition Level-Blinds | Blind Level | 12개 |
| 19 | Event name | Event Name | 2개 |

---

## 1.4 목표

### 주요 산출물

1. **자막별 데이터 필드 명세서** (Part 3)
   - 각 콤포지션의 동적 레이어 목록
   - 필요 데이터 필드 및 타입
   - 데이터 소스 (CSV/수기)

2. **DB 매핑 테이블** (Part 4)
   - AEP 레이어 → wsop 스키마 테이블 매핑
   - 필드별 변환 규칙

3. **입력 가이드** (Part 5)
   - CSV 템플릿 정의
   - 수기 입력 필드 목록

### 성공 기준

| 기준 | 목표 |
|------|------|
| 자막 커버리지 | 18개 AEP 콤포지션 100% 매핑 |
| 필드 정의율 | 모든 동적 레이어에 대해 DB 필드 매핑 |
| CSV 템플릿 | 주요 자막 유형별 템플릿 제공 |

---

## 1.5 관련 문서

| 문서 | 설명 | 참조 |
|------|------|------|
| PRD-0001 | 26개 자막 유형 디자인 | 자막 유형 정의 |
| PRD-0003 | 데이터 수집 워크플로우 | 데이터 소스 분류 |
| PRD-0004 | Caption Database Schema | wsop 스키마 테이블 |
| AEP 분석 파일 | CyprusDesign 분석 결과 | 동적 레이어 목록 |

---

## 1.6 용어 정의

| 용어 | 설명 |
|------|------|
| **동적 레이어** | AEP에서 데이터 바인딩으로 내용이 변경되는 레이어 |
| **텍스트 레이어** | 플레이어 이름, 칩 수량 등 텍스트 데이터 |
| **Footage 레이어** | 국기 이미지, 프로필 사진 등 미디어 데이터 |
| **WSOP+ CSV** | WSOP+ 시스템에서 내보내는 대회 데이터 CSV |
| **수기 입력** | 운영자가 직접 입력하는 데이터 |


---

# Part 2: Data Sources

## 2.1 데이터 소스 분류

### 상호 배타적 원칙

각 데이터 필드는 **하나의 소스에서만** 입력됩니다. 충돌 방지를 위해 소스별 담당 영역이 명확히 구분됩니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    데이터 소스 구조                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │ pokerGFX    │   │ WSOP+ CSV   │   │ 수기 입력    │       │
│  │ JSON        │   │             │   │             │       │
│  ├─────────────┤   ├─────────────┤   ├─────────────┤       │
│  │ Feature     │   │ 대회 정보    │   │ 프로필      │       │
│  │ Table RFID  │   │ 블라인드     │   │ 해설자      │       │
│  │ 실시간 데이터 │   │ 상금 구조    │   │ 일정        │       │
│  │ (제외)      │   │ Other Table │   │ Feature     │       │
│  │             │   │ 플레이어 칩  │   │ Table 구성  │       │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
│       ❌              ✅               ✅                   │
│    PRD-0004        본 문서 범위       본 문서 범위          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2.2 WSOP+ CSV 데이터

### 담당: Data Manager

WSOP+ 시스템에서 내보내는 대회 운영 데이터입니다.

### 테이블별 필드

#### tournaments (대회 정보)

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| name | VARCHAR | 대회명 | "MAIN EVENT" |
| buy_in | INTEGER | 바이인 금액 | 5300 |
| prize_pool | BIGINT | 총 상금 | 6860000 |
| registered_players | INTEGER | 총 참가자 | 1372 |
| remaining_players | INTEGER | 남은 참가자 | 8 |
| places_paid | INTEGER | 상금 지급 순위 | 206 |

#### blind_levels (블라인드 레벨)

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| level_number | INTEGER | 레벨 번호 | 32 |
| small_blind | INTEGER | 스몰 블라인드 | 100000 |
| big_blind | INTEGER | 빅 블라인드 | 200000 |
| ante | INTEGER | 앤티 | 200000 |
| duration | INTEGER | 레벨 시간 (분) | 60 |

#### payouts (상금 구조)

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| place_start | INTEGER | 순위 시작 | 1 |
| place_end | INTEGER | 순위 끝 | 1 |
| amount | BIGINT | 상금 | 1000000 |
| percentage | DECIMAL | 비율 (%) | 14.6 |

#### player_instances (Other Tables 칩)

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| chips | BIGINT | 현재 칩 | 22975000 |
| current_rank | INTEGER | 현재 순위 | 1 |

> **주의**: Feature Table 플레이어의 칩은 pokerGFX JSON에서 실시간 수신

---

## 2.3 수기 입력 데이터

### 담당별 필드

#### PA (Production Assistant) - 현장

| 테이블 | 필드 | 설명 |
|--------|------|------|
| player_instances | seat_number | 좌석 번호 (1-9) |
| feature_tables | players[] | 테이블 플레이어 배치 |

#### PD (Program Director) - 디렉터

| 테이블 | 필드 | 설명 |
|--------|------|------|
| player_instances | is_feature_table | Feature Table 여부 |
| events | name, type | 이벤트 정보 |
| venues | name, location | 장소 정보 |

#### Data Manager

| 테이블 | 필드 | 설명 |
|--------|------|------|
| players_master | long_name | 풀네임 |
| players_master | photo_url | 프로필 사진 URL |
| players_master | nationality | 국적 코드 (ISO 2) |
| players_master | bracelets | 브레이슬릿 수 |

#### Production Team

| 테이블 | 필드 | 설명 |
|--------|------|------|
| commentators | name | 해설자 이름 |
| commentators | credentials | 직함/소속 |
| commentators | social_handle | SNS 핸들 |
| commentators | photo_url | 프로필 사진 |
| schedules | date | 방송 날짜 |
| schedules | time_start | 시작 시간 |
| schedules | title | 방송 제목 |

---

## 2.4 자막별 데이터 소스 매핑

| 자막 유형 | WSOP+ CSV | 수기 입력 | GFX JSON (제외) |
|----------|:---------:|:---------:|:---------------:|
| Feature Table LB | - | seat, is_feature | chips, rank |
| Mini Chip Counts | - | - | chips, rank |
| Payouts | payouts | - | - |
| Mini Payouts | payouts | - | - |
| Event Info | tournaments | events | - |
| Broadcast Schedule | - | schedules | - |
| Commentator Profile | - | commentators | - |
| Venue/Location | - | venues | - |
| Chip Flow | - | - | chip_flow |
| Chip Comparison | - | - | chips |
| VPIP Stats | - | - | player_stats |
| Chips In Play | blind_levels | - | chips |
| Elimination Banner | - | - | eliminations |
| At Risk | payouts | - | chips |
| Player Profile | - | players_master | - |
| Blind Level | blind_levels | - | - |
| Event Name | - | events | - |

---

## 2.5 데이터 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                      데이터 입력 흐름                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   WSOP+ 시스템                                              │
│   ┌─────────────┐                                          │
│   │  CSV Export │ ─────────┐                               │
│   └─────────────┘          │                               │
│                            ▼                               │
│   운영자 입력           ┌─────────────┐                     │
│   ┌─────────────┐      │   wsop DB   │                     │
│   │  Web UI     │ ────▶│   스키마    │                     │
│   └─────────────┘      └─────────────┘                     │
│                            │                               │
│                            ▼                               │
│                    ┌─────────────┐                         │
│                    │   API       │                         │
│                    └─────────────┘                         │
│                            │                               │
│                            ▼                               │
│                    ┌─────────────┐                         │
│                    │  AE 렌더링  │                         │
│                    │  (Nexrender)│                         │
│                    └─────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2.6 데이터 갱신 주기

| 데이터 소스 | 갱신 주기 | 방식 |
|------------|----------|------|
| WSOP+ CSV | 레벨 종료 시 | 수동 업로드 |
| 수기 입력 (대회 정보) | 대회 시작 전 | 수동 입력 |
| 수기 입력 (좌석 배치) | 테이블 변경 시 | 수동 입력 |
| 수기 입력 (해설자) | 방송 시작 전 | 수동 입력 |

> **참고**: pokerGFX JSON은 실시간 (~1초 간격) 자동 갱신 - 본 문서 범위 외


---
