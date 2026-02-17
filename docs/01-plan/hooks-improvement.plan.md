# Hooks Improvement - PDCA Plan

**Version**: 1.0.0
**Date**: 2026-02-06
**Author**: Claude AI
**Status**: Proposed
**Complexity**: 3/5

---

## 1. 프로젝트 개요

### 1.1 배경

SNS 트렌드 분석에서 도출된 Hook 시스템 개선 요구사항 4가지를 반영합니다. 현재 Claude Code Hook 시스템은 PreToolUse 중심의 차단 로직만 제공하며, 파일 수정 후 품질 검증 및 백그라운드 작업 완료 알림 메커니즘이 부재합니다.

### 1.2 핵심 문제

| # | 현재 문제 | 영향 |
|:-:|----------|------|
| 1 | PostToolUse Hook 부재 | 파일 수정 후 자동 린트/테스트 불가 |
| 2 | Task 의존성 패턴 비표준화 | Multi-Agent 작업 분해 시 명시적 차단 관계 누락 |
| 3 | Playwright CLI 전용 사용 | 브라우저 제어에 CLI 명령만 사용 |
| 4 | 백그라운드 완료 알림 부재 | 장시간 작업(npm install 등) 상태 파악 어려움 |

### 1.3 핵심 목표

- TDD Auto-validation Loop 구축 (PostToolUse → ruff + pytest)
- TaskCreate API의 addBlockedBy 메서드 표준 패턴 정립
- Playwright CLI 기반 E2E 자동화 워크플로우 개선
- Notification Hook을 통한 백그라운드 작업 완료 알림

---

## 2. 개선 항목 (4개)

### 2.1 PostToolUse Hook - TDD Auto-validation Loop

**현황**: PreToolUse Hook만 존재 (차단 로직만 가능)

**목표**: 파일 수정 후 자동 품질 검증 파이프라인 구축

**범위**:
- `.claude/settings.json`에 PostToolUse Hook 등록
- `.claude/hooks/post_edit_check.js` 신규 생성
  - Edit/Write 도구 사용 후 트리거
  - Python 파일(`.py`) 감지 시 `ruff check {file} --fix` 자동 실행
  - 테스트 파일(`test_*.py`) 수정 시 해당 파일만 `pytest {file} -v` 실행
  - 실패 시 Claude에게 에러 메시지 반환 (자동 수정 트리거)

**기대 효과**:
- TDD Red-Green-Refactor 사이클의 Green 단계 자동 검증
- 린트 에러 즉시 탐지 및 자동 수정
- 테스트 실패 시 즉각적인 피드백 루프

**영향 파일**:
- `C:\claude\.claude\settings.json` (PostToolUse 섹션 추가)
- `C:\claude\.claude\hooks\post_edit_check.js` (신규)

**기술 스택**:
- Node.js (Claude Code Hook 런타임)
- Python subprocess (ruff, pytest 실행)

**검증 방법**:
```powershell
# 테스트: Python 파일 수정 후 Hook 자동 트리거 확인
echo "import sys" > C:\claude\test_hook.py
# 예상: ruff check 자동 실행 → "All checks passed!"

echo "def test_fail(): assert False" > C:\claude\tests\test_hook.py
# 예상: pytest 자동 실행 → Claude에게 실패 메시지 전달
```

---

### 2.2 Multi-Agent Task 의존성 표준화

**현황**: Task 분해 시 의존성을 설명 텍스트로만 표현

**목표**: TaskCreate API의 `addBlockedBy()` 메서드를 활용한 명시적 의존성 관리

**범위**:
- 표준 패턴 문서화 (`.claude/rules/10-task-decomposition.md` 신규)
- 3단계 워크플로우 예시 정립:
  ```typescript
  const task1 = TaskCreate("designer", "HTML 목업 생성", { model: "sonnet" });
  const task2 = TaskCreate("qa-tester", "Playwright 스크린샷 캡처", { model: "haiku" })
                  .addBlockedBy(task1);  // task1 완료 후 실행
  const task3 = TaskCreate("writer", "문서에 이미지 삽입", { model: "haiku" })
                  .addBlockedBy(task2);  // task2 완료 후 실행
  ```
