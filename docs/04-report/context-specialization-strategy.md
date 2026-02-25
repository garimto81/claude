# 컨텍스트 전문화 전략: 워크플로우 범용성 페널티 해소

> **기반 논문**: "Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"
> (arxiv:2602.11988, Gloaguen et al., ETH Zurich, 2026-02-12)
> **분석 대상**: 현재 Claude Code 워크플로우 (42 에이전트, 37 스킬, CLAUDE.md x2 + 규칙 6개)

---

## 1. 논문 핵심 발견사항

| 지표 | LLM 생성 Context | 개발자 작성 Context |
|------|:----------------:|:-------------------:|
| 성능 변화 | **-2~3%** (저하) | **+4%** (미미한 향상) |
| 비용 증가 | **+20~23%** | **+19%** |
| 추가 단계 수 | +2.45~3.92 단계 | — |
| 문서 제거 효과 | **+2.7%** 향상 | — |

### 핵심 인사이트

```
"Context files cause agents to follow instructions faithfully,
 but this faithfulness does not translate to performance gains."
```

1. **지시사항 준수의 역설**: 에이전트는 context 파일을 충실히 따름 (uv 언급 시 1.6배 사용)
   → 그러나 그 준수가 오히려 불필요한 탐색과 비용을 유발
2. **정보 중복이 주범**: 기존 README와 중복되는 context → 제거 시 +2.7% 성능 향상
3. **최적 원칙**: "최소 요구사항만, 모든 세션에 보편적으로 적용 가능한 지시사항만"
4. **토큰 한계**: 최전선 모델은 ~150~200개 지시사항 처리 가능 (더 작은 모델은 더 적음)

---

## 2. 현재 워크플로우 범용성 페널티 진단

### 2.1 컨텍스트 부하 현황

```
세션 시작 시 항상 로드되는 컨텍스트:

+------------------------------------------+-----------+
| 파일                                     | 줄 수      |
+------------------------------------------+-----------+
| ~/.claude/CLAUDE.md (글로벌 지침)         | 165줄      |
| C:\claude\CLAUDE.md (프로젝트 지침)       | 171줄      |
| .claude/rules/04-tdd.md                  | ~30줄      |
| .claude/rules/08-skill-routing.md        | ~50줄      |
| .claude/rules/10-image-analysis.md       | ~60줄      |
| .claude/rules/11-ascii-diagram.md        | ~80줄      |
| .claude/rules/12-large-document.md       | ~70줄      |
| .claude/rules/13-requirements-prd.md     | ~80줄      |
+------------------------------------------+-----------+
| 소계: 항상 로드                           | ~706줄     |
+------------------------------------------+-----------+
| /auto 실행 시 추가 로드 (SKILL.md)        | 426줄      |
| 시스템 프롬프트 내 에이전트 정의 (42개)     | ~500줄 추정  |
+------------------------------------------+-----------+
| /auto 실행 기준 총 추정                   | ~1,632줄   |
+------------------------------------------+-----------+
```

**논문 기준 적용**: 현재 컨텍스트 부하는 "최소 요구사항" 기준의 **4~8배** 과적재 상태.

### 2.2 5대 범용성 페널티

#### P-1. 모놀리식 CLAUDE.md 상속 (심각도: ★★★★★)

```
34개 서브 프로젝트가 동일한 CLAUDE.md를 상속:

wsoptv_ott (영상 스트리밍)  ─┐
archive-analyzer (파일 분류) ─┤  동일한 706줄 컨텍스트 로드
investment (투자 관리)      ─┤  → 프로젝트 특성 무관 지시사항 80%
youtuber_chatbot (챗봇)    ─┘

문제: "OCR 자동 실행" 규칙이 investment 프로젝트에도 적용됨
     "PRD-First" 규칙이 단순 스크립트 수정에도 트리거됨
     "Architect 검증 강제" 규칙이 설정 파일 변경에도 적용됨
```

