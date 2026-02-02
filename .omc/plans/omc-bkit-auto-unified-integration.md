# OMC + BKIT + /auto 3자 통합 전략 (Unified Absorption Integration)

**Plan ID**: omc-bkit-auto-unified-integration
**Version**: 3.1.0
**Created**: 2026-02-02
**Status**: ✅ APPROVED (Critic OKAY - 2026-02-02)
**Critic Feedback Applied**: BKIT 에이전트 호출 방식, 43 에이전트 매핑, gap-detector 임계값, Phase 의존성, 롤백 전략
**Previous Plans**:
- `omc-auto-absorption-integration.md` (v2.1.0 - 2자 통합)
- `omc-bkit-integration.md` (v1.1.0 - 잘못된 BKIT 이해)

---

## Executive Summary

**새로운 발견**: BKIT는 "OMC 패키지"가 아니라 **popup-studio-ai가 개발한 독립 플러그인**입니다.

| 시스템 | 개발자 | 핵심 철학 | 강점 |
|--------|--------|----------|------|
| **OMC** | garimto81 | Multi-Agent 병렬 실행 | 빠른 자율 실행 (32 에이전트) |
| **BKIT** | popup-studio-ai | PDCA 문서화 방법론 | 체계적 문서화 + 검증 |
| **/auto** | 로컬 (garimto81) | 5계층 Discovery + 통합 | 단일 진입점 + Context 관리 |

**3자 통합 목표**: 각 시스템의 **최선의 기능을 흡수**하여 /auto를 완벽한 단일 진입점으로 만듦

**핵심 원칙:**
- **OMC 흡수**: 32 에이전트, Ralplan, Ultrawork, Ralph (실행력)
- **BKIT 흡수**: PDCA 문서화, gap-detector, 프로젝트 레벨 감지 (체계성)
- **/auto 강화**: 5계층 Discovery, Context 예측, 옵션 체이닝 (통합)

---

## 3자 기능 비교 분석

### 전체 기능 매핑

| 기능 영역 | OMC | BKIT | /auto | 최선 선택 | 흡수 방법 |
|-----------|:---:|:----:|:-----:|-----------|----------|
| **에이전트 수** | 32개 | 11개 | 0개 (위임) | **OMC** | 에이전트 테이블 통합 |
| **병렬 실행** | Ultrawork | 없음 | 없음 | **OMC** | parallel_executor.py |
| **계획 합의** | Ralplan | 없음 | Phase Gate | **OMC** | ralplan_engine.py |
| **완료 루프** | Ralph 5조건 | PDCA iterate | 없음 | **둘 다** | 통합 루프 |
| **문서화** | 선택적 | **필수** (PDCA) | 없음 | **BKIT** | --pdca 옵션 |
| **설계-구현 검증** | Architect | **gap-detector** | 없음 | **BKIT** | 검증 단계 추가 |
| **프로젝트 레벨** | 없음 | **3단계** | 없음 | **BKIT** | 자동 감지 |
| **자율 발견** | 패턴 감지 | 없음 | **5계층** | **/auto** | 기존 유지 |
| **Context 관리** | 기본 | 기본 | **예측 시스템** | **/auto** | 기존 유지 |
| **옵션 체이닝** | 없음 | 없음 | **--gdocs 등** | **/auto** | 확장 (--pdca) |
| **코드 리뷰** | code-reviewer | code-review | 없음 | **둘 다** | 통합 |
| **QA** | ultraqa | zero-script-qa | 없음 | **둘 다** | 통합 |

### 흡수 결정 요약

| 출처 | 흡수할 기능 | 우선순위 |
|------|------------|:--------:|
| **OMC** | 32 에이전트, Ralplan, Ultrawork, Ralph | P0 |
| **BKIT** | PDCA 문서화, gap-detector, 프로젝트 레벨 | P1 |
| **/auto** | 5계층 Discovery, Context 예측, 옵션 체이닝 | P0 (기존 유지) |

---

## CRITICAL: BKIT 에이전트 호출 방식 (Critic 피드백 반영)

### 확인된 사실

1. **BKIT 에이전트는 Task tool에서 직접 호출 가능**
   - prefix: `bkit:{agent-name}`
   - 예: `Task(subagent_type="bkit:gap-detector", ...)`

2. **BKIT 에이전트 11개 전체 목록** (확인됨)

