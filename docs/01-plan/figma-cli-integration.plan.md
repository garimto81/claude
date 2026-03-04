# Figma CLI 연동 설계 계획

## 배경

Figma 디자인 파일에서 React/Tailwind 코드를 추출하는 워크플로우를 구축한다.
Framelink MCP 서버(PAT 인증)를 기본으로 사용하고, 기존 스킬/에이전트 체계에 통합한다.

## 구현 범위

### 1. MCP 서버 설정 (`settings.json`)

Framelink MCP를 `mcpServers`에 추가:

```json
{
  "mcpServers": {
    "figma": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "figma-developer-mcp", "--figma-api-key=${FIGMA_ACCESS_TOKEN}", "--stdio"]
    }
  }
}
```

> Windows에서 `npx` 직접 실행 불가 → `cmd /c npx` 패턴 필수 (MEMORY.md 참조)

### 2. 환경변수 등록

`mcp-credentials.env.template`에 추가:

```env
# ── Figma (Framelink MCP) ──
FIGMA_ACCESS_TOKEN=        # Personal Access Token (https://www.figma.com/developers/api#access-tokens)
```

### 3. 스킬 정의 (`.claude/skills/figma/SKILL.md`)

```yaml
---
name: figma
description: >
  Figma 디자인 파일에서 컨텍스트를 추출하고 React/Tailwind 코드로 변환한다.
  Framelink MCP 서버를 통해 Figma REST API 연동.
triggers:
  keywords:
    - "--figma"
    - "figma"
    - "피그마"
model_preference: opus
auto_trigger: false
---
```

**핵심 커맨드**:

| 커맨드 | MCP 도구 | 설명 |
|--------|----------|------|
| `--figma <url>` | `get_design_context` | URL에서 디자인 추출 → 코드 변환 |
| `--figma tokens <url>` | `get_variable_defs` | 디자인 토큰 추출 |
| `--figma screenshot <url>` | `get_screenshot` | 스크린샷 캡처 |

### 4. 보조 유틸리티 (`lib/figma/`)

Figma URL 파싱 + 환경변수 관리 유틸리티:

```
lib/figma/
├── __init__.py
└── url_parser.py      # Figma URL → file_key + node_id 추출
```

**URL 파싱 로직**:
```
https://www.figma.com/design/<file_key>/<title>?node-id=<node_id>
https://www.figma.com/file/<file_key>/<title>?node-id=<node_id>
```

→ `file_key`, `node_id` 추출하여 MCP 도구에 전달

### 5. /auto 워크플로우 통합

**Step 2.0 (옵션 처리)** 에 `--figma` 추가:

```
/auto "컴포넌트 구현" --figma https://figma.com/design/ABC123/...
```

**실행 흐름**:
1. URL에서 file_key, node_id 파싱
2. Framelink MCP `get_design_context` 호출 → 디자인 컨텍스트 수집
3. (선택) `get_screenshot` → 시각적 참조 이미지
4. 수집된 컨텍스트를 impl-manager/executor에게 전달
5. designer 에이전트가 React + Tailwind 코드 생성

### 6. designer 에이전트 연동

`designer.md`에 Figma 컨텍스트 활용 지침 추가:
- MCP에서 받은 레이아웃/스타일 정보를 코드에 반영
- auto-layout → flexbox/grid 매핑 준수
- 디자인 토큰이 있으면 CSS 변수로 추출

## 영향 파일

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `.claude/settings.json` 또는 `.claude/settings.local.json` | 수정 | mcpServers에 figma 추가 |
| `.claude/mcp-credentials.env.template` | 수정 | FIGMA_ACCESS_TOKEN 추가 |
| `.claude/skills/figma/SKILL.md` | 신규 | 스킬 정의 |
| `lib/figma/__init__.py` | 신규 | 패키지 초기화 |
| `lib/figma/url_parser.py` | 신규 | URL 파싱 유틸리티 |
| `.claude/skills/auto/SKILL.md` | 수정 | --figma 옵션 문서화 |
| `.claude/agents/designer.md` | 수정 | Figma 컨텍스트 활용 지침 |
| `CLAUDE.md` | 수정 | 스킬 수 업데이트 (40→41) |

## 위험 요소

| 위험 | 영향 | 완화 |
|------|------|------|
| Framelink npx 실행 실패 (네트워크) | MCP 서버 미작동 | 에러 메시지 + 수동 설치 가이드 |
| PAT 미설정 시 인증 실패 | 401 에러 | 환경변수 확인 안내 + 중단 |
| 대형 Figma 파일 컨텍스트 초과 | 토큰 한계 | node_id로 특정 프레임만 추출 |
| Framelink API 변경 | 도구명 불일치 | 버전 고정 (`figma-developer-mcp@x.y.z`) |

## 테스트 계획

1. URL 파싱: 다양한 Figma URL 형식 파싱 테스트
2. MCP 연결: `FIGMA_ACCESS_TOKEN` 설정 후 도구 호출 확인
3. 코드 생성: 샘플 Figma 프레임 → React 컴포넌트 변환 확인
4. /auto 통합: `--figma <url>` 옵션 전체 흐름 테스트
