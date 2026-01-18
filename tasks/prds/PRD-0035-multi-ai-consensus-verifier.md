# PRD-0035: Multi-AI Consensus Verifier (Debate-Based)

**Version**: 2.0.0 | **Date**: 2026-01-18 | **Status**: Draft
**Priority**: P1 | **Type**: Enhancement
**Supersedes**: PRD-0031 (Multi-AI Auth - 인증 부분만)

---

## 1. Executive Summary

### 배경

현재 Cross-AI Verifier는 GPT와 Gemini가 **독립적으로 병렬 검증**하고 결과를 단순 병합합니다:

```
코드 → GPT → 결과 A
      → Gemini → 결과 B
      → 단순 병합 (중복 제거)
```

이 방식은 **각 AI의 강점을 최대화하지 못하고**, 의견 충돌 시 어떤 것이 정확한지 판단 기준이 없습니다.

### 제안 솔루션: Debate-Based Consensus

**3개의 AI가 구조화된 토론을 통해 합의된 하나의 개선안**을 도출합니다:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-AI Consensus Verifier                   │
│                                                                  │
│   Round 1: Initial Analysis (병렬)                               │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │ Claude 4.5  │  │ Gemini 3    │  │ GPT-5.2     │             │
│   │ (Opus)      │  │ Pro         │  │             │             │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│          │                │                │                     │
│          ▼                ▼                ▼                     │
│   ┌──────────────────────────────────────────────────┐          │
│   │  Round 2: Cross-Review (각 AI가 다른 AI 분석 검토) │          │
│   │  - 동의/반박/보완 의견 제시                         │          │
│   │  - 신뢰도 점수 부여                                 │          │
│   └──────────────────────────────────────────────────┘          │
│                            │                                     │
│                            ▼                                     │
│   ┌──────────────────────────────────────────────────┐          │
│   │  Round 3: Consensus Building                      │          │
│   │  - 합의 도출 또는 다수결                           │          │
│   │  - 불일치 항목 명시                                │          │
│   └──────────────────────────────────────────────────┘          │
│                            │                                     │
│                            ▼                                     │
│   ┌──────────────────────────────────────────────────┐          │
│   │  Final: Unified Improvement Proposal              │          │
│   │  ✅ 합의된 개선 사항                               │          │
│   │  ⚠️ 논쟁 중인 항목 (판단 근거 제시)                 │          │
│   └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 핵심 원칙 (리서치 기반)

