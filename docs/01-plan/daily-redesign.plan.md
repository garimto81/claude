# Plan: /auto --daily v3.0 전면 재설계

> "수집+표시" 패러다임에서 "학습+액션 추천" 패러다임으로 전환

**Version**: 2.3.0
**Created**: 2026-02-12
**Status**: Approved (Ralplan 4/5 - Critic OKAY)
**PRD**: N/A (내부 워크플로우 재설계)
**Supersedes**:
- `daily-integration.plan.md` (v1.0.0, 2026-02-05) - Secretary+Slack List 통합 접근법 교체
- `skill-unification.plan.md` Task 2 - daily-sync 분리 대신 daily v3.0에 흡수
- `.omc/plans/daily-action-engine.md` (v2.0.0) - 이전 세션 draft. 본 문서가 **유일한 정식 Plan**. daily-action-engine.md는 초기 탐색용 draft였으며, 본 Plan의 9-Phase Pipeline이 해당 7-Phase를 포함 확장함. **해당 draft에서 제안된 `lib/action_engine/` 코드는 구현되지 않았으므로 cleanup 불필요**
**복잡도**: 5/5 (Ralplan 실행)

---

## 1. 배경 및 문제 정의

### 1.1 현재 아키텍처 (AS-IS)

```
/auto --daily
    │
    ├─ 범용 daily: Skill("gmail") → Skill("secretary") → ChecklistParser → ASCII 대시보드
    │                                    ↑ 불완전
    └─ WSOPTV daily-sync: 5-Phase (수집→분석→보고서→Housekeeping→Slack Lists)
                                    ↑ 하드코딩
```

### 1.2 핵심 결함 5개

| # | 결함 | 영향 | 심각도 |
|:-:|------|------|:------:|
| 1 | **Secretary 의존** | 불완전한 모듈에 의존, 실패 시 전체 중단 | CRITICAL |
| 2 | **Slack 데이터 누락** | Gmail+GitHub만 수집, Slack 채널 메시지 분석 없음 | CRITICAL |
| 3 | **전체 재수집** | 매 실행마다 전체 데이터 재수집 → 토큰 낭비 | HIGH |
| 4 | **첨부파일 무시** | PDF/Excel 첨부파일을 읽지 않고 메타데이터만 표시 | HIGH |
| 5 | **프로젝트 전문성 부재** | 프로젝트 도메인 지식 없이 범용 분석만 수행 | CRITICAL |

### 1.3 근본 원인: Cold Start 문제

`.project-sync.yaml`이 READ-ONLY로 설계되어 있어:
- 34개 서브 레포 중 1개만 설정 보유 (wsoptv_ott)
- 나머지 33개에서 `/auto --daily` 실행 시 아무 데이터도 수집 불가
- 설정 파일을 자동 생성/갱신하는 메커니즘 부재

---

## 2. 목표

### 2.1 핵심 목표

| # | 목표 | 측정 기준 |
|:-:|------|----------|
| 1 | 3소스 통합 분석 | Gmail + Slack + GitHub 모두 수집/분석 |
| 2 | 증분 수집 | 이전 실행 이후 새 데이터만 수집 (토큰 절감) |
| 3 | 액션 추천 엔진 | "보낼 메시지"/"회신 초안"을 AI가 생성 |
| 4 | 첨부파일 AI 분석 | PDF/Excel을 직접 읽고 내용 분석 |
| 5 | 프로젝트 전문가 모드 | CLAUDE.md + 이전 분석 학습하여 도메인 전문가로 동작 |
| 6 | Cold Start 해결 | `.project-sync.yaml` 자동 생성/갱신 |
| 7 | daily-sync 기능 100% 보존 | Housekeeping, Slack Lists, 업체 상태 머신 흡수 |

### 2.2 비목표 (명시적 제외)

| 항목 | 이유 |
|------|------|
| 이메일/Slack 메시지 리뷰 기능 | 사용자가 직접 확인 |
| Calendar 연동 | Secretary 제거에 따른 의도적 제외. 향후 `lib/calendar` 신규 모듈로 재도입 가능 |
| 실시간 알림 | 일일 배치 워크플로우 |

---

## 3. 구현 범위

### 3.1 TO-BE 아키텍처 (9-Phase Pipeline)

