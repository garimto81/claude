# PRD-0002: YouTube 방송 채팅 챗봇

**버전**: 2.1.0
**작성일**: 2026-01-04
**상태**: Draft

---

## 1. 개요

### 1.1 목적

AI Coding YouTube 방송에서 시청자와 실시간으로 상호작용하는 **Ollama + Qwen 3** 기반 지능형 챗봇을 구축합니다.

### 1.2 범위

| 항목 | 포함 | 제외 |
|------|------|------|
| 플랫폼 | YouTube Live Chat | Twitch, Discord |
| AI 엔진 | **Ollama + Qwen 3 (로컬)** | Claude, GPT, Gemini |
| 서버 구조 | 독립 서버 (Port 3002) | 메인 서버 통합 |

### 1.3 핵심 기능

1. **시청자 질문 응답** - 코딩/프로그래밍 질문에 Qwen 3 AI가 답변
2. **방송 정보 제공** - 현재 프로젝트, 세션 시간, TDD 상태 등
3. **명령어 처리** - `!help`, `!project`, `!status` 등 커맨드 처리
4. **인사/환영 메시지** - 첫 입장 시 환영, 인사 자동 응답

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

### 2.1 구성도

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
                    │(세션/프로젝트)│
                    └─────────────┘
```

### 2.2 데이터 흐름

| 이벤트 | 소스 | 경로 | 결과 |
|--------|------|------|------|
| 채팅 수신 | YouTube | masterchat → Chatbot | 메시지 파싱 |
| AI 응답 | 사용자 질문 | Chatbot → Ollama(Qwen3) → YouTube | 답변 전송 |
| 방송 정보 | 메인 서버 | Chatbot → Main(3001) → Response | 상태 조회 |
| 명령어 | 사용자 입력 | Chatbot → 내부 처리 → YouTube | 즉시 응답 |

---

## 3. 기술 스택

| 영역 | 기술 | 버전 | 비고 |
|------|------|------|------|
| 런타임 | Node.js | 20 LTS | 기존 프로젝트와 동일 |
| 언어 | TypeScript | 5.x | 타입 안정성 |
| HTTP 서버 | Express | 4.x | API 엔드포인트 |
| YouTube | @stu43005/masterchat | 최신 | API 키 불필요 |
| AI | **ollama** | 최신 | Qwen 3 로컬 실행 |
| 환경변수 | dotenv | 16.x | 설정 관리 |

### 3.1 Qwen 3 모델 선택 가이드

| 모델 | 크기 | VRAM | 용도 | 추천 |
|------|------|------|------|------|
| `qwen3:0.6b` | ~400MB | 1GB | 초경량/테스트 | |
| `qwen3:4b` | ~2.5GB | 4GB | 일반 챗봇 | |
| `qwen3:8b` | ~5GB | 8GB | **균형잡힌 성능** | ✅ 추천 |
| `qwen3:14b` | ~9GB | 12GB | 고품질 응답 | |
| `qwen3:32b` | ~20GB | 24GB | 최고 성능 | |

---

## 4. 프로젝트 구조

```
chatbot/
├── docs/
│   └── PRD-0002-chatbot.md     # 이 문서
├── src/
│   ├── index.ts                # 메인 엔트리포인트
│   ├── config/
│   │   └── index.ts            # 환경변수 로드
│   ├── services/
│   │   ├── youtube-chat.ts     # masterchat 래퍼
│   │   ├── llm-client.ts       # Ollama + Qwen 3 클라이언트
│   │   ├── main-server.ts      # 메인 서버 HTTP 클라이언트
│   │   └── rate-limiter.ts     # 응답 제한
│   ├── handlers/
│   │   ├── message-router.ts   # 메시지 분류/라우팅
│   │   ├── command.ts          # 명령어 처리
│   │   ├── question.ts         # 질문 응답 (AI)
│   │   ├── greeting.ts         # 인사/환영
│   │   └── broadcast-info.ts   # 방송 정보
│   ├── types/
│   │   └── index.ts            # TypeScript 타입
│   └── utils/
│       ├── message-parser.ts   # 메시지 파싱
│       ├── response-formatter.ts
│       └── logger.ts           # 로깅
├── tests/
├── package.json
├── tsconfig.json
├── .env.example
└── CLAUDE.md
```

---

## 5. 핵심 모듈 설계

### 5.1 YouTube Chat 서비스 (masterchat)

```typescript
// src/services/youtube-chat.ts
import { Masterchat, stringify } from '@stu43005/masterchat';

