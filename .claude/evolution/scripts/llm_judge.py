#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-as-Judge: Agent 출력 품질 자동 평가
Claude API를 사용하여 Agent 출력물의 품질을 자동으로 평가

Usage:
    from llm_judge import LLMJudge

    judge = LLMJudge()

    score = judge.evaluate_output(
        agent="context7-engineer",
        task="Verify React 18 docs",
        output="React 18 introduces Suspense, Concurrent rendering...",
        expected="Documentation verification"
    )

    print(f"Quality Score: {score.quality}/10")
    print(f"Relevance: {score.relevance}/10")
    print(f"Completeness: {score.completeness}/10")
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

try:
    import anthropic
except ImportError:
    print("❌ anthropic 패키지가 설치되지 않았습니다.")
    print("   설치: pip install anthropic")
    exit(1)


@dataclass
class JudgeScore:
    """LLM Judge 평가 점수"""
    quality: float  # 0-10
    relevance: float  # 0-10
    completeness: float  # 0-10
    accuracy: float  # 0-10
    reasoning: str  # 평가 근거

    @property
    def overall_score(self) -> float:
        """종합 점수 (0-10)"""
        return (self.quality + self.relevance + self.completeness + self.accuracy) / 4

    @property
    def normalized_score(self) -> float:
        """정규화 점수 (0-1)"""
        return self.overall_score / 10


class LLMJudge:
    """LLM-as-Judge 평가기"""

    def __init__(self):
        """Initialize Claude API client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"

    def evaluate_output(
        self,
        agent: str,
        task: str,
        output: str,
        expected: Optional[str] = None,
        context: Optional[str] = None
    ) -> JudgeScore:
        """
        Agent 출력 품질 평가

        Args:
            agent: Agent 이름
            task: 수행한 작업
            output: Agent 출력 결과
            expected: 기대 결과 (optional)
            context: 추가 컨텍스트 (optional)

        Returns:
            JudgeScore
        """
        prompt = self._build_evaluation_prompt(agent, task, output, expected, context)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text
            score = self._parse_evaluation(result)
            return score

        except Exception as e:
            print(f"⚠️ LLM Judge error: {e}")
            # Fallback to neutral score
            return JudgeScore(
                quality=5.0,
                relevance=5.0,
                completeness=5.0,
                accuracy=5.0,
                reasoning=f"Error during evaluation: {e}"
            )

    def _build_evaluation_prompt(
        self,
        agent: str,
        task: str,
        output: str,
        expected: Optional[str],
        context: Optional[str]
    ) -> str:
        """평가 프롬프트 생성"""
        prompt = f"""You are an expert evaluator assessing the quality of AI agent outputs.

**Agent**: {agent}
**Task**: {task}
"""

        if expected:
            prompt += f"**Expected Result**: {expected}\n"

        if context:
            prompt += f"**Context**: {context}\n"

        prompt += f"""
**Agent Output**:
```
{output}
```

Evaluate the agent's output on the following criteria (0-10 scale):

1. **Quality**: How well-written and professional is the output?
2. **Relevance**: How relevant is the output to the task?
3. **Completeness**: Does the output fully address the task?
4. **Accuracy**: Is the information accurate and correct?

Provide your evaluation in the following JSON format:

```json
{{
  "quality": <score 0-10>,
  "relevance": <score 0-10>,
  "completeness": <score 0-10>,
  "accuracy": <score 0-10>,
  "reasoning": "<brief explanation of scores>"
}}
```

