#!/usr/bin/env python
"""
Ralph CLI - 프롬프트 반복 실행 오케스트레이터

Ralph Wiggum 철학: 같은 프롬프트를 반복하여 점진적 개선

사용법:
    python ralph_cli.py "프롬프트 내용"
    python ralph_cli.py "프롬프트" --max 10
    python ralph_cli.py "프롬프트" --promise "DONE"
    python ralph_cli.py --prompt-file prompt.txt
"""

import argparse
import subprocess
import sys
import time
import io
from datetime import datetime
from pathlib import Path

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def find_claude_executable() -> str:
    """Claude Code 실행 파일 찾기"""
    import shutil
    import os

    # 1. PATH에서 찾기
    claude_path = shutil.which("claude")
    if claude_path:
        return claude_path

    # 2. Windows npm 전역 경로
    if sys.platform == "win32":
        npm_path = Path(os.environ.get("APPDATA", "")) / "npm"
        for ext in [".cmd", ".exe", ""]:
            candidate = npm_path / f"claude{ext}"
            if candidate.exists():
                return str(candidate)

    # 3. 기본값
    return "claude"


def run_claude_code(prompt: str, continue_session: bool = True) -> tuple[int, str]:
    """Claude Code 실행"""
    claude_exe = find_claude_executable()

    cmd = [claude_exe]

    if continue_session:
        cmd.append("--continue")

    cmd.extend(["--print", prompt])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,  # 10분 타임아웃
            shell=(sys.platform == "win32")  # Windows에서 shell=True
        )
        output = result.stdout + result.stderr
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return 1, "Error: Timeout (10분 초과)"
    except FileNotFoundError:
        return 1, f"Error: Claude Code를 찾을 수 없습니다. 경로: {claude_exe}"
    except Exception as e:
        return 1, f"Error: {e}"


def check_promise(output: str, promise: str) -> bool:
    """출력에서 promise 태그 확인"""
    return f"<promise>{promise}</promise>" in output


def run_ralph_loop(
    prompt: str,
    max_iterations: int = 0,
    promise: str = None,
    cooldown: int = 3,
    verbose: bool = True
):
    """Ralph Loop 실행"""

    iteration = 0
    start_time = datetime.now()

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    Ralph Loop Orchestrator                      ║
╠═══════════════════════════════════════════════════════════════╣
║  Prompt: {prompt[:50] + '...' if len(prompt) > 50 else prompt:<53} ║
║  Max iterations: {max_iterations if max_iterations > 0 else 'unlimited':<43} ║
║  Promise: {promise if promise else 'none':<52} ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    while True:
        iteration += 1

        # Max iterations 체크
        if max_iterations > 0 and iteration > max_iterations:
            print(f"\n✅ Max iterations ({max_iterations}) 도달. 종료.")
            break

        print(f"\n{'='*60}")
        print(f"🔄 Iteration {iteration}")
        print(f"{'='*60}")

        # Claude Code 실행
        return_code, output = run_claude_code(prompt, continue_session=(iteration > 1))

        if verbose:
            # 출력의 마지막 500자만 표시
            preview = output[-500:] if len(output) > 500 else output
            print(f"\n📤 Output preview:\n{preview}")

        # Promise 체크
        if promise and check_promise(output, promise):
            print(f"\n🎉 Promise fulfilled: <promise>{promise}</promise>")
            break

        # 에러 체크
        if return_code != 0:
            print(f"\n⚠️ Claude Code returned error code: {return_code}")
            print("Continuing anyway...")

        # Cooldown
        if cooldown > 0:
            print(f"\n⏳ Cooldown: {cooldown}초...")
            time.sleep(cooldown)

    # 완료
    elapsed = datetime.now() - start_time
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    Ralph Loop 완료                              ║
╠═══════════════════════════════════════════════════════════════╣
║  총 Iterations: {iteration:<46} ║
║  소요 시간: {str(elapsed)[:10]:<50} ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(
        description="Ralph Loop - 프롬프트 반복 실행 오케스트레이터",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 기본 실행 (무한 반복)
  python ralph_cli.py "워크플로우 최적화"

  # 최대 10회 반복
  python ralph_cli.py "버그 수정" --max 10

  # 완료 조건 설정
  python ralph_cli.py "테스트 작성" --promise "ALL_TESTS_PASS"

  # 파일에서 프롬프트 읽기
  python ralph_cli.py --prompt-file prompt.txt --max 5
"""
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="반복할 프롬프트"
    )
    parser.add_argument(
        "--prompt-file",
        type=str,
        help="프롬프트 파일 경로"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=0,
        help="최대 반복 횟수 (0=무한)"
    )
    parser.add_argument(
        "--promise",
        type=str,
        help="종료 조건 (<promise>TEXT</promise>)"
    )
    parser.add_argument(
        "--cooldown",
        type=int,
        default=3,
        help="반복 간 대기 시간 (초, 기본: 3)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="출력 미리보기 생략"
    )

    args = parser.parse_args()

    # 프롬프트 결정
    prompt = None
    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if prompt_path.exists():
            prompt = prompt_path.read_text(encoding="utf-8").strip()
        else:
            print(f"Error: 파일을 찾을 수 없습니다: {args.prompt_file}")
            return 1
    elif args.prompt:
        prompt = args.prompt
    else:
        print("Error: 프롬프트를 지정하세요")
        parser.print_help()
        return 1

    # 실행
    run_ralph_loop(
        prompt=prompt,
        max_iterations=args.max,
        promise=args.promise,
        cooldown=args.cooldown,
        verbose=not args.quiet
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
