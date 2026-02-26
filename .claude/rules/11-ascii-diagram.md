# 다이어그램 출력 규칙 — 터미널 vs 문서 분리

**트리거**: 계획 수립, 설계 문서, 아키텍처 설명 등 다이어그램이 필요한 모든 상황

## 핵심 원칙 (RESPONSE_STYLE.md 기준)

출력 위치에 따라 형식이 결정된다. (`docs/RESPONSE_STYLE.md` 시각화 규칙 참조)

| 출력 위치 | 형식 | 이유 |
|-----------|------|------|
| **터미널 채팅 응답** | ASCII art 필수 (최대 65자) | Mermaid/PNG 인라인 렌더링 불가 |
| **저장 파일 (.md)** | Mermaid 코드 블록 기본 | 문서 뷰어에서 렌더링 가능 |

## 적용 기준

| 대상 | 형식 |
|------|:----:|
| Phase 1 계획 문서 (`docs/01-plan/`) | **Mermaid** |
| Phase 2 설계 문서 (`docs/02-design/`) | **Mermaid** |
| PRD 문서 (`docs/00-prd/`) | **Mermaid** |
| 아키텍처 설명 (터미널 채팅 응답) | **ASCII** |
| 워크플로우/흐름도 (터미널 채팅 응답) | **ASCII** |
| UI 레이아웃/와이어프레임 (터미널 채팅 응답) | **ASCII** |
| 저장 파일 내 기술 다이어그램 ASCII (흐름/시퀀스/아키텍처) | `--mockup <파일>` → **Mermaid 코드 블록** 변환 |
| 저장 파일 내 UI 화면/컴포넌트 ASCII 목업 | `--mockup <파일> --bnw` → **HTML + PNG** 변환 |

## 적용 제외 대상 (--mockup --bnw 사용)

아래 컨텍스트에서는 ASCII 대신 `--mockup --bnw`로 HTML 목업을 생성한다:

| 대상 | 처리 방식 |
|------|-----------|
| PRD 내 UI 화면 목업 | `--mockup --bnw` (designer 에이전트 + frontend-design 플러그인) |
| 최종 보고서/이해관계자 전달물의 시각화 | `--mockup --bnw` |
| 화면 설계 목업 (docs/mockups/) | `--mockup --bnw` |

**구분 원칙**: 터미널에서 즉시 확인하는 기술 다이어그램 → ASCII / 문서로 저장·전달되는 UI 목업 → `--mockup --bnw`

## HTML 목업 사이즈 규약

| 속성 | 값 |
|------|-----|
| width | auto |
| height | auto |
| max-width | 720px |
| max-height | 1280px |

> ASCII 다이어그램에는 사이즈 규약 없음.

## ASCII 다이어그램 스타일 가이드

### Flowchart (흐름도)

```
                  +------------------+
                  |   사용자 요청     |
                  +--------+---------+
                           |
                           v
                  +--------+---------+
                  |   복잡도 판단     |
                  +--+-----+------+--+
                     |     |      |
            0-1      |  2-3|   4-5|
                     v     v      v
               +-----+ +------+ +------+
               |LIGHT| |STAND.| |HEAVY |
               +--+--+ +--+---+ +--+---+
                  |        |        |
                  v        v        v
               [단일]  [루프]   [병렬]
```

### Sequence (시퀀스)

```
  User        Lead       Planner    Executor    Architect
   |            |            |           |           |
   |--요청----->|            |           |           |
   |            |--계획----->|           |           |
   |            |<--plan.md--|           |           |
   |            |--구현----------------->|           |
   |            |<--완료-----------------|           |
   |            |--검증----------------------------->|
   |            |<--APPROVE--------------------------|
   |<--완료-----|            |           |           |
```

### Tree (트리 구조)

```
  src/
  ├── agents/
  │   ├── config.py
  │   ├── parallel_workflow.py
  │   └── teams/
  │       ├── coordinator.py
  │       ├── base_team.py
  │       └── dev_team.py
  └── lib/
      ├── gmail/
      └── slack/
```

### Table (데이터 비교)

```
  +----------+--------+---------+--------+
  | 모드     | Phase2 | QA 횟수 | 검증   |
  +----------+--------+---------+--------+
  | LIGHT    | 스킵   | 1회     | Arch.  |
  | STANDARD | 설계   | 3회     | +CR    |
  | HEAVY    | 상세   | 5회     | +CR    |
  +----------+--------+---------+--------+
```

### Component (UI 와이어프레임)

```
  +------------------------------------------+
  | [Logo]        Navigation          [User] |
  +------------------------------------------+
  |          |                               |
  | Sidebar  |       Main Content            |
  |          |                               |
  | [Menu1]  |  +-------------------------+ |
  | [Menu2]  |  |     Card Component      | |
  | [Menu3]  |  |  Title: ...             | |
  |          |  |  Description: ...       | |
  |          |  |  [Action Button]        | |
  |          |  +-------------------------+ |
  |          |                               |
  +----------+-------------------------------+
```

## Mermaid 노드 레이블 줄바꿈 규칙 (CRITICAL)

**트리거**: 저장 파일(.md)에 Mermaid 다이어그램 작성 시

### 줄바꿈 방법 비교

| 방법 | GitHub | VS Code | 로컬 mermaid.js | 결론 |
|------|:------:|:-------:|:---------------:|------|
| `\n` 리터럴 | 리터럴로 표시 | 리터럴로 표시 | 렌더링됨 | **사용 금지** |
| `<br/>` 태그 | 줄바꿈 | 줄바꿈 | 줄바꿈 | **권장** |
| 실제 줄바꿈 + 백틱 | 지원 (v10.1+) | 지원 | 지원 | 조건부 허용 |

### 올바른 예시 (CORRECT)

```
A["이미지 입력<br/>(str | PIL.Image)"] --> B[HybridPipeline.analyze]
H --> I["List[UIElement]<br/>element_type='graphic'<br/>layer=1"]
```

### 금지 예시 (WRONG — 반복 발생 패턴)

```
A["이미지 입력\n(str | PIL.Image)"] --> B[HybridPipeline.analyze]
H --> I["List[UIElement]\nelement_type='graphic'\nlayer=1"]
```

**`\n` 리터럴은 GitHub/VS Code에서 줄바꿈으로 처리되지 않는다. `<br/>` 사용 필수.**

---

## 금지 사항

- **터미널 채팅 응답**에서 Mermaid 코드 블록 사용 금지 (렌더링 불가)
- 다이어그램을 PNG/SVG 파일로만 제공하고 끝내기 금지
- 텍스트 설명만으로 복잡한 흐름을 대체하기 금지
- **저장 파일**에서 ASCII 다이어그램 강제 금지 (Mermaid 사용)
- **Mermaid 노드 레이블**에서 `\n` 리터럴 사용 금지 — `<br/>` 사용 (모든 렌더러 호환)
