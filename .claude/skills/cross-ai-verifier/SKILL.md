---
name: "Cross-AI Verifier"
description: "다중 AI 모델을 통한 코드 검증 (OpenAI + Gemini)"
version: "1.0.0"
author: "Claude Code"
---

# Cross-AI Verifier Skill

Claude가 작성한 코드를 외부 AI(GPT, Gemini)가 교차 검증합니다.

## 사용법

```bash
# 단일 Provider 검증
/verify src/auth.py --focus security --provider openai
/verify tests/ --focus bugs --provider gemini

# 병렬 검증 (OpenAI + Gemini 동시)
/verify --all src/ --parallel
```

## 지원 Provider

| Provider | 모델 | 인증 |
|----------|------|------|
| **OpenAI** | GPT-4 | multi-ai-auth 토큰 또는 OPENAI_API_KEY |
| **Gemini** | Gemini Pro | multi-ai-auth 토큰 또는 GEMINI_API_KEY |

## 검증 Focus

| Focus | 설명 |
|-------|------|
| `security` | 보안 취약점 분석 (SQL Injection, XSS 등) |
| `bugs` | 논리 오류 및 버그 검사 |
| `performance` | 성능 이슈 및 최적화 제안 |
| `all` | 종합 코드 리뷰 |

## 설치

```bash
cd .claude/skills/cross-ai-verifier
pip install -r requirements.txt
```

## 환경 변수 (선택)

```bash
# multi-ai-auth 토큰이 없는 경우
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
```

## 관련 문서

- [Multi-AI Auth Skill](../multi-ai-auth/SKILL.md)
- [PRD-0031](../../../tasks/prds/PRD-0031-multi-ai-auth-skill.md)
