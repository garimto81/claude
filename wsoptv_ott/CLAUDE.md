# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 프로젝트 개요

**WSOPTV OTT Platform** - WSOP(World Series of Poker) 공식 OTT 스트리밍 플랫폼

**현재 단계**: 기획/문서화 (코드 개발 전)

### 핵심 차별점 (vs YouTube)

| 기능 | YouTube | WSOPTV | Phase |
|------|---------|--------|:-----:|
| **Timeshift** | 불가 | 라이브 중 되감기 | MVP |
| **아카이브** | 비공개 | 영구 보존 | MVP |
| **Selected View** | 제한적 | 다중 생방송 중 선택 시청 | MVP |
| **Multi-video** | 없음 | 여러 플레이어 동시 재생 | 2+ |
| **StatsView** | 없음 | HUD 통계 오버레이 | 2+ |

### 용어 정의 (v13.0)

> 모든 문서에서 아래 용어만 사용합니다.

#### 핵심 개념

| 용어 | 정의 | Phase |
|------|------|:-----:|
| **Single Video** | 한 번에 하나의 비디오만 시청 | MVP |
| **Selected View** | 보고 싶은 방송을 선택해서 볼 수 있는 기능 | MVP |
| **Multi-video** | 여러 비디오 플레이어를 동시에 재생 | 2+ |
| **Timeshift** | 라이브 중 되감기 기능 | MVP |
| **StatsView** | 플레이어 통계 HUD 오버레이 | 2+ |

#### Selected View vs Multi-video (CRITICAL)

| 구분 | Selected View | Multi-video |
|:----:|---------------|------------|
| **정의** | 어떤 방송을 볼지 **선택** | 여러 방송을 **동시에** 재생 |
| **구현** | 기본 OTT 기능으로 충분 | 커스텀 플레이어 개발 필요 |
| **Phase** | **MVP** | **2+** |

> **핵심**: MVP에서는 Selected View만 구현하면 됨. 기본 OTT로 다중 생방송 선택 시청 가능.

---

## 명령어

### 목업 스크린샷 캡처

```powershell
# 최초 설치 (1회)
npx playwright install chromium

# 개별 목업 캡처
npx playwright screenshot docs/mockups/PRD-0002/feature-name.html docs/images/PRD-0002/feature-name.png

# 여러 목업 일괄 캡처 예시
npx playwright screenshot docs/mockups/PRD-0006/multiview-3layer.html docs/images/PRD-0006/multiview-3layer.png
```

### Google API 스크립트

```powershell
# Google Slides 읽기 (NBA TV 레퍼런스)
python C:\claude\wsoptv_ott\scripts\read_google_slides.py

# Google Slides 쓰기
python C:\claude\wsoptv_ott\scripts\write_google_slides.py

# 흑백 와이어프레임 생성
python C:\claude\wsoptv_ott\scripts\wsoptv_bw_wireframe.py
```

> **인증**: Google OAuth (Browser 기반). `C:\claude\json\desktop_credentials.json` 필요.

---

## 문서 체계 (Phase 기준)

> **MVP 원칙**: 최소 개발, 최단 시간 론칭 (Q3 2026)

### Phase별 문서 구조

```
docs/
├── phase0/          ← 론칭 전 결정 필수 (3개)
│   ├── 01-vision.md      Vision - 차별점 4가지
│   ├── 02-business.md    Business - 구독/생태계
│   └── 03-vendor-rfp.md  Vendor - Vimeo 선정
│
├── phase1/          ← MVP 구현 (2개)
│   ├── 01-mvp-spec.md    MVP 기획서 (NBA TV 스타일)
│   └── 02-content.md     콘텐츠 소싱
│
├── archive/         ← Phase 2+ 참조용
└── vible/           ← 원천 자료
```

### 핵심 문서 (5개)

| Phase | 문서 | 역할 | 파일 |
|:-----:|------|------|------|
| 0 | **01-vision** | 시청자 경험 비전 | `docs/phase0/01-vision.md` |
| 0 | **02-business** | GG 생태계 전략 | `docs/phase0/02-business.md` |
| 0 | **03-vendor-rfp** | Vimeo 선정 | `docs/phase0/03-vendor-rfp.md` |
| 1 | **01-mvp-spec** | MVP 기획서 ⭐ | `docs/phase1/01-mvp-spec.md` |
| 1 | **02-content** | 콘텐츠 소싱 | `docs/phase1/02-content.md` |

### 메인 인덱스

`docs/README.md` - Phase별 문서 인덱스

---

## 목업 워크플로우

### 디렉토리 구조

```
docs/mockups/PRD-NNNN/*.html   # HTML 목업 소스
docs/images/PRD-NNNN/*.png     # 캡처된 스크린샷
```

### 주요 목업 (PRD-0002)

| 목업 | 설명 |
|------|------|
| `01-three-pillars.html` | 4대 원천 다이어그램 |
| `04-multiview.html` | Multi-video 레이아웃 |
| `16-ovp-stream-architecture.html` | OVP/STREAM 이원화 아키텍처 |
| `27-streaming-architecture-v7.html` | Video Streaming Architecture v7 |

### 주요 목업 (PRD-0006)

