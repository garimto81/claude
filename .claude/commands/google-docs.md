---
name: google-docs
description: Google Docs 문서 작성/변환/관리 통합 커맨드 (A4 최적화)
---

# /google-docs - Google Docs 문서 관리

Markdown 문서를 분석하고 Google Docs에 최적화된 형식으로 변환합니다.

**단순 복사/붙여넣기가 아닌, 문서 구조를 분석하여 Google Docs 네이티브 기능을 활용합니다.**

## Usage

```
/google-docs <subcommand> [args] [options]

Subcommands:
  analyze <file>       문서 분석 및 최적화 제안
  convert <file>       Markdown → Google Docs 변환 (최적화 적용)
  diagram <html>       HTML 목업 → 이미지 캡처 → Docs 삽입
  upload <file>        기존 문서 업로드
  list                 생성된 문서 목록 조회
  sync <doc-id>        Google Docs → 로컬 동기화

Options:
  --folder ID          대상 폴더 ID (기본: 공유 폴더)
  --toc                목차 자동 생성
  --no-folder          폴더 이동 없이 내 드라이브에 생성
  --optimize           문서 분석 후 최적화 적용 (기본: true)
```

---

## 스킬 연동

이 커맨드는 `google-workspace` 스킬과 연동됩니다.

```
.claude/skills/google-workspace/SKILL.md
```

**연동 기능**:
- OAuth 2.0 인증 (`desktop_credentials.json`)
- Google Docs API 연동
- Google Drive 파일 업로드
- 공유 폴더 관리

---

## A4 세로 규격 (핵심)

모든 문서는 **A4 세로** 형식으로 생성됩니다.

```
┌─────────────────────────────────────────────────────────────┐
│  A4 세로 규격                                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  페이지 크기: 210mm × 297mm (595pt × 842pt)                  │
│                                                              │
│  여백: 좌우 각 15mm (42.5pt)                                 │
│                                                              │
│  ┌─────────────────────────────────────┐                    │
│  │  콘텐츠 영역: 180mm (18cm)           │ ← 최대 너비       │
│  │                                      │                    │
│  │  이미지: 최대 18cm (510pt)          │                    │
│  │  테이블: 최대 18cm (510pt)          │                    │
│  │  코드블록: 최대 18cm (510pt)        │                    │
│  │                                      │                    │
│  └─────────────────────────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| 항목 | 크기 | PT 값 |
|------|------|-------|
| 페이지 너비 | 210mm | 595pt |
| 페이지 높이 | 297mm | 842pt |
| 좌우 여백 | 15mm × 2 | 42.5pt × 2 |
| **콘텐츠 최대 너비** | **180mm (18cm)** | **510pt** |

---

## 서브커맨드 상세

### /google-docs analyze - 문서 분석 (NEW)

변환 전 문서를 분석하고 Google Docs 최적화 제안을 제공합니다.

```bash
/google-docs analyze tasks/prds/PRD-0001.md
/google-docs analyze docs/guide.md --verbose
```

**분석 항목**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Markdown 파일  │────▶│  구조 분석      │────▶│  최적화 제안    │
│  (입력)         │     │  (Pattern)      │     │  (Report)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │
         ▼                      ▼
┌───────────────────────────────────────────────────────────────┐
│  분석 요소                                                      │
├───────────────────────────────────────────────────────────────┤
│  1. 제목 계층 (H1-H6 구조 적정성)                               │
│  2. 테이블 복잡도 (열 수, 셀 내용 길이)                         │
│  3. 이미지 크기 (18cm 초과 여부)                                │
│  4. 코드 블록 길이 (페이지 분할 필요 여부)                      │
│  5. 리스트 깊이 (중첩 수준)                                     │
│  6. 인용문/콜아웃 패턴                                          │
└───────────────────────────────────────────────────────────────┘
```

**분석 출력 예시**:

```
============================================================
문서 분석 결과: PRD-0001-feature.md
============================================================

[구조]
  제목 계층: H1(1) → H2(5) → H3(12) ✓ 적정
  총 단어 수: 2,450
  예상 페이지: 8-10페이지

[테이블] 5개 발견
  ✓ 문서 정보 (2열) - 적정
  ⚠ 기능 목록 (6열) - 열 축소 권장 (최대 4열)
  ⚠ API 스펙 (5열) - 가로 스크롤 위험

[이미지] 3개 발견
  ✓ architecture.png (540px) - 적정
  ⚠ workflow.png (800px) - 18cm 초과, 리사이즈 필요

[코드 블록] 8개 발견
  ⚠ config.json (45줄) - 페이지 분할 위험

[최적화 제안]
  1. 6열 테이블 → 2개 테이블로 분리
  2. workflow.png → 510pt로 리사이즈
  3. config.json → 핵심 부분만 표시, 전체는 첨부

[예상 변환 품질]: 92/100
============================================================
```

---

### /google-docs convert - Markdown 변환 (최적화 적용)

문서를 분석하고 Google Docs에 최적화된 형식으로 변환합니다.

