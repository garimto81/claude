# OMC/BKIT 통합 시스템 검증 - Plan Document

**Feature**: OMC/BKIT Integration Verification
**Created**: 2026-02-02
**Status**: Draft
**Plan ID**: omc-bkit-verification

---

## 1. Overview

### 1.1 Background

OMC와 BKIT 두 시스템이 `/auto v16.0`에서 통합되어 하이브리드 워크플로우를 제공합니다.

| 시스템 | 에이전트 수 | 핵심 철학 | 강점 |
|--------|:-----------:|----------|------|
| **OMC** | 32개 | Multi-Agent 병렬 실행 | 빠른 자율 실행, Ralplan, Ultrawork, Ralph |
| **BKIT** | 11개 | PDCA 문서화 방법론 | 체계적 문서화, gap-detector 검증 |
| **통합** | 43개 | 하이브리드 | 실행력 + 체계성 결합 |

통합 시스템의 핵심 구성요소:
- `omc_bridge.py`: 43개 에이전트 통합 레지스트리
- `pdca_engine.py`: PDCA 자동화 엔진
- 병렬 비교 호출 메서드
- 이중 검증 시스템 (OMC Architect + BKIT gap-detector)

### 1.2 Objectives

1. **통합 레지스트리 검증**: 43개 에이전트가 올바르게 등록되고 호출 가능한지 확인
2. **PDCA 엔진 검증**: Plan-Design-Do-Check-Act 사이클이 정상 동작하는지 확인
3. **병렬 비교 호출 검증**: OMC/BKIT 에이전트 병렬 호출 및 결과 비교 로직 검증
4. **이중 검증 검증**: Architect + gap-detector 조합이 정확한 판정을 내리는지 확인

### 1.3 Success Criteria

| # | 기준 | 목표 | 측정 방법 |
|---|------|------|----------|
| 1 | 에이전트 등록률 | 100% (43/43) | 레지스트리 조회 테스트 |
| 2 | 에이전트 호출 성공률 | 95%+ | 통합 테스트 |
| 3 | PDCA 문서 생성 | 4종류 모두 | 파일 존재 확인 |
| 4 | gap-detector 정확도 | 90%+ threshold 적용 | 샘플 케이스 검증 |
| 5 | 이중 검증 일관성 | Architect와 gap-detector 판정 일치율 85%+ | 비교 분석 |

---

## 2. Requirements

### 2.1 Functional Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|:--------:|-------|
| FR-01 | OMC 32개 에이전트 등록 확인 | P0 | `*` prefix |
| FR-02 | BKIT 11개 에이전트 등록 확인 | P0 | `bkit:*` prefix |
| FR-03 | 도메인별 에이전트 분류 검증 | P1 | 16개 도메인 |
| FR-04 | 모델 티어별 에이전트 분류 검증 | P1 | haiku/sonnet/opus |
| FR-05 | 에이전트 호출 메서드 동작 확인 | P0 | `get_agent()`, `get_agents_by_*()` |
| FR-06 | PDCA Plan 문서 생성 | P0 | `docs/01-plan/*.plan.md` |
| FR-07 | PDCA Design 문서 생성 | P0 | `docs/02-design/*.design.md` |
| FR-08 | PDCA Analysis 문서 생성 | P1 | `docs/03-analysis/*.analysis.md` |
| FR-09 | PDCA Report 문서 생성 | P1 | `docs/04-report/*.report.md` |
| FR-10 | gap-detector 임계값 설정 | P0 | PASS: 90%, WARN: 70%, FAIL: <70% |
| FR-11 | 병렬 비교 호출 코드 생성 | P1 | `build_parallel_comparison_call()` |
| FR-12 | 이중 검증 코드 생성 | P0 | `build_verification_comparison_call()` |
| FR-13 | 코드 리뷰 비교 호출 코드 생성 | P2 | `build_code_review_comparison_call()` |
| FR-14 | 결과 비교 및 병합 로직 | P1 | `compare_results()` |
| FR-15 | PDCA 상태 저장/복원 | P1 | `.omc/pdca-state.json` |

### 2.2 Non-Functional Requirements

| ID | Requirement | Metric | Target |
|----|-------------|--------|--------|
| NFR-01 | 에이전트 조회 응답 시간 | 단일 조회 | < 10ms |
| NFR-02 | PDCA 문서 생성 시간 | 단일 문서 | < 5초 |
| NFR-03 | 병렬 호출 오버헤드 | 직렬 대비 | < 20% |
| NFR-04 | 상태 파일 크기 | JSON 직렬화 | < 100KB |
| NFR-05 | 코드 유지보수성 | 순환 복잡도 | < 15 |

---

## 3. Scope

### 3.1 In Scope

