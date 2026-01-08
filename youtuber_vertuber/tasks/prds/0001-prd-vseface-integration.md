# VSeeFace 버튜버 기능 통합 PRD

**번호**: PRD-0001
**작성일**: 2026-01-04
**최종 수정**: 2026-01-06
**작성자**: Claude (AI Assistant)
**우선순위**: High
**상태**: In Progress
**버전**: 2.0.0

---

## 1. 개요

### 문제 정의
현재 youtuber 프로젝트의 OBS 오버레이에서 "얼굴 캠" 영역(320x180)이 비어있어 방송에 개성과 생동감이 부족합니다. AI 코딩 스트리밍이라는 독특한 컨셉에도 불구하고, 시청자가 스트리머와 감정적으로 연결되기 어렵습니다.

### 제안 솔루션
VSeeFace와 VMC Protocol을 활용하여 웹캠 기반 버튜버 아바타를 실시간으로 표시하고, 프로그래밍 방식으로 표정을 제어할 수 있는 아바타 시스템을 구현합니다.

> **v2.0.0 범위 축소**: GitHub Webhook 연동과 YouTube 채팅 연동은 `archive/` 폴더로 이동되었습니다. 현재 버전은 VSeeFace 아바타 활성화 및 VMC Protocol 연동에 집중합니다.

### 예상 효과
- 시청자 몰입도 30% 향상 (평균 시청 시간 증가)
- 채팅 참여도 50% 증가 (메시지당 반응률)
- 구독자 전환율 20% 개선 (첫 방송 → 구독)
- 브랜드 차별화 (AI 코딩 + 버튜버 융합 콘텐츠)

---

## 2. 목표

### 비즈니스 목표
1. **시청자 참여도 향상**: 아바타 반응을 통해 GitHub 활동을 직관적으로 시각화하여 시청자 이해도 증대
2. **구독자 증가**: 독특한 버튜버 + 코딩 스트리밍 콘셉트로 브랜드 차별화
3. **콘텐츠 품질 개선**: 생동감 있는 방송으로 시청자 만족도 향상

### 사용자 목표
1. **스트리머**: 웹캠만으로 쉽게 버튜버 방송 시작 (VSeeFace 자동 연동)
2. **시청자**: GitHub 이벤트를 아바타 반응으로 실시간 확인 (Commit → 기쁨 표정)
3. **채팅 참여자**: 칭찬/질문 시 아바타가 반응하여 소통감 증대

---

## 3. 대상 사용자

**주요 사용자 유형**: 복합 (스트리머 + YouTube 시청자)

**스트리머 (본인)**:
- 기술 수준: 중급 (Node.js, TypeScript 개발 가능)
- 니즈: 방송 품질 향상, 자동화된 아바타 관리
- 예상 사용자 수: 1명 (본인)

**YouTube 시청자**:
- 기술 수준: 초급 (기술 지식 거의 없음)
- 니즈: 재미있고 이해하기 쉬운 코딩 방송
- 예상 사용자 수: 100-1000명 (초기 목표)

---

## 4. 사용자 스토리

### 스토리 1: 웹캠 얼굴 추적
```
As a 스트리머,
I want VSeeFace가 웹캠으로 내 얼굴을 추적하여 아바타를 실시간으로 움직이게 하고 싶다
So that 시청자에게 생동감 있는 방송을 제공할 수 있다

Acceptance Criteria:
- Given VSeeFace가 실행 중이고 웹캠이 연결되어 있을 때
- When 스트리머가 고개를 끄덕이거나 표정을 바꾸면
- Then 아바타가 1초 이내에 동일한 움직임을 반영한다
- And VMC Protocol을 통해 BlendShape 데이터가 30fps로 수신된다
```

### 스토리 2: GitHub 이벤트 반응
```
As a 시청자,
I want Commit이나 PR이 성공했을 때 아바타가 기쁜 표정을 지으면
So that 개발 진행 상황을 직관적으로 이해할 수 있다

Acceptance Criteria:
- Given GitHub Webhook이 설정되어 있을 때
- When Commit이 push되거나 PR이 merged되면
- Then 아바타가 2-3초간 "happy" 표정을 짓는다
- And OBS 오버레이에 반응 아이콘(🎉)이 표시된다
- And 반응 지연시간은 1초 미만이다
```

