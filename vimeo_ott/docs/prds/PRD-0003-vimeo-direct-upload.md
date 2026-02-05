# PRD-0003: Vimeo OTT Direct Upload Strategy

**Version**: 1.1.0
**Status**: Implementation Complete
**Created**: 2026-02-04
**Updated**: 2026-02-04
**Author**: WSOPTV Team
**Parent PRD**: PRD-0001, PRD-0002

---

## 1. 개요

### 1.1 목적

S3 중간 계층 없이 **NAS에서 직접 Vimeo로 업로드**하는 단순화된 파이프라인 구축 및 7TB 콘텐츠 선별 전략 수립

### 1.2 배경

| 상황 | 내용 |
|------|------|
| **기존 설계 (PRD-0002)** | NAS → S3 → Vimeo 3계층 |
| **변경 설계 (PRD-0003)** | NAS → Vimeo 2계층 (S3 제거) |
| **Vimeo Enterprise 한도** | 7 TB 스토리지 |
| **전체 아카이브 규모** | 1,056 파일, ~18 TB |
| **선별 필요량** | 18 TB → 7 TB (~40% 선별) |

### 1.3 아키텍처 변경

```
기존 (PRD-0002):
  NAS ──▶ AWS S3 ──▶ Vimeo ──▶ WSOPTV Apps
        (영구보관)  (스트리밍)

신규 (PRD-0003):
  NAS ──────────────▶ Vimeo ──▶ WSOPTV Apps
                    (스트리밍)
```

### 1.4 범위

| 포함 | 제외 |
|------|------|
| NAS → Vimeo 직접 업로드 | S3 연동 (별도 프로젝트) |
| 7TB 콘텐츠 선별 전략 | 라이브 스트리밍 |
| 10개 샘플 POC | 앱 개발 |
| Vimeo Collections 구성 | 결제 시스템 |

---

## 2. 콘텐츠 분석 (master_catalog 기반)

### 2.1 전체 현황

| 항목 | 값 |
|------|------|
| **총 파일 수** | 1,056개 |
| **총 용량** | 18,393.70 GB (~18 TB) |
| **Vimeo 한도** | 7,168 GB (7 TB) |
| **초과량** | 11,225.70 GB (~11 TB) |

### 2.2 이벤트 유형별 분포

| 이벤트 유형 | 파일 수 | 용량 (GB) | 비율 |
|------------|:------:|----------:|-----:|
| **ME** (Main Event) | 505 | 10,368 | 56.4% |
| **BR** (Bracelet Events) | 308 | 3,530 | 19.2% |
| **COVERAGE** | 34 | 1,636 | 8.9% |
| **WSOPE** (Europe) | 52 | 1,200 | 6.5% |
| **WSOPA** (APAC) | 28 | 680 | 3.7% |
| **기타** | 129 | 980 | 5.3% |

### 2.3 연도별 분포 (주요)

| 연도 | 파일 수 | 용량 (GB) | 특이사항 |
|:----:|:------:|----------:|---------|
| 1973-2002 | ~100 | ~500 | Classic Era |
| 2003-2010 | ~200 | ~3,000 | Modern Era 초기 |
| 2011-2020 | ~450 | ~8,000 | HD 전환 |
| 2021-2025 | ~300 | ~7,000 | 4K 콘텐츠 |

---

## 3. 7TB 콘텐츠 선별 전략

### 3.1 선별 원칙

| 우선순위 | 원칙 | 근거 |
|:--------:|------|------|
| **P0** | Main Event 우선 | 핵심 콘텐츠, 시청 수요 최고 |
| **P1** | Classic Era 전체 포함 | 희소성, 역사적 가치 |
| **P2** | 최신 연도 우선 | 시청자 관심도 |
| **P3** | 고화질 우선 | 사용자 경험 |

### 3.2 선별 시나리오

#### 시나리오 A: Main Event 중심 (권장)

