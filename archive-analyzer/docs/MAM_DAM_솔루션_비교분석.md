# 상용 미디어 자산 관리(MAM/DAM) 솔루션 비교 분석

**분석 날짜**: 2025-12-01
**컨텍스트**: 18TB+ 포커 방송 아카이브, OTT 플랫폼 연동 필요

---

## 1. 솔루션 개요 비교표

| 솔루션 | 유형 | 배포 모델 | 타겟 사용자 | 가격 정책 |
|--------|------|-----------|------------|----------|
| **iconik** | MAM | Cloud-native SaaS | 중소기업, 분산 팀 | $250/월 시작, 사용량 기반, 무제한 사용자 |
| **Dalet** | MAM | On-premise, Hybrid, Cloud | 대기업, 방송사, 스포츠 | 커스텀 견적 (Enterprise급) |
| **Cantemo** | MAM | Hybrid-cloud, On-premise | 대기업, BBC/NASA급 | 요구사항별 커스텀 견적 |
| **Vidispine** | MAM Backend | API/Infrastructure | 개발자, SI 업체 | 커스텀 견적 (백엔드 인프라) |
| **MediaSilo** | DAM/Video | Cloud SaaS | 중소기업, 에이전시 | Free~$999/월 ($15-25/사용자) |
| **Frame.io** | DAM/Video | Cloud SaaS | 크리에이터, 제작팀 | Free~Enterprise ($15-25/사용자) |
| **Canto** | DAM | Cloud SaaS | 중소기업~대기업 | 커스텀 견적 (사용자 + 스토리지) |
| **Brandfolder** | DAM | Cloud SaaS | 브랜드 중심 기업 | 커스텀 견적 (Basic~Enterprise) |

---

## 2. 주요 기능 상세 비교

### 2.1 MAM 솔루션 (방송/OTT 특화)

| 기능 | iconik | Dalet | Cantemo | Vidispine |
|------|--------|-------|---------|-----------|
| **NAS/SMB 연동** | ✅ ISG (iconik Storage Gateway) | ✅ 네이티브 지원 | ✅ 네이티브 지원 | ✅ VSA (Vidispine Server Agent) |
| **하이브리드 클라우드** | ✅ BYOS (Bring Your Own Storage) | ✅ Multi-cloud | ✅ Hybrid 지원 | ✅ Hybrid 아키텍처 |
| **AI 자동 태깅** | ✅ Built-in AI | ⚠️ 3rd party 통합 | ⚠️ 3rd party 통합 | ⚠️ API 레벨 |
| **AI 전사** | ✅ 자동 전사 | ⚠️ 3rd party | ⚠️ 3rd party | ⚠️ API 레벨 |
| **프레임 정확 편집** | ✅ Time-coded metadata | ✅ Frame-accurate | ✅ Frame-accurate logging | ✅ Frame-accurate proxies |
| **Adobe 통합** | ✅ Premiere/AE/Photoshop | ✅ NLE 통합 | ✅ Premiere Pro Panel | ✅ Via 앱 |
| **Final Cut Pro 통합** | ✅ FCP X | ✅ NLE 통합 | ✅ FCP X | ✅ Via 앱 |
| **트랜스코딩** | ✅ Intelligent proxies | ✅ Built-in | ✅ Cantemo Transcode Framework | ✅ Native |
| **아카이빙** | ✅ 자동 계층화 | ✅ LTO/Cloud | ✅ StorNext/DIVArchive/P5 | ✅ Multi-site replication |
| **API** | ✅ RESTful API | ✅ RESTful API | ✅ Open API | ✅ VidiCore API (MAM 백본) |
| **배포 속도** | ✅ 수일 (클라우드) | ⚠️ 수주~수개월 | ⚠️ 수주 | ⚠️ 수주 (개발 필요) |
| **커스터마이징** | ⚠️ 제한적 | ✅ 높음 | ✅ 매우 높음 | ✅ 최고 (API 기반) |

### 2.2 DAM 솔루션 (범용 디지털 자산)

