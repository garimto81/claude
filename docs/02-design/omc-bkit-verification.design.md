# OMC/BKIT 통합 시스템 검증 - Design Document

**Feature**: OMC/BKIT Integration Verification
**Created**: 2026-02-02
**Status**: Draft
**Plan Reference**: docs/01-plan/omc-bkit-verification.plan.md

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         /auto v16.0 Unified System                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐        │
│  │      omc_bridge.py          │    │      pdca_engine.py         │        │
│  │   (Agent Registry + Bridge) │◀──▶│   (PDCA Workflow Engine)    │        │
│  └──────────────┬──────────────┘    └──────────────┬──────────────┘        │
│                 │                                   │                       │
│    ┌────────────┴────────────┐         ┌───────────┴───────────┐           │
│    │                         │         │                       │           │
│    ▼                         ▼         ▼                       ▼           │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────────┐       │
│  │   OMC     │  │   BKIT    │  │   PDCA    │  │   State Manager   │       │
│  │ 32 Agents │  │ 11 Agents │  │ Documents │  │ (.omc/pdca-state) │       │
│  └───────────┘  └───────────┘  └───────────┘  └───────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Test Cases

### TC-01: 에이전트 레지스트리 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-01-01 | OMC 에이전트 수 | `get_agents_by_source("omc")` | 32개 |
| TC-01-02 | BKIT 에이전트 수 | `get_agents_by_source("bkit")` | 11개 |
| TC-01-03 | 전체 에이전트 수 | `len(UNIFIED_AGENT_REGISTRY)` | 43개 |

### TC-02: PDCA 엔진 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-02-01 | 기본 임계값 | `PDCAConfig().gap_threshold_pass` | 90 |
| TC-02-02 | PASS 판정 | `check_gap_result(90)` | True |
| TC-02-03 | FAIL 판정 | `check_gap_result(89)` | False |

### TC-03: 이중 검증 매트릭스

| ID | Architect | gap-detector | 최종 판정 |
|----|:---------:|:------------:|:---------:|
| TC-03-01 | APPROVED | >= 90% | **COMPLETE** |
| TC-03-02 | APPROVED | < 90% | **ITERATE** |
| TC-03-03 | REJECTED | any | **REVIEW** |

---

## 3. Data Flow

### PDCA Cycle Flow

```
PLAN → DESIGN → DO → CHECK → ACT
  │       │       │      │      │
  ▼       ▼       ▼      ▼      ▼
planner architect executor gap-   pdca-
(opus)  (opus)   (sonnet) detector iterator
                          (opus)  (sonnet)
                            │
                    gap < 90%? ──YES──▶ ACT으로 돌아감
                            │
                           NO
                            ▼
                         REPORT
```

---

## 4. Acceptance Criteria

| AC | 기준 | 목표 |
|----|------|------|
| AC-01 | 에이전트 등록률 | 100% (43/43) |
| AC-02 | gap threshold 적용 | 90% |
| AC-03 | PDCA 문서 생성 | 4종류 모두 |
| AC-04 | 이중 검증 동작 | Architect + gap-detector |

---

**DESIGN_READY: docs/02-design/omc-bkit-verification.design.md**
