"""
Google Docs PRD 문서 생성 스크립트
스크린샷을 Google Drive에 업로드하고 Google Docs 문서를 생성합니다.
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
SCREENSHOTS_DIR = Path(r"D:\AI\claude01\ggp_heritage_mall\design\screenshots")
DRIVE_FOLDER_ID = "1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW"  # Google AI Studio 폴더

# Google API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]


def get_credentials():
    """OAuth 인증 처리"""
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


def upload_images_to_drive(creds):
    """스크린샷을 Google Drive에 업로드"""
    drive_service = build("drive", "v3", credentials=creds)

    # 스크린샷 폴더 생성
    folder_metadata = {
        "name": "GGP Heritage Mall - UI Mockups",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [DRIVE_FOLDER_ID],
    }

    folder = (
        drive_service.files()
        .create(body=folder_metadata, fields="id, webViewLink")
        .execute()
    )
    folder_id = folder["id"]
    print(f"폴더 생성됨: {folder['webViewLink']}")

    # 이미지 업로드
    uploaded_images = {}
    screenshot_files = sorted(SCREENSHOTS_DIR.glob("*.png"))

    for screenshot_path in screenshot_files:
        print(f"업로드 중: {screenshot_path.name}...")

        file_metadata = {"name": screenshot_path.name, "parents": [folder_id]}

        media = MediaFileUpload(str(screenshot_path), mimetype="image/png")

        file = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink")
            .execute()
        )

        # 파일을 공개로 설정 (Google Docs에서 참조하기 위해)
        drive_service.permissions().create(
            fileId=file["id"], body={"type": "anyone", "role": "reader"}
        ).execute()

        uploaded_images[screenshot_path.stem] = file["id"]
        print(f"  업로드 완료: {file['webViewLink']}")

    return folder_id, uploaded_images


def create_google_docs(creds, uploaded_images):
    """Google Docs 문서 생성"""
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # 문서 생성
    doc_metadata = {"title": "GGP Heritage Mall - PRD 기획서 (UI 시안 포함)"}
    doc = docs_service.documents().create(body=doc_metadata).execute()
    doc_id = doc["documentId"]
    print(f"\n문서 생성됨: https://docs.google.com/document/d/{doc_id}/edit")

    # 문서를 공유 폴더로 이동
    drive_service.files().update(
        fileId=doc_id,
        addParents=DRIVE_FOLDER_ID,
        removeParents="root",
        fields="id, parents",
    ).execute()

    # 문서 내용 작성
    requests = []

    # 제목
    requests.append(
        {
            "insertText": {
                "location": {"index": 1},
                "text": "GGP Heritage Mall\nVIP 전용 헤리티지 쇼핑몰 기획서\n\n",
            }
        }
    )

    # 문서 정보
    requests.append(
        {
            "insertText": {
                "location": {"index": 1},
                "text": """Version: 1.0
Date: 2025-12-18
Status: Draft
Project Code: GGP-HM-001

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""",
            }
        }
    )

    # 1. Executive Summary
    requests.append(
        {
            "insertText": {
                "location": {"index": 1},
                "text": """1. Executive Summary

GG POKER VIP 고객을 위한 초대 전용 프리미엄 쇼핑몰입니다.

핵심 특징:
• 초대 전용: 고유 URL 링크로만 접근 가능
• 무료 증정: 결제 시스템 없이 무료 배송
• 등급별 혜택: Silver(3개) / Gold(5개) 수량 제한
• 재고 관리: 실시간 재고 추적, 품절 시 선택 불가
• 고급 디자인: 럭셔리하고 세련된 UI/UX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""",
            }
        }
    )

    # 2. 목표 사용자
    requests.append(
        {
            "insertText": {
                "location": {"index": 1},
                "text": """2. 목표 사용자

