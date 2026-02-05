# PRD-0001: Vimeo OTT Automation

**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-02-04
**Author**: WSOPTV Team

---

## 1. 개요

### 1.1 목적

WSOP 아카이브 콘텐츠를 Vimeo Enterprise에 자동으로 업로드하고 관리하는 시스템 구축

### 1.2 배경

- WSOPTV OTT 플랫폼이 Vimeo Enterprise를 비디오 호스팅 솔루션으로 선정
- 50년치 WSOP 아카이브 (1973-2024) 대량 이관 필요
- 수동 업로드의 비효율성 해결 필요

### 1.3 범위

| 포함 | 제외 |
|------|------|
| 비디오 업로드 자동화 | 라이브 스트리밍 (별도 프로젝트) |
| 메타데이터 관리 | 플레이어 UI 개발 |
| 컬렉션 구성 | 결제/구독 시스템 |
| 분석 데이터 수집 | CDN 직접 관리 |

---

## 2. 요구사항

### 2.1 기능 요구사항

#### P0 (필수)

| ID | 기능 | 설명 |
|:--:|------|------|
| F-001 | OAuth 인증 | Browser 기반 OAuth 2.0 인증 |
| F-002 | 단일 비디오 업로드 | CLI로 개별 비디오 업로드 |
| F-003 | 업로드 상태 확인 | Transcoding 상태 모니터링 |
| F-004 | 비디오 목록 조회 | 계정 내 비디오 목록 확인 |

#### P1 (중요)

| ID | 기능 | 설명 |
|:--:|------|------|
| F-005 | 일괄 업로드 | 폴더 내 비디오 배치 업로드 |
| F-006 | 메타데이터 자동 태깅 | 파일명/경로에서 정보 추출 |
| F-007 | 컬렉션 자동 구성 | Series/Season별 그룹핑 |
| F-008 | 업로드 이력 관리 | 중복 업로드 방지 |

#### P2 (선택)

| ID | 기능 | 설명 |
|:--:|------|------|
| F-009 | Webhook 수신 | Transcoding 완료 알림 |
| F-010 | 분석 데이터 수집 | 조회수/시청 통계 API |
| F-011 | 썸네일 자동 생성 | 특정 프레임 추출 |
| F-012 | 챕터 자동 생성 | 핸드별 타임스탬프 |

### 2.2 비기능 요구사항

| 항목 | 요구사항 |
|------|----------|
| **성능** | 동시 5개 업로드 지원 |
| **안정성** | 업로드 실패 시 자동 재시도 (3회) |
| **보안** | API 키 미사용, OAuth만 허용 |
| **로깅** | 모든 작업 이력 JSON 로그 |

---

## 3. 아키텍처

### 3.1 시스템 구성

```
┌─────────────────────────────────────────────────────────────┐
│                    Vimeo OTT Automation                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   CLI Tool   │  │  Batch Job   │  │   Webhook    │      │
│  │  (upload)    │  │  (scheduler) │  │  (listener)  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           │                                  │
│                    ┌──────▼───────┐                         │
│                    │  Vimeo API   │                         │
│                    │   Client     │                         │
│                    └──────┬───────┘                         │
│                           │                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                   ┌────────▼────────┐
                   │ Vimeo Enterprise│
                   │     API 3.4     │
                   └─────────────────┘
```

### 3.2 데이터 흐름

```
로컬 비디오 파일
       │
       ▼
┌─────────────────┐
│ 메타데이터 추출  │ ← 파일명/경로 파싱
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vimeo Upload   │ ← TUS 프로토콜 (청크 업로드)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Transcoding   │ ← Vimeo 자동 처리
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  컬렉션 배치    │ ← 자동 그룹핑
└────────┬────────┘
         │
         ▼
    VOD 서비스
```

### 3.3 모듈 구조

```
scripts/vimeo/
├── __init__.py
├── auth.py              # OAuth 인증
├── client.py            # API 클라이언트 (TODO)
├── upload.py            # 업로드 기능 (TODO)
├── batch.py             # 일괄 업로드 (TODO)
├── metadata.py          # 메타데이터 관리 (TODO)
├── collections.py       # 컬렉션 관리 (TODO)
└── upload_poc.py        # POC (완료)
```

---

## 4. 데이터 모델

### 4.1 비디오 메타데이터

```python
@dataclass
class VideoMetadata:
    # 기본 정보
    title: str
    description: str

    # WSOP 특화
    series: str          # "WSOP", "WSOP Circuit", "WSOP Europe"
    year: int            # 1973-2024
    event_name: str      # "Main Event", "High Roller"
    event_number: int    # 1-99

    # 선수 정보
    players: list[str]   # 출연 선수 목록
    winner: str          # 우승자

    # Vimeo 설정
    privacy: str         # "anybody", "unlisted", "password"
    tags: list[str]      # 검색 태그

    # 추적
    source_path: str     # 원본 파일 경로
    vimeo_uri: str       # /videos/123456
```

### 4.2 업로드 상태

```python
class UploadStatus(Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    TRANSCODING = "transcoding"
    AVAILABLE = "available"
    FAILED = "failed"
```

### 4.3 업로드 이력 (JSON)