```bash
/google-docs convert tasks/prds/PRD-0001.md
/google-docs convert docs/guide.md --toc
/google-docs convert README.md --no-optimize  # 분석 없이 직접 변환
```

**최적화 워크플로우**:

```
┌─────────────────┐
│  Markdown 파일  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  1. 문서 분석   │────▶│  2. 최적화 적용 │
│  (구조 파악)    │     │  (자동 조정)    │
└─────────────────┘     └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  테이블 최적화  │     │  이미지 리사이즈│     │  코드블록 처리  │
│  (열 분배)      │     │  (18cm 제한)    │     │  (페이지 고려)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                        ┌─────────────────┐
                        │  Google Docs    │
                        │  (A4 세로)      │
                        └─────────────────┘
```

**최적화 처리 항목**:

| 요소 | 원본 | 최적화 처리 |
|------|------|-------------|
| **이미지** | 임의 크기 | 최대 18cm (510pt) 자동 조정 |
| **테이블** | 5열 이상 | 열 너비 균등 분배, 필요시 분할 제안 |
| **코드블록** | 50줄 이상 | 핵심부만 표시 + 전체 링크 |
| **제목** | 평면 구조 | 계층적 스타일 + 아이콘 자동 부여 |
| **리스트** | 3단계+ 중첩 | 2단계로 평탄화 제안 |

**실행 명령**:

```powershell
python automation_feature_table/scripts/prd_to_google_docs.py <file> [--toc] [--folder ID]
```

**출력 예시**:

```
============================================================
PRD to Google Docs Converter (Optimized for A4)
============================================================
파일: PRD-0001-feature.md
폴더 ID: 1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW
최적화: 활성화
============================================================

[ANALYZE] 문서 분석 중...
  구조: H1(1) H2(5) H3(12)
  테이블: 5개 (1개 최적화 필요)
  이미지: 3개 (1개 리사이즈)

[OPTIMIZE] 최적화 적용 중...
  ✓ 테이블 열 너비 조정 (18cm 기준)
  ✓ 이미지 리사이즈: workflow.png (800→510pt)
  ✓ 코드블록 처리: 8개

[CONVERT] Google Docs 생성 중...
  ✓ 문서 생성됨: PRD-0001: 기능명
  ✓ ID: 1abc...xyz
  ✓ 페이지 크기: A4 (210mm x 297mm)
  ✓ 폴더로 이동됨

[RESULT]
  Content added: 395 requests
  Tables filled: 5 tables (열 너비 최적화됨)
  Images inserted: 3 images (18cm 제한 적용)

  [OK] https://docs.google.com/document/d/1abc.../edit
============================================================
```

---

### /google-docs diagram - 다이어그램 캡처

HTML 목업을 이미지로 캡처하고 문서에 삽입합니다.

```bash
/google-docs diagram docs/mockups/architecture.html
/google-docs diagram docs/mockups/workflow.html --doc-id DOC_ID
```

**HTML 목업 규격 (A4 최적화)**:

| 항목 | 값 | 설명 |
|------|-----|------|
| 캡처 대상 ID | `#capture-target` 또는 `#capture-area` | 필수 |
| **권장 너비** | **510px (18cm)** | A4 콘텐츠 영역 맞춤 |
| 최소 폰트 | 16px | 가독성 확보 |
| 배경색 | 흰색 | 문서 일관성 |

**캡처 명령**:

```powershell
# 요소만 캡처 (510px 권장)
npx playwright screenshot docs/mockups/architecture.html docs/images/architecture.png --selector="#capture-target"
```

---

### /google-docs upload - 문서 업로드

```bash
/google-docs upload README.md
/google-docs upload docs/API.md --folder FOLDER_ID
```

---

### /google-docs list - 문서 목록

```bash
/google-docs list
/google-docs list --folder FOLDER_ID
```

---

### /google-docs sync - 동기화

```bash
/google-docs sync DOC_ID
/google-docs sync DOC_ID --output docs/synced.md
```

---

## Google Docs 최적화 전략

### 복사/붙여넣기 vs 네이티브 변환

| 항목 | 복사/붙여넣기 | 네이티브 변환 (이 커맨드) |
|------|--------------|-------------------------|
| 서식 유지 | 손실 발생 | 완벽 보존 |
| 테이블 | 깨짐 가능 | 네이티브 테이블 생성 |
| 이미지 | 링크 깨짐 | Drive 업로드 + 임베드 |
| 스타일 | 수동 적용 필요 | 자동 Notion 스타일 |
| 크기 제한 | 무시됨 | 18cm 자동 조정 |

### 최적화 제안 규칙

