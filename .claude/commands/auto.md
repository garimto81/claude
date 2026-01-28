---
name: auto
version: 14.0.0
description: 통합 자율 완성 모드 (Ralplan + Critic + Ralph 항상 실행, 작업 유형 기반 분기)
aliases: [autopilot, ulw, ultrawork, ralph]
deprecated: false
---

# /auto - 통합 자율 완성 모드

> ⚠️ **다중 옵션 체인 실행 규칙 (CRITICAL)**
>
> **여러 특수 옵션이 있으면 순차적으로 모두 실행하세요!**
>
> ```
> /auto --gdocs --mockup --bnw "화면"
>       │         │
>       │         └─[2] Skill(skill="mockup", args="화면 --bnw")
>       └─[1] Skill(skill="prd-sync")
> ```
>
> ### 옵션별 스킬 매핑
>
> | 옵션 | 스킬 | 인자 추출 규칙 |
> |------|------|----------------|
> | `--mockup` | `mockup` | `--mockup` 뒤 모든 인자 (`--bnw`, `--force-html`, `--prd=...`, 이름) |
> | `--gdocs` | `prd-sync` | `--gdocs` 뒤 옵션들 (`--sync` 등) |
> | `--debate` | `ultimate-debate` | `--debate` 뒤 주제 |
> | `--research` | `research` | `--research` 뒤 키워드 |
>
> ### 실행 순서 (우선순위)
>
> 1. `--gdocs` (PRD 동기화 먼저)
> 2. `--mockup` (목업 생성)
> 3. `--debate` (토론)
> 4. `--research` (리서치)
>
> ### 예시: `/auto --gdocs --mockup --bnw "로그인"`
>
> ```python
> # Step 1: --gdocs 처리
> Skill(skill="prd-sync")
>
> # Step 2: --mockup --bnw "로그인" 처리
> Skill(skill="mockup", args="로그인 --bnw")
> ```
>
> ### 예시: `/auto --gdocs --sync --mockup "대시보드" --bnw --prd=PRD-0001`
>
> ```python
> # Step 1: --gdocs --sync 처리
> Skill(skill="prd-sync", args="--sync")
>
> # Step 2: --mockup "대시보드" --bnw --prd=PRD-0001 처리
> Skill(skill="mockup", args="대시보드 --bnw --prd=PRD-0001")
> ```

> **Ralph + Ultrawork + Ralplan + Codex 최적화 + Context Manager가 자동으로 적용되는 슈퍼모드입니다.**
> 별도 키워드 없이 `/auto "작업"` 하나로 모든 고급 기능이 활성화됩니다.

## 핵심 철학 (v14.0 변경)

```
/auto = Ralplan (항상) + Critic (항상) + Ralph (개발 작업 시) + Ultrawork (항상)
```

> ⚠️ **v14.0 핵심 변경**: 복잡도 계산 생략, Ralplan + Critic **항상 실행**

### 작업 유형 분류 (복잡도 대신)

| 작업 유형 | 키워드 | 워크플로우 |
|-----------|--------|------------|
| **문서 작업** | docs, README, 문서, PRD, 설계, 기획, md | Ralplan → Critic → 완료 |
| **개발 작업** | 그 외 모든 작업 | Ralplan → Critic → Ralph → Architect → 완료 |

### 통합된 기능

| 기능 | 적용 조건 | 설명 |
|------|----------|------|
| **Ralplan** | ✅ **항상** | Planner → Architect → Critic 합의 |
| **Critic** | ✅ **항상** | 계획 검토 및 품질 검증 |
| **Ralph** | 개발 작업만 | 완료까지 루프 + Architect 검증 |
| **Ultrawork** | 항상 | 병렬 에이전트 오케스트레이션 |
| **Token Optimizer** | 항상 | 캐싱/중복제거로 20-30% 절약 |
| **Auto Model Router** | 항상 | 모델 자동 선택 (복잡도 판단 X) |
| **Phase Gate** | 항상 | 파일 기반 세션 복원력 |
| **Context Manager** | 항상 | 인과관계 그래프 + Compaction 보호 |
| **Circuit Breaker** | 항상 | 3-Failure 에스컬레이션 |
| **Notepad Wisdom** | 완료 시 | HIGH importance 노드 내보내기 |

## 사용법

