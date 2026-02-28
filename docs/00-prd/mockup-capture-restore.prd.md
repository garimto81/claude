# Mockup Capture Restore PRD

## 개요

- **목적**: `/auto --mockup` 워크플로우에서 누락된 PNG 캡처 및 문서 삽입 단계를 복원한다.
- **배경**: v19.0에서 v21.0 마이그레이션 시 `Skill(skill="mockup-hybrid")` 호출이 제거되면서, designer 에이전트가 HTML만 생성하고 PNG 캡처와 문서 삽입이 누락되었다.
- **범위**: SKILL.md의 `--mockup` 섹션에 Step 3.0.2 (PNG 캡처), Step 3.0.3 (문서 삽입) 추가.

## 문제 분석

### v19.0 (이전) 파이프라인

```
Skill(skill="mockup-hybrid")
  -> MockupRouter.route()
    -> HTML 생성
    -> capture_screenshot() (Playwright PNG)
    -> DocumentEmbedder.embed() (문서 삽입)
```

### v21.0+ (현재) 파이프라인 - 누락 발생

```
designer 에이전트 (Agent Teams 패턴)
  -> HTML 생성 (docs/mockups/{name}.html)
  -> [PNG 캡처 누락]
  -> [문서 삽입 누락]
```

### 원인

- v21.0 "Agent Teams 단일 패턴" 전환 시 Skill() 호출 전면 제거
- designer 에이전트는 HTML 생성만 담당하도록 설계됨
- capture_screenshot()과 DocumentEmbedder.embed()를 호출하는 주체가 사라짐

## 요구사항

### 기능 요구사항

1. **[FR-1] PNG 캡처 단계 복원**: designer 에이전트가 HTML 생성 완료 후, Lead가 `capture_screenshot()` 함수를 Bash로 직접 실행하여 PNG 파일을 생성한다.
2. **[FR-2] 문서 삽입 단계 복원**: PNG 캡처 완료 후, Lead가 `generate_markdown_embed()` 함수로 Markdown 삽입 코드를 생성하고 Edit 도구로 대상 문서에 삽입한다.
3. **[FR-3] SKILL.md 업데이트**: `/auto` SKILL.md의 `--mockup` 섹션에 Step 3.0.2 (PNG 캡처)와 Step 3.0.3 (문서 삽입)을 명시적으로 추가한다.
4. **[FR-4] 캡처 실패 폴백**: PNG 캡처가 실패할 경우 HTML 파일 링크로 폴백한다 (기존 `document_embedder.py`의 폴백 로직 재활용).
5. **[FR-5] 기존 코드 재활용**: `lib/mockup_hybrid/export_utils.py`의 `capture_screenshot()`, `generate_markdown_embed()` 함수를 그대로 사용한다. 신규 코드 작성 최소화.

### 비기능 요구사항

1. **[NFR-1] 호환성**: Playwright Python SDK 또는 CLI 폴백 모두 지원 (기존 `export_utils.py` 로직 유지).
2. **[NFR-2] 타임아웃**: 캡처 타임아웃 30초 (기존 설정 유지).
3. **[NFR-3] 경로 규약**: 출력 경로는 `docs/mockups/{name}.html`, `docs/images/mockups/{name}.png` (기존 `get_output_paths()` 규약 유지).
4. **[NFR-4] 문서 무결성**: 문서 삽입 시 기존 내용을 손상시키지 않는다.

## 기능 범위

### 범위 내

| 항목 | 설명 |
|------|------|
| SKILL.md Step 3.0.2 추가 | PNG 캡처 단계 (Lead 직접 Bash 실행) |
| SKILL.md Step 3.0.3 추가 | 문서 삽입 단계 (Lead 직접 Edit 실행) |
| 캡처 실패 폴백 명시 | HTML 링크 폴백 절차 문서화 |

### 범위 외

| 항목 | 이유 |
|------|------|
| designer 에이전트 수정 | HTML 생성만 담당하는 현재 설계 유지 |
| export_utils.py 코드 수정 | 기존 코드 그대로 재활용 |
| document_embedder.py 코드 수정 | 기존 코드 그대로 재활용 |
| Skill() 호출 복원 | v21.0+ Agent Teams 패턴과 충돌, subagent에서 Skill 사용 불가 |

## 제약사항

1. **Skill tool 사용 불가**: subagent에서 Skill tool은 호출할 수 없다 (확인 완료).
2. **Method C 채택**: Designer가 HTML 생성 -> Lead가 직접 Bash로 캡처 -> Lead가 Edit로 문서 삽입.
3. **designer 에이전트는 Bash 도구를 보유**: 그러나 캡처/삽입 책임은 Lead에게 부여 (파이프라인 제어권 집중).
4. **Agent Teams 단일 패턴 유지**: TeamCreate/Task/SendMessage/TeamDelete 패턴을 벗어나지 않는다.

## 수정 대상 파일

| 파일 | 변경 내용 |
|------|-----------|
| `C:\claude\.claude\skills\auto\SKILL.md` | `--mockup` 섹션에 Step 3.0.2, Step 3.0.3 추가 |

## 재활용 코드

| 파일 | 함수 | 용도 |
|------|------|------|
| `C:\claude\lib\mockup_hybrid\export_utils.py` | `capture_screenshot()` | HTML -> PNG 캡처 (Playwright SDK/CLI) |
| `C:\claude\lib\mockup_hybrid\export_utils.py` | `generate_markdown_embed()` | Markdown 삽입 코드 생성 |
| `C:\claude\lib\mockup_hybrid\export_utils.py` | `get_output_paths()` | 출력 경로 생성 |
| `C:\claude\.claude\skills\mockup-hybrid\core\document_embedder.py` | `DocumentEmbedder.embed()` | 문서 삽입 (참조용, 직접 호출 대신 Lead가 Edit로 수행) |

## 우선순위

| 순위 | 항목 | 근거 |
|------|------|------|
| P0 | FR-1 PNG 캡처 단계 복원 | 핵심 누락 기능 |
| P0 | FR-3 SKILL.md 업데이트 | 워크플로우 정의가 없으면 실행 불가 |
| P1 | FR-2 문서 삽입 단계 복원 | 캡처 없이 삽입 불가 (FR-1 의존) |
| P1 | FR-4 캡처 실패 폴백 | 안정성 보장 |
| P2 | FR-5 기존 코드 재활용 확인 | 구현 시 자연스럽게 충족 |

## 구현 상태

| 항목 | 상태 | 비고 |
|------|------|------|
| PRD 작성 | 완료 | 이 문서 |
| SKILL.md Step 3.0.2 추가 | 완료 | PNG 캡처 단계 (169fba4) |
| SKILL.md Step 3.0.3 추가 | 완료 | 문서 삽입 단계 (169fba4) |
| 검증 | 완료 | Architect APPROVE (7/7 PASS) |

## Changelog

| 날짜 | 버전 | 변경 내용 | 결정 근거 |
|------|------|-----------|----------|
| 2026-03-01 | v1.1 | 구현 완료 — Step 3.0.2/3.0.3 추가, Architect APPROVE | PDCA Phase 3-4 완료 |
| 2026-03-01 | v1.0 | 최초 작성 | v21.0+ mockup 파이프라인 PNG 캡처/문서 삽입 누락 복원 |
