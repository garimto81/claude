# Skill Audit Optimization Work Plan

## 배경 (Background)

- **요청 내용**: 41개 스킬 전수 감사 결과를 기반으로 Dead Code 제거, 중복 통합, 메타데이터 정규화를 수행
- **해결하려는 문제**: DEPRECATED stub 미삭제로 인한 디렉토리 혼잡, 고도의 기능 중복으로 인한 유지보수 부담, 메타데이터 누락으로 인한 스킬 라우팅 불일치

## 구현 범위 (Scope)

### 포함 항목

- Task 1: Dead Code 4개 스킬 디렉토리 삭제 (`skill-creator`, `pre-work-research`, `agent-teamworks`, `final-check-automation`)
- Task 2: `code-quality-checker` 기능을 `/check`로 흡수 통합
- Task 3: `webapp-testing` 기능을 `playwright-wrapper`로 흡수 통합
- Task 4: 8개 스킬에 `version: 1.0.0` 메타데이터 추가
- Task 5: `08-skill-routing.md` 스킬 매핑 테이블 업데이트

### 제외 항목

- `/auto` Phase 구조 자체 변경
- 신규 스킬 설계
- 스킬 로직(워크플로우) 의미 변경
- `code-quality-checker/scripts/run_quality_check.py` 삭제 (check로 이관 후 삭제)

## 영향 파일 (Affected Files)

### 삭제 예정 디렉토리

| # | 경로 | 삭제 근거 |
|---|------|----------|
| 1 | `C:/claude/.claude/skills/skill-creator/` | DEPRECATED stub, triggers.keywords: [], 플러그인 충돌 |
| 2 | `C:/claude/.claude/skills/pre-work-research/` | DEPRECATED stub, `/research web`으로 통합 완료 |
| 3 | `C:/claude/.claude/skills/agent-teamworks/` | `src/agents/teams/*.py` 전부 미존재. Dead skill |
| 4 | `C:/claude/.claude/skills/final-check-automation/` | `/auto` Phase 3-4 + `/check` 완전 중복. Phase 5/6 잔재 |

### 수정 예정 파일

| # | 경로 | 변경 내용 |
|---|------|----------|
| 5 | `C:/claude/.claude/skills/check/SKILL.md` | React 검사 규칙 + Level 1/2/3 구조 추가. `scripts/run_quality_check.py` 참조 이관 |
| 6 | `C:/claude/.claude/skills/playwright-wrapper/SKILL.md` | Docker 환경 + safe_browser 패턴 통합. `scripts/with_server.py` 참조 이관 |
| 7 | `C:/claude/.claude/skills/figma/SKILL.md` | frontmatter에 `version: 1.0.0` 추가 |
| 8 | `C:/claude/.claude/skills/jira/SKILL.md` | frontmatter에 `version: 1.0.0` 추가 |
| 9 | `C:/claude/.claude/skills/prd-sync/SKILL.md` | frontmatter에 `version: 1.0.0` 추가 |
| 10 | `C:/claude/.claude/skills/audit/SKILL.md` | frontmatter에 `version: 1.0.0` 추가 |
| 11 | `C:/claude/.claude/skills/chunk/SKILL.md` | frontmatter에 `version: 1.0.0` 추가 |
| 12 | `C:/claude/.claude/skills/confluence/SKILL.md` | frontmatter에 `version: 1.0.0` 추가 |
| 13 | `C:/claude/.claude/skills/deploy/SKILL.md` | frontmatter에 `version: 1.0.0` 추가 |
| 14 | `C:/claude/.claude/skills/todo/SKILL.md` | frontmatter에 `version: 1.0.0` 추가 |
| 15 | `C:/claude/.claude/rules/08-skill-routing.md` | Deprecated 테이블에 삭제/통합 스킬 반영 |

### 신규 생성 파일

없음 (기존 컴포넌트 재활용 원칙)

## 위험 요소 (Risks)

### 잠재적 부작용

