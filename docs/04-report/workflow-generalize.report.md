# workflow-generalize PDCA 완료 보고서

**작성일**: 2026-03-02
**작업**: `/auto` PDCA 워크플로우 범용화 리팩토링
**복잡도**: STANDARD (2/5)
**모드**: --skip-prd, --no-issue, --skip-e2e

---

## 1. 배경 및 목적

### 1.1 배경

`/auto` PDCA 워크플로우는 SKILL.md와 REFERENCE.md를 중심으로 Phase 0-5 전체 사이클을 제어한다. 워크플로우 분석 결과, 전체 구성의 약 85%는 범용 구조이나 나머지 15%에 도메인 특화 요소가 혼재되어 있었다.

| 구성 비율 | 분류 | 예시 |
|-----------|------|------|
| ~85% | 범용 | PDCA 사이클, Agent Teams 패턴, 복잡도 판단 |
| ~10% | 도메인 특화 | Step 3.0 옵션 (`--mockup`, `--daily`, `--gdocs`) |
| ~3% | 프레임워크 종속 | Playwright 전용 E2E, Vercel BP 인라인 규칙 |
| ~2% | 레거시 잔재 | `.omc/` 경로 참조 |

이 혼재 구조는 워크플로우의 재사용성을 저해하고, 새로운 도메인이나 프레임워크를 추가할 때 SKILL.md/REFERENCE.md 본문을 직접 수정해야 하는 결합도 문제를 야기했다.

### 1.2 목적

- 도메인 특화 상세를 외부 파일로 추출하여 SKILL.md/REFERENCE.md 본문을 범용 구조로 유지한다.
- 프레임워크 종속 코드를 추상화하여 다중 프레임워크를 지원한다.
- 레거시 경로(`.omc/`)를 현행 구조(`.claude/`)로 정리한다.
- 자동 로드 규칙 중 `/auto` 전용 규칙을 스킬 가이드라인으로 이동한다.

---

## 2. 구현 범위 및 변경 내역

### 2.1 변경 요약

6개 커밋으로 구성된 리팩토링을 수행했다.

```
Task 1: .omc/ 레거시 경로 정리         → 7d9d473
Task 2: Vercel BP 규칙 추출            → 9d6e854
Task 3: --mockup 상세 이동             → cb6fc77
Task 4: E2E 프레임워크 추상화          → d02c8f3
Task 5: Rule 10 이미지 분석 이동       → b235f38
Task 6: 교차 참조 정합성 검증          → c644cb8
```

### 2.2 변경 상세

#### Task 1: `.omc/` 레거시 경로 정리

**커밋**: `7d9d473`

| 항목 | 내용 |
|------|------|
| 대상 파일 | REFERENCE.md |
| 변경 내용 | `.omc/slack-context/`, `.omc/gmail-context/` → `.claude/context/slack/`, `.claude/context/gmail/` |
| 신규 파일 | `.claude/context/slack/.gitkeep`, `.claude/context/gmail/.gitkeep` |

OMC 플러그인 제거(2026-02-18) 이후 잔존하던 `.omc/` 경로 참조를 현행 `.claude/` 구조로 이전했다.

---

#### Task 2: Vercel BP 규칙 추출

**커밋**: `9d6e854`

| 항목 | 내용 |
|------|------|
| 대상 파일 | REFERENCE.md |
| 변경 내용 | 47개 Vercel BP 규칙을 `.claude/references/vercel-bp-rules.md`로 추출 |
| 원본 변화 | 36줄 인라인 → 8줄 참조 포인터 |

REFERENCE.md 본문에 인라인으로 존재하던 Vercel Best Practices 규칙 47개를 별도 참조 파일로 분리했다. 원본 위치에는 참조 포인터만 남겨 REFERENCE.md의 범용성을 유지한다.

---

#### Task 3: `--mockup` 상세 이동

**커밋**: `cb6fc77`

| 항목 | 내용 |
|------|------|
| 대상 파일 | SKILL.md |
| 이동 대상 | 55줄 `--mockup` 상세 |
| 이동 위치 | mockup-hybrid SKILL.md `/auto 연동` 섹션 |
| 원본 변화 | 55줄 상세 → 6줄 라우팅 포인터 |

`--mockup` 옵션의 상세 실행 절차(designer 에이전트 호출, PNG 캡처, 문서 삽입)를 mockup-hybrid 스킬의 SKILL.md로 이동했다. SKILL.md 본문에는 라우팅 포인터만 남긴다.

---

#### Task 4: E2E 프레임워크 추상화

**커밋**: `d02c8f3`

| 항목 | 내용 |
|------|------|
| 대상 파일 | SKILL.md (Step 4.2.0), REFERENCE.md (E2E runner prompt, description) |
| 변경 내용 | Playwright 전용 → Playwright/Cypress/Vitest 3-framework 자동 감지 |

E2E 테스트 실행이 Playwright에 하드코딩되어 있던 것을 3개 프레임워크 자동 감지 구조로 추상화했다. 프로젝트 루트의 설정 파일(`playwright.config.*`, `cypress.config.*`, `vitest.config.*`)을 탐지하여 적절한 프레임워크를 선택한다.

---

#### Task 5: Rule 10 이미지 분석 이동

**커밋**: `b235f38`

| 항목 | 내용 |
|------|------|
| 원본 | `.claude/rules/10-image-analysis.md` |
| 이동 위치 | `.claude/skills/auto/guidelines/image-analysis.md` |
| 효과 | 모든 세션 자동 로드 → `/auto` 실행 시만 참조 |

