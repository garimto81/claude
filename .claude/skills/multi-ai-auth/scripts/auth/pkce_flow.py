"""OAuth 2.0 Authorization Code + PKCE 구현

Local HTTP Callback을 사용하는 데스크톱 앱용 OAuth 플로우.
Google Gemini API 인증에 사용.
"""

import asyncio
import base64
import hashlib
import secrets
import threading
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
from rich.console import Console
from rich.panel import Panel

console = Console()


@dataclass
class TokenResponse:
    """Token 응답"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_in: int
    scope: Optional[str]


class PKCEFlowError(Exception):
    """PKCE Flow 에러"""
    pass


class CallbackHandler(BaseHTTPRequestHandler):
    """OAuth 콜백 HTTP 핸들러"""

    authorization_code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None

    def log_message(self, format, *args):
        """로그 비활성화"""
        pass

    def do_GET(self):
        """GET 요청 처리 (콜백)"""
        query = urlparse(self.path).query
        params = parse_qs(query)

        if "code" in params:
            CallbackHandler.authorization_code = params["code"][0]
            CallbackHandler.state = params.get("state", [None])[0]
            self._send_success_response()
        elif "error" in params:
            CallbackHandler.error = params.get("error_description", params["error"])[0]
            self._send_error_response()
        else:
            self._send_error_response()

    def _send_success_response(self):
        """성공 응답"""
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>인증 성공</title>
            <style>
                body { font-family: -apple-system, sans-serif; text-align: center; padding: 50px; background: #1a1a2e; color: #eee; }
                h1 { color: #4ade80; }
                p { color: #94a3b8; }
            </style>
        </head>
        <body>
            <h1>✅ 인증 성공!</h1>
            <p>이 창을 닫고 터미널로 돌아가세요.</p>
            <script>setTimeout(() => window.close(), 3000);</script>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

    def _send_error_response(self):
        """에러 응답"""
        self.send_response(400)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>인증 실패</title>
            <style>
                body { font-family: -apple-system, sans-serif; text-align: center; padding: 50px; background: #1a1a2e; color: #eee; }
                h1 { color: #f87171; }
            </style>
        </head>
        <body>
            <h1>❌ 인증 실패</h1>
            <p>다시 시도해 주세요.</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())


class PKCEFlow:
    """OAuth 2.0 Authorization Code + PKCE 구현

    Example:
        flow = PKCEFlow(
            client_id="your-client-id",
            client_secret="your-client-secret",
            authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
            token_endpoint="https://oauth2.googleapis.com/token"
        )
        token = await flow.authenticate()
    """

    def __init__(
        self,
        client_id: str,
        authorization_endpoint: str,
        token_endpoint: str,
        client_secret: Optional[str] = None,
        redirect_port: int = 8080,
        scope: str = "openid email"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.redirect_port = redirect_port
        self.redirect_uri = f"http://localhost:{redirect_port}/callback"
        self.scope = scope

        # PKCE 생성
        self.code_verifier = self._generate_code_verifier()
        self.code_challenge = self._generate_code_challenge(self.code_verifier)
        self.state = secrets.token_hex(16)

    def _generate_code_verifier(self) -> str:
        """PKCE code_verifier 생성 (43-128 characters)"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")

    def _generate_code_challenge(self, verifier: str) -> str:
        """PKCE code_challenge 생성 (SHA256)"""
        digest = hashlib.sha256(verifier.encode()).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")

    def get_authorization_url(self) -> str:
        """Authorization URL 생성"""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": self.state,
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
            "access_type": "offline",  # refresh_token 받기
            "prompt": "consent"
        }
        return f"{self.authorization_endpoint}?{urlencode(params)}"

    def _start_callback_server(self) -> HTTPServer:
        """로컬 콜백 서버 시작"""
        # 핸들러 상태 초기화
        CallbackHandler.authorization_code = None
        CallbackHandler.state = None
        CallbackHandler.error = None

        server = HTTPServer(("localhost", self.redirect_port), CallbackHandler)
        thread = threading.Thread(target=server.handle_request)
        thread.daemon = True
        thread.start()
        return server

    async def exchange_code_for_token(self, code: str) -> TokenResponse:
        """Authorization code를 token으로 교환"""
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "code_verifier": self.code_verifier
            }
            if self.client_secret:
                data["client_secret"] = self.client_secret

            response = await client.post(
                self.token_endpoint,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                raise PKCEFlowError(f"Token exchange failed: {response.text}")

            result = response.json()
            return TokenResponse(
                access_token=result["access_token"],
                refresh_token=result.get("refresh_token"),
                token_type=result.get("token_type", "Bearer"),
                expires_in=result.get("expires_in", 3600),
                scope=result.get("scope")
            )

    async def authenticate(self, timeout: int = 300) -> TokenResponse:
        """전체 인증 플로우 실행

        Args:
            timeout: 인증 타임아웃 (초)

        Returns:
            TokenResponse: 인증 완료 후 토큰
        """
        # 1. 콜백 서버 시작
        server = self._start_callback_server()

        # 2. 브라우저에서 인증 시작
        auth_url = self.get_authorization_url()

        console.print()
        console.print(Panel.fit(
            f"[bold cyan]브라우저가 자동으로 열립니다.[/bold cyan]\n"
            f"열리지 않으면 다음 URL을 방문하세요:\n"
            f"[dim]{auth_url[:80]}...[/dim]",
            title="🔐 인증 필요",
            border_style="cyan"
        ))
        console.print()

        webbrowser.open(auth_url)
        console.print("[dim]브라우저에서 인증을 완료하세요...[/dim]")

        # 3. 콜백 대기
        start_time = asyncio.get_event_loop().time()
        while CallbackHandler.authorization_code is None and CallbackHandler.error is None:
            if asyncio.get_event_loop().time() - start_time > timeout:
                server.shutdown()
                raise PKCEFlowError("Authorization timeout")
            await asyncio.sleep(0.1)

        server.shutdown()

        # 4. 에러 확인
        if CallbackHandler.error:
            raise PKCEFlowError(f"Authorization failed: {CallbackHandler.error}")

        # 5. State 검증
        if CallbackHandler.state != self.state:
            raise PKCEFlowError("State mismatch - possible CSRF attack")

        # 6. Token 교환
        code = CallbackHandler.authorization_code
        token = await self.exchange_code_for_token(code)

        console.print("[bold green]✅ 인증 성공![/bold green]")
        return token


# Google Gemini 전용 설정
class GooglePKCEFlow(PKCEFlow):
    """Google Gemini API용 PKCE Flow"""

    DEFAULT_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    DEFAULT_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

    def __init__(
        self,
        client_id: str,
        client_secret: Optional[str] = None,
        authorization_endpoint: str = DEFAULT_AUTHORIZATION_ENDPOINT,
        token_endpoint: str = DEFAULT_TOKEN_ENDPOINT,
        redirect_port: int = 8080,
        scope: str = "https://www.googleapis.com/auth/generative-language.retriever openid email"
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorization_endpoint=authorization_endpoint,
            token_endpoint=token_endpoint,
            redirect_port=redirect_port,
            scope=scope
        )
