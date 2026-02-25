# karpathy-guidelines 개선 Work Plan

## 배경 (Background)

- **요청 내용**: `C:\claude\.claude\skills\karpathy-guidelines\` 디렉토리에 4개 파일 신규 생성
- **해결하려는 문제**: 외부 레포 `forrestchang/andrej-karpathy-skills` (6.9k★)를 로컬에 적용하면서 6개 기술 갭이 발견됨:
  1. deprecated `.claude-plugin/plugin.json` 형식 사용 (구 OMC 플러그인 스펙)
  2. SKILL.md 프론트매터 필드 미달 (`name`, `description` 2개만)
  3. README 설치 명령 `claude plugins add <url>` 존재하지 않는 명령
  4. 원칙 5 누락: Documents over Documentation
  5. 원칙 6 누락: Context Awareness
  6. EXAMPLES.md 없음 (신규 원칙 5, 6 예시 포함 필요)

---

## 구현 범위 (Scope)

### 포함
- `SKILL.md` — agentskills.io 표준 프론트매터 6개 필드 (Phase A)
- `CLAUDE.md` — 기존 원칙 1-4 유지 + 원칙 5, 6 신규 추가 (Phase B)
- `EXAMPLES.md` — 6원칙 실전 예시 (원칙 5, 6 포함) 신규 작성 (Phase B)
- `README.md` — 올바른 설치 방법 (직접 복사 / 심볼릭 링크) (Phase A)

### 제외
- Phase C: 멀티 에이전트 Hooks 통합, 언어별 확장 (Python/TypeScript)
- agentskills.io 마켓플레이스 게시 (비공개 로컬 전용)
- 외부 레포(`forrestchang/andrej-karpathy-skills`) 수정

---

## 현재 상태 분석 (Current State)

```
C:\claude\.claude\skills\karpathy-guidelines\
  [존재하지 않음 — 전체 신규 생성 필요]
```

**참조 패턴** (기존 스킬에서 확인):
- `C:\claude\.claude\skills\auto\SKILL.md` — v22.4, 풀 스펙 YAML 프론트매터
- `C:\claude\.claude\skills\skill-creator\SKILL.md` — name/description/version/triggers/capabilities/model_preference/auto_trigger/license 패턴
- `C:\claude\.claude\skills\SKILL_TEMPLATE.md` — 공식 템플릿

**원칙 1-4 현황** (외부 레포 분석 결과):
```
원칙 1: Read before you write
원칙 2: Fail loud
원칙 3: Minimal footprint
원칙 4: Prefer reversibility
```

---

## 영향 파일 (Affected Files)

### 신규 생성
```
C:\claude\.claude\skills\karpathy-guidelines\SKILL.md      (신규)
C:\claude\.claude\skills\karpathy-guidelines\CLAUDE.md     (신규)
C:\claude\.claude\skills\karpathy-guidelines\EXAMPLES.md   (신규)
C:\claude\.claude\skills\karpathy-guidelines\README.md     (신규)
```

### 수정 없음
- 기존 스킬 파일 변경 없음
- `C:\claude\CLAUDE.md` 변경 없음

---

## 위험 요소 (Risks)

| 위험 | 영향 | 대응 |
|------|------|------|
| R-1: 원칙 1-4 내용 불확실 | CLAUDE.md 원칙 번호 충돌 | 외부 레포 분석 기반으로 정확히 재현, PRD에 명시된 원칙 5-6 추가 |
| R-2: agentskills.io 스펙 필드 오해 | SKILL.md 검증 실패 | skill-creator의 validate 스크립트로 사후 검증 |
| R-3: `user-invocable: false` vs `true` 불일치 | 스킬 트리거 방식 오작동 | PRD 지시사항에 따라 `user-invocable: true` 적용 |
| R-4: EXAMPLES.md 원칙 번호 체계 불일치 | CLAUDE.md↔EXAMPLES.md 간 불일치 | CLAUDE.md 완성 후 번호 기준으로 EXAMPLES.md 작성 |

**Edge Case 1**: SKILL.md에서 `disable-model-invocation: false`와 `model_preference: sonnet` 공존 시 충돌 가능성 → `model_preference` 필드 유지, `disable-model-invocation`은 agentskills.io 스펙 전용 필드로 별도 관리

**Edge Case 2**: `C:\claude\.claude\skills\karpathy-guidelines\CLAUDE.md`가 상위 `CLAUDE.md`와 혼동될 가능성 → README.md에 로딩 범위 명시, SKILL.md에서 참조 경로 명시

---

## 태스크 목록 (Tasks)

### Phase A: 즉시 구현

#### Task A-1: SKILL.md 신규 생성

**설명**: agentskills.io 표준 프론트매터 + 스킬 실행 지침 작성

**파일**: `C:\claude\.claude\skills\karpathy-guidelines\SKILL.md`

**핵심 내용**:
```yaml
---
name: karpathy-guidelines
description: >
  Andrej Karpathy의 6대 개발 원칙을 적용하여 코드 품질을 높입니다.
  트리거: 코드 리뷰, 새 코드 작성, 리팩토링, 디버깅.
