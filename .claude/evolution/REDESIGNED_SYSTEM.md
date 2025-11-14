# Agent Quality System v2.0 (재설계)

**버전**: 2.0.0
**날짜**: 2025-01-14
**기반**: 비판적 분석 결과

---

## 🎯 설계 원칙

### 1. **Task별 독립 평가**
- Agent 전체가 아닌 Task별로 성공률 추적
- Task 간 누적 효과 제거

### 2. **시간 가중치**
- 최근 성능이 더 중요
- 과거 실패는 점차 용서

### 3. **통계적 유의성**
- 신뢰구간 표시
- 데이터 적을 때 "불확실" 명시

### 4. **객관적 측정**
- 자동 측정 우선 (테스트, 빌드)
- 주관적 판단 최소화

### 5. **복구 가능**
- "죽음" 메커니즘 없음
- 언제든 개선 가능

---

## 📊 핵심 데이터 구조

### Agent Quality Record

```json
{
  "agent": "debugger",
  "version": "1.0.0",
  "tasks": {
    "Fix TypeError in auth.ts": {
      "attempts": [
        {
          "timestamp": "2025-01-14T10:00:00Z",
          "status": "fail",
          "duration": 2.5,
          "error": "Cannot read property 'id' of undefined",
          "auto_detected": true
        },
        {
          "timestamp": "2025-01-14T10:30:00Z",
          "status": "pass",
          "duration": 1.8,
          "auto_detected": true
        }
      ],
      "statistics": {
        "total_attempts": 2,
        "successes": 1,
        "failures": 1,
        "success_rate": 0.5,
        "weighted_rate": 0.7,
        "avg_duration": 2.15,
        "last_status": "pass",
        "confidence": 0.4
      }
    }
  },
  "overall": {
    "total_tasks": 1,
    "avg_success_rate": 0.5,
    "weighted_avg": 0.7,
    "confidence": 0.4,
    "grade": "C",
    "status": "⚠️ Acceptable",
    "trend": "improving"
  }
}
```

---

## 🧮 점수 계산 알고리즘

### 1. Task별 성공률 (기본)

```python
def calculate_task_rate(attempts: List[Dict]) -> float:
    """단순 성공률"""
    if not attempts:
        return None

    successes = sum(1 for a in attempts if a['status'] == 'pass')
    return successes / len(attempts)
```

**예시**:
```python
attempts = [fail, fail, pass, pass, pass]
rate = 3 / 5 = 0.6 (60%)
```

---

### 2. 시간 가중 성공률 (권장)

```python
def calculate_weighted_rate(attempts: List[Dict]) -> float:
    """최근 데이터에 더 높은 가중치"""
    if not attempts:
        return None

    # 최근 N개만 고려 (예: 10개)
    recent = attempts[-10:]
    n = len(recent)

    # 지수 가중치 (최근일수록 높음)
    weights = [0.5 ** (n - i - 1) for i in range(n)]
    total_weight = sum(weights)

    # 가중 평균
    weighted_sum = sum(
        w * (1 if a['status'] == 'pass' else 0)
        for w, a in zip(weights, recent)
    )

    return weighted_sum / total_weight
```

**예시**:
```python
attempts = [fail, fail, fail, pass, pass]
# 오래된 실패 3개의 영향 감소
# 최근 성공 2개의 영향 증가

basic_rate = 2/5 = 0.40 (40%)
weighted_rate = 0.65 (65%)  # 개선 추세 반영
```

---

### 3. 신뢰구간 계산

```python
def calculate_confidence(attempts: List[Dict]) -> float:
    """데이터 신뢰도 (0-1)"""
    n = len(attempts)

    # Wilson score interval 기반
    # 간단 버전: 샘플 크기에 비례

    if n >= 20:
        return 1.0  # 100% 신뢰
    elif n >= 10:
        return 0.8
    elif n >= 5:
        return 0.6
    elif n >= 2:
        return 0.4
    else:
        return 0.2  # 데이터 부족
```

**예시**:
```python
1개 시도: confidence = 0.2 (매우 불확실)
5개 시도: confidence = 0.6 (보통)
20개 시도: confidence = 1.0 (확신)
```

