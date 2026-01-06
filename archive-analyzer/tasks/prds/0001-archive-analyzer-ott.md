# PRD-0001: Archive Analyzer for OTT Solution

## 1. Overview

### 1.1 배경 (Background)
GGP NAS 아카이브(`\\GGPWSOP\docker\GGPNAs\ARCHIVE`)에 저장된 미디어 파일들을 분석하여 B2C OTT 솔루션에 활용 가능한 형태로 정보를 정리해야 함.

### 1.2 아카이브 규모 (2025-11-27 스캔 결과)
- **총 파일 수**: 1,418개
- **총 용량**: 18.03 TB
- **로컬 복사 불가** → 네트워크 직접 접근 필수

#### 파일 유형별 분포
| 유형 | 파일 수 | 용량 | 비율 |
|------|---------|------|------|
| 비디오 (video) | 1,271개 | 15.34 TB | 85.1% |
| 기타 (other) | 147개 | 2.68 TB | 14.9% |

#### 기타 파일 상세 분석
| 확장자 | 파일 수 | 용량 | 설명 |
|--------|---------|------|------|
| .mxf | 126개 | 2,742 GB | 방송용 비디오 포맷 (→ video로 재분류 필요) |
| .part | 4개 | 2.95 GB | 미완료 다운로드 파일 |
| .zip | 1개 | 1.36 GB | 압축 파일 |
| .db | 13개 | < 1 MB | 데이터베이스 파일 |
| .pek | 2개 | < 1 MB | 오디오 피크 파일 |
| .xmp | 1개 | < 1 MB | Adobe 메타데이터 |

> **참고**: MXF (Material eXchange Format)는 프로페셔널 방송용 비디오 포맷으로, video 유형에 포함하면 실제 비디오 파일은 **1,397개 (18.02 TB)**

### 1.3 목적 (Purpose)
- 아카이브 내 모든 미디어 파일 및 메타데이터 파일 스캔
- OTT 서비스용 콘텐츠 카탈로그 생성
- 스트리밍에 필요한 기술 정보 추출

### 1.4 범위 (Scope)
| 포함 | 제외 |
|------|------|
| 비디오 파일 분석 (MP4, MKV, AVI 등) | 실시간 트랜스코딩 구현 |
| 메타데이터 파일 파싱 | DRM 시스템 구축 |
| 콘텐츠 카탈로그 JSON/DB 생성 | 실제 스트리밍 서버 구축 |
| 기술 사양 추출 (코덱, 해상도, 비트레이트) | CDN 연동 |

---

## 2. Requirements

### 2.1 기능 요구사항 (Functional Requirements)

#### FR-001: 아카이브 스캔
- **설명**: 지정된 네트워크 경로의 모든 하위 폴더 및 파일 탐색
- **입력**: 네트워크 경로 (`\\10.10.100.122\...` 또는 로컬 복사본)
- **출력**: 파일 목록 (경로, 크기, 수정일, 파일 유형)
- **우선순위**: P0 (필수)

#### FR-002: 미디어 메타데이터 추출
- **설명**: 비디오 파일에서 기술 정보 추출
- **추출 항목**:
  - 코덱 (비디오/오디오)
  - 해상도 (width x height)
  - 비트레이트
  - 재생 시간 (duration)
  - 프레임레이트
  - 오디오 채널/샘플레이트
- **도구**: FFprobe, MediaInfo
- **우선순위**: P0 (필수)

#### FR-003: 콘텐츠 정보 파싱
- **설명**: 메타데이터 파일(NFO, XML, JSON)에서 콘텐츠 정보 추출
- **추출 항목**:
  - 제목 (title)
  - 설명 (description)
  - 장르 (genre)
  - 출연진 (cast)
  - 제작년도 (year)
  - 썸네일/포스터 경로
  - 자막 파일 경로
- **우선순위**: P0 (필수)

#### FR-004: 카탈로그 생성
- **설명**: 추출된 정보를 OTT 서비스용 데이터 구조로 변환
- **출력 포맷**:
  ```json
  {
    "contents": [{
      "id": "uuid",
      "title": "콘텐츠 제목",
      "description": "설명",
      "genre": ["장르1", "장르2"],
      "duration": 7200,
      "thumbnail": "path/to/thumb.jpg",
      "streams": [{
        "quality": "1080p",
        "codec": "h264",
        "bitrate": 8000000,
        "path": "path/to/video.mp4"
      }],
      "subtitles": [{
        "language": "ko",
        "path": "path/to/sub.srt"
      }]
    }]
  }
  ```
- **우선순위**: P0 (필수)

#### FR-005: 분석 리포트 생성
- **설명**: 아카이브 전체 분석 결과 요약 리포트
- **포함 내용**:
  - 총 콘텐츠 수
  - 파일 유형별 통계
  - 해상도별 분포
  - 총 저장 용량
  - 스트리밍 적합성 평가