interface YouTubeChatService {
  connect(videoIdOrUrl: string): Promise<void>;
  onMessage(callback: (msg: ChatMessage) => void): void;
  sendMessage(text: string): Promise<void>;
  disconnect(): void;
}

interface ChatMessage {
  id: string;
  authorChannelId: string;
  authorName: string;
  message: string;
  timestamp: Date;
  isMember: boolean;
  isModerator: boolean;
}
```

**masterchat 특징:**
- YouTube Data API 키 불필요
- 채팅 읽기 + 전송 모두 지원
- 모더레이션 기능 내장
- Iterator 기반 스트리밍

### 5.2 LLM 클라이언트 (Ollama + Qwen 3)

```typescript
// src/services/llm-client.ts
import ollama from 'ollama';

interface LLMClient {
  generateResponse(question: string, context?: Context): Promise<string>;
  classifyMessage(message: string): Promise<MessageType>;
}

type MessageType = 'question' | 'greeting' | 'command' | 'chitchat' | 'spam';

// 시스템 프롬프트
const SYSTEM_PROMPT = `
당신은 AI 코딩 YouTube 방송의 친근한 챗봇입니다.

역할:
- 시청자의 프로그래밍/코딩 질문에 간결하고 정확하게 답변
- 방송 진행 상황 안내
- 친근하고 유머러스한 톤 유지

제한사항:
- 답변은 200자 이내 (YouTube 채팅 특성)
- 정치, 종교 등 민감한 주제 회피
- 불확실한 정보는 솔직하게 모른다고 답변

호스트: [config/host-profile.json에서 동적으로 로드]
플랫폼: Claude Code (CLI)
주요 언어: [호스트 프로필의 persona.primaryLanguages]
`;

export class LLMClient {
  private model: string;

  constructor(model = 'qwen3:8b') {
    this.model = model;
  }

  async generateResponse(userMessage: string): Promise<string> {
    try {
      const response = await ollama.chat({
        model: this.model,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: userMessage },
        ],
        options: {
          temperature: 0.7,
          num_predict: 256,  // 최대 토큰 제한
        },
      });

      return response.message.content;
    } catch (error) {
      console.error('[LLM] Error:', error);
      return '죄송합니다, 잠시 후 다시 시도해주세요.';
    }
  }

  async classifyMessage(message: string): Promise<MessageType> {
    const response = await ollama.chat({
      model: this.model,
      messages: [
        {
          role: 'system',
          content: '메시지를 분류하세요. question/greeting/command/chitchat/spam 중 하나만 답변.'
        },
        { role: 'user', content: message },
      ],
      options: { temperature: 0 },
    });

    const result = response.message.content.toLowerCase().trim();
    const validTypes = ['question', 'greeting', 'command', 'chitchat', 'spam'];
    return validTypes.includes(result) ? result as MessageType : 'chitchat';
  }

  // 복잡한 질문에 대해 깊은 추론 (Qwen 3 특화)
  async deepThinking(question: string): Promise<string> {
    const response = await ollama.chat({
      model: this.model,
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: `${question} /think` },  // Qwen 3 thinking mode
      ],
    });
    return response.message.content;
  }
}
```

### 5.3 메시지 라우터

```typescript
// src/handlers/message-router.ts
interface MessageRouter {
  route(message: ChatMessage): Promise<RouteResult>;
}

interface RouteResult {
  handler: 'command' | 'question' | 'greeting' | 'broadcast' | 'ignore';
  shouldRespond: boolean;
  response?: string;
}