```bash
# 기본 사용 (모든 고급 기능 자동 적용)
/auto "로그인 기능 구현"
/auto "전체 테스트 통과시켜줘"
/auto "API 리팩토링"

# 지시 없이 실행 (자율 판단)
/auto

# 최대 반복 횟수 지정
/auto --max 10 "버그 수정"

# 세션 관리
/auto status              # 현재 상태
/auto stop                # 중지
/auto resume              # 재개

# 이전 세션 복원 (v12.0 신규)
/auto --restore           # 이전 세션 맥락 복원 후 계속
/auto --no-restore        # 이전 세션 무시하고 새로 시작
```

## 세션 복원 (/clear 후 맥락 유지)

**`/clear` 후에도 이전 세션의 핵심 맥락을 복원할 수 있습니다.**

### 복원 워크플로우

```
/clear (세션 초기화)
    │
    ▼
/auto "작업" 또는 /auto
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 이전 세션 확인                                               │
│   - .omc/context/context_graph.json 존재 여부               │
│   - HIGH importance 노드 3개 이상?                          │
│   - 미해결 에러 존재?                                        │
└─────────────────────────────────────────────────────────────┘
    │
    ├─ 복원 가능 ──────────────────────────────────────────────┐
    │                                                          │
    │  ┌────────────────────────────────────────────────────┐  │
    │  │ ## 이전 세션 발견                                   │  │
    │  │ - 세션 ID: ctx_20260128_143022                     │  │
    │  │ - 중요 노드: 8개                                    │  │
    │  │ - 미해결 에러: 1개                                  │  │
    │  │                                                    │  │
    │  │ 이전 세션을 복원하시겠습니까? [Y/n]                 │  │
    │  └────────────────────────────────────────────────────┘  │
    │                                                          │
    │  ├─ Yes ──▶ 복원 프롬프트 주입 후 작업 계속             │
    │  └─ No ───▶ 새 세션으로 시작                            │
    │
    └─ 복원 불가 ──▶ 새 세션으로 시작
```

### 복원되는 정보

| 항목 | 복원 | 설명 |
|------|:----:|------|
| **원본 요청** | ✅ | 사용자가 요청한 작업 |
| **핵심 결정사항** | ✅ | 결정 + 근거 + 거부된 대안 |
| **변경된 파일** | ✅ | 파일 경로 + 변경 유형 |
| **적용된 솔루션** | ✅ | 해결책 + 접근법 |
| **미해결 에러** | ✅ | 에러 메시지 + 상황 |
| **학습 내용** | ✅ | 패턴, 인사이트 |
| **인과관계 체인** | ✅ | A → B → C 흐름 |

### 복원 프롬프트 예시

```markdown
# 이전 세션 컨텍스트 복원

다음은 이전 세션에서 저장된 핵심 맥락입니다.

## 원본 요청
- API 인증 기능 구현

## 핵심 결정사항
- **JWT + Refresh Token 방식 채택**
  - 근거: 확장성과 stateless 특성이 적합
  - 거부된 대안: Session Cookie, OAuth Only

## 변경된 파일
- [CREATE] src/auth/jwt_handler.py: JWT 핸들러 구현

## ⚠️ 미해결 에러
- PyJWT import 실패
  - 상황: jwt_handler.py 실행 시

## 학습 내용
- 💡 JWT 의존성은 requirements.txt에 추가 필요

## 인과관계 흐름
- [request] API 인증 → [decision] JWT 채택 → [error] import 실패

## 다음 작업
- 위의 미해결 에러를 먼저 해결하세요
```

### 사용 예시

```python
from context_manager import check_restorable_session, get_restoration_prompt

# 1. 복원 가능 여부 확인
result = check_restorable_session()
if result["restorable"]:
    print(result["session_info"])
    # 복원 프롬프트 주입
    prompt = result["restoration_prompt"]

# 2. 간단히 복원 프롬프트만 가져오기
prompt = get_restoration_prompt()
if prompt:
    # 새 세션에 이전 맥락 주입
    pass
```

## 작업 유형 분류 로직 (v14.0 신규)

> **복잡도 계산 생략** - 단순히 문서 작업인지 개발 작업인지만 판단

### 문서 작업 키워드

```python
DOCS_KEYWORDS = [
    "docs", "documentation", "readme", "README",
    "문서", "PRD", "설계", "기획", "명세",
    ".md", "markdown", "설명", "가이드",
    "checklist", "체크리스트", "회의록", "정리"
]
```

### 워크플로우 분기

