# 미디어 아카이브 관리(MAM) 오픈소스 솔루션 조사 보고서

**조사 날짜**: 2025-12-01
**조사 목적**: 18TB+ 포커 방송 아카이브 관리를 위한 오픈소스 MAM 솔루션 평가
**주요 요구사항**: SMB/NAS 연동, 메타데이터 관리, 대용량 비디오 파일 지원

---

## 1. 주요 오픈소스 MAM/DAM 솔루션 비교표

| 솔루션 | 기술 스택 | GitHub Stars | 라이선스 | 메타데이터 | 파일 포맷 지원 | API | 스트리밍 | SMB/NAS 지원 |
|--------|----------|--------------|----------|-----------|--------------|-----|----------|-------------|
| **Pimcore** | PHP, Symfony, MySQL | ~3.7k ⭐ / 1.5k forks | GPLv3 (Community) | ✅ 고급 (220+ 포맷) | ✅ 광범위 | ✅ REST API | ⚠️ 제한적 | ✅ 가능 |
| **Telemeta** | Python, Django, TimeSide | ~100-200 ⭐ (추정) | AGPL v3 | ✅ 고급 (XMP, EXIF) | ✅ 비디오/오디오 | ✅ REST API | ✅ HTML5 Player | ⚠️ 수동 구현 |
| **Archivematica** | Python, Django, Gearman | ~500-700 ⭐ (추정) | AGPL v3 | ✅ OAIS 표준 | ✅ FFmpeg 기반 | ✅ REST API | ❌ 없음 (보존용) | ✅ 스토리지 서비스 |
| **Razuna** | Java, CFML (ColdFusion) | ~300 ⭐ (추정) | AGPL v3 / 상용 | ✅ XMP/IPTC/EXIF | ✅ 비디오/이미지/오디오 | ✅ REST API | ✅ 지원 | ✅ 클라우드 연동 |
| **AtroDAM** | PHP, MySQL/PostgreSQL | ~50-100 ⭐ (추정) | GPLv3 | ✅ 기본 제공 | ✅ 다양한 미디어 | ✅ API-centric | ⚠️ 제한적 | ⚠️ 수동 구성 |
| **ResourceSpace** | PHP, MySQL | SVN 기반 (GitHub 미러) | BSD-style (무료) | ✅ 고급 (IIIF, AI) | ✅ 모든 파일 타입 | ✅ REST API | ⚠️ 제한적 | ✅ 가능 |
| **OpenBroadcaster** | PHP, GStreamer, HTML5 | ~50-100 ⭐ (추정) | AGPL v3 | ✅ 방송 메타데이터 | ✅ 비디오/오디오 | ✅ REST API | ✅ GStreamer | ✅ 네트워크 공유 |

**범례**:
- ✅ 완전 지원 / 내장 기능
- ⚠️ 제한적 지원 / 추가 구성 필요
- ❌ 미지원 / 해당 없음

---

## 2. 솔루션별 상세 분석

### 2.1 Pimcore (엔터프라이즈급 통합 플랫폼)

**개요**: PIM/MDM/CDP/DAM/CMS를 통합한 엔터프라이즈 데이터 관리 플랫폼

**강점**:
- 220+ 파일 포맷 미리보기 지원
- Symfony 기반의 견고한 아키텍처
- 대규모 커뮤니티 (3.7k+ stars)
- 워크플로우 관리 고급 기능
- 얼굴 인식 등 AI 기능 내장

**약점**:
- DAM이 전체 플랫폼의 일부 (over-engineered 가능)
- PHP 기반 (Archive Analyzer는 Python)
- 학습 곡선이 가파름

**적합도**: ⭐⭐⭐☆☆ (엔터프라이즈 전체 솔루션이 필요한 경우)

---

### 2.2 Telemeta (민족음악학 특화 MAM)

**개요**: 오디오/비디오 아카이브 관리 및 협업 플랫폼 (Python/Django)

**강점**:
- **Python 기반** → Archive Analyzer와 통합 용이
- TimeSide 프레임워크 (FFmpeg, GStreamer 통합)
- HTML5 오디오/비디오 플레이어 내장
- 메타데이터 추출 및 트랜스코딩 자동화
- Docker 기반 배포 (Jupyter, ElasticSearch 포함)