1. **final-check-automation 삭제 시 `run_final_check.py` 접근 불가**: `final-check-automation/scripts/run_final_check.py`를 직접 참조하는 워크플로우가 있을 경우 실행 실패. 삭제 전 grep으로 외부 참조 여부 검증 필수 (현재 조사 결과: `final-check-automation/SKILL.md` 자체 참조만 확인됨).

2. **agent-teamworks 삭제 시 `/team` 키워드 트리거 소실**: `agent-teamworks`의 `keywords: ["/team", "/teamwork", "team dev", ...]`가 삭제되면 해당 키워드로 시작되는 요청이 라우팅되지 않음. 단, 참조 코드(`src/agents/teams/*.py`)가 미존재하므로 기능 자체가 작동 불가 상태였음.

3. **check/SKILL.md 내용 추가로 파일 크기 증가**: React 검사 규칙 + Level 1/2/3 구조를 통합하면 현재 31줄에서 최대 150줄로 증가 가능. Progressive Disclosure 적용을 검토할 것 (references/ 분리).

4. **playwright-wrapper에 Docker 패턴 통합 시 키워드 충돌 재발**: webapp-testing의 Docker 관련 트리거가 playwright-wrapper로 이관되면 두 스킬 경계가 다시 모호해질 수 있음. 통합 후 단일 스킬로 완전 대체 방향 검토 필요.

### Edge Cases

1. **`code-quality-checker/scripts/run_quality_check.py`의 직접 실행 참조**: 사용자가 `python .claude/skills/code-quality-checker/scripts/run_quality_check.py` 명령을 직접 입력하던 패턴이 있다면, 스킬 디렉토리 삭제 후 실행 실패. 스크립트를 `check/scripts/`로 이동하거나 wrapper 경로 유지 필요.

2. **`final-check-automation`이 `webapp-testing`을 내부적으로 호출**: `final-check-automation/SKILL.md` 라인 119-123에서 `webapp-testing/scripts/with_server.py`를 직접 참조. `final-check-automation` 삭제 후 해당 참조는 사라지지만, `check/SKILL.md`로 통합 시 동일 참조를 포함해야 함.

3. **version 필드 포맷 불일치**: 일부 스킬은 `version: 2.0.0`(check, debug 등)을 사용하고 신규 추가는 `version: 1.0.0`. 스키마상 충돌은 없으나 버전 정책 문서화 부재 상태.

## 태스크 목록 (Tasks)

---

### Task 1: Dead Code 4개 스킬 삭제

**설명**: DEPRECATED 상태이거나 참조 코드가 미존재하는 4개 스킬 디렉토리를 삭제한다.

**수행 방법**:

Step 1-1: 삭제 전 외부 참조 검증 (grep)
```
Grep pattern="skill-creator|pre-work-research|agent-teamworks|final-check-automation"
     path="C:/claude/.claude/skills/"
     glob="*.md"
     제외: 스킬 자체 SKILL.md
```
- 외부 참조가 발견되면 해당 파일을 먼저 수정 후 삭제 진행

Step 1-2: 디렉토리 삭제
```bash
rm -rf C:/claude/.claude/skills/skill-creator/
rm -rf C:/claude/.claude/skills/pre-work-research/
rm -rf C:/claude/.claude/skills/agent-teamworks/
rm -rf C:/claude/.claude/skills/final-check-automation/
```

**Acceptance Criteria**:
- 4개 디렉토리가 존재하지 않음 (`ls` 결과 없음)
- `C:/claude/.claude/skills/` 하위에 해당 디렉토리명이 없음
- 삭제 후 다른 SKILL.md에서 이 스킬들을 참조하는 경우 0건

---

### Task 2: `code-quality-checker` → `/check` 흡수 통합

**설명**: `code-quality-checker`의 React 검사 규칙 + Level 1/2/3 구조를 `check/SKILL.md`에 추가하고, `scripts/run_quality_check.py`를 `check/scripts/`로 이관한 후 `code-quality-checker` 디렉토리를 삭제한다.

