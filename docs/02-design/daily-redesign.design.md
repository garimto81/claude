# Design: /auto --daily v3.0 전면 재설계

> 9-Phase Pipeline 상세 설계 - "수집+표시" 에서 "학습+액션 추천" 패러다임으로 전환

**Version**: 1.0.0
**Created**: 2026-02-12
**Status**: Draft
**Plan Reference**: `C:\claude\docs\01-plan\daily-redesign.plan.md` (v2.2.1, Approved)

---

## 1. SKILL.md v3.0 설계

### 1.1 daily/SKILL.md v3.0 YAML Frontmatter

현재 `C:\claude\.claude\skills\daily\SKILL.md`(v2.0.0)를 v3.0.0으로 전면 교체합니다.

```yaml
---
name: daily
description: >
  Daily Dashboard v3.0 - 3소스 통합 학습+액션 추천 엔진.
  Gmail/Slack/GitHub 증분 수집, AI 크로스소스 분석, 액션 초안 생성.
  프로젝트 전문가 모드 + Config Auto-Bootstrap.
version: 3.0.0

triggers:
  keywords:
    - "daily"
    - "오늘 현황"
    - "일일 대시보드"
    - "프로젝트 진행률"
    - "전체 현황"
    - "데일리 브리핑"
    - "morning briefing"
    - "아침 브리핑"
    - "daily-sync"
    - "일일 동기화"
    - "업체 현황"
    - "vendor status"
  file_patterns:
    - "**/daily/**"
    - "**/checklists/**"
    - "**/daily-briefings/**"
  context:
    - "업무 현황"
    - "프로젝트 관리"

capabilities:
  - daily_dashboard
  - incremental_collection
  - cross_source_analysis
  - action_recommendation
  - attachment_analysis
  - expert_context_loading
  - config_auto_bootstrap
  - gmail_housekeeping
  - slack_lists_update

model_preference: sonnet
auto_trigger: true
---
```

**변경 핵심**:
- `daily-sync` 트리거 키워드 흡수 (`"daily-sync"`, `"일일 동기화"`, `"업체 현황"`, `"vendor status"`)
- capabilities에 9-Phase 핵심 기능 명시
- Secretary 의존 완전 제거

### 1.2 daily-sync/SKILL.md Deprecated 처리

`C:\claude\.claude\skills\daily-sync\SKILL.md`의 YAML frontmatter를 다음으로 교체합니다:

```yaml
---
name: daily-sync
deprecated: true
redirect: daily
deprecation_message: "/daily-sync는 /daily v3.0에 통합되었습니다. /daily를 사용하세요."
version: 1.4.0
triggers:
  keywords: []
model_preference: sonnet
auto_trigger: false
---
```

### 1.3 auto/SKILL.md --daily 섹션 변경

`C:\claude\.claude\skills\auto\SKILL.md`의 `--daily` 관련 섹션을 다음으로 교체합니다:

**Phase 1 옵션 라우팅 테이블 변경:**

| 옵션 | 실행 | 설명 |
|------|------|------|
| `--daily` | `Skill(skill="daily")` | daily v3.0 9-Phase Pipeline (Config Bootstrap 내장) |
| `--daily --slack` | `Skill(skill="daily")` | 동일 Pipeline + Phase 6 Slack Lists 갱신 |

**제거 항목:**
- Project Context Discovery 섹션 전체 (Phase 0이 내부 처리)
- Secretary 스킬 체인 호출 (`Skill(skill="secretary", ...)`)
- CWD 기반 `.project-sync.yaml` 탐색 로직 (daily v3.0 Phase 0이 내부 처리)

**간소화된 라우팅:**
```
/auto --daily
    │
    └─► Skill(skill="daily") 직접 호출
        └─► daily v3.0 Phase 0~8 자체 실행
```

---

## 2. Phase별 데이터 흐름

### Phase 0: Config Bootstrap

**Input**: CWD 경로, 프로젝트 디렉토리 구조

**Process**:

```
Step 1: .project-sync.yaml 존재 확인
```

```powershell
# 파일 존재 확인
Test-Path .project-sync.yaml
```

존재하는 경우:
```python
import yaml
from pathlib import Path

config_path = Path(".project-sync.yaml")
config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
version = config.get("version", "1.0")

if version == "1.0":
    # v1.0 호환 모드: 읽기만, 갱신 안 함
    config["meta"] = {"auto_generated": False}
elif version == "2.0":
    if config.get("meta", {}).get("auto_generated", False):
        # 자동 갱신 허용
        pass
    else:
        # 수동 편집 파일: 읽기만
        pass
```

존재하지 않는 경우 (자동 생성):
```powershell
# Step 1: 프로젝트 식별
# CLAUDE.md 존재?
$claudemd = Get-Content CLAUDE.md -ErrorAction SilentlyContinue
# README.md fallback
$readme = Get-Content README.md -ErrorAction SilentlyContinue
# 둘 다 없으면 디렉토리명 사용

# Step 2: Gmail 소스 탐색
python -m lib.gmail status --json

# Step 3: Slack 소스 탐색
python -m lib.slack status --json

# Step 4: GitHub 소스 탐색
git remote -v

# Step 5: YAML 생성
# Claude가 수집 결과를 기반으로 .project-sync.yaml v2.0 생성
```

