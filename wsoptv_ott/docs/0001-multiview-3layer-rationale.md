# Architecture Decision Record: 3계층 Multi-View 설계 논리

| 항목 | 내용 |
|------|------|
| **제목** | Multi-View 구조: 2계층에서 3계층으로의 진화 논리 |
| **작성일** | 2026-01-16 |
| **상태** | Draft |
| **영향도** | High - Advanced Mode의 핵심 UX 설계 |
| **관련 PRD** | [PRD-0002](../../tasks/prds/PRD-0002-wsoptv-ott-platform-mvp.md), [PRD-0006](../../tasks/prds/PRD-0006-advanced-mode.md) |

---

## Executive Summary

WSOPTV의 Advanced Mode에서 제공되는 Multi-View는 초기 "단순 2계층(PGM + PlayerCAM)" 구조에서 **3계층 동적 구조(PGM → 피처 테이블 → PlayerCAM)**로 진화했습니다.

이 문서는 그 진화의 논리적 근거, GG POKER 방송 특성 반영, 그리고 각 계층별 역할과 동적 레이아웃 설계를 상세히 설명합니다.

### 구조 비교 개요도

![3-Layer Structure](../images/PRD-0002/multiview-3layer-structure.png)

[HTML 원본](../mockups/PRD-0002/multiview-3layer-structure.html)

---

## 1. Michael 원안 분석: "PlayerCAM 스타일의 2계층 구조"

### 1.1 원문

```
Multi-view 영상: 메인화면이 중앙에 있고, 각 유저들의 얼굴을 잡고 있는 화면이 옆에 또 있는 방식
(아이돌 PlayerCAM 카메라)
```

**출처**: `docs/order/michael_note.md` (Michael, WSOPTV 크리에이티브 디렉터)

### 1.2 원안의 구조: 2계층 구성

Michael의 원안은 **아이돌 PlayerCAM 방식**을 벤치마크한 단순한 2계층 구조였습니다.

**계층 구조**:
| 레벨 | 설명 | 수량 |
|------|------|------|
| **Level 1 (메인)** | PGM (PD 연출 화면) | 1개 |
| **Level 2 (사이드)** | 플레이어 PlayerCAM | n개 |

**특징**:
- 단순하고 직관적
- K-POP 아이돌 콘서트의 PlayerCAM 연출 스타일 차용
- 클릭하면 플레이어 PlayerCAM을 메인화면으로 전환 가능

### 1.3 원안의 가정과 GG POKER 방송 구조

원안이 암묵적으로 가정한 것들:

1. **방송 구조**: 하나의 테이블만 방송 (메인 테이블 고정)
   - **현실**: GG POKER PRODUCTION은 다중 Feature Table 운영 방식 - 라이브 방송 중 여러 테이블이 동시에 운영되며, PD가 상황에 따라 어느 테이블을 중계할지 선택하여 전환함
2. **PlayerCAM 지원**: 모든 플레이어가 PlayerCAM을 가진다
3. **레이아웃**: PGM(메인) + PlayerCAM들(사이드) 고정 구조
4. **상호작용**: 클릭으로 PGM ↔ PlayerCAM 전환만 가능

---

## 2. 원안의 한계와 3계층 필요성

GG POKER 방송의 실제 특성:

- 하나의 라이브 방송 중 **여러 개의 테이블이 동시에 운영**
- PD(연출)이 상황에 따라 어느 테이블을 중계할지 선택하여 전환
- 예: WSOP Main Event 중계 중 Feature Table A~D 동시 운영

### 2.1 원안의 한계점

원안의 2계층 구조는 **3가지 콘텐츠(PGM, 피처 테이블, PlayerCAM)를 동시에 표시할 수 없음**:

| 구성 | Level 1 (메인) | Level 2 (사이드) | 문제점 |
|------|---------------|-----------------|--------|
| 구성 1 | PGM | PlayerCAM들 | 다른 테이블 목록 표시 불가! |
| 구성 2 | PGM | 테이블 목록 | PlayerCAM 표시 공간 없음! |

