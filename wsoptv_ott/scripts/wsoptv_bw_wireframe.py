#!/usr/bin/env python3
"""
WSOPTV B&W Wireframe Slides Generator
NBA TV DNA 기반 2-Column 레이아웃 (65:35)
19개 슬라이드 (슬라이드 2-21, 1번과 20번 제외)
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

# ============================================================
# B&W 색상 팔레트
# ============================================================
COLORS_BW = {
    'bg': {'red': 1, 'green': 1, 'blue': 1},              # 흰색 배경
    'primary': {'red': 0.1, 'green': 0.1, 'blue': 0.1},   # 검정 (주요 텍스트)
    'secondary': {'red': 0.4, 'green': 0.4, 'blue': 0.4}, # 회색 (보조)
    'border': {'red': 0.3, 'green': 0.3, 'blue': 0.3},    # 테두리
    'light': {'red': 0.9, 'green': 0.9, 'blue': 0.9},     # 연한 배경
    'medium': {'red': 0.7, 'green': 0.7, 'blue': 0.7},    # 중간 회색
}

# 2-Column 레이아웃 상수
LEFT_PANEL_X = 10
LEFT_PANEL_WIDTH = 460  # 65%
RIGHT_PANEL_X = 480
RIGHT_PANEL_WIDTH = 230  # 35%
PANEL_HEIGHT = 385
PANEL_Y = 10


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
    return f"bw_{uuid.uuid4().hex[:8]}"


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
# 공통 주석 패널 생성 함수
# ============================================================
def create_annotation_panel(slide_id, title, key_elements, nba_dna, viewer_perspective):
    """우측 주석 패널 생성 (35% 영역)"""
    requests = []

    # 주석 패널 배경
    requests.extend(create_rect(slide_id, RIGHT_PANEL_X, PANEL_Y, RIGHT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))

    y = PANEL_Y + 10

    # 페이지 제목
    requests.extend(create_text_box(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_WIDTH - 20, 20,
                                    f"**{title}**",
                                    font_size=11, bold=True,
                                    text_color=COLORS_BW['primary']))
    y += 30

    # 핵심 요소 섹션
    requests.extend(create_text_box(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_WIDTH - 20, 15,
                                    "핵심 요소",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    y += 15

    # 구분선
    requests.extend(create_line(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_X + RIGHT_PANEL_WIDTH - 10, y,
                               color=COLORS_BW['border']))
    y += 8

    # 핵심 요소 목록
    for elem in key_elements:
        requests.extend(create_text_box(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_WIDTH - 20, 12,
                                        f"• {elem}",
                                        font_size=7,
                                        text_color=COLORS_BW['secondary']))
        y += 14

    y += 10

    # NBA TV DNA 섹션
    requests.extend(create_text_box(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_WIDTH - 20, 15,
                                    "NBA TV DNA",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    y += 15

    requests.extend(create_line(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_X + RIGHT_PANEL_WIDTH - 10, y,
                               color=COLORS_BW['border']))
    y += 8

    # DNA 텍스트
    for line in nba_dna:
        requests.extend(create_text_box(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_WIDTH - 20, 12,
                                        line,
                                        font_size=7,
                                        text_color=COLORS_BW['secondary']))
        y += 14

    y += 10

    # 시청 관점 섹션
    requests.extend(create_text_box(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_WIDTH - 20, 15,
                                    "시청 관점",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    y += 15

    requests.extend(create_line(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_X + RIGHT_PANEL_WIDTH - 10, y,
                               color=COLORS_BW['border']))
    y += 8

    # 시청 관점 목록
    for point in viewer_perspective:
        requests.extend(create_text_box(slide_id, RIGHT_PANEL_X + 10, y, RIGHT_PANEL_WIDTH - 20, 12,
                                        f"- {point}",
                                        font_size=7,
                                        text_color=COLORS_BW['secondary']))
        y += 14

    return requests


# ============================================================
# 슬라이드별 Wireframe 빌더
# ============================================================

def build_slide_2(slide_id):
    """슬라이드 2: 메인 화면 구조"""
    requests = []

    # 좌측 콘텐츠 영역 (65%)
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # Table Strip
    requests.extend(create_rect(slide_id, 15, 15, 450, 35,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 20, 18, 440, 12,
                                    "[TABLE STRIP]",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 20, 32, 440, 12,
                                    "T1:MAIN  T2:PLO  T3:NLH  T4:HIGH  |  45/LIVE  23/LIVE  67/LIVE  8/FINAL",
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # Hero Section
    requests.extend(create_rect(slide_id, 15, 55, 310, 200,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 60, 290, 15,
                                    "MAIN EVENT DAY 5",
                                    font_size=10, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 78, 290, 12,
                                    "FEATURE TABLE",
                                    font_size=8,
                                    text_color=COLORS_BW['secondary']))

    # Hero Video Placeholder
    requests.extend(create_rect(slide_id, 30, 95, 280, 120,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 100, 145, 140, 20,
                                    "[HERO VIDEO]",
                                    font_size=9,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))

    # Quick Actions
    for i, btn in enumerate(["WATCH", "STATS", "HANDS"]):
        requests.extend(create_rect(slide_id, 30 + i*95, 220, 85, 25,
                                    fill_color=COLORS_BW['primary'],
                                    outline_color=COLORS_BW['primary']))
        requests.extend(create_text_box(slide_id, 30 + i*95, 225, 85, 15,
                                        btn,
                                        font_size=8, bold=True,
                                        text_color=COLORS_BW['bg'],
                                        align='CENTER'))

    # Headlines
    requests.extend(create_rect(slide_id, 335, 55, 130, 200,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 340, 60, 120, 15,
                                    "HEADLINES",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))

    headlines = ["> Ivey leads $15.2M", "> Negreanu #5", "> Hellmuth bracelet"]
    for i, h in enumerate(headlines):
        requests.extend(create_text_box(slide_id, 340, 80 + i*40, 120, 35,
                                        h,
                                        font_size=7,
                                        text_color=COLORS_BW['secondary']))

    # Related Content
    requests.extend(create_text_box(slide_id, 15, 255, 450, 12,
                                    "[Related: Top 5 Hands Today]",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "MAIN SCREEN",
        ["Table Strip (실시간 테이블 현황)", "Hero Section (메인 이벤트 강조)",
         "Quick Actions (WATCH/STATS/HANDS)", "Related Content (추천 콘텐츠)"],
        ['"실시간 정보가 항상', '  눈에 들어오게"', '+ 1클릭 접근', '+ 자동 추천'],
        ["어디서든 현황 파악", "1클릭으로 시청 시작", "뉴스로 맥락 이해"]
    ))

    return requests


def build_slide_3(slide_id):
    """슬라이드 3: 콘텐츠 섹션 구성"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # LIVE NOW 섹션
    requests.extend(create_text_box(slide_id, 15, 15, 100, 15,
                                    "LIVE NOW",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))

    for i in range(4):
        requests.extend(create_rect(slide_id, 15 + i*110, 32, 100, 45,
                                    fill_color=COLORS_BW['light'],
                                    outline_color=COLORS_BW['border']))
        label = ["T1 LIVE", "T2 LIVE", "T3 LIVE", "FEAT ALL-A"][i]
        requests.extend(create_text_box(slide_id, 20 + i*110, 45, 90, 15,
                                        label,
                                        font_size=7,
                                        text_color=COLORS_BW['secondary'],
                                        align='CENTER'))

    # TRENDING HANDS 섹션
    requests.extend(create_text_box(slide_id, 15, 85, 150, 15,
                                    "TRENDING HANDS",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 400, 85, 60, 12,
                                    "[See All >]",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))

    trending = ["▶4:51\n$2.4M", "▶3:22\nBLUFF", "▶5:10\nROYAL", "▶2:45\nBADBT"]
    for i, t in enumerate(trending):
        requests.extend(create_rect(slide_id, 15 + i*110, 102, 100, 50,
                                    fill_color=COLORS_BW['light'],
                                    outline_color=COLORS_BW['border']))
        requests.extend(create_text_box(slide_id, 20 + i*110, 110, 90, 35,
                                        t,
                                        font_size=7,
                                        text_color=COLORS_BW['secondary'],
                                        align='CENTER'))

    # BIGGEST POTS 섹션
    requests.extend(create_text_box(slide_id, 15, 160, 180, 15,
                                    "BIGGEST POTS 2026",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 400, 160, 60, 12,
                                    "[See All >]",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))

    pots = ["$5M\nALLIN", "$4.1M\nALLIN", "$3.2M\nALLIN", "$2.8M\nALLIN"]
    for i, p in enumerate(pots):
        requests.extend(create_rect(slide_id, 15 + i*110, 177, 100, 50,
                                    fill_color=COLORS_BW['light'],
                                    outline_color=COLORS_BW['border']))
        requests.extend(create_text_box(slide_id, 20 + i*110, 185, 90, 35,
                                        p,
                                        font_size=7,
                                        text_color=COLORS_BW['secondary'],
                                        align='CENTER'))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "CONTENT SECTIONS",
        ["Live Now (실시간 라이브)", "Trending Hands (인기 핸드 실시간)",
         "Themed Collections (테마별 큐레이션)", "See All Links (확장 탐색)"],
        ['"테마별 큐레이션으로', '  발견의 즐거움"', '+ 실시간 트렌드 반영', '+ 과거 콘텐츠 접근'],
        ["뭘 볼지 모를 때", "큐레이션이 안내", "트렌드 따라가기"]
    ))

    return requests