| 기능 | MediaSilo | Frame.io | Canto | Brandfolder |
|------|-----------|----------|-------|-------------|
| **비디오 특화** | ✅ 비디오 협업 중심 | ✅ 비디오 리뷰 중심 | ⚠️ 범용 (비디오 포함) | ⚠️ 범용 (브랜드 자산) |
| **AI 자동 태깅** | ❌ 미지원 | ⚠️ 제한적 | ✅ Smart Tags | ✅ Auto-Tagging |
| **AI 전사** | ❌ | ⚠️ 제한적 | ⚠️ 제한적 | ✅ Speech-to-text |
| **안면 인식** | ❌ | ❌ | ✅ Facial recognition | ⚠️ 제한적 |
| **프레임 정확 주석** | ✅ Timecode comments | ✅ Time-stamped comments | ⚠️ 제한적 | ⚠️ 제한적 |
| **Adobe 통합** | ✅ Premiere/Resolve Panel | ✅ Premiere/AE/FCP | ✅ Adobe CC | ✅ Adobe CC/Figma |
| **트랜스코딩** | ✅ Adaptive streaming | ✅ 4K playback | ⚠️ 제한적 | ✅ Advanced Video Editor |
| **OTT 워크플로우** | ⚠️ 제한적 | ⚠️ 제한적 | ❌ | ❌ |
| **브랜드 관리** | ❌ | ❌ | ✅ Brand guidelines | ✅ Templating |
| **API** | ✅ RESTful API | ✅ V4 API (2025) | ❌ 정보 부족 | ✅ JSON RESTful API |
| **NAS 연동** | ❌ 클라우드 전용 | ❌ 클라우드 전용 | ❌ | ❌ |

---

## 3. AI/ML 기능 심층 비교

| 기능 | iconik | Dalet | Cantemo | MediaSilo | Frame.io | Canto | Brandfolder |
|------|--------|-------|---------|-----------|----------|-------|-------------|
| **객체 인식** | ✅ | Via 3rd | Via 3rd | ❌ | ⚠️ | ✅ | ✅ |
| **안면 인식** | ✅ | Via 3rd | Via 3rd | ❌ | ❌ | ✅ | ⚠️ |
| **음성-텍스트** | ✅ | Via 3rd | Via 3rd | ❌ | ⚠️ | ⚠️ | ✅ |
| **장면 이해** | ✅ | Via 3rd | Via 3rd | ❌ | ❌ | ❌ | ❌ |
| **로고 인식** | ✅ | Via 3rd | Via 3rd | ❌ | ❌ | ❌ | ❌ |
| **OCR** | ✅ | Via 3rd | Via 3rd | ❌ | ❌ | ❌ | ✅ |
| **감정 분석** | ⚠️ | Via 3rd | Via 3rd | ❌ | ❌ | ❌ | ❌ |
| **컨텍스트 태깅** | ✅ | Via 3rd | Via 3rd | ❌ | ❌ | ✅ | ✅ |

**AI 성능 순위 (2025 기준)**:
1. **iconik** - Built-in AI, 가장 포괄적
2. **Canto** - 63% 향상된 키워드 생성 (2025)
3. **Brandfolder** - Scene detection, speech-to-text
4. **Dalet/Cantemo** - 3rd party 통합 필요
5. **MediaSilo/Frame.io** - 제한적 또는 미지원

---

## 4. 스토리지 통합 비교

| 솔루션 | On-premise NAS | SMB/CIFS | NFS | LTO Tape | AWS S3 | Azure | Google Cloud |
|--------|---------------|----------|-----|----------|--------|-------|--------------|
| **iconik** | ✅ ISG | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Dalet** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Cantemo** | ✅ | ✅ | ✅ | ✅ StorNext | ✅ | ✅ | ⚠️ |
| **Vidispine** | ✅ VSA | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| **MediaSilo** | ❌ | ❌ | ❌ | ❌ | Cloud only | Cloud only | Cloud only |
| **Frame.io** | ❌ | ❌ | ❌ | ❌ | Cloud only | Cloud only | Cloud only |
| **Canto** | ⚠️ 제한적 | ⚠️ | ⚠️ | ❌ | ✅ | ⚠️ | ⚠️ |
| **Brandfolder** | ❌ | ❌ | ❌ | ❌ | Cloud only | Cloud only | Cloud only |

**18TB+ 아카이브에 적합한 순서**:
1. **iconik** - BYOS, ISG를 통한 완전한 하이브리드
2. **Dalet** - 엔터프라이즈급 멀티 스토리지
3. **Cantemo** - StorNext/DIVArchive 네이티브 지원
4. **Vidispine** - VSA를 통한 하이브리드 (개발 필요)

---

## 5. 가격 정책 상세

### 5.1 명시된 가격

