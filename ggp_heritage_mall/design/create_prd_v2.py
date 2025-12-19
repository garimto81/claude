"""
GGP Heritage Mall PRD v2 - Google Docs 생성
Mermaid 다이어그램 및 UI 스크린샷 포함, A4 최적화
"""
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 경로 설정
CREDENTIALS_FILE = r"D:\AI\claude01\json\desktop_credentials.json"
TOKEN_FILE = r"D:\AI\claude01\json\token.json"
DIAGRAMS_DIR = Path(r"D:\AI\claude01\ggp_heritage_mall\design\diagrams")
SCREENSHOTS_DIR = Path(r"D:\AI\claude01\ggp_heritage_mall\design\screenshots")
DRIVE_FOLDER_ID = "1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW"

# A4 사이즈 (pt)
A4_WIDTH_PT = 595
A4_HEIGHT_PT = 842
MARGIN_PT = 72  # 1인치 마진
CONTENT_WIDTH_PT = 451  # 본문 너비 (A4 - 마진*2)
MAX_IMAGE_HEIGHT_PT = 600  # 이미지 최대 높이

# Google API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]


def get_credentials():
    """OAuth 인증"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds


def upload_images(creds):
    """모든 이미지를 Google Drive에 업로드"""
    drive_service = build("drive", "v3", credentials=creds)

    # PRD v2 폴더 생성
    folder_metadata = {
        "name": "GGP Heritage Mall PRD v2",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [DRIVE_FOLDER_ID],
    }
    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    folder_id = folder["id"]
    print(f"Created folder: {folder_id}")

    uploaded = {}

    # 다이어그램 업로드
    for png_file in sorted(DIAGRAMS_DIR.glob("*.png")):
        print(f"  Uploading diagram: {png_file.name}")
        file_metadata = {"name": png_file.name, "parents": [folder_id]}
        media = MediaFileUpload(str(png_file), mimetype="image/png")
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        # 공개 설정
        drive_service.permissions().create(
            fileId=file["id"], body={"type": "anyone", "role": "reader"}
        ).execute()
        uploaded[f"diagram_{png_file.stem}"] = file["id"]

    # 스크린샷 업로드
    for png_file in sorted(SCREENSHOTS_DIR.glob("*.png")):
        print(f"  Uploading screenshot: {png_file.name}")
        file_metadata = {"name": png_file.name, "parents": [folder_id]}
        media = MediaFileUpload(str(png_file), mimetype="image/png")
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        drive_service.permissions().create(
            fileId=file["id"], body={"type": "anyone", "role": "reader"}
        ).execute()
        uploaded[f"screenshot_{png_file.stem}"] = file["id"]

    return folder_id, uploaded


def create_document(creds, uploaded_images):
    """Google Docs 문서 생성"""
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # 문서 생성
    doc = docs_service.documents().create(
        body={"title": "GGP Heritage Mall - PRD 기획서 v2"}
    ).execute()
    doc_id = doc["documentId"]
    print(f"Created document: {doc_id}")

    # 폴더로 이동
    drive_service.files().update(
        fileId=doc_id,
        addParents=DRIVE_FOLDER_ID,
        removeParents="root",
    ).execute()

    # 문서 내용 구성
    requests = build_document_content(uploaded_images)

    # 문서 업데이트
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    return doc_id


def build_document_content(uploaded_images):
    """문서 내용 구성 (역순으로 삽입)"""
    content_parts = []

    # === 표지 ===
    content_parts.append({
        "type": "text",
        "text": "\n\n\n\n\n",
    })
    content_parts.append({
        "type": "text",
        "text": "GGP Heritage Mall\n",
        "style": {"bold": True, "fontSize": 36}
    })
    content_parts.append({
        "type": "text",
        "text": "VIP 전용 헤리티지 쇼핑몰 기획서\n\n",
        "style": {"fontSize": 18}
    })
    content_parts.append({
        "type": "text",
        "text": "Version 2.0\n",
        "style": {"fontSize": 14}
    })
    content_parts.append({
        "type": "text",
        "text": "2025년 12월 18일\n\n\n\n\n\n\n\n\n",
        "style": {"fontSize": 14}
    })

    # === 1. Executive Summary ===
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "1. Executive Summary\n\n",
        "style": {"bold": True, "fontSize": 24}
    })
    content_parts.append({
        "type": "text",
        "text": """GG POKER VIP 고객을 위한 초대 전용 프리미엄 쇼핑몰입니다.

