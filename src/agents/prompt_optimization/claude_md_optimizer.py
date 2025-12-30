"""
CLAUDE.md 자동 최적화 모듈

DSPy를 사용하여 CLAUDE.md 지침을 자동으로 최적화합니다.
목표: 토큰 30% 절감, 성능 10% 향상

사용법:
    pip install dspy-ai anthropic
    python claude_md_optimizer.py --input CLAUDE.md --output CLAUDE_optimized.md
"""

from pathlib import Path
from typing import Optional
import re


class ClaudeMDOptimizer:
    """CLAUDE.md 최적화 클래스"""

    def __init__(self, input_path: str = "CLAUDE.md"):
        self.input_path = Path(input_path)
        self.sections: dict[str, str] = {}
        self.optimization_rules = [
            self._remove_redundant_whitespace,
            self._compress_tables,
            self._shorten_examples,
            self._extract_to_references,
        ]

    def load(self) -> str:
        """CLAUDE.md 파일 로드"""
        if not self.input_path.exists():
            raise FileNotFoundError(f"{self.input_path} not found")
        return self.input_path.read_text(encoding="utf-8")

    def parse_sections(self, content: str) -> dict[str, str]:
        """섹션별로 파싱"""
        sections = {}
        current_section = "header"
        current_content = []

        for line in content.split("\n"):
            if line.startswith("## "):
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = line[3:].strip()
                current_content = [line]
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = "\n".join(current_content)

        self.sections = sections
        return sections

    def _remove_redundant_whitespace(self, content: str) -> str:
        """불필요한 공백 제거"""
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = re.sub(r" +$", "", content, flags=re.MULTILINE)
        return content

    def _compress_tables(self, content: str) -> str:
        """테이블 압축"""
        lines = content.split("\n")
        result = []
        for line in lines:
            if "|" in line:
                cells = line.split("|")
                cells = [cell.strip() for cell in cells]
                line = "|".join(cells)
            result.append(line)
        return "\n".join(result)

    def _shorten_examples(self, content: str) -> str:
        """긴 예시 축소"""

        def shorten_code_block(match):
            code = match.group(0)
            code = re.sub(r"#\s*.{50,}", lambda m: m.group(0)[:50] + "...", code)
            return code

        content = re.sub(r"```[\s\S]*?```", shorten_code_block, content)
        return content

    def _extract_to_references(self, content: str) -> str:
        """상세 내용을 참조로 대체"""
        return content

    def optimize(self, content: str) -> str:
        """모든 최적화 규칙 적용"""
        for rule in self.optimization_rules:
            content = rule(content)
        return content

    def calculate_metrics(self, original: str, optimized: str) -> dict:
        """최적화 메트릭 계산"""
        original_lines = len(original.split("\n"))
        optimized_lines = len(optimized.split("\n"))
        original_chars = len(original)
        optimized_chars = len(optimized)
        original_tokens = original_chars // 4
        optimized_tokens = optimized_chars // 4

        return {
            "original_lines": original_lines,
            "optimized_lines": optimized_lines,
            "line_reduction": f"{(1 - optimized_lines/original_lines)*100:.1f}%",
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "token_reduction": f"{(1 - optimized_tokens/original_tokens)*100:.1f}%",
        }

    def run(self, output_path: Optional[str] = None) -> dict:
        """최적화 실행"""
        original = self.load()
        self.parse_sections(original)
        optimized = self.optimize(original)
        if output_path:
            Path(output_path).write_text(optimized, encoding="utf-8")
        return self.calculate_metrics(original, optimized)


class DSPyOptimizer:
    """DSPy 기반 고급 최적화"""

    def __init__(self):
        self.dspy_available = False
        try:
            import dspy

            self.dspy = dspy
            self.dspy_available = True
        except ImportError:
            pass

    def is_available(self) -> bool:
        return self.dspy_available

    def optimize_with_dspy(
        self, content: str, model: str = "claude-3-5-sonnet-20241022"
    ) -> str:
        """DSPy를 사용한 프롬프트 최적화"""
        if not self.dspy_available:
            raise ImportError("dspy-ai 필요: pip install dspy-ai")

        lm = self.dspy.LM(model)
        self.dspy.configure(lm=lm)

        class OptimizePrompt(self.dspy.Signature):
            """프롬프트 최적화"""

            original_prompt: str = self.dspy.InputField()
            optimized_prompt: str = self.dspy.OutputField()

        optimizer = self.dspy.Predict(OptimizePrompt)
        result = optimizer(original_prompt=content)
        return result.optimized_prompt


def main():
    """CLI 진입점"""
    import argparse

    parser = argparse.ArgumentParser(description="CLAUDE.md 최적화")
    parser.add_argument("--input", default="CLAUDE.md")
    parser.add_argument("--output")
    parser.add_argument("--use-dspy", action="store_true")
    args = parser.parse_args()

    optimizer = ClaudeMDOptimizer(args.input)
    metrics = optimizer.run(args.output)
    print("=== 최적화 결과 ===")
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
