"""
Google Docs API Client

OAuth 2.0 인증 기반 Google Docs/Drive API 클라이언트.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, Resource

logger = logging.getLogger(__name__)


class GoogleDocsClient:
    """Google Docs API 클라이언트"""

    # 기본 경로 설정 - lib/google_docs/auth.py와 통합
    DEFAULT_TOKEN_PATH = Path("C:/claude/json/token.json")
    DEFAULT_CREDENTIALS_PATH = Path("C:/claude/json/desktop_credentials.json")

    # PRD 저장 폴더 ID (Google AI Studio 폴더)
    DEFAULT_FOLDER_ID = "1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW"

    # API 스코프 - lib/google_docs/auth.py와 통합 (drive.file → drive)
    SCOPES = [
        "https://www.googleapis.com/auth/documents",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(
        self,
        token_path: Optional[Path] = None,
        credentials_path: Optional[Path] = None,
        folder_id: Optional[str] = None,
    ):
        """
        클라이언트 초기화

        Args:
            token_path: OAuth 토큰 파일 경로
            credentials_path: OAuth 클라이언트 자격증명 경로
            folder_id: PRD 저장 폴더 ID
        """
        self.token_path = token_path or self.DEFAULT_TOKEN_PATH
        self.credentials_path = credentials_path or self.DEFAULT_CREDENTIALS_PATH
        self.folder_id = folder_id or self.DEFAULT_FOLDER_ID

        self._credentials: Optional[Credentials] = None
        self._docs_service: Optional[Resource] = None
        self._drive_service: Optional[Resource] = None

    def _load_credentials(self) -> Credentials:
        """OAuth 자격증명 로드 및 갱신"""
        if self._credentials and self._credentials.valid:
            return self._credentials

        if self.token_path.exists():
            with open(self.token_path, "r", encoding="utf-8") as f:
                token_data = json.load(f)

            self._credentials = Credentials(
                token=token_data.get("token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri=token_data.get("token_uri"),
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                scopes=token_data.get("scopes", self.SCOPES),
            )

            # 토큰 만료 시 갱신
            if self._credentials.expired and self._credentials.refresh_token:
                logger.info("토큰 갱신 중...")
                self._credentials.refresh(Request())
                self._save_credentials()

        else:
            raise FileNotFoundError(
                f"토큰 파일을 찾을 수 없습니다: {self.token_path}\n"
                "먼저 OAuth 인증을 수행해주세요."
            )

        return self._credentials

    def _save_credentials(self) -> None:
        """갱신된 자격증명 저장"""
        token_data = {
            "token": self._credentials.token,
            "refresh_token": self._credentials.refresh_token,
            "token_uri": self._credentials.token_uri,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "scopes": list(self._credentials.scopes or []),
        }

        with open(self.token_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

        logger.info(f"토큰 저장됨: {self.token_path}")

    @property
    def docs_service(self) -> Resource:
        """Google Docs API 서비스"""
        if self._docs_service is None:
            credentials = self._load_credentials()
            self._docs_service = build("docs", "v1", credentials=credentials)
        return self._docs_service

    @property
    def drive_service(self) -> Resource:
        """Google Drive API 서비스"""
        if self._drive_service is None:
            credentials = self._load_credentials()
            self._drive_service = build("drive", "v3", credentials=credentials)
        return self._drive_service

    # ==================== Document Operations ====================

    def create_document(
        self,
        title: str,
        folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        새 Google Docs 문서 생성

        Args:
            title: 문서 제목
            folder_id: 저장할 폴더 ID (없으면 기본 폴더)

        Returns:
            생성된 문서 정보 (documentId, revisionId, title)
        """
        folder_id = folder_id or self.folder_id

        # 1. 빈 문서 생성
        doc = self.docs_service.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]

        # 2. 폴더로 이동
        if folder_id:
            # 현재 부모 조회
            file_info = (
                self.drive_service.files()
                .get(fileId=doc_id, fields="parents")
                .execute()
            )
            current_parents = ",".join(file_info.get("parents", []))

            # 새 폴더로 이동
            self.drive_service.files().update(
                fileId=doc_id,
                addParents=folder_id,
                removeParents=current_parents,
                fields="id, parents",
            ).execute()

        logger.info(f"문서 생성됨: {title} (ID: {doc_id})")

        return {
            "documentId": doc_id,
            "title": title,
            "url": f"https://docs.google.com/document/d/{doc_id}/edit",
        }

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        문서 내용 조회

        Args:
            document_id: Google Docs 문서 ID

        Returns:
            문서 전체 내용 (body, title 등)
        """
        doc = self.docs_service.documents().get(documentId=document_id).execute()
        return doc

    def get_document_text(self, document_id: str) -> str:
        """
        문서 텍스트만 추출

        Args:
            document_id: Google Docs 문서 ID

        Returns:
            문서 전체 텍스트
        """
        doc = self.get_document(document_id)
        return self._extract_text(doc.get("body", {}).get("content", []))

    def _extract_text(self, content: List[Dict]) -> str:
        """문서 content에서 텍스트 추출"""
        text_parts = []

        for element in content:
            if "paragraph" in element:
                for para_element in element["paragraph"].get("elements", []):
                    if "textRun" in para_element:
                        text_parts.append(para_element["textRun"].get("content", ""))
            elif "table" in element:
                # 테이블 처리 (간단히 텍스트만 추출)
                for row in element["table"].get("tableRows", []):
                    for cell in row.get("tableCells", []):
                        text_parts.append(self._extract_text(cell.get("content", [])))

        return "".join(text_parts)

    def update_document(
        self,
        document_id: str,
        requests: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        문서 업데이트 (batchUpdate)

        Args:
            document_id: Google Docs 문서 ID
            requests: 업데이트 요청 리스트

        Returns:
            업데이트 결과
        """
        result = (
            self.docs_service.documents()
            .batchUpdate(documentId=document_id, body={"requests": requests})
            .execute()
        )
        return result

    def insert_text(
        self,
        document_id: str,
        text: str,
        index: int = 1,
    ) -> Dict[str, Any]:
        """
        문서에 텍스트 삽입

        Args:
            document_id: Google Docs 문서 ID
            text: 삽입할 텍스트
            index: 삽입 위치 (기본: 문서 시작)

        Returns:
            업데이트 결과
        """
        requests = [{"insertText": {"location": {"index": index}, "text": text}}]
        return self.update_document(document_id, requests)

    def apply_heading_style(
        self,
        document_id: str,
        start_index: int,
        end_index: int,
        heading_level: int,
    ) -> Dict[str, Any]:
        """
        텍스트에 헤딩 스타일 적용

        Args:
            document_id: Google Docs 문서 ID
            start_index: 시작 인덱스
            end_index: 끝 인덱스
            heading_level: 헤딩 레벨 (1-6)

        Returns:
            업데이트 결과
        """
        heading_map = {
            1: "HEADING_1",
            2: "HEADING_2",
            3: "HEADING_3",
            4: "HEADING_4",
            5: "HEADING_5",
            6: "HEADING_6",
        }

        requests = [
            {
                "updateParagraphStyle": {
                    "range": {"startIndex": start_index, "endIndex": end_index},
                    "paragraphStyle": {
                        "namedStyleType": heading_map.get(heading_level, "HEADING_1")
                    },
                    "fields": "namedStyleType",
                }
            }
        ]
        return self.update_document(document_id, requests)

    def delete_document(self, document_id: str) -> None:
        """
        문서 삭제 (휴지통으로 이동)

        Args:
            document_id: Google Docs 문서 ID
        """
        self.drive_service.files().delete(fileId=document_id).execute()
        logger.info(f"문서 삭제됨: {document_id}")

    # ==================== Folder Operations ====================

    def list_documents_in_folder(
        self,
        folder_id: Optional[str] = None,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        폴더 내 문서 목록 조회

        Args:
            folder_id: 폴더 ID (없으면 기본 폴더)
            page_size: 페이지 크기

        Returns:
            문서 목록 (id, name, modifiedTime)
        """
        folder_id = folder_id or self.folder_id

        query = (
            f"'{folder_id}' in parents "
            "and mimeType='application/vnd.google-apps.document' "
            "and trashed=false"
        )

        results = (
            self.drive_service.files()
            .list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, modifiedTime, createdTime)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )

        return results.get("files", [])

    def copy_document(
        self,
        source_doc_id: str,
        new_title: str,
        folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        문서 복사 (템플릿 복사용)

        Args:
            source_doc_id: 원본 문서 ID
            new_title: 새 문서 제목
            folder_id: 저장할 폴더 ID

        Returns:
            복사된 문서 정보
        """
        folder_id = folder_id or self.folder_id

        body = {"name": new_title}
        if folder_id:
            body["parents"] = [folder_id]

        copied_file = (
            self.drive_service.files().copy(fileId=source_doc_id, body=body).execute()
        )

        doc_id = copied_file["id"]
        logger.info(f"문서 복사됨: {new_title} (ID: {doc_id})")

        return {
            "documentId": doc_id,
            "title": new_title,
            "url": f"https://docs.google.com/document/d/{doc_id}/edit",
        }

    # ==================== Utility Methods ====================

    def get_document_url(self, document_id: str) -> str:
        """문서 편집 URL 생성"""
        return f"https://docs.google.com/document/d/{document_id}/edit"

    def test_connection(self) -> bool:
        """
        API 연결 테스트

        Returns:
            연결 성공 여부
        """
        try:
            # 간단한 API 호출로 테스트
            self.drive_service.about().get(fields="user").execute()
            logger.info("Google API 연결 성공")
            return True
        except Exception as e:
            logger.error(f"Google API 연결 실패: {e}")
            return False