| 솔루션 | Entry 가격 | Mid-tier | Enterprise | 스토리지 |
|--------|-----------|----------|-----------|----------|
| **iconik** | $250/월 | 사용량 기반 | 커스텀 | BYOS (무료) |
| **MediaSilo** | $15/사용자/월 (Team) | $25/사용자/월 (Pro) | $999/월 | 1TB~3TB 포함 |
| **Frame.io** | Free (2GB) | $15/사용자/월 (Pro 2TB) | $25/사용자/월 (Team 3TB) | 포함됨 |

### 5.2 커스텀 견적 (공개 가격 없음)

- **Dalet**: Enterprise급, 대규모 방송사 타겟 (추정 $50K+/년)
- **Cantemo**: 요구사항 기반 견적
- **Vidispine**: 개발 프로젝트 기반 견적
- **Canto**: 사용자 수 + 스토리지 기반
- **Brandfolder**: Basic~Enterprise, 데모 후 견적

### 5.3 TCO (Total Cost of Ownership) 예측 (18TB 아카이브 기준)

| 솔루션 | 초기 비용 | 연간 비용 (5명) | 연간 비용 (15명) | 스토리지 비용 | 비고 |
|--------|----------|----------------|----------------|--------------|------|
| **iconik** | $0 (클라우드) | ~$3K-6K | ~$6K-12K | $0 (BYOS) | 가장 명확한 가격 |
| **Dalet** | $50K-200K+ | $50K-150K | $100K-300K | 포함 | 엔터프라이즈급 |
| **Cantemo** | $30K-100K | $30K-100K | $60K-200K | 포함 | 커스터마이징 필요 |
| **Vidispine** | $50K+ (개발) | $50K-100K | $100K-200K | 포함 | 개발 리소스 필요 |
| **MediaSilo** | $0 | $900-1.8K | $2.7K-5.4K | 추가 스토리지 필요 | 18TB 미지원 |
| **Frame.io** | $0 | $900-1.8K | $2.7K-5.4K | 추가 스토리지 필요 | 18TB 미지원 |
| **Canto** | $0 | ~$10K-20K | ~$20K-40K | 18TB 추가 비용 | 스토리지 제약 |
| **Brandfolder** | $0 | ~$12K-24K | ~$24K-48K | 포함 (제한적) | 비디오 특화 아님 |

---

## 6. 장단점 비교

### 6.1 iconik

**장점**:
- ✅ 가장 빠른 배포 (수일 내)
- ✅ BYOS로 기존 18TB NAS 활용 가능
- ✅ Built-in AI (태깅, 전사, 안면 인식)
- ✅ 무제한 사용자 (비활성 사용자는 과금 안됨)
- ✅ 투명한 가격 정책
- ✅ Adobe/FCP 네이티브 통합
- ✅ 클라우드 네이티브 (유지보수 불필요)

**단점**:
- ❌ Startup (Cantemo 그룹 분사, 상대적으로 짧은 역사)
- ❌ 커스터마이징 제한적
- ❌ 복잡한 방송 워크플로우는 제한적
- ⚠️ 한글 지원 정보 부족

**적합성 (포커 아카이브)**: ⭐⭐⭐⭐⭐ (5/5)

### 6.2 Dalet

**장점**:
- ✅ 엔터프라이즈급 안정성
- ✅ 방송사 레퍼런스 다수 (스포츠 특화)
- ✅ 복잡한 워크플로우 오케스트레이션
- ✅ LTO/Cloud 아카이빙 네이티브
- ✅ 높은 커스터마이징

**단점**:
- ❌ 높은 초기 비용 ($50K+)
- ❌ 긴 구축 기간 (수주~수개월)
- ❌ 높은 IT 리소스 요구
- ❌ 가파른 학습 곡선

**적합성 (포커 아카이브)**: ⭐⭐⭐ (3/5) - 오버스펙

### 6.3 Cantemo

**장점**:
- ✅ BBC, NASA 등 대형 레퍼런스
- ✅ Frame-accurate 메타데이터
- ✅ StorNext/DIVArchive 네이티브
- ✅ Vidispine API 기반 (안정성)
- ✅ 높은 확장성

**단점**:
- ❌ On-premise 배포 복잡도
- ❌ 가격 정보 불투명
- ❌ AI 기능은 3rd party 의존
- ⚠️ iconik 대비 구식 아키텍처

**적합성 (포커 아카이브)**: ⭐⭐⭐⭐ (4/5) - 안정적이지만 복잡

### 6.4 Vidispine

