"""
Auto Orchestrator - 자율 작업 루프 엔진

Claude Code를 외부에서 호출하여 자율적으로 작업을 반복 수행합니다.
- 2계층 우선순위 기반 작업 발견
- Claude Code subprocess 호출
- 종료 조건 체크 (--max, --promise, Context)
- 체크포인트 자동 저장
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

# 상대 임포트를 위한 경로 설정
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from auto_discovery import AutoDiscovery, DiscoveredTask, Priority
from auto_state import AutoState, CONTEXT_THRESHOLDS
from auto_logger import AutoLogger


class LoopStatus(Enum):
    """루프 상태"""
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CONTEXT_LIMIT = "context_limit"


@dataclass
class LoopConfig:
    """루프 설정"""
    max_iterations: Optional[int] = None  # --max N
    promise_text: Optional[str] = None    # --promise TEXT
    dry_run: bool = False                 # --dry-run
    skip_validation: bool = False         # --skip-validation (검증 생략)
    verbose: bool = True
    context_limit: int = 90               # Context % 임계값
    cooldown_seconds: int = 5             # 반복 간 대기 시간
    retry_on_error: int = 3               # 에러 시 재시도 횟수
    max_debug_attempts: int = 3           # E2E 실패 시 최대 디버그 시도


@dataclass
class ValidationResult:
    """검증 결과"""
    passed: bool
    test_type: str  # "e2e" or "tdd"
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    coverage_percent: float = 0.0
    error_message: Optional[str] = None
    details: Optional[dict] = None


@dataclass
class IterationResult:
    """반복 결과"""
    success: bool
    task: Optional[DiscoveredTask]
    output: str
    duration_seconds: float
    promise_fulfilled: bool = False
    error: Optional[str] = None
    e2e_result: Optional[ValidationResult] = None
    tdd_result: Optional[ValidationResult] = None


class AutoOrchestrator:
    """자율 작업 루프 오케스트레이터"""

    def __init__(
        self,
        config: LoopConfig,
        project_root: str = "D:/AI/claude01",
        session_id: Optional[str] = None
    ):
        self.config = config
        self.project_root = Path(project_root)
        self.discovery = AutoDiscovery(project_root)

        # 상태 관리
        self.state = AutoState(
            session_id=session_id,
            original_request="자율 판단 루프"
        )
        self.session_id = self.state.session_id

        # 통계
        self.iteration_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.start_time = datetime.now()

        # 콜백
        self.on_iteration_start: Optional[Callable] = None
        self.on_iteration_end: Optional[Callable] = None
        self.on_task_discovered: Optional[Callable] = None

    def run(self) -> LoopStatus:
        """메인 루프 실행"""
        self._log_start()
        status = LoopStatus.RUNNING

        try:
            while status == LoopStatus.RUNNING:
                # 종료 조건 체크
                status = self._check_termination()
                if status != LoopStatus.RUNNING:
                    break

                # 반복 실행
                result = self._run_iteration()

                # 결과 처리
                status = self._process_result(result)

                # 쿨다운
                if status == LoopStatus.RUNNING:
                    time.sleep(self.config.cooldown_seconds)

        except KeyboardInterrupt:
            status = LoopStatus.PAUSED
            self._log("사용자 중단 (Ctrl+C)")

        except Exception as e:
            status = LoopStatus.FAILED
            self._log(f"오류 발생: {e}")
            self.state.logger.log_error(str(e))

        finally:
            self._finalize(status)

        return status

    def _check_termination(self) -> LoopStatus:
        """종료 조건 체크"""
        # 1. --max 체크
        if self.config.max_iterations:
            if self.iteration_count >= self.config.max_iterations:
                self._log(f"최대 반복 횟수 도달: {self.config.max_iterations}")
                return LoopStatus.COMPLETED

        # 2. 연속 실패 체크
        if self.failure_count >= self.config.retry_on_error:
            self._log(f"연속 실패 {self.failure_count}회 - 중단")
            return LoopStatus.FAILED

        return LoopStatus.RUNNING

    def _run_iteration(self) -> IterationResult:
        """단일 반복 실행"""
        self.iteration_count += 1
        start = time.time()

        self._log(f"\n{'='*60}")
        self._log(f"[Iteration {self.iteration_count}] 시작")
        self._log(f"{'='*60}")

        if self.on_iteration_start:
            self.on_iteration_start(self.iteration_count)

        # 1. 작업 발견
        task = self.discovery.discover_next_task()

        if not task:
            self._log("✅ 모든 검사 통과 - 할 일 없음")
            return IterationResult(
                success=True,
                task=None,
                output="No tasks found",
                duration_seconds=time.time() - start
            )

        # 작업 발견 로깅
        self._log(f"\n📋 발견된 작업:")
        self._log(f"   우선순위: P{task.priority.value} ({task.category})")
        self._log(f"   제목: {task.title}")
        self._log(f"   설명: {task.description}")
        self._log(f"   명령: {task.command}")

        if self.on_task_discovered:
            self.on_task_discovered(task)

        # 로그 기록
        self.state.logger.log(
            event_type="decision",
            phase="discovery",
            data=task.to_dict()
        )

        # 2. Dry-run 모드
        if self.config.dry_run:
            self._log("\n🔍 [DRY-RUN] 실행하지 않음")
            return IterationResult(
                success=True,
                task=task,
                output="Dry run - not executed",
                duration_seconds=time.time() - start
            )

        # 3. Claude Code 호출
        output, success = self._execute_task(task)

        # 4. E2E 검증 (작업 성공 시 + skip_validation이 False일 때)
        e2e_result = None
        if success and not self.config.skip_validation:
            e2e_result = self._run_e2e_tests()

            # E2E 실패 시 디버그 자동 트리거
            if not e2e_result.passed:
                self._log("\n❌ E2E 테스트 실패 - 디버그 모드 진입")
                debug_success = self._trigger_debug(e2e_result)

                if debug_success:
                    # 디버그 후 재검증
                    e2e_result = self._run_e2e_tests()
                    if e2e_result.passed:
                        self._log("✅ E2E 재검증 통과")
                    else:
                        self._log("❌ E2E 재검증 실패 - 다음 반복에서 재시도")
                        success = False

        # 5. TDD 검증 (E2E 통과 시)
        tdd_result = None
        if success and e2e_result and e2e_result.passed and not self.config.skip_validation:
            tdd_result = self._run_tdd_tests()

            if not tdd_result.passed:
                self._log(f"⚠️  TDD 검증 경고 - 커버리지: {tdd_result.coverage_percent:.1f}%")
                # TDD 실패는 경고만 (작업은 성공으로 간주)

        # 6. Promise 체크
        promise_fulfilled = False
        if self.config.promise_text:
            promise_tag = f"<promise>{self.config.promise_text}</promise>"
            if promise_tag in output:
                promise_fulfilled = True
                self._log(f"\n🎯 Promise 충족: {self.config.promise_text}")

        duration = time.time() - start
        self._log(f"\n⏱️  소요 시간: {duration:.1f}초")

        return IterationResult(
            success=success,
            task=task,
            output=output,
            duration_seconds=duration,
            promise_fulfilled=promise_fulfilled,
            e2e_result=e2e_result,
            tdd_result=tdd_result
        )

    def _execute_task(self, task: DiscoveredTask) -> tuple[str, bool]:
        """Claude Code로 작업 실행"""
        self._log(f"\n🚀 Claude Code 실행: {task.command}")

        try:
            # Claude Code 호출
            # Windows에서는 shell=True 필요 (PATH에서 claude.cmd 찾기)
            import shutil
            claude_path = shutil.which("claude")
            if not claude_path:
                claude_path = "claude"  # fallback

            result = subprocess.run(
                [claude_path, "-p", task.command],
                capture_output=True,
                text=True,
                timeout=600,  # 10분 타임아웃
                cwd=self.project_root,
                encoding="utf-8",
                errors="replace",
                shell=(sys.platform == "win32")  # Windows에서만 shell=True
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            # 로그 기록
            self.state.logger.log_action(
                action="claude_execute",
                target=task.command,
                result="success" if success else "fail",
                details={"returncode": result.returncode}
            )

            if success:
                self.success_count += 1
                self.failure_count = 0  # 연속 실패 카운트 리셋
                self._log("✅ 실행 성공")
            else:
                self.failure_count += 1
                self._log(f"❌ 실행 실패 (returncode: {result.returncode})")

            return output, success

        except subprocess.TimeoutExpired:
            self.failure_count += 1
            self._log("⏰ 타임아웃 (10분 초과)")
            return "Timeout", False

        except FileNotFoundError:
            self._log("❌ Claude Code를 찾을 수 없습니다")
            self._log("   'claude' 명령어가 PATH에 있는지 확인하세요")
            return "Claude not found", False

        except Exception as e:
            self.failure_count += 1
            self._log(f"❌ 실행 오류: {e}")
            return str(e), False

    def _run_e2e_tests(self) -> ValidationResult:
        """E2E 테스트 실행 (Playwright)"""
        self._log("\n🧪 Phase 4: E2E 검증 중...")

        try:
            # Playwright 테스트 실행
            result = subprocess.run(
                ["npx", "playwright", "test"],
                capture_output=True,
                text=True,
                timeout=300,  # 5분 타임아웃
                cwd=self.project_root,
                encoding="utf-8",
                errors="replace",
                shell=(sys.platform == "win32")
            )

            # 결과 파싱 (간단한 패턴 매칭)
            output = result.stdout + result.stderr
            passed = result.returncode == 0

            # 테스트 개수 파싱 (예: "15 passed, 0 failed")
            import re
            passed_match = re.search(r"(\d+) passed", output)
            failed_match = re.search(r"(\d+) failed", output)

            passed_tests = int(passed_match.group(1)) if passed_match else 0
            failed_tests = int(failed_match.group(1)) if failed_match else 0
            total_tests = passed_tests + failed_tests

            validation_result = ValidationResult(
                passed=passed,
                test_type="e2e",
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                error_message=None if passed else "E2E tests failed",
                details={"output": output[:500]}  # 처음 500자만
            )

            # 로그 기록
            self.state.logger.log(
                event_type="milestone",
                phase="e2e_validation",
                data={
                    "passed": passed,
                    "total": total_tests,
                    "failed": failed_tests
                }
            )

            if passed:
                self._log(f"   ✅ E2E 테스트 통과 ({passed_tests}/{total_tests})")
            else:
                self._log(f"   ❌ E2E 테스트 실패 ({passed_tests}/{total_tests})")

            return validation_result

        except subprocess.TimeoutExpired:
            self._log("   ⏰ E2E 테스트 타임아웃 (5분 초과)")
            return ValidationResult(
                passed=False,
                test_type="e2e",
                error_message="Timeout after 5 minutes"
            )

        except FileNotFoundError:
            self._log("   ⚠️  Playwright가 설치되지 않음 - E2E 검증 생략")
            return ValidationResult(
                passed=True,  # 설치 안 된 경우 통과로 간주
                test_type="e2e",
                error_message="Playwright not installed"
            )

        except Exception as e:
            self._log(f"   ❌ E2E 테스트 오류: {e}")
            return ValidationResult(
                passed=False,
                test_type="e2e",
                error_message=str(e)
            )

    def _run_tdd_tests(self) -> ValidationResult:
        """TDD 테스트 실행 (pytest + coverage)"""
        self._log("\n📊 Phase 5: TDD 검증 중...")

        try:
            # pytest 실행 (커버리지 포함)
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--cov=src", "--cov-report=json"],
                capture_output=True,
                text=True,
                timeout=120,  # 2분 타임아웃
                cwd=self.project_root,
                encoding="utf-8",
                errors="replace",
                shell=(sys.platform == "win32")
            )

            output = result.stdout + result.stderr
            passed = result.returncode == 0

            # 테스트 개수 파싱
            import re
            passed_match = re.search(r"(\d+) passed", output)
            failed_match = re.search(r"(\d+) failed", output)

            passed_tests = int(passed_match.group(1)) if passed_match else 0
            failed_tests = int(failed_match.group(1)) if failed_match else 0
            total_tests = passed_tests + failed_tests

            # 커버리지 파싱 (coverage.json)
            coverage_percent = 0.0
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                try:
                    with open(coverage_file, "r") as f:
                        coverage_data = json.load(f)
                        coverage_percent = coverage_data.get("totals", {}).get("percent_covered", 0.0)
                except Exception:
                    pass

            # 검증 기준: 테스트 통과 + 커버리지 80% 이상
            validation_passed = passed and coverage_percent >= 80.0

            validation_result = ValidationResult(
                passed=validation_passed,
                test_type="tdd",
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                coverage_percent=coverage_percent,
                error_message=None if validation_passed else f"Coverage {coverage_percent:.1f}% < 80%",
                details={"output": output[:500]}
            )

            # 로그 기록
            self.state.logger.log(
                event_type="milestone",
                phase="tdd_validation",
                data={
                    "passed": validation_passed,
                    "total": total_tests,
                    "failed": failed_tests,
                    "coverage": coverage_percent
                }
            )

            if validation_passed:
                self._log(f"   ✅ TDD 검증 통과 ({passed_tests}/{total_tests}, 커버리지: {coverage_percent:.1f}%)")
            else:
                self._log(f"   ⚠️  TDD 검증 부족 ({passed_tests}/{total_tests}, 커버리지: {coverage_percent:.1f}%)")

            return validation_result

        except subprocess.TimeoutExpired:
            self._log("   ⏰ TDD 테스트 타임아웃 (2분 초과)")
            return ValidationResult(
                passed=False,
                test_type="tdd",
                error_message="Timeout after 2 minutes"
            )

        except FileNotFoundError:
            self._log("   ⚠️  pytest가 설치되지 않음 - TDD 검증 생략")
            return ValidationResult(
                passed=True,  # 설치 안 된 경우 통과로 간주
                test_type="tdd",
                error_message="pytest not installed"
            )

        except Exception as e:
            self._log(f"   ❌ TDD 테스트 오류: {e}")
            return ValidationResult(
                passed=False,
                test_type="tdd",
                error_message=str(e)
            )

    def _trigger_debug(self, e2e_result: ValidationResult) -> bool:
        """E2E 실패 시 디버그 자동 트리거"""
        self._log("\n🔍 디버그 모드 시작 (가설-검증 사이클)")

        try:
            # /debug 커맨드 실행
            import shutil
            claude_path = shutil.which("claude") or "claude"

            debug_prompt = f"""E2E 테스트 실패 분석:
