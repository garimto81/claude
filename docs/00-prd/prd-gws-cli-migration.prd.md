# Google Workspace CLI (gws) 전환 PRD

## Market Context

- **시장 배경**: Google이 2026년 3월 Workspace CLI (`gws`) v0.11.1 공개. Discovery Service 기반 동적 API, 67개 에이전트 스킬 사전 포함. MCP 서버는 아직 미포함 (향후 버전 예정)
- **비즈니스 Impact**: Python API wrapper 유지보수 비용 제거, API 변경 자동 반영, Claude Code 네이티브 통합으로 UX 향상
- **Appetite**: Small 2주

## 개요

- **목적**: 현재 Python Google API 기반 4개 스킬(Gmail, Calendar, Drive, Google Workspace)을 gws CLI 기반 2-Tier Hybrid 아키텍처로 전환
- **배경**: 현재 13개 Python 모듈(~450KB)이 google-api-python-client, google-auth-oauthlib 등에 의존. Calendar만 gws 하이브리드 지원. gws v0.11.1에는 MCP 서버 미포함이므로 CLI subprocess 방식으로 통합.
- **범위**:
  - IN: gws CLI 설치/인증, 4개 스킬 전환, lib/gmail 하이브리드화
  - OUT: lib/google_docs/converter.py 전환 (복잡도 과다), 기존 Python lib 삭제 (fallback 유지), gws MCP 등록 (v0.11.1 미지원)

## 요구사항

### 기능 요구사항

1. gws CLI 설치 (`npm install -g @googleworkspace/cli`)
2. gws 인증 설정 (`gws auth login` — 기존 OAuth desktop_credentials.json 활용)
3. Gmail 스킬: gws CLI 우선 → Python fallback 2-Tier
4. Calendar 스킬: 기존 gws 하이브리드 유지 + Anti-Patterns 업데이트
5. Drive 스킬: gws CLI로 파일 목록/검색 전환, Drive Guardian은 Python 유지
6. Google Workspace 스킬: Docs/Sheets 읽기를 gws CLI로 전환, converter는 Python 유지
7. 모든 스킬의 Anti-Patterns 섹션에서 `gws mcp 사용 금지` 제거
8. lib/gmail/client.py에 Calendar와 동일한 gws 하이브리드 패턴 적용
9. (향후) gws에 MCP 서버 추가 시 Tier 1으로 승격

### 비기능 요구사항

1. gws 미설치 환경에서도 기존 Python fallback으로 무중단 동작
2. gws v0.9.x 파괴적 변경 대비: CLI 호출 실패 시 자동 Python 전환
3. 인증 토큰 보안: gws는 OS Keyring 사용, 기존 token_*.json도 유지
4. 기존 `cd C:\claude && python -m lib.*` 패턴과 공존

## 전환 전략: 2-Tier Hybrid (MCP Ready)

| Tier | 역할 | 사용 시점 |
|------|------|----------|
| Tier 1: gws CLI | Bash subprocess (primary) | CRUD 조회, 배치/스크립트 |
| Tier 2: Python API | Fallback + 복잡 로직 | gws 미설치 또는 converter/guardian |
| (향후) Tier 0: gws MCP | Claude Code 네이티브 | gws에 MCP 서버 추가 시 승격 |

## 서비스별 전환 범위

| 서비스 | Tier 1 (CLI) | Tier 2 유지 (Python) | 비고 |
|--------|:---:|:---:|------|
| Gmail (읽기/전송/검색) | O | O (fallback) | 신규 추가 |
| Calendar (조회/생성) | O (기존) | O (기존) | Anti-Patterns 정리만 |
| Drive (목록/검색) | O | O (fallback) | 신규 추가 |
| Drive Guardian (감사) | X | O (전환 불가) | AI 맥락 분석 필요 |
| Docs Converter | X | O (전환 불가) | Batch API 수십 건 |
| Sheets (읽기/쓰기) | O | O (fallback) | 신규 추가 |

## 위험 요소

| 위험 | 영향 | 완화 |
|------|------|------|
| gws v0.9.x 파괴적 변경 | CLI 명령 구조 변경 가능 | Python fallback 유지 |
| gws not officially supported | 장기 지원 불확실 | 의존도 최소화 (MCP+CLI만, 핵심 로직은 Python) |
| OAuth 테스트 모드 25 scope 제한 | 일부 API 접근 불가 | 기존 desktop_credentials.json 재사용 |
| gws CLI subprocess 타임아웃 | 장시간 작업 차단 | subprocess timeout 설정 + Python fallback |

## 구현 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| gws CLI 설치 | 완료 | v0.11.1 |
| gws auth 설정 | 완료 | Python OAuth + 12 scopes |
| MCP 서버 등록 | 스킵 | v0.11.1 미지원 |
| Gmail 스킬 전환 | 완료 | 2-Tier |
| Calendar 스킬 보강 | 완료 | Anti-Patterns 정리 |
| Drive 스킬 전환 | 완료 | 목록/검색만 |
| GWS 스킬 전환 | 완료 | Sheets/Docs 읽기 |
| lib/gmail 하이브리드 | 완료 | Calendar 패턴 참조 |

## Changelog

| 날짜 | 버전 | 변경 내용 | 변경 유형 | 결정 근거 |
|------|------|-----------|----------|----------|
| 2026-03-12 | v1.2 | 전체 구현 완료 (4 스킬 + lib/gmail 하이브리드) | TECH | 2-Tier Hybrid 전환 완료 |
| 2026-03-12 | v1.1 | 3-Tier→2-Tier 전환 (gws v0.11.1 MCP 미지원) | TECH | gws MCP 서버 미포함 확인 |
| 2026-03-12 | v1.0 | 최초 작성 | - | gws CLI 출시 대응 |