**검증 대상 파일:**
- `C:\claude\.claude\skills\auto-workflow\scripts\omc_bridge.py` (905줄)
- `C:\claude\.claude\skills\auto-workflow\scripts\pdca_engine.py` (1,011줄)

**검증 항목:**

| 영역 | 검증 내용 |
|------|----------|
| **omc_bridge.py** | |
| - 클래스 | `OMCSkill`, `BKITSkill`, `ModelTier`, `AgentDomain` Enum |
| - 데이터 | `AgentInfo`, `AgentConfig`, `AgentResult`, `ComparisonResult` 등 |
| - 레지스트리 | `UNIFIED_AGENT_REGISTRY` (43개 에이전트) |
| - 매핑 | `DOMAIN_AGENT_PAIRS` (5개 도메인 비교 쌍) |
| - 메서드 | `get_agent()`, `get_agents_by_*()`, `find_*_counterpart()` |
| - 빌더 | `build_*_call()` 메서드들 |
| - 비교 | `compare_results()` |
| **pdca_engine.py** | |
| - Enum | `PDCAPhase`, `PDCAStatus` |
| - 설정 | `PDCAConfig` |
| - 데이터 | `PDCADocument`, `GapAnalysisResult`, `PDCAState` |
| - 템플릿 | `PLAN_TEMPLATE`, `DESIGN_TEMPLATE`, `ANALYSIS_TEMPLATE`, `REPORT_TEMPLATE` |
| - 엔진 | `PDCAEngine` 클래스 |
| - 메서드 | `generate_*_document()`, `check_gap_result()`, `start_cycle()` 등 |

### 3.2 Out of Scope

| 항목 | 이유 |
|------|------|
| 실제 에이전트 실행 | Task tool 호출은 런타임 환경 의존 |
| 외부 API 호출 | 네트워크 의존성 배제 |
| UI/UX 검증 | 백엔드 로직만 대상 |
| 성능 벤치마크 | 별도 성능 테스트 계획 필요 |
| 다른 스킬 파일 | 통합 시스템 핵심 파일만 대상 |

---

## 4. Test Cases

### 4.1 omc_bridge.py 테스트 케이스

#### TC-01: 에이전트 레지스트리 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-01-01 | OMC 에이전트 수 확인 | `get_agents_by_source("omc")` | 32개 |
| TC-01-02 | BKIT 에이전트 수 확인 | `get_agents_by_source("bkit")` | 11개 |
| TC-01-03 | 전체 에이전트 수 확인 | `get_agent_count()["total"]` | 43개 |
| TC-01-04 | 특정 에이전트 조회 | `get_agent("architect")` | AgentInfo(model=OPUS) |
| TC-01-05 | 존재하지 않는 에이전트 | `get_agent("invalid:agent")` | None |

#### TC-02: 도메인별 분류 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-02-01 | Analysis 도메인 | `get_agents_by_domain(ANALYSIS)` | 3개 (architect-*) + 2개 (BKIT) |
| TC-02-02 | Execution 도메인 | `get_agents_by_domain(EXECUTION)` | 3개 (executor-*) |
| TC-02-03 | Verification 도메인 | `get_agents_by_domain(VERIFICATION)` | 2개 (BKIT gap-detector, design-validator) |
| TC-02-04 | 비교 가능 도메인 | `list_comparable_domains()` | 5개 도메인 |

#### TC-03: 모델 티어별 분류 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-03-01 | Haiku 에이전트 | `get_agents_by_model(HAIKU)` | 11개 |
| TC-03-02 | Sonnet 에이전트 | `get_agents_by_model(SONNET)` | 18개 |
| TC-03-03 | Opus 에이전트 | `get_agents_by_model(OPUS)` | 14개 |

#### TC-04: 에이전트 쌍 매칭 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-04-01 | OMC→BKIT 대응 | `find_bkit_counterpart("code-reviewer")` | `bkit:code-analyzer` |
| TC-04-02 | BKIT→OMC 대응 | `find_omc_counterpart("bkit:gap-detector")` | `architect` |
| TC-04-03 | 대응 없는 에이전트 | `find_bkit_counterpart("writer")` | `bkit:report-generator` |

#### TC-05: 병렬 비교 호출 빌더 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-05-01 | 비교 호출 생성 | `build_parallel_comparison_call(REVIEW, "코드 리뷰")` | 두 Task 호출 포함 |
| TC-05-02 | 검증 비교 호출 | `build_verification_comparison_call(...)` | Architect + gap-detector 호출 |
| TC-05-03 | 코드 리뷰 비교 | `build_code_review_comparison_call("src/main.py")` | code-reviewer + code-analyzer 호출 |
| TC-05-04 | 비교 불가 도메인 | `build_parallel_comparison_call(GUIDE, "...")` | 단일 에이전트 호출 |

