# Workflow Review Precision Work Plan

## 배경 (Background)

워크플로우 정밀 검토를 통해 발견된 4개 이슈(CRITICAL 2건, HIGH 2건)를 수정하는 작업.
- v25 재검토 이후 잔존하는 구 에이전트명 참조 및 주석 버그 정리
- MEMORY.md의 v23/v24 구현 상태 부정확 기록 정정
- 에이전트 수 불일치(41→42) 수정

## 구현 범위 (Scope)

**포함:**
- SKILL.md Phase 4.2 주석 1줄 수정 (구 에이전트명 → 현재 에이전트명)
- REFERENCE.md 구 에이전트명 패턴 교체 (다수 라인)
- MEMORY.md v23/v24 구현 상태 정정 및 에이전트 수 수정

**제외:**
- 실제 기능 구현 변경 (주석/문서 수정만)
- REFERENCE.md 구조 변경 (내용 교체만)
- 새 에이전트 추가 또는 삭제

## 영향 파일 (Affected Files)

**수정 예정:**
- `C:\claude\.claude\skills\auto\SKILL.md` — 라인 244 주석 1줄 수정
- `C:\claude\.claude\skills\auto\REFERENCE.md` — 라인 359, 360, 371, 383, 863, 879, 891, 894, 900, 903, 904, 908, 909, 947, 1205, 1206 및 유사 패턴
- `C:\Users\AidenKim\.claude\projects\C--claude\memory\MEMORY.md` — v23/v24 상태 정정, 에이전트 수 수정

**신규 생성 없음**

## 이슈 상세 (Issues)

### CRITICAL-1: SKILL.md Phase 4.2 주석 버그

| 항목 | 내용 |
|------|------|
| 파일 | `C:\claude\.claude\skills\auto\SKILL.md` |
| 라인 | 244 |
| 현재 | `# LIGHT: architect만 / STANDARD/HEAVY: architect → gap-detector → code-analyzer 순차` |
| 수정 | `# LIGHT: architect만 / STANDARD/HEAVY: architect → code-reviewer 순차` |
| 근거 | gap-detector(BKIT 삭제), code-analyzer(존재하지 않음) → code-reviewer가 담당 |

**Acceptance Criteria:** 라인 244에 `gap-detector`와 `code-analyzer` 문자열 미존재.

---

### CRITICAL-2: REFERENCE.md 구 에이전트명 잔존

| 항목 | 내용 |
|------|------|
| 파일 | `C:\claude\.claude\skills\auto\REFERENCE.md` |
| 패턴 교체 1 | 모드 비교표 라인 359-360, 371, 383: `gap-detector`, `code-analyzer` → `code-reviewer` |
| 패턴 교체 2 | 코드 블록 섹션 헤더 라인 863: `gap-detector → code-analyzer` → `code-reviewer` |
| 패턴 교체 3 | 라인 908-909: `gap-checker`, `quality-checker` bullet → 통합 설명으로 수정 |
| 패턴 교체 4 | 라인 947: `code-analyzer teammate prompt` → `code-reviewer teammate prompt` |
| 패턴 교체 5 | 라인 1205-1206: `Skill(ultraqa)` 제거, `code-analyzer에 Vercel BP` → `code-reviewer에 Vercel BP` |
| 패턴 교체 6 | 라인 900: `Architect, gap-detector, code-analyzer 모두` → `Architect, code-reviewer 모두` |

**위험:** `gap-checker`, `quality-checker`는 `name=` 파라미터(role alias)로 사용되는 경우 존재.
- 라인 873: `name="gap-checker"` — subagent_type이 `architect`이므로 name alias는 유지 가능
- 라인 891, 903, 904: `name="gap-checker"`, `name="quality-checker"` — name alias이므로 변경 불필요
- **수정 대상:** `subagent_type=` 값이나 설명 텍스트의 `gap-detector`, `code-analyzer`만 교체
- **유지 대상:** `name="gap-checker"`, `name="quality-checker"` (role alias는 임의 문자열 가능)

