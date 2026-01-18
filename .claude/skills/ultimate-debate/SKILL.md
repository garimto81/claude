# Ultimate Debate Skill

**Version**: 1.0.0
**Type**: Cross-AI Consensus Verifier
**Status**: Phase 1 - Core Implementation

## 개요

3개 AI(Claude, GPT, Gemini)가 병렬 분석 → 교차 검토 → 합의 판정 → 재토론을 반복하여 최종 합의안을 도출하는 스킬입니다.

## 핵심 기능

| 기능 | 설명 |
|------|------|
| **병렬 분석** | 3 AI가 동시에 독립적으로 분석 |
| **교차 검토** | 서로의 분석 결과 리뷰 |
| **합의 판정** | 해시 기반 결론 비교로 합의 체크 |
| **재토론** | 불일치 시 근거 기반 토론 |
| **Context 관리** | MD 파일로 히스토리 저장 (메인 Context 절약) |

## 5-Phase 워크플로우

```
Phase 1: 병렬 분석 (3 AI 동시)
    ↓
Phase 2: 초기 합의 체크 (해시 비교)
    ↓
Phase 3: 교차 검토 (합의 실패 시)
    ↓
Phase 4: 재토론 (불일치 해결)
    ↓
Phase 5: 최종 전략 수립
```

## 디렉토리 구조

```
.claude/skills/ultimate-debate/
├── SKILL.md                    # 이 파일
├── requirements.txt            # 의존성
└── scripts/
    ├── __init__.py
    ├── main.py                 # CLI 엔트리포인트
    ├── debate/
    │   ├── __init__.py
    │   ├── orchestrator.py     # UltimateDebate 클래스
    │   ├── consensus_checker.py # ConsensusChecker 클래스
    │   └── context_manager.py  # DebateContextManager 클래스
    └── models/
        ├── __init__.py
        └── base_client.py      # BaseAIClient 추상 클래스
```

## 사용법

### CLI 사용

```bash
# 새 토론 시작
python .claude/skills/ultimate-debate/scripts/main.py --task "API 리팩토링 전략"

# 상태 확인
python .claude/skills/ultimate-debate/scripts/main.py --status --task-id debate_20260118_abc123

# 옵션 설정
python .claude/skills/ultimate-debate/scripts/main.py \
  --task "보안 감사" \
  --max-rounds 3 \
  --threshold 0.9 \
  --output text
```

### Python API 사용

```python
from debate import UltimateDebate

# 토론 인스턴스 생성
debate = UltimateDebate(
    task="API 성능 최적화 전략",
    max_rounds=5,
    consensus_threshold=0.8
)

# AI 클라이언트 등록 (Phase 2에서 구현 예정)
# debate.register_ai_client("claude", claude_client)
# debate.register_ai_client("gpt", gpt_client)
# debate.register_ai_client("gemini", gemini_client)

# 토론 실행
result = await debate.run()

# 결과 확인
print(f"Status: {result['status']}")
print(f"Consensus: {result['consensus_percentage'] * 100}%")
print(f"Final Strategy: {result['final_strategy']}")
```

## Context 관리 시스템

모든 토론 히스토리는 MD 파일로 저장되어 메인 Context를 절약합니다.

```
.claude/debates/{task_id}/
├── TASK.md                      # 초기 작업 설명
├── round_00/
│   ├── claude.md                # Claude 분석
│   ├── gpt.md                   # GPT 분석
│   ├── gemini.md                # Gemini 분석
│   ├── CONSENSUS.md             # 합의 결과
│   ├── reviews/
│   │   ├── claude_reviews_gpt.md
│   │   └── ...
│   └── debates/
│       ├── claude.md            # 재토론 입장
│       └── ...
├── round_01/
│   └── ...
└── FINAL.md                     # 최종 합의안
```

## 합의 판정 로직

### 해시 기반 비교

```python
# 각 AI의 결론을 정규화 후 해시 계산
conclusion_hash = sha256(normalize(conclusion))

# 동일 해시 개수로 합의율 계산
consensus_percentage = most_common_count / total_count

# 임계값 비교
if consensus_percentage >= 0.8:
    status = "FULL_CONSENSUS"
elif consensus_percentage >= 0.5:
    status = "PARTIAL_CONSENSUS"
else:
    status = "NO_CONSENSUS"
```

### 합의 상태

| 상태 | 조건 | 다음 액션 |
|------|------|-----------|
| `FULL_CONSENSUS` | ≥ 80% 일치 | None (종료) |
| `PARTIAL_CONSENSUS` | 50-80% 일치 | CROSS_REVIEW |
| `NO_CONSENSUS` | < 50% 일치 | DEBATE |

## 출력 형식

### JSON 출력 (기본)

```json
{
  "status": "FULL_CONSENSUS",
  "final_strategy": {
    "conclusion": "REST API를 GraphQL로 마이그레이션",
    "supporting_models": ["claude", "gpt", "gemini"],
    "confidence": 0.85
  },
  "total_rounds": 2,
  "consensus_percentage": 0.85,
  "task_id": "debate_20260118_abc123",
  "agreed_items": [...],
  "disputed_items": []
}
```

### Text 출력

```
status: FULL_CONSENSUS
final_strategy:
{
  "conclusion": "REST API를 GraphQL로 마이그레이션",
  "supporting_models": ["claude", "gpt", "gemini"],
  "confidence": 0.85
}
total_rounds: 2
consensus_percentage: 0.85
task_id: debate_20260118_abc123
```

## Phase 1 구현 범위

✅ **완료**
- 디렉토리 구조 생성
- 5-phase 오케스트레이터 (`orchestrator.py`)
- 합의 판정 로직 (`consensus_checker.py`)
- MD 기반 Context 관리 (`context_manager.py`)
- AI 클라이언트 인터페이스 (`base_client.py`)
- CLI 엔트리포인트 (`main.py`)
- Mock 데이터로 워크플로우 테스트 가능

❌ **미구현** (Phase 2 예정)
- 실제 AI 클라이언트 연동
- Multi-AI Auth 통합
- 병렬 실행 최적화
- 에러 핸들링 강화

## 제약 사항

1. **AI 클라이언트 미구현**: Phase 1에서는 Mock 데이터 사용
2. **Resume 기능 미구현**: `--resume` 옵션은 placeholder
3. **테스트 없음**: Phase 1에서는 단위 테스트 생략

## 다음 단계 (Phase 2)

1. Multi-AI Auth 스킬 연동
2. 실제 AI 클라이언트 구현 (Claude/GPT/Gemini)
3. 비동기 최적화 (asyncio.gather)
4. pytest 테스트 추가
5. 에러 핸들링 및 재시도 로직

## 기술 스택

| 항목 | 기술 |
|------|------|
| **언어** | Python 3.12+ |
| **비동기** | asyncio |
| **타입 힌트** | typing, dataclasses |
| **해싱** | hashlib (SHA-256) |
| **파일 저장** | pathlib, MD format |

## 관련 문서

- PRD: `tasks/prds/PRD-0035-multi-ai-consensus-verifier.md`
- Multi-AI Auth: `.claude/skills/multi-ai-auth/`
- Cross-AI Verifier: `.claude/skills/cross-ai-verifier/`

---

**Last Updated**: 2026-01-18
**Author**: Claude Code
**License**: MIT
