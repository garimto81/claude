---
name: "Multi-AI Authentication"
description: "GPT, Gemini, Poe 등 외부 AI 서비스 OAuth 인증 통합 관리"
version: "1.0.0"
author: "Claude Code"
---

# Multi-AI Authentication Skill

Claude Code에서 외부 AI 모델(GPT, Gemini, Poe)에 `/login` 스타일로 인증하는 스킬입니다.

## 사용법

```bash
# 로그인
/ai-auth login --provider openai    # OpenAI OAuth (Device Flow)
/ai-auth login --provider google    # Google OAuth (InstalledAppFlow)
/ai-auth login --provider poe       # Poe API Key

# 상태 확인
/ai-auth status

# 로그아웃
/ai-auth logout --provider openai
/ai-auth logout --all
```

## 지원 Provider

| Provider | 인증 방식 | 구독 모델 접근 |
|----------|----------|:-------------:|
| **OpenAI** | Device Authorization Grant (RFC 8628) | ChatGPT Plus |
| **Google** | OAuth 2.0 InstalledAppFlow | Gemini API |
| **Poe** | API Key | 100+ 모델 |

## 설치

```bash
pip install -r requirements.txt
```

## 환경 변수 (선택)

```bash
# Poe API Key (선택)
export POE_API_KEY="your-api-key"

# Google OAuth Client (선택)
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
```

## 보안

- 토큰은 OS 자격증명 저장소에 암호화 저장
- Windows: DPAPI
- macOS: Keychain
- Linux: libsecret

## 관련 문서

- [PRD-0031](../../../tasks/prds/PRD-0031-multi-ai-auth-skill.md)
