# PRD: Workflow Automation System

**PRD Number**: PRD-0002
**Version**: 1.1
**Date**: 2025-12-25
**Status**: Draft
**Parent PRD**: PRD-0001 (WSOP Broadcast Graphics System)

### Changelog
| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-01-05 | OBS/vMix → Korea Production 방송 시스템 변경 |
| 1.0 | 2025-12-25 | Initial PRD - 5대 자동화 영역 정의, AI Agent 아키텍처, automation_ae 통합 |

### Source Documents
| Document | Location |
|----------|----------|
| PRD-0001 | [WSOP Broadcast Graphics](./0001-prd-wsop-broadcast-graphics.md) |
| automation_ae PRD | [AE Automation System](D:\AI\claude01\automation_ae\tasks\prds\0001-prd-ae-automation.md) |

---

## 1. Purpose & Context

### 1.1 Background

PRD-0001 (WSOP Broadcast Graphics System)의 **Phase 6: AI Automation** 요구사항을 상세화한 문서입니다. 기존 PRD에서 정의된 4줄의 자동화 요구사항을 5대 영역으로 확장하고, AI 에이전트 아키텍처를 설계합니다.

**PRD-0001 Phase 6 요구사항**:
```
- [ ] 모니터링 자동화
- [ ] 파일 전송 자동화 (한국 ↔ 현장)
- [ ] 파트별 시트 공유 자동화
- [ ] 통합 테스트
```

### 1.2 Goals

- **데이터 동기화 자동화**: RFID → DB → Google Sheets 실시간 양방향 동기화
- **파일 전송 자동화**: 한국 ↔ 현장(LV/Cyprus) 간 Cloud Storage 기반 자동 전송
- **모니터링 자동화**: 시스템 상태 감시, 이상 감지, 알림 발송
- **그래픽 자동화**: 이벤트 기반 그래픽 트리거, automation_ae 통합
- **AI 기반 의사결정**: OpenAI GPT-4o 활용 자율적 판단 및 실행

### 1.3 Non-Goals

- 그래픽 디자인 제작 (PRD-0001 담당)
- 방송 송출 시스템 운영 (Korea Production에서 담당)
- 3D 렌더링/Virtual Table (별도 프로젝트)

---

## 2. Target Users & Roles

### 2.1 Staff 구조 연동

PRD-0001 Section 12의 Staff 구조와 연동:

| 역할 | 현재 | 자동화 후 | 영향 |
|------|------|----------|------|
| **PA (Monitoring) x3** | 수동 모니터링 | 자동 알림 수신 | 부담 감소 |
| **PA (graphics)** | 수동 데이터 입력 | 자동 동기화 | 부담 감소 |
| **Data Manager** | 역할 미정의 | RFID/시트 관리 | 역할 명확화 |
| **Producer (graphics)** | 수동 그래픽 호출 | 자동 트리거 + 오버라이드 | 워크플로우 개선 |

### 2.2 자동화로 인한 역할 변화

- **PA (Monitoring)**: 알림 대응 및 예외 처리에 집중
- **Data Manager**: 시스템 설정 및 품질 관리 담당
- **PD/Producer**: AI 제안 검토 및 최종 결정권 유지

---

## 3. 5대 자동화 영역

![5 Automation Domains](../../docs/images/automation-domains.png)

### 3.1 Data Synchronization

**Priority**: P0 (Critical)

```
RFID System → Parser Agent → PostgreSQL ↔ Sync Agent → Google Sheets
```

#### 핵심 기능

| 기능 | 설명 | 우선순위 |
|------|------|----------|
| RFID 데이터 수신 | 테이블별 카드 인식 데이터 실시간 수신 | P0 |
| 데이터 파싱 | 원시 RFID 데이터를 구조화된 형식으로 변환 | P0 |
| DB 저장 | PostgreSQL에 핸드/플레이어 데이터 저장 | P0 |
| Sheets 양방향 동기화 | DB ↔ Google Sheets 실시간 동기화 | P0 |
| 충돌 해결 | 동시 수정 시 충돌 감지 및 해결 | P1 |

#### 이벤트 타입

