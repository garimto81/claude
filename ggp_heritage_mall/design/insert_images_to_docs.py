"""
Google Docs에 스크린샷 이미지 삽입 스크립트
"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 경로 설정
CREDENTIALS_FILE = r"D:\AI\claude01\json\desktop_credentials.json"
TOKEN_FILE = r"D:\AI\claude01\json\token.json"

# Google Docs 문서 ID
DOC_ID = "1omLU6-l8oSFB16JCBxbodDzKI1Fp8q84rijntTStpTk"

# 이미지 파일 ID (Google Drive)
IMAGE_IDS = {
    "01-landing-page": "1ztYuyEehulps7kBMH16ZhSLj4LV3OERz",
    "02-product-list": "1mkfNSkGFHOC0vDQ5cVVWNAt72nqvyjbe",
    "03-checkout": "16rNflVxgcr2bDqfZg0VZj_CVMGd8xLV2",
    "04-admin-dashboard": "10w2O8tiCl9SzH9D1fm6EzAMX3mudbGWk",
}

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


def get_document_content(docs_service, doc_id):
    """문서 내용 가져오기"""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    return doc


def find_placeholder_positions(doc):
    """[이미지: ...] 플레이스홀더 위치 찾기"""
    positions = []
    content = doc.get("body", {}).get("content", [])

    for element in content:
        if "paragraph" in element:
            paragraph = element["paragraph"]
            for elem in paragraph.get("elements", []):
                if "textRun" in elem:
                    text = elem["textRun"]["content"]
                    start_index = elem["startIndex"]

                    # 각 이미지 플레이스홀더 찾기
                    for image_name in IMAGE_IDS.keys():
                        placeholder = f"[이미지: {image_name}.png]"
                        if placeholder in text:
                            pos = text.find(placeholder)
                            positions.append(
                                {
                                    "image_name": image_name,
                                    "start": start_index + pos,
                                    "end": start_index + pos + len(placeholder),
                                    "placeholder": placeholder,
                                }
                            )

    # 역순 정렬 (뒤에서부터 삽입해야 인덱스가 밀리지 않음)
    positions.sort(key=lambda x: x["start"], reverse=True)
    return positions


def insert_images(creds):
    """문서에 이미지 삽입"""
    docs_service = build("docs", "v1", credentials=creds)

    print("문서 내용 분석 중...")
    doc = get_document_content(docs_service, DOC_ID)

    print("플레이스홀더 위치 찾는 중...")
    positions = find_placeholder_positions(doc)

    if not positions:
        print("플레이스홀더를 찾을 수 없습니다.")
        return

    print(f"발견된 플레이스홀더: {len(positions)}개")

    for pos in positions:
        print(f"  - {pos['placeholder']} at index {pos['start']}")

    # 각 플레이스홀더에 이미지 삽입
    for pos in positions:
        image_name = pos["image_name"]
        image_id = IMAGE_IDS[image_name]
        image_url = f"https://drive.google.com/uc?id={image_id}"

        print(f"\n이미지 삽입 중: {image_name}...")

        requests = [
            # 1. 플레이스홀더 텍스트 삭제
            {
                "deleteContentRange": {
                    "range": {"startIndex": pos["start"], "endIndex": pos["end"]}
                }
            },
            # 2. 이미지 삽입
            {
                "insertInlineImage": {
                    "location": {"index": pos["start"]},
                    "uri": image_url,
                    "objectSize": {
                        "width": {"magnitude": 500, "unit": "PT"},
                        "height": {"magnitude": 280, "unit": "PT"},
                    },
                }
            },
        ]

        try:
            docs_service.documents().batchUpdate(
                documentId=DOC_ID, body={"requests": requests}
            ).execute()
            print(f"  [OK] {image_name} inserted")
        except Exception as e:
            print(f"  [FAIL] {image_name}: {e}")

    print(f"\n완료! 문서 URL: https://docs.google.com/document/d/{DOC_ID}/edit")


def main():
    print("=" * 60)
    print("Google Docs 이미지 삽입")
    print("=" * 60)

    print("\n1. Google 인증 중...")
    creds = get_credentials()
    print("   인증 완료")

    print("\n2. 이미지 삽입 중...")
    insert_images(creds)


if __name__ == "__main__":
    main()
