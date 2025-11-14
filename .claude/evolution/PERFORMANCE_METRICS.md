# Agent Performance Metrics & Evaluation

Agent/스킬 사용 성능을 자동으로 판단하는 시스템

**버전**: 1.0.0
**업데이트**: 2025-01-14

---

## 📊 성능 판단 메커니즘

### 3가지 평가 방식

```
┌─────────────────────────────────────────────────┐
│  1. 정량적 메트릭 (자동 측정)                      │
│     - Task completion rate                      │
│     - Execution duration                        │
│     - Error rate                                │
│     - User rating                               │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  2. 정성적 메트릭 (LLM-as-Judge)                  │
│     - Output quality (출력 품질)                 │
│     - Task relevance (작업 관련성)               │
│     - Code quality (코드 품질)                   │
│     - Completeness (완전성)                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  3. 종합 성능 점수                                │
│     - 가중 평균 (0-100점)                        │
│     - 등급 (S/A/B/C/D/F)                        │
│     - 상태 판정 (Excellent/Good/Acceptable/Poor) │
└─────────────────────────────────────────────────┘
```

---

## 1️⃣ 정량적 메트릭 (자동)

### 측정 항목

| 메트릭 | 설명 | 측정 방법 | 좋은 기준 |
|--------|------|-----------|----------|
| **Success Rate** | 성공/실패율 | Langfuse traces 분석 | ≥90% |
| **Avg Duration** | 평균 실행 시간 | trace duration 계산 | ≤2초 |
| **Error Rate** | 에러율 | error status 비율 | ≤5% |
| **User Rating** | 사용자 평점 | scores.user_rating 평균 | ≥4/5 |
| **Effectiveness** | 효과성 | scores.effectiveness 평균 | ≥0.8 |
| **P95 Duration** | 95 percentile 시간 | 상위 5% 제외 | ≤5초 |

### 자동 수집

```python
from track_agent_usage import get_tracker

tracker = get_tracker()

# Agent 실행 (자동 기록)
with tracker.track("context7-engineer", phase="Phase 0", task="Verify docs"):
    result = agent.run()
    # → duration, status 자동 측정

# 피드백 수집
tracker.collect_feedback(
    agent="context7-engineer",
    rating=5,  # 1-5
    effectiveness=0.95  # 0-1
)
```

---

## 2️⃣ 정성적 메트릭 (LLM-as-Judge)

### Claude API 기반 자동 평가

**목적**: 출력물의 품질을 AI가 자동으로 평가

### 평가 항목

| 항목 | 설명 | 평가 기준 |
|------|------|-----------|
| **Quality** | 출력 품질 | 가독성, 전문성, 구조 |
| **Relevance** | 작업 관련성 | Task 요구사항 충족도 |
| **Completeness** | 완전성 | 필요한 정보 포함 여부 |
| **Accuracy** | 정확성 | 사실 오류, 논리 오류 없음 |

### 사용 방법

```python
from llm_judge import LLMJudge

judge = LLMJudge()

# Agent 출력 평가
score = judge.evaluate_output(
    agent="context7-engineer",
    task="Verify React 18 documentation",
    output="React 18 introduces Suspense, Concurrent rendering...",
    expected="Comprehensive documentation verification"
)

print(f"Quality: {score.quality}/10")
print(f"Overall: {score.overall_score:.1f}/10")
print(f"Reasoning: {score.reasoning}")
```

### 코드 품질 평가

```python
# 생성된 코드 평가
code = """
def calculate_total(items):
    return sum(item.price * item.quantity for item in items)
"""

score = judge.evaluate_code_quality(code, language="python")
# → Quality, Relevance, Completeness, Accuracy
```

### A/B 테스트

```python
# 두 버전 비교
comparison = judge.compare_outputs(
    output_a=agent_v1_output,
    output_b=agent_v2_output,
    task="Generate unit tests"
)

print(f"Winner: {comparison['winner']}")  # "A" or "B" or "tie"
print(f"Reasoning: {comparison['reasoning']}")
```

---

## 3️⃣ 종합 성능 점수

### 계산 공식

```python
performance_score = (
    success_rate * 0.30 +      # 30%
    user_rating * 0.25 +       # 25%
    effectiveness * 0.20 +     # 20%
    speed_score * 0.15 +       # 15% (inverse duration)
    (1 - error_rate) * 0.10    # 10% (inverse error)
) * 100
```

### 등급 체계

| 점수 | 등급 | 상태 | 의미 |
|------|------|------|------|
| 90-100 | S | ✅ Excellent | 최상급, 개선 불필요 |
| 80-89 | A | ✔️ Good | 우수, 소폭 개선 |
| 70-79 | B | ⚠️ Acceptable | 양호, 개선 권장 |
| 60-69 | C | ⚠️ Acceptable | 보통, 개선 필요 |
| 50-59 | D | ❌ Needs Improvement | 미흡, 즉시 개선 |
| 0-49 | F | ❌ Needs Improvement | 불량, 긴급 개선 |

### 예시

```python
from evaluate_agent_performance import AgentEvaluator

evaluator = AgentEvaluator()

# Agent 평가
metrics = evaluator.get_agent_metrics("context7-engineer", days=7)

print(f"Score: {metrics.performance_score}/100")  # 85.2
print(f"Grade: {metrics.grade}")  # "A"
print(f"Status: {metrics.status}")  # "✔️ Good"
```

---

## 📈 사용 시나리오

### 시나리오 1: 신규 Agent 평가

```bash
# 1주일 사용 후 평가
python .claude/evolution/scripts/evaluate_agent_performance.py \
    --agent new-agent \
    --days 7 \
    --report

# 출력:
# Score: 72.5/100 (Grade: B)
# Status: ⚠️ Acceptable
#
# Recommendations:
# 1. Improve success rate (75% → 90%+)
# 2. Reduce avg duration (3.2s → 2s)
```

