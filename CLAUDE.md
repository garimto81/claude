# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 5.2.0 | **Context**: Windows, PowerShell, Root: `D:\AI\claude01`

---

## 환경 요구사항

| 항목 | 값 |
|------|-----|
| **Python** | 3.11+ |
| **API Key** | `ANTHROPIC_API_KEY` 환경변수 필수 |
| **Git** | 2.30+ |

---

## 기본 규칙

| 규칙 | 내용 |
|------|------|
| **언어** | 한글 출력. 기술 용어(code, GitHub)는 영어 |
| **경로** | 절대 경로만. `D:\AI\claude01\...` |
| **충돌** | 지침 충돌 시 → **사용자에게 질문** (임의 판단 금지) |

---

## 출력 스타일

**코드 수정**: 내용 보여주지 않음. 요약만.

```
✅ 파일: src/auth.py (+15/-3)
   - 토큰 검증 로직 추가
   - 만료 시간 체크
```

**응답 구조**: 논리 중심

```
1. 문제/목표 (무엇을)
2. 접근법 (어떻게)
3. 결과 (완료/다음 단계)
```

---

## 작업 방법

```
사용자 요청 → /work "요청 내용" → 자동 완료
```

| 요청 유형 | 처리 |
|-----------|------|
| 기능/리팩토링 | PRE_WORK → IMPL → FINAL_CHECK |
| 버그 수정 | PRE_WORK(light) → IMPL → FINAL_CHECK |
| 문서 수정 | 이슈 → 직접 커밋 |
| 질문 | 직접 응답 |

### 워크플로우 인과관계

```
PRE_WORK ──────────────→ IMPL ──────────────→ FINAL_CHECK
    │                      │                      │
    ├─ OSS 검색           ├─ 이슈/브랜치 생성    ├─ E2E 테스트
    ├─ 중복 확인          ├─ TDD 구현           ├─ Phase 3~5 자동
    └─ Make vs Buy        └─ 커밋               └─ Phase 6 사용자 확인
```

### Phase Pipeline

| Phase | 핵심 | Validator |
|-------|------|-----------|
| 0 | PRD 생성 | `validate-phase-0.ps1` |
| 0.5 | Task 분해 | `validate-phase-0.5.ps1` |
| 1 | 구현 + 테스트 | `validate-phase-1.ps1` |
| 2 | 테스트 통과 | `validate-phase-2.ps1` |
| 2.5 | 코드 리뷰 | `/parallel review` |
| 3 | 버전 결정 | Conventional Commits |
| 4 | PR 생성 | `validate-phase-4.ps1` |
| 5 | E2E + Security | `validate-phase-5.ps1` |
| 6 | 배포 | 사용자 확인 필수 |

**자동 진행 중지**: MAJOR 버전, Critical 보안 취약점, 배포, 3회 실패

### 단계별 지침 (필수 참조)

| 단계 | Phase | 지침 파일 | 트리거 |
|------|-------|----------|--------|
| **문서 작성** | 0, 0.5 | `docs/workflows/PHASE_DOC.md` | PRD, 설계, Task 분해 |
| **코드 구현** | 1~6 | `docs/workflows/PHASE_CODE.md` | 구현, TDD, 테스트, 배포 |

> ⚠️ **각 단계 시작 시 해당 지침 파일을 먼저 읽고 진행**

---

## 핵심 규칙 (Hook 강제)

| 규칙 | 위반 시 | 해결 |
|------|---------|------|
| main 브랜치 수정 금지 | **차단** | `git checkout -b feat/issue-N-desc` |
| 테스트 먼저 (TDD) | 경고 | Red → Green → Refactor |
| 상대 경로 금지 | 경고 | 절대 경로 사용 |

**main에서 허용되는 파일**: `CLAUDE.md`, `.claude/`, `docs/`, `README.md`, `CHANGELOG.md`, `.gitignore`

---

## 문제 해결

```
문제 → WHY(원인) → WHERE(영향 범위) → HOW(해결) → 수정
```

**즉시 수정 금지.** 원인 파악 → 유사 패턴 검색 → 구조적 해결.

---

## 커맨드

| 커맨드 | 용도 |
|--------|------|
| `/work "내용"` | 전체 워크플로우 |
| `/issue fix #N` | 이슈 해결 |
| `/issue create` | 이슈 생성 |
| `/commit` | 커밋 |
| `/tdd` | TDD 워크플로우 |
| `/check` | 린트 + 테스트 |
| `/parallel dev` | 병렬 개발 |

전체: `.claude/commands/`

---

## 빌드 & 테스트

```powershell
pytest tests/test_file.py -v                    # 단일 파일
pytest tests/test_file.py::test_func -v         # 단일 함수
ruff check src/ && black --check src/           # 린트
mypy src/                                       # 타입 체크
npx playwright test                             # E2E
```

---

## 코드 표준

### 명명 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| 변수/함수 | snake_case (Python), camelCase (JS/TS) | `user_list`, `calculateTotal` |
| 클래스 | PascalCase | `UserService` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Boolean | is/has/can 접두사 | `is_active`, `hasPermission` |

### 코드 원칙

| 원칙 | 설명 |
|------|------|
| **KISS** | 불필요한 복잡성 제거 |
| **DRY** | 중복 코드 → 함수/모듈 분리 |
| **단일 책임** | 함수 20-30줄 초과 시 분리 |
| **Early Return** | 예외 먼저 처리 후 반환 |

### 시큐어 코딩

| 항목 | 필수 | 금지 |
|------|------|------|
| 입력 검증 | 서버단 검증 | 클라이언트만 의존 |
| SQL | ORM, PreparedStatement | 동적 쿼리 |
| 민감정보 | 환경변수, Secret Manager | 코드 하드코딩 |
| 에러 메시지 | 일반 메시지 | Stack Trace 노출 |

---

## 안전 규칙

### Crash Prevention (필수)

```powershell
# ❌ 금지 (120초 초과 → 크래시)
pytest tests/ -v --cov                # 대규모 테스트
npm install && npm run build          # 체인 명령

# ✅ 권장
pytest tests/test_a.py -v             # 개별 실행
# 또는 run_in_background: true
```

### 보호 대상

- `pokervod.db` 스키마 변경 금지 (`qwen_hand_analysis` 소유)

---

## Multi-Agent 아키텍처

```
src/agents/
├── config.py             # 모델 티어링, 에이전트 설정
├── parallel_workflow.py  # Fan-Out/Fan-In 병렬 실행
├── dev_workflow.py       # 병렬 개발 (Architect/Coder/Tester/Docs)
└── test_workflow.py      # 병렬 테스트 (Unit/Integration/E2E/Security)
```

**모델 티어링**: supervisor/lead/coder/reviewer → `claude-sonnet-4`, validator → `claude-haiku-3`

---

## 참조

| 문서 | 용도 |
|------|------|
| `docs/WORKFLOW_REFERENCE.md` | 상세 워크플로우 |
| `docs/AGENTS_REFERENCE.md` | 에이전트 목록 |
| `.claude/commands/` | 커맨드 상세 |
| `.claude/skills/` | 스킬 (자동 트리거) |

---

## 금지 사항

- ❌ Phase validator 없이 다음 Phase 진행
- ❌ 상대 경로 사용 (`./`, `../`)
- ❌ PR 없이 main 직접 커밋
- ❌ 테스트 없이 구현 완료
- ❌ `pokervod.db` 스키마 무단 변경 (`qwen_hand_analysis` 소유)
