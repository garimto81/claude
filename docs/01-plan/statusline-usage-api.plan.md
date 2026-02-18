# Plan: Statusline Direct Usage API Polling

## 배경
현재 `hybrid-statusline.mjs`는 OMC HUD subprocess를 통해 간접적으로 Anthropic Usage API를 호출한다.
OMC HUD 빌드/설치 의존성, 5초 timeout, subprocess 오버헤드 등으로 신뢰성이 낮다.
`login_claudecode`의 `LimitDetector`는 regex 텍스트 매칭만 사용하여 정확도가 부족하다.

## 목표
`hybrid-statusline.mjs`에 `api.anthropic.com/api/oauth/usage` 직접 폴링을 내장하여
OMC HUD 없이도 정확한 5h/wk 사용률을 표시한다.

## 구현 범위

### 수정 파일: `~/.claude/hud/hybrid-statusline.mjs` (단일 파일)

#### 1. `readCredentials()` 추가
- `~/.claude/.credentials.json` 읽기
- `claudeAiOauth.accessToken` 추출
- `expiresAt` 만료 검증

#### 2. `fetchUsage()` 추가
- HTTPS GET `api.anthropic.com/api/oauth/usage`
- Header: `Authorization: Bearer {token}`, `anthropic-beta: oauth-2025-04-20`
- 파일 캐시: `~/.claude/.usage-cache.json` (30초 TTL 성공, 15초 TTL 실패)
- 10초 timeout

#### 3. `renderUsage()` 추가
- `five_hour.utilization` → `5h:XX%`
- `seven_day.utilization` → `wk:XX%`
- 색상: green(0-69%), yellow(70-89%), red(90-100%)
- reset 시간 표시 (옵션)

#### 4. `main()` 수정
- OMC HUD 호출 **전에** usage를 직접 fetch
- 직접 fetch 성공 → 자체 렌더링 사용 (OMC HUD 출력에서 rate limit 중복 제거)
- 직접 fetch 실패 → OMC HUD fallback 유지
- 출력 형식: `[OMC] 5h:XX% wk:YY% | ctx:ZZ% | $X.XX | 📁 folder 🌿 branch`

## 참조 구현
- `plugins/cache/omc/.../src/hud/usage-api.ts` — API 호출, 캐시, credential 읽기
- `plugins/cache/omc/.../src/hud/elements/limits.ts` — 렌더링 형식
- `login_claudecode/src/limit_detector.py` — 대체 대상 (regex 방식)

## 위험 요소
- Windows에서 `.credentials.json` 파일 권한 문제 (낮음 - 이미 OMC에서 작동)
- API 응답 형식 변경 (낮음 - `anthropic-beta` 헤더로 버전 고정)
- 캐시 파일 동시 접근 (낮음 - statusline은 순차 실행)
