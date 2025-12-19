"""
GGP Heritage Mall PRD v3 - Google Docs 최적화 버전
네이티브 테이블, A4 레이아웃, 이미지 중앙 정렬
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

# A4 사이즈 (pt) - 1pt = 1/72 inch
A4_WIDTH_PT = 595.0
A4_HEIGHT_PT = 842.0
MARGIN_PT = 72.0
CONTENT_WIDTH_PT = 451.0  # 본문 너비
MAX_IMAGE_HEIGHT_PT = 550.0  # 이미지 최대 높이 (페이지 내 유지)

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
    """이미지를 Google Drive에 업로드"""
    drive_service = build("drive", "v3", credentials=creds)

    # 폴더 생성
    folder_metadata = {
        "name": "GGP Heritage Mall PRD v3",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [DRIVE_FOLDER_ID],
    }
    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    folder_id = folder["id"]
    print(f"  Folder created: {folder_id}")

    uploaded = {}

    # 다이어그램 업로드
    for png_file in sorted(DIAGRAMS_DIR.glob("*.png")):
        print(f"    Uploading: {png_file.name}")
        file_metadata = {"name": png_file.name, "parents": [folder_id]}
        media = MediaFileUpload(str(png_file), mimetype="image/png")
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        drive_service.permissions().create(
            fileId=file["id"], body={"type": "anyone", "role": "reader"}
        ).execute()
        uploaded[f"diagram_{png_file.stem}"] = file["id"]

    # 스크린샷 업로드
    for png_file in sorted(SCREENSHOTS_DIR.glob("*.png")):
        print(f"    Uploading: {png_file.name}")
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


class GoogleDocsBuilder:
    """Google Docs 문서 빌더"""

    def __init__(self, docs_service, doc_id):
        self.docs_service = docs_service
        self.doc_id = doc_id
        self.requests = []
        self.current_index = 1

    def add_text(self, text, bold=False, font_size=None, center=False):
        """텍스트 추가"""
        self.requests.append({
            "insertText": {
                "location": {"index": self.current_index},
                "text": text,
            }
        })

        end_index = self.current_index + len(text)

        # 스타일 적용
        text_style = {}
        if bold:
            text_style["bold"] = True
        if font_size:
            text_style["fontSize"] = {"magnitude": font_size, "unit": "PT"}

        if text_style:
            self.requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": self.current_index, "endIndex": end_index},
                    "textStyle": text_style,
                    "fields": ",".join(text_style.keys()),
                }
            })

        # 중앙 정렬
        if center:
            self.requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": self.current_index, "endIndex": end_index},
                    "paragraphStyle": {"alignment": "CENTER"},
                    "fields": "alignment",
                }
            })

        self.current_index = end_index

    def add_heading(self, text, level=1):
        """제목 추가"""
        font_sizes = {1: 24, 2: 18, 3: 14}
        self.add_text(text + "\n\n", bold=True, font_size=font_sizes.get(level, 14))

    def add_paragraph(self, text):
        """본문 추가"""
        self.add_text(text + "\n\n", font_size=11)

    def add_image(self, image_id, width=CONTENT_WIDTH_PT, height=None, center=True):
        """이미지 추가"""
        image_url = f"https://drive.google.com/uc?id={image_id}"

        # 높이가 지정되지 않으면 16:9 비율 사용
        if height is None:
            height = width * 0.6

        # 최대 높이 제한
        if height > MAX_IMAGE_HEIGHT_PT:
            ratio = MAX_IMAGE_HEIGHT_PT / height
            height = MAX_IMAGE_HEIGHT_PT
            width = width * ratio

        self.requests.append({
            "insertInlineImage": {
                "location": {"index": self.current_index},
                "uri": image_url,
                "objectSize": {
                    "width": {"magnitude": width, "unit": "PT"},
                    "height": {"magnitude": height, "unit": "PT"},
                },
            }
        })

        # 이미지는 1 인덱스 차지
        image_index = self.current_index
        self.current_index += 1

        # 줄바꿈 추가
        self.add_text("\n\n")

        # 중앙 정렬 (나중에 적용)
        if center:
            self.requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": image_index, "endIndex": image_index + 1},
                    "paragraphStyle": {"alignment": "CENTER"},
                    "fields": "alignment",
                }
            })

    def add_table(self, headers, rows):
        """네이티브 테이블 추가"""
        num_rows = len(rows) + 1  # 헤더 포함
        num_cols = len(headers)

        # 테이블 삽입
        self.requests.append({
            "insertTable": {
                "location": {"index": self.current_index},
                "rows": num_rows,
                "columns": num_cols,
            }
        })

        # 테이블 삽입 후 인덱스 계산
        # 테이블 구조: table -> tableRow -> tableCell -> paragraph -> text
        # 각 셀은 최소 2개의 인덱스를 차지 (셀 시작, 단락)
        table_start = self.current_index

        # 테이블 내용은 별도로 업데이트해야 함
        # Google Docs API의 한계로 테이블 생성 후 내용을 채워야 함
        # 여기서는 간단히 테이블 구조만 생성

        # 테이블 크기 계산 (대략적)
        # 각 행: 2 + (cols * 4)
        table_size = 2 + num_rows * (2 + num_cols * 4)
        self.current_index += table_size

        # 줄바꿈
        self.add_text("\n")

    def add_simple_table(self, data):
        """간단한 텍스트 테이블 (정렬된 형태)"""
        # 열 너비 계산
        if not data:
            return

        num_cols = len(data[0])
        col_widths = [0] * num_cols

        for row in data:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # 테이블 텍스트 생성
        lines = []
        for row in data:
            line = "  ".join(
                str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
            )
            lines.append(line)

        table_text = "\n".join(lines) + "\n\n"
        self.add_text(table_text, font_size=10)

    def add_page_break(self):
        """페이지 나눔"""
        self.requests.append({
            "insertPageBreak": {
                "location": {"index": self.current_index},
            }
        })
        self.current_index += 1

    def add_horizontal_line(self):
        """구분선"""
        self.add_text("─" * 60 + "\n\n", font_size=10)

    def execute(self):
        """문서 업데이트 실행"""
        if self.requests:
            self.docs_service.documents().batchUpdate(
                documentId=self.doc_id, body={"requests": self.requests}
            ).execute()


def create_document(creds, uploaded_images):
    """Google Docs 문서 생성"""
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # 문서 생성
    doc = docs_service.documents().create(
        body={"title": "GGP Heritage Mall - PRD 기획서"}
    ).execute()
    doc_id = doc["documentId"]
    print(f"  Document created: {doc_id}")

    # 폴더로 이동
    drive_service.files().update(
        fileId=doc_id,
        addParents=DRIVE_FOLDER_ID,
        removeParents="root",
    ).execute()

    # 문서 빌더
    builder = GoogleDocsBuilder(docs_service, doc_id)

    # === 표지 ===
    builder.add_text("\n\n\n\n\n\n", font_size=11)
    builder.add_text("GGP Heritage Mall\n", bold=True, font_size=36, center=True)
    builder.add_text("VIP 전용 헤리티지 쇼핑몰 기획서\n\n", font_size=18, center=True)
    builder.add_text("Version 2.0\n", font_size=14, center=True)
    builder.add_text("2025년 12월 18일\n", font_size=14, center=True)
    builder.add_text("\n\n\n\n\n\n\n", font_size=11)

    # === 1. Executive Summary ===
    builder.add_page_break()
    builder.add_heading("1. Executive Summary", 1)
    builder.add_paragraph(
        "GG POKER VIP 고객을 위한 초대 전용 프리미엄 쇼핑몰입니다."
    )

    builder.add_heading("핵심 특징", 3)
    builder.add_simple_table([
        ["특징", "설명"],
        ["초대 전용", "고유 URL 링크로만 접근 가능"],
        ["무료 증정", "결제 시스템 없이 무료 배송"],
        ["등급별 혜택", "Silver(3개) / Gold(5개) 수량 제한"],
        ["재고 관리", "실시간 재고 추적, 품절 시 선택 불가"],
        ["고급 디자인", "럭셔리하고 세련된 UI/UX"],
    ])

    # === 2. 목표 사용자 ===
    builder.add_page_break()
    builder.add_heading("2. 목표 사용자", 1)

    builder.add_heading("2.1 Primary Users", 2)
    builder.add_simple_table([
        ["사용자", "설명", "주요 니즈"],
        ["VIP 고객", "GG POKER VIP 멤버", "간편한 제품 선택, 배송 정보 관리"],
        ["관리자", "GG POKER 운영팀", "VIP 초대, 주문 처리, 재고 관리"],
    ])

    builder.add_heading("2.2 VIP 등급 체계", 2)
    if "diagram_04-vip-tier" in uploaded_images:
        builder.add_image(uploaded_images["diagram_04-vip-tier"], height=200)

    builder.add_simple_table([
        ["등급", "선택 가능 수량", "설명"],
        ["Silver", "3개", "기본 VIP"],
        ["Gold", "5개", "프리미엄 VIP"],
    ])

    # === 3. 핵심 기능 ===
    builder.add_page_break()
    builder.add_heading("3. 핵심 기능", 1)

    builder.add_heading("3.1 VIP 고객 플로우", 2)
    if "diagram_01-vip-user-flow" in uploaded_images:
        builder.add_image(uploaded_images["diagram_01-vip-user-flow"], height=400)

    builder.add_paragraph(
        "초대 링크 접근 (Critical)\n"
        "    고유 토큰이 포함된 URL로만 접근 가능\n"
        "    URL: https://heritage.ggpoker.com/shop/{invite_token}\n\n"
        "제품 탐색 및 선택 (Critical)\n"
        "    제품 목록, 상세 페이지, 장바구니, 품절 표시\n\n"
        "배송 정보 관리 (Critical)\n"
        "    저장된 배송 정보 표시 및 수정 기능\n\n"
        "주문 확정 (Critical)\n"
        "    장바구니 확인 → 배송 정보 확인 → 주문 확정"
    )

    # === 3.2 관리자 플로우 ===
    builder.add_page_break()
    builder.add_heading("3.2 관리자 플로우", 2)
    if "diagram_05-admin-flow" in uploaded_images:
        builder.add_image(uploaded_images["diagram_05-admin-flow"], height=380)

    builder.add_paragraph(
        "VIP 초대 관리 (Critical)\n"
        "    신규 VIP 초대, 링크 발송, 등급 변경, 초대 취소\n\n"
        "주문/배송 관리 (Critical)\n"
        "    주문 목록, 배송 상태 변경, 송장 입력, Excel 다운로드\n\n"
        "제품/재고 관리 (High)\n"
        "    제품 등록/수정, 재고 조정, 부족 알림\n\n"
        "통계/리포트 (Medium)\n"
        "    대시보드, 주문 현황 차트, VIP 활동 리포트"
    )

    # === 3.3 주문 상태 흐름 ===
    builder.add_page_break()
    builder.add_heading("3.3 주문 상태 흐름", 2)
    if "diagram_02-order-state" in uploaded_images:
        builder.add_image(uploaded_images["diagram_02-order-state"], height=280)

    builder.add_simple_table([
        ["상태", "설명", "다음 상태"],
        ["Pending", "주문 접수, 검토 대기", "Processing, Cancelled"],
        ["Processing", "상품 준비, 포장 중", "Shipped, Cancelled"],
        ["Shipped", "배송 중, 배송 출발", "Delivered"],
        ["Delivered", "배송 완료", "-"],
        ["Cancelled", "주문 취소", "-"],
    ])

    # === 4. 시스템 아키텍처 ===
    builder.add_page_break()
    builder.add_heading("4. 시스템 아키텍처", 1)
    if "diagram_03-system-architecture" in uploaded_images:
        builder.add_image(uploaded_images["diagram_03-system-architecture"], height=350)

    builder.add_simple_table([
        ["계층", "기술"],
        ["Frontend", "Next.js 15, Tailwind CSS, Framer Motion"],
        ["Backend", "Supabase (PostgreSQL, Auth, Storage)"],
        ["Email", "Resend"],
        ["Hosting", "Vercel + Supabase"],
    ])

    # === 5. 화면 구조 ===
    builder.add_page_break()
    builder.add_heading("5. 화면 구조", 1)
    if "diagram_06-screen-map" in uploaded_images:
        builder.add_image(uploaded_images["diagram_06-screen-map"], height=420)

    builder.add_heading("5.1 VIP 고객 화면", 3)
    builder.add_simple_table([
        ["화면", "경로", "설명"],
        ["랜딩/인증", "/shop/{token}", "초대 토큰 확인"],
        ["메인", "/", "히어로, 제품 하이라이트"],
        ["제품 목록", "/products", "제품 그리드, 필터링"],
        ["장바구니", "/cart", "선택 제품, 수량 제한"],
        ["배송 정보", "/checkout", "배송지 확인/수정"],
        ["주문 완료", "/order-complete", "주문 확인 메시지"],
    ])

    builder.add_heading("5.2 관리자 화면", 3)
    builder.add_simple_table([
        ["화면", "경로", "설명"],
        ["대시보드", "/admin", "통계 요약, 최근 주문"],
        ["VIP 관리", "/admin/vips", "VIP 목록, 초대 발급"],
        ["주문 관리", "/admin/orders", "주문 목록, 상태 필터"],
        ["제품 관리", "/admin/products", "제품 목록, 재고 현황"],
        ["통계", "/admin/stats", "차트, 리포트"],
    ])

    # === 6. UI 시안 ===
    builder.add_page_break()
    builder.add_heading("6. UI 시안", 1)

    builder.add_heading("6.1 랜딩 페이지", 2)
    builder.add_paragraph(
        "VIP 고객이 초대 링크를 통해 처음 접근하는 화면입니다.\n"
        "Hero 섹션, Featured Products, 통계 섹션으로 구성됩니다."
    )
    if "screenshot_01-landing-page" in uploaded_images:
        builder.add_image(uploaded_images["screenshot_01-landing-page"], height=MAX_IMAGE_HEIGHT_PT)

    builder.add_page_break()
    builder.add_heading("6.2 제품 목록 페이지", 2)
    builder.add_paragraph(
        "전체 제품을 브라우징하는 화면입니다.\n"
        "선택 가능 수량 표시, 카테고리 필터, 사이즈 선택, 재고 표시 기능을 제공합니다."
    )
    if "screenshot_02-product-list" in uploaded_images:
        builder.add_image(uploaded_images["screenshot_02-product-list"], height=MAX_IMAGE_HEIGHT_PT)

    builder.add_page_break()
    builder.add_heading("6.3 체크아웃", 2)
    builder.add_paragraph(
        "배송 정보를 확인하고 수정하는 화면입니다.\n"
        "Progress Steps, 저장된 정보, 수령인/배송지 폼, 주문 요약을 표시합니다."
    )
    if "screenshot_03-checkout" in uploaded_images:
        builder.add_image(uploaded_images["screenshot_03-checkout"], height=MAX_IMAGE_HEIGHT_PT)

    builder.add_page_break()
    builder.add_heading("6.4 관리자 대시보드", 2)
    builder.add_paragraph(
        "관리자용 통합 대시보드입니다.\n"
        "통계 카드, 최근 주문 테이블, 활동 로그, 재고 부족 경고를 제공합니다."
    )
    if "screenshot_04-admin-dashboard" in uploaded_images:
        builder.add_image(uploaded_images["screenshot_04-admin-dashboard"], height=MAX_IMAGE_HEIGHT_PT)

    # === 7. 디자인 컨셉 ===
    builder.add_page_break()
    builder.add_heading("7. 디자인 컨셉", 1)

    builder.add_heading("Design Principles", 3)
    builder.add_simple_table([
        ["원칙", "설명"],
        ["럭셔리", "다크 모드 기반, 골드/블랙 컬러 스키마"],
        ["미니멀", "불필요한 요소 제거, 제품 중심"],
        ["세련됨", "부드러운 애니메이션, 정교한 타이포그래피"],
        ["은밀함", "브랜드 강조 최소화, 제품 경험 극대화"],
    ])

    builder.add_heading("Color Palette", 3)
    builder.add_simple_table([
        ["색상", "코드", "용도"],
        ["Primary", "#D4AF37", "Gold (강조)"],
        ["Background", "#0A0A0A", "Deep Black (배경)"],
        ["Surface", "#1A1A1A", "Dark Gray (카드)"],
        ["Text", "#FFFFFF", "White (텍스트)"],
        ["Accent", "#B8860B", "Dark Gold (보조)"],
    ])

    builder.add_heading("Typography", 3)
    builder.add_simple_table([
        ["용도", "폰트", "스타일"],
        ["Heading", "Playfair Display", "Serif, Elegant"],
        ["Body", "Inter", "Sans-serif, Clean"],
    ])

    # === 8. 보안 요구사항 ===
    builder.add_page_break()
    builder.add_heading("8. 보안 요구사항", 1)

    builder.add_heading("인증/권한", 3)
    builder.add_simple_table([
        ["영역", "방식", "설명"],
        ["VIP 접근", "Magic Link", "고유 초대 토큰으로만 접근"],
        ["관리자", "Email + Password", "Supabase Auth"],
        ["API 보안", "Row Level Security", "Supabase RLS 정책"],
        ["토큰 만료", "30일", "만료 시 재발급 필요"],
    ])

    builder.add_heading("데이터 보호", 3)
    builder.add_paragraph(
        "    개인정보 암호화 (이름, 연락처, 주소)\n"
        "    HTTPS 강제\n"
        "    SQL Injection 방지 (Supabase ORM)\n"
        "    XSS 방지 (React 자동 이스케이프)"
    )

    # === 9. 성공 지표 ===
    builder.add_page_break()
    builder.add_heading("9. 성공 지표 (KPIs)", 1)
    builder.add_simple_table([
        ["지표", "목표", "측정 방법"],
        ["주문 완료율", "85%+", "방문 VIP 중 주문 완료 비율"],
        ["페이지 로드", "< 2초", "Lighthouse, Core Web Vitals"],
        ["관리 효율", "주문당 5분", "주문 처리 시간"],
        ["시스템 가용성", "99.9%", "Vercel/Supabase 모니터링"],
    ])

    # === 10. 리스크 및 대응 ===
    builder.add_heading("10. 리스크 및 대응", 1)
    builder.add_simple_table([
        ["리스크", "확률", "영향", "대응"],
        ["토큰 유출", "중", "고", "1인 1토큰, IP 추적"],
        ["트래픽 급증", "저", "중", "Vercel Edge 스케일링"],
        ["이미지 지연", "중", "중", "CDN, 레이지 로딩"],
        ["재고 동시성", "중", "고", "Supabase 트랜잭션"],
    ])

    # === Document History ===
    builder.add_page_break()
    builder.add_heading("Document History", 1)
    builder.add_simple_table([
        ["버전", "날짜", "변경 내용", "작성자"],
        ["1.0", "2025-12-18", "초안 작성", "Claude"],
        ["2.0", "2025-12-18", "다이어그램, UI 시안 추가", "Claude"],
    ])

    builder.add_paragraph("\n\n기술 스택 상세는 별도 문서로 관리됩니다.")

    # 실행
    builder.execute()

    return doc_id


def main():
    print("=" * 60)
    print("GGP Heritage Mall PRD v3 - Google Docs Optimized")
    print("=" * 60)

    print("\n[1/3] Authenticating...")
    creds = get_credentials()
    print("  Done")

    print("\n[2/3] Uploading images...")
    folder_id, uploaded_images = upload_images(creds)
    print(f"  Uploaded {len(uploaded_images)} images")

    print("\n[3/3] Creating document...")
    doc_id = create_document(creds, uploaded_images)

    print("\n" + "=" * 60)
    print("Complete!")
    print("=" * 60)
    print(f"\nDocument: https://docs.google.com/document/d/{doc_id}/edit")
    print(f"Images: https://drive.google.com/drive/folders/{folder_id}")


if __name__ == "__main__":
    main()