| # | 에이전트 | 파일 경로 | model | 역할 |
|---|----------|----------|-------|------|
| 1 | `bkit:starter-guide` | `agents/starter-guide.md` | sonnet | 초보자 가이드 |
| 2 | `bkit:bkend-expert` | `agents/bkend-expert.md` | sonnet | BaaS 전문가 |
| 3 | `bkit:enterprise-expert` | `agents/enterprise-expert.md` | opus | 엔터프라이즈 전문가 |
| 4 | `bkit:infra-architect` | `agents/infra-architect.md` | opus | 인프라 아키텍트 |
| 5 | `bkit:pipeline-guide` | `agents/pipeline-guide.md` | sonnet | 파이프라인 가이드 |
| 6 | `bkit:gap-detector` | `agents/gap-detector.md` | **opus** | 설계-구현 갭 분석 |
| 7 | `bkit:design-validator` | `agents/design-validator.md` | sonnet | 설계 문서 검증 |
| 8 | `bkit:code-analyzer` | `agents/code-analyzer.md` | sonnet | 코드 품질 분석 |
| 9 | `bkit:qa-monitor` | `agents/qa-monitor.md` | sonnet | QA 모니터링 |
| 10 | `bkit:pdca-iterator` | `agents/pdca-iterator.md` | **sonnet** | Check-Act 반복 개선 |
| 11 | `bkit:report-generator` | `agents/report-generator.md` | haiku | 완료 보고서 생성 |

### 호출 방식 명세

```python
# BKIT 에이전트 호출 예시
result = await Task(
    subagent_type="bkit:gap-detector",  # bkit: prefix 사용
    model="opus",                        # 에이전트 정의 model과 일치
    prompt="""
    ## 설계 문서
    {design_doc_content}

    ## 구현 코드
    {implementation_content}

    ## 분석 요청
    설계-구현 일치도를 분석하고 Match Rate를 반환하세요.
    """
)
```

### OMC vs BKIT 에이전트 호출 prefix

| 시스템 | prefix | 예시 |
|--------|--------|------|
| OMC | `oh-my-claudecode:` | `oh-my-claudecode:architect` |
| BKIT | `bkit:` | `bkit:gap-detector` |

---

## CRITICAL: 43 에이전트 완전 매핑 테이블 (Critic 피드백 반영)

### OMC 에이전트 (32개)

| # | 에이전트 | Model | Domain | 용도 |
|---|----------|-------|--------|------|
| 1 | `oh-my-claudecode:architect-low` | haiku | analysis | 간단한 구조 분석 |
| 2 | `oh-my-claudecode:architect-medium` | sonnet | analysis | 중간 규모 설계 |
| 3 | `oh-my-claudecode:architect` | opus | analysis | 복잡한 아키텍처 |
| 4 | `oh-my-claudecode:executor-low` | haiku | execution | 단순 코드 변경 |
| 5 | `oh-my-claudecode:executor` | sonnet | execution | 기능 구현 |
| 6 | `oh-my-claudecode:executor-high` | opus | execution | 복잡한 리팩토링 |
| 7 | `oh-my-claudecode:explore` | haiku | search | 기본 코드베이스 탐색 |
| 8 | `oh-my-claudecode:explore-medium` | sonnet | search | 상세 코드 탐색 |
| 9 | `oh-my-claudecode:explore-high` | opus | search | 심층 코드 분석 |
| 10 | `oh-my-claudecode:researcher-low` | haiku | research | 빠른 문서 조회 |
| 11 | `oh-my-claudecode:researcher` | sonnet | research | 리서치 |
| 12 | `oh-my-claudecode:designer-low` | haiku | frontend | 간단한 UI 수정 |
| 13 | `oh-my-claudecode:designer` | sonnet | frontend | UI 컴포넌트 |
| 14 | `oh-my-claudecode:designer-high` | opus | frontend | 디자인 시스템 |
| 15 | `oh-my-claudecode:writer` | haiku | docs | 문서 작성 |
| 16 | `oh-my-claudecode:vision` | sonnet | visual | 이미지/다이어그램 분석 |
| 17 | `oh-my-claudecode:planner` | opus | planning | 전략적 계획 |
| 18 | `oh-my-claudecode:critic` | opus | planning | 계획 비평 |
| 19 | `oh-my-claudecode:analyst` | opus | planning | 사전 분석 |
| 20 | `oh-my-claudecode:qa-tester` | sonnet | testing | 테스트 실행 |
| 21 | `oh-my-claudecode:qa-tester-high` | opus | testing | 복잡한 테스트 |
| 22 | `oh-my-claudecode:security-reviewer-low` | haiku | security | 빠른 보안 스캔 |
| 23 | `oh-my-claudecode:security-reviewer` | opus | security | 심층 보안 분석 |
| 24 | `oh-my-claudecode:build-fixer-low` | haiku | build | 단순 빌드 오류 |
| 25 | `oh-my-claudecode:build-fixer` | sonnet | build | 빌드 오류 수정 |
| 26 | `oh-my-claudecode:tdd-guide-low` | haiku | tdd | 기본 테스트 제안 |
| 27 | `oh-my-claudecode:tdd-guide` | sonnet | tdd | TDD 워크플로우 |
| 28 | `oh-my-claudecode:code-reviewer-low` | haiku | review | 빠른 코드 검토 |
| 29 | `oh-my-claudecode:code-reviewer` | opus | review | 상세 코드 리뷰 |
| 30 | `oh-my-claudecode:scientist-low` | haiku | data | 간단한 데이터 확인 |
| 31 | `oh-my-claudecode:scientist` | sonnet | data | 데이터 분석 |
| 32 | `oh-my-claudecode:scientist-high` | opus | data | ML/통계 분석 |

