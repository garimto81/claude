# PRD-0002: YouTube 채팅 AI 챗봇

**버전**: 3.1.0
**작성일**: 2026-01-05
**상태**: Active

---

## 1. 개요

### 1.1 목적

YouTube Live 채팅에서 시청자와 실시간으로 상호작용하는 **독립 AI 챗봇 서버**를 구축합니다.

### 1.2 역할 (Scope)

> **이 프로젝트는 YouTube 채팅만 전담합니다.**

| 포함 | 제외 |
|------|------|
| YouTube 채팅 수신/전송 | 메인 서버 연동 |
| AI 질문 응답 (Ollama + Qwen 3) | VTuber/버튜버 연동 |
| 명령어 처리 (`!help`, `!ai` 등) | OBS 오버레이 |
| 인사/환영 메시지 | 방송 세션 관리 |
| 호스트 프로필 관리 | GitHub Webhook |

### 1.3 핵심 기능

1. **시청자 질문 응답** - 프로그래밍/코딩 질문에 Qwen 3 AI가 답변
2. **명령어 처리** - `!help`, `!ai`, `!projects` 등 커맨드 처리
3. **인사/환영 메시지** - 인사 자동 응답
4. **호스트 정보 제공** - 프로젝트, GitHub 정보

### 1.4 Ollama + Qwen 3 선택 이유

| 항목 | 장점 |
|------|------|
| **비용** | 완전 무료 (로컬 실행) |
| **속도** | 네트워크 지연 없음 |
| **프라이버시** | 데이터 외부 전송 없음 |
| **오프라인** | 인터넷 없이 동작 |
| **한국어** | Qwen 3는 119개 언어 지원 |

---

## 2. 시스템 아키텍처

### 2.1 구성도 (단순화)

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   YouTube   │◀────▶│   Chatbot   │────▶│   Ollama    │
│  Live Chat  │      │   Server    │      │  (Qwen 3)   │
│ (masterchat)│      │ Port: 3002  │      │ Port: 11434 │
└─────────────┘      └─────────────┘      └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Host Profile│
                    │   (JSON)    │
                    └─────────────┘
```

### 2.2 데이터 흐름

| 이벤트 | 흐름 | 결과 |
|--------|------|------|
| 채팅 수신 | YouTube → masterchat → Chatbot | 메시지 파싱 |
| AI 응답 | 질문 → Ollama(Qwen3) → YouTube | 답변 전송 |
| 명령어 | `!help` → 내부 처리 → YouTube | 즉시 응답 |

---

## 3. 기술 스택

| 영역 | 기술 | 버전 |
|------|------|------|
| 런타임 | Node.js | 20 LTS |
| 언어 | TypeScript | 5.x |
| HTTP 서버 | Express | 4.x |
| YouTube | @stu43005/masterchat | 최신 |
| AI | Ollama (Qwen 3) | 최신 |
| 테스트 | Vitest | 최신 |

### 3.1 Qwen 3 모델 선택 가이드

| 모델 | VRAM | 추천 |
|------|------|------|
| `qwen3:4b` | 4GB | 저사양 PC |
| `qwen3:8b` | 8GB | **추천** |
| `qwen3:14b` | 12GB | 고품질 |

---

## 4. 프로젝트 구조

```
youtuber_chatbot/
├── docs/
│   └── PRD-0002-chatbot.md     # 이 문서
├── config/
│   ├── host-profile.json       # 호스트 정보
│   └── host-profile.example.json
├── src/
│   ├── index.ts                # 메인 엔트리포인트
│   ├── config/
│   │   ├── index.ts            # 환경변수 로드
│   │   └── host-profile.ts     # 프로필 로더
│   ├── services/
│   │   ├── youtube-chat.ts     # masterchat 래퍼
│   │   ├── llm-client.ts       # Ollama 클라이언트
│   │   ├── prompt-builder.ts   # 시스템 프롬프트 생성
│   │   ├── github-analyzer.ts  # GitHub API
│   │   └── rate-limiter.ts     # 응답 제한
│   ├── handlers/
│   │   ├── message-router.ts   # 메시지 분류/라우팅
│   │   └── command.ts          # 명령어 처리
│   ├── routes/
│   │   └── api.ts              # REST API
│   ├── types/
│   │   └── host.ts             # 호스트 타입
│   └── utils/
│       ├── message-parser.ts
│       ├── response-formatter.ts
│       └── logger.ts
├── tests/
├── package.json
├── tsconfig.json
├── .env.example
└── CLAUDE.md
```

---

## 5. API 엔드포인트 (Port 3002)

| 경로 | 메서드 | 용도 |
|------|--------|------|
| `/health` | GET | 서버 상태 |
| `/api/start` | POST | 챗봇 시작 (videoId) |
| `/api/stop` | POST | 챗봇 중지 |
| `/api/status` | GET | 연결 상태 |
| `/api/stats` | GET | 통계 |
| `/api/test-message` | POST | 테스트 메시지 |
| `/api/ollama/status` | GET | Ollama 연결 상태 |
| `/api/live/detect` | GET | 현재 Live 방송 감지 |
| `/api/live/auto-start` | POST | Live 감지 후 자동 시작 |
| `/api/live/config` | GET | Live 감지 설정 상태 |

---

## 6. 환경 변수

```env
# 서버
PORT=3002

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# YouTube Chat (수동 - 둘 중 하나만 설정)
YOUTUBE_VIDEO_ID=dQw4w9WgXcQ
# 또는
YOUTUBE_LIVE_URL=https://www.youtube.com/watch?v=...

