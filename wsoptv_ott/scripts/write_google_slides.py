#!/usr/bin/env python3
"""
Google Slides API를 사용하여 WSOPTV Wireframe 슬라이드 생성
각 NBA TV 분석 슬라이드 뒤에 WSOPTV 적용 wireframe 슬라이드 삽입
"""

import os
import sys
import uuid
from pathlib import Path

# Windows 콘솔 인코딩 문제 해결
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# OAuth 인증 관련
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 절대 경로 사용
CREDENTIALS_FILE = r'C:\claude\json\desktop_credentials.json'
TOKEN_FILE = r'C:\claude\json\token_slides.json'

# Slides API 읽기/쓰기 권한
SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive'
]

# 프레젠테이션 ID
PRESENTATION_ID = '12czNJ9OmJjzu-Nii1ZefIjNgov94I8gNIyXNVdBv9I4'

# 슬라이드 크기 (포인트)
SLIDE_WIDTH = 720
SLIDE_HEIGHT = 405

# EMU 변환
PT_TO_EMU = 12700


def get_credentials():
    """OAuth 2.0 인증 수행"""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"[ERROR] 인증 파일 없음: {CREDENTIALS_FILE}")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"[OK] 토큰 저장: {TOKEN_FILE}")

    return creds


def get_slides_service():
    """Slides API 서비스 생성"""
    creds = get_credentials()
    return build('slides', 'v1', credentials=creds)


def gen_id():
    """고유 ID 생성"""
    return f"wsoptv_{uuid.uuid4().hex[:8]}"


def create_slide_request(slide_id, insert_index):
    """새 슬라이드 생성 요청"""
    return {
        'createSlide': {
            'objectId': slide_id,
            'insertionIndex': insert_index,
            'slideLayoutReference': {
                'predefinedLayout': 'BLANK'
            }
        }
    }


def create_rect(slide_id, x, y, w, h, fill_color=None, outline_color=None, obj_id=None):
    """사각형 생성 요청"""
    if obj_id is None:
        obj_id = gen_id()

    requests = [{
        'createShape': {
            'objectId': obj_id,
            'shapeType': 'RECTANGLE',
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {
                    'width': {'magnitude': w * PT_TO_EMU, 'unit': 'EMU'},
                    'height': {'magnitude': h * PT_TO_EMU, 'unit': 'EMU'}
                },
                'transform': {
                    'scaleX': 1, 'scaleY': 1,
                    'translateX': x * PT_TO_EMU,
                    'translateY': y * PT_TO_EMU,
                    'unit': 'EMU'
                }
            }
        }
    }]

    if fill_color:
        requests.append({
            'updateShapeProperties': {
                'objectId': obj_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': fill_color},
                            'alpha': 1.0
                        }
                    }
                },
                'fields': 'shapeBackgroundFill'
            }
        })

    if outline_color:
        requests.append({
            'updateShapeProperties': {
                'objectId': obj_id,
                'shapeProperties': {
                    'outline': {
                        'outlineFill': {
                            'solidFill': {'color': {'rgbColor': outline_color}}
                        },
                        'weight': {'magnitude': 1, 'unit': 'PT'}
                    }
                },
                'fields': 'outline'
            }
        })

    return requests


def create_text_box(slide_id, x, y, w, h, text, font_size=12, bold=False,
                    text_color=None, align='START', obj_id=None):
    """텍스트 박스 생성 요청"""
    if obj_id is None:
        obj_id = gen_id()

    # 빈 텍스트 처리
    if not text or text.strip() == "":
        text = " "

    requests = [
        {
            'createShape': {
                'objectId': obj_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': w * PT_TO_EMU, 'unit': 'EMU'},
                        'height': {'magnitude': h * PT_TO_EMU, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': x * PT_TO_EMU,
                        'translateY': y * PT_TO_EMU,
                        'unit': 'EMU'
                    }
                }
            }
        },
        {
            'insertText': {
                'objectId': obj_id,
                'text': text,
                'insertionIndex': 0
            }
        },
        {
            'updateTextStyle': {
                'objectId': obj_id,
                'style': {
                    'fontSize': {'magnitude': font_size, 'unit': 'PT'},
                    'bold': bold
                },
                'textRange': {'type': 'ALL'},
                'fields': 'fontSize,bold'
            }
        },
        {
            'updateParagraphStyle': {
                'objectId': obj_id,
                'style': {
                    'alignment': align
                },
                'textRange': {'type': 'ALL'},
                'fields': 'alignment'
            }
        }
    ]

    if text_color:
        requests.append({
            'updateTextStyle': {
                'objectId': obj_id,
                'style': {
                    'foregroundColor': {
                        'opaqueColor': {'rgbColor': text_color}
                    }
                },
                'textRange': {'type': 'ALL'},
                'fields': 'foregroundColor'
            }
        })

    return requests


def create_line(slide_id, x1, y1, x2, y2, color=None, obj_id=None):
    """선 생성 요청"""
    if obj_id is None:
        obj_id = gen_id()

    requests = [{
        'createLine': {
            'objectId': obj_id,
            'lineCategory': 'STRAIGHT',
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {
                    'width': {'magnitude': abs(x2-x1) * PT_TO_EMU, 'unit': 'EMU'},
                    'height': {'magnitude': abs(y2-y1) * PT_TO_EMU, 'unit': 'EMU'}
                },
                'transform': {
                    'scaleX': 1, 'scaleY': 1,
                    'translateX': min(x1, x2) * PT_TO_EMU,
                    'translateY': min(y1, y2) * PT_TO_EMU,
                    'unit': 'EMU'
                }
            }
        }
    }]

    if color:
        requests.append({
            'updateLineProperties': {
                'objectId': obj_id,
                'lineProperties': {
                    'lineFill': {
                        'solidFill': {'color': {'rgbColor': color}}
                    }
                },
                'fields': 'lineFill'
            }
        })

    return requests


# ============================================================
# 색상 정의
# ============================================================
COLORS = {
    'bg_dark': {'red': 0.1, 'green': 0.1, 'blue': 0.15},
    'bg_card': {'red': 0.15, 'green': 0.15, 'blue': 0.2},
    'bg_section': {'red': 0.2, 'green': 0.2, 'blue': 0.25},
    'accent': {'red': 0.8, 'green': 0.6, 'blue': 0.2},  # Gold
    'text_white': {'red': 1, 'green': 1, 'blue': 1},
    'text_gray': {'red': 0.7, 'green': 0.7, 'blue': 0.7},
    'live_red': {'red': 0.9, 'green': 0.2, 'blue': 0.2},
    'green': {'red': 0.2, 'green': 0.7, 'blue': 0.3},
    'blue': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
    'outline': {'red': 0.4, 'green': 0.4, 'blue': 0.5},
}


# ============================================================
# 슬라이드별 Wireframe 데이터
# ============================================================

def build_slide_1(slide_id):
    """표지 슬라이드 - WSOPTV OTT Platform"""
    requests = []

    # 배경 (어두운 색)
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 제목
    requests.extend(create_text_box(slide_id, 100, 100, 520, 60,
                                    "WSOPTV OTT Platform",
                                    font_size=36, bold=True,
                                    text_color=COLORS['accent'], align='CENTER'))

    # 부제목
    requests.extend(create_text_box(slide_id, 100, 170, 520, 40,
                                    '"Watch Like You\'re at the Table"',
                                    font_size=18,
                                    text_color=COLORS['text_white'], align='CENTER'))

    # 중앙 로고 영역
    requests.extend(create_rect(slide_id, 260, 220, 200, 80,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 260, 240, 200, 40, "WSOP",
                                    font_size=32, bold=True,
                                    text_color=COLORS['accent'], align='CENTER'))

    # 하단 정보
    requests.extend(create_text_box(slide_id, 100, 340, 520, 30,
                                    "GG PRODUCTION | WSOPTV Version",
                                    font_size=14, text_color=COLORS['text_gray'],
                                    align='CENTER'))

    return requests