### BKIT 에이전트 (11개)

| # | 에이전트 | Model | Domain | 용도 |
|---|----------|-------|--------|------|
| 33 | `bkit:starter-guide` | sonnet | guide | 초보자 가이드 |
| 34 | `bkit:bkend-expert` | sonnet | backend | BaaS 전문가 |
| 35 | `bkit:enterprise-expert` | opus | enterprise | 엔터프라이즈 전문가 |
| 36 | `bkit:infra-architect` | opus | infra | 인프라 아키텍트 |
| 37 | `bkit:pipeline-guide` | sonnet | pipeline | 파이프라인 가이드 |
| 38 | `bkit:gap-detector` | opus | verification | 설계-구현 갭 분석 |
| 39 | `bkit:design-validator` | sonnet | verification | 설계 문서 검증 |
| 40 | `bkit:code-analyzer` | sonnet | review | 코드 품질 분석 |
| 41 | `bkit:qa-monitor` | sonnet | testing | QA 모니터링 |
| 42 | `bkit:pdca-iterator` | sonnet | improvement | Check-Act 반복 개선 |
| 43 | `bkit:report-generator` | haiku | docs | 완료 보고서 생성 |

---

## CRITICAL: gap-detector 임계값 설정 (Critic 피드백 반영)

### BKIT 원본 기준 (gap-detector.md에서 확인)

| Match Rate | 판정 | 권장 조치 |
|:----------:|------|----------|
| < 70% | **FAIL** | 설계-구현 동기화 필수 |
| 70% ~ 89% | **WARN** | 문서 업데이트 권장 |
| ≥ 90% | **PASS** | 잘 일치함 |

### /auto 통합 시 적용 방식

```python
# 기본값: BKIT 원본 그대로 적용
GAP_DETECTOR_THRESHOLDS = {
    "PASS": 90,   # 이상이면 통과
    "WARN": 70,   # 이상이면 경고
    "FAIL": 0,    # 미만이면 실패
}

# 임계값 조정 방법 (3가지)
# 1. CLI 옵션
/auto --pdca --gap-threshold 85 "기능 구현"

# 2. 환경 변수
GAP_DETECTOR_PASS_THRESHOLD=85

# 3. 설정 파일 (.omc/config.json)
{
  "gap_detector": {
    "pass_threshold": 90,
    "warn_threshold": 70
  }
}
```

### 임계값 조정 근거

| 상황 | 권장 임계값 | 이유 |
|------|:----------:|------|
| **MVP/프로토타입** | 70% | 빠른 개발 우선 |
| **일반 프로젝트** | 85% | 균형 |
| **엔터프라이즈** | 95% | 높은 품질 요구 |
| **규제 산업** | 98% | 컴플라이언스 필수 |

---

## 통합 아키텍처

### 목표 구조