`.claude/rules/` 디렉토리의 파일은 모든 Claude Code 세션에서 자동 로드된다. 이미지 분석 규칙은 `/auto` 워크플로우 전용이므로, 스킬 가이드라인으로 이동하여 불필요한 컨텍스트 소비를 제거했다.

---

#### Task 6: 교차 참조 정합성 검증

**커밋**: `c644cb8`

| 항목 | 내용 |
|------|------|
| 대상 파일 | daily SKILL.md |
| 변경 내용 | `.omc/` 잔재 추가 수정 |
| 검증 방법 | 6개 grep 패턴 전수 검증 |

Task 1-5 이후 전체 코드베이스에 대해 6개 패턴으로 교차 참조 정합성을 검증했다. daily SKILL.md에서 추가 `.omc/` 잔재를 발견하여 수정했다.

---

## 3. 검증 결과

### 3.1 Phase 3.2 Architect Gate

| 검증 항목 | 결과 |
|-----------|------|
| Task 1-5 구현 완료 여부 | PASS |
| 참조 포인터 정합성 | PASS |
| 기존 기능 영향 없음 | PASS |

**판정**: APPROVE

### 3.2 Phase 4.1 QA Runner

| 검증 항목 | 결과 |
|-----------|------|
| `.omc/` 경로 잔재 검증 (SKILL+REF) | QA_PASSED |
| Vercel BP 참조 포인터 동작 | QA_PASSED |
| `--mockup` 라우팅 포인터 동작 | QA_PASSED |
| E2E 프레임워크 감지 로직 | QA_PASSED |
| Rule 10 이동 후 가이드라인 참조 | QA_PASSED |
| 교차 참조 정합성 (6종 grep) | QA_PASSED |

**판정**: 전항목 QA_PASSED

### 3.3 Phase 4.2 Architect Verification + Code Review

| 검증 단계 | 결과 |
|-----------|------|
| Architect Verification | APPROVE |
| Code Review | APPROVE |

---

## 4. 핵심 지표

| 항목 | Before | After | 변화 |
|------|--------|-------|------|
| SKILL.md 도메인 특화 줄 수 | ~55줄 (`--mockup`) | 6줄 (라우팅 포인터) | -89% |
| REFERENCE.md Vercel BP | 36줄 (인라인) | 8줄 (참조 포인터) | -78% |
| E2E 지원 프레임워크 | 1종 (Playwright) | 3종 (Playwright/Cypress/Vitest) | +200% |
| 자동 로드 규칙 수 | 6개 | 5개 | -1 (Rule 10 이동) |
| `.omc/` 경로 (SKILL+REF) | 2건 | 0건 | -100% |

---

## 5. PDCA 사이클 요약

| Phase | 수행 내용 | 결과 |
|-------|-----------|------|
| Phase 0 | TeamCreate, 요청 분석, --skip-prd 적용 | 완료 |
| Phase 1 | STANDARD 계획 수립, 6개 Task 분해 | 완료 |
| Phase 2 | STANDARD 설계 (추출/이동/추상화 전략) | 완료 |
| Phase 3 | 6개 Task 순차 구현 (6개 커밋) | 완료 |
| Phase 3.2 | Architect Gate | APPROVE |
| Phase 4.1 | QA Runner (6종 검증) | QA_PASSED |
| Phase 4.2 | Architect Verification + Code Review | APPROVE |
| Phase 5 | 완료 보고서 생성 (이 문서) | 완료 |

---

## 6. 범위 외 잔존 이슈

| 이슈 | 상태 | 비고 |
|------|------|------|
| `.omc/` 참조 (hooks/, agents/, commands/) | 미정리 | 별도 정리 작업 대상 |
| `omc_update_detector.py` hook | 무용 상태 | OMC 플러그인 제거 후 동작 불필요, 삭제 검토 대상 |

---

## 7. 결론

`/auto` PDCA 워크플로우의 도메인 특화 요소를 범용 구조로 리팩토링했다. 6개 Task를 통해 다음 성과를 달성했다.

- **레거시 정리**: `.omc/` 경로를 `.claude/` 구조로 이전하여 현행 아키텍처와 정합성 확보
- **관심사 분리**: Vercel BP 규칙(47개)과 `--mockup` 상세(55줄)를 외부 파일로 추출하여 SKILL.md/REFERENCE.md 본문의 범용성 유지
- **프레임워크 추상화**: E2E 테스트 실행을 Playwright 전용에서 3-framework 자동 감지로 확장
- **컨텍스트 최적화**: Rule 10 이미지 분석 규칙을 스킬 가이드라인으로 이동하여 비관련 세션의 자동 로드 제거

SKILL.md/REFERENCE.md 본문은 PDCA 사이클 제어에 집중하고, 도메인 상세는 외부 참조로 분리되어 새로운 도메인이나 프레임워크 추가 시 본문 수정 없이 확장 가능한 구조가 되었다.

---

## 참조 문서

| 문서 | 경로 |
|------|------|
| SKILL.md | `C:\claude\.claude\skills\auto\SKILL.md` |
| REFERENCE.md | `C:\claude\.claude\skills\auto\REFERENCE.md` |
| Vercel BP 규칙 (추출) | `C:\claude\.claude\references\vercel-bp-rules.md` |
| 이미지 분석 가이드라인 (이동) | `C:\claude\.claude\skills\auto\guidelines\image-analysis.md` |

---

*보고서 종료 -- workflow-generalize PDCA 완료 | 작성: writer 에이전트 | 2026-03-02*