```
/auto "작업"
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 0: 작업 유형 분류 (단순 키워드 매칭)                    │
│   - 문서 키워드 포함? → 문서 작업                            │
│   - 그 외 → 개발 작업                                        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: RALPLAN (항상 실행)                                 │
│   - Planner: 계획 수립                                       │
│   - Architect: 계획 검토                                     │
│   - 합의 루프 (최대 5회)                                     │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: CRITIC 검증 (항상 실행)                             │
│   - 계획 품질 검토 (명확성, 검증 가능성, 완전성, 전체 맥락)  │
│   - OKAY 판정까지 반복                                       │
│   - 거부 시 → Phase 1로 복귀하여 계획 수정                   │
└─────────────────────────────────────────────────────────────┘
    │
    ├─ 문서 작업 ──────────────────────────────────────────────┐
    │                                                          │
    │  ┌────────────────────────────────────────────────────┐  │
    │  │ Phase 3a: WRITER 실행                               │  │
    │  │   - 문서 작성/수정 에이전트 호출                    │  │
    │  │   - 완료 후 바로 종료                               │  │
    │  └────────────────────────────────────────────────────┘  │
    │      │                                                   │
    │      ▼                                                   │
    │  완료: <promise>DOCS_COMPLETE</promise>                  │
    │                                                          │
    └─ 개발 작업 ──────────────────────────────────────────────┐
                                                               │
       ┌────────────────────────────────────────────────────┐  │
       │ Phase 3b: ULTRAWORK + RALPH 루프                    │  │
       │   - 병렬 에이전트 스폰                              │  │
       │   - 작업 완료까지 반복                              │  │
       │   - TODO 목록 0개 될 때까지                         │  │
       └────────────────────────────────────────────────────┘  │
           │                                                   │
           ▼                                                   │
       ┌────────────────────────────────────────────────────┐  │
       │ Phase 4: ARCHITECT 검증 (필수)                      │  │
       │   - Architect 에이전트로 완료 검증                  │  │
       │   - 승인 시 → 완료                                  │  │
       │   - 거부 시 → Phase 3b로 복귀                       │  │
       └────────────────────────────────────────────────────┘  │
           │                                                   │
           ▼                                                   │
       완료: <promise>TASK_COMPLETE</promise>                  │
```

### 워크플로우 요약 표

| 단계 | 문서 작업 | 개발 작업 |
|:----:|:---------:|:---------:|
| Phase 0 | 유형 분류 | 유형 분류 |
| Phase 1 | ✅ Ralplan | ✅ Ralplan |
| Phase 2 | ✅ Critic | ✅ Critic |
| Phase 3 | Writer | Ultrawork + Ralph |
| Phase 4 | - | ✅ Architect |
| 완료 태그 | `DOCS_COMPLETE` | `TASK_COMPLETE` |

## 위임 규칙 (CRITICAL)

**Claude는 오케스트레이터입니다. 직접 구현하지 않습니다.**

| Action | Claude | DELEGATE TO |
|--------|:------:|-------------|
| 파일 읽기 (컨텍스트) | ✓ | - |
| 진행 상황 추적 | ✓ | - |
| 에이전트 스폰 | ✓ | - |
| **모든 코드 변경** | ✗ | executor-low/executor/executor-high |
| **UI 작업** | ✗ | designer/designer-high |
| **문서 작성** | ✗ | writer |

**예외 경로**: `.omc/`, `.claude/`, `CLAUDE.md`, `AGENTS.md`는 직접 수정 가능

## 스마트 모델 라우팅 (Auto Model Router)

**Codex 최적화**: `model_router.py`가 작업 복잡도를 자동 분석하여 최적 모델 선택

| 작업 복잡도 | Tier | 에이전트 예시 | 자동 감지 키워드 |
|-------------|------|---------------|-----------------|
| 단순 조회 | LOW (Haiku) | architect-low, executor-low, explore | lookup, find, search, typo |
| 일반 구현 | MEDIUM (Sonnet) | executor, designer, researcher | implement, add, fix, update |
| 복잡한 분석 | HIGH (Opus) | architect, executor-high, planner | refactor, migrate, architecture |

```python
# 자동 모델 라우팅 (model_router.py 사용)
from model_router import route_model
result = route_model("Refactor authentication system", file_count=10)
# → {"model": "opus", "complexity": "high", "confidence": 0.85}

# 수동 지정 (필요 시)
Task(subagent_type="oh-my-claudecode:executor-low", model="haiku", prompt="...")
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="...")
Task(subagent_type="oh-my-claudecode:architect", model="opus", prompt="...")
```

## 사용 가능한 에이전트