```
+===================================================================+
|                    /auto (Unified Master System)                  |
|              8,211줄 → ~13,000줄로 확장 (3자 통합)                  |
+===================================================================+
|                                                                    |
|  +-- Layer 1: CLI & Entry ----------------------------------------+
|  |   auto_cli.py (257줄)                                          |
|  |     + --pdca 옵션 추가                                          |
|  |     + --level 옵션 추가 (starter/dynamic/enterprise)            |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 2: Project Level Detection (BKIT 흡수) ----------------+
|  |   NEW: project_detector.py (~200줄)                             |
|  |     + Starter: HTML/CSS/정적 사이트                              |
|  |     + Dynamic: Fullstack + DB + Auth                            |
|  |     + Enterprise: K8s + MSA + Terraform                         |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 3: Orchestration (OMC 흡수) ---------------------------+
|  |   auto_orchestrator.py (1,065줄 → ~1,800줄)                     |
|  |     + Ultrawork 병렬 실행 로직                                   |
|  |     + Ralph 5조건 루프 통합                                      |
|  |     + PDCA 문서화 트리거                                         |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 4: Discovery (/auto 고유) -----------------------------+
|  |   auto_discovery.py (1,262줄) - 변경 없음                       |
|  |   5계층 우선순위 발견 시스템                                     |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 5: Planning (OMC + BKIT 통합) -------------------------+
|  |   phase_gate.py (559줄 → ~900줄)                                |
|  |     + Ralplan 3자 합의 루프                                      |
|  |     + PDCA Phase 통합 (Plan→Design→Do→Check→Act)                |
|  |                                                                 |
|  |   NEW: ralplan_engine.py (~300줄)                               |
|  |     + Planner → Architect → Critic 사이클                       |
|  |                                                                 |
|  |   NEW: pdca_engine.py (~400줄) [BKIT 흡수]                      |
|  |     + Plan: docs/01-plan/ 자동 생성                             |
|  |     + Design: docs/02-design/ 자동 생성                         |
|  |     + Check: gap-detector 검증                                  |
|  |     + Act: pdca-iterator 반복 개선                               |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 6: State & Context (/auto 고유) -----------------------+
|  |   auto_state.py (569줄) - 변경 없음                             |
|  |   unified_state.py (327줄) - 변경 없음                          |
|  |   context_manager.py (1,786줄) - 변경 없음                      |
|  |   context_predictor.py (197줄) - 변경 없음                      |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 7: Agent System (OMC + BKIT 통합) ---------------------+
|  |   omc_bridge.py (152줄 → ~500줄)                                |
|  |     + OMC 32 에이전트 완전 테이블                                |
|  |     + BKIT 11 에이전트 매핑 추가                                 |
|  |     + 티어 기반 자동 선택 로직                                   |
|  |                                                                 |
|  |   model_router.py (658줄) - 기존 유지                           |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 8: Verification (OMC + BKIT 통합) ---------------------+
|  |   verification.py (214줄 → ~500줄)                              |
|  |     + OMC Mandatory Architect Verification                      |
|  |     + BKIT gap-detector 통합 (설계-구현 90% 일치 검증)           |
|  |     + Ralph 5조건 + PDCA Check 통합                             |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 9: Documentation (BKIT 흡수) --------------------------+
|  |   NEW: pdca_docs.py (~300줄)                                    |
|  |     + docs/01-plan/*.plan.md 생성                               |
|  |     + docs/02-design/*.design.md 생성                           |
|  |     + docs/03-analysis/*.analysis.md 생성                       |
|  |     + docs/04-report/*.report.md 생성                           |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 10: Parallel Execution (OMC 흡수) ---------------------+
|  |   NEW: parallel_executor.py (~500줄)                            |
|  |     + 독립 작업 병렬 실행                                        |
|  |     + 파일 소유권 관리                                           |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 11: Loop Control (OMC + BKIT 통합) --------------------+
|  |   loop_control.py (273줄 → ~500줄)                              |
|  |     + Ralph 5조건 완료 판정                                      |
|  |     + PDCA Check-Act 반복 (90% 일치까지)                        |
|  +----------------------------------------------------------------+
|                                                                    |
|  +-- Layer 12: Logging -------------------------------------------+
|  |   auto_logger.py (293줄) - 변경 없음                            |
|  +----------------------------------------------------------------+
|                                                                    |
+===================================================================+
```

### 파일 변경 요약

