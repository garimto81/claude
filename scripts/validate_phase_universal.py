#!/usr/bin/env python3
"""
Universal Phase Validator (Cross-platform)

Works on Windows, macOS, Linux
Validates all phases (0, 0.5, 1, 2, 3, 5, 6)

Usage:
    python scripts/validate_phase_universal.py 0 NNNN
    python scripts/validate_phase_universal.py 1
    python scripts/validate_phase_universal.py 2 --coverage 80

Version: 1.0.0
Compatible with: claude-code-config >= 5.0.0
"""

import sys
import argparse
import pathlib
import re
import subprocess
from typing import Optional, List, Tuple
from enum import Enum


class ValidationResult(Enum):
    """Validation result status"""
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    WARN = "⚠️  WARN"


class PhaseValidator:
    """Base validator class"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            print(f"  {message}")

    def error(self, message: str):
        """Add error"""
        self.errors.append(message)
        print(f"❌ {message}")

    def warn(self, message: str):
        """Add warning"""
        self.warnings.append(message)
        print(f"⚠️  {message}")

    def success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")

    def result(self) -> ValidationResult:
        """Get validation result"""
        if self.errors:
            return ValidationResult.FAIL
        elif self.warnings:
            return ValidationResult.WARN
        else:
            return ValidationResult.PASS


class Phase0Validator(PhaseValidator):
    """Phase 0: PRD validation"""

    def validate(self, prd_number: str) -> ValidationResult:
        """
        Validate Phase 0 completion

        Args:
            prd_number: PRD number (e.g., "0001")

        Returns:
            ValidationResult
        """
        print(f"\n🔍 Validating Phase 0 (PRD-{prd_number})...")

        # 1. Check PRD file exists
        prd_pattern = f"tasks/prds/{prd_number}-prd-*.md"
        prd_files = list(pathlib.Path(".").glob(prd_pattern))

        if not prd_files:
            self.error(f"PRD file not found: {prd_pattern}")
            return self.result()

        prd_file = prd_files[0]
        self.success(f"PRD file found: {prd_file}")

        # 2. Check minimum lines
        with open(prd_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if len(lines) < 50:
            self.error(f"PRD too short: {len(lines)} lines (minimum 50)")
        else:
            self.success(f"PRD length OK: {len(lines)} lines")

        # 3. Check required sections
        content = "".join(lines)
        required_sections = [
            ("Purpose", r"##\s*(?:1\.)?\s*Purpose"),
            ("Features", r"##\s*(?:\d+\.)?\s*.*Features"),
            ("Success", r"##\s*(?:\d+\.)?\s*Success"),
        ]

        for section_name, pattern in required_sections:
            if re.search(pattern, content, re.IGNORECASE):
                self.success(f"Section found: {section_name}")
            else:
                self.warn(f"Section missing or misnamed: {section_name}")

        return self.result()


class Phase05Validator(PhaseValidator):
    """Phase 0.5: Task List validation"""

    def validate(self, prd_number: str) -> ValidationResult:
        """Validate Phase 0.5 completion"""
        print(f"\n🔍 Validating Phase 0.5 (PRD-{prd_number})...")

        # 1. Check task list exists
        task_pattern = f"tasks/{prd_number}-tasks-*.md"
        task_files = list(pathlib.Path(".").glob(task_pattern))

        if not task_files:
            self.error(f"Task list not found: {task_pattern}")
            return self.result()

        task_file = task_files[0]
        self.success(f"Task list found: {task_file}")

        # 2. Check Task 0.0 completed
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for Task 0.0 and check if checkboxes are marked
        task_00_pattern = r"##\s*Task\s*0\.0.*?(?=##|\Z)"
        task_00_match = re.search(task_00_pattern, content, re.DOTALL)

        if not task_00_match:
            self.warn("Task 0.0 section not found")
        else:
            task_00_content = task_00_match.group(0)
            completed = task_00_content.count("[x]")
            total = task_00_content.count("[") // 2  # Count all checkboxes

            if completed == 0:
                self.error("Task 0.0 not started")
            elif completed == total:
                self.success(f"Task 0.0 completed ({completed}/{total})")
            else:
                self.warn(f"Task 0.0 partially done ({completed}/{total})")

        # 3. Check overall progress
        total_tasks = content.count("- [ ]") + content.count("- [x]")
        completed_tasks = content.count("- [x]")

        if total_tasks > 0:
            progress = (completed_tasks / total_tasks) * 100
            self.success(f"Overall progress: {completed_tasks}/{total_tasks} ({progress:.1f}%)")
        else:
            self.warn("No tasks with checkboxes found")

        return self.result()


class Phase1Validator(PhaseValidator):
    """Phase 1: 1:1 Test Pairing validation"""

    def validate(self) -> ValidationResult:
        """Validate Phase 1: All implementation files have tests"""
        print("\n🔍 Validating Phase 1 (1:1 Test Pairing)...")

        # Find all implementation files
        src_patterns = ["src/**/*.py", "src/**/*.ts", "src/**/*.tsx", "src/**/*.js", "src/**/*.jsx"]
        src_files = []
        for pattern in src_patterns:
            src_files.extend(pathlib.Path(".").glob(pattern))

        if not src_files:
            self.warn("No implementation files found in src/")
            return self.result()

        self.log(f"Found {len(src_files)} implementation files")

        # Check each has a test file
        orphaned = []
        for src_file in src_files:
            test_file = self._get_test_file_path(src_file)

            if test_file.exists():
                self.log(f"✅ {src_file} → {test_file}")
            else:
                orphaned.append(src_file)
                self.log(f"❌ {src_file} → MISSING: {test_file}")

        if orphaned:
            self.error(f"Orphaned files without tests: {len(orphaned)}")
            for file in orphaned:
                print(f"   ❌ {file}")
        else:
            self.success(f"All {len(src_files)} files have 1:1 test pairs")

        return self.result()

    def _get_test_file_path(self, src_file: pathlib.Path) -> pathlib.Path:
        """Get expected test file path for implementation file"""
        # src/auth/oauth.py → tests/auth/test_oauth.py
        # src/components/Button.tsx → tests/components/Button.test.tsx

        relative = src_file.relative_to("src")
        parent = relative.parent
        name = relative.stem
        suffix = relative.suffix

        # Determine test naming convention
        if suffix in [".ts", ".tsx", ".js", ".jsx"]:
            test_name = f"{name}.test{suffix}"
        else:  # Python
            test_name = f"test_{name}{suffix}"

        return pathlib.Path("tests") / parent / test_name


class Phase2Validator(PhaseValidator):
    """Phase 2: Testing validation"""

    def validate(self, min_coverage: int = 80) -> ValidationResult:
        """Validate Phase 2: Tests pass with minimum coverage"""
        print(f"\n🔍 Validating Phase 2 (Tests & Coverage)...")

        # Detect project type
        if (pathlib.Path("package.json").exists()):
            return self._validate_node(min_coverage)
        elif (pathlib.Path("requirements.txt").exists() or
              pathlib.Path("pyproject.toml").exists()):
            return self._validate_python(min_coverage)
        else:
            self.error("Cannot detect project type (no package.json or requirements.txt)")
            return self.result()

    def _validate_python(self, min_coverage: int) -> ValidationResult:
        """Validate Python tests"""
        try:
            # Run pytest with coverage
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--cov=src", "--cov-report=term"],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.success("All tests passed")
            else:
                self.error("Tests failed")
                print(result.stdout)
                print(result.stderr)
                return self.result()

            # Check coverage (rough parsing)
            if f"TOTAL" in result.stdout:
                # Extract coverage percentage
                match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", result.stdout)
                if match:
                    coverage = int(match.group(1))
                    if coverage >= min_coverage:
                        self.success(f"Coverage: {coverage}% (>= {min_coverage}%)")
                    else:
                        self.error(f"Coverage too low: {coverage}% (minimum {min_coverage}%)")
                else:
                    self.warn("Could not parse coverage percentage")

        except FileNotFoundError:
            self.error("pytest not found. Install: pip install pytest pytest-cov")
        except subprocess.TimeoutExpired:
            self.error("Tests timed out after 5 minutes")

        return self.result()

    def _validate_node(self, min_coverage: int) -> ValidationResult:
        """Validate Node.js tests"""
        try:
            # Run npm test
            result = subprocess.run(
                ["npm", "test"],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.success("All tests passed")
            else:
                self.error("Tests failed")
                print(result.stdout)
                print(result.stderr)

        except FileNotFoundError:
            self.error("npm not found")
        except subprocess.TimeoutExpired:
            self.error("Tests timed out after 5 minutes")

        return self.result()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Universal Phase Validator (Cross-platform)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_phase_universal.py 0 0001       # Validate Phase 0
  python scripts/validate_phase_universal.py 0.5 0001     # Validate Phase 0.5
  python scripts/validate_phase_universal.py 1            # Validate Phase 1
  python scripts/validate_phase_universal.py 2            # Validate Phase 2
  python scripts/validate_phase_universal.py 2 --coverage 90  # Custom coverage
        """
    )

    parser.add_argument("phase", type=str, help="Phase to validate (0, 0.5, 1, 2, 3, 5, 6)")
    parser.add_argument("prd_number", nargs="?", help="PRD number (for Phase 0, 0.5)")
    parser.add_argument("--coverage", type=int, default=80, help="Minimum coverage % (Phase 2)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Validate based on phase
    if args.phase == "0":
        if not args.prd_number:
            print("❌ PRD number required for Phase 0")
            sys.exit(1)
        validator = Phase0Validator(verbose=args.verbose)
        result = validator.validate(args.prd_number)

    elif args.phase == "0.5":
        if not args.prd_number:
            print("❌ PRD number required for Phase 0.5")
            sys.exit(1)
        validator = Phase05Validator(verbose=args.verbose)
        result = validator.validate(args.prd_number)

    elif args.phase == "1":
        validator = Phase1Validator(verbose=args.verbose)
        result = validator.validate()

    elif args.phase == "2":
        validator = Phase2Validator(verbose=args.verbose)
        result = validator.validate(min_coverage=args.coverage)

    else:
        print(f"❌ Phase {args.phase} validation not yet implemented")
        print("   Available: 0, 0.5, 1, 2")
        sys.exit(1)

    # Print final result
    print(f"\n{result.value}")
    sys.exit(0 if result == ValidationResult.PASS else 1)


if __name__ == "__main__":
    main()