프로젝트 타입 자동 분류:
```python
# CLAUDE.md 또는 README.md 파싱 결과에서 키워드 매칭
TYPE_KEYWORDS = {
    "vendor_management": ["업체", "vendor", "RFP", "견적", "quote"],
    "development": ["src/", "package.json", "setup.py", "Cargo.toml"],
    "infrastructure": ["Dockerfile", "terraform", "k8s", "helm"],
    "research": ["분석", "analysis"],  # docs/ 비중이 높을 때
    "content": ["영상", "media", "upload", "vimeo"],
}

# 파일 시스템도 함께 확인
if Path("src").exists() or Path("package.json").exists():
    project_type = "development"
```

**Output**: `.project-sync.yaml` v2.0 (신규 생성 또는 기존 로드)

**Error**: CLAUDE.md/README.md 모두 없으면 디렉토리명 기반 최소 설정 생성, `project_type="development"` 기본값, confidence=0.0

---

### Phase 1: Expert Context Loading

**Input**: `.project-sync.yaml`, CLAUDE.md, `.omc/daily-state/<project>.json`

**Process**:

Claude가 아래 3-Tier 소스를 읽고 expert_context JSON을 생성합니다.

```
# Tier 1: Identity Context (500t)
Read: CLAUDE.md
Read: .project-sync.yaml
-> 프로젝트명, 목표, 기술 스택, 핵심 용어, 데이터 소스 목록, communication_style 추출

# Tier 2: Operational Context (2000t)
Read: .omc/daily-state/<project>.json -> learned_context 섹션
-> entities(업체, 사람, 상태), patterns(반복 패턴) 추출

# Tier 3: Deep Context (3000t, 있는 경우만)
Read: docs/ 내 핵심 문서 (README, PRD, 아키텍처 문서)
Read: .omc/daily-state/<project>.learned-context.json (있으면)
-> 도메인 지식, 이전 분석 결과 축적
```

**Output**: 메모리 내 expert_context 구조체 (Phase 4, 5에서 prompt에 주입)

```json
{
  "project_identity": "프로젝트명 - 한줄 설명",
  "project_type": "vendor_management",
  "key_entities": {
    "vendors": [],
    "stakeholders": [],
    "products": []
  },
  "analysis_perspective": "분석 관점 설명",
  "domain_vocabulary": [],
  "current_phase": "현재 진행 단계",
  "recent_decisions": [],
  "communication_style": {
    "email_tone": "professional",
    "slack_tone": "casual",
    "language": "ko"
  }
}
```

**Error**: CLAUDE.md 없으면 Tier 1을 디렉토리명 + `.project-sync.yaml`만으로 구성 (최소 context). daily-state 없으면 Tier 2 생략 (초회 실행).

---

### Phase 2: Incremental Data Collection

**Input**: `.project-sync.yaml` (소스 설정), `.omc/daily-state/<project>.json` (커서)

**Process**:

**Step 0: 인증 확인**

```powershell
# Gmail 인증 확인
python -m lib.gmail status --json
# 출력: {"authenticated": true, "valid": true, "email": "user@gmail.com"}

# Slack 인증 확인
python -m lib.slack status --json
# 출력: {"authenticated": true, "valid": true, ...}

# GitHub 인증 확인
gh auth status
```

인증 실패 소스는 `enabled=false`로 이번 실행에서 skip. 활성 소스 0개면 에러 출력 후 중단.

**Step 1: Gmail 수집**

초회 실행 (daily-state 없음):
```python
from lib.gmail import GmailClient

client = GmailClient()
# historyId 시딩
profile = client.get_profile()  # lib/gmail/client.py:47
history_id = profile["historyId"]

# 최근 7일 수집
emails = client.list_emails(  # lib/gmail/client.py:128
    query="newer_than:7d",
    max_results=50,
    label_ids=[config["daily"]["sources"]["gmail"]["label_id"]]  # 있으면
)
```

증분 실행 (daily-state 존재):
```python
# Primary: History API
result = client.list_history(  # lib/gmail/client.py:72
    start_history_id=state["cursors"]["gmail"]["history_id"],
    history_types=["messageAdded"],
    label_id=config["daily"]["sources"]["gmail"].get("label_id"),
    max_results=100
)
# historyId 404 (만료) 시 Fallback
if not result.get("history"):
    # Fallback: 날짜 기반 검색
    emails = client.list_emails(
        query=f"after:{state['cursors']['gmail']['last_timestamp'][:10].replace('-','/')}",
        max_results=50
    )
```

**Step 2: Slack 수집**