// 라우팅 로직
// 1. !로 시작 → command
// 2. @봇멘션 → question
// 3. AI 분류 → question/greeting/ignore
```

### 5.4 명령어 핸들러

```typescript
// src/handlers/command.ts
// 동적 명령어 생성 - 호스트 프로필 기반
export function buildCommandMap() {
  const profile = getHostProfile();

  return {
    '!help': () => '명령어: !help, !projects, !github, !ai, !sync-repos, ...',
    '!projects': () => {
      // 프로젝트 목록 동적 생성
      return profile.projects.map(p => `- ${p.name} (${p.id})`).join('\n');
    },
    '!github': () => `GitHub: https://github.com/${profile.social.github}`,
    '!ai': () => 'AI: Qwen 3 (8B) - Ollama 로컬 실행',
    '!sync-repos': async () => {
      // GitHub Pinned repos 동기화
      const analyzer = new GitHubAnalyzer(profile.social.github, process.env.GITHUB_TOKEN);
      const pinnedRepos = await analyzer.getPinnedRepositories();
      await loader.mergeGitHubProjects(pinnedRepos);
      return `✅ ${pinnedRepos.length}개 레포 동기화 완료`;
    },
    // 프로젝트별 명령어 (!claude, !studio 등) 자동 생성
    ...generateProjectCommands(profile.projects)
  };
}
```

### 5.5 메인 서버 클라이언트

```typescript
// src/services/main-server.ts
interface MainServerClient {
  getSessionStats(): Promise<SessionStats>;
  health(): Promise<HealthStatus>;
}

interface SessionStats {
  running: boolean;
  duration?: number;
  commits?: number;
  currentProject?: string;
  tdd?: { phase: string; testsPassed: number; testsTotal: number };
}
```

---

## 6. API 엔드포인트 (Port 3002)

| 경로 | 메서드 | 용도 |
|------|--------|------|
| `/health` | GET | 서버 상태 |
| `/api/start` | POST | 챗봇 시작 (videoId 지정) |
| `/api/stop` | POST | 챗봇 중지 |
| `/api/status` | GET | 현재 연결 상태 |
| `/api/stats` | GET | 통계 (응답 수, 질문 수) |
| `/api/test-message` | POST | 테스트 메시지 전송 |
| `/api/ollama/status` | GET | Ollama 연결 상태 |

---

## 7. 환경 변수

```env
# 챗봇 서버
PORT=3002
HOST=localhost

# Ollama 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# 메인 서버 연결
MAIN_SERVER_URL=http://localhost:3001

# 챗봇 설정
BOT_NAME=CodingBot
RESPONSE_DELAY_MS=500
MAX_RESPONSE_LENGTH=200
ENABLE_AUTO_GREETING=true

# GitHub 동기화 설정
GITHUB_TOKEN=                    # Personal Access Token
GITHUB_AUTO_SYNC=false           # 앱 시작 시 자동 동기화
GITHUB_ACTIVITY_DAYS=5           # 최근 활동 조회 기간 (일)
```

---

## 8. Rate Limiting

| 제한 항목 | 값 | 대응 |
|-----------|-----|------|
| 분당 응답 | 30회 | 큐 기반 처리 |
| 시간당 응답 | 500회 | 모니터링 |
| 사용자별 쿨다운 | 5초 | 중복 방지 |

**참고**: Ollama는 로컬 실행이므로 API Rate Limit이 없음. 제한은 YouTube 채팅 특성상 적용.

---

## 9. 메시지 처리 흐름

```
YouTube Chat ──▶ masterchat ──▶ Message Queue
                                    │
                                    ▼
                         ┌──────────────────┐
                         │ Message Router   │
                         │ (AI 분류)        │
                         └────────┬─────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
   ┌───────────┐           ┌───────────┐            ┌───────────┐
   │  Command  │           │ Question  │            │ Greeting  │
   │  Handler  │           │  Handler  │            │  Handler  │
   └─────┬─────┘           └─────┬─────┘            └─────┬─────┘
         │                 Ollama (Qwen 3)                 │
         └───────────────────────┼─────────────────────────┘
                                 ▼
                          Rate Limiter
                                 │
                                 ▼
                    YouTube Chat (응답 전송)
```

---

## 10. Ollama 설치 및 실행

### 10.1 Ollama 설치

```powershell
# Windows: https://ollama.com/download 에서 설치
# 또는 winget 사용
winget install Ollama.Ollama
```

### 10.2 Qwen 3 모델 다운로드

```powershell
# Ollama 서비스 시작
ollama serve

# 모델 다운로드 (새 터미널)
ollama pull qwen3:8b

