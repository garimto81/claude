# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

> **이 프로젝트는 YouTube 채팅만 전담합니다.**

YouTube Live Chat AI 챗봇 - **Ollama + Qwen 3** 기반으로 시청자 질문에 응답하고, 명령어를 처리하는 독립 서버입니다.

### 역할 (Scope)

| 포함 | 제외 |
|------|------|
| YouTube 채팅 수신/전송 | 메인 서버 연동 |
| AI 질문 응답 | VTuber/버튜버 연동 |
| 명령어 처리 | OBS 오버레이 |
| 호스트 프로필 관리 | 방송 세션 관리 |

## 빌드/테스트 명령

```powershell
npm install              # 의존성 설치
npm run dev              # 개발 서버 (tsx watch, 핫 리로드)
npm run build            # TypeScript 빌드
npm run start            # 프로덕션 서버 실행
npm run lint             # ESLint 검사
npm run lint:fix         # ESLint 자동 수정
npm run test             # Vitest 전체 실행
npm run test:watch       # Vitest 워치 모드
```

### 개별 테스트 실행

```powershell
npx vitest run tests/services/llm-client.test.ts     # 특정 파일
npx vitest run -t "generateResponse"                  # 특정 테스트명
npx vitest run tests/handlers/                        # 디렉토리 전체
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
└─────────────┘      └─────────────┘      └─────────────┘
```

### 핵심 컴포넌트

| 파일 | 역할 |
|------|------|
| `src/index.ts` | Express 서버 메인 엔트리 |
| `src/config/index.ts` | 호스트 프로필 로드/캐싱 |
| `src/services/youtube-chat.ts` | masterchat 래퍼 (채팅 읽기/전송) |
| `src/services/llm-client.ts` | Ollama + Qwen 3 클라이언트 |
| `src/services/rate-limiter.ts` | 응답 제한 (LRU Cache) |
| `src/handlers/message-router.ts` | 메시지 분류 및 라우팅 |
| `src/handlers/command.ts` | 동적 명령어 맵 생성 |
| `src/routes/api.ts` | REST API 엔드포인트 |

### 메시지 처리 파이프라인

```
1. 채팅 수신: YouTube → masterchat → ChatMessage
2. 메시지 분류: MessageRouter → LLMClient.classifyMessage()
   - question: LLM 응답 생성
   - greeting: 환영 메시지
   - command: 명령어 핸들러
   - chitchat: 일반 응답
   - spam: 무시
3. 응답 생성: Handler → Ollama (Qwen 3)
4. 응답 전송: masterchat → YouTube Chat
```

### 명령어 동적 생성

`buildCommandMap()` 함수가 호스트 프로필 기반으로 명령어 맵 생성:
- 기본: `!help`, `!github`, `!ai`, `!projects`, `!sync-repos`
- 프로젝트별: `!{project.id}`

## 환경 변수

```env
PORT=3002                              # 서버 포트
OLLAMA_BASE_URL=http://localhost:11434 # Ollama 서버 URL
OLLAMA_MODEL=qwen3:8b                  # 사용할 모델
MAX_RESPONSE_LENGTH=200                # 최대 응답 길이

# YouTube Chat (선택)
YOUTUBE_VIDEO_ID=dQw4w9WgXcQ

# GitHub 동기화 (선택)
GITHUB_TOKEN=ghp_xxxxx
GITHUB_AUTO_SYNC=false
GITHUB_ACTIVITY_DAYS=5

# 호스트 프로필 (선택)
HOST_PROFILE_PATH=config/host-profile.json
```

## 실행 순서

```powershell
# 터미널 1: Ollama 서버
ollama serve

# 터미널 2: 챗봇 서버
cd C:\claude\youtuber_chatbot
npm run dev
```

## 테스트 구조

```
tests/
├── config/
│   └── index.test.ts              # 설정 모듈 테스트
├── handlers/
│   ├── command.test.ts            # 명령어 테스트
│   └── message-router.test.ts     # 라우팅 테스트
├── routes/
│   └── api.test.ts                # API 엔드포인트 테스트
├── services/
│   ├── github-analyzer.test.ts
│   ├── llm-client.test.ts
│   ├── prompt-builder.test.ts
│   ├── rate-limiter.test.ts
│   └── youtube-chat.test.ts
└── utils/
    ├── message-parser.test.ts
    └── response-formatter.test.ts
```

현재 테스트: **163개** (12 파일)

## Qwen 3 모델 선택

| 모델 | VRAM | 추천 |
|------|------|------|
| `qwen3:4b` | 4GB | 저사양 PC |
| `qwen3:8b` | 8GB | **추천** |
| `qwen3:14b` | 12GB | 고품질 |

## 관련 문서

- PRD: `docs/PRD-0002-chatbot.md`
- GitHub: https://github.com/garimto81/youtuber_chatbot