| Domain | LOW (Haiku) | MEDIUM (Sonnet) | HIGH (Opus) |
|--------|-------------|-----------------|-------------|
| **분석** | `architect-low` | `architect-medium` | `architect` |
| **실행** | `executor-low` | `executor` | `executor-high` |
| **탐색** | `explore` | `explore-medium` | `explore-high` |
| **리서치** | `researcher-low` | `researcher` | - |
| **프론트엔드** | `designer-low` | `designer` | `designer-high` |
| **문서** | `writer` | - | - |
| **시각** | - | `vision` | - |
| **계획** | - | - | `planner`, `critic`, `analyst` |
| **테스트** | - | `qa-tester` | `qa-tester-high` |
| **보안** | `security-reviewer-low` | - | `security-reviewer` |
| **빌드** | `build-fixer-low` | `build-fixer` | - |
| **TDD** | `tdd-guide-low` | `tdd-guide` | - |
| **코드리뷰** | `code-reviewer-low` | - | `code-reviewer` |

## 백그라운드 실행 규칙

**Background (`run_in_background: true`):**
- 패키지 설치: npm install, pip install
- 빌드: npm run build, make, tsc
- 테스트: npm test, pytest

**Foreground (블로킹):**
- 상태 확인: git status, ls
- 파일 읽기 (수정은 위임)
- 단순 명령

## 완료 조건 (ZERO TOLERANCE)

작업 완료 전 **반드시** 확인:

- [ ] **TODO**: pending/in_progress 작업 0개
- [ ] **기능**: 요청된 모든 기능 동작
- [ ] **테스트**: 모든 테스트 통과
- [ ] **에러**: 미해결 에러 0개
- [ ] **Architect**: 검증 통과

**하나라도 미충족 시 → 계속 작업**

## Architect 검증 (필수)

완료 주장 전 반드시 Architect 검증:

```python
Task(
    subagent_type="oh-my-claudecode:architect",
    model="opus",
    prompt="다음 구현이 완료되었는지 검증하세요: [작업 설명]"
)
```

- **승인** → `<promise>TASK_COMPLETE</promise>` 출력
- **거부** → 문제 수정 후 재검증

## Context 관리 + Token Optimizer

**Codex 최적화**: `token_optimizer.py`가 중복 요청 캐싱으로 20-30% 토큰 절약

| 사용량 | 상태 | 액션 |
|--------|------|------|
| 0-60% | Safe | 정상 작업 |
| 60-80% | Warning | 체크포인트 준비 |
| 80-90% | Critical | 진행 중 작업 완료 후 정리 |
| **90%+** | Emergency | 즉시 /commit → 세션 종료 |

### Token Optimizer 기능

```python
# 캐시 저장소: .omc/cache/token_cache.json
# 캐시 TTL: 5분 (조절 가능)

# 자동 캐싱 대상:
# - Read: 동일 파일 읽기 요청
# - Grep: 동일 패턴 검색
# - Glob: 동일 패턴 파일 탐색

# 통계 확인
from token_optimizer import TokenOptimizer
optimizer = TokenOptimizer()
stats = optimizer.get_stats()
# → {"cache_hits": 45, "tokens_saved": 12500, "hit_rate_percent": 35.2}
```

## 옵션

| 옵션 | 설명 |
|------|------|
| `--max N` | 최대 N회 반복 |
| `--eco` | 토큰 절약 모드 (Haiku 우선) |
| `--no-critic` | Critic 검증 스킵 (긴급 작업용, 권장하지 않음) |
| `--dry-run` | 계획만 출력, 실행 안함 |
| `--mockup` | 목업 생성 모드 (하위 옵션 지원) |
| `--debate` | 3AI 토론 모드 |
| `--gdocs` | Google Docs 변환 모드 |
| `--research` | 리서치 모드 |

## 특수 기능 (라우팅)

`/auto`에서 특수 옵션 감지 시 해당 스킬로 라우팅됩니다.

### --mockup (목업 생성)

`/auto --mockup` 사용 시 `/mockup` 스킬의 모든 옵션을 지원합니다.