# YouTube 자동 감지 (권장)
YOUTUBE_API_KEY=AIza...          # Google Cloud Console에서 발급
YOUTUBE_CHANNEL_ID=UC...         # 채널 ID (UC로 시작)

# YouTube 인증 쿠키 (채팅 전송에 필요)
# 브라우저 개발자도구 → Application → Cookies → youtube.com 에서 복사
YT_SAPISID=...
YT_APISID=...
YT_HSID=...
YT_SID=...
YT_SSID=...

# 챗봇
MAX_RESPONSE_LENGTH=200

# GitHub (선택)
GITHUB_TOKEN=ghp_xxxxx
GITHUB_AUTO_SYNC=false
GITHUB_ACTIVITY_DAYS=5

# 호스트 프로필 (선택)
HOST_PROFILE_PATH=config/host-profile.json
```

> ⚠️ **채팅 전송 제한**: 쿠키 기반 인증은 YouTube 보안 정책으로 인해 불안정할 수 있습니다. 안정적인 채팅 전송이 필요하면 [OAuth 2.0 (공식 API)](https://developers.google.com/youtube/v3/live/docs/liveChatMessages/insert) 사용을 권장합니다.

---

## 7. 명령어

| 명령어 | 설명 |
|--------|------|
| `!help` | 사용 가능한 명령어 목록 |
| `!ai` | AI 모델 정보 |
| `!github` | GitHub 링크 |
| `!projects` | 활성 프로젝트 목록 |
| `!sync-repos` | GitHub Pinned repos 동기화 |
| `!{project-id}` | 특정 프로젝트 정보 |

---

## 8. 메시지 처리 흐름

```
YouTube Chat ──▶ masterchat ──▶ Message Router
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                    Command?               AI 분류
                         │            (question/greeting/
                         │             chitchat/spam)
                         ▼                     │
                   Command Handler             ▼
                         │             Ollama (Qwen 3)
                         └──────────┬──────────┘
                                    ▼
                              Rate Limiter
                                    │
                                    ▼
                         YouTube Chat (응답)
```

---

## 9. Rate Limiting

| 제한 | 값 |
|------|-----|
| 분당 응답 | 30회 |
| 시간당 응답 | 500회 |
| 사용자별 쿨다운 | 5초 |
| 최대 추적 사용자 | 10,000명 |

---

## 10. 호스트 프로필

### 10.1 설정 방법

```bash
cp config/host-profile.example.json config/host-profile.json
```

### 10.2 필수 항목

```json
{
  "host": {
    "name": "닉네임",
    "displayName": "표시 이름"
  },
  "social": {
    "github": "username"
  },
  "projects": [
    {
      "id": "project-id",
      "name": "프로젝트 이름",
      "description": "설명"
    }
  ]
}
```

### 10.3 GitHub 자동 동기화

- `!sync-repos` 명령어로 Pinned repos 동기화
- `GITHUB_AUTO_SYNC=true` 설정 시 시작 시 자동 동기화

---

## 11. 실행 순서

```powershell
# 터미널 1: Ollama 서버
ollama serve

# 터미널 2: 챗봇 서버
cd C:\claude\youtuber_chatbot
npm run dev
```

---

## 12. 테스트

```powershell
# 전체 테스트
npm run test

# 특정 파일
npx vitest run tests/services/llm-client.test.ts
```

현재 테스트: **163개** (12 파일)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-04 | 초안 작성 |
| 2.0.0 | 2026-01-04 | 호스트 정보 관리 시스템 |
| 2.1.0 | 2026-01-04 | 최근 활동 프로젝트 조회 |
| 3.0.0 | 2026-01-05 | 역할 축소: 채팅 전담 프로젝트 |
| **3.1.0** | **2026-01-05** | **YouTube Live 자동 감지 및 인증**<br/>- Live 방송 자동 감지 (`/api/live/detect`)<br/>- YouTube 쿠키 인증 지원<br/>- 에러 핸들링 개선<br/>- dotenv 설정 추가 |

---

## 아카이브

이전 버전의 메인 서버 연동, VTuber 관련 기능은 `docs/archive/` 폴더에 보관됩니다.