핵심 특징

""",
    })
    content_parts.append({
        "type": "text",
        "text": """    초대 전용        고유 URL 링크로만 접근 가능
    무료 증정        결제 시스템 없이 무료 배송
    등급별 혜택      Silver(3개) / Gold(5개) 수량 제한
    재고 관리        실시간 재고 추적, 품절 시 선택 불가
    고급 디자인      럭셔리하고 세련된 UI/UX

""",
    })

    # === 2. 목표 사용자 ===
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "2. 목표 사용자\n\n",
        "style": {"bold": True, "fontSize": 24}
    })
    content_parts.append({
        "type": "text",
        "text": """Primary Users

VIP 고객
    GG POKER VIP 멤버
    간편한 제품 선택 및 배송 정보 관리

관리자
    GG POKER 운영팀
    VIP 초대, 주문 처리, 재고 관리


VIP 등급 체계

""",
    })
    # VIP 등급 다이어그램
    if "diagram_04-vip-tier" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["diagram_04-vip-tier"],
            "width": CONTENT_WIDTH_PT,
            "height": 250,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    # === 3. 핵심 기능 ===
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "3. 핵심 기능\n\n",
        "style": {"bold": True, "fontSize": 24}
    })

    # 3.1 VIP 사용자 플로우
    content_parts.append({
        "type": "text",
        "text": "3.1 VIP 고객 플로우\n\n",
        "style": {"bold": True, "fontSize": 18}
    })
    if "diagram_01-vip-user-flow" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["diagram_01-vip-user-flow"],
            "width": CONTENT_WIDTH_PT,
            "height": 500,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    content_parts.append({
        "type": "text",
        "text": """주요 기능 상세

초대 링크 접근 (Critical)
    고유 토큰이 포함된 URL로만 접근 가능
    URL Format: https://heritage.ggpoker.com/shop/{invite_token}

제품 탐색 및 선택 (Critical)
    제품 목록 (그리드/리스트 뷰)
    제품 상세 페이지 (이미지 갤러리, 설명, 사이즈)
    장바구니 (선택 수량 제한 표시)
    품절 상품 표시 (선택 불가)

배송 정보 관리 (Critical)
    저장된 배송 정보 표시 (이름, 연락처, 주소)
    배송 정보 수정 기능
    배송 정보 확인 후 주문 확정

""",
    })

    # 3.2 관리자 플로우
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "3.2 관리자 플로우\n\n",
        "style": {"bold": True, "fontSize": 18}
    })
    if "diagram_05-admin-flow" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["diagram_05-admin-flow"],
            "width": CONTENT_WIDTH_PT,
            "height": 450,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    content_parts.append({
        "type": "text",
        "text": """관리자 기능 상세

VIP 초대 관리 (Critical)
    신규 VIP 초대 (이메일 + 등급 설정)
    초대 링크 생성 및 발송
    VIP 목록 조회/검색, 등급 변경, 초대 취소/재발급

주문/배송 관리 (Critical)
    주문 목록 (대기/처리중/완료)
    주문 상세 (고객 정보, 제품, 배송지)
    배송 상태 변경, 송장 번호 입력
    주문 내역 Excel 다운로드

제품/재고 관리 (High)
    제품 등록/수정/삭제
    재고 수량 설정/조정
    재고 부족 알림

