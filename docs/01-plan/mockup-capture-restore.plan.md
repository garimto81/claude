# Mockup Capture Restore Work Plan

## 배경 (Background)

- 요청 내용: `/auto --mockup` 워크플로우에서 누락된 PNG 캡처 및 문서 삽입 단계 복원
- 해결하려는 문제: v21.0 Agent Teams 전환 시 `Skill(skill="mockup-hybrid")` 제거로 designer가 HTML만 생성하고 PNG 캡처 + 문서 삽입 단계가 사라짐

## 구현 범위 (Scope)

- **포함**: SKILL.md `--mockup` 섹션에 Step 3.0.2 (PNG 캡처), Step 3.0.3 (문서 삽입) 추가
- **제외**: designer 에이전트 수정, export_utils.py 수정, document_embedder.py 수정

## 영향 파일 (Affected Files)

- 수정: `C:\claude\.claude\skills\auto\SKILL.md` (Line 239-244 근처 `--mockup 화면명` 블록 하단)
- 재활용(수정 없음): `C:\claude\lib\mockup_hybrid\export_utils.py`

## 위험 요소 (Risks)

1. **Playwright 미설치 환경**: `capture_screenshot()` 반환값이 `None` → 폴백 없이 진행하면 문서에 깨진 이미지 삽입. 반드시 `None` 체크 후 HTML 링크 폴백 필요.
2. **SKILL.md 삽입 위치 오류**: `--mockup <파일>` 경로와 `--mockup "화면명"` 경로가 구분되어 있음. 신규 Step 3.0.2/3.0.3은 `화면명(파일 미지정)` 경로 아래에만 추가해야 함. 파일 지정 경로에 잘못 삽입하면 흐름 혼란.

## 태스크 목록 (Tasks)

### Task 1: SKILL.md Step 3.0.2 추가 (PNG 캡처)

- **설명**: `--mockup "화면명"` 블록의 `designer teammate → docs/mockups/{name}.html` 이후에 Step 3.0.2 삽입
- **수행 방법**: SKILL.md Line 240-244 블록 하단에 아래 내용 Edit 추가
  ```
  Step 3.0.2 PNG 캡처 (Lead 직접 실행):
  python -c "
  from pathlib import Path
  from lib.mockup_hybrid.export_utils import capture_screenshot, get_output_paths
  html_path, img_path = get_output_paths('{name}')
  result = capture_screenshot(html_path, img_path)
  print(result if result else 'CAPTURE_FAILED')
  "
  ```
- **Acceptance Criteria**: SKILL.md에 Step 3.0.2 블록이 존재하며 Python 원라이너 명령이 명시됨

### Task 2: SKILL.md Step 3.0.3 추가 (문서 삽입 + 폴백)

- **설명**: Step 3.0.2 직후에 Step 3.0.3 삽입. 캡처 성공 시 `generate_markdown_embed()` 결과를 Edit로 대상 문서에 삽입, 실패(CAPTURE_FAILED) 시 HTML 링크만 삽입
- **수행 방법**: Step 3.0.2 블록 아래에 Edit 추가
  ```
  Step 3.0.3 문서 삽입 (Lead 직접 실행):
  - 성공 시: generate_markdown_embed(img_path, html_path, alt_text="{name}") 결과를 Edit로 대상 문서 삽입
    → ![{name}](docs/images/mockups/{name}.png)
      [HTML 원본](docs/mockups/{name}.html)
  - 실패(CAPTURE_FAILED) 시 폴백:
    → [목업: {name}](docs/mockups/{name}.html) (PNG 캡처 실패 — HTML 링크로 대체)
  ```
- **Acceptance Criteria**: SKILL.md에 Step 3.0.3 폴백 분기가 명시됨; 성공/실패 두 경로 모두 문서화됨

## 커밋 전략 (Commit Strategy)

```
feat(auto): --mockup 워크플로우에 PNG 캡처 및 문서 삽입 단계 복원 (Step 3.0.2-3.0.3)
```

> Conventional Commit: `feat(auto):`
> 범위: `SKILL.md` 1개 파일 수정