- Orchestrator에게 의존성 시각화 요구 (DAG 다이어그램 자동 생성)

**기대 효과**:
- Multi-Agent 병렬 실행 시 데이터 레이스 방지
- 의존성 그래프 자동 생성으로 복잡한 워크플로우 가시성 확보
- 에러 추적 간소화 (어느 Task에서 실패했는지 명확)

**영향 파일**:
- `.claude/rules/10-task-decomposition.md` (신규 - 표준 패턴 문서)
- `docs/AGENTS_REFERENCE.md` (의존성 패턴 예시 추가)

**적용 대상**:
- `/auto --mockup` (HTML → 스크린샷 → 문서 삽입)
- `/check --all` (린트 → 테스트 → 보안 검사)
- `/parallel test` (유닛 → 통합 → E2E 순차 실행)

---

### 2.3 Playwright CLI 워크플로우 개선

**현황**: `.claude/skills/webapp-testing/`에서 Playwright CLI 사용 중

**목표**: CLI 기반 스크린샷 및 테스트 워크플로우 최적화

**범위**:
- 스크린샷 자동화:
  ```powershell
  npx playwright screenshot docs/mockups/feature.html docs/images/feature.png
  ```
- 스킬 업데이트: `webapp-testing/SKILL.md`에서 CLI 명령 가이드 제공
  - 스크린샷: `npx playwright screenshot <url> <output>`
  - 헤드리스 테스트: `npx playwright test`
  - 디버깅: `npx playwright test --headed --debug`
- 장점:
  - 경량 (추가 서버 불필요)
  - 표준 도구 활용
  - CI/CD 통합 용이

**기대 효과**:
- `/auto --mockup` 워크플로우에서 Playwright 스크린샷 단계 자동화
- 일관된 CLI 기반 워크플로우
- 외부 의존성 최소화

**영향 파일**:
- `.claude/skills/webapp-testing/SKILL.md` (CLI 사용 예시 추가)

**의존성**:
- Playwright CLI (npm/npx 기반)
- Node.js 런타임

**검증 방법**:
```powershell
# 목업 생성
echo '<h1>Test</h1>' > docs/mockups/test.html

# 스크린샷 생성
npx playwright screenshot file:///$PWD/docs/mockups/test.html docs/images/test.png

# 이미지 확인
Test-Path docs/images/test.png
```

---

### 2.4 Notification Hook - 백그라운드 완료 알림

**현황**: 백그라운드 작업(`run_in_background: true`) 완료 여부 파악 불가

**목표**: 장시간 작업 완료 시 Claude에게 Notification 전송

**범위**:
- `.claude/settings.json`에 Notification Hook 등록 (신규 Hook 타입 제안)
- `.claude/hooks/background_notifier.js` 신규 생성
  - 백그라운드 작업 완료 이벤트 수신
  - npm install, pip install, tsc, pytest 등 감지
  - Claude에게 "✅ npm install 완료 (2분 소요)" 메시지 전송
  - 실패 시 "❌ pytest 실패: [에러 요약]" 전송

**기대 효과**:
- 장시간 작업 중 다른 Task 진행 가능 (멀티태스킹)
- 사용자 개입 없이 자동 후속 작업 트리거
- CI/CD 파이프라인에서 유용 (빌드 완료 → 자동 테스트)

**영향 파일**:
- `C:\claude\.claude\settings.json` (Notification 섹션 추가)
- `C:\claude\.claude\hooks\background_notifier.js` (신규)

**기술 제약**:
- Notification Hook은 Claude Code 공식 지원 여부 확인 필요
- 대안: PostToolUse Hook에서 백그라운드 작업 폴링

