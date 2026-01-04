# Task List: VSeeFace 버튜버 기능 통합 (PRD-0001)

**PRD**: PRD-0001
**Created**: 2026-01-04
**Status**: In Progress
**Priority**: High
**Estimated Total**: 96h (12일, 하루 8시간 기준)

---

## Progress Summary

| Phase | Tasks | Completed | Progress | Status |
|-------|-------|-----------|----------|--------|
| Phase 1 | 6 | 0 | 0% | Pending |
| Phase 2 | 5 | 0 | 0% | Pending |
| Phase 3 | 5 | 0 | 0% | Pending |
| Phase 4 | 5 | 0 | 0% | Pending |
| **Total** | **21** | **0** | **0%** | In Progress |

---

## Phase 1: VSeeFace 기본 연동 (D+0 ~ D+3)

**목표**: VMC Protocol을 통한 VSeeFace 연결 및 BlendShape 데이터 수신

### Task 1.0: VSeeFace 설치 및 설정
- [ ] **Task 1.0**: VSeeFace 설치 및 VMC Protocol 설정
  - Priority: High
  - Due: 2026-01-05
  - Estimate: 2h
  - Tags: setup, phase1, documentation
  - **Subtasks**:
    - [ ] VSeeFace v1.13.38+ 다운로드 및 설치
    - [ ] VMC Protocol 활성화 (Port 39539)
    - [ ] 웹캠 연결 테스트
    - [ ] 설정 가이드 문서 작성 (README.md 또는 SETUP.md)

### Task 1.1: VRoid 아바타 준비
- [ ] **Task 1.1**: VRoid Hub 무료 아바타 선택 및 다운로드
  - Priority: High
  - Due: 2026-01-05
  - Estimate: 3h
  - Tags: setup, phase1, avatar
  - **Subtasks**:
    - [ ] VRoid Hub에서 프로그래머/코더 컨셉 아바타 검색
    - [ ] 3개 후보 선정 (무료 라이선스 확인)
    - [ ] VRM 파일 다운로드
    - [ ] VSeeFace에서 아바타 로드 테스트
    - [ ] 최종 1개 아바타 선택

### Task 1.2: packages/vtuber 패키지 생성
- [ ] **Task 1.2**: Monorepo에 vtuber 패키지 추가
  - Priority: High
  - Due: 2026-01-06
  - Estimate: 2h
  - Tags: phase1, setup, monorepo
  - PR: #101
  - Branch: feat/PRD-0001-101-vtuber-package
  - **Subtasks**:
    - [ ] pnpm-workspace.yaml에 packages/vtuber 추가
    - [ ] package.json 생성 (의존성: osc@^2.4.0, @youtuber/shared)
    - [ ] tsconfig.json 설정 (tsconfig.base.json 확장)
    - [ ] 기본 디렉토리 구조 생성 (src/, tests/)
    - [ ] .gitignore 설정

### Task 1.3: VMC Protocol 클라이언트 구현
- [ ] **Task 1.3**: VMCClient 클래스 구현
  - Priority: High
  - Due: 2026-01-06
  - Estimate: 6h
  - Tags: phase1, implementation, vmc
  - PR: #102
  - Branch: feat/PRD-0001-102-vmc-client
  - Depends: 1.2
  - **Subtasks**:
    - [ ] vmc-client.ts 파일 생성
    - [ ] VMCClient 클래스 구현 (osc 라이브러리 사용)
    - [ ] connect() 메서드 (UDP Port 연결)
    - [ ] disconnect() 메서드
    - [ ] onBlendShapeUpdate() 메서드 (BlendShape 데이터 수신)
    - [ ] sendExpression() 메서드 (표정 전송)
    - [ ] 연결 상태 모니터링 (health check 5초 간격)
    - [ ] 에러 핸들링 (재연결 로직)