```bash
# 기본 사용 (자동 선택)
/auto --mockup "로그인 화면"

# Black & White 모드 (HTML 와이어프레임)
/auto --mockup "대시보드" --bnw

# 강제 HTML 또는 Stitch
/auto --mockup "인증 흐름" --force-html
/auto --mockup "프레젠테이션용 UI" --force-hifi

# PRD 연결
/auto --mockup "인증 화면" --bnw --prd=PRD-0003

# 다중 화면
/auto --mockup "온보딩 플로우" --bnw --screens=3 --flow
```

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--bnw` | Black & White 모드 (자동 선택) | - |
| `--force-html` | 강제 HTML 와이어프레임 | - |
| `--force-hifi` | 강제 Stitch API (고품질) | - |
| `--prd=PRD-NNNN` | PRD 연결 (자동 고품질 선택) | - |
| `--screens=N` | 생성할 화면 수 (1-5) | 1 |
| `--flow` | 흐름 다이어그램 포함 | - |
| `--style=TYPE` | wireframe \| detailed | wireframe |

> 💡 상세 가이드: `/mockup --help` 또는 `.claude/commands/mockup.md`

### --debate (3AI 토론)

```bash
/auto --debate "주제"
```

### --gdocs (Google Docs 변환)

```bash
/auto --gdocs             # 현재 디렉토리 PRD 변환
/auto --gdocs --sync      # 동기화 모드
```

> 🚨 **CRITICAL: WebFetch 사용 금지**
>
> `--gdocs` 옵션 또는 Google Docs URL 감지 시:
>
> ```python
> # ❌ 절대 하면 안 됨 (401 에러 발생)
> WebFetch(url="https://docs.google.com/document/d/...")
>
> # ✅ 반드시 이렇게 해야 함
> Bash(command="cd C:\\claude && python scripts/prd_sync.py check")
> # 또는
> Bash(command="cd C:\\claude && python -m lib.google_docs convert 파일.md")
> ```
>
> **이유**: Google 서비스는 OAuth 2.0 인증 필수, WebFetch는 인증 토큰 전달 불가

### --research (리서치)

```bash
/auto --research "키워드"
```

## Phase Gate 세션 복원 (Codex 최적화)

**Codex 최적화**: `phase_gate.py`가 파일 기반 상태 저장으로 세션 복원력 80% 향상

```
Phase 흐름: INIT → PLAN → EXECUTE → VERIFY → COMPLETE
                  ↓         ↓
               PAUSED     FAILED → INIT (재시작)
```

| Phase | 설명 | 자동 저장 |
|-------|------|----------|
| **INIT** | 작업 분석 | 요청, 복잡도 |
| **PLAN** | 계획 수립 | 계획 결과, 합의 |
| **EXECUTE** | 실행 | 완료 작업, 변경 파일 |
| **VERIFY** | Architect 검증 | 검증 결과 |
| **COMPLETE** | 완료 | 최종 요약 |

```python
# Phase 상태 파일: .omc/state/phase/{session_id}.json
# 세션 복원
from phase_gate import restore_session, get_active_sessions

# 활성 세션 목록
active = get_active_sessions()

# 세션 복원
manager = restore_session("phase_20260128_143022")
print(manager.get_summary())  # 복원 정보 출력
```

## 실행 흐름 요약 (v14.0 업데이트)

```
/auto "작업"
    │
    ├─[0] 이전 세션 복원 확인 (v12.1)
    │      └─ check_restorable_session()
    │
    ├─[1] 통합 상태 초기화
    │      └─ UnifiedStateManager 생성
    │      └─ start_workflow("auto")
    │
    ├─[2] Phase Gate 초기화
    │      └─ state.set_phase("INIT")
    │
    ├─[3] 작업 유형 분류 (v14.0 변경)
    │      └─ classify_task_type(description)
    │      └─ 문서 작업 vs 개발 작업 판단
    │      └─ 모델 자동 선택 (복잡도 판단 X)
    │
    ├─[4] Ralplan (항상 실행) ← v14.0 변경
    │      └─ Planner → Architect 합의 루프
    │      └─ state.set_phase("PLAN")
    │
    ├─[5] Critic 검증 (항상 실행) ← v14.0 신규
    │      └─ 계획 품질 검토
    │      └─ OKAY 판정까지 반복
    │      └─ 거부 시 → [4]로 복귀
    │
    ├─[분기] 작업 유형에 따른 분기
    │
    ├─[문서 작업] ──────────────────────────────────────────────┐
    │                                                          │
    │  ├─[6a] Writer 에이전트 호출                             │
    │  │       └─ 문서 작성/수정                               │
    │  │                                                       │
    │  └─[7a] 완료                                             │
    │         └─ <promise>DOCS_COMPLETE</promise>              │
    │                                                          │
    └─[개발 작업] ──────────────────────────────────────────────┐
                                                               │
       ├─[6b] Ultrawork + Ralph 루프                           │
       │       └─ 병렬 에이전트 스폰                           │
       │       └─ 작업 완료까지 반복                           │
       │       └─ Circuit Breaker 체크                         │
       │       └─ state.set_phase("EXECUTE")                   │
       │                                                       │
       ├─[7b] Architect 검증 (필수)                            │
       │       └─ state.set_phase("VERIFY")                    │
       │       └─ 거부 시 → [6b]로 복귀                        │
       │                                                       │
       ├─[8] Notepad Wisdom 내보내기                           │
       │       └─ ctx.export_to_wisdom(task_name)              │
       │                                                       │
       └─[9] 완료                                              │
              └─ <promise>TASK_COMPLETE</promise>              │
           └─ state.complete_workflow(success=True)
           └─ <promise>TASK_COMPLETE</promise>