```
┌─────────────────────────────────────────────────────────────┐
│  Google Docs 최적화 규칙                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [테이블]                                                    │
│  • 열 수: 최대 4열 권장 (5열 이상 → 분할 제안)              │
│  • 셀 내용: 50자 이하 권장 (초과 시 줄바꿈 처리)            │
│  • 헤더: 볼드 + 배경색 (#F6F8FA)                            │
│                                                              │
│  [이미지]                                                    │
│  • 최대 너비: 18cm (510pt)                                  │
│  • 형식: PNG 권장 (투명 배경 지원)                          │
│  • 캡션: alt 텍스트 → 이미지 아래 설명                      │
│                                                              │
│  [코드블록]                                                  │
│  • 최대 줄: 30줄 권장 (초과 시 접기 또는 링크)              │
│  • 폰트: Consolas 13pt                                      │
│  • 배경: #F6F8FA (연한 회색)                                │
│                                                              │
│  [제목]                                                      │
│  • H1: 문서당 1개만                                         │
│  • H2: 주요 섹션 (아이콘 자동 추가)                         │
│  • H3: 하위 섹션                                            │
│  • H4-H6: 최소 사용                                         │
│                                                              │
│  [리스트]                                                    │
│  • 중첩: 최대 2단계 권장                                    │
│  • 항목: 한 줄에 80자 이하                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 스타일 시스템

### Notion 스타일 적용

Google Docs에 Notion 스타일의 깔끔한 디자인이 적용됩니다.

**색상 팔레트**:

| 용도 | 색상 | HEX |
|------|------|-----|
| 텍스트 Primary | 거의 검정 | `#1a1a1a` |
| 제목 Primary | GitHub Blue | `#0969DA` |
| 코드 배경 | 연한 회색 | `#F6F8FA` |
| 코드 텍스트 | 빨강 | `#CF222E` |
| 링크 | 파랑 | `#0969DA` |

**타이포그래피**:

| 레벨 | 크기 | 여백 (전/후) |
|------|------|-------------|
| H1 | 32pt | 48pt / 16pt |
| H2 | 24pt | 36pt / 12pt |
| H3 | 18pt | 28pt / 8pt |
| Body | 14pt | - / 8pt |
| Code | 13pt | 16pt / 16pt |

**섹션 아이콘 (자동 추가)**:

| 키워드 | 아이콘 |
|--------|--------|
| overview, introduction | 📋, 📝 |
| architecture, technical | 🏗️, ⚙️ |
| features, requirements | ✨, 📋 |
| workflow, process | 🔄, ⚡ |
| testing, security | 🧪, 🔒 |
| deployment | 🚢 |

---

## OAuth 인증

### 설정 파일

| 파일 | 경로 |
|------|------|
| Credentials | `D:\AI\claude01\json\desktop_credentials.json` |
| Token | `D:\AI\claude01\json\token.json` |

### 필요 권한

```python
SCOPES = [
    'https://www.googleapis.com/auth/documents',  # Docs 읽기/쓰기
    'https://www.googleapis.com/auth/drive'       # Drive 읽기/쓰기
]
```

---

## 공유 폴더

| 항목 | 값 |
|------|-----|
| 폴더 ID | `1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW` |
| URL | [Google AI Studio 폴더](https://drive.google.com/drive/folders/1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW) |

---

## 예제

### 분석 후 변환 워크플로우

```bash
# 1. 먼저 문서 분석
/google-docs analyze tasks/prds/PRD-0001.md

# 결과 확인 후:
# - 테이블 6열 → 분할 권장
# - 이미지 800px → 리사이즈 권장

# 2. 최적화 적용하여 변환
/google-docs convert tasks/prds/PRD-0001.md --toc

# 결과:
# ✓ 테이블 자동 분할됨
# ✓ 이미지 18cm로 조정됨
# ✓ https://docs.google.com/document/d/.../edit
```

### PRD 변환 전체 워크플로우

```bash
# 1. HTML 목업으로 다이어그램 작성 (510px 너비)
# docs/mockups/prd-architecture.html

# 2. 다이어그램 캡처
/google-docs diagram docs/mockups/prd-architecture.html

# 3. Markdown PRD에 이미지 참조 추가
# ![아키텍처](../../docs/images/prd-architecture.png)

# 4. Google Docs로 변환 (분석 + 최적화)
/google-docs convert tasks/prds/PRD-0001.md --toc

# 결과:
# ✓ 문서 분석됨: 구조 적정
# ✓ 이미지 최적화됨: 18cm 맞춤
# ✓ 테이블 최적화됨: 열 너비 균등
# ✓ https://docs.google.com/document/d/.../edit
```

---

## 문제 해결

| 오류 | 원인 | 해결 |
|------|------|------|
| `token.json not found` | 인증 미완료 | 스크립트 실행 시 브라우저 인증 |
| `Folder move failed` | 폴더 권한 없음 | 폴더 공유 권한 확인 |
| `Image insert failed` | 이미지 경로 오류 | 절대 경로 또는 상대 경로 확인 |
| `Table fill failed` | 테이블 구조 오류 | 마크다운 테이블 문법 확인 |
| `Image too wide` | 18cm 초과 | `--no-optimize`로 원본 유지 또는 이미지 수정 |

---

## Related

- `google-workspace` 스킬 - Google API 통합 (`.claude/skills/google-workspace/`)
- `/create prd` - PRD 생성 (대화형 질문 기반)
- `/prd-sync` - PRD 동기화 (Google Docs → 로컬)
- `/research web` - 웹 리서치 후 문서화