### 스토리 3: 채팅 상호작용
```
As a 시청자,
I want 채팅으로 칭찬("대박!", "멋져요!")을 보내면 아바타가 기뻐하면
So that 스트리머와 더 가까워진 느낌을 받는다

Acceptance Criteria:
- Given youtuber_chatbot이 실행 중이고 감정 분석이 활성화되어 있을 때
- When 시청자가 긍정적인 채팅 메시지를 보내면
- Then youtuber_chatbot이 감정을 분석하여 "positive" → "happy" 표정으로 변환한다
- And 아바타가 2초 이내에 반응한다
- And 너무 빈번한 반응은 방지한다 (최소 5초 간격)
```

---

## 5. 기능 요구사항

### 5.1 필수 기능 (Must Have)

#### 1. VSeeFace 웹캠 얼굴 추적
- 설명: VSeeFace와 VMC Protocol을 통해 웹캠 얼굴 추적 데이터를 실시간으로 수신
- 수락 기준:
  - [x] VSeeFace 설치 및 VMC Protocol 활성화 (Port 39539)
  - [x] VMC Client 구현 (Node.js osc 라이브러리)
  - [x] BlendShape 데이터 수신 (Joy, Angry, Sorrow, Fun)
  - [x] 연결 상태 모니터링 (5초마다 health check)

#### 2. OBS Browser Source 오버레이
- 설명: 320x180 "얼굴 캠" 영역에 VSeeFace 아바타를 표시
- 수락 기준:
  - [x] VSeeFace Window Capture를 OBS에 추가
  - [x] 배경 투명 처리 (Chroma Key 또는 VSeeFace 투명 배경)
  - [x] 1920x1080 레이아웃에서 깨짐 없이 표시
  - [x] OBS Browser Source로 반응 아이콘 오버레이

#### ~~3. GitHub Webhook 연동 (아바타 표정 변경)~~ → `archive/`
> **아카이빙됨 (v2.0.0)**: 이 기능은 범위 축소로 인해 `archive/stream-server/`로 이동되었습니다.

#### ~~4. youtuber_chatbot 연동 (채팅 감정 분석)~~ → `archive/`
> **아카이빙됨 (v2.0.0)**: 이 기능은 범위 축소로 인해 `archive/stream-server/`로 이동되었습니다.

### 5.2 선택 기능 (Nice to Have)

#### 1. 아바타 교체 UI
- 설명: 웹 UI에서 VRM 파일을 업로드하여 아바타 변경
- 우선순위: v2 (Phase 5)

#### 2. 표정 커스터마이징
- 설명: GitHub 이벤트별 표정 매핑을 설정 파일에서 커스터마이징
- 우선순위: v2 (Phase 5)

#### 3. TTS 음성 합성
- 설명: 채팅 메시지를 TTS로 변환하여 아바타 입 움직임과 동기화
- 우선순위: v3 (미정)

---

## 6. 범위 제외 (Out of Scope)

명확히 제외되는 항목:
- **TTS 음성 합성** (v1에서 제외, v3 검토)
- **복잡한 3D 환경/배경** (VSeeFace 기본 배경만 사용)
- **모바일 지원** (데스크톱 방송만)
- **실시간 아바타 에디팅** (VRoid Studio 별도 사용)
- **멀티 아바타 동시 표시** (1개 아바타만)
- **아바타 포즈 커스터마이징** (VSeeFace 기본 포즈만)

---

## 7. 데이터 요구사항

### 입력 데이터
- **VMC Protocol 데이터**: BlendShapes (Joy, Angry, Sorrow, Fun 등), Bone 위치/회전
- **GitHub Webhook**: Commit, PR, Issue, CI 이벤트 페이로드
- **YouTube 채팅 메시지**: 메시지 ID, 작성자, 내용, 타임스탬프

### 출력 데이터
- **WebSocket 메시지**: VTuber 표정 변경 이벤트 (type: 'vtuber:expression')
- **OBS 오버레이 데이터**: 반응 아이콘, 애니메이션 트리거