### Task 1.4: VSeeFace 연결 테스트 작성
- [ ] **Task 1.4**: VMC Client 단위 테스트
  - Priority: High
  - Due: 2026-01-07
  - Estimate: 4h
  - Tags: phase1, testing, tdd
  - PR: #102
  - Branch: feat/PRD-0001-102-vmc-client
  - Depends: 1.3
  - **Subtasks**:
    - [ ] vmc-client.test.ts 생성
    - [ ] VMC Client 연결/해제 테스트
    - [ ] BlendShape 데이터 파싱 테스트
    - [ ] 에러 핸들링 테스트 (연결 실패, 타임아웃)
    - [ ] Mock OSC 서버 구현 (테스트용)
    - [ ] 커버리지 > 80% 확인

### Task 1.5: WebSocket 메시지 타입 추가
- [ ] **Task 1.5**: shared 패키지 타입 확장
  - Priority: High
  - Due: 2026-01-07
  - Estimate: 3h
  - Tags: phase1, types, shared
  - PR: #103
  - Branch: feat/PRD-0001-103-shared-types
  - **Subtasks**:
    - [ ] packages/shared/src/types/index.ts 수정
    - [ ] MessageType에 'vtuber:expression', 'vtuber:status', 'vtuber:tracking' 추가
    - [ ] SubscriptionChannel에 'vtuber' 추가
    - [ ] VTuberExpressionPayload 인터페이스 정의
    - [ ] VTuberStatusPayload 인터페이스 정의
    - [ ] VTuberTrackingPayload 인터페이스 정의 (선택사항)
    - [ ] 타입 export 확인

**Phase 1 Estimate**: 20h (3일)

---

## Phase 2: OBS 오버레이 (D+4 ~ D+5)

**목표**: 320x180 "얼굴 캠" 영역에 VSeeFace 아바타 표시

