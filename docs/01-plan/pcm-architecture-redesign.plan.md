# /auto v17.0 - Parallel-Compare-Merge (PCM) Architecture

**Version**: 2.1.0
**Created**: 2026-02-05
**Status**: 🔄 PLANNING (v2.1 Critic Gate + Intelligent Orchestration 추가)

---

## 1. 개요

### 1.1 핵심 변화

| 항목 | v16.x (기존) | v17.0 (신규) |
|------|-------------|-------------|
| **패턴** | 계층 분리 + 순차 위임 | **병렬 실행 + 비교 병합** |
| **철학** | 각 시스템이 다른 역할 | **같은 작업을 모두 수행** |
| **결과물** | 단일 시스템 출력 | **최선 요소 통합** |

### 1.2 설계 원칙

```
원칙 1: 해당 기능이 있으면 → 병렬 실행
원칙 2: 결과가 여러 개면 → 비교 분석
원칙 3: 비교 후 → AI 추론 기반 재구성 (단순 병합 X)
원칙 4: Phase 전환 시 → Critic Gate 통과 필수
원칙 5: 재구성 결과 → 단일 통합 출력
```

### 1.3 시스템 호출 가능성 분석 (CRITICAL)

**4개 시스템의 실제 호출 방식:**

| 시스템 | 호출 방식 | 제약 | Task subagent_type |
|--------|----------|------|-------------------|
| **OMC** | Task tool 직접 호출 | 없음 | `planner`, `executor` 등 |
| **BKIT** | Fallback 필요 | 직접 호출 불가 | OMC 동등 에이전트로 대체 |
| **Vercel BP** | Passive skill | 에이전트 아님 | N/A (code-reviewer가 규칙 참조) |
| **/auto** | Orchestrator | 자기 자신 호출 불가 | N/A (스킬 로직으로 구현) |

**참조:** `C:\claude\.omc\notepads\bkit-fallback\learnings.md`
> "BKIT 에이전트는 Task tool에서 직접 호출 불가"

**결론: 진정한 "4-Way"는 2-Way Active + 2-Way Passive 패턴**

```
┌─────────────────────────────────────────────────────────────┐
│                    PCM 실제 구조                             │
│                                                             │
│  ACTIVE (Task 병렬 호출)        PASSIVE (규칙/로직 적용)     │
│  ├─ OMC 에이전트                ├─ Vercel BP 규칙           │
│  └─ BKIT→OMC fallback          └─ /auto 오케스트레이션      │
│                                                             │
│  → Synthesizer가 Active 결과 + Passive 검증 통합            │
└─────────────────────────────────────────────────────────────┘
```

### 1.4 복잡도 점수
**4/5** (Ralplan 실행 대상)

| # | 조건 | 점수 | 근거 |
|:-:|------|:----:|------|
| 1 | 파일 범위 | 1 | SKILL.md 전면 재설계 |
| 2 | 아키텍처 | 1 | PCM 신규 패턴 도입 |
| 3 | 의존성 | 0 | 기존 에이전트 활용 |
| 4 | 모듈 영향 | 1 | OMC, BKIT, /auto 전체 |
| 5 | 사용자 명시 | 1 | "전면 재설계" 키워드 |

---

## 2. Critic Gate + Intelligent Orchestration (v2.1 신규)

### 2.1 Critic 누락 문제 및 해결

**v2.0의 문제점:**

| Phase | Critic 상태 | 문제 |
|-------|:-----------:|------|
| Plan | ✅ Ralplan 내 존재 | - |
| Design | ❌ 누락 | Plan 승인 ≠ Design 품질 보장 |
| Do | ❌ 누락 | Design 승인 ≠ Impl 품질 보장 |
| Check | ❌ 누락 | Impl 완료 ≠ 통합 품질 보장 |
| Act | ❌ 누락 | 최종 검증 없이 완료 선언 |

