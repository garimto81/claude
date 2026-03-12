# Google Calendar Integration PRD

## 개요
- **목적**: Google Calendar API를 `gws` CLI thin wrapper + Python API fallback 하이브리드로 통합
- **배경**: 기존 Google Workspace 스킬에 Calendar 미구현. `gws` CLI v0.9.1 출시로 thin wrapper 가능
- **범위**: Calendar CRUD (조회, 생성, 삭제), CLI 인터페이스, 스킬 통합

## 요구사항

### 기능 요구사항
1. `gws` CLI subprocess 호출로 Calendar API 접근 (primary)
2. Python Google Calendar API fallback (`gws` 미설치 시 자동 전환)
3. CLI: `python -m lib.calendar login|status|today|week|list|create|delete|calendars`
4. JSON 출력 옵션 (`--json`) 전 커맨드 지원
5. Pydantic 모델 기반 구조화된 데이터 (CalendarEvent, EventTime 등)
6. OAuth 2.0 인증 (기존 `desktop_credentials.json` 재사용, Calendar scope 추가)

### 비기능 요구사항
1. Gmail 모듈과 동일한 7-파일 패턴 준수 (errors, models, auth, client, cli, __init__, __main__)
2. Windows 호환 (UTF-8 encoding, absolute paths)
3. `gws` 호출 타임아웃 30초 제한
4. Token 파일: `C:\claude\json\token_calendar.json` (기존 token.json과 분리)

## Decision Matrix

| 기능 | 구현 방식 | 근거 |
|------|----------|------|
| Calendar CRUD | gws wrapper + Python API fallback | gws pre-v1.0 리스크 헤지 |
| 인증 | OAuth 2.0 (기존 credentials 재사용) | 추가 인증 최소화 |
| CLI | Typer + Rich (Gmail 패턴) | 일관성 |
| 데이터 모델 | Pydantic v2 | Gmail 패턴 일치 |

## 구현 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| lib/calendar/ 모듈 (7파일) | 완료 | errors, models, auth, client, cli, __init__, __main__ |
| .claude/skills/calendar/SKILL.md | 완료 | 트리거 키워드 + 실행 지시 |
| google-workspace SKILL.md v2.9.0 | 완료 | Calendar 서비스 추가 |
| REFERENCE.md Calendar 섹션 | 완료 | gws wrapper 기반으로 교체 |

## 아키텍처

```
lib/calendar/
├── errors.py              # CalendarError hierarchy
├── models.py              # Pydantic models (CalendarEvent, EventTime, etc.)
├── auth.py                # OAuth 2.0 (token_calendar.json)
├── calendar_client.py     # gws CLI wrapper + Python API fallback
├── cli.py                 # Typer CLI (today, week, list, create, delete)
├── __init__.py            # Module exports
└── __main__.py            # Entry point
```

## Changelog

| 날짜 | 버전 | 변경 내용 | 결정 근거 |
|------|------|-----------|----------|
| 2026-03-10 | v1.0 | 최초 작성 | gws v0.9.1 출시 + Calendar 미구현 |
