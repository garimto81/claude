# Agent Evolution System Guide

**버전**: 1.0.0
**출처**: Langfuse (MIT License)
**적용**: claude01 15-agent plugin system

---

## 📋 개요

서브 에이전트와 스킬 사용 시 **피드백을 수집하고 분석**하여 자동으로 개선하는 진화 시스템

### 🎯 목적
- ✅ 모든 agent 사용 자동 추적 (Phase, Task, 시간, 비용)
- ✅ 사용자 피드백 수집 (평점, 코멘트, 개선 제안)
- ✅ 실시간 성능 분석 (대시보드)
- ✅ 데이터 기반 agent instruction 개선 (Phase 2)

### 📊 Phase 1 범위 (현재)
- Langfuse 설치 및 설정
- Agent 사용 추적 시스템
- 피드백 수집 시스템
- 대시보드 시각화

---

## 🚀 빠른 시작

### 1. Langfuse 설치 (Self-Hosted)

```bash
# 1. 설정 파일 생성
cd .claude/evolution
cp .env.example .env

# 2. 시크릿 생성 (Unix/macOS)
echo "NEXTAUTH_SECRET=$(openssl rand -base64 32)" >> .env
echo "SALT=$(openssl rand -base64 32)" >> .env

# Windows (PowerShell)
$secret = [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
Add-Content .env "NEXTAUTH_SECRET=$secret"

# 3. Admin 계정 설정
vim .env  # LANGFUSE_ADMIN_EMAIL, LANGFUSE_ADMIN_PASSWORD 변경

# 4. Langfuse 시작
docker-compose up -d

# 5. 대시보드 접속
# http://localhost:3000
# Login with admin credentials

# 6. API 키 발급
# Settings → API Keys → Create new key
# → .env에 LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY 추가
```

**출력**:
```
[+] Running 2/2
 ✔ Container langfuse-db      Started
 ✔ Container langfuse-server  Started
```

### 2. Python 클라이언트 설치

```bash
# 의존성 설치
pip install -r .claude/evolution/requirements.txt
```

### 3. Agent 추적 시작

```python
from .claude.evolution.scripts.track_agent_usage import get_tracker

tracker = get_tracker()

# Agent 실행 추적
with tracker.track("context7-engineer", phase="Phase 0", task="Verify React docs"):
    # Agent 실행
    result = verify_react_docs()

# 피드백 수집
tracker.collect_feedback(
    agent="context7-engineer",
    rating=5,
    comment="Docs verified correctly",
    effectiveness=0.95
)

tracker.flush()
```

---

## 📖 사용 방법

### 방법 1: 코드 통합 (권장)

```python
from .claude.evolution.scripts.track_agent_usage import track_agent

@track_agent("playwright-engineer", phase="Phase 2")
def run_e2e_tests():
    # E2E 테스트 실행
    return test_results
```

### 방법 2: CLI 피드백 수집

```bash
# Agent 사용 후 실행
python .claude/evolution/scripts/collect_feedback.py context7-engineer

# 대화형 모드
python .claude/evolution/scripts/collect_feedback.py context7-engineer --interactive

# 빠른 평점
python .claude/evolution/scripts/collect_feedback.py context7-engineer --rating 5

# 완전한 피드백
python .claude/evolution/scripts/collect_feedback.py context7-engineer \
    --rating 5 \
    --comment "Verified React 18 hooks correctly" \
    --effectiveness 9 \
    --suggestion "Add auto-retry for API failures"
```

### 방법 3: 컨텍스트 매니저

```python
tracker = get_tracker()

with tracker.track("debugger", phase="Phase 1", task="Fix TypeError"):
    # 디버깅 실행
    fix_error()

# 터미널에서 피드백 입력
tracker.prompt_feedback("debugger")
```

---

## 🏗️ 시스템 아키텍처

