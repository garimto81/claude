# /auto REFERENCE - 상세 워크플로우

이 파일은 SKILL.md에서 분리된 상세 워크플로우입니다.

---

## Phase 0: PDCA 문서화 상세 (BKIT 워크플로우)

**모든 작업은 PDCA 사이클을 따릅니다:**

```
Plan --> Design --> Do --> Check --> Act
 |         |        |        |        |
 v         v        v        v        v
계획문서  설계문서   구현    갭검증   개선반복
                            |
                   병렬 검증: OMC Architect + BKIT gap-detector
```

### Step 0.0: Knowledge Context Loading

daily가 축적한 프로젝트 지식을 작업 세션에 로드합니다. `--daily` 옵션 사용 시에는 `Skill(skill="daily")`로 위임되어 auto Phase 0에 도달하지 않으므로, 이 Step은 비-daily 세션에서만 실행됩니다.

```
1. 프로젝트명 식별:
   - .project-sync.yaml 존재 -> project_name 필드
   - 없으면 -> CWD 디렉토리명
2. Read: .omc/daily-state/<project>/knowledge/snapshots/latest.json
3. 존재 -> 컨텍스트 주입 (~1300t):
   [프로젝트 지식] ----------------------
   프로젝트: {project_phase}
   핵심 토픽: {active_topics}
   주의 Entity: {key_entities 요약}
   최근 이벤트: {recent_events_digest}
   활성 패턴: {active_patterns}
   -----------------------------------------
4. 존재하지 않음 -> 건너뜀 (daily 미실행 프로젝트)
```

**토큰 예산**: ~1300t (Tier 2 Operational Context 2000t 슬롯 내)

### Step 0.1: Plan 문서 생성 (Ralplan 연동)

**복잡도 점수 판단 (MANDATORY - 5점 만점):**

| # | 조건 | 1점 기준 | 0점 기준 |
|:-:|------|---------|---------|
| 1 | **파일 범위** | 3개 이상 파일 수정 예상 | 1-2개 파일 |
| 2 | **아키텍처** | 새 패턴/구조 도입 | 기존 패턴 내 수정 |
| 3 | **의존성** | 새 라이브러리/서비스 추가 | 기존 의존성만 사용 |
| 4 | **모듈 영향** | 2개 이상 모듈/패키지 영향 | 단일 모듈 내 변경 |
| 5 | **사용자 명시** | `ralplan` 키워드 포함 | 키워드 없음 |

**판단 규칙:**
- **score >= 3** -> Ralplan 실행 (Planner + Architect + Critic 합의)
- **score < 3** -> Planner 단독 실행

**판단 로그 출력 (항상 필수):**
```
=== 복잡도 판단 ===
파일 범위: {0|1}점 ({근거})
아키텍처: {0|1}점 ({근거})
의존성:   {0|1}점 ({근거})
모듈 영향: {0|1}점 ({근거})
사용자 명시: {0|1}점
총점: {score}/5 -> {Ralplan 실행|Planner 단독}
===================
```

**score >= 3: Ralplan 실행**

```
Skill(skill="oh-my-claudecode:ralplan", args="작업 설명. Critic 추가 검증: docs/01-plan/ 내 기존 Plan과 범위 겹침 여부 확인 필수")
```
-> `docs/01-plan/{feature}.plan.md` 생성

**score < 3: Planner 단독 실행**
```
Task(
  subagent_type="oh-my-claudecode:planner",
  model="opus",
  description="[PDCA Plan] 기능 계획",
  prompt="... (복잡도 점수: {score}/5, 판단 근거 포함)"
)
```

### Step 0.2: Design 문서 생성 (Plan 게이트 검증 포함)

**Plan->Design 전환 게이트 (MANDATORY):**

| # | 필수 섹션 | 확인 방법 |
|:-:|----------|----------|
| 1 | 배경/문제 정의 | `## 배경` 또는 `## 문제 정의` 헤딩 존재 |
| 2 | 구현 범위 | `## 구현 범위` 또는 `## 범위` 헤딩 존재 |
| 3 | 예상 영향 파일 | 파일 경로 목록 포함 |
| 4 | 위험 요소 | `## 위험` 또는 `위험 요소` 헤딩 존재 |

누락 시 Plan 문서를 먼저 보완한 후 Design으로 진행합니다.

