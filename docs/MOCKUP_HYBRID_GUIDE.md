# Mockup Hybrid 가이드

**Version**: 1.0.0
**Last Updated**: 2026-01-23

HTML 와이어프레임과 Google Stitch API를 통합한 하이브리드 목업 생성 시스템입니다.

---

## 개요

`/mockup` 커맨드는 프롬프트를 분석하여 최적의 백엔드를 자동으로 선택합니다.

| 백엔드 | 특징 | 용도 |
|--------|------|------|
| **HTML** | 빠른 생성, 로컬 처리 | 구조 검토, 빠른 프로토타이핑 |
| **Stitch** | AI 생성 고품질 UI | 프레젠테이션, 이해관계자 리뷰 |

---

## 빠른 시작

```bash
# 기본 사용 (자동 선택)
/mockup "로그인 화면" --bnw

# 고품질 목업 (Stitch 자동 선택)
/mockup "대시보드 - 이해관계자 프레젠테이션" --bnw

# 강제 HTML
/mockup "화면" --bnw --force-html

# 강제 Stitch
/mockup "화면" --bnw --force-hifi
```

---

## 자동 선택 시스템

### 선택 흐름

```
/mockup "프롬프트" --bnw
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  1. 강제 옵션 확인                                   │
│     --force-html → HTML                             │
│     --force-hifi → Stitch (API 가능 시)             │
└─────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  2. 키워드 분석                                      │
│     "프레젠테이션", "고품질", "리뷰용" → Stitch      │
│     "빠른", "구조", "와이어프레임" → HTML           │
└─────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  3. 컨텍스트 분석                                    │
│     --prd=PRD-NNNN → Stitch (문서용 고품질)         │
│     --screens=3+ → HTML (빠른 생성)                 │
└─────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  4. 환경 검사                                        │
│     Stitch API 키 없음 → HTML                       │
│     Rate Limit 초과 → HTML                          │
└─────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────┐
│  5. 기본값: HTML (가장 빠름)                         │
└─────────────────────────────────────────────────────┘
```

### 선택 키워드

#### Stitch 트리거 (고품질 필요)

| 키워드 | 영문 |
|--------|------|
| 프레젠테이션 | presentation |
| 고품질 | high quality, hifi |
| 리뷰용 | review |
| 이해관계자 | stakeholder |
| 최종 | final |
| 공식 | official |
| 데모 | demo |
| 클라이언트 | client |

#### HTML 트리거 (빠른 생성)

| 키워드 | 영문 |
|--------|------|
| 빠른 | quick, fast |
| 구조 | structure |
| 와이어프레임 | wireframe |
| 초안 | draft |
| 스케치 | sketch |
| 테스트 | test |

---

## 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--bnw` | Black & White 모드 (기본) | `/mockup "화면" --bnw` |
| `--force-html` | 강제 HTML 생성 | `/mockup "화면" --force-html` |
| `--force-hifi` | 강제 Stitch 생성 | `/mockup "화면" --force-hifi` |
| `--screens=N` | 화면 수 (1-5) | `/mockup "화면" --screens=3` |
| `--prd=PRD-NNNN` | PRD 연결 | `/mockup "화면" --prd=PRD-0001` |
| `--flow` | 흐름도 포함 | `/mockup "화면" --flow` |

---

## 폴백 시스템

Stitch API 실패 시 자동으로 HTML로 폴백합니다.

### 폴백 조건

| 조건 | 동작 |
|------|------|
| API 키 없음 | HTML로 자동 전환 |
| Rate Limit 초과 | HTML로 자동 전환 |
| 네트워크 오류 | HTML로 자동 전환 |
| `--force-hifi` 사용 | 폴백 없이 오류 반환 |

### 폴백 출력 예시

```
⚠️ Stitch API 실패 → HTML로 폴백
📝 선택: HTML Generator (이유: 폴백)
✅ 생성: docs/mockups/dashboard.html
📸 캡처: docs/images/mockups/dashboard.png
```

---

## Google Stitch 설정

### 1. API 키 발급

1. https://stitch.withgoogle.com/ 접속
2. Google 계정으로 로그인
3. Settings → API Keys에서 키 생성

### 2. 환경 변수 설정

```bash
# .env 또는 시스템 환경변수
STITCH_API_KEY=your-api-key
STITCH_API_BASE_URL=https://api.stitch.withgoogle.com/v1  # 선택
```

### 3. 비용

| 항목 | 비용 | 월 한도 |
|------|:----:|---------|
| Standard Mode | **무료** | 350 screens/월 |
| Experimental Mode | **무료** | 50-200 screens/월 |

> **참고**: Google Labs 실험 단계로 현재 완전 무료. 향후 변경 가능성 있음.

---

## 출력 파일

### 파일 구조

