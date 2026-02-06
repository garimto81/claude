---
name: daily
description: >
  Daily Dashboard - 개인 업무와 프로젝트 진행률을 통합하여 한눈에 파악.
  /gmail, /secretary, Slack List를 스킬 체인으로 연동한 통합 현황 대시보드.
version: 2.0.0

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
  file_patterns:
    - "**/daily/**"
    - "**/checklists/**"
    - "**/daily-briefings/**"
  context:
    - "업무 현황"
    - "프로젝트 관리"
    - "EBS 브리핑"

capabilities:
  - daily_dashboard
  - project_progress
  - standup_briefing
  - retro_review
  - ebs_briefing

model_preference: sonnet
auto_trigger: true
---

# Daily Skill - 통합 대시보드

개인 업무와 프로젝트 진행률을 단일 대시보드로 통합합니다.

## 스킬 체인 연동 (v1.1.0)

`/daily`는 다음 스킬들을 체인으로 호출하여 데이터를 수집합니다:

| 스킬 | 호출 형식 | 수집 데이터 |
|------|----------|------------|
| `/gmail` | `Skill(skill="gmail", args="unread --limit 20 --json")` | 안 읽은 이메일 |
| `/secretary` | `Skill(skill="secretary", args="--json")` | Calendar, GitHub |
| `/slack` | `Skill(skill="slack", args="channels --json")` | Slack 채널 (옵션) |

**스킬 체인 워크플로우:**

```
/daily 실행
    │
    ├─► Skill(skill="gmail", args="unread --limit 20 --json")
    │       └─► Email 데이터 수집
    │
    ├─► Skill(skill="secretary", args="--json")
    │       └─► Calendar + GitHub 데이터 수집
    │
    └─► 결과 통합 → 대시보드 출력
```

## 사용법

### 전체 대시보드

```bash
/daily                      # 스킬 체인 자동 실행
```

**내부 동작:**
1. `Skill(skill="gmail", args="unread --limit 20 --json")` 실행
2. `Skill(skill="secretary", args="--json")` 실행
3. 결과 파싱 및 통합 대시보드 출력

### 서브커맨드

| 커맨드 | 설명 | 용도 |
|--------|------|------|
| `/daily` | 전체 대시보드 | 기본 |
| `/daily standup` | 아침 브리핑 | 하루 시작 |
| `/daily retro` | 저녁 회고 | 하루 마무리 |
| `/daily projects` | 프로젝트만 | 진행률 확인 |
| `/daily ebs` | EBS 데일리 브리핑 | EBS 프로젝트 전용 |

### 옵션

| 옵션 | 설명 |
|------|------|
| `--json` | JSON 형식 출력 |
| `--no-personal` | 개인 업무 제외 (Gmail, Calendar 스킵) |
| `--no-projects` | 프로젝트 제외 |

### Slack 연동

`/auto --daily --slack` 조합으로 Slack 채널에 대시보드 포스팅 및 동기화:

```bash
/auto --daily --slack "#project-channel"    # 대시보드를 채널에 포스팅
/auto --daily standup --slack "#team"       # 아침 브리핑 전송
```

**동작:**
1. `/daily` 스킬 체인 실행 → 결과 수집
2. `Skill(skill="slack", args="send <채널> <대시보드>")` 호출
3. Slack List와 Checklist 양방향 동기화

**상세 워크플로우:** `.claude/skills/auto/SKILL.md` 참조 (`--daily --slack` 섹션)

## 연동 스킬

| 스킬 | 연동 방식 | 데이터 |
|------|----------|--------|
| `/gmail` | `Skill()` 직접 호출 | 안 읽은 이메일, 액션 아이템 |
| `/secretary` | `Skill()` 직접 호출 | Calendar, GitHub |
| `/slack` | `Skill()` 직접 호출 | 채널 메시지, List 동기화 |
| Checklist | 파일 읽기 | `docs/checklists/*.md` |

## 출력 예시

