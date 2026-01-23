# STRAT-0001: 시청자 경험 비전 (Viewer Experience Vision)

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Draft

---

## 개요

WSOPTV를 어떻게 설계할 것인가? - **시청자의 관점**에서 정의한 핵심 전략 문서입니다.

---

## 소스 분류

### Vible (핵심 아이디어) - Michael Note

운영 계획과 비즈니스 요구사항의 근간이 되는 Michael의 아이디어입니다.

### Moses Commentary (모세의 첨언) - Tony Note

Michael의 아이디어에 대한 Tony의 보완 의견입니다.

---

## 1. 콘텐츠 소싱 전략

### Vible: 콘텐츠 3단계 구조

| 소스 | 수량 | 특징 |
|------|------|------|
| ESPN | 10개/년 | 계약에 따라 1년 후 WSOPTV 유입 |
| PokerGO | 10개/년 | 계약에 따라 이후 WSOPTV 유입 |
| WSOP 직접 제작 | 30개/년 | YouTube + WSOPTV 동시 중계 |

**핵심 포인트**:
- YouTube 라이브: 뒤로 스크롤 불가 + 종료 후 비공개
- WSOPTV 라이브: 뒤로 가기 허용 + 종료 후 아카이브 유지

### Moses Commentary

> *별도 첨언 없음 - 콘텐츠 소싱은 Michael 방향 그대로 진행*

---

## 2. 시청자 차별화 경험: Advanced Mode

### Vible: Multi-view 개념

**핵심 아이디어**: 아이돌 직캠 카메라 방식
- 메인 화면이 중앙
- 각 선수별 얼굴 카메라가 측면 배치

### Vible: StatsView 개념

**핵심 아이디어**: HUD 스타일 오버레이
- 선수별 통계 (VPIP, PFR 등)
- 플랍 베팅 확률
- 실시간 Pot Odds 표시

### Moses Commentary: 확장된 시청 기능

| 기능 | 설명 |
|------|------|
| **멀티 재생** | 한 테이블 내 각 선수별 화면 동시 재생 |
| **크로스 대회** | 각각 다른 대회/테이블 동시 재생 |
| **핸드 검색** | 특정 선수가 참여한 Pot만 필터링 |
| **패배 패턴 검색** | 포카드 vs 로열 스트레이트 플러시 등 |

**검색 예제**:
- A 선수와 B 선수가 함께 했던 대회/핸드 검색
- 특정 핸드(AA, KK 등)로 이기거나 진 상황 검색

---

## 3. 콘텐츠 메타데이터: 동영상 Tagging

### Moses Commentary: 필수 태깅 항목

| 레벨 | 태깅 데이터 |
|------|------------|
| **Hand 단위** | 핸드 넘버, 시작/종료 타임스탬프 |
| **참여 플레이어** | 해당 핸드에 참여한 선수 목록 |
| **각 플레이어 Hands** | 홀카드 정보 (공개 시점 기준) |
| **Community Card** | 플랍/턴/리버 카드 |
| **최종 Winner** | 해당 핸드 승자 |

**활용 시나리오**:
- 대회 영상 또는 해설 Script 기반 자동 태깅
- 시청자가 특정 조건으로 핸드 검색 가능

---

## 4. 플랫폼 요구사항

### Vible: B2B 요구사항

| 요구사항 | 우선순위 |
|----------|---------|
| GGPass 로그인 | 필수 |
| 구독 모델 구현 | 필수 |
| 역대 모든 WSOP 영상 업로드 | 필수 |
| 5개 플랫폼 배포 | 필수 |
| Web 제공 (WSOP.TV) | 필수 |
| View Mode 전환 | 필수 |
| 광고 지원 | 제외 |

### Moses Commentary: 플랫폼 기능

| 항목 | 설명 |
|------|------|
| 로그인 | GGPass 통합 |
| Payment | 자체 구독 시스템 |

---

## 5. 구독 모델

### Vible: 2티어 구독

| 티어 | 가격 | 이름 |
|------|------|------|
| Basic | $10/월 | WSOP Plus |
| Premium | $50/월 | WSOP Plus+ |

**참고**:
- "Plus"는 구독 명칭
- Exclusive Content (비하인드 씬)는 별도 제작하지 않음

---

## 6. 배포 전략

### Vible: 앱 배포 계정

**WSOP 회사 Apple 계정** (Bracelet IP, Ireland 회사)으로 통합:
- WSOP Live (WSOP+에서 이름 변경 필요)
- WSOP TV
- WSOP Academy
- PokerStake

**마감**: 2027년 3월 1일 전

---

## 7. 시청자 경험 우선순위 매트릭스

| 기능 | 출처 | 우선순위 | MVP 포함 |
|------|------|---------|---------|
| 라이브 스트리밍 | Vible | P0 | Y |
| VOD 아카이브 | Vible | P0 | Y |
| Multi-view | Vible | P1 | Y |
| StatsView | Vible | P1 | Y |
| 핸드 검색 | Moses | P2 | N |
| 멀티 대회 재생 | Moses | P2 | N |
| 동영상 Tagging | Moses | P2 | N |
| 선수별 필터링 | Moses | P2 | N |

---

## 결론

### 핵심 차별점 (YouTube 대비)

1. **Timeshift**: 라이브 중 뒤로 가기 가능
2. **아카이브**: 종료 후 영상 유지
3. **Advanced Mode**: Multi-view + StatsView
4. **검색 기능**: 핸드/선수 기반 정밀 검색 (Phase 2)

### 다음 단계

1. PRD-0002에 핵심 기능 반영
2. PRD-0006 (Advanced Mode) 상세 스펙 작성
3. 동영상 Tagging 시스템 별도 PRD 작성 (Phase 2)

---

*이 문서는 Michael Note와 Tony Note를 기반으로 작성되었습니다.*
