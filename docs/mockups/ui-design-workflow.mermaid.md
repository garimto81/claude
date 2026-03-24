# UI 설계 워크플로우 자동화 — Mockup Diagrams

> 구현 범위: Quasar 자동 감지, `--mockup` 3-Tier 라우팅, UI Layout Verification (Step 3.1b)

---

## 1. `--mockup` 3-Tier 라우팅 (with Quasar 자동 감지)

사용자가 `--mockup`을 실행하면, 라우터가 6단계 우선순위로 최적 백엔드를 결정합니다.

### Stage 1: 진입점

```mermaid
flowchart TD
    A["--mockup 실행"] --> B{"강제 옵션?"}
```

`--mockup mermaid`, `--mockup html`, `--mockup hifi` 등 명시적 지정 여부를 먼저 확인합니다.

### Stage 2: 키워드 + 프로젝트 타입 분기

```mermaid
flowchart TD
    A["--mockup 실행"] --> B{"강제 옵션?"}
    B -->|yes| C["지정 백엔드"]
    B -->|no| D{"키워드 감지?"}
    D -->|흐름, 시퀀스, API| E["Mermaid"]
    D -->|화면, UI, 레이아웃| F{"프로젝트 타입?"}
```

키워드가 UI/화면 계열이면, 프로젝트 타입을 추가 확인합니다.

### Stage 3: 완성 — Quasar 자동 감지 포함

```mermaid
flowchart TD
    A["--mockup 실행"] --> B{"강제 옵션?"}
    B -->|yes| C["지정 백엔드"]
    B -->|no| D{"키워드 감지?"}
    D -->|흐름, 시퀀스| E["Mermaid<br/>.mermaid.md"]
    D -->|화면, UI| F{"프로젝트 타입?"}
    D -->|고품질, 발표| G["Stitch AI<br/>HiFi .html"]
    F -->|Quasar 감지| H["HTML<br/>Quasar 스타일"]
    F -->|React/기타| I["HTML<br/>B&W Minimal"]
```

> **[NEW]** Quasar 감지: `package.json` quasar dep 또는 `quasar.config.*` 존재 시 자동 적용. `--quasar` 명시 불필요.

---

## 2. UI Layout Verification (Phase 3 Step 3.1b)

CSS/SCSS 변경 + HTML 목업 존재 시 자동 실행되는 레이아웃 밸런스 검증입니다.

### Stage 1: 트리거 조건

```mermaid
flowchart TD
    A["Phase 3 VERIFY 진입"] --> B{"목업 존재?<br/>docs/mockups/*.html"}
    B -->|no| C["Step 3.1b 스킵"]
```

### Stage 2: CSS 변경 확인

```mermaid
flowchart TD
    A["Phase 3 VERIFY 진입"] --> B{"목업 존재?<br/>docs/mockups/*.html"}
    B -->|no| C["Step 3.1b 스킵"]
    B -->|yes| D{"CSS/SCSS<br/>변경?"}
    D -->|no| C
    D -->|yes| E["balance_checker.py<br/>실행"]
```

### Stage 3: 완성 — 측정 + 판정

```mermaid
flowchart TD
    A["Phase 3 VERIFY"] --> B{"목업 + CSS 변경?"}
    B -->|no| C["스킵 → Step 3.2"]
    B -->|yes| D["Playwright<br/>DOM 측정"]
    D --> E{"밸런스 판정"}
    E -->|PASS| F["로그 출력<br/>→ Step 3.2"]
    E -->|FAIL| G["QA 리포트에<br/>경고 포함"]
    G --> F
```

**측정 항목 4가지:**

| 항목 | 기준 |
|------|------|
| 열 높이 편차 | ≤ 50px |
| 정보 밀도 편차 | ≤ 20% |
| 여백 비율 | 25-35% |
| 스크롤 필요 열 | ≤ 1개 |

---

## 3. 전체 통합 — /auto Phase 흐름 내 위치

### Stage 1: Phase 0 감지

```mermaid
flowchart LR
    A["Phase 0<br/>INIT"] --> B["Plugin Scan"]
    B --> C{"Quasar?"}
    C -->|yes| D["frontend-design<br/>활성화"]
    C -->|no| E["기본 플러그인"]
```

### Stage 2: Phase 2-3 연결

```mermaid
flowchart LR
    A["Phase 0<br/>감지"] --> B["Phase 2<br/>BUILD"]
    B --> C["--mockup 시<br/>Quasar 스타일"]
    B --> D["구현 완료"]
    D --> E["Phase 3<br/>VERIFY"]
    E --> F["Step 3.1<br/>QA"]
    F --> G["Step 3.1b<br/>밸런스 체크"]
    G --> H["Step 3.2<br/>E2E"]
```

> Phase 0에서 Quasar 감지 → Phase 2 `--mockup` 시 자동 스타일 적용 → Phase 3 목업 밸런스 자동 검증.

---

## 모듈 의존성

```mermaid
flowchart TD
    subgraph Detection["감지 레이어"]
        A["plugin-fusion-rules.md<br/>§1+§7 Quasar 감지"]
        B["SKILL.md<br/>Phase 0.4 테이블"]
    end
    subgraph Routing["라우팅 레이어"]
        C["mockup-hybrid SKILL.md<br/>3-Tier + 프로젝트 타입"]
    end
    subgraph Execution["실행 레이어"]
        D["balance_checker.py<br/>DOM 밸런스 측정"]
        E["REFERENCE.md<br/>Step 3.1b 자동 트리거"]
    end
    A --> C
    B --> C
    C --> D
    D --> E
```

> 감지 → 라우팅 → 실행의 3레이어 구조. 각 레이어는 자료 결합도(1단계)로 연결.
