# Prompt Learning 개발 가이드

**버전**: 1.0.0
**관련 이슈**: [#9](https://github.com/garimto81/archive-analyzer/issues/9)
**기술 스택**: DSPy + Claude Hook + TextGrad + LangGraph

---

## 1. 개요

### 1.1 Prompt Learning이란?

강화 학습(RL)에서 영감을 받아, 에이전트의 출력 성능을 바탕으로 시스템 프롬프트(CLAUDE.md)를 지속적으로 개선하는 최적화 방법입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    Prompt Learning Loop                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│   │ CLAUDE.md│───▶│  Claude  │───▶│  Output  │             │
│   │ (Prompt) │    │   Code   │    │ (Result) │             │
│   └────▲─────┘    └──────────┘    └────┬─────┘             │
│        │                               │                    │
│        │         ┌──────────┐          │                    │
│        └─────────│ Feedback │◀─────────┘                    │
│                  │   LLM    │                               │
│                  └──────────┘                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 목표

| 지표 | 현재 | 목표 | 개선율 |
|------|------|------|--------|
| Phase 검증 준수율 | 60% | 85% | +25%p |
| 태스크 완료 시간 | 100% | 85% | -15% |
| 토큰 비용 | 100% | 80% | -20% |

---

## 2. 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                     Prompt Learning System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Claude Hook    │  │     DSPy        │  │    TextGrad     │ │
│  │  (Real-time)    │  │  (Compile-time) │  │   (Test-time)   │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ - 규칙 위반 감지 │  │ - Phase 검증기  │  │ - 에이전트 최적화│ │
│  │ - 즉시 피드백   │  │ - Few-shot 생성 │  │ - 텍스트 그래디언트│
│  │ - 0 토큰 오버헤드│  │ - A/B 테스트    │  │ - 반복 개선     │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │          │
│           └────────────────────┼────────────────────┘          │
│                                ▼                                │
│                    ┌─────────────────────┐                     │
│                    │   CLAUDE.md         │                     │
│                    │   Updater           │                     │
│                    └─────────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 모듈 구조

```
src/agents/prompt_learning/
├── __init__.py
├── session_parser.py       # .jsonl 세션 로그 파싱
├── failure_analyzer.py     # 실패 원인 분석
├── pattern_detector.py     # 반복 패턴 감지
├── dspy_optimizer.py       # DSPy 기반 최적화
├── textgrad_optimizer.py   # TextGrad 기반 최적화
├── claude_md_updater.py    # CLAUDE.md 자동 업데이트
└── metrics.py              # 성능 측정

.claude/hooks/
└── claude-md-validator.py  # 실시간 검증 Hook
```

---

## 3. Phase 1: Claude Hook 검증기

### 3.1 Hook 구현

```python
# .claude/hooks/claude-md-validator.py
"""
CLAUDE.md 규칙 실시간 검증 Hook

UserPromptSubmit 이벤트를 인터셉트하여 규칙 위반 감지
"""

import json
import sys
import re
from typing import list

# CLAUDE.md 핵심 규칙
RULES = {
    "absolute_path": {
        "pattern": r'(?:^|\s)\.\/|(?:^|\s)cd\s+(?!\/|[A-Z]:)',
        "message": "절대 경로 사용 필요 (CLAUDE.md Section 1.2)",
        "severity": "high"
    },
    "skip_validation": {
        "pattern": r'skip\s+(?:phase\s+)?validation|validation\s+skip',
        "message": "Phase 검증 생략 불가 (CLAUDE.md Section 3)",
        "severity": "critical"
    },
    "tdd_order": {
        "pattern": r'implement.*(?:without|before|skip).*test',
        "message": "TDD: 테스트 먼저 작성 (CLAUDE.md Section 9)",
        "severity": "high"
    },
    "korean_output": {
        "pattern": r'(?:respond|answer|output)\s+(?:in\s+)?english',
        "message": "사용자 출력은 한글로 (CLAUDE.md Section 1.1)",
        "severity": "medium"
    }
}


def validate_prompt(prompt: str) -> list[dict]:
    """프롬프트에서 CLAUDE.md 규칙 위반 검사"""
    violations = []

    for rule_id, rule in RULES.items():
        if re.search(rule["pattern"], prompt, re.IGNORECASE):
            violations.append({
                "rule_id": rule_id,
                "message": rule["message"],
                "severity": rule["severity"]
            })

    return violations


def format_feedback(violations: list[dict]) -> str:
    """위반 사항을 사용자 친화적 메시지로 변환"""
    if not violations:
        return None

    severity_icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }

    lines = ["**CLAUDE.md 규칙 위반 감지:**\n"]
    for v in violations:
        icon = severity_icons.get(v["severity"], "⚪")
        lines.append(f"{icon} {v['message']}")

    return "\n".join(lines)


def main():
    """Hook 진입점"""
    # stdin에서 프롬프트 읽기
    input_data = json.loads(sys.stdin.read())
    prompt = input_data.get("prompt", "")

    # 검증 실행
    violations = validate_prompt(prompt)

    if violations:
        # Critical 위반이 있으면 차단
        critical = [v for v in violations if v["severity"] == "critical"]

        if critical:
            output = {
                "action": "block",
                "message": format_feedback(violations)
            }
        else:
            # 경고만 표시하고 진행 허용
            output = {
                "action": "warn",
                "message": format_feedback(violations)
            }
    else:
        output = {"action": "proceed"}

    print(json.dumps(output))


if __name__ == "__main__":
    main()
```

### 3.2 Hook 등록

```json
// .claude/settings.json에 추가
{
  "hooks": {
    "UserPromptSubmit": {
      "command": "python .claude/hooks/claude-md-validator.py",
      "timeout": 5000
    }
  }
}
```

### 3.3 테스트

```python
# tests/test_claude_md_validator.py
import pytest
from claude.hooks.claude_md_validator import validate_prompt

def test_absolute_path_violation():
    violations = validate_prompt("cd ./src && run tests")
    assert len(violations) == 1
    assert violations[0]["rule_id"] == "absolute_path"

def test_skip_validation_blocked():
    violations = validate_prompt("skip phase validation and proceed")
    assert any(v["severity"] == "critical" for v in violations)

def test_clean_prompt_passes():
    violations = validate_prompt("D:\\AI\\claude01\\src 파일을 분석해주세요")
    assert len(violations) == 0
```

---

## 4. Phase 2: DSPy 통합

### 4.1 설치

```bash
pip install dspy-ai anthropic
```

### 4.2 Phase 검증기 Signature 정의

```python
# src/agents/prompt_learning/dspy_optimizer.py
"""
DSPy 기반 Phase 검증기 최적화
"""

import dspy
from dspy.teleprompt import MIPROv2, BootstrapFewShot


# Claude 모델 설정
lm = dspy.LM("anthropic/claude-sonnet-4-20250514")
dspy.settings.configure(lm=lm)


# Phase 0: PRD 검증 Signature
class PRDValidator(dspy.Signature):
    """PRD 문서가 8개 필수 섹션을 포함하는지 검증"""

    prd_content: str = dspy.InputField(desc="PRD 문서 전체 내용")
    validation_result: bool = dspy.OutputField(desc="True if valid, False otherwise")
    missing_sections: list[str] = dspy.OutputField(desc="누락된 섹션 목록")
    suggestions: str = dspy.OutputField(desc="개선 제안")


# Phase 1: TDD 검증 Signature
class TDDValidator(dspy.Signature):
    """TDD 순서(Red-Green-Refactor) 준수 검증"""

    commit_history: str = dspy.InputField(desc="최근 커밋 히스토리")
    file_changes: str = dspy.InputField(desc="변경된 파일 목록")
    tdd_compliant: bool = dspy.OutputField(desc="TDD 순서 준수 여부")
    violations: list[str] = dspy.OutputField(desc="위반 사항")


# Phase 2: 테스트 커버리지 Signature
class CoverageValidator(dspy.Signature):
    """테스트 커버리지 검증"""

    coverage_report: str = dspy.InputField(desc="커버리지 리포트")
    threshold: float = dspy.InputField(desc="최소 커버리지 임계값")
    passes_threshold: bool = dspy.OutputField(desc="임계값 통과 여부")
    uncovered_files: list[str] = dspy.OutputField(desc="커버리지 미달 파일")


# 검증기 모듈
class PhaseValidatorModule(dspy.Module):
    """Phase 0-6 통합 검증 모듈"""

    def __init__(self):
        super().__init__()
        self.prd_validator = dspy.ChainOfThought(PRDValidator)
        self.tdd_validator = dspy.ChainOfThought(TDDValidator)
        self.coverage_validator = dspy.ChainOfThought(CoverageValidator)

    def forward(self, phase: int, **kwargs):
        if phase == 0:
            return self.prd_validator(**kwargs)
        elif phase == 1:
            return self.tdd_validator(**kwargs)
        elif phase == 2:
            return self.coverage_validator(**kwargs)
        else:
            raise ValueError(f"Unknown phase: {phase}")
```

### 4.3 최적화 실행

```python
# scripts/optimize_phase_validators.py
"""
Phase 검증기 자동 최적화 스크립트
"""

from src.agents.prompt_learning.dspy_optimizer import (
    PhaseValidatorModule, PRDValidator
)
from dspy.teleprompt import MIPROv2
import dspy


def load_training_examples():
    """기존 PRD 예시 로드"""
    import glob

    examples = []
    for prd_file in glob.glob("tasks/prds/*.md"):
        with open(prd_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 수동으로 라벨링된 예시 (실제로는 DB나 파일에서 로드)
        examples.append(dspy.Example(
            prd_content=content,
            validation_result=True,
            missing_sections=[],
            suggestions=""
        ).with_inputs("prd_content"))

    return examples


def prd_quality_metric(example, prediction, trace=None):
    """PRD 품질 평가 메트릭"""
    # 정확도 점수
    correct = example.validation_result == prediction.validation_result

    # 섹션 감지 정확도
    if hasattr(example, 'missing_sections') and hasattr(prediction, 'missing_sections'):
        section_match = set(example.missing_sections) == set(prediction.missing_sections)
    else:
        section_match = True

    return correct and section_match


def optimize():
    """MIPROv2로 최적화 실행"""
    # 학습 데이터 로드
    trainset = load_training_examples()

    if len(trainset) < 10:
        print("경고: 학습 예시가 10개 미만입니다. 더 많은 예시 권장.")

    # 기본 모듈 생성
    module = PhaseValidatorModule()

    # MIPROv2 옵티마이저
    optimizer = MIPROv2(
        metric=prd_quality_metric,
        num_candidates=7,
        init_temperature=1.0
    )

    # 컴파일 (최적화)
    optimized_module = optimizer.compile(
        module,
        trainset=trainset,
        num_batches=10,
        max_bootstrapped_demos=3,
        max_labeled_demos=5
    )

    # 최적화된 모듈 저장
    optimized_module.save("models/optimized_phase_validator.json")

    print("최적화 완료! 저장 위치: models/optimized_phase_validator.json")

    return optimized_module


if __name__ == "__main__":
    optimize()
```

### 4.4 A/B 테스트

```python
# scripts/ab_test_validators.py
"""
최적화 전/후 A/B 테스트
"""

import random
from src.agents.prompt_learning.dspy_optimizer import PhaseValidatorModule


def run_ab_test(test_cases: list, num_trials: int = 100):
    """A/B 테스트 실행"""

    # 기본 모듈
    baseline = PhaseValidatorModule()

    # 최적화된 모듈
    optimized = PhaseValidatorModule()
    optimized.load("models/optimized_phase_validator.json")

    baseline_scores = []
    optimized_scores = []

    for _ in range(num_trials):
        test_case = random.choice(test_cases)

        # 기본 모듈 평가
        baseline_result = baseline.forward(phase=0, prd_content=test_case["content"])
        baseline_correct = baseline_result.validation_result == test_case["expected"]
        baseline_scores.append(1 if baseline_correct else 0)

        # 최적화 모듈 평가
        optimized_result = optimized.forward(phase=0, prd_content=test_case["content"])
        optimized_correct = optimized_result.validation_result == test_case["expected"]
        optimized_scores.append(1 if optimized_correct else 0)

    # 결과 출력
    baseline_acc = sum(baseline_scores) / len(baseline_scores)
    optimized_acc = sum(optimized_scores) / len(optimized_scores)
    improvement = (optimized_acc - baseline_acc) / baseline_acc * 100

    print(f"Baseline 정확도: {baseline_acc:.2%}")
    print(f"Optimized 정확도: {optimized_acc:.2%}")
    print(f"개선율: {improvement:+.1f}%")

    return {
        "baseline": baseline_acc,
        "optimized": optimized_acc,
        "improvement": improvement
    }
```

---

## 5. Phase 3: TextGrad 적용

### 5.1 설치

```bash
pip install textgrad
```

### 5.2 에이전트 프롬프트 최적화

```python
# src/agents/prompt_learning/textgrad_optimizer.py
"""
TextGrad 기반 에이전트 프롬프트 최적화
"""

import textgrad as tg
from pathlib import Path


def optimize_agent_prompt(agent_name: str, test_cases: list[dict]):
    """
    특정 에이전트의 프롬프트를 TextGrad로 최적화

    Args:
        agent_name: 에이전트 이름 (예: "code-reviewer")
        test_cases: 테스트 케이스 목록
    """

    # 에이전트 프롬프트 로드
    agent_path = Path(f".claude/agents/{agent_name}.md")
    with open(agent_path, "r", encoding="utf-8") as f:
        original_prompt = f.read()

    # TextGrad 변수로 변환
    agent_prompt = tg.Variable(
        value=original_prompt,
        role_description=f"{agent_name} agent system prompt",
        requires_grad=True
    )

    # 손실 함수 정의
    loss_fn = tg.TextLoss(
        f"""
        이 에이전트 프롬프트를 평가하세요:
        1. 역할이 명확한가?
        2. 출력 형식이 구체적인가?
        3. 에러 처리 지침이 있는가?
        4. 예시가 포함되어 있는가?

        0-100 점수와 개선 제안을 제공하세요.
        """
    )

    # 옵티마이저 설정
    optimizer = tg.TGD(
        parameters=[agent_prompt],
        lr=0.1
    )

    # 최적화 루프
    for iteration in range(3):
        total_loss = 0

        for test_case in test_cases:
            # 테스트 실행
            response = simulate_agent_response(agent_prompt.value, test_case["input"])

            # 손실 계산
            loss = loss_fn(response)
            total_loss += loss

        # 역전파
        total_loss.backward()

        # 그래디언트 확인
        print(f"\n=== Iteration {iteration + 1} ===")
        print(f"Textual Gradient:\n{agent_prompt.gradients}")

        # 업데이트
        optimizer.step()
        optimizer.zero_grad()

    # 최적화된 프롬프트 저장
    optimized_path = Path(f".claude/agents/{agent_name}.optimized.md")
    with open(optimized_path, "w", encoding="utf-8") as f:
        f.write(agent_prompt.value)

    print(f"\n최적화 완료! 저장 위치: {optimized_path}")

    return agent_prompt.value


def simulate_agent_response(prompt: str, input_text: str) -> str:
    """에이전트 응답 시뮬레이션 (실제로는 Claude API 호출)"""
    # TODO: 실제 Claude API 연동
    return f"[Simulated response for: {input_text[:50]}...]"
```

### 5.3 배치 최적화

```python
# scripts/optimize_all_agents.py
"""
모든 에이전트 프롬프트 일괄 최적화
"""

from pathlib import Path
from src.agents.prompt_learning.textgrad_optimizer import optimize_agent_prompt


def optimize_all():
    """33개 에이전트 프롬프트 일괄 최적화"""

    agents_dir = Path(".claude/agents")
    agent_files = list(agents_dir.glob("*.md"))

    # 공통 테스트 케이스
    common_test_cases = [
        {"input": "복잡한 기능을 구현해주세요", "expected": "명확한 단계별 응답"},
        {"input": "에러가 발생했습니다", "expected": "디버깅 가이드"},
        {"input": "코드를 리뷰해주세요", "expected": "구조화된 피드백"},
    ]

    results = {}

    for agent_file in agent_files:
        agent_name = agent_file.stem

        # .optimized 파일은 제외
        if ".optimized" in agent_name:
            continue

        print(f"\n{'='*50}")
        print(f"최적화 중: {agent_name}")
        print(f"{'='*50}")

        try:
            optimized = optimize_agent_prompt(agent_name, common_test_cases)
            results[agent_name] = "success"
        except Exception as e:
            print(f"에러: {e}")
            results[agent_name] = f"failed: {e}"

    # 결과 요약
    print(f"\n{'='*50}")
    print("최적화 결과 요약")
    print(f"{'='*50}")

    success = sum(1 for r in results.values() if r == "success")
    print(f"성공: {success}/{len(results)}")

    return results


if __name__ == "__main__":
    optimize_all()
```

---

## 6. Phase 4: 자동 피드백 루프

### 6.1 세션 파서

```python
# src/agents/prompt_learning/session_parser.py
"""
Claude Code 세션 로그 파서
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class SessionEvent:
    """세션 이벤트"""
    timestamp: str
    event_type: str
    content: dict
    tool_name: Optional[str] = None
    success: Optional[bool] = None
    error: Optional[str] = None


@dataclass
class SessionSummary:
    """세션 요약"""
    session_id: str
    total_events: int
    tool_calls: int
    errors: list[dict]
    success: bool
    duration_seconds: float


def parse_session_log(log_path: Path) -> list[SessionEvent]:
    """
    .jsonl 세션 로그 파싱

    Args:
        log_path: 세션 로그 파일 경로

    Returns:
        SessionEvent 목록
    """
    events = []

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                event = SessionEvent(
                    timestamp=data.get("timestamp", ""),
                    event_type=data.get("type", "unknown"),
                    content=data.get("content", {}),
                    tool_name=data.get("tool", {}).get("name"),
                    success=data.get("success"),
                    error=data.get("error")
                )
                events.append(event)
            except json.JSONDecodeError:
                continue

    return events


def summarize_session(events: list[SessionEvent]) -> SessionSummary:
    """세션 요약 생성"""

    errors = []
    tool_calls = 0

    for event in events:
        if event.tool_name:
            tool_calls += 1

        if event.error:
            errors.append({
                "timestamp": event.timestamp,
                "tool": event.tool_name,
                "error": event.error
            })

    # 성공 여부 판단
    success = len(errors) == 0

    # 시간 계산 (첫 이벤트 ~ 마지막 이벤트)
    if events:
        # TODO: 실제 타임스탬프 파싱
        duration = 0.0
    else:
        duration = 0.0

    return SessionSummary(
        session_id=events[0].content.get("session_id", "unknown") if events else "unknown",
        total_events=len(events),
        tool_calls=tool_calls,
        errors=errors,
        success=success,
        duration_seconds=duration
    )
```

### 6.2 실패 분석기

```python
# src/agents/prompt_learning/failure_analyzer.py
"""
세션 실패 원인 분석
"""

import dspy
from dataclasses import dataclass
from typing import Optional


@dataclass
class FailureAnalysis:
    """실패 분석 결과"""
    root_cause: str
    category: str  # "conceptual", "execution", "validation", "external"
    claude_md_relevant: bool
    suggested_improvement: Optional[str]
    confidence: float


class FailureAnalyzer(dspy.Signature):
    """세션 실패 원인 분석"""

    session_log: str = dspy.InputField(desc="세션 로그 요약")
    error_messages: str = dspy.InputField(desc="에러 메시지 목록")
    task_description: str = dspy.InputField(desc="원래 태스크 설명")

    root_cause: str = dspy.OutputField(desc="근본 원인 설명")
    category: str = dspy.OutputField(desc="실패 카테고리")
    is_prompt_issue: bool = dspy.OutputField(desc="CLAUDE.md 관련 이슈 여부")
    improvement: str = dspy.OutputField(desc="CLAUDE.md 개선 제안")


class FailureAnalyzerModule(dspy.Module):
    """실패 분석 모듈"""

    def __init__(self):
        super().__init__()
        self.analyzer = dspy.ChainOfThought(FailureAnalyzer)

    def forward(self, session_log: str, error_messages: str, task_description: str):
        result = self.analyzer(
            session_log=session_log,
            error_messages=error_messages,
            task_description=task_description
        )

        return FailureAnalysis(
            root_cause=result.root_cause,
            category=result.category,
            claude_md_relevant=result.is_prompt_issue,
            suggested_improvement=result.improvement if result.is_prompt_issue else None,
            confidence=0.8  # TODO: 신뢰도 계산 로직 추가
        )
```

### 6.3 CLAUDE.md 자동 업데이터

```python
# src/agents/prompt_learning/claude_md_updater.py
"""
CLAUDE.md 자동 업데이트 시스템
"""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import dspy


@dataclass
class UpdateProposal:
    """업데이트 제안"""
    section: str
    current_content: str
    proposed_content: str
    reason: str
    confidence: float


class ClaudeMDUpdater:
    """CLAUDE.md 자동 업데이트"""

    def __init__(self, claude_md_path: str = "CLAUDE.md"):
        self.path = Path(claude_md_path)
        self.backup_path = Path(f"{claude_md_path}.backup")
        self.content = self._load()

    def _load(self) -> str:
        """CLAUDE.md 로드"""
        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()

    def _backup(self):
        """백업 생성"""
        with open(self.backup_path, "w", encoding="utf-8") as f:
            f.write(self.content)

    def _parse_sections(self) -> dict[str, str]:
        """섹션별로 파싱"""
        sections = {}
        current_section = None
        current_content = []

        for line in self.content.split("\n"):
            if line.startswith("## "):
                if current_section:
                    sections[current_section] = "\n".join(current_content)
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content)

        return sections

    def propose_update(
        self,
        failure_analysis: 'FailureAnalysis',
        min_confidence: float = 0.7
    ) -> Optional[UpdateProposal]:
        """
        실패 분석 기반 업데이트 제안
        """
        if not failure_analysis.claude_md_relevant:
            return None

        if failure_analysis.confidence < min_confidence:
            return None

        # 관련 섹션 찾기
        sections = self._parse_sections()

        # DSPy로 최적 섹션 및 업데이트 내용 생성
        # TODO: 실제 구현

        return UpdateProposal(
            section="3. Workflow Pipeline",
            current_content=sections.get("3. Workflow Pipeline", ""),
            proposed_content=failure_analysis.suggested_improvement,
            reason=failure_analysis.root_cause,
            confidence=failure_analysis.confidence
        )

    def apply_update(self, proposal: UpdateProposal, dry_run: bool = True) -> str:
        """
        업데이트 적용

        Args:
            proposal: 업데이트 제안
            dry_run: True면 실제 파일 변경 없이 결과만 반환
        """
        if not dry_run:
            self._backup()

        # 섹션 교체
        new_content = self.content.replace(
            proposal.current_content,
            proposal.proposed_content
        )

        if not dry_run:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(new_content)
            self.content = new_content

        return new_content

    def rollback(self):
        """백업에서 복원"""
        if self.backup_path.exists():
            with open(self.backup_path, "r", encoding="utf-8") as f:
                self.content = f.read()
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(self.content)
```

---

## 7. 슬래시 커맨드

### 7.1 /prompt-learn 커맨드

```markdown
<!-- .claude/commands/prompt-learn.md -->
# Prompt Learning 피드백 분석

세션 실패를 분석하고 CLAUDE.md 개선안을 제안합니다.

## 워크플로우

1. **세션 로그 분석**: 실패한 세션의 .jsonl 파일 파싱
2. **실패 원인 분석**: LLM으로 근본 원인 파악
3. **CLAUDE.md 연관성**: 프롬프트 이슈 여부 판단
4. **개선안 제안**: 구체적인 CLAUDE.md 수정 제안
5. **A/B 테스트**: 개선 효과 측정

## 사용법

```
/prompt-learn                    # 최근 실패 세션 분석
/prompt-learn --session <id>     # 특정 세션 분석
/prompt-learn --apply            # 제안된 개선안 적용
/prompt-learn --rollback         # 이전 버전으로 복원
```

## 출력 형식

```markdown
# Prompt Learning 분석 결과

## 세션 요약
- **세션 ID**: abc123
- **총 이벤트**: 45
- **에러 수**: 3
- **성공 여부**: ❌ 실패

## 실패 분석

### 근본 원인
[분석 결과]

### 카테고리
- [ ] 개념적 오류
- [x] 실행 오류
- [ ] 검증 오류
- [ ] 외부 요인

### CLAUDE.md 관련성
**관련 여부**: ✅ 예

## 개선 제안

### 현재 내용 (Section 3)
```
[현재 CLAUDE.md 내용]
```

### 제안 내용
```
[개선된 내용]
```

### 적용 명령
```bash
/prompt-learn --apply
```
```

---

**분석할 세션을 지정하거나, 최근 실패 세션을 자동으로 분석합니다.**
```

---

## 8. CI/CD 통합

### 8.1 GitHub Actions 워크플로우

```yaml
# .github/workflows/prompt-learning.yml
name: CLAUDE.md Prompt Learning

on:
  schedule:
    - cron: '0 0 * * 0'  # 매주 일요일 자정
  workflow_dispatch:
    inputs:
      force_optimize:
        description: '강제 최적화 실행'
        type: boolean
        default: false

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install dspy-ai textgrad anthropic

      - name: Collect session logs
        run: |
          # 최근 1주일 실패 세션 수집
          python scripts/collect_failed_sessions.py --days 7

      - name: Run failure analysis
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/analyze_failures.py --output analysis_report.json

      - name: Generate improvements
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/generate_improvements.py \
            --input analysis_report.json \
            --output improvements.json

      - name: A/B Test
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/ab_test_validators.py \
            --improvements improvements.json \
            --output ab_results.json

      - name: Create PR if improvement > 5%
        if: ${{ fromJson(steps.ab_test.outputs.improvement) > 5 }}
        run: |
          gh pr create \
            --title "chore: CLAUDE.md auto-optimization" \
            --body-file improvements.json \
            --label "prompt-learning,auto-generated"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 9. 메트릭 및 모니터링

### 9.1 성능 지표

```python
# src/agents/prompt_learning/metrics.py
"""
Prompt Learning 성능 메트릭
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json
from pathlib import Path


@dataclass
class PromptLearningMetrics:
    """Prompt Learning 성능 지표"""

    # 기본 지표
    timestamp: datetime
    claude_md_version: str

    # Phase 검증 지표
    phase_0_pass_rate: float
    phase_1_pass_rate: float
    phase_2_pass_rate: float
    overall_pass_rate: float

    # 효율성 지표
    avg_task_completion_time: float  # seconds
    avg_tokens_per_task: int

    # 품질 지표
    user_satisfaction_score: Optional[float]
    rollback_count: int

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "claude_md_version": self.claude_md_version,
            "phase_pass_rates": {
                "phase_0": self.phase_0_pass_rate,
                "phase_1": self.phase_1_pass_rate,
                "phase_2": self.phase_2_pass_rate,
                "overall": self.overall_pass_rate
            },
            "efficiency": {
                "avg_completion_time": self.avg_task_completion_time,
                "avg_tokens": self.avg_tokens_per_task
            },
            "quality": {
                "satisfaction": self.user_satisfaction_score,
                "rollbacks": self.rollback_count
            }
        }

    def save(self, path: str = "metrics/prompt_learning.jsonl"):
        """메트릭 저장 (append)"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.to_dict()) + "\n")


def calculate_improvement(baseline: PromptLearningMetrics, current: PromptLearningMetrics) -> dict:
    """개선율 계산"""
    return {
        "pass_rate_improvement": (
            (current.overall_pass_rate - baseline.overall_pass_rate)
            / baseline.overall_pass_rate * 100
        ),
        "time_improvement": (
            (baseline.avg_task_completion_time - current.avg_task_completion_time)
            / baseline.avg_task_completion_time * 100
        ),
        "token_improvement": (
            (baseline.avg_tokens_per_task - current.avg_tokens_per_task)
            / baseline.avg_tokens_per_task * 100
        )
    }
```

---

## 10. 참고 자료

### 핵심 라이브러리
- [DSPy - Stanford NLP](https://github.com/stanfordnlp/dspy) (30.3k ⭐)
- [TextGrad - Stanford Zou](https://github.com/zou-group/textgrad) (3.1k ⭐)
- [LangGraph](https://github.com/langchain-ai/langgraph)

### 문서
- [DSPy Optimizers](https://dspy.ai/learn/optimization/optimizers/)
- [TextGrad Nature Paper](https://hai.stanford.edu/news/textgrad-autograd-text)
- [Arize: CLAUDE.md Prompt Learning](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/)

### 관련 이슈
- [#9 - feat: Prompt Learning 피드백 루프 시스템 구현](https://github.com/garimto81/archive-analyzer/issues/9)

---

## 부록: 빠른 시작

```bash
# 1. 의존성 설치
pip install dspy-ai textgrad anthropic langgraph

# 2. 환경 변수 설정
export ANTHROPIC_API_KEY="your-api-key"

# 3. Hook 설치
cp .claude/hooks/claude-md-validator.py ~/.claude/hooks/

# 4. DSPy 최적화 실행
python scripts/optimize_phase_validators.py

# 5. A/B 테스트
python scripts/ab_test_validators.py
```
