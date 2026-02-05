---
name: drive
description: >
  Google Drive 맥락 기반 정리 스킬. AI가 파일명, 내용, 폴더 구조를 분석하여
  의미적으로 분류하고 중복 제거, 버전 관리, 폴더 구조화를 수행합니다.
  단순 패턴 매칭이 아닌 문맥 이해 기반 정리.
version: 1.1.0

triggers:
  keywords:
    - "drive 정리"
    - "드라이브 정리"
    - "파일 정리"
    - "폴더 정리"
    - "중복 제거"
    - "버전 관리"
    - "drive cleanup"
    - "drive organize"
    - "구글 드라이브 정리"
  context:
    - "Drive 파일 분류"
    - "문서 정리"
    - "폴더 구조화"

capabilities:
  - semantic_analysis      # 파일명/내용 의미 분석
  - duplicate_detection    # 중복 파일 탐지
  - version_management     # 버전 아카이빙
  - folder_restructure     # 폴더 재구조화
  - project_classification # 프로젝트별 분류

model_preference: opus  # 의미 분석에 Opus 권장

auto_trigger: true
auto_execute: true  # /drive 호출 시 자동 실행
---

# Drive Organizer Skill

## ⚠️ 자동 실행 프로토콜 (CRITICAL)

**`/drive` 호출 시 아래 단계를 순서대로 자동 실행합니다.**

### Step 1: 현황 수집 (MANDATORY)

```bash
cd C:\claude && python -m lib.google_docs drive status --json
```

**출력 예시:**
```json
{
  "total_files": 150,
  "folders": {"WSOPTV": {...}, "EBS": {...}, "Archive": {...}},
  "duplicates": 12,
  "unorganized": 55
}
```

### Step 2: AI 분석 (Claude 직접 수행)

수집된 데이터를 분석하여:

1. **프로젝트 분류**: 파일명에서 프로젝트 키워드 추출
   - `WSOPTV`, `WSOP TV`, `PRD-0002` → WSOPTV 프로젝트
   - `EBS`, `PRD-0003` → EBS 프로젝트
   - 그 외 → Archive

2. **문서 유형 분류**:
   - `PRD-`, `Product Requirement` → `prds/`
   - `Executive Summary`, `요약` → `executive/`
   - `STRAT-`, `Strategy` → `strategy/`
   - `Analysis`, `분석` → `analysis/`

3. **버전/중복 감지**:
   - `v1`, `v2`, `v3` → 최신 버전만 유지
   - `(사본)`, `Copy of` → 원본 확인 후 아카이브
   - `최종`, `Final` → 최신 취급

4. **정리 계획 생성**:
   - 이동할 파일 목록
   - 생성할 폴더 구조
   - 아카이브할 구버전 목록

### Step 3: 사용자 확인 (AskUserQuestion 사용)

```
📁 Drive 정리 계획

분석 결과:
- 총 파일: 150개
- 중복 파일: 12그룹 (30개)
- 미분류 파일: 55개

제안 작업:
1. 중복 파일 제거: 30개 → 12개
2. 프로젝트별 분류: WSOPTV(24), EBS(4), Archive(55)
3. 버전 아카이브: 8개 문서의 구버전 → _versions/

진행할까요?
```

**AskUserQuestion 옵션:**
- "전체 실행 (권장)" - 모든 작업 수행
- "중복 제거만" - 중복 파일만 정리
- "분석만" - 실행 없이 결과 확인
- "취소" - 작업 중단

### Step 4: 실행 (승인 시)

```bash
# 중복 제거
cd C:\claude && python -m lib.google_docs drive duplicates --delete

# 폴더 구조 생성
cd C:\claude && python -m lib.google_docs drive init

# 파일 정리 (프로젝트별 이동)
cd C:\claude && python -m lib.google_docs drive organize
```

또는 Drive API 직접 호출:

```python
from lib.google_docs.auth import get_credentials, DEFAULT_FOLDER_ID
from lib.google_docs.drive_organizer import DriveOrganizer

creds = get_credentials()
organizer = DriveOrganizer(creds, DEFAULT_FOLDER_ID)

# 폴더 생성
organizer.create_folder("WSOPTV/prds", parent_id)

# 파일 이동
organizer.move_file(file_id, new_parent_id)
```