| 파일 | 현재 | 예상 | 변경 내용 | 출처 |
|------|------|------|----------|------|
| `auto_cli.py` | 257 | ~300 | --pdca, --level 옵션 | BKIT |
| `auto_orchestrator.py` | 1,065 | ~1,800 | Ultrawork, Ralph, PDCA 트리거 | OMC+BKIT |
| `phase_gate.py` | 559 | ~900 | Ralplan + PDCA Phase | OMC+BKIT |
| `omc_bridge.py` | 152 | ~500 | 32+11 에이전트 테이블 | OMC+BKIT |
| `verification.py` | 214 | ~500 | Architect + gap-detector | OMC+BKIT |
| `loop_control.py` | 273 | ~500 | Ralph 5조건 + PDCA iterate | OMC+BKIT |
| **NEW** `project_detector.py` | 0 | ~200 | 프로젝트 레벨 감지 | BKIT |
| **NEW** `ralplan_engine.py` | 0 | ~300 | Ralplan 엔진 | OMC |
| **NEW** `pdca_engine.py` | 0 | ~400 | PDCA 사이클 엔진 | BKIT |
| **NEW** `pdca_docs.py` | 0 | ~300 | PDCA 문서 생성 | BKIT |
| **NEW** `parallel_executor.py` | 0 | ~500 | Ultrawork 구현 | OMC |
| **총 변경** | 8,211 | ~13,000 | +4,789줄 (58% 증가) | |

---

## 상세 흡수 작업

### Phase 1: OMC 패턴 흡수 (Week 1-2)

#### Task 1.1: Ralph 5조건 (loop_control.py)

**흡수 내용**: OMC의 Ralph 완료 조건

```python
RALPH_COMPLETION_CONDITIONS = {
    "TODO_LIST": "미완료 작업 없음",
    "FUNCTIONALITY": "모든 요청 기능 작동",
    "TESTS": "모든 테스트 통과",
    "ERRORS": "미처리 오류 없음",
    "ARCHITECT": "Architect 검증 통과"
}
```

**Acceptance Criteria**:
- [ ] 5개 조건 개별 체크 함수
- [ ] 전체 조건 통합 검증
- [ ] 실패 시 구체적 이유 반환

#### Task 1.2: Ralplan 3자 합의 (NEW: ralplan_engine.py)

**흡수 내용**: OMC의 Planner → Architect → Critic 루프

```python
class RalplanEngine:
    async def run_consensus_loop(self, task: str) -> RalplanResult:
        while iteration < max_iterations:
            plan = await self._run_planner(task)
            if plan.has_questions:
                answers = await self._consult_architect(plan.questions)
            verdict = await self._run_critic(plan)
            if verdict.is_okay:
                return RalplanResult(approved=True, plan=plan)
            iteration += 1
```

**Acceptance Criteria**:
- [ ] Planner 프롬프트 생성
- [ ] Critic 검증 로직
- [ ] 최대 5회 반복

#### Task 1.3: Ultrawork 병렬 실행 (NEW: parallel_executor.py)

**흡수 내용**: OMC의 병렬 에이전트 실행

```python
class ParallelExecutor:
    async def execute_parallel(self, tasks: List[ParallelTask]) -> List[TaskResult]:
        independent, dependent = self._classify_tasks(tasks)
        # 독립 작업 병렬 실행
        parallel_results = await asyncio.gather(*[...])
        # 의존 작업 순차 실행
        for task in self._topological_sort(dependent):
            result = await self._execute_single(task)
```

**Acceptance Criteria**:
- [ ] 독립/의존 작업 분류
- [ ] asyncio 병렬 실행
- [ ] 파일 소유권 충돌 방지

#### Task 1.4: 43 에이전트 통합 테이블 (omc_bridge.py)

**흡수 내용**: OMC 32개 + BKIT 11개 에이전트

```python
UNIFIED_AGENT_REGISTRY = {
    # OMC 에이전트 (32개)
    "oh-my-claudecode:architect": {"model": "opus", "domain": "analysis"},
    "oh-my-claudecode:executor": {"model": "sonnet", "domain": "execution"},
    # ... 30개 더

    # BKIT 에이전트 (11개)
    "bkit:gap-detector": {"model": "opus", "domain": "verification"},
    "bkit:pdca-iterator": {"model": "sonnet", "domain": "improvement"},
    "bkit:code-analyzer": {"model": "sonnet", "domain": "review"},
    # ... 8개 더
}
```

**Acceptance Criteria**:
- [ ] 43개 에이전트 전체 등록
- [ ] 도메인별 분류
- [ ] 자동 선택 로직

---

### Phase 2: BKIT 패턴 흡수 (Week 3-4)

#### Task 2.1: 프로젝트 레벨 감지 (NEW: project_detector.py)

