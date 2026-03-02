---
name: mockup-hybrid
description: >
  3-Tier 하이브리드 목업 생성 시스템.
  Mermaid 다이어그램 + HTML 와이어프레임 + Google Stitch AI 자동 선택.
version: 2.0.0

triggers:
  keywords:
    - "mockup"
    - "/mockup"
    - "목업"
    - "와이어프레임"
    - "wireframe"
    - "ui mockup"
    - "다이어그램"
    - "diagram"
    - "mermaid"
  file_patterns:
    - "docs/mockups/*.html"
    - "docs/mockups/*.mermaid.md"
    - "docs/images/mockups/*.png"
  context:
    - "UI 디자인"
    - "화면 설계"
    - "프로토타입"
    - "시스템 구조"
    - "흐름도"

capabilities:
  - auto_backend_selection
  - mermaid_diagram_generation
  - html_wireframe_generation
  - stitch_api_integration
  - playwright_screenshot
  - fallback_handling

model_preference: sonnet

auto_trigger: true
---

# Mockup Hybrid Skill v2.0

3-Tier 자동 선택 목업 생성 시스템. `--mockup`만으로 최적의 시각화 방식을 자동 결정합니다.

## 동작 모드

### Mode 1: 문서 기반 (Document-Driven)
```
/auto --mockup docs/02-design/feature.md
      │
      ▼
┌─────────────────────────────────┐
│      Document Scanner           │
│  ## 헤딩 기준 섹션 분리 + 분류  │
│  NEED / SKIP / EXIST 판단      │
└─────────────────────────────────┘
      │
      ├─ NEED 섹션들 ──▶ 3-Tier Router ──▶ 일괄 생성
      ├─ EXIST 섹션   ──▶ 스킵 (--force 시 재생성)
      └─ SKIP 섹션    ──▶ 스킵 (서술형)
      │
      ▼
┌─────────────────────────────────┐
│      Document Embedder          │
│  Mermaid → 인라인 코드 블록    │
│  HTML    → ![](이미지 참조)    │
└─────────────────────────────────┘
```

### Mode 2: 단건 (Prompt-Driven)
```
/auto "요청" --mockup
      │
      ▼
  3-Tier Router
      ├─ 다이어그램 키워드 ──▶ Mermaid (~2초)
      ├─ UI/화면 키워드    ──▶ HTML Wireframe (~5초)
      └─ 고품질/발표 키워드 ─▶ Stitch AI (~15초)
```

## 자동 라우팅 규칙

### 우선순위

1. **강제 옵션** (사용자 명시)
   - `--mockup mermaid` → Mermaid 고정
   - `--mockup html` → HTML 고정
   - `--mockup hifi` → Stitch 고정

2. **키워드 감지** (자동)

| Tier | 키워드 | 출력 |
|:----:|--------|------|
| Mermaid | 흐름, 플로우, 시퀀스, API 호출, DB, 스키마, ER, 클래스, 아키텍처, 파이프라인, 상태, 워크플로우 | `.mermaid.md` |
| HTML | 화면, UI, 레이아웃, 페이지, 대시보드, 폼, 카드, 사이드바, 와이어프레임 | `.html` + `.png` |
| Stitch | 프레젠테이션, 고품질, 최종, 데모, 발표, 리뷰용, 이해관계자 | `.html` + `.png` (HiFi) |

3. **컨텍스트** — `--prd=PRD-NNNN` → Stitch, `--screens=3+` → HTML
4. **환경** — Stitch API 불가 → HTML
5. **기본값** → HTML

## Mermaid 다이어그램 타입

| 타입 | 트리거 | 용도 |
|------|--------|------|
| `flowchart` | 흐름, 프로세스, 파이프라인 | 워크플로우, 결정 트리 |
| `sequenceDiagram` | 시퀀스, API 호출, 통신, 인증 | API 흐름, 인증 플로우 |
| `erDiagram` | DB, 스키마, ER, 테이블 관계 | 데이터 모델 |
| `classDiagram` | 클래스, 인터페이스, 상속 | OOP 구조 |
| `stateDiagram-v2` | 상태, 상태 머신, 라이프사이클 | 상태 전이 |
| `gitGraph` | 브랜치, 커밋, 머지 | Git 전략 |

