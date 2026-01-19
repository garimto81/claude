# -*- coding: utf-8 -*-
"""Google Docs 이미지 교체 스크립트"""

import sys
from pathlib import Path

sys.path.insert(0, "C:/claude/lib")

from google_docs.auth import get_credentials
from google_docs.image_inserter import ImageInserter
from googleapiclient.discovery import build


def main():
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    inserter = ImageInserter(creds, docs_service, drive_service)

    new_doc_id = "1b6U1KuFp4vVBcdSzzjVYxKO9bfSAw8pTfpnEaJWKGnQ"
    folder_id = "1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW"  # Google AI Studio 폴더

    # 새 이미지 파일들
    image_files = [
        Path("C:/claude/WSOPTV/docs/images/PRD-0005/en/responsibility-matrix.png"),
        Path("C:/claude/WSOPTV/docs/images/PRD-0005/en/data-flow.png"),
        Path("C:/claude/WSOPTV/docs/images/PRD-0005/en/system-architecture.png"),
    ]

    # 현재 문서의 이미지 정보 가져오기
    doc = docs_service.documents().get(documentId=new_doc_id).execute()
    body = doc.get("body", {})
    content = body.get("content", [])

    # 이미지 위치 수집 (역순 정렬)
    image_positions = []
    for element in content:
        if "paragraph" in element:
            para = element["paragraph"]
            for elem in para.get("elements", []):
                if "inlineObjectElement" in elem:
                    inline_obj = elem["inlineObjectElement"]
                    obj_id = inline_obj.get("inlineObjectId")
                    start_idx = elem.get("startIndex", 0)
                    end_idx = elem.get("endIndex", 0)
                    image_positions.append(
                        {"id": obj_id, "start": start_idx, "end": end_idx}
                    )

    # 역순 정렬 (인덱스 시프트 방지)
    image_positions.sort(key=lambda x: x["start"], reverse=True)

    print(f"문서 내 이미지 {len(image_positions)}개 발견")
    print(f"교체할 이미지 {len(image_files)}개")

    # 이미지 업로드 및 URL 생성
    image_urls = []
    for img_file in image_files:
        print(f"\n업로드 중: {img_file.name}")
        file_id, image_url = inserter.upload_to_drive(
            img_file,
            folder_id=folder_id,
            make_public=True,
            file_name=f"PRD-0005-EN-{img_file.name}",
        )
        image_urls.append(image_url)
        print(f"  URL: {image_url}")

    # 이미지 교체 (역순으로)
    for i, (pos, url) in enumerate(zip(image_positions, image_urls)):
        print(f'\n이미지 {i+1} 교체 중: {pos["id"]}')

        # 1. 기존 이미지 삭제
        delete_request = {
            "deleteContentRange": {
                "range": {"startIndex": pos["start"], "endIndex": pos["end"]}
            }
        }

        # 2. 새 이미지 삽입
        insert_request = {
            "insertInlineImage": {
                "location": {"index": pos["start"]},
                "uri": url,
                "objectSize": {"width": {"magnitude": 510, "unit": "PT"}},
            }
        }

        try:
            result = (
                docs_service.documents()
                .batchUpdate(
                    documentId=new_doc_id,
                    body={"requests": [delete_request, insert_request]},
                )
                .execute()
            )
            print("  교체 완료!")
        except Exception as e:
            print(f"  오류: {e}")

    print("\n모든 이미지 교체 완료!")
    print(f"문서 URL: https://docs.google.com/document/d/{new_doc_id}/edit")


if __name__ == "__main__":
    main()