# 테스트 실행
ollama run qwen3:8b "안녕하세요!"
```

### 10.3 실행 순서

```powershell
# 터미널 1: Ollama 서버
ollama serve

# 터미널 2: 메인 서버 (선택)
cd D:\AI\claude01\youtuber
npm run dev

# 터미널 3: 챗봇 서버
cd D:\AI\claude01\youtuber\chatbot
npm install
npm run dev
```

---

## 11. 구현 단계

### Phase 1: 기본 인프라
- [ ] 프로젝트 초기화 (npm, TypeScript)
- [ ] 환경 변수 및 설정 모듈
- [ ] Express 서버 구조

### Phase 2: Ollama 연동
- [ ] Ollama 연결 확인
- [ ] LLM 클라이언트 구현
- [ ] 시스템 프롬프트 설계
- [ ] 메시지 분류 기능

### Phase 3: YouTube 연동
- [ ] masterchat 연결
- [ ] 메시지 수신 구현
- [ ] 메시지 전송 구현

### Phase 4: 핸들러 구현
- [ ] 명령어 핸들러
- [ ] 질문 응답 핸들러
- [ ] 인사/환영 핸들러

### Phase 5: 메인 서버 연동
- [ ] HTTP 클라이언트
- [ ] 세션 정보 조회

### Phase 6: 테스트
- [ ] 단위 테스트
- [ ] 실제 방송 테스트

---

## 12. 호스트 프로필 설정

챗봇의 호스트 정보는 `config/host-profile.json`에서 관리됩니다.

### 12.1 설정 방법

**1단계: 템플릿 복사**
```bash
cp config/host-profile.example.json config/host-profile.json
```

**2단계: 정보 수정**

`config/host-profile.json` 파일을 열어 다음 항목을 수정:
- `host.name`: 호스트 닉네임
- `host.displayName`: 표시 이름 (선택)
- `host.bio`: 자기소개 (선택)
- `social.github`: GitHub 사용자명
- `persona.role`: 챗봇 역할 설명
- `persona.tone`: 말투/톤
- `persona.expertise`: 전문 분야 목록
- `projects`: 프로젝트 목록 (최소 1개)

**3단계: 프로젝트 추가**

`projects` 배열에 새 프로젝트 추가 시 자동으로 `!프로젝트ID` 명령어가 생성됩니다:

```json
{
  "id": "my-project",
  "name": "My Project",
  "description": "프로젝트 설명",
  "repository": "username/repo",
  "version": "1.0.0",
  "stack": "TypeScript",
  "isActive": true,
  "source": "manual"
}
```

### 12.2 GitHub 레포지토리 자동 동기화

**환경 변수 설정**

`.env` 파일에 GitHub Token 추가:
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx  # Personal Access Token
GITHUB_AUTO_SYNC=false           # 자동 동기화 여부
```

**수동 동기화**

YouTube 채팅에서 `!sync-repos` 명령어 실행:
- Pinned repositories를 자동으로 조회
- `config/host-profile.json`의 projects에 병합
- `source: "github"` 태그가 있는 프로젝트만 자동 업데이트

**자동 동기화**

`GITHUB_AUTO_SYNC=true` 설정 시 앱 시작마다 Pinned repos 자동 동기화

**병합 규칙**:
1. `source: "manual"` 프로젝트는 덮어쓰지 않음
2. `source: "github"` 프로젝트만 자동 업데이트
3. 새로운 Pinned repo는 자동 추가

### 12.3 동적 명령어 생성

프로젝트를 추가하면 자동으로 명령어가 생성됩니다:

| 프로젝트 ID | 생성되는 명령어 | 출력 예시 |
|------------|---------------|----------|
| `claude` | `!claude` | `claude v11.6.0 ⭐45 - Claude Code 개발 방법론` |
| `cc-wf-studio` | `!studio` | `Workflow Studio v3.11.3 ⭐12 - VSCode 워크플로우 에디터` |

**구현 예시**:
```typescript
// src/handlers/command.ts
export function buildCommandMap() {
  const profile = getHostProfile();
  const projectCommands = {};

  profile.projects.forEach(p => {
    const stars = p.stars ? ` ⭐${p.stars}` : '';
    projectCommands[`!${p.id}`] = () =>
      `${p.name} v${p.version}${stars} - ${p.description}`;
  });

  return { ...baseCommands, ...projectCommands };
}
```

