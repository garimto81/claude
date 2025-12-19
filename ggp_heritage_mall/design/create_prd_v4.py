"""
GGP Heritage Mall PRD v4 - Native Google Docs Tables with Styling
골드/블랙 테마의 네이티브 테이블 적용
"""
import os
import time
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
CONTENT_WIDTH_PT = 451.0
MAX_IMAGE_HEIGHT_PT = 650.0     # 다이어그램이 더 크게 보이도록

# 이미지 크기 표준화 (cm to pt: 1cm = 28.35pt)
WIDTH_18CM = 451        # 18cm (max A4 content width)
WIDTH_14CM = 397        # 14cm
WIDTH_12CM = 340        # 12cm
WIDTH_10CM = 284        # 10cm
WIDTH_8CM = 227         # 8cm
SCREENSHOT_HEIGHT = 550 # UI 스크린샷 (높이 기준)

# 폰트 크기 표준화 (16pt 기준)
FONT_TITLE = 32
FONT_SUBTITLE = 18
FONT_H1 = 24
FONT_H2 = 20
FONT_H3 = 16
FONT_BODY = 16
FONT_TABLE = 16

# 색상 테마 (RGB 0-1)
GOLD = {"red": 0.831, "green": 0.686, "blue": 0.216}  # #D4AF37
DARK_GOLD = {"red": 0.722, "green": 0.525, "blue": 0.043}  # #B88617
BLACK = {"red": 0.039, "green": 0.039, "blue": 0.039}  # #0A0A0A
DARK_GRAY = {"red": 0.102, "green": 0.102, "blue": 0.102}  # #1A1A1A
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}

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

    folder_metadata = {
        "name": "GGP Heritage Mall PRD v4",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [DRIVE_FOLDER_ID],
    }
    folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    folder_id = folder["id"]
    print(f"  Folder created: {folder_id}")

    uploaded = {}

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