#### TC-06: 결과 비교 로직 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-06-01 | 둘 다 성공 | `compare_results(success, success)` | winner="both", confidence=0.9 |
| TC-06-02 | OMC만 성공 | `compare_results(success, fail)` | winner="omc", confidence=0.7 |
| TC-06-03 | BKIT만 성공 | `compare_results(fail, success)` | winner="bkit", confidence=0.7 |
| TC-06-04 | 둘 다 실패 | `compare_results(fail, fail)` | winner="none" |

### 4.2 pdca_engine.py 테스트 케이스

#### TC-07: PDCA 설정 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-07-01 | 기본 설정값 | `PDCAConfig()` | gap_threshold_pass=90, max_iterations=5 |
| TC-07-02 | 커스텀 설정 | `create_pdca_config(gap_threshold=85)` | gap_threshold_pass=85 |
| TC-07-03 | 디렉토리 경로 | `config.plan_dir` | "docs/01-plan" |

#### TC-08: PDCA 사이클 관리 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-08-01 | 사이클 시작 | `start_cycle("로그인 기능")` | PDCAState(phase=PLAN, iteration=1) |
| TC-08-02 | 반복 시작 | `start_iteration()` | iteration 증가, status=ITERATING |
| TC-08-03 | 반복 가능 여부 | `can_iterate()` (iteration<5) | True |
| TC-08-04 | 반복 불가 | `can_iterate()` (iteration=5) | False |

#### TC-09: PDCA 문서 생성 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-09-01 | Plan 문서 생성 | `generate_plan_document("로그인")` | docs/01-plan/로그인.plan.md |
| TC-09-02 | Design 문서 생성 | `generate_design_document("로그인", plan_path)` | docs/02-design/로그인.design.md |
| TC-09-03 | Analysis 문서 생성 | `generate_analysis_document(...)` | docs/03-analysis/로그인.analysis.md |
| TC-09-04 | Report 문서 생성 | `generate_report("로그인")` | docs/04-report/로그인.report.md |
| TC-09-05 | kebab-case 변환 | `_to_kebab_case("User Auth")` | "user-auth" |

#### TC-10: gap-detector 임계값 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-10-01 | PASS 판정 | `check_gap_result(95)` | True |
| TC-10-02 | PASS 경계값 | `check_gap_result(90)` | True |
| TC-10-03 | FAIL 판정 | `check_gap_result(89)` | False |
| TC-10-04 | GapAnalysisResult 입력 | `check_gap_result(GapAnalysisResult(92, "PASS"))` | True |

#### TC-11: PDCA 상태 저장/복원 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-11-01 | 상태 저장 | `save_state()` | .omc/pdca-state.json 생성 |
| TC-11-02 | 상태 복원 | `load_state()` | PDCAState 복원 |
| TC-11-03 | 문서 복원 | `load_state()` | documents dict 복원 |
| TC-11-04 | gap 결과 복원 | `load_state()` | gap_results list 복원 |
| TC-11-05 | 파일 없음 | `load_state("nonexistent")` | None |

#### TC-12: PDCA 워크플로우 빌더 검증

| ID | 테스트 | 입력 | 예상 결과 |
|----|--------|------|----------|
| TC-12-01 | 전체 워크플로우 | `build_full_pdca_workflow("로그인")` | 5 Phase Task 호출 포함 |
| TC-12-02 | Check 전용 워크플로우 | `build_check_only_workflow(...)` | Architect + gap-detector 호출 |

### 4.3 통합 테스트 케이스

#### TC-13: 이중 검증 시나리오

| ID | 시나리오 | 예상 결과 |
|----|----------|----------|
| TC-13-01 | Architect APPROVED + gap >= 90% | 완료 판정 |
| TC-13-02 | Architect APPROVED + gap 70-89% | WARN, 개선 권장 |
| TC-13-03 | Architect APPROVED + gap < 70% | FAIL, 개선 필수 |
| TC-13-04 | Architect REJECTED + gap >= 90% | 재검토 필요 |
| TC-13-05 | Architect REJECTED + gap < 70% | 즉시 개선 필요 |

#### TC-14: 에이전트 호출 흐름

| ID | 시나리오 | 예상 흐름 |
|----|----------|----------|
| TC-14-01 | PDCA Plan 생성 | planner (opus) -> Plan 문서 |
| TC-14-02 | PDCA Design 생성 | architect (opus) -> Design 문서 |
| TC-14-03 | PDCA Check 실행 | gap-detector (opus) -> Analysis 문서 |
| TC-14-04 | PDCA Act 실행 | pdca-iterator (sonnet) -> 개선 |
| TC-14-05 | Report 생성 | report-generator (haiku) -> Report 문서 |

---

## 5. Acceptance Criteria

### 5.1 기능 검증 합격 기준

