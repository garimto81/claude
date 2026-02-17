# Hook 시스템 개선 설계 문서

**Version**: 1.0.0
**Date**: 2026-02-06
**Status**: IMPLEMENTED

---

## 목차

1. [설계 개요](#설계-개요)
2. [PostToolUse Hook 아키텍처](#posttooluse-hook-아키텍처)
3. [Playwright CLI 워크플로우](#playwright-cli-워크플로우)
4. [Multi-Agent Task Decomposition 패턴](#multi-agent-task-decomposition-패턴)
5. [Hook Event Coverage 현황](#hook-event-coverage-현황)
6. [기술적 결정사항](#기술적-결정사항)
7. [검증 전략](#검증-전략)

---

## 설계 개요

### 목적

Claude Code Hook 시스템의 확장성과 자동화 수준을 향상시키기 위한 4가지 핵심 개선사항 구현.

### 범위

| 개선 영역 | 구현 범위 |
|----------|----------|
| **PostToolUse Hook** | Edit/Write 도구 실행 후 자동 검증 |
| **Playwright CLI** | 브라우저 자동화 CLI 워크플로우 |
| **Task Decomposition** | 표준화된 병렬 작업 분해 패턴 |
| **Event Coverage** | Hook 지원 이벤트 확대 |

### 제약사항

| 제약 | 내용 |
|------|------|
| **플랫폼** | Windows PowerShell 환경 |
| **타임아웃** | 120초 초과 방지 (개별 명령 30초 제한) |
| **비차단** | PostToolUse는 절대 차단하지 않음 |
| **권한** | MCP 서버는 명시적 허용 필요 |

---

## PostToolUse Hook 아키텍처

### 1. 파일 구조

```
C:\claude\.claude\hooks\
├── post_edit_check.js           # PostToolUse 메인 로직
├── session_init.py              # SessionStart 기존
├── branch_guard.py              # PreToolUse 기존
└── tool_validator.py            # PreToolUse 기존
```

### 2. 핵심 설계 결정

#### 2.1 Node.js 선택 이유

| 이유 | 설명 |
|------|------|
| **Windows 호환성** | PowerShell/bash 차이 없이 동작 |
| **JSON 파싱** | 네이티브 지원 (stdin 읽기) |
| **child_process** | 동기/비동기 subprocess 실행 용이 |
| **타임아웃 제어** | `{timeout: 30000}` 옵션 지원 |

#### 2.2 비차단 원칙

```javascript
// 항상 approve 반환 (차단 절대 금지)
return {
  decision: "approve",
  message: "✅ ruff clean | 🧪 pytest passed"
};
```

**이유**: PostToolUse는 도구 실행 **후** 발생. 차단해도 이미 파일 수정 완료.

#### 2.3 Python 파일 자동 워크플로우

```
Edit src/auth/login.py
    │
    ▼
post_edit_check.js 실행
    │
    ├─ ruff check --fix src/auth/login.py (30초 타임아웃)
    │  ├─ Success → "✅ ruff clean"
    │  └─ Error   → "⚠️ ruff found issues"
    │
    └─ 테스트 파일 탐색
       ├─ tests/test_login.py 발견 → pytest 실행 (30초)
       │  ├─ PASSED → "✅ 1 passed"
       │  └─ FAILED → "❌ 1 failed (not blocking)"
       └─ 미발견 → 스킵
```

#### 2.4 테스트 파일 탐색 로직

| 원본 파일 | 탐색 경로 (우선순위) |
|-----------|---------------------|
| `src/foo/bar.py` | 1. `tests/test_bar.py` |
|                  | 2. `tests/foo/test_bar.py` |
|                  | 3. `tests/unit/test_bar.py` |
| `lib/auth.py` | 1. `tests/test_auth.py` |
|               | 2. `lib/tests/test_auth.py` |

**구현**:
```javascript
function findTestFile(filePath) {
  const basename = path.basename(filePath, '.py');
  const candidates = [
    `tests/test_${basename}.py`,
    `tests/${path.dirname(filePath)}/test_${basename}.py`,
    `tests/unit/test_${basename}.py`,
    `${path.dirname(filePath)}/tests/test_${basename}.py`
  ];
  return candidates.find(fs.existsSync);
}
```

#### 2.5 TypeScript 파일 처리

```javascript
if (filePath.endsWith('.ts') || filePath.endsWith('.tsx')) {
  return {
    decision: "approve",
    message: "💡 Reminder: tsc로 타입 검사 권장"
  };
}
```

**이유**: TypeScript는 프로젝트 전체 컴파일 필요 → 개별 파일 체크 불가능.

### 3. settings.json Hook 등록

```json
{
  "PostToolUse": [{
    "matcher": "Edit|Write",
    "hooks": [{
      "type": "command",
      "command": "node .claude/hooks/post_edit_check.js"
    }]
  }]
}
```

**matcher 패턴**: 정규표현식 → `Edit` 또는 `Write` 도구 모두 트리거.

### 4. 스킵 패턴

```javascript
const skipPatterns = [
  /node_modules/,
  /\.git/,
  /__pycache__/,
  /\.pyc$/,
  /\.omc/,
  /dist\//,
  /build\//,
  /\.min\./,
  /package-lock\.json/,
  /yarn\.lock/
];
```

**이유**: 빌드 산출물, 의존성 파일은 검증 불필요.

### 5. 타임아웃 전략

| 명령 | 제한 | 이유 |
|------|------|------|
| `ruff check` | 30초 | 단일 파일 → 충분 |
| `pytest` | 30초 | 개별 테스트 → 빠름 |
| **전체 Hook** | 60초 | 두 명령 합산 + 여유 |

**120초 크래시 방지**: 개별 명령 30초 → 최악 60초 (안전 마진).

---

## Playwright CLI 워크플로우

### 1. 설치 및 설정

```powershell
# Playwright 설치 (이미 설치된 경우 생략)
npm install -D @playwright/test

# Playwright 브라우저 설치
npx playwright install
```

**설정 위치**: `package.json` (devDependencies)

### 2. 주요 CLI 명령

| 명령 | 용도 | 예시 |
|------|------|------|
| `npx playwright screenshot` | 스크린샷 생성 | URL을 이미지로 저장 |
| `npx playwright test` | E2E 테스트 실행 | 헤드리스 모드 테스트 |
| `npx playwright test --headed` | 브라우저 표시 | 디버깅용 |
| `npx playwright codegen` | 테스트 코드 생성 | 레코딩 기반 자동 생성 |

### 3. PRD 목업 워크플로우 통합

```
┌─────────────────┐
│ HTML 목업 생성   │
│ (docs/mockups/) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Playwright CLI  │
│ screenshot      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 이미지 저장     │
│ (docs/images/)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 문서 임베드     │
│ ![](images/..)  │
└─────────────────┘
```

### 4. 스크린샷 생성 예시

```powershell
# 기본 스크린샷
npx playwright screenshot file:///C:/claude/docs/mockups/feature.html docs/images/feature.png

# 뷰포트 크기 지정
npx playwright screenshot --viewport-size=1920,1080 file:///C:/claude/docs/mockups/feature.html docs/images/feature-desktop.png

# 모바일 뷰
npx playwright screenshot --viewport-size=375,667 file:///C:/claude/docs/mockups/feature.html docs/images/feature-mobile.png

# 전체 페이지 스크린샷
npx playwright screenshot --full-page file:///C:/claude/docs/mockups/feature.html docs/images/feature-full.png
```

---

## Multi-Agent Task Decomposition 패턴

### 1. 표준 패턴

```typescript
// 독립적 작업
const task1 = await TaskCreate({
  subagent_type: "writer",
  model: "haiku",
  prompt: "Create HTML mockup"
});

// 의존적 작업
const task2 = await TaskCreate({
  subagent_type: "vision",
  model: "sonnet",
  prompt: "Take screenshot of mockup"
});
await addBlockedBy(task2.id, task1.id);

// 통합 작업
const task3 = await TaskCreate({
  subagent_type: "writer",
  model: "haiku",
  prompt: "Embed image in PRD"
});
await addBlockedBy(task3.id, task2.id);
```

### 2. 실행 순서 보장

```
Task 1 (독립)       Task 2 (의존)       Task 3 (의존)
    │                   │                   │
    ▼                   │                   │
  Complete              │                   │
    │                   │                   │
    └──────────────────▶│                   │
                        ▼                   │
                      Complete              │
                        │                   │
                        └──────────────────▶│
                                            ▼
                                          Complete
```

### 3. 병렬 실행 최적화

```typescript
// 독립적인 작업은 동시 실행
const [task1, task2] = await Promise.all([
  TaskCreate({ /* 목업 생성 */ }),
  TaskCreate({ /* 문서 초안 */ })
]);

// 의존 작업은 순차 실행
const task3 = await TaskCreate({ /* 스크린샷 */ });
await addBlockedBy(task3.id, task1.id);
```

### 4. 에러 처리

| 시나리오 | 처리 |
|----------|------|
| Task 1 실패 | Task 2, 3 자동 취소 |
| Task 2 실패 | Task 3 자동 취소, Task 1 유지 |
| 타임아웃 | 30초 초과 시 경고 + 수동 개입 |

---

## Hook Event Coverage 현황

### 1. 지원 이벤트

| Event | 구현 | Hook 파일 | 차단 가능 |
|-------|:----:|-----------|:--------:|
| **PreToolUse** | ✅ | `tool_validator.py`, `branch_guard.py` | ✅ |
| **PostToolUse** | ✅ | `post_edit_check.js` | ❌ |
| **SessionStart** | ✅ | `session_init.py` | ❌ |
| **SessionEnd** | ✅ | (없음, 로깅만) | ❌ |
| **SubagentStop** | ✅ | (없음, 로깅만) | ❌ |
| **Notification** | ❌ | (미지원) | - |

### 2. 이벤트별 활용

#### PreToolUse

**목적**: 도구 실행 전 검증 및 차단

```python
# tool_validator.py
if "taskkill /F /IM node.exe" in command:
    return {"decision": "reject", "message": "전체 프로세스 종료 금지"}
```

#### PostToolUse

**목적**: 도구 실행 후 자동 검증 (비차단)

```javascript
// post_edit_check.js
if (isPython) {
  execSync(`ruff check --fix ${filePath}`);
  return {decision: "approve", message: "✅ ruff clean"};
}
```

#### SessionStart

**목적**: 세션 초기화 검사

```python
# session_init.py
if not is_absolute_path(cwd):
    log_warning("상대 경로 사용 감지")
```

### 3. 미지원 이벤트

| Event | 상태 | 계획 |
|-------|------|------|
| **Notification** | 미지원 | 향후 고려 (사용자 알림 시) |
| **ContextUpdate** | 미정의 | 공식 문서 부재 |

---

## 기술적 결정사항

### 1. Node.js vs Bash

| 기준 | Node.js | Bash |
|------|:-------:|:----:|
| Windows 호환성 | ✅ | ❌ |
| JSON 파싱 | ✅ | ⚠️ (jq 필요) |
| 타임아웃 제어 | ✅ | ⚠️ (복잡) |
| 기존 Hook 일관성 | ⚠️ (Python 혼재) | ❌ |

**선택**: Node.js (Windows 환경 우선)

### 2. 차단 vs 비차단

| Hook | 차단 | 이유 |
|------|:----:|------|
| PreToolUse | ✅ | 도구 실행 **전** → 차단 의미 있음 |
| PostToolUse | ❌ | 도구 실행 **후** → 차단 무의미 |

### 3. 테스트 실행 전략

| 방식 | 장점 | 단점 |
|------|------|------|
| **개별 파일만** | 빠름 (30초 이내) | 통합 테스트 누락 |
| 전체 테스트 | 완전한 검증 | 120초 크래시 위험 |

**선택**: 개별 파일만 (안정성 우선)

### 4. MCP 서버 범위

| 옵션 | 범위 | 선택 |
|------|------|:----:|
| Global | 모든 프로젝트 | ✅ |
| Project | 단일 프로젝트 | ❌ |

**이유**: Playwright는 범용 도구 → Global 설치 효율적

---

## 검증 전략

### 1. PostToolUse Hook 검증

#### 테스트 케이스

| 케이스 | 입력 | 예상 출력 |
|--------|------|----------|
| Python 파일 수정 | `src/auth.py` | `✅ ruff clean` |
| Python + 테스트 | `src/auth.py` + `tests/test_auth.py` | `🧪 pytest passed` |
| TypeScript 수정 | `src/App.tsx` | `💡 tsc 권장` |
| 스킵 패턴 | `node_modules/lib.js` | (Hook 미실행) |
| Timeout 초과 | 30초+ 테스트 | `⚠️ timeout` |

#### 검증 명령

```powershell
# 1. Python 파일 수정
echo "# test" >> C:\claude\src\agents\config.py

# 2. Hook 로그 확인
cat C:\claude\.claude\hooks\post_edit_check.log

# 3. 예상 출력
# ✅ ruff check clean
# 🧪 No test file found
```

### 2. Playwright CLI 검증

```powershell
# 1. Playwright 설치 확인
npx playwright --version

# 2. 목업 생성
echo '<h1>Test</h1>' > C:\claude\docs\mockups\test.html

# 3. 스크린샷 생성
npx playwright screenshot file:///C:/claude/docs/mockups/test.html C:\claude\docs\images\test.png

# 4. 이미지 확인
Test-Path C:\claude\docs\images\test.png
```

### 3. Task Decomposition 검증

```typescript
// 순차 실행 확인
const start = Date.now();
const task1 = await TaskCreate({...});
await task1.wait();
const task2 = await TaskCreate({...});
await addBlockedBy(task2.id, task1.id);
await task2.wait();
const elapsed = Date.now() - start;

// Task 2가 Task 1 완료 후 시작되었는지 확인
assert(elapsed > task1.duration);
```

### 4. Event Coverage 검증

| Event | 검증 방법 |
|-------|----------|
| PreToolUse | 차단 명령 실행 → `reject` 확인 |
| PostToolUse | Python 파일 수정 → ruff 실행 확인 |
| SessionStart | 세션 시작 → 경고 로그 확인 |

---

## 부록

### A. 관련 파일

| 파일 | 역할 |
|------|------|
| `.claude/hooks/post_edit_check.js` | PostToolUse 메인 로직 |
| `.claude/settings.json` | Hook 등록 |
| `.claude/settings.local.json` | MCP 권한 |
| `~/.claude.json` | MCP 서버 설정 |

### B. 참조 문서

- `.claude/rules/03-git.md` - Hook 강제 규칙
- `.claude/rules/07-build-test.md` - 빌드/테스트 명령
- `docs/01-plan/hooks-improvement.plan.md` - 계획 문서

### C. 마이그레이션 가이드

기존 프로젝트에 적용:

```powershell
# 1. hooks 디렉토리 생성
mkdir .claude\hooks

# 2. post_edit_check.js 복사
Copy-Item C:\claude\.claude\hooks\post_edit_check.js .claude\hooks\

# 3. settings.json 업데이트
# (PostToolUse 섹션 추가)

# 4. Playwright 설치
npm install -D @playwright/test
npx playwright install
```

---

**변경 이력**

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-06 | 초기 설계 문서 작성 |