#### P-2. /auto 5단계 PDCA 강제 (심각도: ★★★★★)

```
현재: 모든 작업 → /auto → 5 Phase PDCA
     (Phase 0 → 0.5 → 1 → 2 → 3 → 4 → 5)

실제 필요 예시:
  "git commit 생성"    → 실제 필요: 30초 / 현재 비용: 5분+ (TeamCreate → ... → TeamDelete)
  "변수명 변경"        → 실제 필요: 10초 / 현재 비용: PRD → Plan → Architect 검증
  "README 오타 수정"   → 실제 필요: 5초  / 현재 비용: PRD-First 트리거 가능성

Ambiguity Score가 0.5 미만이면 즉시 실행이지만
  → 그래도 /auto 호출 시 426줄 SKILL.md + TeamCreate 오버헤드
```

#### P-3. 42개 에이전트 전체 활성화 (심각도: ★★★☆☆)

```
현재: 모든 세션에서 42개 에이전트 정의 접근 가능
  → 에이전트 선택 로직이 복잡한 라우팅 계산 수행
  → 특수 에이전트(catalog-engineer, cloud-architect 등)가
     무관한 프로젝트에서 불필요하게 고려됨

catalog-engineer  → WSOPTV 프로젝트에서만 의미 있음
cloud-architect   → automation_hub에서만 필요
scientist-high    → investment/data 프로젝트에서만 사용
```

#### P-4. 규칙 시스템 보편 적용 (심각도: ★★★★☆)

```
현재 보편 적용 규칙 → 실제 필요 범위:

규칙                    | 실제 필요 프로젝트
------------------------+---------------------------
OCR 자동 실행           | archive-analyzer, qwen_hand_analysis만
PRD-First              | 신규 기능 구현에만
Mermaid/ASCII 다이어그램 | 문서화 작업에만
대형 문서 프로토콜       | 300줄+ 문서 생성에만
Playwright E2E          | wsoptv_flutter, webapp에만

→ 보편 적용으로 불필요한 지시사항이 에이전트 행동을 왜곡
```

#### P-5. Hook 시스템 전역 실행 (심각도: ★★★☆☆)

```
현재: 모든 도구 호출에 hook 실행
  tool_validator.py    → 모든 Bash 명령 검증
  branch_guard.py      → 모든 파일 편집 시 브랜치 체크
  post_edit_check.js   → 모든 편집 후 품질 검증

영향:
  단순 설정 파일 편집에도 post_edit_check.js 실행
  빠른 스크립트 작성에도 Architect 검증 압박
  Tool call 실패율 증가 (hook에 의한 차단)
```

---

## 3. 컨텍스트 전문화 전략 (3-Tier Architecture)

### 전략 개요

```
현재 (모놀리식):
  모든 프로젝트 → 동일한 ~1600줄 컨텍스트

제안 (도메인별 전문화):
  MINIMAL  → 단순 스크립트/유틸   → ~200줄 컨텍스트
  STANDARD → 일반 개발 프로젝트   → ~500줄 컨텍스트
  DOMAIN   → 전문 도메인 프로젝트 → ~800줄 + 도메인 특화
```

### 3.1 전략 A: 프로젝트 타입별 CLAUDE.md 슬림화

각 프로젝트 클러스터에 특화된 최소 CLAUDE.md 생성:

```
C:\claude\.claude\profiles\
├── minimal.md        (< 50줄) — 단순 스크립트, 유틸리티
├── web.md           (< 80줄) — React/Next.js 프로젝트
├── data.md          (< 80줄) — 데이터 파이프라인, ETL
├── media.md         (< 80줄) — 영상/스트리밍 (WSOPTV 계열)
├── ops.md           (< 80줄) — 자동화/인프라
└── docs.md          (< 60줄) — 순수 문서화 작업
```

