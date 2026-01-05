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
| `src/index.ts` | Express 서버 메인 엔트리, 초기화 순서 관리 |
| `src/config/index.ts` | 호스트 프로필 로드/캐싱 (싱글톤) |
| `src/config/host-profile.ts` | 프로필 로더, GitHub 프로젝트 병합 |
| `src/services/youtube-chat.ts` | masterchat 래퍼 (채팅 읽기/전송) |
| `src/services/llm-client.ts` | Ollama + Qwen 3 클라이언트 |
| `src/services/prompt-builder.ts` | 호스트 프로필 기반 시스템 프롬프트 생성 |
| `src/services/github-analyzer.ts` | GitHub API (REST + GraphQL) 연동 |
| `src/handlers/message-router.ts` | 메시지 분류 및 라우팅 |
| `src/handlers/command.ts` | 동적 명령어 맵 생성 (!help, !github 등) |
| `src/types/host.ts` | HostProfile, HostProject 타입 정의 |

### 메시지 처리 파이프라인

```
1. 채팅 수신: YouTube → masterchat → ChatMessage
2. 메시지 분류: MessageRouter → LLMClient.classifyMessage()
   - question: LLM 응답 생성
   - greeting: 랜덤 환영 메시지
   - command: 명령어 핸들러 (!help, !github 등)
   - chitchat: 랜덤 응답
   - spam: 무시
3. 응답 생성: Handler → Ollama (Qwen 3)
4. 응답 전송: masterchat → YouTube Chat
```

### 호스트 프로필 로딩 순서

`loadHostProfile()` 호출 시 다음 순서로 프로필을 탐색:
1. `HOST_PROFILE_JSON` 환경 변수 (JSON 문자열)
2. `HOST_PROFILE_PATH` 환경 변수 (파일 경로)
3. `config/host-profile.json` (기본 경로)
4. 환경 변수 개별 필드 조합 (fallback)

### 명령어 동적 생성

`buildCommandMap()` 함수가 호스트 프로필을 기반으로 명령어 맵 생성:
- 기본 명령어: `!help`, `!github`, `!ai`, `!projects`, `!sync-repos`
- 프로젝트별 명령어: `!{project.id}` (예: `!claude`, `!youtuber`)

## 환경 변수

```env
PORT=3002                              # 서버 포트
OLLAMA_BASE_URL=http://localhost:11434 # Ollama 서버 URL
OLLAMA_MODEL=qwen3:8b                  # 사용할 모델
MAX_RESPONSE_LENGTH=200                # 최대 응답 길이

# YouTube Chat (선택 - 둘 중 하나)
YOUTUBE_VIDEO_ID=dQw4w9WgXcQ
YOUTUBE_LIVE_URL=https://www.youtube.com/watch?v=...

# GitHub 동기화 (선택)
GITHUB_TOKEN=ghp_xxxxx                 # API 토큰
GITHUB_AUTO_SYNC=true                  # 시작 시 자동 동기화
GITHUB_ACTIVITY_DAYS=5                 # 최근 N일 활동 기준

# 호스트 프로필 (선택)
HOST_PROFILE_PATH=config/host-profile.json
```

## 실행 순서

```powershell
# 터미널 1: Ollama 서버
ollama serve

# 터미널 2: 메인 서버 (선택)
cd C:\claude\youtuber
npm run dev

# 터미널 3: 챗봇 서버
cd C:\claude\youtuber_chatbot
npm run dev
```

## 테스트 구조

```
tests/
├── handlers/
│   ├── command.test.ts         # 동적 명령어 맵 테스트
│   └── message-router.test.ts  # 메시지 라우팅 테스트
├── loaders/
│   └── host-profile.test.ts    # 프로필 로더 테스트
└── services/
    ├── github-analyzer.test.ts # GitHub API 테스트
    ├── llm-client.test.ts      # Ollama 클라이언트 테스트
    ├── prompt-builder.test.ts  # 프롬프트 생성 테스트
    └── youtube-chat.test.ts    # masterchat 래퍼 테스트
```

테스트는 `vi.mock()`으로 외부 의존성 (ollama, config 모듈) 모킹.

## Qwen 3 모델 선택

| 모델 | VRAM | 추천 |
|------|------|------|
| `qwen3:4b` | 4GB | 저사양 PC |
| `qwen3:8b` | 8GB | **추천** |
| `qwen3:14b` | 12GB | 고품질 |

## 관련 문서

- PRD: `docs/PRD-0002-chatbot.md`
- 메인 프로젝트: `C:\claude\youtuber`
