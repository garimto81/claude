# Claude AI 전역 지침 레포

**목적**: Claude Code 작업을 위한 전역 워크플로우 및 가이드 관리

**버전**: 4.15.0 | **업데이트**: 2025-01-14

---

## 📚 핵심 문서

### 워크플로우 (필수)
- **[CLAUDE.md](CLAUDE.md)** - Phase 0-6 개발 사이클, Agent Top 5

### GitHub 네이티브
- [깃허브_워크플로우_개요.md](깃허브_워크플로우_개요.md) - 5분 개요, ROI
- [깃허브_빠른시작.md](깃허브_빠른시작.md) - 30분 설정 가이드
- [README_GITHUB_WORKFLOW.md](README_GITHUB_WORKFLOW.md) - 문서 색인

### Spec Kit
- [docs/SPECKIT_EXECUTIVE_SUMMARY.md](docs/SPECKIT_EXECUTIVE_SUMMARY.md) - 5분 개요
- [.speckit/constitution.md](.speckit/constitution.md) - Constitution 템플릿

### 자동화 시스템

**Auto PR/Merge**:
- [.github/workflows/auto-pr-merge.yml](.github/workflows/auto-pr-merge.yml) - GitHub Actions
- [docs/BRANCH_PROTECTION_GUIDE.md](docs/BRANCH_PROTECTION_GUIDE.md) - 설정 가이드

**Agent Optimizer**:
- [docs/AGENT_OPTIMIZER_GUIDE.md](docs/AGENT_OPTIMIZER_GUIDE.md) - 완전한 가이드
- [.claude/optimizer-config.json](.claude/optimizer-config.json) - 설정

**Scripts**:
- `bash scripts/setup-github-labels.sh` - GitHub 라벨 설정
- `bash scripts/github-issue-dev.sh 123` - 이슈 작업 시작

---

## 🚀 빠른 시작

### 1. 처음 사용하는 경우
```bash
# 1. 워크플로우 읽기 (10분)
cat CLAUDE.md

# 2. Phase 0 실습 - PRD 작성
mkdir -p tasks/prds
vim tasks/prds/0001-prd-test-feature.md
```

### 2. GitHub 워크플로우 도입
```bash
# 1. 개요 읽기 (5분)
cat 깃허브_워크플로우_개요.md

# 2. 라벨 설정 (2분)
bash scripts/setup-github-labels.sh

# 3. 첫 이슈 시작
gh issue create --template 01-feature-prd.yml
bash scripts/github-issue-dev.sh 123
```

### 3. Agent Optimizer 설치
```bash
# 1. Git hook 활성화
ln -s ../../.claude/hooks/post-commit .git/hooks/post-commit  # Unix/macOS
# 또는
cp .claude/hooks/post-commit .git/hooks/post-commit          # Windows

# 2. 의존성 설치
pip install -r requirements.txt

# 3. (선택) API 키 설정
export ANTHROPIC_API_KEY=your_key
```

---

## 📂 폴더 구조

```
claude01/
├── CLAUDE.md                    # 핵심 워크플로우
├── README.md                    # 이 파일
│
├── 깃허브_워크플로우_개요.md     # GitHub 워크플로우 5분 개요
├── 깃허브_빠른시작.md           # 30분 설정 가이드
│
├── docs/                        # 상세 가이드
│   ├── AGENTS_REFERENCE.md
│   ├── AGENT_OPTIMIZER_GUIDE.md
│   ├── BRANCH_PROTECTION_GUIDE.md
│   └── SPECKIT_*.md
│
├── scripts/                     # 자동화 스크립트
│   ├── setup-github-labels.sh
│   ├── github-issue-dev.sh
│   ├── check-phase-completion.py
│   └── create-phase-pr.sh
│
├── .claude/                     # Claude Code 확장
│   ├── hooks/post-commit
│   ├── scripts/analyze_agent_usage.py
│   └── optimizer-config.json
│
├── .github/workflows/           # GitHub Actions
│   └── auto-pr-merge.yml
│
├── tasks/                       # PRD 및 Task List
│   ├── prds/
│   └── tickets/
│
└── tests/                       # 테스트 (pytest)
```