**약점**:
- 민족음악학 중심 설계 (방송 워크플로우 맞춤화 필요)
- 커뮤니티 규모 작음
- 스포츠 방송 특화 기능 부족

**적합도**: ⭐⭐⭐⭐☆ (Python 생태계 통합 및 오디오/비디오 아카이브)

**SMB 통합 방법**: Django 기반이므로 `smbprotocol` 라이브러리로 Storage Backend 확장 가능

---

### 2.3 Archivematica (장기 디지털 보존)

**개요**: ISO-OAIS 표준 기반 디지털 보존 시스템 (Python/Django)

**강점**:
- **Python 기반** → 기존 코드베이스와 통합 가능
- 마이크로서비스 아키텍처
- FFmpeg, MediaInfo, BagIt 등 보존 도구 통합
- 포맷 정책 레지스트리 (FPR)
- 스토리지 서비스로 NAS/클라우드 연동

**약점**:
- **스트리밍 미지원** (보존용 AIP 생성 중심)
- 복잡한 설정 및 인프라 요구
- OTT 플랫폼보다는 아카이브 기관용

**적합도**: ⭐⭐⭐☆☆ (장기 보존이 최우선인 경우)

**SMB 통합 방법**: Storage Service에 SMB 백엔드 추가 가능

---

### 2.4 Razuna (클라우드 친화적 DAM)

**개요**: 클라우드 스토리지 통합에 강점을 둔 DAM (Java/CFML)

**강점**:
- 클라우드 스토리지 연동 (AWS S3, Azure 등)
- WordPress 플러그인 등 CMS 통합
- 비디오 포맷 변환 지원
- 전문 검색 (문서 전문 색인)

**약점**:
- **레거시 기술 스택** (ColdFusion/OpenBD)
- 메인 리포지토리 유지보수 중단 (razuna.com으로 전환)
- Java/CFML은 Python 환경과 이질적

**적합도**: ⭐⭐☆☆☆ (기술 스택 불일치, 유지보수 우려)

---

### 2.5 AtroDAM (차세대 경량 DAM)

**개요**: 신세대 오픈소스 DAM (PHP, SPA 아키텍처)

**강점**:
- API 중심 설계
- 단일 페이지 애플리케이션 (SPA)
- 경량 및 확장 가능
- GPLv3 (무료)

**약점**:
- 커뮤니티 규모 매우 작음
- 비디오 스트리밍 기능 제한적
- 방송/미디어 특화 기능 부족

**적합도**: ⭐⭐☆☆☆ (기본 DAM 필요 시)

---

### 2.6 ResourceSpace (교육/문화 기관 표준)

**개요**: 박물관, 도서관, 교육기관에서 널리 사용되는 DAM

**강점**:
- 성숙한 플랫폼 (수년간 개발)
- AI 검색 (OpenAI CLIP 통합)
- 자동 전사 (Whisper)
- IIIF API 지원
- 무료 라이선스

**약점**:
- SVN 기반 (GitHub는 미러)
- PHP 기반
- 방송 워크플로우 특화 기능 부족

**적합도**: ⭐⭐⭐☆☆ (문화/교육 콘텐츠 관리)

---

### 2.7 OpenBroadcaster (방송 자동화 특화)

**개요**: 라디오/TV 방송 자동화 및 MAM (PHP, GStreamer)

**강점**:
- **방송 워크플로우 특화**
- GStreamer 기반 플레이아웃
- 스케줄링 및 자동화
- IPTV 지원
- 원주민 언어 방송 커뮤니티 활발

**약점**:
- PHP 기반 (Python 통합 어려움)
- 소규모 커뮤니티
- OTT 스트리밍보다는 선형 방송용

**적합도**: ⭐⭐⭐☆☆ (방송 자동화 + MAM 통합 필요 시)

---

## 3. 보조 도구 (메타데이터 추출 전용)

