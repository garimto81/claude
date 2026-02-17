# /auto + /work 통합 계획

**Version**: 1.0.0 | **Date**: 2026-02-15 | **Status**: DRAFT

---

## 1. 배경

### 왜 통합하는가

현재 `/work`와 `/auto`는 "작업 실행"이라는 동일한 목적을 가지면서 서로 다른 Phase 구조를 유지하고 있어 3가지 문제가 발생한다:

| 문제 | 상세 | 영향 |
|------|------|------|
| **사용자 혼란** | "이 작업에 `/work`를 쓸지 `/auto`를 쓸지?" 판단 필요 | 진입 장벽 |
| **코드 중복** | 분석/테스트/검증 로직이 양쪽에 존재 (SKILL.md + command.md 합계 500줄+) | 유지보수 부담 |
| **기능 분산** | `/work`의 이슈 연동/E2E는 `/auto`에 없고, `/auto`의 PDCA/Ralph는 `/work`에 없음 | 불완전한 워크플로우 |

### 통합 방향

`/auto`를 유일한 실행 커맨드로 만들되, `/work`의 고유 가치(병렬 분석, 이슈 연동, E2E, TDD 보고)를 `/auto` Phase 구조 안에 자연스럽게 녹인다. `/work`는 `/auto`로 리다이렉트하는 stub으로 전환한다.

### 핵심 원칙

1. `/auto` Phase 1-5 PDCA 구조는 유지
2. 복잡도 기반 경량/중량 분기 도입 (간단 작업에 Opus 남용 방지)
3. 기존 인과관계 그래프 보존
4. 하위 호환성 유지 (`/work "작업"` 입력은 계속 동작)

---

## 2. 구현 범위

### 2.1 /work 고유 기능 → /auto Phase 매핑

| /work 고유 기능 | 흡수 위치 | 통합 방식 |
|----------------|----------|----------|
| **병렬 분석** (문서 + 이슈) | Phase 1 PLAN Step 1.0 (신규) | 복잡도 판단 전 사전 분석 단계로 추가 |
| **이슈 생성/연동** | Phase 1 PLAN Step 1.3 (신규) | Plan 산출물 생성 후 이슈 자동 생성/연결 |
| **E2E 검증** (Playwright + /debug) | Phase 4 CHECK Step 4.3 (신규) | UltraQA 후 E2E 검증 단계 추가 |
| **TDD 보고** (커버리지) | Phase 4 CHECK Step 4.1 확장 | UltraQA 사이클에 커버리지 기준 추가 |
| **최종 보고서** | Phase 5 ACT | 기존 report-generator 산출물 확장 |
| **옵션** (--skip-analysis, --no-issue, --strict, --dry-run) | /auto 옵션 통합 | /auto 옵션 테이블에 추가 |

### 2.2 복잡도 기반 경량/중량 분기 (신규)

현재 복잡도 점수(0-5)를 활용하여 Phase 실행 깊이를 분기한다:

| 복잡도 | 모드 | Phase 실행 |
|:------:|------|-----------|
| **0-1** | LIGHT | Phase 1 (Planner haiku) → Phase 3 (executor sonnet) → Phase 4 (UltraQA only) → Phase 5 (보고) |
| **2-3** | STANDARD | Phase 1 (Planner sonnet) → Phase 2 (Architect sonnet) → Phase 3 (Ralph) → Phase 4 (UltraQA + Architect) → Phase 5 |
| **4-5** | HEAVY | Phase 1 (Ralplan opus) → Phase 2 (Architect opus) → Phase 3 (Ralph + 병렬) → Phase 4 (UltraQA + 이중검증) → Phase 5 |

**LIGHT 모드 절감 효과**: Opus 호출 0회, Design Phase 스킵, 이중검증 스킵 → 토큰 60%+ 절감

### 2.3 통합 후 /auto Phase 1-5 설계

#### Phase 1: PLAN (확장)

```
Step 1.0: 사전 분석 [NEW] (--skip-analysis로 스킵 가능)
  ├── [Agent 1] 문서 분석 (Explore, haiku) - PRD, CLAUDE.md, docs/ 병렬 탐색
  └── [Agent 2] 이슈 분석 (Explore, haiku) - gh issue list, gh pr list 병렬 탐색

Step 1.1: 복잡도 판단 (5점 만점) [기존 유지]
  → 판단 로그 출력

Step 1.2: 계획 수립 [기존 유지]
  ├── LIGHT (0-1): Task(planner, haiku) - 간단 계획
  ├── STANDARD (2-3): Task(planner, sonnet) - 표준 계획
  └── HEAVY (4-5): Skill(ralplan, opus) - 정밀 계획

Step 1.3: 이슈 연동 [NEW] (--no-issue로 스킵 가능)
  ├── 관련 이슈 없음 → 새 이슈 생성
  ├── 관련 이슈 있음 (Open) → 기존 이슈에 코멘트
  └── 관련 이슈 있음 (Closed) → 새 이슈 생성 + 참조
```

