# Mermaid 다이어그램 버그 수정 PRD

## 개요

- **목적**: Mermaid 다이어그램 생성 시 반복적으로 발생하는 버그들을 원천적으로 해결
- **배경**: 두 가지 독립적 버그가 확인됨: (1) Windows 경로 백슬래시 버그 (이미 수정됨), (2) 노드 레이블 내 `\n` 리터럴 버그 (반복 발생 중)
- **범위**: `scripts/generate_mermaid_png.py`, `.claude/rules/11-ascii-diagram.md`, `.claude/hooks/post_edit_check.js`, `scripts/sanitize_mermaid.py` (신규)

---

## 버그 1: Windows 경로 백슬래시 (v1.0 — 수정 완료)

### 문제
Windows에서 `Path` 객체를 `f"file:///{html_path}"` 형태로 포함하면 `file:///C:\Users\...` 형태가 되어 Playwright URL이 무효화됨

### 구현 상태 (완료)

| 항목 | 상태 | 비고 |
|------|------|------|
| 버그 원인 분석 | 완료 | |
| 코드 수정 (line 66) | **완료** | `str(html_path).replace(chr(92), '/')` 적용됨 |
| 테스트 검증 | 완료 | |

---

## 버그 2: 노드 레이블 내 `\n` 리터럴 (v1.1 — 신규)

### 문제 요약

LLM 에이전트가 Mermaid 다이어그램을 생성할 때 노드 레이블에 `\n` (백슬래시+n 두 글자)을 사용하는 패턴이 **반복적으로** 발생한다. 이는 구조적 문제로, 일회성 수정으로는 해결되지 않는다.

### 근본 원인

| 원인 | 설명 |
|------|------|
| LLM 자연 패턴 | LLM은 줄바꿈을 `\n`으로 표현하도록 학습됨 |
| 렌더러 불일치 | mermaid.js v10 로컬에서는 처리되나, GitHub/VS Code에서는 리터럴 `\n`으로 표시 |
| 규칙 부재 | `11-ascii-diagram.md`에 `\n` 금지 규칙 없음 |
| 자동화 부재 | Hook/Post-processing에서 자동 감지/수정 없음 |

### 피해 규모 (2026-02-26 기준)

- `docs/02-design/ocr-hybrid-pipeline.design.md`: 12개 mermaid 블록, **287개 `\n` 리터럴 발생**
- 패턴 예시: `A["이미지 입력\n(str | PIL.Image)"]`, `H --> I["List[UIElement]\nelement_type='graphic'"]`

### Mermaid 올바른 줄바꿈 표준 (웹 연구 결과)

| 방법 | 호환성 | 비고 |
|------|--------|------|
| `<br/>` 태그 | **모든 렌더러** | 가장 안전한 방법 (권장) |
| 실제 줄바꿈 + 백틱 | mermaid v10.1.0+ | 마크다운 문자열 |
| `\n` 리터럴 | 일부만 동작 | **금지** |

### 요구사항

#### 기능 요구사항

1. **규칙 업데이트**: `11-ascii-diagram.md`에 Mermaid 노드 레이블 `\n` 금지 + `<br/>` 사용 강제 규칙 추가
2. **Hook 자동 감지**: `post_edit_check.js`에서 `.md` 파일 저장 시 Mermaid 블록 내 `\n` 리터럴 탐지 → 경고 출력
3. **배치 수정 스크립트**: `scripts/sanitize_mermaid.py` 신규 생성 — 기존 파일의 `\n` → `<br/>` 일괄 변환
4. **에이전트 프롬프트**: 디자인/플래너 에이전트 프롬프트에 `\n` 금지 명시

#### 비기능 요구사항

1. `<br/>` 변환 시 따옴표(`"`, `[`) 내부 레이블만 대상으로 할 것 (코드 블록 외부 `\n`은 건드리지 않음)
2. 배치 수정 후 원본 파일 백업 생성 (`.bak`)
3. Hook은 경고만 출력 (빌드 차단 금지 — 생산성 저해 방지)

### 구현 계획

| 항목 | 파일 | 상태 |
|------|------|------|
| 규칙 파일 업데이트 | `.claude/rules/11-ascii-diagram.md` | **완료** |
| Hook 감지 추가 | `.claude/hooks/post_edit_check.js` | **완료** |
| 배치 수정 스크립트 | `scripts/sanitize_mermaid.py` | **완료** |
| 기존 파일 일괄 수정 | `docs/02-design/ocr-hybrid-pipeline.design.md` | **완료** (19개 수정) |

## 버그 3: PostToolUse Hook 자동수정 미구현 (v1.3 — 신규)

### 문제 요약

4-layer 구조적 수정(규칙+Hook+스크립트+파일수정)을 완료했음에도 `\n` 버그가 계속 재발생하고 있다. 현재 접근법의 근본 한계:

1. `sanitize_mermaid.py`는 수동 실행 도구 — 자동화되지 않음
2. `post_edit_check.js`의 Mermaid 감지 로직이 **경고만 출력** — 파일을 자동 수정하지 않음
3. 경고를 보더라도 LLM이 수정하지 않거나, 다음 편집에서 다시 `\n` 사용
4. hook은 `.gitignore`에 포함되어 git 추적 불가 — 배포 일관성 없음

### 근본 해결책

PostToolUse hook에서 `\n` 감지 시 **경고 → 자동 수정**으로 변경.
파일 저장 직후 hook이 자동으로 `\n` → `<br/>` 교체 실행.

### 요구사항

#### 기능 요구사항

1. **`post_edit_check.js`의 `checkMermaidNewlines()` 함수를 `fixMermaidNewlines()`로 업그레이드**
   - 경고 메시지 출력만 → 파일 직접 수정 + 수정 내용 보고
   - 수정된 경우: "자동수정: N개 `\n` → `<br/>` 교체됨" 보고
   - 수정 없는 경우: 조용히 통과
2. **기존 `sanitize_mermaid.py`의 정규식 로직을 JS로 포팅**
3. **수정 시 백업 생성 안 함** (hook은 빠른 처리 우선, git history로 복구 가능)

### 구현 계획

| 항목 | 파일 | 상태 |
|------|------|------|
| Hook 자동수정 업그레이드 | `.claude/hooks/post_edit_check.js` | **완료** |

---

## Changelog

| 날짜 | 버전 | 변경 내용 | 결정 근거 |
|------|------|-----------|----------|
| 2026-02-26 | v1.3 | Hook 경고→자동수정 전환 필요 발견 | 4-layer 수정에도 버그 재발 확인 |
| 2026-02-26 | v1.2 | 4-layer 구조적 수정 완료 (규칙+Hook+스크립트+파일 수정) | feat/mermaid-newline-fix → main 머지 |
| 2026-02-26 | v1.1 | `\n` 리터럴 버그 추가 (구조적 수정 필요) | 반복 발생 패턴 확인, 287개 리터럴 발견 |
| 2026-02-24 | v1.0 | 최초 작성 | Windows 경로 버그 수정 |