**각 프로필 포함 내용** (논문 권장: "최소 & 보편적"):
- 해당 도메인에서 ALWAYS 필요한 명령어 (빌드, 테스트)
- 특수 도구 지시 (예: media.md에는 FFmpeg 패턴)
- 해당 도메인 에이전트 목록 (5개 이하)

**제거 대상** (논문 발견: "중복 정보 제거 시 +2.7% 성능"):
- 디렉토리 구조 설명 (Claude가 직접 탐색 가능)
- 다른 문서(AGENTS_REFERENCE.md)와 중복되는 내용
- 해당 프로젝트와 무관한 규칙

### 3.2 전략 B: 도메인별 마이크로 스킬

```
현재 /auto (426줄 SKILL.md, 5 Phase, 42 에이전트):
  /auto "텍스트 변경" → 426줄 로드 + TeamCreate + 5Phase → TeamDelete

제안: 태스크 유형별 분리 스킬

+------------------+----------+--------+-------------------+
| 스킬             | 대상 태스크 | 라인수  | 에이전트 수        |
+------------------+----------+--------+-------------------+
| /quick           | ≤10줄 변경 | <30줄  | 0 (직접 실행)     |
| /fix             | 단일 버그 | <60줄  | 1 (executor)      |
| /auto-web        | 프론트엔드 | <150줄 | 5 (web 특화)      |
| /auto-data       | 데이터 파이프 | <150줄 | 5 (data 특화)  |
| /auto-media      | 영상 처리 | <150줄 | 5 (media 특화)    |
| /auto-ops        | 인프라/자동화 | <150줄 | 5 (ops 특화)   |
| /auto            | 범용 복잡 작업 | 현행    | 풀 42 에이전트    |
+------------------+----------+--------+-------------------+
```

#### /quick 스킬 설계 (신규)

```markdown
# /quick — 즉시 실행 (10줄 이하 변경, 팀 생성 없음)

트리거: 명확한 단일 파일 변경, 오타 수정, 변수명 변경

실행:
1. 파일 읽기 → 직접 Edit → 완료
2. PRD-First 스킵 (--skip-prd 자동 적용)
3. Architect 검증 스킵 (단순 변경)
4. Hook 적용 (branch_guard만)

금지: 10줄 초과 변경, 신규 파일 생성, 다중 파일 변경
```

#### /auto-media 스킬 설계 (WSOPTV 특화, 신규)

```markdown
# /auto-media — 영상/스트리밍 워크플로우

컨텍스트: WSOPTV, Vimeo OTT, 쇼츠 생성 프로젝트
에이전트: executor, catalog-engineer, qa-tester, code-reviewer
Phase: 3-Phase (Plan → Implement → Verify)
기본 제외: Playwright E2E, PRD-First (미디어 작업의 경우)
기본 포함: FFmpeg 패턴, Vimeo API 사용법, 쇼츠 파이프라인
```

### 3.3 전략 C: 동적 컨텍스트 프로파일링

세션 시작 시 프로젝트 타입을 자동 감지하여 최적 컨텍스트 로드:

```python
# session_init.py 확장 (개념적 설계)

def detect_project_type(cwd: str) -> str:
    markers = {
        "media":  ["ffmpeg", "vimeo", "wsoptv", "shorts"],
        "web":    ["package.json", "next.config", "tailwind"],
        "data":   ["pandas", "pyspark", "etl", "pipeline"],
        "ops":    ["docker", "terraform", "github/workflows"],
        "docs":   [".md only", "no src/"],
    }
    # cwd 파일 탐색으로 타입 결정
    return detected_type

def load_context(project_type: str) -> str:
    profiles = {
        "media":   "~/.claude/profiles/media.md",
        "web":     "~/.claude/profiles/web.md",
        ...
        "default": "~/.claude/CLAUDE.md"
    }
    return profiles.get(project_type, "default")
```

**효과**: 34개 서브 프로젝트가 각각 최적화된 컨텍스트만 로드
- wsoptv_ott → media.md (80줄, FFmpeg/Vimeo 특화)
- investment → data.md (80줄, 분석 특화)
- archive-analyzer → data.md + OCR 규칙만

