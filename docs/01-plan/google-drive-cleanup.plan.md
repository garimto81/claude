# Google Drive 정리 및 아카이빙 계획

**Version**: 1.0.0
**Date**: 2026-02-03
**Status**: Draft
**Author**: Claude + User

---

## 1. 현황 분석

### 1.1 현재 상태

| 항목 | 수치 | 문제점 |
|------|------|--------|
| **총 이미지 파일** | 200+ 개 | 루트 폴더에 정리 없이 존재 |
| **중복 파일** | 23종류, 100+개 | 동일 파일 최대 22개 중복 |
| **문서 파일** | 7개 | Google Docs/Sheets |
| **총 용량** | ~5.14 MB | 중복으로 인한 불필요 용량 |

### 1.2 중복 파일 상세

| 파일명 | 중복 수 | 원인 추정 |
|--------|---------|----------|
| `01-three-pillars.png` | 22개 | PRD 문서 반복 업로드 |
| `02-content-sourcing.png` | 22개 | PRD 문서 반복 업로드 |
| `03-subscription-plans.png` | 21개 | PRD 문서 반복 업로드 |
| `05-hand-search.png` | 21개 | PRD 문서 반복 업로드 |
| `04-multiview.png` | 15개 | PRD 문서 반복 업로드 |

### 1.3 파일명 패턴 분석

```
01-xxx.png  → 40개 (메인 화면/시작 관련)
02-xxx.png  → 40개 (콘텐츠/옵션 관련)
03-xxx.png  → 39개 (구독/오디오 관련)
04-xxx.png  → 44개 (멀티뷰 관련)
05-xxx.png  → 37개 (핸드 검색 관련)
```

---

## 2. 정리 전략

### 2.1 폴더 구조 설계

```
Google AI Studio (1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW)
├── 📁 documents/              # Google Docs, Sheets
│   ├── 📁 prds/               # PRD 문서
│   ├── 📁 guides/             # 가이드 문서
│   └── 📁 archives/           # 아카이브된 문서
│
├── 📁 images/                 # 이미지 자산
│   ├── 📁 prds/               # PRD 관련 이미지
│   │   ├── 📁 PRD-0001/
│   │   ├── 📁 PRD-0002/
│   │   └── 📁 PRD-0005/
│   ├── 📁 wireframes/         # 와이어프레임
│   ├── 📁 diagrams/           # 아키텍처 다이어그램
│   └── 📁 screenshots/        # 스크린샷
│
└── 📁 archives/               # 전체 아카이브
    ├── 📁 2026-Q1/            # 분기별 아카이브
    └── 📁 deprecated/         # 더 이상 사용 안 함
```

### 2.2 정리 단계

| 단계 | 작업 | 자동화 가능 |
|:----:|------|:----------:|
| 1 | 폴더 구조 생성 | ✅ |
| 2 | 중복 파일 식별 및 삭제 | ✅ |
| 3 | 파일 분류 및 이동 | ⚠️ 부분 |
| 4 | 기존 문서 링크 업데이트 | ❌ 수동 |
| 5 | 자동화 파이프라인 구축 | ✅ |

---

## 3. 구현 계획

### 3.1 Phase 1: 폴더 구조 생성 (자동화)

```python
# lib/google_docs/drive_organizer.py

def create_folder_structure():
    """Drive 폴더 구조 생성"""
    folders = {
        'documents': {
            'prds': {},
            'guides': {},
            'archives': {}
        },
        'images': {
            'prds': {},
            'wireframes': {},
            'diagrams': {},
            'screenshots': {}
        },
        'archives': {
            '2026-Q1': {},
            'deprecated': {}
        }
    }
    # ... 구현
```

### 3.2 Phase 2: 중복 파일 처리 (자동화)

**전략**: Hash 기반 중복 검출 + 최신 파일 유지

```python
def deduplicate_files(folder_id: str, dry_run: bool = True):
    """중복 파일 식별 및 삭제"""
    # 1. 파일명 기반 그룹화
    # 2. 각 그룹에서 최신 파일만 유지
    # 3. 나머지는 trash로 이동 (dry_run=False 시)
```

**예상 결과**:
- 중복 삭제 후: ~80개 고유 파일
- 용량 절감: ~3MB

### 3.3 Phase 3: 파일 분류 및 이동 (반자동)

**분류 규칙**:

| 파일명 패턴 | 대상 폴더 | 규칙 |
|------------|----------|------|
| `PRD-NNNN-*` | `images/prds/PRD-NNNN/` | PRD ID 추출 |
| `*-wireframe*`, `*-mockup*` | `images/wireframes/` | 키워드 매칭 |
| `*-diagram*`, `*-arch*` | `images/diagrams/` | 키워드 매칭 |
| `beginner-*` | `images/prds/tutorials/` | 튜토리얼 자료 |
| `NN-*` (숫자-) | `images/prds/general/` | 일반 PRD 이미지 |

### 3.4 Phase 4: 자동화 파이프라인 (신규)