---

### 4. Agent 전체 점수

```python
def calculate_agent_score(tasks: Dict) -> Dict:
    """Agent 전체 점수 = Task 점수들의 평균"""

    if not tasks:
        return {
            "avg_success_rate": None,
            "weighted_avg": None,
            "confidence": 0.0,
            "grade": "N/A",
            "status": "No data"
        }

    # Task별 가중 성공률들
    task_rates = []
    task_confidences = []

    for task, data in tasks.items():
        rate = data['statistics']['weighted_rate']
        conf = data['statistics']['confidence']

        if rate is not None:
            task_rates.append(rate)
            task_confidences.append(conf)

    if not task_rates:
        return {"avg_success_rate": None, ...}

    # 평균 성공률
    avg_rate = sum(task_rates) / len(task_rates)

    # 전체 신뢰도 = 평균 신뢰도
    avg_confidence = sum(task_confidences) / len(task_confidences)

    return {
        "avg_success_rate": avg_rate,
        "weighted_avg": avg_rate,  # 동일
        "confidence": avg_confidence,
        "grade": get_grade(avg_rate),
        "status": get_status(avg_rate),
        "total_tasks": len(task_rates)
    }

def get_grade(rate: float) -> str:
    """성공률 → 등급"""
    if rate >= 0.9: return "S"
    if rate >= 0.8: return "A"
    if rate >= 0.7: return "B"
    if rate >= 0.6: return "C"
    if rate >= 0.5: return "D"
    return "F"

def get_status(rate: float) -> str:
    """성공률 → 상태"""
    if rate >= 0.8: return "✅ Excellent"
    if rate >= 0.7: return "✔️ Good"
    if rate >= 0.6: return "⚠️ Acceptable"
    if rate >= 0.5: return "⚠️ Poor"
    return "❌ Critical"
```

---

### 5. 추세 분석

```python
def calculate_trend(attempts: List[Dict]) -> str:
    """성능 추세"""
    if len(attempts) < 4:
        return "insufficient_data"

    # 전반부 vs 후반부 비교
    mid = len(attempts) // 2
    first_half = attempts[:mid]
    second_half = attempts[mid:]

    first_rate = sum(1 for a in first_half if a['status'] == 'pass') / len(first_half)
    second_rate = sum(1 for a in second_half if a['status'] == 'pass') / len(second_half)

    diff = second_rate - first_rate

    if diff > 0.15:
        return "improving"
    elif diff < -0.15:
        return "declining"
    else:
        return "stable"
```

---

## 📝 로그 구조 (변경)

### 기존 (v1.0)
```jsonl
{"timestamp":"...","agent":"debugger","phase":"Phase 1","task":"Fix bug","attempt":1,"status":"fail","score":4.0}
```

**문제**:
- `score` 필드가 누적됨
- Task 독립성 없음

### 신규 (v2.0)
```jsonl
{"timestamp":"2025-01-14T10:00:00Z","agent":"debugger","version":"1.0.0","phase":"Phase 1","task":"Fix TypeError in auth.ts","status":"fail","duration":2.5,"error":"Cannot read property","auto_detected":true,"test_output":"FAILED tests/test_auth.py::test_login"}
```

**개선**:
- ✅ `score` 제거 (자동 계산)
- ✅ `version` 추가 (agent 버전 추적)
- ✅ `auto_detected` 추가 (자동/수동 측정 구분)
- ✅ `test_output` 추가 (객관적 증거)

---

## 🛠️ 사용 방법

### 서브 레포에서 기록

```bash
# v2.0 track script
python .claude/track2.py \
    --agent "debugger" \
    --version "1.0.0" \
    --phase "Phase 1" \
    --task "Fix TypeError in auth.ts" \
    --status "fail" \
    --duration 2.5 \
    --error "Cannot read property 'id'" \
    --auto-detected  # 자동 감지 (테스트 실패)
```

**또는 자동 감지**:
```bash
# pytest 후크
pytest tests/ --track-agent="test-automator"

# 테스트 실패 시 자동으로:
# .claude/track2.py --agent test-automator \
#     --task "Unit tests" \
#     --status fail \
#     --auto-detected \
#     --test-output "FAILED tests/test_foo.py"
```

