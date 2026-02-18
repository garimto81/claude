# Command Reference

**Version**: 1.4.0 | **Updated**: 2026-02-06

이 문서는 모든 슬래시 커맨드의 사용법을 정리합니다.

---

## 목차

| 카테고리 | 커맨드 | 설명 |
|----------|--------|------|
| **핵심** | `/auto` | 통합 PDCA 워크플로우 (v20.1 - Agent Teams + PDCA) |
| | `/orchestrate` | 메인-서브 에이전트 오케스트레이션 |
| | `/commit` | Conventional Commit 생성 |
| | `/check` | 코드 품질/보안 검사 |
| | `/tdd` | TDD 워크플로우 |
| | `/debug` | 가설-검증 기반 디버깅 (D0-D4) |
| **이슈/PR** | `/issue` | GitHub 이슈 관리 |
| | `/pr` | PR 리뷰/머지 |
| | `/create` | PRD/PR/문서 생성 |
| | `/prd-sync` | PRD 동기화 (Google Docs → 로컬) |
| **분석** | `/research` | 코드베이스/웹 리서치 |
| | `/parallel` | 병렬 멀티에이전트 실행 |
| **관리** | `/todo` | 작업 관리 |
| | `/session` | 세션 관리 |
| | `/deploy` | 버전/Docker 배포 |
| | `/audit` | 설정 점검 및 개선 |
| **도구** | `/ai-login` | AI 서비스 인증 (GPT, Gemini) |
| | `/ai-subtitle` | Claude Vision AI 자막 생성 |
| | `/chunk` | PDF 청킹 (토큰/페이지 기반) |
| | `/ccs` | CCS CLI 위임 실행 |
| | `/gmail` | Gmail 메일 관리 |
| | `/mockup` | 하이브리드 목업 생성 |
| | `/shorts` | 쇼츠 영상 생성 |

---

## 1. /work (v19.0 - /auto로 통합됨)

> **`/work`는 `/auto`로 통합되었습니다.** 모든 작업에 `/auto`를 사용하세요.

```bash
# 이전
/work "작업 내용"
/work --auto "작업"
/work --loop

# 이후 (v19.0)
/auto "작업 내용"
/auto "작업"
/auto
```

상세 내용은 `/auto` 섹션을 참조하세요.

---

## 2. /auto - PDCA Orchestrator (v20.1 - Agent Teams)

> **Agent Teams**: 모든 에이전트가 독립 context window에서 실행됩니다 (Lead context 오염 없음).
> **v20.1**: Agent Teams 전면 마이그레이션 + Phase 2 READ-ONLY 버그 수정

별도 키워드 없이 `/auto "작업"` 하나로 모든 고급 기능이 활성화됩니다.

### 통합된 기능

| 기능 | 자동 적용 조건 |
|------|----------------|
| **Agent Teams** | 항상 (TeamCreate → Task(name, team_name) → SendMessage → TeamDelete) |
| **Ralph** | STANDARD/HEAVY (완료까지 루프 + Architect 검증) |
| **Ralplan** | HEAVY (Planner→Architect→Critic 합의) |

### 사용법

```bash
# 기본 사용 (모든 고급 기능 자동 적용)
/auto "로그인 기능 구현"
/auto "전체 테스트 통과시켜줘"

# 지시 없이 실행 (자율 판단)
/auto

# 옵션 (v19.0 - /work 옵션 통합)
/auto --skip-analysis "빠른 수정"    # 사전 분석 스킵
/auto --no-issue "이슈 없이 작업"    # GitHub 이슈 생성 스킵
/auto --strict "엄격 모드"           # E2E 1회 실패 시 중단
/auto --dry-run "작업 계획"          # 계획만 출력, 실행 안 함
/auto --eco "간단한 수정"            # 토큰 절약 모드
/auto status                         # 현재 상태
/auto stop                           # 중지
/auto resume                         # 재개
```

### 자동 실행 흐름 (v20.1 PDCA Phase 0-5 + Agent Teams)

```
/auto "작업"
    │
    ├─[Phase 0] 옵션 파싱 + 모드 결정 + TeamCreate
    ├─[Phase 1] PLAN: explore x2 → 복잡도 판단 → planner/ralplan → 이슈 연동
    ├─[Phase 2] DESIGN: executor/executor-high (STANDARD/HEAVY만, 문서 생성)
    ├─[Phase 3] DO: executor/ralph (복잡도별 분기)
    ├─[Phase 4] CHECK: ultraqa → Architect 검증 → gap-detector → E2E → TDD
    └─[Phase 5] ACT: gap < 90% → 재실행 / gap >= 90% → 완료 → TeamDelete
```