### 3.4 전략 D: 규칙 선택적 활성화

```
현재: 6개 규칙 파일 항상 로드 (~370줄)
제안: 규칙을 태그로 분류, 프로젝트 타입별 선택 로드

규칙 태그 시스템:
  [ALL]    → 모든 프로젝트 (branch_guard, 언어 설정만)
  [DEV]    → 개발 프로젝트 (TDD, PRD-First)
  [MEDIA]  → 미디어 프로젝트 (OCR)
  [DOCS]   → 문서 작업 (대형 문서 프로토콜, ASCII 다이어그램)
  [INFRA]  → 인프라 (Playwright E2E)

효과: MINIMAL 프로젝트는 [ALL] 규칙만 → ~30줄
     개발 프로젝트는 [ALL]+[DEV] → ~130줄
```

---

## 4. 파편화된 프로젝트 컨텍스트 오염 최소화 전략

### 4.1 프로젝트 클러스터 매핑

```
현재 34개 서브 프로젝트 → 6개 클러스터

MEDIA 클러스터 (media.md):
  wsoptv_ott, wsoptv_mvp, wsoptv_flutter, wsoptv_nbatv,
  vimeo_ott, archive-analyzer, shorts-generator, airi

WEB 클러스터 (web.md):
  wsoptv_flutter (Flutter), webtoon_remaster, kanban_board,
  project-showcase-hub, youtuber, youtuber_chatbot

DATA 클러스터 (data.md):
  automation_hub, automation_ae, automation_aep_csv,
  automation_dashboard, investment, gg_ecosystem

OPS 클러스터 (ops.md):
  automation_orchestration, automation_sub, automation_schema,
  ebs, ebs_reverse, mad_framework

SIMPLE 클러스터 (minimal.md):
  secretary, scripts, ceo, todo 관련 유틸리티

DOCS 클러스터 (docs.md):
  claude-auto-continue, README 전용 레포
```

### 4.2 프로젝트별 .claude/profile.yaml 도입

```yaml
# wsoptv_ott/.claude/profile.yaml (예시)
type: media
complexity_cap: STANDARD  # HEAVY 진입 차단
agents:
  - executor
  - catalog-engineer
  - qa-tester
  - code-reviewer
skip_rules:
  - prd-first       # 미디어 스크립트는 PRD 불필요
  - playwright-e2e  # 미디어 작업은 E2E 다름
active_rules:
  - ocr             # OCR은 이 프로젝트에서 핵심
  - tdd             # TDD는 유지
context_budget: 800  # 최대 토큰
```

```yaml
# investment/.claude/profile.yaml (예시)
type: data
complexity_cap: HEAVY
agents:
  - executor
  - scientist-high
  - data-specialist
  - code-reviewer
skip_rules:
  - ocr             # OCR 불필요
  - playwright-e2e  # E2E 불필요
active_rules:
  - tdd
  - prd-first
context_budget: 1200
```

### 4.3 에이전트 Lazy Loading 전략

```
현재: 42개 에이전트 항상 시스템 프롬프트에 존재
     → 모든 결정에서 42개 에이전트 선택 로직 실행

제안: 2단계 에이전트 로딩

Step 1: 5개 핵심 에이전트만 기본 활성화
  - executor, architect, qa-tester, code-reviewer, writer

Step 2: 도메인별 추가 에이전트 (필요 시 활성화)
  - media: catalog-engineer, vision
  - data: scientist-high, data-specialist
  - web: designer, frontend-dev
  - ops: devops-engineer, cloud-architect

효과:
  - 에이전트 선택 계산 80% 감소
  - 불필요한 특수 에이전트 참조 제거
  - 더 명확한 위임 결정
```

---

## 5. 구체적 구현 로드맵

### Phase 1 (즉시, 1주): 긴급 슬림화

