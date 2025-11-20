# 깃허브 네이티브 워크플로우 빠른 시작

**목적**: 로컬 PRD/Task → GitHub Issue/Projects 전환

**예상 시간**: 30분

---

## 1단계: 사전 준비 (5분)

### 1.1 GitHub CLI 설치

```bash
# Windows
winget install GitHub.cli

# macOS
brew install gh

# Linux
sudo apt install gh
```

### 1.2 인증

```bash
gh auth login
# → GitHub.com → HTTPS → Login with browser
```

### 1.3 Repository 설정

```bash
# Repository 확인
gh repo view

# 환경변수 (PowerShell)
$env:GITHUB_REPOSITORY = "username/repo"

# 또는 Bash
export GITHUB_REPOSITORY="username/repo"
```

---

## 2단계: Labels 생성 (5분)

```bash
# 권한 부여 (Git Bash/WSL)
chmod +x scripts/setup-github-labels.sh

# 실행
bash scripts/setup-github-labels.sh

# 확인
gh label list
```

**결과**: Phase 0-6, Type, Status, Priority 레이블 생성

---

## 3단계: Issue Templates 추가

```bash
# 파일 확인
ls .github/ISSUE_TEMPLATE/

# 커밋 & 푸시
git add .github/ISSUE_TEMPLATE/
git commit -m "docs: Add GitHub issue templates"
git push
```

---

## 4단계: GitHub Project 생성 (5분)

### 웹에서 생성 (추천)

1. GitHub 프로필 → Projects → New Project
2. Template: Board
3. Title: "개발"
4. Add to repository

### 또는 CLI

```bash
gh project create --title "개발" --owner @me
```

### Automation 설정

- Item added → Move to Planning
- Item closed → Move to Deployed

---

## 5단계: 첫 이슈 생성 (5분)

### 웹에서 (추천)

```bash
gh repo view --web
# → Issues → New Issue → 템플릿 선택
```

### 또는 CLI

```bash
gh issue create \
  --title "[FEATURE] Google OAuth" \
  --label "phase-0,type:feature,priority:p1" \
  --body "$(cat <<'EOF'
## Executive Summary
Google OAuth 로그인 추가

## Goals
1. Google OAuth 2.0 통합
2. 프로필 자동 생성
3. 세션 관리 (7일)

## Success Metrics
- [ ] 로그인 < 2초
- [ ] 프로필 자동 생성

## Security
- [x] 환경변수 분리
- [ ] RLS 정책
EOF
)"
```

---

## 6단계: 이슈 작업 시작 (5분)

### 자동화 스크립트

```bash
# 권한 부여
chmod +x scripts/github-issue-dev.sh

# 작업 시작 (예: #1)
bash scripts/github-issue-dev.sh 1

# 자동 실행:
# - Branch: feature/issue-1
# - Draft PR 생성
# - Label: status:in-progress
```

### 코드 & 커밋

```bash
# 코드 작성...

# 커밋 (이슈 번호 필수)
git add .
git commit -m "feat: Add Google OAuth [#1]"
git push
```

### PR Ready

```bash
gh pr ready
# 또는 웹: PR 페이지 → Ready for review
```

---

## 7단계: 기존 PRD 마이그레이션 (선택)

```bash
# Python 확인
python --version

# 패키지 설치
pip install PyGithub

# Token 설정
$env:GITHUB_TOKEN = "ghp_token"        # PowerShell
export GITHUB_TOKEN="ghp_token"        # Bash

# 마이그레이션
python scripts/migrate_prds_to_issues.py tasks/prds/0001-*.md
```

---

## 일일 워크플로우

### 아침

```bash
# 진행 중 확인
gh issue list --label "status:in-progress" --assignee @me

# 다음 작업 선택
gh issue list --label "status:planning" --limit 5

# 작업 시작
bash scripts/github-issue-dev.sh <issue-number>
```

### 개발

```bash
# 코드 작성...
git add .
git commit -m "feat: implement [#N]"
git push

# 상태 확인
gh pr status
```

### 완료

```bash
# PR ready
gh pr ready

# Merge (자동 or 수동)
gh pr merge --squash
```

---

## GitHub vs Local

| 작업 | Before | After |
|------|--------|-------|
| PRD | `tasks/prds/0001-*.md` | Issue 템플릿 |
| Task List | `generate_tasks.py` | Issue tasklist |
| 진행 추적 | 로컬 체크박스 | Project Board |
| 커밋 참조 | `[PRD-0001]` | `[#123]` (자동 링크) |
| Cross-repo | 수동 관리 | Issue references |

---

## 명령어 치트시트

```bash
# Issue
gh issue list                          # 목록
gh issue view 123                      # 보기
gh issue create                        # 생성
gh issue close 123                     # 닫기

# PR
gh pr list                             # 목록
gh pr view 45                          # 보기
gh pr create                           # 생성
gh pr ready                            # Draft → Ready
gh pr merge --squash                   # 병합

# Label
gh label list                          # 목록
gh label create "name" --color "hex"   # 생성

# Project
gh project list                        # 목록
gh project view 1                      # 보기

# 빠른 워크플로우
bash scripts/github-issue-dev.sh 123   # 이슈 작업 시작
gh pr ready && gh pr merge --auto --squash  # 완료 & 병합
```

---

## 문제 해결

### gh 실행 안됨

```bash
# 인증 확인
gh auth status

# 재인증
gh auth login
```

### 스크립트 권한 에러 (Windows)

```bash
# Git Bash 사용
bash scripts/github-issue-dev.sh 1

# 또는 PowerShell 직접
gh issue view 1
git checkout -b feature/issue-1
gh pr create --draft
```

### Issue Template 안보임

- 커밋 & 푸시 확인: `.github/ISSUE_TEMPLATE/*.yml`
- GitHub 웹 확인: Issues → New Issue

---

## 다음 단계

1. **첫 Feature** - Issue → PR → Merge 전체 사이클
2. **Cross-repo** - VTC_Logger에서 sso-system 이슈 참조
3. **GitHub Actions** - 자동 테스트 & 배포
4. **Team 확장** - 팀원 초대 시에도 동일 워크플로우

---

## 참고

- [깃허브_워크플로우_개요.md](깃허브_워크플로우_개요.md) - 5분 개요
- [docs/깃허브_네이티브_워크플로우.md](docs/깃허브_네이티브_워크플로우.md) - 상세 가이드
- [GitHub CLI 문서](https://cli.github.com/manual/)
- [GitHub Issues](https://docs.github.com/en/issues)
- [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects)

---

**시작하기**:

```bash
gh issue create
# 또는
gh repo view --web
```