- **우선순위**: P1 (중요)

### 2.2 비기능 요구사항 (Non-Functional Requirements)

#### NFR-001: 성능
- 대용량 아카이브(10TB+) 처리 가능
- 병렬 처리로 분석 시간 최소화
- 진행률 표시 및 재개 기능

#### NFR-002: 확장성
- 새로운 파일 포맷 지원 용이
- 플러그인 방식의 메타데이터 파서

#### NFR-003: 신뢰성
- 분석 실패 시 로그 기록
- 부분 실패해도 전체 프로세스 계속 진행
- 결과 데이터 검증

---

## 3. Technical Specifications

### 3.1 기술 스택
| 구성요소 | 기술 | 이유 |
|----------|------|------|
| 언어 | Python 3.11+ | 풍부한 미디어 처리 라이브러리 |
| **SMB 클라이언트** | **aiosmb / smbprotocol** | **비동기 네트워크 접근, SMB 2/3 지원** |
| 미디어 분석 | FFprobe / pymediainfo | 산업 표준 도구 |
| 데이터 저장 | SQLite + JSON export | 로컬 실행, 이식성 |
| 파일 탐색 | aiosmb + asyncio | 비동기 대용량 처리 |

### 3.2 아키텍처
```
┌─────────────────────────────────────────────────────────────────┐
│                    Archive Analyzer v1.0                         │
├─────────────────────────────────────────────────────────────────┤
│  네트워크 계층                                                    │
│  ├── aiosmb (비동기 SMB 클라이언트) ─ 1차 권장                    │
│  └── smbprotocol (폴백용)                                        │
├─────────────────────────────────────────────────────────────────┤
│  분석 계층                                                        │
│  ├── FFprobe (비디오 기술 메타데이터)                             │
│  ├── pymediainfo (추가 미디어 정보)                               │
│  └── NFO/XML Parser (콘텐츠 메타데이터)                           │
├─────────────────────────────────────────────────────────────────┤
│  저장 계층                                                        │
│  ├── SQLite (로컬 DB)                                            │
│  └── JSON Export (OTT 백엔드용)                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 지원 파일 포맷
| 유형 | 확장자 |
|------|--------|
| 비디오 | .mp4, .mkv, .avi, .mov, .wmv, .flv, .webm, .mxf, .ts, .m2ts, .vob, .mpg |
| 오디오 | .mp3, .aac, .flac, .wav, .m4a, .ogg, .wma, .opus |
| 자막 | .srt, .ass, .ssa, .vtt, .sub, .idx, .smi |
| 메타데이터 | .nfo, .xml, .json, .yaml |
| 이미지 | .jpg, .png, .webp, .gif, .bmp (썸네일/포스터) |

---

## 4. Data Model

### 4.1 파일 테이블 (files)
```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    extension TEXT,
    size_bytes INTEGER,
    modified_at DATETIME,
    file_type TEXT, -- video, audio, subtitle, metadata, image
    parent_folder TEXT,
    scan_status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 미디어 정보 테이블 (media_info)