class StyledDocsBuilder:
    """스타일이 적용된 Google Docs 빌더"""

    def __init__(self, docs_service, doc_id):
        self.docs_service = docs_service
        self.doc_id = doc_id
        self.current_index = 1

    def _execute(self, requests, delay=1.2):
        """요청 실행 (API Rate limit 대응)"""
        if requests:
            self.docs_service.documents().batchUpdate(
                documentId=self.doc_id, body={"requests": requests}
            ).execute()
            time.sleep(delay)  # Rate limit: 60 requests/min

    def _get_doc(self):
        """현재 문서 상태 조회"""
        return self.docs_service.documents().get(documentId=self.doc_id).execute()

    def _refresh_index(self):
        """문서 끝 인덱스 갱신"""
        doc = self._get_doc()
        content = doc.get("body", {}).get("content", [])
        if content:
            self.current_index = content[-1].get("endIndex", 1) - 1
        return self.current_index

    def add_text(self, text, bold=False, font_size=None, center=False, color=None):
        """텍스트 추가"""
        self._refresh_index()
        requests = []

        requests.append({
            "insertText": {
                "location": {"index": self.current_index},
                "text": text,
            }
        })

        end_index = self.current_index + len(text)

        # 텍스트 스타일
        text_style = {}
        fields = []

        if bold:
            text_style["bold"] = True
            fields.append("bold")
        if font_size:
            text_style["fontSize"] = {"magnitude": font_size, "unit": "PT"}
            fields.append("fontSize")
        if color:
            text_style["foregroundColor"] = {"color": {"rgbColor": color}}
            fields.append("foregroundColor")

        if text_style:
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": self.current_index, "endIndex": end_index},
                    "textStyle": text_style,
                    "fields": ",".join(fields),
                }
            })

        if center:
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": self.current_index, "endIndex": end_index},
                    "paragraphStyle": {"alignment": "CENTER"},
                    "fields": "alignment",
                }
            })

        self._execute(requests)
        self.current_index = end_index

    def add_heading(self, text, level=1):
        """제목 추가"""
        font_sizes = {1: FONT_H1, 2: FONT_H2, 3: FONT_H3}
        self.add_text(text + "\n\n", bold=True, font_size=font_sizes.get(level, FONT_H3), color=GOLD)

    def add_paragraph(self, text):
        """본문 추가"""
        self.add_text(text + "\n\n", font_size=FONT_BODY)

    def add_page_break(self):
        """페이지 나눔"""
        self._refresh_index()
        requests = [{
            "insertPageBreak": {
                "location": {"index": self.current_index},
            }
        }]
        self._execute(requests)
        self.current_index += 1

    def add_image(self, image_id, width=CONTENT_WIDTH_PT, height=None, center=True):
        """이미지 추가 (최대 크기 제한 적용)"""
        self._refresh_index()

        image_url = f"https://drive.google.com/uc?id={image_id}"

        # 최대 크기 제한 적용
        final_width = width if width is not None else CONTENT_WIDTH_PT
        final_height = height

        # 너비가 본문 너비를 초과하면 축소
        if final_width > CONTENT_WIDTH_PT:
            ratio = CONTENT_WIDTH_PT / final_width
            final_width = CONTENT_WIDTH_PT
            if final_height is not None:
                final_height = final_height * ratio

        # 높이가 최대 높이를 초과하면 축소
        if final_height is not None and final_height > MAX_IMAGE_HEIGHT_PT:
            ratio = MAX_IMAGE_HEIGHT_PT / final_height
            final_height = MAX_IMAGE_HEIGHT_PT
            final_width = final_width * ratio

        # objectSize 구성
        object_size = {"width": {"magnitude": final_width, "unit": "PT"}}
        if final_height is not None:
            object_size["height"] = {"magnitude": final_height, "unit": "PT"}

        requests = [{
            "insertInlineImage": {
                "location": {"index": self.current_index},
                "uri": image_url,
                "objectSize": object_size,
            }
        }]

        self._execute(requests)
        image_index = self.current_index

        # 줄바꿈
        self._refresh_index()
        self._execute([{
            "insertText": {
                "location": {"index": self.current_index},
                "text": "\n\n",
            }
        }])

        # 중앙 정렬
        if center:
            self._execute([{
                "updateParagraphStyle": {
                    "range": {"startIndex": image_index, "endIndex": image_index + 1},
                    "paragraphStyle": {"alignment": "CENTER"},
                    "fields": "alignment",
                }
            }])

    def add_styled_table(self, headers, rows):
        """스타일이 적용된 네이티브 테이블 추가"""
        self._refresh_index()

        num_rows = len(rows) + 1
        num_cols = len(headers)

        # 1. 테이블 삽입
        requests = [{
            "insertTable": {
                "location": {"index": self.current_index},
                "rows": num_rows,
                "columns": num_cols,
            }
        }]
        self._execute(requests)

        # 2. 문서에서 테이블 찾기
        doc = self._get_doc()
        table = self._find_last_table(doc)

        if not table:
            print("    Warning: Table not found")
            return

        # 3. 테이블 시작 인덱스 가져오기
        table_start_idx = table.get("_startIndex", 0)

        # 4. 셀 배경색 스타일 먼저 적용 (인덱스 변경 없음)
        style_requests = []
        table_rows = table.get("tableRows", [])

        for row_idx, table_row in enumerate(table_rows):
            cells = table_row.get("tableCells", [])

            for col_idx, cell in enumerate(cells):
                is_header = (row_idx == 0)

                if is_header:
                    style_requests.append({
                        "updateTableCellStyle": {
                            "tableRange": {
                                "tableCellLocation": {
                                    "tableStartLocation": {"index": table_start_idx},
                                    "rowIndex": row_idx,
                                    "columnIndex": col_idx,
                                },
                                "rowSpan": 1,
                                "columnSpan": 1,
                            },
                            "tableCellStyle": {
                                "backgroundColor": {"color": {"rgbColor": DARK_GOLD}},
                                "paddingTop": {"magnitude": 5, "unit": "PT"},
                                "paddingBottom": {"magnitude": 5, "unit": "PT"},
                                "paddingLeft": {"magnitude": 8, "unit": "PT"},
                                "paddingRight": {"magnitude": 8, "unit": "PT"},
                            },
                            "fields": "backgroundColor,paddingTop,paddingBottom,paddingLeft,paddingRight",
                        }
                    })
                else:
                    bg_color = DARK_GRAY if row_idx % 2 == 1 else {"red": 0.15, "green": 0.15, "blue": 0.15}
                    style_requests.append({
                        "updateTableCellStyle": {
                            "tableRange": {
                                "tableCellLocation": {
                                    "tableStartLocation": {"index": table_start_idx},
                                    "rowIndex": row_idx,
                                    "columnIndex": col_idx,
                                },
                                "rowSpan": 1,
                                "columnSpan": 1,
                            },
                            "tableCellStyle": {
                                "backgroundColor": {"color": {"rgbColor": bg_color}},
                                "paddingTop": {"magnitude": 4, "unit": "PT"},
                                "paddingBottom": {"magnitude": 4, "unit": "PT"},
                                "paddingLeft": {"magnitude": 8, "unit": "PT"},
                                "paddingRight": {"magnitude": 8, "unit": "PT"},
                            },
                            "fields": "backgroundColor,paddingTop,paddingBottom,paddingLeft,paddingRight",
                        }
                    })

        self._execute(style_requests)

        # 5. 텍스트 삽입 (역순으로 - 인덱스 변경 방지)
        all_cells = []
        for row_idx, table_row in enumerate(table_rows):
            cells = table_row.get("tableCells", [])
            for col_idx, cell in enumerate(cells):
                if row_idx == 0:
                    cell_text = headers[col_idx]
                else:
                    cell_text = rows[row_idx - 1][col_idx] if col_idx < len(rows[row_idx - 1]) else ""

                cell_content = cell.get("content", [])
                if cell_content:
                    paragraph = cell_content[0]
                    start_index = paragraph.get("startIndex", 0)
                    all_cells.append((start_index, str(cell_text), row_idx))

        # 역순 정렬 (뒤에서부터 삽입하면 앞의 인덱스가 변하지 않음)
        all_cells.sort(key=lambda x: x[0], reverse=True)

        # 배치 요청으로 통합 (역순으로 정렬된 상태로 한 번에 전송)
        batch_requests = []
        for start_index, cell_text, row_idx in all_cells:
            if cell_text:
                batch_requests.append({
                    "insertText": {
                        "location": {"index": start_index},
                        "text": cell_text,
                    }
                })

                # 헤더 텍스트 스타일 (볼드 + 흰색)
                if row_idx == 0:
                    batch_requests.append({
                        "updateTextStyle": {
                            "range": {
                                "startIndex": start_index,
                                "endIndex": start_index + len(cell_text),
                            },
                            "textStyle": {
                                "bold": True,
                                "foregroundColor": {"color": {"rgbColor": WHITE}},
                                "fontSize": {"magnitude": FONT_TABLE, "unit": "PT"},
                            },
                            "fields": "bold,foregroundColor,fontSize",
                        }
                    })
                else:
                    # 본문 텍스트도 흰색으로 (어두운 배경에서 보이도록)
                    batch_requests.append({
                        "updateTextStyle": {
                            "range": {
                                "startIndex": start_index,
                                "endIndex": start_index + len(cell_text),
                            },
                            "textStyle": {
                                "foregroundColor": {"color": {"rgbColor": WHITE}},
                                "fontSize": {"magnitude": FONT_TABLE, "unit": "PT"},
                            },
                            "fields": "foregroundColor,fontSize",
                        }
                    })

        if batch_requests:
            self._execute(batch_requests)

        # 6. 줄바꿈 추가
        self._refresh_index()
        self._execute([{
            "insertText": {
                "location": {"index": self.current_index},
                "text": "\n",
            }
        }])

    def _find_last_table(self, doc):
        """문서에서 마지막 테이블 찾기 (startIndex 포함)"""
        content = doc.get("body", {}).get("content", [])
        tables = [elem for elem in content if "table" in elem]
        if tables:
            last_table_elem = tables[-1]
            table = last_table_elem.get("table")
            # 테이블 요소의 startIndex를 table 객체에 추가
            table["_startIndex"] = last_table_elem.get("startIndex", 0)
            return table
        return None


