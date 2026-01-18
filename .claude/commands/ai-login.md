---
name: ai-login
description: AI 서비스 인증 설정 (GPT, Gemini)
---

# /ai-login - AI 서비스 인증 설정

GPT 및 Gemini 사용을 위한 인증 설정을 안내합니다.

## 사용법

```bash
/ai-login openai    # OpenAI Browser OAuth 로그인 (ChatGPT Plus/Pro)
/ai-login google    # Google OAuth 브라우저 로그인
/ai-login status    # 인증 상태 확인
/ai-login logout    # 모든 세션 로그아웃
```

---

## 실행 지시

$ARGUMENTS를 파싱하여 해당 Provider의 인증 설정을 실행하세요.

### 파라미터 매핑

| 입력 | 동작 |
|------|------|
| `openai` 또는 `gpt` | OpenAI Browser OAuth 로그인 (ChatGPT Plus/Pro) |
| `google` 또는 `gemini` | Google Browser OAuth 로그인 |
| `status` | 인증 상태 확인 |
| `logout` | 모든 토큰 삭제 |

---

## [OpenAI 설정] /ai-login openai

### 인증 방식: Browser OAuth (ChatGPT Plus/Pro)

OpenAI OAuth를 통해 ChatGPT Plus/Pro 구독 계정으로 인증합니다.
Claude Code `/login`과 동일한 브라우저 기반 인증 방식입니다.

### 로그인 프로세스 (자동)

다음 Python 스크립트를 실행하세요:

```python
import asyncio
import sys
sys.path.insert(0, "ultimate-debate/src")

from ultimate_debate.auth.providers import OpenAIProvider
from ultimate_debate.auth.storage import TokenStore

async def login_openai():
    provider = OpenAIProvider()
    storage = TokenStore()

    print('[INFO] OpenAI Browser OAuth login starting...')
    print('       Using Codex CLI compatible settings')
    print('       Browser will open automatically.')
    print()

    try:
        # 자동 콜백 시도 → 실패 시 수동 모드로 전환
        token = await provider.login()
        await storage.save(token)

        info = await provider.get_account_info(token)
        email = info.get('email', 'Unknown') if info else 'Unknown'

        print()
        print('[SUCCESS] OpenAI login successful!')
        print(f'   Account: {email}')
        print(f'   Expires: {token.expires_at.strftime("%Y-%m-%d %H:%M")}')
        return True
    except Exception as e:
        print()
        print(f'[ERROR] Login failed: {e}')
        return False

asyncio.run(login_openai())
```

### 인증 흐름

1. **자동 모드 시도** (60초 대기)
   - 브라우저에서 OpenAI 로그인
   - localhost:1455로 자동 콜백 수신

2. **수동 모드 전환** (자동 실패 시)
   - 브라우저에서 리디렉션된 URL 복사
   - 터미널에 URL 붙여넣기
   - code/state 추출하여 토큰 교환

### 출력 형식

```markdown
## OpenAI 브라우저 로그인

[INFO] OpenAI Browser OAuth login starting...
       Browser will open automatically.

[자동 모드 성공 시]
[OK] 인증 코드 수신 완료!
[OK] 인증 성공!

[수동 모드 전환 시]
[WARN] 자동 콜백 수신 실패. 수동 모드로 전환합니다.
[수동 OAuth 인증 모드]
1. 브라우저에서 로그인
2. 리디렉션된 URL 복사
3. 터미널에 붙여넣기

[SUCCESS] OpenAI login successful!
   Account: user@example.com
   Expires: 2026-01-19 10:00

---

**이제 `/verify --provider openai`로 GPT 검증을 사용할 수 있습니다!**
```

---

## [Google 로그인] /ai-login google

### 사전 설정 (최초 1회)

Google Gemini OAuth에는 Client ID 설정이 필요합니다:

1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials) 접속
2. 프로젝트 선택 또는 생성
3. "OAuth 클라이언트 ID 만들기" 클릭
4. 애플리케이션 유형: **데스크톱 앱**
5. 생성된 Client ID와 Secret을 환경변수로 설정:

```powershell
# PowerShell (영구 설정)
[System.Environment]::SetEnvironmentVariable("GOOGLE_CLIENT_ID", "<YOUR_CLIENT_ID>.apps.googleusercontent.com", "User")
[System.Environment]::SetEnvironmentVariable("GOOGLE_CLIENT_SECRET", "<YOUR_CLIENT_SECRET>", "User")
```

> ⚠️ **보안 주의사항**
> - Client Secret은 민감한 정보입니다
> - 절대 Git에 커밋하지 마세요
> - 권장: `.env` 파일 사용 후 `.gitignore`에 등록

