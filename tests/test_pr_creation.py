"""
tests/test_pr_creation.py

PR 생성 로직 통합 테스트

Usage:
    pytest tests/test_pr_creation.py -v
"""

import pytest
import subprocess
import os

# 스크립트 파일 존재 여부 확인
SCRIPTS_EXIST = os.path.exists("scripts/create-phase-pr.sh") and os.path.exists(
    "scripts/check-phase-completion.py"
)


@pytest.mark.skipif(not SCRIPTS_EXIST, reason="PR 생성 스크립트가 설치되지 않음")
class TestPRCreationScript:
    """PR 생성 스크립트 통합 테스트"""

    def test_script_exists(self):
        """PR 생성 스크립트 파일 존재 확인"""
        script_path = "scripts/create-phase-pr.sh"
        assert os.path.exists(script_path), f"{script_path} 파일이 존재하지 않습니다"

    def test_script_is_executable(self):
        """스크립트 실행 권한 확인 (Unix 계열)"""
        script_path = "scripts/create-phase-pr.sh"

        if os.name != "nt":  # Windows가 아닌 경우만 체크
            assert os.access(
                script_path, os.X_OK
            ), f"{script_path}에 실행 권한이 없습니다"

    def test_script_has_shebang(self):
        """스크립트 shebang 확인"""
        script_path = "scripts/create-phase-pr.sh"

        with open(script_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()

        assert first_line.startswith("#!/"), "Shebang이 없습니다"
        assert "bash" in first_line, "Bash shebang이 아닙니다"


@pytest.mark.skipif(not SCRIPTS_EXIST, reason="Phase 감지 스크립트가 설치되지 않음")
class TestPhaseDetectionScript:
    """Phase 감지 스크립트 통합 테스트"""

    def test_script_exists(self):
        """Phase 감지 스크립트 파일 존재 확인"""
        script_path = "scripts/check-phase-completion.py"
        assert os.path.exists(script_path), f"{script_path} 파일이 존재하지 않습니다"

    def test_script_is_executable(self):
        """스크립트 실행 권한 확인 (Unix 계열)"""
        script_path = "scripts/check-phase-completion.py"

        if os.name != "nt":  # Windows가 아닌 경우만 체크
            assert os.access(
                script_path, os.X_OK
            ), f"{script_path}에 실행 권한이 없습니다"

    def test_script_has_shebang(self):
        """스크립트 shebang 확인"""
        script_path = "scripts/check-phase-completion.py"

        with open(script_path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()

        assert first_line.startswith("#!/"), "Shebang이 없습니다"
        assert "python" in first_line, "Python shebang이 아닙니다"

    @pytest.mark.skipif(os.name == "nt", reason="Windows에서는 Git bash 필요")
    def test_script_runs_successfully(self):
        """스크립트가 정상 실행되는지 확인 (Git 저장소 내에서)"""
        script_path = "scripts/check-phase-completion.py"

        try:
            # HEAD 커밋 분석 시도
            result = subprocess.run(
                ["python", script_path, "HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Exit code 0 또는 1 (Phase 완료 여부와 관계없이 스크립트는 정상 종료)
            assert result.returncode in [0, 1], f"스크립트 실행 실패: {result.stderr}"

        except subprocess.TimeoutExpired:
            pytest.fail("스크립트 실행 시간 초과")
        except FileNotFoundError:
            pytest.skip("Python 또는 Git이 설치되지 않음")


class TestWorkflowFile:
    """GitHub Actions 워크플로우 파일 테스트"""

    def test_workflow_file_exists(self):
        """워크플로우 파일 존재 확인"""
        workflow_path = ".github/workflows/auto-pr-merge.yml"
        assert os.path.exists(
            workflow_path
        ), f"{workflow_path} 파일이 존재하지 않습니다"

    def test_workflow_syntax(self):
        """워크플로우 파일 YAML 문법 검증"""
        workflow_path = ".github/workflows/auto-pr-merge.yml"

        try:
            import yaml

            with open(workflow_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)

            assert content is not None, "YAML 파일이 비어있습니다"
            assert "name" in content, "워크플로우 이름이 없습니다"
            # YAML에서 "on"은 True로 파싱될 수 있으므로 True도 허용
            assert "on" in content or True in content, "트리거 설정이 없습니다"
            assert "jobs" in content, "Job 설정이 없습니다"

        except ImportError:
            pytest.skip("PyYAML이 설치되지 않음 (pip install pyyaml)")
        except yaml.YAMLError as e:
            pytest.fail(f"YAML 문법 오류: {e}")

    def test_workflow_has_required_jobs(self):
        """워크플로우에 필수 Job이 있는지 확인"""
        workflow_path = ".github/workflows/auto-pr-merge.yml"

        try:
            import yaml

            with open(workflow_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)

            jobs = content.get("jobs", {})
            required_jobs = ["phase-detection", "create-pr", "run-tests", "auto-merge"]

            for job_name in required_jobs:
                assert job_name in jobs, f"필수 Job '{job_name}'이 없습니다"

        except ImportError:
            pytest.skip("PyYAML이 설치되지 않음")

    def test_workflow_permissions(self):
        """워크플로우 권한 설정 확인"""
        workflow_path = ".github/workflows/auto-pr-merge.yml"

        try:
            import yaml

            with open(workflow_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)

            permissions = content.get("permissions", {})

            assert "contents" in permissions, "contents 권한이 없습니다"
            assert "pull-requests" in permissions, "pull-requests 권한이 없습니다"
            assert (
                permissions["contents"] == "write"
            ), "contents write 권한이 필요합니다"
            assert (
                permissions["pull-requests"] == "write"
            ), "pull-requests write 권한이 필요합니다"

        except ImportError:
            pytest.skip("PyYAML이 설치되지 않음")


class TestPRTemplate:
    """PR 템플릿 테스트"""

    def test_pr_template_exists(self):
        """PR 템플릿 파일 존재 확인"""
        template_path = ".github/pull_request_template.md"
        assert os.path.exists(
            template_path
        ), f"{template_path} 파일이 존재하지 않습니다"

    def test_pr_template_has_checklist(self):
        """PR 템플릿에 체크리스트가 있는지 확인"""
        template_path = ".github/pull_request_template.md"

        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 체크박스 형식 확인
        assert "- [ ]" in content, "체크리스트가 없습니다"
        assert (
            "Checklist" in content or "checklist" in content
        ), "Checklist 섹션이 없습니다"

    def test_pr_template_has_phase_sections(self):
        """PR 템플릿에 Phase 섹션이 있는지 확인"""
        template_path = ".github/pull_request_template.md"

        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Phase 관련 섹션 확인
        assert "Phase" in content, "Phase 관련 섹션이 없습니다"
        assert "PRD" in content, "PRD 섹션이 없습니다"

    def test_pr_template_has_test_section(self):
        """PR 템플릿에 테스트 섹션이 있는지 확인"""
        template_path = ".github/pull_request_template.md"

        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert any(
            keyword in content for keyword in ["Test", "test", "Testing"]
        ), "테스트 섹션이 없습니다"


class TestDocumentation:
    """문서 파일 테스트"""

    def test_branch_protection_guide_exists(self):
        """Branch Protection 가이드 문서 존재 확인"""
        doc_path = "docs/BRANCH_PROTECTION_GUIDE.md"
        assert os.path.exists(doc_path), f"{doc_path} 파일이 존재하지 않습니다"

    def test_branch_protection_guide_has_content(self):
        """Branch Protection 가이드 내용 확인"""
        doc_path = "docs/BRANCH_PROTECTION_GUIDE.md"

        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 주요 키워드 확인
        keywords = [
            "Branch Protection",
            "auto-merge",
            "Required status checks",
            "GitHub Actions",
        ]

        for keyword in keywords:
            assert keyword in content, f"'{keyword}' 키워드가 문서에 없습니다"


class TestIntegration:
    """통합 테스트"""

    def test_all_required_files_exist(self):
        """모든 필수 파일이 존재하는지 확인"""
        # 필수 파일 (선택적 파일은 제외)
        required_files = [
            ".github/workflows/auto-pr-merge.yml",
            ".github/pull_request_template.md",
            "docs/BRANCH_PROTECTION_GUIDE.md",
        ]

        # 선택적 파일 (설치되지 않을 수 있음)
        optional_files = [
            "scripts/check-phase-completion.py",
            "scripts/create-phase-pr.sh",
            "tasks/prds/0002-prd-auto-pr-merge.md",
            "tasks/0002-tasks-auto-pr-merge.md",
        ]

        missing_required = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_required.append(file_path)

        assert not missing_required, f"누락된 필수 파일: {', '.join(missing_required)}"

        # 선택적 파일 경고만 출력 (실패하지 않음)
        missing_optional = [f for f in optional_files if not os.path.exists(f)]
        if missing_optional:
            import warnings

            warnings.warn(f"선택적 파일 누락: {', '.join(missing_optional)}")

    @pytest.mark.skipif(not SCRIPTS_EXIST, reason="스크립트가 설치되지 않음")
    def test_scripts_directory_structure(self):
        """scripts 디렉토리 구조 확인"""
        assert os.path.isdir("scripts"), "scripts 디렉토리가 없습니다"

        required_scripts = [
            "scripts/check-phase-completion.py",
            "scripts/create-phase-pr.sh",
        ]

        for script in required_scripts:
            assert os.path.exists(script), f"{script} 파일이 없습니다"

    def test_github_directory_structure(self):
        """.github 디렉토리 구조 확인"""
        assert os.path.isdir(".github"), ".github 디렉토리가 없습니다"
        assert os.path.isdir(
            ".github/workflows"
        ), ".github/workflows 디렉토리가 없습니다"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