```sql
CREATE TABLE media_info (
    id INTEGER PRIMARY KEY,
    file_id INTEGER REFERENCES files(id),
    video_codec TEXT,
    audio_codec TEXT,
    width INTEGER,
    height INTEGER,
    duration_seconds REAL,
    bitrate INTEGER,
    framerate REAL,
    audio_channels INTEGER,
    audio_sample_rate INTEGER,
    container_format TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 콘텐츠 메타데이터 테이블 (content_metadata)
```sql
CREATE TABLE content_metadata (
    id INTEGER PRIMARY KEY,
    content_id TEXT UNIQUE,
    title TEXT,
    original_title TEXT,
    description TEXT,
    genre TEXT, -- JSON array
    cast TEXT,  -- JSON array
    director TEXT,
    year INTEGER,
    rating TEXT,
    thumbnail_path TEXT,
    poster_path TEXT,
    source_file TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. User Stories

### US-001: 아카이브 스캔
> **As a** 콘텐츠 관리자
> **I want to** 아카이브의 모든 파일을 자동으로 스캔하고 싶다
> **So that** 보유 콘텐츠를 파악할 수 있다

**Acceptance Criteria:**
- [ ] 지정 경로의 모든 하위 폴더 탐색
- [ ] 파일 유형별 자동 분류
- [ ] 스캔 진행률 표시
- [ ] 스캔 결과 저장

### US-002: 메타데이터 추출
> **As a** 콘텐츠 관리자
> **I want to** 비디오 파일의 기술 정보를 자동 추출하고 싶다
> **So that** 스트리밍 적합성을 평가할 수 있다

**Acceptance Criteria:**
- [ ] 코덱, 해상도, 비트레이트 추출
- [ ] 재생 시간 정보 추출
- [ ] 분석 실패 시 로그 기록

### US-003: 카탈로그 내보내기
> **As a** OTT 개발자
> **I want to** 분석 결과를 JSON 포맷으로 내보내고 싶다
> **So that** OTT 백엔드에서 바로 사용할 수 있다

**Acceptance Criteria:**
- [ ] 표준 JSON 스키마로 출력
- [ ] 콘텐츠별 스트림 정보 포함
- [ ] 자막/썸네일 경로 포함

---

## 6. Milestones

| 마일스톤 | 설명 | 산출물 |
|----------|------|--------|
| M1 | 기본 스캐너 구현 | 파일 목록 DB |
| M2 | 미디어 분석기 구현 | 기술 정보 추출 |
| M3 | 메타데이터 파서 구현 | 콘텐츠 정보 추출 |
| M4 | 카탈로그 생성기 구현 | JSON 카탈로그 |
| M5 | 리포트 생성기 구현 | 분석 리포트 |

---

## 7. Risks & Mitigations

| 리스크 | 영향 | 대응 방안 |
|--------|------|-----------|
| 네트워크 접속 불안정 | 스캔 중단 | 로컬 복사본 사용, 재개 기능 |
| 대용량 파일 처리 | 메모리 부족 | 스트리밍 방식 처리 |
| 다양한 메타데이터 포맷 | 파싱 실패 | 플러그인 파서, 폴백 로직 |
| 손상된 미디어 파일 | 분석 실패 | 에러 로깅, 건너뛰기 |

---

## 8. Success Metrics

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| 스캔 완료율 | 100% | 전체 파일 vs 스캔된 파일 |
| 메타데이터 추출률 | >95% | 분석 성공 vs 전체 미디어 파일 |
| 카탈로그 생성 | 유효한 JSON | JSON 스키마 검증 |
| 처리 속도 | >100 files/min | 처리량 측정 |

---

## Appendix

### A. 네트워크 접속 정보
- **서버**: 10.10.100.122 (GGPWSOP)
- **경로**: `\\GGPWSOP\docker\GGPNAs\ARCHIVE`
- **인증**: GGP / !@QW12qw

### B. 참조 문서
- FFprobe 공식 문서: https://ffmpeg.org/ffprobe.html
- MediaInfo 라이브러리: https://mediaarea.net/en/MediaInfo
- **smbprotocol (GitHub)**: https://github.com/jborean93/smbprotocol
- **aiosmb (GitHub)**: https://github.com/skelsec/aiosmb
- **ffprobe-python (GitHub)**: https://github.com/gbstack/ffprobe-python
- **Video-Metadata-Extractor (GitHub)**: https://github.com/CTinMich/Video-Metadata-Extractor

### D. 의존성 패키지
```bash
pip install smbprotocol aiosmb pymediainfo ffmpeg-python
```

### E. 용어 정의
| 용어 | 정의 |
|------|------|
| OTT | Over-The-Top, 인터넷 기반 미디어 스트리밍 서비스 |
| 카탈로그 | 콘텐츠 메타데이터 모음 |
| 트랜스코딩 | 미디어 포맷/코덱 변환 |

---

**작성일**: 2025-11-27
**수정일**: 2025-11-27
**작성자**: Claude (AI Assistant)
**버전**: 1.2.0

### Changelog
- **v1.2.0**: 실제 스캔 결과 반영 (1,418개/18.03TB), 파일 유형별 상세 분석 추가, MXF 포맷 지원 추가
- **v1.1.0**: 아카이브 규모 추가 (1869개/18TB), SMB 라이브러리 기술 스택 반영, 아키텍처 업데이트
- **v1.0.0**: 최초 작성

---

## Appendix F. 구현 진행 상황

### 완료된 이슈
| 이슈 | 설명 | 상태 |
|------|------|------|
| Issue #1 | SMB 네트워크 연결 테스트 | ✅ 완료 |
| Issue #2 | SMB 커넥터 모듈 구현 | ✅ 완료 |
| Issue #3 | 아카이브 파일 스캐너 구현 | ✅ 완료 |
| Issue #8 | 미디어 메타데이터 추출기 구현 | ✅ 완료 |

### 구현된 모듈
| 모듈 | 파일 | 설명 |
|------|------|------|
| SMB Connector | `smb_connector.py` | SMB 2/3 네트워크 연결 관리 |
| File Classifier | `file_classifier.py` | 파일 유형별 분류 |
| Database | `database.py` | SQLite DB 관리, files/media_info 테이블 |
| Scanner | `scanner.py` | 재귀적 디렉토리 스캔, 체크포인트 |
| Media Extractor | `media_extractor.py` | FFprobe 기반 메타데이터 추출 |

### 테스트 현황
- SMB Connector: 20개 테스트 통과
- Scanner: 21개 테스트 통과
- Media Extractor: 27개 테스트 통과