```
┌────────────────────────────────────────────┐
│  1. Agent 실행 (context7-engineer)          │
│     with tracker.track("context7", ...)    │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│  2. Langfuse Trace 생성                     │
│     - Trace ID                             │
│     - Agent name, Phase, Task              │
│     - Start time                           │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│  3. Agent 실행 완료                         │
│     - Duration 계산                         │
│     - Status (success/error)               │
│     - Output/Error 기록                    │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│  4. 피드백 수집 (선택)                       │
│     - User rating (1-5)                    │
│     - Comment                              │
│     - Effectiveness (0-1)                  │
│     - Improvement suggestions              │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│  5. Langfuse 대시보드                       │
│     - Agent별 성능 차트                     │
│     - Phase별 사용 패턴                     │
│     - 평균 duration, rating                │
│     - 에러율, 개선 제안 리스트              │
└────────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│  6. Phase 2: 자동 개선 (향후)               │
│     - PromptAgent로 instruction 최적화      │
│     - A/B 테스트                           │
│     - 자동 PR 생성                         │
└────────────────────────────────────────────┘
```

---

## 📊 대시보드 사용법

### 접속
```
http://localhost:3000
```

### 주요 메트릭

#### 1. Traces (실행 기록)
- 각 agent 실행 로그
- Duration, Status, Metadata
- 필터: Agent, Phase, Status, Date

#### 2. Scores (피드백)
- User rating (1-5)
- Effectiveness (0-1)
- Improvement suggestions

#### 3. Analytics
- Agent별 평균 duration
- Phase별 사용 빈도
- 에러율 추이
- 비용 분석 (향후)

### 유용한 쿼리

```
# Phase 0에서 context7-engineer 사용 횟수
metadata.agent = "context7-engineer" AND metadata.phase = "Phase 0"

# 평점 4점 이하 agent
scores.user_rating < 0.8

# 에러 발생한 agent
output.status = "error"

# 2초 이상 걸린 실행
output.duration_seconds > 2
```

---

## 💡 사용 시나리오

### 시나리오 1: 신규 Agent 테스트

```python
# 1. Agent 실행 추적
with tracker.track("new-agent", phase="Phase 1", task="Test new feature"):
    result = new_agent.run()

# 2. 터미널에서 피드백
tracker.prompt_feedback("new-agent")
# → 평점: 3
# → 코멘트: "결과는 좋으나 느림"
# → 효과성: 7/10
# → 제안: "캐싱 추가"

# 3. 대시보드 확인
# → new-agent 평균 rating: 3/5
# → 평균 duration: 5.2초
# → 개선 제안: "캐싱 추가"
```

### 시나리오 2: Phase별 성능 비교

```python
# Phase 0에서 5개 agent 사용
agents = ["context7", "seq", "backend-architect"]

for agent in agents:
    with tracker.track(agent, phase="Phase 0"):
        run_agent(agent)
    tracker.prompt_feedback(agent)

# 대시보드에서 확인:
# - Phase 0 평균 duration: 2.1초
# - 최고 평점: context7-engineer (4.8/5)
# - 개선 필요: seq-engineer (3.2/5)
```

### 시나리오 3: 에러 분석

```python
try:
    with tracker.track("playwright", phase="Phase 2", task="E2E test"):
        run_e2e_tests()
except Exception as e:
    # 에러 자동 기록됨
    pass

# 대시보드 필터:
# output.status = "error" AND metadata.agent = "playwright"
# → 최근 3회 중 2회 실패
# → 에러 메시지: "Timeout waiting for selector"
# → 제안: timeout 증가 필요
```

---

## 🔧 고급 설정

### Custom Metadata

```python
with tracker.track(
    "context7-engineer",
    phase="Phase 0",
    task="Verify React docs",
    metadata={
        "library": "React",
        "version": "18.2.0",
        "retry_count": 1,
        "cache_hit": False
    }
):
    result = verify_docs()
```

### Multiple Scores

```python
trace = tracker.track("debugger", phase="Phase 1")

# Task completion
trace.score(name="task_completion", value=1.0, comment="Bug fixed")

# Code quality
trace.score(name="code_quality", value=0.8, comment="Good but can improve")

# Time efficiency
trace.score(name="time_efficiency", value=0.6, comment="Took longer than expected")
```

