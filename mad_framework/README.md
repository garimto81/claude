# MAD Framework

**Multi-Agent Debate** - 웹 자동화 기반 LLM 토론 프레임워크

## Overview

브라우저 자동화로 ChatGPT, Claude, Gemini 웹 UI를 조작하여 **API 키 없이** LLM 간 토론을 수행하는 실험적 프로젝트입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    MAD Framework                             │
├─────────────────────────────────────────────────────────────┤
│  Topic ──▶ LLM 토론 (Round 1, 2, 3...) ──▶ 최종 결과        │
│                                                               │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                │
│  │ ChatGPT │ ←→  │  Claude │ ←→  │ Gemini  │                │
│  │  (웹)   │     │  (웹)   │     │  (웹)   │                │
│  └─────────┘     └─────────┘     └─────────┘                │
│         ↓              ↓              ↓                      │
│      BrowserView 자동화 (Electron)                           │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **웹 자동화**: Electron BrowserView로 LLM 웹 UI 자동 조작
- **API 키 불필요**: 기존 브라우저 로그인 세션 활용
- **실시간 스트리밍**: 응답을 실시간으로 UI에 표시
- **순환 감지**: Levenshtein 거리 기반 반복 패턴 감지
- **프리셋**: 코드 리뷰, Q&A 정확도, 의사결정 지원

## Quick Start

```powershell
cd desktop
npm install
npm run dev:electron
```

1. 앱 실행 후 각 LLM (ChatGPT, Claude, Gemini) 로그인
2. 토론 주제 및 프리셋 선택
3. 토론 시작 버튼 클릭

## Architecture

```
desktop/
├── electron/           # Main Process
│   ├── browser/        # BrowserView + 어댑터
│   ├── debate/         # 토론 컨트롤러
│   └── ipc/            # Renderer 통신
├── src/                # Renderer (React + Zustand)
├── playwright/         # Headless PoC
└── shared/             # 공유 타입
```

## Presets

| 프리셋 | 평가 요소 |
|--------|----------|
| `code_review` | 보안, 성능, 가독성, 유지보수성 |
| `qa_accuracy` | 정확성, 완전성, 명확성 |
| `decision` | 장점, 단점, 위험, 기회 |

## Development

```powershell
npm run dev:electron    # 개발 모드
npm run test:run        # 테스트
npm run lint            # 린트
npm run build           # 빌드
```

## Roadmap

- [ ] Playwright Headless 모드 완성 (Claude, Gemini)
- [ ] E2E 테스트
- [ ] 프로덕션 데이터베이스 통합
- [ ] 토론 결과 내보내기

## License

MIT License
