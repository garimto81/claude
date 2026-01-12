# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 11.7.1 | **Context**: Windows, PowerShell, Root: `C:\claude`

**GitHub**: `garimto81/claude`

---

## 기본 규칙

| 규칙 | 내용 |
|------|------|
| **언어** | 한글 출력. 기술 용어(code, GitHub)는 영어 |
| **경로** | 절대 경로만. `C:\claude\...` |
| **충돌** | 사용자에게 질문 (임의 판단 금지) |
| **응답** | 상세: `docs/RESPONSE_STYLE.md` |

---

## 핵심 규칙 (Hook 강제)

| 규칙 | 위반 시 | 해결 |
|------|---------|------|
| 테스트 먼저 (TDD) | 경고 | Red → Green → Refactor |
| 상대 경로 금지 | 경고 | 절대 경로 사용 |
| **전체 프로세스 종료 금지** | **차단** | 해당 프로젝트 node만 종료 |
| **100줄 이상 수정 시 자동 커밋** | 자동 | `/commit` 실행 |

⚠️ `taskkill /F /IM node.exe` 등 전체 종료 명령 **절대 금지**. 다른 프로젝트 영향.

main 허용: `CLAUDE.md`, `README.md`, `.claude/`, `docs/`

---

## 빌드/테스트 명령

### Python

```powershell
ruff check src/ --fix                    # 린트
pytest tests/test_specific.py -v         # 개별 테스트 (권장)
# pytest tests/ -v --cov=src             # 전체 (background 필수)
```

### E2E (Playwright 필수)

```powershell
npx playwright test                       # 전체 E2E
npx playwright test tests/e2e/auth.spec.ts  # 개별 테스트
```

**안전 규칙**: `pytest tests/ -v --cov` → 120초 초과 → 크래시. 개별 파일 실행 권장.

---

## 작업 방법

```
사용자 요청 → /work "요청 내용" → 자동 완료
```

| 요청 유형 | 처리 |
|-----------|------|
| 기능/리팩토링 | `/work` → 이슈 → 브랜치 → TDD → PR |
| 버그 수정 | `/issue fix #N` |
| 문서 수정 | 직접 수정 |
| 질문 | 직접 응답 |

---

## 빠른 참조

### 주요 커맨드

| 커맨드 | 용도 |
|--------|------|
| `/work` | 전체 워크플로우 (이슈→TDD→PR) |
| `/auto` | 자율 판단 자동 완성 (로그/Context 관리) |
| `/orchestrate` | 메인-서브 에이전트 오케스트레이션 |
| `/check` | 린트/테스트/보안 검사 |
| `/commit` | Conventional Commit 생성 |
| `/debug` | 가설-검증 기반 디버깅 (D0-D4) |
| `/issue` | GitHub 이슈 관리 (list/create/fix) |

**전체 18개**: `docs/COMMAND_REFERENCE.md`

### 에이전트 & 스킬

**에이전트 23개** (커스텀 19 + 내장 4): `docs/AGENTS_REFERENCE.md`

**스킬 19개**: `docs/AGENTS_REFERENCE.md`

---

## 코드 아키텍처

```
C:\claude\
├── src/
│   ├── agents/              # 워크플로우 자동화 (Python)
│   │   ├── prompt_learning/ # 프롬프트 최적화
│   │   └── prompt_optimization/
│   └── services/
│       └── google_docs/     # Google Docs PRD 연동
├── .claude/
│   ├── commands/            # 슬래시 커맨드 (18개)
│   ├── agents/              # 커스텀 에이전트 (19개)
│   └── skills/              # 자동화 스킬 (19개)
└── scripts/                 # 유틸리티 스크립트
```

### 핵심 모듈

| 모듈 | 위치 | 역할 |
|------|------|------|
| **PRD 연동** | `src/services/google_docs/` | Google Docs ↔ 로컬 동기화 |
| **워크플로우** | `src/agents/` | 병렬 실행, Phase 검증 |
| **프롬프트 학습** | `src/agents/prompt_learning/` | 세션 분석, 패턴 감지 |

---

## 문제 해결