def create_document(creds, uploaded_images):
    """Google Docs 문서 생성"""
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # 문서 생성
    doc = docs_service.documents().create(
        body={"title": "GGP Heritage Mall - PRD v4 (Styled)"}
    ).execute()
    doc_id = doc["documentId"]
    print(f"  Document created: {doc_id}")

    # 폴더로 이동
    drive_service.files().update(
        fileId=doc_id,
        addParents=DRIVE_FOLDER_ID,
        removeParents="root",
    ).execute()

    # 빌더
    builder = StyledDocsBuilder(docs_service, doc_id)

    # === 표지 ===
    builder.add_text("\n\n\n\n\n\n", font_size=FONT_BODY)
    builder.add_text("GGP Heritage Mall\n", bold=True, font_size=FONT_TITLE, center=True, color=GOLD)
    builder.add_text("VIP 전용 헤리티지 쇼핑몰 기획서\n\n", font_size=FONT_SUBTITLE, center=True)
    builder.add_text("Version 2.0\n", font_size=FONT_H3, center=True)
    builder.add_text("2025년 12월 18일\n", font_size=FONT_H3, center=True)

    # === 1. Executive Summary ===
    builder.add_page_break()
    builder.add_heading("1. Executive Summary", 1)
    builder.add_paragraph("GG POKER VIP 고객을 위한 초대 전용 프리미엄 쇼핑몰입니다.")

    builder.add_heading("핵심 특징", 3)
    builder.add_styled_table(
        headers=["특징", "설명"],
        rows=[
            ["초대 전용", "고유 URL 링크로만 접근 가능"],
            ["무료 증정", "결제 시스템 없이 무료 배송"],
            ["등급별 혜택", "Silver(3개) / Gold(5개) 수량 제한"],
            ["재고 관리", "실시간 재고 추적, 품절 시 선택 불가"],
            ["고급 디자인", "럭셔리하고 세련된 UI/UX"],
        ]
    )

    # === 2. 목표 사용자 ===
    builder.add_page_break()
    builder.add_heading("2. 목표 사용자", 1)

    builder.add_heading("2.1 Primary Users", 2)
    builder.add_styled_table(
        headers=["사용자", "설명", "주요 니즈"],
        rows=[
            ["VIP 고객", "GG POKER VIP 멤버", "간편한 제품 선택, 배송 정보 관리"],
            ["관리자", "GG POKER 운영팀", "VIP 초대, 주문 처리, 재고 관리"],
        ]
    )

    builder.add_heading("2.2 VIP 등급 체계", 2)
    if "diagram_04-vip-tier" in uploaded_images:
        builder.add_image(uploaded_images["diagram_04-vip-tier"], width=WIDTH_14CM)

    builder.add_styled_table(
        headers=["Tier", "Order Limit"],
        rows=[
            ["Silver", "3 Items"],
            ["Gold", "5 Items"],
        ]
    )

    # === 3. 핵심 기능 ===
    builder.add_page_break()
    builder.add_heading("3. 핵심 기능", 1)

    builder.add_heading("3.1 VIP 고객 플로우", 2)
    if "diagram_01-vip-user-flow" in uploaded_images:
        builder.add_image(uploaded_images["diagram_01-vip-user-flow"], width=WIDTH_10CM)

    builder.add_styled_table(
        headers=["기능", "우선순위", "설명"],
        rows=[
            ["초대 링크 접근", "Critical", "고유 토큰 URL로만 접근"],
            ["제품 탐색/선택", "Critical", "목록, 상세, 장바구니, 품절 표시"],
            ["배송 정보 관리", "Critical", "저장된 배송 정보 표시/수정"],
            ["주문 확정", "Critical", "확인 후 주문 완료"],
        ]
    )

    # === 3.2 관리자 플로우 ===
    builder.add_page_break()
    builder.add_heading("3.2 관리자 플로우", 2)
    if "diagram_05-admin-flow" in uploaded_images:
        builder.add_image(uploaded_images["diagram_05-admin-flow"], width=WIDTH_10CM)

    builder.add_styled_table(
        headers=["기능", "우선순위", "설명"],
        rows=[
            ["VIP 초대 관리", "Critical", "초대, 링크 발송, 등급 변경"],
            ["주문/배송 관리", "Critical", "목록, 상태 변경, 송장 입력"],
            ["제품/재고 관리", "High", "등록/수정, 재고 조정"],
            ["통계/리포트", "Medium", "대시보드, 차트, 활동 리포트"],
        ]
    )

    # === 3.3 주문 상태 흐름 ===
    builder.add_page_break()
    builder.add_heading("3.3 주문 상태 흐름", 2)
    if "diagram_02-order-state" in uploaded_images:
        builder.add_image(uploaded_images["diagram_02-order-state"], width=WIDTH_14CM)

    builder.add_styled_table(
        headers=["Status", "Description", "Next Status"],
        rows=[
            ["Pending", "Order received, awaiting review", "Processing, Cancelled"],
            ["Processing", "Preparing items, hand over to carrier", "Shipped, Cancelled"],
            ["Shipped", "In transit (DHL, FedEx, etc.)", "Delivered"],
            ["Delivered", "Delivery complete", "-"],
            ["Cancelled", "Order cancelled", "-"],
        ]
    )

    builder.add_heading("Carrier Information", 3)
    builder.add_paragraph("When shipping starts, tracking number and carrier information (DHL, FedEx, etc.) are provided to customers.")

    # === 4. 시스템 아키텍처 ===
    builder.add_page_break()
    builder.add_heading("4. 시스템 아키텍처", 1)
    if "diagram_03-system-architecture" in uploaded_images:
        builder.add_image(uploaded_images["diagram_03-system-architecture"], width=WIDTH_18CM)

    builder.add_styled_table(
        headers=["계층", "기술"],
        rows=[
            ["Frontend", "Next.js 15, Tailwind CSS, Framer Motion"],
            ["Backend", "Supabase (PostgreSQL, Auth, Storage)"],
            ["Email", "Resend"],
            ["Hosting", "Vercel + Supabase"],
        ]
    )

    # === 4.1 데이터베이스 스키마 ===
    builder.add_page_break()
    builder.add_heading("4.1 데이터베이스 스키마", 2)
    builder.add_paragraph("Supabase PostgreSQL 기반의 데이터베이스 구조입니다.")
    if "diagram_08-db-schema" in uploaded_images:
        builder.add_image(uploaded_images["diagram_08-db-schema"], width=WIDTH_18CM)

    builder.add_heading("테이블 설명", 3)
    builder.add_styled_table(
        headers=["테이블", "설명", "주요 컬럼"],
        rows=[
            ["vips", "VIP 고객 정보", "email, tier, reg_type, invite_token"],
            ["verification_codes", "QR 인증 코드", "code(6자리), status, approved_by"],
            ["invite_settings", "자동 초대 설정", "target_count, auto_send"],
            ["products", "상품 정보", "name, category_id, tier_required"],
            ["categories", "상품 카테고리", "name, slug"],
            ["inventory", "재고 관리", "product_id, size, quantity"],
            ["orders", "주문 정보", "vip_id, status, shipping_address"],
            ["order_items", "주문 상품", "order_id, product_id, size, quantity"],
        ]
    )

    builder.add_heading("RLS 정책", 3)
    builder.add_styled_table(
        headers=["테이블", "정책", "설명"],
        rows=[
            ["vips", "자신의 데이터만 조회", "auth.uid() = id"],
            ["verification_codes", "관리자만 승인 가능", "is_admin = true"],
            ["products", "활성 상품만 조회", "is_active = true"],
            ["orders", "자신의 주문만 조회", "vip_id = auth.uid()"],
            ["inventory", "읽기 전용", "SELECT only"],
        ]
    )

    # === 5. UI 시안 ===
    builder.add_page_break()
    builder.add_heading("5. UI 시안", 1)

    builder.add_heading("5.1 제품 목록 페이지", 2)
    builder.add_paragraph("VIP 고객이 초대 링크를 통해 바로 접근하는 메인 화면입니다. 별도 랜딩 페이지 없이 제품 목록으로 직접 연결됩니다.")
    if "screenshot_02-product-list" in uploaded_images:
        builder.add_image(uploaded_images["screenshot_02-product-list"], width=WIDTH_18CM)

    builder.add_page_break()
    builder.add_heading("5.2 제품 상세 페이지", 2)
    builder.add_paragraph("개별 제품의 상세 정보를 확인하는 화면입니다. 이미지 갤러리, 상품 정보, 사이즈 선택, 장바구니 추가 기능을 제공합니다.")
    if "screenshot_05-product-detail" in uploaded_images:
        builder.add_image(uploaded_images["screenshot_05-product-detail"], width=WIDTH_18CM)

    builder.add_page_break()
    builder.add_heading("5.3 체크아웃", 2)
    builder.add_paragraph("배송 정보를 확인하고 수정하는 화면입니다.")
    if "screenshot_03-checkout" in uploaded_images:
        builder.add_image(uploaded_images["screenshot_03-checkout"], width=WIDTH_18CM)

    builder.add_page_break()
    builder.add_heading("5.4 관리자 대시보드", 2)
    builder.add_paragraph("관리자용 통합 대시보드입니다.")
    if "screenshot_04-admin-dashboard" in uploaded_images:
        builder.add_image(uploaded_images["screenshot_04-admin-dashboard"], width=WIDTH_18CM)

    builder.add_page_break()
    builder.add_heading("5.5 제품 추가 워크플로우", 2)
    builder.add_paragraph("관리자가 새 제품을 등록하는 프로세스입니다.")
    if "diagram_07-product-add-flow" in uploaded_images:
        builder.add_image(uploaded_images["diagram_07-product-add-flow"], width=WIDTH_18CM)

    builder.add_heading("제품 등록 단계", 3)
    builder.add_styled_table(
        headers=["단계", "항목", "설명"],
        rows=[
            ["1", "기본 정보", "상품명, 설명, 카테고리"],
            ["2", "이미지 업로드", "상품 이미지 (최대 5장)"],
            ["3", "재고 설정", "사이즈별 재고 수량"],
            ["4", "VIP 등급 설정", "Silver/Gold 구매 가능 여부"],
            ["5", "검토 및 등록", "최종 확인 후 등록"],
        ]
    )

    builder.add_page_break()
    builder.add_heading("5.6 제품 구매 워크플로우", 2)
    builder.add_paragraph("VIP 고객이 제품을 구매하는 전체 프로세스입니다.")
    if "diagram_09-purchase-flow" in uploaded_images:
        builder.add_image(uploaded_images["diagram_09-purchase-flow"], width=WIDTH_12CM)

    builder.add_heading("구매 단계별 설명", 3)
    builder.add_styled_table(
        headers=["단계", "프로세스", "설명"],
        rows=[
            ["1. 인증", "토큰 검증", "초대 링크의 토큰 유효성 확인"],
            ["2. 탐색", "상품 브라우징", "카테고리 필터, 재고 확인, 사이즈 선택"],
            ["3. 장바구니", "수량 제한 확인", "Silver 3개 / Gold 5개 제한"],
            ["4. 주문", "배송 정보 확인", "주소 확인/수정 후 주문 확정"],
        ]
    )

    # === 5.7 QR 코드 가입 플로우 ===
    builder.add_page_break()
    builder.add_heading("5.7 QR 코드 VIP 가입", 2)
    builder.add_paragraph("QR 코드를 통한 VIP 가입 프로세스입니다. 이메일 초대와 달리 관리자 승인이 필요합니다.")
    if "diagram_10-qr-registration-flow" in uploaded_images:
        builder.add_image(uploaded_images["diagram_10-qr-registration-flow"], width=WIDTH_18CM)

    builder.add_heading("QR 가입 vs 이메일 초대 비교", 3)
    builder.add_styled_table(
        headers=["구분", "이메일 초대", "QR 코드 가입"],
        rows=[
            ["접근 방식", "관리자가 직접 초대", "사용자가 QR 스캔"],
            ["인증 방식", "토큰 링크 (자동 승인)", "6자리 코드 (관리자 승인)"],
            ["승인 절차", "불필요", "관리자 수동 승인 필요"],
            ["보안 수준", "높음 (지정된 이메일)", "중간 (코드 검증 필요)"],
        ]
    )

    builder.add_heading("QR 가입 프로세스", 3)
    builder.add_styled_table(
        headers=["단계", "사용자", "관리자"],
        rows=[
            ["1", "QR 코드 스캔", "-"],
            ["2", "가입 정보 입력 (이름, 이메일)", "-"],
            ["3", "6자리 인증코드 발급", "대기 목록에 신청 표시"],
            ["4", "코드 확인 및 대기", "신청자 정보 검토"],
            ["5", "-", "승인 또는 거부"],
            ["6", "승인 시 쇼핑몰 접속", "-"],
        ]
    )

    # === 6. 디자인 컨셉 ===
    builder.add_page_break()
    builder.add_heading("6. 디자인 컨셉", 1)

    builder.add_heading("Design Principles", 3)
    builder.add_styled_table(
        headers=["원칙", "설명"],
        rows=[
            ["럭셔리", "다크 모드 기반, 골드/블랙 컬러"],
            ["미니멀", "불필요한 요소 제거, 제품 중심"],
            ["세련됨", "부드러운 애니메이션, 정교한 타이포"],
            ["은밀함", "브랜드 최소화, 제품 경험 극대화"],
        ]
    )

    builder.add_heading("Color Palette", 3)
    builder.add_styled_table(
        headers=["색상", "코드", "용도"],
        rows=[
            ["Primary", "#D4AF37", "Gold (강조)"],
            ["Background", "#0A0A0A", "Deep Black (배경)"],
            ["Surface", "#1A1A1A", "Dark Gray (카드)"],
            ["Text", "#FFFFFF", "White (텍스트)"],
            ["Accent", "#B8860B", "Dark Gold (보조)"],
        ]
    )

    builder.add_heading("Typography", 3)
    builder.add_styled_table(
        headers=["용도", "폰트", "스타일"],
        rows=[
            ["Heading", "Playfair Display", "Serif, Elegant"],
            ["Body", "Inter", "Sans-serif, Clean"],
        ]
    )

    # === 8. 보안 요구사항 ===
    builder.add_page_break()
    builder.add_heading("7. 보안 요구사항", 1)

    builder.add_heading("인증/권한", 3)
    builder.add_styled_table(
        headers=["영역", "방식", "설명"],
        rows=[
            ["VIP 접근", "Magic Link", "고유 초대 토큰"],
            ["관리자", "Email + Password", "Supabase Auth"],
            ["API 보안", "Row Level Security", "Supabase RLS"],
            ["토큰 만료", "30일", "만료 시 재발급"],
        ]
    )

    # === 9. 성공 지표 ===
    builder.add_page_break()
    builder.add_heading("8. 성공 지표 (KPIs)", 1)
    builder.add_styled_table(
        headers=["지표", "목표", "측정 방법"],
        rows=[
            ["주문 완료율", "85%+", "방문 VIP 중 주문 완료"],
            ["페이지 로드", "< 2초", "Lighthouse"],
            ["관리 효율", "주문당 5분", "처리 시간"],
            ["가용성", "99.9%", "모니터링"],
        ]
    )

    # === 10. 리스크 ===
    builder.add_heading("9. 리스크 및 대응", 1)
    builder.add_styled_table(
        headers=["리스크", "확률", "영향", "대응"],
        rows=[
            ["토큰 유출", "중", "고", "1인 1토큰, IP 추적"],
            ["트래픽 급증", "저", "중", "Edge 스케일링"],
            ["이미지 지연", "중", "중", "CDN, 레이지 로딩"],
            ["재고 동시성", "중", "고", "트랜잭션"],
        ]
    )

    return doc_id


def main():
    print("=" * 60)
    print("GGP Heritage Mall PRD v4 - Native Tables with Styling")
    print("=" * 60)

    print("\n[1/3] Authenticating...")
    creds = get_credentials()
    print("  Done")

    print("\n[2/3] Uploading images...")
    folder_id, uploaded_images = upload_images(creds)
    print(f"  Uploaded {len(uploaded_images)} images")

    print("\n[3/3] Creating document with styled tables...")
    doc_id = create_document(creds, uploaded_images)

    print("\n" + "=" * 60)
    print("Complete!")
    print("=" * 60)
    print(f"\nDocument: https://docs.google.com/document/d/{doc_id}/edit")
    print(f"Images: https://drive.google.com/drive/folders/{folder_id}")


if __name__ == "__main__":
    main()
