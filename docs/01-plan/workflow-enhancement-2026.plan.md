# Workflow Enhancement 2026 - PDCA Plan

**Version**: 1.0.0
**Date**: 2026-02-05
**Author**: Aiden Kim
**Status**: Active

---

## 1. 프로젝트 개요

### 1.1 배경
2026년 2월 SNS 트렌드 분석에서 도출된 3가지 핵심 트렌드를 벤치마크로, 현재 Claude Code 워크플로우 시스템(커맨드 23개, 스킬 46개, 에이전트 62개)의 전면 개선을 수행합니다.

### 1.2 벤치마크 트렌드

| # | 트렌드 | 현재 수준 | 목표 |
|:-:|--------|:--------:|:----:|
| 1 | Agentic Planner (계획 선행 강제) | 95% | 98% |
| 2 | Claude Code Action (CI/CD 자동화) | 65% | 95% |
| 3 | Skills 패키징 (도메인 지식 주입) | 85% | 95% |

### 1.3 핵심 목표
- CI/CD 파이프라인에 Claude Code Action 완전 통합
- BKIT 에이전트의 실질적 역할 확립 (OMC shadow에서 탈피)
- 스킬/커맨드 중복 제거 및 구조 단순화
- 에이전트 성과 메트릭 기반 지속적 개선 체계 구축

---

## 2. 개선 항목 (11개)

### Phase 1: 즉시 실행 (HIGH IMPACT, LOW EFFORT)

#### 2.1 Claude Code Action 활성화
- **현황**: `.github/workflows/claude-code.yml`이 Placeholder 상태 (lines 46-53 주석 처리)
- **목표**: anthropics/claude-code-action@v1 실제 연결
- **범위**:
  - Phase A: 이슈 코멘트 트리거 ("@claude fix this" → 자동 수정 → PR 생성)
  - Phase B: PR 자동 리뷰 (pull_request 이벤트 → Claude 리뷰 코멘트)
  - Phase C: CI 실패 자동 복구 (ci.yml 실패 → claude-autofix 라벨 자동 부착)
- **영향 파일**: `.github/workflows/claude-code.yml`
- **의존성**: ANTHROPIC_API_KEY GitHub Secret 등록 필요

#### 2.2 Deprecated 스킬 5개 정리
- **현황**: auto-executor, auto-workflow, cross-ai-verifier, issue-resolution, tdd-workflow가 redirect만 수행
- **목표**: 디렉토리 삭제 또는 최소화
- **범위**: 각 SKILL.md를 3줄 redirect-only로 축소 (디렉토리 완전 삭제는 기존 참조 깨짐 방지)
- **영향 파일**: `.claude/skills/{5개 deprecated 스킬}/SKILL.md`

#### 2.3 AGENTS_REFERENCE.md 동기화
- **현황**:
  - code-reviewer: 문서 "sonnet" / 실제 "haiku"
  - docs-writer: 문서 "sonnet" / 실제 "haiku"
  - github-engineer: 문서 "sonnet" / 실제 "haiku"
  - 스킬 개수: 문서 "18개" / 실제 "46개"
- **목표**: 실제 파일과 100% 일치
- **영향 파일**: `docs/AGENTS_REFERENCE.md`

#### 2.4 Ralplan-PDCA 자동 연결
- **현황**: Ralplan 결과가 메모리에만 존재, PDCA Plan 문서와 미연결
- **목표**: Ralplan 완료 시 docs/01-plan/{feature}.plan.md에 자동 기록
- **범위**: `/auto` SKILL.md Phase 0.1에 Ralplan→Plan 문서 연결 로직 추가
- **영향 파일**: `.claude/skills/auto/SKILL.md`

### Phase 2: 중기 개선 (1-2주)

#### 2.5 /auto --interactive 단계적 승인 모드
- **현황**: /auto는 전체 자율 실행 또는 중단만 가능
- **목표**: 각 Phase(Plan→Design→Do→Check) 전환 시 사용자 확인 옵션
- **범위**:
  - SKILL.md에 --interactive 옵션 문서화
  - 각 Phase 경계에서 AskUserQuestion 호출
  - 사용자가 "skip" 선택 시 해당 Phase 건너뜀 가능
- **영향 파일**: `.claude/skills/auto/SKILL.md`, `.claude/commands/auto.md`

#### 2.6 CI 실패 자동 복구 파이프라인
- **현황**: CI 실패 시 수동 대응
- **목표**: ci.yml 실패 → claude-autofix 라벨 자동 부착 → Claude Code Action 트리거
- **범위**:
  - ci.yml에 on failure step 추가 (라벨 부착)
  - claude-code.yml에 CI 실패 컨텍스트 전달 로직
- **영향 파일**: `.github/workflows/ci.yml`, `.github/workflows/claude-code.yml`

