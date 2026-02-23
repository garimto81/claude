# PRD: Opus 4.6 모델 라우팅 도입

**버전**: 1.0.0 | **작성일**: 2026-02-23 | **작성자**: Claude

---

## 1. 배경 및 목적

### 1.1 배경

현재 `/auto` PDCA 워크플로우는 v23.0 이후 모든 에이전트에 sonnet 모델을 사용한다. opus는 `--opus` 플래그 입력 시에만 활성화되며, 기본 워크플로우에서는 완전히 제거된 상태다.

그러나 Sonnet 4.6은 일반 실행 작업에서 Opus-level 성능을 보이지만, **검증·계획 수립·아키텍처 진단** 등 고신뢰도가 요구되는 판단 단계에서는 Opus 4.6의 추론 깊이가 실질적인 품질 차이를 만든다. 특히 STANDARD/HEAVY 복잡도 작업에서 Planner와 Architect Gate가 Sonnet을 사용할 경우, 계획의 누락과 검증의 허점이 발생할 수 있다.

### 1.2 목적

- STANDARD 이상의 복잡도에서 **계획 수립 및 검증 단계**에 Opus 4.6을 선택적으로 적용한다.
- 비용 증가(+40~60%)를 최소화하면서 고신뢰도 판단이 필요한 4개 단계에만 opus를 제한한다.
- Smart Model Routing 정책을 업데이트하여 모델 티어 구분을 명확히 한다.

---

## 2. 요구사항 목록

### 기능 요구사항

**R1. STANDARD/HEAVY Planner — Opus 적용**
- 대상: Phase 1 계획 수립 (Planner 에이전트)
- 조건: 복잡도 점수 STANDARD(4-7) 이상
- LIGHT(0-3)는 Sonnet 유지

**R2. STANDARD/HEAVY Architect Gate — Opus 적용**
- 대상: Phase 3.2 Architect 검증 게이트
- 조건: STANDARD 이상 복잡도 작업
- LIGHT는 Sonnet 유지

**R3. Root Cause 진단 — Opus 적용**
- 대상: Phase 4.1 Architect 진단 (버그/실패 원인 분석)
- 조건: 복잡도 무관하게 항상 적용 (진단의 정확도 우선)

**R4. 검증 단계 Architect — Opus 적용**
- 대상: Phase 4.2 Architect 최종 검증
- 조건: STANDARD 이상 복잡도 작업

**R5. LIGHT 모드 — 변경 없음**
- LIGHT(복잡도 0-3) 전체 단계는 Sonnet 유지
- `--eco` 플래그 시 전체 Sonnet 강제 (현행 유지)

**R6. --opus 플래그 — 전체 Opus 오버라이드 유지**
- 기존 `--opus` 플래그 동작 유지 (모든 단계 opus 강제)

### 비기능 요구사항

**NR1. 비용 예측 가시성**
- Phase 0 옵션 파싱 시 opus 사용 단계 수를 출력하여 사용자가 비용을 예측할 수 있어야 한다.

**NR2. 하위 호환성**
- 기존 `--eco`, `--opus` 플래그의 동작을 변경하지 않는다.
- LIGHT 모드 사용자는 이번 변경의 영향을 받지 않는다.

**NR3. 문서 일관성**
- 수정되는 4개 파일의 모델 정책이 서로 일치해야 한다.

---

## 3. 수정 범위

### 3.1 수정 대상 파일

| 번호 | 파일 | 수정 내용 |
|------|------|-----------|
| F1 | `C:\Users\AidenKim\.claude\CLAUDE.md` | Smart Model Routing 테이블 — opus 행 조건 변경 |
| F2 | `C:\Users\AidenKim\.claude\OMC_REFERENCE.md` | Agent Tier Table — Planner/Architect 티어 업데이트 |
| F3 | `C:\claude\.claude\skills\auto\SKILL.md` | Phase 1, 3.2, 4.1, 4.2의 model 파라미터 수정 |
| F4 | `C:\claude\.claude\skills\auto\REFERENCE.md` | 모델 오버라이드 섹션 — opus 조건부 적용 규칙 추가 |

### 3.2 변경 모델 라우팅 요약

```
현재:
  Planner (ALL)     → sonnet
  Architect (ALL)   → sonnet
  Executor (ALL)    → sonnet

변경 후:
  Planner (LIGHT)   → sonnet
  Planner (STANDARD/HEAVY) → opus
  Architect Gate (LIGHT)   → sonnet
  Architect Gate (STANDARD/HEAVY) → opus
  Root Cause 진단 (ALL)    → opus
  Architect 최종 검증 (STANDARD/HEAVY) → opus
  Executor (ALL)    → sonnet (변경 없음)
```

---

## 4. 제약사항

| 제약 | 내용 |
|------|------|
| API 가용성 | Opus 4.6 (`claude-opus-4-6`) API 접근 가능 상태 전제 |
| 비용 한도 | 기본 대비 +40~60% 허용 범위 내 (Heavy 작업 기준 최대 +60%) |
| 모델 ID | `claude-opus-4-6` 사용 (최신 Claude 4.6 패밀리) |
| 플래그 충돌 | `--eco` 플래그 사용 시 opus 적용 단계도 sonnet으로 강제 |

---

## 5. 우선순위

| 우선순위 | 항목 | 이유 |
|----------|------|------|
| P0 | R3 Root Cause 진단 Opus 적용 | 버그 재현 실패 방지에 직결 |
| P0 | R1 STANDARD/HEAVY Planner Opus 적용 | 계획 품질이 전체 작업 결과 결정 |
| P1 | R2 STANDARD/HEAVY Architect Gate Opus 적용 | 잘못된 구현 통과 방지 |
| P1 | R4 검증 단계 Architect Opus 적용 | 최종 품질 게이트 강화 |
| P2 | NR1 비용 예측 가시성 | UX 개선, 기능에 비필수 |

---

## 6. 영향 분석

### 6.1 예상 비용 증가

| 복잡도 | 현재 | 변경 후 | 증가율 |
|--------|------|---------|--------|
| LIGHT | sonnet | sonnet | 0% |
| STANDARD | sonnet (전체) | sonnet + opus (2~4단계) | +40% |
| HEAVY | sonnet (전체) | sonnet + opus (4단계) | +60% |

### 6.2 품질 개선 기대 효과

- Planner opus 전환: 계획 누락 항목 감소, 태스크 분해 정밀도 향상
- Architect Gate opus 전환: 잘못된 구현 통과율 감소
- Root Cause 진단 opus 전환: 디버깅 1차 시도 성공률 향상

### 6.3 비영향 범위

- Executor 에이전트 전체 (sonnet 유지)
- LIGHT 모드 전체 워크플로우
- `--eco` 플래그 동작
- `--opus` 플래그 동작

---

## 7. 구현 검증 기준

| 검증 항목 | 기준 |
|-----------|------|
| F1~F4 파일 수정 완료 | 4개 파일 모두 수정됨 |
| STANDARD 작업 실행 시 opus 호출 확인 | Planner/Architect에 `model=opus` 전달 |
| LIGHT 작업 실행 시 sonnet 유지 확인 | 모든 단계 sonnet |
| `--eco` 플래그 동작 유지 | opus 단계도 sonnet으로 강제됨 |
| `--opus` 플래그 동작 유지 | 전체 단계 opus 강제됨 |