**산출물**: `docs/01-plan/{feature}.plan.md`, GitHub Issue (선택)

#### Phase 2: DESIGN (경량 분기 추가)

```
LIGHT 모드: Phase 2 스킵 (Phase 3 직행)
STANDARD 모드: Task(architect, sonnet) - 표준 설계
HEAVY 모드: Task(architect, opus) - 정밀 설계 [기존 유지]
```

**산출물**: `docs/02-design/{feature}.design.md` (STANDARD/HEAVY만)

#### Phase 3: DO (기존 유지)

```
LIGHT 모드: Task(executor, sonnet) - 단일 실행 (Ralph 없음)
STANDARD/HEAVY 모드: Skill(ralph) - Ralph 루프 [기존 유지]
```

#### Phase 4: CHECK (E2E 추가)

```
Step 4.1: UltraQA 사이클 [기존 유지, 커버리지 기준 추가]
  └── 신규 코드 커버리지 80% 미달 시 FAIL 처리

Step 4.2: 이중 검증 [STANDARD/HEAVY만]
  ├── Architect 검증
  └── gap-detector 검증

Step 4.3: E2E 검증 [NEW] (Playwright 프로젝트에만 적용)
  ├── Playwright 테스트 실행
  ├── 실패 시 /debug 자동 트리거 (가설-검증 사이클)
  ├── --strict: 1회 실패 시 중단
  └── 3회 가설 기각 → /issue failed

Step 4.4: TDD 커버리지 보고 [NEW]
  └── pytest --cov / jest --coverage 실행 → 결과 수집
```

#### Phase 5: ACT (보고서 확장)

```
기존 분기 로직 유지 +

보고서 포맷 확장 (report-generator):
  ├── Phase 1 분석 결과 (관련 문서/이슈 수)
  ├── Phase 2 설계 요약
  ├── Phase 3 구현 내역 (파일별 변경량)
  ├── Phase 4 E2E 결과 (통과/실패 수)
  ├── Phase 4 TDD 결과 (커버리지 %)
  ├── 생성된 이슈/PR 링크
  └── 다음 단계 권장
```

---

## 3. 영향 파일

### 3.1 수정 대상 (MUST CHANGE)

| 파일 | 변경 내용 | 크기 |
|------|----------|------|
| `.claude/skills/auto/SKILL.md` | Phase 1 확장 (Step 1.0, 1.3), Phase 4 확장 (Step 4.3, 4.4), 복잡도 분기 테이블, 옵션 추가 | 중 |
| `.claude/skills/auto/REFERENCE.md` | 상세 워크플로우 업데이트 (새 Step 포함), 모델 분기 테이블 추가 | 중 |
| `.claude/commands/auto.md` | 옵션 테이블에 --skip-analysis, --no-issue, --strict, --dry-run 추가 | 소 |
| `.claude/commands/work.md` | stub으로 전환 (모든 로직 제거, `/auto`로 리다이렉트 안내) | 소 |
| `.claude/skills/work/SKILL.md` | stub으로 전환 (trigger 유지, `/auto` 위임) | 소 |
| `.claude/references/skill-causality-graph.md` | `/work` 노드 제거, `/auto` Phase 1/4 확장 반영 | 소 |
| `.claude/rules/08-skill-routing.md` | `/work` → `/auto` 리다이렉트 추가 (Deprecated 테이블) | 소 |
| `docs/COMMAND_REFERENCE.md` | `/work` 섹션을 `/auto` 리다이렉트로 변경, `/auto` 섹션 확장 | 중 |
| `CLAUDE.md` | 작업 방법 섹션에서 `/work` → `/auto` 변경 | 소 |

### 3.2 확인 대상 (MAY NEED CHANGE)

