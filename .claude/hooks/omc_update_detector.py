#!/usr/bin/env python3
"""
OMC Plugin Update Detector — SessionStart hook

OMC 플러그인 버전 변경 감지 → 로컬 에이전트와 diff 분석 → 보고.
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime

# Paths
OMC_PLUGIN_DIR = (
    Path.home() / "AppData" / "Roaming" / "npm" / "node_modules" / "oh-my-claude-sisyphus"
)
LOCAL_AGENTS_DIR = Path("C:/claude/.claude/agents")
VERSION_CACHE = Path("C:/claude/.omc/omc-plugin-version.json")


def _file_hash(path: Path) -> str | None:
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except Exception:
        return None


def _get_plugin_version() -> str | None:
    pkg = OMC_PLUGIN_DIR / "package.json"
    if not pkg.exists():
        return None
    try:
        with open(pkg, "r", encoding="utf-8") as f:
            return json.load(f).get("version")
    except Exception:
        return None


def _get_stored() -> dict:
    if not VERSION_CACHE.exists():
        return {}
    try:
        with open(VERSION_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(version: str, diff: dict):
    VERSION_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(VERSION_CACHE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "version": version,
                "checked_at": datetime.now().isoformat(),
                "diff": diff,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )


def _compare_agents() -> dict:
    """로컬 vs 플러그인 에이전트 파일 비교"""
    plugin_dir = OMC_PLUGIN_DIR / "agents"
    if not plugin_dir.exists() or not LOCAL_AGENTS_DIR.exists():
        return {"new": [], "modified": []}

    plugin_files = {f.name: f for f in plugin_dir.glob("*.md")}
    local_files = {f.name: f for f in LOCAL_AGENTS_DIR.glob("*.md")}

    new = []
    modified = []

    for name, pf in plugin_files.items():
        if name not in local_files:
            new.append(name)
        elif _file_hash(pf) != _file_hash(local_files[name]):
            modified.append(name)

    return {"new": new, "modified": modified}


def _compare_skills() -> dict:
    """플러그인 스킬 변경 감지 (SKILL.md 해시 비교)"""
    plugin_skills = OMC_PLUGIN_DIR / "skills"
    if not plugin_skills.exists():
        return {"changed_skills": []}

    stored = _get_stored()
    old_hashes = stored.get("skill_hashes", {})
    new_hashes = {}
    changed = []

    for skill_dir in plugin_skills.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            h = _file_hash(skill_file)
            new_hashes[skill_dir.name] = h
            if skill_dir.name in old_hashes and old_hashes[skill_dir.name] != h:
                changed.append(skill_dir.name)

    return {"changed_skills": changed, "skill_hashes": new_hashes}


def main():
    try:
        current = _get_plugin_version()
        if not current:
            # OMC not installed
            print(json.dumps({"continue": True}))
            return

        stored = _get_stored()
        stored_version = stored.get("version")

        if current == stored_version:
            print(json.dumps({"continue": True}))
            return

        # Version changed — analyze
        agent_diff = _compare_agents()
        skill_diff = _compare_skills()

        parts = []
        if stored_version:
            parts.append(f"OMC plugin update: {stored_version} -> {current}")
        else:
            parts.append(f"OMC plugin version recorded: {current}")

        if agent_diff["new"]:
            parts.append(
                f"  New agents ({len(agent_diff['new'])}): "
                + ", ".join(a.replace(".md", "") for a in agent_diff["new"])
            )
        if agent_diff["modified"]:
            parts.append(
                f"  Modified agents ({len(agent_diff['modified'])}): "
                + ", ".join(a.replace(".md", "") for a in agent_diff["modified"])
            )
        if skill_diff["changed_skills"]:
            parts.append(
                f"  Changed skills ({len(skill_diff['changed_skills'])}): "
                + ", ".join(skill_diff["changed_skills"])
            )

        has_changes = (
            agent_diff["new"] or agent_diff["modified"] or skill_diff["changed_skills"]
        )
        if has_changes and stored_version:
            parts.append(
                "  Tip: Review changes with "
                "`/auto \"omc update review\"` to sync improvements"
            )

        # Save state
        save_data = {
            "new": agent_diff["new"],
            "modified": agent_diff["modified"],
            "changed_skills": skill_diff["changed_skills"],
        }
        # Persist skill hashes for next comparison
        _save_state(current, save_data)
        # Save skill hashes separately in version cache
        if skill_diff.get("skill_hashes"):
            cache = _get_stored()
            cache["skill_hashes"] = skill_diff["skill_hashes"]
            with open(VERSION_CACHE, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)

        message = "\n".join(parts)
        print(json.dumps({"continue": True, "message": message}))

    except Exception:
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