### 레거시 키워드 지원

| 기존 키워드 | 동작 |
|-------------|------|
| `/work "작업"` | → `/auto "작업"` (v19.0) |
| `/work --auto` | → `/auto "작업"` |
| `/work --loop` | → `/auto` |
| `ralph: 작업` | → `/auto "작업"` |
| `ulw: 작업` | → `/auto "작업"` |
| `ultrawork: 작업` | → `/auto "작업"` |
| `ralplan: 작업` | → `/auto "작업"` (계획 모드 강제) |

### 상세 문서

→ `.claude/commands/auto.md` (v20.1)

---

## 3. /orchestrate - 메인-서브 에이전트 오케스트레이션

YAML 기반으로 서브 에이전트를 백그라운드에서 격리 실행하고 결과를 수집합니다.

### 사용법

```bash
/orchestrate "작업 지시 내용"
/orchestrate "로그인 기능 만들어줘"
/orchestrate --parallel "3개 API 만들어줘"
/orchestrate --timeout=30 "대규모 작업"
```

### 실행 흐름

```
STEP 1: 지시 분석 (에이전트 매핑)
    ↓
STEP 2: YAML 업무 파일 생성
    ↓
STEP 3: 서브 에이전트 백그라운드 실행 (격리)
    ↓
STEP 4: 결과 수집 (TaskOutput 대기)
    ↓
STEP 5: 결과 보고 및 판단
```

### 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **YAML 기반** | 모든 업무와 결과를 YAML 파일로 관리 |
| **진행 상황 비공유** | 서브 에이전트는 진행 상황을 공유하지 않음 |
| **결과만 저장** | 서브 에이전트는 결과만 YAML에 저장 |
| **메인 판단** | 메인 에이전트가 결과 확인 후 다음 단계 판단 |

### 옵션

| 옵션 | 설명 |
|------|------|
| `--parallel` | 독립 작업 병렬 실행 |
| `--sequential` | 모든 작업 순차 실행 |
| `--timeout=N` | 작업별 타임아웃 (분) |
| `--retry=N` | 실패 시 재시도 횟수 |

### 폴더 구조

```
.claude/workflow/
├── jobs/           # 업무 정의
├── results/        # 서브 에이전트 결과
└── history/        # 완료된 워크플로우 아카이브
```

---

## 4. /commit - Conventional Commit 생성

Conventional Commits 형식으로 커밋을 생성하고 푸시합니다.

### 사용법

```bash
/commit              # 커밋 + 푸시
/commit --no-push    # 커밋만, 푸시 안함
```

### 커밋 형식

```
<type>(<scope>): <subject> <emoji>

<body>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### 커밋 타입

| Type | 설명 | Emoji |
|------|------|-------|
| `feat` | 새 기능 | ✨ |
| `fix` | 버그 수정 | 🐛 |
| `docs` | 문서 | 📝 |
| `style` | 포맷팅 | 💄 |
| `refactor` | 리팩토링 | ♻️ |
| `perf` | 성능 | ⚡ |
| `test` | 테스트 | ✅ |
| `chore` | 유지보수 | 🔧 |
| `ci` | CI/CD | 👷 |
| `build` | 빌드 | 📦 |

### 예시

```bash
$ /commit

git commit -m "feat(auth): Add OAuth2 authentication ✨"
git push origin main

✅ Committed and pushed: feat(auth): Add OAuth2 authentication ✨
```

---

## 5. /check - 코드 품질/보안 검사

정적 분석, E2E 테스트, 성능 분석, 보안 검사를 수행합니다.

### 사용법

```bash
/check               # 기본 검사 (lint, type, security)
/check --fix         # 자동 수정 가능한 이슈 수정
/check --e2e         # E2E 테스트 + 자동 수정
/check --perf        # 성능 분석
/check --security    # 보안 검사 심화
/check --all         # 모든 검사
/check --e2e --fix   # 조합 사용
```

### 검사 항목

| 카테고리 | 검사 | 도구 |
|----------|------|------|
| **정적 분석** | Type checking | mypy, tsc |
| | Linting | ruff, ESLint |
| | 코드 스타일 | black, Prettier |
| **보안** | 의존성 취약점 | pip-audit, npm audit |
| | SAST | SQL injection, XSS, 시크릿 |
| **테스트** | 커버리지 | pytest --cov, jest |

### --e2e 모드 (E2E 테스트)

```bash
/check --e2e