```json
{
  "uploads": [
    {
      "source_path": "Z:/WSOP/1973/WSOP - 1973.avi",
      "vimeo_uri": "/videos/1161388909",
      "vimeo_url": "https://vimeo.com/1161388909",
      "status": "available",
      "uploaded_at": "2026-02-03T10:44:39Z",
      "file_size_bytes": 763150336,
      "duration_seconds": 2849
    }
  ]
}
```

---

## 5. API 설계

### 5.1 CLI 명령어

```bash
# 인증
vimeo-ott auth [--force]

# 단일 업로드
vimeo-ott upload <file> [--title <title>] [--series <series>] [--year <year>]

# 일괄 업로드
vimeo-ott batch <folder> [--pattern "*.avi"] [--dry-run]

# 상태 확인
vimeo-ott status <video_id>

# 목록
vimeo-ott list [--limit <n>] [--status <status>]

# 컬렉션
vimeo-ott collection create <name>
vimeo-ott collection add <collection_id> <video_id>
```

### 5.2 Python API

```python
from vimeo_ott import VimeoOTT

# 클라이언트 초기화
client = VimeoOTT()

# 업로드
video = client.upload(
    file_path="video.mp4",
    metadata=VideoMetadata(
        title="WSOP 1973",
        series="WSOP",
        year=1973
    )
)

# 일괄 업로드
results = client.batch_upload(
    folder="Z:/WSOP/1973",
    pattern="*.avi"
)

# 컬렉션 생성
collection = client.create_collection("WSOP Classic (1973-2002)")
client.add_to_collection(collection.id, video.uri)
```

---

## 6. 구현 계획

### Phase 1: Foundation (현재)

| 작업 | 상태 | 담당 |
|------|:----:|------|
| OAuth 인증 | ✅ 완료 | - |
| 단일 업로드 POC | ✅ 완료 | - |
| 비디오 목록/정보 | ✅ 완료 | - |
| 프로젝트 분리 | ✅ 완료 | - |

### Phase 2: Core Features

| 작업 | 예상 | 우선순위 |
|------|:----:|:--------:|
| API 클라이언트 리팩토링 | - | P0 |
| 일괄 업로드 | - | P1 |
| 메타데이터 파싱 | - | P1 |
| 업로드 이력 관리 | - | P1 |

### Phase 3: Advanced

| 작업 | 예상 | 우선순위 |
|------|:----:|:--------:|
| 컬렉션 관리 | - | P2 |
| Webhook 수신 | - | P2 |
| 분석 데이터 | - | P2 |

---

## 7. 성공 지표

| 지표 | 목표 |
|------|------|
| 업로드 성공률 | 99% |
| 평균 업로드 속도 | 100 Mbps+ |
| 메타데이터 정확도 | 95% |
| 중복 업로드 | 0건 |

---

## 8. 리스크

| 리스크 | 영향 | 완화 방안 |
|--------|:----:|----------|
| Rate Limit 초과 | 중 | 요청 간격 조절, 지수 백오프 |
| Token 만료 | 중 | Refresh token 구현 |
| 대용량 파일 실패 | 중 | TUS 청크 업로드, 재시도 로직 |
| Vimeo 서비스 변경 | 저 | API 버전 고정, 추상화 레이어 |

---

## 9. 참고 문서

| 문서 | 링크 |
|------|------|
| Vimeo API Docs | https://developer.vimeo.com/api |
| PyVimeo SDK | https://github.com/vimeo/vimeo.py |
| WSOPTV PRD-0002 | `C:\claude\wsoptv_ott\docs\prds\PRD-0002-wsoptv-concept-paper.md` |
| WSOPTV PRD-0012 | `C:\claude\wsoptv_ott\docs\prds\PRD-0012-phase1-vimeo-nbatv-style.md` |

---

## Appendix A: WSOP 아카이브 구조

```
Z:\GGPNAs\ARCHIVE\WSOP\
├── WSOP Classic (1973 - 2002)/
│   ├── WSOP 1973/
│   │   └── WSOP - 1973.avi
│   ├── WSOP 1974/
│   └── ...
├── WSOP Modern (2003 - 2024)/
│   ├── 2003/
│   │   ├── Main Event/
│   │   ├── Event 01 - $500 Casino Employees/
│   │   └── ...
│   └── ...
└── WSOP Europe/
    └── ...
```

### 예상 콘텐츠 규모

| 시대 | 기간 | 예상 파일 수 | 예상 용량 |
|------|------|:-----------:|:---------:|
| Classic | 1973-2002 | ~100 | ~50 GB |
| Modern | 2003-2024 | ~2,000 | ~5 TB |
| Europe | 2007-2024 | ~500 | ~1 TB |
| **Total** | - | **~2,600** | **~6 TB** |

---

## Appendix B: Vimeo Enterprise 기능

| 기능 | 지원 | 비고 |
|------|:----:|------|
| 무제한 스토리지 | ✅ | 7 TB 할당 |
| Live Streaming API | ✅ | Enterprise 전용 |
| 화이트라벨 플레이어 | ✅ | 브랜딩 제거 가능 |
| 다운로드 링크 | ✅ | 원본 파일 접근 |
| 분석 API | ✅ | 상세 시청 통계 |
| SSO 통합 | ✅ | 기업 인증 연동 |
