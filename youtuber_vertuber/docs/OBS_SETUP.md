# OBS Studio 설정 가이드 - VTuber 아바타 오버레이

**PRD**: PRD-0001 (VSeeFace 버튜버 기능 통합)
**Phase**: Phase 2 (OBS 오버레이)
**Version**: 1.0.0
**Last Updated**: 2026-01-05

---

## 목차

1. [시스템 요구사항](#1-시스템-요구사항)
2. [OBS Browser Source 설정](#2-obs-browser-source-설정)
3. [VSeeFace Window Capture 설정](#3-vseface-window-capture-설정)
4. [레이아웃 구성](#4-레이아웃-구성)
5. [문제 해결](#5-문제-해결)

---

## 1. 시스템 요구사항

### 소프트웨어

| 항목 | 버전 | 다운로드 |
|------|------|----------|
| **OBS Studio** | v28.0 이상 | https://obsproject.com/ |
| **VSeeFace** | v1.13.38 이상 | https://www.vseeface.icu/ |
| **stream-server** | 실행 중 | http://localhost:3001 |

### 확인사항

- [ ] OBS Studio 설치 완료
- [ ] VSeeFace 실행 중 (VMC Protocol 활성화)
- [ ] stream-server 실행 중 (포트 3001)
- [ ] VTuber 오버레이 파일 존재 (`packages/stream-server/public/vtuber/`)

---

## 2. OBS Browser Source 설정

### 2.1 Browser Source 추가

1. **OBS Studio 실행**

2. **Sources 패널** → **+** 버튼 클릭

3. **Browser** 선택

4. **Create New** 선택
   - Name: `VTuber 아바타 오버레이`
   - **OK** 클릭

5. **Properties 설정**:
   ```
   ☐ Local file (체크 해제)

   URL: http://localhost:3001/vtuber/index.html

   Width: 320
   Height: 180

   ☑ Shutdown source when not visible
   ☐ Refresh browser when scene becomes active

   Custom CSS: (비워둠)
   ```

6. **OK** 클릭

### 2.2 위치 및 크기 조정

#### 방법 A: 마우스 드래그
1. OBS Preview 화면에서 `VTuber 아바타 오버레이` 소스 선택
2. 우측 상단으로 드래그
3. 모서리를 드래그하여 크기 조정 (320 × 180)

#### 방법 B: Transform 수동 설정
1. 소스 우클릭 → **Transform** → **Edit Transform...**
2. **Position** 설정:
   ```
   X: 1600
   Y: 0
   ```
3. **Size** 설정:
   ```
   Width: 320
   Height: 180
   ```
4. **OK** 클릭

### 2.3 투명 모드 (선택사항)

아바타만 표시하고 배경을 완전히 투명하게 하려면:

**URL 수정**:
```
http://localhost:3001/vtuber/index.html?transparent=true
```

---

## 3. VSeeFace Window Capture 설정

### 3.1 VSeeFace 투명 배경 활성화

1. **VSeeFace 실행**

2. **Settings** → **General** 탭

3. **Transparent Background** ✅ 체크

4. **Apply** 클릭

### 3.2 OBS Window Capture 추가

1. **OBS Sources** → **+** → **Window Capture**

2. **Create New**
   - Name: `VSeeFace 아바타 (Direct)`
   - **OK** 클릭

3. **Properties 설정**:
   ```
   Window: [VSeeFace.exe]: VSeeFace

   Capture Method: Windows 10 (1903 and newer)

   ☐ Capture Cursor (체크 해제)
   ☑ Capture Third-party overlays (체크)
   ```

4. **OK** 클릭

### 3.3 크기 및 위치 조정

1. 소스 우클릭 → **Transform** → **Edit Transform...**

2. **Position**:
   ```
   X: 1600
   Y: 0
   ```

3. **Bounding Box Size**:
   ```
   Width: 320
   Height: 180
   ```

4. **Bounding Box Type**: `Scale to inner bounds`

5. **OK** 클릭

### 3.4 Chroma Key 적용 (배경 제거)

VSeeFace 배경이 투명하지 않은 경우:

1. `VSeeFace 아바타 (Direct)` 소스 우클릭

2. **Filters** 클릭

3. **Effect Filters** → **+** → **Chroma Key**

4. **Chroma Key 설정**:
   ```
   Key Color Type: Green

   Similarity: 400
   Smoothness: 80

   Spill Reduction: 100
   ```

5. **Close** 클릭

---

## 4. 레이아웃 구성

### 4.1 권장 Scene 구성

```
OBS Scene: "방송 메인"
├─ [Layer 1] VSCode (Source: Window Capture)
│  └─ Window: [Code.exe]: Visual Studio Code
│     Position: (0, 0)
│     Size: 1920 × 1080 (Full Screen)
│
├─ [Layer 2] youtuber 오버레이 (Source: Browser)
│  └─ URL: (youtuber 프로젝트에서 제공)
│     Position: (커스텀)
│     Size: (커스텀)
│
└─ [Layer 3] VTuber 아바타 (Source: Browser or Window Capture)
   └─ URL: http://localhost:3001/vtuber/index.html
      Position: (1600, 0)
      Size: 320 × 180
```

### 4.2 레이어 순서 조정

**중요**: VTuber 아바타가 최상단에 표시되어야 합니다.

**순서 변경**:
1. Sources 패널에서 `VTuber 아바타 오버레이` 선택
2. 드래그하여 리스트 **최상단**으로 이동

**최종 순서** (위에서 아래):
```
1. VTuber 아바타 오버레이  ← 최상단 (가장 앞)
2. youtuber 오버레이
3. VSCode                   ← 최하단 (배경)
```

### 4.3 1920x1080 레이아웃 확인

**OBS Canvas 설정**:
```
Settings → Video
├─ Base (Canvas) Resolution: 1920x1080
└─ Output (Scaled) Resolution: 1920x1080
```

**Preview 확인**:
- VSCode: 전체 화면 (또는 1600x900 영역)
- youtuber 오버레이: 하단 또는 커스텀 위치
- VTuber 아바타: 우측 상단 (320x180)

---

## 5. 문제 해결

### 5.1 Browser Source가 표시 안됨

**증상**: OBS에 아무것도 보이지 않음

**원인**:
1. stream-server가 실행 중이 아님
2. URL이 잘못됨
3. OBS Browser Source 플러그인 문제

**해결**:
```bash
# 1. stream-server 확인
# 브라우저에서 확인:
http://localhost:3001/vtuber/index.html

# 2. OBS 로그 확인
Help → Log Files → View Current Log
# "Failed to connect" 메시지 검색

# 3. OBS Browser Source 재설치
Help → Check for Updates
```

### 5.2 WebSocket 연결 실패

**증상**: 연결 상태가 🔴 "연결 대기중..." 상태

**원인**: stream-server가 WebSocket 서버를 제공하지 않음

**해결** (임시):
```html
<!-- 개발 모드: app.js 수정 -->
// WebSocket 연결 비활성화
// connectWebSocket(); 주석 처리

// 연결 상태 수동 설정
updateConnectionStatus(true, '로컬 모드 (WebSocket 없음)');
```

**정식 해결** (Phase 2 후속 작업):
- stream-server에 WebSocket 서버 추가 (`ws` 라이브러리)
- Express + WebSocket 통합

### 5.3 VSeeFace 투명 배경 안됨

**증상**: Window Capture에서 배경이 보임

**해결**:
1. VSeeFace → Settings → General → **Transparent Background** ✅

2. VSeeFace 재시작

3. OBS Chroma Key 필터 추가 (위 3.4 참조)

4. 그래도 안되면:
   ```
   VSeeFace → Settings → General
   └─ Background Color: Green
   ```
   → OBS Chroma Key로 Green 제거

### 5.4 아바타 위치가 틀어짐

**증상**: 아바타가 예상 위치에 없음 (1920x1080 기준)

**원인**: OBS Canvas 해상도가 다름

**해결**:
```
Settings → Video
├─ Base (Canvas) Resolution: 1920x1080 ← 확인
└─ Output (Scaled) Resolution: 1920x1080
```

**다른 해상도 사용 시**:
- 1280x720: Position (853, 0), Size (213, 120)
- 2560x1440: Position (2133, 0), Size (427, 240)

### 5.5 성능 저하 (프레임 드롭)

**증상**: OBS가 60fps를 유지하지 못함

**원인**:
1. Browser Source가 CPU를 많이 사용
2. VSeeFace + OBS 동시 실행

**해결**:
1. **Hardware Acceleration 활성화**:
   ```
   OBS Settings → Advanced
   └─ Renderer: Direct3D 11
   ```

2. **Browser Source FPS 제한**:
   ```
   소스 우클릭 → Properties
   └─ FPS: 30 (기본 60에서 낮춤)
   ```

3. **VSeeFace 품질 낮춤**:
   ```
   VSeeFace → Settings → Quality
   ├─ Render Quality: Medium
   └─ Shadow Quality: Off
   ```

### 5.6 아바타가 잘림 (Crop 문제)

**증상**: 아바타 머리나 몸이 잘려서 보임

**해결**:
1. VSeeFace 화면에서 마우스 휠로 **Zoom Out**

2. 드래그로 아바타 위치 조정 (중앙)

3. OBS Transform 재조정:
   ```
   Bounding Box Type: Scale to inner bounds
   ```

---

## 6. 고급 설정

### 6.1 자동 시작 설정

**OBS Scene Collection 저장**:
```
Scene Collection → Save → "VTuber 방송"
```

**자동 로드**:
```
Settings → General
└─ Scene Collection: VTuber 방송
```

### 6.2 Hotkey 설정

**아바타 표시/숨김**:
```
Settings → Hotkeys
└─ VTuber 아바타 오버레이: Show/Hide
   Hotkey: Ctrl + Shift + V
```

### 6.3 Scene Transition

**아바타 페이드 인**:
```
Scene Transition: Fade
Duration: 300ms
```

---

## 7. 체크리스트

### 방송 시작 전 확인

- [ ] VSeeFace 실행 중 (VMC Protocol 활성화)
- [ ] stream-server 실행 중 (`http://localhost:3001`)
- [ ] OBS Browser Source 표시됨
- [ ] 연결 상태: 🟢 "연결됨" (WebSocket 활성화 시)
- [ ] 아바타 위치: 우측 상단 (1600, 0)
- [ ] 아바타 크기: 320 × 180
- [ ] 레이어 순서: VTuber 아바타 최상단
- [ ] 60fps 유지 (OBS Stats 확인)

---

## 참고 자료

- **VTuber 오버레이 README**: `packages/stream-server/public/vtuber/README.md`
- **VSeeFace 설치 가이드**: `docs/VSEFACE_SETUP.md`
- **PRD 문서**: `tasks/prds/0001-prd-vseface-integration.md`
- **OBS 공식 문서**: https://obsproject.com/wiki/

---

**Last Updated**: 2026-01-05
**Version**: 1.0.0
**Author**: Claude (AI Assistant)
