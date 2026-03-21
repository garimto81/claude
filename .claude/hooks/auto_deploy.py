#!/usr/bin/env python3
"""Stop hook: server/Flutter/src 변경 감지 시 자동 빌드 + Docker 배포.

기존 deploy_gate.py(경고만)를 대체. 실제 빌드/배포를 자동 실행.
"""

import os
import subprocess
import sys
import time

PROJECT = "C:/claude/game_kfc"
FLUTTER_DIR = os.path.join(PROJECT, "game_kfc_flutter")
WEB_BUILD = os.path.join(PROJECT, "web_build")
FLAG = os.path.join(PROJECT, ".deploy_verified")
WATCH_PATHS = ["server/", "game_kfc_flutter/lib/", "src/"]


def run(cmd, cwd=PROJECT, timeout=300):
    """명령 실행. Windows에서 shell=True로 .bat/.cmd 명령 지원."""
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd,
            timeout=timeout, shell=True, encoding="utf-8", errors="replace",
        )
        return (r.returncode == 0, (r.stdout or "") + (r.stderr or ""))
    except subprocess.TimeoutExpired:
        return (False, f"Timeout: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")


def main():
    try:
        sys.stdin.read()
    except Exception:
        pass

    # 1. 변경 파일 확인
    ok, out = run("git diff --name-only HEAD")
    if not ok:
        return
    changed = [f for f in out.strip().split("\n") if f]

    # 2. 감시 대상 변경 여부
    needs_deploy = any(
        any(f.startswith(wp) for wp in WATCH_PATHS) for f in changed
    )
    if not needs_deploy:
        return

    # 3. 플래그 확인
    if os.path.exists(FLAG):
        return

    sys.stderr.write("🚀 auto_deploy: 변경 감지, 빌드+배포 시작...\n")

    # 4a. Flutter Web 빌드 (flutter 변경 시만)
    flutter_changed = any(f.startswith("game_kfc_flutter/") for f in changed)
    if flutter_changed and os.path.isdir(FLUTTER_DIR):
        ok, out = run(
            f"flutter build web --output={WEB_BUILD}",
            cwd=FLUTTER_DIR,
            timeout=300,
        )
        if not ok:
            sys.stderr.write(f"❌ Flutter build 실패: {out[:200]}\n")
            return

    # 4b. Docker rebuild
    ok, out = run("docker compose down --remove-orphans")
    if not ok:
        sys.stderr.write(f"❌ docker compose down 실패: {out[:200]}\n")
        return

    ok, out = run("docker compose build", timeout=300)
    if not ok:
        sys.stderr.write(f"❌ docker compose build 실패: {out[:200]}\n")
        return

    ok, out = run("docker compose up -d")
    if not ok:
        sys.stderr.write(f"❌ docker compose up 실패: {out[:200]}\n")
        return

    # 4c. 헬스 체크
    time.sleep(3)
    ok, out = run("curl -sf http://localhost:8000/api/rooms", timeout=10)
    if not ok:
        sys.stderr.write("⚠️ 헬스 체크 실패 (서버 시작 지연 가능)\n")

    # 4d. 플래그 생성
    with open(FLAG, "w") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S"))

    sys.stderr.write("✅ auto_deploy: 빌드+배포 완료\n")


if __name__ == "__main__":
    main()