| 파일 | 확인 사항 |
|------|----------|
| `.claude/commands/check.md` | `/work` 참조 여부 확인 |
| `.claude/commands/debug.md` | `/work` E2E 실패 자동 트리거 경로 변경 |
| `.claude/skills/debug/SKILL.md` | `/work` 참조를 `/auto`로 변경 |
| `.claude/test-cases.json` | `/work` 테스트 케이스 업데이트 |
| `~/.claude/CLAUDE.md` | `/work` 패턴 매칭 규칙 확인 |

### 3.3 생성 대상 (NEW FILES)

없음. 기존 파일 수정만으로 충분.

---

## 4. 위험 요소

### 4.1 High Risk

| 위험 | 영향 | 완화 방안 |
|------|------|----------|
| **인과관계 그래프 파괴** | `/auto` PDCA 시스템 전체 작동 불가 | 변경 전후 causality graph diff 비교 필수. `/work` 제거가 아닌 리다이렉트 방식 |
| **기존 `/work` 사용자 습관 파괴** | 사용자가 `/work "작업"`을 입력했는데 동작 안 함 | `/work`를 stub으로 유지하고 `/auto`로 자동 전달 |
| **LIGHT 모드에서 품질 저하** | 복잡도 오판 시 Opus 없이 어려운 작업 실행 | LIGHT→STANDARD 자동 승격 조건 추가 (빌드 실패 2회 이상 시) |

### 4.2 Medium Risk

| 위험 | 영향 | 완화 방안 |
|------|------|----------|
| **E2E 단계 추가로 /auto 실행 시간 증가** | Playwright가 없는 프로젝트에서 불필요한 지연 | Playwright 설정 파일 존재 여부로 자동 감지. 없으면 Step 4.3 스킵 |
| **옵션 충돌** | `--skip-analysis`와 `--interactive` 조합 등 | 옵션 호환성 매트릭스 정의 |
| **SKILL.md 크기 증가** | 현재 145줄에서 200줄+ 예상 → 토큰 증가 | 상세 로직은 REFERENCE.md로 분리 (SKILL.md는 테이블 중심 유지) |

### 4.3 Low Risk

| 위험 | 영향 | 완화 방안 |
|------|------|----------|
| **문서 동기화 누락** | COMMAND_REFERENCE.md와 실제 동작 불일치 | /audit로 사후 검증 |
| **레거시 키워드 충돌** | `work: 작업` 키워드가 남아있을 가능성 | keyword-detector.mjs 확인 |

---

## 5. 통합 설계

### 5.1 통합 후 전체 흐름도

```
/auto "작업" (또는 /work "작업" → /auto 리다이렉트)
  │
  ├── [Step 0] 옵션 파싱 + 모드 결정
  │     ├── --dry-run → 판단만 출력, 실행 안함
  │     └── --eco → 토큰 절약 모드 (Haiku 우선)
  │
  ├── Phase 1: PLAN ────────────────────────────────────────
  │     │
  │     ├── Step 1.0: 사전 분석 [NEW] (--skip-analysis 시 스킵)
  │     │     ├── [Agent 1] Explore(haiku): 문서 분석
  │     │     └── [Agent 2] Explore(haiku): 이슈 분석   ← 병렬
  │     │
  │     ├── Step 1.1: 복잡도 판단 (5점 만점)
  │     │     └── 분석 결과를 복잡도 판단에 활용
  │     │
  │     ├── Step 1.2: 계획 수립
  │     │     ├── LIGHT (0-1): Task(planner, haiku)
  │     │     ├── STANDARD (2-3): Task(planner, sonnet)
  │     │     └── HEAVY (4-5): Skill(ralplan)
  │     │
  │     └── Step 1.3: 이슈 연동 [NEW] (--no-issue 시 스킵)
  │           └── gh issue create / comment
  │
  ├── Phase 2: DESIGN ──────────────────────────────────────
  │     ├── LIGHT: 스킵 (Phase 3 직행)
  │     ├── STANDARD: Task(architect, sonnet)
  │     └── HEAVY: Task(architect, opus)
  │
  ├── Phase 3: DO ──────────────────────────────────────────
  │     ├── [Step 3.0] 옵션 처리 (--gdocs, --mockup 등)
  │     ├── LIGHT: Task(executor, sonnet) - 단일 실행
  │     └── STANDARD/HEAVY: Skill(ralph) - Ralph 루프
  │
  ├── Phase 4: CHECK ───────────────────────────────────────
  │     │
  │     ├── Step 4.1: UltraQA 사이클 (Build→Lint→Test→Fix)
  │     │     └── [확장] 커버리지 80% 미달 시 FAIL
  │     │
  │     ├── Step 4.2: 이중 검증 (STANDARD/HEAVY만)
  │     │     ├── Architect 검증
  │     │     └── gap-detector 검증
  │     │
  │     ├── Step 4.3: E2E 검증 [NEW] (Playwright 존재 시만)
  │     │     ├── npx playwright test
  │     │     ├── 실패 → /debug (가설-검증)
  │     │     └── --strict → 1회 실패 시 중단
  │     │
  │     └── Step 4.4: TDD 보고 [NEW]
  │           └── 커버리지 수치 수집
  │
  └── Phase 5: ACT ────────────────────────────────────────
        ├── gap < 90% → pdca-iterator (최대 5회)
        ├── gap >= 90% + APPROVE → report-generator [보고서 확장]
        └── Architect REJECT → executor → Phase 4 재실행
```

