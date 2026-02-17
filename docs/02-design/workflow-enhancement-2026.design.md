# Workflow Enhancement 2026 - Design Document

**Version**: 1.0.0
**Date**: 2026-02-05
**Author**: Aiden Kim
**Plan Reference**: docs/01-plan/workflow-enhancement-2026.plan.md

---

## 1. 아키텍처 설계

### 1.1 현재 아키텍처

```
사용자
  │
  ▼
/auto (Orchestrator) ─── omc_delegate ──► autopilot
  │                                            │
  ├─ Phase 0: PDCA 문서화                       ├─ Ralplan (Planner→Architect→Critic)
  ├─ Phase 1: 옵션 라우팅                       ├─ Ultrawork (병렬 실행)
  ├─ Phase 2: Ralph 루프                        └─ Ralph (5개 조건 검증)
  └─ Phase 3: 자율 발견
```

### 1.2 목표 아키텍처

```
사용자
  │
  ▼
/auto (Orchestrator v16.1)
  │
  ├─ --interactive: 단계적 승인 게이트
  ├─ --work: /work --loop 흡수 (장기)
  │
  ├─ Phase 0: PDCA 문서화 (Ralplan 자동 연결)
  │    ├─ Ralplan 합의 → docs/01-plan/ 자동 기록 ★NEW
  │    └─ Architect 설계 → docs/02-design/ 자동 기록
  │
  ├─ Phase 1: 옵션 라우팅
  │    └─ --interactive 옵션 추가 ★NEW
  │
  ├─ Phase 2: Ralph 루프
  │    └─ 이중 검증 (OMC Architect + BKIT gap-detector 독립 실행) ★ENHANCED
  │
  └─ Phase 3: CI/CD 연동
       ├─ Claude Code Action (이슈→수정→PR) ★NEW
       ├─ PR 자동 리뷰 ★NEW
       └─ CI 실패 자동 복구 ★NEW
```

---

## 2. 컴포넌트별 상세 설계

### 2.1 Claude Code Action (claude-code.yml)

**이벤트 트리거:**

| 이벤트 | Job | 동작 |
|--------|-----|------|
| `issues` + `claude-autofix` 라벨 | fix-issue | 이슈 분석 → 브랜치 생성 → 수정 → PR |
| `issue_comment` + `@claude` 멘션 | fix-issue | 코멘트 기반 수정 지시 |
| `pull_request` | review-pr | 코드 리뷰 코멘트 자동 생성 |
| `pull_request_review_comment` + `@claude` | review-pr | 리뷰 코멘트 기반 추가 수정 |

**CI 실패 자동 복구 체인:**
```
ci.yml 실패 (PR)
  → auto-fix-on-failure job 실행
  → "CI Fix: {PR제목}" 이슈 자동 생성
  → claude-autofix + ci-failure 라벨 부착
  → claude-code.yml fix-issue job 트리거
  → Claude가 실패 로그 분석 → 수정 → PR
```

### 2.2 BKIT 에이전트 역할 분화

**변경 전 (force_omc=True):**
```
bkit:gap-detector 요청 → OMC architect로 fallback → 동일한 검증
```

**변경 후 (force_omc=False):**
```
bkit:gap-detector 요청 → BKIT 직접 실행 → 수치적 갭 분석 (match_percentage)
OMC architect 요청 → OMC 직접 실행 → 기능적 완성도 검증 (APPROVED/REJECTED)
```

**BKIT 에이전트 PDCA 역할 매핑:**

| 에이전트 | PDCA 단계 | 고유 역할 | OMC와의 차별점 |
|---------|----------|----------|---------------|
| gap-detector | Check | 수치적 갭 분석 (0-100%) | OMC architect는 정성적 판단 |
| design-validator | Design | 설계 완성도 검증 | OMC architect는 아키텍처 판단 |
| code-analyzer | Check | 컨벤션/품질 정량 분석 | OMC code-reviewer는 보안/버그 중심 |
| pdca-iterator | Act | 자동 개선 사이클 (max 5) | OMC executor는 단순 구현 |
| report-generator | Report | PDCA 종합 보고서 | OMC writer는 일반 문서 |

### 2.3 /auto --interactive 설계