# 수행 작업:
# 1. Playwright E2E 테스트 실행
# 2. 실패 시 자동 수정 시도 (최대 2회)
# 3. Visual regression 검사
# 4. 접근성 검사 (a11y)
```

### --perf 모드 (성능 분석)

```bash
/check --perf

# 수행 작업:
# 1. CPU/Memory 프로파일링
# 2. 병목 지점 식별
# 3. 최적화 제안 생성
```

### 출력 예시

```
🔍 Running Code Quality Checks...

✅ Static Analysis
   • Type checking: PASSED
   • Linting: PASSED (2 warnings)

⚠️  Security Scan
   • Dependency vulnerabilities: 1 MODERATE
   → Run: npm audit fix

✅ Test Coverage: 87% (target: 80%)

Summary: 1 warning, 1 moderate issue
```

---

## 6. /tdd - TDD 워크플로우

Red-Green-Refactor 사이클로 TDD를 수행합니다.

### 사용법

```bash
/tdd <feature-name>
/tdd user-authentication
```

### Red-Green-Refactor 사이클

#### 🔴 Red: 실패하는 테스트 작성

```bash
# 1. 테스트 작성
def test_login_success():
    user = login("test@example.com", "password")
    assert user.is_authenticated == True

# 2. 실행 (반드시 실패)
pytest tests/test_auth.py -v  # ❌ FAILED

# 3. 커밋
git commit -m "test: Add login success test (RED) 🔴"
```

#### 🟢 Green: 테스트 통과하는 최소 코드 작성

```bash
# 1. 최소 구현
def login(email, password):
    user = User(email=email)
    user.is_authenticated = True
    return user

# 2. 실행 (통과)
pytest tests/test_auth.py -v  # ✅ PASSED

# 3. 커밋
git commit -m "feat: Implement login function (GREEN) 🟢"
```

#### ♻️ Refactor: 코드 개선

```bash
# 1. 리팩토링
def login(email, password):
    return User.authenticate(email, password)

# 2. 테스트 여전히 통과 확인
pytest tests/test_auth.py -v  # ✅ PASSED

# 3. 커밋
git commit -m "refactor: Use User.authenticate method ♻️"
```

---

## 7. /debug - 가설-검증 기반 디버깅

원인 분석 없이 수정하는 것을 방지하고, 체계적인 디버깅 프로세스를 강제합니다.

### 사용법

```bash
/debug [description]      # 반자동 진행 (D0→D1→D2→D3→D4)
/debug status             # 현재 상태 확인
/debug abort              # 디버깅 세션 취소
```

### Phase Gate 모델

```
문제 발생
    ↓
[D0: 이슈 등록] ─── 이슈 설명 필수
    ↓ (자동)
[D1: 원인 분석] ─── 가설 작성 필수 (최소 20자)
    ↓ (자동)
[D2: 검증 설계] ─── 검증 방법 기록 필수
    ↓ (자동)
[D3: 가설 검증] ─── 결과 기록 필수
    │
    ├─ 기각 → D1로 복귀 (3회 시 /issue failed)
    │
    └─ 확인 → [D4: 수정 허용]
```

### Phase별 동작

| Phase | 질문 | Gate 조건 |
|-------|------|----------|
| D0 | "이슈를 설명해주세요" | 설명 필수 |
| D1 | "원인 가설을 작성해주세요" | 최소 20자 |
| D2 | "이 가설을 어떻게 검증할까요?" | 검증 계획 필수 |
| D3 | "검증 결과를 입력해주세요" | confirmed/rejected |
| D4 | (자동) 수정 허용 | - |

### 통합 워크플로우

- `/auto` E2E 실패 시 자동 트리거
- `/issue fix` confidence < 80% 시 자동 트리거
- 3회 가설 기각 시 `/issue failed` 호출

---

## 8. /issue - GitHub 이슈 관리

이슈의 전체 생명주기를 관리합니다.

### 사용법

```bash
/issue list              # 열린 이슈 목록
/issue list mine         # 내게 할당된 이슈
/issue list 123          # 이슈 #123 상세
/issue create "제목"     # 새 이슈 생성
/issue edit 123 --close  # 이슈 닫기
/issue fix 123           # 이슈 해결 워크플로우
/issue failed 123        # 실패 분석
```

### /issue list - 이슈 조회

```bash
/issue list              # 열린 이슈 전체
/issue list open         # 열린 이슈
/issue list closed       # 닫힌 이슈
/issue list label:bug    # 라벨별 필터
/issue list mine         # 내게 할당된 이슈
```

### /issue create - 이슈 생성

```bash
/issue create "로그인 타임아웃 버그"
/issue create "새 기능" --labels=enhancement
```

### /issue edit - 이슈 수정

```bash
/issue edit 123 --close              # 닫기
/issue edit 123 --reopen             # 재오픈
/issue edit 123 --label bug          # 라벨 추가
/issue edit 123 --assignee @me       # 담당자 할당
/issue edit 123 --milestone v1.0     # 마일스톤 설정
```

### /issue fix - 이슈 해결

```bash
/issue fix 123