### 저장/보존 요구사항
- **아바타 설정**: VRM 파일 경로, 선택된 아바타 정보 (JSON 파일)
- **표정 매핑**: GitHub 이벤트 → 표정 매핑 테이블 (JSON 파일)
- **로그**: VMC 연결 상태, 표정 변경 이력 (선택사항, v2)

---

## 8. UI/UX 고려사항

### 화면 구성

**OBS 오버레이 레이아웃** (1920x1080):
```
┌──────────────────────────────────────────────┬────────────────────┐
│ [화면 캡처 - OBS Window Capture]               │   아바타 프레임    │
│         (1600 x 900)                         │   (320 x 180)      │
│                                              │                    │
│                                              │  ┌──────────────┐  │
│                                              │  │  VSeeFace    │  │
│                                              │  │  아바타      │  │
│                                              │  └──────────────┘  │
│                                              │  연결 상태: 🟢    │
├──────────────────────────────────────────────┤────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐      │  Active Projects   │
│ │ 프로젝트1 │ │ 프로젝트2 │ │ 프로젝트3 │      │   (320 x 900)      │
│ │  활동    │ │  활동    │ │  활동    │      │                    │
│ │  🎉 반응 │ │          │ │          │      │                    │
│ └──────────┘ └──────────┘ └──────────┘      │                    │
│    멀티 프로젝트 활동 카드 (1600 x 180)      │                    │
└──────────────────────────────────────────────┴────────────────────┘
```

### 주요 인터랙션

1. **아바타 얼굴 추적**: 스트리머 얼굴 움직임 → 아바타 실시간 반영 (30fps)
2. **GitHub 반응 애니메이션**:
   - Commit → 프로젝트 카드에 🎉 아이콘 2초간 표시
   - 아바타 표정 "happy" (2초)
3. **채팅 반응 애니메이션**:
   - 긍정적 채팅 → 아바타 표정 "happy" (2초)
   - 우측 상단에 💬 아이콘 깜빡임

### 반응형/접근성

- **반응형**: 고정 레이아웃 (1920x1080만 지원, OBS 방송용)
- **접근성**: 시각적 반응 우선 (TTS 음성은 v3에서 고려)
- **성능**: 60fps OBS 방송 유지 (아바타 30fps, 오버레이 60fps)

---

## 9. 기술 고려사항

### 9.1 기술 스택

| 영역 | 기술 | 버전 | 비고 |
|------|------|------|------|
| **VTuber 소프트웨어** | VSeeFace | v1.13.38+ | VMC Protocol 지원 |
| **아바타 포맷** | VRM | 0.0 / 1.0 | VRoid Hub 호환 |
| **VMC Protocol** | osc (Node.js) | ^2.4.0 | UDP 통신 |
| **WebSocket** | ws (기존) | 8.18.0 | 기존 youtuber 시스템 |
| **채팅 분석** | youtuber_chatbot | 1.0.0 | Ollama + Qwen 3 |
| **OBS 연동** | obs-websocket-js | 5.0.6 | 기존 시스템 활용 |

### 9.2 패키지 구조 (Monorepo) - v2.0.0 현재

```
youtuber_vertuber/
  packages/
    vtuber/                        # VMC Client 패키지
      src/
        vmc-client.ts              # VMC Protocol UDP 클라이언트
        avatar-controller.ts       # 우선순위 큐 기반 표정 제어
        reaction-mapper.ts         # 이벤트 → 표정 매핑 로직
        types.ts                   # VTuber 전용 타입 정의
        index.ts                   # 패키지 엔트리포인트
      tests/
        vmc-client.test.ts         # VMC 클라이언트 단위 테스트
        avatar-controller.test.ts  # AvatarController 단위 테스트
        reaction-mapper.test.ts    # ReactionMapper 단위 테스트
      package.json                 # 의존성: osc, @youtuber/shared

    shared/                        # 공유 타입 정의
      src/
        types/
          index.ts                 # VTuber 메시지 타입

  archive/                         # 아카이빙된 코드 (git 제외)
    stream-server/                 # WebSocket, GitHub Webhook, OBS Overlay
```

### 9.3 WebSocket 메시지 타입 확장