**Acceptance Criteria:** REFERENCE.md 내 `gap-detector`(subagent_type/설명), `code-analyzer`, `Skill(ultraqa)` 문자열 미존재. `gap-checker`/`quality-checker`는 name 파라미터 문맥에서만 잔존 허용.

---

### HIGH-1: MEMORY.md v23/v24 상태 부정확

| 항목 | 내용 |
|------|------|
| 파일 | `C:\Users\AidenKim\.claude\projects\C--claude\memory\MEMORY.md` |
| 현재 | v23.0, v24.0 모두 "완료"로 기록 |
| 실제 SKILL.md/REFERENCE.md 버전 | v22.1 |

**v23 구현 상태:**
- 구현됨: Opus→Sonnet 마이그레이션, HEAVY opus→sonnet 교체
- 미구현(SKILL.md 미반영): `--opus` 플래그, Model Tier 테이블(SCOUT/WORK/APEX)

**v24 구현 상태:**
- 구현됨: `--eco` 옵션, `--worktree` 옵션, REFERENCE.md Vercel BP 규칙 섹션
- 미구현(SKILL.md 미반영): `--note`, `--swarm N`, `--pipeline`, `--prd` 옵션; Phase 0 `is_react_project` 자동감지

**수정 방향:** v23/v24 항목의 "완료" 표현을 "부분 구현"으로 정정하고 미구현 기능 목록 명시.

**주의:** 완료된 작업 내역(Opus→Sonnet 마이그레이션 등) 훼손 금지. 상태 레이블 수정만.

**Acceptance Criteria:** MEMORY.md에 v23/v24 "부분 구현" 명시, 미구현 기능 목록 존재.

---

### HIGH-2: MEMORY.md 에이전트 수 불일치

| 항목 | 내용 |
|------|------|
| 파일 | `C:\Users\AidenKim\.claude\projects\C--claude\memory\MEMORY.md` |
| MEMORY 기록 | "로컬 에이전트 41개" |
| 실제 (.claude/agents/ glob 결과) | 42개 (.md 파일 42개 확인) |
| 수정 | `41개` → `42개` |

**Acceptance Criteria:** MEMORY.md 프로젝트 구조 섹션에 `42개` 기재.

## 위험 요소 (Risks)

**위험 1: name alias와 subagent_type 혼동**
- `gap-checker`, `quality-checker`는 `name=` 파라미터(역할 별칭)로 사용됨
- `subagent_type="architect"` + `name="gap-checker"` 형태는 정상 패턴
- 수정 시 `subagent_type` 값과 설명 텍스트만 변경하고 `name=` 값은 건드리지 말 것
- **검증 방법:** 수정 후 `name="gap-checker"` 패턴이 존재하는지 grep으로 확인 (존재해도 정상)

**위험 2: MEMORY.md 이전 완료 내역 훼손**
- v23/v24 섹션에 완료된 작업 목록이 혼재함
- "완료" 레이블만 "부분 구현"으로 수정하고 세부 내역 삭제 금지
- **검증 방법:** 수정 전후 MEMORY.md diff 확인 — 기존 bullet point 수 동일해야 함

**위험 3: REFERENCE.md 모드 비교표 일관성**
- 라인 359-383의 모드별 표에서 교체 누락 시 LIGHT/STANDARD/HEAVY 설명 불일치
- 세 모드 전부(359, 371, 383) 동시에 수정 필요

## 태스크 목록 (Tasks)

### Task 1: SKILL.md Phase 4.2 주석 수정

**수행 방법:**
- 파일: `C:\claude\.claude\skills\auto\SKILL.md`, 라인 244
- Edit 도구로 정확히 1줄 교체

**Before:**
```
# LIGHT: architect만 / STANDARD/HEAVY: architect → gap-detector → code-analyzer 순차
```

**After:**
```
# LIGHT: architect만 / STANDARD/HEAVY: architect → code-reviewer 순차
```