---

## 📊 전역 레포에서 분석

### 동기화 (변경 없음)
```bash
python .claude/evolution/scripts/sync_quality_logs.py --all
```

### 분석 (새 출력 형식)
```bash
python .claude/evolution/scripts/analyze_quality2.py --agent debugger
```

**출력**:
```
📊 debugger - Quality Report (v2.0)

Overall Score: 0.75 ± 0.15 (Grade: B)
Status: ✔️ Good
Trend: improving
Confidence: 60% (12 attempts)

Task Breakdown:
┌──────────────────────────────────┬──────────┬────────┬────────────┬────────┐
│ Task                             │ Rate     │ Weight │ Confidence │ Trend  │
├──────────────────────────────────┼──────────┼────────┼────────────┼────────┤
│ Fix TypeError in auth.ts         │ 75%      │ 80%    │ 0.6        │ ↗️      │
│ Fix ReferenceError in api.ts     │ 80%      │ 85%    │ 0.8        │ →      │
│ Fix null pointer in utils.ts     │ 70%      │ 65%    │ 0.4        │ ↗️      │
└──────────────────────────────────┴──────────┴────────┴────────────┴────────┘

Recommendations:
1. ✅ Good overall performance
2. ⚠️  "Fix null pointer" needs more data (confidence: 40%)
3. 📈 Improving trend - keep up the good work

Recent Attempts (last 5):
  1. ✅ Fix TypeError in auth.ts (1.8s) - pass
  2. ✅ Fix ReferenceError in api.ts (2.1s) - pass
  3. ❌ Fix null pointer in utils.ts (3.5s) - fail: "undefined"
  4. ✅ Fix null pointer in utils.ts (2.2s) - pass
  5. ✅ Fix TypeError in auth.ts (1.5s) - pass
```

---

## 🔍 비교: v1.0 vs v2.0

### Scenario: 5번 실패 후 개선

**v1.0 (기존)**:
```
시도 1: fail → 4.0
시도 2: fail → 3.0
시도 3: fail → 2.0
시도 4: fail → 1.0
시도 5: fail → 0.0 💀 (죽음)

# 이후 10번 성공해도:
시도 6-15: pass → 여전히 0.0? 또는 5.0?
# 불명확, 복구 불가능
```

**v2.0 (재설계)**:
```
시도 1-5: fail → rate = 0/5 = 0% (Grade: F)
                   confidence = 0.6

# 이후 10번 성공:
시도 6-15: pass → rate = 10/15 = 67% (Grade: C)
                   weighted_rate = 85% (Grade: A)
                   confidence = 1.0

# 최근 10개만 보면:
recent_rate = 10/10 = 100% (Grade: S)

# → 복구 가능, 개선 추세 반영
```

---

### Scenario: 여러 Task 독립 평가

**v1.0 (기존)**:
```
Task A 실패: 5.0 → 4.0
Task B 실패: 4.0 → 3.0
Task C 실패: 3.0 → 2.0

# 문제: 세 Task가 완전히 다른데 점수가 누적
# A, B, C 각각의 품질을 알 수 없음
```

**v2.0 (재설계)**:
```
Task A: rate = 0/1 = 0% (confidence: 0.2)
Task B: rate = 0/1 = 0% (confidence: 0.2)
Task C: rate = 0/1 = 0% (confidence: 0.2)

Agent overall: avg = 0%, confidence = 0.2 (매우 불확실)

# 각 Task 재시도 후:
Task A: rate = 1/2 = 50%
Task B: rate = 0/2 = 0%  # 여전히 문제
Task C: rate = 1/2 = 50%

Agent overall: avg = 33%

# → Task별로 어디가 문제인지 명확
```

---

## 🎯 알림 시스템 (개선)

### v1.0 (기존)
```python
if score < 3.0:
    alert("Quality low")
```

**문제**: 컨텍스트 없음