```

## 레거시 지원

기존 키워드도 `/auto`로 라우팅됩니다:

| 기존 키워드 | 동작 |
|-------------|------|
| `ralph: 작업` | → `/auto "작업"` |
| `ulw: 작업` | → `/auto "작업"` |
| `ultrawork: 작업` | → `/auto "작업"` |
| `ralplan: 작업` | → `/auto "작업"` (계획 모드 강제) |

## Codex 최적화 모듈 위치

| 모듈 | 경로 | 기능 |
|------|------|------|
| **Token Optimizer** | `.claude/hooks/token_optimizer.py` | 캐싱/중복제거 |
| **Model Router** | `.claude/skills/auto-workflow/scripts/model_router.py` | 자동 모델 선택 |
| **Phase Gate** | `.claude/skills/auto-workflow/scripts/phase_gate.py` | 세션 복원 |
| **Context Manager** | `.claude/skills/auto-workflow/scripts/context_manager.py` | 인과관계 추적 |

### 예상 효과 (OpenAI Codex 분석 기반)

| 최적화 | 예상 절감 | 적용 대상 |
|--------|----------|----------|
| Token Caching | 20-30% 토큰 | Read, Grep, Glob |
| Auto Model Routing | 15-20% 비용 | 모든 에이전트 호출 |
| Phase Handoff | 80% 복원력 | 세션 중단 시 |
| Context Manager | 90%+ 인과관계 보존 | Compaction 시 |

---

## Circuit Breaker (v13.0 신규)

**3-Failure 에스컬레이션 패턴으로 무한 루프를 방지합니다.**

### 동작 원리

```
에러 발생
    │
    ├─ 1차 실패 ─▶ RETRY (동일 접근법 재시도)
    │
    ├─ 2차 실패 ─▶ ALTERNATE_APPROACH (다른 방법 시도)
    │
    └─ 3차 실패 ─▶ ESCALATE_TO_ARCHITECT (Architect 호출)
```

### 사용법

```python
from context_manager import ContextManager

ctx = ContextManager()

# 에러 발생 시
error_id = ctx.record_error("빌드 실패: TypeScript 에러")
action = ctx.record_failure("build_task", error_id)

if action == "RETRY":
    # 동일 방법 재시도
    pass
elif action == "ALTERNATE_APPROACH":
    # 다른 접근법 시도
    pass
elif action == "ESCALATE_TO_ARCHITECT":
    # Architect 에이전트 호출
    summary = ctx.get_escalation_summary()
    # Task(subagent_type="oh-my-claudecode:architect", prompt=summary)
```

### Architect 에스컬레이션 프롬프트

```markdown
## 에스컬레이션 요청

3회 연속 실패로 Architect 검토가 필요합니다.

### 실패 이력
- **task_key**: build_task
- **시도 횟수**: 3
- **에러들**:
  1. TypeScript 에러: Property 'x' does not exist
  2. TypeScript 에러: Cannot find module 'y'
  3. TypeScript 에러: Type 'A' is not assignable to 'B'

### 관련 컨텍스트
[인과관계 체인 요약]

### 요청
근본 원인을 분석하고 해결 방안을 제시해주세요.
```

---

## Context Manager (v12.0 신규)

**인과관계 기반 컨텍스트 관리로 Compaction 시에도 핵심 정보를 보존합니다.**

### 노드 유형

| 유형 | 중요도 | 설명 |
|------|--------|------|
| **REQUEST** | HIGH | 사용자 요청 (항상 보존) |
| **DECISION** | HIGH | 결정 사항 + 근거 |
| **ERROR** | HIGH | 발생한 에러 |
| **SOLUTION** | HIGH | 해결책 |
| **LEARNING** | HIGH | 학습 내용/패턴 |
| **ANALYSIS** | MEDIUM | 분석 결과 |
| **FILE** | MEDIUM | 파일 변경 |
| **REJECTED** | LOW | 거부된 대안 |

### 엣지 유형 (인과관계)

```
causes      : A가 B를 유발
leads_to    : A가 B로 이어짐
resolved_by : A(에러)가 B(솔루션)로 해결
blocks      : A가 B를 차단
depends_on  : A가 B에 의존
rejects     : A가 B를 거부 (대안 기록)
```

### 사용법

```python
from context_manager import ContextManager, Importance