```python
from lib.slack import SlackClient

client = SlackClient()
channel_id = config["daily"]["sources"]["slack"]["channel_id"]

# 초회: 7일 lookback
import time
oldest = str(time.time() - 604800)  # 7일

# 증분: 마지막 ts 이후
oldest = state["cursors"]["slack"]["last_ts"]

messages = client.get_history(  # lib/slack/client.py:225
    channel=channel_id,
    limit=100,
    oldest=oldest
)
```

**Step 3: GitHub 수집**

```powershell
# 이슈
gh issue list --repo garimto81/claude --since "2026-02-11T18:00:00Z" --json number,title,state,author,updatedAt,labels

# PR
gh pr list --repo garimto81/claude --json number,title,state,author,updatedAt,reviewDecision

# 최근 커밋
gh api repos/garimto81/claude/commits --jq '.[0:10] | .[] | {sha: .sha[0:7], message: .commit.message[0:80], date: .commit.author.date}'
```

**Output**: 소스별 raw data (이메일 목록, Slack 메시지 목록, GitHub 이슈/PR)

**Error**:
- Gmail History API 404 (historyId 만료) -> `list_emails(query="after:...")` fallback
- Slack rate limit -> 1.2초 간격 자동 대기 (`RateLimiter` 내장, `lib/slack/client.py:57`)
- 인증 실패 -> 해당 소스 skip, partial report

---

### Phase 3: Attachment Analysis

**Input**: Phase 2에서 수집된 이메일 메타데이터 (첨부파일 정보 포함)

**Process**:

**Step 1: 첨부파일 식별**

Phase 2에서 수집된 `GmailMessage.attachments` 목록에서 분석 대상 필터링:
- PDF: `mime_type == "application/pdf"`
- Excel: `mime_type`에 `spreadsheet` 또는 `excel` 포함
- 이미지: `mime_type`이 `image/png` 또는 `image/jpeg`

**Step 2: SHA256 캐시 확인**

```python
import hashlib

# 캐시 위치: .omc/daily-state/<project>.json의 cache.attachments
cache = state.get("cache", {}).get("attachments", {})

# 각 첨부파일의 SHA256을 message_id + attachment_id로 생성
cache_key = hashlib.sha256(f"{message_id}:{attachment_id}".encode()).hexdigest()
if cache_key in cache:
    # 캐시 적중 -> 이전 분석 결과 재사용
    pass
```

**Step 3: 첨부파일 다운로드**

```python
# 신규 메서드 (lib/gmail/client.py에 추가 예정)
import base64

# GmailClient.download_attachment(message_id, attachment_id) -> bytes
result = client.service.users().messages().attachments().get(
    userId='me',
    messageId=message_id,
    id=attachment_id
).execute()
file_bytes = base64.urlsafe_b64decode(result['data'])
```

임시 저장: `.omc/daily-state/attachments/<sha256>.ext`

**Step 4: 파일 타입별 분석**

| 타입 | 조건 | 방법 |
|------|------|------|
| PDF (20p 이하) | `page_count <= 20` | Claude Read tool 직접 분석 |
| PDF (20p 초과) | `page_count > 20` | `lib/pdf_utils` PDFExtractor 청크 분할 |
| Excel/CSV | - | 구조 요약 (행/열, 헤더, 샘플 5행) |
| 이미지 | PNG/JPG | Claude Vision 분석 |
| 기타 | - | 메타데이터만 기록 |

PDF 20p 초과 분석:
```python
from lib.pdf_utils import PDFExtractor  # lib/pdf_utils/extractor.py

with PDFExtractor(temp_file_path) as pdf:
    info = pdf.get_info()  # extractor.py:205
    if info.page_count > 20:
        # 20페이지씩 분할
        split = pdf.split_pages(  # extractor.py:242
            output_dir=".omc/daily-state/attachments/chunks",
            pages_per_split=20
        )
        # 각 청크를 Claude Read로 분석
```

**Step 5: 분석 관점 적용**

expert_context.analysis_perspective에 따른 분석 프롬프트:
- `vendor_management`: "견적서인가? 금액, 유효기간, 조건은?"
- `development`: "API 스펙인가? 변경점, breaking change는?"

**Output**: 첨부파일별 분석 결과 (summary, key_data)

**Error**:
- 다운로드 실패 -> 해당 첨부파일 skip, 메타데이터만 기록
- PDF 암호화 -> `PDFEncryptedError` catch, skip 후 보고
- 토큰 과다 -> 20페이지 제한 + 캐시로 방지

---

### Phase 4: AI Cross-Source Analysis

**Input**: Phase 2 raw data, Phase 3 첨부파일 분석 결과, Phase 1 expert_context

**Process**:

**Step 1: 소스별 독립 분석**

Claude가 각 소스 데이터를 독립적으로 분석합니다. expert_context를 system prompt에 주입하여 도메인 전문가로 동작합니다.

**Step 2: 크로스 소스 연결 분석**

소스별 분석 결과를 통합하여 소스 간 연결점을 찾습니다.

**Output**: 구조화된 분석 결과 (소스별 요약 + 크로스 소스 인사이트)

**Error**: 단일 소스만 활성인 경우 크로스 소스 분석 생략, 해당 소스 독립 분석만 수행

