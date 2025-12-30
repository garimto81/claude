---
name: create
description: Create PRD, PR, or documentation (prd, pr, docs)
---

# /create - 생성 통합 커맨드

PRD, PR, 문서를 생성합니다.

## Usage

```
/create <target> [args]

Targets:
  prd [name] [--template] [--local-only]   PRD 문서 생성 (Google Docs 마스터)
  pr [base-branch]                          Pull Request 생성 (Phase 4)
  docs [path] [--format]                    API/코드 문서 생성
```

---

## /create prd - PRD 생성 (Google Docs 마스터)

**기본 동작**: Google Docs에 PRD를 생성하고 로컬에는 읽기 전용 캐시를 저장합니다.

```bash
/create prd user-authentication            # Google Docs 생성 (기본)
/create prd "검색 기능" --template=deep    # DEEP 템플릿으로 생성
/create prd feature --local-only           # 로컬 Markdown만 (호환 모드)
```

### 아키텍처

```
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│   /create prd   │───────▶│   Google Docs   │───────▶│  Local Cache    │
│   (대화형 질문) │        │   (마스터)      │        │  (읽기 전용)    │
└─────────────────┘        └─────────────────┘        └─────────────────┘
                                    │                          │
                                    └──────────┬───────────────┘
                                               ▼
                                    ┌─────────────────┐
                                    │ .prd-registry   │
                                    │    .json        │
                                    └─────────────────┘
```

### Google Docs 워크플로우

```
/create prd [name]
      │
      ▼
┌─────────────────────────────────┐
│ 1. 대화형 질문 (A/B/C/D 형식)   │
│    - Target Users               │
│    - Core Features              │
│    - Technical Stack            │
│    - Success Metrics            │
└─────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│ 2. PRD 번호 자동 할당           │
│    .prd-registry.json에서       │
│    next_prd_number 조회         │
└─────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│ 3. Google Docs 문서 생성        │
│    - 템플릿 기반 문서 생성      │
│    - 공유 폴더에 저장           │
│    - 섹션별 내용 삽입           │
└─────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│ 4. 로컬 참조 파일 생성          │
│    - .prd-registry.json 업데이트│
│    - PRD-NNNN.cache.md 생성     │
│    - docs/checklists/PRD-NNNN.md│
└─────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────┐
│ 5. 결과 출력                    │
│    → Google Docs URL            │
│    → 로컬 캐시 경로             │
│    → Checklist 경로             │
└─────────────────────────────────┘
```

### 대화형 질문

Claude Code가 3-8개 명확화 질문 (A/B/C/D 형식):

```
/create prd user-authentication

Let's create a PRD. I'll ask some questions:

A. Target Users
   A) End users only
   B) Admins only
   C) Both
   D) External API consumers

B. Authentication Method
   A) Email/Password
   B) OAuth2
   C) SSO
   D) No auth needed

C. Core Features
   A) Login/Logout only
   B) + Password reset
   C) + MFA
   D) Full auth suite

...
```

### 템플릿 옵션

| 템플릿 | 소요 시간 | 토큰 | 대상 |
|--------|----------|------|------|
| `minimal` | 10분 | ~1270 | 숙련 개발자 |
| `standard` | 20-30분 | ~2500 | 일반 프로젝트 (기본) |
| `junior` | 40-60분 | ~4500 | 초보자 |
| `deep` | 60+분 | ~6000 | 완벽한 기획서 |

### 출력 예시

```bash
/create prd user-authentication

# Output:
# ✓ PRD 번호 할당: PRD-0002
# ✓ Google Docs 생성 중...
# ✓ 문서 생성 완료!
#
# PRD-0002: User Authentication
# ├── Google Docs: https://docs.google.com/document/d/1abc.../edit
# ├── Local Cache: tasks/prds/PRD-0002.cache.md
# └── Checklist: docs/checklists/PRD-0002.md
#
# Next Steps:
#   - 문서 편집: 위 Google Docs URL 클릭
#   - 동기화: /prd-sync PRD-0002
#   - Task 생성: /todo generate PRD-0002
```

### 로컬 캐시 형식

```markdown
<!--
  PRD-0002 Local Cache (Read-Only)
  Master: https://docs.google.com/document/d/1abc.../edit
  Last Synced: 2025-12-24T10:00:00Z
  DO NOT EDIT - Changes will be overwritten
-->

# PRD-0002: User Authentication

| 항목 | 값 |
|------|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Priority** | P1 |
| **Created** | 2025-12-24 |
...
```

### 메타데이터 레지스트리