**흡수 내용**: BKIT의 3단계 프로젝트 레벨 감지

```python
class ProjectDetector:
    def detect_level(self, project_path: str) -> ProjectLevel:
        """프로젝트 복잡도 자동 감지"""
        indicators = self._scan_indicators(project_path)

        if indicators.has_kubernetes or indicators.has_terraform:
            return ProjectLevel.ENTERPRISE
        elif indicators.has_database or indicators.has_auth:
            return ProjectLevel.DYNAMIC
        else:
            return ProjectLevel.STARTER

    def _scan_indicators(self, path: str) -> Indicators:
        return Indicators(
            has_kubernetes="k8s" in files or "kubernetes" in files,
            has_terraform=".tf" in files,
            has_database="prisma" in files or "supabase" in files,
            has_auth="auth" in files or "login" in files,
        )
```

**Acceptance Criteria**:
- [ ] Starter/Dynamic/Enterprise 자동 감지
- [ ] 파일 패턴 기반 분석
- [ ] 레벨별 권장 워크플로우 제안

#### Task 2.2: PDCA 문서화 엔진 (NEW: pdca_engine.py)

**흡수 내용**: BKIT의 PDCA 사이클 + 문서 자동 생성

```python
class PDCAEngine:
    async def run_pdca_cycle(self, feature: str) -> PDCAResult:
        # Plan Phase
        plan_doc = await self._generate_plan(feature)
        self._save_to("docs/01-plan", f"{feature}.plan.md", plan_doc)

        # Design Phase
        design_doc = await self._generate_design(feature, plan_doc)
        self._save_to("docs/02-design", f"{feature}.design.md", design_doc)

        # Do Phase (기존 /auto 워크플로우)
        # ... 구현 실행

        # Check Phase (gap-detector)
        gap_result = await self._run_gap_detector(design_doc, implementation)

        # Act Phase (pdca-iterator)
        if gap_result.match_percentage < 90:
            await self._iterate_until_match(gap_result)

        return PDCAResult(...)
```

**Acceptance Criteria**:
- [ ] Plan 문서 자동 생성
- [ ] Design 문서 자동 생성
- [ ] gap-detector 검증 (90% 일치)
- [ ] pdca-iterator 반복 개선

#### Task 2.3: gap-detector 통합 (verification.py 확장)

**흡수 내용**: BKIT의 설계-구현 일치 검증

```python
class GapDetector:
    async def detect_gaps(self, design_doc: str, implementation: str) -> GapResult:
        """설계 문서와 구현의 일치도 검증"""
        prompt = f"""
        ## 설계 문서
        {design_doc}

        ## 구현 코드
        {implementation}

        ## 검증 항목
        1. 설계에 명시된 기능이 모두 구현되었는가?
        2. 구현이 설계를 정확히 따르는가?
        3. 누락된 기능이 있는가?
        4. 추가된 기능이 있는가?

        ## 출력
        - match_percentage: 0-100
        - gaps: [누락된 항목 목록]
        - extras: [추가된 항목 목록]
        """
        return await self._invoke_agent("bkit:gap-detector", prompt)
```

**Acceptance Criteria**:
- [ ] 설계-구현 일치도 % 계산
- [ ] 누락/추가 항목 식별
- [ ] 90% 미만 시 자동 개선 트리거

#### Task 2.4: --pdca 옵션 추가 (auto_cli.py)

**흡수 내용**: BKIT 스타일 문서화 워크플로우 옵션

```python
# auto_cli.py 확장
parser.add_argument('--pdca', action='store_true',
                    help='PDCA 문서화 모드 활성화')
parser.add_argument('--level', choices=['starter', 'dynamic', 'enterprise'],
                    help='프로젝트 레벨 명시 (자동 감지 override)')
```

**사용 예시**:
```bash
/auto --pdca "로그인 기능 구현"
# → docs/01-plan/login.plan.md 생성
# → docs/02-design/login.design.md 생성
# → 구현 실행
# → gap-detector 검증
# → 90% 일치까지 반복
```

**Acceptance Criteria**:
- [ ] --pdca 옵션 파싱
- [ ] PDCA 엔진 연동
- [ ] 문서 자동 생성

---

### Phase 3: 통합 검증 및 최적화 (Week 5)

#### Task 3.1: 통합 완료 루프 (loop_control.py)

**목표**: Ralph 5조건 + PDCA Check-Act 통합