def build_slide_2(slide_id):
    """메인 화면 - WSOPTV"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 상단 네비게이션
    requests.extend(create_rect(slide_id, 10, 10, 700, 30,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 20, 15, 680, 20,
                                    "WSOP   Tournaments   Live   VOD   Stats   Players",
                                    font_size=10, text_color=COLORS['text_white']))

    # Table Strip (상단)
    for i, (name, event) in enumerate([
        ("TABLE 1", "MAIN EVENT"),
        ("TABLE 2", "$10K PLO"),
        ("TABLE 3", "$5K NLH"),
        ("TABLE 4", "$25K HIGH")
    ]):
        x = 15 + i * 175
        requests.extend(create_rect(slide_id, x, 50, 165, 55,
                                    fill_color=COLORS['bg_card'],
                                    outline_color=COLORS['outline']))
        requests.extend(create_text_box(slide_id, x+5, 55, 155, 15, name,
                                        font_size=9, bold=True,
                                        text_color=COLORS['accent']))
        requests.extend(create_text_box(slide_id, x+5, 70, 155, 15, event,
                                        font_size=8, text_color=COLORS['text_white']))
        requests.extend(create_text_box(slide_id, x+5, 85, 60, 12, "LIVE",
                                        font_size=7, bold=True,
                                        text_color=COLORS['live_red']))

    # Hero Section (메인 비디오)
    requests.extend(create_rect(slide_id, 15, 115, 480, 200,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 25, 125, 460, 25,
                                    "MAIN EVENT DAY 5 - FEATURE TABLE",
                                    font_size=14, bold=True,
                                    text_color=COLORS['text_white']))
    requests.extend(create_text_box(slide_id, 25, 155, 460, 20,
                                    "[FEATURE TABLE LIVE]",
                                    font_size=11, text_color=COLORS['text_gray'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 25, 250, 200, 20,
                                    "$32,450,000 PRIZE POOL",
                                    font_size=12, bold=True,
                                    text_color=COLORS['accent']))
    # CTA 버튼들
    for i, btn in enumerate(["WATCH", "STATS", "HANDS"]):
        requests.extend(create_rect(slide_id, 25 + i*100, 280, 90, 25,
                                    fill_color=COLORS['accent'],
                                    outline_color=COLORS['accent']))
        requests.extend(create_text_box(slide_id, 25 + i*100, 283, 90, 20, btn,
                                        font_size=10, bold=True,
                                        text_color=COLORS['bg_dark'], align='CENTER'))

    # Headlines (우측)
    requests.extend(create_rect(slide_id, 505, 115, 200, 200,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 515, 120, 180, 20, "HEADLINES",
                                    font_size=12, bold=True,
                                    text_color=COLORS['accent']))
    for i, news in enumerate([
        "Phil Ivey leads with 15.2M",
        "Negreanu eliminated 23rd",
        "Hellmuth bracelet count: 17"
    ]):
        requests.extend(create_text_box(slide_id, 515, 145 + i*50, 180, 40, news,
                                        font_size=9, text_color=COLORS['text_white']))

    # 하단 바
    requests.extend(create_rect(slide_id, 15, 325, 690, 25,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 25, 328, 670, 20,
                                    "WSOP 2026  |  Main Event  |  $10M GTD  |  Schedule",
                                    font_size=10, text_color=COLORS['text_gray']))

    # 슬라이드 번호
    requests.extend(create_text_box(slide_id, 650, 380, 60, 15,
                                    "Slide 2-1", font_size=8,
                                    text_color=COLORS['text_gray']))

    return requests


def build_slide_3(slide_id):
    """콘텐츠 섹션 - WSOPTV"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # LIVE TABLES 섹션
    requests.extend(create_text_box(slide_id, 20, 15, 200, 20, "LIVE TABLES",
                                    font_size=14, bold=True,
                                    text_color=COLORS['accent']))

    for i in range(4):
        x = 20 + i * 170
        requests.extend(create_rect(slide_id, x, 40, 160, 70,
                                    fill_color=COLORS['bg_card'],
                                    outline_color=COLORS['outline']))
        requests.extend(create_text_box(slide_id, x+5, 45, 60, 15, "LIVE",
                                        font_size=8, bold=True,
                                        text_color=COLORS['live_red']))
        requests.extend(create_text_box(slide_id, x+5, 60, 150, 15,
                                        f"TABLE {i+1}",
                                        font_size=10, bold=True,
                                        text_color=COLORS['text_white']))

    # TRENDING NOW 섹션
    requests.extend(create_text_box(slide_id, 20, 120, 200, 20, "TRENDING NOW",
                                    font_size=12, bold=True,
                                    text_color=COLORS['text_white']))
    requests.extend(create_text_box(slide_id, 620, 120, 80, 20, "See More >",
                                    font_size=9, text_color=COLORS['accent']))

    for i, title in enumerate(["$2.4M Pot", "Sick Bluff", "Royal Flush", "Bad Beat"]):
        x = 20 + i * 170
        requests.extend(create_rect(slide_id, x, 145, 160, 70,
                                    fill_color=COLORS['bg_card'],
                                    outline_color=COLORS['outline']))
        requests.extend(create_text_box(slide_id, x+5, 150, 50, 15, "4:51",
                                        font_size=8, text_color=COLORS['text_gray']))
        requests.extend(create_text_box(slide_id, x+5, 190, 150, 20, title,
                                        font_size=10, bold=True,
                                        text_color=COLORS['text_white']))

    # ALL-IN MOMENTS 섹션
    requests.extend(create_text_box(slide_id, 20, 225, 200, 20, "ALL-IN MOMENTS 2026",
                                    font_size=12, bold=True,
                                    text_color=COLORS['text_white']))

    for i, (pot, players) in enumerate([
        ("$5M", "Ivey vs Negreanu"),
        ("$3.2M", "Hellmuth vs Dwan"),
        ("$4.1M", "Negreanu vs Ivey"),
        ("$2.8M", "Polk vs Doug P")
    ]):
        x = 20 + i * 170
        requests.extend(create_rect(slide_id, x, 250, 160, 70,
                                    fill_color=COLORS['bg_card'],
                                    outline_color=COLORS['outline']))
        requests.extend(create_text_box(slide_id, x+5, 255, 150, 20, pot,
                                        font_size=14, bold=True,
                                        text_color=COLORS['accent']))
        requests.extend(create_text_box(slide_id, x+5, 275, 150, 15, "ALL-IN",
                                        font_size=8, text_color=COLORS['live_red']))
        requests.extend(create_text_box(slide_id, x+5, 295, 150, 15, players,
                                        font_size=8, text_color=COLORS['text_white']))

    # DAILY RECAPS 섹션
    requests.extend(create_text_box(slide_id, 20, 330, 200, 20, "DAILY RECAPS",
                                    font_size=12, bold=True,
                                    text_color=COLORS['text_white']))

    for i in range(4):
        x = 20 + i * 170
        requests.extend(create_rect(slide_id, x, 355, 160, 40,
                                    fill_color=COLORS['bg_section'],
                                    outline_color=COLORS['outline']))
        requests.extend(create_text_box(slide_id, x+5, 360, 150, 15,
                                        f"Day {5-i} RECAP",
                                        font_size=9, text_color=COLORS['text_white']))

    return requests


