"""
Google Docs 이미지 중앙 정렬 스크립트
"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 설정
CREDENTIALS_FILE = r"D:\AI\claude01\json\desktop_credentials.json"
TOKEN_FILE = r"D:\AI\claude01\json\token.json"
DOC_ID = "1_tTRxSsZ9CER-L_vxnWHcqWFbAETx-LEEuR27kazwCQ"

SCOPES = [
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


def find_image_paragraphs(doc):
    """이미지가 포함된 단락의 인덱스 찾기"""
    image_ranges = []
    content = doc.get("body", {}).get("content", [])

    for element in content:
        if "paragraph" in element:
            paragraph = element["paragraph"]
            start_index = element["startIndex"]
            end_index = element["endIndex"]

            for elem in paragraph.get("elements", []):
                if "inlineObjectElement" in elem:
                    image_ranges.append({
                        "start": start_index,
                        "end": end_index,
                    })
                    break

    return image_ranges


def center_images(creds):
    """이미지 단락 중앙 정렬"""
    docs_service = build("docs", "v1", credentials=creds)

    print("Fetching document...")
    doc = docs_service.documents().get(documentId=DOC_ID).execute()

    print("Finding image paragraphs...")
    image_ranges = find_image_paragraphs(doc)
    print(f"Found {len(image_ranges)} images")

    if not image_ranges:
        print("No images found")
        return

    # 중앙 정렬 요청 생성
    requests = []
    for img_range in image_ranges:
        requests.append({
            "updateParagraphStyle": {
                "range": {
                    "startIndex": img_range["start"],
                    "endIndex": img_range["end"],
                },
                "paragraphStyle": {
                    "alignment": "CENTER",
                },
                "fields": "alignment",
            }
        })

    print(f"Centering {len(requests)} paragraphs...")
    docs_service.documents().batchUpdate(
        documentId=DOC_ID, body={"requests": requests}
    ).execute()

    print("Done!")
    print(f"Document: https://docs.google.com/document/d/{DOC_ID}/edit")


def main():
    print("=" * 50)
    print("Center Images in Google Docs")
    print("=" * 50)

    creds = get_credentials()
    center_images(creds)


if __name__ == "__main__":
    main()