### 12.5 최근 활동 프로젝트 조회

**`!projects` 명령어 개선** (v2.1.0)

YouTube 채팅에서 `!projects` 입력 시, 최근 5일간 커밋 또는 이슈가 있는 프로젝트만 표시합니다.

**활동 기준**:
- 최근 커밋 (`pushed_at` 확인)
- 최근 이슈 생성/업데이트 (`since` 파라미터 사용)

**예시 출력**:
```
📊 최근 5일간 활동 프로젝트 (3개):
- claude ⭐45 (Python, PowerShell)
- Workflow Studio ⭐12 (TypeScript, VSCode Extension)
- 방송 오버레이 (TypeScript, Express, WebSocket)
```

**구현**:
```typescript
// src/services/github-analyzer.ts
async getRecentActiveRepositories(days: number = 5): Promise<HostProject[]> {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - days);

  const allRepos = await this.listRepositories();
  const activeRepos = [];

  for (const repo of allRepos) {
    const hasActivity = await this.hasRecentActivity(repo.repository, cutoffDate);
    if (hasActivity) {
      activeRepos.push(repo);
    }
  }

  return activeRepos;
}
```

**세션 시작 시 자동 동기화**:
```env
GITHUB_AUTO_SYNC=true           # 앱 시작 시 자동 동기화
GITHUB_ACTIVITY_DAYS=5          # 최근 5일 활동 조회
```

앱 시작 시 `GITHUB_AUTO_SYNC=true`일 경우:
1. GitHub API로 최근 N일간 활동이 있는 레포 조회
2. `config/host-profile.json`의 projects에 자동 병합
3. `source: "github"` 태그가 있는 프로젝트만 업데이트

### 12.4 시스템 프롬프트 동적 생성

호스트 프로필 기반으로 LLM 시스템 프롬프트가 자동 생성됩니다:

```typescript
// src/services/prompt-builder.ts
const prompt = PromptBuilder.buildSystemPrompt(profile);

// 생성 예시:
// "당신은 AI 코딩 YouTube 방송의 친근한 챗봇입니다.
//  호스트: Garimto (GitHub: garimto81)
//  전문 분야: TypeScript/Python 개발, TDD 방법론
//  활성 프로젝트: claude (v11.6.0) ⭐45 - ..."
```

---

## 13. 참고 자료

### 기술 문서
- [Qwen 3 - Ollama](https://ollama.com/library/qwen3)
- [How to Set Up Qwen3 with Ollama - DataCamp](https://www.datacamp.com/tutorial/qwen3-ollama)
- [@stu43005/masterchat - npm](https://www.npmjs.com/package/@stu43005/masterchat)
- [Qwen3 GitHub](https://github.com/QwenLM/Qwen3)

### GitHub API
- [Octokit.js - Official GitHub SDK](https://github.com/octokit/octokit.js)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)

### 프로젝트
- 메인 프로젝트: `D:\AI\claude01\youtuber\`
- 호스트 정보: `config/host-profile.json` 참조

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-01-04 | 초안 작성 (Claude API 기반) |
| 1.1.0 | 2026-01-04 | Ollama + Qwen 3 기반으로 변경 |
| 1.2.0 | 2026-01-04 | 호스트 프로젝트 컨텍스트 추가 |
| 2.0.0 | 2026-01-04 | 🎉 **호스트 정보 관리 시스템 구현 완료**<br/>- JSON 기반 호스트 프로필 (`config/host-profile.json`)<br/>- GitHub API 연동 (Octokit) 및 자동 동기화<br/>- 동적 명령어 생성 (`!sync-repos`, 프로젝트별 명령어)<br/>- 시스템 프롬프트 동적 생성<br/>- 다른 스트리머 지원 (템플릿화) |
| 2.1.0 | 2026-01-04 | ✨ **최근 활동 프로젝트 자동 조회**<br/>- `!projects` 명령어: 최근 5일간 활동 프로젝트만 표시<br/>- `getRecentActiveRepositories()` 메서드 추가<br/>- `GITHUB_ACTIVITY_DAYS` 환경 변수 추가<br/>- 세션 시작 시 자동 필터링 로직 (커밋/이슈 기준) |
