---
name: figma
description: >
  Figma 디자인 파일에서 컨텍스트를 추출하고 React/Tailwind 코드로 변환한다.
  공식 Figma MCP 플러그인 (implement-design, code-connect, design-system-rules) 통합.
triggers:
  keywords:
    - "--figma"
    - "figma"
    - "피그마"
    - "디자인 구현"
    - "design implementation"
  context:
    - "Figma URL이 포함된 요청"
    - "디자인→코드 변환 요청"
model_preference: opus
auto_trigger: false
---

# Figma 디자인 연동 스킬 (`--figma`)

> `/auto "작업" --figma <url>` — Figma 디자인에서 컨텍스트 추출 → 코드 변환

## 개요

공식 Figma MCP 플러그인 래퍼. 3개 서브스킬을 라우팅하여 디자인→코드 변환을 수행한다.

## 사용법

```
/auto "컴포넌트 구현" --figma https://figma.com/design/KEY/Name?node-id=1-2
/auto "컴포넌트 매핑" --figma connect https://figma.com/design/KEY/Name
/auto "디자인 시스템" --figma rules
```

### 파라미터

| 파라미터 | 필수 | 설명 |
|----------|:----:|------|
| `<url>` | YES | Figma 디자인 URL |
| `connect` | NO | 디자인↔코드 컴포넌트 매핑 모드 |
| `rules` | NO | 디자인 시스템 규칙 생성 모드 |

## 커맨드 라우팅

| 커맨드 | 플러그인 스킬 | 설명 |
|--------|-------------|------|
| `--figma <url>` | `figma:implement-design` | URL에서 디자인 추출 → 코드 변환 |
| `--figma connect <url>` | `figma:code-connect-components` | 디자인↔코드 컴포넌트 매핑 |
| `--figma rules` | `figma:create-design-system-rules` | 프로젝트 디자인 시스템 규칙 생성 |

## URL 파싱 규칙

`https://figma.com/design/:fileKey/:fileName?node-id=X-Y` 형식에서 추출:
- `fileKey`: 파일 고유 식별자
- `nodeId`: `X-Y` → `X:Y` 변환 (MCP 도구 형식)

파싱 유틸리티: `lib/figma/url_parser.py`

```bash
python lib/figma/url_parser.py "https://figma.com/design/ABC123/MyFile?node-id=1-2"
```

## MCP 도구 참조

| 도구 | 용도 |
|------|------|
| `get_design_context` | 레이아웃/스타일 정보 추출 |
| `get_screenshot` | 디자인 스크린샷 캡처 |
| `get_metadata` | 파일/컴포넌트 메타데이터 |
| `get_code_connect_suggestions` | 코드 연결 제안 |

## /auto 통합 동작

`--figma` 옵션이 `/auto`에 전달되면 **Step 2.0 (옵션 처리)** 단계에서 실행:

1. URL 파싱 (`lib/figma/url_parser.py`)으로 fileKey, nodeId 추출
2. 서브커맨드 판별 (기본: `implement-design`, `connect`: `code-connect`, `rules`: `design-system-rules`)
3. MCP 플러그인 스킬 호출 → 디자인 컨텍스트 수집
4. 결과를 designer 에이전트에 전달 → 코드 구현

## 환경 변수

| 변수 | 필수 | 설명 |
|------|:----:|------|
| `FIGMA_ACCESS_TOKEN` | NO | Figma PAT (보조 인증용, MCP 플러그인이 기본 인증 처리) |

## 에러 처리

| 에러 | 처리 |
|------|------|
| 잘못된 URL 형식 | ValueError + 올바른 형식 안내 |
| MCP 서버 미연결 | 플러그인 설치 확인 안내 + 중단 |
| 인증 실패 | FIGMA_ACCESS_TOKEN 확인 안내 |
| node-id 미존재 | 전체 파일 컨텍스트로 fallback |

**옵션 실패 시: 에러 출력, 절대 조용히 스킵 금지.**