### v2.0 (재설계)
```python
def check_alerts(agent_data):
    alerts = []

    # 1. 전체 성공률 낮음
    if agent_data['overall']['weighted_avg'] < 0.6:
        if agent_data['overall']['confidence'] >= 0.6:
            # 데이터 충분하고 실제로 낮음
            alerts.append({
                'level': 'urgent',
                'message': f"Success rate: {rate:.0%} (confident)",
                'action': 'Review all failed tasks'
            })
        else:
            # 데이터 부족
            alerts.append({
                'level': 'info',
                'message': f"Success rate: {rate:.0%} (uncertain)",
                'action': 'Collect more data'
            })

    # 2. 특정 Task 반복 실패
    for task, data in agent_data['tasks'].items():
        if data['statistics']['success_rate'] < 0.3:
            if data['statistics']['total_attempts'] >= 5:
                alerts.append({
                    'level': 'urgent',
                    'task': task,
                    'message': f"Task failing {data['statistics']['failures']}/{data['statistics']['total_attempts']} times",
                    'action': f"Review task: {task}"
                })

    # 3. 하락 추세
    if agent_data['overall']['trend'] == 'declining':
        alerts.append({
            'level': 'warning',
            'message': 'Performance declining',
            'action': 'Compare recent vs previous attempts'
        })

    return alerts
```

**출력**:
```
🚨 Alerts for debugger:

1. [URGENT] Task "Fix null pointer in utils.ts"
   Failing 4/5 times
   Action: Review this specific task

2. [WARNING] Performance declining
   Recent rate: 50% (was 80%)
   Action: Compare recent vs previous attempts
```

---

## 🔧 마이그레이션 가이드

### v1.0 → v2.0 전환

```bash
# 1. 기존 로그 변환
python .claude/evolution/scripts/migrate_v1_to_v2.py

# 작동:
# .agent-quality.jsonl (v1.0)
# → .agent-quality-v2.jsonl (v2.0)
# → 기존 데이터 보존, Task별 재구성

# 2. 새 스크립트 설치
cp .claude/evolution/templates/track2.py .claude/track.py
```

---

## 📈 예상 효과

| 지표 | v1.0 | v2.0 | 개선 |
|------|------|------|------|
| **Task 독립성** | ❌ 누적 | ✅ 독립 | 비교 가능 |
| **복구 가능성** | ❌ 0점=죽음 | ✅ 항상 가능 | 무한 개선 |
| **신뢰도 표시** | ❌ 없음 | ✅ 신뢰구간 | 통계적 |
| **추세 반영** | ❌ 없음 | ✅ 가중치 | 최근 중요 |
| **측정 객관성** | ⚠️ 주관적 | ✅ 자동 우선 | 신뢰성 ↑ |

---

## 💡 사용 예시

### Python API

```python
from agent_quality_v2 import AgentQuality

quality = AgentQuality("debugger", version="1.0.0")

# 기록
quality.record(
    task="Fix TypeError in auth.ts",
    status="fail",
    duration=2.5,
    error="Cannot read property 'id'",
    auto_detected=True
)

quality.record(
    task="Fix TypeError in auth.ts",
    status="pass",
    duration=1.8,
    auto_detected=True
)

# 점수 확인
score = quality.get_score()
print(f"Overall: {score['weighted_avg']:.0%} ± {1-score['confidence']:.0%}")
print(f"Grade: {score['grade']}")
print(f"Status: {score['status']}")
print(f"Trend: {score['trend']}")

# Task별 상세
for task, stats in score['tasks'].items():
    print(f"  {task}:")
    print(f"    Rate: {stats['success_rate']:.0%}")
    print(f"    Weighted: {stats['weighted_rate']:.0%}")
    print(f"    Confidence: {stats['confidence']:.0%}")
```

---

## 🚀 다음 단계

1. **v2.0 스크립트 구현** (3-4시간)
   - track2.py
   - analyze_quality2.py
   - migrate_v1_to_v2.py

2. **테스트** (1시간)
   - 시뮬레이션 데이터
   - Edge case 검증

3. **문서화** (30분)
   - 사용 가이드
   - 마이그레이션 가이드

4. **배포** (30분)
   - PR 업데이트
   - v1.0 deprecate 공지

---

**작성자**: Claude Code
**버전**: 2.0.0
**상태**: 설계 완료, 구현 대기
