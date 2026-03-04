# Figma CLI 연동 PRD

## 개요
- **목적**: Figma 디자인 파일을 읽어 React/HTML 코드로 변환하는 CLI 워크플로우 구축
- **배경**: 현재 목업 생성은 HTML/Stitch AI 기반이지만, 실제 Figma 디자인에서 코드를 추출하는 기능이 없음
- **범위**: MCP 서버 설정 + 스킬 정의 + /auto 워크플로우 통합

## 요구사항

### 기능 요구사항
1. Figma 파일/노드에서 디자인 컨텍스트 추출 (레이아웃, 스타일, 컴포넌트)
2. 추출된 디자인을 React + Tailwind CSS 코드로 변환
3. 디자인 토큰(색상, 폰트, 간격) 동기화
4. Figma URL 기반 자동 파일/노드 식별
5. `/auto --figma <url>` 옵션으로 워크플로우 통합

### 비기능 요구사항
1. PAT(Personal Access Token) 기반 인증 (OAuth 불필요)
2. Windows 환경 호환 (cmd + npx 패턴)
3. 기존 designer 에이전트와의 협업 가능
4. 오프라인 Figma Desktop 앱 없이도 동작

## 아키텍처 결정

### MCP 서버 선택: 듀얼 MCP 전략

| 서버 | 역할 | 인증 | 용도 |
|------|------|------|------|
| **Framelink (GLips)** | 기본 서버 | PAT | 디자인 컨텍스트 추출, 코드 변환 |
| **공식 Figma MCP** | 보조 서버 (선택) | Desktop 모드 | Code Connect, 디자인 생성 |

**결정 근거**: 공식 MCP의 Remote 모드는 OAuth 필수라 PAT 요구사항과 충돌. Framelink이 PAT 지원 + 레이아웃 컨텍스트 최적화로 디자인→코드 변환에 더 적합.

### 코드 변환 파이프라인

```
Figma URL → Framelink MCP → get_design_context → AI 코드 생성 → React/Tailwind
```

## 구현 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| MCP 서버 설정 (settings.json) | 불필요 | 공식 Figma 플러그인 (v1.2.0) 기설치 |
| 스킬 정의 (SKILL.md) | 완료 | .claude/skills/figma/SKILL.md |
| 환경변수 템플릿 | 불필요 | 기존 env template에 FIGMA 섹션 존재 |
| /auto 옵션 통합 | 완료 | --figma 옵션 Phase 0 + Step 2.0 추가 |
| 보조 유틸리티 (lib/figma/) | 완료 | url_parser.py (URL 파싱) |
| designer 에이전트 연동 | 완료 | Figma Design Context 섹션 추가 |
| 테스트 | 완료 | 9/9 통과 (tests/test_figma_url_parser.py) |

## Changelog

| 날짜 | 버전 | 변경 내용 | 결정 근거 |
|------|------|-----------|----------|
| 2026-03-04 | v1.1 | 구현 완료 — 플러그인 기설치 반영, 범위 조정 | Framelink→공식 플러그인 전환 |
| 2026-03-04 | v1.0 | 최초 작성 | Figma 디자인→코드 변환 요구 |