| 목업 | 설명 |
|------|------|
| `multiview-3layer.html` | 3계층 Multi-video |
| `statsview-hud.html` | StatsView HUD 오버레이 |
| `4layer-standard.html` | 4계층 레이아웃 |

---

## DB 스키마

**위치**: `scripts/db/`

| 파일 | 내용 |
|------|------|
| `001_initial_schema.sql` | 핵심 테이블 (series, tournaments, events, players) |
| `002_additional_tables_and_constraints.sql` | 추가 테이블 및 제약조건 |

**설계 문서**: `docs/adrs/ADR-0002-database-schema-design.md`

---

## Google Docs 동기화

| 문서 | Google Docs ID | 버전 |
|------|----------------|------|
| **PRD-0002** (Concept Paper) | `1Y5KMRFunHJEXmR0MrXbb_flmf-_88obGnJBe0AC94_A` | v10.0 |
| **PRD-0002-executive-summary** | `1Y_GmF6AYOEkj7TEX3CptimlFVDEGZdssRysdzXHIQDs` | v7.0 |

**동기화 방법**: Google Docs 변경 시 로컬 PRD 수동 업데이트

**URL**:
- PRD-0002: https://docs.google.com/document/d/1Y5KMRFunHJEXmR0MrXbb_flmf-_88obGnJBe0AC94_A/edit
- Executive Summary: https://docs.google.com/document/d/1Y_GmF6AYOEkj7TEX3CptimlFVDEGZdssRysdzXHIQDs/edit

---

## 문서 명명 규칙

### Phase 문서 (활성)

```
phase{N}/{순번}-{역할}.md

예시:
phase0/01-vision.md      ← 시청자 비전
phase0/02-business.md    ← 비즈니스 모델
phase1/01-mvp-spec.md    ← MVP 기획서
phase1/02-content.md     ← 콘텐츠 소싱
```

### Archive 문서 (Phase 2+)

| 유형 | 접두사 | 예시 |
|------|--------|------|
| PRD | `PRD-NNNN` | `PRD-0002-wsoptv-concept-paper.md` |
| TECH | `TECH-NNNN` | `TECH-0001-streaming-infrastructure.md` |
| STRAT | `STRAT-NNNN` | `STRAT-0008-content-sourcing-architecture.md` |
| ADR | `ADR-NNNN` | `ADR-0001-multiview-3layer-rationale.md` |

---

## 프로젝트 관리 시스템

### 관리 문서 위치

`docs/management/` 디렉토리에서 프로젝트 진행 상태를 추적합니다.

| 시스템 | 파일 | 용도 |
|--------|------|------|
| 📧 메일 관리 | `EMAIL-LOG.md` | 업체별 이메일 커뮤니케이션 추적 |
| 💬 슬랙 관리 | `SLACK-LOG.md` | 의사결정/액션 아이템 추적 |
| 🏢 업체 관리 | `VENDOR-DASHBOARD.md` | RFP 진행 상태 대시보드 |
| 📄 기획 관리 | `DOCUMENT-TRACKER.md` | 문서 버전/동기화 관리 |

### Gmail/Slack 자동 동기화

```powershell
# 전체 동기화
python scripts/sync_management.py sync

# Slack만 (최근 7일)
python scripts/sync_management.py sync --slack --days 7

# Gmail만 (wsoptv 라벨)
python scripts/sync_management.py sync --gmail

# Dry-run (미리보기)
python scripts/sync_management.py sync --dry-run

# 상태 확인
python scripts/sync_management.py status
```

### 연동 설정

| 항목 | 값 | 설명 |
|------|-----|------|
| **Gmail 라벨** | `wsoptv` | 업체 이메일을 이 라벨로 분류 |
| **Slack 채널** | `C09TX3M1J2W` | WSOPTV 프로젝트 채널 |
| **인증** | Browser OAuth | `C:\claude\json\token_gmail.json`, `slack_token.json` |

### 동기화 스크립트 구조

```
scripts/
├── sync_management.py        # 메인 CLI (typer)
└── sync/
    ├── __init__.py
    ├── models.py             # 데이터 모델
    ├── slack_sync.py         # Slack → SLACK-LOG.md
    └── gmail_sync.py         # Gmail → EMAIL-LOG.md (준비 중)
```

---

## 업체 관리 현황

### 검토 중인 4개 업체

| 업체 | 상태 | 견적 | 평가 |
|------|:----:|------|:----:|
| **메가존** | 🟢 최우선 | 48억 + 15억/년 | 3.9/5.0 |
| **Brightcove** | ⚠️ 대기 | 견적 대기 | 미정 |
| **Vimeo** | 🔴 제외 | - | 매각 진행 |
| **맑음소프트** | 🔴 제외 | 1~2억 | P1 미충족 |

### 평가 템플릿

- `docs/templates/vendor-evaluation-matrix.md` - 대행사 평가 매트릭스
- `docs/templates/rfp-feedback-request-templates.md` - RFP 피드백 요청 양식

---

## 상위 규칙 상속

`C:\claude\CLAUDE.md` 규칙 적용:

- 언어: 한글 출력, 기술 용어 영어 유지
- 경로: 절대 경로 (`C:\claude\wsoptv_ott\...`)
- Git: Conventional Commit
