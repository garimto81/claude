# PRD-0009: Hand Tagging & Search System

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Priority** | P2 (Phase 2) |
| **Created** | 2026-01-19 |
| **Author** | Claude Code |
| **Source** | [STRAT-0001](../strategies/STRAT-0001-viewer-experience-vision.md) - Tony 기획 (Moses Commentary) |

---

## Executive Summary

WSOPTV의 **4번째 핵심 차별점** - 핸드/선수 기반 정밀 검색 시스템. 대회 영상을 핸드 단위로 태깅하여 시청자가 원하는 특정 상황을 즉시 찾아볼 수 있는 기능.

> **전략 기준**: [STRAT-0001 시청자 경험 비전](../strategies/STRAT-0001-viewer-experience-vision.md) - YouTube 대비 4번째 핵심 차별점

### 핵심 가치

| YouTube | WSOPTV |
|---------|--------|
| 영상 제목 검색만 가능 | 핸드 단위 검색 가능 |
| 전체 영상 탐색 필요 | 원하는 핸드로 즉시 점프 |
| 선수별 필터 없음 | 특정 선수 참여 핸드 필터 |

---

## Problem Statement

### 현재 상황

- 포커 영상은 수시간 분량이며, 특정 장면을 찾기 어려움
- "Phil Ivey가 AA로 올인한 장면"을 보려면 전체 영상을 탐색해야 함
- 학습 목적으로 특정 상황 (예: Bad Beat)만 모아 보기 불가능

### 해결 방안

- 모든 영상을 핸드 단위로 태깅
- 검색/필터로 원하는 핸드 즉시 탐색
- 검색 결과에서 해당 시점으로 점프

---

## Target Users

| 사용자 | 니즈 | 검색 예시 |
|--------|------|----------|
| **포커 학습자** | 특정 상황 학습 | "AA vs KK 대결" |
| **팬** | 좋아하는 선수 경기 | "Phil Ivey 하이라이트" |
| **분석가** | 패턴 연구 | "리버 블러프 성공" |
| **스트리머** | 콘텐츠 제작 | "Bad Beat 모음" |

---

## Feature Specification

### 1. 핸드 태깅 데이터 모델

#### 1.1 Hand 엔티티

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `hand_id` | UUID | 고유 식별자 | `550e8400-e29b-...` |
| `video_id` | FK | 영상 참조 | `video_001` |
| `hand_number` | INT | 핸드 번호 | `47` |
| `timestamp_start` | TIME | 시작 시점 | `01:23:45` |
| `timestamp_end` | TIME | 종료 시점 | `01:27:30` |
| `blinds` | STRING | 블라인드 레벨 | `50K/100K` |
| `pot_size` | INT | 최종 팟 크기 | `2400000` |

#### 1.2 Player Participation 엔티티

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `hand_id` | FK | 핸드 참조 | - |
| `player_id` | FK | 선수 참조 | `ivey_001` |
| `position` | ENUM | 포지션 | `BTN`, `BB`, `UTG` |
| `hole_cards` | STRING | 홀카드 | `As Ah` |
| `result` | ENUM | 결과 | `WIN`, `FOLD`, `LOSE` |
| `chips_change` | INT | 칩 변동 | `+850000` |

#### 1.3 Board 엔티티

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `hand_id` | FK | 핸드 참조 | - |
| `flop` | STRING | 플랍 | `Ah Kd 7c` |
| `turn` | STRING | 턴 | `2s` |
| `river` | STRING | 리버 | `Qh` |
| `board_texture` | ARRAY | 보드 특성 | `["flush_possible", "straight_possible"]` |

#### 1.4 Action 엔티티

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `hand_id` | FK | 핸드 참조 | - |
| `player_id` | FK | 선수 참조 | - |
| `street` | ENUM | 스트리트 | `PREFLOP`, `FLOP`, `TURN`, `RIVER` |
| `action_type` | ENUM | 액션 | `RAISE`, `CALL`, `FOLD`, `CHECK` |
| `amount` | INT | 금액 | `150000` |
| `timestamp` | TIME | 시점 | `01:24:12` |

---

### 2. 태깅 파이프라인

#### 2.1 데이터 소스

| 소스 | 자동화 | 정확도 | 비용 |
|------|:------:|:------:|:----:|
| **RFID 테이블** | 100% | 99% | 높음 |
| **해설 Script** | 80% | 90% | 중간 |
| **OCR/AI** | 70% | 85% | 낮음 |
| **수동 QA** | 0% | 100% | 매우 높음 |

#### 2.2 태깅 워크플로우

```
영상 업로드
    │
    ▼
┌─────────────────────┐
│ 1. 자동 태깅 (AI)    │
│ - OCR 카드 인식      │
│ - 해설 Script 파싱   │
│ - RFID 데이터 연동   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. 수동 QA 검증      │
│ - 핸드 번호 확인     │
│ - 홀카드 검증        │
│ - 결과 검증         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. 검색 인덱싱       │
│ - Elasticsearch     │
│ - 필터 최적화       │
└─────────────────────┘
```

---

### 3. 검색 UI/UX

#### 3.1 검색 유형

| 유형 | 설명 | 예시 쿼리 |
|------|------|----------|
| **선수 기반** | 특정 선수 참여 핸드 | `player:ivey` |
| **핸드 기반** | 특정 홀카드 | `cards:AA`, `cards:KQs` |
| **결과 기반** | 승패/특수 상황 | `result:bad_beat` |
| **복합 검색** | 여러 조건 조합 | `player:ivey AND cards:AA` |