def build_slide_4(slide_id):
    """슬라이드 4: Around WSOP (뉴스)"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 제목
    requests.extend(create_text_box(slide_id, 15, 15, 200, 20,
                                    "AROUND WSOP",
                                    font_size=12, bold=True,
                                    text_color=COLORS_BW['primary']))

    # 뉴스 항목
    news_items = [
        ("POY RACE: IVEY #1", "Phil Ivey takes lead...", "June 17, 2026"),
        ("BRACELET WATCH", "Top candidates for...", "June 17, 2026"),
        ("ROOKIE SPOTLIGHT", "First-time players...", "June 15, 2026")
    ]

    for i, (title, desc, date) in enumerate(news_items):
        y = 42 + i * 70
        requests.extend(create_rect(slide_id, 15, y, 450, 60,
                                    fill_color=COLORS_BW['light'],
                                    outline_color=COLORS_BW['border']))
        # 이미지 플레이스홀더
        requests.extend(create_rect(slide_id, 20, y + 5, 70, 50,
                                    fill_color=COLORS_BW['medium'],
                                    outline_color=COLORS_BW['border']))
        requests.extend(create_text_box(slide_id, 25, y + 22, 60, 15,
                                        "[IMG]",
                                        font_size=7,
                                        text_color=COLORS_BW['secondary'],
                                        align='CENTER'))
        # 제목
        requests.extend(create_text_box(slide_id, 100, y + 8, 360, 15,
                                        title,
                                        font_size=9, bold=True,
                                        text_color=COLORS_BW['primary']))
        # 설명
        requests.extend(create_text_box(slide_id, 100, y + 25, 360, 12,
                                        desc,
                                        font_size=7,
                                        text_color=COLORS_BW['secondary']))
        # 날짜
        requests.extend(create_text_box(slide_id, 100, y + 42, 150, 12,
                                        date,
                                        font_size=6,
                                        text_color=COLORS_BW['medium']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "NEWS FEED",
        ["News List (최신순 정렬)", "Thumbnail + Title (이미지 + 제목)",
         "Date Stamp (날짜 표시)", "Mixed Media (기사 + 영상)"],
        ['"경기 외 스토리로', '  팬심 유지"', '+ 최신순 = 신선함', '+ 기사/영상 혼합'],
        ["경기 외적 스토리", "선수 인간적 면모", "커뮤니티 연결감"]
    ))

    return requests


def build_slide_5(slide_id):
    """슬라이드 5: Streaming Options (Views)"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 중앙 패널
    requests.extend(create_rect(slide_id, 60, 20, 380, 240,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))

    # 제목
    requests.extend(create_text_box(slide_id, 80, 30, 340, 20,
                                    "STREAMING OPTIONS",
                                    font_size=11, bold=True,
                                    text_color=COLORS_BW['primary'],
                                    align='CENTER'))

    # 탭
    tabs = ["[Views]", "[Languages]", "[Audio]"]
    for i, tab in enumerate(tabs):
        bold = (i == 0)
        requests.extend(create_text_box(slide_id, 100 + i*110, 55, 100, 15,
                                        tab,
                                        font_size=8, bold=bold,
                                        text_color=COLORS_BW['primary'] if bold else COLORS_BW['secondary'],
                                        align='CENTER'))

    # 구분선
    requests.extend(create_line(slide_id, 80, 75, 420, 75, color=COLORS_BW['border']))

    # 옵션 목록
    options = [
        ("[●] Feature Table View", "Main broadcast"),
        ("[ ] Player Cam", "Focus on player"),
        ("[ ] Stats Overlay", "Real-time statistics"),
        ("[ ] Mobile Optimized", "Vertical view")
    ]

    for i, (opt, desc) in enumerate(options):
        y = 85 + i * 40
        requests.extend(create_text_box(slide_id, 90, y, 300, 15,
                                        opt,
                                        font_size=9, bold=True,
                                        text_color=COLORS_BW['primary']))
        requests.extend(create_text_box(slide_id, 120, y + 15, 280, 12,
                                        desc,
                                        font_size=7,
                                        text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "STREAMING OPTIONS",
        ["Tab Navigation (Views/Lang/Audio)", "Radio Selection (단일 선택)",
         "Description Text (옵션별 설명)", "4가지 뷰 옵션"],
        ['"같은 경기, 다른 관점"', '→ 시청자가 원하는', '  방식 선택'],
        ['"어떻게 볼지" 선택', "개인화된 시청 경험", "디바이스별 최적화"]
    ))

    return requests