### 5.2 복잡도 분기 상세

```
복잡도 점수 판단 (5점 만점)
  │
  ├── 0-1점 (LIGHT) ──── 간단한 수정, 단일 파일
  │     ├── Phase 1: haiku 분석 + haiku 계획
  │     ├── Phase 2: 스킵
  │     ├── Phase 3: sonnet executor (Ralph 없음)
  │     ├── Phase 4: UltraQA only (이중검증 스킵)
  │     └── Phase 5: haiku 보고서
  │     └── 예상 토큰: ~5,000t (기존 대비 60% 절감)
  │
  ├── 2-3점 (STANDARD) ── 보통 기능, 다중 파일
  │     ├── Phase 1: haiku 분석 + sonnet 계획
  │     ├── Phase 2: sonnet 설계
  │     ├── Phase 3: Ralph 루프 (sonnet executor)
  │     ├── Phase 4: UltraQA + Architect(sonnet) 검증
  │     └── Phase 5: sonnet 보고서
  │     └── 예상 토큰: ~12,000t (기존 대비 30% 절감)
  │
  └── 4-5점 (HEAVY) ──── 복잡한 아키텍처 변경
        ├── Phase 1: haiku 분석 + Ralplan(opus)
        ├── Phase 2: opus 설계
        ├── Phase 3: Ralph 루프 (병렬 + opus 검증)
        ├── Phase 4: UltraQA + 이중검증(opus)
        └── Phase 5: 완전 보고서
        └── 예상 토큰: ~20,000t (기존과 동일)
```

### 5.3 자동 승격 규칙

LIGHT 모드에서 다음 조건 발생 시 STANDARD로 자동 승격:

| 조건 | 트리거 시점 |
|------|-----------|
| Phase 3 빌드 실패 2회 이상 | DO 중 |
| Phase 4 UltraQA 3사이클 초과 | CHECK 중 |
| 예상보다 영향 파일 5개 이상 | PLAN 완료 후 |

승격 시 Phase 2 (DESIGN)부터 재실행.

### 5.4 /work stub 설계

```markdown
# /work → /auto 리다이렉트

> `/work`는 `/auto`로 통합되었습니다 (v19.0).

| 기존 명령 | 신규 명령 |
|----------|----------|
| `/work "작업"` | `/auto "작업"` |
| `/work --auto "작업"` | `/auto "작업"` |
| `/work --skip-analysis` | `/auto --skip-analysis` |
| `/work --no-issue` | `/auto --no-issue` |
| `/work --strict` | `/auto --strict` |
| `/work --dry-run` | `/auto --dry-run` |
| `/work --loop` | `/auto` (기존 리다이렉트 유지) |
```

### 5.5 옵션 호환성 매트릭스

| 옵션 | LIGHT | STANDARD | HEAVY | 비고 |
|------|:-----:|:--------:|:-----:|------|
| `--skip-analysis` | O | O | O | Step 1.0 스킵 |
| `--no-issue` | O | O | O | Step 1.3 스킵 |
| `--strict` | O | O | O | E2E 1회 실패 시 중단 |
| `--dry-run` | O | O | O | 실행 안함 |
| `--eco` | 강제 LIGHT | O | O | 복잡도와 무관하게 LIGHT 강제 |
| `--interactive` | O | O | O | Phase 전환 시 확인 |
| `--gdocs` | O | O | O | Phase 3 전처리 |
| `--mockup` | O | O | O | Phase 3 전처리 |

---

## 6. Task 분해

