# PRD-0005: GG Production 자막 워크 플로우

| 항목 | 값 |
|------|-----|
| **Version** | 2.0 |
| **Status** | Draft |
| **Priority** | P0 |
| **Created** | 2025-01-08 |
| **Updated** | 2025-01-08 |
| **Author** | Automation Team |

---

## 1. 개요

### 1.1 목적

WSOP 방송 프로덕션의 **전체 데이터 흐름**을 정의하고, **4인 작업 -> 1인 운영** 자동화를 통한 효율화 달성.

### 1.2 핵심 목표

| 지표 | AS-IS | TO-BE |
|------|:-----:|:-----:|
| **운영 인력** | 4명 | **1명** |
| **프로세스 단계** | 9단계 | **5단계** |
| **수동 작업** | 90% | **20%** |

### 1.3 인력 효율화

| 역할 | AS-IS | TO-BE |
|------|:-----:|:-----:|
| 자막 작업 | 2명 | - |
| 편집/렌더링/출력 | 2명 | - |
| **운영 관리자** | - | **1명** |
| **합계** | **4명** | **1명** |

---

## 2. 프로세스 비교

### 2.1 AS-IS (기존 방식)

```
GFX -> 구글 시트 -> 수동 매핑 -> 큐시트 업로드 -> 수동 다운로드 -> AE 작업 -> AE 렌더링 -> 파일 전달 -> 최종 편집
```

**9단계 수동 프로세스**:

| 단계 | 작업 | 담당 | 문제점 |
|:----:|------|------|--------|
| 1 | GFX 데이터 수집 | 자동 | - |
| 2 | 구글 시트 입력 | 수동 | 오타, 누락 |
| 3 | 수동 매핑 | 수동 | 시간 소요 |
| 4 | 큐시트 업로드 | 수동 | 형식 오류 |
| 5 | 수동 다운로드 | 수동 | 버전 혼란 |
| 6 | AE 작업 | 수동 | 반복 작업 |
| 7 | AE 렌더링 | 반자동 | 대기 시간 |
| 8 | 파일 전달 | 수동 | 경로 오류 |
| 9 | 최종 편집 | 수동 | - |

### 2.2 TO-BE (자동화)

```
GFX -> DB -> Select -> AE Export -> Final Edit
```

**5단계 자동화 프로세스**:

| 단계 | 작업 | 담당 | 개선점 |
|:----:|------|------|--------|
| 1 | GFX 데이터 수집 | 자동 | RFID + WSOP+ |
| 2 | DB 저장/구조화 | 자동 | 실시간 동기화 |
| 3 | 데이터 선택 | **운영 관리자** | UI 기반 선택 |
| 4 | AE Export | 자동 | 원클릭 렌더링 |
| 5 | Final Edit | **운영 관리자** | 최종 확인 |

![AS-IS TO-BE 비교](/docs/unified/images/hub-0005-as-is-to-be.png)

---

## 3. 프로덕션 워크플로우

### 3.1 전체 흐름

![전체 워크플로우](/docs/unified/images/hub-0005-workflow.png)

### 3.2 Phase별 상세

#### Phase 1: 데이터 입력

| 소스 | 형태 | 처리 | 프로젝트 |
|------|------|------|----------|
| **RFID** | 실시간 | 자동 | automation_feature_table |
| **WSOP+** | CSV -> API | 자동 | 외부 연동 |
| **Manual** | 수작업 | 운영 관리자 | automation_sub UI |

#### Phase 2: 데이터 관리 (automation_sub)

| 기능 | 설명 | 담당 |
|------|------|------|
| DB 저장 | 원시 데이터 구조화 | 자동 |
| 검증 | 데이터 정합성 확인 | 운영 관리자 |
| 가공 | 방송용 데이터 편집 | 운영 관리자 |
| 수작업 입력 | 누락 데이터 보정 | 운영 관리자 |

#### Phase 3: 데이터 출력 (automation_ae)

| 기능 | 설명 | 담당 |
|------|------|------|
| 데이터 선택 | 방송할 핸드 선택 | 운영 관리자 |
| 렌더링 실행 | AE 템플릿 적용 | 자동 |
| 출력물 생성 | 영상 파일 생성 | 자동 |
| 최종 확인 | 품질 검수 | 운영 관리자 |

---

## 4. 논리적 시스템 아키텍처

### 4.1 프로젝트 구조

![시스템 아키텍처](/docs/unified/images/hub-0005-architecture.png)

### 4.2 프로젝트별 역할