```
┌─────────────────────────────────────────────────────────────┐
│  7TB 선별 시나리오 A: Main Event 중심                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Classic Era (1973-2002)                           │
│  ├── 모든 Main Event                                        │
│  └── 약 100 파일, ~500 GB                                   │
│                                                              │
│  Layer 2: Modern Era Main Events (2003-2024)                │
│  ├── Main Event Final Table                                 │
│  ├── Main Event Day 7+                                      │
│  └── 약 300 파일, ~4,500 GB                                 │
│                                                              │
│  Layer 3: Featured Bracelet Events                          │
│  ├── $10K+ Buy-in Events                                    │
│  ├── High Roller Events                                     │
│  └── 약 100 파일, ~1,500 GB                                 │
│                                                              │
│  Layer 4: Coverage Highlights                               │
│  └── 약 30 파일, ~500 GB                                    │
│                                                              │
│  Total: ~530 파일, ~7,000 GB                                │
└─────────────────────────────────────────────────────────────┘
```

| 계층 | 콘텐츠 | 파일 수 | 용량 (GB) |
|:----:|--------|:------:|----------:|
| 1 | Classic Era 전체 | 100 | 500 |
| 2 | Modern Main Events | 300 | 4,500 |
| 3 | Featured Bracelet | 100 | 1,500 |
| 4 | Coverage Highlights | 30 | 500 |
| **합계** | - | **530** | **7,000** |

#### 시나리오 B: 균형 선별

| 계층 | 콘텐츠 | 파일 수 | 용량 (GB) |
|:----:|--------|:------:|----------:|
| 1 | Classic Era 전체 | 100 | 500 |
| 2 | Main Event 50% | 250 | 5,000 |
| 3 | Bracelet Event 20% | 60 | 700 |
| 4 | WSOPE/WSOPA 선별 | 40 | 800 |
| **합계** | - | **450** | **7,000** |

### 3.3 선별 제외 기준

| 제외 대상 | 이유 |
|----------|------|
| 중복 파일 | 용량 낭비 |
| 저화질 버전 (고화질 존재 시) | 품질 우선 |
| 미완성/손상 파일 | 시청 불가 |
| 비공개 콘텐츠 | 라이선스 |

---

## 4. POC 테스트 계획

### 4.1 샘플 영상 10개 선정

WSOP Classic (1973-2002)에서 다양한 포맷/용량으로 선정:

| # | 연도 | 파일명 | 용량 | 형식 | 선정 이유 |
|:-:|:----:|--------|-----:|:----:|----------|
| 1 | 1973 | WSOP - 1973.avi | 728 MB | AVI | 최초 영상 |
| 2 | 1978 | wsop-1978-me-nobug.mp4 | 1.5 GB | MP4 | 초기 ME |
| 3 | 1983 | wsop-1983-me-nobug.mp4 | 3.3 GB | MP4 | 중간 용량 |
| 4 | 1988 | 1988 World Series of Poker.mov | 41.5 GB | MOV | 대용량 테스트 |
| 5 | 1989 | wsop-1989-me_nobug.mp4 | 1.8 GB | MP4 | 표준 용량 |
| 6 | 1992 | wsop-1992-me-nobug.mp4 | 3.5 GB | MP4 | 표준 용량 |
| 7 | 1994 | wsop-1994-me-nobug.mp4 | 3.5 GB | MP4 | 표준 용량 |
| 8 | 1995 | wsop-1995-me-nobug.mp4 | 4.0 GB | MP4 | 표준 용량 |
| 9 | 1998 | 1998 World Series of Poker.mov | 91.3 GB | MOV | 최대 용량 테스트 |
| 10 | 2000 | wsop-2000-me-nobug.mp4 | 5.5 GB | MP4 | 밀레니엄 |

**NAS 경로**: `Z:\GGPNAs\ARCHIVE\WSOP\WSOP Classic (1973 - 2002)\`

**총 용량**: ~156 GB (10개 파일)

### 4.2 검증 항목

| # | 검증 항목 | 성공 기준 |
|:-:|----------|----------|
| 1 | 업로드 성공률 | 10/10 (100%) |
| 2 | 트랜스코딩 완료 | status == "available" |
| 3 | 메타데이터 정확도 | 연도/제목 일치 |
| 4 | 재생 품질 | 원본 대비 90%+ |
| 5 | Collections 구성 | WSOP Classic 폴더/앨범 생성 |
| 6 | 업로드 속도 | 평균 50 Mbps+ |

### 4.3 대용량 파일 업로드 전략

**TUS 청크 업로드 프로토콜:**

```
┌─────────────────────────────────────────────────────────────┐
│  TUS Chunked Upload (대용량 파일 처리)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  원본 파일: 91.3 GB (1998 WSOP)                             │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────┬─────────┬─────────┬─────────┬─────┐           │
│  │ Chunk 1 │ Chunk 2 │ Chunk 3 │   ...   │ N   │           │
│  │ 128 MB  │ 128 MB  │ 128 MB  │         │     │           │
│  └────┬────┴────┬────┴────┬────┴─────────┴─────┘           │
│       │         │         │                                  │
│       ▼         ▼         ▼                                  │
│  [순차 업로드] ─── 실패 시 해당 청크부터 재개 ───            │
│       │                                                      │
│       ▼                                                      │
│  Vimeo 서버에서 재조립 → 트랜스코딩                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