통계/리포트 (Medium)
    대시보드 (오늘 주문, 전체 VIP, 재고 현황)
    주문 현황 차트, VIP 활동 리포트

""",
    })

    # 3.3 주문 상태 흐름
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "3.3 주문 상태 흐름\n\n",
        "style": {"bold": True, "fontSize": 18}
    })
    if "diagram_02-order-state" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["diagram_02-order-state"],
            "width": CONTENT_WIDTH_PT,
            "height": 350,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    # === 4. 시스템 아키텍처 ===
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "4. 시스템 아키텍처\n\n",
        "style": {"bold": True, "fontSize": 24}
    })
    if "diagram_03-system-architecture" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["diagram_03-system-architecture"],
            "width": CONTENT_WIDTH_PT,
            "height": 400,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    # === 5. 화면 구조 ===
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "5. 화면 구조\n\n",
        "style": {"bold": True, "fontSize": 24}
    })
    if "diagram_06-screen-map" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["diagram_06-screen-map"],
            "width": CONTENT_WIDTH_PT,
            "height": 500,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    # === 6. UI 시안 ===
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "6. UI 시안\n\n",
        "style": {"bold": True, "fontSize": 24}
    })

    # 6.1 랜딩 페이지
    content_parts.append({
        "type": "text",
        "text": "6.1 랜딩 페이지 (VIP 메인 화면)\n\n",
        "style": {"bold": True, "fontSize": 18}
    })
    content_parts.append({
        "type": "text",
        "text": """VIP 고객이 초대 링크를 통해 처음 접근하는 화면입니다.
Hero 섹션에서 Heritage Collection을 소개하고, 추천 제품을 표시합니다.

""",
    })
    if "screenshot_01-landing-page" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["screenshot_01-landing-page"],
            "width": CONTENT_WIDTH_PT,
            "height": MAX_IMAGE_HEIGHT_PT,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    # 6.2 제품 목록
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "6.2 제품 목록 페이지\n\n",
        "style": {"bold": True, "fontSize": 18}
    })
    content_parts.append({
        "type": "text",
        "text": """전체 제품을 브라우징하는 화면입니다.
상단에 선택 가능 수량을 표시하고, 카테고리별 필터링이 가능합니다.
각 제품 카드에서 사이즈 선택 및 재고 확인이 가능합니다.

""",
    })
    if "screenshot_02-product-list" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["screenshot_02-product-list"],
            "width": CONTENT_WIDTH_PT,
            "height": MAX_IMAGE_HEIGHT_PT,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    # 6.3 체크아웃
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "6.3 체크아웃 (배송 정보 확인)\n\n",
        "style": {"bold": True, "fontSize": 18}
    })
    content_parts.append({
        "type": "text",
        "text": """배송 정보를 확인하고 수정하는 화면입니다.
저장된 정보를 표시하고, 필요시 수정할 수 있습니다.
주문 요약에서 선택한 아이템과 VIP 무료 증정을 표시합니다.

""",
    })
    if "screenshot_03-checkout" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["screenshot_03-checkout"],
            "width": CONTENT_WIDTH_PT,
            "height": MAX_IMAGE_HEIGHT_PT,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    # 6.4 관리자 대시보드
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "6.4 관리자 대시보드\n\n",
        "style": {"bold": True, "fontSize": 18}
    })
    content_parts.append({
        "type": "text",
        "text": """관리자용 통합 대시보드입니다.
오늘 주문, 전체 VIP, 재고 부족, 배송 완료 통계를 표시합니다.
최근 주문 테이블과 실시간 활동 로그를 제공합니다.

""",
    })
    if "screenshot_04-admin-dashboard" in uploaded_images:
        content_parts.append({
            "type": "image",
            "image_id": uploaded_images["screenshot_04-admin-dashboard"],
            "width": CONTENT_WIDTH_PT,
            "height": MAX_IMAGE_HEIGHT_PT,
        })
    content_parts.append({"type": "text", "text": "\n\n"})

    # === 7. 디자인 컨셉 ===
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "7. 디자인 컨셉\n\n",
        "style": {"bold": True, "fontSize": 24}
    })
    content_parts.append({
        "type": "text",
        "text": """Design Principles