## 사용 예시

```bash
# 문서 기반 자동 목업 (핵심 기능)
/auto --mockup docs/02-design/auth.design.md
# → 문서 스캔 → 시각화 필요 섹션 자동 발견 → 일괄 생성 + 삽입

# 미리보기 (실제 수정 없이 어떤 목업이 생성될지 확인)
/auto --mockup docs/02-design/auth.design.md --dry-run

# 기존 목업도 재생성
/auto --mockup docs/02-design/auth.design.md --force

# 단건 자동 선택 (프롬프트 기반)
/auto "API 인증 흐름 설계" --mockup
/auto "대시보드 화면 설계" --mockup

# 강제 지정
/auto "시스템 구조" --mockup mermaid
/auto "로그인 화면" --mockup html
/auto "데모 페이지" --mockup hifi
```

## 출력 형식

```bash
# Mermaid 선택 시
📊 선택: Mermaid sequenceDiagram (이유: 다이어그램 키워드 감지)
✅ 생성: docs/mockups/인증흐름.mermaid.md

# HTML 선택 시
📝 선택: HTML Generator (이유: 기본값)
✅ 생성: docs/mockups/dashboard.html
📸 캡처: docs/images/mockups/dashboard.png

# Stitch 선택 시
🤖 선택: Stitch API (이유: 고품질 키워드 감지)
✅ 생성: docs/mockups/landing-hifi.html
📸 캡처: docs/images/mockups/landing-hifi.png
```

## 모듈 구조

```
.claude/skills/mockup-hybrid/
├── SKILL.md
├── adapters/
│   ├── mermaid_adapter.py      # Mermaid 코드 생성 (NEW)
│   ├── html_adapter.py         # HTML 와이어프레임 생성
│   └── stitch_adapter.py       # Stitch API 연동
├── core/
│   ├── analyzer.py             # 3-Tier 프롬프트 분석
│   ├── router.py               # 백엔드 라우팅
│   └── fallback_handler.py     # 폴백 처리
└── config/
    └── selection_rules.yaml    # 자동 선택 규칙 (v2.0)

lib/mockup_hybrid/
├── __init__.py                 # 타입 정의 (MERMAID 추가)
├── stitch_client.py            # Stitch API 클라이언트
└── export_utils.py             # 내보내기 유틸리티
```

## 환경 변수

```bash
# Google Stitch (무료 - 350 screens/월) — Tier 3 전용
STITCH_API_KEY=your-api-key
STITCH_API_BASE_URL=https://api.stitch.withgoogle.com/v1
```

## --bnw 모드 (designer 에이전트 내장 가이드라인 기반 모노크롬)

`--bnw`는 **B&W 스타일 제약**이며, HTML 강제 옵션이 아니다. 3-Tier 라우팅이 먼저 결정된다.

### 동작 방식

```
/auto "요청" --mockup --bnw
      │
      ▼
3-Tier 라우터 (키워드 기반 — 라우팅 우선)
      │
      ├─ 다이어그램 키워드 → Mermaid 생성
      │   (흐름, 시퀀스, API, DB, ER, 클래스, 상태, 아키텍처 등)
      │   → --bnw 무시 (Mermaid는 기본 흑백 계열)
      │
      └─ UI/화면 키워드 → designer 에이전트 (B&W 제약 주입)
              (화면, UI, 레이아웃, 페이지, 대시보드, 폼, 와이어프레임 등)
              │
              ├── 팔레트: #000, #1a1a1a, #2d2d2d, #666, #999, #e5e5e5, #f8f8f8, #fff
              ├── 아이콘 없음 (텍스트 레이블만, emoji/SVG/icon font 금지)
              ├── Roboto/Inter/Arial 금지 → 독창적 타이포그래피
              ├── 비대칭 레이아웃, 여백 리듬, 그리드 시스템 적용
              └── border, shadow, 배경 질감 허용 (색상 없이)
```