```
Task(
  subagent_type="oh-my-claudecode:architect",
  model="opus",
  description="[PDCA Design] 기능 설계",
  prompt="docs/01-plan/{feature}.plan.md를 참조하여 설계 문서를 작성하세요."
)
```
-> `docs/02-design/{feature}.design.md` 생성

### Step 0.3: Do (구현)
- 기존 /auto 워크플로우 (Ralplan + Ultrawork)

### Step 0.4: Check (이중 검증 - 병렬)
```
Task(subagent_type="oh-my-claudecode:architect", model="opus", ...)
Task(subagent_type="bkit:gap-detector", model="opus", ...)
```
- Architect: 기능 완성도 검증
- gap-detector: 설계-구현 90% 일치 검증

### Step 0.5: Act (자동 실행 - CRITICAL)

**PDCA 완료 시 자동 실행 규칙 ("Recommended" 출력 금지):**

| Check 결과 | 자동 실행 |
|-----------|----------|
| gap < 90% | bkit:pdca-iterator (최대 5회 반복) |
| gap >= 90% | bkit:report-generator (자동 호출) -> docs/04-report/{feature}.report.md |
| Architect REJECT | oh-my-claudecode:executor (수정) -> Check Phase 재실행 |
| 모든 조건 충족 | 완료 보고서 자동 생성 |

**Case 1: gap < 90%**
```
Task(
  subagent_type="bkit:pdca-iterator",
  model="sonnet",
  description="[PDCA Act] 갭 자동 개선",
  prompt="설계-구현 갭을 90% 이상으로 개선하세요. 최대 5회 반복."
)
```

**Case 2: gap >= 90%**
```
Task(
  subagent_type="bkit:report-generator",
  model="haiku",
  description="[PDCA Report] 완료 보고서 생성",
  prompt="PDCA 사이클 완료 보고서를 생성하세요.
  포함 항목: Plan 요약, Design 요약, 구현 결과, Check 결과, 교훈
  출력 위치: docs/04-report/{feature}.report.md"
)
```

**Case 3: Architect REJECT**
```
Task(
  subagent_type="oh-my-claudecode:executor",
  model="sonnet",
  description="[PDCA Act] Architect 피드백 반영",
  prompt="Architect 거부 사유를 해결하세요: {rejection_reason}"
)
# 해결 후 Check Phase 재실행
```

---

## `--slack` 옵션 워크플로우

Slack 채널의 모든 메시지를 분석하여 프로젝트 컨텍스트로 활용합니다.

**Step 1: 인증 확인**
```bash
cd C:\claude && python -m lib.slack status --json
```
- `"authenticated": false` -> 에러 출력 후 중단

**Step 2: 채널 히스토리 수집**
```bash
python -m lib.slack history "<채널ID>" --limit 100 --json
```

**Step 3: 메시지 분석 (Analyst Agent)**
```
Task(
  subagent_type="oh-my-claudecode:analyst",
  model="opus",
  prompt="SLACK CHANNEL ANALYSIS
  채널: <채널ID>
  분석 항목: 주요 토픽, 핵심 결정사항, 공유 문서 링크, 참여자 역할, 미해결 이슈, 기술 스택
  출력: 구조화된 컨텍스트 문서"
)
```

**Step 4: 컨텍스트 파일 생성**
`.omc/slack-context/<채널ID>.md` 생성 (프로젝트 개요, 핵심 결정사항, 관련 문서, 기술 스택, 미해결 이슈, 원본 메시지)

**Step 5: 메인 워크플로우 실행**
- 생성된 컨텍스트 파일을 Read하여 Ralplan에 전달

---

## `--gmail` 옵션 워크플로우

Gmail 메일을 분석하여 프로젝트 컨텍스트로 활용합니다.

**사용 형식:**
```bash
/auto --gmail                           # 안 읽은 메일 분석
/auto --gmail "검색어"                   # Gmail 검색 쿼리로 필터링
/auto --gmail "작업 설명"                # 메일 기반 작업 실행
/auto --gmail "from:client" "응답 초안"  # 검색 + 작업 조합
```

**Step 1: 인증 확인 (MANDATORY)**
```bash
cd C:\claude && python -m lib.gmail status --json
```