def build_slide_6(slide_id):
    """슬라이드 6: Player Cam 비교"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # Phil Ivey 패널
    requests.extend(create_text_box(slide_id, 15, 15, 150, 15,
                                    "Phil Ivey",
                                    font_size=10, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_rect(slide_id, 15, 32, 215, 140,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 70, 80, 100, 15,
                                    "[PLAYER CAM]",
                                    font_size=8,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 20, 130, 200, 12,
                                    "Chips: $15.2M | Rank: 1/45",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_text_box(slide_id, 20, 145, 200, 12,
                                    "VPIP: 22% | PFR: 18%",
                                    font_size=6,
                                    text_color=COLORS_BW['medium']))

    # Daniel Negreanu 패널
    requests.extend(create_text_box(slide_id, 240, 15, 180, 15,
                                    "Daniel Negreanu",
                                    font_size=10, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_rect(slide_id, 240, 32, 215, 140,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 295, 80, 100, 15,
                                    "[PLAYER CAM]",
                                    font_size=8,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 245, 130, 200, 12,
                                    "Chips: $8.7M | Rank: 5/45",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_text_box(slide_id, 245, 145, 200, 12,
                                    "VPIP: 28% | PFR: 22%",
                                    font_size=6,
                                    text_color=COLORS_BW['medium']))

    # 핵심 메시지 박스
    requests.extend(create_rect(slide_id, 15, 180, 440, 50,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 190, 420, 15,
                                    '"응원하는 선수에게만 집중"',
                                    font_size=10, bold=True,
                                    text_color=COLORS_BW['primary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 25, 210, 420, 12,
                                    "= WSOPTV 핵심 가치 제안",
                                    font_size=8,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "PLAYER CAM ★핵심",
        ["Player Video Feed (선수별 전용 캠)", "Real-time Stats (칩/순위/스탯)",
         "Side-by-side View (비교 시청)", "Favorite Selection (관심 선수 선택)"],
        ['"당신이 보고 싶은', '  팀/선수에게만 집중"', '→ Lakers팬=Lakers만', '→ Ivey팬=Ivey만'],
        ["팬덤 기반 개인화", "몰입도 극대화", "감정적 연결"]
    ))

    return requests


def build_slide_7(slide_id):
    """슬라이드 7: 다국어 지원"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 중앙 패널
    requests.extend(create_rect(slide_id, 60, 20, 380, 230,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))

    # 제목
    requests.extend(create_text_box(slide_id, 80, 30, 340, 20,
                                    "STREAMING OPTIONS",
                                    font_size=11, bold=True,
                                    text_color=COLORS_BW['primary'],
                                    align='CENTER'))

    # 탭 (Languages 선택)
    tabs = ["[Views]", "[Languages]", "[Audio]"]
    for i, tab in enumerate(tabs):
        bold = (i == 1)
        requests.extend(create_text_box(slide_id, 100 + i*110, 55, 100, 15,
                                        tab,
                                        font_size=8, bold=bold,
                                        text_color=COLORS_BW['primary'] if bold else COLORS_BW['secondary'],
                                        align='CENTER'))

    # 구분선
    requests.extend(create_line(slide_id, 80, 75, 420, 75, color=COLORS_BW['border']))

    # 언어 목록
    languages = [
        ("[●] English (Default)", "Professional commentary"),
        ("[ ] Spanish - GGPoker", "Pre/Live/Post analysis"),
        ("[ ] Portuguese - GGPoker", " "),
        ("[ ] Japanese", " "),
        ("[ ] Korean", " "),
        ("[ ] Chinese", " ")
    ]

    for i, (lang, desc) in enumerate(languages):
        y = 80 + i * 25
        requests.extend(create_text_box(slide_id, 90, y, 280, 13,
                                        lang,
                                        font_size=8,
                                        text_color=COLORS_BW['primary']))
        if desc.strip():
            requests.extend(create_text_box(slide_id, 280, y, 150, 13,
                                            desc,
                                            font_size=6,
                                            text_color=COLORS_BW['secondary']))

    # +15 more
    requests.extend(create_text_box(slide_id, 90, 230, 200, 12,
                                    "+ 15 more languages...",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))

    # PRD 참조
    requests.extend(create_text_box(slide_id, 15, 255, 250, 12,
                                    "[PRD-0002: 20개국 다국어 자막]",
                                    font_size=6,
                                    text_color=COLORS_BW['medium']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "LANGUAGE OPTIONS",
        ["Language List (언어 목록)", "Default Selection (기본값 English)",
         "Partner Streams (GGPoker 등 파트너)", "20+ Languages (20개국 지원)"],
        ['"글로벌 접근성"', '→ 언어 장벽 없이', '  누구나 시청'],
        ["모국어 시청", "이해도 상승", "몰입도 증가"]
    ))

    return requests


