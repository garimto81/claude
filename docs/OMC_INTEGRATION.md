# OMC Integration Guide

**Version**: 1.0.0
**Last Updated**: 2026-01-29

로컬 커맨드/스킬과 oh-my-claudecode(OMC) 플러그인 통합 가이드입니다.

---

## 개요

### 시스템 구조

```
사용자 입력: /auto "작업"
       │
       ▼
┌─────────────────────────────┐
│  .claude/skills/auto/       │
│  SKILL.md (트리거 + 지시)   │
│  omc_delegate: autopilot    │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  OMC Plugin                 │
│  oh-my-claudecode:autopilot │
│  (32개 에이전트 활용)        │
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Ralph 루프 (5개 조건)      │
│  - TODO == 0               │
│  - 기능 동작                │
│  - 테스트 통과              │
│  - 에러 == 0               │
│  - Architect 승인          │
└─────────────────────────────┘
```

---

## OMC 모드

| 모드 | 트리거 | 설명 |
|------|--------|------|
| **autopilot** | `/auto`, "autopilot" | 전체 자율 실행 (Ralplan + Ultrawork + Ralph) |
| **ralph** | "ralph", "don't stop" | 5개 조건 충족까지 반복 |
| **ultrawork** | "ulw", "parallel" | 최대 병렬 실행 |
| **ralplan** | "ralplan" | Planner-Architect-Critic 합의 |
| **ecomode** | "eco", "budget" | 토큰 효율적 실행 |

---

## 스킬 매핑

### 핵심 스킬

| 로컬 커맨드 | OMC 스킬 | 활성화 기능 |
|-------------|----------|-------------|
| `/auto` | `autopilot` | Ralplan + Ultrawork + Ralph |
| `/check` | `ultraqa` | QA 사이클 (테스트-수정-반복) |
| `/debug` | `analyze` | 가설-검증 디버깅 |
| `/tdd` | `tdd` | Red-Green-Refactor |

### 직접 실행 스킬

| 로컬 커맨드 | 실행 방식 |
|-------------|----------|
| `/commit` | Git 워크플로우 직접 실행 |
| `/issue` | GitHub CLI 직접 실행 |
| `/create pr` | gh pr create 직접 실행 |

---

## 에이전트 티어

### 32개 에이전트 분류

| 티어 | 모델 | 에이전트 |
|------|------|----------|
| **LOW** | haiku | explore, executor-low, writer, researcher-low |
| **MEDIUM** | sonnet | executor, designer, qa-tester, build-fixer |
| **HIGH** | opus | architect, planner, critic, executor-high |

### 작업별 권장 에이전트

| 작업 | 에이전트 | 이유 |
|------|----------|------|
| 파일 검색 | `explore` (haiku) | 빠른 조회 |
| 기능 구현 | `executor` (sonnet) | 균형잡힌 성능 |
| 복잡한 디버깅 | `architect` (opus) | 깊은 분석 필요 |
| UI 작업 | `designer` (sonnet) | 디자인 감각 |
| 계획 수립 | `planner` (opus) | 전략적 사고 |

---

## Ralph 루프

### 5개 완료 조건

```
┌─────────────────────────────────────────────┐
│            Ralph 루프 체크리스트             │
├─────────────────────────────────────────────┤
│  ☐ 조건 1: TODO == 0 (모든 태스크 완료)     │
│  ☐ 조건 2: 기능 동작 (요청 기능 작동 확인)   │
│  ☐ 조건 3: 테스트 통과 (관련 테스트 green)  │
│  ☐ 조건 4: 에러 == 0 (빌드/린트 클린)       │
│  ☐ 조건 5: Architect 승인 (품질 검증)       │
├─────────────────────────────────────────────┤
│  ANY 실패 → 자동 재시도                      │
│  ALL 통과 → 완료 선언                        │
└─────────────────────────────────────────────┘
```

### 검증 순서

1. **TODO 확인**: `TaskList` 도구로 pending 태스크 확인
2. **기능 테스트**: 구현된 기능 수동/자동 검증
3. **테스트 실행**: `pytest`, `npm test` 등 실행
4. **빌드 확인**: `ruff check`, `tsc`, `npm run build`
5. **Architect 호출**:
   ```
   Task(subagent_type="oh-my-claudecode:architect",
        model="opus",
        prompt="검증: [작업 설명]")
   ```

---

## 서브프로젝트 설정

### 심볼릭 링크 생성

```powershell
# 관리자 권한으로 실행
$subprojects = @(
    "automation_hub",
    "archive-analyzer",
    "wsoptv_ott"
)

foreach ($proj in $subprojects) {
    $skillsPath = "C:\claude\$proj\.claude\skills"
    $targetPath = "C:\claude\.claude\skills"

    if (-not (Test-Path $skillsPath)) {
        New-Item -ItemType Directory -Path "C:\claude\$proj\.claude" -Force
        New-Item -ItemType SymbolicLink -Path $skillsPath -Target $targetPath
    }
}
```

---

## 트러블슈팅

### /auto가 OMC 기능을 활성화하지 않음

1. **SKILL.md 확인**: `omc_delegate` 필드 존재 여부
2. **심볼릭 링크 확인**: 서브프로젝트의 `.claude/skills` 연결 상태
3. **OMC 플러그인 확인**: `/oh-my-claudecode:doctor` 실행

### Ralph 루프가 종료되지 않음

1. **TODO 확인**: `TaskList`로 미완료 태스크 확인
2. **빌드 에러 확인**: `ruff check`, `tsc` 실행
3. **Architect 거부 이유 확인**: 로그 검토

### 옵션이 조용히 스킵됨

**금지됨**: 명시적 옵션(`--gdocs`, `--mockup`)은 실패 시 에러 출력 필수

---

## Best Practices

1. **짧은 커맨드 사용**: `/auto`, `/commit`
2. **복잡한 작업은 autopilot**: Ralph 루프로 완료 보장
3. **간단한 작업은 직접 실행**: 단일 파일 수정 등
4. **서브프로젝트는 심볼릭 링크**: 스킬 복제 금지
5. **Architect 검증 필수**: 완료 선언 전 반드시 승인 받기
