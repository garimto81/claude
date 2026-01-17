# PRD-0031: Multi-AI Authentication Skill

**Version**: 1.0.0 | **Date**: 2026-01-18 | **Status**: Draft
**Priority**: P1 | **Type**: New Feature

---

## 1. Executive Summary

### 문제 정의

Claude Code에서 외부 AI 모델(GPT, Gemini)을 활용한 Cross-AI Verification을 구현하려면 각 서비스의 인증이 필요합니다. 현재 구조에서는:

| 문제 | 현재 상태 | 영향 |
|------|----------|------|
| **인증 부재** | 각 AI 서비스에 대한 인증 메커니즘 없음 | 외부 AI 활용 불가 |
| **API 키 관리** | 환경변수 수동 설정 필요 | UX 저하 |
| **토큰 갱신** | 자동 갱신 메커니즘 없음 | 세션 만료 |
| **통합 부재** | 각 서비스별 개별 설정 필요 | 복잡성 증가 |

### 제안 솔루션

`/login` 스타일의 **OAuth 기반 Multi-AI Authentication Skill** 구현:

```
/ai-auth login --provider openai    # OpenAI OAuth (Device Flow)
/ai-auth login --provider google    # Google OAuth (InstalledAppFlow)
/ai-auth login --provider poe       # Poe API Key
/ai-auth status                     # 인증 상태 확인
/ai-auth logout --provider openai   # 로그아웃
```

### 예상 효과

| 지표 | 현재 | 목표 |
|------|------|------|
| 외부 AI 접근성 | 0% | **100%** |
| 인증 설정 시간 | 10분+ (수동) | **2분** (자동) |
| 토큰 관리 | 수동 | **자동 갱신** |
| 보안 수준 | 환경변수 노출 | **암호화 저장** |

---

## 2. 기술 사양

### 2.1 지원 인증 방식

| Provider | 인증 방식 | 구독 모델 접근 | 비고 |
|----------|----------|:-------------:|------|
| **OpenAI (Codex)** | Device Authorization Grant (RFC 8628) | ✅ ChatGPT Plus | 공식 지원 |
| **Google Gemini** | OAuth 2.0 InstalledAppFlow | ✅ API 접근 | API Key도 지원 |
| **Poe** | API Key | ✅ 100+ 모델 | $4.99/월 |
| **Anthropic** | API Key | ✅ Claude API | 기존 /login과 별개 |

### 2.2 OAuth 플로우 구현

#### Device Authorization Grant (OpenAI Codex)

```
┌─────────────────────────────────────────────────────────────┐
│  RFC 8628 Device Authorization Grant                        │
│                                                             │
│  1. CLI → Authorization Server: device_code 요청            │
│  2. Server → CLI: device_code, user_code, verification_url  │
│  3. CLI → 사용자: "방문: {url}, 코드: {code}"               │
│  4. 사용자 → 브라우저: 인증 완료                            │
│  5. CLI → Server: Polling으로 token 확인                    │
│  6. Server → CLI: access_token 반환                         │
│  7. CLI → Token Store: 암호화 저장                          │
└─────────────────────────────────────────────────────────────┘
```

#### InstalledAppFlow (Google)

```
┌─────────────────────────────────────────────────────────────┐
│  OAuth 2.0 + PKCE (Local Callback)                          │
│                                                             │
│  1. CLI → 로컬 HTTP 서버 시작 (localhost:PORT)              │
│  2. CLI → 브라우저 자동 오픈 (Authorization URL + PKCE)     │
│  3. 사용자 → 브라우저에서 인증                              │
│  4. Server → localhost:PORT/callback 으로 Redirect          │
│  5. CLI → authorization_code를 access_token으로 교환        │
│  6. CLI → Token Store: 암호화 저장                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 토큰 저장

| OS | 저장 위치 | 암호화 |
|----|----------|--------|
| Windows | `%APPDATA%\claude-code\ai-auth\` | DPAPI |
| macOS | Keychain | 시스템 암호화 |
| Linux | `~/.config/claude-code/ai-auth/` | libsecret |

**토큰 파일 구조**:
```json
{
  "provider": "openai",
  "access_token": "encrypted:...",
  "refresh_token": "encrypted:...",
  "expires_at": "2026-01-19T10:00:00Z",
  "scopes": ["chat", "models"]
}
```

---

## 3. 기능 명세

### 3.1 CLI 인터페이스

```bash
# 로그인
/ai-auth login --provider openai
/ai-auth login --provider google
/ai-auth login --provider poe --api-key "sk-..."

