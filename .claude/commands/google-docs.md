---
name: google-docs
description: Google Docs 문서 작성/변환/관리 통합 커맨드
---

# /google-docs - Google Docs 문서 관리

Markdown 문서를 Google Docs로 변환하고, 다이어그램을 삽입하며, 문서를 관리합니다.

## Usage

```
/google-docs <subcommand> [args] [options]

Subcommands:
  convert <file>       Markdown → Google Docs 변환
  diagram <html>       HTML 목업 → 이미지 캡처 → Docs 삽입
  upload <file>        기존 문서 업로드
  list                 생성된 문서 목록 조회
  sync <doc-id>        Google Docs → 로컬 동기화

Options:
  --folder ID          대상 폴더 ID (기본: 공유 폴더)
  --toc                목차 자동 생성
  --no-folder          폴더 이동 없이 내 드라이브에 생성
```

---

## 서브커맨드 상세

### /google-docs convert - Markdown 변환

Markdown 파일을 Google Docs로 변환합니다.

```bash
/google-docs convert tasks/prds/PRD-0001.md
/google-docs convert docs/guide.md --toc
/google-docs convert README.md --no-folder
```

**워크플로우**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Markdown 파일  │────▶│  Converter      │────▶│  Google Docs    │
│  (로컬)         │     │  (Python)       │     │  (게시용)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  docs/images/   │     │  Drive 이미지   │
│  (로컬 이미지)  │     │  (업로드됨)     │
└─────────────────┘     └─────────────────┘
```

**지원 마크다운 문법**:

| 문법 | 변환 결과 |
|------|----------|
| `# H1` ~ `###### H6` | 스타일링된 제목 (아이콘 자동 추가) |
| `**bold**` | 굵은 글씨 |
| `*italic*` | 기울임 |
| `` `code` `` | 인라인 코드 (빨간 텍스트 + 배경) |
| `[text](url)` | 하이퍼링크 |
| `- item` | 불릿 리스트 |
| `1. item` | 번호 리스트 |
| `- [ ]` / `- [x]` | 체크박스 |
| `> quote` | 인용문 (왼쪽 테두리) |
| ` ``` ` | 코드 블록 (언어 표시) |
| `\| a \| b \|` | 네이티브 테이블 |
| `![alt](path)` | 이미지 (Drive 업로드) |
| `---` | 수평선 |

**실행 명령**:

```powershell
python automation_feature_table/scripts/prd_to_google_docs.py <file> [--toc] [--folder ID]
```

**출력 예시**:

```
============================================================
PRD to Google Docs Converter (Optimized)
============================================================
파일 수: 1
폴더 ID: 1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW
============================================================

[FILE] PRD-0001-feature.md
  문서 생성됨: PRD-0001: 기능명
  ID: 1abc...xyz
  페이지 크기: A4 (210mm x 297mm)
  폴더로 이동됨
  Content added: 395 requests
  Tables filled: 25 tables
  Images inserted: 3 images
  [OK] https://docs.google.com/document/d/1abc.../edit
```

---

### /google-docs diagram - 다이어그램 캡처

HTML 목업을 이미지로 캡처하고 문서에 삽입합니다.

```bash
/google-docs diagram docs/mockups/architecture.html
/google-docs diagram docs/mockups/workflow.html --doc-id DOC_ID
```

**워크플로우**:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  HTML Mockup    │────▶│  Playwright     │────▶│  PNG 이미지     │
│  (540px 너비)   │     │  Screenshot     │     │  (캡처됨)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Google Docs    │
                                                │  (이미지 삽입)   │
                                                └─────────────────┘
```

**HTML 목업 규격**:

| 항목 | 값 | 설명 |
|------|-----|------|
| 캡처 대상 ID | `#capture-target` 또는 `#capture-area` | 필수 |
| 권장 너비 | 540px | 문서 삽입 최적화 |
| 최소 폰트 | 16px | 가독성 확보 |
| 배경색 | 흰색 | 문서 일관성 |

**캡처 명령**:

```powershell
# 요소만 캡처 (권장)
npx playwright screenshot docs/mockups/architecture.html docs/images/architecture.png --selector="#capture-target"

# 전체 화면 (비권장)
npx playwright screenshot docs/mockups/architecture.html docs/images/architecture.png
```

**템플릿 위치**:

| 템플릿 | 용도 |
|--------|------|
| `lib/google_docs/templates/architecture.html` | 시스템 아키텍처 |
| `lib/google_docs/templates/flowchart.html` | 프로세스 흐름도 |
| `lib/google_docs/templates/erd.html` | 데이터베이스 ERD |
| `lib/google_docs/templates/ui-mockup.html` | UI 목업 |

---

### /google-docs upload - 문서 업로드

기존 Markdown/텍스트 파일을 Google Docs에 업로드합니다.

```bash
/google-docs upload README.md
/google-docs upload docs/API.md --folder FOLDER_ID
```

---

### /google-docs list - 문서 목록

생성된 Google Docs 문서 목록을 조회합니다.

```bash
/google-docs list
/google-docs list --folder FOLDER_ID
```

**출력 예시**:

```
Google Docs 문서 목록 (3개)
============================================================
[1] PRD-0001: 포커 핸드 자동 캡처
    URL: https://docs.google.com/document/d/1abc.../edit
    Updated: 2025-12-25

[2] PRD-0002: User Authentication
    URL: https://docs.google.com/document/d/2def.../edit
    Updated: 2025-12-24

[3] API Documentation
    URL: https://docs.google.com/document/d/3ghi.../edit
    Updated: 2025-12-23
============================================================
```

---

### /google-docs sync - 동기화

Google Docs 내용을 로컬로 동기화합니다.

```bash
/google-docs sync DOC_ID
/google-docs sync DOC_ID --output docs/synced.md
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

### PRD 변환 전체 워크플로우

```bash
# 1. HTML 목업으로 다이어그램 작성
# docs/mockups/prd-architecture.html

# 2. 다이어그램 캡처
/google-docs diagram docs/mockups/prd-architecture.html

# 3. Markdown PRD에 이미지 참조 추가
# ![아키텍처](../../docs/images/prd-architecture.png)

# 4. Google Docs로 변환
/google-docs convert tasks/prds/PRD-0001.md --toc

# 결과:
# ✓ 문서 생성됨: PRD-0001: Feature Name
# ✓ 이미지 삽입됨: 3개
# ✓ https://docs.google.com/document/d/.../edit
```

### 배치 변환

```bash
# 모든 PRD 변환
/google-docs convert tasks/prds/*.md

# 특정 폴더의 문서들 변환
/google-docs convert docs/guides/*.md --folder NEW_FOLDER_ID
```

---

## 문제 해결

| 오류 | 원인 | 해결 |
|------|------|------|
| `token.json not found` | 인증 미완료 | 스크립트 실행 시 브라우저 인증 |
| `Folder move failed` | 폴더 권한 없음 | 폴더 공유 권한 확인 |
| `Image insert failed` | 이미지 경로 오류 | 절대 경로 또는 상대 경로 확인 |
| `Table fill failed` | 테이블 구조 오류 | 마크다운 테이블 문법 확인 |

---

## Related

- `/create prd` - PRD 생성 (대화형 질문 기반)
- `/prd-sync` - PRD 동기화 (Google Docs → 로컬)
- `/research web` - 웹 리서치 후 문서화