### Task 2.0: HTML 오버레이 파일 생성
- [ ] **Task 2.0**: OBS Browser Source 오버레이 구현
  - Priority: High
  - Due: 2026-01-08
  - Estimate: 4h
  - Tags: phase2, frontend, obs
  - PR: #104
  - Branch: feat/PRD-0001-104-overlay
  - **Subtasks**:
    - [ ] packages/stream-server/overlay/index.html 생성
    - [ ] packages/stream-server/overlay/styles.css 생성
    - [ ] 1920x1080 레이아웃 구현 (화면 캡처 1600x900, 아바타 320x180)
    - [ ] CSS Grid/Flexbox로 반응형 레이아웃
    - [ ] WebSocket 연결 로직 (ws://localhost:3001)

### Task 2.1: 아바타 프레임 컴포넌트
- [ ] **Task 2.1**: 아바타 전용 프레임 구현
  - Priority: High
  - Due: 2026-01-08
  - Estimate: 3h
  - Tags: phase2, frontend, component
  - PR: #104
  - Branch: feat/PRD-0001-104-overlay
  - Depends: 2.0
  - **Subtasks**:
    - [ ] vtuber-frame.html 생성 (아바타 전용 프레임)
    - [ ] VSeeFace 연결 상태 표시 (연결됨 🟢 / 끊김 🔴)
    - [ ] 표정 인디케이터 (happy, surprised 등)
    - [ ] CSS 애니메이션 (pulse, blink)
    - [ ] TypeScript로 WebSocket 메시지 핸들링

### Task 2.2: OBS Browser Source 설정 가이드
- [ ] **Task 2.2**: OBS 설정 문서화
  - Priority: Medium
  - Due: 2026-01-09
  - Estimate: 2h
  - Tags: phase2, documentation, obs
  - PR: #105
  - Branch: feat/PRD-0001-105-obs-setup
  - **Subtasks**:
    - [ ] OBS Browser Source 설정 가이드 작성 (docs/OBS_SETUP.md)
    - [ ] Browser Source URL: http://localhost:3001/overlay
    - [ ] 크기: 1920x1080
    - [ ] Chroma Key 설정 방법 (배경 투명화)
    - [ ] 스크린샷 포함 (설정 화면)

### Task 2.3: VSeeFace Window Capture 통합
- [ ] **Task 2.3**: VSeeFace 화면 캡처 설정
  - Priority: High
  - Due: 2026-01-09
  - Estimate: 2h
  - Tags: phase2, obs, integration
  - PR: #105
  - Branch: feat/PRD-0001-105-obs-setup
  - **Subtasks**:
    - [ ] VSeeFace "Transparent Background" 활성화 방법 문서화
    - [ ] OBS Window Capture 추가 (VSeeFace 선택)
    - [ ] Crop/Scale → 320x180 영역
    - [ ] 레이아웃 위치 조정 (우측 상단)
    - [ ] 테스트 (아바타 표시 확인)

### Task 2.4: 레이아웃 반응형 테스트
- [ ] **Task 2.4**: 오버레이 레이아웃 테스트
  - Priority: Medium
  - Due: 2026-01-09
  - Estimate: 3h
  - Tags: phase2, testing, e2e
  - PR: #106
  - Branch: feat/PRD-0001-106-layout-test
  - **Subtasks**:
    - [ ] 1920x1080 레이아웃 테스트
    - [ ] 아바타 영역 깨짐 없는지 확인
    - [ ] 멀티 프로젝트 활동 카드 정렬 확인
    - [ ] Active Projects 패널 스크롤 테스트
    - [ ] Playwright E2E 테스트 작성 (선택사항)

**Phase 2 Estimate**: 14h (2일)

---

## Phase 3: GitHub 연동 (아바타 반응) (D+6 ~ D+8)

**목표**: Commit/PR/CI 이벤트 시 아바타 표정 자동 변경

### Task 3.0: AvatarController 클래스 구현
- [ ] **Task 3.0**: 아바타 상태 관리 로직
  - Priority: High
  - Due: 2026-01-10
  - Estimate: 5h
  - Tags: phase3, implementation, controller
  - PR: #107
  - Branch: feat/PRD-0001-107-avatar-controller
  - **Subtasks**:
    - [ ] avatar-controller.ts 생성
    - [ ] AvatarController 클래스 구현
    - [ ] setExpression() 메서드 (표정 설정)
    - [ ] queueExpression() 메서드 (우선순위 큐)
    - [ ] getCurrentExpression() 메서드
    - [ ] 표정 지속 시간 관리 (duration, setTimeout)
    - [ ] 우선순위 로직 (GitHub > 채팅)
    - [ ] 단위 테스트 작성

### Task 3.1: 이벤트-표정 매핑 로직
- [ ] **Task 3.1**: ReactionMapper 구현
  - Priority: High
  - Due: 2026-01-10
  - Estimate: 4h
  - Tags: phase3, implementation, mapper
  - PR: #107
  - Branch: feat/PRD-0001-107-avatar-controller
  - Depends: 3.0
  - **Subtasks**:
    - [ ] reaction-mapper.ts 생성
    - [ ] ReactionMapper 클래스 구현
    - [ ] mapGitHubEvent() 함수 (Commit → happy, PR Merged → surprised)
    - [ ] expressionMap 테이블 정의 (JSON 또는 TypeScript 객체)
    - [ ] mapChatEmotion() 함수 (positive → happy)
    - [ ] 단위 테스트 작성 (reaction-mapper.test.ts)

### Task 3.2: github-webhook.ts 수정
- [ ] **Task 3.2**: GitHub Webhook 핸들러에 아바타 반응 추가
  - Priority: High
  - Due: 2026-01-11
  - Estimate: 4h
  - Tags: phase3, implementation, webhook
  - PR: #108
  - Branch: feat/PRD-0001-108-github-reaction
  - Depends: 3.1
  - **Subtasks**:
    - [ ] packages/stream-server/src/github-webhook.ts 수정
    - [ ] handlePush() 함수에 아바타 반응 추가
    - [ ] handlePullRequest() 함수에 아바타 반응 추가
    - [ ] handleCheckRun() 함수에 아바타 반응 추가
    - [ ] wsManager.broadcast('vtuber', {...}) 호출
    - [ ] 반응 지연시간 측정 로깅

### Task 3.3: 표정 애니메이션 테스트
- [ ] **Task 3.3**: 통합 테스트 (GitHub → 아바타)
  - Priority: High
  - Due: 2026-01-11
  - Estimate: 4h
  - Tags: phase3, testing, integration
  - PR: #108
  - Branch: feat/PRD-0001-108-github-reaction
  - Depends: 3.2
  - **Subtasks**:
    - [ ] github-webhook.integration.test.ts 생성
    - [ ] Mock GitHub Webhook 전송 (Commit, PR, CI)
    - [ ] WebSocket 메시지 수신 확인
    - [ ] 아바타 표정 변경 확인 (VMC Client Mock)
    - [ ] 반응 지연시간 < 1초 검증

### Task 3.4: 우선순위 반응 구현
- [ ] **Task 3.4**: 핵심 반응 (Commit, PR, CI) 완성
  - Priority: High
  - Due: 2026-01-12
  - Estimate: 5h
  - Tags: phase3, implementation, priority
  - PR: #109
  - Branch: feat/PRD-0001-109-priority-reactions
  - Depends: 3.3
  - **Subtasks**:
    - [ ] Commit → happy (2초) 구현 및 테스트
    - [ ] PR Merged → surprised (3초) 구현 및 테스트
    - [ ] Test Passed (CI) → focused (1초) → happy (2초) 시퀀스 구현
    - [ ] 우선순위 큐 동작 확인 (동시 이벤트 처리)
    - [ ] 수동 테스트 (실제 GitHub Webhook 전송)

**Phase 3 Estimate**: 22h (3일)

---

## Phase 4: 채팅 상호작용 (D+9 ~ D+12)

**목표**: YouTube 채팅 감정 분석 → 아바타 표정 변경

### Task 4.0: youtuber_chatbot API 연동
- [ ] **Task 4.0**: 채팅봇 감정 분석 API 클라이언트
  - Priority: High
  - Due: 2026-01-13
  - Estimate: 5h
  - Tags: phase4, implementation, api
  - PR: #110
  - Branch: feat/PRD-0001-110-chatbot-integration
  - **Subtasks**:
    - [ ] chatbot-client.ts 생성
    - [ ] POST http://localhost:3002/api/chat/analyze 호출
    - [ ] 감정 분석 결과 수신 (positive, negative, neutral)
    - [ ] 에러 핸들링 (타임아웃 2초, fallback to neutral)
    - [ ] 재시도 로직 (최대 3회)
    - [ ] 단위 테스트 (Mock HTTP 서버)

### Task 4.1: 감정 분석 → 표정 변환 로직
- [ ] **Task 4.1**: 채팅 감정 매핑
  - Priority: High
  - Due: 2026-01-13
  - Estimate: 3h
  - Tags: phase4, implementation, mapper
  - PR: #110
  - Branch: feat/PRD-0001-110-chatbot-integration
  - Depends: 4.0
  - **Subtasks**:
    - [ ] ReactionMapper.mapChatEmotion() 함수 추가
    - [ ] positive/excited → happy
    - [ ] curious → surprised
    - [ ] neutral → neutral
    - [ ] 스팸 방지 로직 (동일 감정 최소 5초 간격)
    - [ ] 단위 테스트 작성

### Task 4.2: 채팅 WebSocket 메시지 핸들링
- [ ] **Task 4.2**: 채팅 메시지 처리
  - Priority: High
  - Due: 2026-01-14
  - Estimate: 4h
  - Tags: phase4, implementation, websocket
  - PR: #111
  - Branch: feat/PRD-0001-111-chat-handling
  - Depends: 4.1
  - **Subtasks**:
    - [ ] stream-server에 chat 채널 핸들러 추가
    - [ ] 채팅 메시지 수신 → 감정 분석 → 표정 트리거 파이프라인
    - [ ] WebSocket 브로드캐스트 (type: 'vtuber:expression', trigger: 'chat')
    - [ ] 에러 핸들링 (chatbot API 실패 시)
    - [ ] 로깅 (감정 분석 결과, 표정 변경)

### Task 4.3: 통합 테스트 (E2E)
- [ ] **Task 4.3**: 전체 워크플로우 E2E 테스트
  - Priority: High
  - Due: 2026-01-15
  - Estimate: 6h
  - Tags: phase4, testing, e2e
  - PR: #112
  - Branch: feat/PRD-0001-112-e2e-test
  - Depends: 4.2
  - **Subtasks**:
    - [ ] Playwright E2E 테스트 작성 (tests/e2e/vtuber.spec.ts)
    - [ ] 시나리오 1: VSeeFace 연결 → 아바타 표시
    - [ ] 시나리오 2: GitHub Commit → 표정 변경 (happy)
    - [ ] 시나리오 3: 채팅 메시지 → 표정 변경 (positive → happy)
    - [ ] 시나리오 4: 동시 이벤트 (우선순위 큐 테스트)
    - [ ] 모든 Phase 통합 검증

### Task 4.4: 문서화 (README, API 가이드)
- [ ] **Task 4.4**: 프로젝트 문서화 완료
  - Priority: Medium
  - Due: 2026-01-16
  - Estimate: 6h
  - Tags: phase4, documentation
  - PR: #113
  - Branch: feat/PRD-0001-113-documentation
  - **Subtasks**:
    - [ ] README.md 업데이트 (VSeeFace 기능 추가, 설치 가이드)
    - [ ] packages/vtuber/README.md 작성 (API 문서, 클래스 설명)
    - [ ] docs/VSEFACE_SETUP.md 작성 (VSeeFace 설치 및 설정 상세 가이드)
    - [ ] docs/TROUBLESHOOTING.md 작성 (FAQ, 문제 해결)
    - [ ] API 엔드포인트 문서화 (Swagger/OpenAPI 선택사항)
    - [ ] 코드 주석 업데이트 (JSDoc)

**Phase 4 Estimate**: 24h (4일)

---

## Daily Tasks (매일)

### 일일 체크리스트
- [ ] 아침: 오늘의 작업 계획 (`/todo today`)
- [ ] 작업 전: 브랜치 생성 및 TDD 시작 (`/tdd`)
- [ ] 작업 중: 진행 상황 로깅 (`/todo --log "작업 내용"`)
- [ ] 작업 후: 커밋 및 PR 생성 (`/commit`, `gh pr create`)
- [ ] 저녁: 진행률 확인 (`/todo progress`)

---

## Dependencies Graph

```
Phase 1:
1.0 → 1.1 (병렬 가능)
1.2 → 1.3 → 1.4
1.5 (독립)

Phase 2:
2.0 → 2.1
2.2, 2.3 (병렬 가능, 2.0 의존)
2.4 (전체 의존)

Phase 3:
3.0 → 3.1 → 3.2 → 3.3 → 3.4

Phase 4:
4.0 → 4.1 → 4.2 → 4.3
4.4 (독립, 마지막)
```

---

## Risk Mitigation

| Task | Risk | Mitigation | Status |
|------|------|------------|--------|
| 1.3 | VMC Protocol 불안정 | Mock 서버로 개발 우선, VSeeFace 연결은 나중 | Planned |
| 2.3 | OBS 성능 저하 | Browser Source로 전환 준비 | Monitoring |
| 3.2 | GitHub Webhook 지연 | 로깅으로 병목 구간 파악 | Monitoring |
| 4.0 | chatbot API 타임아웃 | Fallback 표정 (neutral) | Planned |

---

## Next Steps

1. **즉시 시작**: Task 1.0 (VSeeFace 설치 및 설정)
   ```bash
   /todo status 1.0 in_progress
   ```

2. **브랜치 생성**:
   ```bash
   git checkout -b feat/PRD-0001-101-vtuber-package
   ```

3. **TDD 시작**:
   ```bash
   /tdd  # Red-Green-Refactor
   ```

4. **진행률 추적**:
   ```bash
   /todo progress
   /todo list --phase=1
   ```

---

## Related Documents

- **PRD**: [tasks/prds/0001-prd-vseface-integration.md](prds/0001-prd-vseface-integration.md)
- **Checklist**: [docs/checklists/PRD-0001.md](../docs/checklists/PRD-0001.md)
- **Plan**: [C:\Users\레노버\.claude\plans\swirling-meandering-adleman.md]()

---

**Created**: 2026-01-04
**Last Updated**: 2026-01-04
**Estimated Completion**: 2026-01-16 (D+12)