| 원칙 | 출처 | 적용 |
|------|------|------|
| **Heterogeneous Agents** | [Multi-Agent Debate Survey](https://arxiv.org/html/2501.06322v1) | 동일 모델 반복 X, 다양한 AI 사용 |
| **Thought Signatures** | [Gemini 3 API](https://ai.google.dev/gemini-api/docs/gemini-3) | 추론 맥락 유지 |
| **Effort Parameter** | [Claude Opus 4.5](https://www.anthropic.com/news/claude-opus-4-5) | 작업별 추론 깊이 조절 |
| **Limited Debate Depth** | [DMAD Research](https://openreview.net/forum?id=t6QHYUOQL7) | 3라운드 이내 권장 |

### 예상 효과

| 지표 | 현재 (병렬 독립) | 목표 (토론 합의) |
|------|-----------------|-----------------|
| 이슈 정확도 | ~70% | **~90%** |
| False Positive 비율 | ~25% | **~8%** |
| 실행 가능한 제안 비율 | ~60% | **~95%** |
| 의견 충돌 해결률 | 0% (병합만) | **85%** |

---

## 2. 지원 AI 모델

### 2.1 모델별 역할

| AI 모델 | 역할 | 강점 | API |
|---------|------|------|-----|
| **Claude Opus 4.5** | Orchestrator + Reviewer | 80.9% SWE-bench, Effort 파라미터 | Anthropic API |
| **Gemini 3 Pro** | Code Analyst | 76.2% SWE-bench, Thought Signatures | Google AI API |
| **GPT-5.2** | Security & Bug Expert | 90%+ ARC-AGI-1, 45% 오류 감소 | OpenAI API |

### 2.2 모델별 최신 기능 활용

#### Claude Opus 4.5
```python
# Effort 파라미터로 추론 깊이 조절
response = await client.messages.create(
    model="claude-opus-4-5-20251101",
    effort="high",  # low | medium | high
    max_tokens=4000,
    messages=[...]
)
```

#### Gemini 3 Pro
```python
# Thought Signatures로 추론 맥락 유지
response = await client.generate_content(
    model="gemini-3-pro",
    thinking_level="high",  # 복잡한 태스크
    thought_signatures=previous_signatures,  # 이전 라운드 맥락
    contents=[...]
)
```

#### GPT-5.2
```python
# Reasoning 파라미터로 심층 분석
response = await client.chat.completions.create(
    model="gpt-5.2",
    reasoning="xhigh",  # 최고 품질 (새 기능)
    verbosity="detailed",
    messages=[...]
)
```

---

## 3. Debate Protocol

### 3.1 라운드 구조

```yaml
debate_protocol:
  max_rounds: 3
  consensus_threshold: 0.8  # 80% 동의 시 합의
  fallback:
    - majority_vote
    - claude_as_arbiter

  rounds:
    - name: "Initial Analysis"
      participants: [claude, gemini, gpt]
      parallel: true
      output: "individual_findings"

    - name: "Cross-Review"
      participants: [claude, gemini, gpt]
      parallel: false  # 순차 (이전 분석 참조)
      input: "all_initial_findings"
      output: "critiques_and_agreements"

    - name: "Consensus Building"
      orchestrator: claude
      input: "all_critiques"
      output: "unified_proposal"
```

### 3.2 라운드별 상세

#### Round 1: Initial Analysis (병렬)

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: 코드 + Focus (security/bugs/performance/all)        │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Claude 4.5   │    │ Gemini 3 Pro │    │ GPT-5.2      │
│              │    │              │    │              │
│ Focus:       │    │ Focus:       │    │ Focus:       │
│ - 아키텍처   │    │ - 코드 품질  │    │ - 보안/버그  │
│ - 패턴       │    │ - 성능       │    │ - 로직 오류  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────────────────────────────────────────────────┐
│  OUTPUT: 3개의 독립 분석 결과 (JSON)                      │
│  - issues: [{line, severity, message, confidence}]       │
│  - suggestions: [string]                                  │
│  - reasoning: string (분석 근거)                          │
└──────────────────────────────────────────────────────────┘
```

#### Round 2: Cross-Review (순차)

```python
for reviewer in [claude, gemini, gpt]:
    for analysis in [all_initial_analyses except reviewer's]:
        review = await reviewer.review(
            original_code=code,
            analysis=analysis,
            prompt="""
            다른 AI의 분석을 검토하세요:

            1. 동의하는 이슈: [리스트]
            2. 반박하는 이슈: [리스트 + 반박 근거]
            3. 추가 발견: [놓친 이슈]
            4. 신뢰도 점수: 0-100
            """
        )
```

**출력 예시**:
```json
{
  "reviewer": "claude",
  "reviewing": "gpt_analysis",
  "agreements": [
    {"issue_id": "GPT-001", "confidence": 95}
  ],
  "disagreements": [
    {
      "issue_id": "GPT-003",
      "reason": "이 코드 경로는 실제로 도달 불가능함",
      "evidence": "line 45에서 early return으로 차단됨"
    }
  ],
  "additions": [
    {"line": 78, "severity": "medium", "message": "잠재적 race condition"}
  ],
  "overall_confidence": 82
}
```

#### Round 3: Consensus Building

```python
# Claude가 Orchestrator로서 최종 합의 도출
consensus = await claude.build_consensus(
    all_analyses=initial_analyses,
    all_reviews=cross_reviews,
    prompt="""
    모든 분석과 리뷰를 종합하여 최종 합의안을 작성하세요:

    ## 합의된 이슈 (2개 이상 AI 동의)
    - 확정된 문제점과 수정 제안

    ## 논쟁 중인 이슈 (의견 분분)
    - 각 AI의 입장과 근거
    - 추천 판단 (있다면)

    ## 최종 개선 제안
    - 우선순위별 정리
    - 구체적 코드 수정안
    """
)
```

---

## 4. Context 관리 전략

### 4.1 Smart Router (하이브리드)

```python
class SmartConsensusRouter:
    """Context 최적화 라우터"""

    def route(self, request: str, code_size: int) -> str:
        """
        작업 복잡도에 따라 실행 경로 결정

        Returns:
            "single": 단일 AI (작은 코드)
            "parallel": 병렬 독립 검증 (중간)
            "debate": 전체 토론 프로토콜 (복잡)
        """
        if code_size < 50:
            return "single"  # Claude만 사용
        elif code_size < 200:
            return "parallel"  # 기존 방식
        else:
            return "debate"  # 전체 토론

    def select_models(self, focus: str) -> list[str]:
        """Focus에 따라 최적 모델 조합 선택"""
        FOCUS_MODELS = {
            "security": ["gpt-5.2", "claude-opus-4.5"],
            "bugs": ["gpt-5.2", "gemini-3-pro"],
            "performance": ["gemini-3-pro", "claude-opus-4.5"],
            "all": ["claude-opus-4.5", "gemini-3-pro", "gpt-5.2"],
        }
        return FOCUS_MODELS.get(focus, FOCUS_MODELS["all"])
```

### 4.2 Context 소비 비교

| 방식 | Main Context | API 호출 | 총 비용 |
|------|:-----------:|:--------:|:-------:|
| 단일 AI | 3% | 1회 | $0.01 |
| 병렬 독립 | 5% | 2-3회 | $0.05 |
| **토론 합의** | 8% | 7-9회 | $0.15 |

**비용-품질 트레이드오프**: 50줄 이상 코드 변경 시에만 토론 모드 권장

---

## 5. 구현 사양

### 5.1 디렉토리 구조

```
.claude/skills/cross-ai-verifier/
├── scripts/
│   ├── engines/
│   │   ├── verify_engine.py        # 기존 (유지)
│   │   └── consensus_engine.py     # 🆕 토론 엔진
│   ├── providers/
│   │   ├── router.py               # 수정: 토론 모드 추가
│   │   └── adapters/
│   │       ├── openai_adapter.py   # 수정: GPT-5.2 지원
│   │       ├── gemini_adapter.py   # 수정: Gemini 3 지원
│   │       └── claude_adapter.py   # 🆕 Claude API 어댑터
│   ├── debate/
│   │   ├── __init__.py
│   │   ├── protocol.py             # 🆕 토론 프로토콜
│   │   ├── round_manager.py        # 🆕 라운드 관리
│   │   └── consensus_builder.py    # 🆕 합의 도출
│   └── prompts/
│       ├── verify_prompt.py        # 기존 (유지)
│       └── debate_prompts.py       # 🆕 토론용 프롬프트
```

### 5.2 핵심 클래스

```python
# debate/protocol.py
from dataclasses import dataclass
from enum import Enum

class DebateRound(Enum):
    INITIAL = "initial_analysis"
    CROSS_REVIEW = "cross_review"
    CONSENSUS = "consensus_building"

@dataclass
class DebateConfig:
    max_rounds: int = 3
    consensus_threshold: float = 0.8
    timeout_per_round: int = 60  # seconds
    models: list[str] = None

    def __post_init__(self):
        if self.models is None:
            self.models = ["claude-opus-4.5", "gemini-3-pro", "gpt-5.2"]

@dataclass
class DebateResult:
    consensus_items: list[dict]
    disputed_items: list[dict]
    final_proposal: str
    confidence: float
    rounds_completed: int
    model_contributions: dict[str, int]
```

```python
# debate/consensus_builder.py
class ConsensusBuilder:
    """토론 결과에서 합의 도출"""

    def __init__(self, config: DebateConfig):
        self.config = config
        self.threshold = config.consensus_threshold

    def build(
        self,
        initial_analyses: list[dict],
        cross_reviews: list[dict]
    ) -> DebateResult:
        """
        합의 도출 알고리즘:
        1. 2개 이상 AI가 동의한 이슈 → 확정
        2. 1개 AI만 발견 + 다른 AI 반박 없음 → 잠정 확정
        3. 명시적 반박 있음 → 논쟁 중으로 분류
        """
        consensus = []
        disputed = []

        for issue in self._aggregate_issues(initial_analyses):
            agreements = self._count_agreements(issue, cross_reviews)
            disagreements = self._count_disagreements(issue, cross_reviews)

            if agreements >= 2:
                consensus.append({**issue, "status": "confirmed"})
            elif agreements == 1 and disagreements == 0:
                consensus.append({**issue, "status": "tentative"})
            else:
                disputed.append({
                    **issue,
                    "status": "disputed",
                    "arguments": self._collect_arguments(issue, cross_reviews)
                })

        return DebateResult(
            consensus_items=consensus,
            disputed_items=disputed,
            final_proposal=self._generate_proposal(consensus, disputed),
            confidence=len(consensus) / (len(consensus) + len(disputed)),
            rounds_completed=3,
            model_contributions=self._count_contributions(initial_analyses)
        )
```

### 5.3 CLI 인터페이스

```bash
# 기존 호환
/verify src/auth.py --focus security

# 토론 모드 (새 기능)
/verify src/auth.py --focus security --debate

# 모델 선택
/verify src/auth.py --models claude,gpt

# 상세 설정
/verify src/auth.py --debate --rounds 2 --threshold 0.7
```

---

## 6. 출력 형식

### 6.1 토론 모드 출력

```markdown
## 🔍 Multi-AI Consensus Verification

### 참여 모델
| AI | 역할 | 발견 이슈 |
|----|------|----------|
| Claude Opus 4.5 | Orchestrator | 3개 |
| Gemini 3 Pro | Analyst | 4개 |
| GPT-5.2 | Security Expert | 2개 |

---

### ✅ 합의된 이슈 (5개)

| # | 심각도 | 라인 | 설명 | 동의 |
|---|--------|------|------|------|
| 1 | 🔴 High | 45 | SQL Injection 취약점 | 3/3 |
| 2 | 🔴 High | 78 | 하드코딩된 비밀키 | 3/3 |
| 3 | 🟡 Medium | 120 | 입력 검증 누락 | 2/3 |
| 4 | 🟡 Medium | 156 | N+1 쿼리 패턴 | 2/3 |
| 5 | 🟢 Low | 200 | 불필요한 변수 | 2/3 |

---

### ⚠️ 논쟁 중인 이슈 (2개)

#### Issue #6: 라인 89 - 예외 처리 방식
| AI | 의견 | 근거 |
|----|------|------|
| Claude | ❌ 문제 아님 | FastAPI가 자동 처리 |
| Gemini | ⚠️ 경고 권장 | 명시적 처리가 안전 |
| GPT | ⚠️ 경고 권장 | 프로덕션에서 디버깅 어려움 |

**권장**: 명시적 예외 처리 추가 (2:1 다수결)

#### Issue #7: 라인 134 - 비동기 패턴
| AI | 의견 | 근거 |
|----|------|------|
| Claude | ✅ 개선 필요 | 블로킹 호출 |
| Gemini | ❌ 현재 적절 | I/O 바운드 아님 |
| GPT | ❓ 컨텍스트 부족 | 추가 정보 필요 |

**권장**: 사용자 판단 필요

---

### 📋 최종 개선 제안

#### 우선순위 1 (즉시 수정)
```python
# 라인 45: 파라미터화된 쿼리 사용
- query = f"SELECT * FROM users WHERE id = {user_id}"
+ query = "SELECT * FROM users WHERE id = ?"
+ cursor.execute(query, (user_id,))
```

#### 우선순위 2 (권장)
```python
# 라인 78: 환경변수로 이동
- SECRET_KEY = "hardcoded-secret-123"
+ SECRET_KEY = os.environ.get("SECRET_KEY")
```

---

### 📊 신뢰도
- 합의율: **71%** (5/7 이슈 합의)
- 평균 신뢰도: **87%**
```

---

## 7. 구현 일정

| Phase | 작업 | 예상 시간 |
|:-----:|------|:--------:|
| 1 | Claude Adapter 추가 | 2시간 |
| 2 | Gemini 3 / GPT-5.2 어댑터 업그레이드 | 3시간 |
| 3 | Debate Protocol 구현 | 4시간 |
| 4 | Consensus Builder 구현 | 3시간 |
| 5 | Smart Router 통합 | 2시간 |
| 6 | CLI 확장 + 출력 포맷 | 2시간 |
| 7 | 테스트 + 문서화 | 3시간 |

**총 예상 시간**: 19-22시간

---

## 8. 테스트 계획

### 8.1 토론 프로토콜 테스트

```python
async def test_debate_reaches_consensus():
    """3 AI가 동의하는 명확한 버그에서 합의 도달"""
    code = """
    def get_user(id):
        query = f"SELECT * FROM users WHERE id = {id}"  # SQL Injection
        return db.execute(query)
    """

    result = await consensus_engine.verify(code, focus="security")

    assert len(result.consensus_items) >= 1
    assert result.consensus_items[0]["severity"] == "high"
    assert result.confidence >= 0.8

async def test_debate_handles_disagreement():
    """의견 분분한 코드에서 논쟁 항목 분류"""
    code = """
    async def fetch_data():
        return requests.get(url)  # sync in async - 논쟁 가능
    """

    result = await consensus_engine.verify(code, focus="performance")

    # 논쟁 항목이 있어야 함
    assert len(result.disputed_items) >= 1
    # 각 AI의 의견이 기록되어야 함
    assert "arguments" in result.disputed_items[0]
```

### 8.2 성능 테스트

| 테스트 | 목표 |
|--------|------|
| 50줄 코드 토론 | < 30초 |
| 200줄 코드 토론 | < 90초 |
| API 실패 시 fallback | 정상 동작 |

---

## 9. 참조

### 리서치 기반

- [Patterns for Democratic Multi-Agent AI: Debate-Based Consensus](https://medium.com/@edoardo.schepis/patterns-for-democratic-multi-agent-ai-debate-based-consensus-part-1-8ef80557ff8a)
- [Multi-Agent Collaboration Mechanisms: A Survey of LLMs](https://arxiv.org/html/2501.06322v1)
- [Diverse Multi-Agent Debate (DMAD)](https://openreview.net/forum?id=t6QHYUOQL7)
- [Multi-Agent Collaboration via Evolving Orchestration](https://arxiv.org/html/2505.19591v1)

### AI 모델 API

- [Claude Opus 4.5 API](https://www.anthropic.com/news/claude-opus-4-5)
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [GPT-5.2 API](https://openai.com/index/introducing-gpt-5-2/)

---

## 10. 체크리스트

### 구현 체크리스트

- [ ] Claude Adapter 구현 (Effort 파라미터)
- [ ] Gemini 3 Adapter 업그레이드 (Thought Signatures)
- [ ] GPT-5.2 Adapter 업그레이드 (Reasoning xhigh)
- [ ] Debate Protocol 구현
- [ ] Round Manager 구현
- [ ] Consensus Builder 구현
- [ ] Smart Router 통합
- [ ] CLI --debate 옵션 추가
- [ ] 토론 결과 출력 포맷
- [ ] 테스트 작성
- [ ] 문서화

### 검증 체크리스트

- [ ] 3 AI 토론 E2E 테스트
- [ ] 합의 도달 테스트
- [ ] 논쟁 처리 테스트
- [ ] API 실패 fallback 테스트
- [ ] 성능 벤치마크

---

**이 PRD는 기존 Cross-AI Verifier를 확장하여 AI간 상호작용 기반의 합의 시스템으로 발전시킵니다.**