### Session Tracking

```python
# 동일 세션에서 여러 agent 추적
tracker = AgentTracker()  # session_id 자동 생성

with tracker.track("agent1", phase="Phase 0"):
    pass

with tracker.track("agent2", phase="Phase 0"):
    pass

# 대시보드에서 session_id로 그룹화
```

---

## 🎓 Langfuse 개념

### Trace
- 최상위 실행 단위
- 하나의 agent 실행 = 하나의 trace
- Metadata: agent, phase, task, timestamp

### Span (향후)
- Trace 내부 단계
- 예: fetch → parse → analyze → response

### Score
- 평가 메트릭
- user_rating, effectiveness, task_completion 등
- 0-1 scale (정규화)

### Session
- 관련된 trace들의 그룹
- 예: 하나의 Phase에서 사용한 모든 agent

---

## 📊 Phase 2 계획: 자동 개선

### PromptAgent 통합 (향후)

```python
# 주간 최적화 실행
python .claude/evolution/scripts/optimize_agents.py --weekly

# 작동 방식:
# 1. Langfuse에서 피드백 데이터 수집
# 2. 평점 낮은 agent 식별
# 3. PromptAgent로 instruction 개선
# 4. A/B 테스트 (v1.0 vs v1.1)
# 5. 승자 자동 PR 생성

# 출력:
# 📊 분석 완료:
#   - context7-engineer: 평균 4.2/5 → 개선 불필요
#   - seq-engineer: 평균 3.1/5 → 개선 필요
#
# 🧬 Instruction 최적화 중...
#   seq-engineer v1.1 생성됨
#
# 🧪 A/B 테스트 (10회):
#   v1.0: 3.1/5
#   v1.1: 4.3/5 ✅
#
# 📝 PR 생성:
#   feat: Improve seq-engineer instruction (v1.1)
#   - 평균 rating: 3.1 → 4.3 (39% 향상)
#   - 사용자 피드백 반영
```

---

## ❓ FAQ

### Q1: Docker 없이 사용 가능한가요?
**A**: Langfuse Cloud 사용 가능 (유료)
```bash
# Langfuse Cloud 가입 후
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_HOST=https://cloud.langfuse.com
```

### Q2: 피드백 수집이 필수인가요?
**A**: 아니요, 선택 사항
- 최소: Agent 실행 추적만 (duration, status)
- 권장: 피드백 수집 (rating, comment)
- 최대: 세부 메트릭 + 개선 제안

### Q3: 대시보드를 외부에서 접속하려면?
**A**: docker-compose.yml 수정
```yaml
ports:
  - "0.0.0.0:3000:3000"  # 모든 인터페이스

# 또는 nginx reverse proxy 사용
```

### Q4: 데이터는 어디에 저장되나요?
**A**: PostgreSQL (Docker volume)
```bash
# 볼륨 위치
docker volume ls
# → langfuse-db-data

# 백업
docker exec langfuse-db pg_dump -U langfuse langfuse > backup.sql
```

### Q5: Phase 2는 언제 출시되나요?
**A**: Phase 1 안정화 후 (예상 2-3주)
- PromptAgent 통합
- 자동 instruction 최적화
- A/B 테스트 프레임워크
- 자동 PR 생성

---

## 🔗 참고 링크

- **Langfuse 공식**: https://langfuse.com/docs
- **GitHub**: https://github.com/langfuse/langfuse
- **PromptAgent 논문**: https://arxiv.org/abs/2310.16427
- **EvoAgentX**: https://github.com/EvoAgentX/EvoAgentX

---

## 🚀 다음 단계

1. ✅ Langfuse 설치 및 API 키 발급
2. ✅ Agent 5개로 테스트 실행
3. ✅ 1주일 데이터 수집
4. 🔜 Phase 2: PromptAgent 통합
5. 🔜 Phase 3: 자동 PR 워크플로우

---

**작성자**: Claude Code
**최종 업데이트**: 2025-01-14
**버전**: 1.0.0
**이슈**: [#16](https://github.com/garimto81/claude-code-config/issues/16)