```
/auto --daily
    │
    ▼
Phase 0: Config Bootstrap (자동 생성/갱신)
    │  .project-sync.yaml 없으면 → CLAUDE.md/README.md + API 탐색으로 자동 생성
    │  CLAUDE.md 없으면 → 디렉토리명 + git remote 기반 최소 설정
    │  있으면 → 유효성 검증 + 자동 갱신 (auto_generated: true만)
    ▼
Phase 1: Expert Context Loading (프로젝트 전문가 학습)
    │  CLAUDE.md → Identity Context (500t)
    │  .project-sync.yaml + snapshots/latest.json → Operational Context (2000t)
    │  docs/ 핵심 문서 → Deep Context (3000t)
    │  → expert_context.json (5500t) 생성
    ▼
Phase 2: Incremental Data Collection (증분 수집)
    │  Gmail: History API (historyId 기반 delta)
    │  Slack: oldest 파라미터 (timestamp 기반 delta)
    │  GitHub: gh --since (ISO timestamp 기반 delta)
    │  초회 실행: get_profile() → historyId 시딩, 7일 lookback
    │  인증 실패: 해당 소스 skip + 경고 (partial report)
    ▼
Phase 3: Attachment Analysis (첨부파일 분석)
    │  다운로드: GmailClient.download_attachment() (신규 메서드)
    │  Claude Read (20페이지 이하 PDF/이미지)
    │  lib/pdf_utils (20페이지 초과 PDF → 청크 분할)
    │  SHA256 캐시로 중복 분석 방지
    ▼
Phase 4: AI Cross-Source Analysis (크로스 소스 분석)
    │  소스별 독립 분석 → 크로스 소스 연결 분석
    │  → expert_context 기반 도메인 특화 분석
    ▼
Phase 5: Action Recommendation Engine (액션 추천)
    │  Slack 메시지 초안 + 이메일 회신 초안 + GitHub 액션 제안
    │  톤 캘리브레이션: expert_context.communication_style 참조
    │  액션 최대 10건, 우선순위(URGENT/HIGH/MEDIUM) 정렬
    ▼
Phase 6: Project-Specific Operations (프로젝트 특화 작업)
    │  vendor_management: Slack Lists 갱신 (ListsSyncManager)
    │  vendor_management: 업체 상태 자동 전이 (wsoptv_sync_config.yaml)
    │  vendor_management: 견적 비교표 갱신
    │  development: CI/CD 상태 갱신
    │  → .project-sync.yaml의 config_file 참조
    ▼
Phase 7: Gmail Housekeeping (이메일 정리)
    │  라벨 자동 적용 (vendor 도메인 매칭)
    │  INBOX 정리 (config: "auto" | "confirm" | "skip")
    │  결과 보고 (N개 라벨링, M개 정리)
    ▼
Phase 8: State Update & Knowledge Layer (상태 갱신 + 학습)
    │  8A: .omc/daily-state/<project>/state.json 갱신 (커서, 캐시)
    │  8B: Knowledge Update (entities.json, relationships.json, patterns.json, events/)
    │  8C: Snapshot & Eviction (snapshots/latest.json 생성, 퇴거 실행)
    ▼
Output: 구조화된 대시보드 + 액션 아이템
```

### 3.2 Config Auto-Bootstrap 설계

#### 3.2.1 `.project-sync.yaml` v2.0 스키마

```yaml
version: "2.0"
project_name: "프로젝트명"       # CLAUDE.md 또는 디렉토리명에서 추출
project_type: "vendor_management" # 자동 분류 (5가지)

meta:
  auto_generated: true            # 자동 생성 여부 (true면 갱신 허용)
  generated_at: "2026-02-12T09:00:00Z"
  last_calibrated: null           # 사용자 확인 시 timestamp
  confidence: 0.75                # 자동 생성 신뢰도
  pending_additions: []           # 자동 감지 후 확인 대기 항목

daily:
  skill: "daily"                  # 기본값 (전용 스킬 없으면)
  sources:
    gmail:
      enabled: true
      auto_generated: true
      label: "wsoptv"
      label_id: "Label_xxx"
      vendor_domains: ["vimeo.com", "brightcove.com"]
    slack:
      enabled: true
      auto_generated: true
      channel_id: "C09TX3M1J2W"
      channel_name: "#wsoptv"
    github:
      enabled: true
      auto_generated: true
      repo: "garimto81/claude"
      track_branches: ["main", "feat/*"]
      track_issues: true
      track_prs: true

  # 프로젝트 특화 설정 (있으면)
  config_file: "wsoptv_sync_config.yaml"  # vendor_management 전용 설정

  output:
    report_dir: "docs/management"
    slack_channel: null

  housekeeping:
    gmail_label_auto: true
    inbox_cleanup: "confirm"        # "auto" | "confirm" | "skip"

  communication_style:              # 액션 추천 톤 캘리브레이션
    email_tone: "professional"      # professional | casual | formal
    slack_tone: "casual"
    language: "ko"                  # ko | en | mixed
```

#### 3.2.2 v1.0 → v2.0 마이그레이션 전략

| 기존 파일 | 마이그레이션 동작 |
|-----------|------------------|
| v1.0 (wsoptv_ott) | `version: "1.0"` 감지 → `auto_generated: false` 설정 → 읽기만, 갱신 안 함 |
| v2.0 (auto_generated: true) | 자동 갱신 허용 |
| v2.0 (auto_generated: false) | 수동 편집된 파일 → 읽기만, 갱신 안 함 |
| 없음 | 자동 생성 (auto_generated: true) |

**v1.0 필드 호환성:**
- v1.0의 `sources`, `config_file`, `output`, `housekeeping` → v2.0에서 동일 경로
- v2.0 추가 필드: `meta.*`, `communication_style`, `project_type`, 소스별 `auto_generated`
- v1.0 파일은 읽기 시 누락 필드를 기본값으로 채움 (파일 수정 안 함)

#### 3.2.3 Bootstrap 알고리즘 (CLAUDE.md 부재 대응 포함)