**장점**:
- ✅ MAM 백본 API (최대 유연성)
- ✅ 하이브리드 클라우드 아키텍처
- ✅ Backward-compatible API
- ✅ AWS Elemental 통합

**단점**:
- ❌ UI 없음 (개발 필요)
- ❌ 높은 초기 개발 비용
- ❌ 전문 개발팀 필요
- ❌ 긴 구축 기간

**적합성 (포커 아카이브)**: ⭐⭐ (2/5) - 개발 리소스 없으면 부적합

### 6.5 MediaSilo

**장점**:
- ✅ 저렴한 가격 ($15/사용자)
- ✅ 비디오 협업 특화
- ✅ Timecode 주석
- ✅ 빠른 배포

**단점**:
- ❌ NAS 연동 없음 (클라우드 전용)
- ❌ 18TB 업로드 비용/시간 막대
- ❌ AI 기능 미약
- ❌ 아카이빙 기능 부족

**적합성 (포커 아카이브)**: ⭐⭐ (2/5) - 18TB 마이그레이션 불가

### 6.6 Frame.io

**장점**:
- ✅ 최고의 비디오 리뷰 UI
- ✅ Camera to Cloud
- ✅ Adobe Workfront 통합
- ✅ 크리에이터 친화적

**단점**:
- ❌ NAS 연동 없음
- ❌ 18TB 마이그레이션 문제
- ❌ AI 기능 제한적
- ❌ MAM 수준 기능 부족

**적합성 (포커 아카이브)**: ⭐⭐ (2/5) - 협업 도구일 뿐, MAM 아님

### 6.7 Canto

**장점**:
- ✅ 강력한 AI (63% 향상된 태깅)
- ✅ 안면 인식
- ✅ PIM 통합
- ✅ 엔터프라이즈 보안

**단점**:
- ❌ 비디오 특화 아님 (범용 DAM)
- ❌ NAS 연동 제한적
- ❌ 18TB 스토리지 비용 높음
- ❌ 프레임 정확 편집 미약

**적합성 (포커 아카이브)**: ⭐⭐ (2/5) - DAM이지 MAM 아님

### 6.8 Brandfolder

**장점**:
- ✅ 브랜드 관리 특화
- ✅ Templating
- ✅ Video Editor 내장
- ✅ Salesforce/HubSpot 통합

**단점**:
- ❌ 브랜드 자산 중심 (방송 아님)
- ❌ NAS 연동 없음
- ❌ 18TB 마이그레이션 불가
- ❌ OTT 워크플로우 부족

**적합성 (포커 아카이브)**: ⭐ (1/5) - 완전히 다른 유스케이스

---

## 7. 포커 방송 아카이브 특화 추천

### 7.1 최우선 추천: **iconik**

**이유**:
1. **BYOS (Bring Your Own Storage)** - 기존 18TB NAS를 그대로 사용, 마이그레이션 불필요
2. **ISG (iconik Storage Gateway)** - SMB/NAS를 클라우드 MAM과 연결
3. **Built-in AI** - 포커 게임 장면, 플레이어 얼굴, 음성 전사 자동화
4. **빠른 배포** - 수일 내 구축 가능
5. **투명한 가격** - $250/월 시작, 사용량 기반
6. **OTT 친화적** - Adaptive streaming, AWS/Azure 통합

**구축 로드맵 (1주)**:
- Day 1: iconik 계정 생성 + ISG 설치 (Windows Server)
- Day 2: NAS 18TB 연결 (SMB 경로 매핑)
- Day 3: AI 자동 태깅 설정 (포커 용어, 플레이어 이름)
- Day 4: Adobe Premiere 통합 테스트
- Day 5: OTT 플랫폼 API 연동 (배포 워크플로우)
- Day 6-7: 사용자 교육 + 파일럿 런

**예상 비용 (1년)**:
- iconik 구독: $3,000 - $6,000 (5명 기준)
- ISG 서버: $1,000 (1회)
- 기존 NAS 활용: $0
- **총 TCO**: ~$7,000

---

### 7.2 차선책: **Cantemo**

**이유**:
1. **Vidispine 백본** - 방송급 안정성
2. **Frame-accurate logging** - 포커 핸드별 정확한 타임코드
3. **StorNext 통합** - 대용량 아카이브 최적화
4. **BBC/NASA 레퍼런스** - 검증된 신뢰성