**목표**: PRD 변환 시 이미지 자동 정리

```python
# lib/google_docs/converter.py 확장

def upload_image_organized(image_path: Path, prd_id: str = None):
    """이미지 업로드 시 자동 폴더 분류"""
    target_folder = get_target_folder(image_path, prd_id)
    # 중복 체크
    existing = check_duplicate(image_path, target_folder)
    if existing:
        return existing['id'], existing['url']
    # 새로 업로드
    return upload_to_drive(image_path, target_folder)
```

---

## 4. 아카이빙 전략

### 4.1 아카이브 정책

| 기준 | 정책 | 보관 기간 |
|------|------|----------|
| **활성 문서** | `documents/` 폴더 | 무기한 |
| **완료 PRD** | `archives/YYYY-QN/` | 1년 |
| **더 이상 사용 안 함** | `archives/deprecated/` | 6개월 후 삭제 검토 |
| **중복 파일** | 즉시 삭제 | - |

### 4.2 아카이브 자동화

```python
def archive_completed_prd(prd_id: str):
    """완료된 PRD 아카이브"""
    # 1. PRD 문서 이동
    # 2. 관련 이미지 이동
    # 3. 로컬 캐시 업데이트
    # 4. .prd-registry.json 업데이트
```

### 4.3 메타데이터 관리

**`.drive-registry.json`** (신규):

```json
{
  "version": "1.0.0",
  "folders": {
    "root": "1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW",
    "documents": "FOLDER_ID",
    "images": "FOLDER_ID",
    "archives": "FOLDER_ID"
  },
  "images": {
    "hash": {
      "abc123...": {
        "file_id": "FILE_ID",
        "name": "01-three-pillars.png",
        "folder": "images/prds/PRD-0002",
        "uploaded_at": "2026-02-03T10:00:00Z"
      }
    }
  }
}
```

---

## 5. 구현 우선순위

### 5.1 즉시 실행 (1-2일)

| 순서 | 작업 | 소요 시간 |
|:----:|------|:--------:|
| 1 | 폴더 구조 생성 | 30분 |
| 2 | 중복 파일 삭제 (dry-run 후 실행) | 1시간 |
| 3 | 기본 분류 스크립트 작성 | 2시간 |

### 5.2 단기 (1주)

| 순서 | 작업 | 소요 시간 |
|:----:|------|:--------:|
| 4 | `lib/google_docs/drive_organizer.py` 모듈 구현 | 4시간 |
| 5 | converter.py에 자동 분류 통합 | 2시간 |
| 6 | CLI 명령 추가 (`python -m lib.google_docs organize`) | 1시간 |

### 5.3 중기 (1개월)

| 순서 | 작업 | 소요 시간 |
|:----:|------|:--------:|
| 7 | Hash 기반 중복 검출 고도화 | 4시간 |
| 8 | 아카이브 자동화 스크립트 | 3시간 |
| 9 | 메타데이터 레지스트리 구현 | 4시간 |

---

## 6. CLI 명령 설계

### 6.1 명령 구조

```bash
# 현재 상태 분석
python -m lib.google_docs drive status

# 중복 파일 분석
python -m lib.google_docs drive duplicates
python -m lib.google_docs drive duplicates --delete  # 실제 삭제

# 폴더 구조 생성
python -m lib.google_docs drive init

# 파일 정리
python -m lib.google_docs drive organize
python -m lib.google_docs drive organize --dry-run  # 미리보기

# 아카이브
python -m lib.google_docs drive archive PRD-0001
```

### 6.2 예상 출력

```
$ python -m lib.google_docs drive status

Google Drive Status
============================================================
Folder: Google AI Studio (1JwdlUe_v4Ug...8hW)

Files:
  - Documents:  7 (Google Docs/Sheets)
  - Images:     200 (5.14 MB)
  - Others:     0

Issues:
  ⚠️  23 duplicate file groups detected
  ⚠️  No folder structure (all files in root)

Recommendations:
  1. Run 'drive duplicates --delete' to remove 150+ duplicates
  2. Run 'drive init' to create folder structure
  3. Run 'drive organize' to sort files
```

---

## 7. 리스크 및 완화

| 리스크 | 영향 | 완화 방안 |
|--------|------|----------|
| 잘못된 파일 삭제 | 높음 | dry-run 필수, trash 우선 이동 |
| 기존 문서 링크 깨짐 | 중간 | 이미지 ID 유지, 폴더만 이동 |
| API 할당량 초과 | 낮음 | 배치 처리, 백오프 |

---

## 8. 다음 단계

1. **사용자 승인** 후 Phase 1 실행 (폴더 생성)
2. **dry-run** 으로 중복 파일 목록 확인
3. **승인 후** 중복 파일 삭제 실행
4. **점진적** 파일 분류 진행

---

## 참조

- Google Drive API: https://developers.google.com/drive/api
- 현재 스킬: `.claude/skills/google-workspace/SKILL.md`
- 인증 설정: `C:\claude\json\desktop_credentials.json`