```
Phase 0: Config Bootstrap
    │
    ├─ .project-sync.yaml 존재?
    │   ├─ YES + version "1.0" → v1.0 호환 모드 (읽기만, auto_generated=false)
    │   ├─ YES + version "2.0" + auto_generated: true → 자동 갱신 허용
    │   ├─ YES + version "2.0" + auto_generated: false → 읽기만
    │   │
    │   └─ NO → 자동 생성 시작
    │       │
    │       ├─ Step 1: 프로젝트 식별
    │       │   ├─ CLAUDE.md 존재 → 파싱 (이름, 스택, 키워드, 타입)
    │       │   ├─ README.md만 존재 → 제한적 파싱 (이름, 설명)
    │       │   └─ 둘 다 없음 → 디렉토리명 사용, project_type="development" 기본
    │       │
    │       ├─ Step 2: Gmail 소스 탐색 (인증 확인 우선)
    │       │   ├─ python -m lib.gmail status --json
    │       │   │   ├─ authenticated: true → labels 조회 → fuzzy match
    │       │   │   └─ authenticated: false → gmail.enabled=false, 경고 출력
    │       │   └─ 매칭 실패 → gmail.enabled=false, pending_additions에 기록
    │       │
    │       ├─ Step 3: Slack 소스 탐색 (인증 확인 우선)
    │       │   ├─ python -m lib.slack status --json
    │       │   │   ├─ authenticated: true → channels 조회 → fuzzy match
    │       │   │   └─ authenticated: false → slack.enabled=false, 경고 출력
    │       │   └─ 매칭 실패 → slack.enabled=false, pending_additions에 기록
    │       │
    │       ├─ Step 4: GitHub 소스 탐색
    │       │   └─ git remote -v → repo URL 추출 (항상 가능)
    │       │
    │       └─ Step 5: YAML 생성
    │           → .project-sync.yaml 생성 (auto_generated: true)
    │           → confidence 계산: (매칭 소스 수 / 3) 반올림
    │           → 소스 0개 매칭 → confidence: 0.0, GitHub만 활성
```

#### 3.2.4 프로젝트 타입 분류

| 타입 | 감지 키워드/파일 | 분석 초점 |
|------|----------------|----------|
| `vendor_management` | 업체, vendor, RFP, 견적, quote | 업체별 상태, 견적 비교, follow-up |
| `development` | src/, package.json, setup.py, Cargo.toml | 브랜치 상태, PR 리뷰, CI/CD |
| `infrastructure` | Dockerfile, terraform, k8s, helm | 배포 상태, 장애 알림, 리소스 |
| `research` | docs/ 비중 높음, 분석, analysis | 문서 업데이트, 리뷰 요청 |
| `content` | 영상, media, upload, vimeo | 콘텐츠 파이프라인, 업로드 상태 |

### 3.3 Incremental State 설계

#### 3.3.1 상태 파일 스키마

파일 위치: `.omc/daily-state/<project-name>/state.json`

```json
{
  "version": "2.0",
  "project": "wsoptv_ott",
  "last_run": "2026-02-12T09:00:00Z",
  "run_count": 5,
  "cursors": {
    "gmail": {
      "history_id": "12345678",
      "last_message_id": "msg_abc123",
      "last_timestamp": "2026-02-11T18:00:00Z"
    },
    "slack": {
      "last_ts": "1707699600.000000",
      "last_timestamp": "2026-02-11T18:00:00Z"
    },
    "github": {
      "last_check": "2026-02-11T18:00:00Z",
      "last_commit_sha": "abc1234"
    }
  },
  "cache": {
    "attachments": {}
  },
  "knowledge_version": "1.0",
  "knowledge_path": "knowledge/"
}
```

> **Knowledge Layer**: `learned_context`는 `knowledge/` 디렉토리 구조로 대체됨. 상세 스키마는 `docs/01-plan/knowledge-layer.plan.md` Section 3-7 참조.

#### 3.3.2 초회 실행 (First-Run) 초기화

상태 파일이 없는 최초 실행 시:

| 소스 | 초기화 방법 | 기본 lookback |
|------|-----------|:------------:|
| Gmail | `get_profile()` → `historyId` 시딩 + `list_emails(query="newer_than:7d")` | 7일 |
| Slack | `oldest = now() - 7days` (Unix timestamp) | 7일 |
| GitHub | `gh issue list --since 7d`, `gh pr list` | 7일 |

```
초회 실행 흐름:
    │
    ├─ daily-state/<project>/state.json 존재?
    │   ├─ YES → cursors 사용하여 증분 수집
    │   └─ NO → 초회 초기화
    │       ├─ Gmail: get_profile() → historyId 저장
    │       │   └─ list_emails(query="newer_than:7d") → 최근 7일 수집
    │       ├─ Slack: oldest = str(time.time() - 604800)
    │       │   └─ get_history(oldest=oldest) → 최근 7일 수집
    │       └─ GitHub: gh issue list --since "7 days ago"
    │           └─ 상태 파일 생성 (run_count: 1)
```

#### 3.3.3 증분 수집 방법

| 소스 | Primary 방법 | Fallback (historyId 만료 등) | 기존 코드 |
|------|-------------|---------------------------|----------|
| Gmail | `list_history(history_id)` | `list_emails(query="after:YYYY/MM/DD")` | `client.py:72-106` |
| Slack | `get_history(oldest=ts)` | `get_history(oldest=yesterday_ts)` | `client.py:229` |
| GitHub | `gh issue list --since`, `gh pr list` | 전체 조회 + 날짜 필터 | gh CLI |

