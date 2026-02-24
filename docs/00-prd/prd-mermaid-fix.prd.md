# Mermaid 다이어그램 Windows 경로 버그 수정 PRD

## 개요

- **목적**: `scripts/generate_mermaid_png.py`에서 Windows 경로의 백슬래시(`\`)가 `file://` URL에 그대로 사용되어 Playwright가 HTML 파일을 로드하지 못하는 버그 수정
- **배경**: Windows에서 `Path` 객체를 `f"file:///{html_path}"` 형태로 포함하면 `file:///C:\Users\...` 형태가 되어 URL이 무효화됨. 정상 URL은 `file:///C:/Users/...` (포워드슬래시) 형식이어야 함
- **범위**: `scripts/generate_mermaid_png.py` line 66 단일 라인 수정

## 요구사항

### 기능 요구사항

1. `file://` URL 생성 시 Windows 경로 구분자 `\`를 `/`로 변환해야 한다
2. 기존 정상 구현(`lib/google_docs/mermaid_renderer.py`)과 동일한 패턴을 사용해야 한다
3. 수정 후 Playwright가 임시 HTML 파일을 정상적으로 로드해야 한다

### 비기능 요구사항

1. 단일 라인 수정으로 최소 침습적 변경
2. Linux/Mac 환경에서도 정상 동작 유지 (포워드슬래시는 그대로)

## 버그 상세

| 항목 | 내용 |
|------|------|
| 파일 | `scripts/generate_mermaid_png.py` |
| 라인 | 66 |
| 현재 코드 | `await page.goto(f"file:///{html_path}")` |
| 수정 코드 | `await page.goto(f"file:///{str(html_path).replace(chr(92), '/')}")` |
| 참조 패턴 | `lib/google_docs/mermaid_renderer.py` line 233 |

## 구현 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| 버그 원인 분석 | 완료 | 이전 세션 조사 결과 |
| 코드 수정 | 진행 중 | line 66 단일 라인 |
| 테스트 검증 | 예정 | |

## Changelog

| 날짜 | 버전 | 변경 내용 | 결정 근거 |
|------|------|-----------|----------|
| 2026-02-24 | v1.0 | 최초 작성 | Windows 경로 버그 수정 |
