# -*- coding: utf-8 -*-
"""한글 텍스트를 영문으로 교체하는 스크립트"""

import sys

sys.path.insert(0, "C:/claude/lib")

from google_docs.auth import get_credentials
from googleapiclient.discovery import build


def main():
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)

    new_doc_id = "1b6U1KuFp4vVBcdSzzjVYxKO9bfSAw8pTfpnEaJWKGnQ"

    # 한글 → 영문 교체
    replacements = [
        ("다이어그램", "Diagram"),
        ("값", "Value"),
    ]

    requests = []
    for old_text, new_text in replacements:
        requests.append(
            {
                "replaceAllText": {
                    "containsText": {"text": old_text, "matchCase": False},
                    "replaceText": new_text,
                }
            }
        )

    result = (
        docs_service.documents()
        .batchUpdate(documentId=new_doc_id, body={"requests": requests})
        .execute()
    )

    print("한글 교체 완료!")
    for i, reply in enumerate(result.get("replies", [])):
        if "replaceAllText" in reply:
            c = reply["replaceAllText"].get("occurrencesChanged", 0)
            print(f'  "{replacements[i][0]}" -> "{replacements[i][1]}": {c}회')


if __name__ == "__main__":
    main()