### Step 5: 결과 리포트

```
============================================================
Google Drive Cleanup Complete
============================================================

✅ 완료된 작업
- 중복 파일 삭제: 18개
- 폴더 생성: 5개
- 파일 이동: 32개
- 버전 아카이브: 8개

📁 최종 구조
WSOPTV/
├── documents/
│   ├── prds/ (6개)
│   ├── strategy/ (2개)
│   └── executive/ (1개)
└── images/ (3개)

🔗 Drive: https://drive.google.com/drive/folders/...
============================================================
```

---

## 옵션별 실행

| 명령 | 동작 |
|------|------|
| `/drive` | 전체 자동 실행 (분석 → 확인 → 실행) |
| `/drive --analyze` | 분석만 (실행 없음) |
| `/drive --folder "WSOPTV"` | 특정 폴더만 정리 |
| `/drive --dedupe` | 중복 제거만 |
| `/drive --archive` | 구버전 아카이브만 |

---

Google Drive를 **AI 맥락 분석** 기반으로 정리하는 스킬입니다.

---

## 🎯 핵심 차별점

| 기존 스크립트 방식 | 이 스킬 (AI 맥락 분석) |
|-------------------|----------------------|
| 파일명 패턴 매칭 (`PRD-*.md`) | **문서 제목/내용의 의미적 분석** |
| 하드코딩된 분류 규칙 | **맥락 기반 동적 분류** |
| 동일 파일명만 중복 감지 | **유사 제목/내용 기반 중복 감지** |
| 수동 폴더 구조 정의 | **프로젝트 분석 후 자동 제안** |

---

## 📋 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│                    Drive Organizer 워크플로우                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: 현황 분석 (Scan)                                   │
│     ├── Drive API로 전체 파일/폴더 수집                     │
│     ├── 파일 메타데이터 추출 (이름, 수정일, 크기)           │
│     └── 문서 제목/첫 페이지 내용 샘플링                     │
│                                                              │
│  Step 2: AI 의미 분석 (Analyze)                             │
│     ├── 파일명 → 프로젝트/카테고리 추론                     │
│     ├── 유사 문서 그룹핑 (제목 유사도 분석)                │
│     ├── 버전 관계 파악 (v1, v2, 사본, 최종 등)             │
│     └── 고아 파일 식별 (분류 불가 항목)                    │
│                                                              │
│  Step 3: 정리 계획 생성 (Plan)                              │
│     ├── 폴더 구조 제안 (프로젝트별)                        │
│     ├── 파일 이동 계획 (from → to)                         │
│     ├── 중복/구버전 아카이브 계획                          │
│     └── 사용자 확인 요청                                    │
│                                                              │
│  Step 4: 실행 (Execute)                                     │
│     ├── 폴더 구조 생성                                      │
│     ├── 파일 이동                                           │
│     ├── 구버전 → _versions/ 아카이브                       │
│     └── 결과 리포트 출력                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 사용법

### 기본 사용

```bash
# 전체 Drive 분석 및 정리 (자동 실행)
/drive

# 특정 폴더만 정리
/drive --folder "WSOPTV"

# 분석만 (실행 없이)
/drive --analyze

# 중복 제거만
/drive --dedupe

# 구버전 아카이브만
/drive --archive
```

### 대화형 사용

```
사용자: 드라이브 정리해줘
Claude: [Drive Organizer 활성화]

        현황 분석 중...

        📊 분석 결과:
        - 총 파일: 150개
        - 문서: 83개
        - 이미지: 67개

        🔍 발견된 패턴:
        1. WSOPTV 관련 문서 24개 (PRD, Executive Summary 등)
        2. EBS 관련 문서 4개
        3. 미분류 문서 55개

        📁 제안 폴더 구조:
        ├── WSOPTV/
        │   ├── prds/
        │   ├── strategy/
        │   └── analysis/
        ├── EBS/
        │   └── documents/
        └── Archive/

        이 구조로 정리할까요?
```

---

## 🧠 AI 분석 로직

### 1. 프로젝트 추론