| 도구 | 목적 | 기술 스택 | 라이선스 | Archive Analyzer 통합 |
|------|------|----------|----------|----------------------|
| **MediaInfo** | 메타데이터 분석 | C++ | BSD-2-Clause | ✅ 이미 사용 중 (FFprobe 대안) |
| **ExifTool** | 메타데이터 편집 | Perl | GPL/Artistic | ⚠️ 이미지 메타데이터용 |
| **QCTools** | 비디오 품질 관리 | C++, Qt, FFmpeg | GPLv3 | ⚠️ QC 워크플로우 추가 시 |
| **MediaConch** | 규격 적합성 검증 | C++ | BSD/GPLv3 | ⚠️ 규격 검증 필요 시 |
| **tinyMediaManager** | Kodi 메타데이터 | Java | Apache 2.0 | ❌ 다른 목적 (홈 미디어) |

---

## 4. SMB/NAS 통합 평가

### Python 생태계 (Archive Analyzer 호환)
- **smbprotocol**: Archive Analyzer에서 이미 사용 중 (SMB 2/3)
- **pysmb**: SMB 1/2 지원 (레거시)

### Node.js 생태계
- **@marsaud/smb2**: 실험 단계
- **samba-client**: smbclient 래퍼 (Linux 종속)
- **node-smb-server**: Adobe 개발 (SMB 서버 구현)

**결론**: Python 솔루션(Telemeta, Archivematica)이 기존 `smbprotocol` 통합으로 SMB 연동이 가장 자연스러움.

---

## 5. 기술 스택별 분류

### Python 기반 (Archive Analyzer와 통합 용이)
1. **Telemeta** - 오디오/비디오 아카이브 + 협업
2. **Archivematica** - 디지털 보존 (OAIS)

### PHP 기반 (별도 시스템 운영)
1. **Pimcore** - 엔터프라이즈 통합 플랫폼
2. **ResourceSpace** - 문화기관 DAM
3. **AtroDAM** - 경량 차세대 DAM
4. **OpenBroadcaster** - 방송 자동화

### Java/CFML 기반 (레거시)
1. **Razuna** - 클라우드 DAM (유지보수 중단)

---

## 6. 18TB 포커 방송 아카이브 요구사항 매칭

### 핵심 요구사항
| 요구사항 | Telemeta | Archivematica | Pimcore | OpenBroadcaster |
|---------|----------|--------------|---------|-----------------|
| SMB/NAS 연동 | ✅ (Python) | ✅ (Storage Service) | ✅ (PHP 구성) | ✅ (네트워크 공유) |
| 대용량 비디오 처리 | ✅ (TimeSide) | ✅ (FFmpeg) | ✅ | ✅ (GStreamer) |
| 메타데이터 추출 | ✅ (XMP/EXIF) | ✅ (FITS, MediaInfo) | ✅ (220+ 포맷) | ✅ (방송 메타) |
| OTT 스트리밍 지원 | ✅ (HTML5) | ❌ | ⚠️ | ✅ (IPTV) |
| Python 통합 | ✅ (네이티브) | ✅ (네이티브) | ❌ (API 호출) | ❌ (API 호출) |
| 검색 기능 | ✅ (ElasticSearch) | ✅ (Haystack) | ✅ | ✅ |
| 협업 기능 | ✅ | ⚠️ | ✅ | ⚠️ |

---

## 7. 권장 사항

### 🥇 최우선 추천: Telemeta
**이유**:
- Python/Django 기반 → Archive Analyzer 코드베이스와 완벽 통합
- TimeSide 프레임워크가 FFmpeg/GStreamer를 추상화
- HTML5 스트리밍 플레이어 내장
- Docker 기반 배포로 ElasticSearch, Jupyter 등 즉시 사용
- 오디오/비디오 아카이브에 특화된 메타데이터 관리

**통합 전략**:
```python
# Archive Analyzer → Telemeta 메타데이터 푸시
from telemeta.models import MediaItem
from archive_analyzer.database import Database

db = Database("archive.db")
for file_info in db.get_all_files():
    MediaItem.objects.create(
        title=file_info['path'],
        duration=file_info['duration'],
        codec=file_info['video_codec'],
        # SMB 경로를 Telemeta 스토리지로 매핑
    )
```