```python
class DataSyncEvent(Enum):
    RFID_DATA_RECEIVED = "data_sync.rfid.received"
    RFID_PARSED = "data_sync.rfid.parsed"
    DB_UPDATED = "data_sync.db.updated"
    SHEETS_SYNCED = "data_sync.sheets.synced"
    SYNC_CONFLICT = "data_sync.conflict"
```

---

### 3.2 File Transfer

**Priority**: P0 (Critical)

```
현장 (LV/Cyprus) → Upload Agent → Cloud Storage → Download Agent → 한국 본사
```

#### 핵심 기능

| 기능 | 설명 | 우선순위 |
|------|------|----------|
| 변경 감지 | 폴더 감시로 새 파일/수정 파일 자동 감지 | P0 |
| 청크 전송 | 대용량 파일 분할 전송 | P0 |
| 무결성 검증 | MD5/SHA256 체크섬 검증 | P0 |
| 자동 재전송 | 실패 시 자동 재전송 (최대 3회) | P1 |
| 대역폭 관리 | 전송 속도 제어 (방송 중 제한) | P2 |

#### 전송 대상 파일

- 그래픽 디자인 변경사항 (.aep, .html)
- Soft Contents 영상/이미지
- 플레이어 프로필 이미지
- 대본/스크립트 업데이트

---

### 3.3 Monitoring

**Priority**: P0 (Critical)

```
Health Check Agent → Anomaly Detection → Alert Agent → Slack/Dashboard
```

#### 핵심 기능

| 기능 | 설명 | 우선순위 |
|------|------|----------|
| 헬스 체크 | RFID, DB, Sheets 연결 상태 확인 | P0 |
| 데이터 오류 감지 | 누락, 중복, 이상치 자동 감지 | P0 |
| 알림 발송 | Slack/Discord/Email 자동 알림 | P0 |
| 대시보드 | PA 모니터링 현황판 제공 | P1 |
| 에스컬레이션 | 심각도별 알림 확대 (Warning → Critical) | P2 |

#### 알림 규칙 예시

```python
ALERT_RULES = [
    {
        "name": "RFID_CONNECTION_LOST",
        "condition": "rfid.connection_status == 'disconnected'",
        "severity": "critical",
        "channels": ["slack", "sms"],
        "cooldown_minutes": 5
    },
    {
        "name": "DATA_SYNC_DELAYED",
        "condition": "sheets.last_sync_seconds > 60",
        "severity": "warning",
        "channels": ["slack"],
        "cooldown_minutes": 10
    }
]
```

---

### 3.4 Graphics Automation (automation_ae 통합)

**Priority**: P1 (High)

![Graphics Automation](../../docs/images/graphics-automation.png)

#### 통합 아키텍처

| 렌더링 엔진 | 기술 | 용도 |
|------------|------|------|
| **After Effects** | Nexrender (automation_ae) | Lower Third, Transitions, Animations |
| **Web Graphics** | Playwright (HTML→PNG) | Leaderboard, Chip Flow, Stats |

#### automation_ae 재사용 컴포넌트

| 컴포넌트 | 파일 | 용도 |
|----------|------|------|
| NAS 출력 관리 | `output_manager.py` | 렌더링 결과 자동 저장 |
| 배치 작업 | `csv_parser.py` | 플레이어 리스트 일괄 처리 |
| 렌더링 워커 | `render_worker.py` | Celery 비동기 처리 |
| WebSocket | 기존 인프라 | 실시간 진행률 |

#### 이벤트-그래픽 매핑

| 이벤트 | 그래픽 액션 | 조건 | 우선순위 |
|--------|------------|------|----------|
| `blind_level_change` | Blind Level 표시 | 항상 | High |
| `player_all_in` | At Risk 오버레이 | ITM 이후 | High |
| `big_pot_completed` | Chip Flow 업데이트 | 팟 > 평균 x2 | Medium |
| `player_eliminated` | Elimination 배너 | 항상 | High |
| `day_transition` | Content Strategy 전환 | 항상 | Low |

---

### 3.5 AI Agent

**Priority**: P1 (High)

![AI Agent Hierarchy](../../docs/images/ai-agent-hierarchy.png)

#### AI Agent 역할