#### 3.2 검색 예시 (Tony 기획)

| 검색 요청 | 쿼리 변환 |
|----------|----------|
| "A 선수와 B 선수가 함께 했던 대회" | `player:A AND player:B` |
| "포카드가 로열 스트레이트에게 패한 핸드" | `loser_hand:quads AND winner_hand:royal_flush` |
| "Phil Ivey AA 승리" | `player:ivey AND cards:AA AND result:win` |
| "리버 블러프 성공" | `river_bluff:true AND result:win` |

#### 3.3 검색 결과 UI

```
┌─────────────────────────────────────────────────────────────┐
│ 검색: "Phil Ivey AA"                                        │
│ 결과: 47개 핸드                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [썸네일]  Hand #47 - WSOP Main Event 2025               │ │
│  │          Phil Ivey vs Negreanu                          │ │
│  │          A♠ A♥ vs K♠ K♦                                │ │
│  │          POT: $2.4M | Result: WIN                       │ │
│  │          [▶ 해당 시점으로 이동]                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [썸네일]  Hand #112 - High Roller $100K                 │ │
│  │          Phil Ivey vs Polk                              │ │
│  │          A♠ A♦ vs Q♠ Q♥                                │ │
│  │          POT: $890K | Result: WIN                       │ │
│  │          [▶ 해당 시점으로 이동]                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 3.4 검색 필터

| 필터 | 옵션 |
|------|------|
| **대회** | Main Event, High Roller, 전체 |
| **년도** | 2020-2026 |
| **선수** | 자동완성 지원 |
| **포지션** | BTN, BB, SB, CO, MP, UTG |
| **결과** | 승리, 패배, 폴드 |
| **특수 상황** | Bad Beat, Cooler, Bluff |

---

### 4. 기술 요구사항

#### 4.1 Elasticsearch 스키마

```json
{
  "mappings": {
    "properties": {
      "hand_id": { "type": "keyword" },
      "video_id": { "type": "keyword" },
      "tournament": { "type": "text" },
      "year": { "type": "integer" },
      "players": {
        "type": "nested",
        "properties": {
          "name": { "type": "text" },
          "cards": { "type": "keyword" },
          "position": { "type": "keyword" },
          "result": { "type": "keyword" }
        }
      },
      "board": { "type": "keyword" },
      "pot_size": { "type": "long" },
      "tags": { "type": "keyword" },
      "timestamp": { "type": "date" }
    }
  }
}
```

#### 4.2 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| `GET` | `/api/v1/hands/search` | 핸드 검색 |
| `GET` | `/api/v1/hands/{id}` | 핸드 상세 |
| `GET` | `/api/v1/players/{id}/hands` | 선수별 핸드 |
| `POST` | `/api/v1/hands` | 태그 생성 (관리자) |

---

## Scope

### In Scope (Phase 2)

| 항목 | 설명 |
|------|------|
| 핸드 태깅 시스템 | 데이터 모델 + 파이프라인 |
| 기본 검색 | 선수, 핸드, 결과 기반 |
| 복합 검색 | AND/OR 조건 |
| 검색 결과 → 점프 | 해당 시점으로 이동 |

### Out of Scope

| 항목 | 사유 | Phase |
|------|------|-------|
| AI 자동 태깅 | VLM 고비용 | Phase 3 |
| 음성 검색 | 추가 개발 필요 | Phase 3 |
| 추천 알고리즘 | ML 모델 필요 | Phase 3 |

---

## Dependencies

| 의존성 | 설명 | 담당 |
|--------|------|------|
| RFID 테이블 데이터 | 실시간 카드 정보 | 프로덕션팀 |
| 해설 Script | 핸드별 설명 | 콘텐츠팀 |
| Elasticsearch 인프라 | 검색 엔진 | 개발팀 |
| 영상 타임스탬프 | 핸드-시점 매핑 | OVP 업체 |

---

## Success Metrics

| 지표 | 목표 | 측정 |
|------|------|------|
| 검색 사용률 | 월 10K+ 검색 | 로그 분석 |
| 검색→재생 전환율 | 70%+ | 클릭 추적 |
| 검색 정확도 | 상위 3개 중 1개 정확 | 사용자 피드백 |
| 태깅 커버리지 | 신규 영상 100% | 태깅 완료율 |

---

## Timeline

| 마일스톤 | 내용 | 예상 시점 |
|---------|------|----------|
| M1 | 데이터 모델 설계 | Q3 2026 |
| M2 | 태깅 파이프라인 구축 | Q4 2026 |
| M3 | 검색 UI 개발 | Q4 2026 |
| M4 | 베타 출시 | Q1 2027 |

---

## References

- [STRAT-0001 시청자 경험 비전](../strategies/STRAT-0001-viewer-experience-vision.md) - Tony 기획 원본
- [PRD-0002 WSOPTV OTT Platform MVP](PRD-0002-wsoptv-ott-platform-mvp.md) - Phase 2 연계
- [PRD-0006 Advanced Mode](PRD-0006-advanced-mode.md) - Key Hands 연동
- [STRAT-0007 Content Sourcing](../strategies/STRAT-0007-content-sourcing.md) - 핸드 레벨 태그

---

*Created: 2026-01-19*
