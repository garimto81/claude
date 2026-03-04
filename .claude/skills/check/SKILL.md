---
name: check
description: >
  This skill should be used when the user requests code quality checks, security audits, lint, type checks, or QA cycles.
version: 2.0.0
triggers:
  keywords:
    - "/check"
    - "코드 검사"
    - "품질 검사"
    - "QA 실행"
auto_trigger: false
---

# /check - 코드 품질 검사

## QA 사이클
1. 테스트 실행
2. 실패 시 수정
3. 통과까지 반복

## 직접 실행 (옵션)

```bash
# 린트
ruff check src/ --fix

# 테스트
pytest tests/ -v
```