파일명에서 프로젝트를 자동 추론합니다:

| 파일명 패턴 | 추론 프로젝트 |
|------------|--------------|
| `WSOPTV...`, `WSOP TV...`, `PRD-0002...` | WSOPTV |
| `EBS...`, `PRD-0003...` | EBS |
| `GGP...`, `Heritage...` | GGP Heritage |
| 위에 해당 없음 | Archive |

### 2. 문서 유형 분류

| 파일명 키워드 | 분류 | 대상 폴더 |
|--------------|------|----------|
| `PRD-`, `Product Requirement` | PRD | `prds/` |
| `Executive Summary`, `요약` | 경영 요약 | `executive/` |
| `STRAT-`, `Strategy`, `전략` | 전략 문서 | `strategy/` |
| `Analyze`, `분석`, `Analysis` | 분석 문서 | `analysis/` |
| `Guide`, `가이드`, `Tutorial` | 가이드 | `guides/` |
| `Test`, `테스트`, `Draft` | 임시 문서 | `_archive/` |

### 3. 버전/중복 감지

| 패턴 | 의미 | 처리 |
|------|------|------|
| `v1`, `v2`, `v3` | 명시적 버전 | 최신만 유지, 나머지 archive |
| `(사본)`, `Copy of` | 복사본 | 원본 확인 후 archive |
| `최종`, `Final`, `완료` | 최종본 | 최신 취급 |
| `old`, `이전`, `백업` | 구버전 | archive |
| 동일 제목 + 다른 수정일 | 암묵적 중복 | 최신만 유지 |

---

## 📦 필요 인프라

### Python 모듈

```python
# 이미 존재하는 모듈 활용
from lib.google_docs.auth import get_credentials, DEFAULT_FOLDER_ID
from lib.google_docs.drive_organizer import DriveOrganizer  # 기존 모듈
```

### 기존 CLI 명령

```bash
# Drive 상태 확인
python -m lib.google_docs drive status

# 중복 파일 분석
python -m lib.google_docs drive duplicates

# 폴더 구조 생성
python -m lib.google_docs drive init

# 파일 정리
python -m lib.google_docs drive organize
```

---

## 🤖 에이전트 연동

이 스킬은 다음 에이전트와 연동됩니다:

| 에이전트 | 역할 | 사용 시점 |
|----------|------|----------|
| `oh-my-claudecode:analyst` | 파일 목록 의미 분석 | Step 2 |
| `oh-my-claudecode:architect` | 폴더 구조 설계 | Step 3 |
| `oh-my-claudecode:executor` | 정리 작업 실행 | Step 4 |

---

## 🔧 실행 규칙 (Claude가 따라야 할 프로토콜)

### Step 1: 현황 수집

```python
# Drive 파일 목록 수집
python -c "
from lib.google_docs.auth import get_credentials, DEFAULT_FOLDER_ID
from googleapiclient.discovery import build

creds = get_credentials()
drive = build('drive', 'v3', credentials=creds)

# 전체 파일 수집 (재귀)
def get_all_files(folder_id, path=''):
    query = f\"'{folder_id}' in parents and trashed=false\"
    results = drive.files().list(
        q=query,
        pageSize=200,
        fields='files(id, name, mimeType, modifiedTime, parents)'
    ).execute()
    # ... 재귀 처리
"
```

### Step 2: AI 분석

수집된 파일 목록을 Claude가 직접 분석합니다:

1. **프로젝트 그룹핑**: 파일명에서 프로젝트 키워드 추출
2. **유사 문서 그룹핑**: 제목 유사도 비교 (Levenshtein distance 또는 의미적 유사성)
3. **버전 관계 파악**: v1/v2, 사본, 최종 등 패턴 감지
4. **카테고리 분류**: PRD, 전략, 분석, 가이드 등

### Step 3: 계획 생성 및 사용자 확인

