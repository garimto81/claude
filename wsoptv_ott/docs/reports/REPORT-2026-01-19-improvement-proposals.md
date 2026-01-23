# REPORT-2026-01-19: 문서 개선 제안서

**Date**: 2026-01-19
**Basis**: STRAT-0001-viewer-experience-vision.md (시청자 경험 비전)
**Scope**: PRD-0002, PRD-0006, STRAT-0007 Gap 분석 및 개선 제안

---

## Executive Summary

STRAT-0001 (시청자 경험 비전)을 기준으로 기존 문서를 분석한 결과, 다음과 같은 개선 기회를 발견했습니다:

| 구분 | 현황 | Gap | 개선 필요도 |
|------|------|-----|:----------:|
| **핵심 차별점** | 흩어져 있음 | 일관된 메시지 부재 | HIGH |
| **동영상 Tagging** | PRD-0006에 간략 언급 | 별도 PRD 필요 | HIGH |
| **검색 기능** | 미정의 | Phase 2 기능 누락 | MEDIUM |
| **우선순위** | 기술 중심 | 시청자 관점 재정렬 | MEDIUM |

---

## 1. Gap 분석: STRAT-0001 vs 기존 문서

### 1.1 YouTube 대비 핵심 차별점

**STRAT-0001 정의**:
1. Timeshift - 라이브 중 뒤로 가기 가능
2. 아카이브 - 종료 후 영상 유지
3. Advanced Mode - Multi-view + StatsView
4. 검색 기능 - 핸드/선수 기반 검색 (Phase 2)

**PRD-0002 현황**:
- FR-3 Timeshift: 잘 정의됨
- FR-4 Advanced Mode: 잘 정의됨
- **검색 기능: 간략 언급만** (Collections Screen 검색)

**Gap**: 핸드/선수 기반 검색이 별도 Feature로 정의되지 않음

---

### 1.2 동영상 Tagging 시스템

**STRAT-0001 정의 (Tony 기획)**:

| 태깅 필드 | 설명 |
|----------|------|
| Hand Number | 핸드 넘버, 시작/종료 타임스탬프 |
| 참여 플레이어 | 해당 핸드에 참여한 선수 목록 |
| 각 플레이어 Hands | 홀카드 정보 |
| Community Card | 플랍/턴/리버 카드 |
| 최종 Winner | 해당 핸드 승자 |

**PRD-0006 현황** (섹션 12):
- 선수별/테이블별 멀티 재생: 간략 언급
- 동영상 Tagging: 간략 언급
- 고급 검색 기능: 간략 언급

**Gap**:
- 동영상 Tagging이 **FR-요구사항**으로 정의되지 않음
- **별도 PRD 필요** (데이터 모델, 태깅 파이프라인, UI/UX)

---

### 1.3 고급 검색 기능

**STRAT-0001 정의 (Tony 기획)**:

| 검색 유형 | 예시 |
|----------|------|
| 선수 기반 | 특정 선수가 참여한 Pot만 재생 |
| 핸드 결과 기반 | 특정 핸드로 이기거나 진 핸드 |
| 복합 검색 | A 선수와 B 선수가 함께 했던 대회 |
| 특수 상황 | 포카드가 로열 스트레이트에게 패한 핸드 |

**현황**:
- PRD-0006 섹션 12에 간략 언급
- PRD-0002 Collections Screen: 대회명, 년도, 플레이어명 검색만

**Gap**:
- **핸드 단위 검색 미정의**
- 복합 조건 검색 미정의
- Elasticsearch 스키마에 핸드 태그 미포함

---

### 1.4 콘텐츠 소싱 전략

**STRAT-0001 정의 (Michael 기획)**:

| 소스 | 수량 | 특징 |
|------|------|------|
| ESPN | 10개/년 | 1년 후 WSOPTV 유입 |
| PokerGO | 10개/년 | 계약에 따라 유입 |
| WSOP 직접 | 30개/년 | YouTube + WSOPTV 동시 중계 |

**STRAT-0007 현황**:
- 잘 정의됨, 상세 파트너십 모델 포함
- 메타데이터 태깅 시스템 정의됨

**Gap**:
- STRAT-0007이 STRAT-0001과 잘 정렬됨
- 단, **핸드 단위 태깅**이 STRAT-0007에 미포함

---

## 2. 개선 제안

### 제안 A: PRD-0009 "Hand Tagging & Search" 신규 작성

**목적**: Tony 기획의 핵심 기능을 별도 PRD로 정의

**포함 내용**:

```
PRD-0009: Hand Tagging & Search System

1. 동영상 Tagging 데이터 모델
   - Hand 엔티티
   - Player 참여 엔티티
   - Card 엔티티
   - Result 엔티티

2. 태깅 파이프라인
   - 자동 태깅 (AI/OCR)
   - 수동 검증 (QA)
   - 해설 Script 연동

3. 검색 UI/UX
   - 선수 검색
   - 핸드 조건 검색
   - 복합 검색 빌더
   - 검색 결과 → 해당 시점 점프

4. 기술 요구사항
   - Elasticsearch 핸드 인덱스
   - 타임스탬프 연동
```

**우선순위**: P2 (Phase 2)
**권장 일정**: Q4 2026

---

### 제안 B: PRD-0002 Executive Summary 개선

**현재**:
> WSOP(World Series of Poker) 공식 OTT 스트리밍 플랫폼 구축...