**packages/shared/src/types/index.ts 수정**:
```typescript
export type MessageType =
  // ... 기존 타입
  | 'vtuber:expression'    // 아바타 표정 변경 트리거
  | 'vtuber:status'        // VSeeFace 연결 상태
  | 'vtuber:tracking';     // 웹캠 추적 데이터 (선택사항)

export type SubscriptionChannel =
  // ... 기존 채널
  | 'vtuber';

export interface VTuberExpressionPayload {
  expression: 'happy' | 'surprised' | 'neutral' | 'focused' | 'sorrow';
  duration: number;  // ms (지속 시간)
  trigger: 'commit' | 'pr_merged' | 'test_passed' | 'test_failed' | 'chat';
  metadata?: {
    repo?: string;
    message?: string;
  };
}

export interface VTuberStatusPayload {
  connected: boolean;
  vmcHost: string;
  vmcPort: number;
  avatarName?: string;
  lastUpdate: string;
}
```

### 9.4 GitHub Webhook 연동

**packages/stream-server/src/github-webhook.ts 수정**:
```typescript
function handlePush(payload: GitHubPushEvent): void {
  const commits = payload.commits || [];
  const repo = payload.repository.name;

  commits.forEach((commit) => {
    // ... 기존 로직 (CommitPayload 생성, 브로드캐스트)

    // [신규] 아바타 반응 추가
    wsManager.broadcast('vtuber', {
      type: 'vtuber:expression',
      payload: {
        expression: 'happy',
        duration: 2000,
        trigger: 'commit',
        metadata: {
          repo,
          message: commit.message.split('\n')[0]
        }
      } as VTuberExpressionPayload,
      timestamp: new Date().toISOString(),
    });

    console.log(`[VTuber] Triggered happy expression for commit: ${repo}`);
  });
}

// handlePullRequest, handleCheckRun 함수도 유사하게 수정
```

### 9.5 반응 매핑 테이블

| GitHub 이벤트 | 표정 | 지속시간 | 우선순위 | Phase |
|--------------|------|---------|---------|-------|
| Commit | happy | 2초 | Must Have | Phase 3 |
| PR Opened | neutral | 2초 | Nice to Have | Phase 3 |
| PR Merged | surprised (기쁨) | 3초 | Must Have | Phase 3 |
| Test Passed (CI) | focused (1초) → happy (2초) | 3초 | Must Have | Phase 3 |
| Test Failed (CI) | sorrow | 3초 | Nice to Have | Phase 3 |
| Issue Closed | neutral | 2초 | Nice to Have | Phase 4 |

### 9.6 VMC Protocol 연동

**packages/vtuber/src/vmc-client.ts 구현 예시**:
```typescript
import osc from 'osc';

export class VMCClient {
  private udpPort: osc.UDPPort;
  private connected: boolean = false;

  constructor(
    private host: string = 'localhost',
    private port: number = 39539
  ) {
    this.udpPort = new osc.UDPPort({
      localAddress: '0.0.0.0',
      localPort: 0,
      metadata: true
    });
  }

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.udpPort.open();
      this.udpPort.on('ready', () => {
        console.log('[VMC] UDP Port ready');
        this.connected = true;
        resolve();
      });
      this.udpPort.on('error', (err) => {
        console.error('[VMC] Error:', err);
        reject(err);
      });
    });
  }

  onBlendShapeUpdate(callback: (blendShapes: BlendShapeData) => void): void {
    this.udpPort.on('message', (oscMsg) => {
      if (oscMsg.address.startsWith('/VMC/Ext/Blend/Val')) {
        // BlendShape 데이터 파싱
        const blendShapeName = oscMsg.address.split('/').pop();
        const value = oscMsg.args[0];
        callback({ [blendShapeName]: value });
      }
    });
  }

  sendExpression(expression: string, value: number = 1.0): void {
    if (!this.connected) {
      console.warn('[VMC] Not connected, cannot send expression');
      return;
    }

    this.udpPort.send({
      address: `/VMC/Ext/Blend/Apply`,
      args: [
        { type: 's', value: expression },  // Joy, Angry, Sorrow, Fun
        { type: 'f', value }
      ]
    }, this.host, this.port);
  }

  disconnect(): void {
    this.udpPort.close();
    this.connected = false;
  }
}

export interface BlendShapeData {
  [key: string]: number;  // e.g., { "Joy": 0.8, "Angry": 0.0 }
}
```