```python
class UnifiedCompletionChecker:
    async def check_completion(self, state: AutoState) -> CompletionResult:
        # Ralph 5조건
        ralph_result = await self._check_ralph_conditions(state)

        # PDCA Check (--pdca 모드일 때만)
        if state.pdca_enabled:
            pdca_result = await self._check_pdca_match(state)
            return CompletionResult(
                complete=ralph_result.complete and pdca_result.match >= 90,
                ralph=ralph_result,
                pdca=pdca_result
            )

        return CompletionResult(complete=ralph_result.complete, ralph=ralph_result)
```

#### Task 3.2: 통합 테스트

**테스트 케이스**:

| # | 시나리오 | 예상 결과 |
|---|----------|----------|
| 1 | `/auto "기능"` | OMC 스타일 실행 (Ralph + Ultrawork) |
| 2 | `/auto --pdca "기능"` | BKIT 스타일 문서화 + 검증 |
| 3 | `/auto --level enterprise "기능"` | Enterprise 권장 워크플로우 |
| 4 | gap-detector 80% 결과 | 자동 pdca-iterator 실행 |
| 5 | 43 에이전트 호출 | OMC + BKIT 에이전트 모두 동작 |

---

## 옵션 체이닝 확장

### 기존 옵션

| 옵션 | 설명 | 출처 |
|------|------|------|
| `--gdocs` | Google Docs PRD 동기화 | /auto |
| `--mockup` | 목업 생성 | /auto |
| `--debate` | 3AI 토론 | /auto |
| `--research` | 리서치 모드 | /auto |
| `--slack` | Slack 컨텍스트 | /auto |
| `--gmail` | Gmail 컨텍스트 | /auto |

### 신규 옵션 (BKIT 흡수)

| 옵션 | 설명 | 출처 |
|------|------|------|
| `--pdca` | PDCA 문서화 모드 | BKIT |
| `--level <level>` | 프로젝트 레벨 명시 | BKIT |
| `--gap-check` | 설계-구현 검증만 실행 | BKIT |
| `--docs-only` | 문서만 생성 (구현 안 함) | BKIT |

### 옵션 조합 예시

```bash
# PDCA + Google Docs
/auto --gdocs --pdca "PRD 기반 로그인 구현"
# → PRD 동기화 → Plan 문서 → Design 문서 → 구현 → gap 검증

# 엔터프라이즈 레벨 + PDCA
/auto --level enterprise --pdca "마이크로서비스 구축"
# → Enterprise 권장사항 적용 → K8s 설정 포함 문서화

# 문서만 생성
/auto --pdca --docs-only "API 설계"
# → Plan + Design 문서만 생성, 구현 안 함
```

---

## 마이그레이션 계획 (Critic 피드백 반영: Phase 의존성 명확화)

### Phase 의존성 다이어그램

```
Phase 1 (Week 1-2)          Phase 2 (Week 3-4)          Phase 3 (Week 5)
  OMC 흡수                     BKIT 흡수                   통합
      │                            │                         │
      │ 병렬 가능 ─────────────────┤                         │
      │                            │                         │
      ├─ Ralph 5조건               ├─ 프로젝트 레벨            │
      ├─ Ralplan 엔진              ├─ PDCA 엔진        ──────►│ 통합 루프
      ├─ Ultrawork                 ├─ gap-detector            │
      ├─ 32 에이전트               ├─ 11 에이전트      ──────►│ Orchestrator
      └─ Architect 검증            └─ --pdca 옵션             │
                                                              └─ 테스트
```

**의존성 규칙:**
- Phase 1과 Phase 2는 **병렬 진행 가능** (독립적)
- Phase 3은 **Phase 1+2 완료 필수** (통합 단계)

### Phase 1: OMC 흡수 (Week 1-2) - 독립 실행 가능

| Task | 파일 | 변경량 | 의존성 |
|------|------|--------|--------|
| Ralph 5조건 | `loop_control.py` | +227줄 | 없음 |
| Ralplan 엔진 | NEW `ralplan_engine.py` | +300줄 | 없음 |
| Ultrawork | NEW `parallel_executor.py` | +500줄 | 없음 |
| 32 에이전트 | `omc_bridge.py` | +248줄 | 없음 |
| Architect 검증 | `verification.py` | +136줄 | 없음 |

### Phase 2: BKIT 흡수 (Week 3-4) - 독립 실행 가능