**검증 방법**:
```powershell
# 백그라운드 작업 실행
npm install --save-dev playwright  # 예상: 1-2분 소요

# 예상 동작:
# 1. Claude가 다른 Task 진행
# 2. 완료 시 "✅ npm install 완료 (85초 소요)" 알림
# 3. 후속 작업 자동 시작
```

---

## 3. 실행 일정

| Phase | 항목 | 시작 | 예상 완료 | 우선순위 |
|:-----:|------|:----:|:---------:|:--------:|
| 1 | PostToolUse Hook 구현 | 2026-02-06 | 2026-02-06 | P0 |
| 1 | Task 의존성 표준 문서 작성 | 2026-02-06 | 2026-02-06 | P1 |
| 2 | Playwright CLI 워크플로우 개선 | 2026-02-07 | 2026-02-07 | P1 |
| 2 | Notification Hook 제안/구현 | 2026-02-08 | 2026-02-10 | P2 |
| 3 | 통합 검증 (E2E) | 2026-02-11 | 2026-02-11 | P0 |

---

## 4. 성공 지표

| 지표 | 현재 | 목표 | 측정 방법 |
|------|:----:|:----:|----------|
| 파일 수정 후 자동 검증률 | 0% | 95% | PostToolUse Hook 트리거 횟수 / 파일 수정 횟수 |
| Multi-Agent 의존성 에러 | 월 3-5건 | 0건 | addBlockedBy 사용률 100% |
| Playwright 워크플로우 효율성 | 수동 스크린샷 생성 | CLI 자동화 스크립트 | 워크플로우 자동화 완료 |
| 백그라운드 작업 대기 시간 | 수동 확인 (평균 5분 지연) | 자동 알림 (0초 지연) | Notification Hook 응답 시간 |

---

## 5. 위험 요소

| 위험 | 확률 | 영향 | 완화 방안 |
|------|:----:|:----:|----------|
| PostToolUse Hook 무한 루프 | 중 | 높 | Hook 내부에서 파일 수정 금지 (readonly 모드) |
| Playwright CLI 타임아웃 | 낮 | 중 | 타임아웃 60초 설정 + 에러 핸들링 |
| Notification Hook 공식 미지원 | 높 | 중 | PostToolUse에서 폴링 방식으로 대체 |
| ruff/pytest 실행 시간 초과 | 낮 | 중 | 타임아웃 30초 설정 + 비동기 실행 |
| Task 의존성 순환 참조 | 낮 | 높 | addBlockedBy에서 순환 감지 로직 추가 필요 (제안) |

---

## 6. 파일 영향 범위

### 신규 파일

| 파일 | 크기 | 역할 |
|------|:----:|------|
| `C:\claude\.claude\hooks\post_edit_check.js` | ~100줄 | PostToolUse Hook 실행 스크립트 |
| `C:\claude\.claude\hooks\background_notifier.js` | ~80줄 | Notification Hook 실행 스크립트 |
| `C:\claude\.claude\rules\10-task-decomposition.md` | ~200줄 | Task 의존성 표준 패턴 문서 |

### 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `C:\claude\.claude\settings.json` | PostToolUse, Notification Hook 등록 |
| `C:\claude\.claude\skills\webapp-testing\SKILL.md` | MCP 사용 예시 추가 |
| `C:\claude\docs\AGENTS_REFERENCE.md` | Task 의존성 패턴 예시 추가 |

---

## 7. 참조 문서

| 문서 | 용도 |
|------|------|
| `.claude/rules/04-tdd.md` | TDD 규칙 (Red-Green-Refactor) |
| `.claude/rules/08-skill-routing.md` | Multi-Agent 인과관계 그래프 |
| `docs/BUILD_TEST.md` | 빌드/테스트 명령어 참조 |
| `.claude/hooks/branch_guard.py` | 기존 PreToolUse Hook 예시 |
| Claude Code Hook 공식 문서 | Hook 타입 및 이벤트 구조 |

---