**제안**:
> WSOP 공식 OTT 플랫폼. **YouTube 대비 4가지 핵심 차별점** 제공:
> 1. **Timeshift**: 라이브 중 뒤로 가기 (YouTube 불가)
> 2. **아카이브**: 종료 후 영상 영구 보존 (YouTube 비공개)
> 3. **Advanced Mode**: Multi-view + StatsView
> 4. **검색**: 핸드/선수 기반 정밀 검색 (Phase 2)

**효과**: 시청자 관점 가치 제안 명확화

---

### 제안 C: STRAT-0007 핸드 태깅 섹션 추가

**현재 Content Tagging System** (섹션 5):
- 소스 태그
- 이벤트 태그
- 시리즈 태그
- 게임 타입 태그
- 년도 태그

**제안 추가**:

```markdown
#### 5.6 핸드 레벨 태그 (Phase 2)

대회 영상을 핸드 단위로 태깅하여 정밀 검색 지원.

| 태그 유형 | 예시 | 용도 |
|----------|------|------|
| `HAND_#N` | HAND_#47 | 특정 핸드 식별 |
| `PLAYER_IN_HAND` | ivey, negreanu | 참여 선수 필터 |
| `HOLE_CARDS` | AA, KQs | 홀카드 기반 검색 |
| `BOARD_TEXTURE` | flush_possible | 보드 상황 |
| `SHOWDOWN_WINNER` | player_name | 쇼다운 승자 |
| `RESULT_TYPE` | bad_beat, cooler | 결과 유형 |

**데이터 소스**:
- 해설 Script 자동 파싱
- RFID 테이블 데이터
- 수동 QA 검증
```

---

### 제안 D: 우선순위 재정렬 (시청자 관점)

**현재 Phase 구분**:

| Phase | 기존 정의 |
|-------|----------|
| Phase 1 | Web + Mobile, 라이브 + VOD |
| Phase 2 | TV 앱, 3계층 멀티뷰 |
| Phase 3 | 4K, AI 챕터 |

**제안 재정렬**:

| Phase | 시청자 관점 우선순위 |
|-------|---------------------|
| **Phase 1** | 핵심 차별점 확립 |
|  | - Timeshift (YouTube 불가 기능) |
|  | - 아카이브 (영구 보존) |
|  | - Multi-view 4분할 (NBA 스타일) |
|  | - StatsView (GGPoker HUD) |
| **Phase 2** | 검색 & 탐색 강화 |
|  | - Key Hands 점프 |
|  | - Hand-by-Hand Log |
|  | - **핸드 태깅 시스템** ★ |
|  | - **선수/핸드 검색** ★ |
| **Phase 3** | 프리미엄 확장 |
|  | - 3계층 Multi-view |
|  | - Position Analysis |
|  | - AI Key Hands 자동 추출 |
|  | - 4K 화질 |

**근거**:
- Phase 2에 Tony 기획 (핸드 태깅, 검색) 명시적 포함
- 시청자가 "특정 선수/핸드 찾기"를 원할 때 대응

---

### 제안 E: 문서 간 참조 강화

**현재 문제**:
- STRAT-0001이 핵심 전략이나 다른 문서에서 참조 없음
- PRD-0002, PRD-0006이 STRAT-0001을 언급하지 않음

**제안**:

1. **PRD-0002 References 섹션에 추가**:
```markdown
### 전략 문서
- [STRAT-0001 Viewer Experience Vision](../strategies/STRAT-0001-viewer-experience-vision.md) - **핵심 전략 (YouTube 대비 차별점)**
```

2. **PRD-0006 Executive Summary에 추가**:
```markdown
> **전략 기준**: [STRAT-0001 시청자 경험 비전](../strategies/STRAT-0001-viewer-experience-vision.md)
```

3. **STRAT-0007에 추가**:
```markdown
## References
- [STRAT-0001 Viewer Experience Vision](STRAT-0001-viewer-experience-vision.md) - 시청자 관점 핵심 전략
```

---

## 3. 실행 권장 순서

| 순서 | 작업 | 영향도 | 난이도 |
|:----:|------|:------:|:------:|
| 1 | PRD-0002 Executive Summary 개선 | HIGH | LOW |
| 2 | 문서 간 STRAT-0001 참조 추가 | MEDIUM | LOW |
| 3 | STRAT-0007 핸드 태깅 섹션 추가 | HIGH | MEDIUM |
| 4 | PRD-0009 Hand Tagging & Search 작성 | HIGH | HIGH |
| 5 | 우선순위 재정렬 반영 | MEDIUM | MEDIUM |

---

## 4. 결론

STRAT-0001 (시청자 경험 비전)은 Michael + Tony의 핵심 아이디어를 정리한 문서로, **기존 문서들과의 정렬이 필요**합니다.

### 핵심 개선점:

1. **Tony 기획 (핸드 태깅, 검색) 별도 PRD 필요**
   - PRD-0009 신규 작성 권장

2. **YouTube 대비 차별점 명확화**
   - PRD-0002 Executive Summary 개선

3. **문서 계층 구조 확립**
   - STRAT-0001 → PRD-0002/PRD-0006 → STRAT-0007 참조 연결

4. **Phase 2에 검색 기능 명시**
   - 시청자 관점 우선순위 반영

---

*Report Generated: 2026-01-19*
*Basis: STRAT-0001-viewer-experience-vision.md*
