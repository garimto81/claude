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

### 1. Ollama 설치

```powershell
winget install Ollama.Ollama
ollama pull qwen3:8b
ollama serve  # 별도 터미널
```

### 2. YouTube OAuth 2.0 설정 (필수)

```
1. https://console.cloud.google.com 접속
2. 프로젝트 생성 또는 선택
3. "API 및 서비스" → "라이브러리" → "YouTube Data API v3" 활성화
4. "API 및 서비스" → "사용자 인증 정보" → "OAuth 2.0 클라이언트 ID" 생성
   - 애플리케이션 유형: 웹 애플리케이션
   - 승인된 리디렉션 URI: http://localhost:3002/oauth/callback
5. 클라이언트 ID와 시크릿을 .env에 설정
```

## 아키텍처

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   YouTube   │◀────▶│   Chatbot   │────▶│   Ollama    │
│  Live Chat  │      │   Server    │      │  (Qwen 3)   │
│ (공식 API)  │      │ Port: 3002  │      │ Port: 11434 │
└─────────────┘      └─────────────┘      └─────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────┐
│   OAuth2    │      │   Token     │
│   Flow      │      │   Storage   │
└─────────────┘      └─────────────┘
```

### 핵심 컴포넌트

| 파일 | 역할 |
|------|------|
| `src/index.ts` | Express 서버 메인 엔트리 |
| `src/config/index.ts` | 호스트 프로필 로드/캐싱 |
| `src/services/oauth.ts` | OAuth 2.0 토큰 관리 |
| `src/services/youtube-chat.ts` | YouTube 공식 API 채팅 클라이언트 |
| `src/services/llm-client.ts` | Ollama + Qwen 3 클라이언트 |
| `src/services/rate-limiter.ts` | 응답 제한 (LRU Cache) |
| `src/handlers/message-router.ts` | 메시지 분류 및 라우팅 |
| `src/handlers/command.ts` | 동적 명령어 맵 생성 |
| `src/routes/api.ts` | REST API 엔드포인트 |

### 메시지 처리 파이프라인

```
1. OAuth 인증: /oauth/authorize → Google 로그인 → 토큰 저장
2. 채팅 수신: YouTube API → liveChatMessages.list (폴링) → ChatMessage
3. 메시지 분류: MessageRouter → LLMClient.classifyMessage()
   - question: LLM 응답 생성
   - greeting: 환영 메시지
   - command: 명령어 핸들러
   - chitchat: 일반 응답
   - spam: 무시
4. 응답 생성: Handler → Ollama (Qwen 3)
5. 응답 전송: liveChatMessages.insert → YouTube Chat
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

# YouTube OAuth 2.0 (필수)
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx
GOOGLE_REDIRECT_URI=http://localhost:3002/oauth/callback

# YouTube 자동 감지 (선택)
YOUTUBE_API_KEY=AIzaSyD...
YOUTUBE_CHANNEL_ID=UCxxxxxxxxxxxxxxxx

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

# 브라우저: OAuth 인증 (최초 1회)
# http://localhost:3002/oauth/authorize
```

## API 엔드포인트

### 챗봇 제어

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/start` | POST | 챗봇 시작 (videoId 또는 liveUrl) |
| `/api/stop` | POST | 챗봇 중지 |
| `/api/status` | GET | 연결 상태 조회 |
| `/api/stats` | GET | 통계 조회 |
| `/api/test-message` | POST | 테스트 메시지 (개발용) |

### OAuth 2.0

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/oauth/authorize` | GET | OAuth 인증 시작 (Google 리다이렉트) |
| `/oauth/callback` | GET | OAuth 콜백 (자동 처리) |
| `/oauth/status` | GET | 토큰 상태 확인 |
| `/oauth/refresh` | POST | 토큰 강제 갱신 |
| `/oauth/revoke` | POST | 토큰 삭제 (로그아웃) |

### Live 감지

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/live/detect` | GET | Live 방송 감지 |
| `/api/live/auto-start` | POST | Live 자동 감지 후 시작 |
| `/api/live/config` | GET | Live 감지 설정 상태 |

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
│   ├── oauth.test.ts              # OAuth 서비스 테스트
│   ├── prompt-builder.test.ts
│   ├── rate-limiter.test.ts
│   └── youtube-chat.test.ts       # YouTube Chat 테스트
└── utils/
    ├── message-parser.test.ts
    └── response-formatter.test.ts
```

## Quota 관리

| API 호출 | 예상 비용 | 빈도 |
|----------|----------|------|
| liveChatMessages.list | 5 units | 폴링마다 |
| liveChatMessages.insert | 50 units | 응답당 |
| videos.list | 1 unit | 시작 시 1회 |

**기본 할당량**: 10,000 units/일

**최적화 팁**:
- API 응답의 `pollingIntervalMillis` 값 사용 (동적 폴링 간격)
- 필요 시 [Quota Extension](https://support.google.com/youtube/contact/yt_api_form) 신청

## Qwen 3 모델 선택

| 모델 | VRAM | 추천 |
|------|------|------|
| `qwen3:4b` | 4GB | 저사양 PC |
| `qwen3:8b` | 8GB | **추천** |
| `qwen3:14b` | 12GB | 고품질 |

## 관련 문서

- PRD: `docs/PRD-0002-chatbot.md`
- GitHub: https://github.com/garimto81/youtuber_chatbot