### 9.7 VSeeFace 연동 설계

**설치 및 설정**:
1. VSeeFace 다운로드: https://www.vseeface.icu/
2. VSeeFace 실행 → Settings → General
3. VMC Protocol 활성화:
   - Protocol: OSC
   - Port: 39539 (기본값)
   - Enable Sending: ON
   - Enable Receiving: ON

**VRoid Hub 아바타 다운로드**:
1. VRoid Hub 방문: https://hub.vroid.com/
2. 무료 라이선스 아바타 검색 (검색어: "programmer", "coder", "casual")
3. VRM 파일 다운로드 (3개 후보 선정)
4. VSeeFace → Load Model → VRM 파일 선택

**VMC Client 구현**:
- Node.js osc 라이브러리 사용
- BlendShape 데이터 수신: Joy, Angry, Sorrow, Fun, Blink 등
- 30fps 데이터 수신 목표

### 9.8 아바타 반응 시스템

**ReactionMapper 구현** (packages/vtuber/src/reaction-mapper.ts):
```typescript
export class ReactionMapper {
  private static expressionMap = {
    commit: { expression: 'happy', duration: 2000 },
    pr_merged: { expression: 'surprised', duration: 3000 },
    test_passed: [
      { expression: 'focused', duration: 1000 },
      { expression: 'happy', duration: 2000 }
    ],
    test_failed: { expression: 'sorrow', duration: 3000 },
    chat_positive: { expression: 'happy', duration: 2000 },
  };

  static mapGitHubEvent(event: string): ExpressionSequence {
    return this.expressionMap[event] || { expression: 'neutral', duration: 1000 };
  }

  static mapChatEmotion(emotion: string): ExpressionSequence {
    if (emotion === 'positive' || emotion === 'excited') {
      return { expression: 'happy', duration: 2000 };
    } else if (emotion === 'curious') {
      return { expression: 'surprised', duration: 2000 };
    }
    return { expression: 'neutral', duration: 1000 };
  }
}
```

**우선순위 큐** (동시 이벤트 처리):
- Commit과 채팅이 동시 발생 → Commit 우선 (GitHub 이벤트 > 채팅)
- Test Passed가 진행 중 → 다른 표정 요청 무시 (현재 표정 완료 후 처리)

### 9.9 외부 의존성

- **VSeeFace**: v1.13.38+ (무료, Windows 전용)
- **osc (Node.js)**: ^2.4.0 (VMC Protocol 통신)
- **youtuber_chatbot**: Port 3002 (감정 분석 API)
- **OBS Studio**: v28.0+ (WebSocket 4.9.1+)

### 9.10 성능 요구사항

- **VMC 데이터 수신**: 30fps (33ms 간격)
- **GitHub → 아바타 반응**: < 1초
- **채팅 → 아바타 반응**: < 2초 (감정 분석 포함)
- **OBS 방송 프레임률**: 60fps 유지 (아바타는 30fps, 오버레이는 60fps)
- **메모리 사용**: packages/vtuber 패키지 < 50MB

### 9.11 보안 고려사항

- [x] **VMC Protocol**: 로컬 네트워크만 허용 (localhost:39539, 외부 접근 차단)
- [x] **GitHub Webhook**: 서명 검증 (기존 시스템 활용, HMAC SHA256)
- [x] **youtuber_chatbot API**: localhost만 허용 (Port 3002)
- [x] **입력 검증**: VRM 파일 업로드 시 파일 크기 제한 (< 50MB)
- [x] **XSS 방지**: OBS 오버레이 HTML에서 사용자 입력 sanitize

---

## 10. 성공 지표

### 정량적 지표

