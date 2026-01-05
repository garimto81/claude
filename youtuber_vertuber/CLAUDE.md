# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VSeeFace 버튜버 아바타 활성화 프로젝트
- VSeeFace → VMC Protocol (UDP:39539) → 표정 제어
- 핵심: VSeeFace 연동 및 BlendShape 송수신

## Build & Test Commands

```powershell
# 빌드
pnpm build

# 테스트 (모든 패키지)
pnpm test

# 특정 패키지 테스트
pnpm --filter @youtuber/vtuber test

# 린트
pnpm lint
```

### 개별 패키지 개발

```powershell
# packages/vtuber 개발
cd packages/vtuber && pnpm dev
```

## Architecture

### Monorepo 구조 (pnpm workspaces)

```
packages/
├── shared/          # 공유 타입 정의 (@youtuber/shared)
│   └── src/types/   # VTuber 표정 타입
└── vtuber/          # VMC Client 및 아바타 컨트롤러 (@youtuber/vtuber)
    └── src/
        ├── vmc-client.ts        # VSeeFace VMC Protocol UDP 클라이언트
        └── avatar-controller.ts # 우선순위 큐 기반 표정 관리

VSeeFace/            # VSeeFace 바이너리 (git 제외)
archive/             # 아카이빙된 코드 (git 제외)
```

### 데이터 흐름

```
VSeeFace.exe ──UDP:39539──▶ VMCClient ──▶ AvatarController
                              │
                              ▼
                        BlendShape 송수신
```

### 핵심 컴포넌트

| 클래스 | 파일 | 역할 |
|--------|------|------|
| `VMCClient` | `packages/vtuber/src/vmc-client.ts` | VSeeFace OSC 통신, BlendShape 수신 |
| `AvatarController` | `packages/vtuber/src/avatar-controller.ts` | 우선순위 큐 기반 표정 제어 |

### 표정 타입

```typescript
type Expression = 'happy' | 'surprised' | 'neutral' | 'focused' | 'sorrow';
type Priority = 'high' | 'medium' | 'low';
```

## VMC Protocol

- **기본 포트**: 39539 (VSeeFace)
- **프로토콜**: OSC over UDP
- **BlendShape 수신**: `/VMC/Ext/Blend/Val`
- **BlendShape 전송**: `/VMC/Ext/Blend/Apply`

## 패키지 간 의존성

```
@youtuber/shared (공유 타입)
     ↓
@youtuber/vtuber (VMC Client)
```

## Archived (2026-01-05)

다음 기능들은 `archive/` 폴더로 이동됨:
- stream-server (WebSocket, GitHub Webhook, OBS Overlay)
- Phase 3-4 (GitHub 연동, YouTube 채팅)