license: MIT
compatibility: claude-code
user-invocable: true
disable-model-invocation: false
version: 2.0.0
triggers:
  keywords:
    - "karpathy"
    - "개발 원칙"
    - "코드 리뷰"
    - "리팩토링"
model_preference: sonnet
auto_trigger: false
---
```

**본문 지침 포함 항목**:
- 스킬 목적 (1-2문장)
- 6원칙 적용 트리거 조건
- CLAUDE.md 참조 지시 (`Read("C:\claude\.claude\skills\karpathy-guidelines\CLAUDE.md")`)
- EXAMPLES.md 참조 지시 (예시 확인 필요 시)

**Acceptance Criteria**:
- [ ] YAML 프론트매터 6개 필수 필드 존재 (name, description, license, compatibility, user-invocable, disable-model-invocation)
- [ ] `triggers.keywords` 최소 3개
- [ ] 본문에 CLAUDE.md 로딩 지시 포함
- [ ] `C:\claude\.claude\skills\skill-creator\scripts\quick_validate.py` 실행 시 오류 없음

---

#### Task A-2: README.md 신규 생성

**설명**: 올바른 설치 방법 및 스킬 개요 작성

**파일**: `C:\claude\.claude\skills\karpathy-guidelines\README.md`

**핵심 내용**:
```
# karpathy-guidelines

Andrej Karpathy의 6대 개발 원칙 Claude Code 스킬

## 설치 방법

### 방법 1: 직접 복사
cp -r karpathy-guidelines ~/.claude/skills/

### 방법 2: 심볼릭 링크 (Windows)
mklink /D "%USERPROFILE%\.claude\skills\karpathy-guidelines" "C:\claude\.claude\skills\karpathy-guidelines"

## 사용법
- 자동: 코드 리뷰, 리팩토링 요청 시 자동 트리거
- 수동: "karpathy 원칙 적용해서 리뷰해줘"

## 원칙 목록
1. Read before you write
2. Fail loud
3. Minimal footprint
4. Prefer reversibility
5. Documents over Documentation (신규)
6. Context Awareness (신규)
```

**Acceptance Criteria**:
- [ ] `claude plugins add` 명령 미사용 (존재하지 않는 명령)
- [ ] Windows 심볼릭 링크 명령 포함
- [ ] 6원칙 목록 전체 포함
- [ ] 설치 방법 2가지 이상 제시

---

### Phase B: 단기 구현

#### Task B-1: CLAUDE.md 신규 생성

**설명**: 6원칙 정의 파일. 원칙 1-4는 외부 레포 기준 재현, 원칙 5-6 신규 추가

**파일**: `C:\claude\.claude\skills\karpathy-guidelines\CLAUDE.md`

**원칙 구조**:

```
# Karpathy Development Guidelines

## 원칙 1: Read before you write
코드를 수정하기 전에 반드시 먼저 읽는다.
- 파일을 편집하기 전 전체 내용 파악
- 기존 패턴과 일관성 유지
- 추정으로 수정 금지

## 원칙 2: Fail loud
오류를 숨기지 않는다.
- 조용한 fallback 금지
- 예외는 명시적으로 raise
- 오류 메시지는 원인과 위치를 포함

## 원칙 3: Minimal footprint
필요한 것만 변경한다.
- 요청 범위 밖 수정 금지
- 파일 생성 최소화
- 의존성 추가 신중히

## 원칙 4: Prefer reversibility
되돌릴 수 있는 변경을 선호한다.
- 파괴적 작업 전 백업 또는 확인
- 점진적 변경 선호
- git 단계별 커밋