**수행 방법**:

Step 2-1: `check/SKILL.md`에 추가할 내용 결정
- `code-quality-checker/SKILL.md`의 검사 수준(Level 1/2/3) 섹션
- React 성능 검사 섹션 (`/check --react` 서브커맨드 추가)
- `vercel-react-best-practices` 연동 참조

Step 2-2: `check/scripts/` 디렉토리 생성 후 스크립트 이관
```bash
mkdir -p C:/claude/.claude/skills/check/scripts/
cp C:/claude/.claude/skills/code-quality-checker/scripts/run_quality_check.py \
   C:/claude/.claude/skills/check/scripts/run_quality_check.py
```

Step 2-3: `check/SKILL.md` 업데이트 (현재 31줄)
- frontmatter: `--react`, `--security`, `--level` 옵션 추가
- 검사 수준 섹션 추가
- 스크립트 경로를 `check/scripts/run_quality_check.py`로 업데이트

Step 2-4: `code-quality-checker` 디렉토리 삭제
```bash
rm -rf C:/claude/.claude/skills/code-quality-checker/
```

**Acceptance Criteria**:
- `check/SKILL.md`에 Level 1/2/3 섹션이 존재
- `check/SKILL.md`에 `--react` 서브커맨드 설명이 존재
- `check/scripts/run_quality_check.py`가 존재하고 실행 가능
- `code-quality-checker/` 디렉토리가 존재하지 않음
- `check/SKILL.md`의 스크립트 참조 경로가 `check/scripts/run_quality_check.py`로 일치

---

### Task 3: `webapp-testing` → `playwright-wrapper` 흡수 통합

**설명**: `webapp-testing`의 Docker 환경 + `safe_browser` 패턴을 `playwright-wrapper/SKILL.md`에 통합하고, `scripts/with_server.py`를 `playwright-wrapper/scripts/`로 이관한 후 `webapp-testing` 디렉토리를 삭제한다.

**수행 방법**:

Step 3-1: `playwright-wrapper/SKILL.md`에 추가할 내용 결정
- `webapp-testing/SKILL.md`의 Docker 환경 테스트 흐름 섹션
- `safe_browser` 컨텍스트 매니저 패턴 (Python SDK)
- `with_server.py` 스크립트 참조

Step 3-2: `playwright-wrapper/scripts/` 디렉토리 생성 후 스크립트 이관
```bash
mkdir -p C:/claude/.claude/skills/playwright-wrapper/scripts/
cp C:/claude/.claude/skills/webapp-testing/scripts/with_server.py \
   C:/claude/.claude/skills/playwright-wrapper/scripts/with_server.py
```

Step 3-3: `playwright-wrapper/SKILL.md` 업데이트
- "Docker 환경 테스트" 섹션 추가 (`with_server.py` 사용법)
- `safe_browser` 패턴 통합
- 트리거 keywords에서 webapp-testing과 중복되는 항목 정리

Step 3-4: `webapp-testing` 디렉토리 삭제
```bash
rm -rf C:/claude/.claude/skills/webapp-testing/
```

**Acceptance Criteria**:
- `playwright-wrapper/SKILL.md`에 Docker 환경 테스트 섹션이 존재
- `playwright-wrapper/scripts/with_server.py`가 존재하고 실행 가능
- `webapp-testing/` 디렉토리가 존재하지 않음
- `playwright-wrapper/SKILL.md`의 스크립트 참조 경로가 `playwright-wrapper/scripts/with_server.py`로 일치

---

### Task 4: 메타데이터 정규화 — `version: 1.0.0` 추가 (8개 스킬)

**설명**: `version` 필드가 누락된 8개 스킬의 frontmatter에 `version: 1.0.0`을 추가한다.

**수행 방법**: 각 SKILL.md frontmatter의 `name:` 행 다음 줄에 `version: 1.0.0` 삽입

