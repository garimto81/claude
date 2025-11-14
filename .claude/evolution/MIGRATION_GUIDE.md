# Agent Quality System v1.0 → v2.0 Migration Guide

## 📋 목차

1. [변경 사항 요약](#변경-사항-요약)
2. [왜 v2.0으로 재설계했나?](#왜-v20으로-재설계했나)
3. [마이그레이션 방법](#마이그레이션-방법)
4. [새로운 사용법](#새로운-사용법)
5. [FAQ](#faq)

---

## 변경 사항 요약

### v1.0 (Deprecated)

```json
{
  "timestamp": "2025-01-14T10:30:00Z",
  "agent": "debugger",
  "task": "Fix TypeError",
  "status": "pass",
  "score": 4.5,  // ❌ 제거됨
  "duration": 1.5,
  "error": null
}
```

**문제점:**
- `score` 필드가 누적되어 서로 다른 Task의 실패가 쌓임
- 5.0에서 시작하여 0.0까지 떨어지면 영구 "사망"
- 쉬운 Task와 어려운 Task의 차이 무시
- 임의의 벌점 비율 (-1.0 실패, +0.5 수정)

### v2.0 (Current)

```json
{
  "timestamp": "2025-01-14T10:30:00Z",
  "agent": "debugger",
  "version": "1.0.0",  // ✅ 추가됨
  "task": "Fix TypeError",
  "status": "pass",
  // score 필드 없음 - 동적 계산
  "duration": 1.5,
  "error": null,
  "auto_detected": false
}
```

**개선사항:**
- Task별 독립 평가 (서로 다른 Task의 점수가 쌓이지 않음)
- 시간 가중치 (최근 성능이 더 중요)
- 통계적 신뢰구간 (샘플 수에 따라 신뢰도 계산)
- 항상 복구 가능 (영구 "사망" 없음)
- Agent 버전 추적

---

## 왜 v2.0으로 재설계했나?

### v1.0의 7가지 근본적 결함

#### 1. 초기 5.0 점수 모순
- **문제**: 한 번도 사용하지 않은 Agent = 완벽한 5.0점?
- **현실**: 신뢰도가 낮아야 함
- **v2.0**: 신뢰구간 기반 평가 (샘플 수 < 5 → 신뢰도 0.6 이하)

#### 2. 불가능한 회복
- **문제**: 0.0점 도달 → 영구 사망
- **현실**: 개선 가능해야 함
- **v2.0**: 항상 복구 가능 (최근 성능이 더 중요)

#### 3. 비논리적 누적
- **문제**: "Fix TypeError" 실패 → "Build project" 점수도 감소
- **현실**: Task는 독립적
- **v2.0**: Task별 독립 평가

#### 4. 맥락 무시
- **문제**: 쉬운 Task와 어려운 Task 동일 벌점
- **현실**: Task 난이도 차이 존재
- **v2.0**: Task별 통계, 추세 분석

#### 5. 주관적 측정
- **문제**: "통과"의 기준이 불명확
- **현실**: 객관적 측정 필요
- **v2.0**: `auto_detected` 플래그로 자동/수동 구분

#### 6. Goodhart's Law
- **문제**: "측정되면 게임이 된다"
- **현실**: 점수 올리기 위해 쉬운 Task만 시도
- **v2.0**: Task별 평가로 게임 불가능

#### 7. 임의의 벌점 비율
- **문제**: -1.0 / +0.5 비율의 근거 없음
- **현실**: 통계적 근거 필요
- **v2.0**: 시간 가중치 (지수 함수) + 베이지안 신뢰구간

### 상세 분석

📄 **[SYSTEM_CRITIQUE.md](./SYSTEM_CRITIQUE.md)** - 전체 비판 분석 문서

---

## 마이그레이션 방법

### 1단계: 백업 생성

```bash
# 기존 v1.0 로그 백업
cp .agent-quality.jsonl .agent-quality.jsonl.bak
```

### 2단계: Dry Run 테스트

```bash
cd .claude/evolution/scripts

# 테스트 실행 (실제 변환 안함)
python migrate_v1_to_v2.py --dry-run
```

예상 출력:
```
===========================================================
🔍 Dry Run - Migration Preview
===========================================================

총 로그: 150
마이그레이션: 150
스킵: 0

💡 실제 마이그레이션을 수행하려면 --dry-run 옵션을 제거하세요.
```

### 3단계: 실제 마이그레이션

```bash
# 백업과 함께 마이그레이션
python migrate_v1_to_v2.py --backup
```

예상 출력:
```
✅ 백업 생성: .agent-quality.jsonl.bak
===========================================================
✅ Migration Complete
===========================================================

총 로그: 150
마이그레이션: 150
스킵: 0

✅ v2.0 로그 파일이 생성되었습니다.
💡 이제 analyze_quality2.py를 사용하여 분석할 수 있습니다.
```

### 4단계: 검증

```bash
# v2.0 분석 도구로 확인
python analyze_quality2.py --summary
```

### 5단계: 서브 레포 .gitignore 업데이트

각 서브 레포의 `.gitignore`에 추가:

```gitignore
# Agent quality tracking
.agent-quality.jsonl       # v1.0 (deprecated)
.agent-quality-v2.jsonl    # v2.0 (current)
.agent-quality.jsonl.bak   # Backup files
```

---

## 새로운 사용법

### 기본 추적 (v2.0)

```bash
# templates/track2.py를 서브 레포에 복사
cp .claude/evolution/templates/track2.py .claude/track.py

# Agent 사용 기록
python .claude/track.py \
  --agent "debugger" \
  --task "Fix TypeError in auth.ts" \
  --status "pass" \
  --duration 1.5
```

출력:
```
✅ Logged: debugger - Fix TypeError in auth.ts (PASS)
   Duration: 1.50s
   Task Score: 70% (confidence: 60%)
```

### 전체 요약

```bash
python analyze_quality2.py --summary
```

출력:
```
======================================================================
📊 Agent Quality Summary (v2.0)
======================================================================

Agent                     Version    Score    Conf   Grade  Status
----------------------------------------------------------------------
debugger                  1.0.0      75±20%   0.8    B      ✔️ Good
test-automator            1.0.0      85±15%   0.8    A      ✅ Excellent
frontend-developer        1.2.0      92±8%    1.0    S      ✅ Excellent

전체 통계:
  총 시도: 150
  성공: 120
  실패: 30
  전체 성공률: 80.0%
  기간: 2025-01-01 ~ 2025-01-14
```

### 특정 Agent 상세 분석

```bash
python analyze_quality2.py --agent debugger
```

출력:
```
============================================================
📊 debugger v1.0.0 - Quality Report (v2.0)
============================================================

Overall Score: 75% ± 20% (Grade: B)
Status: ✔️ Good
Trend: improving
Confidence: 80% (50 total attempts)

Task Breakdown:
Task                                     Rate     Weight   Conf   Trend
--------------------------------------------------------------------------------
Fix TypeError                            50%      70%      0.6    ↗️ improving
Fix ReferenceError                       100%     100%     0.4    → stable
Build project                            80%      85%      0.8    → stable
```

### 추세 분석

```bash
python analyze_quality2.py --trend
```

출력:
```
======================================================================
📈 Trend Analysis
======================================================================

날짜별 성공률:
Date         Success Rate    Attempts
----------------------------------------
2025-01-10   60.0% ████████████         (10)
2025-01-11   70.0% ██████████████       (15)
2025-01-12   85.0% █████████████████    (20)
2025-01-13   90.0% ██████████████████   (22)

Agent별 추세:
Agent                     Trend           Recent Rate
-------------------------------------------------------
debugger                  ↗️ Improving    90.0%
test-automator            → Stable        85.0%
frontend-developer        → Stable        92.0%
```

### 경고 확인

```bash
python analyze_quality2.py --alerts
```

출력:
```
======================================================================
⚠️ Quality Alerts
======================================================================

Agent                     Score      Grade  Status          Trend
----------------------------------------------------------------------
database-optimizer        55.0%      D      ⚠️ Poor         ↘️ declining

💡 database-optimizer의 성능이 기준(60%) 이하입니다.
```

---

## v1.0 vs v2.0 비교표

| 항목 | v1.0 | v2.0 |
|------|------|------|
| **점수 계산** | 누적 (5.0 → 0.0) | Task별 독립 평가 |
| **가중치** | 없음 | 시간 가중 (최근 중요) |
| **신뢰구간** | 없음 | Wilson score 기반 |
| **복구 가능** | ❌ (0.0 = 사망) | ✅ (항상 가능) |
| **Task 독립성** | ❌ (누적) | ✅ (독립 평가) |
| **버전 추적** | ❌ | ✅ |
| **추세 분석** | ❌ | ✅ (improving/stable/declining) |
| **등급 시스템** | ❌ | ✅ (S/A/B/C/D/F) |
| **객관성** | 주관적 | `auto_detected` 플래그 |

---

## FAQ

### Q1: 기존 v1.0 로그는 어떻게 되나요?

**A:** `migrate_v1_to_v2.py`로 자동 변환됩니다. `score` 필드는 제거되고 `version` 필드가 추가됩니다.

### Q2: v1.0과 v2.0을 동시에 사용할 수 있나요?

**A:** 권장하지 않습니다. v2.0으로 완전히 전환하는 것이 좋습니다. 두 시스템의 점수 계산 방식이 완전히 다릅니다.

### Q3: v2.0에서 점수가 더 낮게 나오는데요?

**A:** v2.0은 통계적으로 더 정확합니다. v1.0은 초기 5.0점에서 시작하여 비현실적으로 높은 점수를 보였습니다. v2.0은 실제 성과를 반영합니다.

### Q4: 신뢰구간(confidence)이란?

**A:** 샘플 수에 따른 신뢰도입니다:
- 20회 이상: 1.0 (매우 신뢰)
- 10-19회: 0.8 (신뢰)
- 5-9회: 0.6 (보통)
- 2-4회: 0.4 (낮음)
- 0-1회: 0.2 (매우 낮음)

### Q5: 시간 가중치는 어떻게 계산되나요?

**A:** 최근 10개 시도에 대해 지수 가중치를 적용합니다:

```python
weights = [0.5 ** (n - i - 1) for i in range(n)]
# 예: [0.5^0, 0.5^1, 0.5^2, ..., 0.5^9]
# = [1.0, 0.5, 0.25, 0.125, ...]
```

가장 최근 시도가 가장 높은 가중치(1.0)를 받습니다.

### Q6: Task별 평가는 어떻게 작동하나요?

**A:** 각 Task는 독립적으로 평가됩니다:

```
Agent: debugger
  Task: "Fix TypeError" → 70% (10회 시도)
  Task: "Fix ReferenceError" → 100% (5회 시도)
  Overall: (70% + 100%) / 2 = 85%
```

### Q7: 추세(trend)는 어떻게 판단하나요?

**A:** 전반부와 후반부의 성공률을 비교합니다:

- 차이 > +15%: `improving` ↗️
- 차이 < -15%: `declining` ↘️
- 그 외: `stable` →

### Q8: Grade 등급 기준은?

**A:**
- S: 90% 이상
- A: 80-89%
- B: 70-79%
- C: 60-69%
- D: 50-59%
- F: 50% 미만

### Q9: v1.0 파일을 삭제해도 되나요?

**A:** 마이그레이션 후 백업(`.bak`)을 보관하고 원본은 삭제해도 됩니다:

```bash
# 마이그레이션 확인 후
rm .agent-quality.jsonl
# 백업은 보관
ls .agent-quality.jsonl.bak  # ✅
```

### Q10: 전역 레포에서 분석하려면?

**A:** v2.0도 sync 스크립트를 지원합니다 (향후 업데이트 예정):

```bash
# 각 서브 레포의 v2.0 로그 수집
python .claude/evolution/scripts/sync_quality_logs_v2.py

# 전역 분석
python .claude/evolution/scripts/analyze_quality2.py --summary
```

---

## 관련 문서

- **[SYSTEM_CRITIQUE.md](./SYSTEM_CRITIQUE.md)** - v1.0 시스템 비판 분석
- **[REDESIGNED_SYSTEM.md](./REDESIGNED_SYSTEM.md)** - v2.0 시스템 설계 명세
- **[agent_quality_v2.py](./scripts/agent_quality_v2.py)** - v2.0 핵심 로직
- **[track2.py](./templates/track2.py)** - v2.0 사용자 스크립트
- **[analyze_quality2.py](./scripts/analyze_quality2.py)** - v2.0 분석 도구
- **[migrate_v1_to_v2.py](./scripts/migrate_v1_to_v2.py)** - 마이그레이션 스크립트

---

**Version**: 2.0.0
**Last Updated**: 2025-01-14
**Status**: ✅ Production Ready