def build_slide_4(slide_id):
    """Around WSOP - 뉴스 섹션"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 제목
    requests.extend(create_text_box(slide_id, 20, 15, 200, 25, "AROUND WSOP",
                                    font_size=16, bold=True,
                                    text_color=COLORS['accent']))

    # 뉴스 항목들
    news_items = [
        ("POY LADDER: IVEY RECLAIMS #1 SPOT",
         "Phil Ivey takes the lead for the first time since April"),
        ("WHO ARE TOP BRACELET CANDIDATES?",
         "These names lead the way for Most Bracelets, POY"),
        ("ROOKIE WATCH: FLAGG NEARING TOP 5",
         "Cooper Flagg joins the poker world"),
        ("WHO ARE TOP EARNERS AT MIDSEASON?",
         "Daniel Negreanu and Phil Hellmuth are shining")
    ]

    for i, (title, desc) in enumerate(news_items):
        y = 50 + i * 85
        # 뉴스 카드
        requests.extend(create_rect(slide_id, 20, y, 680, 75,
                                    fill_color=COLORS['bg_card'],
                                    outline_color=COLORS['outline']))
        # 이미지 플레이스홀더
        requests.extend(create_rect(slide_id, 30, y+10, 100, 55,
                                    fill_color=COLORS['bg_section'],
                                    outline_color=COLORS['outline']))
        requests.extend(create_text_box(slide_id, 30, y+30, 100, 20, "[PHOTO]",
                                        font_size=9, text_color=COLORS['text_gray'],
                                        align='CENTER'))
        # 제목
        requests.extend(create_text_box(slide_id, 145, y+15, 540, 20, title,
                                        font_size=12, bold=True,
                                        text_color=COLORS['text_white']))
        # 설명
        requests.extend(create_text_box(slide_id, 145, y+35, 540, 20, desc,
                                        font_size=9, text_color=COLORS['text_gray']))
        # 날짜
        requests.extend(create_text_box(slide_id, 145, y+55, 150, 15,
                                        "June 17, 2026",
                                        font_size=8, text_color=COLORS['text_gray']))

    return requests


def build_slide_5(slide_id):
    """Streaming Options - Views"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 중앙 패널
    requests.extend(create_rect(slide_id, 120, 30, 480, 340,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))

    # 제목
    requests.extend(create_text_box(slide_id, 140, 40, 440, 25,
                                    "STREAMING OPTIONS",
                                    font_size=16, bold=True,
                                    text_color=COLORS['accent'], align='CENTER'))

    # 탭
    for i, (tab, active) in enumerate([("Views", True), ("Languages", False), ("Audio", False)]):
        color = COLORS['accent'] if active else COLORS['text_gray']
        requests.extend(create_text_box(slide_id, 180 + i*120, 70, 100, 20, tab,
                                        font_size=11, bold=active,
                                        text_color=color, align='CENTER'))

    # 구분선
    requests.extend(create_line(slide_id, 140, 95, 580, 95, color=COLORS['outline']))

    # 옵션 목록
    options = [
        ("Feature Table View", "Main broadcast with hole cards", True),
        ("Player Cam (Phil Ivey)", "Focus on selected player's actions", False),
        ("Stats Overlay", "Real-time statistics and hand history", False),
        ("Director's Cut", "Multiple angles with expert commentary", False),
        ("Mobile Optimized", "Vertical view focused on cards", False)
    ]

    for i, (title, desc, selected) in enumerate(options):
        y = 110 + i * 50
        # 체크 표시
        check = "[X]" if selected else "[ ]"
        requests.extend(create_text_box(slide_id, 150, y, 30, 20, check,
                                        font_size=11,
                                        text_color=COLORS['green'] if selected else COLORS['text_gray']))
        # 제목
        requests.extend(create_text_box(slide_id, 185, y, 380, 20, title,
                                        font_size=12, bold=True,
                                        text_color=COLORS['text_white']))
        # 설명
        requests.extend(create_text_box(slide_id, 185, y+18, 380, 18, desc,
                                        font_size=9,
                                        text_color=COLORS['text_gray']))

    return requests


def build_slide_6(slide_id):
    """플레이어별 스트림 비교"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 좌측 플레이어
    requests.extend(create_text_box(slide_id, 20, 15, 300, 20, "Phil Ivey Stream",
                                    font_size=14, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_rect(slide_id, 20, 40, 340, 180,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 60, 320, 20, "[IVEY CAM VIEW]",
                                    font_size=11, text_color=COLORS['text_gray'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 30, 120, 320, 20,
                                    "Chip Count: $15.2M   Position: 1st/45",
                                    font_size=10, text_color=COLORS['text_white']))
    requests.extend(create_text_box(slide_id, 30, 150, 320, 60,
                                    "VPIP: 22%   PFR: 18%   3-Bet: 8%",
                                    font_size=10, text_color=COLORS['text_gray']))

    # 우측 플레이어
    requests.extend(create_text_box(slide_id, 380, 15, 320, 20, "Daniel Negreanu Stream",
                                    font_size=14, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_rect(slide_id, 380, 40, 320, 180,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 390, 60, 300, 20, "[NEGREANU CAM]",
                                    font_size=11, text_color=COLORS['text_gray'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 390, 120, 300, 20,
                                    "Chip Count: $8.7M   Position: 5th/45",
                                    font_size=10, text_color=COLORS['text_white']))
    requests.extend(create_text_box(slide_id, 390, 150, 300, 60,
                                    "VPIP: 28%   PFR: 22%   3-Bet: 12%",
                                    font_size=10, text_color=COLORS['text_gray']))

    # 하단 설명
    requests.extend(create_rect(slide_id, 20, 240, 680, 100,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 30, 255, 660, 25,
                                    '"당신이 응원하는 플레이어에게만 집중할 수 있는 환경"',
                                    font_size=14, bold=True,
                                    text_color=COLORS['accent'], align='CENTER'))
    requests.extend(create_text_box(slide_id, 30, 290, 660, 40,
                                    'WSOPTV가 시청자를 끌어들이는 방식은 결국\n"당신이 보고 싶은 플레이어에게만 집중할 수 있는 환경을 준다"는 것입니다.',
                                    font_size=10, text_color=COLORS['text_white'],
                                    align='CENTER'))

    return requests


def build_slide_7(slide_id):
    """다국어 지원 - Languages"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 중앙 패널
    requests.extend(create_rect(slide_id, 120, 20, 480, 340,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))

    # 제목
    requests.extend(create_text_box(slide_id, 140, 30, 440, 25,
                                    "STREAMING OPTIONS",
                                    font_size=16, bold=True,
                                    text_color=COLORS['accent'], align='CENTER'))

    # 탭
    for i, (tab, active) in enumerate([("Views", False), ("Languages", True), ("Audio", False)]):
        color = COLORS['accent'] if active else COLORS['text_gray']
        requests.extend(create_text_box(slide_id, 180 + i*120, 60, 100, 20, tab,
                                        font_size=11, bold=active,
                                        text_color=color, align='CENTER'))

    # 언어 목록
    languages = [
        ("English (Default)", "Professional commentary"),
        ("Spanish (GGPoker)", "Pre-game, live, and post-game"),
        ("Portuguese (GGPoker)", "Pre-game, live, and post-game"),
        ("Japanese", "Live commentary"),
        ("Korean", "Live commentary")
    ]

    for i, (lang, desc) in enumerate(languages):
        y = 95 + i * 45
        requests.extend(create_text_box(slide_id, 150, y, 400, 20, lang,
                                        font_size=12, bold=True,
                                        text_color=COLORS['text_white']))
        requests.extend(create_text_box(slide_id, 150, y+18, 400, 18, desc,
                                        font_size=9, text_color=COLORS['text_gray']))

    # 추가 언어
    requests.extend(create_text_box(slide_id, 150, 320, 400, 20,
                                    "+ 15 more languages...",
                                    font_size=10, text_color=COLORS['accent']))

    # PRD 참조
    requests.extend(create_text_box(slide_id, 20, 375, 300, 20,
                                    "PRD-0002: 20개국 다국어 자막 지원",
                                    font_size=9, text_color=COLORS['text_gray']))

    return requests


