---
name: auto
description: 하이브리드 자율 워크플로우 - OMC+BKIT 통합 (Ralph + Ultrawork + PDCA 필수)
version: 18.1.0
triggers:
  keywords:
    - "/auto"
    - "auto"
    - "autopilot"
    - "ulw"
    - "ultrawork"
    - "ralph"
model_preference: opus
auto_trigger: true
omc_delegate: oh-my-claudecode:autopilot
omc_agents:
  - executor
  - executor-high
  - oh-my-claudecode:architect
  - planner
  - critic
bkit_agents:
  - gap-detector
  - pdca-iterator
  - code-analyzer
  - report-generator
---

# /auto - 하이브리드 자율 워크플로우 (v16.0 - OMC+BKIT 통합)

> **핵심**: `/auto "작업"` = **PDCA 문서화(필수)** + Ralph 루프 + Ultrawork 병렬 + **이중 검증**

## OMC + BKIT Integration (43 에이전트)

**OMC** (실행력): executor, executor-high, architect, planner, critic, code-reviewer
**BKIT** (체계성): gap-detector (90% 검증), pdca-iterator, code-analyzer, report-generator
**호출**: `Skill(skill="oh-my-claudecode:autopilot", args="작업 설명")`

## 필수 실행 규칙 (CRITICAL)

**이 스킬이 활성화되면 반드시 아래 워크플로우를 실행하세요!**

### Phase 0: PDCA 문서화 (필수 - BKIT 워크플로우)

상세 PDCA 워크플로우 (Step 0.0~0.5): `REFERENCE.md` 참조

### Phase 1: 옵션 라우팅 (있을 경우)

| 옵션 | 실행할 스킬 | 설명 |
|------|-------------|------|
| `--gdocs` | `Skill(skill="prd-sync")` | Google Docs PRD 동기화 |
| `--mockup` | `Skill(skill="mockup-hybrid", args="...")` | 목업 생성 |
| `--debate` | `Skill(skill="ultimate-debate", args="...")` | 3AI 토론 |
| `--research` | `Skill(skill="research", args="...")` | 리서치 모드 |
| `--slack <채널>` | Slack 채널 분석 후 컨텍스트 주입 | 채널 히스토리 기반 작업 |
| `--gmail` | Gmail 메일 분석 후 컨텍스트 주입 | 메일 기반 작업 |
| `--daily` | `Skill(skill="daily")` | daily v3.0 9-Phase Pipeline |
| `--daily --slack` | `Skill(skill="daily")` | 동일 Pipeline + Phase 6 Slack Lists 갱신 |
| `--interactive` | 각 Phase 전환 시 사용자 승인 요청 | 단계적 승인 모드 |

**옵션 체인 예시:**
```
/auto --gdocs --mockup "화면명"
→ Step 1: Skill(skill="prd-sync")
→ Step 2: Skill(skill="mockup-hybrid", args="화면명")
```

**옵션 실패 시**: 에러 메시지 출력, **절대 조용히 스킵하지 않음**. 상세: `REFERENCE.md`

### Phase 2: 메인 워크플로우 (Ralph + Ultrawork + Team Coordinator)

**작업이 주어지면 (`/auto "작업내용"`):**

**Step 2.0: 복잡도 기반 라우팅 (10점 만점 확장)**

| 점수 (10점) | 라우팅 경로 | 설명 |
|:-----------:|------------|------|
| 0-3 | 기존 경로 | Ralplan/Planner 단독 |
| 4-5 | Team Coordinator -> Dev 단독 | 단일 기능 구현 |
| 6-7 | Team Coordinator -> Dev + Quality | 기능 + 품질 검증 |
| 8-9 | Team Coordinator -> Dev + Quality + Research | 복잡한 기능 + 조사 |
| 10 | Team Coordinator -> 4팀 전체 | 대규모 프로젝트 |

**5점 -> 10점 변환**: `score_10 = score_5 * 2`. `"teamwork"` 키워드 포함 시 자동 10점.

**score < 4 (기존 경로):**

1. **Ralplan 호출** (score >= 3): `Skill(skill="oh-my-claudecode:ralplan", args="작업내용")`
2. **Ultrawork 모드**: 독립 작업 병렬 실행, `run_in_background: true`, 10+ 동시 에이전트
3. **에이전트 라우팅**:

   | 작업 유형 | 에이전트 | 모델 |
   |----------|----------|------|
   | 간단한 조회 | `oh-my-claudecode:explore` | haiku |
   | 기능 구현 | `oh-my-claudecode:executor` | sonnet |
   | 복잡한 분석 | `oh-my-claudecode:architect` | opus |
   | UI 작업 | `oh-my-claudecode:designer` | sonnet |
   | 테스트 | `oh-my-claudecode:qa-tester` | sonnet |
   | 빌드 에러 | `oh-my-claudecode:build-fixer` | sonnet |

**score >= 4 (Team Coordinator):**

```python
from src.agents.teams import Coordinator
coordinator = Coordinator()
result = coordinator.run("작업 설명")
```

4. **Architect 검증** (완료 전 필수)
5. **완료 조건**: Architect 승인 + 모든 TODO 완료 + 빌드/테스트 통과

## Ralph 루프 워크플로우 (CRITICAL)

**autopilot = Ralplan + Ultrawork + Ralph 루프**

```
Ralplan (계획 합의) -> Ultrawork (병렬 실행) -> Architect 검증
-> Ralph 루프 (5개 조건: TODO==0, 기능 동작, 테스트 통과, 에러==0, Architect 승인)
-> ANY 실패? -> 자동 재시도 / 모두 충족 -> 완료 선언
```

### Phase 3: 자율 발견 모드 (`/auto` 단독 실행)

| Tier | 이름 | 발견 대상 | 실행 |
|:----:|------|----------|------|
| 0 | CONTEXT | context >= 90% | 체크포인트 생성 |
| 1 | EXPLICIT | 사용자 지시 | 해당 작업 실행 |
| 2 | URGENT | 빌드/테스트 실패 | `/debug` 실행 |
| 3 | WORK | pending TODO, 이슈 | 작업 처리 |
| 4 | SUPPORT | staged 파일, 린트 에러 | `/commit`, `/check` |
| 5 | AUTONOMOUS | 코드 품질 개선 | 리팩토링 제안 |

## 세션 관리

```bash
/auto status    # 현재 상태 확인
/auto stop      # 중지 (상태 저장)
/auto resume    # 재개
```

## 금지 사항

옵션 실패 시 조용히 스킵 / Architect 검증 없이 완료 선언 / 증거 없이 "완료됨" 주장 / 테스트 삭제로 문제 해결

**상세**: Phase 0 PDCA, --slack, --gmail, --interactive, Phase 4 /work --loop -> `REFERENCE.md` | `.claude/commands/auto.md`