| 지표 | 목표값 | 측정 방법 |
|------|--------|----------|
| 아바타 표시 안정성 | 99% | VMC 연결 유지 시간 / 총 방송 시간 |
| GitHub 반응 지연시간 | < 1초 | Webhook 수신 → 표정 변경 시간 |
| 채팅 반응 지연시간 | < 2초 | 메시지 → 감정 분석 → 표정 변경 |
| 시청자 평균 시청 시간 | 30% 증가 | YouTube Analytics (Before/After) |
| 채팅 참여도 | 50% 증가 | 메시지 수 / 시청자 수 |

### 정성적 지표

- 시청자 피드백: "아바타 반응이 재미있다", "코딩 과정이 이해하기 쉬워졌다"
- 방송 몰입도: 시청자가 GitHub 이벤트를 기다리며 참여
- 브랜드 인지도: "AI 코딩 버튜버"로 차별화

---

## 11. 마일스톤

| Phase | 설명 | 상태 | 완료 기준 |
|-------|------|------|----------|
| **Phase 1** | VSeeFace 기본 연동 | ✅ 완료 | VMC 데이터 수신 확인, packages/vtuber 패키지 생성 |
| **Phase 2** | 표정 제어 및 OBS | 🔄 진행중 | AvatarController, VSeeFace 연결 테스트 |
| ~~Phase 3~~ | ~~GitHub 연동~~ | ⏸️ 아카이빙 | `archive/stream-server/`로 이동 |
| ~~Phase 4~~ | ~~채팅 상호작용~~ | ⏸️ 아카이빙 | `archive/stream-server/`로 이동 |

**Phase 1 완료 항목**:
- [x] packages/vtuber 패키지 생성
- [x] VMCClient 클래스 구현 (connect, disconnect, sendExpression)
- [x] BlendShape 데이터 송수신
- [x] 단위 테스트 커버리지 > 80%
- [x] WebSocket 메시지 타입 추가 (shared)

**Phase 2 진행 항목**:
- [x] AvatarController 클래스 구현
- [x] ReactionMapper 클래스 구현
- [x] VSeeFace Window Capture 가이드 작성
- [ ] VSeeFace 실행 연동 테스트
- [ ] VRoid Hub 아바타 선택

---

## 12. 미결 질문

- [ ] **VRoid Hub 아바타 선택**: 프로그래머 컨셉 3개 후보 중 최종 1개 선정 (Phase 1에서 결정)
- [ ] **반응 애니메이션 우선순위**: Commit과 채팅이 동시 발생 시 어느 것 우선? (Phase 3에서 결정)
- [ ] **TTS 음성 합성 추가 여부**: v2에서 고려할 것인가, v3으로 미룰 것인가?
- [ ] **아바타 교체 빈도**: 방송마다 교체할 것인가, 고정할 것인가?
- [ ] **OBS Window Capture vs Browser Source**: 성능 이슈 시 Browser Source (WebGL)로 전환할 것인가?

---

## 13. 첨부 자료

### 와이어프레임 / 목업

- **HTML 목업**: [docs/mockups/vseface-overlay.html](../../docs/mockups/vseface-overlay.html)
- **스크린샷**: [docs/images/vseface-overlay.png](../../docs/images/vseface-overlay.png)

### 아키텍처 다이어그램

- **시스템 아키텍처**: [docs/images/vseface-architecture.mmd](../../docs/images/vseface-architecture.mmd)
- **데이터 흐름**: [docs/images/vseface-dataflow.mmd](../../docs/images/vseface-dataflow.mmd)

### 참고 자료

- VSeeFace 공식: https://www.vseeface.icu/
- VMC Protocol: https://protocol.vmc.info/
- VRoid Hub: https://hub.vroid.com/
- youtuber 프로젝트 README: [../../README.md](../../README.md)
- youtuber_chatbot PRD: [../../../youtuber_chatbot/docs/PRD-0002-chatbot.md](../../../youtuber_chatbot/docs/PRD-0002-chatbot.md)

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2026-01-04 | 1.0.0 | 초안 작성 (Draft) | Claude |
| 2026-01-06 | 2.0.0 | **범위 축소**: Phase 3-4 아카이빙, VSeeFace 활성화 집중 | Claude |

---

**검토자**: (사용자 승인 대기)
**승인일**: (미정)
**다음 단계**: Phase 1 개발 시작 (`/work "PRD-0001 Phase 1 VSeeFace 기본 연동 구현"`)