럭셔리
    다크 모드 기반, 골드/블랙 컬러 스키마

미니멀
    불필요한 요소 제거, 제품 중심

세련됨
    부드러운 애니메이션, 정교한 타이포그래피

은밀함
    브랜드 강조 최소화, 제품 경험 극대화


Color Palette

    Primary         #D4AF37 (Gold)
    Background      #0A0A0A (Deep Black)
    Surface         #1A1A1A (Dark Gray)
    Text            #FFFFFF (White)
    Accent          #B8860B (Dark Gold)


Typography

    Heading         Playfair Display (Serif, Elegant)
    Body            Inter (Sans-serif, Clean)

""",
    })

    # === Document History ===
    content_parts.append({"type": "pagebreak"})
    content_parts.append({
        "type": "text",
        "text": "Document History\n\n",
        "style": {"bold": True, "fontSize": 24}
    })
    content_parts.append({
        "type": "text",
        "text": """Version     Date            Changes                 Author

1.0         2025-12-18      초안 작성               Claude
2.0         2025-12-18      Mermaid 다이어그램,     Claude
                            UI 시안 추가



기술 스택은 별도 문서로 관리됩니다.

""",
    })

    # requests 생성 (역순으로)
    requests = []
    current_index = 1

    for part in content_parts:
        if part["type"] == "text":
            requests.append({
                "insertText": {
                    "location": {"index": current_index},
                    "text": part["text"],
                }
            })
            current_index += len(part["text"])

            # 스타일 적용
            if "style" in part:
                style = part["style"]
                text_style = {}
                if style.get("bold"):
                    text_style["bold"] = True
                if style.get("fontSize"):
                    text_style["fontSize"] = {
                        "magnitude": style["fontSize"],
                        "unit": "PT"
                    }

                if text_style:
                    requests.append({
                        "updateTextStyle": {
                            "range": {
                                "startIndex": current_index - len(part["text"]),
                                "endIndex": current_index,
                            },
                            "textStyle": text_style,
                            "fields": ",".join(text_style.keys()),
                        }
                    })

        elif part["type"] == "image":
            image_url = f"https://drive.google.com/uc?id={part['image_id']}"
            requests.append({
                "insertInlineImage": {
                    "location": {"index": current_index},
                    "uri": image_url,
                    "objectSize": {
                        "width": {"magnitude": part["width"], "unit": "PT"},
                        "height": {"magnitude": part["height"], "unit": "PT"},
                    },
                }
            })
            current_index += 1  # 이미지는 1 인덱스 차지

        elif part["type"] == "pagebreak":
            requests.append({
                "insertText": {
                    "location": {"index": current_index},
                    "text": "\n",
                }
            })
            current_index += 1
            requests.append({
                "insertPageBreak": {
                    "location": {"index": current_index},
                }
            })
            current_index += 1

    return requests


def main():
    print("=" * 60)
    print("GGP Heritage Mall PRD v2 - Google Docs")
    print("=" * 60)

    print("\n1. Authenticating...")
    creds = get_credentials()
    print("   Done")

    print("\n2. Uploading images...")
    folder_id, uploaded_images = upload_images(creds)
    print(f"   Uploaded {len(uploaded_images)} images")

    print("\n3. Creating document...")
    doc_id = create_document(creds, uploaded_images)

    print("\n" + "=" * 60)
    print("Complete!")
    print("=" * 60)
    print(f"\nDocument: https://docs.google.com/document/d/{doc_id}/edit")
    print(f"Images: https://drive.google.com/drive/folders/{folder_id}")


if __name__ == "__main__":
    main()