| Agent | 역할 | AI 모델 | 자율성 수준 |
|-------|------|---------|------------|
| **Story Detection** | 스토리라인 추출, 하이라이트 제안 | GPT-4o | 제안만 (PD 승인 필요) |
| **Priority Decision** | 그래픽 우선순위 판단, Day별 비율 조절 | GPT-4o-mini | 자율 (오버라이드 가능) |
| **Anomaly Resolution** | 데이터 오류 자동 수정 | 규칙 기반 + GPT | 범위 제한 자율 |

#### OpenAI API 통합

```python
# GPT-4o: 복잡한 판단 (스토리 분석, 컨텍스트 이해)
# GPT-4o-mini: 비용 효율 작업 (우선순위 판단, 간단한 분류)

AI_CONFIG = {
    "story_detection": {
        "model": "gpt-4o",
        "max_tokens": 500,
        "temperature": 0.7
    },
    "priority_decision": {
        "model": "gpt-4o-mini",
        "max_tokens": 200,
        "temperature": 0.3
    }
}
```

#### Human-in-the-Loop

- **PD 오버라이드**: AI 결정을 언제든 수동으로 변경 가능
- **승인 요청**: 중요 결정은 Slack으로 승인 요청
- **피드백 수집**: AI 결정에 대한 피드백 수집 및 학습

---

## 4. AI Agent Architecture

![Workflow Architecture](../../docs/images/workflow-architecture.png)

### 4.1 Agent 계층 구조

```
Level 0: WorkflowOrchestratorAgent (전체 조율)
         │
Level 1: ┌──────────┬──────────┬──────────┬──────────┬──────────┐
         │DataSync  │FileTrans │Monitor   │Graphics  │AI Agent  │
         │Agent     │Agent     │Agent     │AutoAgent │          │
         └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘
Level 2:     │rfid_parse │upload    │health    │trigger   │story
             │sheets_sync│download  │alert     │render    │priority
             │           │verify    │dashboard │          │anomaly
```

### 4.2 Agent 인터페이스

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class AgentConfig:
    agent_id: str
    level: str  # orchestrator, domain, block
    enabled: bool
    retry_policy: dict
    ai_enabled: bool
    human_approval_required: bool

