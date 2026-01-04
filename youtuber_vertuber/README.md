# youtuber_vertuber

**VSeeFace 버튜버 기능 통합 프로젝트**

AI 코딩 스트리밍에 버튜버 아바타를 연동하여 시청자 참여도를 높이는 인터랙티브 방송 시스템입니다.

---

## 개요

youtuber_vertuber는 VSeeFace와 VMC Protocol을 활용하여 웹캠 기반 버튜버 아바타를 OBS 오버레이에 실시간으로 표시하고, GitHub 이벤트(Commit, PR, CI)와 YouTube 채팅에 반응하는 시스템입니다.

### 주요 기능

- **실시간 아바타 추적**: VSeeFace를 통한 웹캠 얼굴 추적 (30fps)
- **GitHub 이벤트 반응**: Commit/PR/CI 성공 시 아바타 표정 자동 변경
- **채팅 상호작용**: YouTube 채팅 감정 분석 → 아바타 반응
- **OBS 오버레이**: 320x180 "얼굴 캠" 영역에 아바타 표시
- **자동화**: VMC Protocol 자동 연결 및 상태 모니터링

---

## 프로젝트 상태

| Phase | 목표 | 진행률 | 상태 |
|-------|------|--------|------|
| **Phase 1** | VSeeFace 기본 연동 | 0% | Pending |
| **Phase 2** | OBS 오버레이 | 0% | Pending |
| **Phase 3** | GitHub 연동 | 0% | Pending |
| **Phase 4** | 채팅 상호작용 | 0% | Pending |

**현재 작업**: Phase 1 - VSeeFace 설치 및 VMC Protocol 연동

**예상 완료**: 2026-01-16 (D+12)

---

## 빠른 시작

### 사전 요구사항

- **OS**: Windows 10 (64-bit) 이상
- **Node.js**: v18+ (LTS)
- **pnpm**: v8+
- **웹캠**: HD 웹캠 (720p 이상)
- **VSeeFace**: v1.13.38+

### 설치

```bash
# 1. VSeeFace 설치 (가이드 참조)
# docs/VSEFACE_SETUP.md 참조

# 2. 프로젝트 클론
git clone https://github.com/yourusername/youtuber_vertuber.git
cd youtuber_vertuber

# 3. 의존성 설치 (Phase 1 완료 후)
pnpm install

# 4. 개발 서버 실행 (Phase 1 완료 후)
pnpm dev
```

### VSeeFace 설정

1. VSeeFace 설치 및 아바타 로드
2. VMC Protocol 활성화 (Port 39539)
3. 배경 투명화 활성화

**상세 가이드**: [docs/VSEFACE_SETUP.md](docs/VSEFACE_SETUP.md)

---

## 아키텍처

### 시스템 구성

```
┌─────────────────┐
│   VSeeFace      │ ← 웹캠 얼굴 추적
│   (VMC Server)  │
└────────┬────────┘
         │ VMC Protocol (UDP:39539)
         │ BlendShape 데이터 (30fps)
         ▼
┌─────────────────┐
│  VMC Client     │
│  (packages/     │
│   vtuber)       │
└────────┬────────┘
         │ WebSocket
         ▼
┌─────────────────┐     ┌──────────────────┐
│  Stream Server  │◄────┤  GitHub Webhook  │
│  (WS Manager)   │     │  (Commit/PR/CI)  │
└────────┬────────┘     └──────────────────┘
         │
         │ WebSocket          ┌──────────────────┐
         ├───────────────────►│  OBS Overlay     │
         │                    │  (Browser Source)│
         │                    └──────────────────┘
         │
         ▼
┌─────────────────┐
│  Chatbot        │ ← YouTube 채팅 감정 분석
│  (youtuber_     │
│   chatbot)      │
└─────────────────┘
```

### 데이터 흐름

1. **VSeeFace** → VMC Protocol → **VMC Client**
2. **VMC Client** → WebSocket → **Stream Server**
3. **GitHub Webhook** → **Stream Server** → 표정 트리거
4. **YouTube 채팅** → **Chatbot** → 감정 분석 → **Stream Server**
5. **Stream Server** → WebSocket → **OBS Overlay** → 아바타 반응 표시

---

## 디렉토리 구조

```
youtuber_vertuber/
├── docs/                          # 문서
│   ├── VSEFACE_SETUP.md          # VSeeFace 설치 가이드
│   ├── checklists/               # Phase별 체크리스트
│   │   └── PRD-0001.md           # PRD-0001 Checklist
│   ├── images/                   # 이미지 및 다이어그램
│   └── mockups/                  # HTML 목업
├── tasks/                         # 태스크 및 PRD
│   ├── 0001-tasks-vseface-integration.md  # Task 리스트
│   └── prds/
│       └── 0001-prd-vseface-integration.md  # PRD 문서
├── logs/                          # 로그 파일
├── packages/                      # Monorepo 패키지 (Phase 1 이후 생성)
│   ├── vtuber/                   # VMC Client, AvatarController
│   ├── stream-server/            # WebSocket 서버, GitHub Webhook
│   └── shared/                   # 공유 타입 정의
├── README.md                      # 프로젝트 개요 (이 파일)
└── package.json                   # Monorepo 설정 (Phase 1 이후 생성)
```

---

## Phase별 개발 계획

### Phase 1: VSeeFace 기본 연동 (D+0 ~ D+3)

**목표**: VMC Protocol을 통한 VSeeFace 연결 및 BlendShape 데이터 수신

**작업**:
- [x] VSeeFace 설치 및 설정 가이드 작성
- [ ] VRoid Hub 무료 아바타 선택 및 다운로드
- [ ] packages/vtuber 패키지 생성
- [ ] VMC Protocol 클라이언트 구현
- [ ] VSeeFace 연결 테스트 작성
- [ ] WebSocket 메시지 타입 추가 (shared)