**단점**:
- 높은 구축 비용 ($30K-100K)
- 긴 구축 기간 (4-8주)
- AI는 3rd party 통합 필요

**적합 시나리오**: 예산이 충분하고, 장기적으로 방송사급 인프라 구축 계획

---

### 7.3 예산 제약 시: **Archive Analyzer (자체 솔루션) + MediaSilo**

현재 Archive Analyzer의 메타데이터 추출 기능을 활용하고, 협업 리뷰용으로만 MediaSilo 사용.

**장점**:
- Archive Analyzer: 메타데이터 추출 (FFprobe, SQLite)
- MediaSilo: 협업 리뷰 ($15/사용자)
- 낮은 비용 (~$1,800/년)

**단점**:
- AI 기능 없음
- 수동 업로드 필요
- OTT 통합 제한적

---

## 8. MAM vs DAM 선택 가이드 (포커 아카이브 기준)

| 요구사항 | MAM 필요 | DAM 충분 |
|---------|---------|---------|
| **18TB+ 대용량** | ✅ NAS 연동 필수 | ❌ 클라우드 마이그레이션 비용 막대 |
| **프레임 정확 편집** | ✅ Time-coded metadata | ❌ 제한적 |
| **포커 하이라이트 클립** | ✅ Proxy workflows | ⚠️ 수동 작업 |
| **OTT 배포** | ✅ Transcoding pipelines | ⚠️ 별도 도구 필요 |
| **AI 태깅** | ✅ iconik/Canto | ✅ Canto |
| **협업 리뷰** | ✅ 모든 솔루션 | ✅ Frame.io/MediaSilo |
| **브랜드 자산 관리** | ⚠️ 부가 기능 | ✅ Brandfolder |

**결론**: 포커 방송 아카이브는 **MAM 솔루션**이 필수. DAM은 부족.

---

## 9. 체크리스트: 솔루션 선택 전 확인사항

### 9.1 기술 요구사항
- [ ] 기존 NAS (18TB+) 연동 가능한가?
- [ ] SMB/CIFS 프로토콜 지원하는가?
- [ ] AI 자동 태깅 (포커 용어, 플레이어) 가능한가?
- [ ] 음성 전사 (영어 해설) 지원하는가?
- [ ] Frame-accurate 편집 가능한가?
- [ ] OTT 플랫폼 API 연동 가능한가?
- [ ] Adobe Premiere Pro 통합되는가?

### 9.2 비즈니스 요구사항
- [ ] 1주 이내 배포 가능한가?
- [ ] 예산 $10K 이내인가?
- [ ] 사용자 5-15명 지원하는가?
- [ ] 무제한 뷰어 (시청자) 가능한가?
- [ ] 투명한 가격 정책인가?
- [ ] 클라우드 네이티브 (유지보수 불필요)인가?

### 9.3 워크플로우 요구사항
- [ ] 포커 토너먼트별 폴더 구조 유지되는가?
- [ ] 플레이어별 검색 가능한가?
- [ ] WSOP/HCL/PAD 카테고리 분류 가능한가?
- [ ] 하이라이트 클립 자동 생성 가능한가?
- [ ] OTT 플랫폼에 원클릭 배포 가능한가?

**iconik는 위 모든 체크리스트를 만족합니다.**

---

## 10. 참고 자료

### Sources