---

### Phase 5: Action Recommendation

**Input**: Phase 4 분석 결과, expert_context.communication_style

**Process**:

Claude가 분석 결과를 기반으로 구체적인 액션 초안을 생성합니다.

| 액션 유형 | 생성 조건 |
|----------|----------|
| Slack 메시지 초안 | 미응답 질문, follow-up 필요 |
| 이메일 회신 초안 | 미응답 48h+, 견적 수신 |
| GitHub 액션 | PR 리뷰 대기 3일+, 이슈 미응답 |

톤 캘리브레이션은 `communication_style`을 참조합니다.

**Output**: 최대 10건 액션 아이템 (URGENT/HIGH/MEDIUM 정렬)

**Error**: 분석 결과 없으면 "현재 추가 액션이 필요하지 않습니다" 표시

---

### Phase 6: Project-Specific Operations

**Input**: Phase 4/5 결과, `.project-sync.yaml`의 `project_type` 및 `config_file`

**Process**:

`project_type`에 따라 조건부 실행:

**vendor_management 타입:**

```powershell
# Slack Lists 갱신 (ListsSyncManager)
cd C:\claude\wsoptv_ott && python -c "
import sys; sys.path.insert(0, 'scripts/sync')
from lists_sync import ListsSyncManager

manager = ListsSyncManager()
manager.update_item('Vimeo OTT',
    status='협상 중',
    quote='$115K/yr',
    last_contact='2026-02-12',
    next_action='수정 견적 대기')
manager.generate_summary_message()
manager.post_summary()
"

# 업체 상태 자동 전이 (StatusInferencer)
cd C:\claude\wsoptv_ott && python -c "
import sys; sys.path.insert(0, 'scripts/sync')
from analyzers.status_inferencer import StatusInferencer
from config_models import ProjectConfig
import yaml

config = ProjectConfig(**yaml.safe_load(open('wsoptv_sync_config.yaml')))
inferencer = StatusInferencer(config=config)
# Phase 4 분석 결과를 기반으로 상태 전이 판단
"

# 견적 비교표 (QuoteFormatter)
cd C:\claude\wsoptv_ott && python -c "
import sys; sys.path.insert(0, 'scripts/sync')
from formatters.quote_formatter import QuoteFormatter

formatter = QuoteFormatter()
# Phase 3에서 추출된 견적 정보로 포맷팅
"
```

**development 타입:**

```powershell
# CI/CD 상태
gh run list --repo garimto81/claude --limit 5 --json databaseId,status,conclusion,name,createdAt

# 브랜치 상태
gh pr list --repo garimto81/claude --state open --json number,title,headRefName,updatedAt

# 마일스톤 진행률
gh api repos/garimto81/claude/milestones --jq '.[] | {title, open_issues, closed_issues}'
```

**Output**: 프로젝트 특화 결과 (Slack Lists 갱신 결과, CI/CD 상태 등)

**Error**: `config_file` 없으면 Phase 6 skip. Slack Lists API 실패 -> 경고 출력 후 계속 진행.

---

### Phase 7: Gmail Housekeeping

**Input**: Phase 2 수집 결과, `.project-sync.yaml`의 `housekeeping` 설정

**Process**:

**7a. 라벨 자동 적용** (`housekeeping.gmail_label_auto: true` 일 때):

```python
from lib.gmail import GmailClient

client = GmailClient()
label_id = config["daily"]["sources"]["gmail"]["label_id"]
vendor_domains = config["daily"]["sources"]["gmail"]["vendor_domains"]

# Phase 2에서 수집된 이메일 중 라벨 없는 것 필터
for email in unlabeled_emails:
    sender_domain = email.sender.split("@")[-1].rstrip(">")
    if sender_domain in vendor_domains:
        # 시스템 메일 제외 (noreply, notifications, drive-shares)
        if not any(kw in email.sender.lower() for kw in ["noreply", "no-reply", "notifications@", "drive-shares"]):
            client.modify_labels(  # lib/gmail/client.py:350
                email_id=email.id,
                add_labels=[label_id]
            )
```

**7b. INBOX 정리** (`housekeeping.inbox_cleanup` 설정에 따라):

| 모드 | 동작 |
|------|------|
| `"auto"` | 자동 archive |
| `"confirm"` | 대상 목록 표시 후 사용자 확인 |
| `"skip"` | 건너뜀 (기본) |

```python
if inbox_cleanup == "confirm":
    # 대상 목록 출력 후 AskUserQuestion으로 확인
    # 승인 시:
    for email in labeled_inbox_emails:
        client.archive(email.id)  # lib/gmail/client.py:392
```

**Output**: "N개 라벨링, M개 정리" 로그

**Error**: Gmail API 실패 -> 해당 동작 skip, 경고 출력

---

### Phase 8: State Update

**Input**: 전체 Phase 실행 결과

**Process**:

**Phase A (소스 커서 기록 - 수집 완료 직후):**

