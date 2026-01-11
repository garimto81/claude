# 프로젝트 전체 Checklist

**Version**: 1.0.0 | **Updated**: 2026-01-11

이 문서는 프로젝트 전체의 주요 Checklist를 관리합니다.

---

## PRD별 Checklist

| PRD | 상태 | 위치 |
|-----|------|------|
| PRD-0001 | Active | `docs/checklists/PRD-0001.md` |
| PRD-0002 | Active | `docs/checklists/PRD-0002.md` |

---

## 일반 Checklist

### 코드 품질

- [ ] 린트 통과 (`ruff check src/`)
- [ ] 타입 체크 통과 (`mypy src/`)
- [ ] 테스트 통과 (`pytest tests/`)
- [ ] 커버리지 80% 이상

### 문서화

- [ ] README.md 최신화
- [ ] CLAUDE.md 버전 업데이트
- [ ] API 문서 최신화

### 보안

- [ ] 시크릿 노출 없음
- [ ] 의존성 취약점 없음 (`pip-audit`)

---

## 참조

- `.github/CHECKLIST_STANDARD.md` - Checklist 작성 표준
- `docs/checklists/` - PRD별 상세 Checklist