Primary Users:
┌─────────────────┬─────────────────────────────┬─────────────────────────────┐
│ 사용자          │ 설명                        │ 주요 니즈                   │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│ VIP 고객        │ GG POKER VIP 멤버           │ 간편한 제품 선택, 배송 관리 │
│ 관리자          │ GG POKER 운영팀             │ VIP 초대, 주문 처리, 재고   │
└─────────────────┴─────────────────────────────┴─────────────────────────────┘

VIP 등급 체계:
┌─────────────────┬─────────────────────────────┬─────────────────────────────┐
│ 등급            │ 선택 가능 수량              │ 설명                        │
├─────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Silver          │ 3개                         │ 기본 VIP                    │
│ Gold            │ 5개                         │ 프리미엄 VIP                │
└─────────────────┴─────────────────────────────┴─────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""",
            }
        }
    )

    # 3. 핵심 기능
    requests.append(
        {
            "insertText": {
                "location": {"index": 1},
                "text": """3. 핵심 기능

3.1 VIP 고객 기능

3.1.1 초대 링크 접근 [Critical]
• 고유 토큰이 포함된 URL로만 접근 가능
• Flow: 이메일/SNS 수신 → 고유 링크 클릭 → 자동 인증 → 쇼핑몰 진입
• URL Format: https://heritage.ggpoker.com/shop/{invite_token}

3.1.2 제품 탐색 및 선택 [Critical]
• 제품 목록 (그리드/리스트 뷰)
• 제품 상세 페이지 (이미지 갤러리, 설명, 사이즈)
• 장바구니 (선택 수량 제한 표시)
• 품절 상품 표시 (선택 불가)

3.1.3 배송 정보 관리 [Critical]
• 저장된 배송 정보 표시 (이름, 연락처, 주소)
• 배송 정보 수정 기능
• 배송 정보 확인 후 주문 확정

3.1.4 주문 확정 [Critical]
• Flow: 장바구니 확인 → 배송 정보 확인/수정 → 주문 확정 → 완료 페이지

─────────────────────────────────────────────────────────────

3.2 관리자 기능

3.2.1 VIP 초대 관리 [Critical]
• 신규 VIP 초대 (이메일 + 등급 설정)
• 초대 링크 생성 및 발송
• VIP 목록 조회/검색
• 등급 변경
• 초대 취소/재발급

3.2.2 주문/배송 관리 [Critical]
• 주문 목록 (대기/처리중/완료)
• 주문 상세 (고객 정보, 제품, 배송지)
• 배송 상태 변경 (접수 → 배송중 → 완료)
• 송장 번호 입력
• 주문 내역 Excel 다운로드

3.2.3 제품/재고 관리 [High]
• 제품 등록 (이름, 설명, 이미지, 카테고리)
• 제품 수정/삭제
• 재고 수량 설정/조정
• 재고 부족 알림

3.2.4 통계/리포트 [Medium]
• 대시보드 (오늘 주문, 전체 VIP, 재고 현황)
• 주문 현황 차트
• VIP 활동 리포트
• 인기 제품 순위

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""",
            }
        }
    )

    # UI 시안 섹션
    requests.append(
        {
            "insertText": {
                "location": {"index": 1},
                "text": """4. UI 시안

아래는 각 화면의 UI 시안입니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4.1 랜딩 페이지 (VIP 메인 화면)

• VIP 고객이 초대 링크를 통해 처음 접근하는 화면
• Hero 섹션: Heritage Collection 소개
• Featured Products: 이번 시즌 추천 제품
• 통계 섹션: VIP 멤버, 제품 수, 무료 배송, 빠른 배송 정보

[이미지: 01-landing-page.png]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4.2 제품 목록 페이지

• 전체 제품 브라우징 화면
• 상단: 선택 가능 수량 표시 (등급별)
• 필터: 카테고리별 필터링
• 제품 카드: 선택 체크박스, 사이즈 선택, 재고 표시
• 하단: 선택한 아이템 요약 및 다음 단계 버튼

[이미지: 02-product-list.png]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4.3 체크아웃 (배송 정보 확인) 페이지

