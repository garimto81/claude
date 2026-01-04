# YouTube Live Chat AI Chatbot

**버전**: 1.0.0
**기반**: Ollama + Qwen 3
**용도**: YouTube 방송 실시간 채팅 AI 챗봇

---

## 개요

AI Coding YouTube 방송에서 시청자와 실시간 상호작용하는 지능형 챗봇입니다.

### 주요 기능

- **시청자 질문 응답**: Qwen 3 AI가 프로그래밍 질문에 답변
- **방송 정보 제공**: 현재 프로젝트, 세션 시간, TDD 상태
- **명령어 처리**: `!help`, `!project`, `!status` 등
- **인사/환영 메시지**: 첫 입장 시 자동 환영

---

## 시스템 요구사항

| 항목 | 요구사항 |
|------|----------|
| Node.js | 20 LTS 이상 |
| Ollama | 최신 버전 |
| VRAM | 8GB 이상 (qwen3:8b 기준) |
| OS | Windows, macOS, Linux |

---

## 설치 및 실행

### 1. Ollama 설치

```powershell
# Windows
winget install Ollama.Ollama

# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Qwen 3 모델 다운로드

```powershell
ollama pull qwen3:8b
```

### 3. 프로젝트 설정

```powershell
# 의존성 설치
npm install

# 환경 변수 설정
copy .env.example .env
# .env 파일을 열어 필요한 값 수정

# Ollama 서버 실행 (별도 터미널)
ollama serve
```

### 4. 개발 실행

```powershell
# 개발 모드 (핫 리로드)
npm run dev

# 프로덕션 빌드
npm run build
npm run start
```

---

## 환경 변수

```env
# 서버 설정
PORT=3002
HOST=localhost

# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# 메인 서버 연결 (선택)
MAIN_SERVER_URL=http://localhost:3001

# 챗봇 설정
BOT_NAME=CodingBot
RESPONSE_DELAY_MS=500
MAX_RESPONSE_LENGTH=200
ENABLE_AUTO_GREETING=true
```

---

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

---

## 프로젝트 구조

```
youtuber_chatbot/
├── docs/
│   └── PRD-0002-chatbot.md     # 요구사항 명세서
├── src/
│   ├── config/                  # 환경변수 로드
│   ├── handlers/                # 메시지 라우팅, 명령어 처리
│   ├── services/                # YouTube, LLM, 메인 서버 클라이언트
│   ├── types/                   # TypeScript 타입 정의
│   └── utils/                   # 유틸리티 함수
├── shared/
│   └── src/types/               # 공유 타입 (메인 서버와 공유)
├── tests/                       # 테스트 코드
├── package.json
├── tsconfig.json
├── .env.example
├── CLAUDE.md                    # Claude Code 개발 가이드
└── README.md                    # 이 파일
```

---

## 명령어

### 개발

| 명령어 | 설명 |
|--------|------|
| `npm run dev` | 개발 서버 (tsx watch, 핫 리로드) |
| `npm run build` | TypeScript 빌드 |
| `npm run start` | 프로덕션 서버 실행 |
| `npm run lint` | ESLint 검사 |
| `npm run test` | Vitest 실행 |

### 챗봇 명령어 (YouTube Chat)

| 명령어 | 설명 |
|--------|------|
| `!help` | 사용 가능한 명령어 목록 |
| `!project` | 현재 작업 프로젝트 정보 |
| `!status` | TDD 상태 (Red/Green/Refactor) |
| `!time` | 방송 경과 시간 |
| `!github` | GitHub 링크 |
| `!ai` | AI 모델 정보 |

---

## Qwen 3 모델 선택

| 모델 | 크기 | VRAM | 용도 | 추천 |
|------|------|------|------|------|
| `qwen3:4b` | ~2.5GB | 4GB | 저사양 PC | |
| `qwen3:8b` | ~5GB | 8GB | 균형잡힌 성능 | ✅ 추천 |
| `qwen3:14b` | ~9GB | 12GB | 고품질 응답 | |
| `qwen3:32b` | ~20GB | 24GB | 최고 성능 | |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 런타임 | Node.js 20 LTS |
| 언어 | TypeScript 5.x |
| HTTP 서버 | Express 4.x |
| YouTube Chat | @stu43005/masterchat |
| AI | Ollama (Qwen 3) |
| 테스트 | Vitest |

---

## 관련 문서

- **PRD**: [docs/PRD-0002-chatbot.md](docs/PRD-0002-chatbot.md)
- **개발 가이드**: [CLAUDE.md](CLAUDE.md)
- **메인 프로젝트**: [youtuber](https://github.com/garimto81/youtuber)

---

## 라이선스

MIT

---

## 다른 스트리머를 위한 커스터마이징

이 챗봇을 자신의 방송에 사용하려면:

### 1. 호스트 프로필 생성

```bash
cp config/host-profile.example.json config/host-profile.json
```

### 2. 정보 수정

`config/host-profile.json` 파일을 열어 수정:
- `host.name`: 당신의 닉네임
- `social.github`: GitHub 사용자명
- `projects`: 당신의 프로젝트 목록 (최소 1개)
- `persona`: 챗봇 페르소나 커스터마이징

### 3. GitHub 동기화 (선택)

Pinned repositories를 자동으로 프로젝트 목록에 추가:

```bash
# .env 파일에 GitHub Token 추가
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_AUTO_SYNC=false
```

- **수동 동기화**: YouTube 채팅에서 `!sync-repos` 명령어
- **자동 동기화**: `GITHUB_AUTO_SYNC=true` 설정

### 4. 테스트

```bash
npm run dev
curl http://localhost:3002/health
```

**주의**: `config/host-profile.json`은 Git에 커밋되지 않습니다.

---

## 저자

저자 정보는 `config/host-profile.json`에서 설정합니다.

원작자: [garimto81](https://github.com/garimto81)