```
📁 정리 계획:

┌─────────────────────────────────────────────┐
│ 이동 계획 (15개 파일)                        │
├─────────────────────────────────────────────┤
│ WSOPTV/ (10개)                              │
│   ├─ prds/PRD-0002/ (2개)                   │
│   ├─ prds/PRD-0005/ (3개)                   │
│   ├─ prds/PRD-0006/ (1개)                   │
│   ├─ strategy/ (1개)                        │
│   ├─ executive/ (1개)                       │
│   └─ analysis/ (2개)                        │
│                                              │
│ _archive/ (5개)                              │
│   └─ _versions/ (중복/구버전)                │
└─────────────────────────────────────────────┘

계속 진행할까요? [Y/n]
```

### Step 4: 실행

사용자 승인 후 Drive API로 실제 정리 실행:

```python
# 폴더 생성
def create_folder(name, parent_id):
    # ...

# 파일 이동
def move_file(file_id, new_parent_id):
    # ...
```

---

## ⚠️ 주의사항

### 금지 행동

| 금지 | 이유 |
|------|------|
| ❌ 사용자 확인 없이 파일 삭제 | 데이터 손실 위험 |
| ❌ 원본 파일 직접 삭제 | Trash로 이동만 허용 |
| ❌ 공유 문서 권한 변경 | 협업 방해 |
| ❌ 루트 폴더 구조 임의 변경 | 사용자 승인 필수 |

### 필수 행동

| 필수 | 설명 |
|------|------|
| ✅ 분석 결과 사용자 확인 | 계획 실행 전 승인 |
| ✅ 실행 결과 리포트 | 이동/아카이브된 파일 목록 |
| ✅ 롤백 가능성 안내 | Trash에서 복구 가능 안내 |
| ✅ 중요 파일 백업 권고 | 대규모 정리 전 |

---

## 📊 출력 형식

### 분석 결과

```
============================================================
Google Drive Analysis Report
============================================================

📊 현황 요약
- 총 파일: 150개
- 문서: 83개 (Google Docs: 75, Sheets: 5, Slides: 3)
- 이미지: 67개 (PNG: 50, JPG: 17)
- 폴더: 12개

🔍 프로젝트 분류
| 프로젝트 | 문서 | 이미지 | 비고 |
|----------|------|--------|------|
| WSOPTV | 24개 | 3개 | PRD 5개, Executive 1개 |
| EBS | 4개 | 0개 | PRD 2개 |
| Archive | 55개 | 64개 | 미분류/레거시 |

⚠️ 발견된 문제
1. 중복 파일 12그룹 (30개 초과 파일)
2. 버전 관리 필요 문서 8개
3. 고아 폴더 3개 (빈 폴더)
4. 미분류 파일 55개

💡 추천 액션
1. /drive-organizer --dedupe : 중복 제거
2. /drive-organizer --archive-versions : 구버전 아카이브
3. /drive-organizer --restructure : 폴더 재구조화
```

### 실행 결과

```
============================================================
Google Drive Cleanup Complete
============================================================

✅ 완료된 작업
- 폴더 생성: 8개
- 파일 이동: 45개
- 버전 아카이브: 12개
- 빈 폴더 삭제: 3개

📁 최종 구조
WSOPTV/
├── documents/
│   ├── prds/ (6개)
│   ├── strategy/ (1개)
│   ├── executive/ (1개)
│   └── analysis/ (2개)
└── images/ (3개)

EBS/
└── documents/ (4개)

Archive/
├── documents/ (55개)
├── images/ (64개)
└── _versions/ (12개)

🔗 Drive: https://drive.google.com/drive/folders/1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW
```

---

## 🔗 관련 스킬

| 스킬 | 관계 |
|------|------|
| `google-workspace` | 기반 인프라 (인증, API) |
| `prd-sync` | PRD 문서 동기화 |

---

## 변경 로그

### v1.1.0 (2026-02-03)

**Auto-Execute 기능 추가:**
- `/drive` 호출 시 자동 실행 프로토콜 추가
- Step 1-5 자동화된 워크플로우
- AskUserQuestion 기반 사용자 확인
- 옵션별 분기 처리 (`--analyze`, `--dedupe`, `--archive`, `--folder`)

### v1.0.0 (2026-02-03)

**Initial Release:**
- AI 맥락 분석 기반 파일 분류
- 프로젝트별 자동 그룹핑
- 유사 문서 중복 감지
- 버전 관리 자동화
- 사용자 확인 기반 안전한 실행