#### 3.3.4 Two-Phase Commit

```
Phase A: 소스 커서 기록 (수집 완료 직후)
    → cursors.gmail.history_id = new_id (get_profile()로 최신값)
    → cursors.slack.last_ts = 수집된 마지막 메시지 ts
    → cursors.github.last_check = now()

Phase B: 분석 캐시 기록 (분석 완료 후)
    → cache.attachments += new_analyses
    # Knowledge Layer Phase 8B/8C (docs/01-plan/knowledge-layer.plan.md 참조):
    # 8B: Entity 추출 → entities.json, relationships.json, patterns.json, events/ 갱신
    # 8C: Snapshot 생성 (latest.json) + Eviction + Notepad Wisdom 연동
```

실패 시 Phase A만 롤백 → 다음 실행에서 같은 데이터 재수집 (안전)

### 3.4 Expert Context Loading 설계

#### 3.4.1 3-Tier Context Assembly

```
Tier 1: Identity Context (500 tokens)
    ├─ CLAUDE.md / README.md에서 추출
    │   → 프로젝트명, 목표, 기술 스택
    │   → 핵심 용어 (WSOP, OTT, Vimeo 등)
    └─ .project-sync.yaml에서 추출
        → 데이터 소스 목록, 프로젝트 타입, communication_style

Tier 2: Operational Context (2000 tokens)
    ├─ Read: .omc/daily-state/<project>/knowledge/snapshots/latest.json
    │   → key_entities, active_patterns, recent_events_digest
    └─ 최근 보고서 요약 (있으면)
        → docs/management/ 최신 파일 300t 요약

Tier 3: Deep Context (3000 tokens)
    ├─ docs/ 핵심 문서 스캔
    │   → README, PRD, 아키텍처 문서 키포인트
    └─ .omc/daily-state/<project>/knowledge/snapshots/latest.json
        → 축적된 도메인 지식
```

총합: ~5500 tokens (200K 윈도우의 2.75%)

#### 3.4.2 Expert Context JSON 구조

```json
{
  "project_identity": "WSOP OTT 스트리밍 플랫폼 - Q3 2026 론칭 목표",
  "project_type": "vendor_management",
  "key_entities": {
    "vendors": ["Brightcove", "Vimeo", "Megazone", "JRMAX"],
    "stakeholders": ["김대표", "이팀장"],
    "products": ["WSOPTV", "VHX"]
  },
  "analysis_perspective": "업체 견적 비교, 계약 협상 진행률, 기술 검증 상태에 집중",
  "domain_vocabulary": ["RFP", "SI", "CDN", "DRM", "HLS"],
  "current_phase": "Phase 1 MVP (Vimeo 기반)",
  "recent_decisions": ["Vimeo OTT 선정", "SI 업체 평가 진행 중"],
  "communication_style": {
    "email_tone": "professional",
    "slack_tone": "casual",
    "language": "ko"
  }
}
```

### 3.5 Attachment Analysis 설계

#### 3.5.1 첨부파일 다운로드 경로

| 방법 | 구현 | 사용 조건 |
|------|------|----------|
| `GmailClient.download_attachment(message_id, attachment_id)` | **신규 메서드 추가** (`lib/gmail/client.py`) | 범용 (모든 프로젝트) |
| `messages().attachments().get()` | Gmail API 직접 호출 | download_attachment 내부 |
| 임시 저장 | `.omc/daily-state/attachments/<sha256>.ext` | 분석 후 자동 삭제 |

**구현 상세**: `GmailClient`에 다음 메서드 추가

```python
def download_attachment(self, message_id: str, attachment_id: str) -> bytes:
    """Gmail 첨부파일 바이너리 다운로드"""
    result = self.service.users().messages().attachments().get(
        userId='me', messageId=message_id, id=attachment_id
    ).execute()
    return base64.urlsafe_b64decode(result['data'])
```

**기존 AttachmentDownloader와의 관계**:

| 항목 | `GmailClient.download_attachment()` (신규) | `AttachmentDownloader` (기존) |
|------|------------------------------------------|-----------------------------|
| 위치 | `lib/gmail/client.py` | `wsoptv_ott/scripts/sync/collectors/attachment_downloader.py` |
| 범위 | 범용 (모든 프로젝트) | WSOPTV 전용 |
| 반환 | `bytes` (raw binary) | `Path` (파일 저장 후 경로) |
| 캐시 | 없음 (caller가 관리) | MD5 기반 파일 캐시 |
| 의존 | 없음 | `models_v2.Attachment` (Pydantic) |

**방침**: `GmailClient.download_attachment()`는 low-level 메서드로 추가. 기존 `AttachmentDownloader`는 Phase 6 (vendor_management)에서 그대로 사용. `AttachmentDownloader.download()` 내부의 직접 API 호출(lines 97-102)을 `self.gmail_client.download_attachment()` 호출로 교체하는 리팩토링은 선택 사항(향후).

