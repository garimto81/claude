# PRD-0002: WSOPTV OTT + AWS S3 통합 전략

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Priority** | P0 |
| **Created** | 2026-02-04 |
| **Author** | Claude Code |
| **Parent** | PRD-0001, PRD-0012 |

---

## Executive Summary

WSOP 아카이브 콘텐츠를 **AWS S3에 영구 보관**하고 **Vimeo Enterprise를 통해 스트리밍**하는 3계층 인프라 전략입니다.

### 핵심 아키텍처

```
NAS (작업용) ──▶ AWS S3 (영구 보관) ──▶ Vimeo (스트리밍) ──▶ WSOPTV Apps
```

### 주요 결정사항

| 결정 | 선택 | 근거 |
|------|------|------|
| **S3 역할** | 원본 보관소 | NAS 의존도 제거, 장기 비용 효율 |
| **Vimeo 역할** | 스트리밍 전용 | CDN/트랜스코딩/앱 플랫폼 활용 |
| **우선순위** | POC 먼저 | 리스크 최소화, 비용 검증 |

### Phase 1 목표

- 10-20개 파일로 전체 파이프라인 검증
- S3 ↔ Vimeo 자동 동기화 POC
- 비용/성능 측정 및 분석

---

## 1. 배경 및 목적

### 1.1 현재 상태

| 항목 | 상태 |
|------|------|
| Vimeo Enterprise | ✅ 계정 확보 (7TB) |
| Vimeo OAuth | ✅ 인증 구현 완료 |
| Vimeo 업로드 POC | ✅ 단일 파일 테스트 완료 |
| AWS S3 | ✅ API 접근 가능 확인 |
| WSOP 아카이브 | ~2,600 파일, ~6TB |

### 1.2 문제 정의

| 문제 | 영향 | 해결 방안 |
|------|------|----------|
| NAS 의존성 | 단일 장애점, 확장 어려움 | S3 이중화 |
| 수동 업로드 | 비효율, 일관성 부족 | 자동화 파이프라인 |
| 메타데이터 분산 | 검색/관리 어려움 | 중앙집중 JSON 스키마 |

### 1.3 목표

| 목표 | 측정 지표 | 기준 |
|------|----------|------|
| **자동화** | 수동 개입 비율 | < 5% |
| **신뢰성** | 업로드 성공률 | > 99% |
| **비용 효율** | TCO 절감 | Full Custom 대비 90%+ |
| **확장성** | 처리량 | 100GB/일 |

---

## 2. 아키텍처

### 2.1 시스템 구성도

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WSOPTV OTT Platform Architecture                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │    NAS       │    │   AWS S3     │    │   Vimeo      │                   │
│  │  (Source)    │───▶│  (Archive)   │───▶│ (Streaming)  │                   │
│  │              │    │              │    │              │                   │
│  │ Z:\GGPNAs\   │    │ wsoptv-      │    │ Enterprise   │                   │
│  │ ARCHIVE\     │    │ archive      │    │ 7TB          │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                  │                   │                             │
│         │                  │                   │                             │
│         ▼                  ▼                   ▼                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         WSOPTV Apps                                  │    │
│  │  [iOS]  [Android]  [Web]  [Apple TV]  [Roku]  [Fire TV]            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 3계층 스토리지 전략

| 계층 | 역할 | 스토리지 | 비용 |
|:----:|------|----------|-----:|
| **1** | 작업용 (편집/인코딩) | NAS | 기존 |
| **2** | 영구 보관 (마스터) | AWS S3 | ~$52/월 |
| **3** | 스트리밍 전달 | Vimeo CDN | 협의 |

### 2.3 데이터 흐름

```
[NAS 원본]
    │
    │ (1) Python CLI: s3_sync.py
    │     - 파일 해시 계산
    │     - 중복 체크
    │     - 청크 업로드 (100MB)
    ▼
[AWS S3]
    │
    │ (2) S3 Event → Lambda/CLI
    │     - 자동 트리거
    │     - 메타데이터 생성
    ▼
[Vimeo Upload]
    │
    │ (3) TUS 프로토콜
    │     - 청크 업로드
    │     - 재시도 로직
    ▼
[Vimeo Transcoding]
    │
    │ (4) 자동 처리
    │     - HLS Adaptive
    │     - 다중 해상도
    ▼
[Vimeo CDN → WSOPTV Apps]
```

---

## 3. AWS S3 설계

### 3.1 버킷 구조

```
wsoptv-archive/
├── raw/                    # 원본 비디오
│   ├── wsop-classic/       # 1973-2002
│   ├── wsop-modern/        # 2003-2024
│   └── wsop-europe/        # 2007-2024
├── metadata/               # 메타데이터 JSON
├── thumbnails/             # 썸네일
├── logs/                   # 업로드 로그
└── temp/                   # 임시 스테이징
```

### 3.2 스토리지 클래스 전략

