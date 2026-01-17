# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Version**: 11.8.0 | **Context**: Windows, PowerShell, Root: `C:\claude`

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

## 서브 에이전트 우선 정책 (Context 관리)

모든 작업을 서브 에이전트로 위임하여 **메인 Context 사용을 최소화**합니다.

| 규칙 | 내용 |
|------|------|
| **기본 모드** | `/delegate`로 모든 작업 위임 |
| **직접 처리** | 단순 질문, 1줄 수정만 허용 |
| **Context 80%** | 즉시 서브 에이전트로 전환 |

### 판단 기준

| 작업 유형 | 처리 방식 | 이유 |
|----------|----------|------|
| 파일 읽기 3개+ | `/delegate` | Context 절약 |
| 코드 분석/탐색 | `/delegate` | 독립 실행 |
| 디버깅 | `/delegate` | 시행착오 격리 |
| 테스트 실행 | `/delegate` | 로그가 긺 |
| 리팩토링 | `/delegate` | 변경량 많음 |
| 단순 질문 | 직접 응답 | 빠른 처리 |
| 1줄 수정 | 직접 수정 | 위임 오버헤드 |

### 사용법

```bash
/delegate "API 성능 개선"           # 자동 에이전트 선택
/delegate --agent debugger "에러"   # 에이전트 지정
/delegate /check --e2e              # 기존 커맨드 래핑
/delegate --parallel "3개 작업"     # 병렬 실행
```

### Context 절약 효과

| 작업 | 직접 | /delegate | 절약 |
|------|:----:|:---------:|:----:|
| 코드 분석 | ~30% | ~5% | **85%** |
| 디버깅 | ~40% | ~8% | **80%** |
| E2E 테스트 | ~25% | ~3% | **88%** |

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

## Supabase 작업 규칙 (스키마 누락 방지)

⚠️ **Supabase 관련 코드 작성 전 반드시 CLI로 실제 DB 스키마를 확인해야 합니다.**

### 필수 스키마 확인 절차

| 단계 | 명령어 | 목적 |
|:----:|--------|------|
| 1 | `supabase db dump --schema public` | 현재 테이블/컬럼 구조 확인 |
| 2 | `supabase inspect db table-sizes` | 테이블 존재 여부 확인 |
| 3 | `supabase db diff` | 로컬 마이그레이션 vs 원격 DB 차이 |

### 작업 유형별 필수 확인

| 작업 유형 | 필수 명령어 | 확인 사항 |
|-----------|------------|----------|
| **테이블 조회 코드** | `supabase db dump --schema public -t [테이블명]` | 컬럼명, 타입, nullable |
| **새 테이블 생성** | `supabase inspect db table-sizes` | 동일 이름 테이블 존재 여부 |
| **RLS 정책 작성** | `supabase inspect db policies` | 기존 정책 충돌 확인 |
| **인덱스 추가** | `supabase inspect db index-sizes` | 기존 인덱스 확인 |
| **FK 관계 설정** | `supabase db dump --schema public` | 참조 테이블 존재 확인 |

### 스키마 확인 흐름

```
Supabase 코드 작성 요청
         │
         ▼
┌─────────────────────────────┐
│ supabase db dump 실행       │ ◄── 필수 1단계
│ (실제 스키마 확인)           │
└─────────────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 타입 정의와 실제 DB 비교     │ ◄── 필수 2단계
│ (types/supabase.ts vs 실제) │
└─────────────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 코드 작성/수정              │
└─────────────────────────────┘
```

### 금지 사항

| 금지 | 이유 | 대안 |
|------|------|------|
| ❌ TypeScript 타입만 보고 가정 | outdated 가능 | CLI로 실제 확인 |
| ❌ 마이그레이션 파일만 확인 | 미적용 가능 | `db diff`로 비교 |
| ❌ 테이블/컬럼 존재 가정 | 런타임 에러 | `db dump`로 확인 |
| ❌ RLS 비활성화 가정 | 보안 이슈 | `inspect db policies` |

### 프로젝트별 Supabase 설정 확인

```powershell
# 프로젝트 디렉토리에서 실행
supabase status                    # 연결 상태 확인
supabase db dump --schema public   # 전체 스키마
supabase inspect db table-sizes    # 테이블 목록
supabase inspect db policies       # RLS 정책
```

### 체크리스트 (코드 작성 전)

```markdown
- [ ] `supabase db dump` 실행하여 실제 스키마 확인
- [ ] 사용할 테이블/컬럼이 실제로 존재하는지 확인
- [ ] TypeScript 타입과 실제 DB 스키마 일치 여부 확인
- [ ] 새 마이그레이션 필요 시 `supabase migration new` 사용
```

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
| `/delegate` | **서브 에이전트 위임 (Context 절약)** |
| `/work` | 전체 워크플로우 (이슈→TDD→PR) |
| `/auto` | 자율 판단 자동 완성 (로그/Context 관리) |
| `/orchestrate` | 메인-서브 에이전트 오케스트레이션 |
| `/check` | 린트/테스트/보안 검사 |
| `/commit` | Conventional Commit 생성 |
| `/debug` | 가설-검증 기반 디버깅 (D0-D4) |
| `/issue` | GitHub 이슈 관리 (list/create/fix) |

**전체 19개**: `docs/COMMAND_REFERENCE.md`

### 에이전트 & 스킬

**에이전트 23개** (커스텀 19 + 내장 4): `docs/AGENTS_REFERENCE.md`

**스킬 18개**: `docs/AGENTS_REFERENCE.md`

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
│   └── skills/              # 자동화 스킬 (18개)
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

## 참조

| 문서 | 용도 |
|------|------|
| `docs/RESPONSE_STYLE.md` | 응답 스타일 상세 |
| `docs/BUILD_TEST.md` | 빌드/테스트 명령어 |
| `docs/COMMAND_REFERENCE.md` | 커맨드 상세 |
| `docs/AGENTS_REFERENCE.md` | 에이전트 상세 |
| `docs/SUPABASE_GUIDE.md` | **Supabase CLI 스키마 확인 상세** |
| `docs/CHANGELOG-CLAUDE.md` | 변경 이력 |
| `.github/CHECKLIST_STANDARD.md` | Checklist 작성 표준 |