Phase 3 캐시는 SHA256 사용 (content-addressable). 기존 `AttachmentDownloader`의 MD5 캐시는 email_id+attachment_id 기반으로 목적이 다르므로 공존.

#### 3.5.2 분석 전략

```
첨부파일 감지 (Phase 2에서 메타데이터 수집)
    │
    ├─ 이미 분석됨? (SHA256 캐시 확인)
    │   └─ YES → 캐시 결과 재사용
    │
    ├─ 파일 타입 판단
    │   ├─ PDF ≤ 20페이지 → Claude Read 직접 분석
    │   ├─ PDF > 20페이지 → lib/pdf_utils 청크 분할 후 분석
    │   ├─ Excel/CSV → 구조 요약 (행/열 수, 헤더, 샘플 5행)
    │   ├─ 이미지 (PNG/JPG) → Claude Vision 분석
    │   └─ 기타 → 메타데이터만 기록 (파일명, 크기, MIME)
    │
    └─ 분석 관점 (expert_context.analysis_perspective)
        → vendor_management: "견적서인가? 금액, 유효기간, 조건은?"
        → development: "API 스펙인가? 변경점, breaking change는?"
```

#### 3.5.3 캐시 구조

```json
{
  "sha256_of_file": {
    "filename": "brightcove_quote_2026.pdf",
    "analyzed_at": "2026-02-11T09:00:00Z",
    "source": "gmail",
    "file_type": "pdf",
    "pages": 5,
    "summary": "Brightcove Enterprise 연간 계약 견적: $120K/yr, CDN 포함",
    "key_data": {
      "amount": "$120,000/year",
      "vendor": "Brightcove",
      "valid_until": "2026-03-15"
    }
  }
}
```

### 3.6 Action Recommendation Engine 설계

#### 3.6.1 액션 유형

| 유형 | 트리거 조건 | 생성 결과 |
|------|-----------|----------|
| **Slack 메시지 추천** | 미응답 질문, follow-up 필요 | 메시지 초안 + 대상 채널 |
| **이메일 회신 추천** | 미응답 48h+, 견적 수신, 요청사항 | 회신 초안 + 긴급도 |
| **GitHub 액션** | PR 리뷰 대기 3일+, 이슈 미응답 | 리뷰 코멘트 초안 |
| **개발 상태 알림** | CI 실패, 브랜치 충돌 | 수정 제안 |

#### 3.6.2 톤 캘리브레이션

```
expert_context.communication_style 적용:
    │
    ├─ email_tone: "professional" → 격식체, 영문 비즈니스 형식
    ├─ email_tone: "casual" → 반말체, 간결한 형식
    ├─ email_tone: "formal" → 존칭, 공식 문서 형식
    │
    ├─ slack_tone: "casual" → 반말, 이모지 허용
    ├─ slack_tone: "professional" → 존칭, 이모지 최소화
    │
    └─ language: "ko" | "en" | "mixed"
```

**피드백 루프**: `learned_context.action_feedback`에 사용자 교정 기록

```json
{
  "action_feedback": [
    {
      "type": "email_tone_correction",
      "original": "Dear Kim, Thank you...",
      "correction": "김 담당님, 검토 감사합니다...",
      "pattern": "한국 업체에는 한글 존칭 사용"
    }
  ]
}
```

#### 3.6.3 액션 제한 및 우선순위

| 규칙 | 값 |
|------|-----|
| 최대 액션 수 | 10건 |
| 우선순위 정렬 | URGENT → HIGH → MEDIUM |
| URGENT 기준 | 미응답 48h+, CI 실패, 마감일 D-1 |
| HIGH 기준 | 견적 수신, PR 리뷰 대기 3d+, 패턴 감지 |
| MEDIUM 기준 | 정보 공유, 일반 follow-up |
| 액션 없음 시 | "현재 추가 액션이 필요하지 않습니다" 표시 |

### 3.7 Project-Specific Operations 설계 (Phase 6)

daily-sync v1.4.0의 기능을 프로젝트 타입별로 조건 실행합니다.

#### 3.7.1 vendor_management 타입

| 기능 | daily-sync 원본 | v3.0 대응 | 조건 |
|------|----------------|----------|------|
| Slack Lists 갱신 | Phase 5: `ListsSyncManager.update_item()` | Phase 6에서 동일 실행 | `slack_lists.enabled: true` |
| 업체 상태 자동 전이 | `analyzers/status_inferencer.py` | Phase 6에서 실행 | `config_file` 존재 |
| 견적 비교표 | `formatters/quote_formatter.py` | Phase 6에서 실행 | 견적 첨부파일 감지 시 |
| 요약 메시지 포스팅 | `generate_summary_message()` + `post_summary()` | Phase 6 출력으로 포스팅 | `output.slack_channel` 설정 |

#### 3.7.2 development 타입

| 기능 | v3.0 대응 |
|------|----------|
| CI/CD 상태 요약 | `gh run list` → 최근 실행 결과 |
| 브랜치 상태 | `gh pr list` + `git branch -r` |
| 마일스톤 진행률 | `gh api repos/{}/milestones` |

#### 3.7.3 프로젝트 특화 설정 참조