#### 2.7 BKIT 에이전트 실질적 분화
- **현황**: omc_bridge.py의 force_omc=True로 BKIT 에이전트가 항상 OMC로 fallback
- **목표**: BKIT 에이전트가 PDCA 문서 생성/검증에 실질적으로 기여
- **범위**:
  - force_omc 기본값을 False로 변경
  - BKIT 에이전트 프롬프트에 PDCA 특화 지시 추가
  - gap-detector: 설계 문서 기반 수치적 갭 분석 (OMC architect와 차별화)
  - pdca-iterator: 반복 개선 사이클 자동 실행
  - report-generator: PDCA 보고서 템플릿 기반 문서 생성
- **영향 파일**: `.claude/skills/auto-workflow/scripts/omc_bridge.py`

### Phase 3: 장기 비전 (1개월+)

#### 2.8 /auto와 /work --loop 통합
- **현황**: /auto(1278줄)와 /work --loop(516줄)이 5계층 우선순위, 자율 반복, Context 관리를 중복 제공
- **목표**: /work --loop를 /auto의 서브모드로 흡수
- **범위**:
  - /auto --work 옵션으로 기존 /work --loop 기능 제공
  - /work 커맨드는 단일 작업 실행으로 역할 축소 (비루프)
  - 인과관계 그래프 업데이트
- **영향 파일**: `.claude/commands/auto.md`, `.claude/commands/work.md`, `.claude/skills/work/SKILL.md`, `.claude/rules/08-skill-routing.md`

#### 2.9 에이전트 성과 메트릭 시스템
- **현황**: 에이전트 사용 통계 없음 (command-analytics 스킬은 커맨드만 추적)
- **목표**: 에이전트별 성공률/비용/응답시간 자동 추적
- **범위**:
  - `.omc/stats/agent-metrics.json` 자동 기록
  - 호출 시작/종료 시간, 성공/실패, 모델 티어 기록
  - /audit 스킬에서 메트릭 분석 및 최적화 추천
- **영향 파일**: `.omc/stats/agent-metrics.json` (신규), `/audit` 커맨드

---

## 3. 실행 일정

| Phase | 항목 | 시작 | 예상 완료 | 우선순위 |
|:-----:|------|:----:|:---------:|:--------:|
| 1 | Claude Code Action 활성화 | 2026-02-05 | 2026-02-05 | P0 |
| 1 | Deprecated 스킬 정리 | 2026-02-05 | 2026-02-05 | P1 |
| 1 | AGENTS_REFERENCE 동기화 | 2026-02-05 | 2026-02-05 | P1 |
| 1 | Ralplan-PDCA 연결 | 2026-02-05 | 2026-02-05 | P0 |
| 2 | --interactive 모드 | 2026-02-06 | 2026-02-10 | P1 |
| 2 | CI 자동 복구 | 2026-02-06 | 2026-02-12 | P0 |
| 2 | BKIT 역할 재정의 | 2026-02-10 | 2026-02-17 | P1 |
| 3 | /auto + /work 통합 | 2026-02-17 | 2026-03-01 | P2 |
| 3 | 에이전트 메트릭 | 2026-02-20 | 2026-03-10 | P2 |

---

## 4. 성공 지표

| 지표 | 현재 | 목표 | 측정 방법 |
|------|:----:|:----:|----------|
| Agentic Planner 트렌드 일치 | 95% | 98% | Ralplan→PDCA 문서 자동 연결률 |
| CI/CD 자동화 수준 | 65% | 95% | Claude Code Action 활성 이벤트 수 |
| Skills 패키징 성숙도 | 85% | 95% | deprecated 제거 + 문서 동기화율 |
| 에이전트 레이어 효율 | 62개 (shadow 포함) | 62개 (각자 고유 역할) | BKIT 독립 실행률 |
| 중복 제거 | /auto+/work 중복 | 단일 진입점 | 커맨드 줄 수 감소율 |

---

## 5. 위험 요소

| 위험 | 확률 | 영향 | 완화 방안 |
|------|:----:|:----:|----------|
| ANTHROPIC_API_KEY 미등록 | 중 | 높 | GitHub Secret 등록 가이드 제공 |
| Claude Code Action 공식 미출시 | 낮 | 높 | 대안: Claude API 직접 호출 스크립트 |
| 인과관계 그래프 깨짐 | 중 | 높 | 변경 전 /audit 검증 필수 |
| BKIT force_omc 변경 부작용 | 중 | 중 | 단계적 전환 (도메인별 opt-in) |
| /work 통합 시 기존 사용자 혼란 | 낮 | 중 | /work을 alias로 유지 |

---

## 6. 참조 문서

| 문서 | 용도 |
|------|------|
| `.claude/rules/08-skill-routing.md` | 인과관계 그래프 (절대 보존) |
| `docs/AGENTS_REFERENCE.md` | 에이전트 참조 가이드 |
| `.github/workflows/claude-code.yml` | Claude Code Action 워크플로우 |
| `.claude/skills/auto-workflow/scripts/omc_bridge.py` | OMC+BKIT 통합 브리지 |
