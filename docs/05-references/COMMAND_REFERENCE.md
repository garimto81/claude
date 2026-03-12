# Command Reference

> 자동 생성: `/audit` 기준. 커맨드 22개.

## 커맨드 목록

| # | 커맨드 | 설명 | 파일 |
|:-:|--------|------|------|
| 1 | `/audit` | Daily configuration audit and improvement suggestions | `.claude/commands/audit.md` |
| 2 | `/auth` | AI 인증 관리 (openai, google, status, logout) | `.claude/commands/auth.md` |
| 3 | `/auto` | PDCA Orchestrator - Agent Teams + PDCA 통합 워크플로우 | `.claude/commands/auto.md` |
| 4 | `/check` | Comprehensive code quality and security checks | `.claude/commands/check.md` |
| 5 | `/chunk` | PDF 청킹 - 토큰 기반(텍스트) 또는 페이지 기반(레이아웃 보존) 분할 | `.claude/commands/chunk.md` |
| 6 | `/commit` | Create git commits using conventional commit format with emojis | `.claude/commands/commit.md` |
| 7 | `/create` | Create PRD, PR, or documentation (prd, pr, docs) | `.claude/commands/create.md` |
| 8 | `/debug` | Hypothesis-verification based debugging (Phase Gate D0-D4) | `.claude/commands/debug.md` |
| 9 | `/deploy` | Version update and Docker rebuild workflow | `.claude/commands/deploy.md` |
| 10 | `/gmail` | Gmail 메일 관리 커맨드 | `.claude/commands/gmail.md` |
| 11 | `/issue` | GitHub issue lifecycle management (list, create, fix, failed) | `.claude/commands/issue.md` |
| 12 | `/mockup` | HTML 와이어프레임 + Google Stitch 하이브리드 목업 생성 | `.claude/commands/mockup.md` |
| 13 | `/parallel` | Multi-agent parallel execution (dev, test, review, research) | `.claude/commands/parallel.md` |
| 14 | `/pr` | PR review, improvement suggestions, and auto-merge workflow | `.claude/commands/pr.md` |
| 15 | `/prd-sync` | PRD 동기화 (Google Docs -> 로컬) | `.claude/commands/prd-sync.md` |
| 16 | `/prd-update` | 로컬 PRD 업데이트 (브랜치 기반 자동 탐지) | `.claude/commands/prd-update.md` |
| 17 | `/research` | RPI Phase 1 - 코드베이스 분석, 리서치, AI 리뷰 | `.claude/commands/research.md` |
| 18 | `/session` | 세션 관리 통합 (compact, journey, changelog, resume) | `.claude/commands/session.md` |
| 19 | `/shorts` | PocketBase 사진으로 쇼츠 영상 생성 (Claude Vision 이미지 분석) | `.claude/commands/shorts.md` |
| 20 | `/tdd` | Guide Test-Driven Development with Red-Green-Refactor discipline | `.claude/commands/tdd.md` |
| 21 | `/todo` | Manage project todos with priorities, due dates, and tracking | `.claude/commands/todo.md` |
| 22 | `/work` | `/auto`로 통합됨 (v19.0). 리다이렉트 stub. | `.claude/commands/work.md` |

## 카테고리별 분류

### 핵심 워크플로우

| 커맨드 | 용도 |
|--------|------|
| `/auto` | PDCA 전체 자동화 (Phase 0-4) |
| `/commit` | Conventional Commit 생성 |
| `/check` | 코드 품질/보안 점검 |
| `/debug` | 구조적 디버깅 (D0-D4) |
| `/tdd` | TDD Red-Green-Refactor |

### 프로젝트 관리

| 커맨드 | 용도 |
|--------|------|
| `/issue` | GitHub 이슈 CRUD |
| `/pr` | PR 리뷰/머지 |
| `/todo` | 작업 추적 |
| `/prd-update` | 로컬 PRD 업데이트 |
| `/prd-sync` | Google Docs PRD 동기화 |
| `/create` | PRD/PR/문서 생성 |

### 분석/리서치

| 커맨드 | 용도 |
|--------|------|
| `/research` | 코드베이스/외부 리서치 |
| `/audit` | 설정 점검 + 트렌드 분석 |
| `/parallel` | 병렬 에이전트 실행 |

### 도구/유틸리티

| 커맨드 | 용도 |
|--------|------|
| `/auth` | AI 서비스 인증 |
| `/deploy` | 버전/Docker 배포 |
| `/gmail` | Gmail 관리 |
| `/session` | 세션 관리 |
| `/chunk` | PDF 청킹 |
| `/mockup` | UI 목업 생성 |
| `/shorts` | 쇼츠 영상 생성 |

### Deprecated

| 커맨드 | 리다이렉트 |
|--------|-----------|
| `/work` | `/auto` (v19.0 통합) |