# 워크플로우:
# 1. 이슈 정보 조회
# 2. 컨텍스트 분석
# 3. 브랜치 생성: fix/issue-123-description
# 4. 구현 + 테스트
# 5. PR 생성 (Fixes #123 참조)
```

### /issue failed - 실패 분석

```bash
/issue failed 123

# 이전 해결 시도 실패 시:
# 1. 실패 원인 분석
# 2. 새 솔루션 제안
# 3. GitHub에 분석 코멘트 추가
```

---

## 9. /pr - PR 리뷰/머지

PR 리뷰, 개선 제안, 자동 머지를 수행합니다.

### 사용법

```bash
/pr review           # 현재 브랜치 PR 리뷰
/pr review #42       # 특정 PR 리뷰
/pr merge            # 조건 확인 후 머지
/pr merge #42        # 특정 PR 머지
/pr auto             # 리뷰 + 자동 머지
/pr list             # 리뷰 대기 PR 목록
```

### /pr review - PR 리뷰

```bash
/pr review #42
/pr review --strict   # 엄격 모드 (경고도 블로커)
```

**리뷰 체크리스트:**

| 카테고리 | 검사 | 심각도 |
|----------|------|--------|
| 코드 품질 | Lint/Type 오류 | High |
| 테스트 | 테스트 실패 | High |
| 보안 | 하드코딩 시크릿 | Critical |
| 스타일 | 포맷팅 오류 | Low |

### /pr merge - PR 머지

```bash
/pr merge            # 기본: squash merge
/pr merge --force    # 조건 무시 (위험)
```

**머지 조건:**
- CI 통과
- 충돌 없음
- Critical/High 이슈 없음

### /pr auto - 자동 리뷰 + 머지

```bash
/pr auto             # 리뷰 후 머지
/pr auto --auto-approve  # 블로커 없으면 자동 머지
```

### 예시 출력

```bash
$ /pr auto

🔍 PR #42 정보 확인...
🔬 리뷰 실행 중...
   [1/3] 코드 품질 검사... ✅
   [2/3] 테스트 검증... ✅
   [3/3] 보안 검사... ✅

✅ 머지 조건 충족
머지를 진행할까요? (Y/N): Y

🎉 PR #42 머지 완료!
```

---

## 10. /create - PRD/PR/문서 생성

PRD, PR, 문서를 생성합니다.

### 사용법

```bash
/create prd <name>       # PRD 생성
/create pr [base]        # PR 생성
/create docs [path]      # 문서 생성
```

### /create prd - PRD 생성

```bash
/create prd user-authentication
/create prd "검색 기능" --template=minimal
/create prd --template=deep
```

**템플릿 옵션:**

| 템플릿 | 소요 시간 | 대상 |
|--------|----------|------|
| `minimal` | 10분 | 숙련 개발자 |
| `standard` | 20-30분 | 일반 프로젝트 |
| `junior` | 40-60분 | 초보자 |
| `deep` | 60+분 | 완벽한 기획서 |

**대화형 워크플로우:**

```
/create prd user-authentication

A. Target Users
   A) End users only
   B) Admins only
   C) Both

B. Authentication Method
   A) Email/Password
   B) OAuth2
   C) SSO
