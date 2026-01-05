# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VSeeFace VTuber 기능 통합 프로젝트 - AI 코딩 스트리밍에 버튜버 아바타 연동
- VSeeFace → VMC Protocol → WebSocket → OBS Overlay 데이터 흐름
- GitHub 이벤트 및 YouTube 채팅 감정 분석에 따른 아바타 반응 시스템

## Build & Test Commands

```powershell
# 개발 서버 (모든 패키지)
pnpm dev

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

# packages/stream-server 개발
cd packages/stream-server && pnpm dev
```

## Architecture

### Monorepo 구조 (pnpm workspaces)

```
packages/
├── shared/          # 공유 타입 정의 (@youtuber/shared)
│   └── src/types/   # WebSocket 메시지 타입, VTuber 표정 타입
├── vtuber/          # VMC Client 및 아바타 컨트롤러 (@youtuber/vtuber)
│   └── src/
│       ├── vmc-client.ts       # VSeeFace VMC Protocol UDP 클라이언트
│       ├── avatar-controller.ts # 우선순위 큐 기반 표정 관리
│       └── reaction-mapper.ts   # 이벤트→표정 매핑 테이블
└── stream-server/   # WebSocket 서버 (@youtuber/stream-server)
    └── public/
        ├── overlay/ # 1920x1080 전체 OBS 오버레이
        └── vtuber/  # 320x180 아바타 전용 프레임
```

### 데이터 흐름

1. **VSeeFace** → VMC Protocol (UDP:39539) → **VMCClient** (BlendShape 수신)
2. **VMCClient** → WebSocket → **Stream Server**
3. **GitHub Webhook** / **YouTube Chat** → **Stream Server** → **AvatarController**
4. **AvatarController** → WebSocket → **OBS Overlay**

### 핵심 컴포넌트

| 클래스 | 파일 | 역할 |
|--------|------|------|
| `VMCClient` | `packages/vtuber/src/vmc-client.ts` | VSeeFace OSC 통신, BlendShape 수신 |
| `AvatarController` | `packages/vtuber/src/avatar-controller.ts` | 우선순위 큐 기반 표정 제어 |
| `ReactionMapper` | `packages/vtuber/src/reaction-mapper.ts` | GitHub 이벤트/채팅 감정 → 표정 매핑 |

### 표정 타입

```typescript
type Expression = 'happy' | 'surprised' | 'neutral' | 'focused' | 'sorrow';
type Priority = 'high' | 'medium' | 'low';
```

### 이벤트-표정 매핑

| 이벤트 | 표정 | 우선순위 |
|--------|------|----------|
| `commit` | `happy` | medium |
| `pr_merged` | `surprised` | high |
| `test_passed` | `focused` → `happy` | high |
| `test_failed` | `sorrow` | medium |

## OBS Overlay URLs

```
# 전체 오버레이 (1920x1080)
http://localhost:3001/overlay/?transparent=true

# 아바타 프레임만 (320x180)
http://localhost:3001/vtuber/?transparent=true
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
     ↓
@youtuber/stream-server (WebSocket 서버)
```
