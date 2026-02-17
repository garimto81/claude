# OMC/BKIT 통합 시스템 검증 - Analysis Document

**Feature**: OMC/BKIT Integration Verification
**Created**: 2026-02-02
**Status**: Analyzed
**Plan Reference**: docs/01-plan/omc-bkit-verification.plan.md
**Design Reference**: docs/02-design/omc-bkit-verification.design.md

---

## 1. 검증 결과 요약

### 1.1 이중 검증 결과

| 검증자 | 결과 | 점수 |
|--------|:----:|:----:|
| **OMC Architect** | APPROVED (조건부) | 82/100 |
| **BKIT gap-detector** | ⚠️ 호출 불가 | N/A |

### 1.2 Gap 분석

**실제 Gap Rate: 82%** (90% 미달 - ITERATE 필요)

| 항목 | 만점 | 획득 | Gap |
|------|:----:|:----:|:---:|
| 에이전트 레지스트리 | 25 | 25 | 0 |
| PDCA 엔진 로직 | 25 | 25 | 0 |
| 병렬 비교 호출 빌더 | 15 | 15 | 0 |
| 이중 검증 시스템 | 20 | 10 | **-10** |
| 테스트 커버리지 | 10 | 2 | **-8** |
| 문서화 | 5 | 5 | 0 |

---

## 2. 발견된 이슈

### 2.1 CRITICAL: BKIT 에이전트 호출 불가

```
문제: bkit:gap-detector, bkit:pdca-iterator 등 BKIT 에이전트가
     Task tool의 subagent_type으로 직접 호출 불가

원인: Claude Code의 Task tool은 현재 프로젝트에 등록된 에이전트만 호출 가능
     BKIT 에이전트는 플러그인 캐시에만 존재하고 로컬 등록 안 됨

영향: 이중 검증 시스템의 핵심 기능(gap-detector) 동작 불가
```

### 2.2 HIGH: 테스트 파일 부재

- `tests/test_omc_bridge.py` - 없음
- `tests/test_pdca_engine.py` - 없음
- 인라인 테스트만 수행 (pytest 형식 아님)

---

## 3. 수정 필요 항목

### P0 (필수)

1. **BKIT 에이전트 호출 폴백 전략 구현**
   - Option A: BKIT 에이전트를 `.claude/agents/`로 복사
   - Option B: OMC architect로 gap-detector 역할 대체
   - Option C: BKIT 스킬을 Skill tool로 호출

### P1 (권장)

2. **pytest 테스트 파일 생성**
   - `tests/test_omc_bridge.py`
   - `tests/test_pdca_engine.py`

---

## 4. 다음 단계

Gap 82% < 90% 이므로 **Act 단계로 진행하여 개선 필요**

| Phase | 상태 |
|-------|:----:|
| Plan | ✅ 완료 |
| Design | ✅ 완료 |
| Do | ✅ 완료 (테스트 10/10 PASS) |
| Check | ⚠️ Gap 82% (90% 미달) |
| Act | 🔄 진행 필요 |

---

**ANALYSIS_READY: docs/03-analysis/omc-bkit-verification.analysis.md**