| Task | 파일 | 변경량 | 의존성 |
|------|------|--------|--------|
| 프로젝트 레벨 | NEW `project_detector.py` | +200줄 | 없음 |
| PDCA 엔진 | NEW `pdca_engine.py` | +400줄 | 없음 |
| PDCA 문서 | NEW `pdca_docs.py` | +300줄 | 없음 |
| gap-detector | `verification.py` | +150줄 | 없음 |
| 11 에이전트 | `omc_bridge.py` | +100줄 | 없음 |
| --pdca 옵션 | `auto_cli.py` | +43줄 | 없음 |

### Phase 3: 통합 (Week 5) - Phase 1+2 완료 필수

| Task | 파일 | 변경량 | 의존성 |
|------|------|--------|--------|
| 통합 루프 | `loop_control.py` | +100줄 | Phase 1 Ralph + Phase 2 PDCA |
| Orchestrator 연동 | `auto_orchestrator.py` | +735줄 | Phase 1+2 전체 |
| Phase Gate 확장 | `phase_gate.py` | +341줄 | Phase 1 Ralplan |
| 테스트 | `tests/` | +500줄 | Phase 1+2+3 전체 |

### Phase 완료 조건 (Critic 피드백 반영: 롤백 포인트)

```markdown
## Phase 1 완료 조건
- [ ] 기존 모든 테스트 통과
- [ ] Ralph 5조건 단위 테스트 통과
- [ ] Ralplan 엔진 통합 테스트 통과
- [ ] `git tag v3.0.0-phase1` 생성

## Phase 2 완료 조건
- [ ] 기존 모든 테스트 통과
- [ ] PDCA 문서 생성 테스트 통과
- [ ] gap-detector 통합 테스트 통과
- [ ] `git tag v3.0.0-phase2` 생성

## Phase 3 완료 조건
- [ ] 전체 통합 테스트 통과
- [ ] Edge Case 테스트 통과
- [ ] `git tag v3.0.0` 생성
```

---

## Success Criteria

### Functional

| # | 검증 항목 | 검증 방법 |
|---|-----------|-----------|
| 1 | Ralph 5조건 | 5개 조건 모두 확인 후 완료 |
| 2 | Ralplan 합의 | Planner→Critic 루프 동작 |
| 3 | Ultrawork 병렬 | 2+ 작업 동시 실행 |
| 4 | PDCA 문서화 | docs/01-plan, 02-design 자동 생성 |
| 5 | gap-detector | 설계-구현 90% 일치 검증 |
| 6 | 43 에이전트 | OMC + BKIT 에이전트 모두 동작 |
| 7 | --pdca 옵션 | 문서화 모드 정상 동작 |

### Non-Functional

| # | 검증 항목 | 기준 |
|---|-----------|------|
| 1 | 코드 증가량 | ~4,800줄 (기존 8,211 → 13,000) |
| 2 | OMC 위임 제거 | 직접 구현으로 대체 |
| 3 | BKIT 호환 | `bkit:*` 에이전트 호출 가능 |

---

## Risks and Mitigations

| 리스크 | 영향 | 완화 방안 |
|--------|------|-----------|
| 코드 복잡도 증가 | 유지보수 어려움 | 모듈 분리, 테스트 커버리지 |
| BKIT 버전 충돌 | 에이전트 호출 실패 | 버전 호환성 체크 |
| 문서화 오버헤드 | 실행 속도 저하 | --pdca 옵션으로 선택적 적용 |
| gap-detector 정확도 | 잘못된 판정 | 90% 임계값 조정 가능 |

---

## Version History

### v3.0.0 (2026-02-02)
- **NEW**: 3자 통합 (OMC + BKIT + /auto)
- **NEW**: BKIT 실제 분석 반영 (popup-studio-ai 플러그인)
- **NEW**: PDCA 문서화 흡수
- **NEW**: gap-detector 통합
- **NEW**: 43 에이전트 통합 테이블
- **NEW**: --pdca, --level 옵션

---

## References

- `/auto` 스크립트: `C:\claude\.claude\skills\auto-workflow\scripts\`
- OMC 가이드라인: `C:\Users\AidenKim\.claude\CLAUDE.md`
- BKIT 플러그인: `C:\Users\AidenKim\.claude\plugins\cache\bkit-marketplace\bkit\1.5.0\`
- 이전 계획: `.omc/plans/omc-auto-absorption-integration.md` (v2.1.0)

---

**PLAN_READY: .omc/plans/omc-bkit-auto-unified-integration.md**