| 프로젝트 | Phase | 역할 | 핵심 기능 |
|----------|:-----:|------|-----------|
| **automation_feature_table** | 1 | 데이터 입력 | RFID 카드 인식, Hand 데이터 생성 |
| **automation_sub** | 2 | 데이터 관리 | DB 구조화, 운영자 UI, 검증/가공 |
| **automation_ae** | 3 | 데이터 출력 | AE 렌더링, 출력물 생성 |
| **automation_hub** | 전체 | 공유 인프라 | DB, 모델, Repository, 모니터링 |

### 4.3 데이터 흐름

![데이터 흐름도](/docs/unified/images/hub-0005-data-flow.png)

---

## 5. 물리적 배포 아키텍처

### 5.1 3-App Architecture 개요

**3개 앱**을 실행하여 전체 프로세스 처리:

| 앱 | 역할 | 실행 환경 |
|----|------|----------|
| **App 1: NAS Container** | JSON 파일 감시 + DB 마이그레이션 | NAS Docker Container |
| **App 2: 프런트 서버** | 프런트엔드 + DB 관리 + 자막 출력 | 웹 서버 |
| **App 3: Nexrender** | AE 렌더링 | Windows PC (AE 라이선스) |

![3-App 아키텍처](/docs/unified/images/hub-0005-3app-architecture.png)

### 5.2 App 1: NAS Container 앱 서버

**역할**: GFX PC에서 생성된 JSON 파일을 감시하고 DB에 저장

```
GFX PC -> JSON 파일 생성 -> NAS 동기화 -> App 1 (watchdog) -> DB 저장
```

**구성 요소**:

| 컴포넌트 | 파일 | 설명 |
|----------|------|------|
| JSONFileWatcher | `json_file_watcher.py` | PollingObserver로 2초 간격 파일 감시 |
| PokerGFXFileParser | `pokergfx_file_parser.py` | JSON 파싱 + Hand 데이터 변환 |
| HandsRepository | `repositories.py` | PostgreSQL 저장 |

**설정**:

```env
POKERGFX_MODE=json
POKERGFX_JSON_PATH=/nas/pokergfx
POKERGFX_POLLING_INTERVAL=2.0
POKERGFX_FILE_PATTERN=*.json
```

**기존 구현**: `automation_feature_table/src/primary/json_file_watcher.py`

### 5.3 App 2: 프런트 앱 서버

**역할**: 운영 관리자 UI + DB 관리 + 자막 출력 선택/실행

```
운영자 (브라우저) -> React UI -> FastAPI -> PostgreSQL
                                      -> RenderInstruction 생성
```

**구성 요소**:

| 컴포넌트 | 포트 | 설명 |
|----------|------|------|
| React Frontend | 3000 (dev) / 8080 (prod) | 대시보드 UI |
| FastAPI Backend | 8080 | REST API + WebSocket |
| DB 연결 | 5432 | PostgreSQL 연결 |

**주요 기능**:

| 기능 | 설명 |
|------|------|
| Hand 목록 | 입력된 핸드 데이터 조회/편집 |
| 수작업 입력 | Manual 데이터 입력 폼 |
| 렌더링 선택 | 방송할 핸드 선택 |
| 렌더링 큐 | 진행 중인 작업 상태 |
| 출력물 확인 | 완료된 렌더링 결과 |

**의존**: PRD-0004 (프론트엔드 대시보드)

### 5.4 App 3: Nexrender 서버

**역할**: AE 템플릿 기반 자동 렌더링

```
render_instructions (pending) -> Nexrender Worker -> After Effects -> NAS Output
```

**구성 요소**:

| 컴포넌트 | 설명 |
|----------|------|
| Nexrender Worker | render_instructions 테이블 polling (5초 간격) |
| After Effects | 템플릿 프로젝트 (.aep) 렌더링 |
| Output Storage | NAS 공유 폴더에 결과물 저장 |

**작업 흐름**:

1. `render_instructions` 테이블에서 `status=pending` 조회
2. `status=processing`으로 업데이트
3. AE 템플릿에 `layer_data` 주입
4. 렌더링 실행
5. `status=completed` 업데이트 + `render_outputs` 저장
6. 실패 시 `status=failed` + `error_message` 기록

**실행 환경**: Windows PC (After Effects 라이선스 필요)

---

## 6. 네트워크 토폴로지

### 6.1 서버 간 통신

![네트워크 토폴로지](/docs/unified/images/hub-0005-network-topology.png)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  GFX PC     │     │  NAS        │     │  App 1      │
│  (PokerGFX) │────>│  SMB Share  │<────│  Container  │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                           │                    │ TCP 5432
                           │                    ▼
                    ┌──────┴──────┐     ┌─────────────┐
                    │  Output     │<────│  PostgreSQL │
                    │  \\NAS\out  │     │             │
                    └─────────────┘     └──────┬──────┘
                           ▲                   │
                           │            ┌──────┴──────┐
                    ┌──────┴──────┐     │  App 2      │
                    │  App 3      │<────│  Frontend   │
                    │  Nexrender  │     │  + API      │
                    └─────────────┘     └─────────────┘