...
```

### /create pr - PR 생성

```bash
/create pr              # main 대상
/create pr develop      # develop 대상
/create pr --draft      # Draft PR
```

### /create docs - 문서 생성

```bash
/create docs                   # 전체 프로젝트
/create docs src/auth/         # 특정 경로
/create docs --format=sphinx   # Sphinx 형식
```

---

## 11. /prd-sync - PRD 동기화

Google Docs 마스터 문서에서 로컬 캐시로 동기화합니다.

### 사용법

```bash
/prd-sync PRD-0001           # 특정 PRD 동기화
/prd-sync --all              # 모든 PRD 동기화
/prd-sync --list             # PRD 목록 조회
```

### 동기화 흐름

```
Google Docs (마스터) → prd_manager.py → Local Cache (읽기 전용)
```

### 관련 파일

| 파일 | 용도 |
|------|------|
| `.prd-registry.json` | PRD 메타데이터 레지스트리 |
| `tasks/prds/PRD-NNNN.cache.md` | 로컬 캐시 (읽기 전용) |
| `scripts/prd_manager.py` | PRD 관리 스크립트 |

### 주의사항

- 로컬 캐시 파일을 직접 수정하지 마세요
- 수정은 항상 Google Docs에서 진행
- 동기화 전 Google Docs 저장 확인

---

## 12. /research - 리서치

코드베이스 분석, 웹 검색, 구현 계획을 수행합니다.

### 사용법

```bash
/research                     # 코드베이스 분석 (기본)
/research code [path]         # 특정 경로 분석
/research web "keyword"       # 웹 검색
/research plan [target]       # 구현 계획 수립
/research --codebase          # 전체 구조 분석
/research --deps              # 의존성 분석
```

### /research code - 코드베이스 분석

```bash
/research code                 # 전체 분석
/research code src/api/        # 특정 경로
/research code 123             # 이슈 #123 관련
/research code --codebase      # 구조 분석
/research code --deps          # 의존성 분석
```

### /research web - 오픈소스/솔루션 검색

```bash
/research web "React state management"
/research web "Python async HTTP client"
```

**수행 작업:**
1. 관련 오픈소스 라이브러리 검색
2. Make vs Buy 분석
3. 유사 구현 사례 조사

### /research plan - 구현 계획 수립

```bash
/research plan 123             # 이슈 #123 구현 계획
/research plan "user auth"     # 기능 구현 계획
/research plan --tdd           # TDD 기반 계획
```

### 옵션

| 옵션 | 설명 |
|------|------|
| `--save` | `.claude/research/`에 저장 |
| `--quick` | 빠른 탐색 (5분 이내) |
| `--thorough` | 철저한 분석 (15-30분) |

---

## 13. /parallel - 병렬 멀티에이전트 실행

4개의 전문 에이전트가 병렬로 작업합니다.

### 사용법

```bash
/parallel dev "작업 설명"      # 병렬 개발
/parallel test                 # 병렬 테스트
/parallel review               # 병렬 코드 리뷰
/parallel research "주제"      # 병렬 리서치
/parallel check "A, B, C"      # 충돌 검사
/parallel dev --branch         # 브랜치 기반 병렬 개발
```

### /parallel check - 충돌 검사

병렬 작업 전 파일 충돌 가능성을 사전 분석합니다.

```bash
/parallel check "Task A, Task B, Task C"

# 출력: 충돌 매트릭스
┌──────────┬────┬────┬─────────┐
│ 파일     │ A  │ B  │ 충돌    │
├──────────┼────┼────┼─────────┤
│ user.ts  │ W  │ W  │ ⚠️ A-B │
└──────────┴────┴────┴─────────┘
```

### /parallel dev - 병렬 개발

```bash
/parallel dev "인증 기능 추가"
/parallel dev --branch "인증 + API + UI"  # 브랜치 격리
```

**에이전트 역할:**

| 에이전트 | 역할 |
|----------|------|
| Architect | 설계, 인터페이스 정의 |
| Coder | 핵심 로직 구현 |
| Tester | 테스트 작성 |
| Docs | 문서화 |

### /parallel test - 병렬 테스트

```bash
/parallel test
/parallel test --module auth
```

**테스터 역할:**

| 에이전트 | 테스트 범위 |
|----------|-------------|
| Unit | 함수, 클래스, 모듈 |
| Integration | API, DB 연동 |
| E2E | 전체 사용자 플로우 |
| Security | OWASP Top 10 |

### /parallel review - 병렬 코드 리뷰

```bash
/parallel review
/parallel review src/auth/
```

**리뷰어 역할:**

| 에이전트 | 검토 항목 |
|----------|-----------|
| Security | SQL Injection, XSS |
| Logic | 알고리즘, 비즈니스 로직 |
| Style | 명명 규칙, 가독성 |
| Performance | 시간 복잡도, N+1 쿼리 |

### /parallel research - 병렬 리서치

```bash
/parallel research "React vs Vue 비교"
```

---

## 14. /todo - 작업 관리

프로젝트 작업을 관리합니다.

### 사용법

```bash
/todo list                     # 목록 조회
/todo add "작업" --priority=high  # 작업 추가
/todo status 1 completed       # 상태 변경
/todo priority 2 high          # 우선순위 변경
/todo depends 3 on 1,2         # 의존성 설정
/todo progress                 # 진행률 확인
/todo --log "작업 내용"        # 작업 로그 기록
```

### 상태 옵션

| 상태 | 마커 | 설명 |
|------|------|------|
| pending | `[ ]` | 미시작 |
| in_progress | `[→]` | 진행 중 |
| completed | `[x]` | 완료 |
| failed | `[!]` | 실패 |
| blocked | `[⏸]` | 블락 |

### PRD에서 Task 생성

```bash
/todo generate tasks/prds/0001-prd-auth.md