| 항목 | 값 |
|------|------|
| **청크 크기** | 128 MB |
| **91GB 파일 청크 수** | ~730개 |
| **재시도 로직** | 실패 청크부터 재개 |
| **타임아웃** | 청크당 5분 |

---

## 5. 요구사항

### 5.1 기능 요구사항

#### P0 (필수)

| ID | 기능 | 설명 |
|:--:|------|------|
| F-001 | 배치 업로드 | 다중 파일 순차 업로드 |
| F-002 | 메타데이터 파싱 | 파일명에서 연도/이벤트 추출 |
| F-003 | 업로드 이력 | JSON 기반 중복 방지 |
| F-004 | 재시도 로직 | 실패 시 자동 재시도 (3회) |

#### P1 (중요)

| ID | 기능 | 설명 |
|:--:|------|------|
| F-005 | Collections 관리 | 폴더/앨범 자동 생성 |
| F-006 | 진행률 표시 | 업로드/트랜스코딩 상태 |
| F-007 | dry-run 모드 | 실제 업로드 없이 검증 |

#### P2 (선택)

| ID | 기능 | 설명 |
|:--:|------|------|
| F-008 | 선별 도구 | master_catalog 기반 7TB 선별 |
| F-009 | 리포트 생성 | 업로드 결과 리포트 |

### 5.2 비기능 요구사항

| 항목 | 요구사항 |
|------|----------|
| **안정성** | 대용량 파일 (100GB+) 처리 가능 |
| **재개 가능** | 네트워크 끊김 시 이어서 업로드 |
| **로깅** | 모든 작업 JSON 로그 저장 |
| **인증** | Browser OAuth만 사용 (API 키 금지) |

---

## 6. 구현 계획

### 6.1 새로 구현할 파일

| 파일 | 용도 | 우선순위 |
|------|------|:--------:|
| `scripts/vimeo/metadata_parser.py` | 파일명에서 메타데이터 추출 | P0 |
| `scripts/vimeo/collections.py` | Vimeo Collections API 래퍼 | P0 |
| `scripts/vimeo/batch_upload.py` | 배치 업로드 CLI | P0 |

### 6.2 기존 활용 파일

| 파일 | 용도 | 상태 |
|------|------|:----:|
| `scripts/vimeo/auth.py` | OAuth 인증 | ✅ 완료 |
| `scripts/vimeo/upload_poc.py` | 단일 업로드 | ✅ 완료 |

### 6.3 실행 순서

```
Phase 1: 스크립트 구현
├── metadata_parser.py 구현
├── collections.py 구현
└── batch_upload.py 구현

Phase 2: POC 실행
├── Vimeo "WSOP Classic" 폴더 생성
├── 연도별 앨범 생성
├── 샘플 10개 업로드 (~156 GB)
└── 결과 검증

Phase 3: 7TB 선별
├── master_catalog 분석 완료
├── 시나리오 A/B 최종 선택
└── 전체 업로드 계획 수립
```

---

## 7. 리스크 및 완화

| 리스크 | 영향 | 완화 방안 |
|--------|:----:|----------|
| 대용량 파일 업로드 실패 | 중 | TUS 청크 업로드, 재시도 로직 |
| 네트워크 불안정 | 중 | 이력 저장, resume 기능 |
| Vimeo Rate Limit | 중 | 업로드 간격 조절 (1분) |
| 7TB 초과 | 중 | 선별 전략 적용, 모니터링 |
| Folders API 미지원 | 저 | Albums만 사용 fallback |

---

## 8. 성공 지표