6. Gemini API 활성화: [Generative Language API](https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com)

### 로그인 프로세스 (자동)

다음 Python 스크립트를 실행하세요:

```python
import asyncio
import sys
sys.path.insert(0, "ultimate-debate/src")

from ultimate_debate.auth.providers import GoogleProvider
from ultimate_debate.auth.storage import TokenStore

async def login_google():
    provider = GoogleProvider()
    storage = TokenStore()

    print('[INFO] Google Browser OAuth login starting...')
    print('       Browser will open automatically.')
    print('       Please login with Google account.')
    print()

    try:
        token = await provider.login()
        await storage.save(token)

        info = await provider.get_account_info(token)
        email = info.get('email', 'Unknown') if info else 'Unknown'

        print()
        print('[SUCCESS] Google login successful!')
        print(f'   Account: {email}')
        print(f'   Expires: {token.expires_at.strftime("%Y-%m-%d %H:%M")}')
        return True
    except Exception as e:
        print()
        print(f'[ERROR] Login failed: {e}')
        return False

asyncio.run(login_google())
```

### 출력 형식

```markdown
## Google 브라우저 로그인

[INFO] Google Browser OAuth login starting...
       Browser will open automatically.

[SUCCESS] Google login successful!
   Account: user@gmail.com
   Expires: 2026-01-19 10:00

---

**이제 `/verify --provider gemini`로 Gemini 검증을 사용할 수 있습니다!**
```

---

## [상태 확인] /ai-login status

인증 상태를 확인하세요:

```python
import sys
import os
sys.path.insert(0, "ultimate-debate/src")

from ultimate_debate.auth.storage import TokenStore

storage = TokenStore()

print("## AI Authentication Status")
print()
print("| Provider | Method | Status |")
print("|----------|--------|--------|")

# OpenAI - OAuth 토큰 확인
openai_token = storage.get_valid_token("openai")
if openai_token:
    expires = openai_token.expires_at.strftime("%Y-%m-%d %H:%M")
    print(f"| OpenAI | OAuth | [OK] Expires {expires} |")
else:
    print("| OpenAI | OAuth | [X] Not logged in |")

# Google - OAuth 토큰 확인
google_token = storage.get_valid_token("google")
if google_token:
    expires = google_token.expires_at.strftime("%Y-%m-%d %H:%M")
    print(f"| Google | OAuth | [OK] Expires {expires} |")
else:
    print("| Google | OAuth | [X] Not logged in |")
```

### 출력 형식

```markdown
## AI Authentication Status

| Provider | Method | Status |
|----------|--------|--------|
| OpenAI | OAuth | [X] Not logged in |
| Google | OAuth | [X] Not logged in |

---

**설정 필요:**
- `/ai-login openai` - OpenAI OAuth 로그인
- `/ai-login google` - Google OAuth 로그인
```

---

## [로그아웃] /ai-login logout

모든 저장된 토큰을 삭제합니다:

```python
import asyncio
import sys
sys.path.insert(0, "ultimate-debate/src")

from ultimate_debate.auth.storage import TokenStore

async def logout_all():
    storage = TokenStore()
    await storage.clear_all()
    print("[OK] All AI sessions logged out.")

asyncio.run(logout_all())
```

---

## 인증 방식 비교

| Provider | 방식 | 설정 난이도 | 비용 |
|----------|------|------------|------|
| **OpenAI** | Browser OAuth (PKCE) | 중간 (수동 모드 필요) | ChatGPT Plus/Pro 구독 |
| **Google** | Browser OAuth (PKCE) | 중간 (Client ID 필요) | 무료 (할당량 내) |

---

## 관련 커맨드

| 커맨드 | 용도 |
|--------|------|
| `/verify` | Cross-AI 코드 검증 실행 |
| `/auto` | 자동 워크플로우 (자동 검증 포함) |

---

## 문제 해결

### OpenAI

| 증상 | 해결 |
|------|------|
| "자동 콜백 수신 실패" | 수동 모드에서 URL 복사/붙여넣기 |
| "인증 시간 초과" | 브라우저에서 빠르게 로그인 후 URL 복사 |
| "토큰 교환 실패" | ChatGPT Plus/Pro 구독 확인 |
| "권한 없음" | ChatGPT Plus/Pro 구독 필요 |

### Google

| 증상 | 해결 |
|------|------|
| "Client ID 필요" | 환경변수 GOOGLE_CLIENT_ID 설정 |
| "권한 오류" | OAuth 동의 화면에서 테스트 사용자 추가 |
| API 오류 | Generative Language API 활성화 확인 |