# 자동 생성:
# - Task 0.0: Setup
# - Task 1.0: Implementation
# - Task 2.0: Testing
```

### --log 모드

```bash
/todo --log "API 인증 구현 완료"

# 자동 생성: logs/work-log-2025-01-20.md
```

---

## 15. /session - 세션 관리

컨텍스트 압축, 여정 기록, 변경 로그, 세션 이어가기를 관리합니다.

### 사용법

```bash
/session                       # 현재 세션 여정 (기본)
/session compact               # 컨텍스트 압축
/session journey               # 세션 여정 기록
/session changelog [version]   # 변경 로그 생성
/session save                  # 세션 상태 저장
/session resume                # 이전 세션 이어가기
```

### /session save - 세션 상태 저장 ⭐

세션 종료 전 현재 작업 상태를 저장합니다.

```bash
/session save
/session save "인증 기능 70% 완료"
```

### /session resume - 세션 이어가기 ⭐

```bash
/session resume               # 최근 세션 로드
/session resume list          # 저장된 세션 목록
/session resume [date]        # 특정 날짜 세션
```

### /session compact - 컨텍스트 압축

```bash
/session compact              # 즉시 압축
/session compact save         # 압축 결과 저장
/session compact status       # 현재 상태 확인
```

**컨텍스트 임계값:**

| 사용량 | 상태 | 권장 조치 |
|--------|------|-----------|
| 0-40% | 🟢 Safe | 정상 |
| 40-60% | 🟡 DUMB | 주의 |
| 60-80% | 🟠 COMPRESS | 압축 권장 |
| 80%+ | 🚨 CRITICAL | 즉시 압축 |

### /session journey - 세션 여정 기록

```bash
/session journey              # 현재 세션 표시
/session journey save         # 세션 저장
/session journey export       # PR용 마크다운
```

### /session changelog - 변경 로그 생성

```bash
/session changelog            # Unreleased에 추가
/session changelog 1.2.0      # 특정 버전으로 릴리즈
```

### 권장 워크플로우

```
[세션 시작]
/session resume              # 이전 작업 불러오기
     ↓
[작업 진행]
... 코드 작성 ...
     ↓
[세션 종료 전]
/session save "인증 기능 70% 완료"
     ↓
[다음 세션]
/session resume              # 자동으로 이어서 시작
```

---

## 16. /deploy - 버전/Docker 배포

버전 업데이트와 Docker 재빌드를 수행합니다.

### 사용법

```bash
/deploy                        # 대화형 모드
/deploy patch                  # 패치 버전 + 리빌드
/deploy minor                  # 마이너 버전 + 리빌드
/deploy major                  # 메이저 버전 + 리빌드
/deploy 2.3.4                  # 특정 버전 설정
/deploy --docker-only          # Docker만 리빌드
/deploy --version-only         # 버전만 업데이트
/deploy patch --no-cache       # 캐시 없이 리빌드
```

### Semantic Versioning

| Bump | 사용 시점 | 예시 |
|------|----------|------|
| `patch` | 버그 수정 | 1.0.0 → 1.0.1 |
| `minor` | 새 기능 | 1.0.0 → 1.1.0 |
| `major` | Breaking changes | 1.0.0 → 2.0.0 |

### 예시

```bash
$ /deploy minor

=== DEPLOY WORKFLOW ===

[1/2] Version Update
Current: 1.2.3 → New: 1.3.0
Updated: package.json, CLAUDE.md
Committed: chore(release): bump version to 1.3.0

