# Multi-AI Auth 통합 가이드

Cross-AI Verifier와 Multi-AI Auth Skill 통합 방법

## 개요

ProviderRouter는 Multi-AI Auth의 TokenStore를 통해 OAuth 토큰을 자동으로 관리합니다.

## 사용 방법

### 1. 기본 모드 (OAuth 우선, API 키 fallback)

```python
from providers.router import ProviderRouter

router = ProviderRouter()
result = await router.verify(code, "openai", prompt)
# 1. TokenStore에서 OAuth 토큰 조회
# 2. 토큰이 없으면 환경변수 (OPENAI_API_KEY) 사용
```

### 2. 인증 강제 모드 (OAuth 토큰 필수)

```python
router = ProviderRouter(require_auth=True)

# 토큰 없으면 에러 발생 + 로그인 안내
await router.ensure_authenticated("openai")
# ❌ OPENAI 인증이 필요합니다.
#    다음 명령어로 로그인하세요:
#    /ai-auth login --provider openai

result = await router.verify(code, "openai", prompt)
```

## 구현 상세

### TokenStore Import 경로

```python
# 절대 경로로 안정적인 import
.claude/skills/cross-ai-verifier/
└── scripts/providers/router.py
    └── imports from: .claude/skills/multi-ai-auth/scripts/storage/token_store.py
```

### 주요 메서드

| 메서드 | 역할 |
|--------|------|
| `__init__(require_auth: bool)` | 인증 강제 모드 설정 |
| `ensure_authenticated(provider)` | 토큰 확인 + 로그인 안내 |
| `_get_token(provider)` | TokenStore에서 토큰 조회 |

### 에러 메시지

```
❌ OPENAI 인증이 필요합니다.
   다음 명령어로 로그인하세요:
   /ai-auth login --provider openai
```

## 하위 호환성

기존 코드는 `require_auth=False`가 기본값이므로 그대로 동작합니다.

```python
# 기존 코드 (그대로 동작)
router = ProviderRouter()
result = await router.verify(code, "openai", prompt)
```

## 의존성

- Multi-AI Auth Skill이 설치되지 않으면 `HAS_TOKEN_STORE=False`로 동작
- `require_auth=True`는 TokenStore가 없으면 RuntimeError 발생