# 상태 확인
/ai-auth status
/ai-auth status --provider openai

# 로그아웃
/ai-auth logout --provider openai
/ai-auth logout --all

# 토큰 갱신 (자동/수동)
/ai-auth refresh --provider openai
```

### 3.2 출력 형식

#### 로그인 성공
```
🔐 OpenAI 인증 시작...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  브라우저에서 방문: https://auth.openai.com/device
  코드 입력: ABC-123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

인증 대기 중... ✓

✅ OpenAI 인증 성공!
   계정: user@example.com
   플랜: ChatGPT Plus
   만료: 2026-02-17
```

#### 상태 확인
```
## AI 인증 상태

| Provider | 상태 | 계정 | 만료 |
|----------|------|------|------|
| OpenAI   | ✅ 활성 | user@example.com | 30일 |
| Google   | ✅ 활성 | user@gmail.com | 7일 |
| Poe      | ❌ 미인증 | - | - |
| Anthropic| ✅ 활성 | (API Key) | 무제한 |
```

### 3.3 자동 토큰 갱신

```python
# 토큰 만료 7일 전 자동 갱신
if token.expires_in_days < 7:
    await refresh_token(provider)

# API 호출 시 만료 확인
async def call_api(provider, request):
    token = await get_valid_token(provider)  # 자동 갱신 포함
    return await make_request(token, request)
```

---

## 4. 구현 계획

### 4.1 디렉토리 구조

```
.claude/skills/multi-ai-auth/
├── SKILL.md                          # 스킬 메타데이터
├── scripts/
│   ├── __init__.py
│   ├── main.py                       # CLI 엔트리포인트
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── device_flow.py            # RFC 8628 구현
│   │   ├── pkce_flow.py              # PKCE + Local Callback
│   │   └── api_key_flow.py           # API Key 인증
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                   # 추상 Provider
│   │   ├── openai_provider.py        # OpenAI Codex
│   │   ├── google_provider.py        # Gemini
│   │   └── poe_provider.py           # Poe
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── token_store.py            # 토큰 저장/로드
│   │   └── encryption.py             # 암호화/복호화
│   └── utils/
│       ├── __init__.py
│       └── http_server.py            # 로컬 콜백 서버
├── tests/
│   ├── test_device_flow.py
│   ├── test_pkce_flow.py
│   └── test_providers.py
└── requirements.txt
```

### 4.2 핵심 클래스 설계

```python
# providers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AuthToken:
    access_token: str
    refresh_token: str | None
    expires_at: datetime
    provider: str
    scopes: list[str]

class BaseProvider(ABC):
    @abstractmethod
    async def login(self) -> AuthToken:
        """인증 수행"""
        pass

    @abstractmethod
    async def refresh(self, token: AuthToken) -> AuthToken:
        """토큰 갱신"""
        pass

    @abstractmethod
    async def logout(self, token: AuthToken) -> bool:
        """로그아웃"""
        pass

    @abstractmethod
    def is_valid(self, token: AuthToken) -> bool:
        """토큰 유효성 확인"""
        pass