def build_slide_8(slide_id):
    """플레이어 컨트롤 UI"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 상단 제목
    requests.extend(create_text_box(slide_id, 20, 10, 400, 20,
                                    "MAIN EVENT - FEATURE TABLE",
                                    font_size=12, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 20, 28, 200, 15,
                                    "Feature Table View",
                                    font_size=9, text_color=COLORS['text_gray']))

    # 메인 테이블 뷰
    requests.extend(create_rect(slide_id, 20, 50, 680, 250,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 280, 150, 160, 30,
                                    "[POKER TABLE VIEW]",
                                    font_size=12, text_color=COLORS['text_gray'],
                                    align='CENTER'))

    # 플레이어 위치
    players = [
        (80, 80, "Phil Ivey", "$15.2M"),
        (560, 80, "D. Negreanu", "$8.7M"),
        (80, 220, "Player 5", "$4.2M"),
        (560, 220, "Player 3", "$5.1M"),
        (320, 100, "POT: $2,450,000", "")
    ]

    for x, y, name, chips in players:
        requests.extend(create_text_box(slide_id, x, y, 120, 15, name,
                                        font_size=9, bold=True,
                                        text_color=COLORS['text_white']))
        if chips:
            requests.extend(create_text_box(slide_id, x, y+15, 120, 15, chips,
                                            font_size=8,
                                            text_color=COLORS['accent']))

    # 레이아웃 옵션
    requests.extend(create_rect(slide_id, 20, 310, 200, 30,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 30, 315, 180, 20,
                                    "[1] [2] [4] Layout Options",
                                    font_size=9, text_color=COLORS['text_white']))

    # 하단 컨트롤 바
    requests.extend(create_rect(slide_id, 20, 350, 680, 35,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))

    for i, btn in enumerate(["Tables 4", "MultiView", "Key Hands", "Stats"]):
        requests.extend(create_text_box(slide_id, 40 + i*170, 358, 150, 20, btn,
                                        font_size=10, bold=True,
                                        text_color=COLORS['accent'], align='CENTER'))

    # 타임라인
    requests.extend(create_text_box(slide_id, 20, 390, 680, 15,
                                    "02:31:43 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ LIVE",
                                    font_size=8, text_color=COLORS['text_gray']))

    return requests


def build_slide_9(slide_id):
    """MultiView 선택"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 메인 테이블 뷰 (상단)
    requests.extend(create_rect(slide_id, 20, 20, 680, 140,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 280, 70, 160, 30,
                                    "[MAIN TABLE VIEW]\nFeature Table - 9 players",
                                    font_size=11, text_color=COLORS['text_gray'],
                                    align='CENTER'))

    # 추가 뷰 슬롯 (좌측)
    requests.extend(create_rect(slide_id, 20, 170, 340, 150,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 100, 200, 180, 20,
                                    "+ Add Table from Table Strip",
                                    font_size=10, text_color=COLORS['text_white'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 40, 235, 300, 60,
                                    "Available:\n  - Table 2 ($10K PLO)\n  - Table 3 ($5K NLH)\n  - Table 4 ($25K HIGH)",
                                    font_size=9, text_color=COLORS['text_gray']))

    # 추가 뷰 슬롯 (우측)
    requests.extend(create_rect(slide_id, 370, 170, 330, 150,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 440, 200, 180, 20,
                                    "+ Add Table from Table Strip",
                                    font_size=10, text_color=COLORS['text_white'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 390, 235, 290, 60,
                                    "Or select:\n  - Stats View\n  - Player Cam\n  - Hand History",
                                    font_size=9, text_color=COLORS['text_gray']))

    # Tip
    requests.extend(create_rect(slide_id, 20, 330, 680, 35,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 338, 660, 20,
                                    "Tip: 테이블 Strip에서 드래그하여 뷰에 추가하세요",
                                    font_size=10, text_color=COLORS['accent'],
                                    align='CENTER'))

    return requests


def build_slide_10(slide_id):
    """2분할 뷰"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 좌측 뷰
    requests.extend(create_rect(slide_id, 20, 20, 340, 290,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 30, 320, 20, "FEATURE TABLE",
                                    font_size=12, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 50, 320, 15, "Main Event Day 5",
                                    font_size=9, text_color=COLORS['text_gray']))
    requests.extend(create_rect(slide_id, 60, 80, 260, 140,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 120, 140, 140, 20, "[POKER TABLE]",
                                    font_size=10, text_color=COLORS['text_gray'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 30, 230, 320, 15, "POT: $2.4M",
                                    font_size=10, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 250, 320, 15, "9 players remaining",
                                    font_size=9, text_color=COLORS['text_white']))
    requests.extend(create_text_box(slide_id, 30, 280, 150, 15, "Active Audio",
                                    font_size=9, bold=True,
                                    text_color=COLORS['green']))

    # 우측 뷰
    requests.extend(create_rect(slide_id, 370, 20, 330, 290,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 380, 30, 310, 20, "TABLE 2 - $10K PLO",
                                    font_size=12, bold=True,
                                    text_color=COLORS['text_white']))
    requests.extend(create_text_box(slide_id, 380, 50, 310, 15, "Final Table",
                                    font_size=9, text_color=COLORS['text_gray']))
    requests.extend(create_rect(slide_id, 410, 80, 260, 140,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 470, 140, 140, 20, "[POKER TABLE]",
                                    font_size=10, text_color=COLORS['text_gray'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 380, 230, 310, 15, "POT: $850K",
                                    font_size=10, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 380, 250, 310, 15, "6 players remaining",
                                    font_size=9, text_color=COLORS['text_white']))
    requests.extend(create_text_box(slide_id, 380, 280, 150, 15, "Muted",
                                    font_size=9, text_color=COLORS['text_gray']))

    # 하단 Tip
    requests.extend(create_text_box(slide_id, 20, 320, 680, 30,
                                    '"서로 다른 토너먼트 동시 시청 - 각 뷰 독립 오디오"',
                                    font_size=11, text_color=COLORS['accent'],
                                    align='CENTER'))

    return requests


def build_slide_11(slide_id):
    """3-Layer MultiView (핵심)"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 4분할 뷰
    views = [
        (20, 20, "LAYER 1: FEATURE TABLE", "POT: $2.4M\nPhil Ivey: ALL-IN", True),
        (370, 20, "LAYER 2: TABLE 2", "POT: $850K\nHeads-up action", False),
        (20, 200, "LAYER 2: TABLE 3", "POT: $340K\nEarly stage", False),
        (370, 200, "LAYER 3: STATS VIEW", "HAND HISTORY\n#142 Ivey 3-bet\n#143 Negreanu\n#144 ALL-IN", False)
    ]

    for x, y, title, content, is_primary in views:
        outline = COLORS['accent'] if is_primary else COLORS['outline']
        requests.extend(create_rect(slide_id, x, y, 340, 170,
                                    fill_color=COLORS['bg_card'],
                                    outline_color=outline))
        requests.extend(create_text_box(slide_id, x+10, y+10, 320, 15, title,
                                        font_size=10, bold=True,
                                        text_color=COLORS['accent'] if is_primary else COLORS['text_white']))
        requests.extend(create_rect(slide_id, x+20, y+35, 300, 90,
                                    fill_color=COLORS['bg_section'],
                                    outline_color=COLORS['outline']))
        requests.extend(create_text_box(slide_id, x+30, y+55, 280, 60, content,
                                        font_size=9, text_color=COLORS['text_gray']))

    # 하단 라벨
    requests.extend(create_text_box(slide_id, 20, 380, 350, 20,
                                    "3-Layer Multi-view | PRD-0006 Advanced Mode",
                                    font_size=10, bold=True,
                                    text_color=COLORS['accent']))

    return requests


def build_slide_12(slide_id):
    """Key Hands"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 중앙 패널
    requests.extend(create_rect(slide_id, 120, 25, 480, 330,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))

    # 제목
    requests.extend(create_text_box(slide_id, 140, 35, 420, 25, "KEY HANDS",
                                    font_size=16, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 560, 35, 30, 25, "X",
                                    font_size=14, text_color=COLORS['text_gray']))

    # Key hands 목록
    hands = [
        ("$2.4M All-in: Ivey vs Negreanu", "Hand #142 - 02:31:15", "BIGGEST POT TODAY"),
        ("Sick Bluff by Phil Hellmuth", "Hand #138 - 02:15:22", ""),
        ("Royal Flush - Table 3", "Hand #125 - 01:45:10", "RARE HAND"),
        ("Bad Beat: Set over Set", "Hand #112 - 01:22:45", "BAD BEAT")
    ]

    for i, (title, time, badge) in enumerate(hands):
        y = 70 + i * 65
        # 썸네일
        requests.extend(create_rect(slide_id, 140, y, 60, 50,
                                    fill_color=COLORS['bg_section'],
                                    outline_color=COLORS['outline']))
        # 제목
        requests.extend(create_text_box(slide_id, 210, y+5, 370, 20, title,
                                        font_size=11, bold=True,
                                        text_color=COLORS['text_white']))
        # 시간
        requests.extend(create_text_box(slide_id, 210, y+25, 200, 15, time,
                                        font_size=9, text_color=COLORS['text_gray']))
        # 배지
        if badge:
            color = COLORS['accent'] if "BIGGEST" in badge else (
                COLORS['green'] if "RARE" in badge else COLORS['live_red'])
            requests.extend(create_text_box(slide_id, 210, y+40, 150, 15, badge,
                                            font_size=8, bold=True,
                                            text_color=color))

    # 하단 Tip
    requests.extend(create_text_box(slide_id, 140, 340, 420, 15,
                                    "클릭하면 해당 핸드 시작 시점으로 즉시 이동",
                                    font_size=9, text_color=COLORS['accent'],
                                    align='CENTER'))

    return requests


def build_slide_13(slide_id):
    """Smart Key Hands AI (핵심)"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 좌측: 테이블 뷰
    requests.extend(create_rect(slide_id, 20, 20, 340, 280,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 100, 50, 180, 20, "[POKER TABLE VIEW]",
                                    font_size=10, text_color=COLORS['text_gray'],
                                    align='CENTER'))

    # Smart Key Hand 알림바
    requests.extend(create_rect(slide_id, 60, 100, 240, 60,
                                fill_color=COLORS['accent'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 70, 105, 220, 20, "Smart Key Hand",
                                    font_size=11, bold=True,
                                    text_color=COLORS['bg_dark']))
    requests.extend(create_text_box(slide_id, 70, 125, 220, 15, "$2.4M All-in",
                                    font_size=10, text_color=COLORS['bg_dark']))
    requests.extend(create_text_box(slide_id, 70, 142, 220, 15, "1 of 4 Key Hands",
                                    font_size=8, text_color=COLORS['bg_dark']))

    requests.extend(create_text_box(slide_id, 30, 200, 320, 40,
                                    "Phil Ivey: ALL-IN\nD. Negreanu: CALL",
                                    font_size=11, text_color=COLORS['text_white']))

    # 우측: 설명
    requests.extend(create_text_box(slide_id, 380, 25, 320, 25,
                                    "WSOPTV OTT의 핵심 지능형 기능",
                                    font_size=12, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 380, 50, 320, 20,
                                    "'Smart Key Hands' 알림바",
                                    font_size=11, text_color=COLORS['text_white']))

    features = [
        ("1. 자동 하이라이트 추출:", "핸드 중 All-in, Big Pot, 레어 핸드 발생 시 AI가 즉시 'Key Hand'로 등록"),
        ("2. 즉시 이동:", "시청자가 바를 클릭하면 해당 핸드 시작점으로 점프"),
        ("3. 상황 인지:", '"지금까지 놓친 핸드" 요약')
    ]

    for i, (title, desc) in enumerate(features):
        y = 100 + i * 80
        requests.extend(create_text_box(slide_id, 380, y, 320, 20, title,
                                        font_size=10, bold=True,
                                        text_color=COLORS['text_white']))
        requests.extend(create_text_box(slide_id, 380, y+20, 320, 50, desc,
                                        font_size=9, text_color=COLORS['text_gray']))

    return requests


def build_slide_14(slide_id):
    """Preview / Recap"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 좌측: Preview
    requests.extend(create_text_box(slide_id, 20, 15, 150, 20, "Summary | Preview",
                                    font_size=10, text_color=COLORS['text_gray']))
    requests.extend(create_rect(slide_id, 20, 40, 340, 290,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 50, 320, 25, "MAIN EVENT DAY 5",
                                    font_size=14, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 75, 320, 20, "PREVIEW",
                                    font_size=12, text_color=COLORS['text_white']))

    preview_content = """Starting Chips:
  - Ivey: $15.2M
  - Negreanu: $8.7M
  - Hellmuth: $6.3M

Key Matchups:
  - Ivey vs Negreanu (H2H: 3-2)

Players to Watch:
  - Phil Ivey (HOT)"""
    requests.extend(create_text_box(slide_id, 30, 105, 320, 200, preview_content,
                                    font_size=9, text_color=COLORS['text_gray']))

    # 우측: Recap
    requests.extend(create_text_box(slide_id, 380, 15, 150, 20, "Summary | Recap",
                                    font_size=10, text_color=COLORS['text_gray']))
    requests.extend(create_rect(slide_id, 380, 40, 320, 290,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 390, 50, 300, 25, "MAIN EVENT DAY 4",
                                    font_size=14, bold=True,
                                    text_color=COLORS['text_white']))
    requests.extend(create_text_box(slide_id, 390, 75, 300, 20, "RECAP",
                                    font_size=12, text_color=COLORS['text_gray']))

    recap_content = """Final Chips:
  - Ivey: $15.2M
  - Negreanu: $8.7M
  - Hellmuth: $6.3M

Eliminations:
  - Tom Dwan (12th)
  - Doug Polk (15th)

Key Hands:
  - $2.4M All-in
  - Royal Flush"""
    requests.extend(create_text_box(slide_id, 390, 105, 300, 200, recap_content,
                                    font_size=9, text_color=COLORS['text_gray']))

    # 하단 설명
    requests.extend(create_text_box(slide_id, 20, 345, 680, 30,
                                    "Preview: 시작 전 분석 / Recap: 데이 종료 후 요약",
                                    font_size=11, text_color=COLORS['accent'],
                                    align='CENTER'))

    return requests


def build_slide_15(slide_id):
    """Player Stats"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 제목
    requests.extend(create_text_box(slide_id, 20, 15, 200, 25, "Player Stats",
                                    font_size=16, bold=True,
                                    text_color=COLORS['accent']))

    # 테이블 헤더
    requests.extend(create_rect(slide_id, 20, 45, 680, 30,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    headers = ["PLAYER", "HANDS", "VPIP", "PFR", "3-BET", "BB WON", "SHOWDOWN"]
    x_positions = [30, 150, 230, 300, 370, 450, 560]

    for header, x in zip(headers, x_positions):
        requests.extend(create_text_box(slide_id, x, 50, 80, 20, header,
                                        font_size=9, bold=True,
                                        text_color=COLORS['accent']))

    # 플레이어 데이터
    players = [
        ("Phil Ivey", "142", "22%", "18%", "8%", "+125", "12 (8W)"),
        ("D. Negreanu", "138", "28%", "22%", "12%", "+89", "15 (9W)"),
        ("Phil Hellmuth", "145", "18%", "12%", "6%", "+67", "8 (5W)"),
        ("Tom Dwan", "134", "32%", "25%", "15%", "-45", "18 (7W)"),
        ("Doug Polk", "140", "25%", "20%", "10%", "-23", "10 (4W)"),
        ("Patrik Ant...", "128", "20%", "15%", "9%", "+34", "9 (6W)")
    ]

    for i, row in enumerate(players):
        y = 80 + i * 35
        # 행 배경
        bg = COLORS['bg_card'] if i % 2 == 0 else COLORS['bg_section']
        requests.extend(create_rect(slide_id, 20, y, 680, 30,
                                    fill_color=bg, outline_color=COLORS['outline']))

        for val, x in zip(row, x_positions):
            color = COLORS['green'] if val.startswith('+') else (
                COLORS['live_red'] if val.startswith('-') else COLORS['text_white'])
            requests.extend(create_text_box(slide_id, x, y+5, 80, 20, val,
                                            font_size=9, text_color=color))

    # Legend
    requests.extend(create_rect(slide_id, 20, 300, 680, 60,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 30, 305, 100, 15, "Legend:",
                                    font_size=10, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 325, 660, 30,
                                    "VPIP = Voluntarily Put $ In Pot | PFR = Pre-Flop Raise | BB WON = Big Blinds Won/Lost",
                                    font_size=9, text_color=COLORS['text_gray']))

    return requests


def build_slide_16(slide_id):
    """Position Chart"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 제목
    requests.extend(create_text_box(slide_id, 20, 15, 400, 25,
                                    "Position Charts  [All Players]  [All Hands]",
                                    font_size=14, bold=True,
                                    text_color=COLORS['accent']))

    # 좌측: Phil Ivey
    requests.extend(create_rect(slide_id, 20, 50, 340, 280,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 30, 60, 320, 20, "PHIL IVEY",
                                    font_size=12, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 80, 320, 15, "All Players",
                                    font_size=9, text_color=COLORS['text_gray']))

    # 테이블 차트 (좌)
    requests.extend(create_rect(slide_id, 70, 110, 240, 160,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 150, 130, 80, 20, "POKER TABLE",
                                    font_size=9, text_color=COLORS['text_gray'],
                                    align='CENTER'))
    # Position 데이터
    positions = [("UTG", "OX"), ("MP", "OO"), ("CO", "OOO"),
                 ("BTN", "OOO"), ("SB", "X"), ("BB", "XO")]
    for i, (pos, result) in enumerate(positions):
        col = i % 3
        row = i // 3
        x = 90 + col * 75
        y = 180 + row * 50
        requests.extend(create_text_box(slide_id, x, y, 60, 15, pos,
                                        font_size=9, text_color=COLORS['text_white']))
        requests.extend(create_text_box(slide_id, x, y+15, 60, 15, result,
                                        font_size=10, bold=True,
                                        text_color=COLORS['green']))

    requests.extend(create_text_box(slide_id, 30, 290, 320, 20, "Win Rate: 57.1%",
                                    font_size=10, bold=True,
                                    text_color=COLORS['green']))
    requests.extend(create_text_box(slide_id, 30, 310, 320, 15, "O Won  X Lost",
                                    font_size=8, text_color=COLORS['text_gray']))

    # 우측: Daniel Negreanu
    requests.extend(create_rect(slide_id, 380, 50, 320, 280,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 390, 60, 300, 20, "DANIEL NEGREANU",
                                    font_size=12, bold=True,
                                    text_color=COLORS['text_white']))
    requests.extend(create_text_box(slide_id, 390, 80, 300, 15, "All Players",
                                    font_size=9, text_color=COLORS['text_gray']))

    # 테이블 차트 (우)
    requests.extend(create_rect(slide_id, 420, 110, 240, 160,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 500, 130, 80, 20, "POKER TABLE",
                                    font_size=9, text_color=COLORS['text_gray'],
                                    align='CENTER'))

    requests.extend(create_text_box(slide_id, 390, 290, 300, 20, "Win Rate: 46.7%",
                                    font_size=10, bold=True,
                                    text_color=COLORS['text_gray']))

    # 하단 설명
    requests.extend(create_text_box(slide_id, 20, 345, 680, 30,
                                    "포지션별 승률 시각화 - NBA Shot Plot 스타일 적용",
                                    font_size=11, text_color=COLORS['accent'],
                                    align='CENTER'))

    return requests


def build_slide_17(slide_id):
    """Performance Heatmap (핵심)"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 제목
    requests.extend(create_text_box(slide_id, 20, 15, 400, 25,
                                    "Performance Heatmap  [Win Rate vs Avg]",
                                    font_size=14, bold=True,
                                    text_color=COLORS['accent']))

    # 좌측: 히트맵
    requests.extend(create_rect(slide_id, 20, 50, 340, 280,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 60, 320, 20, "PHIL IVEY",
                                    font_size=12, bold=True,
                                    text_color=COLORS['accent']))

    # 히트맵 테이블
    requests.extend(create_rect(slide_id, 60, 90, 260, 180,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 150, 100, 80, 20, "POKER TABLE",
                                    font_size=9, text_color=COLORS['text_gray'],
                                    align='CENTER'))

    # 히트맵 데이터
    heatmap_data = [
        ("UTG", "+12%", "green"), ("MP", "+8%", "green"), ("CO", "+15%", "green"),
        ("BTN", "+18%", "green"), ("SB", "+2%", "yellow"), ("BB", "-8%", "red")
    ]

    for i, (pos, val, color_name) in enumerate(heatmap_data):
        col = i % 3
        row = i // 3
        x = 90 + col * 75
        y = 150 + row * 60

        color_map = {
            "green": COLORS['green'],
            "yellow": {'red': 0.9, 'green': 0.8, 'blue': 0.2},
            "red": COLORS['live_red']
        }

        requests.extend(create_rect(slide_id, x-5, y-5, 60, 40,
                                    fill_color=color_map[color_name],
                                    outline_color=COLORS['outline']))
        requests.extend(create_text_box(slide_id, x, y, 50, 15, pos,
                                        font_size=9, bold=True,
                                        text_color=COLORS['bg_dark']))
        requests.extend(create_text_box(slide_id, x, y+15, 50, 15, val,
                                        font_size=9,
                                        text_color=COLORS['bg_dark']))

    requests.extend(create_text_box(slide_id, 30, 285, 320, 15, "Win% vs League Avg",
                                    font_size=9, text_color=COLORS['text_gray']))
    requests.extend(create_text_box(slide_id, 30, 305, 320, 15, "[-10]  [0]  [+10]",
                                    font_size=9, text_color=COLORS['text_gray']))

    # 우측: 범례
    requests.extend(create_rect(slide_id, 380, 50, 320, 280,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))

    legend_items = [
        ("승률을 '많이 이겼는지'가", ""),
        ("아니라, '평균 대비 잘", ""),
        ("이겼는지'를 보여주는 차트", ""),
        ("", ""),
        ("색상:", ""),
        ("초록: 평균보다 높음", "(+10%p 이상)"),
        ("노랑: 평균 수준", "(+/-10%p)"),
        ("빨강: 평균보다 낮음", "(-10%p 이상)")
    ]

    for i, (text, sub) in enumerate(legend_items):
        y = 65 + i * 30
        color = COLORS['text_white']
        if "초록" in text:
            color = COLORS['green']
        elif "노랑" in text:
            color = {'red': 0.9, 'green': 0.8, 'blue': 0.2}
        elif "빨강" in text:
            color = COLORS['live_red']

        requests.extend(create_text_box(slide_id, 390, y, 300, 20, text,
                                        font_size=10, text_color=color))
        if sub:
            requests.extend(create_text_box(slide_id, 520, y, 150, 20, sub,
                                            font_size=9, text_color=COLORS['text_gray']))

    # 하단 설명
    requests.extend(create_text_box(slide_id, 20, 345, 680, 30,
                                    "NBA Shot Zone 히트맵 -> WSOPTV 포지션별 성과 히트맵",
                                    font_size=11, text_color=COLORS['accent'],
                                    align='CENTER'))

    return requests


def build_slide_18(slide_id):
    """Interactive Player Filter"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 좌측: 플레이어 필터
    requests.extend(create_rect(slide_id, 20, 20, 280, 330,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 30, 30, 260, 20, "PLAYER FILTER",
                                    font_size=12, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 55, 260, 15, "All Players",
                                    font_size=9, text_color=COLORS['text_gray']))

    players = [
        ("Phil Ivey", False),
        ("D. Negreanu", False),
        ("Phil Hellmuth", False),
        ("Tom Dwan", False),
        ("Doug Polk", True),  # Selected
        ("Patrik Antonius", False)
    ]

    for i, (name, selected) in enumerate(players):
        y = 80 + i * 25
        check = "[X]" if selected else "[ ]"
        color = COLORS['accent'] if selected else COLORS['text_white']
        requests.extend(create_text_box(slide_id, 30, y, 30, 20, check,
                                        font_size=10, text_color=color))
        requests.extend(create_text_box(slide_id, 60, y, 200, 20, name,
                                        font_size=10, text_color=color))

    # 선택된 플레이어 차트
    requests.extend(create_rect(slide_id, 40, 240, 240, 80,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 50, 250, 220, 20, "DOUG POLK",
                                    font_size=11, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 50, 275, 220, 20, "O X O X O",
                                    font_size=14, text_color=COLORS['green']))
    requests.extend(create_text_box(slide_id, 50, 300, 220, 15, "Win: 52.9% (9/17)",
                                    font_size=10, text_color=COLORS['text_white']))

    # 우측: 설명
    requests.extend(create_rect(slide_id, 320, 20, 380, 330,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))

    explanations = [
        ("인터랙티브 선수 필터 (좌측):",
         "체크박스로 특정 선수 선택.\n예: Doug Polk 선택 시 해당 선수 데이터만 동기화"),
        ("포지션 데이터 시각화 (중앙):",
         "테이블 위에 승/패 표시\n- O (파란색): Win\n- X (빨간색): Loss"),
        ("실시간 성과 지표 (하단):",
         "현재까지의 승률과 핸드 수\n예: 52.9%, 9/17")
    ]

    for i, (title, desc) in enumerate(explanations):
        y = 40 + i * 100
        requests.extend(create_text_box(slide_id, 335, y, 350, 20, title,
                                        font_size=11, bold=True,
                                        text_color=COLORS['accent']))
        requests.extend(create_text_box(slide_id, 335, y+25, 350, 65, desc,
                                        font_size=9, text_color=COLORS['text_gray']))

    return requests


def build_slide_19(slide_id):
    """Chip Tracker & Comparison"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # Chip Tracker (상단)
    requests.extend(create_rect(slide_id, 20, 20, 680, 140,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 30, 30, 200, 20, "CHIP TRACKER",
                                    font_size=14, bold=True,
                                    text_color=COLORS['accent']))

    # 칩 바
    requests.extend(create_text_box(slide_id, 30, 60, 80, 15, "Ivey",
                                    font_size=10, text_color=COLORS['text_white']))
    requests.extend(create_rect(slide_id, 110, 60, 400, 20,
                                fill_color=COLORS['accent'],
                                outline_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 520, 60, 100, 15, "$15.2M",
                                    font_size=10, bold=True,
                                    text_color=COLORS['accent']))

    requests.extend(create_text_box(slide_id, 30, 90, 80, 15, "Negr",
                                    font_size=10, text_color=COLORS['text_white']))
    requests.extend(create_rect(slide_id, 110, 90, 230, 20,
                                fill_color=COLORS['blue'],
                                outline_color=COLORS['blue']))
    requests.extend(create_text_box(slide_id, 350, 90, 100, 15, "$8.7M",
                                    font_size=10, text_color=COLORS['blue']))

    # 레벨 라벨
    requests.extend(create_text_box(slide_id, 110, 115, 500, 15,
                                    "Level 1         Level 2         Level 3         Level 4",
                                    font_size=8, text_color=COLORS['text_gray']))

    # 통계
    requests.extend(create_text_box(slide_id, 30, 135, 660, 15,
                                    "Biggest Stack: $15.2M (Ivey)  |  Avg Stack: $6.8M  |  Eliminations: 12  |  Remaining: 45",
                                    font_size=9, text_color=COLORS['text_gray']))

    # Player Network (좌하단)
    requests.extend(create_rect(slide_id, 20, 170, 280, 180,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 30, 180, 260, 20, "PLAYER NETWORK",
                                    font_size=11, bold=True,
                                    text_color=COLORS['text_white']))

    # 네트워크 다이어그램 (간략화)
    requests.extend(create_text_box(slide_id, 70, 220, 180, 80,
                                    "   Ivey-----Negr\n    |\\      /|\n    | \\    / |\n    |  \\  /  |\n   Hell--X--Dwan",
                                    font_size=9, text_color=COLORS['text_gray']))
    requests.extend(create_text_box(slide_id, 30, 320, 260, 20, "같은 핸드 참여 관계",
                                    font_size=9, text_color=COLORS['text_gray']))

    # Head-to-Head (우하단)
    requests.extend(create_rect(slide_id, 320, 170, 380, 180,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 330, 180, 360, 20, "HEAD-TO-HEAD",
                                    font_size=11, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 330, 205, 360, 20, "Ivey vs Negreanu",
                                    font_size=12, bold=True,
                                    text_color=COLORS['text_white']))

    h2h_stats = [
        "Hands: 23",
        "Ivey Won: 14 (61%)",
        "Negreanu Won: 9 (39%)",
        "Biggest Pot: $2.4M"
    ]
    for i, stat in enumerate(h2h_stats):
        requests.extend(create_text_box(slide_id, 330, 235 + i*25, 360, 20, stat,
                                        font_size=10, text_color=COLORS['text_gray']))

    # 하단 설명
    requests.extend(create_text_box(slide_id, 20, 360, 680, 30,
                                    "NBA Lead Tracker -> WSOPTV Chip Tracker 적용",
                                    font_size=11, text_color=COLORS['accent'],
                                    align='CENTER'))

    return requests


def build_slide_20(slide_id):
    """Feature Summary"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 제목
    requests.extend(create_text_box(slide_id, 200, 20, 320, 30,
                                    "WSOPTV OTT - Feature Summary",
                                    font_size=18, bold=True,
                                    text_color=COLORS['accent'], align='CENTER'))

    # Feature 카드 - 상단 행
    features_row1 = [
        ("3-Layer\nMultiView", "4개 테이블\n동시 시청"),
        ("Smart Key\nHands", "AI 자동\n하이라이트"),
        ("Performance\nHeatmap", "포지션별\n승률 분석")
    ]

    for i, (title, desc) in enumerate(features_row1):
        x = 100 + i * 180
        requests.extend(create_rect(slide_id, x, 70, 160, 110,
                                    fill_color=COLORS['bg_card'],
                                    outline_color=COLORS['accent']))
        requests.extend(create_text_box(slide_id, x+10, 80, 140, 40, title,
                                        font_size=12, bold=True,
                                        text_color=COLORS['accent'], align='CENTER'))
        requests.extend(create_text_box(slide_id, x+10, 130, 140, 40, desc,
                                        font_size=10, text_color=COLORS['text_white'],
                                        align='CENTER'))

    # Feature 카드 - 하단 행
    features_row2 = [
        ("Player\nCam", "선수별\n전용 스트림"),
        ("20 Lang\nSupport", "다국어\n자막/해설"),
        ("Hand-by-\nHand", "실시간\n플레이 로그")
    ]

    for i, (title, desc) in enumerate(features_row2):
        x = 100 + i * 180
        requests.extend(create_rect(slide_id, x, 200, 160, 110,
                                    fill_color=COLORS['bg_card'],
                                    outline_color=COLORS['outline']))
        requests.extend(create_text_box(slide_id, x+10, 210, 140, 40, title,
                                        font_size=12, bold=True,
                                        text_color=COLORS['text_white'], align='CENTER'))
        requests.extend(create_text_box(slide_id, x+10, 260, 140, 40, desc,
                                        font_size=10, text_color=COLORS['text_gray'],
                                        align='CENTER'))

    # 슬로건
    requests.extend(create_text_box(slide_id, 150, 340, 420, 30,
                                    '"Watch Like You\'re at the Table"',
                                    font_size=16, bold=True,
                                    text_color=COLORS['accent'], align='CENTER'))

    return requests


def build_slide_21(slide_id):
    """Hand-by-Hand"""
    requests = []

    # 배경
    requests.extend(create_rect(slide_id, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT,
                                fill_color=COLORS['bg_dark']))

    # 제목
    requests.extend(create_text_box(slide_id, 20, 15, 300, 25,
                                    "Hand-by-Hand  [Level 4]  [ALL]",
                                    font_size=14, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 20, 40, 400, 15,
                                    "[LIVE] Auto Switch Level O  Latest First O",
                                    font_size=9, text_color=COLORS['text_gray']))

    # 테이블
    requests.extend(create_rect(slide_id, 20, 60, 680, 280,
                                fill_color=COLORS['bg_card'],
                                outline_color=COLORS['accent']))

    # 헤더
    requests.extend(create_rect(slide_id, 25, 65, 670, 25,
                                fill_color=COLORS['bg_section'],
                                outline_color=COLORS['outline']))
    requests.extend(create_text_box(slide_id, 35, 70, 80, 15, "Time",
                                    font_size=9, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 130, 70, 350, 15, "Action",
                                    font_size=9, bold=True,
                                    text_color=COLORS['accent']))
    requests.extend(create_text_box(slide_id, 550, 70, 100, 15, "Pot",
                                    font_size=9, bold=True,
                                    text_color=COLORS['accent']))

    # Hand 데이터
    hands = [
        ("02:31:15", "Phil Ivey raises to $45,000 (BTN)", "$67,500"),
        ("02:31:22", "D. Negreanu 3-bets to $150,000 (BB)", "$217,500"),
        ("02:31:35", "Phil Ivey 4-bets to $450,000", "$517,500"),
        ("02:31:48", "D. Negreanu 5-bet ALL-IN $8,250,000", "$8.7M"),
        ("02:31:55", "Phil Ivey CALLS", "$17.4M"),
        ("02:32:10", "SHOWDOWN", ""),
        ("", "Ivey: A-A  vs  Negreanu: K-K", ""),
        ("02:32:45", "Phil Ivey WINS $17.4M", "")
    ]

    for i, (time, action, pot) in enumerate(hands):
        y = 95 + i * 25

        # 특별한 행 강조
        if "ALL-IN" in action or "WINS" in action:
            requests.extend(create_rect(slide_id, 25, y-3, 670, 22,
                                        fill_color=COLORS['accent']))
            text_color = COLORS['bg_dark']
        elif "SHOWDOWN" in action:
            requests.extend(create_rect(slide_id, 25, y-3, 670, 22,
                                        fill_color=COLORS['bg_section']))
            text_color = COLORS['accent']
        else:
            text_color = COLORS['text_white']

        requests.extend(create_text_box(slide_id, 35, y, 80, 15, time,
                                        font_size=9, text_color=text_color))
        requests.extend(create_text_box(slide_id, 130, y, 400, 15, action,
                                        font_size=9, text_color=text_color))
        requests.extend(create_text_box(slide_id, 550, y, 100, 15, pot,
                                        font_size=9, bold=True,
                                        text_color=text_color))

    # 하단 설명
    requests.extend(create_text_box(slide_id, 20, 355, 680, 30,
                                    "NBA Play-by-Play -> WSOPTV Hand-by-Hand 적용",
                                    font_size=11, text_color=COLORS['accent'],
                                    align='CENTER'))

    return requests


# ============================================================
# 슬라이드 빌더 매핑
# ============================================================

SLIDE_BUILDERS = {
    1: build_slide_1,
    2: build_slide_2,
    3: build_slide_3,
    4: build_slide_4,
    5: build_slide_5,
    6: build_slide_6,
    7: build_slide_7,
    8: build_slide_8,
    9: build_slide_9,
    10: build_slide_10,
    11: build_slide_11,
    12: build_slide_12,
    13: build_slide_13,
    14: build_slide_14,
    15: build_slide_15,
    16: build_slide_16,
    17: build_slide_17,
    18: build_slide_18,
    19: build_slide_19,
    20: build_slide_20,
    21: build_slide_21
}


def main():
    """메인 실행"""
    print("=" * 60)
    print("WSOPTV Wireframe Slides Generator")
    print("=" * 60)

    try:
        service = get_slides_service()

        # 프레젠테이션 정보 가져오기
        presentation = service.presentations().get(
            presentationId=PRESENTATION_ID
        ).execute()

        original_slides = presentation.get('slides', [])
        original_count = len(original_slides)

        print(f"\n[INFO] 프레젠테이션: {presentation.get('title')}")
        print(f"[INFO] 기존 슬라이드: {original_count}개")
        print(f"[INFO] 생성할 슬라이드: 21개")
        print(f"[INFO] 최종 슬라이드: {original_count + 21}개")

        print("\n[START] 슬라이드 생성 시작...")
        print("-" * 60)

        # 뒤에서부터 삽입 (인덱스 유지)
        for slide_num in range(21, 0, -1):
            print(f"  [CREATING] 슬라이드 {slide_num}-1 (WSOPTV Wireframe)...")

            # 새 슬라이드 ID (고유)
            new_slide_id = f"wsoptv_{slide_num}_{uuid.uuid4().hex[:6]}"

            # 삽입 위치 (기존 슬라이드 뒤)
            insert_index = slide_num  # 0-indexed에서 slide_num 위치에 삽입

            # 1. 슬라이드 생성
            create_request = create_slide_request(new_slide_id, insert_index)

            body = {'requests': [create_request]}
            service.presentations().batchUpdate(
                presentationId=PRESENTATION_ID,
                body=body
            ).execute()

            # 2. 슬라이드 내용 추가
            if slide_num in SLIDE_BUILDERS:
                content_requests = SLIDE_BUILDERS[slide_num](new_slide_id)

                if content_requests:
                    body = {'requests': content_requests}
                    service.presentations().batchUpdate(
                        presentationId=PRESENTATION_ID,
                        body=body
                    ).execute()

            print(f"  [OK] 슬라이드 {slide_num}-1 완료")

        print("\n" + "=" * 60)
        print("[COMPLETE] 모든 슬라이드 생성 완료!")
        print(f"[LINK] https://docs.google.com/presentation/d/{PRESENTATION_ID}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