**상태 머신:**
```
INIT → PLAN_GATE → DESIGN_GATE → DO → CHECK_GATE → ACT_GATE → COMPLETE
         │              │                    │           │
         ▼              ▼                    ▼           ▼
    AskUserQuestion  AskUserQuestion  AskUserQuestion  AskUserQuestion
    (진행/수정/스킵) (진행/수정/스킵) (진행/수정)     (자동/수동/완료)
```

### 2.4 Ralplan→PDCA 자동 연결

**데이터 흐름:**
```
1. Ralplan 실행 (Planner→Architect→Critic 합의)
2. 합의 결과 JSON 생성
3. Executor가 JSON → docs/01-plan/{feature}.plan.md 변환
4. Plan 문서에 포함될 섹션:
   - 합의된 아키텍처 결정
   - 구현 범위 및 제외
   - 영향 파일 목록
   - 위험 요소
   - 각 관점 요약 (Planner/Architect/Critic)
```

### 2.5 /auto + /work --loop 통합 설계 (장기)

**현재 중복:**
| 기능 | /auto | /work --loop |
|------|-------|-------------|
| 자율 반복 | ✅ Ralph 루프 | ✅ 5계층 Tier |
| Context 관리 | ✅ 90% 임계값 | ✅ 90% 임계값 |
| 에이전트 호출 | ✅ 43개 | ✅ 제한적 |
| PDCA | ✅ 필수 | ❌ 없음 |
| Ralplan | ✅ 있음 | ❌ 없음 |

**통합 방안:**
- /auto --work: 기존 /work --loop 기능 (PDCA 없이 빠른 실행)
- /work: 단일 작업 실행 (비루프)으로 역할 축소
- /work --loop: /auto --work로 redirect

### 2.6 에이전트 메트릭 시스템 (장기)

**데이터 모델:**
```json
{
  "agent_type": "executor",
  "model": "sonnet",
  "invocation_id": "uuid",
  "start_time": "ISO8601",
  "end_time": "ISO8601",
  "duration_ms": 15000,
  "success": true,
  "tokens_used": 5000,
  "task_type": "implementation",
  "caller": "/auto"
}
```

**저장 위치:** `.omc/stats/agent-metrics.json`
**분석:** `/audit` 커맨드에서 메트릭 분석 및 최적화 추천

---

## 3. 영향 분석

### 3.1 파일 변경 목록

| 파일 | 변경 유형 | 개선 항목 |
|------|----------|----------|
| `.github/workflows/claude-code.yml` | 전면 교체 | Claude Code Action 활성화 |
| `.github/workflows/ci.yml` | 추가 | CI 실패 자동 복구 job |
| `.claude/skills/auto/SKILL.md` | 수정 | Ralplan-PDCA 연결, --interactive |
| `.claude/skills/auto-workflow/scripts/omc_bridge.py` | 수정 | BKIT force_omc 변경, 역할 강화 |
| `docs/AGENTS_REFERENCE.md` | 수정 | 모델 정보 동기화 |
| `.claude/skills/{5개}/SKILL.md` | 축소 | Deprecated 스킬 정리 |
| `.claude/commands/work.md` | 수정 (장기) | --loop redirect |
| `.claude/rules/08-skill-routing.md` | 수정 (장기) | 인과관계 그래프 업데이트 |
| `.omc/stats/agent-metrics.json` | 신규 (장기) | 메트릭 저장소 |

### 3.2 호환성

| 변경 | 하위 호환성 | 완화 방안 |
|------|:----------:|----------|
| BKIT force_omc=False | ⚠️ | BKIT 에이전트는 이미 Claude Code에서 직접 호출 가능 |
| --interactive 옵션 | ✅ | 기존 동작 변경 없음 (옵션 미사용 시) |
| /work --loop redirect | ⚠️ (장기) | alias 유지 |

---

## 4. 검증 계획

| 검증 항목 | 방법 | 통과 기준 |
|----------|------|----------|
| Claude Code Action 작동 | claude-autofix 라벨 테스트 이슈 생성 | PR 자동 생성됨 |
| CI 자동 복구 | 의도적 테스트 실패 PR | auto-fix 이슈 생성됨 |
| BKIT 독립 실행 | gap-detector 직접 호출 | fallback 없이 결과 반환 |
| Ralplan-PDCA 연결 | /auto "테스트" 실행 | plan.md 자동 생성됨 |
| --interactive | /auto --interactive "테스트" | AskUserQuestion 호출됨 |
