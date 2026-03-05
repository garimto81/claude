#!/usr/bin/env python3
"""Create Kickoff Epic + Stories for EBS 2026 annual plan.

Creates 1 Epic (Kickoff 기획서) with 8 child Stories in Jira PV project.
Independent from existing 8-Epic structure (PV-6512~PV-6563).

Usage:
    python scripts/create_kickoff_epic.py          # dry-run
    python scripts/create_kickoff_epic.py --apply  # create in Jira
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from lib.jira_client import get_config, create_issue

PROJECT_KEY = "PV"
EPIC_TYPE_ID = "10000"
STORY_TYPE_ID = "10001"


# ---------------------------------------------------------------------------
# ADF helpers (reused from create_epics_v2.py)
# ---------------------------------------------------------------------------

def adf_doc(*blocks):
    return {"version": 1, "type": "doc", "content": list(blocks)}


def adf_heading(text, level=2):
    return {"type": "heading", "attrs": {"level": level},
            "content": [{"type": "text", "text": text}]}


def adf_paragraph(text):
    return {"type": "paragraph",
            "content": [{"type": "text", "text": text}]}


def adf_table(headers, rows):
    def cell(text, is_header=False):
        return {"type": "tableHeader" if is_header else "tableCell",
                "content": [adf_paragraph(str(text))]}
    header_row = {"type": "tableRow", "content": [cell(h, True) for h in headers]}
    body_rows = [{"type": "tableRow", "content": [cell(c) for c in row]} for row in rows]
    return {"type": "table", "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
            "content": [header_row] + body_rows}


def adf_rule():
    return {"type": "rule"}


# ---------------------------------------------------------------------------
# Epic Description (ADF)
# ---------------------------------------------------------------------------

EPIC_DESCRIPTION = adf_doc(
    adf_heading("2026 연간 목표", 2),
    adf_table(
        ["반기", "목표", "핵심 산출물", "Epic 연관"],
        [
            ["상반기 (3~6월)", "RFID 보드 연결 + Overlay POC 검증", "POC 데모, 검증 보고서", "Epic 1, 3"],
            ["하반기 (7~12월)", "홀덤 기준 GFX 구현", "홀덤 방송 GFX 빌드", "Epic 2, 3"],
        ],
    ),
    adf_rule(),
    adf_heading("상반기 마일스톤", 2),
    adf_table(
        ["월", "기획", "개발"],
        [
            ["3월", "요구사항 정의, POC 범위 확정", "RFID 보드 환경 구축"],
            ["4월", "UI/UX 와이어프레임", "RFID 데이터 수신 연동"],
            ["5월", "Overlay 디자인", "Overlay 프로토타입 렌더링"],
            ["6월", "POC 검증 기준 정의", "통합 데모 + 검증 보고서"],
        ],
    ),
    adf_rule(),
    adf_heading("하반기 마일스톤", 2),
    adf_table(
        ["월", "기획", "개발"],
        [
            ["7~8월", "홀덤 규칙 상세 스펙", "게임 엔진 코어 구현"],
            ["9~10월", "GFX 디자인 가이드", "GFX 렌더링 구현"],
            ["11월", "QA 시나리오", "통합 테스트"],
            ["12월", "릴리스 체크리스트", "릴리스 빌드"],
        ],
    ),
)


# ---------------------------------------------------------------------------
# Stories data
# ---------------------------------------------------------------------------

STORIES = [
    {
        "summary": "[Kickoff] 상반기 목표: RFID+Overlay POC 검증",
        "description": adf_doc(
            adf_heading("상반기 목표 정의", 3),
            adf_paragraph("RFID 보드 연결 → 데이터 overlay 화면 표시까지의 POC 검증 범위를 확정한다."),
            adf_table(
                ["항목", "내용"],
                [
                    ["반기", "H1 (3~6월)"],
                    ["구분", "기획"],
                    ["핵심 산출물", "POC 범위 문서, 요구사항 정의서"],
                ],
            ),
        ),
    },
    {
        "summary": "[Kickoff] RFID 보드 연동 환경 구축",
        "description": adf_doc(
            adf_heading("RFID 보드 연동 환경 구축", 3),
            adf_paragraph("RFID 하드웨어 보드와의 물리적/소프트웨어 연결 환경을 구성한다."),
            adf_table(
                ["항목", "내용"],
                [
                    ["반기", "H1 (3~6월)"],
                    ["구분", "개발"],
                    ["핵심 산출물", "RFID 보드 연동 프로토타입, 데이터 수신 검증"],
                ],
            ),
        ),
    },
    {
        "summary": "[Kickoff] Overlay 데이터 표시 프로토타입",
        "description": adf_doc(
            adf_heading("Overlay 데이터 표시 프로토타입", 3),
            adf_paragraph("RFID에서 수신한 카드 데이터를 방송 오버레이 화면에 표시하는 프로토타입을 구현한다."),
            adf_table(
                ["항목", "내용"],
                [
                    ["반기", "H1 (3~6월)"],
                    ["구분", "개발"],
                    ["핵심 산출물", "Overlay 렌더링 프로토타입"],
                ],
            ),
        ),
    },
    {
        "summary": "[Kickoff] POC 통합 데모 및 검증 보고서",
        "description": adf_doc(
            adf_heading("POC 통합 데모 및 검증 보고서", 3),
            adf_paragraph("RFID + Overlay 통합 데모를 실행하고, POC 검증 결과를 보고서로 정리한다."),
            adf_table(
                ["항목", "내용"],
                [
                    ["반기", "H1 (3~6월)"],
                    ["구분", "기획"],
                    ["핵심 산출물", "통합 데모 영상, POC 검증 보고서"],
                ],
            ),
        ),
    },
    {
        "summary": "[Kickoff] 하반기 목표: 홀덤 기준 GFX 구현",
        "description": adf_doc(
            adf_heading("하반기 목표 정의", 3),
            adf_paragraph("홀덤 게임 규칙 기반의 방송 GFX 시스템 구현 범위를 확정한다."),
            adf_table(
                ["항목", "내용"],
                [
                    ["반기", "H2 (7~12월)"],
                    ["구분", "기획"],
                    ["핵심 산출물", "홀덤 GFX 스펙 문서, 디자인 가이드"],
                ],
            ),
        ),
    },
    {
        "summary": "[Kickoff] 홀덤 규칙 엔진 코어",
        "description": adf_doc(
            adf_heading("홀덤 규칙 엔진 코어", 3),
            adf_paragraph("홀덤 게임 규칙(핸드 랭킹, 베팅 구조, 게임 흐름)을 처리하는 엔진 코어를 구현한다."),
            adf_table(
                ["항목", "내용"],
                [
                    ["반기", "H2 (7~12월)"],
                    ["구분", "개발"],
                    ["핵심 산출물", "홀덤 규칙 엔진 빌드"],
                ],
            ),
        ),
    },
    {
        "summary": "[Kickoff] 홀덤 방송 GFX 렌더링",
        "description": adf_doc(
            adf_heading("홀덤 방송 GFX 렌더링", 3),
            adf_paragraph("홀덤 게임 상태를 시각화하는 방송 그래픽(오버레이, 카드, 플레이어 정보)을 렌더링한다."),
            adf_table(
                ["항목", "내용"],
                [
                    ["반기", "H2 (7~12월)"],
                    ["구분", "개발"],
                    ["핵심 산출물", "홀덤 GFX 렌더링 빌드"],
                ],
            ),
        ),
    },
    {
        "summary": "[Kickoff] 통합 테스트 및 릴리스",
        "description": adf_doc(
            adf_heading("통합 테스트 및 릴리스", 3),
            adf_paragraph("홀덤 규칙 엔진 + GFX 렌더링의 통합 테스트를 수행하고 릴리스 빌드를 생성한다."),
            adf_table(
                ["항목", "내용"],
                [
                    ["반기", "H2 (7~12월)"],
                    ["구분", "개발"],
                    ["핵심 산출물", "통합 테스트 보고서, 릴리스 빌드"],
                ],
            ),
        ),
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    dry_run = "--apply" not in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN — Jira will NOT be modified")
        print("Pass --apply to actually create issues")
        print("=" * 60)

    cfg = get_config()
    if not cfg["email"] or not cfg["token"]:
        print("ERROR: ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN required.", file=sys.stderr)
        sys.exit(1)

    epic_summary = "[EBS] Kickoff 기획서 — 2026 연간 목표"

    print(f"\n{'═' * 60}")
    print(f"Epic: {epic_summary}")
    print(f"  Stories: {len(STORIES)}")

    if dry_run:
        print(f"  [DRY RUN] Would create Epic")
        for j, story in enumerate(STORIES, 1):
            print(f"    Story {j}: {story['summary']}")
        print(f"\n{'═' * 60}")
        print(f"Summary: 1 Epic, {len(STORIES)} Stories")
        print("(dry run — nothing created)")
        return

    # Create Epic
    epic_key = None
    try:
        epic_fields = {
            "project": {"key": PROJECT_KEY},
            "issuetype": {"id": EPIC_TYPE_ID},
            "summary": epic_summary,
            "description": EPIC_DESCRIPTION,
        }
        result = create_issue(epic_fields, cfg=cfg)
        epic_key = result.get("key", "???")
        print(f"  ✓ Epic created: {epic_key}")
    except Exception as e:
        print(f"  ✗ Epic FAILED: {e}", file=sys.stderr)
        sys.exit(1)

    # Create Stories
    created_stories = 0
    for j, story in enumerate(STORIES, 1):
        try:
            story_fields = {
                "project": {"key": PROJECT_KEY},
                "issuetype": {"id": STORY_TYPE_ID},
                "summary": story["summary"],
                "description": story["description"],
                "parent": {"key": epic_key},
            }
            result = create_issue(story_fields, cfg=cfg)
            story_key = result.get("key", "???")
            print(f"    ✓ Story {j}: {story_key} — {story['summary']}")
            created_stories += 1
        except Exception as e:
            print(f"    ✗ Story {j} FAILED: {e}")

    print(f"\n{'═' * 60}")
    print(f"Summary: Epic {epic_key} + {created_stories}/{len(STORIES)} Stories created")
    print(f"URL: {cfg['base_url']}/browse/{epic_key}")


if __name__ == "__main__":
    main()
