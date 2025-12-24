"""
OAuth 2.0 인증 모듈

Google Docs/Drive API 인증을 처리합니다.
"""

import os
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# 인증 파일 경로 (절대 경로)
CREDENTIALS_FILE = Path(r'D:\AI\claude01\json\desktop_credentials.json')
TOKEN_FILE = Path(r'D:\AI\claude01\json\token.json')

# Google Docs + Drive 권한
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

# 공유 폴더 ID (Google AI Studio 폴더)
DEFAULT_FOLDER_ID = '1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW'


def get_credentials() -> Credentials:
    """
    OAuth 2.0 인증 정보 획득

    Returns:
        Credentials: Google API 인증 정보
    """
    creds = None

    # 기존 토큰 확인
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # 토큰이 없거나 만료된 경우
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 토큰 갱신
            creds.refresh(Request())
        else:
            # 새로운 인증 플로우
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"OAuth 자격증명 파일을 찾을 수 없습니다: {CREDENTIALS_FILE}\n"
                    "Google Cloud Console에서 다운로드하세요."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # 토큰 저장
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds
