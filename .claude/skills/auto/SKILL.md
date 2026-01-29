---
name: auto
description: 하이브리드 자율 워크플로우 - Ralph + Ultrawork + Ralplan 자동 통합
version: 15.1.0
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
---

# /auto - 하이브리드 자율 워크플로우

> **핵심**: `/auto "작업"` = Ralph 루프 + Ultrawork 병렬 실행 + Architect 검증

## ⚠️ 필수 실행 규칙 (CRITICAL)

**이 스킬이 활성화되면 반드시 아래 워크플로우를 실행하세요!**

### Phase 1: 옵션 라우팅 (있을 경우)

| 옵션 | 실행할 스킬 | 설명 |
|------|-------------|------|
| `--gdocs` | `Skill(skill="prd-sync")` | Google Docs PRD 동기화 |
| `--mockup` | `Skill(skill="mockup-hybrid", args="...")` | 목업 생성 |
| `--debate` | `Skill(skill="ultimate-debate", args="...")` | 3AI 토론 |
| `--research` | `Skill(skill="research", args="...")` | 리서치 모드 |

**옵션 체인 예시:**
```
/auto --gdocs --mockup "화면명"
→ Step 1: Skill(skill="prd-sync")
→ Step 2: Skill(skill="mockup-hybrid", args="화면명")
```

**옵션 실패 시**: 에러 메시지 출력하고 **절대 조용히 스킵하지 않음**

### Phase 2: 메인 워크플로우 (Ralph + Ultrawork)

**작업이 주어지면 (`/auto "작업내용"`):**

1. **Ralplan 호출** (복잡한 작업인 경우):
   ```
   Skill(skill="oh-my-claudecode:ralplan", args="작업내용")
   ```
   - Planner → Architect → Critic 합의 도달까지 반복

2. **Ultrawork 모드 활성화**:
   - 모든 독립적 작업은 **병렬 실행**
   - Task tool에 `run_in_background: true` 사용
   - 10+ 동시 에이전트 허용

3. **에이전트 라우팅**:

   | 작업 유형 | 에이전트 | 모델 |
   |----------|----------|------|
   | 간단한 조회 | `oh-my-claudecode:explore` | haiku |
   | 기능 구현 | `oh-my-claudecode:executor` | sonnet |
   | 복잡한 분석 | `oh-my-claudecode:architect` | opus |
   | UI 작업 | `oh-my-claudecode:designer` | sonnet |
   | 테스트 | `oh-my-claudecode:qa-tester` | sonnet |
   | 빌드 에러 | `oh-my-claudecode:build-fixer` | sonnet |

4. **Architect 검증** (완료 전 필수):
   ```
   Task(subagent_type="oh-my-claudecode:architect", model="opus",
        prompt="구현 완료 검증: [작업 설명]")
   ```

5. **완료 조건**:
   - Architect 승인 받음
   - 모든 TODO 완료
   - 빌드/테스트 통과 확인 (fresh evidence)

### Phase 3: 자율 발견 모드 (`/auto` 단독 실행)

작업이 명시되지 않으면 5계층 발견 시스템 실행:

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

- ❌ 옵션 실패 시 조용히 스킵
- ❌ Architect 검증 없이 완료 선언
- ❌ 증거 없이 "완료됨" 주장
- ❌ 테스트 삭제로 문제 해결

## 상세 워크플로우

추가 세부사항: `.claude/commands/auto.md`