---

### 🥈 차선책: Archivematica
**이유**:
- 장기 보존 표준 (OAIS) 준수 필요 시
- Python 기반으로 확장 가능
- Storage Service가 SMB/NAS 연동 지원

**단점**: 스트리밍 미지원 → 별도 플레이어 필요

---

### 🥉 엔터프라이즈 옵션: Pimcore
**이유**:
- 조직 전체 데이터 플랫폼 구축 시
- PIM/CMS 등 추가 기능 필요 시
- 대규모 커뮤니티 및 상용 지원

**단점**: Python 환경과 이질적, 복잡도 높음

---

### ⚠️ 제외 권장
1. **Razuna** - 유지보수 중단, 레거시 기술 스택
2. **AtroDAM** - 커뮤니티 규모 너무 작음, 미성숙
3. **tinyMediaManager** - 홈 미디어 관리용 (엔터프라이즈 부적합)

---

## 8. 하이브리드 접근법

**Archive Analyzer (현재 시스템) + Telemeta 통합**:

```
┌─────────────────────────────────────────────┐
│ SMB/NAS (18TB+ 포커 아카이브)                │
└───────────┬─────────────────────────────────┘
            │
            ├─────────────────┐
            │                 │
            ▼                 ▼
    ┌───────────────┐  ┌──────────────┐
    │ Archive       │  │ Telemeta     │
    │ Analyzer      │  │ (Web UI +    │
    │ (메타추출)     │─▶│  협업 + 스트리밍)│
    │ - Scanner     │  │              │
    │ - FFprobe     │  │ - TimeSide   │
    │ - SQLite      │  │ - Django     │
    └───────────────┘  │ - HTML5      │
                       └──────────────┘
```

**장점**:
- Archive Analyzer는 메타데이터 추출 엔진 역할 (경량, 빠름)
- Telemeta는 사용자 인터페이스 및 협업 계층 (풍부한 기능)
- 두 시스템 모두 Python → 통합 코드 간결

---

## 9. 다음 단계

### Phase 1: 개념 증명 (PoC)
1. Telemeta Docker 컨테이너 로컬 설치
2. Archive Analyzer SQLite → Telemeta DB 동기화 스크립트 작성
3. SMB 경로를 Telemeta 스토리지 백엔드로 연결
4. 샘플 100개 파일로 메타데이터 추출 → 웹 UI 확인

### Phase 2: 평가
1. 검색 성능 테스트 (ElasticSearch)
2. 스트리밍 품질 확인 (H.264/HEVC 호환성)
3. 사용자 협업 기능 테스트
4. Archive Analyzer 대비 메타데이터 품질 비교

### Phase 3: 프로덕션 배포
1. 18TB 전체 아카이브 마이그레이션 계획
2. 백업 및 재해 복구 전략
3. 사용자 교육 및 문서화
4. 모니터링 및 유지보수 프로세스

---

## 10. 참고 자료

### Telemeta
- 공식 사이트: http://telemeta.org/
- GitHub: https://github.com/Parisson/Telemeta
- PyPI: https://pypi.org/project/Telemeta/
- 논문: [Telemeta: An open-source web framework for ethnomusicological audio archives](https://hal.science/hal-03271840v1)

### Archivematica
- 공식 사이트: https://www.archivematica.org/
- GitHub: https://github.com/artefactual/archivematica
- 문서: https://www.archivematica.org/en/docs/

### Pimcore
- 공식 사이트: https://pimcore.com/
- GitHub: https://github.com/pimcore/pimcore
- Community Edition: https://pimcore.com/en/platform/community-edition

### 오픈소스 방송 도구
- EBU Awesome Broadcasting: https://github.com/ebu/awesome-broadcasting
- AMIA Open Workflows: https://github.com/amiaopensource/open-workflows

### 메타데이터 도구
- MediaInfo: https://mediaarea.net/MediaInfo
- QCTools: https://github.com/bavc/qctools
- MediaConch: https://mediaarea.net/MediaConch

---

**문서 버전**: 1.0
**작성자**: Archive Analyzer 프로젝트
**최종 업데이트**: 2025-12-01