[2/2] Docker Rebuild
Stopping containers... done
Rebuilding images... done
Starting containers... done

=== DEPLOY COMPLETE ===
Version: 1.2.3 → 1.3.0
```

---

## 17. /audit - 설정 점검

CLAUDE.md, 커맨드, 에이전트, 스킬의 일관성을 점검합니다.

### 사용법

```bash
/audit              # 전체 점검
/audit quick        # 빠른 점검 (버전/개수만)
/audit deep         # 심층 점검 (내용 분석 포함)
/audit fix          # 발견된 문제 자동 수정
/audit baseline     # 현재 상태를 기준으로 저장

# 솔루션 추천 (신규)
/audit suggest              # 전체 영역 솔루션 추천
/audit suggest security     # 보안 도구 추천
/audit suggest ci-cd        # CI/CD 도구 추천
/audit suggest code-review  # 코드 리뷰 도구 추천
/audit suggest mcp          # MCP 서버 추천
/audit suggest deps         # 의존성 관리 도구 추천
```

### 점검 항목

| 영역 | 검사 내용 |
|------|----------|
| CLAUDE.md | 버전, 개수 일치 |
| 커맨드 | frontmatter, Usage 섹션 |
| 에이전트 | 역할, 도구 정의 |
| 스킬 | SKILL.md, 트리거 조건 |
| 문서 동기화 | REFERENCE 문서 일치 |

### 출력 예시

```
🔍 Configuration Audit - 2025-12-12

[1/5] CLAUDE.md 점검...
  ✅ 버전: 10.2.0
  ✅ 커맨드: 14개 일치

[2/5] 커맨드 점검...
  ✅ 14개 파일 검사 완료

[3/5] 에이전트 점검...
  ✅ 18개 파일 검사 완료

[4/5] 스킬 점검...
  ✅ 13개 디렉토리 검사 완료

[5/5] 문서 동기화 점검...
  ✅ 모든 문서 동기화됨

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 모든 점검 통과
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 권장 사용 시점

| 시점 | 권장 명령 |
|------|----------|
| 매일 작업 시작 | `/audit quick` |
| 설정 수정 후 | `/audit` |
| 주간/릴리즈 전 | `/audit deep` |
| 새 도구 탐색 | `/audit suggest` |

### /audit suggest - 솔루션 추천

웹과 GitHub를 검색하여 최신 도구/솔루션을 추천합니다.

| 영역 | 추천 내용 |
|------|----------|
| `security` | Snyk, Semgrep, Gitleaks (SAST, 취약점) |
| `ci-cd` | Spacelift, Harness (GitOps, 파이프라인) |
| `code-review` | Qodo Merge, CodeRabbit (AI 코드 리뷰) |
| `mcp` | github-mcp, postgres-mcp (MCP 서버) |
| `deps` | Dependabot, Renovate (의존성 자동화) |

**추천 흐름:**
1. 현재 설정 분석 (MCP, package.json 등)
2. GitHub 트렌드 검색 (스타 수, 업데이트)
3. 웹 검색 (Exa MCP 활용)
4. Make vs Buy 분석 + 설치 가이드

---

## 18. /ai-login - AI 서비스 인증

AI 검증용 서비스(OpenAI, Google) 인증을 관리합니다. Browser OAuth와 CLI 토큰 재사용을 지원합니다.

### 사용법

```bash
/ai-login openai                    # OpenAI OAuth 인증
/ai-login google                    # Google OAuth 인증
/ai-login google --api-key          # Google API Key 방식
/ai-login status                    # 전체 인증 상태
/ai-login logout                    # 모든 세션 로그아웃
```

### 인증 우선순위

| Provider | 1순위 | 2순위 | 3순위 |
|----------|-------|-------|-------|
| OpenAI | 저장된 토큰 | Codex CLI 토큰 | Browser OAuth |
| Google | 저장된 토큰 | Gemini CLI 토큰 | Browser OAuth |

---

## 19. /ai-subtitle - Claude Vision AI 자막 생성

Claude의 Read 도구로 이미지를 직접 분석하여 휠 복원 마케팅 자막을 생성합니다.

### 사용법

```bash
/ai-subtitle                           # temp/ 폴더 이미지 분석
/ai-subtitle -g <group_id>             # 그룹 이미지 다운로드 후 분석
/ai-subtitle -g <group_id> -n 10       # 최대 N개 이미지
/ai-subtitle --output subtitles.json   # JSON 파일로 저장
```