```
문제 → WHY(원인) → WHERE(영향) → HOW(해결) → 수정
```

**즉시 수정 금지.** 원인 파악 → 유사 패턴 검색 → 구조적 해결.

---

## 문서 작업 규칙

### 시각화 필수

| 단계 | 작업 | 산출물 |
|------|------|--------|
| 1 | HTML 목업 생성 | `docs/mockups/*.html` |
| 2 | 스크린샷 캡처 | `docs/images/*.png` |
| 3 | 문서에 이미지 첨부 | PRD, 설계 문서 |

### 시각화 흐름

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  HTML 목업  │────▶│  스크린샷   │────▶│  문서 첨부  │
│  작성       │     │  캡처       │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

### HTML 목업 생성

```powershell
# 목업 파일 생성
Write docs/mockups/feature-name.html

# Playwright로 스크린샷 캡처
npx playwright screenshot docs/mockups/feature-name.html docs/images/feature-name.png
```

### 적용 대상

| 문서 유형 | 시각화 필수 여부 |
|-----------|-----------------|
| PRD (기능 명세) | ✅ 필수 |
| 아키텍처 설계 | ✅ 필수 |
| API 문서 | ⚠️ 권장 |
| 변경 로그 | ❌ 선택 |

---

## Checklist 표준 (Slack List 연동 필수)

⚠️ **Slack List 연동을 위해 반드시 Checklist 문서를 작성해야 합니다.**

### 문서 위치 (필수)

| 순위 | 경로 | 설명 |
|:----:|------|------|
| 1 | `docs/checklists/PRD-NNNN.md` | **필수** - 전용 Checklist 폴더 |
| 2 | `tasks/prds/NNNN-prd-*.md` | PRD 문서 내 Checklist 섹션 |
| 3 | `docs/CHECKLIST.md` | 프로젝트 전체 Checklist |

❌ **미작성 시**: PR 본문 Checklist로 Fallback (누적 진행률 추적 불가)

### PR-Checklist 연결 (필수)

```
PR 제목: feat: add login [PRD-0001] #123
브랜치: feat/PRD-0001-123-add-login
```

### 자동 체크 항목 작성

```markdown
- [ ] 기능 구현 (#101)     ← PR #101 머지 시 자동 체크
- [ ] 테스트 작성         ← 수동 체크 (PR 번호 없음)
```

**상세**: `.github/CHECKLIST_STANDARD.md`

---

## 통합 문서 구조

5개 프로젝트의 PRD가 `docs/unified/`에 통합 관리됩니다.

### 네임스페이스

| 접두어 | 프로젝트 | 위치 |
|--------|----------|------|
| **MAIN** | 루트 (Claude Root) | `docs/unified/prds/MAIN/` |
| **HUB** | automation_hub | `docs/unified/prds/HUB/` |
| **FT** | automation_feature_table | `docs/unified/prds/FT/` |
| **SUB** | automation_sub | `docs/unified/prds/SUB/` |
| **AE** | automation_ae | `docs/unified/prds/AE/` |

### 새 PRD 생성

```powershell
# 1. PRD 문서 생성
docs/unified/prds/{NS}/{NS}-{NNNN}-{slug}.md

# 2. 체크리스트 생성
docs/unified/checklists/{NS}/{NS}-{NNNN}.md

# 3. 레지스트리 업데이트
docs/unified/registry.json
```

### 참조

- [통합 인덱스](docs/unified/index.md) - 전체 PRD 목록
- [통합 레지스트리](docs/unified/registry.json) - PRD 메타데이터

---

## 참조

| 문서 | 용도 |
|------|------|
| `docs/RESPONSE_STYLE.md` | 응답 스타일 상세 |
| `docs/BUILD_TEST.md` | 빌드/테스트 명령어 |
| `docs/COMMAND_REFERENCE.md` | 커맨드 상세 |
| `docs/AGENTS_REFERENCE.md` | 에이전트 상세 |
| `docs/CHANGELOG-CLAUDE.md` | 변경 이력 |
| `.github/CHECKLIST_STANDARD.md` | Checklist 작성 표준 |