# 컨텍스트 생성
ctx = ContextManager()

# 요청 기록
req_id = ctx.record_request("API 인증 기능 구현")

# 분석 기록
analysis_id = ctx.record_analysis(
    "JWT 토큰 방식이 적합함",
    caused_by=req_id,
    importance=Importance.HIGH
)

# 결정 기록
decision_id = ctx.record_decision(
    "JWT + Refresh Token 방식 채택",
    rationale="확장성과 stateless 특성이 적합",
    caused_by=analysis_id,
    alternatives=["Session Cookie", "OAuth Only"]
)

# 파일 변경 기록
file_id = ctx.record_file_change(
    "src/auth/jwt_handler.py",
    "create",
    "JWT 핸들러 구현",
    caused_by=decision_id
)

# 에러 기록
error_id = ctx.record_error(
    "PyJWT import 실패",
    caused_by=file_id
)

# 솔루션 기록
solution_id = ctx.record_solution(
    "pip install PyJWT 실행",
    resolves=error_id,
    approach="의존성 설치"
)

# 학습 기록
learning_id = ctx.record_learning(
    "JWT 의존성은 requirements.txt에 추가 필요",
    source=solution_id
)

# Compact Summary 생성 (Compaction 생존용)
summary = ctx.generate_compact_summary()
```

### Compact Summary 구조

```markdown
# Context Compact Summary
Session: ctx_20260128_143022

## Original Request
- API 인증 기능 구현

## Key Decisions
- **JWT + Refresh Token 방식 채택**
  - Rationale: 확장성과 stateless 특성이 적합

## Changed Files
- [CREATE] src/auth/jwt_handler.py: JWT 핸들러 구현

## Solutions Applied
- ✅ pip install PyJWT 실행
  - Approach: 의존성 설치

## Learnings
- 💡 JWT 의존성은 requirements.txt에 추가 필요

## Causality Chains
- [request] API 인증 기능 → [analysis] JWT 적합 → [decision] JWT 채택...
```

### 통계 조회

```python
stats = ctx.get_stats()
# {
#   "session_id": "ctx_20260128_143022",
#   "total_nodes": 15,
#   "total_edges": 12,
#   "nodes_by_type": {"request": 1, "decision": 3, "file": 5, ...},
#   "nodes_by_importance": {"high": 8, "medium": 5, "low": 2},
#   "unresolved_errors": 0,
#   "high_importance": 8
# }
```

### 저장 위치

```
.omc/context/
├── context_graph.json    # 인과관계 그래프
├── compact_summary.md    # Compaction 생존용 요약
└── archive/              # 정리된 노드 아카이브
    └── archive_YYYYMMDD_HHMMSS.json
```

### 파일 크기 제한 (자동 정리)

**JSON 파일 비대화 방지를 위한 자동 정리 메커니즘:**

| 제한 항목 | 기본값 | 설명 |
|-----------|--------|------|
| **MAX_NODES** | 500 | 최대 노드 수 |
| **MAX_EDGES** | 1000 | 최대 엣지 수 |
| **MAX_FILE_SIZE_KB** | 1024 (1MB) | 최대 파일 크기 |
| **TTL_HOURS** | 24 | 노드 생존 시간 |
| **CLEANUP_THRESHOLD** | 80% | 정리 시작 임계값 |

#### 자동 정리 로직

```
저장 시 자동 체크:
    │
    ├─ 노드 수 > 400 (80%)? ──────┐
    ├─ 엣지 수 > 800 (80%)? ──────┼──▶ 정리 트리거
    └─ 파일 크기 > 820KB (80%)? ──┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│ 정리 우선순위:                                               │