**완료 기준**:
- VSeeFace 실행 시 VMC Client 자동 연결
- WebSocket으로 BlendShape 데이터 수신 (30fps)
- 단위 테스트 커버리지 > 80%

### Phase 2: OBS 오버레이 (D+4 ~ D+5)

**목표**: 320x180 "얼굴 캠" 영역에 VSeeFace 아바타 표시

**작업**:
- [ ] HTML 오버레이 파일 생성
- [ ] 아바타 프레임 컴포넌트
- [ ] OBS Browser Source 설정 가이드
- [ ] VSeeFace Window Capture 통합
- [ ] 레이아웃 반응형 테스트

**완료 기준**:
- OBS에서 아바타 320x180 영역 표시
- 배경 투명 처리
- 1920x1080 레이아웃에서 깨짐 없음

### Phase 3: GitHub 연동 (아바타 반응) (D+6 ~ D+8)

**목표**: Commit/PR/CI 이벤트 시 아바타 표정 자동 변경

**작업**:
- [ ] AvatarController 클래스 구현
- [ ] 이벤트-표정 매핑 로직
- [ ] github-webhook.ts 수정
- [ ] 표정 애니메이션 테스트
- [ ] 우선순위 반응 구현

**완료 기준**:
- Commit/PR/CI 이벤트별 표정 변경 동작
- 반응 지연시간 < 1초
- 통합 테스트 통과

### Phase 4: 채팅 상호작용 (D+9 ~ D+12)

**목표**: YouTube 채팅 감정 분석 → 아바타 표정 변경

**작업**:
- [ ] youtuber_chatbot API 연동
- [ ] 감정 분석 → 표정 변환 로직
- [ ] 채팅 WebSocket 메시지 핸들링
- [ ] 통합 테스트 (E2E)
- [ ] 문서화 (README, API 가이드)

**완료 기준**:
- youtuber_chatbot 감정 분석 연동
- 채팅 메시지 → 표정 변경 < 2초
- E2E 테스트 (Playwright)
- 문서화 완료

---

## 기술 스택

### 백엔드
- **Node.js** v18+
- **TypeScript** v5+
- **osc** (VMC Protocol 통신)
- **WebSocket** (실시간 데이터 전송)

### 프론트엔드 (OBS Overlay)
- **HTML5** + **CSS3**
- **JavaScript** (Vanilla)
- **WebSocket Client**

### 외부 연동
- **VSeeFace** (버튜버 아바타)
- **VRoid Hub** (아바타 다운로드)
- **GitHub Webhook** (Commit/PR/CI 이벤트)
- **youtuber_chatbot** (채팅 감정 분석)

### 테스트
- **Vitest** (단위 테스트)
- **Playwright** (E2E 테스트)
- **Mock OSC Server** (VMC Protocol 테스트)

---

## 개발 가이드

### 브랜치 전략

```
main                    # 프로덕션 브랜치
  ├─ feat/PRD-0001-101-vtuber-package
  ├─ feat/PRD-0001-102-vmc-client
  └─ feat/PRD-0001-103-shared-types
```

**브랜치 명명 규칙**: `feat/PRD-0001-<PR번호>-<설명>`

### 커밋 메시지

**Conventional Commits** 형식 사용:

```
<type>: <description> [PRD-0001] #<PR번호>

feat: add VMC Client class [PRD-0001] #102
fix: resolve WebSocket connection issue [PRD-0001] #105
docs: update VSeeFace setup guide [PRD-0001] #101
```

### 테스트 전략

1. **TDD (Test-Driven Development)**: Red → Green → Refactor
2. **단위 테스트**: 모든 클래스/함수 커버리지 > 80%
3. **통합 테스트**: VMC Client ↔ Stream Server 연동 테스트
4. **E2E 테스트**: VSeeFace → OBS 오버레이 전체 워크플로우

---

## 문제 해결

### 일반적인 문제

| 문제 | 해결 방법 |
|------|----------|
| VSeeFace 연결 실패 | VMC Protocol 활성화 확인 (Port 39539) |
| 아바타가 표시되지 않음 | OBS Browser Source URL 확인 (http://localhost:3001/overlay) |
| GitHub Webhook 미수신 | ngrok 또는 공개 URL 설정 확인 |
| 채팅 감정 분석 실패 | youtuber_chatbot API 실행 상태 확인 |

**상세 가이드**: [docs/VSEFACE_SETUP.md](docs/VSEFACE_SETUP.md) > Troubleshooting

---

## 참고 자료

### 공식 문서
- [VSeeFace 공식 사이트](https://www.vseeface.icu/)
- [VMC Protocol 문서](https://protocol.vmc.info/)
- [VRoid Hub](https://hub.vroid.com/)
- [OSC Protocol](https://opensoundcontrol.stanford.edu/)

### 프로젝트 문서
- [PRD-0001: VSeeFace 통합](tasks/prds/0001-prd-vseface-integration.md)
- [Checklist: PRD-0001](docs/checklists/PRD-0001.md)
- [Task List: PRD-0001](tasks/0001-tasks-vseface-integration.md)
- [VSeeFace 설치 가이드](docs/VSEFACE_SETUP.md)

---

## 라이선스

MIT License

---

## 기여

이 프로젝트는 개인 프로젝트입니다. 이슈 및 피드백은 환영합니다!

---

## 연락처

- **작성자**: Claude (AI Assistant)
- **프로젝트**: youtuber_vertuber
- **PRD**: PRD-0001
- **작성일**: 2026-01-04

---

**Last Updated**: 2026-01-04
**Version**: 0.1.0 (Phase 1 진행 중)