```
.project-sync.yaml
    └─ daily.config_file: "wsoptv_sync_config.yaml"
        → 업체 도메인 매핑, 상태 전이 규칙, Slack Lists 컬럼 ID
        → Phase 6에서 이 파일을 읽어 프로젝트 특화 로직 실행
```

#### 3.7.4 프로젝트 특화 모듈 호출 패턴

Phase 6에서 wsoptv_ott 등 서브 프로젝트의 모듈을 호출할 때, 기존 daily-sync SKILL.md v1.4.0의 패턴을 따릅니다:

```
# SKILL.md 내에서 Claude가 Python CLI 호출하는 패턴
Bash: cd C:\claude\wsoptv_ott && python -c "
import sys; sys.path.insert(0, 'scripts/sync')
from analyzers.status_inferencer import StatusInferencer
# ...
"

# 또는 Bash: python C:\claude\wsoptv_ott\scripts\sync\lists_sync_v2.py status
```

**호출 원칙**: `sys.path` 조작이 아닌 절대 경로 + `cd` 패턴 사용. `daily/SKILL.md`에서 `.project-sync.yaml`의 프로젝트 경로(CWD)를 기준으로 상대 모듈을 해석.

### 3.8 Gmail Housekeeping 설계 (Phase 7)

daily-sync v1.4.0 Phase 4를 그대로 흡수합니다.

| 기능 | 동작 | 설정 |
|------|------|------|
| 라벨 자동 적용 | vendor_domains 매칭 이메일에 프로젝트 라벨 적용 | `housekeeping.gmail_label_auto: true` |
| INBOX 정리 | 처리 완료 메일 archive | `housekeeping.inbox_cleanup: "confirm"` |
| 결과 보고 | "N개 라벨링, M개 정리" 로그 | 항상 |

**inbox_cleanup 모드:**
- `"auto"`: 자동 archive (위험)
- `"confirm"`: 대상 목록 표시 후 사용자 확인
- `"skip"`: 건너뜀 (기본값)

### 3.9 인증 실패 시 Graceful Degradation

| 소스 | 인증 미설정 | 인증 만료 | 동작 |
|------|-----------|----------|------|
| Gmail | skip + 경고 | 자동 refresh 시도 → 실패 시 skip + 재인증 안내 | Partial report |
| Slack | skip + 경고 | 재인증 안내 출력 | Partial report |
| GitHub | skip + 경고 | N/A (gh CLI 토큰 관리) | Partial report |
| **전체 실패** | - | - | 에러 메시지 + 인증 설정 안내 후 중단 |

```
인증 체크 흐름:
    │
    ├─ Gmail: python -m lib.gmail status --json
    │   └─ authenticated: false → sources.gmail.enabled = false (이번 실행만)
    │
    ├─ Slack: python -m lib.slack status --json
    │   └─ authenticated: false → sources.slack.enabled = false (이번 실행만)
    │
    ├─ GitHub: gh auth status
    │   └─ not logged in → sources.github.enabled = false (이번 실행만)
    │
    └─ 활성 소스 0개? → 에러 출력 후 중단
        "❌ 활성 데이터 소스가 없습니다. 다음 중 하나를 설정하세요:
         - Gmail: python -m lib.gmail login
         - Slack: python -m lib.slack login
         - GitHub: gh auth login"
```

---

## 4. daily-sync Feature Preservation Matrix

| daily-sync v1.4.0 기능 | v3.0 Phase | 보존 상태 | 비고 |
|------------------------|:---------:|:---------:|------|
| Gmail 3-step 검색 (label→domain→keyword) | Phase 2 | **대체** | 증분 수집으로 교체 (더 효율적) |
| Slack 채널 히스토리 수집 | Phase 2 | **보존** | oldest 파라미터 활용 |
| Slack Lists 조회/갱신 | Phase 6 | **보존** | vendor_management 타입에서 실행 |
| Gmail Housekeeping (라벨) | Phase 7 | **보존** | 독립 Phase로 분리 |
| Gmail INBOX 정리 | Phase 7 | **보존** | confirm 모드 기본 |
| AI 이메일 분석 | Phase 4 | **확장** | 크로스 소스 분석 추가 |
| AI 상태 추론 (status_inferencer) | Phase 6 | **보존** | config_file 참조 |
| 견적 추출 (quote_extractor) | Phase 3+6 | **보존** | 첨부파일 분석 + 견적 포맷팅 |
| 견적 포맷팅 (quote_formatter) | Phase 6 | **보존** | vendor_management에서 실행 |
| 첨부파일 다운로드 | Phase 3 | **범용화** | GmailClient 메서드로 이전 |
| 보고서 생성 | Output | **확장** | 액션 추천 추가 |
| `wsoptv_sync_config.yaml` 참조 | Phase 6 | **보존** | `daily.config_file` 필드로 참조 |
| 요약 메시지 Slack 포스팅 | Phase 6 | **보존** | output.slack_channel로 포스팅 |

---

## 5. 예상 영향 파일

### 5.1 신규 생성

| 파일 | 역할 |
|------|------|
| `.omc/daily-state/<project>/state.json` | 프로젝트별 증분 상태 |
| `.omc/daily-state/<project>/expert_context.json` | 프로젝트 전문가 컨텍스트 |