---

## 20. /chunk - PDF 청킹

PDF를 LLM 입력용 청크로 분할합니다. 토큰 기반과 페이지 기반 두 가지 모드를 지원합니다.

### 사용법

```bash
/chunk <pdf_path>                    # 기본 청킹 (4000토큰, 200 오버랩)
/chunk <pdf_path> --tokens 2000      # 토큰 수 지정
/chunk <pdf_path> --page             # 페이지 기반 (레이아웃 보존)
/chunk <pdf_path> --info             # PDF 정보만 확인
/chunk <pdf_path> --preview 3        # 처음 3개 청크 미리보기
```

### 모드 비교

| 모드 | 옵션 | 특징 | 용도 |
|------|------|------|------|
| **토큰** (기본) | - | 텍스트만 추출 | 순수 텍스트 분석 |
| **페이지** | `--page` | 레이아웃 100% 보존 | 이미지/표 포함 |

---

## 21. /ccs - CCS CLI 위임

CCS CLI를 통해 다른 AI에게 작업을 위임합니다. 프로필 자동 선택 기능이 포함됩니다.

### 사용법

```bash
/ccs "refactor auth.js to use async/await"    # 단순 작업
/ccs "analyze entire architecture"            # 장문 분석
/ccs --glm "add tests for UserService"        # 특정 프로필 강제
/ccs "/cook create landing page"              # 중첩 커맨드
```

---

## 22. /gmail - Gmail 관리

Gmail 메일 읽기, 검색, 전송, 관리를 위한 통합 커맨드입니다.

### 사용법

```bash
/gmail                      # 안 읽은 메일 확인
/gmail inbox                # 받은편지함 보기
/gmail search "from:boss"   # 메일 검색
/gmail send "to" "제목" "본문"  # 메일 전송
/gmail read <id>            # 메일 상세 보기
/gmail labels               # 라벨 목록
```

### 서브커맨드

| 서브커맨드 | 설명 |
|-----------|------|
| (없음) | 안 읽은 메일 확인 |
| `inbox` | 받은편지함 |
| `unread` | 안 읽은 메일 |
| `search` | 메일 검색 |
| `read` | 메일 상세 |
| `send` | 메일 전송 |
| `labels` | 라벨 목록 |

---

## 23. /mockup - 하이브리드 목업 생성

HTML 와이어프레임과 Google Stitch를 자동 선택하여 최적의 목업을 생성합니다.

### 사용법

```bash
/mockup [name]              # 기본 (B&W 와이어프레임)
/mockup [name] --force-html # 강제 HTML
/mockup [name] --force-hifi # 강제 Stitch API (고품질)
/mockup [name] --screens=3  # 3개 화면 생성
/mockup [name] --prd=PRD-0001  # PRD 연결
/mockup [name] --flow       # 전체 흐름 다이어그램
```

---

## 24. /shorts - 쇼츠 영상 생성

PocketBase에서 사진을 가져와 마케팅용 쇼츠 영상을 생성합니다.

### 사용법

```bash
/shorts list                          # 그룹 목록 조회
/shorts list -g <group_id>            # 그룹별 사진 조회
/shorts create -g <group_id> --auto   # 영상 생성
/shorts batch -g <group_id>           # 전체 워크플로우 (권장)
```

---

## Quick Reference

### 일상 워크플로우

```bash
# 작업 시작
/session resume              # 이전 세션 이어가기
/research 123                # 이슈 분석

# 개발
/tdd user-auth               # TDD로 개발
/check --fix                 # 품질 검사 + 자동 수정

# 완료
/commit                      # 커밋 + 푸시
/create pr                   # PR 생성
/pr auto                     # 리뷰 + 머지

# 세션 종료
/session save "작업 설명"     # 상태 저장
```

### 전체 자동화

```bash
/auto "기능 구현"             # PDCA Phase 0-5 완전 자동화
/auto                         # 자율 판단 반복 실행
```

### 병렬 작업

```bash
/parallel dev --branch "대규모 기능"  # 브랜치 격리 병렬 개발
/parallel review                      # 병렬 코드 리뷰
```

---

## 관련 문서

| 문서 | 설명 |
|------|------|
| `CLAUDE.md` | 프로젝트 전체 지침 |
| `docs/AGENTS_REFERENCE.md` | 에이전트 상세 |
| `.claude/commands/` | 커맨드 원본 파일 |
| `.claude/skills/` | 스킬 상세 |
