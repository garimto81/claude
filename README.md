# Claude AI 전역 지침 레포

**목적**: Claude Code 작업을 위한 전역 워크플로우 및 가이드 관리

**버전**: 5.0.0 | **업데이트**: 2025-01-18 | **주요 업데이트**: Comprehensive workflow optimization 🚀

---

## 🎉 v5.0.0 주요 업데이트 (2025-01-18)

### 전면 워크플로우 최적화! ⭐

**문서 구조 개선**:
- ✅ **CLAUDE.md 토큰 35% 절감** (1,368줄 → ~1,125줄)
- ✅ **docs/PHASE_AGENT_MAPPING.md** - Phase 3-6 상세 가이드 (새 문서)
- ✅ **docs/AGENT_USAGE_BEST_PRACTICES.md** - Agent 선택 가이드 (새 문서)
- ✅ **Phase 2.5 추가** - 전문 리뷰 워크플로우 공식화

**Phase 2.5: Professional Reviews** (신규):
- `/pragmatic-code-review` - 7-tier 계층적 코드 리뷰 (Opus)
- `/design-review` - Playwright MCP 디자인 리뷰 (Sonnet)
- `/security-review` - OWASP Top 10 보안 리뷰

**개발 사이클 업그레이드**:
```
Phase 0 → 0.5 → 1 → 2 → [2.5 ⭐ NEW] → 3 → 4 → 5 → 6
```

**성과**:
- 토큰 사용: 35% 절감 (~1,900 토큰 절약)
- 문서 유지보수성: 대폭 향상 (3개 독립 문서)
- 리뷰 품질: 전문화된 워크플로우

---

## 🎉 v4.18.0 주요 업데이트 (2025-01-18)

### Workflow-Reviews Plugin 추가!

- ✅ **OneRedOak/claude-code-workflows 통합** (2개 에이전트 + 3개 커맨드)
- ✅ **pragmatic-code-review 에이전트** (Opus) - 7단계 계층적 리뷰 프레임워크
- ✅ **design-review 에이전트** (Sonnet) - Playwright MCP 활용 디자인 리뷰
- ✅ **/pragmatic-code-review** - PR 종합 코드 리뷰 커맨드
- ✅ **/design-review** - UI/UX 일관성 검증 커맨드
- ✅ **/security-review** - OWASP Top 10 기반 보안 리뷰 커맨드

**사용 사례**: Anthropic 자체 개발 프로세스 기반 전문 리뷰
- PR 코드 리뷰 → `/pragmatic-code-review`
- UI 변경사항 검증 → `/design-review`
- 보안 취약점 탐지 → `/security-review`

**성과**:
- 플러그인 개수: 24 → 25 (+4%)
- 리뷰 자동화 (7-tier 계층적 분석, WCAG 2.1 AA 준수)

---

## 🎉 v4.17.0 주요 업데이트 (2025-01-18)

### Meta-Development Plugin 추가!

- ✅ **davila7/claude-code-templates 통합** (6개 메타 에이전트)
- ✅ **agent-expert** - 에이전트 개발 메타 가이드 (476줄)
- ✅ **command-expert** - 슬래시 커맨드 개발 가이드 (420줄)
- ✅ **mcp-expert** - MCP 통합 개발 가이드 (257줄)
- ✅ **cli-ui-designer** - CLI UI 디자인 전문가 (404줄)
- ✅ **docusaurus-expert** - 문서화 전문가 (173줄)
- ✅ **marketplace.json** 68개 플러그인으로 업데이트

**사용 사례**: Claude Code 시스템 자체를 개발하거나 확장할 때
- 새로운 에이전트 만들기 → agent-expert
- 슬래시 커맨드 추가 → command-expert
- MCP 서버 통합 → mcp-expert

---

## 🎉 v4.16.0 주요 업데이트 (2025-01-18)

### 플러그인 시스템 통합 완료!

