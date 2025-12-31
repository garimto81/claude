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
    verbose: bool = True
    context_limit: int = 90               # Context % 임계값
    cooldown_seconds: int = 5             # 반복 간 대기 시간
    retry_on_error: int = 3               # 에러 시 재시도 횟수


@dataclass
class IterationResult:
    """반복 결과"""
    success: bool
    task: Optional[DiscoveredTask]
    output: str
    duration_seconds: float
    promise_fulfilled: bool = False
    error: Optional[str] = None


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

        # 4. Promise 체크
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
            promise_fulfilled=promise_fulfilled
        )

    def _execute_task(self, task: DiscoveredTask) -> tuple[str, bool]:
        """Claude Code로 작업 실행"""
        self._log(f"\n🚀 Claude Code 실행: {task.command}")

        try:
            # Claude Code 호출
            # 주의: 실제 환경에서는 claude 명령어 경로 확인 필요
            result = subprocess.run(
                ["claude", "-p", task.command],
                capture_output=True,
                text=True,
                timeout=600,  # 10분 타임아웃
                cwd=self.project_root,
                encoding="utf-8",
                errors="replace"
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
    session_id: Optional[str] = None
) -> LoopStatus:
    """
    편의 함수: 루프 실행

    Args:
        max_iterations: 최대 반복 횟수
        promise: 종료 조건 텍스트
        dry_run: 실행 없이 판단만
        session_id: 재개할 세션 ID
    """
    config = LoopConfig(
        max_iterations=max_iterations,
        promise_text=promise,
        dry_run=dry_run
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
            dry_run=args.dry_run
        )
        print(f"\n최종 상태: {status.value}")