```python
import json
from datetime import datetime
from pathlib import Path

state_path = Path(f".omc/daily-state/{project_name}.json")
state_path.parent.mkdir(parents=True, exist_ok=True)

# 커서 갱신
state["cursors"]["gmail"]["history_id"] = new_history_id  # get_profile()에서
state["cursors"]["gmail"]["last_timestamp"] = datetime.utcnow().isoformat() + "Z"
state["cursors"]["slack"]["last_ts"] = last_message_ts
state["cursors"]["github"]["last_check"] = datetime.utcnow().isoformat() + "Z"
state["last_run"] = datetime.utcnow().isoformat() + "Z"
state["run_count"] = state.get("run_count", 0) + 1
```

**Phase B (분석 캐시 기록 - 분석 완료 후):**

```python
# 첨부파일 캐시 추가
for sha, analysis in new_attachment_analyses.items():
    state["cache"]["attachments"][sha] = analysis

# 학습 컨텍스트 갱신
state["learned_context"]["entities"].update(new_entities)
state["learned_context"]["patterns"].extend(new_patterns)
```

**Config 자동 갱신** (`.project-sync.yaml`의 `auto_generated: true`인 경우만):

```python
# 새 도메인 감지 시 pending_additions에 추가
config["meta"]["pending_additions"].append({
    "type": "gmail_domain",
    "value": "newvendor.com",
    "detected_at": datetime.utcnow().isoformat()
})
```

**Output**: 갱신된 state 파일, 갱신된 config 파일 (조건부)

**Error**: 파일 쓰기 실패 -> 다음 실행에서 같은 데이터 재수집 (Phase A 롤백 효과). 데이터 손실 없음.

---

## 3. AI Prompt 설계

### 3.1 Phase 1: Expert Context Assembly Prompt

```
당신은 프로젝트 전문가입니다. 아래 정보를 읽고 프로젝트에 대한 전문가 컨텍스트를 구성하세요.

## 프로젝트 정보

### CLAUDE.md 내용:
{claude_md_content}

### .project-sync.yaml 설정:
{project_sync_yaml}

### 이전 학습 컨텍스트 (있는 경우):
{learned_context_json}

### docs/ 핵심 문서 (있는 경우):
{docs_summaries}

## 생성할 JSON 구조

다음 JSON을 생성하세요. 총 5500 tokens 이내로 압축합니다.

{
  "project_identity": "프로젝트명 - 한줄 목표/설명",
  "project_type": "vendor_management | development | infrastructure | research | content",
  "key_entities": {
    "vendors": ["업체명1", "업체명2"],
    "stakeholders": ["담당자1"],
    "products": ["제품명"]
  },
  "analysis_perspective": "이 프로젝트에서 일일 분석 시 집중해야 할 관점 1-2문장",
  "domain_vocabulary": ["RFP", "CDN", "DRM"],
  "current_phase": "현재 진행 단계",
  "recent_decisions": ["최근 주요 결정사항"],
  "communication_style": {
    "email_tone": "professional | casual | formal",
    "slack_tone": "casual | professional",
    "language": "ko | en | mixed"
  }
}

## 규칙
- project_type이 불명확하면 "development"로 기본 설정
- 이전 학습 컨텍스트가 없으면 entities를 빈 배열로
- communication_style은 .project-sync.yaml에서 가져오되, 없으면 email_tone="professional", slack_tone="casual", language="ko" 기본값
- 도메인 용어는 CLAUDE.md의 기술 스택과 프로젝트 설명에서 추출
```

### 3.2 Phase 4: 소스별 독립 분석 Prompt

```
당신은 {project_identity}의 전문가입니다.

## 프로젝트 컨텍스트
{expert_context_json}

## 분석 관점
{analysis_perspective}

## Gmail 데이터 (최근 수집)
{gmail_emails_json}

## Slack 데이터 (최근 수집)
{slack_messages_json}

## GitHub 데이터 (최근 수집)
{github_data_json}

## 첨부파일 분석 결과
{attachment_analyses_json}

## 지시사항

각 소스별로 독립 분석하세요:

### 1. Gmail 분석
각 이메일/스레드에 대해:
- **발신자**: 누구인가 (key_entities 참조)
- **핵심 내용**: 1-2줄 요약
- **긴급도**: URGENT(미응답 48h+, 마감일 D-1) / HIGH(미응답 24h+, 견적 수신) / MEDIUM(일반) / LOW(정보 전달)
- **필요 액션**: 회신 필요 여부, 내부 공유 필요 여부
- **견적 정보**: 금액, 통화, 유효기간 (첨부파일 분석 결과 통합)
- **상태 추론**: 협상 단계 (vendor_management인 경우)

### 2. Slack 분석
채널 메시지에서:
- **의사결정 사항**: 합의된 내용
- **액션 아이템**: 누가 무엇을 해야 하는지
- **미해결 질문**: 답변이 필요한 질문
- **업체/프로젝트 관련 언급**: key_entities와 매칭

### 3. GitHub 분석
- **PR 상태**: 리뷰 대기, 변경 요청, 승인
- **이슈 상태**: 미해결, 할당, 마감일
- **CI/CD**: 실패한 워크플로우

### 출력 형식 (JSON)

{
  "gmail_analysis": [
    {
      "email_id": "...",
      "sender": "...",
      "summary": "...",
      "urgency": "URGENT|HIGH|MEDIUM|LOW",
      "needs_reply": true/false,
      "reply_deadline": "YYYY-MM-DD 또는 null",
      "quotes": [...],
      "vendor_status": "negotiating (vendor_management만)"
    }
  ],
  "slack_analysis": {
    "decisions": [...],
    "action_items": [...],
    "unanswered_questions": [...],
    "entity_mentions": [...]
  },
  "github_analysis": {
    "pending_reviews": [...],
    "open_issues": [...],
    "failed_workflows": [...]
  }
}
```

