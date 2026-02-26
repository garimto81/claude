#!/usr/bin/env python3
"""PreCompact State Saver — Context Compaction 전 상태 보존.

bkit Context Engineering FR-07 기반 OMC 적용.
Context Compaction 직전에 현재 PDCA 상태, TODO 목록,
진행 중 파일 목록을 직렬화하여 저장합니다.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(r"C:\claude")
OMC_DIR = PROJECT_ROOT / ".omc"
CONTEXT_DIR = OMC_DIR / "context"
SUMMARY_FILE = CONTEXT_DIR / "compact_summary.md"
SNAPSHOTS_DIR = PROJECT_ROOT / "docs" / ".pdca-snapshots"
MAX_SNAPSHOTS = 10


def get_current_state() -> dict:
    """현재 작업 상태를 수집한다."""
    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": None,
        "feature": None,
        "todos": [],
        "in_progress_files": [],
    }

    # ultrawork-state.json에서 Phase 정보
    ultrawork = OMC_DIR / "ultrawork-state.json"
    if ultrawork.exists():
        try:
            data = json.loads(ultrawork.read_text(encoding="utf-8"))
            state["phase"] = data.get("currentPhase")
            state["feature"] = data.get("feature")
        except (json.JSONDecodeError, KeyError):
            pass

    # pdca-status.json에서 활성 피처 정보
    pdca_status = PROJECT_ROOT / "docs" / ".pdca-status.json"
    if pdca_status.exists():
        try:
            data = json.loads(pdca_status.read_text(encoding="utf-8"))
            if not state["feature"] and data.get("primaryFeature"):
                state["feature"] = data["primaryFeature"]
            state["pdca_phase"] = data.get("phase")
        except (json.JSONDecodeError, KeyError):
            pass

    return state


def save_snapshot(state: dict) -> None:
    """PDCA 스냅샷을 저장한다 (최대 MAX_SNAPSHOTS개 유지)."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    snapshot_file = SNAPSHOTS_DIR / f"snapshot-compact-{timestamp}.json"
    snapshot_file.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 오래된 스냅샷 정리
    snapshots = sorted(SNAPSHOTS_DIR.glob("snapshot-compact-*.json"))
    while len(snapshots) > MAX_SNAPSHOTS:
        snapshots[0].unlink()
        snapshots.pop(0)


def generate_summary(state: dict) -> str:
    """compact_summary.md 내용을 생성한다."""
    lines = [
        "# Session Compact Summary",
        "",
        f"> 저장 시각: {state['timestamp']}",
        "",
    ]

    if state.get("feature"):
        lines.append(f"## 진행 중 Feature: {state['feature']}")
        lines.append("")

    if state.get("phase"):
        lines.append(f"## 현재 Phase: {state['phase']}")
        lines.append("")

    if state.get("pdca_phase"):
        lines.append(f"## PDCA Phase: {state['pdca_phase']}")
        lines.append("")

    if state.get("todos"):
        lines.append("## TODO 목록")
        lines.append("")
        for todo in state["todos"]:
            status = "x" if todo.get("done") else " "
            lines.append(f"- [{status}] {todo.get('text', '')}")
        lines.append("")

    if state.get("in_progress_files"):
        lines.append("## 작업 중 파일")
        lines.append("")
        for f in state["in_progress_files"]:
            lines.append(f"- {f}")
        lines.append("")

    lines.append("---")
    lines.append("*이 파일은 PreCompact Hook에 의해 자동 생성됩니다.*")

    return "\n".join(lines)


def main() -> None:
    CONTEXT_DIR.mkdir(parents=True, exist_ok=True)

    state = get_current_state()
    save_snapshot(state)

    summary = generate_summary(state)
    SUMMARY_FILE.write_text(summary, encoding="utf-8")

    print(f"[PreCompact] 상태 저장 완료: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
