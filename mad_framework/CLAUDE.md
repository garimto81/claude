# CLAUDE.md

MAD Framework - 웹 자동화 기반 Multi-Agent Debate (Electron + React)

## 프로젝트 목적

**API 키 없이** 브라우저 자동화로 ChatGPT/Claude/Gemini 웹 UI를 조작하여 LLM 간 토론을 수행하는 실험적 프로젝트.

## Commands

```powershell
cd D:\AI\claude01\mad_framework\desktop

# 개발
npm run dev:electron                    # Electron 앱 실행

# 테스트
npm run test:run                        # 전체 테스트
npm run test:run -- tests/unit/debate   # 디렉토리별
npm run test:coverage                   # 커버리지

# 빌드
npm run lint                            # ESLint
npm run build                           # 프로덕션 빌드
```

## Architecture

```
desktop/
├── electron/                    # Main Process
│   ├── main.ts                  # 앱 진입점
│   ├── preload.ts               # 보안 컨텍스트
│   ├── ipc/handlers.ts          # IPC 핸들러
│   ├── browser/
│   │   ├── browser-view-manager.ts   # BrowserView 관리
│   │   ├── session-manager.ts        # 세션 유지
│   │   └── adapters/
│   │       ├── base-adapter.ts       # AdapterResult<T> 패턴
│   │       ├── chatgpt-adapter.ts
│   │       ├── claude-adapter.ts
│   │       ├── gemini-adapter.ts
│   │       └── selector-config.ts    # CSS 셀렉터 + fallback
│   └── debate/
│       ├── debate-controller.ts      # 토론 루프 (MAX=100)
│       ├── cycle-detector.ts         # Levenshtein 순환 감지
│       └── in-memory-repository.ts   # 데이터 저장
│
├── src/                         # Renderer Process (React)
│   ├── App.tsx
│   ├── stores/                  # Zustand
│   │   ├── debate-store.ts
│   │   └── login-store.ts
│   └── components/              # UI 컴포넌트 8개
│
├── playwright/                  # Headless PoC (70%)
│   ├── playwright-browser-manager.ts
│   └── adapters/chatgpt-adapter.ts  # ChatGPT만 구현
│
└── shared/types.ts              # 공유 타입 정의
```

## Key Patterns

```typescript
// AdapterResult<T> - 성공/실패 표준화
interface AdapterResult<T> { success: boolean; data?: T; error?: AdapterError; }

// SelectorSet - fallback 시스템
interface SelectorSet { primary: string; fallbacks: string[]; }

// IPC Events
'debate:start' | 'debate:progress' | 'debate:stream-chunk' | 'debate:complete'
```

## Constants

| 상수 | 위치 | 값 | 용도 |
|------|------|-----|------|
| `MAX_ITERATIONS` | debate-controller.ts | 100 | 토론 반복 제한 |
| `MAX_CONSECUTIVE_EMPTY` | debate-controller.ts | 3 | 빈 응답 차단 |
| `SIMILARITY_THRESHOLD` | cycle-detector.ts | 0.85 | 순환 감지 임계값 |
| `completionThreshold` | DebateConfig | 90 | 요소 완성 점수 |

## Presets

| 프리셋 | 평가 요소 |
|--------|----------|
| `code_review` | 보안, 성능, 가독성, 유지보수성 |
| `qa_accuracy` | 정확성, 완전성, 명확성 |
| `decision` | 장점, 단점, 위험, 기회 |

## 미완성 항목

- [ ] Playwright Claude/Gemini 어댑터
- [ ] E2E 테스트
- [ ] 프로덕션 데이터베이스 통합