### 3.3 Phase 4: 크로스 소스 분석 Prompt

```
당신은 {project_identity}의 전문가입니다.

## 소스별 독립 분석 결과
{source_analysis_json}

## 프로젝트 컨텍스트
{expert_context_json}

## 지시사항

소스 간 연결점을 찾아 크로스 소스 인사이트를 도출하세요:

1. **동일 주제 감지**: Gmail에서 논의된 내용이 Slack에서도 언급되었는가?
2. **액션 연결**: 이메일 요청사항이 GitHub 이슈/PR로 이어지는가?
3. **상태 불일치**: Gmail에서는 "완료"라 했는데 GitHub 이슈가 아직 open인가?
4. **타임라인 구성**: 동일 주제의 소스별 이벤트를 시간순으로 연결

### 출력 형식

{
  "cross_source_insights": [
    {
      "topic": "주제명",
      "sources": ["gmail", "slack"],
      "insight": "Gmail에서 업체 A가 견적을 보냈고, Slack에서 팀이 검토 중으로 논의함",
      "urgency": "HIGH",
      "recommendation": "팀 논의 결과를 업체에 회신 필요"
    }
  ],
  "timeline": [
    {
      "date": "2026-02-10",
      "source": "gmail",
      "event": "업체 A 견적 수신"
    },
    {
      "date": "2026-02-11",
      "source": "slack",
      "event": "팀 내부 검토 논의"
    }
  ]
}
```

### 3.4 Phase 5: Action Recommendation Prompt

```
당신은 {project_identity}의 전문가이자 비서입니다.

## 분석 결과
{phase4_analysis_json}

## 커뮤니케이션 스타일
{communication_style_json}

## 이전 피드백 (톤 교정 기록)
{action_feedback_json}

## 지시사항

분석 결과를 기반으로 구체적인 액션 아이템을 추천하세요.

### 액션 유형별 생성 규칙

1. **이메일 회신 초안**
   - 트리거: 미응답 48h+, 견적 수신, 명시적 요청
   - email_tone에 따른 문체 적용:
     - "professional": 존칭, 비즈니스 형식 (예: "검토 감사합니다. 말씀하신 견적 관련...")
     - "casual": 반말, 간결 (예: "견적 확인했어요. 다음 주까지...")
     - "formal": 극존칭, 공식 형식 (예: "귀사의 제안서를 검토하였습니다...")
   - language에 따른 언어 선택

2. **Slack 메시지 초안**
   - 트리거: 미응답 질문, follow-up 필요
   - slack_tone에 따른 문체 적용
   - 대상 채널 명시

3. **GitHub 액션**
   - 트리거: PR 리뷰 대기 3일+, 이슈 미응답
   - 리뷰 코멘트 초안 또는 이슈 응답 초안

### 제한 규칙
- 최대 10건
- URGENT -> HIGH -> MEDIUM 순서로 정렬
- 각 액션에 예상 소요 시간 명시 (1분, 5분, 15분, 30분)
- 액션 없으면: "현재 추가 액션이 필요하지 않습니다"

### 이전 피드백 반영
action_feedback에 톤 교정 기록이 있으면 해당 패턴을 반영하세요.
예: "한국 업체에는 한글 존칭 사용" -> 한국 업체 이메일은 한글 존칭으로 작성

### 출력 형식

{
  "actions": [
    {
      "id": 1,
      "type": "email_reply",
      "priority": "URGENT",
      "target": "vendor@example.com",
      "subject": "RE: 견적 검토 관련",
      "draft": "검토 감사합니다. ...",
      "estimated_time": "5분",
      "reason": "48시간 미응답, 견적 유효기간 D-3"
    },
    {
      "id": 2,
      "type": "slack_message",
      "priority": "HIGH",
      "target_channel": "#wsoptv",
      "draft": "견적 검토 결과 공유합니다...",
      "estimated_time": "1분",
      "reason": "팀 내부 공유 필요"
    }
  ],
  "summary": "URGENT 1건, HIGH 2건, MEDIUM 3건 - 총 예상 소요 시간 약 30분"
}
```

---

## 4. Error Handling Matrix