class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, event_bus, db_session):
        self.config = config
        self.event_bus = event_bus
        self.db = db_session
        self.status = AgentStatus.IDLE

    @abstractmethod
    async def initialize(self) -> None:
        """에이전트 초기화"""
        pass

    @abstractmethod
    async def process(self, event) -> dict:
        """이벤트 처리"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """상태 체크"""
        pass
```

### 4.3 Event Bus System

```python
class WorkflowEventType(Enum):
    # Data Sync
    RFID_DATA_RECEIVED = "workflow.data_sync.rfid.received"
    SHEETS_SYNC_COMPLETED = "workflow.data_sync.sheets.completed"

    # File Transfer
    FILE_UPLOAD_COMPLETED = "workflow.file.upload.completed"
    FILE_DOWNLOAD_COMPLETED = "workflow.file.download.completed"

    # Monitoring
    ANOMALY_DETECTED = "workflow.monitor.anomaly.detected"
    ALERT_SENT = "workflow.monitor.alert.sent"

    # Graphics
    GRAPHICS_TRIGGER_REQUESTED = "workflow.graphics.trigger.requested"
    GRAPHICS_EXECUTED = "workflow.graphics.executed"

    # AI
    AI_DECISION_COMPLETED = "workflow.ai.decision.completed"
    HUMAN_APPROVAL_REQUESTED = "workflow.ai.approval.requested"
```

### 4.4 Human-in-the-Loop

- AI 결정에 대한 PD 승인 요청 워크플로우
- Slack 알림 및 대시보드 연동
- 승인/거부 기록 및 학습 데이터 수집

---

## 5. Technical Requirements

### 5.1 System Architecture

![Data Flow](../../docs/images/data-flow.png)

### 5.2 Technology Stack

| Layer | Technology | Reason |
|-------|------------|--------|
| **Backend** | FastAPI | 비동기 처리, WebSocket, PRD-0001과 동일 |
| **Agent Framework** | Python asyncio | 비동기 에이전트 처리 |
| **Message Queue** | Redis | Event Bus, 캐싱 |
| **Database** | PostgreSQL | PRD-0001과 공유 |
| **Task Queue** | Celery | 렌더링 워커 (automation_ae 재사용) |
| **AI/ML** | OpenAI API | GPT-4o, GPT-4o-mini |
| **File Storage** | GCS/S3/R2 | Cloud Storage |
| **Monitoring** | Prometheus + Grafana | 메트릭 수집 및 시각화 |
| **Alerting** | Slack API | 알림 발송 |

### 5.3 Data Schema

PRD-0001 Section 6과 공유하며, 다음 테이블 추가:

```python
# Workflow Event Log
class WorkflowEvent(Base):
    id: UUID
    event_type: str
    payload: JSON
    source_agent: str
    correlation_id: UUID
    timestamp: datetime
    status: str  # pending, processed, failed

# Agent Configuration
class AgentConfig(Base):
    agent_id: str
    level: str
    enabled: bool
    config: JSON
    last_health_check: datetime

# Alert History
class AlertHistory(Base):
    id: UUID
    alert_type: str
    severity: str
    message: str
    channels: list[str]
    sent_at: datetime
    acknowledged_at: datetime | None
    acknowledged_by: str | None
```

---

## 6. Integration with PRD-0001

![Integration Map](../../docs/images/integration.png)

### 6.1 공유 인프라

| 인프라 | PRD-0001 담당 | PRD-0002 담당 |
|--------|--------------|--------------|
| PostgreSQL | 스키마 정의, 그래픽 데이터 | 워크플로우 상태, 이벤트 로그 |
| Google Sheets | 읽기 (그래픽 렌더링) | 양방향 동기화 (쓰기 포함) |
| WebSocket | 그래픽 UI 업데이트 | 모니터링 대시보드 |
| Redis | 세션/캐시 | Event Bus |

### 6.2 데이터 흐름

```
RFID System
    │
    ▼
PRD-0002: RFID Parser Agent
    │
    ├──────────▶ PostgreSQL ◀──────────┐
    │                │                  │
    ▼                ▼                  │
PRD-0002: Sheets Sync Agent      PRD-0001: Backend
    │                │                  │
    ▼                ▼                  │
Google Sheets        WebSocket ─────────┤
    │                                   │
    └───────────────────────────────────┘
                    │
                    ▼
            PRD-0001: Frontend (Graphics UI)
```

### 6.3 의존성 그래프

| PRD-0002 Agent | 의존하는 PRD-0001 컴포넌트 | 제공하는 데이터/기능 |
|----------------|--------------------------|-------------------|
| Data Sync Agent | PostgreSQL 스키마 | 실시간 플레이어/핸드 데이터 |
| Graphics Trigger Agent | GraphicsAPI | 그래픽 호출 명령 |
| Monitoring Agent | Backend Health API | 시스템 상태 데이터 |
| AI Story Agent | 플레이어 히스토리 | 하이라이트 제안 |

---

## 7. Implementation Phases

### Phase 0: Infrastructure (1주)

| 작업 | 설명 | 산출물 |
|------|------|--------|
| Event Bus 구현 | Redis 기반 비동기 이벤트 버스 | `event_bus.py` |
| Base Agent 정의 | 에이전트 기본 인터페이스 | `base_agent.py` |
| 설정 관리 | YAML 기반 설정 | `config.yaml` |
| 로깅/모니터링 | 구조화된 로깅 | `logger.py` |

### Phase 1: Data Synchronization (2주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| RFID Parser Agent | RFID 데이터 파싱 | P0 |
| Sheets Sync Agent | Google Sheets 양방향 동기화 | P0 |
| Conflict Resolution | 동시 수정 충돌 해결 | P1 |

### Phase 2: File Transfer (2주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| Upload Agent | 현장 → Cloud 업로드 | P0 |
| Download Agent | Cloud → 한국 다운로드 | P0 |
| Integrity Verification | 체크섬 검증 | P0 |

### Phase 3: Monitoring (2주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| Health Check Agent | 시스템 상태 모니터링 | P0 |
| Alert Agent | Slack/Discord 알림 | P0 |
| Dashboard Agent | PA 모니터링 대시보드 | P1 |

### Phase 4: Graphics Automation (2주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| Trigger Agent | 이벤트-그래픽 매핑 | P0 |
| automation_ae 통합 | Nexrender 연동 | P0 |
| Web Graphics Renderer | Playwright HTML→PNG | P1 |

### Phase 5: AI Agent (3주)

| 작업 | 설명 | 우선순위 |
|------|------|----------|
| OpenAI 통합 | GPT API 연동 | P0 |
| Story Detection Agent | 스토리라인 추출 | P1 |
| Priority Decision Agent | 그래픽 우선순위 | P1 |
| Anomaly Resolution Agent | 데이터 자동 보정 | P1 |
| Human-in-the-Loop | 휴먼 승인 워크플로우 | P1 |

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| 데이터 동기화 지연 | < 2초 | DB → Sheets 반영 시간 |
| 파일 전송 성공률 | > 99% | 전송 완료 / 시도 |
| 알림 응답 시간 | < 30초 | 이상 감지 → 알림 발송 |
| 그래픽 자동화율 | > 60% | 자동 트리거 / 전체 그래픽 |
| AI 제안 채택률 | > 70% | 승인 / 제안 |
| PA 모니터링 시간 감소 | 50%↓ | 수동 모니터링 시간 |

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| RFID 연결 끊김 | High | 자동 재연결, 로컬 버퍼링 |
| Cloud Storage 지연 | Medium | 청크 업로드, 대역폭 관리 |
| AI 잘못된 판단 | Medium | Human-in-the-Loop, 자율성 제한 |
| 동시 수정 충돌 | Medium | 충돌 해결 로직, 알림 |
| 시스템 과부하 | Low | 큐 기반 처리, 우선순위 관리 |

---

## 10. Open Questions

1. **RFID 시스템**: 구체적인 데이터 포맷 및 통신 프로토콜?
2. **Cloud Storage**: GCS vs S3 vs Cloudflare R2 선택?
3. **AI 비용**: GPT-4o 호출 빈도 및 예상 비용?
4. **Slack 워크스페이스**: 알림 채널 구조?
5. **automation_ae 통합**: 별도 서비스 vs 모노레포 통합?

---

## Appendix

### A. automation_ae 참조 파일

| 파일 | 경로 | 재사용 방식 |
|------|------|------------|
| output_manager.py | `automation_ae/backend/app/services/output_manager.py` | NAS 출력 로직 |
| csv_parser.py | `automation_ae/backend/app/services/csv_parser.py` | 배치 작업 로직 |
| render_worker.py | `automation_ae/backend/app/workers/render_worker.py` | Celery 워커 패턴 |
| job.py | `automation_ae/backend/app/models/job.py` | JobStatus enum |

### B. Event Catalog

| Event Type | Payload | Source Agent |
|------------|---------|--------------|
| `data_sync.rfid.received` | `{table_id, cards, timestamp}` | RFID Parser |
| `data_sync.sheets.synced` | `{sheet_id, rows_updated}` | Sheets Sync |
| `file.upload.completed` | `{file_path, checksum, size}` | Upload Agent |
| `monitor.anomaly.detected` | `{type, details, severity}` | Health Check |
| `graphics.executed` | `{graphic_type, player_id}` | Graphics Trigger |
| `ai.decision.completed` | `{decision, confidence, reason}` | AI Agent |

### C. Diagram References

| Diagram | Location |
|---------|----------|
| Workflow Architecture | `docs/images/workflow-architecture.png` |
| 5 Automation Domains | `docs/images/automation-domains.png` |
| AI Agent Hierarchy | `docs/images/ai-agent-hierarchy.png` |
| Data Flow | `docs/images/data-flow.png` |
| PRD Integration | `docs/images/integration.png` |
| Graphics Automation | `docs/images/graphics-automation.png` |

### D. Related Documents

- [PRD-0001: WSOP Broadcast Graphics](./0001-prd-wsop-broadcast-graphics.md)
- [automation_ae PRD](D:\AI\claude01\automation_ae\tasks\prds\0001-prd-ae-automation.md)
- [HTML Mockup Guide](../../docs/HTML_MOCKUP_GUIDE.md)

---

**Next Steps**:
1. Open Questions 해결
2. Phase 0: Infrastructure 구현 시작
3. `/issue create` 로 GitHub 이슈 생성
4. Checklist 업데이트: `docs/unified/checklists/SUB/SUB-0002.md`

