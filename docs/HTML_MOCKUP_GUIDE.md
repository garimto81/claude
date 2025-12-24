# HTML 목업 설계 가이드

**Version**: 1.0.0 | **Updated**: 2025-12-24

PRD 및 설계 문서에 삽입할 UI 목업을 HTML로 설계하고 캡처하는 가이드입니다.

---

## 왜 HTML 목업인가?

| 방식 | 장점 | 단점 |
|------|------|------|
| Figma | 전문 디자인 도구 | API로 생성 불가 |
| 스크린샷 | 실제 화면 | 개발 전 불가 |
| **HTML 목업** | 코드로 직접 생성, 즉시 캡처 | ✅ 권장 |

---

## 디자인 규격

| 항목 | 값 | 이유 |
|------|-----|------|
| **가로 너비** | 540px | 문서 삽입 최적화 |
| **최소 폰트** | 16px | 가독성 표준 |
| **라인 높이** | 1.5 | 읽기 편안함 |
| **여백** | 16~24px | 시각적 여유 |
| **버튼 크기** | 44x44px 이상 | 터치 타겟 표준 |
| **캡처 대상** | `#capture-target` | 요소별 캡처용 ID |

---

## HTML 템플릿

### 기본 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=540">
  <title>Mockup - [Feature Name]</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      width: 540px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 16px;
      line-height: 1.5;
      background: #f5f5f5;
    }

    #capture-target {
      background: #ffffff;
      padding: 24px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* 컴포넌트 스타일 */
    .title {
      font-size: 24px;
      font-weight: 600;
      margin-bottom: 16px;
    }

    .button {
      display: inline-block;
      padding: 12px 24px;
      font-size: 16px;
      font-weight: 500;
      color: #fff;
      background: #007AFF;
      border: none;
      border-radius: 8px;
      cursor: pointer;
    }

    .input {
      width: 100%;
      padding: 12px 16px;
      font-size: 16px;
      border: 1px solid #ddd;
      border-radius: 8px;
      margin-bottom: 12px;
    }

    .card {
      padding: 16px;
      background: #f9f9f9;
      border-radius: 8px;
      margin-bottom: 12px;
    }
  </style>
</head>
<body>
  <!-- 이 영역만 캡처됨 -->
  <div id="capture-target">
    <h1 class="title">제목</h1>
    <p>설명 텍스트</p>
    <button class="button">버튼</button>
  </div>
</body>
</html>
```

### 폼 예시

```html
<div id="capture-target">
  <h2 class="title">로그인</h2>
  <input type="email" class="input" placeholder="이메일">
  <input type="password" class="input" placeholder="비밀번호">
  <button class="button" style="width: 100%;">로그인</button>
</div>
```

### 카드 리스트 예시

```html
<div id="capture-target">
  <h2 class="title">최근 항목</h2>
  <div class="card">
    <strong>항목 1</strong>
    <p style="color: #666; font-size: 14px;">설명 텍스트</p>
  </div>
  <div class="card">
    <strong>항목 2</strong>
    <p style="color: #666; font-size: 14px;">설명 텍스트</p>
  </div>
</div>
```

---

## 캡처 명령어

### 요소만 캡처 (권장)

```powershell
npx playwright screenshot docs/mockups/login.html docs/images/login.png --selector="#capture-target"
```

### 전체 페이지 캡처 (비권장)

```powershell
npx playwright screenshot docs/mockups/login.html docs/images/login-full.png
```

### 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `--selector` | CSS 선택자로 요소 지정 | `--selector="#capture-target"` |
| `--full-page` | 전체 페이지 캡처 | `--full-page` |
| `--device` | 디바이스 에뮬레이션 | `--device="iPhone 12"` |

---

## 워크플로우

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. 설계    │────▶│  2. HTML    │────▶│  3. 캡처    │────▶│  4. 삽입    │
│  (구상)     │     │  목업 작성   │     │  (요소만)   │     │  (PRD)      │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### 단계별 상세

1. **설계**: UI 구상 (와이어프레임 수준)
2. **HTML 작성**: `docs/mockups/[feature].html` 생성
3. **캡처**: Playwright로 `#capture-target` 요소만 캡처
4. **삽입**: PRD/설계 문서에 이미지 첨부