```

### 6.2 포트 매핑

| 서비스 | 포트 | 프로토콜 | 용도 |
|--------|------|----------|------|
| NAS SMB | 445 | TCP | JSON/Output 파일 공유 |
| PostgreSQL | 5432 | TCP | DB 연결 (모든 앱) |
| Frontend API | 8080 | HTTP | REST + WebSocket |
| Frontend Dev | 3000 | HTTP | React 개발 서버 |
| Redis | 6379 | TCP | 작업 큐 (PRD-0001 v2.0) |

### 6.3 NAS 마운트 설정

**Windows**:
```powershell
# 네트워크 드라이브 연결
net use Z: \\NAS\pokergfx /persistent:yes
net use Y: \\NAS\output /persistent:yes
```

**Docker (Linux Container)**:
```yaml
volumes:
  - type: bind
    source: //NAS/pokergfx
    target: /nas/pokergfx
    read_only: true
```

---

## 7. Docker 구성

### 7.1 docker-compose.yml 확장

```yaml
version: '3.8'

services:
  # 공유 인프라 - PostgreSQL
  postgres:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/01-init.sql

  # Redis (PRD-0001 v2.0, 선택)
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    profiles: [full]

  # App 1: NAS Watcher
  nas-watcher:
    build:
      context: ../automation_feature_table
      dockerfile: Dockerfile.watcher
    environment:
      POKERGFX_MODE: json
      POKERGFX_JSON_PATH: /nas/pokergfx
    volumes:
      - //NAS/pokergfx:/nas/pokergfx:ro
    depends_on:
      postgres:
        condition: service_healthy

  # App 2: Frontend + API
  frontend-api:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports: ["8080:8080"]
    depends_on:
      postgres:
        condition: service_healthy

  # App 3: Nexrender (Windows 전용 - 주석 처리)
  # nexrender:
  #   profiles: [nexrender]
```

### 7.2 앱별 Dockerfile

| 앱 | Dockerfile | Base Image |
|----|------------|------------|
| App 1 | `Dockerfile.watcher` | python:3.11-slim |
| App 2 | `Dockerfile.frontend` | node:20-alpine (multi-stage) |
| App 3 | - | Windows 직접 실행 |

### 7.3 배포 프로파일

```bash
# 기본 (PostgreSQL + App 1 + App 2)
docker-compose up -d

# Full (Redis 포함)
docker-compose --profile full up -d

# Nexrender (Windows에서 별도 실행)
# npx nexrender-worker --host localhost --port 3000
```

---

## 8. 운영자 UI

### 8.1 운영 관리자 대시보드

운영 관리자가 Phase 2 + Phase 3를 단일 UI에서 처리:

| 화면 | 기능 | Phase |
|------|------|:-----:|
| **Hand 목록** | 입력된 Hand 데이터 확인/편집 | 2 |
| **수작업 입력** | Manual 데이터 입력 폼 | 1 |
| **데이터 검증** | 오류/누락 데이터 표시 | 2 |
| **렌더링 선택** | 방송할 Hand 선택 | 3 |
| **렌더링 큐** | 진행 중인 렌더링 상태 | 3 |
| **출력물 확인** | 완료된 렌더링 결과 | 3 |

![운영자 대시보드](/docs/unified/images/hub-0005-operator-dashboard.png)

### 8.2 화면 흐름

![화면 흐름](/docs/unified/images/hub-0005-screen-flow.png)

---

## 9. 연관 PRD 및 의존성

### 9.1 PRD 의존성 그래프

```
                    ┌────────────────┐
                    │   PRD-0001     │
                    │ automation_hub │
                    │   v2.0 (인프라)│
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────────┐
        │                   │                       │
        ▼                   ▼                       ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│   PRD-0002     │ │   PRD-0003     │ │   PRD-0004     │
│ 충돌 모니터링  │ │ 모델 통합      │ │ Frontend       │
└────────────────┘ └───────┬────────┘ └───────┬────────┘
                           │                  │
                           └──────────┬───────┘
                                      │
                                      ▼
                           ┌────────────────────┐
                           │     PRD-0005       │
                           │  Production        │
                           │  Workflow (통합)   │
                           └────────────────────┘