**실제 필요 콘텐츠 3가지**: PGM + 피처 테이블 + PlayerCAM

> 위 개요도 이미지의 **2-LAYER vs 3-LAYER** 비교 참조

### 2.2 PlayerCAM 지원 불균형

GG POKER 방송의 현실:

- **High Roller 테이블**: PlayerCAM 지원 O (고액 게임이므로 다각도 촬영)
- **Main Event 테이블**: PlayerCAM 부분 지원 (모든 플레이어는 아님)
- **Low Buy-in 테이블**: PlayerCAM 지원 X (촬영 대상이 아님)

**필요한 처리**:
- PlayerCAM 지원 테이블: PlayerCAM 레이어 활성화 + 뱃지 표시
- PlayerCAM 비지원 테이블: 레이어 비활성화 + 명시적 안내

---

## 3. 3계층 구조로의 진화: 설계 근거

### 3.1 구조 정의

**3계층 동적 구조**:

| 계층 | 설명 | 수량 | 역할 | 언제 표시 |
|------|------|------|------|----------|
| **Layer 1: PGM** | PD 연출 메인 화면 | 1개 | 라이브 방송의 메인 콘텐츠 | 항상 |
| **Layer 2: 피처 테이블** | 동시 운영되는 다른 테이블 | n개 | 테이블 전환용 링크 | 항상 (사이드바) |
| **Layer 3: 플레이어 PlayerCAM** | 선택한 테이블의 PlayerCAM | n개 (테이블별) | 개인 플레이어 집중 시청용 | PlayerCAM 지원 테이블만 |

> 상세 구조는 위 **LAYER DETAILS** 이미지 참조

#### 시각적 레이어 구성

**Layer 1: PGM (메인 연출 화면)**

![Layer 1 PGM](../images/PRD-0002/multiview-layer1-pgm.png)

**Layer 2: 피처 테이블 (테이블 선택)**

![Layer 2 Table](../images/PRD-0002/multiview-layer2-table.png)

**Layer 3: PlayerCAM (개별 플레이어 포커스)**

![Layer 3 PlayerCAM](../images/PRD-0002/multiview-layer3-playercam.png)

### 3.2 각 계층의 역할

> 각 계층의 시각적 예시와 상세 설명은 아래 이미지 참조

#### Layer 1: PGM (Primary / Main)

**역할**: 라이브 방송의 메인 콘텐츠 - 현재 PD(연출)이 선택하여 중계 중인 테이블 또는 PGM 원본 화면 (예: 전체 홀 카메라)

**특징**:
- 가장 큰 화면 (메인)
- 항상 표시됨
- 시청자가 "메인" 클릭 시 복귀하는 기본 화면

#### Layer 2: 피처 테이블 (Feature Table)

**역할**: 테이블 전환을 위한 네비게이션 - 동시에 운영되는 다른 Feature Table들의 목록

**특징**:
- 사이드바에 배치 (일반적으로 좌측 또는 우측)
- 각 테이블을 썸네일로 표시
- 클릭 시 해당 테이블을 메인으로 전환

#### Layer 3: 플레이어 PlayerCAM (Player Fancam)

**역할**: 개별 플레이어 집중 시청 - Layer 2에서 선택한 테이블의 플레이어 개별 카메라

**특징**:
- Layer 2 테이블이 PlayerCAM을 지원할 때만 활성화
- PlayerCAM 미지원 테이블 선택 시 이 계층은 비활성화 또는 "PlayerCAM 없음" 메시지
- 클릭 시 해당 플레이어를 메인으로 전환

### 3.3 3계층이 필요한 이유: 유스케이스 시뮬레이션

#### 시나리오: WSOP Main Event 중계

아래 이미지에서 3가지 레이아웃 상태를 확인할 수 있습니다:

![Dynamic Layouts](../images/PRD-0002/dynamic-layouts.png)

[HTML 원본](../mockups/PRD-0002/dynamic-layouts.html)

