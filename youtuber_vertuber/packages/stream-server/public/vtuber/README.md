# VTuber 아바타 오버레이 (320x180)

**Phase**: Phase 2 (OBS 오버레이)
**Size**: 320px × 180px
**Purpose**: VSeeFace 아바타를 OBS에 표시하고 연결 상태를 시각화

---

## 파일 구조

```
public/vtuber/
├── index.html       # 320x180 아바타 프레임
├── styles.css       # 투명 배경, 연결 상태 스타일
├── app.js           # WebSocket vtuber:status 처리
└── README.md        # 이 파일
```

---

## OBS 설정 방법

### 방법 1: Browser Source (연결 상태 표시 포함)

1. OBS → **Sources** → **+** → **Browser Source**
2. 이름: "VTuber 아바타 오버레이"
3. 설정:
   - ✅ **Local File**: 체크 해제
   - **URL**: `http://localhost:3001/vtuber/index.html`
   - **Width**: `320`
   - **Height**: `180`
4. **OK** 클릭
5. 소스를 우측 상단으로 드래그 (X=1600, Y=0)

### 방법 2: Window Capture (VSeeFace 직접)

1. OBS → **Sources** → **+** → **Window Capture**
2. 이름: "VSeeFace 아바타"
3. 설정:
   - **Window**: `[VSeeFace.exe]: VSeeFace`
   - **Capture Method**: Windows 10 (1903 and newer)
4. **OK** 클릭
5. 크기 조정: 320 × 180
6. 위치: 우측 상단 (X=1600, Y=0)
7. **Filters** 추가:
   - **Chroma Key**: Green (배경 제거)

---

## URL 파라미터

### 투명 모드

```
http://localhost:3001/vtuber/index.html?transparent=true
```

- 플레이스홀더 텍스트 숨김
- 완전 투명 배경
- OBS에서 VSeeFace Window Capture와 함께 사용

---

## WebSocket 메시지

### 구독

```javascript
{
  "type": "subscribe",
  "channel": "vtuber"
}
```

### 수신 메시지

#### 1. vtuber:status (연결 상태)

```javascript
{
  "type": "vtuber:status",
  "payload": {
    "connected": true,
    "vmcHost": "localhost",
    "vmcPort": 39539,
    "lastUpdate": "2026-01-05T..."
  },
  "timestamp": "2026-01-05T..."
}
```

**UI 반응**:
- `connected: true` → 🟢 연결됨
- `connected: false` → 🔴 연결 끊김

#### 2. vtuber:expression (표정 변경)

```javascript
{
  "type": "vtuber:expression",
  "payload": {
    "expression": "happy",
    "duration": 2000,
    "trigger": "commit",
    "metadata": {
      "repo": "youtuber_vertuber",
      "message": "feat: add vtuber overlay"
    }
  },
  "timestamp": "2026-01-05T..."
}
```

**표정 아이콘**:
- `happy` → 😊
- `surprised` → 😮
- `neutral` → 😐
- `focused` → 🤔
- `sorrow` → 😢

**UI 반응**:
- 우측 상단에 표정 아이콘 표시
- `duration` (기본 2초) 후 자동 숨김

---

## 개발 모드

### 로컬 테스트

```bash
# 간단한 HTTP 서버 실행 (Python)
cd packages/stream-server/public
python -m http.server 8000

# 브라우저에서 확인
http://localhost:8000/vtuber/index.html
```

### WebSocket 연결 확인

```javascript
// 브라우저 콘솔
ws = new WebSocket('ws://localhost:3001');
ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'subscribe', channel: 'vtuber' }));
};

// 테스트 메시지 전송
ws.send(JSON.stringify({
  type: 'vtuber:status',
  payload: { connected: true, vmcHost: 'localhost', vmcPort: 39539 }
}));
```

---

## 커스터마이징

### 크기 변경

```css
/* styles.css */
body {
  width: 400px;   /* 기본 320px */
  height: 225px;  /* 기본 180px */
}
```

### 연결 상태 위치

```css
/* styles.css */
.connection-status {
  bottom: 10px;   /* 하단 */
  left: 10px;     /* 좌측 */
  /* 또는 */
  top: 10px;      /* 상단 */
  right: 10px;    /* 우측 */
}
```

### 표정 인디케이터 제거

```javascript
// app.js
function handleVTuberExpression(payload) {
  // 주석 처리
  // expressionIndicator.classList.add('active');
  console.log('Expression:', payload.expression);
}
```

---

## 문제 해결

### 1. 아무것도 표시 안됨

**확인**:
- stream-server가 실행 중인가? (`http://localhost:3001`)
- OBS Browser Source URL이 정확한가?
- 브라우저 콘솔에 오류가 있는가? (F12)

### 2. WebSocket 연결 실패

**확인**:
- stream-server가 WebSocket을 지원하는가?
- 포트 3001이 열려있는가? (`netstat -an | findstr :3001`)
- 브라우저 콘솔: `[VTuber Overlay] WebSocket error`

**해결**:
- stream-server에 WebSocket 서버 추가 필요 (Phase 2 후속 작업)

### 3. 투명 배경 안됨

**확인**:
- URL 파라미터 `?transparent=true` 추가했는가?
- OBS → 소스 → 우클릭 → **Properties** → **Shutdown source when not visible** 체크 해제

---

## 다음 단계

### Phase 3: GitHub 연동
- `vtuber:expression` 메시지 자동 전송
- Commit → happy, PR Merged → surprised
- 반응 아이콘 오버레이 추가

### Phase 4: 채팅 연동
- youtuber_chatbot 감정 분석 연동
- 채팅 메시지 → 표정 변경

---

**Last Updated**: 2026-01-05
**Version**: 1.0.0
**Author**: Claude (AI Assistant)