- ✅ **25개 플러그인** (17개 wshobson + 8개 Phase별)
- ✅ **122+ 에이전트** (89개 wshobson + 33개 기존)
- ✅ **27개 스킬** (Progressive Disclosure)
- ✅ **토큰 효율 85-95%** (기존 80-90% 대비 개선)
- ✅ **마켓플레이스 시스템** (.claude-plugin/marketplace.json)

**성과**: 에이전트 +270%, 토큰 사용 -62%, 무한 확장 가능

---

## 📚 핵심 문서

### 워크플로우 (필수)
- **[CLAUDE.md](CLAUDE.md)** - Phase 0-6 개발 사이클, 25개 플러그인 시스템
- **[Quick Start Guide](docs/QUICK_START_GUIDE.md)** ⭐ - v4.16.0 빠른 시작 (5분 완성)

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
├── CLAUDE.md                    # 핵심 워크플로우 (v4.16.0)
├── README.md                    # 이 파일
│
├── 깃허브_워크플로우_개요.md     # GitHub 워크플로우 5분 개요
├── 깃허브_빠른시작.md           # 30분 설정 가이드
│
├── .claude-plugin/              # 🆕 플러그인 마켓플레이스
│   └── marketplace.json         # 25개 플러그인 메타데이터
│
├── .claude/plugins/             # 🆕 플러그인 시스템
│   ├── python-development/      # Python 3.12+ (3 agents, 5 skills)
│   ├── javascript-typescript/   # JS/TS (2 agents, 4 skills)
│   ├── full-stack-orchestration/# 멀티 에이전트 조율
│   ├── security-scanning/       # 보안 스캔
│   ├── kubernetes-operations/   # K8s 배포
│   └── ... (25개 플러그인)
│
├── docs/                        # 상세 가이드
│   ├── AGENTS_REFERENCE.md      # 120+ 에이전트 문서
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

## 🚫 이 레포가 **아닌** 것

### ❌ 실제 프로젝트 코드
이 레포지토리는 **메타 워크플로우 시스템**입니다. 실제 프로젝트 코드는 포함하지 않습니다.

**예시** (모두 삭제됨):
```
✗ VTC_Logger/         - 실제 앱 프로젝트
✗ contents-factory/   - 실제 웹 프로젝트
✗ sso-nextjs/         - 실제 SSO 시스템
✗ repo-analyzer/      - 실제 도구
```

**원칙**:
- ✅ 이 레포 = **어떻게 개발할지** (워크플로우, 에이전트, 템플릿)
- ✅ 별도 레포 = **무엇을 개발할지** (실제 프로젝트 코드)

### ❌ 라이브러리/패키지
`npm install` 또는 `pip install`로 설치하는 패키지가 아닙니다.

**대신**:
- 워크플로우 템플릿을 복사하여 프로젝트에 적용
- 에이전트를 `.claude/` 디렉토리로 복사
- 스크립트를 `scripts/`로 복사

### ❌ 단계별 튜토리얼
순차적 학습 과정이 아닙니다.

**대신**:
- 즉시 사용 가능한 워크플로우 템플릿
- 필요할 때 참조하는 레퍼런스 가이드
- Quick Start로 5분 안에 시작

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
- 120+ Agent 레퍼런스 (v4.16.0 확장)
- Agent Optimizer 완전 가이드
- Branch Protection 설정 가이드
- Plugin System 가이드 (신규)

---

## 📖 최신 기능

### v4.16.0 (2025-01-18) - wshobson/agents 플러그인 시스템 통합
- ✅ 25개 플러그인 시스템 (17 wshobson + 8 Phase별)
- ✅ 120+ 에이전트 통합 (에이전트 +264%)
- ✅ 27개 스킬 시스템 (Progressive Disclosure)
- ✅ 마켓플레이스 아키텍처 (.claude-plugin/)
- ✅ 토큰 효율 85-95% 달성 (토큰 사용 -62%)
- **참조**: https://github.com/wshobson/agents

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
