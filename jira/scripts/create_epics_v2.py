#!/usr/bin/env python3
"""Create 8-Epic structure with Stories in Jira PV project.

Creates new Epics and their child Stories based on PRD v2.0 structure.
Epic 8 (Skin Editor) is v2.0 scope and labeled accordingly.

Usage:
    python scripts/create_epics_v2.py          # dry-run
    python scripts/create_epics_v2.py --apply  # create in Jira
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from lib.jira_client import get_config, create_issue

PROJECT_KEY = "PV"
EPIC_TYPE_ID = "10000"
TASK_TYPE_ID = "11514"   # 작업 (Story 사용 금지)


# ---------------------------------------------------------------------------
# ADF helpers
# ---------------------------------------------------------------------------

def adf_doc(*blocks):
    return {"version": 1, "type": "doc", "content": list(blocks)}

def adf_heading(text, level=2):
    return {"type": "heading", "attrs": {"level": level},
            "content": [{"type": "text", "text": text}]}

def adf_paragraph(text):
    return {"type": "paragraph",
            "content": [{"type": "text", "text": text}]}

def adf_bold_para(bold_text, normal_text=""):
    content = [{"type": "text", "text": bold_text, "marks": [{"type": "strong"}]}]
    if normal_text:
        content.append({"type": "text", "text": normal_text})
    return {"type": "paragraph", "content": content}

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
# 8-Epic + Stories data
# ---------------------------------------------------------------------------

EPICS_DATA = [
    {
        "summary": "[EBS v2] Epic 1: 카드 인식 시스템",
        "description": adf_doc(
            adf_heading("카드 인식 시스템", 2),
            adf_paragraph("RFID 하드웨어 연동 + 카드 상태 추적 + 오류 복구 + RFID 설정 UI + 카드 관련 TCP 명령"),
            adf_rule(),
            adf_bold_para("Settings UI: ", "5개 (System Tab RFID: Y-03~Y-07)"),
            adf_bold_para("Protocol: ", "12개 (Card 9 + RFID 3)"),
            adf_bold_para("기존 Epic 참조: ", "PV-6466"),
        ),
        "stories": [
            {"summary": "[E1] 1.1 RFID 리더기 연동 (Seat×10, Board, Muck)",
             "description": adf_doc(adf_paragraph("12대 안테나(Seat 10 + Board 1 + Muck 1) 연동. PRD §3 매핑."))},
            {"summary": "[E1] 1.2 이중 연결 복구 (무선/유선 전환, 30초 재연결)",
             "description": adf_doc(adf_paragraph("WiFi 기본 + USB 백업, 자동 전환. PRD §3.2 매핑."))},
            {"summary": "[E1] 1.3 카드 상태 머신 (DECK→DETECTED→DEALT→REVEALED/MUCKED)",
             "description": adf_doc(adf_paragraph("5단계 순환 상태 머신. PRD §3.3 매핑."))},
            {"summary": "[E1] 1.4 수동 복구 (52장 그리드, 재스캔, Miss Deal)",
             "description": adf_doc(adf_paragraph("52장 그리드 UI, FORCE_CARD_SCAN, MISS_DEAL 명령. PRD §3.4, §18 매핑."))},
            {"summary": "[E1] 1.5 RFID 장비 설정 UI (Y-03~Y-07)",
             "description": adf_doc(adf_paragraph("System Tab RFID 섹션 5개 요소. UI PRD Ch.9 매핑."))},
            {"summary": "[E1] 1.6 카드 관련 TCP 명령 처리 (Card 9 + RFID 3)",
             "description": adf_doc(adf_paragraph("Protocol Card(9개) + RFID(3개) = 12개 명령 구현."))},
        ],
    },
    {
        "summary": "[EBS v2] Epic 2: 포커 게임 엔진",
        "description": adf_doc(
            adf_heading("포커 게임 엔진", 2),
            adf_paragraph("포커 규칙 적용 + 게임 상태 관리 + 베팅 + 핸드 평가 + 승률 계산 + 규칙 설정 UI + TCP 명령"),
            adf_rule(),
            adf_bold_para("Settings UI: ", "9개 (Rules Tab 전체: G-32~G-56)"),
            adf_bold_para("Protocol: ", "39개 (Game 13 + Player 21 + Betting 5)"),
            adf_bold_para("기존 Epic 참조: ", "PV-6467"),
        ),
        "stories": [
            {"summary": "[E2] 2.1 22개 포커 변형 규칙 (Community 12, Draw 7, Stud 3)",
             "description": adf_doc(adf_paragraph("PRD §4.1 매핑. 22개 게임 변형 규칙 구현."))},
            {"summary": "[E2] 2.2 게임 상태 전이 (Pre-flop~River, Draw/Stud 특화)",
             "description": adf_doc(adf_paragraph("PRD §4.2 매핑. 게임 타입별 상태 전이 로직."))},
            {"summary": "[E2] 2.3 베팅 구조 (NL/PL/FL + 7가지 Ante)",
             "description": adf_doc(adf_paragraph("PRD §4.3 매핑. No Limit, Pot Limit, Fixed Limit + 7가지 Ante 유형."))},
            {"summary": "[E2] 2.4 특수 규칙 (Bomb Pot, Run It Twice)",
             "description": adf_doc(adf_paragraph("PRD §4.4 매핑. Bomb Pot, Run It Twice, 7-2 Side Bet, Straddle."))},
            {"summary": "[E2] 2.5 핸드 평가기 (Lookup Table, High/Hi-Lo/Lowball)",
             "description": adf_doc(adf_paragraph("PRD §5 매핑. 3가지 평가 룰, Lookup Table 기반 즉시 평가."))},
            {"summary": "[E2] 2.6 승률 계산 엔진 (시뮬레이션 분리, 스트리트별 재계산)",
             "description": adf_doc(adf_paragraph("PRD §5 매핑. HandEvaluation 별도 프로세스, Monte Carlo 비동기."))},
            {"summary": "[E2] 2.7 규칙 설정 UI (Rules Tab G-32~G-56)",
             "description": adf_doc(adf_paragraph("UI PRD Ch.7 매핑. Rules Tab 9개 요소 구현."))},
            {"summary": "[E2] 2.8 게임/플레이어/베팅 TCP 명령 (Game 13 + Player 21 + Betting 5)",
             "description": adf_doc(adf_paragraph("Protocol 39개 명령 구현."))},
        ],
    },
    {
        "summary": "[EBS v2] Epic 3: 방송 그래픽 시스템",
        "description": adf_doc(
            adf_heading("방송 그래픽 시스템", 2),
            adf_paragraph("오버레이 렌더링 + 실시간 시각화 + 애니메이션 + 그래픽/디스플레이 설정 UI + TCP 명령"),
            adf_rule(),
            adf_bold_para("Settings UI: ", "37개 (GFX Tab 24 + Display Tab 13)"),
            adf_bold_para("Protocol: ", "17개 (Display 17)"),
            adf_bold_para("기존 Epic 참조: ", "PV-6468"),
        ),
        "stories": [
            {"summary": "[E3] 3.1 Player Info Panel 렌더링",
             "description": adf_doc(adf_paragraph("PRD §6.1 매핑. 플레이어 정보 오버레이 렌더링."))},
            {"summary": "[E3] 3.2 홀카드/커뮤니티카드 표시",
             "description": adf_doc(adf_paragraph("PRD §6.1 매핑. 카드 그래픽 표시 시스템."))},
            {"summary": "[E3] 3.3 Bottom Info Strip (블라인드, 팟)",
             "description": adf_doc(adf_paragraph("PRD §6.1 매핑. 하단 정보 스트립 렌더링."))},
            {"summary": "[E3] 3.4 Action Badge + 실시간 승률 바",
             "description": adf_doc(adf_paragraph("PRD §6.2 매핑. 액션 배지 및 승률 시각화."))},
            {"summary": "[E3] 3.5 11개 Animation Class 매핑",
             "description": adf_doc(adf_paragraph("PRD §6.3 매핑. 16 Animation State × 11 Animation Class."))},
            {"summary": "[E3] 3.6 그래픽 설정 UI (GFX Tab, 24개 요소)",
             "description": adf_doc(adf_paragraph("UI PRD Ch.6 매핑. Layout, Card & Player, Animation, Branding."))},
            {"summary": "[E3] 3.7 디스플레이 설정 UI (Display Tab, 13개 요소)",
             "description": adf_doc(adf_paragraph("UI PRD Ch.8 매핑. Blinds, Precision, Mode 등."))},
            {"summary": "[E3] 3.8 디스플레이 TCP 명령 처리 (Display 17)",
             "description": adf_doc(adf_paragraph("Protocol Display 17개 명령 구현."))},
        ],
    },
    {
        "summary": "[EBS v2] Epic 4: 방송 송출 파이프라인",
        "description": adf_doc(
            adf_heading("방송 송출 파이프라인", 2),
            adf_paragraph("NDI/HDMI/SDI 출력 + 외부 데이터 API + 입출력 설정 UI"),
            adf_rule(),
            adf_bold_para("Settings UI: ", "20개 (I/O Tab 전체)"),
            adf_bold_para("Protocol: ", "13개 (Media 13)"),
            adf_bold_para("기존 Epic 참조: ", "PV-6469"),
        ),
        "stories": [
            {"summary": "[E4] 4.1 NDI/HDMI 실시간 그래픽 합성 출력",
             "description": adf_doc(adf_paragraph("PRD §7.1 매핑. Internal 합성 + External 전달 모드."))},
            {"summary": "[E4] 4.2 SDI 출력 해상도/프레임레이트 설정",
             "description": adf_doc(adf_paragraph("PRD §7.1 매핑. Fill & Key 모드 포함."))},
            {"summary": "[E4] 4.3 LiveApi 실시간 delta 스트리밍",
             "description": adf_doc(adf_paragraph("PRD §7.2 매핑. 실시간 데이터 스트리밍."))},
            {"summary": "[E4] 4.4 핸드 단위 JSON Export + live_export 트리거",
             "description": adf_doc(adf_paragraph("PRD §7.2 매핑. 핸드 완료 시 자동 Export."))},
            {"summary": "[E4] 4.5 입출력 설정 UI (I/O Tab, 20개 요소)",
             "description": adf_doc(adf_paragraph("UI PRD Ch.5 매핑. Sources + Outputs 섹션 전체."))},
        ],
    },
    {
        "summary": "[EBS v2] Epic 5: 액션 트래커",
        "description": adf_doc(
            adf_heading("액션 트래커", 2),
            adf_paragraph("운영자 태블릿 클라이언트 — UI PRD Ch.10 26개 기능 반영"),
            adf_rule(),
            adf_bold_para("Settings UI: ", "2개 (System Tab AT 관련)"),
            adf_bold_para("Protocol: ", "없음 (WebSocket 클라이언트, Epic 2/7 Protocol 소비자)"),
            adf_bold_para("기존 Epic 참조: ", "PV-6470"),
        ),
        "stories": [
            {"summary": "[E5] 5.1 서버 자동 검색 및 접속",
             "description": adf_doc(adf_paragraph("PRD §8.3, AT-01~AT-03. 브로드캐스트 검색 + 자동 연결."))},
            {"summary": "[E5] 5.2 덱 등록 (52장 UID 매핑)",
             "description": adf_doc(adf_paragraph("PRD §8.1, AT-04~AT-06. REGISTER_DECK 52장 매핑."))},
            {"summary": "[E5] 5.3 좌석별 플레이어 등록 + 칩 스택",
             "description": adf_doc(adf_paragraph("PRD §8.1, AT-07~AT-10. 이름/칩 등록 UI."))},
            {"summary": "[E5] 5.4 베팅 금액 입력 UI",
             "description": adf_doc(adf_paragraph("PRD §8.2, AT-11~AT-14. Predictive Bet 포함."))},
            {"summary": "[E5] 5.5 플레이어 액션 조작 (Fold/Check/Call/Raise)",
             "description": adf_doc(adf_paragraph("PRD §8.2, AT-15~AT-18. 4가지 기본 액션 UI."))},
            {"summary": "[E5] 5.6 게임 상태 동기화 (GameInfoResponse)",
             "description": adf_doc(adf_paragraph("PRD §8.3, AT-19~AT-22. 서버 상태 실시간 반영."))},
            {"summary": "[E5] 5.7 AT 전용 설정 (System Tab AT 관련 2개)",
             "description": adf_doc(adf_paragraph("UI PRD Ch.9 매핑. AT 전용 설정 2개 요소."))},
            {"summary": "[E5] 5.8 오류 복구 인터페이스 (Miss Deal, 재스캔)",
             "description": adf_doc(adf_paragraph("AT-23~AT-26. Miss Deal, 재스캔 연동 UI."))},
        ],
    },
    {
        "summary": "[EBS v2] Epic 6: 데이터 아카이브",
        "description": adf_doc(
            adf_heading("데이터 아카이브", 2),
            adf_paragraph("핸드 히스토리 + 리플레이 + Export + 통계"),
            adf_rule(),
            adf_bold_para("Protocol: ", "3개 (History 3)"),
            adf_bold_para("기존 Epic 참조: ", "PV-6471"),
        ),
        "stories": [
            {"summary": "[E6] 6.1 핸드 히스토리 자동 저장",
             "description": adf_doc(adf_paragraph("PRD §9.1 매핑. 메타+홀카드+보드+베팅 자동 저장."))},
            {"summary": "[E6] 6.2 Playback 리플레이 (타임라인 동기화, 크로마키)",
             "description": adf_doc(adf_paragraph("PRD §9.2 매핑. 핸드 리플레이 도구."))},
            {"summary": "[E6] 6.3 데이터 수동 편집 + CSV/JSON Export",
             "description": adf_doc(adf_paragraph("PRD §9.3 매핑. 편집 UI + Export 기능."))},
            {"summary": "[E6] 6.4 플레이어 통계 (VPIP, PFR, 3Bet%) + LIVE Stats API",
             "description": adf_doc(adf_paragraph("PRD §9.4 매핑. 8개 통계 지표 + 실시간 API."))},
        ],
    },
    {
        "summary": "[EBS v2] Epic 7: 시스템 관리",
        "description": adf_doc(
            adf_heading("시스템 관리", 2),
            adf_paragraph("인증 + 라이선스 + 시스템 설정 + 메인 윈도우 + Connection/Slave 프로토콜"),
            adf_rule(),
            adf_bold_para("Settings UI: ", "20개 (Main Window 14 + System Tab Admin 6)"),
            adf_bold_para("Protocol: ", "12개 (Connection 9 + Slave 3)"),
            adf_bold_para("기존 Epic 참조: ", "PV-6473"),
        ),
        "stories": [
            {"summary": "[E7] 7.1 로그인 인증 (관리자/운영자)",
             "description": adf_doc(adf_paragraph("PRD §10.1 매핑. 역할 기반 인증 시스템."))},
            {"summary": "[E7] 7.2 라이선스 검증 및 활성화",
             "description": adf_doc(adf_paragraph("PRD §10.1 매핑. 라이선스 키 검증/활성화."))},
            {"summary": "[E7] 7.3 서버 포트/네트워크/보안 설정 (Y-01~Y-02)",
             "description": adf_doc(adf_paragraph("PRD §10.2, UI PRD Ch.9 매핑. 네트워크 설정."))},
            {"summary": "[E7] 7.4 언어/백업/데이터 관리 (Y-08~Y-13)",
             "description": adf_doc(adf_paragraph("PRD §10.2, UI PRD Ch.9 매핑. 관리 기능."))},
            {"summary": "[E7] 7.5 메인 윈도우 (M-01~M-14)",
             "description": adf_doc(adf_paragraph("UI PRD Ch.4 매핑. Title Bar, Preview, Status, Actions, TabBar."))},
        ],
    },
    {
        "summary": "[EBS v2] Epic 8: 스킨 편집 시스템 (v2.0)",
        "description": adf_doc(
            adf_heading("스킨 편집 시스템 (v2.0 Scope)", 2),
            adf_paragraph("Skin Editor 독립 도구 — UI PRD Ch.11 44개 요소"),
            adf_rule(),
            adf_bold_para("스코프: ", "v2.0 Operational Excellence"),
            adf_bold_para("PRD 매핑: ", "SK-01~SK-44"),
        ),
        "stories": [
            {"summary": "[E8] 8.1 좌표 편집기 (드래그&드롭 위치 조정)",
             "description": adf_doc(adf_paragraph("SK-01~SK-12 매핑. 요소 위치 드래그&드롭."))},
            {"summary": "[E8] 8.2 폰트/색상 편집기",
             "description": adf_doc(adf_paragraph("SK-13~SK-24 매핑. 텍스트/색상 커스터마이징."))},
            {"summary": "[E8] 8.3 프리셋 관리 (저장/불러오기/내보내기)",
             "description": adf_doc(adf_paragraph("SK-25~SK-36 매핑. 프리셋 CRUD + Export."))},
            {"summary": "[E8] 8.4 실시간 미리보기",
             "description": adf_doc(adf_paragraph("SK-37~SK-44 매핑. 편집 결과 실시간 반영."))},
        ],
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

    created_epics = []
    total_stories = 0

    for i, epic_data in enumerate(EPICS_DATA, 1):
        print(f"\n{'═' * 60}")
        print(f"Epic {i}: {epic_data['summary']}")
        print(f"  Stories: {len(epic_data['stories'])}")

        epic_key = None

        if dry_run:
            print(f"  [DRY RUN] Would create Epic")
            for j, story in enumerate(epic_data["stories"], 1):
                print(f"    Story {j}: {story['summary']}")
            total_stories += len(epic_data["stories"])
            continue

        # Create Epic
        try:
            epic_fields = {
                "project": {"key": PROJECT_KEY},
                "issuetype": {"id": EPIC_TYPE_ID},
                "summary": epic_data["summary"],
                "description": epic_data["description"],
            }
            result = create_issue(epic_fields, cfg=cfg)
            epic_key = result.get("key", "???")
            print(f"  ✓ Epic created: {epic_key}")
            created_epics.append(epic_key)
        except Exception as e:
            print(f"  ✗ Epic FAILED: {e}")
            continue

        # Create Stories under this Epic
        for j, story in enumerate(epic_data["stories"], 1):
            try:
                story_fields = {
                    "project": {"key": PROJECT_KEY},
                    "issuetype": {"id": TASK_TYPE_ID},
                    "summary": story["summary"],
                    "description": story["description"],
                    "parent": {"key": epic_key},
                }
                result = create_issue(story_fields, cfg=cfg)
                story_key = result.get("key", "???")
                print(f"    ✓ Story {j}: {story_key} — {story['summary'][:50]}")
                total_stories += 1
            except Exception as e:
                print(f"    ✗ Story {j} FAILED: {e}")

    print(f"\n{'═' * 60}")
    print(f"Summary: {len(created_epics) if not dry_run else len(EPICS_DATA)} Epics, {total_stories} Stories")
    if created_epics:
        print(f"Created Epic keys: {', '.join(created_epics)}")
    if dry_run:
        print("(dry run — nothing created)")


if __name__ == "__main__":
    main()