### 5.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `.claude/skills/auto/SKILL.md` | `--daily` 섹션 전면 재작성: (1) Secretary 의존 제거, (2) 모든 --daily 호출을 daily v3.0으로 라우팅, (3) Project Context Discovery 간소화 (daily v3.0 Phase 0가 내부 처리) |
| `.claude/skills/daily/SKILL.md` | **9-Phase Pipeline 실행 주체**. Secretary 의존 제거, 3소스 직접 수집, Config Bootstrap ~ State Update 전체 오케스트레이션 |
| `lib/gmail/client.py` | `download_attachment()` 메서드 추가 (~15줄) |

### 5.3 활용 (수정 없음)

| 파일 | 활용 방식 |
|------|----------|
| `lib/gmail/client.py` | `list_history()`, `get_profile()`, `list_labels()` |
| `lib/slack/client.py` | `get_history(oldest=...)`, `list_channels()` |
| `lib/pdf_utils/extractor.py` | PDF 청크 분할 |
| `wsoptv_ott/scripts/sync/analyzers/*` | 상태 추론, 견적 추출 (vendor_management Phase 6) |
| `wsoptv_ott/scripts/sync/formatters/*` | 견적 포맷팅 (vendor_management Phase 6) |
| `wsoptv_ott/wsoptv_sync_config.yaml` | 업체 매핑, 상태 전이 규칙 |

### 5.4 Deprecated 처리

| 파일 | 처리 |
|------|------|
| `.claude/skills/daily-sync/SKILL.md` | **Deprecated**. YAML frontmatter에 `deprecated: true`, `redirect: daily` 추가. 기존 `/daily-sync` 호출 시 `/daily`로 리다이렉트. daily-sync의 WSOPTV 특화 로직은 daily v3.0 Phase 6 (vendor_management 타입)에서 실행. **Note**: `wsoptv_ott/.project-sync.yaml` v1.0은 `daily.skill: "daily-sync"`를 유지하며, deprecated redirect를 통해 `/daily`로 자동 라우팅됨. 신규 v2.0 프로젝트는 처음부터 `daily.skill: "daily"`로 생성 |
| `.omc/plans/daily-action-engine.md` | 상단에 `⚠️ SUPERSEDED by docs/01-plan/daily-redesign.plan.md` 경고 추가 |

### 5.5 CLI 인증 체크 (기존 구현 확인 완료)

Phase 0/Phase 2에서 사용하는 인증 확인 커맨드는 이미 구현되어 있음:

| 커맨드 | 구현 위치 | 상태 |
|--------|----------|:----:|
| `python -m lib.gmail status --json` | `lib/gmail/cli.py:59` | ✅ 존재 |
| `python -m lib.slack status --json` | `lib/slack/cli.py:77` | ✅ 존재 |
| `gh auth status` | gh CLI 내장 | ✅ 존재 |

---

## 6. 위험 요소

| # | 위험 | 영향 | 완화 |
|:-:|------|------|------|
| 1 | Gmail History API historyId 만료 (1주+) | 증분 수집 불가 | Fallback: `list_emails(query="after:...")` |
| 2 | 자동 생성 config가 잘못된 소스 매칭 | 잘못된 데이터 수집 | confidence 점수 + pending_additions |
| 3 | 첨부파일 분석이 토큰 과다 소비 | Context 부족 | 20페이지 제한 + SHA256 캐시 |
| 4 | 액션 추천 톤이 사용자 스타일과 불일치 | 사용 의지 감소 | communication_style + action_feedback 루프 |
| 5 | daily-sync 흡수 시 기존 기능 회귀 | WSOPTV 워크플로우 중단 | Feature Preservation Matrix로 추적 |
| 6 | CLAUDE.md 없는 프로젝트에서 빈 설정 | 실질적 기능 제한 | GitHub만이라도 활성화 + 경고 |
| 7 | 다중 프로젝트 동시 실행 시 파일 충돌 | 상태 파일 corruption | 프로젝트별 독립 상태 파일 (충돌 불가) |

---

## 7. 기존 Plan과의 관계

| 기존 Plan | 관계 | 상세 |
|-----------|------|------|
| `daily-integration.plan.md` | **대체** | Secretary+Slack List 통합 접근법을 완전 재설계로 교체 |
| `skill-unification.plan.md` Task 2 (`docs/01-plan/skill-unification.plan.md`) | **대체** | daily-sync를 독립 스킬로 분리하는 대신, daily v3.0에 흡수. daily-sync SKILL.md는 deprecated 처리 |
| `omc-bkit-verification.plan.md` | 무관 | |

---

## 8. 구현 순서