| # | 에러 시나리오 | 증상 | 감지 방법 | 복구 전략 | 사용자 메시지 |
|:-:|-------------|------|----------|----------|-------------|
| 1 | Gmail 인증 미설정 | `authenticated: false` | `python -m lib.gmail status --json` | Gmail skip, partial report | "Gmail 미인증. `python -m lib.gmail login` 실행 필요" |
| 2 | Gmail 토큰 만료 | `GmailAuthError` 발생 | `client.validate_token()` 실패 | 자동 refresh 시도 -> 실패 시 skip | "Gmail 토큰 만료. 재인증: `python -m lib.gmail login`" |
| 3 | Gmail historyId 만료 | History API 404 | `list_history()` 빈 결과 + 404 | `list_emails(query="after:...")` fallback | (자동 복구, 사용자 메시지 없음) |
| 4 | Slack 인증 미설정 | `authenticated: false` | `python -m lib.slack status --json` | Slack skip, partial report | "Slack 미인증. `python -m lib.slack login` 실행 필요" |
| 5 | Slack rate limit | `SlackRateLimitError` | `Retry-After` 헤더 | 대기 후 재시도 (내장) | (자동 복구, 사용자 메시지 없음) |
| 6 | GitHub CLI 미인증 | `gh auth status` 실패 | exit code != 0 | GitHub skip, partial report | "GitHub 미인증. `gh auth login` 실행 필요" |
| 7 | 전체 소스 인증 실패 | 활성 소스 0개 | 3소스 모두 disabled | Pipeline 중단 | "활성 데이터 소스 없음. Gmail/Slack/GitHub 중 하나 설정 필요" |
| 8 | 첨부파일 다운로드 실패 | API 에러 | `HttpError` catch | 해당 첨부파일 skip | "첨부파일 '{filename}' 다운로드 실패, 메타데이터만 기록" |
| 9 | PDF 암호화 | `PDFEncryptedError` | `PDFExtractor` 초기화 시 | skip + 보고 | "'{filename}' 암호화된 PDF, 분석 불가" |
| 10 | State 파일 쓰기 실패 | Permission 에러 | `IOError` catch | 다음 실행에서 재수집 | "상태 저장 실패. 다음 실행 시 동일 데이터 재수집됩니다" |

---

## 5. Output Format

### 5.1 전체 대시보드 출력 템플릿

```
================================================================================
                   Daily Dashboard v3.0 (2026-02-12 Wed)
                   프로젝트: {project_identity}
================================================================================

[소스 현황] --------------------------------------------------------
  Gmail: {N}건 수집 ({new}건 신규) {auth_status}
  Slack: {N}건 수집 ({new}건 신규) {auth_status}
  GitHub: 이슈 {N}건, PR {N}건 {auth_status}

[크로스 소스 인사이트] ------------------------------------------------
  1. {topic}: {insight} (소스: Gmail+Slack)
  2. {topic}: {insight} (소스: Slack+GitHub)

[액션 아이템] --------------------------------------------------------

  🔴 URGENT ({N}건)

  #{id}. [{type}] {target}
     내용: {summary}
     초안: {draft_preview}
     소요: {estimated_time} | 사유: {reason}

  🟡 HIGH ({N}건)

  #{id}. [{type}] {target}
     내용: {summary}
     초안: {draft_preview}
     소요: {estimated_time} | 사유: {reason}

  🔵 MEDIUM ({N}건)

  #{id}. [{type}] {target}
     내용: {summary}

[소스별 상세] --------------------------------------------------------

  Gmail ({N}건)
    * [{urgency}] {subject} - from: {sender} ({days}일 전)
      {summary_1line}

  Slack #{channel} ({N}건)
    * 의사결정: {decision}
    * 액션 아이템: {action_item}
    * 미해결 질문: {question}

  GitHub ({N}건)
    * PR #{number}: {title} ({state}, {review_status})
    * Issue #{number}: {title} ({state})

[첨부파일 분석] --------------------------------------------------------
  * {filename} ({pages}p, {file_type}): {summary}
  * {filename}: {summary}

================================================================================
  총 액션: {total}건 (URGENT {n}, HIGH {n}, MEDIUM {n})
  예상 소요: 약 {total_time}분
  다음 실행 시: 증분 수집 (커서 저장됨)
================================================================================
```

### 5.2 vendor_management 타입 추가 섹션

```
[업체 현황] (vendor_management) ----------------------------------------

  | 업체 | 상태 | 견적 | 마지막 연락 | 긴급도 |
  |------|------|------|-----------|--------|
  | {vendor} | {status} | {quote} | {last_contact} | {urgency} |

  견적 비교:
  {quote_comparison_table}

  Slack Lists 갱신:
  * {vendor}: {field} -> "{new_value}" (이전: "{old_value}")

  요약 메시지 포스팅: #{slack_channel}
```

### 5.3 development 타입 추가 섹션

```
[개발 현황] (development) ----------------------------------------

  CI/CD 상태:
  | Workflow | 상태 | 마지막 실행 |
  |----------|------|-----------|
  | {name} | {status} {conclusion} | {created_at} |

  브랜치 상태:
  * PR #{number}: {title} ({head_ref} -> main, {updated_at})

  마일스톤 진행률:
  * {title}: {closed}/{total} ({percentage}%)
```