## 8. 구현 세부사항

### 8.1 PostToolUse Hook 구조

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "node .claude/hooks/post_edit_check.js"
          }
        ]
      }
    ]
  }
}
```

**post_edit_check.js 의사코드**:
```javascript
// stdin에서 tool_input.file_path 읽기
const filePath = JSON.parse(stdin).tool_input.file_path;

// Python 파일 감지
if (filePath.endsWith('.py')) {
  // ruff check 실행
  const ruffResult = exec(`ruff check ${filePath} --fix`);
  if (ruffResult.exitCode !== 0) {
    return { error: `Ruff failed: ${ruffResult.stderr}` };
  }

  // 테스트 파일 감지
  if (filePath.includes('test_')) {
    const pytestResult = exec(`pytest ${filePath} -v`);
    if (pytestResult.exitCode !== 0) {
      return { error: `Pytest failed: ${pytestResult.stderr}` };
    }
  }
}

return { success: true };
```

### 8.2 Task 의존성 표준 패턴

**시나리오**: `/auto --mockup` 실행 시 HTML → 스크린샷 → 문서 삽입

```typescript
// Phase 1: HTML 목업 생성
const htmlTask = await TaskCreate({
  subagent_type: "designer",
  model: "sonnet",
  prompt: "docs/mockups/feature-x.html에 HTML 목업 생성"
});

// Phase 2: 스크린샷 캡처 (htmlTask 완료 후)
const screenshotTask = await TaskCreate({
  subagent_type: "qa-tester",
  model: "haiku",
  prompt: "Playwright로 docs/mockups/feature-x.html 스크린샷 → docs/images/feature-x.png"
}).addBlockedBy(htmlTask);

// Phase 3: 문서 삽입 (screenshotTask 완료 후)
const docTask = await TaskCreate({
  subagent_type: "writer",
  model: "haiku",
  prompt: "docs/01-plan/feature-x.plan.md에 ![](../images/feature-x.png) 삽입"
}).addBlockedBy(screenshotTask);

// 실행 순서 보장: htmlTask → screenshotTask → docTask
```

### 8.3 Playwright CLI 워크플로우

```powershell
# 스크린샷 생성
npx playwright screenshot <url> <output-path>

# 목업 스크린샷 예시
npx playwright screenshot file:///C:/claude/docs/mockups/feature.html docs/images/feature.png

# 검증
Test-Path docs/images/feature.png
```

**webapp-testing/SKILL.md 업데이트**:
```markdown
## Playwright CLI 사용 예시

스크린샷 생성:
\```powershell
npx playwright screenshot file:///$PWD/docs/mockups/feature.html docs/images/feature.png
\```

E2E 테스트:
\```powershell
npx playwright test --headed
\```

디버깅:
\```powershell
npx playwright test --headed --debug
\```
```

---

## 9. 롤백 계획

| 단계 | 문제 발생 시 조치 |
|:----:|------------------|
| PostToolUse Hook | `.claude/settings.json`에서 PostToolUse 섹션 제거 |
| Playwright CLI | CLI 명령 제거 (기본 도구로 유지) |
| Task 의존성 문서 | `.claude/rules/10-task-decomposition.md` 삭제 (기존 방식 유지) |
| Notification Hook | `.claude/settings.json`에서 Notification 섹션 제거 |

**백업 필수 파일**:
- `.claude/settings.json.backup`
- `.claude/hooks/*.backup`

---

## 10. 후속 과제

| 과제 | 우선순위 | 예상 시작 |
|------|:--------:|:---------:|
| PreCommit Hook에 PostToolUse 통합 | P1 | 2026-02-12 |
| Task DAG 시각화 도구 구축 | P2 | 2026-02-15 |
| Playwright CLI 스크립트 라이브러리 확장 | P2 | 2026-02-20 |
| Hook 성능 메트릭 수집 (`.omc/stats/hook-metrics.json`) | P3 | 2026-03-01 |

