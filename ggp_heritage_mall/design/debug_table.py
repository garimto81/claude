"""
Google Docs 테이블 내용 상세 확인
"""
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CREDENTIALS_FILE = r"D:\AI\claude01\json\desktop_credentials.json"
TOKEN_FILE = r"D:\AI\claude01\json\token.json"
DOC_ID = "19ln1f5z-tWYVmCMFFh3uimlTcohHPY8n3DRLY5lVIwc"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return creds


def extract_text_from_cell(cell):
    """셀에서 텍스트 추출"""
    text = ""
    for content in cell.get("content", []):
        if "paragraph" in content:
            for elem in content["paragraph"].get("elements", []):
                if "textRun" in elem:
                    text += elem["textRun"].get("content", "")
    return text.strip()


def analyze_tables(doc):
    """모든 테이블 내용 출력"""
    content = doc.get("body", {}).get("content", [])

    table_num = 0
    for element in content:
        if "table" in element:
            table_num += 1
            table = element["table"]
            rows = table.get("tableRows", [])

            print(f"\n{'='*60}")
            print(f"테이블 #{table_num} ({len(rows)}행)")
            print("=" * 60)

            for row_idx, row in enumerate(rows):
                cells = row.get("tableCells", [])
                row_data = []

                for cell in cells:
                    cell_text = extract_text_from_cell(cell)
                    # 셀 스타일 확인
                    style = cell.get("tableCellStyle", {})
                    bg = style.get("backgroundColor", {}).get("color", {}).get("rgbColor", {})
                    has_bg = bool(bg)

                    row_data.append(cell_text if cell_text else "(empty)")

                row_type = "HEADER" if row_idx == 0 else f"ROW {row_idx}"
                print(f"[{row_type}] {' | '.join(row_data)}")

            # 첫 3개 테이블만 상세 출력
            if table_num >= 3:
                print(f"\n... 나머지 테이블 생략 (총 {len([e for e in content if 'table' in e])}개)")
                break


def main():
    print("Google Docs 테이블 내용 확인")
    print("=" * 60)

    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)

    doc = docs_service.documents().get(documentId=DOC_ID).execute()
    print(f"문서: {doc.get('title')}")

    analyze_tables(doc)


if __name__ == "__main__":
    main()