### 시나리오 2: Agent 비교

```bash
# Phase 0에서 3개 agent 비교
python .claude/evolution/scripts/evaluate_agent_performance.py \
    --compare \
    --phase "Phase 0"

# 출력:
# Agent                      Score    Grade  Status
# ========================================================
# context7-engineer          88.3     A      ✔️ Good
# seq-engineer               71.2     B      ⚠️ Acceptable
# backend-architect          84.5     A      ✔️ Good
#
# 🥇 Best: context7-engineer
```

### 시나리오 3: Baseline 설정

```bash
# 현재 성능을 baseline으로 설정
python .claude/evolution/scripts/evaluate_agent_performance.py \
    --agent context7-engineer \
    --baseline

# → config/context7-engineer-baseline.json 저장
# 향후 개선 전/후 비교 가능
```

### 시나리오 4: LLM-as-Judge 평가

```python
# Agent 출력 자동 평가
judge = LLMJudge()

with tracker.track("playwright-engineer", phase="Phase 2"):
    test_code = generate_e2e_tests()

# LLM Judge로 코드 품질 평가
score = judge.evaluate_code_quality(test_code, language="javascript")

# Langfuse에 score 기록
tracker.current_trace.score(
    name="llm_judge_quality",
    value=score.normalized_score,  # 0-1
    comment=score.reasoning
)
```

---

## 🎯 개선 권장 기준

### 자동 권장 액션

| 조건 | 권장 액션 | 우선순위 |
|------|----------|---------|
| Success rate < 80% | 실패 trace 분석, 에러 핸들링 개선 | 🔴 High |
| Avg duration > 3s | 캐싱, 병렬 처리, 최적화 | 🟡 Medium |
| User rating < 3.5/5 | 피드백 분석, instruction 개선 | 🔴 High |
| Error rate > 10% | 에러 로그 분석, retry 로직 추가 | 🔴 High |
| LLM Judge score < 6/10 | 출력 품질 개선, 프롬프트 튜닝 | 🟡 Medium |

### Phase 2 자동 개선 (향후)

```python
# PromptAgent로 자동 최적화
python .claude/evolution/scripts/optimize_agents.py --weekly

# 작동:
# 1. 성능 평가 (정량 + LLM Judge)
# 2. 낮은 점수 agent 식별
# 3. PromptAgent로 instruction 개선
# 4. A/B 테스트 (v1.0 vs v1.1)
# 5. 승자 자동 PR 생성
```

---

## 📊 대시보드 활용

### Langfuse에서 확인

**Traces**:
- Filter: `output.status = "success"`
- Group by: `metadata.agent`
- Metric: Avg duration

**Scores**:
- Filter: `scores.user_rating < 0.8`
- Sort by: Agent
- Identify: 개선 필요 agent

**Analytics**:
- Chart: Agent별 성공률 추이
- Chart: Phase별 평균 duration
- Chart: 시간에 따른 user rating 변화

---

## 🧪 테스트 & 검증

### 성능 메트릭 검증

```bash
# 1. 데모 실행 (시뮬레이션 데이터)
python .claude/evolution/scripts/example_integration.py

# 2. 성능 평가
python .claude/evolution/scripts/evaluate_agent_performance.py \
    --agent context7-engineer

# 3. LLM Judge 테스트
python .claude/evolution/scripts/llm_judge.py
```

---

## 📚 참고 자료

### 논문 & 연구

- **LLM-as-Judge**: [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685)
- **PromptAgent**: [Strategic Planning with LLMs](https://arxiv.org/abs/2310.16427)
- **AgentBench**: [Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688)

### 관련 도구

- **Langfuse**: https://langfuse.com/docs/scores
- **DeepEval**: https://github.com/confident-ai/deepeval
- **Opik**: https://github.com/comet-ml/opik

---

## 🔄 개선 로드맵

### Phase 1 (현재)
- ✅ 정량적 메트릭 수집
- ✅ LLM-as-Judge 구현
- ✅ 성능 점수 계산
- ✅ 등급 체계

### Phase 2 (2-3주)
- 🔜 PromptAgent 통합
- 🔜 자동 A/B 테스트
- 🔜 Baseline 비교
- 🔜 자동 개선 PR

### Phase 3 (1-2개월)
- 🔜 실시간 모니터링
- 🔜 알림 시스템 (성능 저하 감지)
- 🔜 트렌드 분석
- 🔜 예측 모델 (성능 예측)

---

## 💡 Best Practices

### 1. Baseline 설정
```bash
# 새 agent 추가 시 baseline 설정
python evaluate_agent_performance.py --agent new-agent --baseline
```

### 2. 주간 리뷰
```bash
# 매주 전체 agent 성능 확인
python evaluate_agent_performance.py --compare
```

### 3. 개선 전/후 비교
```python
# Before
metrics_before = evaluator.get_agent_metrics("agent", days=7)

# 개선 작업 (instruction 수정 등)

# After
metrics_after = evaluator.get_agent_metrics("agent", days=1)

improvement = metrics_after.performance_score - metrics_before.performance_score
print(f"Improvement: +{improvement:.1f} points")
```

### 4. LLM Judge 활용
```python
# 모든 agent 출력에 자동 적용
with tracker.track("agent", ...):
    output = agent.run()

    # 자동 품질 평가
    score = judge.evaluate_output(agent, task, output)

    tracker.current_trace.score(
        name="llm_judge",
        value=score.normalized_score
    )
```

---

**작성자**: Claude Code
**업데이트**: 2025-01-14
**버전**: 1.0.0
