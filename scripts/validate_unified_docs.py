#!/usr/bin/env python3
"""
Unified Documentation Validator

통합 문서 폴더(docs/unified/)의 정합성을 검증합니다.

Usage:
    python scripts/validate_unified_docs.py
    python scripts/validate_unified_docs.py --namespace HUB
    python scripts/validate_unified_docs.py --fix
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Violation:
    rule_id: str
    message: str
    severity: Severity
    file_path: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False


@dataclass
class ValidationReport:
    violations: list[Violation] = field(default_factory=list)
    files_checked: int = 0

    @property
    def errors(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.ERROR)

    @property
    def warnings(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.WARNING)


# 설정
UNIFIED_PATH = Path(r"C:\claude\docs\unified")
VALID_NAMESPACES = {"MAIN", "HUB", "FT", "SUB", "AE"}

# 파일명 패턴
PRD_PATTERN = re.compile(r"^([A-Z]+)-(\d{4}[a-z]?)-([a-z0-9-]+)\.md$")
CHECKLIST_PATTERN = re.compile(r"^([A-Z]+)-(\d{4}[a-z]?)\.md$")


def validate_filename(filename: str, doc_type: str) -> Optional[Violation]:
    """파일명 패턴 검증"""
    pattern = PRD_PATTERN if doc_type == "prd" else CHECKLIST_PATTERN

    if not pattern.match(filename):
        return Violation(
            rule_id="F001",
            message=f"Invalid filename pattern: {filename}",
            severity=Severity.ERROR,
            file_path=filename,
            suggestion=f"Expected: {{NS}}-{{NNNN}}-{{slug}}.md" if doc_type == "prd" else "{{NS}}-{{NNNN}}.md"
        )

    # 네임스페이스 검증
    match = pattern.match(filename)
    if match:
        ns = match.group(1)
        if ns not in VALID_NAMESPACES:
            return Violation(
                rule_id="F002",
                message=f"Invalid namespace: {ns}",
                severity=Severity.ERROR,
                file_path=filename,
                suggestion=f"Valid namespaces: {', '.join(VALID_NAMESPACES)}"
            )

    return None


def check_prd_checklist_mapping(prds: set[str], checklists: set[str]) -> list[Violation]:
    """PRD-체크리스트 매핑 검증"""
    violations = []

    for prd_id in prds:
        if prd_id not in checklists:
            violations.append(Violation(
                rule_id="F004",
                message=f"PRD without checklist: {prd_id}",
                severity=Severity.WARNING,
                file_path=f"prds/*/{prd_id}-*.md",
                suggestion=f"Create checklists/*/{prd_id}.md",
                auto_fixable=True
            ))

    return violations


def validate_registry(registry_path: Path, actual_prds: set[str]) -> list[Violation]:
    """registry.json 검증"""
    violations = []

    if not registry_path.exists():
        violations.append(Violation(
            rule_id="R001",
            message="registry.json not found",
            severity=Severity.ERROR,
            file_path=str(registry_path)
        ))
        return violations

    with open(registry_path, encoding="utf-8") as f:
        registry = json.load(f)

    registered_prds = set(registry.get("prds", {}).keys())

    # 레지스트리에 있지만 파일이 없는 경우
    for prd_id in registered_prds - actual_prds:
        violations.append(Violation(
            rule_id="R006",
            message=f"Registered but file not found: {prd_id}",
            severity=Severity.ERROR,
            file_path="registry.json"
        ))

    # 파일이 있지만 레지스트리에 없는 경우
    for prd_id in actual_prds - registered_prds:
        violations.append(Violation(
            rule_id="R005",
            message=f"File exists but not registered: {prd_id}",
            severity=Severity.WARNING,
            file_path="registry.json",
            auto_fixable=True
        ))

    # 통계 검증
    stats = registry.get("statistics", {})
    if stats.get("total_prds") != len(actual_prds):
        violations.append(Violation(
            rule_id="R002",
            message=f"Statistics mismatch: registry={stats.get('total_prds')}, actual={len(actual_prds)}",
            severity=Severity.WARNING,
            file_path="registry.json",
            auto_fixable=True
        ))

    return violations


def scan_prds(namespace: Optional[str] = None) -> tuple[set[str], int]:
    """PRD 파일 스캔"""
    prds_dir = UNIFIED_PATH / "prds"
    prd_ids = set()
    count = 0

    for ns_dir in prds_dir.iterdir():
        if not ns_dir.is_dir():
            continue
        if namespace and ns_dir.name != namespace:
            continue

        for prd_file in ns_dir.glob("*.md"):
            count += 1
            match = PRD_PATTERN.match(prd_file.name)
            if match:
                prd_ids.add(f"{match.group(1)}-{match.group(2)}")

    return prd_ids, count


def scan_checklists(namespace: Optional[str] = None) -> set[str]:
    """체크리스트 파일 스캔"""
    checklists_dir = UNIFIED_PATH / "checklists"
    checklist_ids = set()

    for ns_dir in checklists_dir.iterdir():
        if not ns_dir.is_dir():
            continue
        if namespace and ns_dir.name != namespace:
            continue

        for cl_file in ns_dir.glob("*.md"):
            match = CHECKLIST_PATTERN.match(cl_file.name)
            if match:
                checklist_ids.add(f"{match.group(1)}-{match.group(2)}")

    return checklist_ids


def run_validation(namespace: Optional[str] = None) -> ValidationReport:
    """전체 검증 실행"""
    report = ValidationReport()

    # PRD 스캔 및 파일명 검증
    prds_dir = UNIFIED_PATH / "prds"
    prd_ids = set()

    for ns_dir in prds_dir.iterdir():
        if not ns_dir.is_dir():
            continue
        if namespace and ns_dir.name != namespace:
            continue

        for prd_file in ns_dir.glob("*.md"):
            report.files_checked += 1

            # 파일명 검증
            violation = validate_filename(prd_file.name, "prd")
            if violation:
                violation.file_path = str(prd_file.relative_to(UNIFIED_PATH))
                report.violations.append(violation)
            else:
                match = PRD_PATTERN.match(prd_file.name)
                if match:
                    prd_ids.add(f"{match.group(1)}-{match.group(2)}")

    # 체크리스트 스캔
    checklist_ids = scan_checklists(namespace)

    # PRD-체크리스트 매핑 검증
    report.violations.extend(check_prd_checklist_mapping(prd_ids, checklist_ids))

    # 레지스트리 검증 (전체 검증일 때만)
    if namespace is None:
        all_prds, _ = scan_prds()
        report.violations.extend(validate_registry(UNIFIED_PATH / "registry.json", all_prds))

    return report


def print_report(report: ValidationReport):
    """리포트 출력"""
    print("=" * 60)
    print("  Unified Documentation Validation Report")
    print("=" * 60)
    print()
    print(f"Files checked: {report.files_checked}")
    print()

    if report.errors > 0:
        print(f"ERRORS ({report.errors})")
        print("-" * 60)
        for v in report.violations:
            if v.severity == Severity.ERROR:
                print(f"[{v.rule_id}] {v.message}")
                print(f"  -> {v.file_path}")
                if v.suggestion:
                    print(f"  Suggestion: {v.suggestion}")
                print()

    if report.warnings > 0:
        print(f"WARNINGS ({report.warnings})")
        print("-" * 60)
        for v in report.violations:
            if v.severity == Severity.WARNING:
                fix_mark = " [Auto-fix available]" if v.auto_fixable else ""
                print(f"[{v.rule_id}] {v.message}{fix_mark}")
                print(f"  -> {v.file_path}")
                if v.suggestion:
                    print(f"  Suggestion: {v.suggestion}")
                print()

    print("=" * 60)
    print("  Summary")
    print("=" * 60)
    print(f"  Errors:   {report.errors}")
    print(f"  Warnings: {report.warnings}")
    auto_fixable = sum(1 for v in report.violations if v.auto_fixable)
    print(f"  Auto-fixable: {auto_fixable}")
    print()

    if report.errors > 0:
        print("Validation FAILED")
        return 1
    elif report.warnings > 0:
        print("Validation PASSED with warnings")
        return 0
    else:
        print("Validation PASSED")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Validate unified documentation")
    parser.add_argument("--namespace", "-n", help="Validate specific namespace only")
    parser.add_argument("--fix", action="store_true", help="Apply automatic fixes")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.namespace and args.namespace not in VALID_NAMESPACES:
        print(f"Error: Invalid namespace '{args.namespace}'")
        print(f"Valid namespaces: {', '.join(VALID_NAMESPACES)}")
        sys.exit(1)

    report = run_validation(args.namespace)

    if args.json:
        output = {
            "files_checked": report.files_checked,
            "errors": report.errors,
            "warnings": report.warnings,
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "message": v.message,
                    "severity": v.severity.value,
                    "file_path": v.file_path,
                    "suggestion": v.suggestion,
                    "auto_fixable": v.auto_fixable
                }
                for v in report.violations
            ]
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        sys.exit(0 if report.errors == 0 else 1)
    else:
        sys.exit(print_report(report))


if __name__ == "__main__":
    main()