| 사용자 행동 | 레이아웃 전환 | 결과 |
|------------|--------------|------|
| **초기 진입** | Layout A | PGM 메인 + 피처 테이블 사이드바, PlayerCAM 비활성 |
| **테이블 클릭** | A → B | 선택 테이블 메인 + PGM/PlayerCAM 사이드바 |
| **PlayerCAM 클릭** | B → C | 플레이어 클로즈업 메인 + PGM/테이블/다른CAM 사이드바 |
| **PlayerCAM 미지원 테이블** | A → B | 테이블 메인 + "PlayerCAM 없음" 안내 |

---

## 4. 동적 레이아웃 설계

> 상세 레이아웃 시각화는 **섹션 3.3 이미지** 참조

### 4.1 레이아웃의 원칙

**원칙 1: 메인에 보이는 콘텐츠에 따라 사이드바가 동적으로 재배치**

| 메인 콘텐츠 | 사이드바 구성 |
|------------|--------------|
| **PGM** | 피처 테이블들 + PlayerCAM 비활성 |
| **피처 테이블** | PGM 미니 + 다른 테이블들 + 해당 테이블 PlayerCAM들 |
| **PlayerCAM** | PGM 미니 + 피처 테이블들 + 다른 PlayerCAM들 |

**원칙 2: 항상 메인 콘텐츠 + 대기 콘텐츠 + (선택사항) 상세 콘텐츠 표시**

가로 3단 레이아웃: 좌측 사이드 | **메인 (선택된 콘텐츠)** | 우측 사이드

### 4.2 3가지 레이아웃 구성

| 레이아웃 | 트리거 | 메인 | 좌측 사이드 | 우측 사이드 |
|---------|--------|------|------------|------------|
| **A: PGM 메인** | 초기 진입, "PGM Main" 클릭 | PGM (PD 연출) | 피처 테이블들 | PlayerCAM 비활성 |
| **B: 테이블 메인** | 피처 테이블 클릭 | 선택 테이블 | PGM 미니 + 다른 테이블 | 해당 테이블 PlayerCAM들 |
| **C: PlayerCAM 메인** | PlayerCAM 클릭 | 선택 플레이어 클로즈업 | PGM 미니 + 테이블들 | 다른 PlayerCAM들 |

### 4.3 동적 레이아웃의 트리거

| 사용자 액션 | 현재 상태 | 전환 대상 | 결과 레이아웃 |
|-----------|---------|---------|-----------|
| 메인 PGM 클릭 | B 또는 C | → A | PGM 메인 + 테이블 사이드 |
| 피처 테이블 클릭 | A 또는 C | → B | 테이블 메인 + PGM/PlayerCAM 사이드 |
| 플레이어 PlayerCAM 클릭 | B 또는 A | → C | PlayerCAM 메인 + PGM/테이블 사이드 |
| "메인으로 돌아가기" 버튼 | B 또는 C | → A | PGM 메인 + 테이블 사이드 |

---

## 5. PlayerCAM 지원 여부 처리

### 5.1 문제: 모든 테이블이 PlayerCAM을 지원하지 않음

아래 이미지에서 PlayerCAM 뱃지 시스템의 전체 설계를 확인할 수 있습니다:

![PlayerCAM Badge System](../images/PRD-0002/playercam-badge-system.png)

[HTML 원본](../mockups/PRD-0002/playercam-badge-system.html)

### 5.2 해결책: PlayerCAM 뱃지

| 테이블 유형 | PlayerCAM 지원 | UI 표시 |
|------------|---------------|---------|
| **High Roller Table** | O | `PlayerCAM ●` 뱃지 |
| **Main Event Table A** | 부분 | 인기 플레이어만 뱃지 |
| **Main Event Table B** | X | 뱃지 없음, 점선 테두리 |
| **Side Event** | X | 뱃지 없음, 점선 테두리 |

**핵심 원칙**:
- PlayerCAM 뱃지를 지원 테이블에만 표시
- 시청자가 클릭 전에 지원 여부 확인 가능
- 미지원 테이블 선택 시 "PlayerCAM 없음" 안내 + PGM 복귀 버튼