---

## 🎯 사용 방법

### 새 프로젝트 시작

```bash
# 1. 전역 워크플로우 참조
cat CLAUDE.md

# 2. 프로젝트 폴더 생성 (claude01 밖에)
cd d:\Projects && mkdir my-project && cd my-project

# 3. Git 초기화 및 Phase 0 시작
git init
vim tasks/prds/0001-prd-feature.md
```

### 기존 프로젝트에 적용

```bash
# 1. 스크립트 복사
cp ~/claude01/scripts/*.sh ./scripts/

# 2. GitHub 라벨 설정
bash scripts/setup-github-labels.sh

# 3. 워크플로우 파일 복사 (선택)
cp ~/claude01/.github/workflows/auto-pr-merge.yml .github/workflows/
```

---

## 🚫 포함하지 않는 것

**프로젝트별 폴더** (.gitignore 등록됨):
```
actiontracker/
contents-factory/
VTC_Logger/
sso-system/
... 기타 프로젝트
```

**원칙**: 이 레포 = 전역 지침만 | 각 프로젝트 = 별도 레포

---

## 📊 구현 상태

### ✅ 핵심 기능
- Phase 0-6 워크플로우
- GitHub 네이티브 워크플로우
- 자동 PR/머지 시스템
- Agent 자동 최적화
- Context7 + Playwright 필수 검증

### 🔧 자동화
- GitHub 라벨 설정 스크립트
- 이슈 작업 시작 스크립트
- Phase 완료 감지
- PR 자동 생성

### 📁 문서 체계
- MINIMAL/STANDARD/JUNIOR PRD 가이드
- 33개 Agent 레퍼런스
- Agent Optimizer 완전 가이드
- Branch Protection 설정 가이드

---

## 📖 최신 기능

### v4.4.0 (2025-01-13)
- ✅ README 토큰 최적화: 347→250줄 (-28%)
- ✅ Agent Optimizer 섹션 간소화
- ✅ 중복 제거 (Phase 설명, 주요 개념)
- ✅ 네비게이션 중심 재구성

### v4.3.0 (2025-01-13)
- ✅ Agent/Skill 자동 최적화 시스템 추가
- ✅ 폴더 구조 업데이트

### v4.2.0 (2025-01-13)
- ✅ Auto PR/Merge 시스템 추가
- ✅ GitHub Actions 워크플로우

### v4.1.0 (2025-01-12)
- ✅ README 전역 지침 중심 재작성
- ✅ 프로젝트/전역 분리 명확화

---

## 🎓 빠른 참조

### 자주 사용하는 명령어
```bash
# GitHub 라벨 설정
bash scripts/setup-github-labels.sh

# 이슈로 작업 시작
bash scripts/github-issue-dev.sh 123

# 진행률 확인
grep -oP '\[.\]' tasks/0001-*.md | sort | uniq -c

# Agent Optimizer 로그 확인
cat .claude/improvement-suggestions.md
```

### 문서 네비게이션
- **전체 색인**: [docs/깃허브_워크플로우_색인.md](docs/깃허브_워크플로우_색인.md)
- **Agent 레퍼런스**: [docs/AGENTS_REFERENCE.md](docs/AGENTS_REFERENCE.md)
- **영문 참조**: [README_GITHUB_WORKFLOW.md](README_GITHUB_WORKFLOW.md)

---

## 🤝 기여

개인 워크플로우 관리용이지만 개선 제안 환영합니다.

- Issue 생성
- Pull Request

---

## 📝 라이센스

MIT License

---

**관리자**: 바이브 코더
**도구**: Claude Code + GitHub
**최종 업데이트**: 2025-01-13
