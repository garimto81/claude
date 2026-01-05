# YouTube Live Chat AI Chatbot

[![Tests](https://img.shields.io/badge/tests-163%20passed-success)](https://github.com/garimto81/youtuber_chatbot)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-20%2B-green)](https://nodejs.org/)

**버전**: 3.0.0
**기반**: Ollama + Qwen 3
**용도**: YouTube 채팅 전담 AI 챗봇

---

## 개요

> **이 프로젝트는 YouTube 채팅만 전담합니다.**

YouTube Live 채팅에서 시청자와 실시간 상호작용하는 독립 AI 챗봇 서버입니다.

### 주요 기능

| 기능 | 설명 |
|------|------|
| **AI 질문 응답** | Qwen 3가 프로그래밍 질문에 답변 |
| **명령어 처리** | `!help`, `!ai`, `!projects` 등 |
| **인사 응답** | 자동 인사 응답 |
| **호스트 정보** | 프로젝트, GitHub 정보 제공 |

### 제외 범위

- 메인 서버 연동 (별도 프로젝트)
- VTuber/버튜버 연동 (youtuber_vertuber)
- OBS 오버레이
- 방송 세션 관리

---

## 시스템 요구사항

| 항목 | 요구사항 |
|------|----------|
| Node.js | 20 LTS 이상 |
| Ollama | 최신 버전 |
| VRAM | 8GB 이상 (qwen3:8b) |

---

## 아키텍처

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   YouTube   │◀────▶│   Chatbot   │────▶│   Ollama    │
│  Live Chat  │      │   Server    │      │  (Qwen 3)   │
│ (masterchat)│      │ Port: 3002  │      │ Port: 11434 │
└─────────────┘      └─────────────┘      └─────────────┘
```

---

## 설치 및 실행

### 1. Ollama 설치

```powershell
# Windows
winget install Ollama.Ollama

# macOS
brew install ollama
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
```

### 4. 실행

```powershell
# 터미널 1: Ollama 서버
ollama serve

# 터미널 2: 챗봇 서버
npm run dev
```

---

## 환경 변수

```env
# 서버
PORT=3002

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# YouTube Chat (선택)
YOUTUBE_VIDEO_ID=your_video_id

# 챗봇
MAX_RESPONSE_LENGTH=200

# GitHub (선택)
GITHUB_TOKEN=ghp_xxxxx
```

---

## 명령어

### 개발

| 명령어 | 설명 |
|--------|------|
| `npm run dev` | 개발 서버 (핫 리로드) |
| `npm run build` | TypeScript 빌드 |
| `npm run test` | 테스트 실행 |
| `npm run lint` | ESLint 검사 |

### 챗봇 (YouTube Chat)

| 명령어 | 설명 |
|--------|------|
| `!help` | 명령어 목록 |
| `!ai` | AI 모델 정보 |
| `!github` | GitHub 링크 |
| `!projects` | 프로젝트 목록 |

---

## 프로젝트 구조

```
youtuber_chatbot/
├── config/                 # 호스트 프로필
├── src/
│   ├── config/             # 환경변수
│   ├── handlers/           # 메시지 라우팅
│   ├── services/           # YouTube, LLM 클라이언트
│   ├── routes/             # REST API
│   └── utils/              # 유틸리티
├── tests/                  # 테스트 (163개)
└── docs/                   # PRD 문서
```

---

## Qwen 3 모델 선택

| 모델 | VRAM | 추천 |
|------|------|------|
| `qwen3:4b` | 4GB | 저사양 |
| `qwen3:8b` | 8GB | **추천** |
| `qwen3:14b` | 12GB | 고품질 |

---

## 호스트 커스터마이징

```bash
# 호스트 프로필 생성
cp config/host-profile.example.json config/host-profile.json
```

수정 항목:
- `host.name`: 닉네임
- `social.github`: GitHub 사용자명
- `projects`: 프로젝트 목록

---

## 관련 문서

- **PRD**: [docs/PRD-0002-chatbot.md](docs/PRD-0002-chatbot.md)
- **개발 가이드**: [CLAUDE.md](CLAUDE.md)

---

## 라이선스

MIT

---

**원작자**: [garimto81](https://github.com/garimto81)