Be objective and fair in your assessment.
"""
        return prompt

    def _parse_evaluation(self, result: str) -> JudgeScore:
        """평가 결과 파싱"""
        import json
        import re

        # JSON 추출
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # JSON 블록 없으면 전체에서 시도
            json_str = result

        try:
            data = json.loads(json_str)
            return JudgeScore(
                quality=float(data.get('quality', 5.0)),
                relevance=float(data.get('relevance', 5.0)),
                completeness=float(data.get('completeness', 5.0)),
                accuracy=float(data.get('accuracy', 5.0)),
                reasoning=data.get('reasoning', 'No reasoning provided')
            )
        except json.JSONDecodeError:
            # Fallback
            return JudgeScore(
                quality=5.0,
                relevance=5.0,
                completeness=5.0,
                accuracy=5.0,
                reasoning="Failed to parse evaluation"
            )

    def evaluate_code_quality(self, code: str, language: str = "python") -> JudgeScore:
        """
        생성된 코드 품질 평가

        Args:
            code: 코드
            language: 프로그래밍 언어

        Returns:
            JudgeScore
        """
        prompt = f"""Evaluate the quality of this {language} code:

```{language}
{code}
```

Rate on these criteria (0-10):

1. **Quality**: Code readability, style, best practices
2. **Relevance**: Does it solve the intended problem?
3. **Completeness**: Is it complete and functional?
4. **Accuracy**: Is the logic correct?

Provide JSON format:
```json
{{
  "quality": <score>,
  "relevance": <score>,
  "completeness": <score>,
  "accuracy": <score>,
  "reasoning": "<explanation>"
}}
```
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text
            return self._parse_evaluation(result)

        except Exception as e:
            return JudgeScore(5.0, 5.0, 5.0, 5.0, f"Error: {e}")

    def compare_outputs(self, output_a: str, output_b: str, task: str) -> Dict:
        """
        두 Agent 출력 비교

        Args:
            output_a: Agent A 출력
            output_b: Agent B 출력
            task: 작업 설명

        Returns:
            비교 결과
        """
        prompt = f"""Compare two agent outputs for this task: {task}

**Output A**:
```
{output_a}
```

**Output B**:
```
{output_b}
```

Which output is better? Provide:

```json
{{
  "winner": "A" or "B" or "tie",
  "score_a": <0-10>,
  "score_b": <0-10>,
  "reasoning": "<explanation>"
}}
```
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text

            import json
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                return data
            else:
                return {
                    "winner": "tie",
                    "score_a": 5.0,
                    "score_b": 5.0,
                    "reasoning": "Failed to parse"
                }

        except Exception as e:
            return {
                "winner": "tie",
                "score_a": 5.0,
                "score_b": 5.0,
                "reasoning": f"Error: {e}"
            }


def main():
    """테스트 실행"""
    print("🧪 Testing LLM Judge...\n")

    judge = LLMJudge()

    # Test 1: 문서 검증 평가
    print("Test 1: Document Verification")
    score = judge.evaluate_output(
        agent="context7-engineer",
        task="Verify React 18 documentation",
        output="""React 18 introduces several new features:
        1. Concurrent Rendering
        2. Automatic Batching
        3. Suspense for data fetching
        4. New hooks: useId, useDeferredValue, useTransition

        All features are production-ready and documented at react.dev""",
        expected="Comprehensive verification of React 18 features"
    )

    print(f"Quality: {score.quality}/10")
    print(f"Relevance: {score.relevance}/10")
    print(f"Completeness: {score.completeness}/10")
    print(f"Accuracy: {score.accuracy}/10")
    print(f"Overall: {score.overall_score:.1f}/10")
    print(f"Reasoning: {score.reasoning}\n")

    # Test 2: 코드 품질 평가
    print("Test 2: Code Quality")
    code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    return total
"""
    score = judge.evaluate_code_quality(code, language="python")

    print(f"Code Quality: {score.overall_score:.1f}/10")
    print(f"Reasoning: {score.reasoning}\n")

    # Test 3: 출력 비교
    print("Test 3: Output Comparison")
    output_a = "React 18 has Suspense"
    output_b = "React 18 introduces Suspense for data fetching, Concurrent rendering, and automatic batching"

    comparison = judge.compare_outputs(output_a, output_b, "Describe React 18 features")
    print(f"Winner: {comparison['winner']}")
    print(f"Score A: {comparison['score_a']}/10")
    print(f"Score B: {comparison['score_b']}/10")
    print(f"Reasoning: {comparison['reasoning']}")

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    from typing import Dict
    main()