1. **글로벌 CLAUDE.md 축소**
   - 현재 165줄 → 목표 80줄 이하
   - 제거: 복잡한 라우팅 테이블, 중복 설명
   - 유지: 핵심 5 규칙 (DELEGATION-FIRST, 언어, 경로, Git)

2. **/auto SKILL.md 분리**
   - 426줄 SKILL.md → 핵심 100줄 + REFERENCE.md (상세)
   - REFERENCE.md는 필요 시에만 참조

3. **프로젝트 CLAUDE.md 최소화**
   - 현재 171줄 → 80줄 이하
   - 제거: 상세 아키텍처 설명 (코드베이스에 이미 존재)

### Phase 2 (2~4주): 도메인 프로파일링

1. **6개 프로필 파일 작성** (`~/.claude/profiles/`)
2. **상위 5개 프로젝트에 profile.yaml 적용**
   - wsoptv_ott, automation_hub, archive-analyzer, investment, youtuber
3. **session_init.py 프로파일 감지 로직 추가**

### Phase 3 (1~2개월): 마이크로 스킬 구현

1. **/quick 스킬 구현** (즉시 실행, 팀 없음)
2. **/auto-media 스킬 구현** (WSOPTV 특화)
3. **/auto-data 스킬 구현** (데이터 파이프라인 특화)
4. **에이전트 기본 5개 → Lazy Loading 전환**

---

## 6. 예상 효과

| 지표 | 현재 | Phase 1 후 | Phase 3 후 |
|------|:----:|:----------:|:----------:|
| 항상 로드 컨텍스트 | ~706줄 | ~350줄 (-50%) | ~200줄 (-72%) |
| /auto 실행 비용 | ~1632줄 | ~900줄 (-45%) | 작업별 최적화 |
| 단순 작업 오버헤드 | 5분+ | 2분 | 30초 (/quick) |
| 에이전트 선택 복잡도 | 42개 | 42개 | 5+도메인별 |
| 프로젝트 컨텍스트 오염 | 80% | 50% | 10% |

논문 기준 예상 성능 향상: **+4~7%** (비용 중복 제거 효과)
논문 기준 예상 비용 절감: **-20~35%** (컨텍스트 토큰 감소)

---

## 7. 주의사항 및 트레이드오프

### 유의사항
- **일관성 vs 전문성**: 도메인별 분리는 유지보수 복잡도 증가
  → 해결: 공통 베이스 프로필 + 도메인 덮어쓰기 패턴
- **발견 가능성**: 에이전트 줄이면 특수 에이전트 놓칠 수 있음
  → 해결: `/list-agents <domain>` 커맨드로 항상 발견 가능
- **Phase 1 위험성**: 너무 빠른 축소 시 기존 동작 깨짐
  → 해결: A/B 테스트 (새 CLAUDE.md vs 기존) 1주 운영

### 핵심 설계 원칙 (논문에서 도출)
1. **CLAUDE.md에 넣지 말아야 할 것**: 코드베이스 구조, README와 중복, 상황별 규칙
2. **넣어야 할 것**: 특수 도구 명령, 해당 프로젝트에만 있는 규약, 에이전트가 발견하기 어려운 정보
3. **황금 규칙**: "에이전트가 없어도 파일/코드 탐색으로 알 수 있다면 → 제거"

---

## 참고 자료

- [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) — Gloaguen et al. (2026)
- [On the Impact of AGENTS.md Files](https://arxiv.org/html/2601.20404v1) — 유사 연구
- [Context Engineering for Multi-Agent LLM](https://arxiv.org/pdf/2508.08322) — 컨텍스트 엔지니어링
- [Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — 실무 가이드
- [Agent READMEs: Empirical Study](https://arxiv.org/html/2511.12884v1) — 경험적 연구

---

*생성일: 2026-02-25 | 브랜치: feat/prd-chunking-strategy | 담당: Claude Code Orchestrator*
