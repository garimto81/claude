# opus-routing PDCA 완료 보고서

**작성일**: 2026-02-23
**작업 브랜치**: feat/prd-chunking-strategy
**검증 상태**: Architect APPROVE 완료
**PDCA 버전**: v24.1

---

## 1. 배경 및 목적

### 1.1 배경

v23.0 이후 `/auto` PDCA 워크플로우는 모든 에이전트에 Sonnet 4.6을 기본 모델로 사용했다. `--opus` 플래그를 명시할 때만 Opus가 활성화되며, 기본 워크플로우에서는 Opus 호출이 0회였다.

Sonnet 4.6은 SWE-bench 79.6%, OSWorld 72.5%의 성능으로 일반 실행 작업에서 Opus-level에 근접하지만, **계획 수립·아키텍처 검증·Root Cause 진단** 등 고신뢰도 판단이 요구되는 단계에서 Opus 4.6의 추론 깊이가 실질적인 품질 차이를 만든다. STANDARD/HEAVY 복잡도 작업에서 Planner와 Architect Gate가 Sonnet을 사용할 경우 계획 누락과 검증 허점이 발생할 수 있었다.

### 1.2 목적

- STANDARD(복잡도 2-3) 이상 작업의 **계획 수립 및 검증 단계**에만 Opus 4.6을 선택적으로 적용한다.
- 비용 증가를 최소화하면서 고신뢰도 판단이 필요한 핵심 단계에 opus를 제한한다.
- Smart Model Routing 정책을 v23.0에서 v24.1로 업데이트하여 "실행=Sonnet / 판단=Opus" 분리 원칙을 명확히 한다.

---

## 2. 구현 범위 및 변경 내역

### 2.1 모델 라우팅 정책 변경 요약

```
[이전 — v23.0]
  Planner (ALL)          → sonnet
  Architect Gate (ALL)   → sonnet
  Executor (ALL)         → sonnet

[이후 — v24.1]
  Planner (LIGHT)                    → haiku
  Planner (STANDARD)                 → opus
  Planner (HEAVY Loop)               → opus
  Critic-Lite (STANDARD)             → opus
  Architect/Critic (HEAVY Loop)      → opus
  Architect Gate (LIGHT)             → sonnet
  Architect Gate (STANDARD/HEAVY)    → opus
  Root Cause 진단 (ALL 복잡도)        → opus
  Architect 최종 검증 (STANDARD/HEAVY) → opus
  Executor (ALL)                     → sonnet (변경 없음)
  QA Runner (ALL)                    → sonnet (변경 없음)
```

### 2.2 변경 파일 상세

#### F1. `C:\Users\AidenKim\.claude\CLAUDE.md`

**변경 내용**: Smart Model Routing 테이블 v23.0 → v24.1

| 이전 (v23.0) | 이후 (v24.1) |
|--------------|--------------|
| `Standard + Complex work` 행: sonnet | `Execution & Implementation` 행으로 명칭 변경 |
| `Premium (on-demand)` 행: opus (`--opus` 플래그만) | `Verification & Planning (STANDARD+)` 행 추가: opus (STANDARD/HEAVY architect 검증, planner 계획, root cause 진단) |
| 헤더: `v23.0 — Sonnet 4.6 = Opus-level @ 1/5 cost` | 헤더: `v24.1 — Sonnet 실행 / Opus 판단 분리` |

**수정 위치**: `### Smart Model Routing` 섹션 전체

---

#### F2. `C:\Users\AidenKim\.claude\OMC_REFERENCE.md`

**변경 내용**: 버전 노트 v24.1 반영

- Agent Tier Table의 Planner/Architect 티어 설명 업데이트
- v24.1 정책 노트 추가 (실행=Sonnet / 판단=Opus 분리 원칙)

---

#### F3. `C:\claude\.claude\skills\auto\SKILL.md`

**변경 내용**: Phase 1.2, 3.2, 4.1, 4.2의 `model` 파라미터 수정 — 7곳

| Phase | 단계 | 에이전트 | 이전 | 이후 |
|-------|------|---------|------|------|
| 1.2 | STANDARD Planner | planner | `sonnet` | `opus` |
| 1.2 | STANDARD Critic-Lite | critic | `sonnet` | `opus` |
| 1.2 | HEAVY Loop Planner | planner | `sonnet` | `opus` |
| 1.2 | HEAVY Loop Architect | architect | `sonnet` | `opus` |
| 1.2 | HEAVY Loop Critic | critic | `sonnet` | `opus` |
| 3.2 | Architect Gate | architect | `sonnet` | `opus` |
| 4.1 | Root Cause 진단 | architect (diagnostician) | `sonnet` | `opus` |
| 4.2 | 최종 검증 Architect | architect (verifier) — STANDARD/HEAVY | `sonnet` | `opus` |