**Step 2: 메일 수집**

| 입력 패턴 | 실행 명령 |
|----------|----------|
| `--gmail` (검색어 없음) | `python -m lib.gmail unread --limit 20 --json` |
| `--gmail "from:..."` | `python -m lib.gmail search "from:..." --limit 20 --json` |
| `--gmail "subject:..."` | `python -m lib.gmail search "subject:..." --limit 20 --json` |
| `--gmail "newer_than:7d"` | `python -m lib.gmail search "newer_than:7d" --limit 20 --json` |

**Gmail 검색 쿼리 문법:**

| 조건 | 예시 |
|------|------|
| 발신자 | `from:boss@company.com` |
| 제목 | `subject:meeting` |
| 최근 N일 | `newer_than:7d` |
| 첨부파일 | `has:attachment` |
| 안 읽음 | `is:unread` |
| 라벨 | `label:work` |

**Step 3: 메일 분석 (Analyst Agent)**
```
Task(
  subagent_type="oh-my-claudecode:analyst",
  model="opus",
  prompt="GMAIL ANALYSIS
  분석 항목: 요청사항/할일 추출, 발신자 우선순위, 회신 필요 메일, 첨부파일, 키워드 연관성, 리스크
  출력: 구조화된 이메일 분석 문서 (마크다운)"
)
```

**Step 4: 컨텍스트 파일 생성**
`.omc/gmail-context/<timestamp>.md` 생성 (요약, 긴급 회신, 할일 추출, 메일 목록, 첨부파일, 관련 링크)

**Step 5: 후속 작업 분기**

| 사용자 요청 | 실행 |
|------------|------|
| 검색만 | 분석 결과 출력 후 종료 |
| "응답 초안" | 각 메일에 대한 회신 초안 생성 |
| "할일 생성" | TaskCreate로 TODO 항목 생성 |
| "요약 전송" | 분석 결과를 이메일로 전송 |
| 구체적 작업 | 메인 워크플로우 실행 (메일 컨텍스트 포함) |

---

## `--interactive` 옵션 워크플로우

각 PDCA Phase 전환 시 사용자에게 확인을 요청하여 단계적 승인을 받습니다.

**사용 형식:**
```bash
/auto --interactive "작업 설명"        # 모든 Phase에서 승인 요청
/auto --interactive --skip-plan "작업"  # Plan 건너뛰고 Design부터 시작
```

| Phase 전환 | 선택지 | 기본값 |
|-----------|--------|:------:|
| Plan 완료 -> Design | 진행 / 수정 / 건너뛰기 | 진행 |
| Design 완료 -> Do | 진행 / 수정 / 건너뛰기 | 진행 |
| Do 완료 -> Check | 진행 / 수정 | 진행 |
| Check 결과 -> Act | 자동 개선 / 수동 수정 / 완료 | 자동 개선 |

**Phase 전환 시 출력 형식:**
```
===================================================
 Phase [현재] 완료 -> Phase [다음] 진입 대기
===================================================
 산출물: docs/01-plan/{feature}.plan.md
 소요 에이전트: planner (opus), critic (opus)
 핵심 결정: [1줄 요약]
===================================================
```

**--interactive 미사용 시** (기본 동작): 모든 Phase를 자동으로 진행합니다.

---

## Phase 4: /work --loop 통합 (장기 계획)

> **상태**: 설계 완료, 구현 예정 (2026-03 목표)

`/work --loop`의 자율 반복 기능을 `/auto --work`로 흡수합니다.

**통합 매핑:**

| 기존 | 신규 | 동작 |
|------|------|------|
| `/work --loop` | `/auto --work` | PDCA 없이 빠른 자율 반복 실행 |
| `/work "작업"` | `/work "작업"` | 단일 작업 실행 (변경 없음) |

**`/auto --work` 모드:**
- PDCA 문서화 생략 (빠른 실행)
- Ralplan 대신 단순 Planner 호출
- Ralph 루프 5개 조건 검증 유지
- Context 90% 임계값 관리 유지

**마이그레이션:**
1. `/work --loop` 사용 시 `/auto --work`로 자동 redirect
2. 기존 /work 커맨드는 단일 작업 실행으로 역할 유지
3. `.claude/rules/08-skill-routing.md` 인과관계 그래프 업데이트