### Task 1: /auto SKILL.md Phase 1 확장
- Step 1.0 (사전 분석) 추가
- Step 1.3 (이슈 연동) 추가
- 복잡도 분기 테이블 (LIGHT/STANDARD/HEAVY) 추가
- 모델 라우팅 테이블 업데이트
- **파일**: `.claude/skills/auto/SKILL.md`
- **검증**: SKILL.md 파싱 오류 없음, 기존 Phase 2-5 변경 없음

### Task 2: /auto SKILL.md Phase 4 확장
- Step 4.3 (E2E 검증) 추가
- Step 4.4 (TDD 보고) 추가
- UltraQA 커버리지 기준 추가
- **파일**: `.claude/skills/auto/SKILL.md`
- **검증**: Phase 4 기존 Step 4.1, 4.2 변경 없음
- **의존**: Task 1 완료 후 (같은 파일 수정)

### Task 3: /auto REFERENCE.md 상세 워크플로우 업데이트
- 새 Step들의 상세 워크플로우 추가
- 복잡도 분기 상세 설명
- 자동 승격 규칙 문서화
- **파일**: `.claude/skills/auto/REFERENCE.md`
- **검증**: SKILL.md와 일관성 확인

### Task 4: /auto 커맨드 파일 옵션 추가
- --skip-analysis, --no-issue, --strict, --dry-run 옵션 추가
- 옵션 호환성 매트릭스 추가
- **파일**: `.claude/commands/auto.md`
- **검증**: 기존 옵션과 충돌 없음

### Task 5: /work stub 전환
- `.claude/commands/work.md` → stub (리다이렉트 안내)
- `.claude/skills/work/SKILL.md` → stub (trigger 유지, /auto 위임)
- **파일**: `.claude/commands/work.md`, `.claude/skills/work/SKILL.md`
- **검증**: `/work` 입력 시 `/auto`로 안내되는지 확인

### Task 6: 참조 문서 업데이트
- `skill-causality-graph.md` 업데이트
- `08-skill-routing.md`에 `/work` deprecated 추가
- `COMMAND_REFERENCE.md` `/work` 섹션 변경
- `CLAUDE.md` 작업 방법 섹션 변경
- **파일**: 4개 파일
- **검증**: `/work` 참조 → `/auto` 리다이렉트 안내로 통일

### Task 7: 교차 참조 정리
- `/debug` SKILL.md의 `/work` 참조를 `/auto`로 변경
- `.claude/test-cases.json`의 `/work` 케이스 업데이트
- 기타 `/work` 참조 파일 확인 및 정리
- **파일**: Grep 결과 기반 (약 10개 파일)
- **검증**: `grep -r "/work" .claude/` 결과 stub 이외에 남은 참조 없음

---

## 7. Commit 전략

| 순서 | Commit | 포함 Task | 내용 |
|:----:|--------|:---------:|------|
| 1 | `feat(auto): Phase 1 확장 - 사전 분석 + 이슈 연동 + 복잡도 분기` | Task 1 | SKILL.md Phase 1 변경 |
| 2 | `feat(auto): Phase 4 확장 - E2E 검증 + TDD 보고` | Task 2 | SKILL.md Phase 4 변경 |
| 3 | `docs(auto): REFERENCE.md 상세 워크플로우 업데이트` | Task 3 | REFERENCE.md |
| 4 | `feat(auto): --skip-analysis, --no-issue, --strict, --dry-run 옵션 추가` | Task 4 | auto.md 커맨드 |
| 5 | `refactor(work): /work → /auto 리다이렉트 stub 전환` | Task 5 | work.md, work/SKILL.md |
| 6 | `docs: /work → /auto 통합 참조 문서 업데이트` | Task 6, 7 | 참조 문서 일괄 |

---

## 8. 성공 기준

| 기준 | 측정 방법 |
|------|----------|
| `/work "작업"` 입력 시 `/auto` 안내 | stub 파일에 리다이렉트 안내 존재 |
| `/auto` Phase 1에 사전 분석 + 이슈 연동 포함 | SKILL.md Step 1.0, 1.3 존재 |
| `/auto` Phase 4에 E2E + TDD 보고 포함 | SKILL.md Step 4.3, 4.4 존재 |
| 복잡도 0-1 LIGHT 모드에서 Opus 호출 0회 | 모델 라우팅 테이블 확인 |
| 인과관계 그래프 보존 | causality graph 변경 전후 diff에서 PDCA 체인 무결 |
| `/work` 참조 잔여 0건 | `grep -r "/work" .claude/` 결과 stub 이외 없음 |
| SKILL.md 크기 200줄 이내 유지 | 상세 로직은 REFERENCE.md로 분리 |