```
================================================================================
                        Daily Dashboard (2026-02-05 Wed)
================================================================================

[Personal] --------------------------------------------------------
  Email (3 action items)
    * [URGENT] 계약서 검토 요청 - Due 2/6 (from: 김대표)
    * [MEDIUM] 회의록 확인 요청 (from: 이팀장)

  Calendar (2 events)
    * 10:00 팀 스탠드업 (Google Meet)
    * 14:00 클라이언트 미팅 (회의실 A)

  GitHub (2 attention needed)
    * PR #42 (secretary): Review pending 3 days

[Projects] --------------------------------------------------------
  PRD-0001  [=========>    ] 80%  인증 시스템
  PRD-0002  [==>           ] 20%  PR 수집
  PRD-0135  [======>       ] 60%  워크플로우 활성화

  Overall: 53% (8/15 items)

================================================================================
```

## EBS 브리핑 모드 (v2.0.0)

`/daily ebs` 서브커맨드로 EBS 프로젝트 전용 데일리 브리핑을 실행합니다.

### 사용법

```bash
/daily ebs                    # 전체 워크플로우 (수집 + 리포트 + 채널 업데이트)
/daily ebs --collect-only     # 데이터 수집만
/daily ebs --no-post          # 채널 메시지 업데이트 생략
/daily ebs --full             # 전체 재수집 (incremental 대신)
/daily ebs --ralph            # Ralph 루프 활성화 (문제 자동 해결)
```

### 실행 워크플로우

**이 서브커맨드가 활성화되면 반드시 아래 절차를 실행하세요!**

#### Step 1: Python 실행

```bash
cd C:\claude\ebs\tools\morning-automation && python main.py <플래그>
```

| 입력 | 실행 명령 |
|------|----------|
| `/daily ebs` | `python main.py --post` |
| `/daily ebs --collect-only` | `python main.py` |
| `/daily ebs --full` | `python main.py --full --post` |

**주의**: `--notify` 플래그 사용 금지 (`chat:write:bot` scope 없음)

#### Step 2: 출력 분석

Python 실행 결과에서 추출할 정보:

| 항목 | 위치 |
|------|------|
| 리포트 경로 | `Report: C:\claude\ebs\docs\...` |
| Slack 메시지 수 | `Total messages: N` |
| Gmail 이메일 수 | `Total emails: N` |
| 업체 수 | `Total items: N` |
| Follow-up 필요 | `Follow-up needed: N` |

#### Step 3: Gmail 첨부파일 분석 (Claude 직접 수행)

```
Read: C:\claude\ebs\tools\morning-automation\data\gmail_emails.json
```

PDF 첨부파일이 있으면 Read 도구로 직접 분석 (20페이지 이하).

#### Step 4: Slack 메시지 분석 (Claude 직접 수행)

```
Read: C:\claude\ebs\tools\morning-automation\data\slack_messages.json
```

미완료 멘션 분석, 긴급도 판단 (HIGH/MEDIUM/LOW), 업체별 요약 생성.

#### Step 5: 결과 표시

```
## EBS 데일리 브리핑 완료

| 항목 | 값 |
|------|-----|
| 리포트 | docs/5-operations/daily-briefings/YYYY-MM-DD.md |
| Slack 메시지 | N개 수집 |
| Gmail 이메일 | N개 수집 |
| 등록 업체 | N개 |
| Follow-up 필요 | N건 |
```

### Ralph 루프 통합

`--ralph` 옵션으로 Ralph 루프 활성화:
- 데이터 수집 실패 시 자동 재시도 (최대 3회)
- Gmail/Slack 인증 에러 시 자동 재인증 시도
- 완료 조건: 데이터 수집 + 리포트 생성 + 채널 업데이트 + 긴급 알림 처리

### 관련 파일

| 파일 | 용도 |
|------|------|
| `C:\claude\ebs\tools\morning-automation\main.py` | 메인 오케스트레이터 |
| `C:\claude\ebs\tools\morning-automation\config\settings.py` | 설정 |
| `C:\claude\ebs\docs\5-operations\daily-briefings\` | 일일 리포트 저장 |

---

## 변경 이력

| 버전 | 변경 |
|------|------|
| 2.0.0 | EBS 브리핑 모드 통합 (`/daily ebs`), 기존 ebs 고유 daily 스킬 흡수 |
| 1.1.0 | 스킬 체인 연동 (Gmail, Secretary) |
| 1.0.0 | 초기 릴리스 |