---

## 폴더 구조

```
docs/
├── mockups/           # HTML 목업 원본
│   ├── login.html
│   ├── dashboard.html
│   └── settings.html
└── images/            # 캡처된 이미지
    ├── login.png
    ├── dashboard.png
    └── settings.png
```

---

## 주의사항

| 항목 | 주의점 |
|------|--------|
| **폰트 크기** | 16px 미만 사용 금지 (가독성) |
| **가로 너비** | 540px 초과 금지 (문서 삽입) |
| **캡처 대상** | `#capture-target` ID 필수 |
| **배경색** | 흰색 권장 (문서 일관성) |
| **요소 가시성** | 숨겨진 요소 캡처 불가 |

---

## 색상 팔레트 (권장)

| 용도 | 색상 | HEX |
|------|------|-----|
| Primary | 파랑 | `#007AFF` |
| Success | 초록 | `#34C759` |
| Warning | 노랑 | `#FF9500` |
| Error | 빨강 | `#FF3B30` |
| Text | 검정 | `#1C1C1E` |
| Secondary | 회색 | `#8E8E93` |
| Background | 흰색 | `#FFFFFF` |
| Surface | 연회색 | `#F2F2F7` |

---

## 예시: 로그인 폼 전체

### HTML 파일: `docs/mockups/login.html`

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=540">
  <title>Mockup - Login</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      width: 540px;
      font-family: -apple-system, sans-serif;
      font-size: 16px;
      line-height: 1.5;
      background: #f5f5f5;
      padding: 20px;
    }
    #capture-target {
      background: #fff;
      padding: 32px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .logo { text-align: center; margin-bottom: 24px; }
    .logo img { width: 64px; height: 64px; }
    .title { font-size: 24px; font-weight: 600; text-align: center; margin-bottom: 8px; }
    .subtitle { font-size: 16px; color: #8E8E93; text-align: center; margin-bottom: 24px; }
    .input {
      width: 100%;
      padding: 14px 16px;
      font-size: 16px;
      border: 1px solid #ddd;
      border-radius: 8px;
      margin-bottom: 12px;
    }
    .input:focus { border-color: #007AFF; outline: none; }
    .button {
      width: 100%;
      padding: 14px;
      font-size: 16px;
      font-weight: 600;
      color: #fff;
      background: #007AFF;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      margin-top: 8px;
    }
    .link { text-align: center; margin-top: 16px; }
    .link a { color: #007AFF; text-decoration: none; font-size: 14px; }
  </style>
</head>
<body>
  <div id="capture-target">
    <div class="logo">
      <div style="width:64px;height:64px;background:#007AFF;border-radius:16px;margin:0 auto;"></div>
    </div>
    <h1 class="title">로그인</h1>
    <p class="subtitle">계정에 로그인하세요</p>
    <input type="email" class="input" placeholder="이메일 주소">
    <input type="password" class="input" placeholder="비밀번호">
    <button class="button">로그인</button>
    <div class="link">
      <a href="#">비밀번호를 잊으셨나요?</a>
    </div>
  </div>
</body>
</html>
```

### 캡처 명령어

```powershell
npx playwright screenshot docs/mockups/login.html docs/images/login.png --selector="#capture-target"
```

---

## 관련 문서

| 문서 | 설명 |
|------|------|
| `CLAUDE.md` | 전역 지침 (최소 규칙) |
| `docs/COMMAND_REFERENCE.md` | 커맨드 참조 |
| [Playwright Screenshots](https://playwright.dev/docs/screenshots) | 공식 문서 |

---

## 버전 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| 1.0.0 | 2025-12-24 | 초기 작성 |