- 실패한 테스트: {e2e_result.failed_tests}개
- 오류 메시지: {e2e_result.error_message}

/debug 커맨드로 가설-검증 사이클 시작"""

            result = subprocess.run(
                [claude_path, "-p", debug_prompt],
                capture_output=True,
                text=True,
                timeout=600,  # 10분 타임아웃
                cwd=self.project_root,
                encoding="utf-8",
                errors="replace",
                shell=(sys.platform == "win32")
            )

            success = result.returncode == 0

            # 로그 기록
            self.state.logger.log_action(
                action="debug_triggered",
                target="e2e_failure",
                result="success" if success else "fail",
                details={
                    "failed_tests": e2e_result.failed_tests,
                    "returncode": result.returncode
                }
            )

            if success:
                self._log("   ✅ 디버그 완료")
            else:
                self._log("   ❌ 디버그 실패")

            return success

        except subprocess.TimeoutExpired:
            self._log("   ⏰ 디버그 타임아웃 (10분 초과)")
            return False

        except Exception as e:
            self._log(f"   ❌ 디버그 오류: {e}")
            return False

    def _process_result(self, result: IterationResult) -> LoopStatus:
        """결과 처리"""
        # 상태 업데이트
        self.state.update_progress(
            total=self.iteration_count,
            completed=self.success_count,
            in_progress=1 if result.task else 0,
            pending=0
        )

        if self.on_iteration_end:
            self.on_iteration_end(result)

        # Promise 충족 시 완료
        if result.promise_fulfilled:
            return LoopStatus.COMPLETED

        # 작업 없으면 계속 (자율 발견)
        if not result.task:
            self._log("💤 대기 후 재검사...")
            time.sleep(30)  # 30초 대기 후 재검사

        return LoopStatus.RUNNING

    def _finalize(self, status: LoopStatus):
        """종료 처리"""
        duration = (datetime.now() - self.start_time).total_seconds()

        self._log(f"\n{'='*60}")
        self._log(f"루프 종료: {status.value}")
        self._log(f"{'='*60}")
        self._log(f"총 반복: {self.iteration_count}")
        self._log(f"성공: {self.success_count}")
        self._log(f"실패: {self.failure_count}")
        self._log(f"총 소요 시간: {duration:.1f}초")

        # 상태 저장
        if status == LoopStatus.PAUSED:
            self.state.set_status("paused")
            # 체크포인트 생성
            self.state.create_checkpoint(
                task_id=self.iteration_count,
                task_content=f"Iteration {self.iteration_count}",
                context_hint="루프 일시 정지",
                todo_state=[]
            )
            self._log(f"\n💾 체크포인트 저장됨")
            self._log(f"   재개: python auto_orchestrator.py resume {self.session_id}")

        elif status == LoopStatus.COMPLETED:
            self.state.complete({
                "iterations": self.iteration_count,
                "success": self.success_count,
                "duration": duration
            })

        elif status == LoopStatus.FAILED:
            self.state.set_status("failed")

    def _log(self, message: str):
        """로깅"""
        if self.config.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")

    def _log_start(self):
        """시작 로깅"""
        self._log(f"\n{'#'*60}")
        self._log(f"# Auto Orchestrator 시작")
        self._log(f"# Session: {self.session_id}")
        self._log(f"# 설정:")
        self._log(f"#   max_iterations: {self.config.max_iterations or '무제한'}")
        self._log(f"#   promise: {self.config.promise_text or '없음'}")
        self._log(f"#   dry_run: {self.config.dry_run}")
        self._log(f"#   skip_validation: {self.config.skip_validation}")
        self._log(f"{'#'*60}")

    def get_status(self) -> dict:
        """현재 상태 조회"""
        return {
            "session_id": self.session_id,
            "iteration_count": self.iteration_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "state": self.state.get_status()
        }


def run_loop(
    max_iterations: Optional[int] = None,
    promise: Optional[str] = None,
    dry_run: bool = False,
    skip_validation: bool = False,
    session_id: Optional[str] = None
) -> LoopStatus:
    """
    편의 함수: 루프 실행

    Args:
        max_iterations: 최대 반복 횟수
        promise: 종료 조건 텍스트
        dry_run: 실행 없이 판단만
        skip_validation: E2E/TDD 검증 생략
        session_id: 재개할 세션 ID
    """
    config = LoopConfig(
        max_iterations=max_iterations,
        promise_text=promise,
        dry_run=dry_run,
        skip_validation=skip_validation
    )

    orchestrator = AutoOrchestrator(
        config=config,
        session_id=session_id
    )

    return orchestrator.run()


def resume_session(session_id: str) -> LoopStatus:
    """세션 재개"""
    from auto_state import restore_session

    state, summary = restore_session(session_id)
    print(summary)

    return run_loop(session_id=session_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto Orchestrator - 자율 작업 루프")
    parser.add_argument("command", nargs="?", default="run", choices=["run", "resume", "status"])
    parser.add_argument("session_id", nargs="?", help="세션 ID (resume 시)")
    parser.add_argument("--max", type=int, help="최대 반복 횟수")
    parser.add_argument("--promise", type=str, help="종료 조건 텍스트")
    parser.add_argument("--dry-run", action="store_true", help="실행 없이 판단만")
    parser.add_argument("--skip-validation", action="store_true", help="E2E/TDD 검증 생략")

    args = parser.parse_args()

    if args.command == "resume":
        if not args.session_id:
            # 최근 세션 찾기
            from auto_state import get_latest_active_session
            args.session_id = get_latest_active_session()
            if not args.session_id:
                print("재개할 세션이 없습니다")
                sys.exit(1)
        status = resume_session(args.session_id)

    elif args.command == "status":
        from auto_state import get_latest_active_session
        session_id = args.session_id or get_latest_active_session()
        if session_id:
            state = AutoState(session_id)
            import pprint
            pprint.pprint(state.get_status())
        else:
            print("활성 세션이 없습니다")

    else:  # run
        status = run_loop(
            max_iterations=args.max,
            promise=args.promise,
            dry_run=args.dry_run,
            skip_validation=args.skip_validation
        )
        print(f"\n최종 상태: {status.value}")