| # | 파일 경로 | 삽입 위치 |
|---|----------|----------|
| 1 | `C:/claude/.claude/skills/figma/SKILL.md` | `name: figma` 행 다음 |
| 2 | `C:/claude/.claude/skills/jira/SKILL.md` | `name: jira` 행 다음 |
| 3 | `C:/claude/.claude/skills/prd-sync/SKILL.md` | `name: prd-sync` 행 다음 |
| 4 | `C:/claude/.claude/skills/audit/SKILL.md` | `name: audit` 행 다음 |
| 5 | `C:/claude/.claude/skills/chunk/SKILL.md` | `name: chunk` 행 다음 |
| 6 | `C:/claude/.claude/skills/confluence/SKILL.md` | `name: confluence` 행 다음 |
| 7 | `C:/claude/.claude/skills/deploy/SKILL.md` | `name: deploy` 행 다음 |
| 8 | `C:/claude/.claude/skills/todo/SKILL.md` | `name: todo` 행 다음 |

**Acceptance Criteria**:
- 8개 스킬 모두 frontmatter에 `version:` 필드가 존재
- `grep "^version:" C:/claude/.claude/skills/{figma,jira,prd-sync,audit,chunk,confluence,deploy,todo}/SKILL.md` 결과가 8줄

---

### Task 5: `08-skill-routing.md` 스킬 매핑 테이블 업데이트

**설명**: `08-skill-routing.md`의 Deprecated 테이블에 삭제/통합된 스킬을 반영하고, `/check`와 `playwright-wrapper`의 기능 확장을 매핑 테이블에 업데이트한다.

**수행 방법**:

Step 5-1: Deprecated 테이블에 항목 추가
```
| `/team`, `/teamwork` | → 삭제 (참조 코드 미존재) |
| `final-check-automation` | → `/check --e2e --security` |
| `code-quality-checker` | → `/check` |
| `webapp-testing` | → `playwright-wrapper` |
```

Step 5-2: 스킬 매핑 테이블 업데이트 (해당 시)
- `/check`의 서브커맨드에 `--react`, `--level` 추가 반영
- `playwright-wrapper`의 Docker 환경 통합 반영

**파일**: `C:/claude/.claude/rules/08-skill-routing.md`
**수정 위치**: 라인 27-38 (Deprecated 스킬 섹션)

**Acceptance Criteria**:
- `08-skill-routing.md`의 Deprecated 테이블에 4개 삭제 항목이 기록됨
- 매핑 테이블에서 삭제된 스킬명이 active entry로 존재하지 않음
- `/check` 서브커맨드 설명이 React 검사 옵션을 포함

---

## 구현 흐름

```
  +------------------+     +------------------+     +------------------+
  | Task 1           |     | Task 2           |     | Task 3           |
  | Dead Code 삭제   |     | code-quality     |     | webapp-testing   |
  | (4개 스킬)       |     | → check 통합     |     | → playwright 통합|
  +--------+---------+     +--------+---------+     +--------+---------+
           |                        |                        |
           v                        v                        v
  +------------------+     +------------------+     +------------------+
  | Task 4           |     | Task 5                                    |
  | version 메타     |     | 08-skill-routing.md 업데이트              |
  | 데이터 (8개)     |     | (Task 1-3 완료 후 실행)                   |
  +------------------+     +-------------------------------------------+
```

Task 1, 2, 3, 4는 병렬 실행 가능. Task 5는 1-3 완료 후 실행.

## 커밋 전략 (Commit Strategy)

| 순서 | 커밋 메시지 | 포함 변경 |
|------|-----------|----------|
| 1 | `chore(skills): DEPRECATED + Dead Code 스킬 4개 삭제` | Task 1 |
| 2 | `refactor(skills): code-quality-checker → check 흡수 통합` | Task 2 |
| 3 | `refactor(skills): webapp-testing → playwright-wrapper 흡수 통합` | Task 3 |
| 4 | `chore(skills): version 메타데이터 정규화 8개 스킬` | Task 4 |
| 5 | `docs(rules): 08-skill-routing 삭제/통합 스킬 반영` | Task 5 |