```
docs/
├── mockups/
│   ├── login.html           # 기본 목업
│   ├── dashboard-hifi.html  # Stitch 생성 (suffix: -hifi)
│   └── PRD-0001/
│       └── auth-hifi.html   # PRD 연결 시
└── images/
    └── mockups/
        ├── login.png
        ├── dashboard-hifi.png
        └── PRD-0001/
            └── auth-hifi.png
```

### 파일명 규칙

| 백엔드 | 접미사 | 예시 |
|--------|--------|------|
| HTML | (없음) | `login.html` |
| Stitch | `-hifi` | `login-hifi.html` |
| 폴백 | (없음) | `login.html` |

---

## 사용 예시

### 기본 사용

```bash
# 단순 화면 → HTML 자동 선택
/mockup "로그인 화면" --bnw

# 출력:
# 📝 선택: HTML Generator (이유: 기본값)
# ✅ 생성: docs/mockups/로그인화면.html
# 📸 캡처: docs/images/mockups/로그인화면.png
```

### 고품질 목업

```bash
# 프레젠테이션용 → Stitch 자동 선택
/mockup "대시보드 - 이해관계자 프레젠테이션" --bnw

# 출력:
# 🤖 선택: Stitch API (이유: 고품질 키워드 감지)
# ✅ 생성: docs/mockups/대시보드-hifi.html
# 📸 캡처: docs/images/mockups/대시보드-hifi.png
```

### PRD 연결

```bash
# PRD 연결 → Stitch 자동 선택 + PRD 폴더
/mockup "인증 흐름" --bnw --prd=PRD-0001

# 출력:
# 🤖 선택: Stitch API (이유: PRD 연결)
# ✅ 생성: docs/mockups/PRD-0001/인증흐름-hifi.html
# 📸 캡처: docs/images/PRD-0001/인증흐름-hifi.png
```

### 강제 선택

```bash
# 고품질 키워드 있어도 HTML 강제
/mockup "프레젠테이션 화면" --bnw --force-html

# 출력:
# 📝 선택: HTML Generator (이유: 강제 HTML 옵션)
# ✅ 생성: docs/mockups/프레젠테이션화면.html
```

---

## 아키텍처

### 모듈 구조

```
.claude/skills/mockup-hybrid/
├── SKILL.md                    # 스킬 정의
├── adapters/
│   ├── __init__.py
│   ├── html_adapter.py         # HTML 와이어프레임 생성
│   └── stitch_adapter.py       # Stitch API 연동
├── core/
│   ├── __init__.py
│   ├── analyzer.py             # 프롬프트 분석 + 자동 선택
│   ├── router.py               # 백엔드 라우팅
│   └── fallback_handler.py     # Stitch → HTML 폴백
└── config/
    └── selection_rules.yaml    # 자동 선택 규칙

lib/mockup_hybrid/
├── __init__.py                 # 데이터 모델
├── stitch_client.py            # Stitch API 클라이언트
└── export_utils.py             # 내보내기 유틸리티
```

### 데이터 흐름

```
사용자 요청
    │
    ▼
┌───────────────────┐
│  DesignContext    │
│  Analyzer         │
│  (프롬프트 분석)  │
└───────────────────┘
    │
    ▼
┌───────────────────┐
│  MockupRouter     │
│  (백엔드 라우팅)  │
└───────────────────┘
    │
    ├──────────────────────┐
    ▼                      ▼
┌───────────┐       ┌───────────┐
│  HTML     │       │  Stitch   │
│  Adapter  │       │  Adapter  │
└───────────┘       └───────────┘
    │                      │
    │                      ▼
    │              ┌───────────┐
    │              │  Fallback │
    │              │  Handler  │
    │              └───────────┘
    │                      │
    └──────────────────────┘
                │
                ▼
        ┌───────────────┐
        │  ExportUtils  │
        │  (저장/캡처)  │
        └───────────────┘
```

---

## 문제 해결

### Stitch API 오류

```
❌ Stitch API 키가 설정되지 않았습니다.
```

**해결**: 환경변수 `STITCH_API_KEY` 설정

### Rate Limit 초과

```
❌ 월간 사용 한도를 초과했습니다.
```

**해결**: 다음 달까지 대기 또는 `--force-html` 사용

### 스크린샷 실패

```
❌ Playwright가 설치되지 않음
```

**해결**: `npx playwright install` 실행

---

## 관련 문서

| 문서 | 설명 |
|------|------|
| `.claude/commands/mockup.md` | 커맨드 정의 |
| `.claude/skills/mockup-hybrid/SKILL.md` | 스킬 정의 |
| `.claude/templates/mockup-wireframe.html` | HTML 템플릿 |
| `.claude/templates/mockup-hifi.html` | Hi-Fi 폴백 템플릿 |

---

## 변경 로그

### v1.0.0 (2026-01-23)

- 초기 버전 릴리스
- HTML + Stitch 하이브리드 지원
- 프롬프트 기반 자동 백엔드 선택
- Stitch → HTML 자동 폴백