def build_slide_8(slide_id):
    """슬라이드 8: 플레이어 컨트롤 UI"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 헤더
    requests.extend(create_text_box(slide_id, 15, 15, 300, 15,
                                    "MAIN EVENT - FEATURE TABLE",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 350, 15, 100, 12,
                                    "[Settings]",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_text_box(slide_id, 15, 30, 150, 12,
                                    "Feature Table View",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))

    # 메인 비디오 영역
    requests.extend(create_rect(slide_id, 15, 45, 440, 150,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['primary']))

    # 포커 테이블 표시
    requests.extend(create_text_box(slide_id, 170, 100, 120, 20,
                                    "[POKER TABLE VIEW]",
                                    font_size=8,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))

    # 플레이어 위치
    players = [
        (25, 55, "Player 1", "$15.2M"),
        (380, 55, "Player 2", "$8.7M"),
        (25, 160, "Player 6", " "),
        (380, 160, "Player 3", " "),
        (180, 75, "POT: $2,450,000", " ")
    ]
    for x, y, name, chips in players:
        requests.extend(create_text_box(slide_id, x, y, 80, 10,
                                        name,
                                        font_size=6, bold=True,
                                        text_color=COLORS_BW['primary']))
        if chips.strip():
            requests.extend(create_text_box(slide_id, x, y + 10, 80, 10,
                                            chips,
                                            font_size=5,
                                            text_color=COLORS_BW['secondary']))

    # 레이아웃 스위처
    requests.extend(create_rect(slide_id, 15, 200, 150, 25,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 20, 205, 140, 15,
                                    "Layout: [1] [2] [4]",
                                    font_size=8,
                                    text_color=COLORS_BW['primary']))

    # Quick Action Bar
    requests.extend(create_rect(slide_id, 15, 230, 440, 30,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    buttons = ["Tables 4", "MultiVw", "KeyHands", "Stats"]
    for i, btn in enumerate(buttons):
        requests.extend(create_rect(slide_id, 20 + i*110, 235, 100, 20,
                                    fill_color=COLORS_BW['bg'],
                                    outline_color=COLORS_BW['border']))
        requests.extend(create_text_box(slide_id, 20 + i*110, 238, 100, 15,
                                        btn,
                                        font_size=7, bold=True,
                                        text_color=COLORS_BW['primary'],
                                        align='CENTER'))

    # 타임라인
    requests.extend(create_text_box(slide_id, 15, 265, 440, 12,
                                    "▶ 02:31:43 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ LIVE",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "PLAYER CONTROLS",
        ["Header Bar (제목 + 설정)", "Main Video Area (포커 테이블 뷰)",
         "Layout Switcher [1][2][4]", "Quick Action Bar (4개 버튼)",
         "Timeline/Seek Bar"],
        ['"핵심 기능 3가지에', '  1클릭 접근"', '- Streams (다른 경기)', '- MultiView (동시)', '- Key Plays (하이라이트)'],
        ["시청 중단 없이 접근", "레이아웃 즉시 변경", "4버튼으로 단순화"]
    ))

    return requests


def build_slide_9(slide_id):
    """슬라이드 9: MultiView 선택"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 메인 뷰 (Fixed)
    requests.extend(create_rect(slide_id, 15, 15, 440, 80,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 170, 40, 120, 20,
                                    "[MAIN TABLE VIEW]",
                                    font_size=8,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 170, 60, 120, 15,
                                    "Feature Table - 9p",
                                    font_size=6,
                                    text_color=COLORS_BW['medium'],
                                    align='CENTER'))

    # Add Slot 1
    requests.extend(create_rect(slide_id, 15, 100, 215, 110,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 60, 115, 130, 15,
                                    "+ Add from",
                                    font_size=8,
                                    text_color=COLORS_BW['primary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 60, 130, 130, 15,
                                    "Table Strip",
                                    font_size=8,
                                    text_color=COLORS_BW['primary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 25, 155, 200, 50,
                                    "Available:\n• T2 ($10K)\n• T3 ($5K)\n• T4 ($25K)",
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # Add Slot 2
    requests.extend(create_rect(slide_id, 240, 100, 215, 110,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 285, 115, 130, 15,
                                    "+ Add from",
                                    font_size=8,
                                    text_color=COLORS_BW['primary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 285, 130, 130, 15,
                                    "Table Strip",
                                    font_size=8,
                                    text_color=COLORS_BW['primary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 250, 155, 200, 50,
                                    "Or choose:\n• Stats View\n• Player Cam\n• History",
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # Tip
    requests.extend(create_rect(slide_id, 15, 220, 440, 30,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 228, 420, 15,
                                    "TIP: Drag from Table Strip",
                                    font_size=8,
                                    text_color=COLORS_BW['primary'],
                                    align='CENTER'))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "MULTIVIEW SELECT",
        ["Main View (Fixed) (메인 뷰 고정)", "Add Slots (추가 슬롯 2-3개)",
         "Table Strip 연동 (드래그 앤 드롭)", "Content Options (Tables/Stats/Cam)"],
        ['"Score Strip에서', '  직접 추가"', '→ 직관적 콘텐츠 조합'],
        ["원하는 조합 직접 구성", "드래그로 쉽게 추가", "유연한 레이아웃"]
    ))

    return requests


def build_slide_10(slide_id):
    """슬라이드 10: 2분할 뷰"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 좌측 뷰 (MAIN EVENT)
    requests.extend(create_rect(slide_id, 15, 15, 217, 200,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 20, 20, 200, 15,
                                    "MAIN EVENT",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 20, 35, 200, 12,
                                    "Feature Table",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_rect(slide_id, 30, 50, 185, 100,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 80, 90, 80, 15,
                                    "[POKER TABLE]",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 20, 160, 200, 12,
                                    "POT: $2.4M | 9 players",
                                    font_size=7,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 20, 175, 100, 15,
                                    "[AUDIO: ON]",
                                    font_size=7, bold=True,
                                    text_color=COLORS_BW['primary']))

    # 우측 뷰 ($10K PLO)
    requests.extend(create_rect(slide_id, 238, 15, 217, 200,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 243, 20, 200, 15,
                                    "$10K PLO",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_text_box(slide_id, 243, 35, 200, 12,
                                    "Final Table",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_rect(slide_id, 253, 50, 185, 100,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 303, 90, 80, 15,
                                    "[POKER TABLE]",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))
    requests.extend(create_text_box(slide_id, 243, 160, 200, 12,
                                    "POT: $850K | 6 players",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_text_box(slide_id, 243, 175, 100, 15,
                                    "[AUDIO:MUTED]",
                                    font_size=7,
                                    text_color=COLORS_BW['medium']))

    # 핵심 메시지
    requests.extend(create_rect(slide_id, 15, 220, 440, 35,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 230, 420, 15,
                                    "핵심: 각 뷰 독립 오디오 컨트롤 → 메인 해설 + 다른 테이블 모니터",
                                    font_size=8,
                                    text_color=COLORS_BW['primary'],
                                    align='CENTER'))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "2-SPLIT VIEW",
        ["2개 동시 뷰 (50:50 분할)", "Independent Audio (각 뷰 독립 오디오)",
         "Table Info Overlay (테이블명/POT/인원)", "Audio Toggle (ON/MUTED 스위치)"],
        ['"서로 다른 콘텐츠', '  동시 시청"', '+ 각 뷰 독립 오디오'],
        ["놓치고 싶지 않은 상황 동시 추적", "해설 들으면서 모니터"]
    ))

    return requests


def build_slide_11(slide_id):
    """슬라이드 11: 3-Layer MultiView (핵심)"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 4분할 그리드
    views = [
        (15, 15, 220, 110, "LAYER 1: MAIN", "[FEATURE TBL]\nPOT: $2.4M\nIvey: ALL-IN", True),
        (240, 15, 215, 110, "LAYER 2: T2", "[$10K PLO]\nPOT: $850K", False),
        (15, 130, 220, 110, "LAYER 2: T3", "[$5K NLH]\nPOT: $340K", False),
        (240, 130, 215, 110, "LAYER 3: STATS", "HAND HISTORY\n#142 3-bet\n#143 ↗\n#144 ALL-IN⚠", False)
    ]

    for x, y, w, h, title, content, is_primary in views:
        outline = COLORS_BW['primary'] if is_primary else COLORS_BW['border']
        requests.extend(create_rect(slide_id, x, y, w, h,
                                    fill_color=COLORS_BW['bg'],
                                    outline_color=outline))
        requests.extend(create_text_box(slide_id, x + 5, y + 5, w - 10, 12,
                                        title,
                                        font_size=7, bold=True,
                                        text_color=COLORS_BW['primary'] if is_primary else COLORS_BW['secondary']))
        requests.extend(create_rect(slide_id, x + 10, y + 22, w - 20, h - 35,
                                    fill_color=COLORS_BW['light'],
                                    outline_color=COLORS_BW['border']))
        requests.extend(create_text_box(slide_id, x + 15, y + 35, w - 30, h - 50,
                                        content,
                                        font_size=6,
                                        text_color=COLORS_BW['secondary']))

    # 하단 라벨
    requests.extend(create_text_box(slide_id, 15, 250, 300, 15,
                                    "3-Layer Multi-view | PRD-0006 Advanced Mode",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['primary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "3-LAYER MULTIVIEW ★핵심",
        ["Layer 1: Main (Feature Table)", "Layer 2: Secondary (Other Tables 2-3)",
         "Layer 3: Stats (Hand History/Stats)", "4-Split Grid (2x2 레이아웃)"],
        ['"4분할, 각 뷰가', '  독립적 목적"', '- 팀 브랜딩', '- 메인 액션', '- 하이라이트', '- 분위기'],
        ["전문가 시청 모드", "여러 테이블+통계", "Advanced Mode 핵심"]
    ))

    return requests


def build_slide_12(slide_id):
    """슬라이드 12: Key Hands"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 중앙 패널
    requests.extend(create_rect(slide_id, 50, 15, 380, 245,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))

    # 제목
    requests.extend(create_text_box(slide_id, 70, 22, 320, 20,
                                    "KEY HANDS",
                                    font_size=12, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 400, 22, 20, 15,
                                    "[X]",
                                    font_size=9,
                                    text_color=COLORS_BW['secondary']))

    # Key hands 목록
    hands = [
        ("[IMG]", "$2.4M All-in: Ivey", "Hand #142 • 02:31:15", "★ BIGGEST POT TODAY"),
        ("[IMG]", "Sick Bluff by Hellmuth", "Hand #138 • 02:15:22", " "),
        ("[IMG]", "Royal Flush - T3", "Hand #125 • 01:45:10", "♦ RARE HAND"),
        ("[IMG]", "Bad Beat: Set over Set", "Hand #112 • 01:22:45", "💔 BAD BEAT")
    ]

    for i, (img, title, time, badge) in enumerate(hands):
        y = 48 + i * 48
        # 썸네일
        requests.extend(create_rect(slide_id, 60, y, 45, 38,
                                    fill_color=COLORS_BW['light'],
                                    outline_color=COLORS_BW['border']))
        requests.extend(create_text_box(slide_id, 62, y + 12, 40, 15,
                                        img,
                                        font_size=6,
                                        text_color=COLORS_BW['medium'],
                                        align='CENTER'))
        # 제목
        requests.extend(create_text_box(slide_id, 115, y + 3, 300, 13,
                                        title,
                                        font_size=9, bold=True,
                                        text_color=COLORS_BW['primary']))
        # 시간
        requests.extend(create_text_box(slide_id, 115, y + 17, 200, 11,
                                        time,
                                        font_size=6,
                                        text_color=COLORS_BW['secondary']))
        # 배지
        if badge.strip():
            requests.extend(create_text_box(slide_id, 115, y + 30, 150, 11,
                                            badge,
                                            font_size=6, bold=True,
                                            text_color=COLORS_BW['primary']))

    # 하단 Tip
    requests.extend(create_text_box(slide_id, 70, 245, 340, 12,
                                    "→ 클릭 시 해당 핸드 시작점으로 이동",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "KEY HANDS",
        ["Scrollable List (스크롤 가능 목록)", "Thumbnail + Title (썸네일 + 제목)",
         "Timestamp (Hand# + 시간)", "Tags/Labels (BIGGEST/RARE/BAD)",
         "Click = Jump (클릭 → 즉시 이동)"],
        ['"주요 장면 빠르게 찾기"', '- 시간순 정렬', '- 썸네일+설명+시간', '- 클릭 = 즉시 점프'],
        ['"뭘 볼지 모를 때"', "Key Hands가 안내"]
    ))

    return requests


def build_slide_13(slide_id):
    """슬라이드 13: Smart Key Hands AI (핵심)"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 테이블 뷰
    requests.extend(create_rect(slide_id, 15, 15, 260, 180,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 90, 30, 120, 15,
                                    "[POKER TABLE VIEW]",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary'],
                                    align='CENTER'))

    # Smart Key Hand 알림바
    requests.extend(create_rect(slide_id, 45, 55, 190, 50,
                                fill_color=COLORS_BW['primary'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 55, 60, 170, 13,
                                    "⚡ Smart Key Hand",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['bg']))
    requests.extend(create_text_box(slide_id, 55, 75, 170, 12,
                                    "$2.4M All-in",
                                    font_size=8,
                                    text_color=COLORS_BW['bg']))
    requests.extend(create_text_box(slide_id, 55, 90, 170, 10,
                                    "1 of 4 Key Hands",
                                    font_size=6,
                                    text_color=COLORS_BW['light']))

    # 선수 정보
    requests.extend(create_text_box(slide_id, 25, 130, 240, 30,
                                    "Phil Ivey: ALL-IN\nNegreanu: CALL",
                                    font_size=8,
                                    text_color=COLORS_BW['primary']))

    # 우측 설명
    requests.extend(create_rect(slide_id, 285, 15, 170, 240,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 295, 25, 150, 15,
                                    "AI 감지 대상:",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['primary']))

    detections = [
        "• All-in 상황 ★★★",
        "• $1M+ Pot ★★★",
        "• Rare Hands ★★★",
        "• Star vs Star ★★"
    ]
    for i, d in enumerate(detections):
        requests.extend(create_text_box(slide_id, 295, 45 + i*20, 150, 15,
                                        d,
                                        font_size=7,
                                        text_color=COLORS_BW['secondary']))

    requests.extend(create_text_box(slide_id, 295, 130, 150, 12,
                                    "3가지 핵심 가치:",
                                    font_size=7, bold=True,
                                    text_color=COLORS_BW['primary']))
    values = [
        "1. 자동 하이라이트",
        "2. 즉시 이동",
        "3. 상황 인지"
    ]
    for i, v in enumerate(values):
        requests.extend(create_text_box(slide_id, 295, 148 + i*18, 150, 15,
                                        v,
                                        font_size=6,
                                        text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "SMART KEY HANDS ★AI",
        ["AI Auto Detection (AI 자동 감지)", "Popup Notification (팝업 알림)",
         "Click to Jump (클릭 → 점프)", "Catch-up Summary (놓친 핸드 요약)"],
        ['"AI가 중요한 순간을', '  자동으로 찾아줌"', '1. 자동 하이라이트', '2. 즉시 이동', '3. 상황 인지'],
        ["늦게 접속해도 OK", "놓친 장면 알림", "타임라인 안 뒤져도"]
    ))

    return requests


def build_slide_14(slide_id):
    """슬라이드 14: Preview / Recap"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # Preview 패널
    requests.extend(create_text_box(slide_id, 15, 15, 120, 12,
                                    "PREVIEW (Day 5)",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_rect(slide_id, 15, 30, 217, 210,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 40, 200, 15,
                                    "MAIN EVENT DAY 5",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    preview_content = """Starting:
• Ivey $15.2M
• Negr $8.7M
• Hell $6.3M

Key Matchups:
• Ivey vs Neg (H2H: 3-2)

Watch: Ivey🔥"""
    requests.extend(create_text_box(slide_id, 25, 60, 200, 170,
                                    preview_content,
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # Recap 패널
    requests.extend(create_text_box(slide_id, 240, 15, 120, 12,
                                    "RECAP (Day 4)",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_rect(slide_id, 240, 30, 217, 210,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 250, 40, 200, 15,
                                    "MAIN EVENT DAY 4",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['secondary']))
    recap_content = """Final:
• Ivey $15.2M
• Negr $8.7M
• Hell $6.3M

Eliminations:
• Dwan (12th)
• Polk (15th)

Top Hands:
• $2.4M All-in"""
    requests.extend(create_text_box(slide_id, 250, 60, 200, 170,
                                    recap_content,
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "PREVIEW / RECAP",
        ["Preview Mode (경기 전 기대감)", "- Starting Chips, Key Matchups",
         "Recap Mode (경기 후 정리)", "- Final Chips, Eliminations, Top Hands"],
        ['"경기 전: 기대감 조성"', '"경기 후: 정리와 회고"'],
        ["Preview: 오늘 뭐볼까", "Recap: 빠른 따라잡기"]
    ))

    return requests


def build_slide_15(slide_id):
    """슬라이드 15: Player Stats (Box Score)"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 제목
    requests.extend(create_text_box(slide_id, 15, 15, 150, 18,
                                    "PLAYER STATS",
                                    font_size=11, bold=True,
                                    text_color=COLORS_BW['primary']))

    # 테이블 헤더
    requests.extend(create_rect(slide_id, 15, 38, 440, 22,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    headers = ["PLAYER", "HANDS", "VPIP", "PFR", "BB WON"]
    x_positions = [20, 120, 190, 260, 350]
    for h, x in zip(headers, x_positions):
        requests.extend(create_text_box(slide_id, x, 42, 70, 12,
                                        h,
                                        font_size=7, bold=True,
                                        text_color=COLORS_BW['primary']))

    # 데이터 행
    players = [
        ("Phil Ivey", "142", "22%", "18%", "+125"),
        ("D.Negreanu", "138", "28%", "22%", "+89"),
        ("P.Hellmuth", "145", "18%", "12%", "+67"),
        ("Tom Dwan", "134", "32%", "25%", "-45"),
        ("Doug Polk", "140", "25%", "20%", "-23")
    ]

    for i, row in enumerate(players):
        y = 62 + i * 22
        bg = COLORS_BW['bg'] if i % 2 == 0 else COLORS_BW['light']
        requests.extend(create_rect(slide_id, 15, y, 440, 20,
                                    fill_color=bg,
                                    outline_color=COLORS_BW['border']))
        for val, x in zip(row, x_positions):
            requests.extend(create_text_box(slide_id, x, y + 4, 70, 12,
                                            val,
                                            font_size=6,
                                            text_color=COLORS_BW['primary']))

    # Legend
    requests.extend(create_rect(slide_id, 15, 180, 440, 55,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 20, 185, 50, 12,
                                    "Legend:",
                                    font_size=7, bold=True,
                                    text_color=COLORS_BW['primary']))
    legend_text = """• VPIP = 자발적 팟 참여율
• PFR = 프리플랍 레이즈율
• BB WON = 획득/손실 빅블라인드"""
    requests.extend(create_text_box(slide_id, 20, 200, 420, 35,
                                    legend_text,
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "BOX SCORE",
        ["Data Table (선수별 스탯 테이블)", "Sortable Columns (컬럼별 정렬)",
         "Key Metrics:", "- HANDS (참여 핸드)", "- VPIP (참여율)", "- BB WON (획득/손실)"],
        ['"선수별 상세 스탯"', '→ 숫자로 경기력 파악', '(MIN→HANDS, FG%→VPIP,', ' PTS→BB WON)'],
        ["숫자로 스타일 파악", "선수 비교 분석"]
    ))

    return requests


def build_slide_16(slide_id):
    """슬라이드 16: Position Chart (Shot Plot)"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 제목
    requests.extend(create_text_box(slide_id, 15, 15, 200, 15,
                                    "POSITION CHARTS",
                                    font_size=10, bold=True,
                                    text_color=COLORS_BW['primary']))

    # Phil Ivey 차트
    requests.extend(create_rect(slide_id, 15, 35, 215, 195,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 25, 40, 190, 15,
                                    "PHIL IVEY",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 55, 100, 12,
                                    "All Players ▼",
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # 테이블 차트
    requests.extend(create_rect(slide_id, 40, 72, 170, 110,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 90, 80, 80, 12,
                                    "POKER TABLE",
                                    font_size=6,
                                    text_color=COLORS_BW['medium'],
                                    align='CENTER'))

    # Position 데이터
    positions = [("UTG", "○×"), ("MP", "○○"), ("CO", "○○○"),
                 ("BTN", "○○○"), ("SB", "×"), ("BB", "×○")]
    for i, (pos, result) in enumerate(positions):
        col = i % 3
        row = i // 3
        x = 55 + col * 55
        y = 105 + row * 40
        requests.extend(create_text_box(slide_id, x, y, 45, 10,
                                        pos,
                                        font_size=6,
                                        text_color=COLORS_BW['secondary']))
        requests.extend(create_text_box(slide_id, x, y + 12, 45, 12,
                                        result,
                                        font_size=8, bold=True,
                                        text_color=COLORS_BW['primary']))

    requests.extend(create_text_box(slide_id, 25, 190, 180, 12,
                                    "Win: 57.1%  |  ○=Won ×=Lost",
                                    font_size=7,
                                    text_color=COLORS_BW['primary']))

    # Daniel Negreanu 차트
    requests.extend(create_rect(slide_id, 240, 35, 215, 195,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 250, 40, 190, 15,
                                    "D. NEGREANU",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_text_box(slide_id, 250, 55, 100, 12,
                                    "All Players ▼",
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    requests.extend(create_rect(slide_id, 265, 72, 170, 110,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 315, 80, 80, 12,
                                    "POKER TABLE",
                                    font_size=6,
                                    text_color=COLORS_BW['medium'],
                                    align='CENTER'))

    requests.extend(create_text_box(slide_id, 250, 190, 180, 12,
                                    "Win: 46.7%",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "SHOT PLOT",
        ["Table Position Map (포지션별 시각화)", "Win/Loss Markers (○=Won, ×=Lost)",
         "Position Labels (UTG/MP/CO/BTN/SB/BB)", "Player Dropdown (선수 선택)",
         "Win Rate Summary (총 승률 표시)"],
        ['"공간 기반 데이터 시각화"', '- 코트 위치 → 포지션', '- Made/Miss → Win/Loss'],
        ["어느 포지션에서 강함?", "패턴 파악"]
    ))

    return requests


def build_slide_17(slide_id):
    """슬라이드 17: Performance Heatmap (Shot Zone)"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 제목
    requests.extend(create_text_box(slide_id, 15, 15, 300, 15,
                                    "PERFORMANCE HEATMAP",
                                    font_size=10, bold=True,
                                    text_color=COLORS_BW['primary']))

    # 히트맵 패널
    requests.extend(create_rect(slide_id, 15, 35, 250, 195,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 42, 180, 15,
                                    "PHIL IVEY",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))

    # 히트맵 그리드
    requests.extend(create_rect(slide_id, 35, 62, 210, 120,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 105, 68, 80, 12,
                                    "POKER TABLE",
                                    font_size=6,
                                    text_color=COLORS_BW['medium'],
                                    align='CENTER'))

    # 히트맵 셀 (그레이스케일로 표현)
    heatmap_data = [
        ("UTG", "+12%", COLORS_BW['primary']),
        ("MP", "+8%", COLORS_BW['primary']),
        ("CO", "+15%", COLORS_BW['primary']),
        ("BTN", "+18%", COLORS_BW['primary']),
        ("SB", "+2%", COLORS_BW['medium']),
        ("BB", "-8%", COLORS_BW['light'])
    ]

    for i, (pos, val, color) in enumerate(heatmap_data):
        col = i % 3
        row = i // 3
        x = 50 + col * 65
        y = 92 + row * 45
        requests.extend(create_rect(slide_id, x, y, 50, 35,
                                    fill_color=color,
                                    outline_color=COLORS_BW['border']))
        text_color = COLORS_BW['bg'] if color == COLORS_BW['primary'] else COLORS_BW['primary']
        requests.extend(create_text_box(slide_id, x + 5, y + 5, 40, 12,
                                        pos,
                                        font_size=7, bold=True,
                                        text_color=text_color))
        requests.extend(create_text_box(slide_id, x + 5, y + 18, 40, 12,
                                        val,
                                        font_size=7,
                                        text_color=text_color))

    # 범례
    requests.extend(create_text_box(slide_id, 25, 190, 220, 12,
                                    "Win% vs Average: [-10%] ─── [+10%]",
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # 설명 패널
    requests.extend(create_rect(slide_id, 275, 35, 180, 195,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    explanation = """색상 의미:

■ (진함)
 평균보다 높음 (+10%p↑)

□ (중간)
 평균 수준 (±10%p)

░ (연함)
 평균보다 낮음 (-10%p↓)

→ "많이 이겼는지"가 아니라
  "평균 대비 잘 이겼는지"를
  보여주는 차트"""
    requests.extend(create_text_box(slide_id, 285, 45, 160, 175,
                                    explanation,
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "SHOT ZONE",
        ["Heatmap Grid (포지션별 성과 격자)", "Color Intensity (진함/중간/연함)",
         "Percentage Labels (정확한 수치)", "vs Average Compare (평균 대비 비교)"],
        ['"평균 대비 성과 비교"', '→ 많이 이겼는지 (X)', '→ 평균 대비 잘 이겼는지'],
        ["진짜 강점/약점 파악", "상대적 성과 분석"]
    ))

    return requests


def build_slide_18(slide_id):
    """슬라이드 18: Interactive Player Filter"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 필터 패널
    requests.extend(create_rect(slide_id, 15, 15, 200, 225,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 25, 22, 180, 15,
                                    "PLAYER FILTER",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 38, 100, 12,
                                    "All Players",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))

    # 체크박스 목록
    players = [
        ("□ Phil Ivey", False),
        ("□ D. Negreanu", False),
        ("□ Phil Hellmuth", False),
        ("□ Tom Dwan", False),
        ("■ Doug Polk", True),
        ("□ Patrik Antonius", False)
    ]

    for i, (name, selected) in enumerate(players):
        y = 55 + i * 22
        color = COLORS_BW['primary'] if selected else COLORS_BW['secondary']
        requests.extend(create_text_box(slide_id, 30, y, 170, 15,
                                        name,
                                        font_size=8,
                                        text_color=color))

    # 선택된 플레이어 미니 차트
    requests.extend(create_rect(slide_id, 30, 190, 170, 45,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 40, 195, 150, 13,
                                    "DOUG POLK",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 40, 210, 150, 12,
                                    "○ × ○ × ○",
                                    font_size=10,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 40, 222, 150, 10,
                                    "Win: 52.9% (9/17)",
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # 설명 패널
    requests.extend(create_rect(slide_id, 225, 15, 230, 225,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    explanation = """선수 필터 기능:

1. 체크박스로 선택
   → 특정 선수 데이터만 표시

2. 다중 선택 가능
   → 여러 선수 비교 분석

3. 선택 시 강조 표시
   → ■ = 선택됨

4. 실시간 데이터 갱신
   → 선택 즉시 차트 업데이트

5. 미니 차트 미리보기
   → 선택 선수 간략 통계"""
    requests.extend(create_text_box(slide_id, 235, 25, 210, 200,
                                    explanation,
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "PLAYER FILTER",
        ["Checkbox List (선수 체크박스)", "Multi-select (다중 선택 가능)",
         "Selected Highlight (선택 선수 강조)", "Real-time Update (실시간 갱신)",
         "Mini Chart Preview (미니 차트)"],
        ['"원하는 선수만', '  필터링해서 보기"', '- 체크박스 선택', '- 실시간 업데이트', '- 시각화 동기화'],
        ["특정 선수 집중 분석", "비교 분석 가능"]
    ))

    return requests


def build_slide_19(slide_id):
    """슬라이드 19: Chip Tracker & Comparison"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # Chip Tracker
    requests.extend(create_rect(slide_id, 15, 15, 440, 85,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 25, 20, 150, 15,
                                    "CHIP TRACKER",
                                    font_size=9, bold=True,
                                    text_color=COLORS_BW['primary']))

    # 칩 바
    requests.extend(create_text_box(slide_id, 25, 40, 50, 12,
                                    "Ivey",
                                    font_size=7,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_rect(slide_id, 80, 40, 300, 15,
                                fill_color=COLORS_BW['primary'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 390, 40, 60, 12,
                                    "$15.2M",
                                    font_size=7, bold=True,
                                    text_color=COLORS_BW['primary']))

    requests.extend(create_text_box(slide_id, 25, 60, 50, 12,
                                    "Negr",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))
    requests.extend(create_rect(slide_id, 80, 60, 170, 15,
                                fill_color=COLORS_BW['secondary'],
                                outline_color=COLORS_BW['secondary']))
    requests.extend(create_text_box(slide_id, 260, 60, 60, 12,
                                    "$8.7M",
                                    font_size=7,
                                    text_color=COLORS_BW['secondary']))

    # 레벨 라벨
    requests.extend(create_text_box(slide_id, 80, 80, 350, 10,
                                    "Lv1          Lv2          Lv3          Lv4",
                                    font_size=5,
                                    text_color=COLORS_BW['medium']))

    # Network 패널
    requests.extend(create_rect(slide_id, 15, 105, 215, 130,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 25, 110, 150, 15,
                                    "NETWORK",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['secondary']))
    network_text = """   Ivey───Negr
    | \\    / |
    |  \\  /  |
   Hell──X──Dwan

  (같은핸드참여)"""
    requests.extend(create_text_box(slide_id, 30, 130, 190, 90,
                                    network_text,
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # Head-to-Head 패널
    requests.extend(create_rect(slide_id, 240, 105, 215, 130,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 250, 110, 150, 15,
                                    "HEAD-TO-HEAD",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 250, 128, 190, 13,
                                    "Ivey vs Negreanu",
                                    font_size=8, bold=True,
                                    text_color=COLORS_BW['primary']))
    h2h_text = """Hands: 23
Ivey: 14 (61%)
Negr: 9 (39%)
Biggest: $2.4M"""
    requests.extend(create_text_box(slide_id, 250, 145, 190, 70,
                                    h2h_text,
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "LEAD TRACKER",
        ["Chip Progress Bar (칩 변화 막대)", "Timeline Axis (레벨별 시간축)",
         "Summary Stats (최대/평균)", "Player Network (대결 관계 그래프)",
         "H2H Stats (1:1 대결 통계)"],
        ['"시간에 따른 리드 변화"', '+ 선수 간 관계 네트워크', '+ 팀 비교 (H2H)'],
        ["누가 이기고 있는가?", "누구와 자주 맞붙는가?"]
    ))

    return requests


def build_slide_21(slide_id):
    """슬라이드 21: Hand-by-Hand (Play-by-Play)"""
    requests = []

    # 좌측 콘텐츠 영역
    requests.extend(create_rect(slide_id, LEFT_PANEL_X, PANEL_Y, LEFT_PANEL_WIDTH, PANEL_HEIGHT,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['border']))

    # 제목
    requests.extend(create_text_box(slide_id, 15, 15, 200, 15,
                                    "HAND-BY-HAND",
                                    font_size=10, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 200, 15, 250, 12,
                                    "[Level 4] [ALL] [LIVE] Auto○ Latest○",
                                    font_size=6,
                                    text_color=COLORS_BW['secondary']))

    # 테이블
    requests.extend(create_rect(slide_id, 15, 35, 440, 200,
                                fill_color=COLORS_BW['bg'],
                                outline_color=COLORS_BW['primary']))

    # 헤더
    requests.extend(create_rect(slide_id, 20, 40, 430, 18,
                                fill_color=COLORS_BW['light'],
                                outline_color=COLORS_BW['border']))
    requests.extend(create_text_box(slide_id, 25, 43, 60, 12,
                                    "Time",
                                    font_size=7, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 100, 43, 200, 12,
                                    "Action",
                                    font_size=7, bold=True,
                                    text_color=COLORS_BW['primary']))
    requests.extend(create_text_box(slide_id, 380, 43, 60, 12,
                                    "Pot",
                                    font_size=7, bold=True,
                                    text_color=COLORS_BW['primary']))

    # 데이터 행
    hands = [
        ("02:31:15", "Ivey raises $45K", "$67K", False),
        ("02:31:22", "Negr 3-bet $150K", "$217K", False),
        ("02:31:35", "Ivey 4-bet $450K", "$517K", False),
        ("02:31:48", "★ Negr ALL-IN $8.2M", "$8.7M", True),
        ("02:31:55", "★ Ivey CALLS", "$17M", True),
        ("02:32:10", "SHOWDOWN", " ", False),
        (" ", "A♠A♥ vs K♠K♥", " ", False),
        ("02:32:45", "✓ Ivey WINS $17.4M", " ", True)
    ]

    for i, (time, action, pot, highlight) in enumerate(hands):
        y = 60 + i * 20
        if highlight:
            requests.extend(create_rect(slide_id, 20, y, 430, 18,
                                        fill_color=COLORS_BW['primary'],
                                        outline_color=COLORS_BW['primary']))
            text_color = COLORS_BW['bg']
        else:
            text_color = COLORS_BW['primary']

        requests.extend(create_text_box(slide_id, 25, y + 3, 60, 12,
                                        time,
                                        font_size=6,
                                        text_color=text_color))
        requests.extend(create_text_box(slide_id, 100, y + 3, 270, 12,
                                        action,
                                        font_size=6,
                                        text_color=text_color))
        requests.extend(create_text_box(slide_id, 380, y + 3, 60, 12,
                                        pot,
                                        font_size=6, bold=True,
                                        text_color=text_color))

    # 우측 주석 패널
    requests.extend(create_annotation_panel(
        slide_id,
        "PLAY-BY-PLAY",
        ["Action Log Table (시간순 이벤트)", "Columns: Time/Action/Pot",
         "Highlight Actions (★ ALL-IN 강조)", "Level/Filter Tabs (레벨 필터)",
         "Auto Switch Toggle (자동 전환)"],
        ['"시간순 이벤트 로그"', '- 양측 액션 나열', '- 스코어 변동 표시', '- Auto/Latest 옵션'],
        ["정확히 무슨 일이?", "시간순 추적"]
    ))

    return requests


# ============================================================
# 슬라이드 빌더 매핑
# ============================================================

SLIDE_BUILDERS = {
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
    21: build_slide_21  # 20번 제외
}


def main():
    """메인 실행"""
    print("=" * 60)
    print("WSOPTV B&W Wireframe Slides Generator")
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
        print(f"[INFO] 생성할 슬라이드: 19개 (2-19, 21번)")

        print("\n[START] B&W Wireframe 슬라이드 생성 시작...")
        print("-" * 60)

        # 슬라이드 번호 목록 (1, 20 제외)
        slide_numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21]

        # 뒤에서부터 삽입 (인덱스 유지)
        for slide_num in reversed(slide_numbers):
            print(f"  [CREATING] 슬라이드 {slide_num} (B&W Wireframe)...")

            # 새 슬라이드 ID (고유)
            new_slide_id = f"bw_{slide_num}_{uuid.uuid4().hex[:6]}"

            # 삽입 위치 (기존 슬라이드 끝에 추가)
            insert_index = original_count

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

            print(f"  [OK] 슬라이드 {slide_num} 완료")

        print("\n" + "=" * 60)
        print("[COMPLETE] B&W Wireframe 슬라이드 생성 완료!")
        print(f"[LINK] https://docs.google.com/presentation/d/{PRESENTATION_ID}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