│   1. TTL 만료 + LOW importance → 즉시 삭제                  │
│   2. TTL 만료 + MEDIUM (오버플로우 시) → 삭제               │
│   3. LOW importance (TTL 무관, 오래된 순) → 삭제            │
│   ⚠️ HIGH importance → 절대 삭제 안함                       │
└─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         아카이브 후 삭제
                  (.omc/context/archive/*.json)
```

#### 강제 정리 API

```python
# 파일 크기 통계 조회
file_stats = ctx.get_file_stats()
# {
#   "file_size_kb": 245.32,
#   "max_file_size_kb": 1024,
#   "file_usage_percent": 24.0,
#   "node_count": 150,
#   "max_nodes": 500,
#   "node_usage_percent": 30.0,
#   ...
# }

# LOW importance 노드 강제 정리
result = ctx.force_cleanup(keep_high_only=False)
# {"removed_nodes": 25, "removed_edges": 40, ...}

# HIGH만 남기고 전부 정리 (긴급 상황)
result = ctx.force_cleanup(keep_high_only=True)
```

---

## Notepad Wisdom 연동 (v13.0 신규)

**HIGH importance 노드를 재활용 가능한 지식으로 내보냅니다.**

### 저장 위치

```
.omc/notepads/{plan-name}/
├── learnings.md    # LEARNING 노드
├── decisions.md    # DECISION 노드 (rationale 포함)
└── issues.md       # ERROR + SOLUTION 쌍
```

### 사용법

```python
from context_manager import ContextManager

ctx = ContextManager()

# 작업 완료 후 지식 내보내기
result = ctx.export_to_wisdom("feature-auth")
# {"learnings": 3, "decisions": 2, "issues": 1}
```

### 자동 내보내기

`/auto` 완료 시 자동으로 Notepad Wisdom에 내보내기가 실행됩니다:

```
Phase 5 완료
    │
    ├─ Architect 검증 통과
    │
    └─ export_to_wisdom(task_name) 자동 실행
```

---

## 통합 상태 관리 (v13.0 신규)

**모든 컴포넌트 상태를 단일 진입점으로 관리합니다.**

### 상태 파일 구조

```
.omc/state/
├── unified-session.json    # 통합 세션 상태
├── phase/                  # Phase Gate 상태
│   └── {session_id}.json
├── circuit-breaker.json    # Circuit Breaker 상태
└── ...
```

### unified-session.json 구조

```json
{
  "session_id": "unified_20260128_150000",
  "workflow": {
    "mode": "auto",
    "iteration": 3,
    "max_iterations": 10,
    "status": "running"
  },
  "components": {
    "context_manager": {"active": true},
    "phase_gate": {"active": true, "current_phase": "EXECUTE"},
    "circuit_breaker": {"active": true, "failures": {}},
    "verification": {"checks": {"BUILD": {"passed": true}}}
  }
}
```

### 사용법

```python
from unified_state import UnifiedStateManager

state = UnifiedStateManager()

# 워크플로우 시작
state.start_workflow("auto", max_iterations=10)

# Phase 설정
state.set_phase("EXECUTE")

# 상태 조회
status = state.get_status()
```

---

## Context Manager 워크플로우

```
/auto "작업"
    │
    ├─[0] Context Manager 초기화
    │      └─ record_request("작업")
    │      └─ .omc/context/context_graph.json 생성
    │
    ├─[1] 작업 분석 + Context 기록
    │      └─ record_analysis(분석 결과)
    │      └─ record_decision(결정, rationale, alternatives)
    │
    ├─[2] 실행 중 Context 기록
    │      └─ record_file_change(파일, 변경 유형)
    │      └─ record_error(에러 발생 시)
    │      └─ record_solution(해결 시)
    │
    ├─[3] Context 참조
    │      └─ get_unresolved_errors() → 미해결 에러 확인
    │      └─ get_related_nodes() → 인과관계 추적
    │
    ├─[4] Compaction 보호
    │      └─ generate_compact_summary()
    │      └─ HIGH importance 노드 우선 보존
    │
    └─[5] 완료 시 Learning 기록
           └─ record_learning(패턴, 인사이트)
```

---

**Version 14.0.0**: 복잡도 계산 생략, Ralplan + Critic 항상 실행, 작업 유형 분류 (문서 vs 개발)
**Version 13.0.0**: OMC 통합 (Circuit Breaker + Notepad Wisdom + 통합 상태 관리 + Architect 필수 검증)
**Version 12.1.0**: 세션 복원 기능 추가 (/clear 후 맥락 유지)
**Version 12.0.0**: Context Manager 통합 (인과관계 그래프 + Compaction 보호 + 자동 정리)
**Version 11.0.0**: Codex Agent Loop 최적화 통합 (Token, Model, Phase)
**Version 10.0.0**: Ralph + Ultrawork + Ralplan 통합 슈퍼모드로 전환