```

### 4.3 구현 일정

| Phase | 작업 | 예상 시간 |
|:-----:|------|:--------:|
| 1 | 스킬 구조 생성 + SKILL.md | 30분 |
| 2 | Device Flow 구현 (OpenAI) | 2시간 |
| 3 | PKCE Flow 구현 (Google) | 2시간 |
| 4 | API Key Flow 구현 (Poe) | 1시간 |
| 5 | Token Store 구현 | 1시간 |
| 6 | CLI 인터페이스 통합 | 1시간 |
| 7 | 테스트 작성 | 1시간 |

**총 예상 시간**: 8-10시간

---

## 5. 보안 고려사항

### 5.1 토큰 보안

| 항목 | 구현 |
|------|------|
| **저장 암호화** | OS 자격증명 저장소 사용 |
| **메모리 보호** | SecureString 패턴 |
| **전송 암호화** | HTTPS only |
| **토큰 마스킹** | 로그에 토큰 미출력 |

### 5.2 위험 완화

| 위험 | 완화 방법 |
|------|----------|
| 토큰 유출 | 파일 권한 600, 암호화 저장 |
| 중간자 공격 | TLS 1.3 강제, 인증서 검증 |
| 세션 하이재킹 | state 파라미터 검증 |
| CSRF | PKCE code_verifier 사용 |

---

## 6. 테스트 계획

### 6.1 단위 테스트

```python
# tests/test_device_flow.py
async def test_device_code_request():
    """Device code 요청 테스트"""
    flow = DeviceFlow(client_id="test")
    response = await flow.request_device_code()
    assert "device_code" in response
    assert "user_code" in response

async def test_token_polling():
    """Token polling 테스트"""
    flow = DeviceFlow(client_id="test")
    # Mock authorization
    token = await flow.poll_for_token(device_code="test")
    assert token.access_token is not None
```

### 6.2 통합 테스트

| 테스트 | 검증 항목 |
|--------|----------|
| E2E Login | 전체 로그인 플로우 |
| Token Refresh | 자동 갱신 동작 |
| Multi-Provider | 여러 provider 동시 인증 |
| Error Handling | 네트워크 오류, 인증 실패 |

---

## 7. 의존성

### 7.1 Python 패키지

```txt
# requirements.txt
httpx>=0.27.0          # 비동기 HTTP 클라이언트
cryptography>=42.0.0   # 토큰 암호화
keyring>=25.0.0        # OS 자격증명 저장소
pydantic>=2.0.0        # 데이터 검증
rich>=13.0.0           # CLI 출력 포맷팅
```

### 7.2 외부 서비스

| 서비스 | 엔드포인트 | 용도 |
|--------|-----------|------|
| OpenAI Auth | auth.openai.com | Device Flow |
| Google OAuth | accounts.google.com | InstalledAppFlow |
| Poe API | api.poe.com | API Key 검증 |

---

## 8. 향후 확장

### 8.1 Phase 2 기능

- [ ] MCP 서버 통합 (Dynamic Client Registration)
- [ ] SSO (Single Sign-On) 지원
- [ ] 팀 계정 공유 (Enterprise)
- [ ] 토큰 사용량 모니터링

### 8.2 추가 Provider

- [ ] Azure OpenAI
- [ ] AWS Bedrock
- [ ] Hugging Face Hub
- [ ] Ollama (로컬)

---

## 9. 체크리스트

### 구현 체크리스트

- [ ] SKILL.md 작성
- [ ] Device Flow 구현 (OpenAI)
- [ ] PKCE Flow 구현 (Google)
- [ ] API Key Flow 구현 (Poe)
- [ ] Token Store 구현
- [ ] CLI 통합
- [ ] 테스트 작성
- [ ] 문서화

### 검증 체크리스트

- [ ] OpenAI 로그인 테스트
- [ ] Google 로그인 테스트
- [ ] Poe API Key 테스트
- [ ] 토큰 갱신 테스트
- [ ] 보안 검토

---

## 10. 참조

- [RFC 8628 - Device Authorization Grant](https://datatracker.ietf.org/doc/html/rfc8628)
- [OAuth 2.0 PKCE](https://oauth.net/2/pkce/)
- [OpenAI Codex CLI](https://github.com/openai/codex)
- [Google OAuth InstalledAppFlow](https://google-auth.readthedocs.io/)
- [Poe API Documentation](https://poe.com/api)