| # | 검증 항목 | 합격 기준 | 검증 방법 |
|---|----------|----------|----------|
| AC-01 | 에이전트 레지스트리 | 43개 전체 등록 확인 | 단위 테스트 |
| AC-02 | 도메인 분류 | 16개 도메인 매핑 정확 | 단위 테스트 |
| AC-03 | 모델 티어 분류 | haiku/sonnet/opus 분류 정확 | 단위 테스트 |
| AC-04 | 비교 쌍 매칭 | 5개 도메인 쌍 매칭 정확 | 단위 테스트 |
| AC-05 | PDCA 문서 생성 | 4종류 문서 모두 생성 | 통합 테스트 |
| AC-06 | gap 임계값 | 90% 기준 정확 적용 | 단위 테스트 |
| AC-07 | 상태 관리 | 저장/복원 무손실 | 단위 테스트 |

### 5.2 이중 검증 합격 기준 (90% gap threshold)

| 조합 | Architect | gap-detector | 최종 판정 |
|------|:---------:|:------------:|:---------:|
| A | APPROVED | >= 90% (PASS) | **COMPLETE** |
| B | APPROVED | 70-89% (WARN) | WARN |
| C | APPROVED | < 70% (FAIL) | **FAIL** |
| D | REJECTED | >= 90% (PASS) | **REVIEW** |
| E | REJECTED | < 90% | **FAIL** |

**합격 조건:**
- 조합 A일 때만 "COMPLETE" 판정
- 조합 B일 때 WARN과 함께 개선 권장사항 제공
- 조합 C, E일 때 즉시 개선 필요 안내
- 조합 D일 때 Architect 재검토 요청

### 5.3 테스트 커버리지 기준

| 파일 | 최소 커버리지 | 목표 커버리지 |
|------|:------------:|:------------:|
| omc_bridge.py | 80% | 90% |
| pdca_engine.py | 80% | 90% |
| 통합 테스트 | 70% | 85% |

---

## 6. Risks

| Risk | Probability | Impact | Mitigation |
|------|:-----------:|:------:|------------|
| BKIT 에이전트 호출 실패 | Medium | High | prefix 규칙 명확화, 폴백 로직 구현 |
| gap-detector 정확도 이슈 | Medium | Medium | 임계값 조정 가능하게 설정 |
| 상태 파일 손상 | Low | Medium | 백업 및 복구 로직 추가 |
| 병렬 호출 타이밍 이슈 | Low | Low | 타임아웃 설정, 재시도 로직 |
| 템플릿 형식 변경 | Low | Low | 버전 관리, 마이그레이션 가이드 |
| 에이전트 API 변경 | Medium | High | 버전 호환성 매트릭스 유지 |

---

## 7. Timeline

| Phase | Duration | Deliverable |
|-------|:--------:|-------------|
| Plan | 완료 | 본 문서 |
| Design | 1일 | 테스트 설계 문서 |
| Do | 2일 | 테스트 코드 구현 |
| Check | 1일 | 테스트 실행 및 gap 분석 |
| Act | 1일 | 발견된 이슈 수정 |
| **Total** | **5일** | 검증 완료 보고서 |

---

## 8. Test Execution Plan

### 8.1 테스트 환경

| 항목 | 값 |
|------|-----|
| Python 버전 | 3.11+ |
| 테스트 프레임워크 | pytest |
| 커버리지 도구 | pytest-cov |
| 실행 위치 | `C:\claude\` |

### 8.2 테스트 명령

```powershell
# 단위 테스트
pytest tests/test_omc_bridge.py -v

# PDCA 엔진 테스트
pytest tests/test_pdca_engine.py -v

# 통합 테스트
pytest tests/test_omc_bkit_integration.py -v

# 커버리지 포함
pytest tests/ -v --cov=.claude/skills/auto-workflow/scripts --cov-report=html
```

### 8.3 테스트 파일 구조

```
tests/
+-- test_omc_bridge.py           # TC-01 ~ TC-06
+-- test_pdca_engine.py          # TC-07 ~ TC-12
+-- test_omc_bkit_integration.py # TC-13 ~ TC-14
+-- fixtures/
    +-- sample_design.md         # 테스트용 설계 문서
    +-- sample_implementation.py # 테스트용 구현 코드
```

---

## Version History

| Version | Date | Author | Changes |
|:-------:|------|--------|---------|
| 0.1 | 2026-02-02 | Prometheus | Initial draft |

---

## References

- `omc_bridge.py`: `C:\claude\.claude\skills\auto-workflow\scripts\omc_bridge.py`
- `pdca_engine.py`: `C:\claude\.claude\skills\auto-workflow\scripts\pdca_engine.py`
- 통합 계획: `.omc/plans/omc-bkit-auto-unified-integration.md`
- BKIT 통합 계획: `.omc/plans/omc-bkit-integration.md`

---

**PLAN_READY: docs/01-plan/omc-bkit-verification.plan.md**