**LIGHT 모드 변경 없음**: Step 1.2 LIGHT Planner는 haiku 유지. Step 4.2 LIGHT architect는 sonnet 유지.

---

#### F4. `C:\claude\.claude\skills\auto\REFERENCE.md`

**변경 내용**: 모델 오버라이드 정책문 + 9개 코드 블록 수정

- Phase 1, 3, 4의 모든 관련 `Task()` 호출에서 `model=` 파라미터 업데이트
- 모델 라우팅 정책 섹션에 v24.1 규칙 명시:
  - 실행 단계 (impl-manager, executor, qa-tester): Sonnet 유지
  - 판단 단계 (planner STANDARD+, architect gate, root cause 진단): Opus 적용
  - `--eco` 플래그 시 opus 단계 포함 전체 sonnet 강제
  - `--opus` 플래그 시 전체 단계 opus 강제 (기존 동작 유지)

---

## 3. 검증 결과

### 3.1 Architect APPROVE 확인

| 검증 항목 | 결과 |
|-----------|------|
| F1 CLAUDE.md 수정 완료 | PASS |
| F2 OMC_REFERENCE.md 수정 완료 | PASS |
| F3 SKILL.md 7곳 model 파라미터 수정 | PASS |
| F4 REFERENCE.md 9개 코드 블록 수정 | PASS |
| STANDARD Planner → opus 전달 확인 | PASS |
| STANDARD Architect Gate → opus 전달 확인 | PASS |
| Root Cause 진단 → opus 전달 확인 | PASS |
| LIGHT 모드 전체 sonnet 유지 확인 | PASS |
| `--eco` 플래그 시 opus 단계 sonnet 강제 확인 | PASS |
| `--opus` 플래그 동작 유지 확인 | PASS |
| 4개 파일 간 정책 일관성 확인 | PASS |

**최종 판정**: APPROVE

---

## 4. 예상 효과

### 4.1 품질 향상

| 단계 | 변경 | 기대 효과 |
|------|------|-----------|
| Planner (STANDARD/HEAVY) | sonnet → opus | 계획 누락 항목 감소, 태스크 분해 정밀도 향상 |
| Architect Gate (STANDARD/HEAVY) | sonnet → opus | 잘못된 구현 통과율 감소, 설계 위반 조기 탐지 |
| Root Cause 진단 (전체) | sonnet → opus | 디버깅 1차 시도 성공률 향상, 반복 QA 사이클 감소 |
| 최종 검증 Architect (STANDARD/HEAVY) | sonnet → opus | 최종 품질 게이트 강화 |

### 4.2 비용 영향

| 복잡도 | 변경 전 | 변경 후 | 예상 증가율 |
|--------|---------|---------|------------|
| LIGHT | sonnet 전체 | sonnet 전체 | 0% |
| STANDARD | sonnet 전체 | sonnet + opus (2~4단계) | +40% |
| HEAVY | sonnet 전체 | sonnet + opus (4단계) | +60% |

> LIGHT 모드 사용자는 이번 변경의 비용 영향을 전혀 받지 않는다.

---

## 5. 제약 및 하위 호환성

### 5.1 플래그 동작 유지

| 플래그 | 동작 | 변경 여부 |
|--------|------|-----------|
| `--eco` | 전체 단계 sonnet 강제 (opus 단계 포함) | 변경 없음 |
| `--opus` | 전체 단계 opus 강제 | 변경 없음 |
| (기본, 플래그 없음) | LIGHT=haiku/sonnet, STANDARD/HEAVY=sonnet+opus 혼합 | **v24.1 신규** |

### 5.2 Executor 불변 원칙

`impl-manager`, `executor`, `qa-tester` 등 **구현·실행 에이전트는 모두 sonnet 유지**. 비용 폭증 방지 및 실행 안정성 보장.

### 5.3 API 가용성 전제

`claude-opus-4-6` API 접근 가능 상태 전제. Opus API 접근 불가 시 `--eco` 플래그로 sonnet 강제 사용 가능.

---

## 6. 변경 이력

| 날짜 | 버전 | 내용 |
|------|------|------|
| 2026-02-23 | v24.1 | opus-routing 구현 완료 — Sonnet 실행 / Opus 판단 분리 원칙 도입 |
| 이전 | v23.0 | 전체 sonnet 기본 적용, `--opus` 플래그만 opus 활성화 |

---

*보고서 종료 — opus-routing PDCA 완료 | 작성: writer 에이전트 | 2026-02-23*