### 크기 및 텍스트 규칙 (필수 적용)

| 항목 | 규칙 |
|------|------|
| **최대 규격** | 너비 720px × 높이 1280px (`max-width: 720px; max-height: 1280px`) |
| **폰트 크기** | body 14px, caption 12px, 제목 최대 22px |
| **텍스트 우선** | 텍스트로 표현 가능한 요소는 이미지/SVG/아이콘 삽입 금지 — 레이블/텍스트로만 표현 |

### B&W 팔레트 규칙

| 용도 | 색상 |
|------|------|
| 주요 텍스트 | `#000`, `#1a1a1a` |
| 보조 텍스트 | `#2d2d2d`, `#666` |
| 비활성/플레이스홀더 | `#999` |
| 구분선/보더 | `#e5e5e5` |
| 배경 (밝은) | `#f8f8f8`, `#fff` |

### designer 에이전트 미사용 시 폴백

`designer` 에이전트를 사용할 수 없는 경우 `html_adapter.py`의 개선된 기본 템플릿으로 폴백:
- Google Fonts 독창적 선택 (`DM Serif Display` + `Space Mono`)
- 8px 기반 공간 시스템
- `box-shadow` + 세련된 보더

## 변경 로그

### v2.1.0 (2026-02-19)

**Features:**
- `--bnw` 복원 (frontend-design 에이전트 기반 모노크롬 디자인)
- B&W 팔레트 규칙 정의 (그레이스케일 #000~#fff만)
- `html_adapter.py` 폴백 템플릿 품질 개선 (Roboto 제거, 독창적 타이포그래피)

### v2.0.0 (2026-02-16)

**Features:**
- 3-Tier 자동 선택 (Mermaid/HTML/Stitch)
- Mermaid 다이어그램 어댑터 (6가지 다이어그램 타입)
- `--mockup`만으로 자동 라우팅
- `--mockup mermaid/html/hifi` 강제 지정 옵션

### v1.0.0 (2026-01-23)

- 초기 버전 (HTML + Stitch 2-tier)

## /auto 연동

`/auto --mockup` 실행 시 아래 워크플로우가 적용된다.

### Step 3.0.2: PNG 캡처 (Lead 직접 Bash 실행 -- designer 완료 후)

```bash
python -c "
import sys; sys.path.insert(0, 'C:/claude')
from pathlib import Path
from lib.mockup_hybrid.export_utils import capture_screenshot, get_output_paths
html_path = Path('docs/mockups/{name}.html')
_, img_path = get_output_paths('{name}')
result = capture_screenshot(html_path, img_path, auto_size=True)
print(f'CAPTURED: {result}' if result else 'CAPTURE_FAILED')
"
```

- 성공: `docs/images/mockups/{name}.png` 생성 -> Step 3.0.3 성공 경로
- 실패 (Playwright 미설치 등): `CAPTURE_FAILED` 출력 -> Step 3.0.3 폴백 경로

### Step 3.0.3: 문서 삽입 (Lead 직접 Edit 실행 -- 대상 문서가 있는 경우만)

- **캡처 성공 시**: `generate_markdown_embed()` 결과를 Edit로 대상 문서에 삽입
  - `![{name}](docs/images/mockups/{name}.png)` + `[HTML 원본](docs/mockups/{name}.html)`
- **캡처 실패 시 (CAPTURE_FAILED)**: HTML 링크로 폴백
  - `[{name} 목업](docs/mockups/{name}.html)` + 경고 메시지
- **대상 문서 없음**: 삽입 스킵 (HTML/PNG 파일만 생성된 상태로 완료)

### 금지 사항

- executor 또는 executor-high가 `docs/mockups/*.html`을 직접 Write하는 것은 금지
- UI 목업 생성 시 반드시 designer 에이전트 경유
- `--bnw`: HTML 목업의 스타일 제약만 (색상 없음). 자동 트리거 없음 -- 명시적 플래그 필수
