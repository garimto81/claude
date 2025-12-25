---
name: google-docs
description: Google Docs 문서 작성 통합 파이프라인 (분석→캡처→변환→업로드 자동화)
---

# /google-docs - Google Docs 문서 생성 파이프라인

Markdown 문서를 분석하고, 다이어그램을 캡처하고, Google Docs로 변환하여 업로드하는 **전체 워크플로우를 자동 실행**합니다.

## 핵심 개념

**하나의 명령으로 모든 작업 완료** - 개별 단계를 따로 실행할 필요 없음

```
/google-docs tasks/prds/PRD-0001.md
```

위 명령 하나로:
1. ✓ 문서 구조 분석
2. ✓ HTML 목업 → 이미지 캡처
3. ✓ Markdown → Google Docs 변환
4. ✓ Drive에 업로드 완료

---

## Usage

```
/google-docs <file> [options]

기본 실행 (전체 파이프라인):
  /google-docs <file.md>              분석 → 캡처 → 변환 → 업로드 자동 실행

개별 단계 실행 (--step 옵션):
  /google-docs <file> --step=analyze  분석만 실행
  /google-docs <file> --step=diagram  다이어그램 캡처만 실행
  /google-docs <file> --step=convert  변환만 실행

유틸리티:
  /google-docs list                   생성된 문서 목록
  /google-docs sync <doc-id>          Docs → 로컬 동기화

Options:
  --step=STEP          특정 단계만 실행 (analyze|diagram|convert)
  --folder ID          대상 폴더 ID (기본: 공유 폴더)
  --toc                목차 자동 생성
  --no-optimize        최적화 없이 직접 변환
  --dry-run            실제 실행 없이 계획만 출력
```

---

## 자동 파이프라인

### 전체 워크플로우 (기본)

```
/google-docs tasks/prds/PRD-0001.md
```

