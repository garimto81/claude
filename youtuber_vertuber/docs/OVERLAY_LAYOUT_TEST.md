# OBS 오버레이 레이아웃 테스트 가이드

**버전**: 1.0.0
**작성일**: 2026-01-05
**관련 이슈**: [#85](https://github.com/garimto81/claude/issues/85)
**PRD**: [PRD-0001](../tasks/prds/0001-prd-vseface-integration.md)

---

## 개요

1920x1080 OBS 오버레이 레이아웃이 PRD 요구사항을 충족하는지 검증합니다.

---

## 사전 준비

### 1. 서버 실행

```bash
cd D:\AI\claude01\youtuber_vertuber
pnpm run dev
```

서버가 `http://localhost:3001`에서 실행되어야 합니다.

### 2. 브라우저 개발자 도구 준비

- Chrome 또는 Edge 브라우저 사용
- 개발자 도구 (F12) 열기
- Responsive Design Mode 활성화 (Ctrl+Shift+M)
- 해상도를 `1920 x 1080`으로 설정

---

## 테스트 케이스

### TC-1: 전체 레이아웃 크기 검증

**목적**: 1920x1080 레이아웃이 정확히 구현되었는지 확인

**URL**: `http://localhost:3001/overlay/`

**단계**:
1. 브라우저에서 URL 접속
2. 개발자 도구 → Elements 탭
3. `<body>` 요소 선택
4. Computed 탭에서 width, height 확인

**예상 결과**:
- [ ] `width: 1920px`
- [ ] `height: 1080px`
- [ ] `overflow: hidden`

**실제 결과**:
```
width: _______
height: _______
```

---

### TC-2: CSS Grid 레이아웃 검증

**목적**: 4개 영역이 CSS Grid로 정확히 배치되었는지 확인

**URL**: `http://localhost:3001/overlay/`

**단계**:
1. 개발자 도구 → Elements 탭
2. `.obs-overlay` 요소 선택
3. Computed 탭에서 `display: grid` 확인
4. Layout 탭에서 Grid 시각화 확인

**예상 결과**:
- [ ] `display: grid`
- [ ] `grid-template-columns: 1600px 320px`
- [ ] `grid-template-rows: 900px 180px`
- [ ] 4개 영역 (2x2 그리드)

**Grid 영역**:
```
┌────────────────────┬──────────┐
│  main-screen       │ vtuber-  │
│  (1600x900)        │ frame    │
│                    │ (320x180)│
├────────────────────┼──────────┤
│  project-cards     │ active-  │
│  (1600x180)        │ projects │
│                    │ (320x900)│
└────────────────────┴──────────┘
```

---

### TC-3: 메인 화면 영역 (1600x900)

**목적**: 화면 캡처 영역 크기 검증

**URL**: `http://localhost:3001/overlay/`

**단계**:
1. `.main-screen` 요소 선택
2. Computed 탭에서 width, height 확인
3. `.screen-placeholder` 표시 확인

**예상 결과**:
- [ ] `width: 1600px`
- [ ] `height: 900px`
- [ ] 플레이스홀더 텍스트: "화면 캡처 영역"
- [ ] `grid-column: 1 / 2`, `grid-row: 1 / 2`

**실제 결과**:
```
width: _______
height: _______
```

---

### TC-4: VTuber 아바타 프레임 (320x180)

**목적**: 아바타 프레임 iframe 연동 검증

**URL**: `http://localhost:3001/overlay/`

**단계**:
1. `.vtuber-frame` 요소 선택
2. iframe 로드 확인 (`../vtuber/index.html?transparent=true`)
3. iframe 크기 확인

**예상 결과**:
- [ ] `width: 320px`
- [ ] `height: 180px`
- [ ] iframe `src="../vtuber/index.html?transparent=true"`
- [ ] iframe 내부: 연결 상태 표시 (🔴 또는 🟢)
- [ ] `grid-column: 2 / 3`, `grid-row: 1 / 2`

**iframe 로드 확인**:
- [ ] iframe 내부 콘텐츠 표시됨
- [ ] 깨짐 없음
- [ ] 투명 배경 정상

---

### TC-5: 멀티 프로젝트 활동 카드 (1600x180)

**목적**: 프로젝트 카드 레이아웃 및 스타일 검증

**URL**: `http://localhost:3001/overlay/`

**단계**:
1. `.project-cards` 요소 선택
2. Flexbox 레이아웃 확인
3. 3개 카드 크기 확인 (동일 너비)
4. hover 효과 테스트

**예상 결과**:
- [ ] `display: flex`, `gap: 16px`
- [ ] 3개 카드 (`#project1`, `#project2`, `#project3`)
- [ ] 각 카드 `flex: 1` (동일 너비)
- [ ] 카드 배경: `rgba(0, 0, 0, 0.7)`
- [ ] hover 시 `transform: translateY(-4px)`

**카드 크기 측정**:
```
project1 width: _______
project2 width: _______
project3 width: _______
(모두 동일해야 함)
```

**hover 효과**:
- [ ] 마우스 호버 시 카드가 위로 이동
- [ ] box-shadow 변경

---

### TC-6: 프로젝트 카드 반응 오버레이

**목적**: 반응 애니메이션 (🎉, 🎊) 정상 작동 확인

**URL**: `http://localhost:3001/overlay/`

**단계**:
1. 개발자 도구 → Console 탭
2. 다음 코드 실행하여 반응 트리거:
```javascript
// 프로젝트 카드 1에 반응 표시
const overlay = document.getElementById('reaction1');
overlay.classList.add('active');
setTimeout(() => overlay.classList.remove('active'), 2000);
```

**예상 결과**:
- [ ] 반응 오버레이 표시 (🎉 아이콘)
- [ ] 2초 후 자동 숨김
- [ ] bounce 애니메이션 정상
- [ ] `opacity: 0 → 1 → 0` 전환

---

### TC-7: Active Projects 패널 (320x900)

**목적**: 프로젝트 목록 패널 및 스크롤 검증

**URL**: `http://localhost:3001/overlay/`

**단계**:
1. `.active-projects-panel` 요소 선택
2. 크기 확인
3. 프로젝트 목록 표시 확인
4. 스크롤 테스트 (항목 많을 때)

**예상 결과**:
- [ ] `width: 320px`
- [ ] `height: 180px` (grid-row: 2 / 3)
- [ ] 패널 헤더: "Active Projects"
- [ ] 프로젝트 목록 표시:
  - youtuber_vertuber (활성: 🟢)
  - youtuber_chatbot
  - tft-assist
- [ ] 스크롤바 커스텀 스타일 (항목 많을 때)

**활성 상태 표시**:
- [ ] `.item-status.active` → 녹색 점 (`#4ade80`)
- [ ] pulse 애니메이션 (2초 간격)

---

### TC-8: 투명 배경 모드

**목적**: OBS Browser Source용 투명 배경 정상 작동 확인

**URL**: `http://localhost:3001/overlay/?transparent=true`

**단계**:
1. URL 파라미터 `?transparent=true` 추가
2. 개발자 도구 → Elements 탭
3. `<body>` 요소에 `transparent-mode` 클래스 확인
4. 플레이스홀더 숨김 확인

**예상 결과**:
- [ ] `<body class="transparent-mode">`
- [ ] `.screen-placeholder` 배경 투명, 텍스트 숨김
- [ ] `.screen-placeholder p { display: none; }`
- [ ] 전체 배경 투명 (`background: transparent`)

---

### TC-9: WebSocket 연결

**목적**: WebSocket 연결 및 메시지 수신 확인

**URL**: `http://localhost:3001/overlay/`

**단계**:
1. 개발자 도구 → Console 탭
2. WebSocket 연결 로그 확인:
```
[OBS Overlay] Initializing...
[OBS Overlay] WebSocket connected
```
3. 채널 구독 확인:
```
type: "subscribe", channel: "commit"
type: "subscribe", channel: "pr"
type: "subscribe", channel: "vtuber"
```

**예상 결과**:
- [ ] WebSocket 연결 성공
- [ ] 3개 채널 구독 (commit, pr, vtuber)
- [ ] 연결 끊김 시 5초 후 재연결 시도

**재연결 테스트**:
1. stream-server 종료
2. Console에 "[OBS Overlay] WebSocket closed" 확인
3. "[OBS Overlay] Reconnecting..." (5초 간격) 확인
4. stream-server 재시작
5. "[OBS Overlay] WebSocket connected" 확인

---

### TC-10: 스크린샷 캡처 (OBS 통합)

**목적**: OBS Browser Source 추가 및 스크린샷 캡처

**사전 준비**:
- OBS Studio v28.0+ 설치
- stream-server 실행 중

**단계**:
1. OBS Studio 실행
2. Sources → + → Browser
3. 설정:
   - Name: `VTuber Overlay`
   - URL: `http://localhost:3001/overlay/?transparent=true`
   - Width: `1920`
   - Height: `1080`
   - Custom CSS: (비워둠)
   - Shutdown source when not visible: ✅
   - Refresh browser when scene becomes active: ✅
4. OK 클릭
5. 오버레이 표시 확인
6. 스크린샷 캡처 (OBS → Screenshot → Save)

**예상 결과**:
- [ ] 오버레이 정상 표시
- [ ] 투명 배경 정상 (OBS 배경 투과)
- [ ] 모든 영역 깨짐 없음
- [ ] 스크린샷 저장: `docs/images/overlay-layout-test.png`

**OBS 설정 추가 확인**:
- [ ] Browser Source 성능: 60fps 유지
- [ ] CPU 사용률: 정상 범위
- [ ] 메모리 사용: < 100MB

---

## 검증 체크리스트

### 레이아웃 정확도
- [ ] 전체 크기: 1920x1080
- [ ] CSS Grid: 2x2 (1600px+320px / 900px+180px)
- [ ] 메인 화면: 1600x900
- [ ] 아바타 프레임: 320x180
- [ ] 프로젝트 카드: 1600x180
- [ ] Active Projects 패널: 320x900

### 기능 동작
- [ ] iframe 로드 정상 (VTuber 프레임)
- [ ] Flexbox 레이아웃 (프로젝트 카드)
- [ ] hover 효과 (카드 상승, 그림자)
- [ ] 반응 오버레이 (bounce 애니메이션)
- [ ] 스크롤바 (Active Projects 패널)
- [ ] 투명 배경 모드 (?transparent=true)

### WebSocket 통합
- [ ] 연결 성공
- [ ] 채널 구독 (commit, pr, vtuber)
- [ ] 자동 재연결 (5초 간격)

### OBS 통합
- [ ] Browser Source 추가 성공
- [ ] 투명 배경 정상
- [ ] 60fps 성능 유지
- [ ] 스크린샷 캡처 완료

---

## 테스트 결과 요약

**테스트 일시**: ___________________
**테스터**: ___________________
**환경**:
- OS: Windows 11
- 브라우저: Chrome/Edge
- OBS Studio: v___________

**전체 통과율**: ____/40 (____%)

**발견된 이슈**:
1.
2.
3.

**권장 사항**:
1.
2.
3.

---

## 부록: 빠른 테스트 스크립트

### Console에서 실행 가능한 검증 스크립트

```javascript
// 1. 레이아웃 크기 검증
console.log('=== Layout Size Verification ===');
console.log('Body:', document.body.offsetWidth, 'x', document.body.offsetHeight);
console.log('Main Screen:', document.querySelector('.main-screen').offsetWidth, 'x', document.querySelector('.main-screen').offsetHeight);
console.log('VTuber Frame:', document.querySelector('.vtuber-frame').offsetWidth, 'x', document.querySelector('.vtuber-frame').offsetHeight);
console.log('Project Cards:', document.querySelector('.project-cards').offsetWidth, 'x', document.querySelector('.project-cards').offsetHeight);
console.log('Active Projects:', document.querySelector('.active-projects-panel').offsetWidth, 'x', document.querySelector('.active-projects-panel').offsetHeight);

// 2. 프로젝트 카드 동일 너비 검증
console.log('=== Project Card Widths ===');
const cards = [1, 2, 3].map(i => document.getElementById(`project${i}`));
cards.forEach((card, i) => {
  console.log(`Project Card ${i + 1}:`, card.offsetWidth, 'px');
});

// 3. Grid 레이아웃 검증
console.log('=== CSS Grid Verification ===');
const overlay = document.querySelector('.obs-overlay');
const gridStyle = window.getComputedStyle(overlay);
console.log('Display:', gridStyle.display);
console.log('Grid Template Columns:', gridStyle.gridTemplateColumns);
console.log('Grid Template Rows:', gridStyle.gridTemplateRows);

// 4. 투명 모드 확인
console.log('=== Transparent Mode ===');
console.log('Body class:', document.body.className);
console.log('Transparent mode enabled:', document.body.classList.contains('transparent-mode'));
```

**결과 저장**:
Console → 우클릭 → Save as... → `layout-verification-result.txt`

---

## 참고 자료

- PRD: [tasks/prds/0001-prd-vseface-integration.md](../tasks/prds/0001-prd-vseface-integration.md)
- Checklist: [docs/checklists/PRD-0001.md](checklists/PRD-0001.md:104-108)
- OBS 설정 가이드: [docs/OBS_SETUP.md](OBS_SETUP.md)
- 이슈 #85: https://github.com/garimto81/claude/issues/85