| 클래스 | 대상 | 접근 빈도 | 비용 (TB/월) |
|--------|------|:--------:|------------:|
| **S3 Standard** | 최근 1년 | 자주 | $23 |
| **S3 Glacier IR** | 1-3년 | 가끔 | $4 |
| **S3 Glacier Deep** | 3년+ | 드물게 | $1 |

### 3.3 Lifecycle 정책

| 조건 | 전환 |
|------|------|
| 생성 후 365일 | Standard → Glacier Instant Retrieval |
| 생성 후 1095일 | Glacier IR → Deep Archive |

### 3.4 비용 예측 (월간)

| 항목 | 용량 | 단가 | 비용 |
|------|:----:|:----:|-----:|
| S3 Standard | 1TB | $0.023/GB | $23 |
| S3 Glacier IR | 5TB | $0.004/GB | $20 |
| 데이터 전송 | 100GB | $0.09/GB | $9 |
| **합계** | 6TB | - | **~$52/월** |

---

## 4. Vimeo OTT 연동

### 4.1 Enterprise 기능 활용

| 기능 | 설명 | Phase |
|------|------|:-----:|
| **API 업로드** | TUS 프로토콜 청크 업로드 | 1 |
| **Collections** | 시리즈/시즌 구조화 | 1 |
| **Live Streaming** | RTMP 수신, DVR | 2 |
| **Subscription** | Stripe 연동 결제 | 2 |
| **Analytics** | 시청 데이터 수집 | 2 |
| **Multi-platform** | iOS, Android, TV 앱 | 2 |

### 4.2 S3 → Vimeo 워크플로우

```python
def sync_s3_to_vimeo(s3_key: str) -> str:
    """S3 파일을 Vimeo에 동기화"""

    # 1. 메타데이터 조회
    metadata = s3.get_json(f"metadata/{video_id}.json")

    # 2. Presigned URL 생성 (또는 직접 다운로드)
    presigned_url = s3.generate_presigned_url(s3_key, expires=3600)

    # 3. Vimeo 업로드 (TUS)
    vimeo_uri = vimeo.upload(
        file_url=presigned_url,
        data={
            "name": metadata["title"],
            "description": metadata.get("description", ""),
            "privacy": {"view": "unlisted"}
        }
    )

    # 4. 메타데이터 업데이트
    metadata["vimeo_uri"] = vimeo_uri
    metadata["status"] = "transcoding"
    s3.put_json(f"metadata/{video_id}.json", metadata)

    return vimeo_uri
```

### 4.3 컬렉션 매핑

| WSOP 구조 | Vimeo 구현 |
|----------|-----------|
| Series (WSOP 2026) | Folder |
| Event (Main Event) | Collection |
| Day (Day 1A) | Video |

---

## 5. 메타데이터 스키마

### 5.1 Video Metadata (JSON)

```json
{
  "video_id": "wsop-2026-main-event-day-1a",
  "title": "WSOP 2026 Main Event - Day 1A",
  "description": "...",
  "source_path": "Z:\\GGPNAs\\ARCHIVE\\WSOP\\2026\\Main Event\\Day 1A.mp4",
  "s3_key": "raw/wsop-modern/2026/main-event/day-1a.mp4",
  "vimeo_uri": "/videos/1234567890",
  "status": "available",

  "wsop": {
    "series": "WSOP",
    "year": 2026,
    "event_name": "Main Event",
    "event_number": 68,
    "day": "Day 1A",
    "players": ["Daniel Negreanu", "Phil Ivey"],
    "winner": null
  },

  "technical": {
    "duration_seconds": 28800,
    "file_size_bytes": 10737418240,
    "format": "mp4",
    "resolution": "1920x1080",
    "codec": "h264"
  },

  "timestamps": {
    "created_at": "2026-06-01T10:00:00Z",
    "s3_uploaded_at": "2026-06-02T08:30:00Z",
    "vimeo_uploaded_at": "2026-06-02T09:15:00Z",
    "available_at": "2026-06-02T12:00:00Z"
  }
}
```

### 5.2 상태 전이

```
PENDING → S3_UPLOADED → VIMEO_UPLOADING → TRANSCODING → AVAILABLE
    │                                                       │
    └───────────────────── FAILED ◀─────────────────────────┘
```

---

## 6. POC 테스트 계획

### 6.1 테스트 범위

| 항목 | 값 |
|------|---|
| **대상 파일** | WSOP Classic 1973-1975 |
| **파일 수** | 10-20개 |
| **총 용량** | ~5GB |
| **포맷** | AVI, MP4, MOV |

### 6.2 검증 항목

| # | 검증 항목 | 성공 기준 |
|:-:|----------|----------|
| 1 | NAS → S3 업로드 | 성공률 100% |
| 2 | S3 → Vimeo 전송 | 성공률 100% |
| 3 | 메타데이터 동기화 | 일치율 100% |
| 4 | 업로드 속도 | 10 MB/s 이상 |
| 5 | 트랜스코딩 시간 | 24시간 내 완료 |
| 6 | 비용 측정 | 예측 오차 ±20% |