| 지표 | 목표 |
|------|------|
| POC 업로드 성공률 | 100% (10/10) |
| 트랜스코딩 완료 | 24시간 내 |
| 메타데이터 정확도 | 100% |
| 7TB 선별 완료 | 530개 파일 |
| Collections 구성 | WSOP Classic 완료 |

---

## 9. 참고 문서

| 문서 | 설명 |
|------|------|
| [PRD-0001](./PRD-0001-vimeo-automation.md) | Vimeo 자동화 기초 |
| [PRD-0002](./PRD-0002-vimeo-ott-s3-strategy.md) | S3 통합 전략 (참조용) |
| [Plan 문서](../01-plan/vimeo-ott-direct-upload.plan.md) | 구현 계획 상세 |
| [master_catalog](https://docs.google.com/spreadsheets/d/1h27Ha7pR-iYK_Gik8F4FfSvsk4s89sxk49CsU3XP_m4) | 콘텐츠 목록 |

---

## Appendix A: master_catalog 컬럼 구조

| 컬럼 | 설명 | 예시 |
|------|------|------|
| A | 연도 | 2024 |
| B | 이벤트 유형 | ME, BR, COVERAGE |
| C | 이벤트명 | Main Event Day 7 |
| D | 파일명 | wsop-2024-me-day7.mp4 |
| E | 용량 (GB) | 45.6 |
| F | 형식 | MP4, MOV, AVI |
| G | 해상도 | 1080p, 4K |
| H | NAS 경로 | Z:\GGPNAs\ARCHIVE\... |

---

## Appendix B: Vimeo Enterprise 기능

| 기능 | 지원 | 비고 |
|------|:----:|------|
| 스토리지 | 7 TB | 현재 할당량 |
| API 업로드 | ✅ | TUS 프로토콜 |
| Folders | ✅ | Enterprise 전용 |
| Albums | ✅ | Standard도 지원 |
| 분석 API | ✅ | 시청 통계 |
| 화이트라벨 플레이어 | ✅ | 브랜딩 제거 가능 |

---

## 10. 구현 완료 결과

### 10.1 구현된 모듈

| 모듈 | 경로 | 상태 |
|------|------|:----:|
| `metadata_parser.py` | `scripts/vimeo/` | ✅ |
| `vimeo_collections.py` | `scripts/vimeo/` | ✅ |
| `batch_upload.py` | `scripts/vimeo/` | ✅ |
| `poc_samples.py` | `scripts/vimeo/` | ✅ |

### 10.2 POC 샘플 (실제 검증)

실제 NAS 구조에 맞춰 10개 샘플 선정 (총 32.58 GB):

| # | 연도 | 파일명 | 용량 |
|:-:|:----:|--------|-----:|
| 1 | 1973 | WSOP - 1973.avi | 0.71 GB |
| 2 | 1978 | wsop-1978-me-nobug.mp4 | 1.47 GB |
| 3 | 1983 | wsop-1983-me-nobug.mp4 | 3.20 GB |
| 4 | 1989 | wsop-1989-me_nobug.mp4 | 1.72 GB |
| 5 | 1992 | wsop-1992-me-nobug.mp4 | 3.40 GB |
| 6 | 1994 | wsop-1994-me-nobug.mp4 | 3.39 GB |
| 7 | 1995 | wsop-1995-me-nobug.mp4 | 3.89 GB |
| 8 | 1998 | wsop-1998-me-nobug.mp4 | 4.11 GB |
| 9 | 2000 | wsop-2000-me-nobug.mp4 | 5.32 GB |
| 10 | 2001 | wsop-2001-me-nobug.mp4 | 5.38 GB |

### 10.3 테스트 결과

| 테스트 | 결과 |
|--------|:----:|
| metadata_parser --test | ✅ PASS |
| vimeo_collections list | ✅ PASS |
| batch_upload --poc --dry-run | ✅ PASS |
| poc_samples validation | ✅ PASS (10/10) |

### 10.4 사용법 요약

```bash
# POC dry-run
python scripts/vimeo/batch_upload.py --poc --dry-run

# POC 실제 업로드
python scripts/vimeo/batch_upload.py --poc

# 상태 확인
python scripts/vimeo/batch_upload.py --status
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-04 | 초안 작성 |
| 1.1.0 | 2026-02-04 | 구현 완료, POC 샘플 검증 |