```

### 9.2 의존성 매트릭스

| PRD-0005 컴포넌트 | 의존 PRD | 필요 산출물 |
|-------------------|----------|-------------|
| **App 1: NAS Watcher** | PRD-0003 | shared/models/Hand, SourceType |
| **App 1: NAS Watcher** | PRD-0001 | Database, HandsRepository |
| **App 2: Frontend** | PRD-0004 | React 대시보드, DB 운영자 UI |
| **App 2: Frontend** | PRD-0001 | FastAPI, WebSocket, Basic Auth |
| **App 2: 렌더링 선택** | PRD-0003 | RenderInstruction, Template |
| **App 2: 렌더링 큐** | PRD-0001 | Redis Stream (v2.0) or DB Polling |
| **App 3: Nexrender** | PRD-0001 | render_instructions polling |
| **충돌 감지** | PRD-0002 | ConflictMonitor, GitHub Issues |

### 9.3 통합 순서 (권장)

| Phase | 작업 | PRD |
|:-----:|------|-----|
| A | PostgreSQL + shared/models + shared/db | PRD-0001 (완료) |
| B | JSONFileWatcher + App 1 Docker화 | PRD-0003 |
| C | Frontend 대시보드 + FastAPI API | PRD-0004 + PRD-0001 |
| D | Nexrender + render_instructions polling | PRD-0001 |
| E | Redis Stream + WebSocket + 충돌 모니터링 | PRD-0001 v2.0 + PRD-0002 |

---

## 10. 시각화 산출물

### 10.1 기존 HTML 목업 (6개)

| 파일명 | 내용 |
|--------|------|
| `prd-0005-as-is-to-be.html` | AS-IS vs TO-BE 프로세스 비교 |
| `prd-0005-workflow.html` | 전체 워크플로우 (Phase 1-3) |
| `prd-0005-architecture.html` | 논리적 시스템 아키텍처 |
| `prd-0005-data-flow.html` | 데이터 흐름도 |
| `prd-0005-screen-flow.html` | 화면 흐름 |
| `prd-0005-operator-dashboard.html` | 운영자 대시보드 UI 목업 |

### 10.2 신규 HTML 목업 (3개)

| 파일명 | 내용 |
|--------|------|
| `prd-0005-3app-architecture.html` | 3-App 물리적 배포 아키텍처 |
| `prd-0005-network-topology.html` | 네트워크 토폴로지 + 포트 |
| `prd-0005-data-flow-3app.html` | 3개 앱 간 데이터 흐름 |

### 10.3 스크린샷

| 파일명 | 위치 |
|--------|------|
| `prd-0005-as-is-to-be.png` | `docs/images/` |
| `prd-0005-workflow.png` | `docs/images/` |
| `prd-0005-architecture.png` | `docs/images/` |
| `prd-0005-data-flow.png` | `docs/images/` |
| `prd-0005-screen-flow.png` | `docs/images/` |
| `prd-0005-operator-dashboard.png` | `docs/images/` |
| `prd-0005-3app-architecture.png` | `docs/images/` |
| `prd-0005-network-topology.png` | `docs/images/` |
| `prd-0005-data-flow-3app.png` | `docs/images/` |

---

## 11. 용어 정의

| 용어 | 설명 |
|------|------|
| **GFX** | Graphics, 방송 그래픽 데이터 |
| **RFID** | Radio-Frequency Identification, 카드 인식 기술 |
| **WSOP+** | World Series of Poker Plus 앱 |
| **Hand** | 포커 한 판의 데이터 (카드, 액션, 결과) |
| **AE** | Adobe After Effects, 렌더링 소프트웨어 |
| **운영 관리자** | Phase 2+3를 담당하는 1인 운영자 |
| **NAS** | Network Attached Storage, 네트워크 공유 스토리지 |
| **Nexrender** | After Effects 헤드리스 렌더링 엔진 |
| **PollingObserver** | watchdog 라이브러리의 파일 감시 방식 (SMB 호환) |
| **render_instructions** | AE 렌더링 작업 지시서 테이블 |

---

## Appendix

### A. 참조 문서

- [automation_feature_table README](../../../automation_feature_table/README.md)
- [automation_sub README](../../../automation_sub/README.md)
- [automation_ae README](../../../automation_ae/README.md)
- [PRD-0001: Automation Hub v2.0](./HUB-0001-automation-hub-v2.md)
- [PRD-0004: 프론트엔드 대시보드](./HUB-0004-frontend-dashboard.md)

### B. 핵심 파일 참조

| 용도 | 절대 경로 |
|------|---------|
| JSON 파일 감시자 | `C:\claude\automation_feature_table\src\primary\json_file_watcher.py` |
| PokerGFX JSON 파서 | `C:\claude\automation_feature_table\src\primary\pokergfx_file_parser.py` |
| 공유 모델 | `C:\claude\automation_hub\shared\models\` |
| Repository | `C:\claude\automation_hub\shared\db\repositories.py` |
| Docker 구성 | `C:\claude\automation_hub\docker-compose.yml` |

### C. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0 | 2025-01-08 | 초안 작성 |
| 2.0 | 2025-01-08 | 3-App 물리적 배포 아키텍처 추가 (섹션 5-7) |