### 6.3 테스트 스크립트

| 스크립트 | 기능 |
|----------|------|
| `scripts/aws/s3_client.py` | S3 업로드/다운로드 |
| `scripts/aws/s3_sync.py` | NAS → S3 동기화 |
| `scripts/poc/test_pipeline.py` | 전체 파이프라인 테스트 |
| `scripts/poc/validate_metadata.py` | 메타데이터 검증 |

### 6.4 테스트 실행 계획

| 단계 | 작업 | 예상 |
|:----:|------|------|
| 1 | AWS 버킷 생성/IAM 설정 | 1일 |
| 2 | S3 업로드 스크립트 개발 | 1일 |
| 3 | POC 파일 S3 업로드 | 1일 |
| 4 | Vimeo 연동 테스트 | 1일 |
| 5 | 결과 분석 및 리포트 | 1일 |

---

## 7. 구현 로드맵

### Phase 1: POC (현재)

| 작업 | 상태 | 우선순위 |
|------|:----:|:--------:|
| S3 버킷 생성 | TODO | P0 |
| IAM 사용자 설정 | TODO | P0 |
| S3 업로드 스크립트 | TODO | P0 |
| POC 테스트 실행 | TODO | P0 |
| 결과 분석 리포트 | TODO | P0 |

### Phase 2: 아카이브 이관

| 작업 | 예상 | 우선순위 |
|------|------|:--------:|
| 전체 아카이브 S3 업로드 | 6TB/100Mbps ≈ 6일 | P1 |
| 메타데이터 일괄 생성 | 2,600 파일 | P1 |
| Vimeo 일괄 업로드 | 병렬 5개 | P1 |

### Phase 3: 자동화 파이프라인

| 작업 | 설명 | 우선순위 |
|------|------|:--------:|
| S3 Event → Lambda | 새 파일 자동 감지 | P1 |
| Vimeo Webhook | 트랜스코딩 완료 알림 | P1 |
| 모니터링 대시보드 | CloudWatch 연동 | P2 |

### Phase 4: 앱 출시 (PRD-0012 연계)

| 작업 | 설명 | 목표 |
|------|------|------|
| Vimeo OTT 앱 배포 | iOS, Android, Apple TV | Q3 2026 |
| 구독 결제 연동 | Stripe + GGPass | Q3 2026 |
| 론칭 | WSOP 2026 메인 이벤트 전 | Q3 2026 |

---

## 8. 비용 분석

### 8.1 월간 운영 비용

| 항목 | 비용 |
|------|-----:|
| AWS S3 (6TB) | $52 |
| AWS 데이터 전송 | $10 |
| Vimeo Enterprise | 협의 필요 |
| **합계** | ~$100+α |

### 8.2 TCO 비교 (연간)

| 방안 | 연 비용 | 비고 |
|------|-------:|------|
| **S3 + Vimeo (권장)** | ~$1,500 | 현 방안 |
| Vimeo Only | ~$6,000 | S3 백업 없음 |
| Full Custom | ~$60,000+ | 자체 CDN/인코더 |

---

## 9. 리스크 및 완화

| 리스크 | 영향 | 확률 | 완화 방안 |
|--------|:----:|:----:|----------|
| S3 업로드 실패 | 중 | 낮 | 청크 업로드, 3회 재시도 |
| Vimeo Rate Limit | 중 | 중 | 지수 백오프, 병렬 제한 (5개) |
| 비용 초과 | 중 | 낮 | Glacier 전환, 모니터링 알림 |
| 트랜스코딩 지연 | 저 | 중 | 우선순위 큐, Vimeo 지원 요청 |
| 메타데이터 불일치 | 저 | 낮 | 검증 스크립트, 자동 수정 |

---

## 10. 성공 지표

| KPI | 목표 | 측정 방법 |
|-----|------|----------|
| 업로드 성공률 | > 99% | 로그 분석 |
| 평균 처리 시간 | < 2시간/파일 | 타임스탬프 |
| 비용 효율 | < $0.01/GB/월 | AWS/Vimeo 청구서 |
| 수동 개입률 | < 5% | 운영 로그 |
| 앱 가용성 | > 99.9% | Vimeo SLA |

---

## 11. 관련 문서

| 문서 | 설명 |
|------|------|
| [PRD-0001](PRD-0001-vimeo-automation.md) | Vimeo 자동화 기초 PRD |
| [PRD-0012](../../wsoptv_ott/docs/prds/PRD-0012-phase1-vimeo-nbatv-style.md) | Phase 1 MVP (NBA TV 스타일) |
| [Plan Doc](../01-plan/vimeo-ott-s3-strategy.plan.md) | 전략 계획 문서 |
| [Design Doc](../02-design/vimeo-ott-s3-architecture.design.md) | 아키텍처 설계 문서 |

---

## Revision History

| 버전 | 날짜 | 작성자 | 내용 |
|------|------|--------|------|
| 1.0 | 2026-02-04 | Claude Code | 최초 작성 |