---

## 6. Module Integration Interface

### 6.1 GmailClient 메서드 (`C:\claude\lib\gmail\client.py`)

| 메서드 | 위치 | Phase | 용도 | 기존/신규 |
|--------|------|:-----:|------|:---------:|
| `get_profile()` | :47 | 2, 8 | historyId 조회, 계정 확인 | 기존 |
| `list_history(start_history_id, ...)` | :72 | 2 | 증분 수집 (delta) | 기존 |
| `list_emails(query, max_results, label_ids)` | :128 | 2 | 초회 수집, historyId 만료 fallback | 기존 |
| `get_email(email_id)` | :166 | 2, 3 | 이메일 상세 조회 (첨부파일 메타데이터 포함) | 기존 |
| `list_labels()` | :326 | 0 | Bootstrap 시 라벨 fuzzy match | 기존 |
| `modify_labels(email_id, add_labels, remove_labels)` | :350 | 7 | 라벨 자동 적용 | 기존 |
| `archive(email_id)` | :392 | 7 | INBOX 정리 | 기존 |
| `download_attachment(message_id, attachment_id)` | 신규 | 3 | 첨부파일 바이너리 다운로드 | **신규** |

**신규 메서드 시그니처:**
```python
def download_attachment(self, message_id: str, attachment_id: str) -> bytes:
    """Gmail 첨부파일 바이너리 다운로드.

    Args:
        message_id: Gmail 메시지 ID
        attachment_id: 첨부파일 ID (GmailAttachment.id)

    Returns:
        bytes: 디코딩된 바이너리 데이터

    Raises:
        GmailAPIError: API 호출 실패
    """
```

### 6.2 SlackClient 메서드 (`C:\claude\lib\slack\client.py`)

| 메서드 | 위치 | Phase | 용도 |
|--------|------|:-----:|------|
| `get_history(channel, limit, oldest)` | :225 | 2 | 증분 수집 (oldest 파라미터) |
| `list_channels(include_private)` | :273 | 0 | Bootstrap 시 채널 fuzzy match |
| `send_message(channel, text)` | :155 | 6 | 요약 메시지 포스팅 |
| `validate_token()` | :344 | 0 | 인증 확인 |

**SlackUserClient** (`C:\claude\lib\slack\client.py:556`):

| 메서드 | Phase | 용도 |
|--------|:-----:|------|
| `create_list()` | 6 | Slack Lists 생성 (필요 시) |
| `add_list_item()` | 6 | 업체 항목 추가 |
| `get_list_items()` | 6 | 기존 항목 조회 |

### 6.3 gh CLI 커맨드

| 커맨드 | Phase | 용도 |
|--------|:-----:|------|
| `gh auth status` | 0 | 인증 확인 |
| `gh issue list --since {ISO} --json ...` | 2 | 이슈 증분 수집 |
| `gh pr list --json ...` | 2, 6 | PR 목록 |
| `gh run list --limit 5 --json ...` | 6 | CI/CD 상태 (development) |
| `gh api repos/{owner}/{repo}/milestones` | 6 | 마일스톤 (development) |

### 6.4 Phase 6 프로젝트별 모듈 호출 패턴

**원칙**: `cd {project_path} && python -c "..."` 패턴 사용. `sys.path` 조작은 inline script 내부에서만 허용.

**vendor_management 모듈:**

| 모듈 | 경로 | 호출 패턴 |
|------|------|----------|
| StatusInferencer | `wsoptv_ott/scripts/sync/analyzers/status_inferencer.py` | `cd C:\claude\wsoptv_ott && python -c "import sys; sys.path.insert(0, 'scripts/sync'); from analyzers.status_inferencer import StatusInferencer; ..."` |
| QuoteFormatter | `wsoptv_ott/scripts/sync/formatters/quote_formatter.py` | `cd C:\claude\wsoptv_ott && python -c "import sys; sys.path.insert(0, 'scripts/sync'); from formatters.quote_formatter import QuoteFormatter; ..."` |
| ListsSyncManager | `wsoptv_ott/scripts/sync/lists_sync.py` | `cd C:\claude\wsoptv_ott && python scripts\sync\lists_sync.py update --vendor "Name" --field "status" --value "값"` |
| AttachmentDownloader | `wsoptv_ott/scripts/sync/collectors/attachment_downloader.py` | Phase 3에서 직접 호출하지 않음 (GmailClient.download_attachment() 사용). Phase 6에서 vendor_management 전용 캐시 활용 시에만 사용 |

**lib/pdf_utils 모듈:**

| 클래스 | 경로 | 호출 |
|--------|------|------|
| PDFExtractor | `lib/pdf_utils/extractor.py` | `from lib.pdf_utils import PDFExtractor` (lib이 sys.path에 있으므로 직접 import) |

---

## 변경 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| 1.0.0 | 2026-02-12 | 초기 Design 문서 작성 |