`.prd-registry.json`:

```json
{
  "version": "1.0.0",
  "last_sync": "2025-12-24T10:00:00Z",
  "next_prd_number": 3,
  "prds": {
    "PRD-0001": {
      "google_doc_id": "1abc...",
      "google_doc_url": "https://docs.google.com/document/d/.../edit",
      "title": "포커 핸드 자동 캡처",
      "status": "In Progress",
      "priority": "P0",
      "local_cache": "PRD-0001.cache.md",
      "checklist_path": "docs/checklists/PRD-0001.md"
    }
  }
}
```

### 옵션

| 옵션 | 설명 |
|------|------|
| `--template=TYPE` | 템플릿 선택 (minimal/standard/junior/deep) |
| `--local-only` | 로컬 Markdown만 생성 (Google Docs 미사용) |
| `--priority=P0-P3` | 우선순위 지정 |
| `--status=STATUS` | 상태 지정 (Draft/In Progress/Review/Approved) |

### 공유 폴더

- **폴더 ID**: `1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW`
- **URL**: [Google AI Studio 폴더](https://drive.google.com/drive/folders/1JwdlUe_v4Ug-yQ0veXTldFl6C24GH8hW)

---

## /create pr - Pull Request 생성

```bash
/create pr              # 기본 (main 대상)
/create pr develop      # 특정 base branch
/create pr --draft      # Draft PR
```

### Workflow

1. **Verify Git State**
   - 현재 브랜치 확인
   - 클린 워킹 디렉토리 확인
   - 커밋 존재 확인

2. **Push Changes**
   ```bash
   git push -u origin <branch>
   ```

3. **Generate PR Description**
   - `git log`에서 변경 사항 분석
   - 템플릿 적용:

   ```markdown
   ## Summary
   - Key changes

   ## Test Plan
   - [ ] Testing checklist

   ## Related
   - PRD reference
   ```

4. **Create PR**
   ```bash
   gh pr create --title "..." --body "..."
   ```
   - 자동 라벨 적용
   - 이슈 연결

### Phase Integration

- **Phase 4**: Primary use case
- `[PRD-NNNN]` 또는 `[#issue]` 참조
- Auto-merge 워크플로우 연동

### 출력 예시

```bash
/create pr

# Output:
# ✓ Pushing to origin/feature/PRD-0001-auth
# ✓ Analyzing 3 commits
# ✓ Creating PR #42: Add OAuth2 authentication
# → https://github.com/user/repo/pull/42
```

---

## /create docs - 문서 생성

```bash
/create docs                         # 전체 프로젝트
/create docs src/auth/               # 특정 경로
/create docs --format=html           # HTML 형식
/create docs --format=sphinx         # Sphinx 형식
```

### 문서 유형

#### 1. API Documentation

```markdown
## `login(email: str, password: str) -> User`

Authenticates user with email and password.

### Parameters
- `email` (str): User email address
- `password` (str): Plain text password

### Returns
- `User`: Authenticated user object

### Raises
- `AuthenticationError`: Invalid credentials

### Example
```python
user = login("test@example.com", "password123")
```

### Edge Cases
- Empty email/password → raises ValueError
```

#### 2. Class Documentation

```markdown
## Class: `UserManager`

Manages user accounts and authentication.

### Attributes
- `session`: Database session
- `cache`: Redis cache instance

### Methods
- `create_user()`: Create new user
- `authenticate()`: Verify credentials

### Usage
```python
manager = UserManager(session=db.session)
user = manager.create_user(email="test@example.com")
```
```

#### 3. Module Documentation

```markdown
# auth Module

User authentication and session management.

## Overview
Provides OAuth2 and email/password authentication.

## Quick Start
```python
from auth import login, logout
user = login("test@example.com", "password")
```

## Components
- `login()`: User authentication
- `logout()`: Session termination
```

### 출력 구조

```
docs/
├── api/
│   ├── auth.md
│   ├── users.md
│   └── sessions.md
├── guides/
│   ├── quickstart.md
│   └── authentication.md
├── reference/
│   └── configuration.md
└── index.md
```

### Auto-Generated Content

- **입출력 분석**: 함수 시그니처, 타입 힌트
- **Edge Cases**: None 처리, 빈 문자열, 경계 조건
- **Code Examples**: 기본 사용, 고급 패턴, 에러 처리

---

## Related

- `/prd-sync` - PRD 동기화 (Google Docs → 로컬)
- `/commit` - 커밋 생성
- `/session changelog` - CHANGELOG 업데이트
- `/todo` - PRD에서 Task 생성