---

## 6. 스포츠 스트리밍 서비스 비교

### 6.1 NBA TV / NBA League Pass

| 항목 | NBA TV | WSOPTV |
|------|--------|--------|
| Multi-view | 4 Court View | 3계층 동적 |
| Player Focus | Player Tracking | PlayerCAM |
| Stats | 실시간 통계 오버레이 | StatsView HUD |
| 특징 | 여러 경기 동시 시청 | 여러 테이블 동시 시청 |

**유사점**: 주요 경기(코트)와 개별 선수(플레이어)에 모두 접근 가능

**차이점**: NBA TV는 경기별 독립적 뷰, WSOPTV는 테이블 기반 계층적 구조

### 6.2 MLB TV

| 항목 | MLB TV | WSOPTV |
|------|--------|--------|
| Multi-view | Mosaic (4-8 games) | 3계층 동적 |
| Stats | Statcast 오버레이 | StatsView HUD |
| 특징 | 개별 경기 선택 | 개별 테이블 선택 |

**유사점**: 여러 스트림 동시 모니터링, 통계 기반 인사이트

**차이점**: MLB TV는 경기 중심, WSOPTV는 테이블과 플레이어 계층 모두 지원

### 6.3 F1 TV

| 항목 | F1 TV | WSOPTV |
|------|-------|--------|
| Multi-view | Main + Driver Cams | PGM + PlayerCAM |
| Driver Focus | 개별 드라이버 캠 | 개별 PlayerCAM |
| Stats | 실시간 텔레메트리 | StatsView HUD |
| 특징 | 20+ 스트림 동시 | n개 테이블 + PlayerCAM |

**유사점**: 메인 뷰(Main/PGM) + 개별 대상 포커스(Driver/Player), 기술 통계 제공

**차이점**: F1 TV는 경쟁자 중심, WSOPTV는 테이블 계층 추가

### 6.4 UFC Fight Pass

| 항목 | UFC Fight Pass | WSOPTV |
|------|---------------|--------|
| Multi-view | 제한적 | 3계층 동적 |
| Fighter Focus | 코너 캠 | PlayerCAM |
| Stats | 타격 통계 | 포커 HUD 통계 |

**유사점**: 메인 액션(경기/게임) + 개별 참가자 포커스

**차이점**: UFC는 선형 경기 구조, WSOPTV는 다중 테이블 병렬 구조

### 6.5 WSOPTV의 차별화 전략

| 차별화 포인트 | 설명 | 스포츠 유사사례 |
|--------------|------|----------------|
| **3계층 동적 구조** | 스포츠 중계와 달리 포커는 다중 테이블 운영이 핵심 | NBA Mosaic과 유사하나 더 깊은 계층화 |
| **PlayerCAM 선택적 활성화** | F1 TV의 Driver Cam과 유사하지만 테이블별 가용성 다름 | F1 TV Driver Selection |
| **StatsView HUD** | GGPoker DB 연동으로 더 상세한 플레이어 통계 제공 | MLB TV Statcast와 유사 |
| **Timeshift 지원** | 라이브 중 임의 지점으로 이동 가능 | 스포츠 서비스 표준 기능 |

**핵심 경쟁력**: 포커의 다중 테이블 운영 특성에 맞춘 **계층적 Multi-View** + **선택적 PlayerCAM** + **통계 기반 인사이트**

---

## 7. 기술적 고려사항

아래 이미지에서 기술적 고려사항의 상세 시각화를 확인할 수 있습니다:

![Technical & UX Flows](../images/PRD-0002/technical-ux-flows.png)

[HTML 원본](../mockups/PRD-0002/technical-ux-flows.html)

### 7.1 스트림 동기화

**문제**: 여러 스트림이 동시 표시될 때 동기화 필요 (오차: ±500ms 이하)

**해결책**: 서버 사이드 동기화 (타임코드 기반)

### 7.2 스트림 개수