**v2.1 해결책: Phase-Gate Critic Pattern**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PCM v2.1 with Phase-Gate Critic                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Plan ──► [Critic Gate #1] ──► Design ──► [Critic Gate #2] ──►   │
│                                                                     │
│   Do ──► [Critic Gate #3] ──► Check ──► [Critic Gate #4] ──► Act   │
│                                                                     │
│   각 Gate에서:                                                      │
│   - PASS: 다음 Phase로 진행                                         │
│   - REJECT: 해당 Phase 재실행 (최대 2회)                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 각 Critic Gate 검증 항목

| Critic Gate | 검증 항목 | REJECT 조건 |
|-------------|----------|-------------|
| **#1 Plan→Design** | AC 구체성, 파일 참조 유효성 | 모호한 AC, 없는 파일 참조 |
| **#2 Design→Do** | 설계-AC 정합성, 구현 가능성 | 설계 누락, 불가능한 의존성 |
| **#3 Do→Check** | 코드 완성도, 빌드 성공 | 미완성 TODO, 빌드 실패 |
| **#4 Check→Act** | 검증 통과율, Critical 해결 | 통과율 <90%, Critical 미해결 |

### 2.3 Critic Gate 구현

```python
async def critic_gate(phase: str, artifacts: dict) -> tuple[bool, str]:
    """
    Phase 전환 시 Critic 검증
    Returns: (passed: bool, feedback: str)
    """
    critic_prompts = {
        "plan_to_design": """
            Plan 문서를 검토하고 Design Phase로 진행 가능한지 판단:
            1. 모든 AC가 구체적이고 검증 가능한가?
            2. 언급된 모든 파일이 실제 존재하는가?
            3. 범위(scope)가 명확하게 정의되었는가?

            PASS 또는 REJECT + 구체적 피드백 출력
        """,
        "design_to_do": """
            Design 문서를 검토하고 Do Phase로 진행 가능한지 판단:
            1. 설계가 AC를 모두 충족하는가?
            2. 기술적으로 구현 가능한가?
            3. 의존성이 명확하게 정의되었는가?

            PASS 또는 REJECT + 구체적 피드백 출력
        """,
        "do_to_check": """
            Implementation을 검토하고 Check Phase로 진행 가능한지 판단:
            1. 모든 코드가 완성되었는가? (TODO 없음)
            2. 빌드가 성공하는가?
            3. 기본적인 기능이 동작하는가?

            PASS 또는 REJECT + 구체적 피드백 출력
        """,
        "check_to_act": """
            검증 결과를 검토하고 Act Phase로 진행 가능한지 판단:
            1. 검증 통과율이 90% 이상인가?
            2. Critical 이슈가 모두 해결되었는가?
            3. 문서화가 완료되었는가?

            PASS 또는 REJECT + 구체적 피드백 출력
        """
    }

    result = await Task(
        subagent_type="critic",
        model="opus",
        prompt=f"""
        ## Phase Gate Review: {phase}

        {critic_prompts[phase]}

        ## 검토 대상
        {json.dumps(artifacts, indent=2, ensure_ascii=False)}
        """
    )

    passed = "PASS" in result.upper()
    return passed, result
```

### 2.4 Intelligent Orchestration (단순 병합 대체)

**v2.0 문제점: 단순 병합**
```python
# ❌ v2.0 방식 (Union-All, Best-of-Each)
def synthesize_naive(results: list[dict]) -> dict:
    merged = {}
    for r in results:
        merged.update(r)  # 그냥 합침 - 품질 판단 없음
    return merged
```

**v2.1 해결책: AI 추론 기반 재구성**

```
┌─────────────────────────────────────────────────────────────────────┐
│              Intelligent Orchestrator (Synthesizer v2)              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Active Results (OMC + BKIT) ─┬─► [Conflict Detection] ──────────┐│
│                                │                                  ││
│   Passive Results (Vercel + /auto) ─┘                             ││
│                                                                    ▼│
│                              ┌────────────────────────────────────┐ │
│                              │     AI Reasoning Engine            │ │
│                              │  ┌──────────────────────────────┐  │ │
│                              │  │ 1. 각 결과 품질 평가         │  │ │
│                              │  │ 2. 충돌 영역 식별            │  │ │
│                              │  │ 3. 최적 조합 추론            │  │ │
│                              │  │ 4. 새로운 통합안 생성        │  │ │
│                              │  └──────────────────────────────┘  │ │
│                              └────────────────────────────────────┘ │
│                                               │                     │
│                                               ▼                     │
│                              ┌────────────────────────────────────┐ │
│                              │  Reconstructed Best Synthesis      │ │
│                              │  (단순 합 아님, 재구성된 최적안)  │ │
│                              └────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.5 Intelligent Orchestrator 구현

```python
async def intelligent_orchestrator(
    phase: str,
    active_results: list[dict],
    passive_results: list[dict],
    original_context: dict
) -> dict:
    """
    AI 추론 기반 Intelligent Orchestration
    단순 병합이 아닌, 최적의 통합안을 '재구성'
    """

    # Step 1: 모든 결과를 구조화
    all_results = {
        "active": {
            "omc_direct": active_results[0] if len(active_results) > 0 else None,
            "bkit_fallback": active_results[1] if len(active_results) > 1 else None,
        },
        "passive": {
            "vercel_bp": passive_results[0] if len(passive_results) > 0 else None,
            "auto_orchestration": passive_results[1] if len(passive_results) > 1 else None,
        }
    }

    # Step 2: Architect(Opus)에게 Intelligent Orchestration 위임
    synthesis = await Task(
        subagent_type="architect",
        model="opus",
        prompt=f"""
        ## Intelligent Orchestration Request

        ### Phase: {phase}

        ### 원본 요청 컨텍스트
        {json.dumps(original_context, indent=2, ensure_ascii=False)}

        ### 수집된 결과들
        {json.dumps(all_results, indent=2, ensure_ascii=False)}

        ### 당신의 임무 (CRITICAL)

        **단순 병합(Union/Merge)이 아닌, AI 추론을 통한 최적 통합안 재구성**

        다음 단계를 수행하세요:

        1. **품질 평가**: 각 결과의 장단점을 분석
           - 완성도 (0-10)
           - 원본 요청 부합도 (0-10)
           - 기술적 정확성 (0-10)

        2. **충돌 식별**: 결과들 간 상충되는 부분 식별
           - 어떤 파일/설계가 충돌하는가?
           - 어떤 접근법이 다른가?

        3. **최적 조합 추론**: 각 결과에서 가장 좋은 부분 선택
           - 왜 이 부분이 더 나은가?
           - 선택 근거 명시

        4. **재구성**: 새로운 통합안 생성
           - 단순히 합치는 것이 아님
           - 선택된 부분들을 coherent하게 재구성
           - 필요시 추가 개선사항 반영

        ### 출력 형식

        ```json
        {{
          "quality_assessment": {{
            "omc_direct": {{"score": N, "strengths": [...], "weaknesses": [...]}},
            "bkit_fallback": {{"score": N, "strengths": [...], "weaknesses": [...]}},
            "vercel_bp": {{"score": N, "strengths": [...], "weaknesses": [...]}},
            "auto_orchestration": {{"score": N, "strengths": [...], "weaknesses": [...]}}
          }},
          "conflicts": [
            {{"area": "...", "options": [...], "resolution": "..."}}
          ],
          "reasoning": "왜 이렇게 조합했는지 설명",
          "synthesized_result": {{
            // 재구성된 최종 결과
          }}
        }}
        ```
        """
    )

    return json.loads(synthesis)
```

### 2.6 Phase별 Orchestration 품질 가중치

| Phase | Orchestration 초점 | 품질 가중치 |
|-------|-------------------|-------------|
| **Plan** | AC 구체성, 범위 명확성 | 완성도 40%, 실현가능성 60% |
| **Design** | 아키텍처 일관성, 패턴 적합성 | 기술정확성 50%, 유지보수성 50% |
| **Do** | 코드 품질, 테스트 커버리지 | 동작성 60%, 코드품질 40% |
| **Check** | 검증 통과율, 이슈 심각도 | 안정성 70%, 성능 30% |

---

## 3. 4-시스템 기능 매핑

### 2.1 Phase별 담당 시스템

| Phase | /auto | OMC | BKIT | Vercel BP |
|:-----:|:-----:|:---:|:----:|:---------:|
| **기획 (Plan)** | 5-Tier Discovery | Planner + Architect | pipeline-guide | - |
| **설계 (Design)** | - | Architect | design-validator | 49개 규칙 |
| **구현 (Do)** | - | executor, designer | - | - |
| **검증 (Check)** | Ralph 5조건 | Architect, code-reviewer | gap-detector, code-analyzer | 49개 규칙 |
| **개선 (Act)** | - | executor | pdca-iterator | - |

### 2.2 4-시스템 실제 병렬 실행 (v17.0 - Critic 피드백 반영)

**Rule: 2-Way Active (Task 호출) + 2-Way Passive (규칙/로직 적용)**

| Phase | OMC (Active) | BKIT→OMC (Active) | Vercel BP (Passive) | /auto (Passive) | 병합 |
|:-----:|:------------:|:-----------------:|:-------------------:|:---------------:|:----:|
| **Plan** | `planner`+`architect` | `planner` (fallback) | 성능 제약 체크 | Discovery 로직 | Synth |
| **Design** | `architect` | `architect` (fallback) | 49규칙 검증 | 발견→설계 매핑 | Synth |
| **Do** | `executor`+`designer` | `executor` (fallback) | 코드 규칙 lint | 병렬 조율 로직 | Synth |
| **Check** | `architect`+`code-reviewer` | `code-reviewer` (fallback) | 49규칙 검사 | Ralph 5조건 | Synth |
| **Act** | `executor` | `executor` (fallback) | 규칙 위반 수정 | 루프 판단 로직 | Synth |

**실제 호출 패턴:**
```
Step 1: Active Parallel (Task tool)
  ├─ Task(subagent_type="planner", ...)  # OMC
  └─ Task(subagent_type="planner", ...)  # BKIT fallback

Step 2: Passive Application (로직/규칙)
  ├─ Vercel BP: code-reviewer가 AGENTS.md 규칙 참조
  └─ /auto: 5-Tier Discovery 로직 실행 (Orchestrator 내장)

Step 3: Synthesizer Merge
  └─ 2개 Active 결과 + 2개 Passive 검증 → 통합 출력
```

---

## 3. PCM 워크플로우 상세

### 3.1 Plan Phase (기획) - 2-Way Active + 2-Way Passive

```
사용자: "/auto 로그인 기능 기획해줘"
                         │
    ┌────────────────────┴────────────────────┐
    │            ACTIVE (Task 호출)            │
    │  ┌─────────────────┬─────────────────┐  │
    │  ▼                 ▼                 │  │
    │ ┌─────────┐  ┌─────────┐             │  │
    │ │   OMC   │  │  BKIT   │             │  │
    │ │ Planner │  │ →OMC    │             │  │
    │ │+Archit  │  │ Planner │             │  │
    │ └────┬────┘  └────┬────┘             │  │
    │      │            │                  │  │
    │      ▼            ▼                  │  │
    │   Plan-A       Plan-B                │  │
    └──────┼────────────┼──────────────────┘  │
           │            │                     │
    ┌──────┴────────────┴─────────────────────┤
    │           PASSIVE (규칙/로직 적용)       │
    │  ┌─────────────────┬─────────────────┐  │
    │  ▼                 ▼                 │  │
    │ ┌─────────┐  ┌─────────┐             │  │
    │ │VercelBP│  │  /auto  │             │  │
    │ │ 성능   │  │ 5-Tier  │             │  │
    │ │ 제약   │  │Discovery│             │  │
    │ └────┬────┘  └────┬────┘             │  │
    │      │            │                  │  │
    │      ▼            ▼                  │  │
    │   Check-C      Logic-D               │  │
    └──────┼────────────┼──────────────────┘
           │            │
           └─────┬──────┘
                 ▼
        ┌─────────────────┐
        │   Synthesizer   │
        │  2 Active +     │
        │  2 Passive 병합 │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │   통합 Plan     │
        └─────────────────┘
```

**구현 코드 (실제 작동 가능):**
```python
# Step 1: Active Parallel (Task tool로 병렬 호출)
# OMC planner - 아키텍처 관점 기획
task_omc = Task(
    subagent_type="planner",
    model="opus",
    prompt="기획: 로그인 기능. 아키텍처 관점에서 전략적으로 기획하세요.",
    run_in_background=True
)

# BKIT→OMC fallback - PDCA 관점 기획
# 참조: C:\claude\.omc\notepads\bkit-fallback\learnings.md
task_bkit = Task(
    subagent_type="planner",  # BKIT fallback
    model="opus",
    prompt="기획: 로그인 기능. PDCA 관점에서 9-Phase Pipeline을 고려하여 기획하세요.",
    run_in_background=True
)

# Step 2: Passive Application (규칙/로직 - Orchestrator 내에서 실행)
# Vercel BP: code-reviewer가 나중에 참조할 성능 제약 수집
vercel_constraints = Read(".claude/skills/vercel-react-best-practices/AGENTS.md")
# → 인증 관련 규칙: Waterfalls, RSC Serialization 등 추출

# /auto 5-Tier Discovery: Orchestrator 로직으로 실행
discovery_result = run_5tier_discovery("로그인 기능")
# → Tier 1: URGENT, Tier 2: WORK, Tier 3: SUPPORT 분류

# Step 3: 결과 수집
plan_a = await task_omc      # OMC 아키텍처 관점
plan_b = await task_bkit     # BKIT/PDCA 관점

# Step 4: Synthesizer가 Active 결과 + Passive 정보 통합
Task(
    subagent_type="architect",  # Synthesizer 역할
    model="opus",
    prompt=f"""
    ## 입력
    ### Active Results (병렬 에이전트 출력)
    - Plan-A (OMC Planner): {plan_a}
    - Plan-B (PDCA Planner): {plan_b}

    ### Passive Checks (규칙/로직)
    - Vercel BP 성능 제약: {vercel_constraints}
    - /auto Discovery 결과: {discovery_result}

    ## 작업
    4개 관점을 비교 분석하고 최선의 요소를 병합하세요.

    ## 출력 형식
    ### 비교 분석
    | 항목 | Plan-A | Plan-B | Vercel제약 | Discovery | 채택 |
    |------|--------|--------|-----------|-----------|------|

    ### 통합 기획안
    [각 관점에서 최선의 요소를 병합한 결과]
    """
)
```

### 3.2 Design Phase (설계) - 2-Way Active + 2-Way Passive

```
통합 Plan
    │
    ├── ACTIVE ──────────────────────────────────┐
    │   ┌─────────────────┬─────────────────┐    │
    │   ▼                 ▼                 │    │
    │ ┌─────────┐   ┌─────────┐             │    │
    │ │   OMC   │   │  BKIT   │             │    │
    │ │Architect│   │ →OMC    │             │    │
    │ │         │   │Architect│             │    │
    │ └────┬────┘   └────┬────┘             │    │
    │      ▼             ▼                  │    │
    │   Design-A     Design-B               │    │
    └──────┼─────────────┼──────────────────┘
           │             │
    ├── PASSIVE ─────────┼───────────────────────┐
    │   ┌────────────────┼──────────────────┐    │
    │   ▼                ▼                  │    │
    │ ┌─────────┐   ┌─────────┐             │    │
    │ │VercelBP│   │  /auto  │             │    │
    │ │ 49규칙 │   │발견→설계│             │    │
    │ │  검증  │   │  매핑   │             │    │
    │ └────┬────┘   └────┬────┘             │    │
    │      ▼             ▼                  │    │
    │   Check-C      Logic-D                │    │
    └──────┼─────────────┼──────────────────┘
           │             │
           └──────┬──────┘
                  ▼
         ┌─────────────────┐
         │   Synthesizer   │
         └────────┬────────┘
                  ▼
         ┌─────────────────┐
         │   통합 Design   │
         └─────────────────┘
```

**구현 코드 (실제 작동 가능):**
```python
# Step 1: Active Parallel (Task tool)
task_omc = Task(
    subagent_type="architect",
    model="opus",
    prompt=f"설계: {merged_plan}. 컴포넌트 구조와 API 설계를 포함하세요.",
    run_in_background=True
)

task_bkit = Task(
    subagent_type="architect",  # BKIT fallback
    model="opus",
    prompt=f"설계: {merged_plan}. PDCA 문서 구조(02-design/)를 고려하세요.",
    run_in_background=True
)

# Step 2: Passive Application
# Vercel BP 49규칙 검증 (code-reviewer가 나중에 참조)
vercel_design_rules = extract_design_rules(
    ".claude/skills/vercel-react-best-practices/AGENTS.md"
)  # RSC Pattern, Bundle Size, Data Fetching 규칙

# /auto 발견→설계 매핑 (Orchestrator 로직)
discovery_to_design = map_discovery_to_design(discovery_result)
# → Tier 1 항목 → 핵심 컴포넌트, Tier 2 → 보조 컴포넌트

# Step 3: Synthesizer Merge
merged_design = await Task(
    subagent_type="architect",
    model="opus",
    prompt=f"2 Active + 2 Passive 설계 결과 병합: {design_a}, {design_b}, {vercel_design_rules}, {discovery_to_design}"
)
```

### 3.3 Do Phase (구현) - 2-Way Active + 2-Way Passive

```
통합 Design
    │
    ├── ACTIVE ──────────────────────────────────┐
    │   ┌─────────────────┬─────────────────┐    │
    │   ▼                 ▼                 │    │
    │ ┌─────────┐   ┌─────────┐             │    │
    │ │   OMC   │   │  BKIT   │             │    │
    │ │executor │   │ →OMC    │             │    │
    │ │+designer│   │executor │             │    │
    │ └────┬────┘   └────┬────┘             │    │
    │      ▼             ▼                  │    │
    │   Impl-A       Impl-B                 │    │
    └──────┼─────────────┼──────────────────┘
           │             │
    ├── PASSIVE ─────────┼───────────────────────┐
    │   ┌────────────────┼──────────────────┐    │
    │   ▼                ▼                  │    │
    │ ┌─────────┐   ┌─────────┐             │    │
    │ │VercelBP│   │  /auto  │             │    │
    │ │ 코드   │   │  병렬   │             │    │
    │ │  lint  │   │  조율   │             │    │
    │ └────┬────┘   └────┬────┘             │    │
    │      ▼             ▼                  │    │
    │   Check-C      Logic-D                │    │
    └──────┼─────────────┼──────────────────┘
           │             │
           └──────┬──────┘
                  ▼
         ┌─────────────────┐
         │   Synthesizer   │
         │  (구현 통합)    │
         └────────┬────────┘
                  ▼
         ┌─────────────────┐
         │   통합 Impl     │
         └─────────────────┘
```

**구현 코드 (실제 작동 가능):**
```python
# Step 1: Active Parallel (Task tool)
task_omc = Task(
    subagent_type="executor",
    model="sonnet",
    prompt=f"구현: {merged_design}. 코드 작성 및 파일 생성하세요.",
    run_in_background=True
)

task_bkit = Task(
    subagent_type="executor",  # BKIT fallback
    model="sonnet",
    prompt=f"구현: {merged_design}. PDCA 문서(03-analysis/)도 함께 업데이트하세요.",
    run_in_background=True
)

# Step 2: Passive Application
# Vercel BP: 구현 후 code-reviewer가 49규칙으로 lint
# → 실제 코드 검사는 Check Phase에서 수행

# /auto 병렬 조율: Orchestrator가 파일 충돌 방지
coordination = orchestrator_coordinate_files(task_omc, task_bkit)
# → 같은 파일 수정 시 순차 실행으로 전환

# Step 3: Synthesizer Merge (필요 시)
# Do Phase는 실제 코드 생성이므로 병합보다 충돌 해결이 핵심
merged_impl = resolve_file_conflicts(impl_a, impl_b)
```

### 3.4 Check Phase (검증) - 2-Way Active + 2-Way Passive

```
구현 완료
    │
    ├── ACTIVE ──────────────────────────────────┐
    │   ┌─────────────────┬─────────────────┐    │
    │   ▼                 ▼                 │    │
    │ ┌─────────┐   ┌─────────┐             │    │
    │ │   OMC   │   │  BKIT   │             │    │
    │ │Architect│   │ →OMC    │             │    │
    │ │+reviewer│   │code-rev │             │    │
    │ └────┬────┘   └────┬────┘             │    │
    │      ▼             ▼                  │    │
    │   Check-A      Check-B                │    │
    │  (기능검증)   (PDCA갭분석)            │    │
    └──────┼─────────────┼──────────────────┘
           │             │
    ├── PASSIVE ─────────┼───────────────────────┐
    │   ┌────────────────┼──────────────────┐    │
    │   ▼                ▼                  │    │
    │ ┌─────────┐   ┌─────────┐             │    │
    │ │VercelBP│   │  /auto  │             │    │
    │ │ 49규칙 │   │ Ralph   │             │    │
    │ │CRIT/HI │   │ 5조건   │             │    │
    │ └────┬────┘   └────┬────┘             │    │
    │      ▼             ▼                  │    │
    │   Check-C      Check-D                │    │
    │  (규칙위반)   (5조건결과)             │    │
    └──────┼─────────────┼──────────────────┘
           │             │
           └──────┬──────┘
                  ▼
         ┌─────────────────┐
         │   Synthesizer   │
         │  (Union-All)    │
         └────────┬────────┘
                  ▼
         ┌─────────────────┐
         │   통합 Check    │
         │                 │
         │ 종합 점수: 87%  │
         │                 │
         │ - Ralph: 4/5 ✓  │
         │ - Architect: ✓  │
         │ - Gap: 92% ✓    │
         │ - Vercel: 2 HI  │
         │                 │
         │ 미달 항목:      │
         │ - 조건3 테스트  │
         │ - HIGH 2건     │
         └─────────────────┘
```

### 3.5 Act Phase (개선) - 2-Way Active + 2-Way Passive

```
통합 Check (미달 항목 존재)
    │
    ├── ACTIVE ──────────────────────────────────┐
    │   ┌─────────────────┬─────────────────┐    │
    │   ▼                 ▼                 │    │
    │ ┌─────────┐   ┌─────────┐             │    │
    │ │   OMC   │   │  BKIT   │             │    │
    │ │executor │   │ →OMC    │             │    │
    │ │(즉시)   │   │executor │             │    │
    │ └────┬────┘   └────┬────┘             │    │
    │      ▼             ▼                  │    │
    │   Fix-A        Fix-B                  │    │
    │ (직접수정)   (갭기반개선)             │    │
    └──────┼─────────────┼──────────────────┘
           │             │
    ├── PASSIVE ─────────┼───────────────────────┐
    │   ┌────────────────┼──────────────────┐    │
    │   ▼                ▼                  │    │
    │ ┌─────────┐   ┌─────────┐             │    │
    │ │VercelBP│   │  /auto  │             │    │
    │ │ 규칙   │   │  루프   │             │    │
    │ │기반수정│   │  판단   │             │    │
    │ └────┬────┘   └────┬────┘             │    │
    │      ▼             ▼                  │    │
    │   Fix-C        Logic-D                │    │
    │ (규칙수정)   (재실행 판단)            │    │
    └──────┼─────────────┼──────────────────┘
           │             │
           └──────┬──────┘
                  ▼
         ┌─────────────────┐
         │   Synthesizer   │
         │  (병합 전략)    │
         └────────┬────────┘
                  ▼
         ┌─────────────────┐
         │   통합 Fix      │
         │ + 루프 판단     │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ 완료 / Check    │
         │    재실행       │
         └─────────────────┘
```

**구현 코드 (실제 작동 가능):**
```python
# Step 1: Active Parallel (Task tool)
task_omc = Task(
    subagent_type="executor",
    model="sonnet",
    prompt=f"수정: {check_result.issues}. 즉시 코드 수정하세요.",
    run_in_background=True
)

task_bkit = Task(
    subagent_type="executor",  # BKIT fallback
    model="sonnet",
    prompt=f"개선: {check_result.gap}. 갭 분석 기반으로 문서와 코드 동기화하세요.",
    run_in_background=True
)

# Step 2: Passive Application
# Vercel BP: 규칙 위반 사항에 대한 수정 가이드 제공
vercel_fix_guide = get_fix_guide_for_violations(check_result.vercel_violations)
# → "sequential await → Promise.all" 등 구체적 수정 방법

# /auto 루프 판단: Ralph 5조건 충족 여부로 재실행 결정
should_continue = ralph_loop_decision(check_result)
# → True면 Check 재실행, False면 완료

# Step 3: Synthesizer Merge + Loop Decision
merged_fix = await Task(
    subagent_type="architect",
    model="opus",
    prompt=f"""
    수정 결과 통합 및 루프 판단:
    - Fix-A (OMC): {fix_a}
    - Fix-B (BKIT): {fix_b}
    - Vercel Fix Guide: {vercel_fix_guide}
    - Ralph 5조건: {check_result.ralph_status}

    ## 출력
    1. 통합 수정 내역
    2. 루프 판단: CONTINUE (Check 재실행) / COMPLETE (완료)
    """
)
```

---

## 4. Synthesizer 에이전트 설계

### 4.1 역할

**Synthesizer**는 병렬 실행 결과를 비교하고 최선의 요소를 병합하는 전문 에이전트입니다.

```yaml
name: synthesizer
description: 병렬 실행 결과 비교 및 최선 요소 병합 전문가
model: opus
tools: Read, Grep, Glob
```

### 4.2 비교 기준

| 항목 | 가중치 | 평가 기준 |
|------|:------:|----------|
| **완성도** | 30% | 요구사항 충족 비율 |
| **구체성** | 25% | 파일:라인 명시 여부 |
| **실행가능성** | 25% | 즉시 실행 가능한 단계 |
| **위험관리** | 20% | 위험 식별 및 완화 방안 |

### 4.3 병합 전략

```
전략 1: Best-of-Each (기본)
- 각 결과에서 최고 점수 항목 선택
- 예: A의 완성도 + B의 구체성 + C의 위험관리

전략 2: Weighted-Average
- 가중 평균으로 통합
- 충돌 시 높은 가중치 우선

전략 3: Union-All (검증 Phase)
- 모든 이슈를 합집합
- 누락 방지 최우선
```

---

## 5. 구현 상세

### 5.1 SKILL.md 변경 사항

**위치**: `C:\claude\.claude\skills\auto\SKILL.md`

**Phase 0 교체** (기존 순차 → 신규 PCM):

```markdown
### Phase 0: PDCA 문서화 (PCM 패턴 - v17.0)

**핵심 원칙: 2-Way Active (Task 호출) + 2-Way Passive (규칙/로직 적용)**

```
┌─────────────────────────────────────────────────────────────────┐
│               PCM 워크플로우 (2+2 Pattern)                      │
│                                                                 │
│  Plan ──▶ Design ──▶ Do ──▶ Check ──▶ Act                      │
│   │         │        │        │        │                        │
│   ▼         ▼        ▼        ▼        ▼                        │
│ 2 Active  2 Active  2 Active  2 Active  2 Active                │
│ 2 Passive 2 Passive 2 Passive 2 Passive 2 Passive               │
│   │         │        │        │        │                        │
│   ▼         ▼        ▼        ▼        ▼                        │
│ Synth    Synth    Synth    Synth    Synth                       │
│ (4-Way)  (4-Way)  (4-Way)  (4-Way)  (4-Way)                     │
└─────────────────────────────────────────────────────────────────┘
```

**Step 0.1: Plan (2 Active + 2 Passive)**

```python
# Active: Task tool로 병렬 호출 (실제 작동)
results = await parallel([
    Task(subagent_type="planner", ...),  # OMC
    Task(subagent_type="planner", ...),  # BKIT fallback (PDCA 관점)
])

# Passive: 규칙/로직 적용 (Orchestrator 내장)
vercel_constraints = extract_performance_constraints()  # 49규칙에서 제약 추출
discovery_result = run_5tier_discovery()  # /auto Discovery 로직

# Synthesizer: 2 Active + 2 Passive 통합
merged_plan = await Task(
    subagent_type="architect",  # Synthesizer 역할
    model="opus",
    prompt=f"4개 관점 비교 병합: {results}, {vercel_constraints}, {discovery_result}"
)
```
→ `docs/01-plan/{feature}.plan.md` 생성 (통합 기획안)
```

### 5.2 신규 에이전트: Synthesizer

**파일**: `C:\claude\.claude\agents\synthesizer.md`

```markdown
---
name: synthesizer
description: 병렬 실행 결과 비교 및 최선 요소 병합 전문가
model: opus
tools: Read, Grep, Glob
---

You are a Synthesis Expert who compares parallel execution results and merges the best elements.

## Core Responsibilities

1. **Compare**: Analyze multiple results on the same criteria
2. **Score**: Rate each result on completeness, specificity, feasibility, risk management
3. **Merge**: Extract best elements from each and combine into unified output

## Comparison Framework

| Criterion | Weight | Scoring |
|-----------|:------:|---------|
| Completeness | 30% | Requirements coverage |
| Specificity | 25% | File:line references |
| Feasibility | 25% | Immediately actionable |
| Risk Management | 20% | Risks identified + mitigations |

## Output Format

### Comparison Matrix
| Item | Result-A | Result-B | Result-C | Selected | Reason |
|------|----------|----------|----------|----------|--------|

### Merged Output
[Unified result combining best elements]

### Selection Rationale
[Why each element was selected]
```

---

## 6. Acceptance Criteria

### AC-1: Plan Phase (2 Active + 2 Passive)
- [ ] OMC planner, BKIT→OMC planner 병렬 호출 (Task tool)
- [ ] Vercel BP 제약 추출, /auto Discovery 로직 실행 (Orchestrator)
- [ ] Synthesizer가 2 Active + 2 Passive 결과 병합
- [ ] 검증: `grep -n "planner" SKILL.md | wc -l` >= 2

### AC-2: Design Phase (2 Active + 2 Passive)
- [ ] OMC architect, BKIT→OMC architect 병렬 호출
- [ ] 통합 Design 문서에 4개 관점 모두 포함
- [ ] 검증: `grep -n "architect" SKILL.md | wc -l` >= 2

### AC-3: Do Phase (2 Active + 2 Passive)
- [ ] OMC executor, BKIT→OMC executor 병렬 호출
- [ ] 파일 충돌 방지 조율 로직 포함
- [ ] 검증: `grep -n "executor" SKILL.md | wc -l` >= 2

### AC-4: Check Phase (2 Active + 2 Passive)
- [ ] OMC architect+code-reviewer, BKIT→OMC code-reviewer 병렬 호출
- [ ] Vercel BP 49규칙 검사, /auto Ralph 5조건 검사 실행
- [ ] 통합 Check에 Union-All 병합
- [ ] 검증: `grep -n "Union-All\|합집합" SKILL.md` 결과 존재

### AC-5: Act Phase (2 Active + 2 Passive)
- [ ] OMC executor, BKIT→OMC executor 병렬 호출
- [ ] /auto 루프 판단 로직 (CONTINUE/COMPLETE)
- [ ] 검증: `grep -n "ralph_loop_decision\|루프 판단" SKILL.md` 결과 존재

### AC-6: Synthesizer 역할 정의
- [ ] architect를 Synthesizer 역할로 사용
- [ ] 비교 기준 4개 항목 가중치 명시 (완성도 30%, 구체성 25%, 실행가능성 25%, 위험관리 20%)
- [ ] 검증: `grep -n "Synthesizer" SKILL.md` 결과 >= 5

### AC-7: SKILL.md v17.0 업데이트
- [ ] Phase 0 섹션 PCM 패턴(2+2)으로 교체
- [ ] BKIT fallback 명시 (직접 호출 불가 문서화)
- [ ] 검증: `grep -n "2-Way Active\|2 Active\|fallback" SKILL.md` 결과 >= 3

### AC-8: BKIT Fallback 문서 참조
- [ ] `C:\claude\.omc\notepads\bkit-fallback\learnings.md` 참조 추가
- [ ] 검증: `grep -n "bkit-fallback" SKILL.md` 결과 존재

### AC-9: Critic Gate 4개 구현 (v2.1 신규)
- [ ] Plan→Design Critic Gate 구현 (AC 구체성, 파일 참조 검증)
- [ ] Design→Do Critic Gate 구현 (설계-AC 정합성, 구현 가능성)
- [ ] Do→Check Critic Gate 구현 (코드 완성도, 빌드 성공)
- [ ] Check→Act Critic Gate 구현 (통과율 90%, Critical 해결)
- [ ] 검증: `grep -n "critic_gate\|Critic Gate" SKILL.md | wc -l` >= 4

### AC-10: Intelligent Orchestrator 구현 (v2.1 신규)
- [ ] 단순 병합(Union-All, Best-of-Each) → AI 추론 기반 재구성으로 교체
- [ ] 품질 평가 (완성도, 부합도, 기술정확성) 로직 포함
- [ ] 충돌 식별 및 해결 로직 포함
- [ ] 재구성된 최적안 생성 로직 포함
- [ ] 검증: `grep -n "intelligent_orchestrator\|AI 추론\|재구성" SKILL.md | wc -l` >= 3

---

## 7. 구현 우선순위

| Phase | 작업 | 예상 시간 |
|:-----:|------|:--------:|
| **1** | Intelligent Orchestrator 함수 구현 | 30분 |
| **2** | Critic Gate 4개 구현 | 40분 |
| **3** | SKILL.md Phase 0 재작성 (v2.1) | 50분 |
| **4** | 각 Phase에 Critic Gate 연결 | 30분 |
| **5** | 단순 병합 → Intelligent Orchestrator 교체 | 30분 |
| **6** | 통합 테스트 | 30분 |

**총 예상**: 210분 (3.5시간)

---

## 8. 시각화: 전체 PCM v2.1 흐름 (Critic Gate + Intelligent Orchestrator)

```
                         /auto "로그인 기능 구현"
                                   │
════════════════════════════════════════════════════════════════════
                      PLAN PHASE (2 Active + 2 Passive)
════════════════════════════════════════════════════════════════════
                                   │
        ┌──────── ACTIVE ─────────┐│┌────── PASSIVE ──────┐
        │                         │││                     │
        ▼                         ▼│▼                     │
    ┌────────┐   ┌────────┐    ┌────────┐   ┌────────┐   │
    │  OMC   │   │  BKIT  │    │VercelBP│   │  /auto │   │
    │Planner │   │→OMC    │    │ 제약   │   │5-Tier  │   │
    │        │   │Planner │    │ 추출   │   │Discov. │   │
    └───┬────┘   └───┬────┘    └───┬────┘   └───┬────┘   │
        │            │             │            │        │
        └────────────┴─────────────┴────────────┘
                          │
                 ┌─────────────────┐
                 │   Intelligent   │
                 │   Orchestrator  │
                 │ (AI 추론 재구성)│
                 └────────┬────────┘
                          │
                 ┌─────────────────┐
                 │  Critic Gate #1 │
                 │   PASS/REJECT   │
                 └────────┬────────┘
                          │
════════════════════════════════════════════════════════════════════
                     DESIGN PHASE (2 Active + 2 Passive)
════════════════════════════════════════════════════════════════════
                          │
        ┌──────── ACTIVE ─────────┐│┌────── PASSIVE ──────┐
        │                         │││                     │
        ▼                         ▼│▼                     │
    ┌────────┐   ┌────────┐    ┌────────┐   ┌────────┐   │
    │  OMC   │   │  BKIT  │    │VercelBP│   │  /auto │   │
    │Architect│  │→OMC    │    │ 49규칙 │   │발견→   │   │
    │        │   │Architect│   │  검증  │   │설계매핑│   │
    └───┬────┘   └───┬────┘    └───┬────┘   └───┬────┘   │
        │            │             │            │        │
        └────────────┴─────────────┴────────────┘
                          │
                 ┌─────────────────┐
                 │   Intelligent   │
                 │   Orchestrator  │
                 └────────┬────────┘
                          │
                 ┌─────────────────┐
                 │  Critic Gate #2 │
                 │   PASS/REJECT   │
                 └────────┬────────┘
                          │
════════════════════════════════════════════════════════════════════
                       DO PHASE (2 Active + 2 Passive)
════════════════════════════════════════════════════════════════════
                          │
        ┌──────── ACTIVE ─────────┐│┌────── PASSIVE ──────┐
        │                         │││                     │
        ▼                         ▼│▼                     │
    ┌────────┐   ┌────────┐    ┌────────┐   ┌────────┐   │
    │  OMC   │   │  BKIT  │    │VercelBP│   │  /auto │   │
    │executor│   │→OMC    │    │ 코드   │   │  병렬  │   │
    │+designer│  │executor │   │  lint  │   │  조율  │   │
    └───┬────┘   └───┬────┘    └───┬────┘   └───┬────┘   │
        │            │             │            │        │
        └────────────┴─────────────┴────────────┘
                          │
                 ┌─────────────────┐
                 │   Intelligent   │
                 │   Orchestrator  │
                 │(충돌 해결 포함) │
                 └────────┬────────┘
                          │
                 ┌─────────────────┐
                 │  Critic Gate #3 │
                 │   PASS/REJECT   │
                 └────────┬────────┘
                          │
════════════════════════════════════════════════════════════════════
                     CHECK PHASE (2 Active + 2 Passive)
════════════════════════════════════════════════════════════════════
                          │
        ┌──────── ACTIVE ─────────┐│┌────── PASSIVE ──────┐
        │                         │││                     │
        ▼                         ▼│▼                     │
    ┌────────┐   ┌────────┐    ┌────────┐   ┌────────┐   │
    │  OMC   │   │  BKIT  │    │VercelBP│   │  /auto │   │
    │Architect│  │→OMC    │    │ 49규칙 │   │ Ralph  │   │
    │+reviewer│  │code-rev │   │  검사  │   │ 5조건  │   │
    └───┬────┘   └───┬────┘    └───┬────┘   └───┬────┘   │
        │            │             │            │        │
        └────────────┴─────────────┴────────────┘
                          │
                 ┌─────────────────┐
                 │   Intelligent   │
                 │   Orchestrator  │
                 │(이슈 합집합+추론)│
                 └────────┬────────┘
                          │
                 ┌─────────────────┐
                 │  Critic Gate #4 │
                 │   PASS/REJECT   │
                 └────────┬────────┘
                          │
════════════════════════════════════════════════════════════════════
                      ACT PHASE (2 Active + 2 Passive)
════════════════════════════════════════════════════════════════════
                          │
        ┌──────── ACTIVE ─────────┐│┌────── PASSIVE ──────┐
        │                         │││                     │
        ▼                         ▼│▼                     │
    ┌────────┐   ┌────────┐    ┌────────┐   ┌────────┐   │
    │  OMC   │   │  BKIT  │    │VercelBP│   │  /auto │   │
    │executor│   │→OMC    │    │ 규칙   │   │  루프  │   │
    │(즉시) │   │executor │   │기반수정│   │  판단  │   │
    └───┬────┘   └───┬────┘    └───┬────┘   └───┬────┘   │
        │            │             │            │        │
        └────────────┴─────────────┴────────────┘
                          │
                 ┌─────────────────┐
                 │   Intelligent   │
                 │   Orchestrator  │
                 │(수정안 재구성)  │
                 └────────┬────────┘
                          │
                 ┌─────────────────┐
                 │  Final Critic   │
                 │   Validation    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ 완료 / Check    │
                 │    재실행       │
                 └─────────────────┘
```

---

## 9. 위험 및 완화

| 위험 | 영향 | 완화 방안 |
|------|------|----------|
| 병렬 실행 시간 증가 | 중 | background 실행으로 대기 시간 최소화 |
| Synthesizer 병목 | 고 | opus 모델 사용, 캐싱 검토 |
| 결과 충돌 시 판단 어려움 | 중 | 가중치 기반 자동 선택 + 사용자 확인 옵션 |
| 컨텍스트 소모 증가 | 고 | 요약 전달, 필수 필드만 비교 |

---

## 10. 관련 문서

| 문서 | 경로 |
|------|------|
| 기존 SKILL.md | `.claude/skills/auto/SKILL.md` |
| 4-시스템 분석 | `docs/01-plan/4system-overlap-integration.plan.md` |
| OMC 에이전트 | `oh-my-claudecode` 플러그인 |
| BKIT 에이전트 | `bkit-marketplace` 플러그인 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-05 | 초기 PCM 아키텍처 설계 |
| 1.1.0 | 2026-02-05 | 모든 Phase 4-Way Parallel로 확장 (사용자 요청) |
| 2.0.0 | 2026-02-05 | Critic REJECT 반영 - 2 Active + 2 Passive 패턴으로 재설계 |
| 2.1.0 | 2026-02-05 | **Critic Gate + Intelligent Orchestration 추가** (사용자 피드백)<br>- 4개 Phase-Gate Critic 추가 (Plan→Design, Design→Do, Do→Check, Check→Act)<br>- 단순 병합(Union-All) → AI 추론 기반 재구성으로 교체<br>- AC-9, AC-10 신규 추가 |