**자동 실행 흐름**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  /google-docs <file.md>                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 1: ANALYZE (문서 분석)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  • 제목 계층 분석 (H1-H6)                                                   │
│  • 테이블 구조 검사 (열 수, 셀 길이)                                        │
│  • 이미지 경로 수집 및 크기 확인                                            │
│  • HTML 목업 참조 탐지 (docs/mockups/*.html)                                │
│  • 코드블록 길이 체크                                                       │
│                                                                              │
│  출력: 최적화 제안 리포트                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 2: DIAGRAM (다이어그램 캡처)                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  • HTML 목업 파일 탐지 (문서 내 참조 또는 연관 파일)                        │
│  • Playwright로 #capture-target 캡처                                        │
│  • 이미지 크기 조정 (최대 510px/18cm)                                       │
│  • docs/images/에 PNG 저장                                                  │
│                                                                              │
│  조건: HTML 목업이 없으면 이 단계 자동 스킵                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 3: CONVERT (변환 + 업로드)                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Markdown → Google Docs API 요청 생성                                     │
│  • 테이블 열 너비 18cm 맞춤                                                 │
│  • 이미지 Drive 업로드 + 문서 삽입                                          │
│  • Notion 스타일 적용 (색상, 폰트, 아이콘)                                  │
│  • A4 세로 페이지 설정                                                      │
│  • 공유 폴더로 이동                                                         │
│                                                                              │
│  출력: Google Docs URL                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  결과                                                                        │
│  ✓ https://docs.google.com/document/d/1abc.../edit                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 실행 예시

### 기본 실행 (전체 파이프라인)

```bash
/google-docs tasks/prds/PRD-0001-poker-hand.md

# 출력:
============================================================
Google Docs Pipeline
============================================================
입력: PRD-0001-poker-hand.md
모드: 전체 파이프라인 (analyze → diagram → convert)
============================================================

[Phase 1/3] ANALYZE
  ✓ 제목 계층: H1(1) H2(5) H3(12) - 적정
  ✓ 테이블: 5개 (열 너비 조정 예정)
  ✓ 이미지: 3개 (1개 리사이즈 필요)
  ✓ HTML 목업: 2개 발견
    - docs/mockups/prd-architecture.html
    - docs/mockups/prd-workflow.html

[Phase 2/3] DIAGRAM
  ✓ prd-architecture.html → prd-architecture.png (510px)
  ✓ prd-workflow.html → prd-workflow.png (510px)

[Phase 3/3] CONVERT
  ✓ 문서 생성: PRD-0001: 포커 핸드 자동 캡처
  ✓ 페이지: A4 세로 (210×297mm)
  ✓ 테이블: 5개 (18cm 맞춤)
  ✓ 이미지: 5개 삽입됨
  ✓ 폴더 이동 완료

============================================================
[OK] https://docs.google.com/document/d/1abc.../edit
============================================================
```

### Dry Run (계획만 확인)

```bash
/google-docs tasks/prds/PRD-0001.md --dry-run

# 실제 실행 없이 어떤 작업이 수행될지 미리 확인
```

### 특정 단계만 실행

```bash
# 분석만 실행
/google-docs tasks/prds/PRD-0001.md --step=analyze

# 다이어그램 캡처만 실행
/google-docs tasks/prds/PRD-0001.md --step=diagram

# 변환만 실행 (분석/캡처 스킵)
/google-docs tasks/prds/PRD-0001.md --step=convert
```

---

## 스킬 연동

이 커맨드는 `google-workspace` 스킬과 연동됩니다.

```
.claude/skills/google-workspace/SKILL.md
```

**연동 기능**:
- OAuth 2.0 인증 (`desktop_credentials.json`)
- Google Docs API
- Google Drive 업로드
- 공유 폴더 관리

---

## A4 세로 규격

모든 문서는 **A4 세로** 형식으로 생성됩니다.

```
┌─────────────────────────────────────────────────────────────┐
│  A4 세로 규격                                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  페이지: 210mm × 297mm                                       │
│  여백: 좌우 각 15mm                                          │
│                                                              │
│  ┌─────────────────────────────────────┐                    │
│  │  콘텐츠 최대 너비: 18cm (510pt)     │                    │
│  │                                      │                    │
│  │  • 이미지: 최대 18cm                │                    │
│  │  • 테이블: 최대 18cm                │                    │
│  │  • 코드블록: 최대 18cm              │                    │
│  └─────────────────────────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## HTML 목업 자동 탐지

파이프라인은 다음 위치에서 HTML 목업을 자동으로 찾습니다:

1. **문서 내 참조**: `![](docs/mockups/xxx.html)` 패턴
2. **연관 파일**: 문서명 기반 (예: `PRD-0001.md` → `prd-0001-*.html`)
3. **목업 디렉토리**: `docs/mockups/` 스캔

**HTML 목업 규격**:

| 항목 | 값 |
|------|-----|
| 캡처 대상 | `#capture-target` 또는 `#capture-area` |
| 권장 너비 | 510px (18cm) |
| 최소 폰트 | 16px |

---

## 최적화 규칙

파이프라인이 자동으로 적용하는 최적화:

| 요소 | 원본 | 자동 처리 |
|------|------|----------|
| **이미지** | 임의 크기 | 최대 510pt로 리사이즈 |
| **테이블** | 5열 이상 | 열 너비 균등 분배 |
| **코드블록** | 50줄 이상 | 경고 표시 |
| **제목** | 평면 | 아이콘 + 스타일 자동 부여 |

---

## 스타일 시스템

### Notion 스타일 자동 적용

| 레벨 | 크기 | 색상 |
|------|------|------|
| H1 | 32pt | GitHub Blue |
| H2 | 24pt | 진한 검정 + 아이콘 |
| H3 | 18pt | 진한 검정 |
| Body | 14pt | 거의 검정 |
| Code | 13pt | 빨강 + 회색 배경 |

### 섹션 아이콘 (자동)

| 키워드 | 아이콘 |
|--------|--------|
| overview, 개요 | 📋 |
| architecture, 아키텍처 | 🏗️ |
| features, 기능 | ✨ |
| workflow, 워크플로우 | 🔄 |
| testing, 테스트 | 🧪 |
| security, 보안 | 🔒 |

---

## OAuth 인증

| 파일 | 경로 |
|------|------|
| Credentials | `D:\AI\claude01\json\desktop_credentials.json` |
| Token | `D:\AI\claude01\json\token.json` |

---

## 공유 폴더

| 항목 | 값 |
|------|-----|
| 폴더 ID | `1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW` |
| URL | [Google AI Studio 폴더](https://drive.google.com/drive/folders/1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW) |

---

## 유틸리티

### 문서 목록 조회

```bash
/google-docs list
/google-docs list --folder FOLDER_ID
```

### 동기화 (Docs → 로컬)

```bash
/google-docs sync DOC_ID
/google-docs sync DOC_ID --output docs/synced.md
```

---

## 문제 해결

| 오류 | 해결 |
|------|------|
| `token.json not found` | 스크립트 실행 시 브라우저 인증 |
| `No HTML mockups found` | 정상 - diagram 단계 자동 스킵 |
| `Image too wide` | 자동 리사이즈됨 (18cm 제한) |
| `Table fill failed` | 마크다운 테이블 문법 확인 |

---

## 실행 명령 (내부)

```powershell
python automation_feature_table/scripts/prd_to_google_docs.py <file> [--toc] [--folder ID]
```

---

## Related

- `google-workspace` 스킬 - Google API 통합
- `/create prd` - PRD 생성 (대화형 질문 기반)
- `/prd-sync` - PRD 동기화