• 배송 정보 확인 및 수정 화면
• Progress Steps: 상품 선택 → 배송 정보 → 주문 완료
• 저장된 정보: 기존 배송 정보 표시
• 폼: 수령인 정보, 배송지 정보, 배송 요청사항
• 주문 요약: 선택한 아이템 목록, VIP 무료 증정 표시

[이미지: 03-checkout.png]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4.4 관리자 대시보드

• 관리자용 통합 대시보드
• 통계 카드: 오늘 주문, 전체 VIP, 재고 부족, 배송 완료
• 최근 주문 테이블: 주문번호, 고객, 등급, 상품수, 상태
• 최근 활동: 실시간 활동 로그
• 재고 부족 경고: 재고가 부족한 상품 알림

[이미지: 04-admin-dashboard.png]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""",
            }
        }
    )

    # 디자인 컨셉
    requests.append(
        {
            "insertText": {
                "location": {"index": 1},
                "text": """5. 디자인 컨셉

Design Principles:
• 럭셔리: 다크 모드 기반, 골드/블랙 컬러 스키마
• 미니멀: 불필요한 요소 제거, 제품 중심
• 세련됨: 부드러운 애니메이션, 정교한 타이포그래피
• 은밀함: 브랜드 강조 최소화, 제품 경험 극대화

Color Palette:
• Primary: #D4AF37 (Gold)
• Background: #0A0A0A (Deep Black)
• Surface: #1A1A1A (Dark Gray)
• Text: #FFFFFF (White)
• Accent: #B8860B (Dark Gold)

Typography:
• Heading: Playfair Display (Serif, Elegant)
• Body: Inter (Sans-serif, Clean)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""",
            }
        }
    )

    # 문서 끝
    requests.append(
        {
            "insertText": {
                "location": {"index": 1},
                "text": """Document History:
┌─────────┬────────────┬─────────────────────────────┬─────────┐
│ 버전    │ 날짜       │ 변경 내용                   │ 작성자  │
├─────────┼────────────┼─────────────────────────────┼─────────┤
│ 1.0     │ 2025-12-18 │ 초안 작성                   │ Claude  │
└─────────┴────────────┴─────────────────────────────┴─────────┘

※ 기술 스택은 별도 문서로 관리됩니다.
※ UI 시안 이미지는 Google Drive에서 확인하실 수 있습니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
            }
        }
    )

    # 내용 순서 뒤집기 (Google Docs API는 index 1부터 삽입하므로 역순으로)
    requests.reverse()

    # 문서 업데이트
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    print(f"문서 내용 작성 완료")

    # 이미지 삽입 안내
    print("\n" + "=" * 60)
    print("이미지 삽입 안내")
    print("=" * 60)
    print(
        "\nGoogle Docs API는 텍스트 삽입만 지원합니다."
    )
    print("이미지는 수동으로 삽입해주세요:")
    print(f"\n문서 URL: https://docs.google.com/document/d/{doc_id}/edit")
    print("\n업로드된 이미지 (Drive에서 삽입 → 드라이브):")
    for name, file_id in uploaded_images.items():
        print(f"  - {name}: https://drive.google.com/file/d/{file_id}/view")

    return doc_id


def main():
    print("=" * 60)
    print("GGP Heritage Mall - Google Docs PRD 생성")
    print("=" * 60)

    # 인증
    print("\n1. Google 인증 중...")
    creds = get_credentials()
    print("   인증 완료")

    # 이미지 업로드
    print("\n2. 스크린샷 업로드 중...")
    folder_id, uploaded_images = upload_images_to_drive(creds)

    # 문서 생성
    print("\n3. Google Docs 문서 생성 중...")
    doc_id = create_google_docs(creds, uploaded_images)

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)
    print(f"\n문서 URL: https://docs.google.com/document/d/{doc_id}/edit")
    print(
        f"이미지 폴더: https://drive.google.com/drive/folders/{folder_id}"
    )


if __name__ == "__main__":
    main()