## 원칙 5: Documents over Documentation
하나의 문서, 하나의 진실. 메타 문서 금지.
- 다른 문서를 설명하는 문서 생성 금지
- 요약 필요 시 → 원본 상단에 "Summary" 섹션 추가
- 작업 산출물 → 작업 완료 후 삭제
- 문서 구조 개편 시 → 원본 직접 편집

## 원칙 6: Context Awareness
아는 것과 모르는 것을 구분한다.
- 기존 코드 수정 전 파일 반드시 읽기
- 이전 단계에서 가져온 컨텍스트 명시
- 불확실한 정보를 확실한 것처럼 제시 금지
- 지식 경계 인정: "이 파일을 보지 않았으므로..."
```

**Acceptance Criteria**:
- [ ] 원칙 1-6 전체 포함
- [ ] 각 원칙에 정의 + 적용 규칙 최소 3개
- [ ] 원칙 5, 6 PRD 지시사항과 일치
- [ ] 번호 체계 1-6 연속성 유지

---

#### Task B-2: EXAMPLES.md 신규 생성

**설명**: 6원칙 실전 예시 파일. 각 원칙별 Bad/Good 예시 포함

**파일**: `C:\claude\.claude\skills\karpathy-guidelines\EXAMPLES.md`

**구조**:
```
# Karpathy Guidelines — 실전 예시

## 원칙 1: Read before you write
[Bad] 파일 안 보고 수정
[Good] Read 도구로 파일 확인 후 수정

## 원칙 2: Fail loud
[Bad] try/except: pass
[Good] 명시적 에러 메시지 + raise

## 원칙 3: Minimal footprint
[Bad] 요청 외 코드 정리/리팩토링
[Good] 요청된 버그만 수정

## 원칙 4: Prefer reversibility
[Bad] rm -rf 직접 실행
[Good] 삭제 전 사용자 확인 요청

## 원칙 5: Documents over Documentation
[Bad] SUMMARY.md 신규 생성 → 기존 README.md 설명
[Good] README.md 상단에 "Summary" 섹션 추가 후 편집

## 원칙 6: Context Awareness
[Bad] "이 함수는 X를 한다" (파일 미확인 상태)
[Good] Read("auth.py") 후 → "auth.py:42에서 확인한 결과..."
```

**Acceptance Criteria**:
- [ ] 6원칙 모두 포함
- [ ] 각 원칙에 Bad/Good 대비 예시 최소 1쌍
- [ ] 원칙 5, 6 예시가 CLAUDE.md 정의와 일치
- [ ] 실제 Claude Code 컨텍스트 반영 (도구명, 파일 경로 패턴)

---

## 커밋 전략 (Commit Strategy)

### Phase A 완료 후
```
feat(skills): karpathy-guidelines Phase A — SKILL.md + README.md 생성
```

### Phase B 완료 후
```
feat(skills): karpathy-guidelines Phase B — CLAUDE.md + EXAMPLES.md (원칙 5, 6 추가)
```

### PRD 업데이트 커밋
```
docs(prd): karpathy-guidelines 구현 완료 반영
```

---

## 실행 흐름 (Execution Flow)

```
  +------------------+     +------------------+
  | Task A-1         |     | Task A-2         |
  | SKILL.md 생성    |     | README.md 생성   |
  | (프론트매터 표준화)|     | (올바른 설치법)  |
  +--------+---------+     +--------+---------+
           |                        |
           +----------+-------------+
                      |
                      v
             Phase A 완료 커밋
                      |
                      v
  +------------------+     +------------------+
  | Task B-1         |---->| Task B-2         |
  | CLAUDE.md 생성   |     | EXAMPLES.md 생성 |
  | (6원칙 정의)     |     | (6원칙 예시)     |
  +------------------+     +------------------+
           |                        |
           +----------+-------------+
                      |
                      v
             Phase B 완료 커밋
```

---

## 검증 체크리스트 (Quality Gates)

- [ ] `C:\claude\.claude\skills\karpathy-guidelines\` 디렉토리 생성됨
- [ ] 4개 파일 모두 존재: SKILL.md, CLAUDE.md, EXAMPLES.md, README.md
- [ ] SKILL.md 프론트매터에 6개 필수 필드 포함
- [ ] CLAUDE.md 원칙 1-6 번호 체계 연속
- [ ] EXAMPLES.md 각 원칙별 Bad/Good 예시 존재
- [ ] README.md에 `claude plugins add` 명령 없음
- [ ] 원칙 5, 6이 PRD 지시사항과 일치