**Acceptance Criteria:**
- 라인 244의 `gap-detector`, `code-analyzer` 미존재
- 파일 전체 줄 수 변화 없음 (1줄 교체)

---

### Task 2: REFERENCE.md 모드 비교표 교체 (라인 359-384)

**수행 방법:**
- LIGHT 모드 표 라인 359-360: `gap-detector`, `E2E 스킵` → `code-reviewer`, `E2E 스킵`
- STANDARD 모드 표 라인 371: `gap-detector + code-analyzer` → `code-reviewer`
- HEAVY 모드 표 라인 383: `gap-detector + code-analyzer` → `code-reviewer`

**Acceptance Criteria:**
- 모드 비교표 3곳 모두 `code-reviewer` 사용
- `gap-detector`, `code-analyzer` 미존재 (해당 라인)

---

### Task 3: REFERENCE.md Step 4.2 섹션 교체 (라인 863-910)

**수행 방법:**
- 섹션 헤더 라인 863: `gap-detector → code-analyzer` → `code-reviewer`
- 라인 900: `Architect, gap-detector, code-analyzer 모두` → `Architect, code-reviewer 모두`
- 라인 908-909: bullet 설명에서 `gap-checker`, `quality-checker` 설명 단순화
- **유지:** `name="gap-checker"`, `name="quality-checker"` (role alias, 변경 불필요)

**Acceptance Criteria:**
- 섹션 헤더에 구 에이전트명 미존재
- `name="gap-checker"` 패턴 grep 결과 존재해도 정상 (alias이므로)

---

### Task 4: REFERENCE.md 코드 주석 교체 (라인 947)

**수행 방법:**
- 라인 947: `code-analyzer teammate prompt` → `code-reviewer teammate prompt`

**Acceptance Criteria:**
- 라인 947에 `code-analyzer` 미존재

---

### Task 5: REFERENCE.md 변경 이력 섹션 교체 (라인 1205-1206)

**수행 방법:**
- 라인 1205: `Skill(ultraqa) →` 텍스트에서 `Skill(ultraqa)` 제거 → `Lead 직접 QA + Executor 수정 위임`
- 라인 1206: `code-analyzer에 Vercel BP` → `code-reviewer에 Vercel BP`

**Acceptance Criteria:**
- `Skill(ultraqa)`, `code-analyzer에 Vercel BP` 미존재

---

### Task 6: MEMORY.md 에이전트 수 수정

**수행 방법:**
- 파일: `C:\Users\AidenKim\.claude\projects\C--claude\memory\MEMORY.md`
- 프로젝트 구조 섹션: `41개` → `42개`

**Acceptance Criteria:**
- `로컬 에이전트 42개` 기재

---

### Task 7: MEMORY.md v23/v24 상태 정정

**수행 방법:**
- v23.0 섹션 제목/설명에서 "완료" → "부분 구현" 추가
- 미구현 기능 목록 명시: `--opus 플래그`, `SCOUT/WORK/APEX Model Tier 테이블`
- v24.0 섹션에서 미구현 기능 목록 명시: `--note`, `--swarm N`, `--pipeline`, `--prd`, `Phase 0 is_react_project`
- 기존 완료 내역(Opus→Sonnet 마이그레이션 등) 보존

**Acceptance Criteria:**
- v23/v24 섹션에 "부분 구현" 명시
- 미구현 기능 목록 각각 존재
- 완료 내역 bullet point 수 변화 없음

## 커밋 전략 (Commit Strategy)

```
docs(workflow): 정밀 검토 수정 — 구 에이전트명 정정 및 MEMORY 상태 업데이트

- SKILL.md L244: gap-detector/code-analyzer → code-reviewer
- REFERENCE.md: 구 에이전트명 패턴 6곳 교체 (gap-detector, code-analyzer, Skill(ultraqa))
- MEMORY.md: v23/v24 부분 구현 상태 명시, 에이전트 수 41→42 수정
```