| 순서 | 구현 항목 | 의존성 | 검증 기준 |
|:----:|----------|--------|----------|
| 1 | `GmailClient.download_attachment()` 추가 | 없음 | 메서드 호출로 바이너리 반환 |
| 2 | Config Bootstrap (Phase 0) | 없음 | CLAUDE.md 없는 프로젝트에서도 설정 생성 |
| 3 | First-Run 초기화 + Incremental State | Phase 0 | 초회: 7일 수집, 재실행: delta만 수집 |
| 4 | Expert Context Loading (Phase 1) | Phase 0 | expert_context.json 5500t 이내 생성 |
| 5 | 3소스 수집 + 인증 실패 대응 (Phase 2) | Phase 0, 3 | partial report 생성 가능 |
| 6 | Attachment Analysis (Phase 3) | Phase 2, 1 | SHA256 캐시 적중률 측정 |
| 7 | AI Cross-Source Analysis (Phase 4) | Phase 1, 2, 3 | 크로스 소스 인사이트 1건+ 생성 |
| 8 | Action Recommendation (Phase 5) | Phase 4 | 액션 10건 이하, 톤 캘리브레이션 적용 |
| 9 | Project-Specific Ops (Phase 6) | Phase 4, 5 | Slack Lists 갱신 정상 동작 |
| 10 | Gmail Housekeeping (Phase 7) | Phase 2 | 라벨 자동 적용 + inbox 정리 |
| 11 | State Update (Phase 8) | 전체 | 커서 저장 후 재실행 시 증분 동작 |
| 12 | SKILL.md 업데이트 + Supersession 적용 | 전체 | daily/auto SKILL.md 반영 + `.omc/plans/daily-action-engine.md` 상단에 SUPERSEDED 경고 추가 |

---

## 9. Ralplan 합의 추적

| 역할 | Iteration 1 | Iteration 2 | Iteration 3 | Iteration 4 | 비고 |
|------|:-----------:|:-----------:|:-----------:|:-----------:|------|
| Planner | READY | READY (v2.0) | READY (v2.1) | READY (v2.2.1) | 이 문서 |
| Architect | APPROVE (조건부 4건) | - | - | - | 조건 4건 모두 반영 완료 |
| Critic | REJECT (5건) | REJECT (4건 신규) | REJECT (5건 신규) | **OKAY** (3건 Advisory 반영) | 22건 누적 해결 + 3건 Advisory |

### Iteration 1 → 2 반영 내역

| # | Architect/Critic 지적 | 반영 위치 |
|:-:|----------------------|----------|
| 1 | Gmail Housekeeping 누락 | Section 3.8 (Phase 7 신설) |
| 2 | Slack Lists 갱신 누락 | Section 3.7.1 (Phase 6 신설) |
| 3 | 첨부파일 다운로드 메서드 미정 | Section 3.5.1 (download_attachment 상세) |
| 4 | v1.0→v2.0 마이그레이션 전략 | Section 3.2.2 |
| 5 | 초회 실행 historyId 시딩 | Section 3.3.2 (First-Run 초기화) |
| 6 | daily-sync Feature Preservation | Section 4 (전체 매트릭스) |
| 7 | 인증 실패 시 동작 | Section 3.9 (Graceful Degradation) |
| 8 | skill-unification.plan.md 충돌 | Section 7 (명시적 대체 선언) |
| 9 | CLAUDE.md 없는 프로젝트 | Section 3.2.3 Step 1 (README/디렉토리명 fallback) |
| 10 | Calendar 제거 명시 | Section 2.2 (의도적 제외 선언) |
| 11 | 톤 캘리브레이션 | Section 3.6.2 + communication_style |
| 12 | 액션 과다 추천 제한 | Section 3.6.3 (최대 10건, 우선순위) |
| 13 | 프로젝트 특화 설정 경로 | Section 3.7.3 (config_file 참조) |

### Iteration 2 → 3 반영 내역

| # | Critic Iteration 2 지적 | 반영 위치 |
|:-:|------------------------|----------|
| 14 | [CRITICAL] 경쟁 Plan 문서 (`daily-action-engine.md`) | Supersedes 선언 + Section 5.4 deprecated 처리 |
| 15 | [HIGH] daily-sync deprecated 처리 모호 | Section 5.4 (deprecated + redirect 명시) |
| 16 | [MEDIUM] AttachmentDownloader 관계 불명확 | Section 3.5.1 (관계 테이블 + 방침 추가) |
| 17 | [LOW] CLI status --json 존재 여부 | Section 5.5 (기존 구현 확인 완료) |

### Iteration 3 → 4 반영 내역

| # | Critic Iteration 3 지적 | 반영 위치 |
|:-:|------------------------|----------|
| 18 | [HIGH] daily/daily-sync SKILL.md 소유권 모순 | Section 5.2: daily/SKILL.md가 9-Phase 실행 주체로 명확화, daily-sync는 deprecated만 |
| 19 | [MEDIUM] daily-action-engine.md 구현 상태 불명 | Supersedes 선언에 "코드 미구현, cleanup 불필요" 명시 |
| 20 | [MEDIUM] Phase 6 모듈 호출 패턴 미지정 | Section 3.7.4 신설 (cd + python -c 패턴) |
| 21 | [LOW] 섹션 번호 순서 불일치 | 5.1→5.2→5.3→5.4→5.5 순서 정렬 완료 |
| 22 | [LOW] skill-unification.plan.md 경로 불명 | Section 7에 전체 경로 추가 |

---

## 변경 이력

| Version | 변경 내용 |
|---------|----------|
| 2.3.0 | Knowledge Layer 통합. state.json v2.0 (learned_context → knowledge/ 디렉토리), Phase 1/4/8 소스 경로 변경, 파일 구조 flat→directory 전환. `docs/01-plan/knowledge-layer.plan.md` (Ralplan Approved) 참조. |
