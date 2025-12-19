"""
Google Docs 문서 분석 스크립트
"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CREDENTIALS_FILE = r"D:\AI\claude01\json\desktop_credentials.json"
TOKEN_FILE = r"D:\AI\claude01\json\token.json"
DOC_ID = "13IsFncMEJFf8Q15dQVCb9feUEO2IhZotTD21-cq0Tq4"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]


def get_credentials():
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


def analyze_document(doc):
    """문서 구조 분석"""
    issues = []
    stats = {
        "tables": 0,
        "images": 0,
        "paragraphs": 0,
        "page_breaks": 0,
        "headings": [],
        "table_details": [],
        "image_details": [],
    }

    content = doc.get("body", {}).get("content", [])

    for element in content:
        # 테이블 분석
        if "table" in element:
            stats["tables"] += 1
            table = element["table"]
            rows = len(table.get("tableRows", []))
            cols = len(table.get("tableRows", [{}])[0].get("tableCells", []))

            # 셀 내용 확인
            first_row = table.get("tableRows", [{}])[0]
            first_cell_content = ""
            if first_row.get("tableCells"):
                cell = first_row["tableCells"][0]
                cell_content = cell.get("content", [])
                if cell_content:
                    for para in cell_content:
                        for elem in para.get("paragraph", {}).get("elements", []):
                            if "textRun" in elem:
                                first_cell_content += elem["textRun"].get("content", "")

            # 테이블 스타일 확인
            has_style = False
            if first_row.get("tableCells"):
                cell_style = first_row["tableCells"][0].get("tableCellStyle", {})
                if cell_style.get("backgroundColor"):
                    has_style = True

            stats["table_details"].append({
                "rows": rows,
                "cols": cols,
                "first_cell": first_cell_content.strip()[:30],
                "has_style": has_style,
            })

            # 문제점 확인
            if not has_style:
                issues.append(f"Table '{first_cell_content.strip()[:20]}': 배경색 스타일 없음")
            if not first_cell_content.strip():
                issues.append(f"Table {stats['tables']}: 첫 번째 셀이 비어있음")

        # 단락 분석
        if "paragraph" in element:
            stats["paragraphs"] += 1
            paragraph = element["paragraph"]

            # 이미지 확인
            for elem in paragraph.get("elements", []):
                if "inlineObjectElement" in elem:
                    stats["images"] += 1
                    obj_id = elem["inlineObjectElement"].get("inlineObjectId", "")

                    # 이미지 크기 확인
                    inline_objects = doc.get("inlineObjects", {})
                    if obj_id in inline_objects:
                        obj = inline_objects[obj_id]
                        props = obj.get("inlineObjectProperties", {})
                        size = props.get("embeddedObject", {}).get("size", {})
                        width = size.get("width", {}).get("magnitude", 0)
                        height = size.get("height", {}).get("magnitude", 0)

                        stats["image_details"].append({
                            "width": round(width, 1),
                            "height": round(height, 1),
                        })

                        # 크기 문제 확인
                        if width < 100:
                            issues.append(f"Image {stats['images']}: 너비가 너무 작음 ({width}pt)")
                        if height > 600:
                            issues.append(f"Image {stats['images']}: 높이가 너무 큼 ({height}pt)")

                # 텍스트 스타일 확인
                if "textRun" in elem:
                    text = elem["textRun"].get("content", "")
                    style = elem["textRun"].get("textStyle", {})
                    font_size = style.get("fontSize", {}).get("magnitude", 0)

                    # 제목 확인
                    if style.get("bold") and font_size >= 14:
                        text_clean = text.strip()
                        if text_clean:
                            stats["headings"].append({
                                "text": text_clean[:40],
                                "size": font_size,
                            })

        # 페이지 브레이크
        if "paragraph" in element:
            for elem in element["paragraph"].get("elements", []):
                if "pageBreak" in elem:
                    stats["page_breaks"] += 1

    return stats, issues


def main():
    print("=" * 60)
    print("Google Docs 문서 분석")
    print("=" * 60)

    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)

    print("\n문서 가져오는 중...")
    doc = docs_service.documents().get(documentId=DOC_ID).execute()

    title = doc.get("title", "Unknown")
    print(f"제목: {title}")
    print(f"문서 ID: {DOC_ID}")

    stats, issues = analyze_document(doc)

    print("\n" + "=" * 60)
    print("통계")
    print("=" * 60)
    print(f"  테이블: {stats['tables']}개")
    print(f"  이미지: {stats['images']}개")
    print(f"  단락: {stats['paragraphs']}개")
    print(f"  페이지 브레이크: {stats['page_breaks']}개")

    print("\n제목 목록:")
    for h in stats["headings"][:15]:
        print(f"  [{h['size']}pt] {h['text']}")

    print("\n테이블 상세:")
    for i, t in enumerate(stats["table_details"], 1):
        style_mark = "[OK]" if t["has_style"] else "[NO STYLE]"
        print(f"  {i}. {t['rows']}x{t['cols']} - '{t['first_cell']}' {style_mark}")

    print("\n이미지 크기:")
    for i, img in enumerate(stats["image_details"], 1):
        print(f"  {i}. {img['width']}pt x {img['height']}pt")

    print("\n" + "=" * 60)
    print("문제점 분석")
    print("=" * 60)
    if issues:
        for issue in issues:
            print(f"  [!] {issue}")
    else:
        print("  문제점 없음")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