#### iconik
- [Media Asset Management Software | Iconik](https://www.iconik.io/)
- [iconik Reviews 2025: Details, Pricing, & Features | G2](https://www.g2.com/products/iconik/reviews)
- [iconik Pricing 2025](https://www.g2.com/products/iconik/pricing)
- [Iconik API Basics: Exploring Assets, Metadata, and Jobs](https://trackit.io/iconik-api-basics/)

#### Dalet
- [Media Asset Management (MAM) - Manage rich content efficiently | Dalet](https://www.dalet.com/solutions/media-asset-management/)
- [Cloud Based Media Asset Management Explained](https://www.dalet.com/blog/cloud-based-media-asset-management-mam/)

#### Cantemo
- [Cantemo Portal: Next-Gen Media Asset Management Solution](https://turnipbox.netlify.app/)
- [Cantemo Open API](https://www.cantemo.com/open-api/)
- [Changing the Media Asset Management Paradigm | Cantemo](https://www.cantemo.com/portal.html)

#### Vidispine
- [Solution_Media Asset Management](https://vidispine.com/solution_media-asset-management)
- [Media Asset Management solutions by Vidispine](https://www.vidispine.com/media-asset-management/mam-solutions)
- [Customer Case: ITV Using Vidispine API](https://www.vidispine.com/about/arvato-systems-vidispine/customer-cases/itv)

#### MediaSilo
- [MediaSilo: The Smarter Way to Collaborate on Video](https://www.mediasilo.com/mediasilo)
- [MediaSilo Pricing & Signup](https://www.mediasilo.com/pricing)
- [MediaSilo Features](https://www.mediasilo.com/features)

#### Frame.io
- [Frame.io Ecosystem and Integrations: Powering Creative Workflows Across APIs](https://blog.frame.io/2025/06/03/frame-io-ecosystem-and-integrations-powering-creative-workflows-across-apis/)
- [Frame.io Pricing](https://frame.io/pricing)
- [Frame.io Integrations](https://frame.io/integrations)

#### Canto
- [Canto Pricing | Flexible DAM & PIM Plans for Businesses](https://www.canto.com/pricing/)
- [The Canto Platform: DAM + PIM with AI & Workflow Add-ons](https://www.canto.com/product/)
- [The Future of DAM: AI-Powered Search](https://www.canto.com/blog/ai-powered-search/)

#### Brandfolder
- [Digital Asset Management Software | Enterprise DAM | Brandfolder](https://brandfolder.com/product/)
- [Digital Asset Management Pricing Plans | Brandfolder](https://brandfolder.com/pricing/)
- [Digital Asset Management (DAM) Integrations | Brandfolder](https://brandfolder.com/integrations/)

#### MAM vs DAM
- [What is MAM? | Differences and Definitions Between DAM vs. MAM](https://www.mediavalet.com/blog/digital-asset-management-vs-media-asset-management)
- [Digital Media Asset Management For Broadcast and OTT](https://actusdigital.com/digital-media-asset-management-broadcast-and-ott/)
- [MAM vs. DAM: What's the difference? | TechTarget](https://www.techtarget.com/searchcontentmanagement/feature/MAM-vs-DAM-Whats-the-difference)

#### AI Features
- [AI in DAM: Transform Asset Management with Artificial Intelligence](https://www.mediavalet.com/product/artificial-intelligence)
- [How AI can practically enhance your media asset management system](https://wasabi.com/blog/media-entertainment/ai-enhance-media-asset-management)
- [Optimizing Media Asset Management with Facial Recognition and Machine Learning](https://medium.com/firstlineoutsourcing/optimizing-media-asset-management-with-facial-recognition-and-machine-learning-e335ddded753)

#### Sports/Broadcast MAM
- [Why You Must Capture Robust Metadata to Enrich Your Sports Live Feeds](https://blog.ipv.com/metadata-for-sports)
- [Sports Content Monetization: 5 Ways to Monetize Video Archives | Dalet](https://www.dalet.com/blog/sports-content-monetization-video-media-archives/)

#### Hybrid Cloud Storage
- [HybridMount | QNAP](https://www.qnap.com/en-us/software/hybridmount)
- [Hybrid Cloud Asset & Archive Management - StorageDNA](https://storagedna.com/solutions/by-workflows/hybrid-cloud-asset-archive-management/)
- [From on premises to AWS: Hybrid-cloud architecture for network file shares](https://aws.amazon.com/blogs/storage/from-on-premises-to-aws-hybrid-cloud-architecture-for-network-file-shares/)

---

## 11. 최종 권장사항 요약

### 🥇 1순위: **iconik**
- **가격**: $3K-6K/년
- **배포**: 1주
- **NAS 연동**: ✅ ISG
- **AI**: ✅ Built-in
- **적합도**: ⭐⭐⭐⭐⭐

### 🥈 2순위: **Cantemo**
- **가격**: $30K-100K/년
- **배포**: 4-8주
- **NAS 연동**: ✅ Native
- **AI**: ⚠️ 3rd party
- **적합도**: ⭐⭐⭐⭐

### 🥉 3순위: **Dalet**
- **가격**: $50K-150K/년
- **배포**: 8-16주
- **NAS 연동**: ✅ Native
- **AI**: ⚠️ 3rd party
- **적합도**: ⭐⭐⭐ (오버스펙)

### ❌ 비추천: MediaSilo, Frame.io, Canto, Brandfolder
- NAS 연동 불가 또는 18TB 마이그레이션 비현실적

---

**다음 단계**: iconik 14일 무료 체험 + ISG 설치 테스트 권장
