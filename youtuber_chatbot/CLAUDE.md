# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

YouTube Live Chat AI 챗봇 - **Ollama + Qwen 3** 기반으로 시청자 질문에 응답하고, 방송 정보를 제공하며, 명령어를 처리하는 독립 서버입니다.

## 빌드/테스트 명령

```powershell
npm install              # 의존성 설치
npm run dev              # 개발 서버 (tsx watch, 핫 리로드)
npm run build            # TypeScript 빌드
npm run start            # 프로덕션 서버 실행
npm run lint             # ESLint 검사
npm run test             # Vitest 실행
```

## 사전 요구사항

```powershell
# 1. Ollama 설치
winget install Ollama.Ollama

# 2. Qwen 3 모델 다운로드
ollama pull qwen3:8b

# 3. Ollama 서버 실행 (별도 터미널)
ollama serve
```

## 아키텍처

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   YouTube   │◀────▶│   Chatbot   │────▶│   Ollama    │
│  Live Chat  │      │   Server    │      │  (Qwen 3)   │
│ (masterchat)│      │ Port: 3002  │      │ Port: 11434 │
└─────────────┘      └──────┬──────┘      └─────────────┘
                           │ HTTP              (로컬)
                           ▼
                    ┌─────────────┐
                    │ Main Server │
                    │ Port: 3001  │
                    └─────────────┘
```

### 핵심 컴포넌트

| 파일 | 역할 |
|------|------|
| `src/index.ts` | Express 서버 메인 엔트리 |
| `src/services/youtube-chat.ts` | masterchat 래퍼 (채팅 읽기/전송) |
| `src/services/llm-client.ts` | Ollama + Qwen 3 클라이언트 |
| `src/services/main-server.ts` | 메인 서버(3001) HTTP 클라이언트 |
| `src/handlers/message-router.ts` | 메시지 분류 및 라우팅 |
| `src/handlers/command.ts` | 명령어 처리 (!help, !project 등) |
| `src/types/index.ts` | TypeScript 타입 정의 |

### 데이터 흐름

1. **채팅 수신**: YouTube → masterchat → Message Queue
2. **메시지 분류**: Router → Qwen 3 분류 (question/greeting/command)
3. **응답 생성**: Handler → Ollama (Qwen 3) → Rate Limiter
4. **응답 전송**: masterchat → YouTube Chat

### 명령어

| 명령어 | 설명 |
|--------|------|
| `!help` | 사용 가능한 명령어 목록 |
| `!project` | 현재 작업 프로젝트 정보 |
| `!status` | TDD 상태 (Red/Green/Refactor) |
| `!time` | 방송 경과 시간 |
| `!github` | GitHub 링크 |
| `!ai` | AI 모델 정보 |

## 환경 변수

```env
PORT=3002                              # 서버 포트
OLLAMA_BASE_URL=http://localhost:11434 # Ollama 서버 URL
OLLAMA_MODEL=qwen3:8b                  # 사용할 모델
MAIN_SERVER_URL=http://localhost:3001  # 메인 서버 URL
BOT_NAME=CodingBot                     # 챗봇 이름
```

## 실행 순서

```powershell
# 터미널 1: Ollama 서버
ollama serve

# 터미널 2: 메인 서버 (선택)
cd D:\AI\claude01\youtuber
npm run dev

# 터미널 3: 챗봇 서버
cd D:\AI\claude01\youtuber\chatbot
npm run dev
```

## Qwen 3 모델 선택

| 모델 | VRAM | 추천 |
|------|------|------|
| `qwen3:4b` | 4GB | 저사양 PC |
| `qwen3:8b` | 8GB | **추천** |
| `qwen3:14b` | 12GB | 고품질 |

## 관련 문서

- PRD: `docs/PRD-0002-chatbot.md`
- 메인 프로젝트: `D:\AI\claude01\youtuber\`