| 구성 요소 | 개수 |
|----------|------|
| PGM | 1개 |
| 피처 테이블 | 3~5개 |
| PlayerCAM (테이블당) | 3~5개 |
| **총 스트림** | **최대 26개** |

**클라이언트 제한**: 동시 재생 최대 3~4개 (메인 + 사이드 2~3개)

### 7.3 어댑티브 비트레이트 (ABR)

| 위치 | 품질 | 우선순위 |
|------|------|----------|
| **메인** | 1080p | 높음 |
| **좌측 사이드** | 720p | 중간 |
| **우측 사이드** | 360p | 낮음 |

→ 총 대역폭 최적화

---

## 8. 사용자 경험 (UX) 관점

> UX 학습곡선 및 Progressive Disclosure 시각화는 **섹션 7 이미지** 하단 참조

### 8.1 학습곡선

**3계층 구조가 직관적인 이유**:

| 단계 | 계층 | 사용자 동기 | 설명 |
|------|------|------------|------|
| **1** | PGM | "메인 피드 보기" | 기본 모드 - 바로 시작 가능 |
| **2** | 피처 테이블 | "다른 테이블도 보고 싶어" | 호기심 → 사이드바 탐색 |
| **3** | PlayerCAM | "이 선수 반응이 궁금해" | 심화 → 개별 플레이어 집중 |

### 8.2 복잡도 관리

**Progressive Disclosure 원칙**:

| 사용자 수준 | 사용 계층 | 설명 |
|------------|----------|------|
| **초급** | L1만 | PGM만 시청 |
| **중급** | L1 + L2 | PGM + 피처 테이블 전환 |
| **고급** | L1 + L2 + L3 | 3계층 모두 활용 |

**핵심**: 필요할 때만 다음 계층을 노출하므로 초보자도 복잡하지 않음

---

## 9. 결론

### 9.1 3계층 구조의 정당성

| 측면 | 근거 |
|------|------|
| **방송 구조** | GG POKER는 다중 Feature Table 운영 방식 |
| **PlayerCAM 지원** | 모든 테이블이 PlayerCAM을 제공하지는 않음 |
| **동적 레이아웃** | 메인 콘텐츠 전환에 따라 사이드바 재배치 필요 |
| **사용자 니즈** | "특정 테이블", "특정 선수" 집중 시청 요구 |
| **UX 설계** | Progressive Disclosure로 학습곡선 완만 |

### 9.2 원안과의 차이점

| 원안 (2계층) | 개선안 (3계층) |
|----------|-----------|
| PGM + PlayerCAM | PGM + 피처 테이블 + PlayerCAM |
| 고정 레이아웃 | 동적 레이아웃 |
| 단일 테이블 가정 | 다중 테이블 지원 |
| 모든 PlayerCAM 가정 | PlayerCAM 지원 여부 표시 |

### 9.3 최종 권장사항

> **3계층 동적 Multi-View 구조를 Advanced Mode의 핵심 기능으로 채택**하여, WSOPTV가 경쟁 서비스 대비 차별화된 프리미엄 경험을 제공하도록 합니다.

---

## 10. 참고자료

| 문서 | 위치 | 설명 |
|------|------|------|
| Michael Note | `docs/order/michael_note.md` | 크리에이티브 디렉터 원안 |
| Michael Vision Analysis | `docs/order/michael_vision_analysis.md` | 원안 분석 및 해석 |
| PRD-0002 | `tasks/prds/PRD-0002-wsoptv-ott-platform-mvp.md` | MVP 스펙 (3계층 정의) |
| PRD-0006 | `tasks/prds/PRD-0006-advanced-mode.md` | Advanced Mode 상세 스펙 |

---

## 11. 승인 및 검토

| 역할 | 이름 | 날짜 | 서명 |
|------|------|------|------|
| 작성자 | Claude Code | 2026-01-16 | - |
| 기술 검토 | (대기 중) | - | - |
| PO 승인 | (대기 중) | - | - |

---

**문서 버전**: 1.0
**최종 수정**: 2026-01-16
**상태**: Draft
